#!/usr/bin/env python3
"""Build source-linked machine records for ol802794t, PDF pages 1--4."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / "runs/current"
DOC = "doc_75f12f85ca5a5f69"


def ev(page, kind="image"):
    return f"{DOC}:page{page}:{kind}"


def fact(value, evidence=()):
    return {
        "value": value,
        "evidence_ids": list(evidence),
        "verification": "missing" if value is None else "unreviewed",
    }


def field(name, value, evidence=(), targets=()):
    item = {"name": name, "fact": fact(value, evidence)}
    if targets:
        item["target_entity_ids"] = list(targets)
    return item


def participant(entity_id, role, label, evidence, smiles=None, amounts=(), name=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence) if name else fact(None),
        "smiles": fact(smiles, evidence) if smiles else fact(None),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": list(amounts),
    }


def record(suffix, kind, page, participants, steps=(), outcomes=(), notes=(), unresolved=(), extra_evidence=()):
    evidence = [ev(page, "image"), ev(page, "text"), *extra_evidence]
    evidence = list(dict.fromkeys(evidence))
    return {
        "record_id": f"{DOC}:{suffix}",
        "document_id": DOC,
        "source_reaction_id": suffix,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": evidence,
        "participants": participants,
        "steps": list(steps),
        "outcomes": list(outcomes),
        "notes": [fact(text, (ev(page, "image"), ev(page, "text"))) for text in notes],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": list(unresolved),
        },
    }


def step(step_id, participant_ids, conditions):
    return {"step_id": step_id, "participant_ids": participant_ids, "conditions": conditions}


def missing_operations():
    return [
        field("atmosphere", None),
        field("workup", None),
        field("purification", None),
    ]


def q(number, unit, **extra):
    return {"number": number, "unit": unit, **extra}


SIMPLE = {
    "CH2Cl2": "ClCCl",
    "CH3NO2": "C[N+](=O)[O-]",
    "CH3CN": "CC#N",
    "AcOEt": "CCOC(C)=O",
    "THF": "C1CCOC1",
    "DMPU": "CN1CCCN(C)C1=O",
    "DMSO": "CS(C)=O",
    "DMA": "CC(=O)N(C)C",
    "DMF": "CN(C)C=O",
    "PdI2": "[I-].[I-].[Pd+2]",
    "PdBr2": "[Br-].[Br-].[Pd+2]",
    "PdCl2": "[Cl-].[Cl-].[Pd+2]",
    "Pd(OAc)2": "CC(=O)[O-].CC(=O)[O-].[Pd+2]",
    "NaI": "[Na+].[I-]",
    "acetone": "CC(C)=O",
    "Ac2O": "CC(=O)OC(C)=O",
    "DMAP": "CN(C)c1ccncc1",
    "Et2O": "CCOCC",
    "SnCl2": "[Cl-].[Cl-].[Sn+2]",
    "n-C4H9CHO": "CCCCC=O",
    "C2H5CHO": "CCC=O",
    "vinyl acetate": "C=COC(C)=O",
}


records = []

# Page 1: paper-level graphical abstract, not a batch-specific experiment.
p1 = (ev(1, "image"),)
records.append(record(
    "graphical_abstract_general_scheme", "general_scheme", 1,
    [
        participant("generic_bisallenol", "reactant", "generic 1,omega-bisallenol / allenol-allenyl acetate", p1),
        participant("generic_bicyclic_product", "product", "generic 2,5-dihydrofuran-fused bicyclic product", p1),
        participant("generic_pdii", "catalyst", "Pd(II)", p1, amounts=(field("catalyst_loading", q(5, "mol%"), p1),)),
        participant("dmf", "solvent", "DMF", p1, SIMPLE["DMF"]),
    ],
    [step("summary_arrow", ["generic_bisallenol", "generic_pdii", "dmf", "generic_bicyclic_product"], [
        field("concentration", q(0.1, "M"), p1), field("temperature", None), field("time", None),
        *missing_operations(),
    ])],
    notes=("Generic paper-level reaction scope; X, Y, n, R1, and R2 are variable and no batch-specific yield is shown.",),
    unresolved=("Generic R-group structures and batch-specific temperature, time, yield, atmosphere, workup, and purification are not supplied.",),
))

# Page 2 Scheme 1: retrosynthetic/accessibility map without experimental conditions or yields.
p2 = (ev(2, "image"),)
records.append(record(
    "scheme1_accessibility_general_scheme", "general_scheme", 2,
    [
        participant("generic_fused_product", "product", "generic fused bicyclic product", p2),
        participant("generic_bisallenol", "reactant", "generic bis(2,3-allenol)", p2),
        participant("generic_bispropargyl_bromide", "reactant", "generic bis-propargyl bromide", p2),
        participant("generic_diyne_diol", "reactant", "generic diyne diol precursor", p2),
    ],
    notes=("Scheme 1 is a generic retrosynthetic/accessibility sequence shown with disconnection arrows and no reported conditions or yields.",),
    unresolved=("R and X are generic; the diagram does not establish individual experimental batches or stage yields.",),
))

# Page 2 Table 1: every row is a distinct optimization experiment.
table1 = [
    (1, "CH2Cl2", "PdI2", 1.5, 23, 59, 80),
    (2, "CH3NO2", "PdI2", 2, 0, 81, 80),
    (3, "CH3CN", "PdI2", 1.5, 18, 0, 80),
    (4, "AcOEt", "PdI2", 1.5, 32, 0, 80),
    (5, "THF", "PdI2", 1.5, 36, 0, 80),
    (6, "DMPU", "PdI2", 2, 0, 29, 80),
    (7, "DMSO", "PdI2", 1, 45, 0, 80),
    (8, "DMA", "PdI2", 1, 45, 0, 80),
    (9, "DMF", "PdI2", 1, 66, 0, 80),
    (10, "DMF", "PdBr2", 1, 57, 0, 80),
    (11, "DMF", "PdCl2", 1, 70, 0, 80),
    (12, "DMF", "PdCl2", 4, 68, 0, 25),
    (13, "DMF", "PdCl2(PhCN)2", 1, 61, 0, 80),
    (14, "DMF", "Pd(OAc)2", 1, 0, 89, 80),
    (15, "DMF", "PdCl2(PPh3)2", 1, 0, 97, 80),
]
for entry, solvent, catalyst, duration, product_yield, recovery, temperature in table1:
    cat_smiles = SIMPLE.get(catalyst)
    participants = [
        participant("substrate_1a", "reactant", "bis(2,3-allenol) 1a", p2),
        participant("product_2a", "product", "fused bicyclic product 2a", p2),
        participant("catalyst", "catalyst", catalyst, p2, cat_smiles, (field("catalyst_loading", q(5, "mol%"), p2),)),
        participant("solvent", "solvent", solvent, p2, SIMPLE.get(solvent)),
    ]
    conditions = [
        field("temperature", q(temperature, "°C"), p2),
        field("time", q(duration, "h"), p2),
        field("concentration", q(0.1, "M"), p2),
        *missing_operations(),
    ]
    records.append(record(
        f"table1_entry{entry}", "optimization_entry", 2, participants,
        [step("tandem_cyclization", [p["entity_id"] for p in participants], conditions)],
        [
            field("nmr_yield_of_2a", q(product_yield, "%"), p2, ("product_2a",)),
            field("recovered_starting_material_yield", q(recovery, "%"), p2, ("substrate_1a",)),
            field("yield_measurement_basis", "1H NMR analysis using 1,3,5-trimethylbenzene as internal standard", p2),
        ],
        notes=(("Footnote b overrides the reaction temperature to 25 °C." if entry == 12 else "Table 1 row transcribed from the original page image."),),
        unresolved=("Reaction scale, atmosphere, workup, and purification are not stated; substrate/product structures remain unverified.",),
    ))

# Page 3 Table 2: substrate scope.  The common drawing establishes DMF and 0.1 M.
p3 = (ev(3, "image"),)
table2 = [
    (1, "1a", "2a", "NTs", "C2H5", "A", 4, 62),
    (2, "1b", "2b", "NTs", "n-C5H11", "A", 4, 78),
    (3, "1c", "2c", "CH2", "C2H5", "A", 4, 0),
    (4, "1c", "2c", "CH2", "C2H5", "B", 1, 58),
    (5, "1d", "2d", "CH2", "p-ClC6H4", "B", 1, 51),
    (6, "1e", "2e", "O", "C2H5", "B", 2, 57),
    (7, "1f", "2f", "O", "i-C3H7", "B", 2, 67),
    (8, "1g", "2g", "O", "n-C4H9", "B", 1, 65),
    (9, "1g", "2g", "O", "n-C4H9", "footnote_b", 4, 69),
    (10, "1h", "2h", "SO2", "C2H5", "B", 1, 81),
    (11, "1i", "2i", "(CH2)2", "n-C4H9", "B", 1, 68),
    (12, "1j", "2j", "(CH2)2", "p-ClC6H4", "B", 1, 75),
]
for entry, substrate, product, tether, r_group, cond, duration, yld in table2:
    if cond == "A":
        catalyst, temperature, use_nai = "PdCl2", 25, False
    elif cond == "B":
        catalyst, temperature, use_nai = "PdCl2", 80, True
    else:
        catalyst, temperature, use_nai = "PdI2", 25, False
    participants = [
        participant("substrate", "reactant", f"bisallenol {substrate} (X={tether}, R={r_group})", p3),
        participant("product", "product", f"fused bicyclic product {product}", p3),
        participant("catalyst", "catalyst", catalyst, p3, SIMPLE[catalyst], (field("catalyst_loading", q(5, "mol%"), p3),)),
        participant("dmf", "solvent", "DMF", p3, SIMPLE["DMF"]),
    ]
    if use_nai:
        participants.append(participant("nai", "reagent", "NaI", p3, SIMPLE["NaI"], (field("equivalents", q(0.5, "equiv"), p3),)))
    conditions = [field("temperature", q(temperature, "°C"), p3), field("time", q(duration, "h"), p3), field("concentration", q(0.1, "M"), p3), *missing_operations()]
    notes = [f"Table 2 entry {entry}; condition {cond if cond != 'footnote_b' else 'footnote b'}."]
    if entry in (6, 7, 8, 9, 10, 11, 12):
        notes.append("The prose reports stereoselective product formation; the crude 1H NMR showed one stereoisomer, and the E assignment was established for 2e by NOESY.")
    records.append(record(
        f"table2_entry{entry}_{product}", "substrate_scope_entry", 3, participants,
        [step("tandem_cyclization", [p["entity_id"] for p in participants], conditions)],
        [field(f"reported_yield_of_{product}", q(yld, "%"), p3, ("product",)), field("yield_measurement_basis", None)],
        notes=notes,
        unresolved=("Yield basis, reaction scale, atmosphere, workup, and purification are not stated; complex structures and stereochemistry remain unverified.",),
    ))

# Page 3 Scheme 2: three distinct unsymmetrical-substrate experiments.
scheme2 = [
    ("1k", "LG1=OH, LG2=OH", q(32, "%"), q(50, "%")),
    ("1l", "LG1=OAc, LG2=OH", q(77, "%"), "table dash (—)"),
    ("1m", "LG1=OH, LG2=OAc", "table dash (—)", q(94, "%")),
]
for substrate, lg, yield_2l, yield_2m in scheme2:
    participants = [
        participant("substrate", "reactant", f"unsymmetrical substrate {substrate} ({lg})", p3),
        participant("product_2l", "product", "eight-membered fused product 2l", p3),
        participant("product_2m", "product", "eight-membered fused product 2m", p3),
        participant("pdcl2", "catalyst", "PdCl2", p3, SIMPLE["PdCl2"], (field("catalyst_loading", q(5, "mol%"), p3),)),
        participant("nai", "reagent", "NaI", p3, SIMPLE["NaI"], (field("equivalents", q(0.5, "equiv"), p3),)),
        participant("dmf", "solvent", "DMF", p3, SIMPLE["DMF"]),
    ]
    records.append(record(
        f"scheme2_{substrate}_cyclization", "substrate_scope_entry", 3, participants,
        [step("tandem_cyclization", [p["entity_id"] for p in participants], [
            field("temperature", q(80, "°C"), p3), field("time", None), field("concentration", q(0.1, "M"), p3), *missing_operations(),
        ])],
        [
            field("reported_yield_of_2l", yield_2l, p3, ("product_2l",)),
            field("reported_yield_of_2m", yield_2m, p3, ("product_2m",)),
            field("yield_measurement_basis", None),
        ],
        notes=("Source dashes are retained as source markers and are not interpreted as numeric zero or not detected.",),
        unresolved=("Duration, scale, yield basis, atmosphere, workup, and purification are not stated; structures are unverified.",),
    ))


def scheme3_stage(suffix, reactant_label, product_labels, agents, solvent, temperature, yields, extra_outcomes=(), note=None, kind="reported_experiment"):
    participants = [participant("reactant", "reactant", reactant_label, p3)]
    product_ids = []
    for idx, label in enumerate(product_labels, 1):
        entity_id = f"product_{idx}"
        product_ids.append(entity_id)
        participants.append(participant(entity_id, "product", label, p3))
    for idx, (label, role, amount) in enumerate(agents, 1):
        participants.append(participant(f"agent_{idx}", role, label, p3, SIMPLE.get(label), (() if amount is None else (field(amount[0], amount[1], p3),))))
    if solvent:
        participants.append(participant("solvent", "solvent", solvent, p3, SIMPLE.get(solvent)))
    conditions = [field("temperature", None if temperature is None else q(temperature, "°C"), p3), field("time", None), *missing_operations()]
    outcomes = []
    for idx, (name, value) in enumerate(yields):
        outcomes.append(field(name, value, p3, (product_ids[idx],)))
    outcomes.extend(extra_outcomes)
    return record(
        suffix, kind, 3, participants,
        [step("reported_transformation", [p["entity_id"] for p in participants], conditions)],
        outcomes,
        notes=(() if note is None else (note,)),
        unresolved=("The scheme omits duration, scale, atmosphere, workup, purification, and yield measurement basis; complex structures remain unverified.",),
    )


# Scheme 3, first one-pot sequence: one record per dibromide substrate, two product outcomes each.
records.append(scheme3_stage(
    "scheme3_3n_to_1i_and_4n", "bis-propargyl bromide 3n (n=2)",
    ["bisallenol 1i", "propargyl halide-allenol 4n (X=Cl/Br/I mixture)"],
    [("NaI", "reagent", None), ("SnCl2", "reagent", None), ("n-C4H9CHO", "reactant", None)], "DMF", None,
    [("reported_yield_of_1i", q(25, "%")), ("reported_yield_of_4n", q(39, "%"))],
    note="The halide product is explicitly a chloride/bromide/iodide mixture; no single halogen identity is inferred.",
))
records.append(scheme3_stage(
    "scheme3_3o_to_1p_and_4o", "bis-propargyl bromide 3o (n=1)",
    ["bisallenol 1p", "propargyl halide-allenol 4o (X=Cl/Br/I mixture)"],
    [("NaI", "reagent", None), ("SnCl2", "reagent", None), ("n-C4H9CHO", "reactant", None)], "DMF", None,
    [("reported_yield_of_1p", q(26, "%")), ("reported_yield_of_4o", q(34, "%"))],
    note="The halide product is explicitly a chloride/bromide/iodide mixture; no single halogen identity is inferred.",
))

for n_label, start, product, yld in [("n", "4n", "5n", 75), ("o", "4o", "5o", 96)]:
    records.append(scheme3_stage(
        f"scheme3_{start}_to_{product}_halide_exchange", f"propargyl halide-allenol {start}", [f"propargyl iodide-allenol {product}"],
        [("NaI", "reagent", None)], "acetone", None,
        [(f"reported_yield_of_{product}", q(yld, "%"))],
    ))

for start, product, yld in [("5n", "6n", 81), ("5o", "6o", 79)]:
    records.append(scheme3_stage(
        f"scheme3_{start}_to_{product}_acetylation", f"propargyl iodide-allenol {start}", [f"propargyl iodide-allenyl acetate {product}"],
        [("Ac2O", "reagent", None), ("DMAP", "catalyst", None)], "Et2O", None,
        [(f"reported_yield_of_{product}", q(yld, "%"))],
    ))

for start, product, yld in [("6n", "1n", 75), ("6o", "1o", 84)]:
    records.append(scheme3_stage(
        f"scheme3_{start}_to_{product}_allenol_formation", f"propargyl iodide-allenyl acetate {start}", [f"racemic allenol-allenyl acetate {product}"],
        [("SnCl2", "reagent", None), ("C2H5CHO", "reactant", None)], "DMF", None,
        [(f"reported_yield_of_{product}", q(yld, "%"))],
    ))

# Enzymatic kinetic resolutions.
for substrate, yld in [("1n", 41), ("1o", 41)]:
    product = f"(S)-{substrate}"
    extra = [
        field(f"ee_of_{product}", q(99, "%"), p3, ("product_1",)),
        field("ee_assignment_basis", "ee refers to the resolved allenol part", p3, ("product_1",)),
    ]
    rec = scheme3_stage(
        f"scheme3_{substrate}_kinetic_resolution", f"racemic allenol-allenyl acetate {substrate}", [f"resolved allenol-allenyl acetate {product}"],
        [("Novozym-435", "catalyst", None), ("vinyl acetate", "reagent", None)], None, 60,
        [("recovered_resolved_substrate_yield", q(yld, "%"))], extra,
        note="The isolated resolved starting-material enantiomer is represented as recovery, distinct from a product yield.",
    )
    records.append(rec)

# Optically active cyclizations under explicitly referenced standard conditions B.
for substrate, product, yld in [("(S)-1n", "(S)-2n", 80), ("(S)-1o", "(S)-2o", 76)]:
    participants = [
        participant("substrate", "reactant", f"resolved allenol-allenyl acetate {substrate} (99% ee)", p3),
        participant("product", "product", f"optically active fused bicyclic product {product}", p3),
        participant("pdcl2", "catalyst", "PdCl2", p3, SIMPLE["PdCl2"], (field("catalyst_loading", q(5, "mol%"), p3),)),
        participant("nai", "reagent", "NaI", p3, SIMPLE["NaI"], (field("equivalents", q(0.5, "equiv"), p3),)),
        participant("dmf", "solvent", "DMF", p3, SIMPLE["DMF"]),
    ]
    records.append(record(
        f"scheme3_{substrate.replace('(', '').replace(')', '').replace('-', '_')}_cyclization", "substrate_scope_entry", 3, participants,
        [step("tandem_cyclization", [p["entity_id"] for p in participants], [
            field("temperature", q(80, "°C"), p3), field("time", None), field("concentration", q(0.1, "M"), p3), *missing_operations(),
        ])],
        [
            field(f"reported_yield_of_{product}", q(yld, "%"), p3, ("product",)),
            field(f"ee_of_{product}", q(99, "%"), p3, ("product",)),
            field("yield_measurement_basis", None),
        ],
        notes=("The prose states that cyclization proceeded without obvious racemization under standard conditions B.",),
        unresolved=("Duration, scale, yield basis, atmosphere, workup, and purification are not stated; absolute configuration and connectivity remain unverified.",),
    ))

# Page 3 Scheme 4: explicitly proposed mechanism.
records.append(record(
    "scheme4_proposed_coupling_cyclization_mechanism", "mechanism", 3,
    [
        participant("substrate_1", "reactant", "generic 1,5-bisallenol / allenol-allenyl acetate 1", p3),
        participant("pd_x2", "catalyst", "PdX2", p3),
        participant("intermediate_m1", "unspecified_agent", "proposed oxypalladation intermediate M1", p3),
        participant("intermediate_m2", "unspecified_agent", "proposed pi-allylic palladium intermediate M2", p3),
        participant("product_2", "product", "generic fused bicyclic product 2", p3),
    ],
    [
        step("proposed_cyclic_oxypalladation", ["substrate_1", "pd_x2", "intermediate_m1"], [field("operation", "proposed cyclic oxypalladation", p3)]),
        step("proposed_carbopalladation", ["intermediate_m1", "intermediate_m2"], [field("operation", "proposed regioselective intramolecular carbopalladation", p3)]),
        step("proposed_elimination", ["intermediate_m2", "product_2"], [field("operation", "proposed trans-beta-hydroxide or acetate elimination", p3)]),
    ],
    notes=("M1 and M2 are proposed intermediates, not reported isolated products.",),
    unresolved=("Generic X, Y, R1, and R2 groups and organopalladium connectivity are not independently verified.",),
))

assert len(records) == 45, len(records)
assert len({r["record_id"] for r in records}) == len(records)

raw_path = RUN / "raw_model/records_pages_0001_0004.json"
raw_path.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")

page1_ids = [r["record_id"] for r in records if r["source_reaction_id"] == "graphical_abstract_general_scheme"]
page2_ids = [r["record_id"] for r in records if r["source_reaction_id"] == "scheme1_accessibility_general_scheme" or r["source_reaction_id"].startswith("table1_")]
page3_ids = [r["record_id"] for r in records if r["record_id"] not in set(page1_ids + page2_ids)]

coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1,
            "state": "attempted",
            "regions": [
                {"region": "graphical abstract and abstract in the center of the original page", "finding": "Generic present-paper tandem-cyclization scope classified as a general scheme; no batch-specific yield is shown.", "evidence_ids": [ev(1, "image"), ev(1, "text")]},
                {"region": "two-column introduction below the abstract", "finding": "Background and cited prior work only; no independent present-paper experiment is specified.", "evidence_ids": [ev(1, "image"), ev(1, "text")]},
            ],
            "record_ids": page1_ids,
            "unresolved": ["Generic structure variables and batch-specific conditions/outcomes are not resolved on this page."],
        },
        {
            "page": 2,
            "state": "attempted",
            "regions": [
                {"region": "upper-left Scheme 1", "finding": "Generic retrosynthetic/accessibility sequence with disconnection arrows and no conditions or yields; classified as a general scheme.", "evidence_ids": [ev(2, "image"), ev(2, "text")]},
                {"region": "upper-right Table 1 and footnotes", "finding": "Fifteen independent solvent/catalyst optimization rows extracted with image-verified times, NMR yields, recoveries, and the entry-12 temperature override.", "evidence_ids": [ev(2, "image"), ev(2, "text")]},
                {"region": "lower discussion columns", "finding": "Narrative interpretation of Table 1 and lead-in to Table 2; no additional independent batch beyond the table rows.", "evidence_ids": [ev(2, "image"), ev(2, "text")]},
            ],
            "record_ids": page2_ids,
            "unresolved": ["Extracted text concatenates several Table 1 columns; row values were transcribed from the original image.", "Table 1 omits scale, atmosphere, workup, and purification."],
        },
        {
            "page": 3,
            "state": "attempted",
            "regions": [
                {"region": "upper-left Table 2 and footnotes", "finding": "Twelve independent substrate-scope rows extracted; Conditions A/B and the entry-9 PdI2 footnote were applied only to their rows.", "evidence_ids": [ev(3, "image"), ev(3, "text")]},
                {"region": "middle-left Scheme 2", "finding": "Three independent unsymmetrical-substrate cyclizations extracted; displayed dashes are preserved as source markers.", "evidence_ids": [ev(3, "image"), ev(3, "text")]},
                {"region": "upper-right Scheme 3 and adjacent prose", "finding": "Twelve stage- or substrate-specific preparation, halide-exchange, acetylation, allene-formation, kinetic-resolution, and cyclization records extracted.", "evidence_ids": [ev(3, "image"), ev(3, "text")]},
                {"region": "lower-right Scheme 4", "finding": "Oxypalladation/carbopalladation/elimination sequence classified as a proposed mechanism, not an observed batch.", "evidence_ids": [ev(3, "image"), ev(3, "text")]},
            ],
            "record_ids": page3_ids,
            "unresolved": ["Most schemes omit scale, duration, atmosphere, workup, purification, and yield basis.", "Complex structures, E geometry, and absolute stereochemistry remain unverified."],
        },
        {
            "page": 4,
            "state": "attempted",
            "regions": [
                {"region": "conclusion, acknowledgements, Supporting Information notice, and references", "finding": "No new reaction arrow, table, or independent experiment. The paper says SI is available online, but no SI file was supplied or explicitly associated.", "evidence_ids": [ev(4, "image"), ev(4, "text")]},
            ],
            "record_ids": [],
            "unresolved": ["SI association remains unestablished; procedures and spectra advertised by the paper were not inferred."],
        },
    ],
}
(RUN / "coverage").mkdir(parents=True, exist_ok=True)
(RUN / "coverage/pages_0001_0004.json").write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

tasks_path = RUN / "tasks.json"
tasks = json.loads(tasks_path.read_text())
for task in tasks:
    if task["document_id"] == DOC and task["task_id"] in {ev(i, "text") for i in range(1, 5)}:
        task["state"] = "attempted"
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"records": len(records), "raw": str(raw_path), "coverage_pages": [p["page"] for p in coverage["pages"]]}, ensure_ascii=False))
