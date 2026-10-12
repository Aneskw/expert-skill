#!/usr/bin/env python3
"""Build the evidence-linked raw extraction for PDF pages 1--3."""
import json
from pathlib import Path

DOC = "doc_4f67befc97ec7e2c"
OUT = Path(__file__).with_name("records_pages_0001_0003.json")


def fact(value, evidence):
    return {
        "value": value,
        "evidence_ids": list(evidence) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


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


def field(name, value, evidence, targets=None):
    result = {"name": name, "fact": fact(value, evidence)}
    if targets:
        result["target_entity_ids"] = list(targets)
    return result


def qty(number, unit, raw_text=None, qualifier=None):
    result = {"number": number, "unit": unit}
    if raw_text is not None:
        result["raw_text"] = raw_text
    if qualifier is not None:
        result["qualifier"] = qualifier
    return result


def rec(suffix, kind, evidence, participants, steps, outcomes=None, notes=None, unresolved=None):
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
        "notes": [fact(n, evidence) for n in (notes or [])],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved or [],
        },
    }


EV1 = [f"{DOC}:page1:text", f"{DOC}:page1:image"]
EV2 = [f"{DOC}:page2:text", f"{DOC}:page2:image"]
EV3 = [f"{DOC}:page3:text", f"{DOC}:page3:image"]
records = []

# Page 1: abstract-level generic transformation. R1/R2 make both structures generic.
p = [
    participant("abs_1", "reactant", EV1, "1", "generic 1,2-allenyl phenyl sulfide", None),
    participant("abs_i2", "reagent", EV1, None, "iodine", "[I][I]"),
    participant("abs_acetone", "solvent", EV1, None, "acetone", "CC(=O)C"),
    participant("abs_water", "solvent", EV1, None, "water", "O"),
    participant("abs_4", "product", EV1, "(Z)-4", "generic (Z)-3-organosulfur-2-iodo-2-propenol", None),
]
records.append(rec(
    "abstract_general_scheme", "general_scheme", EV1, p,
    [{"step_id": "abstract_arrow", "participant_ids": [x["entity_id"] for x in p], "conditions": [
        field("solvent", "acetone/H2O (4:1)", EV1), field("temperature", "r.t.", EV1)
    ]}],
    notes=["Abstract graphic is a generic transformation and not an individual reported experiment."],
    unresolved=["Generic R1/R2 structures cannot be converted to complete SMILES.", "Reaction time, scale, workup, and yield are not reported in the abstract graphic."],
))

# Shared Table 1 structures and rows.
t1_rows = [
    (1, "CH3CN/H2O = 4:1", 16, 15, 30, "1.08:1", 0, None, 2),
    (2, "CH3CN/H2O = 4:1", 16, 28, 16, "0.32:1", 0, None, 2),
    (3, "acetone/H2O = 2:1", 10, 0, 8, "1.07:1", 50, ">99:1", 2),
    (4, "acetone/H2O = 2:1", 10, 0, 22, "1.28:1", 62, ">99:1", 4),
    (5, "acetone/H2O = 4:1", 11, 15, 16, "1.40:1", 66, ">99:1", 2),
    (6, "acetone/H2O = 4:1", 13, 28, 16, "1.09:1", 68, ">99:1", 2),
    (7, "acetone/H2O = 2:1", 10.5, 15, 12, "1.07:1", 66, ">99:1", 2),
]
for entry, solvent_ratio, hours, temp, y2a, ratio2a, y4a, ratio4a, i2eq in t1_rows:
    solvent_name = "acetonitrile" if solvent_ratio.startswith("CH3CN") else "acetone"
    solvent_smiles = "CC#N" if solvent_name == "acetonitrile" else "CC(=O)C"
    prefix = f"t1e{entry}"
    ps = [
        participant(f"{prefix}_1a", "reactant", EV2, "1a", "3-benzyl-1,2-butadienyl phenyl sulfide", "c1ccccc1SC=C=C(C)Cc1ccccc1"),
        participant(f"{prefix}_i2", "reagent", EV2, None, "iodine", "[I][I]", [field("equivalents", qty(i2eq, "equiv", f"{i2eq} equiv"), EV2)]),
        participant(f"{prefix}_orgsolv", "solvent", EV2, None, solvent_name, solvent_smiles),
        participant(f"{prefix}_water", "solvent", EV2, None, "water", "O"),
        participant(f"{prefix}_2a", "product", EV2, "2a", "2-iodo-2-propenal product 2a", None),
        participant(f"{prefix}_4a", "product", EV2, "(Z)-4a", "(Z)-iodohydroxylation product 4a", "c1ccccc1S/C=C(\\I)C(O)(C)Cc1ccccc1"),
    ]
    conds = [
        field("solvent", solvent_ratio, EV2),
        field("time", qty(hours, "h", f"{hours} h"), EV2),
        field("temperature", qty(temp, "°C", f"{temp} °C"), EV2),
    ]
    outs = [
        field("isolated_yield_2a", qty(y2a, "%", f"{y2a}%"), EV2, [f"{prefix}_2a"]),
        field("E_Z_ratio_2a", ratio2a, EV2, [f"{prefix}_2a"]),
        field("yield_measurement_basis_2a", "isolated yield", EV2, [f"{prefix}_2a"]),
        field("isolated_yield_Z_4a", qty(y4a, "%", f"{y4a}%"), EV2, [f"{prefix}_4a"]),
        field("yield_measurement_basis_Z_4a", "isolated yield", EV2, [f"{prefix}_4a"]),
    ]
    if ratio4a is not None:
        outs.append(field("Z_E_ratio_Z_4a", ratio4a, EV2, [f"{prefix}_4a"]))
    if entry in (4, 5):
        outs.append(field("stereoisomer_ratio_measurement_basis_2a", "determined by isolation", EV2, [f"{prefix}_2a"]))
    else:
        outs.append(field("stereoisomer_ratio_measurement_basis_2a", "1H NMR", EV2, [f"{prefix}_2a"]))
    records.append(rec(
        f"table1_entry_{entry}", "optimization_entry", EV2, ps,
        [{"step_id": "iodohydroxylation", "participant_ids": [x["entity_id"] for x in ps[:4]], "conditions": conds}],
        outs,
        notes=["Table 1 reports separate yields for regioisomeric products 2a and (Z)-4a."],
        unresolved=["The structure of 2a was not assigned a SMILES because the drawn substituent connectivity is not sufficiently certain from the page image alone.", "Reaction scale, detailed procedure, workup, and purification are absent from the main-text table; SI was not provided."],
    ))

# Scheme 1 is mechanistic interpretation of the Table 1 chemistry, not extra experiments.
scheme1_1a = participant("s1a_1a", "reactant", EV2, "1a", "3-benzyl-1,2-butadienyl phenyl sulfide", "c1ccccc1SC=C=C(C)Cc1ccccc1")
scheme1_ip = participant("s1a_ip", "reagent", EV2, "I+", "electrophilic iodine", None)
scheme1_3a = participant("s1a_3a", "unspecified_agent", EV2, "3a", "proposed 2,1-iodohydroxylation intermediate", None)
scheme1_2a = participant("s1a_2a", "product", EV2, "2a", "2-iodo-2-propenal product 2a", None)
records.append(rec(
    "scheme1_path_a", "mechanism", EV2, [scheme1_1a, scheme1_ip, scheme1_3a, scheme1_2a],
    [
        {"step_id": "path_a_intermediate", "participant_ids": ["s1a_1a", "s1a_ip", "s1a_3a"], "conditions": [field("operation", "proposed path a", EV2)]},
        {"step_id": "path_a_hydrolysis", "participant_ids": ["s1a_3a", "s1a_2a"], "conditions": [field("operation", "hydrolysis", EV2)]},
    ],
    notes=["Scheme 1 path a is a proposed mechanism used to rationalize formation of 2a."],
    unresolved=["Intermediate 3a and product 2a structures are not encoded as SMILES because exact connectivity/stereochemistry remains uncertain from the drawing.", "No independent yield or experimental conditions are assigned to this mechanistic path."],
))
scheme1b = [
    participant("s1b_1a", "reactant", EV2, "1a", "3-benzyl-1,2-butadienyl phenyl sulfide", "c1ccccc1SC=C=C(C)Cc1ccccc1"),
    participant("s1b_ip", "reagent", EV2, "I+", "electrophilic iodine", None),
    participant("s1b_4a", "product", EV2, "(Z)-4a", "(Z)-iodohydroxylation product 4a", "c1ccccc1S/C=C(\\I)C(O)(C)Cc1ccccc1"),
]
records.append(rec(
    "scheme1_path_b", "mechanism", EV2, scheme1b,
    [{"step_id": "path_b", "participant_ids": [x["entity_id"] for x in scheme1b], "conditions": [field("operation", "proposed path b", EV2)]}],
    notes=["Scheme 1 path b is a proposed mechanistic route to (Z)-4a, not an additional experiment."],
    unresolved=["No independent time, temperature, or yield is assigned to this mechanistic arrow."],
))

# Table 2 substrate-scope rows. Aldehyde byproduct labels are row-specific and have no assigned SMILES.
t2_rows = [
    (1, "H", "CH3", "1b", "4b", 9, 61, "97/3", "trace"),
    (2, "H", "i-Pr", "1c", "4c", 10, 56, "96/4", "trace"),
    (3, "H", "n-C4H9", "1d", "4d", 13.5, 74, "98/2", 14),
    (4, "H", "n-C7H15", "1e", "4e", 9.5, 67, "96/4", 18),
    (5, "H", "Bn", "1f", "4f", 9.5, 65, "96/4", 18),
    (6, "CH3", "CH3", "1g", "4g", 10.5, 63, "94/6", "trace"),
    (7, "CH3", "C2H5", "1h", "4h", 10, 94, "94/6", "trace"),
    (8, "CH3", "i-Bu", "1i", "4i", 12, 53, "99/1", 14),
    (9, "CH3", "t-C4H9", "1j", "4j", 9, 85, "97/3", "trace"),
    (10, "C2H5", "C2H5", "1k", "4k", 8, 72, "98/2", "trace"),
    (11, "n-C4H9", "n-C4H9", "1l", "4l", 10, 93, "95/5", "trace"),
    (12, "n-C5H11", "n-C5H11", "1m", "4m", 10, 80, "97/3", "trace"),
]
substrate_smiles = {
    "1b": "c1ccccc1SC=C=CC", "1c": "c1ccccc1SC=C=CC(C)C", "1d": "c1ccccc1SC=C=CCCCC",
    "1e": "c1ccccc1SC=C=CCCCCCCC", "1f": "c1ccccc1SC=C=CCc1ccccc1", "1g": "c1ccccc1SC=C=C(C)C",
    "1h": "c1ccccc1SC=C=C(C)CC", "1i": "c1ccccc1SC=C=C(C)CC(C)C", "1j": "c1ccccc1SC=C=C(C)C(C)(C)C",
    "1k": "c1ccccc1SC=C=C(CC)CC", "1l": "c1ccccc1SC=C=C(CCCC)CCCC", "1m": "c1ccccc1SC=C=C(CCCCC)CCCCC",
}
product_smiles = {
    "4b": "c1ccccc1S/C=C(\\I)C(O)C", "4c": "c1ccccc1S/C=C(\\I)C(O)C(C)C", "4d": "c1ccccc1S/C=C(\\I)C(O)CCCC",
    "4e": "c1ccccc1S/C=C(\\I)C(O)CCCCCCC", "4f": "c1ccccc1S/C=C(\\I)C(O)Cc1ccccc1", "4g": "c1ccccc1S/C=C(\\I)C(O)(C)C",
    "4h": "c1ccccc1S/C=C(\\I)C(O)(C)CC", "4i": "c1ccccc1S/C=C(\\I)C(O)(C)CC(C)C", "4j": "c1ccccc1S/C=C(\\I)C(O)(C)C(C)(C)C",
    "4k": "c1ccccc1S/C=C(\\I)C(O)(CC)CC", "4l": "c1ccccc1S/C=C(\\I)C(O)(CCCC)CCCC", "4m": "c1ccccc1S/C=C(\\I)C(O)(CCCCC)CCCCC",
}
for entry, r1, r2, sublabel, prodlabel, hours, yprod, ze, yaldehyde in t2_rows:
    prefix = f"t2e{entry}"
    aldehyde_label = "2" + sublabel[-1]
    ps = [
        participant(f"{prefix}_sub", "reactant", EV2, sublabel, f"allenyl sulfide {sublabel} (R1={r1}, R2={r2})", substrate_smiles[sublabel]),
        participant(f"{prefix}_i2", "reagent", EV2, None, "iodine", "[I][I]", [field("equivalents", qty(2, "equiv", "2 equiv"), EV2)]),
        participant(f"{prefix}_acetone", "solvent", EV2, None, "acetone", "CC(=O)C"),
        participant(f"{prefix}_water", "solvent", EV2, None, "water", "O"),
        participant(f"{prefix}_prod", "product", EV2, prodlabel, f"(Z)-iodohydroxylation product {prodlabel}", product_smiles[prodlabel]),
        participant(f"{prefix}_ald", "product", EV2, aldehyde_label, f"corresponding aldehyde byproduct {aldehyde_label}", None),
    ]
    outs = [
        field(f"yield_{prodlabel}", qty(yprod, "%", f"{yprod}%"), EV2, [f"{prefix}_prod"]),
        field(f"Z_E_ratio_{prodlabel}", ze, EV2, [f"{prefix}_prod"]),
        field(f"yield_measurement_basis_{prodlabel}", None, EV2, [f"{prefix}_prod"]),
        field(f"yield_{aldehyde_label}", "trace" if yaldehyde == "trace" else qty(yaldehyde, "%", f"{yaldehyde}%"), EV2, [f"{prefix}_ald"]),
    ]
    records.append(rec(
        f"table2_entry_{entry}", "substrate_scope_entry", EV2, ps,
        [{"step_id": "iodohydroxylation", "participant_ids": [x["entity_id"] for x in ps[:4]], "conditions": [
            field("solvent", "acetone/H2O (4:1)", EV2), field("temperature", "r.t.", EV2), field("time", qty(hours, "h", f"{hours} h"), EV2)
        ]}],
        outs,
        notes=["Table 2 footnote reports the corresponding aldehyde 2 as trace unless an explicit percentage is given."],
        unresolved=["The main-product yield measurement basis is not explicitly stated in Table 2.", "Corresponding aldehyde byproduct structure is not encoded because only the family label 2 is given for this row.", "Reaction scale, workup, purification, and detailed procedure are absent; SI was not provided."],
    ))

# Scheme 2: two distinct oxidation rows.
for suffix, oxidant_name, oxidant_label, oxidant_smiles, equiv, solvent, solvent_smiles, hours, yld in [
    ("mcpba", "m-CPBA", "m-CPBA", None, 1.1, "CH2Cl2", "ClCCl", 4, 69),
    ("h2o2", "hydrogen peroxide", "H2O2", "OO", 4, "HOAc", "CC(=O)O", 36, 71),
]:
    ps = [
        participant(f"s2_{suffix}_4d", "reactant", EV2, "(Z)-4d", "(Z)-4d", product_smiles["4d"]),
        participant(f"s2_{suffix}_oxidant", "reagent", EV2, oxidant_label, oxidant_name, oxidant_smiles, [field("equivalents", qty(equiv, "equiv", f"{equiv} equiv"), EV2)]),
        participant(f"s2_{suffix}_solvent", "solvent", EV2, solvent, solvent, solvent_smiles),
        participant(f"s2_{suffix}_5d", "product", EV2, "(Z)-5d", "sulfoxide (Z)-5d", "O=S(c1ccccc1)/C=C(\\I)C(O)CCCC"),
    ]
    records.append(rec(
        f"scheme2_{suffix}", "reported_experiment", EV2, ps,
        [{"step_id": "oxidation", "participant_ids": [x["entity_id"] for x in ps[:3]], "conditions": [
            field("solvent", solvent, EV2), field("temperature", "r.t.", EV2), field("time", qty(hours, "h", f"{hours} h"), EV2)
        ]}],
        [
            field("yield_Z_5d", qty(yld, "%", f"{yld}%"), EV2, [f"s2_{suffix}_5d"]),
            field("yield_measurement_basis_Z_5d", None, EV2, [f"s2_{suffix}_5d"]),
            field("diastereomer_ratio_Z_5d", "46:54", EV2, [f"s2_{suffix}_5d"]),
        ],
        unresolved=["The yield measurement basis, scale, workup, and purification are not reported in Scheme 2; SI was not provided.", "m-CPBA is an abbreviation and no SMILES is inferred for it from the label alone." if suffix == "mcpba" else "Stereochemical assignment of the sulfoxide center is not encoded in the candidate SMILES."],
    ))

# Page 3 Scheme 3: one reported overall experiment with a bracketed iodohydroxylation intermediate.
ps = [
    participant("s3_1n", "reactant", EV3, "1n", "allenyl sulfide 1n", "c1ccccc1SC=C=C1CCCCC1"),
    participant("s3_i2", "reagent", EV3, None, "iodine", "[I][I]", [field("equivalents", qty(2, "equiv", "2 equiv"), EV3)]),
    participant("s3_acetone", "solvent", EV3, None, "acetone", "CC(=O)C"),
    participant("s3_water", "solvent", EV3, None, "water", "O"),
    participant("s3_4n", "product", EV3, "(Z)-4n", "bracketed iodohydroxylation product (Z)-4n", "c1ccccc1S/C=C(\\I)C1(O)CCCCC1"),
    participant("s3_6n", "product", EV3, "(Z)-6n", "(Z)-1-(1'-cyclohexenyl)-1-iodo-2-(phenylsulfanyl)ethene", "c1ccccc1S/C=C(\\I)C1=CCCCC1"),
]
records.append(rec(
    "scheme3_1n_to_6n", "reported_experiment", EV3, ps,
    [{"step_id": "overall_iodohydroxylation_dehydration", "participant_ids": [x["entity_id"] for x in ps], "conditions": [
        field("operation", "iodohydroxylation followed by dehydration", EV3), field("solvent", "acetone/H2O (4:1)", EV3),
        field("temperature", qty(25, "°C", "25 °C"), EV3), field("time", qty(11, "h", "11 h"), EV3)
    ]}],
    [
        field("yield_Z_6n", qty(85, "%", "85%"), EV3, ["s3_6n"]),
        field("Z_E_ratio_Z_6n", "97/3", EV3, ["s3_6n"]),
        field("yield_measurement_basis_Z_6n", None, EV3, ["s3_6n"]),
        field("yield_Z_4n", None, EV3, ["s3_4n"]),
    ],
    notes=["The text states that 6n is obtained via dehydration of iodohydroxylation product (Z)-4n; (Z)-4n is bracketed in Scheme 3."],
    unresolved=["Scheme 3 gives only an overall 11 h; timing and conditions of the individual iodohydroxylation and dehydration stages are not separately reported.", "No yield is reported for bracketed intermediate (Z)-4n.", "The yield basis, reaction scale, workup, and purification are absent; SI was not provided."],
))

# Page 3 Scheme 4: proposed generic mechanism, not a reported experiment.
ps = [
    participant("s4_1", "reactant", EV3, "1", "generic 1,2-allenyl phenyl sulfide", None),
    participant("s4_i2", "reagent", EV3, None, "iodine", "[I][I]"),
    participant("s4_complex", "unspecified_agent", EV3, None, "proposed sulfur-iodine molecular complex", None),
    participant("s4_7", "unspecified_agent", EV3, "(Z)-7", "proposed cyclic cationic intermediate (Z)-7", None),
    participant("s4_water", "reagent", EV3, None, "water", "O"),
    participant("s4_4", "product", EV3, "(Z)-4", "generic (Z)-iodohydroxylation product", None),
]
records.append(rec(
    "scheme4_proposed_mechanism", "mechanism", EV3, ps,
    [
        {"step_id": "sulfur_iodine_complexation", "participant_ids": ["s4_1", "s4_i2", "s4_complex"], "conditions": [field("operation", "proposed sulfur-I2 molecular-complex formation", EV3)]},
        {"step_id": "intramolecular_iodine_delivery", "participant_ids": ["s4_complex", "s4_7"], "conditions": [field("operation", "proposed intramolecular electrophilic iodine delivery", EV3)]},
        {"step_id": "hydrolysis", "participant_ids": ["s4_7", "s4_water", "s4_4"], "conditions": [field("operation", "hydrolysis", EV3)]},
    ],
    notes=["Scheme 4 is explicitly discussed as an assumed mechanistic rationale."],
    unresolved=["Generic R1/R2 and proposed intermediates prevent complete structure encoding.", "No independent experimental time, temperature, or yield belongs to this mechanistic scheme."],
))

OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
print(f"wrote {len(records)} records to {OUT}")
