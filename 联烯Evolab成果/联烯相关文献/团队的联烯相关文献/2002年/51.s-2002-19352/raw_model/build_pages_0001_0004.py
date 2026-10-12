#!/usr/bin/env python3
"""Build source-derived machine records for doc_3168c123539e0231, PDF pages 1-4."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "runs/current/raw_model/records_pages_0001_0004.json"
COVERAGE = ROOT / "runs/current/coverage/pages_0001_0004.json"
TASKS = ROOT / "runs/current/tasks.json"
DOC = "doc_3168c123539e0231"
P = {
    1: [f"{DOC}:page1:text", f"{DOC}:page1:image"],
    2: [f"{DOC}:page2:text", f"{DOC}:page2:image"],
    3: [f"{DOC}:page3:text", f"{DOC}:page3:image"],
    4: [f"{DOC}:page4:text", f"{DOC}:page4:image"],
}


def fact(value, evidence):
    return {
        "value": value,
        "evidence_ids": list(evidence) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def field(name, value, evidence, target=None):
    result = {"name": name, "fact": fact(value, evidence)}
    if target:
        result["target_entity_ids"] = list(target)
    return result


def amounts(evidence, mmol=None, equiv=None, molpct=None, volume=None):
    result = []
    if mmol is not None:
        result.append(field("amount", {"number": mmol, "unit": "mmol"}, evidence))
    if equiv is not None:
        result.append(field("equivalents", {"number": equiv, "unit": "equiv"}, evidence))
    if molpct is not None:
        result.append(field("catalyst_loading", {"number": molpct, "unit": "mol%"}, evidence))
    if volume is not None:
        result.append(field("volume", {"number": volume, "unit": "mL"}, evidence))
    return result


def participant(entity_id, role, evidence, label=None, name=None, smiles=None, participant_amounts=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence),
        "smiles": fact(smiles, evidence),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": participant_amounts or [],
    }


def missing_conditions(evidence, include_time=False):
    result = []
    if include_time:
        result.append(field("time", None, evidence))
    result.extend([
        field("atmosphere", None, evidence),
        field("concentration", None, evidence),
        field("workup", None, evidence),
        field("purification", None, evidence),
    ])
    return result


def experiment(record_id, source_id, kind, evidence, participants, conditions, outcomes, notes=None, unresolved=None):
    input_ids = [p["entity_id"] for p in participants if p["role"] != "product"]
    return {
        "record_id": f"{DOC}:{record_id}",
        "document_id": DOC,
        "source_reaction_id": source_id,
        "record_kind": kind,
        "status": "needs_review",
        "completeness": "partial",
        "evidence_ids": list(dict.fromkeys(evidence)),
        "participants": participants,
        "steps": [{"step_id": "reaction", "participant_ids": input_ids, "conditions": conditions}],
        "outcomes": outcomes,
        "notes": [fact(value, evidence) for value in (notes or [])],
        "review": {
            "method": "model",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved or [
                "Machine-extracted record requires independent source review.",
                "Candidate structures were visually interpreted but are not structure-verified.",
                "Atmosphere, concentration, workup, purification, and isolated mass are not reported in the supplied main text.",
                "No supporting information was supplied or explicitly associated.",
            ],
        },
    }


def catalyst_pp(evidence, amount_mmol=0.025, molpct=5):
    return participant(
        "catalyst", "catalyst", evidence, name="Pd(PPh3)4",
        participant_amounts=amounts(evidence, mmol=amount_mmol, molpct=molpct),
    )


def solvent(entity_id, name, smiles, evidence, volume=3):
    return participant(entity_id, "solvent", evidence, name=name, smiles=smiles,
                       participant_amounts=amounts(evidence, volume=volume))


def common_1a(evidence, ph_i_mmol):
    return [
        participant("substrate_1a", "reactant", evidence, label="1a",
                    name="2-methyl-3-n-butylpenta-3,4-dien-1-ol",
                    smiles="C=C=C(CCCC)C(C)CO", participant_amounts=amounts(evidence, mmol=0.5)),
        participant("iodobenzene", "reactant", evidence, name="iodobenzene", smiles="Ic1ccccc1",
                    participant_amounts=amounts(evidence, mmol=ph_i_mmol,
                                                equiv=ph_i_mmol / 0.5)),
    ]


BASES = {
    "K2CO3": ("potassium carbonate", "[K+].[K+].[O-]C([O-])=O"),
    "Na2CO3": ("sodium carbonate", "[Na+].[Na+].[O-]C([O-])=O"),
    "Cs2CO3": ("cesium carbonate", "[Cs+].[Cs+].[O-]C([O-])=O"),
    "KOH": ("potassium hydroxide", "[K+].[OH-]"),
}


SOLVENTS = {
    "toluene": ("toluene", "Cc1ccccc1"),
    "DMF": ("N,N-dimethylformamide", "CN(C)C=O"),
    "THF": ("tetrahydrofuran", "C1CCOC1"),
    "CH3CN": ("acetonitrile", "CC#N"),
}


def base_participant(base, evidence, mmol, equiv):
    name, smiles = BASES[base]
    return participant("base", "reagent", evidence, name=name, smiles=smiles,
                       participant_amounts=amounts(evidence, mmol=mmol, equiv=equiv))


records = []

# Table 1: nine optimization rows. Entry 3 also cites the duplicate equation/prose on page 2.
table1 = [
    (1, "K2CO3", "toluene", 80, 11.5, "trace", True, False),
    (2, "Na2CO3", "DMF", 80, 17, "trace", False, False),
    (3, "K2CO3", "DMF", 70, 10, 56, False, False),
    (4, "K2CO3", "DMF", 60, 11.5, 42, False, True),
    (5, "Cs2CO3", "DMF", 70, 4, 67, False, False),
    (6, "K2CO3", "DMF", 80, 19, 58, True, False),
    (7, "K2CO3", "THF", "reflux", 11.5, 54, True, False),
    (8, "K2CO3", "CH3CN", 80, 17, 26, False, False),
    (9, "K2CO3", "CH3CN", 80, 17, 54, True, False),
]
for entry, base, solv, temp, time, yld, has_tbab, alternate_catalyst in table1:
    evidence = P[1] + (P[2] if entry == 3 else [])
    parts = common_1a(evidence, 1.0)
    parts.append(base_participant(base, evidence, 2.0, 4.0))
    if alternate_catalyst:
        parts.extend([
            participant("pd2dba3_chcl3", "catalyst", evidence, name="Pd2(dba)3·CHCl3",
                        participant_amounts=amounts(evidence, molpct=2.5)),
            participant("pph3", "reagent", evidence, name="triphenylphosphine",
                        smiles="P(c1ccccc1)(c1ccccc1)c1ccccc1",
                        participant_amounts=amounts(evidence, molpct=10)),
        ])
    else:
        parts.append(catalyst_pp(evidence))
    solv_name, solv_smiles = SOLVENTS[solv]
    parts.append(solvent("solvent", solv_name, solv_smiles, evidence))
    if has_tbab:
        parts.append(participant(
            "tbab", "reagent", evidence, name="tetrabutylammonium bromide",
            smiles="CCCC[N+](CCCC)(CCCC)CCCC.[Br-]",
            participant_amounts=amounts(evidence, equiv=1.4),
        ))
    parts.append(participant("product_2a", "product", evidence, label="2a",
                             name="2a (2,3-dihydrofuran product)",
                             smiles="O1C(c2ccccc2)C(CCCC)=C(C)C1"))
    notes = []
    outcomes = [
        field("isolated_yield", yld if isinstance(yld, str) else {"number": yld, "unit": "%"}, evidence,
              ["product_2a"]),
        field("yield_measurement_basis", "isolated yield based on 1a", evidence, ["product_2a"]),
        field("isolated_mass", None, evidence, ["product_2a"]),
    ]
    if entry == 3:
        parts.extend([
            participant("unformed_3a", "product", evidence, label="3a", name="six-membered alternative product 3a"),
            participant("unformed_4a", "product", evidence, label="4a", name="four-membered alternative product 4a"),
        ])
        outcomes.extend([
            field("formation_result", "not formed", P[2], ["unformed_3a"]),
            field("formation_result", "not formed", P[2], ["unformed_4a"]),
            field("reported_selectivity", "exclusive formation of 2a", P[1] + P[2], ["product_2a"]),
        ])
        notes.append("The page-2 equation and prose describe the same 56% experiment as Table 1 entry 3 and were merged rather than duplicated.")
    temperature_value = temp if isinstance(temp, str) else {"number": temp, "unit": "°C"}
    conditions = [
        field("temperature", temperature_value, evidence),
        field("time", {"number": time, "unit": "h"}, evidence),
        field("solvent", solv, evidence),
    ] + missing_conditions(evidence)
    records.append(experiment(
        f"table1_entry_{entry:02d}", f"Table 1 entry {entry}", "optimization_entry", evidence,
        parts, conditions, outcomes, notes,
    ))


# Table 2: aryl iodide scope. Entry 6 substitutes K2CO3 for Cs2CO3.
aryl_rows = [
    (1, "p-FC6H4I", "1-fluoro-4-iodobenzene", "Fc1ccc(I)cc1", 4, "2b", 55, "c2ccc(F)cc2"),
    (2, "p-ClC6H4I", "1-chloro-4-iodobenzene", "Clc1ccc(I)cc1", 4, "2c", 68, "c2ccc(Cl)cc2"),
    (3, "p-BrC6H4I", "1-bromo-4-iodobenzene", "Brc1ccc(I)cc1", 4, "2d", 59, "c2ccc(Br)cc2"),
    (4, "p-MeC6H4I", "1-iodo-4-methylbenzene", "Cc1ccc(I)cc1", 4, "2e", 68, "c2ccc(C)cc2"),
    (5, "o-MeC6H4I", "1-iodo-2-methylbenzene", "Cc1ccccc1I", 6, "2f", 55, "c2ccccc2C"),
    (6, "p-MeO2CC6H4I", "methyl 4-iodobenzoate", "COC(=O)c1ccc(I)cc1", 10, "2g", 56, "c2ccc(C(=O)OC)cc2"),
    (7, "p-MeO2CC6H4I", "methyl 4-iodobenzoate", "COC(=O)c1ccc(I)cc1", 4, "2g", 60, "c2ccc(C(=O)OC)cc2"),
    (8, "p-MeOC6H4I", "1-iodo-4-methoxybenzene", "COc1ccc(I)cc1", 4, "2h", 63, "c2ccc(OC)cc2"),
    (9, "naphthyl iodide", "naphthyl iodide (isomer not specified)", None, 4, "2i", 58, None),
]
for entry, aryl_label, aryl_name, aryl_smiles, time, product_label, yld, aryl_fragment in aryl_rows:
    evidence = P[3]
    parts = [
        participant("substrate_1a", "reactant", evidence, label="1a",
                    name="2-methyl-3-n-butylpenta-3,4-dien-1-ol", smiles="C=C=C(CCCC)C(C)CO",
                    participant_amounts=amounts(evidence, mmol=0.5)),
        participant("aryl_iodide", "reactant", evidence, label=aryl_label, name=aryl_name,
                    smiles=aryl_smiles, participant_amounts=amounts(evidence, mmol=0.75, equiv=1.5)),
        base_participant("K2CO3" if entry == 6 else "Cs2CO3", evidence, 2.0, 4.0),
        catalyst_pp(evidence),
        solvent("solvent", "N,N-dimethylformamide", "CN(C)C=O", evidence),
    ]
    product_smiles = f"O1C({aryl_fragment})C(CCCC)=C(C)C1" if aryl_fragment else None
    parts.append(participant("product", "product", evidence, label=product_label,
                             name=f"{product_label} (2,3-dihydrofuran product)", smiles=product_smiles))
    conditions = [
        field("temperature", {"number": 70, "unit": "°C"}, evidence),
        field("time", {"number": time, "unit": "h"}, evidence),
        field("solvent", "DMF", evidence),
    ] + missing_conditions(evidence)
    outcomes = [
        field("isolated_yield", {"number": yld, "unit": "%"}, evidence, ["product"]),
        field("yield_measurement_basis", "isolated yield based on 1a", evidence, ["product"]),
        field("isolated_mass", None, evidence, ["product"]),
    ]
    unresolved = None
    if entry == 9:
        unresolved = [
            "Machine-extracted record requires independent source review.",
            "The naphthyl iodide positional isomer is not specified in the supplied table, so reactant and product SMILES are null.",
            "Atmosphere, concentration, workup, purification, and isolated mass are not reported in the supplied main text.",
            "No supporting information was supplied or explicitly associated.",
        ]
    records.append(experiment(
        f"table2_entry_{entry:02d}", f"Table 2 entry {entry}", "substrate_scope_entry", evidence,
        parts, conditions, outcomes, unresolved=unresolved,
    ))


# Table 3: seven rows. The table reports no reaction times.
scope_rows = [
    (1, "1b", "3-n-butylpenta-3,4-dien-1-ol", "C=C=C(CCCC)CCO", "Cs2CO3", "2j", 75,
     "O1C(c2ccccc2)C(CCCC)=CC1"),
    (2, "1b", "3-n-butylpenta-3,4-dien-1-ol", "C=C=C(CCCC)CCO", "KOH", "2j", 58,
     "O1C(c2ccccc2)C(CCCC)=CC1"),
    (3, "1c", "drawing-defined i-propyl/n-butyl substituted 3,4-allenol 1c", "CC(C)C=C=C(CCCC)CCO",
     "Cs2CO3", "2k", 40, "O1C(c2ccccc2)(C(C)C)C(CCCC)=CC1"),
    (4, "1d", "drawing-defined phenyl/methyl substituted 3,4-allenol 1d", "C=C=C(c1ccccc1)C(C)CO",
     "Cs2CO3", "2l", 61, "O1C(c2ccccc2)C(c2ccccc2)=C(C)C1"),
    (5, "1e", "drawing-defined tert-butyl/methyl substituted 3,4-allenol 1e", "C=C=C(C(C)(C)C)C(C)CO",
     "Cs2CO3", "2m", 46, "O1C(c2ccccc2)C(C(C)(C)C)=C(C)C1"),
    (6, "1f", "drawing-defined highly substituted 3,4-allenol 1f", "C=C=C(CCCC)C(C)C(O)(C)C",
     "Cs2CO3", "2n", 43, "O1C(c2ccccc2)C(CCCC)=C(C)C1(C)C"),
    (7, "1f", "drawing-defined highly substituted 3,4-allenol 1f", "C=C=C(CCCC)C(C)C(O)(C)C",
     "KOH", "2n", 50, "O1C(c2ccccc2)C(CCCC)=C(C)C1(C)C"),
]
for entry, substrate_label, substrate_name, substrate_smiles, base, product_label, yld, product_smiles in scope_rows:
    evidence = P[3]
    parts = [
        participant("substrate", "reactant", evidence, label=substrate_label, name=substrate_name,
                    smiles=substrate_smiles, participant_amounts=amounts(evidence, mmol=0.5)),
        participant("iodobenzene", "reactant", evidence, name="iodobenzene", smiles="Ic1ccccc1",
                    participant_amounts=amounts(evidence, mmol=0.75, equiv=1.5)),
        base_participant(base, evidence, 2.0, 4.0),
        catalyst_pp(evidence),
        solvent("solvent", "N,N-dimethylformamide", "CN(C)C=O", evidence),
        participant("product", "product", evidence, label=product_label,
                    name=f"{product_label} (drawing-defined 2,3-dihydrofuran product)", smiles=product_smiles),
    ]
    conditions = [
        field("temperature", {"number": 70, "unit": "°C"}, evidence),
        field("time", None, evidence),
        field("solvent", "DMF", evidence),
    ] + missing_conditions(evidence)
    outcomes = [
        field("isolated_yield", {"number": yld, "unit": "%"}, evidence, ["product"]),
        field("yield_measurement_basis", f"isolated yield based on {substrate_label}", evidence, ["product"]),
        field("isolated_mass", None, evidence, ["product"]),
    ]
    records.append(experiment(
        f"table3_entry_{entry:02d}", f"Table 3 entry {entry}", "substrate_scope_entry", evidence,
        parts, conditions, outcomes,
        unresolved=[
            "Machine-extracted record requires independent source review.",
            "Candidate structures were visually interpreted from the table drawings but are not structure-verified.",
            "Reaction time, atmosphere, concentration, workup, purification, and isolated mass are not reported in the supplied main text.",
            "No supporting information was supplied or explicitly associated.",
        ],
    ))


# Two distinct failed substrates stated in page-2 prose and depicted on page 3.
failed = [
    ("1g", "drawing-defined 3-unsubstituted 3,4-allenol 1g", "CCCCC=C=CCCO"),
    ("1h", "drawing-defined 3-unsubstituted 3,4-allenol 1h", "CC(=C=CC(C)CCO)C"),
]
for label, name, smiles in failed:
    evidence = P[2] + P[3]
    parts = [
        participant("substrate", "reactant", evidence, label=label, name=name, smiles=smiles),
        participant("expected_product", "product", evidence,
                    name=f"expected cyclization product from {label}"),
    ]
    conditions = [
        field("temperature", None, evidence),
        field("time", None, evidence),
        field("atmosphere", None, evidence),
        field("concentration", None, evidence),
        field("solvent", None, evidence),
        field("workup", None, evidence),
        field("purification", None, evidence),
    ]
    outcomes = [
        field("expected_product_formation", "not obtained", evidence, ["expected_product"]),
        field("yield", None, evidence, ["expected_product"]),
    ]
    records.append(experiment(
        f"failed_substrate_{label}", f"Failed substrate {label}", "substrate_scope_entry", evidence,
        parts, conditions, outcomes,
        notes=["The article states that a 3-position substituent is necessary and no expected cyclization product was obtained."],
        unresolved=[
            "Machine-extracted failure record requires independent source review.",
            "The prose does not state the exact tested reagent amounts, base, solvent, temperature, time, or analytical detection limit for this failed substrate; Table 3 conditions were not inferred onto it.",
            "Candidate substrate structure was visually interpreted from the drawing but is not structure-verified; the expected product is not depicted or labeled.",
            "No supporting information was supplied or explicitly associated.",
        ],
    ))


# The page-2 generic Scheme is mechanistic, not an experiment.
mechanism_evidence = P[1] + P[2]
records.append({
    "record_id": f"{DOC}:mechanism_generic_scheme",
    "document_id": DOC,
    "source_reaction_id": "Generic Scheme, pathways 1-3",
    "record_kind": "mechanism",
    "status": "needs_review",
    "completeness": "partial",
    "evidence_ids": mechanism_evidence,
    "participants": [
        participant("generic_allenol", "reactant", mechanism_evidence,
                    label="generic R1/R2/R3-substituted allenol"),
        participant("generic_aryl_palladium", "unspecified_agent", mechanism_evidence, label="ArPdI"),
        participant("generic_products", "product", mechanism_evidence,
                    label="generic cyclic oxygen products from pathways 1-3"),
    ],
    "steps": [],
    "outcomes": [],
    "notes": [
        fact("The generic Scheme compares carbopalladation and exo/endo oxypalladation pathways 1-3.", mechanism_evidence),
        fact("The authors assign the observed 2,3-dihydrofuran formation to oxidative addition, exo-mode oxypalladation, and reductive elimination.", P[1] + P[2]),
    ],
    "review": {
        "method": "model",
        "reviewer": None,
        "checked_fields": [],
        "unresolved": [
            "Generic R groups and organopalladium intermediates are not fully specified molecules; SMILES remain null.",
            "This is a proposed mechanism, not an independently reported experimental row.",
        ],
    },
})


OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")

table1_ids = [f"{DOC}:table1_entry_{i:02d}" for i in range(1, 10)]
table2_ids = [f"{DOC}:table2_entry_{i:02d}" for i in range(1, 10)]
table3_ids = [f"{DOC}:table3_entry_{i:02d}" for i in range(1, 8)]
failure_ids = [f"{DOC}:failed_substrate_1g", f"{DOC}:failed_substrate_1h"]
mechanism_id = f"{DOC}:mechanism_generic_scheme"
coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1,
            "state": "attempted",
            "regions": [
                {
                    "region": "right column, Table 1 including footnotes a-d",
                    "finding": "Nine independent optimization rows for 1a + iodobenzene; trace and isolated yields retained; footnote n-Bu4NBr and alternate Pd2(dba)3·CHCl3/PPh3 catalyst system structured.",
                    "evidence_ids": [P[1][1], P[1][0]],
                },
                {
                    "region": "right-column prose immediately above Table 1",
                    "finding": "The 56% formation of 2a is the same experiment as Table 1 entry 3; it was merged with that row rather than duplicated.",
                    "evidence_ids": [P[1][1], P[1][0]],
                },
                {
                    "region": "left-column introduction and cited prior methods",
                    "finding": "Background and cited literature only; no current-paper experimental row created.",
                    "evidence_ids": [P[1][1], P[1][0]],
                },
            ],
            "record_ids": table1_ids + [mechanism_id],
            "unresolved": [
                "The main text supplies no full experimental procedure or SI association.",
                "Candidate structures 1a/2a are machine-interpreted and remain unverified.",
            ],
        },
        {
            "page": 2,
            "state": "attempted",
            "regions": [
                {
                    "region": "upper half, generic Scheme with pathways 1-3",
                    "finding": "Generic proposed mechanism with R groups and organopalladium intermediates; classified as mechanism, not an experiment.",
                    "evidence_ids": [P[2][1], P[2][0]],
                },
                {
                    "region": "lower-left Equation and adjacent prose",
                    "finding": "The 1a→2a equation duplicates Table 1 entry 3; page-2 evidence was merged into that record. Alternatives 3a and 4a are explicitly reported as not formed.",
                    "evidence_ids": [P[2][1], P[2][0]],
                },
                {
                    "region": "lower-right scope discussion",
                    "finding": "Narrative context for Tables 2-3; separately preserves the explicit failures of 3-unsubstituted allenols 1g and 1h.",
                    "evidence_ids": [P[2][1], P[2][0]],
                },
            ],
            "record_ids": [table1_ids[2], mechanism_id] + failure_ids,
            "unresolved": [
                "The exact tested conditions and analytical detection limits for failed substrates 1g and 1h are absent from the prose.",
                "Generic mechanistic R groups cannot be expanded to definite structures.",
            ],
        },
        {
            "page": 3,
            "state": "attempted",
            "regions": [
                {
                    "region": "upper-left, Table 2 including reaction drawing and footnotes a-c",
                    "finding": "Nine independent aryl-iodide substrate-scope rows; shared quantities, times, isolated yields, and entry-6 K2CO3 override structured row by row.",
                    "evidence_ids": [P[3][1], P[3][0]],
                },
                {
                    "region": "upper/right, Table 3 including structures and footnotes a-c",
                    "finding": "Seven independent allenol substrate-scope rows; isolated yields and KOH overrides in entries 2 and 7 retained. Reaction time is not reported and remains missing.",
                    "evidence_ids": [P[3][1], P[3][0]],
                },
                {
                    "region": "below Table 3, structures 1g and 1h",
                    "finding": "Structures correspond to the two no-expected-product findings stated on page 2; two failure records link both pages.",
                    "evidence_ids": [P[3][1], P[3][0], P[2][1], P[2][0]],
                },
                {
                    "region": "lower-left and lower-right reference columns",
                    "finding": "Bibliography only; cited external work was not reconstructed as current-paper experiments.",
                    "evidence_ids": [P[3][1], P[3][0]],
                },
            ],
            "record_ids": table2_ids + table3_ids + failure_ids,
            "unresolved": [
                "Table 2 names only 'naphthyl iodide' for entry 9, so its positional isomer and product structures remain unspecified.",
                "All drawing-derived Table 3 structures remain unverified machine candidates.",
            ],
        },
        {
            "page": 4,
            "state": "attempted",
            "regions": [
                {
                    "region": "two-column page body, references 11-21",
                    "finding": "Bibliography continuation only; no reaction arrow, structure drawing, table, experimental condition, yield, selectivity, or failure result on this page.",
                    "evidence_ids": [P[4][1], P[4][0]],
                }
            ],
            "record_ids": [],
            "unresolved": [
                "Experimental details in the cited external papers are outside the supplied source and were not inferred.",
            ],
        },
    ],
}
COVERAGE.parent.mkdir(parents=True, exist_ok=True)
COVERAGE.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

tasks = json.loads(TASKS.read_text())
for task in tasks:
    if task.get("document_id") == DOC and task.get("task_id") in {P[i][0] for i in range(1, 5)}:
        task["state"] = "attempted"
        task["visual_evidence_id"] = f"{DOC}:page{task['task_id'].split('page')[1].split(':')[0]}:image"
        task["reason"] = "Original page image visually inspected; reaction regions mapped in coverage/pages_0001_0004.json."
TASKS.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"records": len(records), "coverage_pages": [p["page"] for p in coverage["pages"]]}, ensure_ascii=False))
