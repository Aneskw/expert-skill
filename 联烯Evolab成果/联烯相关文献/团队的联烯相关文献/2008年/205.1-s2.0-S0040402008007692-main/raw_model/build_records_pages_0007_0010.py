#!/usr/bin/env python3
"""Enrich existing experiment records from source PDF pages 7--10.

The covered pages contain detailed preparations corresponding to existing
Table 2 and Table 4 records.  They are merged into those records rather than
counted as new reactions.
"""

import copy
import json
from pathlib import Path


DOC = "doc_5faf153e5f1a022a"
BASE = Path(__file__).resolve().parents[1]
SOURCE_RECORDS = Path(__file__).with_name("records_pages_0001_0006.json")
OUT = Path(__file__).with_name("records_pages_0007_0010.json")


def ev(page):
    return [f"{DOC}:page{page}:image", f"{DOC}:page{page}:text"]


def unique(items):
    return list(dict.fromkeys(items))


def fact(value, evidence):
    return {
        "value": value,
        "evidence_ids": unique(evidence) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def q(number, unit):
    return {"number": number, "unit": unit}


def field(name, value, evidence, targets=None):
    item = {"name": name, "fact": fact(value, evidence)}
    if targets:
        item["target_entity_ids"] = list(targets)
    return item


def find_record(records, record_id):
    return copy.deepcopy(next(r for r in records if r["record_id"] == record_id))


def participant(record, entity_id):
    return next(p for p in record["participants"] if p["entity_id"] == entity_id)


def condition(record, name):
    return next(c for s in record["steps"] for c in s["conditions"] if c["name"] == name)


def outcome(record, name):
    return next(o for o in record["outcomes"] if o["name"] == name)


def add_record_evidence(record, evidence):
    record["evidence_ids"] = unique(record["evidence_ids"] + list(evidence))


def add_amount(record, entity_id, name, value, evidence):
    participant(record, entity_id)["amounts"].append(field(name, value, evidence))


def add_mass_amount(record, entity_id, mass_mg, amount_mmol, evidence):
    add_amount(record, entity_id, "mass", q(mass_mg, "mg"), evidence)
    add_amount(record, entity_id, "amount", q(amount_mmol, "mmol"), evidence)


def extend_fact_evidence(item, evidence):
    item["fact"]["evidence_ids"] = unique(item["fact"]["evidence_ids"] + list(evidence))


records = json.loads(SOURCE_RECORDS.read_text())
updated = []


# Page 7 starts with characterization continuing from Table 2 entry 10.  No
# reaction quantities are added, but the continuation is linked to the record.
r = find_record(records, f"{DOC}:table2_entry10")
add_record_evidence(r, ev(7))
r["notes"].append(fact(
    "The analytical characterization of E-5ja continues at the top of page 7; this is not a separate reaction.",
    ev(7),
))
updated.append(r)


KINETIC = {
    11: {
        "substrate": (170.3, 0.30), "alcohol": (11.9, 0.21),
        "pd": (7.5, 0.0107, 3.6), "cui": (2.1, 0.0111, 3.7),
        "et2nh": (15.2, 0.21), "mecn": 0.6,
        "masses": (90.6, 37.6, 3.8),
    },
    12: {
        "substrate": (119.5, 0.25), "alcohol": (14.9, 0.177),
        "pd": (6.0, 0.00856, 3.4), "cui": (1.7, 0.00895, 3.6),
        "et2nh": (12.8, 0.175), "mecn": 0.5,
        "masses": (42.0, 36.2, 8.0),
    },
    13: {
        "substrate": (120.9, 0.25), "alcohol": (14.8, 0.176),
        "pd": (6.1, 0.00870, 3.5), "cui": (1.7, 0.00895, 3.6),
        "et2nh": (12.8, 0.175), "mecn": 0.5,
        "masses": (36.0, 32.1, 4.2),
    },
}

for entry, details in KINETIC.items():
    evidence = ev(7)
    r = find_record(records, f"{DOC}:table2_entry{entry}")
    add_record_evidence(r, evidence)
    substrate_id = r["participants"][0]["entity_id"]
    alcohol_id = r["participants"][1]["entity_id"]
    add_mass_amount(r, substrate_id, *details["substrate"], evidence)
    add_mass_amount(r, alcohol_id, *details["alcohol"], evidence)
    add_mass_amount(r, "pd_complex", details["pd"][0], details["pd"][1], evidence)
    add_amount(r, "pd_complex", "procedure_catalyst_loading", q(details["pd"][2], "mol%"), evidence)
    add_mass_amount(r, "cui", details["cui"][0], details["cui"][1], evidence)
    add_amount(r, "cui", "procedure_catalyst_loading", q(details["cui"][2], "mol%"), evidence)
    add_mass_amount(r, "et2nh", *details["et2nh"], evidence)
    add_amount(r, "mecn", "volume", q(details["mecn"], "mL"), evidence)
    extend_fact_evidence(condition(r, "reaction_time"), evidence)
    for name in (
        "recovered_starting_material_yield",
        "isolated_yield_E_product",
        "isolated_yield_Z_product",
    ):
        extend_fact_evidence(outcome(r, name), evidence)
    recovered_id = r["participants"][6]["entity_id"]
    e_product_id = r["participants"][7]["entity_id"]
    z_product_id = r["participants"][8]["entity_id"]
    recovered_mass, e_mass, z_mass = details["masses"]
    r["outcomes"].extend([
        field("isolated_Z3_mass", q(recovered_mass, "mg"), evidence, [recovered_id]),
        field("E_product_mass", q(e_mass, "mg"), evidence, [e_product_id]),
        field("Z_product_mass", q(z_mass, "mg"), evidence, [z_product_id]),
    ])
    r["review"]["unresolved"] = [
        "All candidate structures and alkene stereochemistry remain unverified.",
        "Atmosphere, workup, and purification are not restated for this abbreviated preparation.",
    ]
    updated.append(r)


# Exact section 3.3 preparations corresponding to Table 4 entries.  The tuple
# layout is: source pages, substrate mass/mmol, alcohol mass/mmol,
# Pd mass/mmol/mol%, CuI mass/mmol/mol%, Et2NH volume, time, Z/E product masses.
COMPLETE = {
    1: ([7], (144.1, 0.30), (21.0, 0.375), (6.5, 0.00927, 3.1), (1.7, 0.00895, 3.0), 1.2, 7.0, (25.0, 53.7)),
    2: ([7], (175.1, 0.30), (20.5, 0.37), (6.2, 0.00884, 2.9), (2.0, 0.0105, 3.5), 1.2, 9.5, (61.7, 32.3)),
    3: ([7, 8], (175.1, 0.40), (27.2, 0.49), (8.7, 0.0124, 3.1), (2.2, 0.0116, 2.9), 1.6, 9.0, (83.9, 35.6)),
    4: ([8], (137.3, 0.30), (20.5, 0.37), (6.4, 0.00913, 3.0), (1.8, 0.00941, 3.2), 1.2, 7.0, (67.0, 28.0)),
    5: ([8], (141.5, 0.25), (16.9, 0.30), (5.3, 0.00756, 3.0), (1.4, 0.00737, 2.9), 0.5, 9.5, (67.9, 29.5)),
    6: ([8], (121.9, 0.25), (16.9, 0.30), (5.3, 0.00756, 3.0), (1.4, 0.00737, 2.9), 0.5, 7.5, (55.1, 21.9)),
    7: ([8], (177.0, 0.30), (20.7, 0.37), (6.1, 0.00870, 2.9), (1.8, 0.00947, 3.2), 1.2, 11.0, (78.4, 52.8)),
    8: ([8], (149.9, 0.30), (19.9, 0.36), (6.3, 0.00899, 3.0), (1.6, 0.00842, 2.8), 1.2, 7.5, (69.4, 30.3)),
    9: ([8], (232.3, 0.50), (34.5, 0.62), (10.8, 0.0154, 3.1), (3.0, 0.0158, 3.2), 2.0, 6.0, (133.4, 49.7)),
    10: ([8, 9], (224.6, 0.40), (27.6, 0.49), (8.6, 0.0123, 3.1), (2.4, 0.0126, 3.2), 1.6, 11.5, (117.3, 50.9)),
    11: ([9], (189.2, 0.40), (40.3, 0.48), (8.4, 0.0120, 3.0), (2.3, 0.0121, 3.0), 1.6, 8.0, (90.6, 45.6)),
    12: ([9], (194.2, 0.40), (40.7, 0.48), (8.6, 0.0123, 3.1), (2.1, 0.0111, 2.8), 1.6, 7.0, (103.2, 41.6)),
    13: ([9], (198.5, 0.40), (41.9, 0.50), (8.4, 0.0120, 3.0), (2.3, 0.0121, 3.0), 1.6, 12.0, (104.7, 33.6)),
    14: ([9], (140.8, 0.30), (30.0, 0.36), (6.3, 0.00899, 3.0), (1.6, 0.00842, 2.8), 0.6, 10.5, (75.1, 35.4)),
}

for entry, details in COMPLETE.items():
    pages, substrate_data, alcohol_data, pd_data, cui_data, solvent_ml, hours, masses = details
    evidence = unique(sum((ev(page) for page in pages), []))
    r = find_record(records, f"{DOC}:table4_entry{entry}")
    add_record_evidence(r, evidence)
    alcohol_id = "4a" if entry <= 10 else "4b"
    add_mass_amount(r, "input_3", *substrate_data, evidence)
    add_mass_amount(r, alcohol_id, *alcohol_data, evidence)
    add_mass_amount(r, "pd_complex", pd_data[0], pd_data[1], evidence)
    add_amount(r, "pd_complex", "procedure_catalyst_loading", q(pd_data[2], "mol%"), evidence)
    add_mass_amount(r, "cui", cui_data[0], cui_data[1], evidence)
    add_amount(r, "cui", "procedure_catalyst_loading", q(cui_data[2], "mol%"), evidence)
    add_amount(r, "et2nh", "volume", q(solvent_ml, "mL"), evidence)
    reaction_time = condition(r, "reaction_time")
    reaction_time["fact"] = fact(q(hours, "h"), evidence)
    z_mass, e_mass = masses
    r["outcomes"].extend([
        field("Z_product_mass", q(z_mass, "mg"), evidence, ["Z_product"]),
        field("E_product_mass", q(e_mass, "mg"), evidence, ["E_product"]),
    ])
    if entry == 1:
        condition(r, "atmosphere")["fact"] = fact("nitrogen", evidence)
        condition(r, "workup")["fact"] = fact(
            "quenched with brine; diluted with diethyl ether; washed with brine (10 mL × 3); dried over anhydrous Na2SO4",
            evidence,
        )
        condition(r, "purification")["fact"] = fact(
            "evaporation and silica-gel column chromatography (petroleum ether/ethyl acetate = 10:1)",
            evidence,
        )
        r["steps"][0]["conditions"].append(field(
            "degassing_operation", "freeze–pump–thaw cycles", evidence
        ))
        r["steps"][0]["conditions"].append(field(
            "reaction_monitoring", "TLC", evidence
        ))
        r["outcomes"].extend([
            field("procedure_isolated_yield_Z_product", q(20, "%"), evidence, ["Z_product"]),
            field("procedure_isolated_yield_E_product", q(44, "%"), evidence, ["E_product"]),
        ])
        conflict_evidence = unique(ev(3) + evidence)
        r["notes"].append(fact(
            "Table 4 entry 1 assigns 44% to Z-5aa and 20% to E-5aa, whereas section 3.3.1 assigns 44% to E-5aa and 20% to Z-5aa.",
            conflict_evidence,
        ))
        r["review"]["unresolved"] = [
            "Candidate product structure and stereochemistry remain unverified.",
            "Table 4 entry 1 and section 3.3.1 conflict on which 5aa isomer has the 44% versus 20% isolated yield; both source statements are retained.",
        ]
    else:
        extend_fact_evidence(outcome(r, "isolated_yield_Z_product"), evidence)
        extend_fact_evidence(outcome(r, "isolated_yield_E_product"), evidence)
        r["review"]["unresolved"] = [
            "Atmosphere, workup, and purification are not restated in this abbreviated preparation.",
            "Candidate product structure and stereochemistry remain unverified.",
        ]
    updated.append(r)


assert len(updated) == 18, len(updated)
assert len({r["record_id"] for r in updated}) == len(updated)
OUT.write_text(json.dumps(updated, ensure_ascii=False, indent=2) + "\n")
print(f"wrote {len(updated)} updated records to {OUT}")
