#!/usr/bin/env python3
"""Build machine extraction records for Yu & Ma, ChemComm 2011, PDF pages 19-24."""
import json
from pathlib import Path

DOC = "doc_e77fa99a0ade23d1"
OUT = Path(__file__).with_name("records_pages_0019_0024.json")


def ev(*pages):
    out = []
    for page in pages:
        out += [f"{DOC}:page{page}:image", f"{DOC}:page{page}:text"]
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


def fld(name, value, evidence, targets=None):
    item = {"name": name, "fact": fact(value, evidence)}
    if targets:
        item["target_entity_ids"] = targets
    return item


def part(entity_id, role, label, name, evidence, amounts=None, smiles=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence),
        "smiles": fact(smiles, evidence),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": [fld(n, v, evidence) for n, v in (amounts or [])],
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
        "conditions": [fld(n, v, evidence) for n, v in conditions],
    }


DEFAULT_UNRESOLVED = [
    "This Feature Article summarizes cited prior literature rather than reporting a full batch procedure by the review authors.",
    "Scale, atmosphere, workup, purification, and yield measurement basis are not fully reported unless explicitly shown.",
    "Generic R-group structures and compact stereochemical drawings remain machine-unverified; unsupported SMILES are null.",
    "Supporting Information was not supplied or explicitly associated.",
]


R = []


def add(rid, kind, pages, participants, steps, outcomes=(), notes=(), unresolved=None):
    evidence = ev(*pages)
    R.append({
        "record_id": f"{DOC}:{rid}",
        "document_id": DOC,
        "source_reaction_id": rid,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": evidence,
        "participants": [
            part(eid, role, label, name, evidence, amounts, smiles)
            for eid, role, label, name, amounts, smiles in participants
        ],
        "steps": [step(sid, ids, evidence, conditions) for sid, ids, conditions in steps],
        "outcomes": [fld(name, value, evidence, targets) for name, value, targets in outcomes],
        "notes": [fact(note, evidence) for note in notes],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": DEFAULT_UNRESOLVED if unresolved is None else unresolved,
        },
    })


# Page 19 drawings: Schemes 110-113.
add("scheme110_n_oxy_aza_cope_rearrangement", "literature_example", (19,), [
    ("s110_320", "reactant", "320", "Z-configured N-oxy-3-aza-Cope substrate", [], None),
    ("s110_321", "product", "321", "oxime allene", [], None),
], [("thermal_rearrangement", ["s110_320", "s110_321"], [
    ("temperature", q(minimum=-20, maximum=70, unit="°C", raw_text="-20 to 70 °C")),
])], [
    ("reported_yield", q(minimum=27, maximum=98, unit="%", raw_text="27-98%"), ["s110_321"]),
    ("yield_measurement_basis", None, ["s110_321"]),
], notes=["The adjacent prose states that Z configuration of the enaminic double bond is critical."])

add("scheme111_rhodium_isomerization_claisen_reduction", "literature_example", (19,), [
    ("s111_322", "reactant", "322", "allyl propargyl ether", [], None),
    ("s111_Rh", "catalyst", None, "[Rh(cod)2]BF4", [("catalyst_loading", q(5, "mol%"))], None),
    ("s111_dppf", "catalyst", None, "dppf", [], None),
    ("s111_CH2Cl2", "solvent", None, "dichloromethane", [], "ClCCl"),
    ("s111_NaBH4", "reagent", None, "sodium borohydride", [], "[BH4-].[Na+]"),
    ("s111_MeOH", "solvent", None, "methanol", [], "CO"),
    ("s111_323", "product", "323", "reduced allenic alcohol", [], None),
], [
    ("isomerization_claisen", ["s111_322", "s111_Rh", "s111_dppf", "s111_CH2Cl2"], [
        ("temperature", "r.t."), ("time", q(minimum=15, maximum=72, unit="h", raw_text="15-72 h")),
    ]),
    ("aldehyde_reduction", ["s111_322", "s111_NaBH4", "s111_MeOH", "s111_323"], [
        ("temperature", "r.t."), ("time", q(1, "h")),
    ]),
], [
    ("reported_yield", q(minimum=49, maximum=81, unit="%", raw_text="49-81%"), ["s111_323"]),
    ("yield_measurement_basis", None, ["s111_323"]),
], notes=["The review explains that unstable allenic aldehydes are reduced in situ; 80 °C instead favors 4,5-dienals, but no independent row is drawn here."])

add("scheme112_keteniminium_claisen_lactone", "literature_example", (19,), [
    ("s112_324", "reactant", "324", "amide-bearing propargyl ether", [], None),
    ("s112_Tf2O", "reagent", None, "triflic anhydride", [], None),
    ("s112_collidine", "reagent", None, "collidine", [], None),
    ("s112_DCM", "solvent", None, "dichloromethane", [], "ClCCl"),
    ("s112_328", "product", "328", "alpha-allenyl lactone", [], None),
], [("keteniminium_formation_claisen_hydrolysis", ["s112_324", "s112_Tf2O", "s112_collidine", "s112_DCM", "s112_328"], [
    ("temperature", q(120, "°C")), ("operation", "microwave irradiation"),
])], [
    ("reported_yield", q(minimum=40, maximum=76, unit="%", raw_text="40-76%"), ["s112_328"]),
    ("yield_measurement_basis", None, ["s112_328"]),
], notes=["Structures 325-327 are proposed keteniminium/rearrangement intermediates, not isolated products."])

add("scheme113_palladium_phosphorimidate_rearrangement", "literature_example", (19,), [
    ("s113_329", "reactant", "329", "propargylic phosphorimidate", [], None),
    ("s113_Pd", "catalyst", None, "PdCl2(CH3CN)2", [("catalyst_loading", q(3, "mol%"))], None),
    ("s113_DCM", "solvent", None, "dichloromethane", [], "ClCCl"),
    ("s113_330", "product", "330", "allenamide", [], None),
], [("palladium_catalyzed_three_three_rearrangement", ["s113_329", "s113_Pd", "s113_DCM", "s113_330"], [
    ("temperature", q(25, "°C")),
])], [
    ("reported_yield", q(minimum=58, maximum=76, unit="%", raw_text="58-76%"), ["s113_330"]),
    ("yield_measurement_basis", None, ["s113_330"]),
])

# Pages 19-20: Schemes 114-123.
add("scheme114_gold_alpha_allenone_formation", "literature_example", (19, 20), [
    ("s114_331", "reactant", "331", "acetoxy diyne", [], None),
    ("s114_Au", "catalyst", None, "AuCl(PPh3)", [("combined_catalyst_loading", q(6, "mol%"))], None),
    ("s114_AgSbF6", "catalyst", None, "silver hexafluoroantimonate", [("combined_catalyst_loading", q(6, "mol%"))], None),
    ("s114_DCM", "solvent", None, "dichloromethane", [], "ClCCl"),
    ("s114_water", "reagent", None, "water", [], "O"),
    ("s114_335", "product", "335", "alpha-allenone", [], None),
], [("gold_catalyzed_rearrangement", ["s114_331", "s114_Au", "s114_AgSbF6", "s114_DCM", "s114_water", "s114_335"], [
    ("temperature", q(0, "°C")), ("time", q(minimum=5, maximum=15, unit="min", raw_text="5-15 min")),
    ("solvent_composition", "DCM/water"),
])], [
    ("reported_yield", q(minimum=55, maximum=85, unit="%", raw_text="55-85%"), ["s114_335"]),
    ("yield_measurement_basis", None, ["s114_335"]),
], notes=["Intermediates 332-334 are proposed. The review states that keeping reaction time below 15 min is critical because further Au(I) activation produces cyclopentenones."])

add("scheme115_two_three_sigma_rearrangement_general", "general_scheme", (19, 20), [
    ("s115_3VIII", "reactant", "3-VIII", "heteroatom-substituted propargylic substrate", [], None),
    ("s115_3VIV", "product", "3-VIV", "heteroatom-substituted allene", [], None),
], [("two_three_sigmatropic_rearrangement", ["s115_3VIII", "s115_3VIV"], [])],
    notes=["Scheme 115 is a generic [2,3]-sigma rearrangement used to introduce heteroatom substituents."],
    unresolved=["Generic X, Y and R groups prevent unique structures and conditions.", "This is a general reaction scheme, not a batch experiment."])

add("scheme116_phosphinite_rearrangement", "literature_example", (19, 20), [
    ("s116_336", "reactant", "336", "propargyl alcohol", [], None),
    ("s116_337", "reactant", "337", "phosphite chloride", [], None),
    ("s116_THF", "solvent", None, "tetrahydrofuran", [], "C1CCOC1"),
    ("s116_Et3N", "reagent", None, "triethylamine", [], "CCN(CC)CC"),
    ("s116_339", "product", "339", "allenic phosphonate", [], None),
], [("condensation_and_rearrangement", ["s116_336", "s116_337", "s116_THF", "s116_Et3N", "s116_339"], [
    ("temperature", "reflux"),
])], [
    ("reported_yield", q(minimum=70, maximum=80, unit="%", raw_text="70-80%"), ["s116_339"]),
    ("yield_measurement_basis", None, ["s116_339"]),
], notes=["Alkynyl phosphinite 338 is depicted as an intermediate."])

add("scheme117_oxazaphospholane_rearrangement", "literature_example", (19, 20), [
    ("s117_340", "reactant", "340", "(d)-pseudoephedrine-derived phosphorus reagent", [], None),
    ("s117_341", "reactant", "341", "propargyl alcohol", [], None),
    ("s117_343", "product", "343", "2-allene-substituted 1,3,2-oxazaphospholane", [], None),
], [("phosphite_formation_and_rearrangement", ["s117_340", "s117_341", "s117_343"], [
    ("temperature", q(minimum=110, maximum=120, unit="°C", raw_text="110-120 °C")),
])], [
    ("reported_yield", q(minimum=75, maximum=84, unit="%", raw_text="75-84%"), ["s117_343"]),
    ("yield_measurement_basis", None, ["s117_343"]),
], notes=["Acetylenic phosphite 342 is a proposed intermediate."])

add("scheme118_sulfimide_amination_rearrangement", "literature_example", (19, 20), [
    ("s118_344", "reactant", "344", "enantioenriched propargylic sulfimide", [], None),
    ("s118_345", "reactant", "345", "CbzNHOTf", [], None),
    ("s118_CH2Cl2", "solvent", None, "dichloromethane", [], "ClCCl"),
    ("s118_NaHCO3", "reagent", None, "sodium bicarbonate", [], "O=C([O-])O.[Na+]"),
    ("s118_347", "product", "347", "chiral allenamide", [], None),
], [
    ("amination", ["s118_344", "s118_345", "s118_CH2Cl2"], []),
    ("rearrangement", ["s118_344", "s118_NaHCO3", "s118_347"], []),
], [
    ("reported_yield", q(minimum=71, maximum=83, unit="%", raw_text="71-83%"), ["s118_347"]),
    ("enantiomeric_excess", q(minimum=81, maximum=89, unit="%", raw_text="81-89% ee"), ["s118_347"]),
    ("yield_measurement_basis", None, ["s118_347"]),
], notes=["Sulfonium-like structure 346 is a proposed intermediate."])

add("scheme119_double_asymmetric_sulfonium_rearrangement", "literature_example", (19, 20), [
    ("s119_348", "reactant", "348", "diazo compound bearing chiral camphor sultam auxiliary", [], None),
    ("s119_349", "reactant", "349", "propargyl aryl sulfide", [], None),
    ("s119_Cu", "catalyst", None, "[Cu(MeCN)4]PF6", [("catalyst_loading", q(20, "mol%"))], None),
    ("s119_350", "catalyst", "350", "chiral bis-imine ligand", [("ligand_loading", q(22, "mol%"))], None),
    ("s119_CH2Cl2", "solvent", None, "dichloromethane", [], "ClCCl"),
    ("s119_LiAlH4", "reagent", None, "lithium aluminium hydride", [], None),
    ("s119_THF", "solvent", None, "tetrahydrofuran", [], "C1CCOC1"),
    ("s119_351", "product", "351", "enantioenriched 3,4-allenol", [], None),
], [
    ("sulfonium_ylide_rearrangement", ["s119_348", "s119_349", "s119_Cu", "s119_350", "s119_CH2Cl2"], [
        ("temperature", q(minimum=0, maximum=20, unit="°C", raw_text="0 °C to rt")),
    ]),
    ("auxiliary_reduction", ["s119_348", "s119_LiAlH4", "s119_THF", "s119_351"], [
        ("temperature", q(minimum=0, maximum=20, unit="°C", raw_text="0 °C to rt")), ("time", q(2, "h")),
    ]),
], [
    ("reported_yield", q(minimum=39, maximum=95, unit="%", raw_text="39-95%"), ["s119_351"]),
    ("enantiomeric_excess", q(minimum=82, maximum=96, unit="%", raw_text="82-96% ee"), ["s119_351"]),
    ("yield_measurement_basis", None, ["s119_351"]),
])

add("scheme120_silver_allenic_sulfone", "literature_example", (19, 20), [
    ("s120_352", "reactant", "352", "propargylic sulfinate", [], None),
    ("s120_AgSbF6", "catalyst", None, "silver hexafluoroantimonate", [("catalyst_loading", q(2, "mol%"))], None),
    ("s120_CH3NO2", "solvent", None, "nitromethane", [], "C[N+](=O)[O-]"),
    ("s120_353", "product", "353", "allenic sulfone", [], None),
], [("silver_catalyzed_rearrangement", ["s120_352", "s120_AgSbF6", "s120_CH3NO2", "s120_353"], [
    ("temperature", "r.t."), ("time", q(2, "min")),
])], [
    ("reported_yield", q(minimum=96, maximum=99, unit="%", raw_text="96-99%"), ["s120_353"]),
    ("yield_measurement_basis", None, ["s120_353"]),
])

add("scheme121_silver_vinylidenecyclopentane", "literature_example", (19, 20), [
    ("s121_354", "reactant", "354", "allyl-tethered propargyl alcohol", [], None),
    ("s121_AgSbF6", "catalyst", None, "silver hexafluoroantimonate", [("catalyst_loading", q(10, "mol%"))], None),
    ("s121_water", "reagent", None, "water (trace amount required)", [], "O"),
    ("s121_CH2Cl2", "solvent", None, "dichloromethane", [], "ClCCl"),
    ("s121_355", "product", "355", "vinylidenecyclopentane", [], None),
], [("silver_mediated_cycloisomerization", ["s121_354", "s121_AgSbF6", "s121_water", "s121_CH2Cl2", "s121_355"], [
    ("temperature", q(15, "°C")),
])], [
    ("reported_yield", q(minimum=54, maximum=94, unit="%", raw_text="54-94%"), ["s121_355"]),
    ("yield_measurement_basis", None, ["s121_355"]),
], notes=["The adjacent prose explicitly states that trace water is necessary; no numeric water amount is reported. Structure 356 is mechanistic."])

add("scheme122_gold_cycloisomerization_product_mixture", "literature_example", (19, 20), [
    ("s122_357", "reactant", "357", "1,6-enyne", [], None),
    ("s122_358", "catalyst", "358", "cationic gold complex", [("catalyst_loading", q(2, "mol%"))], None),
    ("s122_CH2Cl2", "solvent", None, "dichloromethane", [], "ClCCl"),
    ("s122_360", "product", "360", "vinylidenecyclopentane", [], None),
    ("s122_361", "product", "361", "cyclized side product", [], None),
], [("gold_catalyzed_cycloisomerization", ["s122_357", "s122_358", "s122_CH2Cl2", "s122_360", "s122_361"], [
    ("temperature", "r.t."), ("time", q(3, "h")),
])], [
    ("combined_reported_yield", q(81, "%"), ["s122_360", "s122_361"]),
    ("product_ratio_360_361", "3:2", ["s122_360", "s122_361"]),
    ("yield_measurement_basis", None, ["s122_360", "s122_361"]),
], notes=["Intermediate 359 is proposed. The prose notes that side reactions make this method less predictable."])

add("scheme123_dms_allene_general", "mechanism", (19, 20), [
    ("s123_4I", "reactant", "4-I", "geminal dihalocyclopropane", [], None),
    ("s123_RLi", "reactant", None, "alkyllithium reagent", [], None),
    ("s123_4III", "product", "4-III", "allene", [], None),
], [("doering_moore_skattebol_rearrangement", ["s123_4I", "s123_RLi", "s123_4III"], [
    ("temperature", q(-78, "°C")),
])], notes=["Scheme 123 is the general Doering-Moore-Skattebøl reaction; 4-II is a proposed carbenoid-like intermediate."],
    unresolved=["Generic X and R groups prevent unique structures and reagent identity.", "This is a general named-reaction mechanism, not a batch experiment."])

# Pages 20-22: Schemes 124-135.
add("scheme124_sulfoxide_magnesium_exchange_allenol", "literature_example", (19, 20, 21), [
    ("s124_362", "reactant", "362", "1-(p-tolylsulfoxide)-1-chlorocyclopropane derivative", [], None),
    ("s124_iPrMgCl", "reagent", None, "isopropylmagnesium chloride", [("equivalents", q(minimum=5, maximum=10, unit="equiv", raw_text="5-10 equiv"))], None),
    ("s124_toluene", "solvent", None, "toluene", [], "Cc1ccccc1"),
    ("s124_364", "product", "364", "alpha-allenol", [], None),
], [("sulfoxide_magnesium_exchange_rearrangement", ["s124_362", "s124_iPrMgCl", "s124_toluene", "s124_364"], [
    ("temperature", q(0, "°C")), ("time", q(30, "min")),
])], [
    ("reported_yield", q(minimum=35, maximum=88, unit="%", raw_text="35-88%"), ["s124_364"]),
    ("yield_measurement_basis", None, ["s124_364"]),
], notes=["Cyclopropylmagnesium carbenoid 363 is proposed."])

add("scheme125_lithium_amide_alkynylcyclopropane", "literature_example", (20, 21), [
    ("s125_365", "reactant", "365", "alkynylchlorocyclopropane", [], None),
    ("s125_RNHLi", "reactant", None, "lithium monoalkylamide", [], None),
    ("s125_THF", "solvent", None, "tetrahydrofuran", [], "C1CCOC1"),
    ("s125_369", "product", "369", "substituted allene", [], None),
], [("alkynylcyclopropene_rearrangement", ["s125_365", "s125_RNHLi", "s125_THF", "s125_369"], [
    ("temperature", q(20, "°C")),
])], [
    ("reported_yield", q(minimum=40, maximum=50, unit="%", raw_text="40-50%"), ["s125_369"]),
    ("yield_measurement_basis", None, ["s125_369"]),
], notes=["Intermediates 366-368 are proposed; the 40-50% range is stated in page-20 prose."])

add("scheme126_organocuprate_cyclopropane_opening", "literature_example", (20, 21), [
    ("s126_370", "reactant", "370", "propargylcyclopropane-1,1-diester", [], None),
    ("s126_cuprate", "reactant", None, "higher-order organocuprate R3Cu(CN)X2", [], None),
    ("s126_Et2O", "solvent", None, "diethyl ether", [], "CCOCC"),
    ("s126_371", "product", "371", "beta-malonate-tethered allene", [], None),
], [("regioselective_ring_opening", ["s126_370", "s126_cuprate", "s126_Et2O", "s126_371"], [
    ("temperature", "r.t."),
])], [
    ("reported_yield", q(minimum=62, maximum=92, unit="%", raw_text="62-92%"), ["s126_371"]),
    ("yield_measurement_basis", None, ["s126_371"]),
], notes=["The review states that higher-order cuprates are critical and chiral substrates can give enantioenriched allenes."])

add("scheme127_silver_mcp_ring_expansion", "literature_example", (21, 22), [
    ("s127_372", "reactant", "372", "methylenecyclopropane-tethered propargyl alcohol", [], None),
    ("s127_AgOTf", "catalyst", None, "silver triflate", [("catalyst_loading", q(5, "mol%"))], None),
    ("s127_water", "reagent", None, "water", [("equivalents", q(0.5, "equiv"))], "O"),
    ("s127_CH2Cl2", "solvent", None, "dichloromethane", [], "ClCCl"),
    ("s127_376", "product", "376", "polysubstituted allenylcyclobutanol", [], None),
], [("silver_catalyzed_ring_expansion", ["s127_372", "s127_AgOTf", "s127_water", "s127_CH2Cl2", "s127_376"], [
    ("temperature", "r.t."), ("time", q(6, "h")),
])], [
    ("reported_yield", q(minimum=20, maximum=56, unit="%", raw_text="20-56%"), ["s127_376"]),
    ("yield_measurement_basis", None, ["s127_376"]),
], notes=["Structures 373-375 are proposed cationic intermediates."])

add("scheme128_allene_cross_coupling_general", "general_scheme", (21, 22), [
    ("s128_5I", "reactant", "5-I", "metalated or halogenated allene", [], None),
    ("s128_5II", "reactant", "5-II", "electrophile or organometallic coupling partner", [], None),
    ("s128_catalyst", "catalyst", None, "transition-metal catalyst", [], None),
    ("s128_5III", "product", "5-III", "functionalized allene", [], None),
], [("cross_coupling", ["s128_5I", "s128_5II", "s128_catalyst", "s128_5III"], [])],
    unresolved=["Generic X/M, M/X and R groups prevent unique structures and conditions.", "This is a general scheme, not a batch experiment."])

add("scheme129_cutc_allenic_sulfonamide", "literature_example", (21, 22), [
    ("s129_377", "reactant", "377", "bromoallene", [], None),
    ("s129_378", "reactant", "378", "allyl- or aryl-substituted sulfonamide", [], None),
    ("s129_CuTC", "catalyst", None, "copper(I) thiophene-2-carboxylate", [("catalyst_loading", q(15, "mol%"))], None),
    ("s129_DMEDA", "catalyst", None, "DMEDA", [("ligand_loading", q(30, "mol%"))], None),
    ("s129_Cs2CO3", "reagent", None, "cesium carbonate", [], None),
    ("s129_toluene", "solvent", None, "toluene", [], "Cc1ccccc1"),
    ("s129_379", "product", "379", "allenic sulfonamide", [], None),
], [("copper_catalyzed_coupling", ["s129_377", "s129_378", "s129_CuTC", "s129_DMEDA", "s129_Cs2CO3", "s129_toluene", "s129_379"], [
    ("temperature", q(80, "°C")), ("time", q(24, "h")),
])], [
    ("reported_yield", q(minimum=20, maximum=89, unit="%", raw_text="20-89%"), ["s129_379"]),
    ("yield_measurement_basis", None, ["s129_379"]),
])

add("scheme130_propargylzinc_allenyne_coupling", "literature_example", (21, 22), [
    ("s130_380", "reactant", "380", "enantioenriched allenyl bromide", [("enantiomeric_excess", q(95, "%"))], None),
    ("s130_propargylic_ether", "reactant", None, "1-triethylsiloxyl-2-propyne", [], None),
    ("s130_nBuLi", "reagent", None, "n-butyllithium", [], None),
    ("s130_THF", "solvent", None, "tetrahydrofuran", [], "C1CCOC1"),
    ("s130_ZnBr2", "reagent", None, "anhydrous zinc bromide", [], None),
    ("s130_Pd", "catalyst", None, "Pd(PPh3)4", [], None),
    ("s130_381", "product", "381", "allenyne", [], None),
], [
    ("propargylzinc_preparation", ["s130_propargylic_ether", "s130_nBuLi", "s130_THF", "s130_ZnBr2"], [
        ("temperature", q(-78, "°C")),
    ]),
    ("cross_coupling", ["s130_380", "s130_propargylic_ether", "s130_Pd", "s130_THF", "s130_381"], [
        ("temperature", q(-78, "°C")), ("time", q(2, "h")),
    ]),
    ("warming", ["s130_380", "s130_381"], [
        ("temperature", q(0, "°C")), ("time", q(2, "h")),
    ]),
], [
    ("reported_yield", q(90, "%"), ["s130_381"]),
    ("enantiomeric_excess", q(63, "%"), ["s130_381"]),
    ("yield_measurement_basis", None, ["s130_381"]),
], notes=["The review states that axial configuration is inverted in this transformation."])

add("scheme131_allenylzinc_cross_coupling", "literature_example", (21, 22), [
    ("s131_382", "reactant", "382", "1-aryl-3-alkylpropadiene", [], None),
    ("s131_LDA", "reagent", None, "LDA", [("equivalents", q(2, "equiv"))], None),
    ("s131_ZnBr2", "reagent", None, "zinc bromide", [("equivalents", q(4, "equiv"))], None),
    ("s131_RI", "reactant", None, "aryl or alkenyl iodide", [], None),
    ("s131_Pd", "catalyst", None, "Pd(PPh3)4", [("catalyst_loading", q(5, "mol%"))], None),
    ("s131_383", "product", "383", "trisubstituted allene", [], None),
], [
    ("lithiation", ["s131_382", "s131_LDA"], []),
    ("transmetalation", ["s131_382", "s131_ZnBr2"], []),
    ("cross_coupling", ["s131_382", "s131_RI", "s131_Pd", "s131_383"], []),
], [
    ("reported_yield", q(minimum=56, maximum=92, unit="%", raw_text="56-92%"), ["s131_383"]),
    ("regioselectivity", "up to >99/1", ["s131_383"]),
    ("yield_measurement_basis", None, ["s131_383"]),
])

add("scheme132_stereocontrolled_suzuki_allene", "literature_example", (21, 22), [
    ("s132_384", "reactant", "384", "enantioenriched allenyl iodide", [], None),
    ("s132_385", "reactant", "385", "phenylboronic acid", [], "OB(O)c1ccccc1"),
    ("s132_Pd", "catalyst", None, "Pd2(dba)3", [], None),
    ("s132_XPhos", "catalyst", None, "XPhos", [], None),
    ("s132_Ag2O", "reagent", None, "silver(I) oxide", [], None),
    ("s132_THF", "solvent", None, "tetrahydrofuran", [], "C1CCOC1"),
    ("s132_water", "solvent", None, "water", [], "O"),
    ("s132_386", "product", "386", "phenyl-substituted chiral allene", [], None),
], [("stereocontrolled_coupling", ["s132_384", "s132_385", "s132_Pd", "s132_XPhos", "s132_Ag2O", "s132_THF", "s132_water", "s132_386"], [
    ("temperature", q(23, "°C")), ("solvent_ratio", "THF/H2O 10:1"),
])], [
    ("chirality_transfer", "high", ["s132_386"]),
    ("reported_yield", None, ["s132_386"]),
], notes=["Scheme 132 reports high chirality transfer but no numeric yield or ee."])

add("scheme133_asymmetric_bishomoallenylation", "literature_example", (21, 22), [
    ("s133_387", "reactant", "387", "2,3-allenyl phosphate", [], None),
    ("s133_388", "reactant", "388", "benzylamine", [], "NCC1=CC=CC=C1"),
    ("s133_Pd", "catalyst", None, "Pd2(dba)3·CHCl3", [("catalyst_loading", q(2.5, "mol%"))], None),
    ("s133_ligand", "catalyst", None, "(R)-SEGPHOS or (R)-DTBM-SEGPHOS", [("ligand_loading", q(5.0, "mol%"))], None),
    ("s133_THF", "solvent", None, "tetrahydrofuran", [], "C1CCOC1"),
    ("s133_RR389", "product", "(R,R)-389", "bis(homoallenyl)amine diastereomer", [], None),
    ("s133_RS389", "product", "(R,S)-389", "bis(homoallenyl)amine diastereomer", [], None),
], [("one_pot_bishomoallenylation", ["s133_387", "s133_388", "s133_Pd", "s133_ligand", "s133_THF", "s133_RR389", "s133_RS389"], [
    ("temperature", q(20, "°C")),
])], [
    ("combined_reported_yield", q(minimum=52, maximum=78, unit="%", raw_text="52-78%"), ["s133_RR389", "s133_RS389"]),
    ("diastereomeric_ratio", "73:27 to 85:15 dr", ["s133_RR389", "s133_RS389"]),
    ("enantiomeric_excess", q(minimum=75, maximum=95, unit="%", raw_text="75-95% ee"), ["s133_RR389", "s133_RS389"]),
    ("yield_measurement_basis", None, ["s133_RR389", "s133_RS389"]),
])

add("scheme134_pd_diapho_allenylic_alkylation", "literature_example", (21, 22), [
    ("s134_390", "reactant", "390", "2,3-allenyl acetate", [], None),
    ("s134_391", "reactant", "391", "alpha-substituted dimethyl malonate", [], None),
    ("s134_PdOAc2", "catalyst", None, "palladium(II) acetate", [("catalyst_loading", q(5, "mol%"))], None),
    ("s134_392", "catalyst", "(S,Rp)-L 392", "chiral Pd-DIAPHOX ligand", [("ligand_loading", q(10, "mol%"))], None),
    ("s134_LiOAc", "reagent", None, "lithium acetate", [("loading", q(20, "mol%"))], None),
    ("s134_BSA", "reagent", None, "BSA", [("equivalents", q(3, "equiv"))], None),
    ("s134_CH3CN", "solvent", None, "acetonitrile", [], "CC#N"),
    ("s134_393", "product", "(R)-393", "chiral substituted allene", [], None),
], [("asymmetric_allenylic_alkylation", ["s134_390", "s134_391", "s134_PdOAc2", "s134_392", "s134_LiOAc", "s134_BSA", "s134_CH3CN", "s134_393"], [
    ("temperature", q(4, "°C")),
])], [
    ("reported_yield", q(minimum=86, maximum=99, unit="%", raw_text="86-99%"), ["s134_393"]),
    ("enantiomeric_excess", q(minimum=66, maximum=99, unit="%", raw_text="66-99% ee"), ["s134_393"]),
    ("yield_measurement_basis", None, ["s134_393"]),
])

add("scheme135_double_allylmagnesium_addition_scope", "literature_example", (21, 22), [
    ("s135a_394", "reactant", "394", "2,3-allenoate", [], None),
    ("s135a_395", "reactant", "395", "allylmagnesium chloride", [], None),
    ("s135a_THF", "solvent", None, "tetrahydrofuran", [], "C1CCOC1"),
    ("s135a_396", "product", "396", "tertiary alpha-allenol", [], None),
], [("double_one_two_addition", ["s135a_394", "s135a_395", "s135a_THF", "s135a_396"], [
    ("temperature", "r.t."), ("time", q(minimum=2, maximum=35, unit="min", raw_text="2-35 min")),
])], [
    ("reported_yield", q(minimum=60, maximum=100, unit="%", raw_text="60-100%"), ["s135a_396"]),
    ("yield_measurement_basis", None, ["s135a_396"]),
])

add("scheme135_chiral_double_allylmagnesium_addition", "literature_example", (21, 22), [
    ("s135b_397", "reactant", "397", "optically active 2,3-allenoate", [("enantiomeric_excess", q(98, "%"))], None),
    ("s135b_395", "reactant", "395", "allylmagnesium chloride", [], None),
    ("s135b_THF", "solvent", None, "tetrahydrofuran", [], "C1CCOC1"),
    ("s135b_398", "product", "398", "optically active tertiary alpha-allenol", [], None),
], [("double_one_two_addition", ["s135b_397", "s135b_395", "s135b_THF", "s135b_398"], [
    ("temperature", "r.t."), ("time", q(2, "min")),
])], [
    ("reported_yield", q(90, "%"), ["s135b_398"]),
    ("enantiomeric_excess", q(97, "%"), ["s135b_398"]),
    ("yield_measurement_basis", None, ["s135b_398"]),
])

# Pages 21-24: Schemes 136-145.
add("scheme136_perfluoroalkyl_allenyl_ketone", "literature_example", (21, 23), [
    ("s136_399", "reactant", "399", "2,3-allenoate", [], None),
    ("s136_400", "reactant", "400", "perfluoroalkyl Grignard reagent RfMgX", [], None),
    ("s136_Et2O", "solvent", None, "diethyl ether", [], "CCOCC"),
    ("s136_401", "product", "401", "perfluoroalkyl allenyl ketone", [], None),
], [("grignard_addition", ["s136_399", "s136_400", "s136_Et2O", "s136_401"], [
    ("temperature", q(minimum=-80, maximum=-70, unit="°C", raw_text="-80 °C to -70 °C")),
    ("time", q(minimum=30, maximum=40, unit="min", raw_text="30-40 min")),
]), ("hold", ["s136_399", "s136_401"], [
    ("temperature", q(-70, "°C")),
])], [
    ("reported_yield", q(minimum=53, maximum=85, unit="%", raw_text="53-85%"), ["s136_401"]),
    ("yield_measurement_basis", None, ["s136_401"]),
], notes=["The review states that the perfluoroalkyl ketone does not undergo further RfMgX addition."])

add("scheme137_tBAF_allenoate_aldehyde_addition", "literature_example", (22, 23), [
    ("s137_402", "reactant", "402", "2,3-allenoate", [], None),
    ("s137_403", "reactant", "403", "aryl aldehyde", [], None),
    ("s137_TBAF", "reagent", None, "tetrabutylammonium fluoride", [("equivalents", q(2, "equiv"))], None),
    ("s137_THF", "solvent", None, "tetrahydrofuran", [], "C1CCOC1"),
    ("s137_404", "product", "404", "alpha-carbinol allenoate", [], None),
], [("alkynyl_enolate_addition", ["s137_402", "s137_403", "s137_TBAF", "s137_THF", "s137_404"], [
    ("temperature", q(0, "°C")),
])], [
    ("reported_yield", q(minimum=51, maximum=90, unit="%", raw_text="51-90%"), ["s137_404"]),
    ("yield_measurement_basis", None, ["s137_404"]),
], notes=["The prose states gamma addition is typical, with alpha selectivity possible at higher gamma steric demand."])

add("scheme138_allenyl_trifluoroborate", "literature_example", (22, 23), [
    ("s138_405", "reactant", "405", "allenyl pinacolboronic ester", [], None),
    ("s138_406", "reagent", "406", "aqueous potassium bifluoride", [("concentration", q(2.2, "M"))], None),
    ("s138_MeOH", "solvent", None, "methanol", [], "CO"),
    ("s138_407", "product", "407", "potassium allenyl trifluoroborate", [], None),
], [("trifluoroborate_formation", ["s138_405", "s138_406", "s138_MeOH", "s138_407"], [])], [
    ("reported_yield", q(73, "%"), ["s138_407"]),
    ("yield_measurement_basis", None, ["s138_407"]),
], notes=["The prose states that pinacol is removed azeotropically from the reaction mixture."])

add("scheme139_cinchonine_resolution", "literature_example", (22, 23), [
    ("s139a_408", "reactant", "408", "racemic 4-cyclohexyl-2-methyl-buta-2,3-dienoic acid", [], None),
    ("s139a_410", "reagent", "410", "cinchonine", [("equivalents", q(0.7, "equiv"))], None),
    ("s139a_EtOAc", "solvent", None, "ethyl acetate", [], "CCOC(C)=O"),
    ("s139a_H2SO4", "reagent", None, "sulfuric acid", [("concentration", q(20, "%"))], None),
    ("s139a_R411", "product", "(R)-411", "resolved (R)-allenoic acid", [], None),
], [
    ("salt_resolution", ["s139a_408", "s139a_410", "s139a_EtOAc"], [("operation", "recrystallization once from EtOAc")]),
    ("acid_liberation", ["s139a_408", "s139a_H2SO4", "s139a_R411"], []),
], [
    ("reported_yield", q(15, "%"), ["s139a_R411"]),
    ("enantiomeric_excess", q(80, "%"), ["s139a_R411"]),
    ("yield_measurement_basis", None, ["s139a_R411"]),
])

add("scheme139_cinchonidine_resolution", "literature_example", (22, 23), [
    ("s139b_408", "reactant", "408", "racemic 4-cyclohexyl-2-methyl-buta-2,3-dienoic acid", [], None),
    ("s139b_409", "reagent", "409", "cinchonidine", [("equivalents", q(0.75, "equiv"))], None),
    ("s139b_EtOAc", "solvent", None, "ethyl acetate", [], "CCOC(C)=O"),
    ("s139b_H2SO4", "reagent", None, "sulfuric acid", [("concentration", q(20, "%"))], None),
    ("s139b_S411", "product", "(S)-411", "resolved (S)-allenoic acid", [], None),
], [
    ("salt_resolution", ["s139b_408", "s139b_409", "s139b_EtOAc"], [("operation", "recrystallization twice from EtOAc")]),
    ("acid_liberation", ["s139b_408", "s139b_H2SO4", "s139b_S411"], []),
], [
    ("reported_yield", q(20, "%"), ["s139b_S411"]),
    ("enantiomeric_excess", q(95, "%"), ["s139b_S411"]),
    ("yield_measurement_basis", None, ["s139b_S411"]),
])

add("scheme140_ppl_allenol_kinetic_resolution", "literature_example", (22, 23), [
    ("s140_412", "reactant", "412", "racemic 2-methyldeca-2,3-dienol", [], None),
    ("s140_413", "reactant", "413", "vinyl acetate", [], "CC(=O)OC=C"),
    ("s140_PPL", "catalyst", None, "porcine pancreatic lipase", [], None),
    ("s140_414", "product", "414", "allenyl acetate enantiomer", [], None),
    ("s140_415", "product", "415", "recovered enantioenriched allenol", [], None),
], [("enzymatic_kinetic_resolution", ["s140_412", "s140_413", "s140_PPL", "s140_414", "s140_415"], [
    ("temperature", q(30, "°C")),
])], [
    ("reported_yield", q(66, "%"), ["s140_414"]),
    ("enantiomeric_excess", q(32, "%"), ["s140_414"]),
    ("recovered_starting_material_yield", q(19, "%"), ["s140_415"]),
    ("recovered_starting_material_enantiomeric_excess", q(98, "%", qualifier="gt", raw_text=">98% ee"), ["s140_415"]),
    ("yield_measurement_basis", None, ["s140_414", "s140_415"]),
])

add("scheme141_ppl_primary_allenol_resolution", "literature_example", (23, 24), [
    ("s141_416", "reactant", "416", "racemic primary allenic alcohol", [], None),
    ("s141_vinyl_butyrate", "reactant", None, "vinyl butyrate", [], "CCCC(=O)OC=C"),
    ("s141_PPL", "catalyst", None, "porcine pancreatic lipase", [], None),
    ("s141_iPr2O", "solvent", None, "diisopropyl ether", [], "CC(C)OC(C)C"),
    ("s141_R417", "product", "(R)-417", "allenyl butyrate", [], None),
    ("s141_S418", "product", "(S)-418", "recovered allenic alcohol", [], None),
], [("enzymatic_kinetic_resolution", ["s141_416", "s141_vinyl_butyrate", "s141_PPL", "s141_iPr2O", "s141_R417", "s141_S418"], [
    ("temperature", "r.t."),
])], [
    ("conversion", q(minimum=10, maximum=46, unit="%", raw_text="10-46% conv."), ["s141_416"]),
    ("enantiomeric_excess", q(minimum=95, maximum=99.2, unit="%", raw_text="95-99.2% ee"), ["s141_R417"]),
    ("reported_yield", None, ["s141_R417"]),
    ("recovered_starting_material_yield", None, ["s141_S418"]),
], notes=["The review states that substitution pattern controls rate and enantioselectivity; no isolated yields or ee for recovered 418 are shown in Scheme 141."])

add("scheme142_bisphosphoric_acid_kinetic_resolution", "literature_example", (23, 24), [
    ("s142_419", "reactant", "419", "racemic 2,3-allenoate", [], None),
    ("s142_420", "reactant", "420", "aldehyde", [], None),
    ("s142_421", "reactant", "421", "diethyl aminomalonate", [], None),
    ("s142_422", "catalyst", "422", "chiral bisphosphoric acid ligand", [("catalyst_loading", q(minimum=7.5, maximum=10, unit="mol%", raw_text="7.5-10 mol%"))], None),
    ("s142_MS", "reagent", None, "3 angstrom molecular sieves", [], None),
    ("s142_PhMe", "solvent", None, "toluene", [], "Cc1ccccc1"),
    ("s142_423", "product", "423", "recovered (R)-2,3-allenoate", [], None),
    ("s142_424", "product", "424", "3-methylenepyrrolidine derivative", [], None),
], [("one_three_dipolar_cycloaddition_resolution", ["s142_419", "s142_420", "s142_421", "s142_422", "s142_MS", "s142_PhMe", "s142_423", "s142_424"], [
    ("temperature", q(25, "°C")), ("time", q(3, "d")),
])], [
    ("recovered_starting_material_yield", q(minimum=35, maximum=48, unit="%", raw_text="35-48%"), ["s142_423"]),
    ("recovered_starting_material_enantiomeric_excess", q(99, "%", qualifier="gt", raw_text="up to >99% ee"), ["s142_423"]),
    ("reported_yield", q(minimum=39, maximum=57, unit="%", raw_text="39-57%"), ["s142_424"]),
    ("enantiomeric_excess", q(94, "%", qualifier="le", raw_text="up to 94% ee"), ["s142_424"]),
    ("yield_measurement_basis", None, ["s142_423", "s142_424"]),
])

add("scheme143_dynamic_kinetic_resolution", "literature_example", (23, 24), [
    ("s143_425", "reactant", "rac-425", "racemic allenol", [], None),
    ("s143_426", "reactant", "426", "vinyl butyrate", [], "CCCC(=O)OC=C"),
    ("s143_Pd", "catalyst", None, "[(IPr)PdBr2]2", [("catalyst_loading", q(2, "mol%"))], None),
    ("s143_PPL", "catalyst", None, "porcine pancreatic lipase on Celite", [], None),
    ("s143_toluene", "solvent", None, "toluene", [], "Cc1ccccc1"),
    ("s143_427", "product", "(R)-427", "allenyl butyrate", [], None),
], [("dynamic_kinetic_resolution", ["s143_425", "s143_426", "s143_Pd", "s143_PPL", "s143_toluene", "s143_427"], [
    ("temperature", q(50, "°C")),
])], [
    ("reported_yield", q(minimum=70, maximum=87, unit="%", raw_text="70-87%"), ["s143_427"]),
    ("enantiomeric_excess", q(minimum=66, maximum=89, unit="%", raw_text="66% to 89% ee"), ["s143_427"]),
    ("yield_measurement_basis", None, ["s143_427"]),
])

# Scheme 144 is a three-stage sequence; retain each stage separately.
add("scheme144_bromoallene_preparation", "literature_example", (23, 24), [
    ("s144a_428", "reactant", "428", "propargylic tosylate precursor", [], None),
    ("s144a_CuBr", "reagent", None, "copper(I) bromide", [], None),
    ("s144a_LiBr", "reagent", None, "lithium bromide", [], None),
    ("s144a_THF", "solvent", None, "tetrahydrofuran", [], "C1CCOC1"),
    ("s144a_429", "product", "429", "allenyl bromide", [], None),
], [("bromide_substitution", ["s144a_428", "s144a_CuBr", "s144a_LiBr", "s144a_THF", "s144a_429"], [])], [
    ("reported_yield", q(86, "%"), ["s144a_429"]),
    ("yield_measurement_basis", None, ["s144a_429"]),
])

add("scheme144_negishi_allenediyne_coupling", "literature_example", (23, 24), [
    ("s144b_429", "reactant", "429", "allenyl bromide", [], None),
    ("s144b_430", "reactant", "430", "terminal diyne", [], None),
    ("s144b_MeLi", "reagent", None, "methyllithium", [], None),
    ("s144b_ZnBr2", "reagent", None, "zinc bromide", [], None),
    ("s144b_Pd", "catalyst", None, "Pd(PPh3)4", [], None),
    ("s144b_THF", "solvent", None, "tetrahydrofuran", [], "C1CCOC1"),
    ("s144b_431", "product", "431", "protected phomallenic acid C allenediyne", [], None),
], [
    ("diyne_zincation", ["s144b_430", "s144b_MeLi", "s144b_ZnBr2", "s144b_THF"], []),
    ("negishi_coupling", ["s144b_429", "s144b_430", "s144b_Pd", "s144b_THF", "s144b_431"], [
        ("temperature", q(0, "°C")), ("time", q(4, "h")),
    ]),
], [
    ("reported_yield", q(92, "%"), ["s144b_431"]),
    ("yield_measurement_basis", None, ["s144b_431"]),
], notes=["The adjacent prose describes the overall first stereoselective synthesis as giving phomallenic acid C in 88% ee; the depicted coupling-stage product 431 has no separate ee printed at the arrow."])

add("scheme144_phomallenic_acid_deprotection", "literature_example", (23, 24), [
    ("s144c_431", "reactant", "431", "protected phomallenic acid C", [], None),
    ("s144c_TFA", "reagent", None, "trifluoroacetic acid", [], "O=C(O)C(F)(F)F"),
    ("s144c_CH2Cl2", "solvent", None, "dichloromethane", [], "ClCCl"),
    ("s144c_432", "product", "432", "phomallenic acid C", [], None),
], [("deprotection", ["s144c_431", "s144c_TFA", "s144c_CH2Cl2", "s144c_432"], [
    ("temperature", q(minimum=-15, maximum=0, unit="°C", raw_text="-15 to 0 °C")), ("time", q(5, "h")),
])], [
    ("reported_yield", q(92, "%"), ["s144c_432"]),
    ("enantiomeric_excess", q(88, "%"), ["s144c_432"]),
    ("yield_measurement_basis", None, ["s144c_432"]),
])

# Scheme 145 is a two-stage racemic synthesis; retain the failed asymmetric observation in the coupling note.
add("scheme145_palladium_diyne_propargyl_coupling", "literature_example", (23, 24), [
    ("s145a_430", "reactant", "430", "terminal diyne", [], None),
    ("s145a_433", "reactant", "433", "propargylic tosylate", [], None),
    ("s145a_Pd", "catalyst", None, "Pd(PPh3)4", [("catalyst_loading", q(10, "mol%"))], None),
    ("s145a_CuI", "catalyst", None, "copper(I) iodide", [("catalyst_loading", q(10, "mol%"))], None),
    ("s145a_iPr2NH", "reagent", None, "diisopropylamine", [], None),
    ("s145a_benzene", "solvent", None, "benzene", [], "c1ccccc1"),
    ("s145a_434", "product", "434", "methyl ester precursor of phomallenic acid C", [], None),
], [("palladium_catalyzed_coupling", ["s145a_430", "s145a_433", "s145a_Pd", "s145a_CuI", "s145a_iPr2NH", "s145a_benzene", "s145a_434"], [
    ("temperature", "r.t."),
])], [
    ("reported_yield", q(67, "%"), ["s145a_434"]),
    ("asymmetric_attempt_enantiomeric_excess", q(0, "%", raw_text="0% ee"), ["s145a_434"]),
    ("yield_measurement_basis", None, ["s145a_434"]),
], notes=["The drawn route is racemic. The adjacent prose separately reports that attempts using optically active propargylic compounds failed through uncontrollable racemization, giving 0% ee; the exact optically active substrate and its batch conditions are not specified, so no separate experiment record was created."])

add("scheme145_phomallenic_acid_hydrolysis", "literature_example", (23, 24), [
    ("s145b_434", "reactant", "434", "methyl ester precursor of phomallenic acid C", [], None),
    ("s145b_LiOH", "reagent", None, "lithium hydroxide", [], "[Li+].[OH-]"),
    ("s145b_MeOH", "solvent", None, "methanol", [], "CO"),
    ("s145b_432", "product", "432", "racemic phomallenic acid C", [], None),
], [("ester_hydrolysis", ["s145b_434", "s145b_LiOH", "s145b_MeOH", "s145b_432"], [
    ("temperature", q(0, "°C")),
])], [
    ("reported_yield", q(72, "%"), ["s145b_432"]),
    ("yield_measurement_basis", None, ["s145b_432"]),
])


OUT.write_text(json.dumps(R, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"output": str(OUT), "records": len(R)}, ensure_ascii=False))
