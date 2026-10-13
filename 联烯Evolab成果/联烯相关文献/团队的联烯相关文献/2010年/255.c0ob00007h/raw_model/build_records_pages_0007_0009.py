#!/usr/bin/env python3
"""Enrich existing records with source facts from PDF pages 7-9."""
from __future__ import annotations

import copy
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
DATASET = ROOT / "runs/current/dataset.json"
OUT = ROOT / "runs/current/raw_model/records_pages_0007_0009.json"
COVERAGE = ROOT / "runs/current/coverage/pages_0007_0009.json"
TASKS = ROOT / "runs/current/tasks.json"
DOC = "doc_384261d36d616986"


def ev(page: int) -> list[str]:
    return [f"{DOC}:page{page}:image", f"{DOC}:page{page}:text"]


def fact(value, evidence):
    return {
        "value": value,
        "evidence_ids": list(dict.fromkeys(evidence)) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def qty(number, unit, raw_text=None):
    value = {"number": number, "unit": unit}
    if raw_text is not None:
        value["raw_text"] = raw_text
    return value


def fld(name, value, evidence, targets=None):
    result = {"name": name, "fact": fact(value, evidence)}
    if targets:
        result["target_entity_ids"] = list(targets)
    return result


def participant(entity_id, role, label, evidence, name=None, smiles=None, amounts=None):
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


def add_evidence(record, *pages):
    record["evidence_ids"] = list(dict.fromkeys(
        record["evidence_ids"] + [eid for page in pages for eid in ev(page)]
    ))


def entity(record, entity_id):
    return next(p for p in record["participants"] if p["entity_id"] == entity_id)


def outcome(record, name):
    return next(o for o in record["outcomes"] if o["name"] == name)


dataset = json.loads(DATASET.read_text())
existing = {r["record_id"]: r for r in dataset["experiments"]}
records = []

# Page 7 continues the characterization of Z-3j from page 6. No new batch is
# created, but the existing record now cites the continuation explicitly.
rid_3j = f"{DOC}:table2_entry10_z-3j"
r3j = copy.deepcopy(existing[rid_3j])
add_evidence(r3j, 7)
r3j["review"]["unresolved"] = [
    "Supporting Information was not explicitly associated; the candidate structure remains unverified.",
    "Spectral and analytical characterization on pages 6-7 was observed but not atom-by-atom interpreted.",
]
records.append(r3j)


# Detailed racemic hydration batches 11-18 on page 7. They are the same
# experiments as Table 2 rows 11-18, so those records are enriched in place.
scope = {
    11: {"substrate": "1k", "mass": 72.4, "mmol": 0.30, "hoac": 3.0, "time": 24,
         "product": "Z-3k", "name": "3-phenyl-3-(phenylsulfinyl)prop-2(Z)-en-1-ol",
         "smiles": "OCC=C(S(=O)c1ccccc1)c1ccccc1", "purification": "petroleum ether/ethyl acetate = 1:1",
         "yield": 51, "products": [("product", 39.8)]},
    12: {"substrate": "1l", "mass": 61.7, "mmol": 0.30, "hoac": 3.0, "time": 24,
         "product": "Z-3l", "name": "3-(phenylsulfinyl)hexa-2(Z)-5-dien-1-ol",
         "smiles": "OCC=C(CC=C)S(=O)c1ccccc1", "purification": "petroleum ether/ethyl acetate = 1:1",
         "yield": 64, "products": [("product", 43.0)]},
    13: {"substrate": "1m", "mass": 55.5, "mmol": 0.30, "hoac": 3.0, "time": 24,
         "product": "Z-3m", "name": "2-methyl-4-(phenylsulfinyl)but-3(Z)-en-2-ol",
         "smiles": "CC(C)(O)C=CS(=O)c1ccccc1", "purification": "petroleum ether/ethyl acetate = 2:3",
         "yield": 58, "products": [("product", 35.4)]},
    14: {"substrate": "1n", "mass": 66.8, "mmol": 0.30, "hoac": 3.0, "time": 24,
         "product": "Z-3n", "name": "3-ethyl-1-(phenylsulfinyl)pent-1(Z)-en-3-ol",
         "smiles": "CCC(O)(CC)C=CS(=O)c1ccccc1", "purification": "petroleum ether/ethyl acetate = 1:1",
         "yield": 76, "products": [("product", 54.9)]},
    15: {"substrate": "1o", "mass": 75.2, "mmol": 0.30, "hoac": 3.0, "time": 24,
         "product": "Z-3o", "name": "3-propyl-1-(phenylsulfinyl)hex-1(Z)-en-3-ol",
         "smiles": "CCCC(O)(CCC)C=CS(=O)c1ccccc1", "purification": "petroleum ether/ethyl acetate = 3:1",
         "yield": 71, "products": [("product", 57.2)]},
    16: {"substrate": "1p", "mass": 107.0, "mmol": 0.39, "hoac": 4.0, "time": 23.5,
         "product": "Z-3p", "name": "3-butyl-1-(phenylsulfinyl)sept-1(Z)-en-3-ol (source wording)",
         "smiles": "CCCCC(O)(CCCC)C=CS(=O)c1ccccc1", "purification": "petroleum ether/ethyl acetate = 2.5:1",
         "yield": 69, "products": [("product", 78.1)]},
    17: {"substrate": "1q", "mass": 75.9, "mmol": 0.30, "hoac": 3.0, "time": 24,
         "product": "Z-3q", "name": "2-phenyl-4-(phenylsulfinyl)but-3(Z)-en-2-ol",
         "smiles": "CC(O)(c1ccccc1)C=CS(=O)c1ccccc1", "purification": "petroleum ether/ethyl acetate = 1:1",
         "yield": 48, "products": [("product_less_polar", 23.0), ("product_more_polar", 16.1)]},
    18: {"substrate": "1r", "mass": 86.0, "mmol": 0.30, "hoac": 3.0, "time": 24,
         "product": "Z-3r", "name": "4-(p-bromophenylsulfinyl)hex-3(Z)-en-2-ol",
         "smiles": "CC(O)C=C(CC)S(=O)c1ccc(Br)cc1", "purification": "petroleum ether/ethyl acetate = 3:1",
         "yield": 68, "products": [("product_less_polar", 23.9), ("product_more_polar", 38.7)]},
}

workup_participants = [
    participant("workup_bicarbonate", "reagent", "saturated aqueous NaHCO3", ev(5),
                "sodium bicarbonate", "O=C([O-])O.[Na+]"),
    participant("workup_ether", "solvent", "diethyl ether", ev(5), "diethyl ether", "CCOCC"),
    participant("drying_sodium_sulfate", "reagent", "anhydrous Na2SO4", ev(5),
                "sodium sulfate", "[Na+].[Na+].[O-]S(=O)(=O)[O-]"),
]

for entry, row in scope.items():
    rid = f"{DOC}:table2_entry{entry}_{row['product'].lower()}"
    rec = copy.deepcopy(existing[rid])
    add_evidence(rec, 5, 7, *( [8] if entry == 18 else [] ))
    sub = entity(rec, "substrate")
    sub["amounts"] = [
        fld("mass", qty(row["mass"], "mg"), ev(7)),
        fld("amount", qty(row["mmol"], "mmol"), ev(7)),
    ]
    entity(rec, "hoac")["amounts"] = [fld("volume", qty(row["hoac"], "mL"), ev(7))]

    rec["participants"] = [p for p in rec["participants"] if p["role"] != "product"]
    product_ids = []
    for pid, _mass in row["products"]:
        product_ids.append(pid)
        qualifier = ""
        if pid.endswith("less_polar"):
            qualifier = ", less polar sulfoxide diastereomer"
        elif pid.endswith("more_polar"):
            qualifier = ", more polar sulfoxide diastereomer"
        rec["participants"].append(participant(
            pid, "product", row["product"] + qualifier, ev(7), row["name"] + qualifier,
            row["smiles"]
        ))
    present_ids = {p["entity_id"] for p in rec["participants"]}
    for p in workup_participants:
        if p["entity_id"] not in present_ids:
            rec["participants"].append(copy.deepcopy(p))

    rec["steps"][0]["conditions"] = [
        fld("temperature", qty(60, "°C"), ev(7)),
        fld("time", qty(row["time"], "h"), ev(7)),
    ]
    rec["steps"] = [rec["steps"][0], {
        "step_id": "isolation",
        "participant_ids": ["workup_bicarbonate", "workup_ether", "drying_sodium_sulfate"] + product_ids,
        "conditions": [
            fld("workup", "quenched/washed with saturated aqueous NaHCO3, extracted with diethyl ether, dried over anhydrous Na2SO4, filtered and evaporated according to the Z-3a typical procedure", ev(5)),
            fld("purification", "silica-gel chromatography, " + row["purification"], ev(7)),
        ],
    }]
    outcome(rec, "isolated_yield")["target_entity_ids"] = product_ids
    outcome(rec, "isolated_yield")["fact"] = fact(qty(row["yield"], "%"), ev(7))
    if any(o["name"] == "diastereomer_ratio" for o in rec["outcomes"]):
        outcome(rec, "diastereomer_ratio")["target_entity_ids"] = product_ids
    rec["outcomes"] = [o for o in rec["outcomes"] if not o["name"].endswith("_mass")]
    for pid, mass in row["products"]:
        rec["outcomes"].append(fld(f"{pid}_mass", qty(mass, "mg"), ev(7), [pid]))
    rec["review"]["unresolved"] = [
        "Supporting Information was not explicitly associated.",
        "Candidate connectivities derived from the fully specified product names remain structure-unverified; sulfoxide stereochemistry is not encoded.",
        "Spectral and analytical characterization was observed but not atom-by-atom interpreted.",
    ]
    records.append(rec)


# Detailed enantioenriched batches 19-21 on page 8 enrich Table 3 entries.
chiral = {
    1: {"label": "(R)-1d", "mass": 118.2, "mmol": 0.50, "hoac": 5.0,
        "product": "(R)-Z-3d", "name": "1-(phenylsulfinyl)oct-1(Z)-en-3(R)-ol",
        "smiles": "CCCCCC(O)C=CS(=O)c1ccccc1", "masses": [38.7, 46.6],
        "purification": "petroleum ether/ethyl acetate = 2:1", "yield": 68,
        "ee": [97.7, 96.5], "hplc": "Chiralcel OJ-H, n-hexane/i-PrOH = 90:10, 0.5 mL min-1, 254 nm"},
    2: {"label": "(R)-1c", "mass": 73.9, "mmol": 0.30, "hoac": 3.0,
        "product": "(R)-Z-3c", "name": "1-(phenylsulfinyl)non-1(Z)-en-3(R)-ol",
        "smiles": "CCCCCCC(O)C=CS(=O)c1ccccc1", "masses": [20.5, 31.2],
        "purification": "the Z-3a typical procedure (no row-specific eluent ratio stated)", "yield": 65,
        "ee": [98.9, 98.6], "hplc": "Chiralcel OJ-H, n-hexane/i-PrOH = 95:5, 0.5 mL min-1, 254 nm"},
    3: {"label": "(R)-1r", "mass": 84.4, "mmol": 0.30, "hoac": 3.0,
        "product": "(R)-Z-3r", "name": "4-(p-bromophenylsulfinyl)hex-3(Z)-en-2(R)-ol",
        "smiles": "CC(O)C=C(CC)S(=O)c1ccc(Br)cc1", "masses": [26.3, 40.1],
        "purification": "petroleum–ethyl acetate = 2:1 (source wording)", "yield": 74,
        "ee": [95.5, 94.1], "hplc": "Chiralcel OJ-H, n-hexane/i-PrOH = 90:10, 0.5 mL min-1, 254 nm"},
}

for entry, row in chiral.items():
    rid = f"{DOC}:table3_entry{entry}_{row['label'].lower().replace('(', '').replace(')', '')}"
    rec = copy.deepcopy(existing[rid])
    add_evidence(rec, 5, 8)
    sub = entity(rec, "chiral_substrate")
    sub["amounts"] = [
        fld("mass", qty(row["mass"], "mg"), ev(8)),
        fld("amount", qty(row["mmol"], "mmol"), ev(8)),
    ]
    entity(rec, "hoac")["amounts"] = [fld("volume", qty(row["hoac"], "mL"), ev(8))]
    rec["outcomes"] = [o for o in rec["outcomes"] if not (
        o["name"].endswith("_mass")
        or o["name"].endswith("_detailed_experiment_ee")
        or o["name"].endswith("_ee_measurement_basis")
    )]
    for idx, pid in enumerate(("product_isomer_1", "product_isomer_2")):
        p = entity(rec, pid)
        polarity = "less polar" if idx == 0 else "more polar"
        p["label"] = fact(f"{row['product']}, {polarity} sulfoxide diastereomer", ev(8))
        p["name"] = fact(f"{row['name']}, {polarity} sulfoxide diastereomer", ev(8))
        p["smiles"] = fact(row["smiles"], ev(8))
        p["structure_verified"] = False
    present_ids = {p["entity_id"] for p in rec["participants"]}
    for p in workup_participants:
        if p["entity_id"] not in present_ids:
            rec["participants"].append(copy.deepcopy(p))
    rec["steps"][0]["conditions"] = [
        fld("temperature", qty(60, "°C"), ev(8)),
        fld("time", qty(24, "h"), ev(8)),
    ]
    rec["steps"] = [rec["steps"][0], {
        "step_id": "isolation",
        "participant_ids": ["workup_bicarbonate", "workup_ether", "drying_sodium_sulfate", "product_isomer_1", "product_isomer_2"],
        "conditions": [
            fld("workup", "typical hydration workup with saturated aqueous NaHCO3, diethyl ether extraction, and anhydrous Na2SO4 drying", ev(5)),
            fld("purification", row["purification"], ev(8) if entry != 2 else ev(5) + ev(8)),
        ],
    }]
    outcome(rec, "combined_isolated_yield")["fact"] = fact(qty(row["yield"], "%"), ev(8))
    for idx, pid in enumerate(("product_isomer_1", "product_isomer_2")):
        rec["outcomes"].append(fld(f"{pid}_mass", qty(row["masses"][idx], "mg"), ev(8), [pid]))
        rec["outcomes"].append(fld(f"{pid}_detailed_experiment_ee", qty(row["ee"][idx], "%"), ev(8), [pid]))
        rec["outcomes"].append(fld(f"{pid}_ee_measurement_basis", row["hplc"], ev(8), [pid]))
    if entry == 1:
        discrepancy = "Table 3 reports 97.6% ee for the first product isomer, whereas the detailed experiment reports 97.7% ee; both source values are retained in distinct outcome fields."
        if not any(n["value"] == discrepancy for n in rec["notes"]):
            rec["notes"].append(fact(discrepancy, ev(4) + ev(8)))
    rec["review"]["unresolved"] = [
        "Supporting Information was not explicitly associated.",
        "Candidate product connectivities remain structure-unverified; sulfoxide stereochemistry is not encoded in SMILES.",
        "HPLC, rotation, spectral, and analytical data were observed, but only reaction-relevant ee measurement bases were structured.",
    ]
    records.append(rec)


# Section 22 starts on page 8 and continues on page 9. It is the detailed
# version of equation 1 and therefore replaces/enriches that existing record.
rid_d = f"{DOC}:eq1_deuterium_labeling_z3h_d"
rd = copy.deepcopy(existing[rid_d])
add_evidence(rd, 8, 9)
entity(rd, "substrate_1h")["amounts"] = [
    fld("mass", qty(90.3, "mg"), ev(9)),
    fld("amount", qty(0.30, "mmol"), ev(9)),
]
entity(rd, "doac")["amounts"] = [fld("volume", qty(3.0, "mL"), ev(9))]
entity(rd, "d2o")["amounts"] = [
    fld("equivalents", qty(1, "equiv"), ev(3)),
    fld("volume", qty(6, "uL", "6 μL"), ev(9)),
]
pd = entity(rd, "product_z3h_d")
pd["label"] = fact("Z-3h-D", ev(8) + ev(9))
pd["name"] = fact("2-deuterium-3-ethyl-1-phenyl-1-(phenylsulfinyl)pent-1(Z)-en-3-ol", ev(8) + ev(9))
pd["smiles"] = fact(None, [])
rd["participants"] = [p for p in rd["participants"] if p["entity_id"] not in {
    "workup_bicarbonate", "workup_ether", "drying_sodium_sulfate"
}]
rd["participants"] += [
    participant("workup_bicarbonate", "reagent", "saturated aqueous NaHCO3", ev(5),
                "sodium bicarbonate", "O=C([O-])O.[Na+]"),
    participant("workup_ether", "solvent", "diethyl ether", ev(5), "diethyl ether", "CCOCC"),
    participant("drying_sodium_sulfate", "reagent", "anhydrous Na2SO4", ev(5),
                "sodium sulfate", "[Na+].[Na+].[O-]S(=O)(=O)[O-]"),
]
rd["steps"] = [{
    "step_id": "deuterium_labeling",
    "participant_ids": ["substrate_1h", "doac", "d2o"],
    "conditions": [
        fld("temperature", "r.t.", ev(9)),
        fld("time", qty(24, "h"), ev(9)),
        fld("atmosphere", "N2", ev(9)),
    ],
}, {
    "step_id": "isolation",
    "participant_ids": ["workup_bicarbonate", "workup_ether", "drying_sodium_sulfate", "product_z3h_d"],
    "conditions": [
        fld("workup", "typical hydration workup with saturated aqueous NaHCO3, diethyl ether extraction, and anhydrous Na2SO4 drying", ev(5)),
        fld("purification", "petroleum–ethyl acetate = 3:1 (source wording)", ev(9)),
    ],
}]
outcome(rd, "isolated_yield")["fact"] = fact(qty(78, "%"), ev(9))
rd["outcomes"] = [o for o in rd["outcomes"] if o["name"] != "product_mass"]
rd["outcomes"].append(fld("product_mass", qty(85.3, "mg"), ev(9), ["product_z3h_d"]))
temperature_discrepancy = "The Results-and-Discussion summary on page 3 states typical conditions of 60 °C, while the detailed section 22 batch on page 9 explicitly states room temperature under N2; the detailed batch temperature is used in the experimental step and the discrepancy is retained."
if not any(n["value"] == temperature_discrepancy for n in rd["notes"]):
    rd["notes"].append(fact(temperature_discrepancy, ev(3) + ev(9)))
rd["review"]["unresolved"] = [
    "Supporting Information was not explicitly associated.",
    "The page-3 60 °C versus page-9 room-temperature discrepancy requires source-author clarification.",
    "The isotopologue connectivity/stereochemistry is not encoded as a source-verified SMILES.",
]
records.append(rd)


assert len(records) == 13
assert len({r["record_id"] for r in records}) == 13
OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")

coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 7,
            "state": "attempted",
            "regions": [
                {"region": "top-left continuation of Z-3j characterization", "finding": "The page completes analytical characterization for the existing Table 2 entry 10 batch; no separate reaction was created.", "evidence_ids": ev(7)},
                {"region": "left column sections 11-14", "finding": "Detailed hydration batches for Z-3k through Z-3n were merged into Table 2 entries 11-14 with exact substrate masses/scales, HOAc volume, 60 °C/24 h, purification ratios, product masses, and isolated yields.", "evidence_ids": ev(7)},
                {"region": "right column sections 15-18", "finding": "Detailed hydration batches for Z-3o through Z-3r were merged into Table 2 entries 15-18, including the 0.39 mmol/23.5 h override for Z-3p and separate polar-isomer masses for Z-3q/Z-3r.", "evidence_ids": ev(7)},
            ],
            "record_ids": [f"{DOC}:table2_entry{i}_z-3{chr(96+i)}" for i in range(10, 19)],
            "unresolved": ["Candidate structures and sulfoxide stereochemistry remain machine-unverified; spectral data were not atom-by-atom interpreted."],
        },
        {
            "page": 8,
            "state": "attempted",
            "regions": [
                {"region": "upper-left continuation of section 18", "finding": "Analytical characterization for both Z-3r polar isomers completes the existing Table 2 entry 18 record; it is not a new reaction.", "evidence_ids": ev(8)},
                {"region": "sections 19-21 across both columns", "finding": "Three detailed enantioenriched hydrations were merged into Table 3 entries 2, 1, and 3 respectively, retaining exact batch quantities, paired product masses, combined yields, product ee values, and HPLC measurement conditions.", "evidence_ids": ev(8)},
                {"region": "bottom-right start of section 22", "finding": "The title and opening of the deuterium-labeling preparation continue onto page 9 and were merged with the existing equation 1 record.", "evidence_ids": ev(8)},
            ],
            "record_ids": [
                f"{DOC}:table2_entry18_z-3r",
                f"{DOC}:table3_entry2_r-1c",
                f"{DOC}:table3_entry1_r-1d",
                f"{DOC}:table3_entry3_r-1r",
                f"{DOC}:eq1_deuterium_labeling_z3h_d",
            ],
            "unresolved": ["Table 3 gives 97.6% ee for the first Z-3d isomer while section 20 gives 97.7%; both are retained.", "Absolute sulfur configurations are not encoded in candidate SMILES."],
        },
        {
            "page": 9,
            "state": "attempted",
            "regions": [
                {"region": "upper-left continuation of section 22", "finding": "Detailed Z-3h-D batch provides 1h 90.3 mg/0.30 mmol, DOAc 3.0 mL, D2O 6 μL, room temperature, N2, 24 h, 85.3 mg, and 78% isolated yield; merged with equation 1.", "evidence_ids": ev(9)},
                {"region": "lower-left acknowledgements and references", "finding": "No new reaction experiment is reported; acknowledgements and literature citations were inspected and not converted into current-work batches.", "evidence_ids": ev(9)},
                {"region": "right-column references 3-9 and crystallographic notes", "finding": "These are cited prior works and crystallographic characterization/deposition details for already recorded products, not independent reaction experiments.", "evidence_ids": ev(9)},
            ],
            "record_ids": [f"{DOC}:eq1_deuterium_labeling_z3h_d"],
            "unresolved": ["Page 3 states 60 °C for the labeling experiment, whereas the detailed page-9 batch states room temperature; the detailed batch condition is recorded and the conflict remains unresolved.", "No Supporting Information file was explicitly supplied or associated."],
        },
    ],
}

assert [p["page"] for p in coverage["pages"]] == [7, 8, 9]
assert all(p["state"] == "attempted" and p["regions"] for p in coverage["pages"])
all_ids = set(existing)
assert all(rid in all_ids for p in coverage["pages"] for rid in p["record_ids"])
COVERAGE.parent.mkdir(parents=True, exist_ok=True)
COVERAGE.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

tasks = json.loads(TASKS.read_text())
target_tasks = {f"{DOC}:page{i}:text" for i in range(7, 10)}
for task in tasks:
    if task["task_id"] in target_tasks:
        task["state"] = "attempted"
        task["reason"] = "Original page image and extracted text inspected; existing cross-page experiments enriched and coverage recorded."
TASKS.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"replacement_records": len(records), "coverage_pages": 3, "output": str(OUT)}, ensure_ascii=False))
