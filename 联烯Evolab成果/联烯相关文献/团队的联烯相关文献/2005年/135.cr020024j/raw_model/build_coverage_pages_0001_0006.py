#!/usr/bin/env python3
import json
from pathlib import Path

DOC = "doc_a46c3871d27d020b"
dataset = json.loads(Path(__file__).parents[1].joinpath("dataset.json").read_text())


def evidence(page):
    return [f"{DOC}:page{page}:image", f"{DOC}:page{page}:text"]


regions = {
    1: [
        ("整页上半部：题名、作者、目录及引言", "无实验；这是综述题名、目录和背景引言。"),
        ("右栏下部 Scheme 1", "引用工作：丙二烯与α,β-不饱和环己烯酮在光照下的[2+2]环加成。"),
        ("右栏最下部 Scheme 2 引入段", "引用工作：DABCO路线和DMAP路线的正文说明起始于本页，反应图及机理续至第2页。"),
    ],
    2: [
        ("左栏上部作者照片与简介", "无反应；作者简介。"),
        ("左栏中下部 Scheme 2", "引用工作与机理：分别记录DABCO催化生成3、DMAP催化生成13，以及两条提议催化路径。"),
        ("右栏上部 Scheme 3", "引用工作：14分别与烯烃或炔烃反应；烯烃范围收率为汇总区间，两个炔烃例子有独立收率。"),
        ("右栏中下部 Scheme 4", "引用工作/底物范围：17A、17B、17C各自三行取代基与收率，逐行独立建条目。"),
        ("右栏底部 Scheme 5 引入正文", "引用工作：14与烯醚19生成22；图示机理位于第3页。"),
    ],
    3: [
        ("左栏上部 Scheme 5", "提议机理：14/19经20与Z-21/E-21或23的两条替代路径生成22。"),
        ("左栏中部 Scheme 6", "引用工作：24分别与25和27反应，两个箭头独立记录。"),
        ("左栏中部 Scheme 7", "引用工作：15 kbar下的高压[2+2]反应；温度选项与具体底物映射无法从综述页恢复。"),
        ("左栏下部 Scheme 8", "引用工作：31→32与33→34两条光化学分子内[2+2]反应。"),
        ("右栏上部 Scheme 9", "引用工作：35范围条目，以及37中X=O与X=S两个独立结果，保留收率和ee。"),
        ("右栏中部 Scheme 10", "引用工作：39→40、41→42及43→44+45三条不同反应条件。"),
        ("右栏下部 Scheme 11", "引用工作与机理：46的两个R取代例及经47的提议双自由基路径。"),
    ],
    4: [
        ("左栏上部 Scheme 12", "引用工作：49A氧化后与不氧化加热两条分支；综述正文与图中n/标签注释存在难以协调之处。"),
        ("左栏中部 Scheme 13", "引用工作/底物范围：53三行与54两行，均逐行保留220 °C、密封管、dr与收率。"),
        ("左栏下部 Scheme 14", "引用工作：Ni(PPh3)4催化55二聚，收率为底物范围区间。"),
        ("右栏上部 Scheme 15", "引用工作：57、59的关环以及61/62在360 °C的平衡，三条独立记录。"),
        ("右栏中部 Scheme 16", "引用工作：63→64热关环及64→62脱硅两步分开记录。"),
        ("右栏下部 Scheme 17", "引用工作：65→66和67→68两条热关环。"),
        ("右栏最下部 2.2节及Scheme 18引入正文", "引用工作：Scheme 18反应描述始于本页，反应图位于第5页。"),
    ],
    5: [
        ("左栏上部 Scheme 18", "引用工作与机理：69在1,4-环己二烯存在下生成70及少量71，并保留72为提议双自由基。"),
        ("左栏中下部 Scheme 19", "引用工作：73与三种捕获剂的三行反应，以及78和81两条独立Myers–Saito反应。"),
        ("右栏上部 Scheme 20", "引用工作与机理：83在75 °C、1 h经84/85生成86。"),
        ("右栏中部 Scheme 21", "引用工作与机理：87按R2分支生成89或90；91在MeOH与CDCl3中的两个条件分别生成93和92。"),
        ("右栏下部跨页正文", "引用工作上下文：94/97的Scheme 22、100的Scheme 23和102的Scheme 24说明续至第6页原图。"),
    ],
    6: [
        ("左栏上部 Scheme 22", "引用工作与机理：94→95→96及97→98→99两条不同温度/收率的自由基环化。"),
        ("左栏中部 Scheme 23", "引用工作：100在1,4-环己二烯/甲苯中105 °C生成101，38%。"),
        ("左栏中下部 Scheme 24", "引用工作与机理：102在60–70 °C经103、104和[1,5-H]迁移生成105。"),
        ("左栏下部 Scheme 25", "引用工作：108、106、107三种取代基对应不同温度、时间、产物和收率，分为三条。"),
        ("右栏上部 Scheme 26", "引用工作与机理：112的R=t-Bu与R=H两行收率及经自由基/113到114的路径。"),
        ("右栏中部 Scheme 27", "引用工作与机理：115经1,4-双自由基偶联生成116，62%。"),
        ("右栏中下部 Scheme 28", "引用工作：117在Mo(CO)6、DMSO/甲苯、100 °C下生成118；收率为范围。"),
        ("右栏下部 Scheme 29", "引用工作与机理：119与1,1-二取代联烯先形成120，再retro-[2+2]生成121。"),
    ],
}

unresolved = {
    1: ["Scheme 1未给收率、精确温度和时间。", "Scheme 2跨页，复杂通式结构未生成SMILES。"],
    2: ["Scheme 3烯烃行仅给55–98%汇总范围。", "Scheme 4只写heat，未给确切温度/时间。", "Scheme 5未给反应条件和收率。"],
    3: ["多处为R基团通式或范围，无法无歧义转写完整结构。", "Scheme 7的rt/50 °C与具体底物映射未显示。", "各收率的测定基础未说明。"],
    4: ["Scheme 12正文与图中49A/49B、n和51注释存在潜在不一致，需查原始论文。", "Scheme 14、16为范围汇总而非逐底物明细。", "各收率的测定基础未说明。"],
    5: ["Scheme 18中70的X分支与71的具体形成比例需查原始论文。", "Scheme 19若干箭头未给收率或完整条件。", "Scheme 21的87分支未给温度、时间或收率。"],
    6: ["Scheme 25中各箭头的完整试剂环境仅凭综述图不能完全恢复。", "Scheme 26、27未给完整反应条件。", "Scheme 28、29收率为范围且无逐底物对应。"],
}

pages = []
for page in range(1, 7):
    image_id = f"{DOC}:page{page}:image"
    record_ids = [
        r["record_id"] for r in dataset["experiments"] if image_id in r["evidence_ids"]
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
out = Path(__file__).parents[1] / "coverage" / "pages_0001_0006.json"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"output": str(out), "pages": len(pages)}, ensure_ascii=False))
