import json
from pathlib import Path


DOC = "doc_abf5932f5e203fa1"
ROOT = Path(__file__).resolve().parents[3]
RAW_OUT = Path(__file__).with_name("records_pages_0001_0004.json")
COVERAGE_OUT = ROOT / "runs/current/coverage/pages_0001_0004.json"


def eid(page, suffix):
    return f"{DOC}:page{page}:{suffix}"


def fact(value, evidence):
    return {
        "value": value,
        "evidence_ids": list(evidence) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def field(name, value, evidence):
    return {"name": name, "fact": fact(value, evidence)}


def participant(entity_id, role, label, name, evidence, amounts=()):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence),
        "smiles": fact(None, ()),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": [field(k, v, evidence) for k, v in amounts],
    }


def step(step_id, participant_ids, conditions):
    return {
        "step_id": step_id,
        "participant_ids": participant_ids,
        "conditions": conditions,
    }


def record(record_id, kind, evidence, participants, steps=(), outcomes=(), notes=(), source_reaction_id=None, unresolved=()):
    base_unresolved = [
        "No supporting-information file is supplied or associated in this pilot; unreported experimental details remain missing.",
        "Compound structures and all SMILES remain unverified; labels are retained from the source and machine candidates remain separate.",
    ]
    normalized_notes = []
    for note in notes:
        if set(note) == {"name", "fact"}:
            normalized_notes.append(fact({"name": note["name"], "value": note["fact"]["value"]}, note["fact"]["evidence_ids"]))
        else:
            normalized_notes.append(note)
    return {
        "record_id": f"{DOC}:manual:{record_id}",
        "document_id": DOC,
        "source_reaction_id": source_reaction_id,
        "record_kind": kind,
        "status": "needs_review",
        "completeness": "partial",
        "evidence_ids": list(dict.fromkeys(evidence)),
        "participants": list(participants),
        "steps": list(steps),
        "outcomes": list(outcomes),
        "notes": normalized_notes,
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": base_unresolved + list(unresolved),
        },
    }


records = []


# Page 1 graphical abstract and Scheme 1c are a generic scope statement, not an
# individual experiment. The repeated presentation is represented once.
ev_general = [eid(1, "block9"), eid(1, "block10"), eid(1, "image"), eid(2, "block4"), eid(2, "image")]
records.append(record(
    "p1p2_general_allenyl_ester_scope",
    "general_scheme",
    ev_general,
    [
        participant("general_hwe", "reactant", None, "bis(benzylthio)phosphoryl HWE-type reagent (generic CO2R1)", ev_general),
        participant("general_acid_chloride", "reactant", None, "2-phenyl-substituted acid chloride (generic R2)", ev_general, (("equivalents", {"number": 2, "unit": "equiv"}),)),
        participant("general_iprmgbr", "reagent", None, "i-PrMgBr", ev_general, (("equivalents", {"number": 1.1, "unit": "equiv"}),)),
        participant("general_et3n", "reagent", None, "Et3N", ev_general, (("equivalents", {"number": 4, "unit": "equiv"}),)),
        participant("general_thf", "solvent", None, "THF", ev_general),
        participant("general_allenyl_product", "product", None, "conjugated allenyl ester (generic R1/R2)", ev_general),
    ],
    [
        step("activation", ["general_hwe", "general_iprmgbr", "general_thf"], [field("temperature", {"number": 0, "unit": "degC"}, ev_general), field("time", {"number": 10, "unit": "min"}, ev_general)]),
        step("ketene_olefination", ["general_hwe", "general_acid_chloride", "general_et3n", "general_thf", "general_allenyl_product"], [field("temperature", {"number": 0, "unit": "degC"}, ev_general), field("time", "10 or 20 min", ev_general)]),
    ],
    outcomes=[field("reported_yield_range", "90-99%", ev_general)],
    notes=[field("scope_combinations", ["CO2Me/Me", "CO2Me/Et", "CO2Me/Ph", "CO2Bn/Me", "CO2Bn/Et", "CO2Bn/Ph"], ev_general)],
    source_reaction_id="rxn_0001",
    unresolved=("Generic R groups prevent assignment of a single complete molecular structure.",),
))


# Scheme 1a/b: explicitly marked previous work in the paper.
ev_s1 = [eid(2, "block4"), eid(2, "image")]


def literature_example(rid, reagent_label, base_name, base_eq, aldehyde_or_acid, second_eq, t1, t2, product_desc, yield_pct, selectivity, source_id):
    parts = [
        participant(f"{rid}_substrate", "reactant", reagent_label, None, ev_s1, (("equivalents", {"number": second_eq[0], "unit": "equiv"}),) if reagent_label == "2" else ()),
        participant(f"{rid}_partner", "reactant", aldehyde_or_acid[0], aldehyde_or_acid[1], ev_s1, (("equivalents", {"number": aldehyde_or_acid[2], "unit": "equiv"}),) if aldehyde_or_acid[2] else ()),
        participant(f"{rid}_base", "reagent", None, base_name, ev_s1, (("equivalents", {"number": base_eq, "unit": "equiv"}),)),
        participant(f"{rid}_product", "product", product_desc[0], product_desc[1], ev_s1),
    ]
    step1_ids = [f"{rid}_substrate", f"{rid}_base"]
    step2_ids = [f"{rid}_partner", f"{rid}_product"]
    if base_name == "i-PrMgBr":
        parts.append(participant(f"{rid}_solvent", "solvent", None, "THF", ev_s1))
        parts.append(participant(f"{rid}_et3n", "reagent", None, "Et3N", ev_s1, (("equivalents", {"number": 2, "unit": "equiv"}),)))
        step1_ids.append(f"{rid}_solvent")
        step2_ids.extend([f"{rid}_et3n", f"{rid}_solvent"])
    conditions1 = [field("temperature", t1[0], ev_s1), field("time", t1[1], ev_s1)]
    conditions2 = [field("temperature", t2[0], ev_s1), field("time", t2[1], ev_s1)]
    outs = [field("yield_percent", {"number": yield_pct, "unit": "%"}, ev_s1)]
    if selectivity:
        outs.append(field("E_Z_ratio", selectivity, ev_s1))
    records.append(record(
        rid, "literature_example", ev_s1, parts,
        [step("prior_work_step_1", step1_ids, conditions1), step("prior_work_step_2", step2_ids, conditions2)],
        outs,
        [field("source_classification", "Scheme explicitly labels this transformation as previous work", ev_s1)],
        source_reaction_id=source_id,
        unresolved=("This is a cited prior-work example, not a newly reported experiment in the current paper.",),
    ))


literature_example(
    "p2_scheme1a_prior_2015", "1", "i-PrMgBr", 1.1,
    ("3a", "2-phenylpropionyl chloride", 2), (None, None),
    ({"number": 0, "unit": "degC"}, {"number": 1, "unit": "h"}),
    ({"number": 0, "unit": "degC"}, {"number": 1, "unit": "h"}),
    ("4a", "methyl 4-phenylpenta-2,3-dienoate"), 98, None, "rxn_0004",
)
literature_example(
    "p2_scheme1b_prior_E", "2", "NaHMDS", 1.3,
    (None, "benzaldehyde (PhCHO)", None), (1.1, None),
    (None, None), ({"number": 0, "unit": "degC"}, None),
    (None, "(E)-methyl cinnamate"), 99, "100:0", "rxn_0002",
)
literature_example(
    "p2_scheme1b_prior_Z", "2", "NaHMDS", 1.1,
    (None, "benzaldehyde (PhCHO)", None), (1.3, None),
    (None, None), ({"number": -78, "unit": "degC"}, None),
    (None, "(Z)-methyl cinnamate"), 94, "2:98", "rxn_0003",
)


def hwe_scope_record(rid, kind, evidence, source_id, hwe_label, acid_label, product_label, grignard, t1, t2, et3n_eq, yield_value, yield_basis=None, notes=(), detailed=False):
    names = {
        "2": "methyl 2-[bis(benzylthio)phosphoryl]acetate",
        "3a": "2-phenylpropionyl chloride",
        "4a": "methyl 4-phenylpenta-2,3-dienoate",
    }
    pfx = rid.replace("-", "_")
    hwe_amounts = (("equivalents", {"number": 1, "unit": "equiv"}),)
    acid_amounts = (("equivalents", {"number": 2, "unit": "equiv"}),)
    base_amounts = (("equivalents", {"number": 1.1, "unit": "equiv"}),)
    et3_amounts = (("equivalents", {"number": et3n_eq, "unit": "equiv"}),)
    thf_amounts = ()
    product_amounts = ()
    if detailed:
        hwe_amounts += (("mass", {"number": 65.7, "unit": "mg"}), ("amount", {"number": 0.179, "unit": "mmol"}))
        acid_amounts += (("volume", {"number": 53.1, "unit": "uL"}), ("amount", {"number": 0.359, "unit": "mmol"}))
        base_amounts += (("concentration", {"number": 0.67, "unit": "M"}), ("volume", {"number": 294, "unit": "uL"}), ("amount", {"number": 0.197, "unit": "mmol"}))
        et3_amounts += (("volume", {"number": 100, "unit": "uL"}), ("amount", {"number": 0.717, "unit": "mmol"}))
        thf_amounts = (("volume", {"number": 1.5, "unit": "mL"}),)
        product_amounts = (("mass", {"number": 33.5, "unit": "mg"}),)
    parts = [
        participant(f"{pfx}_hwe", "reactant", hwe_label, names.get(hwe_label), evidence, hwe_amounts),
        participant(f"{pfx}_acid", "reactant", acid_label, names.get(acid_label), evidence, acid_amounts),
        participant(f"{pfx}_grignard", "reagent", None, grignard, evidence, base_amounts),
        participant(f"{pfx}_et3n", "reagent", None, "Et3N", evidence, et3_amounts),
        participant(f"{pfx}_thf", "solvent", None, "THF", evidence, thf_amounts),
        participant(f"{pfx}_product", "product", product_label, names.get(product_label), evidence, product_amounts),
    ]
    steps = [
        step("activation", [f"{pfx}_hwe", f"{pfx}_grignard", f"{pfx}_thf"], [field("temperature", {"number": 0, "unit": "degC"}, evidence), field("time", t1, evidence)]),
        step("ketene_generation_and_olefination", [f"{pfx}_acid", f"{pfx}_et3n", f"{pfx}_thf", f"{pfx}_product"], [field("temperature", {"number": 0, "unit": "degC"}, evidence), field("time", t2, evidence)]),
    ]
    if detailed:
        steps[0]["conditions"].append(field("atmosphere", "argon", [eid(4, "block23")]))
        steps[1]["conditions"].append(field("atmosphere", "argon", [eid(4, "block23")]))
        steps.append(step("workup_and_purification", [f"{pfx}_product"], [
            field("quench", "saturated aqueous NH4Cl (4 mL)", [eid(4, "block23")]),
            field("extraction", "CHCl3 (20 mL x 3)", [eid(4, "block23")]),
            field("drying", "anhydrous MgSO4", [eid(4, "block23")]),
            field("concentration", "in vacuo", [eid(4, "block23")]),
            field("purification", "flash chromatography, Silica Gel PSQ 60B, n-hexane/EtOAc 20:1", [eid(4, "block23")]),
        ]))
    outcomes = [field("yield_percent", yield_value, evidence)]
    if yield_basis:
        outcomes.append(field("yield_basis", yield_basis, evidence))
    if detailed:
        outcomes.append(field("appearance", "yellow oil", [eid(4, "block23")]))
    note_fields = [field(n, v, evidence) for n, v in notes]
    records.append(record(rid, kind, evidence, parts, steps, outcomes, note_fields, source_reaction_id=source_id))


# Table 1: seven independent optimization rows. Row 7 incorporates the detailed
# procedure in footnote 9 on page 4 rather than duplicating it.
ev_t1 = [eid(2, "block10"), eid(2, "block7"), eid(2, "image")]
t1_rows = [
    (1, {"number": 1, "unit": "h"}, {"number": 1, "unit": "h"}, 2, {"number": 85, "unit": "%"}, ()),
    (2, {"number": 1, "unit": "h"}, {"number": 30, "unit": "min"}, 2, {"number": 86, "unit": "%"}, ()),
    (3, {"number": 1, "unit": "h"}, {"number": 10, "unit": "min"}, 2, "ca. 96%", (("observed_impurity", "small amount of 2-phenylpropanoic anhydride"),)),
    (4, {"number": 30, "unit": "min"}, {"number": 10, "unit": "min"}, 2, "ca. 96%", (("observed_impurity", "small amount of 2-phenylpropanoic anhydride"),)),
    (5, {"number": 10, "unit": "min"}, {"number": 10, "unit": "min"}, 2, "ca. 96%", (("observed_impurity", "small amount of 2-phenylpropanoic anhydride"),)),
    (6, {"number": 10, "unit": "min"}, {"number": 10, "unit": "min"}, 3, "ca. 96%", (("observed_impurity", "small amount of 2-phenylpropanoic anhydride"),)),
    (7, {"number": 10, "unit": "min"}, {"number": 10, "unit": "min"}, 4, {"number": 99, "unit": "%"}, ()),
]
for row, t1, t2, eteq, yld, row_notes in t1_rows:
    evidence = ev_t1 if row != 7 else ev_t1 + [eid(4, "block23"), eid(4, "image")]
    hwe_scope_record(f"p2_table1_entry{row}", "optimization_entry", evidence, "rxn_0011", "2", "3a", "4a", "i-PrMgBr", t1, t2, eteq, yld, "isolated", row_notes, detailed=(row == 7))


# Alternative bases discussed immediately after Table 1. These are distinct
# experiments; unreported times/quantities for the poor Na/K cases stay missing.
ev_alt = [eid(2, "block7"), eid(2, "image")]
hwe_scope_record("p2_alt_base_LHMDS", "optimization_entry", ev_alt, None, "2", "3a", "4a", "LHMDS", {"number": 30, "unit": "min"}, {"number": 10, "unit": "min"}, 2, {"number": 82, "unit": "%"}, None, (("condition_relation", "only i-PrMgBr in Table 1 entry 4 was changed to LHMDS"),))
for base in ("NaHMDS", "KHMDS"):
    rid = f"p2_alt_base_{base}"
    evidence = ev_alt
    parts = [
        participant(f"{rid}_hwe", "reactant", "2", "methyl 2-[bis(benzylthio)phosphoryl]acetate", evidence),
        participant(f"{rid}_base", "reagent", None, base, evidence),
        participant(f"{rid}_product", "product", "4a", "methyl 4-phenylpenta-2,3-dienoate", evidence),
    ]
    records.append(record(
        rid, "optimization_entry", evidence, parts,
        [step("base_comparison", [f"{rid}_hwe", f"{rid}_base", f"{rid}_product"], [field("time", None, ()), field("temperature", None, ())])],
        [field("reaction_result", "reaction proceeded poorly", evidence), field("recovered_starting_material", "more than half of reagent 2", evidence), field("yield_percent", None, ())],
        source_reaction_id=None,
        unresolved=("The prose does not separately report exact quantities, times, temperature, or product yield for this base.",),
    ))


# Table 2 substrate scope.
ev_t2 = [eid(3, "block4"), eid(3, "image")]
table2 = [
    (1, "2", "3b", "4b", "i-PrMgBr", {"number": 20, "unit": "min"}, 95),
    (2, "2", "3c", "4c", "i-PrMgBr", {"number": 10, "unit": "min"}, 97),
    (3, "5", "3a", "6a", "i-PrMgBr", {"number": 10, "unit": "min"}, 93),
    (4, "5", "3b", "6b", "i-PrMgBr", {"number": 20, "unit": "min"}, 96),
    (5, "5", "3c", "6c", "n-OctMgBr", {"number": 10, "unit": "min"}, 90),
]
for row, hwe, acid, product, base, t2, yld in table2:
    notes = (("footnote_override", "n-OctMgBr used instead of i-PrMgBr"),) if row == 5 else ()
    hwe_scope_record(f"p3_table2_entry{row}", "substrate_scope_entry", ev_t2, "rxn_0012", hwe, acid, product, base, {"number": 10, "unit": "min"}, t2, 4, {"number": yld, "unit": "%"}, "isolated", notes)


# Table 3 substrate scope.
ev_t3 = [eid(3, "block8"), eid(3, "block9"), eid(3, "image")]
for row, acid, product, t2, yld in [
    (1, "3a", "8a", {"number": 1, "unit": "h"}, 95),
    (2, "3b", "8b", {"number": 3, "unit": "h"}, 82),
    (3, "3c", "8c", {"number": 1, "unit": "h"}, 89),
]:
    hwe_scope_record(f"p3_table3_entry{row}", "substrate_scope_entry", ev_t3, "rxn_0013", "7", acid, product, "n-OctMgBr", {"number": 1, "unit": "h"}, t2, 4, {"number": yld, "unit": "%"}, "isolated")


# Scheme 2 comparison reactions.
ev_s2 = [eid(3, "block13"), eid(3, "image")]
hwe_scope_record("p3_scheme2_reagent9", "substrate_scope_entry", ev_s2, "rxn_0006", "9", "3a", "4a", "i-PrMgBr", {"number": 10, "unit": "min"}, {"number": 10, "unit": "min"}, 4, {"number": 38, "unit": "%"})
hwe_scope_record("p3_scheme2_reagent10", "substrate_scope_entry", ev_s2, "rxn_0005", "10", "3a", "8a", "n-OctMgBr", {"number": 1, "unit": "h"}, {"number": 1, "unit": "h"}, 4, {"number": 82, "unit": "%"}, notes=(("observed_impurity", "small amount of n-octyl 2-phenylpropanoate was included"),))


# Scheme 3: two product examples share the displayed four-stage conversion.
ev_s3 = [eid(3, "block16"), eid(3, "image")]


def scheme3_product(product, starting_x, y, r1, yield_pct):
    rid = f"p3_scheme3_product{product}"
    parts = [
        participant(f"{rid}_start", "reactant", None, f"corresponding HWE reagent (X={starting_x}, Y={y}, R1={r1})", ev_s3),
        participant(f"{rid}_tmsbr", "reagent", None, "TMSBr", ev_s3, (("equivalents", {"number": 2.5, "unit": "equiv"}),)),
        participant(f"{rid}_pPh3", "reagent", None, "Ph3P", ev_s3, (("equivalents", {"number": 2.5, "unit": "equiv"}),)),
        participant(f"{rid}_i2", "reagent", None, "I2", ev_s3, (("equivalents", {"number": 2.5, "unit": "equiv"}),)),
        participant(f"{rid}_imidazole", "reagent", None, "imidazole", ev_s3, (("equivalents", {"number": 10, "unit": "equiv"}),)),
        participant(f"{rid}_bnsh", "reagent", None, "BnSH", ev_s3, (("equivalents", {"number": 4, "unit": "equiv"}),)),
        participant(f"{rid}_dbu", "reagent", None, "DBU", ev_s3, (("equivalents", {"number": 6, "unit": "equiv"}),)),
        participant(f"{rid}_product", "product", product, None, ev_s3),
    ]
    steps = [
        step("silylation", [f"{rid}_start", f"{rid}_tmsbr"], [field("solvent", "CH2Cl2", ev_s3), field("temperature", "room temperature", ev_s3), field("time", {"number": 1, "unit": "h"}, ev_s3)]),
        step("activation", [f"{rid}_pPh3", f"{rid}_i2"], [field("solvent", "CHCl3", ev_s3), field("temperature", "room temperature", ev_s3), field("time", {"number": 15, "unit": "min"}, ev_s3)]),
        step("imidazole_treatment", [f"{rid}_imidazole"], [field("solvent", "CHCl3", ev_s3), field("temperature", "room temperature", ev_s3), field("time", {"number": 45, "unit": "min"}, ev_s3)]),
        step("benzylthio_substitution", [f"{rid}_bnsh", f"{rid}_dbu", f"{rid}_product"], [field("solvent", "CHCl3", ev_s3), field("temperature", "room temperature", ev_s3), field("time", {"number": 5, "unit": "h"}, ev_s3)]),
    ]
    records.append(record(rid, "reported_experiment", ev_s3, parts, steps, [field("yield_percent", {"number": yield_pct, "unit": "%"}, ev_s3)], source_reaction_id="rxn_0007"))


scheme3_product("5", "Me", "H", "Bn", 79)
scheme3_product("7", "Et", "Me", "Et", 66)


# Scheme 4: six separately reported arrows/results (S/O reagent comparisons).
def scheme4_record(rid, evidence, source_id, reagent_label, product_label, grignard, t2, yield_pct, impurity=None):
    pfx = rid
    parts = [
        participant(f"{pfx}_hwe", "reactant", reagent_label, None, evidence),
        participant(f"{pfx}_acid", "reactant", "3a", "2-phenylpropionyl chloride", evidence, (("equivalents", {"number": 2, "unit": "equiv"}),)),
        participant(f"{pfx}_grignard", "reagent", None, grignard, evidence, (("equivalents", {"number": 1.1, "unit": "equiv"}),)),
        participant(f"{pfx}_et3n", "reagent", None, "Et3N", evidence, (("equivalents", {"number": 4, "unit": "equiv"}),)),
        participant(f"{pfx}_thf", "solvent", None, "THF", evidence),
        participant(f"{pfx}_product", "product", product_label, None, evidence),
    ]
    temp2 = "room temperature" if product_label == "13" else {"number": 0, "unit": "degC"}
    steps = [
        step("activation", [f"{pfx}_hwe", f"{pfx}_grignard", f"{pfx}_thf"], [field("temperature", {"number": 0, "unit": "degC"}, evidence), field("time", {"number": 1, "unit": "h"}, evidence)]),
        step("ketene_generation_and_olefination", [f"{pfx}_acid", f"{pfx}_et3n", f"{pfx}_thf", f"{pfx}_product"], [field("temperature", temp2, evidence), field("time", t2, evidence)]),
    ]
    note_fields = [] if impurity is None else [field("observed_impurity", impurity, evidence)]
    records.append(record(rid, "substrate_scope_entry", evidence, parts, steps, [field("yield_percent", {"number": yield_pct, "unit": "%"}, evidence)], note_fields, source_reaction_id=source_id))


ev_s4_top = [eid(4, "block3"), eid(4, "image"), eid(3, "block18")]
ev_s4_mid = [eid(4, "block5"), eid(4, "image"), eid(3, "block18")]
scheme4_record("p4_scheme4_reagent11", ev_s4_top, "rxn_0008", "11", "13", "n-OctMgBr", {"number": 6, "unit": "h"}, 82)
scheme4_record("p4_scheme4_reagent12", ev_s4_top, "rxn_0008", "12", "13", "n-OctMgBr", {"number": 6, "unit": "h"}, 58, "small amount of n-octyl 2-phenylpropanoate was included")
scheme4_record("p4_scheme4_reagent14", ev_s4_mid, "rxn_0009", "14", "16", "i-PrMgBr", {"number": 20, "unit": "min"}, 97)
scheme4_record("p4_scheme4_reagent15", ev_s4_mid, "rxn_0009", "15", "16", "i-PrMgBr", {"number": 20, "unit": "min"}, 28)
scheme4_record("p4_scheme4_reagent17", ev_s4_mid, "rxn_0010", "17", "19", "i-PrMgBr", {"number": 1, "unit": "h"}, 88)
scheme4_record("p4_scheme4_reagent18", ev_s4_mid, "rxn_0010", "18", "20", "i-PrMgBr", {"number": 1, "unit": "h"}, 62)


# Footnote 11 reports a separate reference preparation used to identify a
# by-product. It lacks amounts, time, temperature, workup, and yield.
ev_f11 = [eid(4, "block25"), eid(4, "image")]
records.append(record(
    "p4_footnote11_byproduct_reference", "reported_experiment", ev_f11,
    [
        participant("f11_acid", "reactant", "3a", "2-phenylpropionyl chloride", ev_f11),
        participant("f11_isopropanol", "reactant", None, "isopropanol", ev_f11),
        participant("f11_et3n", "reagent", None, "Et3N", ev_f11),
        participant("f11_product", "product", None, "isopropyl 2-phenylpropanoate", ev_f11),
    ],
    [step("reference_preparation", ["f11_acid", "f11_isopropanol", "f11_et3n", "f11_product"], [field("time", None, ()), field("temperature", None, ())])],
    [field("yield_percent", None, ()), field("identity_confirmation", "same chemical structure confirmed by comparison of the 1H NMR spectrum", ev_f11)],
    source_reaction_id=None,
    unresolved=("Amounts, solvent, time, temperature, atmosphere, workup, purification, and yield are not reported in the supplied main article.",),
))


RAW_OUT.parent.mkdir(parents=True, exist_ok=True)
RAW_OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")


ids = {r["record_id"].split(":manual:", 1)[1]: r["record_id"] for r in records}
coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1,
            "state": "attempted",
            "regions": [
                {"region": "graphical abstract, upper-middle", "finding": "Generic HWE-type allenyl-ester synthesis scope; classified as a general scheme and merged with the repeated Scheme 1c presentation, not treated as one reported experiment.", "evidence_ids": [eid(1, "block9"), eid(1, "block10"), eid(1, "image")]},
                {"region": "abstract and two-column introduction", "finding": "Background and cited prior work; no additional current-paper experiment with row-level conditions on this page.", "evidence_ids": [eid(1, "block12"), eid(1, "block18"), eid(1, "block19"), eid(1, "block20"), eid(1, "image")]},
            ],
            "record_ids": [ids["p1p2_general_allenyl_ester_scope"]],
            "unresolved": ["The graphical abstract contains generic R1/R2 structures; no single complete structure is asserted."],
        },
        {
            "page": 2,
            "state": "attempted",
            "regions": [
                {"region": "Scheme 1, top half", "finding": "Three arrows explicitly marked as previous work were recorded as literature examples; the current-work panel is a generic scope statement.", "evidence_ids": [eid(2, "block4"), eid(2, "image")]},
                {"region": "Table 1, lower-right", "finding": "Seven optimization rows recorded separately, including isolated yields and the anhydride footnote for entries 3-6.", "evidence_ids": [eid(2, "block10"), eid(2, "image")]},
                {"region": "optimization discussion, lower-left", "finding": "LHMDS result and separate poor NaHMDS/KHMDS results recorded; missing details for the poor reactions remain explicit.", "evidence_ids": [eid(2, "block7"), eid(2, "image")]},
            ],
            "record_ids": [
                ids["p1p2_general_allenyl_ester_scope"], ids["p2_scheme1a_prior_2015"], ids["p2_scheme1b_prior_E"], ids["p2_scheme1b_prior_Z"],
                *[ids[f"p2_table1_entry{i}"] for i in range(1, 8)], ids["p2_alt_base_LHMDS"], ids["p2_alt_base_NaHMDS"], ids["p2_alt_base_KHMDS"],
            ],
            "unresolved": ["NaHMDS and KHMDS comparison details beyond poor reaction and >50% recovery are not separately reported.", "Detailed procedure for Table 1 entry 7 continues in footnote 9 on page 4 and is merged into that row."],
        },
        {
            "page": 3,
            "state": "attempted",
            "regions": [
                {"region": "Table 2, upper-left", "finding": "Five substrate-scope rows recorded separately; entry 5 applies the n-OctMgBr footnote override.", "evidence_ids": [eid(3, "block4"), eid(3, "image")]},
                {"region": "Table 3, middle-left", "finding": "Three substrate-scope rows recorded separately with isolated yields.", "evidence_ids": [eid(3, "block8"), eid(3, "block9"), eid(3, "image")]},
                {"region": "Scheme 2, upper-right", "finding": "Two P-O comparison reactions recorded separately; product 8a includes the reported n-octyl ester contamination.", "evidence_ids": [eid(3, "block13"), eid(3, "image")]},
                {"region": "Scheme 3, lower-right", "finding": "Four-stage preparation sequence instantiated as separate product-5 and product-7 experiments with 79% and 66% yields.", "evidence_ids": [eid(3, "block16"), eid(3, "image")]},
            ],
            "record_ids": [
                *[ids[f"p3_table2_entry{i}"] for i in range(1, 6)], *[ids[f"p3_table3_entry{i}"] for i in range(1, 4)],
                ids["p3_scheme2_reagent9"], ids["p3_scheme2_reagent10"], ids["p3_scheme3_product5"], ids["p3_scheme3_product7"],
            ],
            "unresolved": ["No masses, concentrations, workup, purification, or characterization are supplied for these entries in the main article."],
        },
        {
            "page": 4,
            "state": "attempted",
            "regions": [
                {"region": "Scheme 4, left column", "finding": "Six current-work scope/comparison results recorded separately for reagents 11/12, 14/15, and 17/18.", "evidence_ids": [eid(4, "block3"), eid(4, "block5"), eid(4, "image")]},
                {"region": "footnote 9, right column", "finding": "Detailed 4a procedure merged with Table 1 entry 7, including quantities, staged conditions, workup, purification, product mass, appearance, and 99% isolated yield.", "evidence_ids": [eid(4, "block23"), eid(4, "image")]},
                {"region": "footnote 11, right column", "finding": "Partial reference preparation of isopropyl 2-phenylpropanoate recorded; 1H NMR comparison is reported but operational details and yield are missing.", "evidence_ids": [eid(4, "block25"), eid(4, "image")]},
                {"region": "supplementary-material notice, upper-right", "finding": "The article points to online supplementary material, but no SI file is supplied or associated in this pilot; no SI facts were inferred.", "evidence_ids": [eid(4, "block13"), eid(4, "image")]},
            ],
            "record_ids": [
                ids["p2_table1_entry7"], ids["p4_scheme4_reagent11"], ids["p4_scheme4_reagent12"], ids["p4_scheme4_reagent14"], ids["p4_scheme4_reagent15"], ids["p4_scheme4_reagent17"], ids["p4_scheme4_reagent18"], ids["p4_footnote11_byproduct_reference"],
            ],
            "unresolved": ["The referenced supplementary material is not part of the supplied dataset.", "Scheme 4 does not report masses, workup, purification, or yield basis in the main article."],
        },
    ],
}
COVERAGE_OUT.parent.mkdir(parents=True, exist_ok=True)
COVERAGE_OUT.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")
print(f"wrote {len(records)} records to {RAW_OUT}")
print(f"wrote coverage to {COVERAGE_OUT}")
