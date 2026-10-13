"""Write the required six-page semantic coverage ledger."""
import json
from pathlib import Path

DOC = "doc_f68af135ec78d163"
RID = lambda suffix: f"{DOC}:{suffix}"
EV = lambda page: [f"{DOC}:page{page}:image", f"{DOC}:page{page}:text"]

table1 = [RID(f"table1_entry{i}") for i in range(1, 14)]
table2_labels = ["1a", "1b", "1c", "1d", "1e", "1f", "1g", "1h", "1i", "1j", "1k"]
table2 = [RID(f"table2_entry{i}_{label}") for i, label in enumerate(table2_labels, 1)]
table3 = [RID(f"table3_entry{i}") for i in range(1, 8)]
table4_labels = ["1m", "1n", "1o", "1p", "1q", "1r", "1s", "1t"]
table4 = [RID(f"table4_entry{i}_{label}") for i, label in enumerate(table4_labels, 1)]
scheme2 = [RID("scheme2_control_" + x) for x in ["i2_only", "bnsh_only", "bnsh_i2", "bnssbn_i2", "bnssbn_only"]]
table5 = [RID(f"table5_entry{i}") for i in range(1, 5)]

ledger = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1,
            "state": "attempted",
            "regions": [
                {
                    "region": "upper title, abstract, and two-column introduction/results prose",
                    "finding": "Article identity, broad iodohydroxylation claim, and opening conditions were checked; abstract-level scope statements were not duplicated as batch records.",
                    "evidence_ids": EV(1),
                },
                {
                    "region": "lower-left Scheme 1",
                    "finding": "Separated the ref. 4 prior halohydroxylation branch from the current paper's generic BnSH route; both remain non-batch records.",
                    "evidence_ids": EV(1),
                },
                {
                    "region": "lower-right Eq. (1)",
                    "finding": "Extracted the 1a/BnSH/I2 experiment in commercial MeCN at 5 °C for 2 h, 53% yield and E/Z 96/4.",
                    "evidence_ids": EV(1),
                },
            ],
            "record_ids": [
                RID("scheme1_prior_halohydroxylation"),
                RID("scheme1_current_generic_route"),
                RID("eq1_1a_iodohydroxylation"),
            ],
            "unresolved": [
                "Scheme 1 uses generic R groups and does not specify unique structures or batch conditions.",
                "Eq. (1) does not state scale, workup, or yield measurement basis on page 1.",
            ],
        },
        {
            "page": 2,
            "state": "attempted",
            "regions": [
                {
                    "region": "upper Table 1 reaction drawing, entries 1-13, and footnotes a-d",
                    "finding": "Extracted all 13 optimization rows independently, including absence of BnSH in entry 5, table dashes in entry 7, zero results in entry 12, and the anhydrous-MeCN/2-equiv-water override in entry 13.",
                    "evidence_ids": EV(2),
                },
                {
                    "region": "lower-left discussion of solvent, temperature, and BnSH effects",
                    "finding": "Discussion was reconciled with Table 1 rather than duplicated; it confirms the entry-specific yields/selectivities and no-BnSH behavior.",
                    "evidence_ids": EV(2),
                },
                {
                    "region": "lower-right prose on water and anhydrous MeCN",
                    "finding": "Added separate partial records for the 77/23 E/Z anhydrous-MeCN comparison and the 10-equiv-water no-reaction test with 73% recovered 1f.",
                    "evidence_ids": EV(2),
                },
            ],
            "record_ids": table1 + [
                RID("prose_anhydrous_mecn_selectivity_test"),
                RID("prose_water_10equiv_no_reaction"),
            ],
            "unresolved": [
                "The two prose-only comparison experiments omit several exact conditions and outcome bases.",
                "Product structures and E/Z assignments are source-read labels but remain unverified machine structures.",
            ],
        },
        {
            "page": 3,
            "state": "attempted",
            "regions": [
                {
                    "region": "upper-left Table 2 drawing, entries 1-11, and footnotes a-e",
                    "finding": "Extracted all 11 monosubstituted-allene scope rows; isolated yields and NMR E/Z ratios were kept separate, and entry 1's Conditions A/anhydrous-MeCN override was linked to page 2.",
                    "evidence_ids": EV(3) + EV(2),
                },
                {
                    "region": "lower full-width Table 3 drawing, entries 1-7, and footnotes a-f",
                    "finding": "Extracted all seven 1l optimization rows, preserving NMR versus parenthesized isolated yields, quench overrides, and 42% recovered 1l in entry 7.",
                    "evidence_ids": EV(3),
                },
                {
                    "region": "upper-right prose continuing into control studies",
                    "finding": "The prose describes no reaction for E-4a with I2 alone or BnSH alone and 18% E-3a with both; these were merged with their Scheme 2 arrows rather than duplicated. The 1a/BnSSBn/I2 result was linked to Eq. (2).",
                    "evidence_ids": EV(3) + EV(4) + EV(5),
                },
            ],
            "record_ids": table2 + table3 + scheme2[:3] + [RID("eq2_1a_bnssbn_i2")],
            "unresolved": [
                "Most table structures are substituent-defined and were not independently converted into verified stereochemical SMILES.",
                "Table 3 does not state the saturated Na2S2O3 volume.",
            ],
        },
        {
            "page": 4,
            "state": "attempted",
            "regions": [
                {
                    "region": "upper Table 4 drawing, entries 1-8, and footnotes a-e",
                    "finding": "Extracted all eight polysubstituted-allene scope rows; entry 3's 1.5-equiv I2 override was structured separately from the 1.2-equiv common condition.",
                    "evidence_ids": EV(4),
                },
                {
                    "region": "middle Scheme 2 five-arrow control matrix",
                    "finding": "Extracted five independent controls, including four no-reaction branches and the BnSH/I2 reduction branch (E-3a 18%, recovered E-4a 78%, BnSSBn 100%).",
                    "evidence_ids": EV(4) + EV(3),
                },
                {
                    "region": "bottom prose beneath Scheme 2",
                    "finding": "Prose classifies BnSSBn as only partially responsible and introduces the proposed mechanism; the cross-page Eq. (2) experiment was linked rather than duplicated.",
                    "evidence_ids": EV(4) + EV(3) + EV(5),
                },
            ],
            "record_ids": table4 + scheme2 + [RID("eq2_1a_bnssbn_i2")],
            "unresolved": [
                "Scheme 2 omits reaction scale, non-water agent amounts, workup, and yield measurement basis.",
                "The exact structures in Table 4 and Scheme 2 remain machine-unverified.",
            ],
        },
        {
            "page": 5,
            "state": "attempted",
            "regions": [
                {
                    "region": "upper-left Eq. (2)",
                    "finding": "Extracted 1a/BnSSBn/I2 with 2 equiv H2O in anhydrous MeCN at 5 °C for 2 h: E-3a 13%, E-4a 57%, and 25% recovered 1a.",
                    "evidence_ids": EV(5) + EV(3) + EV(4),
                },
                {
                    "region": "upper-right Eq. (3)",
                    "finding": "Extracted chirality-transfer experiment R-1g (99.4% ee) to (R)-E-3g in 78% yield and 98.5% ee at -20 °C for 48 min.",
                    "evidence_ids": EV(5),
                },
                {
                    "region": "middle-right Eq. (4)",
                    "finding": "Extracted m-CPBA oxidation of (R)-E-3g (98.0% ee) to (R)-E-4g in 83% yield and 96.9% ee; page 6 ORTEP evidence was linked to the same product record.",
                    "evidence_ids": EV(5) + EV(6),
                },
                {
                    "region": "lower Scheme 3",
                    "finding": "Classified the charged-intermediate/BnSH/H2O network as a proposed mechanism, not as a set of measured batch experiments.",
                    "evidence_ids": EV(5),
                },
            ],
            "record_ids": [
                RID("eq2_1a_bnssbn_i2"),
                RID("eq3_chiral_1g_iodohydroxylation"),
                RID("eq4_RE3g_oxidation"),
                RID("scheme3_proposed_mechanism"),
            ],
            "unresolved": [
                "Equations (2)-(4) omit some scale, reagent amount, workup, purification, or analytical-method details.",
                "Scheme 3 contains generic R groups and transient intermediates, so no unique verified structures are claimed.",
            ],
        },
        {
            "page": 6,
            "state": "attempted",
            "regions": [
                {
                    "region": "upper-left Figure 1 ORTEP",
                    "finding": "Figure 1 is structural characterization of (R)-E-4g, not a new reaction; it was linked to the Eq. (4) oxidation record.",
                    "evidence_ids": EV(6) + EV(5),
                },
                {
                    "region": "upper-right Table 5 entries 1-4 and footnotes a-c",
                    "finding": "Extracted four I2-loading/time isomerization entries independently with isolated yields and NMR E/Z ratios.",
                    "evidence_ids": EV(6),
                },
                {
                    "region": "middle-left Eq. (5)",
                    "finding": "Extracted Z-3a isomerization with 0.5 equiv I2 at 0 °C for 12 h to E/Z 4/96; no unsupported total yield was added.",
                    "evidence_ids": EV(6),
                },
                {
                    "region": "middle-right Scheme 4 three arrows",
                    "finding": "Extracted Sonogashira product 6 (90%), Suzuki product 7 (60%), and m-CPBA oxidation to E-4f (85%) as three separate experiments.",
                    "evidence_ids": EV(6),
                },
                {
                    "region": "lower conclusions",
                    "finding": "Conclusion-level scope and mechanism statements were treated as summaries and were not duplicated as experiments.",
                    "evidence_ids": EV(6),
                },
            ],
            "record_ids": [RID("eq4_RE3g_oxidation")] + table5 + [
                RID("eq5_Z3a_isomerization"),
                RID("scheme4_sonogashira_product6"),
                RID("scheme4_suzuki_product7"),
                RID("scheme4_E3f_oxidation_E4f"),
            ],
            "unresolved": [
                "Table 5 and Scheme 4 omit some reaction scales, component amounts, workup, and purification details.",
                "ORTEP linkage supports identity assignment but does not independently certify the machine-encoded structure fields.",
            ],
        },
    ],
}

out = Path(__file__).parents[1] / "coverage" / "pages_0001_0006.json"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(ledger, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"pages": len(ledger["pages"]), "output": str(out)}, ensure_ascii=False))
