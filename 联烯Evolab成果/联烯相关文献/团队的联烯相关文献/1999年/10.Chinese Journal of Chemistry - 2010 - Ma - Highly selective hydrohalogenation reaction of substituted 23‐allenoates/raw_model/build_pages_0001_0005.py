#!/usr/bin/env python3
"""Build source-linked machine records for PDF pages 1--5.

This file intentionally does not assign SMILES.  Labels and names transcribe the
paper, while every structure remains unverified pending independent review.
"""

import json
from pathlib import Path


DOC = "doc_73c3cd21e49c7838"
ROOT = Path(__file__).resolve().parents[1]
RAW_OUT = ROOT / "raw_model" / "records_pages_0001_0005.json"
COVERAGE_OUT = ROOT / "coverage" / "pages_0001_0005.json"


def ev(page):
    return [f"{DOC}:page{page}:image", f"{DOC}:page{page}:text"]


def fact(value, evidence_ids=None):
    return {
        "value": value,
        "evidence_ids": list(evidence_ids or []),
        "verification": "missing" if value is None else "unreviewed",
    }


def field(name, value, evidence_ids=None):
    return {"name": name, "fact": fact(value, evidence_ids)}


def participant(entity_id, role, label, name, evidence_ids, amounts=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence_ids),
        "name": fact(name, evidence_ids),
        "smiles": fact(None),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": amounts or [],
    }


def record(suffix, source_id, kind, evidence_ids, participants, steps, outcomes,
           notes, unresolved):
    return {
        "record_id": f"{DOC}:{suffix}",
        "document_id": DOC,
        "source_reaction_id": source_id,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": evidence_ids,
        "participants": participants,
        "steps": steps,
        "outcomes": outcomes,
        "notes": [fact(n, evidence_ids) for n in notes],
        "review": {
            "method": "model",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved,
        },
    }


records = []


# Table 1: each optimization row is a distinct experiment.  Entry 6 additionally
# carries the detailed typical procedure printed as reference 6 on page 4.
table1 = [
    # entry, salt, equiv, R, solvent, time value/unit, temperature, product 2,
    # product 2 name, yield 2, product 3, product 3 name, yield 3, yield basis
    (1, "NaI", 1.5, "Me", "HOAc", 24, "h", 80, "2a", "ethyl 3-iodo-2-methyl-3-butenoate", {"number": 41, "unit": "%"}, "3a", "ethyl 3-iodo-2-methyl-2-butenoate", {"number": 10, "unit": "%"}, "isolated yield"),
    (2, "NaI", 4, "Me", "HOAc", 72, "h", 80, "2a", "ethyl 3-iodo-2-methyl-3-butenoate", {"number": 53, "unit": "%"}, "3a", "ethyl 3-iodo-2-methyl-2-butenoate", {"number": 14, "unit": "%"}, "NMR yield"),
    (3, "LiBr-H2O", 1.3, "Me", "HOAc", 72, "h", 80, "2b", "ethyl 3-bromo-2-methyl-3-butenoate", "<5%", "3b", "ethyl 3-bromo-2-methyl-2-butenoate", "<5%", "isolated yield"),
    (4, "LiBr-H2O", 1.5, "Me", "HOAc", 120, "h", 40, "2b", "ethyl 3-bromo-2-methyl-3-butenoate", "<5%", "3b", "ethyl 3-bromo-2-methyl-2-butenoate", "<5%", "isolated yield"),
    (5, "LiCl-H2O", 1.8, "Me", "HOAc", 74, "h", 80, "2c", "ethyl 3-chloro-2-methyl-3-butenoate", "~10%", "3c", "ethyl 3-chloro-2-methyl-2-butenoate", "~5%", "isolated yield"),
    (6, "NaI", 3, "Me", "HOAc-CF3CO2H (1:1)", 4, "h", 80, "2a", "ethyl 3-iodo-2-methyl-3-butenoate", {"number": 95, "unit": "%"}, "3a", "ethyl 3-iodo-2-methyl-2-butenoate", None, "isolated yield"),
    (7, "LiBr-H2O", 3, "Me", "HOAc-CF3CO2H (1:1)", 12, "h", 80, "2b", "ethyl 3-bromo-2-methyl-3-butenoate", {"number": 80, "unit": "%"}, "3b", "ethyl 3-bromo-2-methyl-2-butenoate", None, "isolated yield"),
    (8, "NaI", 2, "Me", "CF3CO2H", 10, "min", 80, "2a", "ethyl 3-iodo-2-methyl-3-butenoate", {"number": 90, "unit": "%"}, "3a", "ethyl 3-iodo-2-methyl-2-butenoate", None, "isolated yield"),
    (9, "LiBr-H2O", 2, "Me", "CF3CO2H", 40, "min", 80, "2b", "ethyl 3-bromo-2-methyl-3-butenoate", {"number": 88, "unit": "%"}, "3b", "ethyl 3-bromo-2-methyl-2-butenoate", None, "isolated yield"),
    (10, "NaI", 2, "n-C3H7", "CF3CO2H", 20, "min", 80, "2d", "ethyl 3-iodo-2-propyl-3-butenoate", {"number": 98, "unit": "%"}, "3", "corresponding alpha,beta-unsaturated 3-iodo-2-alkenoate", None, "isolated yield"),
    (11, "LiBr-H2O", 2, "n-C3H7", "CF3CO2H", 50, "min", 80, "2e", "ethyl 3-bromo-2-propyl-3-butenoate", {"number": 76, "unit": "%"}, "3", "corresponding alpha,beta-unsaturated 3-bromo-2-alkenoate", None, "isolated yield"),
    (12, "LiCl-H2O", 3, "n-C3H7", "CF3CO2H", 10, "h", 80, "2f", "ethyl 3-chloro-2-propyl-3-butenoate", {"number": 63, "unit": "%"}, "3", "corresponding alpha,beta-unsaturated 3-chloro-2-alkenoate", None, "isolated yield"),
]

for row in table1:
    (entry, salt, equiv, r_group, solvent, time_number, time_unit, temperature,
     p2_label, p2_name, y2, p3_label, p3_name, y3, basis) = row
    evid = ev(2) + (ev(4) if entry == 6 else [])
    substrate_name = ("ethyl 2-methyl-2,3-butadienoate" if r_group == "Me"
                      else "ethyl 2-propyl-2,3-butadienoate")
    parts = [
        participant("substrate_1", "reactant", "1", substrate_name, ev(2),
                    ([field("mass", {"number": 90.8, "unit": "mg"}, ev(4)),
                      field("amount", {"number": 0.72, "unit": "mmol"}, ev(4))]
                     if entry == 6 else [])),
        participant("mx", "reagent", salt, salt, ev(2),
                    [field("equivalents", {"number": equiv, "unit": "equiv"}, ev(2))] +
                    ([field("mass", {"number": 325, "unit": "mg"}, ev(4)),
                      field("amount", {"number": 2.17, "unit": "mmol"}, ev(4))]
                     if entry == 6 else [])),
        participant("solvent", "solvent", solvent, solvent, ev(2),
                    ([field("volume", {"number": 2, "unit": "mL"}, ev(4))]
                     if entry == 6 else [])),
        participant("product_2", "product", p2_label, p2_name, ev(2)),
        participant("product_3", "product", p3_label, p3_name, ev(2)),
    ]
    conditions = [
        field("temperature", {"number": temperature, "unit": "°C"}, ev(2)),
        field("time", {"number": time_number, "unit": time_unit}, ev(2)),
        field("atmosphere", None),
        field("concentration", None),
    ]
    if entry == 6:
        conditions.extend([
            field("agitation", "stirring", ev(4)),
            field("monitoring", "TLC", ev(4)),
        ])
    steps = [{
        "step_id": "reaction",
        "participant_ids": ["substrate_1", "mx", "solvent"],
        "conditions": conditions,
    }]
    if entry == 6:
        steps.append({
            "step_id": "workup",
            "participant_ids": [],
            "conditions": [
                field("water_added", {"number": 1, "unit": "mL"}, ev(4)),
                field("neutralization", "saturated NaHCO3 solution", ev(4)),
                field("extraction", "ether, 4 x 5 mL", ev(4)),
                field("wash", "5% Na2S2O3, then brine", ev(4)),
                field("drying", "MgSO4", ev(4)),
                field("isolation", "filtration and evaporation", ev(4)),
                field("purification", None),
            ],
        })
    outcomes = [
        field("yield_product_2", y2, ev(2) + (ev(4) if entry == 6 else [])),
        field("yield_basis_product_2", basis, ev(2)),
    ]
    if y3 is None:
        outcomes.extend([
            field("product_3_observed", False, ev(2)),
            field("yield_product_3", None),
        ])
    else:
        outcomes.extend([
            field("yield_product_3", y3, ev(2)),
            field("yield_basis_product_3", basis, ev(2)),
        ])
    if entry == 6:
        outcomes.extend([
            field("isolated_mass_product_2", {"number": 173.2, "unit": "mg"}, ev(4)),
            field("reported_purity_description", "pure 2a", ev(4)),
        ])
    unresolved = [
        "Participant structures and alkene geometry are not independently verified; SMILES are intentionally null.",
        "Reaction concentration and atmosphere are not reported.",
    ]
    if entry != 6:
        unresolved.append("Row-specific charge, workup, purification, and isolated mass are not reported.")
    else:
        unresolved.append("No chromatographic purification is stated for this 2a isolation; concentration and atmosphere remain missing.")
    records.append(record(
        f"table1_entry_{entry:02d}", f"Table 1 entry {entry}",
        "optimization_entry", evid, parts, steps, outcomes,
        [f"Table 1 row {entry}; R = {r_group}."], unresolved,
    ))


# Scheme 1: three separate current-paper coupling reactions from the same 2a.
scheme1 = [
    ("4a", "n-BuZnBr", "Pd(PPh3)4", "THF", [], 90,
     "n-butyl-coupled beta,gamma-unsaturated alkenoate 4a", ev(3) + ev(5)),
    ("4b", "PhZnBr", "Pd(PPh3)4", "THF", [], 70,
     "phenyl-coupled beta,gamma-unsaturated alkenoate 4b", ev(3)),
    ("4c", "phenylacetylene", "PdCl2(PPh3)2", "CH3CN", ["CuI", "Et3N"], 85,
     "phenylethynyl-coupled beta,gamma-unsaturated alkenoate 4c", ev(3) + ev(5)),
]

for product_label, partner, catalyst, solvent, extras, yield_value, product_name, evid in scheme1:
    parts = [
        participant("substrate_2a", "reactant", "2a", "ethyl 3-iodo-2-methyl-3-butenoate", ev(3)),
        participant("coupling_partner", "reactant" if product_label == "4c" else "reagent", partner, partner, ev(3)),
        participant("catalyst", "catalyst", catalyst, catalyst, ev(3)),
        participant("solvent", "solvent", solvent, solvent, ev(3)),
        participant("product", "product", product_label, product_name, ev(3)),
    ]
    for i, extra in enumerate(extras, start=1):
        parts.append(participant(f"extra_{i}", "catalyst" if extra == "CuI" else "reagent", extra, extra, ev(3)))
    records.append(record(
        f"scheme1_{product_label}", f"Scheme 1 {product_label}", "reported_experiment", evid,
        parts,
        [{
            "step_id": "coupling",
            "participant_ids": [p["entity_id"] for p in parts if p["role"] != "product"],
            "conditions": [
                field("temperature", "room temperature", ev(3)),
                field("time", None),
                field("atmosphere", None),
                field("concentration", None),
            ],
        }],
        [
            field("yield", {"number": yield_value, "unit": "%"}, ev(3)),
            field("yield_basis", None),
        ],
        ["Scheme 1 reports retention of the beta,gamma-unsaturated alkene placement; the corresponding alpha,beta-unsaturated alkenoate was not observed."],
        [
            "Reagent quantities, catalyst loading, reaction time, atmosphere, concentration, workup, purification, and yield basis are not reported.",
            "Product structure is transcribed from the scheme but not independently structure-verified; SMILES is intentionally null.",
        ],
    ))


# Scheme 2: salt-mediated hydrohalogenation of ethyl 2,3-pentadienoate.
scheme2 = [
    ("NaI", "6a", "ethyl 3-iodo-3-pentenoate", 6, "4.7:1", 94),
    ("LiBr-H2O", "6b", "ethyl 3-bromo-3-pentenoate", 20, "5.5:1", 83),
    ("LiCl-H2O", "6c", "ethyl 3-chloro-3-pentenoate", 38, "1.3:1", 70),
]

for salt, product_label, product_name, hours, ratio, yield_value in scheme2:
    evid = ev(3)
    outcomes = [
        field("Z/E_ratio", ratio, evid),
        field("yield", {"number": yield_value, "unit": "%"}, evid),
        field("yield_basis", None),
    ]
    notes = ["Scheme 2 reports a Z/E mixture for the product."]
    if product_label == "6a":
        outcomes.append(field("major_isomer_configuration", "Z", evid))
        notes.append("Scheme 3 assigns Z-6a by a 2D NOESY experiment; this is structural evidence, not a separate reaction run.")
    parts = [
        participant("substrate_5", "reactant", "5", "ethyl 2,3-pentadienoate", evid),
        participant("mx", "reagent", salt, salt, evid),
        participant("solvent", "solvent", "HOAc", "acetic acid", evid),
        participant("product_6", "product", product_label, product_name, evid),
    ]
    records.append(record(
        f"scheme2_{product_label}", f"Scheme 2 {product_label}", "substrate_scope_entry", evid,
        parts,
        [{
            "step_id": "hydrohalogenation",
            "participant_ids": ["substrate_5", "mx", "solvent"],
            "conditions": [
                field("temperature", {"number": 90, "unit": "°C"}, evid),
                field("time", {"number": hours, "unit": "h"}, evid),
                field("reagent_amount", None),
                field("atmosphere", None),
                field("concentration", None),
                field("workup", None),
                field("purification", None),
            ],
        }],
        outcomes, notes,
        [
            "Reagent amount, atmosphere, concentration, workup, purification, isolated mass, and yield basis are not reported.",
            "Product structure and both alkene-isomer structures remain unverified; SMILES are intentionally null.",
        ],
    ))


# Scheme 4: direct HX reactions.  Each X row is a separate experiment and has
# two reported outcomes: retained ester 6 and hydrolyzed acid 7.
scheme4 = [
    ("I", "HI", 4, {"number": 40, "unit": "%"}, {"number": 48, "unit": "%"}),
    ("Br", "HBr", 24, "trace", {"number": 58, "unit": "%"}),
    ("Cl", "HCl", 48, "trace", {"number": 83, "unit": "%"}),
]

for x, hx, hours, y6, y7 in scheme4:
    evid = ev(4)
    halo = {"I": "iodo", "Br": "bromo", "Cl": "chloro"}[x]
    parts = [
        participant("substrate_5", "reactant", "5", "ethyl 2,3-pentadienoate", evid),
        participant("hx", "reagent", f"HX (X={x})", hx, evid),
        participant("product_6", "product", "6", f"ethyl 3-{halo}-3-pentenoate", evid),
        participant("product_7", "product", "7", f"3-{halo}-3-pentenoic acid", evid),
    ]
    records.append(record(
        f"scheme4_x_{x.lower()}", f"Scheme 4 X={x}", "reported_experiment", evid,
        parts,
        [{
            "step_id": "direct_hx_reaction",
            "participant_ids": ["substrate_5", "hx"],
            "conditions": [
                field("temperature", {"number": 80, "unit": "°C"}, evid),
                field("time", {"number": hours, "unit": "h"}, evid),
                field("solvent", None),
                field("reagent_amount", None),
                field("atmosphere", None),
                field("concentration", None),
                field("workup", None),
                field("purification", None),
            ],
        }],
        [
            field("yield_ester_6", y6, evid),
            field("yield_acid_7", y7, evid),
            field("yield_basis", None),
        ],
        ["The paper identifies ester hydrolysis as a serious side reaction in the direct HX reaction."],
        [
            "HX concentration and amount, solvent, atmosphere, reaction concentration, workup, purification, isolated masses, and yield basis are not reported.",
            "Product geometry and structures remain unverified; SMILES are intentionally null.",
        ],
    ))


record_ids = [r["record_id"] for r in records]
t1_ids = [f"{DOC}:table1_entry_{i:02d}" for i in range(1, 13)]
s1_ids = [f"{DOC}:scheme1_4a", f"{DOC}:scheme1_4b", f"{DOC}:scheme1_4c"]
s2_ids = [f"{DOC}:scheme2_6a", f"{DOC}:scheme2_6b", f"{DOC}:scheme2_6c"]
s4_ids = [f"{DOC}:scheme4_x_i", f"{DOC}:scheme4_x_br", f"{DOC}:scheme4_x_cl"]

coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1,
            "state": "attempted",
            "regions": [
                {
                    "region": "title, abstract, and keywords",
                    "finding": "Article scope states substituted allenoate hydrohalogenation and subsequent coupling; no individual arrow or table row appears in this region.",
                    "evidence_ids": ev(1),
                },
                {
                    "region": "middle body paragraphs",
                    "finding": "Prior literature/background describes unsubstituted allenoate hydrohalogenation and earlier HX reactions; these were not converted into current-paper experiments.",
                    "evidence_ids": ev(1),
                },
                {
                    "region": "bottom paragraph continuing onto page 2",
                    "finding": "Current NaI/HOAc trials are introduced and resolved as Table 1 entries 1 and 2 on page 2.",
                    "evidence_ids": ev(1),
                },
            ],
            "record_ids": t1_ids[:2],
            "unresolved": [
                "No SI file is provided or associated.",
                "Page-1 prose does not provide row-complete charges or structures independently of Table 1.",
            ],
        },
        {
            "page": 2,
            "state": "attempted",
            "regions": [
                {
                    "region": "top prose",
                    "finding": "Explains selectivity changes for Table 1 entries 1-12 and identifies the R=Me and R=n-C3H7 substrate groups.",
                    "evidence_ids": ev(2),
                },
                {
                    "region": "Table 1 reaction header and rows 1-12",
                    "finding": "Twelve distinct optimization experiments, including mixed-product outcomes, low yields, footnote-defined NMR yields, a 40 °C override, and explicit not-observed product-3 outcomes.",
                    "evidence_ids": ev(2),
                },
                {
                    "region": "bottom prose introducing Scheme 1",
                    "finding": "States that 2a underwent Pd-catalyzed coupling and that alpha,beta-unsaturated alkenoates were not observed; the three arrows are on page 3.",
                    "evidence_ids": ev(2),
                },
            ],
            "record_ids": t1_ids,
            "unresolved": [
                "Most Table 1 rows lack row-specific charge, workup, purification, isolated mass, atmosphere, and concentration.",
                "Structures remain unverified and SMILES are intentionally absent.",
            ],
        },
        {
            "page": 3,
            "state": "attempted",
            "regions": [
                {
                    "region": "Scheme 1, three arrows",
                    "finding": "Three distinct current-paper coupling reactions of 2a give 4a (90%), 4b (70%), and 4c (85%).",
                    "evidence_ids": ev(3),
                },
                {
                    "region": "Scheme 2 reaction header and three rows",
                    "finding": "Three salt-mediated hydrohalogenation experiments of ethyl 2,3-pentadienoate report time, product, Z/E ratio, and yield.",
                    "evidence_ids": ev(3),
                },
                {
                    "region": "Scheme 3",
                    "finding": "2D NOESY assignment of Z-6a; treated as structural evidence attached to Scheme 2/6a, not as a separate synthetic experiment.",
                    "evidence_ids": ev(3),
                },
            ],
            "record_ids": s1_ids + s2_ids,
            "unresolved": [
                "Scheme 1 omits quantities, time, workup, purification, and yield basis.",
                "Scheme 2 omits reagent amounts, workup, purification, and yield basis.",
                "NOESY evidence assigns the major 6a isomer but does not verify a machine-readable structure.",
            ],
        },
        {
            "page": 4,
            "state": "attempted",
            "regions": [
                {
                    "region": "Scheme 4 and three-row outcome table",
                    "finding": "Three direct HX experiments (X=I, Br, Cl) report ester 6 and hydrolyzed acid 7 yields, including trace ester outcomes.",
                    "evidence_ids": ev(4),
                },
                {
                    "region": "reference 6 typical procedure",
                    "finding": "Detailed preparation is the same run as Table 1 entry 6 and was merged into that record, including charges, reaction, workup, isolated mass, and 95% yield.",
                    "evidence_ids": ev(4),
                },
                {
                    "region": "conclusion and references 1-5, 7",
                    "finding": "Conclusion and cited prior work; no additional current-paper reaction runs were created.",
                    "evidence_ids": ev(4),
                },
            ],
            "record_ids": s4_ids + [f"{DOC}:table1_entry_06"],
            "unresolved": [
                "Scheme 4 omits HX concentration/amount, solvent, workup, purification, and yield basis.",
                "The typical procedure does not report atmosphere or reaction concentration.",
            ],
        },
        {
            "page": 5,
            "state": "attempted",
            "regions": [
                {
                    "region": "reference 9 characterization paragraphs",
                    "finding": "Characterization data for 4a and 4c corroborate Scheme 1 products; these are not separate reaction runs.",
                    "evidence_ids": ev(5),
                },
                {
                    "region": "references 8 and 10-13",
                    "finding": "Bibliographic references and cited prior work only; no current-paper experiment or arrow is present.",
                    "evidence_ids": ev(5),
                },
            ],
            "record_ids": [f"{DOC}:scheme1_4a", f"{DOC}:scheme1_4c"],
            "unresolved": [
                "No characterization paragraph for 4b appears on this page.",
                "The printed formula/spectra are retained as source context but do not independently verify a structure or complete preparation.",
                "No SI file is provided or associated.",
            ],
        },
    ],
}

assert len(records) == 21
assert len(set(record_ids)) == len(record_ids)
assert [p["page"] for p in coverage["pages"]] == [1, 2, 3, 4, 5]
assert all(p["regions"] for p in coverage["pages"])

RAW_OUT.parent.mkdir(parents=True, exist_ok=True)
COVERAGE_OUT.parent.mkdir(parents=True, exist_ok=True)
RAW_OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
COVERAGE_OUT.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"records": len(records), "raw": str(RAW_OUT), "coverage": str(COVERAGE_OUT)}, ensure_ascii=False))
