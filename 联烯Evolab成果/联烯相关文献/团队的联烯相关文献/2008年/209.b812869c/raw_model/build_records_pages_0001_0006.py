#!/usr/bin/env python3
"""Build evidence-linked machine records for 209.b812869c.pdf, PDF pages 1-6."""
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "runs/current/raw_model/records_pages_0001_0006.json"
COVERAGE = ROOT / "runs/current/coverage/pages_0001_0006.json"
TASKS = ROOT / "runs/current/tasks.json"
DOC = "doc_4cf0857e25b75c14"


def ev(page: int) -> list[str]:
    return [f"{DOC}:page{page}:image", f"{DOC}:page{page}:text"]


def merged_ev(*pages: int) -> list[str]:
    result: list[str] = []
    for page in pages:
        for item in ev(page):
            if item not in result:
                result.append(item)
    return result


def fact(value, evidence=()):
    return {
        "value": value,
        "evidence_ids": list(evidence) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def q(number, unit, **extra):
    value = {"number": number, "unit": unit}
    value.update(extra)
    return value


def field(name, value, evidence=(), targets=None):
    item = {"name": name, "fact": fact(value, evidence)}
    if targets:
        item["target_entity_ids"] = list(targets)
    return item


def amount(name, number, unit, evidence):
    return field(name, q(number, unit), evidence)


def participant(entity_id, role, label, name, smiles, evidence, amounts=()):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence),
        "smiles": fact(smiles, evidence),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": list(amounts),
    }


def record(suffix, kind, evidence, participants, conditions, outcomes, unresolved, notes=(), source_id=None):
    rid = f"{DOC}:{suffix}"
    return {
        "record_id": rid,
        "document_id": DOC,
        "source_reaction_id": source_id or suffix,
        "record_kind": kind,
        "status": "needs_review",
        "completeness": "partial",
        "evidence_ids": list(evidence),
        "participants": list(participants),
        "steps": [{
            "step_id": "reaction",
            "participant_ids": [p["entity_id"] for p in participants],
            "conditions": list(conditions),
        }],
        "outcomes": list(outcomes),
        "notes": [fact(n, evidence) for n in notes],
        "review": {
            "method": "model",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": list(unresolved),
        },
    }


SMILES = {
    "1a": "O=CC=C=C1CCCCC1", "2a": "C=CCC(O)C=C=C1CCCCC1",
    "1b": "O=CC=C=C(CCCC)CCCC", "2b": "C=CCC(O)C=C=C(CCCC)CCCC",
    "1c": "O=CC(C)=C=CCCCC", "2c": "C=CCC(O)C(C)=C=CCCCC",
    "1d": "O=CC=C=CC1CCCCC1", "2d": "C=CCC(O)C=C=CC1CCCCC1",
    "1e": "O=CC=C=CCCCCCCC", "2e": "C=CCC(O)C=C=CCCCCCCC",
    "1f": "O=CC=C=CCCCCCCCCCC", "2f": "C=CCC(O)C=C=CCCCCCCCCCC",
    "1g": "O=CC(CCCCCCCCCC)=C=C", "2g": "C=CCC(O)C(CCCCCCCCCC)=C=C",
    "1h": "O=CC(CCCCCCC)=C=C", "2h": "C=CCC(O)C(CCCCCCC)=C=C",
    "1i": "O=CC(CC=C)=C=C", "2i": "C=CCC(O)C(CC=C)=C=C",
    "1j": "O=CC(CCC)=C=C1CCCCC1", "2j": "C=CCC(O)C(CCC)=C=C1CCCCC1",
}

NAMES_1 = {
    "1a": "4,4-pentamethylenebutadienal",
    "1b": "4-butyl-2,3-octadienal",
    "1c": "2-methyl-2,3-octadienal",
    "1d": "4-cyclohexylbutadienal",
    "1e": "2,3-undecadienal",
    "1f": "2,3-tetradecadienal",
    "1g": "2-decyl-2,3-butadienal",
    "1h": "2-heptyl-2,3-butadienal",
    "1i": "2-allylbutadienal",
    "1j": "2-propyl-4,4-pentamethylenebutadienal",
}

NAMES_2 = {
    "2a": "1,1-pentamethylene-1,2,6-heptatrien-4-ol",
    "2b": "7-butyl-1,5,6-undecatrien-4-ol",
    "2c": "5-methyl-1,5,6-undecatrien-4-ol",
    "2d": "1-cyclohexyl-1,2,6-heptatrien-4-ol",
    "2e": "1,5,6-tetradecatrien-4-ol",
    "2f": "1,5,6-heptadecatrien-4-ol",
    "2g": "3-decyl-1,2,6-heptatrien-4-ol",
    "2h": "3-heptyl-1,2,6-heptatrien-4-ol",
    "2i": "3-allyl-1,2,6-heptatrien-4-ol",
    "2j": "1,1-pentamethylene-3-propyl-1,2,6-heptatrien-4-ol",
}

records = []


def add_table1_records():
    rows = [
        # label, detail page, starting material name/smiles, quantities, product mass/yield
        ("1a", 2, "vinylidenecyclohexane", "C=C=C1CCCCC1", 3.21, 29.7, 11.1, 27.75, 3.5, 3.31, 45.0, 40.0, 1.90, 50),
        ("1b", 2, "3-butyl-1,2-heptadiene", "C=C=C(CCCC)CCCC", 1.41, 9.3, 3.4, 8.5, 1.06, 1.00, 13.8, 29.0, 0.35, 23),
        ("1d", 2, "cyclohexyl-1,2-propadiene", "C=C=CC1CCCCC1", 2.76, 22.6, 8.5, 21.25, 2.8, 2.65, 36.3, 60.0, 1.62, 51),
        ("1e", 3, "1,2-decadiene", "C=C=CCCCCCCC", 3.04, 22.0, 8.0, 20.0, 3.0, 2.85, 38.9, 60.0, 1.20, 36),
        ("1f", 3, "1,2-tridecadiene", "C=C=CCCCCCCCCCC", 3.40, 18.9, 7.0, 17.5, 2.3, 2.19, 29.8, 60.0, 1.35, 37),
    ]
    for idx, row in enumerate(rows, 1):
        label, page, start_name, start_smiles, start_g, start_mmol, buli_ml, buli_mmol, dmf_ml, dmf_g, dmf_mmol, thf_ml, prod_g, yield_pct = row
        evidence = merged_ev(1, page)
        pstart = participant("allene_start", "reactant", start_name, start_name, start_smiles, ev(page), [
            amount("mass", start_g, "g", ev(page)), amount("amount", start_mmol, "mmol", ev(page))])
        pbuli = participant("n_butyllithium", "reagent", "n-BuLi", "n-butyllithium", "[Li+].[CH2-]CCC", ev(page), [
            amount("solution_volume", buli_ml, "mL", ev(page)), amount("concentration", 2.5, "M", ev(page)), amount("amount", buli_mmol, "mmol", ev(page))])
        pdmf = participant("dmf", "reagent", "DMF", "dimethylformamide", "CN(C)C=O", ev(page), [
            amount("volume", dmf_ml, "mL", ev(page)), amount("mass", dmf_g, "g", ev(page)), amount("amount", dmf_mmol, "mmol", ev(page))])
        pthf = participant("thf", "solvent", "THF", "tetrahydrofuran", "C1CCOC1", ev(page), [amount("reported_total_or_batch_volume", thf_ml, "mL", ev(page))])
        hcl_amounts = [amount("concentration", 0.1, "M", ev(1))]
        if label == "1a":
            hcl_amounts.append(amount("quench_volume", 500, "mL", ev(2)))
        phcl = participant("hcl", "reagent", "HCl", "hydrochloric acid", "Cl", ev(1), hcl_amounts)
        product = participant("product", "product", label, NAMES_1[label], SMILES[label], ev(1), [])
        conditions = [
            field("atmosphere", "nitrogen", ev(2)),
            field("initial_addition_temperature", q(-60, "°C"), ev(2)),
            field("first_stage_temperature", q(-55, "°C"), ev(2)),
            field("first_stage_time", q(1.2, "h"), ev(2)),
            field("DMF_addition_temperature", q(-70, "°C"), ev(2)),
            field("second_stage_temperature", q(-70, "°C"), ev(2)),
            field("second_stage_time", q(2.0, "h"), ev(2)),
            field("workup", "acid quench, ether extraction, water wash, Na2SO4 drying, evaporation; preceding typical procedure", ev(2)),
            field("purification", "silica-gel column chromatography; preceding typical procedure", ev(2)),
        ]
        outcomes = [
            field("isolated_product_mass", q(prod_g, "g"), ev(page), ["product"]),
            field("isolated_yield", q(yield_pct, "%"), evidence, ["product"]),
            field("yield_measurement_basis", "isolated", evidence, ["product"]),
        ]
        records.append(record(
            f"table1_entry{idx}_{label}", "substrate_scope_entry", evidence,
            [pstart, pbuli, pdmf, pthf, phcl, product], conditions, outcomes,
            ["Candidate structures and connectivity remain unverified.", "Abbreviated batches explicitly refer to the typical procedure, but do not restate all operation-specific volumes."],
            notes=["Table 1 row and its compound-specific experimental paragraph are treated as one experiment."],
        ))


def add_table2_records():
    rows = [
        # label, page, starting alcohol name/smiles, alcohol g/mmol, oxalyl ml or None/g/mmol, dmso ml/g/mmol, et3n ml/g/mmol, dcm mL, product g/yield
        ("1c", 3, "2-methyl-2,3-octadienol", "OCC(C)=C=CCCCC", 2.10, 15.0, 1.7, 2.53, 20.0, 2.7, 2.97, 38.1, 10.0, 7.30, 72.3, 50.0, 1.66, 80),
        ("1g", 4, "2-decyl-2,3-butadienol", "OCC(CCCCCCCCCC)=C=C", 1.60, 7.6, 1.05, 1.64, 12.4, 1.8, 1.98, 25.4, 7.0, 5.11, 50.6, 45.0, 1.35, 85),
        ("1h", 4, "2-heptyl-2,3-butadienol", "OCC(CCCCCCC)=C=C", 0.51, 3.0, None, 0.48, 3.8, 0.55, 0.61, 7.5, 2.1, 1.53, 15.2, 18.0, 0.37, 75),
        ("1i", 4, "2-allylbutadienol", "OCC(CC=C)=C=C", 1.15, 10.5, 1.4, 2.09, 16.6, 2.4, 2.64, 33.8, 9.0, 6.57, 65.0, 20.0, 0.61, 54),
        ("1j", 4, "2-propyl-4,4-pentamethylenebutadienol", "OCC(CCC)=C=C1CCCCC1", 0.502, 2.8, None, 0.445, 3.5, 0.5, 0.550, 7.1, 1.9, 1.39, 13.7, 18.0, 0.404, 81),
    ]
    for idx, row in enumerate(rows, 1):
        label, page, alcohol_name, alcohol_smiles, alc_g, alc_mmol, ox_ml, ox_g, ox_mmol, dmso_ml, dmso_g, dmso_mmol, et_ml, et_g, et_mmol, dcm_ml, prod_g, yield_pct = row
        evidence = merged_ev(2, 3, page)
        alcohol = participant("allenol_start", "reactant", alcohol_name, alcohol_name, alcohol_smiles, ev(page), [amount("mass", alc_g, "g", ev(page)), amount("amount", alc_mmol, "mmol", ev(page))])
        ox_amounts = [amount("table_equivalents", 1.25, "equiv", ev(2)), amount("mass", ox_g, "g", ev(page)), amount("amount", ox_mmol, "mmol", ev(page))]
        if ox_ml is not None:
            ox_amounts.insert(0, amount("volume", ox_ml, "mL", ev(page)))
        oxalyl = participant("oxalyl_chloride", "reagent", "(COCl)2", "oxalyl chloride", "O=C(Cl)C(=O)Cl", ev(page), ox_amounts)
        dmso = participant("dmso", "reagent", "DMSO", "dimethyl sulfoxide", "CS(C)=O", ev(page), [amount("table_equivalents", 2.5, "equiv", ev(2)), amount("volume", dmso_ml, "mL", ev(page)), amount("mass", dmso_g, "g", ev(page)), amount("amount", dmso_mmol, "mmol", ev(page))])
        et3n = participant("triethylamine", "reagent", "Et3N", "triethylamine", "CCN(CC)CC", ev(page), [amount("table_equivalents", 5.0, "equiv", ev(2)), amount("volume", et_ml, "mL", ev(page)), amount("mass", et_g, "g", ev(page)), amount("amount", et_mmol, "mmol", ev(page))])
        dcm = participant("dcm", "solvent", "CH2Cl2", "dichloromethane", "ClCCl", ev(page), [amount("reported_total_or_batch_volume", dcm_ml, "mL", ev(page))])
        product = participant("product", "product", label, NAMES_1[label], SMILES[label], ev(2), [])
        conditions = [
            field("atmosphere", "nitrogen", ev(3)),
            field("DMSO_addition_temperature", q(-78, "°C"), ev(3)),
            field("activation_time", q(20, "min"), ev(3)),
            field("allenol_addition_temperature", q(-78, "°C"), ev(3)),
            field("oxidation_temperature", q(-78, "°C"), ev(3)),
            field("oxidation_time", q(1.3, "h"), ev(3)),
            field("workup", "remove cooling bath, dilute with ether, wash with water, dry over Na2SO4, evaporate; preceding typical procedure", ev(3)),
            field("purification", "silica-gel column chromatography; preceding typical procedure", ev(3)),
        ]
        outcomes = [field("isolated_product_mass", q(prod_g, "g"), ev(page), ["product"]), field("isolated_yield", q(yield_pct, "%"), evidence, ["product"]), field("yield_measurement_basis", "isolated", evidence, ["product"])]
        records.append(record(
            f"table2_entry{idx}_{label}", "substrate_scope_entry", evidence,
            [alcohol, oxalyl, dmso, et3n, dcm, product], conditions, outcomes,
            ["Candidate structures and connectivity remain unverified.", "Abbreviated batches explicitly refer to the typical procedure, but do not restate every operation-specific volume."],
            notes=["Table 2 row and its compound-specific experimental paragraph are treated as one experiment."],
        ))


def add_optimization_records():
    rows = [
        # table entry, metal, eq, solvent, time, yield, activated?
        (1, "In", 2.0, "H2O:THF = 5:2", 45.5, 59, False),
        (2, "In", 2.0, "NH4Cl (2 M):THF = 5:2", 16, 64, False),
        (3, "In", 2.0, "NH4Cl (4 M):THF = 5:2", 14, 84, False),
        (4, "In", 1.1, "saturated aqueous NH4Cl:THF = 5:2", 72, 45, False),
        (5, "In", 1.5, "saturated aqueous NH4Cl:THF = 5:2", 48, 64, False),
        (7, "In", 2.0, "saturated aqueous NH4Cl:THF = 1:2", 17, 54, False),
        (8, "In", 2.0, "saturated aqueous NH4Cl:THF = 10:1", 27, 40, False),
        (9, "Zn", 2.0, "saturated aqueous NH4Cl:THF = 5:2", 17.5, 37, False),
    ]
    evidence = ev(2)
    for entry, metal, metal_eq, solvent_text, time_h, yield_pct, activated in rows:
        p1a = participant("allenal", "reactant", "1a", NAMES_1["1a"], SMILES["1a"], ev(2), [])
        allyl = participant("allyl_bromide", "reactant", "allyl bromide", "allyl bromide", "C=CCBr", ev(2), [amount("equivalents", 2.0, "equiv", ev(2))])
        pmetal = participant("metal", "reagent", metal, "indium" if metal == "In" else "zinc powder", "[In]" if metal == "In" else "[Zn]", ev(2), [amount("equivalents", metal_eq, "equiv", ev(2))])
        medium = participant("reaction_medium", "solvent", solvent_text, solvent_text, None, ev(2), [])
        product = participant("product", "product", "2a", NAMES_2["2a"], SMILES["2a"], ev(2), [])
        records.append(record(
            f"table3_entry{entry}_optimization", "optimization_entry", evidence,
            [p1a, allyl, pmetal, medium, product],
            [field("temperature", "r.t.", ev(2)), field("time", q(time_h, "h"), ev(2)), field("solvent", solvent_text, ev(2)), field("atmosphere", None), field("workup", None), field("purification", None)],
            [field("isolated_yield", q(yield_pct, "%"), ev(2), ["product"]), field("yield_measurement_basis", "isolated", ev(2), ["product"])],
            ["Reaction scale, atmosphere, workup, and purification are not stated for this optimization row.", "Candidate structures remain unverified."],
            notes=["Table 3 entry 6 and entry 10 are excluded here because they are the same experiments as Table 4 entries 1 and 2, respectively."],
        ))


def add_allylation_scope_records():
    rows = [
        # table entry, substrate, product, metal, detail page, metal mg/mmol, substrate mg/mmol, allyl mg/mmol, THF, NH4Cl, time, product mg, yield
        (1, "1a", "2a", "In", 4, 75, 0.65, 40, 0.29, 75, 0.63, 0.8, 2.0, 4.3, 49.6, 95),
        (2, "1a", "2a", "Zn", 4, 45, 0.69, 41, 0.30, 91, 0.76, 0.8, 2.0, 16, 43, 80),
        (3, "1b", "2b", "In", 4, 60, 0.52, 32, 0.18, 49, 0.41, 0.8, 2.0, 7.5, 33.1, 84),
        (4, "1b", "2b", "Zn", 4, 59, 0.91, 72, 0.40, 144, 1.20, 1.0, 2.6, 13, 68.1, 77),
        (5, "1c", "2c", "In", 4, 119, 1.03, 55, 0.40, 100, 0.83, 0.8, 2.0, 12, 46.8, 65),
        (6, "1c", "2c", "Zn", 5, 55, 0.84, 55, 0.40, 100, 0.83, 0.8, 2.0, 17, 41, 57),
        (7, "1d", "2d", "In", 5, 113, 0.98, 74.5, 0.50, 150, 1.25, 0.8, 2.0, 26.3, 82, 86),
        (8, "1d", "2d", "Zn", 5, 50, 0.77, 45.5, 0.30, 80, 0.67, 0.8, 2.0, 27, 43, 74),
        (9, "1e", "2e", "In", 5, 100, 0.87, 67, 0.40, 98, 0.82, 0.8, 2.0, 12, 74.3, 89),
        (10, "1e", "2e", "Zn", 5, 50, 0.77, 49, 0.30, 80, 0.67, 0.8, 2.0, 10.4, 50, 81),
        (11, "1f", "2f", "In", 5, 72, 0.63, 60.9, 0.29, 90, 0.75, 0.8, 2.0, 10, 62.4, 85),
        (12, "1f", "2f", "Zn", 5, 60, 0.92, 61, 0.29, 97, 0.81, 0.8, 2.0, 10, 58.6, 80),
        (13, "1g", "2g", "In", 5, 80, 0.69, 62, 0.30, 80, 0.67, 0.8, 2.0, 11, 62.9, 84),
        (14, "1g", "2g", "Zn", 5, 40, 0.61, 62.1, 0.30, 72.5, 0.60, 0.8, 2.0, 10, 39, 84),
        (15, "1h", "2h", "In", 5, 76, 0.66, 44, 0.27, 80, 0.67, 0.8, 2.0, 10.3, 45, 82),
        (16, "1h", "2h", "Zn", 5, 40, 0.61, 45, 0.27, 80, 0.67, 0.8, 2.0, 12, 49.6, 88),
        (17, "1i", "2i", "In", 5, 92, 0.80, 43, 0.40, 100, 0.83, 1.0, 2.6, 9.5, 43.6, 73),
        (18, "1i", "2i", "Zn", 6, 79.1, 1.22, 64.7, 0.60, 144.1, 1.19, 1.6, 4.0, 17, 67.5, 75),
        (19, "1j", "2j", "In", 6, 125, 1.09, 61, 0.34, 100, 0.83, 1.0, 2.6, 9.2, 54.3, 72),
        (20, "1j", "2j", "Zn", 6, 40, 0.61, 52.9, 0.30, 72.8, 0.60, 0.8, 2.0, 11, 45.2, 69),
    ]
    for row in rows:
        entry, substrate, product_label, metal, page, metal_mg, metal_mmol, sub_mg, sub_mmol, allyl_mg, allyl_mmol, thf_ml, nh4_ml, time_h, product_mg, yield_pct = row
        pages = [3, 4, page]
        if entry in (1, 2):
            pages.append(2)
        evidence = merged_ev(*pages)
        substrate_p = participant("allenal", "reactant", substrate, NAMES_1[substrate], SMILES[substrate], ev(3), [amount("mass", sub_mg, "mg", ev(page)), amount("amount", sub_mmol, "mmol", ev(page))])
        allyl = participant("allyl_bromide", "reactant", "allyl bromide", "allyl bromide", "C=CCBr", ev(page), [amount("table_equivalents", 2.0, "equiv", ev(3)), amount("mass", allyl_mg, "mg", ev(page)), amount("amount", allyl_mmol, "mmol", ev(page))])
        metal_p = participant("metal", "reagent", metal, "indium particle" if metal == "In" else "zinc powder", "[In]" if metal == "In" else "[Zn]", ev(page), [amount("table_equivalents", 2.0, "equiv", ev(3)), amount("mass", metal_mg, "mg", ev(page)), amount("amount", metal_mmol, "mmol", ev(page))])
        thf = participant("thf", "solvent", "THF", "tetrahydrofuran", "C1CCOC1", ev(page), [amount("volume", thf_ml, "mL", ev(page))])
        nh4cl = participant("aq_nh4cl", "solvent", "saturated aqueous NH4Cl", "saturated aqueous ammonium chloride", "[Cl-].[NH4+]", ev(page), [amount("volume", nh4_ml, "mL", ev(page))])
        product = participant("product", "product", product_label, NAMES_2[product_label], SMILES[product_label], ev(3), [])
        unresolved = ["Atmosphere is not stated.", "Candidate structures and connectivity remain unverified."]
        if entry == 14:
            unresolved.append("The printed 39 mg product mass and 84% yield appear internally inconsistent with the stated 0.30 mmol scale; both are retained as printed.")
        notes = ["The compound-specific paragraph is explicitly under the shared typical Barbier procedure."]
        if entry == 1:
            notes.append("This record also represents Table 3 entry 6; Table 3, Table 4, and the detailed procedure report the same 4.3 h/95% experiment.")
        if entry == 2:
            notes.append("This record also represents Table 3 entry 10; Table 3, Table 4, and the detailed paragraph report the same activated-Zn 16 h/80% experiment.")
        records.append(record(
            f"table4_entry{entry}_{product_label}_{metal.lower()}", "substrate_scope_entry", evidence,
            [substrate_p, allyl, metal_p, thf, nh4cl, product],
            [field("temperature", "r.t.", ev(page)), field("time", q(time_h, "h"), ev(page)), field("atmosphere", None), field("workup", "water quench, ether extraction, brine wash, Na2SO4 drying, evaporation; shared typical procedure", ev(4)), field("purification", "silica-gel column chromatography, petroleum ether/ethyl acetate 5:1; shared typical procedure", ev(4))],
            [field("isolated_product_mass", q(product_mg, "mg"), ev(page), ["product"]), field("isolated_yield", q(yield_pct, "%"), evidence, ["product"]), field("yield_measurement_basis", "isolated", ev(3), ["product"]), field("1_4_addition_product_observation", "not observed", ev(2))],
            unresolved, notes=notes,
        ))


add_table1_records()
add_table2_records()
add_optimization_records()
add_allylation_scope_records()

assert len(records) == 38
assert len({r["record_id"] for r in records}) == 38

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")

page_records = {
    1: [r["record_id"] for r in records if ":table1_" in r["record_id"]],
    2: [r["record_id"] for r in records if ":table2_" in r["record_id"] or ":table3_" in r["record_id"] or r["record_id"].endswith(("table4_entry1_2a_in", "table4_entry2_2a_zn")) or ":table1_entry1_" in r["record_id"] or ":table1_entry2_" in r["record_id"] or ":table1_entry3_" in r["record_id"]],
    3: [r["record_id"] for r in records if ":table4_" in r["record_id"] or ":table1_entry4_" in r["record_id"] or ":table1_entry5_" in r["record_id"] or ":table2_entry1_" in r["record_id"]],
    4: [r["record_id"] for r in records if any(f":table2_entry{i}_" in r["record_id"] for i in range(2, 6)) or any(f":table4_entry{i}_" in r["record_id"] for i in range(1, 6))],
    5: [r["record_id"] for r in records if any(f":table4_entry{i}_" in r["record_id"] for i in range(5, 18))],
    6: [r["record_id"] for r in records if any(f":table4_entry{i}_" in r["record_id"] for i in range(18, 21))],
}
for page in page_records:
    page_records[page] = list(dict.fromkeys(page_records[page]))

coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {"page": 1, "state": "attempted", "regions": [
            {"region": "title, abstract, introduction, and Results and discussion prose", "finding": "Broad present-paper claims and cited prior-work summaries; not duplicated as row-level experiments.", "evidence_ids": ev(1)},
            {"region": "lower-right Table 1", "finding": "Five starting-material preparation rows identified; compound-specific procedures on pages 2-3 are merged into these records.", "evidence_ids": ev(1)},
        ], "record_ids": page_records[1], "unresolved": ["Abstract-level claims are not independent experiments.", "ESI is mentioned but no SI file is explicitly provided or associated."]},
        {"page": 2, "state": "attempted", "regions": [
            {"region": "upper-left Table 2", "finding": "Five Swern-oxidation starting-material rows identified; detailed paragraphs on pages 3-4 are merged into the same records.", "evidence_ids": ev(2)},
            {"region": "middle-left Table 3 and footnotes", "finding": "Ten optimization rows inspected. Entries 6 and 10 duplicate Table 4 entries 1 and 2 and are merged; the remaining eight are independent optimization records.", "evidence_ids": ev(2)},
            {"region": "right-column experimental section", "finding": "Typical 1a procedure and abbreviated 1b/1d batches supply quantities and operational detail for Table 1 records.", "evidence_ids": ev(2)},
        ], "record_ids": page_records[2], "unresolved": ["Optimization rows omit scale, atmosphere, workup, and purification.", "Candidate structures remain unverified."]},
        {"page": 3, "state": "attempted", "regions": [
            {"region": "top Table 4 and footnote", "finding": "Twenty In/Zn substrate-scope rows inspected; isolated yields and row-specific times transcribed.", "evidence_ids": ev(3)},
            {"region": "lower-left 1e/1f procedures", "finding": "Detailed Table 1 batches merged into entries 4 and 5.", "evidence_ids": ev(3)},
            {"region": "lower-right typical Swern procedure for 1c", "finding": "Complete quantities, temperature program, workup and purification merged into Table 2 entry 1 and used only through the explicit following-compounds cross-reference.", "evidence_ids": ev(3)},
        ], "record_ids": page_records[3], "unresolved": ["Table 4 structures and machine candidate SMILES require chemistry review."]},
        {"page": 4, "state": "attempted", "regions": [
            {"region": "left column Swern preparations 1g-1j", "finding": "Four compound-specific batches merged into Table 2 entries 2-5.", "evidence_ids": ev(4)},
            {"region": "upper-right typical Barbier procedure and 2a In/Zn batches", "finding": "Operational details and exact quantities merged into Table 4 entries 1-2; these also correspond to Table 3 entries 6 and 10.", "evidence_ids": ev(4)},
            {"region": "lower-right 2b and beginning of 2c preparations", "finding": "In/Zn compound-specific batches merged into Table 4 entries 3-5; 2c continues on page 5.", "evidence_ids": ev(4)},
        ], "record_ids": page_records[4], "unresolved": ["The Barbier typical procedure does not state an atmosphere."]},
        {"page": 5, "state": "attempted", "regions": [
            {"region": "both columns, continuation of 2c and preparations 2d-2i", "finding": "In/Zn batches for Table 4 entries 6-17 and the start of entry 17 characterization were inspected and merged into their table rows.", "evidence_ids": ev(5)},
        ], "record_ids": page_records[5], "unresolved": ["Table 4 entry 14 prints 39 mg product at 84% from 0.30 mmol 1g; this internal inconsistency is retained unresolved.", "Atmosphere is unstated."]},
        {"page": 6, "state": "attempted", "regions": [
            {"region": "upper-left continuation of 2i and 2j preparations", "finding": "Zinc 2i and In/Zn 2j batches corresponding to Table 4 entries 18-20 were inspected and merged into their rows.", "evidence_ids": ev(6)},
            {"region": "acknowledgements and references", "finding": "No additional present-paper experiment; cited literature was not expanded into records.", "evidence_ids": ev(6)},
        ], "record_ids": page_records[6], "unresolved": ["No SI was supplied despite the paper's ESI notice.", "Candidate structures and stereochemistry/connectivity remain unverified."]},
    ],
}
COVERAGE.parent.mkdir(parents=True, exist_ok=True)
COVERAGE.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

if TASKS.exists():
    tasks = json.loads(TASKS.read_text())
    for task in tasks:
        if task.get("document_id") == DOC and task.get("task_id", "").startswith(f"{DOC}:page"):
            task["state"] = "attempted"
    TASKS.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"records": len(records), "raw": str(OUT), "coverage": str(COVERAGE)}, ensure_ascii=False))
