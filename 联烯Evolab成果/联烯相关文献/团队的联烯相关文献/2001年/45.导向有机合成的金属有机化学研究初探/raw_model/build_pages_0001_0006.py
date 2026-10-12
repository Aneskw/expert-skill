#!/usr/bin/env python3
"""Build evidence-linked machine records for source PDF pages 1-6."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / "runs/current"
DOC = "doc_5f6aebaf6cda0211"


def ev(page):
    return [f"{DOC}:page{page}:image", f"{DOC}:page{page}:text"]


def fact(value, page):
    return {"value": value, "evidence_ids": ev(page),
            "verification": "missing" if value is None else "unreviewed"}


def qty(number, unit, **extra):
    value = {"number": number, "unit": unit}
    value.update(extra)
    return value


def rng(low, high, unit, raw):
    return {"minimum": low, "maximum": high, "unit": unit, "raw_text": raw}


def participant(page, entity_id, role, name, smiles=None, amounts=()):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(name, page),
        "name": fact(name, page),
        "smiles": fact(smiles, page) if smiles else fact(None, page),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": [field(n, v, page) for n, v in amounts],
    }


def field(name, value, page, targets=()):
    out = {"name": name, "fact": fact(value, page)}
    if targets:
        out["target_entity_ids"] = list(targets)
    return out


def record(suffix, page, kind, reactants=(), products=(), reagents=(), catalysts=(),
           solvents=(), conditions=(), outcomes=(), note=None, unresolved=()):
    parts = []
    for role, rows in (("reactant", reactants), ("product", products),
                       ("reagent", reagents), ("catalyst", catalysts),
                       ("solvent", solvents)):
        for row in rows:
            name, smiles, amounts = (tuple(row) + (None, ()))[:3]
            entity = f"{suffix}_{role}_{len(parts)+1}"
            parts.append(participant(page, entity, role, name, smiles, amounts))
    product_ids = [p["entity_id"] for p in parts if p["role"] == "product"]
    step_fields = [field(n, v, page) for n, v in conditions]
    if not any(x["name"] == "temperature" for x in step_fields):
        step_fields.append(field("temperature", None, page))
    if not any("time" in x["name"] for x in step_fields):
        step_fields.append(field("time", None, page))
    outcome_fields = []
    for name, value, target_index in outcomes:
        targets = () if target_index is None else (product_ids[target_index],)
        outcome_fields.append(field(name, value, page, targets))
    if not any("yield" in x["name"] for x in outcome_fields):
        outcome_fields.append(field("yield", None, page,
                                    product_ids[:1] if product_ids else ()))
    if not any("measurement" in x["name"] or x["name"].endswith("_basis")
               for x in outcome_fields):
        outcome_fields.append(field("yield_measurement_basis", None, page))
    missing = list(unresolved)
    for item in ("reaction scale", "atmosphere", "workup", "purification"):
        if item not in " ".join(missing).casefold():
            missing.append(f"Source does not report {item} for this summarized arrow.")
    return {
        "record_id": f"{DOC}:{suffix}",
        "document_id": DOC,
        "source_reaction_id": suffix,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": ev(page),
        "participants": parts,
        "steps": [{"step_id": f"{suffix}_step1",
                   "participant_ids": [p["entity_id"] for p in parts],
                   "conditions": step_fields}],
        "outcomes": outcome_fields,
        "notes": [fact(note, page)] if note else [],
        "review": {"method": "none", "reviewer": None,
                   "checked_fields": [], "unresolved": missing},
    }


records = []
add = records.append

# Page 2: allenoic-acid cyclization and solid-phase stages.
add(record("eq1_allenoic_acid_cyclization", 2, "general_scheme",
    reactants=[("generic 2,3-allenoic acid", None, ()), ("generic organic halide R2X", None, ())],
    products=[("generic substituted gamma-butenolide", None, ())],
    catalysts=[("Pd(PPh3)4", None, ()), ("Ag2CO3", None, ())],
    reagents=[("K2CO3", "O=C([O-])[O-].[K+].[K+]", ())], solvents=[("MeCN", "CC#N", ())],
    note="Generic equation (1), attributed to cited reference [2].",
    unresolved=["Generic R groups and catalyst loadings are not specified."]))
add(record("scheme1_solid_phase_cyclization", 2, "general_scheme",
    reactants=[("polymer-bound aryl iodide", None, ()), ("generic 2,3-allenoic acid", None, ())],
    products=[("polymer-bound gamma-butenolide", None, ())],
    note="First stage of the conceptual solid-phase library workflow in Scheme 1, attributed to reference [3].",
    unresolved=["Scheme 1 does not print operating conditions or a yield for this stage."]))
add(record("scheme1_resin_cleavage", 2, "general_scheme",
    reactants=[("polymer-bound gamma-butenolide", None, ())],
    products=[("free gamma-butenolide", None, ()), ("polymer support", None, ())],
    note="Second, generic cleavage stage in Scheme 1.",
    unresolved=["Cleavage reagent, conditions, and yield are not printed in Scheme 1."]))
add(record("scheme2_ester_resin_loading", 2, "literature_example",
    reactants=[("iodobenzoic acid shown in Scheme 2", None, ()), ("Merrifield resin", None, ())],
    products=[("ester-linked aryl iodide resin", None, ())],
    reagents=[("Cs2CO3", None, ()), ("KI", "[K+].[I-]", ())], solvents=[("DMF", "CN(C)C=O", ())],
    note="Specific resin-loading arrow in Scheme 2; summarized cited work [3]."))
add(record("scheme2_phenoxy_resin_loading", 2, "literature_example",
    reactants=[("iodophenol shown in Scheme 2", None, ()), ("Merrifield resin", None, ())],
    products=[("phenoxy-linked aryl iodide resin", None, ())],
    reagents=[("NaOMe", "C[O-].[Na+]", ())], solvents=[("DMF", "CN(C)C=O", ())],
    note="Specific resin-loading arrow in Scheme 2; summarized cited work [3]."))
add(record("scheme2_benzyloxy_resin_loading", 2, "literature_example",
    reactants=[("iodobenzyl alcohol shown in Scheme 2", None, ()), ("Merrifield resin", None, ())],
    products=[("benzyloxy-linked aryl iodide resin", None, ())],
    reagents=[("NaH", "[H-].[Na+]", ())], solvents=[("THF", "C1CCOC1", ())],
    note="Specific resin-loading arrow in Scheme 2; summarized cited work [3]."))
add(record("scheme3_solid_phase_cyclization", 2, "literature_example",
    reactants=[("ester-linked aryl iodide resin", None, ()), ("n-heptyl-substituted 2,3-allenoic acid", None, ())],
    products=[("polymer-bound gamma-butenolide shown in Scheme 3", None, ())],
    catalysts=[("Pd(0)", None, ())], reagents=[("unspecified base", None, ())],
    solvents=[("MeCN", "CC#N", ())], conditions=[("temperature", qty(70, "°C"))],
    note="First arrow of Scheme 3; summarized cited work [3].",
    unresolved=["Identity and loading of Pd(0) and the base are not printed."]))
add(record("scheme3_alcl3_cleavage", 2, "literature_example",
    reactants=[("polymer-bound gamma-butenolide shown in Scheme 3", None, ())],
    products=[("carboxyaryl-substituted gamma-butenolide", None, ())],
    reagents=[("AlCl3", "Cl[Al](Cl)Cl", ()), ("MeNO2", "C[N+](=O)[O-]", ())],
    solvents=[("CH2Cl2", "ClCCl", ())],
    note="Second arrow of Scheme 3; ether/ester cleavage summarized from cited work [3].",
    unresolved=["Reagent quantities, temperature, time, and yield are not reported here."]))

# Page 3: continuation of solid-phase chemistry and allenoic-acid methods.
add(record("scheme4_solid_phase_cyclization", 3, "literature_example",
    reactants=[("ether-linked aryl iodide resin", None, ()), ("generic 2,3-allenoic acid", None, ())],
    products=[("polymer-bound gamma-butenolide in Scheme 4", None, ())],
    catalysts=[("Pd(0)", None, ())], reagents=[("i-Pr2NEt", "CC(C)N(C(C)C)C(C)C", ())],
    solvents=[("MeCN", "CC#N", ())], conditions=[("temperature", qty(70, "°C"))],
    note="First arrow of Scheme 4; summarized cited work [3].",
    unresolved=["Pd identity/loading, time, and yield are not printed."]))
add(record("scheme4_znbr2_acbr_cleavage", 3, "literature_example",
    reactants=[("polymer-bound gamma-butenolide in Scheme 4", None, ())],
    products=[("acetoxyalkyl aryl gamma-butenolide (n = 0 or 1)", None, ())],
    reagents=[("ZnBr2", "Br[Zn]Br", (("equivalents", qty(0.5, "equiv")),)),
              ("AcBr", "CC(=O)Br", (("equivalents", qty(2, "equiv")),))],
    solvents=[("CH2Cl2", "ClCCl", ())],
    conditions=[("temperature", "r.t."), ("time", qty(24, "h"))],
    note="Cleavage/acetylation arrow in Scheme 4; summarized cited work [3]."))
add(record("scheme5_sonogashira_coupling", 3, "literature_example",
    reactants=[("beta-halogenated gamma-butenolide", None, ()), ("terminal alkyne R1CCH", None, ())],
    products=[("alkynyl-substituted gamma-butenolide", None, ())],
    catalysts=[("PdCl2(PPh3)2", None, ()), ("CuI", "[Cu]I", ())],
    reagents=[("K2CO3", "O=C([O-])[O-].[K+].[K+]", ())], conditions=[("temperature", "r.t.")],
    note="Generic Sonogashira arrow in Scheme 5, attributed to references [4,5]."))
add(record("scheme5_organozinc_boron_coupling", 3, "literature_example",
    reactants=[("beta-halogenated gamma-butenolide", None, ()), ("generic organozinc or organoboron reagent R1M", None, ())],
    products=[("R1-substituted gamma-butenolide", None, ())], catalysts=[("Pd(PPh3)4", None, ())],
    note="Generic coupling arrow in Scheme 5, attributed to references [4,5].",
    unresolved=["The drawing groups zinc and boron reagents without row-specific conditions or yields."]))
add(record("eq2_cux2_halolactonization", 3, "literature_example",
    reactants=[("generic 2,3-allenoic acid", None, ())], products=[("beta-halo gamma-butenolide", None, ())],
    reagents=[("CuX2 (X = Cl or Br)", None, ())], solvents=[("acetone-water", None, ())],
    conditions=[("temperature", rng(65, 70, "°C", "65-70 °C")), ("time", rng(2, 4, "h", "2-4 h"))],
    outcomes=[("family_yield", rng(85, 100, "%", "85%-100%"), 0)],
    note="Generic equation (2), attributed to reference [6].",
    unresolved=["The family yield range is not allocated to individual substrates; yield basis is unstated."]))
add(record("scheme6_chiral_salt_halolactonization", 3, "literature_example",
    reactants=[("chiral-base salt of a 2,3-allenoic acid or 2,3-dienoic acid", None, ())],
    products=[("optically active beta-halo gamma-butenolide", None, ())],
    reagents=[("CuX2", None, ())], solvents=[("acetone-water", None, ())],
    conditions=[("temperature", rng(60, 65, "°C", "60-65 °C"))],
    note="Generic chiral-information-transfer family in Scheme 6, attributed to reference [7].",
    unresolved=["Base may be (L)-cinchonidine or (D)/(L)-alpha-methylbenzylamine; substrate-to-base mapping and yields are not printed."]))
add(record("scheme7_asymmetric_pd_cyclization", 3, "literature_example",
    reactants=[("racemic 2,3-allenoic acid", None, ()), ("aryl iodide ArI", None, ())],
    products=[("optically active gamma-butenolide", None, ())],
    catalysts=[("Pd2(dba)3.CHCl3", None, (("loading", qty(2.5, "mol%")),)),
               ("bisoxazoline ligand 1", None, (("loading", qty(20, "mol%")),))],
    reagents=[("i-Pr2NEt", "CC(C)N(C(C)C)C(C)C", ())], solvents=[("MeCN", "CC#N", ())],
    conditions=[("temperature", qty(-15, "°C"))],
    outcomes=[("maximum_ee", qty(53, "%", qualifier="le", raw_text="up to 53% ee"), 0)],
    note="Asymmetric family in Scheme 7, attributed to reference [8].",
    unresolved=["Substrate-specific yield and ee allocation are absent; the drawing reports only the maximum ee."]))
add(record("eq3_allenoate_bromolactonization", 3, "literature_example",
    reactants=[("generic 2,3-allenoate (R = Et or Bn)", None, ())], products=[("brominated gamma-butenolide", None, ())],
    reagents=[("CuBr2", "Br[Cu]Br", ())], solvents=[("ethanol-water", None, ())],
    conditions=[("temperature", rng(80, 85, "°C", "80-85 °C"))],
    outcomes=[("maximum_yield", qty(97, "%", qualifier="le", raw_text="up to 97%"), 0)],
    note="Generic equation (3), attributed to reference [9].",
    unresolved=["Time, individual substrate yields, and yield basis are not printed."]))

# Page 4: additional cyclizations and the chiral-allenol route.
add(record("eq4_allenamide_halolactamization", 4, "literature_example",
    reactants=[("generic 2,3-allenamide", None, ())], products=[("beta-halo gamma-butenolactam", None, ())],
    reagents=[("CuX2 (X = Cl or Br)", None, ())], note="Generic equation (4), attributed to reference [10].",
    unresolved=["R-group cases, conditions, yields, and the subsequent Cu(II)-promoted oxidation details are not allocated here."]))
add(record("eq5_allenyl_malonate_cyclopropanation", 4, "literature_example",
    reactants=[("dimethyl 2-(2,3-allenyl)malonate", None, ()), ("organic halide RX", None, ())],
    products=[("vinylcyclopropane malonate", None, ())], catalysts=[("Pd(PPh3)4", None, ())],
    reagents=[("K2CO3", "O=C([O-])[O-].[K+].[K+]", ()), ("n-Bu4NBr", None, ())],
    solvents=[("MeCN", "CC#N", ())], conditions=[("temperature", "reflux")],
    note="Generic equation (5), attributed to reference [11]."))
add(record("eq6_allenyl_ketone_furan", 4, "literature_example",
    reactants=[("generic 1,2-allenyl ketone", None, ()), ("organic halide R3X", None, ())],
    products=[("polysubstituted furan", None, ())],
    catalysts=[("Pd(PPh3)4", None, (("loading", qty(5, "mol%")),)),
               ("Ag2CO3", None, (("loading", qty(10, "mol%")),))],
    reagents=[("Et3N", "CCN(CC)CC", ())], solvents=[("PhMe", "Cc1ccccc1", ())],
    note="Generic equation (6), attributed to reference [12]."))
add(record("eq7_allyl_bromide_allenyl_ketone_furan", 4, "literature_example",
    reactants=[("generic 1,2-allenyl ketone", None, ()), ("allylic bromide", None, ())],
    products=[("allyl-substituted polysubstituted furan", None, ())],
    catalysts=[("PdCl2(PhCN)2", None, (("loading", qty(5, "mol%")),))],
    reagents=[("K2CO3", "O=C([O-])[O-].[K+].[K+]", ())], solvents=[("MeCN", "CC#N", ())],
    conditions=[("temperature", qty(25, "°C"))], note="Generic equation (7), attributed to reference [13]."))
add(record("eq8_allenol_vinyl_epoxide", 4, "literature_example",
    reactants=[("generic 2,3-allenol 2", None, ()), ("organic iodide R2I", None, ())],
    products=[("trans vinyl epoxide 3", None, ())], note="Generic equation (8), attributed to reference [14].",
    unresolved=["The figure labels the arrow only as Conditions A; their composition and the yield are not stated on this page."]))
add(record("scheme8_chiral_aluminum_addition", 4, "literature_example",
    reactants=[("1-decyn-3-one drawn in Scheme 8", None, ())],
    products=[("chiral terminal propargylic alcohol from Scheme 8", None, ())],
    reagents=[("chiral lithium aluminum binaphthoxide reagent shown in Scheme 8", None, ())],
    outcomes=[("yield", qty(95, "%"), 0)], note="First preparative arrow of Scheme 8, attributed to reference [14].",
    unresolved=["The aluminum reagent contains an unspecified OR group and its exact identity/stoichiometry is unresolved."]))
add(record("scheme8_formaldehyde_homologation", 4, "literature_example",
    reactants=[("chiral terminal propargylic alcohol from Scheme 8", None, ()), ("paraformaldehyde", None, ())],
    products=[("chiral propargylic diol shown in Scheme 8", None, ())], reagents=[("n-BuLi", None, ())],
    outcomes=[("yield", qty(91, "%"), 0)], note="Second preparative arrow of Scheme 8, attributed to reference [14]."))
add(record("scheme8_thp_protection", 4, "literature_example",
    reactants=[("chiral propargylic diol shown in Scheme 8", None, ()), ("DHP", "C1=CCCOC1", (("equivalents", qty(1.1, "equiv")),))],
    products=[("THP-protected propargylic alcohol shown in Scheme 8", None, ())],
    catalysts=[("TsOH", "Cc1ccc(S(=O)(=O)O)cc1", (("loading", qty(10, "mol%")),))],
    outcomes=[("yield", qty(78, "%"), 0)], note="Protection arrow of Scheme 8, attributed to reference [14]."))
add(record("scheme8_lialh4_allenol_formation", 4, "literature_example",
    reactants=[("THP-protected propargylic alcohol shown in Scheme 8", None, ())],
    products=[("optically active allenol (R)-2b", None, ())], reagents=[("LiAlH4", "[Li+].[AlH4-]", ())],
    outcomes=[("yield", qty(61, "%"), 0)], note="Allenol-forming arrow of Scheme 8, attributed to reference [14].",
    unresolved=["The drawing-to-stage connection is compact; exact protection/deprotection state requires source review."]))
add(record("scheme8_cyclization_3k", 4, "literature_example",
    reactants=[("optically active allenol (R)-2b", None, ()), ("(E)-1-iodohexene drawn in Scheme 8", None, ())],
    products=[("(R,R)-3k vinyl epoxide", None, ())], conditions=[("operation", "Conditions A")],
    outcomes=[("yield", qty(52, "%"), 0), ("product_ee", qty(98, "%"), 0)],
    note="Cyclization row of Scheme 8, attributed to reference [14].",
    unresolved=["Starting allenol is printed as 98% ee; the components of Conditions A are not given on this page."]))
add(record("scheme8_cyclization_3l", 4, "literature_example",
    reactants=[("optically active allenol (R)-2b", None, ()), ("p-iodotoluene", "Cc1ccc(I)cc1", ())],
    products=[("(R,R)-3l vinyl epoxide", None, ())], conditions=[("operation", "Conditions A")],
    outcomes=[("yield", qty(85, "%"), 0), ("product_ee", qty(96, "%"), 0)],
    note="Cyclization row of Scheme 8, attributed to reference [14].",
    unresolved=["Starting allenol is printed as 95% ee; Conditions A and yield basis are not given here."]))
add(record("scheme8_cyclization_3m", 4, "literature_example",
    reactants=[("optically active allenol (R)-2b", None, ()), ("p-iodoanisole", "COc1ccc(I)cc1", ())],
    products=[("(R,R)-3m vinyl epoxide", None, ())], conditions=[("operation", "Conditions A")],
    outcomes=[("yield", qty(74, "%"), 0), ("product_ee", qty(97.5, "%"), 0)],
    note="Cyclization row of Scheme 8, attributed to reference [14].",
    unresolved=["Starting allenol is printed as 98% ee; Conditions A and yield basis are not given here."]))
add(record("eq9_allenol_allylic_halide_dihydrofuran", 4, "literature_example",
    reactants=[("generic 2,3-allenol", None, ()), ("allylic halide", None, ())],
    products=[("substituted 2,5-dihydrofuran", None, ())], catalysts=[("PdCl2", "Cl[Pd]Cl", (("loading", qty(5, "mol%")),))],
    solvents=[("DMA", "CC(=O)N(C)C", ())], conditions=[("temperature", "r.t.")],
    note="Generic equation (9), attributed to reference [15]."))

# Page 5: hydrohalogenation families and regioselective monolithiation.
add(record("scheme9_allenic_ketone_hydrohalogenation", 5, "literature_example",
    reactants=[("electron-deficient allenic ketone family", None, ()), ("metal halide MX", None, ())],
    products=[("beta-halo alpha,beta-unsaturated ketone family", None, ())],
    solvents=[("HOAc", "CC(=O)O", ())], conditions=[("temperature", qty(25, "°C"))],
    note="First hydrohalogenation family in Scheme 9, attributed to references [16-22]."))
add(record("scheme9_allenoate_hydrohalogenation", 5, "literature_example",
    reactants=[("electron-deficient allenoate family", None, ()), ("metal halide MX", None, ())],
    products=[("beta-halo alpha,beta-unsaturated ester family", None, ())], reagents=[("acid H+", None, ())],
    note="Second hydrohalogenation family in Scheme 9, attributed to references [16-22]."))
add(record("scheme9_allenoate_lactonization", 5, "literature_example",
    reactants=[("ethyl 2,3-allenoate with four methyl substituents as drawn", None, ())],
    products=[("tetramethyl-substituted gamma-butenolide", None, ())], reagents=[("LiBr", "[Li+].[Br-]", ())],
    solvents=[("HOAc or CF3CO2H", None, ())], conditions=[("temperature", qty(80, "°C"))],
    outcomes=[("family_yield", rng(57, 67, "%", "57%-67%"), 0)],
    note="Cyclization row in Scheme 9, attributed to references [16-22].",
    unresolved=["The yield range is not allocated between the two acid media; yield basis is unstated."]))
add(record("scheme9_allenamide_hydrohalogenation", 5, "literature_example",
    reactants=[("allenamide family", None, ()), ("metal halide MX", None, ())],
    products=[("beta-halo alpha,beta-unsaturated amide family", None, ())],
    outcomes=[("family_yield", rng(75, 99, "%", "75%-99%"), 0)],
    note="Allenamide family in Scheme 9, attributed to references [16-22]."))
add(record("scheme9_allenenitrile_hydrohalogenation", 5, "literature_example",
    reactants=[("allenenitrile family", None, ()), ("metal halide MX", None, ())],
    products=[("beta-halo alpha,beta-unsaturated nitrile family", None, ())],
    outcomes=[("family_yield", rng(76, 87, "%", "76%-87%"), 0)],
    note="Allenenitrile family in Scheme 9, attributed to references [16-22]."))
add(record("scheme9_allenic_sulfone_hydrohalogenation", 5, "literature_example",
    reactants=[("allenic sulfone family", None, ()), ("halide X-", None, ())],
    products=[("beta-halo alpha,beta-unsaturated sulfone family", None, ())], reagents=[("acid H+", None, ())],
    note="Allenic-sulfone family in Scheme 9, attributed to references [16-22]."))
add(record("scheme9_allenic_sulfoxide_hydrohalogenation", 5, "literature_example",
    reactants=[("allenic sulfoxide family", None, ())], products=[("beta-halo alpha,beta-unsaturated sulfoxide family", None, ())],
    reagents=[("AlX3", None, ()), ("H2O", "O", ())], solvents=[("THF", "C1CCOC1", ())],
    conditions=[("temperature", "r.t.")], outcomes=[("family_yield", rng(56, 89, "%", "56%-89%"), 0)],
    note="Allenic-sulfoxide family in Scheme 9, attributed to references [16-22]."))
add(record("scheme9_allenic_phosphine_oxide_hydrohalogenation", 5, "literature_example",
    reactants=[("allenic phosphine oxide shown in Scheme 9", None, ()), ("metal halide MX", None, ())],
    products=[("beta-halo alpha,beta-unsaturated phosphine oxide", None, ())], solvents=[("HOAc", "CC(=O)O", ())],
    outcomes=[("family_yield", rng(60, 75, "%", "60%-75%"), 0)],
    note="Phosphine-oxide row in Scheme 9, attributed to references [16-22]."))
add(record("eq10_hgcl2_monolithiation_alkylation", 5, "literature_example",
    reactants=[("1-phenyl-1-alkyne family", None, ()), ("organic halide R1X", None, ())],
    products=[("monosubstituted alkyne product", None, ())],
    catalysts=[("HgCl2", "Cl[Hg]Cl", (("loading", qty(1.5, "mol%")),))], reagents=[("n-BuLi", None, ())],
    note="Generic equation (10), attributed to references [23,24]."))
add(record("eq11_transmetalation_allene_coupling", 5, "literature_example",
    reactants=[("1-phenyl-1-alkyne family", None, ()), ("aryl halide Ar1X", None, ())],
    products=[("substituted allene", None, ())], catalysts=[("HgCl2", "Cl[Hg]Cl", (("loading", qty(1.5, "mol%")),))],
    reagents=[("n-BuLi", None, ()), ("ZnBr2", "Br[Zn]Br", ())],
    note="Generic equation (11), attributed to reference [25].",
    unresolved=["The palladium catalyst implied by the prose is not specified on the equation arrow."]))
add(record("scheme10_alkyne_product_r_h", 5, "literature_example",
    reactants=[("1-phenyl-1-propyne derivative with R = H", None, ()), ("ethyl 3-iodopropenoate", None, ())],
    products=[("alkyne coupling product shown for R = H", None, ())],
    catalysts=[("HgCl2", "Cl[Hg]Cl", (("loading", qty(1.5, "mol%")),)),
               ("Pd(0)", None, (("loading", qty(5, "mol%")),))],
    reagents=[("n-BuLi", None, ()), ("ZnBr2", "Br[Zn]Br", ())],
    conditions=[("initial_temperature", qty(-78, "°C")), ("warm_to", "r.t.")],
    note="Scheme 10 row a, R = H; attributed to references [26,27].",
    unresolved=["Room temperature is represented by the source endpoint, but exact endpoint temperature and yield are unstated."]))
add(record("scheme10_allene_product_r_npropyl", 5, "literature_example",
    reactants=[("1-phenyl-1-alkyne derivative with R = n-propyl", None, ()), ("ethyl 3-iodopropenoate", None, ())],
    products=[("allene coupling product shown for R = n-propyl", None, ())],
    catalysts=[("HgCl2", "Cl[Hg]Cl", (("loading", qty(1.5, "mol%")),)),
               ("Pd(0)", None, (("loading", qty(5, "mol%")),))],
    reagents=[("n-BuLi", None, ()), ("ZnBr2", "Br[Zn]Br", ())],
    conditions=[("initial_temperature", qty(-78, "°C")), ("warm_to", "r.t.")],
    note="Scheme 10 row a, R = n-propyl; attributed to references [26,27].",
    unresolved=["Exact endpoint temperature and yield are unstated."]))

# Page 6: steric-regioselectivity examples and dibromoalkene chemistry.
for suffix, substrate, partner, products, ratio in [
    ("scheme11_tms_r_h_vinyl_iodide", "TMS-substituted 1-alkyne with R = H", "iodoalkenoate", ["alkyne coupling product"], None),
    ("scheme11_tms_r_npropyl_vinyl_iodide", "TMS-substituted 1-alkyne with R = n-propyl", "iodoalkenoate", ["alkyne coupling product"], None),
    ("scheme11_ph_propyne_o_iodotoluene", "1-phenyl-1-propyne", "o-iodotoluene", ["allene coupling product"], None),
    ("scheme11_tms_propyne_o_iodotoluene", "TMS-substituted propyne", "o-iodotoluene", ["alkyne coupling product"], None),
    ("scheme11_tms_propyne_iodobenzene", "TMS-substituted propyne", "iodobenzene", ["allene product", "alkyne product"], "1:1"),
    ("scheme11_tms_propyne_iodonaphthalene", "TMS-substituted propyne", "iodonaphthalene", ["allene product", "alkyne product"], "2:5"),
    ("scheme11_tbs_propyne_iodonaphthalene", "TBS-substituted propyne", "iodonaphthalene", ["alkyne coupling product"], None),
]:
    outs = []
    if ratio:
        outs.append(("product_ratio", ratio, None))
    add(record(suffix, 6, "literature_example",
        reactants=[(substrate, None, ()), (partner, None, ())],
        products=[(x, None, ()) for x in products],
        catalysts=[("Pd(PPh3)4", None, (("loading", qty(5, "mol%")),))],
        reagents=[("n-BuLi", None, ()), ("ZnBr2", "Br[Zn]Br", ())],
        conditions=[("initial_temperature", qty(-78, "°C")), ("warm_to", "r.t.")], outcomes=outs,
        note="Individual regioselectivity arrow in Scheme 11.",
        unresolved=["Yield and yield basis are not printed; the amount basis of the regioisomer ratio is unstated." if ratio else "Yield and yield basis are not printed."]))

add(record("scheme12_diphenyl_dibromoalkene", 6, "literature_example",
    reactants=[("1,1-dibromo-1,2-diphenylethene", None, ())],
    products=[("1,1-diphenylallene", None, ()), ("diphenylacetylene migration product", None, ())],
    catalysts=[("Pd(PPh3)4", None, ())], conditions=[("temperature", rng(80, 85, "°C", "80-85 °C")), ("time", qty(3, "h"))],
    outcomes=[("allene_gc_yield", qty(15, "%"), 0), ("alkyne_gc_yield", qty(18, "%"), 1),
              ("yield_measurement_basis", "GC", None)],
    note="Upper substrate row of Scheme 12, attributed to references [29,30]."))
add(record("scheme12_phenyl_methyl_dibromoalkene", 6, "literature_example",
    reactants=[("1,1-dibromoalkene bearing phenyl and methyl", None, ())],
    products=[("phenyl-methyl allene product", None, ()), ("phenyl-methyl alkyne migration product", None, ())],
    catalysts=[("Pd(PPh3)4", None, ())], conditions=[("temperature", rng(80, 85, "°C", "80-85 °C")), ("time", qty(2.5, "h"))],
    outcomes=[("allene_gc_yield", qty(15, "%"), 0), ("alkyne_gc_yield", qty(35, "%"), 1),
              ("yield_measurement_basis", "GC", None)],
    note="Lower substrate row of Scheme 12, attributed to references [29,30]."))
add(record("scheme13_k2co3_bu4ncl_path", 6, "literature_example",
    reactants=[("tethered 1,1-dibromoalkene bearing two COOMe groups", None, ())],
    products=[("first Scheme 13 cyclized product", None, ()), ("second Scheme 13 cyclized product", None, ())],
    catalysts=[("Pd(PPh3)4", None, ())], reagents=[("K2CO3", "O=C([O-])[O-].[K+].[K+]", ()), ("Bu4NCl", None, ())],
    solvents=[("xylene", "Cc1ccccc1C", ())],
    outcomes=[("first_product_yield", qty(32, "%"), 0), ("second_product_yield", qty(32, "%"), 1)],
    note="Upper product branch of Scheme 13, attributed to reference [29].",
    unresolved=["Temperature, time, yield basis, and exact xylene isomer are not printed."]))
add(record("scheme13_et3n_bicyclization_path", 6, "literature_example",
    reactants=[("tethered 1,1-dibromoalkene bearing two COOMe groups", None, ())],
    products=[("bicyclic carbopalladation product shown at lower left of Scheme 13", None, ())],
    catalysts=[("Pd(PPh3)4", None, ())], reagents=[("Et3N", "CCN(CC)CC", ())], solvents=[("MeCN", "CC#N", ())],
    conditions=[("temperature", "reflux"), ("time", qty(13, "h"))],
    outcomes=[("yield", qty(61, "%"), 0)],
    note="Lower observed product branch of Scheme 13, attributed to reference [29]."))
add(record("scheme13_proposed_pathway", 6, "mechanism",
    reactants=[("tethered 1,1-dibromoalkene", None, ())],
    products=[("proposed organopalladium intermediate", None, ()), ("crossed-out alpha-dehalopalladation/carbene path", None, ())],
    catalysts=[("Pd(PPh3)4", None, ())],
    outcomes=[("crossed_out_path_observation", "not observed", 1)],
    note="Scheme 13 mechanistic drawing and adjacent prose: intramolecular carbopalladation is proposed to outcompete alpha-dehalopalladation.",
    unresolved=["The depicted intermediates are proposed, not independently observed or isolated."]))


# Coverage ledger. Each region cites its own original page image.
page_records = {page: [r["record_id"] for r in records if f":page{page}:image" in r["evidence_ids"]]
                for page in range(1, 7)}
coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {"page": 1, "state": "attempted", "regions": [
            {"region": "title, abstract, and introductory two-column text", "finding": "Account/summary metadata and broad research themes; no individual reaction arrow, table row, or experimental procedure on this page.", "evidence_ids": [f"{DOC}:page1:image", f"{DOC}:page1:text"]}],
         "record_ids": page_records[1], "unresolved": ["No reaction record is fabricated from abstract-level claims."]},
        {"page": 2, "state": "attempted", "regions": [
            {"region": "left column equation (1) and allenoic-acid discussion", "finding": "Generic Pd/Ag-cocatalyzed allenoic-acid cyclization, cited prior work.", "evidence_ids": [f"{DOC}:page2:image", f"{DOC}:page2:text"]},
            {"region": "right column Schemes 1-2", "finding": "Generic solid-phase workflow plus three distinct resin-loading arrows.", "evidence_ids": [f"{DOC}:page2:image"]},
            {"region": "bottom Scheme 3", "finding": "Specific solid-phase cyclization followed by AlCl3/MeNO2 cleavage; stages split.", "evidence_ids": [f"{DOC}:page2:image"]}],
         "record_ids": page_records[2], "unresolved": ["No yields are printed for Schemes 1-3; catalyst/base identities are incomplete in Scheme 3."]},
        {"page": 3, "state": "attempted", "regions": [
            {"region": "top-left Scheme 4", "finding": "Ether-linked solid-phase cyclization and ZnBr2/AcBr cleavage, treated as successive stages.", "evidence_ids": [f"{DOC}:page3:image"]},
            {"region": "middle-left Scheme 5 and equation (2)", "finding": "Two generic coupling families and CuX2 halolactonization family with reported range.", "evidence_ids": [f"{DOC}:page3:image", f"{DOC}:page3:text"]},
            {"region": "right-column Schemes 6-7 and equation (3)", "finding": "Chiral-salt halolactonization, asymmetric Pd cyclization, and allenoate bromolactonization summaries.", "evidence_ids": [f"{DOC}:page3:image"]}],
         "record_ids": page_records[3], "unresolved": ["Family-level yield/ee maxima are not allocated to individual substrates; yield bases are absent."]},
        {"page": 4, "state": "attempted", "regions": [
            {"region": "left-column equations (4)-(7)", "finding": "Four cited generic cyclization families: allenamides, allenyl malonates, and two allenyl-ketone variants.", "evidence_ids": [f"{DOC}:page4:image", f"{DOC}:page4:text"]},
            {"region": "right-column equation (8) and Scheme 8", "finding": "Generic vinyl-epoxide reaction plus four preparative arrows and three optically enriched coupling rows.", "evidence_ids": [f"{DOC}:page4:image"]},
            {"region": "bottom equation (9)", "finding": "Generic PdCl2-catalyzed allenol/allylic-halide dihydrofuran formation.", "evidence_ids": [f"{DOC}:page4:image"]}],
         "record_ids": page_records[4], "unresolved": ["Conditions A is not defined on this page; compact Scheme 8 stage connectivity and one chiral reagent OR group require review."]},
        {"page": 5, "state": "attempted", "regions": [
            {"region": "left-column Scheme 9", "finding": "Eight distinct cited hydrohalogenation/cyclization families; range outcomes kept at family level.", "evidence_ids": [f"{DOC}:page5:image", f"{DOC}:page5:text"]},
            {"region": "right-column equations (10)-(11)", "finding": "HgCl2-catalyzed monolithiation/alkylation and Zn transmetalation/allene coupling families.", "evidence_ids": [f"{DOC}:page5:image"]},
            {"region": "bottom-right Scheme 10", "finding": "Two regioselectivity rows split by R = H versus n-propyl.", "evidence_ids": [f"{DOC}:page5:image"]}],
         "record_ids": page_records[5], "unresolved": ["Many family arrows omit time, scale, yield basis, and individual range allocation."]},
        {"page": 6, "state": "attempted", "regions": [
            {"region": "left-column Scheme 11", "finding": "Seven distinct steric/regioselectivity arrows, including two reported product ratios.", "evidence_ids": [f"{DOC}:page6:image", f"{DOC}:page6:text"]},
            {"region": "upper-right Scheme 12", "finding": "Two dibromoalkene oxidative-addition examples, each with allene and alkyne GC yields.", "evidence_ids": [f"{DOC}:page6:image"]},
            {"region": "lower-right Scheme 13", "finding": "Two condition-dependent cyclization outcomes plus a proposed/crossed-out mechanistic path.", "evidence_ids": [f"{DOC}:page6:image"]}],
         "record_ids": page_records[6], "unresolved": ["Scheme 11 yields are not printed; Scheme 13 intermediate/pathway is proposed rather than observed. Table 1 and Scheme 14 continue on page 7 and are outside this session."]},
    ],
}


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


write(RUN / "raw_model/records_pages_0001_0006.json", records)
write(RUN / "coverage/pages_0001_0006.json", coverage)

tasks_path = RUN / "tasks.json"
tasks = json.loads(tasks_path.read_text())
for task in tasks:
    page = int(task["evidence_id"].split(":page", 1)[1].split(":", 1)[0])
    if 1 <= page <= 6:
        task["state"] = "attempted"
        task["visual_evidence_id"] = f"{DOC}:page{page}:image"
        task["reason"] = "Original page image visually inspected; records and coverage ledger generated for pages 1-6."
write(tasks_path, tasks)

print(json.dumps({"records": len(records),
                  "by_kind": {k: sum(r["record_kind"] == k for r in records)
                              for k in sorted({r["record_kind"] for r in records})},
                  "pages": [p["page"] for p in coverage["pages"]]}, ensure_ascii=False))
