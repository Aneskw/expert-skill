#!/usr/bin/env python3
"""Build evidence-linked machine records for Yuan and Ma, PDF pages 1--6."""

import json
from pathlib import Path


DOC = "doc_5a2933fd9800dede"
BASE = Path(__file__).resolve().parents[1]


def ev(*pages):
    result = []
    for page in pages:
        result.extend([f"{DOC}:page{page}:text", f"{DOC}:page{page}:image"])
    return list(dict.fromkeys(result))


def fact(value, evidence):
    return {
        "value": value,
        "evidence_ids": list(evidence) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def quantity(number, unit, **extra):
    value = {"number": number, "unit": unit}
    value.update(extra)
    return value


def fld(name, value, evidence, targets=None):
    item = {"name": name, "fact": fact(value, evidence)}
    if targets:
        item["target_entity_ids"] = list(targets)
    return item


def participant(entity_id, role, label, evidence, *, name=None, smiles=None, amounts=()):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence) if name else fact(None, ()),
        "smiles": fact(smiles, evidence) if smiles else fact(None, ()),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": list(amounts),
    }


def amount(name, value, evidence):
    return fld(name, value, evidence)


def record(suffix, kind, evidence, participants, steps, outcomes, notes, unresolved):
    return {
        "record_id": f"{DOC}:{suffix}",
        "document_id": DOC,
        "source_reaction_id": suffix,
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


def step(participants, conditions):
    return {
        "step_id": "reaction",
        "participant_ids": [p["entity_id"] for p in participants],
        "conditions": conditions,
    }


SMILES = {
    "1a": "C=C=Cc1ccccc1",
    "1b": "C=C=Cc1ccc(C)cc1",
    "1c": "C=C=Cc1cccc(C)c1",
    "1d": "C=C=Cc1ccc(OC)cc1",
    "1e": "C=C=Cc1ccc(CCCC)cc1",
    "1f": "C=C=Cc1ccc(C(C)C)cc1",
    "1g": "C=C=Cc1ccsc1",
    "1h": "C=C=Cc1cccs1",
    "1i": "C=C=Cc1ccc(Cl)cc1",
    "1j": "C=C=Cc1cccc(Cl)c1",
    "1k": "C=C=Cc1ccccc1Cl",
    "1l": "C=C=Cc1ccc(Br)cc1",
    "1m": "C=C=Cc1ccccc1Br",
    "1n": "C=C=Cc1ccc(C(=O)OCC)cc1",
    "1o": "C=C=CCc1ccccc1",
    "1p": "C=C=CCCCCCCCC",
    "1q": "C=C=CCCCCCC",
    "B2pin2": "CC1(C)OB(B2OC(C)(C)C(C)(C)O2)OC1(C)C",
    "CuCl": "[Cu]Cl",
    "NaOtBu": "CC(C)(C)[O-].[Na+]",
    "MeOH": "CO",
    "THF": "C1CCOC1",
    "Et2O": "CCOCC",
    "CH3CN": "CC#N",
    "PhCH3": "Cc1ccccc1",
    "CH2Cl2": "ClCCl",
    "AcOH": "CC(=O)O",
    "3a": "C=C(B1OC(C)(C)C(C)(C)O1)Cc1ccccc1",
    "Z-2a": "CC(=Cc1ccccc1)B1OC(C)(C)C(C)(C)O1",
}


SUBSTRATES_T2 = [
    (1, "Ph (1a)", "1a", 40, 72, "Z-2a"),
    (2, "Ph (1a)", "1a", 20, 69, "Z-2a"),
    (3, "p-Me-C6H4 (1b)", "1b", 30, 71, "Z-2b"),
    (4, "m-Me-C6H4 (1c)", "1c", 50, 70, "Z-2c"),
    (5, "p-MeO-C6H4 (1d)", "1d", 50, 66, "Z-2d"),
    (6, "p-Bu-C6H4 (1e)", "1e", 40, 73, "Z-2e"),
    (7, "p-i-Pr-C6H4 (1f)", "1f", 50, 63, "Z-2f"),
    (8, "3-thienyl (1g)", "1g", 30, 76, "Z-2g"),
    (9, "2-thienyl (1h)", "1h", 40, 64, "Z-2h"),
]


SUBSTRATES_T4 = [
    (1, "Ph (1a)", "1a", 40, 67, "3a", "≥95/5", None),
    (2, "Ph (1a)", "1a", 20, 70, "3a", "≥95/5", None),
    (3, "p-Me-C6H4 (1b)", "1b", 40, 70, "3b", "≥94/6", None),
    (4, "m-Me-C6H4 (1c)", "1c", 50, 64, "3c", "≥95/5", None),
    (5, "p-Bu-C6H4 (1e)", "1e", 40, 70, "3d", "≥94/6", None),
    (6, "p-Cl-C6H4 (1i)", "1i", 45, 73, "3e", "≥96/4", "97/3"),
    (7, "m-Cl-C6H4 (1j)", "1j", 60, 60, "3f", "≥96/4", None),
    (8, "o-Cl-C6H4 (1k)", "1k", 45, 62, "3g", ">99/1", None),
    (9, "p-Br-C6H4 (1l)", "1l", 45, 73, "3h", "≥96/4", "97/3"),
    (10, "o-Br-C6H4 (1m)", "1m", 90, 54, "3i", ">99/1", None),
    (11, "p-EtO2C-C6H4 (1n)", "1n", 70, 76, "3j", "≥96/4", "97/3"),
    (12, "Bn (1o)", "1o", 50, 64, "3k", "99/1", None),
    (13, "C8H17 (1p)", "1p", 50, 71, "3l", "≥96/4", None),
    (14, "C6H13 (1q)", "1q", 60, 63, "3m", "≥97/3", "98/2"),
]


records = []

# Page 1: the paper's generic product map, explicitly not a reported experiment.
e1 = ev(1)
generic = [
    participant("generic_allene_1", "reactant", "generic R1-substituted allene 1", e1),
]
for label in ["Z-2", "E-2", "3", "Z-4", "E-4", "5"]:
    generic.append(participant(f"generic_{label.replace('-', '_')}", "product", label, e1))
records.append(record(
    "scheme1_general_monohydroboration_map", "general_scheme", e1, generic, [], [],
    ["Scheme 1 enumerates six possible monohydroboration regio-/stereoisomers."],
    ["This is a generic product map, not one reported experiment; no conditions or yields are assigned.",
     "Generic R1 structures are not resolvable to unique SMILES."],
))

# Page 2 prose: unsuccessful Pd feasibility trial.
e2 = ev(2)
pd_parts = [
    participant("substrate_1a", "reactant", "phenylallene 1a", e2, smiles=SMILES["1a"]),
    participant("diboron", "reactant", "bis(pinacolato)diboron", e2, smiles=SMILES["B2pin2"]),
    participant("pd_catalyst", "catalyst", "Pd(PPh3)4", e2,
                amounts=[amount("catalyst_loading", quantity(5, "mol%"), e2)]),
    participant("acoh", "reagent", "AcOH", e2, smiles=SMILES["AcOH"],
                amounts=[amount("equivalents", quantity(1, "equiv"), e2)]),
    participant("thf", "solvent", "THF", e2, smiles=SMILES["THF"]),
]
records.append(record(
    "prose_initial_pd_trial", "reported_experiment", e2, pd_parts,
    [step(pd_parts, [fld("temperature", "reflux", e2)])],
    [fld("reaction_result", "complicated", e2)],
    ["The authors describe this initial feasibility trial as disappointing and complicated."],
    ["Reaction time, scale, product identities, conversion, workup, and yield are not reported.",
     "Supporting Information was mentioned by the paper but was not supplied or explicitly associated."],
))

# Table 1: sixteen monodentate-ligand optimization rows.
t1_rows = [
    (1, "PPh3", "THF", quantity(40, "°C"), 1.2, "89/11", 72, None),
    (2, "PPh3", "THF", quantity(40, "°C"), 9, "table dash (–)", 5, 82),
    (3, "TFP", "THF", quantity(40, "°C"), 5, "73/27", 54, None),
    (4, "P(t-Bu)3", "THF", quantity(40, "°C"), 1.3, "80/20", 73, None),
    (5, "P(n-Bu)3", "THF", quantity(40, "°C"), 1.3, "88/12", 64, None),
    (6, "P(o-tol)3", "THF", quantity(40, "°C"), 1.3, "80/20", 67, None),
    (7, "P(C6H4OMe-p)3 (L)", "THF", quantity(40, "°C"), 1, "90/10", 78, None),
    (8, "PCy3", "THF", quantity(40, "°C"), 1, "92/8", 79, None),
    (9, "PCy3", "THF", "r.t.", 1.3, "93/7", 80, None),
    (10, "PCy3", "THF", quantity(0, "°C"), 1, "89/11", 66, None),
    (11, "PCy3", "CH3CN", "r.t.", 1.5, "85/15", 34, None),
    (12, "PCy3", "PhCH3", "r.t.", 1, "89/11", 76, None),
    (13, "PCy3", "CH2Cl2", "r.t.", 1, "92/8", 71, None),
    (14, "PCy3", "Et2O", "r.t.", 1, "97/3", 76, None),
    (15, "PCy3", "Et2O", "r.t.", 1, "88/12", 69, None),
    (16, "P(C6H4OMe-p)3 (L)", "Et2O", "r.t.", 1, "100/0", 72, None),
]
solvent_smiles = {k: SMILES[k] for k in ["THF", "CH3CN", "PhCH3", "CH2Cl2", "Et2O"]}
for entry, ligand, solvent, temp, hours, ratio, yld, recovered in t1_rows:
    parts = [
        participant("substrate_1a", "reactant", "phenylallene 1a", e2, smiles=SMILES["1a"],
                    amounts=[amount("amount", quantity(0.2, "mmol"), e2)]),
        participant("diboron", "reactant", "bis(pinacolato)diboron", e2, smiles=SMILES["B2pin2"],
                    amounts=[amount("amount", quantity(0.24, "mmol"), e2)]),
        participant("cucl", "catalyst", "CuCl", e2, smiles=SMILES["CuCl"],
                    amounts=[amount("catalyst_loading", quantity(5, "mol%"), e2)]),
        participant("ligand", "catalyst", ligand, e2,
                    amounts=[amount("ligand_loading", quantity(10 if entry == 15 else 6, "mol%"), e2)]),
        participant("meoh", "reagent", "MeOH", e2, smiles=SMILES["MeOH"],
                    amounts=[amount("amount", quantity(0.4, "mmol"), e2)]),
        participant("solvent", "solvent", solvent, e2, smiles=solvent_smiles[solvent]),
        participant("product_z2a", "product", "Z-2a", e2, smiles=SMILES["Z-2a"]),
        participant("product_3a", "product", "3a", e2, smiles=SMILES["3a"]),
    ]
    if entry != 2:
        parts.insert(4, participant(
            "naotbu", "reagent", "NaO-t-Bu", e2, smiles=SMILES["NaOtBu"],
            amounts=[amount("loading", quantity(20, "mol%"), e2)],
        ))
    outcomes = [
        fld("Z-2a_to_3a_ratio", ratio, e2, ["product_z2a", "product_3a"]),
        fld("Z-2a_yield", quantity(yld, "%"), e2, ["product_z2a"]),
        fld("yield_measurement_basis", "1H NMR using 1,3,5-trimethylbenzene as internal standard", e2),
    ]
    if recovered is not None:
        outcomes.append(fld("recovered_starting_material_yield", quantity(recovered, "%"), e2,
                            ["substrate_1a"]))
    notes = []
    if entry == 2:
        notes.append("Table 1 footnote d states that NaO-t-Bu was not added.")
    if entry == 15:
        notes.append("Table 1 footnote g overrides the shared 6 mol% ligand loading: 10 mol% PCy3 was used.")
    records.append(record(
        f"table1_entry{entry}", "optimization_entry", e2, parts,
        [step(parts, [fld("temperature", temp, e2), fld("time", quantity(hours, "h"), e2),
                      fld("solvent", solvent, e2)])], outcomes, notes,
        ["Atmosphere, solvent volume, workup, and purification are not reported for this optimization row.",
         "Product structures are machine candidates and remain unverified.",
         "Supporting Information was not supplied or explicitly associated."],
    ))

# Table 2: arylallene scope under conditions A. Entry 2 is enriched with page-5 procedure evidence.
e3 = ev(3)
for entry, substrate_label, substrate_id, minutes, yld, product_label in SUBSTRATES_T2:
    evidence = ev(3, 5) if entry == 2 else e3
    if entry == 2:
        parts = [
            participant("substrate", "reactant", substrate_label, evidence, smiles=SMILES[substrate_id],
                        amounts=[amount("mass", quantity(1.0102, "g"), ev(5)), amount("amount", quantity(8.61, "mmol"), ev(5))]),
            participant("diboron", "reactant", "bis(pinacolato)diboron", evidence, smiles=SMILES["B2pin2"],
                        amounts=[amount("mass", quantity(2.6200, "g"), ev(5)), amount("amount", quantity(10.33, "mmol"), ev(5))]),
            participant("cucl", "catalyst", "CuCl", evidence, smiles=SMILES["CuCl"],
                        amounts=[amount("mass", quantity(42.6, "mg"), ev(5)), amount("amount", quantity(0.43, "mmol"), ev(5)), amount("catalyst_loading", quantity(5, "mol%"), e3)]),
            participant("ligand", "catalyst", "P(C6H4OMe-p)3", evidence,
                        amounts=[amount("mass", quantity(182.0, "mg"), ev(5)), amount("amount", quantity(0.52, "mmol"), ev(5)), amount("ligand_loading", quantity(6, "mol%"), e3)]),
            participant("naotbu", "reagent", "NaO-t-Bu", evidence, smiles=SMILES["NaOtBu"],
                        amounts=[amount("mass", quantity(165.4, "mg"), ev(5)), amount("amount", quantity(1.72, "mmol"), ev(5)), amount("loading", quantity(20, "mol%"), e3)]),
            participant("meoh", "reagent", "MeOH", evidence, smiles=SMILES["MeOH"],
                        amounts=[amount("volume", quantity(0.7, "mL"), ev(5)), amount("mass", quantity(551.7, "mg"), ev(5)), amount("amount", quantity(17.22, "mmol"), ev(5))]),
            participant("solvent", "solvent", "Et2O", evidence, smiles=SMILES["Et2O"],
                        amounts=[amount("volume", quantity(20, "mL"), ev(5))]),
            participant("product", "product", product_label, evidence, smiles=SMILES["Z-2a"]),
        ]
        conditions = [
            fld("atmosphere", "argon", ev(5)), fld("temperature", "r.t.", evidence),
            fld("time", quantity(20, "min"), evidence), fld("operation", "monitored by TLC", ev(5)),
            fld("workup", "filtered through a short silica-gel column with Et2O and concentrated", ev(5)),
            fld("purification", "silica-gel chromatography; petroleum ether/ethyl ether = 50/1", ev(5)),
        ]
        outcomes = [
            fld("isolated_yield", quantity(69, "%"), evidence, ["product"]),
            fld("isolated_product_mass", quantity(1.4544, "g"), ev(5), ["product"]),
            fld("yield_measurement_basis", "isolated", evidence),
        ]
        unresolved = [
            "The exact product stereochemical SMILES remains an unverified machine candidate.",
            "Supporting Information was not supplied or explicitly associated.",
        ]
    else:
        parts = [
            participant("substrate", "reactant", substrate_label, evidence, smiles=SMILES[substrate_id],
                        amounts=[amount("amount", quantity(0.5, "mmol"), evidence)]),
            participant("diboron", "reactant", "bis(pinacolato)diboron", evidence, smiles=SMILES["B2pin2"],
                        amounts=[amount("amount", quantity(0.6, "mmol"), evidence)]),
            participant("cucl", "catalyst", "CuCl", evidence, smiles=SMILES["CuCl"],
                        amounts=[amount("catalyst_loading", quantity(5, "mol%"), evidence)]),
            participant("ligand", "catalyst", "P(C6H4OMe-p)3", evidence,
                        amounts=[amount("ligand_loading", quantity(6, "mol%"), evidence)]),
            participant("naotbu", "reagent", "NaO-t-Bu", evidence, smiles=SMILES["NaOtBu"],
                        amounts=[amount("loading", quantity(20, "mol%"), evidence)]),
            participant("meoh", "reagent", "MeOH", evidence, smiles=SMILES["MeOH"],
                        amounts=[amount("amount", quantity(1.0, "mmol"), evidence)]),
            participant("solvent", "solvent", "Et2O", evidence, smiles=SMILES["Et2O"],
                        amounts=[amount("volume", quantity(2, "mL"), evidence)]),
            participant("product", "product", product_label, evidence,
                        smiles=SMILES["Z-2a"] if product_label == "Z-2a" else None),
        ]
        conditions = [fld("temperature", "r.t.", evidence), fld("time", quantity(minutes, "min"), evidence),
                      fld("operation", "monitored by TLC on silica gel", evidence)]
        outcomes = [fld("isolated_yield", quantity(yld, "%"), evidence, ["product"]),
                    fld("yield_measurement_basis", "isolated", evidence)]
        unresolved = [
            "Atmosphere, workup, and purification are not reported for this table row.",
            "The product drawing/label has not been independently converted to a verified structure.",
            "Supporting Information was not supplied or explicitly associated.",
        ]
    records.append(record(
        f"table2_entry{entry}", "substrate_scope_entry", evidence, parts,
        [step(parts, conditions)], outcomes,
        ["Table 2 footnote b identifies entry 2 as a one-gram-scale reaction."] if entry == 2 else [],
        unresolved,
    ))

# Table 3: bidentate-ligand optimization rows.
t3_rows = [
    (1, "dppe", "THF", quantity(40, "°C"), 1.1, "71/29", 47),
    (2, "Xantphos", "THF", quantity(40, "°C"), 1, "74/26", 23),
    (3, "DPEphos", "THF", quantity(40, "°C"), 1.2, "84/16", 70),
    (4, "dppf", "THF", quantity(40, "°C"), 1.1, "93/7", 56),
    (5, "BINAP", "THF", quantity(40, "°C"), 1.1, "93/7", 57),
    (6, "BIPHEP", "THF", quantity(40, "°C"), 1, "95/5", 62),
    (7, "BIPHEP", "THF", "r.t.", 1, "95/5", 63),
    (8, "BIPHEP", "THF", quantity(0, "°C"), 1, "95/5", 57),
    (9, "BIPHEP", "CH3CN", "r.t.", 1, "table dash (–)", "NR"),
    (10, "BIPHEP", "Et2O", "r.t.", 1, "89/11", 57),
    (11, "BIPHEP", "PhCH3", "r.t.", 1, "93/7", 67),
    (12, "BIPHEP", "CH2Cl2", "r.t.", 1, "93/7", 69),
]
for entry, ligand, solvent, temp, hours, ratio, yld in t3_rows:
    parts = [
        participant("substrate_1a", "reactant", "phenylallene 1a", e3, smiles=SMILES["1a"],
                    amounts=[amount("amount", quantity(0.2, "mmol"), e3)]),
        participant("diboron", "reactant", "bis(pinacolato)diboron", e3, smiles=SMILES["B2pin2"],
                    amounts=[amount("amount", quantity(0.24, "mmol"), e3)]),
        participant("cucl", "catalyst", "CuCl", e3, smiles=SMILES["CuCl"],
                    amounts=[amount("catalyst_loading", quantity(5, "mol%"), e3)]),
        participant("ligand", "catalyst", ligand, e3,
                    amounts=[amount("ligand_loading", quantity(5, "mol%"), e3)]),
        participant("naotbu", "reagent", "NaO-t-Bu", e3, smiles=SMILES["NaOtBu"],
                    amounts=[amount("loading", quantity(20, "mol%"), e3)]),
        participant("meoh", "reagent", "MeOH", e3, smiles=SMILES["MeOH"],
                    amounts=[amount("amount", quantity(0.4, "mmol"), e3)]),
        participant("solvent", "solvent", solvent, e3, smiles=solvent_smiles[solvent]),
        participant("product_3a", "product", "3a", e3, smiles=SMILES["3a"]),
        participant("product_z2a", "product", "Z-2a", e3, smiles=SMILES["Z-2a"]),
    ]
    outcomes = [fld("3a_to_Z-2a_ratio", ratio, e3, ["product_3a", "product_z2a"])]
    if yld == "NR":
        outcomes.append(fld("reaction_result", "NR", e3))
    else:
        outcomes.extend([
            fld("3a_yield", quantity(yld, "%"), e3, ["product_3a"]),
            fld("yield_measurement_basis", "1H NMR using 1,3,5-trimethylbenzene as internal standard", e3),
        ])
    records.append(record(
        f"table3_entry{entry}", "optimization_entry", e3, parts,
        [step(parts, [fld("temperature", temp, e3), fld("time", quantity(hours, "h"), e3),
                      fld("solvent", solvent, e3)])], outcomes, [],
        ["Atmosphere, solvent volume, workup, and purification are not reported for this optimization row.",
         "The product structures remain unverified machine candidates.",
         "For entry 9, the table reports NR and a dash rather than a numeric yield/selectivity."] if entry == 9 else
        ["Atmosphere, solvent volume, workup, and purification are not reported for this optimization row.",
         "The product structures remain unverified machine candidates.",
         "Supporting Information was not supplied or explicitly associated."],
    ))

# Table 4: scope under conditions B. Entry 2 is merged with the detailed procedure on page 5.
e4 = ev(4)
for entry, substrate_label, substrate_id, minutes, yld, product_label, ratio, before_sep in SUBSTRATES_T4:
    evidence = ev(4, 5, 6) if entry == 2 else e4
    ligand = "dppf" if entry >= 12 else "BIPHEP"
    if entry == 2:
        parts = [
            participant("substrate", "reactant", substrate_label, evidence, smiles=SMILES[substrate_id],
                        amounts=[amount("mass", quantity(1.0010, "g"), ev(5)), amount("amount", quantity(8.61, "mmol"), ev(5))]),
            participant("diboron", "reactant", "bis(pinacolato)diboron", evidence, smiles=SMILES["B2pin2"],
                        amounts=[amount("mass", quantity(2.6200, "g"), ev(5)), amount("amount", quantity(10.33, "mmol"), ev(5))]),
            participant("cucl", "catalyst", "CuCl", evidence, smiles=SMILES["CuCl"],
                        amounts=[amount("mass", quantity(42.6, "mg"), ev(5)), amount("amount", quantity(0.43, "mmol"), ev(5)), amount("catalyst_loading", quantity(5, "mol%"), e4)]),
            participant("ligand", "catalyst", "BIPHEP", evidence,
                        amounts=[amount("mass", quantity(224.7, "mg"), ev(5)), amount("amount", quantity(0.43, "mmol"), ev(5)), amount("ligand_loading", quantity(5, "mol%"), e4)]),
            participant("naotbu", "reagent", "NaO-t-Bu", evidence, smiles=SMILES["NaOtBu"],
                        amounts=[amount("mass", quantity(165.4, "mg"), ev(5)), amount("amount", quantity(1.72, "mmol"), ev(5)), amount("loading", quantity(20, "mol%"), e4)]),
            participant("meoh", "reagent", "MeOH", evidence, smiles=SMILES["MeOH"],
                        amounts=[amount("volume", quantity(0.7, "mL"), ev(5)), amount("mass", quantity(551.7, "mg"), ev(5)), amount("amount", quantity(17.22, "mmol"), ev(5))]),
            participant("solvent", "solvent", "THF", evidence, smiles=SMILES["THF"],
                        amounts=[amount("volume", quantity(20, "mL"), ev(5))]),
            participant("product_major", "product", product_label, evidence, smiles=SMILES["3a"]),
            participant("product_minor", "product", "Z-2a", evidence, smiles=SMILES["Z-2a"]),
        ]
        conditions = [
            fld("atmosphere", "argon", ev(5)), fld("temperature", "r.t.", evidence),
            fld("time", quantity(20, "min"), evidence), fld("operation", "monitored by TLC", ev(5)),
            fld("workup", "filtered through a short silica-gel column with Et2O and concentrated", ev(5)),
            fld("purification", "silica-gel chromatography; petroleum ether/ethyl ether = 50/1", ev(5)),
        ]
        outcomes = [
            fld("combined_isolated_yield_3_plus_Z-2", quantity(70, "%"), evidence,
                ["product_major", "product_minor"]),
            fld("isolated_product_mixture_mass", quantity(1.4630, "g"), ev(5),
                ["product_major", "product_minor"]),
            fld("3_to_Z-2_ratio", ratio, evidence, ["product_major", "product_minor"]),
            fld("ratio_measurement_basis", "molar ratio by NMR", ev(5)),
            fld("yield_measurement_basis", "isolated product mixture", evidence),
        ]
        unresolved = [
            "The page-6 text continues characterization of 3a but does not add a new reaction experiment.",
            "The isolated material is a 3a/Z-2a mixture; individual component masses/yields are not reported.",
            "Supporting Information was not supplied or explicitly associated.",
        ]
    else:
        parts = [
            participant("substrate", "reactant", substrate_label, evidence, smiles=SMILES[substrate_id],
                        amounts=[amount("amount", quantity(0.5, "mmol"), evidence)]),
            participant("diboron", "reactant", "bis(pinacolato)diboron", evidence, smiles=SMILES["B2pin2"],
                        amounts=[amount("amount", quantity(0.6, "mmol"), evidence)]),
            participant("cucl", "catalyst", "CuCl", evidence, smiles=SMILES["CuCl"],
                        amounts=[amount("catalyst_loading", quantity(5, "mol%"), evidence)]),
            participant("ligand", "catalyst", ligand, evidence,
                        amounts=[amount("ligand_loading", quantity(5, "mol%"), evidence)]),
            participant("naotbu", "reagent", "NaO-t-Bu", evidence, smiles=SMILES["NaOtBu"],
                        amounts=[amount("loading", quantity(20, "mol%"), evidence)]),
            participant("meoh", "reagent", "MeOH", evidence, smiles=SMILES["MeOH"],
                        amounts=[amount("amount", quantity(1.0, "mmol"), evidence)]),
            participant("solvent", "solvent", "THF", evidence, smiles=SMILES["THF"],
                        amounts=[amount("volume", quantity(2, "mL"), evidence)]),
            participant("product_major", "product", product_label, evidence,
                        smiles=SMILES["3a"] if product_label == "3a" else None),
            participant("product_minor", "product", "corresponding Z-2 regioisomer", evidence),
        ]
        conditions = [fld("temperature", "r.t.", evidence), fld("time", quantity(minutes, "min"), evidence)]
        outcomes = [
            fld("combined_isolated_yield_3_plus_Z-2", quantity(yld, "%"), evidence,
                ["product_major", "product_minor"]),
            fld("3_to_Z-2_ratio", ratio, evidence, ["product_major", "product_minor"]),
            fld("yield_measurement_basis", "isolated product mixture", evidence),
        ]
        if before_sep:
            outcomes.append(fld("3_to_Z-2_ratio_before_separation", before_sep, evidence,
                                ["product_major", "product_minor"]))
        unresolved = [
            "Atmosphere, workup, and purification are not reported for this scope row.",
            "The scope product structures remain unverified; non-3a products retain source labels with null SMILES.",
            "Supporting Information was not supplied or explicitly associated.",
        ]
    notes = []
    if entry == 2:
        notes.append("Table 4 footnote c identifies entry 2 as a one-gram-scale reaction.")
    if entry >= 12:
        notes.append("Table 4 footnote e overrides the header ligand: dppf was used.")
    if before_sep:
        notes.append("The table footnote reports a separate selectivity measured before separation.")
    records.append(record(
        f"table4_entry{entry}", "substrate_scope_entry", evidence, parts,
        [step(parts, conditions)], outcomes, notes, unresolved,
    ))

# Scheme 2: two deuterium-labeling experiments.
e45 = ev(4, 5)
for suffix, ligand, ligand_loading, solvent, product, yld, dinc, ratio in [
    ("conditions_A", "P(C6H4OMe-p)3", 6, "Et2O", "Z-2a-d", 72, 97, None),
    ("conditions_B", "BIPHEP", 5, "THF", "3a-d", 61, 91, "≥94/6"),
]:
    parts = [
        participant("substrate_1a", "reactant", "phenylallene 1a", e45, smiles=SMILES["1a"]),
        participant("diboron", "reactant", "bis(pinacolato)diboron", e45, smiles=SMILES["B2pin2"],
                    amounts=[amount("equivalents", quantity(1.2, "equiv"), ev(5))]),
        participant("cucl", "catalyst", "CuCl", e45, smiles=SMILES["CuCl"],
                    amounts=[amount("catalyst_loading", quantity(5, "mol%"), ev(5))]),
        participant("ligand", "catalyst", ligand, e45,
                    amounts=[amount("ligand_loading", quantity(ligand_loading, "mol%"), ev(5))]),
        participant("naotbu", "reagent", "NaO-t-Bu", e45, smiles=SMILES["NaOtBu"],
                    amounts=[amount("loading", quantity(20, "mol%"), ev(5))]),
        participant("meod", "reagent", "MeOD", e45,
                    amounts=[amount("equivalents", quantity(2, "equiv"), ev(5))]),
        participant("solvent", "solvent", solvent, e45, smiles=SMILES[solvent]),
        participant("product", "product", product, e45),
    ]
    outcomes = [
        fld("reported_yield", quantity(yld, "%"), e45, ["product"]),
        fld("deuterium_incorporation", quantity(dinc, "%"), e45, ["product"]),
    ]
    if ratio:
        outcomes.append(fld("3a-d_to_Z-2a-d_ratio", ratio, e45, ["product"]))
    records.append(record(
        f"scheme2_deuterium_{suffix}", "reported_experiment", e45, parts,
        [step(parts, [fld("temperature", "r.t.", ev(5)), fld("time", quantity(50, "min"), ev(5)),
                      fld("solvent", solvent, ev(5))])], outcomes,
        ["The prose locates deuterium incorporation at the allylic position for the 3a-d experiment."] if suffix == "conditions_B" else [],
        ["Reaction scale, solvent volume, atmosphere, workup, purification, and yield measurement basis are not reported.",
         "The labeled product structure remains source-label-only with null SMILES.",
         "Supporting Information was not supplied or explicitly associated."],
    ))

# Scheme 3: proposed catalytic rationale, not a reported experiment.
records.append(record(
    "scheme3_proposed_mechanism", "mechanism", ev(4, 5),
    [
        participant("generic_allene", "reactant", "generic R1-substituted allene 1", ev(5)),
        participant("diboron", "reactant", "B2(pin)2", ev(5), smiles=SMILES["B2pin2"]),
        participant("int1", "unspecified_agent", "Int 1", ev(5)),
        participant("int2", "unspecified_agent", "Int 2", ev(5)),
        participant("product_z2", "product", "Z-2", ev(5)),
        participant("product_3", "product", "3", ev(5)),
    ], [], [],
    ["Scheme 3 proposes ligand-controlled borylcupration followed by gamma-protonolysis; the prose states alpha-protonation cannot be completely excluded."],
    ["This is a proposed mechanism, not an independently observed experiment; no yields or conditions are assigned to intermediates.",
     "Generic R1 and organocopper intermediates are not represented as unique verified structures."],
))


coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1,
            "state": "attempted",
            "regions": [
                {
                    "region": "page 1 center-right, Scheme 1 monohydroboration product map",
                    "finding": "Generic six-product regio-/stereoisomer map; classified as a general scheme, not a reported experiment.",
                    "evidence_ids": ev(1),
                },
                {
                    "region": "page 1 lower two-column introduction",
                    "finding": "Prior-literature hydroboration examples and background discussion; not imported as experiments of this paper.",
                    "evidence_ids": ev(1),
                },
            ],
            "record_ids": [f"{DOC}:scheme1_general_monohydroboration_map"],
            "unresolved": ["Generic R1 structures do not define unique molecules; SI is mentioned but not supplied/associated."],
        },
        {
            "page": 2,
            "state": "attempted",
            "regions": [
                {
                    "region": "page 2 upper half, Table 1 including scheme, rows 1-16 and footnotes a-g",
                    "finding": "Sixteen distinct monodentate-ligand optimization experiments; entry 2 omits NaO-t-Bu and reports 82% recovered starting material, entry 15 uses 10 mol% PCy3.",
                    "evidence_ids": ev(2),
                },
                {
                    "region": "page 2 lower-left opening paragraph",
                    "finding": "Separate initial Pd(PPh3)4/AcOH trial in refluxing THF reported as complicated; Table 1 entry 1 prose is duplicate contextual evidence, not another experiment.",
                    "evidence_ids": ev(2),
                },
                {
                    "region": "page 2 lower-right conditions-A discussion",
                    "finding": "Narrative interpretation of Table 1 and forward reference to Table 2; no extra experiment beyond the table rows and one-gram entry later detailed on page 5.",
                    "evidence_ids": ev(2),
                },
            ],
            "record_ids": [f"{DOC}:prose_initial_pd_trial"] + [f"{DOC}:table1_entry{i}" for i in range(1, 17)],
            "unresolved": ["Most optimization rows omit atmosphere, solvent volume, workup and purification."],
        },
        {
            "page": 3,
            "state": "attempted",
            "regions": [
                {
                    "region": "page 3 upper half, Table 2 rows 1-9 and footnotes",
                    "finding": "Nine distinct arylallene scope experiments under conditions A; entry 2 is the one-gram experiment merged with the detailed page-5 procedure.",
                    "evidence_ids": ev(3),
                },
                {
                    "region": "page 3 lower half, Table 3 rows 1-12 and footnotes",
                    "finding": "Twelve distinct bidentate-ligand optimization experiments; entry 9 reports NR and a table dash rather than numeric yield/selectivity.",
                    "evidence_ids": ev(3),
                },
            ],
            "record_ids": [f"{DOC}:table2_entry{i}" for i in range(1, 10)] + [f"{DOC}:table3_entry{i}" for i in range(1, 13)],
            "unresolved": ["Most table rows omit atmosphere, workup and purification; product structures remain unverified machine candidates."],
        },
        {
            "page": 4,
            "state": "attempted",
            "regions": [
                {
                    "region": "page 4 upper half, Table 4 rows 1-14 and footnotes a-f",
                    "finding": "Fourteen distinct scope experiments under conditions B; rows 12-14 use dppf by footnote override, and rows 6/9/11/14 retain before-separation selectivity values.",
                    "evidence_ids": ev(4),
                },
                {
                    "region": "page 4 lower-right deuterium-labeling paragraph",
                    "finding": "Narrative outcomes for two Scheme 2 deuterium-labeling experiments; linked to the arrows displayed on page 5.",
                    "evidence_ids": ev(4),
                },
                {
                    "region": "page 4 lower-right mechanistic prose and Figure 1",
                    "finding": "Mechanistic rationale continues to Scheme 3 on page 5; Figure 1 is X-ray characterization of 3h, not a new reaction.",
                    "evidence_ids": ev(4),
                },
            ],
            "record_ids": [f"{DOC}:table4_entry{i}" for i in range(1, 15)] + [
                f"{DOC}:scheme2_deuterium_conditions_A", f"{DOC}:scheme2_deuterium_conditions_B",
                f"{DOC}:scheme3_proposed_mechanism",
            ],
            "unresolved": ["Scope rows omit several operational details; Figure 1 confirms a product structure but does not independently verify all machine structures."],
        },
        {
            "page": 5,
            "state": "attempted",
            "regions": [
                {
                    "region": "page 5 upper-left, Scheme 2 two reaction arrows",
                    "finding": "Two distinct MeOD labeling experiments with explicit ligand, solvent, time, yield and D incorporation.",
                    "evidence_ids": ev(5),
                },
                {
                    "region": "page 5 upper/right Experimental Section, two typical procedures",
                    "finding": "Detailed one-gram preparations merged into Table 2 entry 2 (Z-2a) and Table 4 entry 2 (3a/Z-2a mixture); not duplicated as new experiments.",
                    "evidence_ids": ev(5),
                },
                {
                    "region": "page 5 bottom, Scheme 3 catalytic cycles",
                    "finding": "Proposed ligand-controlled borylcupration/gamma-protonolysis mechanism; classified separately from experiments.",
                    "evidence_ids": ev(5),
                },
            ],
            "record_ids": [
                f"{DOC}:table2_entry2", f"{DOC}:table4_entry2",
                f"{DOC}:scheme2_deuterium_conditions_A", f"{DOC}:scheme2_deuterium_conditions_B",
                f"{DOC}:scheme3_proposed_mechanism",
            ],
            "unresolved": ["Scheme 2 omits scale, atmosphere, solvent volume, workup, purification and yield measurement basis."],
        },
        {
            "page": 6,
            "state": "attempted",
            "regions": [
                {
                    "region": "page 6 top-left continuation from page 5",
                    "finding": "Continuation of 3a MS/HRMS characterization for the Table 4 entry 2 preparation; no new reaction experiment.",
                    "evidence_ids": ev(6),
                },
                {
                    "region": "page 6 remaining acknowledgements, references and crystal-data note",
                    "finding": "No new experiment of this paper; references are prior work and the 3h crystal-data note is characterization, not a reaction.",
                    "evidence_ids": ev(6),
                },
            ],
            "record_ids": [f"{DOC}:table4_entry2"],
            "unresolved": ["No SI file or crystallographic data file was supplied; neither was inferred as associated source material."],
        },
    ],
}


def main():
    raw_path = Path(__file__).with_name("records_pages_0001_0006.json")
    raw_path.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
    coverage_path = BASE / "coverage" / "pages_0001_0006.json"
    coverage_path.parent.mkdir(parents=True, exist_ok=True)
    coverage_path.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

    tasks_path = BASE / "tasks.json"
    tasks = json.loads(tasks_path.read_text())
    for task in tasks:
        if task.get("document_id") == DOC and 1 <= int(task["task_id"].split(":page", 1)[1].split(":", 1)[0]) <= 6:
            page = int(task["task_id"].split(":page", 1)[1].split(":", 1)[0])
            task["visual_evidence_id"] = f"{DOC}:page{page}:image"
            task["state"] = "attempted"
            task["reason"] = "Original page image inspected and reaction-bearing regions reconciled into the coverage ledger."
    tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

    print(json.dumps({"records": len(records), "raw": str(raw_path), "coverage": str(coverage_path)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
