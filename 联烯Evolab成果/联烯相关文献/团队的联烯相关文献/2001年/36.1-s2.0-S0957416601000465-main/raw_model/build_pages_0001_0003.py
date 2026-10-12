#!/usr/bin/env python3
"""Build evidence-linked records for source.pdf pages 1-3."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CURRENT = ROOT / "runs" / "current"
RAW = CURRENT / "raw_model"
DOC = "doc_16c2d049c77173c0"
P1T = f"{DOC}:page1:text"
P2T = f"{DOC}:page2:text"
P3T = f"{DOC}:page3:text"
P1I = f"{DOC}:page1:image"
P2I = f"{DOC}:page2:image"
P3I = f"{DOC}:page3:image"


def write(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def fact(value, evidence=()):
    return {
        "value": value,
        "evidence_ids": list(evidence) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def field(name, value, evidence=()):
    return {"name": name, "fact": fact(value, evidence)}


def amount(name, value, evidence):
    return field(name, value, evidence)


def participant(entity_id, role, label, evidence, amounts=()):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(None),
        "smiles": fact(None),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": list(amounts),
    }


def record(suffix, source_id, kind, evidence, participants=(), steps=(), outcomes=(), notes=(), unresolved=()):
    return {
        "record_id": f"{DOC}:{suffix}",
        "document_id": DOC,
        "source_reaction_id": source_id,
        "record_kind": kind,
        "status": "needs_review",
        "completeness": "partial",
        "evidence_ids": list(dict.fromkeys(evidence)),
        "participants": list(participants),
        "steps": list(steps),
        "outcomes": list(outcomes),
        "notes": [fact(value, ev) for value, ev in notes],
        "review": {
            "method": "model",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": list(unresolved),
        },
    }


records = []

# Page 1 equation (1) is explicitly attributed to the authors' earlier work (ref. 2a).
eq1_ev = [P1T, P1I]
eq1_parts = [
    participant("generic_allenoic_acid", "reactant", "generic 2,3-allenoic acid (R-substituted)", eq1_ev),
    participant("generic_organic_halide", "reactant", "R'X", eq1_ev),
    participant("generic_butenolide", "product", "generic polysubstituted butenolide", eq1_ev),
    participant("pd0_eq1", "catalyst", "Pd(0)", eq1_ev),
    participant("ag1_eq1", "catalyst", "Ag(I)", eq1_ev),
    participant("mecn_eq1", "solvent", "CH3CN", eq1_ev),
]
records.append(record(
    "eq1_prior_pd_ag_coupling_cyclisation",
    "Equation (1), cited prior method",
    "literature_example",
    eq1_ev,
    eq1_parts,
    [{"step_id": "coupling_cyclisation", "participant_ids": [p["entity_id"] for p in eq1_parts], "conditions": []}],
    notes=[("The text attributes this generic Pd(0)/Ag(I)-cocatalysed transformation to reference 2a; it is not a current-paper run.", eq1_ev)],
    unresolved=[
        "Generic R and R' groups do not define complete structures.",
        "The local presentation does not report scale, catalyst loadings, temperature, time, workup, purification, or yield.",
        "The cited external procedure was not imported.",
    ],
))


table1_rows = [
    # ligand, PhI equiv, base label, base equiv, additive, additive mol%, temp, time h, 3a yield, 3a ee, 3a' yield, 3a' ee, ligand mol%
    ("2c", 4, "K2CO3", 4, "Ag2CO3", 5, 85, 2, 56, 0, 0, None, 10),
    ("2c", 4, "K2CO3", 4, "Ag2CO3", 5, "rt", 11, 24, 37, 60, 7, 20),
    ("2c", 2, "K2CO3", 4, None, None, "rt", 11, 20, 35, 19, 1.7, 20),
    ("2c", 2, "K2CO3", 4, "TBAB", 100, "rt", 12, 47, 4, 0, None, 20),
    ("2c", 4, "KHCO3", 1, "Ag2CO3", 3.6, "rt", 10.5, 0, None, 0, None, 10),
    ("2c", 4, "KNa(C4H4O6) (sodium potassium tartrate)", 4, "Ag2CO3", 3.6, "rt", 10.5, 0, None, 0, None, 10),
    ("2c", 4, "Cs2CO3", 4, "Ag2CO3", 3.6, "rt", 16, 28, 5, 0, None, 10),
    ("2c", 2, "(i-Pr)2NEt", 1.2, None, None, "rt", 10, 51, 12, 18.1, 1, 20),
    ("2c", 6, "(i-Pr)2NEt", 1.2, None, None, -15, 48, 52, 52, 0, None, 20),
    ("2a", 3.5, "(i-Pr)2NEt", 1.2, None, None, -15, 96, 71, 0, 0, None, 20),
    ("2b", 6, "(i-Pr)2NEt", 1.2, None, None, -15, 55.5, 52, 13, 14, 0, 20),
    ("2d", 6, "(i-Pr)2NEt", 1.2, None, None, -20, 55, 42, 0, 0, None, 20),
    ("2e", 3.5, "(i-Pr)2NEt", 1.2, None, None, -15, 66, 37.5, 2.6, 0, None, 20),
]

for idx, row in enumerate(table1_rows, 1):
    ligand, phi_eq, base, base_eq, additive, additive_mol, temp, time_h, y3a, ee3a, y3ap, ee3ap, ligand_mol = row
    ev = [P2T, P2I]
    if idx in (1, 2, 9):
        ev = [P1T, P1I, P2T, P2I]
    if idx == 9:
        ev += [P3T, P3I]
    parts = [
        participant("substrate_1a", "reactant", "1a", [P2T, P2I]),
        participant("phi", "reactant", "PhI", [P2T, P2I], [amount("equivalents", {"number": phi_eq, "unit": "equiv"}, [P2T, P2I])]),
        participant("product_3a", "product", "3a", [P2T, P2I]),
        participant("product_3a_prime", "product", "3a'", [P2T, P2I]),
        participant("pd_catalyst", "catalyst", "Pd2(dba)3·CHCl3", [P2T, P2I], [amount("catalyst_loading", {"number": 5, "unit": "mol%"}, [P2T, P2I])]),
        participant("ligand", "catalyst", ligand, [P2T, P2I], [amount("ligand_loading", {"number": ligand_mol, "unit": "mol%"}, [P2T, P2I])]),
        participant("base", "reagent", base, [P2T, P2I], [amount("equivalents", {"number": base_eq, "unit": "equiv"}, [P2T, P2I])]),
        participant("mecn", "solvent", "CH3CN", [P2T, P2I]),
    ]
    if additive:
        parts.append(participant("additive", "reagent", additive, [P2T, P2I], [amount("loading", {"number": additive_mol, "unit": "mol%"}, [P2T, P2I])]))
    conditions = [
        field("temperature", temp if temp == "rt" else {"number": temp, "unit": "°C"}, [P2T, P2I]),
        field("time", {"number": time_h, "unit": "h"}, [P2T, P2I]),
        field("additive", additive if additive else "none", [P2T, P2I]),
    ]
    steps = [{"step_id": "coupling_cyclisation", "participant_ids": [p["entity_id"] for p in parts], "conditions": conditions}]
    notes = [("Table 1 footnote c states that the product yields are isolated yields.", [P2T, P2I])]
    if idx == 6:
        notes.append(("Table 1 footnote e identifies KNa(C4H4O6) as sodium potassium tartrate.", [P2T, P2I]))
    outcomes = [
        field("3a_isolated_yield", {"number": y3a, "unit": "%"}, [P2T, P2I]),
        field("3a_ee", {"number": ee3a, "unit": "%"} if ee3a is not None else None, [P2T, P2I]),
        field("3a_prime_isolated_yield", {"number": y3ap, "unit": "%"}, [P2T, P2I]),
        field("3a_prime_ee", {"number": ee3ap, "unit": "%"} if ee3ap is not None else None, [P2T, P2I]),
        field("ee_measurement_method", "HPLC, OD chiral column, n-hexane/2-propanol = 9:1", [P2T, P2I]),
    ]
    unresolved = [
        "The main text does not report reaction scale, solvent volume/concentration, atmosphere, workup, purification, or isolated masses.",
        "Participant structures are conveyed by drawings/labels and remain unverified; SMILES are intentionally null.",
        "No SI is supplied or explicitly associated.",
    ]
    if idx == 9:
        parts += [
            participant("dmf_analysis", "solvent", "DMF", [P3T, P3I]),
            participant("eti_analysis", "reagent", "EtI", [P3T, P3I]),
        ]
        steps.append({
            "step_id": "recovered_1a_analysis_derivatization",
            "participant_ids": ["substrate_1a", "base", "dmf_analysis", "eti_analysis"],
            "conditions": [field("operation", "evaporate solvent, then add DMF, (i-Pr)2NEt, and EtI to form the corresponding ethyl ester", [P3T, P3I])],
        })
        outcomes += [
            field("recovered_racemic_1a", {"number": 31, "unit": "%"}, [P1T, P1I]),
            field("recovered_1a_ee", None),
        ]
        notes += [
            ("The prose reports 3a as the sole product at this point and attributes the low yield to incomplete conversion rather than kinetic resolution.", [P1T, P1I]),
            ("Footnote 7 states that both recovery yield and ee of 1a were measured after conversion to the ethyl ester; the numerical recovered-1a ee is not printed.", [P3T, P3I]),
        ]
        unresolved.append("The numerical ee value of recovered 1a is not reported.")
    records.append(record(
        f"table1_entry_{idx:02d}",
        f"Table 1 entry {idx}",
        "optimization_entry",
        ev,
        parts,
        steps,
        outcomes,
        notes,
        unresolved,
    ))


table2_rows = [
    ("1a", "R1 = n-C7H15; R2 = H", "Phenyl", 6, 2, "3a", 52, 52),
    ("1a", "R1 = n-C7H15; R2 = H", "4-Methylphenyl", 4, 2, "3b", 51, 43),
    ("1a", "R1 = n-C7H15; R2 = H", "4-Methoxycarbonylphenyl", 2, 2, "3c", 52, 49),
    ("1a", "R1 = n-C7H15; R2 = H", "4-Methoxyphenyl", 2, 2.5, "3d", 53, 47),
    ("1b", "R1 = n-C4H9; R2 = H", "Phenyl", 6, 2.5, "3e", 47, 50),
    ("1b", "R1 = n-C4H9; R2 = H", "4-Methylphenyl", 4, 2.5, "3f", 44, 53),
    ("1b", "R1 = n-C4H9; R2 = H", "4-Methoxycarbonylphenyl", 2, 2.5, "3g", 53, 53),
    ("1b", "R1 = n-C4H9; R2 = H", "4-Methoxyphenyl", 2, 2.5, "3h", 51, 46),
    ("1c", "R1 = c-C6H11; R2 = H", "Phenyl", 6, 2.5, "3i", 36, 0),
    ("1d", "R1 = Ph; R2 = Me", "Phenyl", 1.2, 2.5, "3j'", 100, None),
]

for idx, row in enumerate(table2_rows, 1):
    substrate, substituents, aryl, aryl_eq, days, product, yield_pct, ee = row
    ev = [P2T, P2I]
    if idx in (9, 10):
        ev += [P3T, P3I]
    parts = [
        participant("substrate", "reactant", substrate, [P2T, P2I]),
        participant("aryl_iodide", "reactant", f"ArI: {aryl}", [P2T, P2I], [amount("equivalents", {"number": aryl_eq, "unit": "equiv"}, [P2T, P2I])]),
        participant("product", "product", product, [P2T, P2I]),
        participant("pd_catalyst", "catalyst", "Pd2(dba)3·CHCl3", [P2T, P2I], [amount("catalyst_loading", {"number": 2.5, "unit": "mol%"}, [P2T, P2I])]),
        participant("ligand_2c", "catalyst", "2c", [P2T, P2I], [amount("ligand_loading", {"number": 20, "unit": "mol%"}, [P2T, P2I])]),
        participant("dipea", "reagent", "(i-Pr)2NEt", [P2T, P2I]),
        participant("mecn", "solvent", "CH3CN", [P2T, P2I]),
    ]
    steps = [{
        "step_id": "coupling_cyclisation",
        "participant_ids": [p["entity_id"] for p in parts],
        "conditions": [
            field("temperature", {"number": -15, "unit": "°C"}, [P2T, P2I]),
            field("time", {"number": days, "unit": "days"}, [P2T, P2I]),
        ],
    }]
    outcomes = [
        field("isolated_yield", {"number": yield_pct, "unit": "%"}, [P2T, P2I]),
        field("ee", {"number": ee, "unit": "%"} if ee is not None else None, [P2T, P2I]),
        field("ee_measurement_method", "HPLC" if ee is not None else None, [P2T, P2I]),
    ]
    notes = [
        (f"The Table 2 scheme defines {substrate} as {substituents}.", [P2T, P2I]),
        ("Table 2 footnote a states that yields are isolated yields.", [P2T, P2I]),
    ]
    unresolved = [
        "The amount of (i-Pr)2NEt is not printed in the Table 2 scheme and was not inherited from Table 1 by assumption.",
        "Reaction scale, solvent volume/concentration, atmosphere, workup, purification, and isolated mass are not reported.",
        "Participant structures remain unverified and SMILES are null.",
        "No SI is supplied or explicitly associated.",
    ]
    if idx == 9:
        notes.append(("The prose attributes the loss of ee for the c-hex substrate to steric hindrance.", [P3T, P3I]))
    if idx == 10:
        notes.append(("The prose states that only the cycloisomerisation product 3j' was formed.", [P3T, P3I]))
        unresolved.append("No ee value is reported for 3j'.")
    records.append(record(
        f"table2_entry_{idx:02d}",
        f"Table 2 entry {idx}",
        "substrate_scope_entry",
        ev,
        parts,
        steps,
        outcomes,
        notes,
        unresolved,
    ))


timecourse_rows = [(8, 17, 47), (20, 30, 51), (30, 34, 52), (48, 57, 51), (192, 76, 29)]
for idx, (time_h, yield_pct, ee) in enumerate(timecourse_rows, 1):
    ev = [P3T, P3I]
    parts = [
        participant("substrate_1a", "reactant", "1a (n-Hep-substituted allenoic acid)", ev),
        participant("phi", "reactant", "PhI", ev),
        participant("product_3a", "product", "(+)-3a", ev),
        participant("pd_catalyst", "catalyst", "Pd2(dba)3·CHCl3", ev, [amount("catalyst_loading", {"number": 2.5, "unit": "mol%"}, ev)]),
        participant("ligand_2c", "catalyst", "2c", ev, [amount("ligand_loading", {"number": 20, "unit": "mol%"}, ev)]),
        participant("dipea", "reagent", "(i-Pr)2NEt", ev),
        participant("mecn", "solvent", "CH3CN", ev),
    ]
    records.append(record(
        f"scheme1_timecourse_{time_h:03d}h",
        f"Scheme 1, {time_h} h time point",
        "optimization_entry",
        ev,
        parts,
        [{
            "step_id": "coupling_cyclisation_timecourse",
            "participant_ids": [p["entity_id"] for p in parts],
            "conditions": [
                field("temperature", {"number": -15, "unit": "°C"}, ev),
                field("time", {"number": time_h, "unit": "h"}, ev),
            ],
        }],
        [
            field("yield", {"number": yield_pct, "unit": "%"}, ev),
            field("ee", {"number": ee, "unit": "%"}, ev),
            field("yield_measurement_basis", None),
            field("ee_measurement_method", None),
        ],
        [("Scheme 1 reports a distinct time-course outcome under the displayed 2.5 mol% Pd catalyst conditions.", ev)],
        [
            "The yield basis and ee measurement method are not printed in Scheme 1.",
            "PhI and (i-Pr)2NEt quantities, scale, concentration, atmosphere, workup, purification, and isolated mass are not reported.",
            "This time-course presentation differs from Table 1 entry 9 (5 mol% Pd by footnote) and Table 2 entry 1 (different 48 h outcome), so it remains a separate record.",
            "Structures are unverified and SMILES are null; no SI is supplied or associated.",
        ],
    ))


mech_ev = [P3T, P3I]
records.append(record(
    "proposed_carbopalladation_allylic_substitution_mechanism",
    "Conclusion, proposed mechanism",
    "mechanism",
    mech_ev,
    participants=[
        participant("generic_allene", "reactant", "2,3-allenoic acid", mech_ev),
        participant("proposed_pi_allyl_pd", "unspecified_agent", "proposed π-allyl-palladium intermediate", mech_ev),
        participant("generic_butenolide", "product", "β-aryl butenolide", mech_ev),
    ],
    notes=[
        ("The authors propose carbopalladation of the allene to a π-allyl-palladium intermediate, followed by enantioselective intramolecular allylic substitution.", mech_ev),
        ("The intermediate is proposed, not reported as isolated or directly observed.", mech_ev),
    ],
    unresolved=[
        "The paper supplies no kinetic or direct-observation evidence for the proposed intermediate in this passage.",
        "Generic structures are unverified and SMILES are null.",
    ],
))


raw_path = RAW / "records_pages_0001_0003.json"
write(raw_path, records)

table1_ids = [f"{DOC}:table1_entry_{i:02d}" for i in range(1, 14)]
table2_ids = [f"{DOC}:table2_entry_{i:02d}" for i in range(1, 11)]
timecourse_ids = [f"{DOC}:scheme1_timecourse_{h:03d}h" for h, _, _ in timecourse_rows]
coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1,
            "state": "attempted",
            "regions": [
                {
                    "region": "page 1 title, abstract, and introductory prose",
                    "finding": "Current-paper objective and qualitative abstract only; no row-level experiment beyond presentations linked below.",
                    "evidence_ids": [P1T, P1I],
                },
                {
                    "region": "page 1 Equation (1), lower-left column",
                    "finding": "Generic Pd(0)/Ag(I)-cocatalysed prior-literature coupling cyclisation attributed to reference 2a.",
                    "evidence_ids": [P1T, P1I],
                },
                {
                    "region": "page 1 lower-column prose describing Table 1 entries 1, 2, and 9",
                    "finding": "Current optimization outcomes, including entry 9's 31% recovered racemic 1a and incomplete-conversion interpretation; merged with Table 1 row records.",
                    "evidence_ids": [P1T, P1I],
                },
                {
                    "region": "page 1 Figure 1",
                    "finding": "Ligand drawings 2a-2e and R labels; identity context for optimization rows, not standalone experiments.",
                    "evidence_ids": [P1T, P1I],
                },
            ],
            "record_ids": [f"{DOC}:eq1_prior_pd_ag_coupling_cyclisation", f"{DOC}:table1_entry_01", f"{DOC}:table1_entry_02", f"{DOC}:table1_entry_09"],
            "unresolved": [
                "Figure 1 structures were not converted to verified SMILES.",
                "The main text supplies no full experimental procedure and no SI is supplied or associated.",
            ],
        },
        {
            "page": 2,
            "state": "attempted",
            "regions": [
                {
                    "region": "page 2 Table 1 including header scheme, 13 rows, and footnotes a-e",
                    "finding": "Thirteen distinct optimization experiments, including zero-yield and competing cycloisomerisation outcomes; footnote overrides applied row by row.",
                    "evidence_ids": [P2T, P2I],
                },
                {
                    "region": "page 2 Table 2 including header scheme, substrate definitions, 10 rows, and footnotes",
                    "finding": "Ten distinct substrate-scope experiments; entry 10 is the 100% cycloisomerisation product 3j' result rather than a coupling product.",
                    "evidence_ids": [P2T, P2I],
                },
                {
                    "region": "page 2 lower prose",
                    "finding": "Discussion of poor alternative ligands and aryl-iodide/substrate trends; supports the corresponding table rows without adding a new run.",
                    "evidence_ids": [P2T, P2I],
                },
            ],
            "record_ids": table1_ids + table2_ids,
            "unresolved": [
                "No reaction scale, concentration, atmosphere, workup, purification, or isolated masses are reported.",
                "Table 2 does not print the (i-Pr)2NEt amount; it remains missing.",
                "All drawn structures remain unverified and SMILES are null.",
            ],
        },
        {
            "page": 3,
            "state": "attempted",
            "regions": [
                {
                    "region": "page 3 Scheme 1, top",
                    "finding": "Five distinct reaction-time outcomes (8, 20, 30, 48, and 192 h) under displayed 2.5 mol% Pd conditions.",
                    "evidence_ids": [P3T, P3I],
                },
                {
                    "region": "page 3 left-column prose below Scheme 1",
                    "finding": "Table 2 entry 9 steric/ee discussion, entry 10 exclusive cycloisomerisation, and time-course interpretation; linked to existing row/time records.",
                    "evidence_ids": [P3T, P3I],
                },
                {
                    "region": "page 3 conclusion mechanism paragraph",
                    "finding": "Proposed carbopalladation/π-allyl-palladium/intramolecular allylic-substitution mechanism, classified as mechanism rather than experiment.",
                    "evidence_ids": [P3T, P3I],
                },
                {
                    "region": "page 3 footnote 7 and references",
                    "finding": "Footnote 7 gives analytical ethyl-ester conversion for recovered 1a and is merged into Table 1 entry 9; bibliography otherwise supplies context only.",
                    "evidence_ids": [P3T, P3I],
                },
            ],
            "record_ids": timecourse_ids + [f"{DOC}:table1_entry_09", f"{DOC}:table2_entry_09", f"{DOC}:table2_entry_10", f"{DOC}:proposed_carbopalladation_allylic_substitution_mechanism"],
            "unresolved": [
                "Scheme 1 does not state yield basis, ee method, PhI amount, or (i-Pr)2NEt amount.",
                "The numerical ee of recovered 1a is not printed in footnote 7.",
                "The proposed intermediate is not directly observed.",
                "No SI is supplied or explicitly associated.",
            ],
        },
    ],
}
write(CURRENT / "coverage" / "pages_0001_0003.json", coverage)

tasks_path = CURRENT / "tasks.json"
tasks = json.loads(tasks_path.read_text())
for task in tasks:
    page = int(task["evidence_id"].split(":page", 1)[1].split(":", 1)[0])
    if page in (1, 2, 3):
        task["state"] = "attempted"
        task["visual_evidence_id"] = f"{DOC}:page{page}:image"
        task["reason"] = "Original page image and text inspected; source-linked records/coverage generated. Attempted does not certify semantic completeness."
write(tasks_path, tasks)

print(json.dumps({"records": len(records), "raw": str(raw_path.relative_to(ROOT)), "coverage_pages": [1, 2, 3]}, ensure_ascii=False))
