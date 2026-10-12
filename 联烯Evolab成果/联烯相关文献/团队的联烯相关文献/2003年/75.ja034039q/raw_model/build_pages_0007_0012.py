#!/usr/bin/env python3
"""Build evidence-linked records for source.pdf pages 7-12.

The pages are the detailed experimental section.  Records already introduced
on pages 1-6 are enriched under their existing record IDs; only previously
unrepresented starting-material preparations receive new IDs.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path

DOC = "doc_eae2cf05b16fe8b6"
BASE = Path(__file__).resolve().parents[1]
DATASET = BASE / "dataset.json"
OUT = Path(__file__).with_name("extracted_records_pages_0007_0012.json")
COVERAGE = BASE / "coverage" / "pages_0007_0012.json"
TASKS = BASE / "tasks.json"


def evidence(*pages: int) -> list[str]:
    return [f"{DOC}:page{page}:{kind}" for page in pages for kind in ("text", "image")]


def fact(value, pages=(7,)):
    return {
        "value": value,
        "evidence_ids": evidence(*pages) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def field(name, value, pages=(7,), targets=None):
    item = {"name": name, "fact": fact(value, pages)}
    if targets:
        item["target_entity_ids"] = list(targets)
    return item


def q(number, unit, **extra):
    value = {"number": number, "unit": unit}
    value.update(extra)
    return value


SMILES = {
    "triethylamine": "CCN(CC)CC",
    "benzenesulfinyl chloride": "O=S(Cl)c1ccccc1",
    "dichloromethane": "ClCCl",
    "iodine": "[I][I]",
    "bromine": "BrBr",
    "water": "O",
    "acetonitrile": "CC#N",
    "acetone": "CC(C)=O",
    "THF": "C1CCOC1",
    "DMF": "CN(C)C=O",
    "DMSO": "CS(C)=O",
    "lithium acetate dihydrate": "[Li+].CC(=O)[O-].O.O",
    "copper(II) bromide": "[Cu+2].[Br-].[Br-]",
    "copper(II) chloride dihydrate": "[Cu+2].[Cl-].[Cl-].O.O",
    "NBS": "O=C1CCC(=O)N1Br",
    "sodium iodide": "[Na+].[I-]",
    "acetic acid": "CC(=O)O",
    "hydrogen peroxide": "OO",
    "sodium acetate": "[Na+].CC(=O)[O-]",
    "acetic anhydride": "CC(=O)OC(C)=O",
    "potassium carbonate": "[K+].[K+].[O-]C([O-])=O",
    "TBAB": "CCCC[N+](CCCC)(CCCC)CCCC.[Br-]",
    "propargyl alcohol": "C#CCO",
    "1a": "C=C=C[S](=O)c1ccccc1",
}


def amount_fields(items, pages):
    return [field(name, value, pages) for name, value in items]


def participant(entity_id, role, label, pages=(7,), *, name=None, smiles=None, amounts=()):
    if smiles is None:
        smiles = SMILES.get(name or label)
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, pages),
        "name": fact(name, pages) if name is not None else fact(None),
        "smiles": fact(smiles, pages) if smiles is not None else fact(None),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": amount_fields(amounts, pages),
    }


def record(rid, kind, pages, participants, steps, outcomes, unresolved, notes=()):
    return {
        "record_id": f"{DOC}:{rid}",
        "document_id": DOC,
        "source_reaction_id": rid,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": evidence(*pages),
        "participants": participants,
        "steps": steps,
        "outcomes": outcomes,
        "notes": [fact(note, pages) for note in notes],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": list(unresolved),
        },
    }


dataset = json.loads(DATASET.read_text())
existing = {r["record_id"].split(":", 1)[1]: r for r in dataset["experiments"]}
records = []


def clone(rid, *pages):
    rec = copy.deepcopy(existing[rid])
    rec["status"] = "candidate"
    rec["evidence_ids"] = list(dict.fromkeys(rec["evidence_ids"] + evidence(*pages)))
    rec["review"]["method"] = "none"
    rec["review"]["reviewer"] = None
    rec["review"]["checked_fields"] = []
    return rec


def product_id(rec):
    return next(p["entity_id"] for p in rec["participants"] if p["role"] == "product")


def find_part(rec, label):
    return next(p for p in rec["participants"] if p["label"]["value"] == label)


def set_amounts(rec, label, items, pages):
    find_part(rec, label)["amounts"] = amount_fields(items, pages)


def add_part(rec, entity_id, role, label, pages, *, name=None, smiles=None, amounts=()):
    if any(p["entity_id"] == entity_id for p in rec["participants"]):
        return
    rec["participants"].append(participant(entity_id, role, label, pages, name=name, smiles=smiles, amounts=amounts))


def set_outcome(rec, name, value, pages, targets=True):
    target_ids = [product_id(rec)] if targets else None
    rec["outcomes"] = [o for o in rec["outcomes"] if o["name"] != name]
    rec["outcomes"].append(field(name, value, pages, target_ids))


def add_condition(rec, name, value, pages, step_id=None):
    step = rec["steps"][0] if step_id is None else next(s for s in rec["steps"] if s["step_id"] == step_id)
    step["conditions"] = [c for c in step["conditions"] if c["name"] != name]
    step["conditions"].append(field(name, value, pages))


def append_common_unresolved(rec, *items):
    rec["review"]["unresolved"] = list(dict.fromkeys([
        *items,
        "Supporting information was not supplied or explicitly associated.",
        "Molecular structures and stereochemical assignments remain machine-unverified.",
    ]))


# Pages 7-8: eighteen individual sulfinyl-allene starting-material preparations.
starting_materials = [
    # letter, record id, page, reactant label, reactant amounts, Et3N amounts,
    # sulfinyl chloride amounts, product label/name, product amounts, yield, extras
    ("a", "starting_material_1a", 7, "propargyl alcohol", [("mass", q(3.08, "g")), ("amount", q(55, "mmol"))], [("mass", q(5.05, "g")), ("amount", q(55, "mmol"))], [("mass", q(7.23, "g")), ("amount", q(50, "mmol"))], "1a", "1,2-propadienyl phenyl sulfoxide", [("product_mass", q(6.75, "g"))], 82, []),
    ("b", "starting_material_1b", 7, "but-3-yn-2-ol", [("mass", q(4.97, "g")), ("amount", q(71, "mmol"))], [("mass", q(7.2, "g")), ("amount", q(71, "mmol"))], [("mass", q(9.35, "g")), ("amount", q(64.6, "mmol"))], "1b", "1,2-butadienyl phenyl sulfoxide", [("product_mass", q(8.684, "g"))], 76, []),
    ("c", "starting_material_1c", 7, "hept-1-yn-3-ol", [("mass", q(6.09, "g")), ("amount", q(54, "mmol"))], [("mass", q(5.05, "g")), ("amount", q(50, "mmol"))], [("mass", q(7.23, "g")), ("amount", q(50, "mmol"))], "1c", "1,2-heptadienyl phenyl sulfoxide", [("product_mass", q(8.08, "g"))], 73, []),
    ("d", "scheme10_starting_material_a", 7, "(R)-hept-1-yn-3-ol", [("mass", q(240, "mg")), ("amount", q(2, "mmol")), ("starting_material_ee", q(96, "%"))], [("volume", q(0.27, "mL")), ("mass", q(200, "mg")), ("amount", q(2, "mmol"))], [("mass", q(290, "mg")), ("amount", q(2, "mmol"))], "(R)-1c", "(R)-1,2-heptadienyl phenyl sulfoxide", [("product_mass", q(370, "mg"))], 84, [("product_ee", q(95.5, "%")), ("diastereomer_ratio", "70:30")]),
    ("e", "starting_material_1d", 7, "undec-1-yn-3-ol", [("mass", q(5.04, "g")), ("amount", q(30, "mmol"))], [("mass", q(3.34, "g")), ("amount", q(33, "mmol"))], [("mass", q(4.77, "g")), ("amount", q(33, "mmol"))], "1d", "1,2-undecadienyl phenyl sulfoxide", [("product_mass", q(7.03, "g"))], 85, []),
    ("f", "scheme10_starting_material_b", 7, "(S)-undec-1-yn-3-ol", [("mass", q(840, "mg")), ("amount", q(5, "mmol")), ("starting_material_ee", q(95.7, "%"))], [("mass", q(505, "mg")), ("amount", q(5, "mmol"))], [("mass", q(723, "mg")), ("amount", q(5, "mmol"))], "(S)-1d", "(S)-1,2-undecadienyl phenyl sulfoxide", [("product_mass", q(1.18, "g"))], 86, [("product_ee", q(95.7, "%")), ("diastereomer_ratio", "61:39")]),
    ("g", "starting_material_1e", 7, "4,4-dimethylpent-1-yn-3-ol", [("mass", q(2.24, "g")), ("amount", q(20, "mmol"))], [("mass", q(2.22, "g")), ("amount", q(22, "mmol"))], [("mass", q(3.18, "g")), ("amount", q(22, "mmol"))], "1e", "4,4-dimethylpenta-1,2-dienyl phenyl sulfoxide", [("product_mass", q(3.68, "g"))], 84, []),
    ("h", "scheme10_starting_material_c", 7, "(S)-4,4-dimethylpent-1-yn-3-ol", [("mass", q(448, "mg")), ("amount", q(4, "mmol")), ("starting_material_ee", q(99, "%", qualifier="gt", raw_text=">99%"))], [("mass", q(400, "mg")), ("amount", q(4, "mmol"))], [("mass", q(578, "mg")), ("amount", q(4, "mmol"))], "(S)-1e", "(S)-4,4-dimethylpenta-1,2-dienyl phenyl sulfoxide", [("product_mass", q(787, "mg"))], 89, [("product_ee", q(99, "%", qualifier="gt", raw_text=">99%")), ("diastereomer_ratio", "92:8")]),
    ("i", "starting_material_1f", 7, "2-methyl-but-3-yn-2-ol", [("mass", q(2.10, "g")), ("amount", q(25, "mmol"))], [("mass", q(2.53, "g")), ("amount", q(25, "mmol"))], [("mass", q(3.62, "g")), ("amount", q(25, "mmol"))], "1f", "3-methylbuta-1,2-dienyl phenyl sulfoxide", [("product_mass", q(3.50, "g"))], 73, []),
    ("j", "starting_material_1g", 7, "1-ethynylcyclohexanol", [("mass", q(4.10, "g")), ("amount", q(33, "mmol"))], [("mass", q(3.34, "g")), ("amount", q(33, "mmol"))], [("mass", q(4.77, "g")), ("amount", q(33, "mmol"))], "1g", "2-(cyclohexylideneethenyl)phenyl sulfoxide", [("product_mass", q(6.72, "g"))], 88, []),
    ("k", "starting_material_1h", 7, "hept-2-yn-1-ol", [("mass", q(5.68, "g")), ("amount", q(51, "mmol"))], [("mass", q(5.13, "g")), ("amount", q(51, "mmol"))], [("mass", q(7.33, "g")), ("amount", q(51, "mmol"))], "1h", "1,2-heptadien-3-yl phenyl sulfoxide", [("product_mass", q(9.42, "g"))], 85, []),
    ("l", "starting_material_1i", 7, "3-phenylprop-2-yn-1-ol", [("mass", q(3.68, "g")), ("amount", q(28, "mmol"))], [("mass", q(2.83, "g")), ("amount", q(28, "mmol"))], [("mass", q(4.05, "g")), ("amount", q(28, "mmol"))], "1i", "1-phenylpropadienyl phenyl sulfoxide", [("product_mass", q(5.76, "g"))], 86, []),
    ("m", "starting_material_1j", 7, "2-methyl-oct-3-yn-2-ol", [("mass", q(2.53, "g")), ("amount", q(18, "mmol"))], [("mass", q(1.99, "g")), ("amount", q(20, "mmol"))], [("mass", q(2.86, "g")), ("amount", q(20, "mmol"))], "1j", "2-methylocta-2,3-dien-4-yl phenyl sulfoxide", [("product_mass", q(4.04, "g"))], 90, []),
    ("n", "starting_material_1k", 8, "hept-6-en-1-yn-3-ol", [("mass", q(2.59, "g")), ("amount", q(23, "mmol"))], [("mass", q(2.29, "g")), ("amount", q(23, "mmol"))], [("mass", q(3.28, "g")), ("amount", q(23, "mmol"))], "1k", "hepta-1,2,6-trien-1-yl phenyl sulfoxide", [("product_mass", q(3.13, "g"))], 63, []),
    ("o", "starting_material_1l", 8, "hex-5-en-1-yn-3-ol", [("mass", q(2.88, "g")), ("amount", q(30, "mmol"))], [("mass", q(3.0, "g")), ("amount", q(30, "mmol"))], [("mass", q(4.34, "g")), ("amount", q(30, "mmol"))], "1l", "hexa-1,2,5-trien-1-yl phenyl sulfoxide", [("product_mass", q(3.54, "g"))], 58, []),
    ("p", "starting_material_1m", 8, "(1R,2S,4R)-2-ethynyl-1,7,7-trimethylbicyclo[2.2.1]heptan-2-ol", [("mass", q(1.4, "g")), ("amount", q(7.9, "mmol"))], [("mass", q(0.8, "g")), ("amount", q(7.9, "mmol"))], [("mass", q(1.14, "g")), ("amount", q(7.9, "mmol"))], "1m", "2-(benzenesulfinylvinylidene)-1,7,7-trimethylbicyclo[2.2.1]heptane", [("product_mass", q(1.35, "g"))], 60, [("optical_rotation", "[α]D25 = -54.9° (c=1.0, EtOH)")]),
    ("q", "starting_material_1n", 8, "but-2-yn-1,4-diol", [("mass", q(5.16, "g")), ("amount", q(60, "mmol"))], [("mass", q(3.01, "g")), ("amount", q(30, "mmol"))], [("mass", q(4.34, "g")), ("amount", q(30, "mmol"))], "1n", "2-benzenesulfinylbuta-2,3-dien-1-ol", [("product_mass", q(1.52, "g"))], 26, []),
    ("r", "starting_material_1o", 8, "methyl 4-hydroxy-4-methylbut-2-ynoate", [("mass", q(2.84, "g")), ("amount", q(20, "mmol"))], [("mass", q(2.02, "g")), ("amount", q(20, "mmol"))], [("mass", q(2.89, "g")), ("amount", q(20, "mmol"))], "1o", "2-benzenesulfinyl-4-methylpenta-2,3-dienoic acid (source heading)", [("product_mass", q(3.66, "g"))], 72, []),
]

for letter, rid, page, reactant_label, reactant_amounts, base_amounts, chloride_amounts, product_label, product_name, product_amounts, yield_value, extras in starting_materials:
    pages = (4, page) if rid.startswith("scheme10_") else (page,)
    prefix = f"sm_{letter}"
    parts = [
        participant(f"{prefix}_alcohol", "reactant", reactant_label, (page,), name=reactant_label, amounts=reactant_amounts),
        participant(f"{prefix}_et3n", "reagent", "Et3N", (page,), name="triethylamine", amounts=base_amounts),
        participant(f"{prefix}_chloride", "reagent", "sulfenyl chloride", (page,), name="benzenesulfinyl chloride", amounts=chloride_amounts),
        participant(f"{prefix}_dcm", "solvent", "CH2Cl2", (page,), name="dichloromethane"),
        participant(f"{prefix}_product", "product", product_label, (page,), name=product_name, smiles=SMILES.get(product_label), amounts=product_amounts),
    ]
    steps = [
        {"step_id": "step1_base_addition", "participant_ids": [f"{prefix}_alcohol", f"{prefix}_et3n", f"{prefix}_dcm"], "conditions": [field("temperature", q(-85, "°C"), (page,)), field("time", q(10, "min"), (page,)), field("solvent", "CH2Cl2", (page,))]},
        {"step_id": "step2_sulfinyl_chloride_addition", "participant_ids": [f"{prefix}_alcohol", f"{prefix}_et3n", f"{prefix}_chloride", f"{prefix}_dcm"], "conditions": [field("operation", "sulfenyl chloride solution added dropwise", (page,)), field("temperature", q(-85, "°C"), (page,)), field("time", q(10, "min"), (page,)), field("warm_to", "room temperature", (page,)), field("workup", "quenched with water; separated/extracted with CH2Cl2; washed with water and brine; dried over MgSO4; concentrated under reduced pressure", (page,))]},
    ]
    outcomes = [field("yield", q(yield_value, "%"), (page,), [f"{prefix}_product"]), field("yield_measurement_basis", None, targets=[f"{prefix}_product"])]
    outcomes += [field(name, value, (page,), [f"{prefix}_product"]) for name, value in extras]
    source_issues = ["The source does not explicitly name the yield measurement basis.", "No supplementary information was supplied or explicitly associated.", "Product structures are retained by source names/labels and remain machine-unverified."]
    if rid == "starting_material_1o":
        source_issues.append("The source heading calls 1o an acid although the named precursor and the reported methoxy signal indicate a methyl ester; the heading is preserved without silent correction.")
    records.append(record(
        rid, "reported_experiment", pages, parts, steps, outcomes,
        source_issues,
        notes=["The shared general procedure on page 7 supplies the low-temperature addition, warming, quench, extraction, wash, drying, and concentration sequence."],
    ))


# Page 8: three auxiliary transformations already represented on pages 1-2.
rec = clone("scheme3_nai", 8)
set_amounts(rec, "1a", [("mass", q(82, "mg")), ("amount", q(0.5, "mmol"))], (8,))
set_amounts(rec, "NaI", [("mass", q(300, "mg")), ("amount", q(2, "mmol"))], (8,))
set_amounts(rec, "anhydrous HOAc", [("volume", q(1.5, "mL"))], (8,))
set_amounts(rec, "Z-2aa", [("product_mass", q(69, "mg"))], (8,))
add_condition(rec, "temperature", q(80, "°C"), (8,)); add_condition(rec, "time", q(5, "h"), (8,)); add_condition(rec, "workup", "water addition; ether extraction; saturated NaHCO3 wash to pH 7; MgSO4 drying", (8,)); add_condition(rec, "purification", "silica chromatography, n-hexane/ethyl acetate 20:1", (8,))
set_outcome(rec, "yield", q(41, "%"), (8,)); append_common_unresolved(rec, "Yield basis is not explicitly named.")
records.append(rec)

rec = clone("scheme2_oxidation", 8)
set_amounts(rec, "Z-2aa", [("mass", q(40, "mg")), ("amount", q(0.14, "mmol"))], (8,))
set_amounts(rec, "H2O2", [("concentration", q(30, "%")), ("volume", q(0.05, "mL")), ("amount", q(0.44, "mmol"))], (8,))
set_amounts(rec, "HOAc", [("volume", q(0.5, "mL"))], (8,)); set_amounts(rec, "Z-2aa'", [("product_mass", q(42, "mg"))], (8,))
add_condition(rec, "temperature", "r.t.", (8,)); add_condition(rec, "time", q(18, "h"), (8,)); add_condition(rec, "workup", "water addition; ether extraction; saturated NaHCO3 wash to pH 7; MgSO4 drying", (8,)); add_condition(rec, "purification", "silica chromatography, hexane/ethyl acetate 2:1", (8,))
set_outcome(rec, "yield", q(86, "%"), (8,)); append_common_unresolved(rec, "Yield basis is not explicitly named."); records.append(rec)

rec = clone("scheme2_esterification", 8)
set_amounts(rec, "E-3aa", [("mass", q(154, "mg")), ("amount", q(0.5, "mmol"))], (8,)); set_amounts(rec, "NaOAc", [("mass", q(82, "mg")), ("amount", q(1, "mmol"))], (8,)); set_amounts(rec, "Ac2O", [("volume", q(0.1, "mL"))], (8,)); set_amounts(rec, "E-2aa'", [("product_mass", q(151, "mg"))], (8,))
add_part(rec, "s2est_thf", "solvent", "THF", (8,), name="THF", amounts=[("volume", q(1, "mL"))])
rec["steps"][0]["participant_ids"] = list(dict.fromkeys(rec["steps"][0]["participant_ids"] + ["s2est_thf"]))
add_condition(rec, "temperature", "r.t.", (8,)); add_condition(rec, "time", q(6, "h"), (8,)); add_condition(rec, "atmosphere", "N2", (8,)); add_condition(rec, "solvent", "THF", (8,)); add_condition(rec, "workup", "water and ethyl acetate added; neutralized with saturated NaHCO3; extracted with ethyl acetate; dried over MgSO4", (8,)); add_condition(rec, "purification", "silica chromatography, hexane/ethyl acetate 4:1 to 2:1", (8,))
set_outcome(rec, "yield", q(86, "%"), (8,)); append_common_unresolved(rec, "Yield basis is not explicitly named."); records.append(rec)


def enrich_scope(rid, page, amount_map, product_mass, *, extra_outcomes=(), conditions=(), unresolved=()):
    rec = clone(rid, page)
    for label, items in amount_map.items():
        set_amounts(rec, label, items, (page,))
    if product_mass is not None:
        find_part(rec, next(p["label"]["value"] for p in rec["participants"] if p["role"] == "product"))["amounts"] = amount_fields([("product_mass", product_mass)], (page,))
    for name, value in conditions:
        add_condition(rec, name, value, (page,))
    for name, value in extra_outcomes:
        if name.startswith("starting_material_recovered"):
            rec["outcomes"] = [o for o in rec["outcomes"] if o["name"] != name]
            reactant_id = next(p["entity_id"] for p in rec["participants"] if p["role"] == "reactant")
            rec["outcomes"].append(field(name, value, (page,), [reactant_id]))
        else:
            set_outcome(rec, name, value, (page,))
    append_common_unresolved(rec, "Yield basis is not explicitly named even though a product mass is reported.", *unresolved)
    records.append(rec)


# Pages 8-9: detailed iodohydroxylations corresponding to equation 1,
# Table 1, Scheme 7 and Scheme 8.
iodo = [
    ("eq1_e3aa", 8, {"1a": [("mass", q(82, "mg")), ("amount", q(0.5, "mmol"))], "I2": [("mass", q(305, "mg")), ("amount", q(1.2, "mmol"))], "LiOAc·2H2O": [("mass", q(102, "mg")), ("amount", q(1.0, "mmol"))], "H2O": [("volume", q(0.3, "mL"))], "MeCN": [("volume", q(2, "mL"))]}, q(147, "mg"), [("yield", q(96, "%"))], [("temperature", q(55, "°C")), ("time", q(1, "h")), ("workup", "quenched with water; neutralized with saturated NaHCO3; washed with saturated sodium thiosulfate; extracted with CH2Cl2; dried over MgSO4"), ("purification", "flash chromatography on silica gel")], ["The detailed procedure reports 55 °C, whereas the earlier results prose describes the broader Table 1 series at room temperature; the detailed value is retained for this specific run."]),
    ("table1_entry_01", 8, {"1b": [("mass", q(89, "mg")), ("amount", q(0.5, "mmol"))], "I2": [("mass", q(203, "mg")), ("amount", q(0.8, "mmol"))], "LiOAc·2H2O": [("mass", q(102, "mg")), ("amount", q(1.0, "mmol"))]}, q(140, "mg"), [("diastereomer_ratio", "66:34")], [], []),
    ("table1_entry_02", 8, {"1c": [("mass", q(110, "mg")), ("amount", q(0.5, "mmol"))], "I2": [("mass", q(203, "mg")), ("amount", q(0.8, "mmol"))], "LiOAc·2H2O": [("mass", q(102, "mg")), ("amount", q(1.0, "mmol"))]}, q(161, "mg"), [("diastereomer_ratio", "63:37")], [("purification", "two diastereomers separable by repeated silica chromatography")], []),
    ("table1_entry_03", 9, {"1d": [("mass", q(110, "mg")), ("amount", q(0.4, "mmol"))], "I2": [("mass", q(163, "mg")), ("amount", q(0.64, "mmol"))], "LiOAc·2H2O": [("mass", q(60, "mg")), ("amount", q(0.60, "mmol"))]}, q(150, "mg"), [("diastereomer_ratio", "72:28")], [], []),
    ("table1_entry_04", 9, {"1e": [("mass", q(110, "mg")), ("amount", q(0.4, "mmol"))], "I2": [("mass", q(153, "mg")), ("amount", q(0.60, "mmol"))], "LiOAc·2H2O": [("mass", q(102, "mg")), ("amount", q(1.0, "mmol"))]}, q(158, "mg"), [("diastereomer_ratio", "92:8")], [], ["The printed 110 mg/0.4 mmol substrate pair is retained although it is stoichiometrically inconsistent with the stated identity."]),
    ("table1_entry_05", 9, {"1f": [("mass", q(96, "mg")), ("amount", q(0.5, "mmol"))], "I2": [("mass", q(152, "mg")), ("amount", q(0.60, "mmol"))], "LiOAc·2H2O": [("mass", q(102, "mg")), ("amount", q(1.0, "mmol"))]}, q(146, "mg"), [], [], []),
    ("table1_entry_06", 9, {"1g": [("mass", q(232, "mg")), ("amount", q(1.0, "mmol"))], "I2": [("mass", q(304, "mg")), ("amount", q(1.2, "mmol"))], "LiOAc·2H2O": [("mass", q(204, "mg")), ("amount", q(2.0, "mmol"))]}, q(277, "mg"), [], [], []),
    ("table1_entry_07", 9, {"1h": [("mass", q(110, "mg")), ("amount", q(0.50, "mmol"))], "I2": [("mass", q(203, "mg")), ("amount", q(0.8, "mmol"))], "LiOAc·2H2O": [("mass", q(102, "mg")), ("amount", q(1.0, "mmol"))]}, q(149, "mg"), [], [], []),
    ("table1_entry_08", 9, {"1i": [("mass", q(120, "mg")), ("amount", q(0.50, "mmol"))], "I2": [("mass", q(203, "mg")), ("amount", q(0.8, "mmol"))], "LiOAc·2H2O": [("mass", q(102, "mg")), ("amount", q(1.0, "mmol"))]}, q(151, "mg"), [], [], []),
    ("table1_entry_09", 9, {"1j": [("mass", q(248, "mg")), ("amount", q(1.0, "mmol"))], "I2": [("mass", q(305, "mg")), ("amount", q(1.20, "mmol"))], "LiOAc·2H2O": [("mass", q(204, "mg")), ("amount", q(2.0, "mmol"))]}, q(345, "mg"), [], [], []),
    ("table1_entry_10", 9, {"1k": [("mass", q(436, "mg")), ("amount", q(1.0, "mmol"))], "I2": [("mass", q(305, "mg")), ("amount", q(1.20, "mmol"))], "LiOAc·2H2O": [("mass", q(408, "mg")), ("amount", q(4.0, "mmol"))]}, q(594, "mg"), [], [], ["The printed 436 mg/1.0 mmol substrate and 594 mg/82% product figures are mutually inconsistent with the named formulas; values are preserved verbatim for review."]),
    ("table1_entry_11", 9, {"1l": [("mass", q(102, "mg")), ("amount", q(0.5, "mmol"))], "I2": [("mass", q(203, "mg")), ("amount", q(0.80, "mmol"))], "LiOAc·2H2O": [("mass", q(102, "mg")), ("amount", q(1.0, "mmol"))]}, q(160, "mg"), [], [], []),
    ("scheme7_1m_to_e3am", 9, {"1m": [("mass", q(72, "mg")), ("amount", q(0.25, "mmol"))], "I2": [("mass", q(77, "mg")), ("amount", q(0.30, "mmol"))], "LiOAc·2H2O": [("mass", q(51, "mg")), ("amount", q(0.50, "mmol"))]}, q(105, "mg"), [("yield", q(98, "%")), ("optical_rotation", "[α]D20 = -142.3° (c=1, ethanol)")], [], ["The detailed procedure reports 98% whereas Scheme 7 on page 3 reports 97%; the detailed value is used for this record and the discrepancy is retained."]),
    ("scheme8_1n", 9, {"1n": [("mass", q(97, "mg")), ("amount", q(0.50, "mmol"))], "I2": [("mass", q(203, "mg")), ("amount", q(0.80, "mmol"))], "LiOAc·2H2O": [("mass", q(102, "mg")), ("amount", q(1.0, "mmol"))]}, q(137, "mg"), [("yield", q(81, "%"))], [], ["The detailed procedure reports 81% whereas Scheme 8 on page 4 reports 82%; the detailed value is used and the discrepancy is retained."]),
    ("scheme8_1o", 9, {"1o": [("mass", q(100, "mg")), ("amount", q(0.40, "mmol"))], "I2": [("mass", q(127, "mg")), ("amount", q(0.50, "mmol"))], "LiOAc·2H2O": [("mass", q(102, "mg")), ("amount", q(1.0, "mmol"))]}, q(134, "mg"), [], [], []),
]
for rid, page, amount_map, pmass, extras, conditions, unresolved in iodo:
    enrich_scope(rid, page, amount_map, pmass, extra_outcomes=extras, conditions=conditions, unresolved=unresolved)


# Pages 9-10: eight detailed bromohydroxylations (Table 2 records).
bromo = [
    ("table2_entry_01", 9, {"1a": [("mass", q(164, "mg")), ("amount", q(1.0, "mmol"))], "CuBr2": [("mass", q(892, "mg")), ("amount", q(4.0, "mmol"))], "acetone/H2O": [("volume", q(8, "mL"))]}, q(230, "mg"), [], [("solvent", "water/acetone 1:2 (v/v)"), ("workup", "CH2Cl2 extraction; saturated NaHCO3 and water washes; MgSO4 drying"), ("purification", "flash silica chromatography, hexane/ethyl acetate 2:1")], []),
    ("table2_entry_04", 10, {"1e": [("mass", q(55, "mg")), ("amount", q(0.25, "mmol"))], "CuBr2": [("mass", q(223, "mg")), ("amount", q(1.00, "mmol"))], "acetone/H2O": [("volume", q(3, "mL"))]}, q(69, "mg"), [], [("solvent", "H2O/acetone 1:2")], []),
    ("table2_entry_06", 10, {"1h": [("mass", q(55, "mg")), ("amount", q(0.25, "mmol"))], "CuBr2": [("mass", q(223, "mg")), ("amount", q(1.00, "mmol"))], "acetone/H2O": [("volume", q(3, "mL"))]}, q(68, "mg"), [], [("solvent", "H2O/acetone 1:2")], []),
    ("table2_entry_07", 10, {"1j": [("mass", q(62, "mg")), ("amount", q(0.25, "mmol"))], "CuBr2": [("mass", q(223, "mg")), ("amount", q(1.00, "mmol"))], "acetone/H2O": [("volume", q(3, "mL"))]}, q(79, "mg"), [], [("solvent", "H2O/acetone 1:2")], []),
    ("table2_entry_08", 10, {"1m": [("mass", q(72, "mg")), ("amount", q(0.25, "mmol"))], "CuBr2": [("mass", q(223, "mg")), ("amount", q(1.00, "mmol"))], "acetone/H2O": [("volume", q(3, "mL"))]}, q(38, "mg"), [("yield", q(94.5, "%")), ("starting_material_recovered", q(42, "mg"))], [("solvent", "H2O/acetone 1:2")], ["The product mass, 94.5% reported yield, and 42 mg recovered starting material require source review because the basis is not explained."]),
    ("table2_entry_02", 10, {"1c": [("mass", q(110, "mg")), ("amount", q(0.50, "mmol"))], "NBS": [("mass", q(110, "mg")), ("amount", q(0.60, "mmol"))], "LiOAc·2H2O": [("mass", q(60, "mg")), ("amount", q(0.60, "mmol"))], "MeCN/H2O": [("volume", q(2.5, "mL"))]}, q(143, "mg"), [], [("temperature", "r.t."), ("time", q(2, "h")), ("solvent", "H2O/CH3CN 1:7"), ("workup", "CH2Cl2 extraction; brine wash; MgSO4 drying"), ("purification", "flash silica chromatography")], []),
    ("table2_entry_03", 10, {"1d": [("mass", q(138, "mg")), ("amount", q(0.50, "mmol"))], "NBS": [("mass", q(110, "mg")), ("amount", q(0.60, "mmol"))], "LiOAc·2H2O": [("mass", q(60, "mg")), ("amount", q(0.60, "mmol"))]}, q(182, "mg"), [], [], []),
    ("table2_entry_05", 10, {"1f": [("mass", q(96, "mg")), ("amount", q(0.50, "mmol"))], "NBS": [("mass", q(110, "mg")), ("amount", q(0.60, "mmol"))], "LiOAc·2H2O": [("mass", q(60, "mg")), ("amount", q(0.60, "mmol"))]}, q(98, "mg"), [], [], []),
]
for rid, page, amount_map, pmass, extras, conditions, unresolved in bromo:
    enrich_scope(rid, page, amount_map, pmass, extra_outcomes=extras, conditions=conditions, unresolved=unresolved)

# E-3ba starts on page 9 and its characterization continues on page 10.
next(r for r in records if r["source_reaction_id"] == "table2_entry_01")["evidence_ids"] += [eid for eid in evidence(10) if eid not in next(r for r in records if r["source_reaction_id"] == "table2_entry_01")["evidence_ids"]]


# Pages 10-11: five solventless chlorohydroxylations (Table 3/Scheme 9).
chloro = [
    ("table3_entry_01", 10, {"1a": [("mass", q(180, "mg")), ("amount", q(1.1, "mmol"))], "CuCl2·2H2O": [("mass", q(748, "mg")), ("amount", q(4.4, "mmol"))], "silica gel": [("mass", q(400, "mg"))]}, q(105, "mg"), [], [("operation", "milled for a couple of minutes, heated at 65 °C for 5 min, repeated four times"), ("temperature", q(65, "°C")), ("time_per_heating_cycle", q(5, "min")), ("purification", "silica chromatography, petroleum ether/ethyl acetate 1:1 to 1:2")], []),
    ("table3_entry_02", 10, {"1e": [("mass", q(110, "mg")), ("amount", q(0.50, "mmol"))], "CuCl2·2H2O": [("mass", q(340, "mg")), ("amount", q(2.0, "mmol"))], "silica gel": [("mass", q(200, "mg"))]}, q(114, "mg"), [], [], []),
    ("table3_entry_03", 10, {"1f": [("mass", q(96, "mg")), ("amount", q(0.50, "mmol"))], "CuCl2·2H2O": [("mass", q(340, "mg")), ("amount", q(2.0, "mmol"))], "silica gel": [("mass", q(400, "mg"))]}, q(74, "mg"), [("starting_material_recovered", q(12, "%")), ("starting_material_recovered_mass", q(11, "mg"))], [], []),
    ("scheme9_table3_entry_04", 11, {"1g": [("mass", q(58, "mg")), ("amount", q(0.25, "mmol"))], "CuCl2·2H2O": [("mass", q(170, "mg")), ("amount", q(1.0, "mmol"))], "silica gel": [("mass", q(200, "mg"))]}, q(52, "mg"), [], [], []),
    ("table3_entry_05", 11, {"1h": [("mass", q(55, "mg")), ("amount", q(0.25, "mmol"))], "CuCl2·2H2O": [("mass", q(170, "mg")), ("amount", q(1.0, "mmol"))], "silica gel": [("mass", q(200, "mg"))]}, q(35, "mg"), [], [], []),
]
for rid, page, amount_map, pmass, extras, conditions, unresolved in chloro:
    enrich_scope(rid, page, amount_map, pmass, extra_outcomes=extras, conditions=conditions, unresolved=unresolved)

# E-3cf starts on page 10 and its characterization continues on page 11.
next(r for r in records if r["source_reaction_id"] == "table3_entry_03")["evidence_ids"] += [eid for eid in evidence(11) if eid not in next(r for r in records if r["source_reaction_id"] == "table3_entry_03")["evidence_ids"]]


# Page 11: nine optically active halohydroxylation methods (Table 4 rows).
optical = [
    ("table4_entry_01", {"(R)-1c": [("mass", q(110, "mg")), ("amount", q(0.5, "mmol")), ("starting_material_ee", q(96, "%"))], "I2": [("mass", q(153, "mg")), ("amount", q(0.6, "mmol"))]}, q(179, "mg"), [("product_ee", q(95, "%")), ("diastereomer_ratio", "73:27")], []),
    ("table4_entry_02", {"(R)-1c": [("mass", q(55, "mg")), ("amount", q(0.25, "mmol")), ("starting_material_ee", q(96, "%"))], "Br2": [("concentration", q(0.5, "M")), ("volume", q(0.6, "mL")), ("amount", q(0.3, "mmol"))]}, q(76, "mg"), [("product_ee", q(96, "%")), ("diastereomer_ratio", "50:50")], []),
    ("table4_entry_03", {"(R)-1c": [("mass", q(55, "mg")), ("amount", q(0.25, "mmol")), ("starting_material_ee", q(96, "%"))], "CuBr2": [("mass", q(223, "mg")), ("amount", q(1, "mmol"))]}, q(73, "mg"), [("product_ee", q(97, "%")), ("diastereomer_ratio", "51:49")], [("solvent", "water/acetone 1:2, 2 mL"), ("temperature", "r.t.")]),
    ("table4_entry_04", {"(S)-1d": [("mass", q(69, "mg")), ("amount", q(0.25, "mmol")), ("starting_material_ee", q(96, "%"))], "Br2": [("concentration", q(0.5, "M")), ("volume", q(0.7, "mL")), ("amount", q(0.35, "mmol"))]}, q(92, "mg"), [("product_ee", q(97, "%")), ("diastereomer_ratio", "53:47")], []),
    ("table4_entry_05", {"(S)-1d": [("mass", q(69, "mg")), ("amount", q(0.25, "mmol")), ("starting_material_ee", q(96, "%"))], "CuBr2": [("mass", q(223, "mg")), ("amount", q(1, "mmol"))]}, q(90, "mg"), [("product_ee", q(96, "%")), ("diastereomer_ratio", "51:49")], [("solvent", "water/acetone 1:2, 2 mL")]),
    ("table4_entry_06", {"(S)-1e": [("mass", q(110, "mg")), ("amount", q(0.50, "mmol")), ("starting_material_ee", q(99, "%", qualifier="gt", raw_text=">99%"))], "I2": [("mass", q(153, "mg")), ("amount", q(0.60, "mmol"))]}, q(160, "mg"), [("product_ee", q(99, "%", qualifier="gt", raw_text=">99%")), ("diastereomer_ratio", "99:1")], []),
    ("table4_entry_07", {"(S)-1e": [("mass", q(110, "mg")), ("amount", q(0.50, "mmol")), ("starting_material_ee", q(99, "%", qualifier="gt", raw_text=">99%"))], "Br2": [("concentration", q(0.50, "M")), ("volume", q(1.2, "mL")), ("amount", q(0.6, "mmol"))]}, q(135, "mg"), [("product_ee", q(99, "%", qualifier="gt", raw_text=">99%")), ("diastereomer_ratio", "92:8")], []),
    ("table4_entry_08", {"(S)-1e": [("mass", q(110, "mg")), ("amount", q(0.5, "mmol")), ("starting_material_ee", q(99, "%", qualifier="gt", raw_text=">99%"))], "CuBr2": [("mass", q(446, "mg")), ("amount", q(2, "mmol"))]}, q(109, "mg"), [("product_ee", q(99, "%", qualifier="gt", raw_text=">99%")), ("diastereomer_ratio", "98:2")], [("solvent", "water/acetone 1:2, 2 mL"), ("temperature", "r.t.")]),
    ("table4_entry_09", {"(S)-1e": [("mass", q(67, "mg")), ("amount", q(0.3, "mmol")), ("starting_material_ee", q(99, "%", qualifier="gt", raw_text=">99%"))], "CuCl2·2H2O": [("mass", q(204, "mg")), ("amount", q(1.2, "mmol"))]}, q(67, "mg"), [("product_ee", q(99, "%", qualifier="gt", raw_text=">99%")), ("diastereomer_ratio", "89:11")], [("operation", "solventless silica-gel method; 245 mg silica gel")]),
]
for rid, amount_map, pmass, extras, conditions in optical:
    enrich_scope(rid, 11, amount_map, pmass, extra_outcomes=extras, conditions=conditions)
    rec = records[-1]
    entry = int(rid.rsplit("_", 1)[1])
    product_labels = {
        1: "(R)-E-3ac", 2: "(R)-E-3bc", 3: "(R)-E-3bc",
        4: "(S)-E-3bd", 5: "(S)-E-3bd", 6: "(S)-E-3ae",
        7: "(S)-E-3be", 8: "(S)-E-3be", 9: "(S)-E-3ce",
    }
    product = next(p for p in rec["participants"] if p["role"] == "product")
    product["label"] = fact(product_labels[entry], (11,))
    if entry in (1, 2, 4, 6, 7):
        lithium_amounts = {
            1: [("mass", q(102, "mg")), ("amount", q(1.0, "mmol"))],
            2: [("mass", q(60, "mg")), ("amount", q(0.6, "mmol"))],
            4: [("mass", q(60, "mg")), ("amount", q(0.6, "mmol"))],
            6: [("mass", q(102, "mg")), ("amount", q(1.0, "mmol"))],
            7: [("mass", q(102, "mg")), ("amount", q(1.0, "mmol"))],
        }[entry]
        entity_id = f"t4e{entry}_lioac"
        add_part(rec, entity_id, "reagent", "LiOAc·2H2O", (11,), name="lithium acetate dihydrate", amounts=lithium_amounts)
        rec["steps"][0]["participant_ids"] = list(dict.fromkeys(rec["steps"][0]["participant_ids"] + [entity_id]))
    if entry in (2, 4, 7):
        entity_id = f"t4e{entry}_mecn"
        add_part(rec, entity_id, "solvent", "MeCN (Br2 stock solution)", (11,), name="acetonitrile")
        rec["steps"][0]["participant_ids"] = list(dict.fromkeys(rec["steps"][0]["participant_ids"] + [entity_id]))
    if entry == 9:
        add_part(rec, "t4e9_silica", "unspecified_agent", "silica gel", (11,), amounts=[("mass", q(245, "mg"))])
        rec["steps"][0]["participant_ids"] = list(dict.fromkeys(rec["steps"][0]["participant_ids"] + ["t4e9_silica"]))


# Pages 11-12: Sonogashira and Suzuki records.
rec = clone("eq2_sonogashira", 11)
for label, items in {"E-3aa": [("mass", q(77, "mg")), ("amount", q(0.25, "mmol"))], "CH3(CH2)3C≡CH": [("mass", q(41, "mg")), ("amount", q(0.5, "mmol"))], "Pd(PPh3)2Cl2": [("mass", q(0.9, "mg")), ("amount", q(0.00125, "mmol"))], "CuI": [("mass", q(0.5, "mg")), ("amount", q(0.0026, "mmol"))], "Et3N": [("volume", q(1, "mL"))], "DMSO": [("volume", q(1, "mL"))], "Z-4g": [("product_mass", q(60, "mg"))]}.items(): set_amounts(rec, label, items, (11,))
add_condition(rec, "atmosphere", "N2", (11,)); add_condition(rec, "workup", "water added; ether extraction; MgSO4 drying", (11,)); add_condition(rec, "purification", "silica chromatography, hexane/ethyl acetate 2:1", (11,)); append_common_unresolved(rec, "Yield basis is not explicitly named."); records.append(rec)

rec = clone("scheme11_hexenyl_suzuki", 11)
for label, items in {"E-3aa": [("mass", q(27.2, "mg")), ("amount", q(0.09, "mmol"))], "E-1-hexenylboronic acid": [("mass", q(12.6, "mg")), ("amount", q(0.1, "mmol"))], "Pd(PPh3)4": [("mass", q(5.8, "mg")), ("loading", q(5, "mol%"))], "K2CO3": [("concentration", q(2, "M")), ("volume", q(0.15, "mL")), ("amount", q(0.3, "mmol"))], "TBAB": [("mass", q(1.6, "mg")), ("loading", q(5, "mol%"))], "THF": [("volume", q(1, "mL"))], "Z-4h": [("product_mass", q(21, "mg"))]}.items(): set_amounts(rec, label, items, (11,))
add_condition(rec, "atmosphere", "N2", (11,)); add_condition(rec, "workup", "water added; CH2Cl2 extraction; MgSO4 drying", (11,)); add_condition(rec, "purification", "silica chromatography, hexane/ethyl acetate 2:1", (11,)); append_common_unresolved(rec, "Yield basis is not explicitly named."); records.append(rec)

rec = clone("scheme11_phenyl_with_tbab", 12)
next(p for p in rec["participants"] if p["role"] == "product")["label"] = fact("4a", (12,))
for label, items in {"E-3aa": [("mass", q(154, "mg")), ("amount", q(0.5, "mmol"))], "phenylboronic acid": [("mass", q(91.5, "mg")), ("amount", q(0.75, "mmol"))], "Pd(PPh3)4": [("mass", q(29, "mg")), ("loading", q(5, "mol%"))], "TBAB": [("mass", q(15.7, "mg")), ("loading", q(10, "mol%"))], "K2CO3": [("concentration", q(2, "M")), ("volume", q(0.75, "mL")), ("amount", q(1.5, "mmol"))], "THF": [("volume", q(4, "mL"))], "4a": [("product_mass", q(116.1, "mg"))]}.items(): set_amounts(rec, label, items, (12,))
set_outcome(rec, "yield", q(90, "%"), (12,)); set_outcome(rec, "E_Z_ratio", "3:97", (12,)); append_common_unresolved(rec, "The procedure heading identifies Z-4a but the sentence says 'gave E-4a'; the reported E/Z 3:97 ratio and heading are retained without silently resolving the label typo.", "Yield basis is not explicitly named."); records.append(rec)
next(p for p in rec["participants"] if p["role"] == "product")["label"] = fact("Z-4a", (12,))


# Page 12: Negishi couplings.  The table records are enriched with the
# explicit in-situ organozinc precursors and source quantities.
negishi = [
    (2, "ZnBr2", [("mass", q(1.35, "g")), ("amount", q(2.0, "mmol"))], "PhMgBr", [("concentration", q(1.1084, "M")), ("volume", q(5.4, "mL")), ("amount", q(2.0, "mmol"))], "E-3aa", [("mass", q(616, "mg")), ("amount", q(2.0, "mmol"))], [("mass", q(115, "mg")), ("loading", q(5, "mol%"))], q(484, "mg"), ["The printed ZnBr2 and PhMgBr amount values (2.0 mmol each) conflict with their masses/concentration-volume product; values are preserved verbatim."]),
    (3, "ZnBr2", [("mass", q(203, "mg")), ("amount", q(0.9, "mmol"))], "PhMgBr", [("concentration", q(0.7656, "M")), ("volume", q(1.2, "mL")), ("amount", q(0.9, "mmol"))], "E-3ah", [("mass", q(109.2, "mg")), ("amount", q(0.3, "mmol"))], [("mass", q(17, "mg")), ("loading", q(5, "mol%"))], q(77.2, "mg"), ["The heading identifies Z-4b while the sentence says E-4b; the source labels are preserved for review."]),
    (4, "ZnCl2", [("mass", q(2.04, "g")), ("amount", q(15.0, "mmol"))], "PhMgBr", [("concentration", q(0.8275, "M")), ("volume", q(18.0, "mL")), ("amount", q(15.0, "mmol"))], "E-3ac", [("mass", q(1.82, "g")), ("amount", q(5.0, "mmol"))], [("mass", q(145, "mg")), ("loading", q(2.5, "mol%"))], q(1.1073, "g"), []),
    (5, "ZnCl2", [("mass", q(1.54, "g")), ("amount", q(11.3, "mmol"))], "PhMgBr", [("concentration", q(0.8275, "M")), ("volume", q(13.7, "mL")), ("amount", q(11.3, "mmol"))], "(R)-E-3ac", [("mass", q(1.37, "g")), ("amount", q(3.76, "mmol")), ("starting_material_ee", q(97.1, "%"))], [("mass", q(108, "mg")), ("loading", q(2.5, "mol%"))], q(869, "mg"), []),
    (6, "ZnBr2", [("mass", q(5.06, "g")), ("amount", q(22.5, "mmol"))], "PhMgBr", [("concentration", q(0.79, "M")), ("volume", q(28.5, "mL")), ("amount", q(22.5, "mmol"))], "E-3ad", [("mass", q(3.15, "g")), ("amount", q(7.5, "mmol"))], [("mass", q(433, "mg")), ("loading", q(5, "mol%"))], q(2.0959, "g"), []),
    (7, "ZnBr2", [("mass", q(193, "mg")), ("amount", q(0.86, "mmol"))], "PhMgBr", [("concentration", q(0.98, "M")), ("volume", q(0.87, "mL")), ("amount", q(0.86, "mmol"))], "E-3ad", [("mass", q(120, "mg")), ("amount", q(0.29, "mmol"))], [("mass", q(17, "mg")), ("loading", q(5, "mol%"))], q(105.7, "mg"), []),
    (8, "ZnBr2", [("mass", q(0.97, "g")), ("amount", q(4.30, "mmol"))], "PhMgBr", [("concentration", q(1.00, "M")), ("volume", q(4.30, "mL")), ("amount", q(4.30, "mmol"))], "E-3ad", [("mass", q(600, "mg")), ("amount", q(1.43, "mmol"))], [("mass", q(80, "mg")), ("loading", q(5, "mol%"))], q(408.1, "mg"), ["The detailed sentence labels the substrate (R)-E-3ad while the product is (S)-Z-4d and Table 5's footnote refers to an (S)-propargylic alcohol; the configuration conflict is not silently corrected."]),
    (9, "ZnBr2", [("mass", q(225, "mg")), ("amount", q(0.4, "mmol"))], "EtMgBr", [("concentration", q(0.7721, "M")), ("volume", q(1.3, "mL")), ("amount", q(1.0, "mmol"))], "E-3aa", [("mass", q(123.2, "mg")), ("amount", q(0.4, "mmol"))], [("mass", q(23, "mg")), ("loading", q(5, "mol%"))], q(72.3, "mg"), ["The printed ZnBr2 mass and 0.4 mmol amount are stoichiometrically inconsistent; both values are preserved verbatim."]),
]

for entry, zinc_label, zinc_amounts, grignard_label, grignard_amounts, substrate_label, substrate_amounts, pd_amounts, pmass, issues in negishi:
    rid = f"table5_entry_{entry:02d}"
    rec = clone(rid, 12)
    prefix = f"t5e{entry}"
    add_part(rec, f"{prefix}_zinc_salt", "reagent", zinc_label, (12,), amounts=zinc_amounts)
    add_part(rec, f"{prefix}_grignard", "reagent", grignard_label, (12,), amounts=grignard_amounts)
    current_substrate_label = "(R)-E-3ad" if entry in (7, 8) and any(p["label"]["value"] == "(R)-E-3ad" for p in rec["participants"]) else substrate_label
    set_amounts(rec, current_substrate_label, substrate_amounts, (12,))
    set_amounts(rec, "Pd(PPh3)4", pd_amounts, (12,))
    find_part(rec, next(p["label"]["value"] for p in rec["participants"] if p["role"] == "product"))["amounts"] = amount_fields([("product_mass", pmass)], (12,))
    rec["steps"][0]["participant_ids"] = list(dict.fromkeys(rec["steps"][0]["participant_ids"] + [f"{prefix}_zinc_salt", f"{prefix}_grignard"]))
    if entry in (7, 8):
        find_part(rec, current_substrate_label)["label"] = fact("(R)-E-3ad", (12,))
    if entry == 2:
        rec["steps"] = [
            {"step_id": "step1_organozinc_generation", "participant_ids": [f"{prefix}_zinc_salt", f"{prefix}_grignard", f"{prefix}_solv"], "conditions": [field("operation", "PhMgBr added to anhydrous ZnBr2 in dry THF at 0 °C", (12,)), field("temperature", q(0, "°C"), (12,)), field("time_at_room_temperature", q(1, "h"), (12,)), field("solvent", "dry THF (10 mL)", (12,)), field("operation_after_reaction", "THF removed under vacuum", (12,))]},
            {"step_id": "step2_coupling", "participant_ids": [f"{prefix}_sub", f"{prefix}_orgzn", f"{prefix}_pd", f"{prefix}_solv"], "conditions": [field("temperature", "ambient temperature", (12,)), field("time", q(1, "h"), (12,)), field("atmosphere", "N2", (12,)), field("solvent", "anhydrous DMF (10 mL)", (12,)), field("workup", "saturated NH4Cl; ether extraction; brine wash; MgSO4 drying", (12,)), field("purification", "flash silica chromatography, ethyl acetate/n-hexane 1:2", (12,))]},
        ]
    append_common_unresolved(rec, "Yield basis is not explicitly named.", *issues)
    records.append(rec)


# Table 5 entry 11: the detailed organozinc preparation begins on page 12
# and continues on page 13.  Only page-12 facts are added here; the table-5
# yield/time already have page-5 support.
rec = clone("table5_entry_11", 12)
add_part(rec, "t5e11_phenylacetylene", "reactant", "phenylacetylene", (12,), amounts=[("mass", q(122.4, "mg")), ("amount", q(1.2, "mmol"))])
add_part(rec, "t5e11_nbuli", "reagent", "n-BuLi", (12,), amounts=[("concentration", q(1.52, "M")), ("volume", q(0.8, "mL")), ("amount", q(1.2, "mmol"))])
add_part(rec, "t5e11_znbr2", "reagent", "ZnBr2", (12,), amounts=[("mass", q(270, "mg")), ("amount", q(1.2, "mmol"))])
set_amounts(rec, "E-3aa", [("mass", q(123, "mg")), ("amount", q(0.4, "mmol"))], (12,)); set_amounts(rec, "Pd(PPh3)4", [("mass", q(23, "mg")), ("loading", q(5, "mol%"))], (12,)); set_amounts(rec, "THF/HMPA", [("THF_volume_step1", q(3, "mL")), ("THF_volume_step2", q(2, "mL")), ("HMPA_volume", q(1, "mL"))], (12,))
rec["steps"] = [
    {"step_id": "step1_lithium_acetylide_generation", "participant_ids": ["t5e11_phenylacetylene", "t5e11_nbuli", "t5e11_solv"], "conditions": [field("temperature", q(-70, "°C"), (12,)), field("addition_time", q(10, "min"), (12,)), field("time_after_addition", q(15, "min"), (12,)), field("solvent", "THF (3 mL) / n-hexane from n-BuLi solution", (12,))]},
    {"step_id": "step2_organozinc_generation", "participant_ids": ["t5e11_phenylacetylene", "t5e11_nbuli", "t5e11_znbr2", "t5e11_solv"], "conditions": [field("operation", "ZnBr2 solution added; stirred vigorously", (12,)), field("temperature", "room temperature", (12,)), field("time", q(30, "min"), (12,)), field("solvent", "THF (additional 2 mL)", (12,))]},
    {"step_id": "step3_coupling", "participant_ids": ["t5e11_sub", "t5e11_orgzn", "t5e11_pd", "t5e11_solv"], "conditions": [field("temperature", "r.t.", (5,)), field("time", q(1.5, "h"), (5,)), field("solvent", "THF/HMPA", (5, 12))]},
]
append_common_unresolved(rec, "The workup, isolated product mass and characterization continue on page 13, outside this batch; they are not claimed as page-12-reviewed facts.", "Yield basis is not stated in Table 5.")
records.append(rec)


page_records = {
    7: [f"{DOC}:{rid}" for _, rid, page, *_ in starting_materials if page == 7],
    8: [f"{DOC}:{rid}" for _, rid, page, *_ in starting_materials if page == 8] + [f"{DOC}:{x}" for x in ["scheme3_nai", "scheme2_oxidation", "scheme2_esterification", "eq1_e3aa", "table1_entry_01", "table1_entry_02"]],
    9: [f"{DOC}:{x}" for x in ["table1_entry_03", "table1_entry_04", "table1_entry_05", "table1_entry_06", "table1_entry_07", "table1_entry_08", "table1_entry_09", "table1_entry_10", "table1_entry_11", "scheme7_1m_to_e3am", "scheme8_1n", "scheme8_1o", "table2_entry_01"]],
    10: [f"{DOC}:{x}" for x in ["table2_entry_01", "table2_entry_04", "table2_entry_06", "table2_entry_07", "table2_entry_08", "table2_entry_02", "table2_entry_03", "table2_entry_05", "table3_entry_01", "table3_entry_02", "table3_entry_03"]],
    11: [f"{DOC}:{x}" for x in ["table3_entry_03", "scheme9_table3_entry_04", "table3_entry_05", *[f"table4_entry_{i:02d}" for i in range(1, 10)], "eq2_sonogashira", "scheme11_hexenyl_suzuki"]],
    12: [f"{DOC}:{x}" for x in ["scheme11_phenyl_with_tbab", *[f"table5_entry_{i:02d}" for i in range(2, 10)], "table5_entry_11"]],
}

coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {"page": 7, "state": "attempted", "regions": [
            {"region": "Experimental Section, shared sulfinyl-allene procedure", "finding": "Shared two-stage low-temperature procedure inspected and applied only to the detailed preparations that cite it; workup and missing yield-basis limitations retained.", "evidence_ids": evidence(7)},
            {"region": "starting materials (a)-(e), left column", "finding": "Five individual preparations (1a, 1b, 1c, (R)-1c, 1d) with masses, mmol and yields; the chiral row also records ee/dr.", "evidence_ids": evidence(7)},
            {"region": "starting materials (f)-(m), right column", "finding": "Eight individual preparations ((S)-1d through 1j) with source quantities and yields; no table rows or arrows were present.", "evidence_ids": evidence(7)},
        ], "record_ids": page_records[7], "unresolved": ["Yield measurement bases are not explicitly named.", "Product structures were retained by names/labels and are not certified from text alone."]},
        {"page": 8, "state": "attempted", "regions": [
            {"region": "starting materials (n)-(r), left upper column", "finding": "Five additional sulfinyl-allene preparations (1k-1o) recorded independently.", "evidence_ids": evidence(8)},
            {"region": "Z-2aa, Z-2aa' and E-2aa' procedures", "finding": "Three previously inventoried transformations enriched with exact scale, time, temperature, workup, purification and product mass.", "evidence_ids": evidence(8)},
            {"region": "typical iodohydroxylation and products E-3aa to E-3ac", "finding": "The specific E-3aa run and two Table 1 scope entries enriched; E-3aa detailed temperature is 55 °C rather than the broad room-temperature prose description.", "evidence_ids": evidence(8)},
        ], "record_ids": page_records[8], "unresolved": ["The source does not explicitly name most yield bases.", "E-3aa has a temperature-context discrepancy between the detailed procedure and earlier narrative."]},
        {"page": 9, "state": "attempted", "regions": [
            {"region": "iodohydroxylations E-3ad through E-3aj", "finding": "Seven Table 1 entries enriched with exact reactant/reagent/product quantities and reported dr where present.", "evidence_ids": evidence(9)},
            {"region": "iodohydroxylations E-3ak through E-3ao", "finding": "Five additional detailed procedures enriched, including camphor-derived, diol and ester products.", "evidence_ids": evidence(9)},
            {"region": "bromohydroxylation E-3ba, lower right", "finding": "Procedure begins here and continues on page 10; one existing Table 2 record uses both pages as evidence.", "evidence_ids": evidence(9)},
        ], "record_ids": page_records[9], "unresolved": ["Printed E-3ak masses/mmol/yield are internally inconsistent and are preserved for review.", "Detailed E-3am and E-3an yields differ by one percentage point from earlier schemes."]},
        {"page": 10, "state": "attempted", "regions": [
            {"region": "bromohydroxylations E-3ba and E-3be/E-3bh/E-3bj/E-3bm", "finding": "Five CuBr2 procedures inventoried/enriched, including E-3bm recovered starting material.", "evidence_ids": evidence(10)},
            {"region": "NBS bromohydroxylations E-3bc/E-3bd/E-3bf", "finding": "Three NBS procedures enriched with explicit NBS and LiOAc·2H2O quantities; no new table rows invented.", "evidence_ids": evidence(10)},
            {"region": "chlorohydroxylations E-3ca/E-3ce/E-3cf", "finding": "Three solventless milling procedures enriched; E-3cf continues onto page 11.", "evidence_ids": evidence(10)},
        ], "record_ids": page_records[10], "unresolved": ["E-3bm's product mass, reported yield and recovered starting material have no stated calculation basis.", "Several procedures inherit temperature/time from the earlier tables rather than restating them in the paragraph."]},
        {"page": 11, "state": "attempted", "regions": [
            {"region": "chlorohydroxylations E-3cf/E-3cg/E-3ch", "finding": "Completion of E-3cf and two further solventless chlorohydroxylations enriched with exact quantities.", "evidence_ids": evidence(11)},
            {"region": "optically active halohydroxylations, methods A-C", "finding": "Nine distinct method/condition records corresponding to Table 4 rows enriched with scale, ee and dr; A/B methods remain separate.", "evidence_ids": evidence(11)},
            {"region": "C-halogen coupling procedures Z-4g and Z-4h", "finding": "Sonogashira and alkenyl-Suzuki records enriched with catalyst loadings, solvent volumes, atmosphere, workup and product masses.", "evidence_ids": evidence(11)},
        ], "record_ids": page_records[11], "unresolved": ["Yield basis is not explicitly named for the detailed procedures.", "Structures and absolute configurations remain unverified machine records."]},
        {"page": 12, "state": "attempted", "regions": [
            {"region": "Suzuki Z-4a and Negishi Z-4a/Z-4b", "finding": "Suzuki and two Negishi records enriched with exact scale and catalyst/reagent amounts; printed E/Z and E/Z-label inconsistencies retained.", "evidence_ids": evidence(12)},
            {"region": "Negishi Z-4c and chiral (R)-Z-4c", "finding": "Two ZnCl2/PhMgBr preparations enriched; diastereomers remain represented as one reported product batch with separation noted in source characterization.", "evidence_ids": evidence(12)},
            {"region": "Negishi Z-4d, chiral variants and Z-4e", "finding": "Four additional organozinc couplings enriched with explicit precursor quantities, catalyst loading, product mass, ee/dr where given.", "evidence_ids": evidence(12)},
            {"region": "Z-4f organozinc preparation, lower right", "finding": "Page-12 stages for lithium acetylide and zinc reagent formation recorded; final workup/product mass on page 13 intentionally not claimed in this batch.", "evidence_ids": evidence(12)},
        ], "record_ids": page_records[12], "unresolved": ["Printed ZnBr2/Grignard amount pairs in Z-4a and Z-4e procedures are stoichiometrically inconsistent and are preserved verbatim.", "The (R)-E-3ad to (S)-Z-4d wording conflicts with Table 5's chiral footnote.", "Z-4f continues on page 13, outside the requested range."]},
    ],
}


def main():
    ids = [r["record_id"] for r in records]
    if len(ids) != len(set(ids)):
        raise RuntimeError("duplicate record IDs in raw extraction")
    OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
    COVERAGE.parent.mkdir(parents=True, exist_ok=True)
    COVERAGE.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")
    tasks = json.loads(TASKS.read_text())
    for task in tasks:
        if task.get("document_id") != DOC:
            continue
        try:
            page = int(task["evidence_id"].split(":page", 1)[1].split(":", 1)[0])
        except (IndexError, ValueError):
            continue
        if 7 <= page <= 12:
            task["state"] = "attempted"
            task["reason"] = "Original page image inspected; page regions and linked records are documented in coverage/pages_0007_0012.json."
    TASKS.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"records": len(records), "new_records": sum(r["record_id"].split(":", 1)[1] not in existing for r in records), "updated_records": sum(r["record_id"].split(":", 1)[1] in existing for r in records), "coverage_pages": len(coverage["pages"])}, ensure_ascii=False))


if __name__ == "__main__":
    main()
