#!/usr/bin/env python3
"""Enrich existing records for doc_35087b7314dcb02b from PDF pages 7-9."""
from __future__ import annotations

import copy
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / "runs/current"
DOC = "doc_35087b7314dcb02b"
P7 = [f"{DOC}:page7:image", f"{DOC}:page7:text"]
P8 = [f"{DOC}:page8:image", f"{DOC}:page8:text"]


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


def add_unique(seq, values):
    for value in values:
        if value not in seq:
            seq.append(value)


def find_part(record, entity_id):
    return next(p for p in record["participants"] if p["entity_id"] == entity_id)


def touch_fact(item, evidence, value=None):
    target = item["fact"] if "fact" in item else item
    if value is not None:
        target["value"] = value
        target["verification"] = "unreviewed"
    add_unique(target["evidence_ids"], evidence)


def upsert_field(items, name, value, evidence, targets=None):
    for item in items:
        if item["name"] == name:
            item["fact"] = fact(value, evidence)
            if targets:
                item["target_entity_ids"] = list(targets)
            return item
    item = field(name, value, evidence, targets)
    items.append(item)
    return item


def add_participant(record, entity_id, role, label, evidence, amounts=(), smiles=None, name=None):
    participant = {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence) if name else fact(None, []),
        "smiles": fact(smiles, evidence) if smiles else fact(None, []),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": [field(n, v, evidence) for n, v in amounts],
    }
    record["participants"].append(participant)
    add_unique(record["steps"][0]["participant_ids"], [entity_id])
    return participant


def add_note(record, value, evidence):
    if value not in [n["value"] for n in record["notes"]]:
        record["notes"].append(fact(value, evidence))


def replace_unresolved(record, old_fragments, new_items):
    kept = [
        item for item in record["review"]["unresolved"]
        if not any(fragment in item for fragment in old_fragments)
    ]
    for item in new_items:
        if item not in kept:
            kept.append(item)
    record["review"]["unresolved"] = kept


dataset = json.loads((RUN / "dataset.json").read_text())
by_id = {record["record_id"]: record for record in dataset["experiments"]}

ids = [
    f"{DOC}:table2_entry1",
    f"{DOC}:table4_entry1_conditions_a",
    f"{DOC}:table4_entry1_conditions_b",
    f"{DOC}:table5_entry1_conditions_c",
    f"{DOC}:table5_entry1_conditions_d",
]
records = {rid: copy.deepcopy(by_id[rid]) for rid in ids}


def common_detailed_setup(record, evidence, substrate_mass, iron_mass, iron_amount,
                          detailed_loading, product_name, product_smiles):
    add_unique(record["evidence_ids"], evidence)
    allenoate = find_part(record, "allenoate")
    touch_fact(allenoate["label"], evidence)
    touch_fact(allenoate["smiles"], evidence)
    upsert_field(allenoate["amounts"], "amount", {"number": 0.4, "unit": "mmol"}, evidence)
    upsert_field(allenoate["amounts"], "mass", {"number": substrate_mass, "unit": "mg"}, evidence)

    grignard = find_part(record, "grignard")
    touch_fact(grignard["label"], evidence, "methylmagnesium chloride")
    upsert_field(grignard["amounts"], "equivalents", {"number": 3, "unit": "equiv"}, evidence)
    upsert_field(grignard["amounts"], "amount", {"number": 1.2, "unit": "mmol"}, evidence)
    upsert_field(grignard["amounts"], "concentration", {"number": 3, "unit": "M"}, evidence)
    upsert_field(grignard["amounts"], "volume", {"number": 0.4, "unit": "mL"}, evidence)

    iron = find_part(record, "iron_catalyst")
    touch_fact(iron["label"], evidence)
    upsert_field(iron["amounts"], "detailed_procedure_catalyst_loading",
                 {"number": detailed_loading, "unit": "mol%"}, evidence)
    upsert_field(iron["amounts"], "mass", {"number": iron_mass, "unit": "mg"}, evidence)
    upsert_field(iron["amounts"], "amount", {"number": iron_amount, "unit": "mmol"}, evidence)

    toluene = find_part(record, "toluene")
    touch_fact(toluene["label"], evidence)
    touch_fact(toluene["smiles"], evidence)
    upsert_field(toluene["amounts"], "volume", {"number": 5, "unit": "mL"}, evidence)

    product = find_part(record, "product")
    touch_fact(product["label"], evidence)
    product["name"] = fact(product_name, evidence)
    product["smiles"] = fact(product_smiles, evidence)
    product["smiles_parseable"] = None
    product["structure_verified"] = False

    upsert_field(record["steps"][0]["conditions"], "atmosphere", "nitrogen", evidence)
    upsert_field(record["steps"][0]["conditions"], "grignard_addition",
                 "CH3MgCl solution was added by syringe within 3 min at -78 °C", evidence)

    quench = next((p for p in record["participants"] if p["entity_id"] == "quench"), None)
    if quench is None:
        quench = add_participant(record, "quench", "reagent", "saturated aqueous ammonium chloride",
                                 evidence, [("volume", {"number": 1, "unit": "mL"})],
                                 smiles="[Cl-].[NH4+]")
    else:
        touch_fact(quench["label"], evidence)
        upsert_field(quench["amounts"], "volume", {"number": 1, "unit": "mL"}, evidence)

    if not any(p["entity_id"] == "diethyl_ether" for p in record["participants"]):
        add_participant(
            record, "diethyl_ether", "solvent", "diethyl ether", evidence,
            [("extraction_volume", {"number": 30, "unit": "mL", "raw_text": "30 mL × 3"})],
            smiles="CCOCC",
        )


# Complete the cross-page typical Z-5a procedure (Table 2 entry 1).
r = records[f"{DOC}:table2_entry1"]
add_unique(r["evidence_ids"], P7)
grignard = find_part(r, "grignard")
touch_fact(grignard["label"], P7, "methylmagnesium chloride")
touch_fact(grignard["smiles"], [])
upsert_field(grignard["amounts"], "amount", {"number": 1.2, "unit": "mmol"}, P7)
upsert_field(find_part(r, "quench")["amounts"], "volume", {"number": 1, "unit": "mL"}, P7)
add_participant(r, "water_workup", "reagent", "water", P7,
                [("volume", {"number": 5, "unit": "mL"})], smiles="O")
add_participant(r, "diethyl_ether", "solvent", "diethyl ether", P7,
                [("extraction_volume", {"number": 30, "unit": "mL", "raw_text": "30 mL × 3"})],
                smiles="CCOCC")
product = find_part(r, "product")
product["name"] = fact("ethyl 3-methyl-4-phenyl-2-propyl-3(Z)-butenoate", P7)
touch_fact(product["label"], P7)
touch_fact(product["smiles"], P7)
upsert_field(r["steps"][0]["conditions"], "grignard_addition",
             "CH3MgCl solution was added by syringe within 3 min at -78 °C", P7)
upsert_field(r["steps"][0]["conditions"], "workup",
             "Quenched slowly with saturated aqueous NH4Cl (1 mL) at -78 °C; warmed naturally to room temperature; added water (5 mL); extracted with diethyl ether (30 mL × 3); washed successively with 5% aqueous HCl, saturated aqueous NaHCO3, and brine; dried over anhydrous Na2SO4; filtered and evaporated.", P7)
upsert_field(r["steps"][0]["conditions"], "purification",
             "Silica-gel column chromatography; petroleum ether/ethyl acetate = 100:1", P7)
upsert_field(r["outcomes"], "isolated_product_mass", {"number": 86.2, "unit": "mg"}, P7, ["product"])
for outcome in r["outcomes"]:
    if outcome["name"] in {"isolated_yield", "yield_measurement_basis"}:
        touch_fact(outcome, P7)
r["notes"] = [n for n in r["notes"] if not (isinstance(n["value"], str) and n["value"].startswith("Page 6 begins"))]
add_note(r, "The detailed typical procedure begins on page 6 and is completed on page 7.", P7)
replace_unresolved(
    r,
    ["Full workup and purification"],
    ["Product connectivity and alkene geometry are machine-interpreted and remain unverified."],
)


# Table 4 entry 1, Conditions A: detailed Z-9a batch.
r = records[f"{DOC}:table4_entry1_conditions_a"]
common_detailed_setup(
    r, P7, substrate_mass=81.8, iron_mass=2.6, iron_amount=0.010,
    detailed_loading=2.4,
    product_name="ethyl 2-acetyl-2,3-dimethyl-4-phenyl-3(Z)-butenoate",
    product_smiles="CCOC(=O)C(C)(C(=O)C)C(C)=Cc1ccccc1",
)
electrophile = find_part(r, "electrophile")
touch_fact(electrophile["label"], P7)
touch_fact(electrophile["smiles"], P7)
upsert_field(electrophile["amounts"], "amount", {"number": 2, "unit": "mmol"}, P7)
upsert_field(electrophile["amounts"], "equivalents", {"number": 5, "unit": "equiv"}, P7)
upsert_field(electrophile["amounts"], "mass", {"number": 154.6, "unit": "mg"}, P7)
upsert_field(electrophile["amounts"], "volume", {"number": 0.14, "unit": "mL"}, P7)
upsert_field(electrophile["amounts"], "reported_density", "1.104 g mL−1", P7)
upsert_field(r["steps"][0]["conditions"], "detailed_procedure_second_stage_time",
             {"number": 1.5, "unit": "h"}, P7)
upsert_field(r["steps"][0]["conditions"], "electrophile_addition",
             "Acetyl chloride was added slowly dropwise at -78 °C", P7)
upsert_field(r["steps"][0]["conditions"], "workup",
             "Quenched slowly with saturated aqueous NH4Cl (1 mL) at -78 °C; warmed naturally to room temperature; extracted with diethyl ether (30 mL × 3); washed successively with 5% aqueous HCl, saturated aqueous NaHCO3, and brine; dried over anhydrous Na2SO4; filtered and evaporated.", P7)
upsert_field(r["steps"][0]["conditions"], "purification",
             "Silica-gel column chromatography; petroleum ether/ethyl acetate = 100:1 to 20:1", P7)
upsert_field(r["outcomes"], "isolated_product_mass", {"number": 68.7, "unit": "mg"}, P7, ["product"])
for outcome in r["outcomes"]:
    if outcome["name"] in {"isolated_yield", "yield_measurement_basis"}:
        touch_fact(outcome, P7)
add_note(r, "The Table 4 drawing states 5 mol% FeCl3·6H2O, whereas the detailed Z-9a procedure reports 2.4 mol% (2.6 mg, 0.010 mmol); both source statements are retained.", P7)
replace_unresolved(
    r,
    ["Reaction atmosphere", "Product structure"],
    [
        "The table and detailed procedure disagree on FeCl3·6H2O loading (5 mol% versus 2.4 mol%).",
        "Product connectivity and Z geometry remain unverified.",
    ],
)


# Table 4 entry 1, Conditions B: detailed E-9a batch.
r = records[f"{DOC}:table4_entry1_conditions_b"]
common_detailed_setup(
    r, P7, substrate_mass=80.9, iron_mass=2.2, iron_amount=0.008,
    detailed_loading=2,
    product_name="ethyl 2-acetyl-2,3-dimethyl-4-phenyl-3(E)-butenoate",
    product_smiles="CCOC(=O)C(C)(C(=O)C)C(C)=Cc1ccccc1",
)
electrophile = find_part(r, "electrophile")
touch_fact(electrophile["label"], P7)
touch_fact(electrophile["smiles"], P7)
upsert_field(electrophile["amounts"], "amount", {"number": 2, "unit": "mmol"}, P7)
upsert_field(electrophile["amounts"], "equivalents", {"number": 5, "unit": "equiv"}, P7)
upsert_field(electrophile["amounts"], "mass", {"number": 204.2, "unit": "mg"}, P7)
upsert_field(electrophile["amounts"], "volume", {"number": 0.22, "unit": "mL"}, P7)
upsert_field(electrophile["amounts"], "reported_density", "0.928 g mL−1", P7)
upsert_field(r["steps"][0]["conditions"], "electrophile_addition",
             "Allyl acetate was added slowly dropwise at -78 °C, followed by natural warming to room temperature", P7)
upsert_field(r["steps"][0]["conditions"], "workup",
             "Quenched with saturated aqueous NH4Cl (1 mL) at 0 °C; warmed naturally to room temperature; extracted with diethyl ether (30 mL × 3); washed successively with 5% aqueous HCl, saturated aqueous NaHCO3, and brine; dried over anhydrous Na2SO4; filtered and evaporated.", P7)
upsert_field(r["steps"][0]["conditions"], "purification",
             "Silica-gel column chromatography; petroleum ether/ethyl acetate = 100:1 to 20:1", P7)
upsert_field(r["outcomes"], "isolated_product_mass", {"number": 51.8, "unit": "mg"}, P7, ["product"])
for outcome in r["outcomes"]:
    if outcome["name"] in {"isolated_yield", "yield_measurement_basis"}:
        touch_fact(outcome, P7)
add_note(r, "The Table 4 drawing states 5 mol% FeCl3·6H2O, whereas the detailed E-9a procedure reports 2 mol% (2.2 mg, 0.008 mmol); both source statements are retained.", P7)
replace_unresolved(
    r,
    ["Reaction atmosphere"],
    [
        "The table and detailed procedure disagree on FeCl3·6H2O loading (5 mol% versus 2 mol%).",
        "The shared hydrolysis-product range cannot be assigned to an individual Conditions B row.",
        "Product connectivity and E geometry remain unverified.",
    ],
)


# Table 5 entry 1, Conditions C: detailed Z-10a batch.
r = records[f"{DOC}:table5_entry1_conditions_c"]
common_detailed_setup(
    r, P7, substrate_mass=81.8, iron_mass=1.9, iron_amount=0.008,
    detailed_loading=1.8,
    product_name="ethyl 2-allyl-2,3-dimethyl-4-phenyl-3(Z)-butenoate",
    product_smiles="CCOC(=O)C(C)(CC=C)C(C)=Cc1ccccc1",
)
allyl = find_part(r, "allyl_reagent")
touch_fact(allyl["label"], P7)
touch_fact(allyl["smiles"], P7)
upsert_field(allyl["amounts"], "amount", {"number": 2, "unit": "mmol"}, P7)
upsert_field(allyl["amounts"], "equivalents", {"number": 5, "unit": "equiv"}, P7)
upsert_field(allyl["amounts"], "mass", {"number": 204.2, "unit": "mg"}, P7)
upsert_field(allyl["amounts"], "volume", {"number": 0.22, "unit": "mL"}, P7)
upsert_field(allyl["amounts"], "reported_density", "0.928 g mL−1", P7)
pd = find_part(r, "transition_catalyst")
touch_fact(pd["label"], P7)
upsert_field(pd["amounts"], "mass", {"number": 22.4, "unit": "mg"}, P7)
upsert_field(pd["amounts"], "amount", {"number": 0.02, "unit": "mmol"}, P7)
upsert_field(r["steps"][0]["conditions"], "allylation_addition",
             "Pd(PPh3)4 was added, then allyl acetate was added dropwise at -78 °C; the mixture was warmed naturally to room temperature", P7)
upsert_field(r["steps"][0]["conditions"], "workup",
             "Quenched with saturated aqueous NH4Cl (1 mL) at 0 °C; warmed naturally to room temperature; extracted with diethyl ether (30 mL × 3); washed successively with 5% aqueous HCl, saturated aqueous NaHCO3, and brine; dried over anhydrous Na2SO4; filtered and evaporated.", P7)
upsert_field(r["steps"][0]["conditions"], "purification",
             "Silica-gel column chromatography; petroleum ether/CH2Cl2 = 8:1, then petroleum ether/ethyl acetate = 100:1", P7)
upsert_field(r["outcomes"], "isolated_product_mass", {"number": 79.1, "unit": "mg"}, P7, ["product"])
for outcome in r["outcomes"]:
    if outcome["name"] in {"isolated_yield", "yield_measurement_basis"}:
        touch_fact(outcome, P7)
add_note(r, "The Table 5 drawing states 5 mol% FeCl3·6H2O, whereas the detailed Z-10a procedure reports 1.8 mol% (1.9 mg, 0.008 mmol); both source statements are retained.", P7)
replace_unresolved(
    r,
    ["Reaction scale", "Product connectivity"],
    [
        "The table and detailed procedure disagree on FeCl3·6H2O loading (5 mol% versus 1.8 mol%).",
        "The shared hydrolysis-product range cannot be assigned to an individual row.",
        "Product connectivity and Z geometry remain unverified.",
    ],
)


# Table 5 entry 1, Conditions D: detailed E-10a batch and cross-page fractions.
r = records[f"{DOC}:table5_entry1_conditions_d"]
common_detailed_setup(
    r, P7, substrate_mass=80.2, iron_mass=2.1, iron_amount=0.008,
    detailed_loading=1.9,
    product_name="ethyl 2-allyl-2,3-dimethyl-4-phenyl-3(E)-butenoate",
    product_smiles="CCOC(=O)C(C)(CC=C)C(C)=Cc1ccccc1",
)
add_unique(r["evidence_ids"], P8)
allyl = find_part(r, "allyl_reagent")
touch_fact(allyl["label"], P7)
touch_fact(allyl["smiles"], P7)
upsert_field(allyl["amounts"], "amount", {"number": 2, "unit": "mmol"}, P7)
upsert_field(allyl["amounts"], "equivalents", {"number": 5, "unit": "equiv"}, P7)
upsert_field(allyl["amounts"], "mass", {"number": 236.3, "unit": "mg"}, P7)
upsert_field(allyl["amounts"], "volume", {"number": 0.17, "unit": "mL"}, P7)
upsert_field(allyl["amounts"], "reported_density", "1.390 g mL−1", P7)
cui = find_part(r, "transition_catalyst")
touch_fact(cui["label"], P7)
upsert_field(cui["amounts"], "mass", {"number": 7.9, "unit": "mg"}, P7)
upsert_field(cui["amounts"], "amount", {"number": 0.04, "unit": "mmol"}, P7)
add_participant(r, "byproduct_z5e", "product", "Z-5e", P8,
                smiles="CCOC(=O)C(C)C(C)=Cc1ccccc1",
                name="ethyl 2,3-dimethyl-4-phenyl-3(Z)-butenoate")
add_participant(r, "byproduct_e5e", "product", "E-5e", P8,
                smiles="CCOC(=O)C(C)C(C)=Cc1ccccc1",
                name="ethyl 2,3-dimethyl-4-phenyl-3(E)-butenoate")
upsert_field(r["steps"][0]["conditions"], "pre_allylation_room_temperature_time",
             {"number": 2, "unit": "h"}, P7)
upsert_field(r["steps"][0]["conditions"], "allylation_addition",
             "After 2 h at room temperature, CuI was added and allyl bromide was added dropwise", P7)
upsert_field(r["steps"][0]["conditions"], "workup",
             "Quenched with saturated aqueous NH4Cl (1 mL) at 0 °C; warmed naturally to room temperature; extracted with diethyl ether (30 mL × 3); washed successively with 5% aqueous HCl, saturated aqueous NaHCO3, and brine; dried over anhydrous Na2SO4; filtered and evaporated.", P7 + P8)
upsert_field(r["steps"][0]["conditions"], "purification",
             "Silica-gel column chromatography; petroleum ether/CH2Cl2 = 8:1", P8)
upsert_field(r["outcomes"], "first_isolated_fraction_mass", {"number": 42.5, "unit": "mg"}, P8,
             ["product", "byproduct_z5e"])
upsert_field(r["outcomes"], "first_fraction_molar_ratio_by_NMR", "94/6 (E-10a/Z-5e)", P8,
             ["product", "byproduct_z5e"])
upsert_field(r["outcomes"], "first_fraction_E_10a_content_by_weight", {"number": 95, "unit": "%"}, P8,
             ["product"])
upsert_field(r["outcomes"], "second_isolated_fraction_mass", {"number": 0.0141, "unit": "g"}, P8,
             ["product", "byproduct_z5e", "byproduct_e5e"])
upsert_field(r["outcomes"], "second_fraction_molar_ratio_by_NMR", "86/6/8 (E-10a/Z-5e/E-5e)", P8,
             ["product", "byproduct_z5e", "byproduct_e5e"])
upsert_field(r["outcomes"], "second_fraction_E_10a_content_by_weight", {"number": 88, "unit": "%"}, P8,
             ["product"])
for outcome in r["outcomes"]:
    if outcome["name"] in {"isolated_yield", "yield_measurement_basis"}:
        touch_fact(outcome, P8)
add_note(r, "The Table 5 drawing states 5 mol% FeCl3·6H2O, whereas the detailed E-10a procedure reports 1.9 mol% (2.1 mg, 0.008 mmol); both source statements are retained.", P7)
add_note(r, "The reported 52% combined yield was obtained from two isolated mixed fractions with the stated NMR molar ratios and E-10a weight contents.", P8)
replace_unresolved(
    r,
    ["Reaction scale", "Product connectivity"],
    [
        "The table and detailed procedure disagree on FeCl3·6H2O loading (5 mol% versus 1.9 mol%).",
        "The shared hydrolysis-product range cannot be assigned to an individual row.",
        "The source reports mixed isolated fractions; pure isolated E-10a mass is not stated directly.",
        "Product and byproduct connectivity and E/Z geometry remain unverified.",
    ],
)


output_records = [records[rid] for rid in ids]
raw_path = RUN / "raw_model/records_pages_0007_0009.json"
raw_path.write_text(json.dumps(output_records, ensure_ascii=False, indent=2) + "\n")

coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 7,
            "state": "attempted",
            "regions": [
                {
                    "region": "upper-left continuation of the typical Z-5a procedure",
                    "finding": "The page completes the existing Table 2 entry 1 batch with quench, workup, chromatography, 86.2 mg product, and 88% isolated yield; no duplicate experiment was created.",
                    "evidence_ids": P7,
                },
                {
                    "region": "left column Z-9a and E-9a typical procedures",
                    "finding": "Exact substrate/catalyst/electrophile quantities, nitrogen atmosphere, additions, workups, purifications, product masses, and yields enrich the existing Table 4 entry 1 Conditions A/B records. Detailed FeCl3·6H2O loadings conflict with the 5 mol% table drawing and are retained separately.",
                    "evidence_ids": P7,
                },
                {
                    "region": "right column Z-10a procedure and beginning of E-10a procedure",
                    "finding": "Exact Pd/Cu, allyl-reagent, and first-stage quantities and operations enrich the existing Table 5 entry 1 Conditions C/D records; the E-10a workup continues on page 8.",
                    "evidence_ids": P7,
                },
            ],
            "record_ids": ids,
            "unresolved": [
                "The table drawings state 5 mol% FeCl3·6H2O, while the four detailed 3e batches report 2.4, 2.0, 1.8, and 1.9 mol%, respectively.",
                "Second-stage completion times for E-9a, Z-10a, and E-10a are monitored by TLC in the detailed procedures rather than given numerically.",
            ],
        },
        {
            "page": 8,
            "state": "attempted",
            "regions": [
                {
                    "region": "upper-left continuation and outcome of the E-10a procedure",
                    "finding": "The existing Table 5 entry 1 Conditions D record was enriched with the completed workup/purification, two mixed isolated fractions, their NMR molar ratios, E-10a weight contents, and the 52% combined yield.",
                    "evidence_ids": P8,
                },
                {
                    "region": "acknowledgements and references 1-9",
                    "finding": "No independent present-paper experiment is reported. The acknowledgement that selected table entries were reproduced does not state new conditions or outcomes and was not converted into duplicate records; cited prior work was not expanded.",
                    "evidence_ids": P8,
                },
            ],
            "record_ids": [f"{DOC}:table5_entry1_conditions_d"],
            "unresolved": [
                "The source gives two mixed fractions rather than a directly stated pure E-10a mass.",
                "The acknowledgement does not provide enough batch-specific information to represent reproductions as separate experiments.",
            ],
        },
        {
            "page": 9,
            "state": "attempted",
            "regions": [
                {
                    "region": "references 9-14 and closing publication matter",
                    "finding": "The page contains bibliography and a qualitative ionic-radius note only; it has no reaction arrow, table, procedure, experimental condition, yield, or independent present-paper experiment.",
                    "evidence_ids": [f"{DOC}:page9:image", f"{DOC}:page9:text"],
                },
            ],
            "record_ids": [],
            "unresolved": [
                "Bibliographic citations alone do not contain enough reaction-level information to reconstruct experiments, so cited primary papers were not expanded.",
            ],
        },
    ],
}
coverage_path = RUN / "coverage/pages_0007_0009.json"
coverage_path.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

tasks_path = RUN / "tasks.json"
tasks = json.loads(tasks_path.read_text())
requested = {f"{DOC}:page{page}:text" for page in range(7, 10)}
for task in tasks:
    if task["document_id"] == DOC and task["task_id"] in requested:
        task["state"] = "attempted"
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({
    "updated_records": len(output_records),
    "raw": str(raw_path),
    "coverage": str(coverage_path),
}, ensure_ascii=False))
