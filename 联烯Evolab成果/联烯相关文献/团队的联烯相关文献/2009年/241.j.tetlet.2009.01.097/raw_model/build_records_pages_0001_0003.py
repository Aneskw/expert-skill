#!/usr/bin/env python3
"""Build machine-only records for PDF pages 1--3 of doc_55f02dd1b347e86e."""

import json
from pathlib import Path


DOC = "doc_55f02dd1b347e86e"
OUT = Path(__file__).with_name("records_pages_0001_0003.json")
P1T = f"{DOC}:page1:text"
P1I = f"{DOC}:page1:image"
P2T = f"{DOC}:page2:text"
P2I = f"{DOC}:page2:image"
P3T = f"{DOC}:page3:text"
P3I = f"{DOC}:page3:image"
P1 = [P1T, P1I]
P2 = [P2T, P2I]
P3 = [P3T, P3I]


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


def participant(entity_id, role, label, evidence, *, name=None, smiles=None, amounts=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence),
        "smiles": fact(smiles, evidence),
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
        "notes": [fact(value, ev) for value, ev in notes],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": list(unresolved),
        },
    }


SMILES_1A = "CCCCC1=CC1(C(=O)OC)C(=O)OC"
SMILES_2 = "C=C(S(=O)(=O)c1ccccc1)S(=O)(=O)c1ccccc1"
SMILES_3A = "COC(=O)C(=C(CCCC)C1CC1(S(=O)(=O)c2ccccc2)S(=O)(=O)c2ccccc2)C(=O)OC"
SOLVENT_SMILES = {
    "THF": "C1CCOC1",
    "acetone": "CC(=O)C",
    "NMP": "CN1CCCC1=O",
    "DCE": "ClCCCl",
    "CH3CN": "CC#N",
    "toluene": "Cc1ccccc1",
    "DMF": "CN(C)C=O",
    "CH3NO2": "C[N+](=O)[O-]",
    "DME": "COCCOC",
    "dioxane": "O1CCOCC1",
}


def amount_equiv(number, evidence):
    return field("equivalents", {"number": number, "unit": "equiv"}, evidence)


def base_1a(evidence):
    return participant(
        "substrate_1a",
        "reactant",
        "1a",
        evidence,
        name="dimethyl 2-butylcycloprop-2-ene-1,1-dicarboxylate",
        smiles=SMILES_1A,
    )


def reagent_2(evidence, equivalents):
    return participant(
        "reagent_2",
        "reactant",
        "2",
        evidence,
        name="1,1-bis(phenylsulfonyl)ethylene",
        smiles=SMILES_2,
        amounts=[amount_equiv(equivalents, evidence)] if equivalents is not None else [],
    )


def product_3a(evidence):
    return participant(
        "product_3a",
        "product",
        "3a",
        evidence,
        name="dimethyl 2-(1-(2,2-bis(phenylsulfonyl)cyclopropyl)pentylidene)malonate",
        smiles=SMILES_3A,
    )


def nai(evidence, equivalents):
    return participant(
        "nai",
        "catalyst",
        "NaI",
        evidence,
        name="sodium iodide",
        smiles="[Na+].[I-]",
        amounts=[amount_equiv(equivalents, evidence)],
    )


def carbonate(evidence, equivalents):
    return participant(
        "na2co3",
        "reagent",
        "Na2CO3",
        evidence,
        name="sodium carbonate",
        smiles="[Na+].[Na+].[O-]C([O-])=O",
        amounts=[amount_equiv(equivalents, evidence)],
    )


def solvent(name, evidence):
    return participant(
        "solvent",
        "solvent",
        name,
        evidence,
        name=name,
        smiles=SOLVENT_SMILES[name],
    )


def missing_operations():
    return [
        field("atmosphere", None, []),
        field("workup", None, []),
        field("purification", None, []),
    ]


records = []

# Table 1: each condition row is an independent optimization entry.  Footnotes
# override the shared 0.2 equiv NaI / 1.0 equiv reagent-2 header.
table1 = [
    (1, "THF", 1.0, "reflux", {"number": 1, "unit": "h"}, 75, 1.0, 1.0),
    (2, "THF", 1.0, "reflux", {"number": 1, "unit": "h"}, 81, 1.0, 1.2),
    (3, "THF", 1.0, "reflux", {"number": 1, "unit": "h"}, 77, 0.2, 1.0),
    (4, "THF", 1.0, "reflux", {"number": 17.6, "unit": "h"}, 0, None, 1.0),
    (5, "THF", 0.5, "reflux", {"number": 1, "unit": "h"}, 78, 0.2, 1.0),
    (6, "THF", None, "reflux", {"number": 1, "unit": "h"}, 81, 0.2, 1.0),
    (7, "acetone", None, "reflux", {"number": 11, "unit": "h"}, 70, 0.2, 1.0),
    (8, "NMP", None, {"number": 60, "unit": "°C"}, {"number": 10, "unit": "h"}, 67, 0.2, 1.0),
    (9, "DCE", None, {"minimum": 60, "maximum": 80, "unit": "°C", "raw_text": "60–80 °C"}, {"number": 24, "unit": "h"}, 52, 0.2, 1.0),
    (10, "CH3CN", None, {"minimum": 60, "maximum": 80, "unit": "°C", "raw_text": "60–80 °C"}, {"number": 24, "unit": "h"}, 46, 0.2, 1.0),
    (11, "toluene", None, ("program", {"number": 60, "unit": "°C"}, "reflux"), {"number": 24, "unit": "h"}, 45, 0.2, 1.0),
    (12, "DMF", None, {"number": 60, "unit": "°C"}, {"number": 24, "unit": "h"}, 32, 0.2, 1.0),
    (13, "CH3NO2", None, {"number": 60, "unit": "°C"}, {"number": 11, "unit": "h"}, 0, 0.2, 1.0),
    (14, "DME", None, {"number": 60, "unit": "°C"}, {"number": 11, "unit": "h"}, 0, 0.2, 1.0),
    (15, "dioxane", None, ("program", {"number": 60, "unit": "°C"}, "reflux"), {"number": 26, "unit": "h"}, 0, 0.2, 1.0),
]

for entry, solv, additive_eq, temperature, time, yield_pct, nai_eq, reagent_eq in table1:
    row_ev = P2
    top_ev = list(P2)
    if entry in (1, 4, 6):
        top_ev += P1
    if entry == 1:
        top_ev += P3
    parts = [base_1a(row_ev), reagent_2(row_ev, reagent_eq), product_3a(row_ev)]
    if nai_eq is not None:
        parts.append(nai(row_ev, nai_eq))
    if additive_eq is not None:
        parts.append(carbonate(row_ev, additive_eq))
    parts.append(solvent(solv, row_ev))
    conditions = [field("solvent", solv, row_ev)]
    if isinstance(temperature, tuple):
        conditions += [
            field("temperature_initial", temperature[1], row_ev),
            field("temperature_final", temperature[2], row_ev),
        ]
    else:
        conditions.append(field("temperature", temperature, row_ev))
    conditions += [field("time", time, row_ev)] + missing_operations()
    outcomes = [
        field(
            "reported_isolated_yield",
            {"number": yield_pct, "unit": "%"},
            row_ev,
            ["product_3a"],
        ),
        field("yield_measurement_basis", "isolated yield", row_ev, ["product_3a"]),
    ]
    notes = [(f"Table 1 entry {entry}.", row_ev)]
    unresolved = [
        "Reaction scale, atmosphere, workup, purification, and exact substrate amount are not reported in the main-text table.",
        "Candidate structures are machine interpretations of the source drawing and remain unverified.",
    ]
    if additive_eq is None:
        notes.append(("The Na2CO3 additive column contains the source marker —.", row_ev))
    if entry == 1:
        notes += [
            ("The opening prose describes this initial trial and reports the same 75% yield.", P1),
            ("The structure of 3a was established by X-ray diffraction; CCDC 712641 is reported.", P1 + P3),
        ]
    if entry == 4:
        outcomes.append(
            field(
                "recovered_starting_material_yield",
                {"number": 88, "unit": "%"},
                row_ev,
                ["substrate_1a"],
            )
        )
        notes.append(("The reaction was conducted in the absence of NaI; no reaction was observed.", P1 + P2))
    if entry in (13, 14):
        notes.append(("The reaction was complicated.", row_ev))
    if entry == 15:
        outcomes.append(
            field(
                "recovered_starting_material_yield",
                {"number": 69, "unit": "%"},
                row_ev,
                ["substrate_1a"],
            )
        )
    records.append(
        record(
            f"table1_entry{entry}",
            "optimization_entry",
            top_ev,
            parts,
            [{"step_id": "reaction", "participant_ids": [p["entity_id"] for p in parts], "conditions": conditions}],
            outcomes,
            notes,
            unresolved,
        )
    )


# Table 2 shared conditions: 2 (1.0 equiv), NaI (0.2 equiv), THF, reflux.
table2 = [
    (1, "Ph", "CO2Me", "1b", 2.7, 76, "3b"),
    (2, "TBSOCH2CH2CH2", "CO2Me", "1c", 1, 75, "3c"),
    (3, "p-MeC6H4", "CO2Me", "1d", 2, 81, "3d"),
    (4, "THPOCH2CH2CH2", "CO2Me", "1e", 2.3, 76, "3e"),
    (5, "n-C8H17", "CO2Me", "1f", 9, 68, "3f"),
    (6, "Bn", "CO2Me", "1g", 10, 76, "3g"),
    (7, "PhCH2CH2", "CO2Me", "1h", 10, 85, "3h"),
    (8, "p-NO2C6H4", "CO2Me", "1i", 1, 82, "3i"),
    (9, "n-C4H9", "CO2Bn", "1j", 9, 68, "3j"),
]

for entry, r1, r2, substrate_label, time_h, yield_pct, product_label in table2:
    evidence = P1 + P2
    row_ev = P2
    substrate = participant(
        "substrate",
        "reactant",
        substrate_label,
        row_ev,
        name=f"cyclopropene {substrate_label} (R1={r1}; R2={r2})",
        smiles=None,
    )
    product = participant(
        "product",
        "product",
        product_label,
        row_ev,
        name=f"vinyl cyclopropane {product_label} derived from {substrate_label}",
        smiles=None,
    )
    parts = [
        substrate,
        reagent_2(row_ev, 1.0),
        product,
        nai(row_ev, 0.2),
        solvent("THF", row_ev),
    ]
    conditions = [
        field("solvent", "THF", row_ev),
        field("temperature", "reflux", row_ev),
        field("time", {"number": time_h, "unit": "h"}, row_ev),
    ] + missing_operations()
    outcomes = [
        field(
            "reported_isolated_yield",
            {"number": yield_pct, "unit": "%"},
            row_ev,
            ["product"],
        ),
        field("yield_measurement_basis", "isolated yield", row_ev, ["product"]),
    ]
    notes = [
        (f"Table 2 entry {entry}; R1={r1}, R2={r2}.", row_ev),
    ]
    if entry in (3, 9):
        notes.append(("The acknowledgments state that Table 2 entries 3 and 9 were reproduced by Ping Lu.", P2))
    records.append(
        record(
            f"table2_entry{entry}",
            "substrate_scope_entry",
            evidence,
            parts,
            [{"step_id": "reaction", "participant_ids": [p["entity_id"] for p in parts], "conditions": conditions}],
            outcomes,
            notes,
            [
                "Reaction scale, atmosphere, workup, and purification are not reported in the main-text table.",
                "The R-group structures and product connectivity were not independently structure-verified; substrate and product SMILES remain missing.",
            ],
        )
    )


# Prose-only unsuccessful cases.  They remain partial because the paper does not
# provide rows, times, yields, or fully separable substrate identities.
failure_ev = P1

parts = [
    participant("substrate", "reactant", "cyclopropene (R1=t-Bu; R2=CO2Me)", failure_ev),
    reagent_2(failure_ev, None),
    participant("expected_product", "product", "expected vinyl cyclopropane (not formed)", failure_ev),
]
records.append(
    record(
        "prose_tbu_no_reaction",
        "substrate_scope_entry",
        failure_ev,
        parts,
        [{
            "step_id": "reported_trial",
            "participant_ids": [p["entity_id"] for p in parts],
            "conditions": [
                field("temperature", None, []),
                field("time", None, []),
                field("solvent", None, []),
            ] + missing_operations(),
        }],
        [
            field("product_yield", None, [], ["expected_product"]),
            field("reaction_result", "no reaction", failure_ev, ["expected_product"]),
            field("recovered_starting_material", "recovered; percentage not reported", failure_ev, ["substrate"]),
        ],
        [("The starting material was recovered, but no recovery percentage is stated.", failure_ev)],
        [
            "Exact conditions, quantities, duration, and recovery percentage are not reported.",
            "The expected product structure is not shown and remains unencoded.",
        ],
    )
)

parts = [
    participant(
        "substrate_group",
        "reactant",
        "substrate(s): R1=Ph or n-C4H9; R2 or R3=acyl",
        failure_ev,
    ),
    reagent_2(failure_ev, None),
    participant("expected_product", "product", "expected product(s) (not formed)", failure_ev),
]
records.append(
    record(
        "prose_acyl_substrates_no_product",
        "unresolved",
        failure_ev,
        parts,
        [],
        [field("reaction_result", "no expected product was formed", failure_ev, ["expected_product"])],
        [("The prose groups R1=Ph or n-C4H9 with R2 or R3=acyl and does not enumerate individual trials.", failure_ev)],
        [
            "The number and exact identities of experiments cannot be separated from the source sentence.",
            "Conditions, quantities, time, and exact acyl substitution are not reported.",
        ],
    )
)

parts = [
    participant("substrate", "reactant", "cyclopropene (R1=unprotected alcohol; R2=CO2Me)", failure_ev),
    reagent_2(failure_ev, None),
    participant("expected_product", "product", "expected vinyl cyclopropane", failure_ev),
]
records.append(
    record(
        "prose_unprotected_alcohol_complicated",
        "substrate_scope_entry",
        failure_ev,
        parts,
        [{
            "step_id": "reported_trial",
            "participant_ids": [p["entity_id"] for p in parts],
            "conditions": [
                field("temperature", None, []),
                field("time", None, []),
                field("solvent", None, []),
            ] + missing_operations(),
        }],
        [
            field("product_yield", None, [], ["expected_product"]),
            field("reaction_result", "complicated reaction", failure_ev, ["expected_product"]),
        ],
        [],
        [
            "The unprotected alcohol substituent is not fully specified.",
            "Exact conditions, quantities, duration, product identity, and yield are not reported.",
        ],
    )
)


# Scheme 1 is explicitly a plausible mechanism, not a reported batch.
mechanism_ev = P1 + P2
mechanism_parts = [
    base_1a(P2),
    participant("iodide", "unspecified_agent", "I−", P1 + P2, name="iodide", smiles="[I-]"),
    participant("intermediate_4a", "unspecified_agent", "4a", P1 + P2),
    reagent_2(P1 + P2, None),
    participant("intermediate_5a", "unspecified_agent", "5a", P1 + P2),
    product_3a(P1 + P2),
]
records.append(
    record(
        "scheme1_plausible_mechanism",
        "mechanism",
        mechanism_ev,
        mechanism_parts,
        [
            {
                "step_id": "iodide_ring_opening",
                "participant_ids": ["substrate_1a", "iodide", "intermediate_4a"],
                "conditions": [field("operation", "regioselective iodide attack and cyclopropene ring opening", P1 + P2)],
            },
            {
                "step_id": "addition_to_2",
                "participant_ids": ["intermediate_4a", "reagent_2", "intermediate_5a"],
                "conditions": [field("operation", "carbanion 4a attacks 1,1-bis(phenylsulfonyl)ethylene", P1 + P2)],
            },
            {
                "step_id": "ring_closure",
                "participant_ids": ["intermediate_5a", "product_3a"],
                "conditions": [field("operation", "intramolecular nucleophilic substitution", P1 + P2)],
            },
        ],
        [],
        [("Scheme 1 is labeled a plausible mechanism and is not an isolated experimental sequence.", P1 + P2)],
        [
            "Intermediates 4a and 5a are proposed, not reported as isolated compounds.",
            "Their structures remain unencoded pending chemistry review.",
        ],
    )
)


assert len(records) == 28
assert len({r["record_id"] for r in records}) == len(records)
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
print(f"wrote {len(records)} records to {OUT}")
