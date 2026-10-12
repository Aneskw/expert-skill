#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DOC = "doc_32ed381ace69ff22"
OUT = ROOT / "runs/current"


def ev(*pages):
    ids = []
    for p in pages:
        ids += [f"{DOC}:page{p}:text", f"{DOC}:page{p}:image"]
    return ids


def fact(value, evidence):
    return {"value": value, "evidence_ids": list(evidence) if value is not None else [],
            "verification": "unreviewed" if value is not None else "missing"}


def participant(entity_id, role, label, evidence, amounts=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(None, []),
        "smiles": fact(None, []),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": [{"name": k, "fact": fact(v, evidence)} for k, v in (amounts or {}).items()],
    }


def rec(rid, pages, title, participants, conditions=None, outcomes=None, notes=None,
        kind="literature_example", unresolved=None, missing=True):
    evidence = ev(*pages)
    ps = [participant(f"p{i+1}", role, label, evidence, amounts)
          for i, (role, label, amounts) in enumerate(participants)]
    cond = dict(conditions or {})
    if missing:
        for key in ["reaction_scale", "atmosphere", "concentration", "workup", "purification"]:
            cond.setdefault(key, None)
    outs = dict(outcomes or {})
    if any("yield" in k for k in outs):
        outs.setdefault("yield_measurement_basis", None)
    return {
        "record_id": f"{DOC}:{rid}",
        "document_id": DOC,
        "source_reaction_id": rid,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": evidence,
        "participants": ps,
        "steps": [{
            "step_id": "step1",
            "participant_ids": [p["entity_id"] for p in ps],
            "conditions": [{"name": k, "fact": fact(v, evidence)} for k, v in cond.items()],
        }],
        "outcomes": [{"name": k, "fact": fact(v, evidence)} for k, v in outs.items()],
        "notes": [fact(title, evidence)] + [fact(x, evidence) for x in (notes or [])],
        "review": {
            "method": "model", "reviewer": None, "checked_fields": [],
            "unresolved": (unresolved or []) + [
                "This ACCOUNT summarizes cited earlier work; the original cited paper and SI were not supplied.",
                "Structures are drawing- or label-defined and remain unverified with null SMILES.",
            ],
        },
    }


R = []
def add(*args, **kwargs):
    R.append(rec(*args, **kwargs))


# Page 1: conceptual map, prior failures, and Equation 2 condition comparisons.
add("eq1_general", [1], "Equation 1 generic retrosynthetic hydrohalogenation relationship",
    [("reactant", "generic electron-deficient allene", None),
     ("product", "generic 1-functionalized 2-halo-2-alkene", None)],
    kind="general_scheme", missing=False,
    unresolved=["R1/R2/R3, X, and EWG are generic variables; this is not an individual run."])
add("prior_hcl_polymerization", [1], "Cited hydrochlorination of 1,2-allenyl ketones with HCl",
    [("reactant", "1,2-allenyl ketones", None), ("reagent", "HCl", None)],
    outcomes={"reaction_result": "polymerization"})
add("prior_chloroenone_mixture", [1], "Cited alternative hydrochlorination methods",
    [("reactant", "1,2-allenyl ketones", None),
     ("reagent", "N,N'-dimethylhydrazine dihydrochloride or SnCl4", None),
     ("product", "beta,gamma- and alpha,beta-unsaturated beta-chloroenones", None)],
    outcomes={"reaction_result": "mixture; alpha,beta-enone major"},
    unresolved=["The two alternative chlorination reagents are not given separate result values."])
add("eq2_mx_hoac_family", [1], "Equation 2 halide-salt family in acetic acid",
    [("reactant", "3,4-pentadien-2-one", None),
     ("reagent", "NaI, LiI, LiBr-H2O, or LiCl-H2O", None),
     ("solvent", "acetic acid", None), ("product", "4-halo-4-penten-2-one", None)],
    conditions={"temperature": {"number": 25, "unit": "°C"}},
    outcomes={"yield_range": "69-82%"},
    unresolved=["The family yield range is not allocated among the four salts."])
add("eq2_nai_hoac_25", [1], "Equation 2 NaI/HOAc regioselectivity comparison",
    [("reactant", "3,4-pentadien-2-one", None), ("reagent", "NaI", None),
     ("solvent", "HOAc", None), ("product", "enones 1 and 2", None)],
    conditions={"temperature": {"number": 25, "unit": "°C"}},
    outcomes={"product_ratio_1_to_2": "91:9", "yield": None})
add("eq2_mi_hoac_thf_1to1", [1], "Equation 2 HOAc/THF solvent comparison",
    [("reactant", "3,4-pentadien-2-one", None), ("reagent", "MI (LiI or NaI not resolved)", None),
     ("solvent", "HOAc/THF (1:1)", None), ("product", "enones 1 and 2", None)],
    outcomes={"product_ratio_1_to_2": "87:13", "yield": None},
    unresolved=["The sentence does not assign LiI versus NaI to this ratio."])
add("eq2_lii_optimized_large_scale", [2, 3], "Optimized 4-iodo-4-penten-2-one preparation",
    [("reactant", "3,4-pentadien-2-one", {"mass": {"number": 10.7, "unit": "g"}, "amount": {"number": 0.13, "unit": "mol"}}),
     ("reagent", "lithium iodide", {"mass": {"number": 24.3, "unit": "g"}, "amount": {"number": 0.16, "unit": "mol"}}),
     ("reagent", "acetic acid", {"mass": {"number": 23.4, "unit": "g"}, "amount": {"number": 0.39, "unit": "mol"}}),
     ("solvent", "tetrahydrofuran", {"volume_total": {"number": 200, "unit": "mL"}}),
     ("product", "4-iodo-4-penten-2-one", {"isolated_mass": {"number": 16.9, "unit": "g"}})],
    conditions={"temperature": {"number": 0, "unit": "°C"}, "time": "~8 h", "atmosphere": "nitrogen",
                "addition_temperature_limit": "not above 0 °C",
                "workup": "evaporate; dilute with ether; neutralize with cool aqueous K2CO3; separate; extract with ether; brine wash; MgSO4 dry",
                "purification": "distillation"},
    outcomes={"isolated_yield": {"number": 62, "unit": "%"}, "product_ratio_1_to_2": "98:2",
              "boiling_point": "62 °C/1 mmHg", "yield_measurement_basis": "isolated"},
    notes=["Page 2 states the best MI/3 equiv HOAc/THF/0 °C regioisomer ratio; page 3 supplies the LiI preparation."],
    unresolved=["The 98:2 ratio is reported for MI generally; its exact measurement in this large-scale LiI run is not explicitly restated."])

# Page 2: two reproduced starting-material procedures.
add("prep_4_bromo_3_penten_2_one", [2], "Reproduced preparation of 4-bromo-3-penten-2-one (ref. 8)",
    [("reactant", "triphenylphosphine", {"mass": {"number": 132, "unit": "g"}, "amount": {"number": 0.5, "unit": "mol"}}),
     ("reagent", "bromine", {"mass": {"number": 80, "unit": "g"}, "amount": {"number": 0.5, "unit": "mol"}}),
     ("reactant", "acetylacetone", {"mass": {"number": 50, "unit": "g"}, "amount": {"number": 0.5, "unit": "mol"}}),
     ("solvent", "dichloromethane", {"volume_total": {"number": 500, "unit": "mL"}}),
     ("product", "4-bromo-3-penten-2-one", {"isolated_mass": {"number": 70, "unit": "g"}})],
    conditions={"atmosphere": "nitrogen", "bromine_addition_temperature": "not above 10 °C",
                "acetylacetone_addition": "10 min at room temperature", "time": "4-5 h under reflux",
                "workup": "concentrate; add 500 mL ether; remove precipitated triphenylphosphine oxide; wash precipitate with ether (2x100 mL); evaporate",
                "purification": "reduced-pressure distillation"},
    outcomes={"isolated_yield": {"number": 85, "unit": "%"}, "boiling_point": "54-55 °C/15 mmHg", "yield_measurement_basis": "isolated"})
add("prep_3_4_pentadien_2_one", [2], "Reproduced preparation of 3,4-pentadien-2-one (ref. 8)",
    [("reactant", "4-bromo-3-penten-2-one", {"mass": {"number": 65, "unit": "g"}, "amount": {"number": 0.40, "unit": "mol"}}),
     ("reagent", "triethylamine", {"mass": {"number": 45, "unit": "g"}, "amount": {"number": 0.44, "unit": "mol"}}),
     ("solvent", "anhydrous ether", {"volume_total": {"number": 290, "unit": "mL"}}),
     ("product", "3,4-pentadien-2-one", {"isolated_mass": {"number": 21.5, "unit": "g"}})],
    conditions={"temperature": "room temperature", "time": {"number": 5, "unit": "h"},
                "workup": "remove Et3NHBr; wash with ether; wash solution with 5% HCl then cold water; dry MgSO4; evaporate",
                "purification": "distillation"},
    outcomes={"isolated_yield": {"number": 65, "unit": "%"}, "boiling_point": "50 °C/60 mmHg", "yield_measurement_basis": "isolated"})

# Page 3 Scheme 1: one row per salt/substrate combination.
scheme1 = [
    ("nai_butyl", "NaI", "n-C4H9", 90, 3.6), ("libr_butyl", "LiBr-H2O", "n-C4H9", 93, 5),
    ("licl_butyl", "LiCl-H2O", "n-C4H9", 25, 55), ("nai_heptyl", "NaI", "n-C7H15", 87, 3.5),
    ("libr_heptyl", "LiBr-H2O", "n-C7H15", 75, 3.1), ("licl_heptyl", "LiCl-H2O", "n-C7H15", 18, 54),
]
for suffix, mx, rp, zy, ey in scheme1:
    add(f"scheme1_{suffix}", [3], f"Scheme 1 row: {mx}, R'={rp}",
        [("reactant", f"3-{rp} substituted 1,2-allenyl ketone", None), ("reagent", mx, None),
         ("solvent", "HOAc", None), ("product", "Z-3", None), ("product", "E-3", None)],
        conditions={"temperature": {"number": 25, "unit": "°C"}, "time": None},
        outcomes={"NMR_yield_Z_3": {"number": zy, "unit": "%"}, "NMR_yield_E_3": {"number": ey, "unit": "%"},
                  "yield_measurement_basis": "NMR"},
        notes=["No alpha,beta-unsaturated beta-haloenone was observed."])
add("eq3_dimethyl_ketone_family", [3], "Equation 3 5-methyl-3,4-hexadien-2-one family",
    [("reactant", "5-methyl-3,4-hexadien-2-one", None),
     ("reagent", "NaI, LiBr-H2O, or LiCl-H2O", None), ("solvent", "HOAc", None),
     ("product", "4-halo-5-methyl-4-hexen-2-one (4)", None)],
    conditions={"temperature": {"number": 25, "unit": "°C"}},
    outcomes={"yield_range": "89-96%", "alpha_beta_unsaturated_product": "not observed"},
    unresolved=["Individual salt yields are not allocated."])
eq4 = [
    ("nai_hoac", "HOAc", None, "31:69"), ("nai_tfa", "CF3CO2H", 25, "96:4"),
    ("nai_tfa3_thf", "3 equiv CF3CO2H in THF", 78, "80:20"),
    ("nai_mixed_acid", "CF3CO2H/HOAc (1:1)", 82, "96:4"),
]
for suffix, solvent, y, ratio in eq4:
    add(f"eq4_3methyl_{suffix}", [3], f"Equation 4 medium comparison: {solvent}",
        [("reactant", "3-methyl-3,4-pentadien-2-one", None), ("reagent", "NaI", None),
         ("solvent", solvent, None), ("product", "5a", None), ("product", "6a", None)],
        conditions={"temperature": {"number": 25, "unit": "°C"}, "time": None},
        outcomes={"yield": None if y is None else {"number": y, "unit": "%"}, "product_ratio_5a_to_6a": ratio})
add("eq4_mixed_acid_scope_family", [3], "Equation 4 mixed-acid substrate/halide scope",
    [("reactant", "3-methyl- or 3-butyl-3,4-pentadien-2-one", None),
     ("reagent", "NaI, LiBr-H2O, or LiCl-H2O", None), ("solvent", "CF3CO2H/HOAc (1:1)", None),
     ("product", "4-halo-3-methyl(or butyl)-4-penten-2-one 5", None),
     ("product", "alpha,beta-unsaturated enone 6", None)],
    conditions={"temperature": {"number": 25, "unit": "°C"}},
    outcomes={"yield_range_product_5": "70-99%", "product_6_range": "2-5%"},
    unresolved=["The family ranges are not allocated by substrate/halide combination."])
add("acid_unsubstituted_mx_family", [3], "Unsubstituted 2,3-butadienoic acid halide-salt scope",
    [("reactant", "2,3-butadienoic acid", None), ("reagent", "NaI, LiBr-H2O, or LiCl-H2O", None),
     ("solvent", "HOAc", None), ("product", "3-halo-3-butenoic acid", None)],
    conditions={"temperature": {"number": 70, "unit": "°C"}}, outcomes={"yield_range": "87-92%"},
    unresolved=["Individual salt yields and times are not allocated."])
scheme2 = [
    ("butyl_nai", "n-C4H9", "NaI", 95, "90/10"), ("butyl_libr", "n-C4H9", "LiBr-H2O", 89, "70/30"),
    ("butyl_licl", "n-C4H9", "LiCl-H2O", 87, "37/63"), ("heptyl_nai", "n-C7H15", "NaI", 99, "80/20"),
    ("heptyl_libr", "n-C7H15", "LiBr-H2O", 82, "64/36"), ("heptyl_licl", "n-C7H15", "LiCl-H2O", 87, "43/37"),
]
for suffix, rgrp, mx, y, ze in scheme2:
    add(f"scheme2_{suffix}", [3,4], f"Scheme 2 acid row: R={rgrp}, {mx}",
        [("reactant", f"4-{rgrp}-substituted 2,3-butadienoic acid", None), ("reagent", mx, None),
         ("solvent", "HOAc", None), ("product", "E-7 and Z-7", None)],
        conditions={"temperature": "reflux", "time": None},
        outcomes={"yield": {"number": y, "unit": "%"}, "Z_E_ratio_as_printed": ze})
for suffix, mx, t, y in [("nai", "NaI", "2.5 h", 72), ("libr", "LiBr-H2O", "3 h", 61)]:
    add(f"scheme3_{suffix}", [4], f"Scheme 3 2-methyl-substituted acid row: {mx}",
        [("reactant", "2-methyl-substituted 2,3-butadienoic acid", None), ("reagent", mx, None),
         ("solvent", "CF3CO2H", None), ("product", "3-halo-2-methyl-3-butenoic acid 8", None)],
        conditions={"temperature": "room temperature", "time": t}, outcomes={"yield": {"number": y, "unit": "%"}})

# Page 4 allenoate examples and summaries.
add("methyl_butadienoate_mx_family", [4], "Unsubstituted methyl 2,3-butadienoate scope",
    [("reactant", "methyl 2,3-butadienoate", None), ("reagent", "MX", None),
     ("solvent", "HOAc", None), ("product", "methyl 3-halo-3-butenoate", None)],
    outcomes={"yield_range": "56-86%"}, unresolved=["MX identities, individual yields, time, and temperature are not allocated here."])
add("eq5_4alkyl_allenoate_family", [4], "Equation 5 ethyl 4-alkyl allenoate scope",
    [("reactant", "ethyl 4-alkyl-2,3-alkadienoates (R=Me or n-C6H13)", None),
     ("reagent", "NaI, LiBr-H2O, or LiCl-H2O", None), ("solvent", "HOAc or CF3CO2H", None),
     ("product", "ethyl 3-halo-3-alkenoates 9", None)],
    outcomes={"yield_range": "70-98%", "stereoselectivity": "not high"},
    unresolved=["The family range is not allocated by substrate, salt, or solvent."])
add("eq6_ethyl_pentadienoate_hx", [4], "Equation 6 ester hydrolysis side reaction",
    [("reactant", "ethyl 2,3-pentadienoate", None), ("reagent", "HX", None),
     ("product", "ethyl 3-halo-3-pentenoate 9a", None), ("product", "3-halo-3-pentenoic acid 10", None)],
    conditions={"temperature": {"number": 80, "unit": "°C"}}, outcomes={"reaction_result": "mixture of ester 9a and acid 10", "yield": None})
add("eq7_methyl_nai_hoac", [4], "Equation 7 methyl-substituted allenoate with NaI/HOAc",
    [("reactant", "ethyl 2-methyl-2,3-butadienoate", None), ("reagent", "NaI", None),
     ("solvent", "HOAc", None), ("product", "2-enoate 12a", None), ("product", "3-enoate 11a", None)],
    conditions={"temperature": {"number": 80, "unit": "°C"}},
    outcomes={"yield_12a": {"number": 10, "unit": "%"}, "yield_11a": {"number": 41, "unit": "%"}})
add("eq7_methyl_libr_hoac", [4], "Equation 7 methyl-substituted allenoate with LiBr/HOAc",
    [("reactant", "ethyl 2-methyl-2,3-butadienoate", None), ("reagent", "LiBr", None),
     ("solvent", "HOAc", None), ("product", "2-enoate 12a", None), ("product", "3-enoate 11a", None)],
    conditions={"temperature": {"number": 80, "unit": "°C"}}, outcomes={"yield_12a": "<5%", "yield_11a": "<5%"})
add("eq7_methyl_acidic_media_family", [4], "Equation 7 methyl-substituted allenoate in more acidic media",
    [("reactant", "ethyl 2-methyl-2,3-butadienoate", None), ("reagent", "MX", None),
     ("solvent", "CF3CO2H/HOAc (1:1) or CF3CO2H", None), ("product", "ethyl 3-halo-2-methyl-3-butenoate 11a", None)],
    conditions={"temperature": {"number": 80, "unit": "°C"}},
    outcomes={"yield_range": "80-95%", "2_enoate_12a": "not observed"},
    unresolved=["The yield range is not allocated by MX or the two media; CF3CO2H is stated to be more efficient."])
add("eq7_propyl_acidic_media_family", [4], "Equation 7 propyl-substituted allenoate scope",
    [("reactant", "ethyl 2-propyl-2,3-butadienoate", None), ("reagent", "MX", None),
     ("solvent", "CF3CO2H/HOAc (1:1) or CF3CO2H", None), ("product", "ethyl 3-halo-2-propyl-3-butenoate 11b", None)],
    conditions={"temperature": {"number": 80, "unit": "°C"}}, outcomes={"yield_range": "63-98%", "2_enoate_12b": "not observed"},
    unresolved=["The range is not allocated by MX or medium."])
add("scheme4_13ab_family", [4], "Scheme 4 trisubstituted allenoates 13a-b",
    [("reactant", "2,3-dienoates 13a-b", None), ("reagent", "MX", None),
     ("solvent", "CF3CO2H", None), ("product", "beta,gamma-unsaturated 3-enoates 14", None)],
    outcomes={"yield_range": "55-89%"}, unresolved=["No per-substrate or per-halide yields are supplied."])
add("scheme4_13c_cycloisomerization", [4,5], "Scheme 4 4,4-disubstituted allenoate 13c",
    [("reactant", "4,4-disubstituted 2,3-dienoate 13c", None), ("reagent", "MX", None),
     ("solvent", "CF3CO2H", None), ("product", "hydrohalogenation product 14", None),
     ("product", "butenolide 15c", None)], outcomes={"reaction_result": "15c formed as by-product with 14", "yield": None})

# Page 5 functional-group families.
add("eq8_13d_libr", [5], "Equation 8 fully substituted dienoate cycloisomerization",
    [("reactant", "fully substituted 2,3-dienoate 13d", None), ("reagent", "LiBr", None),
     ("solvent", "HOAc or CF3CO2H", None), ("product", "butenolide 15d", None)],
    conditions={"temperature": {"number": 80, "unit": "°C"}}, outcomes={"yield_range": "57-67%", "hydrohalogenation_product_14": "not observed"},
    unresolved=["The two solvent-specific yields are not allocated."])
add("scheme5_16a_16c_family", [5], "Scheme 5 dienamide 16a/16c salt scope",
    [("reactant", "4-methyl-2,3-pentadienamide 16a or 2,3-butadienamide 16c", None),
     ("reagent", "NaI, LiBr-H2O, or LiCl-H2O", None), ("solvent", "HOAc", None),
     ("product", "3-halo-3-alkenamide 17", None)],
    conditions={"temperature": {"number": 70, "unit": "°C"}}, outcomes={"yield_range": "75-99%"},
    unresolved=["The range is not allocated by substrate or salt."])
add("scheme5_16b_family", [5], "Scheme 5 2,3-octadienamide 16b scope",
    [("reactant", "2,3-octadienamide 16b", None), ("reagent", "MX", None),
     ("solvent", "HOAc or CF3CO2H", None), ("product", "3-halo-3-octenamide 17", None)],
    conditions={"temperature": {"number": 70, "unit": "°C"}}, outcomes={"yield_range": "69-98%", "stereoselectivity": "low"},
    unresolved=["The range is not allocated by MX or solvent."])
add("scheme5_16d_media_family", [5], "Scheme 5 N-benzyl dienamide 16d media scope",
    [("reactant", "N-benzyl 2-methyl-2,3-butadienamide 16d", None),
     ("reagent", "MX or aqueous HX", None), ("solvent", "CF3CO2H or aqueous HX", None),
     ("product", "3-halo-3-alkenamide 17", None)], outcomes={"reaction_result": "both MX-CF3CO2H and aqueous HX systems applicable", "yield": None})
add("scheme6_18a_family", [5], "Scheme 6 2,3-butadienenitrile 18a scope",
    [("reactant", "2,3-butadienenitrile 18a", None), ("reagent", "MX", None),
     ("solvent", "HOAc", None), ("product", "3-halo-3-butenenitrile 19", None)], outcomes={"yield_range": "78-86%"})
add("scheme6_18b_hoac", [5], "Scheme 6 4-methyl nitrile 18b in HOAc",
    [("reactant", "4-methyl-2,3-pentadienenitrile 18b", None), ("reagent", "MX", None),
     ("solvent", "HOAc", None), ("product", "3-halo-4-methyl-3-pentenenitrile 19", None)], outcomes={"yield_range": "17-37%"})
add("scheme6_18b_mixed_acid", [5], "Scheme 6 4-methyl nitrile 18b in mixed acid",
    [("reactant", "4-methyl-2,3-pentadienenitrile 18b", None), ("reagent", "MX", None),
     ("solvent", "CF3CO2H/HOAc (1:1)", None), ("product", "3-halo-4-methyl-3-pentenenitrile 19", None)],
    outcomes={"yield_range": "76-80%", "selectivity": "excellent"})
add("scheme6_18c_18d_family", [5], "Scheme 6 substituted nitriles 18c/18d",
    [("reactant", "2,3-octadienenitrile 18c or 4-phenyl-2,3-butadienenitrile 18d", None),
     ("reagent", "MX", None), ("product", "4-substituted 3-halo-3-alkenenitrile 19", None)],
    outcomes={"yield_range": "37-82%", "18d_geometry": "E-isomer only"},
    unresolved=["The reaction medium and individual substrate/halide yields are not stated in this sentence."])
for suffix, cond, solvent, yrange in [
    ("A", "MX (M=Na or Li)", "HOAc (solvent)", "67-80%"),
    ("B", "MX (M=Na or Li); HOAc 1 equiv", "CH3CN", "67-80%"),
    ("C", "HX (reagent and solvent)", "HX", "65-83%")]:
    add(f"scheme7_condition_{suffix.lower()}", [5], f"Scheme 7 allenic sulfone condition {suffix}",
        [("reactant", "1,2-allenic sulfones 20a-d", None), ("reagent", cond, None),
         ("solvent", solvent, None), ("product", "hydrohalogenation product 21", None)],
        outcomes={"yield_range": yrange}, unresolved=["The family yield range is not allocated by substrate or halide."])
add("product21_stability", [5], "Stability test of sulfone hydrohalogenation product 21",
    [("reactant", "product 21", None), ("solvent", "HOAc", None)],
    conditions={"temperature": {"number": 118, "unit": "°C"}, "time": {"number": 11, "unit": "h"}},
    outcomes={"C_C_double_bond_migration": "not observed", "yield": None})

# Page 6 sulfoxide and phosphine oxide sections.
add("scheme8_allenic_sulfone_success", [6], "Scheme 8 cited allenic sulfone comparison",
    [("reactant", "H2C=C=CH-SO2Ph", None), ("reagent", "X- and H+", None),
     ("product", "2-haloallylic sulfone", None)], conditions={"temperature": "heat"}, outcomes={"yield_range": "79-87%"})
add("scheme8_allenic_sulfoxide_failure", [6], "Scheme 8 allenic sulfoxide failure in acidic media",
    [("reactant", "H2C=C=CH-SOPh", None), ("reagent", "X- and H+ (X=Cl, Br, I)", None),
     ("product", "low-polarity product mixture", None)], conditions={"temperature": "heat"},
    outcomes={"expected_2_haloallylic_sulfoxide": "not obtained", "reaction_result": "mixture of low-polarity products", "yield": None})
add("scheme9_alcl3_water_optimization", [6], "AlCl3/H2O optimization for allenic sulfoxides",
    [("reactant", "1,2-allenic sulfoxide 22", None), ("reagent", "AlCl3", {"equivalents": {"number": 0.55, "unit": "equiv"}}),
     ("reagent", "H2O", {"equivalents": {"number": 1, "unit": "equiv"}}), ("solvent", "THF", None),
     ("product", "2-chloroallylic sulfoxide 23", None)], conditions={"temperature": "room temperature", "time": None},
    outcomes={"optimization_result": "most efficient tested AlCl3/H2O ratio", "yield": None})
add("scheme9_alx3_scope", [6], "Scheme 9 AlCl3/AlBr3 hydrohalogenation scope",
    [("reactant", "1,2-allenic sulfoxides 22", None), ("reagent", "AlCl3 or AlBr3 plus H2O", None),
     ("solvent", "THF", None), ("product", "2-haloallylic sulfoxides 23", None)],
    conditions={"temperature": "room temperature"}, outcomes={"yield_range": "56-89%", "relative_efficiency": "AlBr3 less efficient than AlCl3"},
    unresolved=["The overall range is not allocated by substrate or aluminum halide."])
add("scheme9_22a_scope", [6], "Scheme 9 substrate 22a hydrohalogenation family",
    [("reactant", "22a (R=Ph; R1=R2=R3=H)", None), ("reagent", "AlCl3 or AlBr3 plus H2O", None),
     ("solvent", "THF", None), ("product", "23 from 22a", None)], conditions={"temperature": "room temperature"}, outcomes={"yield_range": "81-89%"})
add("scheme9_22b_scope", [6], "Scheme 9 substrate 22b hydrohalogenation family",
    [("reactant", "22b (R=CH3; R1=R2=R3=H)", None), ("reagent", "AlCl3 or AlBr3 plus H2O", None),
     ("solvent", "THF", None), ("product", "23 from 22b", None)], conditions={"temperature": "room temperature"},
    outcomes={"yield_range": "64-71%", "relative_rate": "22b reacted faster than 22a"})
for lab, desc in [("22e", "R=CH3, R1=CH3, R2=R3=H"), ("22f", "R=Ph, R1=CH3, R2=R3=H"), ("22g", "R=Ph, R1=H, R2=R3=CH3")]:
    add(f"scheme9_{lab}_no_reaction", [6], f"Scheme 9 failed substrate {lab}",
        [("reactant", f"{lab} ({desc})", None), ("reagent", "AlCl3 or AlBr3 plus H2O", None),
         ("solvent", "THF", None)], conditions={"temperature": "room temperature", "time": None},
        outcomes={"reaction_result": "did not proceed", "yield": None},
        unresolved=["The prose does not assign the exact aluminum halide, time, or detection limit for this failure."])
add("scheme10_22a_iodination", [6], "Scheme 10 iodination of 22a",
    [("reactant", "22a", None), ("reagent", "NaI", {"equivalents": {"number": 4, "unit": "equiv"}}),
     ("reagent", "AlCl3", {"equivalents": {"number": 0.55, "unit": "equiv"}}), ("reagent", "H2O", None),
     ("solvent", "THF", None), ("product", "2-iodoallylic sulfoxide 23", None)],
    conditions={"temperature": "room temperature", "time": {"number": 4, "unit": "h"}},
    outcomes={"yield": {"number": 79, "unit": "%"}, "hydrochlorination_product": "not observed"})
add("scheme10_22c_iodination", [6], "Scheme 10 iodination of 22c",
    [("reactant", "22c (PhS(O)CH=C=CHCH3)", None), ("reagent", "NaI", None),
     ("reagent", "AlCl3", None), ("reagent", "H2O", None), ("solvent", "THF", None),
     ("product", "2-iodoallylic sulfoxide 23", None)],
    conditions={"temperature": "room temperature", "time": {"number": 3, "unit": "h"}},
    outcomes={"yield": {"number": 69, "unit": "%"}, "Z_E_ratio": "92:8"},
    unresolved=["Scheme 10 does not restate the exact equivalents for 22c."])
add("scheme10_22a_nai_one_equiv", [6], "NaI-equivalent control in iodination of 22a",
    [("reactant", "22a", {"equivalents": {"number": 1, "unit": "equiv"}}),
     ("reagent", "NaI", {"equivalents": {"number": 1, "unit": "equiv"}}),
     ("reagent", "AlCl3", {"equivalents": {"number": 0.55, "unit": "equiv"}}),
     ("product", "hydroiodination product", None), ("product", "hydrochlorination product", None)],
    outcomes={"hydrochlorination_product_yield": {"number": 20, "unit": "%"}, "hydroiodination_product_yield": None})
add("alIII_nucleophilic_attack_mechanism", [6], "Proposed Al(III)-mediated nucleophilic attack mechanism",
    [("reactant", "electron-deficient allene", None), ("reagent", "Al(III) and X-", None),
     ("product", "hydrohalogenation product", None)], kind="mechanism", missing=False,
    notes=["Proposed attack of X- at the allene center carbon; no intermediate is reported as observed."],
    unresolved=["Textual proposal only; no kinetic or intermediate-observation evidence is supplied."])
add("scheme11_24a_mx_hoac", [6], "Scheme 11 propadienyl diphenylphosphine oxide 24a with MX",
    [("reactant", "24a", None), ("reagent", "MX (M=Na or Li; X=Cl, Br, I)", {"equivalents": {"number": 1.1, "unit": "equiv"}}),
     ("solvent", "HOAc", None), ("product", "2-halo-2-propenyl diphenylphosphine oxide 25", None)],
    outcomes={"yield_range": "58-75%"}, unresolved=["The range is not allocated by halide salt."])
add("scheme11_24a_aqueous_hx", [6], "Scheme 11 24a with aqueous HX",
    [("reactant", "24a", None), ("reagent", "aqueous HX", None),
     ("product", "2-halo-2-propenyl diphenylphosphine oxide 25", None)],
    outcomes={"yield_range": "31-46%"}, unresolved=["The range is not allocated by HX identity."])
for lab in ["24b", "24c"]:
    add(f"scheme11_{lab}_low_reactivity", [6], f"Scheme 11 low-reactivity substrate {lab}",
        [("reactant", lab, None), ("reagent", "MX", None), ("solvent", "HOAc", None),
         ("product", "corresponding 25", None)], outcomes={"reactivity": "low", "yield": None},
        unresolved=["No numerical conversion, yield, time, or individual MX identity is supplied."])


records_path = OUT / "raw_model/records_pages_0001_0006.json"
records_path.write_text(json.dumps(R, ensure_ascii=False, indent=2))

by_page = {p: [] for p in range(1, 7)}
for r in R:
    for p in range(1, 7):
        if f"{DOC}:page{p}:text" in r["evidence_ids"]:
            by_page[p].append(r["record_id"])

regions = {
    1: [
        ("Equation 1 and introduction", "Generic retrosynthetic/product-space scheme; not an individual experiment."),
        ("Section 2 prose and Equation 2", "Cited prior failures plus halide-salt family and solvent/temperature regioselectivity comparisons."),
    ],
    2: [
        ("top-left continuation", "Best MI/3 equiv HOAc/THF/0 °C regioselectivity statement, linked to the later LiI preparation."),
        ("Typical Procedure for a Larger Scale Preparation", "Two cited, detailed preparations: 4-bromo-3-penten-2-one and 3,4-pentadien-2-one."),
        ("Biographical Sketches", "No reaction record; author biographies only."),
    ],
    3: [
        ("4-Iodo-4-penten-2-one procedure", "Detailed LiI hydroiodination preparation merged with the optimized Equation 2 record."),
        ("Scheme 1", "Six substrate/halide rows with separate NMR yields for Z-3 and E-3."),
        ("Equations 3 and 4 plus prose", "Ketone family result, four NaI medium comparisons, and mixed-acid family scope."),
        ("Section 3 prose", "Allenic-acid family result and lead-in to Schemes 2-3."),
    ],
    4: [
        ("Schemes 2 and 3", "Six acid-scope rows and two 2-methyl-acid rows transcribed separately."),
        ("Section 4 and Equations 5-7", "Allenoate family summaries, HX hydrolysis, and medium-dependent product outcomes."),
        ("Scheme 4", "Generic trisubstituted-allenoate scope and 13c coproduct case; ranges are not assigned to individual substrates."),
    ],
    5: [
        ("Equation 8", "13d cycloisomerization-only result with LiBr and 57-67% solvent-family range."),
        ("Schemes 5 and 6 with prose", "Dienamide and dienenitrile family summaries; per-substrate yields are unavailable where only ranges are printed."),
        ("Scheme 7 and stability prose", "Three sulfone condition sets plus a separate 118 °C/11 h no-migration test."),
    ],
    6: [
        ("Scheme 8", "Cited sulfone success contrasted with sulfoxide failure/low-polarity mixture."),
        ("Scheme 9 and prose", "AlX3/H2O family results, substrate-dependent ranges, and explicit failures for 22e-g."),
        ("Scheme 10", "Two hydroiodination rows and a one-equivalent NaI hydrochlorination-product control."),
        ("mechanism paragraph", "Textual Al(III)-mediated nucleophilic-attack proposal; not an observed experiment."),
        ("Scheme 11", "24a MX/HOAc and aqueous-HX ranges plus low-reactivity 24b/24c cases."),
    ],
}

unresolved = {
    1: ["Equation 2 family yields are not allocated to individual salts; the HOAc/THF 87:13 sentence does not resolve LiI versus NaI."],
    2: ["No SI is supplied; the reproduced procedures are from cited refs. 7/8 and do not establish this ACCOUNT as the primary experimental report."],
    3: ["Several scope results are family ranges without per-substrate/per-halide allocation; the optimized 98:2 ratio is generic MI wording."],
    4: ["Many allenoate results omit per-salt yields, times, scale, workup, purification, and yield basis."],
    5: ["Amide/nitrile/sulfone results are mostly family summaries; exact substrate-condition-to-yield mappings are absent."],
    6: ["AlX3 and phosphine-oxide ranges lack complete row allocation; 22e-g failure conditions and 24b/c conversions are not quantified."],
}
coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [{
        "page": p,
        "state": "attempted",
        "regions": [{"region": a, "finding": b, "evidence_ids": [f"{DOC}:page{p}:image"]} for a, b in regions[p]],
        "record_ids": by_page[p],
        "unresolved": unresolved[p],
    } for p in range(1, 7)],
}
(OUT / "coverage/pages_0001_0006.json").write_text(json.dumps(coverage, ensure_ascii=False, indent=2))

tasks_path = OUT / "tasks.json"
tasks = json.loads(tasks_path.read_text())
for task in tasks:
    if task["document_id"] == DOC and task["task_id"] in {f"{DOC}:page{p}:text" for p in range(1, 7)}:
        task["state"] = "attempted"
        task["visual_evidence_id"] = task["task_id"].replace(":text", ":image")
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2))

print(json.dumps({"records": len(R), "pages": list(by_page), "records_path": str(records_path)}, ensure_ascii=False))
