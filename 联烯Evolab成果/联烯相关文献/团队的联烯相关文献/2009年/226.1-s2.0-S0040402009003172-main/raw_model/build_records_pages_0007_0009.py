#!/usr/bin/env python3
import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = "doc_9b18f28384e009c1"


def ev(page):
    return [f"{DOC}:page{page}:image", f"{DOC}:page{page}:text"]


def add_unique(items, values):
    for value in values:
        if value not in items:
            items.append(value)


def fact(value, evidence):
    return {"value": value, "evidence_ids": list(evidence), "verification": "unreviewed"}


def qty(number, unit):
    return {"number": number, "unit": unit}


def field(name, value, evidence, targets=None):
    out = {"name": name, "fact": fact(value, evidence)}
    if targets:
        out["target_entity_ids"] = list(targets)
    return out


def participant(record, entity_id):
    return next(p for p in record["participants"] if p["entity_id"] == entity_id)


def add_amount(record, entity_id, name, value, evidence):
    p = participant(record, entity_id)
    p["amounts"] = [x for x in p["amounts"] if x["name"] != name]
    p["amounts"].append(field(name, value, evidence))


def set_condition(record, name, value, evidence):
    for step in record["steps"]:
        for item in step["conditions"]:
            if item["name"] == name:
                item["fact"] = fact(value, evidence)
                return
    record["steps"][0]["conditions"].append(field(name, value, evidence))


def set_outcome(record, name, value, evidence, targets=None):
    for item in record["outcomes"]:
        if item["name"] == name:
            item["fact"] = fact(value, evidence)
            if targets:
                item["target_entity_ids"] = list(targets)
            return
    record["outcomes"].append(field(name, value, evidence, targets))


dataset = json.loads((ROOT / "dataset.json").read_text())
existing = {r["record_id"]: r for r in dataset["experiments"]}
updates = []


def get(record_id, pages):
    record = copy.deepcopy(existing[record_id])
    evidence = []
    for page in pages:
        evidence.extend(ev(page))
    add_unique(record["evidence_ids"], evidence)
    record["status"] = "needs_review"
    record["completeness"] = "partial"
    record["review"]["method"] = "model"
    record["review"]["reviewer"] = None
    record["review"]["checked_fields"] = []
    return record


# Table 5 entries 6-8: detailed chiral ether preparations on page 7.
table5 = {
    6: {
        "id": f"{DOC}:table5_entry6_s-5c", "sub": (1.5666, 8.9),
        "nbuli": (7.8, 19.6), "momcl": (1.00, 1.060, 13.2), "product_mass": 1.1070,
    },
    7: {
        "id": f"{DOC}:table5_entry7_r-5d", "sub": (1.9950, 12.3),
        "nbuli": (10.8, 27.1), "momcl": (1.40, 1.484, 18.5), "product_mass": 1.5444,
    },
    8: {
        "id": f"{DOC}:table5_entry8_s-5d", "sub": (1.1255, 7.0),
        "nbuli": (6.1, 15.3), "momcl": (0.80, 0.848, 10.4), "product_mass": 0.8744,
    },
}
for entry, data in table5.items():
    evidence = ev(7)
    record = get(data["id"], [7])
    add_amount(record, "substrate", "mass", qty(data["sub"][0], "g"), evidence)
    add_amount(record, "substrate", "amount", qty(data["sub"][1], "mmol"), evidence)
    add_amount(record, "nbuli", "volume", qty(data["nbuli"][0], "mL"), evidence)
    add_amount(record, "nbuli", "concentration", qty(2.5, "M"), evidence)
    add_amount(record, "nbuli", "amount", qty(data["nbuli"][1], "mmol"), evidence)
    add_amount(record, "momcl", "volume", qty(data["momcl"][0], "mL"), evidence)
    add_amount(record, "momcl", "mass", qty(data["momcl"][1], "g"), evidence)
    add_amount(record, "momcl", "amount", qty(data["momcl"][2], "mmol"), evidence)
    add_amount(record, "thf", "volume", qty(30, "mL"), evidence)
    add_amount(record, "product", "mass", qty(data["product_mass"], "g"), evidence)
    set_outcome(record, "ee_measurement_basis", "chiral HPLC (Chiralcel AD-H)", evidence)
    record["review"]["unresolved"] = [
        "Candidate connectivity and stereochemistry are unverified.",
        "The abbreviated preparation does not restate atmosphere, workup, or purification; these remain missing.",
    ]
    updates.append(record)


# Table 6 entries 1-14: exact quantities and outcomes from sections 4.5.1-4.5.14.
table6 = {
    1: ("r-6a", 7, 53.0, 0.30, 8.7, 30.2, 4),
    2: ("s-6a", 7, 52.3, 0.30, 8.8, 28.6, 6),
    3: ("r-6b", 7, 57.2, 0.30, 8.8, 30.5, None),
    4: ("s-6b", 7, 57.3, 0.30, 8.6, 29.1, None),
    5: ("r-6c", (7, 8), 68.0, 0.31, 8.5, 19.7, 6),
    6: ("s-6c", 8, 64.5, 0.29, 8.6, 20.3, 6),
    7: ("r-6d", 8, 61.0, 0.30, 8.8, 33.2, 7),
    8: ("s-6d", 8, 62.0, 0.30, 8.7, 34.3, None),
    9: ("r-6e", 8, 53.2, 0.30, 8.8, 20.8, 8),
    10: ("s-6e", 8, 49.9, 0.28, 8.6, 17.5, 5),
    11: ("r-6f", 8, 51.6, 0.29, 8.7, 20.2, 7),
    12: ("s-6f", 8, 52.2, 0.30, 8.6, 21.9, 5),
    13: ("r-6g", 8, 53.2, 0.30, 8.6, 31.8, 11),
    14: ("r-6h", (8, 9), 51.6, 0.29, 8.8, 34.6, 10),
}
for entry, (suffix, pages_value, sub_mass, sub_mmol, cubr_mass, product_mass, detailed_recovery) in table6.items():
    pages = list(pages_value) if isinstance(pages_value, tuple) else [pages_value]
    evidence = []
    for page in pages:
        evidence.extend(ev(page))
    record = get(f"{DOC}:table6_entry{entry}_{suffix}", pages)
    add_amount(record, "substrate", "mass", qty(sub_mass, "mg"), evidence)
    add_amount(record, "substrate", "amount", qty(sub_mmol, "mmol"), evidence)
    add_amount(record, "cubr", "mass", qty(cubr_mass, "mg"), evidence)
    add_amount(record, "cubr", "amount", qty(0.06, "mmol"), evidence)
    add_amount(record, "ether", "volume", qty(1.6, "mL"), evidence)
    add_amount(record, "grignard", "solution_volume", qty(1.4, "mL"), evidence)
    add_amount(record, "grignard", "solution_concentration", qty(1.0, "M"), evidence)
    add_amount(record, "grignard", "amount", qty(1.4, "mmol"), evidence)
    add_amount(record, "product", "mass", qty(product_mass, "mg"), evidence)
    set_outcome(record, "ee_measurement_basis", "chiral HPLC (Chiralcel OD-H)", evidence)
    if detailed_recovery is not None:
        set_outcome(record, "recovered_starting_material_yield", qty(detailed_recovery, "%"), evidence, ["substrate"])
    if entry == 1:
        set_condition(record, "reaction_time", qty(10.5, "h"), evidence)
        set_condition(record, "atmosphere", "nitrogen", evidence)
        set_condition(record, "workup", "quenched with saturated ammonium chloride solution (2 mL), extracted with ether (3 × 10 mL), washed with saturated brine (10 mL), and dried over anhydrous sodium sulfate", evidence)
        set_condition(record, "purification", "evaporation and silica-gel column chromatography (petroleum ether/ethyl acetate 20:1)", evidence)
    elif entry == 13:
        set_condition(record, "reaction_time", qty(8, "h"), evidence)
    unresolved = ["Candidate connectivity and stereochemistry are unverified."]
    if entry != 1:
        unresolved.append("The abbreviated preparation does not restate atmosphere, workup, or purification; these remain missing.")
    if entry not in (1, 13):
        unresolved.append("Reaction time is not stated in the detailed preparation.")
    if entry >= 9:
        unresolved.append("Table 6 prints starting-material labels 5e-5h, while the detailed preparations identify the phenyl-substituted ether as 5a; both source usages are preserved without forcing a relabeling.")
    record["review"]["unresolved"] = unresolved
    updates.append(record)


assert len(updates) == 17
assert len({r["record_id"] for r in updates}) == 17
assert all(r["status"] == "needs_review" and r["completeness"] == "partial" for r in updates)
assert all(not p["structure_verified"] for r in updates for p in r["participants"])

raw_path = ROOT / "raw_model" / "records_pages_0007_0009.json"
raw_path.write_text(json.dumps(updates, ensure_ascii=False, indent=2) + "\n")

coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 7,
            "state": "attempted",
            "regions": [
                {
                    "region": "left column continuation of section 4.4.6 and sections 4.4.7-4.4.8",
                    "finding": "Detailed quantities, isolated masses, yields, product ee values, and chiral-HPLC methods enrich Table 5 entries 6-8; characterization text is identity support, not additional reactions.",
                    "evidence_ids": ev(7),
                },
                {
                    "region": "lower left and right columns, sections 4.5.1-4.5.5",
                    "finding": "The complete typical procedure for R-6a and abbreviated preparations through R-6c enrich Table 6 entries 1-5; section 4.5.5 continues on page 8.",
                    "evidence_ids": ev(7),
                },
            ],
            "record_ids": [
                f"{DOC}:table5_entry6_s-5c", f"{DOC}:table5_entry7_r-5d", f"{DOC}:table5_entry8_s-5d",
                f"{DOC}:table6_entry1_r-6a", f"{DOC}:table6_entry2_s-6a", f"{DOC}:table6_entry3_r-6b",
                f"{DOC}:table6_entry4_s-6b", f"{DOC}:table6_entry5_r-6c",
            ],
            "unresolved": ["Abbreviated preparations do not restate the complete typical-procedure operations; these details were not silently inherited."],
        },
        {
            "page": 8,
            "state": "attempted",
            "regions": [
                {
                    "region": "top-left continuation of section 4.5.5 and sections 4.5.6-4.5.8",
                    "finding": "Exact quantities, isolated masses/yields, ee measurements, and recoveries enrich Table 6 entries 5-8.",
                    "evidence_ids": ev(8),
                },
                {
                    "region": "lower-left and right columns, sections 4.5.9-4.5.14",
                    "finding": "Detailed preparations enrich Table 6 entries 9-14; entry 13 states 8 h, while entry 14 product outcome continues on page 9.",
                    "evidence_ids": ev(8),
                },
            ],
            "record_ids": [f"{DOC}:table6_entry{i}_{suffix}" for i, suffix in [(5,"r-6c"),(6,"s-6c"),(7,"r-6d"),(8,"s-6d"),(9,"r-6e"),(10,"s-6e"),(11,"r-6f"),(12,"s-6f"),(13,"r-6g"),(14,"r-6h")]],
            "unresolved": ["For entries 9-14, Table 6 prints starting-material labels 5e-5h whereas the detailed preparations use 5a; no unsupported normalization was made."],
        },
        {
            "page": 9,
            "state": "attempted",
            "regions": [
                {
                    "region": "upper-left continuation of section 4.5.14",
                    "finding": "The R-6h product mass, 51% isolated yield, 99.6% ee, chiral-HPLC method, and 10% recovered R-5a complete the existing Table 6 entry 14 record.",
                    "evidence_ids": ev(9),
                },
                {
                    "region": "acknowledgements, supplementary-data notice, and references",
                    "finding": "No independent experiment is reported. The paper states that supplementary data exist online, but no SI file was supplied or explicitly associated, so SI remains unestablished; bibliography entries were not expanded into experiments.",
                    "evidence_ids": ev(9),
                },
            ],
            "record_ids": [f"{DOC}:table6_entry14_r-6h"],
            "unresolved": ["SI association remains unestablished despite the availability notice."],
        },
    ],
}

assert [p["page"] for p in coverage["pages"]] == [7, 8, 9]
assert all(p["regions"] for p in coverage["pages"])
assert all(f"{DOC}:page{p['page']}:image" in region["evidence_ids"] for p in coverage["pages"] for region in p["regions"])
(ROOT / "coverage" / "pages_0007_0009.json").write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

tasks_path = ROOT / "tasks.json"
tasks = json.loads(tasks_path.read_text())
for task in tasks:
    if task.get("document_id") == DOC and task.get("evidence_id") in {f"{DOC}:page{i}:text" for i in range(7, 10)}:
        task["state"] = "attempted"
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"submitted_records": len(updates), "new_record_ids": 0, "coverage_pages": [7, 8, 9]}, ensure_ascii=False))
