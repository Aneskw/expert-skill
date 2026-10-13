#!/usr/bin/env python3
"""Enrich/create evidence-linked reaction records for PDF pages 7--10."""
from __future__ import annotations

import copy
import json
from pathlib import Path


DOC = "doc_c4d18a33a17c9cf6"
ROOT = Path(__file__).resolve().parents[3]
DATASET = ROOT / "runs/current/dataset.json"
OUT = Path(__file__).with_name("records_pages_0007_0010.json")
COVERAGE = ROOT / "runs/current/coverage/pages_0007_0010.json"
TASKS = ROOT / "runs/current/tasks.json"


def evidence(*pages: int) -> list[str]:
    return [item for page in pages for item in (
        f"{DOC}:page{page}:image", f"{DOC}:page{page}:text"
    )]


def q(number, unit, **extra):
    value = {"number": number, "unit": unit}
    value.update(extra)
    return value


def qr(minimum, maximum, unit, raw_text):
    return {"minimum": minimum, "maximum": maximum, "unit": unit, "raw_text": raw_text}


def fact(value, *pages: int):
    return {
        "value": value,
        "evidence_ids": evidence(*pages) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def field(name, value, *pages: int, targets=None):
    result = {"name": name, "fact": fact(value, *pages)}
    if targets:
        result["target_entity_ids"] = list(targets)
    return result


def molecule(entity_id, role, label, pages, *, name=None, smiles=None, amounts=()):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, *pages),
        "name": fact(name, *pages) if name is not None else fact(None),
        "smiles": fact(smiles, *pages) if smiles is not None else fact(None),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": [field(n, v, *p) for n, v, p in amounts],
    }


def record(suffix, kind, pages, participants, conditions, outcomes, notes=(), unresolved=()):
    return {
        "record_id": f"{DOC}:{suffix}",
        "document_id": DOC,
        "source_reaction_id": suffix,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": evidence(*pages),
        "participants": participants,
        "steps": [{
            "step_id": "reaction",
            "participant_ids": [p["entity_id"] for p in participants],
            "conditions": conditions,
        }],
        "outcomes": outcomes,
        "notes": [fact(text, *note_pages) for text, note_pages in notes],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": list(unresolved),
        },
    }


def include_pages(rec, *pages: int):
    rec["evidence_ids"] = list(dict.fromkeys(rec["evidence_ids"] + evidence(*pages)))


def participant(rec, entity_id):
    return next(p for p in rec["participants"] if p["entity_id"] == entity_id)


def set_amount(rec, entity_id, name, value, *pages: int):
    p = participant(rec, entity_id)
    for item in p["amounts"]:
        if item["name"] == name:
            item["fact"] = fact(value, *pages)
            item.pop("category", None)
            return
    p["amounts"].append(field(name, value, *pages))


def set_name(rec, entity_id, value, *pages: int):
    participant(rec, entity_id)["name"] = fact(value, *pages)


def set_condition(rec, name, value, *pages: int):
    conditions = rec["steps"][0]["conditions"]
    for item in conditions:
        if item["name"] == name:
            item["fact"] = fact(value, *pages)
            item.pop("category", None)
            return
    conditions.append(field(name, value, *pages))


def add_condition(rec, name, value, *pages: int):
    rec["steps"][0]["conditions"].append(field(name, value, *pages))


def set_outcome(rec, name, value, *pages: int, targets=None):
    for item in rec["outcomes"]:
        if item["name"] == name:
            item["fact"] = fact(value, *pages)
            item.pop("category", None)
            if targets:
                item["target_entity_ids"] = list(targets)
            return
    rec["outcomes"].append(field(name, value, *pages, targets=targets))


def add_note(rec, text, *pages: int):
    rec["notes"].append(fact(text, *pages))


dataset = json.loads(DATASET.read_text())
by_suffix = {r["source_reaction_id"]: r for r in dataset["experiments"]}
records = []

# Page 7 begins with analytical characterization for the page-6 2h batch.
r = copy.deepcopy(by_suffix["table2_entry10_2h"])
include_pages(r, 7)
add_note(r, "The 2h analytical characterization continues at the top of page 7; it is not a separate reaction batch.", 7)
r["review"]["unresolved"] = [
    "Atmosphere is not reported.",
    "Candidate SMILES connectivity and the Z assignment remain machine-unverified against the source structure.",
]
records.append(r)


TYPICAL_II_WORKUP = (
    "According to Typical Procedure II: H2O quench (5 mL), extraction with diethyl ether "
    "(3 x 20 mL), brine wash (5 mL), drying over anhydrous Na2SO4, filtration, and concentration"
)
TYPICAL_II_PURIFICATION = "flash chromatography on silica gel (petroleum ether/ethyl acetate 2:1)"
TYPICAL_II_OPERATION = "H2O was added to the selenyl chloride solution at room temperature, followed by the allenylphosphonate solution"

# Conditions A from Scheme 2: detailed batches on page 7, linked to Typical II on page 5.
scheme2_a = {
    "scheme2_eq1_2i": {
        "substrate": (0.30, 52.3), "reagent": (0.60, 163.1), "time": 3.5,
        "product_mass": 98.6, "state": "liquid", "mp": None,
    },
    "scheme2_eq2_conditions_a_2j": {
        "substrate": (0.30, 56.5), "reagent": (0.60, 161.9), "time": 2.0,
        "product_mass": 99.6, "state": "white solid",
        "mp": qr(125.9, 126.4, "°C", "125.9-126.4 °C"),
    },
    "scheme2_eq3_conditions_a_2k": {
        "substrate": (0.40, 59.5), "reagent": (0.60, 114.8), "time": 4.0,
        "product_mass": 108.9, "state": "liquid", "mp": None,
    },
}
for suffix, spec in scheme2_a.items():
    r = copy.deepcopy(by_suffix[suffix])
    include_pages(r, 5, 7)
    reagent_id = "selenyl_chloride" if "2i" in suffix or "2j" in suffix else "phsecl"
    set_amount(r, "substrate", "amount", q(spec["substrate"][0], "mmol"), 7)
    set_amount(r, "substrate", "mass", q(spec["substrate"][1], "mg"), 7)
    set_amount(r, reagent_id, "amount", q(spec["reagent"][0], "mmol"), 7)
    set_amount(r, reagent_id, "mass", q(spec["reagent"][1], "mg"), 7)
    set_amount(r, "water", "volume", q(0.6, "mL"), 7)
    set_amount(r, "thf", "volume", q(6.0, "mL"), 7)
    add_condition(r, "operation", TYPICAL_II_OPERATION, 5, 7)
    set_condition(r, "workup", TYPICAL_II_WORKUP, 5, 7)
    set_condition(r, "purification", TYPICAL_II_PURIFICATION, 5, 7)
    set_outcome(r, "isolated_product_mass", q(spec["product_mass"], "mg"), 7, targets=["product"])
    set_outcome(r, "physical_state", spec["state"], 7, targets=["product"])
    if spec["mp"] is not None:
        set_outcome(r, "melting_point", spec["mp"], 7, targets=["product"])
        add_note(r, "The melting point is reported after crystallization from n-hexane/ethyl acetate.", 7)
    add_note(r, "NMR and MS/IR/HRMS or elemental-analysis characterization is reported on page 7; no additional batch is implied.", 7)
    r["review"]["unresolved"] = [
        "Atmosphere is not reported for Conditions A.",
        "Product connectivity and stereochemical assignment remain machine-unverified; no candidate SMILES is asserted for this product.",
        "Workup and standard eluent are inherited only because the batch explicitly says it follows Typical Procedure II.",
    ]
    records.append(r)

# Conditions B from Scheme 2: explicit anhydrous-CHCl3 batches on page 7.
scheme2_b = {
    "scheme2_eq2_conditions_b_2j": {
        "substrate": (0.40, 75.4), "reagent": (0.40, 108.5),
        "substrate_solvent": 1.3, "reagent_solvent": 1.1, "time": 26.0,
        "product_mass": 98.7, "purification": "flash chromatography on silica gel (petroleum ether/ethyl acetate 3:2)",
        "workup": "solvent evaporation", "recovery": 13,
    },
    "scheme2_eq3_conditions_b_2k": {
        "substrate": (0.70, 103.3), "reagent": (0.70, 134.8),
        "substrate_solvent": 2.0, "reagent_solvent": 2.4, "time": 19.0,
        "product_mass": 167.5, "purification": "flash chromatography on silica gel (petroleum ether/ethyl acetate 3:1 to 2:1)",
        "workup": "concentration", "recovery": None,
    },
}
for suffix, spec in scheme2_b.items():
    r = copy.deepcopy(by_suffix[suffix])
    include_pages(r, 7)
    reagent_id = "selenyl_chloride" if "2j" in suffix else "phsecl"
    set_amount(r, "substrate", "amount", q(spec["substrate"][0], "mmol"), 7)
    set_amount(r, "substrate", "mass", q(spec["substrate"][1], "mg"), 7)
    set_amount(r, reagent_id, "amount", q(spec["reagent"][0], "mmol"), 7)
    set_amount(r, reagent_id, "mass", q(spec["reagent"][1], "mg"), 7)
    set_amount(r, "chloroform", "substrate_solution_volume", q(spec["substrate_solvent"], "mL"), 7)
    set_amount(r, "chloroform", "reagent_solution_volume", q(spec["reagent_solvent"], "mL"), 7)
    add_condition(r, "operation", "selenyl chloride solution added dropwise at room temperature within 5 min", 7)
    set_condition(r, "workup", spec["workup"], 7)
    set_condition(r, "purification", spec["purification"], 7)
    set_outcome(r, "isolated_product_mass", q(spec["product_mass"], "mg"), 7, targets=["product"])
    set_outcome(r, "physical_state", "white solid" if "2j" in suffix else "liquid", 7, targets=["product"])
    if spec["recovery"] is not None:
        set_outcome(r, "recovery_measurement_basis", "1H NMR analysis of the crude product", 7, targets=["substrate"])
    add_note(r, "The reaction was run in a dried Schlenk tube under nitrogen.", 7)
    r["review"]["unresolved"] = [
        "Product connectivity and stereochemical assignment remain machine-unverified; no candidate SMILES is asserted for this product.",
    ]
    records.append(r)

# Scheme 3 large-scale 1j batch, with the detailed page-7 procedure and page-8 characterization.
r = copy.deepcopy(by_suffix["scheme3_large_scale_1j_to_2l"])
include_pages(r, 5, 7, 8)
set_amount(r, "phsecl", "amount", q(11.0, "mmol"), 7)
set_amount(r, "phsecl", "mass", q(2.1070, "g"), 7)
set_amount(r, "thf", "substrate_solution_volume", q(13, "mL"), 7)
set_amount(r, "thf", "reagent_solution_volume", q(39, "mL"), 7)
set_amount(r, "water", "volume", q(5.2, "mL"), 7)
add_condition(r, "operation", TYPICAL_II_OPERATION, 5, 7)
set_condition(r, "workup", TYPICAL_II_WORKUP, 5, 7)
set_condition(r, "purification", TYPICAL_II_PURIFICATION, 5, 7)
set_outcome(r, "isolated_product_mass", q(1.6716, "g"), 7, targets=["product"])
set_outcome(r, "physical_state", "white solid", 7, targets=["product"])
set_outcome(r, "melting_point", qr(126.6, 127.4, "°C", "126.6-127.4 °C"), 7, targets=["product"])
add_note(r, "The product was crystallized from n-hexane/ethyl acetate; analytical characterization continues on page 8.", 7, 8)
r["review"]["unresolved"] = [
    "Atmosphere is not reported.",
    "Product connectivity and stereochemical assignment remain machine-unverified; no candidate SMILES is asserted.",
    "Workup and standard eluent are inherited only because the batch explicitly says it follows Typical Procedure II.",
]
records.append(r)


TYPICAL_III_WORKUP = (
    "According to Typical Procedure III: H2O quench (5 mL), extraction with diethyl ether "
    "(3 x 20 mL), brine wash (5 mL), drying over anhydrous Na2SO4, filtration, and concentration"
)

# Table 3 batches: product-specific masses and repeated/double chromatography on page 8.
table3 = {
    "table3_entry1": {
        "page": (8,), "substrate_mass": 69.2, "reagent_mass": 85.5,
        "p2_mass": 93.3, "p3_mass": 12.6,
        "p2_name": "diethyl [(Z)-1-chloro-2-(phenylselanyl)-2-hepten-3-yl]phosphonate",
        "p3_name": "3-(n-butyl)-2-ethoxy-4-(phenylselanyl)-2,5-dihydro-1,2-oxaphosphole 2-oxide",
        "workup": TYPICAL_III_WORKUP,
        "purification": "double chromatography on silica gel (petroleum ether/ethyl acetate 5:1 first round, then 4:1 second round)",
    },
    "table3_entry2": {
        "page": (8,), "substrate_mass": 68.8, "reagent_mass": 86.5,
        "p2_mass": 72.2, "p3_mass": 7.5,
        "p2_name": "diethyl [(Z)-1-chloro-2-(phenylselanyl)-2-hepten-3-yl]phosphonate",
        "p3_name": "3-(n-butyl)-2-ethoxy-4-(phenylselanyl)-2,5-dihydro-1,2-oxaphosphole 2-oxide",
        "workup": TYPICAL_II_WORKUP,
        "purification": "repeated chromatography on silica gel (petroleum ether/ethyl acetate 5:1, twice)",
    },
    "table3_entry3": {
        "page": (8,), "substrate_mass": 57.7, "reagent_mass": 86.5,
        "p2_mass": 72.9, "p3_mass": 5.7,
        "p2_name": "diethyl [(Z)-1-chloro-2-(phenylselanyl)-2-buten-3-yl]phosphonate",
        "p3_name": "2-ethoxy-3-methyl-4-(phenylselanyl)-2,5-dihydro-1,2-oxaphosphole 2-oxide",
        "workup": TYPICAL_III_WORKUP,
        "purification": "repeated chromatography on silica gel (petroleum ether/ethyl acetate 2:1, twice)",
    },
    "table3_entry4": {
        "page": (8, 9), "substrate_mass": 81.6, "reagent_mass": 85.7,
        "p2_mass": 95.5, "p3_mass": 11.0,
        "p2_name": "diethyl [(Z)-1-chloro-2-(phenylselanyl)-2-decen-3-yl]phosphonate",
        "p3_name": "2-ethoxy-3-(n-heptyl)-4-(phenylselanyl)-2,5-dihydro-1,2-oxaphosphole 2-oxide",
        "workup": TYPICAL_III_WORKUP,
        "purification": "repeated chromatography on silica gel (petroleum ether/ethyl acetate 5:1, twice)",
    },
}
for suffix, spec in table3.items():
    pages = spec["page"]
    r = copy.deepcopy(by_suffix[suffix])
    include_pages(r, 5, *pages)
    set_amount(r, "substrate", "mass", q(spec["substrate_mass"], "mg"), 8)
    set_amount(r, "phsecl", "mass", q(spec["reagent_mass"], "mg"), 8)
    set_name(r, "product_2", spec["p2_name"], 8)
    set_name(r, "product_3", spec["p3_name"], 8)
    set_condition(r, "workup", spec["workup"], 5, 8)
    set_condition(r, "purification", spec["purification"], 8)
    set_outcome(r, "isolated_product_mass_2", q(spec["p2_mass"], "mg"), 8, targets=["product_2"])
    set_outcome(r, "isolated_product_mass_3", q(spec["p3_mass"], "mg"), 8, targets=["product_3"])
    set_outcome(r, "physical_state_2", "colorless liquid" if suffix == "table3_entry4" else "liquid", 8, targets=["product_2"])
    set_outcome(r, "physical_state_3", "colorless liquid" if suffix == "table3_entry4" else "liquid", 8, targets=["product_3"])
    add_note(r, "NMR/MS/IR/HRMS characterization is reported for both isolated products; this does not create additional reaction records.", *pages)
    r["review"]["unresolved"] = [
        "Atmosphere is not reported.",
        "Product structures and stereochemical assignments remain machine-unverified; SMILES stay null.",
        "Generic workup is inherited only from the explicitly cited Typical Procedure II or III.",
    ]
    records.append(r)

# Page 9 reports two distinct unsuccessful 70 °C attempts before the alternative room-temperature route.
for substrate, substitution in (("1p", "R1=H, R2=Me, R3=Me"), ("1r", "R1=n-C4H9, R2=Me, R3=Me")):
    pages = (5, 9)
    suffix = f"multisubstituted_{substrate}_typical_ii_70c_complicated"
    parts = [
        molecule("substrate", "reactant", substrate, pages,
                 name=f"multisubstituted diethyl allenylphosphonate {substitution}"),
        molecule("phsecl", "reagent", "PhSeCl", pages,
                 name="phenylselanyl chloride", smiles="Cl[Se]c1ccccc1",
                 amounts=[("equivalents", q(1.5, "equiv"), pages)]),
        molecule("thf", "solvent", "THF", pages, smiles="C1CCOC1"),
        molecule("water", "solvent", "water", pages, smiles="O"),
        molecule("products", "product", "complicated product mixture", (9,)),
    ]
    records.append(record(
        suffix, "reported_experiment", pages, parts,
        [
            field("solvent", "THF/H2O (10:1)", *pages),
            field("temperature", q(70, "°C"), 9),
            field("time", None), field("atmosphere", None),
            field("workup", None), field("purification", None),
        ],
        [
            field("reaction_outcome", "complicated reaction", 9, targets=["products"]),
            field("isolated_yield", None, targets=["products"]),
        ],
        notes=[("The paper states that the 70 °C Typical Procedure II attempt was complicated and therefore used an alternative approach.", (9,))],
        unresolved=[
            "No reaction time, exact scale, product identity, isolated yield, workup, or purification is reported for this failed/complex attempt.",
            "The reagent equivalents and solvent ratio are inherited only from the explicitly cited Typical Procedure II.",
        ],
    ))


TYPICAL_IV_WORKUP = (
    "H2O quench (5 mL), extraction with diethyl ether (3 x 20 mL), brine wash (5 mL), "
    "drying over anhydrous Na2SO4, filtration, and concentration"
)
table4 = {
    "table4_entry1": {
        "substrate_mass": 62.9, "reagent_mass": 87.6, "product_mass": 55.7,
        "product_name": "2-ethoxy-4-(phenylselanyl)-2,5-dihydro-5,5-dimethyl-1,2-oxaphosphole 2-oxide",
        "purification": "flash chromatography on silica gel (petroleum ether/ethyl acetate 3:2)",
        "split_volumes": (4.5, 1.5), "detailed_total": None, "water": None,
    },
    "table4_entry2": {
        "substrate_mass": 77.4, "reagent_mass": 86.8, "product_mass": 106.5,
        "product_name": "3-(n-butyl)-2-ethoxy-5-ethyl-4-(phenylselanyl)-2,5-dihydro-1,2-oxaphosphole 2-oxide",
        "purification": "chromatography (petroleum ether/ethyl acetate 5:1 to 3:1)",
        "split_volumes": None, "detailed_total": None, "water": None,
    },
    "table4_entry3": {
        "substrate_mass": 77.9, "reagent_mass": 86.6, "product_mass": 101.2,
        "product_name": "3-(n-butyl)-2-ethoxy-5,5-dimethyl-4-(phenylselanyl)-2,5-dihydro-1,2-oxaphosphole 2-oxide",
        "purification": "chromatography (petroleum ether/ethyl acetate 5:2)",
        "split_volumes": None, "detailed_total": 4.0, "water": 0.4,
    },
}
for suffix, spec in table4.items():
    r = copy.deepcopy(by_suffix[suffix])
    include_pages(r, 9)
    set_amount(r, "substrate", "mass", q(spec["substrate_mass"], "mg"), 9)
    set_amount(r, "phsecl", "mass", q(spec["reagent_mass"], "mg"), 9)
    set_name(r, "product", spec["product_name"], 9)
    if spec["split_volumes"]:
        set_amount(r, "thf", "reagent_solution_volume", q(spec["split_volumes"][0], "mL"), 9)
        set_amount(r, "thf", "substrate_solution_volume", q(spec["split_volumes"][1], "mL"), 9)
    if spec["detailed_total"] is not None:
        set_amount(r, "thf", "detailed_batch_volume", q(spec["detailed_total"], "mL"), 9)
        set_amount(r, "water", "detailed_batch_volume", q(spec["water"], "mL"), 9)
        add_note(r, "Table 4 states 6.0 mL THF and 0.6 mL H2O, whereas the detailed 3r paragraph states 4.0 mL THF and 0.4 mL H2O; both source reports are retained.", 4, 9)
    add_condition(r, "operation", "H2O was added to the PhSeCl solution at room temperature, followed by the allenylphosphonate solution", 9)
    set_condition(r, "workup", TYPICAL_IV_WORKUP, 9)
    set_condition(r, "purification", spec["purification"], 9)
    set_outcome(r, "isolated_product_mass", q(spec["product_mass"], "mg"), 9, targets=["product"])
    set_outcome(r, "physical_state", "liquid", 9, targets=["product"])
    add_note(r, "Analytical characterization is reported on page 9; it is not a separate reaction batch.", 9)
    r["review"]["unresolved"] = [
        "Atmosphere is not reported.",
        "Product structure and stereochemistry remain machine-unverified; SMILES stays null.",
    ]
    if suffix == "table4_entry3":
        r["review"]["unresolved"].append(
            "Table 4 and the detailed 3r paragraph disagree on THF/H2O volumes; neither value was discarded."
        )
    records.append(r)


# Write the raw machine submission.
OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")

rid = lambda suffix: f"{DOC}:{suffix}"
pages = [
    {
        "page": 7,
        "state": "attempted",
        "regions": [
            {
                "region": "upper-left continuation of Z-2h characterization",
                "finding": "Only the analytical characterization of the page-6 Z-2h batch continues here; it was linked to the existing Table 2 entry 10 record and was not counted as a new reaction.",
                "evidence_ids": evidence(7),
            },
            {
                "region": "left column detailed Z-2i and Z-2j Conditions A procedures",
                "finding": "Exact substrate/reagent masses and mmol, solvent volumes, times, isolated product masses/yields, physical states, and the 2j melting-point range were merged into the existing Scheme 2 records.",
                "evidence_ids": evidence(7),
            },
            {
                "region": "lower-left to upper-right 1j plus p-BrC6H4SeCl in anhydrous chloroform",
                "finding": "The Conditions B 2j batch was enriched with dried-Schlenk/N2 setup, two chloroform portions, 5 min addition, 26 h reaction, chromatography, 54% isolated yield, and 13% recovered 1j by crude-product 1H NMR.",
                "evidence_ids": evidence(7),
            },
            {
                "region": "right column Z-2k Conditions A/B and large-scale Z-2l procedure",
                "finding": "The two distinct 2k batches and the 5.5 mmol 2l scale-up were kept separate and enriched with page-7 quantities, operations, product masses, yields, and stated workup/purification details.",
                "evidence_ids": evidence(7),
            },
        ],
        "record_ids": [rid(x) for x in [
            "table2_entry10_2h", "scheme2_eq1_2i", "scheme2_eq2_conditions_a_2j",
            "scheme2_eq2_conditions_b_2j", "scheme2_eq3_conditions_a_2k",
            "scheme2_eq3_conditions_b_2k", "scheme3_large_scale_1j_to_2l",
        ]],
        "unresolved": [
            "Conditions A and the large-scale batch do not report atmosphere.",
            "Stereochemical/product structures remain machine-unverified even where analytical characterization is present.",
        ],
    },
    {
        "page": 8,
        "state": "attempted",
        "regions": [
            {
                "region": "upper-left continuation of Z-2l characterization",
                "finding": "Analytical data continue from the page-7 large-scale 2l batch; no duplicate experiment was created.",
                "evidence_ids": evidence(8),
            },
            {
                "region": "left column dioxane and THF preparations of Z-2m plus 3m",
                "finding": "The two solvent-dependent Table 3 rows remain separate experiments. Exact masses, product-specific isolated masses/yields, and double/repeated chromatography eluents were added.",
                "evidence_ids": evidence(8),
            },
            {
                "region": "right column preparation of Z-2n plus 3n",
                "finding": "The Table 3 entry-3 record was enriched with the detailed dioxane batch quantities, two product masses/yields, and repeated 2:1 chromatography.",
                "evidence_ids": evidence(8),
            },
            {
                "region": "lower-right start of Z-2o plus 3o procedure",
                "finding": "The Table 3 entry-4 batch begins here and continues analytically onto page 9; it remains one cross-page record.",
                "evidence_ids": evidence(8),
            },
        ],
        "record_ids": [rid(x) for x in [
            "scheme3_large_scale_1j_to_2l", "table3_entry1", "table3_entry2",
            "table3_entry3", "table3_entry4",
        ]],
        "unresolved": [
            "Reaction atmospheres are not reported.",
            "Product structures and Z assignments remain machine-unverified; analytical spectra were not interpreted atom by atom.",
        ],
    },
    {
        "page": 9,
        "state": "attempted",
        "regions": [
            {
                "region": "upper-left continuation of Z-2o and 3o characterization",
                "finding": "Analytical characterization completes the page-8 Table 3 entry-4 batch; no additional reaction was created.",
                "evidence_ids": evidence(9),
            },
            {
                "region": "left-middle statement on 1p and 1r at 70 °C under Typical Procedure II",
                "finding": "Two substrate-specific failed/complex experiments were created because the paper explicitly states that the 1p and 1r reactions were complicated before switching to an alternative approach. Their missing time, product identity, and yield remain null.",
                "evidence_ids": evidence(9),
            },
            {
                "region": "lower-left Typical Procedure IV for 3p and start of 3q",
                "finding": "Detailed 3p and 3q batch quantities, workup, chromatography, product masses, and isolated yields were merged with Table 4 entries 1 and 2 rather than duplicated.",
                "evidence_ids": evidence(9),
            },
            {
                "region": "upper-right continuation of 3q and detailed 3r procedure",
                "finding": "The 3q characterization and complete 3r batch were reconciled with Table 4. The table-versus-procedure THF/H2O volume discrepancy for 3r was retained explicitly.",
                "evidence_ids": evidence(9),
            },
            {
                "region": "right-middle Supporting Information note, acknowledgements, and references",
                "finding": "The paper mentions online NMR Supporting Information, but no SI file was explicitly supplied or associated; acknowledgements/references add no new current-paper batch.",
                "evidence_ids": evidence(9),
            },
        ],
        "record_ids": [rid(x) for x in [
            "table3_entry4", "multisubstituted_1p_typical_ii_70c_complicated",
            "multisubstituted_1r_typical_ii_70c_complicated", "table4_entry1",
            "table4_entry2", "table4_entry3",
        ]],
        "unresolved": [
            "The two complicated 70 °C attempts omit time, scale, identified products, yield, workup, and purification.",
            "Table 4 and the detailed 3r paragraph conflict on THF/H2O volumes.",
            "Supporting Information remains unassociated and was not imported.",
        ],
    },
    {
        "page": 10,
        "state": "attempted",
        "regions": [
            {
                "region": "both columns: continuation of references 6--20",
                "finding": "Bibliographic references and prior-work descriptions only; no current-paper reaction batch, table row, or reaction arrow is present.",
                "evidence_ids": evidence(10),
            },
            {
                "region": "left column reference 12 crystal data for Z-2j",
                "finding": "Crystallographic parameters characterize Z-2j and cite CCDC-739001; they do not constitute a new synthesis experiment and were not converted into a reaction record.",
                "evidence_ids": evidence(10),
            },
            {
                "region": "lower-right received/published dates",
                "finding": "Publication metadata only; no reaction information.",
                "evidence_ids": evidence(10),
            },
        ],
        "record_ids": [],
        "unresolved": [
            "Cited external papers and the CCDC deposit were not supplied and were not treated as source experiments for this extraction.",
        ],
    },
]

submitted_ids = {r["record_id"] for r in records}
known_ids = {r["record_id"] for r in dataset["experiments"]} | submitted_ids
referenced_ids = {record_id for page in pages for record_id in page["record_ids"]}
missing = sorted(referenced_ids - known_ids)
if missing:
    raise SystemExit(f"coverage references unknown record IDs: {missing}")
if [page["page"] for page in pages] != [7, 8, 9, 10] or any(not page["regions"] for page in pages):
    raise SystemExit("coverage must contain exactly pages 7--10 with non-empty regions")

COVERAGE.parent.mkdir(parents=True, exist_ok=True)
COVERAGE.write_text(json.dumps({
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": pages,
}, ensure_ascii=False, indent=2) + "\n")

tasks = json.loads(TASKS.read_text())
target_evidence = {f"{DOC}:page{page}:text" for page in range(7, 11)}
for task in tasks:
    if task["document_id"] == DOC and task["evidence_id"] in target_evidence:
        task["state"] = "attempted"
        task["reason"] = "Original page image and page text inspected; records and coverage ledger generated for this page."
TASKS.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({
    "raw_records": str(OUT.relative_to(ROOT)),
    "submitted_records": len(records),
    "updated_records": 14,
    "new_records": 2,
    "coverage": str(COVERAGE.relative_to(ROOT)),
    "coverage_pages": [7, 8, 9, 10],
}, ensure_ascii=False))
