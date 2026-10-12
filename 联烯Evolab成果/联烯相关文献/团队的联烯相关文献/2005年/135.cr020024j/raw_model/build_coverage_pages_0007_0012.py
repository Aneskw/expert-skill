#!/usr/bin/env python3
"""Build the page 7--12 coverage ledger and mark those page tasks attempted."""
import json
from pathlib import Path

DOC = "doc_a46c3871d27d020b"
BASE = Path(__file__).parents[1]
dataset = json.loads((BASE / "dataset.json").read_text())


def evidence(page):
    return [f"{DOC}:page{page}:image", f"{DOC}:page{page}:text"]


regions = {
    7: [
        ("左栏上部 Scheme 30–31", "引用工作及提议路径：同一铬卡宾/联烯体系在Ni(COD)2或10 mol%铑催化剂下分别生成124或126；总体反应与机理分开记录。"),
        ("左栏下部 Scheme 32", "引用工作：Ni介导[3+2+2]支路、Rh催化支路及128的酸解为三个连续但独立箭头；收率分别按产物关联。"),
        ("右栏 Scheme 33", "引用工作/底物范围及机理：三组分子间钛催化氢胺化、一个分子内例子，以及136–138提议循环。"),
        ("右栏底部跨页正文", "Scheme 34的动力学拆分、142分离及丙二烯置换说明始于本页，图和逐行收率位于第8页，已合并跨页证据。"),
    ],
    8: [
        ("左栏上部 Scheme 34", "引用工作：139与联烯络合、141的五行动力学拆分结果、两类142形成及10 equiv丙二烯置换分别建条目。"),
        ("左栏中下部 Scheme 35", "提议机理：144经β-H消除/氢金属化或147↔148↔149烯丙基重排解释构型反转，不作为独立实验。"),
        ("右栏 Scheme 36–37", "引用工作：R取代切换[4+2]/[2+2]路径；154的两分支与157的R=H/Me分支独立记录，159和158B收率关联各自产物。"),
        ("右栏底部正文", "Scheme 38和39的引用工作由本页正文引入、具体箭头及条件在第9页；相应记录使用跨页证据。"),
    ],
    9: [
        ("左栏上部 Scheme 38–40", "引用工作：160与环戊二烯、162的分子内环加成、164的室温反应及166+167框架构建；161→162仅称several steps，未补造步骤。"),
        ("左栏中下部 Scheme 41", "引用工作/条件分支：169和174分别按两组温度/时间拆分，171–177的逐产物收率保留；178→179另建条目。"),
        ("右栏上部 Scheme 42", "引用工作及路径：180热环加成；182经183到184的图示序列另保留为提议路径，条件缺失。"),
        ("右栏中下部 Scheme 43", "引用工作/底物范围：185、187及189表格式四行逐行记录催化剂、配体/添加剂、温度、产物、收率和trans/cis。"),
        ("右栏底部正文", "Scheme 44的回流/室温分支及机理说明跨至第10页，已合并跨页证据。"),
    ],
    10: [
        ("左栏 Scheme 44–45", "引用工作及机理：192+193回流和室温长时反应分开；196–200仅作提议路径；201+202热反应及203中间体分类为引用例子/机理。"),
        ("右栏上部 Scheme 46", "引用工作/底物范围：205的六行R/X收率逐行建条目；207+208仅有汇总收率和dr范围，额外印刷条件的阶段保持未决。"),
        ("右栏中部 Scheme 47", "引用工作/底物范围：210与四种亲双烯体、215的两行取代基均独立记录。"),
        ("右栏下部 Scheme 48", "引用工作与路径：217和TCNE在甲苯25 °C生成219，总体反应与经218的后续关环路径分开。"),
        ("页底跨页正文", "Scheme 49的BF3·OEt2催化反应说明续至第11页，记录使用第10–11页证据。"),
    ],
    11: [
        ("左栏上部 Scheme 49", "引用工作：220+醛的范围、222+亚胺的单例及224分子内范围分别记录。"),
        ("左栏中部 Scheme 50与右栏 Scheme 51", "引用工作与机理：226+227的PBu3催化反应保留汇总收率/dr；229–233循环单列为提议机理。"),
        ("右栏中部 Scheme 52", "引用工作：234在PhNCO/Et3N、苯回流下生成235，40%。"),
        ("右栏中下部 Scheme 53", "引用工作与机理：236在未指明碱、室温下形成242；237–241自由基/环加成级联为提议路径。"),
        ("右栏下部 Scheme 54及页底正文", "引用工作/路径：243与PhNHOH经244生成245；Scheme 55的一般PR3机理说明跨至第12页。"),
    ],
    12: [
        ("左栏上部 Scheme 55", "一般提议机理：246与PR3经247–250形成251；EWG变量未展开，不冒充具体实验。"),
        ("左栏中下部 Scheme 56–57", "引用工作/底物范围：Scheme 56三行分别关联252/253收率；Scheme 57保留255/256合并收率与产物比范围。"),
        ("右栏上部 Scheme 58", "引用工作/多步合成：关键[3+2]、氢化、酸处理、Zn/CH2I2/TiCl4步骤及两步转化至(−)-hinesol分别建记录。"),
        ("右栏中下部 Scheme 59–60", "引用工作/底物范围与机理：261的三行EWG、263的两行R逐行记录；247a/266–270为提议循环。"),
        ("右栏底部 Scheme 61–62引入正文", "只见文字引入而图在第13页：硫代苯甲酰胺反应及272→273各保留text-only部分记录，不声称看过第13页图。"),
    ],
}

unresolved = {
    7: [
        "Scheme 30–33多为通式或汇总范围，缺逐底物条件、时间和收率测定基础。",
        "Scheme 34跨页；起始联烯用量仅定性描述，未强制转成精确当量。",
    ],
    8: [
        "Scheme 34首行小字号取代基暂按印刷C3H5保留，需原始论文确认。",
        "Scheme 35–37多数未给温度、时间、收率或产物测定基础。",
    ],
    9: [
        "Scheme 38中161到162只写several steps，试剂、条件和各步产率缺失。",
        "Scheme 43紧凑配体/添加剂化学式仅文字保留，需原始论文核对。",
        "Scheme 40、42未给完整条件和收率。",
    ],
    10: [
        "Scheme 44室温分支只报混合物，未给194/195比例或分支收率。",
        "Scheme 46的'r.t., dry PhH'与MeCN 80–120 °C的阶段归属在综述图上不够明确。",
        "Scheme 45、48缺完整实验条件或收率。",
    ],
    11: [
        "Scheme 49的224范围、Scheme 53和54缺完整条件、时间及收率。",
        "Scheme 53所用base未指明，未猜测其身份。",
    ],
    12: [
        "Scheme 56–59多为汇总范围或标签结构，收率测定基础未说明。",
        "Scheme 61和62图位于第13页且不在本批次原图范围，只编码第12页明确文字；下游细节保持缺失。",
        "未提供或明确关联支持信息，所有记录仍需原始论文/实验部分核查。",
    ],
}

pages = []
for page in range(7, 13):
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

coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": pages,
}
coverage_path = BASE / "coverage" / "pages_0007_0012.json"
coverage_path.parent.mkdir(parents=True, exist_ok=True)
coverage_path.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

tasks_path = BASE / "tasks.json"
tasks = json.loads(tasks_path.read_text())
for task in tasks:
    if task.get("document_id") == DOC and task.get("evidence_id") in {
            f"{DOC}:page{page}:text" for page in range(7, 13)}:
        task["state"] = "attempted"
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({
    "coverage": str(coverage_path),
    "pages": len(pages),
    "record_links": sum(len(page["record_ids"]) for page in pages),
}, ensure_ascii=False))
