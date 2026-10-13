#!/usr/bin/env python3
"""Write the visual coverage ledger for the current six-page extraction pass."""
import json
from pathlib import Path

DOC = "doc_4e9a90c5ea8a1795"


def ids(prefix, values):
    return [f"{DOC}:{prefix}{v}" for v in values]


def evidence(page):
    return [f"{DOC}:page{page}:image", f"{DOC}:page{page}:text"]


table1 = ids("table1_entry", range(1, 15))
table2 = [f"{DOC}:table2_entry{i}_e3{chr(96+i)}" for i in range(1, 11)]
table3_products = ["4a", "4b", "4c", "4e", "4g", "4i", "4n", "4o", "4p", "4q", "4r", "4s", "4s"]
table3 = [f"{DOC}:table3_entry{i}_{p}" for i, p in enumerate(table3_products, 1)]
scheme1 = [f"{DOC}:scheme1_1k_conditionsA_failure", f"{DOC}:scheme1_1l_conditionsA"]
scheme2 = [f"{DOC}:scheme2_1m_conditions{x}" for x in "ABC"]
scheme3 = [
    f"{DOC}:scheme3_1k_conditionsB_mixture",
    f"{DOC}:scheme3_1k_conditionsC_mixture",
    f"{DOC}:scheme3_1t_conditionsC_mecn_mixture",
    f"{DOC}:scheme3_1t_conditionsC_meno2_mixture",
]
scheme5 = [f"{DOC}:scheme5_large_scale_conditionsA", f"{DOC}:scheme5_large_scale_conditionsB"]

pages = [
    {
        "page": 1,
        "state": "attempted",
        "regions": [
            {
                "region": "title, abstract, introduction, and left-column prior-work discussion",
                "finding": "The title/abstract state overall scope and cite earlier fluorocyclizations; those broad claims and prior work were classified as context and were not duplicated as experiments.",
                "evidence_ids": evidence(1),
            },
            {
                "region": "Results and discussion opening in the lower half and right column",
                "finding": "Narrative identifies substrate 1a, Selectfluor, 80 °C, and the optimization sequence represented by Table 1, including nitrogen/dry-MeCN rows, water effects, Conditions A, and Conditions B. These prose mentions were linked to the Table 1 records rather than counted again.",
                "evidence_ids": evidence(1),
            },
        ],
        "record_ids": table1,
        "unresolved": [
            "The article advertises ESI, but no supplement was explicitly provided or associated.",
            "Page 1 contains no standalone scheme/table from which additional independent batches can be read.",
        ],
    },
    {
        "page": 2,
        "state": "attempted",
        "regions": [
            {
                "region": "upper Table 1, reaction drawing, rows 1–14, and footnotes a–e",
                "finding": "All fourteen optimization rows were extracted independently. Selectfluor equivalents, solvent/additive, time, NMR yields, product ratio, recovered 1a, nitrogen/dry-MeCN footnote, and 1H/19F NMR measurement bases were preserved; dashes were not converted to zero.",
                "evidence_ids": evidence(2),
            },
            {
                "region": "middle Table 2, generic arrow, rows 1–10, and Conditions A footnotes",
                "finding": "All ten substrate-scope rows were extracted independently and later reconciled with their matching detailed preparation paragraphs on pages 4–6. The shared 3 equiv Selectfluor, 0.5 equiv water, 2–3 mL anhydrous MeCN, nitrogen, 80 °C, isolated-yield basis, and crude 19F NMR ratios were retained.",
                "evidence_ids": evidence(2),
            },
            {
                "region": "lower Fig. 1 and adjacent prose",
                "finding": "HOESY supports the E assignments of E-3a and E-5m; it was treated as characterization evidence, not as a new synthesis. Prose describing 1l and the three 1m condition sets was linked to Scheme 1/2 records shown on page 3.",
                "evidence_ids": evidence(2),
            },
        ],
        "record_ids": table1 + table2 + [scheme1[1]] + scheme2,
        "unresolved": [
            "Most Table 1 rows do not report exact batch masses/volumes, workup, or isolation details.",
            "Candidate structure encodings are unverified; R-group table labels were not treated as verified SMILES.",
        ],
    },
    {
        "page": 3,
        "state": "attempted",
        "regions": [
            {
                "region": "upper Table 3, generic arrow, rows 1–13, and footnotes a–d",
                "finding": "Thirteen independent lactonization scope rows were extracted, including the 2.5 equiv overrides for entries 2–3, the MeNO2 solvent override for entry 13, isolated yields, times, and crude 19F NMR 4/3 or 4/5 ratios.",
                "evidence_ids": evidence(3),
            },
            {
                "region": "middle Scheme 1, both reaction arrows",
                "finding": "The 1k Conditions A failure and the separate 1l experiment giving E-3l/4l were recorded independently with their explicit times, yields, and 87/13 ratio.",
                "evidence_ids": evidence(3),
            },
            {
                "region": "lower Scheme 2, three condition rows",
                "finding": "Conditions A, B, and C for substrate 1m were retained as three distinct experiments because their reagent loading/solvent regime, time, and 4m/E-5m outcomes differ.",
                "evidence_ids": evidence(3),
            },
            {
                "region": "bottom prose introducing Scheme 3 and proposed Scheme 4",
                "finding": "The text reports complicated or failed alkyl-substrate outcomes and introduces a plausible mechanism. The former were linked to page-4 Scheme 3 records; the latter was classified as a mechanism, not a reported batch.",
                "evidence_ids": evidence(3),
            },
        ],
        "record_ids": table3 + scheme1 + scheme2 + scheme3 + [f"{DOC}:scheme4_proposed_mechanism"],
        "unresolved": [
            "Table 3 rows 7–13 lack exact batch masses and full operations on the covered pages.",
            "The unidentified mixtures announced in the prose cannot be assigned structures or yields.",
        ],
    },
    {
        "page": 4,
        "state": "attempted",
        "regions": [
            {
                "region": "upper-left Scheme 3, four condition arrows",
                "finding": "Conditions B and C for 1k and the MeCN/MeNO2 Conditions C trials for 1t were extracted as four distinct failed/mixture experiments. The 9% recovered 1k values were classified as recovery rather than product yield.",
                "evidence_ids": evidence(4),
            },
            {
                "region": "left-center Scheme 4 and explanatory prose",
                "finding": "The generic fluorination/hydration/oxidation or dealkylative-lactonization network was captured as one proposed-mechanism record; no experimental yield was assigned to its arrows.",
                "evidence_ids": evidence(4),
            },
            {
                "region": "left-lower Scheme 5, two 5 mmol arrows",
                "finding": "The Conditions A scale-up yielding E-3a plus 4a and the separate Conditions B scale-up yielding 4a were extracted as two independent batches with exact masses, times, workups, purification, yields, and product ratio where shown.",
                "evidence_ids": evidence(4),
            },
            {
                "region": "right-column Experimental section: typical Conditions A for 3a and preparations 3b–3c",
                "finding": "The detailed 3a batch and abbreviated matching batches for 3b and 3c were merged into Table 2 entries 1–3 instead of duplicated. Exact substrate/Selectfluor quantities, solvent volumes, nitrogen, temperature, product masses, and typical workup were retained.",
                "evidence_ids": evidence(4),
            },
        ],
        "record_ids": scheme3 + [f"{DOC}:scheme4_proposed_mechanism"] + scheme5 + table2[:3],
        "unresolved": [
            "Scheme 3 mixture components are unidentified.",
            "Scheme 4 is explicitly only a plausible mechanism and its generic intermediates have no verified structures.",
            "The 3c characterization continues on page 5; it was not treated as a new experiment.",
        ],
    },
    {
        "page": 5,
        "state": "attempted",
        "regions": [
            {
                "region": "upper-left continuation of 3c characterization",
                "finding": "This is analytical continuation of the Table 2 entry 3 batch, not a new reaction; the source-linked 3c record includes page-5 evidence.",
                "evidence_ids": evidence(5),
            },
            {
                "region": "left column preparations 3d–3f",
                "finding": "Exact substrate and Selectfluor masses/mmol, 3 mL H2O–MeCN, nitrogen, 80 °C, product masses, and isolated yields were merged into Table 2 entries 4–6 under the page-4 typical Conditions A procedure.",
                "evidence_ids": evidence(5),
            },
            {
                "region": "right column preparations 3g–3j",
                "finding": "Preparations 3g–3j were merged into Table 2 entries 7–10. The special flash-chromatography 100:1 eluent for 3h was retained; 3j characterization continues on page 6 without creating another record.",
                "evidence_ids": evidence(5),
            },
        ],
        "record_ids": table2[2:],
        "unresolved": [
            "The repeated phrase 'according to this typical procedure' does not restate each workup volume for every derivative.",
            "Spectral assignments were not interpreted atom by atom and do not constitute independent reaction records.",
        ],
    },
    {
        "page": 6,
        "state": "attempted",
        "regions": [
            {
                "region": "upper-left continuation of 3j characterization",
                "finding": "The text continues Table 2 entry 10 characterization only; it was linked to that existing record and not duplicated.",
                "evidence_ids": evidence(6),
            },
            {
                "region": "section 2, typical Conditions B for 4a and preparations 4b, 4c, 4e, 4g, 4i",
                "finding": "Six detailed lactone batches were reconciled with Table 3 entries 1–6. Exact reactant/reagent masses and mmol, MeCN/water volumes, 80 °C, product masses, isolated yields, and the typical workup/purification were retained.",
                "evidence_ids": evidence(6),
            },
            {
                "region": "section 3, typical Conditions C for 4m",
                "finding": "The 0.20 mmol Conditions C batch of 1m yielding 4m in 90% was merged with Scheme 2 Conditions C, including exact masses, 2 mL MeCN, 5.5 h, workup, purification, and product mass.",
                "evidence_ids": evidence(6),
            },
            {
                "region": "bottom-right start of 1m under Conditions A",
                "finding": "The visible 2.01 mmol Conditions A quantities and the 4m/E-5m masses and yields were merged into the Scheme 2 Conditions A record; the page-7 characterization continuation was not imported or claimed as covered.",
                "evidence_ids": evidence(6),
            },
        ],
        "record_ids": [table2[9]] + table3[:6] + [scheme2[0], scheme2[2]],
        "unresolved": [
            "The Conditions A 4m/E-5m discussion continues onto page 7, outside this coverage claim.",
            "No explicitly associated SI was available for additional procedures or spectra.",
            "All structure encodings remain machine candidates with structure_verified=false.",
        ],
    },
]

ledger = {"document_id": DOC, "semantic_accuracy_verified": False, "pages": pages}
path = Path(__file__).parents[1] / "coverage" / "pages_0001_0006.json"
path.parent.mkdir(parents=True, exist_ok=True)
path.write_text(json.dumps(ledger, ensure_ascii=False, indent=2) + "\n")
print(path)
