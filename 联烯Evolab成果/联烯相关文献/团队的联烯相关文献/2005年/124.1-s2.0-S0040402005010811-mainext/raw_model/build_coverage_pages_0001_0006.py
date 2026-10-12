#!/usr/bin/env python3
"""Write the page 1-6 visual coverage ledger and mark only those page tasks attempted."""
from __future__ import annotations

import json
from pathlib import Path


DOC = "doc_b62df268eae80c99"
BASE = Path(__file__).resolve().parents[1]
DATASET = BASE / "dataset.json"
TASKS = BASE / "tasks.json"
OUT = BASE / "coverage" / "pages_0001_0006.json"


def evidence(page: int) -> list[str]:
    return [f"{DOC}:page{page}:image", f"{DOC}:page{page}:text"]


regions = {
    1: [
        {
            "region": "title, abstract, and two-column discussion text",
            "finding": "Article context and prose describing the current Pd/CuCl2 cyclization and control observations; no additional independent arrow beyond the two schemes on this page.",
            "evidence_ids": evidence(1),
        },
        {
            "region": "Scheme 1, lower-left column",
            "finding": "Generic prior-work alpha-allenoic-acid coupling/cyclization with R groups; classified as literature_example, not a current-paper reported experiment.",
            "evidence_ids": evidence(1),
        },
        {
            "region": "Scheme 2, lower-right column",
            "finding": "Current-paper exploratory reaction of 1a and PhI giving products 2a (24%) and 3a (11%); merged with the detailed page-4 procedure rather than duplicated.",
            "evidence_ids": evidence(1),
        },
    ],
    2: [
        {
            "region": "Table 1 reaction header, rows 1-16, and footnotes a-g",
            "finding": "Sixteen distinct optimization experiments were read row-by-row, including upper-bound impure yields, the qualitative complicated result, air/O2/H2O exceptions, absent catalyst/base controls, and modified K2CO3 loadings.",
            "evidence_ids": evidence(2),
        },
        {
            "region": "Table 2 reaction scheme, rows 1-11, and NMR-yield footnote",
            "finding": "Eleven substrate-scope cyclizations 1a-1k to 3a-3k were identified and linked to their matching detailed experiments on pages 4-5; 3k is explicitly a 31% NMR yield.",
            "evidence_ids": evidence(2),
        },
        {
            "region": "mechanistic discussion above Experimental",
            "finding": "Proposed endo anti-oxypalladation/syn beta-H elimination cycle; classified as mechanism and linked to Scheme 3 on page 3.",
            "evidence_ids": evidence(2),
        },
        {
            "region": "Section 3.1 Conditions A opening at lower right",
            "finding": "General hydrolysis conditions begin here and continue on page 3; applied as shared evidence without copying nominal solvent volumes to differently scaled examples.",
            "evidence_ids": evidence(2),
        },
    ],
    3: [
        {
            "region": "Scheme 3, upper half",
            "finding": "Proposed Pd catalytic cycle with generic species 1, 4, and 3; retained as a mechanism rather than a reported experiment.",
            "evidence_ids": evidence(3),
        },
        {
            "region": "Conditions A continuation and Conditions B, middle-left",
            "finding": "Shared workup/purification for hydrolyses and the acid-mediated Conditions B were captured; nominal general-procedure liquid volumes remain distinct from specific example scales.",
            "evidence_ids": evidence(3),
        },
        {
            "region": "Sections 3.1.1-3.1.4 across both columns",
            "finding": "Four individual ester hydrolyses producing 1a-1d with explicit ester/LiOH amounts, product masses, and yields were recorded separately.",
            "evidence_ids": evidence(3),
        },
    ],
    4: [
        {
            "region": "Sections 3.1.5-3.1.11 across both columns",
            "finding": "Seven individual preparations of 1e-1k were recorded separately; 1e-1i use Conditions A and 1j-1k use Conditions B.",
            "evidence_ids": evidence(4),
        },
        {
            "region": "paragraph after Section 3.1.11 and Section 3.1.12",
            "finding": "Detailed counterpart of Scheme 2: one reaction gives 2a and 3a and is followed by 2a characterization. Printed mmol values conflict with printed masses/loadings and were preserved with an unresolved warning rather than corrected.",
            "evidence_ids": evidence(4),
        },
        {
            "region": "Section 3.2 general procedure and Section 3.2.1",
            "finding": "Shared N2/DMF/70 C/12 h workup plus the detailed 1a-to-3a experiment. The page-8 corrigendum is used as necessary context to replace the section's printed Pd(PPh3)4 with PdCl2(PPh3)2.",
            "evidence_ids": evidence(4),
        },
    ],
    5: [
        {
            "region": "Sections 3.2.2-3.2.11 across both columns",
            "finding": "Ten detailed cyclizations 1b-1k to 3b-3k with explicit substrate/CuCl2/K2CO3 quantities, conditions, yields, and product masses where reported; linked to Table 2 rather than duplicated.",
            "evidence_ids": evidence(5),
        },
        {
            "region": "Section 3.2.11 at lower right",
            "finding": "3k has a 31% NMR yield using p-methoxyiodobenzene as internal standard; product mass is not reported.",
            "evidence_ids": evidence(5),
        },
    ],
    6: [
        {
            "region": "References and notes 1-12, both columns",
            "finding": "Bibliography only; no current-paper reaction arrow, experimental procedure, optimization row, or new reported outcome occurs on this page.",
            "evidence_ids": evidence(6),
        },
    ],
}


unresolved = {
    1: ["Scheme 1 uses generic R groups and omits experimental detail.", "Scheme 2 scale/atmosphere are supplied only partly by its page-4 counterpart."],
    2: ["Table 1 omits reaction scale, workup, purification, and yield basis.", "Atmosphere is not explicitly assigned to most Table 1 rows.", "Table 2 structures remain unverified machine candidates."],
    3: ["General-procedure nominal solvent volumes cannot be assigned exactly to differently scaled examples.", "Generic mechanistic structures are not fully specified."],
    4: ["Printed 1a and PhI mmol values in the exploratory reaction are internally inconsistent with the printed masses and catalyst/equivalent values.", "No supporting information was explicitly associated."],
    5: ["The printed catalyst identity in Sections 3.2.2-3.2.11 requires the page-8 corrigendum.", "3k product mass/isolation is missing; all structures remain unverified."],
    6: ["References were not expanded into experiments because they are cited prior literature, not experimental reports in this source."],
}


data = json.loads(DATASET.read_text())
page_rows = []
for page in range(1, 7):
    page_evidence = set(evidence(page))
    record_ids = sorted(
        rec["record_id"] for rec in data["experiments"]
        if page_evidence.intersection(rec.get("evidence_ids", []))
    )
    page_rows.append({
        "page": page,
        "state": "attempted",
        "regions": regions[page],
        "record_ids": record_ids,
        "unresolved": unresolved[page],
    })

coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": page_rows,
}
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

tasks = json.loads(TASKS.read_text())
for task in tasks:
    if task.get("document_id") == DOC and task.get("evidence_id") in {f"{DOC}:page{p}:text" for p in range(1, 7)}:
        task["state"] = "attempted"
        task["reason"] = "Original rendered page image visually inspected; regions and linked records are documented in coverage/pages_0001_0006.json."
TASKS.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"output": str(OUT), "pages": [row["page"] for row in page_rows],
                  "page_record_counts": {str(row["page"]): len(row["record_ids"]) for row in page_rows}}, ensure_ascii=False))
