#!/usr/bin/env python3
"""Reconcile PDF pages 7--9 with existing Zhang et al. 2012 records."""

import copy
import json
from pathlib import Path


DOC = "doc_74b3f5c116def6bc"
ROOT = Path(__file__).resolve().parents[3]
DATASET = ROOT / "runs/current/dataset.json"
OUT = ROOT / "runs/current/raw_model/records_pages_0007_0009.json"
COVERAGE = ROOT / "runs/current/coverage/pages_0007_0009.json"
TASKS = ROOT / "runs/current/tasks.json"


def ev(*pages):
    result = []
    for page in pages:
        result.extend([f"{DOC}:page{page}:text", f"{DOC}:page{page}:image"])
    return result


def fact(value, evidence=None):
    return {
        "value": value,
        "evidence_ids": list(evidence or []) if value is not None else [],
        "verification": "missing" if value is None else "unreviewed",
    }


def field(name, value, evidence=None, targets=None):
    item = {"name": name, "fact": fact(value, evidence)}
    if targets:
        item["target_entity_ids"] = targets
    return item


def q(number, unit, **extra):
    value = {"number": number, "unit": unit}
    value.update(extra)
    return value


def participant(entity_id, role, label, evidence, name=None, smiles=None, amounts=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence) if name is not None else fact(None),
        "smiles": fact(smiles, evidence) if smiles is not None else fact(None),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": amounts or [],
    }


def record(rid, kind, pages, participants, steps, outcomes, notes, unresolved):
    return {
        "record_id": f"{DOC}:{rid}",
        "document_id": DOC,
        "source_reaction_id": rid,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": ev(*pages),
        "participants": participants,
        "steps": steps,
        "outcomes": outcomes,
        "notes": [fact(note, ev(*pages)) for note in notes],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved,
        },
    }


data = json.loads(DATASET.read_text())
existing = {item["source_reaction_id"]: item for item in data["experiments"]}
records = []


def clone(rid, pages):
    item = copy.deepcopy(existing[rid])
    for evidence_id in ev(*pages):
        if evidence_id not in item["evidence_ids"]:
            item["evidence_ids"].append(evidence_id)
    item["status"] = "candidate"
    item["review"] = {"method": "none", "reviewer": None, "checked_fields": [], "unresolved": []}
    return item


def pmap(item):
    return {p["entity_id"]: p for p in item["participants"]}


def set_amounts(item, entity_id, values):
    pmap(item)[entity_id]["amounts"] = values


def replace_outcome(item, name, value, evidence, targets=None):
    for index, outcome in enumerate(item["outcomes"]):
        if outcome["name"] == name:
            item["outcomes"][index] = field(name, value, evidence, targets)
            return
    item["outcomes"].append(field(name, value, evidence, targets))


def set_notes(item, notes, evidence):
    item["notes"] = [fact(note, evidence) for note in notes]


def reconcile_method_b(
    rid, pages, substrate_id, substrate_mass, substrate_mmol,
    base_mass, base_mmol, reagent_mass, reagent_mmol, solvent_volume,
    duration, product_id, product_mass, purification, notes=None,
    iodination_temperature=-60,
):
    item = clone(rid, pages)
    evidence = ev(*pages)
    set_amounts(item, substrate_id, [
        field("mass", q(substrate_mass, "mg"), evidence),
        field("amount", q(substrate_mmol, "mmol"), evidence),
    ])
    set_amounts(item, "base_cs2co3", [
        field("mass", q(base_mass, "mg"), evidence),
        field("amount", q(base_mmol, "mmol"), evidence),
    ])
    set_amounts(item, "iodination_reagent", [
        field("mass", q(reagent_mass, "mg"), evidence),
        field("amount", q(reagent_mmol, "mmol"), evidence),
    ])
    set_amounts(item, "solvent_ch2cl2", [field("volume", q(solvent_volume, "mL"), evidence)])
    item["steps"] = [
        {
            "step_id": "base_prestir",
            "participant_ids": [substrate_id, "base_cs2co3", "solvent_ch2cl2"],
            "conditions": [
                field("temperature", "r.t.", ev(7)),
                field("reaction_time", q(1.5, "h"), ev(7)),
            ],
        },
        {
            "step_id": "iodolactonization",
            "participant_ids": [substrate_id, "base_cs2co3", "iodination_reagent", "solvent_ch2cl2"],
            "conditions": [
                field("temperature", q(iodination_temperature, "°C"), evidence),
                field("reaction_time", q(duration, "h"), evidence) if duration is not None else field("reaction_time", None),
                field("monitoring", "TLC to complete conversion", ev(7)),
                field("workup", "quench with water (3 mL) and saturated aqueous Na2S2O3 (2 mL); extract with Et2O (3 × 15 mL); wash with brine; dry over anhydrous Na2SO4; filter and evaporate", ev(7)),
                field("purification", f"silica-gel column chromatography; {purification}", evidence),
            ],
        },
    ]
    set_amounts(item, product_id, [field("isolated_mass", q(product_mass, "mg"), evidence)])
    replace_outcome(item, "yield_measurement_basis", "isolated after column chromatography", evidence)
    replace_outcome(item, "ratio_measurement_basis", "1H NMR analysis of the crude reaction mixture before separation", evidence)
    replace_outcome(item, "ee_measurement_basis", "chiral HPLC", evidence, [product_id])
    set_notes(item, notes or ["The detailed Method b procedure was reconciled with the matching table or scheme row; it is not a duplicate experiment."], evidence)
    item["review"]["unresolved"] = [
        "Product connectivity and stereochemical structure remain machine-unverified.",
        "No supporting-information file was supplied or explicitly associated.",
    ]
    return item


# Page 7 begins with characterization of the cross-page (S)-3h preparation.
item = clone("prep_S_3h", [7])
item["review"]["unresolved"] = [
    "Atmosphere is not stated for Method a; intermediate structures and final stereochemistry remain machine-unverified.",
    "No supporting-information file was supplied or explicitly associated.",
]
set_notes(item, [
    "The preparation ends on page 6; page 7 supplies the remaining optical-rotation and characterization text and is merged into the same record."
], ev(6, 7))
records.append(item)


# Detailed Method b preparations on page 7 and the page-7/page-8 boundary.
method_b_rows = [
    ("table1_entry4", [7], "substrate", 38.9, 0.20, 67.4, 0.21, 128.0, 0.40, 5, 12, "product_S_Z_5a", 54.1, "petroleum ether/EtOAc = 8:1", None, -60),
    ("scheme4a_Sa_3a", [7], "substrate", 196.0, 1.00, 328.1, 1.01, 587.6, 1.82, 20, 12, "product_major", 240.7, "petroleum ether/EtOAc = 8:1", ["Reagent 8 was added in two portions. The detailed procedure was reconciled with Scheme 4a."], -60),
    ("scheme4b_Ra_3b", [7], "substrate", 42.0, 0.20, 67.2, 0.21, 130.6, 0.40, 5, 11, "product_major", 49.9, "petroleum ether/EtOAc/CH2Cl2 = 10:1:1", None, -60),
    ("scheme4b_Ra_3c", [7], "substrate", 50.0, 0.20, 65.2, 0.20, 124.3, 0.38, 5, 9, "product_major", 46.8, "petroleum ether/EtOAc = 10:1", None, -60),
    ("table2_entry1", [7], "substrate", 153.1, 0.99, 326.0, 1.00, 642.5, 1.99, 25, 10, "product_Z", 194.6, "petroleum ether/EtOAc = 10:1", ["Reagent 8 was added in three portions. The detailed procedure was reconciled with Table 2 entry 1."], -60),
    ("table2_entry2", [7], "substrate", 181.6, 1.00, 329.3, 1.01, 615.0, 1.90, 25, 8, "product_Z", 218.4, "petroleum ether/EtOAc = 20:1", ["Reagent 8 was added in three portions. The detailed procedure and Table 2 report 99% ee for 5e, whereas Scheme 9 prints 97% ee; both source values are retained without reconciliation."], -60),
    ("table2_entry3", [7, 8], "substrate", 41.6, 0.20, 66.0, 0.20, 126.6, 0.39, 5, 14, "product_Z", 55.6, "petroleum ether/EtOAc = 20:1", None, -60),
    ("table2_entry4", [8], "substrate", 42.2, 0.20, 66.3, 0.20, 129.1, 0.40, 5, 10, "product_Z", 59.9, "petroleum ether/EtOAc = 20:1", ["The detailed page-8 prose prints the minor isomer as (4S,5R)-(E)-5f; that source label is retained even though the prior machine record had inferred a different configuration."], -60),
    ("table2_entry5", [8], "substrate", 33.6, 0.20, 66.1, 0.20, 128.5, 0.40, 5, 11, "product_Z", 39.7, "petroleum ether/EtOAc = 10:1", ["The detailed page-8 prose prints the minor isomer as (4S,5R)-(E)-5g; that source label is retained even though the prior machine record had inferred a different configuration."], -60),
]
for row in method_b_rows:
    item = reconcile_method_b(*row)
    if row[0] == "table2_entry4":
        pmap(item)["product_E"]["label"] = fact("(4S,5R)-(E)-5f", ev(8))
    if row[0] == "table2_entry5":
        pmap(item)["product_E"]["label"] = fact("(4S,5R)-(E)-5g", ev(8))
    if row[0] == "table2_entry2":
        item["review"]["unresolved"].append("The source disagrees on the ee of 5e: Table 2 and the detailed procedure report 99%, while Scheme 9 prints 97%.")
    records.append(item)


# Detailed (R)-3h iodolactonization: Scheme 6 supplies its -80 °C/11.5 h override.
item = reconcile_method_b(
    "scheme6_iodolactonization_R_3h", [8], "substrate", 40.0, 0.20,
    66.0, 0.20, 127.3, 0.39, 5, 11.5, "product_RR_Z_5h", 35.1,
    "petroleum ether/EtOAc = 10:1",
    ["The page-8 procedure says 'Following method b'; the explicit Scheme 6 temperature of -80 °C and duration of 11.5 h override the shared -60 °C Method b condition."],
    -80,
)
set_amounts(item, "product_RR_Z_5h", [field("isolated_mass", q(35.1, "mg"), ev(8))])
replace_outcome(item, "ratio_measurement_basis", "1H NMR analysis of the crude reaction mixture before separation", ev(8))
records.append(item)


# Page 8 reports the opposite enantiomer as a separate experiment not present in the earlier dataset.
e8 = ev(8)
parts = [
    participant("substrate", "reactant", "(S)-3h", e8, "(S)-3-methyl-6-phenylhexa-4,5-dienoic acid", None, [
        field("mass", q(40.6, "mg"), e8), field("amount", q(0.20, "mmol"), e8),
    ]),
    participant("base_cs2co3", "reagent", "Cs2CO3", e8, "cesium carbonate", "[Cs+].[Cs+].[O-]C([O-])=O", [
        field("mass", q(67.0, "mg"), e8), field("amount", q(0.21, "mmol"), e8),
    ]),
    participant("iodination_reagent", "reagent", "8", e8, "N-iodo-2,3-naphthalenedicarboximide", None, [
        field("mass", q(126.4, "mg"), e8), field("amount", q(0.39, "mmol"), e8),
    ]),
    participant("solvent_ch2cl2", "solvent", "CH2Cl2", e8, "dichloromethane", "ClCCl", [field("volume", q(5, "mL"), e8)]),
    participant("product_Z", "product", "(4S,5S)-(Z)-5h", e8, amounts=[field("isolated_mass", q(33.9, "mg"), e8)]),
    participant("product_E", "product", "(4S,5R)-(E)-5h", e8),
]
records.append(record(
    "methodb_S_3h_to_5h", "substrate_scope_entry", [8], parts,
    [
        {"step_id": "base_prestir", "participant_ids": ["substrate", "base_cs2co3", "solvent_ch2cl2"], "conditions": [
            field("temperature", "r.t.", ev(7)), field("reaction_time", q(1.5, "h"), ev(7)),
        ]},
        {"step_id": "iodolactonization", "participant_ids": ["substrate", "base_cs2co3", "iodination_reagent", "solvent_ch2cl2"], "conditions": [
            field("temperature", q(-60, "°C"), ev(7, 8)), field("reaction_time", None),
            field("monitoring", "TLC to complete conversion", ev(7)),
            field("workup", "quench with water (3 mL) and saturated aqueous Na2S2O3 (2 mL); extract with Et2O (3 × 15 mL); wash with brine; dry over anhydrous Na2SO4; filter and evaporate", ev(7)),
            field("purification", "silica-gel column chromatography; petroleum ether/EtOAc = 10:1", e8),
        ]},
    ],
    [
        field("isolated_yield_Z_5h", q(51, "%"), e8, ["product_Z"]),
        field("Z_to_E_ratio", ">99:1", e8, ["product_Z", "product_E"]),
        field("Z_product_ee", q(95, "%"), e8, ["product_Z"]),
        field("yield_measurement_basis", "isolated after column chromatography", e8, ["product_Z"]),
        field("ratio_measurement_basis", "1H NMR analysis of the crude reaction mixture before separation", e8, ["product_Z", "product_E"]),
        field("ee_measurement_basis", "chiral HPLC", e8, ["product_Z"]),
    ],
    ["This is the opposite-enantiomer experiment reported separately after the (R)-3h procedure; its reaction duration is not stated."],
    [
        "Iodolactonization duration is not reported for this experiment.",
        "Product connectivity and stereochemical structure remain machine-unverified.",
        "No supporting-information file was supplied or explicitly associated.",
    ],
))


def reconcile_natural_product(rid, start_mass, start_mmol, start_ee, tbaf_volume, tbaf_mmol,
                              dmf_volume, etoac_volume, pd_mass, pd_mmol, product_mass):
    item = clone(rid, [8])
    evidence = ev(4, 8)
    parts = pmap(item)
    set_amounts(item, "reactant_iodolactone", [
        field("mass", q(start_mass, "mg"), ev(8)),
        field("amount", q(start_mmol, "mmol"), ev(8)),
        field("starting_material_ee", q(start_ee, "%"), ev(8)),
    ])
    # Retain the Scheme-9 equivalents already represented and add exact Method-c charge data.
    equivalents = parts["reagent_tbaf"]["amounts"][0]
    parts["reagent_tbaf"]["amounts"] = [
        equivalents,
        field("solution_volume", q(tbaf_volume, "mL"), ev(8)),
        field("concentration", q(1.0, "M"), ev(8)),
        field("amount", q(tbaf_mmol, "mmol"), ev(8)),
    ]
    set_amounts(item, "solvent_dmf", [field("volume", q(dmf_volume, "mL"), ev(8))])
    set_amounts(item, "catalyst_pdc", [
        field("palladium_content", q(10, "%"), ev(8)),
        field("mass", q(pd_mass, "mg"), ev(8)),
        field("amount", q(pd_mmol, "mmol"), ev(8)),
        field("equivalents", q(0.1, "equiv"), ev(8)),
    ])
    set_amounts(item, "solvent_etoac", [field("volume", q(etoac_volume, "mL"), ev(8))])
    set_amounts(item, "natural_product", [field("isolated_mass", q(product_mass, "mg"), ev(8))])
    item["steps"] = [
        {"step_id": "TBAF_dehydroiodination", "participant_ids": ["reactant_iodolactone", "reagent_tbaf", "solvent_dmf"], "conditions": [
            field("temperature", q(25, "°C"), ev(8)), field("reaction_time", q(5, "h"), ev(8)),
            field("monitoring", "TLC", ev(8)),
            field("workup", "quench with H2O (5 mL); acidify with 5% aqueous HCl to pH 1; extract with Et2O (3 × 15 mL); wash with brine; dry over anhydrous Na2SO4; filter and evaporate", ev(8)),
            field("purification", "silica-gel chromatography, petroleum ether/EtOAc = 5:1", ev(8)),
        ]},
        {"step_id": "hydrogenation", "participant_ids": ["alkynyl_lactone", "catalyst_pdc", "hydrogen", "solvent_etoac"], "conditions": [
            field("hydrogen_pressure", "25 atm", ev(8)), field("temperature", "r.t.", ev(8)),
            field("reaction_time", q(23, "h"), ev(8)),
            field("workup", "filter through a short silica-gel column with Et2O", ev(8)),
        ]},
    ]
    replace_outcome(item, "yield_measurement_basis", "combined isolated yield over two steps", ev(8), ["natural_product"])
    set_notes(item, [
        "Method c forms an alkynyl lactone that is used immediately in the hydrogenation; no separate intermediate yield is reported.",
        "The detailed page-8 procedure was reconciled with Scheme 9 rather than counted as a duplicate experiment.",
    ], ev(4, 8))
    item["review"]["unresolved"] = [
        "The alkynyl-lactone intermediate and final stereochemical structures remain machine-unverified.",
        "No supporting-information file was supplied or explicitly associated.",
    ]
    if rid == "scheme9_methyl_decanolide_16":
        item["notes"].append(fact(
            "The detailed page-8 procedure reports the charged 5e as 99% ee, whereas Scheme 9 on page 4 prints 97% ee; both source values are retained without reconciliation.",
            ev(4, 8),
        ))
        item["review"]["unresolved"].append(
            "The source disagrees on the ee of starting 5e: the detailed procedure reports 99%, while Scheme 9 prints 97%."
        )
    return item


records.append(reconcile_natural_product(
    "scheme9_whisky_lactone_15", 129.6, 0.45, 99, 1.61, 1.61, 6, 12, 49.3, 0.05, 64.4,
))
records.append(reconcile_natural_product(
    "scheme9_methyl_decanolide_16", 191.4, 0.62, 99, 1.9, 1.9, 10, 15, 67.2, 0.06, 106.5,
))


assert len(records) == 14, len(records)


coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 7,
            "state": "attempted",
            "regions": [
                {
                    "region": "page 7 upper-left, completion of (S)-3h characterization and Method b general procedure",
                    "finding": "The first lines complete the cross-page (S)-3h preparation from page 6. Method b then states the shared Cs2CO3 pre-stir, -60 °C reagent-8 addition, TLC endpoint, aqueous/thiosulfate workup, extraction, drying, and chromatography used by the detailed iodolactonizations.",
                    "evidence_ids": ev(7),
                },
                {
                    "region": "page 7 left column, detailed preparations of (S)-(Z)-5a, (R)-(Z)-5a, and (S)-(Z)-5b",
                    "finding": "Three detailed experiments were reconciled with Table 1 entry 4 and Scheme 4 records, retaining exact charges, solvent volumes, isolated masses/yields, crude-NMR product ratios, ee values, and entry-specific chromatography.",
                    "evidence_ids": ev(7),
                },
                {
                    "region": "page 7 right column, detailed preparations of (S)-(Z)-5c, (4R,5S)-(Z)-5d, (4R,5S)-(Z)-5e, and beginning of (4R,5S)-(Z)-5f",
                    "finding": "Four detailed scope procedures were matched to Scheme 4/Table 2 rows. The 5f procedure continues onto page 8 and is represented once with cross-page evidence.",
                    "evidence_ids": ev(7),
                },
            ],
            "record_ids": [
                f"{DOC}:prep_S_3h", f"{DOC}:table1_entry4", f"{DOC}:scheme4a_Sa_3a",
                f"{DOC}:scheme4b_Ra_3b", f"{DOC}:scheme4b_Ra_3c", f"{DOC}:table2_entry1",
                f"{DOC}:table2_entry2", f"{DOC}:table2_entry3",
            ],
            "unresolved": [
                "Complex product connectivity and stereochemical structures remain machine-unverified.",
                "No supporting-information file was supplied or explicitly associated.",
            ],
        },
        {
            "page": 8,
            "state": "attempted",
            "regions": [
                {
                    "region": "page 8 upper-left, completion of (4R,5S)-(Z)-5f and detailed preparations of (4S,5R)-(Z)-5f and (4S,5R)-(Z)-5g",
                    "finding": "The cross-page 5f record is completed, and two additional Table 2 experiments are reconciled with exact quantities, isolated masses/yields, >99:1 ratios, and ee values. The printed minor-isomer labels are retained verbatim rather than replaced by inferred configurations.",
                    "evidence_ids": ev(8),
                },
                {
                    "region": "page 8 lower-left to upper-right, detailed (R)-3h and (S)-3h iodolactonizations",
                    "finding": "The (R)-3h experiment is merged with Scheme 6 and its explicit -80 °C/11.5 h override. The separate (S)-3h experiment is newly retained with 51% yield, 95% ee, and >99:1 ratio; its reaction duration is not stated.",
                    "evidence_ids": ev(8),
                },
                {
                    "region": "page 8 right column, Method c syntheses of natural lactones 15 and 16",
                    "finding": "Two two-stage experiments were reconciled with Scheme 9: TBAF dehydroiodination to an unisolated alkynyl lactone followed by Pd/C hydrogenation. Exact charges, solvent volumes, workup, 25 atm H2, isolated masses, combined yields, and ee values were retained.",
                    "evidence_ids": ev(8),
                },
            ],
            "record_ids": [
                f"{DOC}:table2_entry3", f"{DOC}:table2_entry4", f"{DOC}:table2_entry5",
                f"{DOC}:scheme6_iodolactonization_R_3h", f"{DOC}:methodb_S_3h_to_5h",
                f"{DOC}:scheme9_whisky_lactone_15", f"{DOC}:scheme9_methyl_decanolide_16",
            ],
            "unresolved": [
                "The duration of the (S)-3h iodolactonization is not reported.",
                "Complex products and the alkynyl-lactone intermediates remain structure-unverified.",
                "No supporting-information file was supplied or explicitly associated.",
            ],
        },
        {
            "page": 9,
            "state": "attempted",
            "regions": [
                {
                    "region": "page 9 full page, acknowledgements, references [1]–[12], and publication dates",
                    "finding": "The page contains acknowledgements and cited prior literature only. It has no new current-paper reaction arrow, table row, or experimental procedure, so no experiment record was created from this page.",
                    "evidence_ids": ev(9),
                },
            ],
            "record_ids": [],
            "unresolved": [
                "Cited external papers were not expanded into records because they are outside the supplied source evidence.",
            ],
        },
    ],
}


OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
COVERAGE.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

tasks = json.loads(TASKS.read_text())
for item in tasks:
    if item.get("document_id") == DOC and item.get("task_id", "").endswith(":text"):
        page = int(item["task_id"].split(":page", 1)[1].split(":", 1)[0])
        if 7 <= page <= 9:
            item["state"] = "attempted"
            item["reason"] = "Original rendered page image and extracted text inspected; coverage ledger records reconciled experiments, no-reaction findings, and unresolved details."
TASKS.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"records": len(records), "raw": str(OUT), "coverage": str(COVERAGE)}, ensure_ascii=False))
