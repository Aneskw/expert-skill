#!/usr/bin/env python3
"""Build page 7-11 record updates for Kong/Fu/Ma, Eur. J. Org. Chem. 2010."""

from __future__ import annotations

import copy
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
DATASET = ROOT / "runs/current/dataset.json"
OUT = ROOT / "runs/current/raw_model/records_pages_0007_0011.json"
COVERAGE = ROOT / "runs/current/coverage/pages_0007_0011.json"
TASKS = ROOT / "runs/current/tasks.json"
DOC = "doc_be03b7ebc068e9b9"


def ev(*pages: int) -> list[str]:
    return [item for page in pages for item in (f"{DOC}:page{page}:text", f"{DOC}:page{page}:image")]


def fact(value, evidence=()):
    return {
        "value": value,
        "evidence_ids": list(dict.fromkeys(evidence)) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def field(name, value, evidence, targets=()):
    result = {"name": name, "fact": fact(value, evidence)}
    if targets:
        result["target_entity_ids"] = list(targets)
    return result


def participant(entity_id, role, label, evidence, name=None, smiles=None, amounts=()):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence) if name else fact(None),
        "smiles": fact(smiles, evidence) if smiles else fact(None),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": [field(n, v, evidence) for n, v in amounts],
    }


def step(step_id, participant_ids, conditions):
    return {"step_id": step_id, "participant_ids": list(participant_ids), "conditions": list(conditions)}


BASE_UNRESOLVED = [
    "Supporting information was not explicitly supplied or associated; SI-only details were not inferred.",
    "Source structures remain machine-unverified; uncertain structures retain null SMILES.",
]


data = json.loads(DATASET.read_text())
existing = {record["record_id"]: record for record in data["experiments"]}
records = []


def take(suffix: str):
    record = copy.deepcopy(existing[f"{DOC}:{suffix}"])
    record["status"] = "needs_review"
    record["completeness"] = "partial"
    record["review"]["method"] = "model"
    record["review"]["reviewer"] = None
    record["review"]["checked_fields"] = []
    return record


def add_evidence(record, evidence):
    record["evidence_ids"] = list(dict.fromkeys(record["evidence_ids"] + list(evidence)))


def get_participant(record, entity_id):
    return next(item for item in record["participants"] if item["entity_id"] == entity_id)


def get_step(record, step_id):
    return next(item for item in record["steps"] if item["step_id"] == step_id)


def add_amount(record, entity_id, name, value, evidence):
    item = get_participant(record, entity_id)
    item["amounts"] = [entry for entry in item["amounts"] if entry["name"] != name]
    item["amounts"].append(field(name, value, evidence))


def set_name(record, entity_id, value, evidence):
    get_participant(record, entity_id)["name"] = fact(value, evidence)


def set_smiles(record, entity_id, value, evidence):
    get_participant(record, entity_id)["smiles"] = fact(value, evidence)


def set_condition(record, step_id, name, value, evidence):
    item = get_step(record, step_id)
    item["conditions"] = [entry for entry in item["conditions"] if entry["name"] != name]
    item["conditions"].append(field(name, value, evidence))


def replace_outcome(record, old_name, name, value, evidence, targets):
    record["outcomes"] = [entry for entry in record["outcomes"] if entry["name"] not in {old_name, name}]
    record["outcomes"].append(field(name, value, evidence, targets))


def add_outcome(record, name, value, evidence, targets):
    record["outcomes"] = [entry for entry in record["outcomes"] if entry["name"] != name]
    record["outcomes"].append(field(name, value, evidence, targets))


def note(value, evidence):
    return fact(value, evidence)


# Page 7: merge the detailed preparations of 3f-3j into Table 2 entries 6-10.
t2_detail = {
    6: {"sub": "2f", "product": "3f", "sub_qty": (69.1, 0.3), "au": (7.3, 0.015), "ag": (3.2, 0.016), "solv": 1.5, "prod_mass": 40.3, "yield": 74, "purif": "petroleum ether/ethyl acetate 40:1"},
    7: {"sub": "2g", "product": "3g", "sub_qty": (61.2, 0.2), "au": (5.6, 0.011), "ag": (2.5, 0.013), "solv": 1.0, "prod_mass": 41.5, "yield": 84, "purif": "petroleum ether/ethyl acetate 20:1"},
    8: {"sub": "2h", "product": "3h", "sub_qty": (98.5, 0.3), "au": (7.5, 0.015), "ag": (3.5, 0.018), "solv": 1.5, "prod_mass": 67.5, "yield": 84, "purif": "petroleum ether/ethyl acetate 10:1"},
    9: {"sub": "2i", "product": "3i", "sub_qty": (101.5, 0.3), "au": (7.8, 0.015), "ag": (3.5, 0.018), "solv": 1.5, "prod_mass": 67.0, "yield": 80, "purif": "petroleum ether/ethyl acetate 60:1"},
    10: {"sub": "2j", "product": "3j", "sub_qty": (99.1, 0.3), "au": (7.1, 0.014), "ag": (3.1, 0.015), "solv": 2.0, "prod_mass": 49.2, "yield": 61, "purif": "petroleum ether/ethyl acetate 100:1"},
}
for entry, detail in t2_detail.items():
    evidence = ev(7)
    record = take(f"table2_entry{entry}")
    add_evidence(record, evidence)
    prefix = f"t2e{entry}_"
    add_amount(record, prefix + detail["sub"], "mass", {"number": detail["sub_qty"][0], "unit": "mg"}, evidence)
    add_amount(record, prefix + detail["sub"], "amount", {"number": detail["sub_qty"][1], "unit": "mmol"}, evidence)
    for catalyst, values in (("au", detail["au"]), ("ag", detail["ag"])):
        add_amount(record, prefix + catalyst, "mass", {"number": values[0], "unit": "mg"}, evidence)
        add_amount(record, prefix + catalyst, "amount", {"number": values[1], "unit": "mmol"}, evidence)
    add_amount(record, prefix + "diox", "volume", {"number": detail["solv"], "unit": "mL"}, evidence)
    add_amount(record, prefix + detail["product"], "mass", {"number": detail["prod_mass"], "unit": "mg"}, evidence)
    set_condition(record, "gold_cyclization", "operation", "performed according to the representative general procedure and stirred to the stated endpoint", ev(6, 7))
    set_condition(record, "gold_cyclization", "atmosphere", "N2", ev(6, 7))
    set_condition(record, "gold_cyclization", "purification", "silica-gel column chromatography; " + detail["purif"], evidence)
    replace_outcome(record, "reported_yield", "isolated_yield", {"number": detail["yield"], "unit": "%"}, evidence, (prefix + detail["product"],))
    add_outcome(record, "yield_measurement_basis", "isolated after chromatography", evidence, (prefix + detail["product"],))
    record["notes"] = [note("The page-7 detailed batch is the same experiment as its Table 2 row and was merged rather than duplicated.", ev(3, 7))]
    record["review"]["unresolved"] = BASE_UNRESOLVED + ["The abbreviated batch refers to the representative procedure for shared operations rather than restating every operation and volume."]
    records.append(record)


SMILES = {
    "NIS": "O=C1CCC(=O)N1I",
    "diethyl ether": "CCOCC",
    "water": "O",
    "phenylboronic acid": "OB(O)c1ccccc1",
    "4-methoxyphenylboronic acid": "COc1ccc(B(O)O)cc1",
    "(E)-styrylboronic acid": "OB(O)/C=C/c1ccccc1",
    "1-ethynyl-4-methoxybenzene": "COc1ccc(C#C)cc1",
    "TBAB": "[Br-].CCCC[N+](CCCC)(CCCC)CCCC",
}


def workup_participants(prefix, evidence):
    return [
        participant(prefix + "_ether", "solvent", "diethyl ether", evidence, smiles=SMILES["diethyl ether"], amounts=(("dilution_volume", {"number": 10, "unit": "mL"}), ("extraction_volume_each", {"number": 15, "unit": "mL"}))),
        participant(prefix + "_thiosulfate", "reagent", "saturated aqueous Na2S2O3", evidence),
        participant(prefix + "_water", "reagent", "water", evidence, smiles=SMILES["water"]),
        participant(prefix + "_drying", "reagent", "anhydrous Na2SO4", evidence),
    ]


def detailed_iodonaphthalene(suffix, label, name, page, quantities, time_value, isolated_yield, nmr_yield, ratio):
    evidence = ev(page)
    prefix = suffix.replace("_isolated_batch", "")
    sub, au, ag, nis, acetone, product = quantities
    parts = [
        participant(prefix + "_sub", "reactant", label.replace("4", "2"), evidence, amounts=(("mass", {"number": sub[0], "unit": "mg"}), ("amount", {"number": sub[1], "unit": "mmol"}))),
        participant(prefix + "_au", "catalyst", "AuCl(PPh3)", evidence, amounts=(("mass", {"number": au[0], "unit": "mg"}), ("amount", {"number": au[1], "unit": "mmol"}))),
        participant(prefix + "_ag", "catalyst", "AgBF4", evidence, amounts=(("mass", {"number": ag[0], "unit": "mg"}), ("amount", {"number": ag[1], "unit": "mmol"}))),
        participant(prefix + "_nis", "reagent", "NIS", evidence, smiles=SMILES["NIS"], amounts=(("mass", {"number": nis[0], "unit": "mg"}), ("amount", {"number": nis[1], "unit": "mmol"}))),
        participant(prefix + "_acetone", "solvent", "acetone", evidence, smiles="CC(C)=O", amounts=(("volume", {"number": acetone, "unit": "mL"}),)),
        participant(prefix + "_product", "product", label, evidence, name=name, amounts=(("mass", {"number": product, "unit": "mg"}),)),
        participant(prefix + "_byproduct", "product", label.replace("4", "3"), evidence),
        participant(prefix + "_std", "unspecified_agent", "CH2Br2 internal standard", evidence),
    ]
    conditions = [field("temperature", {"number": 0, "unit": "°C"}, evidence), field("reaction_time", time_value, evidence if time_value is not None else ())]
    if suffix.endswith("4a_isolated_batch"):
        conditions += [field("atmosphere", "N2", evidence), field("operation", "stirred until TLC indicated completion", evidence)]
        parts += workup_participants(prefix, evidence)
        conditions += [
            field("workup", "diluted with 10 mL diethyl ether; quenched with saturated aqueous Na2S2O3; extracted with diethyl ether (3 x 15 mL); combined organic layers washed with water and dried over anhydrous Na2SO4; filtered and evaporated", evidence),
            field("purification", "silica-gel column chromatography; petroleum ether/ethyl acetate 40:1", evidence),
        ]
    else:
        conditions.append(field("operation", "performed according to the procedure outlined for 4a", ev(7, page)))
    outcomes = [
        field("isolated_yield_" + label, {"number": isolated_yield, "unit": "%"}, evidence, (prefix + "_product",)),
        field("isolated_yield_measurement_basis", "isolated product", evidence, (prefix + "_product",)),
        field("ratio_" + label + "_to_" + label.replace("4", "3"), ratio, evidence, (prefix + "_product", prefix + "_byproduct")),
    ]
    if nmr_yield is not None:
        outcomes += [
            field("nmr_yield_" + label, {"number": nmr_yield, "unit": "%"}, evidence, (prefix + "_product",)),
            field("nmr_yield_measurement_basis", "1H NMR using CH2Br2 as internal standard", evidence, (prefix + "_product",)),
        ]
    unresolved = list(BASE_UNRESOLVED)
    if time_value is None:
        unresolved.append("The source sentence reads 'at 0 °C for afforded 4i'; the reaction duration is absent and was not borrowed from the distinct Table 4 batch.")
    elif not suffix.endswith("4a_isolated_batch"):
        unresolved.append("The abbreviated paragraph refers to the 4a procedure and does not restate all workup quantities.")
    return {
        "record_id": f"{DOC}:{suffix}", "document_id": DOC, "source_reaction_id": suffix,
        "record_kind": "reported_experiment", "status": "needs_review", "completeness": "partial",
        "evidence_ids": list(dict.fromkeys(ev(4, page) if page != 4 else evidence)),
        "participants": parts,
        "steps": [step("iodocyclization", [p["entity_id"] for p in parts if p["role"] in {"reactant", "catalyst", "solvent", "reagent"}][:5], conditions)],
        "outcomes": outcomes,
        "notes": [note("This isolated-product batch is distinct from the Table 4 tandem batch because its exact charge differs.", evidence)] if label in {"4g", "4i"} else [],
        "review": {"method": "model", "reviewer": None, "checked_fields": [], "unresolved": unresolved},
    }


# Replace the earlier page-4-only 4a record with its detailed page-7 batch.
records.append(detailed_iodonaphthalene(
    "scheme7_4a_isolated_batch", "4a", "6-iodo-1,4-dimethoxy-7-phenylnaphthalene", 7,
    ((96.1, 0.30), (8.0, 0.016), (3.2, 0.016), (100.1, 0.44), 2.0, 86.9),
    {"number": 20, "unit": "h"}, 75, None, "100:0",
))
records.append(detailed_iodonaphthalene(
    "scheme7_4g_isolated_batch", "4g", "(8-iodonaphtho[2,1-d][1,3]dioxol-7-yl)methyl acetate", 7,
    ((90.1, 0.30), (7.4, 0.015), (3.1, 0.015), (105.1, 0.47), 2.0, 65.4),
    {"number": 11, "unit": "h"}, 60, 62, "100:0",
))
records.append(detailed_iodonaphthalene(
    "scheme7_4i_isolated_batch", "4i", "6-butyl-7-iodo-1,2,3-trimethoxynaphthalene", 8,
    ((101.5, 0.30), (7.4, 0.015), (3.5, 0.015), (102.5, 0.45), 2.0, 60.9),
    None, 50, 60, "100:0",
))


# Pages 8-9: detailed tandem iodocyclization/Sonogashira batches for Table 4.
t4_detail = {
    1: {"page": (8,), "sub": "2a", "subq": (64.4, 0.2), "au": (5.1, 0.01), "ag": (2.5, 0.01), "nis": (67.9, 0.3), "acetone": 1.5, "pd": (2.9, 0.004), "cui": (1.2, 0.006), "propargyl": (25.1, 0.45), "dmso": 1.0, "tea": 1.0, "mass": 36.9, "purif": "petroleum ether/ethyl acetate 5:1", "name": "3-(5,8-dimethoxy-3-phenylnaphthalen-2-yl)prop-2-yn-1-ol"},
    2: {"page": (8,), "sub": "2b", "subq": (91.2, 0.3), "au": (7.3, 0.015), "ag": (3.1, 0.015), "nis": (100.9, 0.45), "acetone": 2.0, "pd": (4.4, 0.006), "cui": (2.1, 0.011), "propargyl": (35.6, 0.64), "dmso": 1.0, "tea": 1.0, "mass": 47.7, "purif": "petroleum ether/ethyl acetate 7:1", "interstage": "silica-gel chromatography; petroleum ether/ethyl acetate 40:1", "name": "3-(3-butyl-5,8-dimethoxynaphthalen-2-yl)prop-2-yn-1-ol"},
    3: {"page": (8,), "sub": "2c", "subq": (64.4, 0.2), "au": (5.1, 0.01), "ag": (2.4, 0.01), "nis": (66.8, 0.3), "acetone": 1.0, "pd": (2.9, 0.004), "cui": (1.1, 0.006), "propargyl": (23.0, 0.4), "dmso": 1.0, "tea": 1.0, "mass": 38.7, "purif": "petroleum ether/ethyl acetate 5:1 to 2:1", "name": "3-(7-phenylnaphtho[2,1-d][1,3]dioxol-8-yl)prop-2-yn-1-ol"},
    4: {"page": (8,), "sub": "2d", "subq": (87.0, 0.3), "au": (7.4, 0.015), "ag": (3.5, 0.015), "nis": (101.2, 0.45), "acetone": 2.0, "pd": (4.3, 0.006), "cui": (1.4, 0.007), "propargyl": (34.1, 0.6), "dmso": 1.0, "tea": 1.0, "mass": 56.8, "purif": "petroleum ether/ethyl acetate 10:1 to 5:1", "name": "3-(7-butylnaphtho[2,1-d][1,3]dioxol-8-yl)prop-2-yn-1-ol"},
    5: {"page": (8, 9), "sub": "2e", "subq": (96.6, 0.3), "au": (7.3, 0.015), "ag": (3.1, 0.015), "nis": (102.4, 0.45), "acetone": 2.0, "pd": (4.5, 0.006), "cui": (2.0, 0.011), "propargyl": (40.0, 0.71), "dmso": 1.0, "tea": 1.0, "mass": 49.5, "purif": None, "interstage": "silica-gel chromatography; petroleum ether/ethyl acetate 40:1", "name": "3-(7-p-tolylnaphtho[2,1-d][1,3]dioxol-8-yl)prop-2-yn-1-ol"},
    6: {"page": (9,), "sub": "2f", "subq": (87.1, 0.3), "au": (7.9, 0.016), "ag": (4.2, 0.022), "nis": (102.5, 0.45), "acetone": 2.0, "pd": (4.3, 0.006), "cui": (1.9, 0.010), "propargyl": (34.1, 0.6), "dmso": 1.5, "tea": 1.5, "mass": 47.0, "purif": None, "interstage": "silica-gel chromatography; petroleum ether/ethyl acetate 40:1", "name": "3-{7-(ethoxymethyl)naphtho[2,1-d][1,3]dioxol-8-yl}prop-2-yn-1-ol"},
    7: {"page": (9,), "sub": "2g", "subq": (60.5, 0.2), "au": (5.1, 0.01), "ag": (2.2, 0.01), "nis": (68.2, 0.3), "acetone": 1.5, "pd": (2.9, 0.004), "cui": (1.2, 0.006), "propargyl": (23.9, 0.4), "dmso": 1.0, "tea": 1.0, "mass": 28.6, "purif": "petroleum ether/ethyl acetate 5:1 to 1:1", "name": "{8-(3-hydroxyprop-1-ynyl)naphtho[2,1-d][1,3]dioxol-7-yl}methyl acetate"},
    8: {"page": (9,), "sub": "2h", "subq": (97.1, 0.3), "au": (7.5, 0.015), "ag": (3.5, 0.015), "nis": (101.1, 0.45), "acetone": 2.0, "pd": (4.3, 0.006), "cui": (2.0, 0.010), "propargyl": (35.2, 0.6), "dmso": 1.5, "tea": 1.5, "mass": 41.2, "purif": "petroleum ether/ethyl acetate 3:1", "name": "3-(7,8-dimethoxy-3-phenylnaphthalen-2-yl)prop-2-yn-1-ol"},
    9: {"page": (9,), "sub": "2i", "subq": (101.5, 0.3), "au": (7.5, 0.015), "ag": (3.2, 0.015), "nis": (101.5, 0.45), "acetone": 2.0, "pd": (4.4, 0.006), "cui": (1.2, 0.006), "propargyl": (35.1, 0.6), "dmso": 1.5, "tea": 1.5, "mass": 47.5, "purif": None, "name": "3-(3-butyl-6,7,8-trimethoxynaphthalen-2-yl)prop-2-yn-1-ol"},
}
for entry, detail in t4_detail.items():
    evidence = ev(*detail["page"])
    record = take(f"table4_entry{entry}")
    add_evidence(record, evidence)
    prefix = f"t4e{entry}_"
    for entity, values in ((detail["sub"], detail["subq"]), ("au", detail["au"]), ("ag", detail["ag"]), ("nis", detail["nis"]), ("pd", detail["pd"]), ("cui", detail["cui"]), ("propargyl", detail["propargyl"])):
        add_amount(record, prefix + entity, "mass", {"number": values[0], "unit": "mg"}, evidence)
        add_amount(record, prefix + entity, "amount", {"number": values[1], "unit": "mmol"}, evidence)
    add_amount(record, prefix + "acetone", "volume", {"number": detail["acetone"], "unit": "mL"}, evidence)
    add_amount(record, prefix + "dmso", "volume", {"number": detail["dmso"], "unit": "mL"}, evidence)
    add_amount(record, prefix + "tea", "volume", {"number": detail["tea"], "unit": "mL"}, evidence)
    final = "5" + detail["sub"][-1]
    add_amount(record, prefix + final, "mass", {"number": detail["mass"], "unit": "mg"}, evidence)
    set_name(record, prefix + final, detail["name"], evidence)
    set_smiles(record, prefix + "nis", SMILES["NIS"], evidence)
    if detail.get("interstage"):
        set_condition(record, "gold_iodocyclization", "interstage_purification", detail["interstage"], evidence)
    set_condition(record, "sonogashira_coupling", "operation", "performed according to the representative tandem procedure", ev(8, *detail["page"]))
    if detail["purif"]:
        set_condition(record, "sonogashira_coupling", "purification", "silica-gel column chromatography; " + detail["purif"], evidence)
    if entry == 1:
        set_condition(record, "sonogashira_coupling", "atmosphere", "N2", evidence)
        set_condition(record, "sonogashira_coupling", "workup", "quenched with 5 mL water; extracted with diethyl ether (3 x 15 mL); combined organic layers washed with water and dried over anhydrous Na2SO4; filtered and evaporated", evidence)
    # The isolated 4g/4i procedures are separate batches and must not be folded into these tandem rows.
    record["outcomes"] = [o for o in record["outcomes"] if o["name"] not in {"isolated_yield_4g", "isolated_yield_4i"}]
    record["notes"] = [note("The reported final yield is a combined isolated yield over both stages from substrate 2; it is not the isolated yield of stage 2 alone.", ev(4, *detail["page"])), note("This detailed batch was merged into its Table 4 row; separately charged isolated 4g/4i preparations remain separate records.", evidence)]
    record["review"]["unresolved"] = BASE_UNRESOLVED + ["The detailed tandem paragraph uses the representative procedure for operations not restated in every abbreviated batch; intermediate 4 was not assigned an isolated mass."]
    records.append(record)


# Pages 9-10: exact downstream coupling batches, merged with Scheme 8 records.
couplings = {
    "6a": {"pages": (9,), "partner_label": "phenylboronic acid", "partner_name": "phenylboronic acid", "partner_smiles": SMILES["phenylboronic acid"], "pd": (8.9, 0.0077), "tbab": (2.5, 0.0075), "k2co3": (42.0, 0.30), "water": 0.15, "partner": (25.1, 0.21), "sub": (57.0, 0.15), "thf": 1.5, "prod": 39.8, "purif": "petroleum ether/ethyl acetate 20:1", "name": "1,4-dimethoxy-6,7-diphenylnaphthalene"},
    "7a": {"pages": (9, 10), "partner_label": "4-methoxyphenylboronic acid", "partner_name": "4-methoxyphenylboronic acid", "partner_smiles": SMILES["4-methoxyphenylboronic acid"], "pd": (12.1, 0.01), "tbab": (3.3, 0.01), "k2co3": (56.1, 0.40), "water": 0.20, "partner": (34.0, 0.22), "sub": (78.5, 0.20), "thf": 2.0, "prod": 63.3, "purif": "petroleum ether/ethyl acetate 80:1", "name": "1,4-dimethoxy-6-(4-methoxyphenyl)-7-phenylnaphthalene"},
    "8a": {"pages": (10,), "partner_label": "(E)-styrylboronic acid", "partner_name": "(E)-styrylboronic acid", "partner_smiles": SMILES["(E)-styrylboronic acid"], "pd": (12.5, 0.01), "tbab": (3.5, 0.01), "k2co3": (59.2, 0.40), "water": 0.20, "partner": (35.1, 0.22), "sub": (74.1, 0.19), "thf": 2.0, "prod": 50.5, "purif": "petroleum ether/ethyl acetate 200:1", "name": "(E)-1,4-dimethoxy-6-phenyl-7-styrylnaphthalene"},
}
for product, detail in couplings.items():
    evidence = ev(*detail["pages"])
    record = take(f"scheme8_to_{product}")
    add_evidence(record, evidence)
    prefix = f"s8_{product}"
    partner = get_participant(record, prefix + "_partner")
    partner["label"] = fact(detail["partner_label"], evidence)
    partner["name"] = fact(detail["partner_name"], evidence)
    partner["smiles"] = fact(detail["partner_smiles"], evidence)
    set_name(record, prefix + "_product", detail["name"], evidence)
    for entity, values in (("_pd", detail["pd"]), ("_add0", detail["tbab"]), ("_add1", detail["k2co3"]), ("_partner", detail["partner"]), ("_4a", detail["sub"])):
        add_amount(record, prefix + entity, "mass", {"number": values[0], "unit": "mg"}, evidence)
        add_amount(record, prefix + entity, "amount", {"number": values[1], "unit": "mmol"}, evidence)
    add_amount(record, prefix + "_solv1", "volume", {"number": detail["water"], "unit": "mL"}, evidence)
    add_amount(record, prefix + "_solv0", "volume", {"number": detail["thf"], "unit": "mL"}, evidence)
    add_amount(record, prefix + "_product", "mass", {"number": detail["prod"], "unit": "mg"}, evidence)
    set_smiles(record, prefix + "_add0", SMILES["TBAB"], evidence)
    set_condition(record, "pd_coupling", "atmosphere", "N2", ev(9, *detail["pages"]))
    set_condition(record, "pd_coupling", "operation", "performed according to the representative Suzuki procedure and monitored by TLC", ev(9, *detail["pages"]))
    set_condition(record, "pd_coupling", "purification", "silica-gel column chromatography; " + detail["purif"], evidence)
    old = f"reported_yield_{product}"
    new = f"isolated_yield_{product}"
    current = next(item for item in record["outcomes"] if item["name"] in {old, new})["fact"]["value"]
    replace_outcome(record, old, new, current, evidence, (prefix + "_product",))
    add_outcome(record, "yield_measurement_basis", "isolated after chromatography", evidence, (prefix + "_product",))
    record["notes"] = [note("The detailed experimental paragraph identifies the coupling partner; it overrides any ambiguous small arrow label in Scheme 8.", evidence)] if product == "7a" else []
    record["review"]["unresolved"] = BASE_UNRESOLVED + ["The abbreviated 7a/8a paragraph relies on the representative Suzuki procedure for operations not restated locally."] if product in {"7a", "8a"} else BASE_UNRESOLVED
    records.append(record)


# 9a Sonogashira batch on page 10.
record = take("scheme8_to_9a")
evidence = ev(10)
add_evidence(record, evidence)
prefix = "s8_9a"
partner = get_participant(record, prefix + "_partner")
partner["label"] = fact("1-ethynyl-4-methoxybenzene", evidence)
partner["name"] = fact("1-ethynyl-4-methoxybenzene", evidence)
partner["smiles"] = fact(SMILES["1-ethynyl-4-methoxybenzene"], evidence)
set_name(record, prefix + "_product", "1,4-dimethoxy-6-[(4-methoxyphenyl)ethynyl]-7-phenylnaphthalene", evidence)
for entity, values in (("_pd", (3.5, 0.005)), ("_add0", (1.9, 0.01)), ("_4a", (78.0, 0.20)), ("_partner", (35.1, 0.27))):
    add_amount(record, prefix + entity, "mass", {"number": values[0], "unit": "mg"}, evidence)
    add_amount(record, prefix + entity, "amount", {"number": values[1], "unit": "mmol"}, evidence)
add_amount(record, prefix + "_solv0", "volume", {"number": 1, "unit": "mL"}, evidence)
add_amount(record, prefix + "_solv1", "volume", {"number": 1, "unit": "mL"}, evidence)
add_amount(record, prefix + "_product", "mass", {"number": 72.1, "unit": "mg"}, evidence)
set_condition(record, "pd_coupling", "atmosphere", "N2", ev(8, 10))
set_condition(record, "pd_coupling", "operation", "performed following the representative Sonogashira coupling procedure", ev(8, 10))
set_condition(record, "pd_coupling", "purification", "silica-gel column chromatography; petroleum ether/ethyl acetate 30:1", evidence)
current = next(item for item in record["outcomes"] if item["name"] in {"reported_yield_9a", "isolated_yield_9a"})["fact"]["value"]
replace_outcome(record, "reported_yield_9a", "isolated_yield_9a", current, evidence, (prefix + "_product",))
add_outcome(record, "yield_measurement_basis", "isolated after chromatography", evidence, (prefix + "_product",))
record["notes"] = []
record["review"]["unresolved"] = BASE_UNRESOLVED + ["The page-10 paragraph follows the earlier Sonogashira procedure and does not restate every operation or workup volume."]
records.append(record)


# Preserve the raw machine submission and an exact five-page coverage ledger.
OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")


def ids(*suffixes):
    return [f"{DOC}:{suffix}" for suffix in suffixes]


coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 7, "state": "attempted",
            "regions": [
                {"region": "upper-left continuation of 3e characterization", "finding": "Analytical continuation only; linked to the already extracted 3e experiment and not counted as a new reaction.", "evidence_ids": ev(7)},
                {"region": "left column preparations of 3f-3i", "finding": "Detailed AuCl(PPh3)/AgBF4 cyclization batches merged into Table 2 entries 6-9 with exact quantities, product masses, isolated yields, and chromatography.", "evidence_ids": ev(7)},
                {"region": "upper-right preparation of 3j", "finding": "Detailed 3j batch merged into Table 2 entry 10.", "evidence_ids": ev(7)},
                {"region": "right-column Synthesis of Iodonaphthalenes 4", "finding": "Detailed isolated 4a and 4g batches extracted; 4g is distinct from the later Table 4 tandem batch because the exact charge differs.", "evidence_ids": ev(7)},
            ],
            "record_ids": ids(*[f"table2_entry{i}" for i in range(5, 11)], "scheme7_4a_isolated_batch", "scheme7_4g_isolated_batch"),
            "unresolved": ["Abbreviated 3f-3j batches refer to the representative procedure for operations not restated on page 7; structures remain machine-unverified."],
        },
        {
            "page": 8, "state": "attempted",
            "regions": [
                {"region": "top-left isolated 4i preparation", "finding": "Independent isolated 4i batch extracted with exact charge, 50% isolated yield, 60% NMR yield, and 4i/3i = 100:0; the printed reaction duration is missing.", "evidence_ids": ev(8)},
                {"region": "left-column representative tandem preparation of 5a", "finding": "Full two-stage batch merged into Table 4 entry 1, including exact quantities, N2 atmosphere, workup, purification, and combined yield.", "evidence_ids": ev(8)},
                {"region": "remaining preparations 5b-5d and start of 5e", "finding": "Detailed tandem batches merged into Table 4 entries 2-5; 5e outcome continues on page 9.", "evidence_ids": ev(8)},
                {"region": "spectroscopic paragraphs", "finding": "Characterization supports identities but was not treated as additional reaction experiments.", "evidence_ids": ev(8)},
            ],
            "record_ids": ids("scheme7_4i_isolated_batch", *[f"table4_entry{i}" for i in range(1, 6)]),
            "unresolved": ["The source omits the duration in the isolated 4i sentence ('at 0 °C for afforded'); it was not inferred from the distinct tandem batch."],
        },
        {
            "page": 9, "state": "attempted",
            "regions": [
                {"region": "top-left continuation of 5e", "finding": "5e product mass and combined 52% yield complete the cross-page Table 4 entry 5 record.", "evidence_ids": ev(9)},
                {"region": "preparations of 5f-5i", "finding": "Four detailed two-stage batches merged into Table 4 entries 6-9; separately charged isolated 4g/4i batches were not folded into these rows.", "evidence_ids": ev(9)},
                {"region": "lower-right Suzuki preparations 6a and 7a", "finding": "Detailed 6a and 7a batches merged into Scheme 8 records; page 9 explicitly identifies 4-methoxyphenylboronic acid for 7a.", "evidence_ids": ev(9)},
                {"region": "spectroscopic paragraphs", "finding": "Analytical data were treated as characterization, not separate reactions.", "evidence_ids": ev(9)},
            ],
            "record_ids": ids(*[f"table4_entry{i}" for i in range(5, 10)], "scheme8_to_6a", "scheme8_to_7a"),
            "unresolved": ["Several abbreviated tandem batches rely on the representative 5a procedure and do not restate all operations or workup volumes."],
        },
        {
            "page": 10, "state": "attempted",
            "regions": [
                {"region": "top-left continuation of 7a characterization", "finding": "Continuation of analytical data for the page-9 7a batch; no new experiment.", "evidence_ids": ev(10)},
                {"region": "left-column preparations of 8a and 9a", "finding": "Detailed Suzuki preparation of 8a and Sonogashira preparation of 9a merged into their Scheme 8 records with exact quantities, product masses, chromatography, and isolated yields.", "evidence_ids": ev(10)},
                {"region": "Supporting Information notice and acknowledgments", "finding": "The paper advertises SI and reproduction of selected results, but no SI file was supplied; neither statement was converted into an experiment or SI association.", "evidence_ids": ev(10)},
                {"region": "references 1-19", "finding": "Bibliographic context only; cited literature was not represented as experiments of this paper.", "evidence_ids": ev(10)},
            ],
            "record_ids": ids("scheme8_to_7a", "scheme8_to_8a", "scheme8_to_9a"),
            "unresolved": ["The advertised Supporting Information was not provided or associated; candidate structures remain unverified."],
        },
        {
            "page": 11, "state": "attempted",
            "regions": [
                {"region": "references 20-24 and publication dates", "finding": "Reference list and publication metadata only; no current-paper experimental batch, scheme, table, arrow, or footnote requiring a reaction record is present.", "evidence_ids": ev(11)},
            ],
            "record_ids": [],
            "unresolved": ["None beyond the document-wide unassociated SI and unverified structures; no experiment is claimed on this page."],
        },
    ],
}
COVERAGE.parent.mkdir(parents=True, exist_ok=True)
COVERAGE.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")


tasks = json.loads(TASKS.read_text())
for task in tasks:
    if task.get("document_id") == DOC:
        marker = task.get("task_id", "").split(":page")[-1].split(":")[0]
        if marker.isdigit() and 7 <= int(marker) <= 11:
            task["state"] = "attempted"
            task["reason"] = "Original page image and text inspected; experiments reconciled into source-linked records and coverage ledger."
TASKS.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"submitted_records": len(records), "new_record_ids": 2, "coverage_pages": len(coverage["pages"]), "output": str(OUT.relative_to(ROOT))}, ensure_ascii=False))
