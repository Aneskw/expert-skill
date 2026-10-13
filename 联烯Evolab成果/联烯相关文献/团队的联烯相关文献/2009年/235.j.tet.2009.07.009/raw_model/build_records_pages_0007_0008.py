#!/usr/bin/env python3
"""Enrich existing reaction records with source details visible on PDF pages 7--8."""

import copy
import json
from pathlib import Path


DOC = "doc_1cbf5a93b96a7964"
BASE = Path(__file__).resolve().parents[1]
BASE_RECORDS = Path(__file__).with_name("records_pages_0001_0006.json")
OUT = Path(__file__).with_name("records_pages_0007_0008.json")


def ev(*pages):
    evidence = []
    for page in pages:
        evidence.extend([f"{DOC}:page{page}:text", f"{DOC}:page{page}:image"])
    return evidence


def fact(value, evidence):
    return {
        "value": value,
        "evidence_ids": list(evidence) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def qty(number, unit, raw_text=None):
    value = {"number": number, "unit": unit}
    if raw_text is not None:
        value["raw_text"] = raw_text
    return value


def field(name, value, evidence, targets=None):
    item = {"name": name, "fact": fact(value, evidence)}
    if targets:
        item["target_entity_ids"] = list(targets)
    return item


def add_evidence(container, evidence):
    container["evidence_ids"] = list(dict.fromkeys(container["evidence_ids"] + list(evidence)))


def add_fact_evidence(item, evidence):
    item["fact"]["evidence_ids"] = list(dict.fromkeys(item["fact"]["evidence_ids"] + list(evidence)))


def participant(record, entity_id):
    return next(p for p in record["participants"] if p["entity_id"] == entity_id)


def participant_by_label(record, label):
    return next(p for p in record["participants"] if p["label"]["value"] == label)


def condition(record, name):
    return next(c for c in record["steps"][0]["conditions"] if c["name"] == name)


def outcome(record, name):
    return next(o for o in record["outcomes"] if o["name"] == name)


def add_amount(part, name, value, evidence):
    part["amounts"].append(field(name, value, evidence))


def add_condition(record, name, value, evidence, targets=None):
    record["steps"][0]["conditions"].append(field(name, value, evidence, targets))


def set_product_name(record, name, evidence, product_id="product"):
    participant(record, product_id)["name"] = fact(name, evidence)


def add_standard_workup(record, evidence):
    add_condition(
        record,
        "workup",
        "after TLC-indicated consumption, quenched with water, extracted with diethyl ether, washed with brine, and dried over anhydrous Na2SO4; then filtered and evaporated",
        evidence,
    )
    add_condition(
        record,
        "purification",
        "flash chromatography on silica gel (dichloromethane/ethyl acetate 10:1 to 5:1)",
        evidence,
    )


data = json.loads(BASE_RECORDS.read_text())
by_suffix = {r["source_reaction_id"]: r for r in data}
selected = []


def take(suffix, pages):
    record = copy.deepcopy(by_suffix[suffix])
    add_evidence(record, ev(*pages))
    record["status"] = "needs_review"
    record["completeness"] = "partial"
    selected.append(record)
    return record


# Page 7 begins with the detailed Conditions-B batch for Table 3 entry 10.
r = take("table3_entry10", (2, 6, 7))
e7 = ev(7)
add_amount(participant(r, "substrate"), "mass", qty(75.7, "mg"), e7)
add_amount(participant(r, "substrate"), "amount", qty(0.19, "mmol", "section 4.2.6.2 detailed batch: 0.19 mmol"), e7)
add_amount(participant(r, "selectfluor"), "mass", qty(104.5, "mg"), e7)
add_amount(participant(r, "selectfluor"), "amount", qty(0.285, "mmol", "section 4.2.6.2 detailed batch: 0.285 mmol"), e7)
add_amount(participant(r, "selectfluor"), "purity", qty(95, "%"), e7)
add_amount(participant(r, "water"), "mass", qty(23.1, "mg"), e7)
add_amount(participant(r, "water"), "amount", qty(1.33, "mmol", "section 4.2.6.2 detailed batch: 1.33 mmol"), e7)
add_amount(participant(r, "product"), "mass", qty(61.6, "mg"), e7)
set_product_name(r, "2-fluoro-3-hydroxy-1,3-diphenyl-1(E)-butenyl diphenyl phosphine oxide", e7)
add_fact_evidence(condition(r, "temperature"), e7)
add_fact_evidence(condition(r, "reaction_time"), e7)
add_fact_evidence(outcome(r, "isolated_yield"), e7)
add_fact_evidence(outcome(r, "yield_measurement_basis"), e7)
add_standard_workup(r, ev(6, 7))
r["review"]["unresolved"] = [
    "All structures remain unverified; labels and the product name are retained from the source.",
    "No supporting-information file was explicitly associated.",
    "Table 3 condition B reports 0.20 mmol substrate, 0.30 mmol Selectfluor, and 1.4 mmol water, whereas section 4.2.6.2 reports 0.19, 0.285, and 1.33 mmol; both source values are retained.",
]


# Typical procedure IV is the detailed 0.20 mmol batch behind Table 4 entry 7.
r = take("table4_entry7", (2, 7))
add_amount(participant(r, "substrate"), "mass", qty(62.9, "mg"), e7)
add_amount(participant(r, "selectfluor"), "mass", qty(105.6, "mg"), e7)
add_amount(participant_by_label(r, "MeNO2"), "volume", qty(2.0, "mL"), e7)
add_amount(participant_by_label(r, "H2O"), "volume", qty(0.2, "mL"), e7)
add_amount(participant(r, "product"), "mass", qty(43.3, "mg"), e7)
set_product_name(r, "2-fluoro-3-hydroxy-3-phenyl-1(E)-propenyl diphenyl phosphine oxide", e7)
add_fact_evidence(condition(r, "temperature"), e7)
add_fact_evidence(condition(r, "reaction_time"), e7)
add_fact_evidence(outcome(r, "isolated_yield_E-2f"), e7)
add_standard_workup(r, e7)
r["review"]["unresolved"] = [
    "All structures remain unverified; labels and the product name are retained from the source.",
    "No supporting-information file was explicitly associated.",
    "The 88% NMR yield is reported in Table 4; the detailed batch reports only the 62% isolated yield.",
]


# Sections 4.3.2--4.3.9 correspond to Table 5 entries 2--9. Exact detailed-batch
# quantities are retained alongside the table-footnote quantities, including scale conflicts.
scope = [
    # suffix, pages, substrate mass/mmol, Selectfluor mass/mmol/purity, MeNO2/H2O,
    # temperature, detailed time, product mass/yield, full product name, scale conflict, time conflict
    ("table5_entry2", (3, 7), 71.5, 0.20, 186.7, 0.50, 95, 2.0, 0.2, 80, 28.0, 25.8, 33,
     "2-fluoro-3-hydroxy-3-(4-nitrophenyl)-1(E)-propenyl diphenyl phosphine oxide", True, False),
    ("table5_entry3", (3, 7), 100.5, 0.30, 159.9, 0.45, None, 3.0, 0.3, 80, 10.0, 80.2, 72,
     "2-fluoro-3-hydroxy-3-(4-fluorophenyl)-1(E)-propenyl diphenyl phosphine oxide", False, False),
    ("table5_entry4", (3, 7), 105.8, 0.30, 159.8, 0.45, None, 3.0, 0.3, 80, 12.0, 65.0, 56,
     "2-fluoro-3-hydroxy-3-(4-chlorophenyl)-1(E)-propenyl diphenyl phosphine oxide", False, False),
    ("table5_entry5", (3, 7), 70.3, 0.20, 148.9, 0.40, 95, 2.0, 0.2, 80, 24.0, 38.5, 50,
     "2-fluoro-3-hydroxy-3-(3-chlorophenyl)-1(E)-propenyl diphenyl phosphine oxide", True, False),
    ("table5_entry6", (3, 7), 106.0, 0.30, 159.0, 0.45, None, 3.0, 0.3, 80, 33.0, 65.5, 56,
     "2-fluoro-3-hydroxy-3-(2-chlorophenyl)-1(E)-propenyl diphenyl phosphine oxide", False, False),
    ("table5_entry7", (3, 7), 66.2, 0.20, 106.0, 0.30, None, 2.0, 0.2, 40, 25.0, 46.4, 63,
     "2-fluoro-3-hydroxy-3-(4-methylphenyl)-1(E)-propenyl diphenyl phosphine oxide", True, False),
    ("table5_entry8", (3, 7, 8), 74.9, 0.20, 149.6, 0.40, 95, 2.0, 0.2, 80, 21.0, 48.1, 59,
     "2-fluoro-1-hydroxy-1-phenyl-2(E)-hept-2-en-3-yl diphenyl phosphine oxide", True, True),
    ("table5_entry9", (3, 8), 78.6, 0.20, 105.5, 0.30, None, 2.0, 0.2, 80, 12.5, 57.9, 67,
     "2-fluoro-3-hydroxy-1,3-diphenyl-1(E)-propenyl diphenyl phosphine oxide", True, False),
]

for suffix, pages, smass, smmol, fmass, fmmol, purity, mno2, water, temp, hours, pmass, yld, pname, scale_conflict, time_conflict in scope:
    r = take(suffix, pages)
    detail_page = 8 if suffix == "table5_entry9" else 7
    detail_ev = ev(7, 8) if suffix == "table5_entry8" else ev(detail_page)
    add_amount(participant(r, "substrate"), "mass", qty(smass, "mg"), detail_ev)
    add_amount(participant(r, "substrate"), "amount", qty(smmol, "mmol", f"detailed preparation: {smmol} mmol"), detail_ev)
    add_amount(participant(r, "selectfluor"), "mass", qty(fmass, "mg"), detail_ev)
    add_amount(participant(r, "selectfluor"), "amount", qty(fmmol, "mmol", f"detailed preparation: {fmmol} mmol"), detail_ev)
    if purity is not None:
        add_amount(participant(r, "selectfluor"), "purity", qty(purity, "%"), detail_ev)
    add_amount(participant(r, "solvent1"), "volume", qty(mno2, "mL", f"detailed preparation: {mno2} mL"), detail_ev)
    add_amount(participant(r, "water"), "volume", qty(water, "mL", f"detailed preparation: {water} mL"), detail_ev)
    add_amount(participant(r, "product"), "mass", qty(pmass, "mg"), detail_ev)
    set_product_name(r, pname, detail_ev)
    add_fact_evidence(condition(r, "temperature"), detail_ev)
    if time_conflict:
        add_condition(r, "reaction_time", qty(hours, "h", f"section 4.3.8 detailed preparation: {hours} h"), detail_ev)
    else:
        add_fact_evidence(condition(r, "reaction_time"), detail_ev)
    add_fact_evidence(outcome(r, "isolated_yield"), detail_ev)
    add_fact_evidence(outcome(r, "yield_measurement_basis"), detail_ev)
    add_standard_workup(r, ev(7))
    unresolved = [
        "All structures remain unverified; labels and the product name are retained from the source.",
        "No supporting-information file was explicitly associated.",
    ]
    if scale_conflict:
        unresolved.append("Table 5 footnote-a scale and the named detailed preparation use different substrate/reagent/solvent quantities; both source reports are retained rather than silently reconciled.")
    if time_conflict:
        unresolved.append("Table 5 entry 8 reports 24.0 h, while section 4.3.8 reports 21 h; both reaction times are retained.")
    if suffix in {"table5_entry5", "table5_entry8", "table5_entry9"}:
        unresolved.append("Table 5 refers to Supplementary data for recrystallization detail, but no SI file was explicitly supplied.")
    r["review"]["unresolved"] = unresolved


e8 = ev(8)

# Table 6 entry 5 and section 4.3.10 agree on isolated yield but disagree on time.
r = take("table6_entry5", (3, 8))
add_amount(participant(r, "substrate"), "mass", qty(104.0, "mg"), e8)
add_amount(participant(r, "selectfluor"), "mass", qty(391.7, "mg"), e8)
add_amount(participant(r, "selectfluor"), "purity", qty(95, "%"), e8)
add_amount(participant(r, "product2"), "mass", qty(16.8, "mg"), e8)
set_product_name(r, "2-fluoro-3-hydroxy-3-(3-fluoro-4-methoxyphenyl)-1(E)-propenyl diphenyl phosphine oxide", e8, "product2")
add_fact_evidence(condition(r, "temperature"), e8)
add_condition(r, "reaction_time", qty(9.5, "h", "section 4.3.10 detailed preparation: 9.5 h"), e8)
add_fact_evidence(outcome(r, "isolated_yield"), e8)
add_standard_workup(r, ev(7))
r["review"]["unresolved"] = [
    "All structures remain unverified; labels and the product name are retained from the source.",
    "No supporting-information file was explicitly associated.",
    "Table 6 entry 5 reports 8.0 h, while section 4.3.10 reports 9.5 h; both reaction times are retained.",
    "The 25% combined NMR yield and 0/100 product ratio are table results; the detailed batch states only 14% isolated E-4o.",
]


# Table 6 entry 4 and section 4.3.11 agree on the isolated mixture yield and ratio,
# but the table and detailed paragraph report different durations.
r = take("table6_entry4", (3, 8))
add_amount(participant(r, "substrate"), "mass", qty(103.3, "mg"), e8)
add_amount(participant(r, "selectfluor"), "mass", qty(101.2, "mg"), e8)
add_amount(participant(r, "selectfluor"), "purity", qty(95, "%"), e8)
add_condition(r, "reaction_time", qty(42, "h", "section 4.3.11 detailed preparation: 42 h"), e8)
add_fact_evidence(condition(r, "temperature"), e8)
add_fact_evidence(outcome(r, "product_ratio_E-2o_to_E-4o"), e8)
add_fact_evidence(outcome(r, "isolated_yield"), e8)
r["outcomes"].append(field("isolated_product_mixture_mass", qty(46.8, "mg"), e8, ["product", "product2"]))
set_product_name(r, "2-fluoro-3-hydroxy-3-(4-methoxyphenyl)-1(E)-propenyl diphenyl phosphine oxide", e8, "product")
add_condition(r, "workup", "quenched with water, extracted with diethyl ether, washed with brine, and dried over anhydrous Na2SO4; then filtered and evaporated", e8)
add_condition(r, "purification", "flash chromatography on silica gel (petroleum ether/ethyl acetate 3:2); E-2o and E-4o obtained as a mixture", e8)
r["review"]["unresolved"] = [
    "All structures remain unverified; labels and the product name are retained from the source.",
    "No supporting-information file was explicitly associated.",
    "Table 6 entry 4 reports 8.0 h, while section 4.3.11 reports 42 h; both reaction times are retained.",
    "The 69% combined NMR yield is table-only; the detailed paragraph reports 46.8 mg and 45% isolated mixture at E-2o/E-4o = 97/3.",
]


# Equation (1) and section 4.3.12 are the same E-2o-to-E-4o experiment. The
# detailed paragraph additionally identifies E-4o already present in the input mixture.
r = take("equation1_E-2o_to_E-4o", (3, 8))
add_amount(participant(r, "substrate"), "mass", qty(117.4, "mg"), e8)
add_amount(participant(r, "selectfluor"), "mass", qty(246.7, "mg"), e8)
add_amount(participant(r, "selectfluor"), "purity", qty(95, "%"), e8)
starting_impurity = {
    "entity_id": "starting_E-4o",
    "role": "reactant",
    "label": fact("E-4o present in starting E-2o/E-4o mixture", e8),
    "name": fact(None, e8),
    "smiles": fact(None, e8),
    "smiles_parseable": None,
    "structure_verified": False,
    "amounts": [],
}
r["participants"].append(starting_impurity)
r["steps"][0]["participant_ids"].append("starting_E-4o")
add_condition(r, "starting_material_ratio_E-2o_to_E-4o", "97.5/2.5", e8, ["substrate", "starting_E-4o"])
add_condition(r, "reaction_time", qty(10, "h", "section 4.3.12 detailed preparation: 10 h"), e8)
add_fact_evidence(condition(r, "temperature"), e8)
add_amount(participant(r, "product"), "mass", qty(23.7, "mg"), e8)
set_product_name(r, "2-fluoro-3-hydroxy-3-(3-fluoro-4-methoxyphenyl)-1(E)-propenyl diphenyl phosphine oxide", e8)
add_fact_evidence(outcome(r, "isolated_yield_E-4o"), e8)
add_fact_evidence(outcome(r, "yield_measurement_basis"), e8)
add_standard_workup(r, ev(7, 8))
r["review"]["unresolved"] = [
    "All structures remain unverified; labels and the product name are retained from the source.",
    "No supporting-information file was explicitly associated.",
    "Equation (1) reports 8.0 h, while section 4.3.12 reports 10 h; both reaction times are retained.",
    "The detailed starting material is an E-2o/E-4o 97.5:2.5 mixture; E-4o is represented separately as an input impurity and as the isolated product entity.",
]


OUT.write_text(json.dumps(selected, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"records": len(selected), "path": str(OUT)}, ensure_ascii=False))
