#!/usr/bin/env python3
"""Build machine-extracted records for Yu & Ma, Chem. Commun. 2011, PDF pages 7-12."""
import json
from pathlib import Path

DOC = "doc_e77fa99a0ade23d1"
OUT = Path(__file__).with_name("records_pages_0007_0012.json")


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


def participant(entity_id, role, label, name, evidence, amounts=None, smiles=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence),
        "smiles": fact(smiles, evidence),
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


def record(rid, kind, evidence, participants, steps, outcomes=None, notes=None, unresolved=None):
    default_unresolved = [
        "This feature article summarizes prior literature and does not provide a full batch procedure.",
        "Exact scale, atmosphere, workup, purification, and yield measurement basis are not reported here.",
        "Depicted structures and stereochemistry remain machine-unverified; generic R-group structures have null SMILES.",
        "Supporting Information was not supplied or explicitly associated.",
    ]
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
        "outcomes": outcomes or [],
        "notes": [fact(note, evidence) for note in (notes or [])],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved if unresolved is not None else default_unresolved,
        },
    }


R = []


def add(rid, kind, pages, participant_specs, step_specs, outcome_specs=(), notes=(), unresolved=None):
    evidence = ev(*pages)
    participants = [participant(entity_id, role, label, name, evidence, amounts, smiles)
                    for entity_id, role, label, name, amounts, smiles in participant_specs]
    steps = [step(sid, ids, evidence, conds) for sid, ids, conds in step_specs]
    outcomes = [field(name, value, evidence, targets) for name, value, targets in outcome_specs]
    R.append(record(rid, kind, evidence, participants, steps, outcomes, notes, unresolved))


# Page 7: Schemes 31-34.
add("scheme31_acid_catalyzed_allenylindole", "literature_example", (7,), [
    ("s31_86", "reactant", "86", "2-arylindole", [], None),
    ("s31_87", "reactant", "87", "tertiary propargylic alcohol", [], None),
    ("s31_PTSA", "catalyst", None, "p-toluenesulfonic acid", [("catalyst_loading", q(5, "mol%"))], None),
    ("s31_MeCN", "solvent", None, "acetonitrile", [], "CC#N"),
    ("s31_88", "product", "88", "3-allenylindole derivative", [], None),
], [("substitution", ["s31_86", "s31_87", "s31_PTSA", "s31_MeCN", "s31_88"], [("temperature", "r.t.")])], [
    ("reported_yield", q(minimum=55, maximum=82, unit="%", raw_text="55-82%"), ["s31_88"]),
    ("yield_measurement_basis", None, ["s31_88"]),
])

add("scheme32_phosphine_deoxygenation", "literature_example", (7,), [
    ("s32_89", "reactant", "89", "2,4-alkadiynol", [], None),
    ("s32_PPh3", "reagent", None, "triphenylphosphine", [("equivalents", q(1.2, "equiv"))], None),
    ("s32_toluene", "solvent", None, "toluene", [], "Cc1ccccc1"),
    ("s32_90", "product", "90", "allenyne", [], None),
], [("deoxygenation", ["s32_89", "s32_PPh3", "s32_toluene", "s32_90"], [("temperature", q(80, "°C")), ("time", q(18, "h"))])], [
    ("reported_yield", q(minimum=51, maximum=66, unit="%", raw_text="51-66%"), ["s32_90"]),
    ("yield_measurement_basis", None, ["s32_90"]),
])

add("scheme33_desilylative_allenol_formation", "literature_example", (7,), [
    ("s33_91", "reactant", "91", "TMS-substituted propargyl alcohol", [], None),
    ("s33_TBAF", "reagent", None, "tetrabutylammonium fluoride", [("equivalents", q(1.5, "equiv"))], None),
    ("s33_THF", "solvent", None, "tetrahydrofuran", [], "C1CCOC1"),
    ("s33_92", "product", "92", "2,3-allenol", [], None),
], [("desilylation_isomerization", ["s33_91", "s33_TBAF", "s33_THF", "s33_92"], [("temperature", "r.t."), ("time", q(1, "h"))])], [
    ("reported_yield", q(minimum=78, maximum=95, unit="%", raw_text="78-95%"), ["s33_92"]),
    ("yield_measurement_basis", None, ["s33_92"]),
])

add("scheme34_perfluoro_organocopper_substitution", "literature_example", (7,), [
    ("s34_93", "reactant", "93", "perfluoro organocopper reagent RfM", [], None),
    ("s34_94", "reactant", "94", "tertiary propargylic chloride", [], None),
    ("s34_DMF", "solvent", None, "DMF", [], "CN(C)C=O"),
    ("s34_95", "product", "95", "perfluoro-substituted allene", [], None),
], [("anti_SN2_prime_substitution", ["s34_93", "s34_94", "s34_DMF", "s34_95"], [("temperature", "r.t.")])], [
    ("reported_yield", q(minimum=59, maximum=79, unit="%", raw_text="59-79%"), ["s34_95"]),
    ("yield_measurement_basis", None, ["s34_95"]),
])

# Pages 7-8: Schemes 35-45.
E78 = (7, 8)
add("scheme35_allenylsilane_anti_substitution", "literature_example", E78, [
    ("s35_96", "reactant", "96", "enantiopure oxazolidine propargyl acetate", [], None),
    ("s35_98", "reagent", "98", "(trimethylsilyl)cyanocuprate", [], None),
    ("s35_97", "product", "97", "enantioenriched allenylsilane", [], None),
], [("anti_SN2_prime_substitution", ["s35_96", "s35_98", "s35_97"], [("temperature", q(-78, "°C")), ("time", q(10, "min"))])], notes=[
    "The review describes stereoselective anti-SN2-prime substitution but does not assign a numeric yield or ee in Scheme 35."
])

add("scheme36_chiral_sulfoxide_copper_substitution", "literature_example", E78, [
    ("s36_99", "reactant", "99", "chiral sulfoxide-containing benzylic copper complex", [], None),
    ("s36_100", "reactant", "100", "propargyl bromide or mesylate", [], None),
    ("s36_THF", "solvent", None, "tetrahydrofuran", [], "C1CCOC1"),
    ("s36_101", "product", "101", "chiral allene", [], None),
], [("anti_SN2_prime_substitution", ["s36_99", "s36_100", "s36_THF", "s36_101"], [("temperature", q(-78, "°C"))])], [
    ("reported_yield", q(minimum=40, maximum=76, unit="%", raw_text="40-76%"), ["s36_101"]),
    ("diastereomeric_ratio", "85/15 to >98/2 dr", ["s36_101"]),
    ("yield_measurement_basis", None, ["s36_101"]),
])

add("scheme37_bislactim_ether_allenylation", "literature_example", E78, [
    ("s37_102", "reactant", "102", "bislactim ether of cyclo-(-L-Val-Gly-)", [], None),
    ("s37_nBuLi", "reagent", None, "n-butyllithium", [("equivalents", q(1.02, "equiv"))], None),
    ("s37_CuBrSMe2", "catalyst", None, "CuBr·Me2S", [("equivalents", q(0.5, "equiv"))], None),
    ("s37_103", "reactant", "103", "primary propargyl bromide", [("equivalents", q(1.0, "equiv"))], None),
    ("s37_104", "product", "104", "allenyl-substituted bislactim ether", [], None),
], [("copper_catalyzed_substitution", ["s37_102", "s37_nBuLi", "s37_CuBrSMe2", "s37_103", "s37_104"], [])], [
    ("reported_yield", q(minimum=24, maximum=59, unit="%", raw_text="24-59%"), ["s37_104"]),
    ("diastereomeric_excess", q(minimum=22, maximum=98, unit="%", raw_text="de 22-98%"), ["s37_104"]),
    ("yield_measurement_basis", None, ["s37_104"]),
])

add("scheme37_allenylglycine_deprotection", "literature_example", E78, [
    ("s37b_104", "reactant", "104", "allenyl-substituted bislactim ether", [], None),
    ("s37b_TFA", "reagent", None, "TFA", [("concentration", "0.2 N")], None),
    ("s37b_Boc2O", "reagent", None, "di-tert-butyl dicarbonate", [], None),
    ("s37b_Et3N", "reagent", None, "triethylamine", [], None),
    ("s37b_105", "product", "105", "N-Boc alpha-allenylglycine ester", [], None),
], [("hydrolysis", ["s37b_104", "s37b_TFA"], []), ("Boc_protection", ["s37b_104", "s37b_Boc2O", "s37b_Et3N", "s37b_105"], [])], [
    ("reported_yield", q(minimum=60, maximum=83, unit="%", raw_text="60-83%"), ["s37b_105"]),
    ("enantiomeric_excess", q(95, "%", qualifier="gt", raw_text=">95% ee"), ["s37b_105"]),
    ("yield_measurement_basis", None, ["s37b_105"]),
])

add("scheme38_nhc_copper_hydride_reduction", "literature_example", E78, [
    ("s38_106", "reactant", "106", "propargylic carbonate", [], None),
    ("s38_CuCl", "catalyst", None, "copper(I) chloride", [("catalyst_loading", q(3, "mol%"))], None),
    ("s38_ligand", "catalyst", None, "IBiox12·HOTf", [("ligand_loading", q(3, "mol%"))], None),
    ("s38_NaOtBu", "reagent", None, "sodium tert-butoxide", [("loading", q(9, "mol%"))], None),
    ("s38_PMHS", "reagent", None, "PMHS", [("equivalents", q(2, "equiv"))], None),
    ("s38_PhMe", "solvent", None, "toluene", [], "Cc1ccccc1"),
    ("s38_107", "product", "107", "di- or trisubstituted allene", [], None),
], [("copper_hydride_reduction", ["s38_106", "s38_CuCl", "s38_ligand", "s38_NaOtBu", "s38_PMHS", "s38_PhMe", "s38_107"], [("temperature", "r.t."), ("time", q(minimum=14, maximum=40, unit="h", raw_text="14-40 h"))])], [
    ("reported_yield", q(minimum=55, maximum=96, unit="%", raw_text="55-96%"), ["s38_107"]),
    ("yield_measurement_basis", None, ["s38_107"]),
])

add("scheme39_xantphos_copper_hydride_reduction", "literature_example", E78, [
    ("s39_108", "reactant", "108", "propargylic carbonate", [], None),
    ("s39_CuOAc", "catalyst", None, "copper(II) acetate", [("catalyst_loading", q(2, "mol%"))], None),
    ("s39_Xantphos", "catalyst", None, "Xantphos", [("ligand_loading", q(3, "mol%"))], None),
    ("s39_PMHS", "reagent", None, "PMHS", [("equivalents", q(4, "equiv"))], None),
    ("s39_THF", "solvent", None, "tetrahydrofuran", [], "C1CCOC1"),
    ("s39_109", "product", "109", "di- or trisubstituted allene", [], None),
], [("copper_hydride_reduction", ["s39_108", "s39_CuOAc", "s39_Xantphos", "s39_PMHS", "s39_THF", "s39_109"], [("temperature", q(50, "°C"))])], [
    ("reported_yield", q(minimum=44, maximum=86, unit="%", raw_text="44-86%"), ["s39_109"]),
    ("yield_measurement_basis", None, ["s39_109"]),
])

add("scheme39_chiral_carbonate_reduction", "literature_example", E78, [
    ("s39b_110", "reactant", "110", "enantioenriched propargylic carbonate", [("enantiomeric_excess", q(99.5, "%"))], None),
    ("s39b_CuOAc", "catalyst", None, "copper(II) acetate", [("catalyst_loading", q(2, "mol%"))], None),
    ("s39b_Xantphos", "catalyst", None, "Xantphos", [("ligand_loading", q(3, "mol%"))], None),
    ("s39b_PMHS", "reagent", None, "PMHS", [("equivalents", q(4, "equiv"))], None),
    ("s39b_THF", "solvent", None, "tetrahydrofuran", [], "C1CCOC1"),
    ("s39b_111", "product", "111", "axially chiral allene", [], None),
], [("copper_hydride_reduction", ["s39b_110", "s39b_CuOAc", "s39b_Xantphos", "s39b_PMHS", "s39b_THF", "s39b_111"], [("temperature", q(0, "°C")), ("time", q(86, "h"))])], [
    ("reported_yield", q(77, "%"), ["s39b_111"]),
    ("enantiomeric_excess", q(99.0, "%"), ["s39b_111"]),
    ("yield_measurement_basis", None, ["s39b_111"]),
])

add("scheme40_copper_borylation", "literature_example", E78, [
    ("s40_112", "reactant", "112", "propargylic carbonate", [], None),
    ("s40_113", "reactant", "113", "bis(pinacolato)diboron", [], None),
    ("s40_CuOtBu", "catalyst", None, "copper(I) tert-butoxide", [("catalyst_loading", q(10, "mol%"))], None),
    ("s40_Xantphos", "catalyst", None, "Xantphos", [("ligand_loading", q(10, "mol%"))], None),
    ("s40_THF", "solvent", None, "tetrahydrofuran", [], "C1CCOC1"),
    ("s40_114", "product", "114", "allenylboronate", [], None),
], [("borylative_substitution", ["s40_112", "s40_113", "s40_CuOtBu", "s40_Xantphos", "s40_THF", "s40_114"], [("temperature", q(50, "°C")), ("time", q(minimum=46, maximum=87, unit="h", raw_text="46-87 h"))])], notes=[
    "Scheme 40 gives no numeric yield for the general substrate series 112 to 114."
])

add("scheme40_chiral_allenylboronate", "literature_example", E78, [
    ("s40b_115", "reactant", "115", "enantioenriched propargylic carbonate", [("enantiomeric_excess", q(97, "%"))], None),
    ("s40b_113", "reactant", "113", "bis(pinacolato)diboron", [], None),
    ("s40b_CuOtBu", "catalyst", None, "copper(I) tert-butoxide", [("catalyst_loading", q(10, "mol%"))], None),
    ("s40b_Xantphos", "catalyst", None, "Xantphos", [("ligand_loading", q(10, "mol%"))], None),
    ("s40b_THF", "solvent", None, "tetrahydrofuran", [], "C1CCOC1"),
    ("s40b_116", "product", "116", "axially chiral allenylboronate", [], None),
], [("borylative_substitution", ["s40b_115", "s40b_113", "s40b_CuOtBu", "s40b_Xantphos", "s40b_THF", "s40b_116"], [("temperature", q(50, "°C")), ("time", q(5, "h"))])], [
    ("reported_yield", q(60, "%"), ["s40b_116"]),
    ("enantiomeric_excess", q(96, "%", qualifier="gt", raw_text=">96% ee"), ["s40b_116"]),
    ("yield_measurement_basis", None, ["s40b_116"]),
])

add("scheme41_chiral_allenol_from_propargyl_ether", "literature_example", E78, [
    ("s41_117", "reactant", "117", "optically active 4-hydroxy-4-aryl-2-butynyl methyl ether", [("enantiomeric_excess", q(minimum=96.4, maximum=99.2, unit="%", raw_text="96.4-99.2% ee"))], None),
    ("s41_RMgBr", "reactant", None, "primary alkyl Grignard reagent", [], None),
    ("s41_CuBr", "catalyst", None, "copper(I) bromide", [("catalyst_loading", q(20, "mol%"))], None),
    ("s41_Et2O", "solvent", None, "diethyl ether", [], "CCOCC"),
    ("s41_118", "product", "118", "enantioenriched secondary 2,3-allenol", [], None),
], [("copper_catalyzed_substitution", ["s41_117", "s41_RMgBr", "s41_CuBr", "s41_Et2O", "s41_118"], [("temperature", q(-30, "°C"))])], [
    ("reported_yield", q(minimum=30, maximum=58, unit="%", raw_text="30-58%"), ["s41_118"]),
    ("enantiomeric_excess", q(minimum=95.3, maximum=99.7, unit="%", raw_text="95.3-99.7% ee"), ["s41_118"]),
    ("yield_measurement_basis", None, ["s41_118"]),
])

add("scheme42_chiral_allenol_from_propargyl_chloride", "literature_example", E78, [
    ("s42_119", "reactant", "119", "optically active propargyl chloride", [], None),
    ("s42_RMgBr", "reactant", None, "alkylmagnesium bromide", [("equivalents", q(3, "equiv"))], None),
    ("s42_CuCN", "catalyst", None, "copper(I) cyanide", [("catalyst_loading", q(5, "mol%"))], None),
    ("s42_Et2O", "solvent", None, "diethyl ether", [], "CCOCC"),
    ("s42_120", "product", "120", "enantioenriched 2,3-allenol", [], None),
], [("copper_catalyzed_substitution", ["s42_119", "s42_RMgBr", "s42_CuCN", "s42_Et2O", "s42_120"], [("temperature", q(-60, "°C"))])], [
    ("reported_yield", q(minimum=60, maximum=89, unit="%", raw_text="60-89%"), ["s42_120"]),
    ("yield_measurement_basis", None, ["s42_120"]),
])

add("scheme43_bisepoxide_ring_opening", "literature_example", E78, [
    ("s43_121", "reactant", "121", "bis(acetylenic epoxide)", [], None),
    ("s43_RMgCl", "reactant", None, "alkylmagnesium chloride", [], None),
    ("s43_LiBr", "reagent", None, "lithium bromide", [], None),
    ("s43_CuBrSMe2", "catalyst", None, "CuBr·SMe2", [], None),
    ("s43_THF", "solvent", None, "tetrahydrofuran", [], "C1CCOC1"),
    ("s43_122", "product", "122", "conjugated bisallenol", [], None),
], [("double_ring_opening", ["s43_121", "s43_RMgCl", "s43_LiBr", "s43_CuBrSMe2", "s43_THF", "s43_122"], [("temperature", q(minimum=-65, maximum=20, unit="°C", raw_text="-65 °C to rt"))])], [
    ("reported_yield", q(minimum=12, maximum=58, unit="%", raw_text="12-58%"), ["s43_122"]),
    ("yield_measurement_basis", None, ["s43_122"]),
])

add("scheme44_dioxolanone_ring_opening", "literature_example", E78, [
    ("s44_123", "reactant", "123", "acetylenic dioxolanone", [], None),
    ("s44_RMgX", "reactant", None, "organomagnesium reagent", [], None),
    ("s44_Cu", "catalyst", None, "[Cu(MeCN)4][BF4]", [("catalyst_loading", q(10, "mol%"))], None),
    ("s44_POBu3", "catalyst", None, "tributyl phosphite", [("ligand_loading", q(20, "mol%"))], None),
    ("s44_CH2Cl2", "solvent", None, "dichloromethane", [], "ClCCl"),
    ("s44_125", "product", "125", "alpha-allenol", [], None),
], [("ring_opening", ["s44_123", "s44_RMgX", "s44_Cu", "s44_POBu3", "s44_CH2Cl2", "s44_125"], [("temperature", q(-10, "°C")), ("time", q(2, "h"))])], [
    ("reported_yield", q(minimum=39, maximum=92, unit="%", raw_text="39-92%"), ["s44_125"]),
    ("yield_measurement_basis", None, ["s44_125"]),
], notes=["Structure 124 is depicted as a proposed chelated intermediate and was not recorded as an isolated product."])

add("scheme45_indium_allylation", "literature_example", E78, [
    ("s45_126", "reactant", "126", "tertiary propargyl alcohol", [], None),
    ("s45_127", "reactant", "127", "allyl bromide", [], None),
    ("s45_In", "reagent", None, "indium", [("equivalents", q(1.5, "equiv"))], None),
    ("s45_THF", "solvent", None, "tetrahydrofuran", [], "C1CCOC1"),
    ("s45_128", "product", "128", "tri- or tetrasubstituted allene", [], None),
], [("indium_mediated_allylation", ["s45_126", "s45_127", "s45_In", "s45_THF", "s45_128"], [("temperature", q(minimum=35, maximum=70, unit="°C", raw_text="35-70 °C"))])], [
    ("reported_yield", q(minimum=70, maximum=86, unit="%", raw_text="70-86%"), ["s45_128"]),
    ("yield_measurement_basis", None, ["s45_128"]),
])

# Page 9: Schemes 46-47.
add("scheme46_indium_allenylsilane", "literature_example", (7, 9), [
    ("s46_129", "reactant", "129", "propargyl bromide", [], None),
    ("s46_R3SiCl", "reactant", None, "chlorosilane", [], None),
    ("s46_In", "reagent", None, "indium powder", [("equivalents", q(1, "equiv"))], None),
    ("s46_DMF", "solvent", None, "DMF", [], "CN(C)C=O"),
    ("s46_130", "product", "130", "allenylsilane", [], None),
], [("indium_mediated_silylation", ["s46_129", "s46_R3SiCl", "s46_In", "s46_DMF", "s46_130"], [("temperature", "r.t."), ("time", q(3, "h"))])], [
    ("reported_yield", q(minimum=79, maximum=98, unit="%", raw_text="79-98%"), ["s46_130"]),
    ("yield_measurement_basis", None, ["s46_130"]),
])

add("scheme47_zirconocene_reductive_substitution", "literature_example", (9,), [
    ("s47_131", "reactant", "131", "propargylic alcohol", [], None),
    ("s47_Cp2ZrHCl", "reagent", None, "Schwartz reagent", [("equivalents", q(1.1, "equiv"))], None),
    ("s47_alkylmetal", "reagent", None, "ethylmagnesium chloride", [], None),
    ("s47_solvent", "solvent", None, "toluene", [], "Cc1ccccc1"),
    ("s47_132", "product", "132", "allene", [], None),
], [("anti_reductive_substitution", ["s47_131", "s47_Cp2ZrHCl", "s47_alkylmetal", "s47_solvent", "s47_132"], [("temperature", "r.t."), ("time", q(24, "h"))])], [
    ("reported_yield", None, ["s47_132"]),
    ("enantiomeric_excess", None, ["s47_132"]),
], notes=["Scheme 47 reports 60-90% yield and 93-98% ee across the EtMgCl/toluene and Et2Zn-ZnCl2/toluene-THF options without assigning those ranges to one option."])

add("scheme47_zirconocene_zinc_reductive_substitution", "literature_example", (9,), [
    ("s47b_131", "reactant", "131", "propargylic alcohol", [], None),
    ("s47b_Cp2ZrHCl", "reagent", None, "Schwartz reagent", [("equivalents", q(1.1, "equiv"))], None),
    ("s47b_Et2Zn", "reagent", None, "diethylzinc", [], None),
    ("s47b_ZnCl2", "reagent", None, "zinc chloride", [], None),
    ("s47b_solvent", "solvent", None, "toluene/THF", [], None),
    ("s47b_132", "product", "132", "allene", [], None),
], [("anti_reductive_substitution", ["s47b_131", "s47b_Cp2ZrHCl", "s47b_Et2Zn", "s47b_ZnCl2", "s47b_solvent", "s47b_132"], [("temperature", "r.t."), ("time", q(24, "h"))])], [
    ("reported_yield", None, ["s47b_132"]),
    ("enantiomeric_excess", None, ["s47b_132"]),
], notes=["Scheme 47 reports 60-90% yield and 93-98% ee across the EtMgCl/toluene and Et2Zn-ZnCl2/toluene-THF options without assigning those ranges to one option."])

# Pages 9-10: Schemes 48-57.
E910 = (9, 10)
add("scheme48_rhodium_allenylsilane_scope", "literature_example", E910, [
    ("s48_133", "reactant", "133", "propargylic carbonate", [], None),
    ("s48_134", "reactant", "134", "silylboronate", [], None),
    ("s48_Rh", "catalyst", None, "[Rh(cod)2][BF4]", [("catalyst_loading", q(5, "mol%"))], None),
    ("s48_Et3N", "reagent", None, "triethylamine", [], None),
    ("s48_acetone", "solvent", None, "acetone", [], "CC(=O)C"),
    ("s48_135", "product", "135", "allenylsilane", [], None),
], [("rhodium_catalyzed_coupling", ["s48_133", "s48_134", "s48_Rh", "s48_Et3N", "s48_acetone", "s48_135"], [("temperature", q(50, "°C"))])], [
    ("reported_yield", q(minimum=80, maximum=97, unit="%", raw_text="80-97%"), ["s48_135"]),
    ("yield_measurement_basis", None, ["s48_135"]),
])

add("scheme48_chiral_allenylsilane", "literature_example", E910, [
    ("s48b_136", "reactant", "136", "optically active propargylic carbonate", [("enantiomeric_excess", q(97, "%"))], None),
    ("s48b_134", "reactant", "134", "silylboronate", [], None),
    ("s48b_Rh", "catalyst", None, "[Rh(cod)2][BF4]", [("catalyst_loading", q(10, "mol%"))], None),
    ("s48b_Et3N", "reagent", None, "triethylamine", [], None),
    ("s48b_solvent", "solvent", None, "DMF/MeCN", [], None),
    ("s48b_137", "product", "137", "axially chiral allenylsilane", [], None),
], [("rhodium_catalyzed_coupling", ["s48b_136", "s48b_134", "s48b_Rh", "s48b_Et3N", "s48b_solvent", "s48b_137"], [("temperature", q(25, "°C")), ("time", q(12, "h"))])], [
    ("reported_yield", q(77, "%"), ["s48b_137"]),
    ("yield_measurement_basis", None, ["s48b_137"]),
])

add("scheme48_allenylsilane_aldehyde_addition", "literature_example", E910, [
    ("s48c_137", "reactant", "137", "axially chiral allenylsilane", [], None),
    ("s48c_TiCl4", "reagent", None, "titanium tetrachloride", [("equivalents", q(1.5, "equiv"))], None),
    ("s48c_iPrCHO", "reactant", None, "isobutyraldehyde", [("equivalents", q(1.5, "equiv"))], None),
    ("s48c_CH2Cl2", "solvent", None, "dichloromethane", [], "ClCCl"),
    ("s48c_138", "product", "138", "homoallenyl alcohol", [], None),
], [("Lewis_acid_promoted_addition", ["s48c_137", "s48c_TiCl4", "s48c_iPrCHO", "s48c_CH2Cl2", "s48c_138"], [("temperature", q(-78, "°C")), ("time", q(3, "h"))])], [
    ("reported_yield", q(74, "%"), ["s48c_138"]),
    ("enantiomeric_excess", q(95, "%"), ["s48c_138"]),
    ("diastereomeric_ratio", ">20:1", ["s48c_138"]),
    ("yield_measurement_basis", None, ["s48c_138"]),
])

add("scheme49_organozinc_substitution_scope", "literature_example", E910, [
    ("s49_139", "reactant", "139", "propargyl mesylate", [], None),
    ("s49_ZnR2", "reactant", None, "diorganozinc reagent", [("equivalents", q(2, "equiv"))], None),
    ("s49_DMSO", "solvent", None, "DMSO", [], "CS(C)=O"),
    ("s49_140", "product", "140", "substituted allene", [], None),
], [("SN2_prime_substitution", ["s49_139", "s49_ZnR2", "s49_DMSO", "s49_140"], [("temperature", "r.t.")])], [
    ("reported_yield", q(minimum=44, maximum=100, unit="%", raw_text="44-100%"), ["s49_140"]),
    ("yield_measurement_basis", None, ["s49_140"]),
])

add("scheme49_chiral_organozinc_substitution", "literature_example", E910, [
    ("s49b_141", "reactant", "141", "enantioenriched propargyl mesylate", [("enantiomeric_excess", q(99, "%", qualifier="gt", raw_text=">99% ee"))], None),
    ("s49b_Zn", "reactant", None, "di-n-butylzinc", [("equivalents", q(2, "equiv"))], None),
    ("s49b_DMSO", "solvent", None, "DMSO", [], "CS(C)=O"),
    ("s49b_142", "product", "142", "axially chiral allene", [], None),
], [("SN2_prime_substitution", ["s49b_141", "s49b_Zn", "s49b_DMSO", "s49b_142"], [("temperature", "r.t."), ("time", q(24, "h"))])], [
    ("enantiomeric_excess", q(98, "%"), ["s49b_142"]),
], notes=["Scheme 49 does not display a yield for the specific conversion 141 to 142."])

add("scheme50_nickel_intramolecular_substitution", "literature_example", E910, [
    ("s50_143", "reactant", "143", "propargylic compound with tethered carbon nucleophile", [], None),
    ("s50_Ni", "catalyst", None, "Ni3(PO4)2·8H2O", [("catalyst_loading", q(2, "mol%"))], None),
    ("s50_Cs2CO3", "reagent", None, "cesium carbonate", [], None),
    ("s50_DMF", "solvent", None, "DMF", [], "CN(C)C=O"),
    ("s50_144", "product", "144", "allene-bearing indene derivative", [], None),
], [("intramolecular_substitution", ["s50_143", "s50_Ni", "s50_Cs2CO3", "s50_DMF", "s50_144"], [("temperature", q(60, "°C"))])], [
    ("reported_yield", q(minimum=45, maximum=83, unit="%", raw_text="45-83%"), ["s50_144"]),
    ("yield_measurement_basis", None, ["s50_144"]),
])

add("scheme51_iron_intramolecular_substitution", "literature_example", E910, [
    ("s51_145", "reactant", "145", "benzylamino-substituted propargylic alcohol", [], None),
    ("s51_FeCl3", "catalyst", None, "FeCl3·6H2O", [("catalyst_loading", q(5, "mol%"))], None),
    ("s51_CH3NO2", "solvent", None, "nitromethane", [], "C[N+](=O)[O-]"),
    ("s51_146", "product", "146", "tetrahydroisoquinoline with exo-allene", [], None),
], [("intramolecular_substitution", ["s51_145", "s51_FeCl3", "s51_CH3NO2", "s51_146"], [("temperature", "r.t.")])], [
    ("reported_yield", q(minimum=37, maximum=90, unit="%", raw_text="37-90%"), ["s51_146"]),
    ("yield_measurement_basis", None, ["s51_146"]),
])

add("scheme52_rhodium_epoxide_opening_nbd", "literature_example", E910, [
    ("s52a_147", "reactant", "147", "alkynyl oxirane", [], None),
    ("s52a_148", "reactant", "148", "arylboronic acid", [], None),
    ("s52a_Rh", "catalyst", None, "[RhCl(nbd)]2", [("catalyst_loading", q(2.5, "mol%"))], None),
    ("s52a_KOH", "reagent", None, "potassium hydroxide", [("equivalents", q(minimum=0.5, maximum=0.6, unit="equiv", raw_text="0.5-0.6 equiv"))], None),
    ("s52a_THF", "solvent", None, "tetrahydrofuran", [], "C1CCOC1"),
    ("s52a_151", "product", "151", "syn-configured alpha-allenol", [], None),
], [("rhodium_catalyzed_ring_opening", ["s52a_147", "s52a_148", "s52a_Rh", "s52a_KOH", "s52a_THF", "s52a_151"], [("temperature", "r.t."), ("time", q(minimum=3, maximum=16, unit="h", raw_text="3-16 h"))])], [
    ("reported_yield_across_scheme52_conditions", q(minimum=72, maximum=86, unit="%", raw_text="72-86%"), ["s52a_151"]),
    ("syn_anti_ratio_across_scheme52_conditions", "up to 99/1", ["s52a_151"]),
    ("yield_measurement_basis", None, ["s52a_151"]),
], notes=["The displayed 72-86% and syn/anti up to 99/1 are shared across the two alternative Scheme 52 catalyst systems and are not assigned to one system."])

add("scheme52_rhodium_epoxide_opening_hydroxo", "literature_example", E910, [
    ("s52b_147", "reactant", "147", "alkynyl oxirane", [], None),
    ("s52b_148", "reactant", "148", "arylboronic acid", [], None),
    ("s52b_Rh", "catalyst", None, "[Rh(OH)(cod)]2", [("catalyst_loading", q(5, "mol%"))], None),
    ("s52b_THF", "solvent", None, "tetrahydrofuran", [], "C1CCOC1"),
    ("s52b_151", "product", "151", "syn-configured alpha-allenol", [], None),
], [("rhodium_catalyzed_ring_opening", ["s52b_147", "s52b_148", "s52b_Rh", "s52b_THF", "s52b_151"], [("temperature", q(0, "°C")), ("time", q(minimum=2, maximum=6, unit="h", raw_text="2-6 h"))])], [
    ("reported_yield_across_scheme52_conditions", q(minimum=72, maximum=86, unit="%", raw_text="72-86%"), ["s52b_151"]),
    ("syn_anti_ratio_across_scheme52_conditions", "up to 99/1", ["s52b_151"]),
    ("yield_measurement_basis", None, ["s52b_151"]),
], notes=["The displayed 72-86% and syn/anti up to 99/1 are shared across the two alternative Scheme 52 catalyst systems and are not assigned to one system."])

add("scheme53_aziridine_hydride_migration", "literature_example", E910, [
    ("s53_152", "reactant", "152", "alkynylaziridine", [], None),
    ("s53_9BBN", "reagent", None, "9-BBN", [], None),
    ("s53_THF", "solvent", None, "tetrahydrofuran", [], "C1CCOC1"),
    ("s53_154", "product", "154", "unprotected alpha-amino allene", [], None),
], [("syn_hydride_migration", ["s53_152", "s53_9BBN", "s53_THF", "s53_154"], [("temperature", "r.t."), ("time", q(1, "h"))])], [
    ("reported_yield", q(minimum=55, maximum=88, unit="%", raw_text="55-88%"), ["s53_154"]),
    ("diastereoselectivity", "anti diastereomer (major)", ["s53_154"]),
    ("yield_measurement_basis", None, ["s53_154"]),
], notes=["Structure 153 is a proposed hydride-transfer arrangement and was not recorded as an isolated product."])

add("scheme54_indium_allenylation_of_aldehydes", "literature_example", E910, [
    ("s54_155", "reactant", "155", "aliphatic or aromatic aldehyde", [], None),
    ("s54_156", "reactant", "156", "ethyl 4-bromobutynoate", [], None),
    ("s54_In", "reagent", None, "indium", [("equivalents", q(1, "equiv"))], None),
    ("s54_LiI", "reagent", None, "lithium iodide", [], None),
    ("s54_DMF", "solvent", None, "DMF", [], "CN(C)C=O"),
    ("s54_157", "product", "157", "alpha-hydroxyalkyl allenic ester", [], None),
], [("indium_allenylation", ["s54_155", "s54_156", "s54_In", "s54_LiI", "s54_DMF", "s54_157"], [])], [
    ("reported_yield", q(minimum=65, maximum=93, unit="%", raw_text="65-93%"), ["s54_157"]),
    ("yield_measurement_basis", None, ["s54_157"]),
])

add("scheme55_beta_lactam_allenylation", "literature_example", E910, [
    ("s55_158", "reactant", "158", "4-acetoxy-2-azetidinone", [], None),
    ("s55_159", "reactant", "159", "1,6-dibromo-2,4-hexadiyne", [], None),
    ("s55_In", "reagent", None, "indium", [], None),
    ("s55_LiCl", "reagent", None, "lithium chloride", [], None),
    ("s55_DMF", "solvent", None, "DMF", [], "CN(C)C=O"),
    ("s55_160", "product", "160", "2-azetidinone bearing a 1,2,4,5-hexatetraen-3-yl group", [], None),
], [("indium_mediated_coupling", ["s55_158", "s55_159", "s55_In", "s55_LiCl", "s55_DMF", "s55_160"], [])], [
    ("reported_yield", q(minimum=45, maximum=63, unit="%", raw_text="45-63%"), ["s55_160"]),
    ("yield_measurement_basis", None, ["s55_160"]),
])

add("scheme56_formaldehyde_difluoroallene", "literature_example", E910, [
    ("s56a_161", "reactant", "161", "difluoro-substituted propargyl bromide", [], None),
    ("s56a_In", "reagent", None, "indium", [], None),
    ("s56a_HCHO", "reactant", None, "formaldehyde", [], "C=O"),
    ("s56a_H2O", "solvent", None, "water", [], "O"),
    ("s56a_THF", "solvent", None, "tetrahydrofuran", [], "C1CCOC1"),
    ("s56a_163", "product", "163", "hydroxymethyl difluoroallene", [], None),
], [("indium_mediated_coupling", ["s56a_161", "s56a_In", "s56a_HCHO", "s56a_H2O", "s56a_THF", "s56a_163"], [])], notes=["Scheme 56 does not display a numeric yield for product 163."])

add("scheme56_brominated_difluoroallene", "literature_example", E910, [
    ("s56b_161", "reactant", "161", "difluoro-substituted propargyl bromide", [], None),
    ("s56b_In", "reagent", None, "indium", [], None),
    ("s56b_Br2", "reactant", None, "bromine", [], "BrBr"),
    ("s56b_H2O", "solvent", None, "water", [], "O"),
    ("s56b_THF", "solvent", None, "tetrahydrofuran", [], "C1CCOC1"),
    ("s56b_162", "product", "162", "brominated difluoroallene", [], None),
], [("indium_mediated_coupling", ["s56b_161", "s56b_In", "s56b_Br2", "s56b_H2O", "s56b_THF", "s56b_162"], [])], notes=["Scheme 56 does not display a numeric yield for product 162."])

add("scheme57_chromium_asymmetric_allenylation", "literature_example", E910, [
    ("s57_164", "reactant", "164", "aldehyde", [], None),
    ("s57_165", "reactant", "165", "1-trimethylsilyl-3-bromo-2-butyne", [], None),
    ("s57_CrCl3", "catalyst", None, "chromium(III) chloride", [("catalyst_loading", q(5, "mol%"))], None),
    ("s57_166", "catalyst", "166", "carbazole tridentate ligand", [("ligand_loading", q(5, "mol%"))], None),
    ("s57_Mn", "reagent", None, "manganese", [("equivalents", q(2, "equiv"))], None),
    ("s57_TMSCl", "reagent", None, "trimethylsilyl chloride", [("equivalents", q(1.1, "equiv"))], None),
    ("s57_DIPEA", "reagent", None, "diisopropylethylamine", [("equivalents", q(0.3, "equiv"))], None),
    ("s57_MeCN", "solvent", None, "acetonitrile", [], "CC#N"),
    ("s57_HCl", "reagent", None, "hydrochloric acid", [("concentration", q(1, "M"))], None),
    ("s57_167", "product", "167", "chiral alpha-allenol", [], None),
], [("chromium_allenylation", ["s57_164", "s57_165", "s57_CrCl3", "s57_166", "s57_Mn", "s57_TMSCl", "s57_DIPEA", "s57_MeCN"], [("temperature", "r.t."), ("time", q(48, "h")), ("atmosphere", "N2")]), ("acidic_workup", ["s57_HCl", "s57_167"], [])], [
    ("reported_yield", q(minimum=58, maximum=88, unit="%", raw_text="58-88%"), ["s57_167"]),
    ("enantiomeric_excess", q(minimum=55, maximum=78, unit="%", raw_text="55-78% ee"), ["s57_167"]),
    ("yield_measurement_basis", None, ["s57_167"]),
])

# Page 11: Scheme 58.
add("scheme58_guiry_chromium_allenylation", "literature_example", (11,), [
    ("s58_168", "reactant", "168", "aldehyde", [], None),
    ("s58_169", "reactant", "169", "bromoallene", [], None),
    ("s58_CrCl3", "catalyst", None, "chromium(III) chloride", [("catalyst_loading", q(5, "mol%"))], None),
    ("s58_171", "catalyst", "171", "carbazole tridentate ligand", [("ligand_loading", q(12, "mol%"))], None),
    ("s58_Mn", "reagent", None, "manganese", [("equivalents", q(3, "equiv"))], None),
    ("s58_TMSCl", "reagent", None, "trimethylsilyl chloride", [("equivalents", q(2, "equiv"))], None),
    ("s58_THF", "solvent", None, "tetrahydrofuran", [], "C1CCOC1"),
    ("s58_170", "product", "170", "chiral beta-allenol", [], None),
], [("chromium_allenylation", ["s58_168", "s58_169", "s58_CrCl3", "s58_171", "s58_Mn", "s58_TMSCl", "s58_THF", "s58_170"], [("temperature", "r.t."), ("time", q(16, "h"))])], [
    ("reported_yield", q(minimum=40, maximum=58, unit="%", raw_text="40-58%"), ["s58_170"]),
    ("enantiomeric_excess", q(minimum=87, maximum=96, unit="%", raw_text="87-96% ee"), ["s58_170"]),
    ("yield_measurement_basis", None, ["s58_170"]),
])

# Pages 11-12: Schemes 59-70.
E1112 = (11, 12)
add("scheme59_intramolecular_propargylsilane_addition", "literature_example", E1112, [
    ("s59_172", "reactant", "172", "aldehyde-tethered propargylsilane", [], None),
    ("s59_MsOH", "reagent", None, "methanesulfonic acid", [], None),
    ("s59_CH2Cl2", "solvent", None, "dichloromethane", [], "ClCCl"),
    ("s59_173", "product", "173", "cyclic allenol", [], None),
], [("intramolecular_addition", ["s59_172", "s59_MsOH", "s59_CH2Cl2", "s59_173"], [("temperature", q(-78, "°C")), ("time", q(minimum=5, maximum=15, unit="min", raw_text="5-15 min"))])], [
    ("reported_yield", q(minimum=42, maximum=66, unit="%", raw_text="42-66%"), ["s59_173"]),
    ("diastereoselectivity", "single diastereoisomer", ["s59_173"]),
    ("yield_measurement_basis", None, ["s59_173"]),
])

add("scheme60_intramolecular_alkynyl_enolate_addition", "literature_example", E1112, [
    ("s60_174", "reactant", "174", "acetylenic omega-keto-2-alkynoate", [], None),
    ("s60_TBSOTf", "reagent", None, "tert-butyldimethylsilyl triflate", [], None),
    ("s60_NEt3", "reagent", None, "triethylamine", [], None),
    ("s60_CH2Cl2", "solvent", None, "dichloromethane", [], "ClCCl"),
    ("s60_176", "product", "176", "fused tricyclic allenoate", [], None),
], [("alkynyl_enolate_cyclization", ["s60_174", "s60_TBSOTf", "s60_NEt3", "s60_CH2Cl2", "s60_176"], [("temperature", q(25, "°C"))])], [
    ("reported_yield", q(minimum=78, maximum=90, unit="%", raw_text="78-90%"), ["s60_176"]),
    ("E_Z_ratio", "1/1.4 to 1/2.6", ["s60_176"]),
    ("yield_measurement_basis", None, ["s60_176"]),
], notes=["Structure 175 is depicted as the alkynyl-enolate intermediate and was not recorded as an isolated product."])

add("scheme61_gamma_iodination_of_alkynyl_enolate", "literature_example", E1112, [
    ("s61_177", "reactant", "177", "silyl-ether-protected alkynyl enolate precursor", [], None),
    ("s61_I2", "reagent", None, "iodine", [("equivalents", q(0.8, "equiv"))], "II"),
    ("s61_EtOH", "solvent", None, "ethanol", [], "CCO"),
    ("s61_178", "product", "178", "gamma-iodinated allenoate", [], None),
], [("gamma_iodination", ["s61_177", "s61_I2", "s61_EtOH", "s61_178"], [("temperature", q(-80, "°C")), ("time", q(5, "min"))])], [
    ("reported_yield", q(76, "%"), ["s61_178"]),
    ("yield_measurement_basis", None, ["s61_178"]),
], notes=["The review states that the corresponding unprotected alkynyl enolate did not give the desired products under the strong basic conditions."])

add("scheme62_crabbe_homologation_general", "general_scheme", E1112, [
    ("s62_alkyne", "reactant", "2-V", "terminal alkyne", [], None),
    ("s62_formaldehyde", "reactant", None, "formaldehyde", [], "C=O"),
    ("s62_iPr2NH", "reactant", None, "diisopropylamine", [], None),
    ("s62_CuBr", "catalyst", None, "copper(I) bromide", [], None),
    ("s62_dioxane", "solvent", None, "dioxane", [], "C1COCCO1"),
    ("s62_allene", "product", "2-VII", "monosubstituted allene", [], None),
], [("Crabbe_homologation", ["s62_alkyne", "s62_formaldehyde", "s62_iPr2NH", "s62_CuBr", "s62_dioxane", "s62_allene"], [("time", q(minimum=6, maximum=24, unit="h", raw_text="usually 6-24 h"))])], notes=[
    "Scheme 62 is a named general transformation and includes a proposed copper/Schiff-base intermediate 2-VI; it is not a paper-specific batch experiment."
], unresolved=[
    "Generic R group and polymeric formaldehyde notation prevent unique structures and scale.",
    "Temperature, quantities, workup, purification, and yield are not reported for the general scheme.",
    "Supporting Information was not supplied or explicitly associated.",
])

add("scheme63_microwave_crabbe_homologation", "literature_example", E1112, [
    ("s63_179", "reactant", "179", "terminal alkyne", [], None),
    ("s63_180", "reactant", "180", "paraformaldehyde", [], None),
    ("s63_CuBr", "catalyst", None, "copper(I) bromide", [("equivalents", q(0.3, "equiv"))], None),
    ("s63_HNCy2", "reactant", "182", "dicyclohexylamine", [], None),
    ("s63_dioxane", "solvent", None, "dioxane", [], "C1COCCO1"),
    ("s63_181", "product", "181", "monosubstituted allene", [], None),
], [("microwave_homologation", ["s63_179", "s63_180", "s63_CuBr", "s63_HNCy2", "s63_dioxane", "s63_181"], [("temperature", q(150, "°C")), ("time", q(minimum=1, maximum=20, unit="min", raw_text="1-20 min")), ("operation", "microwave irradiation")])], [
    ("reported_yield", q(minimum=37, maximum=95, unit="%", raw_text="37-95%"), ["s63_181"]),
    ("yield_measurement_basis", None, ["s63_181"]),
])

add("scheme64_cubr_diisopropylamine_homologation", "literature_example", E1112, [
    ("s64a_183", "reactant", "183", "isopropyl-substituted terminal alkyne", [], None),
    ("s64a_184", "reactant", "184", "paraformaldehyde", [], None),
    ("s64a_CuBr", "catalyst", None, "copper(I) bromide", [], None),
    ("s64a_iPr2NH", "reactant", None, "diisopropylamine", [], None),
    ("s64a_dioxane", "solvent", None, "dioxane", [], "C1COCCO1"),
    ("s64a_185", "product", "185", "monosubstituted allene", [], None),
], [("homologation", ["s64a_183", "s64a_184", "s64a_CuBr", "s64a_iPr2NH", "s64a_dioxane", "s64a_185"], [("temperature", "reflux"), ("time", q(minimum=1.5, maximum=3.0, unit="h", raw_text="1.5-3.0 h"))])], [
    ("reported_yield", q(minimum=27, maximum=59, unit="%", raw_text="27-59%"), ["s64a_185"]),
    ("yield_measurement_basis", None, ["s64a_185"]),
])

add("scheme64_cui_dicyclohexylamine_homologation", "literature_example", E1112, [
    ("s64b_183", "reactant", "183", "cyclohexyl-substituted terminal alkyne", [], None),
    ("s64b_184", "reactant", "184", "paraformaldehyde", [], None),
    ("s64b_CuI", "catalyst", None, "copper(I) iodide", [], None),
    ("s64b_HNCy2", "reactant", None, "dicyclohexylamine", [], None),
    ("s64b_dioxane", "solvent", None, "dioxane", [], "C1COCCO1"),
    ("s64b_185", "product", "185", "monosubstituted allene", [], None),
], [("homologation", ["s64b_183", "s64b_184", "s64b_CuI", "s64b_HNCy2", "s64b_dioxane", "s64b_185"], [("temperature", "reflux"), ("time", q(minimum=1.5, maximum=3.0, unit="h", raw_text="1.5-3.0 h"))])], [
    ("reported_yield", q(minimum=42, maximum=98, unit="%", raw_text="42-98%"), ["s64b_185"]),
    ("yield_measurement_basis", None, ["s64b_185"]),
])

add("scheme65_zni2_disubstituted_allene", "literature_example", E1112, [
    ("s65_186", "reactant", "186", "terminal alkyne", [], None),
    ("s65_187", "reactant", "187", "aldehyde", [], None),
    ("s65_188", "reactant", "188", "morpholine", [], "C1COCCN1"),
    ("s65_ZnI2", "reagent", None, "zinc iodide", [("equivalents", q(0.8, "equiv"))], None),
    ("s65_toluene", "solvent", None, "toluene", [], "Cc1ccccc1"),
    ("s65_189", "product", "189", "1,3-disubstituted allene", [], None),
], [("zinc_iodide_mediated_homologation", ["s65_186", "s65_187", "s65_188", "s65_ZnI2", "s65_toluene", "s65_189"], [("temperature", q(130, "°C"))])], [
    ("reported_yield", q(minimum=30, maximum=65, unit="%", raw_text="30-65%"), ["s65_189"]),
    ("yield_measurement_basis", None, ["s65_189"]),
])

add("scheme66_palladium_propargylamine_cat1", "literature_example", E1112, [
    ("s66a_190", "reactant", "190", "propargylamine derivative", [], None),
    ("s66a_Pd", "catalyst", None, "Pd2(dba)3·CHCl3", [("catalyst_loading", q(2.5, "mol%"))], None),
    ("s66a_P", "catalyst", None, "tris(pentafluorophenyl)phosphine", [("ligand_loading", q(20, "mol%"))], None),
    ("s66a_dioxane", "solvent", None, "dioxane", [], "C1COCCO1"),
    ("s66a_191", "product", "191", "mono- or 1,3-disubstituted allene", [], None),
], [("palladium_catalyzed_elimination", ["s66a_190", "s66a_Pd", "s66a_P", "s66a_dioxane", "s66a_191"], [("temperature", q(100, "°C"))])], [
    ("reported_yield", None, ["s66a_191"]),
], notes=["Scheme 66 reports 36-99% across cat 1 or cat 2 conditions without assigning that full range to one catalyst system; the review prose states up to 99% for monosubstituted allenes and 36-68% for 1,3-disubstituted allenes."])

add("scheme66_palladium_propargylamine_cat2", "literature_example", E1112, [
    ("s66b_190", "reactant", "190", "propargylamine derivative", [], None),
    ("s66b_Pd", "catalyst", None, "palladium(II) acetate", [("catalyst_loading", q(5, "mol%"))], None),
    ("s66b_P", "catalyst", None, "bis(pentafluorophenylphosphino)benzene ligand shown in Scheme 66", [("ligand_loading", q(5, "mol%"))], None),
    ("s66b_CHCl3", "solvent", None, "chloroform", [], "ClC(Cl)Cl"),
    ("s66b_191", "product", "191", "mono- or 1,3-disubstituted allene", [], None),
], [("palladium_catalyzed_elimination", ["s66b_190", "s66b_Pd", "s66b_P", "s66b_CHCl3", "s66b_191"], [("temperature", q(100, "°C"))])], [
    ("reported_yield", None, ["s66b_191"]),
], notes=["Scheme 66 reports 36-99% across cat 1 or cat 2 conditions without assigning that full range to one catalyst system; the review prose states up to 99% for monosubstituted allenes and 36-68% for 1,3-disubstituted allenes."])

add("scheme67_gold_chiral_propargylamine", "literature_example", E1112, [
    ("s67_192", "reactant", "192", "chiral propargylamine", [("enantiomeric_excess", q(99, "%"))], None),
    ("s67_KAuCl4", "catalyst", None, "potassium tetrachloroaurate", [("catalyst_loading", q(10, "mol%"))], None),
    ("s67_MeCN", "solvent", None, "acetonitrile", [], "CC#N"),
    ("s67_193", "product", "193", "axially chiral allene", [], None),
], [("gold_catalyzed_elimination", ["s67_192", "s67_KAuCl4", "s67_MeCN", "s67_193"], [("temperature", q(40, "°C")), ("time", q(24, "h"))])], [
    ("reported_yield", q(minimum=61, maximum=93, unit="%", raw_text="61-93%"), ["s67_193"]),
    ("enantiomeric_excess", q(minimum=50, maximum=97, unit="%", raw_text="50-97% ee"), ["s67_193"]),
    ("yield_measurement_basis", None, ["s67_193"]),
])

add("scheme68_silver_chiral_propargylamine_thermal", "literature_example", E1112, [
    ("s68a_194", "reactant", "194", "chiral propargylamine", [("enantiomeric_excess", q(99, "%"))], None),
    ("s68a_AgNO3", "catalyst", None, "silver nitrate", [("catalyst_loading", q(50, "mol%"))], None),
    ("s68a_MeCN", "solvent", None, "acetonitrile", [], "CC#N"),
    ("s68a_195", "product", "195", "axially chiral allene", [], None),
], [("silver_mediated_elimination", ["s68a_194", "s68a_AgNO3", "s68a_MeCN", "s68a_195"], [("temperature", q(40, "°C")), ("time", q(24, "h"))])], [
    ("reported_yield", None, ["s68a_195"]),
    ("enantiomeric_excess", q(91, "%", qualifier="gt", raw_text=">91% ee"), ["s68a_195"]),
], notes=["Scheme 68 reports 63-91% across the thermal or microwave conditions without assigning that full range to one mode."])

add("scheme68_silver_chiral_propargylamine_microwave", "literature_example", E1112, [
    ("s68b_194", "reactant", "194", "chiral propargylamine", [("enantiomeric_excess", q(99, "%"))], None),
    ("s68b_AgNO3", "catalyst", None, "silver nitrate", [("catalyst_loading", q(50, "mol%"))], None),
    ("s68b_MeCN", "solvent", None, "acetonitrile", [], "CC#N"),
    ("s68b_195", "product", "195", "axially chiral allene", [], None),
], [("silver_mediated_elimination", ["s68b_194", "s68b_AgNO3", "s68b_MeCN", "s68b_195"], [("temperature", q(70, "°C")), ("time", q(20, "min")), ("operation", "microwave irradiation")])], [
    ("reported_yield", None, ["s68b_195"]),
    ("enantiomeric_excess", q(91, "%", qualifier="gt", raw_text=">91% ee"), ["s68b_195"]),
], notes=["Scheme 68 reports 63-91% across the thermal or microwave conditions without assigning that full range to one mode."])

add("scheme69_gold_propargyl_benzyl_ether", "literature_example", E1112, [
    ("s69_196", "reactant", "196", "propargyl benzyl ether derivative", [], None),
    ("s69_Au", "catalyst", None, "LAu(NCPh)SbF6", [("catalyst_loading", q(4, "mol%"))], None),
    ("s69_CHCl3", "solvent", None, "chloroform", [], "ClC(Cl)Cl"),
    ("s69_197", "product", "197", "substituted allene", [], None),
], [("hydride_transfer_elimination", ["s69_196", "s69_Au", "s69_CHCl3", "s69_197"], [("temperature", q(20, "°C")), ("time", q(minimum=1, maximum=3, unit="h", raw_text="1-3 h"))])], [
    ("reported_yield", q(minimum=69, maximum=94, unit="%", raw_text="69-94%"), ["s69_197"]),
    ("yield_measurement_basis", None, ["s69_197"]),
])

add("scheme70_pdII_nucleopalladation_general", "mechanism", E1112, [
    ("s70_2VIII", "reactant", "2-VIII", "alkyne bearing a leaving group", [], None),
    ("s70_Nu", "reactant", None, "nucleophile", [], None),
    ("s70_Pd", "catalyst", None, "Pd(II)", [], None),
    ("s70_2VV", "product", "2-VVV", "functionalized allene", [], None),
], [("nucleopalladation_and_elimination", ["s70_2VIII", "s70_Nu", "s70_Pd", "s70_2VV"], [])], notes=[
    "Scheme 70 is a generic Pd(II)-initiated nucleopalladation mechanism; intermediate 2-VIV is proposed and not an isolated product."
], unresolved=[
    "Generic Nu, LG, and R groups prevent unique structures and experimental conditions.",
    "This is a general mechanistic scheme, not a reported batch experiment.",
    "Supporting Information was not supplied or explicitly associated.",
])


OUT.write_text(json.dumps(R, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"output": str(OUT), "records": len(R)}, ensure_ascii=False))
