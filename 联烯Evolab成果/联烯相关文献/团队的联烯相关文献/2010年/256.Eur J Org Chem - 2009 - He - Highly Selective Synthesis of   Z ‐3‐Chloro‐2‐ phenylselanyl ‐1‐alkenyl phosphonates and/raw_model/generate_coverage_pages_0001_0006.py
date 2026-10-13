#!/usr/bin/env python3
"""Write the visual coverage ledger for source PDF pages 1--6."""
from __future__ import annotations

import json
from pathlib import Path

DOC = "doc_c4d18a33a17c9cf6"
ROOT = Path(__file__).resolve().parents[3]
DATASET = ROOT / "runs/current/dataset.json"
COVERAGE = ROOT / "runs/current/coverage/pages_0001_0006.json"
TASKS = ROOT / "runs/current/tasks.json"


def rid(suffix: str) -> str:
    return f"{DOC}:{suffix}"


def ev(page: int) -> list[str]:
    return [f"{DOC}:page{page}:image", f"{DOC}:page{page}:text"]


t1 = [
    "table1_entry1", "table1_entry2", "table1_entry3", "table1_entry4", "table1_entry5",
    "table1_entry6_table2_entry2_typical_iii_2a", "table1_entry7", "table1_entry8",
    "table1_entry9", "table1_entry10_table2_entry1_typical_ii_2a", "table1_entry11",
]
t2 = [
    "table1_entry10_table2_entry1_typical_ii_2a", "table1_entry6_table2_entry2_typical_iii_2a",
    "table2_entry3_2b", "table2_entry4_2b", "table2_entry5_2c", "table2_entry6_2d",
    "table2_entry7_2e", "table2_entry8_2f", "table2_entry9_2g", "table2_entry10_2h",
]
scheme2 = [
    "scheme2_eq1_2i", "scheme2_eq2_conditions_a_2j", "scheme2_eq2_conditions_b_2j",
    "scheme2_eq3_conditions_a_2k", "scheme2_eq3_conditions_b_2k", "macomber_1983_literature_1k",
]
table3 = [f"table3_entry{i}" for i in range(1, 5)]
table4 = [f"table4_entry{i}" for i in range(1, 4)]

pages = [
    {
        "page": 1,
        "state": "attempted",
        "regions": [
            {
                "region": "title, abstract, and introduction in both columns",
                "finding": "The abstract gives broad scope claims only. The introduction identifies cited prior selenochlorination, including the Macomber dimethyl-allenylphosphonate example; the cited example is classified as literature, not as a new batch from this paper.",
                "evidence_ids": ev(1),
            },
            {
                "region": "middle-right Scheme 1, both reaction arrows",
                "finding": "Two generic transformations were inventoried separately: prior E-selective halo/selenohydroxylation and this-work Z-selective PhSeCl selenochlorination. Both remain general_scheme records with generic R groups and no invented batch yield.",
                "evidence_ids": ev(1),
            },
            {
                "region": "lower-right opening Results and Discussion",
                "finding": "The prose reports the Table 1 entry-1 experiment (33% Z-2a plus 36% 3a) and previews the distinct MeCN/H2O 3:1 entry; numeric row details are reconciled with page 2 rather than duplicated.",
                "evidence_ids": ev(1),
            },
        ],
        "record_ids": [rid(x) for x in [
            "scheme1_prior_e_halohydroxylation", "scheme1_this_work_z_selenochlorination",
            "table1_entry1", "table1_entry2", "macomber_1983_literature_1k",
        ]],
        "unresolved": [
            "Scheme 1 structures are generic and cannot support fully specified SMILES.",
            "The linked Supporting Information is mentioned by the paper but was not explicitly provided or associated in this workspace.",
            "Table 1 continues on page 2; page-1 prose alone does not establish every row field.",
        ],
    },
    {
        "page": 2,
        "state": "attempted",
        "regions": [
            {
                "region": "upper full-width Table 1, reaction drawing, rows 1--11, and footnotes a--c",
                "finding": "All 11 optimization rows were extracted independently with PhSeCl equivalents, solvent/water system, temperature, time, product-specific isolated yields, product ratio, and impurity footnote. Rows 6 and 10 are the same conditions/outcomes later repeated in Table 2 and detailed procedures, so they were merged across evidence rather than duplicated.",
                "evidence_ids": ev(2),
            },
            {
                "region": "middle-left Table 1 discussion",
                "finding": "Narrative statements about exclusive 2a formation and solvent screening were used as corroboration; no extra experiments were created beyond the table rows.",
                "evidence_ids": ev(2),
            },
            {
                "region": "middle-right Table 2, reaction drawing, rows 1--10, and footnotes",
                "finding": "Ten scope rows were inventoried. The two 1a rows merge with Table 1 rows 10 and 6 respectively; the remaining eight rows are independent substrate-scope records. Later detailed batch quantities replace no table facts; explicit scale conflicts are preserved as unresolved notes.",
                "evidence_ids": ev(2),
            },
            {
                "region": "lower two-column stereochemistry discussion and page-break continuation",
                "finding": "The page previews the p-bromophenyl and dimethyl control experiments and reports that both 1-phenyl- and 3-phenyl allenylphosphonate reactions became complicated. The two failed/complex substrate experiments are separate partial records; Scheme 2 supplies their control-experiment details on page 3.",
                "evidence_ids": ev(2),
            },
        ],
        "record_ids": [rid(x) for x in t1 + t2 + [
            "phenyl_1_substituted_complicated", "phenyl_3_substituted_complicated",
            "macomber_1983_literature_1k",
        ]],
        "unresolved": [
            "Table 1 entries 3, 4, 7, and 8 contain an unidentified impurity inseparable from 3a.",
            "The Table 2 table-wide 0.30 mmol scale conflicts with detailed 0.20 mmol batches for 1a, 1e, and 1g; the discrepancy is retained rather than guessed away.",
            "The phenyl-substituted reactions have no stated product identity, time, or yield.",
        ],
    },
    {
        "page": 3,
        "state": "attempted",
        "regions": [
            {
                "region": "upper Scheme 2 equations 1--3 and Conditions A/B annotations",
                "finding": "Five current-paper batches (2i; 2j under A and B; 2k under A and B) were separated by substrate and condition. The 7 h/46% Macomber result was classified separately as a literature example, while the current 19 h/71% repetition is a reported experiment. Recovery of 1j under 2j Conditions B is stored as recovery, not product yield.",
                "evidence_ids": ev(3),
            },
            {
                "region": "middle Figure 1 ORTEP and Figure 2 NOE panels",
                "finding": "These panels support stereochemical characterization of already recorded products 2j and 2m; they do not depict new reaction batches and therefore generate no duplicate experiment records.",
                "evidence_ids": ev(3),
            },
            {
                "region": "middle-left Scheme 3 equations 1--2",
                "finding": "Two scale-up batches were extracted independently: 4.8 mmol 1a to Z-2a (72%) and 5.5 mmol 1j to Z-2l (80%). The first is linked to its detailed page-5 procedure.",
                "evidence_ids": ev(3),
            },
            {
                "region": "bottom Table 3, rows 1--4 and footnotes",
                "finding": "Four independent 1-substituted-allenylphosphonate scope rows were extracted with both Z-2 and cyclic-3 product yields. Entry 2 uses the THF/H2O footnote override; the other rows use dioxane/H2O.",
                "evidence_ids": ev(3),
            },
            {
                "region": "right-column mechanistic prose and left-column continuation from page 2",
                "finding": "The phenyl-substrate failure statement is completed, and the proposed selenonium-intermediate rationale is classified with Scheme 4 as mechanism rather than experimental evidence.",
                "evidence_ids": ev(3),
            },
        ],
        "record_ids": [rid(x) for x in scheme2 + [
            "scheme3_large_scale_1a_to_2a", "scheme3_large_scale_1j_to_2l",
            "phenyl_1_substituted_complicated", "phenyl_3_substituted_complicated",
            "scheme4_proposed_selenonium_pathway",
        ] + table3],
        "unresolved": [
            "The cited external Macomber paper was not supplied, so its 7 h/46% batch was not independently source-checked beyond this paper's citation.",
            "Table 3 rows omit exact masses, atmosphere, workup, and purification.",
            "Cyclic and stereochemical structures remain unverified machine interpretations despite ORTEP/NOE support.",
        ],
    },
    {
        "page": 4,
        "state": "attempted",
        "regions": [
            {
                "region": "upper-left Scheme 4 and adjacent mechanism discussion",
                "finding": "The network through proposed intermediates (E)-4 and (Z)-5, chloride attack, and O-attack is stored as one mechanism record. It is not treated as a measured experiment or assigned a yield.",
                "evidence_ids": ev(4),
            },
            {
                "region": "middle-left Table 4, rows 1--3 and footnotes",
                "finding": "Three multisubstituted-allenylphosphonate rows were extracted independently. Entries 1 and 3 use the table's room-temperature header; entry 2 uses the 70 °C footnote override.",
                "evidence_ids": ev(4),
            },
            {
                "region": "lower-left Conclusions",
                "finding": "The conclusions summarize the product-class split and introduce no additional batch experiment.",
                "evidence_ids": ev(4),
            },
            {
                "region": "right-column Experimental Section: Starting Materials and Typical Procedure I for 1e",
                "finding": "The full preparation of 1e was extracted with reagent amounts, -78 °C addition, 15 min addition time, warm-to-room-temperature/reflux operation, workup, chromatography, product mass, and 73% isolated yield.",
                "evidence_ids": ev(4),
            },
            {
                "region": "lower-right abbreviated preparations of 1g and 1q",
                "finding": "The two separate batches were extracted with their explicit quantities and outcomes and linked to Typical Procedure I. Unrestated duration details remain missing; 1q analytical characterization continues on page 5.",
                "evidence_ids": ev(4),
            },
        ],
        "record_ids": [rid(x) for x in ["scheme4_proposed_selenonium_pathway"] + table4 + ["prep_1e", "prep_1g", "prep_1q"]],
        "unresolved": [
            "The abbreviated 1g and 1q preparations do not restate exact addition or reaction durations.",
            "No preparation atmosphere is reported.",
            "Generic Scheme 4 substituents and proposed intermediates are not structure-verified.",
        ],
    },
    {
        "page": 5,
        "state": "attempted",
        "regions": [
            {
                "region": "top-left continuation of 1q characterization",
                "finding": "Only analytical characterization continues from page 4; it supports the existing 1q preparation record and does not create a new reaction batch.",
                "evidence_ids": ev(5),
            },
            {
                "region": "left-column Typical Procedure II and Typical Procedure III for Z-2a",
                "finding": "The THF and dioxane batches match Table 1 entries 10 and 6 and Table 2 entries 1 and 2 respectively, so evidence was merged into two records. Workup and chromatography details were added; the Table 2 scale discrepancy remains explicit.",
                "evidence_ids": ev(5),
            },
            {
                "region": "left-bottom and right-top larger-scale 1a reaction",
                "finding": "The 4.8 mmol scale-up is the same batch as Scheme 3 equation 1; its detailed additions, workup, 1.4637 g product mass, and 72% isolated yield were merged into that record.",
                "evidence_ids": ev(5),
            },
            {
                "region": "right-upper MeCN/H2O 3:1 experiment giving Z-2a and 3a",
                "finding": "This explicit 0.30 mmol batch gives 18% Z-2a and 49% 3a (3a dr 35:65). Although nominal conditions/outcomes match Table 1 entry 2, the table specifies 0.20 mmol, so this batch remains a separate reported experiment.",
                "evidence_ids": ev(5),
            },
            {
                "region": "right-middle two Z-2b procedures and bottom cross-page start of Z-2c",
                "finding": "The dioxane and THF Z-2b batches merge with Table 2 entries 4 and 3. The Z-2c batch begins here and continues on page 6; it is one cross-page record, not two.",
                "evidence_ids": ev(5),
            },
        ],
        "record_ids": [rid(x) for x in [
            "prep_1q", "table1_entry10_table2_entry1_typical_ii_2a",
            "table1_entry6_table2_entry2_typical_iii_2a", "scheme3_large_scale_1a_to_2a",
            "page5_scaled_mecn_3to1_2a_3a", "table2_entry3_2b", "table2_entry4_2b", "table2_entry5_2c",
        ]],
        "unresolved": [
            "The relationship between the 0.30 mmol MeCN batch and 0.20 mmol Table 1 entry 2 is not stated.",
            "Table 2's table-wide scale conflicts with the detailed 0.20 mmol 1a procedures.",
            "Z-2c analytical and outcome text continues on page 6.",
        ],
    },
    {
        "page": 6,
        "state": "attempted",
        "regions": [
            {
                "region": "upper-left continuation of Z-2c procedure and characterization",
                "finding": "The cross-page Z-2c record is completed with 1.5 h at 70 °C, 77.7 mg isolated product, and 64% yield; no duplicate record was created.",
                "evidence_ids": ev(6),
            },
            {
                "region": "left-column Z-2d and Z-2e procedures",
                "finding": "Two distinct THF/H2O scope batches were extracted and merged with Table 2 entries 6 and 7, preserving exact detailed quantities and the 66% and 68% isolated yields.",
                "evidence_ids": ev(6),
            },
            {
                "region": "right-column Z-2f, Z-2g, and Z-2h procedures",
                "finding": "Three distinct THF/H2O scope batches were extracted and merged with Table 2 entries 8--10, including exact batch quantities, time, product mass, and isolated yield. The 1g substrate's stated 91% purity is structured as a participant amount.",
                "evidence_ids": ev(6),
            },
            {
                "region": "analytical characterization blocks throughout both columns",
                "finding": "NMR/MS/IR/HRMS characterization supports product identity but is not represented as additional reaction experiments. The Z-2h characterization continues beyond page 6 and is not claimed as covered here.",
                "evidence_ids": ev(6),
            },
        ],
        "record_ids": [rid(x) for x in [
            "table2_entry5_2c", "table2_entry6_2d", "table2_entry7_2e",
            "table2_entry8_2f", "table2_entry9_2g", "table2_entry10_2h",
        ]],
        "unresolved": [
            "The detailed 1e and 1g batches use 0.20 mmol while Table 2 states a table-wide 0.30 mmol scale.",
            "Reaction atmospheres are not reported.",
            "Z-2h characterization continues on page 7, outside the claimed coverage range.",
        ],
    },
]

dataset = json.loads(DATASET.read_text())
known = {r["record_id"] for r in dataset["experiments"]}
referenced = {record_id for page in pages for record_id in page["record_ids"]}
missing = sorted(referenced - known)
if missing:
    raise SystemExit(f"coverage references unknown record ids: {missing}")

payload = {"document_id": DOC, "semantic_accuracy_verified": False, "pages": pages}
COVERAGE.parent.mkdir(parents=True, exist_ok=True)
COVERAGE.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")

tasks = json.loads(TASKS.read_text())
for task in tasks:
    if task["document_id"] == DOC and task["evidence_id"] in {f"{DOC}:page{p}:text" for p in range(1, 7)}:
        task["state"] = "attempted"
        task["reason"] = "Original page image and text inspected; records and coverage ledger generated for this page."
TASKS.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"coverage": str(COVERAGE.relative_to(ROOT)), "pages": len(pages), "record_ids": len(referenced)}, ensure_ascii=False))
