#!/usr/bin/env python3
"""Augment existing records with source details from PDF pages 13--15."""

import copy
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "runs/current"
DOC = "doc_50d01341363d3c76"


def ev(page):
    return [f"{DOC}:page{page}:text", f"{DOC}:page{page}:image"]


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


def find_participant(record, label):
    return next(p for p in record["participants"] if p["label"]["value"] == label)


def set_amount(participant_obj, name, value, evidence):
    new_field = field(name, value, evidence)
    for index, old in enumerate(participant_obj["amounts"]):
        if old["name"] == name:
            participant_obj["amounts"][index] = new_field
            return
    participant_obj["amounts"].append(new_field)


def set_condition(record, name, value, evidence):
    conditions = record["steps"][0]["conditions"]
    new_field = field(name, value, evidence)
    for index, old in enumerate(conditions):
        if old["name"] == name:
            conditions[index] = new_field
            return
    conditions.append(new_field)


def participant(entity_id, role, label, name, evidence, smiles=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence),
        "smiles": fact(smiles, evidence) if smiles else fact(None, []),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": [],
    }


dataset = json.loads((OUT / "dataset.json").read_text())
existing = {record["source_reaction_id"]: record for record in dataset["experiments"]}
records = []


# Page 13 begins with characterization continuing from the page-12 preparation
# of 9ba. Preserve this as supporting evidence on the existing experiment.
record = copy.deepcopy(existing["table7_entry8_9ba"])
record["evidence_ids"] = unique(record["evidence_ids"] + ev(13))
record["notes"].append(fact(
    "PDF page 13 continues the analytical characterization of the isolated (E)-9ba/10ba material prepared on page 12.",
    ev(13),
))
records.append(record)


# Detailed Conditions-B procedures for the final three Table 7 entries.
table7_details = {
    "table7_entry9_9cd": {
        "allene": "8c", "allene_mass": 66,
        "boronic": "3d", "boronic_mass": 76, "boronic_mmol": 0.50,
        "pd_mass": 29, "pd_mmol": 0.025,
        "product": "(E)-9cd", "product_name": "(E)-2-(4-methoxyphenyl)nonadec-2-ene",
        "product_mass": 32, "isolated_ratio": "95:5",
        "purification": "flash chromatography on silica gel; pure (E)-9cd obtained by recrystallization from Et2O",
    },
    "table7_entry10_9dd": {
        "allene": "8d", "allene_mass": 31,
        "boronic": "3d", "boronic_mass": 76, "boronic_mmol": 0.50,
        "pd_mass": 29, "pd_mmol": 0.025,
        "product": "(E)-9dd", "product_name": "(E)-1-cyclohexyl-2-(4-methoxyphenyl)prop-1-ene",
        "product_mass": 25, "isolated_ratio": "92:8",
        "purification": "flash chromatography on silica gel",
    },
    "table7_entry11_9ed": {
        "allene": "8e", "allene_mass": 33,
        "boronic": "3d", "boronic_mass": 76, "boronic_mmol": 0.50,
        "pd_mass": 29, "pd_mmol": 0.025,
        "product": "(E)-9ed", "product_name": "(E)-3-(4-methoxyphenyl)-1-phenylbut-2-ene",
        "product_mass": 45, "isolated_ratio": None,
        "purification": "flash chromatography on silica gel; paragraph states pure (E)-9ed was isolated",
        "pure_main": True,
    },
}

for suffix, detail in table7_details.items():
    evidence = ev(13)
    record = copy.deepcopy(existing[suffix])
    record["evidence_ids"] = unique(record["evidence_ids"] + evidence)
    allene = find_participant(record, detail["allene"])
    set_amount(allene, "mass", {"number": detail["allene_mass"], "unit": "mg"}, evidence)
    set_amount(allene, "amount", {"number": 0.25, "unit": "mmol"}, evidence)
    boronic = find_participant(record, detail["boronic"])
    set_amount(boronic, "mass", {"number": detail["boronic_mass"], "unit": "mg"}, evidence)
    set_amount(boronic, "amount", {"number": detail["boronic_mmol"], "unit": "mmol"}, evidence)
    pd = find_participant(record, "Pd(PPh3)4")
    set_amount(pd, "mass", {"number": detail["pd_mass"], "unit": "mg"}, evidence)
    set_amount(pd, "amount", {"number": detail["pd_mmol"], "unit": "mmol"}, evidence)
    acoh = find_participant(record, "AcOH")
    set_amount(acoh, "volume", {"number": 14, "unit": "uL"}, evidence)
    set_amount(acoh, "amount", {"number": 0.24, "unit": "mmol"}, evidence)
    dioxane = find_participant(record, "dioxane")
    set_amount(dioxane, "volume", {"number": 3, "unit": "mL"}, evidence)
    product = find_participant(record, detail["product"])
    product["name"] = fact(detail["product_name"], evidence)
    set_condition(record, "workup", "solvent evaporated; crude mixture analyzed by 1H NMR", evidence)
    set_condition(record, "purification", detail["purification"], evidence)
    mass_targets = [product["entity_id"]]
    if not detail.get("pure_main"):
        mass_targets.append(next(p["entity_id"] for p in record["participants"] if p["label"]["value"].startswith("10")))
    record["outcomes"].append(field(
        "isolated_product_mass",
        {"number": detail["product_mass"], "unit": "mg"},
        evidence,
        mass_targets,
    ))
    if detail["isolated_ratio"]:
        minor = next(p for p in record["participants"] if p["label"]["value"].startswith("10"))
        record["outcomes"].append(field(
            "isolated_mixture_ratio_E_9_to_10",
            detail["isolated_ratio"],
            evidence,
            [product["entity_id"], minor["entity_id"]],
        ))
    if detail.get("pure_main"):
        record["outcomes"].append(field(
            "detailed_paragraph_isolated_yield_E_9",
            {"number": 76, "unit": "%"},
            evidence,
            [product["entity_id"]],
        ))
    record["review"]["unresolved"] = [
        "Reflux is qualitative because no numerical temperature is reported.",
        "Product/regioisomer structures and stereochemical SMILES remain unverified.",
    ]
    if detail.get("pure_main"):
        record["review"]["unresolved"].append(
            "Table 7 defines entry 11 as a combined 9ed+10ed yield under a general inseparability footnote, whereas the page-13 paragraph says pure (E)-9ed was isolated; both claims are retained."
        )
    records.append(record)


# Exact compound procedures corresponding to the eight existing Table 8 rows.
table8_details = {
    "table8_entry1_12aa": dict(pages=[13], allene="11a", allene_mass=29, boronic="3a", boronic_mass=61, boronic_mmol=0.50, pd_mass=29, pd_mmol=0.025, product="(E)-12aa", product_mass=20, product_name="(E)-1,2-diphenylprop-1-ene"),
    "table8_entry2_12ab": dict(pages=[13], allene="11a", allene_mass=29, boronic="3b", boronic_mass=67, boronic_mmol=0.49, pd_mass=30, pd_mmol=0.026, product="(E)-12ab", product_mass=38, product_name="(E)-1-phenyl-2-(4-tolyl)prop-1-ene"),
    "table8_entry3_12ad": dict(pages=[13], allene="11a", allene_mass=29, boronic="3d", boronic_mass=76, boronic_mmol=0.50, pd_mass=29, pd_mmol=0.025, product="(E)-12ad", product_mass=44, product_name="(E)-2-(4-methoxyphenyl)-1-phenylprop-1-ene"),
    "table8_entry4_12ag": dict(pages=[13, 14], allene="11a", allene_mass=29, boronic="3g", boronic_mass=82, boronic_mmol=0.50, pd_mass=29, pd_mmol=0.025, product="(E)-12ag", product_mass=26, product_name="(E)-2-(4-acetylphenyl)-1-phenylprop-1-ene"),
    "table8_entry5_12ah": dict(pages=[14], allene="11a", allene_mass=29, boronic="3h", boronic_mass=85, boronic_mmol=0.49, pd_mass=29, pd_mmol=0.025, product="(E)-12ah", product_mass=53, product_name="(E)-2-(1-naphthyl)-1-phenylprop-1-ene"),
    "table8_entry6_12bd": dict(pages=[14], allene="11b", allene_mass=37, boronic="3d", boronic_mass=75, boronic_mmol=0.49, pd_mass=30, pd_mmol=0.026, product="(E)-12bd", product_mass=38, product_name="(E)-1,2-bis(4-methoxyphenyl)prop-1-ene"),
    "table8_entry7_12cd": dict(pages=[14], allene="11c", allene_mass=43, boronic="3d", boronic_mass=77, boronic_mmol=0.51, pd_mass=29, pd_mmol=0.025, product="(E)-12cd", product_mass=46, product_name="(E)-1-(4-tert-butylphenyl)-2-(4-methoxyphenyl)prop-1-ene"),
    "table8_entry8_12dd": dict(pages=[14], allene="11d", allene_mass=40, boronic="3d", boronic_mass=75, boronic_mmol=0.49, pd_mass=30, pd_mmol=0.026, product="(E)-12dd", product_mass=41, product_name="(E)-1-(4-acetylphenyl)-2-(4-methoxyphenyl)prop-1-ene"),
}

for suffix, detail in table8_details.items():
    evidence = unique(sum((ev(page) for page in detail["pages"]), []))
    record = copy.deepcopy(existing[suffix])
    record["evidence_ids"] = unique(record["evidence_ids"] + evidence)
    allene = find_participant(record, detail["allene"])
    set_amount(allene, "mass", {"number": detail["allene_mass"], "unit": "mg"}, evidence)
    set_amount(allene, "amount", {"number": 0.25, "unit": "mmol"}, evidence)
    boronic = find_participant(record, detail["boronic"])
    set_amount(boronic, "mass", {"number": detail["boronic_mass"], "unit": "mg"}, evidence)
    set_amount(boronic, "amount", {"number": detail["boronic_mmol"], "unit": "mmol"}, evidence)
    pd = find_participant(record, "Pd(PPh3)4")
    set_amount(pd, "mass", {"number": detail["pd_mass"], "unit": "mg"}, evidence)
    set_amount(pd, "amount", {"number": detail["pd_mmol"], "unit": "mmol"}, evidence)
    acoh = find_participant(record, "AcOH")
    set_amount(acoh, "volume", {"number": 14, "unit": "uL"}, evidence)
    set_amount(acoh, "amount", {"number": 0.24, "unit": "mmol"}, evidence)
    dioxane = find_participant(record, "dioxane")
    set_amount(dioxane, "volume", {"number": 3, "unit": "mL"}, evidence)
    product = find_participant(record, detail["product"])
    product["name"] = fact(detail["product_name"], evidence)
    set_condition(record, "workup", "solvent evaporated; crude mixture analyzed by 1H NMR", evidence)
    set_condition(record, "purification", "flash chromatography on silica gel", evidence)
    record["outcomes"].append(field(
        "isolated_product_mass",
        {"number": detail["product_mass"], "unit": "mg"},
        evidence,
        [product["entity_id"]],
    ))
    record["review"]["unresolved"] = [
        "Reflux is qualitative because no numerical temperature is reported.",
        "Product/regioisomer connectivity and stereochemical SMILES remain unverified.",
    ]
    if suffix == "table8_entry5_12ah":
        record["notes"].append(fact(
            "The printed HRMS line for (E)-12ah gives C19H16 [M+] calculated as 224.1252 but found as 244.1255; the internal numerical inconsistency is retained as a source issue.",
            ev(14),
        ))
        record["review"]["unresolved"].append(
            "The page-14 (E)-12ah HRMS calculated mass (224.1252) conflicts with the printed formula and found mass (244.1255)."
        )
    records.append(record)


# Page 14 gives the complete procedure for the Scheme 3 oxidation.
e14 = ev(14)
record = copy.deepcopy(existing["scheme3_oxidation_6ab_to_4ab"])
record["evidence_ids"] = unique(record["evidence_ids"] + e14)
reactant = find_participant(record, "(E)-6ab")
set_amount(reactant, "mass", {"number": 101, "unit": "mg"}, e14)
set_amount(reactant, "amount", {"number": 0.4, "unit": "mmol"}, e14)
h2o2 = find_participant(record, "hydrogen peroxide")
h2o2["label"] = fact("30% H2O2", e14)
h2o2["name"] = fact("30% hydrogen peroxide", e14)
set_amount(h2o2, "concentration", {"number": 30, "unit": "%"}, e14)
set_amount(h2o2, "volume", {"number": 5, "unit": "mL"}, e14)
acoh = find_participant(record, "AcOH")
set_amount(acoh, "volume", {"number": 5, "unit": "mL"}, e14)
extras = [
    participant("scheme3_water", "reagent", "H2O", "water", e14, "O"),
    participant("scheme3_chcl3", "solvent", "CHCl3", "chloroform", e14, "ClC(Cl)Cl"),
    participant("scheme3_nahco3", "reagent", "sat. aq. NaHCO3", "saturated aqueous sodium bicarbonate", e14),
    participant("scheme3_mgso4", "reagent", "MgSO4", "magnesium sulfate", e14),
]
set_amount(extras[0], "volume", {"number": 15, "unit": "mL"}, e14)
set_amount(extras[1], "extraction_volume_per_portion", {"number": 25, "unit": "mL"}, e14)
record["participants"].extend(extras)
record["steps"][0]["participant_ids"] = unique(record["steps"][0]["participant_ids"] + [p["entity_id"] for p in extras])
set_condition(record, "monitoring", "TLC (PE–Et2O 1:1) to complete conversion", e14)
set_condition(record, "workup", "quenched with H2O (15 mL); extracted with CHCl3 (6 × 25 mL); organic layer neutralized with saturated aqueous NaHCO3 and dried over MgSO4; solvent evaporated", e14)
set_condition(record, "purification", "flash chromatography on silica gel with PE–Et2O 3:1", e14)
product = find_participant(record, "(E)-4ab")
record["outcomes"].append(field("isolated_product_mass", {"number": 57, "unit": "mg"}, e14, [product["entity_id"]]))
for outcome in record["outcomes"]:
    if outcome["name"] == "yield_measurement_basis":
        outcome["fact"] = fact("isolated after flash chromatography", e14)
record["review"]["unresolved"] = [
    "Atmosphere is not reported.",
    "Reactant/product connectivity and alkene stereochemical SMILES remain unverified.",
]
records.append(record)


# Page 15 contains reference 13's crystallographic data, not a new reaction.
record = copy.deepcopy(existing["table4_entry12_4ca"])
record["evidence_ids"] = unique(record["evidence_ids"] + ev(15))
record["notes"].append(fact(
    "Reference 13 reports crystal-structure data for (E)-4ca and deposition at CCDC under number 613372; this is structural context, not a separate reaction.",
    ev(15),
))
record["review"]["unresolved"] = unique(record["review"]["unresolved"] + [
    "The deposited CCDC crystallographic data are mentioned but were not supplied as an associated source document."
])
records.append(record)


def rid(suffix):
    return f"{DOC}:{suffix}"


coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 13,
            "state": "attempted",
            "regions": [
                {
                    "region": "upper-left continuation of the (E)-9ba analytical characterization",
                    "finding": "Continuation of characterization for the existing Table 7 entry 8 experiment; no additional reaction or condition was created.",
                    "evidence_ids": ev(13),
                },
                {
                    "region": "left column compound procedures for (E)-9cd, (E)-9dd, and (E)-9ed",
                    "finding": "Three existing Table 7 scope records were augmented with exact participant quantities, dioxane volume, evaporation/NMR handling, chromatography, isolated masses, and isolated-mixture ratios where printed.",
                    "evidence_ids": ev(13),
                },
                {
                    "region": "right column compound procedures for (E)-12aa, (E)-12ab, (E)-12ad, and the beginning of (E)-12ag",
                    "finding": "Three complete and one cross-page existing Table 8 scope procedures were linked to their table records; no duplicate experiments were created.",
                    "evidence_ids": ev(13),
                },
            ],
            "record_ids": [rid(x) for x in [
                "table7_entry8_9ba", "table7_entry9_9cd", "table7_entry10_9dd", "table7_entry11_9ed",
                "table8_entry1_12aa", "table8_entry2_12ab", "table8_entry3_12ad", "table8_entry4_12ag",
            ]],
            "unresolved": [
                "Reflux remains qualitative because no numerical temperature is reported.",
                "Table 7 entry 11's general combined-yield/inseparability wording conflicts with the detailed statement that pure (E)-9ed was isolated.",
                "Complex product/regioisomer connectivity and stereochemistry remain unverified.",
            ],
        },
        {
            "page": 14,
            "state": "attempted",
            "regions": [
                {
                    "region": "upper-left continuation of the (E)-12ag procedure and characterization",
                    "finding": "The cross-page Table 8 entry 4 preparation was completed and merged into its existing record.",
                    "evidence_ids": ev(14),
                },
                {
                    "region": "left and upper-right compound procedures for (E)-12ah, (E)-12bd, (E)-12cd, and (E)-12dd",
                    "finding": "Four existing Table 8 scope records were augmented with exact quantities, handling, purification, product masses, yields, and selectivity evidence.",
                    "evidence_ids": ev(14),
                },
                {
                    "region": "middle-right Synthesis of Sulfone (E)-4ab from Sulfoxide (E)-6ab",
                    "finding": "The detailed oxidation procedure was merged into the existing Scheme 3 experiment with reactant/oxidant/solvent quantities, TLC monitoring, workup, chromatography, product mass, and 52% isolated yield basis.",
                    "evidence_ids": ev(14),
                },
                {
                    "region": "lower page acknowledgment and references 1–5",
                    "finding": "Acknowledgment and cited prior publications; no present-paper reaction arrow, table, or new experiment.",
                    "evidence_ids": ev(14),
                },
            ],
            "record_ids": [rid(x) for x in [
                "table8_entry4_12ag", "table8_entry5_12ah", "table8_entry6_12bd",
                "table8_entry7_12cd", "table8_entry8_12dd", "scheme3_oxidation_6ab_to_4ab",
            ]],
            "unresolved": [
                "The oxidation atmosphere is not reported.",
                "Reflux remains qualitative for Table 8 because no numerical temperature is reported.",
                "The printed (E)-12ah HRMS calculated mass conflicts with its formula and found mass.",
                "Complex product/regioisomer connectivity and stereochemistry remain unverified.",
            ],
        },
        {
            "page": 15,
            "state": "attempted",
            "regions": [
                {
                    "region": "two-column references 6–21 and reference-13 crystallographic note",
                    "finding": "No reaction arrow, table, experimental procedure, or new present-paper experiment. Reference 13 supplies crystal data and CCDC 613372 for existing product (E)-4ca only.",
                    "evidence_ids": ev(15),
                }
            ],
            "record_ids": [rid("table4_entry12_4ca")],
            "unresolved": [
                "Cited publications were not supplied as associated source documents and were not mined for experiments.",
                "The deposited CCDC crystallographic data were not supplied; no external SI or crystal file was associated.",
            ],
        },
    ],
}


raw_dir = OUT / "raw_model"
raw_dir.mkdir(parents=True, exist_ok=True)
(raw_dir / "records_pages_0013_0015.json").write_text(json.dumps(records, ensure_ascii=False, indent=2))
coverage_dir = OUT / "coverage"
coverage_dir.mkdir(parents=True, exist_ok=True)
(coverage_dir / "pages_0013_0015.json").write_text(json.dumps(coverage, ensure_ascii=False, indent=2))

tasks_path = OUT / "tasks.json"
tasks = json.loads(tasks_path.read_text())
for task in tasks:
    if task.get("document_id") == DOC and task.get("evidence_id", "").endswith(":text"):
        page = int(task["evidence_id"].split(":page", 1)[1].split(":", 1)[0])
        if 13 <= page <= 15:
            task["state"] = "attempted"
            task["reason"] = "Original page image and text inspected; page-level extraction attempted for this session."
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2))

print(json.dumps({
    "submitted_records": len(records),
    "new_records": 0,
    "replacements": len(records),
    "coverage_pages": [page["page"] for page in coverage["pages"]],
}, ensure_ascii=False, indent=2))
