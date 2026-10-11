#!/usr/bin/env python3
"""Build evidence-linked machine records for PDF pages 1-2.

This is a reproducible raw-model artifact.  The merge tool remains responsible
for enforcing machine-record status and validation.
"""

import json
from pathlib import Path


DOC = "doc_35a076f55d99fce2"
P1T = f"{DOC}:page1:text"
P1I = f"{DOC}:page1:image"
P2T = f"{DOC}:page2:text"
P2I = f"{DOC}:page2:image"
PAGE1 = [P1T, P1I]
PAGE2 = [P2T, P2I]


def fact(value, evidence):
    return {
        "value": value,
        "evidence_ids": list(evidence) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def field(name, value, evidence):
    return {"name": name, "fact": fact(value, evidence)}


def amounts_missing():
    return [field("amount", None, [])]


def participant(entity_id, role, name, evidence, *, label=None, smiles=None,
                amounts=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence),
        "smiles": fact(smiles, evidence),
        # Parseability is a syntax/valence property only; it does not certify
        # that the source drawing was recognized correctly.
        "smiles_parseable": True if smiles is not None else None,
        "structure_verified": False,
        "amounts": amounts if amounts is not None else amounts_missing(),
    }


def record(suffix, kind, evidence, participants, steps, outcomes, notes=None,
           unresolved=None):
    return {
        "record_id": f"{DOC}:{suffix}",
        "document_id": DOC,
        "source_reaction_id": suffix,
        "record_kind": kind,
        "status": "needs_review",
        "completeness": "partial",
        "evidence_ids": list(evidence),
        "participants": participants,
        "steps": steps,
        "outcomes": outcomes,
        "notes": notes or [],
        "review": {
            "method": "model",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved or [
                "Participant quantities, concentration, and atmosphere are not reported.",
                "No associated Supporting Information was supplied in this pilot.",
            ],
        },
    }


SUBSTRATES = {
    "ketone": ("1a", "3,4-pentadien-2-one", "C=C=CC(C)=O"),
    "acid": (None, "2,3-butadienoic acid", "C=C=CC(=O)O"),
    "ester": (None, "methyl 2,3-butadienoate", "C=C=CC(=O)OC"),
}

PRODUCTS = {
    "2a": ("4-iodo-4-penten-2-one", "C=C(I)CC(C)=O"),
    "2b": ("4-bromo-4-penten-2-one", "C=C(Br)CC(C)=O"),
    "2c": ("4-chloro-4-penten-2-one", "C=C(Cl)CC(C)=O"),
    "2d": ("3-iodo-3-butenoic acid", "C=C(I)CC(=O)O"),
    "2e": ("3-bromo-3-butenoic acid", "C=C(Br)CC(=O)O"),
    "2f": ("3-chloro-3-butenoic acid", "C=C(Cl)CC(=O)O"),
    "2g": ("methyl 3-iodo-3-butenoate", "C=C(I)CC(=O)OC"),
    "2h": ("methyl 3-bromo-3-butenoate", "C=C(Br)CC(=O)OC"),
    "2i": ("methyl 3-chloro-3-butenoate", "C=C(Cl)CC(=O)OC"),
}

REAGENTS = {
    "NaI": ("sodium iodide", "[Na+].[I-]"),
    "NaBr": ("sodium bromide", "[Na+].[Br-]"),
    "NaCl": ("sodium chloride", "[Na+].[Cl-]"),
    "LiI": ("lithium iodide", "[Li+].[I-]"),
    "LiBr.H2O": ("lithium bromide monohydrate", "[Li+].[Br-].O"),
    "LiCl.H2O": ("lithium chloride monohydrate", "[Li+].[Cl-].O"),
    "HI_45aq": ("aqueous hydriodic acid (45%)", None),
}


def standard_participants(substrate_key, reagent_key, product_label, evidence):
    substrate_label, substrate_name, substrate_smiles = SUBSTRATES[substrate_key]
    reagent_name, reagent_smiles = REAGENTS[reagent_key]
    product_name, product_smiles = PRODUCTS[product_label]
    reagent_amounts = amounts_missing()
    if reagent_key == "HI_45aq":
        reagent_amounts.append(field("concentration", {"number": 45, "unit": "%"}, evidence))
    return [
        participant("substrate", "reactant", substrate_name, evidence,
                    label=substrate_label, smiles=substrate_smiles),
        participant("halide_source", "reagent", reagent_name, evidence,
                    smiles=reagent_smiles, amounts=reagent_amounts),
        participant("hoac", "solvent", "acetic acid", evidence,
                    smiles="CC(=O)O"),
        participant("product", "product", product_name, evidence,
                    label=product_label, smiles=product_smiles, amounts=[]),
    ]


def reaction_step(time_h, temp_c, evidence, participant_ids=None):
    return {
        "step_id": "reaction",
        "participant_ids": participant_ids or ["substrate", "halide_source", "hoac", "product"],
        "conditions": [
            field("temperature", {"number": temp_c, "unit": "°C"}, evidence),
            field("time", {"number": time_h, "unit": "h"}, evidence),
            field("atmosphere", None, []),
            field("concentration", None, []),
        ],
    }


records = []

# Table 1: each row is a distinct experiment. Entry 1 is merged with the
# page-2 typical procedure and its explicitly reported minor isomer outcome.
table_rows = [
    (1, "ketone", "NaI", 25, 1.5, "2a", 69, "isolated"),
    (2, "ketone", "NaBr", 25, 14, "2b", 35, "1H NMR using CH2Br2 as internal standard"),
    (3, "ketone", "NaCl", 25, 25, "2c", 8, "1H NMR using CH2Br2 as internal standard"),
    (4, "acid", "NaI", 70, 7, "2d", 92, "isolated"),
    (5, "acid", "HI_45aq", 70, 7, "2d", 87, "isolated"),
    (6, "acid", "NaBr", 70, 7, "2e", 82, "1H NMR using CH2Br2 as internal standard"),
    (7, "acid", "LiBr.H2O", 70, 7, "2e", 88, "isolated"),
    (8, "acid", "NaCl", 70, 15, "2f", 16, "1H NMR using CH2Br2 as internal standard"),
    (9, "acid", "LiCl.H2O", 70, 7, "2f", 87, "isolated"),
    (10, "ester", "NaI", 70, 0.5, "2g", 56, "isolated"),
    (11, "ester", "LiBr.H2O", 70, 18, "2h", 86, "isolated"),
    (12, "ester", "LiCl.H2O", 70, 26, "2i", 74, "isolated"),
]

for entry, substrate_key, reagent_key, temp, time_h, product_label, yield_pct, basis in table_rows:
    evidence = PAGE1 + PAGE2 if entry == 1 else PAGE1
    participants = standard_participants(substrate_key, reagent_key, product_label, evidence)
    outcomes = [
        field("product_yield", {"number": yield_pct, "unit": "%"}, PAGE1),
        field("yield_measurement_basis", basis, PAGE1),
    ]
    steps = [reaction_step(time_h, temp, PAGE1)]
    notes = [fact(f"Table 1 entry {entry}.", PAGE1)]
    unresolved = [
        "No associated Supporting Information was supplied in this pilot.",
        "Compound-specific atmosphere and reaction concentration are not reported.",
    ]
    if entry == 1:
        # Replace missing charges with the detailed typical-procedure values.
        participants[0]["amounts"] = [
            field("mass", {"number": 164, "unit": "mg"}, PAGE2),
            field("amount", {"number": 2.0, "unit": "mmol"}, PAGE2),
        ]
        participants[1]["amounts"] = [
            field("mass", {"number": 330, "unit": "mg"}, PAGE2),
            field("amount", {"number": 2.2, "unit": "mmol"}, PAGE2),
        ]
        participants[2]["amounts"] = [field("volume", {"number": 1, "unit": "mL"}, PAGE2)]
        participants.append(participant(
            "minor_isomer", "product", "4-iodo-3-penten-2-one", PAGE2,
            smiles="CC(=O)C=C(I)C", amounts=[]))
        steps[0]["participant_ids"].append("minor_isomer")
        steps.extend([
            {
                "step_id": "workup",
                "participant_ids": [],
                "conditions": [
                    field("dilution", "ether", PAGE2),
                    field("neutralization", "aqueous K2CO3 at 0 °C", PAGE2),
                    field("extraction", "ether", PAGE2),
                    field("drying", "MgSO4", PAGE2),
                    field("solvent_removal", "evaporation", PAGE2),
                ],
            },
            {
                "step_id": "purification",
                "participant_ids": ["product"],
                "conditions": [field("chromatography", "silica gel; petroleum ether/ethyl acetate 10:1", PAGE2)],
            },
        ])
        outcomes.extend([
            field("isolated_product_mass", {"number": 290, "unit": "mg"}, PAGE2),
            field("minor_isomer_yield", "3-4%", PAGE2),
            field("minor_isomer_measurement_basis", None, []),
        ])
        notes.extend([
            fact("The detailed procedure describes room temperature; Table 1 reports 25 °C.", PAGE1 + PAGE2),
            fact("Complete conversion of starting material was reported before workup.", PAGE2),
        ])
        unresolved.append("The measurement basis of the reported 3-4% minor isomer is not stated explicitly.")
    else:
        unresolved.extend([
            "Reactant and reagent charge quantities are not reported for this row.",
            "The article says compounds 2b-2i were prepared similarly, but row-specific workup details are not stated.",
        ])
    records.append(record(
        f"table1_entry{entry:02d}", "optimization_entry", evidence,
        participants, steps, outcomes, notes, unresolved))


# Scheme 1 lithium-halide series: three distinct reported conditions.
scheme_rows = [
    ("lii", "LiI", 4, "2a", 82),
    ("libr_h2o", "LiBr.H2O", 13, "2b", 80),
    ("licl_h2o", "LiCl.H2O", 22, "2c", 80),
]
for suffix, reagent_key, time_h, product_label, yield_pct in scheme_rows:
    records.append(record(
        f"scheme1_{suffix}",
        "optimization_entry",
        PAGE1,
        standard_participants("ketone", reagent_key, product_label, PAGE1),
        [reaction_step(time_h, 25, PAGE1)],
        [
            field("product_yield", {"number": yield_pct, "unit": "%"}, PAGE1),
            field("yield_measurement_basis", "isolated", PAGE1),
        ],
        [fact("Scheme 1 lithium-halide condition.", PAGE1)],
        [
            "Reactant and reagent charge quantities, atmosphere, and concentration are not reported.",
            "No associated Supporting Information was supplied in this pilot.",
        ],
    ))


# Equation 1: one reaction producing two separately quantified products.
eq1_participants = [
    participant("substrate", "reactant", "3,4-pentadien-2-one", PAGE1,
                label="1a", smiles="C=C=CC(C)=O"),
    participant("nai", "reagent", "sodium iodide", PAGE1, smiles="[Na+].[I-]"),
    participant("nacl", "reagent", "sodium chloride", PAGE1, smiles="[Na+].[Cl-]"),
    participant("hoac", "solvent", "acetic acid", PAGE1, smiles="CC(=O)O"),
    participant("product_2a", "product", PRODUCTS["2a"][0], PAGE1,
                label="2a", smiles=PRODUCTS["2a"][1], amounts=[]),
    participant("product_2c", "product", PRODUCTS["2c"][0], PAGE1,
                label="2c", smiles=PRODUCTS["2c"][1], amounts=[]),
]
records.append(record(
    "eq1_mixed_nai_nacl", "reported_experiment", PAGE1, eq1_participants,
    [reaction_step(23, 25, PAGE1,
                   ["substrate", "nai", "nacl", "hoac", "product_2a", "product_2c"])],
    [
        field("yield_2a", {"number": 53, "unit": "%"}, PAGE1),
        field("yield_2c", {"number": 26, "unit": "%"}, PAGE1),
        field("product_ratio_2a_to_2c", "2:1", PAGE1),
        field("yield_measurement_basis", "1H NMR using CH2Br2 as internal standard", PAGE1 + PAGE2),
    ],
    [fact("NaI and NaCl were used in a 1:1 ratio.", PAGE1)],
    [
        "Absolute reagent quantities, atmosphere, and concentration are not reported.",
        "No associated Supporting Information was supplied in this pilot.",
    ],
))


# Equations 2 and 3: explicit no-reaction controls/failures.
eq2_participants = [
    participant("allene", "reactant", "1,2-decadiene", PAGE1,
                smiles="C=C=CCCCCCCC"),
    participant("nai", "reagent", "sodium iodide", PAGE1, smiles="[Na+].[I-]"),
    participant("hoac", "solvent", "acetic acid", PAGE1, smiles="CC(=O)O"),
]
records.append(record(
    "eq2_1_2_decadiene_no_reaction", "reported_experiment", PAGE1,
    eq2_participants,
    [reaction_step(7, 70, PAGE1, ["allene", "nai", "hoac"])],
    [
        field("no_reaction_observed", True, PAGE1),
        field("starting_material_recovery", {"number": 82, "unit": "%"}, PAGE1),
        field("measurement_basis", "1H NMR using CH2Br2 as internal standard", PAGE1 + PAGE2),
    ],
    [fact("The allene lacks an electron-withdrawing group.", PAGE1)],
    [
        "Absolute reagent quantities, atmosphere, concentration, and workup are not reported.",
        "No associated Supporting Information was supplied in this pilot.",
    ],
))

eq3_participants = [
    participant("crotonic_acid", "reactant", "crotonic acid", PAGE1,
                smiles="CC=CC(=O)O"),
    participant("nai", "reagent", "sodium iodide", PAGE1, smiles="[Na+].[I-]"),
    participant("hoac", "solvent", "acetic acid", PAGE1, smiles="CC(=O)O"),
]
records.append(record(
    "eq3_crotonic_acid_no_reaction", "reported_experiment", PAGE1,
    eq3_participants,
    [reaction_step(7, 70, PAGE1, ["crotonic_acid", "nai", "hoac"])],
    [
        field("no_reaction_observed", True, PAGE1),
        field("starting_material_recovery", {"number": 98, "unit": "%"}, PAGE1),
        field("measurement_basis", "1H NMR using CH2Br2 as internal standard", PAGE1 + PAGE2),
    ],
    [fact("This control tests a non-cumulated unsaturated acid.", PAGE1)],
    [
        "Absolute reagent quantities, atmosphere, concentration, and workup are not reported.",
        "The crotonic-acid alkene geometry is not specified in the article text.",
        "No associated Supporting Information was supplied in this pilot.",
    ],
))


# Equation 4: stability/isomerization test of isolated product 2a.
eq4_participants = [
    participant("start_2a", "reactant", PRODUCTS["2a"][0], PAGE2,
                label="2a", smiles=PRODUCTS["2a"][1]),
    participant("nai", "reagent", "sodium iodide", PAGE2, smiles="[Na+].[I-]"),
    participant("hoac", "solvent", "acetic acid", PAGE2, smiles="CC(=O)O"),
    participant("recovered_2a", "product", PRODUCTS["2a"][0], PAGE2,
                label="2a", smiles=PRODUCTS["2a"][1], amounts=[]),
    participant("isomer", "product", "4-iodo-3-penten-2-one", PAGE2,
                smiles="CC(=O)C=C(I)C", amounts=[]),
]
records.append(record(
    "eq4_isomerization_test_2a", "reported_experiment", PAGE2,
    eq4_participants,
    [reaction_step(6, 25, PAGE2,
                   ["start_2a", "nai", "hoac", "recovered_2a", "isomer"])],
    [
        field("recovery_2a", {"number": 92, "unit": "%"}, PAGE2),
        field("isomer_yield", {"operator": "<", "number": 2, "unit": "%"}, PAGE2),
        field("yield_measurement_basis", "1H NMR using CH2Br2 as internal standard", PAGE2),
    ],
    [fact("The experiment probes migration of the double bond from the beta,gamma to alpha,beta position.", PAGE2)],
    [
        "Absolute reagent quantities, atmosphere, concentration, and detailed workup are not reported.",
        "The alkene geometry of 4-iodo-3-penten-2-one is not specified.",
        "No associated Supporting Information was supplied in this pilot.",
    ],
))


assert len(records) == 19
out = Path(__file__).with_name("records_pages_0001_0002.json")
out.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
print(f"Wrote {len(records)} records to {out}")
