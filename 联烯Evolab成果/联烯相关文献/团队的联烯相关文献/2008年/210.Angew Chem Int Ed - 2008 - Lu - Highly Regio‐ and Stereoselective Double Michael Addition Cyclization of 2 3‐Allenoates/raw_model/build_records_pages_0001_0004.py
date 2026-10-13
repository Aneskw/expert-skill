#!/usr/bin/env python3
"""Build evidence-linked machine records for Lu, Chai & Ma (2008), PDF pages 1-4."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "runs/current"
RAW = OUT / "raw_model/records_pages_0001_0004.json"
COVERAGE = OUT / "coverage/pages_0001_0004.json"
TASKS = OUT / "tasks.json"
DOC = "doc_0fbb62f8db3b3133"


def ev(page: int) -> list[str]:
    return [f"{DOC}:page{page}:image", f"{DOC}:page{page}:text"]


def fact(value, evidence):
    return {
        "value": value,
        "evidence_ids": list(evidence) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def field(name, value, evidence, targets=None):
    item = {"name": name, "fact": fact(value, evidence)}
    if targets:
        item["target_entity_ids"] = list(targets)
    return item


def participant(entity_id, role, label, name, smiles, evidence, amounts=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence),
        "smiles": fact(smiles, evidence),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": amounts or [],
    }


def base_record(suffix, kind, evidence, unresolved):
    return {
        "record_id": f"{DOC}:{suffix}",
        "document_id": DOC,
        "source_reaction_id": suffix,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": list(dict.fromkeys(evidence)),
        "participants": [],
        "steps": [],
        "outcomes": [],
        "notes": [],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": list(unresolved),
        },
    }


ALLENES = {
    "1a": ("ethyl 2-methyl-4-phenyl-2,3-butadienoate", "CCOC(=O)C(C)=C=Cc1ccccc1"),
    "1b": ("methyl 2-methyl-4-phenyl-2,3-butadienoate", "COC(=O)C(C)=C=Cc1ccccc1"),
    "1c": ("ethyl 4-(4-bromophenyl)-2-methyl-2,3-butadienoate", "CCOC(=O)C(C)=C=Cc1ccc(Br)cc1"),
    "1d": ("ethyl 4-(4-chlorophenyl)-2-methyl-2,3-butadienoate", "CCOC(=O)C(C)=C=Cc1ccc(Cl)cc1"),
    "1e": ("ethyl 4-(4-fluorophenyl)-2-methyl-2,3-butadienoate", "CCOC(=O)C(C)=C=Cc1ccc(F)cc1"),
    "1f": ("ethyl 4-(4-methoxyphenyl)-2-methyl-2,3-butadienoate", "CCOC(=O)C(C)=C=Cc1ccc(OC)cc1"),
    "1g": ("ethyl 2-ethyl-4-phenyl-2,3-butadienoate", "CCOC(=O)C(CC)=C=Cc1ccccc1"),
}


def product_smiles(ar="c2ccccc2", r1="C", ester="OCC", r="CC"):
    return f"O=C1C({r1})=C({r})C({ar})C(=C{ar})C1({r1})C(=O){ester}"


PRODUCTS = {
    "2a": ("(Z)-2a", product_smiles()),
    "2b": ("(Z)-2b", product_smiles(ester="OC")),
    "2c": ("(Z)-2c", product_smiles(ar="c2ccc(Br)cc2")),
    "2d": ("(Z)-2d", product_smiles(ar="c2ccc(Cl)cc2")),
    "2e": ("(Z)-2e", product_smiles(ar="c2ccc(F)cc2")),
    "2f": ("(Z)-2f", product_smiles(ar="c2ccc(OC)cc2")),
    "2g": ("(Z)-2g", product_smiles(r1="CC")),
    "2h": ("(Z)-2h", product_smiles(r="C")),
    "2i": ("(Z)-2i", product_smiles(ester="OC", r="C")),
    "2j": ("(Z)-2j", product_smiles(ar="c2ccc(Cl)cc2", r="C")),
    "2k": ("(Z)-2k", product_smiles(r="CCCC")),
}


def p_allene(label, evidence, amounts=None, display_label=None):
    name, smiles = ALLENES[label]
    return participant("allene", "reactant", display_label or label, name, smiles, evidence, amounts)


def p_product(label, evidence, display_label=None):
    name, smiles = PRODUCTS[label]
    return participant("product", "product", display_label or label, name, smiles, evidence)


def p_solvent(entity_id, label, smiles, evidence, volume=None):
    amounts = [] if volume is None else [field("volume", volume, evidence)]
    return participant(entity_id, "solvent", label, label, smiles, evidence, amounts)


def missing_operational(evidence, atmosphere=None, workup=None, purification=None):
    return [
        field("atmosphere", atmosphere, evidence),
        field("workup", workup, evidence),
        field("purification", purification, evidence),
    ]


records = []

# Table 1: reaction-time and Et2Zn-loading optimization.
table1 = [
    (1, 3.0, 90, 6, 47, 14, True),
    (2, 3.0, 90, 9, 61, 14, False),
    (3, 3.0, 15, 10, 69, 5, False),
    (4, 2.0, 15, 10, 60, 14, False),
    (5, 1.5, 15, 10, 58, 16, False),
]
for entry, equiv, t1, t2, y2a, y3a, catalyst in table1:
    evidence = ev(1)
    rec = base_record(
        f"table1_entry{entry}", "optimization_entry", evidence,
        ["Workup and purification are not stated for this table entry.",
         "Candidate product connectivity and stereochemistry require chemical review."],
    )
    rec["participants"] = [
        p_allene("1a", evidence, [field("amount", {"number": 0.4, "unit": "mmol"}, evidence)]),
        participant("et2zn", "reagent", "Et2Zn", "diethylzinc", "CC[Zn]CC", evidence, [
            field("equivalents", {"number": equiv, "unit": "equiv"}, evidence),
            field("solution_concentration", {"number": 0.88, "unit": "M"}, evidence),
        ]),
        p_solvent("toluene", "toluene", "Cc1ccccc1", evidence, {"number": 5, "unit": "mL"}),
        p_solvent("hexanes", "hexanes (Et2Zn solution carrier)", "CCCCCC", evidence),
        p_product("2a", evidence),
        participant("product_3a", "product", "3a", "ethyl 3-ethyl-2-methyl-4-phenyl-3-butenoate", "CCOC(=O)C(C)C(CC)=Cc1ccccc1", evidence),
        participant("ch2br2", "reagent", "CH2Br2", "dibromomethane internal standard", "BrCBr", evidence),
    ]
    if catalyst:
        rec["participants"].append(participant(
            "feacac3", "catalyst", "Fe(acac)3", "iron(III) acetylacetonate", None, evidence,
            [field("catalyst_loading", {"number": 5, "unit": "mol%"}, evidence)],
        ))
    rec["steps"] = [{
        "step_id": "reaction",
        "participant_ids": [p["entity_id"] for p in rec["participants"]],
        "conditions": [
            field("initial_temperature", {"number": -78, "unit": "°C"}, evidence),
            field("time_at_minus_78", {"number": t1, "unit": "min"}, evidence),
            field("warm_to", "r.t.", evidence),
            field("time_at_room_temperature", {"number": t2, "unit": "h"}, evidence),
            *missing_operational(evidence),
        ],
    }]
    rec["outcomes"] = [
        field("nmr_yield_2a", {"number": y2a, "unit": "%"}, evidence, ["product"]),
        field("nmr_yield_3a", {"number": y3a, "unit": "%"}, evidence, ["product_3a"]),
        field("yield_measurement_basis", "NMR spectroscopy using CH2Br2 as internal standard", evidence),
    ]
    records.append(rec)

# Table 2: solvent optimization.
table2 = [
    (1, "toluene", "Cc1ccccc1", 76, 10, "table dash (–)"),
    (2, "THF", "C1CCOC1", "trace", 13, 68),
    (3, "Et2O", "CCOCC", 46, 20, 10),
    (4, "Bu2O", "CCCCOCCCC", 50, 16, "table dash (–)"),
    (5, "CH2Cl2", "ClCCl", 57, 17, 8),
    (6, "benzene", "c1ccccc1", 59, 8, "table dash (–)"),
    (7, "ethylbenzene", "CCc1ccccc1", 72, 10, "table dash (–)"),
]
for entry, solvent, solvent_smiles, y2a, y3a, recovery in table2:
    evidence = ev(2)
    rec = base_record(
        f"table2_entry{entry}", "optimization_entry", evidence,
        ["Atmosphere, workup, and purification are not stated.",
         "Candidate product connectivity and stereochemistry require chemical review."],
    )
    rec["participants"] = [
        p_allene("1a", evidence, [field("amount", {"number": 0.4, "unit": "mmol"}, evidence)]),
        participant("et2zn", "reagent", "Et2Zn", "diethylzinc", "CC[Zn]CC", evidence, [
            field("equivalents", {"number": 3, "unit": "equiv"}, evidence),
            field("solution_concentration", {"number": 0.88, "unit": "M"}, evidence),
        ]),
        p_solvent("reaction_solvent", solvent, solvent_smiles, evidence, {"number": 5, "unit": "mL"}),
        p_solvent("hexanes", "hexanes (Et2Zn solution carrier)", "CCCCCC", evidence),
        p_product("2a", evidence),
        participant("product_3a", "product", "3a", "ethyl 3-ethyl-2-methyl-4-phenyl-3-butenoate", "CCOC(=O)C(C)C(CC)=Cc1ccccc1", evidence),
        participant("ch2br2", "reagent", "CH2Br2", "dibromomethane internal standard", "BrCBr", evidence),
    ]
    rec["steps"] = [{
        "step_id": "reaction",
        "participant_ids": [p["entity_id"] for p in rec["participants"]],
        "conditions": [
            field("temperature", "r.t.", evidence),
            field("time", {"number": 1, "unit": "h"}, evidence),
            *missing_operational(evidence),
        ],
    }]
    rec["outcomes"] = [
        field("nmr_yield_2a", y2a if isinstance(y2a, str) else {"number": y2a, "unit": "%"}, evidence, ["product"]),
        field("nmr_yield_3a", {"number": y3a, "unit": "%"}, evidence, ["product_3a"]),
        field("recovered_starting_material_yield", recovery if isinstance(recovery, str) else {"number": recovery, "unit": "%"}, evidence, ["allene"]),
        field("yield_and_recovery_measurement_basis", "NMR spectroscopy using CH2Br2 as internal standard", evidence),
    ]
    records.append(rec)

# Table 3: isolated substrate scope, with the detailed racemic 2a procedure merged into entry 1.
table3 = [
    (1, "1a", "Et", "2a", "r.t.", 1, 65),
    (2, "1b", "Et", "2b", "r.t.", 23, 79),
    (3, "1c", "Et", "2c", "r.t.", 3, 63),
    (4, "1d", "Et", "2d", "r.t.", 3, 69),
    (5, "1e", "Et", "2e", "r.t.", 8, 65),
    (6, "1f", "Et", "2f", "r.t.", 2, 57),
    (7, "1g", "Et", "2g", "r.t.", 3, 47),
    (8, "1a", "Me", None, "r.t.", 13, None),
    (9, "1a", "Me", "2h", 100, 18, 52),
    (10, "1b", "Me", "2i", 100, 24, 64),
    (11, "1d", "Me", "2j", 100, 12, 60),
    (12, "1a", "nBu", "2k", "r.t.", 3, 82),
]
organozinc = {
    "Et": ("Et2Zn", "diethylzinc", "CC[Zn]CC", 0.88, "hexanes", "CCCCCC"),
    "Me": ("Me2Zn", "dimethylzinc", "C[Zn]C", 1.2, "toluene (Me2Zn solution carrier)", "Cc1ccccc1"),
    "nBu": ("nBu2Zn", "dibutylzinc", "CCCC[Zn]CCCC", 1.0, "heptane", "CCCCCCC"),
}
for entry, allene, alkyl, product, temp, time, yield_value in table3:
    evidence = ev(2) + (ev(3) if entry == 1 else [])
    unresolved = ["Candidate structures and stereochemical assignments require chemical review."]
    if entry != 1:
        unresolved.append("Atmosphere, workup, and purification are not stated for this table row.")
    label, reagent_name, reagent_smiles, concentration, carrier, carrier_smiles = organozinc[alkyl]
    allene_amounts = [field("amount", {"number": 0.4, "unit": "mmol"}, ev(2))]
    reagent_amounts = [
        field("amount", {"number": 1.2, "unit": "mmol"}, ev(2)),
        field("equivalents", {"number": 3, "unit": "equiv"}, ev(2)),
        field("solution_concentration", {"number": concentration, "unit": "M"}, ev(2)),
    ]
    if entry == 1:
        allene_amounts.append(field("mass", {"number": 83.6, "unit": "mg"}, ev(3)))
        reagent_amounts.append(field("solution_volume", {"number": 1.36, "unit": "mL"}, ev(3)))
    rec = base_record(f"table3_entry{entry}", "substrate_scope_entry", evidence, unresolved)
    rec["participants"] = [
        p_allene(allene, evidence, allene_amounts),
        participant("organozinc", "reagent", label, reagent_name, reagent_smiles, evidence, reagent_amounts),
        p_solvent("toluene", "toluene", "Cc1ccccc1", evidence, {"number": 5, "unit": "mL"} if entry == 1 else {"number": 5, "unit": "mL"}),
        p_solvent("carrier", carrier, carrier_smiles, ev(2)),
    ]
    if product:
        rec["participants"].append(p_product(product, evidence))
    else:
        rec["participants"].append(participant("expected_product", "product", "expected cyclization product", None, None, evidence))
    conditions = [
        field("temperature", temp if isinstance(temp, str) else {"number": temp, "unit": "°C"}, ev(2)),
        field("time", {"number": time, "unit": "h"}, ev(2)),
    ]
    if entry == 1:
        conditions.extend([
            field("atmosphere", "nitrogen", ev(3)),
            field("operation", "Et2Zn solution added by syringe over 3–5 min at room temperature; completion monitored by TLC", ev(3)),
            field("workup", "Quenched dropwise with saturated NH4Cl (1 mL), then water (5 mL); extracted with Et2O (3 × 30 mL); washed with 1% aqueous HCl, saturated aqueous NaHCO3, and brine; dried over anhydrous Na2SO4; evaporated", ev(3)),
            field("purification", "Silica-gel column chromatography, petroleum ether/ethyl acetate 20:1", ev(3)),
        ])
    else:
        conditions.extend(missing_operational(ev(2)))
    rec["steps"] = [{
        "step_id": "reaction",
        "participant_ids": [p["entity_id"] for p in rec["participants"]],
        "conditions": conditions,
    }]
    if product:
        rec["outcomes"] = [
            field("isolated_yield", {"number": yield_value, "unit": "%"}, ev(2), ["product"]),
            field("yield_measurement_basis", "isolated product", ev(2)),
        ]
        if entry == 1:
            rec["outcomes"].append(field("product_mass", {"number": 52.0, "unit": "mg"}, ev(3), ["product"]))
            rec["notes"].append(fact("The isolated product is reported as a solid; the analytical data continue on page 4.", ev(3)))
    else:
        rec["outcomes"] = [
            field("expected_product_yield", "not formed", ev(2), ["expected_product"]),
            field("recovered_starting_material_yield", {"number": 60, "unit": "%"}, ev(2), ["allene"]),
            field("recovery_measurement_basis", "isolated recovery", ev(2)),
        ]
    records.append(rec)

# Table 4: optically active allene scope. The detailed (+)-(4R,6S)-2a batch is merged into entry 2.
table4 = [
    (1, "1a", "(−)-(R)-1a", 97, "Et", "(−)-(4S,6R)-2a", "2a", [("r.t.", 1)], 61, 97),
    (2, "1a", "(+)-(S)-1a", 96, "Et", "(+)-(4R,6S)-2a", "2a", [("r.t.", 3)], 76, 96),
    (3, "1a", "(−)-(R)-1a", 97, "Me", "(−)-(4S,6R)-2h", "2h", [(100, 12)], 51, 95),
    (4, "1a", "(+)-(S)-1a", 96, "Me", "(+)-(4R,6S)-2h", "2h", [(100, 12)], 52, 95),
    (5, "1a", "(−)-(R)-1a", 98, "nBu", "(−)-(4S,6R)-2k", "2k", [("r.t.", 3), (30, 2)], 69, 97),
    (6, "1a", "(+)-(S)-1a", 96, "nBu", "(+)-(4R,6S)-2k", "2k", [("r.t.", 2), (50, 2)], 73, 96),
    (7, "1c", "(−)-(R)-1c", 92, "Et", "(−)-(4S,6R)-2c", "2c", [("r.t.", 4.5)], 65, 92),
    (8, "1c", "(+)-(S)-1c", 86, "Et", "(+)-(4R,6S)-2c", "2c", [("r.t.", 3)], 69, 85),
]
for entry, allene, input_label, input_ee, alkyl, product_label, product, stages, yld, product_ee in table4:
    evidence = ev(2)
    if entry in (3, 4):
        evidence += ev(3)
    if entry == 2:
        evidence += ev(4)
    label, reagent_name, reagent_smiles, concentration, carrier, carrier_smiles = organozinc[alkyl]
    allene_amounts = [field("starting_material_ee", {"number": input_ee, "unit": "%"}, ev(2))]
    reagent_amounts = [
        field("equivalents", {"number": 3, "unit": "equiv"}, ev(2)),
        field("solution_concentration", {"number": concentration, "unit": "M"}, ev(2)),
    ]
    toluene_volume = None
    if entry == 2:
        allene_amounts.extend([
            field("mass", {"number": 40.4, "unit": "mg"}, ev(4)),
            field("amount", {"number": 0.2, "unit": "mmol"}, ev(4)),
        ])
        reagent_amounts.extend([
            field("solution_volume", {"number": 0.70, "unit": "mL"}, ev(4)),
            field("amount", {"number": 0.6, "unit": "mmol"}, ev(4)),
        ])
        toluene_volume = {"number": 2.5, "unit": "mL"}
    rec = base_record(
        f"table4_entry{entry}", "substrate_scope_entry", evidence,
        ["Atmosphere, workup, and purification are not stated.",
         "Candidate connectivity and absolute stereochemistry require chemical review."],
    )
    rec["participants"] = [
        p_allene(allene, evidence, allene_amounts, input_label),
        participant("organozinc", "reagent", label, reagent_name, reagent_smiles, evidence, reagent_amounts),
        p_solvent("toluene", "toluene", "Cc1ccccc1", evidence, toluene_volume),
        p_solvent("carrier", carrier, carrier_smiles, ev(2)),
        p_product(product, evidence, product_label),
    ]
    rec["steps"] = []
    for number, (stage_temp, stage_time) in enumerate(stages, 1):
        conditions = [
            field("temperature", stage_temp if isinstance(stage_temp, str) else {"number": stage_temp, "unit": "°C"}, ev(2)),
            field("time", {"number": stage_time, "unit": "h"}, ev(2)),
        ]
        if number == len(stages):
            conditions.extend(missing_operational(evidence))
        rec["steps"].append({
            "step_id": f"reaction_stage_{number}",
            "participant_ids": [p["entity_id"] for p in rec["participants"]],
            "conditions": conditions,
        })
    rec["outcomes"] = [
        field("isolated_yield", {"number": yld, "unit": "%"}, ev(2), ["product"]),
        field("product_ee", {"number": product_ee, "unit": "%"}, ev(2), ["product"]),
        field("yield_measurement_basis", "isolated product", ev(2)),
        field("ee_measurement_basis", "HPLC on a chiral phase", ev(2), ["product"]),
    ]
    if entry == 2:
        rec["outcomes"].extend([
            field("product_mass", {"number": 29.7, "unit": "mg"}, ev(4), ["product"]),
            field("ee_measurement_details", "Chiralcel AD-H; n-hexane/iPrOH 95:5; 0.7 mL min−1; 230 nm; tR(minor) 7.8 min and tR(major) 8.7 min", ev(4), ["product"]),
        ])
        rec["notes"].append(fact("The analytical and spectroscopic data were reported to be identical to those of racemic (Z)-2a.", ev(4)))
    records.append(rec)

# Scheme 1: proposed stereochemical model, kept distinct from observed experiments.
evidence = ev(3)
mechanism = base_record(
    "scheme1_stereochemical_model", "mechanism", evidence,
    ["The pathway and intermediate structures are proposed, not independently verified experimental records.",
     "Intermediate organozinc structures and stereochemistry require expert review."],
)
mechanism["participants"] = [
    p_allene("1a", evidence, display_label="(−)-(R)-1a"),
    participant("et2zn", "reagent", "Et2Zn", "diethylzinc", "CC[Zn]CC", evidence),
    participant("intermediate_4", "unspecified_agent", "4", "alpha-zincated 2-alkenoate 4", None, evidence),
    participant("intermediate_5a", "unspecified_agent", "5A", "proposed cyclization precursor 5A", None, evidence),
    participant("intermediate_5b", "unspecified_agent", "5B", "conformer 5B", None, evidence),
    participant("intermediate_6", "unspecified_agent", "6", "atropisomeric zinc 1,3-dienolate 6", None, evidence),
    participant("product_7", "product", "racemic 7", "protonated alkenoate 7", None, evidence),
    p_product("2a", evidence, "(−)-(4S,6R)-2a"),
]
mechanism["steps"] = [
    {"step_id": "first_michael_addition", "participant_ids": ["allene", "et2zn", "intermediate_4"], "conditions": [field("operation", "Proposed regio- and stereoselective Michael addition", evidence)]},
    {"step_id": "second_michael_addition", "participant_ids": ["intermediate_4", "allene", "intermediate_5a"], "conditions": [field("operation", "Proposed gamma-carbon addition to the center allene carbon", evidence)]},
    {"step_id": "cyclization", "participant_ids": ["intermediate_5a", "intermediate_5b", "product"], "conditions": [field("operation", "Proposed conformational change followed by intramolecular 1,2-addition", evidence)]},
    {"step_id": "alternative_dienolate_path", "participant_ids": ["intermediate_4", "intermediate_6", "product_7"], "conditions": [field("operation", "Proposed alternative zinc 1,3-dienolate and protonation pathway", evidence)]},
]
mechanism["outcomes"] = [field("reported_Z_E_ratio_for_racemic_7", "71:29 by NMR", evidence, ["product_7"])]
records.append(mechanism)

# Scheme 2: two distinct mechanistic test experiments.
for suffix, starting_label, starting_ee, etmg_equiv, znbr_equiv, second_time, y2a, ee2a, y7, recovery, recovery_ee in [
    ("scheme2_test1_racemic", "(±)-1a", None, 1.5, 1.5, 1, {"number": 3, "unit": "%", "qualifier": "le", "raw_text": "≤3%"}, None, 28, 11, None),
    ("scheme2_test2_enantioenriched", "(−)-(R)-1a", 98, 0.5, 0.5, 2, {"number": 7, "unit": "%"}, 0, 12, 52, 97),
]:
    evidence = ev(3)
    rec = base_record(
        suffix, "reported_experiment", evidence,
        ["Atmosphere, workup, and purification are not stated.",
         "The structures and exact speciation of the magnesium/zinc dienolates are not independently verified."],
    )
    allene_amounts = []
    if starting_ee is not None:
        allene_amounts.append(field("starting_material_ee", {"number": starting_ee, "unit": "%"}, evidence))
    rec["participants"] = [
        p_allene("1a", evidence, allene_amounts, starting_label),
        participant("etmgbr", "reagent", "EtMgBr", "ethylmagnesium bromide", "CC[Mg]Br", evidence, [field("equivalents", {"number": etmg_equiv, "unit": "equiv"}, evidence)]),
        participant("feacac3", "catalyst", "Fe(acac)3", "iron(III) acetylacetonate", None, evidence, [field("catalyst_loading", {"number": 5, "unit": "mol%"}, evidence)]),
        participant("znbr2", "reagent", "ZnBr2", "zinc bromide", "Br[Zn]Br", evidence, [field("equivalents", {"number": znbr_equiv, "unit": "equiv"}, evidence)]),
        p_product("2a", evidence),
        participant("product_7", "product", "7", "protonated alkenoate 7", None, evidence),
        participant("ch2br2", "reagent", "CH2Br2", "dibromomethane internal standard", "BrCBr", evidence),
    ]
    if suffix.endswith("racemic"):
        rec["participants"].append(participant("additional_allene", "reactant", "(±)-1a", ALLENES["1a"][0], ALLENES["1a"][1], evidence, [field("equivalents", {"number": 1, "unit": "equiv"}, evidence)]))
    rec["steps"] = [
        {"step_id": "grignard_addition", "participant_ids": ["allene", "etmgbr", "feacac3"], "conditions": [field("temperature", {"number": -78, "unit": "°C"}, evidence), field("time", {"number": 1.5, "unit": "h"}, evidence)]},
        {"step_id": "transmetalation_and_reaction", "participant_ids": [p["entity_id"] for p in rec["participants"]], "conditions": [field("operation", "ZnBr2 addition at −78 °C followed by warming to room temperature", evidence), field("time", {"number": second_time, "unit": "h"}, evidence), *missing_operational(evidence)]},
    ]
    rec["outcomes"] = [
        field("nmr_yield_2a", y2a, evidence, ["product"]),
        field("nmr_yield_7", {"number": y7, "unit": "%"}, evidence, ["product_7"]),
        field("recovered_starting_material_yield", {"number": recovery, "unit": "%"}, evidence, ["allene"]),
        field("yield_and_recovery_measurement_basis", "NMR spectroscopy using CH2Br2 as internal standard", evidence),
    ]
    if ee2a is not None:
        rec["outcomes"].append(field("product_ee", {"number": ee2a, "unit": "%"}, evidence, ["product"]))
    if recovery_ee is not None:
        rec["outcomes"].append(field("recovered_starting_material_ee", {"number": recovery_ee, "unit": "%"}, evidence, ["allene"]))
    records.append(rec)


assert len(records) == 35, len(records)
RAW.parent.mkdir(parents=True, exist_ok=True)
RAW.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")

ids = {r["source_reaction_id"]: r["record_id"] for r in records}
coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1,
            "state": "attempted",
            "regions": [
                {"region": "right column, Table 1 and footnotes", "finding": "Five independent time/diethylzinc-loading optimization entries extracted; the Fe(acac)3 footnote applies only to entry 1 and all yields retain their NMR/CH2Br2 basis.", "evidence_ids": ev(1)},
                {"region": "lower-right Figure 1", "finding": "ORTEP representation of 2a linked to the table records; not treated as another reaction.", "evidence_ids": ev(1)},
                {"region": "left-column introduction and discussion", "finding": "Narrative versions of Table 1 and Table 2 results were linked contextually; cited prior iron/Grignard work and biological examples were not expanded into present-paper experiments.", "evidence_ids": ev(1)},
            ],
            "record_ids": [ids[f"table1_entry{i}"] for i in range(1, 6)],
            "unresolved": ["Table 1 omits atmosphere, workup, and purification.", "Candidate product structures and stereochemistry remain unverified."],
        },
        {
            "page": 2,
            "state": "attempted",
            "regions": [
                {"region": "upper-left Table 2 and footnote", "finding": "Seven independent solvent-optimization entries extracted, including trace product, starting-material recoveries, and source table dashes.", "evidence_ids": ev(2)},
                {"region": "lower-left Table 3 and footnotes", "finding": "Twelve independent substrate-scope entries extracted; organozinc solution concentrations/carrier solvents and isolated-yield basis were applied row-wise, and entry 8 retains product not formed plus 60% recovered 1a.", "evidence_ids": ev(2)},
                {"region": "upper-right Table 4 and footnotes", "finding": "Eight independent optically active substrate entries extracted with input ee, staged temperature/time programs, isolated yield, and product ee.", "evidence_ids": ev(2)},
                {"region": "lower-right Figure 2", "finding": "ORTEP representation of (−)-(4S,6R)-2c linked to Table 4 entries 7–8; not treated as another reaction.", "evidence_ids": ev(2)},
            ],
            "record_ids": [
                *[ids[f"table2_entry{i}"] for i in range(1, 8)],
                *[ids[f"table3_entry{i}"] for i in range(1, 13)],
                *[ids[f"table4_entry{i}"] for i in range(1, 9)],
            ],
            "unresolved": ["Tables 2–4 omit atmosphere, workup, and purification; most rows also omit exact reaction-scale details.", "Absolute stereochemistry and complex product connectivity remain machine candidates requiring review."],
        },
        {
            "page": 3,
            "state": "attempted",
            "regions": [
                {"region": "left column, Scheme 1 and discussion", "finding": "Proposed stereochemical model retained as a mechanism record, including intermediates 4/5A/5B/6 and the reported NMR Z/E ratio for racemic 7; not classified as a completed synthetic experiment.", "evidence_ids": ev(3)},
                {"region": "upper-right Scheme 2 and adjacent discussion", "finding": "Two distinct mechanistic test experiments extracted with separate reagent loadings, temperature/time programs, NMR yields, recoveries, and ee results.", "evidence_ids": ev(3)},
                {"region": "lower-right experimental synthesis of racemic (Z)-2a", "finding": "Exact quantities, nitrogen atmosphere, addition, TLC monitoring, workup, chromatography, product mass, and 65% isolated yield merged into Table 3 entry 1 rather than duplicated.", "evidence_ids": ev(3)},
            ],
            "record_ids": [ids["scheme1_stereochemical_model"], ids["scheme2_test1_racemic"], ids["scheme2_test2_enantioenriched"], ids["table3_entry1"], ids["table4_entry3"], ids["table4_entry4"]],
            "unresolved": ["Scheme 1 is a proposed pathway and its organozinc intermediates are not structurally verified.", "Scheme 2 omits atmosphere, workup, and purification.", "The analytical characterization of racemic 2a continues onto page 4."],
        },
        {
            "page": 4,
            "state": "attempted",
            "regions": [
                {"region": "upper-left synthesis of (+)-(4R,6S)-(Z)-2a", "finding": "Exact starting-material/reagent quantities, toluene volume, product mass, isolated yield, product ee, and chiral-HPLC details merged into Table 4 entry 2.", "evidence_ids": ev(4)},
                {"region": "remaining page: characterization continuation, dates, keywords, and references", "finding": "No additional present-paper reaction arrow, table row, or independent experimental batch; references and crystallographic data were not converted into reactions.", "evidence_ids": ev(4)},
            ],
            "record_ids": [ids["table3_entry1"], ids["table4_entry2"]],
            "unresolved": ["The enantioenriched 2a paragraph does not state atmosphere, workup, purification, or reaction time independently; its 3 h duration comes from the explicitly corresponding Table 4 row.", "SI is mentioned as available online but was not supplied or explicitly associated."],
        },
    ],
}
COVERAGE.parent.mkdir(parents=True, exist_ok=True)
COVERAGE.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

tasks = json.loads(TASKS.read_text())
for task in tasks:
    if task.get("document_id") == DOC and task.get("task_id", "").split(":")[-1] == "text":
        task["state"] = "attempted"
TASKS.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"records": len(records), "raw": str(RAW), "coverage": str(COVERAGE)}, ensure_ascii=False))
