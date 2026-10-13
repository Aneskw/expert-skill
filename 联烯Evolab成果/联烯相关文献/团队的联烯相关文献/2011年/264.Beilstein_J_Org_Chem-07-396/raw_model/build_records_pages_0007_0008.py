#!/usr/bin/env python3
"""Enrich existing Gao et al. records from original PDF pages 7--8."""

from __future__ import annotations

import copy
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
CURRENT = ROOT / "runs/current"
DOC = "doc_a5dd7894e70ecebe"
P7 = [f"{DOC}:page7:text", f"{DOC}:page7:image"]
P8 = [f"{DOC}:page8:text", f"{DOC}:page8:image"]


def fact(value, evidence_ids):
    return {
        "value": value,
        "evidence_ids": list(evidence_ids),
        "verification": "missing" if value is None else "unreviewed",
    }


def qty(number, unit, raw_text=None):
    value = {"number": number, "unit": unit}
    if raw_text is not None:
        value["raw_text"] = raw_text
    return value


def amount(name, value, evidence_ids):
    return {"name": name, "fact": fact(value, evidence_ids)}


def add_unique(target, values):
    for value in values:
        if value not in target:
            target.append(value)


def participant(rec, entity_id):
    return next(p for p in rec["participants"] if p["entity_id"] == entity_id)


def condition(rec, name):
    return next(c for c in rec["steps"][0]["conditions"] if c["name"] == name)


def outcome(rec, name):
    return next(o for o in rec["outcomes"] if o["name"] == name)


def update_identity(p, *, label=None, name=None, smiles=None):
    if label is not None:
        p["label"] = fact(label, P7)
    if name is not None:
        p["name"] = fact(name, P7)
    if smiles is not None:
        p["smiles"] = fact(smiles, P7)
        p["smiles_parseable"] = None
        p["structure_verified"] = False


def set_amounts(p, specs):
    p["amounts"] = [amount(name, value, evidence_ids) for name, value, evidence_ids in specs]


dataset = json.loads((CURRENT / "dataset.json").read_text())
by_id = {r["record_id"]: copy.deepcopy(r) for r in dataset["experiments"]}


# Page 7, upper left: detailed 2j batch. This is the same experiment as
# Table 5 entry 10, not a new reaction.
rid_2j = f"{DOC}:table5_entry10_1j_to_2j"
r = by_id[rid_2j]
add_unique(r["evidence_ids"], P7)
sub = participant(r, "substrate")
prod = participant(r, "product")
update_identity(
    sub,
    label="1j",
    name="2-butyl-1-phenylnona-2,3-dien-1-ol",
    smiles="OC(c1ccccc1)C(CCCC)=C=CCCCCC",
)
update_identity(
    prod,
    label="2j",
    name="2-butyl-1-phenylnona-2,3-dien-1-one",
    smiles="O=C(c1ccccc1)C(CCCC)=C=CCCCCC",
)
set_amounts(sub, [("mass", qty(82.2, "mg"), P7), ("amount", qty(0.3, "mmol"), P7)])
set_amounts(prod, [("mass", qty(74.8, "mg"), P7)])
set_amounts(participant(r, "phen"), [("mass", qty(5.6, "mg"), P7), ("amount", qty(0.03, "mmol"), P7), ("loading", qty(10, "mol%"), r["evidence_ids"][:2])])
set_amounts(participant(r, "bpy"), [("mass", qty(4.9, "mg"), P7), ("amount", qty(0.03, "mmol"), P7), ("loading", qty(10, "mol%"), r["evidence_ids"][:2])])
set_amounts(participant(r, "cucl"), [("mass", qty(6.2, "mg"), P7), ("amount", qty(0.06, "mmol"), P7), ("loading", qty(20, "mol%"), r["evidence_ids"][:2])])
set_amounts(participant(r, "k2co3"), [("mass", qty(21.5, "mg"), P7), ("amount", qty(0.15, "mmol"), P7), ("equivalents", qty(0.5, "equiv"), r["evidence_ids"][:2])])
set_amounts(participant(r, "dbad"), [("mass", qty(14.1, "mg"), P7), ("amount", qty(0.06, "mmol"), P7), ("loading", qty(20, "mol%"), r["evidence_ids"][:2])])
participant(r, "toluene")["label"] = fact("dry toluene", P7)
set_amounts(participant(r, "toluene"), [("initial_volume", qty(1.5, "mL"), P7), ("substrate_solution_volume", qty(1.5, "mL"), P7)])
add_unique(outcome(r, "isolated_yield")["fact"]["evidence_ids"], P7)
add_unique(outcome(r, "yield_measurement_basis")["fact"]["evidence_ids"], P7)
r["review"]["unresolved"] = [
    "The abbreviated 2j paragraph does not explicitly restate workup or purification.",
    "Supporting Information is mentioned on page 7 but was not supplied or explicitly associated.",
    "Candidate substrate/product structures are not source-verified.",
]
by_id[rid_2j] = r


# Page 7, middle left: the exact gram-scale 2k charges and isolated mass enrich
# Scheme 1. Conditions remain sourced from Scheme 1 on page 4.
rid_2k = f"{DOC}:scheme1_gram_scale_1k_to_2k"
r = by_id[rid_2k]
add_unique(r["evidence_ids"], P7)
sub = participant(r, "substrate_1k")
prod = participant(r, "product_2k")
add_unique(sub["label"]["evidence_ids"], P7)
add_unique(sub["name"]["evidence_ids"], P7)
add_unique(prod["label"]["evidence_ids"], P7)
add_unique(prod["name"]["evidence_ids"], P7)
set_amounts(sub, [("mass", qty(1.0141, "g"), P7), ("amount", qty(5.4, "mmol"), P7)])
set_amounts(prod, [("mass", qty(0.7512, "g"), P7)])
set_amounts(participant(r, "phen"), [("mass", qty(49.1, "mg"), P7), ("amount", qty(0.27, "mmol"), P7), ("loading", qty(5, "mol%"), r["evidence_ids"][:2])])
set_amounts(participant(r, "bpy"), [("mass", qty(42.6, "mg"), P7), ("amount", qty(0.27, "mmol"), P7), ("loading", qty(5, "mol%"), r["evidence_ids"][:2])])
set_amounts(participant(r, "cucl"), [("mass", qty(54.2, "mg"), P7), ("amount", qty(0.54, "mmol"), P7), ("loading", qty(10, "mol%"), r["evidence_ids"][:2])])
set_amounts(participant(r, "base"), [("mass", qty(373.8, "mg"), P7), ("amount", qty(2.7, "mmol"), P7), ("equivalents", qty(0.5, "equiv"), r["evidence_ids"][:2])])
set_amounts(participant(r, "dbad"), [("mass", qty(124.4, "mg"), P7), ("amount", qty(0.54, "mmol"), P7), ("loading", qty(10, "mol%"), r["evidence_ids"][:2])])
participant(r, "solvent")["label"] = fact("dry toluene", P7)
set_amounts(participant(r, "solvent"), [("initial_volume", qty(9, "mL"), P7), ("substrate_solution_volume", qty(9, "mL"), P7)])
conditions = r["steps"][0]["conditions"]
conditions[:] = [c for c in conditions if c["name"] != "solvent_volume"]
add_unique(outcome(r, "reported_product_yield")["fact"]["evidence_ids"], P7)
r["review"]["unresolved"] = [
    "The detailed 2k paragraph does not explicitly state the yield measurement basis, workup, or purification.",
    "Supporting Information is mentioned on page 7 but was not supplied or explicitly associated.",
    "Candidate substrate/product structures are not source-verified.",
]
by_id[rid_2k] = r


# Page 7, lower left and upper right: complete typical procedure for 2l.
rid_2l = f"{DOC}:scheme2_1l_to_2l"
r = by_id[rid_2l]
add_unique(r["evidence_ids"], P7)
sub = participant(r, "substrate")
prod = participant(r, "product")
for p in (sub, prod):
    add_unique(p["label"]["evidence_ids"], P7)
    add_unique(p["name"]["evidence_ids"], P7)
set_amounts(sub, [("mass", qty(63.8, "mg"), P7), ("amount", qty(0.3, "mmol"), P7)])
set_amounts(prod, [("mass", qty(37.1, "mg"), P7)])
set_amounts(participant(r, "phen"), [("mass", qty(6.9, "mg"), P7), ("amount", qty(0.0375, "mmol"), P7), ("loading", qty(12.5, "mol%"), r["evidence_ids"][:4])])
set_amounts(participant(r, "bpy"), [("mass", qty(5.8, "mg"), P7), ("amount", qty(0.0375, "mmol"), P7), ("loading", qty(12.5, "mol%"), r["evidence_ids"][:4])])
set_amounts(participant(r, "cucl"), [("mass", qty(5.9, "mg"), P7), ("amount", qty(0.06, "mmol"), P7), ("loading", qty(20, "mol%"), r["evidence_ids"][:4])])
set_amounts(participant(r, "base"), [("mass", qty(20.9, "mg"), P7), ("amount", qty(0.15, "mmol"), P7), ("equivalents", qty(0.5, "equiv"), r["evidence_ids"][:4])])
set_amounts(participant(r, "dbad"), [("mass", qty(14.0, "mg"), P7), ("amount", qty(0.06, "mmol"), P7), ("loading", qty(20, "mol%"), r["evidence_ids"][:4])])
participant(r, "solvent")["label"] = fact("dry toluene", P7)
set_amounts(participant(r, "solvent"), [("initial_volume", qty(1.5, "mL"), P7), ("substrate_solution_volume", qty(1.5, "mL"), P7)])
conditions = [
    c for c in r["steps"][0]["conditions"]
    if c["name"] not in {"reaction_scale", "solvent_volume", "workup", "purification"}
]
for name in ("temperature", "time"):
    add_unique(next(c for c in conditions if c["name"] == name)["fact"]["evidence_ids"], P7)
conditions.extend([
    {"name": "vessel_preparation", "fact": fact("Oven-dried Schlenk tube; purged with air and refilled with oxygen twice.", P7)},
    {"name": "catalyst_prestir_temperature", "fact": fact("r.t.", P7)},
    {"name": "catalyst_prestir_time", "fact": fact(qty(0.5, "h"), P7)},
    {"name": "workup", "fact": fact("Filter through silica gel (100–140 mesh), wash with diethyl ether, and evaporate the solvent.", P7)},
    {"name": "purification", "fact": fact("Flash chromatography on silica gel; petroleum ether/ether = 50:1.", P7)},
])
r["steps"][0]["conditions"] = conditions
for name in ("conversion", "isolated_yield", "yield_measurement_basis", "yield_based_on_starting_material_consumed"):
    add_unique(outcome(r, name)["fact"]["evidence_ids"], P7)
r["review"]["unresolved"] = [
    "Supporting Information is mentioned on page 7 but was not supplied or explicitly associated.",
    "Candidate substrate/product structures are not source-verified.",
]
by_id[rid_2l] = r


# Page 7, upper right: exact 2m charges and result. The abbreviated paragraph
# does not restate 2l's vessel-conditioning, workup, or chromatography.
rid_2m = f"{DOC}:scheme2_1m_to_2m"
r = by_id[rid_2m]
add_unique(r["evidence_ids"], P7)
sub = participant(r, "substrate")
prod = participant(r, "product")
for p in (sub, prod):
    add_unique(p["label"]["evidence_ids"], P7)
    add_unique(p["name"]["evidence_ids"], P7)
set_amounts(sub, [("mass", qty(72.7, "mg"), P7), ("amount", qty(0.3, "mmol"), P7)])
set_amounts(prod, [("mass", qty(43.8, "mg"), P7)])
set_amounts(participant(r, "phen"), [("mass", qty(6.9, "mg"), P7), ("amount", qty(0.0375, "mmol"), P7), ("loading", qty(12.5, "mol%"), r["evidence_ids"][:4])])
set_amounts(participant(r, "bpy"), [("mass", qty(5.9, "mg"), P7), ("amount", qty(0.0375, "mmol"), P7), ("loading", qty(12.5, "mol%"), r["evidence_ids"][:4])])
set_amounts(participant(r, "cucl"), [("mass", qty(6.1, "mg"), P7), ("amount", qty(0.06, "mmol"), P7), ("loading", qty(20, "mol%"), r["evidence_ids"][:4])])
set_amounts(participant(r, "base"), [("mass", qty(21.4, "mg"), P7), ("amount", qty(0.15, "mmol"), P7), ("equivalents", qty(0.5, "equiv"), r["evidence_ids"][:4])])
set_amounts(participant(r, "dbad"), [("mass", qty(13.9, "mg"), P7), ("amount", qty(0.06, "mmol"), P7), ("loading", qty(20, "mol%"), r["evidence_ids"][:4])])
participant(r, "solvent")["label"] = fact("dry toluene", P7)
set_amounts(participant(r, "solvent"), [("initial_volume", qty(1.5, "mL"), P7), ("substrate_solution_volume", qty(1.5, "mL"), P7)])
r["steps"][0]["conditions"] = [
    c for c in r["steps"][0]["conditions"]
    if c["name"] not in {"reaction_scale", "solvent_volume"}
]
for name in ("conversion", "isolated_yield", "yield_measurement_basis", "yield_based_on_starting_material_consumed"):
    add_unique(outcome(r, name)["fact"]["evidence_ids"], P7)
r["review"]["unresolved"] = [
    "The abbreviated 2m paragraph does not explicitly restate vessel conditioning, catalyst prestir, workup, or purification; these remain missing rather than inherited from 2l.",
    "Supporting Information is mentioned on page 7 but was not supplied or explicitly associated.",
    "Candidate substrate/product structures are not source-verified.",
]
by_id[rid_2m] = r


updated_ids = [rid_2j, rid_2k, rid_2l, rid_2m]
records = [by_id[rid] for rid in updated_ids]
(OUT / "records_pages_0007_0008.json").write_text(
    json.dumps(records, ensure_ascii=False, indent=2) + "\n"
)


coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 7,
            "state": "attempted",
            "regions": [
                {
                    "region": "upper-left 2j paragraph",
                    "finding": "Detailed charges and isolated product mass for the existing Table 5 entry 10 were merged into that record; characterization was not duplicated as an experiment.",
                    "evidence_ids": P7,
                },
                {
                    "region": "middle-left 2k paragraph",
                    "finding": "Exact gram-scale charges and product mass were merged into the existing Scheme 1 record; page 4 remains the source for pressure, temperature, and duration.",
                    "evidence_ids": P7,
                },
                {
                    "region": "lower-left through upper-right pure-oxygen procedure for 2l",
                    "finding": "The full 2l typical procedure was merged into the existing Scheme 2 record, including vessel preparation, prestir, exact charges, workup, chromatography, conversion, isolated yield, and yield based on consumed alcohol.",
                    "evidence_ids": P7,
                },
                {
                    "region": "upper-right 2m paragraph",
                    "finding": "Exact 2m charges, product mass, conversion, and yields were merged into the existing Scheme 2 record; operations not restated in this abbreviated paragraph remain missing.",
                    "evidence_ids": P7,
                },
                {
                    "region": "Supporting Information box and references 1–9",
                    "finding": "The page mentions an external spectra supplement but no SI was supplied or explicitly associated; references are prior literature and were not extracted as experiments from this paper.",
                    "evidence_ids": P7,
                },
            ],
            "record_ids": updated_ids,
            "unresolved": [
                "The mentioned Supporting Information file was not supplied or explicitly associated and was not imported.",
                "2j, 2k, and 2m abbreviated paragraphs do not explicitly restate all workup/purification operations.",
                "All candidate structures remain unverified machine interpretations.",
            ],
        },
        {
            "page": 8,
            "state": "attempted",
            "regions": [
                {
                    "region": "two-column references 10–44",
                    "finding": "Prior-literature citations only; no reaction arrow, table, experimental batch, or new result reported by this paper appears on the page.",
                    "evidence_ids": P8,
                },
                {
                    "region": "License and Terms box",
                    "finding": "Publication-license metadata only; no chemical experiment.",
                    "evidence_ids": P8,
                },
            ],
            "record_ids": [],
            "unresolved": [],
        },
    ],
}
coverage_dir = CURRENT / "coverage"
coverage_dir.mkdir(parents=True, exist_ok=True)
(coverage_dir / "pages_0007_0008.json").write_text(
    json.dumps(coverage, ensure_ascii=False, indent=2) + "\n"
)


tasks_path = CURRENT / "tasks.json"
tasks = json.loads(tasks_path.read_text())
for task in tasks:
    if task["task_id"] in {f"{DOC}:page7:text", f"{DOC}:page8:text"}:
        task["state"] = "attempted"
        task["reason"] = "Original page image and extracted page text inspected; page 7 continuations were merged and page 8 was classified as references/license only."
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"updated_records": len(records), "coverage_pages": [7, 8]}, ensure_ascii=False))
