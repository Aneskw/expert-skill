#!/usr/bin/env python3
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
DOC = "doc_32ed381ace69ff22"
OUT = ROOT / "runs/current"


def ev(page):
    return [f"{DOC}:page{page}:text", f"{DOC}:page{page}:image"]


def fact(value, evidence):
    return {
        "value": value,
        "evidence_ids": list(evidence) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def participant(entity_id, role, label, evidence, amounts=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(None, []),
        "smiles": fact(None, []),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": [
            {"name": name, "fact": fact(value, evidence)}
            for name, value in (amounts or {}).items()
        ],
    }


def record(rid, title, participants, conditions, outcomes, unresolved):
    evidence = ev(7)
    ps = [
        participant(f"p{i + 1}", role, label, evidence, amounts)
        for i, (role, label, amounts) in enumerate(participants)
    ]
    missing_conditions = {
        "reaction_scale": None,
        "reactant_stoichiometry": None,
        "atmosphere": None,
        "concentration": None,
        "workup": None,
        "purification": None,
    }
    all_conditions = dict(conditions)
    for key, value in missing_conditions.items():
        all_conditions.setdefault(key, value)
    all_outcomes = dict(outcomes)
    all_outcomes.setdefault("yield_measurement_basis", None)
    return {
        "record_id": f"{DOC}:{rid}",
        "document_id": DOC,
        "source_reaction_id": rid,
        "record_kind": "literature_example",
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": evidence,
        "participants": ps,
        "steps": [
            {
                "step_id": "step1",
                "participant_ids": [p["entity_id"] for p in ps],
                "conditions": [
                    {"name": name, "fact": fact(value, evidence)}
                    for name, value in all_conditions.items()
                ],
            }
        ],
        "outcomes": [
            {"name": name, "fact": fact(value, evidence)}
            for name, value in all_outcomes.items()
        ],
        "notes": [fact(title, evidence)],
        "review": {
            "method": "model",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": list(unresolved)
            + [
                "This ACCOUNT attributes the synthetic-application results to cited earlier work; the original cited papers and SI were not supplied.",
                "Structures are defined by compound labels and drawings; SMILES remain null and structures unverified.",
            ],
        },
    }


R = []


def add(*args, **kwargs):
    R.append(record(*args, **kwargs))


# Scheme 12: five distinct Pd-catalyzed coupling arrows.
add(
    "scheme12_11a_nbutylzinc",
    "Scheme 12 Negishi coupling of ester 11a with n-BuZnBr to 26a",
    [
        ("reactant", "ethyl 2-methyl-3-iodo-3-butenoate 11a", None),
        ("reactant", "n-BuZnBr", None),
        ("catalyst", "Pd(PPh3)4", {"catalyst_loading": {"number": 5, "unit": "mol%"}}),
        ("solvent", "THF", None),
        ("product", "coupling product 26a", None),
    ],
    {"temperature": None, "time": {"number": 3, "unit": "h"}},
    {"yield": {"number": 90, "unit": "%"}},
    ["The arrow does not report temperature or the yield measurement basis."],
)

add(
    "scheme12_11a_phenylzinc",
    "Scheme 12 Negishi coupling of ester 11a with PhZnBr to 26b",
    [
        ("reactant", "ethyl 2-methyl-3-iodo-3-butenoate 11a", None),
        ("reactant", "PhZnBr", None),
        ("catalyst", "Pd(PPh3)4", {"catalyst_loading": {"number": 5, "unit": "mol%"}}),
        ("solvent", "THF", None),
        ("product", "coupling product 26b", None),
    ],
    {"temperature": None, "time": {"number": 6, "unit": "h"}},
    {"yield": {"number": 70, "unit": "%"}},
    ["The arrow does not report temperature or the yield measurement basis."],
)

add(
    "scheme12_11a_phenylacetylene",
    "Scheme 12 Sonogashira coupling of ester 11a with phenylacetylene to 26c",
    [
        ("reactant", "ethyl 2-methyl-3-iodo-3-butenoate 11a", None),
        ("reactant", "phenylacetylene", None),
        ("catalyst", "PdCl2(PPh3)2", {"catalyst_loading": {"number": 5, "unit": "mol%"}}),
        ("catalyst", "CuI", {"catalyst_loading": {"number": 10, "unit": "mol%"}}),
        ("reagent", "Et3N", None),
        ("product", "coupling product 26c", None),
    ],
    {"solvent": None, "temperature": None, "time": {"number": 6.5, "unit": "h"}},
    {"yield": {"number": 85, "unit": "%"}},
    [
        "The arrow does not identify a separate solvent or temperature; Et3N is printed without an amount or an explicit solvent/base role.",
        "The yield measurement basis is not stated.",
    ],
)

add(
    "scheme12_9a_phenylzinc",
    "Scheme 12 Negishi coupling of ester mixture 9a with PhZnBr to 26d",
    [
        ("reactant", "3-iodo-3-pentenoate 9a (E/Z = 2.5:1)", None),
        ("reactant", "PhZnBr", None),
        ("catalyst", "Pd(PPh3)4", {"catalyst_loading": {"number": 5, "unit": "mol%"}}),
        ("solvent", "THF", None),
        ("product", "coupling product 26d", None),
    ],
    {"temperature": None, "time": {"number": 8, "unit": "h"}},
    {"yield": {"number": 76, "unit": "%"}, "product_E_Z_ratio": "2.5:1"},
    ["The arrow does not report temperature or the yield measurement basis."],
)

add(
    "scheme12_9a_phenylacetylene",
    "Scheme 12 Sonogashira coupling of ester mixture 9a with phenylacetylene to 26e",
    [
        ("reactant", "3-iodo-3-pentenoate 9a (E/Z = 2.5:1)", None),
        ("reactant", "phenylacetylene", None),
        ("catalyst", "PdCl2(PPh3)2", {"catalyst_loading": {"number": 5, "unit": "mol%"}}),
        ("catalyst", "CuI", {"catalyst_loading": {"number": 10, "unit": "mol%"}}),
        ("reagent", "Et3N", None),
        ("product", "coupling product 26e", None),
    ],
    {"solvent": None, "temperature": None, "time": {"number": 6, "unit": "h"}},
    {"yield": {"number": 82, "unit": "%"}, "product_E_Z_ratio": "2.5:1"},
    [
        "The arrow does not identify a separate solvent or temperature; Et3N is printed without an amount or an explicit solvent/base role.",
        "The yield measurement basis is not stated.",
    ],
)


# Scheme 13: six distinct functional-group-specific coupling arrows.
add(
    "scheme13_17c_phenylzinc",
    "Scheme 13 Negishi coupling of iodoalkenamide 17c with PhZnBr to 27a",
    [
        ("reactant", "iodoalkenamide 17c", None),
        ("reactant", "PhZnBr", None),
        ("catalyst", "Pd(PPh3)4", {"catalyst_loading": {"number": 5, "unit": "mol%"}}),
        ("solvent", "THF", None),
        ("product", "3-alkenamide coupling product 27a", None),
    ],
    {"temperature": "room temperature", "time": {"number": 8, "unit": "h"}},
    {"yield": {"number": 87, "unit": "%"}},
    ["The yield measurement basis is not stated."],
)

add(
    "scheme13_17c_phenylacetylene",
    "Scheme 13 Sonogashira coupling of iodoalkenamide 17c with phenylacetylene to 27b",
    [
        ("reactant", "iodoalkenamide 17c", None),
        ("reactant", "phenylacetylene", None),
        ("catalyst", "PdCl2(PPh3)2", {"catalyst_loading": {"number": 5, "unit": "mol%"}}),
        ("catalyst", "CuI", {"catalyst_loading": {"number": 10, "unit": "mol%"}}),
        ("reagent", "Et3N", None),
        ("product", "3-alkenamide coupling product 27b", None),
    ],
    {"solvent": None, "temperature": "room temperature", "time": {"number": 19, "unit": "h"}},
    {"yield": {"number": 83, "unit": "%"}},
    [
        "The arrow does not identify a separate solvent; Et3N is printed without an amount or an explicit solvent/base role.",
        "The yield measurement basis is not stated.",
    ],
)

add(
    "scheme13_19b_phenylzinc",
    "Scheme 13 Negishi coupling of iodoalkenenitrile 19b with PhZnBr to 28a",
    [
        ("reactant", "iodoalkenenitrile 19b", None),
        ("reactant", "PhZnBr", None),
        ("catalyst", "Pd(PPh3)4", {"catalyst_loading": {"number": 5, "unit": "mol%"}}),
        ("solvent", "THF", None),
        ("product", "3-alkenenitrile coupling product 28a", None),
    ],
    {"temperature": "room temperature", "time": {"number": 7, "unit": "h"}},
    {"yield": {"number": 74, "unit": "%"}},
    ["The yield measurement basis is not stated."],
)

add(
    "scheme13_19b_phenylacetylene",
    "Scheme 13 Sonogashira coupling of iodoalkenenitrile 19b with phenylacetylene to 28b",
    [
        ("reactant", "iodoalkenenitrile 19b", None),
        ("reactant", "phenylacetylene", None),
        ("catalyst", "PdCl2(PPh3)2", {"catalyst_loading": {"number": 5, "unit": "mol%"}}),
        ("catalyst", "CuI", {"catalyst_loading": {"number": 10, "unit": "mol%"}}),
        ("reagent", "K2CO3", None),
        ("product", "3-alkenenitrile coupling product 28b", None),
    ],
    {"solvent": None, "temperature": "room temperature", "time": {"number": 20, "unit": "h"}},
    {"yield": {"number": 91, "unit": "%"}},
    ["No solvent, K2CO3 amount, or yield measurement basis is printed for this arrow."],
)

add(
    "scheme13_25a_1hexyne",
    "Scheme 13 Sonogashira coupling of iodophosphine oxide 25a with 1-hexyne to 29a",
    [
        ("reactant", "iodo-substituted 2-propenyl diphenylphosphine oxide 25a", None),
        ("reactant", "1-hexyne (n-C4H9-CCH)", None),
        ("catalyst", "PdCl2(PPh3)2", {"catalyst_loading": {"number": 1, "unit": "mol%"}}),
        ("catalyst", "CuI", {"catalyst_loading": {"number": 1, "unit": "mol%"}}),
        ("reagent", "Et3N", None),
        ("product", "2-propenyl diphenylphosphine oxide coupling product 29a", None),
    ],
    {"solvent": None, "temperature": "room temperature", "time": None},
    {"yield": {"number": 93, "unit": "%"}},
    [
        "The arrow does not report reaction time or a separate solvent; Et3N is printed without an amount or an explicit solvent/base role.",
        "The yield measurement basis is not stated.",
    ],
)

add(
    "scheme13_25a_phenylacetylene",
    "Scheme 13 Sonogashira coupling of iodophosphine oxide 25a with phenylacetylene to 29b",
    [
        ("reactant", "iodo-substituted 2-propenyl diphenylphosphine oxide 25a", None),
        ("reactant", "phenylacetylene", None),
        ("catalyst", "PdCl2(PPh3)2", {"catalyst_loading": {"number": 1, "unit": "mol%"}}),
        ("catalyst", "CuI", {"catalyst_loading": {"number": 1, "unit": "mol%"}}),
        ("reagent", "Et3N", None),
        ("product", "2-propenyl diphenylphosphine oxide coupling product 29b", None),
    ],
    {"solvent": None, "temperature": "room temperature", "time": None},
    {"yield": {"number": 95, "unit": "%"}},
    [
        "The arrow does not report reaction time or a separate solvent; Et3N is printed without an amount or an explicit solvent/base role.",
        "The yield measurement basis is not stated.",
    ],
)


records_path = OUT / "raw_model/records_pages_0007_0008.json"
records_path.write_text(json.dumps(R, ensure_ascii=False, indent=2))

coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 7,
            "state": "attempted",
            "regions": [
                {
                    "region": "upper-left prose and Scheme 12",
                    "finding": "Five cited synthetic-application coupling arrows: three reactions of ester 11a and two reactions of E/Z ester 9a, with separate catalysts, times, yields, and retained E/Z ratios where printed.",
                    "evidence_ids": [f"{DOC}:page7:image"],
                },
                {
                    "region": "upper-right Scheme 13 and adjoining prose",
                    "finding": "Six cited coupling arrows for iodoalkenamide 17c, iodoalkenenitrile 19b, and phosphine oxide 25a; each arrow was recorded independently.",
                    "evidence_ids": [f"{DOC}:page7:image"],
                },
                {
                    "region": "lower columns: conclusion, acknowledgement, and start of references",
                    "finding": "Summary and bibliography only; no additional individual experiment beyond Schemes 12-13.",
                    "evidence_ids": [f"{DOC}:page7:image"],
                },
            ],
            "record_ids": [r["record_id"] for r in R],
            "unresolved": [
                "The ACCOUNT gives no full procedure for Schemes 12-13; scale, organic-partner stoichiometry, atmosphere, concentration, workup, purification, and yield basis are absent.",
                "The original cited papers and any SI were not supplied; drawing-defined structures remain unverified with null SMILES.",
                "Scheme 12 omits temperature; the two 25a arrows in Scheme 13 omit time, and several Sonogashira arrows do not identify a separate solvent.",
            ],
        },
        {
            "page": 8,
            "state": "attempted",
            "regions": [
                {
                    "region": "both columns and footer",
                    "finding": "References 2-23 and article identifier only; no reaction arrow, table, experimental procedure, or current-page result record.",
                    "evidence_ids": [f"{DOC}:page8:image"],
                }
            ],
            "record_ids": [],
            "unresolved": [
                "Bibliographic citations were not treated as experiments, and no SI association was inferred from them."
            ],
        },
    ],
}
(OUT / "coverage/pages_0007_0008.json").write_text(
    json.dumps(coverage, ensure_ascii=False, indent=2)
)

tasks_path = OUT / "tasks.json"
tasks = json.loads(tasks_path.read_text())
for task in tasks:
    if task["document_id"] == DOC and task["task_id"] in {
        f"{DOC}:page7:text",
        f"{DOC}:page8:text",
    }:
        task["state"] = "attempted"
        task["visual_evidence_id"] = task["task_id"].replace(":text", ":image")
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2))

print(
    json.dumps(
        {
            "records": len(R),
            "record_ids": [r["record_id"] for r in R],
            "records_path": str(records_path),
        },
        ensure_ascii=False,
    )
)
