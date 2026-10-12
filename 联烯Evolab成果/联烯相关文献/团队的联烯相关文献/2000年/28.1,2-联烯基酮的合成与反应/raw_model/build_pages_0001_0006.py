#!/usr/bin/env python3
"""Build evidence-linked review records for source.pdf pages 1-6.

The source is a review article.  Concrete arrows are therefore classified as
literature examples, while generic transformations and proposed pathways are
kept as general-scheme or mechanism records.  No structure is certified.
"""
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "runs/current"
DOC = "doc_6485e9f6c591416c"


def fact(value, page=None):
    if value is None:
        return {"value": None, "evidence_ids": [], "verification": "missing"}
    ev = [] if page is None else [f"{DOC}:page{page}:text", f"{DOC}:page{page}:image"]
    return {"value": value, "evidence_ids": ev, "verification": "unreviewed"}


def field(name, value, page):
    return {"name": name, "fact": fact(value, page)}


def participant(entity_id, role, label, name, page):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, page),
        "name": fact(name, page),
        "smiles": fact(None),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": [],
    }


records = []
by_page = {i: [] for i in range(1, 7)}


def add(page, suffix, kind, source_id, parts, conditions=None, outcomes=None,
        notes=None, unresolved=None, steps=None):
    rid = f"{DOC}:{suffix}"
    ps = [participant(f"{suffix}_{i+1}", *p, page) for i, p in enumerate(parts)]
    if steps is None:
        cond = [field(k, v, page) for k, v in (conditions or {}).items()]
        cond += [
            field("reaction_scale", None, page),
            field("atmosphere", None, page),
            field("workup", None, page),
            field("purification", None, page),
        ]
        step_data = [{
            "step_id": "step1",
            "participant_ids": [p["entity_id"] for p in ps],
            "conditions": cond,
        }]
    else:
        step_data = []
        for j, spec in enumerate(steps, 1):
            step_data.append({
                "step_id": f"step{j}",
                "participant_ids": [p["entity_id"] for p in ps],
                "conditions": [field(k, v, page) for k, v in spec.items()],
            })
    outs = [field(k, v, page) for k, v in (outcomes or {}).items()]
    if not any(x["name"] == "yield_measurement_basis" for x in outs):
        outs.append(field("yield_measurement_basis", None, page))
    base_unresolved = [
        "Exact drawing-derived structures and R-group identities are unverified; SMILES are intentionally null.",
        "The review omits experiment scale, atmosphere, workup, purification, and usually the yield basis.",
        "No supporting-information file is supplied or associated in this pilot.",
    ]
    rec = {
        "record_id": rid,
        "document_id": DOC,
        "source_reaction_id": source_id,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": [f"{DOC}:page{page}:text", f"{DOC}:page{page}:image"],
        "participants": ps,
        "steps": step_data,
        "outcomes": outs,
        "notes": [fact(x, page) for x in (notes or [])],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": base_unresolved + (unresolved or []),
        },
    }
    records.append(rec)
    by_page[page].append(rid)


# Page 2: Schemes 1-3.  All concrete arrows summarize cited work.
add(2, "p02_s01_oxidation_1_to_2", "literature_example", "Scheme 1, oxidation",
    [("reactant", "1", "homopropargylic alcohol family"),
     ("product", "2", "beta,gamma-unsaturated propargyl ketone family")],
    {"transformation": "oxidation", "reported_oxidant_families": "DMP, Cr(IV) reagents, or Swern oxidation"},
    notes=["The prose lists several cited oxidation systems; no single substrate-specific run is reported here."],
    unresolved=["Which cited oxidant applies to a particular R-group example is not specified."])
add(2, "p02_s01_isomerization_2_to_3", "literature_example", "Scheme 1, isomerization",
    [("reactant", "2", "propargyl ketone family"), ("product", "3", "1,2-allenyl ketone family")],
    {"transformation": "isomerization", "reported_conditions": "base (NaHCO3 or Et3N) or silica/alumina chromatography"},
    notes=["The Hashmi example is described as DMP oxidation followed directly by chromatography."],
    unresolved=["The generic scheme does not map individual bases or chromatography media to exact R groups."])
add(2, "p02_s02_ester_grignard", "literature_example", "Scheme 2, top arrow",
    [("reactant", "4", "allenyl/propargyl Grignard reagent family"),
     ("reactant", "RCO2Et", "ethyl ester family"),
     ("product", "5", "allenyl ketone family"),
     ("product", "6", "propargyl ketone isomer family")],
    {"solvent": "Et2O", "temperature": "-78 °C"},
    {"reported_yield": "30%-65%"},
    notes=["The displayed outcome is a mixture of allenyl ketone 5 and propargyl ketone 6."],
    unresolved=["The printed yield is not allocated between products 5 and 6."])
add(2, "p02_s02_bromide_amide_magnesium", "literature_example", "Scheme 2, middle arrow",
    [("reactant", "7", "substituted propargyl bromide family"),
     ("reactant", "8", "N,N-dimethylbenzamide"),
     ("reagent", "Mg", "magnesium"),
     ("product", "9", "allenyl phenyl ketone family"),
     ("product", "10", "propargyl phenyl ketone isomer family")],
    {"reagent": "Mg"},
    notes=["The scheme depicts both allenyl and propargyl ketone products."],
    unresolved=["Product-specific yields and operating conditions are not printed."])
add(2, "p02_s02_weinreb_grignard", "literature_example", "Scheme 2, bottom arrow",
    [("reactant", "11", "aromatic N-methoxy-N-methyl amide family"),
     ("reactant", "12", "propargylmagnesium bromide"),
     ("product", "13", "aryl allenyl ketone family")],
    {"reagent": "propargylmagnesium bromide"},
    notes=["The review text groups this route with organometallic addition to amides."],
    unresolved=["The scheme does not print a row-specific yield."])
add(2, "p02_s03_lithiation_14_to_15", "literature_example", "Scheme 3, lithiation",
    [("reactant", "14", "halo- or hydrogen-substituted allene family; X = H, Br, I"),
     ("reagent", "n-BuLi", "n-butyllithium"),
     ("product", "15", "allenyllithium intermediate family")],
    {"reagent": "n-BuLi"},
    unresolved=["No temperature, time, or isolated status of intermediate 15 is printed."])
add(2, "p02_s03_acylation_15_to_16", "literature_example", "Scheme 3, acylation",
    [("reactant", "15", "allenyllithium intermediate family"),
     ("reactant", "R4CONMe2", "N,N-dimethylamide family"),
     ("product", "16", "allenyl ketone family")],
    {"acylating_agent": "R4CONMe2"},
    {"reported_yield": "62%-86%"},
    unresolved=["The range is family-level and is not assigned to individual R-group combinations."])

# Page 3: Schemes 4-9.
add(3, "p03_s04_propargylmercury_acylation", "literature_example", "Scheme 4, upper arrow",
    [("reactant", "17", "propargylmercury iodide family"), ("reactant", "R'COCl", "acyl chloride family"),
     ("catalyst", "AlCl3", "aluminum chloride"), ("product", "18", "allenyl ketone family")],
    {"catalyst": "AlCl3"})
add(3, "p03_s04_allenylmercury_acylation", "literature_example", "Scheme 4, lower arrow",
    [("reactant", "19", "allenylmercury iodide family"), ("reactant", "R'COCl", "acyl chloride family"),
     ("catalyst", "AlCl3", "aluminum chloride"), ("product", "20", "propargyl ketone family")],
    {"catalyst": "AlCl3"})
add(3, "p03_s04_isomerization_20_to_18", "literature_example", "Scheme 4, vertical isomerization",
    [("reactant", "20", "propargyl ketone family"), ("product", "18", "allenyl ketone family")],
    {"transformation": "isomerization"},
    unresolved=["No separate condition is printed for the vertical 20-to-18 arrow."])
add(3, "p03_s05_cuprate_substitution_21_to_22", "literature_example", "Scheme 5, organocopper formation",
    [("reactant", "21", "propargyl acetate family"), ("reagent", "R3_2CuLi", "lithium diorganocuprate family"),
     ("product", "22", "allenylcopper intermediate family")],
    {"reagent": "R3_2CuLi"},
    unresolved=["Intermediate 22 is depicted but its isolated or in-situ status is not stated."])
add(3, "p03_s05_anhydride_acylation_22_to_23", "literature_example", "Scheme 5, anhydride acylation",
    [("reactant", "22", "allenylcopper intermediate family"),
     ("reactant", "(R4CO)2O", "acid anhydride family"),
     ("product", "23", "propargyl ketone family")],
    {"acylating_agent": "(R4CO)2O"})
add(3, "p03_s05_proton_shift_23_to_24", "literature_example", "Scheme 5, R2 = H conversion",
    [("reactant", "23", "propargyl ketone family"), ("product", "24", "allenyl ketone family")],
    {"structural_constraint": "R2 = H", "transformation": "proton transfer/isomerization"})
add(3, "p03_s06_overall_manganese_route", "literature_example", "Scheme 6, overall route",
    [("reactant", "25", "2-alkynyl ketone family; E = COCH3"),
     ("reagent", "26", "organomanganese reagent MnL3(THF)"),
     ("product", "29", "allenyl ketone family")],
    {"sequence": "MnL3(THF), then Al2O3, then Ce4+"},
    notes=["The scheme condenses coordination, alumina-induced rearrangement, and Ce4+ oxidation."],
    unresolved=["No overall yield or stage-specific operating details are printed."])
add(3, "p03_s06_manganese_intermediates", "mechanism", "Scheme 6, complexes 27-28",
    [("reactant", "25", "2-alkynyl ketone family"), ("reagent", "26", "MnL3(THF)"),
     ("unspecified_agent", "27", "alkyne-manganese complex"),
     ("unspecified_agent", "28", "allene-manganese complex"),
     ("product", "29", "allenyl ketone family")],
    {"proposed_or_condensed_path": "25 + 26 -> 27 (-THF); Al2O3 -> 28; Ce4+ -> 29"},
    notes=["Complexes 27 and 28 are retained as pathway species, not certified isolated experiments."],
    unresolved=["The review does not state direct observation or isolation evidence for both complexes."])
add(3, "p03_s07_mno2_oxidation", "literature_example", "Scheme 7, MnO2 arrow",
    [("reactant", "30", "specific allenyl alcohol"), ("reagent", "MnO2", "manganese dioxide"),
     ("product", "31", "corresponding allenyl ketone")], {"oxidant": "MnO2"})
add(3, "p03_s07_swern_oxidation", "literature_example", "Scheme 7, Swern arrow",
    [("reactant", "32", "allenyl alcohol family"), ("reagent", "Swern", "Swern oxidation system"),
     ("product", "33", "allenyl ketone family")], {"oxidation": "Swern"})
add(3, "p03_s07_nio14_oxidation", "literature_example", "Scheme 7, NiO1.4 arrow",
    [("reactant", "34", "allenyl alcohol family"), ("reagent", "NiO1.4", "nickel oxide oxidant"),
     ("product", "35", "allenyl ketone family")], {"oxidant": "NiO1.4"})
add(3, "p03_s08_overall_23_rearrangement", "literature_example", "Scheme 8, overall synthesis",
    [("reactant", "36", "alpha-hydroxy nitrile family"), ("reactant", "37", "propargyl bromide family"),
     ("product", "40", "allenyl ketone family")],
    {"ether_formation_conditions": "CH2Cl2, NaOH, H2O, R3R'N+Cl-", "rearrangement_conditions": "LDA, THF, -78 °C; then H2O"},
    {"reported_yield": "50%-60%"},
    unresolved=["The printed yield appears on the rearrangement stage; its exact basis is not stated."])
add(3, "p03_s08_rearrangement_mechanism", "mechanism", "Scheme 8, intermediate 39",
    [("reactant", "38", "propargyl ether intermediate"), ("unspecified_agent", "39", "[2,3]-rearrangement transition/intermediate depiction"),
     ("product", "40", "allenyl ketone family")],
    {"conditions": "LDA, THF, -78 °C, loss of LiCl; then H2O"},
    notes=["Curved arrows around 39 depict the proposed [2,3]-rearrangement pathway."])
add(3, "p03_s09_overall_ammonium_route", "literature_example", "Scheme 9, overall synthesis",
    [("reactant", "41", "alpha-cyano tertiary amine family"), ("reactant", "37", "propargyl bromide family"),
     ("product", "45", "allenyl ketone family")],
    {"sequence": "quaternization; t-BuOK rearrangement; Cu2+/H2O conversion"},
    {"reported_yield": "60%"})
add(3, "p03_s09_rearrangement_mechanism", "mechanism", "Scheme 9, intermediates 42-44",
    [("reactant", "42", "quaternary ammonium salt"), ("unspecified_agent", "43", "ylide/rearrangement depiction"),
     ("unspecified_agent", "44", "allenic amine intermediate"), ("product", "45", "allenyl ketone family")],
    {"conditions": "t-BuOK, then Cu2+/H2O"},
    notes=["Curved arrows at 43 depict the proposed [2,3]-rearrangement."])

# Page 4: Schemes 10-14.
add(4, "p04_s10_conversion_46_to_47", "literature_example", "Scheme 10, precursor conversion",
    [("reactant", "46", "propargylic alcohol"), ("product", "47", "propargyloxymethyl ketone derivative")],
    {"transformation": "conversion to propargyloxymethyl ketone"},
    unresolved=["No reagent or yield is printed for 46-to-47."])
add(4, "p04_s10_silylation_47_to_48", "literature_example", "Scheme 10, silyl enol ether formation",
    [("reactant", "47", "propargyloxymethyl ketone derivative"), ("reagent", "TMSCl", "trimethylsilyl chloride"),
     ("reagent", "Et3N", "triethylamine"), ("solvent", "DMF", "dimethylformamide"),
     ("product", "48", "trimethylsilyl enol ether intermediate")],
    {"reagents": "TMSCl, Et3N", "solvent": "DMF"})
add(4, "p04_s10_claisen_48_to_49", "literature_example", "Scheme 10, Claisen rearrangement",
    [("reactant", "48", "trimethylsilyl enol ether intermediate"),
     ("product", "49", "alpha-allenyl-alpha-trimethylsiloxy aldehyde family")],
    {"transformation": "Claisen rearrangement"}, {"reported_yield": "83%-92%"})
add(4, "p04_s10_desilylation_49_to_50", "literature_example", "Scheme 10, desilylation",
    [("reactant", "49", "alpha-allenyl-alpha-trimethylsiloxy aldehyde family"),
     ("catalyst", "PTSA", "p-toluenesulfonic acid"), ("solvent", "MeOH-H2O", "methanol-water"),
     ("product", "50", "desilylated allenyl diol/aldehyde intermediate")],
    {"catalyst": "PTSA", "medium": "MeOH-H2O"})
add(4, "p04_s10_oxidation_50_to_51", "literature_example", "Scheme 10, final oxidation",
    [("reactant", "50", "desilylated allenyl intermediate"), ("product", "51", "allenyl ketone family")],
    {"transformation": "oxidation"}, {"reported_yield": "72%-90%"},
    unresolved=["The oxidant identity is not printed in Scheme 10."])
add(4, "p04_s11_overall_acetal_rearrangement", "literature_example", "Scheme 11, overall route",
    [("reactant", "52", "propargylic alcohol"), ("reactant", "53", "enol methyl ether"),
     ("product", "56", "allenyl ketone")],
    {"initial_conditions": "H+, 80 °C", "sequence": "acetal formation, methanol loss, [3,3]-rearrangement"},
    unresolved=["No yield or separate operating time is printed."])
add(4, "p04_s11_rearrangement_path", "mechanism", "Scheme 11, 54-55 pathway",
    [("reactant", "54", "acetal intermediate"), ("unspecified_agent", "55", "methanol-loss intermediate"),
     ("product", "56", "allenyl ketone")],
    {"proposed_path": "54 loses methanol to 55; 55 undergoes [3,3]-rearrangement to 56"},
    notes=["The review gives a condensed pathway rather than a separately documented run for each intermediate."])
add(4, "p04_s12_ylide_ketene", "literature_example", "Scheme 12, upper arrow",
    [("reactant", "57", "acyl-substituted Wittig reagent family"), ("reactant", "58", "ketene family"),
     ("product", "59", "allenyl ketone family")], {"reaction_type": "Wittig reagent-ketene reaction"})
add(4, "p04_s12_acylchloride_ylide", "literature_example", "Scheme 12, lower arrow",
    [("reactant", "60", "acyl chloride"), ("reactant", "61", "Wittig reagent"),
     ("product", "62", "allenyl ketone")], {"reaction_type": "acyl chloride-Wittig reagent reaction"})
add(4, "p04_s13_bromination_63_to_64", "literature_example", "Scheme 13, bromination",
    [("reactant", "63", "3-substituted acetylacetone family; R = H or alkyl"),
     ("reagent", "Ph3PBr2", "dibromotriphenylphosphorane"), ("product", "64", "4-bromo-3-pentenone family")],
    {"reagent": "Ph3PBr2"})
add(4, "p04_s13_elimination_64_to_65", "literature_example", "Scheme 13, HBr elimination",
    [("reactant", "64", "4-bromo-3-pentenone family"), ("reagent", "Et3N", "triethylamine"),
     ("product", "65", "allenyl ketone family")], {"base": "Et3N", "transformation": "HBr elimination"})
add(4, "p04_s13_hbr_addition_66_to_67", "literature_example", "Scheme 13, HBr addition",
    [("reactant", "66", "allenic acid"), ("reagent", "HBr", "hydrogen bromide"),
     ("product", "67", "3-bromo-3-butenoic acid")], {"reagent": "HBr"}, {"reported_yield": "88%"})
add(4, "p04_s13_diazoketone_67_to_68", "literature_example", "Scheme 13, diazoketone formation",
    [("reactant", "67", "3-bromo-3-butenoic acid"), ("reagent", "COCl2", "COCl2 chlorinating reagent, as printed"),
     ("reagent", "CH2N2", "diazomethane"), ("product", "68", "bromo diazoketone")],
    {"sequence": "1. COCl2 (as printed); 2. CH2N2"},
    unresolved=["The compact COCl2 reagent label is retained literally rather than assigned a more specific identity."])
add(4, "p04_s13_dbn_elimination_68_to_69", "literature_example", "Scheme 13, DBN elimination",
    [("reactant", "68", "bromo diazoketone"), ("reagent", "DBN", "1,5-diazabicyclonon-5-ene"),
     ("product", "69", "allenyl diazoketone")], {"base": "DBN"})
add(4, "p04_s14_hydrolysis_70_to_71", "literature_example", "Scheme 14, overall hydrolysis",
    [("reactant", "70", "4-ethoxy-3-en-1-yne family"), ("reagent", "HClO4", "perchloric acid"),
     ("product", "71", "allenyl ketone family")],
    {"HClO4_concentration": "0.05-0.1 M", "reaction_type": "acid hydrolysis"})
add(4, "p04_s14_hydrolysis_mechanism", "mechanism", "Scheme 14, proposed mechanism",
    [("reactant", "70", "4-ethoxy-3-en-1-yne family"),
     ("unspecified_agent", "protonated intermediate", "protonated ethoxy enyne/allene pathway"),
     ("product", "71", "allenyl ketone family")],
    {"catalyst": "H+", "proposed_path": "protonation and hydrolysis through the depicted oxonium intermediate"})

# Page 5: Schemes 15-22.
add(5, "p05_s15_socl2_72_to_73", "literature_example", "Scheme 15",
    [("reactant", "72", "diaryl propargylic hydroxy ketone family"), ("reagent", "SOCl2", "thionyl chloride"),
     ("product", "73", "alpha-chloro allenyl ketone family")], {"reagent": "SOCl2"})
add(5, "p05_s16_silyl_migration_74_to_75", "literature_example", "Scheme 16",
    [("reactant", "74", "1-trimethylsilyl-2-alkyne-1,4-diol derivative family; G = TMS or Ms"),
     ("reagent", "TMSOTf or Me2AlCl", "migration/elimination promoter"),
     ("product", "75", "alpha-TMS-substituted allenyl ketone family")],
    {"promoter": "TMSOTf or Me2AlCl", "transformation": "1,2-trimethylsilyl migration-elimination"},
    notes=["The prose says the method requires 3-5 separation steps from starting material."],
    unresolved=["No yield is printed for Scheme 16."])
add(5, "p05_s17_onepot_76_to_79", "literature_example", "Scheme 17, one-pot route",
    [("reactant", "76", "propargyl chloride family"), ("reagent", "MeLi", "methyllithium"),
     ("reactant", "MeCOTMS", "trimethylsilyl methyl ketone"), ("reagent", "ZnCl2", "zinc chloride"),
     ("product", "79", "alpha-TMS-substituted allenyl ketone family")],
    {"sequence": "1. MeLi; 2. MeCOTMS; then ZnCl2; 1,2-silyl migration-elimination"},
    {"reported_yield": "40%-68%"},
    notes=["The prose explicitly describes this as a one-pot method."],
    unresolved=["No stage-specific times, temperatures, or intermediate yields are printed."])
add(5, "p05_s17_intermediate_path", "mechanism", "Scheme 17, salts 77-78",
    [("reactant", "76", "propargyl chloride family"), ("unspecified_agent", "77", "lithium salt"),
     ("unspecified_agent", "78", "zinc reagent"), ("product", "79", "allenyl ketone family")],
    {"proposed_or_condensed_path": "76 -> lithium salt 77 -> zinc reagent 78 -> 79 by 1,2-TMS migration-elimination"})
add(5, "p05_s18_acylation_80_to_81", "literature_example", "Scheme 18",
    [("reactant", "80", "3-trimethylsilyl alkyne family; R = H or TMS"),
     ("reactant", "R'COCl", "acyl chloride family; R' = Me or t-Bu"),
     ("catalyst", "AlCl3", "aluminum chloride"), ("product", "81", "allenyl ketone family")],
    {"reagents": "R'COCl/AlCl3"}, {"reported_yield": "45%-60%"})
add(5, "p05_s19_photolysis_82_to_83", "literature_example", "Scheme 19",
    [("reactant", "82", "2-TMS-substituted furan family; R = TMS or Me"),
     ("product", "83", "TMS-substituted allenyl ketone family")],
    {"condition": "hν"}, {"reported_yield": "50%-87%"})
add(5, "p05_s20_row_ph_ph", "literature_example", "Scheme 20, R1 = R2 = Ph",
    [("reactant", "84", "2,5-diphenyl-3-bromofuran"), ("reagent", "BuLi", "butyllithium"),
     ("product", "85", "allenyl ketone product"), ("product", "86", "furan coproduct")],
    {"reagent": "BuLi", "R1": "Ph", "R2": "Ph"},
    {"yield_85": "60%", "yield_86": "30%"})
add(5, "p05_s20_row_pclph_ph", "literature_example", "Scheme 20, R1 = 4-ClC6H4, R2 = Ph",
    [("reactant", "84", "2-phenyl-5-(4-chlorophenyl)-3-bromofuran family"),
     ("reagent", "BuLi", "butyllithium"), ("product", "85", "allenyl ketone product"),
     ("product", "86", "furan coproduct")],
    {"reagent": "BuLi", "R1": "4-ClC6H4", "R2": "Ph"},
    {"yield_85": "40%", "yield_86": "40%"})
add(5, "p05_s21_decarbonylation_87_to_88", "literature_example", "Scheme 21",
    [("reactant", "87", "3-arylmethylenefuran-2(3H)-one family"),
     ("product", "88", "allenyl ketone family")],
    {"condition": "heat", "transformation": "CO loss and ring opening"},
    {"reported_yield": "45%-85%"})
add(5, "p05_s22_overall_palladium_carbonylation", "literature_example", "Scheme 22, overall reaction",
    [("reactant", "89", "propargyl methyl carbonate family"), ("reactant", "active methylene compound", "active methylene nucleophile precursor"),
     ("catalyst", "Pd(0)/PPh3", "palladium(0)/triphenylphosphine"), ("reagent", "CO", "carbon monoxide"),
     ("reagent", "NaH", "sodium hydride"), ("product", "92", "allenyl ketone family")],
    {"sequence": "Pd(0)/PPh3, -CO2; CO insertion; NaH-generated nucleophile"},
    {"reported_yield": "43%-64%"},
    unresolved=["The range is not mapped to individual R/R'/R'' combinations."])
add(5, "p05_s22_palladium_mechanism", "mechanism", "Scheme 22, intermediates 90-91",
    [("reactant", "89", "propargyl methyl carbonate family"),
     ("unspecified_agent", "90", "allenylpalladium intermediate"),
     ("unspecified_agent", "91", "carbonyl-insertion intermediate"),
     ("product", "92", "allenyl ketone family")],
    {"proposed_path": "decarboxylation to 90; CO insertion to 91; nucleophilic substitution to 92"},
    notes=["Intermediates 90 and 91 are pathway species and are not treated as separate observed experiments."])

# Page 6: Schemes 23-27 and the beginning of the Scheme 28 discussion.
add(6, "p06_s23_generic_14_addition", "general_scheme", "Scheme 23",
    [("reactant", "93", "1,2-allenyl ketone family"), ("reactant", "NuH", "generic nucleophile"),
     ("product", "94", "alpha,beta-unsaturated ketone family"),
     ("product", "95", "beta,gamma-unsaturated ketone family")],
    {"reaction_type": "1,4-conjugate nucleophilic addition followed by alpha- or gamma-protonation"},
    notes=["This is a generic product map, not an individual experiment."])
add(6, "p06_s24_overall_umpolung", "literature_example", "Scheme 24, overall sequence",
    [("reactant", "96", "allenyl ketone family"), ("reagent", "Ph3P", "triphenylphosphine"),
     ("reagent", "PTSA", "p-toluenesulfonic acid"), ("reagent", "HOCH2CH2OH", "ethylene glycol"),
     ("reagent", "NaI/H2O", "sodium iodide/water system"),
     ("reactant", "NuH", "ROH, RSH, or RNH2"),
     ("product", "100", "gamma-heteroatom-substituted alpha,beta-unsaturated ketone family")],
    {"sequence": "1. Ph3P, PTSA; 2. HOCH2CH2OH; 3. NaI/H2O; then NuH and deprotection"},
    {"reported_yield": "63%-71%"})
add(6, "p06_s24_umpolung_mechanism", "mechanism", "Scheme 24, intermediates 97-99",
    [("reactant", "96", "allenyl ketone family"), ("unspecified_agent", "97", "cyclic phosphonium acetal"),
     ("unspecified_agent", "98", "nucleophile-addition phosphonium intermediate"),
     ("unspecified_agent", "99", "hydrolyzed phosphonium ketone intermediate"),
     ("product", "100", "gamma-substituted alpha,beta-unsaturated ketone family")],
    {"proposed_path": "96 -> 97 -> 98 -> 99 -> 100 with Ph3P polarity inversion"})
add(6, "p06_s25_alcohol_addition_101_to_102", "literature_example", "Scheme 25, alcohol addition",
    [("reactant", "101", "allenyl ketone family"), ("reactant", "ROH", "alcohol"),
     ("reagent", "base", "base"), ("product", "102", "alkoxy beta,gamma-unsaturated ketone intermediate family")],
    {"conditions": "ROH, base"})
add(6, "p06_s25_isomerization_102_to_103", "literature_example", "Scheme 25, isomerization",
    [("reactant", "102", "alkoxy beta,gamma-unsaturated ketone intermediate family"),
     ("product", "103", "alkoxy alpha,beta-unsaturated ketone family")],
    {"transformation": "double-bond isomerization"}, {"reported_yield": "92%-96%"},
    unresolved=["The placement of 92%-96% may refer to the alcohol-addition/isomerization sequence rather than only this arrow."])
add(6, "p06_s25_hydrolysis_103_to_104", "literature_example", "Scheme 25, acid hydrolysis",
    [("reactant", "103", "alkoxy alpha,beta-unsaturated ketone family"),
     ("reagent", "H2SO4", "sulfuric acid"), ("product", "104", "beta-diketone family")],
    {"reagent": "H2SO4", "transformation": "acid hydrolysis"})
add(6, "p06_s26_overall_hydrazinium_hydrochloride", "literature_example", "Scheme 26, overall reaction",
    [("reactant", "105", "allenyl ketone family"),
     ("reagent", "dimethylhydrazine hydrochloride salt", "dimethylhydrazine hydrochloride salt; exact substitution/salt stoichiometry unresolved"),
     ("product", "109", "(E)-beta-chloro-alpha,beta-unsaturated ketone family")],
    {"selectivity_conditions": "polar solvent or base favors 109"},
    {"reported_selectivity": "highly selective (E) product under polar-solvent or base-catalyzed conditions"},
    unresolved=["The exact dimethylhydrazine substitution pattern and hydrochloride stoichiometry are not safely resolved from the compact print/OCR."])
add(6, "p06_s26_isomerization_mechanism", "mechanism", "Scheme 26, intermediates 106-108",
    [("reactant", "105", "allenyl ketone family"), ("unspecified_agent", "106", "initial addition depiction"),
     ("unspecified_agent", "107", "hydrazinium adduct depiction"),
     ("unspecified_agent", "108", "beta-chloro-beta,gamma-unsaturated ketone"),
     ("product", "109", "(E)-beta-chloro-alpha,beta-unsaturated ketone")],
    {"proposed_path": "addition through 106/107, formation of 108, then isomerization to 109"})
add(6, "p06_s27_overall_sncl4_chlorination", "literature_example", "Scheme 27, overall reaction",
    [("reactant", "allenyl ketone", "allenyl ketone family"), ("reagent", "SnCl4", "tin tetrachloride"),
     ("product", "113", "(E)-beta-chloro-alpha,beta-unsaturated ketone family")],
    {"reagent": "SnCl4"}, {"reported_selectivity": "complete formation of the (E) beta-chloro alpha,beta-unsaturated ketone"})
add(6, "p06_s27_sncl4_mechanism", "mechanism", "Scheme 27, intermediates 110-112",
    [("reactant", "110", "SnCl3-bound allenyl ketone/chloride addition depiction"),
     ("unspecified_agent", "111", "cyclized organotin intermediate"),
     ("unspecified_agent", "112", "proton-transfer organotin intermediate"),
     ("product", "113", "(E)-beta-chloro-alpha,beta-unsaturated ketone")],
    {"proposed_path": "110 -> 111 <-> 112 -> 113"},
    notes=["Curved arrows and the 111/112 equilibrium are mechanistic, not separate observed runs."])


# Coverage ledger.  Page 1 has no record because it is bibliographic/abstract material.
regions = {
    1: [
        {"region": "title, Chinese abstract, and English abstract", "finding": "Review metadata and high-level synthesis/reaction taxonomy; no individual experiment, scheme row, table, or procedure is reported.", "evidence_ids": [f"{DOC}:page1:text", f"{DOC}:page1:image"]},
        {"region": "English abstract reaction summary", "finding": "Generic claims about nucleophilic addition, cycloaddition, and cyclization; retained as context rather than fabricated experiments.", "evidence_ids": [f"{DOC}:page1:text", f"{DOC}:page1:image"]},
    ],
    2: [
        {"region": "left column, Scheme 1 and sections 1.1-1.2", "finding": "Two cited literature transformations: oxidation to propargyl ketone and isomerization to allenyl ketone; multiple alternative oxidants/bases are family-level prose.", "evidence_ids": [f"{DOC}:page2:text", f"{DOC}:page2:image"]},
        {"region": "right column, Schemes 2-3", "finding": "Three organometallic-acylation examples in Scheme 2 and two stages in the allenyllithium/amide route of Scheme 3; all are prior-literature summaries.", "evidence_ids": [f"{DOC}:page2:text", f"{DOC}:page2:image"]},
    ],
    3: [
        {"region": "left column, Schemes 4-6", "finding": "Organomercury, organocopper, and organomanganese routes; concrete condensed arrows are literature examples, while complexes 27-28 are retained as pathway species.", "evidence_ids": [f"{DOC}:page3:text", f"{DOC}:page3:image"]},
        {"region": "right column, Schemes 7-9", "finding": "Three allenol oxidations and two rearrangement-based routes; curved-arrow intermediates are classified as mechanisms rather than observed experiments.", "evidence_ids": [f"{DOC}:page3:text", f"{DOC}:page3:image"]},
    ],
    4: [
        {"region": "left column, Schemes 10-11", "finding": "Multi-stage Claisen/oxidation and acetal/[3,3]-rearrangement routes; independent preparative stages are separated and pathway intermediates are classified as mechanism.", "evidence_ids": [f"{DOC}:page4:text", f"{DOC}:page4:image"]},
        {"region": "right column, Schemes 12-14", "finding": "Two Wittig examples, five elimination-route stages, and acid hydrolysis plus its proposed mechanism; no table or current-paper procedure.", "evidence_ids": [f"{DOC}:page4:text", f"{DOC}:page4:image"]},
    ],
    5: [
        {"region": "left column, Schemes 15-18", "finding": "Four cited synthetic families including the one-pot Scheme 17; one-pot intermediates are retained in a separate mechanism/path record.", "evidence_ids": [f"{DOC}:page5:text", f"{DOC}:page5:image"]},
        {"region": "right column, Schemes 19-22", "finding": "Photolysis, two Scheme-20 substrate rows with coproduct yields, decarbonylation, and palladium carbonylation; Pd intermediates are mechanistic.", "evidence_ids": [f"{DOC}:page5:text", f"{DOC}:page5:image"]},
    ],
    6: [
        {"region": "left column, Schemes 23-24", "finding": "Scheme 23 is a generic product map; Scheme 24 is a cited polarity-inversion sequence plus a proposed intermediate pathway.", "evidence_ids": [f"{DOC}:page6:text", f"{DOC}:page6:image"]},
        {"region": "right column, Schemes 25-27", "finding": "Alcohol addition/isomerization/hydrolysis and two chlorination reactions; Scheme 26-27 pathway species are classified as mechanisms.", "evidence_ids": [f"{DOC}:page6:text", f"{DOC}:page6:image"]},
        {"region": "bottom of right column, beginning of Scheme 28 discussion", "finding": "Text begins a metal-halide/HOAc scope discussion, but its scheme and continuation are on page 7; no page-6-only experiment record was fabricated.", "evidence_ids": [f"{DOC}:page6:text", f"{DOC}:page6:image"]},
    ],
}

unresolved = {
    1: ["Abstract-level claims do not provide row-level substrates, conditions, or yields."],
    2: ["Generic R groups are unresolved; Scheme 2 product-specific yield allocation is not printed."],
    3: ["The observational status of several organometallic/rearrangement intermediates is not established in this review."],
    4: ["Many stage-specific reagents, times, and yield bases are absent; Scheme 14 separates the overall reaction from a proposed mechanism."],
    5: ["Yield ranges are family-level; Scheme 17 stage details and Scheme 22 intermediate observation are not established."],
    6: ["Scheme 28 continues beyond the required page range and is intentionally unresolved here; no SI is supplied."],
}

coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": page,
            "state": "attempted",
            "regions": regions[page],
            "record_ids": by_page[page],
            "unresolved": unresolved[page],
        }
        for page in range(1, 7)
    ],
}


def write(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n")


write(OUT / "raw_model/records_pages_0001_0006.json", records)
write(OUT / "coverage/pages_0001_0006.json", coverage)

# Mark only the six required page tasks attempted; later pages remain pending.
task_path = OUT / "tasks.json"
tasks = json.loads(task_path.read_text())
for task in tasks:
    if task.get("document_id") == DOC:
        page = int(task["evidence_id"].split(":page", 1)[1].split(":", 1)[0])
        if 1 <= page <= 6:
            task["state"] = "attempted"
            task["reason"] = "Original page image inspected; extraction decisions are recorded in pages_0001_0006 coverage ledger."
write(task_path, tasks)

print(json.dumps({"records": len(records), "pages": list(range(1, 7)), "by_page": {str(k): len(v) for k, v in by_page.items()}}, ensure_ascii=False))
