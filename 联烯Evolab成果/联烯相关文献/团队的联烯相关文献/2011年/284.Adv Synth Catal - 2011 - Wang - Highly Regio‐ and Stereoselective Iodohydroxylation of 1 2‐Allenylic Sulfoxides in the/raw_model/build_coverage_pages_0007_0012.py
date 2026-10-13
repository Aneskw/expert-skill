"""Write the semantic coverage ledger for source-PDF pages 7--12."""
import json
from pathlib import Path


DOC = "doc_f68af135ec78d163"
RID = lambda suffix: f"{DOC}:{suffix}"
EV = lambda page: [f"{DOC}:page{page}:image", f"{DOC}:page{page}:text"]


ledger = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 7,
            "state": "attempted",
            "regions": [
                {
                    "region": "upper-left Experimental Section and Synthesis of the Starting Materials",
                    "finding": "The anhydrous-MeCN sentence is a general solvent-preparation note. Three distinct starting-material syntheses (1i, 1j, 1r) were extracted; 1i is fully procedural while 1j and 1r are abbreviated experiments with explicit missing details retained.",
                    "evidence_ids": EV(7),
                },
                {
                    "region": "upper-right through lower-right iodohydroxylation procedures for E-3a and E-3b",
                    "finding": "Detailed quantities, staged addition, workup, purification and component yields were merged into the existing Eq. (1) and Table 2 entry 2 records rather than duplicated.",
                    "evidence_ids": EV(7) + EV(1) + EV(3),
                },
                {
                    "region": "bottom-right abbreviated E-3c preparation",
                    "finding": "Exact charges and isolated E/Z/E-4c outcomes were merged into Table 2 entry 3; operations inherit the explicitly referenced E-3b procedure.",
                    "evidence_ids": EV(7) + EV(3),
                },
            ],
            "record_ids": [
                RID("experimental_starting_material_1i"),
                RID("experimental_starting_material_1j"),
                RID("experimental_starting_material_1r"),
                RID("eq1_1a_iodohydroxylation"),
                RID("table2_entry2_1b"),
                RID("table2_entry3_1c"),
            ],
            "unresolved": [
                "The 1j and 1r paragraphs omit some or all duration, atmosphere, solvent/temperature, and workup details; these were not inferred from the 1i procedure.",
                "The exact identity of the reagent printed only as 'sulfenyl chloride' was not expanded beyond the source label.",
            ],
        },
        {
            "page": 8,
            "state": "attempted",
            "regions": [
                {
                    "region": "upper-left continuation of E/Z-3c characterization and E-3d preparation",
                    "finding": "Characterization continuation was inspected; the E-3d batch charges and E/Z/E-4d isolated outcomes were merged into Table 2 entry 4.",
                    "evidence_ids": EV(8) + EV(7) + EV(3),
                },
                {
                    "region": "left column E-3e and E-3f preparations",
                    "finding": "Exact masses and isolated main/side-product outcomes were merged into Table 2 entries 5 and 6, retaining the page-7 typical procedure as operational evidence.",
                    "evidence_ids": EV(8) + EV(7) + EV(3),
                },
                {
                    "region": "right column E-3g through E-3i preparations",
                    "finding": "Three scope batches were reconciled with Table 2 entries 7-9; E-4 byproduct yields and the isolated Z-3i result were added without creating duplicate experiments.",
                    "evidence_ids": EV(8) + EV(7) + EV(3),
                },
                {
                    "region": "bottom-right E-3j preparation beginning and cross-page continuation",
                    "finding": "Charges and E/Z/E-4j outcomes were merged into Table 2 entry 10; characterization continues on page 9.",
                    "evidence_ids": EV(8) + EV(9) + EV(3),
                },
            ],
            "record_ids": [
                RID("table2_entry3_1c"), RID("table2_entry4_1d"), RID("table2_entry5_1e"),
                RID("table2_entry6_1f"), RID("table2_entry7_1g"), RID("table2_entry8_1h"),
                RID("table2_entry9_1i"), RID("table2_entry10_1j"),
            ],
            "unresolved": [
                "The abbreviated scope paragraphs rely on the page-7 E-3b procedure and do not independently restate every addition, workup, or purification operation.",
                "Spectral characterization was inspected for experiment identity but not modeled as reaction conditions or outcomes.",
            ],
        },
        {
            "page": 9,
            "state": "attempted",
            "regions": [
                {
                    "region": "top-left E/Z-3j characterization and E-3k preparation",
                    "finding": "The E-3j cross-page continuation was reconciled; E-3k exact charges and E-4k outcome were merged into Table 2 entry 11.",
                    "evidence_ids": EV(9) + EV(8) + EV(3),
                },
                {
                    "region": "middle-left detailed E-3l procedure",
                    "finding": "The detailed 1 min iodine addition plus 45 min stirring, workup, purification, masses and isolated yields were merged into Table 3 entry 5; the 46 min table duration is retained as the total.",
                    "evidence_ids": EV(9) + EV(3),
                },
                {
                    "region": "lower-left and right-column E-3m through E-3q preparations",
                    "finding": "Five Table 4 scope rows were enriched with exact masses and E-4 byproduct isolated yields, using the explicitly referenced E-3l procedure for shared operations.",
                    "evidence_ids": EV(9) + EV(4),
                },
                {
                    "region": "bottom-right beginning of E-3r preparation",
                    "finding": "The charge portion of Table 4 entry 6 was linked to its product/yield continuation on page 10.",
                    "evidence_ids": EV(9) + EV(10) + EV(4),
                },
            ],
            "record_ids": [
                RID("table2_entry10_1j"), RID("table2_entry11_1k"), RID("table3_entry5"),
                RID("table4_entry1_1m"), RID("table4_entry2_1n"), RID("table4_entry3_1o"),
                RID("table4_entry4_1p"), RID("table4_entry5_1q"), RID("table4_entry6_1r"),
            ],
            "unresolved": [
                "Most E-3m--E-3r paragraphs abbreviate the common workup/purification rather than restating it.",
                "Named/substituent-defined product structures remain unverified machine structures.",
            ],
        },
        {
            "page": 10,
            "state": "attempted",
            "regions": [
                {
                    "region": "upper-left continuation of E-3r and E-3s/E-3t preparations",
                    "finding": "Table 4 entries 6-8 were enriched with isolated masses and E-4 byproduct yields; E-3r was treated as one cross-page experiment, not two records.",
                    "evidence_ids": EV(10) + EV(9) + EV(4),
                },
                {
                    "region": "middle-left chiral (R)-E-3g preparation",
                    "finding": "Exact quantities, isolated mass, ee and HPLC basis were merged into the existing Eq. (3) chirality-transfer record.",
                    "evidence_ids": EV(10) + EV(5),
                },
                {
                    "region": "upper-right through middle-right E-4f, E-4g and (R)-E-4g oxidations",
                    "finding": "The E-4f and chiral E-4g procedures were merged into their existing Scheme 4/Eq. (4) records. The racemic E-3g to E-4g oxidation is a distinct batch and was added as one new record.",
                    "evidence_ids": EV(10) + EV(5) + EV(6),
                },
                {
                    "region": "lower-right Sonogashira product 6 procedure beginning",
                    "finding": "Detailed charges, nitrogen atmosphere, reaction and workup were merged into the existing Scheme 4 record; isolated mass/yield continues on page 11.",
                    "evidence_ids": EV(10) + EV(11) + EV(6),
                },
            ],
            "record_ids": [
                RID("table4_entry6_1r"), RID("table4_entry7_1s"), RID("table4_entry8_1t"),
                RID("eq3_chiral_1g_iodohydroxylation"), RID("scheme4_E3f_oxidation_E4f"),
                RID("experimental_E3g_oxidation_E4g"), RID("eq4_RE3g_oxidation"),
                RID("scheme4_sonogashira_product6"),
            ],
            "unresolved": [
                "The source prints CuI as 7.6 mg and 0.4 mmol in the Sonogashira batch; the internal inconsistency is preserved without correction.",
                "The abbreviated E-4g paragraphs inherit the preceding oxidation workup and do not restate every operation.",
            ],
        },
        {
            "page": 11,
            "state": "attempted",
            "regions": [
                {
                    "region": "top-left completion and characterization of Sonogashira product 6",
                    "finding": "The 57.2 mg, 90% isolated outcome was merged with the page-10 Sonogashira batch; characterization was inspected but not turned into reaction conditions.",
                    "evidence_ids": EV(11) + EV(10) + EV(6),
                },
                {
                    "region": "middle-left Suzuki product 7 procedure",
                    "finding": "Exact charges, 30 °C/nitrogen conditions, workup, purification and isolated mass were merged into the existing Scheme 4 record. The page-6 scheme's room-temperature label was retained as a source discrepancy.",
                    "evidence_ids": EV(11) + EV(6),
                },
                {
                    "region": "lower-left typical E-3a to Z-3a isomerization procedure",
                    "finding": "This batch matches Table 5 entry 3 (1.5 equiv I2, 15 h, 91%, E/Z 5/95); exact scale, workup and Z-3a isolated mass were merged rather than duplicated.",
                    "evidence_ids": EV(11) + EV(6),
                },
                {
                    "region": "bottom-left acknowledgements and full right-column references/crystal-data note",
                    "finding": "No additional batch experiment was present. The crystal-data paragraph characterizes E-4g and the reference list cites prior work; neither was counted as a new reaction.",
                    "evidence_ids": EV(11),
                },
            ],
            "record_ids": [
                RID("scheme4_sonogashira_product6"), RID("scheme4_suzuki_product7"), RID("table5_entry3"),
            ],
            "unresolved": [
                "Scheme 4 reports room temperature for product 7 while the detailed procedure reports 30 °C; both statements remain in the record.",
                "The isomerization section heading names Z-3a, but the explicit procedure starts from E-3a; the procedure text was prioritized and the mismatch logged.",
            ],
        },
        {
            "page": 12,
            "state": "attempted",
            "regions": [
                {
                    "region": "upper-left continuation of CCDC deposition note and upper-right references 10-11",
                    "finding": "The page contains only crystallographic-data availability text and bibliographic references to prior work; no current-paper experiment, arrow, table, footnote, or procedural batch was present.",
                    "evidence_ids": EV(12),
                },
                {
                    "region": "remaining blank page area",
                    "finding": "No chemical content or additional experiment appears in the remainder of the rendered source page.",
                    "evidence_ids": EV(12),
                },
            ],
            "record_ids": [],
            "unresolved": [
                "No reaction record is associated with this references-only page.",
            ],
        },
    ],
}

out = Path(__file__).parents[1] / "coverage" / "pages_0007_0012.json"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(ledger, ensure_ascii=False, indent=2) + "\n")

tasks_path = Path(__file__).parents[1] / "tasks.json"
tasks = json.loads(tasks_path.read_text())
for task in tasks:
    if task["document_id"] == DOC and any(task["evidence_id"] == f"{DOC}:page{p}:text" for p in range(7, 13)):
        task["state"] = "attempted"
        task["reason"] = "Page image and text inspected; detailed experimental records merged and pages 7-12 coverage ledger written."
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"pages": len(ledger["pages"]), "output": str(out)}, ensure_ascii=False))
