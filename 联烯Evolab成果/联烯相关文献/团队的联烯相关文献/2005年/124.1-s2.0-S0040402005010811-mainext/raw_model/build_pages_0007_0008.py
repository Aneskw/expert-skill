#!/usr/bin/env python3
"""Build page 7-8 corrigendum evidence updates and the visual coverage ledger."""
from __future__ import annotations

import copy
import json
from pathlib import Path


DOC = "doc_b62df268eae80c99"
BASE = Path(__file__).resolve().parents[1]
DATASET = BASE / "dataset.json"
TASKS = BASE / "tasks.json"
RECORDS_OUT = Path(__file__).with_name("extracted_records_pages_0007_0008.json")
COVERAGE_OUT = BASE / "coverage" / "pages_0007_0008.json"
PAGE8_TEXT = f"{DOC}:page8:text"
PAGE8_IMAGE = f"{DOC}:page8:image"


def walk(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)


data = json.loads(DATASET.read_text())
record_prefix = f"{DOC}:table2_cyclization_"
updated_records = []
for source_record in data["experiments"]:
    if not source_record["record_id"].startswith(record_prefix):
        continue
    record = copy.deepcopy(source_record)
    if PAGE8_TEXT not in record.get("evidence_ids", []):
        continue
    if PAGE8_IMAGE not in record["evidence_ids"]:
        record["evidence_ids"].append(PAGE8_IMAGE)
    # The image is direct visual evidence for every fact that already relies on
    # the corrigendum text. Do not broaden it to unrelated quantities/outcomes.
    for obj in walk(record):
        evidence_ids = obj.get("evidence_ids")
        if isinstance(evidence_ids, list) and PAGE8_TEXT in evidence_ids and PAGE8_IMAGE not in evidence_ids:
            evidence_ids.append(PAGE8_IMAGE)
    updated_records.append(record)

updated_records.sort(key=lambda row: row["record_id"])
if len(updated_records) != 11:
    raise RuntimeError(f"Expected 11 corrigendum-linked records, found {len(updated_records)}")

RECORDS_OUT.write_text(json.dumps(updated_records, ensure_ascii=False, indent=2) + "\n")

record_ids = [row["record_id"] for row in updated_records]
coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 7,
            "state": "attempted",
            "regions": [
                {
                    "region": "central Update panel and DOI link",
                    "finding": "Bibliographic update cover pointing to Tetrahedron 63 (2007) 783 and DOI 10.1016/j.tet.2006.11.009; no molecule drawing, reaction arrow, table, footnote, experimental condition, or outcome appears on this page.",
                    "evidence_ids": [f"{DOC}:page7:image", f"{DOC}:page7:text"],
                }
            ],
            "record_ids": [],
            "unresolved": [
                "The cover page alone does not state the chemical correction; its linked corrigendum is on PDF page 8."
            ],
        },
        {
            "page": 8,
            "state": "attempted",
            "regions": [
                {
                    "region": "corrigendum title and article-identification block",
                    "finding": "Corrigendum to the 2005 article; bibliographic identification only, with no new reaction scheme, table, or independently performed experiment.",
                    "evidence_ids": [f"{DOC}:page8:image", f"{DOC}:page8:text"],
                },
                {
                    "region": "single correction sentence beneath the horizontal rule",
                    "finding": "Sections 3.2.1-3.2.11 must read PdCl2(PPh3)2 instead of the printed Pd(PPh3)4. This corrects the catalyst identity in eleven existing cyclization records and is not a new experiment.",
                    "evidence_ids": [f"{DOC}:page8:image", f"{DOC}:page8:text"],
                },
                {
                    "region": "apology, original-article DOI, author contact, and footer",
                    "finding": "Administrative/bibliographic text only; no additional reagent amount, reaction condition, yield, selectivity, workup, or purification is supplied.",
                    "evidence_ids": [f"{DOC}:page8:image", f"{DOC}:page8:text"],
                },
            ],
            "record_ids": record_ids,
            "unresolved": [
                "The corrigendum changes only catalyst identity and does not resolve other missing experimental details or verify candidate structures.",
                "Supporting-information association remains unestablished."
            ],
        },
    ],
}
COVERAGE_OUT.parent.mkdir(parents=True, exist_ok=True)
COVERAGE_OUT.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

tasks = json.loads(TASKS.read_text())
target_tasks = {f"{DOC}:page7:text", f"{DOC}:page8:text"}
updated_task_count = 0
for task in tasks:
    if task.get("document_id") == DOC and task.get("evidence_id") in target_tasks:
        task["state"] = "attempted"
        task["reason"] = (
            "Original rendered page image visually inspected; page-specific findings and linked "
            "records are documented in coverage/pages_0007_0008.json."
        )
        updated_task_count += 1
if updated_task_count != 2:
    raise RuntimeError(f"Expected to update 2 page tasks, updated {updated_task_count}")
TASKS.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({
    "records_updated": len(updated_records),
    "new_records": 0,
    "coverage_pages": [7, 8],
    "tasks_updated": updated_task_count,
    "records_output": str(RECORDS_OUT),
    "coverage_output": str(COVERAGE_OUT),
}, ensure_ascii=False))
