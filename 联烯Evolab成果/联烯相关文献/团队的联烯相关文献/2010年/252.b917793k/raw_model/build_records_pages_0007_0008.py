#!/usr/bin/env python3
"""Enrich existing b917793k records from original PDF pages 7--8.

Page 7 contains detailed continuations of experiments already represented by
Scheme 2, Table 3, and Scheme 5 records. Page 8 is references only. This
builder therefore emits updated copies of existing records and does not create
new experiment IDs.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
DATASET = ROOT / "runs/current/dataset.json"
OUT = Path(__file__).with_name("records_pages_0007_0008.json")
COVERAGE = ROOT / "runs/current/coverage/pages_0007_0008.json"
DOC = "doc_4e9a90c5ea8a1795"
P3 = [f"{DOC}:page3:text", f"{DOC}:page3:image"]
P4 = [f"{DOC}:page4:text", f"{DOC}:page4:image"]
P6 = [f"{DOC}:page6:text", f"{DOC}:page6:image"]
P7 = [f"{DOC}:page7:text", f"{DOC}:page7:image"]
P8 = [f"{DOC}:page8:text", f"{DOC}:page8:image"]


def unique(values):
    return list(dict.fromkeys(values))


def fact(value, evidence):
    return {
        "value": value,
        "evidence_ids": list(evidence) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def field(name, value, evidence):
    return {"name": name, "fact": fact(value, evidence)}


def qty(number, unit):
    return {"number": number, "unit": unit}


def participant_by_id(record, entity_id):
    return next(p for p in record["participants"] if p["entity_id"] == entity_id)


def add_record_evidence(record, evidence):
    record["evidence_ids"] = unique(record["evidence_ids"] + list(evidence))


def add_fact_evidence(obj, evidence):
    """Add corroborating evidence to all non-null facts under obj."""
    if isinstance(obj, dict):
        if {"value", "evidence_ids", "verification"} <= obj.keys():
            if obj["value"] is not None:
                obj["evidence_ids"] = unique(obj["evidence_ids"] + list(evidence))
            return
        for value in obj.values():
            add_fact_evidence(value, evidence)
    elif isinstance(obj, list):
        for value in obj:
            add_fact_evidence(value, evidence)


def upsert_amount(participant, name, value, evidence):
    item = next((x for x in participant["amounts"] if x["name"] == name), None)
    if item is None:
        participant["amounts"].append(field(name, value, evidence))
    else:
        item["fact"] = fact(value, evidence)


def upsert_condition(record, name, value, evidence):
    conditions = record["steps"][0]["conditions"]
    item = next((x for x in conditions if x["name"] == name), None)
    if item is None:
        conditions.append(field(name, value, evidence))
    else:
        item["fact"] = fact(value, evidence)


def ensure_step_participant(record, participant):
    if not any(p["entity_id"] == participant["entity_id"] for p in record["participants"]):
        record["participants"].append(participant)
    ids = record["steps"][0]["participant_ids"]
    if participant["entity_id"] not in ids:
        ids.append(participant["entity_id"])


def set_named_product(product, name, smiles, evidence):
    product["name"] = fact(name, evidence)
    product["smiles"] = fact(smiles, evidence)
    product["smiles_parseable"] = None
    product["structure_verified"] = False


data = json.loads(DATASET.read_text())
by_id = {r["record_id"]: r for r in data["experiments"]}
updates = []


# Scheme 2 Conditions A: page 7 only continues characterization of the same
# 2.01 mmol batch begun on page 6. Link it without inventing another reaction.
rid = f"{DOC}:scheme2_1m_conditionsA"
record = copy.deepcopy(by_id[rid])
add_record_evidence(record, P7)
for entity_id in ("product_4m", "product_E5m"):
    add_fact_evidence(participant_by_id(record, entity_id), P7)
record["notes"].append(fact(
    "Page 7 continues characterization of isolated 4m and E-5m; this is not a separate reaction batch.",
    P7,
))
updates.append(record)


# Scheme 2 Conditions B: page 7 supplies exact quantities and isolated masses.
rid = f"{DOC}:scheme2_1m_conditionsB"
record = copy.deepcopy(by_id[rid])
add_record_evidence(record, P7)
substrate = participant_by_id(record, "substrate")
upsert_amount(substrate, "amount", qty(0.20, "mmol"), P7)
upsert_amount(substrate, "mass", qty(61.8, "mg"), P7)
selectfluor = participant_by_id(record, "selectfluor")
upsert_amount(selectfluor, "amount", qty(0.34, "mmol"), P7)
upsert_amount(selectfluor, "mass", qty(126.3, "mg"), P7)
upsert_amount(selectfluor, "purity", qty(95, "%"), P7)
ensure_step_participant(record, {
    "entity_id": "mecn", "role": "solvent", "label": fact("MeCN", P7),
    "name": fact("acetonitrile", P7), "smiles": fact("CC#N", P7),
    "smiles_parseable": None, "structure_verified": False,
    "amounts": [field("volume", qty(1.3, "mL"), P7)],
})
ensure_step_participant(record, {
    "entity_id": "water", "role": "solvent", "label": fact("H2O", P7),
    "name": fact("water", P7), "smiles": fact("O", P7),
    "smiles_parseable": None, "structure_verified": False,
    "amounts": [field("volume", qty(0.65, "mL"), P7)],
})
product4m = participant_by_id(record, "product_4m")
set_named_product(product4m, "4-fluoro-5,5-diphenyl-3-propyl-2(5H)-furanone", "CCCC1=C(F)OC(c2ccccc2)(c2ccccc2)C1=O", P7)
upsert_amount(product4m, "mass", qty(51.6, "mg"), P7)
product5m = participant_by_id(record, "product_E5m")
set_named_product(product5m, "ethyl 3-fluoro-4-hydroxy-4,4-diphenyl-2-propyl-2(E)-butenoate", "CCOC(=O)C(CCC)=C(F)C(O)(c1ccccc1)c1ccccc1", P7)
upsert_amount(product5m, "mass", qty(4.9, "mg"), P7)
upsert_condition(record, "purification", "silica-gel chromatography; petroleum ether/ethyl acetate 20:1 to 5:1", P7)
record["review"]["unresolved"] = [
    "No SI is associated; candidate structures, including the E assignment of E-5m, remain unverified.",
    "The Conditions B paragraph does not restate a workup before chromatography.",
]
updates.append(record)


# Table 3 entries 7--13: detailed Conditions C batches on page 7. Workup and
# purification follow the page-6 Conditions C typical procedure.
scope = {
    7:  ("4n", "4-Fluoro-3,5-dimethyl-5-phenyl-2(5H)-furanone", "CC1=C(F)OC(C)(c2ccccc2)C1=O", 43.4, 0.20, 85.3, 0.24, "MeCN", 33.0, 80, None),
    8:  ("4o", "4-Fluoro-3-methyl-5,5-diphenyl-2(5H)-furanone", "CC1=C(F)OC(c2ccccc2)(c2ccccc2)C1=O", 55.8, 0.20, 85.3, 0.24, "MeCN", 49.9, 93, None),
    9:  ("4p", "5-Ethyl-4-fluoro-3-methyl-5-phenyl-2(5H)-furanone", "CC1=C(F)OC(CC)(c2ccccc2)C1=O", 45.5, 0.20, 85.1, 0.24, "MeCN", 41.5, 95, None),
    10: ("4q", "5-Ethyl-4-fluoro-5-phenyl-3-propyl-2(5H)-furanone", "CCCC1=C(F)OC(CC)(c2ccccc2)C1=O", 52.4, 0.20, 85.4, 0.24, "MeCN", 45.7, 91, None),
    11: ("4r", "5-Ethyl-4-fluoro-5-phenyl-2(5H)-furanone", "O=C1C=C(F)OC(CC)(c2ccccc2)1", 43.2, 0.20, 84.8, 0.24, "MeCN", 31.4, 76, None),
    12: ("4s", "4-Fluoro-3-methyl-1-oxaspiro[4.5]3-decen-2-one", "CC1=C(F)OC2(CCCCC2)C1=O", 39.7, 0.20, 90.9, 0.24, "MeCN", 11.2, 30, 95),
    13: ("4s", "4-Fluoro-3-methyl-1-oxaspiro[4.5]3-decen-2-one", "CC1=C(F)OC2(CCCCC2)C1=O", 37.8, 0.19, 88.5, 0.24, "MeNO2", 14.9, 42, 95),
}
for entry, values in scope.items():
    product_label, product_name, product_smiles, sub_mg, sub_mmol, sf_mg, sf_mmol, solvent_label, product_mg, yield_pct, purity = values
    rid = f"{DOC}:table3_entry{entry}_{product_label}"
    record = copy.deepcopy(by_id[rid])
    add_record_evidence(record, P6 + P7)
    substrate = participant_by_id(record, "substrate")
    upsert_amount(substrate, "mass", qty(sub_mg, "mg"), P7)
    upsert_amount(substrate, "amount", qty(sub_mmol, "mmol"), P7)
    selectfluor = participant_by_id(record, "selectfluor")
    upsert_amount(selectfluor, "mass", qty(sf_mg, "mg"), P7)
    upsert_amount(selectfluor, "amount", qty(sf_mmol, "mmol"), P7)
    if purity is not None:
        upsert_amount(selectfluor, "purity", qty(purity, "%"), P7)
    solvent = participant_by_id(record, "solvent")
    solvent["label"] = fact(solvent_label, P7)
    upsert_amount(solvent, "volume", qty(2, "mL"), P7)
    product = participant_by_id(record, "product")
    set_named_product(product, product_name, product_smiles, P7)
    upsert_amount(product, "mass", qty(product_mg, "mg"), P7)
    upsert_condition(record, "solvent", solvent_label, P7)
    upsert_condition(record, "workup", "water quench, ether extraction, brine wash, Na2SO4 drying, filtration and evaporation (Conditions C typical procedure)", P6 + P7)
    upsert_condition(record, "purification", "silica-gel chromatography; petroleum ether/ethyl acetate 30:1 (Conditions C typical procedure)", P6 + P7)
    # Page 7 independently restates the isolated yield and product identity.
    isolated_yield = next(x for x in record["outcomes"] if x["name"] == "isolated_yield")
    isolated_yield["fact"] = fact(qty(yield_pct, "%"), P3 + P7)
    record["review"]["unresolved"] = [
        "Candidate product SMILES was derived from the fully specified name and remains structure_verified=false.",
        "The main text refers to Conditions C for the workup/purification; no associated SI was supplied.",
    ]
    updates.append(record)


# Scheme 5 scale-up records: page 7 gives the full operational paragraphs.
for suffix in ("A", "B"):
    rid = f"{DOC}:scheme5_large_scale_conditions{suffix}"
    record = copy.deepcopy(by_id[rid])
    add_record_evidence(record, P7)
    # Every existing non-null fact except the Scheme-5-only ratio is explicitly
    # restated in the page-7 paragraph or its heading.
    for participant in record["participants"]:
        add_fact_evidence(participant, P7)
    for condition in record["steps"][0]["conditions"]:
        add_fact_evidence(condition, P7)
    for outcome in record["outcomes"]:
        if outcome["name"] != "product_ratio_3a_to_4a":
            add_fact_evidence(outcome, P7)
    if suffix == "A":
        product3a = participant_by_id(record, "product_3a")
        set_named_product(product3a, "ethyl 3-fluoro-2-methyl-4-oxo-4-phenyl-2(E)-butenoate", "CCOC(=O)C(C)=C(F)C(=O)c1ccccc1", P4 + P7)
        product4a = participant_by_id(record, "product_4a")
        set_named_product(product4a, "4-fluoro-3-methyl-5-phenyl-2(5H)-furanone", "CC1=C(F)OC(c2ccccc2)C1=O", P4 + P7)
    record["review"]["unresolved"] = [
        "No SI is associated; candidate structures and the E assignment remain unverified where applicable."
    ]
    updates.append(record)


expected_ids = {
    f"{DOC}:scheme2_1m_conditionsA",
    f"{DOC}:scheme2_1m_conditionsB",
    *{f"{DOC}:table3_entry{i}_{scope[i][0]}" for i in scope},
    f"{DOC}:scheme5_large_scale_conditionsA",
    f"{DOC}:scheme5_large_scale_conditionsB",
}
assert len(updates) == 11
assert {r["record_id"] for r in updates} == expected_ids

OUT.write_text(json.dumps(updates, ensure_ascii=False, indent=2) + "\n")

page7_ids = [
    f"{DOC}:scheme2_1m_conditionsA",
    f"{DOC}:scheme2_1m_conditionsB",
    *[f"{DOC}:table3_entry{i}_{scope[i][0]}" for i in range(7, 14)],
    f"{DOC}:scheme5_large_scale_conditionsA",
    f"{DOC}:scheme5_large_scale_conditionsB",
]
ledger = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 7,
            "state": "attempted",
            "regions": [
                {
                    "region": "upper-left continuation of 1m Conditions A characterization and Conditions B paragraph",
                    "finding": "The opening spectra continue the existing Conditions A 1m batch. The following paragraph gives exact quantities, solvent volumes, isolated masses/yields, and chromatography for the distinct Conditions B batch; neither was duplicated as a new experiment ID.",
                    "evidence_ids": P7,
                },
                {
                    "region": "left column sections (2)–(6), Conditions C products 4n–4r",
                    "finding": "Five detailed batches were reconciled with Table 3 entries 7–11. Exact substrate and Selectfluor masses/mmol, 2 mL MeCN, 80 °C, product masses, and isolated yields were added; the shared Conditions C workup/purification was linked from its page-6 typical procedure.",
                    "evidence_ids": P7,
                },
                {
                    "region": "upper-right section (7), product 4s in MeCN and MeNO2",
                    "finding": "Two distinct 4s batches were retained as Table 3 entries 12 and 13 because substrate scale, Selectfluor mass, solvent, time, product mass, and yield differ. The explicitly stated 95% Selectfluor purity was structured for both.",
                    "evidence_ids": P7,
                },
                {
                    "region": "right-column section 4, large scale reactions (1) and (2)",
                    "finding": "The full operational paragraphs for the two 5 mmol Conditions A/B scale-ups were merged with the existing Scheme 5 records, adding page-7 evidence for exact quantities, atmosphere where stated, times, workups, purification, product masses, and isolated yields.",
                    "evidence_ids": P7,
                },
                {
                    "region": "bottom-right acknowledgements",
                    "finding": "Funding and reproducibility acknowledgements contain no additional independent reaction conditions or outcomes; referenced table entries are already represented.",
                    "evidence_ids": P7,
                },
            ],
            "record_ids": page7_ids,
            "unresolved": [
                "The paper advertises ESI, but no supplement was explicitly supplied or associated.",
                "Spectra were recognized as characterization and were not interpreted atom by atom.",
                "Candidate connectivity and stereochemical assignments remain machine-unverified.",
            ],
        },
        {
            "page": 8,
            "state": "attempted",
            "regions": [
                {
                    "region": "entire two-column References section",
                    "finding": "The page contains bibliography entries 1–15 only. These are cited reviews and prior literature, with no current-paper experimental procedure, reaction arrow, table, footnote condition, or new batch to extract.",
                    "evidence_ids": P8,
                }
            ],
            "record_ids": [],
            "unresolved": [
                "Bibliographic citations were not promoted to experiments of the current paper."
            ],
        },
    ],
}
COVERAGE.parent.mkdir(parents=True, exist_ok=True)
COVERAGE.write_text(json.dumps(ledger, ensure_ascii=False, indent=2) + "\n")
print(f"wrote {len(updates)} updated records to {OUT}")
print(COVERAGE)
