#!/usr/bin/env python3
"""Build evidence-linked raw records for jo0507441 PDF pages 1-4."""

import json
from pathlib import Path


DOC = "doc_5f0331537363eece"
BASE = Path(__file__).resolve().parents[1]
RAW = BASE / "raw_model" / "extracted_records_pages_0001_0004.json"
COVERAGE = BASE / "coverage" / "pages_0001_0004.json"


def ev(page):
    return [f"{DOC}:page{page}:text", f"{DOC}:page{page}:image"]


def fact(value, evidence):
    return {
        "value": value,
        "evidence_ids": [] if value is None else list(evidence),
        "verification": "missing" if value is None else "unreviewed",
    }


def field(name, value, evidence, targets=None):
    item = {"name": name, "fact": fact(value, evidence)}
    if targets:
        item["target_entity_ids"] = list(targets)
    return item


def amount(name, number, unit, evidence, targets=None, **extra):
    value = {"number": number, "unit": unit, **extra}
    return field(name, value, evidence, targets)


def participant(entity_id, role, label, evidence, name=None, smiles=None, amounts=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence) if name is not None else fact(None, []),
        "smiles": fact(smiles, evidence) if smiles is not None else fact(None, []),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": amounts or [],
    }


def record(suffix, source_id, kind, evidence, participants, steps=None, outcomes=None,
           notes=None, unresolved=None):
    return {
        "record_id": f"{DOC}:{suffix}",
        "document_id": DOC,
        "source_reaction_id": source_id,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": list(dict.fromkeys(evidence)),
        "participants": participants,
        "steps": steps or [],
        "outcomes": outcomes or [],
        "notes": notes or [],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved or [],
        },
    }


ALLENAMIDES = {
    "1a": ("2,3-allenamide 1a (N-tosyl; terminal dimethyl)", "CC(C)=C=CC(=O)NS(=O)(=O)c1ccc(C)cc1"),
    "1b": ("N-benzyl 2,3-allenamide 1b (terminal dimethyl)", "CC(C)=C=CC(=O)NCc1ccccc1"),
    "1c": ("2,3-allenamide 1c (primary amide; terminal dimethyl)", "CC(C)=C=CC(N)=O"),
    "1d": ("N-n-butyl 2,3-allenamide 1d (terminal dimethyl)", "CCCCNC(=O)C=C=C(C)C"),
    "1e": ("cyclic 2,3-allenamide 1e (R2/R3 = (CH2)5)", "NC(=O)C=C=C1CCCCC1"),
    "1f": ("N-benzyl 2,3-allenamide 1f (terminal methyl/ethyl)", "CCC(C)=C=CC(=O)NCc1ccccc1"),
}

KETONES = {
    "2a": ("1,2-allenyl methyl ketone 2a", "C=C=CC(C)=O"),
    "2b": ("1,2-allenyl phenyl ketone 2b", "C=C=CC(=O)c1ccccc1"),
    "2c": ("1,2-allenyl benzyl ketone 2c", "C=C=CC(=O)Cc1ccccc1"),
    "2d": ("1,2-allenyl n-butyl ketone 2d", "C=C=CC(=O)CCCC"),
    "2e": ("1,2-allenyl n-heptyl ketone 2e", "C=C=CC(=O)CCCCCCC"),
}


def substrate(label, evidence, role="reactant", amounts=None):
    name, smiles = ALLENAMIDES[label]
    return participant(label, role, label, evidence, name, smiles, amounts)


def ketone(label, evidence, amounts=None, shown_label=None):
    name, smiles = KETONES[label]
    return participant(label, "reactant", shown_label or label, evidence, name, smiles, amounts)


def catalyst(evidence, loading, extra_amounts=None):
    amounts = [amount("catalyst_loading", loading, "mol%", evidence)]
    amounts.extend(extra_amounts or [])
    return participant(
        "pd_catalyst", "catalyst", "Pd(CH3CN)2Cl2", evidence,
        "bis(acetonitrile)palladium(II) dichloride", None, amounts,
    )


def benzoquinone(evidence, equivalents=None, extra_amounts=None):
    amounts = []
    if equivalents is not None:
        amounts.append(amount("equivalents", equivalents, "equiv", evidence))
    amounts.extend(extra_amounts or [])
    return participant(
        "benzoquinone", "reagent", "BQ", evidence,
        "1,4-benzoquinone", "O=C1C=CC(=O)C=C1", amounts,
    )


def solvent(entity_id, label, name, smiles, evidence, volume=None):
    amounts = [] if volume is None else [amount("volume", volume, "mL", evidence)]
    return participant(entity_id, "solvent", label, evidence, name, smiles, amounts)


def product(label, evidence, name=None):
    return participant("product", "product", label, evidence, name, None, [])


def reaction_step(participant_ids, evidence, time=None, temperature=None,
                  solvent_text=None, extra=None, step_id="reaction"):
    conditions = []
    if time is not None:
        conditions.append(amount("time", time, "h", evidence))
    if temperature is not None:
        if isinstance(temperature, dict):
            conditions.append(field("temperature", temperature, evidence))
        else:
            conditions.append(amount("temperature", temperature, "°C", evidence))
    if solvent_text is not None:
        conditions.append(field("solvent", solvent_text, evidence))
    conditions.extend(extra or [])
    return {"step_id": step_id, "participant_ids": participant_ids, "conditions": conditions}


def yield_outcome(value, evidence, product_id="product", isolated=False):
    name = "isolated_yield" if isolated else "reported_yield"
    result = [field(name, {"number": value, "unit": "%"}, evidence, [product_id])]
    if isolated:
        result.append(field("yield_measurement_basis", "isolated yield", evidence, [product_id]))
    return result


records = []

# Page 1 graphical abstract: generic current-work transformation, not an experiment.
e1 = ev(1)
records.append(record(
    "graphical_abstract_general_scheme", "page1_graphical_abstract", "general_scheme", e1,
    [
        participant("generic_allenamide_1", "reactant", "1", e1, "generic 2,3-allenamide", None),
        participant("generic_allenyl_ketone_2", "reactant", "2", e1, "generic 1,2-allenyl ketone", None),
        participant("pd_catalyst", "catalyst", "Pd(CH3CN)2Cl2", e1,
                    "bis(acetonitrile)palladium(II) dichloride", None,
                    [amount("catalyst_loading", 1, "mol%", e1)]),
        participant("generic_product_3", "product", "3", e1,
                    "generic 4-(furan-3-yl)-2(5H)-furanimine", None),
    ],
    [reaction_step(["generic_allenamide_1", "generic_allenyl_ketone_2", "pd_catalyst"], e1,
                   extra=[field("operation", "oxidative heterodimerization; additive and solvent are unspecified in the graphical abstract", e1)])],
    unresolved=["Generic R groups prevent complete structures.", "Additive, solvent, time, temperature, and yield are not given in this region."],
))

# Page 2 Scheme 1: arrows summarize prior work; they are not experiments in this paper.
e2 = ev(2)
scheme1_common = [
    participant("organic_halide", "reactant", "R5-X", e2, "generic organic halide", None),
    participant("generic_allenamide", "reactant", "generic 2,3-allenamide", e2, None, None),
]
records.append(record(
    "scheme1_arrow_intermediate", "scheme1_intermediate", "literature_example", e2,
    scheme1_common + [participant("organopalladium_intermediate", "product", "organopalladium intermediate", e2, None, None)],
    [reaction_step(["organic_halide", "generic_allenamide"], e2,
                   extra=[field("operation", "Pd(0)-catalyzed coupling leading to the depicted organopalladium intermediate", e2)])],
    unresolved=["Scheme 1 summarizes cited prior work and gives no individual experimental procedure or yield.", "Generic R groups and X are unresolved."],
))
records.append(record(
    "scheme1_arrow_n_attack", "scheme1_n_attack", "literature_example", e2,
    [participant("organopalladium_intermediate", "reactant", "organopalladium intermediate", e2, None, None),
     participant("n_attack_product", "product", "gamma-lactam product", e2, None, None)],
    [reaction_step(["organopalladium_intermediate"], e2,
                   extra=[field("operation", "N-attack cyclization when R2 = H", e2)])],
    unresolved=["Prior-work pathway only; no experiment-specific quantities, conditions, or yield are supplied."],
))
records.append(record(
    "scheme1_arrow_o_attack", "scheme1_o_attack", "literature_example", e2,
    [participant("organopalladium_intermediate", "reactant", "organopalladium intermediate", e2, None, None),
     participant("o_attack_product", "product", "furanimine product", e2, None, None)],
    [reaction_step(["organopalladium_intermediate"], e2,
                   extra=[field("operation", "O-attack cyclization when R1 and R2 are not H", e2)])],
    unresolved=["Prior-work pathway only; no experiment-specific quantities, conditions, or yield are supplied."],
))


# Table 1, entries 1-7. Page 4 gives the shared procedures and two explicit examples.
table1 = [
    (1, "2a", "A", 3, 30, 86, "Z-3aa"),
    (2, "2a", "B", 5, 30, 66, "Z-3aa"),
    (3, "2b", "A", 3, 30, 60, "Z-3ab"),
    (4, "2b", "B", 5, 30, 75, "Z-3ab"),
    (5, "2c", "B", 3, 35, 63, "Z-3ac"),
    (6, "2d", "A", 1, 25, 63, "Z-3ad"),
    (7, "2d", "B", 1.5, 40, 69, "Z-3ad"),
]
e24 = e2 + ev(4)
for entry, ket, cond, hours, temp, yld, prod_label in table1:
    evidence = e24
    a1_amounts = [amount("table_condition_amount", 0.5 if entry == 3 else 0.25, "mmol", e2)]
    ket_amounts = [amount("equivalents", 5 if cond == "A" else 2, "equiv", e2)]
    if entry != 3:
        ket_amounts.append(amount("table_condition_amount", 1.25 if cond == "A" else 0.5, "mmol", e2))
    cat_extra = []
    bq_extra = []
    solvent_volume = 3 if cond == "A" else 1.5
    outcome_extra = []
    unresolved = ["No supporting information was explicitly associated.", "Product SMILES was not encoded from the compact scheme drawing."]
    extra_conditions = [field("operation", "stirred until complete consumption of starting material by TLC", ev(4))]
    if entry == 1:
        a1_amounts += [amount("procedure_mass", 68, "mg", ev(4)), amount("procedure_amount", 0.257, "mmol", ev(4))]
        ket_amounts += [amount("procedure_mass", 104, "mg", ev(4)), amount("procedure_amount", 0.524, "mmol", ev(4))]
        cat_extra = [amount("procedure_mass", 3, "mg", ev(4)), amount("procedure_amount", 0.0116, "mmol", ev(4))]
        outcome_extra = [amount("product_mass", 76, "mg", ev(4), targets=["product"])]
        unresolved.append("The explicit Condition A example prints 2a as 104 mg and 0.524 mmol, while Table 1 defines 5.0 equiv/1.25 mmol at 0.25 mmol 1a; all printed values are retained without correction.")
    elif entry == 2:
        a1_amounts += [amount("procedure_mass", 66, "mg", ev(4)), amount("procedure_amount", 0.249, "mmol", ev(4))]
        ket_amounts += [amount("procedure_mass", 43, "mg", ev(4)), amount("procedure_amount", 0.524, "mmol", ev(4))]
        cat_extra = [amount("procedure_mass", 0.65, "mg", ev(4)), amount("procedure_amount", 0.0025, "mmol", ev(4))]
        bq_extra = [amount("procedure_mass", 30, "mg", ev(4)), amount("procedure_amount", 0.278, "mmol", ev(4))]
        outcome_extra = [amount("product_mass", 57, "mg", ev(4), targets=["product"])]
        extra_conditions.append(amount("procedure_temperature", 31, "°C", ev(4)))
        unresolved.append("Table 1 reports 30 °C, while the explicit Condition B example reports 31 °C; both are retained.")
    parts = [substrate("1a", evidence, amounts=a1_amounts), ketone(ket, evidence, ket_amounts,
             shown_label=("3d (printed; chemically the 2d ketone series)" if entry in (6, 7) else ket)),
             catalyst(evidence, 5 if cond == "A" else 1, cat_extra)]
    if cond == "B":
        parts.append(benzoquinone(evidence, 1, bq_extra))
    parts += [solvent("acetonitrile", "CH3CN", "acetonitrile", "CC#N", evidence, solvent_volume),
              product(prod_label, evidence,
                      "5,5-dimethyl-4-(5-methylfuran-3-yl)-N-(4-methylbenzenesulfonyl)-2(5H)-furanimine" if prod_label == "Z-3aa" else None)]
    ids = [p["entity_id"] for p in parts if p["role"] != "product"]
    steps = [reaction_step(ids, evidence, hours, temp, "CH3CN", extra_conditions),
             {"step_id": "isolation", "participant_ids": ["product"], "conditions": [
                 field("workup", "CH3CN evaporated after TLC-indicated completion", ev(4)),
                 field("purification", "flash chromatography on silica gel; ethyl acetate/petroleum ether eluent", ev(4)),
             ]}]
    outcomes = yield_outcome(yld, e2) + outcome_extra
    if entry in (6, 7):
        unresolved.append("Table 1 prints the n-Bu ketone label as 3d, whereas the ketone series and Table 3 identify it as 2d; the printed anomaly is preserved in the label.")
    records.append(record(f"table1_entry_{entry:02d}", f"Table 1 entry {entry}", "optimization_entry",
                          evidence, parts, steps, outcomes, unresolved=unresolved))


# Table 2, entries 1-11. Entry 9 is the same experiment as Table 3 entry 1 and the page-4 Z-3ba example.
table2 = [
    (1, 5, None, "CH3CN", 12, 19, 0, 5),
    (2, 5, None, "CH3CN/HOAc = 3:1", 6, 30, 27, 5),
    (3, 10, None, "CH3CN/HOAc = 3:1", 2, 35, 50, 5),
    (4, 5, 1.0, "CH3CN/HOAc = 3:1", 2, 35, 82, 5),
    (5, 2, 1.0, "CH3CN/HOAc = 3:1", 4, 37, 84, 5),
    (6, 5, 1.0, "CH3CN + 1.0 equiv HOAc", 7.5, 36, 0, 5),
    (7, 2, 1.0, "DMA/HOAc = 3:1", 4.5, 36, 0, 5),
    (8, 2, 1.0, "HOAc", 2, 40, 84, 5),
    (9, 2, 1.0, "HOAc", 2, 36, 86, 1),
    (10, 2, 1.5, "HOAc", 2.5, 35, 86, 1),
    (11, 1.5, 1.1, "HOAc", 2, 35, 60, 1),
]
shared_z3ba_id = f"{DOC}:table2_entry_09_table3_entry_01_z3ba"
for entry, ket_eq, bq_eq, solvent_text, hours, temp, yld, cat_loading in table2:
    evidence = e2
    a1_amounts = [amount("reaction_scale", 0.25, "mmol", e2)]
    ket_amounts = [amount("equivalents", ket_eq, "equiv", e2)]
    cat_extra = []
    bq_extra = []
    prod_amounts = []
    unresolved = ["No supporting information was explicitly associated.", "Atmosphere and experiment-specific workup are not reported in Table 2.", "Product SMILES remains unresolved from the scheme drawing."]
    if entry == 9:
        evidence = e2 + ev(3) + ev(4)
        a1_amounts += [amount("procedure_mass", 50, "mg", ev(4)), amount("procedure_amount", 0.249, "mmol", ev(4))]
        ket_amounts += [amount("procedure_mass", 41, "mg", ev(4)), amount("procedure_amount", 0.50, "mmol", ev(4))]
        cat_extra = [amount("procedure_mass", 0.65, "mg", ev(4)), amount("procedure_amount", 0.0025, "mmol", ev(4))]
        bq_extra = [amount("procedure_mass", 28, "mg", ev(4)), amount("procedure_amount", 0.259, "mmol", ev(4))]
        prod_amounts = [amount("product_mass", 60, "mg", ev(4), targets=["product"])]
        unresolved = ["No supporting information was explicitly associated.", "This single experiment is printed as Table 2 entry 9, Table 3 entry 1, and the explicit Z-3ba procedure; it is intentionally not duplicated.", "Product SMILES remains unresolved from the scheme drawing."]
    parts = [substrate("1b", evidence, amounts=a1_amounts), ketone("2a", evidence, ket_amounts),
             catalyst(evidence, cat_loading, cat_extra)]
    if bq_eq is not None:
        parts.append(benzoquinone(evidence, bq_eq, bq_extra))
    if entry == 6:
        parts += [solvent("acetonitrile", "CH3CN", "acetonitrile", "CC#N", evidence),
                  participant("acetic_acid", "reagent", "HOAc", evidence, "acetic acid", "CC(=O)O",
                              [amount("equivalents", 1.0, "equiv", e2)])]
    elif "CH3CN/HOAc" in solvent_text:
        parts += [solvent("acetonitrile", "CH3CN", "acetonitrile", "CC#N", evidence),
                  solvent("acetic_acid", "HOAc", "acetic acid", "CC(=O)O", evidence)]
    elif "DMA/HOAc" in solvent_text:
        parts += [solvent("dma", "DMA", "N,N-dimethylacetamide", "CC(=O)N(C)C", evidence),
                  solvent("acetic_acid", "HOAc", "acetic acid", "CC(=O)O", evidence)]
    elif solvent_text == "HOAc":
        parts.append(solvent("acetic_acid", "HOAc", "acetic acid", "CC(=O)O", evidence, 1.5 if entry == 9 else None))
    else:
        parts.append(solvent("acetonitrile", "CH3CN", "acetonitrile", "CC#N", evidence))
    parts.append(product("Z-3ba", evidence, "5,5-dimethyl-4-(5-methylfuran-3-yl)-N-benzyl-2(5H)-furanimine"))
    ids = [p["entity_id"] for p in parts if p["role"] != "product"]
    extra = []
    if entry == 9:
        extra.append(field("operation", "stirred and monitored by TLC", ev(4)))
    steps = [reaction_step(ids, evidence, hours, temp, solvent_text, extra)]
    if entry == 9:
        steps.append({"step_id": "isolation", "participant_ids": ["product"], "conditions": [
            field("workup", "Workup A: evaporate HOAc after TLC-indicated completion", ev(4)),
            field("purification", "flash chromatography on silica gel", ev(4)),
        ]})
    outcomes = yield_outcome(yld, e2 if entry != 9 else evidence, isolated=True) + prod_amounts
    suffix = "table2_entry_09_table3_entry_01_z3ba" if entry == 9 else f"table2_entry_{entry:02d}"
    source_id = "Table 2 entry 9 / Table 3 entry 1 / Z-3ba explicit procedure" if entry == 9 else f"Table 2 entry {entry}"
    records.append(record(suffix, source_id, "optimization_entry" if entry != 9 else "reported_experiment",
                          evidence, parts, steps, outcomes, unresolved=unresolved))


# Table 3 entries 2-15; entry 1 was merged above with Table 2 entry 9.
scope_rows = [
    (2, "1b", "2b", 1.1, 2, 56, "Z-3bb"),
    (3, "1b", "2c", 1.0, 10, 81, "Z-3bc"),
    (4, "1b", "2d", 1.1, 10, 76, "Z-3bd"),
    (5, "1b", "2e", 1.0, 17, 64, "Z-3be"),
    (6, "1c", "2a", 1.1, 6, 81, "Z-3ca"),
    (7, "1c", "2b", 1.1, 11, 55, "Z-3cb"),
    (8, "1c", "2c", 1.1, 5, 71, "Z-3cc"),
    (9, "1c", "2d", 1.0, 6.5, 76, "Z-3cd"),
    (10, "1c", "2e", 1.0, 5, 59, "Z-3ce"),
    (11, "1d", "2a", 1.1, 4, 68, "Z-3da"),
    (12, "1e", "2a", 1.1, 5.5, 80, "Z-3ea"),
    (13, "1e", "2d", 1.1, 6.5, 70, "Z-3ed"),
    (14, "1f", "2a", 1.0, 4, 69, "Z-3fa"),
    (15, "1f", "2d", 1.0, 3, 63, "Z-3fd"),
]
e34 = ev(3) + ev(4)
temp_range = {"minimum": 25, "maximum": 36, "unit": "°C", "raw_text": "25-36 °C"}
for entry, allene, ket, bq_eq, hours, yld, prod_label in scope_rows:
    evidence = e34
    scale_value = {"number": 0.4, "unit": "mmol"} if entry == 8 else {
        "minimum": 0.25, "maximum": 0.30, "unit": "mmol", "raw_text": "0.25-0.30 mmol"
    }
    allene_amounts = [field("reaction_scale", scale_value, ev(3))]
    ket_eq = 5.0 if entry == 6 else 2.0
    parts = [substrate(allene, evidence, amounts=allene_amounts),
             ketone(ket, evidence, [amount("equivalents", ket_eq, "equiv", ev(3))]),
             catalyst(evidence, 1), benzoquinone(evidence, bq_eq)]
    solvent_text = "HOAc:CH3CN = 1:1" if entry == 8 else "HOAc"
    if entry == 8:
        parts += [solvent("acetic_acid", "HOAc", "acetic acid", "CC(=O)O", evidence),
                  solvent("acetonitrile", "CH3CN", "acetonitrile", "CC#N", evidence)]
    else:
        parts.append(solvent("acetic_acid", "HOAc", "acetic acid", "CC(=O)O", evidence, 1.5))
    parts.append(product(prod_label, evidence))
    ids = [p["entity_id"] for p in parts if p["role"] != "product"]
    temperature = 50 if entry == 6 else temp_range
    steps = [reaction_step(ids, evidence, hours, temperature, solvent_text,
                           [field("operation", "stirred and monitored by TLC under Condition C", ev(4))])]
    outcomes = yield_outcome(yld, ev(3), isolated=True)
    unresolved = ["No supporting information was explicitly associated.", "The source gives alternative Workup A/B procedures but does not assign one to this scope row.", "Atmosphere and product SMILES are not reported/encoded."]
    if entry == 9:
        parts.append(participant("byproduct", "product", "Z-4cc", ev(3),
                                 "homodimerization monohydrolysis product of 1c", None, []))
        outcomes += yield_outcome(15, ev(3), product_id="byproduct", isolated=True)
        unresolved.append("The exact procedure for formation/isolation of the 15% Z-4cc byproduct is not separately detailed in the main text.")
    records.append(record(f"table3_entry_{entry:02d}", f"Table 3 entry {entry}", "substrate_scope_entry",
                          evidence, parts, steps, outcomes, unresolved=unresolved))


# Four explicitly described no-product scope experiments on page 3.
failure_specs = [
    (1, "N-benzyl 2,3-dodecadienamide", None, "2d", "standard ketone 2d"),
    (2, "N-benzyl 2-methyl-4-phenyl-2,3-butadienamide", None, "2d", "standard ketone 2d"),
    (3, "1b", "1b", None, "3-benzyl-3,4-pentadien-2-one"),
    (4, "1c", "1c", None, "1-(p-phenyl)phenyl-1,2-octadien-4-one"),
]
for idx, allene_name, known_allene, known_ketone, other_ketone_name in failure_specs:
    evidence = ev(3) + ev(4)
    if known_allene:
        p_allene = substrate(known_allene, evidence, amounts=[])
    else:
        p_allene = participant("allene_substrate", "reactant", allene_name, evidence, allene_name, None, [])
    if known_ketone:
        p_ket = ketone(known_ketone, evidence, [amount("equivalents", 2.0, "equiv", ev(3))])
    else:
        p_ket = participant("ketone_substrate", "reactant", other_ketone_name, evidence,
                            other_ketone_name, None, [amount("equivalents", 2.0, "equiv", ev(3))])
    parts = [p_allene, p_ket, catalyst(evidence, 1), benzoquinone(evidence, 1.0),
             solvent("acetic_acid", "HOAc", "acetic acid", "CC(=O)O", evidence, 1.5),
             product("expected heterodimerization product", evidence)]
    ids = [p["entity_id"] for p in parts if p["role"] != "product"]
    steps = [reaction_step(ids, evidence, solvent_text="HOAc",
                           extra=[field("operation", "treated under the standard Condition C conditions and analyzed by TLC", ev(3))])]
    outcomes = [field("product_detection", "not detected by TLC", ev(3), ["product"])]
    records.append(record(f"scope_failure_{idx:02d}", f"page 3 failed scope example {idx}",
                          "reported_experiment", evidence, parts, steps, outcomes,
                          unresolved=["No supporting information was explicitly associated.", "Reaction time, exact temperature, expected-product structure, and experiment-specific workup are not reported.", "No numerical yield is reported; the qualitative TLC result is preserved."]))


# Page 4 Scheme 2 mechanistic arrows, explicitly not experimental records.
e4 = ev(4)
records.append(record(
    "scheme2_arrow_coordination_oxypalladation", "Scheme 2: 1+2 to 5", "mechanism", e4,
    [participant("generic_allenamide_1", "reactant", "1", e4, "generic 2,3-allenamide", None),
     participant("generic_ketone_2", "reactant", "2", e4, "generic 1,2-allenyl ketone", None),
     participant("pd_ii", "catalyst", "Pd(II)", e4, "palladium(II) species", None),
     participant("intermediate_5", "product", "5", e4, "depicted palladium intermediate", None)],
    [reaction_step(["generic_allenamide_1", "generic_ketone_2", "pd_ii"], e4,
                   extra=[field("operation", "coordination followed by double cyclic oxypalladation to form intermediate 5", e4)])],
    unresolved=["Plausible mechanism, not a reported experiment; generic R groups and ligands remain unspecified."],
))
records.append(record(
    "scheme2_arrow_reductive_elimination", "Scheme 2: 5 to 3", "mechanism", e4,
    [participant("intermediate_5", "reactant", "5", e4, "depicted palladium intermediate", None),
     participant("generic_product_3", "product", "3", e4, "generic 4-(furan-3-yl)furanimine", None),
     participant("pd_0", "product", "Pd(0)Ln", e4, "palladium(0) species", None)],
    [reaction_step(["intermediate_5"], e4,
                   extra=[field("operation", "reductive elimination gives product 3 and Pd(0)", e4)])],
    unresolved=["Plausible mechanism, not a reported experiment; no kinetic or yield data are supplied for this elementary step."],
))
records.append(record(
    "scheme2_arrow_palladium_reoxidation", "Scheme 2: Pd(0) to Pd(II)", "mechanism", e4,
    [participant("pd_0", "reactant", "Pd(0)Ln", e4, "palladium(0) species", None),
     participant("benzoquinone", "reagent", "BQ", e4, "1,4-benzoquinone", "O=C1C=CC(=O)C=C1", []),
     participant("protons", "reagent", "2 H+", e4, "two protons", "[H+]", [amount("stoichiometry", 2, "equiv", e4)]),
     participant("pd_ii", "product", "PdCl2Ln", e4, "palladium(II) species", None),
     participant("hydroquinone", "product", "hydroquinone", e4, "hydroquinone", "Oc1ccc(O)cc1", [])],
    [reaction_step(["pd_0", "benzoquinone", "protons"], e4,
                   extra=[field("operation", "benzoquinone/proton reoxidation of Pd(0) to catalytically active Pd(II)", e4)])],
    unresolved=["Plausible catalytic-cycle step, not a reported standalone experiment; ligand identity is generic."],
))


assert len(records) == 43, len(records)
ids = [r["record_id"] for r in records]
assert len(ids) == len(set(ids))


def ids_with(prefixes):
    return [r["record_id"] for r in records if any(r["record_id"].endswith(p) for p in prefixes)]


page2_ids = [r["record_id"] for r in records if any(x in r["record_id"] for x in ("scheme1_", "table1_", "table2_"))]
page3_ids = [shared_z3ba_id] + [r["record_id"] for r in records if "table3_entry_" in r["record_id"] or "scope_failure_" in r["record_id"]]
page4_ids = [r["record_id"] for r in records if (
    "table1_" in r["record_id"] or "table3_entry_" in r["record_id"] or
    r["record_id"] == shared_z3ba_id or "scope_failure_" in r["record_id"] or "scheme2_" in r["record_id"]
)]

coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1,
            "state": "attempted",
            "regions": [
                {"region": "graphical abstract reaction arrow beneath title", "finding": "General current-work transformation (generic allenamide 1 + allenyl ketone 2 to furanimine 3); classified as general_scheme, not an individual experiment.", "evidence_ids": [f"{DOC}:page1:image"]},
                {"region": "abstract and Introduction/Results opening columns", "finding": "Narrative context and citations to prior work; no row-level reported experiment on this page.", "evidence_ids": [f"{DOC}:page1:image"]},
            ],
            "record_ids": [f"{DOC}:graphical_abstract_general_scheme"],
            "unresolved": ["Generic R groups, additive, solvent, time, temperature, and yield are not specified in the graphical abstract."],
        },
        {
            "page": 2,
            "state": "attempted",
            "regions": [
                {"region": "Scheme 1, upper-left", "finding": "Three arrows depict prior-work Pd(0) coupling/cyclization pathways; classified as literature_example records, not experiments newly reported here.", "evidence_ids": [f"{DOC}:page2:image"]},
                {"region": "Table 1, left-center", "finding": "Seven optimization/table rows extracted independently, with Condition A/B footnotes applied and page-4 procedures linked.", "evidence_ids": [f"{DOC}:page2:image"]},
                {"region": "Figure 1, upper-right", "finding": "ORTEP characterization of Z-3aa; same product as Table 1 entries 1-2, not a separate reaction experiment.", "evidence_ids": [f"{DOC}:page2:image"]},
                {"region": "Table 2, right-center", "finding": "Eleven independent optimization rows extracted, including three zero-yield/no-product conditions; entry 9 linked to Table 3 entry 1 and the explicit page-4 procedure rather than duplicated.", "evidence_ids": [f"{DOC}:page2:image"]},
                {"region": "discussion prose below tables", "finding": "Narrative confirms O-attack products, isolated-yield optimization trends, and qualitative failures already mapped to table rows.", "evidence_ids": [f"{DOC}:page2:image"]},
            ],
            "record_ids": page2_ids,
            "unresolved": ["Table 1 prints the n-Bu ketone as 3d although the paper's ketone series elsewhere uses 2d.", "The explicit Condition A amounts and Table 1 Condition A equivalents are internally inconsistent; values were retained, not repaired.", "Most product structures are compact drawings and remain without SMILES."],
        },
        {
            "page": 3,
            "state": "attempted",
            "regions": [
                {"region": "Table 3 and reaction header, upper half", "finding": "Fifteen substrate-scope rows checked; entry 1 is the same Z-3ba experiment as Table 2 entry 9, leaving fourteen new row records plus the shared record.", "evidence_ids": [f"{DOC}:page3:image"]},
                {"region": "scope-limitations prose, lower-left", "finding": "Four distinct substrate combinations with no expected product by TLC extracted as qualitative failed experiments.", "evidence_ids": [f"{DOC}:page3:image"]},
                {"region": "Eq. 1, lower-right", "finding": "Table 3 entry 9 cross-product Z-3cd (76%) and concurrent homodimerization/monohydrolysis byproduct Z-4cc (15%) stored in one experiment with product-specific outcomes.", "evidence_ids": [f"{DOC}:page3:image"]},
                {"region": "Figure 2, center-right", "finding": "ORTEP characterization of Z-4cc supports the byproduct identity; not a separate reaction experiment.", "evidence_ids": [f"{DOC}:page3:image"]},
            ],
            "record_ids": page3_ids,
            "unresolved": ["The source does not assign Workup A or B to most Table 3 rows.", "Four failed scope examples lack time, exact temperature, numerical yield, and expected-product structures.", "SI is mentioned as available but was not provided or explicitly associated."],
        },
        {
            "page": 4,
            "state": "attempted",
            "regions": [
                {"region": "Scheme 2, upper-left", "finding": "Plausible catalytic cycle split into three mechanism records (oxypalladation, reductive elimination, and Pd reoxidation), none treated as an experiment.", "evidence_ids": [f"{DOC}:page4:image"]},
                {"region": "Condition A/B general procedure and Z-3aa examples, lower-left to upper-right", "finding": "General isolation steps linked to all Table 1 rows; explicit Z-3aa Condition A/B quantities linked to Table 1 entries 1 and 2 without duplication.", "evidence_ids": [f"{DOC}:page4:image"]},
                {"region": "Condition C procedure and Z-3ba example, right column", "finding": "Condition C/TLC context linked to scope/failure records; explicit Workup A and quantities linked to the shared Table 2 entry 9/Table 3 entry 1 Z-3ba record.", "evidence_ids": [f"{DOC}:page4:image"]},
                {"region": "Supporting Information Available statement, bottom-right", "finding": "SI availability is stated, but no SI file was provided; association remains unestablished and no missing details were inferred.", "evidence_ids": [f"{DOC}:page4:image"]},
            ],
            "record_ids": page4_ids,
            "unresolved": ["Condition C offers alternative Workup A/B procedures but gives no row-by-row assignment except explicit Z-3ba Workup A.", "Atmosphere is not reported.", "SI was not supplied, so product-specific procedures outside Z-3aa/Z-3ba remain incomplete."],
        },
    ],
}

assert [p["page"] for p in coverage["pages"]] == [1, 2, 3, 4]
assert all(p["regions"] for p in coverage["pages"])
assert set(rid for p in coverage["pages"] for rid in p["record_ids"]) <= set(ids)

RAW.parent.mkdir(parents=True, exist_ok=True)
COVERAGE.parent.mkdir(parents=True, exist_ok=True)
RAW.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
COVERAGE.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

tasks_path = BASE / "tasks.json"
tasks = json.loads(tasks_path.read_text())
for task in tasks:
    if task.get("document_id") == DOC and task.get("evidence_id") in {f"{DOC}:page{p}:text" for p in range(1, 5)}:
        task["state"] = "attempted"
        task["visual_evidence_id"] = task.get("visual_evidence_id") or task["evidence_id"].replace(":text", ":image")
        task["reason"] = "Original page image and page text inspected; findings and record IDs are logged in coverage/pages_0001_0004.json."
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"records": len(records), "raw": str(RAW), "coverage": str(COVERAGE)}, ensure_ascii=False))
