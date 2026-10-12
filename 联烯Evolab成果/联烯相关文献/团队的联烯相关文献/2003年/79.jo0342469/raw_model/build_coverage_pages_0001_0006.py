#!/usr/bin/env python3
"""Write the required visual coverage ledger for PDF pages 1-6."""
import json
from pathlib import Path

DOC = "doc_70cf3d194c2f126f"
base = Path(__file__).resolve().parents[1]
dataset = json.loads((base / "dataset.json").read_text())
experiments = dataset["experiments"]


def ids_for(page):
    prefix = f"{DOC}:page{page}:"
    return [r["record_id"] for r in experiments if any(e.startswith(prefix) for e in r["evidence_ids"])]


def region(page, name, finding):
    return {"region": name, "finding": finding,
            "evidence_ids": [f"{DOC}:page{page}:image", f"{DOC}:page{page}:text"]}


pages = [
    {
        "page": 1, "state": "attempted",
        "regions": [
            region(1, "title and abstract", "Article scope and mechanistic conclusion only; no entry-level experiment or reaction arrow is specified."),
            region(1, "introduction, both columns", "Background and cited prior work; no experiment newly reported in this paper is instantiated on this page."),
            region(1, "references 1-12", "Bibliographic citations, not experimental records for this paper."),
        ],
        "record_ids": ids_for(1),
        "unresolved": ["No reaction drawing or complete experiment appears on page 1; abstract statements were not converted into fabricated records."],
    },
    {
        "page": 2, "state": "attempted",
        "regions": [
            region(2, "left column equations 1 and 2", "Equation 1 is a prior-literature generic transformation; equation 2 is a proposed general transformation marked with a question mark. They are classified as literature_example and general_scheme, respectively."),
            region(2, "Scheme 1", "Two-stage preparation of alpha-amino allenes 2a-c; detailed page-6 records for 2a are linked separately, while variants 1b-c/2b-c remain a generic scheme record."),
            region(2, "Scheme 2", "Two-stage preparation of 2d; merged with the detailed page-6 experiment rather than duplicated."),
            region(2, "Scheme 3", "Mitsunobu/hydrazinolysis/protection routes to alpha- and beta-amino allenes; generic variant groups and detailed page-6 5a/6a experiments are separated by record type."),
            region(2, "results prose at page bottom", "Narrative introduces Table 1 and scope results shown on later pages; no additional independent row is created here."),
        ],
        "record_ids": ids_for(2),
        "unresolved": ["Generic R-group structures, individual quantities, times, and yields are absent for many Scheme 1/3 variants.", "Equation 2 has no stated catalyst or outcome because it is conceptual."],
    },
    {
        "page": 3, "state": "attempted",
        "regions": [
            region(3, "Table 1 including reaction drawing, six rows, and footnotes", "Six independent optimization entries extracted; shared allyl-bromide equivalents, catalyst loading, room temperature, isolated-yield basis, and the entry-4 loading override are structured."),
            region(3, "Table 2 including reaction drawing, thirteen rows, and footnotes", "Thirteen independent substrate-scope entries extracted; staged heating/recovery and trans/cis footnotes are preserved."),
            region(3, "Table 3 including reaction drawing, fifteen rows, and footnotes", "Fifteen independent optimization entries extracted; NR rows, recovered starting material, catalyst-loading ranges, base equivalents, and both product yields are preserved."),
            region(3, "discussion prose and footnotes 17-21", "Narrative is used to interpret no-reaction and N-allylation outcomes; reference-only material and crystal data are not new reactions."),
        ],
        "record_ids": ids_for(3),
        "unresolved": ["Table 2 entry 11 reports 120 h but its visible footnote specifies only 48 h at room temperature plus 36 h at 50 °C; the missing 36 h stage is unresolved.", "Source labels are retained because substrate/product structures have not been independently verified and no SI was supplied."],
    },
    {
        "page": 4, "state": "attempted",
        "regions": [
            region(4, "Scheme 4, three arrows", "Three independent reactions of 2b with substituted allylic chlorides extracted, including combined yield, E/Z information, and 7q/7o product ratio."),
            region(4, "Table 4 including reaction drawing, fourteen rows, and footnotes", "Fourteen independent beta-amino-allene scope entries extracted; catalyst override, 50-55 °C override, staged heating, recovered starting material, and complex-mixture failure are retained."),
            region(4, "mechanistic considerations prose", "Narrative descriptions of proposed Pd(II) and Pd(0) routes support mechanism records whose drawings occur on page 5; they are not reported experiments."),
            region(4, "references and crystal data", "Reference citations and X-ray metadata are context, not separate reaction experiments."),
        ],
        "record_ids": ids_for(4),
        "unresolved": ["Table 4 entry 5 reports an unidentified complex mixture and no product yield.", "The product structures and stereochemical assignments remain unverified; no SI was supplied."],
    },
    {
        "page": 5, "state": "attempted",
        "regions": [
            region(5, "Scheme 5 synthetic sequence and key", "Seven precursor-preparation arrows are separate reported-experiment records; the two final coupling arrows are merged with Table 2 entries 12 and 13 to avoid duplication. Yields, ee values, optical rotations, and stated reagents/temperatures are preserved."),
            region(5, "Scheme 6", "Proposed Pd(II) pathway classified as mechanism, not as an experiment."),
            region(5, "Scheme 7", "Two proposed Pd(0) pathways classified together as a mechanism record, not as experiments."),
            region(5, "Scheme 8, three arrows", "Three stoichiometric palladium mechanistic experiments extracted independently with equivalents, time, temperature, combined yield, and product ratios."),
            region(5, "mechanistic discussion and conclusion", "Authors favor Pd(II) but do not completely exclude Pd(0); this qualification is retained without promoting either mechanism to an observed intermediate sequence."),
        ],
        "record_ids": ids_for(5),
        "unresolved": ["Scheme 5 omits most reagent quantities and reaction times; these remain missing.", "Scheme 8 gives mixture ratios but the component structures and E/Z distribution remain unverified."],
    },
    {
        "page": 6, "state": "attempted",
        "regions": [
            region(6, "left column 1a to allenyl bromide and allenyl bromide to 2a", "Two successive isolated experiments extracted separately with quantities, conditions, workup/purification where reported, and yields."),
            region(6, "left column preparation of 2d", "Multistage LDA/ZnCl2 rearrangement and diazomethane methylation extracted as one reported experiment with successive steps and a final isolated yield."),
            region(6, "left-to-right columns preparation of 5a", "Mitsunobu conversion of 4a to isolated phthalimide 5a extracted with quantities, overnight condition, workup, purification, and yield."),
            region(6, "right column preparation of 6a", "Hydrazinolysis, acid/base workup, and tosylation extracted as a multistep reported experiment with final isolated yield."),
            region(6, "right column preparations of (S)-2m and (R)-2n", "Detailed quantities enrich the corresponding Scheme 5 records; page-7 characterization is outside this coverage claim."),
        ],
        "record_ids": ids_for(6),
        "unresolved": ["The (R)-2n paragraph continues onto page 7; only reaction quantities and outcomes visible on page 6 and Scheme 5 are used here.", "Some reagent amounts, atmospheres, and chromatography details are absent and remain missing; no SI was associated."],
    },
]

ledger = {"document_id": DOC, "semantic_accuracy_verified": False, "pages": pages}
out = base / "coverage" / "pages_0001_0006.json"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(ledger, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"output": str(out), "pages": [p["page"] for p in pages]}, ensure_ascii=False))
