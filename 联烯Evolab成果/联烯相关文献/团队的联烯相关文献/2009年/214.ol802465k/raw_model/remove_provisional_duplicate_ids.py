#!/usr/bin/env python3
"""Remove two provisional machine-only IDs superseded by a cross-table merged record."""

import json
from datetime import datetime, timezone
from pathlib import Path


dataset_path = Path(__file__).resolve().parents[1] / "dataset.json"
data = json.loads(dataset_path.read_text())
obsolete = {
    "doc_18cc74d3b2732035:table1_entry9",
    "doc_18cc74d3b2732035:table2_entry1_3aa",
}
matched = [r for r in data["experiments"] if r["record_id"] in obsolete]
if {r["record_id"] for r in matched} != obsolete:
    raise SystemExit("Expected both provisional IDs before cleanup")
if any(r["status"] != "needs_review" or r["review"]["method"] != "model" for r in matched):
    raise SystemExit("Refusing to remove a record that is not a machine-only provisional record")
data["experiments"] = [r for r in data["experiments"] if r["record_id"] not in obsolete]
data["run_log"].append({
    "event": "provisional_duplicate_records_removed",
    "record_ids": sorted(obsolete),
    "replacement_record_id": "doc_18cc74d3b2732035:table1_entry9_table2_entry1_3aa",
    "at": datetime.now(timezone.utc).isoformat(),
})
tmp = dataset_path.with_name(dataset_path.name + ".tmp")
tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False))
tmp.replace(dataset_path)
print(json.dumps({"removed": sorted(obsolete), "remaining": len(data["experiments"])}, ensure_ascii=False))
