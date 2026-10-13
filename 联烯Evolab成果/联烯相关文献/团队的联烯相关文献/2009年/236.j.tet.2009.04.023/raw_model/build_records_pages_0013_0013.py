import copy
import json
from pathlib import Path


DOC = "doc_34a38cb1c5b4d3e7"
BASE = Path(__file__).resolve().parents[1]
DATA = json.loads((BASE / "dataset.json").read_text())
EXISTING = {record["record_id"]: record for record in DATA["experiments"]}
EVIDENCE = [f"{DOC}:page13:text", f"{DOC}:page13:image"]


def enrich(record_id, note):
    record = copy.deepcopy(EXISTING[record_id])
    for evidence_id in EVIDENCE:
        if evidence_id not in record["evidence_ids"]:
            record["evidence_ids"].append(evidence_id)
    if not any(item.get("value") == note for item in record["notes"]):
        record["notes"].append(
            {
                "value": note,
                "evidence_ids": EVIDENCE,
                "verification": "unreviewed",
            }
        )
    record["status"] = "candidate"
    record["completeness"] = "partial"
    record["review"] = {
        "method": "none",
        "reviewer": None,
        "checked_fields": [],
        "unresolved": list(record["review"].get("unresolved", [])),
    }
    return record


records = [
    enrich(
        f"{DOC}:table2_entry2_2b",
        "Reference note 22 reports single-crystal X-ray data for (E)-2b and CCDC deposition 702217; this is analytical support for the reported assignment, not a separate reaction experiment.",
    ),
    enrich(
        f"{DOC}:scheme2_S-1b_to_S-E-2b",
        "Reference note 27 reports single-crystal X-ray data for S-E-(+)-2b and CCDC deposition 702218; this is analytical support for the reported absolute assignment, not a separate reaction experiment.",
    ),
]

assert len(records) == 2
assert len({record["record_id"] for record in records}) == 2

out = BASE / "raw_model" / "records_pages_0013_0013.json"
out.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"updated_records": 2, "new_record_ids": 0, "path": str(out)}, ensure_ascii=False))
