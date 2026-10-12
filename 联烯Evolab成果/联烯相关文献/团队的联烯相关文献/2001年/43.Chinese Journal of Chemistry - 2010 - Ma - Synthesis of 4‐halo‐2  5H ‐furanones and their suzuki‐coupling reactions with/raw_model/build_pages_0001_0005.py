#!/usr/bin/env python3
"""Build evidence-linked records for doc_00d3d1f6854f627b, PDF pages 1-5."""
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / "runs" / "current"
DOC = "doc_00d3d1f6854f627b"


def f(value, evidence=()):
    return {
        "value": value,
        "evidence_ids": list(dict.fromkeys(evidence)),
        "verification": "missing" if value is None else "unreviewed",
    }


def q(number, unit, raw_text=None, qualifier=None):
    value = {"number": number, "unit": unit}
    if raw_text is not None:
        value["raw_text"] = raw_text
    if qualifier is not None:
        value["qualifier"] = qualifier
    return value


def field(name, value, evidence=(), targets=None):
    item = {"name": name, "fact": f(value, evidence)}
    if targets:
        item["target_entity_ids"] = list(targets)
    return item


SMILES = {
    "iodine": "II",
    "potassium carbonate": "[K+].[K+].[O-]C([O-])=O",
    "NBS": "O=C1CCC(=O)N1Br",
    "THF": "C1CCOC1",
    "water": "O",
    "toluene": "Cc1ccccc1",
    "methanol": "CO",
    "phenylboronic acid": "OB(O)c1ccccc1",
    "o-methoxyphenylboronic acid": "COc1ccccc1B(O)O",
    "p-methoxyphenylboronic acid": "COc1ccc(B(O)O)cc1",
    "methylboronic acid": "CB(O)O",
    "sodium carbonate": "[Na+].[Na+].[O-]C([O-])=O",
    "carbon dioxide": "O=C=O",
}


def participant(entity_id, role, label, evidence, *, name=None, smiles=None, amounts=()):
    if smiles is None:
        smiles = SMILES.get(name or label)
    return {
        "entity_id": entity_id,
        "role": role,
        "label": f(label, evidence),
        "name": f(name, evidence) if name else f(None),
        "smiles": f(smiles, evidence) if smiles else f(None),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": list(amounts),
    }


def step(step_id, participant_ids, conditions):
    return {
        "step_id": step_id,
        "participant_ids": list(participant_ids),
        "conditions": list(conditions),
    }


def record(suffix, kind, evidence, participants, steps, outcomes, *, notes=(), unresolved=()):
    return {
        "record_id": f"{DOC}:{suffix}",
        "document_id": DOC,
        "source_reaction_id": suffix,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": list(dict.fromkeys(evidence)),
        "participants": list(participants),
        "steps": list(steps),
        "outcomes": list(outcomes),
        "notes": [f(text, ev) for text, ev in notes],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": list(unresolved),
        },
    }


def amt(name, number, unit, evidence, raw_text=None):
    return field(name, q(number, unit, raw_text), evidence)


P = {
    n: [f"{DOC}:page{n}:text", f"{DOC}:page{n}:image"] for n in range(1, 6)
}


records = []

# Cited/incomplete starting-material preparations from the Reagents and substrates section.
records.append(record(
    "starting_material_allenoic_acids_ref9", "literature_example", P[3],
    [
        participant("sm_allenes", "reactant", "corresponding 1,2-allenes", P[3]),
        participant("sm_n_buli", "reagent", "n-BuLi", P[3], name="n-butyllithium"),
        participant("sm_co2", "reagent", "CO2", P[3], name="carbon dioxide"),
        participant("sm_acids", "product", "2,3-octadienoic acid, 2,3-undecadienoic acid, and 5,5-dimethyl-2,3-hexadienoic acid", P[3]),
    ],
    [
        step("form_allenyllithium", ["sm_allenes", "sm_n_buli"], [field("time", None), field("temperature", None)]),
        step("carboxylation", ["sm_n_buli", "sm_co2", "sm_acids"], [field("time", None), field("temperature", None)]),
    ],
    [],
    notes=[("The article states that these acids were prepared according to published procedure 9; the cited procedure was not imported.", P[3])],
    unresolved=["Compound-specific charges, conditions, workup, purification, and yields are not reported locally.", "Structures are source-labelled but not independently verified."],
))

records.append(record(
    "starting_material_1d_ref10", "literature_example", P[3],
    [
        participant("sm1d_acyl", "reactant", "acyl chlorides", P[3]),
        participant("sm1d_ylide", "reagent", "ethyl 2-(triphenylphosphoranylidene)propionates", P[3]),
        participant("sm1d_base", "unspecified_agent", "NaOH or LiOH (alternative hydrolysis bases)", P[3], amounts=[amt("equivalents", 1.5, "equiv", P[3], "1.5 equiv")]),
        participant("sm1d_product", "product", "4-phenyl-3-methyl-2,3-butadienoic acid (1d)", P[3]),
    ],
    [
        step("allenoate_formation", ["sm1d_acyl", "sm1d_ylide"], [field("time", None), field("temperature", None)]),
        step("hydrolysis", ["sm1d_base", "sm1d_product"], [field("time", None), field("temperature", None)]),
    ],
    [],
    notes=[("The preparation is explicitly attributed to known method 10; NaOH and LiOH are alternatives, not simultaneous reagents.", P[3])],
    unresolved=["Precursor identity, charge, solvent, operating conditions, workup, purification, and yield are not reported locally.", "The printed acid name differs in ordering from the Table 1 substrate descriptor and remains source-local."],
))


# Table 1: iodolactonization. Entries 1-2 are explicitly prior data; entries 3-8 are current scope.
t1 = [
    (1, "n-Bu", "H", "H", "1a", "2a", 91, "4-iodo-5-(n-butyl)-2(5H)-furanone", "literature_example", None),
    (2, "n-C7H15", "H", "H", "1b", "2b", 90, "4-iodo-5-(n-heptyl)-2(5H)-furanone", "literature_example", None),
    (3, "t-Bu", "H", "H", "1c", "2c", 91, "4-iodo-5-(t-butyl)-2(5H)-furanone", "substrate_scope_entry", {"sub_mg": 28.0, "sub_mmol": 0.20, "i_mg": 61.0, "i_mmol": 0.24, "base_mg": 27.6, "base_mmol": 0.20, "prod_mg": 48.6}),
    (4, "Ph", "H", "Me", "1d", "2d", 99, "3-methyl-4-iodo-5-phenyl-2(5H)-furanone", "substrate_scope_entry", {"sub_mg": 470.0, "sub_mmol": 2.70, "i_mg": 720.0, "i_mmol": 2.84, "base_mg": 414.6, "base_mmol": 2.97, "prod_mg": 800.0}),
    (5, "Ph", "H", "n-Pr", "1e", "2e", 97, "3-(n-propyl)-4-iodo-5-phenyl-2(5H)-furanone", "substrate_scope_entry", {"sub_g": 1.097, "sub_mmol": 5.43, "i_g": 1.448, "i_mmol": 5.70, "base_g": 0.826, "base_mmol": 6.00, "prod_g": 1.724}),
    (6, "1'-naphthyl", "H", "Me", "1f", "2f", 97, "3-methyl-4-iodo-5-(1'-naphthyl)-2(5H)-furanone", "substrate_scope_entry", {"sub_mg": 448, "sub_mmol": 2.0, "i_mg": 610, "i_mmol": 2.4, "base_mg": 276, "base_mmol": 2.0, "prod_mg": 682}),
    (7, "Ph", "Me", "H", "1g", "2g", 87, "4-iodo-5-methyl-5-phenyl-2(5H)-furanone", "substrate_scope_entry", {"sub_mg": 348.0, "sub_mmol": 2.0, "i_mg": 533.4, "i_mmol": 2.1, "base_mg": 276.4, "base_mmol": 2.0, "prod_mg": 522.0}),
    (8, "p-BrC6H4", "H", "n-Pr", "1h", "2h", 96, "3-(n-propyl)-4-iodo-5-(4'-bromophenyl)-2(5H)-furanone", "substrate_scope_entry", {"sub_g": 2.30, "sub_mmol": 8.2, "i_g": 2.50, "i_mmol": 9.8, "base_g": 1.36, "base_mmol": 9.8, "prod_g": 3.21}),
]

for entry, r1, r2, r3, sub, prod, yld, prod_name, kind, detail in t1:
    ev = list(P[2])
    if detail:
        ev += P[3]
    if entry == 8:
        ev += P[4]
    sub_amounts = [amt("table_equivalents", 1, "equiv", P[2])]
    i_amounts = []
    base_amounts = []
    prod_amounts = []
    if detail:
        if "sub_mg" in detail:
            sub_amounts += [amt("mass", detail["sub_mg"], "mg", P[3]), amt("amount", detail["sub_mmol"], "mmol", P[3])]
        else:
            sub_amounts += [amt("mass", detail["sub_g"], "g", P[3]), amt("amount", detail["sub_mmol"], "mmol", P[3])]
        if "i_mg" in detail:
            i_amounts += [amt("mass", detail["i_mg"], "mg", P[3]), amt("amount", detail["i_mmol"], "mmol", P[3])]
        else:
            i_amounts += [amt("mass", detail["i_g"], "g", P[3]), amt("amount", detail["i_mmol"], "mmol", P[3])]
        if "base_mg" in detail:
            base_amounts += [amt("mass", detail["base_mg"], "mg", P[3]), amt("amount", detail["base_mmol"], "mmol", P[3])]
        else:
            base_amounts += [amt("mass", detail["base_g"], "g", P[3]), amt("amount", detail["base_mmol"], "mmol", P[3])]
        unit = "mg" if "prod_mg" in detail else "g"
        prod_amounts.append(amt("isolated_mass", detail.get("prod_mg", detail.get("prod_g")), unit, P[3]))
    parts = [
        participant(f"t1e{entry}_sub", "reactant", sub, ev, name=f"2,3-allenoic acid {sub}; R1={r1}, R2={r2}, R3={r3}", amounts=sub_amounts),
        participant(f"t1e{entry}_i2", "reagent", "I2", ev, name="iodine", amounts=i_amounts),
        participant(f"t1e{entry}_base", "reagent", "K2CO3", ev, name="potassium carbonate", amounts=base_amounts),
        participant(f"t1e{entry}_thf", "solvent", "THF", ev, name="THF", amounts=[amt("volume", 2, "mL", P[3])] if entry == 3 else []),
        participant(f"t1e{entry}_prod", "product", prod, ev, name=prod_name, amounts=prod_amounts),
    ]
    step1_conditions = [field("temperature", q(0, "°C"), P[2])]
    step2_conditions = [field("temperature", None), field("time", None)]
    if entry == 3:
        step1_conditions.append(field("time", q(1, "h"), P[3]))
        step2_conditions = [
            field("temperature", q(0, "°C"), P[3]),
            field("time", q(6, "h"), P[3]),
            field("workup", "aqueous sodium thiosulfate quench; extract with diethyl ether (3 x 10 mL); dry over anhydrous MgSO4; remove solvent", P[3]),
            field("purification", "flash chromatography on silica gel, petroleum ether/ethyl acetate 10:1", P[3]),
        ]
    steps = [
        step("iodine_stage", [f"t1e{entry}_sub", f"t1e{entry}_i2", f"t1e{entry}_thf"], step1_conditions),
        step("base_stage", [f"t1e{entry}_base", f"t1e{entry}_prod"], step2_conditions),
    ]
    basis = "isolated after chromatography" if detail else None
    outcomes = [
        field("yield", q(yld, "%"), P[2] if not detail else P[2] + P[3], [f"t1e{entry}_prod"]),
        field("yield_measurement_basis", basis, P[3] if basis else []),
    ]
    note_list = []
    unresolved = ["The substrate and product drawings/labels were not converted to verified SMILES."]
    if entry in (1, 2):
        note_list.append(("The table cites references 6 and 7, and page 3 states that data for 2a and 2b were reported in Ref. 7.", P[2] + P[3]))
        unresolved += ["Local charges, second-stage temperature, time, workup, purification, isolated mass, and yield basis are not reported in this article."]
    elif entry != 3:
        unresolved += ["The abbreviated paragraph reports charges and isolated product mass but does not repeat stage times, second-stage temperature, workup, or purification."]
    records.append(record(f"table1_entry{entry}", kind, ev, parts, steps, outcomes, notes=note_list, unresolved=unresolved))


# Table 2: bromolactonization. Entries 1-2 are explicitly prior data.
t2 = [
    (1, "n-Bu", "H", "H", "1a", "3a", 84, "4-bromo-5-(n-butyl)-2(5H)-furanone", "literature_example", None),
    (2, "n-C7H15", "H", "H", "1b", "3b", 81, "4-bromo-5-(n-heptyl)-2(5H)-furanone", "literature_example", None),
    (3, "Ph", "H", "Me", "1d", "3c", 94, "3-methyl-4-bromo-5-phenyl-2(5H)-furanone", "substrate_scope_entry", {"sub_mg": 174.0, "sub_mmol": 1.0, "nbs_mg": 214.0, "nbs_mmol": 1.2, "base_mg": 138.1, "base_mmol": 0.5, "prod_mg": 237.5}),
    (4, "Ph", "H", "n-Pr", "1e", "3d", 99, "3-(n-propyl)-4-bromo-5-phenyl-2(5H)-furanone", "substrate_scope_entry", {"sub_mg": 202.0, "sub_mmol": 1.0, "nbs_mg": 195.8, "nbs_mmol": 1.1, "base_mg": 69.0, "base_mmol": 0.5, "prod_mg": 277.0}),
    (5, "1'-naphthyl", "H", "Me", "1f", "3e", 98, "3-methyl-4-bromo-5-(1'-naphthyl)-2(5H)-furanone", "substrate_scope_entry", {"sub_mg": 224.0, "sub_mmol": 1.0, "nbs_mg": 214.0, "nbs_mmol": 1.2, "base_mg": 138.2, "base_mmol": 1.0, "prod_mg": 297.3}),
    (6, "Ph", "Me", "H", "1g", "3f", 99, "4-bromo-5-methyl-5-phenyl-2(5H)-furanone", "substrate_scope_entry", {"sub_mg": 174.0, "sub_mmol": 1.0, "nbs_mg": 195.6, "nbs_mmol": 1.1, "base_mg": 69.0, "base_mmol": 0.5, "prod_mg": 252.4}),
]

for entry, r1, r2, r3, sub, prod, yld, prod_name, kind, detail in t2:
    ev = list(P[2]) + (P[4] if detail else [])
    sub_amounts = [amt("table_equivalents", 1, "equiv", P[2])]
    nbs_amounts = [amt("table_equivalents", 1.1, "equiv", P[2])]
    base_amounts = [amt("table_equivalents", 0.5, "equiv", P[2])]
    prod_amounts = []
    if detail:
        sub_amounts += [amt("mass", detail["sub_mg"], "mg", P[4]), amt("amount", detail["sub_mmol"], "mmol", P[4])]
        nbs_amounts += [amt("detailed_mass", detail["nbs_mg"], "mg", P[4]), amt("detailed_amount", detail["nbs_mmol"], "mmol", P[4])]
        base_amounts += [amt("detailed_mass", detail["base_mg"], "mg", P[4]), amt("detailed_amount", detail["base_mmol"], "mmol", P[4])]
        prod_amounts.append(amt("isolated_mass", detail["prod_mg"], "mg", P[4]))
    parts = [
        participant(f"t2e{entry}_sub", "reactant", sub, ev, name=f"2,3-allenoic acid {sub}; R1={r1}, R2={r2}, R3={r3}", amounts=sub_amounts),
        participant(f"t2e{entry}_nbs", "reagent", "NBS", ev, name="NBS", amounts=nbs_amounts),
        participant(f"t2e{entry}_base", "reagent", "K2CO3", ev, name="potassium carbonate", amounts=base_amounts),
        participant(f"t2e{entry}_water", "solvent", "H2O", ev, name="water", amounts=[amt("volume", 5, "mL", P[4])] if entry == 3 else []),
        participant(f"t2e{entry}_prod", "product", prod, ev, name=prod_name, amounts=prod_amounts),
    ]
    conds = [field("temperature", "r.t.", P[2]), field("time", q(1, "h"), P[4]) if entry == 3 else field("time", None)]
    if entry == 3:
        conds += [
            field("workup", "extract with diethyl ether (3 x 10 mL), dry over anhydrous MgSO4, remove solvent", P[4]),
            field("purification", "flash chromatography on silica gel, petroleum ether/ethyl acetate 10:1", P[4]),
        ]
    steps = [step("bromolactonization", [p["entity_id"] for p in parts], conds)]
    outcomes = [
        field("isolated_yield", q(yld, "%"), P[2] + (P[4] if detail else []), [f"t2e{entry}_prod"]),
        field("yield_measurement_basis", "isolated yield", P[2]),
    ]
    note_list = []
    unresolved = ["The substrate and product drawings/labels were not converted to verified SMILES."]
    if entry in (1, 2):
        note_list.append(("The table cites references 6 and 7, and page 4 states that data for 3a and 3b were reported in Ref. 7.", P[2] + P[4]))
        unresolved += ["Local charges, reaction time, workup, purification, and isolated mass are not reported in this article."]
    elif entry != 3:
        unresolved += ["The abbreviated paragraph reports charges and isolated product mass but does not repeat reaction time, workup, or purification."]
    if entry == 3:
        unresolved.append("Table 2 gives NBS as 1.1 equivalents, while the detailed paragraph reports 1.2 mmol per 1.0 mmol substrate.")
    if entry == 5:
        unresolved.append("Table 2 gives NBS/K2CO3 as 1.1/0.5 equivalents, while the detailed paragraph reports 1.2/1.0 mmol per 1.0 mmol substrate.")
    records.append(record(f"table2_entry{entry}", kind, ev, parts, steps, outcomes, notes=note_list, unresolved=unresolved))


# Table 3: Suzuki coupling. Same products under different conditions remain separate records.
t3 = [
    (1, "2a", "I", "phenylboronic acid", "4a", 93, "4-phenyl-5-(n-butyl)-2(5H)-furanone", "toluene", {"sub_mg": 66.5, "sub_mmol": 0.25, "bor_mg": 60.0, "bor_mmol": 0.50, "prod_mg": 50.8}),
    (2, "2a", "I", "o-methoxyphenylboronic acid", "4b", 88, "4-(3'-methoxyphenyl)-5-(n-butyl)-2(5H)-furanone", "toluene", {"sub_mg": 66.5, "sub_mmol": 0.25, "bor_mg": 75.0, "bor_mmol": 0.5, "prod_mg": 54.0}),
    (3, "2b", "I", "phenylboronic acid", "4c", 88, "4-phenyl-5-(n-heptyl)-2(5H)-furanone", "toluene", {"sub_mg": 77.0, "sub_mmol": 0.25, "bor_mg": 60.0, "bor_mmol": 0.5, "prod_mg": 56.8}),
    (4, "2d", "I", "phenylboronic acid", "4d", 84, "3-methyl-4,5-diphenyl-2(5H)-furanone", "xylenes", None),
    (5, "2d", "I", "phenylboronic acid", "4d", 99, "3-methyl-4,5-diphenyl-2(5H)-furanone", "toluene", {"sub_mg": 78.0, "sub_mmol": 0.25, "bor_mg": 60.0, "bor_mmol": 0.5, "prod_mg": 61.9}),
    (6, "3c", "Br", "phenylboronic acid", "4d", 97, "3-methyl-4,5-diphenyl-2(5H)-furanone", "toluene", {"sub_mg": 68.7, "sub_mmol": 0.25, "bor_mg": 60.0, "bor_mmol": 0.5, "prod_mg": 60.6}),
    (7, "2d", "I", "methoxyphenylboronic acid (table: o-; paragraph: p-)", "4e", 85, "3-methyl-4-(p-methoxyphenyl)-5-phenyl-2(5H)-furanone", "toluene", {"sub_mg": 60.0, "sub_mmol": 0.20, "bor_mg": 60.0, "bor_mmol": 0.4, "prod_mg": 46.7}),
    (8, "2f", "I", "phenylboronic acid", "4f", 87, "3-methyl-4-phenyl-5-(1'-naphthyl)-2(5H)-furanone", "toluene", {"sub_mg": 70.0, "sub_mmol": 0.20, "bor_mg": 48.0, "bor_mmol": 0.4, "prod_mg": 52.3}),
    (9, "3e", "Br", "phenylboronic acid", "4f", 83, "3-methyl-4-phenyl-5-(1'-naphthyl)-2(5H)-furanone", "toluene", {"sub_mg": 60.6, "sub_mmol": 0.20, "bor_mg": 48.0, "bor_mmol": 0.4, "prod_mg": 49.8}),
    (10, "2a", "I", "methylboronic acid", None, None, None, "toluene", None),
]

for entry, sub, halide, boronic, prod, yld, prod_name, aromatic_solvent, detail in t3:
    ev = list(P[2])
    if entry in (1, 2):
        ev += P[4]
    if entry in (2, 3, 5, 6, 7, 8, 9):
        ev += P[5]
    sub_amounts = [amt("table_equivalents", 1, "equiv", P[2])]
    bor_amounts = [amt("table_equivalents", 2, "equiv", P[2])]
    prod_amounts = []
    detail_ev = P[4] if entry in (1, 2) else P[5]
    if detail:
        sub_amounts += [amt("mass", detail["sub_mg"], "mg", detail_ev), amt("amount", detail["sub_mmol"], "mmol", detail_ev)]
        bor_amounts += [amt("mass", detail["bor_mg"], "mg", detail_ev), amt("amount", detail["bor_mmol"], "mmol", detail_ev)]
        prod_amounts.append(amt("isolated_mass", detail["prod_mg"], "mg", detail_ev))
    halide_name = {"I": "iodo", "Br": "bromo"}[halide]
    parts = [
        participant(f"t3e{entry}_sub", "reactant", sub, ev, name=f"4-{halide_name}-2(5H)-furanone {sub}", amounts=sub_amounts),
        participant(f"t3e{entry}_bor", "reagent", boronic, ev, name=boronic if boronic in SMILES else None, amounts=bor_amounts),
        participant(f"t3e{entry}_pd", "catalyst", "Pd(PPh3)4", P[2], name="tetrakis(triphenylphosphine)palladium(0)", amounts=[amt("table_equivalents", 0.05, "equiv", P[2])]),
        participant(f"t3e{entry}_base", "reagent", "Na2CO3", ev, name="sodium carbonate", amounts=[amt("solution_concentration", 2, "M", P[2], "2 mol/L in H2O")] + ([amt("solution_volume", 0.3, "mL", P[4])] if entry == 1 else [])),
        participant(f"t3e{entry}_aromsolv", "solvent", aromatic_solvent, ev, name=aromatic_solvent, amounts=[amt("volume", 2, "mL", P[4])] if entry == 1 else []),
        participant(f"t3e{entry}_meoh", "solvent", "MeOH", ev, name="methanol", amounts=[amt("volume", 0.1, "mL", P[4])] if entry == 1 else []),
    ]
    if prod:
        parts.append(participant(f"t3e{entry}_prod", "product", prod, ev, name=prod_name, amounts=prod_amounts))
    conds = [
        field("solvent_ratio", "6:1 v/v aromatic solvent/MeOH", P[2]),
        field("temperature", "reflux", P[2]),
        field("time", "overnight", P[2]),
    ]
    if entry == 1:
        conds += [
            field("operation", "reaction system degassed; monitored by TLC", P[4]),
            field("workup", "quench with water; extract with diethyl ether (3 x 15 mL); combine organic layers; wash with brine; dry over anhydrous MgSO4; remove solvent", P[4]),
            field("purification", "flash chromatography, petroleum ether/ethyl acetate 10:1", P[4]),
        ]
    steps = [step("suzuki_coupling", [p["entity_id"] for p in parts], conds)]
    if prod:
        outcomes = [
            field("isolated_yield", q(yld, "%"), P[2] + (detail_ev if detail else []), [f"t3e{entry}_prod"]),
            field("yield_measurement_basis", "isolated yield", P[2]),
        ]
    else:
        outcomes = [
            field("coupling_result", "no coupling reaction", P[2]),
            field("isolated_yield", None),
        ]
    note_list = []
    unresolved = ["The substrate and product drawings/labels were not converted to verified SMILES.", "Atmosphere, reaction scale, concentration, and row-specific workup/purification are missing unless supplied by the detailed 4a procedure."]
    if entry == 1:
        unresolved.append("Table 3 prints toluene/MeOH = 6:1, while the detailed procedure uses 2.0 mL toluene and 0.1 mL MeOH (20:1 by volume).")
    if entry == 2:
        unresolved.append("The boronic acid is printed as o-methoxyphenylboronic acid, while the product heading calls 4b a 3'-methoxyphenyl product; the positional identity is unresolved.")
    if entry == 7:
        unresolved.append("Table 3 prints o-MeOC6H4, whereas the experimental paragraph and product heading print p-methoxyphenyl; the positional identity is unresolved.")
    if entry == 4:
        note_list.append(("Footnote c replaces toluene with xylenes for this row only.", P[2]))
        unresolved.append("No row-specific charge, isolated mass, or detailed procedure is reported for the 84% xylene run.")
    if entry == 10:
        note_list.append(("The prose explicitly states that coupling did not occur with methylboronic acid.", P[2]))
        unresolved += ["No recovered starting-material amount, detection limit, or numerical yield is reported."]
    records.append(record(f"table3_entry{entry}", "substrate_scope_entry", ev, parts, steps, outcomes, notes=note_list, unresolved=unresolved))


out_records = RUN / "raw_model" / "records_pages_0001_0005.json"
out_records.parent.mkdir(parents=True, exist_ok=True)
out_records.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")


table1_ids = [f"{DOC}:table1_entry{i}" for i in range(1, 9)]
table2_ids = [f"{DOC}:table2_entry{i}" for i in range(1, 7)]
table3_ids = [f"{DOC}:table3_entry{i}" for i in range(1, 11)]
prep_ids = [f"{DOC}:starting_material_allenoic_acids_ref9", f"{DOC}:starting_material_1d_ref10"]

coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1,
            "state": "attempted",
            "regions": [
                {"region": "title, abstract, and keywords", "finding": "Current article scope summary; no individual experiment with row-level conditions or yield.", "evidence_ids": [f"{DOC}:page1:image", f"{DOC}:page1:text"]},
                {"region": "Introduction, both columns", "finding": "Prior methods and biological context are discussed without locally specified individual reaction arrows or complete runs.", "evidence_ids": [f"{DOC}:page1:image", f"{DOC}:page1:text"]},
                {"region": "Results and discussion opening", "finding": "Narrative introduces iodo- and bromolactonization; the individual data are presented in Tables 1 and 2 on page 2.", "evidence_ids": [f"{DOC}:page1:image", f"{DOC}:page1:text"]},
            ],
            "record_ids": [],
            "unresolved": ["No individual row-level experimental record is fully specified on page 1; no record was fabricated from summary prose."],
        },
        {
            "page": 2,
            "state": "attempted",
            "regions": [
                {"region": "Table 1 and reaction header", "finding": "Eight iodolactonization rows; entries 1-2 cite prior work and entries 3-8 are current scope.", "evidence_ids": [f"{DOC}:page2:image", f"{DOC}:page2:text"]},
                {"region": "Table 2 and footnotes", "finding": "Six bromolactonization rows with common 1/NBS/K2CO3 ratio and isolated-yield footnote; entries 1-2 cite prior work.", "evidence_ids": [f"{DOC}:page2:image", f"{DOC}:page2:text"]},
                {"region": "Table 3, footnotes, and preceding prose", "finding": "Ten Suzuki rows, including distinct iodide/bromide and solvent comparisons and one explicit methylboronic-acid failure.", "evidence_ids": [f"{DOC}:page2:image", f"{DOC}:page2:text"]},
                {"region": "Conclusion and Experimental/Apparatus opening", "finding": "Summary and analytical-instrument context; no additional reaction run.", "evidence_ids": [f"{DOC}:page2:image", f"{DOC}:page2:text"]},
            ],
            "record_ids": table1_ids + table2_ids + table3_ids,
            "unresolved": ["Table 1 does not state a common yield measurement basis.", "Several table values conflict with later detailed paragraphs and are retained for source review."],
        },
        {
            "page": 3,
            "state": "attempted",
            "regions": [
                {"region": "Reagents and substrates", "finding": "Two cited/incomplete starting-material preparation families; external procedures were not imported.", "evidence_ids": [f"{DOC}:page3:image", f"{DOC}:page3:text"]},
                {"region": "General procedure for 2c", "finding": "Detailed Table 1 entry 3 charge, staged operation, workup, purification, mass, and 91% result.", "evidence_ids": [f"{DOC}:page3:image", f"{DOC}:page3:text"]},
                {"region": "Abbreviated preparations 2d-2h", "finding": "Charges and isolated product masses/yields supplement Table 1 entries 4-8; 2h characterization continues on page 4.", "evidence_ids": [f"{DOC}:page3:image", f"{DOC}:page3:text"]},
            ],
            "record_ids": prep_ids + [f"{DOC}:table1_entry{i}" for i in range(3, 9)],
            "unresolved": ["Abbreviated 2d-2h paragraphs do not repeat stage times, second-stage temperature, workup, or purification.", "Starting-material procedures are cited rather than reproduced completely."],
        },
        {
            "page": 4,
            "state": "attempted",
            "regions": [
                {"region": "2h characterization continuation", "finding": "Continuation evidence for Table 1 entry 8; no new reaction run.", "evidence_ids": [f"{DOC}:page4:image", f"{DOC}:page4:text"]},
                {"region": "General 3c procedure and abbreviated 3d-3f preparations", "finding": "Detailed/abbreviated evidence for Table 2 entries 3-6; data for 3a-3b are explicitly cited as prior work.", "evidence_ids": [f"{DOC}:page4:image", f"{DOC}:page4:text"]},
                {"region": "General 4a procedure and 4b opening", "finding": "Detailed Table 3 entry 1 procedure and entry 2 charges/yield; 4b characterization continues on page 5.", "evidence_ids": [f"{DOC}:page4:image", f"{DOC}:page4:text"]},
            ],
            "record_ids": [f"{DOC}:table1_entry8"] + [f"{DOC}:table2_entry{i}" for i in range(3, 7)] + [f"{DOC}:table3_entry1", f"{DOC}:table3_entry2"],
            "unresolved": ["Table 2 footnote stoichiometry conflicts with detailed charges for 3c and 3e.", "The 4b heading and o-methoxyphenylboronic-acid identity disagree on substitution position."],
        },
        {
            "page": 5,
            "state": "attempted",
            "regions": [
                {"region": "4b continuation and 4c preparation", "finding": "Continuation for Table 3 entry 2 and abbreviated preparation for entry 3.", "evidence_ids": [f"{DOC}:page5:image", f"{DOC}:page5:text"]},
                {"region": "4d preparations from 2d and 3c", "finding": "Two distinct Suzuki runs matching Table 3 entries 5 and 6; not merged despite identical product.", "evidence_ids": [f"{DOC}:page5:image", f"{DOC}:page5:text"]},
                {"region": "4e and 4f preparations", "finding": "One 4e run and two distinct iodide/bromide routes to 4f, matching Table 3 entries 7-9.", "evidence_ids": [f"{DOC}:page5:image", f"{DOC}:page5:text"]},
                {"region": "References", "finding": "Bibliography only; no additional current-paper experiment record.", "evidence_ids": [f"{DOC}:page5:image", f"{DOC}:page5:text"]},
            ],
            "record_ids": [f"{DOC}:table3_entry{i}" for i in (2, 3, 5, 6, 7, 8, 9)],
            "unresolved": ["Table 3 entry 7 prints o-methoxyphenyl, while the experimental paragraph prints p-methoxyphenyl.", "Abbreviated coupling paragraphs do not restate catalyst/base/solvent charges, workup, or purification."],
        },
    ],
}

coverage_path = RUN / "coverage" / "pages_0001_0005.json"
coverage_path.parent.mkdir(parents=True, exist_ok=True)
coverage_path.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")


tasks_path = RUN / "tasks.json"
tasks = json.loads(tasks_path.read_text())
for task in tasks:
    if task.get("document_id") == DOC and task.get("evidence_id", "").startswith(f"{DOC}:page"):
        page = int(task["evidence_id"].split(":page", 1)[1].split(":", 1)[0])
        if 1 <= page <= 5:
            task["state"] = "attempted"
            task["visual_evidence_id"] = f"{DOC}:page{page}:image"
            task["reason"] = "Original page image visually inspected; reaction regions, prose, footnotes, and experimental continuations extracted with unresolved issues retained."
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"records": len(records), "coverage_pages": [p["page"] for p in coverage["pages"]]}, ensure_ascii=False))
