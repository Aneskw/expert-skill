#!/usr/bin/env python3
"""Build source-faithful machine records for ol802465k, PDF pages 1--4."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "runs/current"
DOC = "doc_18cc74d3b2732035"


def ev(page: int) -> list[str]:
    return [f"{DOC}:page{page}:image", f"{DOC}:page{page}:text"]


def fact(value, evidence):
    return {
        "value": value,
        "evidence_ids": list(evidence),
        "verification": "missing" if value is None else "unreviewed",
    }


def field(name, value, evidence, targets=None):
    result = {"name": name, "fact": fact(value, evidence)}
    if targets:
        result["target_entity_ids"] = list(targets)
    return result


def participant(entity_id, role, label, evidence, *, name=None, smiles=None, amounts=()):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence) if name is not None else fact(None, evidence),
        "smiles": fact(smiles, evidence) if smiles is not None else fact(None, evidence),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": list(amounts),
    }


def record(rid, kind, evidence, participants, steps, outcomes, notes=(), unresolved=()):
    return {
        "record_id": f"{DOC}:{rid}",
        "document_id": DOC,
        "source_reaction_id": rid,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": list(dict.fromkeys(evidence)),
        "participants": participants,
        "steps": steps,
        "outcomes": outcomes,
        "notes": [fact(x, evidence) for x in notes],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": list(unresolved),
        },
    }


def step(step_id, participants, conditions):
    return {
        "step_id": step_id,
        "participant_ids": [p["entity_id"] for p in participants],
        "conditions": conditions,
    }


records = []


# Page 1 graphical abstract: generic R/E scope, not a batch-specific experiment.
e1 = ev(1)
p1 = [
    participant("generic_allene_1", "reactant", "generic (2,3-butadienyl)malonate/bis(sulfone) substrate", e1,
                name="generic substrate with R1 and E substituents"),
    participant("generic_propargylic_carbonate_2", "reactant", "generic propargylic carbonate", e1,
                name="generic propargylic carbonate with R2 and R3 substituents"),
    participant("generic_product_3", "product", "generic 1,3,4-alkatrien-2-yl cyclopropane", e1),
    participant("pd_pph3_4", "catalyst", "Pd(PPh3)4", e1,
                amounts=[field("catalyst_loading", {"number": 5, "unit": "mol%"}, e1)]),
    participant("tbai", "reagent", "TBAI", e1, name="tetrabutylammonium iodide",
                smiles="[I-].CCCC[N+](CCCC)(CCCC)CCCC",
                amounts=[field("loading", {"number": 10, "unit": "mol%"}, e1)]),
    participant("mecn", "solvent", "CH3CN", e1, name="acetonitrile", smiles="CC#N"),
]
records.append(record(
    "graphical_abstract_general_scope", "general_scheme", e1, p1,
    [step("generic_coupling_cyclization", p1, [
        field("temperature", {"number": 80, "unit": "°C"}, e1),
        field("time", {"number": 1, "unit": "h", "qualifier": "le", "raw_text": "≤1 h"}, e1),
    ])],
    [
        field("reported_scope_yield_upper_bound", {"number": 96, "unit": "%", "qualifier": "le", "raw_text": "up to 96% yield"}, e1, ["generic_product_3"]),
        field("reported_regioselectivity", "exclusive regioselectivity", e1, ["generic_product_3"]),
    ],
    notes=["Graphical abstract is a generic scope summary, not an individual experimental batch.", "The graphical abstract states base-free conditions."],
    unresolved=["R1, R2, R3, and E are generic; complete structures are not defined.", "Yield basis, scale, atmosphere, workup, and purification are not stated in this summary."],
))


SMILES = {
    "1a": "C=C=CCC(C(=O)OC)C(=O)OC",
    "1b": "C=C=C(Cc1ccccc1)CC(C(=O)OC)C(=O)OC",
    "1c": "C=C=C(CC)CC(C(=O)OC)C(=O)OC",
    "1d": "C=C=CCC(S(=O)(=O)c1ccccc1)S(=O)(=O)c1ccccc1",
    "2a": "C#CC(CC)(CC)OC(=O)OC",
    "2b": "C#CC1(OC(=O)OC)CCCCC1",
    "2c": "C#CC1(OC(=O)OC)CCCC1",
    "2d": "C#CC(C)(C)OC(=O)OC",
    "2f": "COC(=O)OC(C)(C)C#Cc1ccccc1",
    "2g": "COC(=O)OC(C)(C)C#CCCCC",
    "2h": "COC(=O)OC(C)(C)C#CC1CC1",
    "2i": "COC(=O)C#CC(C)(C)OC(=O)OC",
    "2j": "COCC#CC(C)(C)OC(=O)OC",
}


def cyclization_participants(evidence, ptc_label, *, full_amounts, include_4aa=False):
    amount_1 = field("amount", {"number": 0.2, "unit": "mmol"}, evidence) if full_amounts else field("amount", None, evidence)
    amount_2 = field("amount", {"number": 0.3, "unit": "mmol"}, evidence) if full_amounts else field("amount", None, evidence)
    parts = [
        participant("substrate_1a", "reactant", "1a", evidence,
                    name="dimethyl (2,3-butadienyl)malonate", smiles=SMILES["1a"], amounts=[amount_1]),
        participant("carbonate_2a", "reactant", "2a", evidence,
                    name="terminal propargylic methyl carbonate bearing two ethyl groups", smiles=SMILES["2a"], amounts=[amount_2]),
        participant("product_3aa", "product", "3aa", evidence,
                    name="1,3,4-alkatrien-2-yl cyclopropane 3aa"),
        participant("pd_pph3_4", "catalyst", "Pd(PPh3)4", evidence,
                    amounts=[field("catalyst_loading", {"number": 5, "unit": "mol%"}, evidence)]),
        participant("solvent", "solvent", "reaction solvent", evidence,
                    amounts=[field("volume", {"number": 2, "unit": "mL"}, evidence) if full_amounts else field("volume", None, evidence)]),
    ]
    if include_4aa:
        parts.insert(3, participant("product_4aa", "product", "4aa", evidence,
                                    name="five-membered alternative product 4aa"))
    if ptc_label:
        ion, name, smiles = {
            "TBAB": ("Br", "tetrabutylammonium bromide", "[Br-].CCCC[N+](CCCC)(CCCC)CCCC"),
            "TBAI": ("I", "tetrabutylammonium iodide", "[I-].CCCC[N+](CCCC)(CCCC)CCCC"),
            "TBAC": ("Cl", "tetrabutylammonium chloride", "[Cl-].CCCC[N+](CCCC)(CCCC)CCCC"),
        }[ptc_label]
        del ion
        parts.append(participant("ptc", "reagent", ptc_label, evidence, name=name, smiles=smiles))
    return parts


SOLVENTS = {
    "CH3CN": ("acetonitrile", "CC#N"),
    "DMF": ("N,N-dimethylformamide", "CN(C)C=O"),
    "toluene": ("toluene", "Cc1ccccc1"),
    "DCE": ("1,2-dichloroethane", "ClCCCl"),
    "THF": ("tetrahydrofuran", "C1CCOC1"),
    "CH3NO2": ("nitromethane", "C[N+](=O)[O-]"),
}


def set_solvent(parts, label, evidence):
    p = next(x for x in parts if x["entity_id"] == "solvent")
    p["label"] = fact(label, evidence)
    p["name"] = fact(SOLVENTS[label][0], evidence)
    p["smiles"] = fact(SOLVENTS[label][1], evidence)


# Scheme 1 temperature rows at 40 and 60 °C. The 80 °C row is Table 1 entry 1 below.
for temp, hours, yield_value in [(40, 22, 65), (60, 5, 77)]:
    evidence = ev(2)
    parts = cyclization_participants(evidence, "TBAB", full_amounts=False, include_4aa=True)
    set_solvent(parts, "CH3CN", evidence)
    next(p for p in parts if p["entity_id"] == "ptc")["amounts"] = [field("loading", {"number": 10, "unit": "mol%"}, evidence)]
    conditions = [
        field("temperature", {"number": temp, "unit": "°C"}, evidence),
        field("time", {"number": hours, "unit": "h"}, evidence),
        field("atmosphere", None, evidence), field("workup", None, evidence), field("purification", None, evidence),
    ]
    records.append(record(
        f"scheme1_temperature_{temp}c", "optimization_entry", evidence, parts,
        [step("coupling_cyclization", parts, conditions)],
        [
            field("reported_yield_3aa", {"number": yield_value, "unit": "%"}, evidence, ["product_3aa"]),
            field("yield_of_4aa", "table dash (–)", evidence, ["product_4aa"]),
            field("yield_measurement_basis", None, evidence, ["product_3aa"]),
        ],
        unresolved=["Reaction scale, 1a/2a ratio, solvent volume, yield basis, atmosphere, workup, and purification are not stated for this Scheme 1 row.", "Candidate structures and product connectivity require chemistry review."],
    ))


table1 = [
    (1, "CH3CN", "TBAB", 10, 1, 94, "isolated", 80, None),
    (2, "DMF", "TBAB", 10, 1, 65, "isolated", 80, None),
    (3, "toluene", "TBAB", 10, 1, 91, "isolated", 80, None),
    (4, "DCE", "TBAB", 10, 1, 87, "isolated", 80, None),
    (5, "THF", "TBAB", 10, 1, 92, "isolated", 80, None),
    (6, "CH3NO2", "TBAB", 10, 1, 88, "isolated", 80, None),
    (7, "CH3CN", None, None, 48, 39, "isolated", 40, 15),
    (8, "CH3CN", "TBAB", 30, 1, 80, "NMR using mesitylene as internal standard", 80, 8),
    (9, "CH3CN", "TBAI", 10, 1, 96, "isolated", 80, None),
    (10, "CH3CN", "TBAC", 10, 1, 54, "isolated", 80, None),
]
for entry, solvent, ptc, loading, hours, yld, basis, temp, recovery in table1:
    evidence = ev(2) + ev(3) if entry == 9 else ev(2)
    parts = cyclization_participants(evidence, ptc, full_amounts=True, include_4aa=(entry == 1))
    set_solvent(parts, solvent, evidence)
    if ptc:
        next(p for p in parts if p["entity_id"] == "ptc")["amounts"] = [field("loading", {"number": loading, "unit": "mol%"}, evidence)]
    conditions = [
        field("temperature", {"number": temp, "unit": "°C"}, evidence),
        field("time", {"number": hours, "unit": "h"}, evidence),
        field("reaction_vessel_operation", "Schlenk tube", evidence),
        field("atmosphere", None, evidence), field("workup", None, evidence), field("purification", None, evidence),
    ]
    outcomes = [
        field("reported_yield_3aa", {"number": yld, "unit": "%"}, evidence, ["product_3aa"]),
        field("yield_measurement_basis", basis, evidence, ["product_3aa"]),
    ]
    if entry == 1:
        outcomes.append(field("yield_of_4aa", "table dash (–)", evidence, ["product_4aa"]))
    if recovery is not None:
        outcomes.append(field("recovered_starting_material_yield", {"number": recovery, "unit": "%"}, evidence, ["substrate_1a"]))
    notes = []
    if entry == 1:
        notes.append("This row is the same 80 °C/1 h/94% experiment shown in Scheme 1 and is represented once.")
    if entry == 7:
        notes.append("No phase-transfer catalyst was used; the table footnote overrides the common 80 °C condition to 40 °C.")
    if entry == 9:
        next(p for p in parts if p["entity_id"] == "substrate_1a")["amounts"].append(
            field("table2_reaction_scale_range", {"minimum": 0.1, "maximum": 0.2, "unit": "mmol", "raw_text": "0.1–0.2 mmol"}, ev(3))
        )
        next(p for p in parts if p["entity_id"] == "carbonate_2a")["amounts"].append(
            field("table2_equivalents", {"number": 1.5, "unit": "equiv"}, ev(3))
        )
        notes.append("Table 1 entry 9 and Table 2 entry 1 report the same optimized 1a/2a/TBAI experiment at 96% isolated yield; both appearances are merged into this record.")
    rid = "table1_entry9_table2_entry1_3aa" if entry == 9 else f"table1_entry{entry}"
    kind = "substrate_scope_entry" if entry == 9 else "optimization_entry"
    records.append(record(
        rid, kind, evidence, parts,
        [step("coupling_cyclization", parts, conditions)], outcomes, notes=notes,
        unresolved=["Atmosphere, workup, and purification are not stated.", "Candidate structures and product connectivity require chemistry review."],
    ))


SUBSTRATE_1 = {
    "1a": ("R1=H, E=CO2Me substrate 1a", SMILES["1a"]),
    "1b": ("R1=Bn, E=CO2Me substrate 1b", SMILES["1b"]),
    "1c": ("R1=Et, E=CO2Me substrate 1c", SMILES["1c"]),
    "1d": ("R1=H, E=SO2Ph substrate 1d", SMILES["1d"]),
}
SUBSTRATE_2 = {
    "2a": ("R2=Et, R3=H propargylic carbonate 2a", SMILES["2a"]),
    "2b": ("R2/R2=-(CH2)5-, R3=H propargylic carbonate 2b", SMILES["2b"]),
    "2c": ("R2/R2=-(CH2)4-, R3=H propargylic carbonate 2c", SMILES["2c"]),
    "2d": ("R2=Me, R3=H propargylic carbonate 2d", SMILES["2d"]),
    "2f": ("R2=Me, R3=Ph propargylic carbonate 2f", SMILES["2f"]),
    "2g": ("R2=Me, R3=n-Bu propargylic carbonate 2g", SMILES["2g"]),
    "2h": ("R2=Me, R3=c-C3H5 propargylic carbonate 2h", SMILES["2h"]),
    "2i": ("R2=Me, R3=CO2Me propargylic carbonate 2i", SMILES["2i"]),
    "2j": ("R2=Me, R3=CH2OMe propargylic carbonate 2j", SMILES["2j"]),
}
table2 = [
    (1, "1a", "2a", "3aa", 96), (2, "1b", "2a", "3ba", 78),
    (3, "1b", "2b", "3bb", 92), (4, "1c", "2a", "3ca", 92),
    (5, "1d", "2a", "3da", 92), (6, "1a", "2b", "3ab", 73),
    (7, "1a", "2c", "3ac", 75), (8, "1a", "2d", "3ad", 85),
    (9, "1a", "2f", "3af", 89), (10, "1a", "2g", "3ag", 79),
    (11, "1a", "2h", "3ah", 91), (12, "1a", "2i", "3ai", 96),
    (13, "1a", "2j", "3aj", 90),
]
for entry, s1, s2, prod, yld in table2:
    if entry == 1:
        continue
    evidence = ev(3)
    parts = [
        participant("substrate_1", "reactant", s1, evidence, name=SUBSTRATE_1[s1][0], smiles=SUBSTRATE_1[s1][1],
                    amounts=[field("reaction_scale", {"minimum": 0.1, "maximum": 0.2, "unit": "mmol", "raw_text": "0.1–0.2 mmol"}, evidence)]),
        participant("carbonate_2", "reactant", s2, evidence, name=SUBSTRATE_2[s2][0], smiles=SUBSTRATE_2[s2][1],
                    amounts=[field("equivalents", {"number": 1.5, "unit": "equiv"}, evidence)]),
        participant("product_3", "product", prod, evidence, name=f"cyclopropylvinyl allene product {prod}"),
        participant("pd_pph3_4", "catalyst", "Pd(PPh3)4", evidence,
                    amounts=[field("catalyst_loading", {"number": 5, "unit": "mol%"}, evidence)]),
        participant("tbai", "reagent", "TBAI", evidence, name="tetrabutylammonium iodide",
                    smiles="[I-].CCCC[N+](CCCC)(CCCC)CCCC",
                    amounts=[field("loading", {"number": 10, "unit": "mol%"}, evidence)]),
        participant("mecn", "solvent", "CH3CN", evidence, name="acetonitrile", smiles="CC#N",
                    amounts=[field("volume", {"number": 2, "unit": "mL"}, evidence)]),
    ]
    conditions = [
        field("temperature", {"number": 80, "unit": "°C"}, evidence),
        field("time", None, evidence),
        field("reaction_vessel_operation", "Schlenk tube", evidence),
        field("atmosphere", None, evidence), field("workup", None, evidence), field("purification", None, evidence),
    ]
    records.append(record(
        f"table2_entry{entry}_{prod}", "substrate_scope_entry", evidence, parts,
        [step("coupling_cyclization", parts, conditions)],
        [
            field("isolated_yield", {"number": yld, "unit": "%"}, evidence, ["product_3"]),
            field("yield_measurement_basis", "isolated yield", evidence, ["product_3"]),
        ],
        unresolved=["Table 2 does not state reaction time, atmosphere, workup, or purification.", "Product candidate structure is not encoded; connectivity and all candidate structures require chemistry review."],
    ))


# Page 3 proposed mechanism, explicitly non-experimental.
e3 = ev(3)
pm = [
    participant("generic_carbonate_2", "reactant", "generic propargylic carbonate 2", e3),
    participant("generic_allene_1", "reactant", "generic allene substrate 1", e3),
    participant("pd0", "catalyst", "Pd(0)", e3),
    participant("intermediate_m1", "unspecified_agent", "allenylpalladium intermediate M1", e3),
    participant("intermediate_syn_m2", "unspecified_agent", "π-allylpalladium intermediate syn-M2", e3),
    participant("generic_product_3", "product", "generic product 3", e3),
]
records.append(record(
    "scheme2_plausible_mechanism", "mechanism", e3, pm,
    [
        step("oxidative_addition", [pm[0], pm[2], pm[3]], [field("operation", "oxidative addition of 2 to Pd(0), with CO2 loss, proposed to form M1", e3)]),
        step("carbopalladation", [pm[3], pm[1], pm[4]], [field("operation", "intermolecular carbopalladation proposed to form syn-M2", e3)]),
        step("cyclization", [pm[4], pm[5]], [field("operation", "deprotonation by methoxy anion followed by regioselective intramolecular attack", e3)]),
    ], [],
    notes=["Scheme 2 is explicitly titled a plausible mechanism and is not an observed experimental sequence."],
    unresolved=["Generic R groups and organopalladium structures are not fully defined and are not encoded as SMILES.", "The proposed intermediates are not independently verified."],
))


# Table 3; the catalyst/CO/room-temperature statements begin on page 3 and the table is on page 4.
table3 = [
    (1, "3aa", "R1=H, R2=Et, R3=H", "5a", 7, 72),
    (2, "3ad", "R1=H, R2=Me, R3=H", "5b", 7, 80),
    (3, "3ca", "R1=Et, R2=Et, R3=H", "5c", 12, 86),
    (4, "3af", "R1=H, R2=Me, R3=Ph", "5d", 36, 89),
    (5, "3ac", "R1=H, R2/R2=-(CH2)4-, R3=H", "5e", 3, 82),
    (6, "3ag", "R1=H, R2=Me, R3=n-Bu", "5f", 60, 69),
]
for entry, substrate, description, prod, hours, yld in table3:
    evidence = ev(3) + ev(4)
    parts = [
        participant("substrate_3", "reactant", substrate, evidence, name=f"2-cyclopropyl-1,3,4-triene {substrate}; {description}",
                    amounts=[field("reaction_scale", {"minimum": 0.1, "maximum": 0.2, "unit": "mmol", "raw_text": "0.1–0.2 mmol"}, ev(4))]),
        participant("product_5", "product", prod, evidence, name=f"polysubstituted cyclopentenone {prod}"),
        participant("rh_dimer", "catalyst", "[RhCl(CO)2]2", evidence,
                    amounts=[field("catalyst_loading", {"number": 2.5, "unit": "mol%"}, e3)]),
        participant("co", "reagent", "CO", evidence, name="carbon monoxide", smiles="[C-]#[O+]",
                    amounts=[field("reported_pressure", "1 atm", e3)]),
        participant("dce", "solvent", "DCE", evidence, name="1,2-dichloroethane", smiles="ClCCCl",
                    amounts=[field("volume", {"number": 2, "unit": "mL"}, ev(4))]),
    ]
    conditions = [
        field("temperature", "r.t.", evidence),
        field("time", {"number": hours, "unit": "h"}, ev(4)),
        field("atmosphere", "1 atm CO", e3),
        field("workup", None, ev(4)), field("purification", None, ev(4)),
    ]
    records.append(record(
        f"table3_entry{entry}_{prod}", "substrate_scope_entry", evidence, parts,
        [step("pauson_khand_4_plus_1_cycloaddition", parts, conditions)],
        [
            field("isolated_yield", {"number": yld, "unit": "%"}, ev(4), ["product_5"]),
            field("yield_measurement_basis", "isolated yield", ev(4), ["product_5"]),
        ],
        unresolved=["Table 3 does not state workup or purification.", "Substrate and product structures are not encoded; connectivity requires chemistry review."],
    ))


raw_path = OUT / "raw_model/records_pages_0001_0004.json"
raw_path.parent.mkdir(parents=True, exist_ok=True)
raw_path.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")


ids = {r["source_reaction_id"]: r["record_id"] for r in records}
page2_ids = [ids["scheme1_temperature_40c"], ids["scheme1_temperature_60c"]] + [
    ids["table1_entry9_table2_entry1_3aa"] if i == 9 else ids[f"table1_entry{i}"] for i in range(1, 11)
]
table2_ids = [
    ids["table1_entry9_table2_entry1_3aa"] if i == 1 else ids[f"table2_entry{i}_{prod}"]
    for i, _, _, prod, _ in table2
]
table3_ids = [ids[f"table3_entry{i}_{prod}"] for i, _, _, prod, _, _ in table3]

coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1,
            "state": "attempted",
            "regions": [
                {
                    "region": "graphical abstract beneath the ABSTRACT banner",
                    "finding": "Generic present-paper coupling-cyclization scope with R/E variables, Pd(PPh3)4/TBAI, CH3CN, 80 °C, ≤1 h and up-to-96% claim; classified as a general scheme rather than a batch experiment.",
                    "evidence_ids": ev(1),
                },
                {
                    "region": "title, abstract, introduction, and reference columns",
                    "finding": "High-level present-paper claims and cited background only; no additional independent row-level experiment was created.",
                    "evidence_ids": ev(1),
                },
            ],
            "record_ids": [ids["graphical_abstract_general_scope"]],
            "unresolved": ["Generic R1/R2/R3/E structures and the summary yield basis are not fully specified."],
        },
        {
            "page": 2,
            "state": "attempted",
            "regions": [
                {
                    "region": "upper-left Scheme 1 and adjacent optimization prose",
                    "finding": "Three temperature-screen rows localized. The 80 °C/1 h/94% row is the same experiment as Table 1 entry 1 and is merged; 40 and 60 °C remain separate records. Scheme dashes for 4aa are preserved.",
                    "evidence_ids": ev(2),
                },
                {
                    "region": "upper-right Table 1 including footnotes a-e",
                    "finding": "Ten solvent/PTC optimization rows extracted with row-specific PTC loading, entry-7 temperature override, NMR basis for entry 8, and recovered-starting-material outcomes for entries 7 and 8. Entry 9 is merged with the identical Table 2 entry 1 experiment.",
                    "evidence_ids": ev(2),
                },
                {
                    "region": "remaining two-column prose and citations",
                    "finding": "Narrative explanation of Scheme 1/Table 1 and cited prior chemistry; no additional batch record beyond the table/scheme rows.",
                    "evidence_ids": ev(2),
                },
            ],
            "record_ids": page2_ids,
            "unresolved": ["Scheme 1 rows do not state scale, reagent ratio, solvent volume, or yield basis.", "Atmosphere, workup, and purification are absent."],
        },
        {
            "page": 3,
            "state": "attempted",
            "regions": [
                {
                    "region": "top Table 2 and footnote a",
                    "finding": "Thirteen independent substrate-scope rows extracted with shared scale range, 1.5 equivalents carbonate, catalyst/PTC loadings, solvent volume, temperature, Schlenk vessel, isolated yields, and row-specific substituents.",
                    "evidence_ids": ev(3),
                },
                {
                    "region": "lower-right Scheme 2 and mechanism prose",
                    "finding": "Oxidative addition/carbopalladation/cyclization sequence classified as a plausible mechanism, not an observed experiment.",
                    "evidence_ids": ev(3),
                },
                {
                    "region": "lower-center prose introducing Table 3",
                    "finding": "Shared [RhCl(CO)2]2 loading, 1 atm CO, and room-temperature conditions linked to the six Table 3 records on page 4.",
                    "evidence_ids": ev(3),
                },
            ],
            "record_ids": table2_ids + [ids["scheme2_plausible_mechanism"]] + table3_ids,
            "unresolved": ["Table 2 does not state reaction time, atmosphere, workup, or purification.", "Complex product and organopalladium structures require chemistry review."],
        },
        {
            "page": 4,
            "state": "attempted",
            "regions": [
                {
                    "region": "upper-left Table 3, reaction arrow, and footnotes a-b",
                    "finding": "Six independent [4+1] cycloaddition rows extracted with substrate identities, times, isolated yields, scale range, DCE volume, and the shared catalyst/CO/room-temperature conditions from page 3.",
                    "evidence_ids": ev(4),
                },
                {
                    "region": "upper-right conclusion, acknowledgements, and Supporting Information Available notice",
                    "finding": "No additional experiment. The notice says SI exists online, but no SI file is supplied or explicitly associated, so no SI details were inferred.",
                    "evidence_ids": ev(4),
                },
                {
                    "region": "lower references",
                    "finding": "Cited literature only; no experiment-specific arrows or conditions to extract as present-paper records.",
                    "evidence_ids": ev(4),
                },
            ],
            "record_ids": table3_ids,
            "unresolved": ["Table 3 omits workup and purification.", "SI association remains unestablished."],
        },
    ],
}
(OUT / "coverage").mkdir(parents=True, exist_ok=True)
(OUT / "coverage/pages_0001_0004.json").write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")


tasks_path = OUT / "tasks.json"
tasks = json.loads(tasks_path.read_text())
for task in tasks:
    if task.get("document_id") == DOC and task.get("evidence_id") in {f"{DOC}:page{i}:text" for i in range(1, 5)}:
        task["state"] = "attempted"
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"records": len(records), "raw": str(raw_path), "coverage_pages": len(coverage["pages"])}, ensure_ascii=False))
