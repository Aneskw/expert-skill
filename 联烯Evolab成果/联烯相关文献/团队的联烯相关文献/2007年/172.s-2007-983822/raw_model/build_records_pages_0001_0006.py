#!/usr/bin/env python3
"""Build machine-derived reaction records for PDF pages 1--6."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "runs/current"
DOC = "doc_50d01341363d3c76"


def ev(page):
    return [f"{DOC}:page{page}:text", f"{DOC}:page{page}:image"]


def fact(value, evidence):
    return {
        "value": value,
        "evidence_ids": list(evidence) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def field(name, value, evidence, targets=None):
    result = {"name": name, "fact": fact(value, evidence)}
    if targets:
        result["target_entity_ids"] = targets
    return result


SMILES = {
    "2a": "C=C=CS(=O)(=O)c1ccccc1",
    "1a": "C=C=CS(=O)c1ccccc1",
    "3a": "OB(O)c1ccccc1",
    "3b": "OB(O)c1ccc(C)cc1",
    "AcOH": "CC(=O)O",
    "hydrogen peroxide": "OO",
    "DMSO": "CS(C)=O",
    "dioxane": "C1COCCO1",
    "DMF": "CN(C)C=O",
    "DMA": "CC(=O)N(C)C",
    "EtOH": "CCO",
    "acetone": "CC(C)=O",
    "MeCN": "CC#N",
    "Et2O": "CCOCC",
    "toluene": "Cc1ccccc1",
    "CH2Cl2": "ClCCl",
    "THF": "C1CCOC1",
}


def participant(entity_id, role, label, name, evidence, amounts=None, smiles=None):
    candidate = smiles if smiles is not None else SMILES.get(label)
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence),
        "smiles": fact(candidate, evidence) if candidate else fact(None, []),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": amounts or [],
    }


def quantity(name, number, unit, evidence, **extra):
    value = {"number": number, "unit": unit}
    value.update(extra)
    return field(name, value, evidence)


def base_record(rid, kind, evidence, participants, steps, outcomes, notes=None, unresolved=None):
    return {
        "record_id": f"{DOC}:{rid}",
        "document_id": DOC,
        "source_reaction_id": rid,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": list(dict.fromkeys(evidence)),
        "participants": participants,
        "steps": steps,
        "outcomes": outcomes,
        "notes": [fact(x, evidence) for x in (notes or [])],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved or [
                "Machine-derived record requires expert chemical review.",
                "Participant structures and product stereochemistry remain unverified.",
            ],
        },
    }


def missing_workup(evidence):
    return [field("workup", None, []), field("purification", None, [])]


records = []

# Page 2, Scheme 1: generic literature-based preparation sequence.
e2 = ev(2)
scheme1a_parts = [
    participant("s1a_phscl", "reagent", "PhSCl", "benzenesulfenyl chloride", e2),
    participant("s1a_alcohol", "reactant", "generic propargylic alcohol", "R-group propargylic alcohol", e2),
    participant("s1a_et3n", "reagent", "Et3N", "triethylamine", e2, smiles="CCN(CC)CC"),
    participant("s1a_ch2cl2", "solvent", "CH2Cl2", "dichloromethane", e2),
    participant("s1a_product", "product", "1", "generic 1,2-allenic sulfoxide", e2),
]
records.append(base_record(
    "scheme1_step1_generic_sulfoxide_preparation", "general_scheme", e2,
    scheme1a_parts,
    [{"step_id": "scheme1_step1", "participant_ids": [p["entity_id"] for p in scheme1a_parts],
      "conditions": [field("temperature", {"number": -78, "unit": "°C"}, e2), field("time", None, [])]}],
    [],
    notes=["Generic preparation scheme reported as a literature procedure; six compounds were synthesized by that procedure."],
    unresolved=["Generic R-group structures, quantities, duration, workup, purification, and yield are not supplied on page 2."],
))
scheme1b_parts = [
    participant("s1b_sulfoxide", "reactant", "1", "generic 1,2-allenic sulfoxide", e2),
    participant("s1b_h2o2", "reagent", "hydrogen peroxide", "hydrogen peroxide", e2),
    participant("s1b_acoh", "solvent", "AcOH", "acetic acid", e2),
    participant("s1b_product", "product", "2", "generic 1,2-allenic sulfone", e2),
]
records.append(base_record(
    "scheme1_step2_generic_sulfone_preparation", "general_scheme", e2,
    scheme1b_parts,
    [{"step_id": "scheme1_step2", "participant_ids": [p["entity_id"] for p in scheme1b_parts],
      "conditions": [field("temperature", {"number": 100, "unit": "°C"}, e2), field("time", None, [])]}],
    [],
    notes=["Generic oxidation scheme reported as part of a literature procedure."],
    unresolved=["Generic R-group structures, reagent quantities, duration, workup, purification, and yield are not supplied on page 2."],
))

# Page 2, Scheme 2: two substrate-specific failed experiments.
for substrate, substituent in [("1b", "R = Me"), ("1c", "R = n-Bu")]:
    parts = [
        participant(f"{substrate}_reactant", "reactant", substrate, f"1,2-allenic sulfoxide {substrate} ({substituent})", e2),
        participant(f"{substrate}_3a", "reactant", "3a", "phenylboronic acid", e2,
                    [quantity("equivalents", 2.0, "equiv", e2)]),
        participant(f"{substrate}_pd", "catalyst", "Pd(PPh3)4", "tetrakis(triphenylphosphine)palladium(0)", e2,
                    [quantity("catalyst_loading", 10, "mol%", e2)]),
        participant(f"{substrate}_acoh", "reagent", "AcOH", "acetic acid", e2,
                    [quantity("loading", 100, "mol%", e2)]),
        participant(f"{substrate}_thf", "solvent", "THF", "tetrahydrofuran", e2,
                    [field("volume", None, [])]),
        participant(f"{substrate}_expected", "product", "expected products", "expected hydroarylation products", e2),
    ]
    records.append(base_record(
        f"scheme2_{substrate}_no_expected_products", "reported_experiment", e2, parts,
        [{"step_id": "reaction", "participant_ids": [p["entity_id"] for p in parts],
          "conditions": [field("temperature", "r.t.", e2), field("time", None, []),
                         field("atmosphere", None, [])] + missing_workup(e2)}],
        [field("expected_product_formation", "no expected products", e2, [f"{substrate}_expected"])],
        unresolved=["Time, atmosphere, solvent volume, workup, purification, and product identities are not reported on page 2."],
    ))


def standard_2a_3a_parts(prefix, evidence, solvent_label, catalyst_label="Pd(PPh3)4",
                         catalyst_loading=10, acetic_loading=100, solvent_volume=3,
                         pph3_loading=None):
    parts = [
        participant(f"{prefix}_2a", "reactant", "2a", "phenyl propa-1,2-dienyl sulfone", evidence,
                    [quantity("amount", 0.25, "mmol", evidence)]),
        participant(f"{prefix}_3a", "reactant", "3a", "phenylboronic acid", evidence,
                    [quantity("equivalents", 2.0, "equiv", evidence)]),
        participant(f"{prefix}_pd", "catalyst", catalyst_label, catalyst_label, evidence,
                    [quantity("catalyst_loading", catalyst_loading, "mol%", evidence)]),
        participant(f"{prefix}_acoh", "reagent", "AcOH", "acetic acid", evidence,
                    [quantity("loading", acetic_loading, "mol%", evidence)]),
        participant(f"{prefix}_solvent", "solvent", solvent_label, solvent_label, evidence,
                    [quantity("volume", solvent_volume, "mL", evidence)] if solvent_volume is not None else [field("volume", None, [])]),
    ]
    if pph3_loading is not None:
        parts.append(participant(f"{prefix}_pph3", "reagent", "PPh3", "triphenylphosphine", evidence,
                                 [quantity("loading", pph3_loading, "mol%", evidence)],
                                 smiles="P(c1ccccc1)(c1ccccc1)c1ccccc1"))
    parts.extend([
        participant(f"{prefix}_e4aa", "product", "(E)-4aa", "phenyl (E)-2-phenylprop-1-en-1-yl sulfone", evidence),
        participant(f"{prefix}_z4aa", "product", "(Z)-4aa", "phenyl (Z)-2-phenylprop-1-en-1-yl sulfone", evidence),
        participant(f"{prefix}_5aa", "product", "5aa", "reported regioisomer 5aa", evidence),
    ])
    return parts


def selectivity_outcomes(prefix, evidence, regio, yield_value, stereo, recovery=None,
                         result=None, yield_targets=None):
    outcomes = [
        field("regioisomer_ratio_4aa_to_5aa", regio, evidence, [f"{prefix}_e4aa", f"{prefix}_5aa"]),
        field("isolated_yield_E_4aa", yield_value, evidence, yield_targets or [f"{prefix}_e4aa"]),
        field("stereoisomer_ratio_E_4aa_to_Z_4aa", stereo, evidence, [f"{prefix}_e4aa", f"{prefix}_z4aa"]),
        field("yield_measurement_basis", "isolated yield", evidence),
        field("selectivity_measurement_basis", "1H NMR (300 MHz) of crude after filtration and evaporation", evidence),
    ]
    if recovery is not None:
        outcomes.append(field("recovered_starting_material_yield", {"number": recovery, "unit": "%"}, evidence, [f"{prefix}_2a"]))
    if result is not None:
        outcomes.append(field("reaction_result", result, evidence))
    return outcomes


# Page 3, Table 1. Entry 11 is the repeated optimized experiment.
e3 = ev(3)
table1 = [
    (1, "DMSO", 24, "table dash (–)", "table dash (–)", "table dash (–)", 32),
    (2, "dioxane", 16, "table dash (–)", "table dash (–)", "table dash (–)", 56),
    (3, "DMF", 9, "table dash (–)", "trace", "table dash (–)", None),
    (4, "DMA", 9, "table dash (–)", "trace", "table dash (–)", None),
    (5, "EtOH", 40, "table dash (–)", "trace", "table dash (–)", None),
    (6, "acetone", 65, "81:19", {"number": 70, "unit": "%"}, ">99:1", None),
    (7, "MeCN", 40, "82:18", {"number": 23, "unit": "%"}, ">99:1", None),
    (8, "Et2O", 40, "83:17", {"number": 67, "unit": "%"}, ">99:1", None),
    (9, "toluene", 55, "87:13", {"number": 48, "unit": "%"}, ">99:1", None),
    (10, "CH2Cl2", 40, "90:10", {"number": 48, "unit": "%"}, ">99:1", None),
]
for entry, solvent, hours, regio, yld, stereo, recovery in table1:
    rid = f"table1_entry{entry}_solvent_screen"
    parts = standard_2a_3a_parts(rid, e3, solvent)
    records.append(base_record(
        rid, "optimization_entry", e3, parts,
        [{"step_id": "reaction", "participant_ids": [p["entity_id"] for p in parts],
          "conditions": [field("temperature", "r.t.", e3), field("time", {"number": hours, "unit": "h"}, e3),
                         field("atmosphere", "N2", e3)] + missing_workup(e3)}],
        selectivity_outcomes(rid, e3, regio, yld, stereo, recovery),
        notes=["A printed table dash is retained as an undefined source marker and is not converted to zero."] if entry <= 5 else [],
        unresolved=["Workup and purification are not reported for this optimization row.",
                    "Product structures and stereochemical SMILES remain unverified."],
    ))

# Shared optimized experiment: Table 1 entry 11 = Table 3 entry 3 = Table 4 entry 1.
e345 = e3 + ev(4) + ev(5)
rid = "optimized_2a_3a_conditions_A"
parts = standard_2a_3a_parts(rid, e345, "THF")
records.append(base_record(
    rid, "optimization_entry", e345, parts,
    [{"step_id": "reaction", "participant_ids": [p["entity_id"] for p in parts],
      "conditions": [field("temperature", "r.t.", e345), field("time", {"number": 22, "unit": "h"}, e345),
                     field("atmosphere", "N2", e345)] + missing_workup(e345)}],
    selectivity_outcomes(rid, e345, "91:9", {"number": 68, "unit": "%"}, ">99:1"),
    notes=["The same condition/result is printed as Table 1 entry 11, Table 3 entry 3, and Table 4 entry 1; evidence is merged rather than duplicated."],
    unresolved=["Workup and purification are not reported in PDF pages 1–6.",
                "Product structures and stereochemical SMILES remain unverified."],
))

# Page 3, Scheme 3 oxidation.
parts = [
    participant("scheme3_6ab", "reactant", "(E)-6ab", "phenyl (E)-2-(4-tolyl)prop-1-en-1-yl sulfoxide", e3),
    participant("scheme3_h2o2", "reagent", "hydrogen peroxide", "hydrogen peroxide", e3),
    participant("scheme3_acoh", "solvent", "AcOH", "acetic acid", e3),
    participant("scheme3_4ab", "product", "(E)-4ab", "phenyl (E)-2-(4-tolyl)prop-1-en-1-yl sulfone", e3),
]
records.append(base_record(
    "scheme3_oxidation_6ab_to_4ab", "reported_experiment", e3, parts,
    [{"step_id": "oxidation", "participant_ids": [p["entity_id"] for p in parts],
      "conditions": [field("temperature", {"number": 40, "unit": "°C"}, e3),
                     field("time", {"number": 24, "unit": "h"}, e3), field("atmosphere", None, [])]
                    + missing_workup(e3)}],
    [field("reported_yield_4ab", {"number": 52, "unit": "%"}, e3, ["scheme3_4ab"]),
     field("yield_measurement_basis", None, [])],
    unresolved=["Reagent amounts, atmosphere, workup, purification, and yield basis are absent from page 3.",
                "The detailed procedure occurs outside the requested page range and was not imported as covered evidence."],
))

# Page 4, Table 2 catalyst screen.
e4 = ev(4)
table2 = [
    (1, "Pd(PhCN)2Cl2", 65, None, None, None, 57, None),
    (2, "Pd(OAc)2", 61, None, None, None, 67, None),
    (3, "PdCl2", 65, None, None, None, 79, None),
    (4, "PdCl2", 65, None, None, None, 44, 20),
    (5, "Pd(PhCN)2Cl2", 61, None, None, None, 84, 20),
    (6, "Pd(dba)2", 41, None, None, None, None, None),
    (7, "Pd(dba)2", 9, "90:10", 61, ">99:1", None, 20),
    (8, "Pd(OAc)2", 12, "90:10", 78, ">99:1", None, 20),
]
for entry, catalyst, hours, regio, yld, stereo, recovery, pph3 in table2:
    rid = f"table2_entry{entry}_catalyst_screen"
    parts = standard_2a_3a_parts(rid, e4, "THF", catalyst, pph3_loading=pph3)
    yval = {"number": yld, "unit": "%"} if yld is not None else "table dash (–)"
    outcomes = selectivity_outcomes(
        rid, e4, regio or "table dash (–)", yval, stereo or "table dash (–)", recovery,
        result="complex mixture" if entry == 6 else None,
    )
    records.append(base_record(
        rid, "optimization_entry", e4, parts,
        [{"step_id": "reaction", "participant_ids": [p["entity_id"] for p in parts],
          "conditions": [field("temperature", "r.t.", e4), field("time", {"number": hours, "unit": "h"}, e4),
                         field("atmosphere", "N2", e4)] + missing_workup(e4)}],
        outcomes,
        notes=["A printed table dash is retained as an undefined source marker and is not converted to zero."] if entry <= 6 else [],
        unresolved=["Workup and purification are not reported for this catalyst-screen row.",
                    "Product structures and stereochemical SMILES remain unverified."],
    ))

# Page 4, Table 3 AcOH loading screen; entry 3 is already merged above.
for entry, loading, hours, temp, regio, yld in [
    (1, 20, 24, "r.t.", "86:14", 65),
    (2, 50, 24, "r.t.", "87:13", 68),
    (4, 200, 24, "r.t.", "90:10", 57),
    (5, 100, 7, "reflux", "90:10", 54),
]:
    rid = f"table3_entry{entry}_acoh_screen"
    parts = standard_2a_3a_parts(rid, e4, "THF", acetic_loading=loading)
    records.append(base_record(
        rid, "optimization_entry", e4, parts,
        [{"step_id": "reaction", "participant_ids": [p["entity_id"] for p in parts],
          "conditions": [field("temperature", temp, e4), field("time", {"number": hours, "unit": "h"}, e4),
                         field("atmosphere", "N2", e4)] + missing_workup(e4)}],
        selectivity_outcomes(rid, e4, regio, {"number": yld, "unit": "%"}, ">99:1"),
        unresolved=["Workup and purification are not reported for this loading-screen row.",
                    "Reflux is qualitative because no numerical temperature is printed." if temp == "reflux" else "Product structures remain unverified."],
    ))


def conditions_a_parts(prefix, evidence, allene_label, allene_name, boronic_label, boronic_name,
                       main_label, main_name, minor_label, minor_name, z_label, z_name):
    return [
        participant(f"{prefix}_allene", "reactant", allene_label, allene_name, evidence,
                    [quantity("amount", 0.25, "mmol", evidence)]),
        participant(f"{prefix}_boronic", "reactant", boronic_label, boronic_name, evidence,
                    [quantity("equivalents", 2.0, "equiv", evidence)]),
        participant(f"{prefix}_pd", "catalyst", "Pd(PPh3)4", "tetrakis(triphenylphosphine)palladium(0)", evidence,
                    [quantity("catalyst_loading", 10, "mol%", evidence)]),
        participant(f"{prefix}_acoh", "reagent", "AcOH", "acetic acid", evidence,
                    [quantity("loading", 100, "mol%", evidence)]),
        participant(f"{prefix}_thf", "solvent", "THF", "tetrahydrofuran", evidence, [field("volume", None, [])]),
        participant(f"{prefix}_main", "product", main_label, main_name, evidence),
        participant(f"{prefix}_z", "product", z_label, z_name, evidence),
        participant(f"{prefix}_minor", "product", minor_label, minor_name, evidence),
    ]


def scope_outcomes(prefix, evidence, family, ratio, yld, stereo):
    return [
        field(f"regioisomer_ratio_{family}", ratio, evidence, [f"{prefix}_main", f"{prefix}_minor"]),
        field(f"isolated_yield_{family}", {"number": yld, "unit": "%"}, evidence, [f"{prefix}_main"]),
        field(f"stereoisomer_ratio_{family}", stereo, evidence, [f"{prefix}_main", f"{prefix}_z"]),
        field("yield_measurement_basis", "isolated yield", evidence),
        field("selectivity_measurement_basis", "1H NMR (300 MHz) of crude after filtration and evaporation", evidence),
    ]


# Page 5, Table 4 scope, excluding duplicated entry 1.
e5 = ev(5)
table4 = [
    (2, "2a", "phenyl propa-1,2-dienyl sulfone", "3b", "4-tolylboronic acid", 22, "4ab", ">99:1", 62),
    (3, "2a", "phenyl propa-1,2-dienyl sulfone", "3c", "3-methoxyphenylboronic acid", 59, "4ac", ">97:3", 35),
    (4, "2a", "phenyl propa-1,2-dienyl sulfone", "3d", "4-methoxyphenylboronic acid", 17.5, "4ad", "93:7", 78),
    (5, "2a", "phenyl propa-1,2-dienyl sulfone", "3e", "3-nitrophenylboronic acid", 19, "4ae", "94:6", 66),
    (6, "2a", "phenyl propa-1,2-dienyl sulfone", "3f", "3-acetylphenylboronic acid", 22, "4af", ">99:1", 80),
    (7, "2a", "phenyl propa-1,2-dienyl sulfone", "3g", "4-acetylphenylboronic acid", 22, "4ag", "94:6", 80),
    (8, "2a", "phenyl propa-1,2-dienyl sulfone", "3h", "1-naphthylboronic acid", 21.5, "4ah", "91:9", 73),
    (9, "2a", "phenyl propa-1,2-dienyl sulfone", "3i", "(E)-hex-1-enylboronic acid", 25, "4ai", "90:10", 72),
    (10, "2a", "phenyl propa-1,2-dienyl sulfone", "3j", "(E)-styrylboronic acid", 11, "4aj", "94:6", 52),
    (11, "2b", "methyl-substituted 1,2-allenic phenyl sulfone (R1 = Me)", "3a", "phenylboronic acid", 72, "4ba", ">99:1", 50),
    (12, "2c", "n-butyl-substituted 1,2-allenic phenyl sulfone (R1 = n-Bu)", "3a", "phenylboronic acid", 96, "4ca", ">99:1", 55),
]
for entry, allene, allene_name, boronic, boronic_name, hours, product, ratio, yld in table4:
    rid = f"table4_entry{entry}_{product}"
    parts = conditions_a_parts(rid, e5, allene, allene_name, boronic, boronic_name,
                               f"(E)-{product}", f"reported (E)-alkenyl sulfone {product}",
                               product.replace("4", "5", 1), f"reported regioisomer of {product}",
                               f"(Z)-{product}", f"reported (Z)-alkenyl sulfone {product}")
    records.append(base_record(
        rid, "substrate_scope_entry", e5, parts,
        [{"step_id": "reaction", "participant_ids": [p["entity_id"] for p in parts],
          "conditions": [field("temperature", "r.t.", e5), field("time", {"number": hours, "unit": "h"}, e5),
                         field("atmosphere", "N2", e5)] + missing_workup(e5)}],
        scope_outcomes(rid, e5, f"{product}_to_regioisomer", ratio, yld, ">99:1"),
        unresolved=["THF volume, workup, and purification are not reported on page 5.",
                    "Complex product/regioisomer structures and stereochemical SMILES remain unverified."],
    ))

# Page 6, Table 5 sulfoxide scope.
e6 = ev(6)
table5 = [
    (1, "3a", "phenylboronic acid", 72, "6aa", "94:6", 50),
    (2, "3b", "4-tolylboronic acid", 36, "6ab", ">97:3", 58),
    (3, "3c", "3-methoxyphenylboronic acid", 12, "6ac", "99:1", 59),
    (4, "3d", "4-methoxyphenylboronic acid", 24.5, "6ad", "95:5", 52),
    (5, "3e", "3-nitrophenylboronic acid", 48, "6ae", ">96:4", 49),
    (6, "3g", "4-acetylphenylboronic acid", 48, "6ag", ">99:1", 48),
    (7, "3h", "1-naphthylboronic acid", 24, "6ah", ">94:6", 41),
    (8, "3k", "(E)-pent-1-enylboronic acid", 72, "6ak", ">92:8", 53),
    (9, "3j", "(E)-styrylboronic acid", 50, "6aj", ">94:6", 46),
]
for entry, boronic, boronic_name, hours, product, ratio, yld in table5:
    rid = f"table5_entry{entry}_{product}"
    minor = product.replace("6", "7", 1)
    parts = conditions_a_parts(rid, e6, "1a", "phenyl propa-1,2-dienyl sulfoxide", boronic, boronic_name,
                               f"(E)-{product}", f"reported (E)-alkenyl sulfoxide {product}",
                               minor, f"reported regioisomer {minor}",
                               f"(Z)-{product}", f"reported (Z)-alkenyl sulfoxide {product}")
    records.append(base_record(
        rid, "substrate_scope_entry", e6, parts,
        [{"step_id": "reaction", "participant_ids": [p["entity_id"] for p in parts],
          "conditions": [field("temperature", "r.t.", e6), field("time", {"number": hours, "unit": "h"}, e6),
                         field("atmosphere", "N2", e6)] + missing_workup(e6)}],
        scope_outcomes(rid, e6, f"{product}_to_{minor}", ratio, yld, ">99:1"),
        unresolved=["THF volume, workup, and purification are not reported on page 6.",
                    "Complex product/regioisomer structures and stereochemical SMILES remain unverified."],
    ))

# Page 6, Table 6 alkyl-allene optimization.
table6 = [
    (1, 100, "r.t.", 60, 38, "91:9", ">99:1", "THF", None),
    (2, 100, "reflux", 8, 75, "90:10", ">99:1", "THF", None),
    (3, 100, {"number": 50, "unit": "°C"}, 18, 64, "90:10", ">99:1", "dioxane", None),
    (4, 100, "reflux", 9, 75, "92:8", ">99:1", "dioxane", None),
    (5, 100, {"number": 130, "unit": "°C"}, 5, 68, "90:10", ">99:1", "dioxane", "Schlenk tube with a screw cap"),
    (6, 20, "reflux", 9, 42, "90:10", ">99:1", "dioxane", None),
    (7, 50, "reflux", 9, 45, "92:8", ">99:1", "dioxane", None),
    (8, 200, "reflux", 9, 44, "91:9", ">99:1", "dioxane", None),
]
for entry, acetic, temp, hours, yld, regio, stereo, solvent, vessel in table6:
    rid = f"table6_entry{entry}_alkyl_allene_screen"
    parts = [
        participant(f"{rid}_8a", "reactant", "8a", "n-octyl-substituted allene 8a", e6,
                    [quantity("amount", 0.25, "mmol", e6)]),
        participant(f"{rid}_3a", "reactant", "3a", "phenylboronic acid", e6,
                    [quantity("equivalents", 2.0, "equiv", e6)]),
        participant(f"{rid}_pd", "catalyst", "Pd(PPh3)4", "tetrakis(triphenylphosphine)palladium(0)", e6,
                    [quantity("catalyst_loading", 10, "mol%", e6)]),
        participant(f"{rid}_acoh", "reagent", "AcOH", "acetic acid", e6,
                    [quantity("loading", acetic, "mol%", e6)]),
        participant(f"{rid}_solvent", "solvent", solvent, solvent, e6,
                    [quantity("volume", 3, "mL", e6)]),
        participant(f"{rid}_e9aa", "product", "(E)-9aa", "(E)-2-phenylundec-2-ene", e6),
        participant(f"{rid}_z9aa", "product", "(Z)-9aa", "(Z)-2-phenylundec-2-ene", e6),
        participant(f"{rid}_10aa", "product", "10aa", "reported regioisomer 10aa", e6),
    ]
    conditions = [field("temperature", temp, e6), field("time", {"number": hours, "unit": "h"}, e6),
                  field("atmosphere", "N2", e6)]
    if vessel:
        conditions.append(field("reaction_vessel", vessel, e6))
    conditions += missing_workup(e6)
    records.append(base_record(
        rid, "optimization_entry", e6, parts,
        [{"step_id": "reaction", "participant_ids": [p["entity_id"] for p in parts], "conditions": conditions}],
        [field("combined_isolated_yield_9aa_and_10aa", {"number": yld, "unit": "%"}, e6,
               [f"{rid}_e9aa", f"{rid}_z9aa", f"{rid}_10aa"]),
         field("regioisomer_ratio_9aa_to_10aa", regio, e6, [f"{rid}_e9aa", f"{rid}_z9aa", f"{rid}_10aa"]),
         field("stereoisomer_ratio_E_9aa_to_Z_9aa", stereo, e6, [f"{rid}_e9aa", f"{rid}_z9aa"]),
         field("yield_measurement_basis", "isolated yield; isomers could not be separated by flash chromatography", e6),
         field("selectivity_measurement_basis", "1H NMR (300 MHz) of crude after evaporation", e6)],
        unresolved=["Workup and purification are not reported for this optimization row.",
                    "Reflux is qualitative where no numerical temperature is printed.",
                    "Product structures and stereochemical SMILES remain unverified."],
    ))


coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1,
            "state": "attempted",
            "regions": [{
                "region": "title, abstract, introduction, and opening Results and Discussion across the original page",
                "finding": "No row-level present-paper experiment, table, or reaction arrow; abstract and prose provide only high-level claims and cited background.",
                "evidence_ids": ev(1),
            }],
            "record_ids": [],
            "unresolved": ["Abstract-level reaction claims were not converted into duplicate experiments; later tables provide row-level evidence."],
        },
        {
            "page": 2,
            "state": "attempted",
            "regions": [
                {"region": "upper Scheme 1", "finding": "Two generic literature-procedure preparation arrows classified as general schemes, with generic R groups and missing row-specific yields.", "evidence_ids": ev(2)},
                {"region": "middle-right Scheme 2", "finding": "Two substrate-specific failed reactions (1b and 1c) extracted independently; no expected products formed.", "evidence_ids": ev(2)},
                {"region": "main prose and biographical sketches", "finding": "Narrative cross-references to later tables and author biographies; no additional independent reaction row.", "evidence_ids": ev(2)},
            ],
            "record_ids": [r["record_id"] for r in records if r["source_reaction_id"].startswith("scheme1_") or r["source_reaction_id"].startswith("scheme2_")],
            "unresolved": ["Scheme 1 gives generic structures and cites a literature procedure; quantities, durations, yields, and compound-specific mapping are incomplete.", "Scheme 2 omits time, atmosphere, solvent volume, workup, purification, and expected-product structures."],
        },
        {
            "page": 3,
            "state": "attempted",
            "regions": [
                {"region": "upper Table 1 and footnotes", "finding": "All 11 solvent-screen rows extracted; entry 11 merged with its exact repeats in Tables 3 and 4. Recovery, trace, table-dash, yield, and selectivity results were kept distinct.", "evidence_ids": ev(3)},
                {"region": "lower-left Figure 1", "finding": "ORTEP structure of (E)-4ca linked contextually to Table 4 entry 12; not treated as an additional reaction.", "evidence_ids": ev(3)},
                {"region": "lower-right Scheme 3", "finding": "Oxidation of (E)-6ab to (E)-4ab extracted as one reported experiment with 52% yield.", "evidence_ids": ev(3)},
            ],
            "record_ids": [r["record_id"] for r in records if r["source_reaction_id"].startswith("table1_") or r["source_reaction_id"] == "optimized_2a_3a_conditions_A" or r["source_reaction_id"].startswith("scheme3_") or r["source_reaction_id"] == "table4_entry12_4ca"],
            "unresolved": ["Table dashes are undefined and retained as source markers.", "Scheme 3 lacks quantities, atmosphere, workup, purification, and yield basis on this page."],
        },
        {
            "page": 4,
            "state": "attempted",
            "regions": [
                {"region": "upper Table 2 and footnotes", "finding": "All eight palladium-catalyst screen rows extracted, including PPh3 footnote additions, recovered 2a, and the complex-mixture result.", "evidence_ids": ev(4)},
                {"region": "lower Table 3 and footnotes", "finding": "Five AcOH-loading/temperature rows accounted for; entry 3 merged with the identical optimized experiment already printed in Table 1.", "evidence_ids": ev(4)},
            ],
            "record_ids": [r["record_id"] for r in records if r["source_reaction_id"].startswith("table2_") or r["source_reaction_id"].startswith("table3_") or r["source_reaction_id"] == "optimized_2a_3a_conditions_A"],
            "unresolved": ["Table dashes are undefined source markers.", "Workup and purification are absent; reflux has no numerical temperature."],
        },
        {
            "page": 5,
            "state": "attempted",
            "regions": [
                {"region": "upper Table 4 and footnotes", "finding": "All 12 sulfone-scope rows accounted for; entry 1 merged with the identical optimized experiment, and entries 2–12 extracted independently.", "evidence_ids": ev(5)},
                {"region": "lower-left Figure 2", "finding": "NOESY interaction supporting (E)-9aa configuration; linked as structural context and not counted as another reaction.", "evidence_ids": ev(5)},
                {"region": "conclusion and general experimental text", "finding": "Narrative summary and instrument/general-material statements; no additional row-level experiment.", "evidence_ids": ev(5)},
            ],
            "record_ids": [r["record_id"] for r in records if r["source_reaction_id"].startswith("table4_") or r["source_reaction_id"] == "optimized_2a_3a_conditions_A"],
            "unresolved": ["Table 4 omits THF volume, workup, and purification.", "Complex structures and stereochemical SMILES remain unverified."],
        },
        {
            "page": 6,
            "state": "attempted",
            "regions": [
                {"region": "upper Table 5 and footnotes", "finding": "All nine sulfoxide-scope rows extracted independently with isolated yields and two selectivity ratios.", "evidence_ids": ev(6)},
                {"region": "lower Table 6 and footnotes", "finding": "All eight alkyl-allene optimization rows extracted independently, including THF overrides and the screw-cap Schlenk condition.", "evidence_ids": ev(6)},
            ],
            "record_ids": [r["record_id"] for r in records if r["source_reaction_id"].startswith("table5_") or r["source_reaction_id"].startswith("table6_")],
            "unresolved": ["Table 5 omits THF volume, workup, and purification.", "Table 6 omits workup/purification and gives qualitative reflux temperatures.", "Complex product/regioisomer structures remain unverified."],
        },
    ],
}


raw_dir = OUT / "raw_model"
raw_dir.mkdir(parents=True, exist_ok=True)
(raw_dir / "records_pages_0001_0006.json").write_text(json.dumps(records, ensure_ascii=False, indent=2))
coverage_dir = OUT / "coverage"
coverage_dir.mkdir(parents=True, exist_ok=True)
(coverage_dir / "pages_0001_0006.json").write_text(json.dumps(coverage, ensure_ascii=False, indent=2))

tasks_path = OUT / "tasks.json"
tasks = json.loads(tasks_path.read_text())
for task in tasks:
    if task.get("document_id") == DOC and task.get("evidence_id", "").endswith(":text"):
        page = int(task["evidence_id"].split(":page", 1)[1].split(":", 1)[0])
        if 1 <= page <= 6:
            task["state"] = "attempted"
            task["reason"] = "Original page image and text inspected; page-level extraction attempted for this session."
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2))

print(json.dumps({
    "records": len(records),
    "kinds": {kind: sum(r["record_kind"] == kind for r in records) for kind in sorted({r["record_kind"] for r in records})},
    "coverage_pages": [p["page"] for p in coverage["pages"]],
}, ensure_ascii=False, indent=2))
