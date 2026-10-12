#!/usr/bin/env python3
"""Enrich existing Scheme 5 records from original PDF pages 7--8.

This is a machine extraction artifact.  It preserves the existing record
boundaries, adds page-7 experimental quantities, and emits a two-page
coverage ledger.  Page 8 contains references only and creates no record.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / "runs" / "current"
DOC = "doc_77c72f16fe1e869a"
PAGE7 = [f"{DOC}:page7:text", f"{DOC}:page7:image"]
PAGE8 = [f"{DOC}:page8:text", f"{DOC}:page8:image"]


def uniq(values):
    return list(dict.fromkeys(values))


def fact(value, evidence=None):
    return {
        "value": value,
        "evidence_ids": [] if value is None else list(evidence or []),
        "verification": "missing" if value is None else "unreviewed",
    }


def field(name, value, evidence=None, targets=None):
    out = {"name": name, "fact": fact(value, evidence)}
    if targets:
        out["target_entity_ids"] = list(targets)
    return out


def qty(number, unit):
    return {"number": number, "unit": unit}


def replace_amounts(participant, values):
    participant["amounts"] = [field(name, value, PAGE7) for name, value in values]


dataset = json.loads((RUN / "dataset.json").read_text())
by_id = {record["record_id"]: record for record in dataset["experiments"]}

details = {
    "5ad": {
        "start": "1a",
        "start_mass": 172,
        "base_mass": 11.0,
        "product_mass": 180,
        "yield": 65,
    },
    "5bd": {
        "start": "1b",
        "start_mass": 122,
        "base_mass": 12.0,
        "product_mass": 143,
        "yield": 63,
    },
    "5cd": {
        "start": "1c",
        "start_mass": 138,
        "base_mass": 12.0,
        "product_mass": 193,
        "yield": 79,
    },
}

records = []
for product, detail in details.items():
    rid = f"{DOC}:scheme5_{product}"
    record = copy.deepcopy(by_id[rid])
    record["evidence_ids"] = uniq(record["evidence_ids"] + PAGE7)

    participants = {p["entity_id"]: p for p in record["participants"]}
    replace_amounts(participants[detail["start"]], [
        ("mass", qty(detail["start_mass"], "mg")),
        ("amount", qty(1.0, "mmol")),
    ])
    replace_amounts(participants["4d"], [
        ("mass", qty(106, "mg")),
        ("amount", qty(1.0, "mmol")),
    ])
    participants["t_BuOK"]["amounts"] = [
        field("catalyst_loading", qty(10, "mol%"), PAGE7),
        field("mass", qty(detail["base_mass"], "mg"), PAGE7),
        field("amount", qty(0.1, "mmol"), PAGE7),
    ]
    replace_amounts(participants["acetone"], [("volume", qty(2, "mL"))])

    # Page 7 depicts and names each product.  Retain the pre-existing
    # candidate structure but add the new source evidence; merge will keep
    # structure_verified false.
    for key in ("label", "name", "smiles"):
        participants[product][key]["evidence_ids"] = uniq(
            participants[product][key]["evidence_ids"] + PAGE7
        )

    reaction = next(step for step in record["steps"] if step["step_id"] == "reaction")
    for condition in reaction["conditions"]:
        if condition["name"] == "time":
            condition["fact"] = fact(None)

    record["outcomes"] = [
        field("yield", qty(detail["yield"], "%"), PAGE7, [product]),
        field("product_mass", qty(detail["product_mass"], "mg"), PAGE7, [product]),
        field("product_form", "yellow liquid", PAGE7, [product]),
        field(
            "yield_measurement_basis",
            "isolated after silica gel chromatography",
            [f"{DOC}:page4:text", f"{DOC}:page4:image", *PAGE7],
            [product],
        ),
    ]
    generated_note_markers = (
        "Scheme 5 substrate-scope row",
        "The product is accompanied by IR",
        "The printed Scheme 5 header",
    )
    record["notes"] = [
        note for note in record["notes"]
        if not (
            isinstance(note.get("value"), str)
            and any(marker in note["value"] for marker in generated_note_markers)
        )
    ]
    record["notes"].extend([
        fact(
            "Scheme 5 substrate-scope row enriched from the matching detailed experiment in section 2.1.15, 2.1.16, or 2.1.17.",
            PAGE7,
        ),
        fact(
            "The product is accompanied by IR, 1H NMR, 13C NMR, MS, and HRMS characterization on page 7; spectra are not converted into reaction-condition fields.",
            PAGE7,
        ),
        fact(
            "The printed Scheme 5 header says 'yield of 7 (%)' although the products are labeled 5ad, 5bd, and 5cd.",
            [f"{DOC}:page3:text", f"{DOC}:page3:image"],
        ),
    ])
    record["review"]["unresolved"] = [
        "Supporting-information association is unestablished.",
        "Atmosphere is not reported.",
        "The detailed experiment does not restate an exact reaction time; the general procedure says reactions usually completed within 10 min, so the individual time remains missing.",
    ]
    record["status"] = "candidate"
    record["review"]["method"] = "none"
    record["review"]["reviewer"] = None
    record["review"]["checked_fields"] = []
    records.append(record)


coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 7,
            "state": "attempted",
            "regions": [
                {
                    "region": "left column, section 2.1.15 (5ad)",
                    "finding": "Detailed current-paper experiment for 5ad, including exact reactant/catalyst quantities, acetone volume, product mass, yield, product form, depicted structure, and characterization; merged into the existing Scheme 5 record.",
                    "evidence_ids": PAGE7,
                },
                {
                    "region": "left column, section 2.1.16 (5bd)",
                    "finding": "Detailed current-paper experiment for 5bd with exact quantities, product mass, yield, product form, depicted structure, and characterization; merged into the existing Scheme 5 record.",
                    "evidence_ids": PAGE7,
                },
                {
                    "region": "lower-left through upper-right columns, section 2.1.17 (5cd)",
                    "finding": "Detailed current-paper experiment for 5cd with exact quantities, product mass, yield, product form, depicted structure, and characterization; merged into the existing Scheme 5 record.",
                    "evidence_ids": PAGE7,
                },
                {
                    "region": "right column, acknowledgements and references 1-6(d)",
                    "finding": "Acknowledgements and cited literature only; no additional current-paper experiment, reaction arrow, table row, or footnote is present.",
                    "evidence_ids": PAGE7,
                },
            ],
            "record_ids": [f"{DOC}:scheme5_{product}" for product in details],
            "unresolved": [
                "The three detailed experiments do not restate exact reaction durations or atmosphere.",
                "Supporting-information association remains unestablished.",
            ],
        },
        {
            "page": 8,
            "state": "attempted",
            "regions": [
                {
                    "region": "upper two-column reference-list continuation; remaining page blank",
                    "finding": "References 6(e)-8(d) only. No current-paper experiment, scheme, reaction arrow, table, footnote, or experimental procedure is present, so no reaction record is created.",
                    "evidence_ids": PAGE8,
                }
            ],
            "record_ids": [],
            "unresolved": [
                "Cited papers were not supplied and their experiments were not expanded into records for this current-paper page pass."
            ],
        },
    ],
}


(RUN / "raw_model" / "pages_0007_0008_records.json").write_text(
    json.dumps(records, ensure_ascii=False, indent=2) + "\n"
)
(RUN / "coverage" / "pages_0007_0008.json").write_text(
    json.dumps(coverage, ensure_ascii=False, indent=2) + "\n"
)

tasks_path = RUN / "tasks.json"
tasks = json.loads(tasks_path.read_text())
for task in tasks:
    if task["evidence_id"] in {f"{DOC}:page7:text", f"{DOC}:page8:text"}:
        task["state"] = "attempted"
        task["reason"] = "Original page image and text inspected; see coverage/pages_0007_0008.json."
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({
    "updated_records": len(records),
    "new_records": 0,
    "coverage_pages": [7, 8],
}, ensure_ascii=False))
