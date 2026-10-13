#!/usr/bin/env python3
"""Build evidence-linked machine records for PDF pages 1-6 of doc_b4569e6415d4f17a."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "runs/current/raw_model/records_pages_0001_0006.json"
COVERAGE = ROOT / "runs/current/coverage/pages_0001_0006.json"
TASKS = ROOT / "runs/current/tasks.json"
DOC = "doc_b4569e6415d4f17a"


def ev(page: int, kind: str = "text") -> str:
    return f"{DOC}:page{page}:{kind}"


def evidence(*pages: int) -> list[str]:
    out: list[str] = []
    for page in pages:
        out.extend([ev(page, "text"), ev(page, "image")])
    return out


def fact(value, eids):
    return {
        "value": value,
        "evidence_ids": list(dict.fromkeys(eids)) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def qty(number, unit, **extra):
    return {"number": number, "unit": unit, **extra}


def field(name, value, eids, targets=None):
    out = {"name": name, "fact": fact(value, eids)}
    if targets:
        out["target_entity_ids"] = targets
    return out


SMILES = {
    "toluene": "Cc1ccccc1",
    "DMF": "CN(C)C=O",
    "MeCN": "CC#N",
    "water": "O",
    "methanol": "CO",
    "THF": "C1CCOC1",
    "diethyl ether": "CCOCC",
    "1-hexyne": "C#CCCCC",
    "phenylboronic acid": "OB(O)c1ccccc1",
    "diethylamine": "CCNCC",
    "iodine": "II",
    "bromine": "BrBr",
    "NBS": "O=C1CCC(=O)N1Br",
    "NIS": "O=C1CCC(=O)N1I",
    "sodium borohydride": "[Na+].[BH4-]",
}


def participant(entity_id, role, label, eids, *, name=None, smiles=None, amounts=()):
    if smiles is None:
        smiles = SMILES.get(name or label)
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, eids),
        "name": fact(name, eids) if name else fact(None, []),
        "smiles": fact(smiles, eids) if smiles else fact(None, []),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": [field(n, v, eids) for n, v in amounts],
    }


def record(rid, kind, eids, participants, steps, outcomes, *, notes=(), unresolved=()):
    return {
        "record_id": f"{DOC}:{rid}",
        "document_id": DOC,
        "source_reaction_id": rid,
        "record_kind": kind,
        "status": "needs_review",
        "completeness": "partial",
        "evidence_ids": list(dict.fromkeys(eids)),
        "participants": participants,
        "steps": steps,
        "outcomes": outcomes,
        "notes": [fact(x, eids) for x in notes],
        "review": {
            "method": "model",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": list(unresolved),
        },
    }


def common_step(step_id, pids, conditions):
    return {"step_id": step_id, "participant_ids": pids, "conditions": conditions}


records = []

# Table 1: primary allenol preparations.
table1 = [
    (1, "n-C7H15", "H", "1a", "2a", 5.3, 23),
    (2, "n-C6H13", "CH3", "1b", "2b", 2.5, 36),
    (3, "n-C7H15", "CH3", "1c", "2c", 3.8, 57),
    (4, "n-C6H13", "n-C3H7", "1d", "2d", 6.2, 70),
    (5, "n-C7H15", "n-C3H7", "1e", "2e", 6.7, 53),
    (6, "CH3", "Bn", "1f", "2f", 3.5, 32),
    (7, "n-C3H7", "Bn", "1g", "2g", 4.8, 33),
    (8, "n-C4H9", "Bn", "1h", "2h", 3.3, 38),
    (9, "n-C6H13", "Bn", "1i", "2i", 3.5, 40),
]
for entry, r1, r2, sub, prod, hours, yld in table1:
    pages = (2, 5)
    eids = evidence(*pages)
    ps = [
        participant("substrate", "reactant", sub, eids, name=f"2,3-allenoate {sub}; R1={r1}, R2={r2}"),
        participant("dibal", "reagent", "DIBAL-H", eids, amounts=[("equivalents", qty(2.1, "equiv"))]),
        participant("toluene", "solvent", "toluene", eids, name="toluene"),
        participant("product", "product", prod, eids, name=f"primary 2,3-allenol {prod}; R1={r1}, R2={r2}"),
    ]
    cond = [field("temperature", qty(-78, "°C"), eids), field("time", qty(hours, "h"), eids), field("atmosphere", "open air unless otherwise indicated", evidence(5))]
    if entry == 4:
        ps[0]["amounts"] += [field("substrate_mass", qty(5.88, "g"), eids), field("amount", qty(24.7, "mmol"), eids)]
        ps[1]["amounts"] += [field("reagent_volume", qty(51.9, "mL"), eids), field("amount", qty(59.1, "mmol"), eids), field("concentration", qty(1.0, "M"), eids)]
        ps[2]["amounts"] += [field("solvent_volume", qty(35, "mL"), eids)]
        ps[3]["amounts"] += [field("product_mass", qty(3.39, "g"), eids)]
        cond += [
            field("workup", "quenched with 25 mL methanol; washed with 300 mL 5% aqueous HCl; aqueous layer extracted with ether; combined organic layer dried over Na2SO4, filtered, and evaporated", evidence(5)),
            field("purification", "silica-gel column chromatography, petroleum ether/ethyl acetate 5:1", evidence(5)),
        ]
    outcomes = [field("reported_yield", qty(yld, "%"), eids, ["product"]), field("yield_measurement_basis", "isolated" if entry == 4 else None, eids, ["product"])]
    records.append(record(f"table1_entry{entry}_{prod}", "substrate_scope_entry", eids, ps, [common_step("reduction", [p["entity_id"] for p in ps], cond)], outcomes, unresolved=["Yield basis is not stated in Table 1." if entry != 4 else "Candidate molecular connectivity is unverified."]))

# Table 2: secondary allenol preparations.
table2 = [
    (1, "n-C4H9", "Ph", 12, 40, "5a"),
    (2, "n-C4H9", "m,p-OCH2OC6H3", 15, 45, "5b"),
    (3, "n-C4H9", "p-MeOC6H4", 10, 45, "5c"),
    (4, "n-C4H9", "p-MeC6H4", 12, 57, "5d"),
    (5, "n-C2H5", "m,p-OCH2OC6H3", 16, 44, "5e"),
    (6, "n-C2H5", "p-MeOC6H4", 12, 66, "5f"),
    (7, "n-C2H5", "p-MeC6H4", 11, 51, "5g"),
    (8, "allyl", "m,p-OCH2OC6H3", 12, 62, "5h"),
    (9, "allyl", "p-MeOC6H4", 11, 41, "5i"),
    (10, "allyl", "p-MeC6H4", 17, 56, "5j"),
    (11, "n-C4H9", "alpha-naphthyl", 17, 62, "5k"),
    (12, "n-C4H9", "m-BrC6H4", 20, 58, "5l"),
    (13, "n-C4H9", "p-ClC6H4", 11, 46, "5m"),
    (14, "n-C4H9", "p-NO2C6H4", 17, 66, "5n"),
    (15, "n-C4H9", "o,p-Cl2C6H3", 20, 49, "5o"),
    (16, "n-C4H9", "o-ClC6H4", 20, 52, "5p"),
    (17, "n-C4H9", "CH3", 10, 46, "5q"),
]
for entry, r1, r2, hours, yld, prod in table2:
    pages = (2, 5)
    eids = evidence(*pages)
    ps = [
        participant("bromide", "reactant", f"propargylic bromide 3 (R1={r1})", eids),
        participant("aldehyde", "reactant", f"aldehyde 4 (R2={r2})", eids),
        participant("sncl2", "reagent", "SnCl2", eids),
        participant("nai", "reagent", "NaI", eids),
        participant("dmf", "solvent", "DMF", eids, name="DMF"),
        participant("product", "product", prod, eids, name=f"secondary 2,3-allenol {prod}; R1={r1}, R2={r2}"),
    ]
    cond = [field("temperature", qty(0, "°C"), eids), field("time", qty(hours, "h"), eids), field("atmosphere", "open air unless otherwise indicated", evidence(5))]
    if entry == 1:
        ps[0]["amounts"] += [field("substrate_mass", qty(1.43, "g"), eids), field("amount", qty(8.2, "mmol"), eids)]
        ps[2]["amounts"] += [field("reagent_mass", qty(2.21, "g"), eids), field("amount", qty(11.5, "mmol"), eids)]
        ps[3]["amounts"] += [field("reagent_mass", qty(1.73, "g"), eids), field("amount", qty(11.4, "mmol"), eids)]
        ps[1]["amounts"] += [field("reactant_volume", qty(1.16, "mL"), eids), field("amount", qty(11.4, "mmol"), eids)]
        ps[4]["amounts"] += [field("initial_solvent_volume", qty(40, "mL"), eids), field("aldehyde_solution_solvent_volume", qty(40, "mL"), eids)]
        ps[5]["amounts"] += [field("product_mass", qty(0.66, "g"), eids)]
        cond = [
            field("preactivation_temperature", "r.t.", eids), field("preactivation_time", qty(1, "h"), eids),
            field("aldehyde_addition_temperature", qty(0, "°C"), eids), field("time", qty(12, "h"), eids),
            field("workup", "quenched with 15 mL water; extracted with diethyl ether; washed with saturated NaCl; dried over anhydrous Na2SO4; evaporated", evidence(5)),
            field("purification", "silica-gel column chromatography, petroleum ether/ethyl acetate 10:1", evidence(5)),
        ]
    records.append(record(f"table2_entry{entry}_{prod}", "substrate_scope_entry", eids, ps, [common_step("allenol_formation", [p["entity_id"] for p in ps], cond)], [field("reported_yield", qty(yld, "%"), eids, ["product"]), field("yield_measurement_basis", "isolated" if entry == 1 else None, eids, ["product"])], unresolved=["Yield basis is not stated in Table 2." if entry != 1 else "Candidate molecular connectivity is unverified."]))

# Scheme 1: tertiary allenol preparation.
eids = evidence(2, 5)
ps = [
    participant("bromide", "reactant", "3b", eids, name="3-bromohept-1-yne-type propargylic bromide shown in Scheme 1"),
    participant("acetophenone", "reactant", "PhCOCH3", eids, name="acetophenone", smiles="CC(=O)c1ccccc1"),
    participant("indium", "reagent", "In", eids, smiles="[In]"),
    participant("thf", "solvent", "THF", eids, name="THF"), participant("water", "solvent", "H2O", eids, name="water"),
    participant("product", "product", "5r", eids, name="2-phenyl-3-ethylpenta-3,4-dien-2-ol"),
]
records.append(record("scheme1_5r", "reported_experiment", eids, ps, [common_step("tertiary_allenol_formation", [p["entity_id"] for p in ps], [field("solvent_ratio", "THF/H2O = 1:1", eids), field("temperature", "r.t.", eids), field("time", "overnight", eids), field("atmosphere", "open air unless otherwise indicated", evidence(5))])], [field("reported_yield", qty(30, "%"), eids, ["product"]), field("yield_measurement_basis", None, eids, ["product"])], unresolved=["Absolute quantities, workup, purification, and yield basis are not stated.", "Product structure is unverified."]))

# Table 3: iodocyclization of primary allenols.
table3 = [
    (1, "n-C7H15", "H", "2a", 1.3, 65, "6a"),
    (2, "n-C6H13", "CH3", "2b", 20, 60, "6b"),
    (3, "n-C7H15", "CH3", "2c", 16, 72, "6c"),
    (4, "n-C6H13", "n-C3H7", "2d", 22, 60, "6d"),
    (5, "n-C7H15", "n-C3H7", "2e", 22, 63, "6e"),
    (6, "CH3", "Bn", "2f", 1.7, 67, "6f"),
    (7, "n-C3H7", "Bn", "2g", 10, 73, "6g"),
    (8, "n-C4H9", "Bn", "2h", 2.5, 75, "6h"),
    (9, "n-C6H13", "Bn", "2i", 1.7, 82, "6i"),
]
for entry, r1, r2, sub, hours, yld, prod in table3:
    pages = [2, 5] if entry == 1 else [2, 5]
    eids = evidence(*pages)
    ps = [
        participant("substrate", "reactant", sub, eids, name=f"primary 2,3-allenol {sub}; R1={r1}, R2={r2}", amounts=[("reaction_scale", {"minimum": 0.4, "maximum": 0.5, "unit": "mmol", "raw_text": "0.4–0.5 mmol"})]),
        participant("iodine", "reagent", "I2", eids, name="iodine", amounts=[("equivalents", qty(2.5, "equiv"))]),
        participant("mecn", "solvent", "MeCN", eids, name="MeCN"), participant("water", "solvent", "H2O", eids, name="water"),
        participant("product", "product", prod, eids, name=f"3-iodo-2,5-dihydrofuran {prod}; R1={r1}, R2={r2}"),
    ]
    cond = [
        field("solvent_ratio", "MeCN/H2O = 15:1", eids), field("temperature", "r.t.", eids), field("time", qty(hours, "h"), eids),
        field("atmosphere", "open air unless otherwise indicated", evidence(5)),
        field("workup", "quenched with water then saturated aqueous Na2S2O3; extracted with diethyl ether; washed with aqueous NaCl; dried over Na2SO4; concentrated", evidence(5)),
        field("purification", "silica-gel column chromatography, petroleum ether/ethyl acetate 40:1", evidence(5)),
    ]
    if entry == 1:
        ps[0]["amounts"] += [field("substrate_mass", qty(85.7, "mg"), eids), field("amount", qty(0.5, "mmol"), eids)]
        ps[1]["amounts"] += [field("reagent_mass", qty(319.5, "mg"), eids), field("amount", qty(1.25, "mmol"), eids)]
        ps[2]["amounts"] += [field("solvent_volume", qty(4, "mL"), eids)]
        ps[3]["amounts"] += [field("solvent_volume", qty(0.27, "mL"), eids)]
        ps[4]["amounts"] += [field("product_mass", qty(97.5, "mg"), eids)]
        cond[2] = field("time", qty(80, "min"), eids)
    notes = []
    if entry == 4:
        notes.append("Results prose also states 60% yield for 6d under the same 2.5-equiv-I2 aqueous-MeCN conditions; it is merged with Table 3 entry 4.")
    records.append(record(f"table3_entry{entry}_{prod}", "substrate_scope_entry", eids, ps, [common_step("iodocyclization", [p["entity_id"] for p in ps], cond)], [field("isolated_yield", qty(yld, "%"), eids, ["product"]), field("yield_measurement_basis", "isolated", eids, ["product"])], notes=notes, unresolved=["Product connectivity and stereochemistry are unverified."]))

# Scheme 2 couplings.
eids = evidence(3, 5)
ps = [
    participant("substrate", "reactant", "6d", eids, amounts=[("substrate_mass", qty(82.0, "mg")), ("amount", qty(0.25, "mmol"))]),
    participant("hexyne", "reactant", "1-hexyne", eids, name="1-hexyne", amounts=[("reactant_mass", qty(26.9, "mg")), ("amount", qty(0.325, "mmol"))]),
    participant("pd", "catalyst", "PdCl2(PPh3)2", eids, amounts=[("catalyst_mass", qty(8.5, "mg")), ("catalyst_loading", qty(5, "mol%"))]),
    participant("cui", "catalyst", "CuI", eids, amounts=[("catalyst_mass", qty(4.0, "mg")), ("catalyst_loading", qty(10, "mol%"))]),
    participant("amine", "reagent", "Et2NH", eids, name="diethylamine", amounts=[("reagent_mass", qty(24.7, "mg")), ("amount", qty(0.325, "mmol")), ("equivalents", qty(1.3, "equiv"))]),
    participant("mecn", "solvent", "MeCN", eids, name="MeCN", amounts=[("solvent_volume", qty(2, "mL"))]),
    participant("product", "product", "7a", eids, name="2-hexyl-3-hexynyl-4-propyl-2,5-dihydrofuran", amounts=[("product_mass", qty(67.3, "mg"))]),
]
records.append(record("scheme2_sonogashira_7a", "reported_experiment", eids, ps, [common_step("sonogashira_coupling", [p["entity_id"] for p in ps], [field("temperature", qty(30, "°C"), eids), field("time", qty(17, "h"), eids), field("atmosphere", "N2", eids), field("workup", "added 6 mL water; extracted with ether; washed with saturated brine; dried over Na2SO4; filtered and evaporated", eids), field("purification", "silica-gel column chromatography, petroleum ether/ethyl acetate 100:1", eids)])], [field("isolated_yield", qty(96, "%"), eids, ["product"]), field("yield_measurement_basis", "isolated", eids, ["product"])], unresolved=["Product structure is unverified."]))

eids = evidence(3, 6)
ps = [
    participant("substrate", "reactant", "6d", eids, amounts=[("substrate_mass", qty(82.5, "mg")), ("amount", qty(0.25, "mmol"))]),
    participant("boronic", "reactant", "PhB(OH)2", eids, name="phenylboronic acid", amounts=[("reactant_mass", qty(62.0, "mg")), ("amount", qty(0.5, "mmol"))]),
    participant("pd", "catalyst", "Pd(PPh3)4", eids, amounts=[("catalyst_mass", qty(15.5, "mg")), ("catalyst_loading", qty(5, "mol%"))]),
    participant("methanol", "solvent", "CH3OH", eids, name="methanol", amounts=[("solvent_volume", qty(0.1, "mL"))]),
    participant("carbonate", "reagent", "Na2CO3", eids, amounts=[("solution_volume", qty(0.3, "mL")), ("concentration", qty(2, "M"))]),
    participant("toluene", "solvent", "toluene", eids, name="toluene", amounts=[("solvent_volume", qty(2, "mL"))]),
    participant("product", "product", "8a", eids, name="2-hexyl-3-phenyl-4-propyl-2,5-dihydrofuran", amounts=[("product_mass", qty(64.2, "mg"))]),
]
records.append(record("scheme2_suzuki_8a", "reported_experiment", eids, ps, [common_step("suzuki_coupling", [p["entity_id"] for p in ps], [field("temperature", "reflux", eids), field("time", qty(10, "h"), eids), field("atmosphere", "N2", eids), field("workup", "added 6 mL water; extracted with ether; washed with saturated NaCl; dried over Na2SO4; filtered and evaporated", eids), field("purification", "silica-gel column chromatography", eids)])], [field("isolated_yield", qty(92, "%"), eids, ["product"]), field("yield_measurement_basis", "isolated", eids, ["product"])], unresolved=["Reflux temperature and chromatography eluent are not numerically specified in the detailed paragraph.", "Product structure is unverified."]))

# Table 4: secondary allenol halogenations.
table4 = [
    (1,"5a","n-C4H9","Ph","Br2",2,0,30,80,"10a","12a","≥95:5"),
    (2,"5b","n-C4H9","m,p-OCH2OC6H3","Br2",2,"r.t.",50,78,"10b","12b","98:2"),
    (3,"5b","n-C4H9","m,p-OCH2OC6H3","NBS",1.2,0,30,93,"10b","12b","99:1"),
    (4,"5b","n-C4H9","m,p-OCH2OC6H3","I2",2,"r.t.",60,80,"11b","13b",">99:1"),
    (5,"5c","n-C4H9","p-MeOC6H4","Br2",2,"r.t.",90,71,"10c","12c","≥99:1"),
    (6,"5c","n-C4H9","p-MeOC6H4","NBS",1.2,"r.t.",30,88,"10c","12c","99:1"),
    (7,"5c","n-C4H9","p-MeOC6H4","I2",2,"r.t.",30,77,"11c","13c",">99:1"),
    (8,"5c","n-C4H9","p-MeOC6H4","NIS",2,"r.t.",30,89,"11c","13c",">99:1"),
    (9,"5d","n-C4H9","p-MeC6H4","Br2",1.2,0,60,87,"10d","12d","97:3"),
    (10,"5d","n-C4H9","p-MeC6H4","NBS",1.2,0,140,90,"10d","12d","97:3"),
    (11,"5d","n-C4H9","p-MeC6H4","I2",2,0,25,68,"11d","13d","97:3"),
    (12,"5e","C2H5","m,p-OCH2OC6H3","Br2",1.2,0,25,78,"10e","12e",">99:1"),
    (13,"5e","C2H5","m,p-OCH2OC6H3","NBS",1.2,0,30,84,"10e","12e",">99:1"),
    (14,"5e","C2H5","m,p-OCH2OC6H3","I2",2,"r.t.",30,69,"11e","13e",">99:1"),
    (15,"5e","C2H5","m,p-OCH2OC6H3","NIS",2,"r.t.",25,87,"11e","13e",">99:1"),
    (16,"5f","C2H5","p-MeOC6H4","Br2",1.2,0,30,80,"10f","12f",">99:1"),
    (17,"5f","C2H5","p-MeOC6H4","NBS",1.2,0,40,88,"10f","12f",">99:1"),
    (18,"5f","C2H5","p-MeOC6H4","I2",2,0,30,83,"11f","13f",">99:1"),
    (19,"5g","C2H5","p-MeC6H4","Br2",1.2,0,30,86,"10g","12g","97:3"),
    (20,"5g","C2H5","p-MeC6H4","NBS",1.2,0,35,64,"10g","12g","97:3"),
    (21,"5g","C2H5","p-MeC6H4","I2",2,0,30,55,"11g","13g","97:3"),
    (22,"5g","C2H5","p-MeC6H4","NIS",1.2,"r.t.",40,79,"11g","13g","96:4"),
    (23,"5h","allyl","m,p-OCH2OC6H3","Br2",1.2,0,30,68,"10h","12h",">99:1"),
    (24,"5h","allyl","m,p-OCH2OC6H3","NBS",1.2,0,30,88,"10h","12h",">99:1"),
    (25,"5h","allyl","m,p-OCH2OC6H3","I2",1.2,"r.t.",50,"complicated",None,None,"table dash (–)"),
    (26,"5i","allyl","p-MeOC6H4","Br2",1.2,0,100,57,"10i","12i",">99:1"),
    (27,"5i","allyl","p-MeOC6H4","NBS",1.2,0,50,62,"10i","12i",">99:1"),
    (28,"5i","allyl","p-MeOC6H4","I2",1.2,"r.t.",30,"complicated",None,None,"table dash (–)"),
    (29,"5i","allyl","p-MeOC6H4","I2",1.2,-20,25,37,"11i","13i","≥98:2"),
    (30,"5j","allyl","p-MeC6H4","Br2",1.2,0,55,50,"10j","12j","≥97:3"),
    (31,"5j","allyl","p-MeC6H4","NBS",1.2,0,60,71,"10j","12j","≥97:3"),
    (32,"5k","n-C4H9","alpha-naphthyl","Br2",2,0,30,73,"10k","12k","90:10"),
    (33,"5k","n-C4H9","alpha-naphthyl","NBS",1.2,0,50,76,"10k","12k","93:7"),
    (34,"5l","n-C4H9","m-BrC6H4","Br2",1.2,"r.t.",30,49,"10l","12l","80:20"),
    (35,"5l","n-C4H9","m-BrC6H4","NBS",1.2,0,30,45,"10l","12l","80:20"),
]
table4_ids = []
for entry, sub, r1, r2, reagent, equiv, temp, mins, yld, major, minor, ratio in table4:
    pages = [3, 4, 5]
    if entry in (1, 32, 33): pages.append(6)
    eids = evidence(*pages)
    ps = [participant("substrate", "reactant", sub, eids, name=f"secondary 2,3-allenol {sub}; R1={r1}, R2={r2}"), participant("halogen", "reagent", reagent, eids, name={"Br2":"bromine","I2":"iodine","NBS":"NBS","NIS":"NIS"}[reagent], amounts=[("equivalents", qty(equiv, "equiv"))]), participant("mecn", "solvent", "MeCN", eids, name="MeCN"), participant("water", "solvent", "H2O", eids, name="water")]
    targets = []
    if major:
        ps.append(participant("major", "product", major, eids, name=f"major halo product {major}")); targets.append("major")
    if minor:
        ps.append(participant("minor", "product", minor, eids, name=f"minor ketone product {minor}")); targets.append("minor")
    if not targets:
        ps.append(participant("mixture", "product", "complicated mixture", eids)); targets = ["mixture"]
    cond = [field("solvent_ratio", "MeCN/H2O = 15:1", eids), field("temperature", qty(temp, "°C") if isinstance(temp, (int,float)) else temp, eids), field("time", qty(mins, "min"), eids), field("atmosphere", "open air unless otherwise indicated", evidence(5))]
    if entry == 1:
        ps[0]["amounts"] += [field("substrate_mass", qty(82.4, "mg"), eids), field("amount", qty(0.41, "mmol"), eids)]
        ps[1]["amounts"] += [field("solution_volume", qty(1.6, "mL"), eids), field("amount", qty(0.8, "mmol"), eids), field("concentration", qty(0.5, "M"), eids)]
        ps[2]["amounts"] += [field("solvent_volume", qty(2.4, "mL"), eids)]
        ps[3]["amounts"] += [field("solvent_volume", qty(0.27, "mL"), eids)]
        cond += [field("workup", "quenched with 6 mL water then saturated aqueous Na2S2O3; extracted with diethyl ether (25 mL × 3); washed with NaCl; dried over anhydrous Na2SO4; evaporated", evidence(6)), field("purification", "silica-gel column chromatography, petroleum ether/ethyl acetate 100:1", evidence(6))]
    if entry == 32:
        ps[0]["amounts"] += [field("substrate_mass", qty(100.2, "mg"), eids), field("amount", qty(0.4, "mmol"), eids)]
        ps[1]["amounts"] += [field("solution_volume", qty(1.6, "mL"), eids), field("amount", qty(0.8, "mmol"), eids), field("concentration", qty(0.5, "M"), eids)]
        ps[2]["amounts"] += [field("solvent_volume", qty(2.4, "mL"), eids)]
        ps[3]["amounts"] += [field("solvent_volume", qty(0.27, "mL"), eids)]
    if entry == 33:
        ps[0]["amounts"] += [field("substrate_mass", qty(75.5, "mg"), eids), field("amount", qty(0.3, "mmol"), eids)]
        ps[1]["amounts"] += [field("reagent_mass", qty(64.2, "mg"), eids), field("amount", qty(0.36, "mmol"), eids)]
        ps[2]["amounts"] += [field("solvent_volume", qty(4, "mL"), eids)]
        ps[3]["amounts"] += [field("solvent_volume", qty(0.27, "mL"), eids)]
    outcomes = [field("reported_yield", qty(yld, "%") if isinstance(yld, (int,float)) else yld, eids, targets if entry in (1,32,33,34,35) else [targets[0]]), field("yield_measurement_basis", "isolated" if entry == 1 else None, eids, targets), field("major_minor_product_ratio", ratio, eids, targets), field("ratio_measurement_basis", "1H NMR", eids, targets)]
    rid = f"table4_entry{entry:02d}_{sub}_{reagent.lower()}"
    table4_ids.append(f"{DOC}:{rid}")
    records.append(record(rid, "substrate_scope_entry", eids, ps, [common_step("halogenation_rearrangement", [p["entity_id"] for p in ps], cond)], outcomes, unresolved=["Yield basis is unstated except for the detailed entry-1 chromatographic isolation.", "Product connectivity/stereochemistry is unverified."] + (["No identified product was assigned from the complicated mixture."] if not major else [])))

# Scheme 3.
eids = evidence(4, 5)
ps = [participant("substrate", "reactant", "5q", eids), participant("iodine", "reagent", "I2", eids, name="iodine"), participant("mecn", "solvent", "MeCN", eids, name="MeCN"), participant("water", "solvent", "H2O", eids, name="water"), participant("aldehyde", "product", "11q", eids), participant("ketone", "product", "13q", eids)]
records.append(record("scheme3_5q_11q_13q", "reported_experiment", eids, ps, [common_step("iodination_rearrangement", [p["entity_id"] for p in ps], [field("solvent_ratio", "MeCN/H2O = 15:1", eids), field("temperature", "r.t.", eids), field("time", qty(98, "min"), eids), field("atmosphere", "open air unless otherwise indicated", evidence(5))])], [field("combined_reported_yield", qty(49, "%"), eids, ["aldehyde","ketone"]), field("11q_13q_ratio", "2:98", eids, ["aldehyde","ketone"]), field("yield_measurement_basis", None, eids, ["aldehyde","ketone"])], unresolved=["Iodine loading, scale, workup, purification, and yield basis are not printed in Scheme 3.", "Product structures are unverified."]))

# Scheme 4.
eids = evidence(4, 5)
ps = [participant("substrate", "reactant", "5r", eids, name="2-phenyl-3-ethylpenta-3,4-dien-2-ol"), participant("bromine", "reagent", "Br2", eids, name="bromine"), participant("mecn", "solvent", "MeCN", eids, name="MeCN"), participant("water", "solvent", "H2O", eids, name="water"), participant("product", "product", "12r", eids, name="4-bromo-3-ethyl-3-phenyl-4-penten-2-one")]
records.append(record("scheme4_5r_12r", "reported_experiment", eids, ps, [common_step("bromination_rearrangement", [p["entity_id"] for p in ps], [field("solvent_ratio", "MeCN/H2O = 15:1", eids), field("temperature", qty(0, "°C"), eids), field("time", qty(30, "min"), eids), field("atmosphere", "open air unless otherwise indicated", evidence(5))])], [field("reported_yield", qty(83, "%"), eids, ["product"]), field("yield_measurement_basis", None, eids, ["product"])], unresolved=["Absolute quantities, workup, purification, and yield basis are not printed on page 4.", "Product structure is unverified."]))

# Scheme 5 mechanism.
eids = evidence(4)
ps = [participant("allenol", "reactant", "5", eids, name="generic secondary 2,3-allenol"), participant("electrophile", "reagent", "X+", eids), participant("int14", "unspecified_agent", "14", eids, name="proposed cationic three-membered intermediate"), participant("int15", "unspecified_agent", "15", eids, name="proposed aryl-shift intermediate"), participant("int16", "unspecified_agent", "16", eids, name="proposed hydride-shift intermediate"), participant("enal", "product", "10 or 11", eids), participant("ketone", "product", "12 or 13", eids)]
records.append(record("scheme5_proposed_pathway", "mechanism", eids, ps, [common_step("proposed_electrophilic_interaction", [p["entity_id"] for p in ps], [])], [], notes=["Proposed X+ interaction gives intermediate 14; a 1,2-R2 shift via 15 gives enal 10/11, whereas a 1,2-H shift via 16 gives ketone 12/13 after H+ loss."], unresolved=["Scheme 5 is a proposed mechanism, not a sequence of isolated experimental stages.", "Generic R groups and charged intermediate structures are unverified."]))

# Cross-page reduction beginning on page 6. Yield continues onto page 7 and is intentionally missing here.
eids = evidence(5, 6)
ps = [participant("substrate", "reactant", "12k", eids, name="crude 3-bromo-2-butyl-1-(1-naphthyl)-3-buten-1-one", amounts=[("substrate_mass", qty(38.3, "mg"))]), participant("nabh4", "reagent", "NaBH4", eids, name="sodium borohydride", amounts=[("reagent_mass", qty(3.5, "mg")), ("amount", qty(0.092, "mmol"))]), participant("thf", "solvent", "THF", eids, name="THF", amounts=[("solvent_volume", qty(3, "mL"))]), participant("product", "product", "18k", eids, name="3-bromo-2-butyl-1-(1-naphthyl)-3-buten-1-ol")]
records.append(record("reduction_12k_to_18k", "reported_experiment", eids, ps, [common_step("borohydride_reduction", [p["entity_id"] for p in ps], [field("temperature", "r.t.", eids), field("time", qty(26, "h"), eids), field("atmosphere", "open air unless otherwise indicated", evidence(5)), field("workup", "quenched with 2 mL water; extracted with diethyl ether (3 × 10 mL); washed with saturated brine; dried over anhydrous Na2SO4; evaporated", evidence(6)), field("purification", "silica-gel column chromatography, petroleum ether/ethyl acetate 20:1", evidence(6))])], [field("reported_yield", None, eids, ["product"]), field("yield_measurement_basis", None, eids, ["product"])], unresolved=["The yield and product mass continue onto PDF page 7, outside this batch's claimed coverage, and are therefore left missing.", "Starting material is described as crude 12k; its purity and amount are not reported.", "Product structure/stereochemistry is unverified."]))

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")

def page_record_ids(page):
    return [r["record_id"] for r in records if ev(page, "text") in r["evidence_ids"] or ev(page, "image") in r["evidence_ids"]]

page2_ids = page_record_ids(2)
page3_ids = page_record_ids(3)
page4_ids = page_record_ids(4)
page5_ids = page_record_ids(5)
page6_ids = page_record_ids(6)

coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {"page": 1, "state": "attempted", "regions": [
            {"region": "title, abstract, introduction, and lower-right opening Results text", "finding": "No row-level present-paper experiment or reaction arrow. Abstract-level reaction families were not duplicated; cited prior halogenation examples remain literature context.", "evidence_ids": evidence(1)}
        ], "record_ids": [], "unresolved": ["Supporting information is mentioned online but was not supplied or explicitly associated."]},
        {"page": 2, "state": "attempted", "regions": [
            {"region": "upper-left Table 1", "finding": "Nine independent DIBAL-H preparations of primary 2,3-allenols extracted row by row.", "evidence_ids": evidence(2)},
            {"region": "lower-left Table 2", "finding": "Seventeen independent SnCl2/NaI preparations of secondary 2,3-allenols extracted row by row.", "evidence_ids": evidence(2)},
            {"region": "upper-right Scheme 1", "finding": "One present-paper tertiary allenol preparation (5r) extracted.", "evidence_ids": evidence(2)},
            {"region": "middle-right Table 3 and prose", "finding": "Nine iodine cyclizations extracted; the narrative 2d/6d result is merged with Table 3 entry 4.", "evidence_ids": evidence(2)}
        ], "record_ids": page2_ids, "unresolved": ["Most Table 1/2 rows omit workup, purification, atmosphere, and yield basis.", "Complex structures and stereochemistry remain unverified."]},
        {"page": 3, "state": "attempted", "regions": [
            {"region": "upper Scheme 2", "finding": "Sonogashira and Suzuki couplings of 6d extracted as two independent experiments.", "evidence_ids": evidence(3)},
            {"region": "Table 4 and footnote", "finding": "All 35 halogenation/rearrangement rows extracted independently, including two complicated mixtures, the -20 °C row, and NMR product ratios.", "evidence_ids": evidence(3)}
        ], "record_ids": page3_ids, "unresolved": ["Table 4 does not generally state yield basis, scale, workup, or purification.", "The table's two complicated outcomes do not identify products."]},
        {"page": 4, "state": "attempted", "regions": [
            {"region": "left-column Table 4 discussion", "finding": "Narrative selectivity and failed-iodination context linked to the 35 Table 4 rows; the cited 77% prior-communication result for 10a was not duplicated as a current experiment.", "evidence_ids": evidence(4)},
            {"region": "lower-left Scheme 3", "finding": "5q iodination extracted with 49% combined yield and 11q:13q = 2:98.", "evidence_ids": evidence(4)},
            {"region": "upper-right Scheme 4", "finding": "5r bromination to 12r extracted at 0 °C for 30 min in 83% reported yield.", "evidence_ids": evidence(4)},
            {"region": "center-right Scheme 5", "finding": "1,2-R shift versus 1,2-H shift pathway classified as a proposed mechanism, not an executed experiment.", "evidence_ids": evidence(4)}
        ], "record_ids": page4_ids, "unresolved": ["Scheme 3/4 omit several absolute quantities and operational details.", "Scheme 5 intermediates are proposed and structurally unverified."]},
        {"page": 5, "state": "attempted", "regions": [
            {"region": "General Methods and 2d typical procedure", "finding": "Open-air default and exact DIBAL-H preparation of 2d merged into Table 1 entry 4.", "evidence_ids": evidence(5)},
            {"region": "5a typical procedure", "finding": "Exact two-stage SnCl2/NaI/aldehyde procedure merged into Table 2 entry 1.", "evidence_ids": evidence(5)},
            {"region": "iodocyclization general procedure and 6a preparation", "finding": "General workup/purification linked to Table 3; exact 6a quantities and 80 min duration merged into entry 1.", "evidence_ids": evidence(5)},
            {"region": "lower-right Sonogashira procedure", "finding": "Exact quantities, atmosphere, workup, product mass, and isolated yield merged into Scheme 2's 7a experiment.", "evidence_ids": evidence(5)}
        ], "record_ids": page5_ids, "unresolved": ["Online supporting information mentioned by the paper is not an associated source."]},
        {"page": 6, "state": "attempted", "regions": [
            {"region": "left-column Suzuki procedure", "finding": "Exact 6d/phenylboronic-acid coupling quantities, N2/reflux/10 h, workup, 64.2 mg and 92% isolated yield merged into 8a.", "evidence_ids": evidence(6)},
            {"region": "right-column 10a/10k/12k procedures", "finding": "Exact details merged into Table 4 entries 1, 32, and 33, including mixture ratios and masses where printed.", "evidence_ids": evidence(6)},
            {"region": "lower-right 12k-to-18k reduction", "finding": "Cross-page reduction extracted through the end of page 6; yield remains missing because it appears on page 7, outside claimed coverage.", "evidence_ids": evidence(6)}
        ], "record_ids": page6_ids, "unresolved": ["The 18k product mass/yield and characterization continue on page 7 and were not imported in this pages-1-6 batch.", "Most abbreviated 10k/12k paragraphs do not restate complete workup and purification."]},
    ],
}
COVERAGE.parent.mkdir(parents=True, exist_ok=True)
COVERAGE.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

tasks = json.loads(TASKS.read_text())
for task in tasks:
    if task["document_id"] == DOC and task["task_id"].startswith(f"{DOC}:page"):
        page = int(task["task_id"].split(":page", 1)[1].split(":", 1)[0])
        if 1 <= page <= 6:
            task["state"] = "attempted"
TASKS.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"records": len(records), "record_file": str(OUT), "coverage_file": str(COVERAGE)}, ensure_ascii=False))
