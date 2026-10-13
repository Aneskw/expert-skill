#!/usr/bin/env python3
"""Enrich existing reaction records from original PDF pages 7-9.

The covered pages continue experiments already identified on pages 1-6, so
this snapshot updates those record IDs instead of creating duplicates. All
facts remain machine-unreviewed after merge and all structures unverified.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path


DOC = "doc_065298449e790f13"
HERE = Path(__file__).resolve().parent
RUN = HERE.parent
DATASET = RUN / "dataset.json"
OUT = HERE / "pages_0007_0009_records.json"
COVERAGE = RUN / "coverage" / "pages_0007_0009.json"


def evid(page: int) -> list[str]:
    return [f"{DOC}:page{page}:text", f"{DOC}:page{page}:image"]


def fact(value, ev: list[str] | None = None) -> dict:
    return {
        "value": value,
        "evidence_ids": list(ev or []) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def field(name: str, value, ev: list[str] | None = None, targets=None) -> dict:
    item = {"name": name, "fact": fact(value, ev)}
    if targets:
        item["target_entity_ids"] = list(targets)
    return item


def amount(name: str, number: float, unit: str, ev: list[str]) -> dict:
    return field(name, {"number": number, "unit": unit}, ev)


def participant(entity_id: str, role: str, label: str, name: str, ev: list[str],
                smiles: str | None = None, amounts=None) -> dict:
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, ev),
        "name": fact(name, ev),
        "smiles": fact(smiles, ev) if smiles else fact(None),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": amounts or [],
    }


data = json.loads(DATASET.read_text())
by_id = {record["record_id"]: record for record in data["experiments"]}


def get(suffix: str) -> dict:
    return copy.deepcopy(by_id[f"{DOC}:{suffix}"])


def entity(record: dict, entity_id: str) -> dict:
    return next(item for item in record["participants"] if item["entity_id"] == entity_id)


def add_record_evidence(record: dict, ev: list[str]) -> None:
    record["evidence_ids"] = list(dict.fromkeys(record["evidence_ids"] + ev))


def add_fact_evidence(item: dict, ev: list[str]) -> None:
    item["fact"]["evidence_ids"] = list(dict.fromkeys(item["fact"]["evidence_ids"] + ev))


ev7 = evid(7)
ev8 = evid(8)
records: list[dict] = []


# Page 7 supplies row-specific preparations for Table 2 entries 18-21.
scope_exact = {
    18: ("substrate_1r", 40.8, 0.19, 76.9, 0.40, 0.4, 4.0, "product_2r", 64.5),
    19: ("substrate_1r", 42.9, 0.20, 78.3, 0.41, None, 4.0, "product_2r", 62.6),
    20: ("substrate_1s", 38.0, 0.20, 76.5, 0.40, 0.4, 4.0, "product_2s", 60.2),
    21: ("substrate_1s", 39.4, 0.20, 76.1, 0.40, None, 4.0, "product_2s", 54.6),
}

for entry_no, values in scope_exact.items():
    sub_id, sub_mass, sub_mmol, reagent_mass, reagent_mmol, water_ml, mecn_ml, product_id, product_mass = values
    rec = get(f"table2_entry_{entry_no}")
    add_record_evidence(rec, ev7)
    entity(rec, sub_id)["amounts"] = [
        amount("mass", sub_mass, "mg", ev7),
        amount("amount", sub_mmol, "mmol", ev7),
    ]
    phsecl = entity(rec, "phsecl")
    # Retain the table-level 2 equiv field and add the exact preparation values.
    phsecl["amounts"] = [x for x in phsecl["amounts"] if "equiv" in x["name"]] + [
        amount("mass", reagent_mass, "mg", ev7),
        amount("amount", reagent_mmol, "mmol", ev7),
    ]
    entity(rec, "mecn")["amounts"] = [amount("volume", mecn_ml, "mL", ev7)]
    if water_ml is not None:
        entity(rec, "water")["amounts"] = [amount("volume", water_ml, "mL", ev7)]
    entity(rec, product_id)["amounts"] = [amount("mass", product_mass, "mg", ev7)]
    for outcome in rec["outcomes"]:
        add_fact_evidence(outcome, ev7)
    rec["review"]["unresolved"] = [
        "Atmosphere is not reported.",
        "Workup and purification are not reported for this entry.",
        "Candidate structures are machine interpretations and require chemical review.",
        "No supporting-information file was explicitly associated.",
    ]
    records.append(rec)


# Page 7 section 4.1.19 gives exact amounts for Scheme 1's first stage.
# The printed sentence calls its starting material 3t; Scheme 1 and the mass/
# amount relation identify 1t. Preserve the discrepancy explicitly.
rec = get("scheme1_1t_to_3t")
add_record_evidence(rec, ev7)
entity(rec, "substrate_1t")["amounts"] = [
    amount("reported_starting_material_mass", 101.1, "mg", ev7),
    amount("reported_starting_material_amount", 1.03, "mmol", ev7),
]
phsecl = entity(rec, "phsecl")
phsecl["amounts"] = [x for x in phsecl["amounts"] if "equiv" in x["name"]] + [
    amount("mass", 384.1, "mg", ev7),
    amount("amount", 2.01, "mmol", ev7),
]
entity(rec, "mecn")["amounts"] = [amount("volume", 20.0, "mL", ev7)]
entity(rec, "water")["amounts"] = [amount("volume", 2.0, "mL", ev7)]
entity(rec, "product_3t")["amounts"] = [amount("mass", 242.0, "mg", ev7)]
for outcome in rec["outcomes"]:
    add_fact_evidence(outcome, ev7)
rec["notes"].append(fact(
    "Section 4.1.19 literally names the 101.1 mg (1.03 mmol) starting material as 3t, "
    "which conflicts with Scheme 1 and with the same sentence reporting 3t as product; "
    "the existing 1t assignment therefore remains a machine interpretation requiring review.",
    ev7,
))
rec["review"]["unresolved"] = [
    "Reaction time, atmosphere, workup, and purification are not reported.",
    "Section 4.1.19 contains an internal starting-material label conflict (printed 3t versus Scheme 1's 1t).",
    "The candidate SMILES preserves connectivity but does not encode the reported Z geometry.",
    "No supporting-information file was explicitly associated.",
]
records.append(rec)


# Page 7 section 4.1.20 fully describes the separate DIBAL-H reduction/workup.
rec = get("scheme1_3t_to_4t")
add_record_evidence(rec, ev7)
entity(rec, "substrate_3t")["amounts"] = [
    amount("mass", 103.6, "mg", ev7),
    amount("amount", 0.36, "mmol", ev7),
]
entity(rec, "dibal_h")["amounts"] = [
    amount("solution_volume", 2.0, "mL", ev7),
    amount("solution_concentration", 1.0, "M", ev7),
]
entity(rec, "product_4t")["amounts"] = [amount("mass", 78.9, "mg", ev7)]
rec["participants"].extend([
    participant("toluene", "solvent", "toluene", "toluene", ev7, "Cc1ccccc1",
                [amount("substrate_solution_volume", 2.0, "mL", ev7)]),
    participant("methanol_quench", "unspecified_agent", "MeOH", "methanol quench", ev7, "CO",
                [amount("volume", 2.0, "mL", ev7)]),
    participant("water_quench", "unspecified_agent", "water", "water quench", ev7, "O",
                [amount("volume", 5.0, "mL", ev7)]),
    participant("diethyl_ether", "solvent", "diethyl ether", "diethyl ether extraction solvent", ev7,
                "CCOCC", [amount("extraction_volume_each", 25.0, "mL", ev7),
                           field("extraction_repetitions", 3, ev7)]),
    participant("sodium_sulfate", "unspecified_agent", "anhydrous Na2SO4", "anhydrous sodium sulfate", ev7,
                "[Na+].[Na+].[O-]S(=O)(=O)[O-]"),
])
rec["steps"] = [
    {
        "step_id": "reduction",
        "participant_ids": ["substrate_3t", "dibal_h", "toluene", "product_4t"],
        "conditions": [
            field("temperature", {"number": -78, "unit": "°C"}, ev7),
            field("time", {"number": 3, "unit": "h"}, ev7),
            field("solvent", "toluene", ev7),
            field("operation", "3t solution was added to DIBAL-H at -78 °C, then stirred at that temperature.", ev7),
            field("atmosphere", None),
        ],
    },
    {
        "step_id": "workup_and_purification",
        "participant_ids": ["methanol_quench", "water_quench", "diethyl_ether", "sodium_sulfate", "product_4t"],
        "conditions": [
            field("workup", "quenched with MeOH and water; extracted with diethyl ether three times; dried over anhydrous Na2SO4; evaporated", ev7),
            field("purification", "silica-gel column chromatography; petroleum ether/ethyl acetate 5:1", ev7),
        ],
    },
]
rec["outcomes"] = [
    field("isolated_yield", {"number": 84, "unit": "%"}, ev7, ["product_4t"]),
    field("yield_measurement_basis", "isolated after column chromatography", ev7, ["product_4t"]),
]
rec["review"]["unresolved"] = [
    "Atmosphere is not reported.",
    "The candidate SMILES does not encode the reported Z geometry.",
    "The source does not explicitly state a molar equivalent for DIBAL-H; only solution volume and concentration are retained.",
    "No supporting-information file was explicitly associated.",
]
records.append(rec)


# Page 8 supplies exact scale and product masses for the Scheme 3 experiment.
rec = get("scheme3_mechanistic_probe")
add_record_evidence(rec, ev8)
entity(rec, "substrate_1u")["amounts"] = [
    amount("mass", 59.0, "mg", ev8),
    amount("amount", 0.20, "mmol", ev8),
]
phsecl = entity(rec, "phsecl")
phsecl["amounts"] = [x for x in phsecl["amounts"] if "equiv" in x["name"]] + [
    amount("mass", 77.0, "mg", ev8),
    amount("amount", 0.40, "mmol", ev8),
]
entity(rec, "mecn")["amounts"] = [amount("volume", 4.0, "mL", ev8)]
entity(rec, "water")["amounts"] = [amount("volume", 0.4, "mL", ev8)]
entity(rec, "product_2g")["amounts"] = [amount("mass", 59.0, "mg", ev8)]
entity(rec, "product_7u")["amounts"] = [amount("mass", 22.0, "mg", ev8)]
for outcome in rec["outcomes"]:
    add_fact_evidence(outcome, ev8)
rec["review"]["unresolved"] = [
    "Reaction time, atmosphere, workup, and purification are not reported.",
    "Candidate structures are machine interpretations and require chemical review.",
    "No supporting-information file was explicitly associated.",
]
records.append(rec)


OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")

coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 7,
            "state": "attempted",
            "regions": [
                {
                    "region": "左栏顶部2q分析数据续文",
                    "finding": "确认仅为化合物2q表征的跨页续文，对应既有Table 2 entry 17；未重复建立实验记录。",
                    "evidence_ids": [f"{DOC}:page7:image", f"{DOC}:page7:text"],
                },
                {
                    "region": "左栏4.1.17与4.1.18制备段落",
                    "finding": "为Table 2 entries 18-21补入1r/1s、PhSeCl、H2O/MeCN及2r/2s的逐实验质量、物质的量、体积和产物质量；有水与无水条件保持为四条独立记录。",
                    "evidence_ids": [f"{DOC}:page7:image", f"{DOC}:page7:text"],
                },
                {
                    "region": "右栏4.1.19 3t制备段落",
                    "finding": "补入Scheme 1第一阶段的规模、PhSeCl与溶剂用量及3t质量；原文把起始物印为3t，与Scheme 1和同句产物3t冲突，未静默消解而列为待核查。",
                    "evidence_ids": [f"{DOC}:page7:image", f"{DOC}:page7:text", f"{DOC}:page2:image", f"{DOC}:page3:image"],
                },
                {
                    "region": "右栏4.1.20 DIBAL-H还原与后处理段落",
                    "finding": "为3t至4t阶段补入-78 °C、3 h、DIBAL-H溶液体积/浓度、甲醇和水淬灭、醚萃取、Na2SO4干燥、柱层析及84%分离收率。",
                    "evidence_ids": [f"{DOC}:page7:image", f"{DOC}:page7:text"],
                },
            ],
            "record_ids": [
                f"{DOC}:table2_entry_17", f"{DOC}:table2_entry_18", f"{DOC}:table2_entry_19",
                f"{DOC}:table2_entry_20", f"{DOC}:table2_entry_21",
                f"{DOC}:scheme1_1t_to_3t", f"{DOC}:scheme1_3t_to_4t",
            ],
            "unresolved": [
                "4.1.19原文的起始物标签存在内部冲突：印为3t，但Scheme 1为1t生成3t。",
                "2r/2s及3t制备段落未报告逐项后处理、纯化或气氛；3t制备还未报告反应时间。",
                "候选结构和Z构型编码仍需化学复核。",
            ],
        },
        {
            "page": 8,
            "state": "attempted",
            "regions": [
                {
                    "region": "左栏顶部4t分析数据续文",
                    "finding": "确认是第7页4t记录的连续表征信息，不是新增反应。",
                    "evidence_ids": [f"{DOC}:page8:image", f"{DOC}:page8:text"],
                },
                {
                    "region": "左栏4.2 Mechanistic study反应式与制备段落",
                    "finding": "将1u机理验证实验的59 mg/0.20 mmol底物、77 mg/0.40 mmol PhSeCl、0.4 mL H2O、4 mL MeCN，以及2g 59 mg/89%和7u 22 mg/80%合并进既有Scheme 3记录。",
                    "evidence_ids": [f"{DOC}:page8:image", f"{DOC}:page8:text", f"{DOC}:page3:image"],
                },
                {
                    "region": "左栏Acknowledgements及其后、右栏References and notes",
                    "finding": "致谢与参考文献区不构成本篇新的逐实验记录；未从被引论文反向补齐缺失条件。",
                    "evidence_ids": [f"{DOC}:page8:image", f"{DOC}:page8:text"],
                },
            ],
            "record_ids": [f"{DOC}:scheme1_3t_to_4t", f"{DOC}:scheme3_mechanistic_probe"],
            "unresolved": [
                "1u机理验证实验未报告反应时间、气氛、后处理或纯化。",
                "本页没有明确提供或关联SI。",
            ],
        },
        {
            "page": 9,
            "state": "attempted",
            "regions": [
                {
                    "region": "全页References and notes 5-12",
                    "finding": "整页为参考文献及关于2,3-allenoic acids制备的引文说明；无本篇新增反应箭头、表格、脚注实验或实验步骤，故不新增记录，也不以引文补齐主文缺失信息。",
                    "evidence_ids": [f"{DOC}:page9:image", f"{DOC}:page9:text"],
                },
            ],
            "record_ids": [],
            "unresolved": [
                "被引文献的具体实验内容不在本次提供来源中，未作二手推断。",
                "本页没有明确提供或关联SI。",
            ],
        },
    ],
}
COVERAGE.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

# Mark only this session's bounded page tasks attempted.
tasks_path = RUN / "tasks.json"
tasks = json.loads(tasks_path.read_text())
for task in tasks:
    if task["document_id"] == DOC and task["evidence_id"] in {
        f"{DOC}:page7:text", f"{DOC}:page8:text", f"{DOC}:page9:text"
    }:
        task["state"] = "attempted"
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({
    "updated_records": len(records),
    "record_ids": [r["record_id"] for r in records],
    "raw_output": str(OUT),
    "coverage": str(COVERAGE),
}, ensure_ascii=False))
