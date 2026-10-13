#!/usr/bin/env python3
"""Enrich existing reaction records from original PDF pages 7--12.

The experimental paragraphs on pages 7--11 are detailed preparations for
scope records already created from pages 4--5.  They are updated rather than
duplicated.  Page 12 contains references and crystallographic deposition
details; those details are linked to the corresponding existing records.
"""

from copy import deepcopy
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
DOC = "doc_e5379ddb5b502c43"
DATASET = ROOT / "runs/current/dataset.json"


def ev(page, kind="image"):
    return f"{DOC}:page{page}:{kind}"


def page_evidence(*pages):
    return [item for page in pages for item in (ev(page, "image"), ev(page, "text"))]


def fact(value, evidence=()):
    return {
        "value": value,
        "evidence_ids": list(dict.fromkeys(evidence)),
        "verification": "missing" if value is None else "unreviewed",
    }


def field(name, value, evidence=(), targets=None):
    item = {"name": name, "fact": fact(value, evidence)}
    if targets:
        item["target_entity_ids"] = list(targets)
    return item


def upsert_field(items, name, value, evidence, targets=None):
    items[:] = [item for item in items if item["name"] != name]
    items.append(field(name, value, evidence, targets))


def participant(record, entity_id):
    return next(p for p in record["participants"] if p["entity_id"] == entity_id)


def condition_list(record):
    assert len(record["steps"]) == 1
    return record["steps"][0]["conditions"]


dataset = json.loads(DATASET.read_text())
by_id = {record["record_id"]: record for record in dataset["experiments"]}


# Values are transcribed from the original rendered pages.  Times and reaction
# temperatures already present from Tables 3/4 and Scheme 3/4 are retained.
preparations = [
    {
        "suffix": "table3_entry2", "pages": [6, 7], "product": "2b",
        "product_name": "3-isobutyryl-5-phenyl-5(E)-3,4,7,8-tetrahydro-2H-oxocin-2-one",
        "pd": [5.4, "mg", 0.025], "pph3": [13.3, "mg", 0.050], "base": [138.1, "mg", 1.0],
        "halide_name": "iodobenzene", "halide_mass": [152.9, "mg"], "halide_mmol": 0.75,
        "substrate_mass": [97.6, "mg"], "substrate_mmol": 0.50, "solvent_ml": 4,
        "product_mass": [112.5, "mg"], "yield": 83, "form": "liquid",
        "eluent": "petroleum ether/ethyl ether = 10/1",
    },
    {
        "suffix": "table3_entry3", "pages": [7], "product": "2c",
        "product_name": "3-benzoyl-5-phenyl-5(E)-3,4,7,8-tetrahydro-2H-oxocin-2-one",
        "pd": [5.5, "mg", 0.025], "pph3": [13.4, "mg", 0.050], "base": [137.7, "mg", 1.0],
        "halide_name": "iodobenzene", "halide_mass": [152.0, "mg"], "halide_mmol": 0.75,
        "substrate_mass": [114.9, "mg"], "substrate_mmol": 0.50, "solvent_ml": 4,
        "product_mass": [120.5, "mg"], "yield": 79, "form": "oil",
        "eluent": "petroleum ether/ethyl ether = 10/1",
    },
    {
        "suffix": "table3_entry4", "pages": [7], "product": "2d",
        "product_name": "3-acetyl-3-methyl-5-phenyl-5(E)-3,4,7,8-tetrahydro-2H-oxocin-2-one",
        "pd": [5.7, "mg", 0.025], "pph3": [13.4, "mg", 0.050], "base": [138.5, "mg", 1.0],
        "halide_name": "iodobenzene", "halide_mass": [152.9, "mg"], "halide_mmol": 0.75,
        "substrate_mass": [90.1, "mg"], "substrate_mmol": 0.50, "solvent_ml": 4,
        "product_mass": [103.4, "mg"], "yield": 81, "form": "oil",
        "eluent": "petroleum ether (b.p. 30–60 °C)/ethyl ether = 10/1",
    },
    {
        "suffix": "table3_entry5", "pages": [7], "product": "2e",
        "product_name": "3-acetyl-3-ethyl-5-phenyl-5(E)-3,4,7,8-tetrahydro-2H-oxocin-2-one",
        "pd": [5.5, "mg", 0.025], "pph3": [13.2, "mg", 0.050], "base": [138.4, "mg", 1.0],
        "halide_name": "iodobenzene", "halide_mass": [255.6, "mg"], "halide_mmol": 1.25,
        "substrate_mass": [98.5, "mg"], "substrate_mmol": 0.50, "solvent_ml": 4,
        "product_mass": [86.2, "mg"], "yield": 63, "form": "white solid",
        "eluent": "petroleum ether/ethyl acetate = 20/1", "mp": [124, 125],
        "mp_solvent": "ethyl ether/petroleum ether",
    },
    {
        "suffix": "table3_entry7", "pages": [7], "product": "2f",
        "product_name": "3-acetyl-3-allyl-5-phenyl-5(E)-3,4,7,8-tetrahydro-2H-oxocin-2-one",
        "pd": [5.7, "mg", 0.025], "pph3": [13.1, "mg", 0.050], "base": [138.7, "mg", 1.0],
        "halide_name": "iodobenzene", "halide_mass": [153.5, "mg"], "halide_mmol": 0.75,
        "substrate_mass": [104.8, "mg"], "substrate_mmol": 0.50, "solvent_ml": 4,
        "product_mass": [99.2, "mg"], "yield": 69, "form": "white solid",
        "eluent": "petroleum ether (b.p. 30–60 °C)/ethyl acetate = 20/1", "mp": [77, 78],
        "mp_solvent": "ethyl ether/petroleum ether",
    },
    {
        "suffix": "table4_entry1", "pages": [7, 8], "product": "2g",
        "product_name": "3-benzoyl-5-p-tolyl-5(E)-3,4,7,8-tetrahydro-2H-oxocin-2-one",
        "pd": [5.8, "mg", 0.025], "pph3": [13.3, "mg", 0.050], "base": [138.0, "mg", 1.0],
        "halide_name": "p-methylphenyl iodide", "halide_mass": [164.1, "mg"], "halide_mmol": 0.75,
        "substrate_mass": [115.0, "mg"], "substrate_mmol": 0.50, "solvent_ml": 4,
        "product_mass": [120.1, "mg"], "yield": 75, "form": "white solid",
        "eluent": "petroleum ether/ethyl ether = 10/1", "mp": [110, 111],
        "mp_solvent": "ethyl ether/petroleum ether",
    },
    {
        "suffix": "table4_entry2", "pages": [8], "product": "2h",
        "product_name": "3-benzoyl-5-(4-methoxyphenyl)-5(E)-3,4,7,8-tetrahydro-2H-oxocin-2-one",
        "pd": [5.5, "mg", 0.025], "pph3": [13.4, "mg", 0.050], "base": [138.5, "mg", 1.0],
        "halide_name": "p-methoxyphenyl iodide", "halide_mass": [176.1, "mg"], "halide_mmol": 0.75,
        "substrate_mass": [115.3, "mg"], "substrate_mmol": 0.50, "solvent_ml": 4,
        "product_mass": [116.8, "mg"], "yield": 69, "form": "white solid",
        "eluent": "petroleum ether (b.p. 30–60 °C)/ethyl ether = 10/1", "mp": [132, 133],
        "mp_solvent": "ethyl ether/petroleum ether",
    },
    {
        "suffix": "table4_entry3", "pages": [8], "product": "2i",
        "product_name": "3-benzoyl-5-(m-tolyl)-5(E)-3,4,7,8-tetrahydro-2H-oxocin-2-one",
        "pd": [5.5, "mg", 0.025], "pph3": [13.3, "mg", 0.050], "base": [138.4, "mg", 1.0],
        "halide_name": "m-methylphenyl iodide", "halide_mass": [163.0, "mg"], "halide_mmol": 0.75,
        "substrate_mass": [115.6, "mg"], "substrate_mmol": 0.50, "solvent_ml": 4,
        "product_mass": [124.8, "mg"], "yield": 78, "form": "oil",
        "eluent": "petroleum ether (b.p. 30–60 °C)/ethyl ether = 10/1",
    },
    {
        "suffix": "table4_entry4", "pages": [8], "product": "2j",
        "product_name": "3-benzoyl-5-(3,4-dimethylphenyl)-5(E)-3,4,7,8-tetrahydro-2H-oxocin-2-one",
        "pd": [5.7, "mg", 0.025], "pph3": [13.3, "mg", 0.050], "base": [138.5, "mg", 1.0],
        "halide_name": "3,4-dimethylphenyl iodide", "halide_mass": [174.5, "mg"], "halide_mmol": 0.75,
        "substrate_mass": [113.9, "mg"], "substrate_mmol": 0.50, "solvent_ml": 4,
        "product_mass": [119.2, "mg"], "yield": 72, "form": "oil",
        "eluent": "petroleum ether (b.p. 30–60 °C)/ethyl ether = 10/1",
    },
    {
        "suffix": "table4_entry5", "pages": [8, 9], "product": "2k",
        "product_name": "3-benzoyl-5-(2,3-dihydrobenzo[b][1,4]dioxin-6-yl)-5(E)-3,4,7,8-tetrahydro-2H-oxocin-2-one",
        "pd": [5.5, "mg", 0.025], "pph3": [13.4, "mg", 0.050], "base": [138.9, "mg", 1.0],
        "halide_name": "6-iodo-1,4-benzodioxane", "halide_mass": [196.5, "mg"], "halide_mmol": 0.75,
        "substrate_mass": [116.0, "mg"], "substrate_mmol": 0.50, "solvent_ml": 4,
        "product_mass": [121.3, "mg"], "yield": 66, "form": "white solid",
        "eluent": "petroleum ether (b.p. 30–60 °C)/ethyl ether = 10/1", "mp": [142, 143],
        "mp_solvent": "ethyl ether/petroleum ether",
    },
    {
        "suffix": "table4_entry6", "pages": [9], "product": "2l",
        "product_name": "3-benzoyl-5-(4-ethoxycarbonylphenyl)-5(E)-3,4,7,8-tetrahydro-2H-oxocin-2-one",
        "pd": [5.7, "mg", 0.025], "pph3": [13.3, "mg", 0.050], "base": [138.7, "mg", 1.0],
        "halide_name": "ethyl 4-iodobenzoate", "halide_mass": [206.9, "mg"], "halide_mmol": 0.75,
        "substrate_mass": [115.9, "mg"], "substrate_mmol": 0.50, "solvent_ml": 4,
        "product_mass": [111.3, "mg"], "yield": 58, "form": "white solid",
        "eluent": "petroleum ether (b.p. 30–60 °C)/dichloromethane = 1/2", "mp": [123, 124],
        "mp_solvent": "ethyl ether/petroleum ether",
    },
    {
        "suffix": "table4_entry7", "pages": [9], "product": "2m",
        "product_name": "3-benzoyl-5-(4-bromophenyl)-5(E)-3,4,7,8-tetrahydro-2H-oxocin-2-one",
        "pd": [5.4, "mg", 0.025], "pph3": [13.5, "mg", 0.050], "base": [137.4, "mg", 1.0],
        "halide_name": "1-bromo-4-iodobenzene", "halide_mass": [211.7, "mg"], "halide_mmol": 0.75,
        "substrate_mass": [113.8, "mg"], "substrate_mmol": 0.50, "solvent_ml": 4,
        "product_mass": [120.8, "mg"], "yield": 63, "form": "solid",
        "eluent": "petroleum ether (b.p. 30–60 °C)/ethyl ether = 15/1", "mp": [136, 137],
        "mp_solvent": "ethyl ether/petroleum ether",
    },
    {
        "suffix": "table4_entry8", "pages": [9], "product": "2n",
        "product_name": "3-benzoyl-5-(3-thienyl)-5(E)-3,4,7,8-tetrahydro-2H-oxocin-2-one",
        "pd": [5.7, "mg", 0.025], "pph3": [13.3, "mg", 0.050], "base": [138.1, "mg", 1.0],
        "halide_name": "3-iodothiophene", "halide_mass": [156.5, "mg"], "halide_mmol": 0.75,
        "substrate_mass": [114.5, "mg"], "substrate_mmol": 0.50, "solvent_ml": 4,
        "product_mass": [108.1, "mg"], "yield": 70, "form": "white solid",
        "eluent": "petroleum ether (b.p. 30–60 °C)/ethyl ether = 10/1", "mp": [120, 122],
        "mp_solvent": "ethyl ether/petroleum ether",
    },
    {
        "suffix": "table4_entry9", "pages": [9], "product": "2o",
        "product_name": "3-benzoyl-5-[(E)-hex-1-enyl]-5(E)-3,4,7,8-tetrahydro-2H-oxocin-2-one",
        "pd": [5.6, "mg", 0.025], "pph3": [13.2, "mg", 0.050], "base": [138.7, "mg", 1.0],
        "halide_name": "(E)-1-iodohex-1-ene", "halide_mass": [157.3, "mg"], "halide_mmol": 0.75,
        "substrate_mass": [114.9, "mg"], "substrate_mmol": 0.50, "solvent_ml": 4,
        "product_mass": [92.0, "mg"], "yield": 59, "form": "white solid",
        "eluent": "petroleum ether (b.p. 30–60 °C)/ethyl ether = 15/1", "mp": [70, 71],
        "mp_solvent": "ethyl ether/petroleum ether",
    },
    {
        "suffix": "table4_entry10", "pages": [9, 10], "product": "2p",
        "product_name": "3-benzoyl-5-styryl-5(E)-3,4,7,8-tetrahydro-2H-oxocin-2-one",
        "pd": [5.7, "mg", 0.025], "pph3": [13.3, "mg", 0.050], "base": [139.0, "mg", 1.0],
        "halide_name": "(E)-(2-iodovinyl)benzene", "halide_mass": [173.3, "mg"], "halide_mmol": 0.75,
        "substrate_mass": [115.0, "mg"], "substrate_mmol": 0.50, "solvent_ml": 4,
        "product_mass": [95.8, "mg"], "yield": 58, "form": "white solid",
        "eluent": "petroleum ether (b.p. 30–60 °C)/ethyl ether = 15/1", "mp": [116, 117],
        "mp_solvent": "ethyl ether/petroleum ether",
    },
    {
        "suffix": "scheme3_e_2q", "pages": [10], "product": "E-2q",
        "product_name": "3-acetyl-5-phenyl-5(E)-3,4,8,9-tetrahydrooxonin-2(3H)-one",
        "pd": [67.3, "mg", 0.3], "pph3": [158.0, "mg", 0.6], "base": [1.6581, "g", 12.0],
        "halide_name": "iodobenzene", "halide_mass": [1.8366, "g"], "halide_mmol": 9.0,
        "substrate_mass": [1.0947, "g"], "substrate_mmol": 6.0, "solvent_ml": 30,
        "product_mass": [1.2690, "g"], "yield": 82, "form": "liquid",
        "eluent": "petroleum ether/ethyl acetate = 10/1", "scaleup": True,
    },
    {
        "suffix": "scheme3_e_2r", "pages": [10], "product": "E-2r",
        "product_name": "3-acetyl-5-(4-methoxyphenyl)-5(E)-3,4,8,9-tetrahydrooxonin-2(3H)-one",
        "pd": [5.8, "mg", 0.025], "pph3": [13.3, "mg", 0.05], "base": [138.5, "mg", 1.0],
        "halide_name": "p-methoxyphenyl iodide", "halide_mass": [174.6, "mg"], "halide_mmol": 0.75,
        "substrate_mass": [92.1, "mg"], "substrate_mmol": 0.5, "solvent_ml": 4,
        "product_mass": [114.4, "mg"], "yield": 78, "form": "liquid",
        "eluent": "petroleum ether/ethyl acetate = 10/1",
    },
    {
        "suffix": "scheme3_e_2s", "pages": [10], "product": "E-2s",
        "product_name": "3-acetyl-5-(4-nitrophenyl)-5(E)-3,4,8,9-tetrahydrooxonin-2(3H)-one",
        "pd": [5.4, "mg", 0.025], "pph3": [13.1, "mg", 0.05], "base": [138.0, "mg", 1.0],
        "halide_name": "1-iodo-4-nitrobenzene", "halide_mass": [186.6, "mg"], "halide_mmol": 0.75,
        "substrate_mass": [91.5, "mg"], "substrate_mmol": 0.5, "solvent_ml": 4,
        "product_mass": [112.8, "mg"], "yield": 74, "form": "yellow solid",
        "eluent": "petroleum ether/ethyl ether = 5/1", "mp": [115, 116],
        "mp_solvent": "ethyl ether/petroleum ether",
    },
    {
        "suffix": "scheme3_e_2t", "pages": [10], "product": "E-2t",
        "product_name": "3-acetyl-5-phenyl-5(E)-3,4,7,8,9,10-hexahydro-2H-oxecin-2-one",
        "pd": [5.7, "mg", 0.025], "pph3": [13.1, "mg", 0.05], "base": [137.4, "mg", 1.0],
        "halide_name": "iodobenzene", "halide_mass": [152.2, "mg"], "halide_mmol": 0.75,
        "substrate_mass": [97.8, "mg"], "substrate_mmol": 0.5, "solvent_ml": 4,
        "product_mass": [96.4, "mg"], "yield": 71, "form": "solid",
        "eluent": "petroleum ether (b.p. 30–60 °C)/ethyl acetate = 15/1", "mp": [100, 101],
        "mp_solvent": "ethyl ether/petroleum ether",
    },
    {
        "suffix": "scheme3_e_2u", "pages": [10, 11], "product": "E-2u",
        "product_name": "3-acetyl-5-(4-bromophenyl)-5(E)-3,4,7,8,9,10-hexahydro-2H-oxecin-2-one",
        "pd": [5.6, "mg", 0.025], "pph3": [13.1, "mg", 0.05], "base": [138.1, "mg", 1.0],
        "halide_name": "1-bromo-4-iodobenzene", "halide_mass": [212.6, "mg"], "halide_mmol": 0.75,
        "substrate_mass": [98.9, "mg"], "substrate_mmol": 0.5, "solvent_ml": 4,
        "product_mass": [122.4, "mg"], "yield": 69, "form": "yellow solid",
        "eluent": "petroleum ether/dichloromethane = 1/1→2/3", "mp": [95, 96],
        "mp_solvent": "ethyl ether/petroleum ether",
    },
    {
        "suffix": "table3_entry6", "pages": [11], "product": "2v",
        "product_name": "3-acetyl-3-propyl-5-phenyl-5(E)-3,4,7,8-tetrahydro-2H-oxocin-2-one",
        "pd": [5.5, "mg", 0.025], "pph3": [13.2, "mg", 0.050], "base": [138.5, "mg", 1.0],
        "halide_name": "iodobenzene", "halide_mass": [255.1, "mg"], "halide_mmol": 1.25,
        "substrate_mass": [106.0, "mg"], "substrate_mmol": 0.50, "solvent_ml": 4,
        "product_mass": [96.1, "mg"], "yield": 67, "form": "white solid",
        "eluent": "petroleum ether/ethyl ether = 10/1", "mp": [111, 112],
        "mp_solvent": "ethyl ether/petroleum ether",
    },
    {
        "suffix": "table3_entryrow_1j", "pages": [11], "product": "2w",
        "product_name": "3-acetyl-3-benzyl-5-phenyl-5(E)-3,4,7,8-tetrahydro-2H-oxocin-2-one",
        "pd": [5.4, "mg", 0.025], "pph3": [13.0, "mg", 0.050], "base": [138.0, "mg", 1.0],
        "halide_name": "iodobenzene", "halide_mass": [155.0, "mg"], "halide_mmol": 0.75,
        "substrate_mass": [128.8, "mg"], "substrate_mmol": 0.50, "solvent_ml": 4,
        "product_mass": [124.9, "mg"], "yield": 75, "form": "white solid",
        "eluent": "petroleum ether/ethyl ether = 10/1", "mp": [114, 115],
        "mp_solvent": "ethyl ether/petroleum ether",
    },
    {
        "suffix": "scheme4_1k_to_2x", "pages": [11], "product": "2x",
        "product_name": "3-acetyl-5-(4-nitrophenyl)-5(E)-3,4,7,8-tetrahydro-2H-oxocin-2-one",
        "pd": [5.6, "mg", 0.025], "pph3": [13.0, "mg", 0.050], "base": [138.7, "mg", 1.0],
        "halide_name": "1-iodo-4-nitrobenzene", "halide_mass": [186.5, "mg"], "halide_mmol": 0.75,
        "substrate_mass": [92.1, "mg"], "substrate_mmol": 0.50, "solvent_ml": 4,
        "product_mass": [99.6, "mg"], "yield": 65, "form": "solid",
        "eluent": "petroleum ether/ethyl acetate = 9/1", "mp": [144, 145],
        "mp_solvent": "CH2Cl2/petroleum ether",
    },
]


updated = []
for item in preparations:
    record_id = f"{DOC}:{item['suffix']}"
    record = deepcopy(by_id[record_id])
    evidence = page_evidence(*item["pages"])
    record["evidence_ids"] = list(dict.fromkeys(record["evidence_ids"] + evidence))
    record["completeness"] = "partial"

    substrate = participant(record, "substrate")
    halide = participant(record, "halide")
    pd_oac2 = participant(record, "pd_oac2")
    pph3 = participant(record, "pph3")
    k2co3 = participant(record, "k2co3")
    ch3cn = participant(record, "ch3cn")
    product = participant(record, "product")

    halide["name"] = fact(item["halide_name"], evidence)
    product["name"] = fact(item["product_name"], evidence)
    upsert_field(substrate["amounts"], "mass", {"number": item["substrate_mass"][0], "unit": item["substrate_mass"][1]}, evidence)
    upsert_field(substrate["amounts"], "amount", {"number": item["substrate_mmol"], "unit": "mmol"}, evidence)
    upsert_field(halide["amounts"], "mass", {"number": item["halide_mass"][0], "unit": item["halide_mass"][1]}, evidence)
    upsert_field(halide["amounts"], "amount", {"number": item["halide_mmol"], "unit": "mmol"}, evidence)
    for p, key in [(pd_oac2, "pd"), (pph3, "pph3"), (k2co3, "base")]:
        upsert_field(p["amounts"], "mass", {"number": item[key][0], "unit": item[key][1]}, evidence)
        upsert_field(p["amounts"], "amount", {"number": item[key][2], "unit": "mmol"}, evidence)
    upsert_field(ch3cn["amounts"], "volume", {"number": item["solvent_ml"], "unit": "mL"}, evidence)

    conditions = condition_list(record)
    upsert_field(conditions, "purification", f"Chromatography; eluent: {item['eluent']}.", evidence)
    if item.get("scaleup"):
        upsert_field(conditions, "atmosphere", "argon", evidence)
        upsert_field(conditions, "operation", "Reagents and CH3CN were added sequentially to a three-necked flask; the mixture was stirred in a preheated oil bath and monitored by TLC.", evidence)
        upsert_field(conditions, "workup", "Filtered to remove the solid; the filtrate was concentrated.", evidence)
        upsert_field(conditions, "purification", f"Silica-gel chromatography; eluent: {item['eluent']}.", evidence)

    # Preserve the field name already used by the table/scheme record while
    # making the detailed paragraph's isolated basis explicit.
    yield_field = next(o for o in record["outcomes"] if "yield" in o["name"] and o["name"] != "yield_measurement_basis")
    yield_field["fact"] = fact({"number": item["yield"], "unit": "%"}, evidence)
    yield_field["target_entity_ids"] = ["product"]
    upsert_field(record["outcomes"], "yield_measurement_basis", "isolated yield", evidence, ["product"])
    upsert_field(record["outcomes"], "product_mass", {"number": item["product_mass"][0], "unit": item["product_mass"][1]}, evidence, ["product"])
    upsert_field(record["outcomes"], "product_form", item["form"], evidence, ["product"])
    if item.get("mp"):
        upsert_field(record["outcomes"], "melting_point", {"minimum": item["mp"][0], "maximum": item["mp"][1], "unit": "°C", "raw_text": f"{item['mp'][0]}–{item['mp'][1]} °C"}, evidence, ["product"])
        upsert_field(record["outcomes"], "melting_point_crystallization_solvent", item["mp_solvent"], evidence, ["product"])

    if item.get("scaleup"):
        record["review"]["unresolved"] = [
            "Product connectivity and stereochemistry remain machine-unverified; no product SMILES is assigned.",
            "The explicitly mentioned supporting information was not supplied or associated.",
        ]
    else:
        record["review"]["unresolved"] = [
            "Atmosphere and workup are not restated in the abbreviated product preparation.",
            "Substrate/product connectivity and stereochemistry remain machine-unverified; no product SMILES is assigned.",
            "The explicitly mentioned supporting information was not supplied or associated.",
        ]
    updated.append(record)


# Page 12 gives crystallographic deposition details, not new syntheses.  Link
# those statements to the corresponding reaction records as characterization
# evidence without promoting structure_verified.
crystal_notes = {
    "table4_entry7": "Crystallographic data for compound 2m were deposited as CCDC 801336.",
    "scheme3_e_2s": "Crystallographic data for compound 2s were deposited as CCDC 801335.",
    "scheme3_e_2u": "Crystallographic data for compound 2u were deposited as CCDC 801334.",
    "scheme4_1k_to_2x": "Crystallographic data for compound 2x were deposited as CCDC 822025.",
}
for suffix, note in crystal_notes.items():
    record = next(r for r in updated if r["record_id"] == f"{DOC}:{suffix}")
    evidence = page_evidence(12)
    record["evidence_ids"] = list(dict.fromkeys(record["evidence_ids"] + evidence))
    record["notes"] = [item for item in record["notes"] if item["value"] != note]
    record["notes"].append(fact(note, evidence))


assert len(updated) == 23
assert len({r["record_id"] for r in updated}) == 23
OUT.mkdir(parents=True, exist_ok=True)
(OUT / "records_pages_0007_0012.json").write_text(json.dumps(updated, ensure_ascii=False, indent=2) + "\n")


rid = lambda suffix: f"{DOC}:{suffix}"
coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 7,
            "state": "attempted",
            "regions": [
                {"region": "upper-left continuation of 2b and left-column 2c preparation", "finding": "The 2b paragraph continues from page 6 with product mass, isolated yield, form, and eluent; the complete 2c batch gives exact charges, product mass, yield, form, and eluent. Both enrich existing Table 3 records.", "evidence_ids": page_evidence(7)},
                {"region": "lower-left 2d preparation", "finding": "Exact 2d charges and isolated outcome were merged into the existing Table 3 entry rather than duplicated.", "evidence_ids": page_evidence(7)},
                {"region": "right-column 2e, 2f, and beginning of 2g", "finding": "Detailed preparations for 2e and 2f and the opening charges for 2g were inspected; 2g continues on page 8.", "evidence_ids": page_evidence(7)},
            ],
            "record_ids": [rid("table3_entry2"), rid("table3_entry3"), rid("table3_entry4"), rid("table3_entry5"), rid("table3_entry7"), rid("table4_entry1")],
            "unresolved": ["The abbreviated preparations do not restate atmosphere or workup; structure assignments and spectra remain machine-unverified."],
        },
        {
            "page": 8,
            "state": "attempted",
            "regions": [
                {"region": "upper-left continuation of 2g and left-column 2h/2i", "finding": "The 2g outcome and the complete 2h and 2i preparations supply exact charges, product masses, isolated yields, forms, eluents, and reported melting points where applicable.", "evidence_ids": page_evidence(8)},
                {"region": "right-column 2j and 2k", "finding": "Detailed preparations for 2j and 2k were merged into existing Table 4 records; 2k characterization continues on page 9.", "evidence_ids": page_evidence(8)},
            ],
            "record_ids": [rid("table4_entry1"), rid("table4_entry2"), rid("table4_entry3"), rid("table4_entry4"), rid("table4_entry5")],
            "unresolved": ["Atmosphere and workup are not restated; the machine extraction does not certify the complex product structures."],
        },
        {
            "page": 9,
            "state": "attempted",
            "regions": [
                {"region": "top-left continuation of 2k and left-column 2l/2m", "finding": "The page opens with characterization of 2k, then reports exact preparations and isolated outcomes for 2l and 2m.", "evidence_ids": page_evidence(9)},
                {"region": "right-column 2n and 2o", "finding": "Exact reagent charges, product masses, isolated yields, forms, eluents, and melting points for 2n and 2o were merged into the corresponding Table 4 records.", "evidence_ids": page_evidence(9)},
                {"region": "lower-right beginning of 2p", "finding": "The 2p batch and isolated outcome begin here; spectral characterization continues on page 10, so both pages are linked to the same existing record.", "evidence_ids": page_evidence(9)},
            ],
            "record_ids": [rid("table4_entry5"), rid("table4_entry6"), rid("table4_entry7"), rid("table4_entry8"), rid("table4_entry9"), rid("table4_entry10")],
            "unresolved": ["Atmosphere and workup are absent from the abbreviated batch descriptions; structures and characterization were not independently certified."],
        },
        {
            "page": 10,
            "state": "attempted",
            "regions": [
                {"region": "upper-left continuation of 2p", "finding": "Only spectral characterization continues; it remains linked to the page-9 2p preparation and is not counted as another experiment.", "evidence_ids": page_evidence(10)},
                {"region": "left-column one-gram-scale 2q and 2r", "finding": "The 2q scale-up gives sequential additions, argon atmosphere, workup, chromatography, and gram-scale isolated outcome; 2r gives an abbreviated exact batch and isolated outcome.", "evidence_ids": page_evidence(10)},
                {"region": "right-column 2s, 2t, and beginning of 2u", "finding": "Detailed preparations for 2s and 2t and the opening charges for 2u were merged into existing Scheme 3 records; 2u continues on page 11.", "evidence_ids": page_evidence(10)},
            ],
            "record_ids": [rid("table4_entry10"), rid("scheme3_e_2q"), rid("scheme3_e_2r"), rid("scheme3_e_2s"), rid("scheme3_e_2t"), rid("scheme3_e_2u")],
            "unresolved": ["Only 2q restates atmosphere and workup; all complex product structures remain machine-unverified."],
        },
        {
            "page": 11,
            "state": "attempted",
            "regions": [
                {"region": "upper-left continuation of 2u", "finding": "Product mass, isolated yield, yellow-solid form, gradient eluent, and melting point complete the page-10 2u batch.", "evidence_ids": page_evidence(11)},
                {"region": "left-column 2v and 2w", "finding": "Exact detailed batches for 2v and 2w enrich the existing Table 3 records, including the 2.5-equivalent iodobenzene charge for 2v already specified by the table footnote.", "evidence_ids": page_evidence(11)},
                {"region": "upper-right 2x preparation", "finding": "The detailed 2x preparation supplies exact charges, product mass, isolated-yield basis, eluent, form, and melting point; the >8:1 dr remains linked from Scheme 4 on page 5.", "evidence_ids": page_evidence(11)},
                {"region": "lower-right acknowledgements and references 1–4", "finding": "No new reaction experiment is reported; cited prior work was not attributed to this paper.", "evidence_ids": page_evidence(11)},
            ],
            "record_ids": [rid("scheme3_e_2u"), rid("table3_entry6"), rid("table3_entryrow_1j"), rid("scheme4_1k_to_2x")],
            "unresolved": ["Atmosphere and workup are not restated in these abbreviated preparations; product stereochemistry is not machine-certified."],
        },
        {
            "page": 12,
            "state": "attempted",
            "regions": [
                {"region": "left column references 5–16", "finding": "These are cited reviews and prior literature, plus the beginning of a crystallographic footnote; they are not new reaction batches from this paper.", "evidence_ids": page_evidence(12)},
                {"region": "right column crystallographic footnotes 16–19", "finding": "CCDC deposition details for 2m, 2s, 2u, and 2x were linked as characterization notes to their existing reaction records; no structure was automatically marked verified.", "evidence_ids": page_evidence(12)},
                {"region": "lower-right references 20–21", "finding": "Prior mechanistic literature and a known terminal-allenol preparation are citations, not experiments newly reported in this paper.", "evidence_ids": page_evidence(12)},
            ],
            "record_ids": [rid("table4_entry7"), rid("scheme3_e_2s"), rid("scheme3_e_2u"), rid("scheme4_1k_to_2x")],
            "unresolved": ["Crystallographic deposits were not independently retrieved; the cited Supporting Information is unassociated."],
        },
    ],
}

coverage_dir = ROOT / "runs/current/coverage"
coverage_dir.mkdir(parents=True, exist_ok=True)
(coverage_dir / "pages_0007_0012.json").write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

tasks_path = ROOT / "runs/current/tasks.json"
tasks = json.loads(tasks_path.read_text())
for task in tasks:
    if task["document_id"] == DOC and task["task_id"] in {ev(page, "text") for page in range(7, 13)}:
        task["state"] = "attempted"
        task["reason"] = "Original page image and extracted text inspected for detailed preparations, continuations, characterization, references, and missing details in session pages 7-12."
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"updated_records": len(updated), "new_record_ids": 0, "coverage_pages": [p["page"] for p in coverage["pages"]]}, ensure_ascii=False))
