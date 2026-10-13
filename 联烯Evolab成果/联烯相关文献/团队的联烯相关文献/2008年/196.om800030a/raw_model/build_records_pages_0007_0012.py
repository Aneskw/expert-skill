#!/usr/bin/env python3
"""Build evidence-linked records for PDF pages 7-12 and cross-page continuations."""

import copy
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CURRENT = ROOT / "runs" / "current"
DOC = "doc_9ba0460dd1a6041e"


def ev(page, kind="text"):
    return f"{DOC}:page{page}:{kind}"


def page(page_number):
    return (ev(page_number, "text"), ev(page_number, "image"))


def fact(value, evidence=()):
    return {
        "value": value,
        "evidence_ids": list(dict.fromkeys(evidence)),
        "verification": "missing" if value is None else "unreviewed",
    }


def field(name, value, evidence=(), targets=()):
    result = {"name": name, "fact": fact(value, evidence)}
    if targets:
        result["target_entity_ids"] = list(targets)
    return result


def quantity(name, number, unit, evidence):
    return field(name, {"number": number, "unit": unit}, evidence)


def participant(entity_id, role, label, name, evidence, smiles=None, amounts=()):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence),
        "smiles": fact(smiles, evidence if smiles is not None else ()),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": list(amounts),
    }


def record(rid, source_id, kind, evidence, participants, steps, outcomes, notes, unresolved):
    return {
        "record_id": f"{DOC}:{rid}",
        "document_id": DOC,
        "source_reaction_id": source_id,
        "record_kind": kind,
        "status": "needs_review",
        "completeness": "partial",
        "evidence_ids": list(dict.fromkeys(evidence)),
        "participants": participants,
        "steps": steps,
        "outcomes": outcomes,
        "notes": [fact(text, evidence_ids) for text, evidence_ids in notes],
        "review": {
            "method": "model",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": list(unresolved),
        },
    }


def set_field(fields, name, value, evidence, targets=()):
    fields[:] = [item for item in fields if item["name"] != name]
    fields.append(field(name, value, evidence, targets))


def set_condition(rec, name, value, evidence):
    set_field(rec["steps"][0]["conditions"], name, value, evidence)


def add_evidence(rec, evidence):
    rec["evidence_ids"] = list(dict.fromkeys(rec["evidence_ids"] + list(evidence)))


def get_participant(rec, entity_id):
    return next(item for item in rec["participants"] if item["entity_id"] == entity_id)


def set_amounts(rec, entity_id, amounts):
    get_participant(rec, entity_id)["amounts"] = list(amounts)


def add_participant(rec, item):
    if not any(existing["entity_id"] == item["entity_id"] for existing in rec["participants"]):
        rec["participants"].append(item)
        rec["steps"][0]["participant_ids"].append(item["entity_id"])


P7, P8, P9, P10, P11, P12 = (page(n) for n in range(7, 13))
P13_TEXT = (ev(13, "text"),)
dataset = json.loads((CURRENT / "dataset.json").read_text())
existing = {item["record_id"]: item for item in dataset["experiments"]}
records = []


# Complete the seven present-paper insertion records already created from pages 1-6.
procedure_specs = {
    "scheme2_1_2_to_3": {
        "extra_evidence": P9 + P11,
        "reactants": {
            "r3_complex1": [("mass", 151, "mg"), ("amount", 0.130, "mmol")],
            "r3_allene2": [("volume", 0.040, "mL"), ("amount", 0.32, "mmol")],
            "r3_dcm": [("volume", 8, "mL")],
        },
        "conditions": {
            "solvent": "dichloromethane",
            "temperature": "r.t.",
            "reaction_time": {"number": 30, "unit": "min"},
            "atmosphere": "argon",
            "workup": "concentrated to dryness; residue washed with diethyl ether (3 mL x 3); dried under vacuum",
            "purification": "washing/precipitation; no chromatography reported",
        },
        "targets": ("r3_product3",),
        "yield": 76,
        "mass": (0.14, "g"),
        "unresolved": ["The organopalladium product has no source-verified SMILES; no associated SI was supplied."],
    },
    "scheme2_1_4_to_5": {
        "extra_evidence": P9 + P11,
        "reactants": {
            "scheme2_1_4_to_5_complex1": [("mass", 233, "mg"), ("amount", 0.20, "mmol")],
            "scheme2_1_4_to_5_allene": [("mass", 0.040, "g"), ("amount", 0.42, "mmol")],
            "scheme2_1_4_to_5_dcm": [("volume", 5, "mL")],
        },
        "add": [("scheme2_1_4_to_5_benzene", "solvent", "benzene", "benzene", "c1ccccc1", [("volume", 10, "mL")])],
        "conditions": {
            "solvent": "benzene (10 mL) and dichloromethane (5 mL)",
            "temperature": "r.t.",
            "reaction_time": {"number": 2, "unit": "h"},
            "atmosphere": "argon",
            "workup": "concentrated to dryness under vacuum; diethyl ether (4 mL) added to precipitate product; filtered; washed with ether (2 mL x 2); dried under vacuum",
            "purification": "precipitation and washing",
        },
        "targets": ("scheme2_1_4_to_5_trans_5", "scheme2_1_4_to_5_cis_5"),
        "yield": 84,
        "mass": (0.23, "g"),
        "unresolved": ["The two organopalladium product structures have no source-verified SMILES; no associated SI was supplied."],
    },
    "scheme2_1_6_to_7": {
        "extra_evidence": P9 + P11,
        "reactants": {
            "scheme2_1_6_to_7_complex1": [("mass", 225, "mg"), ("amount", 0.200, "mmol")],
            "scheme2_1_6_to_7_allene": [("mass", 0.050, "g"), ("amount", 0.44, "mmol")],
        },
        "remove": ("scheme2_1_6_to_7_dcm",),
        "add": [("scheme2_1_6_to_7_benzene", "solvent", "benzene", "benzene", "c1ccccc1", [("volume", 10, "mL")])],
        "conditions": {
            "solvent": "benzene",
            "temperature": "r.t.",
            "reaction_time": {"number": 2, "unit": "h"},
            "atmosphere": "argon",
            "workup": "concentrated to dryness; diethyl ether (2 mL) added; solid filtered; washed with hexane (2 mL x 3); dried under vacuum",
            "purification": "precipitation and washing",
        },
        "targets": ("scheme2_1_6_to_7_trans_7", "scheme2_1_6_to_7_cis_7"),
        "yield": 80,
        "mass": (0.22, "g"),
        "unresolved": ["The two organopalladium product structures have no source-verified SMILES; no associated SI was supplied."],
    },
    "scheme3_1_8_to_9": {
        "extra_evidence": P9 + P11,
        "reactants": {
            "scheme3_1_8_to_9_complex1": [("mass", 50, "mg"), ("amount", 0.0435, "mmol")],
            "scheme3_1_8_to_9_allene": [("mass", 19, "mg"), ("amount", 0.107, "mmol")],
            "scheme3_1_8_to_9_dcm": [("volume", 2, "mL")],
        },
        "conditions": {
            "solvent": "dichloromethane",
            "temperature": "r.t.",
            "reaction_time": {"number": 8, "unit": "h"},
            "atmosphere": "argon",
            "workup": "concentrated to dryness under vacuum; residue treated with ether (3 mL x 2); solid filtered; washed with ether (3 mL); dried under vacuum",
            "purification": "precipitation and washing",
        },
        "targets": ("scheme3_1_8_to_9_trans_9", "scheme3_1_8_to_9_cis_9"),
        "yield": 63,
        "mass": (41, "mg"),
        "unresolved": ["The two organopalladium product structures have no source-verified SMILES; no associated SI was supplied."],
    },
    "scheme3_1_10_to_11": {
        "extra_evidence": P7 + P9 + P11,
        "reactants": {
            "scheme3_1_10_to_11_complex1": [("mass", 203, "mg"), ("amount", 0.177, "mmol")],
            "scheme3_1_10_to_11_allene": [("mass", 81, "mg"), ("amount", 0.426, "mmol")],
            "scheme3_1_10_to_11_dcm": [("volume", 10, "mL")],
        },
        "conditions": {
            "solvent": "dichloromethane",
            "temperature": "r.t.",
            "reaction_time": {"number": 10, "unit": "h"},
            "atmosphere": "argon",
            "workup": "concentrated to dryness under vacuum; residue treated with n-hexane (6 mL x 2); solid filtered; washed with n-hexane (6 mL); dried under vacuum",
            "purification": "precipitation and washing",
        },
        "targets": ("scheme3_1_10_to_11_trans_11", "scheme3_1_10_to_11_cis_11"),
        "yield": 70,
        "mass": (186, "mg"),
        "unresolved": ["The Results section gives trans/cis = 1:4.3, while the Experimental section gives 1:4; both source values are retained.", "The two organopalladium product structures have no source-verified SMILES; no associated SI was supplied."],
    },
    "scheme3_1_12_to_13": {
        "extra_evidence": P7 + P9 + P11,
        "reactants": {
            "scheme3_1_12_to_13_complex1": [("mass", 500, "mg"), ("amount", 0.435, "mmol")],
            "scheme3_1_12_to_13_allene": [("mass", 200, "mg"), ("amount", 1.11, "mmol")],
            "scheme3_1_12_to_13_dcm": [("volume", 30, "mL")],
        },
        "conditions": {
            "solvent": "dichloromethane",
            "temperature": "r.t.",
            "reaction_time": {"number": 3, "unit": "h"},
            "atmosphere": "argon",
            "workup": "concentrated to dryness under vacuum; residue treated with ether (25 mL x 2); solid filtered; washed with n-hexane (25 mL); dried under vacuum",
            "purification": "precipitation and washing",
        },
        "targets": ("scheme3_1_12_to_13_trans_13", "scheme3_1_12_to_13_cis_13"),
        "yield": 90,
        "mass": (590, "mg"),
        "unresolved": ["The two organopalladium product structures have no source-verified SMILES; no associated SI was supplied."],
    },
    "scheme3_1_14_to_15": {
        "extra_evidence": P7 + P9 + P11 + P12,
        "reactants": {
            "scheme3_1_14_to_15_complex1": [("mass", 2.00, "g"), ("amount", 1.746, "mmol")],
            "scheme3_1_14_to_15_allene": [("mass", 712, "mg"), ("amount", 3.67, "mmol")],
            "scheme3_1_14_to_15_dcm": [("volume", 60, "mL")],
        },
        "conditions": {
            "solvent": "dichloromethane",
            "temperature": "r.t.",
            "reaction_time": {"number": 8, "unit": "h"},
            "atmosphere": "argon",
            "workup": "concentrated to dryness under vacuum; residue treated with n-hexane (35 mL x 2); solid filtered; washed with n-hexane (35 mL); dried under vacuum",
            "purification": "precipitation and washing",
        },
        "targets": ("scheme3_1_14_to_15_cis_15",),
        "yield": 97,
        "mass": (2.628, "g"),
        "unresolved": ["Elemental analysis indicates dichloromethane in the sample; the organopalladium product has no source-verified SMILES and no associated SI was supplied."],
    },
}


for suffix, spec in procedure_specs.items():
    rec = copy.deepcopy(existing[f"{DOC}:{suffix}"])
    add_evidence(rec, spec["extra_evidence"])
    for entity_id in spec.get("remove", ()):
        rec["participants"] = [item for item in rec["participants"] if item["entity_id"] != entity_id]
        for step in rec["steps"]:
            step["participant_ids"] = [item for item in step["participant_ids"] if item != entity_id]
    for entity_id, amounts in spec["reactants"].items():
        set_amounts(rec, entity_id, [quantity(name, number, unit, P11) for name, number, unit in amounts])
    for entity_id, role, label, name, smiles, amounts in spec.get("add", ()):
        add_participant(rec, participant(entity_id, role, label, name, P11, smiles, [quantity(n, v, u, P11) for n, v, u in amounts]))
    for name, value in spec["conditions"].items():
        evidence = P9 if name == "atmosphere" else P11 + (P12 if suffix == "scheme3_1_14_to_15" and name in ("workup", "purification") else ())
        set_condition(rec, name, value, evidence)
    set_field(rec["outcomes"], "isolated_yield", {"number": spec["yield"], "unit": "%"}, P11 + (P12 if suffix == "scheme3_1_14_to_15" else ()), spec["targets"])
    set_field(rec["outcomes"], "yield_measurement_basis", "isolated after the reported workup", P11 + (P12 if suffix == "scheme3_1_14_to_15" else ()))
    set_field(rec["outcomes"], "isolated_product_mass", {"number": spec["mass"][0], "unit": spec["mass"][1]}, P11 + (P12 if suffix == "scheme3_1_14_to_15" else ()), spec["targets"])
    if suffix == "scheme3_1_10_to_11":
        for item in rec["outcomes"]:
            if item["name"] == "trans_to_cis_ratio":
                item["name"] = "results_section_trans_to_cis_ratio"
        rec["outcomes"].append(field("experimental_section_trans_to_cis_ratio", "1:4", P11, spec["targets"]))
    if suffix == "scheme3_1_14_to_15":
        set_field(rec["outcomes"], "substituent_orientation", "SO2Ph is anti to Ph and Me is syn to Ph", P7, spec["targets"])
        rec["notes"].append(fact("The isolated analytical sample contains dichloromethane according to 1H NMR and elemental analysis.", P12))
    rec["review"]["unresolved"] = spec["unresolved"]
    rec["completeness"] = "partial"
    records.append(rec)


# Four explicitly different no-reaction controls: two allenes in each of two solvents.
for substrate_key, substrate_label, substrate_name, substrate_smiles in (
    ("12", "CH2=C=CHSO2Ph", "(propa-1,2-dienylsulfonyl)benzene", "C=C=CS(=O)(=O)c1ccccc1"),
    ("14", "MeCH=C=CHSO2Ph", "(buta-1,2-dienylsulfonyl)benzene", "CC=C=CS(=O)(=O)c1ccccc1"),
):
    for solvent_key, solvent_name, solvent_smiles in (
        ("benzene", "benzene", "c1ccccc1"),
        ("dcm", "dichloromethane", "ClCCl"),
    ):
        rid = f"control_16_{substrate_key}_{solvent_key}_no_reaction"
        complex_id = f"{rid}_complex16"
        allene_id = f"{rid}_allene"
        solvent_id = f"{rid}_solvent"
        parts = [
            participant(complex_id, "reactant", "16", "PdI(Ph)(dppe)", P7),
            participant(allene_id, "reactant", substrate_key, substrate_name, P7, substrate_smiles),
            participant(solvent_id, "solvent", solvent_name, solvent_name, P7 + P8, solvent_smiles),
        ]
        records.append(record(
            rid,
            f"Control: 16 + allene {substrate_key} in {solvent_name}",
            "reported_experiment",
            P7 + P8 + P9,
            parts,
            [{
                "step_id": "nmr_monitored_no_reaction_control",
                "participant_ids": [complex_id, allene_id, solvent_id],
                "conditions": [
                    field("reactant_molar_ratio", "1:2 (16:allene)", P7 + P8),
                    field("solvent", solvent_name, P7 + P8),
                    field("temperature", "r.t.", P7 + P8),
                    field("reaction_time", {"number": 12, "unit": "h"}, P7 + P8),
                    field("atmosphere", "argon", P9),
                    field("analytical_monitoring", "in situ 31P{1H} NMR", P7),
                    field("workup", None),
                    field("purification", None),
                ],
            }],
            [field("reaction_result", "no appreciable reaction", P7 + P8)],
            [("The source reports a failed insertion control rather than an isolated product.", P7 + P8)],
            ["The source does not give absolute reagent quantities, workup, purification, conversion, or a detection limit for 'no appreciable reaction'."],
        ))


# Computational mechanism: one mechanism record covers Scheme 6 and the Figure 7 pathways.
mech_parts = [
    participant("scheme6_22a", "reactant", "22A", "model precursor complex 22A", P8 + P9),
    participant("scheme6_22b", "reactant", "22B", "model precursor complex 22B", P8 + P9),
    participant("scheme6_22c", "reactant", "22C", "model precursor complex 22C", P8 + P9),
    participant("scheme6_22d", "reactant", "22D", "model precursor complex 22D", P8 + P9),
    participant("scheme6_trans24", "product", "trans-24", "model eta3-allyl complex trans-24", P8 + P10),
    participant("scheme6_cis24", "product", "cis-24", "model eta3-allyl complex cis-24", P8 + P10),
]
records.append(record(
    "scheme6_figure7_computational_pathways",
    "Scheme 6 and Figure 7",
    "mechanism",
    P8 + P9 + P10,
    mech_parts,
    [{
        "step_id": "computed_allene_insertion_pathways",
        "participant_ids": [item["entity_id"] for item in mech_parts],
        "conditions": [
            field("model_complex", "PdI(Ph)(eta2-MeCH=C=CHSO2H)(PH3)", P8 + P10),
            field("reaction_time", None),
            field("temperature", None),
        ],
    }],
    [
        field("calculated_pathway_result", "22A -> 23A -> trans-24 -> cis-24 is reported as the thermodynamically and kinetically most favorable pathway", P8),
        field("figure7_relative_free_and_electronic_energies", "Figure 7 reports relative free energies and electronic energies (parentheses) in kcal/mol for eight allyl/vinyl pathways", P9 + P10),
        field("ph3_model_relative_electronic_energies", "22A 0.0; TSA-prime 14.7; TSA 6.7; trans-24 -39.7; cis-24 -45.4 kcal/mol", P9),
        field("pph3_model_relative_electronic_energies", "22A 0.0; TSA-prime 17.8; TSA 9.8; trans-24 -40.3; cis-24 -45.3 kcal/mol", P9),
    ],
    [("This is a computational mechanism/model, not a wet-chemistry experiment and not an isolated set of intermediates.", P8 + P9 + P10)],
    ["The schema does not support kcal/mol as a structured quantity unit; source energy lists are preserved verbatim as unreviewed text.", "Model-complex structures and transition-state connectivities remain unverified."],
))


# Preparation of precursor complex 16.
prep16_parts = [
    participant("prep16_pdpph34", "reactant", "Pd(PPh3)4", "tetrakis(triphenylphosphine)palladium(0)", P12, amounts=[quantity("mass", 0.500, "g", P12), quantity("amount", 0.433, "mmol", P12)]),
    participant("prep16_dppe", "reactant", "Ph2PCH2CH2PPh2", "1,2-bis(diphenylphosphino)ethane (dppe)", P12, amounts=[quantity("mass", 175, "mg", P12), quantity("amount", 0.44, "mmol", P12)]),
    participant("prep16_phi", "reactant", "PhI", "iodobenzene", P12, "Ic1ccccc1", [quantity("volume", 0.056, "mL", P12), quantity("amount", 0.50, "mmol", P12)]),
    participant("prep16_benzene", "solvent", "benzene", "benzene", P12, "c1ccccc1", [quantity("volume", 12, "mL", P12)]),
    participant("prep16_product", "product", "16", "PdI(Ph)(dppe)", P7 + P12),
]
records.append(record(
    "preparation_complex16",
    "Experimental: preparation of PdI(Ph)(dppe) (16)",
    "reported_experiment",
    P7 + P9 + P12,
    prep16_parts,
    [
        {"step_id": "ligand_substitution", "participant_ids": ["prep16_pdpph34", "prep16_dppe", "prep16_benzene"], "conditions": [field("solvent", "benzene", P12), field("reaction_time", {"number": 1, "unit": "h"}, P12), field("temperature", None), field("atmosphere", "argon", P9)]},
        {"step_id": "oxidative_addition_and_crystallization", "participant_ids": ["prep16_phi", "prep16_product"], "conditions": [field("operation", "PhI added at room temperature; stirred for a further 10 min; then stood overnight without agitation", P12), field("temperature", "r.t.", P12), field("reaction_time", {"number": 10, "unit": "min"}, P12), field("standing_time", "overnight", P12), field("workup", "yellow crystallites filtered, washed with diethyl ether (2 mL x 3), and dried under vacuum", P12), field("purification", "crystallization from the reaction mixture", P12)]},
    ],
    [field("isolated_yield", {"number": 71, "unit": "%"}, P12, ("prep16_product",)), field("yield_measurement_basis", "isolated", P12), field("isolated_product_mass", {"number": 0.22, "unit": "g"}, P12, ("prep16_product",))],
    [("The source states that the NMR data are identical to literature reference 44; this preparation is nevertheless reported in the present Experimental section.", P12)],
    ["The product organopalladium structure has no source-verified SMILES; no associated SI was supplied."],
))


def insertion_record(number, allene_label, allene_name, allene_smiles, allene_mass, allene_amount,
                     tl_mass, tl_amount, acetone_volume, time_value, product_mass, product_yield,
                     evidence, workup, unresolved=()):
    rid = f"scheme_dppex_tlpf6_to_{number}pf6"
    complex_id, allene_id, tl_id = f"{rid}_complex16", f"{rid}_allene", f"{rid}_tlpf6"
    dcm_id, acetone_id, product_id = f"{rid}_dcm", f"{rid}_acetone", f"{rid}_product"
    parts = [
        participant(complex_id, "reactant", "16", "PdI(Ph)(dppe)", evidence, amounts=[quantity("mass", 190, "mg", evidence), quantity("amount", 0.268, "mmol", evidence)]),
        participant(allene_id, "reactant", allene_label, allene_name, evidence, allene_smiles, [quantity("mass", allene_mass, "mg", evidence), quantity("amount", allene_amount, "mmol", evidence)]),
        participant(tl_id, "reagent", "TlPF6", "thallium hexafluorophosphate", evidence, amounts=[quantity("mass", tl_mass, "mg", evidence), quantity("amount", tl_amount, "mmol", evidence)]),
        participant(dcm_id, "solvent", "CH2Cl2", "dichloromethane", evidence, "ClCCl", [quantity("volume", 8, "mL", evidence)]),
        participant(acetone_id, "solvent", "acetone", "acetone", evidence, "CC(=O)C", [quantity("volume", acetone_volume, "mL", evidence)]),
        participant(product_id, "product", f"{number}PF6", f"cationic eta3-allyl palladium complex {number}PF6", P8 + evidence),
    ]
    outcomes = []
    if product_yield is None:
        outcomes += [field("product_yield", None), field("yield_measurement_basis", None)]
    else:
        outcomes += [field("isolated_yield", {"number": product_yield, "unit": "%"}, evidence, (product_id,)), field("yield_measurement_basis", "isolated", evidence), field("isolated_product_mass", {"number": product_mass, "unit": "g"}, evidence, (product_id,))]
    conditions = [field("solvent", f"dichloromethane with TlPF6 added in acetone", evidence), field("temperature", None), field("reaction_time", {"number": time_value[0], "unit": time_value[1]}, evidence), field("atmosphere", "argon", P9), field("workup", workup, evidence), field("purification", "filtration/washing; no chromatography reported" if number != 21 else None, evidence if number != 21 else ())]
    return record(rid, f"Scheme {'4' if number in (17,18,19) else '5'}: 16 + {allene_label} + TlPF6 -> {number}PF6", "reported_experiment", P8 + P9 + evidence, parts, [{"step_id": "cationic_allene_insertion", "participant_ids": [item["entity_id"] for item in parts], "conditions": conditions}], outcomes, [("TlPF6 is an explicit reagent for iodide abstraction and is retained as a participant rather than only in notes.", P8 + evidence)], list(unresolved) + ["Reaction temperature is not stated in the covered source pages.", "The organopalladium product has no source-verified SMILES; no associated SI was supplied."])


records.extend([
    insertion_record(17, "tert-butylallene", "tert-butylallene", "C=C=CC(C)(C)C", 27, 0.28, 96, 0.28, 2, (30, "min"), 0.18, 82, P12, "concentrated to dryness; CH2Cl2 (5 mL) added; filtered through Celite and washed with CH2Cl2 (1 mL); filtrates concentrated; residue washed with ether (2 mL x 3); dried under vacuum"),
    insertion_record(18, "ethyl 2,3-butadienoate", "ethyl 2,3-butadienoate", "C=C=CC(=O)OCC", 31, 0.28, 96, 0.28, 1.5, (30, "min"), 0.22, 96, P12, "solvents removed; CH2Cl2 (5 mL) added; filtered through Celite and washed with CH2Cl2 (1 mL); filtrates concentrated; residue washed with hexane (2 mL x 2) and hexane/ether (5 mL, 2/3 v/v); dried under vacuum"),
    insertion_record(19, "1-phenylbuta-2,3-dien-1-one", "1-phenylbuta-2,3-dien-1-one", "C=C=CC(=O)c1ccccc1", 43, 0.29, 96, 0.28, 2, (2, "h"), 0.15, 64, P12, "concentrated to dryness; CH2Cl2 (5 mL) added; filtered through Celite and washed with CH2Cl2 (5 mL); filtrates concentrated; residue washed with ether (5 mL x 3); dried under vacuum"),
    insertion_record(20, "(propa-1,2-dienylsulfonyl)benzene", "(propa-1,2-dienylsulfonyl)benzene", "C=C=CS(=O)(=O)c1ccccc1", 60, 0.33, 110.2, 0.32, 2, (2, "h"), None, None, P12, "concentrated to dryness; CH2Cl2 (6 mL) added; filtered through Celite and washed with CH2Cl2 (5 mL x 2); filtrates concentrated; residue washed with ether (2 mL x 3); dried under vacuum", ("The 177 mg intermediate solid was mainly 20PF6 but contained several unknown minor species; no isolated yield is assigned to this impure stage.",)),
])

# Scheme 5 depicts 21PF6 within the covered page, but its detailed preparation is outside the viewed range.
rid21 = "scheme_dppex_tlpf6_to_21pf6"
parts21 = [
    participant(f"{rid21}_complex16", "reactant", "16", "PdI(Ph)(dppe)", P8),
    participant(f"{rid21}_allene", "reactant", "MeCH=C=CHSO2Ph", "(buta-1,2-dienylsulfonyl)benzene", P8, "CC=C=CS(=O)(=O)c1ccccc1"),
    participant(f"{rid21}_tlpf6", "reagent", "TlPF6", "thallium hexafluorophosphate", P8),
    participant(f"{rid21}_dcm", "solvent", "CH2Cl2", "dichloromethane", P8, "ClCCl"),
    participant(f"{rid21}_product", "product", "21PF6", "[Pd(eta3-MeCHC(Ph)CHSO2Ph)(dppe)]PF6", P8),
]
records.append(record(rid21, "Scheme 5: 16 + MeCH=C=CHSO2Ph + TlPF6 -> 21PF6", "reported_experiment", P8 + P9, parts21, [{"step_id": "cationic_allene_insertion", "participant_ids": [item["entity_id"] for item in parts21], "conditions": [field("solvent", "dichloromethane", P8), field("temperature", None), field("reaction_time", None), field("atmosphere", "argon", P9), field("workup", None), field("purification", None)]}], [field("product_yield", None), field("yield_measurement_basis", None)], [("The reaction arrow and product identity are visible on covered page 8; the detailed Experimental paragraph is outside the viewed page range and was not imported in this batch.", P8)], ["Amounts, temperature, time, workup, purification, product mass, yield, and yield basis are not reported on covered pages 7-12.", "The organopalladium product has no source-verified SMILES; no associated SI was supplied."]))


def exchange_record(number, precursor_mass, precursor_amount, na_mass, na_amount, precursor_meoh,
                    reagent_meoh, time_value, product_mass, product_yield, extra_workup=""):
    rid = f"salt_exchange_{number}pf6_to_{number}bph4"
    precursor_id, na_id = f"{rid}_precursor", f"{rid}_nabph4"
    meoh_id, product_id = f"{rid}_meoh", f"{rid}_product"
    evidence = P12
    parts = [
        participant(precursor_id, "reactant", f"{number}PF6", f"cationic eta3-allyl palladium complex {number}PF6", evidence, amounts=[quantity("mass", precursor_mass, "mg", evidence), quantity("amount", precursor_amount, "mmol", evidence)]),
        participant(na_id, "reagent", "NaBPh4", "sodium tetraphenylborate", evidence, amounts=[quantity("mass", na_mass, "mg", evidence), quantity("amount", na_amount, "mmol", evidence)]),
        participant(meoh_id, "solvent", "MeOH", "methanol", evidence, "CO", [quantity("volume", precursor_meoh + reagent_meoh, "mL", evidence)]),
        participant(product_id, "product", f"{number}BPh4", f"tetraphenylborate salt {number}BPh4", P8 + evidence),
    ]
    return record(rid, f"Scheme {'4' if number in (17,18) else '5'}: {number}PF6 + NaBPh4 -> {number}BPh4", "reported_experiment", P8 + P9 + evidence, parts, [{"step_id": "counterion_exchange", "participant_ids": [item["entity_id"] for item in parts], "conditions": [field("solvent", f"methanol ({precursor_meoh} mL + {reagent_meoh} mL)", evidence), field("temperature", None), field("reaction_time", {"number": time_value[0], "unit": time_value[1]}, evidence), field("atmosphere", "argon", P9), field("workup", extra_workup, evidence), field("purification", "silica-gel chromatography with CH2Cl2 eluent" if number == 17 else "filtration through Celite after redissolution in CH2Cl2" if number == 18 else None, evidence if number in (17,18) else ())]}], [field("isolated_yield", {"number": product_yield, "unit": "%"}, evidence, (product_id,)), field("yield_measurement_basis", "isolated", evidence), field("isolated_product_mass", {"number": product_mass[0], "unit": product_mass[1]}, evidence, (product_id,))], [("This counterion exchange is a separate experimental operation from formation of the PF6 precursor.", P8 + evidence)], ["Reaction temperature is not stated in the covered source pages.", "The organopalladium product has no source-verified SMILES; no associated SI was supplied."])


records.extend([
    exchange_record(17, 174, 0.21, 87, 0.25, 4, 3, (2, "h"), (145, "mg"), 69, "precipitate filtered, washed with MeOH (2 mL x 3), dried under vacuum, then chromatographed"),
    exchange_record(18, 217, 0.26, 107, 0.31, 5, 4, (30, "min"), (0.15, "g"), 57, "orange precipitate filtered, washed with MeOH (2 mL x 3), redissolved in CH2Cl2 (5 mL), filtered through Celite, and solvent removed"),
])


# 20BPh4 conversion begins on page 12 and its collection/yield continues on page 13 text.
rid20x = "salt_exchange_20pf6_to_20bph4"
parts20x = [
    participant(f"{rid20x}_precursor", "reactant", "mainly 20PF6", "impure [Pd(eta3-CH2C(Ph)CHSO2Ph)(dppe)]PF6", P12, amounts=[quantity("mass", 177, "mg", P12), field("amount", {"number": 0.20, "unit": "mmol", "qualifier": "approx", "raw_text": "ca. 0.20 mmol"}, P12)]),
    participant(f"{rid20x}_nabph4", "reagent", "NaBPh4", "sodium tetraphenylborate", P12, amounts=[quantity("mass", 83, "mg", P12), quantity("amount", 0.24, "mmol", P12)]),
    participant(f"{rid20x}_meoh", "solvent", "MeOH", "methanol", P12, "CO", [quantity("volume", 7, "mL", P12)]),
    participant(f"{rid20x}_product", "product", "20BPh4", "[Pd(eta3-CH2C(Ph)CHSO2Ph)(dppe)]BPh4", P8 + P12 + P13_TEXT),
]
records.append(record(rid20x, "Scheme 5: mainly 20PF6 + NaBPh4 -> 20BPh4", "reported_experiment", P8 + P9 + P12 + P13_TEXT, parts20x, [{"step_id": "counterion_exchange_and_purification", "participant_ids": [item["entity_id"] for item in parts20x], "conditions": [field("solvent", "methanol (4 mL + 3 mL)", P12), field("temperature", None), field("reaction_time", {"number": 2, "unit": "h"}, P12), field("atmosphere", "argon", P9), field("workup", "precipitate filtered, washed with MeOH (2 mL x 3), and dried under vacuum", P13_TEXT), field("purification", "silica-gel chromatography with CH2Cl2 eluent", P13_TEXT)]}], [field("overall_isolated_yield_from_16", {"number": 47, "unit": "%"}, P13_TEXT, (f"{rid20x}_product",)), field("yield_measurement_basis", "overall isolated yield for the two-stage 16 -> 20PF6 -> 20BPh4 sequence", P13_TEXT), field("isolated_product_mass", {"number": 137, "unit": "mg"}, P13_TEXT, (f"{rid20x}_product",))], [("Page 13 text was used only to close the experimental paragraph that begins on covered page 12; page 13 is not claimed as visually covered.", P12 + P13_TEXT), ("The PF6 precursor contained unknown minor species before counterion exchange and chromatography.", P12)], ["Reaction temperature is not stated.", "The 47% yield is explicitly overall and cannot be assigned to the counterion-exchange stage alone.", "The organopalladium product has no source-verified SMILES; no associated SI was supplied."]))


raw_path = CURRENT / "raw_model" / "records_pages_0007_0012.json"
raw_path.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")

by_suffix = {item["record_id"].split(":", 1)[1]: item["record_id"] for item in records}
existing_ids = {item["record_id"].split(":", 1)[1]: item["record_id"] for item in records if item["record_id"] in existing}


def ids(*suffixes):
    return [by_suffix[item] for item in suffixes]


control_suffixes = [
    "control_16_12_benzene_no_reaction", "control_16_12_dcm_no_reaction",
    "control_16_14_benzene_no_reaction", "control_16_14_dcm_no_reaction",
]
insertion_suffixes = [
    "scheme_dppex_tlpf6_to_17pf6", "scheme_dppex_tlpf6_to_18pf6",
    "scheme_dppex_tlpf6_to_19pf6", "scheme_dppex_tlpf6_to_20pf6",
    "scheme_dppex_tlpf6_to_21pf6",
]
exchange_suffixes = ["salt_exchange_17pf6_to_17bph4", "salt_exchange_18pf6_to_18bph4", "salt_exchange_20pf6_to_20bph4"]
all_procedure_suffixes = list(procedure_specs)

coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 7,
            "state": "attempted",
            "regions": [
                {"region": "left column continuation and Figures 4-5", "finding": "The cis-13/cis-11 structural comparison and X-ray figures are characterization evidence for existing Scheme 3 records, not new reactions.", "evidence_ids": [ev(7, "image"), ev(7, "text")]},
                {"region": "left column lower text and Figure 6", "finding": "The 1+14 reaction is confirmed to give only cis-15; SO2Ph is anti and Me is syn to Ph. This supplements the existing record.", "evidence_ids": [ev(7, "image"), ev(7, "text")]},
                {"region": "right column PdI(Ph)(dppe) section", "finding": "Four NMR-monitored no-reaction controls are distinguished by allene 12/14 and benzene/CH2Cl2; the paragraph continues on page 8. Preparation of precursor 16 is cross-referenced and detailed on page 12.", "evidence_ids": [ev(7, "image"), ev(7, "text"), ev(8, "text")]},
            ],
            "record_ids": ids("scheme3_1_10_to_11", "scheme3_1_12_to_13", "scheme3_1_14_to_15", "preparation_complex16", *control_suffixes),
            "unresolved": ["The source does not specify absolute quantities or a detection limit for the no-reaction controls."],
        },
        {
            "page": 8,
            "state": "attempted",
            "regions": [
                {"region": "top-left Scheme 4", "finding": "Three independent TlPF6-promoted insertions to 17PF6/18PF6/19PF6 and two separate NaBPh4 counterion exchanges to 17BPh4/18BPh4 are inventoried.", "evidence_ids": [ev(8, "image"), ev(8, "text")]},
                {"region": "top-right Scheme 5", "finding": "Two independent TlPF6-promoted insertions to 20PF6/21PF6 and the subsequent 20PF6-to-20BPh4 exchange are inventoried.", "evidence_ids": [ev(8, "image"), ev(8, "text")]},
                {"region": "left column no-reaction continuation and cationic-complex discussion", "finding": "The four 12 h room-temperature controls have no appreciable reaction; NMR assignments support the depicted cationic allyl products without creating extra synthetic records.", "evidence_ids": [ev(8, "image"), ev(8, "text"), ev(7, "text")]},
                {"region": "right column theoretical-study discussion", "finding": "Scheme 6/Figure 7 precursor and pathway discussion is classified as a computational mechanism, not a wet experiment.", "evidence_ids": [ev(8, "image"), ev(8, "text")]},
            ],
            "record_ids": ids(*control_suffixes, *insertion_suffixes, *exchange_suffixes, "scheme6_figure7_computational_pathways"),
            "unresolved": ["The page-level prose contains an apparent 19BPh4/CO2Et wording inconsistency; the Scheme 4 drawing and Experimental heading support 19PF6 with COPh, so no 19BPh4 reaction was invented.", "The detailed 21PF6 procedure lies outside pages 7-12 and is not imported."],
        },
        {
            "page": 9,
            "state": "attempted",
            "regions": [
                {"region": "top Scheme 6 and two-column theoretical discussion", "finding": "Four model precursor isomers and eight calculated allyl/vinyl pathways are represented in one mechanism record; the numerical energy lists are preserved as source text because kcal/mol is not a supported structured-quantity unit.", "evidence_ids": [ev(9, "image"), ev(9, "text")]},
                {"region": "right-column conclusion", "finding": "Conclusion reiterates the negative controls and observed allyl selectivity; it does not add independent experiments.", "evidence_ids": [ev(9, "image"), ev(9, "text")]},
                {"region": "right-column Experimental Section general conditions", "finding": "The global argon/Schlenk condition is applied to covered experimental records; literature preparation of starting allenes is context only, not re-extracted.", "evidence_ids": [ev(9, "image"), ev(9, "text")]},
            ],
            "record_ids": ids("scheme6_figure7_computational_pathways", *control_suffixes, *all_procedure_suffixes, "preparation_complex16", *insertion_suffixes, *exchange_suffixes),
            "unresolved": ["Supporting information is mentioned by the paper but was not supplied or explicitly associated in this workspace."],
        },
        {
            "page": 10,
            "state": "attempted",
            "regions": [
                {"region": "full-page Figure 7 panels a and b", "finding": "Computed free/electronic energy profiles for eight pathways from 22A-D were visually inspected and linked to the mechanism record; no wet-chemistry experiment or isolated compound is introduced.", "evidence_ids": [ev(10, "image"), ev(10, "text")]},
            ],
            "record_ids": ids("scheme6_figure7_computational_pathways"),
            "unresolved": ["Transition-state/model connectivities remain machine-unverified; energies are not converted to unsupported schema units."],
        },
        {
            "page": 11,
            "state": "attempted",
            "regions": [
                {"region": "left column top continuation for compound 3", "finding": "The cross-page procedure supplies allene quantity, CH2Cl2 volume, 30 min, workup, 0.14 g and 76% yield; it is merged into the existing 1+2->3 record.", "evidence_ids": [ev(11, "image"), ev(11, "text"), ev(9, "text")]},
                {"region": "left column preparations of 5 and 7", "finding": "Detailed quantities, exact solvents, 2 h room-temperature conditions, workups, masses, 84%/80% yields, and isomer ratios are merged into the two existing Scheme 2 records.", "evidence_ids": [ev(11, "image"), ev(11, "text")]},
                {"region": "left-bottom and right-top preparation of 9", "finding": "The 8 h CH2Cl2 procedure, quantities, 41 mg/63% outcome and 3.5:1 ratio are merged into the existing Scheme 3 record.", "evidence_ids": [ev(11, "image"), ev(11, "text")]},
                {"region": "right column preparations of 11, 13, and beginning of 15", "finding": "Three existing Scheme 3 records are supplemented with exact quantities, times, workups, masses/yields and ratios; the 15 workup/yield continues on page 12.", "evidence_ids": [ev(11, "image"), ev(11, "text"), ev(12, "text")]},
            ],
            "record_ids": ids(*all_procedure_suffixes),
            "unresolved": ["The 11 isomer ratio is 1:4.3 in Results and 1:4 in Experimental; both values are retained without reconciliation.", "Organopalladium structures remain without source-verified SMILES."],
        },
        {
            "page": 12,
            "state": "attempted",
            "regions": [
                {"region": "left-column top continuation for cis-15", "finding": "The workup, 2.628 g/97% isolated outcome, and dichloromethane-containing analytical sample are merged into the existing 1+14->cis-15 record.", "evidence_ids": [ev(12, "image"), ev(12, "text"), ev(11, "text")]},
                {"region": "left column preparation of 16", "finding": "A two-stage precursor preparation from Pd(PPh3)4, dppe, and PhI is extracted as a new reported experiment with 0.22 g/71% isolated product.", "evidence_ids": [ev(12, "image"), ev(12, "text")]},
                {"region": "left and center columns 17PF6/17BPh4/18PF6", "finding": "Two TlPF6-promoted insertions and one separate NaBPh4 counterion exchange are extracted with all explicit quantities, times, workups and yields.", "evidence_ids": [ev(12, "image"), ev(12, "text"), ev(8, "image")]},
                {"region": "center-right 18BPh4 and 19PF6", "finding": "The 18PF6 counterion exchange and the COPh-allene insertion to 19PF6 are extracted as separate experiments.", "evidence_ids": [ev(12, "image"), ev(12, "text"), ev(8, "image")]},
                {"region": "right-column 20PF6/20BPh4 sequence", "finding": "The impure 20PF6 stage and subsequent NaBPh4 exchange are separated; page 13 text is used only to close the page-12 paragraph and preserve the 137 mg, 47% overall outcome.", "evidence_ids": [ev(12, "image"), ev(12, "text"), ev(13, "text")]},
            ],
            "record_ids": ids("scheme3_1_14_to_15", "preparation_complex16", "scheme_dppex_tlpf6_to_17pf6", "salt_exchange_17pf6_to_17bph4", "scheme_dppex_tlpf6_to_18pf6", "salt_exchange_18pf6_to_18bph4", "scheme_dppex_tlpf6_to_19pf6", "scheme_dppex_tlpf6_to_20pf6", "salt_exchange_20pf6_to_20bph4"),
            "unresolved": ["Reaction temperatures for the cationic insertions and counterion exchanges are not stated.", "The 20PF6 intermediate contains unknown minor species and has no isolated yield; 20BPh4 is reported only as a 47% overall yield.", "Page 13 was not visually covered; only its extracted text closes a paragraph beginning on page 12."],
        },
    ],
}

coverage_path = CURRENT / "coverage" / "pages_0007_0012.json"
coverage_path.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

tasks_path = CURRENT / "tasks.json"
tasks = json.loads(tasks_path.read_text())
for task in tasks:
    if task.get("document_id") == DOC and task.get("evidence_id") in {ev(n, "text") for n in range(7, 13)}:
        task["state"] = "attempted"
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"submitted_records": len(records), "new_records": len(records) - len(procedure_specs), "updated_existing_records": len(procedure_specs), "raw": str(raw_path), "coverage": str(coverage_path)}, ensure_ascii=False))
