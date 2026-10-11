#!/usr/bin/env python3
"""Build evidence-linked records for source.pdf pages 1-5.

The source is a short proceedings/review article.  Its reaction sections point to
the underlying publications [4]-[9], so summarized results are classified as
literature examples.  Generic R-group arrows and the sulfone condition families
are retained as general schemes, not promoted to individual experiments.
"""

import json
from pathlib import Path


DOC = "doc_b10e9174e0e6771d"
BASE = Path(__file__).resolve().parents[1]


def ev(*pages):
    ids = []
    for page in pages:
        ids.extend([f"{DOC}:page{page}:text", f"{DOC}:page{page}:image"])
    return ids


def fact(value, evidence):
    return {
        "value": value,
        "evidence_ids": list(evidence) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def field(name, value, evidence):
    return {"name": name, "fact": fact(value, evidence)}


def participant(entity_id, role, label, name, _smiles, amounts, *, evidence):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence),
        "smiles": fact(None, []),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": [field(k, v, evidence) for k, v in (amounts or [])],
    }


def record(
    rid,
    pages,
    kind,
    participants,
    conditions,
    outcomes,
    notes,
    unresolved=None,
):
    evidence = ev(*pages)
    pids = [p[0] for p in participants]
    return {
        "record_id": f"{DOC}:{rid}",
        "document_id": DOC,
        "source_reaction_id": rid,
        "record_kind": kind,
        "status": "needs_review",
        "completeness": "partial",
        "evidence_ids": evidence,
        "participants": [participant(*p, evidence=evidence) for p in participants],
        "steps": [
            {
                "step_id": "step1",
                "participant_ids": pids,
                "conditions": [field(k, v, evidence) for k, v in conditions]
                + [field("reaction_time", None, [])],
            }
        ],
        "outcomes": [field(k, v, evidence) for k, v in outcomes]
        + [field("yield_measurement_basis", None, [])],
        "notes": [fact(v, evidence) for v in notes],
        "review": {
            "method": "model",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": [
                "The proceedings/review article cites an underlying publication; no primary experimental procedure is supplied here.",
                "Structures conveyed by drawings, labels, or generic R groups remain unverified; SMILES are intentionally null.",
                "Reaction charge, concentration, atmosphere, time, workup, purification, and yield basis are missing unless explicitly stated.",
                "No supporting-information file was supplied or explicitly associated in this pilot.",
            ]
            + list(unresolved or []),
        },
    }


R = []


def add(*args, **kwargs):
    R.append(record(*args, **kwargs))


# Page 1: ketones and Scheme 1.
add(
    "scheme1_allenyl_ketone_general",
    [1],
    "general_scheme",
    [
        ("allene1", "reactant", None, "generic 1,2-allenyl ketone 1", None, None),
        ("mx", "reagent", None, None, "MX", None),
        ("hoac", "solvent", None, None, "acetic acid (HOAc)", None),
        ("product2", "product", None, "generic beta-halo-beta,gamma-unsaturated ketone 2", None, None),
    ],
    [("temperature", {"number": 25, "unit": "°C"})],
    [("yield", None)],
    ["Scheme 1 is a generic R-group transformation; R1/R2 = H, Me, n-C4H9, or n-C7H15; R3 = H or Me."],
)
add(
    "ketone_pentadienone_mx_hoac_25c",
    [1],
    "literature_example",
    [
        ("substrate", "reactant", None, None, "3,4-pentadien-2-one", None),
        ("mx", "reagent", None, None, "MX (M = Na or Li; X = I, Br, or Cl)", None),
        ("hoac", "solvent", None, None, "acetic acid", None),
        ("product", "product", None, None, "4-halo-4-penten-2-one", None),
    ],
    [("temperature", {"number": 25, "unit": "°C"})],
    [("yield_range", "69-82%")],
    ["Summarized from reference 4."],
)
add(
    "ketone_pentadienone_iodide_regioselectivity",
    [1],
    "literature_example",
    [
        ("substrate", "reactant", None, None, "3,4-pentadien-2-one", None),
        ("mi", "reagent", None, None, "LiI or NaI", None),
        ("hoac", "reagent", None, None, "HOAc (3 N)", None),
        ("thf", "solvent", None, None, "tetrahydrofuran (THF)", None),
        ("beta_gamma", "product", None, None, "beta,gamma-unsaturated iodoenone", None),
        ("alpha_beta", "product", None, None, "alpha,beta-unsaturated iodoenone", None),
    ],
    [("temperature", {"number": 0, "unit": "°C"})],
    [("beta_gamma_to_alpha_beta_ratio", "98:2")],
    ["Described as the best conditions among those summarized from reference 5."],
)
add(
    "ketone_3_alkyl_iodo_bromo_scope",
    [1],
    "literature_example",
    [
        ("substrate", "reactant", None, None, "3-alkyl-1,2-allenyl ketones", None),
        ("mx", "reagent", None, None, "iodide or bromide metal halide MX", None),
        ("hoac", "solvent", None, None, "acetic acid", None),
        ("product", "product", None, None, "Z beta-halo-beta,gamma-unsaturated ketones", None),
    ],
    [("temperature", {"number": 25, "unit": "°C"})],
    [("yield_range", "75-93%"), ("stereoselectivity", "Z:E >95:5")],
    ["Hydroiodination and hydrobromination are summarized together; no per-halide yields are printed."],
)
add(
    "ketone_3_alkyl_chlorination",
    [1, 2],
    "literature_example",
    [
        ("substrate", "reactant", None, None, "3-alkyl-1,2-allenyl ketones", None),
        ("chloride", "reagent", None, None, "chloride metal halide MX", None),
        ("hoac", "solvent", None, None, "acetic acid", None),
        ("e_product", "product", None, None, "E beta-chloro-beta,gamma-unsaturated ketone", None),
        ("z_product", "product", None, None, "Z beta-chloro-beta,gamma-unsaturated ketone", None),
    ],
    [("temperature", {"number": 25, "unit": "°C"})],
    [("stereochemical_result", "E and Z isomers; E predominating"), ("yield", None)],
    ["The sentence begins on page 1 and continues on page 2."],
)

# Page 2: further ketone scope, carboxylic acids/esters, Scheme 3, and start of amides.
add(
    "ketone_3_3_dimethyl_scope",
    [2],
    "literature_example",
    [
        ("substrate", "reactant", None, None, "3,3-dimethyl-substituted 1,2-allenyl methyl ketone", None),
        ("mx", "reagent", None, None, "MX", None),
        ("hoac", "solvent", None, None, "acetic acid", None),
        ("product", "product", None, None, "4-halo-5-methyl-4-hexen-2-ones", None),
        ("alpha_beta", "product", None, None, "alpha,beta-unsaturated beta-haloenones", None),
    ],
    [("temperature", {"number": 25, "unit": "°C"})],
    [("yield_range", "89-96%"), ("alpha_beta_product_observed", False)],
    ["Summarized from reference 5."],
)
add(
    "ketone_1_methyl_nai_hoac",
    [2],
    "literature_example",
    [
        ("substrate", "reactant", None, None, "1-methyl-1,2-allenyl ketones", None),
        ("nai", "reagent", None, None, "NaI", None),
        ("hoac", "solvent", None, None, "acetic acid", None),
        ("beta_gamma", "product", None, None, "beta,gamma-unsaturated beta-iodoenone", None),
        ("alpha_beta", "product", None, None, "alpha,beta-unsaturated beta-iodoenone", None),
    ],
    [],
    [("product_distribution", "mixture of beta,gamma- and alpha,beta-unsaturated beta-iodoenones"), ("yield", None)],
    ["No numerical yield or regioisomer ratio is printed."],
)
add(
    "ketone_1_methyl_nai_tfa_hoac",
    [2],
    "literature_example",
    [
        ("substrate", "reactant", None, None, "1-methyl-1,2-allenyl ketones", None),
        ("nai", "reagent", None, None, "NaI", None),
        ("tfa", "solvent", None, None, "trifluoroacetic acid (CF3COOH)", None),
        ("hoac", "solvent", None, None, "acetic acid", None),
        ("product", "product", None, None, "beta,gamma-unsaturated beta-iodoenone", None),
    ],
    [("solvent_ratio", "CF3COOH:HOAc = 1:1")],
    [("regioselectivity", "beta,gamma product highly selective"), ("yield", None)],
    ["No numerical yield or selectivity ratio is printed for this sentence."],
)
add(
    "ketone_3_alkyl_3_4_pentadienone_scope",
    [2],
    "literature_example",
    [
        ("substrate", "reactant", None, None, "3-alkyl-3,4-pentadien-2-one", None),
        ("mx", "reagent", None, None, "MX", None),
        ("tfa", "solvent", None, None, "trifluoroacetic acid (CF3COOH)", None),
        ("hoac", "solvent", None, None, "acetic acid", None),
        ("product", "product", None, None, "4-halo-3-alkyl-4-penten-2-ones", None),
    ],
    [("solvent_ratio", "CF3COOH:HOAc = 1:1")],
    [("yield_range", "70-99%"), ("beta_gamma_to_alpha_beta_selectivity", ">93:7")],
    ["The phrase 'under these conditions' refers to the immediately preceding 1:1 CF3COOH/HOAc medium."],
)
add(
    "scheme2_dienyl_acid_ester_general",
    [2],
    "general_scheme",
    [
        ("allene3", "reactant", "3", "generic 2,3-dienoic acid or ester", None, None),
        ("mx", "reagent", None, None, "MX", None),
        ("product4", "product", "4", "generic 3-halo-3-alkenoic acid or ester", None, None),
    ],
    [("acidic_medium", "H+")],
    [("yield", None)],
    ["Scheme 2 is a generic R-group transformation and does not provide a row-level yield."],
)
add(
    "acid_methyl_ester_mx_hoac_70c",
    [2],
    "literature_example",
    [
        ("substrate", "reactant", None, None, "2,3-butadienoic acid or methyl 2,3-butadienoate", None),
        ("mx", "reagent", None, None, "MX", None),
        ("hoac", "solvent", None, None, "acetic acid", None),
        ("product", "product", None, None, "corresponding 3-halo-3-alkenoic acid or methyl ester", None),
    ],
    [("temperature", {"number": 70, "unit": "°C"})],
    [("yield_range", "56-92%")],
    ["The printed product name '3-halo-3-butadienoic acid/methyl ester' is retained conceptually without correcting nomenclature; summarized from reference 4."],
)
add(
    "acid_4_alkyl_nai_hoac_reflux",
    [2],
    "literature_example",
    [
        ("substrate", "reactant", None, None, "4-alkyl-substituted 2,3-butadienoic acid", None),
        ("nai", "reagent", None, None, "NaI", None),
        ("hoac", "solvent", None, None, "acetic acid", None),
        ("product", "product", None, None, "Z 3-iodo-3-alkenoic acid", None),
    ],
    [("temperature", "reflux")],
    [("stereoselectivity", "fairly good Z selectivity"), ("yield", None)],
    ["No numerical yield or Z:E ratio is printed."],
)
add(
    "acid_4_alkyl_libr_licl_hoac",
    [2],
    "literature_example",
    [
        ("substrate", "reactant", None, None, "4-alkyl-substituted 2,3-butadienoic acid", None),
        ("halide", "reagent", None, None, "LiBr·H2O or LiCl·H2O", None),
        ("hoac", "solvent", None, None, "acetic acid", None),
        ("z_product", "product", None, None, "Z 3-halo-3-alkenoic acid", None),
        ("e_product", "product", None, None, "E 3-halo-3-alkenoic acid", None),
    ],
    [],
    [("stereochemical_result", "mixture of Z and E isomers with lower selectivity"), ("yield", None)],
    ["The hydrate notation is retained as printed; no numerical yield or Z:E ratio is given."],
)
add(
    "acid_2_methyl_mx_tfa",
    [2],
    "literature_example",
    [
        ("substrate", "reactant", None, None, "2-methyl-2,3-butadienoic acid", None),
        ("mx", "reagent", None, None, "MX", None),
        ("tfa", "solvent", None, None, "trifluoroacetic acid (CF3CO2H)", None),
        ("product", "product", None, None, "corresponding 3-halo-2-methyl-3-alkenoic acid", None),
    ],
    [],
    [("yield_range", "54-72%")],
    ["Summarized from reference 6."],
)
add(
    "ester_4_alkyl_mx_acid_media",
    [2],
    "literature_example",
    [
        ("substrate", "reactant", None, None, "ethyl 4-alkyl-substituted 2,3-butadienoate", None),
        ("mx", "reagent", None, None, "MX", None),
        ("acid_medium", "solvent", None, None, "HOAc or CF3CO2H", None),
        ("product", "product", None, None, "ethyl 3-halo-3-alkenoate", None),
    ],
    [],
    [("yield_range", "82-99%"), ("stereoselectivity", "not high")],
    ["Results for the two alternative acid media are summarized together."],
)
add(
    "ester_2_alkyl_mx_hoac",
    [2],
    "literature_example",
    [
        ("substrate", "reactant", None, None, "ethyl 2-alkyl-2,3-butadienoate", None),
        ("mx", "reagent", None, None, "MX", None),
        ("hoac", "solvent", None, None, "acetic acid", None),
        ("enoate2", "product", None, None, "2-enoate", None),
        ("enoate3", "product", None, None, "3-enoate", None),
    ],
    [],
    [("product_distribution", "mixture of 2-enoates and 3-enoates"), ("yield", "low"), ("selectivity", "low")],
    ["The source provides no numerical yield or product ratio."],
)
add(
    "ester_2_alkyl_mx_tfa_hoac",
    [2],
    "literature_example",
    [
        ("substrate", "reactant", None, None, "ethyl 2-alkyl-2,3-butadienoate", None),
        ("mx", "reagent", None, None, "MX", None),
        ("tfa", "solvent", None, None, "trifluoroacetic acid", None),
        ("hoac", "solvent", None, None, "acetic acid", None),
        ("product", "product", None, None, "ethyl 3-halo-2-methyl-3-butenoate", None),
        ("enoate2", "product", None, None, "2-enoate", None),
    ],
    [("solvent_ratio", "CF3CO2H:HOAc = 1:1")],
    [("yield", "fairly good"), ("2_enoate_observed", False)],
    ["The source gives no numerical yield."],
)
add(
    "ester_2_alkyl_mx_tfa",
    [2],
    "literature_example",
    [
        ("substrate", "reactant", None, None, "ethyl 2-alkyl-2,3-butadienoate", None),
        ("mx", "reagent", None, None, "MX", None),
        ("tfa", "solvent", None, None, "trifluoroacetic acid", None),
        ("product", "product", None, None, "ethyl 3-halo-2-methyl-3-butenoate", None),
        ("enoate2", "product", None, None, "2-enoate", None),
    ],
    [],
    [("relative_efficiency", "more efficient than CF3CO2H-HOAc (1:1)"), ("2_enoate_observed", False), ("yield", None)],
    ["No numerical yield or definition of efficiency is printed."],
)
add(
    "ester_trisubstituted_scope",
    [2],
    "literature_example",
    [
        ("substrate", "reactant", None, None, "trisubstituted allenoates", None),
        ("mx", "reagent", None, None, "MX", None),
        ("product", "product", None, None, "corresponding hydrohalogenation products", None),
    ],
    [],
    [("qualitative_result", "reaction went smoothly"), ("yield", None)],
    ["The sentence does not specify structures, medium, yield, or selectivity."],
)
add(
    "scheme3_fully_substituted_butenolide",
    [2],
    "literature_example",
    [
        ("allenoate5", "reactant", "5", "fully substituted ethyl 2,3-dienoate", None, None),
        ("libr", "reagent", None, None, "LiBr", None),
        ("acid_medium", "solvent", None, None, "HOAc or CF3CO2H", None),
        ("butenolide6", "product", "6", "butenolide", None, None),
    ],
    [("temperature", {"number": 80, "unit": "°C"})],
    [("yield_range", "57-67%"), ("butenolide_only_observed_reaction", True)],
    ["Scheme 3 combines the two alternative acid media into one displayed yield range; summarized from reference 6."],
)
add(
    "amide_7a_7c_7d_scope",
    [2, 3],
    "literature_example",
    [
        ("substrates", "reactant", "7a, 7c, 7d", "4-methyl-2,3-pentadienamide; 2,3-butadienamide; or 2-methyl-2,3-butadienamide", None, None),
        ("mx", "reagent", None, None, "MX", None),
        ("acid_medium", "solvent", None, None, "HOAc or CF3CO2H", None),
        ("products", "product", "8", "corresponding 3-halo-3-enamides", None, None),
    ],
    [],
    [("shared_family_yield_range", "75-99%")],
    ["The sentence begins on page 2 and ends on page 3; it reports one shared range, not per-substrate yields."],
)

# Page 3: remaining amide scope, nitriles, and sulfone condition families.
add(
    "amide_7b_scope",
    [3],
    "literature_example",
    [
        ("substrate", "reactant", "7b", "2,3-octadienamide", None, None),
        ("mx", "reagent", None, None, "MX", None),
        ("acid_medium", "solvent", None, None, "HOAc or CF3CO2H", None),
        ("z_product", "product", None, None, "Z 3-halo-3-octenamide", None),
        ("e_product", "product", None, None, "E 3-halo-3-octenamide", None),
    ],
    [],
    [("yield", "high"), ("stereoselectivity", "low"), ("isomer_separation", "Z and E isomers separable by silica-gel chromatography")],
    ["No numerical yield or Z:E ratio is printed."],
)
add(
    "nitrile_9a_mx_hoac",
    [3],
    "literature_example",
    [
        ("substrate9a", "reactant", "9a", "2,3-butadienenitrile", None, None),
        ("mx", "reagent", None, None, "MX", None),
        ("hoac", "solvent", None, None, "acetic acid", None),
        ("product", "product", None, None, "3-halo-3-butenenitriles", None),
    ],
    [],
    [("prose_yield_range", "78-87%"), ("scheme5_yield_range", "76-87%")],
    ["The prose and Scheme 5 lower yield bounds disagree."],
    ["Resolve the printed 78% (prose) versus 76% (Scheme 5) lower yield bound against the underlying reference 6."],
)
add(
    "nitrile_9b_mx_hoac",
    [3],
    "literature_example",
    [
        ("substrate9b", "reactant", "9b", "4-methyl-2,3-pentadienenitrile", None, None),
        ("mx", "reagent", None, None, "MX", None),
        ("hoac", "solvent", None, None, "acetic acid", None),
        ("product", "product", None, None, "3-halo-4-methyl-3-pentenenitrile", None),
    ],
    [],
    [("yield_range", "18-37%")],
    ["The source characterizes this range as low yield."],
)
add(
    "nitrile_9b_mx_tfa_hoac",
    [3],
    "literature_example",
    [
        ("substrate9b", "reactant", "9b", "4-methyl-2,3-pentadienenitrile", None, None),
        ("mx", "reagent", None, None, "MX", None),
        ("tfa", "solvent", None, None, "trifluoroacetic acid", None),
        ("hoac", "solvent", None, None, "acetic acid", None),
        ("product", "product", None, None, "3-halo-4-methyl-3-pentenenitrile", None),
    ],
    [("solvent_ratio", "CF3CO2H:HOAc = 1:1")],
    [("yield_range", "76-80%"), ("selectivity", "excellent")],
    ["No numerical selectivity ratio is printed."],
)
add(
    "nitrile_9c_9d_scope",
    [3],
    "literature_example",
    [
        ("substrates", "reactant", "9c, 9d", "2,3-octadienenitrile or 4-phenylbutadienenitrile", None, None),
        ("mx", "reagent", None, None, "MX", None),
        ("products", "product", None, None, "4-substituted 3-halo-3-butenenitriles", None),
    ],
    [],
    [("shared_family_yield_range", "37-82%")],
    ["The phrase 'corresponding reactions' does not unambiguously assign HOAc versus mixed-acid medium; the solvent is left missing."],
    ["Reaction medium for substrates 9c and 9d is not explicit in this summary."],
)
add(
    "sulfone_scheme6_conditions_a",
    [3],
    "general_scheme",
    [
        ("sulfone11", "reactant", "11", "generic 1,2-allenic sulfone", None, None),
        ("mx", "reagent", None, None, "MX (M = Na or Li)", None),
        ("hoac", "solvent", None, None, "acetic acid", None),
        ("sulfone12", "product", "12", "generic 2-haloallylic sulfone", None, None),
    ],
    [("condition_set", "A")],
    [("yield", None)],
    ["Scheme 6 condition set A; generic R-group scheme summarized from reference 8."],
)
add(
    "sulfone_scheme6_conditions_b",
    [3],
    "general_scheme",
    [
        ("sulfone11", "reactant", "11", "generic 1,2-allenic sulfone", None, None),
        ("mx", "reagent", None, None, "MX (M = Na or Li)", None),
        ("hoac", "reagent", None, None, "acetic acid", [("equivalents", {"number": 1, "unit": "equiv"})]),
        ("acn", "solvent", None, None, "acetonitrile (CH3CN)", None),
        ("sulfone12", "product", "12", "generic 2-haloallylic sulfone", None, None),
    ],
    [("condition_set", "B")],
    [("yield", None)],
    ["Scheme 6 condition set B; generic R-group scheme summarized from reference 8."],
)
add(
    "sulfone_scheme6_conditions_c",
    [3],
    "general_scheme",
    [
        ("sulfone11", "reactant", "11", "generic 1,2-allenic sulfone", None, None),
        ("hx", "reagent", None, None, "HX (solvent and reagent)", None),
        ("sulfone12", "product", "12", "generic 2-haloallylic sulfone", None, None),
    ],
    [("condition_set", "C")],
    [("yield", None)],
    ["Scheme 6 condition set C; generic R-group scheme summarized from reference 8."],
)

# Page 4: sulfoxides and phosphine oxides.
add(
    "sulfoxide_mx_hoac_failure",
    [4],
    "literature_example",
    [
        ("substrate", "reactant", None, None, "1,2-allenic sulfoxides", None),
        ("mx", "reagent", None, None, "MX", None),
        ("hoac", "solvent", None, None, "acetic acid", None),
        ("expected", "product", None, None, "expected 2-haloallylic sulfoxides", None),
    ],
    [],
    [("expected_product_observed", False), ("yield", None)],
    ["The failed MX/HOAc experiment is explicitly reported before the AlX3 method."],
)
add(
    "sulfoxide_alcl3_water_optimization",
    [4],
    "literature_example",
    [
        ("substrate", "reactant", None, None, "1,2-allenic sulfoxides", None),
        ("alcl3", "reagent", None, None, "AlCl3", [("equivalents", {"number": 0.55, "unit": "equiv"})]),
        ("water", "reagent", None, None, "water", [("equivalents", {"number": 1, "unit": "equiv"})]),
        ("product", "product", None, None, "2-chloroallylic sulfoxides", None),
    ],
    [],
    [("qualitative_optimization_result", "best AlCl3/H2O ratio for conversion speed"), ("yield", None)],
    ["The source says water promotes the reaction and the AlCl3/H2O ratio affects conversion speed; no numeric rate or yield is tied to this sentence."],
)
add(
    "sulfoxide_alx3_scope",
    [4],
    "literature_example",
    [
        ("sulfoxide13", "reactant", "13", "generic 1,2-allenic sulfoxide", None, None),
        ("alx3", "reagent", None, None, "AlBr3 or AlCl3", None),
        ("water", "reagent", None, None, "water", None),
        ("thf", "solvent", None, None, "tetrahydrofuran", None),
        ("sulfoxide14", "product", "14", "generic 2-haloallylic sulfoxide", None, None),
    ],
    [("temperature", "room temperature")],
    [("shared_family_yield_range", "56-89%"), ("relative_efficiency", "AlBr3 less efficient than AlCl3")],
    ["Scheme 7 and prose summarize AlBr3 and AlCl3 together; no per-halide yields are printed. Standard conditions include water, but its exact amount is established separately in the preceding optimization statement."],
)
add(
    "sulfoxide_iodination_selectivity",
    [4],
    "literature_example",
    [
        ("substrate", "reactant", None, None, "1,2-allenic sulfoxides", None),
        ("nai", "reagent", None, None, "NaI", [("equivalents", {"number": 4, "unit": "equiv"})]),
        ("alcl3", "reagent", None, None, "AlCl3", [("equivalents", {"number": 0.55, "unit": "equiv"})]),
        ("iodide", "product", None, None, "2-iodoallylic sulfoxide", None),
        ("chloride", "product", None, None, "hydrochlorination product", None),
    ],
    [],
    [("hydrochlorination_product_observed", False), ("iodination_yield", None)],
    ["Hydroiodination is reported qualitatively; no numerical iodination yield is tied to this condition in the summary."],
)
add(
    "phosphine_15a_mx_hoac",
    [4],
    "literature_example",
    [
        ("substrate15a", "reactant", "15a", "propadienyl diphenyl phosphine oxide", None, None),
        ("mx", "reagent", None, None, "MX (M = Na or Li; X = Cl, Br, or I)", None),
        ("hoac", "solvent", None, None, "acetic acid", None),
        ("product16", "product", "16", "2-halo-2-propenyl diphenyl phosphine oxides", None, None),
    ],
    [],
    [("prose_yield_range", "58-75%"), ("scheme8_yield_range", "60-75%")],
    ["The prose and Scheme 8 lower yield bounds disagree; summarized from reference 8."],
    ["Resolve the printed 58% (prose) versus 60% (Scheme 8) lower yield bound against the underlying reference 8."],
)
add(
    "phosphine_15a_aqueous_hx",
    [4],
    "literature_example",
    [
        ("substrate15a", "reactant", "15a", "propadienyl diphenyl phosphine oxide", None, None),
        ("hx", "reagent", None, None, "aqueous HX", None),
        ("product16", "product", "16", "2-halo-2-propenyl diphenyl phosphine oxides", None, None),
    ],
    [],
    [("yield_range", "31-46%")],
    ["The source characterizes these as low yields."],
)
add(
    "phosphine_15b_15c_mx_hoac",
    [4],
    "literature_example",
    [
        ("substrates", "reactant", "15b, 15c", "substituted allenyl diphenyl phosphine oxides 15b and 15c", None, None),
        ("mx", "reagent", None, None, "MX", None),
        ("hoac", "solvent", None, None, "acetic acid", None),
        ("products", "product", None, None, "corresponding hydrohalogenation products", None),
    ],
    [],
    [("reactivity", "low"), ("yield", None)],
    ["No individual product structures, yields, or conditions are printed for 15b and 15c."],
)


record_ids = {r["source_reaction_id"]: r["record_id"] for r in R}


def ids(*names):
    return [record_ids[n] for n in names]


coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1,
            "state": "attempted",
            "regions": [
                {
                    "region": "title, abstract, and introduction",
                    "finding": "Article-level overview and prior-work motivation; no standalone current experimental procedure.",
                    "evidence_ids": ev(1),
                },
                {
                    "region": "lower half, 1,2-allenyl ketone prose and Scheme 1",
                    "finding": "Generic Scheme 1 plus cited ketone hydrohalogenation examples, yield ranges, regioisomer ratio, and stereoselectivity; chlorination sentence continues on page 2.",
                    "evidence_ids": ev(1),
                },
            ],
            "record_ids": ids(
                "scheme1_allenyl_ketone_general",
                "ketone_pentadienone_mx_hoac_25c",
                "ketone_pentadienone_iodide_regioselectivity",
                "ketone_3_alkyl_iodo_bromo_scope",
                "ketone_3_alkyl_chlorination",
            ),
            "unresolved": [
                "Scheme 1 and prose provide family ranges rather than compound-by-compound results.",
                "No SI or experimental procedure is supplied.",
            ],
        },
        {
            "page": 2,
            "state": "attempted",
            "regions": [
                {
                    "region": "top, continuation of ketone section",
                    "finding": "Ketone substrate families, solvent-dependent regioselectivity, yield ranges, and an explicit non-observed alpha,beta product.",
                    "evidence_ids": ev(2),
                },
                {
                    "region": "middle, carboxylic acid/ester prose and Scheme 2",
                    "finding": "Generic Scheme 2 and cited acid/ester family results under HOAc, CF3CO2H, or mixed-acid conditions.",
                    "evidence_ids": ev(2),
                },
                {
                    "region": "lower middle, Scheme 3",
                    "finding": "Specific fully substituted allenoate 5 gives butenolide 6 at 80 °C in 57-67%; butenolide is the only observed reaction.",
                    "evidence_ids": ev(2),
                },
                {
                    "region": "bottom, start of 2,3-dienamide section",
                    "finding": "Cited 7a/7c/7d amide scope starts here and continues on page 3.",
                    "evidence_ids": ev(2),
                },
            ],
            "record_ids": ids(
                "ketone_3_alkyl_chlorination",
                "ketone_3_3_dimethyl_scope",
                "ketone_1_methyl_nai_hoac",
                "ketone_1_methyl_nai_tfa_hoac",
                "ketone_3_alkyl_3_4_pentadienone_scope",
                "scheme2_dienyl_acid_ester_general",
                "acid_methyl_ester_mx_hoac_70c",
                "acid_4_alkyl_nai_hoac_reflux",
                "acid_4_alkyl_libr_licl_hoac",
                "acid_2_methyl_mx_tfa",
                "ester_4_alkyl_mx_acid_media",
                "ester_2_alkyl_mx_hoac",
                "ester_2_alkyl_mx_tfa_hoac",
                "ester_2_alkyl_mx_tfa",
                "ester_trisubstituted_scope",
                "scheme3_fully_substituted_butenolide",
                "amide_7a_7c_7d_scope",
            ),
            "unresolved": [
                "Most outcomes are shared ranges or qualitative comparisons, not row-level measurements.",
                "The medium for the vague trisubstituted-allenoate sentence is not specified.",
            ],
        },
        {
            "page": 3,
            "state": "attempted",
            "regions": [
                {
                    "region": "top, Scheme 4 and dienamide continuation",
                    "finding": "Shared 75-99% amide family range and a qualitative 7b high-yield/low-stereoselectivity result.",
                    "evidence_ids": ev(3),
                },
                {
                    "region": "middle, nitrile prose and Scheme 5",
                    "finding": "Four cited nitrile substrate/medium families; prose and arrow disagree on the lower yield bound for 9a (78% vs 76%).",
                    "evidence_ids": ev(3),
                },
                {
                    "region": "bottom, sulfone prose and Scheme 6",
                    "finding": "Generic sulfone transformation with three explicitly distinct condition sets A-C and no printed yields.",
                    "evidence_ids": ev(3),
                },
            ],
            "record_ids": ids(
                "amide_7a_7c_7d_scope",
                "amide_7b_scope",
                "nitrile_9a_mx_hoac",
                "nitrile_9b_mx_hoac",
                "nitrile_9b_mx_tfa_hoac",
                "nitrile_9c_9d_scope",
                "sulfone_scheme6_conditions_a",
                "sulfone_scheme6_conditions_b",
                "sulfone_scheme6_conditions_c",
            ),
            "unresolved": [
                "The 9a yield discrepancy requires the underlying reference 6 to resolve.",
                "Scheme 6 contains no row-level yields, times, or substrate-to-condition mapping.",
            ],
        },
        {
            "page": 4,
            "state": "attempted",
            "regions": [
                {
                    "region": "upper half, sulfoxide prose and Scheme 7",
                    "finding": "Explicit MX/HOAc failure, water/AlCl3 optimization, AlCl3/AlBr3 scope range, and NaI/AlCl3 selectivity result.",
                    "evidence_ids": ev(4),
                },
                {
                    "region": "middle, phosphine-oxide prose and Scheme 8",
                    "finding": "Three cited phosphine-oxide reactivity families; prose and arrow disagree on the lower 15a/MX yield bound (58% vs 60%).",
                    "evidence_ids": ev(4),
                },
                {
                    "region": "lower half, conclusion and references 1-2",
                    "finding": "Conclusion and bibliography only; no additional experiment created.",
                    "evidence_ids": ev(4),
                },
            ],
            "record_ids": ids(
                "sulfoxide_mx_hoac_failure",
                "sulfoxide_alcl3_water_optimization",
                "sulfoxide_alx3_scope",
                "sulfoxide_iodination_selectivity",
                "phosphine_15a_mx_hoac",
                "phosphine_15a_aqueous_hx",
                "phosphine_15b_15c_mx_hoac",
            ),
            "unresolved": [
                "Per-substrate and per-halide values are absent from Schemes 7 and 8.",
                "The 15a yield discrepancy requires the underlying reference 8 to resolve.",
            ],
        },
        {
            "page": 5,
            "state": "attempted",
            "regions": [
                {
                    "region": "upper portion, continuation of references 2 and references 3-9",
                    "finding": "Bibliography only; no reaction arrow, table, footnote with experimental conditions, or current-paper experiment.",
                    "evidence_ids": ev(5),
                },
                {
                    "region": "remaining page",
                    "finding": "Blank publication page area and footer; no chemical content.",
                    "evidence_ids": [f"{DOC}:page5:image"],
                },
            ],
            "record_ids": [],
            "unresolved": [
                "References identify underlying studies but their full texts and SI are not part of this input and were not imported.",
            ],
        },
    ],
}


out_records = BASE / "raw_model" / "records_pages_0001_0005.json"
out_coverage = BASE / "coverage" / "pages_0001_0005.json"
out_records.parent.mkdir(parents=True, exist_ok=True)
out_coverage.parent.mkdir(parents=True, exist_ok=True)
out_records.write_text(json.dumps(R, ensure_ascii=False, indent=2) + "\n")
out_coverage.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"records": len(R), "records_file": str(out_records), "coverage_file": str(out_coverage)}, ensure_ascii=False))
