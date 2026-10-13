import copy
import json
from pathlib import Path


BASE = Path(__file__).resolve().parents[1]
DATASET = json.loads((BASE / "dataset.json").read_text())
DOC = "doc_1e29b02f2fac50bb"
BY_ID = {record["record_id"]: record for record in DATASET["experiments"]}


def ev(*pages):
    result = []
    for page in pages:
        result.extend([f"{DOC}:page{page}:image", f"{DOC}:page{page}:text"])
    return result


def fact(value, evidence):
    return {
        "value": value,
        "evidence_ids": list(evidence),
        "verification": "missing" if value is None else "unreviewed",
    }


def qty(number, unit, **extra):
    value = {"number": number, "unit": unit}
    value.update(extra)
    return value


def field(name, value, evidence, targets=None):
    item = {"name": name, "fact": fact(value, evidence)}
    if targets:
        item["target_entity_ids"] = list(targets)
    return item


def participant(entity_id, role, label, name, smiles, evidence):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence),
        "smiles": fact(smiles, evidence),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": [],
    }


def record(record_id):
    item = copy.deepcopy(BY_ID[f"{DOC}:{record_id}"])
    item["status"] = "candidate"
    item["completeness"] = "partial"
    item["review"] = {
        "method": "none",
        "reviewer": None,
        "checked_fields": [],
        "unresolved": [
            "Machine-extracted record requires chemical source review.",
            "No supporting-information file was explicitly associated with this dataset.",
        ],
    }
    return item


def add_evidence(item, *pages):
    item["evidence_ids"] = list(dict.fromkeys(item["evidence_ids"] + ev(*pages)))


def get_participant(item, entity_id):
    return next(p for p in item["participants"] if p["entity_id"] == entity_id)


def upsert_field(fields, name, value, evidence, targets=None):
    fields[:] = [entry for entry in fields if entry["name"] != name]
    fields.append(field(name, value, evidence, targets))


def add_amount(item, entity_id, name, value, evidence):
    upsert_field(get_participant(item, entity_id)["amounts"], name, value, evidence)


def add_standard_operations(item, evidence, purification):
    conditions = item["steps"][0]["conditions"]
    for name, value in [
        ("atmosphere", "argon"),
        ("operation", "oven-dried screw-cap reaction tube; sealed and stirred in an oil bath"),
        ("endpoint_monitoring", "TLC upon cooling"),
        ("workup", "cooled to room temperature, filtered, and evaporated"),
        ("purification", purification),
    ]:
        upsert_field(conditions, name, value, evidence)


def add_product_details(item, product_id, mass_mg, evidence, form):
    add_amount(item, product_id, "isolated_product_mass", qty(mass_mg, "mg"), evidence)
    upsert_field(item["outcomes"], "isolated_product_form", form, evidence, [product_id])
    for outcome in item["outcomes"]:
        if outcome["name"] in {"isolated_yield", "yield_measurement_basis"}:
            outcome["fact"]["evidence_ids"] = list(
                dict.fromkeys(outcome["fact"]["evidence_ids"] + list(evidence))
            )


def add_common_butanal_batch(
    item, page, substrate_id, product_id, catalyst, substrate, butanal, amine,
    product_mass, purification, form="liquid",
):
    evidence = ev(page)
    add_evidence(item, page)
    cat_mass, cat_mmol = catalyst
    sub_mass, sub_mmol = substrate
    but_volume, but_mass, but_mmol = butanal
    am_volume, am_mass, am_mmol = amine
    add_amount(item, "CuI", "mass", qty(cat_mass, "mg"), evidence)
    add_amount(item, "CuI", "amount", qty(cat_mmol, "mmol"), evidence)
    add_amount(item, substrate_id, "mass", qty(sub_mass, "mg"), evidence)
    add_amount(item, substrate_id, "amount", qty(sub_mmol, "mmol"), evidence)
    if but_volume is not None:
        add_amount(item, "nPrCHO", "volume", qty(but_volume, "uL"), evidence)
        add_amount(item, "nPrCHO", "reported_density", "0.817 g mL−1", evidence)
    add_amount(item, "nPrCHO", "mass", qty(but_mass, "mg"), evidence)
    add_amount(item, "nPrCHO", "amount", qty(but_mmol, "mmol"), evidence)
    if am_volume is not None:
        add_amount(item, "nBu2NH", "volume", qty(am_volume, "uL"), evidence)
        add_amount(item, "nBu2NH", "reported_density", "0.762 g mL−1", evidence)
    add_amount(item, "nBu2NH", "mass", qty(am_mass, "mg"), evidence)
    add_amount(item, "nBu2NH", "amount", qty(am_mmol, "mmol"), evidence)
    add_amount(item, "dioxane", "volume", qty(3, "mL"), evidence)
    add_product_details(item, product_id, product_mass, evidence, form)
    add_standard_operations(item, ev(4, page), purification)


records = []

# Table 4 entries 12-20: detailed batches on pages 7-9 enrich, but do not
# duplicate, the scope rows already extracted from page 3.
details = [
    (12, (6, 7), "1k", "2k", (38.0, 0.10), (208.0, 1.00), (142, 116.0, 1.61),
     (238, 181.4, 1.40), 155.8,
     "silica-gel column chromatography; petroleum ether/ethyl acetate 20/1, then 10/1",
     "liquid"),
    (13, (7,), "1l", "2l", (18.9, 0.10), (174.1, 1.00), (142, 116.0, 1.61),
     (238, 181.4, 1.40), 143.0,
     "silica-gel column chromatography; petroleum ether/ethyl acetate 20/1, then 10/1",
     "liquid; pair of diastereoisomers"),
    (14, (7,), "1m", "2m", (38.7, 0.20), (209.3, 1.00), (None, 116.0, 1.61),
     (None, 180.8, 1.40), 131.1,
     "silica-gel column chromatography; petroleum ether/DCM/ethyl acetate 40/40/1",
     "liquid"),
    (15, (7,), "1n", "2n", (37.6, 0.20), (279.4, 1.00), (None, 115.7, 1.61),
     (None, 181.7, 1.41), 195.9,
     "silica-gel column chromatography; petroleum ether/DCM/ethyl acetate 60/20/1, then 40/40/1",
     "liquid; pair of diastereoisomers"),
    (16, (7, 8), "1o", "2o", (37.9, 0.20), (306.5, 1.00), (None, 116.0, 1.61),
     (None, 179.5, 1.39), 195.2,
     "silica-gel column chromatography; petroleum ether/DCM/ethyl acetate 60/20/1, then 40/40/1",
     "liquid; pair of diastereoisomers"),
    (17, (8,), "1p", "2p", (28.5, 0.15), (168.8, 1.00), (142, 116.0, 1.61),
     (238, 181.4, 1.40), 120.7,
     "silica-gel column chromatography; petroleum ether/ethyl acetate 20/1, then 10/1",
     "liquid"),
    (18, (8,), "1q", "2q", (37.8, 0.20), (147.0, 1.01), (142, 116.0, 1.61),
     (238, 181.4, 1.40), 112.1,
     "silica-gel column chromatography; petroleum ether/ethyl acetate 100/1",
     "liquid"),
    (19, (8,), "1r", "2r", (37.8, 0.20), (141.9, 1.01), (142, 116.0, 1.61),
     (238, 181.4, 1.40), 79.7,
     "silica-gel column chromatography; petroleum ether/ethyl acetate 30/1, then 20/1",
     "liquid; pair of diastereoisomers"),
    (20, (8, 9), "1s", "2s", (28.5, 0.20), (137.9, 1.00), (142, 116.0, 1.61),
     (238, 181.4, 1.40), 128.2,
     "silica-gel column chromatography; petroleum ether (30–60 °C)",
     "liquid"),
]

for (entry, pages, substrate_id, product_id, catalyst, substrate, butanal, amine,
     product_mass, purification, form) in details:
    item = record(f"table4_entry{entry}")
    first_page = pages[0]
    add_common_butanal_batch(
        item, first_page, substrate_id, product_id, catalyst, substrate, butanal,
        amine, product_mass, purification, form,
    )
    add_evidence(item, *pages)
    if len(pages) > 1:
        # Exact charges and/or the outcome/characterization cross page boundaries.
        # Cite the full visible span instead of assigning a value to only one half.
        for part in item["participants"]:
            for amount in part["amounts"]:
                amount["fact"]["evidence_ids"] = list(
                    dict.fromkeys(amount["fact"]["evidence_ids"] + ev(*pages))
                )
        for step in item["steps"]:
            for condition in step["conditions"]:
                condition["fact"]["evidence_ids"] = list(
                    dict.fromkeys(condition["fact"]["evidence_ids"] + ev(*pages))
                )
        for outcome in item["outcomes"]:
            outcome["fact"]["evidence_ids"] = list(
                dict.fromkeys(outcome["fact"]["evidence_ids"] + ev(*pages))
            )
    if entry == 12:
        item["review"]["unresolved"].append(
            "For 2k, page 6 prints CuI as 38.0 mg, 0.10 mmol while Table 4 gives 20 mol% on 1.00 mmol substrate; no correction was inferred."
        )
    if entry == 20:
        item["review"]["unresolved"].append(
            "For 2s, the detailed paragraph prints CuI as 28.5 mg, 0.20 mmol while Table 4 gives 15 mol% on 1.00 mmol substrate; all printed values are retained without reconciliation."
        )
        add_amount(item, "1s", "volume", qty(180, "uL"), ev(8))
        add_amount(item, "1s", "reported_density", "0.766 g mL−1", ev(8))
    records.append(item)


def enrich_scheme2(record_id, page, substrate, aldehyde, amine, product_id,
                   product_mass, purification, form="liquid; pair of diastereoisomers"):
    item = record(record_id)
    evidence = ev(page)
    add_evidence(item, page)
    cat_mass, cat_mmol = substrate.pop("catalyst")
    add_amount(item, "CuI", "mass", qty(cat_mass, "mg"), evidence)
    add_amount(item, "CuI", "amount", qty(cat_mmol, "mmol"), evidence)
    add_amount(item, "1b", "mass", qty(substrate["mass"], "mg"), evidence)
    add_amount(item, "1b", "amount", qty(substrate["mmol"], "mmol"), evidence)
    for name, value in aldehyde.items():
        add_amount(item, "aldehyde", name, value, evidence)
    for name, value in amine.items():
        add_amount(item, "amine", name, value, evidence)
    add_amount(item, "dioxane", "volume", qty(3, "mL"), evidence)
    add_product_details(item, product_id, product_mass, evidence, form)
    add_standard_operations(item, ev(4, page), purification)
    return item


records.append(enrich_scheme2(
    "scheme2_paraformaldehyde", 9,
    {"catalyst": (19.0, 0.10), "mass": 166.3, "mmol": 1.00},
    {"mass": qty(47.9, "mg"), "amount": qty(1.60, "mmol")},
    {"volume": qty(238, "uL"), "reported_density": "0.762 g mL−1",
     "mass": qty(181.4, "mg"), "amount": qty(1.40, "mmol")},
    "2t", 119.9,
    "silica-gel column chromatography; petroleum ether/ethyl acetate 10/1, then 5/1",
    "liquid",
))
records.append(enrich_scheme2(
    "scheme2_propanal", 9,
    {"catalyst": (19.2, 0.10), "mass": 167.9, "mmol": 1.01},
    {"volume": qty(116, "uL"), "reported_density": "0.80 g mL−1",
     "mass": qty(92.8, "mg"), "amount": qty(1.60, "mmol")},
    {"volume": qty(192, "uL"), "reported_density": "0.738 g mL−1",
     "mass": qty(141.7, "mg"), "amount": qty(1.40, "mmol")},
    "2u", 130.0,
    "silica-gel column chromatography; petroleum ether/ethyl acetate 10/1",
))
records.append(enrich_scheme2(
    "scheme2_isobutanal", 9,
    {"catalyst": (19.2, 0.10), "mass": 166.1, "mmol": 1.00},
    {"volume": qty(146, "uL"), "reported_density": "0.794 g mL−1",
     "mass": qty(115.9, "mg"), "amount": qty(1.61, "mmol")},
    {"volume": qty(244, "uL"), "reported_density": "0.74 g mL−1",
     "mass": qty(180.6, "mg"), "amount": qty(1.40, "mmol")},
    "2v", 105.7,
    "silica-gel column chromatography; petroleum ether/ethyl acetate 10/1",
))


def enrich_table5(entry, pages, substrate, aldehyde, amine, product_id,
                  product_mass, purification, form="liquid; pair of diastereoisomers"):
    item = record(f"table5_entry{entry}")
    evidence = ev(*pages)
    add_evidence(item, *pages)
    add_amount(item, "CuI", "mass", qty(substrate["cat_mass"], "mg"), evidence)
    add_amount(item, "CuI", "amount", qty(substrate["cat_mmol"], "mmol"), evidence)
    substrate_id = "1t" if entry == 5 else "1a"
    add_amount(item, substrate_id, "mass", qty(substrate["mass"], "mg"), evidence)
    add_amount(item, substrate_id, "amount", qty(substrate["mmol"], "mmol"), evidence)
    for name, value in aldehyde.items():
        add_amount(item, "aldehyde", name, value, evidence)
    for name, value in amine.items():
        add_amount(item, "iBu2NH", name, value, evidence)
    add_amount(item, "dioxane", "volume", qty(3, "mL"), evidence)
    add_product_details(item, product_id, product_mass, evidence, form)
    add_standard_operations(item, ev(4, *pages), purification)
    return item


records.append(enrich_table5(
    1, (9,), {"cat_mass": 19.0, "cat_mmol": 0.10, "mass": 132.1, "mmol": 1.00},
    {"mass": qty(93.0, "mg"), "amount": qty(1.60, "mmol")},
    {"mass": qty(180.9, "mg"), "amount": qty(1.40, "mmol")},
    "2w", 85.5, "silica-gel column chromatography; petroleum ether/ethyl acetate 15/1",
))
records.append(enrich_table5(
    2, (9, 10), {"cat_mass": 18.8, "cat_mmol": 0.10, "mass": 132.1, "mmol": 1.00},
    {"mass": qty(179.7, "mg"), "amount": qty(1.60, "mmol")},
    {"mass": qty(181.6, "mg"), "amount": qty(1.41, "mmol")},
    "2x", 88.2, "silica-gel column chromatography; petroleum ether/ethyl acetate 15/1",
))
records.append(enrich_table5(
    3, (10,), {"cat_mass": 19.4, "cat_mmol": 0.10, "mass": 132.1, "mmol": 1.00},
    {"mass": qty(159.7, "mg"), "amount": qty(1.60, "mmol")},
    {"mass": qty(181.2, "mg"), "amount": qty(1.40, "mmol")},
    "2y", 119.6, "silica-gel column chromatography; petroleum ether/ethyl acetate 10/1",
))
item_2z = enrich_table5(
    4, (10,), {"cat_mass": 19.5, "cat_mmol": 0.10, "mass": 131.4, "mmol": 1.00},
    {"mass": qty(138.2, "mg"), "amount": qty(1.61, "mmol")},
    {"mass": qty(181.6, "mg"), "amount": qty(1.41, "mmol")},
    "2z", 89.7, "silica-gel column chromatography; petroleum ether/ethyl acetate 15/1",
)
conditions_2z = item_2z["steps"][0]["conditions"]
for condition in conditions_2z:
    if condition["name"] == "reaction_time":
        condition["name"] = "table_reaction_time"
upsert_field(conditions_2z, "experimental_scheme_reaction_time", qty(14, "h"), ev(10))
item_2z["review"]["unresolved"].append(
    "Table 5 entry 4 reports 12 h on page 3, whereas the detailed reaction scheme on page 10 reports 14 h; both are retained without choosing one."
)
records.append(item_2z)

item_2aa = enrich_table5(
    5, (10,), {"cat_mass": 38.3, "cat_mmol": 0.20, "mass": 56.3, "mmol": 1.00},
    {"mass": qty(203.7, "mg"), "amount": qty(1.59, "mmol")},
    {"mass": qty(179.9, "mg"), "amount": qty(1.39, "mmol")},
    "2aa", 70.0,
    "silica-gel column chromatography; petroleum ether/ethyl acetate 20/1, then 10/1",
    "liquid",
)
conditions = item_2aa["steps"][0]["conditions"]
upsert_field(conditions, "initial_temperature", "r.t.", ev(10))
upsert_field(conditions, "heating_ramp_temperature", qty(130, "°C"), ev(10))
upsert_field(conditions, "heating_ramp_time", qty(15, "min"), ev(10))
records.append(item_2aa)


# The 1 g-scale 2a preparation is the detailed realization of Table 4 entry 2.
scale = record("table4_entry2")
add_evidence(scale, 10, 11)
e_scale = ev(10, 11)
for entity_id, amounts in {
    "CuI": [("mass", qty(152.2, "mg")), ("amount", qty(0.80, "mmol"))],
    "1a": [("mass", qty(1.0547, "g")), ("amount", qty(7.99, "mmol"))],
    "nPrCHO": [("volume", qty(1.13, "mL")), ("reported_density", "0.817 g mL−1"),
                ("mass", qty(923.2, "mg")), ("amount", qty(12.8, "mmol"))],
    "nBu2NH": [("volume", qty(1.90, "mL")), ("reported_density", "0.762 g mL−1"),
                ("mass", qty(1.4478, "g")), ("amount", qty(11.2, "mmol"))],
    "dioxane": [("volume", qty(20, "mL"))],
}.items():
    for name, value in amounts:
        add_amount(scale, entity_id, name, value, e_scale)
add_amount(scale, "2a", "isolated_product_mass", qty(0.9854, "g"), ev(11))
conditions = scale["steps"][0]["conditions"]
upsert_field(conditions, "reaction_concentration", qty(0.40, "M"), ev(11))
upsert_field(conditions, "initial_temperature", "r.t.", ev(10, 11))
upsert_field(conditions, "heating_ramp_temperature", qty(130, "°C"), ev(10, 11))
upsert_field(conditions, "heating_ramp_time", qty(20, "min"), ev(10, 11))
add_standard_operations(
    scale, ev(10, 11),
    "silica-gel column chromatography; petroleum ether/DCM/ethyl acetate 60/20/1",
)
upsert_field(scale["outcomes"], "isolated_product_form", "liquid", ev(11), ["2a"])
for outcome in scale["outcomes"]:
    if outcome["name"] in {"isolated_yield", "yield_measurement_basis"}:
        outcome["fact"]["evidence_ids"] = list(dict.fromkeys(outcome["fact"]["evidence_ids"] + ev(11)))
records.append(scale)


# Page 11: independently isolated propargylic amine intermediate 3a.
e11 = ev(11)
parts = [
    participant("1a", "reactant", "1a", "1-phenylprop-2-yn-1-ol", "C#CC(O)c1ccccc1", e11),
    participant("nPrCHO", "reactant", "n-PrCHO", "n-butanal", "CCCC=O", e11),
    participant("nBu2NH", "reagent", "n-Bu2NH", "dibutylamine", "CCCCNCCCC", e11),
    participant("CuI", "catalyst", "CuI", "copper(I) iodide", "[Cu]I", e11),
    participant("dioxane", "solvent", "dioxane", "1,4-dioxane", "O1CCOCC1", e11),
    participant("3a", "product", "3a", "4-(N,N-dibutylamino)-1-phenylhept-2-yn-1-ol",
                "CCCCN(CCCC)C(CCC)C#CC(O)c1ccccc1", e11),
]
amount_map = {
    "1a": [("mass", qty(65.8, "mg")), ("amount", qty(0.50, "mmol"))],
    "nPrCHO": [("mass", qty(58.3, "mg")), ("amount", qty(0.81, "mmol")),
                ("equivalents", qty(1.6, "equiv"))],
    "nBu2NH": [("mass", qty(89.6, "mg")), ("amount", qty(0.69, "mmol")),
                ("equivalents", qty(1.4, "equiv"))],
    "CuI": [("mass", qty(9.8, "mg")), ("amount", qty(0.051, "mmol")),
            ("catalyst_loading", qty(10, "mol%"))],
    "dioxane": [("volume", qty(1.50, "mL"))],
    "3a": [("isolated_product_mass", qty(125.0, "mg"))],
}
for part in parts:
    for name, value in amount_map.get(part["entity_id"], []):
        part["amounts"].append(field(name, value, e11))
record_3a = {
    "record_id": f"{DOC}:preparation_3a",
    "document_id": DOC,
    "source_reaction_id": "preparation_3a",
    "record_kind": "reported_experiment",
    "status": "candidate",
    "completeness": "partial",
    "evidence_ids": e11,
    "participants": parts,
    "steps": [{
        "step_id": "reaction",
        "participant_ids": ["1a", "nPrCHO", "nBu2NH", "CuI", "dioxane"],
        "conditions": [
            field("reaction_concentration", qty(0.33, "M"), e11),
            field("reaction_temperature", qty(50, "°C"), e11),
            field("reaction_time", qty(2.4, "h"), e11),
            field("atmosphere", "argon", e11),
            field("operation", "oven-dried screw-cap reaction tube; sealed and stirred", e11),
            field("endpoint_monitoring", "TLC", e11),
            field("workup", "cooled to room temperature and evaporated", e11),
            field("purification", "silica-gel column chromatography; petroleum ether/ethyl acetate 10/1", e11),
        ],
    }],
    "outcomes": [
        field("isolated_yield", qty(79, "%"), e11, ["3a"]),
        field("yield_measurement_basis", "isolated yield", e11, ["3a"]),
        field("isolated_product_form", "liquid; pair of diastereoisomers", e11, ["3a"]),
    ],
    "notes": [],
    "review": {
        "method": "none",
        "reviewer": None,
        "checked_fields": [],
        "unresolved": [
            "Machine-extracted record requires chemical source review.",
            "No supporting-information file was explicitly associated with this dataset.",
        ],
    },
}
records.append(record_3a)


OUT = Path(__file__).with_name("records_pages_0007_0012.json")
OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({
    "output": str(OUT),
    "submitted_records": len(records),
    "new_records": [record_3a["record_id"]],
    "updated_records": len(records) - 1,
}, ensure_ascii=False))
