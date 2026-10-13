import json
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
DATASET = json.loads((BASE / "dataset.json").read_text())
DOC = "doc_1e29b02f2fac50bb"


def evidence(page):
    return [f"{DOC}:page{page}:image", f"{DOC}:page{page}:text"]


def page_records(page):
    marker = f"{DOC}:page{page}:"
    return [r["record_id"] for r in DATASET["experiments"]
            if any(e.startswith(marker) for e in r["evidence_ids"])]


regions = {
    1: [
        {"region": "lower-left Scheme 1 and adjacent introduction",
         "finding": "The current CuI/di(n-alkyl)amine transformation was classified as a generic scheme; two arrows explicitly labeled as previous reports were retained as literature examples rather than experiments of this paper.",
         "evidence_ids": evidence(1)},
        {"region": "lower-right opening Results and Discussion and Figure 1",
         "finding": "Nine separately depicted amines/cyclic urea were treated as distinct qualitative screening trials that failed to promote the Table 1 reaction within 11 h; no numerical yields are assigned.",
         "evidence_ids": evidence(1)},
    ],
    2: [
        {"region": "upper-left Table 1 including footnotes and reaction header",
         "finding": "Six amine-effect optimization rows were extracted independently with time, NMR yield, CH2Br2 measurement basis, and the entry-1 recovery footnote.",
         "evidence_ids": evidence(2)},
        {"region": "upper-right Table 2 including footnotes and reaction header",
         "finding": "Eleven catalyst-screen rows were extracted independently with product-specific NMR yields for 2a and 3a; table dashes were preserved, and the entry-11 1a recovery was kept separate from product yield.",
         "evidence_ids": evidence(2)},
        {"region": "lower-right Table 3 including footnote and reaction header",
         "finding": "Seven solvent-screen rows were extracted independently, preserving <2%, 'complicated', and table-dash results without conversion to zero.",
         "evidence_ids": evidence(2)},
        {"region": "lower-left and lower-right discussion prose",
         "finding": "Narrative optimization conclusions were used as context only; they were not duplicated as additional experiments beyond Tables 1-3.",
         "evidence_ids": evidence(2)},
    ],
    3: [
        {"region": "upper-left Table 4, header, and footnotes",
         "finding": "Twenty substrate-scope rows were extracted independently, including catalyst-loading overrides, temperatures, times, isolated yields, the R-group footnote, and the 8.0 mmol/20 mL scale-up footnote.",
         "evidence_ids": evidence(3)},
        {"region": "lower-left Scheme 2 and adjacent prose",
         "finding": "The paraformaldehyde, propanal, and isobutanal arrows were extracted as three distinct experiments with their own amines, temperature, time, and isolated yield.",
         "evidence_ids": evidence(3)},
        {"region": "upper-right Equation (1) and explanatory prose",
         "finding": "The mismatched propanal/dibutylamine experiment was extracted once with two product-specific yields (R=Et 43%, R=propyl 12%).",
         "evidence_ids": evidence(3)},
        {"region": "middle-right Table 5 and footnotes",
         "finding": "Five diisobutylamine scope rows were extracted independently; entry 5 uses 20 mol% CuI, and the <5% isobutyral-derived-allene footnote is associated with an explicit unresolved byproduct participant.",
         "evidence_ids": evidence(3)},
        {"region": "lower-right Scheme 3",
         "finding": "The catalytic cycle was classified as a proposed mechanism and not as a batch experiment.",
         "evidence_ids": evidence(3)},
    ],
    4: [
        {"region": "left-column rationale, conclusions, and General section",
         "finding": "The rationale was linked to the Scheme 3 mechanism; conclusions and general reagent-preparation statements were not converted into reaction batches.",
         "evidence_ids": evidence(4)},
        {"region": "lower-left to upper-right typical procedure for 2b",
         "finding": "The detailed 2b batch was merged with Table 4 entry 3, adding exact quantities, argon, sealed-tube heating, TLC endpoint, workup, chromatography, product mass, and isolated yield.",
         "evidence_ids": evidence(4)},
        {"region": "right-column preparation of 2a",
         "finding": "The detailed 2a batch was merged with Table 4 entry 1; the scope row and experimental paragraph were not duplicated.",
         "evidence_ids": evidence(4)},
        {"region": "bottom-right beginning of the 2c paragraph",
         "finding": "The cross-page 2c preparation begins here and was merged with its continuation on page 5 and Table 4 entry 4.",
         "evidence_ids": evidence(4)},
    ],
    5: [
        {"region": "upper-left continuation and completion of 2c",
         "finding": "Exact quantities, product mass, chromatography eluents, and 68% isolated yield were merged into Table 4 entry 4.",
         "evidence_ids": evidence(5)},
        {"region": "left-column preparation of 2d",
         "finding": "The detailed 2d batch was merged into Table 4 entry 5 with exact quantities, product mass, and 74% isolated yield.",
         "evidence_ids": evidence(5)},
        {"region": "upper-right preparation of 2e",
         "finding": "The detailed 2e batch was merged into Table 4 entry 6 with exact quantities, 36 h at 130 °C, product mass, and 60% isolated yield.",
         "evidence_ids": evidence(5)},
        {"region": "lower-right preparation of 2f",
         "finding": "The detailed 2f batch was merged into Table 4 entry 7 with exact quantities, 18 h at 150 °C, product mass, and 60% isolated yield.",
         "evidence_ids": evidence(5)},
    ],
    6: [
        {"region": "upper-left preparation of 2g",
         "finding": "The detailed 2g batch was merged into Table 4 entry 8 with exact quantities, 16 h at 150 °C, product mass, and 64% isolated yield.",
         "evidence_ids": evidence(6)},
        {"region": "middle-left preparation of 2h",
         "finding": "The detailed 2h batch was merged into Table 4 entry 9 with exact quantities, 21.5 h at 150 °C, product mass, and 73% isolated yield.",
         "evidence_ids": evidence(6)},
        {"region": "lower-left and upper-right preparation of 2i",
         "finding": "The detailed 2i batch was merged into Table 4 entry 10 with exact quantities, 26 h at 150 °C, product mass, and 72% isolated yield.",
         "evidence_ids": evidence(6)},
        {"region": "middle-right preparation of 2j",
         "finding": "The detailed 2j batch was merged into Table 4 entry 11 with exact quantities, 26 h at 150 °C, product mass, and 65% isolated yield.",
         "evidence_ids": evidence(6)},
        {"region": "bottom-right beginning of the 2k paragraph",
         "finding": "The visible start of the 2k preparation was merged into Table 4 entry 12; the printed CuI mass/mmol versus table loading inconsistency is preserved and the continuation on page 7 was not imported.",
         "evidence_ids": evidence(6)},
    ],
}

unresolved = {
    1: ["Figure 1 provides qualitative failure only; no numerical yield is stated.",
        "Structure-based names for the first four Figure 1 additives remain machine assignments requiring review."],
    2: ["Table 2 visibly contains duplicate catalyst labels in entries 1/2 and 5/6; these are retained as distinct rows because time and outcomes differ.",
        "Table dashes have undefined semantics and were not interpreted as zero or not detected."],
    3: ["Operational atmosphere, workup, and purification are absent from the Table 4/5 rows unless a matching experimental paragraph occurs on pages 4-6.",
        "The Table 5 isobutyral-derived contaminant is not assigned a complete structure."],
    4: ["The 2c paragraph begins on page 4 but its quantities and outcome continue on page 5.",
        "No supporting-information file was explicitly associated with the dataset."],
    5: ["The compounds are stated to follow the page-4 typical procedure; individual paragraphs do not restate every operation.",
        "No supporting-information file was explicitly associated with the dataset."],
    6: ["The 2k paragraph continues onto page 7, outside this coverage claim.",
        "For 2k, page 6 prints CuI as 38.0 mg, 0.10 mmol while Table 4 gives 20 mol% on 1.0 mmol substrate; no correction was inferred."],
}

result = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {"page": page, "state": "attempted", "regions": regions[page],
         "record_ids": page_records(page), "unresolved": unresolved[page]}
        for page in range(1, 7)
    ],
}

target = BASE / "coverage" / "pages_0001_0006.json"
target.parent.mkdir(parents=True, exist_ok=True)
target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"output": str(target), "pages": len(result["pages"]),
                  "page_record_counts": [len(p["record_ids"]) for p in result["pages"]]}, ensure_ascii=False))
