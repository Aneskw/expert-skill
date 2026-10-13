#!/usr/bin/env python3
"""Build page-7 replacements for doc_b4569e6415d4f17a."""
from __future__ import annotations

import copy
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
DATASET = ROOT / "runs/current/dataset.json"
OUT = ROOT / "runs/current/raw_model/records_pages_0007_0007.json"
COVERAGE = ROOT / "runs/current/coverage/pages_0007_0007.json"
TASKS = ROOT / "runs/current/tasks.json"
DOC = "doc_b4569e6415d4f17a"
P7 = [f"{DOC}:page7:text", f"{DOC}:page7:image"]


def unique(values):
    return list(dict.fromkeys(values))


def fact(value, evidence_ids):
    return {
        "value": value,
        "evidence_ids": unique(evidence_ids) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def field(name, value, evidence_ids, targets=None, category=None):
    result = {"name": name, "fact": fact(value, evidence_ids)}
    if targets:
        result["target_entity_ids"] = targets
    if category:
        result["category"] = category
    return result


def quantity(number, unit):
    return {"number": number, "unit": unit}


def add_evidence(container, evidence_ids):
    container["evidence_ids"] = unique(container.get("evidence_ids", []) + evidence_ids)


def participant(record, entity_id):
    return next(p for p in record["participants"] if p["entity_id"] == entity_id)


def condition(record, name):
    for step in record["steps"]:
        for item in step["conditions"]:
            if item["name"] == name:
                return item
    raise KeyError(name)


dataset = json.loads(DATASET.read_text())
existing = {record["record_id"]: record for record in dataset["experiments"]}
record_ids = [
    f"{DOC}:reduction_12k_to_18k",
    f"{DOC}:scheme4_5r_12r",
    f"{DOC}:table3_entry4_6d",
    f"{DOC}:table3_entry5_6e",
]
records = [copy.deepcopy(existing[record_id]) for record_id in record_ids]
by_id = {record["record_id"]: record for record in records}


# Complete the cross-page NaBH4 reduction using the product mass/yield printed
# at the top of page 7.  The purification operation itself is on page 6.
reduction = by_id[f"{DOC}:reduction_12k_to_18k"]
add_evidence(reduction, P7)
reduction_product = participant(reduction, "product")
reduction_product["amounts"].append(
    field("product_mass", quantity(26.5, "mg"), P7, category="mass")
)
reduction_product["smiles"] = fact(
    "CCCCC(C(Br)=C)C(O)c1cccc2ccccc12",
    [f"{DOC}:page6:text", f"{DOC}:page6:image", *P7],
)
reduction_product["smiles_parseable"] = None
reduction_substrate = participant(reduction, "substrate")
reduction_substrate["smiles"] = fact(
    "CCCCC(C(Br)=C)C(=O)c1cccc2ccccc12",
    [f"{DOC}:page6:text", f"{DOC}:page6:image", *P7],
)
reduction_substrate["smiles_parseable"] = None
reduction["outcomes"] = [
    field(
        "isolated_yield",
        quantity(90, "%"),
        P7,
        ["product"],
        "yield",
    ),
    field(
        "yield_measurement_basis",
        "isolated",
        [f"{DOC}:page6:text", f"{DOC}:page6:image", *P7],
        ["product"],
        "measurement_basis",
    ),
]
reduction["review"]["unresolved"] = [
    "Starting material is described as crude 12k; its purity and molar amount are not reported.",
    "Candidate substrate/product connectivity and product stereochemistry remain unverified.",
]


# Replace the page-4-only Scheme-4 summary with the exact page-7 preparation.
tertiary = by_id[f"{DOC}:scheme4_5r_12r"]
add_evidence(tertiary, P7)
tertiary_substrate = participant(tertiary, "substrate")
tertiary_substrate["amounts"].extend(
    [
        field("substrate_mass", quantity(56.4, "mg"), P7, category="mass"),
        field("amount", quantity(0.30, "mmol"), P7, category="amount"),
    ]
)
tertiary_substrate["smiles"] = fact("CC(O)(c1ccccc1)C(CC)=C=C", P7)
tertiary_substrate["smiles_parseable"] = None
tertiary_bromine = participant(tertiary, "bromine")
tertiary_bromine["amounts"].extend(
    [
        field("solution_volume", quantity(0.72, "mL"), P7, category="volume"),
        field("concentration", quantity(0.5, "M"), P7, category="concentration"),
        field("amount", quantity(0.36, "mmol"), P7, category="amount"),
    ]
)
participant(tertiary, "mecn")["amounts"].append(
    field("solvent_volume", quantity(3.3, "mL"), P7, category="volume")
)
participant(tertiary, "water")["amounts"].append(
    field("solvent_volume", quantity(0.27, "mL"), P7, category="volume")
)
tertiary_product = participant(tertiary, "product")
tertiary_product["amounts"].append(
    field("product_mass", quantity(66.2, "mg"), P7, category="mass")
)
tertiary_product["smiles"] = fact("CC(=O)C(CC)(c1ccccc1)C(Br)=C", P7)
tertiary_product["smiles_parseable"] = None
for condition_name in ("solvent_ratio", "temperature", "time"):
    add_evidence(condition(tertiary, condition_name)["fact"], P7)
tertiary["outcomes"] = [
    field("reported_yield", quantity(83, "%"), P7, ["product"], "yield"),
    field("yield_measurement_basis", None, [], ["product"], "measurement_basis"),
]
tertiary["review"]["unresolved"] = [
    "The exact page-7 paragraph does not state workup, purification, or yield measurement basis.",
    "Candidate substrate/product connectivity remains machine-derived and unverified.",
]


# The acknowledgment supplies reproducibility context for two already extracted
# Table-3 rows; it is not a new execution with independent conditions/results.
for record_id in (f"{DOC}:table3_entry4_6d", f"{DOC}:table3_entry5_6e"):
    record = by_id[record_id]
    add_evidence(record, P7)
    record["notes"].append(
        fact(
            "The acknowledgments state that Mr. Zhichao Ma reproduced the results presented in entries 4 and 5 of Table 3.",
            P7,
        )
    )


OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")

coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 7,
            "state": "attempted",
            "regions": [
                {
                    "region": "upper-left continuation of the 12k-to-18k reduction paragraph",
                    "finding": "The cross-page product statement gives 18k as 26.5 mg in 90% yield; characterization follows. These facts complete the existing reduction record rather than defining a new experiment.",
                    "evidence_ids": P7,
                },
                {
                    "region": "middle-left 5r-to-12r reaction drawing and exact preparation paragraph",
                    "finding": "Exact tertiary-allenol bromination quantities, 0 °C/30 min conditions, 66.2 mg product mass, and 83% yield were merged into the existing Scheme-4 record.",
                    "evidence_ids": P7,
                },
                {
                    "region": "lower-left acknowledgments",
                    "finding": "The authors state that Table 3 entries 4 and 5 were reproduced by a group member. This is linked as reproducibility context and is not counted as a new condition.",
                    "evidence_ids": P7,
                },
                {
                    "region": "right-column references and page furniture",
                    "finding": "References [1]-[16] are citations to external work and do not provide new present-paper experiment rows on this page.",
                    "evidence_ids": P7,
                },
            ],
            "record_ids": record_ids,
            "unresolved": [
                "The 12r paragraph does not report workup, purification, or yield measurement basis.",
                "The crude 12k starting material has no reported purity or molar amount.",
                "The acknowledgment does not supply independent quantities or procedures for the reproduced Table 3 entries.",
                "No Supporting Information or cited reference was supplied or explicitly associated; external details were not inferred.",
                "Candidate molecular connectivity and stereochemistry remain unverified.",
            ],
        }
    ],
}
COVERAGE.parent.mkdir(parents=True, exist_ok=True)
COVERAGE.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

tasks = json.loads(TASKS.read_text())
for task in tasks:
    if task["task_id"] == f"{DOC}:page7:text":
        task["state"] = "attempted"
TASKS.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(
    json.dumps(
        {
            "replacement_records": len(records),
            "record_file": str(OUT),
            "coverage_file": str(COVERAGE),
        },
        ensure_ascii=False,
    )
)
