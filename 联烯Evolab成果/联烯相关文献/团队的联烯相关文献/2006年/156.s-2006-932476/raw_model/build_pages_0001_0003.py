#!/usr/bin/env python3
import json
from pathlib import Path

DOC = "doc_b1d645c8d64c6db5"
P1I, P1T = f"{DOC}:page1:image", f"{DOC}:page1:text"
P2I, P2T = f"{DOC}:page2:image", f"{DOC}:page2:text"
P3I, P3T = f"{DOC}:page3:image", f"{DOC}:page3:text"


def fact(value, evidence=()):
    return {
        "value": value,
        "evidence_ids": list(evidence),
        "verification": "missing" if value is None else "unreviewed",
    }


def fld(name, value, evidence=(), targets=None):
    result = {"name": name, "fact": fact(value, evidence)}
    if targets:
        result["target_entity_ids"] = list(targets)
    return result


def qty(number, unit, **extra):
    result = {"number": number, "unit": unit}
    result.update(extra)
    return result


def rng(low, high, unit, raw_text):
    return {"minimum": low, "maximum": high, "unit": unit, "raw_text": raw_text}


def part(entity_id, role, label, name, smiles, evidence, amounts=()):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence),
        "smiles": fact(smiles, evidence if smiles else ()),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": list(amounts),
    }


def missing_conditions():
    return [
        fld("atmosphere", None),
        fld("workup", None),
        fld("purification", None),
    ]


def record(suffix, source_id, kind, evidence, participants, conditions, outcomes,
           notes=(), unresolved=()):
    return {
        "record_id": f"{DOC}:{suffix}",
        "document_id": DOC,
        "source_reaction_id": source_id,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": list(evidence),
        "participants": participants,
        "steps": [{
            "step_id": "reaction",
            "participant_ids": [p["entity_id"] for p in participants],
            "conditions": conditions,
        }],
        "outcomes": outcomes,
        "notes": [fact(n, evidence) for n in notes],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": list(unresolved),
        },
    }


ALLENE = {
    "Bn": ("1a", "4-phenyl-1,2-butadiene", "C=C=CCc1ccccc1"),
    "n-C5H11": ("1b", "n-pentyl-substituted allene", "C=C=CCCCCC"),
    "n-C7H15": ("1c", "n-heptyl-substituted allene", "C=C=CCCCCCCC"),
    "c-C6H11": ("1d", "cyclohexyl-substituted allene", "C=C=CC1CCCCC1"),
}
RF_IODIDE = {
    "Cl(CF2)4": ("2a", "1-chloro-4-iodoperfluorobutane", "IC(F)(F)C(F)(F)C(F)(F)C(F)(F)Cl"),
    "n-C4F9": ("2b", "1-iodoperfluorobutane", "IC(F)(F)C(F)(F)C(F)(F)C(F)(F)F"),
}
RF_TAIL = {
    "Cl(CF2)4": "C(F)(F)C(F)(F)C(F)(F)C(F)(F)Cl",
    "n-C4F9": "C(F)(F)C(F)(F)C(F)(F)C(F)(F)F",
}
R_PREFIX = {
    "Bn": "c1ccccc1CC",
    "n-C5H11": "CCCCCC",
    "n-C7H15": "CCCCCCCC",
    "c-C6H11": "C1CCCCC1C",
}


def product3_smiles(r, rf):
    return f"{R_PREFIX[r]}=C(I)C{RF_TAIL[rf]}"


def product4_smiles(r, rf):
    return f"{R_PREFIX[r]}=C(C#CCO)C{RF_TAIL[rf]}"


def radical_participants(r, rf, product_label, evidence):
    al_label, al_name, al_smiles = ALLENE[r]
    rf_label, rf_name, rf_smiles = RF_IODIDE[rf]
    shared_eq = evidence
    return [
        part("allene", "reactant", al_label, al_name, al_smiles, evidence,
             [fld("equivalents", qty(1.0, "equiv"), shared_eq)]),
        part("rf_iodide", "reactant", rf_label, rf_name, rf_smiles, evidence,
             [fld("equivalents", qty(1.5, "equiv"), shared_eq)]),
        part("sodium_dithionite", "reagent", None, "sodium dithionite", "[Na+].[Na+].[O-]S(=O)S(=O)[O-]", evidence,
             [fld("equivalents", qty(1.5, "equiv"), shared_eq)]),
        part("sodium_bicarbonate", "reagent", None, "sodium bicarbonate", "[Na+].O=C([O-])O", evidence,
             [fld("equivalents", qty(1.5, "equiv"), shared_eq)]),
        part("dioxane", "solvent", None, "1,4-dioxane", "O1CCOCC1", evidence),
        part("water", "solvent", None, "water", "O", evidence),
        part("product3", "product", product_label, f"{product_label} E/Z mixture", product3_smiles(r, rf), evidence),
    ]


records = []

# Prose solvent screen preceding Table 1: six explicitly distinguished solvent conditions.
screen_solvents = [
    ("ch2cl2_water", "dichloromethane", "ClCCl", "3:1", "not formed"),
    ("benzene_water", "benzene", "c1ccccc1", "3:1", "not formed"),
    ("aqueous_dmf", "N,N-dimethylformamide", "CN(C)C=O", None, rng(15, 25, "%", "15–25%")),
    ("aqueous_dma", "N,N-dimethylacetamide", "CC(=O)N(C)C", None, rng(15, 25, "%", "15–25%")),
    ("aqueous_dmso", "dimethyl sulfoxide", "CS(C)=O", None, rng(15, 25, "%", "15–25%")),
    ("aqueous_thf", "tetrahydrofuran", "C1CCOC1", None, rng(15, 25, "%", "15–25%")),
]
for suffix, solvent_name, solvent_smiles, ratio, result in screen_solvents:
    ev = (P1I, P1T)
    participants = [
        part("allene_1a", "reactant", "1a", "4-phenyl-1,2-butadiene", ALLENE["Bn"][2], ev),
        part("rf_iodide_2a", "reactant", "2a", "I(CF2)4Cl", RF_IODIDE["Cl(CF2)4"][2], ev),
        part("sodium_dithionite", "reagent", None, "sodium dithionite", "[Na+].[Na+].[O-]S(=O)S(=O)[O-]", ev),
        part("organic_solvent", "solvent", None, solvent_name, solvent_smiles, ev),
        part("water", "solvent", None, "water", "O", ev),
        part("product_3a", "product", "3a", "radical-addition product 3a", product3_smiles("Bn", "Cl(CF2)4"), ev),
    ]
    conditions = [fld("solvent", f"aqueous {solvent_name}", ev)]
    if ratio:
        conditions.append(fld("organic_solvent_to_water_ratio", ratio, ev))
    conditions += [fld("temperature", None), fld("time", None)] + missing_conditions()
    collective = result != "not formed"
    unresolved = [
        "Exact reagent quantities, temperature, time, workup, purification, and yield basis are not reported for this solvent trial.",
        "The text does not explicitly state whether NaHCO3 was present in this preliminary trial.",
        "Candidate product connectivity and alkene geometry require chemical review.",
    ]
    if collective:
        unresolved.append("The 15–25% range is reported collectively for aqueous DMF, DMA, DMSO, or THF; no exact yield is assigned to this individual solvent.")
    records.append(record(
        f"solvent_screen_{suffix}", f"prose solvent screen: {suffix}", "optimization_entry", ev,
        participants, conditions,
        [fld("reported_yield_3a", result, ev, ["product_3a"]), fld("yield_measurement_basis", None)],
        notes=("Preliminary solvent screen for formation of expected product 3a.",),
        unresolved=unresolved,
    ))

# Table 1 substrate scope. Entry 2 is enriched by the matching page-3 typical procedure.
table1 = [
    (1, "Bn", "Cl(CF2)4", "3a", 63, "1:1.80"),
    (2, "Bn", "n-C4F9", "3b", 65, "1:1.78"),
    (3, "n-C5H11", "Cl(CF2)4", "3c", 55, "1:2.41"),
    (4, "n-C5H11", "n-C4F9", "3d", 52, "1:2.33"),
    (5, "n-C7H15", "Cl(CF2)4", "3e", 63, "1:2.75"),
    (6, "n-C7H15", "n-C4F9", "3f", 69, "1:2.34"),
    (7, "c-C6H11", "Cl(CF2)4", "3g", 59, "1:2.22"),
    (8, "c-C6H11", "n-C4F9", "3h", 62, "1:2.21"),
]
for entry, r, rf, plabel, yield_value, ez in table1:
    ev = (P1I, P1T, P3I, P3T) if entry == 2 else (P1I, P1T)
    participants = radical_participants(r, rf, plabel, (P1I, P1T))
    if entry == 2:
        exact = (P3I, P3T)
        by_id = {p["entity_id"]: p for p in participants}
        by_id["allene"]["amounts"] += [fld("mass", qty(258.8, "mg"), exact), fld("amount", qty(1.99, "mmol"), exact)]
        by_id["rf_iodide"]["amounts"] += [fld("mass", qty(1.0482, "g"), exact), fld("amount", qty(3.03, "mmol"), exact)]
        by_id["sodium_dithionite"]["amounts"] += [fld("mass", qty(523.6, "mg"), exact), fld("amount", qty(3.01, "mmol"), exact)]
        by_id["sodium_bicarbonate"]["amounts"] += [fld("mass", qty(253.4, "mg"), exact), fld("amount", qty(3.02, "mmol"), exact)]
        by_id["product3"]["amounts"] += [fld("mass", qty(612.7, "mg"), exact)]
    conditions = [
        fld("solvent", "1,4-dioxane–H2O", (P1I, P1T)),
        fld("solvent_ratio", "3:1", (P1I, P1T)),
        fld("temperature", rng(40, 45, "°C", "40–45 °C"), (P1I, P1T)),
        fld("time", qty(3, "h"), (P1I, P1T)),
        fld("atmosphere", None), fld("workup", None), fld("purification", None),
    ]
    if entry == 2:
        conditions.append(fld("mixed_solvent_total_volume", qty(16, "mL"), (P3I, P3T)))
    records.append(record(
        f"table1_entry{entry}", f"Table 1 entry {entry}", "substrate_scope_entry", ev,
        participants, conditions,
        [
            fld("isolated_yield_3", qty(yield_value, "%"), (P1I, P1T), ["product3"]),
            fld("yield_measurement_basis", "isolated", (P1I, P1T)),
            fld("reported_E_Z_ratio", ez, (P1I, P1T), ["product3"]),
            fld("selectivity_measurement_basis", "NMR spectra", (P1I, P1T)),
        ],
        notes=("The E and Z isomers could not be separated by flash chromatography.",),
        unresolved=(
            "Atmosphere, workup, and detailed purification are not reported.",
            "Candidate product connectivity and reported E/Z geometry require chemical review.",
        ),
    ))


def kinetic_participants(r, rf, substrate_label, evidence, alcohol_eq=None, catalyst_loading=None):
    substrate_smiles = product3_smiles(r, rf)
    product_smiles = product4_smiles(r, rf)
    alcohol_amounts = [fld("equivalents", qty(alcohol_eq, "equiv"), evidence)] if alcohol_eq is not None else []
    catalyst_amounts = [fld("catalyst_loading", qty(catalyst_loading, "mol%"), evidence)] if catalyst_loading is not None else []
    amine_amounts = [fld("equivalents", qty(alcohol_eq, "equiv"), evidence)] if alcohol_eq is not None else []
    return [
        part("substrate3", "reactant", substrate_label, f"{substrate_label} E/Z mixture", substrate_smiles, evidence),
        part("propargyl_alcohol", "reactant", None, "propargyl alcohol", "C#CCO", evidence, alcohol_amounts),
        part("pd_catalyst", "catalyst", None, "Pd(PPh3)2Cl2", None, evidence, catalyst_amounts),
        part("cui", "catalyst", None, "copper(I) iodide", "[Cu]I", evidence, catalyst_amounts),
        part("diethylamine", "reagent", None, "diethylamine", "CCNCC", evidence, amine_amounts),
        part("acetonitrile", "solvent", None, "acetonitrile", "CC#N", evidence),
        part("recovered_z3", "product", f"(Z)-{substrate_label}", f"recovered (Z)-{substrate_label}", substrate_smiles, evidence),
        part("product4", "product", f"4{substrate_label[-1]}" if substrate_label[-1].isalpha() else "4", "Sonogashira product E/Z mixture", product_smiles, evidence),
    ]


# Table 2 optimization rows.
table2 = [
    (1, 0.6, 3.0, 50, 54, 26, "95:5"),
    (2, 0.7, 3.5, 25, 48, 29, "93:7"),
    (3, 0.9, 4.5, 12, 61, 33, "96:4"),
    (4, 0.6, 4.5, 30, 54, 30, "96:4"),
    (5, 0.6, 3.5, 30, 57, 32, "95:5"),
    (6, 0.7, 3.0, 12, 53, 34, "91:9"),
    (7, 0.9, 3.0, 12, 50, 35, "88:12"),
]
for entry, equiv, cat, minutes, zrec, prod_yield, ratio in table2:
    ev = (P2I, P2T)
    participants = kinetic_participants("Bn", "n-C4F9", "3b", ev, equiv, cat)
    if entry == 1:
        participants.append(part("recovered_e3", "product", "(E)-3b", "unreacted (E)-3b", product3_smiles("Bn", "n-C4F9"), ev))
    outcomes = [
        fld("recovered_(Z)-3b_yield", qty(zrec, "%"), ev, ["recovered_z3"]),
        fld("reported_yield_4b", qty(prod_yield, "%"), ev, ["product4"]),
        fld("reported_E_Z_ratio_4b", ratio, ev, ["product4"]),
        fld("selectivity_measurement_basis", "GC analysis", ev),
        fld("yield_measurement_basis", None),
    ]
    if entry == 1:
        outcomes.append(fld("recovered_(E)-3b_percentage", qty(16, "%"), ev, ["recovered_e3"]))
    records.append(record(
        f"table2_entry{entry}", f"Table 2 entry {entry}", "optimization_entry", ev,
        participants,
        [
            fld("starting_material_E_Z_ratio", "1:1.78", (P1I, P1T)),
            fld("temperature", "r.t.", ev), fld("time", qty(minutes, "min"), ev),
            fld("atmosphere", None), fld("reaction_scale", None), fld("workup", None), fld("purification", None),
        ],
        outcomes,
        notes=("The table column is headed E/Z ratio, while footnote a prints Z/E ratio; values are retained under the column heading without silently resolving the inconsistency.",),
        unresolved=(
            "Yield measurement basis, scale, atmosphere, workup, and purification are not reported for this optimization row.",
            "The source does not separately state whether the catalyst-loading column applies identically to both displayed catalysts; the machine record applies it to both and requires review.",
            "Candidate substrate/product connectivity and E/Z geometry require chemical review.",
        ),
    ))

# Table 3 kinetic-resolution scope.
table3 = [
    (1, "Bn", "Cl(CF2)4", "3a", 11, 30, 55, 28, 3),
    (2, "n-C5H11", "Cl(CF2)4", "3c", 0, 60, 45, 22, 2),
    (3, "n-C7H15", "n-C4F9", "3f", 0, 60, 58, 22, 1),
    (4, "c-C6H11", "Cl(CF2)4", "3g", 13, 30, 47, 25, 2),
]
for entry, r, rf, substrate_label, temp, minutes, zrec, ey, zy in table3:
    ev = (P2I, P2T)
    substrate_smiles = product3_smiles(r, rf)
    prod_smiles = product4_smiles(r, rf)
    participants = [
        part("substrate3", "reactant", substrate_label, f"{substrate_label} E/Z mixture", substrate_smiles, ev,
             [fld("equivalents", qty(1.0, "equiv"), ev)]),
        part("propargyl_alcohol", "reactant", None, "propargyl alcohol", "C#CCO", ev,
             [fld("equivalents", qty(0.6, "equiv"), ev)]),
        part("pd_catalyst", "catalyst", None, "Pd(PPh3)2Cl2", None, ev,
             [fld("molar_ratio_equivalents", qty(0.035, "equiv"), ev)]),
        part("cui", "catalyst", None, "copper(I) iodide", "[Cu]I", ev,
             [fld("molar_ratio_equivalents", qty(0.035, "equiv"), ev)]),
        part("diethylamine", "reagent", None, "diethylamine", "CCNCC", ev),
        part("acetonitrile", "solvent", None, "acetonitrile", "CC#N", ev),
        part("recovered_z3", "product", f"(Z)-{substrate_label}", f"recovered (Z)-{substrate_label}", substrate_smiles, ev),
        part("product_e4", "product", f"(E)-4{substrate_label[-1]}", "(E)-Sonogashira coupling product", prod_smiles, ev),
        part("product_z4", "product", f"(Z)-4{substrate_label[-1]}", "(Z)-Sonogashira coupling product", prod_smiles, ev),
    ]
    records.append(record(
        f"table3_entry{entry}", f"Table 3 entry {entry}", "substrate_scope_entry", ev,
        participants,
        [
            fld("temperature", qty(temp, "°C"), ev), fld("time", qty(minutes, "min"), ev),
            fld("atmosphere", None), fld("reaction_scale", None), fld("workup", None), fld("purification", None),
        ],
        [
            fld("recovered_(Z)-3_yield", qty(zrec, "%"), ev, ["recovered_z3"]),
            fld("isolated_yield_(E)-4", qty(ey, "%"), ev, ["product_e4"]),
            fld("isolated_yield_(Z)-4", qty(zy, "%"), ev, ["product_z4"]),
            fld("yield_measurement_basis", "isolated", ev),
        ],
        unresolved=(
            "Reaction scale, atmosphere, workup, purification, and the amount of Et2NH are not reported in the table.",
            "Candidate substrate/product connectivity and E/Z geometry require chemical review.",
        ),
    ))

# Page-3 coupling procedure: independent repetition because its exact yields differ from Table 2.
ev = (P3I, P3T)
participants = [
    part("substrate_3b", "reactant", "3b", "3b E/Z mixture", product3_smiles("Bn", "n-C4F9"), ev,
         [fld("mass", qty(118.7, "mg"), ev), fld("amount", qty(0.25, "mmol"), ev)]),
    part("propargyl_alcohol", "reactant", None, "propargyl alcohol", "C#CCO", ev,
         [fld("mass", qty(8.5, "mg"), ev), fld("amount", qty(0.15, "mmol"), ev)]),
    part("pd_catalyst", "catalyst", None, "Pd(PPh3)2Cl2", None, ev,
         [fld("mass", qty(6.2, "mg"), ev), fld("amount", qty(0.00884, "mmol", raw_text="8.84 × 10^-3 mmol"), ev), fld("catalyst_loading", qty(3.5, "mol%"), ev)]),
    part("cui", "catalyst", None, "copper(I) iodide", "[Cu]I", ev,
         [fld("mass", qty(1.8, "mg"), ev), fld("amount", qty(0.00947, "mmol", raw_text="9.47 × 10^-3 mmol"), ev), fld("catalyst_loading", qty(3.8, "mol%"), ev)]),
    part("diethylamine", "reagent", None, "diethylamine", "CCNCC", ev,
         [fld("mass", qty(11.0, "mg"), ev), fld("amount", qty(0.15, "mmol"), ev)]),
    part("acetonitrile", "solvent", None, "acetonitrile", "CC#N", ev,
         [fld("volume", qty(0.5, "mL"), ev)]),
    part("recovered_z3b", "product", "(Z)-3b", "recovered (Z)-3b", product3_smiles("Bn", "n-C4F9"), ev,
         [fld("mass", qty(50.9, "mg"), ev)]),
    part("product_z4b", "product", "(Z)-4b", "(Z)-Sonogashira coupling product 4b", product4_smiles("Bn", "n-C4F9"), ev,
         [fld("mass", qty(4.0, "mg"), ev)]),
    part("product_e4b", "product", "(E)-4b", "(E)-Sonogashira coupling product 4b", product4_smiles("Bn", "n-C4F9"), ev,
         [fld("mass", qty(33.9, "mg"), ev)]),
]
records.append(record(
    "typical_coupling_3b", "Typical procedure: coupling of 3b", "reported_experiment", ev,
    participants,
    [
        fld("starting_material_E_Z_ratio", "1:1.78", ev),
        fld("temperature", None), fld("time", None), fld("atmosphere", None), fld("workup", None), fld("purification", None),
    ],
    [
        fld("recovered_(Z)-3b_yield", qty(43, "%"), ev, ["recovered_z3b"]),
        fld("reported_yield_(Z)-4b", qty(4, "%"), ev, ["product_z4b"]),
        fld("reported_yield_(E)-4b", qty(34, "%"), ev, ["product_e4b"]),
        fld("yield_measurement_basis", None),
    ],
    notes=("Kept separate from Table 2 entry 5 because the reported product and recovered-substrate yields differ despite similar nominal reagent loadings.",),
    unresolved=(
        "Time, temperature, atmosphere, workup, purification, and yield measurement basis are not stated in this procedure.",
        "Candidate substrate/product connectivity and E/Z geometry require chemical review.",
    ),
))

out = Path(__file__).with_name("pages_0001_0003_records.json")
out.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
print(f"wrote {len(records)} records to {out}")
