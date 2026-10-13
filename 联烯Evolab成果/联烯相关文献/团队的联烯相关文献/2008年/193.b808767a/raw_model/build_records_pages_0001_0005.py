#!/usr/bin/env python3
"""Build evidence-linked records for doc_48615b59b28f678b, PDF pages 1–5."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / "runs" / "current"
RAW = RUN / "raw_model"
DOC = "doc_48615b59b28f678b"


def ev(page: int) -> list[str]:
    return [f"{DOC}:page{page}:text", f"{DOC}:page{page}:image"]


def evs(*pages: int) -> list[str]:
    return list(dict.fromkeys(item for page in pages for item in ev(page)))


def fact(value, evidence=None):
    evidence = list(evidence or [])
    return {
        "value": value,
        "evidence_ids": evidence if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def field(name, value, evidence=None, targets=None):
    item = {"name": name, "fact": fact(value, evidence)}
    if targets:
        item["target_entity_ids"] = list(targets)
    return item


def qty(number, unit, **extra):
    value = {"number": number, "unit": unit}
    value.update(extra)
    return value


def participant(entity_id, role, label, evidence, *, name=None, smiles=None, amounts=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence) if name else fact(None),
        "smiles": fact(smiles, evidence) if smiles else fact(None),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": [field(n, v, evidence) for n, v in (amounts or [])],
    }


def record(suffix, kind, evidence, participants, steps, outcomes, *, notes=None, unresolved=None):
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
        "notes": [fact(note, evidence) for note in (notes or [])],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": list(unresolved or []),
        },
    }


def step(step_id, participants, conditions):
    return {
        "step_id": step_id,
        "participant_ids": list(participants),
        "conditions": conditions,
    }


AR = "c1cccc2ccccc12"
PH = "c1ccccc1"
ALLENE_SMILES = {
    "1a": f"C=C=C{AR}",
    "1b": f"CC(=C=C{AR})CO",
    "1c": f"CCOC(=O)C(C)=C=C{AR}",
    "1d": f"CCOC(=O)C(CCC)=C=C{AR}",
    "1e": f"CCOC(=O)C(CCCC)=C=C{AR}",
    "1f": f"CCOC(=O)C(CC(C)C)=C=C{AR}",
    "1g": f"CCOC(=O)C(CC=C)=C=C{AR}",
    "1h": f"CCCC(=C=C{AR})P(=O)({PH}){PH}",
    "1i": f"CCCCC(=C=C{AR})P(=O)({PH}){PH}",
    "1j": f"CCCCCC(=C=C{AR})P(=O)({PH}){PH}",
    "1k": f"CCCCCCC(=C=C{AR})P(=O)({PH}){PH}",
    "1l": f"{PH}CCC(=C=C{AR})P(=O)({PH}){PH}",
    "3": f"C=C=C({PH})P(=O)({PH}){PH}",
}

SOLVENT_SMILES = {
    "Toluene": "Cc1ccccc1",
    "DMF": "CN(C)C=O",
    "i-C8H18": None,
    "DME": "COCCOC",
    "THF": "C1CCOC1",
    "t-BuOMe": "COC(C)(C)C",
    "n-Bu2O": "CCCCOCCCC",
    "Anisole": "COc1ccccc1",
    "CH3CN": "CC#N",
    "CCl3CH3": "CC(Cl)(Cl)Cl",
    "Xylene": None,
    "Dioxane": "C1COCCO1",
}

DMAD = "COC(=O)C#CC(=O)OC"


records = []

# Page 1, Scheme 1: three separately reported initial conditions.
for label, product, result in [("1a", "2a", "NR"), ("1b", "2b", "NR"), ("1c", "2c", 50)]:
    evidence = evs(1)
    parts = [
        participant(label, "reactant", label, evidence, smiles=ALLENE_SMILES[label]),
        participant("dmad", "reactant", "DMAD", evidence, name="dimethyl acetylenedicarboxylate", smiles=DMAD),
        participant("dioxane", "solvent", "dioxane", evidence, smiles=SOLVENT_SMILES["Dioxane"]),
        participant(product, "product", product, evidence),
    ]
    outcomes = (
        [field("reported_result", "NR", evidence, [product])]
        if result == "NR"
        else [field("reported_yield_2c", qty(result, "%"), evidence, [product]), field("yield_measurement_basis", None)]
    )
    records.append(record(
        f"scheme1_{label}_to_{product}", "reported_experiment", evidence, parts,
        [step("cycloaddition_aromatization", [label, "dmad", "dioxane"], [
            field("temperature", qty(150, "°C"), evidence),
            field("time", None),
            field("vessel", "reaction tube with a screw cap", evidence),
            field("atmosphere", None),
            field("workup", None),
            field("purification", None),
        ])], outcomes,
        notes=["Scheme 1 reports this initial condition before the solvent optimization."],
        unresolved=["Reactant amounts, reaction time, atmosphere, workup, and purification are not reported in Scheme 1."] +
                   ([] if result == "NR" else ["The measurement basis of the 50% yield is not stated."]),
    ))

# Page 1 prose: three alternative alkynes explicitly reported as ineffective.
alternative_alkynes = [
    ("diphenylalkyne", "diphenylalkyne", None),
    ("bis_trimethylsilyl_acetylene", "bis(trimethylsilyl)acetylene", "C[Si](C)(C)C#C[Si](C)(C)C"),
    ("dec_5_yne", "dec-5-yne", "CCCCC#CCCCC"),
]
for suffix, label, smiles in alternative_alkynes:
    evidence = evs(1)
    parts = [
        participant("allene_1_unspecified", "reactant", "alpha-naphthyl allene 1 (member unstated)", evidence),
        participant(suffix, "reactant", label, evidence, smiles=smiles),
    ]
    records.append(record(
        f"alternative_alkyne_{suffix}", "reported_experiment", evidence, parts,
        [step("alternative_alkyne_test", [p["entity_id"] for p in parts], [
            field("temperature", None), field("time", None), field("solvent", None),
            field("atmosphere", None), field("workup", None), field("purification", None),
        ])],
        [field("reported_effectiveness", "not effective", evidence)],
        notes=["The Results and discussion prose explicitly identifies this alkyne as ineffective."],
        unresolved=["The allene member, quantities, exact conditions, product identity, and analytical criterion for 'not effective' are not stated."],
    ))

# Page 2, Table 1 solvent/temperature optimization. Entry 12 is added below as the
# multi-evidence Table 1/Table 2/detailed 2c experiment.
table1 = [
    (1, "Toluene", 150, 14, 54),
    (2, "DMF", 150, 3, 39),
    (3, "i-C8H18", 150, 12, 43),
    (4, "DME", 150, 12, 30),
    (5, "THF", 150, 13, 46),
    (6, "t-BuOMe", 150, 13, 39),
    (7, "n-Bu2O", 150, 12, 46),
    (8, "Anisole", 150, 12, 45),
    (9, "CH3CN", 150, 15, 60),
    (10, "CCl3CH3", 150, 10, 66),
    (11, "Xylene", 150, 15, 52),
    (13, "Dioxane", 130, 10, 33),
    (14, "Dioxane", 110, 10, 35),
    (15, "Dioxane", 90, 12, 18),
]
for entry, solvent, temperature, duration, isolated_yield in table1:
    evidence = evs(2)
    parts = [
        participant("1c", "reactant", "1c", evidence, smiles=ALLENE_SMILES["1c"], amounts=[("equivalents", qty(1.5, "equiv"))]),
        participant("dmad", "reactant", "DMAD", evidence, name="dimethyl acetylenedicarboxylate", smiles=DMAD, amounts=[("equivalents", qty(1, "equiv"))]),
        participant("solvent", "solvent", solvent, evidence, smiles=SOLVENT_SMILES[solvent]),
        participant("2c", "product", "2c", evidence, name="1,2-bis(methoxycarbonyl)-3-(1-ethoxycarbonylethyl)phenanthrene"),
    ]
    records.append(record(
        f"table1_entry{entry}", "optimization_entry", evidence, parts,
        [step("cycloaddition_aromatization", ["1c", "dmad", "solvent"], [
            field("solvent", solvent, evidence),
            field("temperature", qty(temperature, "°C"), evidence),
            field("time", qty(duration, "h"), evidence),
            field("vessel", "reaction tube with a screw cap", evidence),
            field("atmosphere", None), field("workup", None), field("purification", None),
        ])],
        [field("isolated_yield_2c", qty(isolated_yield, "%"), evidence, ["2c"]),
         field("yield_measurement_basis", "isolated", evidence, ["2c"])],
        notes=[f"Table 1 entry {entry}."],
        unresolved=["Absolute scale, solvent volume, atmosphere, workup, purification, and product structure require source review."],
    ))

scope = [
    {
        "entry": 1, "substrate": "1c", "product": "2c", "time": 10, "yield": 72,
        "s_mass": 187, "s_mmol": 0.74, "d_mass": 69, "d_mmol": 0.49, "volume": 3,
        "p_mass": 111, "page": 3,
        "name": "1,2-bis(methoxycarbonyl)-3-(1-ethoxycarbonylethyl)phenanthrene",
    },
    {
        "entry": 2, "substrate": "1d", "product": "2d", "time": 24, "yield": 64,
        "s_mass": 105, "s_mmol": 0.375, "d_mass": 34, "d_mmol": 0.25, "volume": 2,
        "p_mass": 65, "page": 3,
        "name": "1,2-bis(methoxycarbonyl)-3-(1-ethoxycarbonylbutyl)phenanthrene",
    },
    {
        "entry": 3, "substrate": "1e", "product": "2e", "time": 24, "yield": 58,
        "s_mass": 100, "s_mmol": 0.340, "d_mass": 35, "d_mmol": 0.25, "volume": 2,
        "p_mass": 62, "page": 3,
        "name": "1,2-bis(methoxycarbonyl)-3-(1-ethoxycarbonylpentyl)phenanthrene",
    },
    {
        "entry": 4, "substrate": "1f", "product": "2f", "time": 24, "yield": 40,
        "s_mass": 115, "s_mmol": 0.391, "d_mass": 36, "d_mmol": 0.25, "volume": 2,
        "p_mass": 44, "page": 3,
        "name": "1,2-bis(methoxycarbonyl)-3-(1-ethoxycarbonyl-3-methylbutyl)phenanthrene",
        "reproduced": True,
    },
    {
        "entry": 5, "substrate": "1g", "product": "2g", "time": 19, "yield": 40,
        "s_mass": 106, "s_mmol": 0.375, "d_mass": 37, "d_mmol": 0.25, "volume": 2,
        "p_mass": 44, "page": 3,
        "name": "1,2-bis(methoxycarbonyl)-3-(1-ethoxycarbonylbut-3-enyl)phenanthrene",
        "extra_pages": [4], "unknown_mass": 34,
    },
    {
        "entry": 6, "substrate": "1h", "product": "2h", "time": 72, "yield": 76,
        "s_mass": 99, "s_mmol": 0.24, "d_mass": 68, "d_mmol": 0.48, "volume": 2,
        "p_mass": 102, "page": 4,
        "name": "1,2-bis(methoxycarbonyl)-3-(1-diphenylphosphinoylbutyl)phenanthrene",
    },
    {
        "entry": 7, "substrate": "1i", "product": "2i", "time": 72, "yield": 80,
        "s_mass": 107, "s_mmol": 0.25, "d_mass": 72, "d_mmol": 0.51, "volume": 2,
        "p_mass": 114, "page": 4,
        "name": "1,2-bis(methoxycarbonyl)-3-(1-diphenylphosphinoylpentyl)phenanthrene",
        "reproduced": True,
    },
    {
        "entry": 8, "substrate": "1j", "product": "2j", "time": 72, "yield": 70,
        "s_mass": 102, "s_mmol": 0.23, "d_mass": 76, "d_mmol": 0.53, "volume": 2,
        "p_mass": 94, "page": 4,
        "name": "1,2-bis(methoxycarbonyl)-3-(1-diphenylphosphinoylhexyl)phenanthrene",
    },
    {
        "entry": 9, "substrate": "1k", "product": "2k", "time": 72, "yield": 73,
        "s_mass": 111, "s_mmol": 0.25, "d_mass": 70, "d_mmol": 0.49, "volume": 2,
        "p_mass": 107, "page": 4,
        "name": "1,2-bis(methoxycarbonyl)-3-(1-diphenylphosphinoylheptyl)phenanthrene",
    },
    {
        "entry": 10, "substrate": "1l", "product": "2l", "time": 72, "yield": 65,
        "s_mass": 120, "s_mmol": 0.26, "d_mass": 70, "d_mmol": 0.49, "volume": 2,
        "p_mass": 101, "page": 4,
        "name": "1,2-bis(methoxycarbonyl)-3-(3-phenyl-1-diphenylphosphinoylpropyl)phenanthrene",
        "reproduced": True,
    },
]


def detailed_scope_record(row):
    detail_pages = [row["page"], *row.get("extra_pages", [])]
    evidence = evs(2, 3, *detail_pages)
    ester_series = row["entry"] <= 5
    allene_equiv = 1.5 if ester_series else 1
    dmad_equiv = 1 if ester_series else 2
    parts = [
        participant(row["substrate"], "reactant", row["substrate"], evidence,
                    smiles=ALLENE_SMILES[row["substrate"]], amounts=[
                        ("mass", qty(row["s_mass"], "mg")),
                        ("amount", qty(row["s_mmol"], "mmol")),
                        ("table_equivalents", qty(allene_equiv, "equiv")),
                    ]),
        participant("dmad", "reactant", "DMAD", evidence, name="dimethyl acetylenedicarboxylate", smiles=DMAD, amounts=[
            ("mass", qty(row["d_mass"], "mg")),
            ("amount", qty(row["d_mmol"], "mmol")),
            ("table_equivalents", qty(dmad_equiv, "equiv")),
        ]),
        participant("dioxane", "solvent", "dry 1,4-dioxane", evidence, smiles=SOLVENT_SMILES["Dioxane"], amounts=[
            ("volume", qty(row["volume"], "mL")),
        ]),
        participant(row["product"], "product", row["product"], evidence, name=row["name"], amounts=[
            ("isolated_mass", qty(row["p_mass"], "mg")),
        ]),
    ]
    if row.get("unknown_mass"):
        parts.append(participant("unidentified_coproduct", "product", "unidentified product", evidence, amounts=[
            ("isolated_mass", qty(row["unknown_mass"], "mg")),
        ]))
    notes = [f"Table 2 entry {row['entry']} was merged with its compound-specific experimental paragraph."]
    if row.get("reproduced"):
        notes.append("The acknowledgements state that this Table 2 result was reproduced by Tao Bai.")
    unresolved = [
        "The atmosphere and isolated product structure remain unverified.",
        "The general procedure is cited for TLC monitoring, concentration, and flash chromatography; no additional compound-specific workup is printed.",
    ]
    if row.get("unknown_mass"):
        unresolved.append("The coproduct is reported only as an unidentified product with a mass; no yield or structure is assigned.")
    return record(
        "table1_entry12_table2_entry1_2c" if row["entry"] == 1 else f"table2_entry{row['entry']}_{row['product']}",
        "optimization_entry" if row["entry"] == 1 else "substrate_scope_entry",
        evidence, parts,
        [step("cycloaddition_aromatization", [row["substrate"], "dmad", "dioxane"], [
            field("solvent", "dry 1,4-dioxane", evidence),
            field("temperature", qty(150, "°C"), evidence),
            field("time", qty(row["time"], "h"), evidence),
            field("vessel", "reaction tube with a screw cap", evidence),
            field("atmosphere", None),
            field("operation", "heated until complete conversion; monitored by TLC with petroleum ether/ethyl acetate 5:1", evs(3)),
            field("workup", "reaction mixture concentrated", evs(3)),
            field("purification", "flash chromatography on silica gel; petroleum ether/ethyl ether 10:1", evs(3)),
        ])],
        [field(f"isolated_yield_{row['product']}", qty(row["yield"], "%"), evidence, [row["product"]]),
         field("yield_measurement_basis", "isolated", evidence, [row["product"]])],
        notes=notes, unresolved=unresolved,
    )


records.extend(detailed_scope_record(row) for row in scope)

# Page 2 Scheme 2 plus page 4 exact preparation of compound 4.
evidence = evs(1, 2, 3, 4)
parts = [
    participant("3", "reactant", "3", evidence, name="phenyl/diphenylphosphinoyl-substituted allene", smiles=ALLENE_SMILES["3"], amounts=[
        ("mass", qty(125, "mg")), ("amount", qty(0.40, "mmol")),
    ]),
    participant("dmad", "reactant", "DMAD", evidence, name="dimethyl acetylenedicarboxylate", smiles=DMAD, amounts=[
        ("mass", qty(37, "mg")), ("amount", qty(0.26, "mmol")),
    ]),
    participant("dioxane", "solvent", "dry 1,4-dioxane", evidence, smiles=SOLVENT_SMILES["Dioxane"], amounts=[
        ("volume", qty(2, "mL")),
    ]),
    participant("4", "product", "4", evidence, name="1,2-bis(methoxycarbonyl)-4-(diphenylphosphinoyl)-3-methylnaphthalene", amounts=[
        ("isolated_mass", qty(85, "mg")),
    ]),
]
records.append(record(
    "scheme2_allene3_to_4", "reported_experiment", evidence, parts,
    [step("cycloaddition_aromatization", ["3", "dmad", "dioxane"], [
        field("solvent", "dry 1,4-dioxane", evidence),
        field("temperature", qty(150, "°C"), evidence),
        field("time", qty(36, "h"), evidence),
        field("vessel", "reaction tube with a screw cap", evidence),
        field("atmosphere", None),
        field("operation", "heated until complete conversion; monitored by TLC with petroleum ether/ethyl acetate 5:1", evs(3)),
        field("workup", "reaction mixture concentrated", evs(3)),
        field("purification", "flash chromatography on silica gel; petroleum ether/ethyl ether 10:1", evs(3)),
    ])],
    [field("isolated_yield_4", qty(71, "%"), evidence, ["4"]),
     field("yield_measurement_basis", "isolated", evidence, ["4"])],
    notes=["The ORTEP figure is structural evidence for product 4 and is not a separate reaction."],
    unresolved=["The atmosphere and complex reactant/product structures remain unverified."],
))

# Stable record ordering.
records.sort(key=lambda item: item["record_id"])

table1_ids = [f"{DOC}:table1_entry{i}" for i in range(1, 16) if i != 12] + [f"{DOC}:table1_entry12_table2_entry1_2c"]
table2_ids = [f"{DOC}:table1_entry12_table2_entry1_2c"] + [f"{DOC}:table2_entry{i}_2{chr(97+i)}" for i in range(2, 11)]
# Correct labels 2h–2l for entries 6–10 (the expression above already gives 2g–2k).
table2_ids = [f"{DOC}:table1_entry12_table2_entry1_2c"] + [f"{DOC}:table2_entry{row['entry']}_{row['product']}" for row in scope[1:]]
scheme1_ids = [f"{DOC}:scheme1_{label}_to_{product}" for label, product in [("1a", "2a"), ("1b", "2b"), ("1c", "2c")]]
alt_ids = [f"{DOC}:alternative_alkyne_{suffix}" for suffix, _, _ in alternative_alkynes]
scheme2_id = f"{DOC}:scheme2_allene3_to_4"

coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1,
            "state": "attempted",
            "regions": [
                {
                    "region": "title, abstract, introduction, and ESI availability statement",
                    "finding": "Background citations and high-level claims were inventoried but not promoted to present-paper experiments; the online ESI statement does not establish an associated SI source.",
                    "evidence_ids": ev(1),
                },
                {
                    "region": "Results and discussion prose and Scheme 1",
                    "finding": "Three initial present-paper conditions were extracted separately: 1a and 1b give NR, while 1c gives 2c in 50% reported yield at 150 °C in dioxane.",
                    "evidence_ids": ev(1),
                },
                {
                    "region": "lower-right scope discussion",
                    "finding": "Three alternative alkynes explicitly described as ineffective were retained as partial failed experiments; Table 2 interpretation and Scheme 2 context continue on page 2.",
                    "evidence_ids": ev(1),
                },
            ],
            "record_ids": scheme1_ids + alt_ids + [scheme2_id],
            "unresolved": [
                "Scheme 1 omits quantities, time, atmosphere, workup, purification, and the 50% yield basis.",
                "The alternative-alkyne sentence omits the exact allene member and all experimental details.",
                "The cited ESI was not supplied or explicitly associated.",
            ],
        },
        {
            "page": 2,
            "state": "attempted",
            "regions": [
                {
                    "region": "upper-left Table 1 and footnote",
                    "finding": "All 15 solvent/temperature optimization rows were extracted independently; entry 12 was merged with Table 2 entry 1 and the exact 2c preparation.",
                    "evidence_ids": ev(2),
                },
                {
                    "region": "upper-right Table 2 and footnotes",
                    "finding": "All 10 substrate-scope rows were extracted; the ester and phosphine-oxide stoichiometry footnotes were applied only to their respective rows.",
                    "evidence_ids": ev(2),
                },
                {
                    "region": "lower page Figures 1–2 and Scheme 2",
                    "finding": "Scheme 2 was extracted as one experiment; ORTEP drawings for 2c and 4 were linked as structural evidence and not counted as reactions.",
                    "evidence_ids": ev(2),
                },
            ],
            "record_ids": table1_ids + table2_ids + [scheme2_id],
            "unresolved": [
                "Most table-only optimization rows omit scale, solvent volume, atmosphere, workup, and purification.",
                "Complex structure assignments remain machine-derived and unverified.",
            ],
        },
        {
            "page": 3,
            "state": "attempted",
            "regions": [
                {
                    "region": "upper-left starting-material statements and General procedure",
                    "finding": "The cited starting-material methods were classified as literature-derived context rather than new row-level experiments; the explicit general TLC/concentration/chromatography operations were merged into the detailed product records.",
                    "evidence_ids": ev(3),
                },
                {
                    "region": "compound preparations 2c–2f and beginning of 2g",
                    "finding": "Exact masses, amounts, solvent volumes, temperatures, times, product masses, and isolated yields were merged into their Table 2 records; 2c also merges Table 1 entry 12.",
                    "evidence_ids": ev(3),
                },
            ],
            "record_ids": table2_ids + [scheme2_id],
            "unresolved": [
                "The atmosphere is not reported.",
                "Starting-material literature procedures are cited but not reproduced in experiment-level detail.",
                "The 2g paragraph continues onto page 4.",
            ],
        },
        {
            "page": 4,
            "state": "attempted",
            "regions": [
                {
                    "region": "continuation of 2g and compound preparations 2h–2l",
                    "finding": "The cross-page 2g paragraph and the five phosphine-oxide scope preparations were merged with Table 2 rows; the unidentified 34 mg coproduct from 2g was retained without a guessed identity or yield.",
                    "evidence_ids": ev(4),
                },
                {
                    "region": "compound 4 preparation and acknowledgements",
                    "finding": "The exact Scheme 2 preparation of 4 was merged into its page-2 arrow. The statement that Table 2 entries 4, 7, and 10 were reproduced was linked to those records rather than counted as new experiments.",
                    "evidence_ids": ev(4),
                },
            ],
            "record_ids": [f"{DOC}:table2_entry5_2g"] + [f"{DOC}:table2_entry{i}_{p}" for i, p in [(6, "2h"), (7, "2i"), (8, "2j"), (9, "2k"), (10, "2l")]] + [scheme2_id],
            "unresolved": [
                "The atmosphere is not reported.",
                "The 2g coproduct is unidentified.",
                "Complex product structures remain unverified.",
            ],
        },
        {
            "page": 5,
            "state": "attempted",
            "regions": [
                {
                    "region": "entire original page: reference list and crystallographic notes",
                    "finding": "No present-paper reaction arrow, table row, procedure, condition, or new result appears. References are citations, and crystal data for 2c/4 are characterization rather than reactions.",
                    "evidence_ids": ev(5),
                }
            ],
            "record_ids": [],
            "unresolved": [
                "Cited publications and CCDC files were not supplied as associated source documents and were not mined for reaction details."
            ],
        },
    ],
}

RAW.mkdir(parents=True, exist_ok=True)
(RAW / "records_pages_0001_0005.json").write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
(RUN / "coverage").mkdir(parents=True, exist_ok=True)
(RUN / "coverage" / "pages_0001_0005.json").write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

tasks_path = RUN / "tasks.json"
tasks = json.loads(tasks_path.read_text())
target_tasks = {f"{DOC}:page{page}:text" for page in range(1, 6)}
for task in tasks:
    if task["task_id"] in target_tasks:
        task["state"] = "attempted"
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"records": len(records), "coverage_pages": [p["page"] for p in coverage["pages"]]}, ensure_ascii=False))
