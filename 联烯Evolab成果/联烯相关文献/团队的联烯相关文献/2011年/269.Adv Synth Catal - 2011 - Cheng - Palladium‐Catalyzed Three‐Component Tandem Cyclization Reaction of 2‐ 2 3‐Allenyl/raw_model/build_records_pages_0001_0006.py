#!/usr/bin/env python3
"""Build machine reaction records for Cheng et al., PDF pages 1--6."""

import json
from pathlib import Path


DOC = "doc_866de1af6b261b5a"
ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).with_name("records_pages_0001_0006.json")


def evidence(page):
    return [f"{DOC}:page{page}:image", f"{DOC}:page{page}:text"]


def unique(items):
    return list(dict.fromkeys(items))


def fact(value, ev=None):
    return {
        "value": value,
        "evidence_ids": [] if value is None else list(ev or []),
        "verification": "missing" if value is None else "unreviewed",
    }


def field(name, value, ev=None, targets=None):
    item = {"name": name, "fact": fact(value, ev)}
    if targets:
        item["target_entity_ids"] = list(targets)
    return item


def participant(entity_id, role, label, ev, name=None, smiles=None, amounts=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, ev),
        "name": fact(name, ev) if name else fact(None),
        "smiles": fact(smiles, ev) if smiles else fact(None),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": [field(n, v, ev) for n, v in (amounts or [])],
    }


def step(step_id, participant_ids, ev, *, temperature=None, time=None,
         solvent=None, extra=None, missing_operations=True):
    conditions = []
    if solvent is not None:
        conditions.append(field("solvent", solvent, ev))
    conditions.append(field("temperature", temperature, ev) if temperature is not None else field("temperature", None))
    conditions.append(field("time", time, ev) if time is not None else field("time", None))
    conditions.extend(extra or [])
    if missing_operations:
        conditions.extend([
            field("atmosphere", None),
            field("workup", None),
            field("purification", None),
        ])
    return {"step_id": step_id, "participant_ids": participant_ids, "conditions": conditions}


def record(suffix, kind, ev, participants=None, steps=None, outcomes=None,
           notes=None, unresolved=None):
    return {
        "record_id": f"{DOC}:{suffix}",
        "document_id": DOC,
        "source_reaction_id": suffix,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": unique(ev),
        "participants": participants or [],
        "steps": steps or [],
        "outcomes": outcomes or [],
        "notes": [fact(x, ev) for x in (notes or [])],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved or [
                "Supporting Information was mentioned but not supplied or explicitly associated.",
                "Machine-extracted structures and reaction semantics require source review.",
            ],
        },
    }


SMILES = {
    "1a": "C=C=CCC(C(=O)C)C(=O)OCC",
    "2a": "COc1ccc(N)cc1",
    "PhI": "Ic1ccccc1",
    "TsOH.H2O": "Cc1ccc(S(=O)(=O)O)cc1.O",
    "toluene": "Cc1ccccc1",
    "MgSO4": "[Mg+2].[O-]S(=O)(=O)[O-]",
    "TfOH": "OS(=O)(=O)C(F)(F)F",
    "TFA": "O=C(O)C(F)(F)F",
    "AcOH": "CC(=O)O",
}


def common_participants(ev, *, amine_label="2a", amine_name="4-methoxyaniline",
                        amine_smiles=SMILES["2a"], amine_eq=None,
                        halide_label="3a", halide_name="iodobenzene",
                        halide_smiles=SMILES["PhI"], halide_eq=None,
                        acid_label="p-TsOH.H2O", acid_name="p-toluenesulfonic acid monohydrate",
                        acid_smiles=SMILES["TsOH.H2O"], acid_loading=None,
                        solvent_label="toluene", solvent_name="toluene",
                        solvent_smiles=SMILES["toluene"], include_product=True,
                        product_label="4aa"):
    parts = [
        participant("substrate_1a", "reactant", "1a", ev,
                    "ethyl 2-(2,3-allenyl)acetylacetate", SMILES["1a"]),
        participant("amine", "reactant", amine_label, ev, amine_name, amine_smiles,
                    [("equivalents", {"number": amine_eq, "unit": "equiv"})] if amine_eq is not None else []),
        participant("pd_catalyst", "catalyst", "Pd(PPh3)4", ev,
                    "tetrakis(triphenylphosphine)palladium(0)", None,
                    [("catalyst_loading", {"number": 5, "unit": "mol%"})]),
    ]
    if halide_label:
        parts.append(participant("organic_halide", "reactant", halide_label, ev,
                                 halide_name, halide_smiles,
                                 [("equivalents", {"number": halide_eq, "unit": "equiv"})] if halide_eq is not None else []))
    if acid_label:
        parts.append(participant("bronsted_acid", "reagent", acid_label, ev,
                                 acid_name, acid_smiles,
                                 [("acid_loading", {"number": acid_loading, "unit": "mol%"})] if acid_loading is not None else []))
    if solvent_label:
        parts.append(participant("solvent", "solvent", solvent_label, ev,
                                 solvent_name, solvent_smiles))
    if include_product:
        parts.append(participant("product", "product", product_label, ev))
    return parts


def isolated_yield(value, ev, target="product"):
    return [
        field("isolated_yield", {"number": value, "unit": "%"}, ev, [target]),
        field("yield_measurement_basis", "isolated product", ev, [target]),
    ]


records = []

# Page 1: a conceptual, generic scheme rather than an individual batch experiment.
ev1 = evidence(1)
records.append(record(
    "scheme1_general_transformation", "general_scheme", ev1,
    notes=[
        "Scheme 1 proposes generic paths from beta-keto ester allene 1 to dihydrofuran products and to 4,5-dihydro-1H-pyrroles 4 through imine/enamine intermediates 7a/7b.",
        "R-group structures and arrows are generic; no individual yield or batch conditions are reported in this scheme.",
    ],
    unresolved=["Generic R groups prevent assignment of complete individual structures."],
))

# The same 72% reference experiment is repeated in Tables 1--4 and detailed on page 6.
ev2, ev3, ev4, ev6 = evidence(2), evidence(3), evidence(4), evidence(6)
standard_ev = unique(ev2 + ev3 + ev4 + ev6)
standard_parts = common_participants(ev6, amine_eq=3, halide_eq=2, acid_loading=20)
byid = {p["entity_id"]: p for p in standard_parts}
byid["substrate_1a"]["amounts"] = [
    field("mass", {"number": 42, "unit": "mg"}, ev6),
    field("amount", {"number": 0.23, "unit": "mmol"}, ev6),
    field("equivalents", {"number": 1, "unit": "equiv"}, ev2),
]
byid["amine"]["amounts"].extend([
    field("mass", {"number": 94, "unit": "mg"}, ev6),
    field("amount", {"number": 0.76, "unit": "mmol"}, ev6),
])
byid["pd_catalyst"]["amounts"].extend([
    field("mass", {"number": 14, "unit": "mg"}, ev6),
    field("amount", {"number": 0.0125, "unit": "mmol"}, ev6),
])
byid["organic_halide"]["amounts"].extend([
    field("mass", {"number": 107, "unit": "mg"}, ev6),
    field("amount", {"number": 0.52, "unit": "mmol"}, ev6),
])
byid["bronsted_acid"]["amounts"].extend([
    field("mass", {"number": 11, "unit": "mg"}, ev6),
    field("amount", {"number": 0.06, "unit": "mmol"}, ev6),
])
byid["solvent"]["amounts"] = [field("volume", {"number": 2, "unit": "mL"}, ev6)]
standard_step = {
    "step_id": "one_pot_cyclization",
    "participant_ids": [p["entity_id"] for p in standard_parts],
    "conditions": [
        field("operation", "flame-dried Schlenk tube; mixture stirred", ev6),
        field("atmosphere", "argon", ev6),
        field("solvent", "toluene", ev6),
        field("temperature", {"number": 90, "unit": "°C"}, ev6),
        field("time", {"number": 10, "unit": "h"}, ev6),
        field("reaction_monitoring", "TLC; petroleum ether/ethyl acetate = 15:1", ev6),
        field("workup", "reaction mixture evaporated", ev6),
        field("purification", "flash chromatography on silica gel; petroleum ether/ethyl acetate = 20:1", ev6),
    ],
}
standard_outcomes = isolated_yield(72, ev6)
standard_outcomes.extend([
    field("product_mass", {"number": 60, "unit": "mg"}, ev6, ["product"]),
    field("product_state", "liquid", ev6, ["product"]),
])
records.append(record(
    "standard_4aa", "optimization_entry", standard_ev,
    standard_parts, [standard_step], standard_outcomes,
    notes=["This single experiment is repeated as Table 1 entry 4, Table 2 entry 5, Table 3 entry 1, Table 4 entry 1, and the Typical Procedure."],
    unresolved=[
        "The source product drawing and candidate substrate SMILES remain machine-unverified.",
        "Supporting Information was mentioned but not supplied or explicitly associated.",
    ],
))

# Page 2, Table 1: amine loading and Bronsted-acid optimization (entry 4 is standard_4aa).
table1 = {
    1: (1, "p-TsOH.H2O", 16, 27),
    2: (0.6, "p-TsOH.H2O", 9, 22),
    3: (2, "p-TsOH.H2O", 16, 52),
    5: (3, "p-TsOH.H2O", 8, 56),
    6: (4, "p-TsOH.H2O", 10, 60),
    7: (5, "p-TsOH.H2O", 5, 63),
    8: (3, None, 10, 50),
    9: (3, "TfOH", 10, 56),
    10: (3, "TFA", 6, 54),
    11: (3, "AcOH", 8, 53),
}
acid_names = {
    "p-TsOH.H2O": "p-toluenesulfonic acid monohydrate",
    "TfOH": "trifluoromethanesulfonic acid",
    "TFA": "trifluoroacetic acid",
    "AcOH": "acetic acid",
}
for entry, (amine_eq, acid, hours, yld) in table1.items():
    parts = common_participants(
        ev2, amine_eq=amine_eq, halide_eq=2,
        acid_label=acid, acid_name=acid_names.get(acid), acid_smiles=SMILES.get(acid),
        acid_loading=20 if acid else None,
    )
    if entry == 5:
        parts.append(participant(
            "magnesium_sulfate", "reagent", "anhydrous MgSO4", ev2,
            "anhydrous magnesium sulfate", SMILES["MgSO4"],
            [("equivalents", {"number": 1.0, "unit": "equiv"})],
        ))
    participant_ids = [p["entity_id"] for p in parts if p["role"] != "product"]
    conditions = [field("solvent", "toluene", ev2), field("temperature", {"number": 90, "unit": "°C"}, ev2)]
    conditions.append(field("time", {"number": hours, "unit": "h"}, ev2))
    conditions.extend([field("atmosphere", None), field("workup", None), field("purification", None)])
    notes = []
    if entry == 8:
        notes.append("The Bronsted-acid column contains a dash; no acid participant is assigned and the dash is not converted to zero.")
    records.append(record(
        f"table1_entry{entry}", "optimization_entry", ev2,
        parts, [{"step_id": "cyclization", "participant_ids": participant_ids, "conditions": conditions}],
        isolated_yield(yld, ev2), notes=notes,
    ))

# Page 2, Table 2: solvent optimization (entry 5 is standard_4aa).
table2 = {
    1: ("MeNO2", "nitromethane", "C[N+](=O)[O-]", "reflux", 7, "complicated"),
    2: ("DMF", "N,N-dimethylformamide", "CN(C)C=O", {"number": 90, "unit": "°C"}, 8, 57),
    3: ("DCE", "1,2-dichloroethane", "ClCCCl", "reflux", 7, 64),
    4: ("DME", "1,2-dimethoxyethane", "COCCOC", "reflux", 8, 65),
    6: ("PhCl", "chlorobenzene", "Clc1ccccc1", {"number": 90, "unit": "°C"}, 8, 73),
}
for entry, (solv_label, solv_name, solv_smiles, temp, hours, result) in table2.items():
    parts = common_participants(
        ev2, amine_eq=3, halide_eq=2, acid_loading=20,
        solvent_label=solv_label, solvent_name=solv_name, solvent_smiles=solv_smiles,
    )
    outcomes = ([field("reaction_result", "complicated", ev2)] if result == "complicated" else isolated_yield(result, ev2))
    records.append(record(
        f"table2_entry{entry}", "optimization_entry", ev2,
        parts,
        [step("cyclization", [p["entity_id"] for p in parts if p["role"] != "product"], ev2,
              temperature=temp, time={"number": hours, "unit": "h"}, solvent=solv_label)],
        outcomes,
        unresolved=[
            "Exact reagent masses, solvent volume, atmosphere, workup, and purification are not stated for this table row.",
            "The product structure remains machine-unverified." if result != "complicated" else "The components of the complicated mixture are not identified.",
        ],
    ))

# Page 3, Table 3: amine scope (entry 1 is standard_4aa).
amine_rows = {
    2: ("2b", "p-toluidine", "Cc1ccc(N)cc1", 10, 60, "4ab"),
    3: ("2c", "aniline", "Nc1ccccc1", 8, 64, "4ac"),
    4: ("2d", "4-methoxybenzylamine", "COc1ccc(CN)cc1", 6, 69, "4ad"),
    5: ("2e", "benzylamine", "NCc1ccccc1", 8, 67, "4ae"),
    6: ("2f", "n-butylamine", "CCCCN", 9, 38, "4af"),
    7: ("2g", "allylamine", "C=CCN", 10, 42, "4ag"),
}
for entry, (amine_label, amine_name, amine_smiles, hours, yld, product_label) in amine_rows.items():
    parts = common_participants(
        ev3, amine_label=amine_label, amine_name=amine_name, amine_smiles=amine_smiles,
        amine_eq=3, halide_eq=2, acid_loading=20, product_label=product_label,
    )
    outcomes = isolated_yield(yld, ev3)
    notes = []
    if entry == 2:
        notes.append("The text states that 4ab decomposed easily after silica-gel chromatography.")
    if entry == 7:
        parts.append(participant("secondary_product", "product", "5a", ev3))
        outcomes.append(field("reported_secondary_product_yield", {"number": 34, "unit": "%"}, ev3, ["secondary_product"]))
        notes.append("Footnote b states that 34% of 5a was also discovered; its yield basis is not separately stated.")
    records.append(record(
        f"table3_entry{entry}", "substrate_scope_entry", ev3,
        parts,
        [step("cyclization", [p["entity_id"] for p in parts if p["role"] not in ("product",)], ev3,
              temperature={"number": 90, "unit": "°C"}, time={"number": hours, "unit": "h"}, solvent="toluene")],
        outcomes, notes=notes,
    ))

# Scheme 2 spans page 3 structures and page 4 discussion/NOE context.
scheme2_ev = unique(ev3 + ev4)
scheme2_rows = [
    ("1b", "6a", 3.04, 2.0, 46, 58, None),
    ("1c", "6b", 3.13, 2.13, 16, 52, "single trans diastereomer; relative configuration supported by NOE"),
    ("1d", "6c", 3.04, 2.0, 18, 51, "single trans diastereomer"),
]
for substrate_label, product_label, amine_eq, phi_eq, hours, yld, selectivity in scheme2_rows:
    parts = [
        participant("substrate", "reactant", substrate_label, ev3),
        participant("amine", "reactant", "2a", ev3, "4-methoxyaniline", SMILES["2a"], [("equivalents", {"number": amine_eq, "unit": "equiv"})]),
        participant("pd_catalyst", "catalyst", "Pd(PPh3)4", ev3, "tetrakis(triphenylphosphine)palladium(0)", None, [("catalyst_loading", {"number": 5, "unit": "mol%"})]),
        participant("organic_halide", "reactant", "PhI", ev3, "iodobenzene", SMILES["PhI"], [("equivalents", {"number": phi_eq, "unit": "equiv"})]),
        participant("bronsted_acid", "reagent", "p-TsOH.H2O", ev3, "p-toluenesulfonic acid monohydrate", SMILES["TsOH.H2O"], [("acid_loading", {"number": 20, "unit": "mol%"})]),
        participant("solvent", "solvent", "toluene", ev3, "toluene", SMILES["toluene"]),
        participant("product", "product", product_label, ev3),
    ]
    outcomes = isolated_yield(yld, ev3)
    if selectivity:
        outcomes.append(field("diastereoselectivity", selectivity, scheme2_ev, ["product"]))
    records.append(record(
        f"scheme2_{substrate_label}_to_{product_label}", "substrate_scope_entry", scheme2_ev,
        parts,
        [step("cyclization", [p["entity_id"] for p in parts if p["role"] != "product"], ev3,
              temperature={"number": 90, "unit": "°C"}, time={"number": hours, "unit": "h"}, solvent="toluene")],
        outcomes,
        unresolved=[
            "Exact scale, solvent volume, atmosphere, workup, and purification are not reported in Scheme 2.",
            "The depicted substrate/product structures and stereochemistry remain machine-unverified.",
        ],
    ))

# Page 4, Scheme 3: chiral amine and substrate-without-ethoxycarbonyl controls.
parts = [
    participant("substrate_1a", "reactant", "1a", ev4, "ethyl 2-(2,3-allenyl)acetylacetate", SMILES["1a"]),
    participant("amine", "reactant", "S-2h", ev4, "(S)-(-)-alpha-phenylethylamine", "C[C@H](N)c1ccccc1", [("equivalents", {"number": 3.13, "unit": "equiv"})]),
    participant("pd_catalyst", "catalyst", "Pd(PPh3)4", ev4, None, None, [("catalyst_loading", {"number": 5, "unit": "mol%"})]),
    participant("organic_halide", "reactant", "PhI", ev4, "iodobenzene", SMILES["PhI"], [("equivalents", {"number": 2.13, "unit": "equiv"})]),
    participant("bronsted_acid", "reagent", "p-TsOH.H2O", ev4, None, SMILES["TsOH.H2O"], [("acid_loading", {"number": 21, "unit": "mol%"})]),
    participant("solvent", "solvent", "toluene", ev4, "toluene", SMILES["toluene"]),
    participant("product", "product", "6d", ev4),
]
outcomes = isolated_yield(69, ev4)
outcomes.append(field("diastereomer_ratio", "1.3:1", ev4, ["product"]))
records.append(record(
    "scheme3_chiral_amine_6d", "substrate_scope_entry", ev4,
    parts,
    [step("cyclization", [p["entity_id"] for p in parts if p["role"] != "product"], ev4,
          temperature={"number": 90, "unit": "°C"}, time={"number": 10, "unit": "h"}, solvent="toluene")],
    outcomes,
))

scheme3_fail_ev = unique(ev4 + evidence(5))
parts = [
    participant("substrate", "reactant", "1e", ev4, "allene substrate without an ethoxycarbonyl moiety"),
    participant("amine", "reactant", "2a", ev4, "4-methoxyaniline", SMILES["2a"], [("equivalents", {"number": 2.92, "unit": "equiv"})]),
    participant("pd_catalyst", "catalyst", "Pd(PPh3)4", ev4, None, None, [("catalyst_loading", {"number": 5, "unit": "mol%"})]),
    participant("organic_halide", "reactant", "PhI", ev4, "iodobenzene", SMILES["PhI"], [("equivalents", {"number": 1.92, "unit": "equiv"})]),
    participant("bronsted_acid", "reagent", "p-TsOH.H2O", ev4, None, SMILES["TsOH.H2O"], [("acid_loading", {"number": 19, "unit": "mol%"})]),
    participant("solvent", "solvent", "toluene", ev4, "toluene", SMILES["toluene"]),
]
records.append(record(
    "scheme3_substrate_1e_complicated", "substrate_scope_entry", scheme3_fail_ev,
    parts,
    [step("cyclization", [p["entity_id"] for p in parts], ev4,
          temperature={"number": 90, "unit": "°C"}, time={"number": 10, "unit": "h"}, solvent="toluene")],
    [field("reaction_result", "complicated / unidentified mixture", scheme3_fail_ev)],
    notes=["The text states that the ethoxycarbonyl moiety appears necessary for the reaction."],
    unresolved=["The mixture components and any product yields are not identified."],
))

# Page 4, Table 4: organic iodide scope (entry 1 is standard_4aa).
halide_rows = {
    2: ("3b", "p-MeC6H4I", "1-iodo-4-methylbenzene", "Cc1ccc(I)cc1", 10, 57, "4ba"),
    3: ("3c", "m-MeC6H4I", "1-iodo-3-methylbenzene", "Cc1cccc(I)c1", 10, 59, "4ca"),
    4: ("3d", "p-MeOC6H4I", "1-iodo-4-methoxybenzene", "COc1ccc(I)cc1", 9, 46, "4da"),
    5: ("3e", "p-MeO2CC6H4I", "methyl 4-iodobenzoate", "COC(=O)c1ccc(I)cc1", 10, 67, "4ea"),
    6: ("3f", "p-BrC6H4I", "1-bromo-4-iodobenzene", "Brc1ccc(I)cc1", 10, 74, "4fa"),
    7: ("3g", "p-FC6H4I", "1-fluoro-4-iodobenzene", "Fc1ccc(I)cc1", 10, 58, "4ga"),
    8: ("3h", "p-PhC6H4I", "4-iodobiphenyl", "Ic1ccc(-c2ccccc2)cc1", 10, 78, "4ha"),
    9: ("3i", "p-(p-BrC6H4)C6H4I", "4-bromo-4'-iodobiphenyl", "Brc1ccc(-c2ccc(I)cc2)cc1", 10, 64, "4ia"),
    10: ("3j", "hex-1(E)-enyl iodide", "(E)-1-iodohex-1-ene", None, 10, 66, "4ja"),
    11: ("3k", "(E)-2-phenylvinyl iodide", "(E)-2-iodovinylbenzene", None, 10, 48, "4ka"),
    12: ("3l", "1-naphthyl iodide", "1-iodonaphthalene", "Ic1cccc2ccccc12", 10, 54, "4la"),
}
for entry, (halide_label, source_r, halide_name, halide_smiles, hours, yld, product_label) in halide_rows.items():
    parts = common_participants(
        ev4, amine_eq=3,
        halide_label=halide_label, halide_name=halide_name, halide_smiles=halide_smiles,
        halide_eq=None, acid_loading=20, product_label=product_label,
    )
    records.append(record(
        f"table4_entry{entry}", "substrate_scope_entry", ev4,
        parts,
        [step("cyclization", [p["entity_id"] for p in parts if p["role"] != "product"], ev4,
              temperature={"number": 90, "unit": "°C"}, time={"number": hours, "unit": "h"}, solvent="toluene")],
        isolated_yield(yld, ev4),
        notes=[f"Table 4 reports R4 as {source_r}."],
        unresolved=[
            "The organic iodide equivalents, exact scale, solvent volume, atmosphere, workup, and purification are not stated in Table 4.",
            "The product structure remains machine-unverified.",
        ],
    ))

# Page 5, Scheme 4: two successive, independently reported transformations.
ev5 = evidence(5)
parts = [
    participant("substrate", "reactant", "4ae", ev5),
    participant("ddq", "reagent", "DDQ", ev5, "2,3-dichloro-5,6-dicyano-1,4-benzoquinone"),
    participant("solvent", "solvent", "toluene", ev5, "toluene", SMILES["toluene"]),
    participant("product", "product", "8", ev5, "N-benzyl pyrrole 8"),
]
records.append(record(
    "scheme4_4ae_to_8", "reported_experiment", ev5,
    parts,
    [step("oxidation", ["substrate", "ddq", "solvent"], ev5,
          temperature="r.t.", time={"number": 0.5, "unit": "h"}, solvent="toluene")],
    isolated_yield(64, ev5),
    unresolved=["Reagent quantities, scale, atmosphere, workup, purification, and product structure are not stated in Scheme 4."],
))

parts = [
    participant("substrate", "reactant", "8", ev5, "N-benzyl pyrrole 8"),
    participant("sodium", "reagent", "Na", ev5, "sodium", "[Na]"),
    participant("ammonia", "reagent", "liquid NH3", ev5, "liquid ammonia", "N"),
    participant("tert_butanol", "reagent", "t-BuOH", ev5, "tert-butanol", "CC(C)(C)O"),
    participant("solvent", "solvent", "THF", ev5, "tetrahydrofuran", "C1CCOC1"),
    participant("product", "product", "9", ev5, "NH pyrrole derivative 9"),
]
records.append(record(
    "scheme4_8_to_9", "reported_experiment", ev5,
    parts,
    [step("benzyl_deprotection", [p["entity_id"] for p in parts if p["role"] != "product"], ev5,
          temperature={"number": -78, "unit": "°C"}, time={"number": 8, "unit": "min"}, solvent="THF")],
    isolated_yield(81, ev5),
    unresolved=["Reagent quantities, scale, atmosphere, workup, purification, and product structure are not stated in Scheme 4."],
))

# Page 5, Scheme 5: three control experiments.
parts = common_participants(ev5, amine_eq=3.26, halide_eq=2.17, acid_loading=22, product_label="4aa")
parts.append(participant("intermediate", "product", "7aa", ev5, "enamine intermediate 7aa"))
outcomes = [
    field("isolated_yield_4aa", {"number": 49, "unit": "%"}, ev5, ["product"]),
    field("isolated_yield_7aa", {"number": 25, "unit": "%"}, ev5, ["intermediate"]),
    field("yield_measurement_basis", "isolated products", ev5, ["product", "intermediate"]),
]
records.append(record(
    "scheme5_intermediate_trapping", "reported_experiment", ev5,
    parts,
    [step("stopped_cyclization", [p["entity_id"] for p in parts if p["role"] != "product"], ev5,
          temperature={"number": 90, "unit": "°C"}, time={"number": 70, "unit": "min"}, solvent="toluene")],
    outcomes,
    notes=["The reaction was stopped after disappearance of allene substrate 1a; enamine 7aa was isolated as mechanistic evidence."],
))

parts = [
    participant("substrate", "reactant", "5a", ev5, "4,5-dihydrofuran derivative 5a"),
    participant("amine", "reactant", "2a", ev5, "4-methoxyaniline", SMILES["2a"], [("equivalents", {"number": 3.06, "unit": "equiv"})]),
    participant("pd_catalyst", "catalyst", "Pd(PPh3)4", ev5, None, None, [("catalyst_loading", {"number": 6, "unit": "mol%"})]),
    participant("bronsted_acid", "reagent", "p-TsOH.H2O", ev5, None, SMILES["TsOH.H2O"], [("acid_loading", {"number": 18, "unit": "mol%"})]),
    participant("solvent", "solvent", "toluene", ev5, "toluene", SMILES["toluene"]),
    participant("product", "product", "4aa", ev5),
]
records.append(record(
    "scheme5_5a_to_4aa", "reported_experiment", ev5,
    parts,
    [step("ring_conversion", [p["entity_id"] for p in parts if p["role"] != "product"], ev5,
          temperature={"number": 90, "unit": "°C"}, time={"number": 10, "unit": "h"}, solvent="toluene")],
    isolated_yield(76, ev5),
))

parts = [
    participant("substrate_1f", "reactant", "1f", ev5, "2-methyl-substituted allene substrate 1f"),
    participant("amine", "reactant", "2a", ev5, "4-methoxyaniline", SMILES["2a"], [("equivalents", {"number": 3, "unit": "equiv"})]),
    participant("pd_catalyst", "catalyst", "Pd(PPh3)4", ev5, None, None, [("catalyst_loading", {"number": 5, "unit": "mol%"})]),
    participant("organic_halide", "reactant", "PhI", ev5, "iodobenzene", SMILES["PhI"], [("equivalents", {"number": 2.03, "unit": "equiv"})]),
    participant("bronsted_acid", "reagent", "p-TsOH.H2O", ev5, None, SMILES["TsOH.H2O"], [("acid_loading", {"number": 21, "unit": "mol%"})]),
    participant("solvent", "solvent", "toluene", ev5, "toluene", SMILES["toluene"]),
]
records.append(record(
    "scheme5_1f_failed_recovery", "reported_experiment", ev5,
    parts,
    [step("attempted_cyclization", [p["entity_id"] for p in parts], ev5,
          temperature={"number": 90, "unit": "°C"}, time={"number": 10, "unit": "h"}, solvent="toluene")],
    [
        field("reaction_result", "no product formed", ev5),
        field("recovered_starting_material_yield", {"number": 83, "unit": "%"}, ev5, ["substrate_1f"]),
    ],
    notes=["The source reports failure of 1f to afford product and places recovered 1f (83%) on the product side of the arrow."],
    unresolved=["The recovered-starting-material measurement basis and isolation details are not stated."],
))

# Pages 5--6: proposed mechanism, explicitly not treated as a reported batch.
mechanism_ev = unique(ev5 + ev6)
records.append(record(
    "scheme6_proposed_mechanism", "mechanism", mechanism_ev,
    notes=[
        "Scheme 6 is a proposed catalytic cycle involving imine 7a, enamine 7b, pi-allylpalladium intermediates A/B, and cyclization to 4 or 6.",
        "The alternative order of palladation and amine condensation is mechanistic interpretation, not a separate reported experiment.",
    ],
    unresolved=["Generic R groups and proposed intermediates are not assigned as verified molecular structures."],
))


OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")


def rid(suffix):
    return f"{DOC}:{suffix}"


coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1,
            "state": "attempted",
            "regions": [
                {
                    "region": "full-page title, abstract, introduction, and lower-right Scheme 1",
                    "finding": "Abstract/introduction state the reaction concept; Scheme 1 is a generic R-group transformation and proposed imine/enamine route, not an individual batch experiment.",
                    "evidence_ids": evidence(1),
                }
            ],
            "record_ids": [rid("scheme1_general_transformation")],
            "unresolved": ["Generic R-group structures in Scheme 1 cannot be expanded into complete individual molecules."],
        },
        {
            "page": 2,
            "state": "attempted",
            "regions": [
                {
                    "region": "upper half, Table 1 and reaction drawing",
                    "finding": "Eleven amine-loading/Bronsted-acid optimization rows were read row by row; entry 5 includes the MgSO4 footnote and entry 8 preserves the acid-column dash without converting it to zero.",
                    "evidence_ids": evidence(2),
                },
                {
                    "region": "middle, Table 2 and reaction drawing",
                    "finding": "Six solvent rows were inspected; MeNO2 at reflux gives a complicated mixture, while the five numeric outcomes are isolated yields.",
                    "evidence_ids": evidence(2),
                },
                {
                    "region": "bottom two-column discussion",
                    "finding": "Narrative corroborates the Table 1 quantities, acid comparison, MgSO4 trial, and the choice of toluene; the common 72% row is not duplicated across tables.",
                    "evidence_ids": evidence(2),
                },
            ],
            "record_ids": [rid("standard_4aa")] + [rid(f"table1_entry{i}") for i in [1, 2, 3, 5, 6, 7, 8, 9, 10, 11]] + [rid(f"table2_entry{i}") for i in [1, 2, 3, 4, 6]],
            "unresolved": ["Most optimization rows omit exact scale, solvent volume, atmosphere, workup, and purification."],
        },
        {
            "page": 3,
            "state": "attempted",
            "regions": [
                {
                    "region": "upper third, Table 3 and footnotes",
                    "finding": "Seven amine-scope rows were inspected; entry 7 has both 4ag (42%) and footnoted 5a (34%), and the text flags post-chromatography decomposition of 4ab.",
                    "evidence_ids": evidence(3),
                },
                {
                    "region": "middle and lower portion, three arrows in Scheme 2",
                    "finding": "Three distinct substrate batches 1b, 1c, and 1d were extracted with their individual amine/PhI ratios, times, yields, and depicted products 6a--6c.",
                    "evidence_ids": evidence(3),
                },
                {
                    "region": "bottom discussion",
                    "finding": "Text provides qualitative context for amine scope; it does not add a new batch beyond Table 3 and Scheme 2.",
                    "evidence_ids": evidence(3),
                },
            ],
            "record_ids": [rid("standard_4aa")] + [rid(f"table3_entry{i}") for i in range(2, 8)] + [rid("scheme2_1b_to_6a"), rid("scheme2_1c_to_6b"), rid("scheme2_1d_to_6c")],
            "unresolved": ["The 34% secondary-product 5a outcome has no separately stated measurement basis; many complex structures remain machine-unverified."],
        },
        {
            "page": 4,
            "state": "attempted",
            "regions": [
                {
                    "region": "upper-left Figure 1 and adjacent Scheme 2 discussion",
                    "finding": "NOE drawing and prose support the relative trans assignment of 6b and the highly diastereoselective 1c/1d reactions; Figure 1 is characterization evidence, not a new experiment.",
                    "evidence_ids": evidence(4),
                },
                {
                    "region": "upper-middle Scheme 3, two reaction arrows",
                    "finding": "The S-2h reaction gives 6d in 69% yield with dr 1.3:1; substrate 1e gives a complicated unidentified mixture and no assigned product.",
                    "evidence_ids": evidence(4),
                },
                {
                    "region": "lower half, Table 4 and reaction drawing",
                    "finding": "All twelve organic-iodide rows were read independently; the common PhI/4aa row is linked to the standard record and the other eleven rows remain separate scope experiments.",
                    "evidence_ids": evidence(4),
                },
            ],
            "record_ids": [rid("standard_4aa"), rid("scheme2_1b_to_6a"), rid("scheme2_1c_to_6b"), rid("scheme2_1d_to_6c"), rid("scheme3_chiral_amine_6d"), rid("scheme3_substrate_1e_complicated")] + [rid(f"table4_entry{i}") for i in range(2, 13)],
            "unresolved": ["Table 4 omits organic-iodide equivalents and most operational details; vinyl-iodide and complex product structures need chemical review."],
        },
        {
            "page": 5,
            "state": "attempted",
            "regions": [
                {
                    "region": "top, two arrows in Scheme 4",
                    "finding": "Oxidation of 4ae to 8 (64%) and subsequent debenzylation of 8 to 9 (81%) were retained as two successive experiments, not one merged transformation.",
                    "evidence_ids": evidence(5),
                },
                {
                    "region": "middle, three arrows in Scheme 5",
                    "finding": "Three control experiments were extracted: early stopping gives 4aa and enamine 7aa; 5a converts to 4aa; 1f gives no product with 83% starting material recovered.",
                    "evidence_ids": evidence(5),
                },
                {
                    "region": "bottom discussion of Schemes 3--6",
                    "finding": "Prose identifies 7aa as an intermediate and discusses a proposed mechanism; mechanistic interpretation is classified separately from reported batches.",
                    "evidence_ids": evidence(5),
                },
            ],
            "record_ids": [rid("scheme3_substrate_1e_complicated"), rid("scheme4_4ae_to_8"), rid("scheme4_8_to_9"), rid("scheme5_intermediate_trapping"), rid("scheme5_5a_to_4aa"), rid("scheme5_1f_failed_recovery"), rid("scheme6_proposed_mechanism")],
            "unresolved": ["Schemes 4 and 5 omit scales, most reagent amounts, workups, and purification details; the recovery basis for 1f is unstated."],
        },
        {
            "page": 6,
            "state": "attempted",
            "regions": [
                {
                    "region": "top, Scheme 6 catalytic cycle",
                    "finding": "The R-group catalytic cycle is explicitly proposed and was stored as one mechanism record, not as experimental arrows with yields.",
                    "evidence_ids": evidence(6),
                },
                {
                    "region": "left column, Experimental Section Typical Procedure",
                    "finding": "Exact charges, argon atmosphere, temperature/time, TLC, evaporation, chromatography, product mass, and 72% yield for 4aa were merged into the standard record repeated in Tables 1--4.",
                    "evidence_ids": evidence(6),
                },
                {
                    "region": "right column references and lower-left characterization",
                    "finding": "Spectroscopic characterization and cited prior literature were inspected but not converted into duplicate reaction experiments.",
                    "evidence_ids": evidence(6),
                },
            ],
            "record_ids": [rid("standard_4aa"), rid("scheme6_proposed_mechanism")],
            "unresolved": ["Supporting Information is mentioned in the paper but no SI was supplied or explicitly associated."],
        },
    ],
}

coverage_path = ROOT / "runs/current/coverage/pages_0001_0006.json"
coverage_path.parent.mkdir(parents=True, exist_ok=True)
coverage_path.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

tasks_path = ROOT / "runs/current/tasks.json"
tasks = json.loads(tasks_path.read_text())
for task in tasks:
    if task.get("document_id") == DOC and 1 <= int(task["evidence_id"].split(":page", 1)[1].split(":", 1)[0]) <= 6:
        task["state"] = "attempted"
        task["reason"] = "Original page image inspected and reconciled into the pages 1--6 coverage ledger."
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"output": str(OUT), "records": len(records), "coverage": str(coverage_path)}, ensure_ascii=False))
