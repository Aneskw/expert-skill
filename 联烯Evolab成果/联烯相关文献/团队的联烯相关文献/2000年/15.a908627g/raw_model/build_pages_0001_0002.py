#!/usr/bin/env python3
"""Build evidence-linked records for a908627g PDF pages 1-2."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / "runs" / "current"
DOC = "doc_bae1fe204ad24bde"
P1T = f"{DOC}:page1:text"
P1I = f"{DOC}:page1:image"
P2T = f"{DOC}:page2:text"
P2I = f"{DOC}:page2:image"


def fact(value, evidence=()):
    return {
        "value": value,
        "evidence_ids": list(evidence) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def field(name, value, evidence=()):
    return {"name": name, "fact": fact(value, evidence)}


def participant(entity_id, role, label, name, evidence, amounts=()):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence),
        "smiles": fact(None),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": list(amounts),
    }


def record(suffix, source_id, kind, evidence, participants, steps, outcomes, notes, unresolved):
    return {
        "record_id": f"{DOC}:{suffix}",
        "document_id": DOC,
        "source_reaction_id": source_id,
        "record_kind": kind,
        "status": "needs_review",
        "completeness": "partial",
        "evidence_ids": list(dict.fromkeys(evidence)),
        "participants": participants,
        "steps": steps,
        "outcomes": outcomes,
        "notes": notes,
        "review": {
            "method": "model",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved,
        },
    }


records = []

# Scheme 1 is a conceptual transformation/proposed Pd pathway, not an individual run.
scheme1_ev = [P1I, P1T]
scheme1_parts = [
    participant("s1_halide", "reactant", "R3X", "organic halide", scheme1_ev),
    participant("s1_ketone", "reactant", "2", "generic 1,2-dienyl ketone", scheme1_ev),
    participant("s1_product", "product", "3", "generic polysubstituted furan", scheme1_ev),
]
records.append(record(
    "scheme1_general_concept", "Scheme 1", "general_scheme", scheme1_ev,
    scheme1_parts,
    [{
        "step_id": "conceptual_cyclization",
        "participant_ids": [p["entity_id"] for p in scheme1_parts],
        "conditions": [
            field("operating_conditions", None),
            field("depicted_intermediate", "generic organopalladium intermediate", scheme1_ev),
        ],
    }],
    [field("transformation", "organic halide plus 1,2-dienyl ketone to polysubstituted furan", scheme1_ev)],
    [
        fact("Scheme 1 is presented as the authors' generic design/concept and contains R-group variables; it is not an individual experimental run.", scheme1_ev),
        fact("The depicted organopalladium species is proposed and is not reported as an observed intermediate.", scheme1_ev),
    ],
    ["Generic R1-R4 groups are not resolved into specific structures.", "No quantities, temperature, time, yield, or workup are reported for this conceptual scheme."],
))


def optimization_record(suffix, source_id, temperature, base_equiv, include_silver, yield_3a, yield_4a, evidence):
    ev = list(evidence)
    parts = [
        participant("ph_i", "reactant", "PhI", "iodobenzene", ev),
        participant("ketone_2a", "reactant", "2a", "heptadeca-3,4-dien-2-one", ev),
        participant("product_3a", "product", "3a", "furan product 3a", ev),
        participant("product_4a", "product", "4a", "furan by-product 4a", ev),
        participant("pd_pph3_4", "catalyst", "Pd(PPh3)4", "tetrakis(triphenylphosphine)palladium(0)", ev,
                    [field("loading", {"number": 5, "unit": "mol%"}, ev)]),
        participant("et3n", "reagent", "NEt3", "triethylamine", ev,
                    [field("amount", {"number": base_equiv, "unit": "equiv"}, ev)]),
        participant("phme", "solvent", "PhMe", "toluene", ev),
    ]
    if include_silver:
        parts.append(participant("ag2co3", "reagent", "Ag2CO3", "silver carbonate", ev,
                                 [field("loading", {"number": 10, "unit": "mol%"}, ev)]))
    conditions = [
        field("temperature", {"number": temperature, "unit": "°C"}, ev),
        field("time", {"number": 12, "unit": "h"}, ev),
        field("reaction_scale", None),
        field("solvent_volume", None),
        field("concentration", None),
        field("atmosphere", None),
        field("workup", None),
        field("purification", None),
    ]
    if not include_silver:
        conditions.append(field("Ag2CO3_present", False, ev))
    outcomes = [
        field("3a_yield", {"number": yield_3a, "unit": "%"}, ev),
        field("4a_yield", {"number": yield_4a, "unit": "%"}, ev),
        field("yield_measurement_basis", "NMR yield", ev),
        field("isolated_mass", None),
    ]
    notes = [fact("Scheme 2 condition row; both 3a and 4a outcomes belong to the same reaction run.", ev)]
    if include_silver:
        notes.append(fact("The page-2 prose repeats this optimized 88%/9% experiment and states that catalytic Ag2CO3 is crucial.", [P2I, P2T]))
    return record(
        suffix, source_id, "optimization_entry", ev, parts,
        [{"step_id": "pd_catalyzed_cyclization", "participant_ids": [p["entity_id"] for p in parts], "conditions": conditions}],
        outcomes, notes,
        ["Exact PhI and ketone charge/ratio is not printed for this Scheme 2 row.", "Reaction scale, solvent volume, concentration, atmosphere, workup, purification, isolated mass, and NMR internal standard are not reported."],
    )


records.append(optimization_record(
    "scheme2_row1_no_silver", "Scheme 2 row 1", 100, 1.5, False, 53, 42, [P1I, P1T]
))
records.append(optimization_record(
    "scheme2_row2_standard_conditions", "Scheme 2 row 2", 80, 2.0, True, 88, 9, [P1I, P1T, P2I, P2T]
))


# Scheme 3 records the generic standard transformation and halide legend.
scheme3_ev = [P1I, P1T, P2I, P2T]
scheme3_parts = [
    participant("s3_halide", "reactant", "1 (R3X)", "aryl or alk-1-enyl halide", scheme3_ev,
                [field("default_amount", {"number": 1.0, "unit": "equiv"}, scheme3_ev)]),
    participant("s3_ketone", "reactant", "2", "1,2-dienyl ketone", scheme3_ev,
                [field("default_amount", {"number": 1.5, "unit": "equiv"}, scheme3_ev)]),
    participant("s3_product", "product", "3", "polysubstituted furan", scheme3_ev),
    participant("s3_pd", "catalyst", "Pd(PPh3)4", "tetrakis(triphenylphosphine)palladium(0)", scheme3_ev,
                [field("loading", {"number": 5, "unit": "mol%"}, scheme3_ev)]),
    participant("s3_et3n", "reagent", "Et3N", "triethylamine", scheme3_ev,
                [field("standard_amount_from_preceding_conditions", {"number": 2.0, "unit": "equiv"}, [P2I, P2T])]),
    participant("s3_ag2co3", "reagent", "Ag2CO3", "silver carbonate", scheme3_ev,
                [field("loading", {"number": 10, "unit": "mol%"}, scheme3_ev)]),
    participant("s3_phme", "solvent", "PhMe", "toluene", scheme3_ev),
]
records.append(record(
    "scheme3_general_standard_conditions", "Scheme 3", "general_scheme", scheme3_ev,
    scheme3_parts,
    [{
        "step_id": "generic_standard_cyclization",
        "participant_ids": [p["entity_id"] for p in scheme3_parts],
        "conditions": [field("temperature", None), field("time", None), field("reaction_scale", None)],
    }],
    [field("product_class", "polysubstituted furans", scheme3_ev), field("yield", None)],
    [
        fact("Scheme 3 is the generic standard transformation instantiated by the individual Table 1 rows; it is not an additional run.", scheme3_ev),
        fact("R3X legend: PhI (1a), p-nitrophenyl iodide (1b), p-methoxycarbonylphenyl iodide (1c), 5-bromopyrimidine (1d), methyl (Z)-3-iodopropenoate (1e), and p-methoxyphenyl iodide (1f).", [P1I, P1T]),
    ],
    ["Generic R1-R4 groups are unresolved.", "Scheme 3 does not give one temperature, time, or yield; these vary by Table 1 row.", "Exact reaction scale, solvent volume, concentration, atmosphere, workup, and purification are not reported."],
))


halide_names = {
    "1a": "iodobenzene",
    "1b": "p-nitrophenyl iodide",
    "1c": "p-methoxycarbonylphenyl iodide",
    "1d": "5-bromopyrimidine",
    "1e": "methyl (Z)-3-iodopropenoate",
    "1f": "p-methoxyphenyl iodide",
}

table_rows = [
    (1, "1a", 2.0, "2a", "H", "H", "C12H25", 80, 12, "3a", 75),
    (2, "1b", 2.0, "2a", "H", "H", "C12H25", 80, 13, "3b", 90),
    (3, "1c", 1.0, "2a", "H", "H", "C12H25", 80, 14, "3c", 94),
    (4, "1a", 1.0, "2b", "H", "H", "Bu", 80, 12, "3d", 73),
    (5, "1b", 1.0, "2b", "H", "H", "Bu", 80, 9, "3e", 92),
    (6, "1c", 1.0, "2b", "H", "H", "Bu", 80, 9, "3f", 85),
    (7, "1d", 1.0, "2b", "H", "H", "Bu", 80, 11, "3g", 71),
    (8, "1e", 1.0, "2b", "H", "H", "Bu", 80, 11, "3h", 61),
    (9, "1c", 1.0, "2c", "H", "Me", "H", 100, 14, "3i", 68),
    (10, "1b", 1.0, "2c", "H", "Me", "H", 100, 11, "3j", 79),
    (11, "1d", 1.0, "2d", "H", "Bu", "H", 100, 17, "3k", 97),
    (12, "1b", 1.0, "2e", "H", "H", "Ph", 80, 10, "3l", 51),
    (13, "1c", 1.0, "2e", "H", "H", "Ph", 80, 10, "3m", 51),
    (14, "1b", 1.0, "2f", "Et", "H", "Ph", 80, 12, "3n", 77),
    (15, "1c", 1.0, "2f", "Et", "H", "Ph", 80, 12, "3o", 73),
    (16, "1f", 1.0, "2b", "H", "H", "Bu", 80, 11, "3p", 66),
    (17, "1f", 1.0, "2g", "H", "H", "C7H15", 80, 11, "3q", 63),
]


def table_record(row):
    entry, halide, halide_equiv, ketone, r1, r2, r4, temperature, hours, product, yield_pct = row
    ev = [P1I, P1T, P2I, P2T]
    ketone_name = "heptadeca-3,4-dien-2-one" if ketone == "2a" else f"1,2-dienyl ketone {ketone}"
    parts = [
        participant(f"halide_{halide}", "reactant", halide, halide_names[halide], [P1I, P1T],
                    [field("amount", {"number": halide_equiv, "unit": "equiv"}, [P1I, P1T])]),
        participant(f"ketone_{ketone}", "reactant", ketone, ketone_name, ev,
                    [field("amount", {"number": 1.5, "unit": "equiv"}, [P1I, P1T])]),
        participant(f"product_{product}", "product", product, f"polysubstituted furan {product}", [P1I, P1T]),
        participant("pd_pph3_4", "catalyst", "Pd(PPh3)4", "tetrakis(triphenylphosphine)palladium(0)", [P1I, P1T],
                    [field("loading", {"number": 5, "unit": "mol%"}, [P1I, P1T])]),
        participant("et3n", "reagent", "Et3N", "triethylamine", ev,
                    [field("amount", {"number": 2.0, "unit": "equiv"}, [P2I, P2T])]),
        participant("ag2co3", "reagent", "Ag2CO3", "silver carbonate", ev,
                    [field("loading", {"number": 10, "unit": "mol%"}, ev)]),
        participant("phme", "solvent", "PhMe", "toluene", ev),
    ]
    conditions = [
        field("temperature", {"number": temperature, "unit": "°C"}, [P1I, P1T]),
        field("time", {"number": hours, "unit": "h"}, [P1I, P1T]),
        field("ketone_R1", r1, [P1I, P1T]),
        field("ketone_R2", r2, [P1I, P1T]),
        field("ketone_R4", r4, [P1I, P1T]),
        field("reaction_scale", None),
        field("solvent_volume", None),
        field("concentration", None),
        field("atmosphere", None),
        field("workup", None),
        field("purification", None),
    ]
    outcomes = [
        field("isolated_yield", {"number": yield_pct, "unit": "%"}, [P1I, P1T]),
        field("yield_measurement_basis", "isolated yield", [P1I, P1T]),
        field("isolated_mass", None),
        field("selectivity", None),
    ]
    notes = [
        fact(f"Table 1 entry {entry}: {halide} + {ketone} gave {product}; ketone substituents R1={r1}, R2={r2}, R4={r4}.", [P1I, P1T]),
        fact("The Et3N/Ag2CO3 conditions are linked through Scheme 3 and the page-2 statement that Table 1 uses the standard conditions.", ev),
    ]
    if entry == 8:
        notes.append(fact("Table footnote d states that the C=C configuration in R3 is trans.", [P1I, P1T]))
    return record(
        f"table1_entry_{entry:02d}", f"Table 1 entry {entry}", "substrate_scope_entry", ev,
        parts,
        [{"step_id": "pd_catalyzed_cyclization", "participant_ids": [p["entity_id"] for p in parts], "conditions": conditions}],
        outcomes, notes,
        ["Exact structures of the drawn ketone and furan are not machine-certified; SMILES are intentionally null.", "Reaction scale, solvent volume, concentration, atmosphere, workup, purification, isolated mass, and any selectivity value are not reported in the supplied main text.", "No SI is supplied or explicitly associated; missing experimental details were not inferred."],
    )


records.extend(table_record(row) for row in table_rows)

raw_path = RUN / "raw_model" / "records_pages_0001_0002.json"
raw_path.parent.mkdir(parents=True, exist_ok=True)
raw_path.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")

all_ids = [r["record_id"] for r in records]
table_ids = [f"{DOC}:table1_entry_{i:02d}" for i in range(1, 18)]
coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1,
            "state": "attempted",
            "regions": [
                {"region": "page 1 title, abstract, and two-column introduction", "finding": "Current-paper reaction class and background were reviewed. The cited Rh+/Ag+ one-component cyclizations and other introductory methods are prior literature without locally reported individual procedures, so no current experiment was fabricated from them.", "evidence_ids": [P1T, P1I]},
                {"region": "page 1 lower-left Scheme 1", "finding": "Generic conceptual transformation with a proposed organopalladium intermediate; classified as a general scheme, not an observed experiment or isolated mechanism intermediate.", "evidence_ids": [P1I]},
                {"region": "page 1 center-right Scheme 2", "finding": "Two separate condition-screening runs were read: no-Ag2CO3 NEt3/100 °C gives 3a/4a at 53%/42% NMR yield; Ag2CO3/NEt3/80 °C gives 88%/9% NMR yield.", "evidence_ids": [P1I]},
                {"region": "page 1 right-middle Scheme 3 and R3X legend", "finding": "Generic standard-condition transformation and identities of halides 1a-1f; retained as a general scheme instantiated by Table 1 rows.", "evidence_ids": [P1I]},
                {"region": "page 1 bottom Table 1 and footnotes a-d", "finding": "All 17 substrate-scope rows were read individually, including row-specific halide/ketone labels, R1/R2/R4, temperature, time, isolated yield, 2.0-equivalent overrides for entries 1-2, and the entry-8 trans footnote.", "evidence_ids": [P1I]},
            ],
            "record_ids": all_ids,
            "unresolved": ["Drawn exact structures for ketones 2b-2g and products 3a-3q are not certified; SMILES remain null.", "No reaction scale, solvent volume, concentration, atmosphere, workup, purification, or isolated masses are reported on page 1."],
        },
        {
            "page": 2,
            "state": "attempted",
            "regions": [
                {"region": "page 2 upper-left continuation and optimized-condition paragraph", "finding": "The 88% 3a/9% 4a optimized Scheme-2 run is repeated with Pd(PPh3)4 (5 mol%), toluene, Et3N (2 equiv), Ag2CO3 (10 mol%), and the statement that catalytic Ag2CO3 is crucial; merged with the existing Scheme-2 row rather than duplicated.", "evidence_ids": [P2T, P2I]},
                {"region": "page 2 upper-left Table 1 discussion", "finding": "The prose confirms use of the standard conditions, a 51-97% yield range, aryl-halide electronic scope, substitution diversity, and the entry-8 methyl (Z)-3-iodopropenoate result; linked to the 17 Table-1 records.", "evidence_ids": [P2T, P2I]},
                {"region": "page 2 lower-left conclusion and page 2 right-column references", "finding": "Conclusion and bibliography only; cited literature was not converted into current-paper experiments, and no additional current experimental procedure is printed.", "evidence_ids": [P2T, P2I]},
            ],
            "record_ids": [f"{DOC}:scheme2_row2_standard_conditions", f"{DOC}:scheme3_general_standard_conditions"] + table_ids,
            "unresolved": ["The supplied two-page article contains no detailed experimental procedure or explicitly associated SI.", "NMR internal standard for Scheme 2, exact run scale, and Table-1 workup/purification details are not reported."],
        },
    ],
}
coverage_path = RUN / "coverage" / "pages_0001_0002.json"
coverage_path.parent.mkdir(parents=True, exist_ok=True)
coverage_path.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

tasks_path = RUN / "tasks.json"
tasks = json.loads(tasks_path.read_text())
for task in tasks:
    if task.get("document_id") == DOC and task.get("evidence_id") in {P1T, P2T}:
        task["state"] = "attempted"
        task["reason"] = "Original page image and page text inspected; reaction regions inventoried and evidence-linked records generated."
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"records": len(records), "raw": str(raw_path.relative_to(ROOT)), "coverage": str(coverage_path.relative_to(ROOT))}, ensure_ascii=False))
