#!/usr/bin/env python3
"""Enrich the existing page-1--6 table records with exact batches on pages 7--11.

This helper transcribes source facts only.  It deliberately keeps every record
partial, every structure unverified, and every fact unreviewed for machine merge.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path


DOC = "doc_e07c8acc21fad353"
ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "dataset.json"
OUT = Path(__file__).with_name("records_pages_0007_0011.json")
COVERAGE = ROOT / "coverage" / "pages_0007_0011.json"
TASKS = ROOT / "tasks.json"


def ev(page: int) -> list[str]:
    return [f"{DOC}:page{page}:text", f"{DOC}:page{page}:image"]


def fact(value, evidence_ids):
    return {
        "value": value,
        "evidence_ids": list(evidence_ids) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def q(number, unit, **extra):
    return {"number": number, "unit": unit, **extra}


def field(name, value, evidence_ids, targets=None):
    result = {"name": name, "fact": fact(value, evidence_ids)}
    if targets:
        result["target_entity_ids"] = list(targets)
    return result


data = json.loads(DATASET.read_text())
selected_ids = {
    "table5_entry3_3f", "table5_entry4_3g", "table5_entry5_3h",
    "table5_entry6_3i", "table5_entry7_3j", "table5_entry8_3q",
    "table5_entry9_3r", "table5_entry10_3k", "table5_entry11_3l",
    "table5_entry12_3m", "table5_entry13_3n", "table5_entry14_3s",
    "table5_entry15_3o", "table6_entry4", "table7_entry3_3g",
    "table7_entry4_3j", "table7_entry5_3k", "table7_entry6_3l",
    "table7_entry7_3m",
}
records = {
    r["source_reaction_id"]: copy.deepcopy(r)
    for r in data["experiments"]
    if r["source_reaction_id"] in selected_ids
}
assert set(records) == selected_ids, sorted(selected_ids - set(records))


def same_field(left, right):
    return (
        left.get("name") == right.get("name")
        and left.get("fact", {}).get("value") == right.get("fact", {}).get("value")
        and left.get("fact", {}).get("evidence_ids") == right.get("fact", {}).get("evidence_ids")
        and left.get("target_entity_ids") == right.get("target_entity_ids")
    )


def add_evidence(record, *pages):
    for page in pages:
        for evidence_id in ev(page):
            if evidence_id not in record["evidence_ids"]:
                record["evidence_ids"].append(evidence_id)


def add_amount(record, entity_id, name, value, page):
    participant = next(p for p in record["participants"] if p["entity_id"] == entity_id)
    addition = field(name, value, ev(page))
    if not any(same_field(x, addition) for x in participant["amounts"]):
        participant["amounts"].append(addition)


def add_condition(record, name, value, page):
    addition = field(name, value, ev(page))
    conditions = record["steps"][0]["conditions"]
    if not any(same_field(x, addition) for x in conditions):
        conditions.append(addition)


def add_note(record, value, page):
    addition = fact(value, ev(page))
    if addition not in record["notes"]:
        record["notes"].append(addition)


def add_specs(record, specs, page):
    for entity_id, amounts in specs.items():
        for name, value in amounts:
            add_amount(record, entity_id, name, value, page)


def enrich_radical(rid, page, specs, purification):
    record = records[rid]
    add_evidence(record, page, 5)
    add_specs(record, specs, page)
    add_condition(record, "procedure_reference", "following typical procedure 1", page)
    add_condition(
        record,
        "workup",
        "quenched with brine, extracted with diethyl ether, and dried over anhydrous Na2SO4",
        5,
    )
    add_condition(record, "operation", "filtration and evaporation", 5)
    add_condition(record, "purification", purification, page)
    record["completeness"] = "partial"
    return record


def enrich_kinetic(rid, page, specs, purification):
    record = records[rid]
    add_evidence(record, page, 6)
    add_specs(record, specs, page)
    add_condition(record, "procedure_reference", "following typical procedure 2", page)
    add_condition(record, "operation", "monitored by GC", 6)
    add_condition(
        record,
        "workup",
        "quenched with brine, extracted with diethyl ether, and dried over anhydrous Na2SO4",
        6,
    )
    add_condition(record, "operation", "filtration and evaporation", 6)
    add_condition(record, "purification", purification, page)
    record["completeness"] = "partial"
    return record


# Page 7: completion of 3f; exact 3g and 3h addition/resolution batches.
enrich_radical("table5_entry3_3f", 7, {
    "1f": [("mass", q(0.3924, "g")), ("amount", q(2.39, "mmol"))],
    "2a": [("mass", q(1.6588, "g")), ("amount", q(4.79, "mmol"))],
    "Na2S2O4": [("mass", q(0.8388, "g")), ("amount", q(4.82, "mmol"))],
    "base": [("mass", q(0.5103, "g")), ("amount", q(4.81, "mmol"))],
    "MeOH": [("volume", q(4.5, "mL"))], "H2O": [("volume", q(1.5, "mL"))],
    "3f": [("mass", q(0.8468, "g"))],
}, "silica-gel column chromatography; petroleum ether/ethyl acetate 10/1")
records["table5_entry3_3f"]["review"]["unresolved"] = [
    x for x in records["table5_entry3_3f"]["review"]["unresolved"]
    if "continues on page 7" not in x
]

enrich_radical("table5_entry4_3g", 7, {
    "1g": [("mass", q(0.3045, "g")), ("amount", q(2.42, "mmol"))],
    "2a": [("mass", q(1.6716, "g")), ("amount", q(4.83, "mmol"))],
    "Na2S2O4": [("mass", q(0.8376, "g")), ("amount", q(4.81, "mmol"))],
    "base": [("mass", q(0.5054, "g")), ("amount", q(4.77, "mmol"))],
    "MeOH": [("volume", q(4.5, "mL"))], "H2O": [("volume", q(1.5, "mL"))],
    "3g": [("mass", q(0.8800, "g"))],
}, "silica-gel column chromatography; petroleum ether/ethyl acetate 10/1")

enrich_kinetic("table7_entry3_3g", 7, {
    "3g": [("mass", q(118.0, "mg")), ("amount", q(0.250, "mmol"))],
    "4": [("mass", q(9.8, "mg")), ("amount", q(0.175, "mmol"))],
    "PdPPh3_2Cl2": [("mass", q(8.8, "mg")), ("amount", q(0.013, "mmol")), ("batch_catalyst_loading", q(5.0, "mol%"))],
    "CuI": [("mass", q(2.3, "mg")), ("amount", q(0.012, "mmol")), ("batch_catalyst_loading", q(4.8, "mol%"))],
    "Et2NH": [("mass", q(13.0, "mg")), ("amount", q(0.179, "mmol"))],
    "CH3CN": [("volume", q(0.5, "mL"))],
    "Z_3g": [("mass", q(53.6, "mg"))], "E_5g": [("mass", q(29.3, "mg"))],
}, "silica-gel chromatography; Z-3g petroleum ether/ethyl acetate 10/1; E-5g 3/1")

enrich_radical("table5_entry5_3h", 7, {
    "1h": [("mass", q(0.2764, "g")), ("amount", q(1.97, "mmol"))],
    "2a": [("mass", q(1.3984, "g")), ("amount", q(4.04, "mmol"))],
    "Na2S2O4": [("mass", q(0.6991, "g")), ("amount", q(4.02, "mmol"))],
    "base": [("mass", q(0.4270, "g")), ("amount", q(4.03, "mmol"))],
    "MeOH": [("volume", q(6.0, "mL"))], "H2O": [("volume", q(2.0, "mL"))],
    "3h": [("mass_as_printed", q(0.6508, "mg"))],
}, "silica-gel column chromatography; petroleum ether/ethyl acetate 10/1")
record_3h = records["table5_entry5_3h"]
for item in record_3h["steps"][0]["conditions"]:
    if item["name"] == "reaction_time":
        item["fact"] = fact(q(40, "min"), ev(7))
add_note(record_3h, "The source prints the 3h product mass as 0.6508 mg alongside a 68% yield from 1.97 mmol substrate.", 7)
if "The printed 3h product mass unit is internally inconsistent with the reported scale and 68% yield; it was preserved without correction." not in record_3h["review"]["unresolved"]:
    record_3h["review"]["unresolved"].append(
        "The printed 3h product mass unit is internally inconsistent with the reported scale and 68% yield; it was preserved without correction."
    )

enrich_kinetic("table6_entry4", 7, {
    "E_Z_3h": [("mass", q(121.9, "mg")), ("amount", q(0.251, "mmol"))],
    "4": [("mass", q(9.8, "mg")), ("amount", q(0.175, "mmol"))],
    "PdPPh3_2Cl2": [("mass", q(8.7, "mg")), ("amount", q(0.012, "mmol")), ("batch_catalyst_loading", q(4.9, "mol%"))],
    "CuI": [("mass", q(2.4, "mg")), ("amount", q(0.013, "mmol")), ("batch_catalyst_loading", q(5.0, "mol%"))],
    "Et2NH": [("mass", q(12.9, "mg")), ("amount", q(0.177, "mmol"))],
    "CH3CN": [("volume", q(0.5, "mL"))],
    "Z_3h": [("mass", q(56.3, "mg"))], "E_5h": [("mass", q(25.6, "mg"))],
}, "silica-gel chromatography; Z-3h petroleum ether/ethyl acetate 10/1; E-5h 3/1")


# Page 8: exact 3i, 3j, 3q, and 3r batches plus the 3j resolution.
enrich_radical("table5_entry6_3i", 8, {
    "1i": [("mass", q(0.3687, "g")), ("amount", q(2.39, "mmol"))],
    "2a": [("mass", q(1.6645, "g")), ("amount", q(4.81, "mmol"))],
    "Na2S2O4": [("mass", q(0.8334, "g")), ("amount", q(4.79, "mmol"))],
    "base": [("mass", q(0.5082, "g")), ("amount", q(4.79, "mmol"))],
    "MeOH": [("volume", q(4.5, "mL"))], "H2O": [("volume", q(1.5, "mL"))],
    "3i": [("mass", q(0.7124, "g"))],
}, "silica-gel column chromatography; petroleum ether/ethyl acetate 10/1")

enrich_radical("table5_entry7_3j", 8, {
    "1j": [("mass", q(0.3215, "g")), ("amount", q(2.01, "mmol"))],
    "2a": [("mass", q(1.3986, "g")), ("amount", q(4.04, "mmol"))],
    "Na2S2O4": [("mass", q(0.6971, "g")), ("amount", q(4.01, "mmol"))],
    "base": [("mass", q(0.4257, "g")), ("amount", q(4.02, "mmol"))],
    "MeOH": [("volume", q(3.75, "mL"))], "H2O": [("volume", q(1.25, "mL"))],
    "3j": [("mass", q(0.6101, "g"))],
}, "silica-gel column chromatography; petroleum ether/ethyl acetate 10/1")

enrich_kinetic("table7_entry4_3j", 8, {
    "3j": [("mass", q(126.5, "mg")), ("amount", q(0.250, "mmol"))],
    "4": [("mass", q(9.7, "mg")), ("amount", q(0.173, "mmol"))],
    "PdPPh3_2Cl2": [("mass", q(8.9, "mg")), ("amount", q(0.013, "mmol")), ("batch_catalyst_loading", q(5.1, "mol%"))],
    "CuI": [("mass", q(2.5, "mg")), ("amount", q(0.013, "mmol")), ("batch_catalyst_loading", q(5.3, "mol%"))],
    "Et2NH": [("mass", q(12.8, "mg")), ("amount", q(0.175, "mmol"))],
    "CH3CN": [("volume", q(0.5, "mL"))],
    "Z_3j": [("mass", q(49.9, "mg"))], "E_5j": [("mass", q(42.3, "mg"))],
}, "silica-gel chromatography; Z-3j petroleum ether/ethyl acetate 10/1; E-5j 2/1")

enrich_radical("table5_entry8_3q", 8, {
    "1n": [("mass", q(67.1, "mg")), ("amount", q(0.60, "mmol"))],
    "2a": [("volume", q(0.21, "mL")), ("density_as_reported", "d=2.01"), ("mass", q(0.4221, "g")), ("amount", q(1.22, "mmol"))],
    "Na2S2O4": [("mass", q(0.2098, "g")), ("amount", q(1.21, "mmol"))],
    "base": [("mass", q(0.1277, "g")), ("amount", q(1.20, "mmol"))],
    "MeOH": [("volume", q(1.5, "mL"))], "H2O": [("volume", q(0.5, "mL"))],
    "3q": [("mass", q(185.2, "mg"))],
}, "silica-gel column chromatography; petroleum ether/diethyl ether 20/1 to 10/1")

enrich_radical("table5_entry9_3r", 8, {
    "1o": [("mass", q(76.6, "mg")), ("amount", q(0.61, "mmol"))],
    "2a": [("volume", q(0.21, "mL")), ("density_as_reported", "d=2.01"), ("mass", q(0.4221, "g")), ("amount", q(1.22, "mmol"))],
    "Na2S2O4": [("mass", q(208.9, "mg")), ("amount", q(1.20, "mmol"))],
    "base": [("mass", q(128.8, "mg")), ("amount", q(1.22, "mmol"))],
    "MeOH": [("volume", q(1.5, "mL"))], "H2O": [("volume", q(0.5, "mL"))],
    "3r": [("mass", q(237.8, "mg"))],
}, "silica-gel column chromatography; 30-60 °C petroleum ether/diethyl ether 20/1")


# Page 9: exact C6F13 radical additions and their kinetic resolutions.
enrich_radical("table5_entry10_3k", 9, {
    "1g": [("mass", q(0.2517, "g")), ("amount", q(2.00, "mmol"))],
    "2b": [("mass", q(1.7856, "g")), ("amount", q(4.00, "mmol"))],
    "Na2S2O4": [("mass", q(0.6954, "g")), ("amount", q(4.00, "mmol"))],
    "base": [("mass", q(0.4240, "g")), ("amount", q(4.00, "mmol"))],
    "MeOH": [("volume", q(3.75, "mL"))], "H2O": [("volume", q(1.25, "mL"))],
    "3k": [("mass", q(0.8304, "g"))],
}, "silica-gel column chromatography; petroleum ether/ethyl acetate 10/1")

enrich_kinetic("table7_entry5_3k", 9, {
    "3k": [("mass", q(129.6, "mg")), ("amount", q(0.227, "mmol"))],
    "4": [("mass", q(8.8, "mg")), ("amount", q(0.157, "mmol"))],
    "PdPPh3_2Cl2": [("mass", q(8.4, "mg")), ("amount", q(0.012, "mmol")), ("batch_catalyst_loading", q(5.3, "mol%"))],
    "CuI": [("mass", q(2.0, "mg")), ("amount", q(0.011, "mmol")), ("batch_catalyst_loading", q(4.9, "mol%"))],
    "Et2NH": [("mass", q(12.0, "mg")), ("amount", q(0.164, "mmol"))],
    "CH3CN": [("volume", q(0.46, "mL"))],
    "Z_3k": [("mass", q(64.1, "mg"))], "E_5k": [("mass", q(30.8, "mg"))],
}, "silica-gel chromatography; Z-3k petroleum ether/ethyl acetate 10/1; E-5k 3/1")

enrich_radical("table5_entry11_3l", 9, {
    "1h": [("mass", q(0.3369, "g")), ("amount", q(2.41, "mmol"))],
    "2b": [("mass", q(2.1682, "g")), ("amount", q(4.86, "mmol"))],
    "Na2S2O4": [("mass", q(0.8363, "g")), ("amount", q(4.81, "mmol"))],
    "base": [("mass", q(0.5075, "g")), ("amount", q(4.79, "mmol"))],
    "MeOH": [("volume", q(4.5, "mL"))], "H2O": [("volume", q(1.5, "mL"))],
    "3l": [("mass", q(0.8759, "g"))],
}, "silica-gel column chromatography; petroleum ether/ethyl acetate 10/1")

enrich_kinetic("table7_entry6_3l", 9, {
    "3l": [("mass", q(235.2, "mg")), ("amount", q(0.401, "mmol"))],
    "4": [("mass", q(15.6, "mg")), ("amount", q(0.279, "mmol"))],
    "PdPPh3_2Cl2": [("mass", q(13.9, "mg")), ("amount", q(0.020, "mmol")), ("batch_catalyst_loading", q(4.9, "mol%"))],
    "CuI": [("mass", q(3.3, "mg")), ("amount", q(0.017, "mmol")), ("batch_catalyst_loading", q(4.3, "mol%"))],
    "Et2NH": [("mass", q(20.5, "mg")), ("amount", q(0.281, "mmol"))],
    "CH3CN": [("volume", q(0.8, "mL"))],
    "Z_3l": [("mass", q(115.9, "mg"))], "E_5l": [("mass", q(46.6, "mg"))],
}, "silica-gel chromatography; Z-3l petroleum ether/ethyl acetate 10/1; E-5l 3/1")


# Page 10: exact 3m/resolution, 3n, and 3s batches.
enrich_radical("table5_entry12_3m", 10, {
    "1i": [("mass", q(0.3073, "g")), ("amount", q(2.00, "mmol"))],
    "2b": [("mass", q(1.7996, "g")), ("amount", q(4.03, "mmol"))],
    "Na2S2O4": [("mass", q(0.6964, "g")), ("amount", q(4.00, "mmol"))],
    "base": [("mass", q(0.4228, "g")), ("amount", q(3.99, "mmol"))],
    "MeOH": [("volume", q(3.75, "mL"))], "H2O": [("volume", q(1.25, "mL"))],
    "3m": [("mass", q(0.9901, "g"))],
}, "silica-gel column chromatography; petroleum ether/ethyl acetate 10/1")

enrich_kinetic("table7_entry7_3m", 10, {
    "3m": [("mass", q(149.4, "mg")), ("amount", q(0.249, "mmol"))],
    "4": [("mass", q(9.8, "mg")), ("amount", q(0.175, "mmol"))],
    "PdPPh3_2Cl2": [("mass", q(8.7, "mg")), ("amount", q(0.012, "mmol")), ("batch_catalyst_loading", q(5.0, "mol%"))],
    "CuI": [("mass", q(2.5, "mg")), ("amount", q(0.013, "mmol")), ("batch_catalyst_loading", q(5.3, "mol%"))],
    "Et2NH": [("mass", q(12.6, "mg")), ("amount", q(0.173, "mmol"))],
    "CH3CN": [("volume", q(0.5, "mL"))],
    "Z_3m": [("mass", q(77.9, "mg"))], "E_5m": [("mass", q(29.1, "mg"))],
}, "silica-gel chromatography; Z-3m petroleum ether/ethyl acetate 10/1; E-5m 3/1")

enrich_radical("table5_entry13_3n", 10, {
    "1k": [("mass", q(0.1314, "g")), ("amount", q(0.82, "mmol"))],
    "2a": [("mass", q(0.5661, "g")), ("amount", q(1.64, "mmol"))],
    "Na2S2O4": [("mass", q(0.2802, "g")), ("amount", q(1.61, "mmol"))],
    "base": [("mass", q(0.1694, "g")), ("amount", q(1.60, "mmol"))],
    "MeOH": [("volume", q(1.5, "mL"))], "H2O": [("volume", q(0.5, "mL"))],
    "E_3n": [("mass", q(0.2337, "g"))], "Z_3n": [("mass", q(0.0246, "g"))],
}, "silica-gel chromatography; E-3n petroleum ether/diethyl ether 60/1; Z-3n 20/1")

enrich_radical("table5_entry14_3s", 10, {
    "1p": [("mass", q(54.6, "mg")), ("amount", q(0.30, "mmol"))],
    "2a": [("volume", q(0.10, "mL")), ("density_as_reported", "d=2.01"), ("mass", q(0.201, "g")), ("amount", q(0.58, "mmol"))],
    "Na2S2O4": [("mass", q(105.3, "mg")), ("amount", q(0.61, "mmol"))],
    "base": [("mass", q(63.8, "mg")), ("amount", q(0.60, "mmol"))],
    "MeOH": [("volume", q(1.5, "mL"))], "H2O": [("volume", q(0.5, "mL"))],
    "E_3s": [("mass", q(77.2, "mg"))],
}, "silica-gel column chromatography; petroleum ether/diethyl ether 80/1 to 20/1")


# Page 11: exact E/Z-3o batch.  References, acknowledgements, and SI notice do
# not create additional reaction records.
enrich_radical("table5_entry15_3o", 11, {
    "1l": [("mass", q(0.1117, "g")), ("amount", q(0.81, "mmol"))],
    "2a": [("mass", q(0.5379, "g")), ("amount", q(1.55, "mmol"))],
    "Na2S2O4": [("mass", q(0.2800, "g")), ("amount", q(1.61, "mmol"))],
    "base": [("mass", q(0.1687, "g")), ("amount", q(1.59, "mmol"))],
    "MeOH": [("volume", q(1.5, "mL"))], "H2O": [("volume", q(0.5, "mL"))],
    "E_3o": [("mass", q(0.2307, "g"))], "Z_3o": [("mass", q(0.0216, "g"))],
}, "silica-gel chromatography; E-3o petroleum ether/diethyl ether 40/1; Z-3o 20/1")


ordered = [records[rid] for rid in sorted(records)]
OUT.write_text(json.dumps(ordered, ensure_ascii=False, indent=2) + "\n")


def record_ids(*ids):
    return [f"{DOC}:{rid}" for rid in ids]


coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 7,
            "state": "attempted",
            "regions": [
                {"region": "upper-left continuation of section 4.2.8", "finding": "Exact 3f radical-addition batch, product mass, isolated yield, E/Z ratio, and eluent merged into the existing Table 5 entry 3 record.", "evidence_ids": ev(7)},
                {"region": "left column section 4.2.9", "finding": "3g radical-addition and Sonogashira kinetic-resolution batches inspected and merged into existing Table 5 entry 4 and Table 7 entry 3 records; characterization is not a separate experiment.", "evidence_ids": ev(7)},
                {"region": "upper-right characterization continuation for E-5g", "finding": "Spectroscopic and analytical characterization only; no new reaction record.", "evidence_ids": ev(7)},
                {"region": "right column section 4.2.10", "finding": "3h radical-addition and kinetic-resolution batches inspected and merged into Table 5 entry 5 and Table 6 entry 4. The printed 0.6508 mg 3h mass is internally inconsistent with the stated scale/yield and remains unresolved.", "evidence_ids": ev(7)},
            ],
            "record_ids": record_ids("table5_entry3_3f", "table5_entry4_3g", "table7_entry3_3g", "table5_entry5_3h", "table6_entry4"),
            "unresolved": ["The source prints 3h product mass as 0.6508 mg alongside 68% yield from 1.97 mmol substrate; no correction was inferred."],
        },
        {
            "page": 8,
            "state": "attempted",
            "regions": [
                {"region": "upper-left continuation of E-5h characterization", "finding": "Characterization continuation only; linked to the existing Table 6 entry 4 batch and not counted as a new reaction.", "evidence_ids": ev(8)},
                {"region": "left column sections 4.2.11 and 4.2.12", "finding": "Exact 3i and 3j radical-addition batches plus the 3j kinetic resolution were merged into existing Table 5 entries 6-7 and Table 7 entry 4.", "evidence_ids": ev(8)},
                {"region": "upper-right continuation of 3j kinetic resolution and characterization", "finding": "Exact Z-3j/E-5j masses, yields, and eluents complete the cross-column batch; subsequent spectra are characterization only.", "evidence_ids": ev(8)},
                {"region": "lower-right sections 4.2.13 and 4.2.14", "finding": "Exact 3q and 3r radical-addition batches were merged into Table 5 entries 8 and 9; the 3r characterization continues on page 9.", "evidence_ids": ev(8)},
            ],
            "record_ids": record_ids("table6_entry4", "table5_entry6_3i", "table5_entry7_3j", "table7_entry4_3j", "table5_entry8_3q", "table5_entry9_3r"),
            "unresolved": ["Complex structures and E/Z assignments remain machine-unverified; spectra were not interpreted into additional reaction fields."],
        },
        {
            "page": 9,
            "state": "attempted",
            "regions": [
                {"region": "top-left continuation of 3r characterization", "finding": "Characterization continuation only; no new experiment beyond the page-8 3r batch.", "evidence_ids": ev(9)},
                {"region": "left column section 4.2.15", "finding": "Exact 3k radical-addition and kinetic-resolution batches were merged into existing Table 5 entry 10 and Table 7 entry 5 records.", "evidence_ids": ev(9)},
                {"region": "right column section 4.2.16", "finding": "Exact 3l radical-addition and kinetic-resolution batches were merged into existing Table 5 entry 11 and Table 7 entry 6 records; E-5l characterization continues on page 10.", "evidence_ids": ev(9)},
            ],
            "record_ids": record_ids("table5_entry9_3r", "table5_entry10_3k", "table7_entry5_3k", "table5_entry11_3l", "table7_entry6_3l"),
            "unresolved": ["Structures are retained by source labels with null SMILES and remain unverified."],
        },
        {
            "page": 10,
            "state": "attempted",
            "regions": [
                {"region": "upper-left continuation of E-5l characterization", "finding": "Characterization continuation only; no new experiment beyond the page-9 Table 7 entry 6 batch.", "evidence_ids": ev(10)},
                {"region": "left column section 4.2.17", "finding": "Exact 3m radical-addition and kinetic-resolution batches were merged into existing Table 5 entry 12 and Table 7 entry 7 records.", "evidence_ids": ev(10)},
                {"region": "upper-right continuation of E-5m characterization", "finding": "Spectroscopic and analytical characterization only; no independent reaction record.", "evidence_ids": ev(10)},
                {"region": "right column sections 4.2.18 and 4.2.19", "finding": "Exact separate E/Z-3n isolation and E-3s/Z-3s outcomes were merged into Table 5 entries 13 and 14, preserving the impure Z-3s result and crude-NMR E/Z ratio context.", "evidence_ids": ev(10)},
            ],
            "record_ids": record_ids("table7_entry6_3l", "table5_entry12_3m", "table7_entry7_3m", "table5_entry13_3n", "table5_entry14_3s"),
            "unresolved": ["Z-3s was explicitly not isolated in pure form; no pure-product yield was inferred."],
        },
        {
            "page": 11,
            "state": "attempted",
            "regions": [
                {"region": "left column section 4.2.20", "finding": "Exact E-3o and Z-3o isolation batch was merged into existing Table 5 entry 15; characterization paragraphs were inspected but not made into separate reactions.", "evidence_ids": ev(11)},
                {"region": "lower-left acknowledgements and Supplementary data notice", "finding": "Acknowledgement of reproduced Table 7 results provides no separate conditions/outcomes, so no duplicate experiments were created. The paper links online supplementary data, but no SI file was explicitly supplied or associated.", "evidence_ids": ev(11)},
                {"region": "right column References and notes", "finding": "Prior literature and review citations only; no experiments of the present paper were extracted from this region.", "evidence_ids": ev(11)},
            ],
            "record_ids": record_ids("table5_entry15_3o"),
            "unresolved": ["Supporting Information remains unassociated and was not used."],
        },
    ],
}
COVERAGE.parent.mkdir(parents=True, exist_ok=True)
COVERAGE.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")


tasks = json.loads(TASKS.read_text())
for task in tasks:
    if task.get("document_id") == DOC and task.get("task_id") in {
        f"{DOC}:page{page}:text" for page in range(7, 12)
    }:
        task["state"] = "attempted"
        task["reason"] = "Original page image and text inspected; detailed batches reconciled with existing records and page coverage logged."
TASKS.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({
    "updated_records": len(ordered),
    "records_file": str(OUT),
    "coverage_file": str(COVERAGE),
    "coverage_pages": [p["page"] for p in coverage["pages"]],
}, ensure_ascii=False))
