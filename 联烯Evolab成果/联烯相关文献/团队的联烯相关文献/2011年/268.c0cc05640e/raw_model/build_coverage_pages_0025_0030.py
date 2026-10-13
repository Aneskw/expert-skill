#!/usr/bin/env python3
"""Build the page 25-30 coverage ledger for doc_e77fa99a0ade23d1."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
records = json.loads((HERE / "records_pages_0025_0030.json").read_text())
DOC = "doc_e77fa99a0ade23d1"


def ids_for(page):
    token = f"{DOC}:page{page}:"
    return [r["record_id"] for r in records if any(e.startswith(token) for e in r["evidence_ids"])]


def region(page, name, finding):
    return {
        "region": name,
        "finding": finding,
        "evidence_ids": [f"{DOC}:page{page}:image", f"{DOC}:page{page}:text"],
    }


pages = [
    {
        "page": 25,
        "state": "attempted",
        "regions": [
            region(25, "upper-left and middle-left Schemes 146-148",
                   "The original image shows cited phomallenic-acid-C and marasin routes. Each visible coupling, bromide substitution, sulfoxide elimination, and DIBAL stage was recorded separately; unlabelled completion arrows remain partial rather than receiving invented conditions."),
            region(25, "lower-left Schemes 149-150",
                   "The iodine-elimination route and the lower-homologue allenyne route were separated by arrow. The low-yield Scheme 150 extension is retained with 24% yield and 15% ee and a failure/decomposition note from the adjacent review prose."),
            region(25, "right column Schemes 151-152 and Nemotin opening",
                   "The scorodonin sequences were split into coupling, deprotection, chloride formation, allene-forming elimination, and unlabelled completion stages. The visually reused label 448 was preserved independently in Schemes 150 and 151 without cross-scheme structure merging."),
        ],
        "record_ids": ids_for(25),
        "unresolved": [
            "Several total-synthesis completion arrows omit reagents, times, temperatures, and yields.",
            "Compound label 448 appears under two different-looking structures; source labels were preserved without assuming identity.",
            "Complex structures and axial configurations remain machine-unverified; original cited papers/SI were not supplied.",
        ],
    },
    {
        "page": 26,
        "state": "attempted",
        "regions": [
            region(26, "left and right review prose, Sections 6.4-6.7",
                   "The prose classifies Schemes 153-161 as cited total-synthesis literature examples and supplies route interpretation, including anti-SN2-prime substitution, oxymercuration/demercuration, hydride reduction, and the failed epimeric peridinin route. These are not new experiments by the Feature Article authors."),
            region(26, "bottom-left Scheme 153",
                   "Nemotin formation was split into the visible Negishi coupling and the subsequent AgNO3/NaCN-NH4Cl deprotection sequence, with the reported 64% and 71% yields retained separately."),
        ],
        "record_ids": ids_for(26),
        "unresolved": [
            "The compact Scheme 153 organometallic coupling partner is retained descriptively because its exact drawn identity is not machine-verified.",
            "Schemes 154-161 are discussed here but most drawings and quantitative arrow labels occur on pages 27-28.",
            "No SI was explicitly associated.",
        ],
    },
    {
        "page": 27,
        "state": "attempted",
        "regions": [
            region(27, "left column Schemes 154-158",
                   "Two Scheme 154 leaving-group rows were kept independent (Tris 65%, Ms 50%). Schemes 155-158 were transcribed as separate cited oxymercuration, bromoetherification, oxocarbenium allenylation, and LiCuBr2 substitution examples; proposed mercurio species 463 was not promoted to an isolated product."),
            region(27, "upper-right Scheme 159",
                   "The unlabelled glycidol-to-iodide sequence, the 99% allenyl-lithium substitution, and the 85% SmI2 conversion to histrionicotoxin were separated into three records."),
            region(27, "middle-right Scheme 160",
                   "The two 85% epoxide-opening/acetylation stages, 64% Stille coupling, 99% DIBAL reduction, and unlabelled peridinin completion were kept separate. The review's epimer/configuration-inversion warning is retained."),
            region(27, "lower-right Section 7.1 opening",
                   "Allene-based ligand prose introduces Scheme 162 on page 28. It was treated as cited prior work and linked to the page-28 drawing, not as an experiment performed in this review."),
        ],
        "record_ids": ids_for(27),
        "unresolved": [
            "Several total-synthesis arrows lack scale, atmosphere, workup, purification, or yield basis.",
            "The first Scheme 160 bromoallene intermediate is unnumbered; a descriptive participant is used only to preserve the separate 85% stage yield.",
            "The cited original procedures and SI are unavailable.",
        ],
    },
    {
        "page": 28,
        "state": "attempted",
        "regions": [
            region(28, "upper-left Scheme 161 and middle-left Scheme 162",
                   "Sonogashira coupling, DIBAL allene formation, and unlabelled paracentrone completion were separated. Scheme 162 was split into bromoallene formation, phosphine trapping, and the phosphine-oxide rearrangement; bracketed species 489 remains an intermediate."),
            region(28, "lower-left Scheme 163 and ligand-application prose",
                   "The three alternative propargylic-substitution routes were kept as separate condition records because their shared 93-97% yield and 33-87% ee ranges are not route-resolved. The SnCl4/meso-epoxide ligand application is a separate partial literature example with only 82-94% ee reported."),
            region(28, "upper-right Scheme 164 and middle-right Scheme 165 table",
                   "The organocuprate allenophane formation was recorded with all three 30-equivalent reagents. All four Scheme 165 rows were extracted independently with R/configuration, base, temperature, time, yield, and enantiomer ratio."),
            region(28, "lower-right Scheme 166",
                   "Cross-coupling, TBAF desilylation, the second low-yield coupling, and TCNE addition were separated. The second coupling partner is not redrawn at its arrow and remains explicitly unresolved rather than inferred."),
        ],
        "record_ids": ids_for(28),
        "unresolved": [
            "Scheme 163 aggregate yield/ee ranges cannot be assigned to any one of its three alternative routes.",
            "The identity and amount of the second Scheme 166 coupling partner are not explicit at that arrow.",
            "Complex stereochemical drawings remain machine-unverified.",
        ],
    },
    {
        "page": 29,
        "state": "attempted",
        "regions": [
            region(29, "upper-left Scheme 167",
                   "The three-step macrocycle protocol was split into 99% oxidative homodimerization, 65% deprotection, and 68% one-pot dimerization-cyclization. The separate oligomerization arrow to 509 was retained as a partial cited example with missing independent conditions and yield."),
            region(29, "lower-left conclusions",
                   "The conclusions contain general review statements and no additional paper-specific reaction arrow, table row, or batch experiment."),
            region(29, "right column acknowledgements and references opening",
                   "Funding, acknowledgements, and bibliographic entries were inspected and did not generate reaction records."),
        ],
        "record_ids": ids_for(29),
        "unresolved": [
            "Scheme 167 does not give the iteration count, product distribution, or yield for oligomers 509.",
            "Yield measurement bases and full original procedures are absent.",
        ],
    },
    {
        "page": 30,
        "state": "attempted",
        "regions": [
            region(30, "full two-column page of Notes and references 9-59",
                   "The original page image contains bibliography only: no scheme, table, reaction arrow, footnote condition row, or experimental procedure. No reaction record was created."),
        ],
        "record_ids": [],
        "unresolved": [
            "Bibliographic entries were not converted into experiments because the cited source articles themselves were not supplied in this task.",
        ],
    },
]

out = {"document_id": DOC, "semantic_accuracy_verified": False, "pages": pages}
target = HERE.parent / "coverage" / "pages_0025_0030.json"
target.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"output": str(target), "pages": len(pages), "records": len(records)}, ensure_ascii=False))
