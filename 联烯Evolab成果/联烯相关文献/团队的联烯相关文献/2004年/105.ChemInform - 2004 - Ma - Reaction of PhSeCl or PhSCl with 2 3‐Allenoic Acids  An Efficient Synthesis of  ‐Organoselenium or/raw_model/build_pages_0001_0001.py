#!/usr/bin/env python3
"""Build the raw page-1 extraction for ChemInform entry R 0060."""

import json
from pathlib import Path


DOC = "doc_9d6e249c5e399d9d"
IMAGE = f"{DOC}:page1:image"
TEXT = f"{DOC}:page1:text"
OUT = Path(__file__).with_name("extracted_records_pages_0001_0001.json")


def fact(value, evidence=(IMAGE,)):
    return {
        "value": value,
        "evidence_ids": list(evidence),
        "verification": "missing" if value is None else "unreviewed",
    }


def participant(entity_id, role, label, smiles=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label),
        "name": fact(None, ()),
        "smiles": fact(smiles),
        "smiles_parseable": True if smiles else None,
        "structure_verified": False,
        "amounts": [],
    }


def field(name, value, *, target=None, evidence=(IMAGE,)):
    item = {"name": name, "fact": fact(value, evidence)}
    if target:
        item["target_entity_ids"] = [target]
    return item


def record(series, entry, substrate_label, reagent_label, product_label,
           reaction_time, reaction_yield, product_ambiguity=False):
    prefix = f"{series}_{entry}"
    substrate = f"{prefix}_substrate"
    reagent = f"{prefix}_reagent"
    solvent = f"{prefix}_solvent"
    product = f"{prefix}_product"
    unresolved = [
        "This is a ChemInform abstract entry citing Synlett 2004, 1, 85-88; the supplied PDF is not the primary article, so the row is classified as a literature example.",
        "No reagent or substrate amounts, concentration, reaction scale, workup, purification, or detailed procedure are supplied on this page.",
        "The yield measurement basis is not stated.",
        "No Supporting Information was supplied or explicitly associated.",
        "The generic R-group scheme and abbreviated substituent labels do not support a source-verified complete substrate or product SMILES.",
    ]
    if product_ambiguity:
        unresolved.append(
            "The lower product chalcogen annotation appears visually inconsistent with the PhSCl reagent/title in the supplied rendering; product identity is retained only by source label and no product SMILES is assigned."
        )
    return {
        "record_id": f"{DOC}:{prefix}",
        "document_id": DOC,
        "source_reaction_id": f"R 0060 {series} scheme entry {entry}",
        "record_kind": "literature_example",
        "status": "needs_review",
        "completeness": "partial",
        "evidence_ids": [IMAGE, TEXT],
        "participants": [
            participant(substrate, "reactant", substrate_label),
            participant(reagent, "reagent", reagent_label),
            participant(solvent, "solvent", "MeCN (condition A)", "CC#N"),
            participant(product, "product", product_label),
        ],
        "steps": [{
            "step_id": "reaction",
            "participant_ids": [substrate, reagent, solvent],
            "conditions": [
                field("solvent", "MeCN"),
                field("temperature", {"number": 0, "unit": "°C", "raw_text": "0°C"}),
                field("atmosphere", "[N2]"),
                field("time", reaction_time),
            ],
        }],
        "outcomes": [
            field("yield", {"number": reaction_yield, "unit": "%"}, target=product),
            field("yield_measurement_basis", None, target=product, evidence=(IMAGE,)),
        ],
        "notes": [
            fact(
                "ChemInform R 0060 cites S. Ma, F. Pan, X. Hao, and X. Huang, Synlett 2004, 1, 85-88.",
                (IMAGE, TEXT),
            )
        ],
        "review": {
            "method": "model",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved,
        },
    }


records = [
    record(
        "phsecl", "a",
        "allenoic acid I-a (R1 = Bu; R2 = H)",
        "PhSeCl (II)",
        "butenolide III-a (R1 = Bu; R2 = H; Ph-Se substituent depicted)",
        {"number": 19, "unit": "h"}, 91,
    ),
    record(
        "phsecl", "b",
        "allenoic acid I-b (R1 = Ph; R2 = Pr)",
        "PhSeCl (II)",
        "butenolide III-b (R1 = Ph; R2 = Pr; Ph-Se substituent depicted)",
        {"number": 10, "unit": "h"}, 98,
    ),
    record(
        "phsecl", "c",
        "allenoic acid I-c (R1 = fused bicyclic aryl group drawn; R2 = Pr)",
        "PhSeCl (II)",
        "butenolide III-c (R1 = fused bicyclic aryl group drawn; R2 = Pr; Ph-Se substituent depicted)",
        {"number": 7, "unit": "h"}, 94,
    ),
    record(
        "phscl", "a",
        "allenoic acid IV-a (R3 = (CH2)6-Me; R4 = H; R5 = H)",
        "PhSCl (V)",
        "butenolide VI-a (R3 = (CH2)6-Me; R4 = H; R5 = H)",
        {"number": 10, "unit": "h", "qualifier": "approx", "raw_text": "~10 h"}, 71,
        product_ambiguity=True,
    ),
    record(
        "phscl", "b",
        "allenoic acid IV-b (R3 = Ph; R4 = H; R5 = CH2-Ph)",
        "PhSCl (V)",
        "butenolide VI-b (R3 = Ph; R4 = H; R5 = CH2-Ph)",
        {"number": 20, "unit": "h"}, 82,
        product_ambiguity=True,
    ),
    record(
        "phscl", "c",
        "allenoic acid IV-c (R3-R4 = cyclohexane ring drawn; R5 = Me)",
        "PhSCl (V)",
        "butenolide VI-c (R3-R4 = cyclohexane ring drawn; R5 = Me)",
        {"number": 10, "unit": "h", "qualifier": "approx", "raw_text": "~10 h"}, 61,
        product_ambiguity=True,
    ),
]

OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
print(f"wrote {len(records)} records to {OUT}")
