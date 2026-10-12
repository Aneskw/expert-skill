#!/usr/bin/env python3
"""Enrich the six existing page-3/4 records with source details from PDF page 7.

Page 8 contains references only, so it contributes coverage but no experiment record.
The script deliberately preserves the printed 2b/2k substrate-label conflicts for 4j/4k.
"""
import copy
import json
from pathlib import Path


DOC = "doc_28bbeb684eb62f95"
BASE = Path(__file__).resolve().parents[1]
DATASET = BASE / "dataset.json"
OUT = Path(__file__).with_name("pages_0007_0008_records.json")
E7 = [f"{DOC}:page7:text", f"{DOC}:page7:image"]


def fact(value, evidence=E7):
    return {
        "value": value,
        "evidence_ids": list(evidence) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def field(name, value, evidence=E7, targets=None):
    item = {"name": name, "fact": fact(value, evidence)}
    if targets:
        item["target_entity_ids"] = list(targets)
    return item


def amount(name, number, unit):
    return field(name, {"number": number, "unit": unit})


def add_evidence(fact_obj, evidence=E7):
    if fact_obj["value"] is not None:
        fact_obj["evidence_ids"] = list(dict.fromkeys(fact_obj["evidence_ids"] + list(evidence)))


def participant(entity_id, role, label, name=None, smiles=None, amounts=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label),
        "name": fact(name),
        "smiles": fact(smiles),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": amounts or [],
    }


def by_entity(record, entity_id):
    return next(p for p in record["participants"] if p["entity_id"] == entity_id)


def by_field(fields, name):
    return next(f for f in fields if f["name"] == name)


def append_page7_evidence(record):
    record["evidence_ids"] = list(dict.fromkeys(record["evidence_ids"] + E7))


def strip_generated_workup(record):
    """Make reruns safe after these same records have already been merged."""
    generated_entities = {"workup_ether", "sodium_thiosulfate", "drying_agent"}
    generated_steps = {"quench_and_extraction", "drying_and_purification"}
    record["participants"] = [
        p for p in record["participants"] if p["entity_id"] not in generated_entities
    ]
    record["steps"] = [
        s for s in record["steps"] if s["step_id"] not in generated_steps
    ]


def add_shared_workup(record):
    record["participants"].extend([
        participant(
            "workup_ether", "solvent", "Et2O", "diethyl ether", "CCOCC",
            [amount("volume", 10, "mL")],
        ),
        participant(
            "sodium_thiosulfate", "reagent", "Na2S2O3 solution",
            "sodium thiosulfate solution",
        ),
        participant(
            "drying_agent", "reagent", "Na2SO4", "anhydrous sodium sulfate",
        ),
    ])
    record["steps"].extend([
        {
            "step_id": "quench_and_extraction",
            "participant_ids": ["workup_ether", "sodium_thiosulfate"],
            "conditions": [
                field("operation", "Et2O was added; aqueous Na2S2O3 was then added to remove excess I2, followed by Et2O extraction."),
            ],
        },
        {
            "step_id": "drying_and_purification",
            "participant_ids": ["drying_agent"],
            "conditions": [
                field("operation", "The organic extract was dried over Na2SO4 and evaporated."),
                field("purification", "flash chromatography on silica gel"),
            ],
        },
    ])


data = json.loads(DATASET.read_text())
index = {r["record_id"]: r for r in data["experiments"]}
records = []


# Page 7 sections 3.4.1--3.4.4 are detailed realizations of Table 3, not new rows.
iodo_details = {
    "5k": {
        "substrate_mass": 106, "substrate_mmol": 0.53,
        "iodine_mass": 268, "iodine_mmol": 1.06, "thf_volume": 4,
        "product_mass": 129,
        "name": "Z-2-Benzylimino-4-iodo-5,5-dimethyl-2,5-dihydrofuran",
        "ratio_page7": True,
    },
    "5l": {
        "substrate_mass": 47, "substrate_mmol": 0.18,
        "iodine_mass": 91, "iodine_mmol": 0.36, "thf_volume": 5,
        "product_mass": 59,
        "name": "Z-2-Benzylimino-4-iodo-5-methyl-5-phenyl-2,5-dihydrofuran",
        "ratio_page7": True,
    },
    "5m": {
        "substrate_mass": 78, "substrate_mmol": 0.27,
        "iodine_mass": 136, "iodine_mmol": 0.54, "thf_volume": 5,
        "product_mass": 103,
        "name": "Z-2-Benzylimino-3-benzyl-4-iodo-5,5-dimethyl-2,5-dihydrofuran",
        "ratio_page7": False,
    },
    "5n": {
        "substrate_mass": 21, "substrate_mmol": 0.10,
        "iodine_mass": 50, "iodine_mmol": 0.20, "thf_volume": 3,
        "product_mass": 33,
        "name": "Z-2-Benzylimino-3-methyl-4-iodo-5,5-dimethyl-2,5-dihydrofuran",
        "ratio_page7": False,
    },
}

for product_label, detail in iodo_details.items():
    rid = f"{DOC}:table3_{product_label}"
    record = copy.deepcopy(index[rid])
    strip_generated_workup(record)
    append_page7_evidence(record)
    record["source_reaction_id"] = f"Table 3 / section 3.4 {product_label}"

    substrate = by_entity(record, "substrate")
    add_evidence(substrate["label"])
    substrate["amounts"] = [
        amount("mass", detail["substrate_mass"], "mg"),
        amount("amount", detail["substrate_mmol"], "mmol"),
    ]

    iodine = by_entity(record, "halogen_reagent")
    for key in ("label", "name"):
        add_evidence(iodine[key])
    iodine["amounts"] = [f for f in iodine["amounts"] if f["name"] == "equivalents"]
    add_evidence(iodine["amounts"][0]["fact"])
    iodine["amounts"].extend([
        amount("mass", detail["iodine_mass"], "mg"),
        amount("amount", detail["iodine_mmol"], "mmol"),
    ])

    thf = by_entity(record, "solvent_1")
    for key in ("label", "name"):
        add_evidence(thf[key])
    thf["amounts"] = [amount("volume", detail["thf_volume"], "mL")]

    product = by_entity(record, "product")
    add_evidence(product["label"])
    product["name"] = fact(detail["name"])
    product["amounts"] = [amount("mass", detail["product_mass"], "mg")]

    reaction = record["steps"][0]
    for condition in reaction["conditions"]:
        add_evidence(condition["fact"])
    for outcome in record["outcomes"]:
        if outcome["name"] in ("isolated_yield", "yield_measurement_basis"):
            add_evidence(outcome["fact"])
        elif detail["ratio_page7"] and outcome["name"] == "Z_to_E_ratio":
            add_evidence(outcome["fact"])

    add_shared_workup(record)
    record["notes"] = [
        fact("Section 3.4 is the detailed realization of the corresponding Table 3 row; it is merged rather than counted as a new experiment."),
    ]
    record["review"]["unresolved"] = [
        "The authors describe C=N configurations other than the separately established 5e assignment as tentative; stereochemistry is not encoded in the candidate SMILES.",
        "The concentration and volume of aqueous Na2S2O3 and the number/volume of Et2O extractions are not reported.",
        "No supporting information was explicitly provided or associated.",
        "Candidate structures remain unverified against an independently interpreted structure drawing.",
    ]
    record["completeness"] = "partial"
    records.append(record)


# Page 7 sections 3.5.1--3.5.2 are detailed realizations of the two Scheme 8 rows.
lactam_details = {
    "4j": {
        "substrate_label": "2b",
        "substrate_mass": 63, "substrate_mmol": 0.23,
        "iodine_mass": 118, "iodine_mmol": 0.46,
        "product_mass": 85,
        "name": "1-Benzyl-5-hydroxy-5-heptyl-4-iodopyrrol-2(5H)-one",
        "reported_time": 24,
        "label_issue": "Section 3.5.1 prints substrate label 2b, but the named N-benzyl product and the earlier Scheme 8 drawing are inconsistent with that label; the substrate SMILES is therefore left null rather than silently corrected.",
    },
    "4k": {
        "substrate_label": "2k",
        "substrate_mass": 70, "substrate_mmol": 0.37,
        "iodine_mass": 191, "iodine_mmol": 0.75,
        "product_mass": 71,
        "name": "1-Benzyl-5-hydroxy-4-iodo-3-methylpyrrol-2(5H)-one",
        "reported_time": 42,
        "label_issue": "Section 3.5.2 prints substrate label 2k, whereas the earlier Scheme 8 record uses a different substrate label; the substrate SMILES is therefore left null rather than silently reconciling the conflict.",
    },
}

for product_label, detail in lactam_details.items():
    rid = f"{DOC}:scheme8_{product_label}"
    record = copy.deepcopy(index[rid])
    strip_generated_workup(record)
    append_page7_evidence(record)
    record["source_reaction_id"] = f"Scheme 8 / section 3.5 {product_label}"

    substrate = by_entity(record, "substrate")
    substrate["label"] = fact(detail["substrate_label"])
    substrate["name"] = fact(None)
    substrate["smiles"] = fact(None)
    substrate["smiles_parseable"] = None
    substrate["structure_verified"] = False
    substrate["amounts"] = [
        amount("mass", detail["substrate_mass"], "mg"),
        amount("amount", detail["substrate_mmol"], "mmol"),
    ]

    iodine = by_entity(record, "iodine")
    for key in ("label", "name"):
        add_evidence(iodine[key])
    iodine["amounts"] = [f for f in iodine["amounts"] if f["name"] == "equivalents"]
    add_evidence(iodine["amounts"][0]["fact"])
    iodine["amounts"].extend([
        amount("mass", detail["iodine_mass"], "mg"),
        amount("amount", detail["iodine_mmol"], "mmol"),
    ])

    thf = by_entity(record, "THF")
    for key in ("label", "name"):
        add_evidence(thf[key])
    thf["amounts"] = [amount("volume", 5, "mL")]

    oxygen = by_entity(record, "oxygen")
    for key in ("label", "name"):
        add_evidence(oxygen[key])

    product = by_entity(record, "product")
    add_evidence(product["label"])
    product["name"] = fact(detail["name"])
    product["amounts"] = [amount("mass", detail["product_mass"], "mg")]

    iodination = next(s for s in record["steps"] if s["step_id"] == "iodination")
    for condition in iodination["conditions"]:
        add_evidence(condition["fact"])
    oxidation = next(s for s in record["steps"] if s["step_id"] == "oxygen_oxidation")
    by_field(oxidation["conditions"], "total_reported_time")["fact"] = fact(
        {"number": detail["reported_time"], "unit": "h"}
    )
    add_evidence(by_field(oxidation["conditions"], "temperature")["fact"])
    oxidation["conditions"] = [f for f in oxidation["conditions"] if f["name"] != "pressure"]
    oxidation["conditions"].append(field("pressure", "1 atm"))

    for outcome in record["outcomes"]:
        add_evidence(outcome["fact"])

    add_shared_workup(record)
    record["notes"] = [
        fact("Section 3.5 is the detailed realization of the corresponding Scheme 8 row; it is merged rather than counted as a new experiment."),
    ]
    record["review"]["unresolved"] = [
        detail["label_issue"],
        f"It is unclear whether the specific {detail['reported_time']} h report includes the initial 1 h before O2 charging; the times are preserved in separate fields and are not added.",
        "The concentration and volume of aqueous Na2S2O3 and the number/volume of Et2O extractions are not reported.",
        "No supporting information was explicitly provided or associated.",
        "Product candidate structures remain unverified; conflicting substrate structures are left null.",
    ]
    record["completeness"] = "partial"
    records.append(record)


assert len(records) == 6
assert len({r["record_id"] for r in records}) == 6
OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
print(f"wrote {len(records)} enriched records to {OUT}")
