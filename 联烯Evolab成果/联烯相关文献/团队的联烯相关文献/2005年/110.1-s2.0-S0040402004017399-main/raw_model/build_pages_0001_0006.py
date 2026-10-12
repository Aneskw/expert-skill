#!/usr/bin/env python3
"""Build the page-1--6 machine extraction payload without changing extraction tools."""
import json
from pathlib import Path

DOC = "doc_28bbeb684eb62f95"
OUT = Path(__file__).with_name("pages_0001_0006_records.json")


def ev(page):
    return [f"{DOC}:page{page}:text", f"{DOC}:page{page}:image"]


def fact(value, evidence):
    return {
        "value": value,
        "evidence_ids": list(evidence) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def field(name, value, evidence, targets=None):
    item = {"name": name, "fact": fact(value, evidence)}
    if targets:
        item["target_entity_ids"] = targets
    return item


def participant(entity_id, role, label, evidence, name=None, smiles=None, amounts=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence) if name else fact(None, []),
        "smiles": fact(smiles, evidence) if smiles else fact(None, []),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": amounts or [],
    }


def record(rid, source_id, kind, evidence, participants, steps, outcomes, notes=None, unresolved=None):
    return {
        "record_id": f"{DOC}:{rid}",
        "document_id": DOC,
        "source_reaction_id": source_id,
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
            "unresolved": unresolved or [
                "No supporting information was explicitly provided or associated; unreported details remain missing.",
                "Machine-extracted structures and roles require independent source review.",
            ],
        },
    }


SMILES = {
    "2a": "O=C(NCc1ccccc1)C(C)=C=CCCCCCC",
    "2b": "NC(=O)C=C=CCCCCCCC",
    "2c": "O=C(NCc1ccccc1)C=C=CCCCCCCC",
    "2d": "CCCCNC(=O)C(C)=C=Cc1ccccc1",
    "2e": "CC(C)=C=CC(=O)NCc1ccccc1",
    "2f": "CCCCNC(=O)C=C=C(C)C",
    "2g": "O=C(NCc1ccccc1)C=C=C(C)c1ccccc1",
    "2h": "C=C=C(C)C(=O)NCc1ccccc1",
    "2i": "CC(C)=C=C(Cc1ccccc1)C(=O)NCc1ccccc1",
    "2j": "CC(C)=C=C(C)C(=O)NCc1ccccc1",
    "4a": "CCCCCCC1(O)N(Cc2ccccc2)C(=O)C(C)=C1Br",
    "4b": "CCCCCCC1(O)N(Cc2ccccc2)C(=O)C(C)=C1Cl",
    "4c": "CCCCCCCC1(O)NC(=O)C=C1Br",
    "4d": "CCCCCCCC1(O)N(Cc2ccccc2)C(=O)C=C1Br",
    "4e": "CCCCCCCC1(O)N(Cc2ccccc2)C(=O)C=C1Cl",
    "4f": "CCCCN1C(=O)C(C)=C(Br)C1(O)c1ccccc1",
    "4g": "CCCCN1C(=O)C(C)=C(Cl)C1(O)c1ccccc1",
    "4h": "CC1=C(Br)C(O)N(Cc2ccccc2)C1=O",
    "4i": "CC1=C(Cl)C(O)N(Cc2ccccc2)C1=O",
    "4j": "CCCCCCCC1(O)N(Cc2ccccc2)C(=O)C=C1I",
    "4k": "CC1=C(I)C(O)N(Cc2ccccc2)C1=O",
    "5a": "CC1(C)OC(=NCc2ccccc2)C=C1Br",
    "5b": "CC1(C)OC(=NCc2ccccc2)C=C1Cl",
    "5c": "CC1(c2ccccc2)OC(=NCc2ccccc2)C=C1Br",
    "5d": "CC1(c2ccccc2)OC(=NCc2ccccc2)C=C1Cl",
    "5e": "CC1(C)OC(=NCc2ccccc2)C(Cc2ccccc2)=C1Br",
    "5f": "CC1(C)OC(=NCc2ccccc2)C(Cc2ccccc2)=C1Cl",
    "5g": "CC1(C)OC(=NCCCC)C=C1Br",
    "5h": "CC1(C)OC(=NCCCC)C=C1Cl",
    "5i": "CC1(C)OC(=NCc2ccccc2)C(C)=C1Br",
    "5j": "CC1(C)OC(=NCc2ccccc2)C(C)=C1Cl",
    "5k": "CC1(C)OC(=NCc2ccccc2)C=C1I",
    "5l": "CC1(c2ccccc2)OC(=NCc2ccccc2)C=C1I",
    "5m": "CC1(C)OC(=NCc2ccccc2)C(Cc2ccccc2)=C1I",
    "5n": "CC1(C)OC(=NCc2ccccc2)C(C)=C1I",
}

COMMON = {
    "BnNH2": ("benzylamine", "NCC1=CC=CC=C1"),
    "n-BuNH2": ("n-butylamine", "CCCCN"),
    "Et3N": ("triethylamine", "CCN(CC)CC"),
    "CO": ("carbon monoxide", "[C-]#[O+]"),
    "THF": ("tetrahydrofuran", "C1CCOC1"),
    "H2O": ("water", "O"),
    "EtOH": ("ethanol", "CCO"),
    "acetone": ("acetone", "CC(C)=O"),
    "CuBr2": ("copper(II) bromide", "[Br-].[Br-].[Cu+2]"),
    "CuCl2": ("copper(II) chloride", "[Cl-].[Cl-].[Cu+2]"),
    "CuCl2·2H2O": ("copper(II) chloride dihydrate", None),
    "I2": ("iodine", "II"),
    "DCC": ("dicyclohexylcarbodiimide", "C1CCC(CC1)N=C=NC2CCCCC2"),
    "DMAP": ("4-dimethylaminopyridine", "CN(C)c1ccncc1"),
    "SOCl2": ("thionyl chloride", "O=S(Cl)Cl"),
    "n-BuLi": ("n-butyllithium", None),
    "TsCl": ("p-toluenesulfonyl chloride", "Cc1ccc(S(=O)(=O)Cl)cc1"),
    "Pd(PPh3)4": ("tetrakis(triphenylphosphine)palladium(0)", None),
    "PhB(OH)2": ("phenylboronic acid", "OB(O)c1ccccc1"),
    "Na2CO3": ("sodium carbonate", "[Na+].[Na+].[O-]C([O-])=O"),
}


def common(entity_id, role, label, evidence, amounts=None):
    name, smiles = COMMON[label]
    return participant(entity_id, role, label, evidence, name, smiles, amounts)


records = []


def add_starting_material(label, evidence, precursors, conditions, yld, details=None, notes=None, unresolved=None):
    product = participant(f"product_{label}", "product", label, evidence,
                          details.get("name") if details else None, SMILES[label],
                          details.get("product_amounts", []) if details else [])
    parts = precursors + [product]
    records.append(record(
        f"starting_material_{label}", f"Scheme starting-material synthesis {label}",
        "reported_experiment", evidence, parts,
        [{"step_id": "reaction", "participant_ids": [p["entity_id"] for p in parts if p["role"] != "product"],
          "conditions": conditions}],
        [field("isolated_yield", {"number": yld, "unit": "%"}, evidence, [f"product_{label}"]),
         field("yield_measurement_basis", "isolated", evidence, [f"product_{label}"])],
        notes=notes,
        unresolved=unresolved,
    ))


# Starting-material syntheses 2a-c: Scheme 2 plus the page-4 experimental procedures.
for label, substrate, sub_amounts, amine, amine_amounts, thf_vol, time_h, yld, product_mass, name, pages in [
    ("2a", "3-bromo-2-decyne", [("mass", 1.09, "g"), ("amount", 5.0, "mmol")], "BnNH2", [("volume", 0.6, "mL"), ("amount", 5.5, "mmol")], 20, 1, 83, 1.12, "N-benzyl 2-methyl-2,3-decadienamide", [1, 4]),
    ("2b", "3-bromo-1-decyne", [("mass", 1.02, "g"), ("amount", 4.7, "mmol")], "NH3·H2O", [("volume", 0.4, "mL"), ("amount", 5.2, "mmol")], 25, 2, 68, 0.58, "2,3-undecadienamide", [1, 4]),
    ("2c", "3-bromo-1-decyne", [("mass", 1.09, "g"), ("amount", 5.0, "mmol")], "BnNH2", [("volume", 0.6, "mL"), ("amount", 5.5, "mmol")], 20, 1.5, 68, 0.92, "N-benzyl 2,3-undecadienamide", [1, 4, 5]),
]:
    evidence = sum((ev(p) for p in pages), [])
    prec = [participant("substrate", "reactant", substrate, evidence,
                        amounts=[field(n, {"number": v, "unit": u}, evidence) for n, v, u in sub_amounts])]
    if amine == "NH3·H2O":
        prec.append(participant("amine", "reactant", amine, evidence, "aqueous ammonia",
                                amounts=[field(n, {"number": v, "unit": u}, evidence) for n, v, u in amine_amounts]))
    else:
        prec.append(common("amine", "reactant", amine, evidence,
                           [field(n, {"number": v, "unit": u}, evidence) for n, v, u in amine_amounts]))
    prec += [common("Et3N", "reagent", "Et3N", evidence,
                    [field("volume", {"number": 0.72 if label == "2b" else 0.77, "unit": "mL"}, evidence),
                     field("amount", {"number": 5.2 if label == "2b" else 5.5, "unit": "mmol"}, evidence)]),
             common("Pd", "catalyst", "Pd(PPh3)4", evidence,
                    [field("mass", {"number": 54 if label == "2b" else 64, "unit": "mg"}, evidence),
                     field("amount", {"number": 0.047 if label == "2b" else 0.05, "unit": "mmol"}, evidence)]),
             common("CO", "reagent", "CO", evidence),
             common("THF", "solvent", "THF", evidence, [field("volume", {"number": thf_vol, "unit": "mL"}, evidence)])]
    add_starting_material(label, evidence, prec,
                          [field("temperature", "r.t.", evidence), field("time", {"number": time_h, "unit": "h"}, evidence),
                           field("pressure", "18 atm", evidence)],
                          yld, {"name": name, "product_amounts": [field("mass", {"number": product_mass, "unit": "g"}, evidence)]},
                          notes=["Typical procedure A; aqueous quench, CH2Cl2 extraction, 1 N HCl/brine washes, silica-gel chromatography."],
                          unresolved=["No explicitly associated SI; spectroscopic characterization is present but not transcribed as reaction conditions.",
                                      "Candidate SMILES was generated from the printed product name/drawing and remains unverified."])

# 2d detailed multistage synthesis (Scheme 2/page 1 and section 3.1.5/page 5).
e = ev(1) + ev(5)
parts = [
    participant("alcohol", "reactant", "1-phenyl-2-butyn-1-ol", e, smiles="CC#CC(O)c1ccccc1",
                amounts=[field("mass", {"number": 580, "unit": "mg"}, e), field("amount", {"number": 4.0, "unit": "mmol"}, e)]),
    common("nBuLi", "reagent", "n-BuLi", e, [field("volume", {"number": 2.5, "unit": "mL"}, e), field("concentration", {"number": 1.6, "unit": "M"}, e), field("amount", {"number": 4.0, "unit": "mmol"}, e)]),
    common("TsCl", "reagent", "TsCl", e, [field("mass", {"number": 762, "unit": "mg"}, e), field("amount", {"number": 4.0, "unit": "mmol"}, e)]),
    common("amine", "reactant", "n-BuNH2", e, [field("volume", {"number": 0.35, "unit": "mL"}, e), field("amount", {"number": 4.0, "unit": "mmol"}, e)]),
    common("Et3N", "reagent", "Et3N", e, [field("volume", {"number": 0.56, "unit": "mL"}, e), field("amount", {"number": 4.0, "unit": "mmol"}, e)]),
    common("Pd", "catalyst", "Pd(PPh3)4", e, [field("mass", {"number": 46, "unit": "mg"}, e), field("amount", {"number": 0.04, "unit": "mmol"}, e)]),
    common("CO", "reagent", "CO", e), common("THF", "solvent", "THF", e, [field("volume", {"number": 40, "unit": "mL"}, e)]),
    participant("product_2d", "product", "2d", e, "N-butyl 2-methyl-4-phenyl-2,3-butadienamide", SMILES["2d"], [field("mass", {"number": 0.59, "unit": "g"}, e)]),
]
records.append(record("starting_material_2d", "Scheme 2 / section 3.1.5", "reported_experiment", e, parts, [
    {"step_id": "deprotonation", "participant_ids": ["alcohol", "nBuLi", "THF"], "conditions": [field("temperature", {"number": -60, "unit": "°C"}, e), field("time", {"number": 30, "unit": "min"}, e)]},
    {"step_id": "tosylation", "participant_ids": ["TsCl"], "conditions": [field("temperature", {"number": -60, "unit": "°C"}, e), field("time_at_minus_60_C", {"number": 15, "unit": "min"}, e), field("time_at_room_temperature", {"number": 2, "unit": "h"}, e)]},
    {"step_id": "carbonylation", "participant_ids": ["amine", "Et3N", "Pd", "CO"], "conditions": [field("addition_temperature", {"number": -78, "unit": "°C"}, e), field("temperature", "r.t.", e), field("time", {"number": 1, "unit": "h"}, e), field("pressure", "25 atm", e)]},
], [field("isolated_yield", {"number": 65, "unit": "%"}, e, ["product_2d"]), field("yield_measurement_basis", "isolated", e, ["product_2d"])],
notes=["Aqueous quench, CH2Cl2 extraction, 1 N HCl/brine washes, and silica-gel chromatography."],
unresolved=["Candidate structures are unverified; the in-situ tosylate intermediate is not separately encoded.", "No explicitly associated SI."]))

# Scheme-only starting materials 2e/2f and page-5 detailed 2g.
for label, amine, yld, name in [("2e", "BnNH2", 85, None), ("2f", "n-BuNH2", 84, None)]:
    e = ev(1)
    prec = [participant("allenyl_bromide", "reactant", f"1,2-allenylic bromide precursor for {label}", e),
            common("amine", "reactant", amine, e), common("Pd", "catalyst", "Pd(PPh3)4", e),
            common("CO", "reagent", "CO", e), common("Et3N", "reagent", "Et3N", e)]
    add_starting_material(label, e, prec, [], yld, {"name": name},
                          notes=["Scheme 2 reports the carbonylation product and yield; exact quantities, temperature, and time are not printed in the inspected region."],
                          unresolved=["Exact experimental quantities, time, temperature, workup, and purification are missing on pages 1-6.",
                                      "Candidate SMILES is based on the fully drawn Scheme 2 structure and remains unverified.",
                                      "No explicitly associated SI."])

e = ev(1) + ev(5)
prec = [participant("allenyl_bromide", "reactant", "1-bromo-3-phenyl-1,2-butadiene", e,
                    amounts=[field("mass", {"number": 0.87, "unit": "g"}, e), field("amount", {"number": 4.1, "unit": "mmol"}, e)]),
        common("amine", "reactant", "BnNH2", e, [field("volume", {"number": 0.5, "unit": "mL"}, e), field("amount", {"number": 4.5, "unit": "mmol"}, e)]),
        common("Et3N", "reagent", "Et3N", e, [field("volume", {"number": 0.65, "unit": "mL"}, e), field("amount", {"number": 4.5, "unit": "mmol"}, e)]),
        common("Pd", "catalyst", "Pd(PPh3)4", e, [field("mass", {"number": 49, "unit": "mg"}, e), field("amount", {"number": 0.04, "unit": "mmol"}, e)]),
        common("CO", "reagent", "CO", e), common("THF", "solvent", "THF", e, [field("volume", {"number": 25, "unit": "mL"}, e)])]
add_starting_material("2g", e, prec, [field("temperature", "r.t.", e), field("time", {"number": 1.5, "unit": "h"}, e)], 71,
                      {"name": "N-benzyl 4-phenyl-2,3-pentadienamide", "product_amounts": [field("mass", {"number": 0.77, "unit": "g"}, e)]},
                      unresolved=["CO pressure and workup/purification are not stated in section 3.1.4 on page 5.", "Candidate structures remain unverified.", "No explicitly associated SI."])

# 2h: Scheme 3 and section 3.1.6.
e = ev(2) + ev(5)
parts = [participant("acid", "reactant", "2-methylbuta-2,3-dienoic acid", e, smiles="C=C=C(C)C(=O)O",
                     amounts=[field("mass", {"number": 922, "unit": "mg"}, e), field("amount", {"number": 9.4, "unit": "mmol"}, e)]),
         common("SOCl2", "reagent", "SOCl2", e, [field("volume", {"number": 1.4, "unit": "mL"}, e), field("amount", {"number": 18.8, "unit": "mmol"}, e)]),
         common("amine", "reactant", "BnNH2", e, [field("volume", {"number": 1.1, "unit": "mL"}, e), field("amount", {"number": 10.3, "unit": "mmol"}, e)]),
         common("Et3N", "reagent", "Et3N", e, [field("volume", {"number": 1.4, "unit": "mL"}, e), field("amount", {"number": 10.3, "unit": "mmol"}, e)]),
         participant("ether", "solvent", "dry ether", e, "diethyl ether", "CCOCC", [field("volume_per_stage", {"number": 30, "unit": "mL"}, e)]),
         participant("product_2h", "product", "2h", e, "N-benzyl 2-methyl-2,3-butadienamide", SMILES["2h"], [field("mass", {"number": 655, "unit": "mg"}, e)])]
records.append(record("starting_material_2h", "Scheme 3 / section 3.1.6", "reported_experiment", e, parts, [
    {"step_id": "acid_chloride_formation", "participant_ids": ["acid", "SOCl2"], "conditions": [field("temperature", "r.t.", e), field("time", {"number": 30, "unit": "min"}, e)]},
    {"step_id": "amidation", "participant_ids": ["amine", "Et3N", "ether"], "conditions": [field("temperature", "r.t.", e), field("time", "overnight", e)]},
], [field("isolated_yield", {"number": 38, "unit": "%"}, e, ["product_2h"]), field("yield_measurement_basis", "isolated", e, ["product_2h"])],
notes=["Water quench, ether extraction, MgSO4 drying, evaporation, and silica-gel chromatography."],
unresolved=["The exact isolated acid-chloride amount is not reported.", "Candidate structures remain unverified.", "No explicitly associated SI."]))

# Scheme 4 amidations to 2i and 2j.
for label, acid_smiles, yld in [("2i", "CC(C)=C=C(Cc1ccccc1)C(=O)O", 55), ("2j", "CC(C)=C=C(C)C(=O)O", 45)]:
    e = ev(2)
    prec = [participant("acid", "reactant", f"allenoic acid precursor 1 for {label}", e, smiles=acid_smiles),
            common("amine", "reactant", "BnNH2", e), common("DCC", "reagent", "DCC", e), common("DMAP", "catalyst", "DMAP", e)]
    add_starting_material(label, e, prec, [], yld, {},
                          notes=["Scheme 4 reports DMAP-catalyzed DCC amidation; exact quantities, solvent, time, and temperature are not shown."],
                          unresolved=["Exact quantities, solvent, time, temperature, workup, and purification are missing on pages 1-6.", "Candidate structures remain unverified.", "No explicitly associated SI."])


def add_cyclization(rid, source_id, kind, pages, substrate_label, product_label, reagent_label,
                    equiv, solvent_parts, temperature, time_h, yld, ratio=None,
                    exact=None, notes=None, unresolved=None):
    evidence = sum((ev(p) for p in pages), [])
    exact = exact or {}
    substrate_amounts = []
    if exact.get("substrate_mass") is not None:
        substrate_amounts.append(field("mass", {"number": exact["substrate_mass"], "unit": "mg"}, evidence))
    if exact.get("substrate_mmol") is not None:
        substrate_amounts.append(field("amount", {"number": exact["substrate_mmol"], "unit": "mmol"}, evidence))
    substrate = participant("substrate", "reactant", substrate_label, evidence, smiles=SMILES.get(substrate_label), amounts=substrate_amounts)
    reagent_amounts = []
    if equiv is not None:
        reagent_amounts.append(field("equivalents", {"number": equiv, "unit": "equiv"}, evidence))
    if exact.get("reagent_mass") is not None:
        reagent_amounts.append(field("mass", {"number": exact["reagent_mass"], "unit": "mg"}, evidence))
    if exact.get("reagent_mmol") is not None:
        reagent_amounts.append(field("amount", {"number": exact["reagent_mmol"], "unit": "mmol"}, evidence))
    reagent = common("halogen_reagent", "reagent", reagent_label, evidence, reagent_amounts)
    solvents = []
    for index, (label, volume) in enumerate(solvent_parts, 1):
        amounts = [field("volume", {"number": volume, "unit": "mL"}, evidence)] if volume is not None else []
        solvents.append(common(f"solvent_{index}", "solvent", label, evidence, amounts))
    product_amounts = []
    if exact.get("product_mass") is not None:
        product_amounts.append(field("mass", {"number": exact["product_mass"], "unit": "mg"}, evidence))
    product = participant("product", "product", product_label, evidence, smiles=SMILES.get(product_label), amounts=product_amounts)
    parts = [substrate, reagent] + solvents + [product]
    conditions = [field("temperature", temperature, evidence),
                  field("time", {"number": time_h, "unit": "h"} if time_h is not None else None, evidence)]
    outcomes = [field("isolated_yield", {"number": yld, "unit": "%"}, evidence, ["product"]),
                field("yield_measurement_basis", "isolated", evidence, ["product"])]
    if ratio:
        outcomes.append(field("Z_to_E_ratio", ratio, evidence, ["product"]))
        outcomes.append(field("selectivity_measurement_basis", "1H NMR", evidence, ["product"]))
    records.append(record(rid, source_id, kind, evidence, parts,
                          [{"step_id": "reaction", "participant_ids": [p["entity_id"] for p in parts if p["role"] != "product"], "conditions": conditions}],
                          outcomes, notes=notes, unresolved=unresolved))


# Table 1, one independent record per row. Page 5 general procedure/detailed 4a is linked as the same experiment.
table1 = [
    ("4a", "2a", "CuBr2", 1.1, {"number": 50, "unit": "°C"}, 18.5, 72),
    ("4b", "2a", "CuCl2", 1.1, "reflux", 21, 57),
    ("4c", "2b", "CuBr2", 1.1, {"number": 50, "unit": "°C"}, 22, 69),
    ("4d", "2c", "CuBr2", 1.1, {"number": 50, "unit": "°C"}, 32, 78),
    ("4e", "2c", "CuCl2", 2.0, {"number": 50, "unit": "°C"}, 36, 78),
    ("4f", "2d", "CuBr2", 2.0, "reflux", 24, 94),
    ("4g", "2d", "CuCl2", 4.0, "reflux", 60, 71),
]
for product, substrate, reagent, equiv, temp, tm, yld in table1:
    exact = {"substrate_mass": 75, "substrate_mmol": 0.28, "reagent_mass": 68, "reagent_mmol": 0.30, "product_mass": 73} if product == "4a" else {}
    add_cyclization(f"table1_{product}", f"Table 1 {product}", "substrate_scope_entry", [2, 5], substrate, product, reagent, equiv,
                    [("THF", 4 if product == "4a" else None), ("H2O", 4 if product == "4a" else None)], temp, tm, yld, exact=exact,
                    notes=["General procedure B: saturated NH4Cl quench, five chloroform extractions, Na2SO4 drying, evaporation, and silica-gel chromatography; solid products recrystallized from petroleum ether."],
                    unresolved=["The detailed paragraph for 4a prints reactant/product labels as 1a/2a, inconsistent with Scheme 5 and Table 1; this record follows the unambiguous structures and labels 2a/4a.",
                                "For 4b-4g, exact weighed amounts and characterization are referred to external supporting information not explicitly associated here.",
                                "Product candidate SMILES is unverified."] if product == "4a" else
                               ["Exact weighed amounts and product characterization are referred to supporting information that was not explicitly provided/associated.", "Product candidate SMILES is unverified."])

# Distinct Scheme 5 acetone/water result and the prose aqueous result for 2h.
add_cyclization("scheme5_4a_acetone", "Scheme 5 acetone/H2O condition", "optimization_entry", [2], "2a", "4a", "CuBr2", None,
                [("acetone", None), ("H2O", None)], {"number": 50, "unit": "°C"}, 18.5, 70,
                notes=["Scheme 5 prints acetone/H2O (3:2) and 70% as a condition distinct from the 72% THF/H2O result."],
                unresolved=["CuBr2 equivalents and solvent volumes for this condition are not separately printed in Scheme 5.", "Yield basis is not explicitly footnoted for Scheme 5; retained as reported yield rather than inferred purity.", "Candidate structures remain unverified."])
add_cyclization("optimization_2h_aqueous_4h", "Prose 2h THF/H2O screening", "optimization_entry", [2], "2h", "4h", "CuBr2", None,
                [("THF", None), ("H2O", None)], None, None, 48,
                notes=["The prose reports 48% in THF/H2O (1:1) before optimization."],
                unresolved=["CuBr2 equivalents, temperature, time, scale, and yield basis are not printed for this screening result.", "Candidate structures remain unverified."])

# Scheme 6 optimized 2h reactions.
for product, reagent, tm, yld in [("4h", "CuBr2", 19, 78), ("4i", "CuCl2", 22, 60)]:
    add_cyclization(f"scheme6_{product}", f"Scheme 6 {product}", "optimization_entry", [3], "2h", product, reagent, None,
                    [("EtOH", None), ("H2O", None)], {"number": 50, "unit": "°C"}, tm, yld,
                    notes=["Scheme 6 specifies EtOH/H2O (3:2)."],
                    unresolved=["CuX2 equivalents, scale, solvent volumes, workup, purification, and yield basis are not separately printed in Scheme 6.", "Candidate structures remain unverified."])

# Table 2 and detailed sections 3.3.1-3.3.10. Exact values come from pages 5-6.
table2 = [
    ("5a", "2e", "CuBr2", 1.1, 1, 85, ">97:3", 112, .56, 137, .61, 5, 132),
    ("5b", "2e", "CuCl2·2H2O", 1.1, 1, 85, ">98:2", 119, .59, 111, .65, 5, 119),
    ("5c", "2g", "CuBr2", 3.0, 1, 99, ">99:1", 67, .25, 168, .75, 5, 86),
    ("5d", "2g", "CuCl2·2H2O", 3.0, 2, 98, "96:4", 85, .32, 165, .97, 5, 94),
    ("5e", "2i", "CuBr2", 3.0, 1, 94, "100:0", 62, .21, 143, .61, 4, 74),
    ("5f", "2i", "CuCl2·2H2O", 3.0, 1, 97, "100:0", 48, .16, 84, .45, 4, 52),
    ("5g", "2f", "CuBr2", 1.1, 1, 78, ">98:2", 119, .71, 175, .78, 5, 137),
    ("5h", "2f", "CuCl2·2H2O", 1.1, 1, 68, ">96:4", 126, .75, 142, .83, 6, 103),
    ("5i", "2j", "CuBr2", 1.1, 2, 82, "100:0", 96, .45, 110, .49, 5, 108),
    ("5j", "2j", "CuCl2·2H2O", 1.1, 1, 95, "100:0", 105, .49, 92, .54, 5, 116),
]
for product, substrate, reagent, equiv, tm, yld, ratio, smass, smmol, rmass, rmmol, svol, pmass in table2:
    pages = [3, 5] if product == "5a" else [3, 5, 6]
    extra_note = " Scheme 7 independently shows 2i to Z-5e under CuBr2/THF for 1 h; it is the same experiment and is not duplicated." if product == "5e" else ""
    add_cyclization(f"table2_{product}", f"Table 2 / section 3.3 {product}", "substrate_scope_entry", pages, substrate, product, reagent, equiv,
                    [("THF", svol)], "r.t.", tm, yld, ratio,
                    exact={"substrate_mass": smass, "substrate_mmol": smmol, "reagent_mass": rmass, "reagent_mmol": rmmol, "product_mass": pmass},
                    notes=["General procedure C: add Et2O and saturated NH4Cl, stir 5 min, extract three times with Et2O, dry over Na2SO4, evaporate, and purify by flash silica chromatography." + extra_note],
                    unresolved=["The printed Z/E assignments for products other than 5e are described by the authors as tentative; stereochemistry is not encoded in the candidate SMILES.", "No explicitly associated SI; structures remain unverified."])

# Table 3 iodoiminolactonizations.
for product, substrate, tm, yld, ratio in [
    ("5k", "2e", 3, 75, "95:5"), ("5l", "2g", 26, 84, "96:4"),
    ("5m", "2i", 16, 92, "100:0"), ("5n", "2j", 16, 99, "100:0"),
]:
    add_cyclization(f"table3_{product}", f"Table 3 {product}", "substrate_scope_entry", [3], substrate, product, "I2", 2.0,
                    [("THF", None)], "r.t.", tm, yld, ratio,
                    unresolved=["Exact scale, solvent volume, workup, purification, and product mass are not printed in Table 3 on page 3; later pages were not included in the requested coverage ledger.", "The printed Z/E assignments are tentative except where separately established; stereochemistry is not encoded in the candidate SMILES.", "No explicitly associated SI."])

# Scheme 8 two-stage iodolactamization/oxidation rows.
for product, substrate_printed, tm, yld in [("4j", "2b", 24, 89), ("4k", "2h", 42, 58)]:
    e = ev(4)
    parts = [participant("substrate", "reactant", substrate_printed, e, smiles=SMILES.get(substrate_printed)),
             common("iodine", "reagent", "I2", e, [field("equivalents", {"number": 2.0, "unit": "equiv"}, e)]),
             common("THF", "solvent", "THF", e),
             participant("oxygen", "reagent", "O2", e, "oxygen", "O=O"),
             participant("product", "product", product, e, smiles=SMILES[product])]
    records.append(record(f"scheme8_{product}", f"Scheme 8 {product}", "substrate_scope_entry", e, parts, [
        {"step_id": "iodination", "participant_ids": ["substrate", "iodine", "THF"], "conditions": [field("temperature", "r.t.", e), field("time", {"number": 1, "unit": "h"}, e)]},
        {"step_id": "oxygen_oxidation", "participant_ids": ["oxygen"], "conditions": [field("temperature", "r.t.", e), field("total_reported_time", {"number": tm, "unit": "h"}, e)]},
    ], [field("isolated_yield", {"number": yld, "unit": "%"}, e, ["product"]), field("yield_measurement_basis", "isolated", e, ["product"])],
    notes=["Scheme 8 reports THF, I2 (2.0 equiv), 1 h before O2, and the row time/yield."],
    unresolved=["The first Scheme 8 row prints substrate label 2b while the drawn substrate/product are N-benzyl; this internal inconsistency is preserved and not silently corrected.", "It is unclear whether the row time includes the initial 1 h stage; stages were not arithmetically combined.", "Exact scale, solvent volume, O2 amount/pressure, workup, and purification are missing on page 4.", "Candidate structures remain unverified."] if product == "4j" else
               ["It is unclear whether the row time includes the initial 1 h stage; stages were not arithmetically combined.", "Exact scale, solvent volume, O2 amount/pressure, workup, and purification are missing on page 4.", "Candidate structures remain unverified."]))

# Scheme 7 Pd-catalyzed coupling used to support structural assignment.
e = ev(3)
parts = [participant("substrate", "reactant", "Z-5e", e, smiles=SMILES["5e"]),
         common("boronic_acid", "reagent", "PhB(OH)2", e), common("base", "reagent", "Na2CO3", e),
         common("Pd", "catalyst", "Pd(PPh3)4", e), participant("product", "product", "Z-6", e)]
records.append(record("scheme7_coupling_Z5e_to_Z6", "Scheme 7 coupling", "reported_experiment", e, parts,
                      [{"step_id": "coupling", "participant_ids": ["substrate", "boronic_acid", "base", "Pd"], "conditions": []}], [],
                      notes=["The coupling to known derivative Z-6 is presented as evidence for correcting the product assignment and establishing Z-5e."],
                      unresolved=["Scheme 7 does not print solvent, quantities, temperature, time, yield, workup, or purification for the coupling.", "The product Z-6 SMILES is left null because the drawing was not independently structure-verified.", "No explicitly associated SI."]))

assert len(records) == 38, len(records)
OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
print(f"wrote {len(records)} records to {OUT}")
