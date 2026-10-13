#!/usr/bin/env python3
"""Enrich existing Kong et al. records with PDF pages 7--9 evidence."""

import copy
import json
from pathlib import Path


DOC = "doc_bf2d3fefda9ca663"
ROOT = Path(__file__).resolve().parents[3]
DATASET = ROOT / "runs/current/dataset.json"
RAW = ROOT / "runs/current/raw_model/records_pages_0007_0009.json"
COVERAGE = ROOT / "runs/current/coverage/pages_0007_0009.json"
TASKS = ROOT / "runs/current/tasks.json"


def ev(page):
    return [f"{DOC}:page{page}:text", f"{DOC}:page{page}:image"]


def fact(value, evidence=None):
    return {
        "value": value,
        "evidence_ids": list(evidence or []) if value is not None else [],
        "verification": "missing" if value is None else "unreviewed",
    }


def field(name, value, evidence=None, targets=None):
    item = {"name": name, "fact": fact(value, evidence)}
    if targets:
        item["target_entity_ids"] = targets
    return item


def q(number, unit):
    return {"number": number, "unit": unit}


def extend_unique(items, additions):
    for value in additions:
        if value not in items:
            items.append(value)


def add_fact_evidence(item, evidence):
    value = item.get("value")
    if value is not None:
        extend_unique(item["evidence_ids"], evidence)


def participant(record, entity_id):
    return next(p for p in record["participants"] if p["entity_id"] == entity_id)


def condition(record, name):
    return next(c for s in record["steps"] for c in s["conditions"] if c["name"] == name)


def outcome(record, name):
    return next(o for o in record["outcomes"] if o["name"] == name)


dataset = json.loads(DATASET.read_text())
by_id = {r["record_id"]: r for r in dataset["experiments"]}
records = []
e7 = ev(7)
e9 = ev(9)


# Page 7 starts with analytical characterization continuing from the page-6 6h
# preparation. It is part of the same experiment and supplies no new reaction.
rid = f"{DOC}:table2_entry5"
r = copy.deepcopy(by_id[rid])
extend_unique(r["evidence_ids"], e7)
r["notes"].append(fact(
    "Page 7 continues elemental-analysis characterization of 6h from the detailed page-6 preparation; it does not describe a separate reaction.",
    e7,
))
records.append(r)


# Detailed experimental paragraphs for Table 2 entries 6 and 7.
table2_details = {
    6: {
        "substrate": "substrate_5i", "product": "product_6i",
        "substrate_mass": 88.0, "substrate_amount": 0.30,
        "catalyst_mass": 4.9, "catalyst_amount": 0.018,
        "solvent_volume": 1.5, "time": 4,
        "product_mass": 50.7, "yield": 61,
        "purification": "silica-gel column chromatography; petroleum ether/ethyl acetate 40:1",
    },
    7: {
        "substrate": "substrate_5j", "product": "product_6j",
        "substrate_mass": 91.2, "substrate_amount": 0.30,
        "catalyst_mass": 4.1, "catalyst_amount": 0.015,
        "solvent_volume": 1.5, "time": 13,
        "product_mass": 71.3, "yield": 83,
        "purification": "silica-gel column chromatography; petroleum ether/ethyl acetate 100:1",
    },
}

for entry, detail in table2_details.items():
    rid = f"{DOC}:table2_entry{entry}"
    r = copy.deepcopy(by_id[rid])
    extend_unique(r["evidence_ids"], e7)

    sub = participant(r, detail["substrate"])
    sub["amounts"].extend([
        field("experimental_section_mass", q(detail["substrate_mass"], "mg"), e7),
        field("experimental_section_amount", q(detail["substrate_amount"], "mmol"), e7),
    ])
    add_fact_evidence(sub["label"], e7)
    add_fact_evidence(sub["name"], e7)

    cat = participant(r, "catalyst_ptcl2")
    cat["amounts"].extend([
        field("mass", q(detail["catalyst_mass"], "mg"), e7),
        field("amount", q(detail["catalyst_amount"], "mmol"), e7),
    ])
    for key in ("label", "name", "smiles"):
        add_fact_evidence(cat[key], e7)

    solv = participant(r, "solvent_toluene")
    solv["amounts"].append(field(
        "experimental_section_volume", q(detail["solvent_volume"], "mL"), e7
    ))
    for key in ("label", "name", "smiles"):
        add_fact_evidence(solv[key], e7)

    prod = participant(r, detail["product"])
    prod["amounts"].append(field("isolated_mass", q(detail["product_mass"], "mg"), e7))
    add_fact_evidence(prod["label"], e7)
    add_fact_evidence(prod["name"], e7)

    add_fact_evidence(condition(r, "temperature")["fact"], e7)
    add_fact_evidence(condition(r, "reaction_time")["fact"], e7)
    r["steps"][0]["conditions"].append(field("purification", detail["purification"], e7))

    add_fact_evidence(outcome(r, "isolated_yield")["fact"], e7)
    r["outcomes"].append(field(
        "isolated_product_mass", q(detail["product_mass"], "mg"), e7, [detail["product"]]
    ))
    r["notes"].append(fact(
        "The detailed page-7 preparation and the matching Table 2 row were treated as one reported transformation, not duplicate experiments.",
        e7,
    ))
    r["review"]["unresolved"] = [
        "Table 2 states 0.4 mmol substrate and 2 mL toluene, whereas the detailed preparation uses 0.30 mmol and 1.5 mL; both source statements are retained without reconciliation.",
        "The workup is not stated in the detailed paragraph; complex structures remain machine-unverified.",
        "No supporting-information file was supplied or explicitly associated.",
    ]
    records.append(r)


# Detailed experimental paragraphs for the five Scheme 4 rows.
scheme4_details = {
    "k": {
        "product_name": "9-ethyl-1,4-dimethyl-3-phenyl-9H-carbazole",
        "substrate_mass": 96.2, "substrate_amount": 0.30,
        "catalyst_mass": 4.2, "catalyst_amount": 0.016,
        "solvent_volume": 1.5, "time": 24,
        "product_mass": 75.6, "yield": 83,
        "purification": "silica-gel column chromatography; petroleum ether/ethyl acetate 40:1",
    },
    "l": {
        "product_name": "9-ethyl-2,3,4-trimethyl-9H-carbazole",
        "substrate_mass": 78.5, "substrate_amount": 0.30,
        "catalyst_mass": 4.1, "catalyst_amount": 0.015,
        "solvent_volume": 1.5, "time": 12,
        "product_mass": 40.3, "yield": 55,
        "purification": "double silica-gel chromatography; first petroleum ether/ethyl acetate 10:1, then 200:1",
    },
    "m": {
        "product_name": "9-ethyl-4,6-dimethyl-3-(p-tolyl)-9H-carbazole",
        "substrate_mass": 99.4, "substrate_amount": 0.30,
        "catalyst_mass": 3.9, "catalyst_amount": 0.015,
        "solvent_volume": 1.5, "time": 16,
        "product_mass": 77.8, "yield": 83,
        "purification": "silica-gel column chromatography; petroleum ether/ethyl acetate 100:1",
    },
    "n": {
        "product_name": "9-ethyl-6-methoxy-3,4-dimethyl-9H-carbazole",
        "substrate_mass": 82.0, "substrate_amount": 0.30,
        "catalyst_mass": 4.1, "catalyst_amount": 0.015,
        "solvent_volume": 2.0, "time": 12,
        "product_mass": 53.6, "yield": 70,
        "purification": "silica-gel column chromatography; petroleum ether/ethyl acetate 40:1",
    },
    "o": {
        "product_name": "9-ethyl-1,5,6-trimethyl-9H-carbazole",
        "substrate_mass": 101.1, "substrate_amount": 0.40,
        "catalyst_mass": 5.4, "catalyst_amount": 0.020,
        "solvent_volume": 2.0, "time": 16,
        "product_mass": 68.1, "yield": 72,
        "purification": "double silica-gel chromatography; first petroleum ether/ethyl acetate 50:1, then 100:1",
    },
}

for suffix, detail in scheme4_details.items():
    rid = f"{DOC}:scheme4_5{suffix}_to_6{suffix}"
    r = copy.deepcopy(by_id[rid])
    extend_unique(r["evidence_ids"], e7)

    sub_id = f"substrate_5{suffix}"
    prod_id = f"product_6{suffix}"
    sub = participant(r, sub_id)
    add_fact_evidence(sub["label"], e7)
    sub["amounts"].extend([
        field("mass", q(detail["substrate_mass"], "mg"), e7),
        field("amount", q(detail["substrate_amount"], "mmol"), e7),
    ])

    cat = participant(r, "catalyst_ptcl2")
    for key in ("label", "name", "smiles"):
        add_fact_evidence(cat[key], e7)
    cat["amounts"].extend([
        field("mass", q(detail["catalyst_mass"], "mg"), e7),
        field("amount", q(detail["catalyst_amount"], "mmol"), e7),
    ])

    solv = participant(r, "solvent_toluene")
    for key in ("label", "name", "smiles"):
        add_fact_evidence(solv[key], e7)
    solv["amounts"].append(field("volume", q(detail["solvent_volume"], "mL"), e7))

    prod = participant(r, prod_id)
    add_fact_evidence(prod["label"], e7)
    prod["name"] = fact(detail["product_name"], e7)
    prod["amounts"].append(field("isolated_mass", q(detail["product_mass"], "mg"), e7))

    add_fact_evidence(condition(r, "temperature")["fact"], e7)
    time_field = condition(r, "reaction_time")
    time_field["fact"] = fact(q(detail["time"], "h"), e7)
    r["steps"][0]["conditions"].append(field("purification", detail["purification"], e7))

    yld = outcome(r, "reported_yield")
    add_fact_evidence(yld["fact"], e7)
    basis = outcome(r, "yield_measurement_basis")
    basis["fact"] = fact("isolated yield", e7)
    r["outcomes"].append(field(
        "isolated_product_mass", q(detail["product_mass"], "mg"), e7, [prod_id]
    ))
    r["notes"].append(fact(
        "The detailed page-7 preparation and the matching Scheme 4 arrow were treated as one reported transformation, not duplicate experiments.",
        e7,
    ))
    if suffix == "m":
        extend_unique(r["evidence_ids"], e9)
        r["notes"].append(fact(
            "Reference [17] on page 9 reports crystallographic data and CCDC 737002 for 6m; this is product characterization, not another reaction experiment.",
            e9,
        ))
    r["review"]["unresolved"] = [
        "Atmosphere and workup are not restated in the detailed paragraph and were not inferred from a representative procedure.",
        "The source identifies the substrate/product by label and name, but their complex structures remain machine-unverified.",
        "No supporting-information file was supplied or explicitly associated.",
    ]
    records.append(r)


assert len(records) == 8, len(records)

page7_ids = [
    f"{DOC}:table2_entry5", f"{DOC}:table2_entry6", f"{DOC}:table2_entry7",
    *[f"{DOC}:scheme4_5{x}_to_6{x}" for x in "klmno"],
]

coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 7,
            "state": "attempted",
            "regions": [
                {
                    "region": "page 7 upper-left, continuation of 6h analytical characterization",
                    "finding": "The page completes MS/elemental-analysis characterization for the 6h preparation begun on page 6. It contains no new reaction conditions or outcome and was linked to the existing Table 2 entry 5 record.",
                    "evidence_ids": e7,
                },
                {
                    "region": "page 7 left column, detailed preparations of 6i and 6j",
                    "finding": "Two detailed PtCl2/toluene room-temperature cyclizations were reconciled with existing Table 2 entries 6 and 7, adding exact charges, solvent volumes, chromatography, product masses, and confirming the 61% and 83% isolated yields.",
                    "evidence_ids": e7,
                },
                {
                    "region": "page 7 lower-left through right column, detailed preparations of 6k–6o",
                    "finding": "Five detailed PtCl2-catalyzed cyclizations were reconciled with the five existing Scheme 4 records, adding exact substrate/catalyst quantities, solvent volumes, times, purification, product names/masses, and isolated-yield bases.",
                    "evidence_ids": e7,
                },
            ],
            "record_ids": page7_ids,
            "unresolved": [
                "The detailed 6i/6j scales (0.30 mmol, 1.5 mL) differ from the shared Table 2 footnote (0.4 mmol, 2 mL); both source statements remain in the records.",
                "Atmosphere and workup are not restated for the abbreviated 6k–6o paragraphs; complex structures remain machine-unverified.",
            ],
        },
        {
            "page": 8,
            "state": "attempted",
            "regions": [
                {
                    "region": "page 8 upper-left, Supporting Information and Acknowledgements",
                    "finding": "The page states that preparations and spectra are available in Supporting Information, but no SI file is supplied or explicitly associated in this workspace. The acknowledgement that a result was reproduced is not a separately specified experiment and was not converted into a record.",
                    "evidence_ids": ev(8),
                },
                {
                    "region": "page 8 remaining two columns, references [1]–[8]",
                    "finding": "Bibliographic citations and review references are prior literature, not experiments newly reported in this paper; no reaction records were created from them.",
                    "evidence_ids": ev(8),
                },
            ],
            "record_ids": [],
            "unresolved": [
                "The acknowledgement refers to 'entry 3 of Scheme 3', but the page does not restate a uniquely identifiable experiment; no experimental facts were inferred from it.",
                "Supporting Information association remains unestablished.",
            ],
        },
        {
            "page": 9,
            "state": "attempted",
            "regions": [
                {
                    "region": "page 9 references [9]–[16] and [18]–[20]",
                    "finding": "The cited articles are prior literature and were not expanded into current-paper experiment records.",
                    "evidence_ids": ev(9),
                },
                {
                    "region": "page 9 right column, reference [17] crystal data for 6m",
                    "finding": "The paragraph supplies crystallographic characterization and CCDC 737002 for product 6m. It supports the existing 5m-to-6m record but is not an additional reaction experiment.",
                    "evidence_ids": ev(9),
                },
            ],
            "record_ids": [f"{DOC}:scheme4_5m_to_6m"],
            "unresolved": [
                "The external CCDC deposit was not supplied as source evidence and was not imported.",
            ],
        },
    ],
}


RAW.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
COVERAGE.parent.mkdir(parents=True, exist_ok=True)
COVERAGE.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

tasks = json.loads(TASKS.read_text())
for item in tasks:
    if item.get("document_id") == DOC and item.get("task_id", "").endswith(":text"):
        page = int(item["task_id"].split(":page", 1)[1].split(":", 1)[0])
        if 7 <= page <= 9:
            item["state"] = "attempted"
            item["reason"] = "Original page image and extracted text inspected; coverage ledger records detailed reaction reconciliation, non-experimental content, and unresolved issues."
TASKS.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"records": len(records), "raw": str(RAW), "coverage": str(COVERAGE)}, ensure_ascii=False))
