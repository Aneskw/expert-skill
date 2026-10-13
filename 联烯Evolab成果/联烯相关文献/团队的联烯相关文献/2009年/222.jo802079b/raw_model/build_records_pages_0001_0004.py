#!/usr/bin/env python3
"""Build source-linked machine records for jo802079b, PDF pages 1-4."""
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "runs/current"
DOC = "doc_c4b54089834cf856"


def ev(page: int) -> list[str]:
    return [f"{DOC}:page{page}:image", f"{DOC}:page{page}:text"]


def uniq(values):
    return list(dict.fromkeys(values))


def fact(value, evidence=None):
    return {
        "value": value,
        "evidence_ids": [] if value is None else uniq(evidence or []),
        "verification": "missing" if value is None else "unreviewed",
    }


def field(name, value, evidence=None, targets=None):
    item = {"name": name, "fact": fact(value, evidence)}
    if targets:
        item["target_entity_ids"] = targets
    return item


def participant(entity_id, role, label, evidence, *, name=None, smiles=None, amounts=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence) if name else fact(None),
        "smiles": fact(smiles, evidence) if smiles else fact(None),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": amounts or [],
    }


def rec(rid, kind, evidence, participants, steps, outcomes, *, notes=None, unresolved=None):
    return {
        "record_id": f"{DOC}:{rid}",
        "document_id": DOC,
        "source_reaction_id": rid,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": uniq(evidence),
        "participants": participants,
        "steps": steps,
        "outcomes": outcomes,
        "notes": [fact(x, evidence) for x in (notes or [])],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved or [
                "Machine-extracted chemistry and structures require source review.",
                "Supporting information was not supplied or explicitly associated.",
            ],
        },
    }


def step(step_id, ids, conditions):
    return {"step_id": step_id, "participant_ids": ids, "conditions": conditions}


def q(number, unit, **extra):
    value = {"number": number, "unit": unit}
    value.update(extra)
    return value


def missing_ops():
    return [
        field("atmosphere", None),
        field("workup", None),
        field("purification", None),
    ]


def common(name, role, label, evidence, smiles=None, amount_fields=None):
    return participant(name, role, label, evidence, smiles=smiles, amounts=amount_fields)


records = []

# Page 1 graphical abstract: a generic scope summary, not a batch experiment.
e1 = ev(1)
records.append(rec(
    "graphical_abstract_scope", "general_scheme", e1,
    [
        participant("generic_45_allenol", "reactant", "generic 4,5-allenol (R1-R4)", e1),
        participant("generic_iodotetrahydrofuran", "product", "generic 2-(1-iodoalkenyl)tetrahydrofuran", e1),
        participant("iodine", "reagent", "I2", e1, smiles="II"),
        participant("nis", "reagent", "NIS", e1),
    ],
    [step("scope_A", ["generic_45_allenol", "iodine", "generic_iodotetrahydrofuran"], [
        field("solvent", "n-hexane", e1), field("temperature", "r.t.", e1)
    ]), step("scope_B", ["generic_45_allenol", "nis", "generic_iodotetrahydrofuran"], [
        field("solvent", "CH2Cl2", e1), field("temperature", "r.t.", e1)
    ])],
    [
        field("scope_yield_range", {"minimum": 42, "maximum": 81, "unit": "%", "raw_text": "42-81%"}, e1, ["generic_iodotetrahydrofuran"]),
        field("scope_dr", "up to 99/1", e1, ["generic_iodotetrahydrofuran"]),
        field("scope_Z_E_ratio", "up to 99/1", e1, ["generic_iodotetrahydrofuran"]),
        field("kinetic_resolution_scope_yield_range", {"minimum": 68, "maximum": 75, "unit": "%", "raw_text": "68-75%"}, e1, ["generic_iodotetrahydrofuran"]),
        field("kinetic_resolution_Z_E_ratio", ">99/1", e1, ["generic_iodotetrahydrofuran"]),
    ],
    notes=["The graphic summarizes routes A and B and kinetic resolution; it is not an individual experimental batch."],
    unresolved=["Generic R groups prevent complete structure assignment.", "The scope ranges summarize experiments detailed elsewhere."],
))

# Scheme 1: optically active starting-material preparation, split by product series and chemical stage.
scheme1 = ev(1) + ev(2)
route_data = {
    "b": {"r": "n-C5H11", "start_ee": 96, "p2_y": 49, "p2_t": (5, 2.5), "p3_y": 35, "p3_t": (12, 23), "p4_y": 81, "p4_t": 3.7, "p5_y": 80, "p5_t": 3, "p5_ee": 95},
    "c": {"r": "n-C6H13", "start_ee": {"number": 99, "unit": "%", "qualifier": "gt", "raw_text": ">99%"}, "p2_y": 79, "p2_t": (2.3, 2.3), "p3_y": 57, "p3_t": (3, 23), "p4_y": 97, "p4_t": 26, "p5_y": 92, "p5_t": 5, "p5_ee": 98},
}
for suffix, d in route_data.items():
    start_ee = q(d["start_ee"], "%") if isinstance(d["start_ee"], (int, float)) else d["start_ee"]
    p1 = participant(f"r1{suffix}", "reactant", f"(R)-1{suffix} (R = {d['r']})", scheme1, amounts=[field("starting_material_ee", start_ee, scheme1)])
    p2 = participant(f"r2{suffix}", "product", f"(R)-2{suffix}", scheme1)
    ortho = participant(f"orthoacetate_{suffix}", "reagent", "CH3C(OEt)3", scheme1)
    acid = participant(f"propionic_acid_{suffix}", "reagent", "CH3CH2COOH", scheme1, smiles="CCC(=O)O")
    lah = participant(f"lah_2{suffix}", "reagent", "LiAlH4", scheme1)
    thf = participant(f"thf_2{suffix}", "solvent", "THF", scheme1, smiles="C1CCOC1")
    records.append(rec(
        f"scheme1_1{suffix}_to_2{suffix}", "reported_experiment", scheme1,
        [p1, p2, ortho, acid, lah, thf],
        [
            step("claisen_rearrangement", [p1["entity_id"], ortho["entity_id"], acid["entity_id"]], [field("temperature", q(140, "°C"), ev(2)), field("time", q(d["p2_t"][0], "h"), ev(2))]),
            step("reduction", [lah["entity_id"], thf["entity_id"], p2["entity_id"]], [field("temperature", q(0, "°C"), ev(2)), field("time", q(d["p2_t"][1], "h"), ev(2))] + missing_ops()),
        ],
        [field("reported_yield", q(d["p2_y"], "%"), ev(2), [p2["entity_id"]]), field("yield_measurement_basis", None)],
        unresolved=["The displayed yield is assigned to isolated product 2, but the yield basis and whether it is overall across both arrows are not stated.", "Atmosphere, workup, and purification are not stated."],
    ))

    r2 = participant(f"r2{suffix}", "reactant", f"(R)-2{suffix}", scheme1)
    r3 = participant(f"r3{suffix}", "product", f"(R)-3{suffix}", scheme1)
    pts = participant(f"ptscl_{suffix}", "reagent", "p-TsCl", scheme1)
    pyr = participant(f"pyridine_{suffix}", "solvent", "pyridine", scheme1, smiles="n1ccccc1")
    nacn = participant(f"nacn_{suffix}", "reagent", "NaCN", scheme1, smiles="[Na+].[C-]#N")
    dmso = participant(f"dmso_{suffix}", "solvent", "DMSO", scheme1, smiles="CS(C)=O")
    records.append(rec(
        f"scheme1_2{suffix}_to_3{suffix}", "reported_experiment", scheme1,
        [r2, r3, pts, pyr, nacn, dmso],
        [
            step("tosylation", [r2["entity_id"], pts["entity_id"], pyr["entity_id"]], [field("temperature", q(0, "°C"), ev(2)), field("time", q(d["p3_t"][0], "h"), ev(2))]),
            step("cyanide_substitution", [nacn["entity_id"], dmso["entity_id"], r3["entity_id"]], [field("temperature", None), field("time", q(d["p3_t"][1], "h"), ev(2))] + missing_ops()),
        ],
        [field("reported_yield", q(d["p3_y"], "%"), ev(2), [r3["entity_id"]]), field("yield_measurement_basis", None)],
        unresolved=["The displayed yield is assigned to nitrile 3, but its basis and whether it covers both arrows are not stated.", "The NaCN-stage temperature, atmosphere, workup, and purification are not stated."],
    ))

    r3 = participant(f"r3{suffix}", "reactant", f"(R)-3{suffix}", scheme1)
    r4 = participant(f"r4{suffix}", "product", f"(R)-4{suffix}", scheme1)
    naoh = participant(f"naoh_{suffix}", "reagent", "NaOH", scheme1, smiles="[Na+].[OH-]")
    etoh = participant(f"etoh_{suffix}", "solvent", "EtOH", scheme1, smiles="CCO")
    water = participant(f"water_hydro_{suffix}", "solvent", "H2O", scheme1, smiles="O")
    proton = participant(f"hplus_{suffix}", "reagent", "H+", scheme1)
    records.append(rec(
        f"scheme1_3{suffix}_to_4{suffix}", "reported_experiment", scheme1,
        [r3, r4, naoh, etoh, water, proton],
        [step("nitrile_hydrolysis", [x["entity_id"] for x in [r3, naoh, etoh, water, proton, r4]], [field("temperature", "reflux", ev(2)), field("time", q(d["p4_t"], "h"), ev(2)), field("operation", "NaOH in EtOH/H2O under reflux, then H+", ev(2))] + missing_ops())],
        [field("reported_yield", q(d["p4_y"], "%"), ev(2), [r4["entity_id"]]), field("yield_measurement_basis", None)],
        unresolved=["Yield basis, atmosphere, workup, and purification are not stated."],
    ))

    r4 = participant(f"r4{suffix}", "reactant", f"(R)-4{suffix}", scheme1)
    r5 = participant(f"r5{suffix}", "product", f"(R)-5{suffix}", scheme1)
    lah = participant(f"lah_5{suffix}", "reagent", "LiAlH4", scheme1)
    ether = participant(f"ether_5{suffix}", "solvent", "Et2O", scheme1, smiles="CCOCC")
    records.append(rec(
        f"scheme1_4{suffix}_to_5{suffix}", "reported_experiment", scheme1,
        [r4, r5, lah, ether],
        [step("carboxylic_acid_reduction", [x["entity_id"] for x in [r4, lah, ether, r5]], [field("temperature", q(0, "°C"), ev(2)), field("time", q(d["p5_t"], "h"), ev(2))] + missing_ops())],
        [field("reported_yield", q(d["p5_y"], "%"), ev(2), [r5["entity_id"]]), field("product_ee", q(d["p5_ee"], "%"), ev(2), [r5["entity_id"]]), field("yield_measurement_basis", None)],
        unresolved=["Yield/ee measurement bases, atmosphere, workup, and purification are not stated."],
    ))

# Table 1: eight distinct optimization rows.
table1_rows = [
    (1, 1.2, "CH2Cl2", 1.5, 81, "96/4", "r.t."),
    (2, 1.2, "CH3CN", 1.4, 89, "91/9", "r.t."),
    (3, 1.2, "THF", 1.8, 85, "89/11", "r.t."),
    (4, 1.2, "DMF", 16, 82, "89/11", "r.t."),
    (5, 1.2, "c-hexane", 1.2, 76, "97/3", "r.t."),
    (6, 1.2, "n-hexane", 1.9, 58, "99/1", "r.t."),
    (7, 1.0, "n-hexane", 1.5, 88, "98/2", "r.t."),
    (8, 1.0, "n-hexane", 2, 75, "95/5", q(-20, "°C")),
]
solvent_smiles = {"CH2Cl2": "ClCCl", "CH3CN": "CC#N", "THF": "C1CCOC1", "DMF": "CN(C)C=O", "c-hexane": "C1CCCCC1", "n-hexane": "CCCCCC"}
for n, equiv, solvent, hours, yld, ze, temp in table1_rows:
    evidence = ev(2) + (ev(1) if n == 1 else [])
    p5a = participant("5a", "reactant", "4,5-decadienol (5a)", evidence, smiles="OCCCC=C=CCCCC")
    i2 = participant("iodine", "reagent", "I2", evidence, smiles="II", amounts=[field("equivalents", q(equiv, "equiv"), ev(2))])
    solv = participant("solvent", "solvent", solvent, evidence, smiles=solvent_smiles[solvent])
    p6a = participant("6a", "product", "2-(1'-iodo-1'(Z)-hexenyl)tetrahydrofuran (6a)", evidence, smiles="IC(=CCCCC)C1CCCO1")
    notes = []
    if n == 1:
        notes.append("The prose states that seven-membered product 7a was not formed in this initial experiment.")
    records.append(rec(
        f"table1_entry{n}", "optimization_entry", evidence, [p5a, i2, solv, p6a],
        [step("iodoetherification", ["5a", "iodine", "solvent", "6a"], [field("temperature", temp, ev(2)), field("time", q(hours, "h"), ev(2))] + missing_ops())],
        [field("nmr_yield", q(yld, "%"), ev(2), ["6a"]), field("Z_E_ratio", ze, ev(2), ["6a"]), field("yield_and_ratio_measurement_basis", "1H NMR analysis (400 MHz)", ev(2))],
        notes=notes,
        unresolved=["Reaction scale, atmosphere, workup, and purification are not stated for the optimization row.", "Candidate structures and alkene geometry remain unverified."],
    ))

# Scheme 2: additional I2 scope outside Table 2.
scheme2_rows = [
    ("5j", "6j", "R1 = C2H5 (6,6-disubstituted allenol)", 65, 48, None),
    ("5k", "6k", "R1 = n-C3H7 (6,6-disubstituted allenol)", 60, 51, None),
    ("5l", "6l", "cyclohexylidene allene with a 3-methyl substituent", 40, 53, ">99/1"),
]
for s, p, descriptor, mins, yld, dr in scheme2_rows:
    evidence = ev(2)
    parts = [
        participant(s, "reactant", f"allenol {s}: {descriptor}", evidence),
        participant("iodine", "reagent", "I2", evidence, smiles="II", amounts=[field("equivalents", q(1.0, "equiv"), evidence)]),
        participant("n_hexane", "solvent", "n-hexane", evidence, smiles="CCCCCC"),
        participant(p, "product", f"iodocyclization product {p}", evidence),
    ]
    outcomes = [field("reported_yield", q(yld, "%"), evidence, [p]), field("yield_measurement_basis", None)]
    if dr:
        outcomes.append(field("dr_trans_cis", dr, evidence, [p]))
    records.append(rec(
        f"scheme2_{s}_to_{p}", "substrate_scope_entry", evidence, parts,
        [step("iodoetherification", [x["entity_id"] for x in parts], [field("temperature", "r.t.", evidence), field("time", q(mins, "min"), evidence)] + missing_ops())],
        outcomes,
        notes=["The text says Scheme 2 was conducted under the optimized Table 1 entry 7 conditions; 1.0 equivalent I2 is therefore source-linked through that explicit cross-reference."],
        unresolved=["Yield basis, scale, atmosphere, workup, purification, and complete structures are not stated or independently verified."],
    ))

# Scheme 3: difficult substrates under I2 or NIS conditions.
e2 = ev(2)
def scheme3_record(rid, substrate, reagent_label, solvent_label, product_labels, duration, yields, *, ze=None, negative=False):
    parts = [participant(substrate, "reactant", f"allenol {substrate}", e2)]
    reagent_id = "iodine" if reagent_label == "I2" else "nis"
    reagent_smiles = "II" if reagent_label == "I2" else None
    amounts = [field("equivalents", q(1.0, "equiv"), e2)] if reagent_label == "I2" else []
    parts.append(participant(reagent_id, "reagent", reagent_label, e2, smiles=reagent_smiles, amounts=amounts))
    solv_id = "n_hexane" if solvent_label == "n-hexane" else "ch2cl2"
    parts.append(participant(solv_id, "solvent", solvent_label, e2, smiles="CCCCCC" if solv_id == "n_hexane" else "ClCCl"))
    for pid, plabel in product_labels:
        parts.append(participant(pid, "product", plabel, e2))
    outcomes = []
    for pid, value, basis in yields:
        outcomes.append(field("reported_yield", q(value, "%"), e2, [pid]))
        outcomes.append(field(f"yield_measurement_basis_{pid}", basis, e2, [pid]))
    if ze:
        outcomes.append(field("E_Z_ratio", ze, e2, ["8m"]))
    if negative:
        outcomes.append(field("cyclic_product_detection", "no cyclic product detected by 1H NMR", e2))
    return rec(
        rid, "substrate_scope_entry", e2, parts,
        [step("iodoetherification", [x["entity_id"] for x in parts], [field("temperature", "r.t.", e2), field("time", duration, e2)] + missing_ops())],
        outcomes,
        notes=["I2 cases are described as optimized/standard reactions and inherit 1.0 equivalent I2 from Table 1 entry 7." if reagent_label == "I2" else "NIS loading is not stated in Scheme 3."],
        unresolved=["Scale, atmosphere, workup, purification, and complete structures are missing or unverified.", "NIS equivalents are not stated." if reagent_label == "NIS" else "The I2 loading is supported through the explicit optimized-condition cross-reference rather than printed on the Scheme 3 arrow."],
    )

records.append(scheme3_record(
    "scheme3_5m_i2", "5m", "I2", "n-hexane", [("6m", "expected tetrahydrofuran 6m"), ("8m", "5,6-diiodo-4-(n-butyl)-4-hexenol (8m)")], q(42, "min"), [("6m", 30, "1H NMR"), ("8m", 55, "1H NMR")], ze="3/2"
))
records.append(scheme3_record(
    "scheme3_5n_i2_no_cyclization", "5n", "I2", "n-hexane", [], q(1.5, "h"), [], negative=True
))
records.append(scheme3_record(
    "scheme3_5m_nis", "5m", "NIS", "CH2Cl2", [("6m", "tetrahydrofuran 6m")], q(1, "h"), [("6m", 84, None)]
))
records.append(scheme3_record(
    "scheme3_5n_nis", "5n", "NIS", "CH2Cl2", [("6n", "tetrahydrofuran 6n")], q(1.3, "h"), [("6n", 50, None)]
))

# Table 2: nine row-wise substrate-scope experiments. Entry 1 is enriched by the page-4 procedure.
table2_rows = [
    (1, "n-C4H9", "H", "H", "5a", "6a", 81, 45, "97/3", None),
    (2, "n-C5H11", "H", "H", "5b", "6b", 79, 50, "97/3", None),
    (3, "n-C6H13", "H", "H", "5c", "6c", 76, 60, "97/3", None),
    (4, "CH3", "C2H5", "H", "5d", "6d", 42, 40, ">99/1", None),
    (5, "n-C3H7", "n-C4H9", "H", "5e", "6e", 78, 60, ">99/1", None),
    (6, "CH3", "H", "n-C3H7", "5f", "6f", 73, 30, "97/3", ">98/2"),
    (7, "CH3", "H", "C2H5", "5g", "6g", 59, 40, "97/3", ">97/3"),
    (8, "n-C6H13", "H", "n-C3H7", "5h", "6h", 81, 25, "98/2", ">98/2"),
    (9, "n-C4H9", "H", "CH3", "5i", "6i", 81, 33, "96/4", ">96/4"),
]
for n, r1, r2, r3, s, p, yld, mins, ze, dr in table2_rows:
    evidence = ev(3) + (ev(4) if n == 1 else [])
    s_smiles = "OCCCC=C=CCCCC" if s == "5a" else None
    p_smiles = "IC(=CCCCC)C1CCCO1" if p == "6a" else None
    ps = participant(s, "reactant", f"{s} (R1={r1}, R2={r2}, R3={r3})", evidence, smiles=s_smiles)
    iodine_amounts = [field("equivalents", q(1.0, "equiv"), ev(3))]
    if n == 1:
        ps["amounts"] += [field("mass", q(61.9, "mg"), ev(4)), field("amount", q(0.40, "mmol"), ev(4))]
        iodine_amounts += [field("mass", q(103.1, "mg"), ev(4)), field("amount", q(0.41, "mmol"), ev(4))]
    iodine = participant("iodine", "reagent", "I2", evidence, smiles="II", amounts=iodine_amounts)
    hex_amounts = [field("initial_volume", q(1, "mL"), ev(4)), field("additional_volume", q(1, "mL"), ev(4))] if n == 1 else []
    hexane = participant("n_hexane", "solvent", "n-hexane", evidence, smiles="CCCCCC", amounts=hex_amounts)
    pp = participant(p, "product", f"iodocyclization product {p}", evidence, smiles=p_smiles)
    if n == 1:
        pp["amounts"].append(field("isolated_product_mass", q(91.2, "mg"), ev(4)))
    conditions = [field("temperature", "r.t.", ev(3)), field("time", q(mins, "min"), ev(3))]
    if n == 1:
        conditions += [
            field("operation", "sequential addition; TLC monitoring to complete conversion", ev(4)),
            field("workup", "quench with 10 mL H2O and saturated aqueous Na2S2O3; extract with 15 mL ether; wash with 10 mL water and 10 mL brine; dry over anhydrous Na2SO4; filter and evaporate", ev(4)),
            field("purification", "silica-gel chromatography, petroleum ether/ethyl acetate 40:1", ev(4)),
            field("atmosphere", None),
        ]
    else:
        conditions += missing_ops()
    outcomes = [
        field("isolated_yield", q(yld, "%"), evidence, [p]),
        field("yield_measurement_basis", "isolated after flash chromatography on silica gel", ev(3), [p]),
        field("Z_E_ratio", ze, ev(3), [p]),
        field("selectivity_measurement_basis", "1H NMR and 1H-1H NOESY analysis", ev(3), [p]),
    ]
    if dr:
        outcomes.append(field("dr_trans_cis", dr, ev(3), [p]))
    if n == 1:
        internal = participant("internal_standard", "reagent", "1,3,5-trimethylbenzene", ev(4), smiles="Cc1cc(C)cc(C)c1", amounts=[field("volume", q(18.5, "uL"), ev(4)), field("amount", q(0.13, "mmol"), ev(4))])
        parts = [ps, iodine, hexane, pp, internal]
        outcomes.append(field("procedure_Z_E_ratio", "97/3", ev(4), [p]))
    else:
        parts = [ps, iodine, hexane, pp]
    records.append(rec(
        f"table2_entry{n}_{p}", "substrate_scope_entry", evidence, parts,
        [step("iodoetherification", [x["entity_id"] for x in parts], conditions)], outcomes,
        notes=["The scope is explicitly stated to use optimized Table 1 entry 7 conditions; 1.0 equivalent I2 is therefore represented for each row."],
        unresolved=["Atmosphere is not stated." if n == 1 else "Scale, atmosphere, workup, and purification are not stated for this row.", "Candidate structure and stereochemistry require review."],
    ))

# Scheme 4: three asymmetric iodoetherifications and two kinetic resolutions.
e23 = ev(2) + ev(3)
parts = [
    participant("r5b", "reactant", "(R)-5b (R=n-C5H11, ee=95%)", e23, amounts=[field("starting_material_ee", q(95, "%"), e23)]),
    participant("iodine", "reagent", "I2", e23, smiles="II"),
    participant("n_hexane", "solvent", "n-hexane", e23, smiles="CCCCCC"),
    participant("s6b", "product", "(S)-6b", e23),
]
records.append(rec(
    "scheme4_r5b_i2", "reported_experiment", e23, parts,
    [step("asymmetric_iodoetherification", [x["entity_id"] for x in parts], [field("temperature", "r.t.", ev(3)), field("time", q(40, "min"), ev(3))] + missing_ops())],
    [field("reported_yield", q(80, "%"), e23, ["s6b"]), field("Z_E_ratio", "98/2", ev(3), ["s6b"]), field("product_ee", q(20, "%"), e23, ["s6b"]), field("yield_measurement_basis", None)],
    unresolved=["I2 loading, scale, yield basis, atmosphere, workup, and purification are not stated.", "Absolute configuration and candidate structure remain unverified."],
))

def nis_asym(suffix, rgroup, input_ee, mins, yld):
    evidence = ev(3) + (ev(4) if suffix == "b" else [])
    react = participant(f"r5{suffix}", "reactant", f"(R)-5{suffix} (R={rgroup})", evidence, amounts=[field("starting_material_ee", q(input_ee, "%"), evidence)])
    nis_amounts = []
    solv_amounts = []
    if suffix == "b":
        react["amounts"] += [field("mass", q(33.4, "mg"), ev(4)), field("amount", q(0.20, "mmol"), ev(4))]
        nis_amounts = [field("mass", q(54.4, "mg"), ev(4)), field("amount", q(0.24, "mmol"), ev(4)), field("equivalents", q(1.2, "equiv"), ev(4))]
        solv_amounts = [field("initial_volume", q(1, "mL"), ev(4)), field("additional_volume", q(1, "mL"), ev(4))]
    nis = participant("nis", "reagent", "NIS", evidence, amounts=nis_amounts)
    ch2cl2 = participant("ch2cl2", "solvent", "CH2Cl2", evidence, smiles="ClCCl", amounts=solv_amounts)
    zp = participant(f"sz6{suffix}", "product", f"(S)-Z-6{suffix}", evidence)
    ep = participant(f"re6{suffix}", "product", f"(R)-E-6{suffix}", evidence)
    if suffix == "b":
        zp["amounts"].append(field("combined_product_mass_with_E_isomer", q(54.3, "mg"), ev(4)))
    conditions = [field("temperature", "r.t.", evidence), field("time", q(mins, "min"), ev(3))]
    if suffix == "b":
        conditions += [field("operation", "sequential addition; TLC monitoring to completion", ev(4)), field("workup", "quench with 10 mL H2O; wash with saturated aqueous Na2S2O3; extract with 25 mL ether; wash with 10 mL water and 10 mL brine; dry over anhydrous Na2SO4; filter and evaporate", ev(4)), field("purification", "silica-gel chromatography, petroleum ether/ethyl acetate 40:1", ev(4)), field("atmosphere", None)]
    else:
        conditions += missing_ops()
    return rec(
        f"scheme4_r5{suffix}_nis", "reported_experiment", evidence, [react, nis, ch2cl2, zp, ep],
        [step("asymmetric_nis_iodoetherification", [react["entity_id"], "nis", "ch2cl2", zp["entity_id"], ep["entity_id"]], conditions)],
        [field("combined_product_yield", q(yld, "%"), evidence, [zp["entity_id"], ep["entity_id"]]), field("Z_E_ratio", "90/10", evidence, [zp["entity_id"], ep["entity_id"]]), field("yield_measurement_basis", "isolated after flash chromatography" if suffix == "b" else None, ev(4) if suffix == "b" else None)],
        unresolved=["Atmosphere is not stated." if suffix == "b" else "Scale, NIS loading, atmosphere, workup, purification, and yield basis are not stated.", "Product structures and absolute configurations remain unverified."],
    )

records.append(nis_asym("b", "n-C5H11", 95, 55, 93))
records.append(nis_asym("c", "n-C6H13", 98, 45, 88))

def kinetic(suffix, input_ee, output_ee, recovered_yield):
    evidence = ev(3) + (ev(4) if suffix == "b" else [])
    mix = participant(f"ze_mix_6{suffix}", "reactant", f"mixture of (S)-Z-6{suffix} and (R)-E-6{suffix} (Z/E=90/10)", evidence)
    if suffix == "b":
        mix["amounts"] += [field("mass", q(54.3, "mg"), ev(4)), field("amount", q(0.18, "mmol"), ev(4))]
    propargyl_amounts = [field("equivalents", q(0.25, "equiv"), ev(3))]
    amine_amounts = [field("equivalents", q(0.25, "equiv"), ev(3))]
    pd_amounts = [field("catalyst_loading", q(3.5, "mol%"), ev(3))]
    cui_amounts = [field("catalyst_loading", q(3.5, "mol%"), ev(3))]
    if suffix == "b":
        propargyl_amounts += [field("mass", q(3.2, "mg"), ev(4)), field("amount", q(0.057, "mmol"), ev(4))]
        amine_amounts += [field("mass", q(4.4, "mg"), ev(4)), field("amount", q(0.06, "mmol"), ev(4))]
        pd_amounts += [field("mass", q(4.9, "mg"), ev(4)), field("amount", q(0.007, "mmol"), ev(4))]
        cui_amounts += [field("mass", q(1.6, "mg"), ev(4)), field("amount", q(0.008, "mmol"), ev(4))]
    propargyl = participant("propargyl_alcohol", "reactant", "prop-2-yn-1-ol", evidence, smiles="C#CCO", amounts=propargyl_amounts)
    amine = participant("et2nh", "reagent", "Et2NH", evidence, smiles="CCNCC", amounts=amine_amounts)
    pd = participant("pd_catalyst", "catalyst", "Pd(PPh3)2Cl2", evidence, amounts=pd_amounts)
    cui = participant("cui", "catalyst", "CuI", evidence, smiles="[Cu]I", amounts=cui_amounts)
    mecn_amounts = [field("volume", q(2, "mL"), ev(4))] if suffix == "b" else []
    mecn = participant("mecn", "solvent", "CH3CN", evidence, smiles="CC#N", amounts=mecn_amounts)
    recovered = participant(f"recovered_sz6{suffix}", "product", f"recovered (S)-Z-6{suffix}", evidence)
    if suffix == "b":
        recovered["amounts"].append(field("isolated_mass", q(44.1, "mg"), ev(4)))
    conditions = [field("temperature", q(20, "°C") if suffix == "b" else "r.t.", evidence), field("time", q(20, "min"), evidence)]
    if suffix == "b":
        conditions += [field("atmosphere", "nitrogen", ev(4)), field("workup", "filter, wash with Et2O, and evaporate", ev(4)), field("purification", "silica-gel chromatography, petroleum ether/ethyl acetate 40:1", ev(4))]
    else:
        conditions += missing_ops()
    parts = [mix, propargyl, amine, pd, cui, mecn, recovered]
    return rec(
        f"scheme4_kinetic_resolution_6{suffix}", "reported_experiment", evidence, parts,
        [step("sonogashira_kinetic_resolution", [x["entity_id"] for x in parts], conditions)],
        [field("recovered_starting_material_yield", q(recovered_yield, "%"), evidence, [recovered["entity_id"]]), field("isolated_Z_E_ratio_after_resolution", ">99/1", evidence, [recovered["entity_id"]]), field("recovered_product_ee", q(output_ee, "%"), evidence, [recovered["entity_id"]]), field("yield_measurement_basis", "recovered after flash chromatography" if suffix == "b" else None, ev(4) if suffix == "b" else None)],
        unresolved=["The coupled E-isomer product and its yield are not reported in the covered source.", "Recovered-product structure and absolute configuration remain unverified."] + ([] if suffix == "b" else ["Scale, atmosphere, workup, purification, and yield basis are not stated for the 6c kinetic resolution."]),
    )

records.append(kinetic("b", 95, 95, 81))
records.append(kinetic("c", 98, 97, 77))

# Scheme 5: proposed stereochemical pathways only.
e3 = ev(3)
records.append(rec(
    "scheme5_stereochemical_mechanism", "mechanism", e3,
    [participant("generic_allenol", "reactant", "generic 4,5-allenol", e3), participant("iodonium_or_allylic_intermediate", "unspecified_agent", "proposed iodonium or 2-iodo-pi-allylic cationic intermediate", e3), participant("generic_product", "product", "generic iodoalkenyltetrahydrofuran", e3)],
    [step("proposed_cyclization", ["generic_allenol", "iodonium_or_allylic_intermediate", "generic_product"], [field("operation", "proposed intramolecular oxygen attack, deprotonation, and 1,2-chiral induction pathways", e3)])],
    [], notes=["The authors use the scheme to rationalize Z selectivity, reduced Z/E selectivity with NIS, and trans diastereoselectivity for 6f-i,l."],
    unresolved=["The depicted intermediates are proposed, not isolated or directly observed.", "Generic R groups prevent complete structure assignment."],
))

# Page 4: preparation of 5a, a distinct starting-material batch.
e4 = ev(4)
p4a = participant("4a", "reactant", "4a (4,5-decadienoic acid precursor)", e4, amounts=[field("mass", q(2.45, "g"), e4), field("amount", q(14.6, "mmol"), e4)])
lah = participant("lah", "reagent", "LiAlH4", e4, amounts=[field("mass", q(0.84, "g"), e4), field("amount", q(22.1, "mmol"), e4)])
ether = participant("ether", "solvent", "anhydrous ether", e4, smiles="CCOCC", amounts=[field("volume", q(37, "mL"), e4)])
p5a = participant("5a", "product", "4,5-decadienol (5a)", e4, smiles="OCCCC=C=CCCCC", amounts=[field("isolated_product_mass", q(1.41, "g"), e4)])
records.append(rec(
    "preparation_5a", "reported_experiment", e4, [p4a, lah, ether, p5a],
    [step("lithium_aluminium_hydride_reduction", ["4a", "lah", "ether", "5a"], [field("temperature", None), field("time", None), field("operation", "monitor by TLC until complete consumption", e4), field("workup", "quench with water; extract with ether three times; wash with brine; dry over anhydrous Na2SO4; filter and evaporate", e4), field("purification", "flash silica-gel chromatography, petroleum ether/ethyl acetate 5:1", e4), field("atmosphere", None)])],
    [field("isolated_yield", q(63, "%"), e4, ["5a"]), field("physical_form", "liquid", e4, ["5a"])],
    unresolved=["Reaction temperature, duration, and atmosphere are not stated.", "The structure assigned to 4a is label-based; candidate 5a connectivity remains unverified."],
))

assert len(records) == 40, len(records)

raw_path = OUT / "raw_model/records_pages_0001_0004.json"
raw_path.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")

ids = {r["source_reaction_id"]: r["record_id"] for r in records}
page2_ids = [
    *(ids[f"scheme1_1{x}_to_2{x}"] for x in "bc"),
    *(ids[f"scheme1_2{x}_to_3{x}"] for x in "bc"),
    *(ids[f"scheme1_3{x}_to_4{x}"] for x in "bc"),
    *(ids[f"scheme1_4{x}_to_5{x}"] for x in "bc"),
    *(ids[f"table1_entry{n}"] for n in range(1, 9)),
    *(ids[f"scheme2_5{x}_to_6{x}"] for x in "jkl"),
    ids["scheme3_5m_i2"], ids["scheme3_5n_i2_no_cyclization"], ids["scheme3_5m_nis"], ids["scheme3_5n_nis"],
    ids["scheme4_r5b_i2"],
]
page3_ids = [
    *(ids[f"table2_entry{n}_6{chr(96+n)}"] for n in range(1, 10)),
    ids["scheme4_r5b_i2"], ids["scheme4_r5b_nis"], ids["scheme4_r5c_nis"],
    ids["scheme4_kinetic_resolution_6b"], ids["scheme4_kinetic_resolution_6c"],
    ids["scheme5_stereochemical_mechanism"],
]
coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1,
            "state": "attempted",
            "regions": [
                {"region": "left-column graphical abstract", "finding": "Generic present-paper scope summary classified as a general scheme; it is not a batch-specific experiment.", "evidence_ids": ev(1)},
                {"region": "abstract, introduction, and upper-right preparation/cyclization prose", "finding": "Broad claims were not duplicated. The prose links to the Scheme 1 preparation route and Table 1 entry 1; cited Backvall bromoetherification remains prior-work context.", "evidence_ids": ev(1)},
            ],
            "record_ids": [ids["graphical_abstract_scope"], *(ids[f"scheme1_{a}{x}_to_{b}{x}"] for x in "bc" for a, b in [(1, 2), (2, 3), (3, 4), (4, 5)]), ids["table1_entry1"]],
            "unresolved": ["The graphical abstract contains generic R groups and scope ranges, not uniquely reconstructable structures.", "The Supporting Information mentioned in the paper was not supplied or explicitly associated."],
        },
        {
            "page": 2,
            "state": "attempted",
            "regions": [
                {"region": "upper-left Scheme 1", "finding": "Two optically active starting-material series were split by substrate and chemical stage into eight records; combined-arrow yield scopes are retained as unresolved where necessary.", "evidence_ids": ev(2)},
                {"region": "lower-left Table 1 and footnotes", "finding": "Eight independent solvent/I2-loading optimization rows extracted, including the -20 °C footnote override and 1H NMR basis.", "evidence_ids": ev(2)},
                {"region": "upper-right Scheme 2", "finding": "Three independent I2 cyclizations (5j, 5k, 5l) extracted; 5l retains dr >99/1.", "evidence_ids": ev(2)},
                {"region": "middle/lower-right Scheme 3 and adjacent prose", "finding": "I2 reactions of 5m/5n, including the 6m/8m mixture and failed cyclization, plus two NIS rescue reactions were extracted separately.", "evidence_ids": ev(2)},
                {"region": "bottom-right asymmetric-cyclization prose", "finding": "The optically active (R)-5b/I2 result was linked to the full Scheme 4 record on page 3 rather than duplicated.", "evidence_ids": ev(2)},
            ],
            "record_ids": page2_ids,
            "unresolved": ["Schemes 2-3 omit yield basis and most operational details.", "NIS loadings for 5m/5n are not stated.", "Several complex structures and stereochemical assignments remain unverified."],
        },
        {
            "page": 3,
            "state": "attempted",
            "regions": [
                {"region": "top Table 2 and footnotes", "finding": "Nine independent I2 substrate-scope rows extracted with isolated yield, time, Z/E, and row-specific dr.", "evidence_ids": ev(3)},
                {"region": "middle-left Scheme 4", "finding": "Three asymmetric iodoetherifications and two substrate-specific Sonogashira kinetic resolutions extracted; repeated page-4 procedures are merged into the same records.", "evidence_ids": ev(3)},
                {"region": "middle/lower-right Scheme 5 and explanatory prose", "finding": "Proposed iodonium/allylic-cation stereochemical rationale classified as mechanism, not an observed experiment.", "evidence_ids": ev(3)},
            ],
            "record_ids": page3_ids,
            "unresolved": ["Most scope rows omit scale, atmosphere, workup, and purification.", "The Scheme 4 6c kinetic-resolution batch lacks exact quantities and operational details.", "Mechanistic intermediates are proposed and not isolated."],
        },
        {
            "page": 4,
            "state": "attempted",
            "regions": [
                {"region": "upper-left preparation of 5a", "finding": "Detailed LiAlH4 reduction batch extracted as a distinct starting-material preparation.", "evidence_ids": ev(4)},
                {"region": "left-column preparation of 6a", "finding": "Detailed batch merged into Table 2 entry 1, adding exact amounts, workup, purification, isolated mass, and the procedure Z/E value.", "evidence_ids": ev(4)},
                {"region": "lower-left to upper-right optically active 6b preparation", "finding": "Detailed NIS batch merged into Scheme 4 (R)-5b/NIS record.", "evidence_ids": ev(4)},
                {"region": "upper-right kinetic resolution of 6b", "finding": "Detailed Sonogashira resolution merged into the Scheme 4 6b kinetic-resolution record; 81% is represented as recovery of (S)-Z-6b.", "evidence_ids": ev(4)},
                {"region": "acknowledgment and Supporting Information notice", "finding": "No additional experiment. SI availability notice was not treated as an associated SI file.", "evidence_ids": ev(4)},
            ],
            "record_ids": [ids["preparation_5a"], ids["table2_entry1_6a"], ids["scheme4_r5b_nis"], ids["scheme4_kinetic_resolution_6b"]],
            "unresolved": ["The 5a reduction omits reaction temperature, duration, and atmosphere.", "The detailed 6a and NIS-6b procedures omit atmosphere.", "Analytical data support identity but do not independently verify machine structures."],
        },
    ],
}
(OUT / "coverage").mkdir(parents=True, exist_ok=True)
(OUT / "coverage/pages_0001_0004.json").write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

tasks_path = OUT / "tasks.json"
tasks = json.loads(tasks_path.read_text())
for task in tasks:
    if task.get("document_id") == DOC and task.get("evidence_id") in {f"{DOC}:page{i}:text" for i in range(1, 5)}:
        task["state"] = "attempted"
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"records": len(records), "raw": str(raw_path), "coverage_pages": [p["page"] for p in coverage["pages"]]}, ensure_ascii=False))
