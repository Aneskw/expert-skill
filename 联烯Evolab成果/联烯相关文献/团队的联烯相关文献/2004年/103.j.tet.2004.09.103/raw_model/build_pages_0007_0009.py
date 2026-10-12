#!/usr/bin/env python3
"""Enrich existing records with source-derived details from PDF pages 7-9."""

import copy
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
DATASET = ROOT / "runs/current/dataset.json"
OUT = ROOT / "runs/current/raw_model/extracted_records_pages_0007_0009.json"
COVERAGE = ROOT / "runs/current/coverage/pages_0007_0009.json"
TASKS = ROOT / "runs/current/tasks.json"
DOC = "doc_a746be3717c6f516"


def ev(page, kind):
    return f"{DOC}:page{page}:{kind}"


def page_evidence(page):
    return [ev(page, "image"), ev(page, "text")]


def unique(values):
    return list(dict.fromkeys(values))


def fact(value, evidence):
    return {
        "value": value,
        "evidence_ids": list(evidence) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def field(name, value, evidence, targets=None):
    item = {"name": name, "fact": fact(value, evidence)}
    if targets:
        item["target_entity_ids"] = list(targets)
    return item


def qty(number, unit):
    return {"number": number, "unit": unit}


def participant(entity_id, role, label, name, evidence, smiles=None, amounts=()):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence),
        "smiles": fact(smiles, evidence if smiles is not None else ()),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": list(amounts),
    }


def add_fact_evidence(fact_obj, evidence):
    if fact_obj["value"] is not None:
        fact_obj["evidence_ids"] = unique(fact_obj["evidence_ids"] + list(evidence))


def find_participant(record, entity_id):
    return next(item for item in record["participants"] if item["entity_id"] == entity_id)


def find_outcome(record, name):
    return next(item for item in record["outcomes"] if item["name"] == name)


def upsert_amount(participant_obj, name, value, evidence):
    existing = next((item for item in participant_obj["amounts"] if item["name"] == name), None)
    if existing is None:
        participant_obj["amounts"].append(field(name, value, evidence))
    else:
        existing["fact"]["value"] = value
        add_fact_evidence(existing["fact"], evidence)


data = json.loads(DATASET.read_text())
existing = {item["record_id"]: item for item in data["experiments"]}


scope = {
    9: {
        "suffix": "table3_entry09_1i",
        "pages": [7],
        "reaction_page": 7,
        "base": "6-cyclohexylidene-5-(n-butyl)hexa-5-en-3-ol",
        "alcohol": "(S)-6-cyclohexylidene-5-(n-butyl)hexa-5-en-3-ol",
        "ester": "(R)-6-cyclohexylidene-5-(n-butyl)hex-5-en-3-yl acetate",
        "vinyl_uL": 78,
        "alcohol_mg": 42,
        "ester_mg": 60,
        "measurement": "Alcohol ee was determined after conversion to the corresponding benzoate by HPLC; ester ee was determined after conversion to the corresponding benzoate.",
    },
    10: {
        "suffix": "table3_entry10_1j",
        "pages": [7],
        "reaction_page": 7,
        "base": "4-(n-butyl)hexa-4,5-dien-2-ol",
        "alcohol": "(S)-4-(n-butyl)hexa-4,5-dien-2-ol",
        "ester": "(R)-4-(n-butyl)hexa-4,5-dien-2-yl acetate",
        "vinyl_uL": 120,
        "alcohol_mg": 37,
        "ester_mg": 45,
        "measurement": "Alcohol ee was determined after conversion to the corresponding acetate; ester ee was determined by GC.",
        "experimental_ester_ee": 89.3,
    },
    11: {
        "suffix": "table3_entry11_1k",
        "pages": [7],
        "reaction_page": 7,
        "base": "6-methyl-4-(n-butyl)hepta-4,5-dien-2-ol",
        "alcohol": "(S)-6-methyl-4-(n-butyl)hepta-4,5-dien-2-ol",
        "ester": "(R)-6-methyl-4-(n-butyl)hepta-4,5-dien-2-yl acetate",
        "vinyl_uL": 102,
        "alcohol_mg": 38,
        "ester_mg": 64,
        "measurement": "Alcohol ee was determined after conversion to the corresponding acetate; ester ee was determined by GC.",
    },
    12: {
        "suffix": "table3_entry12_1l",
        "pages": [7],
        "reaction_page": 7,
        "base": "5-(n-butyl)hepta-1,5,6-trien-3-ol",
        "alcohol": "(R)-5-(n-butyl)hepta-1,5,6-trien-3-ol",
        "ester": "(S)-5-(n-butyl)hepta-1,5,6-trien-3-yl acetate",
        "vinyl_uL": 111,
        "alcohol_mg": 43,
        "ester_mg": 70,
        "measurement": "Alcohol ee was determined after conversion to the corresponding acetate; ester ee was determined by GC.",
    },
    13: {
        "suffix": "table3_entry13_1m",
        "pages": [7, 8],
        "reaction_page": 7,
        "base": "5-(n-pentyl)hepta-1,5,6-trien-3-ol",
        "alcohol": "(R)-5-(n-pentyl)hepta-1,5,6-trien-3-ol",
        "ester": "(S)-5-(n-pentyl)hepta-1,5,6-trien-3-yl acetate",
        "vinyl_uL": 103,
        "alcohol_mg": 44,
        "ester_mg": 49,
        "measurement": "Alcohol ee was determined after conversion to the corresponding acetate; ester ee was determined by GC.",
    },
    14: {
        "suffix": "table3_entry14_1n",
        "pages": [8],
        "reaction_page": 8,
        "base": "5-(n-butyl)hepta-5,6-dien-1-yn-3-ol",
        "alcohol": "(R)-5-(n-butyl)hepta-5,6-dien-1-yn-3-ol",
        "ester": "(S)-5-(n-butyl)hepta-5,6-dien-1-yn-3-yl acetate",
        "vinyl_uL": 113,
        "alcohol_mg": 38,
        "ester_mg": 71,
        "measurement": "Alcohol ee was determined after conversion to the corresponding acetate; ester ee was determined by GC.",
    },
    15: {
        "suffix": "table3_entry15_1o",
        "pages": [8],
        "reaction_page": 8,
        "base": "5-(n-pentyl)hepta-5,6-dien-1-yn-3-ol",
        "alcohol": "(R)-5-(n-pentyl)hepta-5,6-dien-1-yn-3-ol",
        "ester": "(S)-5-(n-pentyl)hepta-5,6-dien-1-yn-3-yl acetate",
        "vinyl_uL": 103,
        "alcohol_mg": 40,
        "ester_mg": 50,
        "measurement": "Alcohol ee was determined after conversion to the corresponding acetate; ester ee was determined by GC.",
    },
}


records = []
for entry, detail in scope.items():
    record_id = f"{DOC}:{detail['suffix']}"
    record = copy.deepcopy(existing[record_id])
    all_evidence = unique(sum((page_evidence(page) for page in detail["pages"]), []))
    reaction_evidence = page_evidence(detail["reaction_page"])
    record["evidence_ids"] = unique(record["evidence_ids"] + all_evidence)

    prefix = f"t3e{entry:02d}"
    substrate = find_participant(record, f"{prefix}_substrate")
    alcohol = find_participant(record, f"{prefix}_alcohol")
    ester = find_participant(record, f"{prefix}_ester")
    vinyl = find_participant(record, f"{prefix}_va")
    enzyme = find_participant(record, f"{prefix}_enzyme")

    substrate["name"] = fact(f"racemic {detail['base']}", reaction_evidence)
    alcohol["name"] = fact(detail["alcohol"], all_evidence)
    ester["name"] = fact(detail["ester"], all_evidence)
    for item in (substrate, alcohol, ester):
        add_fact_evidence(item["label"], all_evidence)
        add_fact_evidence(item["smiles"], all_evidence)

    upsert_amount(substrate, "mass", qty(100, "mg"), reaction_evidence)
    upsert_amount(vinyl, "volume", qty(detail["vinyl_uL"], "uL"), reaction_evidence)
    enzyme_mass = next(item["fact"]["value"] for item in enzyme["amounts"] if item["name"] == "mass")
    upsert_amount(enzyme, "mass", enzyme_mass, reaction_evidence)
    upsert_amount(alcohol, "isolated_mass", qty(detail["alcohol_mg"], "mg"), reaction_evidence)
    upsert_amount(ester, "isolated_mass", qty(detail["ester_mg"], "mg"), reaction_evidence)

    for outcome_name in ("alcohol_yield", "table_alcohol_ee", "ester_yield", "ester_ee"):
        outcome = find_outcome(record, outcome_name)
        outcome_evidence = all_evidence if entry == 13 else reaction_evidence
        add_fact_evidence(outcome["fact"], outcome_evidence)

    if entry == 10:
        table_ester_ee = find_outcome(record, "ester_ee")
        table_ester_ee["name"] = "table_ester_ee"
        record["outcomes"].append(field(
            "experimental_ester_ee",
            qty(detail["experimental_ester_ee"], "%"),
            reaction_evidence,
            [ester["entity_id"]],
        ))

    record["notes"].append(fact(detail["measurement"], all_evidence))
    record["review"]["unresolved"] = [
        item for item in record["review"]["unresolved"]
        if not item.startswith("Pages 1–6 do not contain")
    ]
    record["review"]["unresolved"].append(
        "The individual experimental paragraph does not state a separate workup or purification; shared reaction conditions remain sourced from Table 3."
    )
    if entry == 10:
        record["review"]["unresolved"].append(
            "Table 3 reports ester ee 89%, while section 3.2.10 reports 89.3% for the same 2j product; both values are retained."
        )
    record["review"]["unresolved"] = unique(record["review"]["unresolved"])
    records.append(record)


# The detailed section 3.2.16 paragraph describes the same reaction as Eq. 3.
eq3_id = f"{DOC}:eq3_pd_coupling_cyclization"
eq3 = copy.deepcopy(existing[eq3_id])
p8 = page_evidence(8)
eq3["evidence_ids"] = unique(eq3["evidence_ids"] + p8)

r1a = find_participant(eq3, "eq3_r1a")
allyl = find_participant(eq3, "eq3_allyl_bromide")
pdcl2 = find_participant(eq3, "eq3_pdcl2")
dma = find_participant(eq3, "eq3_dma")
product = find_participant(eq3, "eq3_r3a")
for item in (r1a, allyl, pdcl2, dma, product):
    add_fact_evidence(item["label"], p8)
    add_fact_evidence(item["name"], p8)
    add_fact_evidence(item["smiles"], p8)

allyl["label"] = fact("allyl bromide", p8)
upsert_amount(r1a, "mass", qty(52, "mg"), p8)
upsert_amount(r1a, "amount", qty(0.3, "mmol"), p8)
upsert_amount(r1a, "reactant_ee", qty(97, "%"), p8)
upsert_amount(allyl, "volume", qty(0.13, "mL"), p8)
upsert_amount(allyl, "amount", qty(1.5, "mmol"), p8)
upsert_amount(pdcl2, "mass", qty(0.003, "g"), p8)
upsert_amount(pdcl2, "catalyst_loading", qty(5, "mol%"), p8)
upsert_amount(dma, "volume", qty(1.8, "mL"), p8)
upsert_amount(product, "isolated_mass", qty(41, "mg"), p8)

# Candidate constitution from the fully named and depicted product; stereochemistry is not encoded.
product["smiles"] = fact("O1CC(CC=C)=C(CCCC)CC(CC)1", [ev(4, "image"), *p8])

ether = participant(
    "eq3_ether", "solvent", "diethyl ether", "diethyl ether", p8, "CCOCC",
    [field("volume", qty(50, "mL"), p8)],
)
brine = participant("eq3_brine", "reagent", "brine", "brine", p8)
na2so4 = participant(
    "eq3_na2so4", "reagent", "anhydrous Na2SO4", "anhydrous sodium sulfate", p8,
    "[Na+].[Na+].[O-]S(=O)(=O)[O-]",
)
eq3["participants"].extend([ether, brine, na2so4])

reaction_step = next(item for item in eq3["steps"] if item["step_id"] == "coupling_cyclization")
reaction_step["conditions"].append(field("experimental_temperature", "r.t.", p8))
reaction_step["conditions"].append(field("reaction_monitoring", "until complete as monitored by TLC", p8))
eq3["steps"].append({
    "step_id": "workup_and_purification",
    "participant_ids": ["eq3_ether", "eq3_brine", "eq3_na2so4", "eq3_r3a"],
    "conditions": [
        field("operation", "add diethyl ether; wash with brine three times; dry over anhydrous sodium sulfate", p8),
        field("purification", "silica-gel column chromatography; petroleum ether/ethyl ether 80:1", p8),
    ],
})
for outcome_name in ("product_yield", "product_ee"):
    add_fact_evidence(find_outcome(eq3, outcome_name)["fact"], p8)
eq3["outcomes"].append(field("yield_measurement_basis", None, (), ["eq3_r3a"]))
eq3["notes"].append(fact("The (R)-1a reactant was obtained by hydrolysis of (R)-2a.", p8))
eq3["review"]["unresolved"] = [
    "Reaction atmosphere, explicit yield basis, and SI association are not reported.",
    "The product SMILES is a constitution-only candidate; the reported/depicted absolute configuration remains structure-unverified.",
]
records.append(eq3)


def rid(suffix):
    return f"{DOC}:{suffix}"


coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 7,
            "state": "attempted",
            "regions": [
                {
                    "region": "upper-left continuation of section 3.2.9",
                    "finding": "Detailed 1i kinetic-resolution quantities and product selectivity/characterization; merged into existing Table 3 entry 9 rather than duplicated.",
                    "evidence_ids": page_evidence(7),
                },
                {
                    "region": "left column sections 3.2.10-3.2.11",
                    "finding": "Detailed 1j and 1k kinetic resolutions. Section 3.2.10 gives 89.3% ee for 2j versus 89% in Table 3; both are retained.",
                    "evidence_ids": page_evidence(7),
                },
                {
                    "region": "right column sections 3.2.12 and beginning of 3.2.13",
                    "finding": "Detailed 1l kinetic resolution and the reaction/output portion of 1m; 1m characterization continues on page 8.",
                    "evidence_ids": page_evidence(7),
                },
            ],
            "record_ids": [
                rid("table3_entry09_1i"), rid("table3_entry10_1j"), rid("table3_entry11_1k"),
                rid("table3_entry12_1l"), rid("table3_entry13_1m"),
            ],
            "unresolved": [
                "The individual scope paragraphs do not repeat the shared reaction time, temperature, cyclohexane volume, workup, or purification.",
                "Absolute configurations remain the authors' tentative Table 3 assignments and are not encoded in the constitution-only SMILES candidates.",
            ],
        },
        {
            "page": 8,
            "state": "attempted",
            "regions": [
                {
                    "region": "upper-left continuation of section 3.2.13",
                    "finding": "Continuation of 1m product characterization, including 85% ee for (S)-2m; merged with the page-7/Table-3 record.",
                    "evidence_ids": page_evidence(8),
                },
                {
                    "region": "left column sections 3.2.14-3.2.15 and upper-right continuation",
                    "finding": "Detailed 1n and 1o kinetic resolutions with substrate/enzyme/vinyl-acetate amounts, two product masses/yields, and ee values.",
                    "evidence_ids": page_evidence(8),
                },
                {
                    "region": "right column section 3.2.16",
                    "finding": "Detailed PdCl2-catalyzed coupling/cyclization corresponding to Eq. 3, including scale, room-temperature/TLC monitoring, workup, purification, isolated mass, 64% yield, and 97% ee.",
                    "evidence_ids": page_evidence(8),
                },
                {
                    "region": "lower-right acknowledgements and start of references",
                    "finding": "Funding acknowledgements and prior-literature references; no additional reported experiment.",
                    "evidence_ids": page_evidence(8),
                },
            ],
            "record_ids": [
                rid("table3_entry13_1m"), rid("table3_entry14_1n"), rid("table3_entry15_1o"),
                rid("eq3_pd_coupling_cyclization"),
            ],
            "unresolved": [
                "The individual 1n/1o paragraphs do not state separate workup or purification details.",
                "The Pd experiment does not state an atmosphere or explicit yield basis; no SI was supplied or associated.",
            ],
        },
        {
            "page": 9,
            "state": "attempted",
            "regions": [
                {
                    "region": "entire two-column page, references 2-18",
                    "finding": "Bibliographic references to prior literature only; no arrow, table, experimental procedure, or new experiment reported by this paper.",
                    "evidence_ids": page_evidence(9),
                },
            ],
            "record_ids": [],
            "unresolved": [],
        },
    ],
}


OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
COVERAGE.parent.mkdir(parents=True, exist_ok=True)
COVERAGE.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

tasks = json.loads(TASKS.read_text())
for item in tasks:
    page = int(item["evidence_id"].split(":page", 1)[1].split(":", 1)[0])
    if 7 <= page <= 9:
        item["state"] = "attempted"
        item["visual_evidence_id"] = ev(page, "image")
        item["reason"] = "Original page image inspected; regions and record mappings saved in coverage/pages_0007_0009.json."
TASKS.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({
    "submitted_records": len(records),
    "new_record_ids": 0,
    "updated_record_ids": len(records),
    "coverage_pages": [item["page"] for item in coverage["pages"]],
    "output": str(OUT),
}, ensure_ascii=False))
