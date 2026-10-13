#!/usr/bin/env python3
"""Build page-7 evidence updates for the two existing Table 2 scope records."""

import json
from pathlib import Path


DOC = "doc_e90694bb0bb41003"
BASE = Path(__file__).resolve().parents[1]
DATASET = BASE / "dataset.json"
OUT = Path(__file__).with_name("pages_0007_0007_records.json")
PAGE3 = f"{DOC}:page3:image"
PAGE7 = f"{DOC}:page7:image"


def add_evidence(fact, evidence_id):
    if fact["value"] is not None and evidence_id not in fact["evidence_ids"]:
        fact["evidence_ids"].append(evidence_id)


def quantity(name, number, unit):
    return {
        "name": name,
        "fact": {
            "value": {"number": number, "unit": unit},
            "evidence_ids": [PAGE7],
            "verification": "unreviewed",
        },
    }


with DATASET.open() as handle:
    dataset = json.load(handle)

updates = {
    f"{DOC}:table2_entry13_16o": {
        "section": "4.1.13",
        "substrate_mass": 70,
        "substrate_amount": 0.24,
        "product_name": "5-allyl-7-phenyl-8-(trimethylsilyl)-3-oxabicyclo[4.2.0]octa-1(8),5-dien-4-one",
        "product_mass": 45,
    },
    f"{DOC}:table2_entry14_16p": {
        "section": "4.1.14",
        "substrate_mass": 69,
        "substrate_amount": 0.24,
        "product_name": "7-hexyl-5-methyl-8-(trimethylsilyl)-3-oxabicyclo[4.2.0]octa-1(8),5-dien-4-one",
        "product_mass": 17,
    },
}

records = {record["record_id"]: record for record in dataset["experiments"]}
result = []
for record_id, values in updates.items():
    record = json.loads(json.dumps(records[record_id]))
    record["source_reaction_id"] += f"; section {values['section']}"
    if PAGE7 not in record["evidence_ids"]:
        record["evidence_ids"].append(PAGE7)

    participants = {participant["entity_id"]: participant for participant in record["participants"]}
    substrate = participants["substrate"]
    add_evidence(substrate["label"], PAGE7)
    add_evidence(substrate["name"], PAGE7)
    substrate["amounts"] = [
        quantity("mass", values["substrate_mass"], "mg"),
        quantity("amount", values["substrate_amount"], "mmol"),
    ]

    product = participants["product_17"]
    add_evidence(product["label"], PAGE7)
    product["name"] = {
        "value": values["product_name"],
        "evidence_ids": [PAGE3, PAGE7],
        "verification": "unreviewed",
    }
    product["amounts"] = [quantity("mass", values["product_mass"], "mg")]

    toluene = participants["toluene"]
    add_evidence(toluene["label"], PAGE7)
    add_evidence(toluene["name"], PAGE7)
    toluene["amounts"] = [quantity("volume", 6, "mL")]

    conditions = {condition["name"]: condition for condition in record["steps"][0]["conditions"]}
    add_evidence(conditions["temperature"]["fact"], PAGE7)
    add_evidence(conditions["time"]["fact"], PAGE7)
    conditions["atmosphere"]["fact"] = {
        "value": "argon",
        "evidence_ids": [PAGE7],
        "verification": "unreviewed",
    }

    outcomes = {outcome["name"]: outcome for outcome in record["outcomes"]}
    yield_name = next(name for name in outcomes if name.startswith("isolated_yield_17"))
    add_evidence(outcomes[yield_name]["fact"], PAGE7)

    record["notes"] = [
        note for note in record["notes"]
        if not (isinstance(note.get("value"), str) and note["value"].startswith("Only the nominal page-3"))
    ]
    record["notes"].append({
        "value": f"The exact preparation in section {values['section']} supplies row-specific quantities and product mass; it is merged with the corresponding Table 2 row rather than counted twice.",
        "evidence_ids": [PAGE7],
        "verification": "unreviewed",
    })
    record["review"]["unresolved"] = [
        item for item in record["review"]["unresolved"]
        if not item.startswith("Row-specific mass")
    ]
    record["status"] = "candidate"
    record["review"]["method"] = "none"
    record["review"]["checked_fields"] = []
    result.append(record)

OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"output": str(OUT), "records": len(result)}, ensure_ascii=False))
