#!/usr/bin/env python3
"""Build the page 1--4 machine extraction batch for doc_0d07f64a30744936."""

import json
from pathlib import Path


DOC = "doc_0d07f64a30744936"
P2 = [f"{DOC}:page2:image", f"{DOC}:page2:text"]
P3 = [f"{DOC}:page3:image", f"{DOC}:page3:text"]
P4 = [f"{DOC}:page4:image", f"{DOC}:page4:text"]


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


def participant(entity_id, role, label, evidence, *, smiles=None, amounts=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(None, []),
        "smiles": fact(smiles, evidence if smiles is not None else []),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": amounts or [],
    }


def record(rid, kind, evidence, *, participants=None, steps=None, outcomes=None,
           notes=None, unresolved=None):
    return {
        "record_id": f"{DOC}:{rid}",
        "document_id": DOC,
        "source_reaction_id": rid,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": list(evidence),
        "participants": participants or [],
        "steps": steps or [],
        "outcomes": outcomes or [],
        "notes": [fact(value, evidence) for value in (notes or [])],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved or [],
        },
    }


SMILES = {
    "Au(PPh3)Cl": "Cl[Au]P(c1ccccc1)(c1ccccc1)c1ccccc1",
    "AgBF4": "[Ag+].[B-](F)(F)(F)F",
    "AgSbF6": "[Ag+].[Sb-](F)(F)(F)(F)(F)F",
    "AgOTf": "[Ag+].[O-]S(=O)(=O)C(F)(F)F",
    "AuCl3": "Cl[Au](Cl)Cl",
    "toluene": "Cc1ccccc1",
    "mesitylene": "Cc1cc(C)cc(C)c1",
    "1,4-dioxane": "O1CCOCC1",
    "DMSO": "CS(C)=O",
    "DMF": "CN(C)C=O",
    "Pd(OAc)2": "CC(=O)[O-].CC(=O)[O-].[Pd+2]",
    "PhB(OH)2": "OB(O)c1ccccc1",
    "K3PO4": "[K+].[K+].[K+].[O-]P([O-])([O-])=O",
    "H2O": "O",
    "CH2Cl2": "ClCCl",
    "TFA": "O=C(O)C(F)(F)F",
    "D4-acetic acid": "[2H]OC(=O)C([2H])([2H])[2H]",
}


def amount(name, number, unit, evidence):
    return field(name, {"number": number, "unit": unit}, evidence)


def chemical(entity_id, role, label, evidence, *, amount_fields=None):
    return participant(
        entity_id, role, label, evidence,
        smiles=SMILES.get(label), amounts=amount_fields,
    )


records = []

# Scheme 1 is explicitly a conceptual/retrosynthetic scheme, not a batch experiment.
records.append(record(
    "scheme1_allene_approach", "general_scheme", P2,
    notes=[
        "Scheme 1 is a generic allene approach/retrosynthetic relationship between a 3-allenylindole and a cyclopenta[b]indole skeleton; it reports no batch conditions or outcome."
    ],
    unresolved=["Generic R-group structures are not represented as complete molecular structures."],
))

# Scheme 2 summarizes multiple failed screenings and therefore is retained as unresolved,
# rather than being promoted to one fully specified experiment.
scheme2_participants = [
    participant("substrate_1a", "reactant", "1a", P2),
    chemical("au_pph3_cl", "catalyst", "Au(PPh3)Cl", P2),
    chemical("ag_otf", "catalyst", "AgOTf", P2),
    chemical("toluene", "solvent", "toluene", P2),
    participant("desired_cyclized_product", "product", "desired cyclized product from 1a", P2),
    participant("unknown_product", "product", "unknown product", P2),
]
records.append(record(
    "scheme2_failed_screening_summary", "unresolved", P2,
    participants=scheme2_participants,
    steps=[{
        "step_id": "screening_summary",
        "participant_ids": ["substrate_1a", "au_pph3_cl", "ag_otf", "toluene"],
        "conditions": [field("temperature", "rt or reflux", P2), field("solvent", "toluene", P2)],
    }],
    outcomes=[
        field("desired_product_observation", "not observed", P2, ["desired_cyclized_product"]),
        field("unknown_product_observation", "formed", P2, ["unknown_product"]),
    ],
    notes=["The prose states that the desired product was not observed after many screenings and that an unknown product formed."],
    unresolved=[
        "Scheme 2 collapses multiple screenings; individual catalyst loadings, times, temperatures, and yields are not reported.",
        "The unknown product identity and both depicted organic structures lack source-verified SMILES.",
    ],
))


# Table 1: every optimization row is an independent experiment.
table1 = [
    (1, "Au(PPh3)Cl", "AgBF4", 130, "toluene", 19.3, 37, 48),
    (2, "Au(PPh3)Cl", "AgSbF6", 130, "toluene", 19, 80, 13),
    (3, "Au(PPh3)Cl", "AgOTf", 130, "toluene", 19.3, 95, 0),
    (4, None, "AgOTf", 130, "toluene", 24, 0, 85),
    (5, "Au(PPh3)Cl", None, 130, "toluene", 24, 0, 80),
    (6, "AuCl3", None, 130, "toluene", 24, 8, 76),
    (7, "Au(PPh3)Cl", "AgOTf", 130, "mesitylene", 21, 63, 0),
    (8, "Au(PPh3)Cl", "AgOTf", 130, "1,4-dioxane", 10, 75, 0),
    (9, "Au(PPh3)Cl", "AgOTf", 130, "DMSO", 21, 0, 23),
    (10, "Au(PPh3)Cl", "AgOTf", 130, "DMF", 22.5, 0, 12),
    (11, "Au(PPh3)Cl", "AgOTf", 110, "toluene", 9, 95, 0),
    (12, "(JohnPhos)AuCl", "AgOTf", 110, "toluene", 9, 94, 0),
    (13, "(IPr)AuCl", "AgOTf", 110, "toluene", 9, 92, 0),
    (14, "Au(PPh3)Cl", "AgOTf", 80, "toluene", 22, 16, 78),
    (15, "Au(PPh3)Cl", "AgOTf", "rt", "toluene", 22, 5, 73),
]

for entry, au, ag, temperature, solvent, hours, product_yield, recovery in table1:
    participants = [
        participant("substrate_1b", "reactant", "1b", P3, amounts=[amount("amount", 0.2, "mmol", P3)]),
        participant("product_2b", "product", "2b", P3),
    ]
    active_ids = ["substrate_1b"]
    if au:
        participants.append(chemical("au_component", "catalyst", au, P3, amount_fields=[amount("loading_mol_percent", 5, "mol%", P3)]))
        active_ids.append("au_component")
    if ag:
        participants.append(chemical("ag_component", "catalyst", ag, P3, amount_fields=[amount("loading_mol_percent", 5, "mol%", P3)]))
        active_ids.append("ag_component")
    solvent_amounts = [amount("volume", 2, "mL", P3)] if solvent == "toluene" else []
    participants.append(chemical("solvent", "solvent", solvent, P3, amount_fields=solvent_amounts))
    active_ids.append("solvent")
    unresolved = [
        "The main-text table omits workup and purification; no explicitly associated SI was supplied.",
        "Structures of 1b and 2b are image-depicted but not encoded as source-verified SMILES.",
    ]
    if solvent != "toluene":
        unresolved.append("The footnote explicitly states 2 mL of toluene and does not unambiguously restate solvent volume for this non-toluene row.")
    records.append(record(
        f"table1_entry{entry}", "optimization_entry", P3,
        participants=participants,
        steps=[{
            "step_id": "cyclization",
            "participant_ids": active_ids,
            "conditions": [
                field("temperature", temperature if isinstance(temperature, str) else {"number": temperature, "unit": "°C"}, P3),
                field("time", {"number": hours, "unit": "h"}, P3),
                field("solvent", solvent, P3),
            ],
        }],
        outcomes=[
            field("product_2b_nmr_yield", {"number": product_yield, "unit": "%"}, P3, ["product_2b"]),
            field("recovered_starting_material_yield", {"number": recovery, "unit": "%"}, P3, ["substrate_1b"]),
            field("yield_measurement_basis", "NMR using mesitylene or CH2Br2 as internal standard", P3),
        ],
        notes=[f"Table 1 optimization entry {entry}; a dash in a catalyst column is represented by omission of that catalyst participant."],
        unresolved=unresolved,
    ))


# Table 2 substrate scope. Footnotes b/c/d are applied only to marked rows.
table2 = [
    ("b", 9, "h", 93, True, False, False),
    ("c", 7.2, "h", 89, False, False, False),
    ("d", 28, "h", 86, False, False, False),
    ("e", 23, "h", 92, False, False, False),
    ("f", 24, "h", 72, False, False, False),
    ("g", 26.5, "h", 63, True, True, False),
    ("h", 28, "h", 83, False, False, False),
    ("i", 28.5, "h", 78, False, False, False),
    ("j", 12, "h", 76, False, False, False),
    ("k", 26, "h", 75, False, False, False),
    ("l", 31, "h", 56, False, True, False),
    ("m", 24, "h", 85, False, False, False),
    ("n", 53, "h", 56, False, False, True),
    ("o", 15.5, "h", 83, False, False, False),
    ("p", 3.7, "d", 62, False, False, False),
    ("q", 43.5, "h", 74, False, True, False),
]

for suffix, duration, duration_unit, reported_yield, scale02, cat10, temp115 in table2:
    substrate_id = f"substrate_1{suffix}"
    product_id = f"product_2{suffix}"
    scale = 0.2 if scale02 else 0.5
    loading = 10 if cat10 else 5
    temperature = 115 if temp115 else 110
    participants = [
        participant(substrate_id, "reactant", f"1{suffix}", P3, amounts=[amount("amount", scale, "mmol", P3)]),
        participant(product_id, "product", f"2{suffix}", P3),
        chemical("au_pph3_cl", "catalyst", "Au(PPh3)Cl", P3, amount_fields=[amount("loading_mol_percent", loading, "mol%", P3)]),
        chemical("ag_otf", "catalyst", "AgOTf", P3, amount_fields=[amount("loading_mol_percent", loading, "mol%", P3)]),
        chemical("toluene", "solvent", "toluene", P3, amount_fields=[amount("volume", 2, "mL", P3)]),
    ]
    records.append(record(
        f"table2_1{suffix}_to_2{suffix}", "substrate_scope_entry", P3,
        participants=participants,
        steps=[{
            "step_id": "gold_catalyzed_cyclization",
            "participant_ids": [substrate_id, "au_pph3_cl", "ag_otf", "toluene"],
            "conditions": [
                field("temperature", {"number": temperature, "unit": "°C"}, P3),
                field("time", {"number": duration, "unit": duration_unit}, P3),
                field("solvent", "toluene", P3),
                field("vessel", "Schlenk tube", P3),
            ],
        }],
        outcomes=[
            field(f"product_2{suffix}_reported_yield", {"number": reported_yield, "unit": "%"}, P3, [product_id]),
            field("yield_measurement_basis", None, []),
        ],
        notes=[f"Table 2 substrate-scope row 1{suffix} to 2{suffix}; marked footnotes were applied to scale, catalyst loading, and temperature."],
        unresolved=[
            "The main-text table does not state the yield measurement basis, workup, or purification; no explicitly associated SI was supplied.",
            f"The depicted structures of 1{suffix} and 2{suffix} are not encoded as source-verified SMILES.",
        ],
    ))


# Scheme 3: other electron-withdrawing groups and a distinct gram-scale batch.
for suffix, hours, reported_yield in [("r", 10, 91), ("s", 3, 85)]:
    sid, pid = f"substrate_1{suffix}", f"product_2{suffix}"
    participants = [
        participant(sid, "reactant", f"1{suffix}", P3),
        participant(pid, "product", f"2{suffix}", P3),
        chemical("au_pph3_cl", "catalyst", "Au(PPh3)Cl", P3, amount_fields=[amount("loading_mol_percent", 10, "mol%", P3)]),
        chemical("ag_otf", "catalyst", "AgOTf", P3, amount_fields=[amount("loading_mol_percent", 10, "mol%", P3)]),
        chemical("toluene", "solvent", "toluene", P3),
    ]
    records.append(record(
        f"scheme3_1{suffix}_to_2{suffix}", "substrate_scope_entry", P3,
        participants=participants,
        steps=[{
            "step_id": "gold_catalyzed_cyclization",
            "participant_ids": [sid, "au_pph3_cl", "ag_otf", "toluene"],
            "conditions": [field("temperature", {"number": 110, "unit": "°C"}, P3), field("time", {"number": hours, "unit": "h"}, P3), field("solvent", "toluene", P3)],
        }],
        outcomes=[field(f"product_2{suffix}_reported_yield", {"number": reported_yield, "unit": "%"}, P3, [pid]), field("yield_measurement_basis", None, [])],
        notes=[f"Scheme 3: 1{suffix} bears the explicitly depicted electron-withdrawing group and affords 2{suffix}."],
        unresolved=["Substrate amount, solvent volume, yield basis, workup, and purification are not stated in Scheme 3.", "Depicted organic structures are not encoded as source-verified SMILES."],
    ))

gram_participants = [
    participant("substrate_1o", "reactant", "1o", P3, amounts=[amount("mass", 1.2433, "g", P3)]),
    participant("product_2o", "product", "2o", P3, amounts=[amount("mass", 1.0488, "g", P3)]),
    chemical("au_pph3_cl", "catalyst", "Au(PPh3)Cl", P3, amount_fields=[amount("loading_mol_percent", 5, "mol%", P3)]),
    chemical("ag_otf", "catalyst", "AgOTf", P3, amount_fields=[amount("loading_mol_percent", 5, "mol%", P3)]),
    chemical("toluene", "solvent", "toluene", P3),
]
records.append(record(
    "scheme3_gram_scale_1o_to_2o", "reported_experiment", P3,
    participants=gram_participants,
    steps=[{
        "step_id": "gram_scale_cyclization",
        "participant_ids": ["substrate_1o", "au_pph3_cl", "ag_otf", "toluene"],
        "conditions": [field("temperature", {"number": 110, "unit": "°C"}, P3), field("time", {"number": 11.5, "unit": "h"}, P3), field("solvent", "toluene", P3)],
    }],
    outcomes=[field("product_2o_reported_yield", {"number": 84, "unit": "%"}, P3, ["product_2o"]), field("yield_measurement_basis", None, [])],
    notes=["Scheme 3 gram-scale experiment is distinct from the Table 2 1o-to-2o scope row because the scale, time, and yield differ."],
    unresolved=["Solvent volume, yield basis, workup, and purification are not stated in Scheme 3.", "Depicted structures of 1o and 2o are not encoded as source-verified SMILES."],
))


# Scheme 4: two synthetic applications.
suzuki_participants = [
    participant("reactant_2h", "reactant", "2h", P4),
    participant("product_3h", "product", "3h", P4),
    chemical("pd_oac2", "catalyst", "Pd(OAc)2", P4, amount_fields=[amount("loading_mol_percent", 6, "mol%", P4)]),
    participant("lb_phos_hbf4", "catalyst", "LB-phos·HBF4", P4, amounts=[amount("loading_mol_percent", 12, "mol%", P4)]),
    chemical("phenylboronic_acid", "reagent", "PhB(OH)2", P4, amount_fields=[amount("equivalents", 4.0, "equiv", P4)]),
    chemical("potassium_phosphate", "reagent", "K3PO4", P4, amount_fields=[amount("equivalents", 3.5, "equiv", P4)]),
    chemical("water", "reagent", "H2O", P4, amount_fields=[amount("equivalents", 3.0, "equiv", P4)]),
    chemical("dioxane", "solvent", "1,4-dioxane", P4),
]
records.append(record(
    "scheme4_suzuki_2h_to_3h", "reported_experiment", P4,
    participants=suzuki_participants,
    steps=[{
        "step_id": "suzuki_coupling",
        "participant_ids": ["reactant_2h", "pd_oac2", "lb_phos_hbf4", "phenylboronic_acid", "potassium_phosphate", "water", "dioxane"],
        "conditions": [field("temperature", {"number": 110, "unit": "°C"}, P4), field("time", {"number": 53, "unit": "h"}, P4), field("solvent", "1,4-dioxane", P4)],
    }],
    outcomes=[field("product_3h_reported_yield", {"number": 90, "unit": "%"}, P4, ["product_3h"]), field("yield_measurement_basis", None, [])],
    unresolved=["Reaction scale, solvent volume, yield basis, workup, and purification are not reported in the main-text scheme.", "Structures of 2h, 3h, and LB-phos·HBF4 are not encoded as source-verified SMILES."],
))

cyclo_participants = [
    participant("reactant_2o", "reactant", "2o", P4),
    participant("product_3o", "product", "3o", P4),
    participant("azomethine_precursor", "reagent", "TMS–CH2–N(Bn)–CH2–OMe (depicted reagent)", P4, amounts=[amount("equivalents", 4, "equiv", P4)]),
    chemical("tfa", "reagent", "TFA", P4, amount_fields=[amount("loading_mol_percent", 50, "mol%", P4)]),
    chemical("dichloromethane", "solvent", "CH2Cl2", P4),
]
records.append(record(
    "scheme4_cycloaddition_2o_to_3o", "reported_experiment", P4,
    participants=cyclo_participants,
    steps=[{
        "step_id": "one_three_dipolar_cycloaddition",
        "participant_ids": ["reactant_2o", "azomethine_precursor", "tfa", "dichloromethane"],
        "conditions": [field("temperature", "reflux", P4), field("time", {"number": 29, "unit": "h"}, P4), field("solvent", "CH2Cl2", P4)],
    }],
    outcomes=[field("product_3o_reported_yield", {"number": 97, "unit": "%"}, P4, ["product_3o"]), field("yield_measurement_basis", None, [])],
    unresolved=["Reaction scale, solvent volume, reflux temperature, yield basis, workup, and purification are not reported in the main-text scheme.", "The depicted organic structures, including the azomethine-ylide precursor, are not encoded as source-verified SMILES."],
))


# Scheme 5: preserve the two isotope-labeling batches independently.
label_common = [
    participant("substrate_1o", "reactant", "1o", P4),
    participant("product_2o_d", "product", "2o-d", P4),
    chemical("au_pph3_cl", "catalyst", "Au(PPh3)Cl", P4, amount_fields=[amount("loading_mol_percent", 5, "mol%", P4)]),
    chemical("ag_otf", "catalyst", "AgOTf", P4, amount_fields=[amount("loading_mol_percent", 5, "mol%", P4)]),
]
first = label_common + [
    chemical("d4_acetic_acid", "reagent", "D4-acetic acid", P4, amount_fields=[amount("equivalents", 10, "equiv", P4)]),
    chemical("toluene", "solvent", "toluene", P4),
]
records.append(record(
    "scheme5_d4_acetic_acid_labeling", "reported_experiment", P4,
    participants=first,
    steps=[{
        "step_id": "deuterium_labeling_cyclization",
        "participant_ids": ["substrate_1o", "au_pph3_cl", "ag_otf", "d4_acetic_acid", "toluene"],
        "conditions": [field("temperature", {"number": 110, "unit": "°C"}, P4), field("time", {"number": 3, "unit": "h"}, P4), field("solvent", "toluene", P4)],
    }],
    outcomes=[
        field("product_2o_d_isolated_yield", {"number": 82, "unit": "%"}, P4, ["product_2o_d"]),
        field("deuterium_incorporation", {"number": 84, "unit": "%"}, P4, ["product_2o_d"]),
        field("yield_measurement_basis", "isolated yield", P4),
    ],
    unresolved=["Reaction scale, solvent volume, workup, and purification are not reported in the main text.", "Structures of 1o and 2o-d are not encoded as source-verified SMILES."],
))

second = label_common + [participant("d8_toluene", "solvent", "D8-toluene", P4)]
records.append(record(
    "scheme5_d8_toluene_labeling", "reported_experiment", P4,
    participants=second,
    steps=[{
        "step_id": "deuterium_labeling_cyclization",
        "participant_ids": ["substrate_1o", "au_pph3_cl", "ag_otf", "d8_toluene"],
        "conditions": [field("temperature", {"number": 110, "unit": "°C"}, P4), field("time", {"number": 1.5, "unit": "h"}, P4), field("solvent", "D8-toluene", P4)],
    }],
    outcomes=[
        field("product_2o_d_isolated_yield", {"number": 89, "unit": "%"}, P4, ["product_2o_d"]),
        field("deuterium_incorporation", {"number": 86, "unit": "%"}, P4, ["product_2o_d"]),
        field("yield_measurement_basis", "isolated yield", P4),
    ],
    notes=["The prose describes this as the same reaction in d8-toluene, but does not independently restate d4-acetic acid for this row."],
    unresolved=[
        "Whether the arrow's 10 equiv d4-acetic acid condition also applies to the d8-toluene row is visually/textually ambiguous, so it is not added as a participant.",
        "Reaction scale, solvent volume, workup, and purification are not reported in the main text.",
        "Structures of 1o and 2o-d are not encoded as source-verified SMILES.",
    ],
))


records.append(record(
    "scheme5_proposed_mechanism", "mechanism", P4,
    notes=[
        "Scheme 5 proposes cationic-gold activation, indole C2 attack through A/A', vinylgold intermediate B, rearomatization, and demetalation; it is a proposed mechanism, not an additional experiment."
    ],
    unresolved=["Intermediates A, A', B, and C are proposed structures and are not encoded as verified molecular records."],
))


out = Path(__file__).with_name("records_pages_0001_0004.json")
out.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"path": str(out), "records": len(records)}, ensure_ascii=False))
