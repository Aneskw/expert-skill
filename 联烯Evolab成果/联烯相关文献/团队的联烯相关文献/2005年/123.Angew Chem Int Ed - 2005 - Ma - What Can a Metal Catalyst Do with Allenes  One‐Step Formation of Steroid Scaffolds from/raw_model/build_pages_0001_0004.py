#!/usr/bin/env python3
"""Build source-linked machine records for PDF pages 1--4 of doc_d6bb811b29c64a7b."""

import json
from pathlib import Path


DOC = "doc_d6bb811b29c64a7b"
BASE = Path(__file__).resolve().parents[1]
RAW = BASE / "raw_model" / "extracted_records_pages_0001_0004.json"
COVERAGE = BASE / "coverage" / "pages_0001_0004.json"
TASKS = BASE / "tasks.json"


def fact(value, evidence=()):
    return {
        "value": value,
        "evidence_ids": list(evidence) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def field(name, value, evidence=(), targets=None):
    item = {"name": name, "fact": fact(value, evidence)}
    if targets:
        item["target_entity_ids"] = list(targets)
    return item


def participant(entity_id, role, label, evidence, *, name=None, smiles=None, amounts=()):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence) if name is not None else fact(None),
        "smiles": fact(smiles, evidence) if smiles is not None else fact(None),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": list(amounts),
    }


def record(source_id, kind, evidence, participants, steps, outcomes, *, notes=(), unresolved=()):
    return {
        "record_id": f"{DOC}:{source_id}",
        "document_id": DOC,
        "source_reaction_id": source_id,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": list(evidence),
        "participants": list(participants),
        "steps": list(steps),
        "outcomes": list(outcomes),
        "notes": [fact(text, evidence) for text in notes],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": list(unresolved),
        },
    }


def step(step_id, participant_ids, conditions):
    return {
        "step_id": step_id,
        "participant_ids": list(participant_ids),
        "conditions": list(conditions),
    }


def q(number, unit, raw_text=None):
    value = {"number": number, "unit": unit}
    if raw_text:
        value["raw_text"] = raw_text
    return value


def ev(page):
    return (f"{DOC}:page{page}:text", f"{DOC}:page{page}:image")


E2 = ev(2)
E3 = ev(3)
SMILES_1A = "COC(=O)C(CC=C=C)(CC=C=C)C(=O)OC"
SMILES_1B = "N#CC(CC=C=C)(CC=C=C)C#N"
SMILES_1C = "O=S(=O)(c1ccccc1)C(CC=C=C)(CC=C=C)S(=O)(=O)c1ccccc1"
SMILES_1D = "CCOC(=O)C(C#N)(CC=C=C)CC=C=C"
SMILES_1E = "Cc1ccc(S(=O)(=O)N(CC=C=C)CC=C=C)cc1"


def substrate_1a(evidence, amounts=()):
    return participant(
        "substrate_1a", "reactant", "1a", evidence,
        name="5,5-bis(methoxycarbonyl)-1,2,7,8-nonatetraene",
        smiles=SMILES_1A, amounts=amounts,
    )


def product_2a(evidence):
    return participant(
        "product_2a", "product", "2a", evidence,
        name="18,19-norsteroid derivative 2a",
    )


def catalyst(label, evidence, entity_id="catalyst", loading=5):
    return participant(
        entity_id, "catalyst", label, evidence,
        amounts=[field("catalyst_loading", q(loading, "mol%"), evidence)],
    )


def solvent(label, evidence, smiles=None, volume=None, entity_id="solvent"):
    amounts = [] if volume is None else [field("volume", volume, evidence)]
    return participant(entity_id, "solvent", label, evidence, name=label, smiles=smiles, amounts=amounts)


records = []

# Page 2 prose: a sparse preparation statement, retained separately from cyclization.
prep1a_parts = [
    participant("diethyl_malonate", "reactant", "diethyl malonate", E2,
                name="diethyl malonate", smiles="CCOC(=O)CC(=O)OCC"),
    participant("butadienyl_bromide", "reactant", "2,3-butadienyl bromide", E2,
                name="2,3-butadienyl bromide", smiles="BrCC=C=C"),
    participant("product_1a", "product", "1a", E2,
                name="5,5-bis(methoxycarbonyl)-1,2,7,8-nonatetraene", smiles=SMILES_1A),
]
records.append(record(
    "preparation_1a", "reported_experiment", E2, prep1a_parts,
    [step("bisallenylation", [p["entity_id"] for p in prep1a_parts], [
        field("operation", "bisallenylation", E2),
        field("solvent", None), field("temperature", None), field("time", None),
    ])],
    [field("yield", None, targets=["product_1a"])],
    notes=(
        "The prose states that 1a was prepared by bisallenylation of diethyl malonate with 2,3-butadienyl bromide.",
        "The printed name diethyl malonate is not reconciled with the methoxycarbonyl groups drawn/named for 1a.",
    ),
    unresolved=(
        "Yield, reagent/base, solvent, temperature, time, workup and purification are not reported here.",
        "The precursor/product ester-label inconsistency requires external source review; no correction was inferred.",
        "No explicitly associated supporting information was supplied.",
    ),
))


def table1(entry, catalyst_label, time_h, yield_value, *, concentration=0.25, additives=(), failure=False):
    sid = "optimization_t1e6_t2e1" if entry == 6 else f"optimization_t1e{entry}"
    substrate_amounts = [field("substrate_concentration", q(concentration, "M"), E2)]
    parts = [substrate_1a(E2, substrate_amounts), product_2a(E2), catalyst(catalyst_label, E2)]
    for entity_id, label, loading in additives:
        parts.append(participant(
            entity_id, "reagent", label, E2,
            amounts=[field("amount", q(loading, "mol%"), E2)],
        ))
    parts.append(solvent("toluene", E2, "Cc1ccccc1"))
    outcome = "not detected" if failure else q(yield_value, "%")
    notes = []
    if failure:
        notes.append("The table prints a dash for yield and the accompanying prose states that the catalyst showed no activity.")
    if entry == 6:
        notes.append("This is the same 0.25 M, 2 h, 42% experiment repeated as Table 2 entry 1; it is represented once.")
    return record(
        sid, "optimization_entry", E2, parts,
        [step("cycloisomerization", [p["entity_id"] for p in parts], [
            field("temperature", "reflux", E2),
            field("time", q(time_h, "h"), E2),
            field("solvent", "toluene", E2),
        ])],
        [
            field("yield", outcome, E2, ["product_2a"]),
            field("yield_measurement_basis", None, targets=["product_2a"]),
        ],
        notes=notes,
        unresolved=(
            "Yield measurement basis, workup and purification are not reported for this optimization entry.",
            "Product 2a is structurally complex; no machine SMILES was assigned.",
            "No explicitly associated supporting information was supplied.",
        ),
    )


records.extend([
    table1(1, "[RhCl(PPh3)3]", 3, 10, additives=(("agsbf6", "AgSbF6", 10),)),
    table1(2, "[RhCl(cod)]2", 12.5, 15, additives=(("triphenyl_phosphite", "P(OPh)3", 10),)),
    table1(3, "[RhH(CO)(PPh3)2]", 2.5, 31, concentration=0.125),
    table1(4, "[RhCl(cod)]2", 12, 38, additives=(("triphenylphosphine", "PPh3", 10),)),
    table1(5, "[RhCl(PPh3)3]", 2, 38),
    table1(6, "trans-[RhCl(CO)(PPh3)2]", 2, 42),
    table1(7, "[Rh(cod)2]BF4", 12, None, failure=True),
    table1(8, "PtCl2", 4, None, failure=True),
])


def table2(entry, concentration, yield_percent):
    if entry == 1:
        return None
    sid = "optimization_t2e4_t3e1" if entry == 4 else f"optimization_t2e{entry}"
    amounts = [
        field("reaction_scale", q(0.25, "mmol"), E2),
        field("substrate_concentration", q(concentration, "M"), E2),
    ]
    parts = [
        substrate_1a(E2, amounts), product_2a(E2),
        catalyst("trans-[RhCl(CO)(PPh3)2]", E2),
        solvent("toluene", E2, "Cc1ccccc1"),
    ]
    outcomes = [
        field("yield", q(yield_percent, "%"), E2, ["product_2a"]),
        field("yield_measurement_basis", None, targets=["product_2a"]),
    ]
    notes = []
    if entry == 4:
        outcomes.append(field(
            "stereochemical_selectivity",
            "cis C/D ring junction; only one stereoisomer detected in the crude product by 1H NMR",
            E2, ["product_2a"],
        ))
        notes.append("This is the same 0.0417 M toluene, 2 h, 73% experiment repeated as Table 3 entry 1 and in prose; it is represented once.")
        notes.append("No intermediate product was observed during the reaction process.")
    return record(
        sid, "optimization_entry", E2, parts,
        [step("cycloisomerization", [p["entity_id"] for p in parts], [
            field("temperature", "reflux", E2),
            field("time", q(2, "h"), E2),
            field("solvent", "toluene", E2),
        ])],
        outcomes,
        notes=notes,
        unresolved=(
            "Yield measurement basis, workup and purification are not reported for Table 2.",
            "Product 2a is structurally complex; no machine SMILES was assigned.",
            "No explicitly associated supporting information was supplied.",
        ),
    )


for args in [(1, 0.25, 42), (2, 0.125, 55), (3, 0.0625, 69), (4, 0.0417, 73), (5, 0.0313, 72)]:
    item = table2(*args)
    if item:
        records.append(item)


SOLVENT_SMILES = {
    "toluene": "Cc1ccccc1",
    "CH3CN": "CC#N",
    "THF": "C1CCOC1",
    "DMF": "CN(C)C=O",
    "dioxane": "O1CCOCC1",
    "benzene": "c1ccccc1",
    # The source says only "xylene" and does not specify an isomer.
    "xylene": None,
}


def table3(entry, solvent_name, time_h, yield_percent, temperature):
    if entry == 1:
        return None
    sid = f"optimization_t3e{entry}"
    amounts = [
        field("reaction_scale", q(0.25, "mmol"), E2),
        field("substrate_concentration", q(0.0417, "M"), E2),
    ]
    parts = [
        substrate_1a(E2, amounts), product_2a(E2),
        catalyst("trans-[RhCl(CO)(PPh3)2]", E2),
        solvent(solvent_name, E2, SOLVENT_SMILES[solvent_name]),
        participant("nmr_internal_standard", "unspecified_agent", "1,3,5-trimethylbenzene", E2,
                    name="1,3,5-trimethylbenzene (NMR internal standard)", smiles="Cc1cc(C)cc(C)c1"),
    ]
    return record(
        sid, "optimization_entry", E2, parts,
        [step("cycloisomerization", [p["entity_id"] for p in parts], [
            field("temperature", temperature, E2),
            field("time", q(time_h, "h"), E2),
            field("solvent", solvent_name, E2),
        ])],
        [
            field("yield", q(yield_percent, "%"), E2, ["product_2a"]),
            field("yield_measurement_basis", "NMR spectroscopy using 1,3,5-trimethylbenzene as internal standard", E2, ["product_2a"]),
        ],
        unresolved=(
            "Internal-standard amount, workup and purification are not reported for this optimization entry.",
            "Product 2a is structurally complex; no machine SMILES was assigned.",
            "No explicitly associated supporting information was supplied.",
        ),
    )


for args in [
    (1, "toluene", 2, 73, "reflux"),
    (2, "toluene", 57, 43, q(60, "°C")),
    (3, "CH3CN", 9.6, 17, "reflux"),
    (4, "THF", 6, 36, "reflux"),
    (5, "DMF", 2.5, 28, q(110, "°C")),
    (6, "dioxane", 2.5, 41, "reflux"),
    (7, "benzene", 7, 54, "reflux"),
    (8, "xylene", 2, 41, "reflux"),
]:
    item = table3(*args)
    if item:
        records.append(item)


# Page 3 prose: preparation of scope substrate 1c.
prep1c_parts = [
    participant("bis_phenylsulfonyl_methane", "reactant", "CH2(SO2Ph)2", E3,
                name="bis(phenylsulfonyl)methane", smiles="O=S(=O)(c1ccccc1)CS(=O)(=O)c1ccccc1"),
    participant("butadienyl_bromide", "reactant", "2,3-butadienyl bromide", E3,
                name="2,3-butadienyl bromide", smiles="BrCC=C=C"),
    participant("sodium_hydride", "reagent", "NaH", E3, name="sodium hydride", smiles="[NaH]"),
    participant("product_1c", "product", "1c", E3, name="bisallene 1c", smiles=SMILES_1C),
]
records.append(record(
    "preparation_1c", "reported_experiment", E3, prep1c_parts,
    [step("bisallenylation", [p["entity_id"] for p in prep1c_parts], [
        field("operation", "bisallenylation", E3),
        field("solvent", None), field("temperature", None), field("time", None),
    ])],
    [
        field("yield", "quantitative", E3, ["product_1c"]),
        field("yield_measurement_basis", None, targets=["product_1c"]),
    ],
    unresolved=(
        "Reactant quantities, solvent, temperature, time, yield measurement basis, workup and purification are not reported here.",
        "No explicitly associated supporting information was supplied.",
    ),
))


SCOPE = {
    "b": ("1b", "2b", "bisallene 1b (E = CN)", "18,19-norsteroid derivative 2b", SMILES_1B, 74),
    "c": ("1c", "2c", "bisallene 1c (E = SO2Ph)", "18,19-norsteroid derivative 2c", SMILES_1C, 72),
    "d": ("1d", "2d", "bisallene 1d", "2,16-epimeric 18,19-norsteroid products 2d", SMILES_1D, 67),
    "e": ("1e", "2e", "bis(2,3-allenyl)amine 1e", "nitrogen analogue 2e", SMILES_1E, 57),
}


for key, (slabel, plabel, sname, pname, ssmiles, yield_percent) in SCOPE.items():
    s_amounts = []
    p_amounts = []
    if key == "c":
        s_amounts = [
            field("mass", q(1.509, "g"), E3),
            field("amount", q(3.76, "mmol"), E3),
        ]
        p_amounts = [field("mass", q(1.086, "g"), E3)]
    parts = [
        participant(f"substrate_{slabel}", "reactant", slabel, E3, name=sname, smiles=ssmiles, amounts=s_amounts),
        participant(f"product_{plabel}", "product", plabel, E3, name=pname, amounts=p_amounts),
        catalyst("trans-[RhCl(CO)(PPh3)2]", E3),
        solvent("dry toluene" if key == "c" else "toluene", E3, "Cc1ccccc1",
                q(90, "mL") if key == "c" else None),
    ]
    if key == "c":
        parts[2]["amounts"].extend([
            field("mass", q(130, "mg"), E3),
            field("amount", q(0.19, "mmol"), E3),
        ])
    conditions = [
        field("temperature", "reflux", E3),
        field("time", q(3, "h"), E3),
        field("solvent", "dry toluene" if key == "c" else "toluene", E3),
    ]
    outcomes = [
        field("yield", q(yield_percent, "%"), E3, [f"product_{plabel}"]),
        field("yield_measurement_basis", None, targets=[f"product_{plabel}"]),
    ]
    notes = []
    unresolved = [
        "Yield measurement basis is not stated.",
        "The complex product drawing was not converted to a machine SMILES.",
        "No explicitly associated supporting information was supplied.",
    ]
    if key == "c":
        conditions.append(field("atmosphere", "argon", E3))
        conditions.append(field("operation", "Reaction completion monitored by TLC (CH2Cl2/MeOH 40:1)", E3))
        conditions.append(field("workup", "Solvent removed by rotary evaporation", E3))
        conditions.append(field("purification", "Flash chromatography on silica gel; CH2Cl2/MeOH 100:1", E3))
        outcomes.append(field("melting_point", {"minimum": 143, "maximum": 145, "unit": "°C", "raw_text": "143–145 °C"}, E3, [f"product_{plabel}"]))
        notes.append("A full analytical characterization block for 2c is printed after the typical procedure.")
        unresolved[0] = "The 72% yield measurement basis is not explicitly labeled, although isolated mass and chromatography are reported."
    if key == "d":
        outcomes.append(field("diastereoselectivity", "mixture of 2,16 epimers", E3, [f"product_{plabel}"]))
        unresolved.append("The ratio of the 2,16 epimers is not reported.")
    records.append(record(
        f"scope_{slabel}_to_{plabel}", "substrate_scope_entry", E3, parts,
        [step("dimeric_cyclization", [p["entity_id"] for p in parts], conditions)],
        outcomes, notes=notes, unresolved=unresolved,
    ))


# The low-temperature trapping attempt is empirical but incompletely specified.
low_temp_parts = [
    substrate_1a(E3), product_2a(E3),
    catalyst("trans-[RhCl(CO)(PPh3)2]", E3),
]
records.append(record(
    "low_temperature_intermediate_trapping", "reported_experiment", E3, low_temp_parts,
    [step("intermediate_trapping_attempt", [p["entity_id"] for p in low_temp_parts], [
        field("temperature", "low temperature (exact value not reported)", E3),
        field("time", None),
    ])],
    [
        field("intermediate_detection", "no intermediate product detected", E3),
        field("yield", None, targets=["product_2a"]),
    ],
    notes=("The authors report that the reaction remained very fast at low temperature.",),
    unresolved=(
        "Exact temperature, time, concentration, analytical method and product yield are not reported for this trapping attempt.",
        "The catalyst/product assignment follows the immediately adjacent proposed pathway and requires source review.",
        "No explicitly associated supporting information was supplied.",
    ),
))


# Scheme 2 is retained as a mechanism, not as another reported 69% experiment.
mechanism_parts = [
    substrate_1a(E3), product_2a(E3),
    *[participant(f"intermediate_{label}", "unspecified_agent", label, E3,
                  name=f"proposed intermediate {label}") for label in ("4a", "5a", "6a", "7a", "8a", "9a")],
]
records.append(record(
    "scheme2_proposed_mechanism", "mechanism", E3, mechanism_parts,
    [
        step("cyclometalation", ["substrate_1a", "intermediate_4a", "intermediate_7a"], [field("operation", "proposed cyclometalation", E3)]),
        step("carbometalation", ["substrate_1a", "intermediate_4a", "intermediate_5a", "intermediate_7a", "intermediate_8a"], [field("operation", "proposed carbometalation with a second molecule of 1a", E3)]),
        step("reductive_elimination", ["intermediate_5a", "intermediate_6a", "intermediate_8a", "intermediate_9a"], [field("operation", "proposed reductive elimination", E3)]),
        step("diels_alder", ["intermediate_6a", "intermediate_9a", "product_2a"], [field("operation", "proposed intramolecular Diels–Alder reaction", E3)]),
    ],
    [],
    notes=(
        "Scheme 2 is explicitly labeled a possible mechanism; its central 69% transformation is an empirical context already represented by Table 2 entry 3 and is not duplicated here.",
        "E denotes CO2Me in Scheme 2.",
    ),
    unresolved=(
        "The proposed intermediates were not observed and were not assigned machine SMILES.",
        "This record is a mechanistic hypothesis, not a reported isolated experiment.",
    ),
))


RAW.parent.mkdir(parents=True, exist_ok=True)
COVERAGE.parent.mkdir(parents=True, exist_ok=True)
RAW.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")


def ids(prefixes):
    return [r["record_id"] for r in records if any(r["source_reaction_id"].startswith(p) for p in prefixes)]


coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1,
            "state": "attempted",
            "regions": [
                {
                    "region": "title, author block, introduction and supporting-information availability note",
                    "finding": "No reaction scheme, table, arrow, or current-paper experiment is presented on this page; it contains bibliographic/background material only.",
                    "evidence_ids": [f"{DOC}:page1:image", f"{DOC}:page1:text"],
                }
            ],
            "record_ids": [],
            "unresolved": ["The page states that supporting information is available, but no SI file was explicitly supplied or associated."],
        },
        {
            "page": 2,
            "state": "attempted",
            "regions": [
                {
                    "region": "upper-left prose above Table 1",
                    "finding": "Sparse preparation statement for 1a and narrative identification of product 2a; the preparation is retained as a partial reported experiment.",
                    "evidence_ids": [f"{DOC}:page2:image", f"{DOC}:page2:text"],
                },
                {
                    "region": "Table 1, its reaction arrow and footnotes, plus Figure 1",
                    "finding": "Eight catalyst-screening entries were extracted row-by-row; footnote additives/loadings were structured, and two dash/no-activity results were preserved. Figure 1 is crystallographic characterization, not another reaction.",
                    "evidence_ids": [f"{DOC}:page2:image", f"{DOC}:page2:text"],
                },
                {
                    "region": "Table 2, concentration series and adjacent optimized-condition prose",
                    "finding": "Five concentration entries were inspected; Table 2 entry 1 duplicates Table 1 entry 6, and Table 2 entry 4 duplicates Table 3 entry 1, so each pair maps to one record with shared page evidence.",
                    "evidence_ids": [f"{DOC}:page2:image", f"{DOC}:page2:text"],
                },
                {
                    "region": "Table 3, solvent series and footnotes",
                    "finding": "Eight solvent entries were inspected; the Table 3 entry 1 duplicate was merged, while entries 2–8 remain independent. NMR yield basis, internal standard and temperature footnote overrides were structured.",
                    "evidence_ids": [f"{DOC}:page2:image", f"{DOC}:page2:text"],
                },
            ],
            "record_ids": ids(("preparation_1a", "optimization_")),
            "unresolved": [
                "No associated SI was supplied; most optimization workups, purification details and Table 1/2 yield bases remain missing.",
                "Complex product 2a has no machine SMILES; structure correctness is not certified by the crystal image.",
            ],
        },
        {
            "page": 3,
            "state": "attempted",
            "regions": [
                {
                    "region": "upper-left scope prose and Scheme 1",
                    "finding": "Four substrate-scope arrows (1b–1e to 2b–2e) were extracted independently; the prose-only preparation of 1c was separated from its subsequent cyclization.",
                    "evidence_ids": [f"{DOC}:page3:image", f"{DOC}:page3:text"],
                },
                {
                    "region": "upper-right Scheme 2 and adjacent mechanism discussion",
                    "finding": "The cyclometalation/carbometalation/reductive-elimination/Diels–Alder network was classified as a proposed mechanism, not a reported experiment. The failed low-temperature intermediate-trapping attempt was retained separately with missing exact conditions.",
                    "evidence_ids": [f"{DOC}:page3:image", f"{DOC}:page3:text"],
                },
                {
                    "region": "lower-right Experimental Section typical procedure",
                    "finding": "The detailed 1c to 2c procedure was merged into the Scheme 1 scope record, including scale, catalyst loading, dry-toluene volume, argon, reflux time, TLC, workup, chromatography, isolated mass, yield and melting range.",
                    "evidence_ids": [f"{DOC}:page3:image", f"{DOC}:page3:text"],
                },
            ],
            "record_ids": ids(("preparation_1c", "scope_", "low_temperature_", "scheme2_")),
            "unresolved": [
                "Most scope entries lack substrate quantities, workup, purification and yield measurement basis in the supplied main text.",
                "The ratio of the 2,16 epimers 2d is not reported.",
                "Proposed intermediates 4a–9a were not observed and remain structure-unverified.",
            ],
        },
        {
            "page": 4,
            "state": "attempted",
            "regions": [
                {
                    "region": "references 1–32 and CCDC-262016 crystallographic-data note",
                    "finding": "No current-paper reaction arrow or experimental table occurs on this page. Cited prior work, including the referenced preparation of 2,3-butadienyl bromide, was not reclassified as an experiment of this paper; the CCDC note is characterization-data access information.",
                    "evidence_ids": [f"{DOC}:page4:image", f"{DOC}:page4:text"],
                }
            ],
            "record_ids": [],
            "unresolved": ["Referenced papers and CCDC files were not supplied and were not treated as associated SI."],
        },
    ],
}
COVERAGE.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")
if TASKS.exists():
    task_rows = json.loads(TASKS.read_text())
    for task in task_rows:
        if task.get("document_id") == DOC and task.get("task_id") in {
            f"{DOC}:page{page}:text" for page in range(1, 5)
        }:
            task["state"] = "attempted"
    TASKS.write_text(json.dumps(task_rows, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"records": len(records), "raw": str(RAW), "coverage": str(COVERAGE)}, ensure_ascii=False))
