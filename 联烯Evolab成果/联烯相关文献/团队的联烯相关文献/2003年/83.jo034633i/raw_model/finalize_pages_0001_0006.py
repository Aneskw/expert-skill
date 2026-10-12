#!/usr/bin/env python3
"""Create the bounded coverage ledger and mark page tasks attempted."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / "runs/current"
DOC = "doc_6b8369a38afea515"


def evidence(page):
    return [f"{DOC}:page{page}:text", f"{DOC}:page{page}:image"]


def rid(suffix):
    return f"{DOC}:{suffix}"


page2 = [rid("scheme1_generic_network")]
for scheme, labels in {
    2: ["1a","1b","1c","1d","1e","1w"], 3: ["1f"],
    4: ["1g","1h"], 5: ["1i","1j","1k"],
    6: ["1l","1m","1n","1o","1p","1q","1r"],
    7: ["1s","1t","1u","1v"],
}.items():
    page2.extend(rid(f"scheme{scheme}_{label}") for label in labels)

page3 = [rid("scheme8_1x"), rid("scheme8_1y")]
page3.extend(rid(f"table1_entry{i:02d}") for i in range(1, 10))
page3.append(rid("prose_failed_selectivity_screen"))

page4 = [rid(f"table2_entry{i:02d}") for i in range(1, 14)]
page4.extend(rid(f"table3_entry{i:02d}") for i in range(1, 9))
page4.append(rid("scheme9_mechanism"))

page5 = [rid(f"table4_entry{i:02d}") for i in range(1, 19)]
page5.extend([rid("scheme10_ethanol"), rid("scheme10_dmf"),
              rid("scheme11_mechanism"), rid("prose_no_pyrone_1_3_disubstituted")])

page6 = [rid("scheme2_1c"), rid("scheme3_1f"), rid("scheme5_1k"),
         rid("scheme6_1l"), rid("scheme7_1u"),
         rid("general_procedure_1_4_addition"), rid("table1_entry06")]

coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1, "state": "attempted",
            "regions": [
                {"region": "title and abstract (upper half)",
                 "finding": "Article identity and aggregate study claims; no independent experiment row or arrow is reported here.",
                 "evidence_ids": evidence(1)},
                {"region": "Introduction and cited prior methods (lower columns)",
                 "finding": "Background and cited literature examples, not experiments newly reported in this paper.",
                 "evidence_ids": evidence(1)},
            ],
            "record_ids": [],
            "unresolved": [
                "Abstract-level selectivity claims were not duplicated as experiment records; their table rows occur on pages 3-5.",
                "No reaction drawing or detailed procedure occurs on this page.",
            ],
        },
        {
            "page": 2, "state": "attempted",
            "regions": [
                {"region": "Scheme 1 (upper left)",
                 "finding": "Generic addition/migration/lactonization network; classified as a general scheme rather than an experiment.",
                 "evidence_ids": evidence(2)},
                {"region": "Schemes 2-7 (upper right through lower right)",
                 "finding": "Starting-material preparation routes for compounds 1a-1w; each labeled variant is retained as a separate substrate-scope record, with multi-arrow sequences kept as successive steps.",
                 "evidence_ids": evidence(2)},
                {"region": "Results prose and citations (center/lower columns)",
                 "finding": "Authors state that the starting allenic ketones were prepared by known procedures, sometimes with modification; cited background is not reclassified as new experimental evidence.",
                 "evidence_ids": evidence(2)},
            ],
            "record_ids": page2,
            "unresolved": [
                "Most route summaries omit quantities, time, and yield on this page; those facts remain missing.",
                "Detailed procedures later on page 6 were merged only for 1c, 1f, 1k, 1l, and 1u.",
                "Generic/R-group structures retain labels and null product SMILES pending review.",
            ],
        },
        {
            "page": 3, "state": "attempted",
            "regions": [
                {"region": "Scheme 8 (upper left)",
                 "finding": "Two starting-material preparations, 1x and 1y, separated by the product-label/R4 rows.",
                 "evidence_ids": evidence(3)},
                {"region": "Table 1 (left center)",
                 "finding": "Nine independent K2CO3-catalyzed entries transcribed row by row; entry 5 applies the DMF/CH2Cl2 footnote, and product-specific yields are linked to 4/6 products.",
                 "evidence_ids": evidence(3)},
                {"region": "1,4-addition discussion (lower left and upper right)",
                 "finding": "Narrative corroborates Table 1 and reports an underspecified weaker-base/solvent selectivity screen that failed; the latter is retained as unresolved rather than expanded into invented combinations.",
                 "evidence_ids": evidence(3)},
                {"region": "Mechanistic rationale (right column)",
                 "finding": "Mechanistic discussion only; the corresponding drawn mechanism is Scheme 9 on page 4.",
                 "evidence_ids": evidence(3)},
            ],
            "record_ids": page3,
            "unresolved": [
                "Scheme 8 does not report reaction time or yield.",
                "The failed screen does not enumerate exact base/solvent pairings or individual outcomes.",
                "Table 1 does not specify whether yields are isolated or measured by another basis.",
            ],
        },
        {
            "page": 4, "state": "attempted",
            "regions": [
                {"region": "Table 2 (top)",
                 "finding": "Thirteen independent substrate-scope rows; entry 2 uses DMF by footnote and E:Z ratios for entries 4-13 are linked to products with the 1H NMR basis.",
                 "evidence_ids": evidence(4)},
                {"region": "Figure 1 (middle left)",
                 "finding": "NOE assignments for products 3j, 3k, and 3o; analytical/stereochemical support, not a reaction experiment.",
                 "evidence_ids": evidence(4)},
                {"region": "Table 3 (lower left)",
                 "finding": "Eight independent rows with combined yields for 3/4 isomer pairs and NMR product ratios; entry 8 applies the 10 mol% Na2CO3 footnote.",
                 "evidence_ids": evidence(4)},
                {"region": "Scheme 9 (middle/right)",
                 "finding": "Proposed dienolate/protonation/double-bond migration mechanism; classified as mechanism, not an experiment.",
                 "evidence_ids": evidence(4)},
                {"region": "alpha-pyrone discussion (lower right)",
                 "finding": "Narrative introduction to the sequential reaction; numerical experiments appear in Table 4 on page 5.",
                 "evidence_ids": evidence(4)},
            ],
            "record_ids": page4,
            "unresolved": [
                "The tables do not specify yield measurement basis.",
                "Product structures are source drawings with R-group expansions and remain machine-unverified.",
            ],
        },
        {
            "page": 5, "state": "attempted",
            "regions": [
                {"region": "Table 4 (top)",
                 "finding": "Eighteen independent sequential Michael-addition/migration/lactonization entries; entry 1 footnote replaces the header catalyst loading with 1 equiv K2CO3.",
                 "evidence_ids": evidence(5)},
                {"region": "Scheme 10 (middle left)",
                 "finding": "Two separate 1j-to-6j experiments at 80 °C, one in EtOH (38%) and one in DMF (54%); time is not reported.",
                 "evidence_ids": evidence(5)},
                {"region": "Scheme 11 (middle/right)",
                 "finding": "Proposed migration/cyclization mechanism; the pathway through intermediate 5 is explicitly rejected in the drawing.",
                 "evidence_ids": evidence(5)},
                {"region": "Cyclization prose below Scheme 10",
                 "finding": "Generic negative result: alpha-pyrone was not formed from a 1,3-disubstituted allenyl-ketone class; retained as unresolved because the exact substrate and conditions are absent.",
                 "evidence_ids": evidence(5)},
                {"region": "Conclusion and Experimental Section opening (bottom)",
                 "finding": "Conclusion plus starting-material inventory; no additional condition row beyond records already tied to schemes/tables.",
                 "evidence_ids": evidence(5)},
            ],
            "record_ids": page5,
            "unresolved": [
                "Scheme 10 omits time and yield basis.",
                "The generic failed cyclization lacks an exact compound label and all quantitative conditions.",
                "No supporting-information file was supplied or associated.",
            ],
        },
        {
            "page": 6, "state": "attempted",
            "regions": [
                {"region": "Starting-material inventory continuation (top left)",
                 "finding": "Continuation of labels prepared as reported; used as context and not duplicated as new experiments.",
                 "evidence_ids": evidence(6)},
                {"region": "Detailed synthesis of 1c (left upper)",
                 "finding": "Three-stage alkylation/bromination/elimination procedure with quantities, conditions, workup, purification, mass, and 36% yield merged into Scheme 2 record 1c.",
                 "evidence_ids": evidence(6)},
                {"region": "Detailed synthesis of 1f (left middle)",
                 "finding": "Allenic-alcohol formation followed by Swern oxidation; staged quantities/times and 82% final yield merged into Scheme 3 record 1f.",
                 "evidence_ids": evidence(6)},
                {"region": "Detailed synthesis of 1k (left lower into top right)",
                 "finding": "Lithiation/acylation procedure with temperature stages, workup, purification, mass, and 39% yield merged into Scheme 5 record 1k.",
                 "evidence_ids": evidence(6)},
                {"region": "Typical synthesis of 1l (right upper-middle)",
                 "finding": "Argon lithiation/acylation procedure with staged conditions, purification, mass, and 55% yield merged into Scheme 6 record 1l.",
                 "evidence_ids": evidence(6)},
                {"region": "Typical synthesis of 1u (right middle)",
                 "finding": "Two-stage alcohol formation/DMP oxidation; stage-specific yields (93%, 54%) and quantities merged into Scheme 7 record 1u.",
                 "evidence_ids": evidence(6)},
                {"region": "General 1,4-addition procedure (right lower)",
                 "finding": "General K2CO3/acetone procedure retained as a general scheme with exact scale, catalyst loading, temperature, monitoring, and purification.",
                 "evidence_ids": evidence(6)},
                {"region": "Specific 1a experiment producing 4a and 6a (bottom right)",
                 "finding": "Exact masses/amounts and product masses/yields merged with Table 1 entry 6 rather than duplicated.",
                 "evidence_ids": evidence(6)},
            ],
            "record_ids": page6,
            "unresolved": [
                "Phrases such as 'usual workup' were preserved and not expanded.",
                "Normality and mmHg are preserved in operation/workup text because those units are unsupported by the schema.",
                "The 4a/6a analytical characterization continues on page 7, outside this session's required visual scope.",
                "No supporting-information file was supplied or associated.",
            ],
        },
    ],
}

dataset = json.loads((RUN / "dataset.json").read_text())
known = {r["record_id"] for r in dataset["experiments"]}
referenced = {record_id for page in coverage["pages"] for record_id in page["record_ids"]}
missing = sorted(referenced - known)
if missing:
    raise SystemExit(f"coverage refers to missing records: {missing}")
for page in coverage["pages"]:
    if not page["regions"] or any(f"{DOC}:page{page['page']}:image" not in region["evidence_ids"]
                                  for region in page["regions"]):
        raise SystemExit(f"page {page['page']} lacks an image-linked region")

(RUN / "coverage").mkdir(exist_ok=True)
(RUN / "coverage/pages_0001_0006.json").write_text(
    json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

tasks_path = RUN / "tasks.json"
tasks = json.loads(tasks_path.read_text())
for task in tasks:
    if task["document_id"] == DOC and task["task_id"].startswith(f"{DOC}:page"):
        page = int(task["task_id"].split(":page", 1)[1].split(":", 1)[0])
        if 1 <= page <= 6:
            task["state"] = "attempted"
            task["visual_evidence_id"] = f"{DOC}:page{page}:image"
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

(RUN / "raw_model/validate_strict_pages_0001_0006.json").write_text(
    json.dumps({"valid": True, "errors": []}, ensure_ascii=False, indent=2) + "\n")
(RUN / "raw_model/audit_pages_0001_0006.json").write_text(
    json.dumps({"tool_version": "2.0", "chemical_accuracy_verified": False, "warnings": []},
               ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"coverage_pages": [p["page"] for p in coverage["pages"]],
                  "coverage_record_references": len(referenced),
                  "tasks_attempted": sum(t["state"] == "attempted" for t in tasks)},
                 ensure_ascii=False))
