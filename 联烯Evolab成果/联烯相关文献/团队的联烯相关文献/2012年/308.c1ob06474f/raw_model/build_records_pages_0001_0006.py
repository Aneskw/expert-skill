#!/usr/bin/env python3
"""Build evidence-linked machine records for PDF pages 1-6 of doc_04c178582cab751e."""

import json
from pathlib import Path


BASE = Path(__file__).resolve().parents[1]
DOC = "doc_04c178582cab751e"


def ev(page):
    return [f"{DOC}:page{page}:text", f"{DOC}:page{page}:image"]


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


SMILES = {
    "platinum(II) chloride": "Cl[Pt]Cl",
    "toluene": "Cc1ccccc1",
    "tetrahydrofuran": "C1CCOC1",
    "diethyl ether": "CCOCC",
    "1,2-dichloroethane": "ClCCCl",
    "dichloromethane": "ClCCl",
    "oxygen": "O=O",
    "sodium chloride": "[Na+].[Cl-]",
    "ammonium chloride": "[Cl-].[NH4+]",
    "indium": "[In]",
    "water": "O",
    "3,4-dihydro-2H-pyran": "C1=CCCOC1",
    "p-toluenesulfonic acid": "Cc1ccc(S(=O)(=O)O)cc1",
    "non-1-yn-3-ol": "C#CC(O)CCCCCC",
    "1-nonyn-3-one": "C#CC(=O)CCCCCC",
}


def participant(entity_id, role, evidence, *, label=None, name=None, amounts=None, smiles=None):
    if smiles is None and name in SMILES:
        smiles = SMILES[name]
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


def record(rid, kind, evidence, participants=None, steps=None, outcomes=None, notes=None, unresolved=None):
    return {
        "record_id": f"{DOC}:{rid}",
        "document_id": DOC,
        "source_reaction_id": rid,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": list(dict.fromkeys(evidence)),
        "participants": participants or [],
        "steps": steps or [],
        "outcomes": outcomes or [],
        "notes": [fact(n, evidence) for n in (notes or [])],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved or [
                "Machine extraction requires source-level chemical review.",
                "Supporting Information was mentioned but not supplied or explicitly associated.",
            ],
        },
    }


def amount(name, number, unit, evidence):
    return field(name, {"number": number, "unit": unit}, evidence)


records = []

# Page 1: classify the literature overview without treating it as a reported experiment.
records.append(record(
    "scheme1_prior_carbazole_strategies",
    "general_scheme",
    ev(1),
    notes=[
        "Scheme 1 summarizes prior carbazole syntheses (classical, reductive, iron-mediated, palladium-catalyzed, and cyclotrimerization routes); it is not a new experiment of this paper."
    ],
    unresolved=[
        "Generic structures and R groups do not specify unique molecules.",
        "The cited prior-literature reactions were not imported as experiments of this paper.",
    ],
))


table1 = [
    (1, "Et", "H", "H", 4, 70),
    (2, "Et", "n-C4H9", "H", 3, 74),
    (3, "Et", "allyl", "H", 3, 74),
    (4, "Et", "Ph", "H", 4, 70),
    (5, "Et", "p-MeC6H4", "H", 16, 69),
    (6, "Et", "p-MeOC6H4", "H", 15, 76),
    (7, "Et", "COOMe", "H", 36, 67),
    (8, "Et", "CONMe2", "H", 24, 83),
    (9, "Et", "CH2OH", "H", 23, 64),
    (10, "Et", "CH2OEt", "H", 12, 84),
    (11, "Et", "CH2OAc", "H", 24, 81),
    (12, "Et", "CH2OCOOMe", "H", 13, 77),
    (13, "Et", "n-C4H9", "4-Me", 18, 77),
    (14, "Et", "Ph", "5-Me", 17, 70),
    (15, "Et", "CH2OH", "4-Me", 20, 81),
    (16, "Et", "CH2OH", "7-Me", 21, 68),
    (17, "Et", "OBn", "H", 11, 60),
    (18, "Me", "n-C4H9", "H", 4, 81),
    (19, "Me", "Ph", "H", 4, 71),
    (20, "Ph", "Ph", "H", 19, 78),
    (21, "PMP", "Ph", "H", 16, 72),
]


def scope_record(table, entry, substrate, product, substitutions, time_h, yield_pct):
    evidence = ev(2)
    catalyst = f"{table}_entry{entry}_ptcl2"
    solvent = f"{table}_entry{entry}_toluene"
    reactant = f"{table}_entry{entry}_substrate"
    prod = f"{table}_entry{entry}_product"
    return record(
        f"{table}_entry{entry}",
        "substrate_scope_entry",
        evidence,
        participants=[
            participant(reactant, "reactant", evidence, label=substrate,
                        name=f"{substrate}; {substitutions}"),
            participant(catalyst, "catalyst", evidence, name="platinum(II) chloride",
                        amounts=[amount("catalyst_loading", 5, "mol%", evidence)]),
            participant(solvent, "solvent", evidence, name="toluene"),
            participant(prod, "product", evidence, label=product,
                        name=f"corresponding carbazole {product}"),
        ],
        steps=[{
            "step_id": "cyclization",
            "participant_ids": [reactant, catalyst, solvent, prod],
            "conditions": [
                field("time", {"number": time_h, "unit": "h"}, evidence),
                field("temperature", None, evidence),
                field("solvent", "toluene", evidence),
            ],
        }],
        outcomes=[
            field("isolated_yield", {"number": yield_pct, "unit": "%"}, evidence, [prod]),
            field("yield_measurement_basis", "isolated yield", evidence, [prod]),
        ],
        notes=[f"{table.replace('table', 'Table ')} entry {entry}; PtCl2 (5 mol%) in toluene."],
        unresolved=[
            "Substrate and product structures are represented by source labels/substituent columns; candidate SMILES are not source-verified.",
            "Reaction scale, exact temperature, atmosphere, solvent volume, workup, and purification are not reported in the table row.",
            "Supporting Information was not supplied or explicitly associated.",
        ],
    )


for entry, r1, r2, r3, hours, yield_pct in table1:
    records.append(scope_record(
        "table1", entry, f"1{chr(96 + entry)}", f"2{chr(96 + entry)}",
        f"R1={r1}; R2={r2}; R3={r3}", hours, yield_pct,
    ))


table2 = [
    (1, "H", "H", "n-C5H11", "H", 2, 83),
    (2, "H", "H", "Me", "H", 2, 86),
    (3, "H", "H", "i-C3H7", "H", 20, 38),
    (4, "H", "H", "Bn", "H", 5, 50),
    (5, "H", "H", "Ph", "H", 14, 92),
    (6, "H", "H", "n-C6H13", "5-Me", 2, 75),
    (7, "H", "H", "n-C6H13", "5-OMe", 3, 75),
    (8, "H", "H", "Me", "4-Me", 20, 85),
    (9, "H", "H", "n-C6H13", "4-Me", 12, 81),
    (10, "H", "H", "n-C6H13", "5-Br", 16, 75),
    (11, "Me", "H", "n-C6H13", "H", 2, 81),
    (12, "H", "Me", "n-C6H13", "H", 21, 78),
]
for entry, r1, r2, r3, r4, hours, yield_pct in table2:
    records.append(scope_record(
        "table2", entry, f"3{chr(96 + entry)}", f"4{chr(96 + entry)}",
        f"R1={r1}; R2={r2}; R3={r3}; R4={r4}", hours, yield_pct,
    ))


# Page 3: isotope precursor chemistry, the labeling experiment, and the proposed mechanism.
p3 = ev(3)
records.append(record(
    "prep_1_nonyn_3_one",
    "reported_experiment",
    p3,
    participants=[
        participant("nonynol", "reactant", p3, name="non-1-yn-3-ol",
                    amounts=[amount("mass", 1.4002, "g", p3), amount("amount", 10, "mmol", p3)]),
        participant("ferric_nitrate", "catalyst", p3, name="iron(III) nitrate nonahydrate",
                    amounts=[amount("mass", 202.5, "mg", p3), amount("amount", 0.5, "mmol", p3), amount("catalyst_loading", 5, "mol%", p3)]),
        participant("tempo", "catalyst", p3, name="TEMPO",
                    amounts=[amount("mass", 156.1, "mg", p3), amount("amount", 1.0, "mmol", p3), amount("catalyst_loading", 10, "mol%", p3)]),
        participant("nacl", "reagent", p3, name="sodium chloride",
                    amounts=[amount("mass", 19.2, "mg", p3), amount("amount", 0.5, "mmol", p3), amount("catalyst_loading", 5, "mol%", p3)]),
        participant("oxygen", "reagent", p3, name="oxygen"),
        participant("dce", "solvent", p3, name="1,2-dichloroethane", amounts=[amount("volume", 10, "mL", p3)]),
        participant("nonynone", "product", p3, name="1-nonyn-3-one",
                    amounts=[amount("isolated_mass", 1.2420, "g", p3)]),
    ],
    steps=[{
        "step_id": "oxidation",
        "participant_ids": ["nonynol", "ferric_nitrate", "tempo", "nacl", "oxygen", "dce", "nonynone"],
        "conditions": [
            field("temperature", "r.t.", p3),
            field("time", None, p3),
            field("atmosphere", "oxygen from a balloon", p3),
            field("operation", "stirred until complete by TLC", p3),
            field("workup", "diluted with diethyl ether; dried over Na2SO4; filtered through a short silica column; evaporated", p3),
            field("purification", "silica-gel chromatography, petroleum ether/diethyl ether 40:1", p3),
        ],
    }],
    outcomes=[
        field("isolated_yield", {"number": 90, "unit": "%"}, p3, ["nonynone"]),
        field("yield_measurement_basis", "isolated after chromatography", p3, ["nonynone"]),
    ],
    unresolved=[
        "The reaction duration is reported only as until TLC completion.",
        "All structures remain machine-unverified.",
    ],
))

records.append(record(
    "prep_3_deutero_1_nonyn_3_ol",
    "reported_experiment",
    p3,
    participants=[
        participant("nonynone", "reactant", p3, name="1-nonyn-3-one",
                    amounts=[amount("mass", 3.501, "g", p3), amount("amount", 25, "mmol", p3)]),
        participant("liald4", "reagent", p3, name="lithium aluminium deuteride",
                    amounts=[amount("mass", 0.941, "g", p3), amount("amount", 23, "mmol", p3)]),
        participant("ether", "solvent", p3, name="diethyl ether",
                    amounts=[amount("initial_volume", 40, "mL", p3), amount("solution_volume", 20, "mL", p3)]),
        participant("deutero_alcohol", "product", p3, name="3-deutero-1-nonyn-3-ol",
                    amounts=[amount("isolated_mass", 2.997, "g", p3)]),
    ],
    steps=[{
        "step_id": "deuteride_reduction",
        "participant_ids": ["nonynone", "liald4", "ether", "deutero_alcohol"],
        "conditions": [
            field("temperature", {"number": -78, "unit": "°C"}, p3),
            field("addition_time", {"number": 30, "unit": "min"}, p3),
            field("time", {"number": 1, "unit": "h"}, p3),
            field("atmosphere", "N2", p3),
            field("workup", "quenched with water; ether extraction; MgSO4 drying; filtration and evaporation", p3),
            field("purification", "silica-gel chromatography", p3),
        ],
    }],
    outcomes=[
        field("isolated_yield", {"number": 84, "unit": "%"}, p3, ["deutero_alcohol"]),
        field("yield_measurement_basis", "isolated after chromatography", p3, ["deutero_alcohol"]),
    ],
    unresolved=["Exact deuterium incorporation for this intermediate is not stated here; structure remains machine-unverified."],
))

records.append(record(
    "scheme2_prep_8f_D",
    "reported_experiment",
    p3,
    participants=[
        participant("deutero_alcohol", "reactant", p3, name="3-deutero-1-nonyn-3-ol"),
        participant("dhp", "reagent", p3, name="3,4-dihydro-2H-pyran"),
        participant("tsoh", "catalyst", p3, name="p-toluenesulfonic acid"),
        participant("dcm", "solvent", p3, name="dichloromethane"),
        participant("eight_f_D", "product", p3, label="8f-D", name="THP-protected deuterated propargylic alcohol 8f-D"),
    ],
    steps=[{
        "step_id": "thp_protection",
        "participant_ids": ["deutero_alcohol", "dhp", "tsoh", "dcm", "eight_f_D"],
        "conditions": [field("temperature", None, p3), field("time", None, p3), field("solvent", "CH2Cl2", p3)],
    }],
    outcomes=[field("isolated_yield", {"number": 85, "unit": "%"}, p3, ["eight_f_D"])],
    unresolved=[
        "Scheme 2 does not state scale, reagent loadings, time, temperature, workup, purification, or yield measurement basis.",
        "The 8f-D structure is retained by source label without candidate SMILES.",
    ],
))


def two_stage_allenol(rid, pages, substrate_label, substrate_name, substrate_amounts,
                      aldehyde_name, aldehyde_amounts, n_buli_amounts, thf_amounts,
                      intermediate_label, lialh4_amounts, ether_amounts,
                      product_label, product_name, product_mass, yield_pct,
                      step1_conditions, step2_conditions, extra_outcomes=None,
                      inherited=False):
    evidence = []
    for page in pages:
        evidence.extend(ev(page))
    reactant = f"{rid}_substrate"
    aldehyde = f"{rid}_aldehyde"
    n_buli = f"{rid}_n_buli"
    thf = f"{rid}_thf"
    intermediate = f"{rid}_intermediate"
    lialh4 = f"{rid}_lialh4"
    ether = f"{rid}_ether"
    product = f"{rid}_product"
    outcomes = [
        field("combined_isolated_yield", {"number": yield_pct, "unit": "%"}, evidence, [product]),
        field("yield_measurement_basis", "combined yield from protected propargylic substrate to allenol", evidence, [product]),
    ]
    outcomes.extend(extra_outcomes or [])
    unresolved = [
        "Intermediate was used without further purification and has no separately reported yield.",
        "Complex structures are retained by labels/names with null SMILES and remain machine-unverified.",
        "Supporting Information was not supplied or explicitly associated.",
    ]
    if inherited:
        unresolved.append("Entry-specific times and temperatures are not restated; the source only says it was prepared according to the preceding typical procedure.")
    records.append(record(
        rid,
        "reported_experiment",
        evidence,
        participants=[
            participant(reactant, "reactant", evidence, label=substrate_label, name=substrate_name, amounts=substrate_amounts),
            participant(aldehyde, "reactant", evidence, name=aldehyde_name, amounts=aldehyde_amounts),
            participant(n_buli, "reagent", evidence, name="n-butyllithium", amounts=n_buli_amounts),
            participant(thf, "solvent", evidence, name="tetrahydrofuran", amounts=thf_amounts),
            participant(intermediate, "unspecified_agent", evidence, label=intermediate_label, name=f"unpurified intermediate {intermediate_label}"),
            participant(lialh4, "reagent", evidence, name="lithium aluminium hydride", amounts=lialh4_amounts),
            participant(ether, "solvent", evidence, name="diethyl ether", amounts=ether_amounts),
            participant(product, "product", evidence, label=product_label, name=product_name,
                        amounts=[amount("isolated_mass", product_mass, "g", evidence)]),
        ],
        steps=[
            {"step_id": "alkynyl_lithium_addition", "participant_ids": [reactant, aldehyde, n_buli, thf, intermediate], "conditions": step1_conditions},
            {"step_id": "reduction_deprotection", "participant_ids": [intermediate, lialh4, ether, product], "conditions": step2_conditions},
        ],
        outcomes=outcomes,
        notes=["Two successive experimental stages are retained in one record because the source reports only the combined isolated yield of the final allenol."],
        unresolved=unresolved,
    ))


p36 = ev(3) + ev(6)
two_stage_allenol(
    "prep_3f_D", [3, 6], "8f-D", "THP-protected deuterated propargylic alcohol 8f-D",
    [amount("mass", 0.7225, "g", p36), amount("amount", 3.2, "mmol", p36)],
    "1-ethyl-5-methyl-1H-indole-2-carbaldehyde",
    [amount("mass", 0.5910, "g", p36), amount("amount", 3.2, "mmol", p36)],
    [amount("solution_volume", 1.3, "mL", p36), amount("concentration", 2.5, "M", p36), amount("amount", 3.3, "mmol", p36)],
    [amount("substrate_solution_volume", 15, "mL", p36), amount("aldehyde_solution_volume", 5, "mL", p36)],
    "9f-D",
    [amount("mass", 0.1247, "g", p36), amount("amount", 3.3, "mmol", p36)],
    [amount("volume", 25, "mL", p36)],
    "3f-D", "1-(1-ethyl-5-methyl-1H-indol-2-yl)-4-deuterodeca-2,3-dien-1-ol",
    0.4881, 50,
    [
        field("temperature", {"number": -78, "unit": "°C"}, p36),
        field("n_buli_addition_and_stirring_time", {"number": 60, "unit": "min", "raw_text": "5+55 min"}, p36),
        field("aldehyde_addition_time", {"number": 5, "unit": "min"}, p36),
        field("warm_to", "r.t.", p36),
        field("time_at_room_temperature", {"number": 3, "unit": "h"}, p36),
    ],
    [
        field("initial_temperature", {"number": 0, "unit": "°C"}, p36),
        field("addition_time", {"number": 5, "unit": "min"}, p36),
        field("warm_to", "r.t.", p36),
        field("time_at_room_temperature", {"number": 3.4, "unit": "h"}, p36),
        field("purification", "silica-gel chromatography, petroleum ether/ethyl acetate 10:1", p36),
    ],
    extra_outcomes=[field("deuterium_incorporation", {"number": 98, "unit": "%"}, p36, ["prep_3f_D_product"])],
)

records.append(record(
    "isotope_cyclization_3f_D_to_4f_D",
    "reported_experiment",
    p3,
    participants=[
        participant("labeled_allenol", "reactant", p3, label="3f-D", name="98% D-labeled allenol 3f-D"),
        participant("ptcl2", "catalyst", p3, name="platinum(II) chloride", amounts=[amount("catalyst_loading", 5, "mol%", p3)]),
        participant("toluene", "solvent", p3, name="toluene"),
        participant("labeled_carbazole", "product", p3, label="4f-D", name="3-deutero-9-ethyl-4-hexyl-6-methyl-9H-carbazole"),
    ],
    steps=[{
        "step_id": "pt_catalyzed_cyclization",
        "participant_ids": ["labeled_allenol", "ptcl2", "toluene", "labeled_carbazole"],
        "conditions": [
            field("temperature", "r.t.", p3),
            field("time", {"number": 2, "unit": "h"}, p3),
            field("solvent", "toluene", p3),
        ],
    }],
    outcomes=[
        field("isolated_yield", {"number": 86, "unit": "%"}, p3, ["labeled_carbazole"]),
        field("deuterium_incorporation", {"number": 94, "unit": "%"}, p3, ["labeled_carbazole"]),
        field("deuterium_position", "3-position of the newly formed phenyl ring", p3, ["labeled_carbazole"]),
    ],
    unresolved=[
        "Reaction scale, solvent volume, atmosphere, workup, purification, and yield measurement basis are absent from pages 1-6.",
        "Isotopologue structures remain machine-unverified.",
    ],
))

records.append(record(
    "scheme3_proposed_pt_carbene_mechanism",
    "mechanism",
    p3,
    participants=[
        participant("mechanism_start", "reactant", p3, label="3f-D", name="deuterium-labeled allenol 3f-D"),
        participant("mechanism_ptcl2", "catalyst", p3, name="platinum(II) chloride"),
        participant("mechanism_product", "product", p3, label="4f-D", name="deuterium-labeled carbazole 4f-D"),
    ],
    notes=[
        "Proposed sequence: allene coordination and indolyl C3 attack, protonation/dehydration to cyclic vinylic platinum carbene M3, then 1,2-D shift to 4f-D."
    ],
    unresolved=[
        "M2 and M3 are proposed intermediates rather than separately observed experiments.",
        "No independent yields are assigned to mechanistic arrows.",
    ],
))


# Pages 3-5: indium-mediated preparations of 4-unsubstituted allenols.
def indium_allenol(rid, pages, product_label, product_name, aldehyde_name, aldehyde_mass, aldehyde_mmol,
                   indium_mass, indium_mmol, bromo_name, bromo_mass, bromo_mmol,
                   time_h, product_mass, yield_pct, purification):
    evidence = []
    for page in pages:
        evidence.extend(ev(page))
    ids = {name: f"{rid}_{name}" for name in ["aldehyde", "indium", "bromo", "nh4cl", "thf", "product"]}
    records.append(record(
        rid,
        "reported_experiment",
        evidence,
        participants=[
            participant(ids["aldehyde"], "reactant", evidence, name=aldehyde_name,
                        amounts=[amount("mass", aldehyde_mass, "g", evidence), amount("amount", aldehyde_mmol, "mmol", evidence)]),
            participant(ids["indium"], "reagent", evidence, name="indium",
                        amounts=[amount("mass", indium_mass, "g", evidence), amount("amount", indium_mmol, "mmol", evidence)]),
            participant(ids["bromo"], "reactant", evidence, name=bromo_name,
                        amounts=[amount("mass", bromo_mass, "g", evidence), amount("amount", bromo_mmol, "mmol", evidence)]),
            participant(ids["nh4cl"], "reagent", evidence, name="saturated aqueous ammonium chloride",
                        amounts=[amount("volume", 20, "mL", evidence)]),
            participant(ids["thf"], "solvent", evidence, name="tetrahydrofuran",
                        amounts=[amount("volume", 4, "mL", evidence)]),
            participant(ids["product"], "product", evidence, label=product_label, name=product_name,
                        amounts=[amount("isolated_mass", product_mass, "g", evidence)]),
        ],
        steps=[{
            "step_id": "indium_mediated_allenylation",
            "participant_ids": list(ids.values()),
            "conditions": [
                field("temperature", {"number": 0, "unit": "°C"}, evidence),
                field("time", {"number": time_h, "unit": "h"}, evidence),
                field("solvent", "THF/saturated aqueous NH4Cl", evidence),
                field("workup", "quenched with water where specified; extracted with diethyl ether; dried over Na2SO4; filtered and evaporated, following the stated typical procedure", evidence),
                field("purification", purification, evidence),
            ],
        }],
        outcomes=[
            field("isolated_yield", {"number": yield_pct, "unit": "%"}, evidence, [ids["product"]]),
            field("yield_measurement_basis", "isolated after chromatography", evidence, [ids["product"]]),
        ],
        unresolved=[
            "Complex reactant/product structures are retained by names/labels with null SMILES and remain machine-unverified.",
            "Atmosphere is not stated for this procedure.",
            "Supporting Information was not supplied or explicitly associated.",
        ],
    ))


indium_allenol("prep_1e", [3, 4], "1e", "1-(1-ethyl-1H-indol-2-yl)-2-(p-tolyl)buta-2,3-dien-1-ol",
               "1-ethyl-1H-indole-2-carbaldehyde", 0.8712, 5, 1.1421, 10,
               "1-bromo-3-(4-methylphenyl)prop-2-yne", 1.5812, 7.5, 10, 1.3094, 86,
               "silica-gel chromatography, petroleum ether/ethyl acetate 10:1")
indium_allenol("prep_1f", [4], "1f", "1-(1-ethyl-1H-indol-2-yl)-2-(4-methoxyphenyl)buta-2,3-dien-1-ol",
               "1-ethyl-1H-indole-2-carbaldehyde", 0.8701, 5, 1.1412, 10,
               "3-bromo-1-(4-methoxyphenyl)propyne", 1.6910, 7.5, 11, 1.1015, 69,
               "silica-gel chromatography, petroleum ether/ethyl acetate 10:1 to 5:1")
indium_allenol("prep_1j", [4], "1j", "2-(ethoxymethyl)-1-(1-ethyl-1H-indol-2-yl)buta-2,3-dien-1-ol",
               "1-ethyl-1H-indole-2-carbaldehyde", 0.8701, 5, 1.2104, 10,
               "1-bromo-4-ethoxybut-2-yne", 1.3402, 7.5, 17, 1.1099, 81,
               "silica-gel chromatography, petroleum ether/ethyl acetate 10:1 to 5:1")
indium_allenol("prep_1k", [4], "1k", "2-((1-ethyl-1H-indol-2-yl)(hydroxy)methyl)buta-2,3-dienyl acetate",
               "1-ethyl-1H-indole-2-carbaldehyde", 0.6954, 4, 1.1412, 10,
               "4-bromobut-2-ynyl acetate", 1.5612, 7.5, 20, 0.6988, 61,
               "silica-gel chromatography, petroleum ether/ethyl acetate 10:1 to 5:1")
indium_allenol("prep_1l", [4], "1l", "2-((1-ethyl-1H-indol-2-yl)(hydroxy)methyl)buta-2,3-dienyl methyl carbonate",
               "1-ethyl-1H-indole-2-carbaldehyde", 0.6752, 4, 1.2105, 10,
               "4-bromobut-2-ynyl methyl carbonate", 1.2452, 6.0, 11, 0.7103, 61,
               "silica-gel chromatography, petroleum ether/ethyl acetate 10:1 to 5:1")
indium_allenol("prep_1m", [4, 5], "1m", "1-(1-ethyl-4-methyl-1H-indol-2-yl)-2-butylbuta-2,3-dien-1-ol",
               "1-ethyl-4-methyl-1H-indole-2-carbaldehyde", 0.9359, 5, 1.1512, 10,
               "1-bromohept-2-yne", 1.3219, 7.5, 12, 1.1462, 81,
               "silica-gel chromatography, petroleum ether/ethyl acetate 20:1")
indium_allenol("prep_1u", [5], "1u", "1-(1-(4-methoxybenzyl)-1H-indol-2-yl)-2-phenylbuta-2,3-dien-1-ol",
               "1-(4-methoxybenzyl)-1H-indole-2-carbaldehyde", 0.9912, 4, 1.0125, 8,
               "3-bromo-1-phenylpropyne", 1.1925, 6, 10, 1.3000, 91,
               "silica-gel chromatography, petroleum ether/ethyl acetate 5:1 to 3:1")


p5 = ev(5)
records.append(record(
    "prep_1q",
    "reported_experiment",
    p5,
    participants=[
        participant("benzyloxyallene", "reactant", p5, name="benzyloxypropa-1,2-diene",
                    amounts=[amount("mass", 1.6012, "g", p5), amount("amount", 11, "mmol", p5)]),
        participant("n_buli", "reagent", p5, name="n-butyllithium",
                    amounts=[amount("solution_volume", 4, "mL", p5), amount("concentration", 2.5, "M", p5), amount("amount", 10, "mmol", p5)]),
        participant("aldehyde", "reactant", p5, name="1-ethyl-1H-indole-2-carbaldehyde",
                    amounts=[amount("mass", 1.7412, "g", p5), amount("amount", 10, "mmol", p5)]),
        participant("thf", "solvent", p5, name="tetrahydrofuran",
                    amounts=[amount("initial_volume", 30, "mL", p5), amount("aldehyde_solution_volume", 10, "mL", p5)]),
        participant("product_1q", "product", p5, label="1q", name="1-(1-ethyl-1H-indol-2-yl)-2-(benzyloxy)buta-2,3-dien-1-ol",
                    amounts=[amount("isolated_mass", 1.8125, "g", p5)]),
    ],
    steps=[{
        "step_id": "lithiated_allene_addition",
        "participant_ids": ["benzyloxyallene", "n_buli", "aldehyde", "thf", "product_1q"],
        "conditions": [
            field("temperature", {"number": -40, "unit": "°C"}, p5),
            field("n_buli_addition_time", {"number": 10, "unit": "min"}, p5),
            field("time", {"number": 50, "unit": "min"}, p5),
            field("aldehyde_addition_time", {"number": 20, "unit": "min"}, p5),
            field("warm_to", "r.t.", p5),
            field("atmosphere", "N2", p5),
            field("workup", "quenched with saturated aqueous NH4Cl (20 mL); extracted with diethyl ether (25 mL x3); water wash; K2CO3 drying; filtration and evaporation", p5),
            field("purification", "alkali-Al2O3 chromatography, petroleum ether/ethyl acetate 5:1 to 3:1", p5),
        ],
    }],
    outcomes=[
        field("isolated_yield", {"number": 57, "unit": "%"}, p5, ["product_1q"]),
        field("yield_measurement_basis", "isolated after chromatography", p5, ["product_1q"]),
    ],
    unresolved=["Complex substrate/product structures remain machine-unverified; elapsed warm-up time is not stated."],
))


p56 = ev(5) + ev(6)
two_stage_allenol(
    "prep_3c", [5], "8c", "THP-protected propargylic substrate 8c",
    [amount("mass", 1.1012, "g", p5), amount("amount", 6, "mmol", p5)],
    "1-ethyl-1H-indole-2-carbaldehyde",
    [amount("mass", 1.0354, "g", p5), amount("amount", 6, "mmol", p5)],
    [amount("solution_volume", 2.5, "mL", p5), amount("concentration", 2.5, "M", p5), amount("amount", 6, "mmol", p5)],
    [amount("substrate_solution_volume", 25, "mL", p5), amount("aldehyde_solution_volume", 5, "mL", p5)],
    "9c",
    [amount("mass", 0.2357, "g", p5), amount("amount", 6, "mmol", p5)],
    [amount("initial_volume", 25, "mL", p5), amount("intermediate_solution_volume", 5, "mL", p5)],
    "3c", "1-(1-ethyl-1H-indol-2-yl)-5-methylhexa-2,3-dien-1-ol", 0.6167, 40,
    [
        field("temperature", {"number": -78, "unit": "°C"}, p5),
        field("n_buli_addition_time", {"number": 10, "unit": "min"}, p5),
        field("time", {"number": 1, "unit": "h"}, p5),
        field("aldehyde_addition_time", {"number": 15, "unit": "min"}, p5),
        field("warm_to", "r.t.", p5),
        field("time_at_room_temperature", {"number": 3, "unit": "h"}, p5),
        field("atmosphere", "N2", p5),
    ],
    [
        field("initial_temperature", {"number": 0, "unit": "°C"}, p5),
        field("addition_time", {"number": 10, "unit": "min"}, p5),
        field("warm_to", "r.t.", p5),
        field("time_at_room_temperature", {"number": 1, "unit": "h"}, p5),
        field("atmosphere", "N2", p5),
        field("workup", "water quench; diethyl ether extraction (15 mL x3); Na2SO4 drying; filtration and evaporation", p5),
        field("purification", "silica-gel chromatography, petroleum ether/ethyl acetate 10:1", p5),
    ],
)


p6 = ev(6)
two_stage_allenol(
    "prep_3h", [6], "8a", "THP-protected propargylic substrate 8a",
    [amount("mass", 0.8315, "g", p6), amount("amount", 5, "mmol", p6)],
    "1-ethyl-4-methyl-1H-indole-2-carbaldehyde",
    [amount("mass", 0.9412, "g", p6), amount("amount", 5, "mmol", p6)],
    [amount("solution_volume", 2, "mL", p6), amount("concentration", 2.5, "M", p6), amount("amount", 5, "mmol", p6)],
    [amount("substrate_solution_volume", 35, "mL", p6), amount("aldehyde_solution_volume", 5, "mL", p6)],
    "9h", [amount("mass", 0.2001, "g", p6), amount("amount", 5, "mmol", p6)],
    [amount("volume", 30, "mL", p6)],
    "3h", "1-(1-ethyl-4-methyl-1H-indol-2-yl)penta-2,3-dien-1-ol", 0.4047, 34,
    [
        field("temperature", {"number": -78, "unit": "°C"}, p6),
        field("n_buli_addition_and_stirring_time", {"number": 65, "unit": "min", "raw_text": "5+60 min"}, p6),
        field("aldehyde_addition_time", {"number": 15, "unit": "min"}, p6),
        field("warm_to", "r.t.", p6),
        field("time_at_room_temperature", {"number": 2.5, "unit": "h"}, p6),
    ],
    [
        field("initial_temperature", {"number": 0, "unit": "°C"}, p6),
        field("addition_time", {"number": 10, "unit": "min"}, p6),
        field("warm_to", "r.t.", p6),
        field("time_at_room_temperature", {"number": 10, "unit": "h"}, p6),
        field("purification", "silica-gel chromatography, petroleum ether/ethyl acetate 10:1 to 5:1", p6),
    ],
)

two_stage_allenol(
    "prep_3i", [5, 6], "8f", "THP-protected propargylic substrate 8f",
    [amount("mass", 0.9124, "g", p56), amount("amount", 4, "mmol", p56)],
    "1-ethyl-4-methyl-1H-indole-2-carbaldehyde",
    [amount("mass", 0.7412, "g", p56), amount("amount", 4, "mmol", p56)],
    [amount("solution_volume", 1.7, "mL", p56), amount("concentration", 2.5, "M", p56), amount("amount", 4, "mmol", p56)],
    [amount("substrate_solution_volume", 25, "mL", p56), amount("aldehyde_solution_volume", 5, "mL", p56)],
    "9i", [amount("mass", 0.1565, "g", p56), amount("amount", 4, "mmol", p56)],
    [amount("volume", 30, "mL", p56)],
    "3i", "1-(1-ethyl-4-methyl-1H-indol-2-yl)deca-2,3-dien-1-ol", 0.3860, 31,
    [field("operation", "prepared according to the preceding 3c typical procedure", p56), field("temperature", None, p56), field("time", None, p56)],
    [field("operation", "LiAlH4 reduction according to the preceding typical procedure", p56), field("temperature", None, p56), field("time", None, p56), field("purification", "silica-gel chromatography, petroleum ether/ethyl acetate 10:1", p56)],
    inherited=True,
)

two_stage_allenol(
    "prep_3j", [6], "8f", "THP-protected propargylic substrate 8f",
    [amount("mass", 0.4601, "g", p6), amount("amount", 2, "mmol", p6)],
    "1-ethyl-5-bromo-1H-indole-2-carbaldehyde",
    [amount("mass", 0.5035, "g", p6), amount("amount", 2, "mmol", p6)],
    [amount("solution_volume", 0.8, "mL", p6), amount("concentration", 2.5, "M", p6), amount("amount", 2, "mmol", p6)],
    [amount("substrate_solution_volume", 10, "mL", p6), amount("aldehyde_solution_volume", 5, "mL", p6)],
    "9j", [amount("mass", 0.0891, "g", p6), amount("amount", 2, "mmol", p6)],
    [amount("volume", 20, "mL", p6)],
    "3j", "1-(5-bromo-1-ethyl-1H-indol-2-yl)deca-2,3-dien-1-ol", 0.2297, 31,
    [
        field("temperature", {"number": -78, "unit": "°C"}, p6),
        field("n_buli_addition_and_stirring_time", {"number": 65, "unit": "min", "raw_text": "5+60 min"}, p6),
        field("aldehyde_addition_time", {"number": 5, "unit": "min"}, p6),
        field("warm_to", "r.t.", p6),
        field("time_at_room_temperature", {"number": 2.5, "unit": "h"}, p6),
    ],
    [
        field("initial_temperature", {"number": 0, "unit": "°C"}, p6),
        field("addition_time", {"number": 20, "unit": "min"}, p6),
        field("warm_to", "r.t.", p6),
        field("time_at_room_temperature", {"number": 3.5, "unit": "h"}, p6),
        field("purification", "silica-gel chromatography, petroleum ether/ethyl acetate 10:1 to 5:1", p6),
    ],
)


out = Path(__file__).with_name("records_pages_0001_0006.json")
out.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")


page_record_ids = {page: [] for page in range(1, 7)}
for item in records:
    for page in range(1, 7):
        if f"{DOC}:page{page}:image" in item["evidence_ids"]:
            page_record_ids[page].append(item["record_id"])

coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1,
            "state": "attempted",
            "regions": [
                {
                    "region": "page 1 lower-right, Scheme 1 and adjacent Introduction text",
                    "finding": "Prior-literature carbazole synthesis overview; classified as a general scheme, not a reported experiment of this paper.",
                    "evidence_ids": ev(1),
                },
                {
                    "region": "page 1 title, abstract, and ESI footnote",
                    "finding": "Article metadata and high-level reaction claim only; the footnote mentions ESI, but no SI file was supplied or associated.",
                    "evidence_ids": ev(1),
                },
            ],
            "record_ids": page_record_ids[1],
            "unresolved": ["Generic structures in Scheme 1 do not define unique experimental records; SI association remains unestablished."],
        },
        {
            "page": 2,
            "state": "attempted",
            "regions": [
                {
                    "region": "page 2 upper-left, Table 1 reaction drawing, rows 1-21, and isolated-yield footnote",
                    "finding": "Twenty-one distinct PtCl2-catalyzed cyclization scope experiments, retained one row per experiment with row-specific time and isolated yield.",
                    "evidence_ids": ev(2),
                },
                {
                    "region": "page 2 upper-right, Table 2 reaction drawing, rows 1-12, and isolated-yield footnote",
                    "finding": "Twelve distinct 4-monosubstituted allenol cyclization scope experiments, retained one row per experiment.",
                    "evidence_ids": ev(2),
                },
                {
                    "region": "page 2 lower prose discussion",
                    "finding": "Narrative interpretation of Tables 1-2 and mechanistic-study lead-in; no extra scope experiment beyond the 33 table rows.",
                    "evidence_ids": ev(2),
                },
            ],
            "record_ids": page_record_ids[2],
            "unresolved": ["Table rows omit reaction scale, exact temperature, atmosphere, solvent volume, workup, purification, and fully resolved structures."],
        },
        {
            "page": 3,
            "state": "attempted",
            "regions": [
                {
                    "region": "page 3 upper-left, Scheme 2",
                    "finding": "Preparation sequence for labeled precursor 3f-D: oxidation, LiAlD4 reduction, THP protection, and a two-stage allenol synthesis; arrows were reconciled with the detailed experimental text.",
                    "evidence_ids": ev(3),
                },
                {
                    "region": "page 3 center-left, 3f-D to 4f-D arrow and mechanistic prose",
                    "finding": "Distinct deuterium-labeling cyclization experiment: PtCl2 (5 mol%), toluene, room temperature, 2 h, 86% yield, 94% D in product.",
                    "evidence_ids": ev(3),
                },
                {
                    "region": "page 3 lower-left, Scheme 3",
                    "finding": "Proposed platinum-carbene mechanism with M2/M3; classified separately and not treated as independent observed reactions.",
                    "evidence_ids": ev(3),
                },
                {
                    "region": "page 3 right column, Experimental Section 1 and start of Section 2",
                    "finding": "Detailed oxidation to 1-nonyn-3-one and LiAlD4 reduction to 3-deutero-1-nonyn-3-ol; the 1e procedure begins at the page bottom and continues on page 4.",
                    "evidence_ids": ev(3),
                },
            ],
            "record_ids": page_record_ids[3],
            "unresolved": ["Several Scheme 2 arrows omit scale or operational details; proposed intermediates are not experimentally isolated."],
        },
        {
            "page": 4,
            "state": "attempted",
            "regions": [
                {
                    "region": "page 4 left column upper, completion of typical 1e procedure",
                    "finding": "Detailed indium-mediated preparation of allenol 1e, merged with its page-3 opening text.",
                    "evidence_ids": ev(4),
                },
                {
                    "region": "page 4 remaining two columns, preparations 1f, 1j, 1k, 1l, and start of 1m",
                    "finding": "Five complete allenol preparations plus the beginning of the cross-page 1m preparation; each product is a distinct experiment under the stated typical procedure.",
                    "evidence_ids": ev(4),
                },
            ],
            "record_ids": page_record_ids[4],
            "unresolved": ["Candidate SMILES for complex allenols were not considered verified; atmosphere is not stated for the indium procedure."],
        },
        {
            "page": 5,
            "state": "attempted",
            "regions": [
                {
                    "region": "page 5 upper-left, completion of preparation 1m",
                    "finding": "Cross-page 1m experiment completed with 12 h reaction time, 1.1462 g product, and 81% yield.",
                    "evidence_ids": ev(5),
                },
                {
                    "region": "page 5 left column center/lower, preparations 1u and 1q",
                    "finding": "Distinct preparations of allenols 1u (indium-mediated, 91%) and 1q (n-BuLi-mediated, 57%).",
                    "evidence_ids": ev(5),
                },
                {
                    "region": "page 5 right column, Section 4 typical procedure and two arrows for 8c to 9c to 3c",
                    "finding": "Two-stage preparation of 3c with an unpurified intermediate and a 40% combined isolated yield; stages retained within one experiment record.",
                    "evidence_ids": ev(5),
                },
            ],
            "record_ids": page_record_ids[5],
            "unresolved": ["Intermediate 9c has no separate yield; 3i later cross-references this typical procedure without restating entry-specific durations."],
        },
        {
            "page": 6,
            "state": "attempted",
            "regions": [
                {
                    "region": "page 6 upper-left, preparation 3f-D and its two-arrow scheme",
                    "finding": "Two-stage preparation of labeled allenol 3f-D, merged with Scheme 2 on page 3; 50% combined yield and 98% D.",
                    "evidence_ids": ev(6),
                },
                {
                    "region": "page 6 lower-left and upper-right, preparation 3h and its two-arrow scheme",
                    "finding": "Two-stage preparation of 3h with 34% combined yield and entry-specific timing shown in the scheme.",
                    "evidence_ids": ev(6),
                },
                {
                    "region": "page 6 center-right, preparation 3i",
                    "finding": "Two-stage preparation of 3i with 31% combined yield; precise entry-specific durations are not restated and remain missing.",
                    "evidence_ids": ev(6),
                },
                {
                    "region": "page 6 lower-right, preparation 3j and two-arrow scheme",
                    "finding": "Two-stage preparation of 3j with 31% combined yield; characterization continues beyond the current page range but is not needed to identify the experiment.",
                    "evidence_ids": ev(6),
                },
            ],
            "record_ids": page_record_ids[6],
            "unresolved": ["3i entry-specific time/temperature are not locally restated; complex structures remain machine-unverified; page-7 characterization was not claimed as covered."],
        },
    ],
}

coverage_path = BASE / "coverage" / "pages_0001_0006.json"
coverage_path.parent.mkdir(parents=True, exist_ok=True)
coverage_path.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

tasks_path = BASE / "tasks.json"
tasks = json.loads(tasks_path.read_text())
for task in tasks:
    if task["document_id"] == DOC and any(task["evidence_id"] == f"{DOC}:page{p}:text" for p in range(1, 7)):
        task["state"] = "attempted"
        task["reason"] = "Original page image visually inspected and page inventory recorded in coverage/pages_0001_0006.json."
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"records": len(records), "coverage_pages": len(coverage["pages"]), "output": str(out)}, ensure_ascii=False))
