#!/usr/bin/env python3
"""Enrich existing evidence-linked records from PDF pages 7-10."""
from __future__ import annotations

import copy
import json
from pathlib import Path

DOC = "doc_9eeb484825ce883e"
BASE = Path(__file__).resolve().parents[1]
DATASET = BASE / "dataset.json"
OUT = BASE / "raw_model" / "extracted_records_pages_0007_0010.json"
COVERAGE = BASE / "coverage" / "pages_0007_0010.json"


def ev(*pages: int) -> list[str]:
    return [f"{DOC}:page{p}:{kind}" for p in pages for kind in ("text", "image")]


def fact(value, evidence=None):
    return {
        "value": value,
        "evidence_ids": list(dict.fromkeys(evidence or [])),
        "verification": "missing" if value is None else "unreviewed",
    }


def field(name, value, evidence=None, targets=None):
    result = {"name": name, "fact": fact(value, evidence)}
    if targets:
        result["target_entity_ids"] = list(targets)
    return result


def quantity(name, number, unit, evidence):
    return field(name, {"number": number, "unit": unit}, evidence)


def set_amounts(record, entity, values, evidence):
    participant = next(p for p in record["participants"] if p["entity_id"] == entity)
    participant["amounts"] = [quantity(name, number, unit, evidence) for name, number, unit in values]


def set_smiles_and_name(record, entity, smiles, name, evidence):
    participant = next(p for p in record["participants"] if p["entity_id"] == entity)
    participant["name"] = fact(name, evidence)
    participant["smiles"] = fact(smiles, evidence)
    participant["smiles_parseable"] = None
    participant["structure_verified"] = False


def set_condition(record, name, value, evidence):
    conditions = record["steps"][0]["conditions"]
    existing = next((x for x in conditions if x["name"] == name), None)
    replacement = field(name, value, evidence)
    if existing is None:
        conditions.append(replacement)
    else:
        existing.clear()
        existing.update(replacement)


def set_outcome(record, name, value, evidence, targets=None):
    existing = next((x for x in record["outcomes"] if x["name"] == name), None)
    replacement = field(name, value, evidence, targets)
    if existing is None:
        record["outcomes"].append(replacement)
    else:
        existing.clear()
        existing.update(replacement)


def add_evidence(record, evidence):
    record["evidence_ids"] = list(dict.fromkeys(record["evidence_ids"] + list(evidence)))


def add_note(record, text, evidence):
    if not any(n["value"] == text for n in record["notes"]):
        record["notes"].append(fact(text, evidence))


def keep_unresolved(record, extra=()):
    old = record["review"]["unresolved"]
    retained = [x for x in old if "Supporting-information association" in x or "stereochemistry" in x.lower()]
    record["review"]["unresolved"] = list(dict.fromkeys(retained + list(extra)))


data = json.loads(DATASET.read_text())
existing = {r["record_id"]: r for r in data["experiments"]}
updates: dict[str, dict] = {}


def get(suffix: str) -> dict:
    rid = f"{DOC}:{suffix}"
    if rid not in updates:
        updates[rid] = copy.deepcopy(existing[rid])
    return updates[rid]


# Fully specified, connectivity-only product candidates from the printed names/drawings.
# They remain unverified after merge; stereochemical labels are not encoded.
product_info = {
    "3a": ("4-(3-(5-methylfuranyl))-5-phenyl-3-propyl-2(5H)-furanone", "O=C1OC(c2ccccc2)C(c2cc(C)oc2)=C1CCC"),
    "3b": ("3-methyl-4-(3-(5-methylfuranyl))-5-phenyl-2(5H)-furanone", "O=C1OC(c2ccccc2)C(c2cc(C)oc2)=C1C"),
    "3d": ("3-allyl-4-(3-(5-methylfuranyl))-5-phenyl-2(5H)-furanone", "O=C1OC(c2ccccc2)C(c2cc(C)oc2)=C1CC=C"),
    "3e": ("3-methyl-4-(3-(5-methylfuranyl))-5-(1-naphthyl)-2(5H)-furanone", "O=C1OC(c2cccc3ccccc23)C(c2cc(C)oc2)=C1C"),
    "3g": ("3-benzyl-5-methyl-4-(3-(5-methylfuranyl))-2(5H)-furanone", "O=C1OC(C)C(c2cc(C)oc2)=C1Cc1ccccc1"),
    "3h": ("5-ethyl-3-methyl-4-(3-(5-methylfuranyl))-5-phenyl-2(5H)-furanone", "O=C1OC(CC)(c2ccccc2)C(c2cc(C)oc2)=C1C"),
    "3i": ("5-heptyl-4-(3-(5-methylfuranyl))-2(5H)-furanone", "O=C1OC(CCCCCCC)C(c2cc(C)oc2)=C1"),
    "3j": ("4-(3-(5-methylfuranyl))-5-(4-bromophenyl)-3-propyl-2(5H)-furanone", "O=C1OC(c2ccc(Br)cc2)C(c2cc(C)oc2)=C1CCC"),
    "3k": ("4-(3-(5-butylfuranyl))-5-phenyl-3-propyl-2(5H)-furanone", "O=C1OC(c2ccccc2)C(c2cc(CCCC)oc2)=C1CCC"),
    "3l": ("4-(3-(5-butylfuranyl))-3-methyl-5-phenyl-2(5H)-furanone", "O=C1OC(c2ccccc2)C(c2cc(CCCC)oc2)=C1C"),
    "3m": ("3-allyl-4-(3-(5-butylfuranyl))-5-phenyl-2(5H)-furanone", "O=C1OC(c2ccccc2)C(c2cc(CCCC)oc2)=C1CC=C"),
    "3n": ("3-methyl-4-(3-(5-butylfuranyl))-5-(1-naphthyl)-2(5H)-furanone", "O=C1OC(c2cccc3ccccc23)C(c2cc(CCCC)oc2)=C1C"),
    "3o": ("4-(3-(5-butylfuranyl))-5-ethyl-3-methyl-5-phenyl-2(5H)-furanone", "O=C1OC(CC)(c2ccccc2)C(c2cc(CCCC)oc2)=C1C"),
    "3p": ("4-(3-(5-butylfuranyl))-5-heptyl-2(5H)-furanone", "O=C1OC(CCCCCCC)C(c2cc(CCCC)oc2)=C1"),
    "3q": ("4-(3-(5-benzylfuranyl))-5-phenyl-3-propyl-2(5H)-furanone", "O=C1OC(c2ccccc2)C(c2cc(Cc3ccccc3)oc2)=C1CCC"),
    "3r": ("4-(3-(5-benzylfuranyl))-3-methyl-5-phenyl-2(5H)-furanone", "O=C1OC(c2ccccc2)C(c2cc(Cc3ccccc3)oc2)=C1C"),
    "3s": ("3-allyl-4-(3-(5-benzylfuranyl))-5-phenyl-2(5H)-furanone", "O=C1OC(c2ccccc2)C(c2cc(Cc3ccccc3)oc2)=C1CC=C"),
    "3t": ("4-(3-(5-benzylfuranyl))-3-methyl-5-(1-naphthyl)-2(5H)-furanone", "O=C1OC(c2cccc3ccccc23)C(c2cc(Cc3ccccc3)oc2)=C1C"),
    "3u": ("4-(3-(5-benzylfuranyl))-5-ethyl-3-methyl-5-phenyl-2(5H)-furanone", "O=C1OC(CC)(c2ccccc2)C(c2cc(Cc3ccccc3)oc2)=C1C"),
    "3v": ("4-(3-(5-benzylfuranyl))-5-heptyl-2(5H)-furanone", "O=C1OC(CCCCCCC)C(c2cc(Cc3ccccc3)oc2)=C1"),
}

# Detailed achiral procedures. Values are copied from the individual experimental paragraphs.
scope = {
    "3g": (7, "1g", (94, 0.5), "2a", (207, 2.5), (6, 0.023), 5, 4, "flash chromatography on silica gel (petroleum ether/ethyl acetate 10:1, then CH2Cl2)", 120, "oil", 90),
    "3h": (7, "1h", (101, 0.5), "2a", (205, 2.5), (6, 0.023), 5, 4, "flash chromatography on silica gel (petroleum ether/Et2O 10:1)", 120, "oil", 85),
    "3i": (7, "1i", (91, 0.5), "2a", (208, 2.5), (6, 0.023), 5, 4, "flash chromatography on silica gel (petroleum ether/Et2O 2.5:1)", 91, "oil", 69),
    "3j": (7, "1j", (70, 0.249), "2a", (103, 1.26), (3, 0.012), 3, 4.5, "flash chromatography on silica gel (petroleum ether/Et2O 3:1)", 63, "white solid", 70),
    "3k": (7, "1a", (50, 0.248), "2b", (157, 1.27), (3, 0.012), 3, 4, "flash chromatography on silica gel (petroleum ether/Et2O 3:1, then CH2Cl2)", 67, "oil", 84),
    "3l": (7, "1b", (44, 0.253), "2b", (156, 1.258), (3, 0.012), 3, 4, "flash chromatography on silica gel (ethyl acetate/petroleum ether 1:5)", 47, "oil", 63),
    "3m": (7, "1d", (50, 0.25), "2b", (157, 1.266), (3, 0.012), 3, 4, "flash chromatography on silica gel (petroleum ether/ethyl acetate 6:1)", 53, "oil", 66),
    "3n": (7, "1e", (58, 0.259), "2b", (162, 1.306), (3, 0.012), 3, 4, "flash chromatography on silica gel (petroleum ether/ethyl acetate 5:1)", 71, "oil", 79),
    "3o": (7, "1h", (50, 0.248), "2b", (153, 1.23), (3, 0.012), 3, 4, "flash chromatography on silica gel (petroleum ether/Et2O 3:1, then CH2Cl2)", 69, "oil", 86),
    "3p": (7, "1i", (45, 0.247), "2b", (154, 1.24), (3, 0.012), 3, 4, "flash chromatography on silica gel (petroleum ether/Et2O 3:1)", 52, "oil", 69),
    "3q": (7, "1a", (50, 0.248), "2c", (197, 1.25), (3, 0.012), 3, 4, "flash chromatography on silica gel (petroleum ether/Et2O 3:1)", 66, "oil", 74),
    "3r": ((7, 8), "1b", (44, 0.253), "2c", (198, 1.253), (3, 0.012), 3, 4, "flash chromatography on silica gel (ethyl acetate/petroleum ether 1:5)", 72, "oil", 86),
    "3s": (8, "1d", (31, 0.155), "2c", (125, 0.791), (2, 0.0077), 2, 4, "flash chromatography on silica gel (petroleum ether/ethyl acetate 5:1)", 45, "oil", 82),
    "3t": (8, "1e", (55, 0.246), "2c", (199, 1.259), (3, 0.012), 3, 4, "flash chromatography on silica gel (petroleum ether/ethyl acetate 5:1)", 84, "oil", 90),
    "3u": (8, "1h", (50, 0.248), "2c", (195, 1.24), (3, 0.012), 3, 4, "flash chromatography on silica gel (petroleum ether/Et2O 2.5:1)", 74, "oil", 84),
    "3v": (8, "1i", (45, 0.247), "2c", (197, 1.25), (3, 0.012), 3, 4, "flash chromatography on silica gel (petroleum ether/Et2O 2.6:1, then CH2Cl2)", 59, "oil", 71),
}
scope_ids = {
    "3g": 7, "3h": 8, "3i": 9, "3j": 10, "3k": 11, "3l": 12, "3m": 13,
    "3n": 14, "3o": 15, "3p": 16, "3q": 17, "3r": 18, "3s": 19,
    "3t": 20, "3u": 21, "3v": 22,
}

for product, values in scope.items():
    pages, acid, acid_q, ketone, ketone_q, catalyst_q, solvent_v, hours, purification, mass, form, yld = values
    pages = (pages,) if isinstance(pages, int) else pages
    evidence = ev(*pages)
    rec = get(f"table2_entry_{scope_ids[product]:02d}_{product}")
    add_evidence(rec, evidence)
    set_amounts(rec, acid, [("mass", acid_q[0], "mg"), ("amount", acid_q[1], "mmol")], evidence)
    set_amounts(rec, ketone, [("mass", ketone_q[0], "mg"), ("amount", ketone_q[1], "mmol")], evidence)
    set_amounts(rec, "cat", [("mass", catalyst_q[0], "mg"), ("amount", catalyst_q[1], "mmol")], evidence)
    set_amounts(rec, "solvent", [("volume", solvent_v, "mL")], evidence)
    set_smiles_and_name(rec, product, product_info[product][1], product_info[product][0], evidence)
    set_condition(rec, "temperature", "r.t.", evidence)
    set_condition(rec, "time", {"number": hours, "unit": "h"}, evidence)
    set_condition(rec, "purification", purification, evidence)
    set_outcome(rec, "product_yield", {"number": yld, "unit": "%"}, list(dict.fromkeys(rec["outcomes"][0]["fact"]["evidence_ids"] + evidence)), [product])
    set_outcome(rec, "product_mass", {"number": mass, "unit": "mg"}, evidence, [product])
    set_outcome(rec, "physical_form", form, evidence, [product])
    set_outcome(rec, "yield_measurement_basis", "isolated after flash chromatography", evidence, [product])
    keep_unresolved(rec, ["Supporting-information association is unestablished."])

# Product 3a was already procedurally complete on page 6; page 10 adds crystallography only.
rec = get("table2_entry_01_3a")
add_evidence(rec, ev(10))
add_note(rec, "Reference 20 reports X-ray crystal data for 3a and CCDC-210552.", ev(10))


# Detailed optically active preparations. HPLC/rotation strings are kept verbatim-like,
# while yield/ee quantities stay structured and product-specific.
chiral = {
    "table3_entry_01_3a": (8, "S_1a", (50, 0.248, 98), "2a", (103, 1.26), (3, 0.012), 3, 4, "flash chromatography on silica gel (petroleum ether/Et2O 5:1)", "S_3a", "3a", 61, 87, 95, "AD column; 0.7 mL/min; hexane/iPrOH 80:20", "+132° (c=1.07, EtOH, T=20 °C)"),
    "table3_entry_04_3b": (8, "R_1b", (44, 0.253, 99), "2a", (105, 1.28), (3, 0.012), 3, 4, "flash chromatography on silica gel (ethyl acetate/petroleum ether 1:2, then CH2Cl2)", "R_3b", "3b", 49, 76, 97, "AD column; 0.7 mL/min; hexane/iPrOH 85:15", "-135° (c=1.145, EtOH, T=20 °C)"),
    "table3_entry_07_3d": (8, "S_1d", (50, 0.25, 98), "2a", (104, 1.27), (3, 0.012), 3, 6, "flash chromatography on silica gel (petroleum ether/ethyl acetate 5:1)", "S_3d", "3d", 51, 73, 97, "OD column; 0.7 mL/min; hexane/iPrOH 80:20", "+70° (c=1.045, CHCl3, T=20 °C)"),
    "table3_entry_10_3e": (8, "S_1e", (56, 0.25, 98), "2a", (104, 1.27), (3, 0.012), 3, 4, "flash chromatography on silica gel (petroleum ether/ethyl acetate 3:1)", "S_3e", "3e", 56, 74, 97, "OD column; 0.7 mL/min; hexane/iPrOH 60:40", "-34° (c=1.635, CHCl3, T=20 °C)"),
    "table3_entry_02_3k": (8, "R_1a", (50, 0.248, 97), "2b", (154, 1.24), (3, 0.012), 3, 4, "flash chromatography on silica gel (petroleum ether/ethyl acetate 3:1)", "R_3k", "3k", 60, 75, ">99", "OD column; 0.7 mL/min; hexane/iPrOH 70:30", "-56° (c=1.190, CHCl3, T=20 °C)"),
    "table3_entry_05_3l": (8, "R_1b", (44, 0.253, 99), "2b", (157, 1.27), (3, 0.012), 3, 4, "flash chromatography on silica gel (ethyl acetate/petroleum ether 1:5)", "R_3l", "3l", 61, 81, 99, "OD column; 0.7 mL/min; hexane/iPrOH 90:10", "-42° (c=2.540, CHCl3, T=20 °C)"),
    "table3_entry_08_3m": (8, "S_1d", (50, 0.25, 98), "2b", (157, 1.27), (3, 0.012), 3, 4, "flash chromatography on silica gel (petroleum ether/ethyl acetate 6:1)", "S_3m", "3m", 54, 67, 99, "OD column; 0.7 mL/min; hexane/iPrOH 90:10", "+49° (c=1.400, CHCl3, T=20 °C)"),
    "table3_entry_11_3n": (8, "S_1e", (56, 0.25, 98), "2b", (160, 1.29), (3, 0.012), 3, 4, "flash chromatography on silica gel (petroleum ether/ethyl acetate 4:1)", "S_3n", "3n", 66, 76, 99, "AS column; 0.7 mL/min; hexane/iPrOH 80:20", "-39° (c=3.125, CHCl3, T=20 °C)"),
    "table3_entry_03_3q": (8, "R_1a", (50, 0.248, 97), "2c", (198, 1.25), (3, 0.012), 3, 4, "flash chromatography on silica gel (petroleum ether/ethyl acetate 8:1)", "R_3q", "3q", 76, 86, ">99", "OD column; 0.7 mL/min; hexane/iPrOH 60:40", "-44° (c=1.785, CHCl3, T=20 °C)"),
    "table3_entry_06_3r": (9, "R_1b", (44, 0.253, 99), "2c", (198, 1.253), (3, 0.012), 3, 4, "flash chromatography on silica gel (ethyl acetate/petroleum ether 1:3, then CH2Cl2)", "R_3r", "3r", 60, 72, 96, "AS column; 0.7 mL/min; hexane/iPrOH 60:40", "-35° (c=2.570, CHCl3, T=20 °C)"),
    "table3_entry_09_3s": (9, "S_1d", (31, 0.155, 98), "2c", (124, 0.785), (2, 0.0077), 2, 4, "flash chromatography on silica gel (petroleum ether/ethyl acetate 5:1)", "S_3s", "3s", 37, 67, 99, "AS column; 0.7 mL/min; hexane/iPrOH 60:40", "+45° (c=1.315, CHCl3, T=20 °C)"),
    "table3_entry_12_3t": (9, "S_1e", (56, 0.25, 98), "2c", (200, 1.266), (3, 0.012), 3, 4, "flash chromatography on silica gel (petroleum ether/ethyl acetate 5:1)", "S_3t", "3t", 83, 87, ">99", "AS column; 0.7 mL/min; hexane/iPrOH 60:40", "-9.7° (c=2.675, CHCl3, T=20 °C)"),
}

for suffix, values in chiral.items():
    page, acid, acid_q, ketone, ketone_q, catalyst_q, solvent_v, hours, purification, product_id, product, mass, yld, ee_value, hplc, rotation = values
    evidence = ev(page)
    rec = get(suffix)
    add_evidence(rec, evidence)
    set_amounts(rec, acid, [("mass", acid_q[0], "mg"), ("amount", acid_q[1], "mmol"), ("starting_material_ee", acid_q[2], "%")], evidence)
    set_amounts(rec, ketone, [("mass", ketone_q[0], "mg"), ("amount", ketone_q[1], "mmol")], evidence)
    set_amounts(rec, "cat", [("mass", catalyst_q[0], "mg"), ("amount", catalyst_q[1], "mmol")], evidence)
    set_amounts(rec, "solvent", [("volume", solvent_v, "mL")], evidence)
    set_smiles_and_name(rec, product_id, product_info[product][1], product_info[product][0], evidence)
    set_condition(rec, "temperature", "r.t.", evidence)
    set_condition(rec, "time", {"number": hours, "unit": "h"}, evidence)
    set_condition(rec, "purification", purification, evidence)
    set_outcome(rec, "product_yield", {"number": yld, "unit": "%"}, list(dict.fromkeys(rec["outcomes"][0]["fact"]["evidence_ids"] + evidence)), [product_id])
    set_outcome(rec, "product_mass", {"number": mass, "unit": "mg"}, evidence, [product_id])
    set_outcome(rec, "yield_measurement_basis", "isolated after flash chromatography", evidence, [product_id])
    set_outcome(rec, "hplc_condition", hplc, evidence, [product_id])
    set_outcome(rec, "specific_rotation", rotation, evidence, [product_id])
    ee_quantity = {"number": 99, "unit": "%", "qualifier": "gt", "raw_text": ">99%"} if ee_value == ">99" else {"number": ee_value, "unit": "%"}
    if product == "3s":
        old_ee = next(x for x in rec["outcomes"] if x["name"] == "product_ee")
        old_ee["name"] = "table_product_ee"
        old_ee["target_entity_ids"] = [product_id]
        set_outcome(rec, "experimental_section_product_ee", ee_quantity, evidence, [product_id])
        keep_unresolved(rec, ["Table 3 reports 98% ee for 3s, whereas the individual experimental paragraph reports 99% ee; both source values are retained without adjudication.", "Axial/product stereochemistry is preserved in labels but is not encoded in candidate SMILES.", "Supporting-information association is unestablished."])
    else:
        current = next(x for x in rec["outcomes"] if x["name"] == "product_ee")
        combined = list(dict.fromkeys(current["fact"]["evidence_ids"] + evidence))
        set_outcome(rec, "product_ee", ee_quantity, combined, [product_id])
        keep_unresolved(rec, ["Axial/product stereochemistry is preserved in labels but is not encoded in candidate SMILES.", "Supporting-information association is unestablished."])


# Equation 3 is not a Table 3 row; enrich its existing independent record from page 8.
rec = get("equation3_chiral_1j_to_3j")
evidence = ev(8)
add_evidence(rec, evidence + ev(10))
set_amounts(rec, "S_1j", [("mass", 43, "mg"), ("amount", 0.153, "mmol"), ("starting_material_ee", 99, "%")], evidence)
set_amounts(rec, "2a", [("mass", 67, "mg"), ("amount", 0.817, "mmol")], evidence)
set_amounts(rec, "cat", [("mass", 2, "mg"), ("amount", 0.0077, "mmol")], evidence)
set_amounts(rec, "solvent", [("volume", 3, "mL")], evidence)
set_smiles_and_name(rec, "S_3j", product_info["3j"][1], "(S)-" + product_info["3j"][0], evidence)
set_condition(rec, "temperature", "r.t.", evidence)
set_condition(rec, "time", {"number": 4, "unit": "h"}, evidence)
set_condition(rec, "purification", "flash chromatography on silica gel (petroleum ether/Et2O 3:1)", evidence)
set_outcome(rec, "product_yield", {"number": 76, "unit": "%"}, ev(3, 8), ["S_3j"])
set_outcome(rec, "product_mass", {"number": 42, "unit": "mg"}, evidence, ["S_3j"])
set_outcome(rec, "product_ee", {"number": 99, "unit": "%"}, ev(3, 8), ["S_3j"])
set_outcome(rec, "yield_measurement_basis", "isolated after flash chromatography", evidence, ["S_3j"])
set_outcome(rec, "hplc_condition", "AD column; 0.7 mL/min; hexane/iPrOH 95:5", evidence, ["S_3j"])
set_outcome(rec, "specific_rotation", "+122° (c=0.505, EtOH, T=20 °C)", evidence, ["S_3j"])
add_note(rec, "Reference 21 reports X-ray crystal data for (S)-(+)-3j and CCDC-210551.", ev(10))
keep_unresolved(rec, ["Reactant axial stereochemistry and product stereochemistry are preserved in labels but are not encoded in candidate SMILES.", "Supporting-information association is unestablished."])


# Page 9 adds characterization for byproducts, while page 10 gives the 8a crystal data.
rec = get("scheme2_byproduct_distribution")
add_evidence(rec, ev(9, 10))
add_note(rec, "Page 9 reports NMR characterization for 6a, NMR/IR/MS/elemental-analysis characterization for 7a, and NMR/MS/IR characterization for 8a; it does not provide a separate preparation procedure.", ev(9))
add_note(rec, "Reference 22 reports X-ray crystal data for 8a and CCDC-210550.", ev(10))


# Coverage is page-scoped and cites each page's own rendered image evidence.
p7_scope = [f"{DOC}:table2_entry_{scope_ids[p]:02d}_{p}" for p in ("3g", "3h", "3i", "3j", "3k", "3l", "3m", "3n", "3o", "3p", "3q", "3r")]
p8_scope = [f"{DOC}:table2_entry_{scope_ids[p]:02d}_{p}" for p in ("3r", "3s", "3t", "3u", "3v")]
p8_chiral = [f"{DOC}:{x}" for x in (
    "table3_entry_01_3a", "table3_entry_04_3b", "table3_entry_07_3d", "table3_entry_10_3e",
    "equation3_chiral_1j_to_3j", "table3_entry_02_3k", "table3_entry_05_3l",
    "table3_entry_08_3m", "table3_entry_11_3n", "table3_entry_03_3q",
)]
p9_chiral = [f"{DOC}:{x}" for x in ("table3_entry_06_3r", "table3_entry_09_3s", "table3_entry_12_3t")]
coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 7,
            "state": "attempted",
            "regions": [
                {"region": "left column, continuation of 3g followed by individual procedures 3h-3l", "finding": "Detailed quantities, reaction times, chromatographic purification, product masses/forms, and yields continue the existing Table 2 scope experiments; they were merged into the matching records rather than duplicated.", "evidence_ids": ev(7)},
                {"region": "right column, individual procedures 3m-3q and beginning of 3r", "finding": "Detailed procedures enrich existing Table 2 rows; the 3r paragraph continues on page 8.", "evidence_ids": ev(7)},
            ],
            "record_ids": p7_scope,
            "unresolved": ["No supporting-information file was explicitly provided or associated.", "Connectivity-only product SMILES remain unverified against an independent structure review."],
        },
        {
            "page": 8,
            "state": "attempted",
            "regions": [
                {"region": "left column, continuation of 3r and procedures 3s-3v", "finding": "Detailed achiral procedures complete the existing Table 2 scope records for 3r-3v.", "evidence_ids": ev(8)},
                {"region": "lower-left and right columns, optically active product procedures", "finding": "Detailed preparations for chiral 3a, 3b, 3d, 3e, 3j, 3k, 3l, 3m, 3n, and 3q add exact quantities, isolation, ee/HPLC, and optical rotation to existing Equation 3/Table 3 records.", "evidence_ids": ev(8)},
            ],
            "record_ids": list(dict.fromkeys(p8_scope + p8_chiral)),
            "unresolved": ["The printed stereochemical labels are retained textually; axial/product stereochemistry is not encoded in candidate SMILES.", "No supporting-information file was explicitly provided or associated."],
        },
        {
            "page": 9,
            "state": "attempted",
            "regions": [
                {"region": "upper-left, optically active 3r-3t procedures", "finding": "Detailed procedures enrich existing Table 3 entries. For 3s the paragraph reports 99% ee while Table 3 reports 98% ee; both values are retained as a source discrepancy.", "evidence_ids": ev(9)},
                {"region": "mid-left, compounds 6a-8a characterization", "finding": "Spectroscopic/analytical characterization for already reported Scheme 2 byproducts; no separate preparation procedure is given, so no new experiment record was created.", "evidence_ids": ev(9)},
                {"region": "acknowledgment and references 1-18", "finding": "Bibliographic and acknowledgment content only; cited prior work is not reclassified as experiments in this paper.", "evidence_ids": ev(9)},
            ],
            "record_ids": p9_chiral + [f"{DOC}:scheme2_byproduct_distribution"],
            "unresolved": ["The 3s ee discrepancy (98% in Table 3 versus 99% in the individual procedure) is unresolved by the source.", "No supporting-information file was explicitly provided or associated."],
        },
        {
            "page": 10,
            "state": "attempted",
            "regions": [
                {"region": "references 20-22, crystallographic data for 3a, (S)-3j, and 8a", "finding": "Product characterization and CCDC deposition data were linked to the existing records; these are not separate reaction experiments.", "evidence_ids": ev(10)},
                {"region": "references 19 and 23-29 plus received/revised dates", "finding": "Prior-literature citations and publication metadata only; no current-paper reaction experiment or new condition is reported.", "evidence_ids": ev(10)},
            ],
            "record_ids": [f"{DOC}:table2_entry_01_3a", f"{DOC}:equation3_chiral_1j_to_3j", f"{DOC}:scheme2_byproduct_distribution"],
            "unresolved": ["The CCDC availability statements do not establish an associated experimental SI file for this extraction dataset."],
        },
    ],
}

OUT.write_text(json.dumps(list(updates.values()), ensure_ascii=False, indent=2) + "\n")
COVERAGE.parent.mkdir(parents=True, exist_ok=True)
COVERAGE.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

# Mark only the four inspected page-text tasks attempted.
tasks_path = BASE / "tasks.json"
tasks = json.loads(tasks_path.read_text())
for task in tasks:
    if task["document_id"] == DOC and task["evidence_id"] in {f"{DOC}:page{p}:text" for p in range(7, 11)}:
        task["state"] = "attempted"
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"updated_records": len(updates), "raw": str(OUT), "coverage": str(COVERAGE)}, ensure_ascii=False))
