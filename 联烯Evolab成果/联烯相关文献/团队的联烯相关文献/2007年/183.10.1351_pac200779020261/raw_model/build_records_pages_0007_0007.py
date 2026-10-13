#!/usr/bin/env python3
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "runs/current"
DOC = "doc_cc2bd70aeb39d26b"
P6 = [f"{DOC}:page6:text", f"{DOC}:page6:image"]
P7 = [f"{DOC}:page7:text", f"{DOC}:page7:image"]
P7_IMAGE = [f"{DOC}:page7:image"]


def fact(value, evidence):
    return {
        "value": value,
        "evidence_ids": list(evidence) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def quantity(number, unit):
    return {"number": number, "unit": unit}


def field(name, value, evidence, targets=None):
    result = {"name": name, "fact": fact(value, evidence)}
    if targets:
        result["target_entity_ids"] = list(targets)
    return result


def participant(entity_id, role, label, evidence, name=None, smiles=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence) if name else fact(None, []),
        "smiles": fact(smiles, evidence) if smiles else fact(None, []),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": [],
    }


def scheme15_record(
    suffix,
    prefix,
    alkyl_label,
    reagent_label,
    reagent_name,
    reagent_smiles,
    product_number,
    product_label,
    substrate_smiles,
    product_smiles,
    yield_number,
    drawing_ambiguity=False,
):
    evidence = P6 + P7
    participants = [
        participant(
            f"{prefix}_substrate",
            "reactant",
            f"3-{alkyl_label}-3,4-pentadien-2-ol (Scheme 15 substrate)",
            P6 + P7_IMAGE,
            smiles=substrate_smiles,
        ),
        participant(
            f"{prefix}_halogen",
            "reagent",
            reagent_label,
            P6 + P7_IMAGE,
            name=reagent_name,
            smiles=reagent_smiles,
        ),
        participant(
            f"{prefix}_mecn",
            "solvent",
            "CH3CN",
            P7_IMAGE,
            name="acetonitrile",
            smiles="CC#N",
        ),
        participant(
            f"{prefix}_water",
            "solvent",
            "H2O",
            P7_IMAGE,
            name="water",
            smiles="O",
        ),
        participant(
            f"{prefix}_product",
            "product",
            f"{product_label} {product_number}",
            P6 + P7_IMAGE,
            smiles=product_smiles,
        ),
    ]
    unresolved = [
        "This review article summarizes cited reference 12; experiment-level details absent here require review against the original cited paper.",
        "All machine constitutional structures and the source's 1,2-H-shift assignment remain unverified.",
        "Halogen equivalents, CH3CN/H2O ratio, duration, atmosphere, workup, purification, and yield measurement basis are not reported.",
    ]
    if drawing_ambiguity:
        unresolved.append(
            "The upper product drawing visibly carries an I label, while the explicit legend assigns X = Br to product 16; the brominated identity is retained from that legend but requires source review."
        )
    return {
        "record_id": f"{DOC}:{suffix}",
        "document_id": DOC,
        "source_reaction_id": suffix,
        "record_kind": "literature_example",
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": evidence,
        "participants": participants,
        "steps": [
            {
                "step_id": "reaction",
                "participant_ids": [p["entity_id"] for p in participants],
                "conditions": [
                    field("solvent", "CH3CN/H2O (ratio not reported)", P7_IMAGE),
                    field("temperature", "r.t.", P7_IMAGE),
                    field("time", None, []),
                    field("atmosphere", None, []),
                    field("workup", None, []),
                    field("purification", None, []),
                ],
            }
        ],
        "outcomes": [
            field(
                "reported_yield",
                quantity(yield_number, "%"),
                P7_IMAGE,
                [f"{prefix}_product"],
            ),
            field("yield_measurement_basis", None, []),
        ],
        "notes": [
            fact(
                "Page 6 attributes this Scheme 15 product class to a 1,2-H shift from a 14-type cationic intermediate.",
                P6,
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
    scheme15_record(
        "scheme15_iodine_condition_from_page6_prose",
        "s15_nbu_i",
        "n-butyl",
        "I2",
        "iodine",
        "[I][I]",
        "15",
        "4-iodo-3-n-butylpent-4-en-2-one",
        "C=C=C(CCCC)C(O)C",
        "C=C(I)C(CCCC)C(=O)C",
        49,
    ),
    scheme15_record(
        "scheme15_bromine_condition_from_page6_prose",
        "s15_nbu_br",
        "n-butyl",
        "Br2",
        "bromine",
        "BrBr",
        "16",
        "4-bromo-3-n-butylpent-4-en-2-one",
        "C=C=C(CCCC)C(O)C",
        "C=C(Br)C(CCCC)C(=O)C",
        46,
        drawing_ambiguity=True,
    ),
    scheme15_record(
        "scheme15_iodine_nhexyl_product17",
        "s15_nhex_i",
        "n-hexyl",
        "I2",
        "iodine",
        "[I][I]",
        "17",
        "4-iodo-3-n-hexylpent-4-en-2-one",
        "C=C=C(CCCCCC)C(O)C",
        "C=C(I)C(CCCCCC)C(=O)C",
        52,
    ),
]

records_path = OUT / "raw_model/records_pages_0007_0007.json"
records_path.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")

coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 7,
            "state": "attempted",
            "regions": [
                {
                    "region": "upper Scheme 15, n-C4H9 substrate arrow and X = I/X = Br legend",
                    "finding": "Two distinct cited prior-work reactions were resolved from the shared arrow: I2 gives product 15 in 49%, while Br2 gives product 16 in 46%, both in CH3CN/H2O at room temperature.",
                    "evidence_ids": P7,
                },
                {
                    "region": "middle Scheme 15, n-C6H13 substrate arrow",
                    "finding": "One cited prior-work I2 reaction gives product 17 in 52% in CH3CN/H2O at room temperature.",
                    "evidence_ids": P7,
                },
                {
                    "region": "conclusion, acknowledgments, and references below Scheme 15",
                    "finding": "Conclusion summarizes substituent- and condition-dependent selectivity; acknowledgments and references add no independent reaction arrow or experimental row.",
                    "evidence_ids": P7,
                },
            ],
            "record_ids": [record["record_id"] for record in records],
            "unresolved": [
                "Scheme 15 omits halogen equivalents, solvent ratio, duration, atmosphere, workup, purification, and yield measurement basis.",
                "The upper product drawing appears to show I even though the legend explicitly assigns X = Br to product 16.",
                "The three reactions are summaries of cited reference 12, and their candidate structures and 1,2-H-shift interpretation remain unverified.",
                "No supporting-information file was supplied or explicitly associated.",
            ],
        }
    ],
}

coverage_path = OUT / "coverage/pages_0007_0007.json"
coverage_path.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

tasks_path = OUT / "tasks.json"
tasks = json.loads(tasks_path.read_text())
for task in tasks:
    if task["task_id"] == f"{DOC}:page7:text":
        task["state"] = "attempted"
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(
    json.dumps(
        {
            "records": len(records),
            "records_path": str(records_path),
            "coverage_path": str(coverage_path),
        },
        ensure_ascii=False,
    )
)
