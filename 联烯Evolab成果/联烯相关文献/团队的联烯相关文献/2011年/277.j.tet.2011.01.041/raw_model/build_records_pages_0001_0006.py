#!/usr/bin/env python3
"""Build evidence-linked machine records for doc_bb7cac4025113344, PDF pages 1-6."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
DOC = "doc_bb7cac4025113344"


def ev(page: int, kind: str = "text") -> str:
    return f"{DOC}:page{page}:{kind}"


def fact(value, evidence=()):
    return {
        "value": value,
        "evidence_ids": list(evidence),
        "verification": "missing" if value is None else "unreviewed",
    }


def field(name, value, evidence, targets=None):
    item = {"name": name, "fact": fact(value, evidence)}
    if targets:
        item["target_entity_ids"] = list(targets)
    return item


def quantity(number, unit, raw_text=None, **extra):
    value = {"number": number, "unit": unit}
    if raw_text is not None:
        value["raw_text"] = raw_text
    value.update(extra)
    return value


def participant(entity_id, role, label, evidence, name=None, smiles=None, amounts=()):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence) if name is not None else fact(None),
        "smiles": fact(smiles, evidence) if smiles is not None else fact(None),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": list(amounts),
    }


def record(suffix, kind, evidence, participants, steps=(), outcomes=(), notes=(), unresolved=()):
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
        "notes": [fact(x, evidence) for x in notes],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": list(unresolved),
        },
    }


SMILES = {
    "1a": "O=C(NCc1ccccc1)C=C=C(C)C",
    "1b": "O=C(NCCCC)C=C=C(C)C",
    "1c": "CC(C)(C)NC(=O)C=C=C(C)C",
    "1d": "O=C(NCc1ccccc1)C=C=C(C)CC",
    "1e": "O=C(NCc1ccccc1)C(C)=C=C(C)C",
    "2a": "C#CC(C)(C)OC(=O)OC",
    "2b": "C#CC(CC)(CC)OC(=O)OC",
    "2c": "C#CC1(CCCCC1)OC(=O)OC",
    "2d": "C#CC(C)(c1ccccc1)OC(=O)OC",
    "2e": "CCCCC#CC(C)(C)OC(=O)OC",
    "2f": "c1ccccc1C#CC(C)(C)OC(=O)OC",
    "2g": "CC(OC(=O)OC)C#Cc1ccccc1",
    "2h": "C#CCOC(=O)OC",
    "Pd(OAc)2": "[Pd+2].CC(=O)[O-].CC(=O)[O-]",
    "K2CO3": "[K+].[K+].[O-]C([O-])=O",
    "DMSO": "CS(C)=O",
    "TFP": "P(c1ccco1)(c1ccco1)c1ccco1",
    "mesitylene": "Cc1cc(C)cc(C)c1",
}


def amount(name, number, unit, evidence):
    return field(name, quantity(number, unit), evidence)


def p_labeled(label, role, evidence, name=None, amounts=()):
    return participant(label.replace("(+)-", "plus_").replace("'", "prime"), role, label, evidence,
                       name=name, smiles=SMILES.get(label.replace("(+)-", "")), amounts=amounts)


records = []

# Table 1. Entry 1 is the same 3aa batch as Table 2 entry 1 and section 4.2.1,
# so it is built below with the scope records and cited from all three pages.
table1 = [
    # entry, ligand, solvent, temperature, time, NMR yield, recovery, 2a equiv
    (2, "TFP", "Dioxane", 38, 15, 8, 37, 2.0),
    (3, "TFP", "MeCN", 38, 15, 5, 60, 2.0),
    (4, "TFP", "DMF", 38, 15, 43, 32, 2.0),
    (5, "TFP", "DMA", 38, 15, 27, 43, 2.0),
    (6, "TFP", "DMSO", 50, 11, 52, 0, 2.0),
    (7, "dppe", "DMSO", 38, 23, 12, 80, 2.0),
    (8, "SPhos", "DMSO", 38, 23, 2, 75, 2.0),
    (9, "TFP", "DMSO", 38, 15, 58, 11, 1.0),
    (10, "TFP", "DMSO", 38, 15, 72, 1, 1.5),
    (11, "TFP", "DMSO", 38, 15, 70, None, 2.5),
]
for entry, ligand, solvent, temp, time, yld, recovery, equiv2a in table1:
    evidence = [ev(1, "image"), ev(1)]
    if entry in (9, 10, 11):
        evidence += [ev(2, "image"), ev(2)]
    parts = [
        participant("1a", "reactant", "1a", evidence, "N-benzyl 4-methylpenta-2,3-dienamide",
                    SMILES["1a"], [amount("amount", 0.2, "mmol", evidence)]),
        participant("2a", "reactant", "2a", evidence, "methyl 2-methylbut-3-yn-2-yl carbonate",
                    SMILES["2a"], [amount("equivalents", equiv2a, "equiv", evidence)] +
                    ([amount("amount", 0.4, "mmol", evidence)] if entry <= 8 else [])),
        participant("3aa", "product", "3aa", evidence,
                    "(Z)-N-benzyl 5,5-dimethyl-4-(3'-methylbuta-1',2'-dienyl)furan-2(5H)-imine"),
        participant("PdOAc2", "catalyst", "Pd(OAc)2", evidence, "palladium(II) acetate",
                    SMILES["Pd(OAc)2"], [amount("catalyst_loading", 5, "mol%", evidence)]),
        participant("ligand", "catalyst", ligand, evidence, amounts=[amount("catalyst_loading", 10, "mol%", evidence)]),
        participant("K2CO3", "reagent", "K2CO3", evidence, "potassium carbonate", SMILES["K2CO3"],
                    [amount("amount", 0.2, "mmol", evidence), amount("equivalents", 1.0, "equiv", evidence)]),
        participant("solvent", "solvent", solvent, evidence, smiles=SMILES.get(solvent)),
    ]
    outcomes = [
        field("nmr_yield", quantity(yld, "%"), evidence, ["3aa"]),
        field("yield_measurement_basis", "1H NMR with mesitylene as internal standard", evidence, ["3aa"]),
    ]
    if recovery is not None:
        outcomes.append(field("recovered_starting_material_yield", quantity(recovery, "%"), evidence, ["1a"]))
    else:
        outcomes.append(field("recovered_starting_material_yield", None, evidence, ["1a"]))
    steps = [{
        "step_id": "cyclization",
        "participant_ids": [p["entity_id"] for p in parts],
        "conditions": [
            field("temperature", quantity(temp, "°C"), evidence),
            field("time", quantity(time, "h"), evidence),
            field("atmosphere", "N2", evidence),
            field("solvent", solvent, evidence),
            field("solvent_volume", None, evidence),
            field("workup", None, evidence),
            field("purification", None, evidence),
        ],
    }]
    unresolved = ["Product and substrate structures are machine candidates and are not source-verified."]
    if recovery is None:
        unresolved.append("Table 1 entry 11 does not report recovery of 1a; the blank is not interpreted as zero.")
    records.append(record(f"table1_entry{entry}", "optimization_entry", evidence, parts, steps, outcomes,
                          unresolved=unresolved))


scope = [
    # entry, substrate, carbonate, product, page, temp, time, NMR, isolated, masses/amounts, product mass, eluent
    (1, "1a", "2a", "3aa", 3, 38, 15, 70, 54, (41.4,.21,58.0,.41,2.3,.010,4.5,.019,27.0,.20),29.5,"petroleum ether (30-60 °C)/ethyl acetate 7/1"),
    (2, "1a", "2b", "3ab", 3, 38, 13, 58, 42, (39.8,.20,68.5,.40,2.2,.010,4.5,.019,27.7,.20),24.6,"petroleum ether/ethyl acetate 7/1 to 5/1"),
    (3, "1a", "2c", "3ac", 4, 38, 14, 74, 56, (40.7,.20,73.0,.40,2.2,.010,4.7,.020,28.1,.20),34.9,"petroleum ether/ethyl acetate 7/1 to 5/1 to 3/1"),
    (4, "1a", "2d", "3ad", 4, 50, 11, 61, 57, (40.1,.20,83.1,.41,2.3,.010,4.6,.020,27.7,.20),37.4,"petroleum ether/ethyl acetate 7/1 to 5/1 to 3/1"),
    (5, "1a", "2e", "3ae", 4, 50, 19, 77, 70, (39.5,.20,80.5,.41,2.2,.010,4.7,.020,27.8,.20),44.6,"petroleum ether/ethyl acetate 7/1"),
    (6, "1a", "2f", "3af", 4, 50, 15, 88, 72, (40.6,.20,86.3,.40,2.3,.010,4.7,.020,27.8,.20),49.8,"petroleum ether/ethyl acetate 5/1"),
    (7, "1b", "2e", "3be", 4, 50, 18, 73, 53, (33.2,.20,80.0,.41,2.3,.010,4.8,.021,27.8,.20),30.2,"petroleum ether/ethyl acetate 7/1 to 5/1"),
    (8, "1c", "2e", "3ce", 4, 50, 17, 79, 68, (33.8,.20,80.2,.41,2.3,.010,4.6,.020,27.6,.20),39.6,"petroleum ether/ethyl acetate 4/1 to 3/1 to 1/1"),
    (9, "1c", "2f", "3cf", 4, 50, 17, 95, 93, (34.0,.20,89.2,.41,2.2,.010,4.7,.020,27.7,.20),58.5,"petroleum ether/ethyl acetate 5/1 to 1/1.5"),
    (10,"1d", "2e", "3de", 4, 50, 14, 59, 51, (43.0,.20,80.2,.41,2.2,.010,4.7,.020,27.7,.20),34.2,"petroleum ether/ethyl acetate 8/1"),
    (11,"1e", "2a", "3ea", 5, 50, 15, 98, 89, (43.5,.20,58.1,.41,2.2,.010,4.6,.020,27.6,.20),50.5,"petroleum ether/ethyl acetate 7/1"),
    (12,"1e", "2c", "3ec", 5, 50, 23, 93, 91, (42.3,.20,73.7,.40,2.3,.010,4.8,.021,27.7,.20),57.2,"petroleum ether/ethyl acetate 10/1"),
    (13,"1e", "2d", "3ed", 5, 50, 14, 77, 73, (42.7,.20,80.9,.40,2.2,.010,4.8,.021,28.1,.20),49.6,"petroleum ether/ethyl acetate 10/1"),
    (14,"1e", "2f", "3ef", 5, 50, 14,100, 93, (42.9,.20,88.4,.41,2.3,.010,4.7,.020,27.6,.20),66.1,"petroleum ether/ethyl acetate 20/1"),
]
names = {
 "1a":"N-benzyl 4-methylpenta-2,3-dienamide", "1b":"N-(n-butyl) 4-methylpenta-2,3-dienamide",
 "1c":"N-(tert-butyl) 4-methylpenta-2,3-dienamide", "1d":"N-benzyl 4-ethyl-4-methyl allenamide",
 "1e":"N-benzyl 2,4,4-trimethyl allenamide", "2a":"methyl 2-methylbut-3-yn-2-yl carbonate",
 "2b":"propargylic carbonate 2b", "2c":"propargylic carbonate 2c", "2d":"methyl 2-phenylbut-3-yn-2-yl carbonate",
 "2e":"propargylic carbonate 2e (R5=n-Bu, R6=R7=Me)", "2f":"propargylic carbonate 2f (R5=Ph, R6=R7=Me)",
 "3aa":"(Z)-N-benzyl 5,5-dimethyl-4-(3'-methylbuta-1',2'-dienyl)furan-2(5H)-imine",
 "3ab":"(Z)-N-benzyl 5,5-dimethyl-4-(3'-ethylpenta-1',2'-dienyl)furan-2(5H)-imine",
 "3ac":"(Z)-N-benzyl 4-(3',3'-pentamethylenepropa-1',2'-dienyl)-5,5-dimethylfuran-2(5H)-imine",
 "3ad":"(Z)-N-benzyl 5,5-dimethyl-4-(3'-phenylbuta-1',2'-dienyl)furan-2(5H)-imine",
 "3ae":"(Z)-N-benzyl 5,5-dimethyl-4-(2'-methylocta-2',3'-dien-4'-yl)furan-2(5H)-imine",
 "3af":"(Z)-N-benzyl 5,5-dimethyl-4-(3'-methyl-1'-phenylbuta-1',2'-dienyl)furan-2(5H)-imine",
 "3be":"(Z)-N-(n-butyl) 5,5-dimethyl-4-(2'-methylocta-2',3'-dien-4'-yl)furan-2(5H)-imine",
 "3ce":"(Z)-N-(tert-butyl) 5,5-dimethyl-4-(2'-methylocta-2',3'-dien-4'-yl)furan-2(5H)-imine",
 "3cf":"(Z)-N-(tert-butyl) 5,5-dimethyl-4-(3'-methyl-1'-phenylbuta-1',2'-dienyl)furan-2(5H)-imine",
 "3de":"(Z)-N-benzyl 5-ethyl-5-methyl-4-(2'-methylocta-2',3'-dien-4'-yl)furan-2(5H)-imine",
 "3ea":"(Z)-N-benzyl 3,5,5-trimethyl-4-(3'-methylbuta-1',2'-dienyl)furan-2(5H)-imine",
 "3ec":"(Z)-N-benzyl 4-(3',3'-pentamethylenepropa-1',2'-dienyl)-3,5,5-trimethylfuran-2(5H)-imine",
 "3ed":"(Z)-N-benzyl 3,5,5-trimethyl-4-(3'-phenylbuta-1',2'-dienyl)furan-2(5H)-imine",
 "3ef":"(Z)-N-benzyl 3,5,5-trimethyl-4-(3'-methyl-1'-phenylbuta-1',2'-dienyl)furan-2(5H)-imine",
}

for entry, sub, carb, prod, page, temp, time, nmr, isolated, vals, prod_mass, eluent in scope:
    sub_mg, sub_mmol, carb_mg, carb_mmol, pd_mg, pd_mmol, tfp_mg, tfp_mmol, k_mg, k_mmol = vals
    evidence = [ev(2, "image"), ev(2), ev(page, "image"), ev(page)]
    if entry == 2:  # 3ab procedure starts on page 3; characterization continues on page 4.
        evidence += [ev(4, "image"), ev(4)]
    if entry == 11:  # 3ea charge is printed at the foot of page 4; outcome continues on page 5.
        evidence += [ev(4, "image"), ev(4)]
    if entry == 1:
        evidence = [ev(1, "image"), ev(1), ev(2, "image"), ev(2), ev(3, "image"), ev(3)]
        suffix, kind = "table1_entry1_table2_entry1_3aa", "optimization_entry"
    else:
        suffix, kind = f"table2_entry{entry}_{prod}", "substrate_scope_entry"
    parts = [
        participant(sub, "reactant", sub, evidence, names[sub], SMILES.get(sub),
                    [amount("mass", sub_mg, "mg", evidence), amount("amount", sub_mmol, "mmol", evidence)]),
        participant(carb, "reactant", carb, evidence, names[carb], SMILES.get(carb),
                    [amount("mass", carb_mg, "mg", evidence), amount("amount", carb_mmol, "mmol", evidence)]),
        participant(prod, "product", prod, evidence, names[prod]),
        participant("PdOAc2", "catalyst", "Pd(OAc)2", evidence, "palladium(II) acetate", SMILES["Pd(OAc)2"],
                    [amount("mass", pd_mg, "mg", evidence), amount("amount", pd_mmol, "mmol", evidence), amount("catalyst_loading", 5, "mol%", evidence)]),
        participant("TFP", "catalyst", "TFP", evidence, "tri(furan-2-yl)phosphine", SMILES["TFP"],
                    [amount("mass", tfp_mg, "mg", evidence), amount("amount", tfp_mmol, "mmol", evidence), amount("catalyst_loading", 10, "mol%", evidence)]),
        participant("K2CO3", "reagent", "K2CO3", evidence, "potassium carbonate", SMILES["K2CO3"],
                    [amount("mass", k_mg, "mg", evidence), amount("amount", k_mmol, "mmol", evidence), amount("equivalents", 1.0, "equiv", evidence)]),
        participant("DMSO", "solvent", "DMSO", evidence, "dimethyl sulfoxide", SMILES["DMSO"],
                    [amount("volume", 2, "mL", evidence)]),
    ]
    if entry == 1:
        parts += [
            participant("3aa_prime", "product", "3aa'", evidence, "N-attacked regioisomer 3aa'"),
            participant("mesitylene", "reagent", "mesitylene", evidence, smiles=SMILES["mesitylene"],
                        amounts=[amount("volume", 27, "uL", evidence), amount("amount", 0.2, "mmol", evidence)]),
        ]
    conditions = [
        field("temperature", quantity(temp, "°C"), evidence), field("time", quantity(time, "h"), evidence),
        field("solvent", "DMSO", evidence), field("atmosphere", "N2" if entry == 1 else None, evidence),
        field("operation", "heated with stirring" if entry == 1 else None, evidence),
        field("workup", "quenched with 10 mL H2O; extracted with ether (15 mL x3); washed with brine; dried over anhydrous Na2SO4; filtered and evaporated" if entry == 1 else None, evidence),
        field("purification", f"silica-gel chromatography; eluent {eluent}", evidence),
    ]
    outcomes = [
        field("nmr_yield", quantity(nmr, "%"), evidence, [prod]),
        field("nmr_yield_measurement_basis", "1H NMR with mesitylene as internal standard", evidence, [prod]),
        field("isolated_yield", quantity(isolated, "%"), evidence, [prod]),
        field("isolated_product_mass", quantity(prod_mass, "mg"), evidence, [prod]),
        field("isolated_yield_measurement_basis", "isolated after silica-gel chromatography", evidence, [prod]),
    ]
    notes = []
    unresolved = ["Product connectivity/stereochemistry and all candidate SMILES remain machine-unverified."]
    if entry == 1:
        outcomes += [field("regioselectivity", "O-attacked 3aa only; N-attacked 3aa' not observed", evidence, [prod, "3aa_prime"])]
        notes.append("Table 1 entry 1, Table 2 entry 1, and section 4.2.1 report the same 3aa batch and are merged here.")
    if entry == 6:
        notes.append("Section 4.2.6 outcome sentence says 3ae, while its heading, Table 2, formula, and characterization identify 3af; label discrepancy retained for review.")
        unresolved.append("Resolve the apparent 3ae/3af typographical discrepancy against authoritative source review.")
    if entry == 7:
        notes.append("Section 4.2.7 says 1a in the charge sentence, while the heading, Table 2, and mass/formula identify substrate 1b; discrepancy retained for review.")
        unresolved.append("Resolve the apparent 1a/1b typographical discrepancy against authoritative source review.")
    if entry == 14:
        notes.append("Section 4.2.14 outcome sentence says 3ed, while its heading, Table 2, formula, and characterization identify 3ef; label discrepancy retained for review.")
        unresolved.append("Resolve the apparent 3ed/3ef typographical discrepancy against authoritative source review.")
    records.append(record(suffix, kind, evidence, parts,
                          [{"step_id":"cyclization", "participant_ids":[p["entity_id"] for p in parts], "conditions":conditions}],
                          outcomes, notes, unresolved))


# Scheme 1: distinct failed/unsuccessful experiments.
for label, carbonate, outcome in [("scheme1_2g_complicated", "2g", "complicated"),
                                  ("scheme1_2h_no_reaction", "2h", "no reaction")]:
    evidence = [ev(2, "image"), ev(2)]
    parts = [
        participant("1a", "reactant", "1a", evidence, names["1a"], SMILES["1a"]),
        participant(carbonate, "reactant", carbonate, evidence, f"propargylic carbonate {carbonate}", SMILES[carbonate]),
        participant("PdOAc2", "catalyst", "Pd(OAc)2", evidence, smiles=SMILES["Pd(OAc)2"], amounts=[amount("catalyst_loading",5,"mol%",evidence)]),
        participant("TFP", "catalyst", "TFP", evidence, smiles=SMILES["TFP"], amounts=[amount("catalyst_loading",10,"mol%",evidence)]),
        participant("K2CO3", "reagent", "K2CO3", evidence, smiles=SMILES["K2CO3"], amounts=[amount("equivalents",1,"equiv",evidence)]),
        participant("DMSO", "solvent", "DMSO", evidence, smiles=SMILES["DMSO"]),
    ]
    records.append(record(label, "reported_experiment", evidence, parts,
        [{"step_id":"cyclization_attempt", "participant_ids":[p["entity_id"] for p in parts], "conditions":[
            field("temperature",None,evidence), field("time",None,evidence), field("solvent","DMSO",evidence),
            field("atmosphere",None,evidence), field("workup",None,evidence), field("purification",None,evidence)]}],
        [field("reaction_outcome", outcome, evidence)],
        unresolved=["Scheme 1 does not report scale, temperature, time, atmosphere, workup, purification, or isolated products."]))


# Scheme 2 is explicitly proposed mechanistic material, not a batch experiment.
evidence = [ev(2, "image"), ev(2), ev(3, "image"), ev(3)]
parts = [participant("generic_1", "reactant", "1", evidence, "generic 2,3-allenamide"),
         participant("generic_2", "reactant", "2", evidence, "generic propargylic carbonate"),
         participant("generic_3", "product", "3", evidence, "generic beta-allenyl furanimine")]
records.append(record("scheme2_mechanistic_pathways", "mechanism", evidence, parts, notes=[
    "Two proposed pathways are shown: Pd(0)-initiated via M1/M1' and M2, and Pd(II)-initiated via M3 and M4.",
    "The authors favor the Pd(0)-initiated pathway because the optically active carbonate probe gives racemic 3ad."
], unresolved=["Generic R-group structures and proposed intermediates are not isolated compounds and have no assigned SMILES."]))


# Section 4.1.1: preparation of new allenamide 1c.
evidence = [ev(3, "image"), ev(3)]
parts = [
    participant("bromoallene", "reactant", "1-bromo-3-methylbuta-1,2-diene", evidence,
                smiles="CC(C)=C=CBr", amounts=[amount("mass",2.0333,"g",evidence),amount("amount",13.83,"mmol",evidence)]),
    participant("tert_butylamine", "reactant", "t-BuNH2", evidence, "tert-butylamine", "CC(C)(C)N",
                [amount("mass",1.2102,"g",evidence),amount("amount",16.58,"mmol",evidence)]),
    participant("CO", "reactant", "CO", evidence, "carbon monoxide", "[C-]#[O+]", [field("pressure","25 atm",evidence)]),
    participant("1c", "product", "1c", evidence, names["1c"], SMILES["1c"]),
    participant("Et3N", "reagent", "Et3N", evidence, "triethylamine", "CCN(CC)CC",
                [amount("volume",2.4,"mL",evidence),amount("mass",1.7400,"g",evidence),amount("amount",17.23,"mmol",evidence)]),
    participant("PdPPh3_4", "catalyst", "Pd(PPh3)4", evidence, "tetrakis(triphenylphosphine)palladium(0)",
                amounts=[amount("mass",0.2012,"g",evidence),amount("amount",0.17,"mmol",evidence)]),
    participant("THF", "solvent", "THF", evidence, "tetrahydrofuran", "C1CCOC1", [amount("volume",15,"mL",evidence)]),
]
records.append(record("section4_1_1_synthesis_1c", "reported_experiment", evidence, parts,
    [{"step_id":"carbonylation", "participant_ids":[p["entity_id"] for p in parts], "conditions":[
        field("operation","charged sequentially to a glass-lined stainless-steel autoclave; pressurized with CO; stirred; CO released gently",evidence),
        field("temperature","r.t.",evidence), field("time",quantity(1.5,"h"),evidence), field("atmosphere","CO, 25 atm",evidence),
        field("workup","quenched with 10 mL water; added 20 mL CH2Cl2; separated; organic phase washed with dilute HCl then brine; dried over anhydrous Na2SO4; filtered and evaporated",evidence),
        field("purification","flash chromatography on silica gel (petroleum ether/ethyl acetate 10/1 to 1/1), then recrystallization from n-hexane/CH2Cl2",evidence)]}],
    [field("isolated_yield",quantity(47,"%"),evidence,["1c"]),field("isolated_product_mass",quantity(1.0913,"g"),evidence,["1c"]),
     field("product_appearance","white solid",evidence,["1c"]),
     field("melting_point",{"minimum":161.5,"maximum":162.0,"unit":"°C","raw_text":"161.5-162.0 °C"},evidence,["1c"])],
    unresolved=["Candidate structures remain machine-unverified; analytical characterization is not exhaustively structured."]))


# Section 4.3.1: optically active carbonate (+)-2d.
evidence = [ev(5, "image"), ev(5)]
parts = [
    participant("plus_alcohol", "reactant", "(+)-2-phenylbut-3-yn-2-ol", evidence,
                smiles="C#CC(C)(O)c1ccccc1", amounts=[amount("mass",305.3,"mg",evidence),amount("amount",2.09,"mmol",evidence),amount("enantiomeric_excess",95,"%",evidence)]),
    participant("NaH", "reagent", "NaH", evidence, "sodium hydride", "[Na+].[H-]",
                [amount("mass",90.2,"mg",evidence),amount("amount",2.25,"mmol",evidence),amount("reagent_assay",60,"%",evidence)]),
    participant("methyl_chloroformate", "reactant", "methyl chloroformate", evidence, smiles="COC(=O)Cl",
                amounts=[amount("mass",222.5,"mg",evidence),amount("amount",2.35,"mmol",evidence)]),
    participant("plus_2d", "product", "(+)-2d", evidence, "optically active methyl 2-phenylbut-3-yn-2-yl carbonate", SMILES["2d"]),
    participant("THF", "solvent", "THF", evidence, "tetrahydrofuran", "C1CCOC1",
                [amount("initial_volume",2,"mL",evidence),amount("alcohol_solution_volume",1,"mL",evidence),amount("chloroformate_solution_volume",1,"mL",evidence)]),
]
records.append(record("section4_3_1_synthesis_plus_2d", "reported_experiment", evidence, parts,
    [{"step_id":"carbonate_formation", "participant_ids":[p["entity_id"] for p in parts], "conditions":[
        field("operation","alcohol solution added slowly dropwise to NaH suspension under N2; stirred 1 h; cooled in ice bath; methyl chloroformate solution added dropwise; stirred 16 h at room temperature",evidence),
        field("atmosphere","N2",evidence), field("initial_temperature","r.t.",evidence), field("initial_time",quantity(1,"h"),evidence),
        field("addition_temperature","ice bath",evidence), field("time_at_room_temperature",quantity(16,"h"),evidence),
        field("workup","quenched with H2O; extracted with ether (15 mL x3); washed with brine; dried over anhydrous Na2SO4; filtered and evaporated",evidence),
        field("purification","silica-gel chromatography, petroleum ether/ethyl acetate 60/1 to 40/1",evidence)]}],
    [field("isolated_yield",quantity(81,"%"),evidence,["plus_2d"]),field("isolated_product_mass",quantity(345.6,"mg"),evidence,["plus_2d"]),
     field("product_enantiomeric_excess",quantity(95,"%"),evidence,["plus_2d"]),
     field("specific_rotation","[alpha]D20 +43.8 (c 1.02, CHCl3)",evidence,["plus_2d"])],
    notes=["The starting alcohol was obtained by preparative HPLC separation of racemic alcohol; absolute configuration is not assigned."],
    unresolved=["Absolute configuration is unknown; candidate structures remain machine-unverified."]))


# Scheme 3 / section 4.3.2: distinct optically active mechanistic probe.
evidence = [ev(2, "image"), ev(2), ev(3, "image"), ev(3), ev(5, "image"), ev(5)]
parts = [
    participant("1a", "reactant", "1a", evidence, names["1a"], SMILES["1a"],[amount("mass",20.3,"mg",evidence),amount("amount",0.10,"mmol",evidence)]),
    participant("plus_2d", "reactant", "(+)-2d", evidence, "optically active methyl 2-phenylbut-3-yn-2-yl carbonate", SMILES["2d"],[amount("mass",40.2,"mg",evidence),amount("amount",0.20,"mmol",evidence),amount("enantiomeric_excess",95,"%",evidence)]),
    participant("3ad_probe", "product", "3ad", evidence, names["3ad"]),
    participant("PdOAc2", "catalyst", "Pd(OAc)2", evidence, smiles=SMILES["Pd(OAc)2"], amounts=[amount("mass",1.2,"mg",evidence),amount("amount",0.005,"mmol",evidence),amount("catalyst_loading",5,"mol%",evidence)]),
    participant("TFP", "catalyst", "TFP", evidence, smiles=SMILES["TFP"], amounts=[amount("mass",2.4,"mg",evidence),amount("amount",0.010,"mmol",evidence),amount("catalyst_loading",10,"mol%",evidence)]),
    participant("K2CO3", "reagent", "K2CO3", evidence, smiles=SMILES["K2CO3"], amounts=[amount("mass",14.0,"mg",evidence),amount("amount",0.10,"mmol",evidence),amount("equivalents",1,"equiv",evidence)]),
    participant("DMSO", "solvent", "DMSO", evidence, smiles=SMILES["DMSO"], amounts=[amount("volume",1,"mL",evidence)]),
]
records.append(record("scheme3_section4_3_2_chiral_probe", "reported_experiment", evidence, parts,
    [{"step_id":"chiral_probe_cyclization", "participant_ids":[p["entity_id"] for p in parts], "conditions":[
        field("temperature",quantity(50,"°C"),evidence),field("time",None,evidence),field("solvent","DMSO",evidence),
        field("atmosphere",None,evidence),field("workup",None,evidence),field("purification","silica-gel chromatography, petroleum ether/ethyl acetate 4/1 to 3/1",evidence)]}],
    [field("isolated_yield",quantity(62,"%"),evidence,["3ad_probe"]),field("isolated_product_mass",quantity(20.7,"mg"),evidence,["3ad_probe"]),
     field("product_enantiomeric_excess",quantity(0,"%"),evidence,["3ad_probe"]),field("ee_measurement_basis","HPLC on Chiralpak AD-H",evidence,["3ad_probe"])],
    notes=["Complete racemization was used by the authors as evidence favoring the Pd(0)-initiated mechanism."],
    unresolved=["Reaction duration, atmosphere, and workup are not restated for this distinct probe batch; product stereostructure remains unverified."]))


# Coverage ledger, exactly pages 1-6 with visual evidence on every page.
ids = [r["record_id"] for r in records]
def rid(suffix): return f"{DOC}:{suffix}"
table1_ids = [rid("table1_entry1_table2_entry1_3aa")] + [rid(f"table1_entry{x}") for x in range(2,12)]
scope_ids = [rid("table1_entry1_table2_entry1_3aa")] + [rid(f"table2_entry{x}_{scope[x-1][3]}") for x in range(2,15)]
coverage = {"document_id":DOC,"semantic_accuracy_verified":False,"pages":[
 {"page":1,"state":"attempted","regions":[
   {"region":"upper title, abstract, introduction, and opening Results and Discussion","finding":"Article-level scope and cited prior literature provide context; the opening 70% NMR result is the same experiment as Table 1 entry 1 and is not duplicated.","evidence_ids":[ev(1,"image"),ev(1)]},
   {"region":"lower-right Table 1 and footnote","finding":"All 11 optimization rows were visually read; entry 1 is reconciled with Table 2 entry 1/section 4.2.1, while entries 2-11 remain independent condition rows. NMR yield and recovery are kept distinct.","evidence_ids":[ev(1,"image"),ev(1)]}],
  "record_ids":table1_ids,"unresolved":["Table 1 entry 11 leaves recovery blank; it is retained as missing, not zero."]},
 {"page":2,"state":"attempted","regions":[
   {"region":"middle-left Table 2 and footnotes","finding":"Fourteen substrate-scope rows were visually read. Table-wide catalyst/reagent/solvent conditions and row-specific time, temperature, NMR yield, and parenthesized isolated yield were linked to the detailed procedures on pages 3-5.","evidence_ids":[ev(2,"image"),ev(2)]},
   {"region":"lower-left Scheme 1","finding":"The secondary propargylic carbonate 2g gives a complicated reaction and simple propargyl carbonate 2h gives no reaction; these are two distinct unsuccessful experiments.","evidence_ids":[ev(2,"image"),ev(2)]},
   {"region":"upper-right Fig. 1 and right-column mechanism discussion","finding":"Fig. 1 is an ORTEP representation of 3cf, not a reaction. The prose introduces two proposed mechanisms and the optically active (+)-2d probe; the mechanism is classified separately from the probe experiment.","evidence_ids":[ev(2,"image"),ev(2)]}],
  "record_ids":scope_ids+[rid("scheme1_2g_complicated"),rid("scheme1_2h_no_reaction"),rid("scheme2_mechanistic_pathways"),rid("scheme3_section4_3_2_chiral_probe")],
  "unresolved":["Scheme 1 omits scale, time, temperature, atmosphere, workup, purification, and product identities."]},
 {"page":3,"state":"attempted","regions":[
   {"region":"upper Scheme 2","finding":"Two proposed Pd(0)- and Pd(II)-initiated pathways are mechanistic hypotheses, not reported batches.","evidence_ids":[ev(3,"image"),ev(3)]},
   {"region":"middle-left Scheme 3","finding":"Optically active (+)-2d (95% ee) gives 3ad in 62% yield and 0% ee at 50 °C; this distinct mechanistic-probe batch is not merged with racemic Table 2 entry 4.","evidence_ids":[ev(3,"image"),ev(3)]},
   {"region":"lower-left section 4.1.1","finding":"Detailed carbonylative synthesis of new allenamide 1c extracted with charges, CO pressure, time, room temperature, workup, purification, mass, and 47% isolated yield.","evidence_ids":[ev(3,"image"),ev(3)]},
   {"region":"lower-right sections 4.2.1-4.2.2","finding":"General 3aa batch and abbreviated 3ab batch enrich the matching Table 2 records; analytical spectra are retained in source evidence but not exhaustively decomposed.","evidence_ids":[ev(3,"image"),ev(3)]}],
  "record_ids":[rid("scheme2_mechanistic_pathways"),rid("scheme3_section4_3_2_chiral_probe"),rid("section4_1_1_synthesis_1c"),rid("table1_entry1_table2_entry1_3aa"),rid("table2_entry2_3ab")],
  "unresolved":["Scheme 3/detailed section 4.3.2 does not state reaction duration; complex structures remain machine-unverified."]},
 {"page":4,"state":"attempted","regions":[
   {"region":"left-column continuation of 4.2.2 and sections 4.2.3-4.2.6","finding":"Detailed quantities and isolated outcomes for 3ab-3af were reconciled with Table 2 rows rather than duplicated.","evidence_ids":[ev(4,"image"),ev(4)]},
   {"region":"right-column sections 4.2.7-4.2.11","finding":"Detailed quantities and isolated outcomes for 3be, 3ce, 3cf, 3de, and the beginning of 3ea were reconciled with Table 2 rows.","evidence_ids":[ev(4,"image"),ev(4)]}],
  "record_ids":[rid(f"table2_entry{x}_{scope[x-1][3]}") for x in range(2,12)],
  "unresolved":["Printed label inconsistencies in sections 4.2.6 (3ae/3af) and 4.2.7 (1a/1b) are preserved for review; abbreviated procedures omit atmosphere/workup."]},
 {"page":5,"state":"attempted","regions":[
   {"region":"left column continuation of 4.2.11 and sections 4.2.12-4.2.14","finding":"Detailed quantities and isolated outcomes for 3ea, 3ec, 3ed, and 3ef were reconciled with Table 2 rows.","evidence_ids":[ev(5,"image"),ev(5)]},
   {"region":"lower-left/right section 4.3.1","finding":"Two-stage preparation of optically active (+)-2d extracted with separate THF portions, 1 h and 16 h stages, ice-bath addition, workup, chromatography, 81% isolated yield, and 95% ee.","evidence_ids":[ev(5,"image"),ev(5)]},
   {"region":"right-column section 4.3.2","finding":"Detailed half-scale (+)-2d mechanistic-probe batch gives 3ad in 62% isolated yield and 0% ee; it is linked to Scheme 3 and kept distinct from Table 2 entry 4.","evidence_ids":[ev(5,"image"),ev(5)]}],
  "record_ids":[rid(f"table2_entry{x}_{scope[x-1][3]}") for x in range(11,15)]+[rid("section4_3_1_synthesis_plus_2d"),rid("scheme3_section4_3_2_chiral_probe")],
  "unresolved":["Section 4.2.14 has a printed 3ed/3ef label inconsistency; absolute configuration of (+)-2d is not established; probe reaction duration/workup are missing."]},
 {"page":6,"state":"attempted","regions":[
   {"region":"full page references 4-8 and crystal-data continuation","finding":"No new independent experiment is reported. The page contains cited literature and crystallographic data for 3cf; cited works are not recast as experiments of this paper.","evidence_ids":[ev(6,"image"),ev(6)]}],
  "record_ids":[rid("table2_entry9_3cf")],
  "unresolved":["CCDC 800853 and cited-paper procedures were not supplied as explicit associated source data; no SI association is inferred."]}
]}

OUT.mkdir(parents=True, exist_ok=True)
(OUT / "records_pages_0001_0006.json").write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
coverage_path = ROOT / "runs/current/coverage/pages_0001_0006.json"
coverage_path.parent.mkdir(parents=True, exist_ok=True)
coverage_path.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

# Mark the six mechanically prepared page tasks as attempted.
tasks_path = ROOT / "runs/current/tasks.json"
tasks = json.loads(tasks_path.read_text())
for task in tasks:
    if task.get("document_id") == DOC and task.get("evidence_id") in {ev(p) for p in range(1,7)}:
        task["state"] = "attempted"
        task["reason"] = "Original page image inspected; experiments reconciled into evidence-linked records and coverage ledger."
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

assert len(records) == 30
assert len({r["record_id"] for r in records}) == 30
assert [p["page"] for p in coverage["pages"]] == [1,2,3,4,5,6]
assert all(p["regions"] for p in coverage["pages"])
assert all(ev(p["page"], "image") in {e for region in p["regions"] for e in region["evidence_ids"]}
           for p in coverage["pages"])
assert set(x for p in coverage["pages"] for x in p["record_ids"]) <= set(ids)
print(json.dumps({"records":len(records),"coverage_pages":[1,2,3,4,5,6]}, ensure_ascii=False))
