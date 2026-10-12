#!/usr/bin/env python3
"""Build the exact page 37--42 coverage ledger and mark those tasks attempted."""
import json
from pathlib import Path

DOC = "doc_a46c3871d27d020b"
BASE = Path(__file__).parents[1]
dataset = json.loads((BASE / "dataset.json").read_text())


def evidence(page):
    return [f"{DOC}:page{page}:image", f"{DOC}:page{page}:text"]


regions = {
    37: [
        ("左栏上部 Scheme 174–175", "引用工作：补全第36页边界记录；Scheme 174按MeOH和六种亲电体逐箭头建档，Scheme 175的818与820两条立体专一性反应分开。"),
        ("左栏中下部 Scheme 176", "引用工作/范围：823通式范围单列；824的两行烯丙基磷酸酯按75%与70%逐行记录。"),
        ("右栏 Scheme 177", "引用工作与机理：825和830的碱诱导扩环范围、832的五行R1/R2收率及两个提议路径分别记录。"),
        ("页底正文跨页引入 Schemes 178–182", "引用工作上下文：氧杂Cope、Claisen、Rh硅基环化、Pd偶联和交叉复分解的正文说明续至第38页原图；对应记录合并两页证据。"),
    ],
    38: [
        ("左栏 Scheme 178–179", "引用工作/通式/机理：835→836、838与839两分支、Claisen通式及三个具体箭头分开；DMF/苯条件未强行逐例映射。"),
        ("右栏上中部 Scheme 180–182", "引用工作：两条Rh反应、Pd(II)偶联、联烯交叉复分解产物范围及R=Ar仅聚合失败结果均独立建档。"),
        ("右栏下部 Scheme 183", "引用工作及提议机理：846与848两个底物范围分开，Pd通路单列为机制。"),
        ("页底正文跨页引入 Schemes 184–185", "引用工作上下文：钒催化醛醇型加成和不对称双环丙烷化的说明续至第39页原图；记录合并两页证据。"),
    ],
    39: [
        ("左栏上部 Scheme 184–185", "引用工作与机理：850的钒催化反应及循环、855常规范围和R=Ph的7%低收率结果分别记录。"),
        ("左栏中下部 Scheme 186–187", "引用工作/逐行范围：858范围、α-取代烯酮无反应、859四个醛行及860的收率/ee范围分别建档。"),
        ("右栏及左栏页底：结论、缩写、致谢与ASAP说明", "无新增反应；属于综述结论和文后信息。"),
    ],
    40: [
        ("整页 References 1–57", "无反应图、表或实验箭头；本页仅为参考文献列表。"),
    ],
    41: [
        ("整页 References 58–136", "无反应图、表或实验箭头；本页仅为参考文献列表。"),
    ],
    42: [
        ("整页 References 137–203", "无反应图、表或实验箭头；本页仅为参考文献列表。"),
    ],
}

unresolved = {
    37: [
        "Scheme 174亲电体捕获箭头未单独标温度/时间；只将−40 °C、1 h用于815形成阶段。",
        "Scheme 177的多种碱与具体R取代底物未逐行映射；复杂结构仅保留标签。",
    ],
    38: [
        "Scheme 179未说明三个具体例子分别使用DMF/120 °C还是苯回流。",
        "Schemes 180–183多为综述汇总范围，缺逐底物条件、时间和收率测定基础。",
    ],
    39: [
        "Scheme 186第三个醛行印作‘i-Bn’，未猜测其真实取代基身份。",
        "Scheme 187试剂缩写按原图保留为ADMX，未从综述页推断其配方。",
    ],
    40: ["本页只核查为参考文献列表；未把引用条目本身转换为实验记录。"],
    41: ["本页只核查为参考文献列表；未把引用条目本身转换为实验记录。"],
    42: ["本页只核查为参考文献列表；参考文献续页不在本批覆盖范围。"],
}

pages = []
for page in range(37, 43):
    image_id = f"{DOC}:page{page}:image"
    record_ids = [
        record["record_id"] for record in dataset["experiments"]
        if image_id in record["evidence_ids"]
    ]
    pages.append({
        "page": page,
        "state": "attempted",
        "regions": [
            {"region": region, "finding": finding, "evidence_ids": evidence(page)}
            for region, finding in regions[page]
        ],
        "record_ids": record_ids,
        "unresolved": unresolved[page],
    })

coverage = {"document_id": DOC, "semantic_accuracy_verified": False, "pages": pages}
path = BASE / "coverage" / "pages_0037_0042.json"
path.parent.mkdir(parents=True, exist_ok=True)
path.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

tasks_path = BASE / "tasks.json"
tasks = json.loads(tasks_path.read_text())
target_ids = {f"{DOC}:page{page}:text" for page in range(37, 43)}
for task in tasks:
    if task.get("document_id") == DOC and task.get("evidence_id") in target_ids:
        page = int(task["evidence_id"].split(":page", 1)[1].split(":", 1)[0])
        task["state"] = "attempted"
        task["visual_evidence_id"] = f"{DOC}:page{page}:image"
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({
    "coverage": str(path), "pages": len(pages),
    "record_links": sum(len(page["record_ids"]) for page in pages),
}, ensure_ascii=False))
