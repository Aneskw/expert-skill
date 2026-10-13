#!/usr/bin/env python3
import copy
import json
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
DOC = "doc_568ce4bf656e1cc8"


def ev(page, kind="text"):
    return f"{DOC}:page{page}:{kind}"


def evidence(page):
    return [ev(page), ev(page, "image")]


def fact(value, evidence_ids=()):
    return {
        "value": value,
        "evidence_ids": list(evidence_ids),
        "verification": "missing" if value is None else "unreviewed",
    }


def field(name, value, evidence_ids=(), targets=None):
    item = {"name": name, "fact": fact(value, evidence_ids)}
    if targets:
        item["target_entity_ids"] = list(targets)
    return item


def q(number, unit, **extra):
    return {"number": number, "unit": unit, **extra}


def participant(entity_id, role, label, evidence_ids, *, name=None, smiles=None, amounts=()):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence_ids),
        "name": fact(name, evidence_ids if name else ()),
        "smiles": fact(smiles, evidence_ids if smiles else ()),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": list(amounts),
    }


def add_page(record, page):
    for eid in evidence(page):
        if eid not in record["evidence_ids"]:
            record["evidence_ids"].append(eid)


def by_participant(record):
    return {p["entity_id"]: p for p in record["participants"]}


def exact_amounts(page, mass, amount):
    ee = evidence(page)
    return [field("mass", q(mass, "mg"), ee), field("amount", q(amount, "mmol"), ee)]


def set_scope_details(record, page, values, time, product_mass, detail_yield, *, workup=None, purification=None):
    add_page(record, page)
    ee = evidence(page)
    pp = by_participant(record)
    for entity_id, mass, amount in values:
        pp[entity_id]["amounts"] = exact_amounts(page, mass, amount)
    pp["palladium_acetate"]["amounts"].insert(
        0, field("catalyst_loading", q(2, "mol%"), [ev(4), ev(4, "image")])
    )
    pp["hoac"]["amounts"] = [field("volume", q(2, "mL"), ee)]
    pp["product"]["amounts"] = [field("isolated_mass", q(product_mass, "mg"), ee)]
    record["steps"] = [{
        "step_id": "cyclization",
        "participant_ids": [p["entity_id"] for p in record["participants"]],
        "conditions": [
            field("time", q(time, "h"), ee),
            field("temperature", q(60, "°C"), ee),
            field("operation", "Schlenk tube with screw cap", [ev(4), ev(4, "image")]),
            field("atmosphere", None),
            field("workup", workup, ee if workup else ()),
            field("purification", purification, ee if purification else ()),
        ],
    }]
    if not any(o["name"] == "compound_specific_reported_yield" for o in record["outcomes"]):
        record["outcomes"].append(
            field("compound_specific_reported_yield", q(detail_yield, "%"), ee, ["product"])
        )
    record["review"]["unresolved"] = [
        "Yield measurement basis and atmosphere are not explicitly stated in the compound-specific paragraph.",
        "Complex substrate/product connectivity and stereochemistry remain unverified.",
        "No supporting-information source was supplied or associated.",
    ]
    if workup and purification is None:
        record["review"]["unresolved"].append(
            "The source reports that workup afforded pure product but does not state a separate chromatographic purification."
        )


data = json.loads((BASE / "dataset.json").read_text())
existing = {r["source_reaction_id"]: r for r in data["experiments"]}
records = []


def take(source_reaction_id):
    record = copy.deepcopy(existing[source_reaction_id])
    records.append(record)
    return record


# Page 7 starts with characterization continuing from the page-6 Z-5ad paragraph.
r = take("table3_entry3_z5ad")
add_page(r, 7)
r["review"]["unresolved"] = [
    "Yield measurement basis, atmosphere, workup, and purification are not stated for this abbreviated preparation.",
    "Complex structures and stereochemistry remain unverified.",
    "No supporting-information source was supplied or associated.",
]


table3_page7 = {
    "table3_entry4_z5ae": (
        [("substrate", 43, 0.25), ("allene", 61, 0.50), ("lithium_bromide", 53, 0.50),
         ("benzoquinone", 41, 0.375), ("palladium_acetate", 1, 0.0045)], 7, 65, 70
    ),
    "table3_entry5_z5af": (
        [("substrate", 43, 0.25), ("allene", 58, 0.50), ("lithium_bromide", 53, 0.50),
         ("benzoquinone", 41, 0.375), ("palladium_acetate", 1, 0.0045)], 6.5, 80, 88
    ),
    "table3_entry6_z5ag": (
        [("substrate", 43, 0.25), ("allene", 65, 0.50), ("lithium_bromide", 53, 0.50),
         ("benzoquinone", 41, 0.375), ("palladium_acetate", 1, 0.0045)], 5.5, 58, 61
    ),
    "table3_entry7_z5db": (
        [("substrate", 70, 0.25), ("allene", 62, 0.50), ("lithium_bromide", 53, 0.50),
         ("benzoquinone", 41, 0.375), ("palladium_acetate", 1, 0.0045)], 6, 69, 57
    ),
    "table3_entry8_z5ic": (
        [("substrate", 47, 0.25), ("allene", 69, 0.50), ("lithium_bromide", 53, 0.50),
         ("benzoquinone", 41, 0.375), ("palladium_acetate", 1, 0.0045)], 18.5, 50, 50
    ),
    "table3_entry9_z5jd": (
        [("substrate", 52, 0.26), ("allene", 76, 0.50), ("lithium_bromide", 53, 0.50),
         ("benzoquinone", 41, 0.375), ("palladium_acetate", 1, 0.0045)], 10, 62, 56
    ),
}
for rid, (values, time, product_mass, yld) in table3_page7.items():
    set_scope_details(take(rid), 7, values, time, product_mass, yld)


# Table 4 rows are completed by compound-specific paragraphs on pages 7 and 8.
table4_details = {
    "table4_entry1_z5ah": (
        7,
        [("substrate", 43, 0.25), ("allene", 92, 0.50), ("lithium_bromide", 53, 0.50),
         ("benzoquinone", 41, 0.375), ("palladium_acetate", 1, 0.0045)],
        6, 63, 58,
        "Dissolved in CH2Cl2 (30 mL), washed with water (5 mL x 3), dried over Na2SO4, and evaporated to afford pure Z-5ah.",
        None,
    ),
    "table4_entry2_z5ai": (
        7,
        [("substrate", 44, 0.25), ("allene", 106, 0.50), ("lithium_bromide", 53, 0.50),
         ("benzoquinone", 41, 0.375), ("palladium_acetate", 1, 0.0045)],
        6, 71, 60, None, None,
    ),
    "table4_entry3_z5aj": (
        8,
        [("substrate", 44, 0.25), ("allene", 63, 0.50), ("lithium_bromide", 53, 0.50),
         ("benzoquinone", 41, 0.375), ("palladium_acetate", 1, 0.0045)],
        6, 64, 67, None, None,
    ),
    "table4_entry4_z5fj": (
        8,
        [("substrate", 56, 0.25), ("allene", 62, 0.49), ("lithium_bromide", 53, 0.50),
         ("benzoquinone", 41, 0.375), ("palladium_acetate", 1, 0.0045)],
        10, 69, 64, None, None,
    ),
    "table4_entry5_z5ak": (
        8,
        [("substrate", 44, 0.25), ("allene", 106, 0.50), ("lithium_bromide", 53, 0.50),
         ("benzoquinone", 41, 0.375), ("palladium_acetate", 1, 0.0045)],
        6, 87, 74,
        "After TLC showed complete consumption, solvent was evaporated; residue was dissolved in CH2Cl2 (50 mL), washed with water (5 mL x 4), dried over Na2SO4, and evaporated.",
        "Flash chromatography on silica gel.",
    ),
}
for rid, (page, values, time, product_mass, yld, workup, purification) in table4_details.items():
    rec = take(rid)
    set_scope_details(rec, page, values, time, product_mass, yld, workup=workup, purification=purification)
    if rid == "table4_entry5_z5ak":
        rec["notes"].append(fact(
            "The compound heading names an alpha-naphthyl product, while the paragraph uses substrate 1a and reports formula C24H21NO4Br; the conflict is retained without choosing a structure.",
            evidence(8),
        ))
        rec["review"]["unresolved"].append(
            "The Z-5ak heading/substrate/formula identity conflict requires expert source review."
        )


# Table 5: retain table values and add the exact compound-specific values.
table5_details = {
    "table5_entry1_rz5aa": ("allene", 48, 0.50, 44, 0.25, 59, 67, 98),
    "table5_entry2_rz5ab": ("allene", 62, 0.50, 43, 0.25, 60, 63, 98),
    "table5_entry3_rz5aj": ("allene", 63, 0.50, 43, 0.25, 66, 70, 98),
    "table5_entry4_rz5af": ("allene", 58, 0.50, 44, 0.25, 75, 80, 97),
}
for rid, (_, allene_mass, allene_amount, substrate_mass, substrate_amount, product_mass, detail_yield, product_ee) in table5_details.items():
    rec = take(rid)
    add_page(rec, 8)
    ee = evidence(8)
    pp = by_participant(rec)
    pp["substrate"]["amounts"] = exact_amounts(8, substrate_mass, substrate_amount) + [
        field("starting_material_ee", q(98, "%"), ee)
    ]
    pp["allene"]["amounts"] = exact_amounts(8, allene_mass, allene_amount)
    pp["lithium_bromide"]["amounts"] = exact_amounts(8, 53, 0.50)
    pp["benzoquinone"]["amounts"] = exact_amounts(8, 41, 0.375)
    pp["palladium_acetate"]["amounts"] = exact_amounts(8, 1, 0.0045) + [
        field("catalyst_loading", q(2, "mol%"), ee)
    ]
    pp["hoac"]["amounts"] = [field("volume", q(2, "mL"), ee)]
    pp["product"]["amounts"] = [field("isolated_mass", q(product_mass, "mg"), ee)]
    rec["steps"] = [{
        "step_id": "enantioenriched_cyclization",
        "participant_ids": [p["entity_id"] for p in rec["participants"]],
        "conditions": [
            field("time", q(6, "h"), ee),
            field("temperature", q(60, "°C"), ee),
            field("operation", "Schlenk tube with screw cap", [ev(4), ev(4, "image")]),
            field("atmosphere", None),
            field("workup", None),
            field("purification", None),
        ],
    }]
    rec["outcomes"] = [o for o in rec["outcomes"] if o["name"] not in {
        "compound_specific_reported_yield", "product_ee_measurement_basis"
    }]
    rec["outcomes"].append(field("compound_specific_reported_yield", q(detail_yield, "%"), ee, ["product"]))
    rec["outcomes"].append(field("product_ee_measurement_basis", "chiral HPLC", ee, ["product"]))
    # Retain the product-ee value with direct detailed-procedure evidence.
    for outcome in rec["outcomes"]:
        if outcome["name"] == "product_ee":
            outcome["fact"] = fact(q(product_ee, "%"), ee)
    rec["review"]["unresolved"] = [
        "Yield basis, atmosphere, workup, and purification are not stated in the compound-specific paragraph.",
        "Absolute/axial stereochemical structures remain unverified.",
        "No supporting-information source was supplied or associated.",
    ]
    if rid in {"table5_entry1_rz5aa", "table5_entry2_rz5ab"}:
        rec["notes"].append(fact(
            "The Table 5 yield and the compound-specific experimental yield differ; both source values are retained.",
            [ev(4), ev(4, "image"), ev(8), ev(8, "image")],
        ))
        rec["review"]["unresolved"].append(
            "Table 5 versus compound-specific yield conflict requires expert review."
        )


# Page 8 gives the complete LiCl experiment and corrects the earlier provisional stoichiometry.
r = take("equation1_licl_halide_exchange")
add_page(r, 8)
ee8 = evidence(8)
old = by_participant(r)
r["participants"] = [
    participant("z5aa_start", "reactant", "Z-5aa", ee8, amounts=exact_amounts(8, 100, 0.29)),
    participant("licl", "reagent", "LiCl", ee8, name="lithium chloride", smiles="[Li+].[Cl-]", amounts=exact_amounts(8, 49, 1.16)),
    participant("thf", "solvent", "THF", ee8, name="tetrahydrofuran", smiles="C1CCOC1", amounts=[field("volume", q(4, "mL"), ee8)]),
    participant("water", "solvent", "distilled H2O", ee8, name="water", smiles="O", amounts=[field("volume", q(4, "mL"), ee8)]),
    copy.deepcopy(old["z5aa_product"]),
    copy.deepcopy(old["z5aa_chloride"]),
]
r["steps"] = [{
    "step_id": "halide_exchange",
    "participant_ids": [p["entity_id"] for p in r["participants"]],
    "conditions": [
        field("temperature", q(40, "°C"), ee8),
        field("time", q(5.5, "h"), ee8),
        field("atmosphere", None),
        field("workup", None),
        field("purification", None),
    ],
}]
r["outcomes"] = [
    field("combined_reported_yield", q(100, "%"), [ev(3), ev(3, "image")], ["z5aa_product", "z5aa_chloride"]),
    field("combined_product_mass", q(101, "mg"), ee8, ["z5aa_product", "z5aa_chloride"]),
    field("product_ratio", "Z-5aa:Z-5AA = 1:1", ee8, ["z5aa_product", "z5aa_chloride"]),
    field("yield_measurement_basis", None, (), ["z5aa_product", "z5aa_chloride"]),
]
r["review"]["unresolved"] = [
    "Atmosphere, workup, purification, and yield measurement basis are not reported.",
    "Product structures remain unverified.",
]


def set_amounts(record, entity_id, values, page):
    pp = by_participant(record)
    pp[entity_id]["amounts"] = [field(name, value, evidence(page)) for name, value in values]


# Synthetic applications 1 and 2 on page 8.
r = take("scheme4_diethylamine_substitution")
add_page(r, 8)
set_amounts(r, "start", [("mass", q(59, "mg")), ("amount", q(0.17, "mmol"))], 8)
set_amounts(r, "et2nh", [("mass", q(25, "mg")), ("amount", q(0.34, "mmol"))], 8)
set_amounts(r, "k2co3", [("mass", q(47, "mg")), ("amount", q(0.34, "mmol"))], 8)
set_amounts(r, "solvent", [("volume", q(2, "mL"))], 8)
set_amounts(r, "z10", [("isolated_mass", q(38, "mg"))], 8)
r["steps"] = [{
    "step_id": "diethylamine_substitution",
    "participant_ids": [p["entity_id"] for p in r["participants"]],
    "conditions": [
        field("temperature", "r.t.", evidence(8)), field("time", q(6, "h"), evidence(8)),
        field("atmosphere", "argon", evidence(8)),
        field("operation", "Schlenk tube with screw cap; TLC monitoring to complete consumption", evidence(8)),
        field("workup", "Quenched with H2O (5 mL), extracted with ether (50 mL), washed with brine, dried over Na2SO4, evaporated, and analyzed by 1H NMR.", evidence(8)),
        field("purification", "Flash chromatography on silica gel.", evidence(8)),
    ],
}]
r["outcomes"] = [
    field("isolated_yield", q(66, "%"), evidence(8), ["z10"]),
    field("yield_measurement_basis", "isolated after flash chromatography", evidence(8), ["z10"]),
]
r["review"]["unresolved"] = ["Product connectivity/stereochemistry remain unverified.", "No SI source was supplied or associated."]

r = take("scheme4_benzenesulfinate_substitution")
add_page(r, 8)
set_amounts(r, "start", [("mass", q(54, "mg")), ("amount", q(0.15, "mmol"))], 8)
pp = by_participant(r)
pp["phso2na"]["label"] = fact("PhSO2Na.2H2O", evidence(8))
pp["phso2na"]["name"] = fact("sodium benzenesulfinate dihydrate", evidence(8))
set_amounts(r, "phso2na", [("mass", q(60, "mg")), ("amount", q(0.30, "mmol"))], 8)
set_amounts(r, "solvent", [("volume", q(2, "mL"))], 8)
set_amounts(r, "z11", [("isolated_mass", q(59, "mg"))], 8)
r["steps"] = [{
    "step_id": "benzenesulfinate_substitution",
    "participant_ids": [p["entity_id"] for p in r["participants"]],
    "conditions": [
        field("temperature", q(-22, "°C"), evidence(8)), field("time", q(2.5, "h"), evidence(8)),
        field("atmosphere", "argon", evidence(8)), field("operation", "TLC monitoring to complete consumption", evidence(8)),
        field("workup", "Diluted with ether (60 mL), washed sequentially with H2O and brine, dried over Na2SO4, evaporated, and analyzed by 1H NMR.", evidence(8)),
        field("purification", "Flash chromatography on silica gel.", evidence(8)),
    ],
}]
r["outcomes"] = [
    field("isolated_yield", q(93, "%"), evidence(8), ["z11"]),
    field("yield_measurement_basis", "isolated after flash chromatography", evidence(8), ["z11"]),
]
r["review"]["unresolved"] = ["Product connectivity/stereochemistry remain unverified.", "No SI source was supplied or associated."]


# Page 9 completes synthetic applications 3-6.
r = take("scheme4_borohydride_reduction")
add_page(r, 9)
set_amounts(r, "start", [("mass", q(69, "mg")), ("amount", q(0.20, "mmol"))], 9)
set_amounts(r, "nabh4", [("mass", q(15, "mg")), ("amount", q(0.40, "mmol"))], 9)
set_amounts(r, "solvent", [("volume", q(3, "mL"))], 9)
set_amounts(r, "e12", [("isolated_mass", q(38, "mg"))], 9)
r["steps"] = [{
    "step_id": "borohydride_reduction",
    "participant_ids": [p["entity_id"] for p in r["participants"]],
    "conditions": [
        field("temperature", q(18, "°C"), evidence(9)), field("time", q(50, "min"), evidence(9)),
        field("atmosphere", "argon", evidence(9)), field("operation", "TLC monitoring to complete consumption", evidence(9)),
        field("workup", "Diluted with ether (60 mL), washed sequentially with H2O and brine, dried over Na2SO4, evaporated, and analyzed by 1H NMR.", evidence(9)),
        field("purification", "Flash chromatography on silica gel.", evidence(9)),
    ],
}]
r["outcomes"] = [
    field("isolated_yield", q(71, "%"), evidence(9), ["e12"]),
    field("yield_measurement_basis", "isolated after flash chromatography", evidence(9), ["e12"]),
    field("regioselectivity_ratio", "1/15", evidence(9), ["e12"]),
    field("E_to_Z_ratio", ">=22/1", evidence(9), ["e12"]),
]
r["notes"].append(fact("Selectivity expressions are preserved in the source orientation: regioselectivity 1/15 and E/Z >= 22/1.", evidence(9)))
r["review"]["unresolved"] = ["The identities corresponding to the two regioselectivity terms are not named in the paragraph.", "Product structure/stereochemistry remain unverified.", "No SI source was supplied or associated."]


def add_grignard_solvents(record):
    record["participants"].extend([
        participant("toluene_in_grignard_solution", "solvent", "toluene (CH3MgBr solution)", evidence(9), smiles="Cc1ccccc1"),
        participant("thf_in_grignard_solution", "solvent", "THF (CH3MgBr solution)", evidence(9), smiles="C1CCOC1"),
    ])


def grignard_record(rid, start_mass, start_amount, catalyst_mass, catalyst_amount, dcm_volume,
                    grignard_volume, grignard_amount, product_mass, yld, regio, dr):
    rec = take(rid)
    add_page(rec, 9)
    set_amounts(rec, "start", [("mass", q(start_mass, "mg")), ("amount", q(start_amount, "mmol"))], 9)
    set_amounts(rec, "cubr", [("mass", q(catalyst_mass, "mg")), ("amount", q(catalyst_amount, "mmol"))], 9)
    by_participant(rec)["cubr"]["amounts"].append(
        field("catalyst_loading", q(5, "mol%"), [ev(5), ev(5, "image")])
    )
    set_amounts(rec, "solvent", [("volume", q(dcm_volume, "mL"))], 9)
    set_amounts(rec, "ch3mgbr", [("solution_volume", q(grignard_volume, "mL")), ("concentration", q(1.4, "M")), ("amount", q(grignard_amount, "mmol"))], 9)
    product_id = "p13a" if rid.endswith("13a") else "p13b"
    set_amounts(rec, product_id, [("isolated_mass", q(product_mass, "mg"))], 9)
    add_grignard_solvents(rec)
    rec["steps"] = [{
        "step_id": "copper_catalyzed_grignard_substitution",
        "participant_ids": [p["entity_id"] for p in rec["participants"]],
        "conditions": [
            field("temperature", q(-78, "°C"), evidence(9)), field("time", q(30, "min"), evidence(9)),
            field("atmosphere", "argon", evidence(9)),
            field("operation", "CH3MgBr solution was added by syringe at -78 °C; solution solvent toluene/THF = 75/25.", evidence(9)),
            field("workup", "H2O (0.5 mL) was added at -78 °C; mixture was warmed to room temperature, filtered through a short silica-gel column, evaporated, and analyzed by 1H NMR.", evidence(9)),
            field("purification", "Flash chromatography on silica gel.", evidence(9)),
        ],
    }]
    rec["outcomes"] = [
        field("isolated_yield", q(yld, "%"), evidence(9), [product_id]),
        field("yield_measurement_basis", "isolated after flash chromatography", evidence(9), [product_id]),
        field("regioselectivity_ratio", regio, evidence(9), [product_id]),
        field("diastereomeric_ratio", dr, evidence(9), [product_id]),
    ]
    rec["review"]["unresolved"] = ["Product connectivity and relative stereochemistry remain unverified.", "No SI source was supplied or associated."]


grignard_record("scheme4_grignard_substitution_13a", 70, 0.20, 2, 0.01, 4, 0.36, 0.50, 51, 90, "18/1", "25/1")
grignard_record("scheme4_grignard_substitution_13b", 54, 0.135, 1, 0.005, 3, 0.24, 0.34, 36, 80, ">25/1", ">50/1")


r = take("scheme4_bromination_14ba_14bb")
add_page(r, 9)
set_amounts(r, "start", [("mass", q(30, "mg")), ("amount", q(0.09, "mmol"))], 9)
set_amounts(r, "br2", [("solution_volume", q(0.36, "mL")), ("concentration", q(0.50, "M"))], 9)
set_amounts(r, "solvent", [("reaction_volume", q(2, "mL")), ("extraction_volume", q(30, "mL"))], 9)
set_amounts(r, "p14ba", [("isolated_mass", q(6, "mg"))], 9)
set_amounts(r, "p14bb", [("isolated_mass", q(34, "mg"))], 9)
r["participants"].append(participant(
    "sodium_thiosulfate", "reagent", "aqueous saturated Na2S2O3", evidence(9),
    name="sodium thiosulfate", amounts=[field("amount", "minimal amount until excess Br2 color disappeared", evidence(9))]
))
r["steps"] = [{
    "step_id": "bromination",
    "participant_ids": [p["entity_id"] for p in r["participants"]],
    "conditions": [
        field("temperature", "r.t.", evidence(9)), field("time", q(5, "h"), evidence(9)),
        field("atmosphere", None), field("operation", "TLC monitoring to complete consumption", evidence(9)),
        field("workup", "Added minimal saturated aqueous Na2S2O3 until excess Br2 color disappeared; extracted with CH2Cl2 (30 mL), dried over anhydrous Na2SO4, and evaporated.", evidence(9)),
        field("purification", "Flash chromatography on silica gel; petroleum ether/ethyl acetate = 20:1.", evidence(9)),
    ],
}]
r["outcomes"] = [
    field("isolated_yield_14ba", q(14, "%"), evidence(9), ["p14ba"]),
    field("isolated_yield_14bb", q(77, "%"), evidence(9), ["p14bb"]),
    field("yield_measurement_basis", "isolated after flash chromatography", evidence(9), ["p14ba", "p14bb"]),
]
r["review"]["unresolved"] = [
    "Reaction atmosphere is not reported.",
    "Product connectivity and the relative stereochemical assignments remain unverified; Figure 2 on page 5 is supporting evidence, not a separate reaction.",
    "No SI source was supplied or associated.",
]


assert len(records) == 23
out = BASE / "raw_model" / "records_pages_0007_0009.json"
out.write_text(json.dumps(records, ensure_ascii=False, indent=2))


def full_id(source_reaction_id):
    return f"{DOC}:{source_reaction_id}"


page7_ids = [
    full_id("table3_entry3_z5ad"), full_id("table3_entry4_z5ae"), full_id("table3_entry5_z5af"),
    full_id("table3_entry6_z5ag"), full_id("table3_entry7_z5db"), full_id("table3_entry8_z5ic"),
    full_id("table3_entry9_z5jd"), full_id("table4_entry1_z5ah"), full_id("table4_entry2_z5ai"),
]
page8_ids = [
    full_id("table4_entry3_z5aj"), full_id("table4_entry4_z5fj"), full_id("table4_entry5_z5ak"),
    full_id("table5_entry1_rz5aa"), full_id("table5_entry2_rz5ab"), full_id("table5_entry3_rz5aj"),
    full_id("table5_entry4_rz5af"), full_id("equation1_licl_halide_exchange"),
    full_id("scheme4_diethylamine_substitution"), full_id("scheme4_benzenesulfinate_substitution"),
]
page9_ids = [
    full_id("scheme4_borohydride_reduction"), full_id("scheme4_grignard_substitution_13a"),
    full_id("scheme4_grignard_substitution_13b"), full_id("scheme4_bromination_14ba_14bb"),
]
coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 7,
            "state": "attempted",
            "regions": [
                {
                    "region": "upper-left continuation of experimental paragraph 11",
                    "finding": "Characterization for Z-5ad continues from page 6; associated with Table 3 entry 3 and not counted as a new experiment.",
                    "evidence_ids": [ev(7, "image"), ev(7)],
                },
                {
                    "region": "left column, experimental paragraphs 12-15",
                    "finding": "Exact preparations of Z-5ae, Z-5af, Z-5ag, and Z-5db merged into Table 3 entries 4-7.",
                    "evidence_ids": [ev(7, "image"), ev(7)],
                },
                {
                    "region": "right column, experimental paragraphs 16-19",
                    "finding": "Exact preparations of Z-5ic, Z-5jd, Z-5ah, and Z-5ai merged into Table 3 entries 8-9 and Table 4 entries 1-2.",
                    "evidence_ids": [ev(7, "image"), ev(7)],
                },
            ],
            "record_ids": page7_ids,
            "unresolved": [
                "Most abbreviated preparations do not state atmosphere, workup, purification, or yield measurement basis.",
                "Complex structures and stereochemistry remain unverified.",
            ],
        },
        {
            "page": 8,
            "state": "attempted",
            "regions": [
                {
                    "region": "left column, experimental paragraphs 20-22",
                    "finding": "Exact preparations of Z-5aj, Z-5fj, and Z-5ak merged into Table 4 entries 3-5; the Z-5ak heading/substrate/formula identity conflict is retained.",
                    "evidence_ids": [ev(8, "image"), ev(8)],
                },
                {
                    "region": "lower-left through upper-right, optically active typical procedure paragraphs 1-4",
                    "finding": "Four enantioenriched cyclizations merged into Table 5 entries 1-4 with exact quantities, product masses, yields, ee, and HPLC measurement basis.",
                    "evidence_ids": [ev(8, "image"), ev(8)],
                },
                {
                    "region": "middle-right, The Reaction of Z-5aa with LiCl",
                    "finding": "Detailed LiCl halide-exchange procedure merged into equation 1, replacing the earlier provisional stoichiometry and filling time and solvent volumes.",
                    "evidence_ids": [ev(8, "image"), ev(8)],
                },
                {
                    "region": "lower-right, Synthetic Application paragraphs 1-2",
                    "finding": "Detailed Z-10 and Z-11 substitution procedures merged into the two corresponding Scheme 4 records.",
                    "evidence_ids": [ev(8, "image"), ev(8)],
                },
            ],
            "record_ids": page8_ids,
            "unresolved": [
                "Table 5 and the detailed paragraphs disagree for the first two yields: 63% versus 67%, and 67% versus 63%.",
                "The Z-5ak heading names an alpha-naphthyl product although the paragraph uses 1a and reports formula C24H21NO4Br.",
                "Several abbreviated cyclizations omit atmosphere, workup, purification, and yield basis.",
            ],
        },
        {
            "page": 9,
            "state": "attempted",
            "regions": [
                {
                    "region": "left column, Synthetic Application paragraphs 3-5",
                    "finding": "Detailed NaBH4 reduction and two substrate-specific Cu-catalyzed Grignard substitutions merged into the corresponding Scheme 4 records.",
                    "evidence_ids": [ev(9, "image"), ev(9)],
                },
                {
                    "region": "upper-right, Synthetic Application paragraph 6",
                    "finding": "Detailed bromination of 13b, including workup, chromatographic separation, and separate 14ba/14bb yields, merged into the existing Scheme 4 bromination record.",
                    "evidence_ids": [ev(9, "image"), ev(9)],
                },
                {
                    "region": "lower-right acknowledgments and Supporting Information Available statement",
                    "finding": "No additional reaction; the paper states that SI exists online, but no SI file is supplied or explicitly associated in this workspace.",
                    "evidence_ids": [ev(9, "image"), ev(9)],
                },
            ],
            "record_ids": page9_ids,
            "unresolved": [
                "The E-12 paragraph reports regioselectivity as 1/15 without naming the two regioisomers.",
                "Bromination atmosphere is not reported.",
                "SI is mentioned but was not supplied or associated; no SI facts were inferred.",
                "Complex product connectivity and stereochemical assignments remain unverified.",
            ],
        },
    ],
}
coverage_path = BASE / "coverage" / "pages_0007_0009.json"
coverage_path.write_text(json.dumps(coverage, ensure_ascii=False, indent=2))

tasks_path = BASE / "tasks.json"
tasks = json.loads(tasks_path.read_text())
for task in tasks:
    if task["document_id"] == DOC and task["evidence_id"] in {ev(7), ev(8), ev(9)}:
        task["state"] = "attempted"
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2))

print(json.dumps({
    "updated_records": len(records),
    "coverage_pages": [p["page"] for p in coverage["pages"]],
    "records_output": str(out),
    "coverage_output": str(coverage_path),
}, ensure_ascii=False))
