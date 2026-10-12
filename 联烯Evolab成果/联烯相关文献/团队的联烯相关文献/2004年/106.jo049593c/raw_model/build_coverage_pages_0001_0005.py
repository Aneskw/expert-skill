#!/usr/bin/env python3
"""Write the required pages 1-5 coverage ledger and mark page tasks attempted."""
import json
from pathlib import Path

DOC = "doc_c1d24ef1513fb165"
CURRENT = Path(__file__).resolve().parents[1]
DATASET = CURRENT / "dataset.json"
COVERAGE = CURRENT / "coverage" / "pages_0001_0005.json"


def rid(suffix):
    return f"{DOC}:{suffix}"


def ids(prefix, entries):
    return [rid(f"{prefix}{entry:02d}") for entry in entries]


page2_scheme = [
    rid("scheme1_general_sulfide_preparation"),
    rid("scheme2_general_selenide_rearrangement"),
    rid("equation1_sulfide_2s_preparation"),
]
page2_scheme3 = [rid("scheme3_mecn_condition"), rid("table1_entry01")]
page2_table1 = ids("table1_entry", range(1, 15))

page3_scheme4 = ids("scheme4_entry", range(1, 4))
page3_oxidations = [rid("literature_oxidation_6e_mcpba"), rid("literature_oxidation_6e_h2o2")]
page3_table2 = ids("table2_entry", range(1, 12))
page3_table3 = ids("table3_entry", [1, 2, 3, 4, 5, 7, 8, 9, 10, 11, 12, 14, 15, 16, 17, 18])

page4_table4 = ids("table4_entry", [1, 2, 3, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14])
page4_scheme5 = [rid("scheme5_2r"), rid("scheme5_2s")]
page4_table5 = ids("table5_entry", range(1, 19))
page4_table6 = ids("table6_entry", range(1, 11))
page4_scheme6 = [rid("scheme6_4a"), rid("scheme6_4b"), rid("scheme6_4o")]
page4_scheme7_context = [rid("scheme7_literature_z_branch"), rid("scheme7_literature_e_branch")]

page5_scheme7 = page4_scheme7_context
page5_scheme8 = [rid("scheme8_proposed_mechanism")]
page5_scheme5_context = page4_scheme5


def evidence(page):
    return [f"{DOC}:page{page}:image", f"{DOC}:page{page}:text"]


pages = [
    {
        "page": 1,
        "state": "attempted",
        "regions": [
            {
                "region": "title, abstract, and two-column Introduction",
                "finding": "No individual experiment row or reaction arrow is present. The abstract states the paper-level halohydroxylation claim; the Introduction discusses background and cited prior work only.",
                "evidence_ids": evidence(1),
            },
            {
                "region": "footnotes and references 1-9",
                "finding": "Bibliographic prior work and background references; no sufficiently specified experiment on this page was converted into a record.",
                "evidence_ids": evidence(1),
            },
        ],
        "record_ids": [],
        "unresolved": ["Page 1 contains high-level claims but no row/arrow-level experimental quantities."],
    },
    {
        "page": 2,
        "state": "attempted",
        "regions": [
            {
                "region": "left column Scheme 1",
                "finding": "Generic reduction of allenyl sulfoxides 1 to sulfides 2 with P2S5/pyridine in CH2Cl2 at room temperature; classified as a general scheme because no individual yield/scale/time is shown.",
                "evidence_ids": evidence(2),
            },
            {
                "region": "left column Scheme 2 and equation (1)",
                "finding": "Generic propargyl selenide rearrangement 3 to 4 at 48 °C for 70 min and a separate reported preparation of 2s with t-BuOK/t-BuOH. The 0.1 N normality is preserved as source text.",
                "evidence_ids": evidence(2),
            },
            {
                "region": "upper-right Scheme 3 and adjacent discussion",
                "finding": "Two distinct iodination conditions for 2a were represented: MeCN/H2O gives 5a and 0% 6a; the acetone/H2O condition is the same experiment as Table 1 entry 1 and is not duplicated.",
                "evidence_ids": evidence(2),
            },
            {
                "region": "right-column Table 1 including footnotes a-e",
                "finding": "All 14 substrate-scope rows were extracted separately. Each aldehyde coproduct 5 is structured as trace or the footnoted 14-18% yield, and each main yield/selectivity targets product 6.",
                "evidence_ids": evidence(2),
            },
        ],
        "record_ids": list(dict.fromkeys(page2_scheme + page2_scheme3 + page2_table1)),
        "unresolved": [
            "Scheme 3 labels the 6a ratio as E/Z (>99:1), while Table 1 labels 6a as Z/E=99/1; no silent reconciliation was made.",
            "Main-product yield measurement basis, reaction scale, detailed operation, workup and purification are absent from the supplied main text.",
            "Most substrate/product structures are R-group depictions and remain label-based with null SMILES pending structure review.",
        ],
    },
    {
        "page": 3,
        "state": "attempted",
        "regions": [
            {
                "region": "top-left Scheme 4",
                "finding": "Three separate reactions were extracted: 2o/I2 to 9o, 2p/I2 to 9p, and 2p/Br2 to 11p, each with its own yield and Z/E ratio.",
                "evidence_ids": evidence(3),
            },
            {
                "region": "opening prose on oxidation of Z-6e",
                "finding": "Two alternative prior-literature oxidations to Z-8e (m-CPBA/CH2Cl2 and H2O2/HOAc) were separated and classified as literature examples, not new experiments.",
                "evidence_ids": evidence(3),
            },
            {
                "region": "left-column Table 2 including solvent footnotes",
                "finding": "All 11 optimization rows for 2b were extracted separately, including CuBr2, NBS and Br2 loadings and the footnoted solvent changes in entries 10-11.",
                "evidence_ids": evidence(3),
            },
            {
                "region": "upper-right Table 3 and footnote",
                "finding": "All 16 printed optimization rows for 2e were extracted separately; additives and their equivalents are participants, and crude-product Z/E values are retained.",
                "evidence_ids": evidence(3),
            },
            {
                "region": "lower discussion paragraphs",
                "finding": "Narrative comparisons and the selected Table 3 condition are supporting prose for the same table rows, not new experiments.",
                "evidence_ids": evidence(3),
            },
        ],
        "record_ids": page3_scheme4 + page3_oxidations + page3_table2 + page3_table3,
        "unresolved": [
            "Table 3 prints the yield header as product 10d, while the depicted structure and prose identify 10e; records retain 10e and flag the source inconsistency.",
            "The cited Z-6e oxidation examples lack amounts, time, temperature and yield in this source.",
            "Yield basis, scale, workup and purification are not given for the table rows.",
        ],
    },
    {
        "page": 4,
        "state": "attempted",
        "regions": [
            {
                "region": "upper-left Table 4 including footnotes b-c",
                "finding": "All 13 printed substrate-scope rows were extracted. Entry 1 omits Na2CO3 per footnote b; entry 14 uses p-bromophenyl sulfide per footnote c.",
                "evidence_ids": evidence(4),
            },
            {
                "region": "middle-left Scheme 5",
                "finding": "Separate 2r and 2s bromohydroxylation experiments were extracted. The 10s yield is left missing because Scheme 5 prints 44% but page 5 prose prints 43%.",
                "evidence_ids": evidence(4),
            },
            {
                "region": "upper-right Table 5 including footnotes a-e",
                "finding": "All 18 iodine-optimization rows were extracted independently. LiOAc·2H2O (2 equiv) is structured for entry 1, addition time is structured for every row, and not-determined Z/E cells remain null/missing.",
                "evidence_ids": evidence(4),
            },
            {
                "region": "middle-right Table 6 and shared reaction arrow",
                "finding": "All 10 iodohydroxylation scope rows were extracted with shared I2 loading, MeCN/H2O ratio, 0 °C and N2 conditions plus row-specific time/yield/Z-E data.",
                "evidence_ids": evidence(4),
            },
            {
                "region": "lower-right Scheme 6",
                "finding": "Three substrate-specific bromohydroxylation failures/trace outcomes were retained separately for 4a, 4b and source-labeled 4o.",
                "evidence_ids": evidence(4),
            },
            {
                "region": "bottom-right prose introducing mercury methoxymercuration",
                "finding": "This paragraph introduces cited prior work continued as Scheme 7 on page 5; it is linked to the two literature-example branch records and is not treated as this paper's experiment.",
                "evidence_ids": evidence(4),
            },
        ],
        "record_ids": page4_table4 + page4_scheme5 + page4_table5 + page4_table6 + page4_scheme6 + page4_scheme7_context,
        "unresolved": [
            "Scheme 5/page 5 disagree on 10s yield (44% versus 43%).",
            "Table 5 entry 18 row (I2 loading and 1:1 solvent) conflicts with adjacent prose that calls the solvent 4:1.",
            "Scheme 6 labels the ortho-tolyl substrate 4o, while Table 6 assigns o-tolyl to 4c.",
            "Scheme 6 reports trace while prose describes failure to yield expected product; trace is preserved without conversion to zero.",
        ],
    },
    {
        "page": 5,
        "state": "attempted",
        "regions": [
            {
                "region": "upper-left Scheme 7",
                "finding": "Two mechanistic branches of a cited Hg(OAc)2 methoxymercuration example were represented as literature_example records (Z-14 83%, E-14 17%), not as experiments performed in this paper.",
                "evidence_ids": evidence(5),
            },
            {
                "region": "upper-right Scheme 8",
                "finding": "Generic halogen association, bridged intermediate Z-16 and water attack were captured as a mechanism record without experimental yield.",
                "evidence_ids": evidence(5),
            },
            {
                "region": "left-column Scheme 5 discussion",
                "finding": "The prose repeats the 2r/2s experiments rather than defining new reactions; evidence is merged into the page 4 Scheme 5 records and exposes the 10s 43%/44% conflict.",
                "evidence_ids": evidence(5),
            },
            {
                "region": "conclusion, acknowledgments, and Supporting Information notice",
                "finding": "No additional experiment is specified. SI is advertised as available, but no SI file was supplied or explicitly associated in this workspace.",
                "evidence_ids": evidence(5),
            },
        ],
        "record_ids": page5_scheme7 + page5_scheme8 + page5_scheme5_context,
        "unresolved": [
            "The source article for Scheme 7 reference 18 was not supplied, so its detailed conditions and yield basis cannot be checked.",
            "Scheme 8 is mechanistic rationale only and its generic structures are not assigned SMILES.",
            "The advertised Supporting Information is not part of the supplied source set and remains unassociated.",
        ],
    },
]

ledger = {"document_id": DOC, "semantic_accuracy_verified": False, "pages": pages}

dataset = json.loads(DATASET.read_text())
known = {r["record_id"] for r in dataset["experiments"]}
referenced = {record_id for page in pages for record_id in page["record_ids"]}
missing = sorted(referenced - known)
uncovered = sorted(known - referenced)
if missing or uncovered:
    raise SystemExit(f"coverage mismatch: missing={missing}, uncovered={uncovered}")
if [page["page"] for page in pages] != [1, 2, 3, 4, 5]:
    raise SystemExit("coverage must contain exactly pages 1-5")
if any(not page["regions"] for page in pages):
    raise SystemExit("every page needs at least one region")
for page in pages:
    expected_image = f"{DOC}:page{page['page']}:image"
    if any(expected_image not in region["evidence_ids"] for region in page["regions"]):
        raise SystemExit(f"page {page['page']} region lacks page-image evidence")

COVERAGE.parent.mkdir(parents=True, exist_ok=True)
COVERAGE.write_text(json.dumps(ledger, ensure_ascii=False, indent=2) + "\n")

tasks_path = CURRENT / "tasks.json"
tasks = json.loads(tasks_path.read_text())
for task in tasks:
    if task.get("document_id") == DOC and task.get("evidence_id", "").endswith(":text"):
        page = int(task["evidence_id"].split(":page", 1)[1].split(":", 1)[0])
        if 1 <= page <= 5:
            task["state"] = "attempted"
            task["visual_evidence_id"] = f"{DOC}:page{page}:image"
            task["reason"] = "Original page image and extracted text inspected; records and unresolved issues mapped in coverage/pages_0001_0005.json."
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"coverage": str(COVERAGE), "pages": len(pages), "records": len(known)}, ensure_ascii=False))
