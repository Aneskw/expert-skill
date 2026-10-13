#!/usr/bin/env python3
"""Build source-linked machine records for PDF pages 1--6."""

import json
from pathlib import Path


DOC = "doc_5faf153e5f1a022a"
OUT = Path(__file__).with_name("records_pages_0001_0006.json")


def ev(page):
    return [f"{DOC}:page{page}:image", f"{DOC}:page{page}:text"]


def fact(value, evidence):
    return {
        "value": value,
        "evidence_ids": list(evidence) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def q(number, unit, **extra):
    value = {"number": number, "unit": unit}
    value.update(extra)
    return value


def rng(low, high, unit, raw_text):
    return {"minimum": low, "maximum": high, "unit": unit, "raw_text": raw_text}


def fld(name, value, evidence, targets=None):
    value = {"name": name, "fact": fact(value, evidence)}
    if targets:
        value["target_entity_ids"] = list(targets)
    return value


def amounts(evidence, mass=None, mass_unit="mg", mmol=None, equiv=None,
            molpct=None, volume=None, volume_unit="mL", extra=None):
    fields = []
    if mass is not None:
        fields.append(fld("mass", q(mass, mass_unit), evidence))
    if mmol is not None:
        fields.append(fld("amount", q(mmol, "mmol"), evidence))
    if equiv is not None:
        fields.append(fld("equivalents", q(equiv, "equiv"), evidence))
    if molpct is not None:
        fields.append(fld("catalyst_loading", q(molpct, "mol%"), evidence))
    if volume is not None:
        fields.append(fld("volume", q(volume, volume_unit), evidence))
    fields.extend(extra or [])
    return fields


def part(entity_id, role, label, evidence, name=None, smiles=None, amts=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence) if name else fact(None, []),
        "smiles": fact(smiles, evidence) if smiles else fact(None, []),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": amts or [],
    }


def record(suffix, kind, evidence, participants, steps, outcomes, notes=None,
           unresolved=None):
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
        "notes": [fact(n, evidence) for n in (notes or [])],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved or [],
        },
    }


ALLENE = {
    "1a": ("4-phenyl-1,2-butadiene", "C=C=CCc1ccccc1"),
    "1b": ("1,2-heptadiene (R = n-C4H9)", "C=C=CCCCC"),
    "1c": ("1,2-octadiene (R = n-C5H11)", "C=C=CCCCCC"),
    "1d": ("1,2-decadiene (R = n-C7H15)", "C=C=CCCCCCCC"),
    "1e": ("1,2-undecadiene (R = n-C8H17)", "C=C=CCCCCCCCC"),
    "1f": ("cyclohexyl-substituted allene", "C=C=CC1CCCCC1"),
}


def pf(n):
    return "C(F)(F)" * (n - 1) + "C(F)(F)F"


RFI = {
    "2a": ("n-C4F9I", "IC(F)(F)" + pf(3)),
    "2b": ("n-C6F13I", "IC(F)(F)" + pf(5)),
    "2c": ("Cl(CF2)4I", "IC(F)(F)C(F)(F)C(F)(F)C(F)(F)Cl"),
}

LEFT = {
    "1a": "c1ccccc1CC=",
    "1b": "CCCCC=",
    "1c": "CCCCCC=",
    "1d": "CCCCCCCC=",
    "1e": "CCCCCCCCC=",
    "1f": "C1CCCCC1C=",
}
R_FRAGMENT = {
    "1a": "Cc1ccccc1",
    "1b": "CCCC",
    "1c": "CCCCC",
    "1d": "CCCCCCC",
    "1e": "CCCCCCCC",
    "1f": "C1CCCCC1",
}
RF_INFO = {"2a": (4, "F"), "2b": (6, "F"), "2c": (4, "Cl")}


def rf_product_fragment(rfi):
    n, terminus = RF_INFO[rfi]
    if terminus == "F":
        return pf(n)
    return "C(F)(F)" * (n - 1) + "C(F)(F)Cl"


def product3_smiles(allene, rfi):
    return LEFT[allene] + "C(I)C" + rf_product_fragment(rfi)


def product5_smiles(allene, rfi, alcohol):
    head = "OCC#CC" if alcohol == "4a" else "CC(O)(C)C#CC"
    return head + "(=C" + R_FRAGMENT[allene] + ")C" + rf_product_fragment(rfi)


COMMON = {
    "dithionite": ("sodium dithionite", "[Na+].[Na+].[O-]S(=O)S(=O)[O-]"),
    "bicarbonate": ("sodium bicarbonate", "[Na+].[O-]C(=O)O"),
    "dioxane": ("1,4-dioxane", "O1CCOCC1"),
    "water": ("water", "O"),
    "4a": ("propargyl alcohol", "C#CCO"),
    "4b": ("2-methyl-3-butyn-2-ol", "CC(O)(C)C#C"),
    "et2nh": ("diethylamine", "CCNCC"),
    "mecn": ("acetonitrile", "CC#N"),
}


TABLE1 = [
    (1, "1a", "2a", "3a", 64, "36:64", 1),
    (2, "1a", "2b", "3b", 55, "37:63", 1),
    (3, "1b", "2a", "3c", 52, "33:67", 2),
    (4, "1c", "2a", "3d", 50, "30:70", 2),
    (5, "1c", "2b", "3e", 55, "30:70", 2),
    (6, "1d", "2c", "3f", 60, "27:73", 3),
    (7, "1d", "2a", "3g", 66, "30:70", 3),
    (8, "1d", "2b", "3h", 61, "28:72", 3),
    (9, "1e", "2a", "3i", 52, "28:72", 2),
    (10, "1f", "2a", "3j", 61, "31:69", 1),
    (11, "1f", "2b", "3k", 63, "30:70", 1),
]


records = []

for entry, a, rfi, prod, main_yield, ez, minor_yield in TABLE1:
    evidence = ev(2)
    p_main = f"main_{prod}"
    p_minor = f"minor_{prod}_prime"
    participants = [
        part(a, "reactant", a, evidence, *ALLENE[a], amts=amounts(evidence, equiv=1)),
        part(rfi, "reactant", rfi, evidence, *RFI[rfi], amts=amounts(evidence, equiv=1.5)),
        part("na2s2o4", "reagent", "Na2S2O4", evidence, COMMON["dithionite"][0], COMMON["dithionite"][1], amounts(evidence, equiv=1.5)),
        part("nahco3", "reagent", "NaHCO3", evidence, COMMON["bicarbonate"][0], COMMON["bicarbonate"][1], amounts(evidence, equiv=1.5)),
        part("dioxane", "solvent", "1,4-dioxane", evidence, *COMMON["dioxane"]),
        part("water", "solvent", "H2O", evidence, *COMMON["water"]),
        part(p_main, "product", prod, evidence, f"2-iodo-1-perfluoroalkyl-2-alkene {prod} (E/Z mixture)", product3_smiles(a, rfi)),
        part(p_minor, "product", f"{prod}'", evidence, f"regioisomer {prod}'", None),
    ]
    steps = [{
        "step_id": "radical_addition",
        "participant_ids": [p["entity_id"] for p in participants],
        "conditions": [
            fld("reaction_temperature", rng(40, 45, "°C", "40–45 °C"), evidence),
            fld("reaction_time", q(3, "h"), evidence),
            fld("solvent_composition", "1,4-dioxane/H2O = 3:1 (v/v)", evidence),
            fld("atmosphere", None, evidence),
            fld("workup", None, evidence),
            fld("purification", "column chromatography on silica gel; E/Z isomers not separable", evidence),
        ],
    }]
    outcomes = [
        fld("isolated_yield_main_product", q(main_yield, "%"), evidence, [p_main]),
        fld("main_product_E_Z_ratio", ez, evidence, [p_main]),
        fld("selectivity_measurement_basis", "1H NMR (400 MHz)", evidence, [p_main]),
        fld("isolated_yield_regioisomer", q(minor_yield, "%"), evidence, [p_minor]),
        fld("yield_measurement_basis", "isolated yield", evidence, [p_main, p_minor]),
    ]
    records.append(record(
        f"table1_entry{entry}", "substrate_scope_entry", evidence, participants, steps, outcomes,
        notes=["The E and Z isomers of product 3 could not be separated by silica-gel chromatography."],
        unresolved=["Atmosphere and workup are not stated in Table 1.", "Product and regioisomer structures remain unverified."],
    ))


RADICAL_PREPS = [
    # label, allene, rfi, allene mass/unit/mmol, rfi mass/unit/mmol, dithionite mg/mmol,
    # bicarbonate mg/mmol, mixed solvent mL, time h, product mass/unit, yield, E/Z expression
    ("3a", "1a", "2a", 258.8, "mg", 1.99, 1.0482, "g", 3.03, 523.6, 3.01, 253.4, 3.02, None, 9, 612.7, "mg", 65, "36:64"),
    ("3b", "1a", "2b", 262.0, "mg", 2.02, 1.3529, "g", 3.03, 525.0, 3.02, 255.2, 3.04, 16, 4, 651.4, "mg", 56, "37:63"),
    ("3c", "1b", "2a", 95.4, "mg", 0.99, 515.4, "mg", 1.49, 261.4, 1.50, 126.0, 1.50, 8, 3, 238.2, "mg", 54, "33:67"),
    ("3d", "1c", "2a", 111.0, "mg", 1.01, 525.3, "mg", 1.52, 261.6, 1.50, 124.9, 1.49, 8, 3, 237.4, "mg", 52, "30:70"),
    ("3e", "1c", "2b", 223.2, "mg", 2.03, 1.3711, "g", 3.07, 520.5, 2.99, 253.0, 3.01, 8, 3, 643.3, "mg", 57, "30:70"),
    ("3f", "1d", "2c", 68.7, "mg", 0.50, 280.0, "mg", 0.77, 130.4, 0.75, 64.4, 0.77, 4, 3, 156.3, "mg", 63, "27:73"),
    ("3g", "1d", "2a", 70.0, "mg", 0.51, 265.9, "mg", 0.77, 131.1, 0.75, 63.0, 0.75, 4, 3, 169.8, "mg", 69, "30:70"),
    ("3h", "1d", "2b", 415.6, "mg", 3.01, 2.0754, "g", 4.65, 786.7, 4.52, 376.8, 4.49, 12, 2.5, 1.1276, "g", 64, "28:72"),
    ("3i", "1e", "2a", 152.8, "mg", 1.01, 519.0, "mg", 1.50, 262.6, 1.51, 125.7, 1.50, 8, 3, 269.2, "mg", 54, "28:72"),
    ("3j", "1f", "2a", 120.1, "mg", 0.98, 522.2, "mg", 1.51, 262.2, 1.51, 128.1, 1.53, 8, 3, 287.0, "mg", 62, "31:69"),
    ("3k", "1f", "2b", 121.0, "mg", 0.99, 665.4, "mg", 1.49, 260.6, 1.50, 128.1, 1.53, 8, 3, 360.1, "mg", 64, "30:70"),
]

for row in RADICAL_PREPS:
    (prod, a, rfi, amass, aunit, ammol, rimass, riunit, rimmol, dmass, dmmol,
     bmass, bmmol, solvent_total, hours, pmass, punit, yld, ezratio) = row
    pages = [3, 4] if prod == "3a" else [4]
    evidence = sum((ev(p) for p in pages), [])
    prod_id = f"product_{prod}"
    diox_extra = []
    water_extra = []
    if prod == "3a":
        diox_extra = [fld("initial_volume", q(10, "mL"), evidence), fld("additional_volume", q(2, "mL"), evidence)]
        water_extra = [fld("volume", q(4, "mL"), evidence)]
    participants = [
        part(a, "reactant", a, evidence, *ALLENE[a], amounts(evidence, mass=amass, mass_unit=aunit, mmol=ammol)),
        part(rfi, "reactant", rfi, evidence, *RFI[rfi], amounts(evidence, mass=rimass, mass_unit=riunit, mmol=rimmol)),
        part("na2s2o4", "reagent", "Na2S2O4", evidence, COMMON["dithionite"][0], COMMON["dithionite"][1], amounts(evidence, mass=dmass, mmol=dmmol)),
        part("nahco3", "reagent", "NaHCO3", evidence, COMMON["bicarbonate"][0], COMMON["bicarbonate"][1], amounts(evidence, mass=bmass, mmol=bmmol)),
        part("dioxane", "solvent", "1,4-dioxane", evidence, *COMMON["dioxane"], amts=diox_extra),
        part("water", "solvent", "H2O", evidence, *COMMON["water"], amts=water_extra),
        part(prod_id, "product", prod, evidence, f"isolated E/Z mixture of {prod}", product3_smiles(a, rfi)),
    ]
    conditions = [
        fld("reaction_temperature", rng(40, 45, "°C", "40–45 °C") if prod == "3a" else None, evidence),
        fld("reaction_time", q(hours, "h"), evidence),
        fld("mixed_solvent_total_volume", q(solvent_total, "mL") if solvent_total is not None else None, evidence),
        fld("solvent_composition", "1,4-dioxane/H2O = 3:1 (v/v)" if prod != "3a" else None, evidence),
        fld("atmosphere", None, evidence),
        fld("workup", "quenched with brine; extracted with diethyl ether; dried over anhydrous Na2SO4" if prod == "3a" else None, evidence),
        fld("purification", "evaporation and silica-gel column chromatography (petroleum ether)" if prod == "3a" else None, evidence),
    ]
    outcomes = [
        fld("isolated_yield", q(yld, "%"), evidence, [prod_id]),
        fld("product_mass", q(pmass, punit), evidence, [prod_id]),
        fld("product_E_Z_ratio", ezratio, evidence, [prod_id]),
        fld("yield_measurement_basis", "isolated yield", evidence, [prod_id]),
    ]
    unresolved = ["Product stereochemistry and candidate SMILES remain unverified."]
    if prod != "3a":
        unresolved += ["Temperature, atmosphere, workup, and purification are not restated in the abbreviated preparation."]
    else:
        unresolved += ["The paragraph labels 36:64 as Z/E, while its NMR integrals and Table 1 describe 36:64 as E/Z.", "Atmosphere is not stated."]
    records.append(record(
        f"section3_1_prep_{prod}", "reported_experiment", evidence, participants,
        [{"step_id": "preparation", "participant_ids": [p["entity_id"] for p in participants], "conditions": conditions}],
        outcomes,
        notes=["This preparation is retained separately from Table 1 because the reported yield differs; reaction time also differs for 3a, 3b, and 3h."],
        unresolved=unresolved,
    ))


TABLE2 = [
    # entry, allene key, rfi, substrate, alcohol, temp C, min, recovered %, E product %, Z product/marker, ratio scheme
    (1, "1a", "2a", "3a", "4a", 13, 30, 43, 34, 4, 0.6),
    (2, "1a", "2b", "3b", "4a", 0, 100, 42, 26, 2, 0.7),
    (3, "1b", "2a", "3c", "4a", 0, 75, 49, 26, 3, 0.6),
    (4, "1c", "2a", "3d", "4a", 0, 60, 48, 23, 1, 0.6),
    (5, "1c", "2b", "3e", "4a", 0, 120, 57, 29, 2, 0.7),
    (6, "1d", "2c", "3f", "4a", 0, 60, 68, 23, 7, 0.6),
    (7, "1d", "2a", "3g", "4a", 0, 60, 58, 22, 1, 0.6),
    (8, "1d", "2b", "3h", "4a", 0, 150, 73, 19, "table dash (—)", 0.7),
    (9, "1e", "2a", "3i", "4a", 0, 120, 61, 23, 2, 0.6),
    (10, "1f", "2a", "3j", "4a", 0, 60, 61, 24, 2, 0.6),
    (11, "1f", "2b", "3k", "4a", 0, 150, 53, 25, 3, 0.7),
    (12, "1a", "2a", "3a", "4b", 10, 120, 35, 33, 7, 0.7),
    (13, "1d", "2a", "3g", "4b", 11, 80, 30, 29, 4, 0.7),
]

KIN_DETAIL = {
    1: ((118.7, 0.25), (8.5, 0.15), (6.2, 0.00884, 3.5), (1.7, 0.00947, 3.8), (11.1, 0.15), 0.5, (50.9, 33.9, 4.0)),
    2: ((173.6, 0.30), (11.9, 0.21), (7.3, 0.0104, 3.5), (2.0, 0.0105, 3.5), (15.3, 0.21), 0.6, (73.3, 39.7, 3.6)),
    3: ((132.8, 0.30), (10.2, 0.18), (7.4, 0.0106, 3.5), (2.0, 0.0105, 3.5), (13.1, 0.18), 0.6, (65.6, 29.2, 3.3)),
    4: ((114.5, 0.25), (8.3, 0.15), (6.2, 0.00884, 3.5), (1.8, 0.00947, 3.8), (11.1, 0.15), 0.5, (54.8, 21.7, 0.5)),
    5: ((139.7, 0.25), (9.7, 0.173), (6.2, 0.00884, 3.5), (1.8, 0.00947, 3.8), (12.7, 0.174), 0.5, (79.5, 35.3, 2.3)),
    6: ((207.0, 0.41), (14.0, 0.25), (10.1, 0.0144, 3.5), (2.8, 0.0147, 3.6), (18.1, 0.25), 0.8, (140.5, 41.3, 11.5)),
    7: ((125.4, 0.26), (8.7, 0.16), (6.4, 0.00913, 3.5), (1.7, 0.00895, 3.4), (11.6, 0.16), 0.5, (73.0, 23.5, 1.0)),
    8: ((146.4, 0.25), (10.0, 0.179), (6.2, 0.00884, 3.5), (1.8, 0.00947, 3.8), (13.0, 0.178), 0.5, (106.6, 24.1, None)),
    9: ((149.9, 0.30), (10.0, 0.179), (7.5, 0.0107, 3.6), (2.1, 0.0111, 3.7), (13.1, 0.179), 0.6, (90.8, 29.5, 2.3)),
    10: ((111.5, 0.24), (8.2, 0.146), (5.9, 0.00842, 3.5), (1.5, 0.00789, 3.3), (10.6, 0.145), 0.5, (68.4, 22.2, 1.4)),
}

for entry, a, rfi, substrate, alcohol, temp, minutes, recovered, eyield, zyield, alcohol_eq in TABLE2:
    pages = [2]
    if entry <= 4:
        pages.append(5)
    elif entry == 5:
        pages.extend([5, 6])
    elif entry <= 10:
        pages.append(6)
    evidence = sum((ev(p) for p in pages), [])
    input_id = f"input_{substrate}_mixture"
    alcohol_name, alcohol_smiles = COMMON[alcohol]
    rec_id = f"recovered_Z_{substrate}"
    eprod = f"E_5{substrate[-1]}{alcohol[-1]}"
    zprod = f"Z_5{substrate[-1]}{alcohol[-1]}"
    input_amount = amounts(evidence, equiv=1)
    alc_amount = amounts(evidence, equiv=alcohol_eq)
    pd_amount = amounts(evidence, molpct=3.5)
    cui_amount = amounts(evidence, molpct=3.5)
    et_amount = amounts(evidence, equiv=alcohol_eq)
    mecn_amount = []
    product_masses = None
    if entry in KIN_DETAIL:
        inp, alc, pd, cui, et, solv, product_masses = KIN_DETAIL[entry]
        input_amount = amounts(evidence, mass=inp[0], mmol=inp[1], equiv=1)
        alc_amount = amounts(evidence, mass=alc[0], mmol=alc[1], equiv=alcohol_eq)
        pd_amount = amounts(evidence, mass=pd[0], mmol=pd[1], molpct=pd[2])
        cui_amount = amounts(evidence, mass=cui[0], mmol=cui[1], molpct=cui[2])
        et_amount = amounts(evidence, mass=et[0], mmol=et[1], equiv=alcohol_eq)
        mecn_amount = amounts(evidence, volume=solv)
    participants = [
        part(input_id, "reactant", substrate, evidence, f"E/Z mixture of {substrate}", product3_smiles(a, rfi), input_amount),
        part(alcohol, "reactant", alcohol, evidence, alcohol_name, alcohol_smiles, alc_amount),
        part("pd_complex", "catalyst", "Pd(PPh3)2Cl2", evidence, "bis(triphenylphosphine)palladium(II) dichloride", None, pd_amount),
        part("cui", "catalyst", "CuI", evidence, "copper(I) iodide", None, cui_amount),
        part("et2nh", "reagent", "Et2NH", evidence, *COMMON["et2nh"], amts=et_amount),
        part("mecn", "solvent", "CH3CN", evidence, *COMMON["mecn"], amts=mecn_amount),
        part(rec_id, "product", f"Z-{substrate}", evidence, f"recovered Z isomer of {substrate}", product3_smiles(a, rfi)),
        part(eprod, "product", f"E-5{substrate[-1]}{alcohol[-1]}", evidence, "E Sonogashira coupling product", product5_smiles(a, rfi, alcohol)),
        part(zprod, "product", f"Z-5{substrate[-1]}{alcohol[-1]}", evidence, "Z Sonogashira coupling product", product5_smiles(a, rfi, alcohol)),
    ]
    conditions = [
        fld("table_temperature", q(temp, "°C"), ev(2)),
        fld("reaction_time", q(minutes, "min"), ev(2)),
        fld("atmosphere", "nitrogen" if entry == 1 else None, evidence),
        fld("workup", "quenched with brine; extracted with diethyl ether; dried over anhydrous Na2SO4" if entry == 1 else None, evidence),
        fld("purification", "silica-gel column chromatography; petroleum ether for Z-3a and petroleum ether/ethyl acetate 10:1 for 5aa" if entry == 1 else None, evidence),
    ]
    if entry == 1:
        conditions.append(fld("procedure_temperature", "room temperature", ev(5)))
    outcomes = [
        fld("recovered_starting_material_yield", q(recovered, "%"), evidence, [rec_id]),
        fld("isolated_yield_E_product", q(eyield, "%"), evidence, [eprod]),
        fld("isolated_yield_Z_product", q(zyield, "%") if isinstance(zyield, (int, float)) else zyield, evidence, [zprod]),
        fld("yield_measurement_basis", "isolated yield", evidence, [rec_id, eprod, zprod]),
    ]
    if entry == 8:
        outcomes.append(fld("isolated_Z3_Z_E_ratio", "97:3", evidence, [rec_id]))
        outcomes.append(fld("selectivity_measurement_basis", "1H NMR (400 MHz)", evidence, [rec_id]))
    if product_masses:
        rz_mass, e_mass, z_mass = product_masses
        outcomes.extend([
            fld("isolated_Z3_mass", q(rz_mass, "mg"), evidence, [rec_id]),
            fld("E_product_mass", q(e_mass, "mg"), evidence, [eprod]),
            fld("Z_product_mass", q(z_mass, "mg") if z_mass is not None else None, evidence, [zprod]),
        ])
    unresolved = ["All candidate structures and alkene stereochemistry remain unverified."]
    if entry == 1:
        unresolved.append("Table 2 reports 13 °C, while the typical procedure says room temperature; both are retained.")
    else:
        unresolved.append("Atmosphere, workup, and purification are not stated for this row in the covered pages.")
    if entry > 10:
        unresolved.append("No detailed preparation for this row occurs within the covered page range.")
    records.append(record(
        f"table2_entry{entry}", "substrate_scope_entry", evidence, participants,
        [{"step_id": "kinetic_resolution", "participant_ids": [p["entity_id"] for p in participants], "conditions": conditions}],
        outcomes,
        notes=["The E isomer reacts preferentially; the Z iodide is isolated as recovered starting material."],
        unresolved=unresolved,
    ))


TABLE3 = [
    (1, "K2CO3", "CH3CN", 1.2, 60, 24, 3, 12, 4, 1.2),
    (2, "Et2NH", "CH3CN", 1.2, 60, 47.5, 3, 26, 13, 1.2),
    (3, "Et2NH", "CH3CN", 2.0, 60, 11, 3, 29, 14, 2.0),
    (4, "Et3N", None, 1.2, 60, 28, 3, 23, 15, None),
    (5, "hexahydropyridine", None, 1.2, 60, 9.5, 3, 48, 16, None),
    (6, "(i-Pr)2NH", None, 1.2, 60, 10, 3, 48, 20, None),
    (7, "Et2NH", None, 1.2, 60, 10, 5, 49, 19, None),
    (8, "Et2NH", None, 1.2, 60, 10.5, 3, 51, 18, None),
    (9, "Et2NH", None, 1.2, 60, 22, 1, 46, 19, None),
    (10, "Et2NH", None, 1.2, 40, 11.5, 3, 53, 21, None),
    (11, "Et2NH", None, 1.2, 40, 17.5, 1, 46, 23, None),
    (12, "Et2NH", None, 1.2, 20, 10, 3, 45, 16, None),
]
BASE_SMILES = {
    "K2CO3": "[K+].[K+].[O-]C([O-])=O",
    "Et2NH": "CCNCC",
    "Et3N": "CCN(CC)CC",
    "hexahydropyridine": "N1CCCCC1",
    "(i-Pr)2NH": "CC(C)NC(C)C",
}

for entry, base, solvent, alc_eq, temp, hours, cat, zy, ey, base_eq in TABLE3:
    evidence = ev(3)
    base_role = "reagent" if solvent == "CH3CN" else "solvent"
    participants = [
        part("input_3g", "reactant", "3g", evidence, "E/Z mixture of 3g", product3_smiles("1d", "2a"), amounts(evidence, equiv=1)),
        part("4a", "reactant", "4a", evidence, *COMMON["4a"], amts=amounts(evidence, equiv=alc_eq)),
        part("pd_complex", "catalyst", "Pd(PPh3)2Cl2", evidence, "bis(triphenylphosphine)palladium(II) dichloride", None, amounts(evidence, molpct=cat)),
        part("cui", "catalyst", "CuI", evidence, "copper(I) iodide", None, amounts(evidence, molpct=cat)),
        part("base", base_role, base, evidence, base, BASE_SMILES[base], amounts(evidence, equiv=base_eq) if base_eq is not None else []),
        part("Z_5ga", "product", "Z-5ga", evidence, "Z coupling product 5ga", product5_smiles("1d", "2a", "4a")),
        part("E_5ga", "product", "E-5ga", evidence, "E coupling product 5ga", product5_smiles("1d", "2a", "4a")),
    ]
    if solvent == "CH3CN":
        participants.insert(5, part("mecn", "solvent", "CH3CN", evidence, *COMMON["mecn"]))
    steps = [{
        "step_id": "complete_sonogashira_optimization",
        "participant_ids": [p["entity_id"] for p in participants],
        "conditions": [
            fld("reaction_temperature", q(temp, "°C"), evidence),
            fld("reaction_time", q(hours, "h"), evidence),
            fld("atmosphere", None, evidence),
            fld("workup", None, evidence),
            fld("purification", None, evidence),
        ],
    }]
    outcomes = [
        fld("isolated_yield_Z_product", q(zy, "%"), evidence, ["Z_5ga"]),
        fld("isolated_yield_E_product", q(ey, "%"), evidence, ["E_5ga"]),
        fld("yield_measurement_basis", "isolated yield", evidence, ["Z_5ga", "E_5ga"]),
    ]
    records.append(record(
        f"table3_entry{entry}", "optimization_entry", evidence, participants, steps, outcomes,
        unresolved=["Atmosphere, workup, and purification are not stated in Table 3.", "Candidate product structure and stereochemistry remain unverified."],
    ))


TABLE4 = [
    (1, "1a", "2a", "3a", "4a", 44, 20, 40),
    (2, "1a", "2b", "3b", "4a", 40, 21, 40),
    (3, "1b", "2a", "3c", "4a", 57, 24, 40),
    (4, "1c", "2a", "3d", "4a", 58, 24, 40),
    (5, "1c", "2b", "3e", "4a", 55, 24, 40),
    (6, "1d", "2a", "3g", "4a", 53, 21, 40),
    (7, "1d", "2b", "3h", "4a", 51, 34, 40),
    (8, "1e", "2a", "3i", "4a", 54, 24, 40),
    (9, "1f", "2a", "3j", "4a", 68, 25, 40),
    (10, "1f", "2b", "3k", "4a", 60, 26, 40),
    (11, "1a", "2a", "3a", "4b", 53, 27, 40),
    (12, "1d", "2a", "3g", "4b", 58, 24, 40),
    (13, "1e", "2a", "3i", "4b", 58, 19, 40),
    (14, "1f", "2a", "3j", "4b", 59, 28, 60),
]

for entry, a, rfi, substrate, alcohol, zy, ey, temp in TABLE4:
    evidence = ev(3)
    suffix = f"5{substrate[-1]}{alcohol[-1]}"
    participants = [
        part("input_3", "reactant", substrate, evidence, f"E/Z mixture of {substrate}", product3_smiles(a, rfi), amounts(evidence, equiv=1)),
        part(alcohol, "reactant", alcohol, evidence, *COMMON[alcohol], amts=amounts(evidence, equiv=1.2)),
        part("pd_complex", "catalyst", "Pd(PPh3)2Cl2", evidence, "bis(triphenylphosphine)palladium(II) dichloride", None, amounts(evidence, molpct=3)),
        part("cui", "catalyst", "CuI", evidence, "copper(I) iodide", None, amounts(evidence, molpct=3)),
        part("et2nh", "solvent", "Et2NH", evidence, *COMMON["et2nh"]),
        part("Z_product", "product", f"Z-{suffix}", evidence, "Z Sonogashira coupling product", product5_smiles(a, rfi, alcohol)),
        part("E_product", "product", f"E-{suffix}", evidence, "E Sonogashira coupling product", product5_smiles(a, rfi, alcohol)),
    ]
    steps = [{
        "step_id": "complete_sonogashira_coupling",
        "participant_ids": [p["entity_id"] for p in participants],
        "conditions": [
            fld("reaction_temperature", q(temp, "°C"), evidence),
            fld("reaction_time", None, evidence),
            fld("atmosphere", None, evidence),
            fld("workup", None, evidence),
            fld("purification", None, evidence),
        ],
    }]
    outcomes = [
        fld("isolated_yield_Z_product", q(zy, "%"), evidence, ["Z_product"]),
        fld("isolated_yield_E_product", q(ey, "%"), evidence, ["E_product"]),
        fld("yield_measurement_basis", "isolated yield", evidence, ["Z_product", "E_product"]),
    ]
    records.append(record(
        f"table4_entry{entry}", "substrate_scope_entry", evidence, participants, steps, outcomes,
        unresolved=["Reaction time, atmosphere, workup, and purification are not stated in Table 4.", "Candidate product structure and stereochemistry remain unverified."],
    ))


assert len(records) == 61, len(records)
OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
print(f"wrote {len(records)} records to {OUT}")
