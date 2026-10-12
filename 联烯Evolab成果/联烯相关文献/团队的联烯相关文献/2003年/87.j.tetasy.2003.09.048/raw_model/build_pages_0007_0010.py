#!/usr/bin/env python3
"""Enrich existing evidence-linked records from visually inspected PDF pages 7-10."""
from __future__ import annotations

import copy
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
DATASET = ROOT / "runs/current/dataset.json"
OUT = ROOT / "runs/current/raw_model/extracted_records_pages_0007_0010.json"
COVERAGE = ROOT / "runs/current/coverage/pages_0007_0010.json"
TASKS = ROOT / "runs/current/tasks.json"
DOC = "doc_a92716bc66b648fb"


def unique(values):
    return list(dict.fromkeys(values))


def evid(page: int) -> list[str]:
    return [f"{DOC}:page{page}:image", f"{DOC}:page{page}:text"]


def fact(value, evidence=None):
    return {
        "value": value,
        "evidence_ids": unique(evidence or []) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def field(name, value, evidence=None, targets=None):
    result = {"name": name, "fact": fact(value, evidence)}
    if targets:
        result["target_entity_ids"] = targets
    return result


def q(number, unit, qualifier=None, raw_text=None):
    result = {"number": number, "unit": unit}
    if qualifier:
        result["qualifier"] = qualifier
    if raw_text:
        result["raw_text"] = raw_text
    return result


def participant(entity_id, role, label, name, evidence, smiles=None, amounts=None):
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


data = json.loads(DATASET.read_text())
by_id = {record["record_id"]: record for record in data["experiments"]}


def take(suffix: str):
    record_id = f"{DOC}:{suffix}"
    if record_id not in by_id:
        raise KeyError(f"missing existing record {record_id}")
    return copy.deepcopy(by_id[record_id])


def add_record_evidence(record, page):
    record["evidence_ids"] = unique(record["evidence_ids"] + evid(page))


def get_participant(record, entity_id):
    return next(p for p in record["participants"] if p["entity_id"] == entity_id)


def set_amounts(record, entity_id, amounts):
    get_participant(record, entity_id)["amounts"] = amounts


def add_outcome_evidence(record, name, target, page):
    for outcome in record["outcomes"]:
        if outcome["name"] == name and target in outcome.get("target_entity_ids", []):
            outcome["fact"]["evidence_ids"] = unique(outcome["fact"]["evidence_ids"] + evid(page))


records = []

# Page 7 opens with characterization continuing the page-6 1g resolution.
r = take("table1_entry7_1g_kinetic_resolution")
add_record_evidence(r, 7)
add_outcome_evidence(r, "product_ee", "kr_1g_R_acetate", 7)
r["notes"].append(fact("Page 7 continues characterization of (R)-2g from the page-6 experiment.", evid(7)))
records.append(r)

# Detailed kinetic resolutions for 1h and 1i, merged with the existing Table 1 rows.
for entry, label, product_masses in ((8, "1h", (50, 59)), (9, "1i", (42, 51))):
    suffix = f"table1_entry{entry}_{label}_kinetic_resolution"
    r = take(suffix)
    add_record_evidence(r, 7)
    set_amounts(r, f"kr_{label}_substrate", [field("mass", q(100, "mg"), evid(7))])
    set_amounts(r, f"kr_{label}_enzyme", [field("mass", q(70, "mg"), evid(7))])
    alcohol_id = f"kr_{label}_S_alcohol"
    acetate_id = f"kr_{label}_R_acetate"
    r["outcomes"] = [x for x in r["outcomes"] if x["name"] != "isolated_product_mass"]
    r["outcomes"].extend([
        field("isolated_product_mass", q(product_masses[0], "mg"), evid(7), [alcohol_id]),
        field("isolated_product_mass", q(product_masses[1], "mg"), evid(7), [acetate_id]),
    ])
    for outcome in r["outcomes"]:
        if outcome["name"] in {"isolated_yield", "product_ee"}:
            outcome["fact"]["evidence_ids"] = unique(outcome["fact"]["evidence_ids"] + evid(7))
    r["review"]["unresolved"] = [
        "No explicitly associated Supporting Information was supplied.",
        "Candidate structures remain unverified.",
    ]
    records.append(r)

# Page 7 section 3.2.10 supplies the exact hydrolysis procedure previously mentioned on page 3.
r = take("page3_R2a_hydrolysis_to_R1a")
add_record_evidence(r, 7)
set_amounts(r, "hyd_R2a", [
    field("mass", q(0.49, "g"), evid(7)),
    field("amount", q(2.55, "mmol"), evid(7)),
    field("input_ee", q(99, "%"), evid(7)),
])
set_amounts(r, "hyd_k2co3", [
    field("mass", q(0.35, "g"), evid(7)),
    field("amount", q(2.55, "mmol"), evid(7)),
])
set_amounts(r, "hyd_meoh", [field("volume", q(5, "mL"), evid(7))])
r["steps"] = [{
    "step_id": "hydrolysis",
    "participant_ids": ["hyd_R2a", "hyd_k2co3", "hyd_meoh"],
    "conditions": [
        field("temperature", "r.t.", evid(7)),
        field("time", q(9, "h"), evid(7)),
        field("operation", "stirred and monitored by TLC", evid(7)),
        field("workup", "filtered, washed with ethyl ether, and evaporated", evid(7)),
        field("purification", "flash chromatography on silica gel; petroleum ether/ethyl ether 10:1", evid(7)),
    ],
}]
r["outcomes"] = [
    field("isolated_product_mass", q(0.31, "g"), evid(7), ["hyd_R1a"]),
    field("isolated_yield", q(82, "%"), evid(7), ["hyd_R1a"]),
    field("product_ee", q(99, "%"), evid(7), ["hyd_R1a"]),
]
r["review"]["unresolved"] = [
    "No explicitly associated Supporting Information was supplied.",
    "Candidate structures remain unverified.",
]
records.append(r)

# Sections 3.3.1-3.3.8: detailed quantities supplement the existing Table 3 rows.
scope = {
    1: dict(page=7, product="3a", sub=(75, 0.5, 99), cui=(2.2, 0.01), pd=(6.9, 0.01),
            base=(0.07, 0.5), aryl_mass=None, aryl_volume=0.08, aryl_amount=0.7,
            thf=2, product_mass=97, yld=86, ee=98),
    2: dict(page=7, product="3b", sub=(44, 0.29, 99), cui=(1.2, 0.006), pd=(4.1, 0.006),
            base=(0.04, 0.3), aryl_mass=85, aryl_volume=None, aryl_amount=0.32,
            thf=1.2, product_mass=76, yld=92, ee=99),
    3: dict(page=8, product="3c", sub=(45, 0.3, 99), cui=(1.2, 0.006), pd=(4.1, 0.006),
            base=(0.04, 0.3), aryl_mass=85, aryl_volume=None, aryl_amount=0.33,
            thf=1.2, product_mass=70, yld=86, ee=99),
    4: dict(page=8, product="3d", sub=(40, 0.27, 98), cui=(1.0, 0.005), pd=(4.0, 0.006),
            base=(0.04, 0.3), aryl_mass=72, aryl_volume=None, aryl_amount=0.33,
            thf=1, product_mass=55, yld=86, ee=98),
    5: dict(page=8, product="3e", sub=(47, 0.31, 98), cui=(1.3, 0.007), pd=(4.2, 0.006),
            base=(0.05, 0.36), aryl_mass=77, aryl_volume=None, aryl_amount=0.33,
            thf=1, product_mass=67, yld=84, ee=98),
    6: dict(page=8, product="3f", sub=(48, 0.32, 98), cui=(1.4, 0.007), pd=(5.0, 0.007),
            base=(0.05, 0.36), aryl_mass=94, aryl_volume=None, aryl_amount=0.33,
            thf=2, product_mass=78, yld=80, ee=98),
    7: dict(page=8, product="3g", sub=(43, 0.29, 98), cui=(1.4, 0.007), pd=(4.3, 0.006),
            base=(0.05, 0.36), aryl_mass=75, aryl_volume=None, aryl_amount=0.33,
            thf=1, product_mass=62, yld=86, ee=98),
    8: dict(page=8, product="3h", sub=(73, 0.49, 98), cui=(2.0, 0.01), pd=(7.0, 0.01),
            base=(0.07, 0.5), aryl_mass=None, aryl_volume=0.075, aryl_amount=0.59,
            thf=2, product_mass=103, yld=87, ee=97),
}

for entry, details in scope.items():
    product = details["product"]
    r = take(f"table3_entry{entry}_{product}_aryl_scope")
    page = details["page"]
    e = evid(page)
    add_record_evidence(r, page)
    prefix = f"t3e{entry}"
    set_amounts(r, prefix + "_1a", [
        field("mass", q(details["sub"][0], "mg"), e),
        field("amount", q(details["sub"][1], "mmol"), e),
        field("input_ee", q(details["sub"][2], "%"), e),
    ])
    set_amounts(r, prefix + "_cui", [
        field("mass", q(details["cui"][0], "mg"), e),
        field("amount", q(details["cui"][1], "mmol"), e),
    ])
    set_amounts(r, prefix + "_pd", [
        field("mass", q(details["pd"][0], "mg"), e),
        field("amount", q(details["pd"][1], "mmol"), e),
    ])
    set_amounts(r, prefix + "_base", [
        field("volume", q(details["base"][0], "mL"), e),
        field("amount", q(details["base"][1], "mmol"), e),
    ])
    aryl_amounts = [field("amount", q(details["aryl_amount"], "mmol"), e)]
    if details["aryl_mass"] is not None:
        aryl_amounts.insert(0, field("mass", q(details["aryl_mass"], "mg"), e))
    if details["aryl_volume"] is not None:
        aryl_amounts.insert(0, field("volume", q(details["aryl_volume"], "mL"), e))
    set_amounts(r, prefix + "_aryl", aryl_amounts)
    set_amounts(r, prefix + "_thf", [field("volume", q(details["thf"], "mL"), e)])
    r["outcomes"] = [x for x in r["outcomes"] if x["name"] != "isolated_product_mass"]
    for outcome in r["outcomes"]:
        if outcome["name"] in {"isolated_yield", "product_ee"}:
            outcome["fact"]["evidence_ids"] = unique(outcome["fact"]["evidence_ids"] + e)
    r["outcomes"].append(field("isolated_product_mass", q(details["product_mass"], "mg"), e, [prefix + "_product"]))
    if entry == 1:
        r["steps"][0]["conditions"].extend([
            field("atmosphere", "nitrogen", e),
            field("operation", "i-Pr2NH added to the mixture; stirred while monitored by TLC", e),
            field("workup", "filtered, washed with ethyl ether, and evaporated", e),
            field("purification", "flash chromatography on silica gel; petroleum ether/ethyl ether 10:1; column prewashed with petroleum ether/i-Pr2NH 100:1", e),
        ])
        unresolved = [
            "No explicitly associated Supporting Information was supplied.",
            "Candidate structures remain unverified.",
        ]
    else:
        unresolved = [
            "The individual procedure reports quantities and outcomes but does not restate temperature, duration, workup, or purification; temperature and time remain sourced from Table 3 on page 4.",
            "No explicitly associated Supporting Information was supplied.",
            "Candidate structures remain unverified.",
        ]
    r["review"]["unresolved"] = unresolved
    records.append(r)

# Page 8-9 section 3.4.1: replace the scheme-only 4a record with its full three-stage procedure.
e8 = evid(8)
e9 = evid(9)
e49 = unique(evid(4) + e8 + e9)
r = take("scheme3_4a_multistep_alkylation")
r["evidence_ids"] = unique(r["evidence_ids"] + e8 + e9)
r["participants"] = [
    participant("s3_4a_S1a", "reactant", "(S)-1a", "(S)-4-(n-butyl)hexa-4,5-dien-1-yn-3-ol", e8, "C=C=C(CCCC)C(O)C#C", [field("mass", q(73, "mg"), e8), field("amount", q(0.49, "mmol"), e8), field("input_ee", q(98, "%"), e8)]),
    participant("s3_4a_vinyl_ether", "reactant", "vinyl ethyl ether", "ethyl vinyl ether", e8, "CCOC=C", [field("volume", q(0.072, "mL"), e8), field("amount", q(0.75, "mmol"), e8)]),
    participant("s3_4a_ch2cl2", "solvent", "CH2Cl2", "dichloromethane", e8, "ClCCl", [field("volume", q(1, "mL"), e8)]),
    participant("s3_4a_ppts1", "reagent", "PPTS", "pyridinium p-toluenesulfonate", e8, None, [field("mass", q(14, "mg"), e8), field("amount", q(0.05, "mmol"), e8)]),
    participant("s3_4a_5", "product", "5", "protected intermediate 5", e9),
    participant("s3_4a_thf", "solvent", "THF", "tetrahydrofuran", e9, "C1CCOC1", [field("volume", q(1, "mL"), e9)]),
    participant("s3_4a_nbuli", "reagent", "n-BuLi", "n-butyllithium", e9, "[Li]CCCC", [field("volume", q(0.31, "mL"), e9), field("concentration", q(1.6, "M"), e9)]),
    participant("s3_4a_hmpa", "reagent", "HMPA", "hexamethylphosphoramide", e9, "CN(C)P(=O)(N(C)C)N(C)C", [field("volume", q(10, "uL"), e9)]),
    participant("s3_4a_mei", "reactant", "CH3I", "methyl iodide", e9, "CI", [field("amount", q(0.75, "mmol"), e9)]),
    participant("s3_4a_6", "product", "6a", "alkylated protected intermediate 6a", e9),
    participant("s3_4a_meoh", "solvent", "CH3OH", "methanol", e9, "CO", [field("volume", q(2, "mL"), e9)]),
    participant("s3_4a_ppts2", "reagent", "PPTS", "pyridinium p-toluenesulfonate", e9, None, [field("mass", q(14, "mg"), e9), field("amount", q(0.05, "mmol"), e9)]),
    participant("s3_4a_product", "product", "(S)-(+)-4a", "(S)-(+)-3-(n-butyl)hepta-1,2-dien-5-yn-4-ol", e9, "C=C=C(CCCC)C(O)C#CC"),
]
r["steps"] = [
    {"step_id": "protection", "participant_ids": ["s3_4a_S1a", "s3_4a_vinyl_ether", "s3_4a_ch2cl2", "s3_4a_ppts1", "s3_4a_5"], "conditions": [field("temperature", "r.t.", e8), field("time", q(4.5, "h"), e9), field("operation", "stirred while monitored by TLC", e9), field("workup", "evaporated", e9), field("purification", "flash chromatography on silica gel; petroleum ether/ethyl ether 40:1", e9)]},
    {"step_id": "deprotonation", "participant_ids": ["s3_4a_5", "s3_4a_thf", "s3_4a_nbuli"], "conditions": [field("atmosphere", "nitrogen", e9), field("temperature", q(-78, "°C"), e9), field("time", q(1, "h"), e9)]},
    {"step_id": "alkylation", "participant_ids": ["s3_4a_5", "s3_4a_nbuli", "s3_4a_hmpa", "s3_4a_mei", "s3_4a_6"], "conditions": [field("temperature", "r.t.", e9), field("time", q(13.5, "h"), e9), field("operation", "HMPA and CH3I added subsequently; mixture stirred", e9), field("workup", "saturated brine added; extracted with ethyl ether (20 mL x3), dried over anhydrous Na2SO4, and evaporated", e9), field("purification", "chromatography on silica gel", e9)]},
    {"step_id": "deprotection", "participant_ids": ["s3_4a_6", "s3_4a_meoh", "s3_4a_ppts2", "s3_4a_product"], "conditions": [field("temperature", "r.t.", e9), field("time", q(3, "h"), e9), field("workup", "evaporated", e9), field("purification", "flash chromatography on silica gel; petroleum ether/ethyl ether 10:1", e9)]},
]
r["outcomes"] = [
    field("isolated_product_mass", q(60, "mg"), e9, ["s3_4a_product"]),
    field("total_yield", q(75, "%"), unique(evid(4) + e9), ["s3_4a_product"]),
    field("product_ee", q(98, "%"), unique(evid(4) + e9), ["s3_4a_product"]),
]
r["notes"] = [fact("The 75% value is reported as a total yield in Scheme 3 and as the isolated final-product yield in section 3.4.1.", unique(evid(4) + e9))]
r["review"]["unresolved"] = [
    "Intermediate structures 5 and 6a are not specified in enough detail in the prose and remain without SMILES.",
    "No explicitly associated Supporting Information was supplied.",
    "Candidate structures remain unverified.",
]
records.append(r)

# Page 9 section 3.4.2: retain missing stage conditions and the source's 62%/63% yield conflict.
r = take("scheme3_4b_multistep_alkylation")
r["evidence_ids"] = unique(r["evidence_ids"] + e9)
r["participants"] = [
    participant("s3_4b_S1a", "reactant", "(S)-1a", "(S)-4-(n-butyl)hexa-4,5-dien-1-yn-3-ol", e9, "C=C=C(CCCC)C(O)C#C", [field("mass", q(78, "mg"), e9), field("amount", q(0.52, "mmol"), e9), field("input_ee", q(98, "%"), e9)]),
    participant("s3_4b_vinyl_ether", "reactant", "vinyl ethyl ether", "ethyl vinyl ether", e9, "CCOC=C", [field("volume", q(0.08, "mL"), e9), field("amount", q(0.83, "mmol"), e9)]),
    participant("s3_4b_ch2cl2", "solvent", "CH2Cl2", "dichloromethane", e9, "ClCCl", [field("volume", q(1, "mL"), e9)]),
    participant("s3_4b_ppts1", "reagent", "PPTS", "pyridinium p-toluenesulfonate", e9, None, [field("mass", q(14, "mg"), e9), field("amount", None)]),
    participant("s3_4b_5", "product", "5", "protected intermediate 5", e9),
    participant("s3_4b_nbuli", "reagent", "n-BuLi", "n-butyllithium", e9, "[Li]CCCC", [field("volume", q(0.33, "mL"), e9), field("concentration", q(1.6, "M"), e9)]),
    participant("s3_4b_hmpa", "reagent", "HMPA", "hexamethylphosphoramide", e9, "CN(C)P(=O)(N(C)C)N(C)C", [field("volume", q(10, "uL"), e9)]),
    participant("s3_4b_eti", "reactant", "CH3CH2I", "ethyl iodide", e9, "CCI", [field("amount", q(0.78, "mmol"), e9)]),
    participant("s3_4b_6", "product", "6b", "alkylated protected intermediate 6b", e9),
    participant("s3_4b_meoh", "solvent", "CH3OH", "methanol", e9, "CO", [field("volume", q(1, "mL"), e9)]),
    participant("s3_4b_ppts2", "reagent", "PPTS", "pyridinium p-toluenesulfonate", e9, None, [field("mass", q(14, "mg"), e9), field("amount", q(0.05, "mmol"), e9)]),
    participant("s3_4b_product", "product", "(S)-4b", "(S)-4-(n-butyl)oct-1,2-diene-5-yn-4-ol", e9, "C=C=C(CCCC)C(O)C#CCC"),
]
r["steps"] = [
    {"step_id": "protection", "participant_ids": ["s3_4b_S1a", "s3_4b_vinyl_ether", "s3_4b_ch2cl2", "s3_4b_ppts1", "s3_4b_5"], "conditions": [field("temperature", None), field("time", None), field("operation", "reacted to afford compound 5", e9)]},
    {"step_id": "alkylation", "participant_ids": ["s3_4b_5", "s3_4b_nbuli", "s3_4b_hmpa", "s3_4b_eti", "s3_4b_6"], "conditions": [field("temperature", None), field("time", None), field("operation", "reacted to afford compound 6b", e9)]},
    {"step_id": "deprotection", "participant_ids": ["s3_4b_6", "s3_4b_meoh", "s3_4b_ppts2", "s3_4b_product"], "conditions": [field("temperature", None), field("time", None), field("operation", "reacted to afford (S)-4b", e9)]},
]
r["outcomes"] = [
    field("isolated_product_mass", q(59, "mg"), e9, ["s3_4b_product"]),
    field("scheme_total_yield", q(62, "%"), evid(4), ["s3_4b_product"]),
    field("section_3.4.2_yield", q(63, "%"), e9, ["s3_4b_product"]),
    field("product_ee", None, targets=["s3_4b_product"]),
]
r["notes"] = [
    fact("Scheme 3 reports 62% total yield, whereas section 3.4.2 reports 59 mg (63%); both source values are retained.", unique(evid(4) + e9)),
    fact("The first PPTS amount is printed as '(14 mg, 0.05)' without a unit; the numeric amount is not forced into mmol.", e9),
]
r["review"]["unresolved"] = [
    "The 62% Scheme 3 yield conflicts with the 63% yield in section 3.4.2.",
    "The unit for the first-stage PPTS value 0.05 is missing in the source.",
    "Section 3.4.2 does not restate stage temperatures, durations, workups, or purifications; these were not imported by analogy from the 4a typical procedure.",
    "Product 4b ee is not reported.",
    "Intermediate structures 5 and 6b remain without SMILES.",
    "No explicitly associated Supporting Information was supplied.",
    "Candidate structures remain unverified.",
]
records.append(r)

if len(records) != 14:
    raise RuntimeError(f"expected 14 updated records, found {len(records)}")

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")

coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 7,
            "state": "attempted",
            "regions": [
                {"region": "upper-left continuation of section 3.2.7", "finding": "Characterization of acetate (R)-2g continues from page 6; merged with the existing 1g kinetic-resolution record rather than counted as a new experiment.", "evidence_ids": evid(7)},
                {"region": "left column sections 3.2.8-3.2.9", "finding": "Detailed kinetic-resolution outcomes for 1h and 1i, including product masses and ee values; merged with Table 1 entries 8 and 9.", "evidence_ids": evid(7)},
                {"region": "upper-right section 3.2.10", "finding": "Distinct hydrolysis of (R)-2a to (R)-1a with exact quantities, 9 h at room temperature, workup, 82% yield, and 99% ee; enriches the page-3 prose record.", "evidence_ids": evid(7)},
                {"region": "right column sections 3.3.1-3.3.2", "finding": "Detailed Sonogashira procedures for products 3a and 3b; merged with existing Table 3 scope rows.", "evidence_ids": evid(7)},
            ],
            "record_ids": [
                f"{DOC}:table1_entry7_1g_kinetic_resolution",
                f"{DOC}:table1_entry8_1h_kinetic_resolution",
                f"{DOC}:table1_entry9_1i_kinetic_resolution",
                f"{DOC}:page3_R2a_hydrolysis_to_R1a",
                f"{DOC}:table3_entry1_3a_aryl_scope",
                f"{DOC}:table3_entry2_3b_aryl_scope",
            ],
            "unresolved": [
                "The page contains characterization data beyond the reaction fields represented by the current schema.",
                "Machine-proposed structures remain unverified.",
            ],
        },
        {
            "page": 8,
            "state": "attempted",
            "regions": [
                {"region": "sections 3.3.3-3.3.8 across both columns", "finding": "Six detailed Sonogashira scope procedures for products 3c-3h with reagent quantities, product masses, yields, and ee values; merged with existing Table 3 rows.", "evidence_ids": evid(8)},
                {"region": "lower-right beginning of section 3.4.1", "finding": "First protection stage of the multistep 4a synthesis begins, giving (S)-1a, vinyl ethyl ether, PPTS, CH2Cl2, and room temperature; the experiment continues on page 9.", "evidence_ids": evid(8)},
            ],
            "record_ids": [
                f"{DOC}:table3_entry3_3c_aryl_scope",
                f"{DOC}:table3_entry4_3d_aryl_scope",
                f"{DOC}:table3_entry5_3e_aryl_scope",
                f"{DOC}:table3_entry6_3f_aryl_scope",
                f"{DOC}:table3_entry7_3g_aryl_scope",
                f"{DOC}:table3_entry8_3h_aryl_scope",
                f"{DOC}:scheme3_4a_multistep_alkylation",
            ],
            "unresolved": [
                "Procedures 3b-3h do not restate the Table 3 temperature/time or the typical workup and purification.",
                "The 4a experiment continues on page 9.",
            ],
        },
        {
            "page": 9,
            "state": "attempted",
            "regions": [
                {"region": "upper-left continuation of section 3.4.1", "finding": "Completion of the three-stage 4a protection/deprotonation-alkylation/deprotection sequence, including stage times, temperatures, workups, 60 mg (75%) product, and 98% ee.", "evidence_ids": evid(9)},
                {"region": "middle-left section 3.4.2", "finding": "Three-stage 4b sequence with explicit reagent quantities and 59 mg (63%) final product; most stage conditions are not restated and remain missing.", "evidence_ids": evid(9)},
                {"region": "lower-left acknowledgements and right-column references 1-12", "finding": "Acknowledgements and cited literature only; no additional reported experiment records created.", "evidence_ids": evid(9)},
            ],
            "record_ids": [
                f"{DOC}:scheme3_4a_multistep_alkylation",
                f"{DOC}:scheme3_4b_multistep_alkylation",
            ],
            "unresolved": [
                "Scheme 3 gives 62% total yield for 4b while section 3.4.2 gives 63%; both values are retained.",
                "The first-stage 4b PPTS amount is printed as 0.05 without a unit.",
                "No ee is reported for 4b.",
            ],
        },
        {
            "page": 10,
            "state": "attempted",
            "regions": [
                {"region": "reference list 12-18", "finding": "Reference citations only, including prior kinetic-resolution, starting-material, lipase-structure, selectivity-rule, Sonogashira, and literature-compound sources; these are cited works rather than experiments reported in this paper.", "evidence_ids": evid(10)},
                {"region": "remaining lower page", "finding": "Blank page area; no figures, tables, arrows, footnotes, or experimental prose.", "evidence_ids": [f"{DOC}:page10:image"]},
            ],
            "record_ids": [],
            "unresolved": [],
        },
    ],
}
COVERAGE.parent.mkdir(parents=True, exist_ok=True)
COVERAGE.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

tasks = json.loads(TASKS.read_text())
for task in tasks:
    page = int(task["evidence_id"].split(":page", 1)[1].split(":", 1)[0])
    if 7 <= page <= 10:
        task["state"] = "attempted"
        task["visual_evidence_id"] = f"{DOC}:page{page}:image"
        task["reason"] = "Original page image visually inspected; findings and record links are in coverage/pages_0007_0010.json."
TASKS.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"updated_records": len(records), "coverage_pages": [7, 8, 9, 10], "output": str(OUT)}, ensure_ascii=False))
