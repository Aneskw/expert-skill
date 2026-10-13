#!/usr/bin/env python3
"""Enrich source-faithful records for doc_960bc2f9d5111dda, PDF pages 7-9."""
from __future__ import annotations

import copy
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "runs/current"
DOC = "doc_960bc2f9d5111dda"


def ev(page: int) -> list[str]:
    return [f"{DOC}:page{page}:image", f"{DOC}:page{page}:text"]


def fact(value, evidence):
    return {
        "value": value,
        "evidence_ids": list(evidence) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def fld(name, value, evidence, targets=None):
    item = {"name": name, "fact": fact(value, evidence)}
    if targets:
        item["target_entity_ids"] = list(targets)
    return item


def qty(name, number, unit, evidence, **extra):
    return fld(name, {"number": number, "unit": unit, **extra}, evidence)


def participant(entity_id, role, label, evidence, smiles=None, amounts=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(None, []),
        "smiles": fact(smiles, evidence) if smiles else fact(None, []),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": amounts or [],
    }


data = json.loads((OUT / "dataset.json").read_text())
by_source = {r["source_reaction_id"]: copy.deepcopy(r) for r in data["experiments"]}
selected: list[dict] = []


def get(source_id: str) -> dict:
    record = by_source[source_id]
    selected.append(record)
    return record


def add_evidence(record: dict, *evidence_groups: list[str]) -> None:
    merged = list(record["evidence_ids"])
    for group in evidence_groups:
        merged.extend(group)
    record["evidence_ids"] = list(dict.fromkeys(merged))


def part(record: dict, entity_id: str) -> dict:
    return next(p for p in record["participants"] if p["entity_id"] == entity_id)


def set_amounts(record: dict, entity_id: str, amounts: list[dict]) -> None:
    part(record, entity_id)["amounts"] = amounts


def set_conditions(record: dict, fields: list[dict]) -> None:
    record["steps"] = [{
        "step_id": "step1",
        "participant_ids": [p["entity_id"] for p in record["participants"]],
        "conditions": fields,
    }]


def add_unresolved(record: dict, message: str) -> None:
    if message not in record["review"]["unresolved"]:
        record["review"]["unresolved"].append(message)


e7 = ev(7)
e8 = ev(8)
e78 = e7 + e8

# Page 7: analytical confirmation of the two preparatively separated benzyl esters.
r = get("scheme8_preparative_hplc_separation")
add_evidence(r, e7)
r["outcomes"] = [
    fld("peak1_dr", ">99:1", e7, ["peak1"]),
    fld("peak2_dr", ">98:2", e7, ["peak2"]),
    fld("analytical_HPLC_peak1_retention_time", {"number": 9.377, "unit": "min"}, e7, ["peak1"]),
    fld("analytical_HPLC_peak2_retention_time", {"number": 9.930, "unit": "min"}, e7, ["peak2"]),
]
r["notes"].append(fact(
    "The absolute configuration of peak 2 was assigned as (Ra,R) by comparison of optical-rotation sign with an independently prepared sample; peak 1 was then assigned as (Sa,R).",
    e7,
))
add_unresolved(r, "The analytical HPLC retention times on page 7 differ from the preparative separation retention times on page 6 because they use different columns/flow conditions; they are retained as distinct measurements.")

# Page 7: detailed hydrolysis corresponding to Scheme 8.
r = get("scheme8_hydrolysis_sa_r_13a")
add_evidence(r, e7)
set_amounts(r, "substrate", [qty("mass", 16, "mg", e7), qty("amount", 0.06, "mmol", e7)])
set_amounts(r, "reagent1", [qty("mass", 8, "mg", e7), qty("amount", 0.18, "mmol", e7)])
set_amounts(r, "solvent", [qty("water_volume", 0.3, "mL", e7), qty("MeOH_volume", 0.6, "mL", e7)])
set_conditions(r, [
    fld("temperature", {"number": 30, "unit": "°C"}, e7),
    fld("time", {"number": 12, "unit": "h"}, e7),
    fld("atmosphere", None, []),
    fld("workup", "acidified with 5% aqueous HCl to pH 1; ether extraction; water/brine washes; Na2SO4 drying; filtration and vacuum concentration", e7),
    fld("purification", "silica-gel chromatography, petroleum ether/ethyl acetate 20:1", e7),
])
r["outcomes"] = [
    fld("scheme_isolated_yield", {"number": 67, "unit": "%"}, ev(4), ["product"]),
    fld("detailed_batch_isolated_yield", {"number": 66, "unit": "%"}, e7, ["product"]),
    fld("product_mass", {"number": 7.1, "unit": "mg"}, e7, ["product"]),
]
add_unresolved(r, "Scheme 8 reports 67% while the detailed page-7 batch reports 66%; both source values are retained.")

# Page 7: detailed stages corresponding to Scheme 7.
r = get("scheme7_8a_to_12a")
add_evidence(r, e7)
set_amounts(r, "substrate", [qty("mass", 2.3543, "g", e7), qty("amount", 13, "mmol", e7)])
set_amounts(r, "reagent1", [qty("solution_volume", 14.0, "mL", e7), qty("concentration", 1, "M", e7), qty("amount", 14, "mmol", e7)])
set_amounts(r, "solvent", [qty("substrate_solution_volume", 20, "mL", e7)])
set_conditions(r, [
    fld("temperature", {"number": 0, "unit": "°C"}, e7),
    fld("time", {"number": 25, "unit": "min"}, e7),
    fld("atmosphere", None, []),
    fld("workup", "filtered through a 1.5 cm silica-gel plug and eluted with CH2Cl2; filtrate concentrated", e7),
    fld("purification", "flash chromatography on silica gel, petroleum ether (30–60 °C)/ether 5:1", e7),
])
r["outcomes"] = [
    fld("isolated_yield", {"number": 51, "unit": "%"}, e7, ["product"]),
    fld("product_mass", {"number": 0.7234, "unit": "g"}, e7, ["product"]),
]

r = get("scheme7_12a_to_acid")
add_evidence(r, e7)
set_amounts(r, "substrate", [qty("source_printed_mass", 34.1, "g", e7), qty("amount", 0.3, "mmol", e7)])
set_amounts(r, "reagent1", [qty("solution_volume", 0.65, "mL", e7), qty("concentration", 1, "M", e7), qty("amount", 0.65, "mmol", e7)])
set_amounts(r, "reagent2", [qty("mass", 6.8, "mg", e7), qty("amount", 0.03, "mmol", e7)])
r["participants"].append(participant(
    "reagent3", "reagent", "dimethyl sulfide", e7, "CSC",
    [qty("volume", 0.2, "mL", e7)],
))
set_amounts(r, "solvent", [qty("volume", 3.5, "mL", e7)])
set_conditions(r, [
    fld("temperature", {"number": -78, "unit": "°C"}, e7),
    fld("addition_time", {"number": 5, "unit": "min"}, e7),
    fld("time", {"number": 20, "unit": "min"}, e7),
    fld("atmosphere", None, []),
    fld("workup", "saturated aqueous NH4Cl quench; ether extraction (30 mL × 3); water/brine washes; Na2SO4 drying; filtration and concentration", e7),
    fld("purification", "flash chromatography on silica gel", e7),
])
r["outcomes"] = [
    fld("isolated_yield", {"number": 80, "unit": "%"}, e7, ["product"]),
    fld("product_mass", {"number": 0.0415, "unit": "g"}, e7, ["product"]),
]
add_unresolved(r, "The source image explicitly prints 34.1 g of 12a together with 0.3 mmol; this internally inconsistent pair is preserved without correction.")

r = get("scheme7_acid_to_10a")
add_evidence(r, e7)
set_amounts(r, "substrate", [qty("mass", 0.3229, "g", e7), qty("amount", 1.9, "mmol", e7)])
set_amounts(r, "reagent1", [qty("mass", 0.1441, "g", e7), qty("amount", 3.8, "mmol", e7)])
# The scheme and detailed paragraph name different solvents; keep both source statements.
part(r, "solvent")["entity_id"] = "scheme_solvent"
part(r, "scheme_solvent")["label"] = fact("THF (Scheme 7)", ev(4))
part(r, "scheme_solvent")["smiles"] = fact("C1CCOC1", ev(4))
r["participants"].append(participant(
    "detailed_batch_solvent", "solvent", "anhydrous diethyl ether", e7, "CCOCC",
    [qty("substrate_solution_volume", 3, "mL", e7), qty("suspension_volume", 15, "mL", e7)],
))
set_conditions(r, [
    fld("temperature", {"number": 0, "unit": "°C"}, ev(4)),
    fld("time", None, []),
    fld("atmosphere", None, []),
    fld("workup", None, []),
    fld("purification", None, []),
])
r["outcomes"] = [
    fld("isolated_yield", {"number": 43, "unit": "%"}, e7, ["product"]),
    fld("product_mass", {"number": 0.1284, "unit": "g"}, e7, ["product"]),
]
add_unresolved(r, "Scheme 7 labels THF, whereas the detailed page-7 batch explicitly uses anhydrous diethyl ether; both solvent statements are retained.")
add_unresolved(r, "The detailed paragraph invokes an earlier procedure and does not restate duration, workup, or purification.")

r = get("scheme7_10a_to_tosylate")
add_evidence(r, e7)
set_amounts(r, "substrate", [qty("mass", 0.1284, "g", e7), qty("amount", 0.8, "mmol", e7)])
set_amounts(r, "reagent1", [qty("mass", 0.4785, "g", e7), qty("amount", 2.5, "mmol", e7)])
set_amounts(r, "solvent", [qty("volume", 1, "mL", e7)])
set_conditions(r, [
    fld("temperature", None, []), fld("time", None, []), fld("atmosphere", None, []),
    fld("workup", None, []), fld("purification", "none; tosylate used in the next step without further purification", e7),
])
r["outcomes"] = [fld("stage_yield", None, [], ["product"])]

r = get("scheme7_tosylate_to_11a")
add_evidence(r, e7)
part(r, "product")["label"] = fact("(Ra,S)-3-methyldeca-4,5-dienenitrile", e7)
set_amounts(r, "reagent1", [qty("mass", 0.0482, "g", e7), qty("amount", 0.96, "mmol", e7)])
set_amounts(r, "solvent", [qty("volume", 2, "mL", e7)])
set_conditions(r, [
    fld("temperature", None, []), fld("time", None, []), fld("atmosphere", None, []),
    fld("workup", None, []), fld("purification", "none; nitrile used in the next step without further purification", e7),
])
r["outcomes"] = [fld("stage_yield", None, [], ["product"])]

r = get("scheme7_11a_to_1l")
add_evidence(r, e7)
part(r, "substrate")["label"] = fact("(Ra,S)-3-methyldeca-4,5-dienenitrile", e7)
set_amounts(r, "substrate", [qty("mass", 0.0814, "g", e7), qty("amount", 0.5, "mmol", e7)])
set_amounts(r, "reagent1", [qty("mass", 0.4, "g", e7), qty("amount", 10, "mmol", e7)])
set_amounts(r, "solvent", [qty("EtOH_volume", 2, "mL", e7), qty("water_volume", 0.6, "mL", e7)])
set_conditions(r, [
    fld("temperature", None, []), fld("time", None, []), fld("atmosphere", None, []),
    fld("workup", None, []), fld("purification", None, []),
])
r["outcomes"] = [
    fld("combined_yield_over_three_steps", {"number": 43, "unit": "%"}, e7, ["product"]),
    fld("product_mass", {"number": 0.0660, "unit": "g"}, e7, ["product"]),
]
add_unresolved(r, "The abbreviated hydrolysis invokes an earlier procedure but does not restate temperature, duration, workup, purification, or the hydrolysis-only yield.")

r = get("scheme7_1l_to_13a")
add_evidence(r, e7)
set_amounts(r, "substrate", [qty("mass", 8.9, "mg", e7), qty("amount", 0.055, "mmol", e7)])
set_amounts(r, "reagent1", [qty("mass", 16.9, "mg", e7), qty("amount", 0.165, "mmol", e7)])
set_amounts(r, "reagent2", [qty("mass", 5.4, "mg", e7), qty("amount", 0.044, "mmol", e7)])
set_amounts(r, "reagent3", [qty("mass", 13.6, "mg", e7), qty("amount", 0.06, "mmol", e7)])
set_amounts(r, "solvent", [qty("volume", 1, "mL", e7)])
set_conditions(r, [
    fld("addition_temperature", {"number": 0, "unit": "°C"}, e7),
    fld("temperature", "r.t.", e7),
    fld("time", {"number": 23.5, "unit": "h"}, e7),
    fld("atmosphere", None, []),
    fld("workup", "diluted with ether (10 mL), transferred, and evaporated", e7),
    fld("purification", "silica-gel chromatography", e7),
])
r["outcomes"] = [
    fld("isolated_yield", {"number": 100, "unit": "%"}, e7, ["product"]),
    fld("product_mass", {"number": 13.3, "unit": "mg"}, e7, ["product"]),
    fld("product_dr_by_HPLC", "96:4", e7, ["product"]),
]

# Pages 7-8: the detailed typical 2a batch is Table 2 entry 1, not a new reaction.
r = get("table2_entry1")
add_evidence(r, e7, e8)
set_amounts(r, "substrate", [qty("mass", 59.3, "mg", e7), qty("amount", 0.3, "mmol", e7)])
set_amounts(r, "reagent1", [qty("equivalents", 1.5, "equiv", ev(2)), qty("mass", 114.3, "mg", e7), qty("amount", 0.45, "mmol", e7)])
set_amounts(r, "solvent", [qty("volume", 4, "mL", e7)])
set_conditions(r, [
    fld("temperature", "r.t.", e7),
    fld("time", {"number": 1, "unit": "h"}, ev(2)),
    fld("atmosphere", None, []),
    fld("workup", "water quench followed by saturated aqueous Na2S2O3; ether extraction; brine wash; Na2SO4 drying and filtration", e7),
    fld("purification", "silica-gel chromatography, petroleum ether/ethyl acetate 5:1", e7),
])
r["outcomes"] = [
    fld("isolated_yield", {"number": 83, "unit": "%"}, e7, ["product"]),
    fld("product_mass", {"number": 81, "unit": "mg"}, e7, ["product"]),
    fld("Z_E_ratio", "98:2", e7, ["product"]),
    fld("Z_E_ratio_measurement_basis", "400 MHz 1H NMR spectroscopy after solvent evaporation", e7, ["product"]),
]

# Page 8: the detailed Conditions B batch is Table 2 entry 7.
r = get("table2_entry7")
add_evidence(r, e8)
set_amounts(r, "substrate", [qty("mass", 50.5, "mg", e8), qty("amount", 0.3, "mmol", e8)])
set_amounts(r, "reagent1", [qty("equivalents", 1.5, "equiv", ev(2)), qty("mass", 116.0, "mg", e8), qty("amount", 0.45, "mmol", e8)])
set_amounts(r, "reagent2", [qty("equivalents", 1, "equiv", ev(2)), qty("mass", 43.7, "mg", e8), qty("amount", 0.3, "mmol", e8)])
set_amounts(r, "solvent", [qty("volume", 4, "mL", e8)])
set_conditions(r, [
    fld("temperature", "r.t.", ev(2)),
    fld("pre_stirring_time_before_I2_addition", {"number": 20, "unit": "min"}, e8),
    fld("time_after_I2_addition", {"number": 1, "unit": "h"}, e8),
    fld("atmosphere", None, []),
    fld("workup", "sequential water and saturated aqueous Na2S2O3 quench; ether extraction; brine wash; Na2SO4 drying and filtration", e8),
    fld("purification", "flash chromatography on silica gel, petroleum ether/ethyl acetate 5:1", e8),
])
r["outcomes"] = [
    fld("isolated_yield", {"number": 87, "unit": "%"}, e8, ["product"]),
    fld("product_mass", {"number": 76.9, "unit": "mg"}, e8, ["product"]),
    fld("Z_E_ratio", "table dash (—)", ev(2), ["product"]),
]

# Page 8: detailed NIS/Cs2CO3 cyclization corresponding to Scheme 2.
r = get("scheme2_nis_ch2cl2_1a")
add_evidence(r, e8)
set_amounts(r, "substrate", [qty("mass", 396.0, "mg", e8), qty("amount", 2, "mmol", e8)])
set_amounts(r, "reagent1", [
    qty("initial_mass", 677.2, "mg", e8), qty("initial_amount", 3, "mmol", e8), qty("initial_equivalents", 1.5, "equiv", e8),
    qty("supplemental_mass", 225.1, "mg", e8), qty("supplemental_amount", 1, "mmol", e8), qty("supplemental_equivalents", 0.5, "equiv", e8),
    qty("total_equivalents", 2, "equiv", e8),
])
set_amounts(r, "reagent2", [qty("mass", 667.8, "mg", e8), qty("amount", 2, "mmol", e8), qty("equivalents", 1, "equiv", e8)])
set_amounts(r, "solvent", [qty("volume", 24, "mL", e8)])
r["steps"] = [
    {
        "step_id": "step1_initial_NIS",
        "participant_ids": [p["entity_id"] for p in r["participants"]],
        "conditions": [
            fld("operation", "Cs2CO3 added to substrate solution at r.t.; initial NIS added at −60 °C", e8),
            fld("temperature", {"number": -60, "unit": "°C"}, e8),
            fld("time", {"number": 10, "unit": "h"}, e8),
            fld("atmosphere", None, []),
        ],
    },
    {
        "step_id": "step2_supplemental_NIS_and_isolation",
        "participant_ids": [p["entity_id"] for p in r["participants"]],
        "conditions": [
            fld("operation", "0.5 equiv additional NIS added at −60 °C; after TLC completion mixture warmed to r.t.", e8),
            fld("temperature", {"number": -60, "unit": "°C"}, e8),
            fld("time", None, []),
            fld("workup", "sequential water and saturated aqueous Na2S2O3 quench; ether extraction; brine wash; Na2SO4 drying; filtration and evaporation", e8),
            fld("purification", "silica-gel chromatography, petroleum ether/ethyl acetate/CH2Cl2 6:1:1", e8),
        ],
    },
]
r["outcomes"] = [
    fld("scheme_reported_yield", {"number": 86, "unit": "%"}, ev(3), ["product"]),
    fld("detailed_batch_isolated_yield", {"number": 89, "unit": "%"}, e8, ["product"]),
    fld("product_mass", {"number": 575.8, "unit": "mg"}, e8, ["product"]),
    fld("Z_E_product_ratio", "85:15", e8, ["product"]),
    fld("major_Z_isomer_ee", {"number": 99, "unit": "%"}, e8, ["product"]),
    fld("ee_measurement_basis", "HPLC, Chiralcel OJ-H", e8, ["product"]),
]
add_unresolved(r, "Scheme 2 reports 86% while the detailed page-8 batch reports 89%; both source values are retained.")
add_unresolved(r, "The duration after the supplemental 0.5 equiv NIS addition is not stated.")

# Page 8: detailed kinetic resolution corresponding to Scheme 4.
r = get("scheme4_kinetic_resolution_2a")
add_evidence(r, e8)
set_amounts(r, "substrate", [qty("mass", 95.8, "mg", e8), qty("amount", 0.3, "mmol", e8)])
set_amounts(r, "reagent1", [
    fld("scheme_equivalents", {"minimum": 0.35, "maximum": 0.45, "unit": "equiv", "raw_text": "0.35–0.45 equiv"}, ev(3)),
    qty("mass", 5.4, "mg", e8), qty("amount", 0.096, "mmol", e8),
])
set_amounts(r, "reagent2", [qty("mass", 2.1, "mg", e8), qty("amount", 0.011, "mmol", e8), qty("catalyst_loading", 3.5, "mol%", e8)])
set_amounts(r, "reagent3", [qty("mass", 7.4, "mg", e8), qty("amount", 0.011, "mmol", e8), qty("catalyst_loading", 3.5, "mol%", e8)])
set_amounts(r, "reagent4", [
    fld("scheme_equivalents", {"minimum": 0.35, "maximum": 0.45, "unit": "equiv", "raw_text": "0.35–0.45 equiv"}, ev(3)),
    qty("mass", 8.3, "mg", e8), qty("amount", 0.11, "mmol", e8),
])
r["participants"].append(participant("solvent", "solvent", "CH3CN", e8, "CC#N", [qty("volume", 1, "mL", e8)]))
set_conditions(r, [
    fld("starting_Z_E_ratio", "85:15", e8),
    fld("temperature", {"number": 3, "unit": "°C"}, e8),
    fld("time", {"number": 1, "unit": "h"}, e8),
    fld("atmosphere", "nitrogen", e8),
    fld("workup", "water quench; ether dilution and separation; ether extraction; brine wash; Na2SO4 drying; filtration and evaporation", e8),
    fld("purification", "silica-gel chromatography, petroleum ether/ethyl acetate 6:1", e8),
])
r["outcomes"] = [
    fld("isolated_yield", {"number": 74, "unit": "%"}, e8, ["product"]),
    fld("product_mass", {"number": 70.9, "unit": "mg"}, e8, ["product"]),
    fld("scheme_product_Z_E_ratio", "99:1", ev(3), ["product"]),
    fld("detailed_batch_product_Z_E_ratio", "98:2", e8, ["product"]),
    fld("product_ee", {"number": 99, "unit": "%"}, e8, ["product"]),
    fld("ee_measurement_basis", "HPLC, Chiralcel OJ-H", e8, ["product"]),
]
r["notes"].append(fact("The page-3 prose calls the recovered 2a isomer (R)-(+)-(Z)-2a, whereas Scheme 4 and the detailed page-8 heading label it (S)-(+)-(Z)-2a.", ev(3) + e8))
add_unresolved(r, "Scheme 4 reports Z/E 99:1, the page-3 prose gives 96:4 in a combined sentence for 2a/2b, and the detailed page-8 batch reports 98:2; these statements are not reconciled.")
add_unresolved(r, "The source disagrees on the absolute-configuration label of recovered (Z)-2a; the Scheme 4/page-8 label is retained as the participant label, with the prose conflict noted.")

# Machine submissions remain candidates here; merge will quarantine them as needs_review.
for record in selected:
    record["status"] = "candidate"
    record["completeness"] = "partial"
    record["review"]["method"] = "none"
    record["review"]["reviewer"] = None
    record["review"]["checked_fields"] = []

raw_path = OUT / "raw_model/records_pages_0007_0009.json"
raw_path.write_text(json.dumps(selected, ensure_ascii=False, indent=2))

coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 7,
            "state": "attempted",
            "regions": [
                {
                    "region": "upper-left analytical characterizations of preparatively separated (Sa,R)-13a and (Ra,R)-13a",
                    "finding": "Analytical HPLC, d.r., optical-rotation, and assignment evidence linked to the existing Scheme 8 preparative-HPLC separation; no new reaction created.",
                    "evidence_ids": ev(7),
                },
                {
                    "region": "middle-left detailed hydrolysis of (Sa,R)-13a",
                    "finding": "Detailed 12 h LiOH hydrolysis merged into Scheme 8 hydrolysis; the scheme's 67% and detailed batch's 66% yields are both retained.",
                    "evidence_ids": ev(7),
                },
                {
                    "region": "lower-left and upper-right preparation of (Ra,R)-1l",
                    "finding": "TBAF deprotection, Cu/Grignard homologation, LiAlH4 reduction, tosylation, cyanide substitution, and nitrile hydrolysis enrich the existing Scheme 7 stage records.",
                    "evidence_ids": ev(7),
                },
                {
                    "region": "right-column benzylation to (Ra,R)-13a",
                    "finding": "Exact quantities, 23.5 h reaction, isolation, 100% yield, and d.r. merged into the existing Scheme 7 benzylation record.",
                    "evidence_ids": ev(7),
                },
                {
                    "region": "lower-right typical preparation of (Z)-2a beginning",
                    "finding": "Detailed batch corresponds to Table 2 entry 1 and continues on page 8; merged rather than duplicated.",
                    "evidence_ids": ev(7),
                },
            ],
            "record_ids": [
                f"{DOC}:scheme8_preparative_hplc_separation",
                f"{DOC}:scheme8_hydrolysis_sa_r_13a",
                f"{DOC}:scheme7_8a_to_12a",
                f"{DOC}:scheme7_12a_to_acid",
                f"{DOC}:scheme7_acid_to_10a",
                f"{DOC}:scheme7_10a_to_tosylate",
                f"{DOC}:scheme7_tosylate_to_11a",
                f"{DOC}:scheme7_11a_to_1l",
                f"{DOC}:scheme7_1l_to_13a",
                f"{DOC}:table2_entry1",
            ],
            "unresolved": [
                "Scheme 8 and the detailed hydrolysis report 67% and 66%, respectively.",
                "The source prints 34.1 g of 12a together with 0.3 mmol; the inconsistency is preserved.",
                "Scheme 7 names THF for the LiAlH4 reduction while the detailed batch names anhydrous ether.",
                "Several abbreviated stages do not restate duration, atmosphere, workup, purification, or stage-only yield.",
            ],
        },
        {
            "page": 8,
            "state": "attempted",
            "regions": [
                {
                    "region": "upper-left continuation of (Z)-2a characterization",
                    "finding": "Characterization continues the Table 2 entry 1 detailed batch from page 7; no independent experiment.",
                    "evidence_ids": ev(8),
                },
                {
                    "region": "upper/middle-left typical I2/K2CO3 iodocyclization of 1f",
                    "finding": "Exact Conditions B batch merged into Table 2 entry 7, including the 20 min pre-stir and 1 h after iodine addition.",
                    "evidence_ids": ev(8),
                },
                {
                    "region": "middle-left NIS/Cs2CO3 cyclization of optically active (R)-1a",
                    "finding": "Two-stage NIS addition and detailed 89% batch merged into Scheme 2; the scheme's 86% value is retained separately.",
                    "evidence_ids": ev(8),
                },
                {
                    "region": "lower-left Sonogashira kinetic resolution of the 2a Z/E mixture",
                    "finding": "Detailed 3 °C, 1 h, nitrogen procedure merged into Scheme 4; conflicting Z/E statements are retained.",
                    "evidence_ids": ev(8),
                },
                {
                    "region": "right column acknowledgements and references 1-20",
                    "finding": "No present-paper reaction arrow, table row, or new experimental procedure; cited works were not expanded into experiments.",
                    "evidence_ids": ev(8),
                },
            ],
            "record_ids": [
                f"{DOC}:table2_entry1",
                f"{DOC}:table2_entry7",
                f"{DOC}:scheme2_nis_ch2cl2_1a",
                f"{DOC}:scheme4_kinetic_resolution_2a",
            ],
            "unresolved": [
                "Scheme 2 reports 86% while the detailed NIS batch reports 89%; the post-supplement NIS duration is absent.",
                "Scheme 4, its prose, and the detailed kinetic-resolution batch give nonmatching Z/E values and disagree on the absolute-configuration label for recovered (Z)-2a.",
                "No supporting-information file was supplied or explicitly associated.",
            ],
        },
        {
            "page": 9,
            "state": "attempted",
            "regions": [
                {
                    "region": "references 20-26, note 24, received/published dates, and otherwise blank page",
                    "finding": "No present-paper experiment. Note 24 summarizes loss of axial chirality during TBAF desilylation and cites prior work; it is contextual commentary, not an additional reaction record.",
                    "evidence_ids": ev(9),
                },
            ],
            "record_ids": [],
            "unresolved": [
                "Reference-only content was not expanded into experimental records.",
                "The extent of axial-chirality loss in note 24 is qualitative and not assigned a numeric outcome.",
            ],
        },
    ],
}
coverage_path = OUT / "coverage/pages_0007_0009.json"
coverage_path.write_text(json.dumps(coverage, ensure_ascii=False, indent=2))

tasks_path = OUT / "tasks.json"
tasks = json.loads(tasks_path.read_text())
for task in tasks:
    if task["document_id"] == DOC and task["evidence_id"] in {f"{DOC}:page{p}:text" for p in range(7, 10)}:
        task["state"] = "attempted"
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2))

print(json.dumps({"updated_records": len(selected), "raw": str(raw_path), "coverage": str(coverage_path)}, ensure_ascii=False))
