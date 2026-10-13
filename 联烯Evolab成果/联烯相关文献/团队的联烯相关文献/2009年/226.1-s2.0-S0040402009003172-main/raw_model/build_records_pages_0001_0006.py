#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = "doc_9b18f28384e009c1"


def ev(*pages):
    out = []
    for page in pages:
        out.extend([f"{DOC}:page{page}:image", f"{DOC}:page{page}:text"])
    return list(dict.fromkeys(out))


def fact(value, evidence=None):
    return {
        "value": value,
        "evidence_ids": [] if value is None else list(evidence or []),
        "verification": "missing" if value is None else "unreviewed",
    }


def fld(name, value, evidence=None, targets=None):
    item = {"name": name, "fact": fact(value, evidence)}
    if targets:
        item["target_entity_ids"] = list(targets)
    return item


def qty(number, unit, **extra):
    value = {"number": number, "unit": unit}
    value.update(extra)
    return value


def part(entity_id, role, label, evidence, name=None, smiles=None, amounts=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence) if name else fact(None),
        "smiles": fact(smiles, evidence) if smiles else fact(None),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": list(amounts or []),
    }


def step(step_id, participant_ids, conditions):
    return {"step_id": step_id, "participant_ids": list(dict.fromkeys(participant_ids)), "conditions": conditions}


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
        "notes": [fact(x, evidence) for x in (notes or [])],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": list(unresolved or []),
        },
    }


def all_ids(parts):
    return [p["entity_id"] for p in parts]


SMILES = {
    "1a": "COCC#Cc1ccccc1",
    "2a": "C=C=C(CCCC)c1ccccc1",
    "2b": "C=C=C(CC)c1ccccc1",
    "2c": "C=C=C(CCCCCC)c1ccccc1",
    "3a": "C#Cc1ccccc1",
    "3b": "C#CCCCC",
    "3c": "C#CCCCCCC",
    "4a": "C#CC(O)c1ccccc1",
    "4b": "C#CC(O)c1ccc(C)cc1",
    "4c": "C#CC(O)c1ccc2c(c1)OCO2",
    "4d": "C#CC(O)c1ccc(OC)cc1",
    "5a": "COCC#CC(O)c1ccccc1",
    "5b": "COCC#CC(O)c1ccc(C)cc1",
    "5c": "COCC#CC(O)c1ccc2c(c1)OCO2",
    "5d": "COCC#CC(O)c1ccc(OC)cc1",
    "5e": "COCC#CC(O)C",
    "6a": "C=C=C(CCCC)C(O)c1ccccc1",
    "6b": "C=C=C(CCCC)C(O)c1ccc(C)cc1",
    "6c": "C=C=C(CCCC)C(O)c1ccc2c(c1)OCO2",
    "6d": "C=C=C(CCCC)C(O)c1ccc(OC)cc1",
    "6e": "C=C=C(CC)C(O)c1ccccc1",
    "6f": "C=C=C(CCC)C(O)c1ccccc1",
    "6g": "C=C=C(CCCCC)C(O)c1ccccc1",
    "6h": "C=C=C(CCCCCC)C(O)c1ccccc1",
    "6i": "C=C=C(c1ccccc1)C(O)c1ccccc1",
    "7a": "CCCCCC=C(CCCC)C(O)c1ccccc1",
    "8a": "C=C=CC(O)c1ccccc1",
    "9a": "CC#CC(O)c1ccccc1",
    "7i": "OC(c1ccccc1)C(=CCc1ccccc1)c1ccccc1",
    "Et2O": "CCOCC",
    "THF": "C1CCOC1",
    "MOMCl": "COCCl",
    "phenylmagnesium_bromide": None,
}

records = []

# Page 1: generic route, explicitly not a batch experiment.
e = ev(1)
parts = [
    part("generic_4", "reactant", "optically active terminal propargylic alcohol 4", e),
    part("generic_5", "product", "optically active 4-hydroxy-2-alkynyl methyl ether 5", e),
    part("generic_6", "product", "optically active 2-substituted secondary 2,3-allenol 6", e),
]
records.append(record(
    "scheme1_general_route", "general_scheme", e, parts,
    [step("conceptual_route", all_ids(parts), [fld("operation", "generic route 4 to 5 to 6; conditions are not shown", e)])],
    [],
    notes=["Scheme 1 is a generic route with R-group variables, not an individual experimental batch."],
    unresolved=["R groups and batch-specific conditions/yields are not supplied in Scheme 1."],
))

# Table 1: seven independent optimization rows.
table1 = [
    (1, 0, 2.0, 0), (2, 1.5, 2.0, 60), (3, 5, 2.0, 72),
    (4, 10, 2.0, 81), (5, 20, 2.0, 82), (6, 10, 1.5, 77), (7, 10, 1.2, 48),
]
for entry, cubr, grig, yld in table1:
    e = ev(2) + (ev(1) if entry in (1, 4) else [])
    parts = [
        part("substrate_1a", "reactant", "1a", e, "methyl 3-phenylpropargyl ether", SMILES["1a"]),
        part("nbu_mgbr", "reagent", "n-C4H9MgBr", e, amounts=[fld("equivalents", qty(grig, "equiv"), e)]),
        part("cubr", "catalyst", "CuBr", e, amounts=[fld("catalyst_loading", qty(cubr, "mol%"), e)]),
        part("ether", "solvent", "Et2O", e, "diethyl ether", SMILES["Et2O"]),
        part("product_2a", "product", "2a", e, "3-phenylhepta-1,2-diene", SMILES["2a"]),
    ]
    records.append(record(
        f"table1_entry{entry}", "optimization_entry", e, parts,
        [step("reaction", all_ids(parts), [fld("temperature", "r.t.", e), fld("reaction_time", None)])],
        [fld("reported_yield", qty(yld, "%"), ev(2), ["product_2a"]), fld("yield_measurement_basis", None)],
        unresolved=["Reaction time, scale, atmosphere, workup, purification, and yield basis are not stated in Table 1."],
    ))

# Table 2 plus detailed preparations on page 4.
table2 = [
    (1, "3a", "phenylacetylene", "n-C4H9", "n-C4H9MgBr", 2.0, 0.2, 1.5, 1.5, "2a", 86,
     [("substrate_mass", 1.020, "g"), ("substrate_amount", 10.0, "mmol")],
     [("product_mass", 1.473, "g")]),
    (2, "3b", "1-hexyne", "Ph", "PhMgBr", 2.0, 0.1, 0.5, 15.5, "2a", 57,
     [("substrate_mass", 0.823, "g"), ("substrate_amount", 10.0, "mmol")],
     [("product_mass", 0.978, "g")]),
    (3, "3a", "phenylacetylene", "C2H5", "C2H5MgBr", 2.0, 0.2, 2.0, 1.0, "2b", 75,
     [("substrate_mass", 1.024, "g"), ("substrate_amount", 10.0, "mmol")],
     [("product_mass", 1.086, "g")]),
    (4, "3c", "1-octyne", "Ph", "PhMgBr", 2.0, 0.1, 0.5, 15.5, "2c", 60,
     [("substrate_mass", 1.102, "g"), ("substrate_amount", 10.0, "mmol")],
     [("product_mass", 1.201, "g")]),
]
table2_reagent_details = {
    1: {"nbuli": (4.0, 10.0), "momcl": (None, 0.810, 10.1), "cubr": (0.280, 1.95), "grignard": (20.0, 20.0)},
    2: {"nbuli": (4.2, 10.5), "momcl": (0.76, 0.806, 10.5), "cubr": (0.144, 1.0), "grignard": (20.0, 20.0)},
    3: {"nbuli": (4.0, 10.0), "momcl": (None, 0.815, 10.1), "cubr": (0.280, 1.95), "grignard": (20.0, 20.0)},
    4: {"nbuli": (4.2, 10.5), "momcl": (0.76, 0.806, 10.5), "cubr": (0.144, 1.0), "grignard": (20.0, 20.0)},
}
for entry, sublabel, subname, r2, griglabel, geq, cueq, t1, t2, prodlabel, yld, subamts, prodamts in table2:
    e = ev(1, 2, 4)
    subev, prodev = ev(4), ev(4)
    parts = [
        part("substrate", "reactant", sublabel, e, subname, SMILES[sublabel], [fld(n, qty(v, u), subev) for n, v, u in subamts]),
        part("nbuli", "reagent", "n-BuLi", e),
        part("momcl", "reagent", "MOMCl", e, "chloromethyl methyl ether", SMILES["MOMCl"]),
        part("grignard", "reagent", griglabel, e, amounts=[fld("equivalents", qty(geq, "equiv"), ev(2))]),
        part("cubr", "catalyst", "CuBr", e, amounts=[fld("equivalents", qty(cueq, "equiv"), ev(2))]),
        part("ether", "solvent", "anhydrous Et2O", e, "diethyl ether", SMILES["Et2O"], [fld("volume", qty(20.0, "mL"), ev(4))]),
        part("product", "product", prodlabel, e, {"2a":"3-phenylhepta-1,2-diene","2b":"3-phenyl-1,2-pentadiene","2c":"3-phenyl-1,2-nonadiene"}[prodlabel], SMILES[prodlabel], [fld(n, qty(v, u), prodev) for n, v, u in prodamts]),
    ]
    rd = table2_reagent_details[entry]
    parts[1]["amounts"] = [fld("volume", qty(rd["nbuli"][0], "mL"), ev(4)), fld("concentration", qty(2.5, "M"), ev(4)), fld("amount", qty(rd["nbuli"][1], "mmol"), ev(4))]
    parts[2]["amounts"] = ([fld("volume", qty(rd["momcl"][0], "mL"), ev(4))] if rd["momcl"][0] is not None else []) + [fld("mass", qty(rd["momcl"][1], "g"), ev(4)), fld("amount", qty(rd["momcl"][2], "mmol"), ev(4))]
    parts[3]["amounts"].extend([fld("solution_volume", qty(rd["grignard"][0], "mL"), ev(4)), fld("solution_concentration", qty(1.0, "M"), ev(4)), fld("amount", qty(rd["grignard"][1], "mmol"), ev(4))])
    parts[4]["amounts"].extend([fld("mass", qty(rd["cubr"][0], "g"), ev(4)), fld("amount", qty(rd["cubr"][1], "mmol"), ev(4))])
    notes = []
    if entry in (2, 4):
        parts.append(part("biphenyl", "product", "biphenyl", e, "biphenyl", "c1ccc(-c2ccccc2)cc1"))
        notes.append("Biphenyl was formed as a side product.")
    records.append(record(
        f"table2_entry{entry}_{prodlabel}", "substrate_scope_entry", e, parts,
        [
            step("deprotonation", ["substrate", "nbuli", "ether"], [fld("temperature", qty(-40, "°C"), e), fld("reaction_time", qty(0.5, "h"), e), fld("atmosphere", "nitrogen", ev(4))]),
            step("mom_installation", ["substrate", "momcl", "ether"], [fld("operation", "warmed from -40 °C to r.t.", e), fld("reaction_time", qty(t1, "h"), ev(2))]),
            step("grignard_allene_formation", all_ids(parts), [fld("temperature", "r.t.", e), fld("reaction_time", qty(t2, "h"), ev(2)), fld("workup", "quenched, extracted, brine-washed, and dried; exact volumes are fully stated only for entry 1", ev(4)), fld("purification", "silica-gel chromatography", ev(4))]),
        ],
        [fld("isolated_yield", qty(yld, "%"), ev(2, 4), ["product"]), fld("yield_measurement_basis", "isolated", ev(2))] + ([fld("approximate_biphenyl_yield", {"minimum": 5, "maximum": 6, "unit": "%", "qualifier": "approx", "raw_text": "about 5–6%"}, ev(2), ["biphenyl"])] if entry in (2,4) else []),
        notes=notes,
        unresolved=["Candidate structures are unverified; abbreviated preparations do not restate every operation-specific volume."],
    ))

# Prose-only failed one-pot attempt.
e = ev(2)
parts = [
    part("generic_4", "reactant", "racemic terminal propargylic alcohols 4", e),
    part("nbuli", "reagent", "n-BuLi", e), part("momcl", "reagent", "MOMCl", e, smiles=SMILES["MOMCl"]),
    part("grignard", "reagent", "primary alkyl Grignard reagent", e), part("cubr", "catalyst", "CuBr", e),
    part("target_6", "product", "racemic 2-substituted secondary 2,3-allenols 6", e),
]
records.append(record(
    "prose_failed_onepot_propargylic_alcohol", "reported_experiment", e, parts,
    [step("attempted_onepot_sequence", all_ids(parts), [fld("operation", "same one-pot protocol as the terminal-alkyne sequence", e), fld("temperature", None), fld("reaction_time", None)])],
    [fld("result", "complicated mixture", e, ["target_6"]), fld("reported_yield", None, targets=["target_6"])],
    unresolved=["Exact substrate variant, quantities, temperature program, time, and product composition are not stated."],
))

# Scheme 2 / section 4.2: four racemic ether preparations.
scheme2 = [
    ("5a", "4a", "1-phenyl-2-propynol", 60, 16, "Et2O", (1.3310, 10.1), (8.0, 20.0), (0.68, 0.72, 9.0), (0.9508,)),
    ("5b", "4b", "1-(4-methylphenyl)-2-propynol", 69, 12, "THF", (1.4652, 10.0), (8.8, 22.0), (1.14, 1.21, 15.0), (1.3118,)),
    ("5c", "4c", "1-(3,4-methylenedioxyphenyl)-2-propynol", 60, 12, "THF", (1.7588, 10.0), (8.8, 22.0), (1.16, 1.208, 15.0), (1.3208,)),
    ("5d", "4d", "1-(4-methoxyphenyl)-2-propynol", 68, 12, "THF", (1.330, 8.2), (7.25, 18.1), (0.75, 0.795, 9.9), (1.1562,)),
]
for idx, (prodlabel, sublabel, subname, yld, hours, solvent, subvals, livals, momvals, prodvals) in enumerate(scheme2, 1):
    pages = (2, 4, 5) if prodlabel == "5d" else (2, 4)
    e = ev(*pages)
    detail = ev(4, 5) if prodlabel == "5d" else ev(4)
    warm = -30 if prodlabel == "5a" else -20
    parts = [
        part("substrate", "reactant", sublabel, e, subname, SMILES[sublabel], [fld("mass", qty(subvals[0], "g"), detail), fld("amount", qty(subvals[1], "mmol"), detail)]),
        part("nbuli", "reagent", "n-BuLi in hexanes", e, amounts=[fld("volume", qty(livals[0], "mL"), detail), fld("concentration", qty(2.5, "M"), detail), fld("amount", qty(livals[1], "mmol"), detail)]),
        part("momcl", "reagent", "MOMCl", e, "chloromethyl methyl ether", SMILES["MOMCl"], [fld("volume", qty(momvals[0], "mL"), detail), fld("mass", qty(momvals[1], "g"), detail), fld("amount", qty(momvals[2], "mmol"), detail)]),
        part("solvent", "solvent", f"anhydrous {solvent}", e, solvent, SMILES[solvent], [fld("volume", qty(20 if prodlabel == "5a" else 30, "mL"), detail)]),
        part("product", "product", prodlabel, e, {"5a":"4-hydroxy-4-phenyl-2-butynyl methyl ether","5b":"4-hydroxy-4-(4-methylphenyl)-2-butynyl methyl ether","5c":"4-hydroxy-4-(3,4-methylenedioxyphenyl)-2-butynyl methyl ether","5d":"4-hydroxy-4-(4-methoxyphenyl)-2-butynyl methyl ether"}[prodlabel], SMILES[prodlabel], [fld("mass", qty(prodvals[0], "g"), detail)]),
    ]
    records.append(record(
        f"scheme2_racemic_{prodlabel}", "reported_experiment", e, parts,
        [step("ether_formation", all_ids(parts), [fld("initial_temperature", qty(-78, "°C"), e), fld("initial_hold_time", qty(0.5, "h"), detail), fld("warm_to", qty(warm, "°C"), e), fld("reaction_time", qty(hours, "h"), detail), fld("atmosphere", "nitrogen", detail), fld("workup", "quenched, ether-extracted, brine-washed, and dried", detail), fld("purification", "flash chromatography on silica gel", detail)])],
        [fld("isolated_yield", qty(yld, "%"), e, ["product"]), fld("yield_measurement_basis", "isolated", e)],
        unresolved=["Structures remain unverified. The 5c/5d operational sequence is inherited only through the explicit 'prepared according to this procedure' statement."],
    ))

# Table 3 optimization. Entry 14 is enriched by Scheme 3 and the detailed page-5 procedure.
table3 = [
    (1, 3.0, 20, -20, 0, None, "THF", "n-C4H9MgBr"),
    (2, 4.0, 10, -30, 43, None, "Et2O", "n-C4H9MgBr"),
    (3, 4.0, 20, -30, 52, None, "Et2O", "n-C4H9MgBr"),
    (4, 4.0, 30, -30, 52, None, "Et2O", "n-C4H9MgBr"),
    (5, 4.0, 50, -30, 53, None, "Et2O", "n-C4H9MgBr"),
    (6, 4.0, 20, "r.t.", "complicated mixture", None, "Et2O", "n-C4H9MgBr"),
    (7, 4.0, 20, 0, "complicated mixture", None, "Et2O", "n-C4H9MgBr"),
    (8, 4.0, 20, -20, 48, None, "Et2O", "n-C4H9MgBr"),
    (9, 4.0, 20, -40, 30, None, "Et2O", "n-C4H9MgBr"),
    (10, 4.5, 20, -30, 53, None, "Et2O", "n-C4H9MgBr"),
    (11, 4.67, 20, -30, 55, 53, "Et2O", "n-C4H9MgBr"),
    (12, 4.83, 20, -30, 45, None, "Et2O", "n-C4H9MgBr"),
    (13, 5.0, 20, -30, 46, None, "Et2O", "n-C4H9MgBr"),
    (14, 4.67, 20, -30, 27, 26, "Et2O", "n-C4H9MgCl"),
]
for entry, geq, cuload, temp, nmry, isoly, solvent, grig in table3:
    pages = (2, 3, 5) if entry == 14 else (2,)
    e = ev(*pages)
    parts = [
        part("substrate_5a", "reactant", "rac-5a", e, "racemic 4-hydroxy-4-phenyl-2-butynyl methyl ether", SMILES["5a"]),
        part("grignard", "reagent", grig, e, amounts=[fld("equivalents", qty(geq, "equiv"), ev(2))]),
        part("cubr", "catalyst", "CuBr", e, amounts=[fld("catalyst_loading", qty(cuload, "mol%"), ev(2))]),
        part("solvent", "solvent", solvent, e, solvent, SMILES[solvent]),
        part("product_6a", "product", "6a", e, "2-butyl-1-phenyl-2,3-butadien-1-ol", SMILES["6a"]),
    ]
    if entry == 14:
        parts[0]["amounts"] = [fld("mass", qty(52.6, "mg"), ev(5)), fld("amount", qty(0.30, "mmol"), ev(5))]
        parts[1]["amounts"].extend([fld("solution_volume", qty(1.4, "mL"), ev(5)), fld("solution_concentration", qty(1.0, "M"), ev(5)), fld("amount", qty(1.4, "mmol"), ev(5))])
        parts[2]["amounts"].extend([fld("mass", qty(8.9, "mg"), ev(5)), fld("amount", qty(0.06, "mmol"), ev(5))])
        parts[3]["amounts"] = [fld("volume", qty(1.6, "mL"), ev(5))]
        parts[4]["amounts"] = [fld("mass", qty(16.0, "mg"), ev(5))]
    outcomes = []
    if isinstance(nmry, (int, float)):
        outcomes.append(fld("nmr_yield", qty(nmry, "%"), ev(2), ["product_6a"]))
    else:
        outcomes.append(fld("reaction_result", nmry, ev(2), ["product_6a"]))
    if isoly is not None:
        outcomes.append(fld("isolated_yield", qty(isoly, "%"), ev(2), ["product_6a"]))
    outcomes.append(fld("nmr_yield_measurement_basis", "1H NMR with 1,3,5-trimethylbenzene as internal standard", ev(2)))
    if entry == 14:
        parts.extend([
            part("product_7a", "product", "7a", e, "2-butyl-1-phenyl-2-octen-1-ol", SMILES["7a"], [fld("mass", qty(4.5, "mg"), ev(5))]),
            part("product_8a", "product", "8a", e, "1-phenyl-2,3-butadien-1-ol", SMILES["8a"], [fld("mass", qty(7.5, "mg"), ev(5))]),
            part("product_9a", "product", "9a", e, "1-phenyl-2-butyn-1-ol", SMILES["9a"], [fld("mass", qty(5.1, "mg"), ev(5))]),
        ])
        outcomes.extend([
            fld("isolated_yield_7a", qty(6, "%"), ev(3, 5), ["product_7a"]), fld("nmr_yield_7a", qty(9, "%"), ev(3), ["product_7a"]),
            fld("isolated_yield_8a", qty(17, "%"), ev(3, 5), ["product_8a"]), fld("nmr_yield_8a", qty(21, "%"), ev(3), ["product_8a"]),
            fld("isolated_yield_9a", qty(12, "%"), ev(3, 5), ["product_9a"]), fld("nmr_yield_9a", qty(17, "%"), ev(3), ["product_9a"]),
            fld("recovered_starting_material_yield", qty(6, "%"), ev(3, 5), ["substrate_5a"]),
        ])
    temp_value = temp if isinstance(temp, str) else qty(temp, "°C")
    conditions = [fld("temperature", temp_value, ev(2)), fld("reaction_time", qty(10, "h"), ev(3, 5)) if entry == 14 else fld("reaction_time", None)]
    if entry == 14:
        conditions.extend([fld("atmosphere", "nitrogen", ev(5)), fld("workup", "saturated ammonium chloride quench, ether extraction, brine wash, and drying", ev(5)), fld("purification", "silica-gel column chromatography (petroleum ether/ethyl acetate 20:1 to 10:1)", ev(5))])
    records.append(record(
        f"table3_entry{entry}", "optimization_entry", e, parts,
        [step("grignard_allene_formation", all_ids(parts), conditions)], outcomes,
        unresolved=[] if entry == 14 else ["Reaction time, scale, atmosphere, workup, and purification are not stated for this optimization row."],
    ))

# Two explicitly stated trace-result Grignard trials outside Table 4.
for suffix, reagent in [("vinylmagnesium_chloride_trace", "vinylmagnesium chloride"), ("allylmagnesium_chloride_trace", "allylmagnesium chloride")]:
    e = ev(2)
    parts = [
        part("substrate_5", "reactant", "4-hydroxy-4-aryl-2-butynyl methyl ether 5 (exact variant not restated)", e),
        part("grignard", "reagent", reagent, e), part("thf", "solvent", "THF solution", e, "tetrahydrofuran", SMILES["THF"]),
        part("target_product", "product", "corresponding allenol product", e),
    ]
    records.append(record(
        suffix, "reported_experiment", e, parts,
        [step("attempted_grignard_reaction", all_ids(parts), [fld("temperature", None), fld("reaction_time", None)])],
        [fld("reported_yield", "trace", e, ["target_product"])],
        unresolved=["The exact substrate variant, catalyst loading, temperature, duration, scale, and yield basis are not restated."],
    ))

# Table 4, with Scheme 3 Br and sections 4.3.2–4.3.11 merged where applicable.
table4 = [
    (1, "5a", "n-C4H9MgBr", 4.67, "6a", 51, 53, 4, None),
    (2, "5b", "n-C4H9MgBr", 4.67, "6b", 50, 52, 2, None),
    (3, "5c", "n-C4H9MgBr", 4.67, "6c", 33, 33, 6, None),
    (4, "5d", "n-C4H9MgBr", 4.67, "6d", 45, 50, 1, None),
    (5, "5a", "C2H5MgBr", 4.67, "6e", 35, 36, 1, None),
    (6, "5a", "n-C3H7MgBr", 4.67, "6f", 43, 46, 6, None),
    (7, "5a", "n-C5H11MgBr", 4.67, "6g", 48, 50, 2, None),
    (8, "5a", "n-C6H13MgBr", 4.67, "6h", 44, 56, 5, None),
    (9, "5e", "n-C4H9MgBr", 4.0, "6_from_5e", None, 7, 20, None),
    (10, "5a", "PhMgBr", 4.0, "6i", 22, 25, 39, None),
    (11, "5a", "PhMgBr", 4.0, "6i", 33, 33, 0, ("7i", 33, "nmr")),
    (12, "5a", "PhMgBr", 6.0, "6i", None, None, 0, ("7i", 48, "isolated")),
]
mass_details = {
    1: (52.9, 0.30, 8.7, 0.06, 1.6, 1.4, 1.4, 31.1),
    2: (56.8, 0.30, 8.6, 0.10, 1.6, 1.4, 1.4, 32.2),
    3: (65.7, 0.30, 8.7, 0.06, 1.6, 1.4, 1.4, 24.1),
    4: (61.3, 0.30, 8.6, 0.06, 1.6, 1.4, 1.4, 30.9),
    5: (53.5, 0.30, 8.6, 0.06, 1.6, 1.4, 1.4, 19.0),
    6: (51.8, 0.29, 8.6, 0.06, 1.6, 1.4, 1.4, 24.0),
    7: (52.1, 0.30, 8.8, 0.06, 1.6, 1.4, 1.4, 30.8),
    8: (53.1, 0.30, 8.7, 0.06, 1.6, 1.4, 1.4, 30.8),
    10: (52.0, 0.30, 8.9, 0.06, 1.8, 1.2, 1.2, 14.1),
    12: (51.8, 0.29, 8.8, 0.06, 1.2, 1.8, 1.8, 42.3),
}
prod_names = {
    "6a":"2-butyl-1-phenyl-2,3-butadien-1-ol", "6b":"2-butyl-1-(4-methylphenyl)-2,3-butadien-1-ol",
    "6c":"2-butyl-1-(3,4-methylenedioxyphenyl)-2,3-butadien-1-ol", "6d":"2-butyl-1-(4-methoxyphenyl)-2,3-butadien-1-ol",
    "6e":"2-ethyl-1-phenyl-2,3-butadien-1-ol", "6f":"1-phenyl-2-propyl-2,3-butadien-1-ol",
    "6g":"2-pentyl-1-phenyl-2,3-butadien-1-ol", "6h":"2-hexyl-1-phenyl-2,3-butadien-1-ol",
    "6i":"1,2-diphenyl-2,3-butadien-1-ol", "6_from_5e":"product 6 from methyl-substituted substrate 5e",
}
for entry, sublabel, reagent, geq, prodlabel, isol, nmr, recovery, extra in table4:
    pages = [3]
    if entry in range(1, 8 + 1): pages.append(5)
    if entry in (8, 10, 12): pages.append(6)
    if entry in (9, 10, 11, 12): pages.append(2)
    e = ev(*pages)
    details = mass_details.get(entry)
    subsmiles = SMILES.get(sublabel)
    subamounts = []
    if details:
        subamounts = [fld("mass", qty(details[0], "mg"), ev(5, 6)), fld("amount", qty(details[1], "mmol"), ev(5, 6))]
    parts = [
        part("substrate", "reactant", sublabel, e, smiles=subsmiles, amounts=subamounts),
        part("grignard", "reagent", reagent, e, amounts=[fld("equivalents", qty(geq, "equiv"), ev(3))]),
        part("cubr", "catalyst", "CuBr", e, amounts=[fld("catalyst_loading", qty(20, "mol%"), ev(3))]),
        part("ether", "solvent", "Et2O", e, "diethyl ether", SMILES["Et2O"]),
        part("product", "product", prodlabel, e, prod_names[prodlabel], SMILES.get(prodlabel)),
    ]
    if details:
        parts[2]["amounts"].extend([fld("mass", qty(details[2], "mg"), ev(5, 6)), fld("amount", qty(details[3], "mmol"), ev(5, 6))])
        parts[3]["amounts"].append(fld("volume", qty(details[4], "mL"), ev(5, 6)))
        parts[1]["amounts"].extend([fld("solution_volume", qty(details[5], "mL"), ev(5, 6)), fld("solution_concentration", qty(1, "M"), ev(5, 6)), fld("amount", qty(details[6], "mmol"), ev(5, 6))])
        mass_target = "product" if entry != 12 else "product_7i"
        if entry != 12:
            parts[4]["amounts"].append(fld("mass", qty(details[7], "mg"), ev(5, 6)))
    if extra:
        label, _, _ = extra
        parts.append(part("product_7i", "product", label, e, "1,2,4-triphenyl-2-buten-1-ol", SMILES["7i"], [fld("mass", qty(details[7], "mg"), ev(6))] if entry == 12 else []))
    if entry == 1:
        parts.extend([
            part("product_7a", "product", "7a", e, "2-butyl-1-phenyl-2-octen-1-ol", SMILES["7a"], [fld("mass", qty(5.4, "mg"), ev(5))]),
            part("product_8a", "product", "8a", e, "1-phenyl-2,3-butadien-1-ol", SMILES["8a"], [fld("mass", qty(4.0, "mg"), ev(5))]),
            part("product_9a", "product", "9a", e, "1-phenyl-2-butyn-1-ol", SMILES["9a"], [fld("mass", qty(3.7, "mg"), ev(5))]),
        ])
    outcomes = []
    if isol is not None: outcomes.append(fld("isolated_yield", qty(isol, "%"), ev(3, 5, 6), ["product"]))
    if nmr is not None: outcomes.append(fld("nmr_yield", qty(nmr, "%"), ev(3), ["product"]))
    outcomes.append(fld("recovered_starting_material_yield", qty(recovery, "%"), ev(3, 5, 6), ["substrate"]))
    outcomes.append(fld("nmr_yield_measurement_basis", "1H NMR with 1,3,5-trimethylbenzene as internal standard", ev(3)))
    if extra:
        label, val, basis = extra
        outcomes.append(fld(f"{basis}_yield_{label}", qty(val, "%"), ev(3, 6), ["product_7i"]))
    if entry == 1:
        outcomes.extend([
            fld("isolated_yield_7a", qty(7, "%"), ev(3, 5), ["product_7a"]), fld("nmr_yield_7a", qty(9, "%"), ev(3), ["product_7a"]),
            fld("isolated_yield_8a", qty(9, "%"), ev(3, 5), ["product_8a"]), fld("nmr_yield_8a", qty(12, "%"), ev(3), ["product_8a"]),
            fld("isolated_yield_9a", qty(8, "%"), ev(3, 5), ["product_9a"]), fld("nmr_yield_9a", qty(11, "%"), ev(3), ["product_9a"]),
        ])
    conditions = [fld("initial_temperature", qty(-30, "°C"), ev(3))]
    if entry in (11, 12): conditions.append(fld("warm_to", "r.t.", ev(3)))
    conditions.append(fld("reaction_time", qty(10, "h"), ev(3)) if entry == 1 else fld("reaction_time", None))
    records.append(record(
        f"table4_entry{entry}", "substrate_scope_entry", e, parts,
        [step("grignard_allene_formation", all_ids(parts), conditions)], outcomes,
        unresolved=["Atmosphere, workup, purification, and yield basis are not restated for abbreviated rows; time is missing except for entry 1.", "All structures remain unverified."],
    ))

# Table 5, enriched by page-6 preparations for entries 1–6.
table5 = [
    (1, "S-4a", "R-5a", 19, 99.6, 63, 98.2), (2, "R-4a", "S-5a", 16, 99.9, 66, 96.1),
    (3, "S-4b", "R-5b", 14, 99.9, 67, 99.2), (4, "R-4b", "S-5b", 20, 99.5, 61, 98.6),
    (5, "S-4c", "R-5c", 22, 99.3, 62, 98.6), (6, "R-4c", "S-5c", 23, 96.0, 57, 97.1),
    (7, "S-4d", "R-5d", 16, 97.2, 61, 96.7), (8, "R-4d", "S-5d", 16, 96.7, 61, 96.4),
]
table5_details = {
    1: ((1.3166, 10.0), (8.8, 22.0), (1.14, 1.21, 15.0), 50, 1.1139),
    2: ((0.6604, 5.0), (4.4, 11.0), (0.58, 0.615, 7.5), 25, 0.5778),
    3: ((0.4642, 3.2), (2.8, 7.0), (0.36, 0.382, 4.8), 20, 0.4034),
    4: ((0.9112, 6.2), (5.5, 13.7), (0.71, 0.753, 9.4), 30, 0.7201),
    5: ((1.5592, 8.9), (7.8, 19.5), (1.00, 1.060, 13.2), 30, 1.2152),
    6: ((1.5666, 8.9), (7.8, 19.6), None, 30, None),
}
for entry, sublabel, prodlabel, hours, subee, yld, prodee in table5:
    pages = (3, 6) if entry <= 6 else (3,)
    e = ev(*pages)
    base4 = sublabel[-2:]
    base5 = prodlabel[-2:]
    detail = table5_details.get(entry)
    subamts = []
    prodamts = []
    if detail:
        subamts = [fld("mass", qty(detail[0][0], "g"), ev(6)), fld("amount", qty(detail[0][1], "mmol"), ev(6))]
        if detail[4] is not None: prodamts = [fld("mass", qty(detail[4], "g"), ev(6))]
    parts = [
        part("substrate", "reactant", sublabel, e, smiles=SMILES.get(base4), amounts=subamts),
        part("nbuli", "reagent", "n-BuLi in hexanes", e),
        part("momcl", "reagent", "MOMCl", e, "chloromethyl methyl ether", SMILES["MOMCl"]),
        part("thf", "solvent", "anhydrous THF", e, "tetrahydrofuran", SMILES["THF"], [fld("volume", qty(detail[3], "mL"), ev(6))] if detail else []),
        part("product", "product", prodlabel, e, smiles=SMILES.get(base5), amounts=prodamts),
    ]
    if detail:
        parts[1]["amounts"] = [fld("volume", qty(detail[1][0], "mL"), ev(6)), fld("concentration", qty(2.5, "M"), ev(6)), fld("amount", qty(detail[1][1], "mmol"), ev(6))]
        if detail[2]:
            parts[2]["amounts"] = [fld("volume", qty(detail[2][0], "mL"), ev(6)), fld("mass", qty(detail[2][1], "g"), ev(6)), fld("amount", qty(detail[2][2], "mmol"), ev(6))]
    conditions = [fld("initial_temperature", qty(-78, "°C"), e), fld("warm_to", qty(-20, "°C"), e), fld("reaction_time", qty(hours, "h"), ev(3))]
    if entry <= 5:
        conditions.extend([fld("atmosphere", "nitrogen", ev(6)), fld("workup", "aqueous ammonium chloride quench, ether extraction, brine wash, drying", ev(6)), fld("purification", "flash chromatography on silica gel", ev(6))])
    else:
        conditions.extend([fld("atmosphere", None), fld("workup", None), fld("purification", None)])
    outcomes = [
        fld("input_ee", qty(subee, "%"), ev(3, 6), ["substrate"]),
        fld("isolated_yield", qty(yld, "%"), ev(3, 6), ["product"]),
        fld("product_ee", qty(prodee, "%"), ev(3, 6), ["product"]),
        fld("ee_measurement_basis", "chiral HPLC", ev(6)) if entry <= 5 else fld("ee_measurement_basis", None),
    ]
    records.append(record(
        f"table5_entry{entry}_{prodlabel.lower()}", "substrate_scope_entry", e, parts,
        [step("chiral_ether_formation", all_ids(parts), conditions)], outcomes,
        unresolved=["Candidate connectivity and stereochemistry are unverified; entries 7–8 lack detailed procedures in the covered range."],
    ))

# Table 6: fourteen enantioenriched allene scope entries.
table6 = [
    (1, "R-5a", "n-C4H9MgBr", 98.2, "R-6a", 50, 53, 99.5, 4),
    (2, "S-5a", "n-C4H9MgBr", 96.1, "S-6a", 48, 52, 99.2, 6),
    (3, "R-5b", "n-C4H9MgBr", 99.2, "R-6b", 47, 45, 97.5, 0),
    (4, "S-5b", "n-C4H9MgBr", 98.6, "S-6b", 45, 46, 98.9, 0),
    (5, "R-5c", "n-C4H9MgBr", 98.6, "R-6c", 26, 30, 98.5, 6),
    (6, "S-5c", "n-C4H9MgBr", 97.1, "S-6c", 28, 33, 96.9, 6),
    (7, "R-5d", "n-C4H9MgBr", 96.7, "R-6d", 48, 51, 95.3, 7),
    (8, "S-5d", "n-C4H9MgBr", 96.4, "S-6d", 49, 56, 95.8, 0),
    (9, "R-5e", "C2H5MgBr", 98.2, "R-6e", 40, 38, 99.5, 8),
    (10, "S-5e", "C2H5MgBr", 96.1, "S-6e", 35, 40, 99.5, 5),
    (11, "R-5f", "n-C3H7MgBr", 98.2, "R-6f", 37, 41, 99.7, 7),
    (12, "S-5f", "n-C3H7MgBr", 96.1, "S-6f", 39, 42, 97.9, 5),
    (13, "R-5g", "n-C5H11MgBr", 98.2, "R-6g", 49, 57, 99.6, 11),
    (14, "R-5h", "n-C6H13MgBr", 98.2, "R-6h", 51, 58, 99.6, 10),
]
for entry, sublabel, reagent, subee, prodlabel, isol, nmr, prodee, recovery in table6:
    e = ev(3)
    base_sub = sublabel[-2:]
    base_prod = prodlabel[-2:]
    parts = [
        part("substrate", "reactant", sublabel, e, smiles=SMILES.get(base_sub)),
        part("grignard", "reagent", reagent, e, amounts=[fld("equivalents", qty(4.67, "equiv"), e)]),
        part("cubr", "catalyst", "CuBr", e, amounts=[fld("catalyst_loading", qty(20, "mol%"), e)]),
        part("ether", "solvent", "Et2O", e, "diethyl ether", SMILES["Et2O"]),
        part("product", "product", prodlabel, e, smiles=SMILES.get(base_prod)),
    ]
    outcomes = [
        fld("input_ee", qty(subee, "%"), e, ["substrate"]), fld("isolated_yield", qty(isol, "%"), e, ["product"]),
        fld("nmr_yield", qty(nmr, "%"), e, ["product"]), fld("product_ee", qty(prodee, "%"), e, ["product"]),
        fld("recovered_starting_material_yield", qty(recovery, "%"), e, ["substrate"]),
        fld("nmr_yield_measurement_basis", "1H NMR with 1,3,5-trimethylbenzene as internal standard", e),
    ]
    records.append(record(
        f"table6_entry{entry}_{prodlabel.lower()}", "substrate_scope_entry", e, parts,
        [step("enantioenriched_grignard_allene_formation", all_ids(parts), [fld("temperature", qty(-30, "°C"), e), fld("reaction_time", None), fld("atmosphere", None), fld("workup", None), fld("purification", None)])],
        outcomes,
        unresolved=["Reaction time, scale, atmosphere, workup, purification, and ee measurement method are not stated in Table 6.", "Labels 5e–5h repeat the phenyl-substituted starting skeleton but their exact nomenclature relationship to 5a is unresolved; labels are preserved as printed.", "Candidate stereochemistry is unverified."],
    ))

assert len(records) == 67, len(records)
record_ids = {r["record_id"] for r in records}

coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1, "state": "attempted",
            "regions": [
                {"region": "title, abstract, introduction, and lower-right opening Results and Discussion", "finding": "Broad scope claims and cited prior syntheses were not duplicated as batch experiments; opening prose supports Table 1 catalyst-free failure and the one-pot Table 2 protocol.", "evidence_ids": ev(1)},
                {"region": "lower-right Scheme 1", "finding": "Generic route from terminal propargylic alcohol 4 through methyl ether 5 to allenol 6; classified as a general scheme.", "evidence_ids": ev(1)},
            ],
            "record_ids": [f"{DOC}:scheme1_general_route", f"{DOC}:table1_entry1", f"{DOC}:table1_entry4"] + [f"{DOC}:table2_entry{i}_{p}" for i, p in [(1,"2a"),(2,"2a"),(3,"2b"),(4,"2c")]],
            "unresolved": ["Abstract-level >99% ee and general scope statements were not converted into duplicate experiments."],
        },
        {
            "page": 2, "state": "attempted",
            "regions": [
                {"region": "upper-left Tables 1 and 2", "finding": "Seven optimization rows and four one-pot substrate-scope rows extracted independently; Table 2 footnote biphenyl outcome retained on entries 2 and 4.", "evidence_ids": ev(2)},
                {"region": "lower-left Scheme 2 and adjacent prose", "finding": "Four racemic propargylic methyl-ether preparations plus one failed generic one-pot propargylic-alcohol attempt extracted.", "evidence_ids": ev(2)},
                {"region": "upper-right Table 3 and footnotes", "finding": "Fourteen optimization rows extracted, including THF override, Grignard chloride override, zero yields, complicated mixtures, NMR basis, and parenthesized isolated yields.", "evidence_ids": ev(2)},
                {"region": "right-column Table 4 discussion", "finding": "Narrative details for low-yield methyl substrate, phenylmagnesium rows, and separate vinyl/allyl magnesium chloride trace trials linked to their records.", "evidence_ids": ev(2)},
            ],
            "record_ids": sorted(rid for rid in record_ids if any(x in rid for x in [":table1_", ":table2_", ":scheme2_", ":table3_", ":prose_failed_", ":vinylmagnesium_", ":allylmagnesium_"])) + [f"{DOC}:table4_entry{i}" for i in (9,10,11,12)],
            "unresolved": ["The failed one-pot attempt and two trace trials omit exact substrate mapping and most conditions."],
        },
        {
            "page": 3, "state": "attempted",
            "regions": [
                {"region": "top Scheme 3", "finding": "Chloride and bromide selectivity experiments reconciled with Table 3 entry 14 and Table 4 entry 1 respectively; byproduct yields and recovery retained without duplicate records.", "evidence_ids": ev(3)},
                {"region": "middle-left Table 4 and footnotes", "finding": "Twelve independent racemic Grignard scope/condition rows extracted, including 4/6-equivalent overrides, warm-to-room-temperature rows, secondary product 7i, and recovery.", "evidence_ids": ev(3)},
                {"region": "lower-left Table 5", "finding": "Eight optically active ether-preparation rows extracted with input ee, duration, isolated yield, and product ee.", "evidence_ids": ev(3)},
                {"region": "middle-right Table 6", "finding": "Fourteen enantioenriched allene rows extracted with isolated/NMR yields, input/product ee, and recovery.", "evidence_ids": ev(3)},
            ],
            "record_ids": [f"{DOC}:table3_entry14"] + [f"{DOC}:table4_entry{i}" for i in range(1,13)] + [f"{DOC}:table5_entry{i}_{p}" for i,p in [(1,"r-5a"),(2,"s-5a"),(3,"r-5b"),(4,"s-5b"),(5,"r-5c"),(6,"s-5c"),(7,"r-5d"),(8,"s-5d")]] + [f"{DOC}:table6_entry{i}_{p}" for i,p in [(1,"r-6a"),(2,"s-6a"),(3,"r-6b"),(4,"s-6b"),(5,"r-6c"),(6,"s-6c"),(7,"r-6d"),(8,"s-6d"),(9,"r-6e"),(10,"s-6e"),(11,"r-6f"),(12,"s-6f"),(13,"r-6g"),(14,"r-6h")]],
            "unresolved": ["Table 4 and Table 6 omit most operational details; all stereochemical structures remain unverified."],
        },
        {
            "page": 4, "state": "attempted",
            "regions": [
                {"region": "left column sections 4.1.1–4.1.4", "finding": "Detailed preparations for the four Table 2 rows merged into those rows with exact quantities, masses, and typical-procedure operations.", "evidence_ids": ev(4)},
                {"region": "right column sections 4.2.1–4.2.4", "finding": "Detailed preparations for racemic 5a–5d merged into Scheme 2 records; 5d outcome continues on page 5.", "evidence_ids": ev(4)},
            ],
            "record_ids": [f"{DOC}:table2_entry{i}_{p}" for i,p in [(1,"2a"),(2,"2a"),(3,"2b"),(4,"2c")]] + [f"{DOC}:scheme2_racemic_5{x}" for x in "abcd"],
            "unresolved": ["Abbreviated 'prepared similarly/according to this procedure' paragraphs do not restate every operation-specific volume."],
        },
        {
            "page": 5, "state": "attempted",
            "regions": [
                {"region": "top-left continuation of section 4.2.4", "finding": "Product mass and 68% isolated yield for 5d merged with its cross-page Scheme 2 record.", "evidence_ids": ev(5)},
                {"region": "section 4.3.1", "finding": "Detailed n-C4H9MgCl experiment merged with Table 3 entry 14/Scheme 3 chloride row, including four isolated products and recovered 5a.", "evidence_ids": ev(5)},
                {"region": "sections 4.3.2–4.3.9", "finding": "Detailed racemic Table 4 preparations for entries 1–8 merged with their table records; entry 8 characterization continues on page 6.", "evidence_ids": ev(5)},
            ],
            "record_ids": [f"{DOC}:scheme2_racemic_5d", f"{DOC}:table3_entry14"] + [f"{DOC}:table4_entry{i}" for i in range(1,9)],
            "unresolved": ["Abbreviated reactions generally omit duration, atmosphere, workup, and purification."],
        },
        {
            "page": 6, "state": "attempted",
            "regions": [
                {"region": "top-left sections 4.3.9–4.3.11", "finding": "Entry 8 characterization and detailed Table 4 entry 10/12 preparations merged; entry 11 remains table-only because no matching detailed batch is stated.", "evidence_ids": ev(6)},
                {"region": "sections 4.4.1–4.4.6", "finding": "Detailed optically active ether preparations enrich Table 5 entries 1–6; entry 6 continues beyond page 6, so only visible quantities plus Table 5 outcomes were used.", "evidence_ids": ev(6)},
            ],
            "record_ids": [f"{DOC}:table4_entry8", f"{DOC}:table4_entry10", f"{DOC}:table4_entry12"] + [f"{DOC}:table5_entry{i}_{p}" for i,p in [(1,"r-5a"),(2,"s-5a"),(3,"r-5b"),(4,"s-5b"),(5,"r-5c"),(6,"s-5c")]],
            "unresolved": ["Section 4.4.6 continues onto page 7, which is not claimed as covered; missing continuation details were not imported."],
        },
    ],
}

assert [p["page"] for p in coverage["pages"]] == [1,2,3,4,5,6]
assert all(p["regions"] for p in coverage["pages"])
assert all(rid in record_ids for p in coverage["pages"] for rid in p["record_ids"])

(ROOT / "raw_model" / "records_pages_0001_0006.json").write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
(ROOT / "coverage").mkdir(parents=True, exist_ok=True)
(ROOT / "coverage" / "pages_0001_0006.json").write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

tasks_path = ROOT / "tasks.json"
tasks = json.loads(tasks_path.read_text())
for task in tasks:
    if task.get("document_id") == DOC and task.get("evidence_id") in {f"{DOC}:page{i}:text" for i in range(1,7)}:
        task["state"] = "attempted"
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"records": len(records), "coverage_pages": [p["page"] for p in coverage["pages"]]}, ensure_ascii=False))
