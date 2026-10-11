#!/usr/bin/env python3
"""Build source-derived machine records for ol006165u, PDF pages 1-3."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / "runs/current"
DOC = "doc_dcb0f88caf147d14"
P = {
    n: [f"{DOC}:page{n}:text", f"{DOC}:page{n}:image"] for n in (1, 2, 3)
}


def fact(value, evidence=()):
    return {
        "value": value,
        "evidence_ids": list(evidence) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def field(name, value, evidence=()):
    return {"name": name, "fact": fact(value, evidence)}


def participant(entity_id, role, evidence, label=None, name=None, amounts=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence) if label is not None else fact(None),
        "name": fact(name, evidence) if name is not None else fact(None),
        "smiles": fact(None),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": amounts or [],
    }


def record(suffix, kind, evidence, participants, conditions=(), outcomes=(), notes=(), unresolved=()):
    ids = [p["entity_id"] for p in participants]
    return {
        "record_id": f"{DOC}:{suffix}",
        "document_id": DOC,
        "source_reaction_id": suffix,
        "record_kind": kind,
        "status": "needs_review",
        "completeness": "partial",
        "evidence_ids": list(dict.fromkeys(evidence)),
        "participants": participants,
        "steps": [{
            "step_id": "step1",
            "participant_ids": ids,
            "conditions": list(conditions),
        }] if participants or conditions else [],
        "outcomes": list(outcomes),
        "notes": [fact(x, evidence) for x in notes],
        "review": {
            "method": "model",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": list(unresolved),
        },
    }


records = []

# Page 1 graphical abstract: current-paper generic transformation, not a run.
ev = P[1]
records.append(record(
    "abstract_general_scheme", "general_scheme", ev,
    [
        participant("abstract_dienyl_malonate", "reactant", ev, name="generic 2-(2′,3′-dienyl)malonate; E = COOMe"),
        participant("abstract_rx", "reactant", ev, label="RX", name="generic aryl or 1-alkenyl iodide"),
        participant("abstract_palladium", "catalyst", ev, name="Pd(PPh3)4"),
        participant("abstract_k2co3", "reagent", ev, name="K2CO3"),
        participant("abstract_tbab", "reagent", ev, name="n-Bu4NBr"),
        participant("abstract_acetonitrile", "solvent", ev, name="CH3CN"),
        participant("abstract_vinyl_cyclopropane", "product", ev, name="generic vinylic cyclopropane"),
    ],
    [field("temperature", "reflux", ev)],
    notes=("Graphical abstract is a generic current-paper transformation with R-group variables, not an individual experiment.",),
    unresolved=("Exact R group, reaction time, scale, reagent amounts, workup, purification, and yield are not specified in the graphical abstract.",),
))

# Scheme 1: prior work and its proposed regioselectivity pathway.
ev = P[1] + P[2]
records.append(record(
    "scheme1_prior_allenol_oxirane", "literature_example", ev,
    [
        participant("s1_allenol", "reactant", ev, name="generic 2,3-dienol"),
        participant("s1_organic_iodide", "reactant", ev, label="R2I", name="generic organic iodide"),
        participant("s1_pd0", "catalyst", ev, name="Pd(0) catalyst"),
        participant("s1_k2co3", "reagent", ev, name="K2CO3"),
        participant("s1_dmf", "solvent", ev, name="DMF"),
        participant("s1_oxirane", "product", ev, name="generic vinylic oxirane"),
    ],
    [field("temperature", {"number": 55, "unit": "°C"}, ev)],
    notes=("Scheme 1 is attributed to the authors' previous report (reference 6).", "The corresponding 2,5-dihydrofuran was reported as not observed."),
    unresolved=("Exact Pd catalyst identity/loading, scale, time, reagent amounts, yield, and yield basis are absent from this paper's presentation.",),
))
records.append(record(
    "scheme1_pi_allyl_pathways", "mechanism", P[2],
    [participant("s1_pi_allyl", "unspecified_agent", P[2], name="generic pi-allyl palladium intermediate")],
    notes=("Scheme 1 proposes intramolecular O-nucleophile attack pathways a and b; path a is invoked to explain the prior oxirane selectivity.",),
    unresolved=("The depicted palladium intermediate is proposed and is not reported as isolated or directly observed.",),
))

# Scheme 2: Cazes prior work plus proposed A/B pathway framework.
records.append(record(
    "scheme2_cazes_prior_cyclization", "literature_example", P[2],
    [
        participant("s2_dienyl_malonate", "reactant", P[2], name="generic 2-(2′,3′-dienyl)malonate; E = COOMe"),
        participant("s2_rx", "reactant", P[2], label="RX", name="PhI, isopropenyl bromide, c-hexenyl bromide, or vinyl bromide"),
        participant("s2_pd", "catalyst", P[2], name="Pd(dba)2-dppe"),
        participant("s2_thf", "solvent", P[2], name="THF"),
        participant("s2_cyclopropane", "product", P[2], name="generic vinylic cyclopropane product"),
        participant("s2_cyclopentene", "product", P[2], name="generic cyclopentene product"),
    ],
    [field("temperature", {"number": 40, "unit": "°C"}, P[2])],
    notes=("Scheme 2 summarizes Cazes et al. prior literature: cyclopentene was generally major, while vinyl bromide with R1 = R2 = R3 = H gave exclusive cyclopropane.",),
    unresolved=("The generic scheme does not map each listed RX to a numerical yield, time, scale, or complete procedure.",),
))
records.append(record(
    "scheme2_A_B_regioselectivity", "mechanism", P[2] + P[3],
    [
        participant("s2_intermediate_A", "unspecified_agent", P[2], label="A", name="proposed pi-allyl palladium intermediate A"),
        participant("s2_intermediate_B", "unspecified_agent", P[2], label="B", name="proposed pi-allyl palladium intermediate B"),
    ],
    notes=("Scheme 2 proposes A/B intermediates and paths a/b; the conclusion attributes Table 1 cyclopropane selectivity to exclusive formation of a B-type intermediate.",),
    unresolved=("Intermediates A and B are mechanistic proposals, not directly observed species.",),
))


def common_scheme3(entry, solvent, temperature, time_h, yield3, yield4, substrate="PhI", additive=None, catalyst="Pd(PPh3)4", catalyst_loading=None):
    ev = P[2]
    parts = [
        participant(f"s3_{entry}_substrate1", "reactant", ev, label="1", name="dimethyl 2-(2′,3′-butadienyl)malonate"),
        participant(f"s3_{entry}_halide", "reactant", ev, name=substrate),
        participant(f"s3_{entry}_catalyst", "catalyst", ev, name=catalyst,
                    amounts=[field("loading", catalyst_loading or {"number": 5, "unit": "mol%"}, ev)]),
        participant(f"s3_{entry}_base", "reagent", ev, name="K2CO3", amounts=[field("equivalents", {"number": 4, "unit": "equiv"}, ev)]),
        participant(f"s3_{entry}_solvent", "solvent", ev, name=solvent),
        participant(f"s3_{entry}_product3a", "product", ev, label="3a", name="1,1-bis(methoxycarbonyl)-2-(1′-phenyl)ethenylcyclopropane"),
        participant(f"s3_{entry}_product4a", "product", ev, label="4a", name="1-phenyl-4,4-bis(methoxycarbonyl)cyclopentene"),
    ]
    if catalyst.startswith("Pd2"):
        parts.append(participant(f"s3_{entry}_dppe", "catalyst", ev, name="dppe", amounts=[field("loading", {"number": 5, "unit": "mol%"}, ev)]))
    if additive:
        parts.append(participant(f"s3_{entry}_additive", "reagent", ev, name=additive))
    conditions = [field("temperature", temperature, ev), field("time", {"number": time_h, "unit": "h"}, ev)]
    return record(
        f"scheme3_entry_{entry}", "optimization_entry", ev, parts, conditions,
        [
            field("yield_3a", {"number": yield3, "unit": "%"}, ev),
            field("yield_4a", {"number": yield4, "unit": "%"}, ev),
            field("yield_measurement_basis", None),
        ],
        notes=(("n-Bu4NBr is described in prose as a catalytic amount; no numerical amount is printed." if additive else "No additive is shown in this row."),),
        unresolved=("Reaction scale, solvent volume, atmosphere, concentration, workup, purification, isolated masses, and yield measurement basis are not reported in the supplied main text.",),
    )


scheme3_rows = [
    (1, "DMF", {"number": 60, "unit": "°C"}, 25, 65, 8, "PhI", None, "Pd(PPh3)4", None),
    (2, "DMSO", {"number": 62, "unit": "°C"}, 22, 49, 21, "PhI", None, "Pd(PPh3)4", None),
    (3, "toluene", {"number": 82, "unit": "°C"}, 15, 30, 0, "PhI", None, "Pd(PPh3)4", None),
    (4, "benzene", {"number": 80, "unit": "°C"}, 15, 40, 0, "PhI", None, "Pd(PPh3)4", None),
    (5, "CH3CN", "reflux", 21, 41, 0, "PhI", None, "Pd2(dba)3·CHCl3", {"number": 2.5, "unit": "mol%"}),
    (6, "CH3CN", "reflux", 19.5, 32, 0, "PhI", None, "Pd(PPh3)4", None),
    (7, "CH3CN", "reflux", 15, 80, 0, "PhI", "n-Bu4NBr", "Pd(PPh3)4", None),
    (8, "CH3CN", "reflux", 22, 10, 0, "PhBr", None, "Pd(PPh3)4", None),
    (9, "CH3CN", "reflux", 18, 29, 0, "PhBr", "n-Bu4NBr", "Pd(PPh3)4", None),
]
for row in scheme3_rows:
    records.append(common_scheme3(*row))


def table1_record(entry, r_label, time_h, yield_pct, product_label):
    ev = P[2] + P[3]
    suffix = chr(ord("a") + entry - 1)
    parts = [
        participant(f"t1_{entry}_substrate1", "reactant", ev, label="1", name="dimethyl 2-(2′,3′-butadienyl)malonate"),
        participant(f"t1_{entry}_iodide", "reactant", ev, label=f"2{suffix}", name=f"organic iodide with R = {r_label}"),
        participant(f"t1_{entry}_pd", "catalyst", ev, name="Pd(PPh3)4", amounts=[field("loading", {"number": 5, "unit": "mol%"}, ev)]),
        participant(f"t1_{entry}_tbab", "reagent", ev, name="n-Bu4NBr", amounts=[field("loading", {"number": 10, "unit": "mol%"}, ev)]),
        participant(f"t1_{entry}_base", "reagent", ev, name="K2CO3", amounts=[field("equivalents", {"number": 4, "unit": "equiv"}, ev)]),
        participant(f"t1_{entry}_solvent", "solvent", ev, name="CH3CN"),
        participant(f"t1_{entry}_product", "product", ev, label=product_label, name=f"vinylic cyclopropane derivative {product_label}; R = {r_label}"),
    ]
    row_note = "Only the vinylic cyclopropane derivative was reported for this Table 1 row."
    if entry in (2, 6):
        row_note += " The 1-alkenyl iodide gives a 1,3-dienyl cyclopropane."
    if entry == 7:
        row_note += " The carbon-iodine bond reacts while the aryl carbon-bromine bond remains intact."
    return record(
        f"table1_entry_{entry}", "substrate_scope_entry", ev, parts,
        [field("temperature", "reflux", ev), field("time", {"number": time_h, "unit": "h"}, ev)],
        [field("yield", {"number": yield_pct, "unit": "%"}, ev), field("yield_measurement_basis", None)],
        notes=(row_note,),
        unresolved=("Table title prints ‘Methyl 2-(2′,3′-butadienyl)malonate’, while prose calls compound 1 dimethyl and the drawing shows two COOMe groups.", "Reaction scale, solvent volume, atmosphere, concentration, workup, purification, isolated mass, and yield measurement basis are not reported in the supplied main text."),
    )


table1_rows = [
    (1, "Ph", 15, 80, "3a"),
    (2, "(E)-1-hexenyl", 16, 67, "3b"),
    (3, "p-methoxyphenyl", 17, 69, "3c"),
    (4, "p-methylphenyl", 24, 82, "3d"),
    (5, "p-methoxycarbonylphenyl", 24, 58, "3e"),
    (6, "(E)-1-(2′-phenyl)ethenyl", 16, 46, "3f"),
    (7, "p-bromophenyl", 17, 83, "3g"),
    (8, "naphthyl", 23, 86, "3h"),
]
for row in table1_rows:
    records.append(table1_record(*row))


# Page 3 equations.
ev = P[3]
records.append(record(
    "equation1_heptadienyl_malonate", "reported_experiment", ev,
    [
        participant("eq1_heptadienyl", "reactant", ev, name="dimethyl 2-(2′,3′-heptadienyl)malonate"),
        participant("eq1_phi", "reactant", ev, name="PhI"),
        participant("eq1_pd", "catalyst", ev, name="Pd(PPh3)4"),
        participant("eq1_k2co3", "reagent", ev, name="K2CO3"),
        participant("eq1_tbab", "reagent", ev, name="n-Bu4NBr"),
        participant("eq1_ch3cn", "solvent", ev, name="CH3CN"),
        participant("eq1_3i", "product", ev, label="3i", name="three-membered vinylic cyclopropane product 3i"),
        participant("eq1_4i", "product", ev, label="4i", name="five-membered cyclopentene product 4i"),
    ],
    [field("temperature", "reflux", ev), field("time", {"number": 15, "unit": "h"}, ev)],
    [
        field("yield_3i", {"number": 82, "unit": "%"}, ev),
        field("3i_E_Z_ratio", "1.64:1", ev),
        field("yield_4i", {"number": 10, "unit": "%"}, ev),
        field("yield_measurement_basis", None),
    ],
    notes=("Condition set A is printed as catalytic Pd(PPh3)4, K2CO3, n-Bu4NBr, CH3CN, reflux, 15 h; 3i is the predominant product.",),
    unresolved=("Catalyst/base/additive amounts, scale, solvent volume, atmosphere, concentration, workup, purification, isolated masses, and yield measurement basis are not reported.",),
))
records.append(record(
    "equation2_malonitrile", "reported_experiment", ev,
    [
        participant("eq2_malonitrile", "reactant", ev, name="2-(2′,3′-butadienyl)malonitrile"),
        participant("eq2_phi", "reactant", ev, name="PhI"),
        participant("eq2_pd", "catalyst", ev, name="Pd(PPh3)4"),
        participant("eq2_k2co3", "reagent", ev, name="K2CO3"),
        participant("eq2_tbab", "reagent", ev, name="n-Bu4NBr"),
        participant("eq2_ch3cn", "solvent", ev, name="CH3CN"),
        participant("eq2_4j", "product", ev, label="4j", name="cyclopentene derivative 4j"),
    ],
    [field("temperature", "reflux", ev), field("time", {"number": 18, "unit": "h"}, ev)],
    [field("yield_4j", {"number": 43, "unit": "%"}, ev), field("yield_measurement_basis", None)],
    notes=("Cyclopentene derivative 4j was reported as the sole product; the malonate-specific cyclopropane regioselectivity did not extend to malonitrile.",),
    unresolved=("Catalyst/base/additive amounts, scale, solvent volume, atmosphere, concentration, workup, purification, isolated mass, detection limit for alternative products, and yield measurement basis are not reported."),
))


coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1,
            "state": "attempted",
            "regions": [
                {
                    "region": "graphical abstract beneath the ABSTRACT banner",
                    "finding": "Current-paper generic Pd(PPh3)4/K2CO3/n-Bu4NBr/CH3CN coupling-cyclization to a vinylic cyclopropane; treated as a general scheme, not a run.",
                    "evidence_ids": P[1],
                },
                {
                    "region": "introductory two-column prose below graphical abstract",
                    "finding": "Prior allenoic-acid, allenyl-ketone, and allenol chemistry is cited background; the allenol-to-oxirane result continues into Scheme 1 on page 2.",
                    "evidence_ids": P[1],
                },
            ],
            "record_ids": [
                f"{DOC}:abstract_general_scheme",
                f"{DOC}:scheme1_prior_allenol_oxirane",
            ],
            "unresolved": [
                "The graphical abstract omits row-specific substrate identity, time, scale, complete amounts, workup, purification, and yield.",
                "Cited background transformations without local arrows or complete local experimental data were not expanded into invented experiments.",
            ],
        },
        {
            "page": 2,
            "state": "attempted",
            "regions": [
                {
                    "region": "upper-left Scheme 1",
                    "finding": "Prior generic Pd(0)-catalyzed allenol/organic-iodide cyclization to a vinylic oxirane plus proposed pi-allyl attack paths a/b.",
                    "evidence_ids": P[2],
                },
                {
                    "region": "middle-left Scheme 2",
                    "finding": "Cazes prior generic malonate cyclization and proposed A/B intermediates; literature example and mechanism are classified separately.",
                    "evidence_ids": P[2],
                },
                {
                    "region": "upper-right Scheme 3 and footnotes",
                    "finding": "Nine independent optimization rows, including explicit zero 4a outcomes, catalyst-system override in entry 5, and PhBr override in entries 8-9.",
                    "evidence_ids": P[2],
                },
                {
                    "region": "lower-right Table 1 and preceding prose",
                    "finding": "Eight independent substrate-scope rows under shared optimized conditions; all report only vinylic cyclopropane products.",
                    "evidence_ids": P[2],
                },
            ],
            "record_ids": [
                f"{DOC}:scheme1_prior_allenol_oxirane",
                f"{DOC}:scheme1_pi_allyl_pathways",
                f"{DOC}:scheme2_cazes_prior_cyclization",
                f"{DOC}:scheme2_A_B_regioselectivity",
                *[f"{DOC}:scheme3_entry_{i}" for i in range(1, 10)],
                *[f"{DOC}:table1_entry_{i}" for i in range(1, 9)],
            ],
            "unresolved": [
                "Scheme 3 and Table 1 do not state reaction scale, workup, purification, isolated masses, or yield measurement bases.",
                "The exact numerical amount of n-Bu4NBr in Scheme 3 entries 7 and 9 is not printed; prose only calls it catalytic.",
                "Scheme 2 groups multiple prior-literature RX cases without row-level yield/time mapping.",
            ],
        },
        {
            "page": 3,
            "state": "attempted",
            "regions": [
                {
                    "region": "top-left continuation of Table 1 discussion",
                    "finding": "Explains exclusive cyclopropane formation, 1,3-dienyl products for entries 2/6, and selective C-I activation for entry 7.",
                    "evidence_ids": P[3],
                },
                {
                    "region": "left-column equation (1)",
                    "finding": "Heptadienyl malonate/PhI experiment gives 3i (82%, E/Z 1.64:1) and 4i (10%) under condition set A.",
                    "evidence_ids": P[3],
                },
                {
                    "region": "upper-right equation (2)",
                    "finding": "Butadienyl malonitrile/PhI gives cyclopentene 4j as sole product in 43% yield.",
                    "evidence_ids": P[3],
                },
                {
                    "region": "right-column conclusion and Supporting Information notice",
                    "finding": "Conclusion invokes a B-type intermediate for Table 1; SI is advertised online but no SI file is supplied or associated in this pilot.",
                    "evidence_ids": P[3],
                },
            ],
            "record_ids": [
                *[f"{DOC}:table1_entry_{i}" for i in range(1, 9)],
                f"{DOC}:equation1_heptadienyl_malonate",
                f"{DOC}:equation2_malonitrile",
                f"{DOC}:scheme2_A_B_regioselectivity",
            ],
            "unresolved": [
                "Equation 1 and equation 2 omit scale, full reagent loadings, workup, purification, isolated masses, and yield measurement basis.",
                "The article advertises typical procedures and analytical data in SI, but SI is not supplied and no association is inferred.",
            ],
        },
    ],
}


(RUN / "raw_model").mkdir(parents=True, exist_ok=True)
(RUN / "coverage").mkdir(parents=True, exist_ok=True)
(RUN / "raw_model/records_pages_0001_0003.json").write_text(
    json.dumps(records, ensure_ascii=False, indent=2) + "\n"
)
(RUN / "coverage/pages_0001_0003.json").write_text(
    json.dumps(coverage, ensure_ascii=False, indent=2) + "\n"
)

tasks_path = RUN / "tasks.json"
tasks = json.loads(tasks_path.read_text())
for task in tasks:
    if task.get("document_id") == DOC and task.get("evidence_id") in {P[n][0] for n in P}:
        task["state"] = "attempted"
        task["reason"] = "Original page image visually inspected; source-derived records and coverage ledger created."
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"records": len(records), "coverage_pages": [p["page"] for p in coverage["pages"]]}, ensure_ascii=False))
