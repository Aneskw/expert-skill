#!/usr/bin/env python3
"""Enrich existing jo0108616 records from visually inspected PDF pages 7-11."""
from __future__ import annotations

import copy
import json
from pathlib import Path


DOC = "doc_6d3edd1b61c89bf4"
ROOT = Path(__file__).resolve().parents[3]
DATASET = ROOT / "runs/current/dataset.json"
RAW = ROOT / "runs/current/raw_model/records_pages_0007_0011.json"
COVERAGE = ROOT / "runs/current/coverage/pages_0007_0011.json"
TASKS = ROOT / "runs/current/tasks.json"


def evid(*pages: int) -> list[str]:
    return [item for page in pages for item in (f"{DOC}:page{page}:image", f"{DOC}:page{page}:text")]


def fact(value, evidence_ids):
    return {
        "value": value,
        "evidence_ids": list(evidence_ids) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def quantity(number, unit):
    return {"number": number, "unit": unit}


def field(name, value, evidence_ids, targets=None):
    result = {"name": name, "fact": fact(value, evidence_ids)}
    if targets:
        result["target_entity_ids"] = list(targets)
    return result


data = json.loads(DATASET.read_text())
existing = {record["record_id"]: record for record in data["experiments"]}
updates: dict[str, dict] = {}


def rec(suffix: str) -> dict:
    record_id = f"{DOC}:{suffix}"
    if record_id not in updates:
        updates[record_id] = copy.deepcopy(existing[record_id])
    return updates[record_id]


def participant(record: dict, entity_id: str) -> dict:
    return next(item for item in record["participants"] if item["entity_id"] == entity_id)


def add_evidence(record: dict, pages: list[int]):
    record["evidence_ids"] = list(dict.fromkeys(record["evidence_ids"] + evid(*pages)))


def add_amount(item: dict, name: str, value, ev):
    for current in item["amounts"]:
        if current["name"] in (name, f"{name}_experimental_section_listing") and current["fact"]["value"] == value:
            return
    final_name = name
    if any(current["name"] == name for current in item["amounts"]):
        final_name = f"{name}_experimental_section_listing"
    item["amounts"].append(field(final_name, value, ev))


def set_yield(record: dict, entity_id: str, value, ev):
    candidates = [
        item for item in record["outcomes"]
        if item["name"].startswith("yield_") and entity_id in item.get("target_entity_ids", [])
    ]
    if len(candidates) == 1:
        candidates[0]["fact"] = fact(value, ev)
    elif len(candidates) == 0:
        record["outcomes"].append(field(f"experimental_section_yield_{entity_id}", value, ev, [entity_id]))
    else:
        raise ValueError(f"ambiguous yield target {record['record_id']} {entity_id}")


def set_basis(record: dict, text: str, ev):
    item = next((x for x in record["outcomes"] if x["name"] == "yield_measurement_basis"), None)
    if item is None:
        record["outcomes"].append(field("yield_measurement_basis", text, ev))
    else:
        item["fact"] = fact(text, ev)


def upsert_outcome(record: dict, item: dict):
    for index, current in enumerate(record["outcomes"]):
        if current["name"] == item["name"]:
            record["outcomes"][index] = item
            return
    record["outcomes"].append(item)


def upsert_step(record: dict, step: dict):
    for index, current in enumerate(record["steps"]):
        if current["step_id"] == step["step_id"]:
            record["steps"][index] = step
            return
    record["steps"].append(step)


def add_note(record: dict, text: str, ev):
    if not any(item["value"] == text for item in record["notes"]):
        record["notes"].append(fact(text, ev))


def add_unresolved(record: dict, text: str):
    if text not in record["review"]["unresolved"]:
        record["review"]["unresolved"].append(text)


def clean_review(record: dict):
    removed_starts = (
        "Yield measurement basis is not stated",
        "Reaction scale, atmosphere, workup, purification, and isolated mass",
        "Combined yield measurement basis is not stated",
    )
    record["review"]["unresolved"] = [
        item for item in record["review"]["unresolved"]
        if not item.startswith(removed_starts)
    ]
    reminder = (
        "The Experimental Section product paragraph supplies starting quantities and product mass, "
        "but does not independently restate every shared condition and workup detail."
    )
    if reminder not in record["review"]["unresolved"]:
        record["review"]["unresolved"].append(reminder)


PRODUCT_NAMES = {
    "2a": "1,1-bis(methoxycarbonyl)-2-(1′-phenylethenyl)cyclopropane",
    "2b": "1,1-bis(methoxycarbonyl)-2-(1′-(4′′-bromophenyl)ethenyl)cyclopropane",
    "2c": "1,1-bis(methoxycarbonyl)-2-(1′-(4′′-methylphenyl)ethenyl)cyclopropane",
    "2d": "1,1-bis(methoxycarbonyl)-2-(1′-(4′′-methoxyphenyl)ethenyl)cyclopropane",
    "2e": "(E)-1,1-bis(methoxycarbonyl)-2-(1′-methylene-3′-phenyl-2′-propenyl)cyclopropane",
    "2f": "1,1-bis(methoxycarbonyl)-2-(1′-naphthylethenyl)cyclopropane",
    "2g": "1,1-bis(methoxycarbonyl)-2-(1′-(4′′-methoxycarbonylphenyl)ethenyl)cyclopropane",
    "2h": "(E)-1,1-bis(methoxycarbonyl)-2-(1′-methylene-2′-heptenyl)cyclopropane",
    "2i": "1,1-bis(methoxycarbonyl)-2-benzyl-2-(1′-phenylethenyl)cyclopropane",
    "2j": "1,1-bis(methoxycarbonyl)-2-benzyl-2-(1′-(4′′-methoxyphenyl)ethenyl)cyclopropane",
    "2k": "1,1-bis(methoxycarbonyl)-2-benzyl-2-(1′-(4′′-methoxycarbonylphenyl)ethenyl)cyclopropane",
    "2l": "(E)-1,1-bis(methoxycarbonyl)-2-benzyl-2-(1′-methylene-3′-phenyl-2′-propenyl)cyclopropane",
    "2m": "(E)-1,1-bis(methoxycarbonyl)-2-benzyl-2-(1′-methylene-2′-heptenyl)cyclopropane",
    "2n": "(Z)-1,1-bis(methoxycarbonyl)-2-benzyl-2-(1′-methylene-2′-heptenyl)cyclopropane",
    "2o": "1,1-bis(methoxycarbonyl)-2-benzyl-2-(1′-(2′′-thienyl)ethenyl)cyclopropane",
    "2p": "1,1-bis(methoxycarbonyl)-2-propyl-2-(1′-phenylethenyl)cyclopropane",
    "2q": "1,1-bis(methoxycarbonyl)-2-propyl-2-(1′-(4′′-methoxyphenyl)ethenyl)cyclopropane",
    "2r": "1,1-bis(methoxycarbonyl)-2-propyl-2-(1′-(4′′-methoxycarbonylphenyl)ethenyl)cyclopropane",
    "2s": "(E)-1,1-bis(methoxycarbonyl)-2-propyl-2-(1′-methylene-3′-phenyl-2′-propenyl)cyclopropane",
    "2t": "(E)-1,1-bis(methoxycarbonyl)-2-propyl-2-(1′-methylene-2′-heptenyl)cyclopropane",
    "2u": "(Z)-1,1-bis(methoxycarbonyl)-2-propyl-2-(1′-methylene-2′-heptenyl)cyclopropane",
    "2v": "1,1-bis(methoxycarbonyl)-2-propyl-2-(1′-(2′′-thienyl)ethenyl)cyclopropane",
    "2w": "1,1-bis(methoxycarbonyl)-2-((1′-phenyl)oct-1′-enyl)cyclopropane",
    "2x": "1,1-bis(methoxycarbonyl)-2-(1′-(4′′-methylphenyl)oct-1′-enyl)cyclopropane",
    "2y": "1,1-bis(methoxycarbonyl)-2-(1′-(4′′-methoxyphenyl)oct-1′-enyl)cyclopropane",
    "2z": "1,1-bis(methoxycarbonyl)-2-(1′-(4′′-methoxycarbonylphenyl)oct-1′-enyl)cyclopropane",
    "2α": "1,1-bis(methoxycarbonyl)-2-(1′-((E)-2′′-phenylethenyl)oct-1′-enyl)cyclopropane",
    "2β": "1,1-bis(methoxycarbonyl)-2-methyl-2-((1′-phenyl)pent-1′-enyl)cyclopropane",
    "3β": "1-phenyl-2-methyl-4,4-bis(methoxycarbonyl)-5-propylcyclopentene",
    "3i": "1-phenyl-2-benzyl-4,4-bis(methoxycarbonyl)cyclopentene",
    "3γ": "1-(4′-methylphenyl)-2-benzyl-4,4-bis(methoxycarbonyl)cyclopentene",
    "3j": "1-(4′-methoxyphenyl)-2-benzyl-4,4-bis(methoxycarbonyl)cyclopentene",
    "3k": "1-(4′-methoxycarbonylphenyl)-2-benzyl-4,4-bis(methoxycarbonyl)cyclopentene",
    "3p": "1-phenyl-2-propyl-4,4-bis(methoxycarbonyl)cyclopentene",
    "3δ": "1-(4′-methylphenyl)-2-propyl-4,4-bis(methoxycarbonyl)cyclopentene",
    "3q": "1-(4′-methoxyphenyl)-2-propyl-4,4-bis(methoxycarbonyl)cyclopentene",
    "3r": "1-(4′-methoxycarbonylphenyl)-2-propyl-4,4-bis(methoxycarbonyl)cyclopentene",
    "3w": "1-phenyl-4,4-bis(methoxycarbonyl)-5-(n-hexyl)cyclopentene",
    "3x": "1-(4′-methylphenyl)-4,4-bis(methoxycarbonyl)-5-(n-hexyl)cyclopentene",
    "3y": "1-(4′-methoxyphenyl)-4,4-bis(methoxycarbonyl)-5-(n-hexyl)cyclopentene",
    "3z": "1-(4′-methoxycarbonylphenyl)-4,4-bis(methoxycarbonyl)-5-(n-hexyl)cyclopentene",
    "3l": "(E)-1-(2′-phenylethenyl)-2-benzyl-4,4-bis(methoxycarbonyl)cyclopentene",
    "3m": "(E)-1-benzyl-2-(hex-1′-enyl)-4,4-bis(methoxycarbonyl)cyclopentene",
    "3t": "(E)-1-(hex-1′-enyl)-2-propyl-4,4-bis(methoxycarbonyl)cyclopentene",
    "3i-o-Me": "1-benzyl-2-(2′-methylphenyl)-4,4-bis(methoxycarbonyl)cyclopentene",
    "3a": "1-phenyl-4,4-bis(methoxycarbonyl)cyclopentene",
    "3c": "1-(4′-methylphenyl)-4,4-bis(methoxycarbonyl)cyclopentene",
    "3d": "1-(4′-methoxyphenyl)-4,4-bis(methoxycarbonyl)cyclopentene",
    "3g": "1-(4′-methoxycarbonylphenyl)-4,4-bis(methoxycarbonyl)cyclopentene",
}


def enrich(
    suffix: str,
    pages: list[int],
    substrate_mass: float | None,
    substrate_amount: float | None,
    halide_mass: float | None,
    halide_amount: float | None,
    products: list[tuple[str, str, float, float]],
    basis: str = "reported product mass and yield in the Experimental Section",
):
    record = rec(suffix)
    ev = evid(*pages)
    add_evidence(record, pages)
    if substrate_mass is not None:
        add_amount(participant(record, "substrate"), "mass", quantity(substrate_mass, "mg"), ev)
    if substrate_amount is not None:
        add_amount(participant(record, "substrate"), "amount", quantity(substrate_amount, "mmol"), ev)
    if halide_mass is not None:
        add_amount(participant(record, "organic_halide"), "mass", quantity(halide_mass, "mg"), ev)
    if halide_amount is not None:
        add_amount(participant(record, "organic_halide"), "amount", quantity(halide_amount, "mmol"), ev)
    for entity_id, label, product_mass, product_yield in products:
        item = participant(record, entity_id)
        item["label"] = fact(label, ev)
        if label in PRODUCT_NAMES:
            item["name"] = fact(PRODUCT_NAMES[label], ev)
        add_amount(item, "isolated_mass", quantity(product_mass, "mg"), ev)
        set_yield(record, entity_id, quantity(product_yield, "%"), ev)
    set_basis(record, basis, ev)
    clean_review(record)
    return record


# Page 7: Conditions A continuation, detailed typical procedures B-D, and products 1-8.
r = enrich("table1_entry_6", [7], 117, 0.64, 157, 0.77, [("product_2", "2a", 132, 80)],
           "isolated after flash chromatography")
add_note(
    r,
    "The Conditions A typical procedure reports PhI as 156 mg/0.76 mmol, while the product listing reports 157 mg/0.77 mmol; both source statements are retained.",
    [f"{DOC}:page6:image", f"{DOC}:page6:text", f"{DOC}:page7:image", f"{DOC}:page7:text"],
)

r = enrich("table1_entry_7", [7], 67, 0.36, 96, 0.47, [("product_2", "2a", 81, 85)],
           "isolated after flash chromatography")
ev7 = evid(7)
add_amount(participant(r, "base"), "mass", quantity(201, "mg"), ev7)
add_amount(participant(r, "base"), "amount", quantity(1.5, "mmol"), ev7)
add_amount(participant(r, "catalyst"), "mass", quantity(21, "mg"), ev7)
add_amount(participant(r, "solvent"), "volume", quantity(3, "mL"), ev7)
next(x for x in r["steps"][0]["conditions"] if x["name"] == "atmosphere")["fact"] = fact("nitrogen", ev7)
upsert_step(r, {
    "step_id": "workup_and_purification",
    "participant_ids": ["product_2"],
    "conditions": [
        field("workup", "filtered, washed with ether, and evaporated", ev7),
        field("purification", "flash chromatography on silica gel; petroleum ether/ethyl acetate 20:1", ev7),
    ],
})

r = enrich("scheme4_conditions_C", [7], 41, 0.15, 37, None, [("product_3", "3i", 46, 88)],
           "isolated after flash chromatography")
add_amount(participant(r, "base"), "mass", quantity(7, "mg"), ev7)
add_amount(participant(r, "base"), "dispersion_strength", quantity(60, "%"), ev7)
add_amount(participant(r, "catalyst"), "mass", quantity(8.7, "mg"), ev7)
add_amount(participant(r, "solvent"), "volume", quantity(1.5, "mL"), ev7)
next(x for x in r["steps"][0]["conditions"] if x["name"] == "atmosphere")["fact"] = fact("nitrogen", ev7)
upsert_step(r, {
    "step_id": "workup_and_purification",
    "participant_ids": ["product_3"],
    "conditions": [
        field("quench", "aqueous saturated NaCl", ev7),
        field("quench_volume", quantity(2, "mL"), ev7),
        field("workup", "extracted with ether (20 mL), washed with brine (3 × 8 mL), and dried over anhydrous sodium sulfate", ev7),
        field("purification", "flash chromatography on silica gel; petroleum ether/ethyl acetate 10:1", ev7),
    ],
})

r = rec("table7_entry_5")
add_evidence(r, [7, 11])
ev711 = evid(7, 11)
add_amount(participant(r, "substrate"), "mass", quantity(46, "mg"), ev711)
add_amount(participant(r, "substrate"), "amount", quantity(0.25, "mmol"), ev711)
add_amount(participant(r, "organic_halide"), "mass", quantity(61, "mg"), ev711)
add_amount(participant(r, "base"), "mass", quantity(20, "mg"), ev7)
add_amount(participant(r, "base"), "amount", quantity(0.5, "mmol"), ev7)
add_amount(participant(r, "catalyst"), "mass", quantity(14.5, "mg"), ev7)
add_amount(participant(r, "solvent"), "volume", quantity(2.0, "mL"), ev7)
product_3a = participant(r, "product_3")
product_3a["name"] = fact(PRODUCT_NAMES["3a"], evid(11))
add_amount(product_3a, "isolated_mass", quantity(43, "mg"), evid(11))
upsert_outcome(r, field("experimental_section_yield_3a", quantity(66, "%"), evid(11), ["product_3"]))
set_basis(r, "isolated after flash chromatography", ev711)
next(x for x in r["steps"][0]["conditions"] if x["name"] == "atmosphere")["fact"] = fact("nitrogen", ev7)
upsert_step(r, {
    "step_id": "workup_and_purification",
    "participant_ids": ["product_3"],
    "conditions": [
        field("workup", "ether (30 mL) added; washed with brine (3 × 8 mL); dried over anhydrous sodium sulfate; filtered and evaporated", ev7),
        field("purification", "flash chromatography on silica gel; petroleum ether/ethyl acetate 20:1", ev7),
    ],
})
clean_review(r)

page7_pairs = [
    (2, 100, 0.543, 183, 0.65, 184, 83, 79, 0.429, 158, 0.556, 111, 76, "2b"),
    (3, 140, 0.76, 199, 0.91, 170, 82, 92, 0.50, 131, 0.65, 78, 57, "2c"),
    (4, 118, 0.641, 180, 0.769, 128, 69, 105, 0.571, 174, 0.742, 98, 59, "2d"),
    (5, 94, 0.511, 141, 0.613, 67, 46, 101, 0.549, 164, 0.714, 71, 45, "2e"),
    (6, 97, 0.527, 162, 0.632, 166, 86, 80, 0.435, 133, 0.566, 122, 91, "2f"),
    (7, 120, 0.652, 199, 0.76, 120, 58, 82, 0.446, 152, 0.58, 103, 73, "2g"),
    (8, 94, 0.511, 129, 0.613, 91, 67, 95, 0.516, 141, 0.67, 84, 61, "2h"),
]
for row, sma, sna, hma, hna, pma, ya, smb, snb, hmb, hnb, pmb, yb, label in page7_pairs:
    ra = enrich(f"table2_entry_{row}_conditions_A", [7], sma, sna, hma, hna, [("product_2", label, pma, ya)])
    enrich(f"table2_entry_{row}_conditions_B", [7], smb, snb, hmb, hnb, [("product_2", label, pmb, yb)])
    if row == 2:
        upsert_outcome(ra, field("experimental_section_reported_yield_2b", quantity(87, "%"), ev7, ["product_2"]))
        upsert_outcome(ra, field("reported_purity_2b", quantity(87, "%"), ev7, ["product_2"]))
        add_note(
            ra,
            "Table 2 reports 83% for Conditions A, whereas the Experimental Section listing reports purity 87% and yield 87%; the conflicting source values are retained separately.",
            [f"{DOC}:page2:image", f"{DOC}:page7:image", f"{DOC}:page7:text"],
        )
        add_unresolved(ra, "Internal source discrepancy: Table 2 gives 83% but the product listing gives 87% for 2b under Conditions A.")
    if row == 6:
        upsert_outcome(ra, field("experimental_section_reported_yield_2f", quantity(95, "%"), ev7, ["product_2"]))
        upsert_outcome(ra, field("reported_purity_2f", quantity(93, "%"), ev7, ["product_2"]))
        add_note(
            ra,
            "Table 2 reports 86% for Conditions A, whereas the Experimental Section listing reports purity 93% and yield 95%; the conflicting source values are retained separately.",
            [f"{DOC}:page2:image", f"{DOC}:page7:image", f"{DOC}:page7:text"],
        )
        add_unresolved(ra, "Internal source discrepancy: Table 2 gives 86% but the product listing gives 95% for 2f under Conditions A.")


# Page 8: Conditions A product entries 9-19, corresponding to Table 3 entries 1-11.
page8 = [
    (1, 41, 0.15, 37, 0.18, [("product_2", "2i", 41, 80)]),
    (2, 41, 0.15, 42, 0.18, [("product_2", "2j", 36, 63)]),
    (3, 41, 0.15, 47, 0.18, [("product_2", "2k", 50, 82), ("product_3", "3k", 10, 16)]),
    (4, 68, 0.25, 69, 0.3, [("product_2", "2l", 79, 84)]),
    (5, 71, 0.26, 66, 0.31, [("product_2", "2m", 60, 67)]),
    (6, 41, 0.15, 38, 0.18, [("product_2", "2n", 23, 45)]),
    (7, 68, 0.25, 63, 0.3, [("product_2", "2o", 86, 97)]),
    (8, 56.5, 0.25, 61, 0.3, [("product_2", "2p", 58, 77)]),
    (9, 56.5, 0.25, 70, 0.3, [("product_2", "2q", 37, 45)]),
    (10, 56.5, 0.25, 79, 0.3, [("product_2", "2r", 64, 71)]),
    (11, 56.5, 0.25, 69, 0.3, [("product_2", "2s", 62, 71)]),
]
for row, sm, sn, hm, hn, products in page8:
    enrich(f"table3_entry_{row}", [8], sm, sn, hm, hn, products)


# Page 9: Conditions A product entries 20-28, corresponding to Table 3 entries 12-14 and Table 4.
page9_table3 = [
    (12, 56.5, 0.25, 63, 0.3, [("product_2", "2t", 54, 70)]),
    (13, 56.5, 0.25, 63, 0.3, [("product_2", "2u", 44, 57)]),
    (14, 56.5, 0.25, 63, 0.3, [("product_2", "2v", 61, 79)]),
]
for row, sm, sn, hm, hn, products in page9_table3:
    enrich(f"table3_entry_{row}", [9], sm, sn, hm, hn, products)

page9_table4 = [
    (1, 40.2, 0.15, 37, 0.18, [("product_2", "2w", 37, 72), ("product_3", "3w", 3, 6)]),
    (2, 40.2, 0.15, 43, 0.19, [("product_2", "2x", 47, 88), ("product_3", "3x", 2, 4)]),
    (3, 40.2, 0.15, 42, 0.18, [("product_2", "2y", 32, 57), ("product_3", "3y", 5, 9)]),
    (4, 40.2, 0.15, 48, 0.18, [("product_2", "2z", 43, 71), ("product_3", "3z", 5, 8)]),
    (5, 40.2, 0.15, 41.4, 0.18, [("product_2", "2α", 49, 88)]),
    (6, 36, 0.15, 37, 0.18, [("product_2", "2β", 20, 42), ("product_3", "3β", 10, 21)]),
]
for row, sm, sn, hm, hn, products in page9_table4:
    enrich(f"table4_entry_{row}", [9], sm, sn, hm, hn, products)


# Pages 10-11: Conditions C products 29-43 and Conditions A/D products 44-48.
page10_table5 = [
    (1, 41, 0.15, 40, 0.18, [("product_3", "3γ", 43, 79)]),
    (2, 41, 0.15, 42, 0.18, [("product_3", "3j", 56, 98)]),
    (3, 41, 0.15, 47, 0.18, [("product_3", "3k", 47, 77)]),
    (4, 56.5, 0.25, 61, 0.3, [("product_3", "3p", 49, 65)]),
    (5, 56.5, 0.25, 65.4, 0.3, [("product_3", "3δ", 43, 54)]),
    (6, 56.5, 0.25, 70.2, 0.3, [("product_3", "3q", 39, 47), ("product_2", "2q", 6, 7)]),
    (7, 56.5, 0.25, 79, 0.3, [("product_3", "3r", 49, 54), ("product_2", "2r", 7, 8)]),
    (8, 40.2, 0.15, 37, 0.18, [("product_3", "3w", 42, 81)]),
    (10, 40.2, 0.15, 40, 0.18, [("product_3", "3x", 44, 82), ("product_2", "2x", 3, 5)]),
    (11, 40.2, 0.15, 42, 0.18, [("product_3", "3y", 44, 78), ("product_2", "2y", 11, 20)]),
    (12, 41, 0.15, 41.4, 0.18, [("product_3", "3l", 18, 32), ("product_2", "2l", 22, 39)]),
    (13, 68, 0.25, 63, 0.3, [("product_3", "3m", 21, 24), ("product_2", "2m", 36, 40)]),
    (14, 56.5, 0.25, 63, 0.3, [("product_3", "3t", 14, 18), ("product_2", "2t", 25, 32)]),
]
for row, sm, sn, hm, hn, products in page10_table5:
    pages = [10, 11] if row == 14 else [10]
    enrich(f"table5_entry_{row}", pages, sm, sn, hm, hn, products)

# Resolve Greek labels visible in Table 5 using its page-3 image as context.
for row, labels in [(1, ("2γ", "3γ")), (5, ("2δ", "3δ"))]:
    r = rec(f"table5_entry_{row}")
    for entity_id, label in zip(("product_2", "product_3"), labels):
        item = participant(r, entity_id)
        item["label"] = fact(label, [f"{DOC}:page3:image"])
        if entity_id == "product_2":
            item["name"] = fact(f"cyclopropane product {label}", [f"{DOC}:page3:image"])
        for outcome in r["outcomes"]:
            if outcome["name"].startswith("yield_") and entity_id in outcome.get("target_entity_ids", []):
                outcome["name"] = f"yield_{label}"

enrich("table5_entry_15", [11], 46, 0.25, 69, 0.3, [("product_2", "2e", 32, 45)])
enrich("scheme7_o_iodotoluene", [11], 41, 0.15, 40, 0.18, [("product_3", "3i-o-Me", 44, 80)])
enrich("table8_entry_1", [11], 46, 0.25, 65, 0.3, [("product_3", "3c", 43, 63)])
enrich("table8_entry_2", [11], 46, 0.25, 71, 0.3, [("product_3", "3d", 41, 57)])

r = rec("scheme6_conditions_D")
add_evidence(r, [11])
ev11 = evid(11)
add_amount(participant(r, "substrate"), "mass", quantity(46, "mg"), ev11)
add_amount(participant(r, "substrate"), "amount", quantity(0.25, "mmol"), ev11)
add_amount(participant(r, "organic_halide"), "mass", quantity(79, "mg"), ev11)
add_amount(participant(r, "organic_halide"), "amount", quantity(0.3, "mmol"), ev11)
participant(r, "product_3")["name"] = fact(PRODUCT_NAMES["3g"], ev11)
participant(r, "product_2")["name"] = fact(PRODUCT_NAMES["2g"], ev11)
upsert_outcome(r, field("isolated_combined_mass_3g_plus_2g", quantity(44, "mg"), ev11, ["product_3", "product_2"]))
set_basis(r, "reported isolated combined product mass/yield; molar ratio determined by 300 MHz 1H NMR", ev11)
r["review"]["unresolved"] = [
    item for item in r["review"]["unresolved"]
    if not item.startswith("Individual product yields and the combined-yield measurement basis")
]
add_unresolved(
    r,
    "Individual yields for 2g and 3g are not reported separately; only combined mass/yield and an NMR molar ratio are provided.",
)


# Preserve all updates as raw model output. Merge will force needs_review/unreviewed/unverified.
records = list(updates.values())
RAW.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")


page_records = {
    7: [
        "table1_entry_6", "table1_entry_7", "scheme4_conditions_C", "table7_entry_5",
        *[f"table2_entry_{row}_conditions_{condition}" for row in range(2, 9) for condition in ("A", "B")],
    ],
    8: [f"table3_entry_{row}" for row in range(1, 12)],
    9: [*[f"table3_entry_{row}" for row in range(12, 15)], *[f"table4_entry_{row}" for row in range(1, 7)]],
    10: ["scheme4_conditions_C", *[f"table5_entry_{row}" for row in (1, 2, 3, 4, 5, 6, 7, 8, 10, 11, 12, 13, 14)]],
    11: ["table5_entry_14", "table5_entry_15", "scheme7_o_iodotoluene", "table7_entry_5", "table8_entry_1", "table8_entry_2", "scheme6_conditions_D"],
}
page_records = {page: [f"{DOC}:{suffix}" for suffix in suffixes] for page, suffixes in page_records.items()}

coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 7,
            "state": "attempted",
            "regions": [
                {"region": "left column top, continuation of Conditions A and Conditions B-D typical procedures", "finding": "Conditions A continuation and detailed Conditions B, C, and D procedures were matched to four existing experiments; quantities, atmosphere, workup, purification, and product masses were merged rather than duplicated.", "evidence_ids": evid(7)},
                {"region": "left lower and right columns, Experimental Section products 1-8", "finding": "Product paragraphs 1-8 give paired Conditions A/B preparations for 2a-2h with starting quantities, product masses, stated yields, and characterization; each was matched to its existing Table 1/2 record.", "evidence_ids": evid(7)},
            ],
            "record_ids": page_records[7],
            "unresolved": [
                "The Conditions A typical procedure and product listing round PhI differently (156 mg/0.76 mmol versus 157 mg/0.77 mmol); both are retained.",
                "Internal source discrepancies remain for Conditions A 2b (Table 2: 83%; product listing: 87%) and 2f (Table 2: 86%; product listing: 95% with 93% purity).",
                "Product structures remain unverified machine records; no SI file was explicitly supplied or associated.",
            ],
        },
        {
            "page": 8,
            "state": "attempted",
            "regions": [
                {"region": "both columns, Experimental Section products 9-19", "finding": "Conditions A preparations 2i-2s were matched to Table 3 entries 1-11; exact starting quantities, product masses, stated yields, names, and characterization context were added.", "evidence_ids": evid(8)},
            ],
            "record_ids": page_records[8],
            "unresolved": ["The page does not independently restate the shared Conditions A workup for every product; structures and stereochemistry remain unverified machine candidates."],
        },
        {
            "page": 9,
            "state": "attempted",
            "regions": [
                {"region": "left column upper, Experimental Section products 20-22", "finding": "Conditions A preparations 2t-2v were matched to Table 3 entries 12-14 with exact starting quantities, product masses, and stated yields.", "evidence_ids": evid(9)},
                {"region": "left lower and right columns, Experimental Section products 23-28", "finding": "Conditions A preparations from 1d/1e were matched to Table 4 entries 1-6, preserving both cyclopropane and cyclopentene product masses/yields where reported and the 2α/2β/3β labels.", "evidence_ids": evid(9)},
            ],
            "record_ids": page_records[9],
            "unresolved": ["E/Z ratios remain supported by Table 4/page 3; page 9 provides characterization but does not restate every ratio or common workup detail."],
        },
        {
            "page": 10,
            "state": "attempted",
            "regions": [
                {"region": "left column product 29 and products 30-36", "finding": "The detailed Conditions C preparation of 3i and products 3γ, 3j, 3k, 3p, 3δ, 3q/2q, and 3r/2r were matched to Scheme 4/Table 5 records with exact masses and yields.", "evidence_ids": evid(10)},
                {"region": "right column products 37-42", "finding": "Conditions C preparations 3w, 3x/2x, 3y/2y, 3l/2l, 3m/2m, and 3t/2t were matched to Table 5 entries; product 42 characterization continues on page 11.", "evidence_ids": evid(10)},
            ],
            "record_ids": page_records[10],
            "unresolved": ["Table 5 entry 9 (THF, 3w 95%) has no separate detailed product paragraph on this page and was not enriched from an assumed procedure."],
        },
        {
            "page": 11,
            "state": "attempted",
            "regions": [
                {"region": "left column top and products 43-47", "finding": "The page completes product 42 characterization and gives detailed preparations for Conditions C product 2e, Conditions A product 3i-o-Me, and Conditions D products 3a, 3c, and 3d; each was matched to an existing record.", "evidence_ids": evid(11)},
                {"region": "right column product 48", "finding": "The Conditions D 3g/2g mixture was matched to Scheme 6: 44 mg, 55% combined yield, and 66:34 3g/2g molar ratio by 300 MHz 1H NMR; individual yields were not inferred.", "evidence_ids": evid(11)},
                {"region": "right column acknowledgments and Supporting Information notice", "finding": "No reaction experiment is present here. The article states that supporting information is available, but no SI file is explicitly supplied or associated in this workspace.", "evidence_ids": evid(11)},
            ],
            "record_ids": page_records[11],
            "unresolved": ["Individual 2g and 3g yields are not stated separately.", "Supporting-information association remains unestablished; the availability notice is not treated as a supplied SI file."],
        },
    ],
}
COVERAGE.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")


tasks = json.loads(TASKS.read_text())
for task in tasks:
    if task["document_id"] != DOC:
        continue
    for page in range(7, 12):
        if task["task_id"] == f"{DOC}:page{page}:text":
            task["state"] = "attempted"
            task["visual_evidence_id"] = f"{DOC}:page{page}:image"
TASKS.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")


print(json.dumps({
    "updated_records": len(records),
    "coverage_pages": [page["page"] for page in coverage["pages"]],
    "page_record_references": {str(page): len(ids) for page, ids in page_records.items()},
}, ensure_ascii=False, indent=2))
