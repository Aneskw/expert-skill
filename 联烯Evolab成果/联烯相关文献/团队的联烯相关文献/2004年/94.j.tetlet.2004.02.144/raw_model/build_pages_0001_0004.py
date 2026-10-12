#!/usr/bin/env python3
"""Build raw evidence-linked records and coverage for PDF pages 1-4."""

import json
from pathlib import Path


DOC = "doc_a340dcac296e39f3"
OUT = Path(__file__).resolve().parent
BASE = OUT.parent


def ev(page):
    return [f"{DOC}:page{page}:text", f"{DOC}:page{page}:image"]


P1, P2, P3, P4 = (ev(i) for i in range(1, 5))


def fact(value, evidence=None):
    return {
        "value": value,
        "evidence_ids": list(evidence or []) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def field(name, value, evidence=None, targets=None):
    result = {"name": name, "fact": fact(value, evidence)}
    if targets:
        result["target_entity_ids"] = list(targets)
    return result


def participant(entity_id, role, label, evidence, *, name=None, smiles=None, amounts=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence) if name is not None else fact(None),
        "smiles": fact(smiles, evidence) if smiles is not None else fact(None),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": list(amounts or []),
    }


def record(suffix, kind, evidence, participants, steps, outcomes, notes, unresolved):
    return {
        "record_id": f"{DOC}:{suffix}",
        "document_id": DOC,
        "source_reaction_id": suffix,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": list(dict.fromkeys(evidence)),
        "participants": participants,
        "steps": steps,
        "outcomes": outcomes,
        "notes": [fact(note, evidence) for note in notes],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": list(unresolved),
        },
    }


def missing_experimental_conditions():
    return [
        field("time", None),
        field("temperature", None),
        field("atmosphere", None),
        field("workup", None),
        field("purification", None),
    ]


records = []

# Page 1: cited prior work. These are deliberately not current-paper experiments.
prior_common = [
    "This is prior literature summarized by the authors, not a new experiment reported in this paper.",
    "No yield, reaction time, loading, workup, or purification is given on this page.",
]
prior_unresolved = [
    "Original cited-paper procedures were not supplied.",
    "Generic R/R' structures and palladium-complex nuclearities are not encoded as verified structures.",
    "Yield and operational details are missing.",
    "Supporting-information association is unestablished.",
]

records.append(record(
    "p1_scheme1_path_A", "literature_example", P1,
    [
        participant("p1a_allene", "reactant", "allene series (R/R' = H/H, Me/Me, or H/Me)", P1),
        participant("p1a_pd", "reagent", "PdCl2(PhCN)2", P1, name="bis(benzonitrile)palladium(II) dichloride"),
        participant("p1a_benzene", "solvent", "benzene", P1, smiles="c1ccccc1"),
        participant("p1a_product", "product", "dinuclear monomeric 2-chloro-pi-allylic palladium complex A", P1),
    ],
    [{"step_id": "scheme1_A_arrow", "participant_ids": ["p1a_allene", "p1a_pd", "p1a_benzene", "p1a_product"],
      "conditions": [field("solvent", "benzene", P1)] + missing_experimental_conditions()}],
    [field("yield", None, targets=["p1a_product"]), field("yield_measurement_basis", None, targets=["p1a_product"])],
    prior_common + ["Scheme 1 shows one generic arrow for three R/R' substitution cases."], prior_unresolved,
))

records.append(record(
    "p1_scheme1_path_B_C", "literature_example", P1,
    [
        participant("p1bc_prop", "reactant", "propadiene (R = R' = H)", P1, smiles="C=C=C"),
        participant("p1bc_pd", "reagent", "PdCl2(PhCN)2", P1, name="bis(benzonitrile)palladium(II) dichloride"),
        participant("p1bc_product_b", "product", "vinylic palladium species B (Y = Cl)", P1),
        participant("p1bc_product_c", "product", "dimeric pi-allylic palladium complex C", P1),
    ],
    [{"step_id": "scheme1_B_C_arrow", "participant_ids": ["p1bc_prop", "p1bc_pd", "p1bc_product_b", "p1bc_product_c"],
      "conditions": [field("solvent", "benzene or PhCN", P1)] + missing_experimental_conditions()}],
    [field("yield", None, targets=["p1bc_product_b", "p1bc_product_c"]), field("yield_measurement_basis", None, targets=["p1bc_product_b", "p1bc_product_c"])],
    prior_common + ["The page depicts B and C in the cited propadiene chemistry; their experimental relationship is not quantified here."], prior_unresolved,
))

records.append(record(
    "p1_scheme1_path_D_E_F", "literature_example", P1,
    [
        participant("p1def_allene", "reactant", "bromo-substituted allene (R = H, R' = Br)", P1),
        participant("p1def_pd", "reagent", "PdCl2(PhCN)2", P1, name="bis(benzonitrile)palladium(II) dichloride"),
        participant("p1def_d", "product", "pi-allylic palladium complex D", P1),
        participant("p1def_e", "product", "dimeric complex E", P1),
        participant("p1def_f", "product", "trimeric pi-allylic palladium complex F", P1),
    ],
    [
        {"step_id": "scheme1_D_to_E", "participant_ids": ["p1def_allene", "p1def_pd", "p1def_d", "p1def_e"], "conditions": missing_experimental_conditions()},
        {"step_id": "scheme1_E_to_F", "participant_ids": ["p1def_e", "p1def_f"], "conditions": missing_experimental_conditions()},
    ],
    [field("yield", None, targets=["p1def_d", "p1def_e", "p1def_f"]), field("yield_measurement_basis", None, targets=["p1def_d", "p1def_e", "p1def_f"])],
    prior_common + ["Scheme 1 depicts successive D, E, and F complexes."], prior_unresolved,
))

records.append(record(
    "p1_prior_allene_carbonylation", "literature_example", P1,
    [
        participant("p1carb_allene", "reactant", "allene", P1),
        participant("p1carb_pdcl2", "catalyst", "PdCl2", P1, name="palladium(II) chloride"),
        participant("p1carb_cucl2", "unspecified_agent", "CuCl2", P1, name="copper(II) chloride"),
        participant("p1carb_meoh", "solvent", "MeOH", P1, name="methanol", smiles="CO"),
        participant("p1carb_product", "product", "2-ethoxymethylacrylates (as printed in the page text)", P1),
    ],
    [{"step_id": "prior_carbonylation", "participant_ids": ["p1carb_allene", "p1carb_pdcl2", "p1carb_cucl2", "p1carb_meoh", "p1carb_product"],
      "conditions": [field("solvent", "MeOH", P1)] + missing_experimental_conditions()}],
    [field("yield", None, targets=["p1carb_product"]), field("yield_measurement_basis", None, targets=["p1carb_product"])],
    prior_common + ["The product wording is preserved verbatim because the page gives no fully specified substrate/product structure."],
    prior_unresolved + ["The exact product identity and CuCl2 role require the cited original source."],
))


# Shared participants for the current paper.
SMILES_1A = "O=S(c1ccccc1)C=C=C(C)C"
SMILES_3A = "O=S(c1ccccc1)C=C(CC=C)C(C)=C"
SMILES_4A = "O=S(c1ccccc1)C=C(C=CCBr)C(C)=C"


def optimization_record(entry, catalyst_label, catalyst_name, base_label, ratio, yield_value, recovered_value, *, loading=None, extra_reagent=None):
    evidence = P2
    substrate = participant("substrate_1a", "reactant", "1a", evidence, name="3-methyl-1,2-butadienyl phenyl sulfoxide", smiles=SMILES_1A)
    allyl = participant("allyl_bromide_2", "reactant", "2", evidence, name="allyl bromide", smiles="C=CCBr")
    catalyst_amounts = [field("catalyst_loading", {"number": loading, "unit": "mol%"}, evidence)] if loading is not None else [field("catalyst_loading", None)]
    catalyst = participant("catalyst", "catalyst", catalyst_label, evidence, name=catalyst_name, amounts=catalyst_amounts)
    participants = [substrate, allyl, catalyst]
    if base_label:
        base_smiles = {
            "LiOAc": "[Li+].CC(=O)[O-]",
            "LiOAc·2H2O": "O.O.[Li+].CC(=O)[O-]",
            "NaHCO3": "[Na+].O=C([O-])O",
        }.get(base_label)
        participants.append(participant("base", "reagent", base_label, evidence, smiles=base_smiles, amounts=[field("amount", None)]))
    if extra_reagent:
        participants.append(participant("ligand", "reagent", extra_reagent, evidence, name="triphenylphosphine", smiles="P(c1ccccc1)(c1ccccc1)c1ccccc1", amounts=[field("amount", None)]))
    if ratio != "1:0":
        participants.append(participant("thf", "solvent", "THF", evidence, name="tetrahydrofuran", smiles="C1CCOC1", amounts=[field("volume", None)]))
    participants.append(participant("product_3a", "product", "3a", evidence, name="3-methyl-2-allyl-1(E),3(E)-butadienyl phenyl sulfoxide (paper wording)", smiles=SMILES_3A))
    conditions = [field("solvent_ratio_allyl_bromide_to_THF", ratio, evidence)] + missing_experimental_conditions()
    if not base_label:
        conditions.append(field("base", "none", evidence))
    outcomes = [
        field("yield", yield_value, evidence, ["product_3a"]),
        field("yield_measurement_basis", None, targets=["product_3a"]),
        field("recovered_starting_material_percentage", recovered_value, evidence if recovered_value is not None else None, ["substrate_1a"]),
    ]
    unresolved = [
        "Reaction time, temperature, atmosphere, workup, purification, and yield measurement basis are not reported in Table 1.",
        "Catalyst/base/solvent quantities are missing except for catalyst loadings explicitly stated in the prose.",
        "Candidate substrate/product SMILES encode interpreted connectivity only and are not structure-verified.",
        "Supporting-information association is unestablished.",
    ]
    return record(
        f"p2_table1_entry_{entry}", "optimization_entry", evidence, participants,
        [{"step_id": "coupling", "participant_ids": [p["entity_id"] for p in participants], "conditions": conditions}],
        outcomes,
        [f"Table 1 entry {entry}; the solvent column is explicitly headed '2/THF'."],
        unresolved,
    )


opt_rows = [
    (1, "RuCl3", "ruthenium(III) chloride", "LiOAc", "1:1", {"number": 16, "unit": "%"}, None, None, None),
    (2, "PdCl2", "palladium(II) chloride", "LiOAc", "1:1", {"number": 69, "unit": "%"}, None, 5, None),
    (3, "Pd(CH3CN)2Cl2", "bis(acetonitrile)palladium(II) dichloride", "LiOAc·2H2O", "1:1", {"number": 70, "unit": "%"}, None, 5, None),
    (4, "Pd(CH3CN)2Cl2", "bis(acetonitrile)palladium(II) dichloride", "LiOAc", "1:1", {"number": 77, "unit": "%"}, None, 5, None),
    (5, "Pd(CH3CN)2Cl2", "bis(acetonitrile)palladium(II) dichloride", "NaHCO3", "1:0", "trace", None, 5, None),
    (6, "Pd(CH3CN)2Cl2", "bis(acetonitrile)palladium(II) dichloride", None, "1:2", {"number": 9, "unit": "%"}, None, 5, None),
    (7, "Pd2(dba)3·CHCl3", "tris(dibenzylideneacetone)dipalladium chloroform adduct", "LiOAc", "1:2", "not detected", {"number": 73, "unit": "%"}, None, "PPh3"),
    (8, "Pd(PPh3)4", "tetrakis(triphenylphosphine)palladium(0)", "LiOAc", "1:2", "not detected", {"number": 67, "unit": "%"}, None, None),
]
for row in opt_rows:
    records.append(optimization_record(*row[:-2], loading=row[-2], extra_reagent=row[-1]))


scope_rows = [
    (1, "1b", "3b", "CH3", "C2H5", 8, 73, "92:8", "O=S(c1ccccc1)C=C=C(C)CC", "O=S(c1ccccc1)C=C(CC=C)C(CC)=C(C)", False),
    (2, "1c", "3c", "C2H5", "n-C3H7", 2, 58, "97:3", "O=S(c1ccccc1)C=C=C(CC)CCC", "O=S(c1ccccc1)C=C(CC=C)C(CCC)=C(CC)", False),
    (3, "1d", "3d", "n-C3H7", "n-C4H9", 2, 78, "93:7", "O=S(c1ccccc1)C=C=C(CCC)CCCC", "O=S(c1ccccc1)C=C(CC=C)C(CCCC)=C(CCC)", False),
    (4, "1e", "3e", "n-C4H9", "n-C5H11", 2, 60, "93:7", "O=S(c1ccccc1)C=C=C(CCCC)CCCCC", "O=S(c1ccccc1)C=C(CC=C)C(CCCCC)=C(CCCC)", False),
    (5, "1f", "3f", "(CH2)3 bridge", "(CH2)3 bridge", 9, 78, "93:7", "O=S(c1ccccc1)C=C=C1CCC1", "O=S(c1ccccc1)C=C(CC=C)C1=CCCC1", True),
    (6, "1g", "3g", "(CH2)4 bridge", "(CH2)4 bridge", 4.5, 63, "92:8", "O=S(c1ccccc1)C=C=C1CCCC1", "O=S(c1ccccc1)C=C(CC=C)C1=CCCCC1", True),
    (7, "1h", "3h", "H", "Ph", 39, 35, "95:5", "O=S(c1ccccc1)C=C=Cc1ccccc1", "O=S(c1ccccc1)C=C(CC=C)C(c1ccccc1)=C", False),
]


def scope_record(entry, substrate_label, product_label, r1, r2, time_h, yield_pct, ratio, substrate_smiles, product_smiles, cyclic):
    evidence = P2
    participants = [
        participant("substrate", "reactant", substrate_label, evidence, name=f"1,2-allenyl phenyl sulfoxide 1; R1={r1}, R2={r2}", smiles=substrate_smiles,
                    amounts=[field("reaction_scale", {"number": 0.5, "unit": "mmol"}, evidence)]),
        participant("allyl_bromide", "reactant", "allyl bromide", evidence, smiles="C=CCBr", amounts=[field("volume", {"number": 1.0, "unit": "mL"}, evidence)]),
        participant("lioac", "reagent", "LiOAc", evidence, smiles="[Li+].CC(=O)[O-]", amounts=[field("equivalents", {"number": 2, "unit": "equiv"}, evidence)]),
        participant("catalyst", "catalyst", "PdCl2(CH3CN)2", evidence, name="bis(acetonitrile)palladium(II) dichloride",
                    amounts=[field("catalyst_loading", {"number": 5, "unit": "mol%"}, evidence)]),
        participant("thf", "solvent", "dry THF", evidence, name="tetrahydrofuran", smiles="C1CCOC1", amounts=[field("volume", {"number": 1.0, "unit": "mL"}, evidence)]),
        participant("product", "product", product_label, evidence, name=f"E,E-3; R1={r1}, R2={r2}", smiles=product_smiles),
    ]
    conditions = [
        field("time", {"number": time_h, "unit": "h"}, evidence),
        field("temperature", "reflux", evidence),
        field("atmosphere", "N2", evidence),
        field("solvent", "dry THF", evidence),
        field("workup", None),
        field("purification", None),
    ]
    outcomes = [
        field("yield", {"number": yield_pct, "unit": "%"}, evidence, ["product"]),
        field("yield_measurement_basis", None, targets=["product"]),
        field("1,2_C=C_E/Z_ratio", ratio, evidence, ["product"]),
        field("1,2_C=C_selectivity_measurement_basis", "1H NMR analysis of the olefinic protons in the crude product", evidence, ["product"]),
    ]
    if not cyclic:
        outcomes.append(field("3,4_C=C_E_selectivity", {"number": 100, "unit": "%"}, evidence, ["product"]))
    unresolved = [
        "Yield measurement basis, workup, and purification are not reported in Table 2.",
        "Candidate substrate/product SMILES encode interpreted connectivity and omit source-verified stereochemistry.",
        "Supporting-information association is unestablished.",
    ]
    if cyclic:
        unresolved.append("The prose gives a general 100% E statement for the 3,4 double bond, but its row-specific applicability to the bridged cyclic entry is unresolved; it was not assigned as a row outcome.")
    return record(
        f"p2_table2_entry_{entry}", "substrate_scope_entry", evidence, participants,
        [{"step_id": "coupling", "participant_ids": [p["entity_id"] for p in participants], "conditions": conditions}],
        outcomes,
        [f"Table 2 entry {entry}; R1={r1}, R2={r2}."],
        unresolved,
    )


for row in scope_rows:
    records.append(scope_record(*row))


# Scheme 2 is a distinct partial experiment with product-specific main/minor yields.
scheme2_evidence = P2 + P3
scheme2_participants = [
    participant("substrate_1a", "reactant", "1a", P3, name="3-methyl-1,2-butadienyl phenyl sulfoxide", smiles=SMILES_1A, amounts=[field("reaction_scale", None)]),
    participant("allyl_bromide", "reactant", "allyl bromide", P3, smiles="C=CCBr", amounts=[field("amount", None)]),
    participant("catalyst", "catalyst", "PdCl2(CH3CN)2", P3, name="bis(acetonitrile)palladium(II) dichloride", amounts=[field("catalyst_loading", None)]),
    participant("lioac", "reagent", "LiOAc", P3, smiles="[Li+].CC(=O)[O-]", amounts=[field("amount", None)]),
    participant("product_3a", "product", "E-3a", P3, name="major 2-allyl dienyl phenyl sulfoxide", smiles=SMILES_3A),
    participant("product_4a", "product", "4a", P3, name="2-(3'-bromo-1'-propenyl)-3-methylbuta-1,3-dienyl phenyl sulfoxide", smiles=SMILES_4A),
]
records.append(record(
    "p3_scheme2_1a_to_3a_4a", "reported_experiment", scheme2_evidence, scheme2_participants,
    [{"step_id": "coupling", "participant_ids": [p["entity_id"] for p in scheme2_participants], "conditions": [
        field("temperature", "reflux", P3), field("time", None), field("solvent", None), field("atmosphere", None), field("workup", None), field("purification", None)
    ]}],
    [
        field("yield", {"number": 72, "unit": "%"}, [P2[0], P3[1]], ["product_3a"]),
        field("yield", {"number": 4, "unit": "%"}, [P2[0], P3[1]], ["product_4a"]),
        field("yield_measurement_basis", None, targets=["product_3a", "product_4a"]),
    ],
    ["Scheme 2 reports the major product E-3a and minor bromo-propenyl product 4a from the same depicted reaction."],
    [
        "Reaction time, solvent, atmosphere, scale, reagent/catalyst quantities, workup, purification, and yield measurement basis are not stated for Scheme 2.",
        "The source does not explicitly identify Scheme 2 as the identical physical run behind any Table 1 entry, so it remains separate.",
        "Candidate structures are connectivity interpretations and remain unverified.",
        "Supporting-information association is unestablished.",
    ],
))


# Scheme 3: one proposed mechanism record with arrow-level steps, never a reported experiment.
mechanism_evidence = P2 + P3
mechanism_participants = [
    participant("generic_1", "reactant", "generic 1,2-allenyl phenyl sulfoxide 1 (R1/R2)", P3),
    participant("pdii", "catalyst", "Pd(II)LnX2", P3),
    participant("lioac", "reagent", "LiOAc", P3, smiles="[Li+].CC(=O)[O-]"),
    participant("allyl_bromide", "reactant", "allyl bromide", P3, smiles="C=CCBr"),
    participant("e3", "product", "E-3", P3),
    participant("z3", "product", "minor Z-3", P3),
    participant("four_a", "product", "4a (for R2 = Me, R1 = H)", P3, smiles=SMILES_4A),
]
records.append(record(
    "p3_scheme3_proposed_mechanism", "mechanism", mechanism_evidence, mechanism_participants,
    [
        {"step_id": "halopalladation", "participant_ids": ["generic_1", "pdii"], "conditions": [field("operation", "proposed regioselective halopalladation to Z-7; E-7/6-type alternatives are depicted", P3)]},
        {"step_id": "lioac_elimination", "participant_ids": ["generic_1", "lioac"], "conditions": [field("operation", "proposed LiOAc-mediated elimination of Z-7 to Z-5", P3)]},
        {"step_id": "allyl_carbopalladation", "participant_ids": ["allyl_bromide", "e3"], "conditions": [field("operation", "proposed carbopalladation to E-8 followed by beta-debromopalladation to E-3", P3)]},
        {"step_id": "minor_z_path", "participant_ids": ["z3"], "conditions": [field("operation", "minor Z-3 path is depicted from E-5", P3)]},
        {"step_id": "minor_4a_path", "participant_ids": ["allyl_bromide", "four_a"], "conditions": [field("operation", "proposed carbopalladation/beta-H elimination route to 4a for R2 = Me and R1 = H", P3)]},
    ],
    [],
    ["Scheme 3 is explicitly introduced as a rationale/proposed mechanism; intermediates 6, E/Z-7, E/Z-5, and E-8 are not isolated experimental products on these pages."],
    [
        "Generic R1/R2 structures and palladium-ligand identities are not fully specified.",
        "The proposed elementary steps are mechanistic interpretation, not independently verified experimental stages.",
        "Supporting-information association is unestablished.",
    ],
))


raw_path = OUT / "extracted_records_pages_0001_0004.json"
raw_path.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")


opt_ids = [f"{DOC}:p2_table1_entry_{i}" for i in range(1, 9)]
scope_ids = [f"{DOC}:p2_table2_entry_{i}" for i in range(1, 8)]
scheme2_id = f"{DOC}:p3_scheme2_1a_to_3a_4a"
mechanism_id = f"{DOC}:p3_scheme3_proposed_mechanism"
coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1,
            "state": "attempted",
            "regions": [
                {"region": "title, abstract, and introductory current-work statement", "finding": "Article overview only; no row-level current-paper experiment or operational procedure is reported here.", "evidence_ids": [P1[1]]},
                {"region": "Scheme 1, left/lower half", "finding": "Three prior-literature palladium/allene pathways (A; B/C; D/E/F), classified as literature examples rather than this paper's experiments.", "evidence_ids": [P1[1]]},
                {"region": "right-column prior carbonylation paragraph", "finding": "One cited prior allene carbonylation example; product wording and missing details preserved.", "evidence_ids": [P1[1], P1[0]]},
            ],
            "record_ids": [
                f"{DOC}:p1_scheme1_path_A", f"{DOC}:p1_scheme1_path_B_C",
                f"{DOC}:p1_scheme1_path_D_E_F", f"{DOC}:p1_prior_allene_carbonylation",
            ],
            "unresolved": ["Original cited-paper procedures and yields were not supplied; generic complex structures remain unverified."],
        },
        {
            "page": 2,
            "state": "attempted",
            "regions": [
                {"region": "Table 1 and its reaction drawing", "finding": "Eight independent optimization entries, including trace product, no-product Pd(0) results, and recovered starting material.", "evidence_ids": [P2[1], P2[0]]},
                {"region": "Table 2, reaction drawing, and footnotes a-b", "finding": "Seven independent substrate-scope entries with explicit time, yield, E/Z ratio, shared scale/loadings/volumes/N2/reflux conditions, and crude-1H-NMR selectivity basis.", "evidence_ids": [P2[1], P2[0]]},
                {"region": "upper-right Scheme 2 discussion", "finding": "Cross-page evidence for one 1a coupling yielding 3a (72%) and minor 4a (4%); merged with page 3 Scheme 2 rather than duplicated.", "evidence_ids": [P2[1], P2[0], P3[1]]},
                {"region": "lower-right mechanistic rationale text", "finding": "Proposed mechanism context only; linked to page 3 Scheme 3 mechanism record.", "evidence_ids": [P2[1], P2[0], P3[1]]},
            ],
            "record_ids": opt_ids + scope_ids + [scheme2_id, mechanism_id],
            "unresolved": ["Table 1 omits time, temperature, most quantities, atmosphere, and yield basis; Table 2 omits yield basis/workup/purification."],
        },
        {
            "page": 3,
            "state": "attempted",
            "regions": [
                {"region": "Scheme 2, top", "finding": "Current-paper partial experiment: 1a plus allyl bromide under PdCl2(CH3CN)2/LiOAc at reflux gives E-3a (72%) and 4a (4%).", "evidence_ids": [P3[1], P3[0]]},
                {"region": "Scheme 3, center", "finding": "Proposed mechanistic network with main/minor pathways; classified as mechanism, not as isolated experiments.", "evidence_ids": [P3[1], P3[0]]},
                {"region": "conclusion and acknowledgements, lower columns", "finding": "Summary and funding text; no additional row-level experiment or procedure.", "evidence_ids": [P3[1]]},
            ],
            "record_ids": [scheme2_id, mechanism_id],
            "unresolved": ["Scheme 2 lacks time, solvent, scale, quantities, workup, purification, and yield basis; mechanistic intermediates are proposed only."],
        },
        {
            "page": 4,
            "state": "attempted",
            "regions": [
                {"region": "full page, references 2-12", "finding": "References only; no reaction arrow, table row, current-paper procedure, or new experimental outcome.", "evidence_ids": [P4[1], P4[0]]},
            ],
            "record_ids": [],
            "unresolved": ["Referenced original articles were not supplied and were not treated as covered source pages."],
        },
    ],
}
coverage_dir = BASE / "coverage"
coverage_dir.mkdir(parents=True, exist_ok=True)
(coverage_dir / "pages_0001_0004.json").write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"records": len(records), "raw": str(raw_path), "coverage": str(coverage_dir / 'pages_0001_0004.json')}, ensure_ascii=False))
