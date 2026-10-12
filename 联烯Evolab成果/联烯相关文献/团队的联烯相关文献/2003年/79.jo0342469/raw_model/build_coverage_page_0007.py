#!/usr/bin/env python3
"""Write page-7 visual coverage and mark its extraction task attempted."""
import json
from pathlib import Path


DOC = "doc_70cf3d194c2f126f"
BASE = Path(__file__).resolve().parents[1]
TEXT = f"{DOC}:page7:text"
IMAGE = f"{DOC}:page7:image"


def region(name, finding):
    return {
        "region": name,
        "finding": finding,
        "evidence_ids": [IMAGE, TEXT],
    }


record_ids = [
    f"{DOC}:scheme5_R1n_to_R2n",
    f"{DOC}:table1_entry_01",
    f"{DOC}:table1_entry_02",
    f"{DOC}:table2_entry_12",
    f"{DOC}:table2_entry_13",
    f"{DOC}:table4_entry_01",
    f"{DOC}:scheme8_entry_01",
    f"{DOC}:scheme8_entry_02",
    f"{DOC}:scheme8_entry_03",
    f"{DOC}:authentic_15",
]

ledger = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [{
        "page": 7,
        "state": "attempted",
        "regions": [
            region("top-left continuation of (R)-2n characterization", "Only analytical characterization continues from the page-6 preparation of (R)-2n; the evidence was added to the existing preparation record, not treated as a new reaction."),
            region("left column, typical procedure for 7a", "Detailed quantities, 25 °C/4 h conditions, workup, chromatography, product mass, and 61% isolated yield enrich Table 1 entry 1."),
            region("left column, N-allylation product 8a paragraph", "The detailed 23 h experiment yields 7a (44%) and 8a (17%). It matches Table 1 entry 2 by time/yields but reports THF where the table reports DMA; the conflict is retained in the existing row record."),
            region("left column, compounds 7b-n statement and detailed (S)-7m/(R)-7n preparations", "The 'prepared similarly' sentence adds no independent quantities for 7b-l; detailed experiments for (S)-7m and (R)-7n enrich Table 2 entries 12 and 13 with masses, amounts, solvent volumes, and ee values."),
            region("right upper column, typical procedure for 9a", "Detailed 9a quantities and 91% isolated yield enrich Table 4 entry 1. The 0.27 mmol/1.6 mL detailed scale conflicts with the table footnote's 0.50 mmol/3 mL scale and is preserved unresolved."),
            region("right column, compounds 9b-l prepared similarly", "This is a generic cross-reference to the 9a procedure and does not instantiate new independent experiments or supply compound-specific quantities."),
            region("right middle column, Mechanistic Study items 1-3", "Three separate stoichiometric palladium experiments enrich Scheme 8 entries 1-3 with exact masses, amounts, DMA volumes, combined product masses, yields, and product ratios."),
            region("right lower column, Synthesis of Authentic 15", "A distinct AgNO3/acetone cycloisomerization of 2b affords authentic 15 in 96% isolated yield; a new reported-experiment record was created."),
            region("acknowledgment and Supporting Information statement", "No reaction experiment occurs here. SI is stated to be available online, but no SI file was supplied or explicitly associated, so no SI association was inferred."),
        ],
        "record_ids": record_ids,
        "unresolved": [
            "Table 1 entry 2 reports DMA but the matching detailed experimental paragraph reports THF.",
            "Table 4 gives a shared 0.50 mmol/3 mL scale while the detailed 9a procedure gives 0.27 mmol/1.6 mL.",
            "Table 1 shared equivalents differ from the detailed masses/mmol for entries 1 and 2.",
            "Absolute configurations are reported as tentative, and product/mixture structures were not independently verified.",
            "The source mentions Supporting Information, but none was explicitly provided or associated.",
        ],
    }],
}

out = BASE / "coverage" / "pages_0007_0007.json"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(ledger, ensure_ascii=False, indent=2) + "\n")

tasks_path = BASE / "tasks.json"
tasks = json.loads(tasks_path.read_text())
task = next(t for t in tasks if t["evidence_id"] == TEXT)
task["state"] = "attempted"
task["visual_evidence_id"] = IMAGE
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"coverage": str(out), "record_ids": len(record_ids), "task": task["state"]}, ensure_ascii=False))
