#!/usr/bin/env python3
"""Build evidence-linked review records for source.pdf pages 7-11.

The source is a review article.  Concrete transformations are classified as
literature examples, generic product maps as general schemes, and proposed
intermediates as mechanisms.  No structure is certified and no SI is assumed.
"""
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "runs/current"
DOC = "doc_6485e9f6c591416c"


def evidence(pages):
    if isinstance(pages, int):
        pages = [pages]
    return [item for page in pages for item in (
        f"{DOC}:page{page}:text", f"{DOC}:page{page}:image"
    )]


def fact(value, pages=None):
    if value is None:
        return {"value": None, "evidence_ids": [], "verification": "missing"}
    return {"value": value, "evidence_ids": evidence(pages), "verification": "unreviewed"}


def field(name, value, pages):
    return {"name": name, "fact": fact(value, pages)}


def participant(entity_id, role, label, name, pages):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, pages),
        "name": fact(name, pages),
        "smiles": fact(None),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": [],
    }


records = []
by_page = {i: [] for i in range(7, 12)}


def add(page, suffix, kind, source_id, parts, conditions=None, outcomes=None,
        notes=None, unresolved=None, evidence_pages=None):
    pages = evidence_pages or page
    rid = f"{DOC}:{suffix}"
    ps = [participant(f"{suffix}_{i+1}", *p, pages) for i, p in enumerate(parts)]
    cond = [field(k, v, pages) for k, v in (conditions or {}).items()]
    cond += [
        field("reaction_scale", None, pages),
        field("atmosphere", None, pages),
        field("concentration", None, pages),
        field("reaction_time", None, pages),
        field("workup", None, pages),
        field("purification", None, pages),
    ]
    outs = [field(k, v, pages) for k, v in (outcomes or {}).items()]
    if not any(x["name"] == "yield_measurement_basis" for x in outs):
        outs.append(field("yield_measurement_basis", None, pages))
    base_unresolved = [
        "The article is a review; this is a prior-literature summary rather than a current-paper experimental run.",
        "Exact drawing-derived structures and generic R-group identities are unverified; SMILES are intentionally null.",
        "The review omits reaction scale, atmosphere, concentration, workup, purification, and usually time and yield basis.",
        "No supporting-information file is supplied or associated in this pilot.",
    ]
    if kind == "mechanism":
        base_unresolved.append("Depicted pathway species are not established here as isolated or directly observed intermediates.")
    rec = {
        "record_id": rid,
        "document_id": DOC,
        "source_reaction_id": source_id,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": evidence(pages),
        "participants": ps,
        "steps": [{
            "step_id": "step1",
            "participant_ids": [p["entity_id"] for p in ps],
            "conditions": cond,
        }],
        "outcomes": outs,
        "notes": [fact(x, pages) for x in (notes or [])],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": base_unresolved + (unresolved or []),
        },
    }
    records.append(rec)
    by_page[page].append(rid)


# Page 7: completion of Scheme 28, Schemes 29-33, and the thiol prose contrast.
add(7, "p07_s28_generic_hx_addition", "general_scheme", "Scheme 28, upper generic arrow",
    [("reactant", "114", "1,2-allenyl ketone family"),
     ("reactant", "XH", "generic hydrogen halide"),
     ("product", "115", "beta-halo-beta,gamma-unsaturated ketone family"),
     ("product", "116", "beta-halo-alpha,beta-unsaturated ketone family")],
    {"reaction_type": "1,4-addition followed by alternative protonation/isomerization"},
    notes=["The upper drawing is a generic product map rather than an individual reported run."],
    evidence_pages=[6, 7])
add(7, "p07_s28_5substituted_mx_hoac", "literature_example", "Scheme 28, 5-substituted family",
    [("reactant", "5-substituted allenyl ketone", "5-monosubstituted or 5-disubstituted 1,2-allenyl ketone family"),
     ("reagent", "MX", "metal halide family"),
     ("solvent", "HOAc", "acetic acid"),
     ("product", "115", "beta-halo-beta,gamma-unsaturated ketone family")],
    {"medium": "HOAc", "halide_source": "metal halide MX"},
    {"reported_selectivity": "selective formation of 115; 5-monosubstituted substrates give (Z)-115 stereoselectively"},
    evidence_pages=[6, 7])
add(7, "p07_s28_3alkyl_hoac_mixture", "literature_example", "Scheme 28, 3-alkyl/HOAc condition",
    [("reactant", "3-alkyl-substituted allenyl ketone", "3-alkyl-substituted 1,2-allenyl ketone family"),
     ("reagent", "MX", "metal halide family"), ("solvent", "HOAc", "acetic acid"),
     ("product", "115", "beta-halo-beta,gamma-unsaturated ketone family"),
     ("product", "116", "beta-halo-alpha,beta-unsaturated ketone family")],
    {"medium": "HOAc", "halide_source": "metal halide MX"},
    {"reported_outcome": "mixture of 115 and 116"})
add(7, "p07_s28_3alkyl_mixed_acid", "literature_example", "Scheme 28, 3-alkyl/HOAc-CF3CO2H condition",
    [("reactant", "3-alkyl-substituted allenyl ketone", "3-alkyl-substituted 1,2-allenyl ketone family"),
     ("reagent", "MX", "metal halide family"),
     ("solvent", "HOAc-CF3CO2H", "acetic acid-trifluoroacetic acid medium"),
     ("product", "115", "beta-halo-beta,gamma-unsaturated ketone family")],
    {"medium": "HOAc-CF3CO2H", "halide_source": "metal halide MX"},
    {"reported_selectivity": "highly selective", "reported_yield": "high yield (no number printed)"})
add(7, "p07_s29_amine_addition", "literature_example", "Scheme 29",
    [("reactant", "117", "allenyl ketone family"),
     ("reactant", "R3R4NH", "amine family"),
     ("product", "118", "amino-substituted alpha,beta-unsaturated ketone family")],
    {"reaction_type": "amine 1,4-addition"},
    {"reported_yield": "20%-100%", "reported_selectivity": "complete formation of alpha,beta-unsaturated ketone products"})
add(7, "p07_s30_hydrazine_cyclization", "literature_example", "Scheme 30, hydrazine branch",
    [("reactant", "119", "allenyl ketone family"),
     ("reactant", "R'NHNH2", "hydrazine derivative family; R' = H, alkyl, or aryl"),
     ("product", "120", "five-membered nitrogen heterocycle family"),
     ("product", "121", "five-membered nitrogen heterocycle regioisomer family")],
    {"reaction_type": "heterocycle-forming addition/cyclization"})
add(7, "p07_s30_hydroxylamine_cyclization", "literature_example", "Scheme 30, hydroxylamine branch",
    [("reactant", "119", "allenyl ketone family"),
     ("reactant", "NH2OH", "hydroxylamine"),
     ("product", "122", "five-membered oxygen/nitrogen heterocycle family"),
     ("product", "123", "five-membered oxygen heterocycle regioisomer family")],
    {"reaction_type": "heterocycle-forming addition/cyclization"})
add(7, "p07_thiol_no_base_selectivity", "literature_example", "Page 7 thiol prose, no triethylamine",
    [("reactant", "allenyl ketone", "allenyl ketone family"),
     ("reactant", "RSH", "thiol family"),
     ("product", "alpha,beta-unsaturated product", "sulfur-substituted alpha,beta-unsaturated ketone family")],
    {"base": "none stated"}, {"reported_selectivity": "mainly alpha,beta-unsaturated product"},
    unresolved=["No structure number or numerical yield is printed for this prose-only comparison."])
add(7, "p07_thiol_et3n_selectivity", "literature_example", "Page 7 thiol prose, triethylamine present",
    [("reactant", "allenyl ketone", "allenyl ketone family"),
     ("reactant", "RSH", "thiol family"), ("reagent", "Et3N", "triethylamine"),
     ("product", "beta,gamma-unsaturated product", "sulfur-substituted beta,gamma-unsaturated ketone family")],
    {"base": "Et3N"}, {"reported_selectivity": "mainly beta,gamma-unsaturated product"},
    unresolved=["No structure number or numerical yield is printed for this prose-only comparison."])
add(7, "p07_s31_trivalent_phosphorus_cyclization", "literature_example", "Scheme 31",
    [("reactant", "124", "allenyl ketone family"),
     ("reactant", "125", "trivalent organophosphorus reagent family"),
     ("product", "126", "five-membered phosphorus-oxygen heterocycle family")],
    {"reaction_type": "phosphorus-oxygen heterocycle formation"})
add(7, "p07_s32_phosphonate_grignard_addition", "literature_example", "Scheme 32, upper arrow",
    [("reactant", "127", "allenyl ketone family"),
     ("reactant", "128", "(EtO)2P(O)MgBr Grignard reagent"),
     ("product", "129", "phosphonate-substituted alpha,beta-unsaturated ketone family")],
    {"reaction_type": "1,4-nucleophilic addition"})
add(7, "p07_s32_wittig_reagent_addition", "literature_example", "Scheme 32, lower arrow",
    [("reactant", "130", "allenyl ketone family; R = Et or i-Pr"),
     ("reactant", "131", "Ph3P=CHR' Wittig reagent; R' = CN, PhCO, or CH3OCO"),
     ("product", "132", "phosphonium-substituted alpha,beta-unsaturated ketone family")],
    {"reaction_type": "1,4-nucleophilic addition"})
add(7, "p07_s33_overall_cuprate_addition", "literature_example", "Scheme 33, overall outcomes",
    [("reactant", "133", "allenyl ketone family"),
     ("reagent", "R2CuLi", "lithium diorganocuprate family"),
     ("reagent", "NH4Cl/H2O", "aqueous ammonium chloride workup"),
     ("product", "136", "beta,gamma-unsaturated ketone family"),
     ("product", "137", "alpha,beta-unsaturated ketone family")],
    {"sequence": "R2CuLi 1,4-addition, then NH4Cl/H2O hydrolysis"},
    {"reported_outcome": "alternative formation of 136 or 137 through the depicted organocopper species"})
add(7, "p07_s33_cuprate_equilibrium", "mechanism", "Scheme 33, intermediates 134-135",
    [("reactant", "133", "allenyl ketone family"),
     ("reagent", "R2CuLi", "lithium diorganocuprate family"),
     ("unspecified_agent", "134", "organocopper intermediate"),
     ("unspecified_agent", "135", "isomeric organocopper intermediate"),
     ("product", "136", "beta,gamma-unsaturated ketone family"),
     ("product", "137", "alpha,beta-unsaturated ketone family")],
    {"proposed_path": "133 -> 134; slow 134/135 equilibrium; hydrolysis of 134 -> 136 and of 135 -> 137"})


# Page 8: Schemes 34-40.
add(8, "p08_s34_organomagnesium_12_addition", "literature_example", "Scheme 34",
    [("reactant", "138", "allenyl ketone family"),
     ("reactant", "139", "organomagnesium reagent R'Mg"),
     ("product", "140", "allenyl alcohol family")],
    {"reaction_type": "1,2-addition to the carbonyl"},
    notes=["The scheme prints two unsaturated R' substituent examples; their exact condensed formulas remain drawing-dependent."],
    unresolved=["The exact identities of both printed R' examples are not safely normalized from the compact drawing/OCR."])
add(8, "p08_s35_lialh4_reduction", "literature_example", "Scheme 35, LiAlH4 arrow",
    [("reactant", "141", "allenyl ketone family"),
     ("reagent", "LiAlH4", "lithium aluminum hydride"),
     ("product", "142", "allenyl alcohol family")],
    {"reducing_agent": "LiAlH4"}, {"reported_yield": "80%-93%"})
add(8, "p08_s35_dibal_reduction", "literature_example", "Scheme 35 prose, DIBAL alternative",
    [("reactant", "allenyl ketone", "allenyl ketone family"),
     ("reagent", "DIBAL", "diisobutylaluminum hydride"),
     ("product", "allenyl alcohol", "allenyl alcohol family")],
    {"reducing_agent": "DIBAL"},
    unresolved=["The 80%-93% range is printed on the LiAlH4 arrow and is not assigned to DIBAL here."])
add(8, "p08_s36_butadiene_diels_alder", "literature_example", "Scheme 36, 1,3-butadiene branch",
    [("reactant", "143", "allenyl ketone family"),
     ("reactant", "1,3-butadiene family", "1,3-butadiene family"),
     ("product", "144", "six-membered Diels-Alder adduct family")],
    {"reaction_type": "Diels-Alder cycloaddition"})
add(8, "p08_s36_cyclic_diene_diels_alder", "literature_example", "Scheme 36, cyclic-diene branch",
    [("reactant", "143", "allenyl ketone family"),
     ("reactant", "1,3-cyclopentadiene/cyclohexadiene", "cyclic 1,3-diene family"),
     ("product", "145", "bridged six-membered Diels-Alder adduct family")],
    {"reaction_type": "Diels-Alder cycloaddition"},
    unresolved=["The review groups cyclopentadiene and cyclohexadiene literature; exact substrate-to-product mapping is not tabulated."])
add(8, "p08_s36_five_membered_diene_diels_alder", "literature_example", "Scheme 36, X = CH2 or O branch",
    [("reactant", "143", "allenyl ketone family"),
     ("reactant", "five-membered diene; X = CH2 or O", "cyclopentadiene or furan family"),
     ("product", "146", "bridged Diels-Alder adduct family")],
    {"reaction_type": "Diels-Alder cycloaddition"})
add(8, "p08_s37_overall_cascade", "literature_example", "Scheme 37, overall reaction",
    [("reactant", "147", "1,4-diacetoxy-1,3-butadiene"),
     ("reactant", "148", "3,4-pentadien-2-one"),
     ("product", "151", "2-acetoxymethyl acetophenone")],
    {"sequence": "Diels-Alder reaction, [3,3]-rearrangement, then acetic-acid loss"})
add(8, "p08_s37_cascade_path", "mechanism", "Scheme 37, intermediates 149-150",
    [("reactant", "147", "1,4-diacetoxy-1,3-butadiene"),
     ("reactant", "148", "3,4-pentadien-2-one"),
     ("unspecified_agent", "149", "initial cycloadduct/rearrangement depiction"),
     ("unspecified_agent", "150", "rearranged intermediate"),
     ("product", "151", "2-acetoxymethyl acetophenone")],
    {"proposed_path": "147 + 148 -> 149 -> 150 -> 151"})
add(8, "p08_s38_diazomethane_cycloaddition", "literature_example", "Scheme 38, overall reaction",
    [("reactant", "153", "allenyl ketone family"),
     ("reactant", "152", "diazomethane, CH2N2"),
     ("product", "155", "five-membered nitrogen heterocycle family")],
    {"reaction_type": "1,3-dipolar cycloaddition followed by rearrangement"})
add(8, "p08_s38_cycloaddition_path", "mechanism", "Scheme 38, intermediate 154",
    [("reactant", "153", "allenyl ketone family"),
     ("reactant", "152", "diazomethane, CH2N2"),
     ("unspecified_agent", "154", "initial 1,3-dipolar cycloadduct"),
     ("product", "155", "five-membered nitrogen heterocycle family")],
    {"proposed_path": "153 + 152 -> 154 -> 155"})
add(8, "p08_s39_thermal_furan_rearrangement", "literature_example", "Scheme 39",
    [("reactant", "156", "allenyl ketone family"),
     ("product", "157", "substituted furan family")],
    {"condition": "heat", "reaction_type": "thermal rearrangement to furan"})
add(8, "p08_s40_ag_rh_generic_rearrangement", "literature_example", "Scheme 40, Ag(I)/Rh(I) family",
    [("reactant", "158", "allenyl ketone family"),
     ("catalyst", "Ag(I) or Rh(I)", "silver(I) or rhodium(I) catalyst family"),
     ("product", "159", "2-functionalized furan family")],
    {"catalyst_family": "Ag(I) or Rh(I)", "reaction_type": "catalytic rearrangement to furan"})
add(8, "p08_s40_agno3_acetone_water_caco3", "literature_example", "Scheme 40 prose, acetone-water-CaCO3",
    [("reactant", "158", "allenyl ketone family"),
     ("catalyst", "AgNO3", "silver nitrate"),
     ("solvent", "acetone-water", "acetone-water medium"),
     ("reagent", "CaCO3", "calcium carbonate"),
     ("product", "159", "2-functionalized furan family")],
    {"catalyst": "AgNO3", "medium": "acetone-water-CaCO3"},
    {"reported_outcome": "improved formation of furan 159"})
add(8, "p08_s40_agno3_acetone", "literature_example", "Scheme 40 prose, acetone",
    [("reactant", "158", "allenyl ketone family"),
     ("catalyst", "AgNO3", "silver nitrate"),
     ("solvent", "acetone", "acetone"),
     ("product", "159", "2-functionalized furan family")],
    {"catalyst": "AgNO3", "solvent": "acetone"},
    {"reported_outcome": "good formation of furan 159"})
add(8, "p08_s40_agno3_silica", "literature_example", "Scheme 40 prose, AgNO3-silica",
    [("reactant", "158", "allenyl ketone family"),
     ("catalyst", "10% AgNO3/silica", "silver nitrate on silica system"),
     ("product", "159", "2-functionalized furan family")],
    {"catalyst_system": "0.2 mol of 10% AgNO3-silica system, as printed"},
    {"reported_conversion": "nearly complete conversion to 159"},
    unresolved=["The compact phrase '0.2 mol of 10% AgNO3-silica' is preserved literally; its loading basis is not normalized."])


# Page 9: Schemes 41-44 and the proposed Pd mechanism.
add(9, "p09_s41_generic_metal_furanization", "literature_example", "Scheme 41 prose, catalyst family",
    [("reactant", "allenyl ketone", "allenyl ketone family"),
     ("catalyst", "Cu(I)/Rh(II)/Ru(II)/Pd(II)", "Cu(I), Rh(II), Ru(II), or Pd(II) catalyst family"),
     ("product", "furan", "substituted furan family")],
    {"catalyst_family": "Cu(I), Rh(II), Ru(II), or Pd(II)"},
    {"reported_outcome": "catalytic rearrangement to furan products"})
add(9, "p09_s41_pdoac2_product_ratio", "literature_example", "Scheme 41 prose, Pd(OAc)2",
    [("reactant", "160", "terminally unsubstituted allenyl ketone family"),
     ("catalyst", "Pd(OAc)2", "palladium(II) acetate"),
     ("product", "161", "coupled furan product family"),
     ("product", "162", "furan rearrangement product family")],
    {"catalyst": "Pd(OAc)2"}, {"product_ratio_162_to_161": "1:2.4"})
add(9, "p09_s41_tcpc_tfe_acetone", "literature_example", "Scheme 41, TCPC-TFE/acetone condition",
    [("reactant", "160", "terminally unsubstituted allenyl ketone family"),
     ("catalyst", "TCPC^TFE", "TCPC-TFE catalyst system, as printed"),
     ("solvent", "CH3COCH3", "acetone"),
     ("product", "161", "coupled furan product family"),
     ("product", "162", "furan rearrangement product family")],
    {"catalyst_system": "TCPC^TFE", "solvent": "acetone"},
    {"product_ratio_162_to_161": "1:9", "major_product": "161"},
    unresolved=["The exact expanded identity of TCPC^TFE is not provided in this review page."])
add(9, "p09_s41_pdcl2_mecn", "literature_example", "Scheme 41, PdCl2(MeCN)2/MeCN condition",
    [("reactant", "160", "terminally unsubstituted allenyl ketone family"),
     ("catalyst", "PdCl2(MeCN)2", "bis(acetonitrile)palladium(II) dichloride"),
     ("solvent", "MeCN", "acetonitrile"),
     ("product", "161", "coupled furan product family"),
     ("product", "162", "furan rearrangement product family")],
    {"catalyst": "PdCl2(MeCN)2", "solvent": "MeCN"},
    {"product_ratio_162_to_161": "<1:20", "major_product": "161 (almost exclusive)"})
add(9, "p09_s41_chiral_catalyst_163", "literature_example", "Scheme 41, (-)-163 condition",
    [("reactant", "160", "terminally unsubstituted allenyl ketone family"),
     ("catalyst", "(-)-163", "chiral palladium catalyst 163; E = CO2Me"),
     ("product", "162", "furan rearrangement product family")],
    {"catalyst": "(-)-163"}, {"major_product": "162"},
    unresolved=["No numerical yield or 162/161 ratio is printed for catalyst (-)-163."])
add(9, "p09_s42_palladium_mechanism", "mechanism", "Scheme 42",
    [("reactant", "160", "terminally unsubstituted allenyl ketone family"),
     ("catalyst", "Pd(II)L2", "palladium(II) catalyst"),
     ("unspecified_agent", "164", "terminal-double-bond palladium complex"),
     ("unspecified_agent", "165A", "five-membered palladium intermediate A"),
     ("unspecified_agent", "165B", "five-membered palladium intermediate B"),
     ("unspecified_agent", "166", "furanyl palladium intermediate"),
     ("unspecified_agent", "167", "insertion intermediate"),
     ("product", "161", "coupled furan product family"),
     ("product", "162", "furan rearrangement product family")],
    {"proposed_path": "160 coordinates Pd(II) -> 164 -> 165A/165B; beta-H elimination or 1,2-H shift gives 162, while insertion through 166/167 gives 161"})
add(9, "p09_s43_ortho_endo_cyclization", "literature_example", "Scheme 43",
    [("reactant", "168", "aryl-substituted allenyl ketone family; n = 0-3"),
     ("catalyst", "BF3.OEt2 or TiCl4", "Lewis acid catalyst"),
     ("solvent", "CH2Cl2", "dichloromethane"),
     ("product", "169", "five- to eight-membered fused-ring product family")],
    {"catalyst": "BF3.OEt2 or TiCl4", "solvent": "CH2Cl2", "mode": "ortho endo-mode"},
    {"ring_size": "five- to eight-membered products"})
add(9, "p09_s44_bf3_substituted_high_yield", "literature_example", "Scheme 44, methoxy-substituted BF3.OEt2 cases",
    [("reactant", "170", "aryl-substituted allenyl ketone; R1=R2=OMe or R1=OMe/R2=H"),
     ("catalyst", "BF3.OEt2", "boron trifluoride etherate"),
     ("solvent", "CH2Cl2", "dichloromethane"),
     ("product", "171", "spiro/fused cyclization product family")],
    {"catalyst": "BF3.OEt2", "solvent": "CH2Cl2", "mode": "geminal spiro-endo-mode"},
    {"reported_yield": ">80%", "major_product": "171"})
add(9, "p09_s44_bf3_unsubstituted_low_yield", "literature_example", "Scheme 44, R1 = R2 = H with BF3.OEt2",
    [("reactant", "170", "aryl-substituted allenyl ketone; R1 = R2 = H"),
     ("catalyst", "BF3.OEt2", "boron trifluoride etherate"),
     ("solvent", "CH2Cl2", "dichloromethane"),
     ("product", "171", "spiro/fused cyclization product")],
    {"catalyst": "BF3.OEt2", "solvent": "CH2Cl2"}, {"reported_yield": "8%"})
add(9, "p09_s44_hgclo4_unsubstituted", "literature_example", "Scheme 44 prose, R1 = R2 = H with Hg(ClO4)2",
    [("reactant", "170", "aryl-substituted allenyl ketone; R1 = R2 = H"),
     ("catalyst", "Hg(ClO4)2", "mercury(II) perchlorate"),
     ("solvent", "MeCN-water", "acetonitrile-water medium"),
     ("product", "171", "spiro/fused cyclization product")],
    {"catalyst_loading": "1% Hg(ClO4)2", "medium": "MeCN-water"}, {"reported_yield": "80%"},
    unresolved=["The printed 1% loading is preserved without inferring mol%, wt%, or another basis."])


regions = {
    7: [
        {"region": "left column top, continuation and Scheme 28", "finding": "Cross-page metal-halide/acid additions are separated into the generic product map and three condition/substitution families; page 6 is used only as necessary context, not newly claimed as covered.", "evidence_ids": [f"{DOC}:page7:text", f"{DOC}:page7:image"]},
        {"region": "left column middle and bottom, Schemes 29-30", "finding": "Amine addition and the hydrazine versus hydroxylamine cyclization branches are retained as cited literature examples; the two Scheme-30 arrows are not merged.", "evidence_ids": [f"{DOC}:page7:text", f"{DOC}:page7:image"]},
        {"region": "column transition, thiol selectivity prose", "finding": "The no-base and Et3N-present thiol outcomes are distinct condition comparisons with different major unsaturation patterns.", "evidence_ids": [f"{DOC}:page7:text", f"{DOC}:page7:image"]},
        {"region": "right column, Schemes 31-33", "finding": "One phosphorus heterocyclization, two pentavalent-phosphorus additions, and the cuprate overall reaction plus proposed 134/135 equilibrium are represented separately.", "evidence_ids": [f"{DOC}:page7:text", f"{DOC}:page7:image"]},
    ],
    8: [
        {"region": "left column, Schemes 34-36", "finding": "Carbonyl 1,2-addition, two reduction systems, and three Diels-Alder branches are retained as prior-literature examples; the compact R' examples in Scheme 34 remain unresolved.", "evidence_ids": [f"{DOC}:page8:text", f"{DOC}:page8:image"]},
        {"region": "right column upper and middle, Schemes 37-39", "finding": "The Diels-Alder/rearrangement cascade and diazomethane cycloaddition are each split into an overall literature example and a pathway record; thermal furanization is a separate example.", "evidence_ids": [f"{DOC}:page8:text", f"{DOC}:page8:image"]},
        {"region": "right column lower, Scheme 40 and prose", "finding": "Generic Ag(I)/Rh(I) furanization and three materially distinct AgNO3 media/support variants are separated; qualitative conversion claims are preserved without invented yields.", "evidence_ids": [f"{DOC}:page8:text", f"{DOC}:page8:image"]},
    ],
    9: [
        {"region": "left column upper, Scheme 41 and catalyst/solvent discussion", "finding": "Generic metal-catalyst capability and four specific Pd/catalyst-system outcomes are separated; reported 162/161 ratios and major products are retained.", "evidence_ids": [f"{DOC}:page9:text", f"{DOC}:page9:image"]},
        {"region": "right column upper, Scheme 42", "finding": "Pd complexes 164-167 and alternative paths to 161/162 are classified as a proposed mechanism, not observed experiments.", "evidence_ids": [f"{DOC}:page9:text", f"{DOC}:page9:image"]},
        {"region": "lower columns, Schemes 43-44", "finding": "Lewis-acid intramolecular cyclization is separated from the methoxy-substituted, unsubstituted BF3.OEt2, and Hg(ClO4)2/H2O-MeCN cases; their very different yields are preserved.", "evidence_ids": [f"{DOC}:page9:text", f"{DOC}:page9:image"]},
    ],
    10: [
        {"region": "left column top, review conclusion", "finding": "High-level summary of allenyl-ketone reactivity; no new scheme, row, procedure, condition-specific run, or numerical outcome beyond pages 1-9.", "evidence_ids": [f"{DOC}:page10:text", f"{DOC}:page10:image"]},
        {"region": "remaining page, References 1-49", "finding": "Bibliography only; references support earlier review claims but are not local experiment records.", "evidence_ids": [f"{DOC}:page10:text", f"{DOC}:page10:image"]},
    ],
    11: [
        {"region": "both columns, References 49-100", "finding": "Bibliography and author-index footer only; no reaction arrow, table, experimental procedure, or new current-page chemical outcome.", "evidence_ids": [f"{DOC}:page11:text", f"{DOC}:page11:image"]},
    ],
}

unresolved = {
    7: ["Most Scheme 28-33 entries are generic cited families; substrate-specific operating details and yield bases are absent.", "Scheme 28 begins on page 6; page 6 is cited only as cross-page context and is not part of this session's claimed coverage."],
    8: ["Scheme 34's compact R' formulas and Scheme 36's exact cyclic-diene-to-product mapping are not safely normalized.", "The AgNO3-silica loading phrase is retained literally because its basis is not explicit."],
    9: ["The expanded identity of TCPC^TFE and the basis of the printed 1% Hg(ClO4)2 loading are not stated.", "Scheme 44 depicts product 172, but the prose quantifies only product 171 for the listed cases; no yield for 172 is invented."],
    10: ["Conclusion-level statements are not row-level experiments; bibliography entries were not imported as procedures."],
    11: ["Bibliography alone cannot supply missing conditions, yields, or structures for the cited review examples; no SI is supplied."],
}

coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [{
        "page": page,
        "state": "attempted",
        "regions": regions[page],
        "record_ids": by_page[page],
        "unresolved": unresolved[page],
    } for page in range(7, 12)],
}


def write(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n")


write(OUT / "raw_model/records_pages_0007_0011.json", records)
write(OUT / "coverage/pages_0007_0011.json", coverage)

task_path = OUT / "tasks.json"
tasks = json.loads(task_path.read_text())
for task in tasks:
    if task.get("document_id") == DOC:
        page = int(task["evidence_id"].split(":page", 1)[1].split(":", 1)[0])
        if 7 <= page <= 11:
            task["state"] = "attempted"
            task["reason"] = "Original page image inspected; extraction decisions are recorded in pages_0007_0011 coverage ledger."
write(task_path, tasks)

print(json.dumps({
    "records": len(records),
    "pages": list(range(7, 12)),
    "by_page": {str(k): len(v) for k, v in by_page.items()},
}, ensure_ascii=False))
