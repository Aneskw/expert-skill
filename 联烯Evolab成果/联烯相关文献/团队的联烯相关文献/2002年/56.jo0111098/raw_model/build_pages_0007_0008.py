import copy
import json
from pathlib import Path


DOC = "doc_03ca6cf38d4f5d15"
ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / "runs" / "current"
DATA = json.loads((RUN / "dataset.json").read_text())
EXISTING = {r["record_id"]: copy.deepcopy(r) for r in DATA["experiments"]}


def ev(page):
    return [f"{DOC}:page{page}:image", f"{DOC}:page{page}:text"]


def fact(value, evidence):
    return {
        "value": value,
        "evidence_ids": list(evidence) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def field(name, value, evidence, targets=None):
    result = {"name": name, "fact": fact(value, evidence)}
    if targets:
        result["target_entity_ids"] = list(targets)
    return result


def qty(number, unit, raw_text=None, **extra):
    result = {"number": number, "unit": unit}
    if raw_text:
        result["raw_text"] = raw_text
    result.update(extra)
    return result


def part(entity_id, role, label, evidence, name=None, smiles=None, amounts=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence) if name else fact(None, evidence),
        "smiles": fact(smiles, evidence) if smiles else fact(None, evidence),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": [field(n, v, evidence) for n, v in (amounts or [])],
    }


def record(suffix, evidence, participants, conditions, outcomes, *, kind="reported_experiment", notes=None, unresolved=None):
    nonproducts = [p["entity_id"] for p in participants if p["role"] != "product"]
    return {
        "record_id": f"{DOC}:{suffix}",
        "document_id": DOC,
        "source_reaction_id": suffix,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": list(dict.fromkeys(evidence)),
        "participants": participants,
        "steps": [{
            "step_id": "reaction",
            "participant_ids": nonproducts,
            "conditions": [field(n, v, evidence) for n, v in conditions],
        }],
        "outcomes": outcomes,
        "notes": [fact(n, evidence) for n in (notes or [])],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved or [
                "Supporting information was mentioned but not explicitly provided or associated.",
                "Machine extraction requires chemical source review; structures remain unverified.",
            ],
        },
    }


def get(suffix):
    return copy.deepcopy(EXISTING[f"{DOC}:{suffix}"])


def add_evidence(rec, page):
    rec["evidence_ids"] = list(dict.fromkeys(rec["evidence_ids"] + ev(page)))


def find_part(rec, entity_id):
    return next(p for p in rec["participants"] if p["entity_id"] == entity_id)


def set_amounts(rec, entity_id, page, items):
    find_part(rec, entity_id)["amounts"] = [field(n, v, ev(page)) for n, v in items]


def add_conditions(rec, page, items):
    step = rec["steps"][0]
    names = {name for name, _ in items}
    step["conditions"] = [c for c in step["conditions"] if c["name"] not in names]
    step["conditions"].extend(field(name, value, ev(page)) for name, value in items)


def add_note(rec, page, text):
    if not any(n["value"] == text for n in rec["notes"]):
        rec["notes"].append(fact(text, ev(page)))


def add_unresolved(rec, text):
    if text not in rec["review"]["unresolved"]:
        rec["review"]["unresolved"].append(text)


def append_fact_evidence(rec, field_names, page):
    wanted = set(field_names)
    for obj in rec.get("outcomes", []):
        if obj["name"] in wanted and obj["fact"]["value"] is not None:
            obj["fact"]["evidence_ids"] = list(dict.fromkeys(obj["fact"]["evidence_ids"] + ev(page)))


records = []

# Page 7: continuation of Z-2c and the abbreviated E-2c experiment.
r = get("scheme5_Z2c")
add_evidence(r, 7)
add_note(r, 7, "Page 7 continues the product characterization begun on page 6; it is not a second reaction.")
records.append(r)

r = get("scheme5_E2c")
add_evidence(r, 7)
set_amounts(r, "alkyne", 7, [("mass", qty(134, "mg")), ("amount", qty(0.87, "mmol"))])
set_amounts(r, "zinc", 7, [("mass", qty(388, "mg")), ("amount", qty(1.22, "mmol"))])
set_amounts(r, "iodide", 7, [("mass", qty(112, "mg")), ("amount", qty(0.5, "mmol"))])
set_amounts(r, "prod", 7, [("mass", qty(73, "mg"))])
append_fact_evidence(r, ["yield"], 7)
records.append(r)

# Page 7: Table 1 procedures. Row 1 supplies the full typical procedure; rows 2-5 are abbreviated.
table1_amounts = {
    1: {
        "alkyne": [("mass", qty(97, "mg")), ("amount", qty(0.85, "mmol"))],
        "nbuli": [("volume", qty(0.47, "mL")), ("concentration", qty(2.0, "M")), ("amount", qty(0.94, "mmol"))],
        "znbr2": [("mass", qty(378, "mg")), ("amount", qty(1.68, "mmol"))],
        "pd": [("mass", qty(29, "mg")), ("amount", qty(0.025, "mmol")), ("catalyst_loading", qty(5, "mol%"))],
        "arx": [("mass", qty(109, "mg")), ("amount", qty(0.5, "mmol"))],
        "thf": [("volume", qty(6, "mL", "2 mL + 3 mL + 1 mL"))],
        "prod6": [("mass", qty(88, "mg"))],
    },
    2: {
        "alkyne": [("mass", qty(190, "mg")), ("amount", qty(1.7, "mmol"))],
        "znbr2": [("mass", qty(635, "mg")), ("amount", qty(2.82, "mmol"))],
        "arx": [("mass", qty(221, "mg")), ("amount", qty(1.0, "mmol"))],
        "prod2": [("mass", qty(104, "mg"))],
    },
    3: {
        "alkyne": [("mass", qty(190, "mg")), ("amount", qty(1.7, "mmol"))],
        "znbr2": [("mass", qty(546, "mg")), ("amount", qty(2.43, "mmol"))],
        "arx": [("mass", qty(203, "mg")), ("amount", qty(1.0, "mmol"))],
        "prod2": [("mass", qty(46, "mg"))],
        "prod6": [("mass", qty(44, "mg"))],
    },
    4: {
        "alkyne": [("mass", qty(93, "mg")), ("amount", qty(0.85, "mmol"))],
        "znbr2": [("mass", qty(390, "mg")), ("amount", qty(1.73, "mmol"))],
        "arx": [("mass", qty(122, "mg")), ("amount", qty(0.48, "mmol"))],
        "prod2": [("mass", qty(47, "mg"))],
        "prod6": [("mass", qty(19, "mg"))],
    },
    5: {
        "alkyne": [("mass", qty(231, "mg")), ("amount", qty(1.5, "mmol"))],
        "znbr2": [("mass", qty(398, "mg")), ("amount", qty(1.77, "mmol"))],
        "arx": [("mass", qty(128, "mg")), ("amount", qty(0.5, "mmol"))],
        "prod2": [("mass", qty(73, "mg"))],
    },
}
for row in range(1, 6):
    r = get(f"table1_entry{row}")
    add_evidence(r, 7)
    for entity, items in table1_amounts[row].items():
        set_amounts(r, entity, 7, items)
    append_fact_evidence(r, ["yield_2", "yield_6", "product_ratio_2_to_6"], 7)
    if row == 1:
        add_conditions(r, 7, [
            ("atmosphere", "N2"),
            ("initial_lithiation_time", qty(100, "min")),
            ("time_after_ZnBr2_at_minus_78_C", qty(5, "min")),
            ("time_after_warming_to_room_temperature", qty(20, "min")),
            ("reaction_endpoint", "complete by TLC, eluent hexane"),
            ("workup", "quenched with water; extracted with diethyl ether; washed with water; dried over MgSO4; rotary evaporation"),
            ("purification", "silica gel chromatography, hexane"),
        ])
    else:
        add_note(r, 7, "The source states that this compound or product pair was synthesized similarly to the Table 1 entry 1 typical procedure; omitted quantities remain missing.")
    records.append(r)

# Page 7: enrich each Scheme 8 organozinc preparation with the shared detailed procedure.
for row in range(1, 5):
    r = get(f"scheme8_entry{row}")
    add_evidence(r, 7)
    set_amounts(r, "zn", 7, [("mass", qty(1.625, "g")), ("amount", qty(25, "mmol"))])
    set_amounts(r, "dibromoethane", 7, [("mass", qty(94, "mg")), ("amount", qty(0.5, "mmol")), ("volume", qty(0.04, "mL"))])
    set_amounts(r, "tmscl", 7, [("mass", qty(40, "mg")), ("amount", qty(0.4, "mmol")), ("volume", qty(0.05, "mL"))])
    set_amounts(r, "thf", 7, [("volume", qty(7, "mL", "3 mL + 4 mL"))])
    set_amounts(r, "halide", 7, [("amount", qty(10, "mmol"))])
    add_conditions(r, 7, [
        ("atmosphere", "N2"),
        ("zinc_activation_temperature", qty(65, "°C")),
        ("zinc_activation_time", qty(1, "min")),
        ("time_after_trimethylsilyl_chloride_at_room_temperature", qty(15, "min")),
        ("operation", "organic-halide solution added slowly, then heated to 45 °C until TLC showed completion; solution reserved under N2"),
    ])
    if not any(o["name"] == "concentration_calculation_basis" for o in r["outcomes"]):
        r["outcomes"].append(field("concentration_calculation_basis", "calculated assuming 100% yield for the oxidative-addition step", ev(7), ["organozinc"]))
    records.append(r)

# Page 7: iodinolysis/hydrolysis are successive experimental stages, not merged with organozinc formation.
for label in ("12a", "12c", "12d"):
    e = ev(7)
    participants = [
        part("organozinc", "reactant", f"organozinc reagent {label}", e, amounts=[
            ("volume", qty(1, "mL")), ("concentration", qty(1, "M", "ca. 1 mmol/mL")), ("amount", qty(1, "mmol", "ca. 1 mmol")),
        ]),
        part("iodine", "reagent", "iodine", e, name="iodine", smiles="II", amounts=[("mass", qty(381, "mg")), ("amount", qty(1.5, "mmol"))]),
        part("thf", "solvent", "THF", e, name="tetrahydrofuran", smiles="C1CCOC1", amounts=[("volume", qty(5, "mL", "1 mL + 4 mL"))]),
        part("product", "product", f"iodinolysis product(s) from {label}", e),
    ]
    records.append(record(f"iodinolysis_{label}", e, participants, [
        ("initial_temperature", qty(-78, "°C")),
        ("operation", "iodine solution added at -78 °C, then mixture warmed to room temperature"),
        ("reaction_time", None),
        ("workup", "diethyl ether extraction; saturated aqueous sodium thiosulfate wash; saturated aqueous sodium chloride wash; MgSO4 drying; rotary evaporation"),
        ("purification", "silica gel chromatography"),
    ], [field("result", "iodinolysis product(s) obtained; identity and yield not stated in this paragraph", e, ["product"])],
        unresolved=["Reaction time, product identity and yield are not stated in the inspected paragraph.", "Supporting information was not explicitly provided or associated."]))

e = ev(7)
records.append(record("hydrolysis_12b", e, [
    part("organozinc", "reactant", "organozinc reagent 12b", e, amounts=[("volume", qty(1, "mL"))]),
    part("hcl", "reagent", "dilute aqueous hydrochloric acid", e, name="hydrochloric acid", amounts=[("volume", qty(5, "mL"))]),
    part("product", "product", "hydrolysis product(s) from 12b", e),
], [
    ("reaction_temperature", None),
    ("reaction_time", None),
    ("operation", "organozinc reagent 12b was added to dilute aqueous hydrochloric acid"),
    ("workup", "diethyl ether extraction; water wash; MgSO4 drying; rotary evaporation"),
    ("purification", "silica gel chromatography"),
], [field("result", "hydrolysis product(s) obtained; identity and yield not stated in this paragraph", e, ["product"])],
    unresolved=["Reaction temperature, time, product identity and yield are not stated in the inspected paragraph.", "Supporting information was not explicitly provided or associated."]))

# Page 7: three propargylic-carbonate preparations.
e = ev(7)
records.append(record("synthesis_carbonate_11b", e, [
    part("alcohol", "reactant", "3-phenylprop-2-ynol", e, name="3-phenylprop-2-yn-1-ol", smiles="OCC#Cc1ccccc1", amounts=[("mass", qty(4.27, "g")), ("amount", qty(32, "mmol"))]),
    part("pyridine", "reagent", "pyridine", e, smiles="n1ccccc1", amounts=[("amount", qty(70, "mmol")), ("volume", qty(5.71, "mL"))]),
    part("chloroformate", "reactant", "methyl chloroformate", e, smiles="COC(=O)Cl", amounts=[("amount", qty(64, "mmol")), ("volume", qty(2.55, "mL"))]),
    part("ether", "solvent", "Et2O", e, name="diethyl ether", smiles="CCOCC", amounts=[("volume", qty(40, "mL"))]),
    part("product", "product", "11b", e, name="methyl 3-phenylprop-2-ynyl carbonate", smiles="COC(=O)OCC#Cc1ccccc1", amounts=[("mass", qty(5.126, "g"))]),
], [
    ("initial_temperature", qty(0, "°C")),
    ("addition_time", qty(5, "min")),
    ("operation", "methyl chloroformate added slowly at 0 °C; mixture then warmed to room temperature"),
    ("reaction_time", "until complete by TLC"),
    ("workup", "quenched with dilute aqueous HCl; extracted with diethyl ether; washed with saturated aqueous sodium chloride; dried over MgSO4; rotary evaporation"),
    ("purification", "recrystallization from diethyl ether"),
], [field("yield", qty(84, "%"), e, ["product"]), field("yield_measurement_basis", "isolated after recrystallization", e, ["product"])],
    unresolved=["Supporting information was mentioned but not explicitly provided or associated.", "Candidate SMILES are unverified against an independently reviewed structure drawing."]))

for suffix, alcohol_label, alcohol_name, alcohol_smiles, alcohol_mass, alcohol_amount, product_label, product_name, product_smiles, product_mass, yld, recovered_mass, recovery in [
    ("synthesis_carbonate_11d", "1-(trimethylsilyl)hex-1-yn-3-ol", "1-(trimethylsilyl)hex-1-yn-3-ol", "CCCC(O)C#C[Si](C)(C)C", 5.207, 30.6, "11d", "methyl 1-(trimethylsilyl)hex-1-yn-3-yl carbonate", "CCCC(OC(=O)OC)C#C[Si](C)(C)C", 3.538, 51, 1.950, 37),
    ("synthesis_carbonate_11f", "1-phenylhex-1-yn-3-ol", "1-phenylhex-1-yn-3-ol", "CCCC(O)C#Cc1ccccc1", 6.179, 35.5, "11f", "methyl 1-phenylhex-1-yn-3-yl carbonate", "CCCC(OC(=O)OC)C#Cc1ccccc1", 6.08, 74, 1.503, 24),
]:
    participants = [
        part("alcohol", "reactant", alcohol_label, e, name=alcohol_name, smiles=alcohol_smiles, amounts=[("mass", qty(alcohol_mass, "g")), ("amount", qty(alcohol_amount, "mmol"))]),
        part("pyridine", "reagent", "pyridine (shared typical carbonate procedure)", e, smiles="n1ccccc1"),
        part("chloroformate", "reactant", "methyl chloroformate (shared typical carbonate procedure)", e, smiles="COC(=O)Cl"),
        part("ether", "solvent", "Et2O (shared typical carbonate procedure)", e, name="diethyl ether", smiles="CCOCC"),
        part("product", "product", product_label, e, name=product_name, smiles=product_smiles, amounts=[("mass", qty(product_mass, "g"))]),
    ]
    records.append(record(suffix, e, participants, [
        ("operation", "prepared by the propargylic-carbonate typical procedure immediately above; substrate-specific reagent quantities and reaction time were not restated"),
        ("reaction_temperature", None),
        ("reaction_time", None),
    ], [
        field("yield", qty(yld, "%"), e, ["product"]),
        field("yield_measurement_basis", "isolated", e, ["product"]),
        field("recovered_starting_material_mass", qty(recovered_mass, "g"), e, ["alcohol"]),
        field("recovered_starting_material_percentage", qty(recovery, "%"), e, ["alcohol"]),
    ], unresolved=["Exact pyridine, methyl chloroformate and solvent quantities and reaction time were not restated for this substrate.", "Supporting information was mentioned but not explicitly provided or associated.", "Candidate SMILES are unverified against an independently reviewed structure drawing."]))

# Page 8: Table 2 rows 1-9 gain the general workup and substrate-specific amounts.
table2 = {
    1: ("11a", [("mass", qty(121, "mg")), ("amount", qty(0.65, "mmol"))], "12a", [("volume", qty(0.5, "mL")), ("concentration", qty(1.0, "M", "ca. 1.0 M")), ("amount", qty(0.5, "mmol"))], [("prod1", "Z-2a", "ethyl 6-(trimethylsilyl)hex-5-yn-(2Z)-enoate", 46, 44)], (20, 16.5)),
    2: ("11a", [("mass", qty(102, "mg")), ("amount", qty(0.55, "mmol"))], "12b", [("volume", qty(0.41, "mL")), ("concentration", qty(1.0, "M", "ca. 1.0 M")), ("amount", qty(0.41, "mmol"))], [("prod1", "E-2i", "methyl 6-(trimethylsilyl)-4-phenylhex-5-yn-(2Z)-enoate", 90, 60)], None),
    3: ("11a", [("mass", qty(65, "mg")), ("amount", qty(0.35, "mmol"))], "12c", [("volume", qty(0.5, "mL")), ("concentration", qty(1.0, "M", "ca. 1.0 M")), ("amount", qty(0.5, "mmol"))], [("prodZ", "Z-2j", "methyl 6-(trimethylsilyl)-4-methylhex-5-yn-(2Z)-enoate", 20, 28), ("prodE", "E-2j", "methyl 6-(trimethylsilyl)-4-methylhex-5-yn-(2E)-enoate", 26, 35)], None),
    4: ("11b", [("mass", qty(124, "mg")), ("amount", qty(0.65, "mmol"))], "12a", [("volume", qty(0.5, "mL")), ("concentration", qty(1.0, "M", "ca. 1.0 M")), ("amount", qty(0.5, "mmol"))], [("prod1", "Z-2h", "ethyl 6-phenylhex-5-yn-(2Z)-enoate", 63, 60)], (27, None)),
    5: ("11b", [("mass", qty(114, "mg")), ("amount", qty(0.6, "mmol"))], "12b", [("volume", qty(0.41, "mL")), ("concentration", qty(1.0, "M", "ca. 1.0 M")), ("amount", qty(0.5, "mmol"))], [("prod1", "E-2k", "methyl 3,6-diphenylhex-5-yn-(2E)-enoate", 87, 63)], None),
    6: ("11b", [("mass", qty(124, "mg")), ("amount", qty(0.65, "mmol"))], "12d", [("volume", qty(0.5, "mL")), ("concentration", qty(1.0, "M", "ca. 1.0 M")), ("amount", qty(0.5, "mmol"))], [("prodZ", "Z-2h", "ethyl 6-phenylhex-5-yn-(2Z)-enoate", 26, 18.7), ("prodE", "E-2h", "ethyl 6-phenylhex-5-yn-(2E)-enoate", 30, 21.6)], None),
    7: ("11c", [("mass", qty(219, "mg")), ("amount", qty(1.3, "mmol"))], "12a", [("volume", qty(1.0, "mL")), ("concentration", qty(1.0, "M", "ca. 1.0 M")), ("amount", qty(1.0, "mmol"))], [("prod1", "Z-2l", "ethyl dec-5-yn-(2Z)-enoate", 106, 55), ("prod2", "E-6d", "ethyl 4-n-butylhexa-2,4,5-trienoate", 35, 18)], (30, None)),
    8: ("11c", [("mass", qty(102, "mg")), ("amount", qty(0.6, "mmol"))], "12b", [("volume", qty(0.41, "mL")), ("concentration", qty(1.0, "M", "ca. 1.0 M")), ("amount", qty(0.41, "mmol"))], [("prod1", "E-2m", "methyl 4-phenyldec-5-yn-(2E)-enoate", 67, 44)], None),
    9: ("11d", [("mass", qty(146, "mg")), ("amount", qty(0.65, "mmol"))], "12a", [("volume", qty(0.5, "mL")), ("concentration", qty(1.0, "M", "ca. 1.0 M")), ("amount", qty(0.5, "mmol"))], [("prod1", "Z-2c", "ethyl 6-(trimethylsilyl)-4-propylhex-5-yn-(2Z)-enoate", 44, 35)], (52, None)),
}
for row, (carbonate_label, carbonate_amounts, zinc_label, zinc_amounts, products, recovered) in table2.items():
    r = get(f"table2_entry{row}")
    add_evidence(r, 8)
    find_part(r, "carbonate")["label"] = fact(carbonate_label, ev(8))
    set_amounts(r, "carbonate", 8, carbonate_amounts)
    find_part(r, "zinc")["label"] = fact(zinc_label, ev(8))
    set_amounts(r, "zinc", 8, zinc_amounts)
    set_amounts(r, "pd", 8, [("mass", qty(29, "mg")), ("amount", qty(0.025, "mmol")), ("catalyst_loading", qty(5, "mol%"))])
    set_amounts(r, "thf", 8, [("volume", qty(2, "mL"))])
    if row in (3, 6):
        r["participants"] = [p for p in r["participants"] if p["role"] != "product"]
    for entity, label, name, mass, yld in products:
        if not any(p["entity_id"] == entity for p in r["participants"]):
            r["participants"].append(part(entity, "product", label, ev(8), name=name, amounts=[("mass", qty(mass, "mg"))]))
        else:
            p = find_part(r, entity)
            p["label"] = fact(label, ev(8))
            p["name"] = fact(name, ev(8))
            p["amounts"] = [field("mass", qty(mass, "mg"), ev(8))]
    add_conditions(r, 8, [
        ("reaction_endpoint", "complete by TLC"),
        ("workup", "quenched with water; extracted with diethyl ether; washed with water; dried over MgSO4; rotary evaporation"),
        ("purification", "silica gel chromatography"),
    ])
    new_outcomes = []
    for entity, label, name, mass, yld in products:
        yield_name = "detailed_procedure_yield" if row == 4 else "yield"
        new_outcomes.extend([
            field("isolated_product_mass", qty(mass, "mg"), ev(8), [entity]),
            field(yield_name, qty(yld, "%"), ev(8), [entity]),
            field("yield_measurement_basis", "isolated after chromatography", ev(8), [entity]),
        ])
    if row == 3:
        new_outcomes.append(field("combined_yield", qty(63, "%"), ev(4), ["prodZ", "prodE"]))
        new_outcomes.append(field("stereoisomer_ratio", "Z/E=4/5", ev(4), ["prodZ", "prodE"]))
        add_unresolved(r, "The page-8 heading repeats '(2Z)-enoate' for both Z-2j and E-2j; labels and individual analytical blocks are retained without silently correcting the source.")
    elif row == 4:
        new_outcomes.insert(0, field("reported_table_yield", qty(58, "%"), ev(4), ["prod1"]))
        add_unresolved(r, "Source-internal yield conflict: Table 2/cross-page prose reports 58%, while the detailed page-8 procedure reports 63 mg (60%).")
    elif row == 6:
        new_outcomes.append(field("combined_yield", qty(40, "%"), ev(4), ["prodZ", "prodE"]))
        new_outcomes.append(field("stereoisomer_ratio", "Z/E=5/6", ev(4), ["prodZ", "prodE"]))
    if recovered:
        rec_mass, rec_pct = recovered
        new_outcomes.append(field("recovered_starting_material_mass", qty(rec_mass, "mg"), ev(8), ["carbonate"]))
        if rec_pct is not None:
            new_outcomes.append(field("recovered_starting_material_percentage", qty(rec_pct, "%"), ev(8), ["carbonate"]))
    r["outcomes"] = new_outcomes
    if row == 2:
        add_unresolved(r, "Source-internal nomenclature conflict: the page-8 heading names a '(2Z)-enoate' while assigning the product label (E)-2i.")
    records.append(r)

# Page 8: Scheme 9 experiments, including an explicit qualitative no-product result.
scheme9 = {
    "scheme9_11e_12a": ([("mass", qty(138, "mg")), ("amount", qty(0.65, "mmol"))], [("volume", qty(0.6, "mL")), ("concentration", qty(1.0, "M", "ca. 1.0 M")), ("amount", qty(0.6, "mmol"))], 108, 70),
    "scheme9_11e_12d": ([("mass", qty(106, "mg")), ("amount", qty(0.5, "mmol"))], [("volume", qty(1.0, "mL")), ("concentration", qty(1.0, "M", "ca. 1.0 M")), ("amount", qty(1.0, "mmol"))], 65, 55),
    "scheme9_11f_12a_no_product": ([("mass", qty(116, "mg")), ("amount", qty(0.5, "mmol"))], [("volume", qty(0.5, "mL")), ("concentration", qty(1.0, "M", "ca. 1.0 M")), ("amount", qty(0.5, "mmol"))], None, None),
}
for suffix, (carbonate_amounts, zinc_amounts, mass, yld) in scheme9.items():
    r = get(suffix)
    add_evidence(r, 8)
    set_amounts(r, "carbonate", 8, carbonate_amounts)
    set_amounts(r, "zinc", 8, zinc_amounts)
    set_amounts(r, "pd", 8, [("mass", qty(29, "mg")), ("amount", qty(0.025, "mmol")), ("catalyst_loading", qty(5, "mol%"))])
    set_amounts(r, "thf", 8, [("volume", qty(2, "mL"))])
    add_conditions(r, 8, [
        ("reaction_endpoint", "complete by TLC"),
        ("workup", "quenched with water; extracted with diethyl ether; washed with water; dried over MgSO4; rotary evaporation"),
        ("purification", "silica gel chromatography"),
    ])
    if mass is None:
        r["outcomes"] = [field("result", "no product", ev(8))]
        add_unresolved(r, "The source reports no product qualitatively; it does not report a numerical 0% isolated yield.")
    else:
        set_amounts(r, "prod", 8, [("mass", qty(mass, "mg"))])
        r["outcomes"] = [field("yield", qty(yld, "%"), ev(8), ["prod"]), field("yield_measurement_basis", "isolated after chromatography", ev(8), ["prod"])]
    records.append(r)

# Page 8: two boronic-acid coupling experiments.
r = get("scheme10_11g_boronic")
add_evidence(r, 8)
set_amounts(r, "carbonate", 8, [("mass", qty(85, "mg")), ("amount", qty(0.5, "mmol"))])
set_amounts(r, "boronic", 8, [("mass", qty(89, "mg")), ("amount", qty(0.6, "mmol"))])
set_amounts(r, "pd", 8, [("mass", qty(29, "mg")), ("amount", qty(0.025, "mmol")), ("catalyst_loading", qty(5, "mol%"))])
set_amounts(r, "thf", 8, [("volume", qty(2, "mL"))])
set_amounts(r, "prod1", 8, [("mass", qty(52, "mg"))])
set_amounts(r, "prod2", 8, [("mass", qty(29, "mg"))])
add_conditions(r, 8, [
    ("workup", "quenched with water; extracted with diethyl ether; dried over MgSO4; rotary evaporation"),
    ("purification", "silica gel chromatography, hexane"),
])
r["outcomes"] = [
    field("yield", qty(49, "%"), ev(8), ["prod1"]),
    field("yield_measurement_basis", "isolated after chromatography; contaminated with a small amount of compound 13", ev(8), ["prod1"]),
    field("yield", qty(29, "%"), ev(8), ["prod2"]),
    field("yield_measurement_basis", "isolated after chromatography", ev(8), ["prod2"]),
    field("byproduct_amount", "small amount; no numeric yield", ev(8), ["byproduct"]),
]
records.append(r)

r = get("scheme10_11e_boronic")
add_evidence(r, 8)
set_amounts(r, "carbonate", 8, [("mass", qty(53, "mg")), ("amount", qty(0.25, "mmol"))])
set_amounts(r, "boronic", 8, [("mass", qty(74, "mg")), ("amount", qty(0.5, "mmol"))])
set_amounts(r, "base", 8, [("mass", qty(94, "mg")), ("amount", qty(0.88, "mmol")), ("equivalents", qty(3.5, "equiv"))])
set_amounts(r, "prod", 8, [("mass", qty(36, "mg"))])
r["outcomes"] = [field("yield", qty(60, "%"), ev(8), ["prod"]), field("yield_measurement_basis", "isolated product", ev(8), ["prod"]), field("regioselectivity", "sole product", ev(5), ["prod"])]
records.append(r)

# Page 8: Equation (1), distinct acetate substrate experiment.
r = get("equation1_propargyl_acetate_12a")
add_evidence(r, 8)
set_amounts(r, "acetate", 8, [("mass", qty(115, "mg")), ("amount", qty(0.65, "mmol"))])
set_amounts(r, "zinc", 8, [("volume", qty(0.5, "mL")), ("concentration", qty(1.0, "M", "ca. 1.0 M")), ("amount", qty(0.5, "mmol"))])
set_amounts(r, "pd", 8, [("mass", qty(29, "mg")), ("amount", qty(0.025, "mmol")), ("catalyst_loading", qty(5, "mol%"))])
set_amounts(r, "thf", 8, [("volume", qty(2, "mL"))])
set_amounts(r, "prod", 8, [("mass", qty(39, "mg"))])
add_conditions(r, 8, [
    ("reaction_endpoint", "complete by TLC"),
    ("workup", "quenched with water; extracted with diethyl ether; washed with water; dried over MgSO4; rotary evaporation"),
    ("purification", "silica gel chromatography"),
])
r["outcomes"] = [
    field("yield", qty(37, "%"), ev(8), ["prod"]),
    field("yield_measurement_basis", "isolated after chromatography", ev(8), ["prod"]),
    field("recovered_starting_material_mass", qty(37, "mg"), ev(8), ["acetate"]),
]
records.append(r)

out = RUN / "raw_model" / "extracted_records_pages_0007_0008.json"
out.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"records_submitted": len(records), "new_record_ids": [r["record_id"] for r in records if r["record_id"] not in EXISTING], "output": str(out)}, ensure_ascii=False, indent=2))
