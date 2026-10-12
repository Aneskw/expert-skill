#!/usr/bin/env python3
"""Attach page-7 analytical evidence to the existing 4a/6a experiment."""

import copy
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / "runs/current"
DOC = "doc_6b8369a38afea515"
RECORD_ID = f"{DOC}:table1_entry06"
PAGE7 = [f"{DOC}:page7:text", f"{DOC}:page7:image"]


def fact(value, evidence_ids):
    return {
        "value": value,
        "evidence_ids": list(evidence_ids),
        "verification": "unreviewed",
    }


dataset = json.loads((RUN / "dataset.json").read_text())
source = next(
    record for record in dataset["experiments"] if record["record_id"] == RECORD_ID
)
record = copy.deepcopy(source)
record["status"] = "candidate"
record["review"]["method"] = "none"
record["review"]["reviewer"] = None
record["review"]["checked_fields"] = []

for evidence_id in PAGE7:
    if evidence_id not in record["evidence_ids"]:
        record["evidence_ids"].append(evidence_id)

record["notes"].extend(
    [
        fact(
            "Page 7 continues the analytical characterization of 4a with the end "
            "of the 13C NMR list, MS m/z 298 (M+, 0.47) and 181 (100), and HRMS "
            "calculated/found values 298.17802/298.18169.",
            PAGE7,
        ),
        fact(
            "Product 6a is reported as a yellow oil and characterized by 1H NMR, "
            "MS, IR, and elemental analysis; this is analytical support for the "
            "existing experiment, not a separate reaction.",
            PAGE7,
        ),
    ]
)
record["review"]["unresolved"] = [
    item
    for item in record["review"]["unresolved"]
    if item
    != "Analytical characterization continues onto page 7, outside this session's visual coverage."
]

output = RUN / "raw_model/extracted_records_pages_0007_0007.json"
output.write_text(json.dumps([record], ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"records": 1, "record_ids": [RECORD_ID], "output": str(output)}))
