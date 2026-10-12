"""Write the required page-1--6 coverage ledger and mark those page tasks attempted."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / "runs" / "current"
DOC = "doc_f83285164919129a"


def ids(*suffixes):
    return [f"{DOC}:{suffix}" for suffix in suffixes]


def evidence(page):
    return [f"{DOC}:page{page}:text", f"{DOC}:page{page}:image"]


synth = ids(*[f"synthesis_racemic_1{x}" for x in "abcdefghijkl"])
screen = ids(*[f"table1_entry_{n}_enzyme_screen" for n in range(1, 7)])
scope = ids(*[f"kinetic_resolution_1{x}_30c" for x in "abcdefghijkl"])
large = ids("kinetic_resolution_1a_10g_scale")
table3 = ids(*[
    f"table3_entry_{n}_optimization" + ("_table4_entry_1" if n == 9 else "")
    for n in range(1, 10)
])
table4 = ids(*[f"table4_entry_{n}_loading_scope" for n in range(2, 22)])
downstream = ids(
    "agno3_cycloisomerization_1a_to_3a",
    "pdii_coupling_cyclization_1a_allyl_bromide",
    "pd0_coupling_cyclization_1a_iodobenzene",
)

pages = [
    {
        "page": 1,
        "state": "attempted",
        "regions": [
            {"region": "title, abstract, and keywords", "finding": "Article overview reports Novozym-435 kinetic resolution and a 10 g demonstration, but this region contains no independent detailed experiment; detailed records are linked to page 2.", "evidence_ids": evidence(1)},
            {"region": "Introduction and opening Results and Discussion", "finding": "Background and cited prior work are not treated as experiments from this paper; the final paragraph introduces Scheme 1, which is recorded from pages 2 and 4.", "evidence_ids": evidence(1)},
        ],
        "record_ids": [],
        "unresolved": ["No Supporting Information file was explicitly supplied or associated.", "The abstract-level claims are not used to fill details absent from the experimental records."],
    },
    {
        "page": 2,
        "state": "attempted",
        "regions": [
            {"region": "Scheme 1, upper left", "finding": "Two preparation arrows are present: SnCl2/NaI/aldehyde synthesis of racemic 1a-e and 1g-l, and LiAlH4 reduction to 1f. They are mapped to twelve individual experimental records using the page-4 procedures, not duplicated as generic schemes.", "evidence_ids": evidence(2)},
            {"region": "Table 1 and surrounding kinetic-resolution discussion", "finding": "Seven enzyme-screening rows were inspected. Entries 1-2 report no reaction; entries 3-6 are distinct optimization records; entry 7 is the same 96 h Novozym-435 experiment as Table 2 entry 1 and the page-4 typical procedure, so its evidence is merged into that record.", "evidence_ids": evidence(2)},
            {"region": "Table 2", "finding": "Twelve substrate-scope rows (1a-l) were transcribed independently with product-specific yields and ee values; shared footnotes provide 100 mg alcohol, 5 mL vinyl acetate, 70 mg Novozym-435, 30 °C, isolated-yield basis, and analytical basis.", "evidence_ids": evidence(2)},
            {"region": "Equation (1) and scale-up paragraph", "finding": "The 10.005 g/71 mmol scale experiment is a separate reported experiment with 47 h at 30 °C, workup, chromatographic gradient, two products, and product-specific yield/selectivity data.", "evidence_ids": evidence(2)},
            {"region": "Chinese abstract", "finding": "Translation/summary of the article; no additional independent reaction record was created.", "evidence_ids": evidence(2)},
        ],
        "record_ids": synth + screen + scope + large,
        "unresolved": ["The scale-up prose gives 4.622 g alcohol while Equation (1) prints 4.662 g; both values are retained.", "All allene/allene-acetate SMILES remain unverified connectivity candidates and do not certify axial configurations.", "No Supporting Information association was inferred."],
    },
    {
        "page": 3,
        "state": "attempted",
        "regions": [
            {"region": "Table 3", "finding": "Nine independent 1a optimization rows were transcribed. Footnote values stating that the opposite enantiomer was not detected by GC remain qualitative; entry 9 is merged with the identical Table 4 entry 1.", "evidence_ids": evidence(3)},
            {"region": "Table 4", "finding": "Twenty-one loading/concentration rows were inspected; entry 1 is merged with Table 3 entry 9 and entries 2-21 remain separate optimization records.", "evidence_ids": evidence(3)},
            {"region": "Scheme 2", "finding": "Three distinct transformations of (S)-1a (AgNO3 cycloisomerization, PdII/allyl-bromide coupling cyclization, and Pd0/PhI coupling cyclization) are mapped to the full page-6 procedures.", "evidence_ids": evidence(3)},
            {"region": "conclusion and Experimental Section opening", "finding": "Conclusion and general analytical-instrument text contain no additional reaction event. The starting-material subsection begins here and continues on page 4.", "evidence_ids": evidence(3)},
        ],
        "record_ids": table3 + table4 + downstream,
        "unresolved": ["Compound loading units mL g^-1 and mg g^-1 are preserved verbatim because the controlled quantity-unit list does not support them.", "The Table 4 prose describes a 1.0 g scale, but exact per-row reagent volumes/masses were not calculated by inference.", "No Supporting Information association was inferred."],
    },
    {
        "page": 4,
        "state": "attempted",
        "regions": [
            {"region": "left column, racemic 2,3-allenol preparations", "finding": "Individual preparations of 1a-e and 1g-l plus the LiAlH4 reduction to 1f were inventoried as twelve distinct records; the 1a and 1f typical procedures retain steps, workup, purification, quantities, times, and temperatures.", "evidence_ids": evidence(4)},
            {"region": "right/lower columns, kinetic-resolution procedures", "finding": "The 1a, 1b, and 1c procedures and the start of 1d were linked to the matching Table 2 records; product masses, yields, and ee values were merged instead of creating duplicates.", "evidence_ids": evidence(4)},
            {"region": "spectroscopic characterization blocks", "finding": "NMR/IR/MS/HRMS and chromatographic assay details characterize products and do not constitute additional reaction arrows; only the reaction-relevant ee measurement basis was retained.", "evidence_ids": evidence(4)},
        ],
        "record_ids": synth + ids("kinetic_resolution_1a_30c", "kinetic_resolution_1b_30c", "kinetic_resolution_1c_30c", "kinetic_resolution_1d_30c"),
        "unresolved": ["The source calls the aldehyde for 1i acetaldehyde although the product is the ethyl-substituted hexa-4,5-dien-3-ol.", "The source names 1-bromodec-2-yne for pentyl product 1k, creating an internal chain-length inconsistency.", "The 1d characterization continues on page 5."],
    },
    {
        "page": 5,
        "state": "attempted",
        "regions": [
            {"region": "continuation of 1d and procedures for 1e-1j", "finding": "Kinetic-resolution procedures for 1d, 1e, 1f, 1g, 1h, 1i, and the start of 1j were linked to their Table 2 records with product-specific mass, yield, and ee data.", "evidence_ids": evidence(5)},
            {"region": "analytical characterization", "finding": "Product characterization and GC/HPLC conditions support identity/ee reporting but are not separate synthetic experiments.", "evidence_ids": evidence(5)},
        ],
        "record_ids": ids(*[f"kinetic_resolution_1{x}_30c" for x in "defghij"]),
        "unresolved": ["The 1j acetate ee and remaining characterization continue on page 6.", "All product structures remain machine candidates with structure_verified=false."],
    },
    {
        "page": 6,
        "state": "attempted",
        "regions": [
            {"region": "left column, completion of 1j and procedures for 1k-1l", "finding": "The 1j record is completed and the 1k and 1l kinetic resolutions are linked to their Table 2 rows; no duplicate records were added.", "evidence_ids": evidence(6)},
            {"region": "AgNO3-catalyzed cycloisomerization", "finding": "A full reported experiment converts (S)-1a to labeled product (S)-3a with reagent/solvent quantities, nitrogen, reflux for 8 h, workup, purification, 84 mg, 60% yield, and >99% ee.", "evidence_ids": evidence(6)},
            {"region": "PdII-catalyzed coupling cyclization with allyl bromide", "finding": "A distinct room-temperature experiment gives (S)-4a; time is reported only as completion by TLC, and the 122 mg/68%/>99% ee product data are retained.", "evidence_ids": evidence(6)},
            {"region": "Pd0-catalyzed coupling cyclization with PhI", "finding": "A distinct 75-80 °C, 18 h experiment gives (S,S)-5a with 127 mg, 59% yield, 99.4% ee, and Scheme-2 d.r. 35:1.", "evidence_ids": evidence(6)},
            {"region": "Acknowledgements and references 1-4", "finding": "No new experiment from this paper is reported in this region; cited literature is not reclassified as current-paper data.", "evidence_ids": evidence(6)},
        ],
        "record_ids": ids("kinetic_resolution_1j_30c", "kinetic_resolution_1k_30c", "kinetic_resolution_1l_30c") + downstream,
        "unresolved": ["The cycloisomerization heading names an (R) product while the source compound label is (S)-3a; the conflict is preserved.", "The PdII experiment gives only a qualitative reaction time ('until complete by TLC').", "Downstream product SMILES are left null pending structure-aware stereochemical review."],
    },
]

coverage = {"document_id": DOC, "semantic_accuracy_verified": False, "pages": pages}
assert [p["page"] for p in pages] == [1, 2, 3, 4, 5, 6]
assert all(p["regions"] for p in pages)

dataset = json.loads((RUN / "dataset.json").read_text())
known = {r["record_id"] for r in dataset["experiments"]}
referenced = {rid for page in pages for rid in page["record_ids"]}
assert referenced <= known, sorted(referenced - known)
assert len(known) == 63
assert referenced == known, sorted(known - referenced)

dest = RUN / "coverage" / "pages_0001_0006.json"
dest.parent.mkdir(parents=True, exist_ok=True)
dest.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

tasks_path = RUN / "tasks.json"
tasks = json.loads(tasks_path.read_text())
for task in tasks:
    if task["document_id"] == DOC and task["task_id"] in {f"{DOC}:page{p}:text" for p in range(1, 7)}:
        task["state"] = "attempted"
        task["visual_evidence_id"] = task["task_id"].replace(":text", ":image")
        task["reason"] = "Original page image inspected; experiment regions mapped in coverage/pages_0001_0006.json."
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")
print(f"wrote {dest}; {len(referenced)} unique record ids covered")
