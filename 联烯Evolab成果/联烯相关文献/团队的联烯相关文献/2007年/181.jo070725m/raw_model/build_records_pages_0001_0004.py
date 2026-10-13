#!/usr/bin/env python3
"""Build machine-derived reaction records for doc_093bbeacde907501, PDF pages 1-4."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "runs/current"
DOC = "doc_093bbeacde907501"


def ev(page):
    return [f"{DOC}:page{page}:text", f"{DOC}:page{page}:image"]


def fact(value, evidence=()):
    return {
        "value": value,
        "evidence_ids": list(evidence) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def q(number, unit, **extra):
    value = {"number": number, "unit": unit}
    value.update(extra)
    return value


def field(name, value, evidence=(), targets=None):
    result = {"name": name, "fact": fact(value, evidence)}
    if targets:
        result["target_entity_ids"] = list(targets)
    return result


def participant(entity_id, role, label, evidence, name=None, smiles=None, amounts=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence) if name else fact(None),
        "smiles": fact(smiles, evidence) if smiles else fact(None),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": amounts or [],
    }


def record(suffix, kind, evidence, participants, steps, outcomes, notes=None, unresolved=None):
    return {
        "record_id": f"{DOC}:{suffix}",
        "document_id": DOC,
        "source_reaction_id": suffix,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": list(dict.fromkeys(evidence)),
        "participants": participants,
        "steps": steps,
        "outcomes": outcomes,
        "notes": notes or [],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved or [],
        },
    }


def missing_conditions(*names):
    return [field(name, None) for name in names]


R_INFO = {
    "3a": ("C2H5", "3-(methoxycarbonyl)-1,2-hexadien-4-ol", "C=C=C(C(=O)OC)C(O)CC", "propanal", "CCC=O"),
    "3b": ("n-C3H7", "3-(methoxycarbonyl)-1,2-heptadien-4-ol", "C=C=C(C(=O)OC)C(O)CCC", "butanal", "CCCC=O"),
    "3c": ("i-C3H7", "3-(methoxycarbonyl)-5-methyl-1,2-hexadien-4-ol", "C=C=C(C(=O)OC)C(O)C(C)C", "2-methylpropanal", "CC(C)C=O"),
    "3d": ("n-C5H11", "3-(methoxycarbonyl)-1,2-nonadien-4-ol", "C=C=C(C(=O)OC)C(O)CCCCC", "hexanal", "CCCCCC=O"),
    "3e": ("Ph", "3-(methoxycarbonyl)-4-phenyl-1,2-butadien-4-ol", "C=C=C(C(=O)OC)C(O)c1ccccc1", "benzaldehyde", "O=Cc1ccccc1"),
    "3f": ("p-CH3C6H4", "3-(methoxycarbonyl)-4-(p-tolyl)-1,2-butadien-4-ol", "C=C=C(C(=O)OC)C(O)c1ccc(C)cc1", "p-tolualdehyde", "Cc1ccc(C=O)cc1"),
}

PRODUCT_NAMES = {
    "4aa": "methyl 2-(1-iodovinyl)pent-2(Z)-enoate",
    "4ab": "methyl 2-(1-bromovinyl)pent-2(Z)-enoate",
    "4ac": "methyl 2-(1-chlorovinyl)pent-2(Z)-enoate",
    "4ba": "methyl 2-(1-iodovinyl)hex-2(Z)-enoate",
    "4bb": "methyl 2-(1-bromovinyl)hex-2(Z)-enoate",
    "4bc": "methyl 2-(1-chlorovinyl)hex-2(Z)-enoate",
}

R_SMILES = {
    "3a": "CC",
    "3b": "CCC",
    "3c": "C(C)C",
    "3d": "CCCCC",
    "3e": "c1ccccc1",
    "3f": "c1ccc(C)cc1",
}

HALOGEN = {"a": "I", "b": "Br", "c": "Cl"}


def product_smiles(code, substrate):
    x = HALOGEN[code[-1]]
    return f"C=C({x})C(=C{R_SMILES[substrate]})C(=O)OC"


def amount(name, number, unit, evidence):
    return field(name, q(number, unit), evidence)


records = []

# Table 1: six individual starting-material preparations. The exact procedure is printed only for 3a.
t1_rows = [
    (1, "3a", 30, 59),
    (2, "3b", 36, 61),
    (3, "3c", 14, 83),
    (4, "3d", 36, 59),
    (5, "3e", 22, 78),
    (6, "3f", 24, 68),
]
for entry, code, hours, yield_value in t1_rows:
    e = ev(1) + (ev(3) if code == "3a" else [])
    r_label, product_name, product_smi, aldehyde_name, aldehyde_smi = R_INFO[code]
    exact = code == "3a"
    propargyl_amounts = []
    aldehyde_amounts = []
    sncl2_amounts = [amount("equivalents", 1.2, "equiv", ev(1))]
    nai_amounts = [amount("equivalents", 1.2, "equiv", ev(1))]
    dmpu_amounts = []
    product_amounts = []
    if exact:
        propargyl_amounts = [amount("mass", 3.4806, "g", ev(3)), amount("amount", 19.7, "mmol", ev(3))]
        aldehyde_amounts = [amount("mass", 0.9281, "g", ev(3)), amount("amount", 16.0, "mmol", ev(3))]
        sncl2_amounts += [amount("mass", 4.6011, "g", ev(3)), amount("amount", 24.2, "mmol", ev(3))]
        nai_amounts += [amount("mass", 3.6107, "g", ev(3)), amount("amount", 24.1, "mmol", ev(3))]
        dmpu_amounts = [amount("initial_volume", 30, "mL", ev(3)), amount("aldehyde_solution_volume", 10, "mL", ev(3))]
        product_amounts = [amount("isolated_mass", 1.4606, "g", ev(3))]
    parts = [
        participant("propargyl_bromide", "reactant", "1", e, "methyl 4-bromobut-2-ynoate", "COC(=O)C#CCBr", propargyl_amounts),
        participant("aldehyde", "reactant", "2", e, aldehyde_name, aldehyde_smi, aldehyde_amounts),
        participant("sncl2", "reagent", "SnCl2", e, "tin(II) chloride", None, sncl2_amounts),
        participant("nai", "reagent", "NaI", e, "sodium iodide", "[Na+].[I-]", nai_amounts),
        participant("dmpu", "solvent", "DMPU", e, "N,N'-dimethylpropyleneurea", None, dmpu_amounts),
        participant("product", "product", code, e, product_name, product_smi, product_amounts),
    ]
    if exact:
        steps = [
            {"step_id": "preactivation", "participant_ids": ["propargyl_bromide", "sncl2", "nai", "dmpu"], "conditions": [
                field("temperature", "r.t.", ev(3)), field("time", q(6, "h"), ev(3)),
                field("operation", "stirred in the absence of light; reaction tube wrapped with a black plastic bag", ev(3)),
            ]},
            {"step_id": "aldehyde_addition", "participant_ids": ["aldehyde"], "conditions": [
                field("temperature", q(0, "°C"), ev(3)), field("addition_time", q(15, "min"), ev(3)),
                field("operation", "aldehyde solution added dropwise", ev(3)),
            ]},
            {"step_id": "reaction", "participant_ids": [p["entity_id"] for p in parts], "conditions": [
                field("temperature", "r.t.", ev(3)), field("time", q(24, "h"), ev(3)),
                field("table_reported_time", q(30, "h"), ev(1)),
                field("operation", "allowed to warm to room temperature and stirred in the dark", ev(3)),
                field("workup", "cooled to 0 °C; diluted with Et2O; quenched with 30 mL saturated aqueous NH4Cl; aqueous phase extracted with Et2O (4 × 30 mL); combined organic layer washed with brine and dried over anhydrous Na2SO4; evaporated", ev(3)),
                field("purification", "silica-gel column chromatography, petroleum ether/ethyl acetate 5:1", ev(3)),
                field("atmosphere", None),
            ]},
        ]
        basis = field("yield_measurement_basis", "isolated after column chromatography", ev(3), ["product"])
        unresolved = ["Reaction atmosphere is not reported.", "Candidate structures remain machine-derived and unverified."]
    else:
        steps = [{"step_id": "reaction", "participant_ids": [p["entity_id"] for p in parts], "conditions": [
            field("initial_temperature", "r.t.", ev(1)), field("aldehyde_addition_temperature", q(0, "°C"), ev(1)),
            field("final_temperature", "r.t.", ev(1)), field("time", q(hours, "h"), ev(1)),
        ] + missing_conditions("atmosphere", "workup", "purification")}]
        basis = field("yield_measurement_basis", None, targets=["product"])
        unresolved = ["Absolute scale, atmosphere, workup, purification, and yield measurement basis are not reported for this abbreviated Table 1 row.", "Candidate structures remain machine-derived and unverified."]
    records.append(record(
        f"table1_entry{entry}_{code}", "substrate_scope_entry", e, parts, steps,
        [field("reported_yield", q(yield_value, "%"), e, ["product"]), basis],
        notes=[fact(f"Table 1 row uses R = {r_label}.", ev(1))], unresolved=unresolved,
    ))


def allene_part(code, evidence, amounts=None):
    r_label, name, smi, _, _ = R_INFO[code]
    return participant("substrate", "reactant", code, evidence, name, smi, amounts or [])


def halo_product(code, substrate, evidence, expected=False, amounts=None):
    name = PRODUCT_NAMES.get(code, f"3-(methoxycarbonyl)-2-halo-1,3(Z)-diene {code}")
    return participant("product", "product", code, evidence, name, product_smiles(code, substrate), amounts or [])


def solvent_part(label, evidence):
    names = {
        "CH3COOH": ("acetic acid", "CC(=O)O"),
        "HOAc": ("acetic acid", "CC(=O)O"),
        "Ac2O": ("acetic anhydride", "CC(=O)OC(C)=O"),
        "HI": ("hydroiodic acid", None),
        "TFA": ("trifluoroacetic acid", "O=C(O)C(F)(F)F"),
    }
    name, smi = names[label]
    return participant("solvent", "solvent", label, evidence, name, smi)


def halide_part(label, equiv, evidence):
    name_map = {
        "NaI": "sodium iodide", "LiI·3H2O": "lithium iodide trihydrate", "KI": "potassium iodide",
        "LiBr·H2O": "lithium bromide monohydrate", "KBr": "potassium bromide",
        "LiCl·H2O": "lithium chloride monohydrate", "NaCl": "sodium chloride",
    }
    smiles_map = {"NaI": "[Na+].[I-]", "KI": "[K+].[I-]", "KBr": "[K+].[Br-]", "NaCl": "[Na+].[Cl-]"}
    return participant("mx", "reagent", label, evidence, name_map[label], smiles_map.get(label), [amount("equivalents", equiv, "equiv", evidence)])


def addition_record(suffix, kind, evidence, substrate, product, solvent, salt, equiv, time_value, temp_value, yield_value, extra_evidence=(), conflict_times=None, no_product=False):
    e = list(dict.fromkeys(evidence + list(extra_evidence)))
    parts = [allene_part(substrate, e), halide_part(salt, equiv, e), solvent_part(solvent, e), halo_product(product, substrate, e, expected=no_product)]
    conditions = [field("temperature", temp_value, e), field("time", time_value, e)]
    if conflict_times:
        conditions = [field(name, value, source_ev) for name, value, source_ev in conflict_times] + [field("temperature", temp_value, e)]
    conditions += missing_conditions("atmosphere", "workup", "purification")
    outcomes = [field("reported_yield", yield_value, e, ["product"]), field("yield_measurement_basis", None, targets=["product"])]
    notes = []
    unresolved = ["Atmosphere, workup, purification, and yield measurement basis are not reported.", "Candidate substrate/product structures and alkene stereochemistry remain unverified."]
    if no_product:
        outcomes.append(field("product_formation", "no 4ea was formed", evidence, ["product"]))
    if conflict_times:
        unresolved.insert(0, "Table 3 reports 3 h while Table 4 reports 6 h for the same 3b/LiCl·H2O/TFA/55% 4bc condition; both are retained.")
    records.append(record(suffix, kind, e, parts, [{"step_id": "addition_elimination", "participant_ids": [p["entity_id"] for p in parts], "conditions": conditions}], outcomes, notes=notes, unresolved=unresolved))


# Table 2 entries, except entry 5 which is merged with Table 3 entry 1 and Table 4 entry 4 below.
t2_rows = [
    (1, "CH3COOH", "NaI", 1.2, "reflux", q(1, "h"), "trace"),
    (2, "Ac2O", "NaI", 1.2, q(110, "°C"), q(1, "h"), q(41, "%")),
    (4, "TFA", "NaI", 1.2, "reflux", q(1, "h"), q(61, "%")),
    (6, "TFA", "NaI", 4.0, "reflux", q(1, "h"), q(68, "%")),
    (7, "TFA", "NaI", 2.0, "r.t.", q(24, "h"), q(32, "%")),
]
for entry, solv, salt, equiv, temp, duration, yld in t2_rows:
    addition_record(f"table2_entry{entry}_4ba", "optimization_entry", ev(2), "3b", "4ba", solv, salt, equiv, duration, temp, yld)

# Table 2 entry 3 has a blank NaI column and uses HI; do not silently add NaI.
e = ev(2)
parts = [allene_part("3b", e), solvent_part("HI", e), halo_product("4ba", "3b", e)]
records.append(record(
    "table2_entry3_4ba", "optimization_entry", e, parts,
    [{"step_id": "addition_elimination", "participant_ids": [p["entity_id"] for p in parts], "conditions": [
        field("temperature", q(80, "°C"), e), field("time", q(3, "h"), e),
    ] + missing_conditions("atmosphere", "workup", "purification")}],
    [field("reported_yield", "trace", e, ["product"]), field("yield_measurement_basis", None, targets=["product"])],
    notes=[fact("The NaI-equivalents cell is blank for this HI row; NaI was not added as a participant.", e)],
    unresolved=["The role/concentration of HI is not specified beyond its placement in the solvent column.", "Atmosphere, workup, purification, and yield measurement basis are not reported.", "Candidate structures remain unverified."],
))


# Table 3 entries not duplicated in Table 4.
t3_unique = [
    (2, "LiI·3H2O", 2.0, 1, "4ba", 58),
    (3, "KI", 2.0, 1, "4ba", 44),
    (5, "KBr", 2.0, 3, "4bb", 58),
    (7, "NaCl", 4.0, 14, "4bc", "trace"),
]
for entry, salt, equiv, hours, product, yld in t3_unique:
    y = q(yld, "%") if isinstance(yld, (int, float)) else yld
    addition_record(f"table3_entry{entry}_{product}", "optimization_entry", ev(2), "3b", product, "TFA", salt, equiv, q(hours, "h"), "reflux", y)


# Table 4 scope. Entries 4/5/6 absorb their exact duplicates in Table 2/Table 3.
t4_rows = [
    (1, "3a", "TFA", "NaI", 2.0, 1, 50, "4aa"),
    (2, "3a", "TFA", "LiBr·H2O", 2.0, 2, 56, "4ab"),
    (3, "3a", "TFA", "LiCl·H2O", 4.0, 3, 39, "4ac"),
    (4, "3b", "TFA", "NaI", 2.0, 1, 73, "4ba"),
    (5, "3b", "TFA", "LiBr·H2O", 2.0, 2, 76, "4bb"),
    (6, "3b", "TFA", "LiCl·H2O", 4.0, 6, 55, "4bc"),
    (7, "3c", "TFA", "NaI", 2.0, 2, 53, "4ca"),
    (8, "3c", "TFA", "LiBr·H2O", 2.0, 1, 64, "4cb"),
    (9, "3c", "TFA", "LiCl·H2O", 4.0, 2, 39, "4cc"),
    (10, "3d", "TFA", "NaI", 2.0, 1, 75, "4da"),
    (11, "3d", "TFA", "LiBr·H2O", 2.0, 3.5, 67, "4db"),
    (12, "3d", "TFA", "LiCl·H2O", 4.0, 4, 47, "4dc"),
    (13, "3e", "TFA", "NaI", 2.0, 1, 0, "4ea"),
    (14, "3e", "TFA", "LiBr·H2O", 2.0, 1, 44, "4eb"),
    (15, "3e", "TFA", "LiCl·H2O", 4.0, 4, 26, "4ec"),
    (16, "3e", "HOAc", "NaI", 2.0, 2, 40, "4ea"),
    (17, "3e", "HOAc", "LiBr·H2O", 2.0, 3, 44, "4eb"),
    (18, "3e", "HOAc", "LiCl·H2O", 4.0, 4, 30, "4ec"),
    (19, "3f", "HOAc", "NaI", 2.0, 1, 73, "4fa"),
    (20, "3f", "HOAc", "LiBr·H2O", 2.0, 1, 62, "4fb"),
    (21, "3f", "HOAc", "LiCl·H2O", 4.0, 1, 59, "4fc"),
]
for entry, substrate, solv, salt, equiv, hours, yld, product in t4_rows:
    extra = []
    suffix = f"table4_entry{entry}_{product}"
    conflict_times = None
    if entry == 4:
        extra = ev(2)  # Table 2 entry 5 and Table 3 entry 1 are the same printed condition.
        suffix = "standard_3b_nai_4ba"
    elif entry == 5:
        extra = ev(2)  # Table 3 entry 4.
        suffix = "standard_3b_libr_4bb"
    elif entry == 6:
        extra = ev(2)  # Table 3 entry 6, with a conflicting time.
        suffix = "standard_3b_licl_4bc"
        conflict_times = [
            ("table3_time", q(3, "h"), ev(2)),
            ("table4_time", q(6, "h"), ev(2)),
        ]
    no_product = entry == 13
    addition_record(suffix, "substrate_scope_entry", ev(2), substrate, product, solv, salt, equiv, q(hours, "h"), "reflux", q(yld, "%"), extra_evidence=extra, conflict_times=conflict_times, no_product=no_product)

# Replace Table 4 entry 1 with its exact page-3 typical procedure while preserving the same ID.
idx = next(i for i, r in enumerate(records) if r["record_id"].endswith(":table4_entry1_4aa"))
e = ev(1) + ev(2) + ev(3)
parts = [
    allene_part("3a", e, [amount("mass", 77.0, "mg", ev(3)), amount("amount", 0.49, "mmol", ev(3))]),
    participant("mx", "reagent", "NaI", e, "sodium iodide", "[Na+].[I-]", [amount("mass", 151.1, "mg", ev(3)), amount("amount", 1.0, "mmol", ev(3)), amount("equivalents", 2.0, "equiv", ev(2))]),
    participant("solvent", "solvent", "TFA", e, "trifluoroacetic acid", "O=C(O)C(F)(F)F", [amount("volume", 1.0, "mL", ev(3))]),
    halo_product("4aa", "3a", e, amounts=[amount("isolated_mass", 65.4, "mg", ev(3))]),
]
records[idx] = record(
    "table4_entry1_4aa", "substrate_scope_entry", e, parts,
    [{"step_id": "addition_elimination", "participant_ids": [p["entity_id"] for p in parts], "conditions": [
        field("addition_temperature", "r.t.", ev(3)), field("table_temperature", "reflux", ev(2)), field("detailed_temperature", q(80, "°C"), ev(3)), field("time", q(1, "h"), ev(2) + ev(3)),
        field("operation", "stirred and monitored by TLC until complete", ev(3)),
        field("workup", "cooled to room temperature; slowly quenched with 10 mL water; neutralized with NaHCO3 until gas evolution ceased; extracted with diethyl ether (3 × 25 mL); washed with saturated aqueous Na2S2O3 and brine; dried over anhydrous Na2SO4; evaporated", ev(3)),
        field("purification", "silica-gel column chromatography, 30–60 °C petroleum ether/diethyl ether 30:1", ev(3)), field("atmosphere", None),
    ]}],
    [field("isolated_yield", q(50, "%"), ev(2) + ev(3), ["product"]), field("yield_measurement_basis", "isolated after column chromatography", ev(3), ["product"])],
    unresolved=["Reaction atmosphere is not reported.", "Candidate structures and alkene stereochemistry remain unverified."],
)


# Scheme 1: DIBAL-H reduction of 4ba to 5ba, merged with the exact page-3 procedure.
e = ev(2) + ev(3)
parts = [
    participant("substrate", "reactant", "4ba", e, PRODUCT_NAMES["4ba"], product_smiles("4ba", "3b"), [amount("mass", 180.0, "mg", ev(3)), amount("amount", 0.64, "mmol", ev(3))]),
    participant("dibal", "reagent", "DIBAL-H", e, "diisobutylaluminium hydride", None, [amount("volume", 1.4, "mL", ev(3)), amount("concentration", 1, "M", ev(3)), amount("amount", 1.4, "mmol", ev(3))]),
    participant("toluene", "solvent", "toluene", e, "toluene", "Cc1ccccc1", [amount("volume", 3, "mL", ev(3))]),
    participant("product", "product", "5ba", e, "(Z)-2-(1-iodovinyl)hex-2-en-1-ol", "C=C(I)C(=CCCC)CO", [amount("isolated_mass", 118.7, "mg", ev(3))]),
]
records.append(record(
    "scheme1_dibal_reduction_5ba", "reported_experiment", e, parts,
    [{"step_id": "reduction", "participant_ids": [p["entity_id"] for p in parts], "conditions": [
        field("temperature", q(-78, "°C"), e), field("time", None), field("operation", "DIBAL-H added dropwise; conversion monitored by TLC", ev(3)),
        field("workup", "quenched with 2 mL CH3OH and 5 mL water; aqueous layer extracted with diethyl ether (3 × 25 mL); combined organic layer dried over Na2SO4; evaporated", ev(3)),
        field("purification", "silica-gel column chromatography, petroleum ether/ethyl acetate 10:1", ev(3)), field("atmosphere", None),
    ]}],
    [field("isolated_yield", q(73, "%"), e, ["product"]), field("yield_measurement_basis", "isolated after column chromatography", ev(3), ["product"])],
    notes=[fact("NOESY analysis of 5ba was used to establish the stereochemistry of 4ba.", ev(2))],
    unresolved=["Reaction duration and atmosphere are not reported.", "Candidate substrate/product structures and stereochemistry remain unverified."],
))


def coupling_record(suffix, product_code, reaction_type, reagent_label, reagent_name, reagent_smiles, reagent_equiv, catalysts, solvents, temperatures, scheme_yield, prose_yield=None, detailed=False):
    e = ev(3) + (ev(2) if product_code in {"6ba", "6bb", "6bc", "6bd", "6be", "6bf"} else [])
    substrate_amounts = [amount("mass", 55.9, "mg", ev(3)), amount("amount", 0.20, "mmol", ev(3))] if detailed else []
    reagent_amounts = [amount("equivalents", reagent_equiv, "equiv", ev(3))] if reagent_equiv is not None else []
    if detailed:
        reagent_amounts += [amount("mass", 41.6, "mg", ev(3)), amount("amount", 0.41, "mmol", ev(3))]
    parts = [participant("substrate", "reactant", "4ba", e, PRODUCT_NAMES["4ba"], product_smiles("4ba", "3b"), substrate_amounts)]
    parts.append(participant("coupling_partner", "reactant", reagent_label, e, reagent_name, reagent_smiles, reagent_amounts))
    for entity_id, label, name, loading, smi in catalysts:
        amts = [amount("catalyst_loading", loading, "mol%", ev(3))]
        if detailed and entity_id == "pd":
            amts += [amount("mass", 6.8, "mg", ev(3)), amount("amount", 0.01, "mmol", ev(3))]
        if detailed and entity_id == "cui":
            amts += [amount("mass", 4.1, "mg", ev(3)), amount("amount", 0.02, "mmol", ev(3))]
        parts.append(participant(entity_id, "catalyst", label, e, name, smi, amts))
    for i, (label, name, smi, volume) in enumerate(solvents):
        amts = [amount("volume", volume, "mL", ev(3))] if volume is not None else []
        parts.append(participant(f"solvent_{i+1}", "solvent", label, e, name, smi, amts))
    if detailed:
        parts.append(participant("base", "reagent", "Et2NH", e, "diethylamine", "CCNCC", [amount("mass", 22.2, "mg", ev(3)), amount("amount", 0.30, "mmol", ev(3)), amount("equivalents", 1.5, "equiv", ev(3))]))
    elif product_code in {"6ba", "6bb"}:
        parts.append(participant("base", "reagent", "Et2NH", e, "diethylamine", "CCNCC", [amount("equivalents", 1.5, "equiv", ev(3))]))
    elif product_code == "6bc":
        parts.append(participant("base", "reagent", "Et3N", e, "triethylamine", "CCN(CC)CC"))
    product_name = {
        "6ba": "methyl 2-(4-phenylbut-1-en-3-yn-2-yl)hex-2(E)-enoate",
        "6bb": "Sonogashira dienyne 6bb (R = n-Bu)",
        "6bc": "Sonogashira dienyne 6bc bearing a tertiary alcohol",
        "6bd": "Negishi coupling product 6bd (phenyl)",
        "6be": "Negishi coupling product 6be (1(E)-hexenyl)",
        "6bf": "Negishi coupling product 6bf (n-butyl)",
    }[product_code]
    product_amounts = [amount("isolated_mass", 44.1, "mg", ev(3))] if detailed else []
    parts.append(participant("product", "product", product_code, e, product_name, None, product_amounts))
    conditions = []
    for name, value, source in temperatures:
        conditions.append(field(name, value, source))
    if detailed:
        conditions += [field("time", q(24, "h"), ev(3)), field("atmosphere", "nitrogen", ev(3)), field("operation", "stirred until complete conversion as monitored by TLC", ev(3)),
                       field("workup", "diluted with 10 mL Et2O; quenched with 5 mL water; aqueous layer extracted with diethyl ether (3 × 25 mL); combined organic layer dried over Na2SO4; evaporated", ev(3)),
                       field("purification", "silica-gel column chromatography, petroleum ether/diethyl ether 30:1", ev(3))]
    else:
        conditions += missing_conditions("time", "atmosphere", "workup", "purification")
    outcomes = [field("scheme_reported_yield", q(scheme_yield, "%"), ev(3), ["product"])]
    unresolved = ["Product connectivity/stereochemistry remains unverified."]
    if prose_yield is not None and prose_yield != scheme_yield:
        outcomes.append(field("prose_reported_yield", q(prose_yield, "%"), ev(2) + ev(3), ["product"]))
        unresolved.insert(0, f"Scheme 2 reports {scheme_yield}% while the prose reports {prose_yield}% for {product_code}; both are retained.")
    basis = "isolated after column chromatography" if detailed else None
    outcomes.append(field("yield_measurement_basis", basis, ev(3) if basis else (), ["product"]))
    if not detailed:
        unresolved.append("Time, atmosphere, workup, purification, and yield measurement basis are not reported in the supplied main text.")
    records.append(record(suffix, "reported_experiment", e, parts, [{"step_id": reaction_type, "participant_ids": [p["entity_id"] for p in parts], "conditions": conditions}], outcomes, unresolved=unresolved))


SONO_CATS = [
    ("pd", "PdCl2(PPh3)2", "bis(triphenylphosphine)palladium(II) dichloride", 5, None),
    ("cui", "CuI", "copper(I) iodide", 10, "[Cu]I"),
]
NEG_CATS = [("pd", "Pd(PPh3)4", "tetrakis(triphenylphosphine)palladium(0)", 5, None)]

coupling_record("scheme2_sonogashira_6ba", "6ba", "sonogashira_coupling", "phenylacetylene", "phenylacetylene", "C#Cc1ccccc1", 2.0, SONO_CATS, [("CH3CN", "acetonitrile", "CC#N", 2)], [("temperature", "r.t.", ev(3))], 87, detailed=True)
coupling_record("scheme2_sonogashira_6bb", "6bb", "sonogashira_coupling", "1-hexyne", "1-hexyne", "C#CCCCC", 2.0, SONO_CATS, [("CH3CN", "acetonitrile", "CC#N", None)], [("temperature", "r.t.", ev(3))], 64)
coupling_record("scheme2_sonogashira_6bc", "6bc", "sonogashira_coupling", "2-methylbut-3-yn-2-ol", "2-methylbut-3-yn-2-ol", "C#CC(O)(C)C", 2.0, SONO_CATS, [("DMSO", "dimethyl sulfoxide", "CS(C)=O", None)], [("temperature", "r.t.", ev(3))], 69)
coupling_record("scheme2_negishi_6bd", "6bd", "negishi_coupling", "PhZnBr", "phenylzinc bromide", None, 4.0, NEG_CATS, [("THF", "tetrahydrofuran", "C1CCOC1", None)], [("initial_temperature", q(0, "°C"), ev(3)), ("final_temperature", "r.t.", ev(3))], 94, prose_yield=86)
coupling_record("scheme2_negishi_6be", "6be", "negishi_coupling", "1(E)-hexenylZnBr", "1(E)-hexenylzinc bromide", None, 4.0, NEG_CATS, [("THF", "tetrahydrofuran", "C1CCOC1", None)], [("initial_temperature", q(-78, "°C"), ev(3)), ("final_temperature", "r.t.", ev(3))], 78, prose_yield=80)
coupling_record("scheme2_negishi_6bf", "6bf", "negishi_coupling", "n-C4H9ZnBr", "n-butylzinc bromide", None, 4.0, NEG_CATS, [("DMF", "N,N-dimethylformamide", "CN(C)C=O", None), ("THF", "tetrahydrofuran", "C1CCOC1", None)], [("temperature", "r.t.", ev(3))], 51, prose_yield=51)


assert len(records) == 44, len(records)
assert len({r["record_id"] for r in records}) == len(records)

raw_path = OUT / "raw_model/records_pages_0001_0004.json"
raw_path.parent.mkdir(parents=True, exist_ok=True)
raw_path.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")

by_page = {
    1: [r["record_id"] for r in records if f"{DOC}:page1:image" in r["evidence_ids"]],
    2: [r["record_id"] for r in records if f"{DOC}:page2:image" in r["evidence_ids"]],
    3: [r["record_id"] for r in records if f"{DOC}:page3:image" in r["evidence_ids"]],
    4: [],
}
coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1,
            "state": "attempted",
            "regions": [
                {"region": "left-column title, graphical abstract, abstract, and introduction", "finding": "The graphical abstract summarizes the present addition-elimination and downstream coupling chemistry; it is linked to the detailed Table 4/Scheme 2 records rather than duplicated. Prose prior-work examples are classified as citations, not present-paper experiments.", "evidence_ids": ev(1)},
                {"region": "upper-right Table 1 reaction header, six rows, and surrounding starting-material prose", "finding": "Six independent preparations of allenols 3a-3f extracted; common 1.2 equiv NaI/SnCl2, DMPU, temperature sequence, row times, and yields retained.", "evidence_ids": ev(1)},
            ],
            "record_ids": by_page[1],
            "unresolved": ["Table 1 gives no row-specific absolute quantities, atmosphere, workup, purification, or yield basis except where the page-3 exact 3a procedure supplies them.", "Literature references were not mined as associated source documents."],
        },
        {
            "page": 2,
            "state": "attempted",
            "regions": [
                {"region": "left column Table 2 and footnote", "finding": "Seven independent solvent/NaI-loading/temperature optimization entries inventoried; entry 5 merged with its identical Table 3/Table 4 appearances. Trace results and the entry-3 blank NaI cell were preserved.", "evidence_ids": ev(2)},
                {"region": "left column Scheme 1", "finding": "One DIBAL-H reduction to 5ba extracted and merged with its exact page-3 procedure; NOE/NOESY stereochemical context retained.", "evidence_ids": ev(2)},
                {"region": "left column Table 3", "finding": "Seven MX-screen entries inventoried; three exact substrate/reagent/product/yield duplicates were merged with Table 4, while four salt-specific conditions remain independent optimization records.", "evidence_ids": ev(2)},
                {"region": "right column Table 4 and footnote", "finding": "All 21 substrate-scope entries extracted independently. The 0%/no-4ea result in entry 13 remains an explicit failed result.", "evidence_ids": ev(2)},
                {"region": "right-column synthetic-application prose", "finding": "Six coupling yields identified and linked to Scheme 2 records; prose/Scheme yield disagreements for 6bd and 6be are retained.", "evidence_ids": ev(2)},
            ],
            "record_ids": by_page[2],
            "unresolved": ["Table 3 reports 3 h for 4bc while Table 4 reports 6 h under otherwise matching conditions.", "Table 2-4 generally omit atmosphere, workup, purification, absolute scale, and yield basis."],
        },
        {
            "page": 3,
            "state": "attempted",
            "regions": [
                {"region": "left column Scheme 2", "finding": "Six distinct present-paper coupling experiments extracted: three Sonogashira products 6ba-6bc and three Negishi products 6bd-6bf.", "evidence_ids": ev(3)},
                {"region": "left/lower experimental section, exact preparation of 3a", "finding": "Exact quantities, staged temperatures/times, dark conditions, workup, chromatography, isolated mass, and 59% yield merged into Table 1 entry 1.", "evidence_ids": ev(3)},
                {"region": "right-column exact preparation of 4aa", "finding": "Exact NaI/3a/TFA quantities, 80 °C/1 h, TLC monitoring, workup, chromatography, mass, and 50% isolated yield merged into Table 4 entry 1.", "evidence_ids": ev(3)},
                {"region": "right-column exact reduction of 4ba and preparation of 6ba", "finding": "Detailed DIBAL-H reduction and Sonogashira coupling procedures merged into the corresponding Scheme 1/Scheme 2 records.", "evidence_ids": ev(3)},
            ],
            "record_ids": by_page[3],
            "unresolved": ["Scheme 2 and its prose disagree on 6bd (94% vs 86%) and 6be (78% vs 80%).", "Only 6ba has a full coupling procedure in the supplied main text; other Scheme 2 cases omit times and operational details."],
        },
        {
            "page": 4,
            "state": "attempted",
            "regions": [
                {"region": "acknowledgment and Supporting Information availability statement", "finding": "No reaction arrow, table, experiment, condition, or result is present. The statement that SI is available online does not establish an associated SI source.", "evidence_ids": ev(4)},
            ],
            "record_ids": [],
            "unresolved": ["Supporting Information is mentioned but was not supplied or explicitly associated; no SI-derived facts were inferred."],
        },
    ],
}
coverage_path = OUT / "coverage/pages_0001_0004.json"
coverage_path.parent.mkdir(parents=True, exist_ok=True)
coverage_path.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

tasks_path = OUT / "tasks.json"
tasks = json.loads(tasks_path.read_text())
for task in tasks:
    if task["document_id"] == DOC and task["task_id"] in {f"{DOC}:page{i}:text" for i in range(1, 5)}:
        task["state"] = "attempted"
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"records": len(records), "raw": str(raw_path), "coverage": str(coverage_path)}, ensure_ascii=False))
