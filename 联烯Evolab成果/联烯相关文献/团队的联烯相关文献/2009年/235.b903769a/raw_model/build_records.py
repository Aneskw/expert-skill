#!/usr/bin/env python3
"""Build evidence-linked machine records for PDF pages 1--6.

This is a source-specific raw extraction artifact.  It intentionally does not
claim review status or verified structures; reaction_tools.merge enforces that
boundary when importing the generated JSON.
"""
from __future__ import annotations

import json
from pathlib import Path


DOC = "doc_cf4c46706b370f7b"
OUT = Path(__file__).with_name("records_pages_0001_0006.json")


def ev(*pages: int) -> list[str]:
    ids: list[str] = []
    for page in pages:
        ids.extend([f"{DOC}:page{page}:image", f"{DOC}:page{page}:text"])
    return ids


def fact(value, evidence=None):
    return {
        "value": value,
        "evidence_ids": [] if value is None else list(evidence or []),
        "verification": "missing" if value is None else "unreviewed",
    }


def qty(number, unit, **extra):
    value = {"number": number, "unit": unit}
    value.update(extra)
    return value


def amount(name, value, evidence):
    return {"name": name, "fact": fact(value, evidence)}


def participant(entity_id, role, label, name, evidence, smiles=None, amounts=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence),
        "smiles": fact(smiles, evidence) if smiles else fact(None),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": amounts or [],
    }


def field(name, value, evidence, targets=None):
    result = {"name": name, "fact": fact(value, evidence)}
    if targets:
        result["target_entity_ids"] = list(targets)
    return result


def step(step_id, participant_ids, conditions):
    return {"step_id": step_id, "participant_ids": list(participant_ids), "conditions": conditions}


def record(suffix, kind, evidence, participants, steps, outcomes, notes=None, unresolved=None):
    return {
        "record_id": f"{DOC}:{suffix}",
        "document_id": DOC,
        "source_reaction_id": suffix,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": list(evidence),
        "participants": participants,
        "steps": steps,
        "outcomes": outcomes,
        "notes": [fact(x, evidence) for x in (notes or [])],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved or [
                "Machine-extracted record requires source review; depicted structures and stereochemistry are unverified.",
                "No supporting-information file was provided or explicitly associated.",
            ],
        },
    }


STARTERS = {
    "1a": ("4-phenyl-3-butyn-2-ol", "CC(O)C#Cc1ccccc1"),
    "1b": ("1-phenyl-1-octyn-3-ol", "CCCCCC(O)C#Cc1ccccc1"),
    "1c": ("1,3-diphenylprop-2-yn-1-ol", "OC(c1ccccc1)C#Cc1ccccc1"),
    "1d": ("2-methyl-4-phenyl-3-butyn-2-ol", "CC(O)(C)C#Cc1ccccc1"),
    "1e": ("4-(3-methylphenyl)-3-butyn-2-ol", "CC(O)C#Cc1cccc(C)c1"),
    "1f": ("4-(4-methylphenyl)-3-butyn-2-ol", "CC(O)C#Cc1ccc(C)cc1"),
    "1g": ("4-(4-methoxyphenyl)-3-butyn-2-ol", "CC(O)C#Cc1ccc(OC)cc1"),
    "1h": ("4-(4-chlorophenyl)-3-butyn-2-ol", "CC(O)C#Cc1ccc(Cl)cc1"),
    "1i": ("4-(2-pyridyl)-3-butyn-2-ol", "CC(O)C#Cc1ccccn1"),
    "1j": ("4-(2-thienyl)-3-butyn-2-ol", "CC(O)C#Cc1cccs1"),
    "1k": ("4-(trifluoromethylphenyl)-3-butyn-2-ol (positional assignment unresolved)", None),
}


def starter(label, evidence, role="reactant", entity_id="starting_material", amounts=None):
    name, smiles = STARTERS[label]
    return participant(entity_id, role, label, name, evidence, smiles, amounts)


records = []

# Page 1, Scheme 1: four separately reported preparations.  Only 1a is
# operationally detailed on page 4; 1b--d remain scheme-level partial records.
scheme1 = [
    ("1a", "acetaldehyde", "CC=O", 84),
    ("1b", "hexanal", "CCCCCC=O", 67),
    ("1c", "benzaldehyde", "O=Cc1ccccc1", 81),
    ("1d", "acetone", "CC(=O)C", 94),
]
for label, carbonyl, carbonyl_smiles, yield_value in scheme1:
    evidence = ev(1, 4) if label == "1a" else ev(1)
    phenyl_amounts = []
    carbonyl_amounts = []
    mg_amounts = []
    etbr_amounts = []
    thf_amounts = []
    product_amounts = []
    conditions = [field("temperature", qty(55, "°C"), evidence)]
    if label == "1a":
        phenyl_amounts = [amount("volume", qty(11.0, "mL"), evidence), amount("amount", qty(0.10, "mol"), evidence), amount("mass", qty(10.20, "g"), evidence)]
        carbonyl_amounts = [amount("volume", qty(4.0, "mL"), evidence), amount("amount", qty(0.07, "mol"), evidence), amount("mass", qty(3.12, "g"), evidence)]
        mg_amounts = [amount("mass", qty(2.88, "g"), evidence), amount("amount", qty(0.12, "mol"), evidence)]
        etbr_amounts = [amount("volume", qty(8.96, "mL"), evidence), amount("amount", qty(0.12, "mol"), evidence), amount("mass", qty(13.09, "g"), evidence)]
        thf_amounts = [amount("volume", qty(120, "mL"), evidence)]
        product_amounts = [amount("mass", qty(8.72, "g"), evidence)]
        conditions += [field("stage_1_time", qty(1.5, "h"), evidence), field("stage_2_time", qty(2, "h"), evidence), field("operation", "Grignard formation, phenylethyne addition, then carbonyl addition", evidence)]
    parts = [
        participant("phenylethyne", "reactant", "PhC≡CH", "phenylethyne", evidence, "C#Cc1ccccc1", phenyl_amounts),
        participant("carbonyl", "reactant", carbonyl, carbonyl, evidence, carbonyl_smiles, carbonyl_amounts),
        participant("magnesium", "reagent", "Mg", "magnesium", evidence, "[Mg]", mg_amounts),
        participant("ethyl_bromide", "reagent", "EtBr", "ethyl bromide", evidence, "CCBr", etbr_amounts),
        participant("thf", "solvent", "THF", "tetrahydrofuran", evidence, "C1CCOC1", thf_amounts),
        starter(label, evidence, role="product", entity_id="product", amounts=product_amounts),
    ]
    if label == "1a":
        parts.insert(-2, participant("iodine_initiator", "reagent", "I2", "iodine (initiation crystals)", evidence, "II"))
    outcomes = [field("isolated_yield", qty(yield_value, "%"), evidence, ["product"]), field("yield_measurement_basis", "isolated", evidence)]
    records.append(record(f"scheme1_{label}", "reported_experiment", evidence, parts, [step("preparation", [p["entity_id"] for p in parts[:-1]], conditions)], outcomes,
                          unresolved=None if label == "1a" else ["Scheme reports identity and yield but omits batch quantities, duration, workup and purification.", "Depicted structures are machine interpretations and remain unverified.", "No supporting-information file was provided or explicitly associated."]))

# Page 1, Table 1: seven Sonogashira preparations.  Entry 1 is detailed on page 4.
table1 = [
    (1, "3-iodotoluene", "Ic1cccc(C)c1", "1e", 10.5, 89),
    (2, "4-iodotoluene", "Ic1ccc(C)cc1", "1f", 10.3, 91),
    (3, "4-iodoanisole", "COc1ccc(I)cc1", "1g", 11.2, 78),
    (4, "1-chloro-4-iodobenzene", "Clc1ccc(I)cc1", "1h", 11.2, 93),
    (5, "2-iodopyridine", "Ic1ccccn1", "1i", 11.5, 94),
    (6, "2-bromothiophene", "Brc1cccs1", "1j", 15.4, 58),
    (7, "1-bromo-2-(trifluoromethyl)benzene", "Brc1ccccc1C(F)(F)F", "1k", 12.4, 74),
]
for entry, aryl_halide, aryl_smiles, product_label, duration, yield_value in table1:
    evidence = ev(1, 4) if entry == 1 else ev(1)
    aryl_amounts = []
    alkynol_amounts = []
    cui_amounts = [amount("catalyst_loading", qty(2, "mol%"), evidence)]
    pd_amounts = [amount("catalyst_loading", qty(2, "mol%"), evidence)]
    dmso_amounts = []
    et3n_amounts = []
    product_amounts = []
    if entry == 1:
        aryl_amounts = [amount("mass", qty(1.0959, "g"), evidence), amount("amount", qty(5.0, "mmol"), evidence)]
        alkynol_amounts = [amount("mass", qty(0.6983, "g"), evidence), amount("amount", qty(9.9, "mmol"), evidence)]
        cui_amounts += [amount("mass", qty(0.0193, "g"), evidence), amount("amount", qty(0.10, "mmol"), evidence)]
        pd_amounts += [amount("mass", qty(0.0675, "g"), evidence), amount("amount", qty(0.096, "mmol"), evidence)]
        dmso_amounts = [amount("volume", qty(12, "mL"), evidence)]
        et3n_amounts = [amount("volume", qty(10, "mL"), evidence)]
        product_amounts = [amount("mass", qty(0.7166, "g"), evidence)]
    parts = [
        participant("aryl_halide", "reactant", aryl_halide, aryl_halide, evidence, aryl_smiles, aryl_amounts),
        participant("butynol", "reactant", "3-butyn-2-ol", "3-butyn-2-ol", evidence, "CC(O)C#C", alkynol_amounts),
        participant("pd_catalyst", "catalyst", "Pd(PPh3)2Cl2", "bis(triphenylphosphine)palladium(II) dichloride", evidence, None, pd_amounts),
        participant("cui", "catalyst", "CuI", "copper(I) iodide", evidence, "[Cu]I", cui_amounts),
        participant("dmso", "solvent", "DMSO", "dimethyl sulfoxide", evidence, "CS(C)=O", dmso_amounts),
        participant("et3n", "reagent", "Et3N", "triethylamine", evidence, "CCN(CC)CC", et3n_amounts),
        starter(product_label, evidence, role="product", entity_id="product", amounts=product_amounts),
    ]
    conditions = [field("temperature", {"minimum": 40, "maximum": 45, "unit": "°C", "raw_text": "40–45 °C"}, evidence), field("time", qty(duration, "h"), evidence)]
    outcomes = [field("isolated_yield", qty(yield_value, "%"), evidence, ["product"]), field("yield_measurement_basis", "isolated", evidence)]
    unresolved = None if entry == 1 else ["Table row does not provide individual batch quantities, atmosphere, workup or purification.", "Depicted product structure is unverified.", "No supporting-information file was provided or explicitly associated."]
    if entry == 7:
        unresolved.append("Table 1 assigns 1k as the 2-CF3C6H4 isomer, while Table 3 assigns the same 1k label as 3-CF3C6H4; no positional structure is encoded globally.")
    records.append(record(f"table1_entry{entry}", "substrate_scope_entry", evidence, parts, [step("sonogashira_coupling", [p["entity_id"] for p in parts[:-1]], conditions)], outcomes, unresolved=unresolved))

# Page 2 equation 1 / page 4 detailed kinetic resolution: one batch, two products.
evidence = ev(1, 2, 4)
parts = [
    starter("1a", evidence, amounts=[amount("mass", qty(4.0032, "g"), evidence)]),
    participant("vinyl_acetate", "reactant", "vinyl acetate", "vinyl acetate", evidence, "CC(=O)OC=C", [amount("volume", qty(100, "mL"), evidence)]),
    participant("novozym", "catalyst", "Novozym-435", "Novozym-435", evidence, None, [amount("mass", qty(0.7008, "g"), evidence)]),
    participant("s_1a", "product", "(S)-1a", "(S)-4-phenyl-3-butyn-2-ol", evidence, "C[C@H](O)C#Cc1ccccc1", [amount("mass", qty(1.6780, "g"), evidence)]),
    participant("r_acetate", "product", "(R)-1a acetate", "(R)-4-phenyl-3-butyn-2-ol acetate", evidence, "C[C@H](OC(C)=O)C#Cc1ccccc1", [amount("mass", qty(2.7696, "g"), evidence)]),
]
steps = [step("enzymatic_kinetic_resolution", ["starting_material", "vinyl_acetate", "novozym"], [field("temperature", qty(60, "°C"), evidence), field("time", qty(23.3, "h"), evidence), field("operation", "shaking; monitored by TLC", evidence), field("purification", "filtration, ether washing, evaporation, then flash chromatography on silica gel", evidence)])]
outcomes = [
    field("isolated_yield_s_1a", qty(42, "%"), evidence, ["s_1a"]),
    field("product_ee_s_1a", qty(99, "%", qualifier="gt", raw_text=">99% ee"), evidence, ["s_1a"]),
    field("isolated_yield_r_acetate", qty(54, "%"), evidence, ["r_acetate"]),
    field("product_ee_r_acetate", qty(71, "%"), evidence, ["r_acetate"]),
    field("yield_measurement_basis", "isolated after flash chromatography", evidence),
]
records.append(record("eq1_kinetic_resolution", "reported_experiment", evidence, parts, steps, outcomes, notes=["The acetate ee was determined after conversion to the corresponding alcohol."]))

# Page 2, Table 2 optimization rows.
table2 = [
    (1, 3.5, "CuI", 0.5, 12.1, 46, 9, 33),
    (2, 3.5, "CuCl", 1.0, 11.6, 44, 9, 40),
    (3, 4.5, "CuCl", 1.0, 11.6, 87, 3, 8),
    (4, 6.0, "CuCl", 1.0, 11.6, 95, 2, 2),
    (5, 6.0, "CuI", 1.0, 12.0, 70, 8, 8),
    (6, 6.0, "CuBr", 1.0, 12.0, 70, 10, 8),
    (7, 6.0, "CuCl", 1.5, 13.2, 95, 3, 5),
    (8, 6.0, "CuCl", 0.5, 13.2, 88, 4, 6),
    (9, 6.0, "CuCl", 2.0, 13.0, 85, 4, 13),
]
for entry, grig_eq, copper, copper_eq, duration, y2a, y3a, recovery in table2:
    evidence = ev(2)
    parts = [
        starter("1a", evidence),
        participant("grignard", "reactant", "n-C5H11MgBr", "n-pentylmagnesium bromide", evidence, "[Mg+](Br)CCCCC", [amount("equivalents", qty(grig_eq, "equiv"), evidence), amount("concentration", qty(1, "M"), evidence)]),
        participant("copper", "reagent", copper, {"CuI": "copper(I) iodide", "CuCl": "copper(I) chloride", "CuBr": "copper(I) bromide"}[copper], evidence, None, [amount("equivalents", qty(copper_eq, "equiv"), evidence)]),
        participant("toluene", "solvent", "toluene", "toluene", evidence, "Cc1ccccc1"),
        participant("thf", "solvent", "THF", "tetrahydrofuran", evidence, "C1CCOC1"),
        participant("nh4cl", "reagent", "sat. NH4Cl (aq.)", "saturated aqueous ammonium chloride", evidence),
        participant("e2a", "product", "E-2a", "3-(n-pentyl)-4-phenylbut-3(E)-en-2-ol", evidence, "CC(O)C(CCCCC)=Cc1ccccc1"),
        participant("z3a", "product", "Z-3a", "4-phenyl-3(Z)-nonen-2-ol", evidence, "CC(O)C=C(c1ccccc1)CCCCC"),
    ]
    steps = [
        step("carbometallation", ["starting_material", "grignard", "copper", "toluene", "thf"], [field("initial_temperature", qty(-78, "°C"), evidence), field("warm_to", "r.t.", evidence), field("time", qty(duration, "h"), evidence)]),
        step("hydrolysis", ["nh4cl"], [field("initial_temperature", qty(-40, "°C"), evidence), field("warm_to", "r.t.", evidence)]),
    ]
    outcomes = [
        field("nmr_yield_e2a", qty(y2a, "%"), evidence, ["e2a"]),
        field("nmr_yield_z3a", qty(y3a, "%"), evidence, ["z3a"]),
        field("recovered_starting_material_yield", qty(recovery, "%"), evidence, ["starting_material"]),
        field("yield_measurement_basis", "NMR", evidence),
    ]
    records.append(record(f"table2_entry{entry}", "optimization_entry", evidence, parts, steps, outcomes, unresolved=["Optimization table does not give batch scale, individual solvent volume, workup or purification.", "Product structures and E/Z assignments are unverified machine interpretations.", "No supporting-information file was provided or explicitly associated."]))

# Page 2, Table 3 scope rows.  Entries 1 and 11 have detailed procedures on page 4.
table3 = [
    (1, "1a", 8.7, "I2", "Z-4a", 85, 83, None),
    (2, "1h", 10.0, "I2", "Z-4b", 82, 78, None),
    (3, "1k", 11.2, "I2", "Z-4c", 83, 75, None),
    (4, "1e", 17.3, "I2", "Z-4d", 58, 49, None),
    (5, "1f", 14.0, "I2", "Z-4e", 68, 66, None),
    (6, "1g", 13.3, "I2", "Z-4f", 55, 56, None),
    (7, "1j", 10.0, "H+", "E-2b", 87, 83, None),
    (8, "1i", 10.0, "H+", "E-2c", 82, 78, None),
    (9, "1c", 12.0, "H+", "E-2d", 48, 45, None),
    (10, "1b", 12.8, "I2", "Z-4g", 32, 31, 38),
    (11, "1a", 11.6, "H+", "E-2a", 95, 90, None),
    (12, "1a", 16.3, "D2O", "E-5a", 96, 88, None),
    (13, "1a", 16.3, "NBS", "Z-6a", 54, 54, None),
]
product_names = {
    "Z-4a": "4-iodo-3-(n-pentyl)-4-phenyl-3(Z)-buten-2-ol",
    "E-2a": "3-(n-pentyl)-4-phenylbut-3(E)-en-2-ol",
    "E-2b": "3-(n-pentyl)-4-(2-thienyl)-3(E)-buten-2-ol",
    "E-2c": "3-(n-pentyl)-4-(2-pyridyl)-3(E)-buten-2-ol",
    "E-2d": "2-(n-pentyl)-1,3-diphenyl-2(E)-propen-1-ol",
    "Z-4g": "1-iodo-2-(n-pentyl)-1-phenyl-1(Z)-octen-3-ol",
    "E-5a": "4-deutero-3-(n-pentyl)-4-phenyl-3(E)-buten-2-ol",
    "Z-6a": "4-bromo-3-(n-pentyl)-4-phenyl-3(Z)-buten-2-ol",
}
product_smiles = {"Z-4a": "CC(O)C(CCCCC)=C(I)c1ccccc1", "E-2a": "CC(O)C(CCCCC)=Cc1ccccc1", "Z-6a": "CC(O)C(CCCCC)=C(Br)c1ccccc1"}
for entry, start_label, duration, electrophile, product_label, nmr_yield, isolated_yield, recovery in table3:
    evidence = ev(2, 4, 5) if entry == 1 else (ev(2, 4) if entry == 11 else ev(2))
    cu_eq = 2 if entry == 6 else 1
    grig_eq = 9 if entry == 6 else 6
    parts = [
        starter(start_label, evidence, amounts=[amount("reaction_scale", qty(1, "mmol"), evidence)]),
        participant("grignard", "reactant", "n-C5H11MgBr", "n-pentylmagnesium bromide", evidence, None, [amount("equivalents", qty(grig_eq, "equiv"), evidence), amount("concentration", qty(1, "M"), evidence)]),
        participant("cucl", "reagent", "CuCl", "copper(I) chloride", evidence, "[Cu]Cl", [amount("equivalents", qty(cu_eq, "equiv"), evidence)]),
        participant("toluene", "solvent", "toluene", "toluene", evidence, "Cc1ccccc1", [amount("volume", qty(1.5, "mL"), evidence)]),
        participant("thf", "solvent", "THF", "tetrahydrofuran", evidence, "C1CCOC1"),
    ]
    if entry == 3:
        parts[0]["name"] = fact("4-(3-trifluoromethylphenyl)-3-butyn-2-ol (Table 3 assignment)", evidence)
    quench_id = "quench"
    if electrophile == "I2":
        q_amounts = [amount("equivalents", qty(9 if entry == 6 else 6, "equiv"), evidence)] if entry in (1, 6) else []
        parts.append(participant(quench_id, "reagent", "I2", "iodine", evidence, "II", q_amounts))
    elif electrophile == "H+":
        parts.append(participant(quench_id, "reagent", "sat. NH4Cl (aq.)", "saturated aqueous ammonium chloride", evidence))
    elif electrophile == "D2O":
        parts.append(participant(quench_id, "reagent", "D2O", "deuterium oxide", evidence, "[2H]O[2H]"))
    else:
        parts.append(participant(quench_id, "reagent", "NBS", "N-bromosuccinimide", evidence, "O=C1CCC(=O)N1Br"))
    if entry == 11:
        # Page 4 provides the exact batch used for the isolated E-2a result.
        parts[0]["amounts"] += [amount("mass", qty(0.1477, "g"), evidence)]
        parts[1]["amounts"] += [amount("amount", qty(6, "mmol"), evidence), amount("volume", qty(6, "mL"), evidence)]
        parts[2]["amounts"] += [amount("mass", qty(0.1005, "g"), evidence), amount("amount", qty(1.0, "mmol"), evidence)]
    if entry == 1:
        parts[0]["amounts"] += [amount("mass", qty(0.1469, "g"), evidence)]
        parts[1]["amounts"] += [amount("amount", qty(6, "mmol"), evidence), amount("volume", qty(6, "mL"), evidence)]
        parts[2]["amounts"] += [amount("mass", qty(0.1007, "g"), evidence), amount("amount", qty(1.0, "mmol"), evidence)]
        parts[-1]["amounts"] += [amount("mass", qty(1.5243, "g"), evidence), amount("amount", qty(6.0, "mmol"), evidence)]
    product_amounts = []
    if entry == 11:
        product_amounts = [amount("mass", qty(0.1984, "g"), evidence)]
    elif entry == 1:
        product_amounts = [amount("mass", qty(0.2878, "g"), evidence)]
    parts.append(participant("product", "product", product_label, product_names.get(product_label, f"product {product_label}"), evidence, product_smiles.get(product_label), product_amounts))
    quench_temp = -30 if entry == 4 else (0 if electrophile == "H+" else -40)
    steps = [
        step("carbometallation", ["starting_material", "grignard", "cucl", "toluene", "thf"], [field("initial_temperature", qty(-78, "°C"), evidence), field("warm_to", "r.t.", evidence), field("time", qty(duration, "h"), evidence)]),
        step("electrophile_quench", [quench_id], [field("initial_temperature", qty(quench_temp, "°C"), evidence), field("warm_to", "r.t." if electrophile != "H+" else None, evidence)]),
    ]
    outcomes = [field("nmr_yield", qty(nmr_yield, "%"), evidence, ["product"]), field("isolated_yield", qty(isolated_yield, "%"), evidence, ["product"]), field("yield_measurement_basis", "NMR before isolation; parenthesized value isolated", evidence)]
    if recovery is not None:
        outcomes.append(field("recovered_starting_material_yield", qty(recovery, "%"), evidence, ["starting_material"]))
    if entry == 12:
        outcomes.append(field("deuterium_incorporation", qty(99, "%"), evidence, ["product"]))
    unresolved = None
    if entry == 3:
        unresolved = ["Table 3 assigns 1k as the 3-CF3C6H4 isomer, while Table 1 assigns the same label as 2-CF3C6H4; no positional structure is encoded globally.", "Depicted product structure and stereochemistry remain unverified.", "No supporting-information file was provided or explicitly associated."]
    records.append(record(f"table3_entry{entry}", "substrate_scope_entry", evidence, parts, steps, outcomes, unresolved=unresolved))

# Page 2 equation 2: low-yield tertiary substrate result.
evidence = ev(2)
parts = [
    starter("1d", evidence),
    participant("grignard", "reactant", "n-C5H11MgBr", "n-pentylmagnesium bromide", evidence, None, [amount("equivalents", qty(6, "equiv"), evidence), amount("concentration", qty(1, "M"), evidence)]),
    participant("cucl", "reagent", "CuCl", "copper(I) chloride", evidence, "[Cu]Cl", [amount("equivalents", qty(1, "equiv"), evidence)]),
    participant("toluene", "solvent", "toluene", "toluene", evidence, "Cc1ccccc1"),
    participant("nh4cl", "reagent", "sat. NH4Cl (aq.)", "saturated aqueous ammonium chloride", evidence),
    participant("product", "product", "2e", "tertiary allylic alcohol 2e", evidence, "CC(O)(C)C(CCCCC)=Cc1ccccc1"),
]
steps = [step("carbometallation", ["starting_material", "grignard", "cucl", "toluene"], [field("initial_temperature", qty(-78, "°C"), evidence), field("warm_to", "r.t.", evidence), field("time", qty(11.6, "h"), evidence)]), step("hydrolysis", ["nh4cl"], [field("temperature", qty(0, "°C"), evidence)])]
outcomes = [field("nmr_yield", qty(5, "%"), evidence, ["product"]), field("recovered_starting_material_yield", qty(84, "%"), evidence, ["starting_material"]), field("yield_measurement_basis", "NMR", evidence)]
records.append(record("eq2_tertiary_alcohol_1d", "reported_experiment", evidence, parts, steps, outcomes))

# Page 3, Table 4 Grignard scope followed by iodination.
table4 = [
    (1, "EtMgBr", "ethylmagnesium bromide", 16.3, 1.2, "Z-4h", 80, 82),
    (2, "i-PrMgBr", "isopropylmagnesium bromide", 12.1, 1.5, "Z-4i", 79, 83),
    (3, "allylMgCl", "allylmagnesium chloride", 22.0, 0.8, "Z-4j", None, 49),
    (4, "PhMgCl", "phenylmagnesium chloride", 14.0, 1.0, "Z-4k", None, 69),
    (5, "PhMgBr", "phenylmagnesium bromide", 14.0, 1.0, "Z-4k", 58, 63),
    (6, "4-MeC6H4MgBr", "4-methylphenylmagnesium bromide", 20.7, 1.5, "Z-4l", 86, 83),
    (7, "4-MeOC6H4MgBr", "4-methoxyphenylmagnesium bromide", 13.0, 1.0, "Z-4m", 80, 73),
]
for entry, grig_label, grig_name, t1, t2, product_label, nmr_yield, isolated_yield in table4:
    evidence = ev(3)
    parts = [
        starter("1a", evidence, amounts=[amount("reaction_scale", qty(1, "mmol"), evidence)]),
        participant("grignard", "reactant", grig_label, grig_name, evidence, None, [amount("equivalents", qty(6, "equiv"), evidence)]),
        participant("cucl", "reagent", "CuCl", "copper(I) chloride", evidence, "[Cu]Cl", [amount("equivalents", qty(1, "equiv"), evidence)]),
        participant("toluene", "solvent", "toluene", "toluene", evidence, "Cc1ccccc1", [amount("volume", qty(1.5, "mL"), evidence)]),
        participant("thf", "solvent", "THF", "tetrahydrofuran", evidence, "C1CCOC1"),
        participant("iodine", "reagent", "I2", "iodine", evidence, "II"),
        participant("product", "product", product_label, f"iodoallylic alcohol {product_label}", evidence),
    ]
    stage1_conditions = [field("time", qty(t1, "h"), evidence)]
    if entry == 6:
        stage1_conditions += [field("initial_temperature", "r.t.", evidence), field("time_at_room_temperature", qty(13.1, "h"), evidence), field("heated_temperature", qty(40, "°C"), evidence), field("time_at_heated_temperature", qty(7.6, "h"), evidence)]
    else:
        stage1_conditions += [field("initial_temperature", qty(-78, "°C"), evidence), field("warm_to", "r.t.", evidence)]
    steps = [step("carbometallation", ["starting_material", "grignard", "cucl", "toluene", "thf"], stage1_conditions), step("iodination", ["iodine"], [field("initial_temperature", qty(-40, "°C"), evidence), field("warm_to", "r.t.", evidence), field("time", qty(t2, "h"), evidence)])]
    nmr_value = qty(nmr_yield, "%") if nmr_yield is not None else "table dash (–); crude yield could not be determined by NMR analysis"
    outcomes = [field("nmr_yield", nmr_value, evidence, ["product"]), field("isolated_yield", qty(isolated_yield, "%"), evidence, ["product"]), field("yield_measurement_basis", "NMR before isolation; parenthesized value isolated", evidence)]
    records.append(record(f"table4_entry{entry}", "substrate_scope_entry", evidence, parts, steps, outcomes))

# Page 3 equation 3: optically active starting material, distinct batch.
evidence = ev(3)
parts = [
    participant("starting_material", "reactant", "(S)-1a", "(S)-4-phenyl-3-butyn-2-ol", evidence, "C[C@H](O)C#Cc1ccccc1", [amount("starting_material_ee", qty(99, "%", qualifier="gt", raw_text=">99% ee"), evidence)]),
    participant("grignard", "reactant", "n-C5H11MgBr", "n-pentylmagnesium bromide", evidence, None, [amount("equivalents", qty(6, "equiv"), evidence), amount("concentration", qty(1, "M"), evidence)]),
    participant("cucl", "reagent", "CuCl", "copper(I) chloride", evidence, "[Cu]Cl", [amount("equivalents", qty(1, "equiv"), evidence)]),
    participant("toluene", "solvent", "toluene", "toluene", evidence, "Cc1ccccc1"),
    participant("thf", "solvent", "THF", "tetrahydrofuran", evidence, "C1CCOC1"),
    participant("iodine", "reagent", "I2", "iodine", evidence, "II"),
    participant("product", "product", "(S)-Z-4a", "optically active (S)-Z-4a", evidence),
]
steps = [step("carbometallation", ["starting_material", "grignard", "cucl", "toluene", "thf"], [field("initial_temperature", qty(-78, "°C"), evidence), field("warm_to", "r.t.", evidence), field("time", qty(12.2, "h"), evidence)]), step("iodination", ["iodine", "thf"], [field("initial_temperature", qty(-40, "°C"), evidence), field("warm_to", "r.t.", evidence), field("time", qty(2, "h"), evidence)])]
outcomes = [field("isolated_yield", qty(73, "%"), evidence, ["product"]), field("product_ee", qty(99, "%", qualifier="gt", raw_text=">99% ee"), evidence, ["product"]), field("yield_measurement_basis", "isolated", evidence)]
records.append(record("eq3_optically_active_s_1a", "reported_experiment", evidence, parts, steps, outcomes))

# Page 3, Table 5 allylic bromide trapping scope. Entry 1 is detailed on page 5.
table5 = [
    (1, "n-C5H11MgBr", "n-pentylmagnesium bromide", 12.2, 4.3, "allyl bromide", "E-7a", 94, 85),
    (2, "CH3MgCl", "methylmagnesium chloride", 18.0, 3.0, "allyl bromide", "E-7b", 92, 91),
    (3, "i-PrMgBr", "isopropylmagnesium bromide", 12.4, 4.8, "allyl bromide", "E-7c", 89, 82),
    (4, "c-HexylMgCl", "cyclohexylmagnesium chloride", 12.0, 7.4, "allyl bromide", "E-7d", 78, 76),
    (5, "vinylMgCl", "vinylmagnesium chloride", 18.0, 3.2, "allyl bromide", "E-7e", 82, 77),
    (6, "n-C5H11MgBr", "n-pentylmagnesium bromide", 12.2, 6.0, "2-bromoallyl bromide", "E-7f", 54, 48),
    (7, "n-C5H11MgBr", "n-pentylmagnesium bromide", 10.3, 3.3, "2-(n-butyl)allyl bromide", "E-7g", 85, 79),
]
for entry, grig_label, grig_name, t1, t2, allyl_name, product_label, nmr_yield, isolated_yield in table5:
    evidence = ev(3, 5) if entry == 1 else ev(3)
    grig_amounts = [amount("equivalents", qty(6, "equiv"), evidence)]
    allyl_amounts = [amount("equivalents", qty(6, "equiv"), evidence)]
    start_amounts = [amount("reaction_scale", qty(1, "mmol"), evidence)]
    cu_amounts = [amount("equivalents", qty(1, "equiv"), evidence)]
    toluene_amounts = [amount("volume", qty(1.5, "mL"), evidence)]
    product_amounts = []
    if entry == 1:
        start_amounts += [amount("mass", qty(0.1499, "g"), evidence)]
        cu_amounts += [amount("mass", qty(0.1041, "g"), evidence), amount("amount", qty(1.1, "mmol"), evidence)]
        grig_amounts += [amount("amount", qty(6, "mmol"), evidence), amount("volume", qty(6, "mL"), evidence), amount("concentration", qty(1, "M"), evidence)]
        allyl_amounts = [amount("volume", qty(0.54, "mL"), evidence), amount("mass", qty(0.7549, "g"), evidence), amount("amount", qty(6.2, "mmol"), evidence), amount("equivalents", qty(6.2, "equiv"), evidence)]
        product_amounts = [amount("mass", qty(0.2250, "g"), evidence)]
    parts = [
        starter("1a", evidence, amounts=start_amounts),
        participant("grignard", "reactant", grig_label, grig_name, evidence, None, grig_amounts),
        participant("cucl", "reagent", "CuCl", "copper(I) chloride", evidence, "[Cu]Cl", cu_amounts),
        participant("toluene", "solvent", "toluene", "toluene", evidence, "Cc1ccccc1", toluene_amounts),
        participant("thf", "solvent", "THF", "tetrahydrofuran", evidence, "C1CCOC1"),
        participant("allylic_bromide", "reactant", allyl_name, allyl_name, evidence, None, allyl_amounts),
        participant("product", "product", product_label, f"allylic alcohol {product_label}", evidence, "CC(O)C(CCCCC)=C(c1ccccc1)CC=C" if entry == 1 else None, product_amounts),
    ]
    steps = [step("carbometallation", ["starting_material", "grignard", "cucl", "toluene", "thf"], [field("initial_temperature", qty(-78, "°C"), evidence), field("warm_to", "r.t.", evidence), field("time", qty(t1, "h"), evidence)]), step("allylic_bromide_trapping", ["allylic_bromide", "thf"], [field("initial_temperature", qty(-40, "°C"), evidence), field("warm_to", "r.t.", evidence), field("time", qty(t2, "h"), evidence)])]
    outcomes = [field("nmr_yield", qty(nmr_yield, "%"), evidence, ["product"]), field("isolated_yield", qty(isolated_yield, "%"), evidence, ["product"]), field("yield_measurement_basis", "NMR before isolation; parenthesized value isolated", evidence)]
    records.append(record(f"table5_entry{entry}", "substrate_scope_entry", evidence, parts, steps, outcomes))

# Page 3, Table 6 Pd-catalyzed Kumada-type trapping. Entry 1 is detailed on page 5.
table6 = [
    (1, 11.0, 20.0, "PhI", "iodobenzene", "8a", 80, 75),
    (2, 12.2, 24.3, "3-MeC6H4I", "3-iodotoluene", "Z-8b", 77, 75),
    (3, 12.0, 12.0, "4-MeOC6H4I", "4-iodoanisole", "Z-8c", 80, 74),
    (4, 13.0, 12.0, "4-ClC6H4I", "1-chloro-4-iodobenzene", "Z-8d", 71, 69),
    (5, 16.3, 23.5, "(E)-n-C4H9CH=CHI", "1(E)-hexenyl iodide", "E-8e", 56, 48),
]
for entry, t1, t2, iodide_label, iodide_name, product_label, nmr_yield, isolated_yield in table6:
    evidence = ev(3, 5) if entry == 1 else ev(3)
    start_amounts = [amount("reaction_scale", qty(1, "mmol"), evidence)]
    cu_amounts = [amount("equivalents", qty(1, "equiv"), evidence)]
    grig_amounts = [amount("equivalents", qty(6, "equiv"), evidence)]
    iodide_amounts = [amount("equivalents", qty(6, "equiv"), evidence)]
    pd_amounts = [amount("catalyst_loading", qty(2, "mol%"), evidence)]
    product_amounts = []
    if entry == 1:
        start_amounts += [amount("mass", qty(0.1458, "g"), evidence)]
        cu_amounts += [amount("mass", qty(0.0992, "g"), evidence), amount("amount", qty(1.0, "mmol"), evidence)]
        grig_amounts += [amount("amount", qty(6, "mmol"), evidence)]
        iodide_amounts += [amount("mass", qty(1.2537, "g"), evidence), amount("amount", qty(6.2, "mmol"), evidence)]
        pd_amounts += [amount("mass", qty(0.0237, "g"), evidence), amount("amount", qty(0.02, "mmol"), evidence)]
        product_amounts = [amount("mass", qty(0.2204, "g"), evidence)]
    parts = [
        starter("1a", evidence, amounts=start_amounts),
        participant("grignard", "reactant", "n-C5H11MgBr", "n-pentylmagnesium bromide", evidence, None, grig_amounts),
        participant("cucl", "reagent", "CuCl", "copper(I) chloride", evidence, "[Cu]Cl", cu_amounts),
        participant("toluene", "solvent", "toluene", "toluene", evidence, "Cc1ccccc1", [amount("volume", qty(1.5, "mL"), evidence)]),
        participant("thf", "solvent", "THF", "tetrahydrofuran", evidence, "C1CCOC1"),
        participant("organic_iodide", "reactant", iodide_label, iodide_name, evidence, None, iodide_amounts),
        participant("pd_catalyst", "catalyst", "Pd(PPh3)4", "tetrakis(triphenylphosphine)palladium(0)", evidence, None, pd_amounts),
        participant("product", "product", product_label, f"coupling product {product_label}", evidence, "CC(O)C(CCCCC)=C(c1ccccc1)c1ccccc1" if entry == 1 else None, product_amounts),
    ]
    steps = [step("carbometallation", ["starting_material", "grignard", "cucl", "toluene", "thf"], [field("initial_temperature", qty(-78, "°C"), evidence), field("warm_to", "r.t.", evidence), field("time", qty(t1, "h"), evidence)]), step("pd_catalyzed_coupling", ["organic_iodide", "pd_catalyst"], [field("temperature", qty(80, "°C"), evidence), field("time", qty(t2, "h"), evidence)])]
    outcomes = [field("nmr_yield", qty(nmr_yield, "%"), evidence, ["product"]), field("isolated_yield", qty(isolated_yield, "%"), evidence, ["product"]), field("yield_measurement_basis", "NMR before isolation; parenthesized value isolated", evidence)]
    if entry == 1:
        outcomes.append(field("nmr_yield_protonolysis_byproduct", qty(7, "%"), evidence))
    records.append(record(f"table6_entry{entry}", "substrate_scope_entry", evidence, parts, steps, outcomes))

# Page 3 equation 4 / page 5 detailed carbonylation.
evidence = ev(3, 5)
parts = [
    participant("z4a", "reactant", "Z-4a", "4-iodo-3-(n-pentyl)-4-phenyl-3(Z)-buten-2-ol", evidence, "CC(O)C(CCCCC)=C(I)c1ccccc1", [amount("mass", qty(0.1372, "g"), evidence), amount("amount", qty(0.40, "mmol"), evidence)]),
    participant("co", "reactant", "CO", "carbon monoxide", evidence, "[C-]#[O+]", [amount("pressure", "1 atm", evidence)]),
    participant("pd_catalyst", "catalyst", "Pd(PPh3)4", "tetrakis(triphenylphosphine)palladium(0)", evidence, None, [amount("mass", qty(0.0242, "g"), evidence), amount("amount", qty(0.02, "mmol"), evidence), amount("catalyst_loading", qty(5, "mol%"), evidence)]),
    participant("et3n", "reagent", "Et3N", "triethylamine", evidence, "CCN(CC)CC", [amount("mass", qty(0.0828, "g"), evidence), amount("amount", qty(0.82, "mmol"), evidence), amount("equivalents", qty(2, "equiv"), evidence)]),
    participant("acetonitrile", "solvent", "CH3CN", "acetonitrile", evidence, "CC#N", [amount("volume", qty(4, "mL"), evidence)]),
    participant("product", "product", "9a", "5-methyl-4-(n-pentyl)-3-phenyl-2(5H)-furanone", evidence, "CC1OC(=O)C(c2ccccc2)=C1CCCCC", [amount("mass", qty(0.0656, "g"), evidence)]),
]
steps = [step("carbonylation", ["z4a", "co", "pd_catalyst", "et3n", "acetonitrile"], [field("atmosphere", "CO after freeze–pump–thaw degassing", evidence), field("temperature", qty(70, "°C"), evidence), field("time", qty(15.3, "h"), evidence)]), step("workup_and_purification", [], [field("workup", "water quench; ether extraction; sequential 5% HCl, saturated NaHCO3, and brine washes; Na2SO4 drying", evidence), field("purification", "silica chromatography, petroleum ether/ethyl acetate 20/1", evidence)])]
outcomes = [field("isolated_yield", qty(67, "%"), evidence, ["product"]), field("yield_measurement_basis", "isolated after chromatography", evidence)]
records.append(record("eq4_carbonylation_9a", "reported_experiment", evidence, parts, steps, outcomes))


assert len(records) == 56, len(records)
OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
print(f"wrote {len(records)} records to {OUT}")
