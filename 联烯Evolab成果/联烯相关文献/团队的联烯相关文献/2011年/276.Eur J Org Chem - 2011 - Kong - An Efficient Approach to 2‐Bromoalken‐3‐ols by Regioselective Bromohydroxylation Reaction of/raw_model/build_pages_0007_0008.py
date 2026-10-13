#!/usr/bin/env python3
"""Enrich existing cross-page records with source evidence from PDF pages 7-8."""

import copy
import json
from pathlib import Path


DOC = "doc_4bdcd5de15645fe5"
ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "dataset.json"
OUT = Path(__file__).resolve().parent


def ev(page, kind):
    return f"{DOC}:page{page}:{kind}"


def page_evidence(page):
    return [ev(page, "text"), ev(page, "image")]


P7 = page_evidence(7)
P8 = page_evidence(8)


def fact(value, evidence):
    return {
        "value": value,
        "evidence_ids": list(evidence) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def qty(number, unit, raw_text=None):
    value = {"number": number, "unit": unit}
    if raw_text is not None:
        value["raw_text"] = raw_text
    return value


def field(name, value, evidence, targets=None):
    item = {"name": name, "fact": fact(value, evidence)}
    if targets:
        item["target_entity_ids"] = list(targets)
    return item


def participant(entity_id, role, label, name, evidence, smiles=None, amounts=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence),
        "smiles": fact(smiles, evidence) if smiles else fact(None, []),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": amounts or [],
    }


data = json.loads(DATASET.read_text())
wanted = {
    f"{DOC}:scheme2_tbaf_2n",
    f"{DOC}:scheme3_elimination_4a",
    f"{DOC}:scheme3_sonogashira_5a",
    f"{DOC}:scheme3_suzuki_6a",
    f"{DOC}:scheme3_suzuki_7a",
}
existing = {r["record_id"]: copy.deepcopy(r) for r in data["experiments"] if r["record_id"] in wanted}
assert set(existing) == wanted, (set(existing), wanted)


def add_record_evidence(record, evidence=P7):
    record["evidence_ids"] = list(dict.fromkeys(record["evidence_ids"] + list(evidence)))
    record["status"] = "candidate"
    record["completeness"] = "partial"
    record["review"] = {"method": "none", "reviewer": None, "checked_fields": [], "unresolved": []}
    return record


def replace_amounts(record, entity_id, amounts):
    target = next(p for p in record["participants"] if p["entity_id"] == entity_id)
    target["amounts"] = amounts
    return target


def upsert_participant(record, item, index=None):
    for position, current in enumerate(record["participants"]):
        if current["entity_id"] == item["entity_id"]:
            record["participants"][position] = item
            return item
    if index is None:
        record["participants"].append(item)
    else:
        record["participants"].insert(index, item)
    return item


def set_conditions(record, conditions):
    record["steps"] = [{
        "step_id": "reaction",
        "participant_ids": [p["entity_id"] for p in record["participants"] if p["role"] != "product"],
        "conditions": conditions,
    }]


records = []

# Page 7 begins with analytical characterization continuing the page-6 4a
# elimination. It is the same batch and therefore only adds evidence/context.
r = add_record_evidence(existing[f"{DOC}:scheme3_elimination_4a"])
r["notes"] = [
    fact(
        "Scheme 3 reports 30 °C, whereas the detailed procedure on page 6 reports room temperature for the same 12 h experiment; page 7 only continues the analytical characterization of 4a.",
        page_evidence(3) + page_evidence(6) + P7,
    )
]
r["review"]["unresolved"] = [
    "Temperature remains discrepant between Scheme 3 (30 °C) and the detailed procedure (room temperature); both source statements are retained and the generic temperature field remains missing.",
    "The product structure is a machine candidate and was not independently structure-verified.",
]
records.append(r)


# Detailed page-7 TBAF treatment of the 2n Z/E mixture.
r = add_record_evidence(existing[f"{DOC}:scheme2_tbaf_2n"])
replace_amounts(r, "reactant_2n_mixture", [
    field("mass", qty(391.7, "mg"), P7),
    field("amount", qty(1.29, "mmol"), P7),
])
replace_amounts(r, "reagent_tbaf", [
    field("solution_volume", qty(3.9, "mL"), P7),
    field("concentration", qty(1.0, "M", "1 m in THF"), P7),
    field("amount", qty(3.9, "mmol"), P7),
])
replace_amounts(r, "solvent_dmf", [field("volume", qty(13.0, "mL"), P7)])
upsert_participant(
    r,
    participant("tbaf_carrier_thf", "solvent", "THF", "tetrahydrofuran", P7, "C1CCOC1"),
    index=3,
)
set_conditions(r, [
    field("solvent", "DMF; TBAF supplied as a 1 M solution in THF", P7),
    field("temperature", "r.t.", P7),
    field("time", qty(24, "h"), P7),
    field("operation", "2n and TBAF solution were reacted in DMF", P7),
    field("purification", "silica-gel chromatography (petroleum ether/ethyl acetate, 100:1 to 50:1 to 30:1)", P7),
])
r["outcomes"] = [
    field("isolated_yield_Z_2n", qty(51, "%"), P7, ["product_Z_2n"]),
    field("isolated_product_Z_2n_mass", qty(198.8, "mg"), P7, ["product_Z_2n"]),
    field("isolated_yield_4n", qty(6, "%"), P7, ["product_4n"]),
    field("isolated_product_4n_mass", qty(17.0, "mg"), P7, ["product_4n"]),
    field("yield_measurement_basis", "isolated yield", P7),
]
r["notes"] = [
    fact(
        "The source describes selective elimination of the E component of the 2n mixture, isolating (Z)-2n and propargylic alcohol 4n; page 7 provides analytical characterization for both isolated materials.",
        page_evidence(3) + P7,
    )
]
r["review"]["unresolved"] = [
    "No workup is stated before the reported chromatography.",
    "The (Z) assignment is attributed elsewhere in the article to an NOE study in Supporting Information, but no SI was provided or associated.",
    "Structures remain unverified machine candidates.",
]
records.append(r)


# Detailed Sonogashira coupling, identical to the Scheme 3 arrow already recorded.
r = add_record_evidence(existing[f"{DOC}:scheme3_sonogashira_5a"])
for entity_id, amounts in {
    "reactant_2a": [field("mass", qty(68.1, "mg"), P7), field("amount", qty(0.30, "mmol"), P7)],
    "ethynylbenzene": [field("mass", qty(62.5, "mg"), P7), field("amount", qty(0.6, "mmol"), P7)],
    "pd_catalyst": [field("mass", qty(11.0, "mg"), P7), field("amount", qty(0.015, "mmol"), P7)],
    "cui": [field("mass", qty(3.1, "mg"), P7), field("amount", qty(0.015, "mmol"), P7)],
    "nbutylamine": [field("mass", qty(110.2, "mg"), P7), field("amount", qty(1.5, "mmol"), P7)],
    "benzene": [field("volume", qty(2.0, "mL"), P7)],
}.items():
    replace_amounts(r, entity_id, amounts)
product = next(p for p in r["participants"] if p["entity_id"] == "product_5a")
product["name"] = fact("3-methylene-1,5-diphenyl-4-butyn-2-ol", P7)
set_conditions(r, [
    field("solvent", "benzene", P7),
    field("temperature", "r.t.", P7),
    field("time", qty(14, "h"), P7),
    field("operation", "PdCl2(PPh3)2, CuI, 2a, benzene, ethynylbenzene, and nBuNH2 were sequentially added to a Schlenk tube at room temperature; completion was monitored by TLC", P7),
    field("purification", "silica-gel column chromatography (petroleum ether/ethyl acetate, 10:1)", P7),
])
r["outcomes"] = [
    field("isolated_yield", qty(92, "%"), P7, ["product_5a"]),
    field("isolated_product_mass", qty(68.1, "mg"), P7, ["product_5a"]),
    field("yield_measurement_basis", "isolated yield", P7),
]
r["notes"] = [fact("The page-7 detailed procedure corresponds to the Sonogashira arrow for 5a in Scheme 3 and is not a separate experiment.", page_evidence(3) + P7)]
r["review"]["unresolved"] = [
    "The source names a Schlenk tube but does not explicitly state the reaction atmosphere or a separate workup.",
    "The product structure remains an unverified machine candidate.",
]
records.append(r)


# Detailed Suzuki coupling to 6a, including explicitly stated nitrogen handling.
r = add_record_evidence(existing[f"{DOC}:scheme3_suzuki_6a"])
for entity_id, amounts in {
    "reactant_2a": [field("mass", qty(68.6, "mg"), P7), field("amount", qty(0.3, "mmol"), P7)],
    "phenylboronic_acid": [field("mass", qty(73.0, "mg"), P7), field("amount", qty(0.6, "mmol"), P7)],
    "palladium_acetate": [field("mass", qty(2.0, "mg"), P7), field("amount", qty(0.009, "mmol"), P7)],
    "triphenylphosphine": [field("mass", qty(4.8, "mg"), P7), field("amount", qty(0.018, "mmol"), P7)],
    "potassium_phosphate": [field("mass", qty(222.6, "mg"), P7), field("amount", qty(1.05, "mmol"), P7)],
    "dioxane": [field("first_dioxane_volume", qty(1.0, "mL"), P7), field("second_dioxane_volume", qty(1.0, "mL"), P7)],
}.items():
    replace_amounts(r, entity_id, amounts)
upsert_participant(
    r,
    participant("water", "solvent", "H2O", "water", P7, "O", [field("volume", qty(16.5, "uL"), P7), field("amount", qty(0.9, "mmol"), P7)]),
)
upsert_participant(
    r,
    participant("workup_dichloromethane", "solvent", "CH2Cl2", "dichloromethane used for the short silica-gel column", P7, "ClCCl"),
)
set_conditions(r, [
    field("solvent", "1,4-dioxane/H2O", P7),
    field("atmosphere", "nitrogen; vessel was flame-dried under vacuum and backfilled with nitrogen three times", P7),
    field("temperature", qty(110, "°C"), P7),
    field("time", qty(48, "h"), P7),
    field("operation", "Reagents were added sequentially at room temperature, then the mixture was heated in a preheated 110 °C oil bath; completion was monitored by TLC", P7),
    field("workup", "cooled to room temperature and filtered through a short silica-gel column using CH2Cl2, then concentrated", P7),
    field("purification", "silica-gel chromatography (petroleum ether/ethyl acetate, 30:1)", P7),
])
r["outcomes"] = [
    field("isolated_yield", qty(70, "%"), P7, ["product_6a"]),
    field("isolated_product_mass", qty(47.2, "mg"), P7, ["product_6a"]),
    field("yield_measurement_basis", "isolated yield", P7),
]
r["notes"] = [fact("The page-7 detailed procedure corresponds to the Suzuki arrow for 6a in Scheme 3 and is not a separate experiment.", page_evidence(3) + P7)]
r["review"]["unresolved"] = [
    "Supporting Information is mentioned by the article but was not provided or associated.",
    "The product structure remains an unverified machine candidate.",
]
records.append(r)


# Abbreviated Suzuki preparation of 7a. Do not import un-repeated atmosphere or
# workup details from the preceding 6a batch.
r = add_record_evidence(existing[f"{DOC}:scheme3_suzuki_7a"])
for entity_id, amounts in {
    "reactant_2a": [field("mass", qty(68.3, "mg"), P7), field("amount", qty(0.3, "mmol"), P7)],
    "styrylboronic_acid": [field("mass", qty(89.0, "mg"), P7), field("amount", qty(0.6, "mmol"), P7)],
    "palladium_acetate": [field("mass", qty(2.1, "mg"), P7), field("amount", qty(0.009, "mmol"), P7)],
    "triphenylphosphine": [field("mass", qty(4.7, "mg"), P7), field("amount", qty(0.018, "mmol"), P7)],
    "potassium_phosphate": [field("mass", qty(222.6, "mg"), P7), field("amount", qty(1.05, "mmol"), P7)],
    "water": [field("volume", qty(16.5, "uL"), P7), field("amount", qty(0.9, "mmol"), P7)],
    "dioxane": [field("volume", qty(2.0, "mL"), P7)],
}.items():
    replace_amounts(r, entity_id, amounts)
set_conditions(r, [
    field("solvent", "1,4-dioxane/H2O", P7),
    field("temperature", qty(110, "°C"), P7),
    field("time", qty(6, "h"), P7),
    field("operation", "The listed reagents were reacted at 110 °C for 6 h", P7),
    field("purification", "silica-gel chromatography (petroleum ether/ethyl acetate, 20:1)", P7),
])
r["outcomes"] = [
    field("isolated_yield", qty(56, "%"), P7, ["product_7a"]),
    field("isolated_product_mass", qty(42.0, "mg"), P7, ["product_7a"]),
    field("yield_measurement_basis", "isolated yield", P7),
]
r["notes"] = [fact("The page-7 abbreviated preparation corresponds to the Suzuki arrow for 7a in Scheme 3 and is not a separate experiment.", page_evidence(3) + P7)]
r["review"]["unresolved"] = [
    "The abbreviated 7a paragraph does not explicitly restate vessel preparation, atmosphere, or workup, so those details were not inherited from the preceding 6a batch.",
    "Supporting Information is mentioned by the article but was not provided or associated.",
    "The product structure remains an unverified machine candidate.",
]
records.append(r)


coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 7,
            "state": "attempted",
            "regions": [
                {
                    "region": "upper-left continuation of the 4a elimination section",
                    "finding": "Only analytical characterization of 4a continues from page 6; it was linked to the existing 2a-to-4a TBAF elimination record and not counted as a new experiment.",
                    "evidence_ids": P7,
                },
                {
                    "region": "left column, detailed 2n/TBAF experiment",
                    "finding": "The Scheme 2 experiment was enriched with exact substrate, TBAF/THF solution, DMF, time, isolated masses/yields for (Z)-2n and 4n, and chromatography conditions.",
                    "evidence_ids": P7,
                },
                {
                    "region": "left column, Sonogashira procedure for 5a",
                    "finding": "The existing Scheme 3 Sonogashira record was enriched with all stated reagent quantities, sequential addition, room-temperature duration, TLC completion, purification, product mass, and isolated yield.",
                    "evidence_ids": P7,
                },
                {
                    "region": "bottom-left through upper-right, Suzuki procedure for 6a",
                    "finding": "The cross-column 6a procedure was read as one experiment and enriched with two distinct dioxane additions, explicit nitrogen handling, 110 °C/48 h heating, workup, purification, product mass, and isolated yield.",
                    "evidence_ids": P7,
                },
                {
                    "region": "upper-right, abbreviated Suzuki preparation of 7a",
                    "finding": "The 7a Scheme 3 record was enriched with its explicitly restated quantities, 110 °C/6 h conditions, chromatography, product mass, and isolated yield; atmosphere and workup were left missing rather than inherited from 6a.",
                    "evidence_ids": P7,
                },
                {
                    "region": "right-column Supporting Information statement, acknowledgments, and references 1-3",
                    "finding": "No additional independent experimental record is stated. The acknowledgment that selected scope results were reproduced supplies no separate batch conditions or outcomes. SI is mentioned but no SI file was provided or associated.",
                    "evidence_ids": P7,
                },
            ],
            "record_ids": [
                f"{DOC}:scheme3_elimination_4a",
                f"{DOC}:scheme2_tbaf_2n",
                f"{DOC}:scheme3_sonogashira_5a",
                f"{DOC}:scheme3_suzuki_6a",
                f"{DOC}:scheme3_suzuki_7a",
            ],
            "unresolved": [
                "Scheme 3 and the detailed procedure disagree on the 4a elimination temperature (30 °C versus room temperature).",
                "NOE-based stereochemical support and the stated NMR spectra are in unavailable Supporting Information.",
                "Machine-candidate structures remain unverified.",
            ],
        },
        {
            "page": 8,
            "state": "attempted",
            "regions": [
                {
                    "region": "entire page, references 4-17 and publication dates",
                    "finding": "The page contains only bibliographic citations to prior literature and article dates; there are no current-paper arrows, tables, footnotes, procedures, or independent experiments to extract.",
                    "evidence_ids": P8,
                }
            ],
            "record_ids": [],
            "unresolved": [
                "Cited prior-literature reactions were not converted into experiments of the current paper.",
            ],
        },
    ],
}


assert len(records) == 5
assert [page["page"] for page in coverage["pages"]] == [7, 8]
assert all(page["regions"] for page in coverage["pages"])

records_path = OUT / "records_pages_0007_0008.json"
records_path.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
coverage_path = ROOT / "coverage" / "pages_0007_0008.json"
coverage_path.parent.mkdir(parents=True, exist_ok=True)
coverage_path.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

tasks_path = ROOT / "tasks.json"
tasks = json.loads(tasks_path.read_text())
for task in tasks:
    if task["document_id"] == DOC and task["evidence_id"] in {ev(7, "text"), ev(8, "text")}:
        task["state"] = "attempted"
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({
    "records": len(records),
    "records_path": str(records_path),
    "coverage_path": str(coverage_path),
    "pages": [7, 8],
}, ensure_ascii=False))
