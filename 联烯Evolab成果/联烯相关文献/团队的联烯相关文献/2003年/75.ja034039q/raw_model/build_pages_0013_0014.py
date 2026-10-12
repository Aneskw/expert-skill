#!/usr/bin/env python3
"""Build evidence-linked machine records for source.pdf pages 13-14.

Page 13 completes the Z-4f procedure begun on page 12, reports two
sulfoxide oxidations, and starts the C-S coupling procedures. Page 14
continues those procedures. Existing table/scheme records are enriched under
their original IDs; only the distinct chiral Z-6e oxidation receives a new ID.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path

DOC = "doc_eae2cf05b16fe8b6"
BASE = Path(__file__).resolve().parents[1]
DATASET = BASE / "dataset.json"
OUT = Path(__file__).with_name("extracted_records_pages_0013_0014.json")
COVERAGE = BASE / "coverage" / "pages_0013_0014.json"
TASKS = BASE / "tasks.json"


def evidence(*pages: int) -> list[str]:
    return list(dict.fromkeys(
        f"{DOC}:page{page}:{kind}" for page in pages for kind in ("text", "image")
    ))


def fact(value, pages=(13,)):
    return {
        "value": value,
        "evidence_ids": evidence(*pages) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def field(name, value, pages=(13,), targets=None):
    result = {"name": name, "fact": fact(value, pages)}
    if targets:
        result["target_entity_ids"] = list(targets)
    return result


def q(number, unit, **extra):
    result = {"number": number, "unit": unit}
    result.update(extra)
    return result


SMILES = {
    "m-CPBA": "O=C(OO)c1cccc(Cl)c1",
    "dichloromethane": "ClCCl",
    "THF": "C1CCOC1",
    "DMF": "CN(C)C=O",
    "n-BuLi": "[Li]CCCC",
    "1-chloro-4-iodobenzene": "Clc1ccc(I)cc1",
    "4-iodoanisole": "COc1ccc(I)cc1",
}


def amounts(items, pages):
    return [field(name, value, pages) for name, value in items]


def participant(entity_id, role, label, pages=(13,), *, name=None, smiles=None, amount_items=()):
    if smiles is None:
        smiles = SMILES.get(name or label)
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, pages),
        "name": fact(name, pages) if name is not None else fact(None),
        "smiles": fact(smiles, pages) if smiles is not None else fact(None),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": amounts(amount_items, pages),
    }


data = json.loads(DATASET.read_text())
existing = {r["source_reaction_id"]: r for r in data["experiments"]}
records = []


def clone(rid, *pages):
    rec = copy.deepcopy(existing[rid])
    rec["status"] = "candidate"
    rec["evidence_ids"] = list(dict.fromkeys(rec["evidence_ids"] + evidence(*pages)))
    rec["review"]["method"] = "none"
    rec["review"]["reviewer"] = None
    rec["review"]["checked_fields"] = []
    return rec


def find_part(rec, label):
    return next(p for p in rec["participants"] if p["label"]["value"] == label)


def product_part(rec):
    return next(p for p in rec["participants"] if p["role"] == "product")


def set_amounts(rec, label, items, pages):
    find_part(rec, label)["amounts"] = amounts(items, pages)


def add_part(rec, entity_id, role, label, pages, *, name=None, smiles=None, amount_items=()):
    if any(p["entity_id"] == entity_id for p in rec["participants"]):
        return
    rec["participants"].append(participant(entity_id, role, label, pages, name=name, smiles=smiles, amount_items=amount_items))


def replace_condition(step, name, value, pages):
    step["conditions"] = [c for c in step["conditions"] if c["name"] != name]
    step["conditions"].append(field(name, value, pages))


def set_outcome(rec, name, value, pages, targets=True):
    rec["outcomes"] = [o for o in rec["outcomes"] if o["name"] != name]
    target_ids = [product_part(rec)["entity_id"]] if targets else None
    rec["outcomes"].append(field(name, value, pages, target_ids))


def unresolved(rec, *items):
    rec["review"]["unresolved"] = list(dict.fromkeys([
        *items,
        "Supporting information was not supplied or explicitly associated.",
        "Molecular structures and stereochemical assignments remain machine-unverified.",
    ]))


# Completion of Table 5 entry 11 from the bottom of page 12.
rec = clone("table5_entry_11", 13)
set_amounts(rec, "Z-4f", [("product_mass", q(105.9, "mg"))], (13,))
step = next(s for s in rec["steps"] if s["step_id"] == "step3_coupling")
replace_condition(step, "temperature", "ambient temperature", (13,))
replace_condition(step, "time", q(1.5, "h"), (13,))
step["conditions"] += [
    field("workup", "quenched with saturated aqueous NH4Cl (2 mL); ether extraction; combined organic layer washed four times with brine and dried over MgSO4", (13,)),
    field("purification", "flash chromatography on silica gel", (13,)),
]
unresolved(rec, "Yield basis is not explicitly named even though a product mass is reported.")
records.append(rec)


# Detailed oxidation corresponding to equation 5. The page-6 label Z-4e
# conflicts with the detailed page-13 substrate Z-4d; page 13 controls the
# detailed procedure while the discrepancy remains explicit.
rec = clone("eq5_sulfoxide_oxidation", 13)
sub = find_part(rec, "Z-4e (label printed in eq 5)")
sub["label"] = fact("Z-4d", (13,))
sub["name"] = fact("Z-1-(benzenesulfinyl)-2-phenylundec-1-en-3-ol", (13,))
sub["amounts"] = amounts([("mass", q(111, "mg")), ("amount", q(0.3, "mmol"))], (13,))
set_amounts(rec, "m-CPBA", [("purity", q(85, "%")), ("mass", q(91.4, "mg")), ("amount", q(0.45, "mmol"))], (13,))
set_amounts(rec, "CH2Cl2", [("reagent_solution_volume", q(3, "mL")), ("substrate_solution_volume", q(3, "mL"))], (13,))
set_amounts(rec, "Z-6e", [("product_mass", q(100.4, "mg"))], (13,))
step = rec["steps"][0]
step["participant_ids"] = [p["entity_id"] for p in rec["participants"] if p["role"] != "product"]
step["conditions"] = [
    field("operation", "m-CPBA solution added to the Z-4d solution", (13,)),
    field("temperature", q(25, "°C"), (13,)),
    field("time", q(30, "min"), (13,)),
    field("solvent", "CH2Cl2", (13,)),
    field("workup", "saturated Na2SO3 (2 mL) and saturated NaHCO3 (2 mL) added; layers separated; aqueous layer extracted with CH2Cl2; combined organic layer dried over MgSO4; solvent evaporated", (13,)),
    field("purification", "flash chromatography, n-hexane/ethyl acetate 5:1", (13,)),
]
set_outcome(rec, "yield", q(87, "%"), (13,))
set_outcome(rec, "yield_measurement_basis", None, (13,))
set_outcome(rec, "reaction_outcome", "sulfoxide oxidized to sulfone", (13,))
unresolved(rec, "The page-6 equation prints substrate label Z-4e, but the page-13 detailed procedure explicitly uses Z-4d; the detailed label is used and the source discrepancy is retained.", "Yield basis is not explicitly named.")
records.append(rec)


# Distinct chiral oxidation. The paragraph reports quantities, product mass,
# yield and ee, but does not explicitly repeat the preceding procedure's
# solvent, time, temperature, workup or purification.
records.append({
    "record_id": f"{DOC}:s_z6e_oxidation",
    "document_id": DOC,
    "source_reaction_id": "s_z6e_oxidation",
    "record_kind": "reported_experiment",
    "status": "candidate",
    "completeness": "partial",
    "evidence_ids": evidence(13),
    "participants": [
        participant("sz6e_sub", "reactant", "(S)-Z-4d", (13,), name="(S)-Z-1-(benzenesulfinyl)-2-phenylundec-1-en-3-ol", amount_items=[("mass", q(420, "mg")), ("amount", q(1.0, "mmol"))]),
        participant("sz6e_mcpba", "reagent", "m-CPBA", (13,), name="m-CPBA", amount_items=[("purity", q(85, "%")), ("mass", q(244, "mg")), ("amount", q(1.2, "mmol"))]),
        participant("sz6e_prod", "product", "(S)-Z-6e", (13,), name="(S)-Z-1-(benzenesulfonyl)-2-phenylundec-1-en-3-ol", amount_items=[("product_mass", q(348.9, "mg"))]),
    ],
    "steps": [{
        "step_id": "step1_oxidation",
        "participant_ids": ["sz6e_sub", "sz6e_mcpba"],
        "conditions": [
            field("operation", "reaction of m-CPBA and (S)-Z-4d", (13,)),
            field("temperature", None),
            field("time", None),
            field("solvent", None),
            field("workup", None),
            field("purification", None),
        ],
    }],
    "outcomes": [
        field("yield", q(80, "%"), (13,), ["sz6e_prod"]),
        field("product_ee", q(96.0, "%"), (13,), ["sz6e_prod"]),
        field("yield_measurement_basis", None, targets=["sz6e_prod"]),
    ],
    "notes": [fact("The chiral example is printed immediately after the detailed achiral Z-6e oxidation, but the source does not explicitly state that all preceding conditions apply.", (13,))],
    "review": {
        "method": "none",
        "reviewer": None,
        "checked_fields": [],
        "unresolved": [
            "The chiral paragraph does not repeat solvent, temperature, time, workup, or purification; these fields remain missing rather than inheriting the preceding experiment by inference.",
            "Yield basis is not explicitly named.",
            "Supporting information was not supplied or explicitly associated.",
            "Molecular structures and stereochemical assignments remain machine-unverified.",
        ],
    },
})


# Exact procedure-specific data for Table 7. Entries 1-2 use aryllithium to
# zinc transmetalation; entries 3-10 use the printed general Grignard/ZnBr2
# procedure. The table times/temperatures already present remain authoritative.
table7 = {
    1: dict(page=13, zinc=("ZnBr2", [("mass", q(450, "mg")), ("amount", q(2.0, "mmol"))]), precursor=("1-chloro-4-iodobenzene", [("mass", q(477, "mg")), ("amount", q(2.0, "mmol"))]), organolithium=[("concentration", q(2.5, "M")), ("volume", q(0.8, "mL")), ("amount", q(2.0, "mmol"))], substrate=("Z-4a", [("mass", q(103.2, "mg")), ("amount", q(0.4, "mmol"))]), catalyst=[("mass", q(5, "mg")), ("loading", q(5, "mol%"))], dmf=q(4, "mL"), thf=[("aryl_halide_solution_volume", q(2, "mL")), ("ZnBr2_solution_volume", q(2, "mL"))], product=q(66.9, "mg")),
    2: dict(page=13, zinc=("ZnBr2", [("mass", q(450, "mg")), ("amount", q(2.0, "mmol"))]), precursor=("4-iodoanisole", [("mass", q(468, "mg")), ("amount", q(2.0, "mmol"))]), organolithium=[("concentration", q(2.5, "M")), ("volume", q(0.8, "mL")), ("amount", q(2.0, "mmol"))], substrate=("Z-4a", [("mass", q(103.2, "mg")), ("amount", q(0.4, "mmol"))]), catalyst=[("mass", q(5, "mg")), ("loading", q(5, "mol%"))], dmf=q(4, "mL"), thf=[("aryl_halide_solution_volume", q(2, "mL")), ("ZnBr2_solution_volume", q(2, "mL"))], product=q(70.4, "mg")),
    3: dict(page=13, zinc=("ZnBr2", [("mass", q(450, "mg")), ("amount", q(2.0, "mmol"))]), grignard=("PhMgBr", [("concentration", q(0.7905, "M")), ("volume", q(2.53, "mL")), ("amount", q(2.0, "mmol"))]), substrate=("Z-4a", [("mass", q(103.2, "mg")), ("amount", q(0.4, "mmol"))]), catalyst=[("mass", q(5, "mg")), ("loading", q(5, "mol%"))], dmf=q(4, "mL"), product=q(70.5, "mg")),
    4: dict(page=13, zinc=("ZnBr2", [("mass", q(450, "mg")), ("amount", q(2.0, "mmol")), ("THF_volume", q(2.2, "mL"))]), grignard=("o-MeOC6H4MgBr", [("concentration", q(0.53, "M")), ("volume", q(3.8, "mL")), ("amount", q(2.5, "mmol"))]), substrate=("Z-4a", [("mass", q(129, "mg")), ("amount", q(0.5, "mmol"))]), catalyst=[("mass", q(12.8, "mg")), ("loading", q(10, "mol%"))], dmf=q(6, "mL"), product=q(81.5, "mg")),
    5: dict(page=13, zinc=("ZnBr2", [("mass", q(450, "mg")), ("amount", q(2.0, "mmol"))]), grignard=("PhMgBr", [("concentration", q(1.0, "M")), ("volume", q(2.0, "mL")), ("amount", q(2.0, "mmol"))]), substrate=("Z-4d", [("mass", q(148, "mg")), ("amount", q(0.4, "mmol"))]), catalyst=[("mass", q(10, "mg")), ("loading", q(10, "mol%"))], dmf=q(4, "mL"), product=q(88.3, "mg"), detailed_yield=q(68.6, "%")),
    6: dict(page=13, zinc=("ZnBr2", [("mass", q(450, "mg")), ("amount", q(2.0, "mmol"))]), grignard=("PhMgBr", [("concentration", q(0.7905, "M")), ("volume", q(2.5, "mL")), ("amount", q(2.0, "mmol"))]), substrate=("(S)-Z-4d", [("mass", q(148, "mg")), ("amount", q(0.4, "mmol"))]), catalyst=[("mass", q(10, "mg")), ("loading", q(10, "mol%"))], dmf=q(4, "mL"), product=q(82.2, "mg")),
    7: dict(page=14, zinc=("ZnBr2", [("mass", q(450, "mg")), ("amount", q(2.0, "mmol"))]), grignard=("p-MeOC6H4MgBr", [("concentration", q(0.55, "M")), ("volume", q(3.6, "mL")), ("amount", q(2.0, "mmol"))]), substrate=("Z-4d", [("mass", q(148, "mg")), ("amount", q(0.4, "mmol"))]), catalyst=[("mass", q(10, "mg")), ("loading", q(10, "mol%"))], dmf=q(5, "mL"), product=q(84.6, "mg")),
    8: dict(page=14, zinc=("ZnBr2", [("mass", q(450, "mg")), ("amount", q(2.0, "mmol"))]), grignard=("p-MeOC6H4MgBr", [("concentration", q(0.55, "M")), ("volume", q(3.6, "mL")), ("amount", q(2.0, "mmol"))]), substrate=("(S)-Z-4d", [("mass", q(148, "mg")), ("amount", q(0.4, "mmol"))]), catalyst=[("mass", q(10, "mg")), ("loading", q(10, "mol%"))], dmf=q(5, "mL"), product=q(75, "mg")),
    9: dict(page=14, zinc=("ZnBr2", [("mass", q(360, "mg")), ("amount", q(1.6, "mmol"))]), grignard=("p-N(CH3)2C6H4MgBr", [("concentration", q(0.85, "M")), ("volume", q(1.9, "mL")), ("amount", q(1.6, "mmol"))]), substrate=("Z-4c", [("mass", q(125.6, "mg")), ("amount", q(0.4, "mmol"))]), catalyst=[("mass", q(10.28, "mg")), ("loading", q(10, "mol%"))], dmf=q(4, "mL"), product=q(93.6, "mg")),
    10: dict(page=14, zinc=("ZnBr2", [("mass", q(360, "mg")), ("amount", q(1.6, "mmol"))]), grignard=("p-N(CH3)2C6H4MgBr", [("concentration", q(0.85, "M")), ("volume", q(1.9, "mL")), ("amount", q(1.6, "mmol"))]), substrate=("(R)-Z-4c", [("mass", q(125.6, "mg")), ("amount", q(0.4, "mmol"))]), catalyst=[("mass", q(10.28, "mg")), ("loading", q(10, "mol%"))], dmf=q(4, "mL"), product=q(89.7, "mg")),
}


def enrich_coupling(rec, entry, spec, table):
    page = spec["page"]
    prefix = f"t{table}e{entry}"
    set_amounts(rec, spec["substrate"][0], spec["substrate"][1], (page,))
    set_amounts(rec, "Ni(acac)2", spec["catalyst"], (page,))
    product_part(rec)["amounts"] = amounts([("product_mass", spec["product"])], (page,))
    add_part(rec, f"{prefix}_znbr2", "reagent", spec["zinc"][0], (page,), amount_items=spec["zinc"][1])
    add_part(rec, f"{prefix}_dmf", "solvent", "DMF", (page,), name="DMF", amount_items=[("volume", spec["dmf"])])
    if "precursor" in spec:
        add_part(rec, f"{prefix}_aryl_iodide", "reactant", spec["precursor"][0], (page,), name=spec["precursor"][0], amount_items=spec["precursor"][1])
        add_part(rec, f"{prefix}_nbuli", "reagent", "n-BuLi", (page,), name="n-BuLi", amount_items=spec["organolithium"])
        add_part(rec, f"{prefix}_thf", "solvent", "THF", (page,), name="THF", amount_items=spec["thf"])
        rec["steps"] = [
            {"step_id": "step1_aryllithium_generation", "participant_ids": [f"{prefix}_aryl_iodide", f"{prefix}_nbuli", f"{prefix}_thf"], "conditions": [field("temperature", q(-78, "°C"), (page,)), field("addition_time", q(5, "min"), (page,)), field("time_after_addition", q(5, "min"), (page,)), field("atmosphere", "N2", (page,))]},
            {"step_id": "step2_organozinc_generation", "participant_ids": [f"{prefix}_aryl_iodide", f"{prefix}_nbuli", f"{prefix}_znbr2", f"{prefix}_thf"], "conditions": [field("operation", "THF solution of ZnBr2 added", (page,)), field("time", q(30, "min"), (page,))]},
            {"step_id": "step3_coupling", "participant_ids": [next(p["entity_id"] for p in rec["participants"] if p["role"] == "reactant" and p["label"]["value"] == spec["substrate"][0]), next(p["entity_id"] for p in rec["participants"] if p["role"] == "catalyst"), f"{prefix}_dmf"], "conditions": [field("temperature", q(80, "°C"), (page,)), field("time", q(1.5 if entry == 1 else 3, "h"), (6,)), field("solvent", "DMF/THF", (page,)), field("workup", "poured into saturated aqueous NH4Cl (2 mL); extracted with diethyl ether; combined organic layer dried over MgSO4", (13,)), field("purification", "silica-gel chromatography", (13,))]},
        ]
    else:
        add_part(rec, f"{prefix}_grignard", "reagent", spec["grignard"][0], (page,), amount_items=spec["grignard"][1])
        temp_field = next(c for c in rec["steps"][0]["conditions"] if c["name"] == "temperature")
        time_field = next(c for c in rec["steps"][0]["conditions"] if c["name"] == "time")
        rec["steps"] = [
            {"step_id": "step1_organozinc_generation", "participant_ids": [f"{prefix}_znbr2", f"{prefix}_grignard"], "conditions": [field("operation", "dry ZnBr2 in dry THF added to the Grignard reagent", (13,)), field("temperature", "ambient temperature", (13,)), field("time", {"minimum": 0.5, "maximum": 1, "unit": "h", "raw_text": "0.5-1 h"}, (13,))]},
            {"step_id": "step2_coupling", "participant_ids": [next(p["entity_id"] for p in rec["participants"] if p["role"] == "reactant" and p["label"]["value"] == spec["substrate"][0]), next(p["entity_id"] for p in rec["participants"] if p["role"] == "catalyst"), f"{prefix}_dmf"], "conditions": [field("initial_temperature", q(0, "°C"), (13,)), copy.deepcopy(temp_field), copy.deepcopy(time_field), field("solvent", "DMF/THF", (13, page)), field("workup", "saturated aqueous NH4Cl; diethyl ether extraction; combined organic layer dried over MgSO4", (13,)), field("purification", "silica-gel chromatography", (13,))]},
        ]
    if "detailed_yield" in spec:
        set_outcome(rec, "yield", spec["detailed_yield"], (page,))
    unresolved_items = ["Yield basis is not explicitly named even though a product mass is reported."]
    if entry == 5 and table == 7:
        unresolved_items.append("The detailed procedure reports 68.6%, whereas Table 7 rounds the yield to 69%; the detailed value is retained.")
    unresolved(rec, *unresolved_items)
    return rec


for entry, spec in table7.items():
    pages = (13, 14) if entry >= 7 else (spec["page"],)
    records.append(enrich_coupling(clone(f"table7_entry_{entry:02d}", *pages), entry, spec, 7))


# Table 8 C-SO2Ph couplings. All use the page-13 general procedure and the
# exact time already captured from Table 8 on page 6.
table8 = {
    1: dict(zinc=[("mass", q(450, "mg")), ("amount", q(2.0, "mmol"))], grignard=("m-MeC6H4MgBr", [("concentration", q(0.8675, "M")), ("volume", q(2.30, "mL")), ("amount", q(2.0, "mmol"))]), substrate=("Z-6e", [("mass", q(193, "mg")), ("amount", q(0.5, "mmol"))]), dmf=q(5, "mL"), ni=[("mass", q(12.85, "mg")), ("loading", q(10, "mol%"))], product=q(106.2, "mg"), detailed_yield=q(63.2, "%")),
    2: dict(zinc=[("mass", q(315, "mg")), ("amount", q(1.4, "mmol"))], grignard=("m-MeC6H4MgBr", [("concentration", q(0.8675, "M")), ("volume", q(1.6, "mL")), ("amount", q(1.4, "mmol"))]), substrate=("(S)-Z-6e", [("mass", q(135, "mg")), ("amount", q(0.35, "mmol")), ("starting_material_ee", q(96.0, "%"))]), dmf=q(3.5, "mL"), ni=[("mass", q(9.0, "mg")), ("loading", q(10, "mol%"))], product=q(66.4, "mg")),
    3: dict(zinc=[("mass", q(450, "mg")), ("amount", q(2.0, "mmol"))], grignard=("p-MeC6H4MgBr", [("concentration", q(0.85, "M")), ("volume", q(2.35, "mL")), ("amount", q(2.0, "mmol"))]), substrate=("Z-6e", [("mass", q(193, "mg")), ("amount", q(0.5, "mmol"))]), dmf=q(5, "mL"), ni=[("mass", q(12.85, "mg")), ("loading", q(10, "mol%"))], product=q(110, "mg")),
    4: dict(zinc=[("mass", q(450, "mg")), ("amount", q(2.0, "mmol"))], grignard=("p-MeC6H4MgBr", [("concentration", q(0.85, "M")), ("volume", q(2.35, "mL")), ("amount", q(2.0, "mmol"))]), substrate=("(S)-Z-6e", [("mass", q(193, "mg")), ("amount", q(0.5, "mmol")), ("starting_material_ee", q(96.0, "%"))]), dmf=q(5, "mL"), ni=[("mass", q(12.85, "mg")), ("loading", q(10, "mol%"))], product=q(108.5, "mg")),
    5: dict(zinc=[("mass", q(225, "mg")), ("amount", q(1.0, "mmol"))], grignard=("p-CH3OC6H4MgBr", [("concentration", q(1.00, "M")), ("volume", q(1.00, "mL")), ("amount", q(1.0, "mmol"))]), substrate=("Z-6e", [("mass", q(96.5, "mg")), ("amount", q(0.25, "mmol"))]), dmf=q(2.5, "mL"), ni=[("mass", q(6.4, "mg")), ("loading", q(10, "mol%"))], product=q(52.8, "mg")),
    6: dict(zinc=[("mass", q(225, "mg")), ("amount", q(1.0, "mmol"))], grignard=("p-N(CH3)2C6H4MgBr", [("concentration", q(0.80, "M")), ("volume", q(1.25, "mL")), ("amount", q(1.0, "mmol"))]), substrate=("Z-6e", [("mass", q(96.5, "mg")), ("amount", q(0.25, "mmol"))]), dmf=q(2.5, "mL"), ni=[("mass", q(6.4, "mg")), ("loading", q(10, "mol%"))], product=q(64, "mg")),
}

for entry, spec in table8.items():
    rec = clone(f"table8_entry_{entry:02d}", 13, 14)
    prefix = f"t8e{entry}"
    set_amounts(rec, spec["substrate"][0], spec["substrate"][1], (14,))
    set_amounts(rec, "Ni(acac)2", spec["ni"], (14,))
    product_part(rec)["amounts"] = amounts([("product_mass", spec["product"])], (14,))
    add_part(rec, f"{prefix}_znbr2", "reagent", "ZnBr2", (14,), amount_items=spec["zinc"])
    add_part(rec, f"{prefix}_grignard", "reagent", spec["grignard"][0], (14,), amount_items=spec["grignard"][1])
    add_part(rec, f"{prefix}_dmf", "solvent", "DMF", (14,), name="DMF", amount_items=[("volume", spec["dmf"])])
    old = rec["steps"][0]
    temp_field = next(c for c in old["conditions"] if c["name"] == "temperature")
    time_field = next(c for c in old["conditions"] if c["name"] == "time")
    rec["steps"] = [
        {"step_id": "step1_organozinc_generation", "participant_ids": [f"{prefix}_znbr2", f"{prefix}_grignard"], "conditions": [field("operation", "dry ZnBr2 in dry THF added to the Grignard reagent", (13,)), field("temperature", "ambient temperature", (13,)), field("time", {"minimum": 0.5, "maximum": 1, "unit": "h", "raw_text": "0.5-1 h"}, (13,))]},
        {"step_id": "step2_coupling", "participant_ids": [next(p["entity_id"] for p in rec["participants"] if p["role"] == "reactant"), next(p["entity_id"] for p in rec["participants"] if p["role"] == "catalyst"), f"{prefix}_dmf"], "conditions": [field("initial_temperature", q(0, "°C"), (13,)), copy.deepcopy(temp_field), copy.deepcopy(time_field), field("solvent", "DMF/THF", (13, 14)), field("workup", "saturated aqueous NH4Cl; diethyl ether extraction; combined organic layer dried over MgSO4", (13,)), field("purification", "silica-gel chromatography", (13,))]},
    ]
    if "detailed_yield" in spec:
        set_outcome(rec, "yield", spec["detailed_yield"], (14,))
    issues = ["Yield basis is not explicitly named even though a product mass is reported."]
    if entry == 1:
        issues.append("The detailed procedure reports 63.2%, whereas Table 8 rounds the yield to 63%; the detailed value is retained.")
    unresolved(rec, *issues)
    records.append(rec)


page13_ids = [
    f"{DOC}:table5_entry_11",
    f"{DOC}:eq5_sulfoxide_oxidation",
    f"{DOC}:s_z6e_oxidation",
    *[f"{DOC}:table7_entry_{i:02d}" for i in range(1, 8)],
]
page14_ids = [
    *[f"{DOC}:table7_entry_{i:02d}" for i in range(7, 11)],
    *[f"{DOC}:table8_entry_{i:02d}" for i in range(1, 7)],
]

coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 13,
            "state": "attempted",
            "regions": [
                {"region": "left column top, continuation of Z-4f", "finding": "Completion of the page-12 phenylacetynylzinc coupling: 1.5 h ambient-temperature coupling, workup, purification, and 105.9 mg/94% Z-4f linked to existing Table 5 entry 11.", "evidence_ids": evidence(13)},
                {"region": "left column, Z-6e and (S)-Z-6e oxidations", "finding": "Two distinct m-CPBA oxidations inventoried: achiral Z-4d to Z-6e (87%) and chiral (S)-Z-4d to (S)-Z-6e (80%, 96.0% ee).", "evidence_ids": evidence(13)},
                {"region": "left lower column and right upper column, Z-5a and Z-5b", "finding": "Two aryllithium-to-organozinc/Ni coupling procedures enriched with exact precursor, reagent, catalyst, solvent, time, temperature, workup, product mass, and yield data.", "evidence_ids": evidence(13)},
                {"region": "right column, general procedure and Z-5c through (S)-Z-5e", "finding": "Shared Grignard/ZnBr2/Ni procedure applied only to the explicitly listed Z-5c-j preparations; four Table 7 records on this page enriched individually.", "evidence_ids": evidence(13)},
                {"region": "right column bottom, start of Z-5f", "finding": "Z-5f heading begins here and its experimental sentence continues on page 14; represented once under Table 7 entry 7 with both pages as evidence.", "evidence_ids": evidence(13)},
            ],
            "record_ids": page13_ids,
            "unresolved": [
                "The page-6 equation labels the oxidation substrate Z-4e, while the detailed page-13 procedure explicitly uses Z-4d; the conflict is preserved.",
                "The chiral (S)-Z-6e paragraph does not repeat solvent, temperature, time, workup, or purification; these fields remain missing rather than being inherited.",
                "Yield measurement bases are not explicitly named.",
            ],
        },
        {
            "page": 14,
            "state": "attempted",
            "regions": [
                {"region": "left column top, completion of Z-5f and (S)-Z-5f", "finding": "Completion of Table 7 entry 7 and the distinct chiral entry 8, including exact quantities, product masses, yields, and 95.8% ee for (S)-Z-5f.", "evidence_ids": evidence(14)},
                {"region": "left column middle, Z-5g and (R)-Z-5g", "finding": "Two p-dimethylaminophenyl organozinc/Ni couplings corresponding to Table 7 entries 9-10 enriched separately; the chiral product is reported at 94.0% ee.", "evidence_ids": evidence(14)},
                {"region": "left lower and right columns, carbon-sulfonyl couplings Z-5h-j", "finding": "Six independent Table 8 C-SO2Ph coupling procedures enriched with row-specific scale, Grignard concentration/volume, catalyst loading, DMF volume, product mass, yield, and ee where reported.", "evidence_ids": evidence(14)},
                {"region": "right column bottom, acknowledgment and article identifier", "finding": "Acknowledgment and JA034039Q identifier only; no additional experiment or reaction arrow.", "evidence_ids": evidence(14)},
            ],
            "record_ids": page14_ids,
            "unresolved": [
                "Yield measurement bases are not explicitly named.",
                "The shared general procedure states a 12-24 h range, while exact row times are retained from Table 7/8 evidence on page 6.",
                "Molecular structures and stereochemical assignments remain machine-unverified.",
            ],
        },
    ],
}


def main():
    ids = [r["record_id"] for r in records]
    if len(ids) != len(set(ids)):
        raise RuntimeError("duplicate record IDs in raw extraction")
    OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
    COVERAGE.parent.mkdir(parents=True, exist_ok=True)
    COVERAGE.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")
    tasks = json.loads(TASKS.read_text())
    for task in tasks:
        if task.get("document_id") != DOC:
            continue
        if task.get("evidence_id") in {f"{DOC}:page13:text", f"{DOC}:page14:text"}:
            task["state"] = "attempted"
            task["reason"] = "Original page image inspected; page regions and linked records are documented in coverage/pages_0013_0014.json."
    TASKS.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({
        "records": len(records),
        "new_records": sum(r["source_reaction_id"] not in existing for r in records),
        "updated_records": sum(r["source_reaction_id"] in existing for r in records),
        "coverage_pages": len(coverage["pages"]),
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
