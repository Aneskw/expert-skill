import json
from pathlib import Path

DOC = "doc_34a38cb1c5b4d3e7"
BASE = Path(__file__).resolve().parents[1]
dataset = json.loads((BASE / "dataset.json").read_text())
known = {r["record_id"] for r in dataset["experiments"]}


def rid(suffix):
    value = f"{DOC}:{suffix}"
    if value not in known:
        raise KeyError(value)
    return value


def evid(page):
    return [f"{DOC}:page{page}:image", f"{DOC}:page{page}:text"]


t1 = [rid(f"table1_entry{i}") for i in range(1, 15)]
t2 = [rid(f"table2_entry{i}_{p}") for i, p in enumerate(
    ["2a", "2b", "2c", "2d", "2e", "2f", "2g", "2h", "2i", "2j", "2k", "2l", "2m", "2n", "2o", "2p"], 1
)]
t3 = [rid(f"table3_entry{i}") for i in range(1, 6)] + [rid("table3_entry6_table4_entry1")]
t4 = [rid(f"table4_entry{i}_{p}") for i, p in [(2, "2m"), (3, "2n"), (4, "2o"), (5, "2p")]]
scheme1 = [rid("scheme1_tosylation_E-2o_to_E-4o"), rid("scheme1_chlorination_E-4o_to_E-3o")]
scheme2 = [rid("scheme2_S-1b_to_S-E-2b"), rid("scheme2_S-1j_to_S-E-2j"), rid("scheme2_R-1o_to_R-E-2o")]
scheme3 = [rid("scheme3_1h_to_E-2h*"), rid("scheme3_1c_to_E-2c*"), rid("scheme3_1e_to_E-2e*")]
mechanisms = [rid("scheme4_proposed_mechanism"), rid("scheme5_chirality_transfer_rationale")]

pages = [
    {
        "page": 1,
        "state": "attempted",
        "regions": [
            {
                "region": "title, abstract, and Introduction across both columns",
                "finding": "The abstract states the paper-level selenohydroxylation claim; the Introduction summarizes cited prior halohydroxylation/selenolactonization work. These broad claims and literature examples were not converted into duplicate batch experiments.",
                "evidence_ids": evid(1),
            },
            {
                "region": "lower-right Results and Discussion opening",
                "finding": "Narrative screening results map to Table 1 entries 1-14 on page 2, including the aqueous-acetone no-reaction result and the 1.2-equiv PhSeCl override. The rows are represented independently and linked to page 1 only as supporting prose.",
                "evidence_ids": evid(1),
            },
        ],
        "record_ids": t1,
        "unresolved": [
            "Page 1 contains no complete table image; row-level values were checked against the page-2 original image.",
            "Cited prior work was classified as context rather than this paper's reported batches.",
        ],
    },
    {
        "page": 2,
        "state": "attempted",
        "regions": [
            {
                "region": "upper-left Table 1, reaction drawing, and footnotes",
                "finding": "Fourteen independent solvent/time optimization rows were extracted. Entry 10 uses the footnoted 1.2 equiv PhSeCl; entry 11 preserves 0% NMR product yield and 91% recovered 1a as distinct outcome categories.",
                "evidence_ids": evid(2),
            },
            {
                "region": "lower-left Table 2, reaction drawing, and footnotes",
                "finding": "Sixteen independent substrate-scope rows were extracted with shared quantities, times, isolated E-product yields, and the footnoted Z-chloride byproduct yields for entries 12-16.",
                "evidence_ids": evid(2),
            },
            {
                "region": "lower-right Scheme 1 and adjacent discussion",
                "finding": "The tosylation E-2o to E-4o (86%) and LiCl substitution E-4o to E-3o (60%) were represented as two successive experiments. The NOE drawing of Z-3o is structural comparison evidence, not an additional synthesis.",
                "evidence_ids": evid(2),
            },
            {
                "region": "upper-right Figure 1 and surrounding prose",
                "finding": "ORTEP Figure 1 establishes the reported regio-/stereochemical assignment of E-2b but is not a separate reaction experiment.",
                "evidence_ids": evid(2),
            },
        ],
        "record_ids": t1 + t2 + scheme1,
        "unresolved": [
            "Allene and selenium-product SMILES remain unverified; labels and original drawings are retained.",
            "Scheme 1 on this page omits quantities, duration, atmosphere, workup, and purification.",
        ],
    },
    {
        "page": 3,
        "state": "attempted",
        "regions": [
            {
                "region": "upper-left Table 3 and footnotes",
                "finding": "Six independent 1l optimization rows were extracted with solvent ratio, temperature, time, NMR yield, and crude E-2l/Z-3l ratio. Table 3 entry 6 is the same 70 °C batch repeated as Table 4 entry 1 and was merged rather than duplicated.",
                "evidence_ids": evid(3),
            },
            {
                "region": "lower-left Table 4 and footnotes",
                "finding": "Entries 2-5 were extracted independently; footnote b overrides the shared solvent ratio to 1/1 for entries 2 and 4. Entry 1 is linked to the merged Table 3 entry-6 record.",
                "evidence_ids": evid(3),
            },
            {
                "region": "upper-right Scheme 2",
                "finding": "Three optically active selenohydroxylation experiments were extracted with starting/product ee, time, temperature, solvent ratio, and isolated yield.",
                "evidence_ids": evid(3),
            },
            {
                "region": "middle-left isotope/MS and mechanism discussion; lower-right Figure 2",
                "finding": "The prose supports the three Scheme 3 isotope experiments and classifies Schemes 4/5 as proposed mechanisms. Figure 2 is an ORTEP assignment for S-E-2b, not an additional batch.",
                "evidence_ids": evid(3),
            },
        ],
        "record_ids": t3 + t4 + scheme2 + scheme3 + mechanisms,
        "unresolved": [
            "Tables 3 and 4 omit participant amounts and workup details.",
            "The mechanistic alternatives are explicitly not excluded by the authors and remain proposed, not verified.",
        ],
    },
    {
        "page": 4,
        "state": "attempted",
        "regions": [
            {
                "region": "left Figure 3 panels a-c",
                "finding": "ESI-MS/SIM-MS/MS plots for E-2h show the precursor near m/z 491 and daughter near m/z 473; this analytical evidence was linked to the existing Table 2 entry-8 experiment rather than made into a reaction record.",
                "evidence_ids": evid(4),
            },
            {
                "region": "right Figure 4 panels a-c",
                "finding": "ESI-MS/SIM-MS/MS plots for E-2h* show the labeled precursor near m/z 493 and daughter near m/z 475; this was linked to the Scheme 3 isotope record.",
                "evidence_ids": evid(4),
            },
            {
                "region": "lower-right section 4.1.1 opening",
                "finding": "General Procedure I begins the 1j preparation with starting alcohol identity and amount; the batch continues on page 5 and is represented once with cross-page evidence.",
                "evidence_ids": evid(4),
            },
        ],
        "record_ids": [t2[7], scheme3[0], rid("section4.1.1_prepare_1j")],
        "unresolved": [
            "Mass-spectral structure annotations were not converted to verified SMILES.",
            "The 1j procedure is incomplete on page 4 alone and was reconciled with page 5.",
        ],
    },
    {
        "page": 5,
        "state": "attempted",
        "regions": [
            {
                "region": "upper-left Scheme 3",
                "finding": "Three H2-18O experiments (1h, 1c, 1e) were extracted with 1.5 equiv PhSeCl, 20/1 CH3CN/H2-18O, room-temperature times, displayed yields where present, and isotope incorporation. The page-5 scheme does not display a yield for E-2e*, so it remains missing.",
                "evidence_ids": evid(5),
            },
            {
                "region": "left column continuation of 4.1.1 and section 4.1.2",
                "finding": "The cross-page General Procedure I batch for 1j and the reflux preparation of 1e were extracted with explicit quantities, operations, times, workup/purification where stated, product masses, and isolated yields.",
                "evidence_ids": evid(5),
            },
            {
                "region": "right column sections 4.1.3-4.1.5",
                "finding": "Preparations of 1g and 1k were extracted; the preparation of 1p begins here and its product mass/yield continue on page 6, so one cross-page record was used.",
                "evidence_ids": evid(5),
            },
            {
                "region": "bottom Schemes 4 and 5",
                "finding": "Both generic R-group arrow sequences were classified as proposed mechanism/rationale records, not experimental batches.",
                "evidence_ids": evid(5),
            },
        ],
        "record_ids": scheme3 + [rid("section4.1.1_prepare_1j"), rid("section4.1.2_prepare_1e"),
                                  rid("section4.1.3_prepare_1g"), rid("section4.1.4_prepare_1k"),
                                  rid("section4.1.5_prepare_1p")] + mechanisms,
        "unresolved": [
            "Abbreviated General Procedure I derivatives do not restate every temperature, workup, or purification detail.",
            "E-2e* product yield is absent from the page-5 scheme and was not imported from uncovered later pages.",
        ],
    },
    {
        "page": 6,
        "state": "attempted",
        "regions": [
            {
                "region": "top-left continuation of section 4.1.5",
                "finding": "The product mass 2.3521 g and 47% isolated yield complete the cross-page preparation of 1p.",
                "evidence_ids": evid(6),
            },
            {
                "region": "left column section 4.2.1-4.2.3",
                "finding": "General Procedure II preparation of 1a and abbreviated preparations of S-1j and 1l were extracted. The 1l starting material's stated 95% purity/THF contamination was preserved.",
                "evidence_ids": evid(6),
            },
            {
                "region": "right column sections 4.2.4-4.2.5 and 4.2 comparison note",
                "finding": "Preparations of 1o and R-1o were extracted. The explicitly separate General Procedure I comparison leading to only 60% ee R-1o from 99% ee alcohol was retained as its own partial experiment.",
                "evidence_ids": evid(6),
            },
            {
                "region": "right column section 4.3.1 and start of 4.3.2",
                "finding": "The detailed General Procedure III batch for E-2a was merged into Table 2 entry 1 with quantities, workup, product mass, and yield. The opening quantities for E-2b were merged into Table 2 entry 2; its continuation beyond page 6 was not claimed as covered.",
                "evidence_ids": evid(6),
            },
        ],
        "record_ids": [rid("section4.1.5_prepare_1p"), rid("section4.2.1_prepare_1a"),
                       rid("section4.2.2_prepare_S-1j"), rid("section4.2.3_prepare_1l"),
                       rid("section4.2.4_prepare_1o"), rid("section4.2.5_prepare_R-1o"),
                       rid("section4.2_alternative_GP-I_R-1o"), t2[0], t2[1]],
        "unresolved": [
            "The abbreviated General Procedure II preparations do not restate all stage temperatures and workups.",
            "Sections 4.3.2 and later continue beyond page 6; only visible page-6 facts and the already extracted page-2 table outcomes were used.",
            "Product ee is not explicitly quantified in the page-6 preparation paragraphs for S-1j or R-1o.",
        ],
    },
]

coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": pages,
}
out = BASE / "coverage" / "pages_0001_0006.json"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")
tasks_path = BASE / "tasks.json"
tasks = json.loads(tasks_path.read_text())
for task in tasks:
    if task.get("document_id") == DOC and task.get("task_id") in {
        f"{DOC}:page{page}:text" for page in range(1, 7)
    }:
        task["state"] = "attempted"
        task["reason"] = "Original page image and extracted text inspected; experiments reconciled into evidence-linked records."
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"pages": len(pages), "path": str(out), "tasks_attempted": 6}, ensure_ascii=False))
