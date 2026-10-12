#!/usr/bin/env python3
"""Build evidence-linked machine records for ja057985a PDF pages 1-2."""
import json
from pathlib import Path

DOC = "doc_c60fdeb47c691cd7"
P1T = f"{DOC}:page1:text"
P1I = f"{DOC}:page1:image"
P2T = f"{DOC}:page2:text"
P2I = f"{DOC}:page2:image"
EV1 = [P1T, P1I]
EV2 = [P2T, P2I]
EV12 = [P1T, P1I, P2T, P2I]


def fact(value, evidence):
    return {
        "value": value,
        "evidence_ids": list(evidence) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def field(name, value, evidence, targets=None):
    result = {"name": name, "fact": fact(value, evidence)}
    if targets:
        result["target_entity_ids"] = list(targets)
    return result


def participant(entity_id, role, label, evidence, *, name=None, smiles=None, amounts=None):
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


def record(suffix, source_id, kind, evidence, participants, steps, outcomes, notes, unresolved):
    return {
        "record_id": f"{DOC}:{suffix}",
        "document_id": DOC,
        "source_reaction_id": source_id,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": list(evidence),
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


def common_missing_conditions(evidence, atmosphere=None):
    return [
        field("atmosphere", atmosphere, evidence),
        field("workup", None, evidence),
        field("purification", None, evidence),
    ]


def scheme1_variant(suffix, temperature, time_h, yield_pct, *, sealed=False, recovery=None):
    r = "reactant_1aa"
    p = "product_2aa"
    s = "solvent_xylene"
    conditions = [
        field("temperature", {"number": temperature, "unit": "°C"}, EV1),
        field("time", {"number": time_h, "unit": "h"}, EV1),
        field("solvent", "xylene", EV1),
    ]
    if sealed:
        conditions.append(field("operation", "sealed", EV1))
    conditions.extend(common_missing_conditions(EV1))
    outcomes = [
        field("yield", {"number": yield_pct, "unit": "%"}, EV1, [p]),
        field("yield_measurement_basis", None, EV1, [p]),
    ]
    if recovery is not None:
        outcomes.append(field("starting_material_recovery", {"number": recovery, "unit": "%"}, EV1, [r]))
    return record(
        suffix,
        f"Scheme 1; {temperature} °C, {time_h} h",
        "optimization_entry",
        EV1,
        [
            participant(r, "reactant", "1aa", EV1,
                        name="3-allyl-4-(3′-ethylpenta-1′,2′-dienyl)-5-phenylfuran-2(5H)-one"),
            participant(p, "product", "2aa", EV1),
            participant(s, "solvent", None, EV1, name="xylene"),
        ],
        [{"step_id": "thermal_cyclization", "participant_ids": [r, s], "conditions": conditions}],
        outcomes,
        ["Scheme 1 optimization result; the product is described as a formal Alder–ene-type product."],
        [
            "No reaction scale or xylene volume is stated for this Scheme 1-only condition.",
            "Yield measurement basis, workup, and purification are not reported in the supplied main-text pages.",
            "The complex structures of 1aa and 2aa were not transcribed to SMILES by the machine record.",
            "Supporting Information is mentioned but was not supplied or associated.",
        ],
    )


def scope_entry(entry, substrate, product, yield_pct, *, time_h=6, temperature=100,
                unidentified=False):
    r = f"reactant_{substrate}"
    p = f"product_{product}"
    s = "solvent_xylene"
    participants = [
        participant(
            r,
            "reactant",
            substrate,
            EV1,
            amounts=[field("reaction_scale", {"minimum": 0.15, "maximum": 0.25, "unit": "mmol", "raw_text": "0.15–0.25 mmol"}, EV1)],
        ),
        participant(p, "product", product, EV1),
        participant(
            s,
            "solvent",
            None,
            EV1,
            name="xylene",
            amounts=[field("volume", {"number": 4, "unit": "mL"}, EV1)],
        ),
    ]
    outcomes = [
        field("yield", {"number": yield_pct, "unit": "%"}, EV1, [p]),
        field("yield_measurement_basis", None, EV1, [p]),
    ]
    notes = [f"Table 1 entry {entry}; substituent identities are encoded by the displayed substrate/product labels and drawings."]
    unresolved = [
        "Yield measurement basis, workup, and purification are not reported in the supplied main-text pages.",
        f"The complex displayed structures of {substrate} and {product} were not transcribed to SMILES by the machine record.",
        "Supporting Information is mentioned but was not supplied or associated.",
    ]
    if unidentified:
        u = "product_unidentified"
        participants.append(participant(u, "product", "unidentified product", EV1))
        outcomes.extend([
            field("yield_by_weight", {"number": 10, "unit": "%", "qualifier": "approx", "raw_text": "about 10% yield by weight"}, EV1, [u]),
            field("yield_measurement_basis", "by weight", EV1, [u]),
        ])
        notes.append("Table footnote c reports an unidentified product in about 10% yield by weight.")
        unresolved.append("The footnote-c byproduct identity is not reported.")
    return record(
        f"table1_entry_{entry:02d}",
        f"Table 1 entry {entry}",
        "substrate_scope_entry",
        EV1,
        participants,
        [{
            "step_id": "thermal_cyclization",
            "participant_ids": [r, s],
            "conditions": [
                field("temperature", {"number": temperature, "unit": "°C"}, EV1),
                field("time", {"number": time_h, "unit": "h"}, EV1),
                field("solvent", "xylene", EV1),
                field("atmosphere", "argon", EV1),
                field("workup", None, EV1),
                field("purification", None, EV1),
            ],
        }],
        outcomes,
        notes,
        unresolved,
    )


def maleimide(entity_id, evidence):
    return participant(
        entity_id,
        "reagent",
        "3",
        evidence,
        name="N-ethylmaleimide",
        smiles="CCN1C(=O)C=CC1=O",
        amounts=[field("equivalents", {"number": 2.0, "unit": "equiv"}, evidence)],
    )


def scheme2_record(suffix, source_id, reactant_label, product_yields, time_h, recovery=None):
    reactant = f"reactant_{reactant_label}"
    reagent = "dienophile_3"
    solvent = "solvent_xylene"
    evidence = EV12
    participants = [
        participant(reactant, "reactant", reactant_label, evidence),
        maleimide(reagent, evidence),
        participant(solvent, "solvent", None, evidence, name="xylene"),
    ]
    outcomes = []
    for product_label, pct in product_yields:
        product_id = f"product_{product_label}"
        participants.append(participant(product_id, "product", product_label, evidence))
        outcomes.append(field("yield", {"number": pct, "unit": "%"}, evidence, [product_id]))
        outcomes.append(field("yield_measurement_basis", None, evidence, [product_id]))
    if recovery is not None:
        outcomes.append(field("starting_material_recovery", {"number": recovery, "unit": "%"}, evidence, [reactant]))
    return record(
        suffix,
        source_id,
        "reported_experiment",
        evidence,
        participants,
        [{
            "step_id": "mechanistic_probe",
            "participant_ids": [reactant, reagent, solvent],
            "conditions": [
                field("temperature", {"number": 55, "unit": "°C"}, evidence),
                field("time", {"number": time_h, "unit": "h"}, evidence),
                field("solvent", "xylene", evidence),
                field("atmosphere", None, evidence),
                field("workup", None, evidence),
                field("purification", None, evidence),
            ],
        }],
        outcomes,
        ["Scheme 2 mechanistic control experiment. The product percentages are reported on the scheme."],
        [
            "Reaction scale, xylene volume, atmosphere, yield measurement basis, workup, and purification are not reported in the supplied main-text pages.",
            "Only dienophile 3 received a machine-transcribed candidate SMILES; all structures remain unverified.",
            "Supporting Information is mentioned but was not supplied or associated.",
        ],
    )


records = [
    scheme1_variant("scheme1_170c_9_5h", 170, 9.5, 74, sealed=True),
    # The 100 °C/6 h/89% Scheme 1 line is the same experiment as Table 1 entry 1.
    scheme1_variant("scheme1_80c_6h", 80, 6, 24, recovery=35),
]

scope_rows = [
    (1, "1aa", "2aa", 89, 6, 100, False),
    (2, "1ab", "2ab", 84, 7, 100, False),
    (3, "1ac", "2ac", 80, 6, 100, False),
    (4, "1ad", "2ad", 67, 6, 100, True),
    (5, "1ba", "2ba", 97, 6, 100, False),
    (6, "1bb", "2bb", 87, 6, 100, False),
    (7, "1ca", "2ca", 95, 6, 100, False),
    (8, "1cb", "2cb", 84, 6, 100, False),
    (9, "1cd", "2cd", 66, 6, 100, True),
    (10, "1da", "2da", 83, 6, 100, False),
    (11, "1de", "2de", 74, 6, 100, False),
    (12, "1df", "2df", 48, 6, 100, False),
    (13, "1ea", "2ea", 84, 6, 100, False),
    (14, "1ec", "2ec", 89, 6, 100, False),
    (15, "1f", "2f", 56, 2, 90, False),
]
records.extend(
    scope_entry(entry, substrate, product, yield_pct,
                time_h=time_h, temperature=temperature, unidentified=unidentified)
    for entry, substrate, product, yield_pct, time_h, temperature, unidentified in scope_rows
)

records.extend([
    scheme2_record(
        "scheme2_1f_plus_3",
        "Scheme 2: 1f + 3",
        "1f",
        [("2f", 48), ("4f", 26)],
        24,
    ),
    scheme2_record(
        "scheme2_2f_plus_3",
        "Scheme 2: 2f + 3",
        "2f",
        [("4f", 53)],
        24,
        recovery=28,
    ),
    scheme2_record(
        "scheme2_1g_plus_3",
        "Scheme 2: 1g + 3",
        "1g",
        [("4g", 77)],
        21.5,
    ),
])

records.append(record(
    "scheme3_plausible_mechanism",
    "Scheme 3",
    "mechanism",
    EV2,
    [
        participant("mechanism_1f", "reactant", "1f", EV2),
        participant("mechanism_6", "unspecified_agent", "6", EV2),
        participant("mechanism_5", "unspecified_agent", "5", EV2),
        participant("mechanism_7", "unspecified_agent", "7", EV2),
        participant("mechanism_2f", "product", "2f", EV2),
        participant(
            "mechanism_3",
            "reagent",
            "3",
            EV2,
            name="N-ethylmaleimide",
            smiles="CCN1C(=O)C=CC1=O",
        ),
        participant("mechanism_4f", "product", "4f", EV2),
    ],
    [],
    [],
    [
        "Plausible pathway A: 1f undergoes thermal [2+2] cycloaddition to 6, [1,5]-H migration to 5, and electrocyclic rearrangement to 2f.",
        "Plausible pathway B: 1f undergoes 1,5-H shift to tetraene 7 followed by 8π-electrocyclization to 2f.",
        "In the presence of dienophile 3, proposed intermediate 5 may undergo Diels–Alder reaction to afford 4f.",
    ],
    [
        "Scheme 3 is a proposed mechanism, not an independently reported experimental procedure.",
        "Structures of intermediates 5, 6, and 7 were not transcribed to SMILES by the machine record.",
    ],
))

out = Path(__file__).with_name("records_pages_0001_0002.json")
out.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
print(f"wrote {len(records)} records to {out}")
