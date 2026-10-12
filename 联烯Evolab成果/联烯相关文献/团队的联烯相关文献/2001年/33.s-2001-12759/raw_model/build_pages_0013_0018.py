#!/usr/bin/env python3
"""Enrich existing reaction records from visually inspected PDF pages 13-18."""
from __future__ import annotations

import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / "runs/current"
DOC = "doc_0f68a8cc21860341"
OUT = RUN / "raw_model/records_pages_0013_0018.json"
COVERAGE = RUN / "coverage/pages_0013_0018.json"


def ev(page: int, kind: str = "image") -> str:
    return f"{DOC}:page{page}:{kind}"


def evidence(page: int) -> list[str]:
    return [ev(page, "text"), ev(page)]


def q(number, unit):
    return {"number": number, "unit": unit}


def fact(value, pages=()):
    pages = [pages] if isinstance(pages, int) else list(pages)
    return {
        "value": value,
        "evidence_ids": [] if value is None else [ev(page) for page in pages],
        "verification": "missing" if value is None else "unreviewed",
    }


def field(name, value, pages=()):
    return {"name": name, "fact": fact(value, pages)}


def participant(entity_id, role, label, page, amounts=()):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, page),
        "name": fact(None),
        "smiles": fact(None),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": [field(name, value, page) for name, value in amounts],
    }


dataset = json.loads((RUN / "dataset.json").read_text())
existing = {record["source_reaction_id"]: record for record in dataset["experiments"]}
records = []


def get_update(rid: str, pages):
    record = copy.deepcopy(existing[rid])
    pages = [pages] if isinstance(pages, int) else list(pages)
    for page in pages:
        for evidence_id in evidence(page):
            if evidence_id not in record["evidence_ids"]:
                record["evidence_ids"].append(evidence_id)
    record["status"] = "needs_review"
    record["completeness"] = "partial"
    record["review"]["method"] = "model"
    record["review"]["reviewer"] = None
    record["review"]["checked_fields"] = []
    record["review"]["unresolved"] = [
        item.replace("pages 1-6", "the inspected source presentation")
        .replace("pages 1-12", "the inspected source presentation")
        .replace("pages 7-12", "the inspected source presentation")
        for item in record["review"]["unresolved"]
    ]
    return record


def upsert(items, name, value, pages):
    replacement = field(name, value, pages)
    for index, item in enumerate(items):
        if item["name"] == name:
            items[index] = replacement
            return
    items.append(replacement)


def entity(record, entity_id):
    return next(item for item in record["participants"] if item["entity_id"] == entity_id)


def add_amount(record, entity_id, name, value, pages):
    upsert(entity(record, entity_id)["amounts"], name, value, pages)


def add_condition(record, name, value, pages, step_id="reaction"):
    step = next(item for item in record["steps"] if item["step_id"] == step_id)
    upsert(step["conditions"], name, value, pages)


def add_outcome(record, name, value, pages):
    upsert(record["outcomes"], name, value, pages)


def add_note(record, text, pages):
    if not any(item["value"] == text for item in record["notes"]):
        record["notes"].append(fact(text, pages))


def add_unresolved(record, text):
    if text not in record["review"]["unresolved"]:
        record["review"]["unresolved"].append(text)


def add_participant(record, entity_id, role, label, page, amounts=()):
    if any(item["entity_id"] == entity_id for item in record["participants"]):
        return
    record["participants"].append(participant(entity_id, role, label, page, amounts))
    record["steps"][0]["participant_ids"].append(entity_id)


def enrich(rid, pages, *, charges=(), outcomes=(), conditions=(), notes=(), unresolved=(), basis=None, fact_pages=None):
    record = get_update(rid, pages)
    fact_pages = pages if fact_pages is None else fact_pages
    for entity_id, name, value in charges:
        add_amount(record, entity_id, name, value, fact_pages)
    for name, value in outcomes:
        add_outcome(record, name, value, fact_pages)
    for name, value in conditions:
        add_condition(record, name, value, fact_pages)
    if basis is not None:
        add_condition(record, "yield_measurement_basis", basis, fact_pages)
    for note in notes:
        add_note(record, note, fact_pages)
    for item in unresolved:
        add_unresolved(record, item)
    records.append(record)
    return record


# Page 13: finish 7d, complete 7e, and detailed dienamide preparations.
enrich(
    "scheme5_entry4", 13,
    outcomes=(("isolated_mass_7d", q(77, "mg")),),
    conditions=(("purification", "Silica-gel chromatography; petroleum ether-ethyl acetate 60:1.",),),
    basis="isolated",
)

record = enrich(
    "scheme5_entry5", 13,
    charges=(
        ("reactant_1", "mass", q(256, "mg")), ("reactant_1", "amount", q(1.01, "mmol")),
        ("reactant_2", "volume", q(0.2, "mL")), ("reactant_2", "amount", q(1.8, "mmol")),
        ("reagent_1", "mass", q(41, "mg")), ("reagent_1", "amount", q(0.05, "mmol")),
        ("reagent_2", "mass", q(19, "mg")), ("reagent_2", "amount", q(0.1, "mmol")),
        ("reagent_3", "volume", q(0.2, "mL")), ("reagent_3", "amount", q(1.5, "mmol")),
        ("product_1", "isolated_mass", q(188, "mg")),
    ),
    conditions=(
        ("temperature", "r.t."), ("atmosphere", "Ar"),
        ("workup", "Remove solvent by evaporation."),
        ("purification", "Silica-gel chromatography; petroleum ether-ethyl acetate 50:1."),
    ),
    basis="isolated",
)
add_participant(record, "experimental_solvent", "solvent", "MeCN", 13, (("total_volume", q(1.0, "mL")),))


table5_details = {
    1: (13, (("reactant_1", "mass", q(50, "mg")), ("reactant_1", "amount", q(0.45, "mmol")), ("reagent_1", "mass", q(101, "mg")), ("reagent_1", "amount", q(0.67, "mmol")), ("solvent_1", "volume", q(1, "mL"))), (("isolated_mass_9aa", q(94, "mg")),)),
    2: (13, (("reactant_1", "mass", q(30, "mg")), ("reactant_1", "amount", q(0.27, "mmol")), ("reagent_1", "mass", q(43, "mg")), ("reagent_1", "amount", q(0.41, "mmol")), ("solvent_1", "volume", q(1, "mL"))), (("isolated_mass_9ab", q(50, "mg")),)),
    3: (13, (("reactant_1", "mass", q(30, "mg")), ("reactant_1", "amount", q(0.27, "mmol")), ("reagent_1", "mass", q(25, "mg")), ("reagent_1", "amount", q(0.41, "mmol")), ("solvent_1", "volume", q(1, "mL"))), (("isolated_mass_9ac", q(30, "mg")),)),
    4: (13, (("reactant_1", "mass", q(27, "mg")), ("reactant_1", "amount", q(0.14, "mmol")), ("reagent_1", "mass", q(35, "mg")), ("reagent_1", "amount", q(0.23, "mmol")), ("solvent_1", "volume", q(1, "mL"))), (("isolated_mass_E_9ba", q(16, "mg")), ("isolated_mass_Z_9ba", q(28, "mg")))),
    7: (13, (("reactant_1", "mass", q(32, "mg")), ("reactant_1", "amount", q(0.16, "mmol")), ("reagent_1", "mass", q(36, "mg")), ("reagent_1", "amount", q(0.24, "mmol")), ("solvent_1", "volume", q(1, "mL"))), (("isolated_mass_E_9ba", q(34, "mg")), ("isolated_mass_Z_9ba", q(18, "mg")))),
    5: ([13, 14], (("reactant_1", "mass", q(56, "mg")), ("reactant_1", "amount", q(0.29, "mmol")), ("reagent_1", "mass", q(45, "mg")), ("reagent_1", "amount", q(0.43, "mmol")), ("solvent_1", "volume", q(1, "mL"))), (("isolated_mass_E_9bb", q(27, "mg")), ("isolated_mass_Z_9bb", q(44, "mg")))),
    8: (14, (("reactant_1", "mass", q(37, "mg")), ("reactant_1", "amount", q(0.19, "mmol")), ("reagent_1", "mass", q(30, "mg")), ("reagent_1", "amount", q(0.29, "mmol")), ("solvent_1", "volume", q(1, "mL"))), (("isolated_mass_E_9bb", q(25, "mg")), ("isolated_mass_Z_9bb", q(11, "mg")))),
    6: (14, (("reactant_1", "mass", q(66, "mg")), ("reactant_1", "amount", q(0.34, "mmol")), ("reagent_1", "mass", q(31, "mg")), ("reagent_1", "amount", q(0.51, "mmol")), ("solvent_1", "volume", q(1, "mL"))), (("isolated_mass_E_9bc", q(44, "mg")), ("isolated_mass_Z_9bc", q(18, "mg")))),
    9: (14, (("reactant_1", "mass", q(66, "mg")), ("reactant_1", "amount", q(0.34, "mmol")), ("reagent_1", "mass", q(31, "mg")), ("reagent_1", "amount", q(0.51, "mmol")), ("solvent_1", "volume", q(1, "mL"))), (("isolated_mass_E_9bc", q(12, "mg")), ("isolated_mass_Z_9bc", q(6, "mg")))),
    10: (14, (("reactant_1", "mass", q(50, "mg")), ("reactant_1", "amount", q(0.36, "mmol")), ("reagent_1", "mass", q(81, "mg")), ("reagent_1", "amount", q(0.54, "mmol")), ("solvent_1", "volume", q(1, "mL"))), (("isolated_mass_9ca", q(93, "mg")),)),
    11: (14, (("reactant_1", "mass", q(80, "mg")), ("reactant_1", "amount", q(0.58, "mmol")), ("reagent_1", "mass", q(91, "mg")), ("reagent_1", "amount", q(0.87, "mmol")), ("solvent_1", "volume", q(1, "mL"))), (("isolated_mass_9cb", q(118, "mg")),)),
    12: (14, (("reactant_1", "mass", q(112, "mg")), ("reactant_1", "amount", q(0.81, "mmol")), ("reagent_1", "mass", q(74, "mg")), ("reagent_1", "amount", q(1.2, "mmol")), ("solvent_1", "volume", q(1, "mL"))), (("isolated_mass_9cc", q(128, "mg")),)),
    13: (14, (("reactant_1", "mass", q(95, "mg")), ("reactant_1", "amount", q(0.51, "mmol")), ("reagent_1", "mass", q(114, "mg")), ("reagent_1", "amount", q(0.76, "mmol")), ("solvent_1", "volume", q(1, "mL"))), (("isolated_mass_9da", q(155, "mg")),)),
    16: (14, (("reactant_1", "mass", q(31, "mg")), ("reactant_1", "amount", q(0.17, "mmol")), ("reagent_1", "solution_concentration", "45%"), ("reagent_1", "volume", q(0.5, "mL"))), (("isolated_mass_9da", q(40, "mg")),)),
    14: (14, (("reactant_1", "mass", q(100, "mg")), ("reactant_1", "amount", q(0.53, "mmol")), ("reagent_1", "mass", q(84, "mg")), ("reagent_1", "amount", q(0.8, "mmol")), ("solvent_1", "volume", q(1, "mL"))), (("isolated_mass_9db", q(142, "mg")), ("experimental_section_yield", q(91, "%")))),
    17: (14, (("reactant_1", "mass", q(31, "mg")), ("reactant_1", "amount", q(0.17, "mmol")), ("reagent_1", "solution_concentration", "40%"), ("reagent_1", "volume", q(0.5, "mL"))), (("isolated_mass_9db", q(38, "mg")),)),
    15: (14, (("reactant_1", "mass", q(100, "mg")), ("reactant_1", "amount", q(0.53, "mmol")), ("reagent_1", "mass", q(49, "mg")), ("reagent_1", "amount", q(0.81, "mmol")), ("solvent_1", "volume", q(1, "mL"))), (("isolated_mass_9dc", q(104, "mg")),)),
    18: (14, (("reactant_1", "mass", q(33, "mg")), ("reactant_1", "amount", q(0.18, "mmol")), ("reagent_1", "solution_concentration", "37%"), ("reagent_1", "volume", q(0.5, "mL"))), (("isolated_mass_9dc", q(37, "mg")),)),
}
for index, (pages, charges, outcomes) in table5_details.items():
    kwargs = {}
    if index == 5:
        kwargs["fact_pages"] = 13
    if index == 14:
        kwargs = {
            "notes": ("Table 5 reports 99%, while the page-14 experimental paragraph reports 142 mg (91%); both are retained.",),
            "unresolved": ("Table 5 and the experimental paragraph conflict on the 9db yield (99% versus 91%).",),
        }
    enrich(f"table5_entry{index}", pages, charges=charges, outcomes=outcomes, basis="isolated", **kwargs)


# Page 15: detailed coupling procedures for 7f and 7g.
record = enrich(
    "scheme6_entry1", 15,
    charges=(
        ("reactant_1", "mass", q(143, "mg")), ("reactant_1", "amount", q(0.54, "mmol")),
        ("reagent_1", "mass", q(31, "mg")), ("reagent_1", "amount", q(0.027, "mmol")),
        ("solvent_1", "coupling_stage_volume", q(1, "mL")), ("product_1", "isolated_mass", q(101, "mg")),
    ),
    conditions=(
        ("organozinc_preparation", "Add n-BuLi to PhI in THF (1 mL) at -78 °C, warm to -40 °C, then add dried ZnBr2 in THF (2 mL)."),
        ("workup", "Remove solvent by evaporation."), ("purification", "Chromatography on silica gel; eluent not stated."),
    ),
    basis="isolated",
)
add_participant(record, "precursor_phenyl_iodide", "reagent", "PhI", 15, (("mass", q(219, "mg")), ("amount", q(1.07, "mmol"))))
add_participant(record, "precursor_n_butyllithium", "reagent", "n-BuLi", 15, (("molarity", q(2.0, "M")), ("volume", q(0.54, "mL"))))
add_participant(record, "precursor_zinc_bromide", "reagent", "dried ZnBr2", 15, (("mass", q(602, "mg")), ("amount", q(2.68, "mmol"))))

record = enrich(
    "scheme6_entry2", 15,
    charges=(
        ("reactant_1", "mass", q(94, "mg")), ("reactant_1", "amount", q(0.35, "mmol")),
        ("reactant_2", "mass", q(47, "mg")), ("reactant_2", "amount", q(0.46, "mmol")),
        ("reagent_1", "mass", q(14, "mg")), ("reagent_1", "amount", q(0.018, "mmol")),
        ("reagent_2", "mass", q(7, "mg")), ("reagent_2", "amount", q(0.035, "mmol")),
        ("reagent_3", "mass", q(53, "mg")), ("reagent_3", "amount", q(0.53, "mmol")),
        ("product_1", "isolated_mass", q(70, "mg")),
    ),
    conditions=(("atmosphere", "Ar"),),
    basis="isolated",
)
add_participant(record, "experimental_solvent", "solvent", "MeCN", 15, (("total_volume", q(2, "mL")),))


# Pages 15-16: detailed nitrile hydrohalogenations matching Table 6 rows.
table6_details = {
    1: (15, (("reactant_1", "mass", q(131, "mg")), ("reactant_1", "amount", q(2.0, "mmol")), ("reagent_1", "mass", q(231, "mg")), ("reagent_1", "amount", q(2.2, "mmol")), ("solvent_1", "volume", q(1, "mL"))), (("experimental_section_yield", q(87, "%")),), "1H NMR"),
    2: (15, (("reactant_1", "mass", q(130, "mg")), ("reactant_1", "amount", q(2.0, "mmol")), ("reagent_1", "mass", q(133, "mg")), ("reagent_1", "amount", q(2.2, "mmol")), ("solvent_1", "volume", q(1, "mL"))), (), "1H NMR"),
    3: (15, (("reactant_1", "mass", q(93, "mg")), ("reactant_1", "amount", q(1.0, "mmol")), ("reagent_1", "mass", q(225, "mg")), ("reagent_1", "amount", q(1.5, "mmol")), ("solvent_1", "CF3CO2H_volume", q(0.5, "mL")), ("solvent_1", "HOAc_volume", q(0.5, "mL"))), (("isolated_mass_11ba", q(176, "mg")),), "isolated"),
    6: (15, (("reactant_1", "mass", q(96, "mg")), ("reactant_1", "amount", q(1.0, "mmol")), ("reagent_1", "mass", q(165, "mg")), ("reagent_1", "amount", q(1.1, "mmol")), ("solvent_1", "volume", q(1.0, "mL"))), (("isolated_mass_11ba", q(84, "mg")),), "isolated"),
    4: (15, (("reactant_1", "mass", q(93, "mg")), ("reactant_1", "amount", q(1.0, "mmol")), ("reagent_1", "mass", q(210, "mg")), ("reagent_1", "amount", q(2, "mmol")), ("solvent_1", "CF3CO2H_volume", q(0.5, "mL")), ("solvent_1", "HOAc_volume", q(0.5, "mL"))), (("isolated_mass_11bb", q(135, "mg")),), "isolated"),
    7: (15, (("reactant_1", "mass", q(93, "mg")), ("reactant_1", "amount", q(1.0, "mmol")), ("reagent_1", "mass", q(525, "mg")), ("reagent_1", "amount", q(5, "mmol")), ("solvent_1", "volume", q(1.0, "mL"))), (("isolated_mass_11bb", q(30, "mg")),), "isolated"),
    5: (15, (("reactant_1", "mass", q(93, "mg")), ("reactant_1", "amount", q(1.0, "mmol")), ("reagent_1", "mass", q(121, "mg")), ("reagent_1", "amount", q(2, "mmol")), ("solvent_1", "CF3CO2H_volume", q(0.5, "mL")), ("solvent_1", "HOAc_volume", q(0.5, "mL"))), (("isolated_mass_11bc", q(98, "mg")),), "isolated"),
    8: (15, (("reactant_1", "mass", q(44, "mg")), ("reactant_1", "amount", q(0.47, "mmol")), ("reagent_1", "mass", q(43, "mg")), ("reagent_1", "amount", q(0.71, "mmol")), ("solvent_1", "volume", q(1.0, "mL"))), (("isolated_mass_11bc", q(11, "mg")),), "isolated"),
    9: (15, (("reactant_1", "mass", q(120, "mg")), ("reactant_1", "amount", q(0.99, "mmol")), ("reagent_1", "mass", q(225, "mg")), ("reagent_1", "amount", q(1.5, "mmol")), ("solvent_1", "CF3CO2H_volume", q(0.5, "mL")), ("solvent_1", "HOAc_volume", q(0.5, "mL"))), (("isolated_mass_E_11ca", q(155, "mg")), ("isolated_mass_Z_11ca", q(40, "mg"))), "isolated"),
    12: (15, (("reactant_1", "mass", q(89, "mg")), ("reactant_1", "amount", q(0.74, "mmol")), ("reagent_1", "mass", q(165, "mg")), ("reagent_1", "amount", q(1.1, "mmol")), ("solvent_1", "volume", q(1.0, "mL"))), (("isolated_mass_11ca", q(129, "mg")),), "isolated"),
    13: (16, (("reactant_1", "mass", q(80, "mg")), ("reactant_1", "amount", q(0.66, "mmol")), ("reagent_1", "mass", q(149, "mg")), ("reagent_1", "amount", q(0.99, "mmol")), ("solvent_1", "volume", q(1.0, "mL"))), (("isolated_mass_11ca", q(95, "mg")), ("experimental_section_Z/E_ratio", "1:3.1")), "isolated"),
    10: (16, (("reactant_1", "mass", q(121, "mg")), ("reactant_1", "amount", q(1.0, "mmol")), ("reagent_1", "mass", q(158, "mg")), ("reagent_1", "amount", q(1.5, "mmol")), ("solvent_1", "CF3CO2H_volume", q(0.5, "mL")), ("solvent_1", "HOAc_volume", q(0.5, "mL"))), (("isolated_mass_E_11cb", q(118, "mg")), ("isolated_mass_Z_11cb", q(44, "mg"))), "isolated"),
    11: (16, (("reactant_1", "mass", q(121, "mg")), ("reactant_1", "amount", q(1.0, "mmol")), ("reagent_1", "mass", q(91, "mg")), ("reagent_1", "amount", q(1.5, "mmol")), ("solvent_1", "CF3CO2H_volume", q(0.5, "mL")), ("solvent_1", "HOAc_volume", q(0.5, "mL"))), (("isolated_mass_E_11cc", q(78, "mg")), ("isolated_mass_Z_11cc", q(35, "mg"))), "isolated"),
    14: (16, (("reactant_1", "mass", q(38, "mg")), ("reactant_1", "amount", q(0.27, "mmol")), ("reagent_1", "mass", q(62, "mg")), ("reagent_1", "amount", q(0.41, "mmol")), ("solvent_1", "CF3CO2H_volume", q(0.5, "mL")), ("solvent_1", "HOAc_volume", q(0.5, "mL"))), (("isolated_mass_E_11da", q(32, "mg")), ("experimental_section_printed_yield", "4%")), "isolated"),
    15: (16, (("reactant_1", "mass", q(56, "mg")), ("reactant_1", "amount", q(0.40, "mmol")), ("reagent_1", "mass", q(62, "mg")), ("reagent_1", "amount", q(0.59, "mmol")), ("solvent_1", "CF3CO2H_volume", q(0.7, "mL")), ("solvent_1", "HOAc_volume", q(0.7, "mL"))), (("isolated_mass_E_11db", q(71, "mg")),), "isolated"),
    16: (16, (("reactant_1", "mass", q(64, "mg")), ("reactant_1", "amount", q(0.45, "mmol")), ("reagent_1", "mass", q(42, "mg")), ("reagent_1", "amount", q(0.69, "mmol")), ("solvent_1", "CF3CO2H_volume", q(0.5, "mL")), ("solvent_1", "HOAc_volume", q(0.5, "mL"))), (("isolated_mass_E_11dc", q(30, "mg")),), "isolated"),
}
for index, (page, charges, outcomes, basis) in table6_details.items():
    kwargs = {}
    if index == 1:
        kwargs = {
            "notes": ("Table 6 reports 86%, while the page-15 experimental paragraph reports 87% (NMR yield); both are retained.",),
            "unresolved": ("Table 6 and the experimental paragraph differ on the 11ab NMR yield (86% versus 87%).",),
        }
    elif index == 14:
        kwargs = {
            "notes": ("Table 6 reports 44%, while the page-16 experimental paragraph visibly prints 32 mg (4%); both are retained.",),
            "unresolved": ("Table 6 and the experimental paragraph conflict on the (E)-11da yield (44% versus 4%).",),
        }
    enrich(f"table6_entry{index}", page, charges=charges, outcomes=outcomes, basis=basis, **kwargs)


# Page 16: detailed coupling procedures for 7h and 7i.
record = enrich(
    "scheme7_entry1", 16,
    charges=(
        ("reactant_1", "mass", q(112, "mg")), ("reactant_1", "amount", q(0.51, "mmol")),
        ("reagent_1", "mass", q(30, "mg")), ("reagent_1", "amount", q(0.025, "mmol")),
        ("solvent_1", "coupling_stage_volume", q(1, "mL")), ("product_1", "isolated_mass", q(64, "mg")),
    ),
    conditions=(
        ("organozinc_preparation", "Add n-BuLi to PhI in THF (1 mL) at -78 °C, warm to -40 °C, then add dried ZnBr2 in THF (2 mL)."),
        ("workup", "Remove solvent by evaporation."), ("purification", "Chromatography on silica gel; eluent not stated."),
    ),
    basis="isolated",
)
add_participant(record, "precursor_phenyl_iodide", "reagent", "PhI", 16, (("mass", q(211, "mg")), ("amount", q(1.03, "mmol"))))
add_participant(record, "precursor_n_butyllithium", "reagent", "n-BuLi", 16, (("molarity", q(2.0, "M")), ("volume", q(0.52, "mL"))))
add_participant(record, "precursor_zinc_bromide", "reagent", "dried ZnBr2", 16, (("mass", q(582, "mg")), ("amount", q(2.59, "mmol"))))

record = enrich(
    "scheme7_entry2", 16,
    charges=(
        ("reactant_1", "mass", q(98, "mg")), ("reactant_1", "amount", q(0.44, "mmol")),
        ("reactant_2", "mass", q(59, "mg")), ("reactant_2", "amount", q(0.58, "mmol")),
        ("reagent_1", "mass", q(18, "mg")), ("reagent_1", "amount", q(0.022, "mmol")),
        ("reagent_2", "mass", q(8, "mg")), ("reagent_2", "amount", q(0.044, "mmol")),
        ("reagent_3", "mass", q(122, "mg")), ("reagent_3", "amount", q(0.89, "mmol")),
        ("product_1", "isolated_mass", q(79, "mg")),
    ),
    conditions=(("workup", "Remove solvent by evaporation."), ("purification", "Chromatography on silica gel; eluent not stated.")),
    basis="isolated",
)
add_participant(record, "experimental_solvent", "solvent", "MeCN", 16, (("total_volume", q(2, "mL")),))


# Page 17: detailed Table 7 preparations, retaining printed conflicts.
table7_details = {
    2: ((("reactant_1", "mass", q(240, "mg")), ("reactant_1", "amount", q(1.0, "mmol")), ("reagent_1", "mass", q(147, "mg")), ("reagent_1", "amount", q(1.1, "mmol")), ("solvent_1", "volume", q(1.0, "mL"))), (("isolated_mass_13aa", q(276, "mg")),)),
    1: ((("reactant_1", "mass", q(240, "mg")), ("reactant_1", "amount", q(1.0, "mmol")), ("reagent_1", "mass", q(165, "mg")), ("reagent_1", "amount", q(1.1, "mmol")), ("solvent_1", "volume", q(1.0, "mL"))), (("isolated_mass_13aa", q(220, "mg")),)),
    5: ((("reactant_1", "mass", q(120, "mg")), ("reactant_1", "amount", q(0.5, "mmol")), ("reagent_1", "solution_concentration", "45%"), ("reagent_1", "volume", q(1, "mL"))), (("isolated_mass_13aa", q(85, "mg")), ("experimental_section_printed_yield", "4%"))),
    3: ((("reactant_1", "mass", q(240, "mg")), ("reactant_1", "amount", q(1.0, "mmol")), ("reagent_1", "mass", q(114, "mg")), ("reagent_1", "amount", q(1.1, "mmol"))), (("isolated_mass_13ab", q(225, "mg")),)),
    6: ((("reactant_1", "mass", q(120, "mg")), ("reactant_1", "amount", q(0.5, "mmol")), ("reagent_1", "solution_concentration", "40%"), ("reagent_1", "volume", q(1.0, "mL"))), (("isolated_mass_13ab", q(60, "mg")),)),
    4: ((("reactant_1", "mass", q(240, "mg")), ("reactant_1", "amount", q(1.0, "mmol")), ("reagent_1", "mass", q(67, "mg")), ("reagent_1", "amount", q(1.1, "mmol"))), (("isolated_mass_13ac", q(160, "mg")),)),
    7: ((("reactant_1", "mass", q(120, "mg")), ("reactant_1", "amount", q(0.5, "mmol")), ("reagent_1", "solution_concentration", "36%"), ("reagent_1", "volume", q(1.0, "mL"))), (("isolated_mass_13ac", q(43, "mg")), ("experimental_section_yield", q(37, "%")))),
}
for index, (charges, outcomes) in table7_details.items():
    kwargs = {}
    conditions = ()
    if index == 5:
        conditions = (("purification", "Chromatography; petroleum ether-ethyl acetate 2:1."),)
        kwargs = {
            "notes": ("Table 7 reports 46%, while the page-17 experimental paragraph visibly prints 85 mg (4%); both are retained.",),
            "unresolved": ("Table 7 and the experimental paragraph conflict on the aqueous-HI 13aa yield (46% versus 4%).",),
        }
    elif index == 7:
        kwargs = {
            "notes": ("Table 7 reports 31%, while the page-17 experimental paragraph reports 43 mg (37%); both are retained.",),
            "unresolved": ("Table 7 and the experimental paragraph conflict on the aqueous-HCl 13ac yield (31% versus 37%).",),
        }
    enrich(f"table7_entry{index}", 17, charges=charges, outcomes=outcomes, conditions=conditions, basis="isolated", **kwargs)


# Page 17: detailed couplings of 13aa.
record = enrich(
    "scheme8_entry1", 17,
    charges=(
        ("reactant_1", "mass", q(184, "mg")), ("reactant_1", "amount", q(0.5, "mmol")),
        ("reactant_2", "mass", q(49, "mg")), ("reactant_2", "amount", q(0.6, "mmol")),
        ("reagent_1", "mass", q(3, "mg")), ("reagent_1", "amount", q(0.005, "mmol")),
        ("reagent_2", "mass", q(1.0, "mg")), ("reagent_2", "amount", q(0.005, "mmol")),
        ("reagent_3", "mass", q(101, "mg")), ("reagent_3", "amount", q(1.0, "mmol")),
        ("product_1", "isolated_mass", q(150, "mg")),
    ),
    conditions=(
        ("time", "overnight"), ("monitoring", "TLC"),
        ("workup", "Quench with H2O, extract with CH2Cl2, combine organic layers, dry over MgSO4, and evaporate solvent."),
        ("purification", "Flash chromatography on silica gel; petroleum ether-ethyl acetate 2:1."),
    ),
    basis="isolated",
)
add_participant(record, "experimental_solvent", "solvent", "CH3CN", 17, (("volume", q(2, "mL")),))

record = enrich(
    "scheme8_entry2", 17,
    charges=(
        ("reactant_1", "mass", q(184, "mg")), ("reactant_1", "amount", q(0.5, "mmol")),
        ("reactant_2", "mass", q(63, "mg")), ("reactant_2", "amount", q(0.6, "mmol")),
        ("reagent_1", "mass", q(3, "mg")), ("reagent_1", "amount", q(0.005, "mmol")),
        ("reagent_2", "mass", q(1.0, "mg")), ("reagent_2", "amount", q(0.005, "mmol")),
        ("reagent_3", "mass", q(101, "mg")), ("reagent_3", "amount", q(1.0, "mmol")),
        ("product_1", "isolated_mass", q(162, "mg")),
    ),
    conditions=(("time", "overnight"),),
    basis="isolated",
)
add_participant(record, "experimental_solvent", "solvent", "CH3CN", 17, (("volume", q(2, "mL")),))


assert len(records) == 49, len(records)
assert len({record["record_id"] for record in records}) == len(records)


page_record_ids = {
    13: [
        f"{DOC}:scheme5_entry4", f"{DOC}:scheme5_entry5",
        *[f"{DOC}:table5_entry{i}" for i in (1, 2, 3, 4, 7, 5)],
    ],
    14: [f"{DOC}:table5_entry{i}" for i in (5, 8, 6, 9, 10, 11, 12, 13, 16, 14, 17, 15, 18)],
    15: [
        f"{DOC}:scheme6_entry1", f"{DOC}:scheme6_entry2",
        *[f"{DOC}:table6_entry{i}" for i in (1, 2, 3, 6, 4, 7, 5, 8, 9, 12)],
    ],
    16: [
        *[f"{DOC}:table6_entry{i}" for i in (13, 10, 11, 14, 15, 16)],
        f"{DOC}:scheme7_entry1", f"{DOC}:scheme7_entry2",
    ],
    17: [
        *[f"{DOC}:table7_entry{i}" for i in (2, 1, 5, 3, 6, 4, 7)],
        f"{DOC}:scheme8_entry1", f"{DOC}:scheme8_entry2",
    ],
    18: [],
}


coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 13,
            "state": "attempted",
            "regions": [
                {"region": "upper left, continuation of 7d and complete 7e coupling procedure", "finding": "The 7d continuation and 7e procedure were merged into existing Scheme 5 entries 4 and 5; charges, chromatography, isolated masses, and 7e atmosphere/temperature were retained.", "evidence_ids": evidence(13)},
                {"region": "lower left, 9aa and 9ab preparations", "finding": "Detailed charges and isolated masses enrich Table 5 entries 1 and 2; characterization is not a separate experiment.", "evidence_ids": evidence(13)},
                {"region": "upper and middle right, 9ac and two 9ba conditions", "finding": "Three existing Table 5 rows were enriched separately; the HOAc and CF3CO2H runs were not merged with each other.", "evidence_ids": evidence(13)},
                {"region": "lower right, beginning of 9bb preparation", "finding": "The HOAc 9bb experiment begins here and continues onto page 14; it remains one existing Table 5 entry.", "evidence_ids": evidence(13)},
            ],
            "record_ids": page_record_ids[13],
            "unresolved": ["Structures and SMILES remain unverified.", "The detailed 7d procedure begins on page 12; page 12 is context and is not newly claimed as covered here."],
        },
        {
            "page": 14,
            "state": "attempted",
            "regions": [
                {"region": "upper left, continuation of HOAc 9bb and CF3CO2H 9bb run", "finding": "The cross-page HOAc record was linked without duplication and the distinct CF3CO2H condition was enriched separately.", "evidence_ids": evidence(14)},
                {"region": "left column, 9bc under two solvents plus 9ca and 9cb", "finding": "Four distinct Table 5 rows were enriched with printed charges and isolated E/Z or single-product masses.", "evidence_ids": evidence(14)},
                {"region": "right column, 9cc and paired MX/aqueous-HX preparations of 9da-9dc", "finding": "Eight distinct Table 5 rows were enriched; the printed 9db 91% result was retained alongside Table 5's 99% value as a conflict.", "evidence_ids": evidence(14)},
            ],
            "record_ids": page_record_ids[14],
            "unresolved": ["Table 5 and the experimental paragraph conflict on the 9db yield (99% versus 91%).", "Workup and purification are not reported for these abbreviated preparations.", "Structures and SMILES remain unverified."],
        },
        {
            "page": 15,
            "state": "attempted",
            "regions": [
                {"region": "upper left, Pd-catalyzed preparations of 7f and 7g", "finding": "The two Scheme 6 arrows were enriched with organozinc-generation or Sonogashira charges, reaction stages, isolated masses, and printed workup/purification where available.", "evidence_ids": evidence(15)},
                {"region": "lower left and right, detailed 11ab/11ac and 11ba-11ca hydrohalogenations", "finding": "Ten existing Table 6 rows were enriched separately; 11ab/11ac are explicitly NMR yields, while mass-bearing outcomes were retained as isolated yields.", "evidence_ids": evidence(15)},
            ],
            "record_ids": page_record_ids[15],
            "unresolved": ["Table 6 gives 86% for 11ab while the experimental paragraph gives 87% NMR yield.", "Most abbreviated nitrile preparations omit workup and purification.", "Structures and SMILES remain unverified."],
        },
        {
            "page": 16,
            "state": "attempted",
            "regions": [
                {"region": "left column and upper right, continuation of 11ca plus 11cb/11cc/11da-11dc", "finding": "Six Table 6 records were enriched with charges and isolated masses; the page visibly prints 4% for (E)-11da while Table 6 reports 44%, so both were preserved.", "evidence_ids": evidence(16)},
                {"region": "lower right, Pd-catalyzed preparations of 7h and 7i", "finding": "The two Scheme 7 records were enriched with organozinc-generation or Sonogashira charges, stages, isolated masses, and printed workup/purification.", "evidence_ids": evidence(16)},
            ],
            "record_ids": page_record_ids[16],
            "unresolved": ["Table 6 and the experimental paragraph conflict on the (E)-11da yield (44% versus 4%).", "The 11ca ratio is printed as E/Z = 3.1:1 in Table 6 and equivalently as Z/E = 1:3.1 in the experiment.", "Structures and SMILES remain unverified."],
        },
        {
            "page": 17,
            "state": "attempted",
            "regions": [
                {"region": "left column, seven phosphine-oxide hydrohalogenation preparations", "finding": "All seven existing Table 7 rows were enriched with printed charges and isolated masses; the aqueous-HI and aqueous-HCl yield conflicts were retained rather than corrected.", "evidence_ids": evidence(17)},
                {"region": "upper right, detailed couplings of 13aa to 7j and 7k", "finding": "The two Scheme 8 records were enriched with charges, CH3CN, overnight duration, isolated masses, and the fully printed 7j workup/purification.", "evidence_ids": evidence(17)},
                {"region": "lower right, acknowledgement and beginning of references", "finding": "Non-experimental front matter and cited prior work were not converted into current-paper experiments.", "evidence_ids": evidence(17)},
            ],
            "record_ids": page_record_ids[17],
            "unresolved": ["Table 7 versus experimental-paragraph conflicts remain for aqueous HI (46% versus printed 4%) and aqueous HCl (31% versus 37%).", "The 7k paragraph does not state a workup or chromatography procedure.", "Structures and SMILES remain unverified."],
        },
        {
            "page": 18,
            "state": "attempted",
            "regions": [
                {"region": "entire page, references 3-29", "finding": "The page contains bibliography only. These are cited prior works, not current-paper experiments; no reaction record was created.", "evidence_ids": evidence(18)},
            ],
            "record_ids": page_record_ids[18],
            "unresolved": ["No current-paper experimental reaction is present on this page.", "No SI is supplied or explicitly associated in this pilot."],
        },
    ],
}


OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
COVERAGE.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

tasks_path = RUN / "tasks.json"
tasks = json.loads(tasks_path.read_text())
for task in tasks:
    if task.get("document_id") == DOC and task.get("evidence_id") in {ev(page, "text") for page in range(13, 19)}:
        task["state"] = "attempted"
        task["reason"] = "Original page image and page text inspected; existing records enriched and coverage ledger generated for PDF pages 13-18."
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"submitted_records": len(records), "new_records": 0, "updated_records": len(records), "coverage_pages": list(range(13, 19))}, ensure_ascii=False))
