#!/usr/bin/env python3
import json
from pathlib import Path

DOC = "doc_5728b702b8559e95"


def evid(page):
    return [f"{DOC}:page{page}:image", f"{DOC}:page{page}:text"]


def region(page, name, finding):
    return {"region": name, "finding": finding, "evidence_ids": evid(page)}


t1 = [f"{DOC}:table1_entry{i}_{label}" for i, label in enumerate(
    ["1a", "1b", "1c", "1d", "1e", "1f", "1g", "1h", "1i", "1j"], 1)]
t2 = [f"{DOC}:table2_entry{i}" for i in range(1, 12)]
t3_labels = ["3aa", "3ab", "3ac", "3ad", "3ae", "3af", "3ag", "3ah", "3ai", "3aj",
             "3ak", "3al", "3am", "3an", "3ao", "3ap", "3aq", "3ar", "3ba", "3ca",
             "3da", "3ea", "3fa", "3ga", "3ha", "3ia", "3ja"]
t3 = [f"{DOC}:table3_entry{i}_{label}" for i, label in enumerate(t3_labels, 1)]
gram = [f"{DOC}:scheme1_gram_scale_{label}" for label in ["1a", "1e", "1j"]]

pages = [
    {
        "page": 1,
        "state": "attempted",
        "regions": [
            region(1, "left-column introduction and equation (1)",
                   "The displayed CuBr/i-Pr2NH route with 4–55% yields is explicitly attributed to Hashmi et al. ref. 5 and was classified as a literature_example rather than a new experiment."),
            region(1, "lower-right Table 1, entries 1–10 and footnote",
                   "Ten distinct N-propargyl-amide to N-allenyl-amide substrate-scope rows were extracted with shared CuI/paraformaldehyde/Cy2NH/dioxane/100 °C conditions, row-specific times, and isolated yields."),
        ],
        "record_ids": [f"{DOC}:eq1_ref5_literature_example"] + t1,
        "unresolved": [
            "Equation (1) uses a generic R1 structure and gives no reaction time.",
            "The paper advertises ESI, but no SI was explicitly provided or associated in this workspace.",
        ],
    },
    {
        "page": 2,
        "state": "attempted",
        "regions": [
            region(2, "upper-left Scheme 1",
                   "Three separate 10/15 mmol gram-scale allene preparations (1a, 1e, 1j) were extracted and linked to their detailed paragraphs on later pages."),
            region(2, "upper-right Table 2 and footnotes",
                   "All 11 solvent/base optimization rows were extracted independently, including the 0% KOtBu row, NMR measurement basis using mesitylene, and 23%/62% recovered 1a for entries 2/7."),
            region(2, "lower-right Table 3 and footnote",
                   "All 27 palladium-catalyzed coupling–cyclization substrate-scope rows were extracted separately with shared amounts, conditions, row-specific times, and isolated yields."),
            region(2, "lower-left narrative prior-work discussion",
                   "Ag/Au/Cook reactions are literature discussion without a newly reported batch on this page and were not converted into this paper's experiments."),
        ],
        "record_ids": gram + t2 + t3,
        "unresolved": [
            "Most Table 2 and Table 3 rows are table-only and omit workup, purification, and product mass.",
            "Candidate structures, especially heteroaryl and alkenyl substituent products, remain unverified.",
        ],
    },
    {
        "page": 3,
        "state": "attempted",
        "regions": [
            region(3, "upper-left Fig. 1 and surrounding scope discussion",
                   "Fig. 1 is an ORTEP characterization of product 3ah, not a reaction arrow or independent experiment."),
            region(3, "middle-left equations (2) and (3)",
                   "Two separate gram-scale/low-catalyst-loading coupling–cyclization batches were extracted: 1d→3da at 1 mol% Pd and 1a→3ak at 0.1 mol% Pd."),
            region(3, "right-column Table 1 experimental section, typical procedure I and gram-scale 1a",
                   "The detailed 1 mmol Table 1 entry 1 preparation and the distinct 10 mmol gram-scale 1a batch were merged with their respective table/scheme records, retaining exact quantities, workup, product mass, and yields where present."),
            region(3, "bottom-right opening of the 1b preparation",
                   "The displayed 1b reaction is the same Table 1 entry 2 experiment; it was merged with the detailed continuation on page 4."),
        ],
        "record_ids": [t1[0], t1[1], gram[0], f"{DOC}:eq2_gram_scale_3da", f"{DOC}:eq3_gram_scale_3ak"],
        "unresolved": [
            "Equations (2) and (3) omit several reactant/base/solvent quantities and workup details.",
            "The ORTEP is labeled 3ah here, while reference note 12 on page 6 says crystal data for 4ai; the source inconsistency is unresolved.",
        ],
    },
    {
        "page": 4,
        "state": "attempted",
        "regions": [
            region(4, "left column continuation of 1b and preparations 1c–1d",
                   "Detailed Table 1 entries 2–4 were merged with their page-1 table rows, retaining reagent masses/amounts, product masses, times, isolated yields, and chromatography eluents."),
            region(4, "right column preparations 1e–1f and gram-scale 1e paragraph",
                   "Detailed Table 1 entries 5–6 and the distinct 14.6 mmol gram-scale 1e batch were extracted; the gram-scale batch was linked to Scheme 1 rather than merged with the 1 mmol row."),
        ],
        "record_ids": t1[1:6] + [gram[1]],
        "unresolved": [
            "Scheme 1 rounds the 1e scale to 15 mmol, whereas the detailed paragraph reports 14.6 mmol; the detailed batch value was retained.",
            "The source reports CuI as 0.830 g, 7.6 mmol in the gram-scale 1e paragraph; this apparent mass/amount inconsistency is preserved for review.",
        ],
    },
    {
        "page": 5,
        "state": "attempted",
        "regions": [
            region(5, "left column preparations 1g–1i",
                   "Detailed Table 1 entries 7–9 were merged with their page-1 rows, retaining exact quantities, product masses, isolated yields, times, and eluents."),
            region(5, "upper-right preparation 1j and gram-scale 1j paragraph",
                   "The 1 mmol Table 1 entry 10 and separate 15 mmol gram-scale 1j batch were extracted without merging the two conditions."),
            region(5, "lower-right typical procedure II for 3aa",
                   "Exact quantities, nitrogen atmosphere, 80 °C/3 h conditions, workup, purification, 40.3 mg product mass, and 80% isolated yield were merged into Table 3 entry 1; characterization continues on page 6."),
        ],
        "record_ids": t1[6:10] + [gram[2], t3[0]],
        "unresolved": [
            "The paper points to ESI for more detailed 3aa NMR information, but no SI is explicitly associated.",
            "All candidate SMILES remain machine records with structure_verified=false.",
        ],
    },
    {
        "page": 6,
        "state": "attempted",
        "regions": [
            region(6, "top-left continuation of 3aa characterization",
                   "This is the continuation of the same Table 3 entry 1 batch, containing NMR/IR/MS/HRMS characterization only; no new reaction record was created."),
            region(6, "acknowledgements and references columns",
                   "No new experimental arrows or batches occur. Citations and crystallographic note 12 were treated as references/characterization, not experiments."),
        ],
        "record_ids": [t3[0]],
        "unresolved": [
            "The page refers readers to ESI for more detailed 1H NMR, but SI is not available in the dataset.",
            "Reference note 12 says crystal data for 4ai despite Fig. 1 and the main text identifying 3ah.",
        ],
    },
]

coverage = {"document_id": DOC, "semantic_accuracy_verified": False, "pages": pages}
target = Path(__file__).with_name("pages_0001_0006.json")
target.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")
print(target)
