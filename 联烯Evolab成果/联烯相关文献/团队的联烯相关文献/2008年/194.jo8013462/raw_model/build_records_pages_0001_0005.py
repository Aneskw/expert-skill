#!/usr/bin/env python3
"""Build evidence-linked machine records for jo8013462, PDF pages 1-5."""
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
DATASET = ROOT / "runs/current/dataset.json"
OUT = ROOT / "runs/current/raw_model/records_pages_0001_0005.json"
COVERAGE = ROOT / "runs/current/coverage/pages_0001_0005.json"
TASKS = ROOT / "runs/current/tasks.json"
DOC = "doc_7f9358c5ecf8a49e"


def ev(page: int) -> list[str]:
    return [f"{DOC}:page{page}:text", f"{DOC}:page{page}:image"]


def fact(value, evidence):
    return {
        "value": value,
        "evidence_ids": list(dict.fromkeys(evidence)) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def fld(name, value, evidence, targets=None, category=None):
    item = {"name": name, "fact": fact(value, evidence)}
    if targets:
        item["target_entity_ids"] = targets
    if category:
        item["category"] = category
    return item


def part(entity_id, role, label, evidence, *, name=None, smiles=None, amounts=()):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence) if name else fact(None, []),
        "smiles": fact(smiles, evidence) if smiles else fact(None, []),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": [fld(n, v, evidence, category=c) for n, v, c in amounts],
    }


def step(step_id, participants, conditions):
    return {
        "step_id": step_id,
        "participant_ids": participants,
        "conditions": conditions,
    }


def rec(rid, kind, pages, participants, steps, outcomes, *, notes=(), unresolved=()):
    evidence = []
    for page in pages:
        evidence.extend(ev(page))
    evidence = list(dict.fromkeys(evidence))
    return {
        "record_id": f"{DOC}:{rid}",
        "document_id": DOC,
        "source_reaction_id": rid,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": evidence,
        "participants": participants,
        "steps": steps,
        "outcomes": outcomes,
        "notes": [fact(x, evidence) for x in notes],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": list(unresolved),
        },
    }


SMI = {
    "1a": "C=C=C(CCC)P(=O)(c1ccccc1)c1ccccc1",
    "2a": "OCC(I)=C(CCC)P(=O)(c1ccccc1)c1ccccc1",
    "3a": "ICC(I)=C(CCC)P(=O)(c1ccccc1)c1ccccc1",
    "hexynol": "CCCC#CCO",
    "et3n": "CCN(CC)CC",
    "ph2pcl": "ClP(c1ccccc1)c1ccccc1",
    "thf": "C1CCOC1",
    "i2": "[I][I]",
    "mecn": "CC#N",
    "water": "O",
    "etoac": "CCOC(C)=O",
}


records = []

# Page-1 graphical abstract: generic summary, not a row-level experiment.
e = ev(1)
p = [
    part("ga_allene", "reactant", "generic 1,2-allenylic diphenyl phosphine oxide", e),
    part("ga_i2", "reagent", "I2", e, smiles=SMI["i2"], amounts=(("equivalents", {"number": 4, "unit": "equiv"}, None),)),
    part("ga_mecn", "solvent", "MeCN", e, smiles=SMI["mecn"]),
    part("ga_water", "solvent", "H2O", e, smiles=SMI["water"]),
    part("ga_agno3", "reagent", "AgNO3", e, amounts=(("conditional_equivalents", {"number": 6, "unit": "equiv"}, None),)),
    part("ga_product", "product", "generic (E)-2-iodo-3-hydroxy-1-alkenyl diphenyl phosphine oxide", e),
]
records.append(rec(
    "graphical_abstract_iodohydroxylation", "general_scheme", [1], p,
    [step("summary_arrow", [x["entity_id"] for x in p], [
        fld("temperature", "r.t.", e), fld("solvent", "MeCN/H2O", e),
    ])], [],
    notes=("AgNO3 is conditionally required only when R1 is aryl and R2 = R3 = H.",),
    unresolved=("Generic R groups do not support compound-specific structures or a row-level yield.",),
))

# Scheme 1: generic preparation of 1a-r by a cited method.
e = ev(2)
p = [
    part("s1_propargylic_alcohol", "reactant", "generic propargylic alcohol", e),
    part("s1_ph2pcl", "reagent", "Ph2PCl", e, smiles=SMI["ph2pcl"]),
    part("s1_et3n", "reagent", "Et3N", e, smiles=SMI["et3n"]),
    part("s1_thf", "solvent", "THF", e, smiles=SMI["thf"]),
    part("s1_products", "product", "1,2-allenylic diphenyl phosphine oxides 1a-r", e),
]
records.append(rec(
    "scheme1_preparation_1a_to_1r", "general_scheme", [2], p,
    [step("preparation", [x["entity_id"] for x in p], [
        fld("initial_temperature", {"number": -78, "unit": "°C"}, e),
        fld("warming_operation", "warm to room temperature", e),
        fld("time", None, []), fld("atmosphere", None, []),
        fld("workup", None, []), fld("purification", None, []),
    ])],
    [fld("reported_yield_range", {"minimum": 47, "maximum": 80, "unit": "%", "raw_text": "47-80%"}, e, ["s1_products"])],
    notes=("The paper states that eighteen compounds 1a-r were synthesized by the cited procedure.",),
    unresolved=("Scheme 1 gives a collective yield range rather than compound-specific yields.", "Generic substituent structures remain unverified."),
))


def table1_row(entry, ratio, y2, y3, selectivity, *, temp="r.t.", time=24, iodine_eq=4, isolated=None):
    e = ev(2)
    prefix = f"t1e{entry}"
    parts = [
        part(f"{prefix}_1a", "reactant", "1a", e, name="hexa-1,2-dien-3-yl diphenyl phosphine oxide", smiles=SMI["1a"], amounts=(("reaction_scale", {"number": 0.1, "unit": "mmol"}, None),)),
        part(f"{prefix}_i2", "reagent", "I2", e, smiles=SMI["i2"], amounts=(("equivalents", {"number": iodine_eq, "unit": "equiv"}, None),)),
        part(f"{prefix}_mecn", "solvent", "CH3CN", e, smiles=SMI["mecn"]),
        part(f"{prefix}_water", "solvent", "H2O", e, smiles=SMI["water"]),
        part(f"{prefix}_2a", "product", "(E)-2a", e, smiles=SMI["2a"]),
        part(f"{prefix}_3a", "product", "(E)-3a", e, smiles=SMI["3a"]),
    ]
    outcomes = [
        fld("nmr_yield_E_2a", {"number": y2, "unit": "%"}, e, [f"{prefix}_2a"]),
        fld("nmr_yield_E_3a", {"number": y3, "unit": "%"}, e, [f"{prefix}_3a"]),
        fld("E_2a_to_E_3a_ratio", selectivity, e, [f"{prefix}_2a", f"{prefix}_3a"]),
        fld("yield_measurement_basis", "300 MHz 1H NMR of crude mixture using CH2Br2 as internal standard", e),
    ]
    if isolated is not None:
        outcomes.append(fld("isolated_yield_E_2a", {"number": isolated, "unit": "%"}, e, [f"{prefix}_2a"]))
    return rec(
        f"table1_entry{entry}", "optimization_entry", [2], parts,
        [step("iodohydroxylation", [x["entity_id"] for x in parts], [
            fld("solvent_ratio_CH3CN_to_H2O", ratio, e),
            fld("temperature", temp, e),
            fld("time", {"number": time, "unit": "h"}, e),
            fld("atmosphere", None, []), fld("workup", None, []), fld("purification", None, []),
        ])], outcomes,
        unresolved=("Table 1 does not report atmosphere, workup, or purification.", "All candidate structures and alkene geometry remain unverified."),
    )


records += [
    table1_row(1, "5:1", 18, 56, "24:76"),
    table1_row(2, "3:1", 23, 55, "29:71"),
    table1_row(3, "1:1", 47, 33, "59:41"),
    table1_row(4, "1:3", 87, 4, "96:4"),
    table1_row(5, "1:5", 90, 0, ">99:1", isolated=78),
    table1_row(6, "0:100", 86, 7, "92:8"),
    table1_row(7, "1:5", 60, 0, ">99:1", temp={"number": 60, "unit": "°C"}, time=20),
    table1_row(8, "1:5", 95, 5, "95:5", time=37, iodine_eq=3),
]


def condition_a_failure(label, finding, recovery=None):
    e = ev(2)
    rid = f"conditions_a_{label}_failure"
    p = [
        part(f"{rid}_substrate", "reactant", label, e),
        part(f"{rid}_i2", "reagent", "I2", e, smiles=SMI["i2"], amounts=(("equivalents", {"number": 4, "unit": "equiv"}, None),)),
        part(f"{rid}_mecn", "solvent", "CH3CN", e, smiles=SMI["mecn"]),
        part(f"{rid}_water", "solvent", "H2O", e, smiles=SMI["water"]),
        part(f"{rid}_expected", "product", f"expected iodohydroxylation product from {label}", e),
    ]
    out = [fld("reaction_result", finding, e, [f"{rid}_expected"])]
    if recovery is not None:
        out.append(fld("recovered_starting_material_yield", {"number": recovery, "unit": "%"}, e, [f"{rid}_substrate"]))
    return rec(
        rid, "reported_experiment", [2], p,
        [step("conditions_A", [x["entity_id"] for x in p], [
            fld("solvent_ratio_CH3CN_to_H2O", "1:5", e), fld("temperature", "r.t.", e),
            fld("time", None, []), fld("atmosphere", None, []), fld("workup", None, []), fld("purification", None, []),
        ])], out,
        unresolved=("The prose does not report scale, duration, atmosphere, workup, purification, or yield basis.", "Expected-product connectivity remains unverified."),
    )


records += [
    condition_a_failure("1m", "complicated reaction mixture"),
    condition_a_failure("1n", "no expected product formed", 66),
    condition_a_failure("1o", "no expected product formed", 76),
]


table2 = [
    (1, "1a (R1=n-Pr, R2=H, R3=H)", "(E)-2a", 24, 76),
    (2, "1b (R1=Me, R2=H, R3=H)", "(E)-2b", 21, 70),
    (3, "1c (R1=H, R2=Me, R3=H)", "(E)-2c", 8, 67),
    (4, "1d (R1=H, R2=n-Pr, R3=H)", "(E)-2d", 9, 82),
    (5, "1e (R1=H, R2=n-C5H11, R3=H)", "(E)-2e", 9, 80),
    (6, "1f (R1=H, R2=Me, R3=Me)", "(E)-2f", 5, 93),
    (7, "1g (R1=H, R2=Et, R3=Et)", "(E)-2g", 8, 84),
    (8, "1h (R1=H, R2/R3=-(CH2)4-)", "(E)-2h", 9, 56),
    (9, "1i (R1=Et, R2=Me, R3=H)", "(E)-2i", 21, 80),
    (10, "1j (R1=n-Bu, R2=n-Pr, R3=H)", "(E)-2j", 8, 77),
    (11, "1k (R1=Ph, R2=Me, R3=H)", "(E)-2k", 24, 79),
    (12, "1l (R1=Ph, R2=n-Pr, R3=H)", "(E)-2l", 23, 85),
]


for entry, substrate, product, hours, yld in table2:
    pages = [3, 4] if entry == 1 else [3]
    e = []
    for pg in pages:
        e += ev(pg)
    prefix = f"t2e{entry}"
    substrate_smiles = SMI["1a"] if entry == 1 else None
    product_smiles = SMI["2a"] if entry == 1 else None
    substrate_amounts = []
    iodine_amounts = [("equivalents", {"number": 4, "unit": "equiv"}, None)]
    mecn_amounts = []
    water_amounts = []
    product_amounts = []
    if entry == 1:
        substrate_amounts = [("mass", {"number": 56, "unit": "mg"}, None), ("amount", {"number": 0.20, "unit": "mmol"}, None)]
        iodine_amounts += [("mass", {"number": 203, "unit": "mg"}, None), ("amount", {"number": 0.80, "unit": "mmol"}, None)]
        mecn_amounts = [("volume", {"number": 1, "unit": "mL"}, None)]
        water_amounts = [("volume", {"number": 5, "unit": "mL"}, None)]
        product_amounts = [("isolated_mass", {"number": 65, "unit": "mg"}, "mass")]
    else:
        substrate_amounts = [("reaction_scale", {"number": 0.2, "unit": "mmol"}, None)]
    parts = [
        part(f"{prefix}_substrate", "reactant", substrate, e, smiles=substrate_smiles, amounts=substrate_amounts),
        part(f"{prefix}_i2", "reagent", "I2", e, smiles=SMI["i2"], amounts=iodine_amounts),
        part(f"{prefix}_mecn", "solvent", "CH3CN", e, smiles=SMI["mecn"], amounts=mecn_amounts),
        part(f"{prefix}_water", "solvent", "H2O", e, smiles=SMI["water"], amounts=water_amounts),
        part(f"{prefix}_product", "product", product, e, smiles=product_smiles, amounts=product_amounts),
    ]
    conditions = [
        fld("total_solvent_volume", {"number": 6, "unit": "mL"}, ev(3)),
        fld("solvent_ratio_CH3CN_to_H2O", "1:5", ev(3)),
        fld("temperature", "r.t.", ev(3)),
        fld("time", {"number": hours, "unit": "h"}, ev(3)),
        fld("atmosphere", None, []),
    ]
    unresolved = ["Alkene stereochemistry and candidate molecular connectivity remain unverified."]
    if entry == 1:
        conditions += [
            fld("reaction_monitoring", "TLC (ether)", ev(4)),
            fld("workup", "saturated sodium thiosulfate; EtOAc extraction (10 mL x 3); MgSO4 drying; filtration and evaporation", ev(4)),
            fld("purification", "silica-gel flash chromatography (ether)", ev(4)),
        ]
    else:
        conditions += [fld("workup", None, []), fld("purification", None, [])]
        unresolved.append("The scope row does not report atmosphere, workup, purification, or compound-specific mass data.")
    records.append(rec(
        f"table2_entry{entry}", "substrate_scope_entry", pages, parts,
        [step("conditions_A", [x["entity_id"] for x in parts], conditions)],
        [fld("isolated_yield", {"number": yld, "unit": "%"}, ev(3), [f"{prefix}_product"]),
         fld("yield_measurement_basis", "isolated", ev(3)),
         fld("regio_and_stereoselectivity_assessment", "determined by 300 MHz 1H NMR of the crude reaction mixture", ev(3))],
        notes=(("Entry 1 incorporates the exact Typical Procedure II quantities and operations from page 4." if entry == 1 else "Conditions A scope row."),),
        unresolved=unresolved,
    ))


# Scheme 2: one generic literature-based arrow with four explicitly labeled chiral products.
e = ev(3)
p = [
    part("s2_ph2pcl", "reagent", "Ph2PCl", e, smiles=SMI["ph2pcl"]),
    part("s2_propargylic", "reactant", "optically active propargylic alcohols", e),
    part("s2_et3n", "reagent", "Et3N", e, smiles=SMI["et3n"]),
    part("s2_thf", "solvent", "THF", e, smiles=SMI["thf"]),
]
for lab in ["(R)-1c", "(S)-1c", "(R)-1e", "(S)-1e"]:
    p.append(part("s2_" + lab.replace("(", "").replace(")", "").replace("-", "_"), "product", lab, e))
s2ids = {x["label"]["value"]: x["entity_id"] for x in p}
records.append(rec(
    "scheme2_optically_active_starting_materials", "general_scheme", [3], p,
    [step("literature_preparation", [x["entity_id"] for x in p], [
        fld("initial_temperature", {"number": -78, "unit": "°C"}, e),
        fld("warming_operation", "warm to room temperature", e), fld("time", None, []),
        fld("atmosphere", None, []), fld("workup", None, []), fld("purification", None, []),
    ])],
    [fld("starting_material_ee", {"number": val, "unit": "%"}, e, [s2ids[lab]]) for lab, val in
     [("(R)-1c", 94), ("(S)-1c", 95), ("(R)-1e", 98), ("(S)-1e", 97)]],
    notes=("The scheme says the compounds were prepared from optically active propargylic alcohols according to the cited literature procedure.",),
    unresolved=("Compound-specific quantities, yields, duration, atmosphere, workup, and purification are not reported.", "Axial stereochemistry remains unverified."),
))


scheme3 = [
    ("R_1c", "(R)-1c", 94, "(R)-(E)-2c", 75, 94),
    ("R_1e", "(R)-1e", 98, "(R)-(E)-2e", 84, 97),
    ("S_1c", "(S)-1c", 95, "(S)-(E)-2c", 72, 94),
    ("S_1e", "(S)-1e", 97, "(S)-(E)-2e", 84, 97),
]
for suffix, sub, subee, prod, yld, prodee in scheme3:
    e = ev(3)
    prefix = f"s3_{suffix}"
    parts = [
        part(f"{prefix}_sub", "reactant", sub, e),
        part(f"{prefix}_i2", "reagent", "I2", e, smiles=SMI["i2"], amounts=(("equivalents", {"number": 4, "unit": "equiv"}, None),)),
        part(f"{prefix}_mecn", "solvent", "CH3CN", e, smiles=SMI["mecn"]),
        part(f"{prefix}_water", "solvent", "H2O", e, smiles=SMI["water"]),
        part(f"{prefix}_prod", "product", prod, e),
    ]
    records.append(rec(
        f"scheme3_{suffix}_chirality_transfer", "reported_experiment", [3], parts,
        [step("conditions_A", [x["entity_id"] for x in parts], [
            fld("solvent_ratio_CH3CN_to_H2O", "1:5", e), fld("temperature", "r.t.", e),
            fld("time", None, []), fld("atmosphere", None, []), fld("workup", None, []), fld("purification", None, []),
        ])],
        [fld("starting_material_ee", {"number": subee, "unit": "%"}, e, [f"{prefix}_sub"]),
         fld("reported_yield", {"number": yld, "unit": "%"}, e, [f"{prefix}_prod"]),
         fld("product_ee", {"number": prodee, "unit": "%"}, e, [f"{prefix}_prod"])],
        notes=("The paper states efficient transfer of allene axial chirality to the product alcohol stereocenter.",),
        unresolved=("Scale, duration, atmosphere, workup, purification, and yield basis are not reported in Scheme 3.", "Absolute stereochemistry is source-assigned but remains machine-unverified."),
    ))


def table3_row(entry, ag_eq, y2, y3, ratio, *, iodine_eq=4, isolated2=None, isolated3=None, complicated=False, yields_are_isolated_only=False):
    e = ev(3)
    prefix = f"t3e{entry}"
    parts = [
        part(f"{prefix}_1p", "reactant", "1p", e, name="1-phenyl(propa-1,2-dienyl) diphenyl phosphine oxide", amounts=(("reaction_scale", {"number": 0.1, "unit": "mmol"}, None),)),
        part(f"{prefix}_i2", "reagent", "I2", e, smiles=SMI["i2"], amounts=(("equivalents", {"number": iodine_eq, "unit": "equiv"}, None),)),
        part(f"{prefix}_mecn", "solvent", "CH3CN", e, smiles=SMI["mecn"]),
        part(f"{prefix}_water", "solvent", "H2O", e, smiles=SMI["water"]),
        part(f"{prefix}_2p", "product", "(E)-2p", e),
        part(f"{prefix}_3p", "product", "(E)-3p", e),
    ]
    if ag_eq is not None:
        parts.insert(2, part(f"{prefix}_agno3", "reagent", "AgNO3", e, amounts=(("equivalents", {"number": ag_eq, "unit": "equiv"}, None),)))
    if complicated:
        outcomes = [fld("reaction_result", "complicated", e)]
    elif yields_are_isolated_only:
        outcomes = [fld("E_2p_to_E_3p_ratio", ratio, e, [f"{prefix}_2p", f"{prefix}_3p"])]
    else:
        outcomes = [
            fld("nmr_yield_E_2p", {"number": 99 if y2 == 99.01 else y2, "unit": "%", **({"qualifier": "gt", "raw_text": ">99%"} if y2 == 99.01 else {})}, e, [f"{prefix}_2p"]),
            fld("nmr_yield_E_3p", {"number": y3, "unit": "%"}, e, [f"{prefix}_3p"]),
            fld("E_2p_to_E_3p_ratio", ratio, e, [f"{prefix}_2p", f"{prefix}_3p"]),
            fld("yield_measurement_basis", "300 MHz 1H NMR of crude mixture using CH2Br2 as internal standard", e),
        ]
    if not complicated and isolated2 is not None:
        outcomes.append(fld("isolated_yield_E_2p", {"number": isolated2, "unit": "%"}, e, [f"{prefix}_2p"]))
    if not complicated and isolated3 is not None:
        outcomes.append(fld("isolated_yield_E_3p", {"number": isolated3, "unit": "%"}, e, [f"{prefix}_3p"]))
    if yields_are_isolated_only:
        outcomes.append(fld("yield_measurement_basis", "isolated", e))
    return rec(
        f"table3_entry{entry}", "optimization_entry", [3], parts,
        [step("iodohydroxylation", [x["entity_id"] for x in parts], [
            fld("total_solvent_volume", {"number": 6, "unit": "mL"}, e),
            fld("solvent_ratio_CH3CN_to_H2O", "1:5", e), fld("temperature", "r.t.", e),
            fld("time", {"number": 24, "unit": "h"}, e), fld("atmosphere", None, []),
            fld("workup", None, []), fld("purification", None, []),
        ])], outcomes,
        unresolved=("Table 3 does not report atmosphere, workup, or purification.", "Product structures and E geometry remain unverified."),
    )


records += [
    table3_row(1, None, None, None, "72:28", isolated2=64, isolated3=16, yields_are_isolated_only=True),
    table3_row(2, 3, 71, 11, "87:13"),
    table3_row(3, 4, 82, 3, "96:4"),
    table3_row(4, 5, 97, 2, "98:2"),
    table3_row(5, 6, 99.01, 0, ">99:1", isolated2=87),
    table3_row(6, 3, None, None, None, iodine_eq=2, complicated=True),
]


table4 = [
    (1, "1p (Ar=Ph, R=H)", "(E)-2p", 24, 84),
    (2, "1q (Ar=p-CHOC6H4, R=H)", "(E)-2q", 48, 57),
    (3, "1r (Ar=p-MeC6H4, R=H)", "(E)-2r", 61, 77),
    (4, "1k (Ar=Ph, R=Me)", "expected (E)-2k", 24, None),
    (5, "1l (Ar=Ph, R=n-Pr)", "expected (E)-2l", 22, None),
]
for entry, substrate, product, hours, yld in table4:
    pages = [3, 4, 5] if entry == 1 else [3]
    e = []
    for pg in pages:
        e += ev(pg)
    prefix = f"t4e{entry}"
    sub_amounts = [("reaction_scale", {"number": 0.2, "unit": "mmol"}, None)]
    i2_amounts = [("equivalents", {"number": 4, "unit": "equiv"}, None)]
    ag_amounts = [("equivalents", {"number": 6, "unit": "equiv"}, None)]
    mecn_amounts = []
    water_amounts = []
    prod_amounts = []
    if entry == 1:
        sub_amounts += [("mass", {"number": 64, "unit": "mg"}, None)]
        i2_amounts += [("mass", {"number": 204, "unit": "mg"}, None), ("amount", {"number": 0.80, "unit": "mmol"}, None)]
        ag_amounts += [("mass", {"number": 206, "unit": "mg"}, None), ("amount", {"number": 1.22, "unit": "mmol"}, None)]
        mecn_amounts = [("volume", {"number": 1, "unit": "mL"}, None)]
        water_amounts = [("volume", {"number": 5, "unit": "mL"}, None)]
        prod_amounts = [("isolated_mass", {"number": 77, "unit": "mg"}, "mass")]
    parts = [
        part(f"{prefix}_substrate", "reactant", substrate, e, amounts=sub_amounts),
        part(f"{prefix}_i2", "reagent", "I2", e, smiles=SMI["i2"], amounts=i2_amounts),
        part(f"{prefix}_agno3", "reagent", "AgNO3", e, amounts=ag_amounts),
        part(f"{prefix}_mecn", "solvent", "CH3CN", e, smiles=SMI["mecn"], amounts=mecn_amounts),
        part(f"{prefix}_water", "solvent", "H2O", e, smiles=SMI["water"], amounts=water_amounts),
        part(f"{prefix}_product", "product", product, e, amounts=prod_amounts),
    ]
    conds = [
        fld("total_solvent_volume", {"number": 6, "unit": "mL"}, ev(3)),
        fld("solvent_ratio_CH3CN_to_H2O", "1:5", ev(3)), fld("temperature", "r.t.", ev(3)),
        fld("time", {"number": hours, "unit": "h"}, ev(3)), fld("atmosphere", None, []),
    ]
    unresolved = ["Substrate/product connectivity and alkene geometry remain unverified."]
    if entry == 1:
        conds += [
            fld("reaction_monitoring", "TLC (ether)", ev(4)),
            fld("workup", "saturated sodium thiosulfate; EtOAc extraction (10 mL x 3); MgSO4 drying; filtration and evaporation", ev(4)),
            fld("purification", "silica-gel flash chromatography (petroleum ether/ethyl acetate 1:1)", ev(4)),
        ]
    else:
        conds += [fld("workup", None, []), fld("purification", None, [])]
        unresolved.append("The row does not report atmosphere, workup, or purification.")
    outcomes = ([fld("isolated_yield", {"number": yld, "unit": "%"}, ev(3), [f"{prefix}_product"]),
                 fld("yield_measurement_basis", "isolated", ev(3)),
                 fld("stereochemical_result", "only the E product", ev(3), [f"{prefix}_product"])]
                if yld is not None else [fld("reaction_result", "complicated", ev(3), [f"{prefix}_product"])])
    records.append(rec(
        f"table4_entry{entry}", "substrate_scope_entry", pages, parts,
        [step("conditions_B", [x["entity_id"] for x in parts], conds)], outcomes,
        notes=(("Entry 1 incorporates Typical Procedure III; characterization continues onto page 5." if entry == 1 else "Conditions B scope row."),),
        unresolved=unresolved,
    ))


def condition_b_failure(label):
    e = ev(3)
    rid = f"conditions_b_{label}_failure"
    p = [
        part(f"{rid}_sub", "reactant", label, e),
        part(f"{rid}_i2", "reagent", "I2", e, smiles=SMI["i2"], amounts=(("equivalents", {"number": 4, "unit": "equiv"}, None),)),
        part(f"{rid}_agno3", "reagent", "AgNO3", e, amounts=(("equivalents", {"number": 6, "unit": "equiv"}, None),)),
        part(f"{rid}_mecn", "solvent", "CH3CN", e, smiles=SMI["mecn"]),
        part(f"{rid}_water", "solvent", "H2O", e, smiles=SMI["water"]),
        part(f"{rid}_expected", "product", f"expected iodohydroxylation product from {label}", e),
    ]
    return rec(
        rid, "reported_experiment", [3], p,
        [step("conditions_B", [x["entity_id"] for x in p], [
            fld("solvent_ratio_CH3CN_to_H2O", "1:5", e), fld("temperature", "r.t.", e),
            fld("time", None, []), fld("atmosphere", None, []), fld("workup", None, []), fld("purification", None, []),
        ])], [fld("reaction_result", "complicated", e, [f"{rid}_expected"])],
        unresolved=("Scale, duration, atmosphere, workup, purification, and product identity are not reported.",),
    )


records += [condition_b_failure("1n"), condition_b_failure("1o")]

# Equation 1: 1r under Conditions A.
e = ev(4)
p = [
    part("eq1_1r", "reactant", "1r", e),
    part("eq1_i2", "reagent", "I2", e, smiles=SMI["i2"], amounts=(("equivalents", {"number": 4, "unit": "equiv"}, None),)),
    part("eq1_mecn", "solvent", "CH3CN", e, smiles=SMI["mecn"]),
    part("eq1_water", "solvent", "H2O", e, smiles=SMI["water"]),
    part("eq1_2r", "product", "(E)-2r", e),
    part("eq1_3r", "product", "(E)-3r", e),
    part("eq1_unknown", "product", "unidentified byproduct", e),
]
records.append(rec(
    "equation1_1r_conditions_a", "reported_experiment", [4], p,
    [step("conditions_A", [x["entity_id"] for x in p], [
        fld("solvent_ratio_CH3CN_to_H2O", "1:5", e), fld("temperature", "r.t.", e),
        fld("time", None, []), fld("atmosphere", None, []), fld("workup", None, []), fld("purification", None, []),
    ])],
    [fld("reported_yield_E_2r", {"number": 49, "unit": "%"}, e, ["eq1_2r"]),
     fld("reported_yield_E_3r", {"number": 21, "unit": "%"}, e, ["eq1_3r"]),
     fld("E_2r_to_E_3r_ratio", "66:34", e, ["eq1_2r", "eq1_3r"]),
     fld("additional_product", "unidentified byproduct", e, ["eq1_unknown"])],
    notes=("The experiment shows that AgNO3 is still required for electron-rich aryl substrate 1r.",),
    unresolved=("Scale, duration, atmosphere, workup, purification, yield basis, and unidentified-product structure are missing.",),
))

# Scheme 4: two actual ESI-MS/MS fragmentation experiments, not preparative reactions.
for suffix, precursor, daughter, isotope in [("normal", 427, 409, "16O"), ("labeled", 429, 411, "18O")]:
    e = ev(4)
    p = [
        part(f"ms_{suffix}_precursor", "reactant", f"protonated ({isotope})-(E)-2a precursor ion, m/z {precursor}", e),
        part(f"ms_{suffix}_daughter", "product", f"daughter ion, m/z {daughter}", e),
        part(f"ms_{suffix}_water", "product", "neutral H2O loss", e, smiles=SMI["water"]),
    ]
    records.append(rec(
        f"scheme4_esi_msms_{suffix}", "reported_experiment", [4], p,
        [step("esi_msms_fragmentation", [x["entity_id"] for x in p], [
            fld("operation", "ESI-MS/MS fragmentation", e), fld("temperature", None, []), fld("time", None, []),
        ])],
        [fld("precursor_m_over_z", precursor, e, [f"ms_{suffix}_precursor"]),
         fld("daughter_m_over_z", daughter, e, [f"ms_{suffix}_daughter"]),
         fld("observed_neutral_loss", "H2O", e, [f"ms_{suffix}_water"])],
        notes=("Analytical gas-phase fragmentation was used as mechanistic evidence and is not a preparative synthetic reaction.",),
        unresolved=("Ion structures shown in Scheme 4 remain unverified and no collision-energy details are reported.",),
    ))

# Scheme 5 proposed mechanism.
e = ev(4)
p = [
    part("mech_1a", "reactant", "1a", e, smiles=SMI["1a"]),
    part("mech_i2", "reagent", "I2", e, smiles=SMI["i2"]),
    part("mech_iodonium", "product", "proposed iodonium intermediate 4a", e),
    part("mech_cyclic", "product", "proposed five-membered intermediate 5a", e),
    part("mech_h218o", "reagent", "H2-18O", e),
    part("mech_2astar", "product", "(E)-2a*", e),
]
records.append(rec(
    "scheme5_proposed_mechanism", "mechanism", [4], p,
    [step("proposed_pathway", [x["entity_id"] for x in p], [])], [],
    notes=("Proposed sequence: iodonium formation, neighboring-group cyclization, then water attack at phosphorus with P-O cleavage.",),
    unresolved=("The intermediates are proposed rather than isolated, and their structures/charges remain unverified.",),
))

# Exact preparation of starting material 1a.
e = ev(4)
p = [
    part("prep1a_hexynol", "reactant", "hex-2-yn-1-ol", e, smiles=SMI["hexynol"], amounts=(("mass", {"number": 979, "unit": "mg"}, None), ("amount", {"number": 10.0, "unit": "mmol"}, None))),
    part("prep1a_et3n", "reagent", "Et3N", e, smiles=SMI["et3n"], amounts=(("volume", {"number": 2.1, "unit": "mL"}, None), ("mass", {"number": 1.5, "unit": "g"}, None), ("amount", {"number": 15.1, "unit": "mmol"}, None))),
    part("prep1a_ph2pcl", "reagent", "Ph2PCl", e, smiles=SMI["ph2pcl"], amounts=(("volume", {"number": 2.7, "unit": "mL"}, None), ("mass", {"number": 3.3, "unit": "g"}, None), ("amount", {"number": 15.0, "unit": "mmol"}, None))),
    part("prep1a_thf", "solvent", "THF", e, smiles=SMI["thf"], amounts=(("volume", {"number": 30, "unit": "mL"}, None),)),
    part("prep1a_product", "product", "1a", e, name="hexa-1,2-dien-3-yl diphenyl phosphine oxide", smiles=SMI["1a"], amounts=(("isolated_mass", {"number": 1.826, "unit": "g"}, "mass"),)),
]
records.append(rec(
    "typical_procedure1_starting_material_1a", "reported_experiment", [4], p,
    [step("addition_and_reaction", [x["entity_id"] for x in p], [
        fld("initial_temperature", {"number": -78, "unit": "°C"}, e),
        fld("addition_operation", "Ph2PCl added dropwise", e),
        fld("warming_operation", "cooling bath removed; mixture allowed to warm naturally to room temperature", e),
        fld("time", "until complete conversion by TLC", e), fld("atmosphere", None, []),
        fld("workup", "filtration and solvent evaporation", e),
        fld("purification", "silica-gel flash chromatography, petroleum ether/ether 1:1", e),
    ])],
    [fld("isolated_yield_1a", {"number": 65, "unit": "%"}, e, ["prep1a_product"]), fld("yield_measurement_basis", "isolated", e)],
    notes=("Printed reagent densities are 0.726 g/mL for Et3N and 1.229 g/mL for Ph2PCl.",),
    unresolved=("Atmosphere and a numerical duration are not reported; candidate structure remains unverified.",),
))

# Page-5 exact diiodide preparation: separate from Table 1 entry 1 because it is a distinct 0.20 mmol isolation run.
e = ev(5)
p = [
    part("diiod_1a", "reactant", "1a", e, smiles=SMI["1a"], amounts=(("mass", {"number": 55, "unit": "mg"}, None), ("amount", {"number": 0.20, "unit": "mmol"}, None))),
    part("diiod_i2", "reagent", "I2", e, smiles=SMI["i2"], amounts=(("mass", {"number": 205, "unit": "mg"}, None), ("amount", {"number": 0.81, "unit": "mmol"}, None))),
    part("diiod_mecn", "solvent", "CH3CN", e, smiles=SMI["mecn"], amounts=(("volume", {"number": 5, "unit": "mL"}, None),)),
    part("diiod_water", "solvent", "H2O", e, smiles=SMI["water"], amounts=(("volume", {"number": 1, "unit": "mL"}, None),)),
    part("diiod_2a", "product", "(E)-2a", e, smiles=SMI["2a"], amounts=(("isolated_mass", {"number": 36, "unit": "mg"}, "mass"),)),
    part("diiod_3a", "product", "(E)-3a", e, smiles=SMI["3a"], amounts=(("isolated_mass", {"number": 40, "unit": "mg"}, "mass"),)),
]
records.append(rec(
    "diiodide_3a_isolation_run", "reported_experiment", [5], p,
    [step("iodination", [x["entity_id"] for x in p], [
        fld("temperature", "r.t.", e), fld("time", "until complete by TLC", e),
        fld("reaction_monitoring", "TLC (ether)", e), fld("atmosphere", None, []),
        fld("workup", "saturated sodium thiosulfate; EtOAc extraction (10 mL x 3); MgSO4 drying; filtration and evaporation", e),
        fld("purification", "silica-gel flash chromatography, petroleum ether/ether 2:1", e),
    ])],
    [fld("isolated_yield_E_2a", {"number": 42, "unit": "%"}, e, ["diiod_2a"]),
     fld("isolated_yield_E_3a", {"number": 37, "unit": "%"}, e, ["diiod_3a"]),
     fld("yield_measurement_basis", "isolated", e)],
    notes=("This 0.20 mmol isolation run is distinct from the 0.10 mmol Table 1 entry 1 NMR-yield experiment despite matching nominal solvent ratio and iodine loading.",),
    unresolved=("Atmosphere and numerical duration are not reported; structures remain unverified.",),
))

# Exact 18O-labeled synthesis.
e = ev(5)
p = [
    part("iso_1a", "reactant", "1a", e, smiles=SMI["1a"], amounts=(("mass", {"number": 57, "unit": "mg"}, None), ("amount", {"number": 0.20, "unit": "mmol"}, None))),
    part("iso_i2", "reagent", "I2", e, smiles=SMI["i2"], amounts=(("mass", {"number": 207, "unit": "mg"}, None), ("amount", {"number": 0.81, "unit": "mmol"}, None))),
    part("iso_mecn", "solvent", "anhydrous CH3CN", e, smiles=SMI["mecn"], amounts=(("initial_volume", {"number": 0.2, "unit": "mL"}, "volume"), ("wash_volume", {"number": 0.6, "unit": "mL", "raw_text": "0.2 mL x 3"}, "volume"))),
    part("iso_h218o", "solvent", "H2-18O", e, amounts=(("isotopic_purity", {"number": 92, "unit": "%"}, "percentage"), ("iodine_prestir_volume", {"number": 0.4, "unit": "mL"}, "volume"), ("substrate_solution_volume", {"number": 1.0, "unit": "mL"}, "volume"), ("wash_volume", {"number": 2.6, "unit": "mL"}, "volume"))),
    part("iso_product", "product", "(E)-2a*", e, name="18O-labeled 1-hydroxy-2-iodohex-2(E)-en-3-yl diphenyl phosphine oxide", amounts=(("isolated_mass", {"number": 60, "unit": "mg"}, "mass"),)),
]
records.append(rec(
    "oxygen18_labeled_2a_synthesis", "reported_experiment", [5], p,
    [
        step("separate_prestirring", ["iso_i2", "iso_mecn", "iso_h218o", "iso_1a"], [
            fld("temperature", "r.t.", e), fld("time", {"number": 6, "unit": "h"}, e), fld("atmosphere", "nitrogen glovebox", e),
        ]),
        step("combined_reaction", [x["entity_id"] for x in p], [
            fld("temperature", "r.t.", e), fld("time", {"number": 24, "unit": "h"}, e), fld("atmosphere", "nitrogen glovebox", e),
            fld("workup", "none stated before direct chromatography", e),
            fld("purification", "silica-gel flash chromatography, petroleum ether/ethyl acetate 1:1", e),
        ]),
    ],
    [fld("isolated_yield", {"number": 69, "unit": "%"}, e, ["iso_product"]),
     fld("yield_measurement_basis", "isolated", e),
     fld("oxygen18_incorporation", {"number": 86, "unit": "%"}, e, ["iso_product"], category="percentage")],
    notes=("1a was dried over P2O5 for 3 d; MeCN was successively dried with CaH2 and P2O5 under argon before use.",),
    unresolved=("The isotope position and product stereochemical structure remain machine-unverified.",),
))

# Control treatment of unlabeled product in H2-18O.
e = ev(5)
p = [
    part("exchange_2a", "reactant", "(E)-2a", e, smiles=SMI["2a"], amounts=(("mass", {"number": 86, "unit": "mg"}, None), ("amount", {"number": 0.20, "unit": "mmol"}, None))),
    part("exchange_mecn", "solvent", "CH3CN", e, smiles=SMI["mecn"], amounts=(("volume", {"number": 0.2, "unit": "mL"}, None),)),
    part("exchange_h218o", "solvent", "H2-18O", e, amounts=(("volume", {"number": 1.0, "unit": "mL"}, None),)),
    part("exchange_etoac", "solvent", "ethyl acetate", e, smiles=SMI["etoac"], amounts=(("extraction_volume", {"number": 15, "unit": "mL", "raw_text": "5 mL x 3"}, "volume"),)),
]
records.append(rec(
    "oxygen18_exchange_control_2a", "reported_experiment", [5], p,
    [step("exchange_control", [x["entity_id"] for x in p], [
        fld("solvent_ratio_CH3CN_to_H218O", "1:5", e), fld("temperature", "r.t.", e),
        fld("time", {"number": 24, "unit": "h"}, e), fld("atmosphere", "nitrogen glovebox", e),
        fld("workup", "EtOAc extraction (5 mL x 3), MgSO4 drying, filtration and evaporation", e),
        fld("purification", None, []),
    ])],
    [fld("recovered_starting_material_yield", {"number": 93, "unit": "%"}, e, ["exchange_2a"]),
     fld("isolated_mass_after_treatment", {"number": 80, "unit": "mg"}, e, ["exchange_2a"]),
     fld("oxygen18_incorporation", {"number": 1.5, "unit": "%", "qualifier": "le", "raw_text": "<=1.5%"}, e, ["exchange_2a"], category="percentage"),
     fld("isotope_measurement_basis", "ESI-MS", e)],
    unresolved=("No purification is stated; the exact isotopologue distribution beyond the upper bound is not reported.",),
))


# Coverage ledger. Every page cites its original page-image evidence.
rid = lambda suffix: f"{DOC}:{suffix}"
coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1,
            "state": "attempted",
            "regions": [
                {"region": "graphical abstract arrow in upper-middle of original page", "finding": "Generic present-paper iodohydroxylation summary classified as a general scheme; conditional AgNO3 statement retained.", "evidence_ids": ev(1)},
                {"region": "title, abstract, and introduction", "finding": "High-level scope, chirality-transfer, and isotope-mechanism claims; no additional row-level experiment beyond later tables/schemes.", "evidence_ids": ev(1)},
            ],
            "record_ids": [rid("graphical_abstract_iodohydroxylation")],
            "unresolved": ["Abstract-level claims were not duplicated as experiments; generic structures remain unverified."],
        },
        {
            "page": 2,
            "state": "attempted",
            "regions": [
                {"region": "top Scheme 1", "finding": "Generic cited preparation of 1a-r extracted as a general scheme with collective 47-80% range.", "evidence_ids": ev(2)},
                {"region": "upper-left Table 1 and footnotes", "finding": "All eight solvent/temperature/iodine-loading optimization rows extracted independently.", "evidence_ids": ev(2)},
                {"region": "right-column scope discussion", "finding": "Three Conditions-A failures extracted separately: complicated 1m and no expected product with 66%/76% recovered 1n/1o.", "evidence_ids": ev(2)},
            ],
            "record_ids": [rid("scheme1_preparation_1a_to_1r")] + [rid(f"table1_entry{i}") for i in range(1, 9)] + [rid("conditions_a_1m_failure"), rid("conditions_a_1n_failure"), rid("conditions_a_1o_failure")],
            "unresolved": ["Scheme 1 reports only a collective yield range.", "Most Table 1 rows omit atmosphere, workup, and purification."],
        },
        {
            "page": 3,
            "state": "attempted",
            "regions": [
                {"region": "upper-left Table 2", "finding": "All twelve Conditions-A scope rows extracted independently; entry 1 is merged with its page-4 typical procedure.", "evidence_ids": ev(3)},
                {"region": "left-middle Schemes 2 and 3", "finding": "One generic literature-based chiral-starting-material preparation and four independent chirality-transfer reactions extracted.", "evidence_ids": ev(3)},
                {"region": "upper-right Tables 3 and 4", "finding": "All six AgNO3 optimization rows and all five Conditions-B scope rows extracted; complicated rows retained qualitatively.", "evidence_ids": ev(3)},
                {"region": "lower-right prose", "finding": "Separate Conditions-B failures for 1n and 1o extracted from prose.", "evidence_ids": ev(3)},
            ],
            "record_ids": [rid(f"table2_entry{i}") for i in range(1, 13)] + [rid("scheme2_optically_active_starting_materials")] + [rid(f"scheme3_{x}_chirality_transfer") for x in ["R_1c", "R_1e", "S_1c", "S_1e"]] + [rid(f"table3_entry{i}") for i in range(1, 7)] + [rid(f"table4_entry{i}") for i in range(1, 6)] + [rid("conditions_b_1n_failure"), rid("conditions_b_1o_failure")],
            "unresolved": ["Scheme 2 lacks compound-specific yields and operations.", "Scheme 3 omits scale, duration, workup, purification, and yield basis.", "Complex structures and stereochemistry remain unverified."],
        },
        {
            "page": 4,
            "state": "attempted",
            "regions": [
                {"region": "upper-left equation 1", "finding": "Conditions-A 1r experiment extracted with 49%/21% products, 66:34 ratio, and unidentified byproduct.", "evidence_ids": ev(4)},
                {"region": "upper-left Schemes 4 and 5", "finding": "Two ESI-MS/MS fragmentation experiments separated from one proposed mechanism record.", "evidence_ids": ev(4)},
                {"region": "right-column Experimental Section", "finding": "Exact 1a preparation and detailed Conditions-A/Conditions-B procedures merged into their matching records.", "evidence_ids": ev(4)},
            ],
            "record_ids": [rid("equation1_1r_conditions_a"), rid("scheme4_esi_msms_normal"), rid("scheme4_esi_msms_labeled"), rid("scheme5_proposed_mechanism"), rid("typical_procedure1_starting_material_1a"), rid("table2_entry1"), rid("table4_entry1")],
            "unresolved": ["The equation-1 byproduct is unidentified.", "MS/MS ion structures and proposed intermediates remain unverified.", "The 1a preparation omits atmosphere and numerical duration."],
        },
        {
            "page": 5,
            "state": "attempted",
            "regions": [
                {"region": "upper-left continuation of Conditions B characterization", "finding": "Continuation linked to Table 4 entry 1; no duplicate reaction created.", "evidence_ids": ev(5)},
                {"region": "left-column diiodide preparation", "finding": "Distinct 0.20 mmol isolation experiment extracted with separate 42% E-2a and 37% E-3a yields.", "evidence_ids": ev(5)},
                {"region": "lower-left and upper-right 18O-labeled synthesis", "finding": "Staged glovebox synthesis extracted with 69% isolated yield and 86% 18O incorporation.", "evidence_ids": ev(5)},
                {"region": "middle-right 18O exchange control", "finding": "Treatment control extracted with 93% recovery and <=1.5% 18O incorporation.", "evidence_ids": ev(5)},
                {"region": "lower-right Supporting Information statement", "finding": "Online availability noted, but no SI file is supplied or associated; no SI facts imported.", "evidence_ids": ev(5)},
            ],
            "record_ids": [rid("table4_entry1"), rid("diiodide_3a_isolation_run"), rid("oxygen18_labeled_2a_synthesis"), rid("oxygen18_exchange_control_2a")],
            "unresolved": ["No SI PDF or CIF file is supplied or explicitly associated.", "Diiodide experiment omits atmosphere and numerical duration.", "Isotope-position structures remain machine-unverified."],
        },
    ],
}


OUT.parent.mkdir(parents=True, exist_ok=True)
COVERAGE.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
COVERAGE.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

tasks = json.loads(TASKS.read_text())
for task in tasks:
    if task["document_id"] == DOC and task["task_id"].startswith(f"{DOC}:page"):
        task["state"] = "attempted"
TASKS.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"records": len(records), "coverage_pages": [p["page"] for p in coverage["pages"]]}, ensure_ascii=False))
