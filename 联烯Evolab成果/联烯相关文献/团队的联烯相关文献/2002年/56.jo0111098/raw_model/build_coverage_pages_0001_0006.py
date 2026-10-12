import json
from pathlib import Path

DOC = "doc_03ca6cf38d4f5d15"
ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / "runs" / "current"


def rid(name):
    return f"{DOC}:{name}"


scheme3 = [rid("scheme3_alkenylzinc"), rid("scheme3_phenylzinc")]
scheme5 = [rid(x) for x in ["scheme5_Z2a", "scheme5_Z2b", "scheme5_E2a", "scheme5_Z2c", "scheme5_E2c"]]
table1 = [rid(f"table1_entry{i}") for i in range(1, 6)]
table2 = [rid(f"table2_entry{i}") for i in range(1, 11)]
prelim = [rid("carbonate11b_12a_room_temp_no_reaction"), rid("carbonate11b_12a_55C_mixed_products")]
scheme8 = [rid(f"scheme8_entry{i}") for i in range(1, 5)]
scheme9 = [rid(x) for x in ["scheme9_11e_12a", "scheme9_11e_12d", "scheme9_11f_12a_no_product"]]
scheme10 = [rid("scheme10_11g_boronic"), rid("scheme10_11e_boronic")]
eq1 = [rid("equation1_propargyl_acetate_12a")]


def region(page, label, finding):
    return {
        "region": label,
        "finding": finding,
        "evidence_ids": [f"{DOC}:page{page}:image", f"{DOC}:page{page}:text"],
    }


pages = [
    {
        "page": 1,
        "state": "attempted",
        "regions": [
            region(1, "Scheme 1", "通式：联烯/炔丙基金属或钯物种偶联的 Pathway I/II；不是独立实验。"),
            region(1, "Scheme 2 and Introduction", "引用的既往工作与一般背景；未作为本篇新实验。"),
            region(1, "Results and Discussion, lower-right column", "本篇 A/B 混合钯络合物分别与 (2Z)-ethoxycarbonylethenylzinc iodide 和 phenylzinc bromide 的两项实验；与第2页 Scheme 3 和第6页操作合并。"),
        ],
        "record_ids": scheme3,
        "unresolved": ["Scheme 2 的产物结构属于引用工作，未展开为本篇记录。", "页末第二项实验跨至第2页，按跨页同一实验处理。"],
    },
    {
        "page": 2,
        "state": "attempted",
        "regions": [
            region(2, "Scheme 3", "两项本篇实际反应：A/B 与烯基锌给炔产物 57%，与 PhZnBr 给联烯产物 60%。"),
            region(2, "Scheme 4", "区域选择性控制的通式/概念图，不是独立实验。"),
            region(2, "Scheme 5", "五项不同底物/立体构型条件的实际偶联实验，分别建立记录。"),
            region(2, "Table 1 discussion", "正文逐项描述 Table 1 条目 1–5；与第3页表格行合并证据，不重复建记录。"),
        ],
        "record_ids": scheme3 + scheme5 + table1,
        "unresolved": ["Scheme 5 缩略条目的部分用量仅在后续实验段落出现；未用未查看的 SI 补齐。", "E-2c 的详细操作位于本次页范围之外，当前记录保持 partial。"],
    },
    {
        "page": 3,
        "state": "attempted",
        "regions": [
            region(3, "Table 1 rows 1–5", "五行独立底物范围实验；逐行保留温度、时间、两类产物收率及 2/6 比例。"),
            region(3, "Scheme 6", "提出的 Pd 催化机理循环；分类为机理，不建实际实验记录。"),
            region(3, "Scheme 7", "碳酸炔丙酯/有机金属偶联的设计通式；不是具名实验。"),
        ],
        "record_ids": table1,
        "unresolved": ["表中结构以标签和名称转录，SMILES 待化学审阅。", "表格未明确说明收率测量基准。"],
    },
    {
        "page": 4,
        "state": "attempted",
        "regions": [
            region(4, "Table 2 rows 1–10", "十行独立碳酸炔丙酯/烯基锌偶联实验；第7行同一实验含 55% 炔和18%联烯两个产物，第10行无产物。"),
            region(4, "Scheme 8 rows 1–4", "四项有机锌试剂制备/构型判定实验；脚注的 iodinolysis/hydrolysis 判定方法按行保留。"),
            region(4, "Prose below Table 2", "11b/12a 在室温无反应；另一次 55 °C 试验生成 Z-2h 与双键迁移产物，分别作为不同条件记录。"),
        ],
        "record_ids": table2 + prelim + scheme8,
        "unresolved": ["Table 2 entry 4 表格为 50 °C，而跨页正文对58%单一产物实验写55 °C；保留来源内冲突。", "55 °C 混合产物试验未报告反应时间和各产物收率。", "Scheme 8 本页未给各试剂用量。"],
    },
    {
        "page": 5,
        "state": "attempted",
        "regions": [
            region(5, "Table 2 continuation/discussion", "跨页补充 entry 4 的58%结果并讨论多个表格条目的构型变化和区域选择性；与第4页原行合并。"),
            region(5, "Scheme 9", "三项独立实验：11e/12a、11e/12d 生成 E-6e，以及 11f/12a 的0%失败结果。"),
            region(5, "Scheme 10", "两项独立实验：11g/烯基硼酸给 E-2o、E-6f 和少量13；11e/烯基硼酸在3.5 equiv Na2CO3下给 E-6g。"),
            region(5, "Equation (1)", "3-phenylprop-2-ynyl acetate 与 12a 的独立偶联，Z-2h 37%。"),
            region(5, "Scheme 11", "提出的氧化加成/互变机理；不是实际实验。"),
        ],
        "record_ids": table2 + scheme9 + scheme10 + eq1,
        "unresolved": ["副产物13仅称 small amount，未报告数值收率。", "Scheme 9/10 与式(1)的部分反应物用量未在本页图式中给出。", "未据论文的 SI availability 声明自行关联 SI。"],
    },
    {
        "page": 6,
        "state": "attempted",
        "regions": [
            region(6, "Conclusion and Materials", "结论、材料来源和表征通则；材料的文献制备说明不作为本篇独立反应。"),
            region(6, "A/B + (2Z)-ethoxycarbonylethenylzinc iodide procedure", "Scheme 3 第一项的详细操作、后处理、30 mg 与57%收率；合并入已有记录。"),
            region(6, "A/B + phenylzinc bromide procedure", "Scheme 3 第二项的详细多阶段操作、后处理、58 mg 与60%收率；合并入已有记录。"),
            region(6, "Z-2a, Z-2b and E-2a procedures", "Scheme 5 三项实验的典型/缩略实验段落；与图式记录合并。"),
            region(6, "Z-2c procedure (begins at page bottom)", "Z-2c 操作在本页开始但跨至第7页；仅使用本页明确内容，记录保持 partial。"),
        ],
        "record_ids": scheme3 + scheme5[:4],
        "unresolved": ["Z-2c 的产物表征与段落结尾在第7页，本次未声称覆盖。", "本页写明 SI 可获得，但工作区未显式提供/关联 SI。", "缩略的 Z-2b/E-2a 条目引用相似条件，未推断未重述的全部步骤。"],
    },
]

coverage = {"document_id": DOC, "semantic_accuracy_verified": False, "pages": pages}
(RUN / "coverage").mkdir(parents=True, exist_ok=True)
(RUN / "coverage" / "pages_0001_0006.json").write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

tasks_path = RUN / "tasks.json"
tasks = json.loads(tasks_path.read_text())
for task in tasks:
    if task.get("document_id") == DOC and task.get("task_id", "").endswith(":text"):
        page = int(task["task_id"].split(":page", 1)[1].split(":", 1)[0])
        if 1 <= page <= 6:
            task["state"] = "attempted"
            task["reason"] = "Original page image and page text inspected; see coverage/pages_0001_0006.json."
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"pages": [p["page"] for p in pages], "regions": sum(len(p["regions"]) for p in pages), "unique_record_ids": len({r for p in pages for r in p["record_ids"]})}, ensure_ascii=False))
