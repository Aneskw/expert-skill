#!/usr/bin/env python3
"""Enrich existing records with experimental details from PDF pages 7-10."""
from __future__ import annotations

import copy
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
DATASET = ROOT / "runs/current/dataset.json"
OUT = ROOT / "runs/current/raw_model/extracted_records_pages_0007_0010.json"
COVERAGE = ROOT / "runs/current/coverage/pages_0007_0010.json"
TASKS = ROOT / "runs/current/tasks.json"
DOC = "doc_cc7b51233e5bb98b"


def ev(page: int) -> list[str]:
    return [f"{DOC}:page{page}:text", f"{DOC}:page{page}:image"]


def fact(value, evidence):
    return {
        "value": value,
        "evidence_ids": list(evidence) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def qty(number, unit):
    return {"number": number, "unit": unit}


def field(name, value, evidence, targets=None):
    item = {"name": name, "fact": fact(value, evidence)}
    if targets:
        item["target_entity_ids"] = list(targets)
    return item


def add_page(record, page: int):
    for evidence_id in ev(page):
        if evidence_id not in record["evidence_ids"]:
            record["evidence_ids"].append(evidence_id)


def participant(record, entity_id):
    return next(p for p in record["participants"] if p["entity_id"] == entity_id)


def add_amount(record, entity_id, name, value, page):
    p = participant(record, entity_id)
    if any(a["name"] == name for a in p["amounts"]):
        return
    p["amounts"].append(field(name, value, ev(page)))


def add_mass_amount(record, entity_id, mass_mg, amount_mmol, page):
    add_amount(record, entity_id, "mass", qty(mass_mg, "mg"), page)
    add_amount(record, entity_id, "amount", qty(amount_mmol, "mmol"), page)


def set_identity(record, entity_id, name, smiles, page):
    p = participant(record, entity_id)
    p["name"] = fact(name, ev(page))
    p["smiles"] = fact(smiles, ev(page)) if smiles else fact(None, [])
    p["smiles_parseable"] = None
    p["structure_verified"] = False


def set_isolated_yield(record, entity_id, percent, page):
    matched = False
    for outcome in record["outcomes"]:
        targets = outcome.get("target_entity_ids", [])
        value = outcome["fact"]["value"]
        if entity_id in targets and isinstance(value, dict) and value.get("number") == percent:
            outcome["name"] = "isolated_yield"
            for evidence_id in ev(page):
                if evidence_id not in outcome["fact"]["evidence_ids"]:
                    outcome["fact"]["evidence_ids"].append(evidence_id)
            matched = True
            break
    if not matched:
        record["outcomes"].append(field("isolated_yield", qty(percent, "%"), ev(page), [entity_id]))
    record["review"]["unresolved"] = [
        item for item in record["review"]["unresolved"]
        if "yield measurement basis" not in item.casefold()
        and "yield basis" not in item.casefold()
    ]
    record["notes"] = [
        item for item in record["notes"]
        if not (isinstance(item.get("value"), str) and "yield basis" in item["value"].casefold())
    ]


def fur(r2=None, r3=None, r4=None, r5=None):
    def branch(value):
        return f"({value})" if value else ""
    return f"O1C{branch(r2)}=C{branch(r3)}C{branch(r4)}=C1{r5 or ''}"


PRODUCTS = {
    "3ab": ("2-dodecyl-3-(4-nitrophenyl)-5-methylfuran", fur("CCCCCCCCCCCC", "c2ccc([N+](=O)[O-])cc2", None, "C")),
    "3ac": ("2-dodecyl-3-(4-methoxycarbonylphenyl)-5-methylfuran", fur("CCCCCCCCCCCC", "c2ccc(C(=O)OC)cc2", None, "C")),
    "3ba": ("2-butyl-3-phenyl-5-methylfuran", fur("CCCC", "c2ccccc2", None, "C")),
    "3bb": ("2-butyl-3-(4-nitrophenyl)-5-methylfuran", fur("CCCC", "c2ccc([N+](=O)[O-])cc2", None, "C")),
    "3bc": ("2-butyl-3-(4-methoxycarbonylphenyl)-5-methylfuran", fur("CCCC", "c2ccc(C(=O)OC)cc2", None, "C")),
    "3bd": ("2-butyl-3-(pyrimidin-5-yl)-5-methylfuran", fur("CCCC", "c2cncnc2", None, "C")),
    "3be": ("2-butyl-3-(E-2-methoxycarbonylethenyl)-5-methylfuran", fur("CCCC", "/C=C/C(=O)OC", None, "C")),
    "3bf": ("2-butyl-3-(4-methoxyphenyl)-5-methylfuran", fur("CCCC", "c2ccc(OC)cc2", None, "C")),
    "3cc": ("2-heptyl-3-(4-methoxycarbonylphenyl)-5-methylfuran", fur("CCCCCCC", "c2ccc(C(=O)OC)cc2", None, "C")),
    "3cf": ("2-heptyl-3-(4-methoxyphenyl)-5-methylfuran", fur("CCCCCCC", "c2ccc(OC)cc2", None, "C")),
    "3da": ("2-heptyl-3-phenyl-5-cyclohexylfuran", fur("CCCCCCC", "c2ccccc2", None, "C2CCCCC2")),
    "3dc": ("2-heptyl-3-(4-methoxycarbonylphenyl)-5-cyclohexylfuran", fur("CCCCCCC", "c2ccc(C(=O)OC)cc2", None, "C2CCCCC2")),
    "3ea": ("2-heptyl-3-phenyl-5-tert-butylfuran", fur("CCCCCCC", "c2ccccc2", None, "C(C)(C)C")),
    "3fb": ("2-phenyl-3-(4-nitrophenyl)-5-methylfuran", fur("c2ccccc2", "c2ccc([N+](=O)[O-])cc2", None, "C")),
    "3fc": ("2-phenyl-3-(4-methoxycarbonylphenyl)-5-methylfuran", fur("c2ccccc2", "c2ccc(C(=O)OC)cc2", None, "C")),
    "3gb": ("2-phenyl-3-(4-nitrophenyl)-5-propylfuran", fur("c2ccccc2", "c2ccc([N+](=O)[O-])cc2", None, "CCC")),
    "3gc": ("2-phenyl-3-(4-methoxycarbonylphenyl)-5-propylfuran", fur("c2ccccc2", "c2ccc(C(=O)OC)cc2", None, "CCC")),
    "3hb": ("2,3-dimethyl-4-(4-nitrophenyl)furan", fur("C", "C", "c2ccc([N+](=O)[O-])cc2", None)),
    "3hc": ("2,3-dimethyl-4-(4-methoxycarbonylphenyl)furan", fur("C", "C", "c2ccc(C(=O)OC)cc2", None)),
    "3id": ("2-methyl-3-butyl-4-(pyrimidin-5-yl)furan", fur("C", "CCCC", "c2cncnc2", None)),
    "3jb": ("2-methyl-3-allyl-4-(4-nitrophenyl)furan", fur("C", "CC=C", "c2ccc([N+](=O)[O-])cc2", None)),
    "3ka": ("2-pentyl-3-phenyl-4-butyl-5-methylfuran", fur("CCCCC", "c2ccccc2", "CCCC", "C")),
    "4k": ("2-methyl-3-butyl-5-pentylfuran", fur("C", "CCCC", None, "CCCCC")),
    "3kc": ("2-pentyl-3-(4-methoxycarbonylphenyl)-4-butyl-5-methylfuran", fur("CCCCC", "c2ccc(C(=O)OC)cc2", "CCCC", "C")),
    "3ke": ("2-pentyl-3-(E-2-methoxycarbonylethenyl)-4-butyl-5-methylfuran", fur("CCCCC", "/C=C/C(=O)OC", "CCCC", "C")),
    "3kf": ("2-pentyl-3-(4-methoxyphenyl)-4-butyl-5-methylfuran", fur("CCCCC", "c2ccc(OC)cc2", "CCCC", "C")),
    "3la": ("2-butyl-3-phenyl-4-pentyl-5-methylfuran", fur("CCCC", "c2ccccc2", "CCCCC", "C")),
    "3ma": ("2,4-dipentyl-3-phenyl-5-methylfuran", fur("CCCCC", "c2ccccc2", "CCCCC", "C")),
    "3na": ("2-butyl-3-phenyl-4-pentyl-5-isopropylfuran", fur("CCCC", "c2ccccc2", "CCCCC", "C(C)C")),
    "3oa": ("2-(2-methylbutyl)-3-phenyl-4-pentyl-5-methylfuran", fur("CC(C)CC", "c2ccccc2", "CCCCC", "C")),
    "3pc": ("2-(4-methylphenyl)-3-butyl-4-(4-methoxycarbonylphenyl)-5-pentylfuran", fur("c2ccc(C)cc2", "CCCC", "c2ccc(C(=O)OC)cc2", "CCCCC")),
    "3qc": ("2-(4-trifluoromethylphenyl)-3-butyl-4-(4-methoxycarbonylphenyl)-5-pentylfuran", fur("c2ccc(C(F)(F)F)cc2", "CCCC", "c2ccc(C(=O)OC)cc2", "CCCCC")),
}


# record id, page, ketone mass/amount, halide mass/amount, product entity/label/mass/yield
ROWS = [
    ("table2_entry_3", 7, 150, 0.6, 79, 0.3, [("product", "3ac", 108, 94)]),
    ("table2_entry_4", 7, 69, 0.5, 204, 1.0, [("product", "3ba", 78, 73)]),
    ("table2_entry_5", 7, 207, 1.5, 249, 1.0, [("product", "3bb", 239, 92)]),
    ("table2_entry_6", 7, 138, 1.0, 131, 0.5, [("product", "3bc", 115, 85)]),
    ("table2_entry_7", 7, 104, 0.75, 80, 0.5, [("product", "3bd", 77, 71)]),
    ("table2_entry_8", 7, 104, 0.75, 106, 0.5, [("product", "3be", 68, 61)]),
    ("table2_entry_9", 7, 104, 0.75, 117, 0.5, [("product", "3bf", 78, 64)]),
    ("table2_entry_10", 7, 108, 0.6, 80, 0.3, [("product", "3cc", 93, 98)]),
    ("eq5_deuterium_control", 7, 181, 1.0, 131, 0.5, [("product", "3cc", 140, 89)]),
    ("table2_entry_11", 7, 135, 0.75, 117, 0.5, [("product", "3cf", 90, 63)]),
    ("table2_entry_12", 7, 124, 0.5, 204, 1.0, [("product", "3da", 119, 74)]),
    ("table2_entry_13", 7, 186, 0.75, 131, 0.5, [("product", "3dc", 146, 76)]),
    ("eq6_no_alpha_h_control", 7, 111, 0.5, 408, 2.0, [("product", "3ea", 110, 74)]),
    ("table2_entry_14", 8, 119, 0.75, 125, 0.5, [("product", "3fb", 71, 51)]),
    ("table2_entry_15", 8, 119, 0.75, 131, 0.5, [("product", "3fc", 75, 51)]),
    ("table2_entry_16", 8, 140, 0.75, 125, 0.5, [("product", "3gb", 118, 77)]),
    ("table2_entry_17", 8, 140, 0.75, 131, 0.5, [("product", "3gc", 116, 73)]),
    ("table3_entry_1", 8, 182, 2.0, 249, 1.0, [("product", "3hb", 171, 79)]),
    ("table3_entry_2", 8, 144, 1.5, 262, 1.0, [("product", "3hc", 156, 68)]),
    ("table3_entry_3", 8, 207, 1.5, 159, 1.0, [("product", "3id", 209, 97)]),
    ("table3_entry_4", 8, 183, 1.5, 249, 1.0, [("product", "3jb", 191, 79)]),
    ("table4_entry_1", 8, 104, 0.5, 204, 1.0, [("p3ka", "3ka", 81, 57), ("p4k", "4k", 22, 11)]),
    ("table5_entry_2", 8, 208, 1.0, 131, 0.5, [("product", "3kc", 161, 94)]),
    ("table5_entry_3", 8, 166, 0.8, 106, 0.5, [("product", "3ke", 94, 64)]),
    ("table5_entry_4", 9, 208, 1.0, 117, 0.5, [("product", "3kf", 80, 51), ("byproduct", "3ka", 39, 27)]),
    ("table5_entry_5", 9, 208, 1.0, 408, 2.0, [("product", "3la", 196, 69)]),
    ("table5_entry_6", 9, 222, 1.0, 408, 2.0, [("product", "3ma", 176, 59)]),
    ("table5_entry_7", 9, 236, 1.0, 408, 2.0, [("product", "3na", 187, 60)]),
    ("table5_entry_8", 9, 222, 1.0, 408, 2.0, [("product", "3oa", 201, 67)]),
    ("scheme9_1p_individual", 9, 400, 1.41, 200, 0.76, [("product", "3pc", 285, 90)]),
    ("scheme9_1q_individual", 9, 338, 1.0, 131, 0.5, [("product", "3qc", 50, 21)]),
]


data = json.loads(DATASET.read_text())
existing = {r["source_reaction_id"]: r for r in data["experiments"]}
selected = {}


def take(record_id):
    if record_id not in selected:
        selected[record_id] = copy.deepcopy(existing[record_id])
    return selected[record_id]


# Page 7 begins with characterization continuing the 3ab experiment from page 6.
r = take("table2_entry_2")
add_page(r, 7)
set_identity(r, "product", *PRODUCTS["3ab"], 7)

for record_id, page, kmass, kmmol, hmass, hmmol, products in ROWS:
    r = take(record_id)
    add_page(r, page)
    ketone_id = "d1c" if record_id == "eq5_deuterium_control" else "ketone"
    add_mass_amount(r, ketone_id, kmass, kmmol, page)
    add_mass_amount(r, "halide", hmass, hmmol, page)
    for entity_id, label, pmass, percent in products:
        add_amount(r, entity_id, "mass", qty(pmass, "mg"), page)
        set_identity(r, entity_id, *PRODUCTS[label], page)
        set_isolated_yield(r, entity_id, percent, page)

# The 3ea characterization continues at the top of page 8.
add_page(take("eq6_no_alpha_h_control"), 8)

# Explicit identities for 2e differ between the two printed experimental paragraphs.
set_identity(take("table2_entry_8"), "halide", "methyl (Z)-3-iodopropenoate", "COC(=O)/C=C\\I", 7)
set_identity(take("table5_entry_3"), "halide", "methyl (E)-3-iodopropenoate", "COC(=O)/C=C/I", 8)
take("table5_entry_3")["review"]["unresolved"].append(
    "The page-8 experimental paragraph calls 2e methyl (E)-3-iodopropenoate, while the page-3 scope text/footnote identifies 2e as the Z isomer; both source statements are preserved."
)

# Page 8 detailed Conditions B procedure enriches optimization Table 4 entry 8.
r = take("table4_entry_8")
add_page(r, 8)
for entity_id, mass, amount in [
    ("catalyst", 29, 0.05), ("ketone", 104, 1.0), ("base", 138, 1.0),
    ("additive", 32, 0.1), ("halide", 204, 2.0), ("p3ka", 101, None),
]:
    add_amount(r, entity_id, "mass", qty(mass, "mg"), 8)
    if amount is not None:
        add_amount(r, entity_id, "amount", qty(amount, "mmol"), 8)
add_amount(r, "solvent", "volume", qty(2.5, "mL"), 8)
set_identity(r, "p3ka", *PRODUCTS["3ka"], 8)
set_identity(r, "p4k", *PRODUCTS["4k"], 8)
set_isolated_yield(r, "p3ka", 72, 8)
r["steps"][0]["conditions"].extend([
    field("atmosphere", "Ar", ev(8)),
    field("workup", "H2O addition, ether extraction, MgSO4 drying, evaporation", ev(8)),
    field("purification", "silica-gel column chromatography with hexanes", ev(8)),
])
r["review"]["unresolved"].append(
    "The printed Conditions B mass/mmol pairs (notably 104 mg 1k = 1.0 mmol and 204 mg iodobenzene = 2.0 mmol) are internally inconsistent with molecular weights and the table loadings; source values are retained without correction."
)

# Conditions A products are also explicitly named on page 8.
r = take("table4_entry_1")
set_identity(r, "p3ka", *PRODUCTS["3ka"], 8)
set_identity(r, "p4k", *PRODUCTS["4k"], 8)

# Candidate structures are transcriptions from fully specified product headings only.
for r in selected.values():
    if not any("Candidate product SMILES" in item.get("value", "") for item in r["notes"] if isinstance(item.get("value"), str)):
        page = min(int(eid.split(":page", 1)[1].split(":", 1)[0]) for eid in r["evidence_ids"] if ":page" in eid and 7 <= int(eid.split(":page", 1)[1].split(":", 1)[0]) <= 9)
        r["notes"].append(fact(
            "Candidate product SMILES was transcribed from the fully specified experimental heading; it remains structure-unverified.",
            ev(page),
        ))
    r["status"] = "candidate"
    r["completeness"] = "partial"


page_records = {
    7: [
        "table2_entry_2", "table2_entry_3", "table2_entry_4", "table2_entry_5",
        "table2_entry_6", "table2_entry_7", "table2_entry_8", "table2_entry_9",
        "table2_entry_10", "eq5_deuterium_control", "table2_entry_11",
        "table2_entry_12", "table2_entry_13", "eq6_no_alpha_h_control",
    ],
    8: [
        "eq6_no_alpha_h_control", "table2_entry_14", "table2_entry_15",
        "table2_entry_16", "table2_entry_17", "table3_entry_1", "table3_entry_2",
        "table3_entry_3", "table3_entry_4", "table4_entry_1", "table4_entry_8",
        "table5_entry_2", "table5_entry_3",
    ],
    9: [
        "table5_entry_4", "table5_entry_5", "table5_entry_6", "table5_entry_7",
        "table5_entry_8", "scheme9_1p_individual", "scheme9_1q_individual",
    ],
    10: [],
}

regions = {
    7: [
        ("upper-left continuation and 3ac-3bc paragraphs", "3ab characterization continues from page 6; 3ac, 3ba, 3bb, and 3bc give explicit reactant/product masses, amounts, and isolated yields."),
        ("lower-left 3bd-3be paragraphs", "Two additional Conditions A scope experiments (3bd and 3be) with explicit quantities and isolated yields."),
        ("upper/right 3bf-3cc and deuterium-control paragraphs", "3bf, 3cc, and the [D]1c control are explicit experiments; the control adds product mass and isolated yield to Equation 5."),
        ("middle/right 3cf-3dc and bottom 3ea paragraph", "3cf, 3da, 3dc, and 3ea are explicit scope/control experiments; 3ea characterization continues on page 8."),
    ],
    8: [
        ("top continuation and left column 3fb-3gc", "Completion of 3ea characterization followed by four explicit Table 2 scope experiments (3fb, 3fc, 3gb, 3gc)."),
        ("lower-left 3hb-3id and upper-right 3jb", "Four explicit Table 3 scope experiments with masses, amounts, isolated yields, and characterization."),
        ("middle-right Conditions A with 3ka and 4k", "Explicit 1k/iodobenzene Conditions A experiment producing isolated 3ka and 4k; merged with Table 4 entry 1."),
        ("middle-right Conditions B typical procedure", "Detailed Conditions B operation, reagent quantities, atmosphere, workup, purification, and isolated 3ka yield; merged with Table 4 entry 8."),
        ("lower-right 3kc and 3ke", "Two explicit Table 5 scope experiments; the printed E/Z identity of 2e conflicts with page 3 and remains unresolved."),
    ],
    9: [
        ("left column 3kf-3oa", "Five explicit Table 5 scope experiments; 3kf includes isolated 3ka as a second product with its own mass and yield."),
        ("lower-left and upper-right 3pc-3qc", "Two explicit electronic-effect experiments from Scheme 9 with masses, amounts, and isolated yields."),
        ("acknowledgement and references [1]-[6]", "No current-paper reaction arrow or experimental procedure; bibliographic context only."),
    ],
    10: [
        ("left column references [6]-[14]", "Bibliographic references only; no current-paper experimental record or reaction arrow."),
        ("right column references [15]-[28]", "Bibliographic references and explanatory citations only; no standalone experimental procedure extracted."),
        ("received line", "Publication metadata only; no reaction content."),
    ],
}

unresolved = {
    7: [
        "Spectroscopic characterization values are retained in source evidence but not decomposed into reaction-condition fields.",
        "Candidate product structures are name-derived and remain unverified; no Supporting Information was explicitly supplied or associated.",
    ],
    8: [
        "The printed Conditions B mass/mmol values are internally inconsistent and were preserved without correction.",
        "The E/Z identity printed for 2e conflicts across pages 3 and 8.",
        "Candidate product structures remain unverified; no Supporting Information was explicitly supplied or associated.",
    ],
    9: [
        "Individual scope paragraphs do not repeat the full Conditions B workup; shared conditions remain linked from the earlier table/typical procedure.",
        "Candidate product structures remain unverified; no Supporting Information was explicitly supplied or associated.",
    ],
    10: [
        "Bibliographic citations were not expanded into reaction records because this page gives no experimental arrows or procedures.",
    ],
}

coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": page,
            "state": "attempted",
            "regions": [
                {
                    "region": region,
                    "finding": finding,
                    "evidence_ids": [f"{DOC}:page{page}:image", f"{DOC}:page{page}:text"],
                }
                for region, finding in regions[page]
            ],
            "record_ids": [f"{DOC}:{rid}" for rid in page_records[page]],
            "unresolved": unresolved[page],
        }
        for page in range(7, 11)
    ],
}

records = [selected[rid] for rid in sorted(selected)]
OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
COVERAGE.parent.mkdir(parents=True, exist_ok=True)
COVERAGE.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

tasks = json.loads(TASKS.read_text())
for task in tasks:
    if task.get("document_id") != DOC:
        continue
    for page in range(7, 11):
        if task.get("evidence_id") == f"{DOC}:page{page}:text":
            task["state"] = "attempted"
            task["visual_evidence_id"] = f"{DOC}:page{page}:image"
            task["reason"] = "Original rendered page image and extracted page text were inspected; experimental details were merged into existing records and page coverage was logged."
TASKS.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({
    "updated_records": len(records),
    "new_record_ids": 0,
    "pages": [7, 8, 9, 10],
    "output": str(OUT),
    "coverage": str(COVERAGE),
}, ensure_ascii=False))
