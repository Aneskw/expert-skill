#!/usr/bin/env python3
"""Build evidence-linked records for jo802755k, original PDF pages 1-4."""

from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
DOC = "doc_c83842d543160a4f"


def ev(page):
    return [f"{DOC}:page{page}:image", f"{DOC}:page{page}:text"]


P1, P2, P3, P4 = (ev(i) for i in range(1, 5))


def fact(value, evidence):
    return {
        "value": value,
        "evidence_ids": list(evidence) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def field(name, value, evidence, targets=None):
    item = {"name": name, "fact": fact(value, evidence)}
    if targets:
        item["target_entity_ids"] = list(targets)
    return item


def participant(entity_id, role, label, evidence, smiles=None, name=None, amounts=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence) if name is not None else fact(None, []),
        "smiles": fact(smiles, evidence) if smiles is not None else fact(None, []),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": amounts or [],
    }


def record(suffix, kind, evidence, participants, steps, outcomes, notes=None, unresolved=None):
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
        "notes": [fact(x, evidence) for x in (notes or [])],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved or [
                "Machine-extracted connectivity and stereochemistry require chemistry review."
            ],
        },
    }


def step(step_id, participant_ids, conditions):
    return {
        "step_id": step_id,
        "participant_ids": participant_ids,
        "conditions": conditions,
    }


def q(number, unit, **extra):
    return {"number": number, "unit": unit, **extra}


SMILES = {
    "1a": "O=S(c1ccccc1)C=C=C(C)",
    "2a": "O=S(=O)(c1ccccc1)C=C=C(C)",
    "Z-3a": "CC(=O)OC(C)C=CS(=O)(=O)c1ccccc1",
    "1b": "O=S(c1ccccc1)C=C=C",
    "2b": "O=S(=O)(c1ccccc1)C=C=C",
    "Z-3b": "CC(=O)OCC=CS(=O)(=O)c1ccccc1",
    "Z-4b": "CC(=O)OCC=CS(=O)c1ccccc1",
    "1c": "O=S(c1ccccc1)C=C=C(CC)",
    "Z-3c": "CCC(OC(C)=O)C=CS(=O)(=O)c1ccccc1",
    "1d": "O=S(c1ccccc1)C=C=C(CCCC)",
    "Z-3d": "CCCCC(OC(C)=O)C=CS(=O)(=O)c1ccccc1",
    "1e": "O=S(c1ccccc1)C=C=C(CCCCC)",
    "Z-3e": "CCCCCC(OC(C)=O)C=CS(=O)(=O)c1ccccc1",
    "1f": "O=S(c1ccccc1)C=C=C(CCCCCC)",
    "Z-3f": "CCCCCCC(OC(C)=O)C=CS(=O)(=O)c1ccccc1",
    "1g": "O=S(c1ccccc1)C=C=C(CCCCCCC)",
    "Z-3g": "CCCCCCCC(OC(C)=O)C=CS(=O)(=O)c1ccccc1",
    "1h": "O=S(c1ccccc1)C(CC)=C=C(C)",
    "Z-3h": "O=S(=O)(c1ccccc1)C(CC)=CC(C)OC(C)=O",
    "1i": "O=S(c1ccccc1)C(CCCC)=C=C",
    "Z-3i": "O=S(=O)(c1ccccc1)C(CCCC)=CCOC(C)=O",
    "1j": "O=S(c1ccccc1)C(CC=C)=C=C",
    "Z-3j": "O=S(=O)(c1ccccc1)C(CC=C)=CCOC(C)=O",
    "1k": "O=S(c1ccccc1)C(CCCC)=C=C(Cc1ccccc1)",
    "Z-3k": "O=S(=O)(c1ccccc1)C(CCCC)=CC(Cc1ccccc1)OC(C)=O",
    "1l": "O=S(c1ccc(Br)cc1)C=C=C(C)",
    "Z-3l": "CC(=O)OC(C)C=CS(=O)(=O)c1ccc(Br)cc1",
    "Z-4l": "CC(O)C=CS(=O)(=O)c1ccc(Br)cc1",
    "Z-5l": "CC(OC(=O)c1ccc([N+](=O)[O-])cc1)C=CS(=O)(=O)c1ccc(Br)cc1",
    "1m": "O=S(c1ccc(Br)cc1)C(CC)=C=C(C)",
    "Z-3m": "O=S(=O)(c1ccc(Br)cc1)C(CC)=CC(C)OC(C)=O",
}


records = []

# Page 1 graphical summary: a scope-level representation, not a batch.
generic_ev = P1
records.append(record(
    "graphical_abstract_general_scope", "general_scheme", generic_ev,
    [
        participant("generic_allenyl_sulfoxide", "reactant", "generic 1,2-allenylic sulfoxide", generic_ev),
        participant("hydrogen_peroxide", "reagent", "H2O2", generic_ev, "OO"),
        participant("acetic_acid", "solvent", "HOAc", generic_ev, "CC(=O)O"),
        participant("generic_allylic_acetate", "product", "generic 1-sulfonyl-1-alken-3-yl acetate", generic_ev),
    ],
    [step("scope_transformation", ["generic_allenyl_sulfoxide", "hydrogen_peroxide", "acetic_acid", "generic_allylic_acetate"], [])],
    [field("scope_yield_range", {"minimum": 39, "maximum": 90, "unit": "%", "raw_text": "39-90% yield"}, generic_ev, ["generic_allylic_acetate"])],
    notes=["Graphical abstract reports 13 examples and a five-membered cyclic intermediate; it is not an individual batch."],
    unresolved=["Generic R groups and individual batch identities are unresolved in the graphical summary."]
))

# Equation 1 is explicitly described as previous work.
eq1_ev = P1
records.append(record(
    "eq1_prior_oxidation_1a", "literature_example", eq1_ev,
    [
        participant("1a", "reactant", "1a", eq1_ev, SMILES["1a"]),
        participant("h2o2", "reagent", "H2O2", eq1_ev, "OO", amounts=[field("equivalents", q(2.8, "equiv"), eq1_ev)]),
        participant("hoac", "solvent", "HOAc", eq1_ev, "CC(=O)O"),
        participant("2a", "product", "2a", eq1_ev, SMILES["2a"]),
        participant("z3a", "product", "Z-3a", eq1_ev, SMILES["Z-3a"]),
    ],
    [step("oxidation", ["1a", "h2o2", "hoac", "2a", "z3a"], [
        field("temperature", q(100, "°C"), eq1_ev),
        field("time", q(15, "min"), eq1_ev),
    ])],
    [
        field("reported_yield_2a", q(50, "%"), eq1_ev, ["2a"]),
        field("isolated_yield_Z_3a", q(3, "%"), eq1_ev, ["z3a"]),
    ],
    notes=["The paper identifies equation 1 as a result from the group's previous work (reference 6c)."],
    unresolved=["The 2a yield measurement basis is not explicitly stated in the covered source."]
))


def table1_record(entry, concentration, oxidant_label, oxidant_smiles, oxidant_equiv, y2a, yz3a):
    evidence = P2 + (P3 if entry == 8 else [])
    suffix = "table1_entry8_table2_entry1_z3a" if entry == 8 else f"table1_entry{entry}"
    parts = [participant("1a", "reactant", "1a", evidence, SMILES["1a"], amounts=[field("amount", q(0.5, "mmol"), evidence)])]
    if entry == 1:
        parts.append(participant("water", "solvent", "water", evidence, "O"))
    else:
        hoac_amounts = []
        if entry == 8:
            hoac_amounts = [field("first_portion_volume", q(3.0, "mL"), P3), field("second_portion_volume", q(3.0, "mL"), P3)]
        parts.append(participant("hoac", "solvent", "HOAc", evidence, "CC(=O)O", amounts=hoac_amounts))
    oxidant_amounts = []
    if oxidant_equiv is not None:
        oxidant_amounts.append(field("equivalents", q(oxidant_equiv, "equiv"), P2))
    if entry == 8:
        oxidant_amounts += [
            field("solution_concentration", q(30, "%"), P3),
            field("volume", q(57, "uL"), P3),
            field("mass", q(0.063, "g"), P3),
            field("amount", q(0.56, "mmol"), P3),
        ]
        parts[0]["amounts"].append(field("mass", q(88.7, "mg"), P3))
    parts.append(participant("oxidant", "reagent", oxidant_label, evidence, oxidant_smiles, amounts=oxidant_amounts))
    parts += [
        participant("2a", "product", "2a", evidence, SMILES["2a"]),
        participant("z3a", "product", "Z-3a", evidence, SMILES["Z-3a"]),
    ]
    conditions = [
        field("substrate_concentration", q(concentration, "M"), P2),
        field("temperature", q(100, "°C"), P2),
        field("time", q(17, "h"), P2),
    ]
    outcomes = [
        field("NMR_yield_2a", q(y2a, "%"), P2, ["2a"]),
        field("NMR_yield_Z_3a", q(yz3a, "%"), P2, ["z3a"]),
        field("yield_measurement_basis", "NMR yield", P2),
    ]
    notes = []
    unresolved = ["Atmosphere is not stated; structures and Z assignment require chemistry review."]
    if entry == 1:
        notes.append("Table 1 footnote b states that the reaction was carried out in water.")
        unresolved.append("The water-run operational volumes and workup are not stated.")
    elif entry in (10, 11):
        unresolved.append("The oxidant amount is not stated for this footnote-substituted oxidant.")
    if entry == 8:
        conditions += [
            field("addition_time", q(20, "min"), P3),
            field("operation", "H2O2 solution in HOAc was added dropwise to 1a in HOAc at 100 °C; reaction monitored by TLC.", P3),
            field("workup", "Quenched with 10 mL saturated aqueous NaHCO3; extracted with diethyl ether (15 mL × 3), washed with saturated aqueous NaHCO3, dried over anhydrous Na2SO4, filtered and evaporated.", P3),
            field("purification", "Silica-gel column chromatography, petroleum ether/ethyl acetate = 5:1.", P3),
        ]
        parts[4]["amounts"] = [field("product_mass", q(66.9, "mg"), P3)]
        outcomes += [
            field("isolated_yield_Z_3a", q(53, "%"), evidence, ["z3a"]),
            field("physical_form", "solid", P3, ["z3a"]),
            field("melting_point", "88-89 °C (n-hexane/diethyl ether)", P3, ["z3a"]),
        ]
        notes.append("This record merges Table 1 entry 8, Table 2 entry 1, and the page-3 typical Z-3a procedure as the same experiment.")
        unresolved = ["Atmosphere is not stated; candidate connectivity and Z geometry require chemistry review."]
    return record(suffix, "optimization_entry", evidence, parts,
                  [step("oxidative_hydroacetoxylation", [p["entity_id"] for p in parts], conditions)],
                  outcomes, notes=notes, unresolved=unresolved)


table1 = [
    (1, 0.25, "H2O2", "OO", 11.0, 0, 0),
    (2, 0.25, "H2O2", "OO", 4.4, 27, 37),
    (3, 0.25, "H2O2", "OO", 1.7, 13, 38),
    (4, 0.25, "H2O2", "OO", 1.3, 4, 42),
    (5, 0.25, "H2O2", "OO", 0.9, 0, 42),
    (6, 0.5, "H2O2", "OO", 1.1, 0, 30),
    (7, 0.25, "H2O2", "OO", 1.1, 0, 45),
    (8, 0.083, "H2O2", "OO", 1.1, 0, 56),
    (9, 0.05, "H2O2", "OO", 1.1, 0, 53),
    (10, 0.083, "mCPBA", "O=C(OO)c1cccc(Cl)c1", None, 4, 50),
    (11, 0.083, "tBuOOH", "CC(C)(C)OO", None, 0, 41),
]
records += [table1_record(*row) for row in table1]


scope_rows = [
    (2, "1b", "Z-3b", "Ph", "H", "H", 50),
    (3, "1c", "Z-3c", "Ph", "H", "C2H5", 55),
    (4, "1d", "Z-3d", "Ph", "H", "n-C4H9", 54),
    (5, "1e", "Z-3e", "Ph", "H", "n-C5H11", 42),
    (6, "1f", "Z-3f", "Ph", "H", "n-C6H13", 40),
    (7, "1g", "Z-3g", "Ph", "H", "n-C7H15", 45),
    (8, "1h", "Z-3h", "Ph", "C2H5", "CH3", 80),
    (9, "1i", "Z-3i", "Ph", "n-C4H9", "H", 67),
    (10, "1j", "Z-3j", "Ph", "allyl", "H", 62),
    (11, "1k", "Z-3k", "Ph", "n-C4H9", "Bn", 73),
    (12, "1l", "Z-3l", "p-BrC6H4", "H", "CH3", 46),
    (13, "1m", "Z-3m", "p-BrC6H4", "C2H5", "CH3", 83),
]

for entry, substrate, product, r1, r2, r3, yield_value in scope_rows:
    evidence = P2
    parts = [
        participant(substrate, "reactant", substrate, evidence, SMILES.get(substrate), amounts=[field("amount", q(0.5, "mmol"), evidence)]),
        participant("h2o2", "reagent", "H2O2", evidence, "OO", amounts=[field("equivalents", q(1.1, "equiv"), evidence)]),
        participant("hoac", "solvent", "HOAc", evidence, "CC(=O)O", amounts=[field("first_portion_volume", q(3.0, "mL"), evidence), field("second_portion_volume", q(3.0, "mL"), evidence)]),
        participant(product.lower().replace("-", "_"), "product", product, evidence, SMILES.get(product)),
    ]
    prod_id = parts[-1]["entity_id"]
    records.append(record(
        f"table2_entry{entry}", "substrate_scope_entry", evidence, parts,
        [step("oxidative_hydroacetoxylation", [p["entity_id"] for p in parts], [
            field("substrate_concentration", q(0.083, "M"), evidence),
            field("temperature", q(100, "°C"), evidence),
            field("time", q(17, "h"), evidence),
            field("operation", "Substrate in 3.0 mL HOAc was heated to 100 °C; H2O2 in 3.0 mL HOAc was added dropwise with stirring.", evidence),
        ])],
        [
            field("isolated_yield", q(yield_value, "%"), evidence, [prod_id]),
            field("yield_measurement_basis", "isolated yield", evidence),
        ],
        notes=[f"Table 2 substituents: R1={r1}, R2={r2}, R3={r3}."],
        unresolved=["Atmosphere, workup and purification are not stated for this table row; candidate connectivity and Z geometry require chemistry review."]
    ))


# Two prose-only failed substrates.
for suffix, label in [
    ("failed_3phenyl_1_2_butadienyl_sulfoxide", "3-phenyl-1,2-butadienyl phenyl sulfoxide"),
    ("failed_3ethyl_1_2_pentadienyl_sulfoxide", "3-ethyl-1,2-pentadienyl phenyl sulfoxide"),
]:
    evidence = P2
    records.append(record(
        suffix, "substrate_scope_entry", evidence,
        [
            participant("substrate", "reactant", label, evidence),
            participant("expected_product", "product", "expected oxidative hydroacetoxylation product", evidence),
        ],
        [step("attempted_hydroacetoxylation", ["substrate", "expected_product"], [])],
        [field("expected_product_result", "failed to afford the expected product", evidence, ["expected_product"])],
        unresolved=["Exact substrate drawing, scale, conditions, recovery and side products are not stated in the covered source."]
    ))


# Mechanistic probe experiments on page 2.
records.append(record(
    "eq2_doac_deuteration_1m", "reported_experiment", P2,
    [
        participant("1m", "reactant", "1m", P2, SMILES["1m"]),
        participant("h2o2", "reagent", "H2O2 (30%)", P2, "OO", amounts=[field("equivalents", q(1.1, "equiv"), P2), field("solution_concentration", q(30, "%"), P2)]),
        participant("doac", "solvent", "DOAc", P2),
        participant("d3m", "product", "d-3m", P2),
    ],
    [step("deuterium_labeling_hydroacetoxylation", ["1m", "h2o2", "doac", "d3m"], [field("temperature", q(100, "°C"), P2), field("time", q(17, "h"), P2)])],
    [
        field("reported_yield_d_3m", q(79, "%"), P2, ["d3m"]),
        field("deuterium_incorporation", q(95, "%"), P2, ["d3m"]),
        field("deuterium_location", "olefinic position derived from the center carbon of the starting allene moiety", P2, ["d3m"]),
    ],
    unresolved=["Yield and deuterium-incorporation measurement bases, scale, atmosphere, workup and purification are not stated; isotopic connectivity remains unverified."]
))

records.append(record(
    "eq3_hydroacetoxylation_1b_without_h2o2", "reported_experiment", P2,
    [
        participant("1b", "reactant", "1b", P2, SMILES["1b"]),
        participant("hoac", "solvent", "HOAc", P2, "CC(=O)O"),
        participant("z4b", "product", "Z-4b", P2, SMILES["Z-4b"]),
    ],
    [step("hydroacetoxylation_without_oxidant", ["1b", "hoac", "z4b"], [field("temperature", q(95, "°C"), P2), field("time", q(15, "h"), P2)])],
    [field("isolated_yield_Z_4b", q(41, "%"), P2, ["z4b"]), field("yield_measurement_basis", "isolated yield", P2)],
    notes=["The prose explicitly states that H2O2 was absent."],
    unresolved=["Scale, atmosphere, workup and purification are not stated; candidate connectivity and Z geometry require chemistry review."]
))

records.append(record(
    "eq4_allenyl_sulfone_2b_no_reaction", "reported_experiment", P2,
    [
        participant("2b", "reactant", "2b", P2, SMILES["2b"]),
        participant("h2o2", "reagent", "H2O2", P2, "OO"),
        participant("hoac", "solvent", "HOAc", P2, "CC(=O)O"),
        participant("z3b_expected", "product", "Z-3b (expected)", P2, SMILES["Z-3b"]),
    ],
    [step("attempted_hydroacetoxylation_of_sulfone", ["2b", "h2o2", "hoac", "z3b_expected"], [field("temperature", q(100, "°C"), P2)])],
    [
        field("expected_product_result", "no reaction observed", P2, ["z3b_expected"]),
        field("recovered_starting_material_yield", q(46, "%"), P2, ["2b"]),
    ],
    unresolved=["Reaction duration, scale, H2O2 loading, atmosphere, workup, purification and recovery basis are not stated."]
))


# Scheme 1: four successive chemical operations. Step b is the optically active experiment discussed across pages 2-3.
records.append(record(
    "scheme1_step_a_prepare_r_1l", "reported_experiment", P3,
    [
        participant("r_propargyl_alcohol", "reactant", "(R)-3-butyn-2-ol (98% ee)", P3, "CC(O)C#C"),
        participant("pbr_scl", "reagent", "p-BrC6H4SCl", P3, "ClSc1ccc(Br)cc1"),
        participant("et3n", "reagent", "Et3N", P3, "CCN(CC)CC"),
        participant("ch3i", "reagent", "CH3I", P3, "CI"),
        participant("ch2cl2", "solvent", "CH2Cl2", P3, "ClCCl"),
        participant("r1l", "product", "(R)-1l", P3, SMILES["1l"]),
    ],
    [step("prepare_r_1l", ["r_propargyl_alcohol", "pbr_scl", "et3n", "ch3i", "ch2cl2", "r1l"], [
        field("initial_temperature", q(-78, "°C"), P3),
        field("initial_time", q(10, "min"), P3),
        field("operation", "Et3N/CH2Cl2 at -78 °C for 10 min, then CH3I and warming to room temperature.", P3),
    ])],
    [
        field("isolated_yield_R_1l", q(65, "%"), P3, ["r1l"]),
        field("product_ee", q(98.2, "%"), P3, ["r1l"]),
        field("ee_reference", "axial chirality", P3, ["r1l"]),
    ],
    unresolved=["Scale, room-temperature duration, atmosphere, workup, purification and ee measurement method are not stated; absolute configuration remains unverified."]
))

records.append(record(
    "scheme1_step_b_r_1l_to_s_z_3l", "reported_experiment", P2 + P3,
    [
        participant("r1l", "reactant", "(R)-1l", P2 + P3, SMILES["1l"]),
        participant("h2o2", "reagent", "H2O2", P2 + P3, "OO", amounts=[field("equivalents", q(1.1, "equiv"), P3)]),
        participant("hoac", "solvent", "HOAc", P2 + P3, "CC(=O)O"),
        participant("s_z3l", "product", "(S)-(Z)-3l", P2 + P3, SMILES["Z-3l"]),
    ],
    [step("enantiospecific_oxidative_hydroacetoxylation", ["r1l", "h2o2", "hoac", "s_z3l"], [field("temperature", q(95, "°C"), P3), field("time", q(17, "h"), P3)])],
    [
        field("isolated_yield_S_Z_3l", q(41, "%"), P2 + P3, ["s_z3l"]),
        field("product_ee", q(94.8, "%"), P3, ["s_z3l"]),
    ],
    notes=["This optically active experiment is distinct from racemic Table 2 entry 12 (46% yield)."],
    unresolved=["Scale, atmosphere, workup, purification and ee measurement method are not stated; absolute configuration and Z geometry remain unverified."]
))

records.append(record(
    "scheme1_step_c_hydrolysis_s_z_3l", "reported_experiment", P3,
    [
        participant("s_z3l", "reactant", "(S)-(Z)-3l", P3, SMILES["Z-3l"]),
        participant("k2co3", "reagent", "K2CO3", P3, "[K+].[K+].[O-]C([O-])=O"),
        participant("meoh", "solvent", "MeOH", P3, "CO"),
        participant("s_z4l", "product", "(S)-(Z)-4l", P3, SMILES["Z-4l"]),
    ],
    [step("acetate_hydrolysis", ["s_z3l", "k2co3", "meoh", "s_z4l"], [field("temperature", q(-30, "°C"), P3), field("time", q(4, "h"), P3)])],
    [field("isolated_yield_S_Z_4l", q(61, "%"), P3, ["s_z4l"]), field("product_ee", q(93.3, "%"), P3, ["s_z4l"])],
    unresolved=["Scale, reagent loading, atmosphere, workup, purification and ee measurement method are not stated; stereochemistry remains unverified."]
))

records.append(record(
    "scheme1_step_d_pnitrobenzoylation_s_z_4l", "reported_experiment", P3,
    [
        participant("s_z4l", "reactant", "(S)-(Z)-4l", P3, SMILES["Z-4l"]),
        participant("et3n", "reagent", "Et3N", P3, "CCN(CC)CC"),
        participant("dmap", "catalyst", "DMAP", P3, "CN(C)c1ccncc1"),
        participant("pnbcl", "reagent", "4-nitrobenzoyl chloride", P3, "O=C(Cl)c1ccc([N+](=O)[O-])cc1"),
        participant("ch2cl2", "solvent", "CH2Cl2", P3, "ClCCl"),
        participant("s_z5l", "product", "(S)-(Z)-5l", P3, SMILES["Z-5l"]),
    ],
    [step("p_nitrobenzoylation", ["s_z4l", "et3n", "dmap", "pnbcl", "ch2cl2", "s_z5l"], [field("temperature", "r.t.", P3), field("time", q(12, "h"), P3)])],
    [field("isolated_yield_S_Z_5l", q(82, "%"), P3, ["s_z5l"]), field("product_ee", q(92.4, "%"), P3, ["s_z5l"])],
    notes=["The paper uses the X-ray structure of (S)-(Z)-5l to establish absolute configuration after derivatization."],
    unresolved=["Scale, reagent loadings, atmosphere, workup, purification and ee measurement method are not stated; stereochemistry remains unverified."]
))


records.append(record(
    "scheme2_proposed_five_membered_mechanism", "mechanism", P3,
    [
        participant("r1l", "reactant", "(R)-1l", P3, SMILES["1l"]),
        participant("h2o2", "reagent", "H2O2", P3, "OO", amounts=[field("equivalents", q(1.1, "equiv"), P3)]),
        participant("hoac", "solvent", "HOAc", P3, "CC(=O)O"),
        participant("intermediate6", "unspecified_agent", "proposed five-membered cyclic intermediate 6", P3),
        participant("s_z3l", "product", "(S)-(Z)-3l", P3, SMILES["Z-3l"]),
    ],
    [step("proposed_pathway", ["r1l", "h2o2", "hoac", "intermediate6", "s_z3l"], [field("temperature", q(95, "°C"), P3), field("time", q(17, "h"), P3), field("operation", "Proposed protonation and intramolecular sulfinyl-oxygen attack, acetate SN2 attack with inversion, then oxidation/ring opening.", P3)])],
    [field("associated_experimental_yield", q(41, "%"), P3, ["s_z3l"])],
    notes=["Intermediate 6 and the pathway are proposed, not reported as isolated or directly observed."],
    unresolved=["The exact intermediate structure and elementary sequence are mechanistic proposals and require specialist review."]
))


for suffix, substrate, product, input_ee, output_ee, yield_value in [
    ("scheme3_r_1f_to_s_z_3f", "1f", "Z-3f", 99.0, 97.9, 39),
    ("scheme3_r_1m_to_s_z_3m", "1m", "Z-3m", 95.1, 94.8, 90),
]:
    evidence = P3
    substrate_id = "r_" + substrate
    product_id = "s_" + product.lower().replace("-", "_")
    parts = [
        participant(substrate_id, "reactant", f"(R)-{substrate}", evidence, SMILES[substrate]),
        participant("h2o2", "reagent", "H2O2", evidence, "OO"),
        participant("hoac", "solvent", "HOAc", evidence, "CC(=O)O"),
        participant(product_id, "product", f"(S)-({product})", evidence, SMILES[product]),
    ]
    records.append(record(
        suffix, "substrate_scope_entry", evidence, parts,
        [step("enantiospecific_oxidative_hydroacetoxylation", [p["entity_id"] for p in parts], [field("temperature", q(100, "°C"), evidence), field("time", q(17, "h"), evidence)])],
        [
            field("input_ee", q(input_ee, "%"), evidence, [substrate_id]),
            field("isolated_yield", q(yield_value, "%"), evidence, [product_id]),
            field("product_ee", q(output_ee, "%"), evidence, [product_id]),
        ],
        notes=["ee values refer to axial chirality as stated in Scheme 3."],
        unresolved=["Scale, H2O2 loading, atmosphere, workup, purification and ee measurement method are not stated; absolute configuration and Z geometry remain unverified."]
    ))


assert len(records) == 37, len(records)

raw_path = ROOT / "raw_model" / "records_pages_0001_0004.json"
raw_path.parent.mkdir(parents=True, exist_ok=True)
raw_path.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")

# Coverage ledger: every region cites its same-page image and text evidence.
ids = {r["record_id"] for r in records}
def rid(suffix):
    value = f"{DOC}:{suffix}"
    assert value in ids
    return value

table1_ids = [rid(f"table1_entry{i}") for i in range(1, 8)] + [rid("table1_entry8_table2_entry1_z3a")] + [rid("table1_entry9"), rid("table1_entry10"), rid("table1_entry11")]
table2_ids = [rid("table1_entry8_table2_entry1_z3a")] + [rid(f"table2_entry{i}") for i in range(2, 14)]
coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1,
            "state": "attempted",
            "regions": [
                {"region": "upper-left graphical abstract", "finding": "Generic current-paper oxidative hydroacetoxylation scope (13 examples, 39-90% yield) classified as a general scheme, not a batch.", "evidence_ids": P1},
                {"region": "lower-right equation (1) and adjacent prose", "finding": "Prior-work oxidation of 1a with 2.8 equiv H2O2 in HOAc at 100 °C for 15 min gives 2a (50%) and Z-3a (3%); classified as a literature example.", "evidence_ids": P1},
            ],
            "record_ids": [rid("graphical_abstract_general_scope"), rid("eq1_prior_oxidation_1a")],
            "unresolved": ["The graphical abstract contains generic R groups; equation (1) does not explicitly state the 2a yield basis."],
        },
        {
            "page": 2,
            "state": "attempted",
            "regions": [
                {"region": "upper-left Table 1 and footnotes", "finding": "Eleven independent optimization rows extracted from the image; image inspection corrected text-layer row 10/11 outcomes to 4/50 and 0/41 for 2a/Z-3a.", "evidence_ids": P2},
                {"region": "middle-left Table 2 and footnote", "finding": "Thirteen substrate-scope rows extracted; entry 1 is merged with Table 1 entry 8 and the page-3 typical procedure.", "evidence_ids": P2},
                {"region": "right column prose and equations (2)-(4)", "finding": "Two failed substrates plus DOAc labeling, oxidant-free 1b hydroacetoxylation, and unreactive sulfone 2b experiments extracted separately.", "evidence_ids": P2},
                {"region": "bottom-right optically active (R)-1l discussion", "finding": "The 41% optically active (R)-1l to (S)-(Z)-3l experiment is linked to Scheme 1 step b on page 3 and kept distinct from racemic Table 2 entry 12.", "evidence_ids": P2},
            ],
            "record_ids": table1_ids + table2_ids + [
                rid("failed_3phenyl_1_2_butadienyl_sulfoxide"),
                rid("failed_3ethyl_1_2_pentadienyl_sulfoxide"),
                rid("eq2_doac_deuteration_1m"),
                rid("eq3_hydroacetoxylation_1b_without_h2o2"),
                rid("eq4_allenyl_sulfone_2b_no_reaction"),
                rid("scheme1_step_b_r_1l_to_s_z_3l"),
            ],
            "unresolved": ["Most table rows omit atmosphere, workup and purification; the two prose-only failures omit exact conditions and structures."],
        },
        {
            "page": 3,
            "state": "attempted",
            "regions": [
                {"region": "upper-left Scheme 1 and Figure 3", "finding": "Four successive operations extracted; step b merges the page-2 optically active experiment. Figure 3 is assignment evidence, not another reaction.", "evidence_ids": P3},
                {"region": "upper-right Scheme 2", "finding": "Five-membered cyclic intermediate and inversion/oxidation pathway classified as a proposed mechanism, not an observed batch.", "evidence_ids": P3},
                {"region": "middle-right Scheme 3", "finding": "Two substrate-specific optically active preparations extracted independently with input/product ee and isolated yields.", "evidence_ids": P3},
                {"region": "lower-right typical Z-3a procedure", "finding": "Exact quantities, dropwise-addition time, workup, purification, product mass and isolated yield merged into the Table 1 entry 8/Table 2 entry 1 record.", "evidence_ids": P3},
            ],
            "record_ids": [
                rid("scheme1_step_a_prepare_r_1l"), rid("scheme1_step_b_r_1l_to_s_z_3l"),
                rid("scheme1_step_c_hydrolysis_s_z_3l"), rid("scheme1_step_d_pnitrobenzoylation_s_z_4l"),
                rid("scheme2_proposed_five_membered_mechanism"), rid("scheme3_r_1f_to_s_z_3f"),
                rid("scheme3_r_1m_to_s_z_3m"), rid("table1_entry8_table2_entry1_z3a"),
            ],
            "unresolved": ["Scheme operations generally omit scale and operational details; all stereochemical assignments and candidate structures remain unverified."],
        },
        {
            "page": 4,
            "state": "attempted",
            "regions": [
                {"region": "acknowledgement and Supporting Information Available notice", "finding": "No independent reaction is reported. The page states that SI exists online, but no SI file was supplied or explicitly associated.", "evidence_ids": P4},
            ],
            "record_ids": [],
            "unresolved": ["SI association remains unestablished; no SI-only procedure or analytical detail was imported."],
        },
    ],
}
coverage_path = ROOT / "coverage" / "pages_0001_0004.json"
coverage_path.parent.mkdir(parents=True, exist_ok=True)
coverage_path.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

tasks_path = ROOT / "tasks.json"
tasks = json.loads(tasks_path.read_text())
for task in tasks:
    if task["document_id"] == DOC and task["evidence_id"] in {f"{DOC}:page{i}:text" for i in range(1, 5)}:
        task["state"] = "attempted"
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"records": len(records), "raw": str(raw_path), "coverage_pages": [1, 2, 3, 4]}, ensure_ascii=False))
