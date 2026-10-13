#!/usr/bin/env python3
"""Build evidence-linked machine records for Zhang et al., Chem. Eur. J. 2012, PDF pages 1--6."""

import json
from pathlib import Path


DOC = "doc_74b3f5c116def6bc"
ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "runs/current/raw_model/records_pages_0001_0006.json"
COVERAGE = ROOT / "runs/current/coverage/pages_0001_0006.json"
TASKS = ROOT / "runs/current/tasks.json"


def ev(*pages):
    result = []
    for page in pages:
        result.extend([f"{DOC}:page{page}:text", f"{DOC}:page{page}:image"])
    return result


def fact(value, evidence=None):
    return {
        "value": value,
        "evidence_ids": list(evidence or []) if value is not None else [],
        "verification": "missing" if value is None else "unreviewed",
    }


def field(name, value, evidence=None, targets=None):
    item = {"name": name, "fact": fact(value, evidence)}
    if targets:
        item["target_entity_ids"] = targets
    return item


def q(number, unit, **extra):
    value = {"number": number, "unit": unit}
    value.update(extra)
    return value


def participant(entity_id, role, label, evidence, name=None, smiles=None, amounts=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence) if name is not None else fact(None),
        "smiles": fact(smiles, evidence) if smiles is not None else fact(None),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": amounts or [],
    }


def step(step_id, participant_ids, conditions):
    return {"step_id": step_id, "participant_ids": participant_ids, "conditions": conditions}


def record(rid, kind, pages, participants=None, steps=None, outcomes=None, notes=None, unresolved=None):
    evidence = ev(*pages)
    return {
        "record_id": f"{DOC}:{rid}",
        "document_id": DOC,
        "source_reaction_id": rid,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": evidence,
        "participants": participants or [],
        "steps": steps or [],
        "outcomes": outcomes or [],
        "notes": [fact(text, evidence) for text in (notes or [])],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved or [],
        },
    }


def amount(name, number, unit, evidence, **extra):
    return field(name, q(number, unit, **extra), evidence)


def agent(entity_id, role, label, evidence, name=None, smiles=None, quantities=None):
    return participant(entity_id, role, label, evidence, name, smiles, quantities or [])


SMILES = {
    "NIS": "O=C1CCC(=O)N1I",
    "N-iodophthalimide": "O=C1N(I)C(=O)c2ccccc12",
    "Cs2CO3": "[Cs+].[Cs+].[O-]C([O-])=O",
    "CH2Cl2": "ClCCl",
    "p-TsCl": "Cc1ccc(S(=O)(=O)Cl)cc1",
    "pyridine": "n1ccccc1",
    "NaCN": "[Na+].[C-]#N",
    "DMSO": "CS(C)=O",
    "NaOH": "[Na+].[OH-]",
    "EtOH": "CCO",
    "H2O": "O",
    "Et2O": "CCOCC",
    "THF": "C1CCOC1",
    "LiAlH4": "[Li+].[AlH4-]",
    "LiBr": "[Li+].[Br-]",
    "Me2S": "CSC",
    "TBAF": "CCCC[N+](CCCC)(CCCC)CCCC.[F-]",
    "H2": "[H][H]",
    "KOH": "[K+].[OH-]",
    "MeCN": "CC#N",
    "CCl4": "ClC(Cl)(Cl)Cl",
    "I2": "II",
}


def simple(entity_id, role, label, evidence, quantities=None, name=None):
    return agent(entity_id, role, label, evidence, name or label, SMILES.get(label), quantities)


def allenoic(label, evidence, entity_id="substrate", amounts=None):
    names = {
        "(Ra)-3a": "(Ra)-dodeca-4,5-dienoic acid",
        "(Sa)-3a": "(Sa)-dodeca-4,5-dienoic acid",
        "(Ra)-3b": "(Ra)-trideca-4,5-dienoic acid",
        "(Ra)-3c": "(Ra)-hexadeca-4,5,15-trienoic acid",
        "(Ra,R)-3d": "(Ra,R)-3-methylocta-4,5-dienoic acid",
        "(Ra,R)-3e": "(Ra,R)-3-methyldeca-4,5-dienoic acid",
        "(Ra,R)-3f": "(Ra,R)-3-allyldeca-4,5-dienoic acid",
        "(Sa,S)-3f": "(Sa,S)-3-allyldeca-4,5-dienoic acid",
        "(Sa,S)-3g": "(Sa,S)-3,7-dimethylocta-4,5-dienoic acid",
        "(R)-3h": "(R)-3-methyl-6-phenylhexa-4,5-dienoic acid",
        "(S)-3h": "(S)-3-methyl-6-phenylhexa-4,5-dienoic acid",
    }
    candidates = {
        "(Ra)-3a": "CCCCCCC=C=CCCC(=O)O",
        "(Sa)-3a": "CCCCCCC=C=CCCC(=O)O",
        "(Ra)-3b": "CCCCCCCC=C=CCCC(=O)O",
        "(Ra,R)-3d": "CCC=C=CC(C)CC(=O)O",
        "(Ra,R)-3e": "CCCCC=C=CC(C)CC(=O)O",
        "(Sa,S)-3g": "CC(C)C=C=CC(C)CC(=O)O",
        "(R)-3h": "CC1CC(=O)OC1/C(I)=C/c1ccccc1",
    }
    # The 3h candidate is intentionally omitted: the dictionary value above would describe product 5h, not acid 3h.
    smiles = None if label in ("(R)-3h", "(S)-3h") else candidates.get(label)
    return participant(entity_id, "reactant", label, evidence, names.get(label), smiles, amounts)


def iod_reagent(label, evidence, equivalents=2, entity_id="iodination_reagent"):
    names = {"6": "N-iodosuccinimide", "7": "N-iodophthalimide", "8": "N-iodo-2,3-naphthalenedicarboximide"}
    smiles = {"6": SMILES["NIS"], "7": SMILES["N-iodophthalimide"], "8": None}
    return participant(entity_id, "reagent", label, evidence, names[label], smiles[label], [amount("equivalents", equivalents, "equiv", evidence)])


def product(entity_id, label, evidence, name=None, amounts=None):
    return participant(entity_id, "product", label, evidence, name, None, amounts)


records = []

# Page 1: generic overview and two explicitly prior-work examples in Scheme 2.
e1 = ev(1)
records.append(record(
    "scheme1_generic_anti_cyclization", "general_scheme", [1],
    participants=[
        participant("generic_allene", "reactant", "generic 2-allenyl nucleophile 1", e1),
        participant("generic_electrophile", "reagent", "E+Y−", e1),
        participant("generic_product_2", "product", "five-membered product 2 (n=1)", e1),
        participant("generic_product_A", "product", "endo-mode product A (n>2)", e1),
        participant("generic_product_B", "product", "exo-mode product B (n>2)", e1),
    ],
    notes=["Scheme 1 is a generic reaction-class overview with R groups and variable n, not a uniquely specified reported experiment."],
    unresolved=["Generic structures do not support unique molecular structures or experimental quantities."],
))

parts = [
    participant("substrate_R_3", "reactant", "(R)-4-allenoic acid 3", e1),
    simple("reagent_i2", "reagent", "I2", e1, [amount("equivalents", 1.5, "equiv", e1)]),
    participant("solvent_cyclohexane", "solvent", "cyclohexane", e1, "cyclohexane", "C1CCCCC1"),
    product("product_rac_4", "rac-4", e1),
]
records.append(record(
    "scheme2_prior_I2_cationic", "literature_example", [1], parts,
    [step("iodolactonization", ["substrate_R_3", "reagent_i2", "solvent_cyclohexane"], [
        field("temperature", "r.t.", e1), field("time", q(74, "h"), e1)
    ])],
    [field("Z_to_E_ratio", "98:2", e1, ["product_rac_4"]), field("product_ee", q(0, "%"), e1, ["product_rac_4"])],
    ["Scheme 2 marks this arrow as a previous report and illustrates a cationic pathway."],
    ["Yield, scale, workup, purification, and measurement bases are not stated on this page."],
))

parts = [
    participant("substrate_R_3", "reactant", "(R)-4-allenoic acid 3", e1),
    simple("reagent_nis", "reagent", "NIS", e1, [amount("equivalents", 2.0, "equiv", e1)], "N-iodosuccinimide"),
    simple("base_cs2co3", "reagent", "Cs2CO3", e1, [amount("equivalents", 1.0, "equiv", e1)]),
    simple("solvent_ch2cl2", "solvent", "CH2Cl2", e1),
    product("product_S_Z_5", "(S)-(Z)-5", e1),
    product("product_R_E_5", "(R)-(E)-5", e1),
]
records.append(record(
    "scheme2_prior_NIS_anti", "literature_example", [1], parts,
    [step("electrophilic_anti_cyclization", [p["entity_id"] for p in parts[:4]], [field("temperature", q(-60, "°C"), e1), field("time", None)])],
    [field("product_ratio_S_Z_5_to_R_E_5", "79:21–85:15", e1, ["product_S_Z_5", "product_R_E_5"])],
    ["Scheme 2 marks this NIS/Cs2CO3 arrow as a previous report."],
    ["Time, yield, scale, workup, purification, and ratio measurement basis are not stated on this page."],
))


# Page 2 Table 1: each I+ source row is a distinct optimization experiment.
table1 = [
    (1, "6", 13, 86, "78:22", 98, 98, False),
    (2, "6", 18, 99, "78:22", 98, 97, True),
    (3, "7", 16, 71, "93:7", 98, 96, True),
    (4, "8", 12, 85, "97:3", 98, 97, True),
]
for entry, source, duration, yld, ratio, ee_z, ee_e, with_base in table1:
    evidence = ev(2)
    parts = [allenoic("(Ra)-3a", evidence), iod_reagent(source, evidence)]
    if with_base:
        parts.append(simple("base_cs2co3", "reagent", "Cs2CO3", evidence, [amount("equivalents", 1.0, "equiv", evidence)]))
    parts += [simple("solvent_ch2cl2", "solvent", "CH2Cl2", evidence),
              product("product_S_Z_5a", "(S)-(Z)-5a", evidence, "(S)-5-(1-iodo-(Z)-octenyl)-4,5-dihydro-2(3H)-furanone"),
              product("product_R_E_5a", "(R)-(E)-5a", evidence, "(R)-5-(1-iodo-(E)-octenyl)-4,5-dihydro-2(3H)-furanone")]
    inputs = [p["entity_id"] for p in parts if p["role"] in ("reactant", "reagent", "solvent")]
    notes = ["Table 1 reports one experiment per row under a shared iodination-reagent stoichiometry and CH2Cl2/−60 °C header; the stoichiometry is structured on the reagent participant."]
    if not with_base:
        notes.append("Footnote a states that this row was performed without Cs2CO3.")
    records.append(record(
        f"table1_entry{entry}", "optimization_entry", [2], parts,
        [step("iodolactonization", inputs, [field("temperature", q(-60, "°C"), evidence), field("reaction_time", q(duration, "h"), evidence)])],
        [field("reported_yield_5a", q(yld, "%"), evidence, ["product_S_Z_5a", "product_R_E_5a"]),
         field("product_ratio_S_Z_to_R_E", ratio, evidence, ["product_S_Z_5a", "product_R_E_5a"]),
         field("product_S_Z_ee", q(ee_z, "%"), evidence, ["product_S_Z_5a"]),
         field("product_R_E_ee", q(ee_e, "%"), evidence, ["product_R_E_5a"]),
         field("yield_measurement_basis", None), field("ratio_measurement_basis", None)],
        notes,
        ["Reaction scale, atmosphere, workup, purification, and measurement bases are absent from Table 1.",
         "Product structures and stereochemistry remain machine-unverified; no SI was supplied or explicitly associated."],
    ))

records.append(record(
    "scheme3_iodination_reagent_concept", "general_scheme", [2],
    participants=[participant("reagent_6", "reagent", "6", ev(2), "N-iodosuccinimide", SMILES["NIS"]),
                  participant("reagent_7", "reagent", "7", ev(2), "N-iodophthalimide", SMILES["N-iodophthalimide"]),
                  participant("reagent_8", "reagent", "8", ev(2), "N-iodo-2,3-naphthalenedicarboximide")],
    notes=["Scheme 3 is a reagent-design concept showing increasing steric demand; Table 1 contains the actual row-wise experiments."],
    unresolved=["The connectivity candidate for reagent 8 is left null pending expert verification of the fused imide drawing."],
))

# Scheme 4 contains three distinct current-paper scope experiments.
scheme4 = [
    ("scheme4a_Sa_3a", "(Sa)-3a", "(R)-(Z)-5a", "(S)-(E)-5a", 12, 75, "96:4", 97, 97),
    ("scheme4b_Ra_3b", "(Ra)-3b", "(S)-(Z)-5b", "(R)-(E)-5b", 11, 74, "96:4", 99, 98),
    ("scheme4b_Ra_3c", "(Ra)-3c", "(S)-(Z)-5c", "(R)-(E)-5c", 9, 74, "96:4", 92, 90),
]
for rid, sub, major, minor, duration, yld, ratio, major_ee, minor_ee in scheme4:
    evidence = ev(2)
    parts = [allenoic(sub, evidence), iod_reagent("8", evidence),
             simple("base_cs2co3", "reagent", "Cs2CO3", evidence, [amount("equivalents", 1.0, "equiv", evidence)]),
             simple("solvent_ch2cl2", "solvent", "CH2Cl2", evidence),
             product("product_major", major, evidence), product("product_minor", minor, evidence)]
    records.append(record(
        rid, "substrate_scope_entry", [2], parts,
        [step("iodolactonization", [p["entity_id"] for p in parts[:4]], [field("temperature", q(-60, "°C"), evidence), field("reaction_time", q(duration, "h"), evidence)])],
        [field("reported_yield", q(yld, "%"), evidence, ["product_major", "product_minor"]),
         field("Z_to_E_ratio", ratio, evidence, ["product_major", "product_minor"]),
         field("major_product_ee", q(major_ee, "%"), evidence, ["product_major"]),
         field("minor_product_ee", q(minor_ee, "%"), evidence, ["product_minor"]),
         field("yield_measurement_basis", None), field("ratio_measurement_basis", None)],
        ["Scheme 4 reports the combined product outcome and stereochemical values for this substrate."],
        ["Scale, atmosphere, workup, purification, and measurement bases are not stated in Scheme 4.",
         "Complex structures and stereochemical encodings remain machine-unverified."],
    ))

records.append(record(
    "scheme5_cis_lactone_strategy", "general_scheme", [2],
    participants=[participant("generic_chiral_allenoic_acid", "reactant", "(Ra,R)-3", ev(2)),
                  participant("generic_intermediate_9", "unspecified_agent", "π-allylic cation 9 (previous work)", ev(2)),
                  participant("generic_intermediate_Z10", "unspecified_agent", "iodonium intermediate Z-10 (this approach)", ev(2)),
                  participant("generic_trans_product", "product", "trans-(Z)-5", ev(2)),
                  participant("generic_cis_product", "product", "cis-(Z)-5", ev(2))],
    notes=["Scheme 5 contrasts a previous 1,2-chiral-induction concept with the chirality-transfer strategy; it is not a uniquely specified batch experiment."],
    unresolved=["Generic R groups and conceptual intermediates do not support experiment-specific quantities or verified structures."],
))


# Page 3 Table 2: five distinct substrate rows.
table2 = [
    (1, "(Ra,R)-3d", "(4R,5S)-(Z)-5d", "(4R,5R)-(E)-5d", 10, 70, ">97:3", 99),
    (2, "(Ra,R)-3e", "(4R,5S)-(Z)-5e", "(4R,5R)-(E)-5e", 8, 71, ">98:2", 99),
    (3, "(Ra,R)-3f", "(4R,5S)-(Z)-5f", "(4R,5R)-(E)-5f", 14, 83, ">99:1", {"number": 99, "unit": "%", "qualifier": "gt", "raw_text": ">99%"}),
    (4, "(Sa,S)-3f", "(4S,5R)-(Z)-5f", "(4S,5S)-(E)-5f", 10, 88, ">99:1", {"number": 99, "unit": "%", "qualifier": "gt", "raw_text": ">99%"}),
    (5, "(Sa,S)-3g", "(4S,5R)-(Z)-5g", "(4S,5S)-(E)-5g", 11, 68, ">99:1", 99),
]
for entry, sub, major, minor, duration, yld, ratio, ee_value in table2:
    evidence = ev(3, 4) if entry in (1, 2) else ev(3)
    parts = [allenoic(sub, evidence), iod_reagent("8", evidence),
             simple("base_cs2co3", "reagent", "Cs2CO3", evidence, [amount("equivalents", 1.0, "equiv", evidence)]),
             simple("solvent_ch2cl2", "solvent", "CH2Cl2", evidence),
             product("product_Z", major, evidence), product("product_E", minor, evidence)]
    outcomes = [field("isolated_yield_Z_5", q(yld, "%"), evidence, ["product_Z"]),
                field("Z_to_E_ratio", ratio, evidence, ["product_Z", "product_E"]),
                field("Z_product_ee", q(ee_value, "%") if isinstance(ee_value, int) else ee_value, evidence, ["product_Z"]),
                field("yield_measurement_basis", None), field("ratio_measurement_basis", None)]
    notes = ["Table 2 reports the major Z product, isolated yield, Z/E ratio, and ee for one substrate row."]
    if entry == 2:
        outcomes.append(field("scheme9_reported_Z_product_ee", q(97, "%"), ev(4), ["product_Z"]))
        notes.append("Scheme 9 on page 4 prints 97% ee for 5e, whereas Table 2 prints 99% ee; both source values are retained without reconciliation.")
    records.append(record(
        f"table2_entry{entry}", "substrate_scope_entry", [3, 4] if entry in (1, 2) else [3], parts,
        [step("iodolactonization", [p["entity_id"] for p in parts[:4]], [field("temperature", q(-60, "°C"), evidence), field("reaction_time", q(duration, "h"), evidence)])],
        outcomes, notes,
        ["Reaction scale, atmosphere, workup, purification, and measurement bases are not stated in Table 2.",
         "Complex structures and stereochemistry remain machine-unverified."],
    ))


# Scheme 6 and the detailed page-6 text are reconciled into isolated-stage records.
e36 = ev(3, 6)
parts = [
    participant("reactant_11", "reactant", "(3S,4S)-11", e36, "(3S,4S)-3-methyl-4-ethynyloxetan-2-one"),
    participant("phmgbr", "reactant", "PhMgBr", e36, "phenylmagnesium bromide", "[Mg+](Br)c1ccccc1", [amount("amount", 50, "mmol", e36), amount("volume", 50, "mL", e36), amount("concentration", 1.0, "M", e36), amount("equivalents", 5.0, "equiv", ev(3))]),
    simple("libr", "reagent", "LiBr", e36, [amount("mass", 1.4022, "g", e36), amount("amount", 16.1, "mmol", e36), amount("equivalents", 1.5, "equiv", ev(3))]),
    participant("cubr_me2s", "reagent", "CuBr·Me2S", e36, "copper(I) bromide dimethyl sulfide complex", None, [amount("mass", 3.2787, "g", e36), amount("amount", 15.9, "mmol", e36), amount("equivalents", 1.5, "equiv", ev(3))]),
    simple("me2s", "solvent", "Me2S", e36, [amount("volume", 8, "mL", e36)]),
    simple("thf", "solvent", "THF", e36, [amount("volume", 60, "mL", e36)]),
    participant("beta_allenoic_acid", "unspecified_agent", "β-allenoic acid intermediate", e36),
    simple("lialh4", "reagent", "LiAlH4", e36, [amount("mass", 0.5230, "g", e36), amount("amount", 13.8, "mmol", e36)]),
    simple("et2o", "solvent", "Et2O", e36, [amount("total_reported_volume", 30, "mL", e36)]),
    product("product_12", "(Ra,S)-12", e36, "(Ra,S)-3-methyl-6-phenylhexa-4,5-dien-1-ol", [amount("isolated_mass", 1.1236, "g", e36)]),
]
parts[0]["amounts"] = [amount("mass", 1.1165, "g", e36), amount("amount", 10.2, "mmol", e36)]
records.append(record(
    "scheme6_prep_12", "reported_experiment", [3, 6], parts,
    [
        step("organocopper_allene_formation", [p["entity_id"] for p in parts[:6]], [field("atmosphere", "N2", e36), field("temperature", q(-50, "°C"), e36), field("addition_time", q(30, "min"), e36), field("reaction_time_after_addition", q(3.5, "h"), e36), field("workup", "saturated aqueous NH4Cl; acidify with 5% HCl to pH≈1; Et2O extraction; brine wash; Na2SO4 drying; flash chromatography", e36)]),
        step("lialh4_reduction", ["beta_allenoic_acid", "lialh4", "et2o"], [field("atmosphere", "N2", e36), field("initial_temperature", q(0, "°C"), e36), field("warming_operation", "warm to room temperature", e36), field("reaction_time_at_room_temperature", q(1.8, "h"), e36), field("workup", "quench with water at 0 °C; dissolve in 5% HCl; Et2O extraction; NaHCO3/brine washes; Na2SO4 drying", e36), field("purification", "flash silica chromatography, petroleum ether/EtOAc 10:1", e36)]),
    ],
    [field("combined_isolated_yield_over_two_steps", q(64, "%"), e36, ["product_12"]), field("diastereomer_ratio", "11:1", e36, ["product_12"]), field("diastereomer_ratio_measurement_basis", "inverse-gated-decoupling 13C NMR analysis", e36, ["product_12"])],
    ["Scheme 6 summarizes the two arrows; page 6 supplies exact charges and workup. The β-allenoic acid is used directly and has no separate isolated yield."],
    ["Intermediate connectivity and product axial stereochemistry remain machine-unverified; no SI was supplied or associated."],
))

parts = [
    participant("reactant_12", "reactant", "(Ra,S)-12", e36, "(Ra,S)-3-methyl-6-phenylhexa-4,5-dien-1-ol", None, [amount("mass", 1.0636, "g", e36), amount("amount", 6.1, "mmol", e36)]),
    simple("ptscl", "reagent", "p-TsCl", e36, [amount("mass", 3.5204, "g", e36), amount("amount", 18.4, "mmol", e36), amount("equivalents", 3.0, "equiv", ev(3))]),
    simple("pyridine", "solvent", "pyridine", e36, [amount("volume", 6, "mL", e36)]),
    participant("tosylate_intermediate", "unspecified_agent", "tosylate intermediate", e36),
    simple("nacn", "reagent", "NaCN", e36, [amount("mass", 0.4602, "g", e36), amount("amount", 9.4, "mmol", e36)]),
    simple("dmso", "solvent", "DMSO", e36, [amount("volume", 8, "mL", e36)]),
    product("product_13", "(Ra,R)-13", e36, "(Ra,R)-3-methyl-6-phenylhexa-4,5-dienenitrile", [amount("isolated_mass", 0.6734, "g", e36)]),
]
records.append(record(
    "scheme6_prep_13", "reported_experiment", [3, 6], parts,
    [step("tosylation", ["reactant_12", "ptscl", "pyridine"], [field("temperature", "r.t.", ev(3)), field("reaction_time", q(4, "h"), ev(3))]),
     step("cyanation", ["tosylate_intermediate", "nacn", "dmso"], [field("temperature", q(25, "°C"), ev(3)), field("reaction_time", q(18, "h"), ev(3)), field("purification", "silica chromatography, petroleum ether/EtOAc 30:1→20:1", e36)])],
    [field("combined_isolated_yield_over_two_steps", q(60, "%"), e36, ["product_13"]), field("diastereomer_ratio", "11:1", e36, ["product_13"]), field("diastereomer_ratio_measurement_basis", "inverse-gated-decoupling 13C NMR analysis", e36, ["product_13"])],
    ["The tosylate was used without further purification; the reported 60% is over two steps."],
    ["Intermediate and product stereochemical structures remain machine-unverified."],
))

parts = [
    participant("reactant_13", "reactant", "(Ra,R)-13", e36, "(Ra,R)-3-methyl-6-phenylhexa-4,5-dienenitrile", None, [amount("mass", 0.6573, "g", e36), amount("amount", 3.6, "mmol", e36)]),
    simple("naoh", "reagent", "NaOH", e36, [amount("mass", 1.3207, "g", e36), amount("amount", 33.0, "mmol", e36), amount("equivalents", 9.2, "equiv", ev(3))]),
    simple("ethanol", "solvent", "EtOH", e36, [amount("volume", 6, "mL", e36)]),
    simple("water", "solvent", "H2O", e36, [amount("volume", 2.5, "mL", e36)]),
    product("product_R_3h", "(R)-3h", e36, "(R)-3-methyl-6-phenylhexa-4,5-dienoic acid", [amount("isolated_mass", 0.5191, "g", e36)]),
]
records.append(record(
    "scheme6_prep_R_3h", "reported_experiment", [3, 6], parts,
    [step("nitrile_hydrolysis", [p["entity_id"] for p in parts[:4]], [field("temperature", q(80, "°C"), e36), field("reaction_time", q(9, "h"), ev(3)), field("solvent_ratio_EtOH_to_H2O", "2.4:1", ev(3)), field("purification", "silica chromatography, petroleum ether/EtOAc 20:1→10:1→2:1", e36)])],
    [field("isolated_yield", q(72, "%"), e36, ["product_R_3h"]), field("diastereomer_ratio", "1:1", e36, ["product_R_3h"]), field("diastereomer_ratio_measurement_basis", "inverse-gated-decoupling 13C NMR analysis", e36, ["product_R_3h"])],
    ["Axial epimerization gives a 1:1 diastereomeric mixture according to the paper."],
    ["Product stereochemical structure remains machine-unverified."],
))

e3 = ev(3)
parts = [allenoic("(R)-3h", e3), simple("base_cs2co3", "reagent", "Cs2CO3", e3, [amount("equivalents", 1.0, "equiv", e3)]),
         iod_reagent("8", e3), simple("solvent_ch2cl2", "solvent", "CH2Cl2", e3),
         product("product_RR_Z_5h", "(4R,5R)-(Z)-5h", e3)]
records.append(record(
    "scheme6_iodolactonization_R_3h", "substrate_scope_entry", [3], parts,
    [step("base_prestir", ["substrate", "base_cs2co3", "solvent_ch2cl2"], [field("temperature", "r.t.", e3), field("reaction_time", q(1.5, "h"), e3)]),
     step("iodolactonization", ["iodination_reagent"], [field("temperature", q(-80, "°C"), e3), field("reaction_time", q(11.5, "h"), e3)])],
    [field("isolated_yield", q(54, "%"), e3, ["product_RR_Z_5h"]),
     field("diastereomer_ratio", ">99:1", e3, ["product_RR_Z_5h"]),
     field("product_ee", {"number": 99, "unit": "%", "qualifier": "gt", "raw_text": ">99% ee"}, e3, ["product_RR_Z_5h"])],
    ["Scheme 6 reports the staged base pre-stir and addition of reagent 8; the phenyl-substituted substrate gives the trans product by 1,2-chiral induction."],
    ["Scale, atmosphere, workup, purification, and measurement bases are not stated in Scheme 6."],
))

# Scheme 7 is a distinct no-base control; Scheme 8 is proposed rationale.
parts = [allenoic("(Ra,R)-3d", e3), iod_reagent("8", e3), simple("solvent_ch2cl2", "solvent", "CH2Cl2", e3),
         product("product_Z_5d", "(4R,5S)-(Z)-5d", e3), product("product_E_5d", "(4R,5R)-(E)-5d", e3)]
records.append(record(
    "scheme7_no_base_control", "optimization_entry", [3], parts,
    [step("iodolactonization_without_base", [p["entity_id"] for p in parts[:3]], [field("temperature", q(-60, "°C"), e3), field("reaction_time", q(10, "h"), e3)])],
    [field("reported_yield", q(81, "%"), e3, ["product_Z_5d", "product_E_5d"]), field("Z_to_E_ratio", "89:11", e3, ["product_Z_5d", "product_E_5d"]), field("yield_measurement_basis", None), field("ratio_measurement_basis", None)],
    ["The adjacent prose explicitly identifies the absence of Cs2CO3; no base participant is added to this record."],
    ["Scale, atmosphere, workup, purification, and measurement bases are not stated; the minor-product label is retained from the scheme and remains structure-unverified."],
))

records.append(record(
    "scheme8_stereoselectivity_rationale", "mechanism", [3],
    participants=[participant("generic_allenoic_acid_3", "reactant", "allenoic acid 3", e3),
                  participant("reagent_8", "reagent", "8", e3, "N-iodo-2,3-naphthalenedicarboximide"),
                  participant("intermediate_E14", "unspecified_agent", "(E)-14 (disfavored)", e3),
                  participant("intermediate_Z14", "unspecified_agent", "(Z)-14 (favored)", e3),
                  participant("minor_trans_E_5", "product", "minor trans-(E)-5", e3),
                  participant("major_cis_Z_5", "product", "major cis-(Z)-5", e3)],
    notes=["Scheme 8 is a proposed stereochemical rationale involving hydrogen-bonded iodonium intermediates, not an independently observed experiment."],
    unresolved=["Intermediates (E)-14 and (Z)-14 are proposed and not assigned experimental yields or verified structures."],
))


# Page 4 Scheme 9: two downstream, two-stage natural-product syntheses.
for tag, start_label, tbaf_eq, product_label, product_name, yld, product_ee in [
    ("whisky_lactone_15", "(4R,5S)-(Z)-5d", 3.5, "15", "(+)-cis-whisky lactone", 89, 99),
    ("methyl_decanolide_16", "(4R,5S)-(Z)-5e", 3.0, "16", "(+)-cis-3-methyl-4-decanolide", 93, 98),
]:
    evidence = ev(4)
    parts = [product("reactant_iodolactone", start_label, evidence),
             simple("reagent_tbaf", "reagent", "TBAF", evidence, [amount("equivalents", tbaf_eq, "equiv", evidence)]),
             participant("solvent_dmf", "solvent", "DMF", evidence, "N,N-dimethylformamide", "CN(C)C=O"),
             participant("alkynyl_lactone", "unspecified_agent", "alkynyl lactone intermediate shown in Scheme 9", evidence),
             participant("catalyst_pdc", "catalyst", "Pd/C, 10%", evidence, "10% palladium on carbon", None, [amount("palladium_content", 10, "%", evidence)]),
             simple("hydrogen", "reagent", "H2", evidence),
             participant("solvent_etoac", "solvent", "CH3COOEt", evidence, "ethyl acetate", "CCOC(C)=O"),
             product("natural_product", product_label, evidence, product_name)]
    parts[0]["role"] = "reactant"
    records.append(record(
        f"scheme9_{tag}", "reported_experiment", [4], parts,
        [step("TBAF_dehydroiodination", ["reactant_iodolactone", "reagent_tbaf", "solvent_dmf"], [field("temperature", q(25, "°C"), evidence), field("reaction_time", q(5, "h"), evidence)]),
         step("hydrogenation", ["alkynyl_lactone", "catalyst_pdc", "hydrogen", "solvent_etoac"], [field("hydrogen_pressure", "25 atm", evidence), field("temperature", "r.t.", evidence), field("reaction_time", q(23, "h"), evidence)])],
        [field("combined_isolated_yield_over_two_steps", q(yld, "%"), evidence, ["natural_product"]), field("product_ee", q(product_ee, "%"), evidence, ["natural_product"]), field("yield_measurement_basis", None)],
        ["Scheme 9 reports an unisolated alkynyl-lactone intermediate and a combined two-step yield."],
        ["Exact scale, workup, purification, and yield/ee measurement bases are not stated on page 4; the intermediate and product structures remain machine-unverified."],
    ))


# Page 4 detailed three-stage preparation of iodination reagent 8.
e4 = ev(4)
parts = [
    participant("naphthalene_imide", "reactant", "2,3-naphthalenedicarboximide", e4, "2,3-naphthalenedicarboximide", None, [amount("mass", 2.3306, "g", e4), amount("amount", 11.8, "mmol", e4)]),
    simple("koh", "reagent", "KOH", e4, [amount("mass", 0.7399, "g", e4), amount("amount", 13.2, "mmol", e4)]),
    simple("ethanol", "solvent", "EtOH", e4, [amount("solution_volume", 40, "mL", e4)]),
    simple("aqueous_ethanol", "solvent", "EtOH", e4, [amount("aqueous_75_percent_volume", 3, "mL", e4)], "75% aqueous ethanol"),
    participant("potassium_imide", "unspecified_agent", "potassium 2,3-naphthalenedicarboximide", e4),
    participant("pifa", "reagent", "bis(trifluoroacetoxy)iodobenzene", e4, "[bis(trifluoroacetoxy)iodo]benzene", None, [amount("mass", 2.5843, "g", e4), amount("amount", 6.0, "mmol", e4)]),
    simple("mecn", "solvent", "MeCN", e4, [amount("volume", 55, "mL", e4)]),
    participant("hypervalent_intermediate", "unspecified_agent", "phenyliodine(III) bis(2,3-naphthalenedicarboximidate)", e4),
    simple("ccl4", "solvent", "CCl4", e4, [amount("volume", 100, "mL", e4)]),
    simple("iodine", "reagent", "I2", e4, [amount("mass", 3.0462, "g", e4), amount("amount", 12.0, "mmol", e4)]),
    product("product_8", "8", e4, "N-iodo-2,3-naphthalenedicarboximide", [amount("isolated_mass_including_2_percent_imide", 3.2196, "g", e4)]),
]
records.append(record(
    "prep_iodination_reagent_8", "reported_experiment", [4], parts,
    [
        step("potassium_imide_formation", ["naphthalene_imide", "koh", "ethanol", "aqueous_ethanol"], [field("temperature", q(80, "°C"), e4), field("reaction_time", q(10, "min"), e4), field("operation", "filter; wash residue with acetone; dry under vacuum; use crude product immediately", e4)]),
        step("hypervalent_iodine_intermediate_formation", ["potassium_imide", "pifa", "mecn"], [field("reaction_time", q(14, "h"), e4), field("temperature", None), field("operation", "filter suspension; wash residue with MeCN; dry under vacuum; use without purification", e4)]),
        step("N_iodination", ["hypervalent_intermediate", "ccl4", "iodine"], [field("temperature", "r.t.", e4), field("reaction_time", q(23, "h"), e4), field("operation", "filter and wash residue with Et2O", e4)]),
    ],
    [field("combined_isolated_yield_over_three_steps", q(84, "%"), e4, ["product_8"]), field("reported_2_3_naphthalenedicarboximide_impurity", q(2, "%"), e4, ["product_8"])],
    ["The 84% yield is explicitly reported over three steps, and the isolated material includes 2% 2,3-naphthalenedicarboximide."],
    ["The second-stage temperature is not stated; intermediate and product structures remain machine-unverified."],
))


# Pages 5--6: Method a preparations of optically active 4-allenoic acids.
method_a = [
    # rid, pages, start label, start mass/amount, TsCl mass/amount, pyridine, NaCN mass/amount, DMSO,
    # NaOH mass/amount, EtOH, water, product label, product mass, yield, start ee, product dr, purity
    ("prep_Ra_3a", [5], "(Ra)-undeca-3,4-dien-1-ol", 12.0510, (0.072, "mol"), 42.2949, (0.23, "mol"), 90, 5.4104, (0.11, "mol"), 30, 20.0013, (0.50, "mol"), 75, 26, "(Ra)-3a", 10.3239, 73, 99, None, None),
    ("prep_Sa_3a", [5], "(Sa)-undeca-3,4-dien-1-ol", 1.4901, (8.98, "mmol"), 5.2027, (27.24, "mmol"), 10, 0.6631, (13.53, "mmol"), 11, 2.9622, (74.06, "mmol"), 15, 6, "(Sa)-3a", 1.2882, 73, 99, None, None),
    ("prep_Ra_3b", [5], "(Ra)-dodeca-3,4-dien-1-ol", 0.7966, (4.38, "mmol"), 2.5453, (13.33, "mmol"), 6, 0.3213, (6.56, "mmol"), 4, 1.5234, (38.1, "mmol"), 6, 2, "(Ra)-3b", 0.5591, 61, ">99", None, None),
    ("prep_Ra_3c", [5], "(Ra)-pentadeca-3,4,14-trien-1-ol", 1.1863, (5.34, "mmol"), 3.1329, (16.40, "mmol"), 6, 0.4501, (11.25, "mmol"), 10, 2.2006, (55.02, "mmol"), 8, 3, "(Ra)-3c", 0.9852, 74, 96, None, None),
    ("prep_RaR_3d", [5], "(Ra,S)-2-methylhepta-3,4-dien-1-ol", 0.9579, (7.60, "mmol"), 4.4276, (23.18, "mmol"), 10, 0.5601, (11.43, "mmol"), 8, 2.6315, (65.79, "mmol"), 10, 3, "(Ra,R)-3d", 0.5699, 49, None, None, None),
    ("prep_RaR_3e", [5], "(Ra,S)-2-methylnona-3,4-dien-1-ol", 0.9543, (6.20, "mmol"), 3.5935, (18.81, "mmol"), 6, 0.4567, (9.32, "mmol"), 6, 2.1011, (52.53, "mmol"), 5, 2, "(Ra,R)-3e", 0.7890, 70, None, None, None),
    ("prep_RaR_3f", [5, 6], "(Ra,S)-2-allylnona-3,4-dien-1-ol", 1.4171, (7.87, "mmol"), 4.4995, (23.56, "mmol"), 8, 1.1821, (24.12, "mmol"), 8, 3.1441, (78.60, "mmol"), 15, 6, "(Ra,R)-3f", 1.2208, 75, None, None, None),
    ("prep_SaS_3f", [5, 6], "(Sa,R)-2-allylnona-3,4-dien-1-ol", 1.1045, (6.14, "mmol"), 3.4796, (18.22, "mmol"), 6, 0.5911, (12.06, "mmol"), 6, 2.1215, (53.04, "mmol"), 10, 4, "(Sa,S)-3f", 0.9969, 78, None, None, None),
    ("prep_SaS_3g", [5, 6], "(Sa,R)-2,6-dimethylhepta-3,4-dien-1-ol", 0.1838, (1.31, "mmol"), 0.7632, (4.00, "mmol"), 3, 0.0972, (1.98, "mmol"), 3, 0.5133, (12.8, "mmol"), 2.5, 0.8, "(Sa,S)-3g", 0.1552, 70, None, None, None),
    ("prep_S_3h", [5, 6], "(Sa,R)-12", 1.3789, (7.9, "mmol"), 4.6465, (24.3, "mmol"), 8, 1.1773, (24.0, "mmol"), 8, 1.3011, (33.0, "mmol"), 6, 2.5, "(S)-3h", 0.4373, 27, None, "1:1", 91),
]

for (rid, pages, start_label, start_mass, start_amt, ts_mass, ts_amt, py_vol, cn_mass, cn_amt, dmso_vol,
     base_mass, base_amt, etoh_vol, water_vol, prod_label, prod_mass, yld, start_ee, product_dr, purity) in method_a:
    evidence = ev(*pages)
    start_amounts = [amount("mass", start_mass, "g", evidence), amount("amount", start_amt[0], start_amt[1], evidence)]
    if start_ee is not None:
        value = q(start_ee, "%") if isinstance(start_ee, (int, float)) else {"number": 99, "unit": "%", "qualifier": "gt", "raw_text": ">99% ee"}
        start_amounts.append(field("starting_material_ee", value, evidence))
    parts = [
        participant("starting_alcohol", "reactant", start_label, evidence, amounts=start_amounts),
        simple("ptscl", "reagent", "p-TsCl", evidence, [amount("mass", ts_mass, "g", evidence), amount("amount", ts_amt[0], ts_amt[1], evidence)]),
        simple("pyridine", "solvent", "pyridine", evidence, [amount("volume", py_vol, "mL", evidence)]),
        participant("tosylate_intermediate", "unspecified_agent", "crude tosylate intermediate", evidence),
        simple("nacn", "reagent", "NaCN", evidence, [amount("mass", cn_mass, "g", evidence), amount("amount", cn_amt[0], cn_amt[1], evidence)]),
        simple("dmso", "solvent", "DMSO", evidence, [amount("volume", dmso_vol, "mL", evidence)]),
        participant("nitrile_intermediate", "unspecified_agent", "allene nitrile intermediate described in the source", evidence),
        simple("naoh", "reagent", "NaOH", evidence, [amount("mass", base_mass, "g", evidence), amount("amount", base_amt[0], base_amt[1], evidence)]),
        simple("ethanol", "solvent", "EtOH", evidence, [amount("volume", etoh_vol, "mL", evidence)]),
        simple("water", "solvent", "H2O", evidence, [amount("volume", water_vol, "mL", evidence)]),
        product("allenoic_acid_product", prod_label, evidence, None, [amount("isolated_mass", prod_mass, "g", evidence)]),
    ]
    common = ev(5)
    steps = [
        step("tosylation", ["starting_alcohol", "ptscl", "pyridine"], [field("addition_temperature", q(0, "°C"), common), field("reaction_temperature", "r.t.", common), field("reaction_time", q(5, "h"), common), field("workup", "quench with water; Et2O extraction; brine wash; Na2SO4 drying; evaporate; use crude tosylate without purification", common)]),
        step("cyanation", ["tosylate_intermediate", "nacn", "dmso"], [field("temperature", q(20, "°C"), common), field("reaction_time", q(18, "h"), common), field("operation", "aqueous quench/extraction followed by silica chromatography; use nitrile directly in next step", evidence)]),
        step("nitrile_hydrolysis", ["nitrile_intermediate", "naoh", "ethanol", "water"], [field("temperature", q(80, "°C"), common), field("reaction_time", q(5, "h"), common), field("workup", "evaporate solvent; aqueous quench; ether wash; acidify with 5% HCl to pH≈1; Et2O extraction; water/brine washes; Na2SO4 drying", common), field("purification", "silica-gel chromatography; entry-specific petroleum ether/EtOAc or mixed eluent reported in source", evidence)]),
    ]
    outcomes = [field("combined_isolated_yield_over_three_steps", q(yld, "%"), evidence, ["allenoic_acid_product"])]
    if product_dr:
        outcomes.append(field("diastereomer_ratio", product_dr, evidence, ["allenoic_acid_product"]))
        outcomes.append(field("diastereomer_ratio_measurement_basis", "inverse-gated-decoupling 13C NMR analysis", evidence, ["allenoic_acid_product"]))
    if purity is not None:
        outcomes.append(field("reported_purity", q(purity, "%"), evidence, ["allenoic_acid_product"]))
        outcomes.append(field("purity_measurement_basis", "1H NMR analysis", evidence, ["allenoic_acid_product"]))
    notes = ["The entry explicitly follows Method a; shared operation/time/temperature details are therefore linked to page 5 while entry-specific charges and outcome use the local page evidence."]
    if rid in ("prep_RaR_3e", "prep_RaR_3f", "prep_SaS_3f", "prep_SaS_3g", "prep_S_3h"):
        notes.append("The source prose contains apparent intermediate-name inconsistencies (octa/deca/allyl labels); the printed final product label is retained and intermediate SMILES is left null.")
    records.append(record(
        rid, "reported_experiment", pages, parts, steps, outcomes, notes,
        ["Atmosphere is not stated for Method a; intermediate structures and final stereochemistry remain machine-unverified.",
         "No SI was supplied or explicitly associated."],
    ))


assert len(records) == 36, len(records)

page1_ids = [f"{DOC}:scheme1_generic_anti_cyclization", f"{DOC}:scheme2_prior_I2_cationic", f"{DOC}:scheme2_prior_NIS_anti"]
table1_ids = [f"{DOC}:table1_entry{i}" for i in range(1, 5)]
scheme4_ids = [f"{DOC}:scheme4a_Sa_3a", f"{DOC}:scheme4b_Ra_3b", f"{DOC}:scheme4b_Ra_3c"]
table2_ids = [f"{DOC}:table2_entry{i}" for i in range(1, 6)]
scheme6_ids = [f"{DOC}:scheme6_prep_12", f"{DOC}:scheme6_prep_13", f"{DOC}:scheme6_prep_R_3h", f"{DOC}:scheme6_iodolactonization_R_3h"]
method_ids = [f"{DOC}:{row[0]}" for row in method_a]

coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1, "state": "attempted",
            "regions": [
                {"region": "page 1 title, abstract, introduction, and SI availability footnote", "finding": "Article metadata and reaction-class claims were inspected. The page advertises online supporting information, but no SI file was supplied or explicitly associated, so no SI evidence was imported.", "evidence_ids": ev(1)},
                {"region": "page 1 lower-right Scheme 1", "finding": "Generic electrophilic anti-cyclization overview with variable R groups and n; classified as a general scheme rather than a batch experiment.", "evidence_ids": ev(1)},
                {"region": "page 1 bottom-right Scheme 2", "finding": "Two arrows are explicitly marked previous reports: I2/cyclohexane gives rac-4 and NIS/Cs2CO3 gives an (S)-(Z)-5/(R)-(E)-5 mixture. They are retained as literature examples, while the question-mark 'this report' arrow has no result and is not invented as an experiment.", "evidence_ids": ev(1)},
            ],
            "record_ids": page1_ids,
            "unresolved": ["The previous-report examples omit scale, workup, purification, and some yields/times.", "Generic structures are not uniquely resolved."],
        },
        {
            "page": 2, "state": "attempted",
            "regions": [
                {"region": "page 2 left-center Table 1, reaction header, entries 1–4, and footnote a", "finding": "Four distinct I+ source optimization experiments were retained row-by-row, including the no-Cs2CO3 footnote, times, yields, product ratios, and product-specific ee values.", "evidence_ids": ev(2)},
                {"region": "page 2 lower-left Scheme 3", "finding": "NIS-to-phthalimide-to-naphthalene-imide reagent-design concept; classified as a general scheme, with the actual tests represented by Table 1 rows.", "evidence_ids": ev(2)},
                {"region": "page 2 upper-right Scheme 4", "finding": "Three current-paper chirality-transfer experiments were retained separately: (Sa)-3a, (Ra)-3b, and (Ra)-3c, with their row-specific times, yields, ratios, and ee values.", "evidence_ids": ev(2)},
                {"region": "page 2 lower-right Scheme 5", "finding": "Conceptual comparison of previous 1,2-chiral induction and the new chirality-transfer approach; classified as a general scheme, not a unique experiment.", "evidence_ids": ev(2)},
            ],
            "record_ids": [*table1_ids, f"{DOC}:scheme3_iodination_reagent_concept", *scheme4_ids, f"{DOC}:scheme5_cis_lactone_strategy"],
            "unresolved": ["Table/Scheme rows omit scale, workup, purification, and measurement bases.", "Complex structures and stereochemical encodings remain machine-unverified."],
        },
        {
            "page": 3, "state": "attempted",
            "regions": [
                {"region": "page 3 upper-left Table 2 reaction header and entries 1–5", "finding": "Five distinct cis-lactone scope experiments were retained row-by-row with shared −60 °C/8/Cs2CO3 conditions, row times, isolated yields, Z/E ratios, and ee values.", "evidence_ids": ev(3)},
                {"region": "page 3 lower-left Scheme 6 and adjacent prose", "finding": "The multistage synthesis of (R)-3h was split at isolated products 12, 13, and (R)-3h, then the distinct iodolactonization to 5h was retained; page-6 detailed procedures were merged into the first three records.", "evidence_ids": ev(3)},
                {"region": "page 3 center-right Scheme 7 and base-effect prose", "finding": "A distinct no-Cs2CO3 control of 3d with 8 was retained with 10 h, 81% yield, and 89:11 ratio.", "evidence_ids": ev(3)},
                {"region": "page 3 lower-right Scheme 8", "finding": "Proposed hydrogen-bonded iodonium rationale with (E)-14/(Z)-14; classified as mechanism, not an observed batch.", "evidence_ids": ev(3)},
            ],
            "record_ids": [*table2_ids, *scheme6_ids, f"{DOC}:scheme7_no_base_control", f"{DOC}:scheme8_stereoselectivity_rationale"],
            "unresolved": ["Scope/control rows omit scale and most operational details.", "Proposed intermediates are not experimentally isolated."],
        },
        {
            "page": 4, "state": "attempted",
            "regions": [
                {"region": "page 4 left-column literature comparison and conclusion", "finding": "Prior syntheses of natural lactones are cited literature and were not converted into current-paper experiments; the conclusion adds no independent batch.", "evidence_ids": ev(4)},
                {"region": "page 4 lower-left Scheme 9", "finding": "Two distinct two-stage current-paper routes were retained: 5d to (+)-cis-whisky lactone 15 and 5e to (+)-cis-3-methyl-4-decanolide 16. The preceding 3d/3e iodolactonizations duplicate Table 2 entries 1/2 and were merged as cross-page evidence.", "evidence_ids": ev(4)},
                {"region": "page 4 right-column Experimental Section, preparation of reagent 8", "finding": "One three-stage preparation record was retained with potassium-imide formation, hypervalent-iodine intermediate formation, N-iodination, exact charges, 84% overall yield, and 2% imide impurity.", "evidence_ids": ev(4)},
            ],
            "record_ids": [f"{DOC}:table2_entry1", f"{DOC}:table2_entry2", f"{DOC}:scheme9_whisky_lactone_15", f"{DOC}:scheme9_methyl_decanolide_16", f"{DOC}:prep_iodination_reagent_8"],
            "unresolved": ["Scheme 9 omits exact scale/workup and measurement bases.", "The second-stage temperature in the preparation of 8 is not stated.", "Table 2 and Scheme 9 disagree on the printed ee for 5e (99% versus 97%)."],
        },
        {
            "page": 5, "state": "attempted",
            "regions": [
                {"region": "page 5 upper-left Method a detailed procedure for (Ra)-3a", "finding": "Three-stage tosylation/cyanation/hydrolysis procedure with exact quantities, operations, and 73% overall yield; used as the explicitly referenced common method for later entries.", "evidence_ids": ev(5)},
                {"region": "page 5 remaining left column, preparations of (Sa)-3a and (Ra)-3b", "finding": "Two distinct enantiomer/substrate preparations were retained with entry-specific charges and overall yields.", "evidence_ids": ev(5)},
                {"region": "page 5 right column, preparations of (Ra)-3c, (Ra,R)-3d, (Ra,R)-3e, and beginning of (Ra,R)-3f", "finding": "Four distinct allenoic-acid preparations were identified; the cross-page 3f procedure was merged with its continuation on page 6.", "evidence_ids": ev(5)},
            ],
            "record_ids": [f"{DOC}:prep_Ra_3a", f"{DOC}:prep_Sa_3a", f"{DOC}:prep_Ra_3b", f"{DOC}:prep_Ra_3c", f"{DOC}:prep_RaR_3d", f"{DOC}:prep_RaR_3e", f"{DOC}:prep_RaR_3f", f"{DOC}:prep_SaS_3f", f"{DOC}:prep_SaS_3g", f"{DOC}:prep_S_3h"],
            "unresolved": ["Method a does not state atmosphere.", "Several intermediate names are internally inconsistent; their structures remain label-only."],
        },
        {
            "page": 6, "state": "attempted",
            "regions": [
                {"region": "page 6 left column, completion of (Ra,R)-3f and preparations of (Sa,S)-3f and (Sa,S)-3g", "finding": "Three distinct Method-a preparations were retained with entry-specific charges, product masses, and overall yields; the first is a page-5/page-6 cross-page experiment.", "evidence_ids": ev(6)},
                {"region": "page 6 lower-left through upper-right, detailed preparation of (Ra,S)-12", "finding": "Exact two-stage charges, atmosphere, temperatures, timings, workup, 64% combined yield, and 11:1 dr were merged into the Scheme-6 preparation-of-12 record.", "evidence_ids": ev(6)},
                {"region": "page 6 right column, detailed preparation of (Ra,R)-13 and hydrolysis to (R)-3h", "finding": "The two-step 12-to-13 preparation and the distinct nitrile hydrolysis to (R)-3h were merged with their Scheme-6 records, preserving 60%/72% yields and dr values.", "evidence_ids": ev(6)},
                {"region": "page 6 lower-right, preparation of (S)-3h", "finding": "A separate Method-a preparation of (S)-3h was retained with 27% yield, 91% purity, and 1:1 dr; characterization continues on page 7, which is outside this pass and is not claimed covered.", "evidence_ids": ev(6)},
            ],
            "record_ids": [f"{DOC}:prep_RaR_3f", f"{DOC}:prep_SaS_3f", f"{DOC}:prep_SaS_3g", *scheme6_ids[:3], f"{DOC}:prep_S_3h"],
            "unresolved": ["The (S)-3h characterization continues beyond page 6 and was not reviewed here.", "Intermediate naming inconsistencies and complex stereochemistry require expert review."],
        },
    ],
}

OUT.parent.mkdir(parents=True, exist_ok=True)
COVERAGE.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
COVERAGE.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

tasks = json.loads(TASKS.read_text())
for item in tasks:
    if item.get("document_id") == DOC and item.get("task_id", "").endswith(":text"):
        page = int(item["task_id"].split(":page", 1)[1].split(":", 1)[0])
        if 1 <= page <= 6:
            item["state"] = "attempted"
            item["reason"] = "Original rendered page image and extracted text inspected; coverage ledger records experiment mapping and unresolved details."
TASKS.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"records": len(records), "raw": str(OUT), "coverage": str(COVERAGE)}, ensure_ascii=False))
