#!/usr/bin/env python3
"""Build evidence-linked machine records for PDF pages 1--3."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "runs/current"
DOC = "doc_f40d59a31824dbcd"
P1 = [f"{DOC}:page1:image", f"{DOC}:page1:text"]
P2 = [f"{DOC}:page2:image", f"{DOC}:page2:text"]
P3 = [f"{DOC}:page3:image", f"{DOC}:page3:text"]


def fact(value, evidence=()):
    return {
        "value": value,
        "evidence_ids": list(evidence) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def field(name, value, evidence=(), targets=()):
    result = {"name": name, "fact": fact(value, evidence)}
    if targets:
        result["target_entity_ids"] = list(targets)
    return result


def participant(entity_id, role, label, name, evidence, smiles=None, amounts=()):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence),
        "smiles": fact(smiles, evidence if smiles else ()),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": list(amounts),
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
            "unresolved": unresolved,
        },
    }


def missing_conditions(*names):
    return [field(name, None) for name in names]


BR2 = "BrBr"
MECN = "CC#N"
WATER = "O"
THIOSULFATE = "[Na+].[Na+].[O-]S(=O)(=S)[O-]"


records = []

# Table 1: five independent optimization rows.
t1_rows = [
    (1, 2.0, 1.5, 60, 56, {"number": 11, "unit": "%"}, False),
    (2, 0.0, 1.5, 60, 56, {"number": 11, "unit": "%"}, False),
    (3, 0.0, 2.0, 60, 67, {"number": 9, "unit": "%"}, False),
    (4, 0.0, 2.5, 15, 70, "table dash (–)", False),
    (5, 0.0, 2.5, 15, 67, {"number": 1.5, "unit": "%"}, True),
]

for entry, water_eq, br_eq, minutes, y3, y4, direct in t1_rows:
    sid = f"t1e{entry}_1a"
    pids = {
        "substrate": f"{sid}_1a",
        "br2": f"{sid}_br2",
        "mecn": f"{sid}_mecn",
        "initial_water": f"{sid}_initial_water",
        "quench_water": f"{sid}_quench_water",
        "thio": f"{sid}_thio",
        "p3": f"{sid}_3a",
        "p4": f"{sid}_4a",
    }
    parts = [
        participant(pids["substrate"], "reactant", "1a", "1,2-butadienyl phenyl sulfone", P1,
                    "CC=C=C(S(=O)(=O)c1ccccc1)"),
        participant(pids["br2"], "reagent", "Br2", "bromine", P1, BR2,
                    [field("equivalents", {"number": br_eq, "unit": "equiv"}, P1)]),
        participant(pids["mecn"], "solvent", "MeCN", "acetonitrile", P1, MECN),
        participant(pids["initial_water"], "reagent", "H2O (initial loading)", "water", P1, WATER,
                    [field("initial_water_equivalents", {"number": water_eq, "unit": "equiv"}, P1)]),
        participant(pids["thio"], "reagent", "saturated aqueous Na2S2O3", "saturated aqueous sodium thiosulfate", P1, THIOSULFATE),
        participant(pids["p3"], "product", "(E)-3a", "1-(phenylsulfonyl)methylene-2-methylthiirane", P1,
                    "CC1SC1=C(S(=O)(=O)c2ccccc2)"),
        participant(pids["p4"], "product", "(E)-4a", "2,3-dibromobutenyl phenyl sulfone", P1,
                    "CC(Br)C(Br)=C(S(=O)(=O)c1ccccc1)"),
    ]
    reaction_ids = [pids["substrate"], pids["br2"], pids["mecn"], pids["initial_water"]]
    steps = [{
        "step_id": "reaction",
        "participant_ids": reaction_ids,
        "conditions": [
            field("solvent", "MeCN", P1),
            field("temperature", "r.t.", P1),
            field("time", {"number": minutes, "unit": "min"}, P1),
            field("atmosphere", None),
        ],
    }]
    if not direct:
        parts.insert(4, participant(pids["quench_water"], "reagent", "H2O (sequential treatment)", "water", P1, WATER))
        steps.append({
            "step_id": "water_treatment",
            "participant_ids": [pids["quench_water"]],
            "conditions": [field("operation", "treat with water", P1), field("temperature", "r.t.", P1)],
        })
    steps.append({
        "step_id": "thiosulfate_treatment",
        "participant_ids": [pids["thio"]],
        "conditions": [
            field("operation", "quench directly with saturated aqueous Na2S2O3" if direct else "treat with saturated aqueous Na2S2O3", P1),
            field("temperature", "r.t.", P1),
            *missing_conditions("workup", "purification"),
        ],
    })
    outcomes = [
        field("reported_yield_3a", {"number": y3, "unit": "%"}, P1, [pids["p3"]]),
        field("reported_yield_4a", y4, P1, [pids["p4"]]),
        field("yield_measurement_basis", None),
    ]
    notes = []
    if entry == 1:
        notes.append(("The prose states that the reaction was conducted in the presence of the structured initial water loading.", P1))
    if entry == 4:
        notes.append(("The prose calls (E)-3a the only product, while the table prints a dash for (E)-4a; the dash is preserved without conversion to zero.", P1))
    records.append(record(
        f"table1_entry{entry}", "optimization_entry", P1, parts, steps, outcomes, notes,
        [
            "Yield measurement basis is not stated.",
            "Atmosphere, detailed workup, purification, and reagent/solvent absolute quantities are not reported.",
            "Candidate structures and alkene geometry are machine-derived and unverified.",
            "Supporting information is mentioned but was not supplied or explicitly associated.",
        ],
    ))


def phenyl_sulfone(ring="c1ccccc1"):
    return f"S(=O)(=O){ring}"


scope = [
    # entry, substrate, product, R1, R2, R3, yield, time, Br2 equiv, direct quench, substrate smiles, product smiles
    (1, "1a", "3a", "Ph", "H", "CH3", 70, 10, 2.5, False,
     "CC=C=C(S(=O)(=O)c1ccccc1)", "CC1SC1=C(S(=O)(=O)c2ccccc2)"),
    (2, "1b", "3b", "Ph", "H", "C2H5", 70, 15, 2.0, False,
     "CCC=C=C(S(=O)(=O)c1ccccc1)", "CCC1SC1=C(S(=O)(=O)c2ccccc2)"),
    (3, "1b", "3b", "Ph", "H", "C2H5", 55, 15, 2.0, True,
     "CCC=C=C(S(=O)(=O)c1ccccc1)", "CCC1SC1=C(S(=O)(=O)c2ccccc2)"),
    (4, "1c", "3c", "Ph", "H", "n-C3H7", 68, 15, 2.0, False,
     "CCCC=C=C(S(=O)(=O)c1ccccc1)", "CCCC1SC1=C(S(=O)(=O)c2ccccc2)"),
    (5, "1d", "3d", "Ph", "H", "n-C4H9", 71, 15, 2.0, False,
     "CCCCC=C=C(S(=O)(=O)c1ccccc1)", "CCCCC1SC1=C(S(=O)(=O)c2ccccc2)"),
    (6, "1e", "3e", "Ph", "H", "n-C5H11", 63, 15, 2.0, False,
     "CCCCCC=C=C(S(=O)(=O)c1ccccc1)", "CCCCCC1SC1=C(S(=O)(=O)c2ccccc2)"),
    (7, "1f", "3f", "Ph", "H", "n-C6H13", 69, 15, 2.0, False,
     "CCCCCCC=C=C(S(=O)(=O)c1ccccc1)", "CCCCCCC1SC1=C(S(=O)(=O)c2ccccc2)"),
    (8, "1g", "3g", "Ph", "H", "Bn", 72, 15, 2.0, False,
     "c1ccccc1CC=C=C(S(=O)(=O)c2ccccc2)", "c1ccccc1CC2SC2=C(S(=O)(=O)c3ccccc3)"),
    (9, "1h", "3h", "Ph", "n-C4H9", "CH3", 80, 15, 2.0, False,
     "CC=C=C(CCCC)S(=O)(=O)c1ccccc1", "CC1SC1=C(CCCC)S(=O)(=O)c2ccccc2"),
    (10, "1i", "3i", "Ph", "n-C4H9", "C2H5", 67, 15, 2.0, False,
     "CCC=C=C(CCCC)S(=O)(=O)c1ccccc1", "CCC1SC1=C(CCCC)S(=O)(=O)c2ccccc2"),
    (11, "1j", "3j", "Ph", "n-C4H9", "Bn", 84, 15, 2.0, False,
     "c1ccccc1CC=C=C(CCCC)S(=O)(=O)c2ccccc2", "c1ccccc1CC2SC2=C(CCCC)S(=O)(=O)c3ccccc3"),
    (12, "1k", "3k", "Ph", "C2H5", "CH3", 84, 20, 2.0, False,
     "CC=C=C(CC)S(=O)(=O)c1ccccc1", "CC1SC1=C(CC)S(=O)(=O)c2ccccc2"),
    (13, "1l", "3l", "p-BrC6H4", "C2H5", "CH3", 61, 25, 2.0, False,
     "CC=C=C(CC)S(=O)(=O)c1ccc(Br)cc1", "CC1SC1=C(CC)S(=O)(=O)c2ccc(Br)cc2"),
    (14, "1m", "3m", "p-BrC6H4", "H", "CH3", 65, 25, 2.0, False,
     "CC=C=C(S(=O)(=O)c1ccc(Br)cc1)", "CC1SC1=C(S(=O)(=O)c2ccc(Br)cc2)"),
]

table2_ids = []
for entry, sub, prod, r1, r2, r3, yld, minutes, br_eq, direct, sub_smiles, prod_smiles in scope:
    sid = f"t2e{entry}_{sub}_{prod}"
    sub_id, br_id, mecn_id = f"{sid}_sub", f"{sid}_br2", f"{sid}_mecn"
    water_id, thio_id, prod_id = f"{sid}_water", f"{sid}_thio", f"{sid}_prod"
    parts = [
        participant(sub_id, "reactant", sub, f"1,2-allenyl sulfone {sub} (R1={r1}, R2={r2}, R3={r3})", P2, sub_smiles),
        participant(br_id, "reagent", "Br2", "bromine", P2, BR2,
                    [field("equivalents", {"number": br_eq, "unit": "equiv"}, P2)]),
        participant(mecn_id, "solvent", "MeCN", "acetonitrile", P2, MECN),
        participant(thio_id, "reagent", "saturated aqueous Na2S2O3", "saturated aqueous sodium thiosulfate", P2, THIOSULFATE),
        participant(prod_id, "product", f"(E)-{prod}", f"1-sulfonyl alkylidenethiirane {prod} (R1={r1}, R2={r2}, R3={r3})", P2, prod_smiles),
    ]
    steps = [{
        "step_id": "bromination",
        "participant_ids": [sub_id, br_id, mecn_id],
        "conditions": [
            field("solvent", "MeCN", P2),
            field("temperature", "r.t.", P2),
            field("time", {"number": minutes, "unit": "min"}, P2),
            field("atmosphere", None),
        ],
    }]
    if not direct:
        parts.insert(3, participant(water_id, "reagent", "H2O", "water", P2, WATER))
        steps.append({
            "step_id": "water_treatment",
            "participant_ids": [water_id],
            "conditions": [field("operation", "treat with H2O", P2), field("temperature", "r.t.", P2)],
        })
    steps.append({
        "step_id": "thiosulfate_treatment",
        "participant_ids": [thio_id],
        "conditions": [
            field("operation", "quench directly with aqueous Na2S2O3" if direct else "treat with saturated aqueous Na2S2O3", P2),
            field("temperature", "r.t.", P2),
            *missing_conditions("workup", "purification"),
        ],
    })
    suffix = f"table2_entry{entry}_{prod}"
    table2_ids.append(f"{DOC}:{suffix}")
    records.append(record(
        suffix, "substrate_scope_entry", P2, parts, steps,
        [
            field(f"reported_yield_{prod}", {"number": yld, "unit": "%"}, P2, [prod_id]),
            field("yield_measurement_basis", None),
        ],
        [({"R1": r1, "R2": r2, "R3": r3}, P2)],
        [
            "Yield measurement basis, atmosphere, absolute scale, solvent volume, detailed workup, and purification are not stated.",
            "Candidate structures are constitutional machine interpretations of the table drawings; alkene geometry and any axial/central stereochemistry are unverified.",
            "Supporting information is mentioned but was not supplied or explicitly associated.",
        ],
    ))


# Table 3: four enantioenriched-substrate cases.
chiral_rows = [
    (1, "(R)-1f", "(S)-(E)-3f", "Ph", "H", "n-C6H13", {"number": 99, "unit": "%", "qualifier": "gt", "raw_text": ">99%"}, 58, 99,
     "CCCCCCC=C=C(S(=O)(=O)c1ccccc1)", "CCCCCCC1SC1=C(S(=O)(=O)c2ccccc2)"),
    (2, "(R)-1e", "(S)-(E)-3e", "Ph", "H", "n-C5H11", {"number": 99, "unit": "%"}, 62, 99,
     "CCCCCC=C=C(S(=O)(=O)c1ccccc1)", "CCCCCC1SC1=C(S(=O)(=O)c2ccccc2)"),
    (3, "(R)-1l", "(S)-(E)-3l", "p-BrC6H4", "C2H5", "CH3", {"number": 96, "unit": "%"}, 74, 96,
     "CC=C=C(CC)S(=O)(=O)c1ccc(Br)cc1", "CC1SC1=C(CC)S(=O)(=O)c2ccc(Br)cc2"),
    (4, "(R)-1m", "(S)-(E)-3m", "p-BrC6H4", "H", "CH3", {"number": 99, "unit": "%"}, 57, 99,
     "CC=C=C(S(=O)(=O)c1ccc(Br)cc1)", "CC1SC1=C(S(=O)(=O)c2ccc(Br)cc2)"),
]

table3_ids = []
for entry, sub, prod, r1, r2, r3, start_ee, yld, product_ee, sub_smiles, prod_smiles in chiral_rows:
    sid = f"t3e{entry}"
    sub_id, br_id, mecn_id = f"{sid}_sub", f"{sid}_br2", f"{sid}_mecn"
    water_id, thio_id, prod_id = f"{sid}_water", f"{sid}_thio", f"{sid}_prod"
    parts = [
        participant(sub_id, "reactant", sub, f"enantioenriched 1,2-allenyl sulfone (R1={r1}, R2={r2}, R3={r3})", P2, sub_smiles),
        participant(br_id, "reagent", "Br2", "bromine", P2, BR2,
                    [field("equivalents", {"number": 2, "unit": "equiv"}, P2)]),
        participant(mecn_id, "solvent", "MeCN", "acetonitrile", P2, MECN),
        participant(water_id, "reagent", "H2O", "water", P2, WATER),
        participant(thio_id, "reagent", "saturated aqueous Na2S2O3", "saturated aqueous sodium thiosulfate", P2, THIOSULFATE),
        participant(prod_id, "product", prod, f"enantioenriched 1-sulfonyl alkylidenethiirane (R1={r1}, R2={r2}, R3={r3})", P2, prod_smiles),
    ]
    steps = [
        {
            "step_id": "bromination",
            "participant_ids": [sub_id, br_id, mecn_id],
            "conditions": [
                field("solvent", "MeCN", P2),
                field("temperature", "r.t.", P2),
                field("time", {"minimum": 10, "maximum": 25, "unit": "min", "raw_text": "10–25 min"}, P2),
                field("atmosphere", None),
            ],
        },
        {
            "step_id": "water_treatment",
            "participant_ids": [water_id],
            "conditions": [field("operation", "treat with H2O", P2), field("temperature", "r.t.", P2)],
        },
        {
            "step_id": "thiosulfate_treatment",
            "participant_ids": [thio_id],
            "conditions": [field("operation", "treat with saturated aqueous Na2S2O3", P2), field("temperature", "r.t.", P2), *missing_conditions("workup", "purification")],
        },
    ]
    suffix = f"table3_entry{entry}_{prod.replace('(', '').replace(')', '').replace('-', '_')}"
    table3_ids.append(f"{DOC}:{suffix}")
    records.append(record(
        suffix, "substrate_scope_entry", P2, parts, steps,
        [
            field("starting_material_ee", start_ee, P2, [sub_id]),
            field("reported_product_yield", {"number": yld, "unit": "%"}, P2, [prod_id]),
            field("product_ee", {"number": product_ee, "unit": "%"}, P2, [prod_id]),
            field("ee_measurement_basis", "HPLC on a chiral phase", P2, [sub_id, prod_id]),
            field("yield_measurement_basis", None),
        ],
        [({"R1": r1, "R2": r2, "R3": r3}, P2)],
        [
            "The header gives a common 10–25 min range but does not assign an exact duration to each row.",
            "Yield measurement basis, atmosphere, absolute scale, solvent volume, detailed workup, and purification are not stated.",
            "Constitutional SMILES omit unverified axial chirality, central chirality, and alkene stereochemical encoding.",
            "Supporting information is mentioned but was not supplied or explicitly associated.",
        ],
    ))


# Scheme 1, first arrow: isolation of the five-membered intermediate.
scheme1a = f"{DOC}:scheme1_1l_to_5l"
records.append(record(
    "scheme1_1l_to_5l", "reported_experiment", P2,
    [
        participant("s1a_1l", "reactant", "1l", "1,2-butadienyl p-bromophenyl sulfone", P2,
                    "CC=C=C(CC)S(=O)(=O)c1ccc(Br)cc1"),
        participant("s1a_br2", "reagent", "Br2", "bromine", P2, BR2,
                    [field("equivalents", {"number": 2, "unit": "equiv"}, P2)]),
        participant("s1a_mecn", "solvent", "CH3CN", "acetonitrile", P2, MECN),
        participant("s1a_5l", "product", "5l (cis/trans 1:1; Br3− counterion)", "five-membered cyclic intermediate 5l", P2),
    ],
    [{
        "step_id": "intermediate_formation",
        "participant_ids": ["s1a_1l", "s1a_br2", "s1a_mecn"],
        "conditions": [field("solvent", "CH3CN", P2), *missing_conditions("temperature", "time", "atmosphere", "workup", "purification")],
    }],
    [
        field("reported_yield_5l", {"number": 70, "unit": "%"}, P2, ["s1a_5l"]),
        field("cis_trans_ratio", "1:1", P2, ["s1a_5l"]),
        field("yield_measurement_basis", None),
    ],
    [
        ("The source states that 5l could be isolated with careful handling and that the trans isomer was established by X-ray diffraction.", P2),
    ],
    [
        "Temperature, duration, atmosphere, workup, purification, and yield measurement basis are not stated for isolation of 5l.",
        "The ionic intermediate structure and cis/trans assignments remain unverified machine interpretations.",
        "Supporting crystallographic information is cited but was not supplied or explicitly associated.",
    ],
))


# Scheme 1, second arrow: independently isolated 5l converted to 3l.
scheme1b = f"{DOC}:scheme1_5l_to_3l"
records.append(record(
    "scheme1_5l_to_3l", "reported_experiment", P2,
    [
        participant("s1b_5l", "reactant", "5l (cis/trans 1:1; Br3− counterion)", "five-membered cyclic intermediate 5l", P2),
        participant("s1b_mecn", "solvent", "MeCN", "acetonitrile", P2, MECN),
        participant("s1b_water", "reagent", "H2O", "water", P2, WATER),
        participant("s1b_thio", "reagent", "saturated aqueous Na2S2O3", "saturated aqueous sodium thiosulfate", P2, THIOSULFATE),
        participant("s1b_3l", "product", "(E)-3l", "1-(p-bromophenylsulfonyl) alkylidenethiirane 3l", P2,
                    "CC1SC1=C(CC)S(=O)(=O)c2ccc(Br)cc2"),
    ],
    [
        {"step_id": "dissolution", "participant_ids": ["s1b_5l", "s1b_mecn"], "conditions": [field("solvent", "MeCN", P2), *missing_conditions("temperature", "time", "atmosphere")]},
        {"step_id": "water_treatment", "participant_ids": ["s1b_water"], "conditions": [field("operation", "treat with H2O", P2)]},
        {"step_id": "thiosulfate_treatment", "participant_ids": ["s1b_thio"], "conditions": [field("operation", "add saturated aqueous Na2S2O3", P2), *missing_conditions("workup", "purification")]},
    ],
    [
        field("reported_yield_3l", {"number": 84, "unit": "%"}, P2, ["s1b_3l"]),
        field("product_selectivity", "(E)-3l as a single product", P2, ["s1b_3l"]),
        field("yield_measurement_basis", None),
    ],
    [],
    [
        "Absolute quantities, temperature, duration, atmosphere, detailed workup, purification, and yield measurement basis are not stated.",
        "The intermediate and product structures/stereochemistry remain unverified machine interpretations.",
        "Supporting information is mentioned but was not supplied or explicitly associated.",
    ],
))


# Scheme 2 is explicitly proposed and is not promoted to a reported experiment.
mechanism_id = f"{DOC}:scheme2_proposed_mechanism"
mechanism_participants = [
    participant("m_1m", "reactant", "(R)-1m", "enantioenriched 1,2-allenyl p-bromophenyl sulfone", P3,
                "CC=C=C(S(=O)(=O)c1ccc(Br)cc1)"),
    participant("m_br2", "reagent", "Br2", "bromine", P3, BR2),
    participant("m_mecn", "solvent", "MeCN", "acetonitrile", P2 + P3, MECN),
    participant("m_5m", "unspecified_agent", "5m", "proposed five-membered-ring intermediate 5m", P2 + P3),
    participant("m_thio", "reagent", "S2O3^2− / Na2S2O3", "thiosulfate", P2 + P3, THIOSULFATE),
    participant("m_6", "unspecified_agent", "6", "proposed acyclic intermediate 6", P2 + P3),
    participant("m_so3", "product", "SO3", "sulfur trioxide", P2 + P3, "O=S(=O)=O"),
    participant("m_7", "unspecified_agent", "7", "proposed 2-bromoallylic sulfide 7", P2 + P3),
    participant("m_8", "unspecified_agent", "8", "proposed conjugate-addition intermediate 8", P3),
    participant("m_3m", "product", "(S)-(E)-3m", "enantioenriched alkylidenethiirane 3m", P2 + P3,
                "CC1SC1=C(S(=O)(=O)c2ccc(Br)cc2)"),
]
records.append(record(
    "scheme2_proposed_mechanism", "mechanism", P2 + P3, mechanism_participants,
    [
        {"step_id": "electrophilic_addition", "participant_ids": ["m_1m", "m_br2", "m_mecn", "m_5m"], "conditions": [field("solvent", "MeCN", P2 + P3)]},
        {"step_id": "thiosulfate_ring_opening", "participant_ids": ["m_5m", "m_thio", "m_6"], "conditions": [field("operation", "proposed thiosulfate attack and ring opening", P2 + P3)]},
        {"step_id": "sulfur_trioxide_release", "participant_ids": ["m_6", "m_so3", "m_7"], "conditions": [field("operation", "proposed release of SO3", P2 + P3)]},
        {"step_id": "cyclization_elimination", "participant_ids": ["m_7", "m_8", "m_3m"], "conditions": [field("operation", "proposed intramolecular conjugate addition and elimination", P2 + P3)]},
    ],
    [],
    [
        ("The authors explicitly propose this pathway to account for regioselectivity and stereospecific transfer of axial to central chirality.", P2 + P3),
    ],
    [
        "This is a proposed mechanism, not a separately executed experiment.",
        "Intermediate connectivities, charges, stereochemistry, and individual step conditions are not independently verified.",
        "No mechanistic intermediate quantities or step yields are reported.",
    ],
))


records_path = OUT / "raw_model/records_pages_0001_0003.json"
records_path.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")

table1_ids = [f"{DOC}:table1_entry{i}" for i in range(1, 6)]
coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1,
            "state": "attempted",
            "regions": [
                {
                    "region": "upper and left columns: title, introduction, author notes, and SI-availability statement",
                    "finding": "Background/cited chemistry and high-level present-paper claims were distinguished from row-level experiments; the online SI statement was not treated as an associated source.",
                    "evidence_ids": P1,
                },
                {
                    "region": "right-center Table 1, reaction drawing, five rows, and footnote a",
                    "finding": "Five independent optimization entries were extracted, including initial-water and bromine equivalents, duration, two product yields, the printed dash, and the direct-thiosulfate-quench exception.",
                    "evidence_ids": P1,
                },
                {
                    "region": "right-column prose surrounding Table 1",
                    "finding": "Narrative values were linked to the corresponding table rows; no duplicate experiments were created.",
                    "evidence_ids": P1,
                },
            ],
            "record_ids": table1_ids,
            "unresolved": [
                "Table 1 does not report yield basis, atmosphere, absolute scale, detailed workup, or purification.",
                "The entry-4 dash is undefined; the prose says 3a was the only product, so both source expressions are retained without converting the dash to zero.",
                "The main text mentions online Supporting Information, but no SI file was supplied or explicitly associated.",
            ],
        },
        {
            "page": 2,
            "state": "attempted",
            "regions": [
                {
                    "region": "upper-left Table 2 reaction drawing, 14 scope rows, and footnotes a-e",
                    "finding": "All fourteen substrate-scope rows were extracted independently; bromine/time overrides and the direct aqueous-thiosulfate quench were applied only to their marked rows.",
                    "evidence_ids": P2,
                },
                {
                    "region": "middle-left Table 3 reaction drawing, four enantioenriched rows, and ee footnote",
                    "finding": "Four independent asymmetric-scope experiments were extracted with starting and product ee, product yields, the shared duration range, and chiral-HPLC measurement basis.",
                    "evidence_ids": P2,
                },
                {
                    "region": "right-center Figure 2 and Scheme 1",
                    "finding": "Scheme 1 was split into isolation of intermediate 5l and its separate conversion to (E)-3l; Figure 2 is structural evidence for trans-5l, not another reaction.",
                    "evidence_ids": P2,
                },
                {
                    "region": "lower-left Figure 1 and lower-right mechanistic prose",
                    "finding": "Figure 1 was linked as structural context for (S)-(E)-3m; the proposed pathway was classified as a mechanism and linked to the page-3 drawing.",
                    "evidence_ids": P2,
                },
            ],
            "record_ids": table2_ids + table3_ids + [scheme1a, scheme1b, mechanism_id],
            "unresolved": [
                "Tables 2 and 3 generally omit yield basis, atmosphere, absolute scale, solvent volume, detailed workup, and purification.",
                "Table 3 gives a common 10–25 min range without assigning an exact duration to each row.",
                "Scheme 1 omits several quantities and operational details; intermediate and stereochemical structures remain unverified.",
            ],
        },
        {
            "page": 3,
            "state": "attempted",
            "regions": [
                {
                    "region": "upper-left Scheme 2",
                    "finding": "The multistep pathway through 5m, 6, 7, and 8 was classified as a proposed mechanism rather than a reported experiment.",
                    "evidence_ids": P3,
                },
                {
                    "region": "lower-left conclusion, dates, keywords, and references 1-3",
                    "finding": "No additional row-level present-paper experiment was found; cited works were not mined as associated sources.",
                    "evidence_ids": P3,
                },
                {
                    "region": "right column references and crystallographic notes 10-13",
                    "finding": "Crystal data and CCDC identifiers were treated as characterization/reference context, not as reaction experiments or supplied SI.",
                    "evidence_ids": P3,
                },
            ],
            "record_ids": [mechanism_id],
            "unresolved": [
                "Mechanistic intermediates and stereochemical details remain proposed and unverified.",
                "CCDC deposits and online Supporting Information were mentioned but were not supplied or explicitly associated.",
                "Reference 11 describes a cited oxidation route to chiral allenyl sulfones without a compound-specific procedure or yield on this page; it was not promoted to a present-paper experiment.",
            ],
        },
    ],
}
(OUT / "coverage/pages_0001_0003.json").write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

tasks_path = OUT / "tasks.json"
tasks = json.loads(tasks_path.read_text())
for task in tasks:
    if task.get("document_id") == DOC and task.get("evidence_id") in {f"{DOC}:page{i}:text" for i in range(1, 4)}:
        task["state"] = "attempted"
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"records": len(records), "coverage_pages": [1, 2, 3]}, ensure_ascii=False))
