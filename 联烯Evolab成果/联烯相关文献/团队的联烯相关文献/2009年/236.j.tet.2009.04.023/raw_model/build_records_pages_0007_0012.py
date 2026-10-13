import copy
import json
from pathlib import Path


DOC = "doc_34a38cb1c5b4d3e7"
BASE = Path(__file__).resolve().parents[1]
DATA = json.loads((BASE / "dataset.json").read_text())
EXISTING = {record["record_id"]: record for record in DATA["experiments"]}


def rid(suffix):
    return f"{DOC}:{suffix}"


def ev(*pages):
    result = []
    for page in pages:
        result.extend([f"{DOC}:page{page}:text", f"{DOC}:page{page}:image"])
    return result


def q(number, unit, **extra):
    value = {"number": number, "unit": unit}
    value.update(extra)
    return value


def fact(value, pages):
    return {
        "value": value,
        "evidence_ids": ev(*pages) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def field(name, value, pages, targets=None):
    item = {"name": name, "fact": fact(value, pages)}
    if targets:
        item["target_entity_ids"] = targets
    return item


def participant(entity_id, role, label, pages, amounts=None, name=None, smiles=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, pages),
        "name": fact(name, pages),
        "smiles": fact(smiles, pages),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": amounts or [],
    }


def amount(name, value, pages):
    return field(name, value, pages)


def get_record(suffix, *pages):
    record = copy.deepcopy(EXISTING[rid(suffix)])
    for evidence_id in ev(*pages):
        if evidence_id not in record["evidence_ids"]:
            record["evidence_ids"].append(evidence_id)
    record["status"] = "candidate"
    record["completeness"] = "partial"
    record["review"] = {
        "method": "none",
        "reviewer": None,
        "checked_fields": [],
        "unresolved": [],
    }
    return record


def find_participant(record, entity_id):
    return next(p for p in record["participants"] if p["entity_id"] == entity_id)


def set_amounts(record, entity_id, values, pages):
    find_participant(record, entity_id)["amounts"] = [amount(name, value, pages) for name, value in values]


def set_name(record, entity_id, value, pages):
    find_participant(record, entity_id)["name"] = fact(value, pages)


def upsert_outcome(record, name, value, pages, targets=None):
    record["outcomes"] = [item for item in record["outcomes"] if item["name"] != name]
    record["outcomes"].append(field(name, value, pages, targets))


def upsert_condition(record, name, value, pages, step_id="reaction"):
    step = next(step for step in record["steps"] if step["step_id"] == step_id)
    step["conditions"] = [item for item in step["conditions"] if item["name"] != name]
    step["conditions"].append(field(name, value, pages))


def add_note(record, value, pages):
    if not any(note["value"] == value for note in record["notes"]):
        record["notes"].append(fact(value, pages))


def set_review(record, *items):
    record["review"]["unresolved"] = list(items)


records = []

# Detailed preparations for Table 2 scope rows. These paragraphs describe the
# same labeled table experiments and enrich the existing IDs rather than create
# duplicates. Entry 2 starts on page 6 and only its outcome continues on page 7.
scope = [
    # suffix, pages, substrate, substrate mass/mmol, PhSeCl mass/mmol,
    # water/MeCN volumes, product, product name, product mass, optional byproduct data, ratio
    ("table2_entry2_2b", (7,), "1b", None, None, None, "E-2b",
     "3-Hydroxy-2-phenylselanyl-1(E)-butenyl diphenyl phosphine oxide", 106.3, None, None),
    ("table2_entry3_2c", (7,), "1c", (94.9, 0.30), (87.1, 0.45), (0.3, 6.0), "E-2c",
     "3-Hydroxy-3-phenyl-2-phenylselanyl-1(E)-propenyl diphenyl phosphine oxide", 125.5, None, None),
    ("table2_entry4_2d", (7,), "1d", (81.0, 0.30), (86.4, 0.45), (0.3, 6.0), "E-2d",
     "3-Hydroxy-3-methyl-2-phenylselanyl-1(E)-butenyl diphenyl phosphine oxide", 118.6, None, None),
    ("table2_entry5_2e", (7,), "1e", (97.3, 0.30), (85.5, 0.45), (0.3, 6.0), "E-2e",
     "3-Hydroxy-2-phenylselanyl-3-propyl-1(E)-hexenyl diphenyl phosphine oxide", 119.7, None, None),
    ("table2_entry6_2f", (7,), "1f", (93.3, 0.30), (87.5, 0.45), (0.3, 6.0), "E-2f",
     "3-Hydroxy-3,3-pentamethylene-2-phenylselanyl-1(E)-propenyl diphenyl phosphine oxide", 122.9, None, None),
    ("table2_entry7_2g", (7,), "1g", (88.9, 0.30), (86.6, 0.45), (0.3, 6.0), "E-2g",
     "1-Hydroxy-2-phenylselanyl-2(E)-hepten-3-yl diphenyl phosphine oxide", 94.6, None, None),
    ("table2_entry8_2h", (7,), "1h", (95.3, 0.30), (88.6, 0.45), (0.3, 6.0), "E-2h",
     "3-Hydroxy-1-phenyl-2-phenylselanyl-1(E)-propenyl diphenyl phosphine oxide", 117.9, None, None),
    ("table2_entry9_2i", (7, 8), "1i", (90.3, 0.30), (87.1, 0.45), (0.3, 6.0), "E-2i",
     "5-Hydroxy-4-phenylselanyl-3(E)-hexen-3-yl diphenyl phosphine oxide", 130.6, None, None),
    ("table2_entry10_2j", (8,), "1j", (103.7, 0.30), (87.8, 0.45), (0.3, 6.0), "E-2j",
     "3-Hydroxy-1-phenyl-2-phenylselanyl-1(E)-pentenyl diphenyl phosphine oxide", 137.8, None, None),
    ("table2_entry11_2k", (8,), "1k", (95.5, 0.30), (86.2, 0.45), (0.3, 6.0), "E-2k",
     "2-Hydroxy-2-methyl-3-phenylselanyl-3(E)-octen-4-yl diphenyl phosphine oxide", 94.7, None, None),
    ("table2_entry12_2l", (8,), "1l", (422.6, 1.5), (431.8, 2.25), (1.0, 20.0), "E-2l",
     "3-Hydroxy-4-methyl-2-phenylselanyl-1(E)-pentenyl diphenyl phosphine oxide", 525.5,
     ("Z-3l", "3-Chloro-4-methyl-2-phenylselanyl-1(Z)-pentenyl diphenyl phosphine oxide", 52.1, 7), "92:8"),
    ("table2_entry13_2m", (8,), "1m", (71.8, 0.30), (86.6, 0.45), (0.3, 6.0), "E-2m",
     "3-Hydroxy-2-phenylselanyl-1(E)-propenyl diphenyl phosphine oxide", 15.7,
     ("Z-3m", "3-Chloro-2-phenylselanyl-1(Z)-propenyl diphenyl phosphine oxide", 79.4, 61.5), "17.5:82.5"),
    ("table2_entry14_2n", (9,), "1n", (321.0, 1.2), (345.3, 1.8), (0.9, 18.0), "E-2n",
     "3-Hydroxy-2-phenylselanyl-1(E)-pentenyl diphenyl phosphine oxide", 436.1,
     ("Z-3n", "3-Chloro-2-phenylselanyl-1(Z)-pentenyl diphenyl phosphine oxide", 33.9, 6), "93:7"),
    ("table2_entry15_2o", (9,), "1o", (649.3, 2.0), (575.4, 3.0), (1.5, 30.0), "E-2o",
     "3-Hydroxy-2-phenylselanyl-1(E)-nonenyl diphenyl phosphine oxide", 642.2,
     ("Z-3o", "3-Chloro-2-phenylselanyl-1(Z)-nonenyl diphenyl phosphine oxide", 61.2, 6), "91:9"),
    ("table2_entry16_2p", (9,), "1p", (200.2, 0.60), (172.2, 0.90), (0.6, 12.0), "E-2p",
     "3-Hydroxy-4-phenyl-2-phenylselanyl-1(E)-butenyl diphenyl phosphine oxide", 196.4,
     ("Z-3p", "3-Chloro-4-phenyl-2-phenylselanyl-1(Z)-butenyl diphenyl phosphine oxide", 43.5, 14), "82:18"),
]

for suffix, pages, substrate, sub_data, ph_data, solvent_data, product, product_name, product_mass, bp_data, ratio in scope:
    record = get_record(suffix, *pages)
    if sub_data:
        set_amounts(record, substrate, [("mass", q(sub_data[0], "mg")), ("amount", q(sub_data[1], "mmol"))], pages)
        set_amounts(record, "phsecl", [("mass", q(ph_data[0], "mg")), ("amount", q(ph_data[1], "mmol")),
                                        ("equivalents", q(1.5, "equiv"))], pages)
        set_amounts(record, "water", [("volume", q(solvent_data[0], "mL"))], pages)
        set_amounts(record, "mecn", [("volume", q(solvent_data[1], "mL"))], pages)
    set_name(record, product, product_name, pages)
    upsert_outcome(record, "isolated_product_mass", q(product_mass, "mg"), pages, [product])
    if bp_data:
        bp, bp_name, bp_mass, bp_yield = bp_data
        set_name(record, bp, bp_name, pages)
        upsert_outcome(record, "isolated_byproduct_mass", q(bp_mass, "mg"), pages, [bp])
        upsert_outcome(record, f"isolated_yield_{bp}", q(bp_yield, "%"), pages, [bp])
        upsert_outcome(record, f"{product}_to_{bp}_ratio", ratio, pages, [product, bp])
    if suffix == "table2_entry12_2l":
        upsert_condition(record, "purification", "flash chromatography on silica gel; CH2Cl2/ethyl acetate 40:1 to 3:1", pages)
    add_note(record, "Analytical characterization supports the reported product identity but was not converted into a separate reaction record.", pages)
    set_review(
        record,
        "Allene substrate and selenium-containing product structures remain unverified; label/name evidence is retained and SMILES remain null.",
        "Atmosphere is not reported; abbreviated preparations do not restate every General Procedure III workup operation.",
    )
    records.append(record)

# Scheme 1 detailed stages, spanning pages 9-10.
pages = (9, 10)
record = get_record("scheme1_tosylation_E-2o_to_E-4o", *pages)
set_amounts(record, "E-2o", [("mass", q(152.7, "mg")), ("amount", q(0.31, "mmol"))], pages)
set_amounts(record, "tscl", [("mass", q(235.0, "mg")), ("amount", q(1.24, "mmol"))], pages)
set_amounts(record, "dmap", [("mass", q(225.5, "mg")), ("amount", q(1.86, "mmol"))], pages)
set_amounts(record, "ch2cl2", [("volume", q(2.0, "mL"))], pages)
set_name(record, "E-4o", "3-Tosyloxy-2-phenylselanyl-1(E)-nonenyl diphenyl phosphine oxide", pages)
upsert_condition(record, "time", q(2.5, "h"), pages)
upsert_condition(record, "temperature", q(50, "°C"), pages)
upsert_condition(record, "atmosphere", "N2", pages)
upsert_condition(record, "heating_mode", "reflux", pages)
upsert_condition(record, "operation", "DMAP solution added dropwise; solvent evaporated after reaction", pages)
upsert_condition(record, "purification", "flash chromatography on silica gel; petroleum ether/ethyl acetate 3:1 to 2:1", pages)
upsert_outcome(record, "isolated_product_mass", q(172.2, "mg"), pages, ["E-4o"])
add_note(record, "The 2.0 mL CH2Cl2 total comprises separate 1.0 mL substrate/TsCl and 1.0 mL DMAP solutions.", pages)
set_review(record, "Reactant and product structures remain unverified.", "Dropwise-addition duration is not reported.")
records.append(record)

pages = (10,)
record = get_record("scheme1_chlorination_E-4o_to_E-3o", *pages)
set_amounts(record, "E-4o", [("mass", q(80.4, "mg")), ("amount", q(0.15, "mmol"))], pages)
set_amounts(record, "licl", [("mass", q(53.7, "mg")), ("amount", q(1.20, "mmol"))], pages)
set_amounts(record, "dmf", [("volume", q(1.5, "mL"))], pages)
set_name(record, "E-3o", "3-Chloro-2-phenylselanyl-1(E)-nonenyl diphenyl phosphine oxide", pages)
upsert_condition(record, "time", q(29, "h"), pages)
upsert_condition(record, "temperature", q(50, "°C"), pages)
upsert_condition(record, "atmosphere", "N2", pages)
upsert_condition(record, "workup", "quenched with 5 mL water; extracted with 20 mL x 3 Et2O; washed with 5 mL water, 5 mL 5% aqueous HCl, and 5 mL saturated brine; dried over Na2SO4; filtered and evaporated", pages)
upsert_condition(record, "purification", "silica-gel chromatography; petroleum ether/ethyl acetate 3:1", pages)
upsert_outcome(record, "isolated_product_mass", q(38.1, "mg"), pages, ["E-3o"])
set_review(record, "Reactant and product structures remain unverified.")
records.append(record)

# Detailed isotope-labeling experiments. The 1h batch includes explicit staged
# preparation; 1c and 1e are stated to follow that procedure but only their
# restated batch values are structured here.
record = get_record("scheme3_1h_to_E-2h*", 10, 11)
record["participants"] = [
    participant("1h", "reactant", "1h", (10,), [amount("mass", q(95.1, "mg"), (10,)), amount("amount", q(0.30, "mmol"), (10,))]),
    participant("phsecl", "reagent", "PhSeCl", (10,), [amount("mass", q(87.1, "mg"), (10,)), amount("amount", q(0.45, "mmol"), (10,)), amount("equivalents", q(1.5, "equiv"), (10,))], smiles="Cl[Se]c1ccccc1"),
    participant("anhyd_mecn", "solvent", "anhydrous CH3CN", (10,), [amount("volume", q(6.0, "mL"), (10,))], smiles="CC#N"),
    participant("h218o", "solvent", "H2-18O (96%)", (10,), [amount("volume", q(0.3, "mL"), (10,))]),
    participant("p2o5", "reagent", "P2O5", (10,)),
    participant("cah2", "reagent", "CaH2", (10,)),
    participant("molecular_sieves", "reagent", "molecular sieves", (10,)),
    participant("E-2h*", "product", "E-2h*", (10, 11), name="18O-labeled 3-hydroxy-1-phenyl-2-phenylselanyl-1(E)-propenyl diphenyl phosphine oxide"),
]
record["steps"] = [
    {"step_id": "material_and_solvent_drying", "participant_ids": ["1h", "anhyd_mecn", "p2o5", "cah2", "molecular_sieves"], "conditions": [
        field("starting_material_drying_time", q(1, "d"), (10,)),
        field("first_solvent_reflux_time", q(24, "h"), (10,)),
        field("first_solvent_drying_agent", "CaH2 under argon", (10,)),
        field("second_solvent_reflux_time", q(24, "h"), (10,)),
        field("second_solvent_drying_agent", "P2O5 under argon", (10,)),
        field("storage", "distilled MeCN stored over molecular sieves in a nitrogen glove box", (10,)),
    ]},
    {"step_id": "pre_stir_phsecl_solution", "participant_ids": ["phsecl", "anhyd_mecn", "h218o"], "conditions": [
        field("temperature", "r.t.", (10,)), field("time", q(262, "min"), (10,)),
        field("solution_composition", "PhSeCl in 2.0 mL anhydrous CH3CN and 0.1 mL H2-18O", (10,)),
    ]},
    {"step_id": "pre_stir_substrate_solution", "participant_ids": ["1h", "anhyd_mecn", "h218o"], "conditions": [
        field("temperature", "r.t.", (10,)), field("time", q(259, "min"), (10,)),
        field("solution_composition", "1h in 2.0 mL anhydrous CH3CN and 0.2 mL H2-18O", (10,)),
    ]},
    {"step_id": "reaction", "participant_ids": ["1h", "phsecl", "anhyd_mecn", "h218o", "E-2h*"], "conditions": [
        field("temperature", "r.t.", (10,)), field("reaction_time_after_combination", q(10, "min"), (10,)),
        field("scheme3_reported_time", q(45, "min"), (5,)), field("atmosphere", "nitrogen glove box", (10,)),
        field("solvent", "CH3CN/H2-18O = 20/1", (5, 10)),
        field("transfer_wash", "anhydrous CH3CN, 1.0 mL x 2", (10,)),
    ]},
    {"step_id": "purification", "participant_ids": ["E-2h*"], "conditions": [
        field("purification", "direct flash chromatography on silica gel; petroleum ether/ethyl acetate 2:1", (10,)),
    ]},
]
upsert_outcome(record, "isolated_product_mass", q(124.8, "mg"), (10,), ["E-2h*"])
upsert_outcome(record, "isolated_yield_E-2h*", q(84, "%"), (10,), ["E-2h*"])
upsert_outcome(record, "oxygen_18_incorporation", q(94.5, "%"), (10, 11), ["E-2h*"])
upsert_outcome(record, "yield_measurement_basis", "isolated yield", (10,))
add_note(record, "The Scheme 3 arrow gives 45 min, whereas section 4.3.18 gives 10 min after combination plus separate 262 and 259 min pre-stirs; these stage-specific times are preserved rather than summed.", (5, 10))
set_review(record, "The discrepancy between the Scheme 3 arrow time and the detailed post-combination reaction time is unresolved.", "The labeled product structure remains unverified.")
records.append(record)

isotopes = [
    ("scheme3_1c_to_E-2c*", "1c", 94.8, 87.2, 37, "E-2c*", "18O-labeled 3-hydroxy-3-phenyl-2-phenylselanyl-1(E)-propenyl diphenyl phosphine oxide", 126.0, 85, 88.4),
    ("scheme3_1e_to_E-2e*", "1e", 97.2, 85.9, 41, "E-2e*", "18O-labeled 3-hydroxy-2-phenylselanyl-3-propyl-1(E)-hexenyl diphenyl phosphine oxide", 127.7, 85, 69.5),
]
for suffix, substrate, sub_mass, ph_mass, minutes, product, name, product_mass, yld, incorporation in isotopes:
    record = get_record(suffix, 11)
    record["participants"] = [
        participant(substrate, "reactant", substrate, (11,), [amount("mass", q(sub_mass, "mg"), (11,)), amount("amount", q(0.30, "mmol"), (11,))]),
        participant("phsecl", "reagent", "PhSeCl", (11,), [amount("mass", q(ph_mass, "mg"), (11,)), amount("amount", q(0.45, "mmol"), (11,)), amount("equivalents", q(1.5, "equiv"), (5,))], smiles="Cl[Se]c1ccccc1"),
        participant("anhyd_mecn", "solvent", "anhydrous CH3CN", (11,), [amount("volume", q(6.0, "mL"), (11,))], smiles="CC#N"),
        participant("h218o", "solvent", "H2-18O", (11,), [amount("volume", q(0.3, "mL"), (11,))]),
        participant(product, "product", product, (11,), name=name),
    ]
    record["steps"] = [{"step_id": "reaction", "participant_ids": [p["entity_id"] for p in record["participants"]], "conditions": [
        field("temperature", "r.t.", (5,)), field("time", q(minutes, "min"), (11,)),
        field("solvent", "anhydrous CH3CN/H2-18O = 20/1", (5, 11)),
        field("procedure_reference", "prepared according to the section 4.3.18 isotope-labeling procedure", (11,)),
    ]}]
    upsert_outcome(record, f"isolated_yield_{product}", q(yld, "%"), (11,), [product])
    upsert_outcome(record, "isolated_product_mass", q(product_mass, "mg"), (11,), [product])
    upsert_outcome(record, "oxygen_18_incorporation", q(incorporation, "%"), (11,), [product])
    upsert_outcome(record, "yield_measurement_basis", "isolated yield", (11,))
    set_review(record, "The abbreviated paragraph invokes section 4.3.18 but does not restate its drying, pre-stir, workup, or purification details.", "The labeled product structure remains unverified.")
    records.append(record)

# Table 3 entry 6/Table 4 entry 1, now enriched by Typical Procedure IV.
record = get_record("table3_entry6_table4_entry1", 12)
record["participants"] = [
    participant("1l", "reactant", "1l", (12,), [amount("mass", q(57.3, "mg"), (12,)), amount("amount", q(0.30, "mmol"), (12,))]),
    participant("phsecl", "reagent", "PhSeCl", (3, 12), [amount("mass", q(55.6, "mg"), (12,)), amount("amount", q(0.20, "mmol"), (12,)), amount("equivalents", q(1.5, "equiv"), (3,))], smiles="Cl[Se]c1ccccc1"),
    participant("mecn", "solvent", "MeCN", (12,), [amount("volume", q(3.0, "mL"), (12,))], smiles="CC#N"),
    participant("water", "solvent", "H2O", (12,), [amount("volume", q(1.5, "mL"), (12,))], smiles="O"),
    participant("E-2l", "product", "E-2l", (12,), name="3-Hydroxy-4-methyl-2-phenylselanyl-1(E)-pentenyl diphenyl phosphine oxide"),
    participant("Z-3l", "product", "Z-3l", (12,), name="3-Chloro-4-methyl-2-phenylselanyl-1(Z)-pentenyl diphenyl phosphine oxide"),
]
record["steps"] = [{"step_id": "reaction", "participant_ids": [p["entity_id"] for p in record["participants"]], "conditions": [
    field("temperature", q(70, "°C"), (3, 12)), field("time", q(34, "min"), (3, 12)),
    field("solvent", "MeCN/H2O = 2/1", (3, 12)),
    field("workup", "quenched with 5 mL H2O; extracted with 20 mL x 3 diethyl ether; washed with 5 mL brine; dried over Na2SO4; filtered and evaporated", (12,)),
    field("purification", "flash chromatography on silica gel; CH2Cl2/ethyl acetate 10:1 then 5:1", (12,)),
]}]
record["notes"] = [note for note in record["notes"] if not str(note.get("value", "")).startswith("The printed detailed paragraph pairs")]
upsert_outcome(record, "isolated_yield_E-2l", q(82, "%"), (12,), ["E-2l"])
upsert_outcome(record, "isolated_product_mass", q(73.8, "mg"), (12,), ["E-2l"])
upsert_outcome(record, "isolated_yield_measurement_basis", "isolated yield", (12,))
upsert_outcome(record, "E-2l_to_Z-3l_ratio", "97:3", (12,), ["E-2l", "Z-3l"])
upsert_outcome(record, "ratio_measurement_basis", "1H NMR analysis of crude product", (12,))
add_note(record, "The printed detailed paragraph's mass/mmol assignments conflict with the table-level PhSeCl loading; all source values are preserved without correction.", (3, 12))
set_review(record, "The printed mass/mmol assignments conflict with molecular-weight expectations and the table-level 1.5-equivalent statement; source values require chemistry review.", "Substrate and product structures remain unverified.")
records.append(record)

# Table 4 entries 2-5 detailed batches.
table4 = [
    ("table4_entry2_2m", "1m", 72.5, 86.4, 3.0, 3.0, "E-2m", 65.6, "Z-3m", 17.8, 14),
    ("table4_entry3_2n", "1n", 81.1, 86.8, 1.5, 3.0, "E-2n", 104.6, "Z-3n", None, None),
    ("table4_entry4_2o", "1o", 96.8, 85.5, 1.5, 3.0, "E-2o", 110.6, "Z-3o", None, None),
    ("table4_entry5_2p", "1p", 101.0, 87.4, 2.3, 2.3, "E-2p", 118.1, "Z-3p", None, None),
]
for suffix, substrate, sub_mass, ph_mass, water_volume, mecn_volume, product, product_mass, bp, bp_mass, bp_yield in table4:
    record = get_record(suffix, 12)
    set_amounts(record, substrate, [("mass", q(sub_mass, "mg")), ("amount", q(0.30, "mmol"))], (12,))
    set_amounts(record, "phsecl", [("mass", q(ph_mass, "mg")), ("amount", q(0.45, "mmol")), ("equivalents", q(1.5, "equiv"))], (12,))
    record["participants"] = [p for p in record["participants"] if p["entity_id"] not in {"solvent", "mecn", "water"}]
    record["participants"].insert(2, participant("mecn", "solvent", "MeCN", (12,), [amount("volume", q(mecn_volume, "mL"), (12,))], smiles="CC#N"))
    record["participants"].insert(3, participant("water", "solvent", "H2O", (12,), [amount("volume", q(water_volume, "mL"), (12,))], smiles="O"))
    record["steps"][0]["participant_ids"] = [p["entity_id"] for p in record["participants"]]
    upsert_outcome(record, "isolated_product_mass", q(product_mass, "mg"), (12,), [product])
    if bp_mass is not None:
        upsert_outcome(record, "isolated_byproduct_mass", q(bp_mass, "mg"), (12,), [bp])
        upsert_outcome(record, f"isolated_yield_{bp}", q(bp_yield, "%"), (12,), [bp])
    upsert_outcome(record, "yield_measurement_basis", "isolated yield", (3, 12))
    set_review(record, "Workup, purification, and atmosphere are not restated in sections 4.4.2-4.4.5.", "Substrate and product structures remain unverified.")
    records.append(record)

# Optically active selenohydroxylations: Scheme 2 and sections 4.5.1-4.5.3
# are reconciled into the same three records.
chiral = [
    ("scheme2_S-1b_to_S-E-2b", "S-1b", 76.2, 99, 86.7, 0.3, 6.0, "S-E-2b", 110.5, 86, 99, "r.t.", 12,
     "S-3-Hydroxy-2-phenylselanyl-1(E)-butenyl diphenyl phosphine oxide"),
    ("scheme2_S-1j_to_S-E-2j", "S-1j", 103.8, 99, 88.5, 0.3, 6.0, "S-E-2j", 146.8, 94, 99, "r.t.", 8,
     "S-3-Hydroxy-1-phenyl-2-phenylselanyl-1(E)-pentenyl diphenyl phosphine oxide"),
    ("scheme2_R-1o_to_R-E-2o", "R-1o", 97.6, 97, 86.9, 1.5, 3.0, "R-E-2o", 118.2, 79, 97, q(70, "°C"), 30,
     "R-3-Hydroxy-2-phenylselanyl-1(E)-nonenyl diphenyl phosphine oxide"),
]
for suffix, substrate, sub_mass, sub_ee, ph_mass, water_volume, mecn_volume, product, product_mass, yld, product_ee, temp, minutes, product_name in chiral:
    record = get_record(suffix, 12)
    record["participants"] = [
        participant(substrate, "reactant", substrate, (3, 12), [amount("mass", q(sub_mass, "mg"), (12,)), amount("amount", q(0.30, "mmol"), (12,))]),
        participant("phsecl", "reagent", "PhSeCl", (3, 12), [amount("mass", q(ph_mass, "mg"), (12,)), amount("amount", q(0.45, "mmol"), (12,)), amount("equivalents", q(1.5, "equiv"), (3,))], smiles="Cl[Se]c1ccccc1"),
        participant("mecn", "solvent", "MeCN", (12,), [amount("volume", q(mecn_volume, "mL"), (12,))], smiles="CC#N"),
        participant("water", "solvent", "H2O", (12,), [amount("volume", q(water_volume, "mL"), (12,))], smiles="O"),
        participant(product, "product", product, (3, 12), name=product_name),
    ]
    ratio = "20/1" if water_volume == 0.3 else "2/1"
    record["steps"] = [{"step_id": "reaction", "participant_ids": [p["entity_id"] for p in record["participants"]], "conditions": [
        field("temperature", temp, (3, 12)), field("time", q(minutes, "min"), (3, 12)),
        field("solvent", f"CH3CN/H2O = {ratio}", (3, 12)),
    ]}]
    upsert_outcome(record, "starting_material_ee", q(sub_ee, "%"), (3, 12), [substrate])
    upsert_outcome(record, f"isolated_yield_{product}", q(yld, "%"), (3, 12), [product])
    upsert_outcome(record, "isolated_product_mass", q(product_mass, "mg"), (12,), [product])
    upsert_outcome(record, "product_ee", q(product_ee, "%"), (3, 12), [product])
    upsert_outcome(record, "yield_measurement_basis", "isolated yield", (12,))
    set_review(record, "Workup and purification are not restated in sections 4.5.1-4.5.3.", "Absolute structures and stereochemical assignments remain unverified.")
    records.append(record)

assert len(records) == 28
assert len({record["record_id"] for record in records}) == 28

out = BASE / "raw_model" / "records_pages_0007_0012.json"
out.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"updated_records": len(records), "new_record_ids": 0, "path": str(out)}, ensure_ascii=False))
