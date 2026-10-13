#!/usr/bin/env python3
"""Build machine extraction records for doc_994fefd870ff00d2, PDF pages 1-3."""

import json
from pathlib import Path


DOC = "doc_994fefd870ff00d2"
E1 = f"{DOC}:page1:image"
E2 = f"{DOC}:page2:image"
E3 = f"{DOC}:page3:image"


def fact(value, evidence):
    return {
        "value": value,
        "evidence_ids": list(evidence),
        "verification": "missing" if value is None else "unreviewed",
    }


def field(name, value, evidence, targets=None):
    result = {"name": name, "fact": fact(value, evidence)}
    if targets:
        result["target_entity_ids"] = list(targets)
    return result


def participant(entity_id, role, evidence, label=None, name=None, smiles=None, amounts=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence),
        "smiles": fact(smiles, evidence),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": amounts or [],
    }


def record(suffix, kind, evidence, participants, steps, outcomes=None, notes=None, unresolved=None):
    return {
        "record_id": f"{DOC}:{suffix}",
        "document_id": DOC,
        "source_reaction_id": suffix,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": list(evidence),
        "participants": participants,
        "steps": steps,
        "outcomes": outcomes or [],
        "notes": [fact(note, evidence) for note in (notes or [])],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved or [],
        },
    }


def step(step_id, participant_ids, conditions):
    return {"step_id": step_id, "participant_ids": participant_ids, "conditions": conditions}


def q(number, unit, raw_text=None, qualifier=None):
    value = {"number": number, "unit": unit}
    if raw_text is not None:
        value["raw_text"] = raw_text
    if qualifier is not None:
        value["qualifier"] = qualifier
    return value


def qr(minimum, maximum, unit, raw_text):
    return {"minimum": minimum, "maximum": maximum, "unit": unit, "raw_text": raw_text}


records = []

# Page 1: graphical abstract, kept distinct from the row-level experiments.
records.append(record(
    "abstract_general_scheme",
    "general_scheme",
    [E1],
    [
        participant("generic_allenyl_acetylacetate", "reactant", [E1], "2-(2′,3′-allenyl)acetylacetate", "generic R1-substituted allenyl acetylacetate"),
        participant("generic_organic_iodide", "reactant", [E1], "R2I", "generic organic iodide"),
        participant("abstract_pd", "catalyst", [E1], "Pd(PPh3)4", "tetrakis(triphenylphosphine)palladium(0)", amounts=[field("catalyst_loading", q(5, "mol%"), [E1])]),
        participant("abstract_base", "reagent", [E1], "K3PO4·3H2O", "tripotassium phosphate trihydrate", amounts=[field("equivalents", q(2.0, "equiv"), [E1])]),
        participant("abstract_dmf", "solvent", [E1], "DMF", "N,N-dimethylformamide", "CN(C)C=O"),
        participant("generic_dihydrofuran", "product", [E1], "4,5-dihydrofuran derivative", "generic substituted 4,5-dihydrofuran"),
    ],
    [step("coupling_cyclization", ["generic_allenyl_acetylacetate", "generic_organic_iodide", "abstract_pd", "abstract_base", "abstract_dmf", "generic_dihydrofuran"], [field("temperature", q(85, "°C"), [E1]), field("time", None, [E1])])],
    [
        field("reported_yield_range", qr(62, 100, "%", "62–100%"), [E1], ["generic_dihydrofuran"]),
        field("reported_selectivity", ">97:3", [E1], ["generic_dihydrofuran"]),
        field("yield_measurement_basis", None, [E1]),
    ],
    unresolved=[
        "Generic R1/R2 structures cannot be expanded to fixed structures.",
        "Reaction time, scale, workup, purification, atmosphere, and yield basis are not stated in the graphical abstract.",
    ],
))


def add_literature(suffix, reactants, products, conditions, note, unresolved):
    participants = []
    ids = []
    for idx, (label, name) in enumerate(reactants, 1):
        entity = f"lit_reactant_{idx}"
        participants.append(participant(entity, "reactant", [E1], label, name))
        ids.append(entity)
    for idx, (label, name) in enumerate(products, 1):
        entity = f"lit_product_{idx}"
        participants.append(participant(entity, "product", [E1], label, name))
        ids.append(entity)
    for idx, spec in enumerate(conditions, 1):
        label, name, role, smiles = spec
        entity = f"lit_agent_{idx}"
        participants.append(participant(entity, role, [E1], label, name, smiles))
        ids.append(entity)
    records.append(record(suffix, "literature_example", [E1], participants,
                          [step("reported_prior_transformation", ids, [])], notes=[note], unresolved=unresolved))


prior_missing = [
    "This is a cited prior-literature transformation, not an experiment newly reported in this paper.",
    "The supplied page does not give complete quantities, time, temperature, scale, workup, purification, or numerical yield.",
    "Generic structures and substitution patterns require the cited primary source for resolution.",
]
add_literature(
    "page1_prior_allenyl_malonate_to_cyclopropane",
    [("2-(2′,3′-allenyl)malonate", "generic 2-(2′,3′-allenyl)malonate")],
    [("vinylic cyclopropane derivative", "generic vinylic cyclopropane")],
    [],
    "The introduction cites ref. 7a for this selectively accessible carbocycle.",
    prior_missing,
)
add_literature(
    "page1_prior_allenyl_malonate_to_cyclopentene",
    [("2-(2′,3′-allenyl)malonate", "generic 2-(2′,3′-allenyl)malonate")],
    [("cyclopentene derivative", "generic cyclopentene derivative")],
    [],
    "The introduction cites ref. 7b and states that solvent/base tuning controls this branch.",
    prior_missing,
)
add_literature(
    "page1_prior_allenyl_ketone_furan",
    [("1,2-allenyl ketone", "generic 1,2-allenyl ketone"), ("organic halide", "generic organic halide")],
    [("polysubstituted furan", "generic polysubstituted furan")],
    [("Pd(0)", "palladium(0) catalyst", "catalyst", None), ("Ag2CO3", "silver carbonate", "reagent", "[Ag+].[Ag+].[O-]C([O-])=O"), ("Et3N", "triethylamine", "reagent", "CCN(CC)CC"), ("toluene", "toluene", "solvent", "Cc1ccccc1")],
    "The introduction cites refs. 7c–e for this prior furan synthesis.",
    prior_missing,
)
add_literature(
    "page1_prior_23_allenol_dihydrofuran",
    [("allylic halide", "generic allylic halide"), ("2,3-allenol", "generic 2,3-allenol")],
    [("2,5-dihydrofuran", "generic 2,5-dihydrofuran")],
    [("Pd(II)", "palladium(II) catalyst", "catalyst", None)],
    "The introduction cites refs. 7f,g for Pd(II)-catalyzed coupling-cyclization.",
    prior_missing,
)
add_literature(
    "page1_prior_34_allenol_dihydropyran",
    [("allylic halide", "generic allylic halide"), ("3,4-allenol", "generic 3,4-allenol")],
    [("5,6-dihydropyran", "generic 5,6-dihydropyran")],
    [("Pd(II)", "palladium(II) catalyst", "catalyst", None)],
    "The introduction cites refs. 7f,g for Pd(II)-catalyzed coupling-cyclization.",
    prior_missing,
)
add_literature(
    "page1_prior_34_allenol_23_dihydrofuran",
    [("3,4-allenol", "generic 3,4-allenol"), ("aryl iodide", "generic aryl iodide")],
    [("2,3-dihydrofuran", "generic 2,3-dihydrofuran")],
    [],
    "The introduction cites ref. 7h and describes an oxidative-addition/exo-oxypalladation/reductive-elimination sequence.",
    prior_missing,
)

# Page 2 Scheme 1: proposed generic pathways, not observed row-level experiments.
scheme1_participants = [
    participant("scheme1_allene", "reactant", [E2], "generic allenyl β-dicarbonyl", "generic substituted allenyl carbonyl substrate"),
    participant("scheme1_halide", "reactant", [E2], "R5X", "generic organic halide"),
    participant("scheme1_pd", "catalyst", [E2], "Pd(0)", "palladium(0) catalyst"),
    participant("scheme1_base", "reagent", [E2], "base", "unspecified base"),
]
for key, label in [("oa", "O-attack a product"), ("ob", "O-attack b product"), ("ca", "C-attack a product"), ("cb", "C-attack b product")]:
    scheme1_participants.append(participant(f"scheme1_{key}", "product", [E2], label, f"generic proposed {label}"))
records.append(record(
    "scheme1_proposed_pathways", "mechanism", [E2], scheme1_participants,
    [
        step("oxidative_addition_and_enolate", ["scheme1_allene", "scheme1_halide", "scheme1_pd", "scheme1_base"], [field("operation", "Pd(0), then base; proposed π-allylpalladium/enolate intermediate", [E2])]),
        step("o_attack_a", ["scheme1_oa"], [field("operation", "intramolecular O-attack pathway a", [E2])]),
        step("o_attack_b", ["scheme1_ob"], [field("operation", "intramolecular O-attack pathway b", [E2])]),
        step("c_attack_a", ["scheme1_ca"], [field("operation", "intramolecular C-attack pathway a", [E2])]),
        step("c_attack_b", ["scheme1_cb"], [field("operation", "intramolecular C-attack pathway b", [E2])]),
    ],
    notes=["Scheme 1 enumerates possible pathways/products rather than four independently performed experiments."],
    unresolved=["All R groups, EWG, halide identity, quantities, and numerical conditions are generic or unstated."],
))


SMILES_1A = "C=C=CCC(C(C)=O)C(=O)OCC"
SMILES_3AA = "CC1=C(C(=O)OCC)CC(O1)C(=C)c1ccccc1"
SMILES_PHI = "Ic1ccccc1"
SMILES_DMF = "CN(C)C=O"
SMILES_K3PO4_3H2O = "[K+].[K+].[K+].[O-]P([O-])([O-])=O.O.O.O"


def base_participant(label, smiles, evidence):
    return participant("base", "reagent", evidence, label, label, smiles,
                       amounts=[field("equivalents", q(2.0, "equiv"), evidence)])


def common_1a_phi(evidence, base=None, solvent=("DMF", "N,N-dimethylformamide", SMILES_DMF), scale=False):
    parts = [
        participant("substrate_1a", "reactant", evidence, "1a", "ethyl 2-acetyl-2-(buta-2,3-dienyl)acetate", SMILES_1A,
                    amounts=[field("amount", q(0.15, "mmol"), evidence)] if scale else []),
        participant("organic_halide_2a", "reactant", evidence, "2a / PhI", "iodobenzene", SMILES_PHI,
                    amounts=[field("equivalents", q(1.2, "equiv"), evidence)]),
        participant("pd_catalyst", "catalyst", evidence, "Pd(PPh3)4", "tetrakis(triphenylphosphine)palladium(0)",
                    amounts=[field("catalyst_loading", q(5, "mol%"), evidence)]),
        participant("solvent", "solvent", evidence, solvent[0], solvent[1], solvent[2]),
        participant("product_3aa", "product", evidence, "3aa", "2-methyl-3-ethoxycarbonyl-5-(1-phenylvinyl)-4,5-dihydrofuran", SMILES_3AA),
        participant("product_4aa", "product", evidence, "4aa", "five-membered carbocycle 4aa"),
    ]
    if base is not None:
        parts.insert(3, base_participant(base[0], base[1], evidence))
    return parts


BASES = {
    "LiOH": "[Li+].[OH-]",
    "t-BuOK": "CC(C)(C)[O-].[K+]",
    "NaOH": "[Na+].[OH-]",
    "NaH": "[Na+].[H-]",
    "K2CO3": "[K+].[K+].[O-]C([O-])=O",
    "Et3N": "CCN(CC)CC",
    "KOH": "[K+].[OH-]",
    "K3PO4·3H2O": SMILES_K3PO4_3H2O,
}


table1 = [
    (1, "LiOH", 7, 63, 15, "81:19"),
    (2, "t-BuOK", 8, 54, None, "91:9"),
    (3, "NaOH", 8, 68, None, "99:1"),
    (4, "NaH", 7, 45, None, "100:0"),
    (5, "K2CO3", 8, 68, None, "100:0"),
    (6, "Et3N", 7, 73, None, "100:0"),
    (7, "KOH", 8, 68, None, "100:0"),
    (8, None, 8, 13, None, "100:0"),
]
for entry, base_name, hours, yield3, yield4, ratio in table1:
    evidence = [E2]
    parts = common_1a_phi(evidence, (base_name, BASES[base_name]) if base_name else None)
    conditions = [
        field("temperature", q(85, "°C") if entry == 1 else qr(85, 90, "°C", "85–90 °C"), evidence),
        field("time", q(hours, "h"), evidence),
        field("atmosphere", None, evidence),
        field("workup", None, evidence),
        field("purification", None, evidence),
    ]
    outcomes = [
        field("isolated_yield_3aa", q(yield3, "%"), evidence, ["product_3aa"]),
        field("yield_measurement_basis", "isolated", evidence),
        field("selectivity_ratio_3aa_to_4aa", ratio, evidence, ["product_3aa", "product_4aa"]),
        field("ratio_measurement_basis", "NMR analysis", evidence),
    ]
    if yield4 is not None:
        outcomes.insert(1, field("isolated_yield_4aa", q(yield4, "%"), evidence, ["product_4aa"]))
    if entry == 8:
        outcomes.append(field("recovered_starting_material_yield", q(71, "%"), evidence, ["substrate_1a"]))
    records.append(record(
        f"table1_entry{entry}", "optimization_entry", evidence, parts,
        [step("coupling_cyclization", [p["entity_id"] for p in parts], conditions)], outcomes,
        notes=["No base was added in this row."] if entry == 8 else [],
        unresolved=[
            "Table 1 footnote prints 3aa as the material at reaction scale, while the title, scheme, and prose identify 1a as the starting material; the row scale is therefore not assigned.",
            "Individual 4aa yield is not reported for this row." if yield4 is None else "The source does not report whether any additional products were present.",
            "Atmosphere, workup, and purification are not reported in the supplied main text.",
        ],
    ))

# The optimized PhI/DMF/K3PO4 row is repeated as Table 1 entry 9, Table 2 entry 1,
# and Table 3 entry 1. It is represented once with both page images.
standard_ev = [E2, E3]
standard_parts = common_1a_phi(standard_ev, ("K3PO4·3H2O", BASES["K3PO4·3H2O"]), scale=True)
records.append(record(
    "standard_1a_phi_table1e9_table2e1_table3e1", "optimization_entry", standard_ev, standard_parts,
    [step("coupling_cyclization", [p["entity_id"] for p in standard_parts], [
        field("temperature", q(85, "°C"), [E3]), field("time", q(8, "h"), standard_ev),
        field("atmosphere", None, standard_ev), field("workup", None, standard_ev), field("purification", None, standard_ev),
    ])],
    [
        field("isolated_yield_3aa", q(100, "%"), standard_ev, ["product_3aa"]),
        field("yield_measurement_basis", "isolated", standard_ev),
        field("selectivity_ratio_3aa_to_4aa", "100:0", standard_ev, ["product_3aa", "product_4aa"]),
        field("ratio_measurement_basis", "NMR analysis", [E2]),
    ],
    notes=["The same optimized result is printed in three tables and is not counted three times."],
    unresolved=[
        "Table 1 gives an arrow temperature range while Tables 2 and 3 specify 85 °C; the row-specific value is retained.",
        "The hydrate is drawn as K3PO4·3H2O, while prose and table footnotes shorten the base to K3PO4.",
        "Atmosphere, workup, and purification are not reported in the supplied main text.",
    ],
))


SOLVENTS = {
    "THF": ("tetrahydrofuran", "C1CCOC1"),
    "CH3CN": ("acetonitrile", "CC#N"),
    "toluene": ("toluene", "Cc1ccccc1"),
    "DMSO": ("dimethyl sulfoxide", "CS(C)=O"),
    "dioxane": ("1,4-dioxane", "O1CCOCC1"),
    "CH2Cl2": ("dichloromethane", "ClCCl"),
    "CH3OH": ("methanol", "CO"),
}
table2 = [
    (2, "THF", "reflux", 8, 81, "100:0"),
    (3, "CH3CN", "reflux", 8, 81, "≥97:3"),
    (4, "toluene", q(85, "°C"), 8, 91, "100:0"),
    (5, "DMSO", q(85, "°C"), 8, 82, "100:0"),
    (6, "dioxane", q(85, "°C"), 8, 87, "100:0"),
    (7, "CH2Cl2", "reflux", 6, 78, "100:0"),
    (8, "CH3OH", "reflux", 6, 0, None),
]
for entry, solvent_label, temp, hours, yield3, ratio in table2:
    evidence = [E2, E3] if entry == 2 else [E3]
    solvent_name, solvent_smiles = SOLVENTS[solvent_label]
    parts = common_1a_phi(evidence, ("K3PO4·3H2O", BASES["K3PO4·3H2O"]), (solvent_label, solvent_name, solvent_smiles), scale=True)
    outcomes = [field("isolated_yield_3aa", q(yield3, "%"), evidence, ["product_3aa"]), field("yield_measurement_basis", "isolated", evidence)]
    if ratio is not None:
        outcomes.append(field("selectivity_ratio_3aa_to_4aa", ratio, evidence, ["product_3aa", "product_4aa"]))
    records.append(record(
        f"table2_entry{entry}", "optimization_entry", evidence, parts,
        [step("coupling_cyclization", [p["entity_id"] for p in parts], [
            field("temperature", temp, evidence), field("time", q(hours, "h"), evidence),
            field("atmosphere", None, evidence), field("workup", None, evidence), field("purification", None, evidence),
        ])], outcomes,
        notes=(["The prose states that the methanol reaction failed to afford the products."] if entry == 8 else
               ["The page-2 prose says THF formed 3aa together with a small amount of 4aa, but the Table 2 row prints 100:0."] if entry == 2 else []),
        unresolved=[
            "No product ratio is reported for the methanol row." if ratio is None else
            "The prose/table conflict over whether 4aa formed under THF requires source review." if entry == 2 else
            "The table does not state the analytical method for this product ratio.",
            "Atmosphere, workup, and purification are not reported in the supplied main text.",
        ],
    ))


IODIDES = {
    2: ("4-MeC6H4I", "1-iodo-4-methylbenzene", "Cc1ccc(I)cc1", "3ab", "4-methylphenyl", "c1ccc(C)cc1"),
    3: ("4-MeOC6H4I", "1-iodo-4-methoxybenzene", "COc1ccc(I)cc1", "3ac", "4-methoxyphenyl", "c1ccc(OC)cc1"),
    4: ("4-MeO2CC6H4I", "methyl 4-iodobenzoate", "COC(=O)c1ccc(I)cc1", "3ad", "4-methoxycarbonylphenyl", "c1ccc(C(=O)OC)cc1"),
    5: ("4-AcC6H4I", "4-iodoacetophenone", "CC(=O)c1ccc(I)cc1", "3ae", "4-acetylphenyl", "c1ccc(C(C)=O)cc1"),
    6: ("4-BrC6H4I", "1-bromo-4-iodobenzene", "Brc1ccc(I)cc1", "3af", "4-bromophenyl", "c1ccc(Br)cc1"),
    7: ("1-iodonaphthalene", "1-iodonaphthalene", "Ic1cccc2ccccc12", "3ag", "1-naphthyl", "c1cccc2ccccc12"),
    8: ("1-(E)-hexenyl iodide", "(E)-1-iodohex-1-ene", None, "3ah", "1-(E)-hexenyl", None),
    9: ("2-iodothiophene", "2-iodothiophene", "Ic1cccs1", "3ai", "2-thienyl", "c1ccsc1"),
}
scope_values = {2: (8, 87, "100:0"), 3: (8, 89, "100:0"), 4: (8, 58, "99:1"), 5: (2, 100, "97:3"), 6: (8, 80, "99:1"), 7: (8, 77, "100:0"), 8: (7, 81, "100:0"), 9: (2, 84, "99:1")}


def scope_product_smiles(aryl_fragment):
    if aryl_fragment is None:
        return None
    return f"CC1=C(C(=O)OCC)CC(O1)C(=C){aryl_fragment}"


for entry in range(2, 10):
    iodide_label, iodide_name, iodide_smiles, prod_label, substituent_name, fragment = IODIDES[entry]
    hours, yield3, ratio = scope_values[entry]
    evidence = [E3]
    parts = [
        participant("substrate_1a", "reactant", evidence, "1a", "ethyl 2-acetyl-2-(buta-2,3-dienyl)acetate", SMILES_1A),
        participant("organic_iodide", "reactant", evidence, iodide_label, iodide_name, iodide_smiles),
        participant("pd_catalyst", "catalyst", evidence, "Pd(PPh3)4", "tetrakis(triphenylphosphine)palladium(0)", amounts=[field("catalyst_loading", q(5, "mol%"), evidence)]),
        base_participant("K3PO4·3H2O", SMILES_K3PO4_3H2O, evidence),
        participant("solvent", "solvent", evidence, "DMF", "N,N-dimethylformamide", SMILES_DMF),
        participant("product_3a", "product", evidence, prod_label, f"2-methyl-3-ethoxycarbonyl-5-(1-{substituent_name}vinyl)-4,5-dihydrofuran", scope_product_smiles(fragment)),
        participant("product_4a", "product", evidence, "4a", "corresponding five-membered carbocycle 4a"),
    ]
    records.append(record(
        f"table3_entry{entry}", "substrate_scope_entry", evidence, parts,
        [step("coupling_cyclization", [p["entity_id"] for p in parts], [
            field("temperature", q(85, "°C"), evidence), field("time", q(hours, "h"), evidence),
            field("atmosphere", None, evidence), field("workup", None, evidence), field("purification", None, evidence),
        ])],
        [
            field(f"isolated_yield_{prod_label}", q(yield3, "%"), evidence, ["product_3a"]),
            field("yield_measurement_basis", "isolated", evidence),
            field("selectivity_ratio_3a_to_4a", ratio, evidence, ["product_3a", "product_4a"]),
        ],
        unresolved=[
            "Organic iodide equivalents and reaction scale are not repeated in Table 3 and are not inferred from earlier tables.",
            "The table does not state the analytical method for the product ratio.",
            "Atmosphere, workup, and purification are not reported in the supplied main text.",
            "The candidate scope structure is unverified; stereochemistry is not encoded." if fragment is not None else "The alkenyl iodide/product geometry and connectivity are not encoded as SMILES pending chemical review.",
        ],
    ))


table4 = [
    (1, "1b", "n-Pr", 85, "3ba", 91, "4ba", "99:1", "C=C=CCC(C(=O)CCC)C(=O)OC", "CCCC1=C(C(=O)OC)CC(O1)C(=C)c1ccccc1"),
    (2, "1c", "i-Pr", 85, "3ca", 81, "4ca", "98:2", "C=C=CCC(C(=O)C(C)C)C(=O)OC", "CC(C)C1=C(C(=O)OC)CC(O1)C(=C)c1ccccc1"),
    (3, "1c", "i-Pr", 60, "3ca", 40, "4ca", "97:3", "C=C=CCC(C(=O)C(C)C)C(=O)OC", "CC(C)C1=C(C(=O)OC)CC(O1)C(=C)c1ccccc1"),
    (4, "1c", "i-Pr", 100, "3ca", 40, "4ca", "97:3", "C=C=CCC(C(=O)C(C)C)C(=O)OC", "CC(C)C1=C(C(=O)OC)CC(O1)C(=C)c1ccccc1"),
]
for row, substrate_label, r_group, temp, product_label, product_yield, byproduct_label, ratio, substrate_smiles, product_smiles in table4:
    evidence = [E3]
    parts = [
        participant("substrate", "reactant", evidence, substrate_label, f"methyl 2-(buta-2,3-dienyl)-3-oxo ester with R={r_group}", substrate_smiles),
        participant("iodobenzene", "reactant", evidence, "PhI", "iodobenzene", SMILES_PHI),
        participant("pd_catalyst", "catalyst", evidence, "Pd(PPh3)4", "tetrakis(triphenylphosphine)palladium(0)", amounts=[field("catalyst_loading", q(5, "mol%"), evidence)]),
        base_participant("K3PO4·3H2O", SMILES_K3PO4_3H2O, evidence),
        participant("solvent", "solvent", evidence, "DMF", "N,N-dimethylformamide", SMILES_DMF),
        participant("product_3", "product", evidence, product_label, f"4,5-dihydrofuran {product_label}", product_smiles),
        participant("product_4", "product", evidence, byproduct_label, f"five-membered carbocycle {byproduct_label}"),
    ]
    records.append(record(
        f"table4_row{row}", "optimization_entry", evidence, parts,
        [step("coupling_cyclization", [p["entity_id"] for p in parts], [
            field("temperature", q(temp, "°C"), evidence), field("time", q(8, "h"), evidence),
            field("atmosphere", None, evidence), field("workup", None, evidence), field("purification", None, evidence),
        ])],
        [
            field(f"isolated_yield_{product_label}", q(product_yield, "%"), evidence, ["product_3"]),
            field("yield_measurement_basis", "isolated", evidence),
            field("selectivity_ratio_3_to_4", ratio, evidence, ["product_3", "product_4"]),
            field("ratio_measurement_basis", "NMR analysis", evidence),
        ],
        unresolved=[
            "PhI amount and reaction scale are not reported in Table 4.",
            "Individual carbocycle yield is not reported.",
            "Atmosphere, workup, and purification are not reported in the supplied main text.",
            "Candidate substrate/product connectivity is machine-interpreted from the drawing and remains unverified; stereochemistry is not encoded.",
        ],
    ))


scheme2_ev = [E3]
scheme2_parts = [
    participant("substrate_1d", "reactant", scheme2_ev, "1d", "2-(buta-2′,3′-dienyl)cyclohexane-1,3-dione", "C=C=CCC1C(=O)CCCC1=O"),
    participant("iodobenzene_2a", "reactant", scheme2_ev, "2a / PhI", "iodobenzene", SMILES_PHI),
    participant("pd_catalyst", "catalyst", scheme2_ev, "Pd(PPh3)4", "tetrakis(triphenylphosphine)palladium(0)", amounts=[field("catalyst_loading", q(5, "mol%"), scheme2_ev)]),
    base_participant("K3PO4·3H2O", SMILES_K3PO4_3H2O, scheme2_ev),
    participant("solvent", "solvent", scheme2_ev, "DMF", "N,N-dimethylformamide", SMILES_DMF),
    participant("product_3da", "product", scheme2_ev, "3da", "bicyclic dihydrofuran product 3da"),
]
records.append(record(
    "scheme2_1d_phi_to_3da", "substrate_scope_entry", scheme2_ev, scheme2_parts,
    [step("coupling_cyclization", [p["entity_id"] for p in scheme2_parts], [
        field("temperature", None, scheme2_ev), field("time", q(9, "h"), scheme2_ev),
        field("atmosphere", None, scheme2_ev), field("workup", None, scheme2_ev), field("purification", None, scheme2_ev),
    ])],
    [field("reported_yield_3da", q(58, "%"), scheme2_ev, ["product_3da"]), field("yield_measurement_basis", None, scheme2_ev)],
    unresolved=[
        "Temperature, reaction scale, PhI amount, yield basis, atmosphere, workup, and purification are not reported in Scheme 2.",
        "The fused bicyclic product connectivity and stereochemistry are not encoded as SMILES pending chemical review.",
    ],
))


out = Path(__file__).with_name("pages_0001_0003_records.json")
out.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"records": len(records), "output": str(out)}, ensure_ascii=False))
