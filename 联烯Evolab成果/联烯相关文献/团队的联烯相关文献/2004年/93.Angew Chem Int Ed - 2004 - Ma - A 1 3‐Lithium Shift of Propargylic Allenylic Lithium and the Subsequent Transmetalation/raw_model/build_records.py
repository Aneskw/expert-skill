#!/usr/bin/env python3
"""Build the source-linked machine extraction for PDF pages 1--3.

This is a session artifact, not part of the extraction toolchain.  It keeps the
repetitive record construction readable while preserving the emitted JSON as
the raw model output consumed by reaction_tools.py merge.
"""
from __future__ import annotations

import json
from pathlib import Path


DOC = "doc_e7dc25f1447821d4"
HERE = Path(__file__).resolve().parent


def ev(page: int) -> list[str]:
    return [f"{DOC}:page{page}:text", f"{DOC}:page{page}:image"]


def fact(value, evidence=None):
    return {
        "value": value,
        "evidence_ids": list(evidence or []),
        "verification": "missing" if value is None else "unreviewed",
    }


def field(name, value, evidence, targets=None):
    result = {"name": name, "fact": fact(value, evidence)}
    if targets:
        result["target_entity_ids"] = targets
    return result


def participant(entity_id, role, name, evidence, label=None, smiles=None, amounts=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence if label is not None else []),
        "name": fact(name, evidence if name is not None else []),
        "smiles": fact(smiles, evidence if smiles is not None else []),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": amounts or [],
    }


def step(step_id, participant_ids, conditions):
    return {"step_id": step_id, "participant_ids": participant_ids, "conditions": conditions}


def record(suffix, source_id, kind, evidence, participants, steps, outcomes, notes, unresolved):
    return {
        "record_id": f"{DOC}:{suffix}",
        "document_id": DOC,
        "source_reaction_id": source_id,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": evidence,
        "participants": participants,
        "steps": steps,
        "outcomes": outcomes,
        "notes": [fact(x, evidence) for x in notes],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved,
        },
    }


SMILES = {
    "substrate_c2": "CCC#Cc1ccccc1",
    "1a": "CC=C=C(c1ccccc1)c1ccccc1",
    "2a": "CC(=C=Cc1ccccc1)c1ccccc1",
    "iodobenzene": "Ic1ccccc1",
    "zinc_bromide": "[Zn+2].[Br-].[Br-]",
    "thf": "C1CCOC1",
    "tmeda": "CN(C)CCN(C)C",
}


def common_products(evidence, label1="1a", label2="2a", name1=None, name2=None, smiles1=None, smiles2=None):
    return [
        participant("product_1", "product", name1 or "1,1-diphenyl-1,2-butadiene", evidence,
                    label1, smiles1 or SMILES["1a"]),
        participant("product_2", "product", name2 or "1,3-diphenyl-1,2-butadiene", evidence,
                    label2, smiles2 or SMILES["2a"]),
    ]


def base_participant(base, evidence):
    names = {
        "nBuLi": "n-butyllithium",
        "tBuLi": "tert-butyllithium",
        "LDA": "lithium diisopropylamide",
    }
    return participant("base", "reagent", names[base], evidence, base, None)


records = []

# Page 1, Scheme 1: generic chemistry only.  R/Ar variables make complete
# structures unavailable, so no SMILES is fabricated.
e1 = ev(1)
records.append(record(
    "scheme1_general", "Scheme 1", "general_scheme", e1,
    [
        participant("generic_alkyne", "reactant", "1-aryl-1-alkyne (Ar1-C≡C-CH2R)", e1,
                    "Ar1-C≡C-CH2R", None),
        participant("generic_product_1", "product", "1,1-diarylallene", e1, "1", None),
        participant("generic_product_2", "product", "1,3-diarylallene", e1, "2", None),
        participant("zinc_bromide", "reagent", "zinc bromide", e1, "ZnBr2", SMILES["zinc_bromide"]),
        participant("palladium_catalyst", "catalyst", "tetrakis(triphenylphosphine)palladium(0)", e1,
                    "Pd(PPh3)4", None),
        participant("aryl_iodide", "reactant", "aryl iodide", e1, "Ar2I", None),
    ],
    [
        step("lithiation", ["generic_alkyne"], [field("operation", "lithiation", e1)]),
        step("transmetalation", ["zinc_bromide"], [field("operation", "transmetalation", e1)]),
        step("palladium_coupling", ["palladium_catalyst", "aryl_iodide"],
             [field("operation", "Pd-catalyzed coupling", e1)]),
    ],
    [],
    ["Generic protocol and lithium-shift relationship; not counted as a reported experiment."],
    ["Ar1, Ar2, and R are generic variables, so complete molecular structures and quantities are unavailable."],
))


# Page 1, Table 1.  Every populated base/temperature cell is one independent
# optimization entry; dashes are not converted into experiments.
table1_rows = [
    # row, temperature, base, yield, ratio, basis, result
    (1, 8, "nBuLi", None, "1a:2a = 100:0–0:100", None, None),
    (1, 8, "tBuLi", None, "1a:2a = 100:0–0:100", None, None),
    (1, 8, "LDA", 84, "1a:2a = 0:100", "isolated product yield", None),
    (2, -10, "nBuLi", None, "1a:2a = 100:0–0:100", None, None),
    (2, -10, "tBuLi", 54, "1a:2a = 89:11", "1H NMR yield with CH2Br2 internal standard", None),
    (3, -20, "nBuLi", 70, "1a:2a = 100:0", "1H NMR yield with CH2Br2 internal standard", None),
    (3, -20, "tBuLi", 28, "1a:2a = 93:7", "1H NMR yield with CH2Br2 internal standard", None),
    (3, -20, "LDA", 98, "1a:2a = 0:100", "1H NMR yield with CH2Br2 internal standard", None),
    (4, -40, "nBuLi", 54, "1a:2a = 100:0", "1H NMR yield with CH2Br2 internal standard", None),
    (4, -40, "tBuLi", 54, "1a:2a = 100:0", "1H NMR yield with CH2Br2 internal standard", None),
    (4, -40, "LDA", 96, "1a:2a = 19:81", "1H NMR yield with CH2Br2 internal standard", None),
    (5, -55, "LDA", 94, "1a:2a = 45:55", "1H NMR yield with CH2Br2 internal standard", None),
    (6, -65, "LDA", 88, "1a:2a = 77:23", "1H NMR yield with CH2Br2 internal standard", None),
    (7, -78, "nBuLi", None, None, None, "no lithiation"),
    (7, -78, "tBuLi", None, None, None, "no lithiation"),
    (7, -78, "LDA", 50, "1a:2a = 91:9", "1H NMR yield with CH2Br2 internal standard", None),
]

for row, temperature, base, yield_value, ratio, basis, result in table1_rows:
    suffix = f"table1_r{row}_{base.lower()}"
    # Page-2 prose explicitly revisits these Table-1 cells.  Merge that
    # cross-page evidence into the same experiment rather than duplicating it.
    cell_ev = e1 + ev(2) if (row, base) in {
        (3, "nBuLi"), (3, "tBuLi"), (4, "nBuLi"), (4, "tBuLi"), (7, "LDA")
    } else e1
    participants = [
        participant("substrate", "reactant", "1-phenyl-1-butyne", cell_ev, None, SMILES["substrate_c2"]),
        base_participant(base, cell_ev),
    ]
    failed = result == "no lithiation"
    if not failed:
        participants += [
            participant("zinc_bromide", "reagent", "zinc bromide", cell_ev, "ZnBr2", SMILES["zinc_bromide"]),
            participant("iodobenzene", "reactant", "iodobenzene", cell_ev, "PhI", SMILES["iodobenzene"]),
            participant("palladium_catalyst", "catalyst", "tetrakis(triphenylphosphine)palladium(0)", cell_ev,
                        "Pd(PPh3)4", None),
        ] + common_products(cell_ev)
    steps = [step("lithiation", ["substrate", "base"], [
        field("temperature", {"number": temperature, "unit": "°C"}, cell_ev),
        field("time", {"number": 1, "unit": "h"}, cell_ev),
    ])]
    if not failed:
        steps += [
            step("transmetalation", ["zinc_bromide"], [field("time", {"number": 20, "unit": "min"}, cell_ev)]),
            step("palladium_coupling", ["iodobenzene", "palladium_catalyst"], [
                field("temperature", "r.t.", cell_ev), field("time", {"number": 1, "unit": "h"}, cell_ev)
            ]),
        ]
    outcomes = []
    if yield_value is not None:
        outcomes.append(field("yield", {"number": yield_value, "unit": "%"}, cell_ev,
                              ["product_1", "product_2"]))
    else:
        outcomes.append(field("yield", None, [], None))
    if ratio is not None:
        outcomes.append(field("product_ratio", ratio, cell_ev, ["product_1", "product_2"]))
    if basis is not None:
        outcomes.append(field("yield_measurement_basis", basis, cell_ev,
                              ["product_1", "product_2"] if not failed else None))
    if result is not None:
        outcomes.append(field("reaction_result", result, cell_ev))
    unresolved = [
        "Supporting information is mentioned by the paper but was not supplied or explicitly associated.",
        "Participant quantities, solvent, atmosphere, workup, and purification are not stated in Table 1.",
    ]
    if yield_value is None:
        unresolved.append("No numeric yield is reported for this Table 1 condition.")
    if ratio and "–" in ratio:
        unresolved.append("The source reports a variable product-ratio range rather than one reproducible value.")
    records.append(record(
        suffix, f"Table 1 entry {row}, {base}", "optimization_entry", cell_ev,
        participants, steps, outcomes,
        ["Table 1 lithiation temperature is supplied by footnote [a]."], unresolved,
    ))


# Page 2, Scheme 2: four separate room-temperature isomerization times.
e2 = ev(2)
scheme2_rows = [
    ("1h", {"number": 1, "unit": "h"}, {"number": 90, "unit": "%"}, "1a:2a = 29:71", None),
    ("2h", {"number": 2, "unit": "h"}, {"number": 74, "unit": "%"}, "1a:2a = <1:99", None),
    ("5h", {"number": 5, "unit": "h"}, {"number": 10, "unit": "%"}, "1a:2a = 0:100", None),
    ("gt11h", {"number": 11, "unit": "h", "qualifier": "gt", "raw_text": ">11 h"}, None, None,
     "unidentified mixture"),
]
for tag, rt_time, yield_value, ratio, result in scheme2_rows:
    participants = [
        participant("substrate", "reactant", "1-phenyl-1-butyne", e2, None, SMILES["substrate_c2"]),
        base_participant("nBuLi", e2),
        participant("zinc_bromide", "reagent", "zinc bromide", e2, "ZnBr2", SMILES["zinc_bromide"]),
        participant("iodobenzene", "reactant", "iodobenzene", e2, "PhI", SMILES["iodobenzene"]),
        participant("palladium_catalyst", "catalyst", "tetrakis(triphenylphosphine)palladium(0)", e2,
                    "Pd(PPh3)4", None),
    ]
    if result is None:
        participants += common_products(e2)
        targets = ["product_1", "product_2"]
    else:
        participants.append(participant("unidentified_products", "product", "unidentified mixture", e2, None, None))
        targets = ["unidentified_products"]
    outcomes = [field("yield", yield_value, e2, targets)]
    if ratio:
        outcomes.append(field("product_ratio", ratio, e2, targets))
    if yield_value is not None:
        outcomes.append(field("yield_measurement_basis", "1H NMR yield", e2, targets))
    if result:
        outcomes.append(field("reaction_result", result, e2, targets))
    records.append(record(
        f"scheme2_rt_{tag}", f"Scheme 2, x={tag}", "optimization_entry", e2,
        participants,
        [
            step("lithiation", ["substrate", "base"], [
                field("temperature", {"number": -20, "unit": "°C"}, e2),
                field("time", {"number": 1, "unit": "h"}, e2),
            ]),
            step("room_temperature_isomerization", [], [
                field("temperature", "r.t.", e2), field("time", rt_time, e2)
            ]),
            step("transmetalation", ["zinc_bromide"], [
                field("temperature", "r.t.", e2), field("time", {"number": 20, "unit": "min"}, e2)
            ]),
            step("palladium_coupling", ["iodobenzene", "palladium_catalyst"], [
                field("temperature", "r.t.", e2), field("time", {"number": 2, "unit": "h"}, e2)
            ]),
        ], outcomes,
        ["Scheme 2 varies the room-temperature interval x before transmetalation."],
        [
            "Supporting information is mentioned by the paper but was not supplied or explicitly associated.",
            "Participant quantities, solvent, atmosphere, workup, and purification are not reported in Scheme 2.",
        ] + (["Numeric yield and product identities are not reported for the >11 h unidentified mixture."] if result else []),
    ))


# Page 2, Scheme 3: TMEDA-promoted lithium shift.
records.append(record(
    "scheme3_tmeda", "Scheme 3", "reported_experiment", e2,
    [
        participant("substrate", "reactant", "1-phenyl-1-butyne", e2, None, SMILES["substrate_c2"]),
        base_participant("nBuLi", e2),
        participant("tmeda", "reagent", "N,N,N′,N′-tetramethylethylenediamine", e2, "TMEDA", SMILES["tmeda"]),
        participant("zinc_bromide", "reagent", "zinc bromide", e2, "ZnBr2", SMILES["zinc_bromide"]),
        participant("iodobenzene", "reactant", "iodobenzene", e2, "PhI", SMILES["iodobenzene"]),
        participant("palladium_catalyst", "catalyst", "tetrakis(triphenylphosphine)palladium(0)", e2,
                    "Pd(PPh3)4", None),
        participant("product_2", "product", "1,3-diphenyl-1,2-butadiene", e2, "2a", SMILES["2a"]),
    ],
    [
        step("lithiation", ["substrate", "base"], [
            field("temperature", {"number": -20, "unit": "°C"}, e2),
            field("time", {"number": 1, "unit": "h"}, e2),
        ]),
        step("tmeda_addition", ["tmeda"], [
            field("temperature", {"number": -20, "unit": "°C"}, e2),
            field("time", {"number": 1, "unit": "h"}, e2),
        ]),
        step("transmetalation", ["zinc_bromide"], [
            field("temperature", {"number": -20, "unit": "°C"}, e2),
            field("time", {"number": 10, "unit": "min"}, e2),
        ]),
        step("warm_to_room_temperature", [], [
            field("temperature", "r.t.", e2), field("time", {"number": 20, "unit": "min"}, e2)
        ]),
        step("palladium_coupling", ["iodobenzene", "palladium_catalyst"], [
            field("temperature", "r.t.", e2), field("time", {"number": 2, "unit": "h"}, e2)
        ]),
    ],
    [
        field("yield", {"number": 94, "unit": "%"}, e2, ["product_2"]),
        field("yield_measurement_basis", "1H NMR yield", e2, ["product_2"]),
    ],
    ["The prose identifies the product as the isomerized allene 2a."],
    [
        "Supporting information is mentioned by the paper but was not supplied or explicitly associated.",
        "Participant quantities, solvent, atmosphere, workup, and purification are not reported in Scheme 3.",
    ],
))


# Table 2 structures.  These are evidence-linked candidate structures only;
# merge will retain structure_verified=false.
aryl_fragments = {
    "Ph": ("phenyl", "c1ccccc1"),
    "p-PhC6H4": ("4-biphenylyl", "c1ccc(-c2ccccc2)cc1"),
}
aryl_iodides = {
    "C6H5I": ("iodobenzene", "Ic1ccccc1", "phenyl", "c1ccccc1"),
    "p-MeC6H4I": ("4-iodotoluene", "Cc1ccc(I)cc1", "4-methylphenyl", "c1ccc(C)cc1"),
    "α-C10H7I": ("1-iodonaphthalene", "Ic1cccc2ccccc12", "1-naphthyl", "c1cccc2ccccc12"),
    "p-MeOC6H4I": ("4-iodoanisole", "COc1ccc(I)cc1", "4-methoxyphenyl", "c1ccc(OC)cc1"),
    "p-MeO2CC6H4I": ("methyl 4-iodobenzoate", "COC(=O)c1ccc(I)cc1", "4-(methoxycarbonyl)phenyl",
                      "c1ccc(C(=O)OC)cc1"),
}
chain_data = {
    "C2H5": ("ethyl", "CCC#C", "CC=C=C", "CC"),
    "C4H9": ("n-butyl", "CCCCC#C", "CCCC=C=C", "CCCC"),
    "C3H7": ("n-propyl", "CCCC#C", "CCC=C=C", "CCC"),
}


def scope_smiles(ar1_key, chain_key, ar2_key):
    ar1 = aryl_fragments[ar1_key][1]
    ar2 = aryl_iodides[ar2_key][3]
    alkyne_prefix, product1_prefix, product2_prefix = chain_data[chain_key][1:]
    substrate = f"{alkyne_prefix}{ar1}"
    product1 = f"{product1_prefix}({ar1}){ar2}"
    product2 = f"{product2_prefix}(=C=C{ar1}){ar2}"
    return substrate, product1, product2


table2_rows = [
    (1, "Ph", "C2H5", "C6H5I", "nBuLi", -20, 55, "1a", "2a", "100:0", "isolated product yield"),
    (2, "Ph", "C2H5", "C6H5I", "LDA", 8, 84, "1a", "2a", "0:100", "isolated product yield"),
    (3, "Ph", "C4H9", "C6H5I", "nBuLi", -20, 71, "1b", "2b", "99:1", "isolated product yield"),
    (4, "Ph", "C4H9", "C6H5I", "LDA", 10, 89, "1b", "2b", "0:100", "isolated product yield"),
    (5, "Ph", "C4H9", "p-MeC6H4I", "nBuLi", -20, 79, "1c", "2c", "99:1", "isolated product yield"),
    (6, "Ph", "C4H9", "p-MeC6H4I", "LDA", 20, 99, "1c", "2c", "0:100", "isolated product yield"),
    (7, "Ph", "C4H9", "α-C10H7I", "nBuLi", -20, 63, "1d", "2d", "100:0", "isolated product yield"),
    (8, "Ph", "C4H9", "α-C10H7I", "LDA", 20, 56, "1d", "2d", "0:100", "isolated product yield"),
    (9, "Ph", "C4H9", "p-MeOC6H4I", "nBuLi", -20, 74, "1e", "2e", "98:2", "isolated product yield"),
    (10, "Ph", "C4H9", "p-MeOC6H4I", "LDA", 30, 83, "1e", "2e", "0:100", "isolated product yield"),
    (11, "Ph", "C4H9", "p-MeO2CC6H4I", "nBuLi", -20, 93, "1f", "2f", "100:0", "isolated product yield"),
    (12, "Ph", "C4H9", "p-MeO2CC6H4I", "LDA", 19, 71, "1f", "2f", "0:100", "isolated product yield"),
    (13, "Ph", "C3H7", "C6H5I", "nBuLi", -20, 76, "1g", "2g", "100:0", "isolated product yield"),
    (14, "Ph", "C3H7", "C6H5I", "LDA", 11, 96, "1g", "2g", "0:100",
     "1H NMR yield with CH2Br2 internal standard"),
    (15, "p-PhC6H4", "C3H7", "C6H5I", "nBuLi", -20, 77, "1h", "2h", "100:0", "isolated product yield"),
    (16, "p-PhC6H4", "C3H7", "C6H5I", "LDA", 18, 72, "1h", "2h", "0:100", "isolated product yield"),
]


def amount(name, number, unit, evidence):
    return field(name, {"number": number, "unit": unit}, evidence)


for row, ar1_key, chain_key, ar2_key, base, temperature, yield_value, label1, label2, ratio, basis in table2_rows:
    detailed = row in (1, 2)
    evidence = e2 + (ev(3) if detailed else [])
    substrate_smiles, product1_smiles, product2_smiles = scope_smiles(ar1_key, chain_key, ar2_key)
    ar1_name = aryl_fragments[ar1_key][0]
    chain_name = chain_data[chain_key][0]
    halide_name, halide_smiles, ar2_name, _ = aryl_iodides[ar2_key]
    substrate_name = f"1-({ar1_name})-1-alkyne bearing {chain_name} at the other alkyne terminus"
    product1_name = f"1,1-diarylallene ({ar1_name}/{ar2_name}; {chain_key} series)"
    product2_name = f"1,3-diarylallene ({ar1_name}/{ar2_name}; {chain_key} series)"
    participants = [
        participant("substrate", "reactant", substrate_name, evidence, f"Ar1={ar1_key}, CH2R={chain_key}",
                    substrate_smiles),
        base_participant(base, evidence),
        participant("zinc_bromide", "reagent", "zinc bromide", evidence, "ZnBr2", SMILES["zinc_bromide"]),
        participant("aryl_iodide", "reactant", halide_name, evidence, ar2_key, halide_smiles),
        participant("palladium_catalyst", "catalyst", "tetrakis(triphenylphosphine)palladium(0)", evidence,
                    "Pd(PPh3)4", None),
        participant("product_1", "product", product1_name, evidence, label1, product1_smiles),
        participant("product_2", "product", product2_name, evidence, label2, product2_smiles),
    ]
    if detailed:
        e3 = ev(3)
        # The detailed amounts are source-specific and differ between A and B.
        if row == 1:
            participants[0]["amounts"] = [amount("mass", 78, "mg", e2), amount("amount", 0.6, "mmol", e2)]
            participants[1]["amounts"] = [amount("volume", 0.45, "mL", e2),
                                           amount("concentration", 1.6, "M", e2),
                                           amount("amount", 0.72, "mmol", e2)]
            participants[2]["amounts"] = [amount("mass", 275, "mg", e2), amount("amount", 1.2, "mmol", e2)]
            participants[3]["amounts"] = [amount("volume", 83, "uL", e2), amount("amount", 0.72, "mmol", e2)]
            participants[4]["amounts"] = [amount("mass", 35, "mg", e2), amount("catalyst_loading", 5, "mol%", e2)]
            participants[5]["amounts"] = [amount("isolated_mass", 68, "mg", e3)]
        else:
            participants[0]["amounts"] = [amount("mass", 58, "mg", e3), amount("amount", 0.45, "mmol", e3)]
            participants[1]["amounts"] = [amount("volume", 0.4, "mL", e3),
                                           amount("concentration", 2.0, "M", e3),
                                           amount("amount", 0.8, "mmol", e3)]
            participants[2]["amounts"] = [amount("mass", 499, "mg", e3), amount("amount", 2.22, "mmol", e3)]
            participants[3]["amounts"] = [amount("volume", 42, "uL", e3), amount("amount", 0.38, "mmol", e3)]
            participants[4]["amounts"] = [amount("mass", 22, "mg", e3), amount("catalyst_loading", 5, "mol%", e3)]
            participants[6]["amounts"] = [amount("isolated_mass", 65, "mg", e3)]
        participants += [
            participant("thf", "solvent", "tetrahydrofuran", evidence, "THF", SMILES["thf"], [
                amount("initial_solution_volume", 3, "mL", e2 if row == 1 else e3),
                amount("transmetalation_solution_volume", 4, "mL", e2 if row == 1 else e3),
            ]),
            participant("nitrogen", "unspecified_agent", "nitrogen", evidence, "N2", "N#N"),
            participant("ammonium_chloride", "reagent", "saturated ammonium chloride", e3, "sat. NH4Cl", None),
            participant("ether", "solvent", "ether", e3, None, None),
            participant("magnesium_sulfate", "reagent", "magnesium sulfate", e3, "MgSO4", None),
            participant("petroleum_ether", "solvent", "petroleum ether", e3, None, None),
        ]
    lithiation_conditions = [
        field("temperature", {"number": temperature, "unit": "°C"}, evidence),
        field("time", {"number": 1, "unit": "h"}, evidence),
    ]
    if detailed:
        lithiation_conditions.append(field("atmosphere", "N2", evidence))
        lithiation_conditions.append(field("solvent", "THF", evidence))
    steps = [step("lithiation", ["substrate", "base"] + (["thf", "nitrogen"] if detailed else []),
                  lithiation_conditions)]
    if row == 1:
        steps += [
            step("zinc_bromide_addition", ["zinc_bromide", "thf"], [
                field("temperature", {"number": -20, "unit": "°C"}, e2),
                field("time", {"number": 10, "unit": "min"}, e2),
            ]),
            step("warm_to_room_temperature", [], [
                field("temperature", "r.t.", e2), field("time", {"number": 20, "unit": "min"}, e2)
            ]),
            step("palladium_coupling", ["aryl_iodide", "palladium_catalyst"], [
                field("temperature", "r.t.", e2), field("time", None, []),
                field("operation", "stirred until reaction complete by TLC", ev(3)),
            ]),
        ]
    elif row == 2:
        steps += [
            step("zinc_bromide_addition", ["zinc_bromide", "thf"], [
                field("temperature", {"number": temperature, "unit": "°C"}, ev(3)),
                field("time", {"number": 25, "unit": "min"}, ev(3)),
            ]),
            step("palladium_coupling", ["aryl_iodide", "palladium_catalyst"], [
                field("temperature", "r.t.", ev(3)), field("time", None, []),
                field("operation", "stirred until reaction complete by TLC", ev(3)),
            ]),
        ]
    else:
        steps += [
            step("transmetalation", ["zinc_bromide"], [field("operation", "ZnBr2 transmetalation", e2)]),
            step("palladium_coupling", ["aryl_iodide", "palladium_catalyst"], [
                field("temperature", "r.t.", e2), field("operation", "Pd-catalyzed coupling", e2)
            ]),
        ]
    if detailed:
        steps.append(step("workup_and_purification",
                          ["ammonium_chloride", "ether", "magnesium_sulfate", "petroleum_ether"], [
                              field("workup", "quenched with saturated NH4Cl; extracted with ether; dried over MgSO4; solvent removed by rotary evaporation", ev(3)),
                              field("purification", "flash chromatography on silica gel (petroleum ether)", ev(3)),
                          ]))
    outcomes = [
        field("yield", {"number": yield_value, "unit": "%"}, evidence, ["product_1", "product_2"]),
        field("yield_measurement_basis", basis, evidence, ["product_1", "product_2"]),
        field("product_ratio", f"{label1}:{label2} = {ratio}", e2, ["product_1", "product_2"]),
        field("ratio_measurement_basis", "300 MHz 1H NMR analysis", e2, ["product_1", "product_2"]),
    ]
    unresolved = [
        "Supporting information is mentioned by the paper but was not supplied or explicitly associated.",
        "Candidate SMILES were generated from the fully specified table substituents but remain structure-unverified.",
    ]
    if detailed:
        unresolved.append("Coupling duration is reported only as completion by TLC, not as a numeric time.")
    else:
        unresolved.append("Exact participant quantities, solvent, atmosphere, workup, purification, and stage durations are not given for this scope row in the main text.")
    notes = ["Table 2 footnote [a] assigns isolated-product yield except footnote [b] for entry 14; ratios are from 300 MHz 1H NMR analysis."]
    if row == 2:
        notes.append("The detailed condition-B paragraph says 'afford 1b', while Table 2 entry 2 and the reported structure/ratio identify the 84% product as 2a; the discrepancy is retained for review.")
        unresolved.append("Source-label discrepancy in condition B: prose '1b' versus Table 2/structure '2a'.")
    records.append(record(
        f"table2_entry_{row:02d}", f"Table 2 entry {row}", "substrate_scope_entry", evidence,
        participants, steps, outcomes, notes, unresolved,
    ))


out = HERE / "pages_0001_0003_records.json"
out.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"output": str(out), "records": len(records)}, ensure_ascii=False))
