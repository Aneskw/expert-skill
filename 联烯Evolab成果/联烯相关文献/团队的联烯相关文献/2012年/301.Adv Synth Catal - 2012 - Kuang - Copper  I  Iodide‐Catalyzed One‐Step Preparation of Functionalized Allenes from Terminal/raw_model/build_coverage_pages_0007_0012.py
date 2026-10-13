import json
from pathlib import Path


BASE = Path(__file__).resolve().parents[1]
DOC = "doc_1e29b02f2fac50bb"


def evidence(page):
    return [f"{DOC}:page{page}:image", f"{DOC}:page{page}:text"]


def rid(suffix):
    return f"{DOC}:{suffix}"


pages = [
    {
        "page": 7,
        "state": "attempted",
        "regions": [
            {
                "region": "upper-left continuation of 2k and middle-left preparation of 2l",
                "finding": "The cross-page 2k outcome was merged into Table 4 entry 12; the detailed 2l batch was merged into entry 13 with exact charges, product mass, chromatography, and isolated yield.",
                "evidence_ids": evidence(7),
            },
            {
                "region": "lower-left preparation of 2m and right-column preparations of 2n–2o",
                "finding": "Detailed batches for 2m, 2n, and the beginning of the cross-page 2o paragraph were merged into Table 4 entries 14–16; each remains a distinct experiment.",
                "evidence_ids": evidence(7),
            },
        ],
        "record_ids": [rid(f"table4_entry{entry}") for entry in range(12, 17)],
        "unresolved": [
            "For 2k, the printed CuI mass/mmol conflicts with the 20 mol% Table 4 loading and was not corrected.",
            "The 2o preparation continues on page 8.",
        ],
    },
    {
        "page": 8,
        "state": "attempted",
        "regions": [
            {
                "region": "upper-left continuation of 2o and middle-left preparation of 2p",
                "finding": "The 2o outcome was completed across pages 7–8; the exact 2p batch was merged into Table 4 entry 17.",
                "evidence_ids": evidence(8),
            },
            {
                "region": "lower-left preparation of 2q and right-column preparations of 2r–2s",
                "finding": "Detailed batches for 2q, 2r, and 2s were merged into Table 4 entries 18–20 with exact charges, product masses, chromatography, and isolated yields.",
                "evidence_ids": evidence(8),
            },
        ],
        "record_ids": [rid(f"table4_entry{entry}") for entry in range(16, 21)],
        "unresolved": [
            "For 2s, 28.5 mg CuI, 0.20 mmol CuI, and the 15 mol% Table 4 loading are mutually inconsistent; all printed values are preserved.",
            "The 2s characterization continues at the top of page 9.",
        ],
    },
    {
        "page": 9,
        "state": "attempted",
        "regions": [
            {
                "region": "top-left continuation of 2s characterization",
                "finding": "The continuation was linked to Table 4 entry 20 and was not treated as another batch.",
                "evidence_ids": evidence(9),
            },
            {
                "region": "left-column preparations of 2t and 2u",
                "finding": "The detailed paraformaldehyde and propanal experiments were merged with the corresponding Scheme 2 records, including exact reagent quantities and purification.",
                "evidence_ids": evidence(9),
            },
            {
                "region": "right-column preparations of 2v and 2w and beginning of 2x",
                "finding": "The isobutanal Scheme 2 experiment and Table 5 entries 1–2 were enriched from their detailed batches; 2x continues on page 10.",
                "evidence_ids": evidence(9),
            },
        ],
        "record_ids": [
            rid("table4_entry20"), rid("scheme2_paraformaldehyde"),
            rid("scheme2_propanal"), rid("scheme2_isobutanal"),
            rid("table5_entry1"), rid("table5_entry2"),
        ],
        "unresolved": [
            "The 2x outcome and characterization continue on page 10.",
            "Candidate structures remain machine-unverified even where the drawn structures are legible.",
        ],
    },
    {
        "page": 10,
        "state": "attempted",
        "regions": [
            {
                "region": "upper-left continuation of 2x and left-column preparations of 2y–2z",
                "finding": "The 2x batch was completed across pages 9–10 and the detailed 2y and 2z batches were merged into Table 5 entries 3–4. The page-10 2z scheme reports 14 h, conflicting with the 12 h Table 5 row; both values were retained.",
                "evidence_ids": evidence(10),
            },
            {
                "region": "middle-right typical procedure for 2aa",
                "finding": "The exact 2aa charges, 15 min heating ramp, 8 h hold, argon operation, workup, purification, product mass, and isolated yield were merged into Table 5 entry 5.",
                "evidence_ids": evidence(10),
            },
            {
                "region": "bottom-right beginning of the 1 g-scale 2a reaction",
                "finding": "The scale-up is the detailed realization of Table 4 entry 2 and was merged into that existing record; the procedure continues on page 11.",
                "evidence_ids": evidence(10),
            },
        ],
        "record_ids": [
            rid("table5_entry2"), rid("table5_entry3"), rid("table5_entry4"),
            rid("table5_entry5"), rid("table4_entry2"),
        ],
        "unresolved": [
            "The 2z reaction-time discrepancy (12 h versus 14 h) is unresolved and explicitly preserved.",
            "The 1 g-scale 2a paragraph continues on page 11.",
        ],
    },
    {
        "page": 11,
        "state": "attempted",
        "regions": [
            {
                "region": "upper-left completion of the 1 g-scale 2a reaction",
                "finding": "Exact scale-up charges, 0.40 M concentration, 20 min heating ramp, 13 h hold, workup, chromatography, 0.9854 g product, and 66% isolated yield were merged into Table 4 entry 2.",
                "evidence_ids": evidence(11),
            },
            {
                "region": "lower-left synthesis of propargylic amine 3a",
                "finding": "A distinct reported experiment was created for the 50 °C, 2.4 h isolation of intermediate 3a in 79% yield, with exact charges and purification.",
                "evidence_ids": evidence(11),
            },
            {
                "region": "upper-right acknowledgments and lower-right references [1]–[5]",
                "finding": "No new experiment is reported in these regions; cited publications were not converted into experiments of this paper.",
                "evidence_ids": evidence(11),
            },
        ],
        "record_ids": [rid("table4_entry2"), rid("preparation_3a")],
        "unresolved": [
            "The detailed 3a paragraph gives no separate SI association; all structures remain unverified machine candidates.",
        ],
    },
    {
        "page": 12,
        "state": "attempted",
        "regions": [
            {
                "region": "full page, references [6]–[15]",
                "finding": "The page contains bibliography and a brief evaluative note about cited microwave work only; it reports no new batch experiment, scheme, table row, or experimental procedure from this paper.",
                "evidence_ids": evidence(12),
            },
        ],
        "record_ids": [],
        "unresolved": [
            "No reaction records were created from reference-list citations because they are prior literature, not experiments of the current paper.",
        ],
    },
]

coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": pages,
}

target = BASE / "coverage" / "pages_0007_0012.json"
target.parent.mkdir(parents=True, exist_ok=True)
target.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

tasks_path = BASE / "tasks.json"
tasks = json.loads(tasks_path.read_text())
for task in tasks:
    if task.get("document_id") == DOC and task.get("evidence_id") in {
        f"{DOC}:page{page}:text" for page in range(7, 13)
    }:
        task["state"] = "attempted"
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({
    "coverage": str(target),
    "pages": [page["page"] for page in pages],
    "regions": sum(len(page["regions"]) for page in pages),
    "attempted_tasks": sum(task.get("state") == "attempted" for task in tasks),
}, ensure_ascii=False))
