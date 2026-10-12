#!/usr/bin/env python3
"""Build evidence-linked machine records for PDF pages 1--3.

This is a source-transcription artifact.  The merge tool remains responsible for
normalization, validation, and quarantine as needs_review.
"""
from __future__ import annotations

import json
from pathlib import Path


DOC = "doc_a66d7dd63559443c"
BASE = Path(__file__).resolve().parents[1]
OUT = Path(__file__).with_name("records_pages_0001_0003.json")
COVERAGE = BASE / "coverage" / "pages_0001_0003.json"

P1 = [f"{DOC}:page1:text", f"{DOC}:page1:image"]
P2 = [f"{DOC}:page2:text", f"{DOC}:page2:image"]
P3 = [f"{DOC}:page3:text", f"{DOC}:page3:image"]


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


def participant(entity_id, role, label, name, smiles, evidence, amounts=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence),
        "smiles": fact(smiles, evidence),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": amounts or [],
    }


def record(rid, source_id, kind, evidence, participants, steps, outcomes,
           notes=None, unresolved=None):
    return {
        "record_id": f"{DOC}:{rid}",
        "document_id": DOC,
        "source_reaction_id": source_id,
        "record_kind": kind,
        "status": "needs_review",
        "completeness": "partial",
        "evidence_ids": list(evidence),
        "participants": participants,
        "steps": steps,
        "outcomes": outcomes,
        "notes": [fact(v, evidence) for v in (notes or [])],
        "review": {
            "method": "model",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved or [],
        },
    }


def qty(number, unit, **extra):
    return {"number": number, "unit": unit, **extra}


def qrange(minimum, maximum, unit, raw_text):
    return {"minimum": minimum, "maximum": maximum, "unit": unit, "raw_text": raw_text}


SUB_1A = "C=C=C(CCCC)C(O)c1ccccc1"
PROD_2A = "C=C(Br)C(CCCC)(c1ccccc1)C=O"
PROD_3A = "C=C(Br)C1(CCCC)OC1c1ccccc1"
BR2 = "BrBr"


records = []

# Table 1: every optimization row is independent.  Entry 9 is the same experiment
# repeated as Table 2 entry 1, so it carries both pages and is not duplicated.
table1 = [
    (1, "THF", 33, 19, None),
    (2, "toluene", 33, 19, None),
    (3, "benzene", 25, 1, None),
    (4, "CH3CN", 25, 24, 35),
    (5, "CH2Cl2", 32, 2, 60),
    (6, "CCl4", 32, 2, 63),
    (7, "CH3CN/H2O = 4:1", 32, 1, 68),
    (8, "CH3CN/H2O = 8:1", 32, 2, 65),
    (9, "CH3CN/H2O = 15:1", 25, 0.5, 77),
    (10, "CH3CN/H2O = 60:1", 30, 1, 60),
    (11, "CH3CN/H2O = 15:1", -30, 1, 50),
]
solvent_smiles = {
    "THF": "C1CCOC1", "toluene": "Cc1ccccc1", "benzene": "c1ccccc1",
    "CH3CN": "CC#N", "CH2Cl2": "ClCCl", "CCl4": "ClC(Cl)(Cl)Cl",
}
for entry, solvent, temp, hours, yield_value in table1:
    shared = entry == 9
    evidence = P1 + P2 if shared else P1
    rid = "table1_entry_09_table2_entry_01" if shared else f"table1_entry_{entry:02d}"
    source_id = "Table 1 entry 9 / Table 2 entry 1" if shared else f"Table 1 entry {entry}"
    sub_amounts = [field("reaction_scale", qrange(0.3, 0.5, "mmol", "0.3–0.5 mmol"), evidence)] if shared else []
    participants = [
        participant("substrate_1a", "reactant", "1a", "1-phenyl-2-(n-butyl)-2,3-butadien-1-ol", SUB_1A, evidence, sub_amounts),
        participant("bromine", "reagent", "Br2", "bromine", BR2, evidence,
                    [field("equivalents", qty(2, "equiv"), evidence)]),
        participant("product_2a", "product", "2a", "beta-bromo-beta,gamma-unsaturated enal 2a", PROD_2A, evidence),
    ]
    solvent_ids = []
    if solvent.startswith("CH3CN/H2O"):
        mecn_amounts = [field("volume", qty(4, "mL"), evidence)] if shared else []
        water_amounts = [field("volume", qty(0.27, "mL"), evidence)] if shared else []
        participants += [
            participant("solvent_mecn", "solvent", "CH3CN", "acetonitrile", "CC#N", evidence, mecn_amounts),
            participant("solvent_water", "solvent", "H2O", "water", "O", evidence, water_amounts),
        ]
        solvent_ids = ["solvent_mecn", "solvent_water"]
    else:
        sid = "solvent_" + solvent.lower().replace("2", "2").replace("3", "3").replace("4", "4")
        participants.append(participant(sid, "solvent", solvent, solvent, solvent_smiles[solvent], evidence))
        solvent_ids = [sid]
    if shared:
        participants.append(participant("product_3a", "product", "3a", "vinylic epoxide 3a", PROD_3A, evidence))
    conditions = [
        field("solvent", solvent, evidence),
        field("temperature", qty(temp, "°C"), evidence),
        field("time", qty(hours, "h"), evidence),
    ]
    outcomes = [
        field("isolated_yield", qty(yield_value, "%") if yield_value is not None else None,
              evidence, ["product_2a"]),
        field("yield_measurement_basis", "isolated yield", evidence, ["product_2a"]),
    ]
    notes = []
    unresolved = ["No supporting-information file was explicitly associated; detailed procedure, workup and atmosphere are unavailable."]
    if yield_value is None:
        outcomes.append(field("reaction_result", "reaction was complicated", evidence, ["product_2a"]))
        unresolved.append("No numeric yield of 2a is reported because the table marks the reaction as complicated.")
    if entry == 6:
        notes.append("Table 1 reports 63% for CCl4, while the adjacent prose states 67%; the table value is transcribed and the discrepancy is unresolved.")
        unresolved.append("Source discrepancy: CCl4 yield is 63% in Table 1 but 67% in adjacent prose.")
    if shared:
        outcomes.append(field("side_product_yield", {"number": 5, "unit": "%", "qualifier": "lt", "raw_text": "<5%"}, evidence, ["product_3a"]))
        notes += ["The paper states that epoxide 3a was formed in <5% yield, if any.",
                  "This experiment is repeated as Table 1 entry 9 and Table 2 entry 1 and is represented once."]
        unresolved.append("The phrase 'if any' leaves formation of side product 3a uncertain despite the reported <5% bound.")
    scope_outcomes = [field("isolated_yield", qty(yield_value, "%"), P2, ["product_2"]),
                      field("yield_measurement_basis", "isolated yield", P2, ["product_2"])]
    if entry in (6, 7, 8):
        scope_outcomes.append(field("allylic_C=C_halogenation", "not observed", P2, ["product_2"]))
    records.append(record(
        rid, source_id, "optimization_entry", evidence, participants,
        [{"step_id": "halogenation", "participant_ids": ["substrate_1a", "bromine", *solvent_ids], "conditions": conditions}],
        outcomes, notes, unresolved,
    ))


ar_smiles = {
    "H": "c1ccccc1",
    "p-CH3": "c1ccc(C)cc1",
    "p-OCH3": "c1ccc(OC)cc1",
    "m,p-OCH2O": "c1ccc2c(c1)OCO2",
}
r1_smiles = {"n-C4H9": "CCCC", "allyl": "CC=C", "C2H5": "CC"}
halogen_atom = {"Br2": "Br", "NBS": "Br", "I2": "I"}
halogen_smiles = {"Br2": "BrBr", "NBS": "O=C1CCC(=O)N1Br", "I2": "II"}
table2 = [
    (2, "n-C4H9", "p-CH3", "Br2", 0.5, 73, "2b", "rt", 2),
    (3, "n-C4H9", "p-CH3", "NBS", 2, 93, "2b", 0, 1.2),
    (4, "n-C4H9", "p-OCH3", "Br2", 1.5, 73, "2c", "rt", 2),
    (5, "n-C4H9", "m,p-OCH2O", "Br2", 0.5, 78, "2d", "rt", 2),
    (6, "allyl", "p-OCH3", "Br2", 1.5, 57, "2e", 0, 1.2),
    (7, "allyl", "p-CH3", "Br2", 1, 52, "2f", 0, 1.2),
    (8, "allyl", "p-CH3", "NBS", 1, 71, "2f", 0, 1.2),
    (9, "C2H5", "p-CH3", "Br2", 1.5, 71, "2g", "rt", 2),
    (10, "C2H5", "p-OCH3", "Br2", 1, 80, "2h", 0, 2),
    (11, "C2H5", "p-OCH3", "NBS", 0.7, 88, "2h", 0, 1.2),
    (12, "C2H5", "m,p-OCH2O", "Br2", 1.5, 64, "2i", "rt", 2),
    (13, "C2H5", "m,p-OCH2O", "NBS", 0.5, 84, "2i", 0, 1.2),
    (14, "n-C4H9", "m,p-OCH2O", "I2", 1, 80, "2j", "rt", 2),
    (15, "C2H5", "m,p-OCH2O", "I2", 0.5, 69, "2k", "rt", 2),
]
for entry, r1, r2, x2, hours, yield_value, product_label, temp, equiv in table2:
    substrate_smiles = f"C=C=C({r1_smiles[r1]})C(O){ar_smiles[r2]}"
    product_smiles = f"C=C({halogen_atom[x2]})C({r1_smiles[r1]})({ar_smiles[r2]})C=O"
    participants = [
        participant("substrate_1", "reactant", "1", f"2,3-allenol 1 (R1={r1}; R2={r2})", substrate_smiles, P2,
                    [field("reaction_scale", qrange(0.3, 0.5, "mmol", "0.3–0.5 mmol"), P2)]),
        participant("halogen_source", "reagent", x2, x2, halogen_smiles[x2], P2,
                    [field("equivalents", qty(equiv, "equiv"), P2)]),
        participant("solvent_mecn", "solvent", "MeCN", "acetonitrile", "CC#N", P2,
                    [field("volume", qty(4, "mL"), P2)]),
        participant("solvent_water", "solvent", "H2O", "water", "O", P2,
                    [field("volume", qty(0.27, "mL"), P2)]),
        participant("product_2", "product", product_label,
                    f"3-halo-3-enal {product_label} (R1={r1}; R2={r2}; X={halogen_atom[x2]})",
                    product_smiles, P2),
    ]
    notes = []
    unresolved = ["No supporting-information file was explicitly associated; detailed procedure, workup and atmosphere are unavailable."]
    if entry == 10:
        participants.append(participant("footnote_nbs", "unspecified_agent", "NBS", "N-bromosuccinimide", halogen_smiles["NBS"], P2,
                                        [field("equivalents", qty(1.2, "equiv"), P2)]))
        notes.append("Entry 10 lists Br2 with superscripts d,e, while footnote e specifies NBS; both the row reagent and the explicitly linked footnote reagent are retained, with the footnote amount structured on that participant.")
        unresolved.append("Table 2 entry 10 has an internal reagent/footnote inconsistency (Br2 row versus footnote e specifying NBS).")
    temp_value = "r.t." if temp == "rt" else qty(temp, "°C")
    records.append(record(
        f"table2_entry_{entry:02d}", f"Table 2 entry {entry}", "substrate_scope_entry", P2,
        participants,
        [{"step_id": "electrophilic_halogenation", "participant_ids": [p["entity_id"] for p in participants if p["role"] != "product"],
          "conditions": [field("solvent", "MeCN/H2O = 15:1", P2), field("temperature", temp_value, P2), field("time", qty(hours, "h"), P2)]}],
        scope_outcomes,
        notes, unresolved,
    ))


# Scheme 2: the generic X2 arrow represents two reported products and therefore
# two experiments.  The source gives neither time nor yield.
for x2, atom, product_label in [("I2", "I", "7a"), ("Br2", "Br", "7b")]:
    participants = [
        participant("substrate_6a", "reactant", "6a", "3-(n-butyl)penta-3,4-dien-2-ol", "C=C=C(CCCC)C(O)C", P2),
        participant("halogen_source", "reagent", x2, x2, halogen_smiles[x2], P2,
                    [field("equivalents", qty(2, "equiv"), P2)]),
        participant("solvent_mecn", "solvent", "CH3CN", "acetonitrile", "CC#N", P2),
        participant("solvent_water", "solvent", "H2O", "water", "O", P2),
        participant("product_7", "product", product_label, f"1,2-H shift product {product_label}",
                    f"C=C({atom})C(CCCC)C(C)=O", P2),
    ]
    records.append(record(
        f"scheme2_{product_label}", f"Scheme 2, {product_label}", "reported_experiment", P2,
        participants,
        [{"step_id": "halogenation_and_1_2_H_shift", "participant_ids": ["substrate_6a", "halogen_source", "solvent_mecn", "solvent_water"],
          "conditions": [field("solvent", "CH3CN/H2O = 15:1", P2), field("temperature", "r.t.", P2), field("time", None, P2)]}],
        [field("isolated_yield", None, P2, ["product_7"]),
         field("yield_measurement_basis", None, P2, ["product_7"]),
         field("selectivity", "highly selectively", P2, ["product_7"]),
         field("C=C_bond_migration", "not observed", P2, ["product_7"])],
        ["The text reports that 7a and 7b form highly selectively and that C=C migration was not observed."],
        ["Reaction time, product yield, yield basis, exact solvent volumes, workup and purification are not reported in the supplied main text.",
         "No supporting-information file was explicitly associated."],
    ))


AR_BENZODIOXOLE = "c1ccc2c(c1)OCO2"
SUB_2J = f"C=C(I)C(CCCC)({AR_BENZODIOXOLE})C=O"
scheme3 = [
    ("7j", "C=C(C#Cc1ccccc1)C(CCCC)(c1ccc2c(c1)OCO2)C=O", 96,
     [("pd_catalyst", "catalyst", "PdCl2(PPh3)2", "bis(triphenylphosphine)palladium(II) dichloride", None),
      ("coupling_partner", "reactant", "HC≡CPh", "phenylacetylene", "C#Cc1ccccc1"),
      ("cui", "unspecified_agent", "CuI", "copper(I) iodide", None)]),
    ("8j", "C=C(C#CCCCC)C(CCCC)(c1ccc2c(c1)OCO2)C=O", 93,
     [("pd_catalyst", "catalyst", "PdCl2(PPh3)2", "bis(triphenylphosphine)palladium(II) dichloride", None),
      ("coupling_partner", "reactant", "HC≡C-C4H9-n", "1-hexyne", "C#CCCCC"),
      ("cui", "unspecified_agent", "CuI", "copper(I) iodide", None)]),
    ("9j", "C=C(CCCC)C(CCCC)(c1ccc2c(c1)OCO2)C=O", 57,
     [("pd_catalyst", "catalyst", "Pd(PPh3)4", "tetrakis(triphenylphosphine)palladium(0)", None),
      ("coupling_partner", "reactant", "C4H9ZnBr", "n-butylzinc bromide", None)]),
    ("10j", "C=C(c1ccccc1)C(CCCC)(c1ccc2c(c1)OCO2)C=O", 98,
     [("pd_catalyst", "catalyst", "Pd(PPh3)4", "tetrakis(triphenylphosphine)palladium(0)", None),
      ("coupling_partner", "reactant", "PhB(OH)2", "phenylboronic acid", "OB(O)c1ccccc1")]),
    ("11j", "C=C(I)C(CCCC)(c1ccc2c(c1)OCO2)C(O)CC=C", 76,
     [("allyl_bromide", "reactant", "CH2=CHCH2Br", "allyl bromide", "C=CCBr"),
      ("zinc", "reagent", "Zn", "zinc", "[Zn]")]),
    ("12j", "C=C(I)C(CCCC)(c1ccc2c(c1)OCO2)CO", 91,
     [("sodium_borohydride", "reagent", "NaBH4", "sodium borohydride", "[Na+].[BH4-]")]),
]
for product_label, product_smiles, yield_value, agents in scheme3:
    participants = [
        participant("substrate_2j", "reactant", "2j", "3-iodo-3-enal 2j", SUB_2J, P2),
        participant("product", "product", product_label, f"functionalization product {product_label}", product_smiles, P2),
    ]
    for entity_id, role, label, name, smiles in agents:
        participants.append(participant(entity_id, role, label, name, smiles, P2))
    records.append(record(
        f"scheme3_product_{product_label}", f"Scheme 3, 2j to {product_label}", "reported_experiment", P2,
        participants,
        [{"step_id": "transformation", "participant_ids": [p["entity_id"] for p in participants if p["role"] != "product"],
          "conditions": [field("temperature", None, P2), field("time", None, P2), field("solvent", None, P2)]}],
        [field("yield", qty(yield_value, "%"), P2, ["product"]),
         field("yield_measurement_basis", None, P2, ["product"])],
        [f"Scheme 3 reports Y: {yield_value}% for product {product_label}."],
        ["Reagent/catalyst loadings, solvent, temperature, time, workup, purification and yield measurement basis are not reported in the supplied main text.",
         "No supporting-information file was explicitly associated."],
    ))


OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")

page1_ids = [r["record_id"] for r in records if f"{DOC}:page1:image" in r["evidence_ids"]]
page2_ids = [r["record_id"] for r in records if f"{DOC}:page2:image" in r["evidence_ids"]]
coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1,
            "state": "attempted",
            "regions": [
                {"region": "标题、摘要与双栏正文", "finding": "本篇报告2,3-联烯醇与Br2/NBS/I2的亲电反应；正文还提及既往联烯反应与由炔丙基溴制备底物的引用工作，未将引用工作冒充本篇实验。", "evidence_ids": P1},
                {"region": "右下 Table 1（含反应式、11行与脚注）", "finding": "建立11条独立优化记录；第9行与第2页Table 2第1行去重合并；第1–3行保留reaction was complicated与缺失数值收率；3a保留<5%, if any。", "evidence_ids": P1},
                {"region": "左下作者单位与ESI脚注", "finding": "正文声明ESI含experimental section，但本次来源映射未建立SI关联，因此不补写实验操作。", "evidence_ids": P1},
            ],
            "record_ids": page1_ids,
            "unresolved": [
                "ESI在论文中被声明存在，但本次未显式提供或关联。",
                "CCl4条件的2a收率在Table 1为63%，相邻正文为67%。",
                "3a的<5%陈述带有if any，实际是否检出不确定。",
            ],
        },
        {
            "page": 2,
            "state": "attempted",
            "regions": [
                {"region": "左上 Table 2（通式、15行与脚注a–e）", "finding": "逐行核查15行；第1行与Table 1第9行合并，其余14行建立独立底物范围记录；脚注中的反应规模、溶剂体积、温度和当量进入结构化字段。", "evidence_ids": P2},
                {"region": "右上 Scheme 1", "finding": "亲电加成、1,2-芳基迁移与脱H+的机理提案，不作为实际实验记录。", "evidence_ids": P2},
                {"region": "右中 Scheme 2", "finding": "6a与I2或Br2分别生成7a/7b，拆成2条实际实验记录；来源未给出时间和收率。", "evidence_ids": P2},
                {"region": "左中 Fig. 1", "finding": "2j的X射线晶体结构表征图，不是独立反应；未另建实验记录。", "evidence_ids": P2},
                {"region": "下部 Scheme 3（以2j为中心的六个箭头）", "finding": "按六个箭头建立2j到7j–12j的6条独立衍生化实验，并保留每个产物专属Y值。", "evidence_ids": P2},
            ],
            "record_ids": page2_ids,
            "unresolved": [
                "Table 2 entry 10列出Br2并标d,e，而脚注e明确写1.2 equiv NBS，来源内部不一致。",
                "Scheme 2缺时间、收率、具体体积、后处理与纯化。",
                "Scheme 3缺各试剂当量/催化剂负载、溶剂、温度、时间、后处理、纯化及收率测定依据。",
                "未显式关联SI。",
            ],
        },
        {
            "page": 3,
            "state": "attempted",
            "regions": [
                {"region": "左上结论", "finding": "仅总结本篇X+=Br/I条件下的1,2-芳基或质子迁移，没有新增逐项实验。", "evidence_ids": P3},
                {"region": "其余Notes and references 1–16", "finding": "均为背景、方法引用、晶体数据或参考文献；不作为本篇新增实验记录。", "evidence_ids": P3},
            ],
            "record_ids": [],
            "unresolved": ["本页没有实验操作细节；相关ESI未在本次数据集中显式关联。"],
        },
    ],
}
COVERAGE.parent.mkdir(parents=True, exist_ok=True)
COVERAGE.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"records": len(records), "raw": str(OUT), "coverage": str(COVERAGE)}, ensure_ascii=False))
