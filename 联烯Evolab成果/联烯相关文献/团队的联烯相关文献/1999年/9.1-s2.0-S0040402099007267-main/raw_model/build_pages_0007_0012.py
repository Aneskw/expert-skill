#!/usr/bin/env python3
"""Enrich existing machine records with source evidence from PDF pages 7-12."""

from copy import deepcopy
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "runs/current"
DATASET = OUT / "dataset.json"
RAW = OUT / "raw_model/records_pages_0007_0012.json"
COVERAGE = OUT / "coverage/pages_0007_0012.json"
TASKS = OUT / "tasks.json"
DOC = "doc_13430d7f78131b09"


def evidence(pages):
    ids = []
    for page in dict.fromkeys(pages):
        ids.extend([f"{DOC}:page{page}:image", f"{DOC}:page{page}:text"])
    return ids


def fact(value, pages):
    return {
        "value": value,
        "evidence_ids": evidence(pages) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def quantity(number, unit):
    return {"number": number, "unit": unit}


def field(name, value, pages):
    return {"name": name, "fact": fact(value, pages)}


data = json.loads(DATASET.read_text())
existing = {r["record_id"]: r for r in data["experiments"]}


def get(suffix, pages):
    rid = f"{DOC}:{suffix}"
    record = deepcopy(existing[rid])
    record["status"] = "candidate"
    record["review"]["method"] = "none"
    record["review"]["reviewer"] = None
    record["review"]["checked_fields"] = []
    record["evidence_ids"] = list(dict.fromkeys(record["evidence_ids"] + evidence(pages)))
    return record


def participant(record, entity_id):
    return next(p for p in record["participants"] if p["entity_id"] == entity_id)


def ensure_participant(record, entity_id, role, name, pages, label=None, amounts=()):
    found = next((p for p in record["participants"] if p["entity_id"] == entity_id), None)
    if found is None:
        found = {
            "entity_id": entity_id,
            "role": role,
            "label": fact(label, pages),
            "name": fact(name, pages),
            "smiles": fact(None, []),
            "smiles_parseable": None,
            "structure_verified": False,
            "amounts": [],
        }
        record["participants"].append(found)
    else:
        found["role"] = role
        if label is not None:
            found["label"] = fact(label, pages)
        if name is not None:
            found["name"] = fact(name, pages)
    if amounts:
        found["amounts"] = [field(n, v, pages) for n, v in amounts]
    return found


def set_amounts(record, entity_id, pages, amounts):
    participant(record, entity_id)["amounts"] = [field(n, v, pages) for n, v in amounts]


def set_steps(record, rows):
    record["steps"] = [
        {
            "step_id": step_id,
            "participant_ids": participant_ids,
            "conditions": [field(name, value, pages) for name, value in conditions],
        }
        for step_id, participant_ids, conditions, pages in rows
    ]


def put_outcome(record, name, value, pages):
    record["outcomes"] = [o for o in record["outcomes"] if o["name"] != name]
    record["outcomes"].append(field(name, value, pages))


def add_note(record, value, pages):
    record["notes"].append(fact(value, pages))


def add_unresolved(record, *items):
    for item in items:
        if item not in record["review"]["unresolved"]:
            record["review"]["unresolved"].append(item)


def remove_unresolved_matching(record, text):
    record["review"]["unresolved"] = [
        item for item in record["review"]["unresolved"] if text not in item
    ]


records = []

# Page 7: completion of 2a and full/similar preparations of 2b-2d.
r = get("scheme2_iodolactonization_1a_to_2a", [7])
put_outcome(r, "physical_form", "white solid", [7])
put_outcome(r, "melting_point", "62-63 °C (n-hexane)", [7])
remove_unresolved_matching(r, "characterization continues beyond page 6")
add_unresolved(r, "Atmosphere and reaction concentration are not stated; no SI is supplied or associated.")
records.append(r)

r = get("scheme2_iodolactonization_1b_to_2b", [6, 7])
set_amounts(r, "substrate", [7], [("mass", quantity(182, "mg")), ("amount", quantity(1.0, "mmol"))])
set_amounts(r, "iodine", [7], [("mass", quantity(512, "mg")), ("amount", quantity(2.0, "mmol"))])
set_amounts(r, "k2co3", [7], [("mass", quantity(71, "mg")), ("amount", quantity(0.5, "mmol"))])
set_amounts(r, "product", [7], [("isolated_mass", quantity(277, "mg"))])
set_steps(r, [
    ("iodine_stage", ["substrate", "iodine", "solvent"], [("temperature", quantity(0, "°C")), ("time", quantity(1, "h"))], [6, 7]),
    ("base_stage", ["substrate", "iodine", "k2co3", "solvent", "product"], [("temperature", quantity(0, "°C")), ("time", quantity(10, "h"))], [6, 7]),
])
put_outcome(r, "yield", quantity(90, "%"), [7])
put_outcome(r, "yield_measurement_basis", "isolated product from a preparation stated to be similar to 2a", [6, 7])
put_outcome(r, "physical_form", "white solid", [7])
put_outcome(r, "melting_point", "78-79 °C (n-hexane)", [7])
add_note(r, "The source says 2b was prepared similarly to 2a; the staged conditions and workup therefore depend on that explicit cross-reference.", [6, 7])
add_unresolved(r, "Atmosphere and concentration are not stated; no SI is supplied or associated.")
records.append(r)

r = get("scheme2_bromolactonization_1a_to_2c", [7])
set_amounts(r, "substrate", [7], [("mass", quantity(140, "mg")), ("amount", quantity(1.0, "mmol"))])
set_amounts(r, "k2co3", [7], [("mass", quantity(138, "mg")), ("amount", quantity(1.0, "mmol"))])
set_amounts(r, "nbs", [7], [("mass", quantity(354, "mg")), ("amount", quantity(2.0, "mmol"))])
set_amounts(r, "water", [7], [("volume", quantity(5, "mL"))])
set_amounts(r, "product", [7], [("isolated_mass", quantity(184, "mg"))])
set_steps(r, [("reaction", ["substrate", "k2co3", "nbs", "water", "product"], [("temperature", quantity(25, "°C")), ("time", quantity(6, "h"))], [7])])
put_outcome(r, "yield", quantity(84, "%"), [7])
put_outcome(r, "yield_measurement_basis", "isolated after flash chromatography", [7])
put_outcome(r, "physical_form", "yellow oil", [7])
add_note(r, "Extracted with diethyl ether (3 x 10 mL), dried over anhydrous MgSO4, evaporated, and purified by silica-gel flash chromatography with petroleum ether/ethyl acetate 10:1.", [7])
add_unresolved(r, "Atmosphere and concentration are not stated; no SI is supplied or associated.")
records.append(r)

r = get("scheme2_bromolactonization_1b_to_2d", [7])
set_amounts(r, "substrate", [7], [("mass", quantity(182, "mg")), ("amount", quantity(1.0, "mmol"))])
set_amounts(r, "k2co3", [7], [("mass", quantity(138, "mg")), ("amount", quantity(1.0, "mmol"))])
set_amounts(r, "nbs", [7], [("mass", quantity(354, "mg")), ("amount", quantity(2.0, "mmol"))])
set_amounts(r, "product", [7], [("isolated_mass", quantity(214, "mg"))])
set_steps(r, [("reaction", ["substrate", "k2co3", "nbs", "water", "product"], [("temperature", quantity(25, "°C")), ("time", quantity(6, "h"))], [7])])
put_outcome(r, "yield", quantity(81, "%"), [7])
put_outcome(r, "yield_measurement_basis", "isolated product from a preparation stated to be similar to 2c", [7])
put_outcome(r, "physical_form", "white solid", [7])
put_outcome(r, "melting_point", "40-41.5 °C (n-hexane)", [7])
add_note(r, "The source says 2d was prepared similarly to 2c; solvent volume and workup are not repeated for 2d.", [7])
add_unresolved(r, "The 2d paragraph does not independently restate water volume, workup, atmosphere, or concentration; no SI is supplied or associated.")
records.append(r)

# Pages 7-9: Table 1 products, with the typical 3a procedure and row-specific charges.
r = get("table1_entry_01", [7])
set_amounts(r, "halobutenolide", [7], [("mass", quantity(66.5, "mg")), ("amount", quantity(0.25, "mmol"))])
set_amounts(r, "terminal_alkyne", [7], [("mass", quantity(27, "mg")), ("amount", quantity(0.26, "mmol"))])
set_amounts(r, "base", [7], [("mass", quantity(36, "mg")), ("amount", quantity(0.26, "mmol"))])
set_amounts(r, "pd_catalyst", [7], [("mass", quantity(1.8, "mg")), ("amount", quantity(0.0025, "mmol"))])
set_amounts(r, "cui", [7], [("mass", quantity(0.5, "mg")), ("amount", quantity(0.0025, "mmol"))])
set_amounts(r, "solvent", [7], [("volume", quantity(1, "mL"))])
set_amounts(r, "product", [7], [("isolated_mass", quantity(59.6, "mg"))])
set_steps(r, [("reaction", [p["entity_id"] for p in r["participants"]], [("temperature", quantity(20, "°C")), ("table_reported_time", quantity(3, "h")), ("typical_procedure_time", quantity(4, "h")), ("atmosphere", "Ar")], [3, 7])])
put_outcome(r, "yield", quantity(99, "%"), [3, 7])
put_outcome(r, "yield_measurement_basis", "isolated after flash chromatography", [7])
put_outcome(r, "physical_form", "pale yellow oil", [7])
add_note(r, "Filtered through a short silica column, evaporated, and purified by silica-gel flash chromatography with petroleum ether/ethyl acetate 20:1.", [7])
add_unresolved(r, "Table 1 reports 3 h, whereas the detailed typical procedure reports 4 h for the same 99% 3a preparation.")
records.append(r)

table1_details = {
    3: ([8], "halobutenolide", [("mass", quantity(66.5, "mg")), ("amount", quantity(0.25, "mmol"))], [("mass", quantity(21.3, "mg")), ("amount", quantity(0.26, "mmol"))], quantity(51.2, "mg"), None, "yellow oil"),
    4: ([8], "halobutenolide", [("mass", quantity(66.5, "mg")), ("amount", quantity(0.25, "mmol"))], [("mass", quantity(14.6, "mg")), ("amount", quantity(0.26, "mmol"))], quantity(47.9, "mg"), "petroleum ether/ethyl acetate 3:1", "yellow oil"),
    5: ([8], "halobutenolide", [("mass", quantity(26.6, "mg")), ("amount", quantity(0.10, "mmol"))], [("mass", quantity(12, "mg")), ("amount", quantity(0.12, "mmol"))], quantity(16.4, "mg"), None, "yellow oil"),
    6: ([8], "halobutenolide", [("mass", quantity(111.3, "mg")), ("amount", quantity(0.36, "mmol"))], [("mass", quantity(40.8, "mg")), ("amount", quantity(0.40, "mmol"))], quantity(94.1, "mg"), "petroleum ether/ethyl acetate 20:1", "white solid"),
    7: ([8, 9], "halobutenolide", [("mass", quantity(77, "mg")), ("amount", quantity(0.25, "mmol"))], [("mass", quantity(21.3, "mg")), ("amount", quantity(0.26, "mmol"))], quantity(56.3, "mg"), "petroleum ether/ethyl acetate 20:1", "yellow oil"),
    8: ([9], "halobutenolide", [("mass", quantity(77, "mg")), ("amount", quantity(0.25, "mmol"))], [("mass", quantity(14.6, "mg")), ("amount", quantity(0.26, "mmol"))], quantity(46.6, "mg"), "petroleum ether/ethyl acetate 3:1", "white solid"),
    9: ([9], "halobutenolide", [("mass", quantity(77, "mg")), ("amount", quantity(0.25, "mmol"))], [("mass", quantity(25.5, "mg")), ("amount", quantity(0.26, "mmol"))], quantity(48.7, "mg"), "petroleum ether/ethyl acetate 30:1", "yellow oil"),
}
for entry, (pages, substrate_id, substrate_amounts, alkyne_amounts, product_mass, eluent, physical) in table1_details.items():
    r = get(f"table1_entry_{entry:02d}", pages)
    set_amounts(r, substrate_id, pages, substrate_amounts)
    set_amounts(r, "terminal_alkyne", pages, alkyne_amounts)
    set_amounts(r, "product", pages, [("isolated_mass", product_mass)])
    put_outcome(r, "yield_measurement_basis", "isolated product from a preparation stated to use the Table 1 conditions and the typical procedure", [7] + pages)
    put_outcome(r, "physical_form", physical, pages)
    if eluent:
        add_note(r, f"Reported flash-chromatography eluent: {eluent}.", pages)
    add_note(r, "The source states that compounds 3b-3h were prepared similarly using the conditions listed in Table 1; unreported row-specific charges were not calculated from the table ratio.", [7] + pages)
    if entry == 5:
        add_unresolved(r, "The detailed 3d charge is 0.12 mmol alkyne per 0.10 mmol 2a, while the Table 1 footnote gives the standard alkyne ratio as 1.02; the source does not reconcile this difference.")
    add_unresolved(r, "Atmosphere, concentration, and any non-repeated workup details remain dependent on the typical-procedure cross-reference; no SI is supplied or associated.")
    records.append(r)

# Pages 9-11: aryl-, alkenyl-, vinyl-, and alkylzinc detailed procedures.
r = get("table2_entry_01", [9])
halide = participant(r, "halobutenolide")
halide["label"] = fact("2b in Table 2; 2a in the detailed procedure", [5, 9])
halide["name"] = fact("beta-halobutenolide substrate with a source-internal identity conflict", [5, 9])
halide["amounts"] = [field("mass", quantity(66.5, "mg"), [9]), field("amount", quantity(0.25, "mmol"), [9])]
ensure_participant(r, "phenyl_iodide", "reactant", "phenyl iodide", [9], amounts=[("mass", quantity(149, "mg")), ("amount", quantity(0.73, "mmol"))])
ensure_participant(r, "nbuli", "reagent", "n-BuLi (1.6 M in hexanes)", [9], amounts=[("volume", quantity(0.46, "mL")), ("amount", quantity(0.73, "mmol"))])
ensure_participant(r, "znbr2", "reagent", "ZnBr2", [9], amounts=[("mass", quantity(250, "mg")), ("amount", quantity(1.1, "mmol")), ("THF_solution_volume", quantity(1.5, "mL"))])
set_amounts(r, "thf", [9], [("phenyl_iodide_solution_volume", quantity(1, "mL"))])
set_amounts(r, "pd_catalyst", [9], [("mass", quantity(15, "mg")), ("amount", quantity(0.0125, "mmol"))])
set_amounts(r, "product", [9], [("reported_isolated_mass", quantity(60, "mg"))])
set_steps(r, [
    ("halogen_lithium_exchange", ["phenyl_iodide", "nbuli", "thf"], [("addition_temperature", quantity(-78, "°C")), ("hold_temperature", quantity(-40, "°C")), ("time", quantity(1, "h"))], [9]),
    ("transmetalation", ["phenyl_iodide", "nbuli", "znbr2", "organozinc", "thf"], [("initial_time", quantity(10, "min")), ("warm_to", quantity(25, "°C")), ("hold_time", quantity(30, "min"))], [9]),
    ("coupling", ["organozinc", "halobutenolide", "pd_catalyst", "thf", "product"], [("atmosphere", "Ar"), ("table_reported_time", quantity(2, "h")), ("detailed_procedure_time", quantity(4, "h")), ("monitoring", "TLC")], [5, 9]),
])
put_outcome(r, "yield", quantity(93, "%"), [5, 9])
put_outcome(r, "yield_measurement_basis", "isolated after flash chromatography", [9])
add_note(r, "Quenched with 0.5 M aqueous HCl, extracted with ethyl ether (3 x 15 mL), dried over anhydrous MgSO4, evaporated, and purified by flash chromatography with petroleum ether/ethyl acetate 10:1.", [9])
add_unresolved(r,
    "Table 2 prints substrate 2b and a 2 h time, while the detailed procedure names 2a and 4 h.",
    "The detailed heading calls 4a the n-butyl product, whereas the printed 60 mg at 93% is not reconciled with the stated 0.25 mmol 2a charge; source values are preserved without correction.")
records.append(r)

for entry, pages, precursor_id, precursor_name, precursor_amounts, substrate_amounts, product_amounts, eluent in [
    (2, [9, 10], "p_iodotoluene", "4-iodotoluene", [("mass", quantity(93.7, "mg")), ("amount", quantity(0.43, "mmol"))], [("mass", quantity(46.2, "mg")), ("amount", quantity(0.15, "mmol"))], [("isolated_mass", quantity(33.9, "mg"))], "petroleum ether/ethyl acetate 20:1"),
    (3, [10], "iodonaphthalene", "1-iodonaphthalene", [("mass", quantity(112, "mg")), ("amount", quantity(0.44, "mmol"))], [("mass", quantity(40, "mg")), ("amount", quantity(0.15, "mmol"))], [("isolated_mass", quantity(28, "mg"))], "petroleum ether/ethyl acetate 20:1"),
]:
    r = get(f"table2_entry_{entry:02d}", pages)
    ensure_participant(r, precursor_id, "reactant", precursor_name, pages, amounts=precursor_amounts)
    set_amounts(r, "halobutenolide", pages, substrate_amounts)
    set_amounts(r, "product", pages, product_amounts)
    put_outcome(r, "yield_measurement_basis", "isolated product from a preparation stated to be similar to the arylzinc typical procedure", [9] + pages)
    add_note(r, f"Reported flash-chromatography eluent: {eluent}.", pages)
    add_unresolved(r, "The paragraph does not independently repeat the organolithium/ZnBr2 charges, atmosphere, or workup; these remain tied to the explicit 'prepared similarly' cross-reference.")
    records.append(r)

r = get("table2_entry_04", [10])
ensure_participant(r, "e_hexenyl_iodide", "reactant", "(E)-1-iodo-1-hexene", [10], amounts=[("mass", quantity(90, "mg")), ("amount", quantity(0.438, "mmol"))])
ensure_participant(r, "nbuli", "reagent", "n-BuLi (1.6 M in hexanes)", [10], amounts=[("volume", quantity(0.27, "mL")), ("amount", quantity(0.438, "mmol"))])
ensure_participant(r, "znbr2", "reagent", "ZnBr2", [10], amounts=[("mass", quantity(148, "mg")), ("amount", quantity(0.658, "mmol")), ("THF_solution_volume", quantity(2, "mL"))])
set_amounts(r, "thf", [10], [("iodide_solution_volume", quantity(2, "mL"))])
set_amounts(r, "dmf_additive", [10], [("volume", quantity(1, "mL"))])
set_amounts(r, "pd_catalyst", [10], [("mass", quantity(9, "mg")), ("amount", quantity(0.008, "mmol"))])
set_amounts(r, "halobutenolide", [10], [("mass", quantity(46, "mg")), ("amount", quantity(0.15, "mmol"))])
set_amounts(r, "product", [10], [("reported_isolated_mass", quantity(60, "mg"))])
set_steps(r, [
    ("halogen_lithium_exchange", ["e_hexenyl_iodide", "nbuli", "thf"], [("addition_temperature", quantity(-78, "°C")), ("hold_temperature", quantity(-40, "°C")), ("time", quantity(1, "h"))], [10]),
    ("transmetalation", ["e_hexenyl_iodide", "nbuli", "znbr2", "organozinc", "thf", "dmf_additive"], [("initial_time", quantity(10, "min")), ("warm_to", quantity(25, "°C")), ("hold_time", quantity(30, "min")), ("observation", "became homogeneous after dry DMF addition")], [10]),
    ("coupling", ["organozinc", "halobutenolide", "pd_catalyst", "thf", "dmf_additive", "product"], [("atmosphere", "Ar"), ("table_reported_time", quantity(50, "min")), ("detailed_procedure_time", quantity(0.5, "h")), ("monitoring", "TLC")], [5, 10]),
])
put_outcome(r, "yield", quantity(77, "%"), [5, 10])
put_outcome(r, "yield_measurement_basis", "isolated after flash chromatography", [10])
add_note(r, "Quenched with 0.5 M aqueous HCl, extracted with ethyl ether (3 x 15 mL), dried over anhydrous MgSO4, evaporated, and purified by flash chromatography with petroleum ether/ethyl acetate 10:1.", [10])
add_unresolved(r, "The source prints 60 mg and 77% from 0.15 mmol of a product whose printed formula is C17H28O2; these values are preserved but appear internally inconsistent and require source review.")
records.append(r)

r = get("table2_entry_06", [10])
ensure_participant(r, "vinylmagnesium_bromide", "reactant", "vinylmagnesium bromide (1 M in THF)", [10], amounts=[("volume", quantity(0.5, "mL")), ("amount", quantity(0.5, "mmol"))])
ensure_participant(r, "znbr2", "reagent", "ZnBr2", [10], amounts=[("mass", quantity(150, "mg")), ("amount", quantity(0.66, "mmol")), ("THF_solution_volume", quantity(2, "mL"))])
set_amounts(r, "dmf_additive", [10], [("volume", quantity(1, "mL"))])
set_amounts(r, "pd_catalyst", [10], [("mass", quantity(9, "mg")), ("amount", quantity(0.008, "mmol"))])
set_amounts(r, "halobutenolide", [10], [("mass", quantity(40, "mg")), ("amount", quantity(0.15, "mmol"))])
set_amounts(r, "product", [10], [("isolated_mass", quantity(22.9, "mg"))])
set_steps(r, [
    ("transmetalation", ["vinylmagnesium_bromide", "znbr2", "organozinc", "thf", "dmf_additive"], [("temperature", "rt"), ("DMF_addition_after", quantity(30, "min")), ("post_addition_temperature", quantity(25, "°C")), ("post_addition_time", quantity(2, "h")), ("observation", "became homogeneous")], [10]),
    ("coupling", ["organozinc", "halobutenolide", "pd_catalyst", "thf", "dmf_additive", "product"], [("atmosphere", "Ar"), ("table_reported_time", quantity(10, "min")), ("detailed_procedure_time", quantity(10, "h")), ("monitoring", "TLC")], [5, 10]),
])
put_outcome(r, "yield", quantity(92, "%"), [5, 10])
put_outcome(r, "yield_measurement_basis", "isolated after flash chromatography", [10])
add_note(r, "Quenched with 0.5 M aqueous HCl, extracted with ethyl ether (3 x 15 mL), dried over MgSO4, evaporated, and purified by flash chromatography with petroleum ether/ethyl acetate 10:1.", [10])
add_unresolved(r, "Table 2 reports 10 min, whereas the detailed 4e procedure reports 10 h for the coupling stage.")
records.append(r)

r = get("table2_entry_07", [10, 11])
ensure_participant(r, "vinylmagnesium_bromide", "reactant", "vinylmagnesium bromide (1 M in THF)", [11], amounts=[("volume", quantity(0.5, "mL")), ("amount", quantity(0.5, "mmol"))])
set_amounts(r, "halobutenolide", [11], [("mass", quantity(46, "mg")), ("amount", quantity(0.15, "mmol"))])
set_amounts(r, "product", [11], [("isolated_mass", quantity(25.6, "mg"))])
put_outcome(r, "yield", quantity(82, "%"), [5, 11])
put_outcome(r, "yield_measurement_basis", "isolated product from a preparation stated to be similar to 4e", [10, 11])
put_outcome(r, "physical_form", "yellow oil", [11])
add_note(r, "Reported flash-chromatography eluent: petroleum ether/ethyl acetate 20:1.", [11])
add_unresolved(r, "The 4f paragraph does not independently repeat ZnBr2, Pd catalyst, DMF, atmosphere, stage times, or workup; these remain tied to the explicit 'prepared similarly' cross-reference.")
records.append(r)

r = get("eq3_2b_nbutylzinc_to_5a", [11])
r["outcomes"] = [o for o in r["outcomes"] if o["name"] != "yield"]
set_amounts(r, "znbr2", [11], [("mass", quantity(150, "mg")), ("amount", quantity(0.66, "mmol")), ("THF_solution_volume", quantity(2, "mL"))])
set_amounts(r, "nbuli", [11], [("volume", quantity(0.3, "mL")), ("concentration", quantity(1.6, "M")), ("amount", quantity(0.48, "mmol"))])
set_amounts(r, "substrate_2b", [11], [("mass", quantity(46, "mg")), ("amount", quantity(0.15, "mmol"))])
set_amounts(r, "pd_catalyst", [11], [("mass", quantity(9, "mg")), ("amount", quantity(0.008, "mmol"))])
set_amounts(r, "solvent", [11], [("substrate_catalyst_THF_volume", quantity(2, "mL"))])
set_amounts(r, "product_5a", [11], [("isolated_mass", quantity(31, "mg"))])
set_steps(r, [
    ("organozinc_formation", ["znbr2", "nbuli", "nbuznbr", "solvent"], [("addition_temperature", quantity(-78, "°C")), ("atmosphere", "Ar"), ("warm_to", quantity(25, "°C"))], [11]),
    ("coupling_setup", ["substrate_2b", "pd_catalyst", "solvent"], [("temperature", quantity(-78, "°C"))], [11]),
    ("coupling", ["nbuznbr", "substrate_2b", "pd_catalyst", "solvent", "product_5a"], [("transfer", "quick cannula transfer under Ar"), ("temperature_program", "warmed slowly from -78 °C to rt"), ("time", quantity(10, "h")), ("monitoring", "TLC")], [11]),
])
put_outcome(r, "equation_3_yield", quantity(87, "%"), [4, 5])
put_outcome(r, "experimental_section_yield", quantity(82, "%"), [11])
put_outcome(r, "yield_measurement_basis", "isolated after flash chromatography for the 82% experimental-section value", [11])
add_note(r, "Quenched with 0.5 M aqueous HCl, extracted with ethyl ether (3 x 15 mL), dried over anhydrous MgSO4, evaporated, and purified by flash chromatography with petroleum ether/ethyl acetate 10:1.", [11])
add_unresolved(r, "Equation 3/prose reports 87%, whereas the detailed experimental section reports 31 mg (82%) for 5a; the source does not reconcile the two yields.")
records.append(r)

r = get("scheme3_2a_methylzinc_to_5b", [11, 12])
ensure_participant(r, "znbr2", "reagent", "ZnBr2", [11], amounts=[("mass", quantity(148, "mg")), ("amount", quantity(0.658, "mmol")), ("THF_solution_volume", quantity(2, "mL"))])
ensure_participant(r, "magnesium", "reagent", "magnesium", [11], amounts=[("mass", quantity(240, "mg")), ("amount", quantity(10, "mmol"))])
ensure_participant(r, "methyl_iodide", "reagent", "methyl iodide", [11], amounts=[("printed_mass", quantity(142, "mg")), ("printed_amount", quantity(10, "mmol"))])
ensure_participant(r, "methylmagnesium_iodide", "reactant", "methylmagnesium iodide solution", [11], amounts=[("solution_volume_used", quantity(1, "mL"))])
ensure_participant(r, "hmpa", "solvent", "dry HMPA", [11], amounts=[("volume", quantity(0.5, "mL"))])
set_amounts(r, "meznbr", [11], [])
set_amounts(r, "pd_catalyst", [11], [("mass", quantity(9, "mg")), ("amount", quantity(0.008, "mmol"))])
set_amounts(r, "substrate_2a", [11], [("mass", quantity(40, "mg")), ("amount", quantity(0.15, "mmol"))])
set_amounts(r, "solvent", [11], [("xylenes_volume", quantity(10, "mL")), ("substrate_catalyst_THF_volume", quantity(2, "mL")), ("printed_THF_mass_for_Grignard_preparation", quantity(144, "mg")), ("printed_THF_amount_for_Grignard_preparation", quantity(20, "mmol"))])
set_amounts(r, "product_5b", [11], [("isolated_mass", quantity(21, "mg"))])
set_steps(r, [
    ("methylmagnesium_iodide_preparation", ["magnesium", "methyl_iodide", "methylmagnesium_iodide", "solvent"], [("source_cross_reference", "prepared according to reported procedure 12")], [11]),
    ("organozinc_formation", ["znbr2", "methylmagnesium_iodide", "meznbr", "solvent"], [("temperature", "rt"), ("atmosphere", "Ar"), ("time", quantity(1, "h"))], [11]),
    ("transfer_to_substrate", ["meznbr", "substrate_2a", "pd_catalyst", "solvent"], [("transfer", "cannula"), ("temperature", quantity(-78, "°C")), ("atmosphere", "Ar")], [11]),
    ("pre_HMPA_stage", ["meznbr", "substrate_2a", "pd_catalyst", "solvent"], [("temperature", "rt"), ("time", quantity(1, "h")), ("observation", "no reaction observed; mixture heterogeneous")], [11]),
    ("post_HMPA_stage", ["meznbr", "substrate_2a", "pd_catalyst", "solvent", "hmpa", "product_5b"], [("temperature", "rt"), ("time", "complete within 10 h"), ("observation", "became homogeneous"), ("monitoring", "TLC")], [11]),
])
put_outcome(r, "yield", quantity(92, "%"), [5, 6, 11])
put_outcome(r, "yield_measurement_basis", "isolated after flash chromatography", [11])
put_outcome(r, "pre_HMPA_result", "no reaction observed after 1 h at rt; heterogeneous mixture", [11])
put_outcome(r, "physical_form", "yellow oil", [11])
add_note(r, "Quenched with 0.5 M aqueous HCl, extracted with ethyl ether (3 x 15 mL), dried over anhydrous MgSO4, evaporated, and purified by flash chromatography with petroleum ether/ethyl acetate 10:1.", [11])
add_note(r, "Page 12 completes the mass-spectrum paragraph and states that the spectral data matched reference 10d; it does not report another experiment.", [12])
add_unresolved(r,
    "The printed methyl iodide values (142 mg, 10 mmol) and printed THF values (144 mg, 20 mmol) are internally inconsistent with their formulas; they are preserved verbatim and require source review.",
    "Page 5 prose and the experimental section identify product 5b, whereas Scheme 3 on page 6 prints 3a below the product structure.",
    "The locally cited procedure 12 is not supplied as SI and its missing preparation details were not inferred.")
records.append(r)


coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 7,
            "state": "attempted",
            "regions": [
                {"region": "upper page, completion of 2a and preparation of 2b", "finding": "Visually checked the end of the 2a characterization and the explicit 'prepared similarly' 2b charges, isolated mass, 90% yield, physical form and melting point.", "evidence_ids": evidence([7])},
                {"region": "middle page, bromolactonization procedures for 2c and 2d", "finding": "Visually checked the full 2c procedure and the similar 2d preparation, including charges, 25 °C/6 h, workup linkage, isolated masses and yields.", "evidence_ids": evidence([7])},
                {"region": "lower page, typical Sonogashira preparation of 3a", "finding": "Visually checked all charges, Ar atmosphere, 20 °C/4 h, workup, flash eluent, isolated mass and 99% yield; retained the 4 h versus Table 1 3 h discrepancy.", "evidence_ids": evidence([7])},
            ],
            "record_ids": [f"{DOC}:scheme2_iodolactonization_1a_to_2a", f"{DOC}:scheme2_iodolactonization_1b_to_2b", f"{DOC}:scheme2_bromolactonization_1a_to_2c", f"{DOC}:scheme2_bromolactonization_1b_to_2d", f"{DOC}:table1_entry_01"],
            "unresolved": ["The 2b and 2d paragraphs rely on 'prepared similarly' rather than independently repeating every solvent/workup detail.", "No SI file is supplied or associated."],
        },
        {
            "page": 8,
            "state": "attempted",
            "regions": [
                {"region": "top page, completion of 3a characterization and similarity statement", "finding": "Visually checked the continuation of 3a and the statement that 3b-3h were prepared similarly using Table 1 conditions; no duplicate experiment was created.", "evidence_ids": evidence([8])},
                {"region": "body, product paragraphs 3b-3f", "finding": "Visually checked row-specific substrate/alkyne charges, isolated masses, yields, physical forms and stated chromatography eluents for 3b-3f; these enrich existing Table 1 records.", "evidence_ids": evidence([8])},
            ],
            "record_ids": [f"{DOC}:table1_entry_01", *[f"{DOC}:table1_entry_{i:02d}" for i in range(3, 8)]],
            "unresolved": ["The 3b-3f paragraphs do not independently repeat every catalyst/base/solvent charge or workup step.", "The detailed 3d alkyne charge differs from the standard Table 1 ratio."],
        },
        {
            "page": 9,
            "state": "attempted",
            "regions": [
                {"region": "upper page, 3f continuation and preparations of 3g/3h", "finding": "Visually checked the 3f characterization continuation and row-specific 3g/3h charges, isolated masses, yields, forms and eluents.", "evidence_ids": evidence([9])},
                {"region": "middle-lower page, arylzinc typical procedure for 4a", "finding": "Visually checked phenyl iodide lithiation, ZnBr2 transmetalation, Pd coupling, workup and the printed 60 mg/93% result; retained the conflicts with Table 2 substrate and time.", "evidence_ids": evidence([9])},
                {"region": "bottom page, similar preparation of 4b", "finding": "Visually checked the 2b and 4-iodotoluene charges, 33.9 mg/83% outcome and eluent; the characterization continues onto page 10.", "evidence_ids": evidence([9])},
            ],
            "record_ids": [f"{DOC}:table1_entry_07", f"{DOC}:table1_entry_08", f"{DOC}:table1_entry_09", f"{DOC}:table2_entry_01", f"{DOC}:table2_entry_02"],
            "unresolved": ["The detailed 4a procedure says 2a/4 h and names the n-butyl product, whereas Table 2 prints 2b/2 h; the reported mass also remains source-internally questionable."],
        },
        {
            "page": 10,
            "state": "attempted",
            "regions": [
                {"region": "top page, 4b continuation and similar 4c preparation", "finding": "Visually checked the end of 4b characterization and the 2a/1-iodonaphthalene charges, 28 mg/70% outcome and eluent for 4c.", "evidence_ids": evidence([10])},
                {"region": "middle page, full (E)-hexenylzinc/2b preparation of 4d", "finding": "Visually checked all lithiation, transmetalation, DMF, Pd-coupling, workup and isolation details; retained the printed 60 mg/77% internal inconsistency.", "evidence_ids": evidence([10])},
                {"region": "lower page, full vinylzinc/2a preparation of 4e", "finding": "Visually checked reagent preparation, DMF, 25 °C stages, Ar, workup, 22.9 mg/92% result and the detailed 10 h versus Table 2 10 min discrepancy.", "evidence_ids": evidence([10])},
            ],
            "record_ids": [f"{DOC}:table2_entry_02", f"{DOC}:table2_entry_03", f"{DOC}:table2_entry_04", f"{DOC}:table2_entry_06"],
            "unresolved": ["The printed 4d mass/yield pair is internally inconsistent with the stated scale/formula.", "Table 2 and the detailed 4e procedure disagree on 10 min versus 10 h."],
        },
        {
            "page": 11,
            "state": "attempted",
            "regions": [
                {"region": "upper page, similar vinylzinc preparation of 4f", "finding": "Visually checked 2b/vinylmagnesium bromide charges, 25.6 mg/82% isolation and eluent; non-repeated conditions remain tied to the 4e cross-reference.", "evidence_ids": evidence([11])},
                {"region": "middle page, full n-butylzinc coupling preparation of 5a", "finding": "Visually checked organozinc generation, addition order, temperature program, 10 h, workup and 31 mg/82% isolation; retained the 82% versus Equation (3) 87% discrepancy.", "evidence_ids": evidence([11])},
                {"region": "lower page, full methylzinc coupling preparation of 5b", "finding": "Visually checked precursor charges, Ar transfers, the explicit 1 h no-reaction/heterogeneous stage, HMPA-enabled completion, workup and 21 mg/92% isolation.", "evidence_ids": evidence([11])},
            ],
            "record_ids": [f"{DOC}:table2_entry_07", f"{DOC}:eq3_2b_nbutylzinc_to_5a", f"{DOC}:scheme3_2a_methylzinc_to_5b"],
            "unresolved": ["The 5a yields differ between Equation (3) and the experimental section.", "The printed methyl iodide and THF mass/mmol pairs in the 5b precursor paragraph are internally inconsistent and were not corrected."],
        },
        {
            "page": 12,
            "state": "attempted",
            "regions": [
                {"region": "top line, completion of 5b characterization", "finding": "Visually checked the final mass-spectrum values and the statement that 5b spectral data matched reference 10d; this is continuation of the page-11 experiment, not a new run.", "evidence_ids": evidence([12])},
                {"region": "remaining page, references 1-14", "finding": "Visually checked that the remainder is bibliography only; cited literature was not converted into current-paper experimental records.", "evidence_ids": evidence([12])},
            ],
            "record_ids": [f"{DOC}:scheme3_2a_methylzinc_to_5b"],
            "unresolved": ["Reference 12 is cited for methylmagnesium iodide preparation, but no associated SI or referenced full procedure is supplied in this pilot."],
        },
    ],
}


RAW.parent.mkdir(parents=True, exist_ok=True)
COVERAGE.parent.mkdir(parents=True, exist_ok=True)
RAW.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
COVERAGE.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

tasks = json.loads(TASKS.read_text())
target_ids = {f"{DOC}:page{page}:text" for page in range(7, 13)}
for task in tasks:
    if task["task_id"] in target_ids:
        task["state"] = "attempted"
        task["reason"] = "Original page image visually inspected; enriched records and unresolved findings are linked in pages_0007_0012 coverage ledger."
TASKS.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"records": len(records), "coverage_pages": [p["page"] for p in coverage["pages"]]}, ensure_ascii=False))
