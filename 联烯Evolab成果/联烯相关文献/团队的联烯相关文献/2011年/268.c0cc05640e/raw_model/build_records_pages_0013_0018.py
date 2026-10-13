#!/usr/bin/env python3
"""Build machine extraction records for Yu & Ma, ChemComm 2011, PDF pages 13-18."""
import json
from pathlib import Path

DOC = "doc_e77fa99a0ade23d1"
OUT = Path(__file__).with_name("records_pages_0013_0018.json")


def ev(*pages):
    out = []
    for page in pages:
        out += [f"{DOC}:page{page}:image", f"{DOC}:page{page}:text"]
    return out


def fact(value, evidence):
    return {"value": value, "evidence_ids": list(evidence) if value is not None else [],
            "verification": "unreviewed" if value is not None else "missing"}


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
    return {"entity_id": entity_id, "role": role, "label": fact(label, evidence),
            "name": fact(name, evidence), "smiles": fact(smiles, evidence),
            "smiles_parseable": None, "structure_verified": False,
            "amounts": [fld(n, v, evidence) for n, v in (amounts or [])]}


def step(step_id, participant_ids, evidence, conditions=None):
    conditions = list(conditions or [])
    names = {name for name, _ in conditions}
    if "temperature" not in names:
        conditions.append(("temperature", None))
    if "time" not in names:
        conditions.append(("time", None))
    return {"step_id": step_id, "participant_ids": participant_ids,
            "conditions": [fld(n, v, evidence) for n, v in conditions]}


DEFAULT_UNRESOLVED = [
    "This feature article summarizes cited prior literature and does not provide a full batch procedure.",
    "Exact scale, atmosphere, workup, purification, and yield measurement basis are not reported here.",
    "Generic R-group structures and stereochemistry remain machine-unverified; unsupported SMILES are null.",
    "Supporting Information was not supplied or explicitly associated.",
]


def add(rid, kind, pages, participants, steps, outcomes=(), notes=(), unresolved=None):
    evidence = ev(*pages)
    ps = [part(eid, role, label, name, evidence, amounts, smiles)
          for eid, role, label, name, amounts, smiles in participants]
    ss = [step(sid, ids, evidence, conditions) for sid, ids, conditions in steps]
    os = [fld(name, value, evidence, targets) for name, value, targets in outcomes]
    record = {
        "record_id": f"{DOC}:{rid}", "document_id": DOC, "source_reaction_id": rid,
        "record_kind": kind, "status": "candidate", "completeness": "partial",
        "evidence_ids": evidence, "participants": ps, "steps": ss, "outcomes": os,
        "notes": [fact(note, evidence) for note in notes],
        "review": {"method": "none", "reviewer": None, "checked_fields": [],
                   "unresolved": DEFAULT_UNRESOLVED if unresolved is None else unresolved},
    }
    R.append(record)


R = []

# Page 13: generic Pd pathways and Schemes 73-74.
add("scheme71_pd0_propargyl_substitution_general", "mechanism", (13,), [
    ("s71_2VIII", "reactant", "2-VIII", "propargylic substrate bearing leaving group LG", [], None),
    ("s71_Pd", "catalyst", None, "Pd(0)", [], None),
    ("s71_Nu", "reactant", None, "nucleophile or organometallic reagent", [], None),
    ("s71_2VV", "product", "2-VV", "allene from organometallic coupling branch", [], None),
    ("s71_2VVI", "product", "2-VVI", "nucleophile-substituted allene", [], None),
    ("s71_2VVII", "product", "2-VVII", "alkyne regioisomer", [], None),
], [("oxidative_addition_and_substitution", ["s71_2VIII", "s71_Pd", "s71_Nu", "s71_2VV", "s71_2VVI", "s71_2VVII"], [])],
    notes=["Scheme 71 is a generic Pd(0) oxidative-addition mechanism; 2-IV is a proposed allenylpalladium intermediate."],
    unresolved=["Generic LG, Nu, M and R groups prevent unique structures or experimental conditions.",
                "This is a general mechanistic scheme, not a batch experiment."])

add("scheme72_pd0_cross_coupling_general", "mechanism", (13,), [
    ("s72_2VVVI", "reactant", "2-VVVI", "alkenyl or aryl halide", [], None),
    ("s72_Pd", "catalyst", None, "Pd(0)", [], None),
    ("s72_propargylM", "reactant", None, "propargyl/allenyl organometallic reagent", [], None),
    ("s72_2VVV", "product", "2-VVV", "coupled allene", [], None),
], [("oxidative_addition_transmetalation_coupling", ["s72_2VVVI", "s72_Pd", "s72_propargylM", "s72_2VVV"], [])],
    notes=["Scheme 72 is a generic Pd(0) cross-coupling mechanism; 2-VVVI, 2-VVVIII and 2-VVVIV are proposed organopalladium intermediates."],
    unresolved=["Generic X, M and R groups prevent unique structures or conditions.",
                "This is a general mechanistic scheme, not a batch experiment."])

for tag, catalyst, temp in [("pd", "Pd(PPh3)4", q(25, "°C")),
                            ("ni", "Ni(PPh3)2Cl2", q(45, "°C"))]:
    add(f"scheme73_tandem_indene_allene_{tag}", "literature_example", (12, 13), [
        (f"s73{tag}_198", "reactant", "198", "propargylic carbonate-tethered benzylidene malonate", [], None),
        (f"s73{tag}_199", "reactant", "199", "arylamine", [], None),
        (f"s73{tag}_cat", "catalyst", None, catalyst, [], None),
        (f"s73{tag}_Cs2CO3", "reagent", None, "cesium carbonate", [], None),
        (f"s73{tag}_DMF", "solvent", None, "DMF", [], "CN(C)C=O"),
        (f"s73{tag}_202", "product", "202", "highly substituted indene bearing an allene", [], None),
    ], [("tandem_michael_addition_coupling", [f"s73{tag}_{x}" for x in ("198", "199", "cat", "Cs2CO3", "DMF", "202")],
         [("temperature", temp), ("atmosphere", "air" if tag == "ni" else None)])], [
        ("reported_yield_across_scheme73_conditions", q(minimum=40, maximum=80, unit="%", raw_text="40-80%"), [f"s73{tag}_202"]),
        ("yield_measurement_basis", None, [f"s73{tag}_202"]),
    ], notes=["The displayed 40-80% range spans the Pd and Ni alternatives and is not assigned to one catalyst condition."])

for tag, specs in [
    ("pd_cui", [("Pd(dba)2", [("catalyst_loading", q(0.5, "mol%"))]),
                ("CuI", [("catalyst_loading", q(1.0, "mol%"))]), ("DMF", [])]),
    ("cui", [("CuI", [("loading", q(100, "mol%"))]), ("DMSO/THF", [])]),
]:
    ps = [(f"s74{tag}_203", "reactant", "203", "silyl(stannyl)ethene", [], None),
          (f"s74{tag}_204", "reactant", "204", "propargyl bromide", [], None)]
    ids = [f"s74{tag}_203", f"s74{tag}_204"]
    for i, (name, amounts) in enumerate(specs):
        role = "solvent" if name in ("DMF", "DMSO/THF") else ("catalyst" if name != "CuI" or tag == "pd_cui" else "reagent")
        eid = f"s74{tag}_a{i}"
        ps.append((eid, role, None, name, amounts, None)); ids.append(eid)
    ps.append((f"s74{tag}_205", "product", "205", "conjugated 1,3,4-trienyl silane", [], None)); ids.append(f"s74{tag}_205")
    add(f"scheme74_trienylsilane_{tag}", "literature_example", (13,), ps,
        [("coupling", ids, [("temperature", "r.t.")])], [
            ("reported_yield_across_scheme74_conditions", q(minimum=28, maximum=81, unit="%", raw_text="28-81%"), [f"s74{tag}_205"]),
            ("yield_measurement_basis", None, [f"s74{tag}_205"]),
        ], notes=["The 28-81% range covers both displayed Scheme 74 condition sets; the review states that CuI alone was usually higher yielding. Most products were E, except butyl-substituted substrates."])

# Page 14: Schemes 75-83.
add("scheme75_zirconium_palladium_allene_coupling", "literature_example", (13, 14), [
    ("s75_206", "reactant", "206", "propargylic ether", [], None),
    ("s75_Zr", "reagent", None, "Cp2Zr(n-Bu)2", [("equivalents", q(1.6, "equiv"))], None),
    ("s75_THF", "solvent", None, "tetrahydrofuran", [], "C1CCOC1"),
    ("s75_207", "reactant", "207", "aryl iodide", [], None),
    ("s75_Pd", "catalyst", None, "Pd(PPh3)4", [("catalyst_loading", q(5, "mol%"))], None),
    ("s75_CuCl", "reagent", None, "copper(I) chloride", [("equivalents", q(1.2, "equiv"))], None),
    ("s75_210", "product", "210", "multisubstituted allene", [], None),
], [("zirconation", ["s75_206", "s75_Zr", "s75_THF"], [("temperature", q(minimum=-78, maximum=20, unit="°C", raw_text="-78 °C to rt"))]),
    ("palladium_coupling", ["s75_206", "s75_207", "s75_Pd", "s75_CuCl", "s75_210"], [])], [
    ("reported_yield", q(minimum=55, maximum=87, unit="%", raw_text="55-87%"), ["s75_210"]),
    ("yield_measurement_basis", None, ["s75_210"]),
], notes=["Structures 208 and 209 are proposed zirconium intermediates, not isolated products."])

add("scheme76_pd_coupling_cyclization", "literature_example", (13, 14), [
    ("s76_211", "reactant", "211", "propargylic carbonate", [], None),
    ("s76_212", "reactant", "212", "2-(2,3-allenyl)acetylacetate", [], None),
    ("s76_Pd", "catalyst", None, "Pd(PPh3)4", [("catalyst_loading", q(5, "mol%"))], None),
    ("s76_TBAI", "reagent", None, "tetrabutylammonium iodide", [("loading", q(10, "mol%"))], None),
    ("s76_THF", "solvent", None, "tetrahydrofuran", [], "C1CCOC1"),
    ("s76_213", "product", "213", "1,3,4-alkatrien-2-yldihydrofuran", [], None),
], [("coupling_cyclization", ["s76_211", "s76_212", "s76_Pd", "s76_TBAI", "s76_THF", "s76_213"], [("temperature", "reflux")])], [
    ("reported_yield", q(minimum=65, maximum=95, unit="%", raw_text="65-95%"), ["s76_213"]),
    ("yield_measurement_basis", None, ["s76_213"]),
])

add("scheme76_pauson_khand_product_214", "literature_example", (13, 14), [
    ("s76b_213", "reactant", "213", "1,3,4-alkatrien-2-yldihydrofuran", [], None),
    ("s76b_Rh", "catalyst", None, "[RhCl(CO)2]2", [("catalyst_loading", q(2.5, "mol%"))], None),
    ("s76b_CO", "reactant", None, "carbon monoxide", [("pressure", "1 atm")], "[C-]#[O+]"),
    ("s76b_DCE", "solvent", None, "1,2-dichloroethane", [], "ClCCCl"),
    ("s76b_214", "product", "214", "2-(dihydrofuryl)cyclopentenone derivative", [], None),
], [("pauson_khand_reaction", ["s76b_213", "s76b_Rh", "s76b_CO", "s76b_DCE", "s76b_214"], [("temperature", "r.t.")])], [
    ("reported_yield", q(minimum=71, maximum=96, unit="%", raw_text="71-96%"), ["s76b_214"]),
    ("yield_measurement_basis", None, ["s76b_214"]),
])

add("scheme77_allenyl_cyclopropane_formation", "literature_example", (13, 14), [
    ("s77_215", "reactant", "215", "propargylic carbonate", [], None),
    ("s77_216", "reactant", "216", "(2,3-butadienyl)malonate or bis(phenylsulfonyl)methane", [], None),
    ("s77_Pd", "catalyst", None, "Pd(PPh3)4", [("catalyst_loading", q(5, "mol%"))], None),
    ("s77_TBAI", "reagent", None, "tetrabutylammonium iodide", [("loading", q(10, "mol%"))], None),
    ("s77_MeCN", "solvent", None, "acetonitrile", [], "CC#N"),
    ("s77_217", "product", "217", "1,3,4-alkatrien-2-yl cyclopropane", [], None),
], [("coupling_cyclization", ["s77_215", "s77_216", "s77_Pd", "s77_TBAI", "s77_MeCN", "s77_217"], [("temperature", q(80, "°C"))])], [
    ("reported_yield", q(minimum=73, maximum=96, unit="%", raw_text="73-96%"), ["s77_217"]),
    ("yield_measurement_basis", None, ["s77_217"]),
])

add("scheme78_pdII_alkynoate_propargyl_coupling", "literature_example", (13, 14), [
    ("s78_218", "reactant", "218", "alkynoate", [], None),
    ("s78_219", "reactant", "219", "propargyl alcohol", [], None),
    ("s78_PdCl2", "reagent", None, "palladium(II) chloride", [], None),
    ("s78_PBu3", "reagent", None, "tributylphosphine", [], None),
    ("s78_HCl", "reagent", None, "hydrochloric acid", [("concentration", "3 N")], None),
    ("s78_LiCl", "reagent", None, "lithium chloride", [], None),
    ("s78_220", "product", "220", "conjugated alkenyl allene", [], None),
], [("chloropalladation_coupling", ["s78_218", "s78_219", "s78_PdCl2", "s78_PBu3", "s78_HCl", "s78_LiCl", "s78_220"], [])],
    notes=["Scheme 78 shows no numeric yield, reagent loading, solvent, time, or temperature."])

add("scheme79_negishi_coupling_e223", "literature_example", (13, 14), [
    ("s79a_221", "reactant", "221", "4-aryl-3-butyn-1-ene", [], None),
    ("s79a_LDA", "reagent", None, "LDA", [], None),
    ("s79a_ZnBr2", "reagent", None, "zinc bromide", [], None),
    ("s79a_222", "reactant", "Z-222", "(Z)-3-iodoalk-2-enoate", [], None),
    ("s79a_Pd", "catalyst", None, "[Pd(pi-allyl)Cl]2", [], None),
    ("s79a_224", "catalyst", "224", "bis(furyl)phosphine ligand", [], None),
    ("s79a_THF", "solvent", None, "tetrahydrofuran", [], "C1CCOC1"),
    ("s79a_223", "product", "E-223", "conjugated alkenyl allene E-223", [], None),
], [("lithiation", ["s79a_221", "s79a_LDA", "s79a_THF"], [("temperature", q(minimum=-78, maximum=20, unit="°C", raw_text="-78 °C to rt")), ("time", q(1, "h"))]),
    ("transmetalation", ["s79a_221", "s79a_ZnBr2"], [("temperature", "r.t."), ("time", q(minimum=20, maximum=50, unit="min", raw_text="20-50 min"))]),
    ("cross_coupling", ["s79a_221", "s79a_222", "s79a_Pd", "s79a_224", "s79a_223"], [])], [
    ("reported_yield", q(minimum=34, maximum=71, unit="%", raw_text="34-71%"), ["s79a_223"]),
    ("yield_measurement_basis", None, ["s79a_223"]),
])

add("scheme79_negishi_coupling_e225", "literature_example", (13, 14), [
    ("s79b_221", "reactant", "221", "4-aryl-3-butyn-1-ene", [], None),
    ("s79b_nBuLi", "reagent", None, "n-butyllithium", [], None),
    ("s79b_ZnBr2", "reagent", None, "zinc bromide", [], None),
    ("s79b_222", "reactant", "Z-222", "(Z)-3-iodoalk-2-enoate", [], None),
    ("s79b_Pd", "catalyst", None, "[Pd(pi-allyl)Cl]2", [], None),
    ("s79b_226", "catalyst", "226", "racemic phosphine ligand L1", [], None),
    ("s79b_THF", "solvent", None, "tetrahydrofuran", [], "C1CCOC1"),
    ("s79b_225", "product", "E-225", "conjugated alkenyl allene E-225", [], None),
], [("lithiation", ["s79b_221", "s79b_nBuLi", "s79b_THF"], [("temperature", q(-20, "°C")), ("time", q(1, "h"))]),
    ("transmetalation", ["s79b_221", "s79b_ZnBr2"], [("temperature", q(-20, "°C")), ("time", q(10, "min"))]),
    ("warming", ["s79b_221"], [("temperature", q(minimum=-20, maximum=20, unit="°C", raw_text="-20 °C to rt")), ("time", q(20, "min"))]),
    ("cross_coupling", ["s79b_221", "s79b_222", "s79b_Pd", "s79b_226", "s79b_225"], [])], [
    ("reported_yield", q(minimum=72, maximum=91, unit="%", raw_text="72-91%"), ["s79b_225"]),
    ("yield_measurement_basis", None, ["s79b_225"]),
])

add("scheme80_allenylsilane_stille_coupling", "literature_example", (13, 14), [
    ("s80_227", "reactant", "227", "aryl or alkenyl iodide", [], None),
    ("s80_228", "reactant", "228", "3-tri(n-butylstannyl)-1-(trimethylsilyl)-1-propyne", [], None),
    ("s80_Pd", "catalyst", None, "Pd2(dba)3", [("catalyst_loading", q(20, "mol%"))], None),
    ("s80_AsPh3", "reagent", None, "triphenylarsine", [("equivalents", q(0.8, "equiv"))], None),
    ("s80_CuI", "reagent", None, "copper(I) iodide", [], None),
    ("s80_DMF", "solvent", None, "DMF", [], "CN(C)C=O"),
    ("s80_231", "product", "231", "conjugated 1,1-disubstituted allenylsilane", [], None),
], [("cross_coupling", ["s80_227", "s80_228", "s80_Pd", "s80_AsPh3", "s80_CuI", "s80_DMF", "s80_231"], [])], [
    ("reported_yield", q(minimum=50, maximum=82, unit="%", raw_text="50-82%"), ["s80_231"]),
    ("yield_measurement_basis", None, ["s80_231"]),
], notes=["Structures 229 and 230 are proposed palladium intermediates and were not recorded as isolated products."])

add("scheme81_retropropargylative_arylallene", "literature_example", (13, 14), [
    ("s81_232", "reactant", "232", "homopropargylic alcohol", [], None),
    ("s81_233", "reactant", "233", "aryl bromide", [], None),
    ("s81_Pd", "catalyst", None, "Pd2(dba)3", [("catalyst_loading", q(2.5, "mol%"))], None),
    ("s81_P", "catalyst", None, "tri-n-octylphosphine", [("ligand_loading", q(20, "mol%"))], None),
    ("s81_DMA", "reagent", None, "DMA", [("loading", q(70, "mol%"))], None),
    ("s81_KOH", "reagent", None, "potassium hydroxide", [("loading", q(200, "mol%"))], None),
    ("s81_toluene", "solvent", None, "toluene", [], "Cc1ccccc1"),
    ("s81_236", "product", "236", "arylallene", [], None),
], [("retropropargylative_coupling", ["s81_232", "s81_233", "s81_Pd", "s81_P", "s81_DMA", "s81_KOH", "s81_toluene", "s81_236"], [("temperature", "reflux"), ("time", q(4, "h"))])], [
    ("reported_yield", q(minimum=56, maximum=83, unit="%", raw_text="56-83%"), ["s81_236"]),
    ("yield_measurement_basis", None, ["s81_236"]),
], notes=["Structures 234 and 235 are proposed palladium intermediates."])

add("scheme82_dppe_allene_hydrogenolysis", "literature_example", (13, 14), [
    ("s82a_237", "reactant", "237", "propargylic formate", [], None),
    ("s82a_Pd", "catalyst", None, "Pd(acac)2", [("catalyst_loading", q(5, "mol%"))], None),
    ("s82a_DPPE", "catalyst", None, "DPPE", [("ligand_loading", q(5, "mol%"))], None),
    ("s82a_toluene", "solvent", None, "toluene", [], "Cc1ccccc1"),
    ("s82a_238", "product", "238", "internal allene", [], None),
], [("decarboxylative_hydrogenolysis", ["s82a_237", "s82a_Pd", "s82a_DPPE", "s82a_toluene", "s82a_238"], [("temperature", q(50, "°C"))])], [
    ("reported_yield", q(minimum=81, maximum=97, unit="%", raw_text="81-97%"), ["s82a_238"]),
    ("allene_alkyne_ratio", "66:34 to >99:1", ["s82a_238"]),
    ("yield_measurement_basis", None, ["s82a_238"]),
])

add("scheme82_dpph_alkyne_hydrogenolysis", "literature_example", (14,), [
    ("s82b_237", "reactant", "237", "propargylic formate", [], None),
    ("s82b_Pd", "catalyst", None, "Pd(acac)2", [("catalyst_loading", q(5, "mol%"))], None),
    ("s82b_DPPH", "catalyst", None, "DPPH ligand", [], None),
    ("s82b_toluene", "solvent", None, "toluene", [], "Cc1ccccc1"),
    ("s82b_alkyne", "product", None, "corresponding alkyne", [], None),
], [("alpha_selective_hydrogenolysis", ["s82b_237", "s82b_Pd", "s82b_DPPH", "s82b_toluene", "s82b_alkyne"], [("temperature", q(50, "°C"))])],
    notes=["The prose says changing DPPE to DPPH gives alpha-selective hydrogenolysis and the corresponding alkynes; no DPPH loading, yield, or product ratio is stated."])

add("scheme83_zirconate_allenyl_ketone", "literature_example", (14,), [
    ("s83_239", "reactant", "239", "alkynylzirconate complex formed in situ", [("equivalents", q(1.5, "equiv"))], None),
    ("s83_acyl", "reactant", None, "carbonyl electrophile XCOR4", [("equivalents", q(1.0, "equiv"))], None),
    ("s83_hexane", "solvent", None, "hexane", [], None),
    ("s83_240", "product", "240", "highly substituted 2,3-allenyl ketone", [], None),
], [("acylation", ["s83_239", "s83_acyl", "s83_hexane", "s83_240"], [("temperature", q(0, "°C"))])], [
    ("reported_yield", q(minimum=40, maximum=76, unit="%", raw_text="40-76%"), ["s83_240"]),
    ("yield_measurement_basis", None, ["s83_240"]),
], notes=["The review states that 239 is formed in situ from terminal alkyne, alkyllithium reagent, and zirconocene dichloride; their individual quantities are not stated."])

# Pages 15-16: Schemes 84-97.
add("scheme84_zirconium_linear_alkyne_coupling", "literature_example", (14, 15), [
    ("s84_241", "reactant", "241", "aryl-substituted terminal alkyne", [("equivalents", q(3.0, "equiv"))], None),
    ("s84_nBuLi", "reagent", None, "n-butyllithium", [("equivalents", q(3.2, "equiv"))], None),
    ("s84_Zr", "reagent", None, "zirconocene dichloride", [("equivalents", q(1.0, "equiv"))], None),
    ("s84_ClPPh2", "reagent", None, "chlorodiphenylphosphine", [("equivalents", q(3, "equiv"))], None),
    ("s84_242", "product", "242", "conjugated bis(allene)", [], None),
], [("zirconium_promoted_linear_coupling", ["s84_241", "s84_nBuLi", "s84_Zr", "s84_ClPPh2", "s84_242"], [("temperature", "r.t.")])], [
    ("reported_yield", q(minimum=29, maximum=53, unit="%", raw_text="29-53%"), ["s84_242"]),
    ("yield_measurement_basis", None, ["s84_242"]),
])

add("scheme85_intramolecular_heck_allene", "literature_example", (15,), [
    ("s85_243", "reactant", "243", "aryl-chloride-tethered alkyne 243", [], None),
    ("s85_Pd", "catalyst", None, "palladium(II) acetate", [("catalyst_loading", q(15, "mol%"))], None),
    ("s85_Xphos", "catalyst", None, "XPhos", [("ligand_loading", q(30, "mol%"))], None),
    ("s85_Cs2CO3", "reagent", None, "cesium carbonate", [], None),
    ("s85_EtOAc", "solvent", None, "ethyl acetate", [], "CCOC(C)=O"),
    ("s85_244", "product", "244", "tricyclic pyridoisoquinoline allene", [], None),
], [("intramolecular_heck_cyclization", ["s85_243", "s85_Pd", "s85_Xphos", "s85_Cs2CO3", "s85_EtOAc", "s85_244"], [("temperature", q(140, "°C")), ("time", q(30, "min")), ("operation", "microwave irradiation")])], [
    ("reported_yield", q(minimum=36, maximum=78, unit="%", raw_text="36-78%"), ["s85_244"]),
    ("yield_measurement_basis", None, ["s85_244"]),
])

add("scheme86_gold_catalyzed_alkyne_coupling", "literature_example", (15,), [
    ("s86_245", "reactant", "245", "internal dialkyl alkyne", [], None),
    ("s86_amine", "reactant", None, "secondary amine", [("equivalents", q(0.9, "equiv"))], None),
    ("s86_terminal", "reactant", None, "terminal alkyne", [], None),
    ("s86_252", "catalyst", "252", "cationic gold complex", [("catalyst_loading", q(5, "mol%"))], None),
    ("s86_251", "product", "251", "multisubstituted allene", [], None),
], [("hydroamination", ["s86_245", "s86_amine", "s86_252"], [("temperature", q(120, "°C"))]),
    ("terminal_alkyne_addition", ["s86_245", "s86_terminal", "s86_252", "s86_251"], [("temperature", q(130, "°C"))])], [
    ("reported_yield", q(minimum=73, maximum=95, unit="%", raw_text="73-95%"), ["s86_251"]),
    ("yield_measurement_basis", None, ["s86_251"]),
], notes=["Structures 246-250 are proposed mechanistic intermediates. Unsymmetrical internal alkynes can give two regioisomeric allenes with low regioselectivity."])

add("scheme87_gold_allenylindole_cyclization", "literature_example", (15, 16), [
    ("s87_253", "reactant", "253", "3-alkynyl-bearing indole", [], None),
    ("s87_Au", "catalyst", None, "triphenylphosphinegold(I) chloride", [("catalyst_loading", q(7.5, "mol%"))], None),
    ("s87_Ag", "reagent", None, "silver hexafluoroantimonate", [("loading", q(5, "mol%"))], None),
    ("s87_DCE", "solvent", None, "1,2-dichloroethane", [], "ClCCCl"),
    ("s87_255", "product", "255", "functionalized 3-allenylindole", [], None),
], [("cyclization_fragmentation_elimination", ["s87_253", "s87_Au", "s87_Ag", "s87_DCE", "s87_255"], [("temperature", "r.t.")])], [
    ("reported_yield", q(minimum=37, maximum=83, unit="%", raw_text="37-83%"), ["s87_255"]),
    ("yield_measurement_basis", None, ["s87_255"]),
], notes=["Structure 254 is a proposed intermediate."])

add("scheme88_ambiphilic_allene_dimerization", "literature_example", (15, 16), [
    ("s88_256", "reactant", "256", "aromatic 1,2-diketone", [], None),
    ("s88_257", "reactant", "257", "methyl propiolate", [], "COC(=O)C#C"),
    ("s88_Et3N", "catalyst", None, "triethylamine", [("catalyst_loading", q(10, "mol%"))], None),
    ("s88_MeOH", "solvent", None, "methanol", [], "CO"),
    ("s88_259", "product", "259", "cyclobutane dimer of ambiphilic allene 258", [], None),
], [("allene_formation_and_dimerization", ["s88_256", "s88_257", "s88_Et3N", "s88_MeOH", "s88_259"], [])],
    notes=["Ambiphilic allene 258 is depicted in brackets and dimerizes to 259 plus other dimers when no external trapping reagent is present; no numeric yield is shown."])

add("scheme89_ruthenium_allenyl_carbamate", "literature_example", (15, 16), [
    ("s89_260", "reactant", "260", "propargyl alcohol", [], None),
    ("s89_261", "reactant", "261", "isocyanate", [], None),
    ("s89_262", "catalyst", "262", "ruthenium complex", [("catalyst_loading", q(3, "mol%"))], None),
    ("s89_BF3", "reagent", None, "boron trifluoride diethyl etherate", [("loading", q(3, "mol%"))], None),
    ("s89_toluene", "solvent", None, "toluene", [], "Cc1ccccc1"),
    ("s89_263", "product", "263", "allenyl carbamate", [], None),
    ("s89_urea", "product", None, "symmetrical urea R2NHCONHR2", [], None),
], [("carbamate_formation", ["s89_260", "s89_261", "s89_262", "s89_BF3", "s89_toluene", "s89_263", "s89_urea"], [("temperature", q(100, "°C"))])], [
    ("reported_yield", q(minimum=15, maximum=71, unit="%", raw_text="15-71%"), ["s89_263"]),
    ("symmetrical_urea_byproduct", "observed", ["s89_urea"]),
    ("recovered_starting_material", "observed", ["s89_260"]),
    ("yield_measurement_basis", None, ["s89_263"]),
])

add("scheme90_enyne_1_4_addition_general", "general_scheme", (15, 16), [
    ("s90_3I", "reactant", "3-I", "conjugated enyne", [], None),
    ("s90_NuE", "reactant", None, "1,4-addition reagent Nu-E", [], None),
    ("s90_3II", "product", "3-II", "functionalized allene", [], None),
], [("one_four_addition", ["s90_3I", "s90_NuE", "s90_3II"], [])],
    notes=["Nu-E is listed generically as RM, HX or HM."],
    unresolved=["Generic Nu-E and R groups prevent unique structures and conditions.", "This is a general scheme, not a batch experiment."])

add("scheme91_enyne_carbolithiation_general", "mechanism", (15, 16), [
    ("s91_3III", "reactant", "3-III", "conjugated enyne", [], None),
    ("s91_RLi", "reactant", None, "organolithium reagent", [], None),
    ("s91_3IV", "product", "3-IV", "allenyllithium regioisomer", [], None),
    ("s91_3V", "product", "3-V", "allenyllithium regioisomer", [], None),
], [("carbolithiation", ["s91_3III", "s91_RLi", "s91_3IV", "s91_3V"], [])],
    unresolved=["Generic R groups and alternative organolithium regioisomers prevent unique structures or conditions.", "This is a general mechanistic scheme."])

add("scheme92_microflow_aryl_allenylsilane", "literature_example", (15, 16), [
    ("s92_264", "reactant", "264", "aryl bromide", [], None),
    ("s92_nBuLi", "reagent", None, "n-butyllithium", [], None),
    ("s92_265", "reactant", "265", "conjugated enyne", [], None),
    ("s92_silane", "reactant", None, "chlorosilane Me2SiRCl", [], None),
    ("s92_THF", "solvent", None, "tetrahydrofuran", [], "C1CCOC1"),
    ("s92_Et2O", "solvent", None, "diethyl ether", [], "CCOCC"),
    ("s92_266", "product", "266", "allenylsilane", [], None),
], [("halogen_lithium_exchange", ["s92_264", "s92_nBuLi", "s92_THF"], [("temperature", q(-78, "°C")), ("time", q(60, "min")), ("operation", "integrated microflow system")]),
    ("carbolithiation", ["s92_264", "s92_265", "s92_Et2O"], [("operation", "integrated microflow system")]),
    ("silyl_trapping", ["s92_264", "s92_silane", "s92_THF", "s92_266"], [("operation", "integrated microflow system")])], [
    ("reported_yield", q(minimum=47, maximum=84, unit="%", raw_text="47-84%"), ["s92_266"]),
    ("allene_alkyne_ratio", "75/25 to >98/2", ["s92_266"]),
    ("yield_measurement_basis", None, ["s92_266"]),
])

add("scheme93_frustrated_lewis_pair_cyclic_allenes", "literature_example", (15, 16), [
    ("s93_267", "reactant", "267", "Mes2PCH2CH2B(C6F5)2 frustrated Lewis pair", [], None),
    ("s93_268", "reactant", "268", "conjugated enyne", [], None),
    ("s93_pentane", "solvent", None, "pentane", [], None),
    ("s93_269", "product", "269", "eight-membered cyclic allene 269", [], None),
    ("s93_270", "product", "270", "eight-membered cyclic allene 270", [], None),
], [("one_four_addition", ["s93_267", "s93_268", "s93_pentane", "s93_269", "s93_270"], [("temperature", "r.t.")])], [
    ("combined_reported_yield", q(80, "%"), ["s93_269", "s93_270"]),
    ("product_ratio_269_270", "1:2", ["s93_269", "s93_270"]),
    ("yield_measurement_basis", None, ["s93_269", "s93_270"]),
])

add("scheme94_base_catalyzed_michael_addition", "literature_example", (15, 16), [
    ("s94_271", "reactant", "271", "electron-deficient conjugated enyne", [], None),
    ("s94_272", "reactant", "272", "carbon pronucleophile", [], None),
    ("s94_KOH", "catalyst", None, "potassium hydroxide", [("catalyst_loading", q(10, "mol%"))], None),
    ("s94_THF", "solvent", None, "tetrahydrofuran", [], "C1CCOC1"),
    ("s94_273", "product", "273", "functionalized 1,2-allene", [], None),
], [("michael_addition", ["s94_271", "s94_272", "s94_KOH", "s94_THF", "s94_273"], [])], [
    ("reported_yield", q(minimum=55, maximum=96, unit="%", raw_text="55-96%"), ["s94_273"]),
    ("diastereomeric_ratio", "1.1/1 to 15/1", ["s94_273"]),
    ("yield_measurement_basis", None, ["s94_273"]),
])

add("scheme95_three_component_michael_cross_coupling", "literature_example", (15, 16), [
    ("s95_274", "reactant", "274", "electron-deficient conjugated enyne", [], None),
    ("s95_275", "reactant", "275", "aryl iodide", [], None),
    ("s95_276", "reactant", "276", "pronucleophile NuH", [], None),
    ("s95_Pd", "catalyst", None, "Pd(PPh3)4", [("catalyst_loading", q(5, "mol%"))], None),
    ("s95_Ag2O", "reagent", None, "silver(I) oxide", [("equivalents", q(0.6, "equiv"))], None),
    ("s95_dioxane", "solvent", None, "dioxane", [], "C1COCCO1"),
    ("s95_277", "product", "277", "tetrasubstituted allene", [], None),
], [("tandem_michael_cross_coupling", ["s95_274", "s95_275", "s95_276", "s95_Pd", "s95_Ag2O", "s95_dioxane", "s95_277"], [("temperature", q(80, "°C"))])], [
    ("reported_yield", q(minimum=37, maximum=97, unit="%", raw_text="37-97%"), ["s95_277"]),
    ("yield_measurement_basis", None, ["s95_277"]),
])

add("scheme96_copper_carbomagnesiation_trapping", "literature_example", (15, 16), [
    ("s96_278", "reactant", "278", "conjugated enyne", [], None),
    ("s96_279", "reactant", "279", "sec- or tert-alkylmagnesium chloride", [], None),
    ("s96_Cu", "catalyst", None, "Li2CuCl4", [("catalyst_loading", q(1, "mol%"))], None),
    ("s96_THF", "solvent", None, "tetrahydrofuran", [], "C1CCOC1"),
    ("s96_E", "reactant", None, "electrophile E+", [], None),
    ("s96_281", "product", "281", "electrophile-trapped allene", [], None),
], [("carbomagnesiation", ["s96_278", "s96_279", "s96_Cu", "s96_THF"], [("temperature", "r.t."), ("time", q(3, "h"))]),
    ("electrophile_trapping", ["s96_278", "s96_E", "s96_281"], [])], [
    ("reported_yield", q(minimum=68, maximum=98, unit="%", raw_text="68-98%"), ["s96_281"]),
    ("yield_measurement_basis", None, ["s96_281"]),
], notes=["Electrophiles include alkyl/allyl bromides, chlorosilanes, enones, benzoyl chlorides, and carbon dioxide. Bracketed 280 is the allenyl Grignard intermediate."])

add("scheme97_nickel_three_component_enyne_coupling", "literature_example", (15, 16), [
    ("s97_282", "reactant", "282", "conjugated enyne", [], None),
    ("s97_283", "reactant", "283", "organozinc reagent R3Zn", [], None),
    ("s97_284", "reactant", "284", "alkyl halide", [], None),
    ("s97_Ni", "catalyst", None, "Ni(acac)2", [("catalyst_loading", q(8, "mol%"))], None),
    ("s97_dppb", "catalyst", None, "dppb", [("ligand_loading", q(10, "mol%"))], None),
    ("s97_THF", "solvent", None, "tetrahydrofuran", [], "C1CCOC1"),
    ("s97_285", "product", "285", "three-component allene product", [], None),
], [("three_component_coupling", ["s97_282", "s97_283", "s97_284", "s97_Ni", "s97_dppb", "s97_THF", "s97_285"], [])], [
    ("reported_yield", q(minimum=50, maximum=78, unit="%", raw_text="50-78%"), ["s97_285"]),
    ("yield_measurement_basis", None, ["s97_285"]),
])

# Pages 17-18: Schemes 98-109.
add("scheme98_cross_coupling_1_1_diarylallene", "literature_example", (16, 17), [
    ("s98a_286", "reactant", "286", "4-aryl-3-butyn-1-ene", [], None),
    ("s98a_RLi", "reactant", None, "organolithium reagent", [], None),
    ("s98a_ZnBr2", "reagent", None, "zinc bromide", [], None),
    ("s98a_Pd", "catalyst", None, "Pd(PPh3)4", [], None),
    ("s98a_ArI", "reactant", None, "aryl iodide", [], None),
    ("s98a_287", "product", "287", "1,1-diarylallene", [], None),
], [("conjugate_addition_transmetalation_coupling", ["s98a_286", "s98a_RLi", "s98a_ZnBr2", "s98a_Pd", "s98a_ArI", "s98a_287"], [])], [
    ("reported_yield", q(minimum=70, maximum=98, unit="%", raw_text="70-98%"), ["s98a_287"]),
    ("yield_measurement_basis", None, ["s98a_287"]),
])

add("scheme98_hmpa_cross_coupling_1_3_diarylallene", "literature_example", (16, 17), [
    ("s98b_286", "reactant", "286", "4-aryl-3-butyn-1-ene", [], None),
    ("s98b_RLi", "reactant", None, "organolithium reagent", [], None),
    ("s98b_HMPA", "reagent", None, "HMPA", [], None),
    ("s98b_ZnBr2", "reagent", None, "zinc bromide", [], None),
    ("s98b_Pd", "catalyst", None, "Pd(PPh3)4", [], None),
    ("s98b_ArI", "reactant", None, "aryl iodide", [], None),
    ("s98b_288", "product", "288", "1,3-diarylallene", [], None),
], [("hmpa_controlled_conjugate_addition_coupling", ["s98b_286", "s98b_RLi", "s98b_HMPA", "s98b_ZnBr2", "s98b_Pd", "s98b_ArI", "s98b_288"], [])], [
    ("reported_yield", q(minimum=52, maximum=88, unit="%", raw_text="52-88%"), ["s98b_288"]),
    ("yield_measurement_basis", None, ["s98b_288"]),
])

add("scheme99_carbomagnesiation_defluorometallation", "literature_example", (17,), [
    ("s99_289", "reactant", "E-289", "5-perfluoroalkylpenta-4(E)-en-2-ynol", [], None),
    ("s99_290", "reactant", "290", "Grignard reagent R2MgX", [], None),
    ("s99_Et2O", "solvent", None, "diethyl ether", [], "CCOCC"),
    ("s99_291", "product", "Z-291", "6-perfluoroalkyl-6-fluoro-2,3,5(Z)-alkatrienol", [], None),
], [("carbomagnesiation_anti_defluorometallation", ["s99_289", "s99_290", "s99_Et2O", "s99_291"], [("temperature", "r.t."), ("time", q(minimum=2, maximum=2.5, unit="h", raw_text="2-2.5 h"))])], [
    ("reported_yield", q(minimum=66, maximum=95, unit="%", raw_text="66-95%"), ["s99_291"]),
    ("stereoselectivity", "Z-selective", ["s99_291"]),
    ("yield_measurement_basis", None, ["s99_291"]),
])

for tag, catalyst_specs, temp in [
    ("pt_dba", [("Pt2(dba)3", [("catalyst_loading", q(2.5, "mol%"))])], q(80, "°C")),
    ("pt_acac", [("Pt(acac)2", [("catalyst_loading", q(5, "mol%"))]),
                 ("POCy3", [("ligand_loading", q(10, "mol%"))]), ("DIBAL-H", [])], q(minimum=60, maximum=100, unit="°C", raw_text="60-100 °C")),
]:
    ps = [(f"s100{tag}_292", "reactant", "292", "conjugated enyne", [], None),
          (f"s100{tag}_293", "reactant", "293", "silylborane PhMe2Si-B(pin)", [], None),
          (f"s100{tag}_toluene", "solvent", None, "toluene", [], "Cc1ccccc1")]
    ids = [f"s100{tag}_292", f"s100{tag}_293", f"s100{tag}_toluene"]
    for i, (name, amounts) in enumerate(catalyst_specs):
        eid = f"s100{tag}_a{i}"; ps.append((eid, "catalyst" if name.startswith("Pt") or name == "POCy3" else "reagent", None, name, amounts, None)); ids.append(eid)
    ps.append((f"s100{tag}_294", "product", "294", "boron- and silyl-substituted allene", [], None)); ids.append(f"s100{tag}_294")
    add(f"scheme100_silaboration_{tag}", "literature_example", (17, 18), ps,
        [("silaboration", ids, [("temperature", temp)])], [
            ("reported_yield_across_scheme100_conditions", q(minimum=47, maximum=93, unit="%", raw_text="47-93%"), [f"s100{tag}_294"]),
            ("yield_measurement_basis", None, [f"s100{tag}_294"]),
        ], notes=["The displayed 47-93% range spans both Scheme 100 catalyst systems and is not mapped to one alternative."])

add("scheme101_rhodium_asymmetric_enynamide_addition", "literature_example", (17, 18), [
    ("s101_295", "reactant", "295", "enynamide", [], None),
    ("s101_296", "reactant", "296", "arylboronic acid", [], None),
    ("s101_Rh", "catalyst", None, "[RhCl((S,S)-tfb*)]2", [("catalyst_loading", q(5, "mol%"))], None),
    ("s101_297", "catalyst", "297", "chiral diene ligand (S,S)-tfb*", [], None),
    ("s101_K3PO4", "reagent", None, "potassium phosphate", [], None),
    ("s101_solvent", "solvent", None, "1,4-dioxane/water", [], None),
    ("s101_298", "product", "298", "axially chiral allenylsilane", [], None),
], [("asymmetric_aryl_addition", ["s101_295", "s101_296", "s101_Rh", "s101_297", "s101_K3PO4", "s101_solvent", "s101_298"], [("temperature", q(50, "°C"))])], [
    ("reported_yield", q(minimum=70, maximum=89, unit="%", raw_text="70-89%"), ["s101_298"]),
    ("enantiomeric_excess", q(minimum=94, maximum=99, unit="%", raw_text="94-99% ee"), ["s101_298"]),
    ("yield_measurement_basis", None, ["s101_298"]),
])

add("scheme102_intramolecular_hydroamination", "literature_example", (17, 18), [
    ("s102_299", "reactant", "299", "trans-enynyl amine", [], None),
    ("s102_nBuLi", "catalyst", None, "n-butyllithium", [("catalyst_loading", q(20, "mol%"))], None),
    ("s102_300", "product", "300", "allene-substituted pyrrolidine", [], None),
], [("intramolecular_hydroamination", ["s102_299", "s102_nBuLi", "s102_300"], [])], [
    ("reported_yield", q(minimum=70, maximum=95, unit="%", raw_text="70-95%"), ["s102_300"]),
    ("diastereomeric_ratio", "1/1 to 5/1", ["s102_300"]),
    ("yield_measurement_basis", None, ["s102_300"]),
])

add("scheme103_bromolactonization", "literature_example", (17, 18), [
    ("s103_301", "reactant", "301", "conjugated enynyl acid", [], None),
    ("s103_DABCO", "catalyst", None, "DABCO", [("catalyst_loading", q(2, "mol%"))], None),
    ("s103_NBS", "reagent", None, "N-bromosuccinimide", [], None),
    ("s103_CHCl3", "solvent", None, "chloroform", [], "ClC(Cl)Cl"),
    ("s103_302", "product", "302", "bromoallene-tethered lactone", [], None),
], [("syn_1_4_bromolactonization", ["s103_301", "s103_DABCO", "s103_NBS", "s103_CHCl3", "s103_302"], [])], [
    ("reported_yield", q(minimum=17, maximum=97, unit="%", raw_text="17-97%"), ["s103_302"]),
    ("diastereomeric_ratio", "10/1 to >20/1", ["s103_302"]),
    ("yield_measurement_basis", None, ["s103_302"]),
])

add("scheme104_asymmetric_bromolactonization", "literature_example", (17, 18), [
    ("s104_303", "reactant", "303", "conjugated (Z)-enynyl acid", [], None),
    ("s104_NBS", "reagent", "304", "N-bromosuccinimide", [], None),
    ("s104_305", "catalyst", "305", "cinchonidine-derived bifunctional catalyst", [("catalyst_loading", q(20, "mol%"))], None),
    ("s104_DCE", "solvent", None, "1,2-dichloroethane", [], "ClCCCl"),
    ("s104_306", "product", "306", "axially chiral bromoallene-tethered lactone", [], None),
], [("asymmetric_syn_1_4_bromolactonization", ["s104_303", "s104_NBS", "s104_305", "s104_DCE", "s104_306"], [("temperature", "r.t.")])], [
    ("diastereomeric_ratio", "10:1 to 20:1", ["s104_306"]),
    ("enantiomeric_excess", q(minimum=80, maximum=99, unit="%", raw_text="80-99% ee"), ["s104_306"]),
], notes=["Scheme 104 shows NBS as reagent 304, bifunctional catalyst 305, and product 306; no numeric product yield is shown."])

add("scheme105_zirconocene_enyne_aldehyde_coupling", "literature_example", (17, 18), [
    ("s105_307", "reactant", "307", "alkyl-substituted conjugated enyne", [], None),
    ("s105_Zr", "reagent", None, "zirconocene-ethylene complex", [], None),
    ("s105_THF", "solvent", None, "tetrahydrofuran", [], "C1CCOC1"),
    ("s105_RCHO", "reactant", None, "aldehyde R3CHO", [], None),
    ("s105_311", "product", "311", "beta-hydroxyallene", [], None),
], [("cyclometallation", ["s105_307", "s105_Zr", "s105_THF"], [("temperature", "r.t."), ("time", q(2, "h"))]),
    ("aldehyde_addition", ["s105_307", "s105_RCHO", "s105_311"], [("temperature", "r.t."), ("time", q(minimum=3, maximum=6, unit="h", raw_text="3-6 h"))])], [
    ("reported_yield", q(minimum=53, maximum=72, unit="%", raw_text="53-72%"), ["s105_311"]),
    ("diastereomeric_ratio", "88/12 to 98/2", ["s105_311"]),
    ("yield_measurement_basis", None, ["s105_311"]),
], notes=["Structures 308-310 are proposed zirconium intermediates."])

add("scheme106_claisen_cope_general", "general_scheme", (17, 18), [
    ("s106_3VI", "reactant", "3-VI", "propargyl vinyl ether or related heteroenynyl substrate", [], None),
    ("s106_3VII", "product", "3-VII", "beta-allenic carbonyl or related product", [], None),
], [("three_three_sigmatropic_rearrangement", ["s106_3VI", "s106_3VII"], [("operation", "thermal or catalytic activation")])],
    unresolved=["Generic X and R groups prevent unique structures and conditions.", "This is a general rearrangement scheme, not a batch experiment."])

add("scheme107_thermal_claisen_oxindole", "literature_example", (17, 18), [
    ("s107_312", "reactant", "312", "indolinone-tethered vinyl propargyl ether", [], None),
    ("s107_chlorobenzene", "solvent", None, "chlorobenzene", [], "Clc1ccccc1"),
    ("s107_313", "product", "313", "allene-appended oxindole", [], None),
], [("thermal_claisen_rearrangement", ["s107_312", "s107_chlorobenzene", "s107_313"], [("temperature", q(135, "°C")), ("time", q(4, "h"))])], [
    ("reported_yield", q(minimum=59, maximum=84, unit="%", raw_text="59-84%"), ["s107_313"]),
    ("yield_measurement_basis", None, ["s107_313"]),
])

add("scheme108_orthoester_claisen_allenyl_halide", "literature_example", (17, 18), [
    ("s108_314", "reactant", "314", "chiral 3-halo propargyl alcohol", [], None),
    ("s108_ortho", "reactant", None, "triethyl orthoacetate", [("equivalents", q(2, "equiv"))], None),
    ("s108_HOAc", "catalyst", None, "HOAc (arrow label)", [("catalyst_loading", q(5, "mol%"))], None),
    ("s108_toluene", "solvent", None, "toluene", [], "Cc1ccccc1"),
    ("s108_316", "product", "316", "enantiomerically enriched allenyl halide", [], None),
], [("orthoester_claisen_rearrangement", ["s108_314", "s108_ortho", "s108_HOAc", "s108_toluene", "s108_316"], [("temperature", q(100, "°C")), ("time", q(18, "h"))])], [
    ("reported_yield", q(minimum=35, maximum=55, unit="%", raw_text="35-55%"), ["s108_316"]),
    ("enantiomeric_ratio", ">93/7 er", ["s108_316"]),
    ("yield_measurement_basis", None, ["s108_316"]),
], notes=["Structure 315 is a proposed boat transition state.", "The Scheme 108 arrow labels 5 mol% HOAc, while the adjacent review prose calls the catalytic acid propionic acid; the source-level conflict is unresolved."],
    unresolved=DEFAULT_UNRESOLVED + ["Scheme 108 conflicts internally: the arrow says HOAc, whereas the prose says propionic acid."])

add("scheme109_chelation_controlled_allenylglycine", "literature_example", (17, 18), [
    ("s109_317", "reactant", "317", "alpha-acyloxy-alpha-alkynylsilane", [], None),
    ("s109_LDA", "reagent", None, "LDA", [("equivalents", q(3, "equiv"))], None),
    ("s109_ZnCl2", "reagent", None, "zinc chloride", [("equivalents", q(1.2, "equiv"))], None),
    ("s109_THF", "solvent", None, "tetrahydrofuran", [], "C1CCOC1"),
    ("s109_319", "product", "319", "optically active alpha-(allenyl)glycine derivative", [], None),
], [("enolate_formation_and_claisen_rearrangement", ["s109_317", "s109_LDA", "s109_ZnCl2", "s109_THF", "s109_319"], [("temperature", q(minimum=-78, maximum=20, unit="°C", raw_text="-78 °C to rt"))]),
    ("warming", ["s109_317", "s109_319"], [("temperature", "r.t.")])], [
    ("reported_yield", q(minimum=46, maximum=78, unit="%", raw_text="46-78%"), ["s109_319"]),
    ("diastereomeric_ratio", ">20:1", ["s109_319"]),
    ("yield_measurement_basis", None, ["s109_319"]),
], notes=["Structure 318 is a proposed chelated intermediate; the review states that the bulky silyl group can subsequently be removed with TBAF but gives no conditions here."])

OUT.write_text(json.dumps(R, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"output": str(OUT), "records": len(R)}, ensure_ascii=False))
