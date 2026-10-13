import json
from pathlib import Path


DOC = "doc_34a38cb1c5b4d3e7"
BASE = Path(__file__).resolve().parents[1]
dataset = json.loads((BASE / "dataset.json").read_text())
known = {record["record_id"] for record in dataset["experiments"]}


def rid(suffix):
    value = f"{DOC}:{suffix}"
    if value not in known:
        raise KeyError(value)
    return value


def evid(page):
    return [f"{DOC}:page{page}:image", f"{DOC}:page{page}:text"]


t2 = {i: rid(f"table2_entry{i}_2{chr(96+i)}") for i in range(2, 17)}
scheme1_tos = rid("scheme1_tosylation_E-2o_to_E-4o")
scheme1_cl = rid("scheme1_chlorination_E-4o_to_E-3o")
isotopes = [rid("scheme3_1h_to_E-2h*"), rid("scheme3_1c_to_E-2c*"), rid("scheme3_1e_to_E-2e*")]
hot = [rid("table3_entry6_table4_entry1")] + [rid(f"table4_entry{i}_2{p}") for i, p in [(2, "m"), (3, "n"), (4, "o"), (5, "p")]]
chiral = [rid("scheme2_S-1b_to_S-E-2b"), rid("scheme2_S-1j_to_S-E-2j"), rid("scheme2_R-1o_to_R-E-2o")]

pages = [
    {
        "page": 7,
        "state": "attempted",
        "regions": [
            {
                "region": "upper-left continuation of section 4.3.2 and left-column sections 4.3.3-4.3.5",
                "finding": "The continuation supplies the isolated mass for E-2b; sections 4.3.3-4.3.5 give explicit reactant/reagent masses and amounts, solvent volumes, reaction times, product masses, and isolated yields for E-2c through E-2e. These details enrich the existing Table 2 rows rather than create duplicate batches.",
                "evidence_ids": evid(7),
            },
            {
                "region": "right-column sections 4.3.6-4.3.8",
                "finding": "Detailed preparations of E-2f, E-2g, and E-2h were reconciled with Table 2 entries 6-8; analytical spectra were retained as identity support, not additional experiments.",
                "evidence_ids": evid(7),
            },
            {
                "region": "lower-right opening of section 4.3.9",
                "finding": "The E-2i batch begins with the 1i/PhSeCl quantities, solvent volumes, and 10 min duration; its isolated outcome continues on page 8 and is represented once with cross-page evidence.",
                "evidence_ids": evid(7),
            },
        ],
        "record_ids": [t2[i] for i in range(2, 10)],
        "unresolved": [
            "Substrate and selenium-product structures remain unverified; fully named products retain null SMILES.",
            "The abbreviated procedures do not restate every General Procedure III workup operation or atmosphere.",
        ],
    },
    {
        "page": 8,
        "state": "attempted",
        "regions": [
            {
                "region": "upper-left continuation of section 4.3.9 and sections 4.3.10-4.3.11",
                "finding": "The E-2i product mass/yield and detailed E-2j/E-2k batches were merged into Table 2 entries 9-11 with explicit quantities and isolated product masses.",
                "evidence_ids": evid(8),
            },
            {
                "region": "lower-left and right-column sections 4.3.12-4.3.13",
                "finding": "The scaled 1l and 1m batches report both E-hydroxy products and Z-chloro byproducts, including isolated masses/yields and E/Z ratios. They enrich Table 2 entries 12-13; the 1l paragraph also supplies its silica-eluent range.",
                "evidence_ids": evid(8),
            },
        ],
        "record_ids": [t2[i] for i in range(9, 14)],
        "unresolved": [
            "All product/byproduct structures and E/Z assignments remain machine records requiring chemistry review.",
            "Atmosphere is not reported for these scope batches.",
        ],
    },
    {
        "page": 9,
        "state": "attempted",
        "regions": [
            {
                "region": "left column sections 4.3.14-4.3.15",
                "finding": "Scaled 1n and 1o batches provide explicit reagent quantities, solvent volumes, isolated E-product and Z-byproduct masses/yields, and E/Z ratios; these were merged into Table 2 entries 14-15.",
                "evidence_ids": evid(9),
            },
            {
                "region": "right-column section 4.3.16",
                "finding": "The 1p batch affords E-2p and Z-3p with separate isolated masses/yields and an 82:18 ratio; it enriches Table 2 entry 16.",
                "evidence_ids": evid(9),
            },
            {
                "region": "lower-right section 4.3.17.1 opening",
                "finding": "The tosylation E-2o to E-4o begins with the E-2o quantity and continues on page 10; one cross-page stage record is used.",
                "evidence_ids": evid(9),
            },
        ],
        "record_ids": [t2[14], t2[15], t2[16], scheme1_tos],
        "unresolved": [
            "Scope-product structures remain unverified.",
            "The tosylation is incomplete on page 9 alone and was reconciled with page 10.",
        ],
    },
    {
        "page": 10,
        "state": "attempted",
        "regions": [
            {
                "region": "upper-left continuation of section 4.3.17.1",
                "finding": "The tosylation record was completed with p-TsCl/DMAP quantities, split CH2Cl2 volumes, nitrogen atmosphere, 50 °C reflux for 2.5 h, chromatography, and E-4o mass/yield.",
                "evidence_ids": evid(10),
            },
            {
                "region": "lower-left section 4.3.17.2",
                "finding": "LiCl substitution of E-4o was retained as a distinct successive stage with exact quantities, 50 °C/29 h/N2 conditions, workup, chromatography, and E-3o mass/yield.",
                "evidence_ids": evid(10),
            },
            {
                "region": "right-column section 4.3.18",
                "finding": "The E-2h* isotope experiment was expanded into material/solvent drying, two independent pre-stirs, post-combination reaction, and purification steps with explicit quantities and 94.5% 18O incorporation. The scheme-arrow 45 min and detailed 10 min post-combination time are both preserved as a discrepancy.",
                "evidence_ids": evid(10),
            },
        ],
        "record_ids": [scheme1_tos, scheme1_cl, isotopes[0]],
        "unresolved": [
            "The Scheme 3 arrow time conflicts with the detailed post-combination duration and was not silently reconciled.",
            "E-4o, E-3o, and E-2h* structures remain unverified.",
        ],
    },
    {
        "page": 11,
        "state": "attempted",
        "regions": [
            {
                "region": "upper-left isotope-abundance equations and E-2h* calculation conclusion",
                "finding": "The numerical deconvolution supports the reported 94.5% 18O incorporation for the existing E-2h* record; equations were not treated as additional reaction experiments.",
                "evidence_ids": evid(11),
            },
            {
                "region": "lower-left section 4.3.19",
                "finding": "The E-2c* experiment supplies exact 1c/PhSeCl/H2-18O/anhydrous-MeCN quantities, 37 min duration, 126.0 mg/85% isolated outcome, and 88.4% incorporation; the later spectral simulation is analytical evidence, not a new batch.",
                "evidence_ids": evid(11),
            },
            {
                "region": "right-column section 4.3.20",
                "finding": "The E-2e* experiment supplies exact quantities, 41 min duration, 127.7 mg/85% isolated outcome, and 69.5% incorporation, resolving the product yield absent from the page-5 scheme.",
                "evidence_ids": evid(11),
            },
        ],
        "record_ids": isotopes,
        "unresolved": [
            "Sections 4.3.19-4.3.20 invoke the preceding procedure but do not restate its stage-specific drying, pre-stir, workup, or purification operations.",
            "All isotope-labeled structures remain unverified.",
        ],
    },
    {
        "page": 12,
        "state": "attempted",
        "regions": [
            {
                "region": "left-column sections 4.4.1-4.4.5",
                "finding": "Typical Procedure IV completes the merged Table 3 entry-6/Table 4 entry-1 record with operations and isolated mass; sections 4.4.2-4.4.5 enrich the four remaining Table 4 rows with exact quantities and product masses, including the separately isolated Z-3m byproduct.",
                "evidence_ids": evid(12),
            },
            {
                "region": "lower-left and upper-right sections 4.5.1-4.5.3",
                "finding": "The three optically active batches were reconciled with Scheme 2 and enriched with reactant/reagent masses and amounts, solvent volumes, isolated product masses/yields, and reported input/product ee values.",
                "evidence_ids": evid(12),
            },
            {
                "region": "right-column Acknowledgements, Supplementary data notice, and References opening",
                "finding": "Acknowledgements and cited prior literature were not converted into experiments. The notice states that online Supplementary data exist, but no SI file was explicitly provided or associated, so no SI content was imported.",
                "evidence_ids": evid(12),
            },
        ],
        "record_ids": hot + chiral,
        "unresolved": [
            "Typical Procedure IV prints mass/mmol assignments inconsistent with molecular-weight expectations and the table-level PhSeCl loading; source values were preserved without correction.",
            "SI association remains unestablished; structures and stereochemical assignments remain unverified.",
        ],
    },
]

coverage = {"document_id": DOC, "semantic_accuracy_verified": False, "pages": pages}
out = BASE / "coverage" / "pages_0007_0012.json"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

tasks_path = BASE / "tasks.json"
tasks = json.loads(tasks_path.read_text())
target_tasks = {f"{DOC}:page{page}:text" for page in range(7, 13)}
for task in tasks:
    if task.get("document_id") == DOC and task.get("task_id") in target_tasks:
        task["state"] = "attempted"
        task["reason"] = "Original page image and extracted text inspected; detailed procedures reconciled with existing table/scheme records."
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"pages": len(pages), "path": str(out), "tasks_attempted": 6}, ensure_ascii=False))
