#!/usr/bin/env python3
"""Write page-7 coverage, update its task, and snapshot validation/audit."""

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / "runs/current"
DOC = "doc_6b8369a38afea515"
RECORD_ID = f"{DOC}:table1_entry06"
PAGE7 = [f"{DOC}:page7:text", f"{DOC}:page7:image"]


coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 7,
            "state": "attempted",
            "regions": [
                {
                    "region": "upper-left analytical-data continuation",
                    "finding": (
                        "Continuation of the page-6 characterization for products 4a and 6a "
                        "(13C NMR tail/HRMS for 4a; physical description, 1H NMR, MS, IR, "
                        "and elemental analysis for 6a). It supports the existing Table 1 "
                        "entry 6 record and is not a new reaction experiment."
                    ),
                    "evidence_ids": PAGE7,
                },
                {
                    "region": "upper-left/lower continuation acknowledgment",
                    "finding": (
                        "Funding acknowledgment and award statement; no reaction, condition, "
                        "yield, arrow, figure, table, or experimental procedure."
                    ),
                    "evidence_ids": PAGE7,
                },
                {
                    "region": "upper-right Supporting Information notice",
                    "finding": (
                        "The article states that analytical data and NMR spectra are available "
                        "as Supporting Information, but no SI file was supplied or explicitly "
                        "associated in this workspace."
                    ),
                    "evidence_ids": PAGE7,
                },
            ],
            "record_ids": [RECORD_ID],
            "unresolved": [
                "The page begins mid-list in the 13C NMR data for 4a, so complete peak assignments cannot be reconstructed from page 7 alone.",
                "The Supporting Information availability notice does not establish an SI association; no SI file was supplied.",
                "No new reaction conditions, reaction yield, or separate experiment are present on page 7.",
            ],
        }
    ],
}

dataset_path = RUN / "dataset.json"
dataset = json.loads(dataset_path.read_text())
known = {record["record_id"] for record in dataset["experiments"]}
if RECORD_ID not in known:
    raise SystemExit(f"coverage refers to missing record: {RECORD_ID}")

document = next(doc for doc in dataset["documents"] if doc["document_id"] == DOC)
evidence = {item["evidence_id"] for item in document["evidence"]}
if any(evidence_id not in evidence for evidence_id in PAGE7):
    raise SystemExit("page-7 source evidence is missing from the dataset")

(RUN / "coverage").mkdir(exist_ok=True)
(RUN / "coverage/pages_0007_0007.json").write_text(
    json.dumps(coverage, ensure_ascii=False, indent=2) + "\n"
)

tasks_path = RUN / "tasks.json"
tasks = json.loads(tasks_path.read_text())
task = next(item for item in tasks if item["task_id"] == f"{DOC}:page7:text")
task["state"] = "attempted"
task["visual_evidence_id"] = f"{DOC}:page7:image"
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

tool_path = ROOT / "skills/chemical-reaction-extraction/scripts/reaction_tools.py"
spec = importlib.util.spec_from_file_location("reaction_tools", tool_path)
reaction_tools = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reaction_tools)

errors = reaction_tools.validate(
    dataset,
    RUN,
    strict_record_ids={record["record_id"] for record in dataset["experiments"]},
)
validation = {"valid": not errors, "errors": errors}
(RUN / "raw_model/validate_strict_pages_0007_0007.json").write_text(
    json.dumps(validation, ensure_ascii=False, indent=2) + "\n"
)

audit = {
    "tool_version": reaction_tools.VERSION,
    "chemical_accuracy_verified": False,
    "warnings": [
        {"record_id": record["record_id"], "warnings": warnings}
        for record in dataset["experiments"]
        if (warnings := reaction_tools.warnings(record))
    ],
}
(RUN / "raw_model/audit_pages_0007_0007.json").write_text(
    json.dumps(audit, ensure_ascii=False, indent=2) + "\n"
)

if errors:
    raise SystemExit(json.dumps(validation, ensure_ascii=False))

print(
    json.dumps(
        {
            "coverage_pages": [7],
            "coverage_record_references": 1,
            "tasks_attempted": sum(item["state"] == "attempted" for item in tasks),
            "validation": validation,
            "audit_warning_count": len(audit["warnings"]),
        },
        ensure_ascii=False,
    )
)
