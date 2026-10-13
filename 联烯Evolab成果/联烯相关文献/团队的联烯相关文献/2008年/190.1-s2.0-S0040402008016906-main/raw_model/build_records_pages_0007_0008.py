#!/usr/bin/env python3
"""Build page-7 replacements and page-7/8 coverage for doc_b77579854e4d0662."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
DATASET = ROOT / "runs/current/dataset.json"
OUT = ROOT / "runs/current/raw_model/records_pages_0007_0008.json"
COVERAGE = ROOT / "runs/current/coverage/pages_0007_0008.json"
TASKS = ROOT / "runs/current/tasks.json"
DOC = "doc_b77579854e4d0662"


def ev(page):
    return [f"{DOC}:page{page}:text", f"{DOC}:page{page}:image"]


def fact(value, evidence=()):
    return {
        "value": value,
        "evidence_ids": list(dict.fromkeys(evidence)),
        "verification": "missing" if value is None else "unreviewed",
    }


def q(number, unit, **extra):
    value = {"number": number, "unit": unit}
    value.update(extra)
    return value


def fld(name, value, evidence=(), targets=None):
    item = {"name": name, "fact": fact(value, evidence)}
    if targets:
        item["target_entity_ids"] = targets
    return item


def participant(entity_id, role, label, evidence, amounts=(), name=None, smiles=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence) if name else fact(None),
        "smiles": fact(smiles, evidence) if smiles else fact(None),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": list(amounts),
    }


def amount(name, value, evidence):
    return fld(name, value, evidence)


def record(rid, kind, evidence, participants, steps, outcomes, notes=(), unresolved=()):
    return {
        "record_id": f"{DOC}:{rid}",
        "document_id": DOC,
        "source_reaction_id": rid,
        "record_kind": kind,
        "status": "needs_review",
        "completeness": "partial",
        "evidence_ids": list(dict.fromkeys(evidence)),
        "participants": participants,
        "steps": steps,
        "outcomes": outcomes,
        "notes": [fact(note, evidence) for note in notes],
        "review": {
            "method": "model",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": list(unresolved),
        },
    }


records = []


# Section 4.4.1 gives the exact preparation of the authentic pair described on
# page 3 as originating from previous study 16. Keep its prior-work class while
# replacing the former page-3-only placeholder with the complete printed recipe.
evidence = ev(3) + ev(7)
parts = [
    participant("cu_otf2", "catalyst", "Cu(OTf)2", evidence, [
        amount("mass", q(4, "mg"), ev(7)),
        amount("amount", q(0.011, "mmol"), ev(7)),
    ]),
    participant("ss_ph_box", "catalyst", "(S,S)-Ph-BOX", evidence, [
        amount("mass", q(4, "mg"), ev(7)),
        amount("amount", q(0.012, "mmol"), ev(7)),
    ]),
    participant("dcm", "solvent", "CH2Cl2", evidence, [
        amount("volume", q(2, "mL"), ev(7)),
    ], name="dichloromethane", smiles="ClCCl"),
    participant("allenyl_ketoester", "reactant", "ethyl 2-(2',3'-butadienyl)-3-oxobutyrate", evidence, [
        amount("mass", q(18, "mg"), ev(7)),
        amount("amount", q(0.099, "mmol"), ev(7)),
    ]),
    participant("dbad", "reactant", "dibenzyl azodicarboxylate", evidence, [
        amount("mass", q(36, "mg"), ev(7)),
        amount("amount", q(0.11, "mmol"), ev(7)),
    ]),
    participant("k2co3", "reagent", "K2CO3", evidence, [
        amount("mass", q(28, "mg"), ev(7)),
        amount("amount", q(0.20, "mmol"), ev(7)),
    ]),
    participant("pdpph3", "catalyst", "Pd(PPh3)4", evidence, [
        amount("mass", q(6, "mg"), ev(7)),
        amount("amount", q(0.0050, "mmol"), ev(7)),
    ]),
    participant("2g", "reactant", "p-bromoiodobenzene", evidence, [
        amount("mass", q(34, "mg"), ev(7)),
        amount("amount", q(0.12, "mmol"), ev(7)),
    ], name="1-bromo-4-iodobenzene", smiles="Brc1ccc(I)cc1"),
    participant("dioxane", "solvent", "1,4-dioxane", evidence, [
        amount("volume", q(2, "mL"), ev(7)),
    ], smiles="O1CCOCC1"),
    participant("rr4dg", "product", "(3R,5R)-4dg", evidence, [
        amount("isolated_mass", q(19, "mg"), ev(7)),
    ], name="1,2-dibenzyloxycarbonyl-3-ethoxycarbonyl-3-acetyl-5-(1'-(4''-bromophenyl)ethenyl)pyrazolidine"),
    participant("rs4dg", "product", "(3R,5S)-4dg", evidence, [
        amount("isolated_mass", q(38, "mg"), ev(7)),
    ], name="1,2-dibenzyloxycarbonyl-3-ethoxycarbonyl-3-acetyl-5-(1'-(4''-bromophenyl)ethenyl)pyrazolidine"),
]
records.append(record(
    "equation1_prior_authentic_4dg",
    "literature_example",
    evidence,
    parts,
    [
        {
            "step_id": "catalyst_preformation",
            "participant_ids": ["cu_otf2", "ss_ph_box", "dcm"],
            "conditions": [
                fld("temperature", "r.t.", ev(7)),
                fld("reaction_time", q(1, "h"), ev(7)),
                fld("atmosphere", "argon", ev(3)),
            ],
        },
        {
            "step_id": "cu_addition",
            "participant_ids": ["allenyl_ketoester", "dbad", "cu_otf2", "ss_ph_box", "dcm"],
            "conditions": [
                fld("temperature", q(0, "°C"), ev(7)),
                fld("reaction_time", q(3, "h"), ev(7)),
                fld("operation", "substrates added to the catalyst solution; progress monitored by TLC", ev(7)),
            ],
        },
        {
            "step_id": "pd_coupling_cyclization",
            "participant_ids": ["k2co3", "pdpph3", "2g", "dioxane", "rr4dg", "rs4dg"],
            "conditions": [
                fld("temperature", q(100, "°C"), ev(7)),
                fld("reaction_time", q(4, "h"), ev(7)),
                fld("operation", "K2CO3, Pd(PPh3)4, p-bromoiodobenzene, and 1,4-dioxane added sequentially; progress monitored by TLC", ev(7)),
                fld("workup", "solvent evaporated", ev(7)),
                fld("purification", "flash chromatography on silica gel; petroleum ether/ethyl acetate 5:1", ev(7)),
            ],
        },
    ],
    [
        fld("isolated_yield", q(29, "%"), ev(7), ["rr4dg"]),
        fld("product_ee", {"number": 99, "unit": "%", "qualifier": "gt", "raw_text": ">99% ee"}, ev(7), ["rr4dg"]),
        fld("isolated_yield", q(60, "%"), ev(7), ["rs4dg"]),
        fld("product_ee", q(97, "%"), ev(7), ["rs4dg"]),
        fld("yield_measurement_basis", "isolated after flash chromatography", ev(7), ["rr4dg", "rs4dg"]),
        fld("ee_measurement_basis", "chiral HPLC", ev(7), ["rr4dg", "rs4dg"]),
    ],
    notes=[
        "Page 3 identifies these authentic samples with previous study 16; section 4.4.1 supplies the exact preparation and is retained as a literature example rather than a new scope experiment.",
        "The page-7 heading and procedure identify the ligand as (S,S)-Ph-BOX; the abbreviated equation on page 3 prints (S)-Ph-BOX.",
    ],
    unresolved=[
        "The relationship between this reproduced authentic-sample preparation and previous study 16 should be checked by a human reviewer.",
        "Complex reactant/product structures and absolute/relative stereochemistry remain machine-unverified.",
        "No associated SI or crystallographic file was supplied.",
    ],
))


# Section 4.4.2 is the detailed version of the page-3 MeMgBr conversion.
evidence = ev(3) + ev(7)
parts = [
    participant("3dg", "reactant", "(S)-3dg", evidence, [
        amount("mass", q(69, "mg"), ev(7)),
        amount("amount", q(0.10, "mmol"), ev(7)),
    ]),
    participant("memgbr", "reagent", "MeMgBr", evidence, [
        amount("volume", q(38, "uL"), ev(7)),
        amount("amount", q(0.11, "mmol"), ev(7)),
        amount("concentration", q(3.0, "M"), ev(7)),
        amount("equivalents", q(1.1, "equiv"), ev(3)),
    ]),
    participant("ether", "solvent", "Et2O", evidence, [
        amount("reaction_volume", q(3, "mL"), ev(7)),
        amount("extraction_volume", q(20, "mL"), ev(7)),
    ], name="diethyl ether", smiles="CCOCC"),
    participant("hcl", "reagent", "HCl", ev(7), [
        amount("concentration", q(3, "M"), ev(7)),
    ]),
    participant("na2so4", "reagent", "sodium sulfate", ev(7)),
    participant("4dg", "product", "(3S,5S)-4dg", evidence, [
        amount("isolated_mass", q(20, "mg"), ev(7)),
    ], name="1,2-dibenzyloxycarbonyl-3-ethoxycarbonyl-3-acetyl-5-(1'-(4''-bromophenyl)ethenyl)pyrazolidine"),
]
records.append(record(
    "scheme2_memgbr_to_3s5s_4dg",
    "reported_experiment",
    evidence,
    parts,
    [
        {
            "step_id": "grignard_acyl_conversion",
            "participant_ids": ["3dg", "memgbr", "ether", "4dg"],
            "conditions": [
                fld("temperature", q(-78, "°C"), evidence),
                fld("reaction_time", q(3.5, "h"), evidence),
                fld("atmosphere", "argon", ev(7)),
                fld("operation", "MeMgBr added to the Et2O solution at -78 °C; progress monitored by TLC", ev(7)),
            ],
        },
        {
            "step_id": "quench_and_isolation",
            "participant_ids": ["hcl", "ether", "na2so4", "4dg"],
            "conditions": [
                fld("quench_temperature", q(-78, "°C"), ev(7)),
                fld("operation", "quenched with 3 M HCl, then warmed to r.t.", ev(7)),
                fld("workup", "extracted with 20 mL diethyl ether; organic layer washed sequentially with water and brine, dried over sodium sulfate, and filtered", ev(7)),
                fld("purification", "silica-gel chromatography; petroleum ether/ethyl acetate 5:1", ev(7)),
            ],
        },
    ],
    [
        fld("isolated_yield", q(30, "%"), evidence, ["4dg"]),
        fld("product_ee", q(88, "%"), evidence, ["4dg"]),
        fld("yield_measurement_basis", "isolated after silica-gel chromatography", ev(7), ["4dg"]),
        fld("ee_measurement_basis", "chiral HPLC", ev(7), ["4dg"]),
    ],
    notes=[
        "The page-3 prose assigns (3S,5S) by comparison with authentic (3R,5R)-4dg and concludes that 3dg formed with (R,R)-Bn-BOX has S configuration.",
    ],
    unresolved=[
        "The volume of 3 M HCl used for quenching is not reported.",
        "Complex reactant/product connectivity and absolute stereochemistry remain machine-unverified.",
        "No associated SI or crystallographic file was supplied.",
    ],
))


assert len(records) == 2
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
                    "region": "left column, section 4.4.1",
                    "finding": "Exact two-stage preparation and isolation of authentic (3R,5R)-4dg and (3R,5S)-4dg merged into the existing previous-study-16 literature-example record; both product yields and ee values were retained separately.",
                    "evidence_ids": ev(7),
                },
                {
                    "region": "lower-left column, section 4.4.2",
                    "finding": "Exact MeMgBr conversion of (S)-3dg to (3S,5S)-4dg merged into the existing Scheme 2 record, including quantities, quench, workup, chromatography, isolated mass/yield, and ee.",
                    "evidence_ids": ev(7),
                },
                {
                    "region": "right column, supplementary-data statement and references 1-14",
                    "finding": "Online supplementary data are mentioned but were not supplied or explicitly associated; references are citations rather than present-paper experiment rows.",
                    "evidence_ids": ev(7),
                },
            ],
            "record_ids": [r["record_id"] for r in records],
            "unresolved": [
                "No supplementary-data or crystallographic file is present or explicitly associated.",
                "The authentic-sample preparation is explicitly linked to previous study 16; its exact relationship to reproduction in this paper requires human review.",
                "Complex structures and stereochemical assignments remain unverified.",
            ],
        },
        {
            "page": 8,
            "state": "attempted",
            "regions": [
                {
                    "region": "top of page, continuation of references 14-19",
                    "finding": "Only bibliography continuation and journal furniture are present; no table, figure, reaction arrow, experimental procedure, condition, result, or present-paper reaction footnote was found.",
                    "evidence_ids": ev(8),
                }
            ],
            "record_ids": [],
            "unresolved": [
                "Cited publications were not supplied as associated source documents and were not mined for reaction details."
            ],
        },
    ],
}
COVERAGE.parent.mkdir(parents=True, exist_ok=True)
COVERAGE.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

tasks = json.loads(TASKS.read_text())
for task in tasks:
    if task.get("document_id") == DOC and task.get("evidence_id") in {
        f"{DOC}:page7:text", f"{DOC}:page8:text"
    }:
        task["state"] = "attempted"
        task["reason"] = "Original page image and extracted text inspected; page-specific findings recorded in pages_0007_0008 coverage ledger."
TASKS.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"records": len(records), "coverage_pages": [7, 8]}, ensure_ascii=False))
