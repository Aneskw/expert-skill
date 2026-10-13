#!/usr/bin/env python3
"""Build evidence-linked review records for Yu & Ma 2011, PDF pages 25-30."""
import json
from pathlib import Path

DOC = "doc_e77fa99a0ade23d1"
OUT = Path(__file__).with_name("records_pages_0025_0030.json")


def ev(*pages):
    out = []
    for page in pages:
        out.extend([f"{DOC}:page{page}:image", f"{DOC}:page{page}:text"])
    return out


def fact(value, evidence):
    return {
        "value": value,
        "evidence_ids": list(evidence) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def q(number=None, unit=None, minimum=None, maximum=None, raw_text=None, qualifier=None):
    value = {"unit": unit}
    if number is not None:
        value["number"] = number
    else:
        value["minimum"] = minimum
        value["maximum"] = maximum
    if raw_text is not None:
        value["raw_text"] = raw_text
    if qualifier is not None:
        value["qualifier"] = qualifier
    return value


def field(name, value, evidence, targets=None):
    item = {"name": name, "fact": fact(value, evidence)}
    if targets:
        item["target_entity_ids"] = targets
    return item


def participant(entity_id, role, label, name, evidence, amounts=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence),
        "smiles": fact(None, evidence),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": [field(n, v, evidence) for n, v in (amounts or [])],
    }


def step(step_id, participant_ids, evidence, conditions=None):
    conditions = list(conditions or [])
    names = {name for name, _ in conditions}
    if "temperature" not in names:
        conditions.append(("temperature", None))
    if "time" not in names:
        conditions.append(("time", None))
    return {
        "step_id": step_id,
        "participant_ids": participant_ids,
        "conditions": [field(name, value, evidence) for name, value in conditions],
    }


def add(rid, pages, participant_specs, step_specs, outcome_specs=(), notes=(), unresolved=None):
    evidence = ev(*pages)
    participants = [participant(entity_id, role, label, name, evidence, amounts)
                    for entity_id, role, label, name, amounts in participant_specs]
    steps = [step(sid, ids, evidence, conditions) for sid, ids, conditions in step_specs]
    outcomes = [field(name, value, evidence, targets) for name, value, targets in outcome_specs]
    default_unresolved = [
        "This Feature Article summarizes a cited literature example rather than a new experiment by the review authors.",
        "The cited original paper and Supporting Information were not supplied or explicitly associated.",
        "Scale, atmosphere, workup, purification, and yield measurement basis are missing unless explicitly shown.",
        "Depicted connectivity and stereochemistry remain machine-unverified; complex drawings have null SMILES.",
    ]
    R.append({
        "record_id": f"{DOC}:{rid}",
        "document_id": DOC,
        "source_reaction_id": rid,
        "record_kind": "literature_example",
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": evidence,
        "participants": participants,
        "steps": steps,
        "outcomes": outcomes,
        "notes": [fact(note, evidence) for note in notes],
        "review": {"method": "none", "reviewer": None, "checked_fields": [],
                   "unresolved": unresolved if unresolved is not None else default_unresolved},
    })


R = []

# Page 25, Schemes 146-152. Page 24 prose is used only where it explicitly assigns ee.
add("scheme146_negishi_coupling", (25,), [
    ("s146_430", "reactant", "430", "n-propyl-substituted terminal diyne", []),
    ("s146_435", "reactant", "(S)-435", "optically active propargyl mesylate", []),
    ("s146_nBuLi", "reagent", None, "n-butyllithium", [("equivalents", q(2.6, "equiv"))]),
    ("s146_InCl2", "reagent", None, "indium(II) chloride", [("equivalents", q(1.2, "equiv"))]),
    ("s146_Pd", "catalyst", None, "Pd(PPh3)2Cl2", [("catalyst_loading", q(2, "mol%"))]),
    ("s146_THF", "solvent", None, "tetrahydrofuran", []),
    ("s146_436", "product", "(R)-436", "protected phomallenic-acid-C allenediyne", []),
], [("indium_negishi_coupling", ["s146_430", "s146_435", "s146_nBuLi", "s146_InCl2", "s146_Pd", "s146_THF", "s146_436"], [("temperature", "r.t.")])], [
    ("reported_yield", q(72, "%"), ["s146_436"]),
    ("enantiomeric_excess", q(98, "%"), ["s146_436"]),
    ("yield_measurement_basis", None, ["s146_436"]),
])

add("scheme146_phomallenic_acid_completion", (25,), [
    ("s146b_436", "reactant", "(R)-436", "protected phomallenic-acid-C allenediyne", []),
    ("s146b_432", "product", "(R)-432", "(R)-phomallenic acid C", []),
], [("unspecified_completion_sequence", ["s146b_436", "s146b_432"], [])], [
    ("enantiomeric_excess", q(96, "%"), ["s146b_432"]),
], notes=["Scheme 146 shows a multiple-arrow completion but supplies no reagents, time, temperature, or yield for this stage."],
    unresolved=["The number and identity of the transformations from 436 to 432 are not stated in the review scheme.",
                "No stage yield or operational details are reported.",
                "The cited original paper/SI was not supplied; structures remain unverified."])

add("scheme147_tosylate_direct_coupling", (25,), [
    ("s147_437", "reactant", "437", "enantioenriched propargyl tosylate", [("enantiomeric_excess", q(97, "%"))]),
    ("s147_439", "reactant", "439", "zincated TMS-protected diyne", []),
    ("s147_Pd", "catalyst", None, "Pd(PPh3)4", []),
    ("s147_THF", "solvent", None, "tetrahydrofuran", []),
    ("s147_440", "product", "(aS)-440", "marasin allenediyne intermediate", []),
], [("direct_coupling", ["s147_437", "s147_439", "s147_Pd", "s147_THF", "s147_440"], [("temperature", q(minimum=-78, maximum=-20, unit="°C", raw_text="-78 °C to -20 °C"))])], [
    ("reported_yield", q(72, "%"), ["s147_440"]), ("enantiomeric_excess", q(89, "%"), ["s147_440"]),
    ("yield_measurement_basis", None, ["s147_440"]),
])

add("scheme147_bromoallene_preparation", (25,), [
    ("s147b_437", "reactant", "437", "enantioenriched propargyl tosylate", [("enantiomeric_excess", q(97, "%"))]),
    ("s147b_CuBr", "reagent", None, "copper(I) bromide", []),
    ("s147b_LiBr", "reagent", None, "lithium bromide", []),
    ("s147b_438", "product", "(aS)-438", "optically active bromoallene", []),
], [("bromide_substitution", ["s147b_437", "s147b_CuBr", "s147b_LiBr", "s147b_438"], [])], [
    ("reported_yield", q(96, "%"), ["s147b_438"]), ("enantiomeric_excess", q(78, "%"), ["s147b_438"]),
    ("yield_measurement_basis", None, ["s147b_438"]),
])

add("scheme147_bromoallene_coupling", (25,), [
    ("s147c_438", "reactant", "(aS)-438", "optically active bromoallene", [("enantiomeric_excess", q(78, "%"))]),
    ("s147c_439", "reactant", "439", "zincated TMS-protected diyne", []),
    ("s147c_Pd", "catalyst", None, "Pd(PPh3)4", []), ("s147c_THF", "solvent", None, "tetrahydrofuran", []),
    ("s147c_440", "product", "(aR)-440", "marasin allenediyne intermediate", []),
], [("coupling", ["s147c_438", "s147c_439", "s147c_Pd", "s147c_THF", "s147c_440"], [("temperature", q(minimum=-78, maximum=-20, unit="°C", raw_text="-78 °C to -20 °C"))])], [
    ("reported_yield", q(70, "%"), ["s147c_440"]), ("enantiomeric_excess", q(36, "%"), ["s147c_440"]),
    ("yield_measurement_basis", None, ["s147c_440"]),
])

add("scheme148_sulfoxide_elimination", (24, 25), [
    ("s148_441", "reactant", "441", "diyne-containing allyl acetate-vinyl sulfoxide", [("enantiomeric_excess", q(98, "%"))]),
    ("s148_iPrMgBr", "reagent", None, "isopropylmagnesium bromide", []), ("s148_THF", "solvent", None, "tetrahydrofuran", []),
    ("s148_442", "product", "(aS)-442", "marasin allenediyne acetate", []),
], [("sulfoxide_elimination", ["s148_441", "s148_iPrMgBr", "s148_THF", "s148_442"], [("temperature", q(-100, "°C"))])], [
    ("reported_yield", q(85, "%"), ["s148_442"]), ("enantiomeric_excess", q(73, "%"), ["s148_442"]),
    ("yield_measurement_basis", None, ["s148_442"]),
], notes=["Product ee is explicitly assigned in the page-24 prose; the reaction drawing is on page 25."])

add("scheme148_dibal_deprotection", (25,), [
    ("s148b_442", "reactant", "(aS)-442", "marasin allenediyne acetate", [("enantiomeric_excess", q(73, "%"))]),
    ("s148b_DIBAL", "reagent", None, "DIBAL-H", []), ("s148b_CH2Cl2", "solvent", None, "dichloromethane", []),
    ("s148b_443", "product", "(aS)-443", "marasin alcohol", []),
], [("reduction_deprotection", ["s148b_442", "s148b_DIBAL", "s148b_CH2Cl2", "s148b_443"], [("temperature", q(-78, "°C"))])], [
    ("reported_yield", q(87, "%"), ["s148b_443"]), ("enantiomeric_excess", q(73, "%"), ["s148b_443"]),
    ("yield_measurement_basis", None, ["s148b_443"]),
])

add("scheme149_iodide_precursor_preparation", (25,), [
    ("s149_444", "reactant", "444", "iodo-substituted marasin precursor", [("enantiomeric_excess", q(89, "%"))]),
    ("s149_K2CO3", "reagent", None, "potassium carbonate", []), ("s149_Et2O", "solvent", None, "diethyl ether", []),
    ("s149_MeOH", "solvent", None, "methanol", []), ("s149_Ac2O", "reagent", None, "acetic anhydride", []),
    ("s149_CH2Cl2", "solvent", None, "dichloromethane", []), ("s149_DMAP", "reagent", None, "DMAP", []),
    ("s149_Et3N", "reagent", None, "triethylamine", []), ("s149_445", "product", "445", "iodo allylic acetate precursor", []),
], [("carbonate_treatment", ["s149_444", "s149_K2CO3", "s149_Et2O", "s149_MeOH"], [("temperature", "r.t.")]),
    ("acetylation", ["s149_444", "s149_Ac2O", "s149_CH2Cl2", "s149_DMAP", "s149_Et3N", "s149_445"], [])], [
    ("reported_yield", q(79, "%"), ["s149_445"]), ("yield_measurement_basis", None, ["s149_445"]),
])

add("scheme149_marasin_formation", (25,), [
    ("s149b_445", "reactant", "445", "iodo allylic acetate precursor", []),
    ("s149b_iPrMgBr", "reagent", None, "isopropylmagnesium bromide", []), ("s149b_THF", "solvent", None, "tetrahydrofuran", []),
    ("s149b_HCl", "reagent", None, "hydrochloric acid", []), ("s149b_MeOH", "solvent", None, "methanol", []),
    ("s149b_Et2O", "solvent", None, "diethyl ether", []), ("s149b_443", "product", "(aR)-443", "(aR)-(-)-marasin", []),
], [("allene_formation", ["s149b_445", "s149b_iPrMgBr", "s149b_THF"], [("temperature", q(-78, "°C"))]),
    ("acidic_deprotection", ["s149b_445", "s149b_HCl", "s149b_MeOH", "s149b_Et2O", "s149b_443"], [("temperature", q(0, "°C"))])], [
    ("reported_yield", q(79, "%"), ["s149b_443"]), ("enantiomeric_excess", q(75, "%"), ["s149b_443"]),
    ("yield_measurement_basis", None, ["s149b_443"]),
])

add("scheme150_allenyne_formation", (25,), [
    ("s150_446", "reactant", "446", "iodo allylic acetate containing one alkyne", []),
    ("s150_iPrMgBr", "reagent", None, "isopropylmagnesium bromide", []), ("s150_THF", "solvent", None, "tetrahydrofuran", []),
    ("s150_447", "product", "(aS)-447", "optically active allenyne", []),
], [("allene_formation", ["s150_446", "s150_iPrMgBr", "s150_THF", "s150_447"], [("temperature", q(-78, "°C"))])], [
    ("reported_yield", q(80, "%"), ["s150_447"]), ("enantiomeric_excess", q(94, "%"), ["s150_447"]),
    ("yield_measurement_basis", None, ["s150_447"]),
])

add("scheme150_failed_diyne_extension", (24, 25), [
    ("s150b_447", "reactant", "(aS)-447", "optically active allenyne", [("enantiomeric_excess", q(94, "%"))]),
    ("s150b_448", "reactant", "448", "TMS-protected iodo-diyne shown in Scheme 150", []),
    ("s150b_Pd", "catalyst", None, "Pd(PPh3)4", []), ("s150b_CuI", "catalyst", None, "copper(I) iodide", []),
    ("s150b_Et3N", "reagent", None, "triethylamine", []), ("s150b_DMSO", "solvent", None, "DMSO", []),
    ("s150b_442", "product", "(aS)-442", "marasin allenediyne acetate", []),
], [("alkyne_alkyne_coupling", ["s150b_447", "s150b_448", "s150b_Pd", "s150b_CuI", "s150b_Et3N", "s150b_DMSO", "s150b_442"], [("temperature", "r.t."), ("time", q(30, "min"))])], [
    ("reported_yield", q(24, "%"), ["s150b_442"]), ("enantiomeric_excess", q(15, "%"), ["s150b_442"]),
    ("yield_measurement_basis", None, ["s150b_442"]),
], notes=["The page-24 prose describes this attachment attempt as failing synthetically because the substrate decomposed readily; Scheme 150 nevertheless reports 24% product and 15% ee.",
          "Compound label 448 is also printed for a different-looking substrate in Scheme 151; labels are preserved without cross-scheme structure merging."])

add("scheme151_scorodonin_fragment_coupling", (25,), [
    ("s151_448", "reactant", "448", "terminal alkyne bearing an OTES substituent", []),
    ("s151_449", "reactant", "(aR)-449", "optically active bromoallene", [("enantiomeric_excess", q(95, "%"))]),
    ("s151_nBuLi", "reagent", None, "n-butyllithium", []), ("s151_THF", "solvent", None, "tetrahydrofuran", []),
    ("s151_ZnBr2", "reagent", None, "zinc bromide", []), ("s151_Pd", "catalyst", None, "Pd(PPh3)4", [("catalyst_loading", q(5, "mol%"))]),
    ("s151_450", "product", "(aR)-450", "protected scorodonin allenyne", []),
], [("lithiation", ["s151_448", "s151_nBuLi", "s151_THF"], [("temperature", q(-78, "°C"))]),
    ("zincation", ["s151_448", "s151_ZnBr2"], []),
    ("palladium_coupling", ["s151_448", "s151_449", "s151_Pd", "s151_450"], [("temperature", q(-78, "°C")), ("time", q(2, "h"))]),
    ("warming", ["s151_450"], [("temperature", q(0, "°C")), ("time", q(2, "h"))])], [
    ("reported_yield", q(90, "%"), ["s151_450"]), ("enantiomeric_excess", q(63, "%"), ["s151_450"]),
    ("yield_measurement_basis", None, ["s151_450"]),
])

add("scheme151_etes_deprotection", (25,), [
    ("s151b_450", "reactant", "(aR)-450", "OTES-protected scorodonin allenyne", [("enantiomeric_excess", q(63, "%"))]),
    ("s151b_FeCl3", "catalyst", None, "iron(III) chloride", [("catalyst_loading", q(0.1, "mol%"))]),
    ("s151b_MeOH", "solvent", None, "methanol", []), ("s151b_451", "product", "(aR)-451", "hydroxyethyl scorodonin allenyne", []),
], [("OTES_deprotection", ["s151b_450", "s151b_FeCl3", "s151b_MeOH", "s151b_451"], [("temperature", "r.t.")])], [
    ("reported_yield", q(82, "%"), ["s151b_451"]), ("yield_measurement_basis", None, ["s151b_451"]),
])

add("scheme151_chloride_formation", (25,), [
    ("s151c_451", "reactant", "(aR)-451", "hydroxyethyl scorodonin allenyne", []),
    ("s151c_MsCl", "reagent", None, "methanesulfonyl chloride", []), ("s151c_LiCl", "reagent", None, "lithium chloride", []),
    ("s151c_lutidine", "reagent", None, "2,6-lutidine", []), ("s151c_DMF", "solvent", None, "DMF", []),
    ("s151c_452", "product", "(aR)-452", "chloroethyl protected scorodonin allenyne", []),
], [("alcohol_to_chloride", ["s151c_451", "s151c_MsCl", "s151c_LiCl", "s151c_lutidine", "s151c_DMF", "s151c_452"], [("temperature", "r.t."), ("time", q(2, "h"))])], [
    ("reported_yield", q(69, "%"), ["s151c_452"]), ("yield_measurement_basis", None, ["s151c_452"]),
])

add("scheme151_tbs_deprotection", (25,), [
    ("s151d_452", "reactant", "(aR)-452", "TBS-protected scorodonin precursor", []),
    ("s151d_TBAF", "reagent", None, "tetrabutylammonium fluoride", []), ("s151d_THF", "solvent", None, "tetrahydrofuran", []),
    ("s151d_453", "product", "(aR)-453", "(-)-scorodonin", []),
], [("TBS_deprotection", ["s151d_452", "s151d_TBAF", "s151d_THF", "s151d_453"], [("temperature", "r.t."), ("time", q(1, "h"))])], [
    ("reported_yield", q(93, "%"), ["s151d_453"]), ("yield_measurement_basis", None, ["s151d_453"]),
])

add("scheme152_vinyl_sulfoxide_preparation", (25,), [
    ("s152_454", "reactant", "(S)-454", "chiral vinyl sulfoxide precursor", [("enantiomeric_excess", q(88.5, "%"))]),
    ("s152_455", "product", "(S,S)-455", "allylic acetate-vinyl sulfoxide", []),
], [("unspecified_precursor_conversion", ["s152_454", "s152_455"], [])], notes=["Scheme 152 draws an arrow from 454 to 455 but provides no reagents, time, temperature, or yield."],
    unresolved=["Conditions and outcome for conversion 454 to 455 are absent from the review.", "Original paper/SI was not supplied; structures remain unverified."])

add("scheme152_sulfoxide_elimination", (25,), [
    ("s152b_455", "reactant", "(S,S)-455", "allylic acetate-vinyl sulfoxide", []),
    ("s152b_iPrMgBr", "reagent", None, "isopropylmagnesium bromide", []), ("s152b_THF", "solvent", None, "tetrahydrofuran", []),
    ("s152b_456", "product", "(aS)-456", "scorodonin allenyne intermediate", []),
], [("sulfoxide_elimination", ["s152b_455", "s152b_iPrMgBr", "s152b_THF", "s152b_456"], [("temperature", q(-100, "°C")), ("time", q(15, "min"))])], [
    ("reported_yield", q(80, "%"), ["s152b_456"]), ("enantiomeric_excess", q(87, "%"), ["s152b_456"]),
    ("yield_measurement_basis", None, ["s152b_456"]),
])

add("scheme152_scorodonin_completion", (25,), [
    ("s152c_456", "reactant", "(aS)-456", "scorodonin allenyne intermediate", [("enantiomeric_excess", q(87, "%"))]),
    ("s152c_453", "product", "(aS)-453", "(+)-scorodonin", []),
], [("unspecified_completion_sequence", ["s152c_456", "s152c_453"], [])], notes=["Scheme 152 shows a multiple-arrow completion to (+)-scorodonin without conditions or yield."],
    unresolved=["The number, reagents, conditions, and yields of the completion sequence are not reported.", "Original paper/SI was not supplied; structures remain unverified."])

# Pages 26-27, Schemes 153-160.
add("scheme153_negishi_coupling", (26,), [
    ("s153_457", "reactant", "457", "lactone-bearing propargylic tosylate", []),
    ("s153_TMSalkyne", "reactant", None, "TMS-protected alkynyl organolithium species shown in Scheme 153", []),
    ("s153_ZnBr2", "reagent", None, "zinc bromide", []), ("s153_Pd", "catalyst", None, "Pd(PPh3)4", []),
    ("s153_458", "product", "458", "protected nemotin allene-diyne", []),
], [("negishi_coupling", ["s153_457", "s153_TMSalkyne", "s153_ZnBr2", "s153_Pd", "s153_458"], [("temperature", q(minimum=-78, maximum=-20, unit="°C", raw_text="-78 °C to -20 °C")), ("time", q(3, "h"))])], [
    ("reported_yield", q(64, "%"), ["s153_458"]), ("yield_measurement_basis", None, ["s153_458"]),
])

add("scheme153_nemotin_deprotection", (26,), [
    ("s153b_458", "reactant", "458", "protected nemotin allene-diyne", []),
    ("s153b_AgNO3", "reagent", None, "silver nitrate", []), ("s153b_MeOH", "solvent", None, "methanol", []),
    ("s153b_NaCN", "reagent", None, "sodium cyanide", []), ("s153b_NH4Cl", "reagent", None, "ammonium chloride", []),
    ("s153b_459", "product", "459", "nemotin", []),
], [("silver_deprotection", ["s153b_458", "s153b_AgNO3", "s153b_MeOH"], []),
    ("cyanide_ammonium_chloride_workup", ["s153b_458", "s153b_NaCN", "s153b_NH4Cl", "s153b_459"], [])], [
    ("reported_yield", q(71, "%"), ["s153b_459"]), ("yield_measurement_basis", None, ["s153b_459"]),
])

for suffix, leaving_group, yld in [("trisylate", "Tris", 65), ("mesylate", "Ms", 50)]:
    add(f"scheme154_panacene_{suffix}", (26, 27), [
        (f"s154_{suffix}_460", "reactant", "460", f"panacene propargyl {suffix}", [("leaving_group", leaving_group)]),
        (f"s154_{suffix}_LiCuBr2", "reagent", None, "lithium dibromocuprate", []),
        (f"s154_{suffix}_THF", "solvent", None, "tetrahydrofuran", []),
        (f"s154_{suffix}_461", "product", "(-)-461", "(-)-panacene", []),
    ], [("anti_SN2_prime_substitution", [f"s154_{suffix}_460", f"s154_{suffix}_LiCuBr2", f"s154_{suffix}_THF", f"s154_{suffix}_461"], [("temperature", "reflux")])], [
        ("reported_yield", q(yld, "%"), [f"s154_{suffix}_461"]), ("yield_measurement_basis", None, [f"s154_{suffix}_461"]),
    ])

add("scheme155_oxymercuration_demercuration", (26, 27), [
    ("s155_462", "reactant", "462", "bromo-substituted conjugated enyne", []),
    ("s155_HgOAc2", "reagent", None, "mercury(II) acetate", []), ("s155_PhH", "solvent", None, "benzene", []),
    ("s155_dithiol", "reagent", None, "1,3-propanedithiol", []), ("s155_461", "product", "(+/-)-461", "racemic panacene", []),
], [("oxymercuration", ["s155_462", "s155_HgOAc2", "s155_PhH"], [("temperature", "r.t."), ("time", q(2, "h"))]),
    ("thiol_demercuration", ["s155_462", "s155_dithiol", "s155_461"], [])], [
    ("reported_yield", q(75, "%"), ["s155_461"]), ("yield_measurement_basis", None, ["s155_461"]),
], notes=["Mercurio intermediate 463 is bracketed as an intermediate and is not treated as an isolated product."])

add("scheme156_bromoetherification", (26, 27), [
    ("s156_464", "reactant", "464", "panacene enyne precursor", []), ("s156_466", "reagent", "466", "2,4,4,6-tetrabromo-2,5-cyclohexadienone (TBCD)", []),
    ("s156_benzene", "solvent", None, "benzene", []), ("s156_465", "product", "465", "racemic epipanacene", []),
], [("bromoetherification", ["s156_464", "s156_466", "s156_benzene", "s156_465"], [("temperature", "r.t.")])], [
    ("reported_yield", q(81, "%"), ["s156_465"]), ("yield_measurement_basis", None, ["s156_465"]),
])

add("scheme157_desbromopanacene_allenylation", (26, 27), [
    ("s157_467", "reactant", "467", "desbromopanacene oxocarbenium precursor", []),
    ("s157_propargylsilane", "reactant", None, "propargyltrimethylsilane", []), ("s157_BF3", "reagent", None, "boron trifluoride etherate", []),
    ("s157_CH2Cl2", "solvent", None, "dichloromethane", []), ("s157_468", "product", "468", "racemic desbromopanacene", []),
], [("Lewis_acid_allenylation", ["s157_467", "s157_propargylsilane", "s157_BF3", "s157_CH2Cl2", "s157_468"], [("temperature", q(-78, "°C")), ("time", q(15, "min"))])], [
    ("reported_yield", q(63, "%"), ["s157_468"]), ("yield_measurement_basis", None, ["s157_468"]),
])

add("scheme158_aplysiallene_bromoallene", (26, 27), [
    ("s158_469", "reactant", "469", "R-propargyl trisylate aplysiallene precursor", []),
    ("s158_LiCuBr2", "reagent", None, "lithium dibromocuprate", []), ("s158_470", "product", "470", "(-)-aplysiallene", []),
], [("anti_SN2_prime_substitution", ["s158_469", "s158_LiCuBr2", "s158_470"], [])], [
    ("reported_yield", q(60, "%"), ["s158_470"]), ("yield_measurement_basis", None, ["s158_470"]),
])

add("scheme159_glycidol_to_iodide", (26, 27), [
    ("s159_471", "reactant", "471", "(S)-glycidol", []), ("s159_472", "product", "472", "histrionicotoxin alkyl iodide intermediate", []),
], [("unspecified_multistep_sequence", ["s159_471", "s159_472"], [])], notes=["Scheme 159 shows a multiple-arrow sequence from glycidol 471 to iodide 472 without reagents or yields."],
    unresolved=["The number of stages, conditions, and yields from 471 to 472 are omitted in the review.", "Original paper/SI was not supplied; structures remain unverified."])

add("scheme159_allenyl_lithium_substitution", (26, 27), [
    ("s159b_472", "reactant", "472", "histrionicotoxin alkyl iodide intermediate", []),
    ("s159b_473", "reactant", "473", "TIPS-protected terminal allene precursor", []), ("s159b_nBuLi", "reagent", None, "n-butyllithium", []),
    ("s159b_HMPA", "reagent", None, "HMPA", []), ("s159b_THF", "solvent", None, "tetrahydrofuran", []),
    ("s159b_474", "product", "474", "allene-bearing histrionicotoxin intermediate", []),
], [("allenyl_lithium_substitution", ["s159b_472", "s159b_473", "s159b_nBuLi", "s159b_HMPA", "s159b_THF", "s159b_474"], [("temperature", q(-78, "°C"))])], [
    ("reported_yield", q(99, "%"), ["s159b_474"]), ("yield_measurement_basis", None, ["s159b_474"]),
])

add("scheme159_smi2_reduction", (27,), [
    ("s159c_474", "reactant", "474", "allene-bearing histrionicotoxin intermediate", []),
    ("s159c_SmI2", "reagent", None, "samarium(II) iodide", []), ("s159c_THF", "solvent", None, "tetrahydrofuran", []),
    ("s159c_475", "product", "(-)-475", "(-)-histrionicotoxin 285A", []),
], [("reductive_deprotection", ["s159c_474", "s159c_SmI2", "s159c_THF", "s159c_475"], [])], [
    ("reported_yield", q(85, "%"), ["s159c_475"]), ("yield_measurement_basis", None, ["s159c_475"]),
])

add("scheme160_bromoallene_formation", (26, 27), [
    ("s160_476", "reactant", "476", "peridinin propargylic oxirane precursor", []),
    ("s160_CuBr", "reagent", None, "copper(I) bromide", []), ("s160_NH4Br", "reagent", None, "ammonium bromide", []),
    ("s160_HBr", "reagent", None, "hydrogen bromide", []), ("s160_Et2O", "solvent", None, "diethyl ether", []),
    ("s160_intermediate", "product", None, "bromoallene alcohol intermediate from 476", []),
], [("SN2_prime_bromide_opening", ["s160_476", "s160_CuBr", "s160_NH4Br", "s160_HBr", "s160_Et2O", "s160_intermediate"], [("temperature", q(-10, "°C"))])], [
    ("stage_reported_yield", q(85, "%"), ["s160_intermediate"]), ("yield_measurement_basis", None, ["s160_intermediate"]),
], notes=["The first-stage intermediate is not numbered in Scheme 160 but the first 85% is printed before the separate acetylation stage."])

add("scheme160_acetylation_477", (27,), [
    ("s160b_intermediate", "reactant", None, "bromoallene alcohol intermediate from 476", []),
    ("s160b_Ac2O", "reagent", None, "acetic anhydride", []), ("s160b_pyridine", "solvent", None, "pyridine", []),
    ("s160b_477", "product", "477", "bromoallene acetate fragment", []),
], [("acetylation", ["s160b_intermediate", "s160b_Ac2O", "s160b_pyridine", "s160b_477"], [("temperature", q(25, "°C")), ("time", q(16, "h"))])], [
    ("stage_reported_yield", q(85, "%"), ["s160b_477"]), ("yield_measurement_basis", None, ["s160b_477"]),
])

add("scheme160_stille_epimeric_fragment", (26, 27), [
    ("s160c_477", "reactant", "477", "bromoallene acetate fragment", []), ("s160c_478", "reactant", "478", "vinylstannane reagent", []),
    ("s160c_Pd", "catalyst", None, "Pd(PPh3)2Cl2", [("catalyst_loading", q(20, "mol%"))]),
    ("s160c_iPr2NEt", "reagent", None, "diisopropylethylamine", []), ("s160c_solvent", "solvent", None, "DMF/THF", []),
    ("s160c_479", "product", "479", "epimeric peridinin allenene fragment", []),
], [("Stille_coupling", ["s160c_477", "s160c_478", "s160c_Pd", "s160c_iPr2NEt", "s160c_solvent", "s160c_479"], [("temperature", q(40, "°C"))])], [
    ("reported_yield", q(64, "%"), ["s160c_479"]), ("yield_measurement_basis", None, ["s160c_479"]),
], notes=["The review states that allene configuration inverted and this route produced an epimeric fragment."])

add("scheme160_dibal_reduction", (26, 27), [
    ("s160d_480", "reactant", "480", "peridinin propargylic oxirane fragment", []),
    ("s160d_DIBAL", "reagent", None, "DIBAL-H", []), ("s160d_CH2Cl2", "solvent", None, "dichloromethane", []),
    ("s160d_481", "product", "481", "peridinin allenene fragment with correct stereochemistry", []),
], [("SN2_prime_hydride_reduction", ["s160d_480", "s160d_DIBAL", "s160d_CH2Cl2", "s160d_481"], [("temperature", q(0, "°C"))])], [
    ("reported_yield", q(99, "%"), ["s160d_481"]), ("yield_measurement_basis", None, ["s160d_481"]),
])

add("scheme160_peridinin_completion", (27,), [
    ("s160e_481", "reactant", "481", "peridinin allenene fragment", []), ("s160e_482", "product", "482", "peridinin", []),
], [("unspecified_completion_sequence", ["s160e_481", "s160e_482"], [])], notes=["Scheme 160 shows a multiple-arrow completion from fragment 481 to peridinin 482 without conditions or yield."],
    unresolved=["Completion steps and yields from 481 to 482 are not stated.", "Original paper/SI was not supplied; structures remain unverified."])

# Page 28, Schemes 161-166.
add("scheme161_sonogashira_coupling", (26, 28), [
    ("s161_483", "reactant", "483", "acetylene fragment", []), ("s161_484", "reactant", "484", "trienyl vinyl iodide", []),
    ("s161_Pd", "catalyst", None, "Pd(PPh3)4", [("catalyst_loading", q(10, "mol%"))]),
    ("s161_CuI", "catalyst", None, "copper(I) iodide", []), ("s161_iPr2NH", "solvent", None, "diisopropylamine", []),
    ("s161_485", "product", "485", "coupled peridinin/paracentrone acetylene fragment", []),
], [("Sonogashira_coupling", ["s161_483", "s161_484", "s161_Pd", "s161_CuI", "s161_iPr2NH", "s161_485"], [("temperature", "r.t."), ("time", q(4, "h"))])], [
    ("reported_yield", q(81, "%"), ["s161_485"]), ("yield_measurement_basis", None, ["s161_485"]),
])

add("scheme161_dibal_allenene_formation", (26, 28), [
    ("s161b_485", "reactant", "485", "coupled acetylene fragment", []), ("s161b_DIBAL", "reagent", None, "DIBAL-H", []),
    ("s161b_CH2Cl2", "solvent", None, "dichloromethane", []), ("s161b_486", "product", "486", "allenene fragment", []),
], [("SN2_prime_hydride_reduction", ["s161b_485", "s161b_DIBAL", "s161b_CH2Cl2", "s161b_486"], [("temperature", q(0, "°C")), ("time", q(30, "min"))])], [
    ("reported_yield", q(80, "%"), ["s161b_486"]), ("yield_measurement_basis", None, ["s161b_486"]),
])

add("scheme161_paracentrone_completion", (26, 28), [
    ("s161c_486", "reactant", "486", "allenene fragment", []), ("s161c_487", "product", "487", "paracentrone", []),
], [("unspecified_completion_sequence", ["s161c_486", "s161c_487"], [])], notes=["Scheme 161 shows an unlabelled multiple-arrow completion to paracentrone 487."],
    unresolved=["Reagents, conditions, number of stages, and yield for 486 to 487 are omitted.", "Original paper/SI was not supplied; structures remain unverified."])

add("scheme162_bromoallene_formation", (27, 28), [
    ("s162_488", "reactant", "488", "9-(phenylethynyl)fluoren-9-ol", []),
    ("s162_HBr", "reagent", None, "hydrogen bromide", []), ("s162_HOAc", "solvent", None, "acetic acid", []),
    ("s162_491", "product", "491", "fluorene-derived bromoallene", []),
], [("bromoallene_formation", ["s162_488", "s162_HBr", "s162_HOAc", "s162_491"], [])], [
    ("reported_yield", q(92, "%"), ["s162_491"]), ("yield_measurement_basis", None, ["s162_491"]),
])

add("scheme162_allenylphosphine", (27, 28), [
    ("s162b_491", "reactant", "491", "fluorene-derived bromoallene", []), ("s162b_BuLi", "reagent", None, "butyllithium", []),
    ("s162b_THF", "solvent", None, "tetrahydrofuran", []), ("s162b_Ph2PCl", "reactant", None, "chlorodiphenylphosphine", []),
    ("s162b_492", "product", "492", "fluorene-derived allenylphosphine", []),
], [("bromine_lithium_exchange", ["s162b_491", "s162b_BuLi", "s162b_THF"], []),
    ("phosphine_trapping", ["s162b_491", "s162b_Ph2PCl", "s162b_492"], [])], [
    ("reported_yield", q(84, "%"), ["s162b_492"]), ("yield_measurement_basis", None, ["s162b_492"]),
])

add("scheme162_allenylphosphine_oxide", (27, 28), [
    ("s162c_488", "reactant", "488", "9-(phenylethynyl)fluoren-9-ol", []), ("s162c_Ph2PCl", "reactant", None, "chlorodiphenylphosphine", []),
    ("s162c_Et3N", "reagent", None, "triethylamine", []), ("s162c_490", "product", "490", "fluorene-derived allenylphosphine oxide", []),
], [("phosphinite_formation_and_rearrangement", ["s162c_488", "s162c_Ph2PCl", "s162c_Et3N", "s162c_490"], [])], [
    ("reported_yield", q(91, "%"), ["s162c_490"]), ("yield_measurement_basis", None, ["s162c_490"]),
], notes=["Species 489 is bracketed as the acetylenic phosphinite intermediate and is not treated as an isolated product."])

routes = [
    ("memgbr_cui_libr", [("route_reagents", "MeMgBr/CuI/LiBr")]),
    ("tbuli_cucn", [("route_reagents", "tBuLi/CuCN")]),
    ("armgbr_zncl2_pd", [("route_reagents", "ArMgBr/ZnCl2/Pd(PPh3)4")]),
]
for suffix, route_amounts in routes:
    add(f"scheme163_allenic_phosphine_oxide_{suffix}", (28,), [
        (f"s163_{suffix}_493", "reactant", "493", "propargylic acetate or bromide substrate series", []),
        (f"s163_{suffix}_route", "unspecified_agent", None, route_amounts[0][1], []),
        (f"s163_{suffix}_tBuLi", "reagent", None, "tert-butyllithium", []),
        (f"s163_{suffix}_ClPOAr2", "reactant", None, "diarylchlorophosphine oxide", []),
        (f"s163_{suffix}_494", "product", "494", "allenic phosphine oxide ligand", []),
    ], [("propargylic_substitution", [f"s163_{suffix}_493", f"s163_{suffix}_route"], []),
        ("bromine_lithium_exchange", [f"s163_{suffix}_493", f"s163_{suffix}_tBuLi"], []),
        ("phosphine_oxide_trapping", [f"s163_{suffix}_493", f"s163_{suffix}_ClPOAr2", f"s163_{suffix}_494"], [])], [
        ("reported_yield", None, [f"s163_{suffix}_494"]), ("enantiomeric_excess", None, [f"s163_{suffix}_494"]),
    ], notes=["Scheme 163 reports aggregate 93-97% yields and 33-87% ee across three alternative routes; values cannot be assigned safely to this route alone."])

add("scheme163_meso_epoxide_ring_opening", (28,), [
    ("s163b_494", "catalyst", "494", "allenic phosphine oxide ligand", []),
    ("s163b_epoxide", "reactant", None, "meso-epoxide", []), ("s163b_SnCl4", "reagent", None, "tin(IV) chloride", []),
    ("s163b_product", "product", None, "asymmetric ring-opening product", []),
], [("SnCl4_mediated_ring_opening", ["s163b_494", "s163b_epoxide", "s163b_SnCl4", "s163b_product"], [])], [
    ("enantiomeric_excess", q(minimum=82, maximum=94, unit="%", raw_text="82-94% ee"), ["s163b_product"]),
], notes=["The prose reports ligand performance but omits substrate identities, product structures, yields, and full conditions."])

add("scheme164_allenophane_formation", (28,), [
    ("s164_495", "reactant", "495", "optically active bispropargylic acetate precursor", []),
    ("s164_MeMgBr", "reactant", None, "methylmagnesium bromide", [("equivalents", q(30, "equiv"))]),
    ("s164_LiBr", "reagent", None, "lithium bromide", [("equivalents", q(30, "equiv"))]),
    ("s164_CuI", "reagent", None, "copper(I) iodide", [("equivalents", q(30, "equiv"))]),
    ("s164_THF", "solvent", None, "tetrahydrofuran", []), ("s164_496", "product", "496", "enantiomerically pure allenophane", []),
], [("organocuprate_SN2_prime_coupling", ["s164_495", "s164_MeMgBr", "s164_LiBr", "s164_CuI", "s164_THF", "s164_496"], [("temperature", q(0, "°C")), ("time", q(3.5, "h"))]),
    ("warming", ["s164_496"], [("temperature", q(22, "°C")), ("time", q(15, "min"))])], [
    ("reported_yield", q(85, "%"), ["s164_496"]), ("yield_measurement_basis", None, ["s164_496"]),
])

rows165 = [
    ("entry1_tms_s", "TMS (S)", "Cy2NMe", 30, 5, 61, "90:1"),
    ("entry2_tms_r", "TMS (R)", "iPr2NH", 20, 20, 90, "5:95"),
    ("entry3_cme2oh_s", "CMe2OH (S)", "Cy2NMe", 30, 96, 69, "96:4"),
    ("entry4_cme2oh_r", "CMe2OH (R)", "iPr2NH", 20, 96, 49, "7:93"),
]
for suffix, rgroup, base, temp, hours, yld, er in rows165:
    add(f"scheme165_{suffix}", (28,), [
        (f"s165_{suffix}_497", "reactant", "497", f"bispropargylic pentafluorobenzoate, R={rgroup}", []),
        (f"s165_{suffix}_498", "reactant", "498", "terminal alkyne", []),
        (f"s165_{suffix}_Pd", "catalyst", None, "PdCl2(PPh3)2", []), (f"s165_{suffix}_CuI", "catalyst", None, "copper(I) iodide", []),
        (f"s165_{suffix}_base", "reagent", None, base, []), (f"s165_{suffix}_499", "product", "499", "optically active 1,3-diethynylallene", []),
    ], [("enantioselective_SN2_prime_coupling", [f"s165_{suffix}_497", f"s165_{suffix}_498", f"s165_{suffix}_Pd", f"s165_{suffix}_CuI", f"s165_{suffix}_base", f"s165_{suffix}_499"], [("temperature", q(temp, "°C")), ("time", q(hours, "h"))])], [
        ("reported_yield", q(yld, "%"), [f"s165_{suffix}_499"]), ("enantiomeric_ratio", er, [f"s165_{suffix}_499"]),
        ("yield_measurement_basis", None, [f"s165_{suffix}_499"]),
    ])

add("scheme166_first_cross_coupling", (28,), [
    ("s166_500", "reactant", "500", "chiral 1,3-diethynylallene coupling unit", []), ("s166_501", "reactant", "501", "iodo-N,N-dimethylaniline", []),
    ("s166_Pd", "catalyst", None, "PdCl2(PPh3)2", []), ("s166_CuI", "catalyst", None, "copper(I) iodide", []),
    ("s166_iPr2NH", "solvent", None, "diisopropylamine", []), ("s166_THF", "solvent", None, "tetrahydrofuran", []),
    ("s166_502", "product", "502", "aryl-coupled allenophane precursor", []),
], [("cross_coupling", ["s166_500", "s166_501", "s166_Pd", "s166_CuI", "s166_iPr2NH", "s166_THF", "s166_502"], [("temperature", q(-40, "°C"))])], [
    ("reported_yield", q(71, "%"), ["s166_502"]), ("yield_measurement_basis", None, ["s166_502"]),
])

add("scheme166_desilylation", (28,), [
    ("s166b_502", "reactant", "502", "TIPS-protected aryl-coupled allenophane precursor", []),
    ("s166b_TBAF", "reagent", None, "tetrabutylammonium fluoride", []), ("s166b_THF", "solvent", None, "tetrahydrofuran", []),
    ("s166b_product", "product", None, "terminal-alkyne deprotected derivative of 502", []),
], [("desilylation", ["s166b_502", "s166b_TBAF", "s166b_THF", "s166b_product"], [])], [
    ("reported_yield", q(82, "%"), ["s166b_product"]), ("yield_measurement_basis", None, ["s166b_product"]),
])

add("scheme166_second_cross_coupling", (28,), [
    ("s166c_deprotected", "reactant", None, "terminal-alkyne derivative of 502", []),
    ("s166c_unspecified_partner", "reactant", None, "second coupling partner not redrawn in this arrow", []),
    ("s166c_Pd", "catalyst", None, "PdCl2(PPh3)2", []), ("s166c_CuI", "catalyst", None, "copper(I) iodide", []),
    ("s166c_iPr2NH", "solvent", None, "diisopropylamine", []), ("s166c_THF", "solvent", None, "tetrahydrofuran", []),
    ("s166c_503", "product", "503", "extended alleno-acetylenic chromophore precursor", []),
], [("cross_coupling", ["s166c_deprotected", "s166c_unspecified_partner", "s166c_Pd", "s166c_CuI", "s166c_iPr2NH", "s166c_THF", "s166c_503"], [("temperature", q(50, "°C"))])], [
    ("reported_yield", q(19, "%"), ["s166c_503"]), ("yield_measurement_basis", None, ["s166c_503"]),
], notes=["The compact Scheme 166 arrow does not redraw or label the second coupling partner; it remains an unresolved reactant rather than being inferred."],
    unresolved=["Identity and amount of the second coupling partner are not explicit at this arrow.", "Time and yield basis are absent.", "Original paper/SI was not supplied; structures remain unverified."])

add("scheme166_tcne_adduct", (28,), [
    ("s166d_503", "reactant", "503", "extended alleno-acetylenic chromophore precursor", []), ("s166d_TCNE", "reactant", None, "tetracyanoethylene", []),
    ("s166d_CDCl3", "solvent", None, "deuterated chloroform", []), ("s166d_504", "product", "504", "TCNE-derived alleno-acetylenic chromophore", []),
], [("TCNE_addition", ["s166d_503", "s166d_TCNE", "s166d_CDCl3", "s166d_504"], [("temperature", q(20, "°C"))])], [
    ("reported_yield", q(86, "%"), ["s166d_504"]), ("yield_measurement_basis", None, ["s166d_504"]),
])

# Page 29, Scheme 167.
add("scheme167_oxidative_homodimerization", (29,), [
    ("s167_505", "reactant", "505", "enantiomerically pure (P)-DEA derivative", []),
    ("s167_Pd", "catalyst", None, "PdCl2(PPh3)2", []), ("s167_CuI", "catalyst", None, "copper(I) iodide", []),
    ("s167_TMEDA", "reagent", None, "TMEDA", []), ("s167_toluene", "solvent", None, "toluene", []),
    ("s167_506", "product", "506", "linear (P,P)-alleno-acetylenic dimer", []),
], [("oxidative_homocoupling", ["s167_505", "s167_Pd", "s167_CuI", "s167_TMEDA", "s167_toluene", "s167_506"], [("temperature", q(50, "°C")), ("time", q(24, "h"))])], [
    ("reported_yield", q(99, "%"), ["s167_506"]), ("yield_measurement_basis", None, ["s167_506"]),
])

add("scheme167_deprotection", (29,), [
    ("s167b_506", "reactant", "506", "protected linear (P,P)-alleno-acetylenic dimer", []),
    ("s167b_NaOH", "reagent", None, "sodium hydroxide", []), ("s167b_toluene", "solvent", None, "toluene", []),
    ("s167b_507", "product", "507", "deprotected linear (P,P)-alleno-acetylenic dimer", []),
], [("deprotection", ["s167b_506", "s167b_NaOH", "s167b_toluene", "s167b_507"], [("temperature", q(90, "°C")), ("time", q(10, "h"))])], [
    ("reported_yield", q(65, "%"), ["s167b_507"]), ("yield_measurement_basis", None, ["s167b_507"]),
])

add("scheme167_macrocyclization", (29,), [
    ("s167c_507", "reactant", "507", "deprotected linear (P,P)-alleno-acetylenic dimer", []),
    ("s167c_CuCl", "catalyst", None, "copper(I) chloride", []), ("s167c_CuCl2", "catalyst", None, "copper(II) chloride", []),
    ("s167c_pyridine", "solvent", None, "pyridine", []), ("s167c_508", "product", "508", "(P,P,P,P)-alleno-acetylenic macrocycle", []),
], [("one_pot_dimerization_cyclization", ["s167c_507", "s167c_CuCl", "s167c_CuCl2", "s167c_pyridine", "s167c_508"], [("temperature", "r.t.")])], [
    ("reported_yield", q(68, "%"), ["s167c_508"]), ("yield_measurement_basis", None, ["s167c_508"]),
])

add("scheme167_linear_oligomerization", (29,), [
    ("s167d_507", "reactant", "507", "deprotected linear (P,P)-alleno-acetylenic dimer", []),
    ("s167d_509", "product", "509", "linear enantiopure alleno-acetylenic oligomer", []),
], [("repeated_dimerization_deprotection", ["s167d_507", "s167d_509"], [])], notes=["The review states that repeating the dimerization-deprotection sequence without cyclization furnishes oligomers 509; Scheme 167 gives no independent conditions or yield at this arrow."],
    unresolved=["Iteration count, precise conditions, oligomer distribution, and yield are not stated.", "Original paper/SI was not supplied; structures remain unverified."])

OUT.write_text(json.dumps(R, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"output": str(OUT), "records": len(R)}, ensure_ascii=False))
