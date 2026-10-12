#!/usr/bin/env python3
"""Build evidence-linked machine records for source PDF pages 1--3."""
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
COVERAGE = OUT.parent / "coverage" / "pages_0001_0003.json"
DOC = "doc_d61e07b52776da77"
P1T, P1I = f"{DOC}:page1:text", f"{DOC}:page1:image"
P2T, P2I = f"{DOC}:page2:text", f"{DOC}:page2:image"
P3T, P3I = f"{DOC}:page3:text", f"{DOC}:page3:image"


def fact(value, evidence):
    return {
        "value": value,
        "evidence_ids": list(evidence) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def field(name, value, evidence, targets=None):
    item = {"name": name, "fact": fact(value, evidence)}
    if targets:
        item["target_entity_ids"] = targets
    return item


def participant(entity_id, role, label, name, smiles, evidence, amounts=None):
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


def record(source_id, kind, evidence, participants, steps, outcomes, notes, unresolved):
    return {
        "record_id": f"{DOC}:{source_id}",
        "document_id": DOC,
        "source_reaction_id": source_id,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": list(dict.fromkeys(evidence)),
        "participants": participants,
        "steps": steps,
        "outcomes": outcomes,
        "notes": [fact(n, evidence) for n in notes],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved,
        },
    }


records = []

# Scheme 1 is a generic transformation/mechanistic overview, not a discrete experiment.
ev = [P1T, P1I]
records.append(record(
    "scheme1_generic_lithium_shift_coupling", "general_scheme", ev,
    [
        participant("generic_enyne", "reactant", "Ar1-C#C-CH=CH2", "generic 4-aryl-3-butyn-1-ene", None, ev),
        participant("generic_rli", "reactant", "RLi", "generic organolithium", None, ev),
        participant("generic_lithium_intermediate", "unspecified_agent", "propargylic/allenylic lithium species", None, None, ev),
        participant("generic_aryl_iodide", "reactant", "Ar2I", "generic aryl iodide", None, ev),
        participant("zinc_bromide", "reagent", "ZnBr2", "zinc bromide", None, ev),
        participant("pd_pph3_4", "catalyst", "Pd(PPh3)4", "tetrakis(triphenylphosphine)palladium(0)", None, ev),
        participant("generic_product_1", "product", "1", "generic 1,1-diarylallene", None, ev),
        participant("generic_product_2", "product", "2", "generic 1,3-diarylallene", None, ev),
    ],
    [
        {"step_id": "conjugate_addition", "participant_ids": ["generic_enyne", "generic_rli", "generic_lithium_intermediate"],
         "conditions": [field("operation", "conjugate addition forming propargylic/allenylic lithium species", ev)]},
        {"step_id": "lithium_shift", "participant_ids": ["generic_lithium_intermediate"],
         "conditions": [field("operation", "depicted 1,3-lithium shift/interconversion", ev)]},
        {"step_id": "transmetalation_and_coupling", "participant_ids": ["generic_lithium_intermediate", "zinc_bromide", "generic_aryl_iodide", "pd_pph3_4", "generic_product_1", "generic_product_2"],
         "conditions": [field("operation", "ZnBr2 transmetalation followed by Pd(0)-catalyzed coupling", ev)]},
    ],
    [],
    ["Scheme 1 is a generic pathway with Ar and R variables and is not counted as a discrete reported experiment."],
    ["Generic substituents prevent fully specified structures.", "No quantities, solvent, temperature, time, yield, workup, or purification are given for the generic scheme."],
))

# Scheme 2 and the page-1 prose jointly report a temperature-screen concept.
ev = [P1T, P1I, P2T, P2I]
records.append(record(
    "scheme2_temperature_screen_unspecified_t1", "optimization_entry", ev,
    [
        participant("enyne_ph", "reactant", "4-phenyl-3-butyn-1-ene", "4-phenyl-3-butyn-1-ene", "C=CC#Cc1ccccc1", [P1I, P2I]),
        participant("n_buli", "reactant", "n-BuLi", "n-butyllithium", None, ev),
        participant("zinc_bromide", "reagent", "ZnBr2", "zinc bromide", None, [P2I]),
        participant("iodobenzene", "reactant", "PhI", "iodobenzene", "Ic1ccccc1", [P2I]),
        participant("pd_pph3_4", "catalyst", "Pd(PPh3)4", "tetrakis(triphenylphosphine)palladium(0)", None, [P2I]),
        participant("product_1a", "product", "1a", "1,1-diphenylocta-1,2-diene", "CCCCCC=C=C(c1ccccc1)c1ccccc1", [P1I, P2I]),
        participant("product_2a", "product", "2a", "1,3-diphenylocta-1,2-diene", "CCCCCC(=C=Cc1ccccc1)c1ccccc1", [P1I, P2I]),
    ],
    [
        {"step_id": "carbolithiation", "participant_ids": ["enyne_ph", "n_buli"], "conditions": [
            field("temperature", None, []), field("time", {"number": 1, "unit": "h", "raw_text": "1 h"}, [P2I])]},
        {"step_id": "transmetalation", "participant_ids": ["zinc_bromide"], "conditions": [
            field("operation", "warm from the unspecified T1 to r.t.", [P2I]),
            field("time", {"number": 20, "unit": "min", "raw_text": "20 min"}, [P2I])]},
        {"step_id": "coupling", "participant_ids": ["iodobenzene", "pd_pph3_4", "product_1a", "product_2a"], "conditions": [
            field("temperature", "r.t.", [P2I]), field("time", None, [])]},
    ],
    [
        field("reported_observation", "lower carbolithiation temperature favors 1a; higher carbolithiation temperature favors 2a", [P1T, P1I], ["product_1a", "product_2a"]),
        field("reported_yield_trend", "yields were lower when the reactions were carried out at higher temperature", [P1T, P1I], ["product_1a", "product_2a"]),
    ],
    ["Scheme 2 represents a temperature-variable screening concept rather than a row with a specified T1 value."],
    ["The numerical T1 temperatures, individual product ratios, and yields are not supplied.", "Reactant quantities, solvent, atmosphere, workup, purification, and yield basis are not reported."],
))

# Prose-only additive screen. Each named additive is retained as a separate row.
for key, label, name in [
    ("pyridine", "pyridine", "pyridine"),
    ("tetrabutylammonium_iodide", "n-Bu4NI", "tetrabutylammonium iodide"),
    ("diisopropylethylamine", "N,N-diisopropylethylamine", "N,N-diisopropylethylamine"),
    ("dmap", "DMAP", "4-(dimethylamino)pyridine"),
]:
    ev = [P2T, P2I]
    records.append(record(
        f"additive_screen_{key}", "optimization_entry", ev,
        [participant("additive", "reagent", label, name, None, ev)],
        [{"step_id": "additive_test", "participant_ids": ["additive"], "conditions": [
            field("operation", "tested as an additive for the 1,3-lithium shift reaction", ev),
            field("temperature", None, []), field("time", None, [])]}],
        [field("effect_on_1_3_lithium_shift", "little effect", ev)],
        ["The source groups this additive with other additives reported to have little effect."],
        ["Exact substrate/reagent combination, additive quantity, solvent, temperature, time, product distribution, and yield are not reported for this individual test."],
    ))

ev = [P2T, P2I]
records.append(record(
    "additive_screen_tmeda", "optimization_entry", ev,
    [participant("additive", "reagent", "TMEDA", "N,N,N',N'-tetramethylethylenediamine", None, ev)],
    [{"step_id": "additive_test", "participant_ids": ["additive"], "conditions": [
        field("operation", "tested as an additive for the 1,3-lithium shift reaction", ev),
        field("temperature", None, []), field("time", None, [])]}],
    [field("effect_on_1_3_lithium_shift", "some interesting effect", ev), field("reproducibility", "not easily reproducible", ev)],
    ["The source reports an effect but does not quantify it and explicitly states that the reaction was not easily reproducible."],
    ["Exact substrate/reagent combination, additive quantity, solvent, temperature, time, product distribution, and yield are not reported for this test."],
))


product_smiles = {
    ("a", "A"): "CCCCCC=C=C(c1ccccc1)c1ccccc1",
    ("a", "B"): "CCCCCC(=C=Cc1ccccc1)c1ccccc1",
    ("b", "A"): "CC(C)(C)CC=C=C(c1ccccc1)c1ccccc1",
    ("b", "B"): "CC(C)(C)CC(=C=Cc1ccccc1)c1ccccc1",
    ("c", "A"): "CC(C)(C)CC=C=C(c1ccccc1)c1ccc(OC)cc1",
    ("c", "B"): "CC(C)(C)CC(=C=Cc1ccccc1)c1ccc(OC)cc1",
    ("d", "A"): "CC(C)(C)CC=C=C(c1ccccc1)c1ccc(C#N)cc1",
    ("d", "B"): "CC(C)(C)CC(=C=Cc1ccccc1)c1ccc(C#N)cc1",
    ("e", "A"): "CCC(C)CC=C=C(c1ccccc1)c1ccccc1",
    ("e", "B"): "CCC(C)CC(=C=Cc1ccccc1)c1ccccc1",
    ("f", "A"): "CCCCCC=C=C(c1ccccc1)c1ccc(C)cc1",
    ("f", "B"): "CCCCCC(=C=Cc1ccc(C)cc1)c1ccccc1",
}

rows = [
    (1, "Ph", "n-Bu", "Ph", "A", 81, "a"),
    (2, "Ph", "n-Bu", "Ph", "B", 83, "a"),
    (3, "Ph", "t-Bu", "Ph", "A", 89, "b"),
    (4, "Ph", "t-Bu", "Ph", "B", 88, "b"),
    (5, "Ph", "t-Bu", "p-MeOC6H4", "A", 95, "c"),
    (6, "Ph", "t-Bu", "p-MeOC6H4", "B", 66, "c"),
    (7, "Ph", "t-Bu", "p-CNC6H4", "A", 98, "d"),
    (8, "Ph", "t-Bu", "p-CNC6H4", "B", 67, "d"),
    (9, "Ph", "s-Bu", "Ph", "A", 88, "e"),
    (10, "Ph", "s-Bu", "Ph", "B", 76, "e"),
    (11, "p-MeC6H4", "n-Bu", "Ph", "A", 70, "f"),
    (12, "p-MeC6H4", "n-Bu", "Ph", "B", 52, "f"),
]


def start_smiles(ar1):
    return "C=CC#Cc1ccccc1" if ar1 == "Ph" else "C=CC#Cc1ccc(C)cc1"


def aryl_iodide_smiles(ar2):
    return {"Ph": "Ic1ccccc1", "p-MeOC6H4": "COc1ccc(I)cc1", "p-CNC6H4": "N#Cc1ccc(I)cc1"}[ar2]


for entry, ar1, r_group, ar2, condition, yield_value, series in rows:
    ev = [P2T, P2I]
    major_label = f"{1 if condition == 'A' else 2}{series}"
    minor_label = f"{2 if condition == 'A' else 1}{series}"
    ratio = "100:0" if condition == "A" else "0:100"
    parts = [
        participant("enyne", "reactant", f"4-{ar1}-3-butyn-1-ene", None, start_smiles(ar1), ev),
        participant("organolithium", "reactant", f"{r_group}Li", None, None, ev),
        participant("aryl_iodide", "reactant", f"Ar2I (Ar2={ar2})", None, aryl_iodide_smiles(ar2), ev),
        participant("zinc_bromide", "reagent", "ZnBr2", "zinc bromide", None, ev),
        participant("pd_pph3_4", "catalyst", "Pd(PPh3)4", "tetrakis(triphenylphosphine)palladium(0)", None, ev),
        participant("major_product", "product", major_label,
                    "1,1-diphenylocta-1,2-diene" if major_label == "1a" else ("1,3-diphenylocta-1,2-diene" if major_label == "2a" else None),
                    product_smiles[(series, condition)], ev),
    ]
    steps = [{
        "step_id": "carbolithiation", "participant_ids": ["enyne", "organolithium"],
        "conditions": [field("temperature", {"number": -78, "unit": "°C", "raw_text": "-78 °C"}, ev),
                       field("time", {"number": 1, "unit": "h", "raw_text": "1 h"}, ev)],
    }]
    if condition == "A":
        steps.append({
            "step_id": "transmetalation_and_coupling",
            "participant_ids": ["zinc_bromide", "aryl_iodide", "pd_pph3_4", "major_product"],
            "conditions": [field("operation", "transmetalation followed by Pd(0)-catalyzed coupling", ev),
                           field("temperature", "r.t.", ev), field("time", None, [])],
        })
    else:
        hmpa_equiv = 3 if entry in (6, 8) else 2
        parts.append(participant(
            "hmpa", "reagent", "HMPA", "hexamethylphosphoramide", None, ev,
            [field("equivalents", {"number": hmpa_equiv, "unit": "equiv", "raw_text": f"{hmpa_equiv} equiv"}, ev)],
        ))
        steps.extend([
            {"step_id": "hmpa_addition", "participant_ids": ["hmpa"], "conditions": [
                field("operation", "HMPA addition", ev),
                field("temperature", {"number": -78, "unit": "°C", "raw_text": "-78 °C"}, ev), field("time", None, [])]},
            {"step_id": "natural_warming", "participant_ids": [], "conditions": [
                field("operation", "warmed naturally to room temperature", ev), field("temperature", "r.t.", ev), field("time", None, [])]},
            {"step_id": "transmetalation_and_coupling", "participant_ids": ["zinc_bromide", "aryl_iodide", "pd_pph3_4", "major_product"], "conditions": [
                field("operation", "subsequent transmetalation and Pd(0)-catalyzed coupling", ev),
                field("temperature", "r.t.", ev), field("time", None, [])]},
        ])
    notes = [
        f"Table 1 entry {entry}: Ar1={ar1}, R={r_group}, Ar2={ar2}, Conditions {condition}.",
        f"The table reports {major_label}:{minor_label} = {ratio}; the minor regioisomer is not represented as a formed product participant.",
    ]
    if entry == 2:
        notes.append("The accompanying prose identifies this entry as exclusive formation of 2a and a complete 1,3-lithium shift.")
    records.append(record(
        f"table1_entry_{entry:02d}", "substrate_scope_entry", ev, parts, steps,
        [
            field("isolated_yield", {"number": yield_value, "unit": "%", "raw_text": f"{yield_value}%"}, ev, ["major_product"]),
            field("yield_measurement_basis", "isolated yield based on aryl halide", ev, ["major_product"]),
            field("product_ratio", {"components": [f"1{series}", f"2{series}"], "values": [100, 0] if condition == "A" else [0, 100], "raw_text": f"1{series}:2{series} = {ratio}"}, ev, ["major_product"]),
        ],
        notes,
        ["Reactant quantities other than HMPA, solvent, atmosphere, workup, purification, and coupling time are not reported in the supplied main text.",
         "Candidate structures derived from the scheme/table substituent mapping remain unverified.",
         "Supporting-information association is unestablished."],
    ))


# Scheme 3 contains two distinct experiments on the 2-methyl substrate.
def scheme3_record(condition, yield_value):
    ev = [P2T, P2I, P3T, P3I]
    parts = [
        participant("enyne_2methyl", "reactant", "4-phenyl-2-methyl-3-butyn-1-ene", "4-phenyl-2-methyl-3-butyn-1-ene", "C=C(C)C#Cc1ccccc1", [P3T, P3I]),
        participant("t_buli", "reactant", "t-BuLi", "tert-butyllithium", None, [P3I]),
        participant("zinc_bromide", "reagent", "ZnBr2", "zinc bromide", None, [P3I]),
        participant("iodobenzene", "reactant", "PhI", "iodobenzene", "Ic1ccccc1", [P3I]),
        participant("pd_pph3_4", "catalyst", "Pd(PPh3)4", "tetrakis(triphenylphosphine)palladium(0)", None, [P3I]),
        participant("product_3a", "product", "3a", "1,1-diphenylallene 3a", "CC(C)(C)CC(C)=C=C(c1ccccc1)c1ccccc1", [P3T, P3I]),
    ]
    steps = [{
        "step_id": "carbolithiation", "participant_ids": ["enyne_2methyl", "t_buli"], "conditions": [
            field("temperature", {"number": -78, "unit": "°C", "raw_text": "-78 °C"}, [P3I]),
            field("time", {"number": 1, "unit": "h", "raw_text": "1 h"}, [P3I])],
    }]
    if condition == "A":
        steps.extend([
            {"step_id": "transmetalation", "participant_ids": ["zinc_bromide"], "conditions": [
                field("operation", "warmed from -78 °C to r.t.", [P3I]),
                field("starting_temperature", {"number": -78, "unit": "°C", "raw_text": "-78 °C"}, [P3I]),
                field("final_temperature", "r.t.", [P3I]),
                field("time", {"number": 20, "unit": "min", "raw_text": "20 min"}, [P3I])]},
            {"step_id": "coupling", "participant_ids": ["iodobenzene", "pd_pph3_4", "product_3a"], "conditions": [
                field("temperature", "r.t.", [P2T, P2I]), field("time", None, [])]},
        ])
    else:
        parts.append(participant(
            "hmpa", "reagent", "HMPA", "hexamethylphosphoramide", None, [P3I],
            [field("equivalents", {"number": 2, "unit": "equiv", "raw_text": "2 equiv"}, [P3I])],
        ))
        steps.extend([
            {"step_id": "hmpa_shift_stage", "participant_ids": ["hmpa"], "conditions": [
                field("operation", "HMPA addition followed by warming from -78 °C to r.t.", [P3I]),
                field("starting_temperature", {"number": -78, "unit": "°C", "raw_text": "-78 °C"}, [P3I]),
                field("final_temperature", "r.t.", [P3I]),
                field("time", {"number": 1, "unit": "h", "raw_text": "1 h"}, [P3I])]},
            {"step_id": "transmetalation", "participant_ids": ["zinc_bromide"], "conditions": [
                field("temperature", "r.t.", [P3I]), field("time", {"number": 20, "unit": "min", "raw_text": "20 min"}, [P3I])]},
            {"step_id": "coupling", "participant_ids": ["iodobenzene", "pd_pph3_4", "product_3a"], "conditions": [
                field("temperature", None, []), field("time", None, [])]},
        ])
    return record(
        f"scheme3_condition_{condition.lower()}", "reported_experiment", ev, parts, steps,
        [field("reported_yield", {"number": yield_value, "unit": "%", "raw_text": f"{yield_value}%"}, [P3I], ["product_3a"]),
         field("yield_measurement_basis", None, [], ["product_3a"])],
        [f"Scheme 3, Conditions {condition}, affords only the 1,1-diphenylallene 3a according to the accompanying prose."],
        ["Yield measurement basis is not stated.", "Reactant quantities other than HMPA, solvent, atmosphere, workup, purification, and final coupling duration are not reported.",
         "Candidate structures remain unverified.", "Supporting-information association is unestablished."],
    )


records.extend([scheme3_record("A", 68), scheme3_record("B", 50)])


record_ids = [r["record_id"] for r in records]
table_ids = [f"{DOC}:table1_entry_{i:02d}" for i in range(1, 13)]
additive_ids = [
    f"{DOC}:additive_screen_pyridine",
    f"{DOC}:additive_screen_tetrabutylammonium_iodide",
    f"{DOC}:additive_screen_diisopropylethylamine",
    f"{DOC}:additive_screen_dmap",
    f"{DOC}:additive_screen_tmeda",
]
coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1,
            "state": "attempted",
            "regions": [
                {"region": "title, abstract, and introductory left column", "finding": "Article metadata and background; cited prior work is contextual and does not provide a separable current-paper experiment.", "evidence_ids": [P1I, P1T]},
                {"region": "right-column temperature-effect paragraph", "finding": "Reports the qualitative lower-T1 versus higher-T1 regioselectivity screen; merged with Scheme 2 as one partial optimization record.", "evidence_ids": [P1I, P1T]},
                {"region": "Scheme 1 at bottom", "finding": "Generic conjugate-addition/1,3-lithium-shift/transmetalation-coupling pathway with Ar/R variables; classified as general_scheme, not a discrete experiment.", "evidence_ids": [P1I, P1T]},
            ],
            "record_ids": [f"{DOC}:scheme1_generic_lithium_shift_coupling", f"{DOC}:scheme2_temperature_screen_unspecified_t1"],
            "unresolved": ["Scheme 1 uses generic substituents and gives no discrete conditions or yield.", "Numerical T1 values, ratios, and yields for the initial temperature screen are absent."],
        },
        {
            "page": 2,
            "state": "attempted",
            "regions": [
                {"region": "Scheme 2 at upper left", "finding": "Temperature-variable experiment leading to 1a and 2a; exact T1 is not specified, so the record remains partial.", "evidence_ids": [P2I, P2T]},
                {"region": "additive-screen prose below Scheme 2", "finding": "Five named additives were treated as five separate optimization entries; four had little effect and TMEDA was not easily reproducible.", "evidence_ids": [P2I, P2T]},
                {"region": "HMPA conditions prose at upper right", "finding": "Specific HMPA experiment gives exclusive 2a in 83%; merged with Table 1 entry 2 rather than duplicated.", "evidence_ids": [P2I, P2T]},
                {"region": "Table 1 reaction arrows and rows 1-12", "finding": "Twelve independent substrate/condition rows extracted with Ar1, R, Ar2, A/B condition, isolated yield, and product ratio.", "evidence_ids": [P2I, P2T]},
                {"region": "Table 1 footnotes a-c", "finding": "Isolated-yield basis, 3-equiv HMPA overrides for entries 6 and 8, and the A/B step conditions were applied to their own rows.", "evidence_ids": [P2I, P2T]},
            ],
            "record_ids": [f"{DOC}:scheme2_temperature_screen_unspecified_t1", *additive_ids, *table_ids],
            "unresolved": ["Individual additive-test conditions and outcomes are not quantified.", "Most reactant amounts, solvent, atmosphere, workup, purification, and coupling times are absent.", "Candidate structures remain machine-interpreted and unverified."],
        },
        {
            "page": 3,
            "state": "attempted",
            "regions": [
                {"region": "Scheme 3 first arrow sequence", "finding": "Conditions A experiment on 4-phenyl-2-methyl-3-butyn-1-ene affords 3a in 68%; extracted independently.", "evidence_ids": [P3I, P3T]},
                {"region": "Scheme 3 second arrow sequence", "finding": "Conditions B/HMPA experiment on the same substrate affords 3a in 50%; extracted independently with HMPA amount and staged timing.", "evidence_ids": [P3I, P3T]},
                {"region": "Scheme 3 explanatory paragraph", "finding": "States that both conditions afford only 1,1-diphenylallene 3a and interprets the missing 2-position proton as important for lithium shift.", "evidence_ids": [P3I, P3T]},
                {"region": "conclusion, acknowledgments, and references", "finding": "No additional current-paper experimental arrows or table rows; references are prior literature and were not recast as this paper's experiments.", "evidence_ids": [P3I, P3T]},
            ],
            "record_ids": [f"{DOC}:scheme3_condition_a", f"{DOC}:scheme3_condition_b"],
            "unresolved": ["Scheme 3 yield basis is not stated.", "Final coupling time and most reagent quantities, solvent, atmosphere, workup, and purification are absent.", "Candidate structures remain unverified."],
        },
    ],
}

assert len(records) == 21
assert set(record_ids) == {rid for p in coverage["pages"] for rid in p["record_ids"]}
OUT.mkdir(parents=True, exist_ok=True)
COVERAGE.parent.mkdir(parents=True, exist_ok=True)
(OUT / "extracted_records_pages_0001_0003.json").write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
COVERAGE.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"records": len(records), "coverage_pages": [p["page"] for p in coverage["pages"]]}, ensure_ascii=False))
