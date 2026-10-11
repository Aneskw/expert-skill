#!/usr/bin/env python3
"""Build source-derived, machine-review records for jo981315o PDF pages 1--4."""

import json
from pathlib import Path


DOC = "doc_34dfcc3e203262e7"
OUT = Path(__file__).with_name("records_pages_0001_0004.json")
COVERAGE = Path(__file__).parents[1] / "coverage" / "pages_0001_0004.json"

P1T = f"{DOC}:page1:text"
P1I = f"{DOC}:page1:image"
P2T = f"{DOC}:page2:text"
P2I = f"{DOC}:page2:image"
P3T = f"{DOC}:page3:text"
P3I = f"{DOC}:page3:image"
P4T = f"{DOC}:page4:text"
P4I = f"{DOC}:page4:image"


def fact(value, evidence):
    return {
        "value": value,
        "evidence_ids": [] if value is None else list(evidence),
        "verification": "missing" if value is None else "unreviewed",
    }


def field(name, value, evidence):
    return {"name": name, "fact": fact(value, evidence)}


def amount(name, number, unit, evidence):
    return field(name, {"number": number, "unit": unit}, evidence)


def participant(entity_id, role, evidence, *, label=None, name=None, amounts=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence),
        "smiles": fact(None, []),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": amounts or [],
    }


def step(step_id, participant_ids, conditions):
    return {
        "step_id": step_id,
        "participant_ids": participant_ids,
        "conditions": conditions,
    }


def record(suffix, source_id, kind, evidence, participants, steps, outcomes,
           notes=None, unresolved=None):
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
        "notes": [fact(value, ev) for value, ev in (notes or [])],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": (unresolved or []) + [
                "No Supporting Information file is supplied or associated; SI-only spectra and any omitted experimental details remain unavailable.",
                "Participant structures and SMILES remain unverified and are intentionally left null.",
            ],
        },
    }


records = []

# Scheme 1: a cited prior benzylation and the open generic ArX question are not
# current-paper experimental runs.
ev = [P1I, P1T]
records.append(record(
    "scheme1_prior_benzylation", "Scheme 1 upper arrow", "literature_example", ev,
    [
        participant("s1_start", "reactant", ev, label="1", name="1-phenyl-1-propyne"),
        participant("s1_hg", "catalyst", ev, name="mercury(II) chloride", amounts=[amount("loading", 1.5, "mol%", ev)]),
        participant("s1_buli", "reagent", ev, name="n-butyllithium"),
        participant("s1_bnbr", "reactant", ev, name="benzyl bromide"),
        participant("s1_product", "product", ev, label="depicted benzylation product"),
    ],
    [step("benzylation", ["s1_start", "s1_hg", "s1_buli", "s1_bnbr"], [])],
    [field("yield", {"number": 65, "unit": "%"}, ev)],
    notes=[("Scheme 1 and the surrounding prose identify this benzyl-halide reaction as the authors' prior work, not a new experiment in this paper.", ev)],
    unresolved=["Yield measurement basis and the cited prior procedure are not reproduced on the supplied pages."],
))
records.append(record(
    "scheme1_arx_question", "Scheme 1 lower arrow", "general_scheme", ev,
    [
        participant("s1q_start", "reactant", ev, label="1", name="1-phenyl-1-propyne"),
        participant("s1q_hg", "catalyst", ev, name="mercury(II) chloride", amounts=[amount("loading", 1.5, "mol%", ev)]),
        participant("s1q_buli", "reagent", ev, name="n-butyllithium"),
        participant("s1q_arx", "reactant", ev, label="ArX", name="aryl halide"),
    ],
    [step("generic_question", ["s1q_start", "s1q_hg", "s1q_buli", "s1q_arx"], [])],
    [field("product_identity", None, [])],
    notes=[("The question mark in Scheme 1 frames the study; it is not a reported product or yield.", ev)],
    unresolved=["ArX and the product are generic/unknown in this scheme."],
))


def common_start_participants(prefix, evidence, include_hg=True):
    parts = [
        participant(prefix + "_start", "reactant", evidence, label="1a", name="1-phenyl-1-propyne"),
        participant(prefix + "_buli", "reagent", evidence, name="n-butyllithium"),
    ]
    if include_hg:
        parts.insert(1, participant(prefix + "_hg", "catalyst", evidence, name="mercury(II) chloride", amounts=[amount("loading", 1.5, "mol%", evidence)]))
    return parts


# Scheme 2 arrows, merged with their detailed page-3 procedures where present.
ev = [P1I, P1T, P3I, P3T]
p = common_start_participants("s2a", ev, True) + [
    participant("s2a_thf", "solvent", ev, name="tetrahydrofuran", amounts=[amount("initial_volume", 2, "mL", ev)]),
    participant("s2a_phi", "reactant", ev, name="iodobenzene", amounts=[amount("mass", 224, "mg", ev), amount("amount", 1.1, "mmol", ev)]),
]
p[0]["amounts"] = [amount("mass", 116, "mg", ev), amount("amount", 1, "mmol", ev)]
p[1]["amounts"] += [amount("mass", 4, "mg", ev), amount("amount", 0.015, "mmol", ev)]
p[2]["amounts"] = [amount("volume", 0.7, "mL", ev), amount("concentration", 1.6, "M", ev), amount("amount", 1.1, "mmol", ev)]
records.append(record(
    "scheme2_no_pd_no_zinc", "Scheme 2 arrow 1 / Experimental no-Pd reaction", "reported_experiment", ev,
    p,
    [
        step("lithiation", ["s2a_start", "s2a_hg", "s2a_buli", "s2a_thf"], [field("temperature", {"number": -78, "unit": "°C"}, ev), amount("time", 100, "min", ev), field("atmosphere", "N2", ev)]),
        step("iodobenzene_addition", ["s2a_phi"], [field("temperature", "room temperature", ev), amount("time", 4, "h", ev), field("monitoring", "TLC; petroleum ether (60-90 °C) eluent", ev)]),
    ],
    [field("reaction_result", "no reaction observed", ev), field("coupling_product_yield", None, [])],
    unresolved=["Volume of THF used to deliver iodobenzene and any workup/recovery are not reported."],
))

ev = [P1I, P1T, P3I, P3T]
p = common_start_participants("s2b", ev, True) + [
    participant("s2b_thf", "solvent", ev, name="tetrahydrofuran", amounts=[amount("initial_volume", 2, "mL", ev)]),
    participant("s2b_pd", "catalyst", ev, name="bis(triphenylphosphine)palladium(II) dichloride", amounts=[amount("mass", 36, "mg", ev), amount("amount", 0.05, "mmol", ev), amount("loading", 5, "mol%", ev)]),
    participant("s2b_phi", "reactant", ev, name="iodobenzene", amounts=[amount("mass", 224, "mg", ev), amount("amount", 1.1, "mmol", ev)]),
]
p[0]["amounts"] = [amount("mass", 116, "mg", ev), amount("amount", 1, "mmol", ev)]
p[1]["amounts"] += [amount("mass", 4, "mg", ev), amount("amount", 0.015, "mmol", ev)]
p[2]["amounts"] = [amount("volume", 0.7, "mL", ev), amount("concentration", 1.6, "M", ev), amount("amount", 1.1, "mmol", ev)]
records.append(record(
    "scheme2_pd_no_zinc", "Scheme 2 arrow 2 / Experimental no-Zn reaction", "reported_experiment", ev,
    p,
    [
        step("lithiation", ["s2b_start", "s2b_hg", "s2b_buli", "s2b_thf"], [field("temperature", {"number": -78, "unit": "°C"}, ev), amount("time", 100, "min", ev), field("atmosphere", "N2", ev)]),
        step("palladium_coupling_attempt", ["s2b_pd", "s2b_phi"], [field("temperature", "room temperature", ev), amount("time", 7, "h", ev), field("monitoring", "TLC", ev)]),
    ],
    [field("reaction_result", "no reaction observed", ev), field("coupling_product_yield", None, [])],
    unresolved=["No workup, material recovery, or product assay is reported beyond TLC."],
))

ev = [P1I, P1T, P3I, P3T]
p = common_start_participants("s2c", ev, False) + [
    participant("s2c_thf", "solvent", ev, name="tetrahydrofuran", amounts=[amount("initial_volume", 2, "mL", ev), amount("ZnBr2_solution_volume", 5, "mL", ev)]),
    participant("s2c_zn", "reagent", ev, name="zinc bromide", amounts=[amount("mass", 338, "mg", ev), amount("amount", 1.5, "mmol", ev)]),
    participant("s2c_pd", "catalyst", ev, name="bis(triphenylphosphine)palladium(II) dichloride", amounts=[amount("mass", 36, "mg", ev), amount("amount", 0.05, "mmol", ev), amount("loading", 5, "mol%", ev)]),
    participant("s2c_phi", "reactant", ev, name="iodobenzene", amounts=[amount("mass", 224, "mg", ev), amount("amount", 1.1, "mmol", ev)]),
    participant("s2c_product", "product", ev, label="2a", name="1,1-diphenylpropadiene"),
]
p[0]["amounts"] = [amount("mass", 116, "mg", ev), amount("amount", 1, "mmol", ev)]
p[1]["amounts"] = [amount("volume", 0.7, "mL", ev), amount("concentration", 1.6, "M", ev), amount("amount", 1.1, "mmol", ev)]
records.append(record(
    "scheme2_no_hg_2a_62", "Scheme 2 arrow 3 / Experimental Hg-free 2a procedure", "reported_experiment", ev,
    p,
    [
        step("lithiation", ["s2c_start", "s2c_buli", "s2c_thf"], [field("temperature", {"number": -78, "unit": "°C"}, ev), amount("time", 100, "min", ev), field("atmosphere", "N2", ev)]),
        step("transmetalation", ["s2c_zn"], [field("temperature", {"number": -78, "unit": "°C"}, ev), amount("time", 10, "min", ev)]),
        step("warming", [], [field("temperature", "room temperature", ev), amount("time", 20, "min", ev)]),
        step("coupling", ["s2c_pd", "s2c_phi"], [field("temperature", "room temperature", ev), field("time", "until TLC indicated completion", ev)]),
        step("workup", [], [field("quench", "water", ev), field("extraction", "petroleum ether (60-90 °C)", ev), field("drying", "MgSO4", ev), field("concentration", "rotary evaporation", ev)]),
    ],
    [field("yield", {"number": 62, "unit": "%"}, ev), field("yield_measurement_basis", "1H NMR", ev)],
    notes=[("No HgCl2 was used in this experiment.", ev)],
    unresolved=["Coupling duration and isolated yield are not reported; the stated 62% is an NMR yield."],
))

ev = [P1I, P1T, P2I, P2T]
p = common_start_participants("s2d", ev, True) + [
    participant("s2d_zn", "reagent", ev, name="zinc bromide"),
    participant("s2d_pd", "catalyst", ev, name="bis(triphenylphosphine)palladium(II) dichloride"),
    participant("s2d_phi", "reactant", ev, name="iodobenzene"),
    participant("s2d_2a", "product", ev, label="2a", name="1,1-diphenylpropadiene"),
    participant("s2d_3a", "product", ev, label="3a", name="1,3-diphenyl-1-propyne"),
]
records.append(record(
    "scheme2_hg_2a_88", "Scheme 2 arrow 4", "reported_experiment", ev,
    p,
    [
        step("monolithiation", ["s2d_start", "s2d_hg", "s2d_buli"], [field("solvent", "THF", ev), field("temperature", {"number": -78, "unit": "°C"}, ev)]),
        step("transmetalation", ["s2d_zn"], []),
        step("coupling", ["s2d_pd", "s2d_phi"], []),
    ],
    [
        field("2a_yield", {"number": 88, "unit": "%"}, ev),
        field("2a_yield_measurement_basis", "NMR", ev),
        field("3a_regioisomer", "<2%, if any", ev),
    ],
    notes=[("Crude 1H NMR showed allene 2a as the only product, with regioisomer 3a below 2% if present.", ev)],
    unresolved=["Reagent quantities, stage durations, workup, and isolation are not given for this Scheme 2 run."],
))


# Table 1.  Each row is a distinct experiment.  Page 3 names/characterizes the
# isolated products and gives the typical sequence, but row-specific charges are
# not transferred unless explicitly reported for 2b (entry 3).
TABLE = [
    (1, "1a", "1-phenyl-1-propyne", True, "B", "iodobenzene", 5, "2a", "1,1-diphenylpropadiene", 83),
    (2, "1a", "1-phenyl-1-propyne", True, "B", "bromobenzene", 3.5, "2a", "1,1-diphenylpropadiene", 0),
    (3, "1a", "1-phenyl-1-propyne", True, "B", "p-methylphenyl iodide", 3, "2b", "1-phenyl-1-(4-methylphenyl)propadiene", 79),
    (4, "1a", "1-phenyl-1-propyne", True, "A", "p-methylphenyl iodide", 2.5, "2b", "1-phenyl-1-(4-methylphenyl)propadiene", 49),
    (5, "1a", "1-phenyl-1-propyne", True, "B", "p-methoxyphenyl iodide", 8, "2c", "1-phenyl-1-(4-methoxyphenyl)propadiene", 69),
    (6, "1a", "1-phenyl-1-propyne", True, "A", "p-nitrophenyl bromide", 7, "2d", "1-phenyl-1-(4-nitrophenyl)propadiene", 55),
    (7, "1a", "1-phenyl-1-propyne", True, "B", "1-iodonaphthalene", 3.5, "2e", "1-phenyl-1-(1-naphthyl)propadiene", 55),
    (8, "1b", "1-phenyl-1-hexyne", True, "B", "iodobenzene", 2, "2f", "1,1-diphenyl-1,2-hexadiene", 75),
    (9, "1b", "1-phenyl-1-hexyne", True, "B", "p-methylphenyl iodide", 1.5, "2g", "1-phenyl-1-(4-methylphenyl)-1,2-hexadiene", 68),
    (10, "1b", "1-phenyl-1-hexyne", False, "B", "p-methylphenyl iodide", 1.5, "2g", "1-phenyl-1-(4-methylphenyl)-1,2-hexadiene", 36),
    (11, "1b", "1-phenyl-1-hexyne", True, "B", "p-methoxyphenyl iodide", 8, "2h", "1-phenyl-1-(4-methoxyphenyl)-1,2-hexadiene", 45),
    (12, "1b", "1-phenyl-1-hexyne", True, "B", "1-iodonaphthalene", 1.5, "2i", "1-phenyl-1-(1-naphthyl)-1,2-hexadiene", 54),
    (13, "1b", "1-phenyl-1-hexyne", False, "B", "1-iodonaphthalene", 1.5, "2i", "1-phenyl-1-(1-naphthyl)-1,2-hexadiene", 45),
]

for entry, sub_label, sub_name, use_hg, cat_code, arx, hours, prod_label, prod_name, yld in TABLE:
    row_ev = [P2I, P2T] if entry == 2 else [P2I, P2T, P3I, P3T]
    prefix = f"t{entry:02d}"
    cat_name = "bis(triphenylphosphine)palladium(II) dichloride" if cat_code == "A" else "tetrakis(triphenylphosphine)palladium(0)"
    parts = [
        participant(prefix + "_substrate", "reactant", row_ev, label=sub_label, name=sub_name),
        participant(prefix + "_buli", "reagent", row_ev, name="n-butyllithium"),
        participant(prefix + "_zn", "reagent", row_ev, name="zinc bromide"),
        participant(prefix + "_arx", "reactant", row_ev, name=arx),
        participant(prefix + "_cat", "catalyst", row_ev, label=cat_code, name=cat_name),
        participant(prefix + "_product", "product", row_ev, label=prod_label, name=prod_name),
    ]
    if use_hg:
        parts.insert(1, participant(prefix + "_hg", "catalyst", row_ev, name="mercury(II) chloride", amounts=[amount("loading", 1.5, "mol%", row_ev)]))
    lith_ids = [prefix + "_substrate", prefix + "_buli"] + ([prefix + "_hg"] if use_hg else [])
    lith_temp = "room temperature" if entry >= 8 else {"number": -78, "unit": "°C"}
    steps = [
        step("monolithiation", lith_ids, [field("temperature", lith_temp, row_ev), amount("time", 100, "min", row_ev)]),
        step("transmetalation", [prefix + "_zn"], []),
        step("coupling", [prefix + "_arx", prefix + "_cat"], [field("temperature", "room temperature", row_ev), amount("time", hours, "h", row_ev)]),
    ]
    notes = [("Table 1 footnote b defines the reported yield as isolated yield.", [P2I, P2T])]
    if not use_hg:
        notes.append(("Table 1 footnote d: no HgCl2 was added.", [P2I, P2T]))
    if entry >= 8:
        notes.append(("Table 1 footnote c: monolithiation was performed at room temperature for 100 min before ZnBr2 addition.", [P2I, P2T]))
    unresolved = [
        "The table and 'prepared similarly' statement do not independently report every row-specific charge, concentration, atmosphere, workup, or purification detail.",
    ]
    if entry == 2:
        unresolved.append("The 0% row identifies anticipated product 2a but does not report recovered starting material or an assay detection limit.")
    records.append(record(
        f"table1_entry_{entry:02d}", f"Table 1 entry {entry}", "optimization_entry" if entry <= 4 or entry in (10, 13) else "substrate_scope_entry", row_ev,
        parts, steps,
        [field("yield", {"number": yld, "unit": "%"}, [P2I, P2T]), field("yield_measurement_basis", "isolated yield", [P2I, P2T])],
        notes=notes,
        unresolved=unresolved,
    ))

# Enrich the detailed Table 1 entry 3 with the explicit typical-procedure charges,
# workup, and purification rather than adding a duplicate record.
entry3 = next(r for r in records if r["record_id"].endswith("table1_entry_03"))
ev3 = [P2I, P2T, P3I, P3T]
by_id = {p["entity_id"]: p for p in entry3["participants"]}
by_id["t03_substrate"]["amounts"] = [amount("mass", 116, "mg", ev3), amount("amount", 1, "mmol", ev3)]
by_id["t03_hg"]["amounts"] += [amount("mass", 4, "mg", ev3), amount("amount", 0.015, "mmol", ev3)]
by_id["t03_buli"]["amounts"] = [amount("volume", 0.7, "mL", ev3), amount("concentration", 1.6, "M", ev3), amount("amount", 1.1, "mmol", ev3)]
by_id["t03_zn"]["amounts"] = [amount("mass", 338, "mg", ev3), amount("amount", 1.5, "mmol", ev3)]
by_id["t03_arx"]["amounts"] = [amount("mass", 262, "mg", ev3), amount("amount", 1.2, "mmol", ev3)]
by_id["t03_cat"]["amounts"] = [amount("mass", 58, "mg", ev3), amount("amount", 0.05, "mmol", ev3), amount("loading", 5, "mol%", ev3)]
entry3["participants"].append(participant("t03_thf", "solvent", ev3, name="tetrahydrofuran", amounts=[amount("initial_volume", 2, "mL", ev3), amount("ZnBr2_solution_volume", 5, "mL", ev3)]))
entry3["steps"] = [
    step("monolithiation", ["t03_substrate", "t03_hg", "t03_buli", "t03_thf"], [field("temperature", {"number": -78, "unit": "°C"}, ev3), amount("time", 100, "min", ev3), field("atmosphere", "N2", ev3)]),
    step("transmetalation", ["t03_zn"], [field("temperature", {"number": -78, "unit": "°C"}, ev3), amount("time", 10, "min", ev3)]),
    step("warming", [], [field("temperature", "room temperature", ev3), amount("time", 20, "min", ev3)]),
    step("coupling", ["t03_arx", "t03_cat"], [field("temperature", "room temperature", ev3), amount("time", 3, "h", [P2I, P2T]), field("monitoring", "TLC; petroleum ether (60-90 °C) eluent", ev3)]),
    step("workup_and_purification", [], [field("quench", "water", ev3), field("extraction", "petroleum ether (60-90 °C)", ev3), field("drying", "MgSO4", ev3), field("concentration", "rotary evaporation", ev3), field("purification", "silica gel chromatography; petroleum ether (60-90 °C)", ev3)]),
]
entry3["outcomes"].extend([amount("isolated_mass", 163, "mg", [P3I, P3T]), field("physical_state", "liquid", [P3I, P3T])])
entry3["review"]["unresolved"] = [
    "Final reaction volume/concentration and product purity are not reported.",
    "No Supporting Information file is supplied or associated; SI-only spectra and any omitted experimental details remain unavailable.",
    "Participant structures and SMILES remain unverified and are intentionally left null.",
]

# A prose-only unsuccessful alkenyl-iodide scope test.
ev = [P2I, P2T]
records.append(record(
    "alkenyl_iodide_failure", "Results prose: 1-iodo-(1E)-hexene", "reported_experiment", ev,
    [
        participant("vinyl_i", "reactant", ev, name="1-iodo-(1E)-hexene"),
        participant("vinyl_product", "product", ev, label="corresponding cross-coupling product"),
    ],
    [step("coupling_attempt", ["vinyl_i"], [field("conditions", "under the same conditions", ev)])],
    [field("yield", None, []), field("reaction_result", "did not afford the corresponding cross-coupling product in decent yield", ev)],
    unresolved=["The antecedent of 'same conditions,' substrate identity, numerical yield, assay method, and workup are not specified in this prose statement."],
))

# Proposed catalytic cycle in Scheme 3; this is explicitly mechanistic, not an
# observed experimental run.
ev = [P2I, P2T, P3I, P3T]
records.append(record(
    "scheme3_mechanism", "Scheme 3", "mechanism", ev,
    [
        participant("m_ar_i", "reactant", ev, label="ArI", name="aryl iodide"),
        participant("m_pd0", "catalyst", ev, label="Pd(0)"),
        participant("m_1", "reactant", ev, label="1", name="generic 1-phenyl-1-alkyne"),
        participant("m_4", "unspecified_agent", ev, label="4", name="allenic zinc reagent"),
        participant("m_5", "unspecified_agent", ev, label="5", name="propargylic zinc reagent"),
        participant("m_6", "unspecified_agent", ev, label="6", name="allenic arylpalladium intermediate"),
        participant("m_7", "unspecified_agent", ev, label="7", name="propargylic arylpalladium intermediate"),
        participant("m_2", "product", ev, label="2", name="generic 1,1-diaryl-1,2-diene"),
    ],
    [
        step("oxidative_addition", ["m_ar_i", "m_pd0"], [field("proposed_intermediate", "ArPdI", ev)]),
        step("zinc_reagent_formation", ["m_1"], [field("sequence_A", "a) 1.5% HgCl2; b) n-BuLi; c) ZnBr2", ev)]),
        step("transmetalation_and_rearrangement", ["m_4", "m_5", "m_6", "m_7"], [field("proposal", "7 rearranges to 6", ev)]),
        step("reductive_elimination", ["m_6", "m_2"], [field("proposal", "forms product 2 and regenerates Pd(0)", ev)]),
    ],
    [],
    notes=[("The article calls this a plausible mechanism; intermediates 4-7 are proposed and not isolated experiments.", ev)],
    unresolved=["Generic Ar/R substituents are not fully specified and no mechanistic intermediate is independently quantified."],
))

# Water-quench probe reported separately from the coupling experiments.
ev = [P2T, P3I, P3T]
p = common_start_participants("q", ev, True) + [
    participant("q_thf", "solvent", ev, name="tetrahydrofuran", amounts=[amount("initial_volume", 2, "mL", ev), amount("ZnBr2_solution_volume", 5, "mL", ev)]),
    participant("q_zn", "reagent", ev, name="zinc bromide", amounts=[amount("mass", 338, "mg", ev), amount("amount", 1.5, "mmol", ev)]),
    participant("q_water", "reagent", ev, name="water"),
    participant("q_allene", "product", ev, name="1-phenylpropadiene"),
    participant("q_recovered", "product", ev, name="1-phenyl-1-propyne", label="recovered starting material"),
]
p[0]["amounts"] = [amount("mass", 116, "mg", ev), amount("amount", 1, "mmol", ev)]
p[1]["amounts"] += [amount("mass", 4, "mg", ev), amount("amount", 0.015, "mmol", ev)]
p[2]["amounts"] = [amount("volume", 0.7, "mL", ev), amount("concentration", 1.6, "M", ev), amount("amount", 1.1, "mmol", ev)]
records.append(record(
    "water_quench_probe", "Experimental water quench of allenyl/propargyl zinc mixture", "reported_experiment", ev,
    p,
    [
        step("monolithiation", ["q_start", "q_hg", "q_buli", "q_thf"], [field("temperature", {"number": -78, "unit": "°C"}, ev), amount("time", 100, "min", ev), field("atmosphere", "N2", ev)]),
        step("transmetalation", ["q_zn"], [field("temperature", {"number": -78, "unit": "°C"}, ev), amount("time", 10, "min", ev)]),
        step("warming", [], [field("temperature", "room temperature", ev), amount("time", 20, "min", ev)]),
        step("quench_and_workup", ["q_water"], [field("extraction", "diethyl ether", ev), field("drying", "MgSO4", ev), field("concentration", "rotary evaporation", ev)]),
    ],
    [
        field("1-phenylpropadiene_yield", {"number": 44, "unit": "%"}, ev),
        field("1-phenyl-1-propyne_recovery", {"number": 38, "unit": "%"}, ev),
        field("measurement_basis", "1H NMR using CH2Br2 as internal standard", ev),
    ],
    unresolved=["No isolated masses, quench-water amount, extraction volumes, or balance for the remaining material are reported."],
))


coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1,
            "state": "attempted",
            "regions": [
                {"region": "upper-right Scheme 1", "finding": "One cited prior-work benzylation arrow (65%) and one generic ArX question-mark arrow; classified as literature_example and general_scheme, not current experiments.", "evidence_ids": [P1I, P1T]},
                {"region": "right-center Scheme 2", "finding": "Four distinct condition arrows: two no-reaction controls, Hg-free 2a at 62% NMR yield, and Hg-assisted 2a at 88% NMR yield with regioisomer 3a below 2% if any.", "evidence_ids": [P1I, P1T]},
                {"region": "lower-right Results and Discussion prose", "finding": "Prose corroborates Scheme 2 outcomes and distinguishes organolithium, palladium, and organozinc conditions.", "evidence_ids": [P1I, P1T]},
            ],
            "record_ids": [
                f"{DOC}:scheme1_prior_benzylation", f"{DOC}:scheme1_arx_question",
                f"{DOC}:scheme2_no_pd_no_zinc", f"{DOC}:scheme2_pd_no_zinc",
                f"{DOC}:scheme2_no_hg_2a_62", f"{DOC}:scheme2_hg_2a_88",
            ],
            "unresolved": ["Scheme 1 prior-work yield basis is absent; Scheme 2's 88% run lacks full quantities and workup on the supplied pages."],
        },
        {
            "page": 2,
            "state": "attempted",
            "regions": [
                {"region": "top Table 1 including reaction header and footnotes", "finding": "Thirteen row-level experiments were read individually, including the 0% phenyl-bromide row, catalyst A/B comparisons, room-temperature monolithiation footnote, and no-Hg footnote overrides.", "evidence_ids": [P2I, P2T]},
                {"region": "lower-left discussion prose", "finding": "Crude-NMR regioselectivity for Scheme 2 and a prose-only unsuccessful 1-iodo-(1E)-hexene coupling were retained; the latter lacks a numerical yield.", "evidence_ids": [P2I, P2T]},
                {"region": "lower-center/right mechanism discussion", "finding": "Plausible Pd(0) cycle and intermediates 4-7 are classified as a mechanism and linked to Scheme 3, not as observed experimental runs.", "evidence_ids": [P2I, P2T]},
            ],
            "record_ids": [f"{DOC}:scheme2_hg_2a_88"] + [f"{DOC}:table1_entry_{i:02d}" for i in range(1, 14)] + [f"{DOC}:alkenyl_iodide_failure", f"{DOC}:scheme3_mechanism", f"{DOC}:water_quench_probe"],
            "unresolved": ["Table rows do not independently state every charge/workup detail; the alkenyl-iodide test gives neither a numerical yield nor fully resolved antecedent conditions."],
        },
        {
            "page": 3,
            "state": "attempted",
            "regions": [
                {"region": "upper-left Scheme 3", "finding": "Proposed catalytic cycle with allenic/propargylic zinc and palladium intermediates; recorded once as mechanism, not as multiple experiments.", "evidence_ids": [P3I, P3T]},
                {"region": "left-column Experimental Section controls and Hg-free coupling", "finding": "Detailed no-Pd/no-Zn control, Pd/no-Zn control, and Hg-free 2a preparation were merged into the matching Scheme 2 records.", "evidence_ids": [P3I, P3T]},
                {"region": "column break and upper-right typical 2b procedure", "finding": "Detailed quantities, staged temperatures, workup, chromatography, 163 mg and 79% isolated yield were merged with Table 1 entry 3.", "evidence_ids": [P3I, P3T]},
                {"region": "right-column product series 2a-2i", "finding": "Prepared-similarly statement and product identities/isolated yields corroborate Table 1 rows; characterization paragraphs were not duplicated as reaction runs.", "evidence_ids": [P3I, P3T]},
                {"region": "lower-right water-quench experiment", "finding": "Distinct mechanistic probe gives 1-phenylpropadiene (44% NMR) and recovered 1-phenyl-1-propyne (38% NMR).", "evidence_ids": [P3I, P3T]},
            ],
            "record_ids": [
                f"{DOC}:scheme3_mechanism", f"{DOC}:scheme2_no_pd_no_zinc",
                f"{DOC}:scheme2_pd_no_zinc", f"{DOC}:scheme2_no_hg_2a_62",
            ] + [f"{DOC}:table1_entry_{i:02d}" for i in range(1, 14)] + [f"{DOC}:water_quench_probe"],
            "unresolved": ["Most entries rely on 'prepared similarly' rather than row-specific full procedures; supplied SI spectra for 2b-2i are absent."],
        },
        {
            "page": 4,
            "state": "attempted",
            "regions": [
                {"region": "top-left Supporting Information notice", "finding": "The main article states that 1H NMR spectra for 2b-2i exist, but no SI file is supplied or associated in this pilot.", "evidence_ids": [P4I, P4T]},
                {"region": "remainder headed Additions and Corrections", "finding": "This is appended journal matter for other articles (including an unrelated corrected fluorination table and two corrections); it is not experiment content of DOI 10.1021/jo981315o and was not converted into records.", "evidence_ids": [P4I, P4T]},
            ],
            "record_ids": [],
            "unresolved": ["SI association is unestablished and SI-only spectra/details cannot be reviewed; unrelated correction items were excluded from this article's experiment dataset."],
        },
    ],
}


OUT.parent.mkdir(parents=True, exist_ok=True)
COVERAGE.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
COVERAGE.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"records": len(records), "records_file": str(OUT), "coverage_file": str(COVERAGE)}, ensure_ascii=False))
