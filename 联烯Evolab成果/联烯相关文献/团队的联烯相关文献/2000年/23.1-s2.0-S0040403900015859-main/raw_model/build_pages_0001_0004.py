#!/usr/bin/env python3
"""Build evidence-linked records for doc_f51203bb157640ef, PDF pages 1-4."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "runs/current/raw_model/records_pages_0001_0004.json"
COVERAGE = ROOT / "runs/current/coverage/pages_0001_0004.json"
TASKS = ROOT / "runs/current/tasks.json"
DOC = "doc_f51203bb157640ef"


def ev(page, kind="image"):
    return f"{DOC}:page{page}:{kind}"


def fact(value, evidence=()):
    return {
        "value": value,
        "evidence_ids": list(evidence) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def field(name, value, evidence=()):
    return {"name": name, "fact": fact(value, evidence)}


def participant(entity_id, role, label, name, evidence, amounts=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence) if name is not None else fact(None),
        "smiles": fact(None),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": amounts or [],
    }


def record(suffix, kind, evidence, participants=None, steps=None, outcomes=None,
           notes=None, unresolved=None):
    return {
        "record_id": f"{DOC}:{suffix}",
        "document_id": DOC,
        "source_reaction_id": suffix,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": list(dict.fromkeys(evidence)),
        "participants": participants or [],
        "steps": steps or [],
        "outcomes": outcomes or [],
        "notes": [fact(x, evidence) for x in (notes or [])],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved or [],
        },
    }


def simple_step(step_id, participant_ids, conditions):
    return {
        "step_id": step_id,
        "participant_ids": participant_ids,
        "conditions": conditions,
    }


P2 = [ev(2, "image"), ev(2, "text")]
P3 = [ev(3, "image"), ev(3, "text")]
P4 = [ev(4, "image"), ev(4, "text")]
records = []

# Scheme 1 describes the authors' earlier Pd(0) work, not a current-paper run.
records.append(record(
    "scheme1_prior_pd0_selectivity", "literature_example", P2,
    participants=[
        participant("s1_allenol", "reactant", "generic 2,3-allenol", None, P2),
        participant("s1_halide", "reactant", "R3X", "organic halide", P2),
        participant("s1_pd0", "catalyst", "Pd(0)", "palladium(0) catalyst", P2),
        participant("s1_oxirane", "product", "Path A product", "vinylic oxirane", P2),
        participant("s1_dhf", "product", "Path B product", "2,5-dihydrofuran", P2),
    ],
    outcomes=[
        field("path_A_vinylic_oxirane_formed", True, P2),
        field("path_B_2_5_dihydrofuran_observed", False, P2),
    ],
    notes=["Scheme 1 and adjacent prose explicitly describe previous Pd(0)-catalyzed work."],
    unresolved=["Generic R groups and the individual prior-work experiments are not specified locally.",
                "No local yield, scale, time, solvent, workup, or purification is reported."],
))
records.append(record(
    "scheme1_proposed_paths", "mechanism", P2,
    participants=[participant("s1m_allenol", "reactant", "generic 2,3-allenol", None, P2)],
    outcomes=[field("observed_path", "Path A", P2), field("unobserved_path", "Path B", P2)],
    notes=["Scheme 1 depicts alternative oxygen-attack paths A and B around a cationic palladium-associated allene."],
    unresolved=["The depicted palladium species is a mechanistic proposal, not an isolated intermediate.",
                "Generic substituents R1-R3 and X preclude a unique structure assignment."],
))


def screen_record(suffix, halide_label, halide_name, catalyst_label, catalyst_name,
                  catalyst_amount, outcomes, notes, unresolved, extra_conditions=None):
    evidence = P2
    parts = [
        participant("allenol_1a", "reactant", "1a", "3-(n-butyl)-3,4-pentadien-2-ol", evidence),
        participant("allylic_halide", "reactant", halide_label, halide_name, evidence),
        participant("catalyst", "catalyst", catalyst_label, catalyst_name, evidence,
                    [field("loading", catalyst_amount, evidence)] if catalyst_amount is not None else []),
        participant("product_3a", "product", "3a", "2-methyl-3-(n-butyl)-4-allyl-2,5-dihydrofuran", evidence),
    ]
    conditions = extra_conditions or []
    return record(suffix, "optimization_entry", evidence, parts,
                  [simple_step("reaction", [p["entity_id"] for p in parts], conditions)],
                  outcomes, notes, unresolved)


records.append(screen_record(
    "prose_screen_1a_allyl_bromide_74pct", "allyl bromide", "allyl bromide",
    "PdCl2", "palladium(II) chloride", {"number": 5, "unit": "mol%"},
    [field("yield", {"number": 74, "unit": "%"}, P2)],
    ["The prose describes this as an observed result after trial and error."],
    ["Reaction time, scale, concentration, atmosphere, yield basis, workup, and purification are not stated in this sentence.",
     "Relationship to Table 1 entry 1 (76% after 18.5 h under nominally matching conditions) is unresolved."],
    [field("allyl_bromide_amount", {"number": 5, "unit": "equiv"}, P2),
     field("solvent", "DMA", P2), field("temperature", "rt", P2)],
))
records.append(screen_record(
    "prose_screen_less_than_5eq_allyl_bromide", "allyl bromide", "allyl bromide",
    "PdCl2", "palladium(II) chloride", None,
    [field("relative_yield", "lower yields than the 5 equiv allyl bromide reaction", P2)],
    ["The exact amount below 5 equivalents and numerical yield are not reported."],
    ["Exact allyl bromide amount, catalyst loading, reaction time, scale, concentration, atmosphere, workup, purification, and numerical yield are missing."],
    [field("allyl_bromide_amount", "less than 5 equiv", P2), field("solvent", "DMA", P2)],
))
records.append(screen_record(
    "prose_screen_allyl_chloride_51pct", "allyl chloride", "allyl chloride",
    "PdCl2", "palladium(II) chloride", None,
    [field("yield", {"number": 51, "unit": "%"}, P2)],
    ["Allyl chloride was used instead of allyl bromide in the surrounding optimization discussion."],
    ["Exact allyl chloride amount, catalyst loading, reaction time, scale, concentration, atmosphere, yield basis, workup, and purification are not restated."],
    [field("solvent", "DMA", P2), field("temperature", "rt", P2)],
))
records.append(screen_record(
    "prose_screen_pdcl2_1molpct", "allyl bromide", "allyl bromide",
    "PdCl2", "palladium(II) chloride", {"number": 1, "unit": "mol%"},
    [field("yield", {"number": 65, "unit": "%"}, P2)],
    ["The prose explicitly states 5 equivalents of allyl bromide and 1 mol% PdCl2."],
    ["Reaction time, scale, concentration, atmosphere, yield basis, workup, and purification are not reported for this screening result."],
    [field("allyl_bromide_amount", {"number": 5, "unit": "equiv"}, P2),
     field("solvent", "DMA", P2), field("temperature", "rt", P2)],
))

for suffix, label, name in [
    ("prose_screen_pdoac2_effective", "Pd(OAc)2", "palladium(II) acetate"),
    ("prose_screen_pdcl2_mecn2_effective", "PdCl2(CH3CN)2", "bis(acetonitrile)palladium(II) dichloride"),
    ("prose_screen_allylpalladium_chloride_dimer_effective", "[(pi-C3H5)PdCl]2", "allylpalladium chloride dimer"),
]:
    records.append(screen_record(
        suffix, "allyl bromide", "allyl bromide", label, name, None,
        [field("qualitative_result", "effective for this transformation", P2)],
        ["The catalyst is listed among palladium catalysts tested and found effective."],
        ["Catalyst loading, exact charges, time, numerical yield, yield basis, concentration, atmosphere, workup, and purification are not separately reported."],
        [],
    ))

# A substituted allylic-halide failure/complex outcome reported outside Table 1.
records.append(record(
    "prose_1i_3phenyl2propenyl_bromide_complicated", "optimization_entry", P2 + P3,
    participants=[
        participant("allenol_1i", "reactant", "1i", "2,3-allenol 1i (R1=CH3, R2=CH3, R3=Ph)", P2 + P3,
                    [field("amount", {"number": 1, "unit": "mmol"}, P3)]),
        participant("cinnamyl_bromide", "reactant", "3-phenyl-2-propenyl bromide", "3-phenyl-2-propenyl bromide", P2,
                    [field("amount", {"number": 5, "unit": "mmol"}, P3)]),
        participant("pdcl2", "catalyst", "PdCl2", "palladium(II) chloride", P2 + P3,
                    [field("amount", {"number": 0.05, "unit": "mmol"}, P3), field("loading", {"number": 5, "unit": "mol%"}, P3)]),
        participant("dma", "solvent", "DMA", "N,N-dimethylacetamide", P2 + P3,
                    [field("volume", {"number": 6, "unit": "mL"}, P3)]),
    ],
    steps=[simple_step("reaction", ["allenol_1i", "cinnamyl_bromide", "pdcl2", "dma"],
                       [field("temperature", "rt", P2 + P3)])],
    outcomes=[field("result", "reaction was complicated", P2)],
    notes=["The paper states that this screening used the standard reaction conditions."],
    unresolved=["Reaction time, product identities, product distribution, numerical yields, detection limits, atmosphere, workup, and purification are not reported."],
))

table_rows = [
    # entry, substrate, R1, R2, R3, halide, R4, time, yield, product
    (1, "1a", "CH3", "H", "n-C4H9", "2a", "H", 18.5, 76, "3a"),
    (2, "1b", "n-C4H9", "H", "n-C4H9", "2a", "H", 10.5, 81, "3b"),
    (3, "1c", "Ph", "H", "n-C4H9", "2a", "H", 21, 81, "3c"),
    (4, "1d", "CH3", "H", "CH3", "2a", "H", 3.5, 71, "3d"),
    (5, "1e", "n-C4H9", "H", "C3H5 (allyl)", "2a", "H", 2, 64, "3e"),
    (6, "1f", "CH3", "H", "PhCH2", "2a", "H", 18.5, 61, "3f"),
    (7, "1g", "n-C4H9", "H", "Ph", "2a", "H", 14.5, 68, "3g"),
    (8, "1h", "Ph", "H", "Ph", "2a", "H", 14.5, 60, "3h"),
    (9, "1i", "CH3", "CH3", "Ph", "2a", "H", 9, 86, "3i"),
    (10, "1j", "CH3", "CH3", "n-C4H9", "2a", "H", 23, 57, "3j"),
    (11, "1i", "CH3", "CH3", "Ph", "2b", "Ph", 22.5, 74, "3k"),
    (12, "1i", "CH3", "CH3", "Ph", "2c", "Br", 19, 71, "3l"),
]


def table_record(row):
    entry, substrate, r1, r2, r3, halide, r4, time_h, yield_pct, product = row
    evidence = P3 + P4
    halide_name = "allyl bromide" if halide == "2a" else f"allylic bromide {halide} (R4={r4})"
    substrate_name = f"2,3-allenol {substrate} (R1={r1}, R2={r2}, R3={r3})"
    product_name = ("2-methyl-3-(n-butyl)-4-allyl-2,5-dihydrofuran" if product == "3a"
                    else f"2,5-dihydrofuran {product}")
    parts = [
        participant("substrate", "reactant", substrate, substrate_name, P3,
                    [field("amount", {"number": 1, "unit": "mmol"}, P3)]),
        participant("allylic_bromide", "reactant", halide, halide_name, P3,
                    [field("amount", {"number": 5, "unit": "mmol"}, P3),
                     field("equivalents", {"number": 5, "unit": "equiv"}, P3)]),
        participant("pdcl2", "catalyst", "PdCl2", "palladium(II) chloride", P3 + P4,
                    [field("amount", {"number": 0.05, "unit": "mmol"}, P3),
                     field("loading", {"number": 5, "unit": "mol%"}, P3)]),
        participant("dma", "solvent", "DMA", "N,N-dimethylacetamide", P3 + P4,
                    [field("volume", {"number": 6, "unit": "mL"}, P3)]),
        participant("product", "product", product, product_name, P3),
    ]
    steps = [
        simple_step("reaction", ["substrate", "allylic_bromide", "pdcl2", "dma"],
                    [field("temperature", "rt", P3 + P4),
                     field("time", {"number": time_h, "unit": "h"}, P3)]),
        simple_step("workup", ["product"],
                    [field("operations", "after completion, ether was added; washed with brine; dried over anhydrous Na2SO4", P4)]),
        simple_step("purification", ["product"],
                    [field("method", "flash column chromatography on silica", P4),
                     field("eluent", "petroleum ether and ether", P4)]),
    ]
    return record(
        f"table1_entry{entry:02d}", "substrate_scope_entry", evidence, parts, steps,
        [field("isolated_yield", {"number": yield_pct, "unit": "%"}, P3),
         field("yield_basis", "based on 1", P3)],
        [f"Table 1 entry {entry}; R1={r1}, R2={r2}, R3={r3}, R4={r4}."],
        ["Atmosphere, concentration, isolated mass, product purity, and complete characterization are not reported in the supplied main text.",
         "No Supporting Information is supplied or associated in this pilot."],
    )


records.extend(table_record(row) for row in table_rows)

# Scheme 2 is a distinct branched-allyl chloride experiment.
scheme2_ev = P3 + P4
scheme2_parts = [
    participant("substrate_1a", "reactant", "1a", "3-(n-butyl)-3,4-pentadien-2-ol", P3),
    participant("halide_2d", "reactant", "2d", "3-chloro-1-butene", scheme2_ev,
                [field("equivalents", {"number": 5, "unit": "equiv"}, P3)]),
    participant("pdcl2", "catalyst", "PdCl2", "palladium(II) chloride", P3,
                [field("loading", {"number": 5, "unit": "mol%"}, P3)]),
    participant("dma", "solvent", "DMA", "N,N-dimethylacetamide", P3),
    participant("product_4", "product", "4", "SN2'-type product 4", P3),
    participant("product_4prime", "product", "4'", "regioisomer 4'", P3),
]
records.append(record(
    "scheme2_1a_2d", "reported_experiment", scheme2_ev, scheme2_parts,
    [
        simple_step("reaction", ["substrate_1a", "halide_2d", "pdcl2", "dma"],
                    [field("temperature", "rt", P3), field("time", None)]),
    ],
    [field("yield", {"number": 63, "unit": "%"}, P3),
     field("product_ratio_4_to_4prime", "97:3", P3),
     field("product_4_E_Z_ratio", "1:1", P3),
     field("selectivity_description", "SN2'-type product 4 formed with high selectivity", P2 + P3)],
    ["Footnote 17 states that 2d was purchased at 98% purity."],
    ["Reaction scale, solvent volume, reaction time, atmosphere, concentration, yield basis, workup, purification, isolated mass, product purity, and configuration assignments are not reported.",
     "Reference 16 explicitly affords product family 3 and therefore was not generalized to this Scheme 2 product-4 experiment.",
     "No Supporting Information is supplied or associated in this pilot."],
))

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")

page2_ids = [r["record_id"] for r in records if ev(2, "image") in r["evidence_ids"]]
page3_ids = [r["record_id"] for r in records if ev(3, "image") in r["evidence_ids"]]
page4_ids = [r["record_id"] for r in records if ev(4, "image") in r["evidence_ids"]]
coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1,
            "state": "attempted",
            "regions": [
                {"region": "title and abstract", "finding": "Current generic PdCl2/DMA/room-temperature coupling-cyclization is summarized, but no row-specific run, arrow, or numerical experiment is shown on this page.", "evidence_ids": [ev(1, "image"), ev(1, "text")]},
                {"region": "introduction and prior-work discussion", "finding": "Background syntheses and the authors' earlier Pd(0) chemistry are cited; these are not current-paper experiments. The prior Scheme 1 result continues on page 2.", "evidence_ids": [ev(1, "image"), ev(1, "text")]},
            ],
            "record_ids": [],
            "unresolved": ["No SI is supplied; the page contains no complete local experimental procedure."],
        },
        {
            "page": 2,
            "state": "attempted",
            "regions": [
                {"region": "Scheme 1 and preceding/adjacent prose", "finding": "Prior Pd(0) work forms vinylic oxiranes by Path A; the Path B 2,5-dihydrofuran is not observed. The diagram also presents proposed alternative attack paths.", "evidence_ids": [ev(2, "image"), ev(2, "text")]},
                {"region": "optimization prose and 1a + 2a arrow", "finding": "Separate screening outcomes include 74% at 5 mol% PdCl2/5 equiv allyl bromide, lower yields below 5 equiv, 51% with allyl chloride, 65% at 1 mol% PdCl2, and three other effective Pd catalysts without numerical yields.", "evidence_ids": [ev(2, "image"), ev(2, "text")]},
                {"region": "scope prose below the arrow", "finding": "Table 1 is introduced; 1i with 3-phenyl-2-propenyl bromide is explicitly complicated, while 2b-c are deferred to Table 1. The 2d result is deferred to Scheme 2 on page 3.", "evidence_ids": [ev(2, "image"), ev(2, "text")]},
            ],
            "record_ids": page2_ids,
            "unresolved": ["Several prose screening runs lack exact loading, time, yield basis, and workup details.", "The relation between the prose 74% 3a result and Table 1 entry 1 (76%) is not stated."],
        },
        {
            "page": 3,
            "state": "attempted",
            "regions": [
                {"region": "Table 1 header, rows 1-12, and footnotes", "finding": "Twelve substrate-scope rows were transcribed individually with row-specific R groups, time, product label, isolated yield, and shared charges/conditions.", "evidence_ids": [ev(3, "image"), ev(3, "text")]},
                {"region": "Scheme 2", "finding": "1a and 3-chloro-1-butene 2d give products 4 and 4' in 97:3 ratio, product 4 E/Z=1:1, 63% yield under 5 mol% PdCl2/DMA/rt.", "evidence_ids": [ev(3, "image"), ev(3, "text")]},
                {"region": "acknowledgements", "finding": "No reaction or experimental record is present.", "evidence_ids": [ev(3, "image"), ev(3, "text")]},
            ],
            "record_ids": page3_ids,
            "unresolved": ["Scheme 2 does not report reaction time or yield basis.", "The Table 1 header depicts label ranges 1a-k and 3a-m, while the visible rows use substrates through 1j (with 1i repeated) and products through 3l; the presentation mismatch is not normalized.", "No structure was promoted from the drawings to verified SMILES."],
        },
        {
            "page": 4,
            "state": "attempted",
            "regions": [
                {"region": "references 1-15", "finding": "Bibliography and prior-literature context only; no current-paper experiment was created from citations.", "evidence_ids": [ev(4, "image"), ev(4, "text")]},
                {"region": "reference 16 general procedure", "finding": "General procedure supplies 1 mmol allenol, 5 mmol allylic halide, 5 mol% PdCl2, DMA 6 mL, rt, ether/brine/Na2SO4 workup, and silica chromatography with petroleum ether/ether; linked to Table 1 only because the procedure explicitly affords product family 3.", "evidence_ids": [ev(4, "image"), ev(4, "text")]},
                {"region": "reference 17", "finding": "3-Chloro-1-butene 2d is stated to be purchased at 98% purity.", "evidence_ids": [ev(4, "image"), ev(4, "text")]},
            ],
            "record_ids": page4_ids,
            "unresolved": ["The main text provides no atmosphere or concentration and no SI is supplied or associated."],
        },
    ],
}
COVERAGE.parent.mkdir(parents=True, exist_ok=True)
COVERAGE.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

tasks = json.loads(TASKS.read_text())
for task in tasks:
    if task.get("document_id") == DOC and task.get("evidence_id") in {ev(i, "text") for i in range(1, 5)}:
        task["state"] = "attempted"
        task["reason"] = "Original page image inspected; reaction regions classified and linked in pages_0001_0004 coverage ledger."
TASKS.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"records": len(records), "coverage_pages": len(coverage["pages"])}, ensure_ascii=False))
