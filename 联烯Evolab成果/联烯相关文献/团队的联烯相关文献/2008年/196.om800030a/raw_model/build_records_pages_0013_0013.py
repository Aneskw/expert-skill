#!/usr/bin/env python3
"""Build evidence-linked record replacements for PDF page 13."""

import copy
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CURRENT = ROOT / "runs" / "current"
DOC = "doc_9ba0460dd1a6041e"


def ev(page, kind="text"):
    return f"{DOC}:page{page}:{kind}"


P9 = (ev(9, "text"), ev(9, "image"))
P13 = (ev(13, "text"), ev(13, "image"))


def fact(value, evidence=()):
    return {
        "value": value,
        "evidence_ids": list(dict.fromkeys(evidence)),
        "verification": "missing" if value is None else "unreviewed",
    }


def field(name, value, evidence=(), targets=()):
    result = {"name": name, "fact": fact(value, evidence)}
    if targets:
        result["target_entity_ids"] = list(targets)
    return result


def quantity(name, number, unit, evidence=P13):
    return field(name, {"number": number, "unit": unit}, evidence)


def add_evidence(record, evidence):
    record["evidence_ids"] = list(dict.fromkeys(record["evidence_ids"] + list(evidence)))


def set_condition(record, name, value, evidence):
    conditions = record["steps"][0]["conditions"]
    conditions[:] = [item for item in conditions if item["name"] != name]
    conditions.append(field(name, value, evidence))


def set_outcome(record, name, value, evidence, targets=()):
    outcomes = record["outcomes"]
    outcomes[:] = [item for item in outcomes if item["name"] != name]
    outcomes.append(field(name, value, evidence, targets))


def add_note_once(record, text, evidence):
    record["notes"] = [
        item for item in record["notes"]
        if item.get("value") != text
    ]
    record["notes"].append(fact(text, evidence))


def add_page13_image_where_text_is_cited(value):
    """Pair visually checked page-13 image evidence with existing page-13 text facts."""
    if isinstance(value, dict):
        evidence_ids = value.get("evidence_ids")
        if isinstance(evidence_ids, list) and ev(13, "text") in evidence_ids:
            value["evidence_ids"] = list(dict.fromkeys(evidence_ids + [ev(13, "image")]))
        for child in value.values():
            add_page13_image_where_text_is_cited(child)
    elif isinstance(value, list):
        for child in value:
            add_page13_image_where_text_is_cited(child)


dataset = json.loads((CURRENT / "dataset.json").read_text())
existing = {item["record_id"]: item for item in dataset["experiments"]}
records = []


# The page begins by closing the 20PF6 -> 20BPh4 paragraph from page 12.
rid20 = f"{DOC}:salt_exchange_20pf6_to_20bph4"
rec20 = copy.deepcopy(existing[rid20])
add_evidence(rec20, P13)
add_page13_image_where_text_is_cited(rec20)
rec20["notes"] = [
    item for item in rec20["notes"]
    if item.get("value") != "Page 13 text was used only to close the experimental paragraph that begins on covered page 12; page 13 is not claimed as visually covered."
]
add_note_once(
    rec20,
    "Page 13 was visually inspected and closes the page-12 counterion-exchange paragraph; the 137 mg/47% result is explicitly an overall yield for the two-stage sequence.",
    P13,
)
rec20["status"] = "needs_review"
rec20["completeness"] = "partial"
records.append(rec20)


# Replace the page-8-only 21PF6 record with the full page-13 preparation.
rid21 = f"{DOC}:scheme_dppex_tlpf6_to_21pf6"
rec21 = copy.deepcopy(existing[rid21])
add_evidence(rec21, P13)

participant_by_id = {item["entity_id"]: item for item in rec21["participants"]}
participant_by_id["scheme_dppex_tlpf6_to_21pf6_complex16"]["amounts"] = [
    quantity("mass", 190, "mg"),
    quantity("amount", 0.268, "mmol"),
]
participant_by_id["scheme_dppex_tlpf6_to_21pf6_allene"]["amounts"] = [
    quantity("mass", 56, "mg"),
    quantity("amount", 0.29, "mmol"),
]
participant_by_id["scheme_dppex_tlpf6_to_21pf6_tlpf6"]["amounts"] = [
    quantity("mass", 96, "mg"),
    quantity("amount", 0.28, "mmol"),
]
participant_by_id["scheme_dppex_tlpf6_to_21pf6_dcm"]["amounts"] = [
    quantity("initial_volume", 8, "mL"),
]

acetone_id = "scheme_dppex_tlpf6_to_21pf6_acetone"
if acetone_id not in participant_by_id:
    acetone = {
        "entity_id": acetone_id,
        "role": "solvent",
        "label": fact("acetone", P13),
        "name": fact("acetone", P13),
        "smiles": fact("CC(=O)C", P13),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": [quantity("volume", 2, "mL")],
    }
    rec21["participants"].append(acetone)
    rec21["steps"][0]["participant_ids"].append(acetone_id)

set_condition(rec21, "solvent", "dichloromethane (8 mL), with TlPF6 added in acetone (2 mL)", P13)
set_condition(rec21, "temperature", None, ())
set_condition(rec21, "reaction_time", {"number": 2, "unit": "h"}, P13)
set_condition(rec21, "atmosphere", "argon", P9)
set_condition(
    rec21,
    "workup",
    "concentrated to dryness; CH2Cl2 (6 mL) added; filtered through a pad of Celite; Celite washed with CH2Cl2 (6 mL); combined filtrates concentrated to dryness",
    P13,
)
set_condition(rec21, "purification", "silica-gel column chromatography with CH2Cl2 eluent", P13)

product_id = "scheme_dppex_tlpf6_to_21pf6_product"
set_outcome(rec21, "isolated_yield", {"number": 64, "unit": "%"}, P13, (product_id,))
set_outcome(rec21, "yield_measurement_basis", "isolated after silica-gel column chromatography", P13)
set_outcome(rec21, "isolated_product_mass", {"number": 157, "unit": "mg"}, P13, (product_id,))
set_outcome(rec21, "product_appearance", "yellow solid", P13, (product_id,))
rec21["outcomes"] = [item for item in rec21["outcomes"] if item["name"] != "product_yield"]
rec21["notes"] = [
    item for item in rec21["notes"]
    if item.get("value") != "The reaction arrow and product identity are visible on covered page 8; the detailed Experimental paragraph is outside the viewed page range and was not imported in this batch."
]
add_note_once(
    rec21,
    "The page-13 detailed preparation completes the Scheme-5 21PF6 reaction already represented from page 8; it is not a second experiment.",
    P13,
)
rec21["review"]["unresolved"] = [
    "Reaction temperature is not stated in the detailed procedure.",
    "The organopalladium product has no source-verified SMILES; no associated SI was supplied.",
]
rec21["status"] = "needs_review"
rec21["completeness"] = "partial"
records.append(rec21)


# Page-13 crystallization/diffraction methods support six existing products.
crystal_records = {
    "scheme2_1_2_to_3": "3",
    "scheme2_1_4_to_5": "trans-5",
    "scheme3_1_8_to_9": "trans-9",
    "scheme3_1_10_to_11": "cis-11",
    "scheme3_1_12_to_13": "cis-13",
    "scheme3_1_14_to_15": "cis-15",
}
for suffix, product_label in crystal_records.items():
    rec = copy.deepcopy(existing[f"{DOC}:{suffix}"])
    add_evidence(rec, P13)
    add_note_once(
        rec,
        f"Page 13 reports crystal growth plus X-ray diffraction collection/refinement for {product_label}; this is characterization evidence, not an additional reaction execution.",
        P13,
    )
    # Remove exact duplicates introduced by prior cross-page replacements.
    deduped_notes = []
    seen_notes = set()
    for item in rec["notes"]:
        key = json.dumps(item, sort_keys=True)
        if key not in seen_notes:
            deduped_notes.append(item)
            seen_notes.add(key)
    rec["notes"] = deduped_notes
    deduped_outcomes = []
    seen_outcomes = set()
    for item in rec["outcomes"]:
        key = json.dumps(item, sort_keys=True)
        if key not in seen_outcomes:
            deduped_outcomes.append(item)
            seen_outcomes.add(key)
    rec["outcomes"] = deduped_outcomes
    rec["status"] = "needs_review"
    rec["completeness"] = "partial"
    records.append(rec)


# Enrich, but do not split, the existing computational mechanism record.
rid_mech = f"{DOC}:scheme6_figure7_computational_pathways"
rec_mech = copy.deepcopy(existing[rid_mech])
add_evidence(rec_mech, P13)
for name, value in (
    ("computational_method", "B3LYP density-functional geometry optimization and frequency calculations"),
    ("basis_sets", "LanL2DZ ECP/basis for Pd, P, S, and I; 6-31G for C, O, and H; source-specified polarization functions added"),
    ("stationary_point_check", "minima identified by zero imaginary frequency"),
    ("transition_state_check", "intrinsic reaction coordinate calculations used to confirm transition-state connections between minima"),
    ("software", "Gaussian 03; NBO 3.1 used for natural populations"),
):
    set_condition(rec_mech, name, value, P13)
add_note_once(
    rec_mech,
    "Page 13 supplies computational methodology for the Scheme-6/Figure-7 model; it does not report a separate wet-chemistry experiment.",
    P13,
)
rec_mech["status"] = "needs_review"
rec_mech["completeness"] = "partial"
records.append(rec_mech)


raw_path = CURRENT / "raw_model" / "records_pages_0013_0013.json"
raw_path.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")

coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 13,
            "state": "attempted",
            "regions": [
                {
                    "region": "upper-left continuation above the 21PF6 heading",
                    "finding": "Closes the page-12 20PF6-to-20BPh4 sequence: filtration/washing, silica-gel chromatography with CH2Cl2, 137 mg product, and 47% overall yield. Merged into the existing counterion-exchange record.",
                    "evidence_ids": [ev(13, "image"), ev(13, "text")],
                },
                {
                    "region": "left column 21PF6 experimental paragraph",
                    "finding": "Full present-paper preparation of 21PF6 with exact reactant/reagent/solvent quantities, 2 h duration, Celite workup, CH2Cl2 chromatography, 157 mg product, and 64% isolated yield. Merged into the existing Scheme-5 record rather than duplicated.",
                    "evidence_ids": [ev(13, "image"), ev(13, "text")],
                },
                {
                    "region": "lower-left Crystal Structure Analyses paragraph continuing at upper-right",
                    "finding": "Crystal-growth, diffraction-collection, and refinement methods for 3, trans-5, trans-9, cis-11, cis-13, and cis-15; classified as characterization evidence for existing reaction records, not new reactions.",
                    "evidence_ids": [ev(13, "image"), ev(13, "text")],
                },
                {
                    "region": "right-column Computational Details paragraph",
                    "finding": "B3LYP/LanL2DZ/6-31G, frequency, IRC, Gaussian 03, and NBO methods for the existing Scheme-6/Figure-7 computational mechanism; no new wet experiment.",
                    "evidence_ids": [ev(13, "image"), ev(13, "text")],
                },
                {
                    "region": "lower-right acknowledgments, Supporting Information Available statement, and references 48-53",
                    "finding": "No additional reaction experiment. The paper states online supporting material exists, but no SI was supplied or explicitly associated in this workspace, so no SI facts were imported.",
                    "evidence_ids": [ev(13, "image"), ev(13, "text")],
                },
            ],
            "record_ids": [item["record_id"] for item in records],
            "unresolved": [
                "The 21PF6 reaction temperature is not stated.",
                "The 20BPh4 value is explicitly an overall two-stage yield; the counterion-exchange stage alone has no yield, and its temperature is unstated.",
                "Organopalladium connectivities, coordination/stereochemical assignments, and model transition-state structures remain machine-unverified.",
                "Supporting information and CIF files are mentioned but were not supplied or explicitly associated.",
            ],
        }
    ],
}
coverage_path = CURRENT / "coverage" / "pages_0013_0013.json"
coverage_path.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

tasks_path = CURRENT / "tasks.json"
tasks = json.loads(tasks_path.read_text())
for task in tasks:
    if task.get("document_id") == DOC and task.get("evidence_id") == ev(13, "text"):
        task["state"] = "attempted"
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({
    "updated_records": len(records),
    "new_record_ids": 0,
    "raw": str(raw_path),
    "coverage": str(coverage_path),
}, ensure_ascii=False))
