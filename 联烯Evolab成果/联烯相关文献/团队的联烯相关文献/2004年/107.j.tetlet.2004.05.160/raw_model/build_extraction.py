#!/usr/bin/env python3
"""Build the source-derived, unreviewed records for PDF pages 1--3."""
from __future__ import annotations

import json
from pathlib import Path


DOC = "doc_ffb4f61df7cc04a4"
P1T, P1I = f"{DOC}:page1:text", f"{DOC}:page1:image"
P2T, P2I = f"{DOC}:page2:text", f"{DOC}:page2:image"
P3T, P3I = f"{DOC}:page3:text", f"{DOC}:page3:image"


def fact(value, evidence=()):
    return {
        "value": value,
        "evidence_ids": list(evidence) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def q(number, unit, raw_text=None):
    value = {"number": number, "unit": unit}
    if raw_text is not None:
        value["raw_text"] = raw_text
    return value


def field(name, value, evidence=(), targets=None):
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
        "amounts": amounts or [],
    }


def record(suffix, source_id, kind, evidence, participants, steps, outcomes, *, notes=(), unresolved=()):
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
        "notes": [fact(text, ev) for text, ev in notes],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": list(unresolved),
        },
    }


COMMON_STRUCTURE_UNRESOLVED = (
    "Candidate SMILES were transcribed from a legible drawing or common reagent label but remain unverified.",
    "No supporting information was explicitly associated; atmosphere, workup and purification are not reported in the supplied main text.",
)


def table1_record(entry, i2_equiv, bnsh_equiv, yield_4a, ratio, yield_5a, *,
                  page1=False, temp=5, recovery_1a=None, use_bnssbn=False,
                  detailed_condition_a=False, extra_notes=(), extra_unresolved=()):
    ev = [P2T, P2I]
    if page1:
        ev = [P1T, P1I] + ev
    if detailed_condition_a:
        ev += [P3T, P3I]
    p_ev = tuple(ev)

    substrate_amounts = []
    i2_amounts = [field("equivalents", q(i2_equiv, "equiv"), (P2T, P2I))]
    bnsh_amounts = [field("equivalents", q(bnsh_equiv, "equiv"), (P2T, P2I))]
    mecn_amounts = []
    if detailed_condition_a:
        substrate_amounts.append(field("amount", q(0.5, "mmol"), (P3T, P3I)))
        i2_amounts.append(field("mass", q(190.5, "mg"), (P3T, P3I)))
        bnsh_amounts.append(field("amount", q(0.5, "mmol"), (P3T, P3I)))
        mecn_amounts += [
            field("substrate_solution_volume", q(4, "mL"), (P3T, P3I)),
            field("BnSH_solution_volume", q(2, "mL"), (P3T, P3I)),
        ]

    participants = [
        participant("substrate_1a", "reactant", "1a", p_ev,
                    name="1,2-propadienyl phenyl sulfoxide",
                    smiles="C=C=CS(=O)c1ccccc1", amounts=substrate_amounts),
        participant("iodine", "reagent", "I2", p_ev, name="iodine",
                    smiles="[I][I]", amounts=i2_amounts),
        participant("bnsh", "reagent", "BnSH", p_ev, name="benzyl thiol",
                    smiles="SCc1ccccc1", amounts=bnsh_amounts),
        participant("mecn", "solvent", "MeCN", p_ev, name="acetonitrile",
                    smiles="CC#N", amounts=mecn_amounts),
        participant("product_4a", "product", "E-4a", p_ev,
                    name="E-3-phenylthio-2-iodopropenol",
                    smiles="OCC(I)=CSc1ccccc1"),
        participant("product_5a", "product", "E-5a", p_ev,
                    name="E-3-(phenylsulfinyl)-2-iodopropenol",
                    smiles="OCC(I)=CS(=O)c1ccccc1"),
    ]
    if use_bnssbn:
        participants.append(participant(
            "bnssbn", "reagent", "BnSSBn", (P2T, P2I),
            name="dibenzyl disulfide", smiles="c1ccccc1CSSCc2ccccc2",
        ))
    if detailed_condition_a:
        participants.append(participant(
            "bnssbn_product", "product", "BnSSBn", (P2T, P2I),
            name="dibenzyl disulfide", smiles="c1ccccc1CSSCc2ccccc2",
        ))

    if detailed_condition_a:
        steps = [
            {
                "step_id": "condition_A_iodine_pretreatment",
                "participant_ids": ["substrate_1a", "iodine", "mecn"],
                "conditions": [
                    field("solvent", "anhydrous MeCN (4 mL)", (P3T, P3I)),
                    field("time", q(5, "min"), (P3T, P3I)),
                    field("operation", "A solution of 1a in anhydrous MeCN was treated with solid I2.", (P3T, P3I)),
                ],
            },
            {
                "step_id": "condition_A_BnSH_addition_and_reaction",
                "participant_ids": ["substrate_1a", "iodine", "bnsh", "mecn"],
                "conditions": [
                    field("operation", "A solution of BnSH in MeCN was added with stirring.", (P3T, P3I)),
                    field("temperature", q(temp, "°C"), (P2T, P2I, P3T, P3I)),
                    field("time", q(2, "h"), (P2T, P2I, P3T, P3I)),
                ],
            },
        ]
    else:
        steps = [{
            "step_id": "table1_reaction",
            "participant_ids": [p["entity_id"] for p in participants if p["role"] != "product"],
            "conditions": [
                field("solvent", "MeCN", (P2T, P2I)),
                field("temperature", q(temp, "°C"), (P2T, P2I)),
                field("time", q(2, "h"), (P2T, P2I)),
            ],
        }]

    outcomes = [
        field("yield_4a", q(yield_4a, "%"), (P2T, P2I), ["product_4a"]),
        field("yield_4a_measurement_basis", "isolated" if entry == 1 or detailed_condition_a else None,
              (P1T, P1I) if entry == 1 else ((P3T, P3I) if detailed_condition_a else ()), ["product_4a"]),
        field("yield_5a", q(yield_5a, "%"), (P2T, P2I), ["product_5a"]),
        field("yield_5a_measurement_basis", "isolated", (P2T, P2I), ["product_5a"]),
    ]
    if ratio is not None:
        outcomes.append(field("E_Z_ratio_4a", ratio, (P2T, P2I), ["product_4a"]))
    if recovery_1a is not None:
        outcomes.append(field("recovery_yield_1a", q(recovery_1a, "%"), (P2T, P2I), ["substrate_1a"]))
    if detailed_condition_a:
        outcomes += [
            field("yield_BnSSBn", q(95, "%"), (P2T, P2I), ["bnssbn_product"]),
            field("yield_BnSSBn_measurement_basis", "isolated", (P2T, P2I), ["bnssbn_product"]),
        ]

    notes = list(extra_notes)
    if entry == 5:
        notes.append(("Table 1 footnote b overrides the scheme temperature: this entry was conducted at 15 °C.", (P2T, P2I)))
    if use_bnssbn:
        notes.append(("Table 1 footnote c states that no BnSH was added and that 1a was recovered in 21% yield.", (P2T, P2I)))
    unresolved = list(COMMON_STRUCTURE_UNRESOLVED) + list(extra_unresolved)
    if entry not in (1, 3):
        unresolved.append("The measurement basis for the reported 4a yield is not explicitly assigned by the Table 1 footnote.")
    return record(
        f"table1_entry_{entry:02d}", f"Table 1 entry {entry}", "optimization_entry",
        ev, participants, steps, outcomes, notes=notes, unresolved=unresolved,
    )


records = []
records.append(table1_record(1, 1.2, 1, 37, "96/4", 3, page1=True))
records.append(table1_record(2, 1.5, 0, 14, "96/4", 58, page1=True))
records.append(table1_record(
    3, 1.5, 1, 50, "94/6", 3, page1=True, detailed_condition_a=True,
    extra_notes=((
        "Table 1 entry 3, equation (1), and Table 2 entry 1 report the same 1a/4a result and are represented once with combined evidence.",
        (P1T, P1I, P2T, P2I, P3T, P3I),
    ), (
        "The prose glyph for the isolated disulfide is visually ambiguous (appearing as BuSSBu), while equation (1) and Scheme 2 label BnSSBn; the equation label is retained as the product label pending review.",
        (P2T, P2I, P3T, P3I),
    )),
    extra_unresolved=("Resolve the prose/equation discrepancy in the disulfide abbreviation (BuSSBu versus BnSSBn).",),
))
records.append(table1_record(4, 2, 1, 42, "80/20", 5))
records.append(table1_record(5, 0, 1, 0, None, 0, temp=15))
records.append(table1_record(6, 1.5, 0.5, 38, "74/26", 43))
records.append(table1_record(7, 1.5, 1.2, 32, "80/20", 3))
records.append(table1_record(8, 1.5, 0.75, 55, "60/40", 6))
records.append(table1_record(9, 1.5, 2, 19, "99/1", 1))
records.append(table1_record(10, 1.5, 0, 35, "99/1", 33, recovery_1a=21, use_bnssbn=True,
                             extra_unresolved=("The amount of BnSSBn used in Table 1 entry 10 is not reported.",)))


TABLE2 = [
    (2, "1b", "4b", "H", "H", "n-C4H9", 1.5, -20, 0.5, 65, "95/5"),
    (3, "1c", "4c", "H", "H", "n-C7H15", 1.5, -20, 1.5, 67, "96/4"),
    (4, "1d", "4d", "H", "CH3", "CH3", 1.2, -40, 0.2, 74, "94/6"),
    (5, "1e", "4e", "H", "Et", "C2H5", 1.2, -40, 0.3, 78, "94/6"),
    (6, "1f", "4f", "H", "Et", "Ph", 1.2, -40, 0.25, 59, "99/1"),
    (7, "1g", "4g", "H", "CH3", "i-C4H9", 1.2, -40, 0.3, 72, "98/2"),
    (8, "1h", "4h", "H", "(CH2)5", "(CH2)5", 1.2, -40, 0.15, 79, "99/1"),
    (9, "1i", "4i", "n-C4H9", "CH3", "CH3", 1.2, -40, 0.3, 79, "99/1"),
    (10, "1j", "4j", "H", "H", "i-C3H7", 1.5, -20, 0.8, 80, "97/3"),
]


for entry, substrate_label, product_label, r1, r2, r3, equiv, temp, hours, product_yield, ratio in TABLE2:
    ev = (P3T, P3I)
    substrate_id = f"substrate_{substrate_label}"
    product_id = f"product_{product_label}"
    substituent_text = (
        "R1=H; R2 and R3 jointly form a (CH2)5 ring"
        if entry == 8 else f"R1={r1}, R2={r2}, R3={r3}"
    )
    participants = [
        participant(substrate_id, "reactant", f"{substrate_label} ({substituent_text})", ev,
                    amounts=[field("amount", q(0.4, "mmol"), ev)]),
        participant("bnsh", "reagent", "BnSH", ev, name="benzyl thiol", smiles="SCc1ccccc1",
                    amounts=[field("amount", q(0.4, "mmol"), ev)]),
        participant("iodine", "reagent", "I2", ev, name="iodine", smiles="[I][I]", amounts=[
            field("equivalents", q(equiv, "equiv"), ev),
            field("amount", q(0.48, "mmol"), ev),
        ]),
        participant("mecn", "solvent", "anhydrous MeCN", ev, name="acetonitrile", smiles="CC#N", amounts=[
            field("substrate_solution_volume", q(3.6, "mL"), ev),
            field("iodine_solution_volume", q(2.4, "mL"), ev),
        ]),
        participant(product_id, "product", f"{product_label} ({substituent_text})", ev),
    ]
    unresolved = [
        "The row-specific substrate and product structures are given through a generic R-group scaffold; SMILES are left null pending structure review.",
        "No supporting information was explicitly associated; atmosphere, workup and purification are not reported in the supplied main text.",
    ]
    notes = []
    if equiv == 1.5:
        unresolved.append(
            "Condition B states 0.48 mmol I2 for 0.4 mmol substrate (1.2 equiv), while this row reports 1.5 equiv; both source values are retained without reconciliation."
        )
    records.append(record(
        f"table2_entry_{entry:02d}", f"Table 2 entry {entry}", "substrate_scope_entry", ev,
        participants,
        [{
            "step_id": "condition_B_reaction",
            "participant_ids": [substrate_id, "bnsh", "iodine", "mecn"],
            "conditions": [
                field("operation", "A solution of I2 in anhydrous MeCN (2.4 mL) was added to a solution of substrate 1 and BnSH in anhydrous MeCN (3.6 mL).", ev),
                field("temperature", q(temp, "°C"), ev),
                field("time", q(hours, "h"), ev),
            ],
        }],
        [
            field(f"yield_{product_label}", q(product_yield, "%"), ev, [product_id]),
            field(f"yield_{product_label}_measurement_basis", "isolated", ev, [product_id]),
            field(f"E_Z_ratio_{product_label}", ratio, ev, [product_id]),
        ],
        notes=notes,
        unresolved=unresolved,
    ))


# Equation (2) is a separate control experiment, not a Table 1 duplicate.
ev2 = (P2T, P2I)
records.append(record(
    "equation_2_control", "Equation 2", "reported_experiment", ev2,
    [
        participant("reactant_5a", "reactant", "E-5a", ev2,
                    name="E-3-(phenylsulfinyl)-2-iodopropenol", smiles="OCC(I)=CS(=O)c1ccccc1"),
        participant("bnsh", "reagent", "BnSH", ev2, name="benzyl thiol", smiles="SCc1ccccc1"),
        participant("iodine", "reagent", "I2", ev2, name="iodine", smiles="[I][I]"),
        participant("mecn", "solvent", "MeCN", ev2, name="acetonitrile", smiles="CC#N"),
        participant("product_4a", "product", "E-4a", ev2,
                    name="E-3-phenylthio-2-iodopropenol", smiles="OCC(I)=CSc1ccccc1"),
        participant("recovered_5a", "product", "recovered E-5a", ev2,
                    name="E-3-(phenylsulfinyl)-2-iodopropenol", smiles="OCC(I)=CS(=O)c1ccccc1"),
    ],
    [{
        "step_id": "control_reaction",
        "participant_ids": ["reactant_5a", "bnsh", "iodine", "mecn"],
        "conditions": [
            field("solvent", "MeCN", ev2),
            field("temperature", q(5, "°C"), ev2),
            field("time", q(2, "h"), ev2),
        ],
    }],
    [
        field("yield_4a", q(15, "%"), ev2, ["product_4a"]),
        field("recovery_yield_5a", q(75, "%"), ev2, ["recovered_5a"]),
    ],
    notes=(("The authors use this control to argue that E-4a was not formed by in situ reduction of E-5a.", ev2),),
    unresolved=COMMON_STRUCTURE_UNRESOLVED + (
        "The phrase 'under a set of similar condition' does not provide reagent equivalents for equation (2); they remain missing.",
        "The measurement bases of the 15% product yield and 75% recovery are not explicitly stated.",
    ),
))


# Conceptual arrows are classified as mechanisms and carry no experimental yield.
records.append(record(
    "scheme_1_mechanistic_paths", "Scheme 1", "mechanism", (P1T, P1I, P2T, P2I),
    [
        participant("generic_allenyl_sulfoxide_1", "reactant", "generic 1,2-allenyl sulfoxide", (P2T, P2I)),
        participant("iodine", "reagent", "I2", (P2T, P2I), name="iodine", smiles="[I][I]"),
        participant("cyclic_intermediate_2", "unspecified_agent", "cyclic intermediate 2", (P1T, P1I, P2T, P2I)),
        participant("nucleophile", "reagent", "Nu-", (P2T, P2I)),
        participant("generic_product_3", "product", "proposed 3-type product", (P2T, P2I)),
    ],
    [
        {"step_id": "formation_of_2", "participant_ids": ["generic_allenyl_sulfoxide_1", "iodine", "cyclic_intermediate_2"], "conditions": []},
        {"step_id": "proposed_path_a", "participant_ids": ["cyclic_intermediate_2", "nucleophile", "generic_product_3"], "conditions": []},
        {"step_id": "proposed_path_b", "participant_ids": ["cyclic_intermediate_2"], "conditions": []},
    ],
    [],
    notes=(("Scheme 1 depicts hypothetical paths a and b; the path-b product is marked with a question mark.", (P2T, P2I)),),
    unresolved=(
        "This is a conceptual mechanism, not a reported experiment.",
        "Generic R groups and Nu- prevent assignment of complete structures; the path-b product is unspecified.",
    ),
))


records.append(record(
    "scheme_2_proposed_mechanism", "Scheme 2", "mechanism", (P2T, P2I, P3T, P3I),
    [
        participant("cyclic_intermediate_2", "unspecified_agent", "cyclic intermediate 2", (P2T, P2I, P3T, P3I)),
        participant("bnsh", "reagent", "BnSH", (P2T, P2I, P3T, P3I), name="benzyl thiol", smiles="SCc1ccccc1"),
        participant("cationic_intermediate_6", "unspecified_agent", "cationic allylic alcohol 6", (P2T, P2I, P3T, P3I)),
        participant("bns_cation", "unspecified_agent", "BnS+", (P2T, P2I, P3T, P3I)),
        participant("bnssbn", "product", "BnSSBn", (P2T, P2I, P3T, P3I), name="dibenzyl disulfide", smiles="c1ccccc1CSSCc2ccccc2"),
        participant("generic_product_4", "product", "generic sulfide 4", (P2T, P2I, P3T, P3I)),
    ],
    [
        {"step_id": "proposed_2_to_6", "participant_ids": ["cyclic_intermediate_2", "bnsh", "cationic_intermediate_6"], "conditions": []},
        {"step_id": "proposed_6_to_4", "participant_ids": ["cationic_intermediate_6", "generic_product_4", "bns_cation"], "conditions": []},
        {"step_id": "proposed_disulfide_formation", "participant_ids": ["bns_cation", "bnsh", "bnssbn"], "conditions": []},
    ],
    [],
    notes=(("The authors explicitly describe Scheme 2 as a rationale and state that the real mechanism needs further attention.", (P2T, P2I, P3T, P3I)),),
    unresolved=(
        "This is a proposed mechanism, not a reported experiment.",
        "Generic substituents and charged intermediates are not assigned complete SMILES.",
    ),
))


OUT = Path(__file__).with_name("extraction_records.json")
OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
print(f"wrote {len(records)} records to {OUT}")
