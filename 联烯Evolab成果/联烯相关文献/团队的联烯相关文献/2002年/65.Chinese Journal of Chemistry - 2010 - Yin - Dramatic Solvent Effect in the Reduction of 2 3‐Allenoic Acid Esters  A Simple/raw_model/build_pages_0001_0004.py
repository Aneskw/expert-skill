#!/usr/bin/env python3
"""Build evidence-linked machine records for PDF pages 1-4.

The output is intentionally unreviewed.  Candidate structures are source-derived
from the fully specified table substituents and remain unverified.
"""
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "runs/current/raw_model/extracted_records_pages_0001_0004.json"
COVERAGE = ROOT / "runs/current/coverage/pages_0001_0004.json"
DOC = "doc_809f62cc21312ee8"


def ev(page: int) -> list[str]:
    return [f"{DOC}:page{page}:text", f"{DOC}:page{page}:image"]


def evs(*pages: int) -> list[str]:
    return [eid for page in pages for eid in ev(page)]


def fact(value, evidence):
    return {
        "value": value,
        "evidence_ids": list(evidence) if value is not None else list(evidence),
        "verification": "missing" if value is None else "unreviewed",
    }


def field(name: str, value, evidence, target=None):
    item = {"name": name, "fact": fact(value, evidence)}
    if target:
        item["target_entity_ids"] = list(target)
    return item


def participant(entity_id: str, role: str, label, name, smiles, evidence, amounts=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence),
        "smiles": fact(smiles, evidence),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": amounts or [],
    }


def amount(name: str, number: float, unit: str, evidence, raw_text: str | None = None):
    value = {"number": number, "unit": unit}
    if raw_text:
        value["raw_text"] = raw_text
    return field(name, value, evidence)


def missing_field(name: str, evidence, target=None):
    return field(name, None, evidence, target)


def base_record(suffix: str, source_id: str, kind: str, evidence, unresolved):
    return {
        "record_id": f"{DOC}:{suffix}",
        "document_id": DOC,
        "source_reaction_id": source_id,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": list(evidence),
        "participants": [],
        "steps": [],
        "outcomes": [],
        "notes": [],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": list(unresolved),
        },
    }


DIBAL_SMILES = "CC(C)C[AlH]CC(C)C"
SUBSTRATES = {
    "1a": ("ethyl 2-methyl-4-phenylbuta-2,3-dienoate", "CCOC(=O)C(C)=C=Cc1ccccc1"),
    "1b": ("ethyl 2-methyldeca-2,3-dienoate", "CCOC(=O)C(C)=C=CCCCCCC"),
    "1c": ("ethyl 2-allyl-4-phenylbuta-2,3-dienoate", "CCOC(=O)C(CC=C)=C=Cc1ccccc1"),
    "1d": ("ethyl 2-methylocta-2,3-dienoate", "CCOC(=O)C(C)=C=CCCCC"),
    "1e": ("ethyl 2-methyl-4-(1-naphthyl)buta-2,3-dienoate", "CCOC(=O)C(C)=C=Cc1cccc2ccccc12"),
    "1f": ("ethyl 2-benzylbuta-2,3-dienoate", "CCOC(=O)C(Cc1ccccc1)=C=C"),
    "1g": ("ethyl 2-propylbuta-2,3-dienoate", "CCOC(=O)C(CCC)=C=C"),
    "1h": ("ethyl 2-methylhepta-2,3-dienoate", "CCOC(=O)C(C)=C=CCCC"),
}
PRODUCTS = {
    "2a": ("2-methyl-4-phenylbuta-2,3-dien-1-ol", "CC(=C=Cc1ccccc1)CO"),
    "2b": ("2-methyldeca-2,3-dien-1-ol", "CC(=C=CCCCCCC)CO"),
    "2c": ("2-allyl-4-phenylbuta-2,3-dien-1-ol", "C=CCC(=C=Cc1ccccc1)CO"),
    "2d": ("2-methylocta-2,3-dien-1-ol", "CC(=C=CCCCC)CO"),
    "2e": ("2-methyl-4-(1-naphthyl)buta-2,3-dien-1-ol", "CC(=C=Cc1cccc2ccccc12)CO"),
    "2f": ("2-benzylbuta-2,3-dien-1-ol", "C=C=C(Cc1ccccc1)CO"),
    "2g": ("2-propylbuta-2,3-dien-1-ol", "C=C=C(CCC)CO"),
    "2h": ("2-methylhepta-2,3-dien-1-ol", "CC(=C=CCCC)CO"),
}


def core_participants(substrate: str, product: str, evidence, dibal_equiv: float, solvent: str):
    s_name, s_smiles = SUBSTRATES[substrate]
    p_name, p_smiles = PRODUCTS[product]
    result = [
        participant("substrate", "reactant", substrate, s_name, s_smiles, evidence),
        participant("product", "product", product, p_name, p_smiles, evidence),
        participant(
            "dibal_h",
            "reagent",
            "DIBAL-H",
            "diisobutylaluminum hydride",
            DIBAL_SMILES,
            evidence,
            [amount("equivalents", dibal_equiv, "equiv", evidence)],
        ),
    ]
    if solvent == "cyclohexane":
        result.append(participant("cyclohexane", "solvent", None, "cyclohexane", "C1CCCCC1", evidence))
    elif solvent == "ether":
        result.append(participant("diethyl_ether", "solvent", None, "diethyl ether", "CCOCC", evidence))
    elif solvent == "toluene":
        result.append(participant("toluene", "solvent", None, "toluene", "Cc1ccccc1", evidence))
    return result


records = []

# Table 1: distinct optimization rows. Entry 4 is also Table 2 entry 1.
table1 = [
    (1, 4.0, "cyclohexane", "r.t.", {"number": 1.5, "unit": "h"}, "complicated"),
    (2, 2.0, "ether", {"number": -78, "unit": "°C"}, {"number": 3.0, "unit": "h"}, 15),
    (3, 3.0, "ether", {"minimum": -140, "maximum": -90, "unit": "°C", "raw_text": "−90—−140 °C (as printed)"}, {"number": 3.5, "unit": "h"}, "complicated"),
]
for entry, equiv, reaction_solvent, temperature, time, result in table1:
    evidence = evs(1, 2)
    rec = base_record(
        f"table1_entry{entry}",
        f"Table 1 entry {entry}",
        "optimization_entry",
        evidence,
        [
            "Reaction scale and product isolation details are not reported for this optimization row.",
            "Yield measurement basis is not reported.",
            "Supporting information was not supplied or explicitly associated.",
        ],
    )
    # DIBAL-H is supplied in cyclohexane for entries 1-3; entries 2-3 additionally use ether.
    rec["participants"] = core_participants("1a", "2a", ev(2), equiv, reaction_solvent)
    if reaction_solvent == "ether":
        rec["participants"].append(
            participant("cyclohexane", "solvent", None, "cyclohexane (solvent for DIBAL-H)", "C1CCCCC1", ev(2))
        )
    rec["steps"] = [{
        "step_id": "reduction",
        "participant_ids": [p["entity_id"] for p in rec["participants"]],
        "conditions": [field("temperature", temperature, ev(2)), field("time", time, ev(2))],
    }]
    if result == "complicated":
        rec["outcomes"] = [
            field("reaction_result", "complicated mixture", evs(1, 2)),
            missing_field("yield", evs(1, 2), ["product"]),
            missing_field("yield_measurement_basis", evs(1, 2), ["product"]),
        ]
    else:
        rec["outcomes"] = [
            field("yield", {"number": result, "unit": "%"}, evs(1, 2), ["product"]),
            missing_field("yield_measurement_basis", evs(1, 2), ["product"]),
        ]
    if entry == 1:
        rec["notes"].append(fact("The separate reaction-solvent column is printed as a dash; cyclohexane is specified as the solvent for DIBAL-H.", ev(2)))
    records.append(rec)


# Table 1 entry 4 / Table 2 entry 1, enriched with the typical procedure.
evidence = evs(1, 2, 3)
rec = base_record(
    "table1_entry4_table2_entry1",
    "Table 1 entry 4 / Table 2 entry 1 (1a to 2a)",
    "optimization_entry",
    evidence,
    [
        "Atmosphere is not reported.",
        "Supporting information was not supplied or explicitly associated.",
        "Candidate SMILES remain unverified against an independently curated structure source.",
    ],
)
rec["participants"] = core_participants("1a", "2a", ev(2), 2.1, "toluene")
rec["participants"][0]["amounts"] = [amount("mass", 202, "mg", ev(2)), amount("amount", 1.0, "mmol", ev(2))]
rec["participants"][2]["amounts"] += [
    amount("volume", 2.1, "mL", ev(2)),
    amount("concentration", 1.0, "M", ev(2), "1.0 mol/L"),
    amount("amount", 2.1, "mmol", ev(2)),
]
rec["participants"][3]["amounts"] = [amount("volume", 1.0, "mL", ev(2))]
rec["participants"] += [
    participant("methanol", "reagent", None, "methanol (quench)", "CO", ev(2), [amount("volume", 0.5, "mL", ev(2))]),
    participant("hydrochloric_acid", "reagent", "HCl", "aqueous hydrochloric acid", "Cl", ev(2), [amount("volume", 25, "mL", ev(2)), amount("solution_concentration", 5, "%", ev(2))]),
    participant("extraction_ether", "solvent", None, "diethyl ether (extraction)", "CCOCC", ev(2)),
    participant("sodium_sulfate", "reagent", "Na2SO4", "sodium sulfate (drying agent)", "[Na+].[Na+].[O-]S(=O)(=O)[O-]", ev(2)),
]
rec["steps"] = [
    {
        "step_id": "reduction",
        "participant_ids": ["substrate", "dibal_h", "toluene"],
        "conditions": [
            field("operation", "DIBAL-H solution was added dropwise to the substrate solution; completion was monitored by TLC.", ev(2)),
            field("temperature", {"number": -78, "unit": "°C"}, evs(1, 2)),
            field("time", {"number": 5.0, "unit": "h"}, ev(2)),
        ],
    },
    {
        "step_id": "quench_workup_purification",
        "participant_ids": ["methanol", "hydrochloric_acid", "extraction_ether", "sodium_sulfate"],
        "conditions": [
            field("workup", "Quenched with methanol, washed with aqueous HCl, extracted with ether, dried over Na2SO4, filtered, and evaporated.", ev(2)),
            field("purification", "Silica-gel column chromatography; hexane/ethyl acetate 6:1 (v/v).", ev(2)),
        ],
    },
]
rec["outcomes"] = [
    field("product_mass", {"number": 133, "unit": "mg"}, ev(2), ["product"]),
    field("yield", {"number": 83, "unit": "%"}, evs(1, 2), ["product"]),
    field("yield_measurement_basis", "isolated after silica-gel column chromatography", ev(2), ["product"]),
    field("product_description", "white solid", ev(2), ["product"]),
    field("melting_point", {"minimum": 57, "maximum": 58, "unit": "°C", "raw_text": "57–58 °C (petroleum ether)"}, ev(3), ["product"]),
]
rec["notes"] = [fact("This is the same experiment reported as Table 1 entry 4 and Table 2 entry 1; it is represented once.", ev(2))]
records.append(rec)


scope = [
    # entry, substrate, product, time h, yield %, substrate mass/unit, substrate mmol,
    # product mass/unit, DIBAL volume mL, DIBAL mmol, separate toluene volume mL, pages
    (2, "1b", "2b", 3, 71, 210, "mg", 1.0, 119, "mg", 2.1, 2.1, 1.0, (2, 3)),
    (3, "1c", "2c", 6, 42, 228, "mg", 1.0, 75, "mg", 2.1, 2.1, 1.0, (1, 2, 3)),
    (4, "1d", "2d", 2, 76, 151, "mg", 0.83, 88, "mg", 2.1, 2.1, None, (2, 3)),
    (5, "1e", "2e", 5, 57, 133, "mg", 0.5, 65, "mg", 1.08, 1.08, None, (2, 3)),
    (6, "1f", "2f", 3, 85, 5.05, "g", 25, 3.42, "g", 52.5, 52.5, 70, (2, 3)),
    (7, "1g", "2g", 3, 53, 7.70, "g", 50, 2.94, "g", None, None, 150, (2, 3)),
    (8, "1h", "2h", 3, 63, 2.60, "g", 16.8, 1.34, "g", None, None, None, (2, 4)),
]

for entry, substrate, product, time_h, yield_pct, smass, smass_unit, smmol, pmass, pmass_unit, dvol, dmmol, tvol, pages in scope:
    evidence = evs(*pages)
    unresolved = [
        "Atmosphere, workup, and purification are not reported in this product paragraph.",
        "Yield measurement basis is not explicitly stated.",
        "Supporting information was not supplied or explicitly associated.",
        "Candidate SMILES remain unverified against an independently curated structure source.",
    ]
    if entry == 4:
        unresolved.append("The table header gives 2.1 equiv DIBAL-H, while the product paragraph reports 2.1 mmol for 0.83 mmol substrate; the discrepancy is preserved.")
    rec = base_record(
        f"table2_entry{entry}",
        f"Table 2 entry {entry} ({substrate} to {product})",
        "substrate_scope_entry",
        evidence,
        unresolved,
    )
    rec["participants"] = core_participants(substrate, product, ev(2), 2.1, "toluene")
    rec["participants"][0]["amounts"] = [
        amount("mass", smass, smass_unit, evidence),
        amount("amount", smmol, "mmol", evidence),
    ]
    if dvol is not None:
        rec["participants"][2]["amounts"] += [
            amount("volume", dvol, "mL", evidence),
            amount("concentration", 1.0, "M", evidence, "1.0 mol/L"),
        ]
    if dmmol is not None:
        rec["participants"][2]["amounts"].append(amount("amount", dmmol, "mmol", evidence))
    if tvol is not None:
        rec["participants"][3]["amounts"] = [amount("volume", tvol, "mL", evidence)]
    if entry == 3:
        rec["participants"].append(
            participant("unknown_product", "product", None, "unknown product", None, ev(2))
        )
    rec["steps"] = [{
        "step_id": "reduction",
        "participant_ids": ["substrate", "dibal_h", "toluene"],
        "conditions": [
            field("temperature", {"number": -78, "unit": "°C"}, ev(2)),
            field("time", {"number": time_h, "unit": "h"}, ev(2)),
        ],
    }]
    rec["outcomes"] = [
        field("product_mass", {"number": pmass, "unit": pmass_unit}, evidence, ["product"]),
        field("yield", {"number": yield_pct, "unit": "%"}, evidence, ["product"]),
        missing_field("yield_measurement_basis", evidence, ["product"]),
        field("product_description", "white solid" if entry == 5 else "yellow oil", evidence, ["product"]),
    ]
    if entry == 3:
        rec["outcomes"].append(field("co_product_observation", "an unknown product was also formed", evs(1, 2), ["unknown_product"]))
    if entry == 5:
        rec["outcomes"].append(field("melting_point", {"minimum": 56, "maximum": 57, "unit": "°C", "raw_text": "56–57 °C (petroleum ether)"}, ev(3), ["product"]))
    records.append(rec)


OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")

ids = {r["source_reaction_id"]: r["record_id"] for r in records}
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
                    "finding": "Current-work summary: DIBAL-H reduction of 2,3-allenoates to 2,3-allenols in toluene; this summary is context, not a separate experiment.",
                    "evidence_ids": [f"{DOC}:page1:image", f"{DOC}:page1:text"],
                },
                {
                    "region": "left-column Introduction",
                    "finding": "Prior synthetic approaches are cited as background literature; no individually specified current-paper experiment is reported in this region.",
                    "evidence_ids": [f"{DOC}:page1:image", f"{DOC}:page1:text"],
                },
                {
                    "region": "right-column Results and conclusion",
                    "finding": "Narrative reports the four Table 1 solvent/temperature experiments and specifically notes Table 2 entry 3 gives 2c in 42% yield with an unidentified product; these are linked to the table-row records rather than duplicated.",
                    "evidence_ids": [f"{DOC}:page1:image", f"{DOC}:page1:text"],
                },
            ],
            "record_ids": [
                ids["Table 1 entry 1"], ids["Table 1 entry 2"], ids["Table 1 entry 3"],
                ids["Table 1 entry 4 / Table 2 entry 1 (1a to 2a)"],
                ids["Table 2 entry 3 (1c to 2c)"],
            ],
            "unresolved": [
                "No SI was supplied or explicitly associated.",
                "The article does not explain the cause of the solvent effect.",
            ],
        },
        {
            "page": 2,
            "state": "attempted",
            "regions": [
                {
                    "region": "Table 1, scheme and rows 1-4",
                    "finding": "Four independent optimization conditions for 1a to target 2a; entries 1 and 3 give complicated mixtures, entry 2 gives 15%, and entry 4 gives 83%.",
                    "evidence_ids": [f"{DOC}:page2:image", f"{DOC}:page2:text"],
                },
                {
                    "region": "Table 2, general arrow, rows 1-8, and footnote",
                    "finding": "Eight scope rows under DIBAL-H/toluene at −78 °C; Table 2 entry 1 duplicates Table 1 entry 4, so seven additional records were created. Entry 3 footnote reports an unknown co-product.",
                    "evidence_ids": [f"{DOC}:page2:image", f"{DOC}:page2:text"],
                },
                {
                    "region": "Experimental starting-material paragraph and 1c/1f characterization",
                    "finding": "Starting materials 1a-1h are attributed to known procedures; only characterization of new 1c and 1f is supplied here, without a new preparative reaction record.",
                    "evidence_ids": [f"{DOC}:page2:image", f"{DOC}:page2:text"],
                },
                {
                    "region": "Typical procedure for 1a to 2a",
                    "finding": "Detailed reduction, quench, workup, chromatography, product mass, and yield were merged into the shared Table 1 entry 4/Table 2 entry 1 record.",
                    "evidence_ids": [f"{DOC}:page2:image", f"{DOC}:page2:text"],
                },
            ],
            "record_ids": [r["record_id"] for r in records],
            "unresolved": [
                "Yield basis is not stated for Table 1 rows 1-3 or Table 2 rows 2-8.",
                "The table's generic structures were expanded only as unverified candidate SMILES.",
                "Table 1 entry 3 prints a descending temperature expression (−90—−140 °C); normalized bounds retain the raw printed text.",
            ],
        },
        {
            "page": 3,
            "state": "attempted",
            "regions": [
                {
                    "region": "top-left continuation of 2a characterization",
                    "finding": "Continuation of the same 2a experiment; melting point and characterization are not a new reaction.",
                    "evidence_ids": [f"{DOC}:page3:image", f"{DOC}:page3:text"],
                },
                {
                    "region": "experimental blocks for 2b, 2c, and 2d",
                    "finding": "Product-specific starting amounts, DIBAL-H quantities, product masses, and yields enrich Table 2 entries 2-4; each remains a separate record.",
                    "evidence_ids": [f"{DOC}:page3:image", f"{DOC}:page3:text"],
                },
                {
                    "region": "experimental blocks for 2e, 2f, and 2g",
                    "finding": "Product-specific scales, product masses, yields, and descriptions enrich Table 2 entries 5-7; each remains a separate record.",
                    "evidence_ids": [f"{DOC}:page3:image", f"{DOC}:page3:text"],
                },
            ],
            "record_ids": [
                ids["Table 1 entry 4 / Table 2 entry 1 (1a to 2a)"],
                ids["Table 2 entry 2 (1b to 2b)"], ids["Table 2 entry 3 (1c to 2c)"],
                ids["Table 2 entry 4 (1d to 2d)"], ids["Table 2 entry 5 (1e to 2e)"],
                ids["Table 2 entry 6 (1f to 2f)"], ids["Table 2 entry 7 (1g to 2g)"],
            ],
            "unresolved": [
                "Workup and purification are not stated in the shorthand product paragraphs.",
                "For 2d, reported mmol imply a DIBAL-H ratio inconsistent with the 2.1-equiv table header.",
            ],
        },
        {
            "page": 4,
            "state": "attempted",
            "regions": [
                {
                    "region": "top-left experimental paragraph for 2h",
                    "finding": "Table 2 entry 8 continuation reports substrate scale, product mass, 63% yield, and product description; it was merged into that row record.",
                    "evidence_ids": [f"{DOC}:page4:image", f"{DOC}:page4:text"],
                },
                {
                    "region": "References 1-21 and article footer",
                    "finding": "Bibliography only; cited prior work is not represented as current-paper experiments, and no new reaction record was created.",
                    "evidence_ids": [f"{DOC}:page4:image", f"{DOC}:page4:text"],
                },
            ],
            "record_ids": [ids["Table 2 entry 8 (1h to 2h)"]],
            "unresolved": [
                "The 2h paragraph omits explicit DIBAL-H volume, solvent volume, workup, and purification details.",
            ],
        },
    ],
}
COVERAGE.parent.mkdir(parents=True, exist_ok=True)
COVERAGE.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"records": len(records), "raw": str(OUT), "coverage": str(COVERAGE)}, ensure_ascii=False))
