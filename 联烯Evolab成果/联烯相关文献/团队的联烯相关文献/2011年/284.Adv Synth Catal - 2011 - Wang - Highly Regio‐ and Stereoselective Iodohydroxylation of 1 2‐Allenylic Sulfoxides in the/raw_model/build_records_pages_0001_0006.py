"""Build machine-extracted records for PDF pages 1--6.

This is a reproducible serialization of the visual/page-text extraction.  It is
not a chemistry review: merge will retain every record as needs_review.
"""
from __future__ import annotations

import json
from pathlib import Path


DOC = "doc_f68af135ec78d163"
OUT = Path(__file__).with_name("records_pages_0001_0006.json")


def ev(page: int) -> list[str]:
    return [f"{DOC}:page{page}:image", f"{DOC}:page{page}:text"]


def fact(value, evidence=None):
    return {
        "value": value,
        "evidence_ids": list(evidence or []) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def qty(number, unit, **extra):
    value = {"number": number, "unit": unit}
    value.update(extra)
    return value


def fld(name, value, evidence, targets=None):
    item = {"name": name, "fact": fact(value, evidence)}
    if targets:
        item["target_entity_ids"] = list(targets)
    return item


SMILES = {
    "I2": "II",
    "H2O": "O",
    "MeCN": "CC#N",
    "BnSH": "SCC1=CC=CC=C1",
    "BnSSBn": "C(c1ccccc1)SSCc1ccccc1",
    "CH2Cl2": "ClCCl",
    "acetone": "CC(=O)C",
    "toluene": "Cc1ccccc1",
    "nitromethane": "C[N+](=O)[O-]",
    "DMF": "CN(C)C=O",
    "water": "O",
    "m-CPBA": "OOC(=O)c1cccc(Cl)c1",
    "1-hexyne": "CCCCC#C",
    "phenylboronic acid": "OB(O)c1ccccc1",
    "triethylamine": "CCN(CC)CC",
    "DMSO": "CS(C)=O",
    "DME": "COCCOC",
    "sodium carbonate": "[Na+].[Na+].[O-]C([O-])=O",
}


def participant(entity_id, role, label, evidence, amounts=None, name=None, smiles_key=None):
    smiles = SMILES.get(smiles_key or label)
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence) if name else fact(None),
        "smiles": fact(smiles, evidence) if smiles else fact(None),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": amounts or [],
    }


def record(suffix, page, kind, participants=None, steps=None, outcomes=None, notes=None,
           extra_evidence=None, unresolved=None):
    evidence = ev(page) + list(extra_evidence or [])
    return {
        "record_id": f"{DOC}:{suffix}",
        "document_id": DOC,
        "source_reaction_id": suffix,
        "record_kind": kind,
        "status": "needs_review",
        "completeness": "partial",
        "evidence_ids": list(dict.fromkeys(evidence)),
        "participants": participants or [],
        "steps": steps or [],
        "outcomes": outcomes or [],
        "notes": [fact(x, evidence) for x in (notes or [])],
        "review": {
            "method": "model",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": (unresolved or []) + [
                "Machine extraction requires source review; molecular structures are not independently verified.",
                "Supporting information was mentioned by the article but was not explicitly supplied or associated.",
            ],
        },
    }


def reaction_step(ids, evidence, temperature=None, time=None, solvent=None, workup=None, operation=None):
    conditions = []
    if temperature is not None:
        conditions.append(fld("temperature", temperature, evidence))
    if time is not None:
        conditions.append(fld("time", time, evidence))
    if solvent is not None:
        conditions.append(fld("solvent", solvent, evidence))
    if operation is not None:
        conditions.append(fld("operation", operation, evidence))
    if workup is not None:
        conditions.append(fld("workup", workup, evidence))
    return {"step_id": "reaction", "participant_ids": ids, "conditions": conditions}


records = []

# Page 1: distinguish cited prior chemistry from the current generic scheme.
e = ev(1)
records.append(record(
    "scheme1_prior_halohydroxylation", 1, "literature_example",
    participants=[
        participant("generic_1", "reactant", "generic 1,2-allenyl sulfoxide 1", e),
        participant("iodine", "reagent", "I2", e),
        participant("generic_4", "product", "3-phenylsulfinyl-2-iodo-2(E)-alkenol 4", e),
    ],
    steps=[reaction_step(["generic_1", "iodine", "generic_4"], e, solvent=None, operation="H2O; prior work, ref. 4")],
    notes=["Lower-left branch of Scheme 1 is explicitly attributed to reference 4 and is not a new batch experiment in this paper."],
    unresolved=["Generic R1/R2/R3 structures cannot be expanded to unique molecules."],
))
records.append(record(
    "scheme1_current_generic_route", 1, "general_scheme",
    participants=[
        participant("generic_1", "reactant", "generic 1,2-allenyl sulfoxide 1", e),
        participant("iodine", "reagent", "I2", e),
        participant("bnsh", "reagent", "BnSH", e),
        participant("generic_2", "product", "five-membered charged intermediate 2", e),
        participant("generic_3", "product", "3-hydroxy-2-iodo-2(E)-alkenyl sulfide 3", e),
    ],
    steps=[reaction_step(["generic_1", "iodine", "bnsh", "generic_2", "generic_3"], e, operation="generic sequence shown in Scheme 1")],
    notes=["Scheme 1 summarizes the current report and does not state a single batch yield."],
    unresolved=["Generic R1/R2/R3 structures and batch-specific conditions are not specified."],
))
records.append(record(
    "eq1_1a_iodohydroxylation", 1, "reported_experiment",
    participants=[
        participant("substrate_1a", "reactant", "1,2-propadienyl phenyl sulfoxide 1a", e,
                    [fld("equivalents", qty(1, "equiv"), e)]),
        participant("bnsh", "reagent", "BnSH", e, [fld("equivalents", qty(1, "equiv"), e)]),
        participant("iodine", "reagent", "I2", e, [fld("equivalents", qty(1.5, "equiv"), e)]),
        participant("mecn", "solvent", "MeCN", e, smiles_key="MeCN"),
        participant("product_3a", "product", "3a (E-3a/Z-3a mixture)", e),
    ],
    steps=[reaction_step(["substrate_1a", "bnsh", "iodine", "mecn", "product_3a"], e,
                         qty(5, "°C"), qty(2, "h"), "commercially available MeCN")],
    outcomes=[
        fld("reported_yield_3a", qty(53, "%"), e, ["product_3a"]),
        fld("E_Z_ratio_3a", "96/4", e, ["product_3a"]),
        fld("selectivity_measurement_basis", "E-3a stereochemistry determined by NOE; ratio basis not stated on page 1", e),
    ],
    unresolved=["The page-1 scheme gives equivalents but not reaction scale, workup, or yield measurement basis."],
))


# Page 2: Table 1, one record per optimization row.
table1 = [
    (1, "A", "MeCN", 5, 60, 10, "30/70", 3, True, None),
    (2, "B", "MeCN", 5, 10, 31, "61/39", 3, True, None),
    (3, "B", "MeCN", -10, 30, 45, "76/24", 11, True, None),
    (4, "B", "MeCN", -20, 42, 58, "91/9", 13, True, None),
    (5, "B", "MeCN", -20, 42, 4, ">99/1", 63, False, None),
    (6, "B", "MeCN", -40, 60, 47, "96/4", 33, True, None),
    (7, "B", "CH2Cl2", -20, 60, 35, "table dash (–)", "table dash (–)", True, None),
    (8, "B", "toluene", -20, 60, 72, "89/11", 6, True, None),
    (9, "B", "acetone", -20, 30, 57, "81/19", 9, True, None),
    (10, "B", "CH3NO2", -20, 30, 71, "92/8", 17, True, None),
    (11, "B", "dioxane", "r.t.", 42, 62, "97/3", 10, True, None),
    (12, "B", "DMF", -20, 90, 0, "0", 0, True, None),
    (13, "B", "MeCN/H2O", -20, 42, 72, ">99/1", 16, True, 2.0),
]
for row, cond, solvent, temp, minutes, y3, ratio, y4, has_bnsh, water_eq in table1:
    e = ev(2)
    ps = [
        participant("substrate_1f", "reactant", "octa-1,2-dienyl phenyl sulfoxide 1f", e,
                    [fld("amount", qty(0.4, "mmol"), e)]),
        participant("iodine", "reagent", "I2", e,
                    [fld("amount", qty(0.6, "mmol"), e), fld("equivalents", qty(1.5, "equiv"), e)]),
    ]
    if has_bnsh:
        ps.append(participant("bnsh", "reagent", "BnSH", e, [fld("amount", qty(0.4, "mmol"), e)]))
    solvent_label = {"CH3NO2": "nitromethane", "MeCN/H2O": "anhydrous MeCN"}.get(solvent, solvent)
    solvent_key = {"MeCN": "MeCN", "CH2Cl2": "CH2Cl2", "CH3NO2": "nitromethane", "MeCN/H2O": "MeCN"}.get(solvent, solvent_label)
    volumes = ([fld("initial_solvent_volume", qty(4 if cond == "A" else 3, "mL"), e),
                fld("addition_solution_solvent_volume", qty(2 if cond == "A" else 3, "mL"), e)])
    ps.append(participant("solvent", "solvent", solvent_label, e, volumes, smiles_key=solvent_key))
    if water_eq is not None:
        ps.append(participant("water_additive", "reagent", "H2O", e,
                              [fld("equivalents", qty(water_eq, "equiv"), e)], smiles_key="H2O"))
    ps += [
        participant("product_3f", "product", "3f (E/Z mixture)", e),
        participant("product_E4f", "product", "E-4f", e),
        participant("quench_water", "reagent", "H2O (quench)", e,
                    [fld("volume", qty(6, "mL"), e)], smiles_key="H2O"),
        participant("sodium_thiosulfate", "reagent", "saturated aqueous Na2S2O3", e),
    ]
    ids = [p["entity_id"] for p in ps]
    outcomes = [
        fld("NMR_yield_3f", qty(y3, "%") if isinstance(y3, (int, float)) else y3, e, ["product_3f"]),
        fld("E_Z_ratio_3f", ratio, e, ["product_3f"]),
        fld("NMR_yield_E4f", qty(y4, "%") if isinstance(y4, (int, float)) else y4, e, ["product_E4f"]),
        fld("yield_measurement_basis", "1H NMR with CH2Br2 as internal standard", e),
    ]
    notes = [f"Table 1 entry {row}; Conditions {cond}."]
    if not has_bnsh:
        notes.append("Footnote c: reaction conducted in the absence of BnSH.")
    if row == 13:
        notes.append("Footnote d: anhydrous MeCN and 2.0 equivalents H2O were used.")
    records.append(record(
        f"table1_entry{row}", 2, "optimization_entry", ps,
        [reaction_step(ids, e, temp if isinstance(temp, str) else qty(temp, "°C"), qty(minutes, "min"), solvent_label,
                       "quenched with H2O; then saturated aqueous Na2S2O3 (0 °C stated for Conditions B)")],
        outcomes, notes,
        unresolved=["Structures for 1f, 3f, and E-4f were read as labels but stereochemical structures remain unverified."],
    ))

# Two prose-only condition tests adjacent to Table 1.
e = ev(2)
records.append(record(
    "prose_anhydrous_mecn_selectivity_test", 2, "optimization_entry",
    participants=[
        participant("substrate_1f", "reactant", "octa-1,2-dienyl phenyl sulfoxide 1f", e),
        participant("mecn", "solvent", "anhydrous MeCN", e, smiles_key="MeCN"),
        participant("product_3f", "product", "3f (E/Z mixture)", e),
    ],
    steps=[reaction_step(["substrate_1f", "mecn", "product_3f"], e, operation="comparison using MeCN distilled from CaH2 after refluxing 5 h")],
    outcomes=[fld("E_Z_ratio_3f", "77/23", e, ["product_3f"])],
    notes=["The prose compares this result with 91/9 obtained under the corresponding commercial-MeCN condition."],
    unresolved=["Exact reagent amounts, temperature, time, yield, and workup are not restated for this prose comparison."],
))
records.append(record(
    "prose_water_10equiv_no_reaction", 2, "optimization_entry",
    participants=[
        participant("substrate_1f", "reactant", "octa-1,2-dienyl phenyl sulfoxide 1f", e),
        participant("water", "reagent", "H2O", e, [fld("equivalents", qty(10, "equiv"), e)], smiles_key="H2O"),
        participant("recovered_1f", "product", "recovered 1f", e),
    ],
    steps=[reaction_step(["substrate_1f", "water", "recovered_1f"], e, operation="water-loading test")],
    outcomes=[
        fld("reaction_outcome", "no reaction", e),
        fld("recovered_starting_material_yield", qty(73, "%"), e, ["recovered_1f"]),
    ],
    unresolved=["Other reagents, temperature, time, solvent volume, and recovery measurement basis are not restated."],
))


# Page 3: Table 2 substrate scope.
table2 = [
    (1, "H", "1a", 120, 47, ">99/1", "E-3a"),
    (2, "CH3", "1b", 34, 70, "96/4", "E-3b"),
    (3, "C2H5", "1c", 44, 77, "97/3", "E-3c"),
    (4, "i-C3H7", "1d", 33, 75, "97/3", "E-3d"),
    (5, "n-C4H9", "1e", 31, 67, "99/1", "E-3e"),
    (6, "n-C5H11", "1f", 44, 72, ">99/1", "E-3f"),
    (7, "n-C6H13", "1g", 49, 81, "99/1", "E-3g"),
    (8, "n-C7H15", "1h", 91, 65, ">99/1", "E-3h"),
    (9, "n-C8H17", "1i", 61, 71, "95/5", "E-3i"),
    (10, "n-C9H19", "1j", 52, 77, "96/4", "E-3j"),
    (11, "Ph", "1k", 45, 74, ">99/1", "E-3k"),
]
for row, rgroup, substrate, minutes, yld, ratio, product in table2:
    e = ev(3)
    evidence = e + (ev(2) if row == 1 else [])
    ps = [
        participant("substrate", "reactant", f"1,2-allenyl sulfoxide {substrate} (R={rgroup})", evidence,
                    [fld("amount", qty(0.4, "mmol"), evidence)]),
        participant("bnsh", "reagent", "BnSH", evidence, [fld("amount", qty(0.4, "mmol"), evidence)]),
        participant("iodine", "reagent", "I2", evidence,
                    [fld("amount", qty(0.6, "mmol"), evidence), fld("equivalents", qty(1.5, "equiv"), evidence)]),
        participant("mecn", "solvent", "anhydrous MeCN", evidence,
                    [fld("total_volume", qty(6, "mL"), evidence)], smiles_key="MeCN"),
        participant("product_E3", "product", product, evidence),
    ]
    temperature = qty(-20, "°C")
    if row == 1:
        temperature = qty(5, "°C")
    else:
        ps.append(participant("water", "reagent", "H2O", evidence,
                              [fld("amount", qty(0.8, "mmol"), evidence),
                               fld("equivalents", qty(2, "equiv"), evidence),
                               fld("volume", qty(14.4, "uL"), evidence)], smiles_key="H2O"))
    ids = [p["entity_id"] for p in ps]
    notes = [f"Table 2 entry {row}."]
    if row == 1:
        notes.append("Footnote e: Conditions A were used with anhydrous MeCN; page 2 supplies the Conditions A operation.")
    records.append(record(
        f"table2_entry{row}_{substrate}", 3, "substrate_scope_entry", ps,
        [reaction_step(ids, evidence, temperature, qty(minutes, "min"), "anhydrous MeCN",
                       "quenched with 6 mL H2O at reaction temperature, then saturated aqueous Na2S2O3 at 0 °C")],
        [
            fld("isolated_yield_E3", qty(yld, "%"), evidence, ["product_E3"]),
            fld("E_Z_ratio_3", ratio, evidence, ["product_E3"]),
            fld("selectivity_measurement_basis", "1H NMR analysis using CH2Br2 as internal standard", evidence),
        ], notes, extra_evidence=ev(2) if row == 1 else None,
        unresolved=["Product label is source-read; full stereochemical structure is not independently verified."],
    ))


# Page 3: Table 3 optimization of 1l.
table3 = [
    (1, 1.5, -20, 2.0, 17, 34, None, "43/57", 25, None, None),
    (2, 1.5, -40, 2.0, 17, 64, None, "94/6", 34, None, None),
    (3, 1.5, -40, 5.0, 17, 52, None, ">99/1", 30, None, None),
    (4, 1.5, -40, 10.0, 11, 59, None, ">99/1", 34, None, None),
    (5, 1.2, -40, 10.0, 46, 65, 67, ">99/1", 28, 24, None),
    (6, 1.2, -40, 10.0, 21, 66, None, "97/3", 15, None, "quenched with H2O at 0 °C"),
    (7, 1.2, -40, 10.0, 41, 42, None, ">99/1", 0, None, "quenched directly with saturated aqueous Na2S2O3 at -40 °C"),
]
for row, i2eq, temp, h2oeq, minutes, y3_nmr, y3_iso, ratio, y4_nmr, y4_iso, exception in table3:
    e = ev(3)
    ps = [
        participant("substrate_1l", "reactant", "3,3-pentamethylenepropadienyl phenyl sulfoxide 1l", e,
                    [fld("amount", qty(0.4, "mmol"), e)]),
        participant("bnsh", "reagent", "BnSH", e, [fld("amount", qty(0.4, "mmol"), e)]),
        participant("water", "reagent", "H2O", e, [fld("equivalents", qty(h2oeq, "equiv"), e)], smiles_key="H2O"),
        participant("iodine", "reagent", "I2", e,
                    [fld("equivalents", qty(i2eq, "equiv"), e), fld("solution_volume", qty(1.8, "mL"), e)]),
        participant("mecn", "solvent", "anhydrous MeCN", e,
                    [fld("substrate_solution_volume", qty(4.2, "mL"), e),
                     fld("iodine_solution_volume", qty(1.8, "mL"), e)], smiles_key="MeCN"),
        participant("product_E3l", "product", "E-3l", e),
        participant("product_Z3l", "product", "Z-3l", e),
        participant("product_E4l", "product", "E-4l", e),
    ]
    if row == 7:
        ps.append(participant("recovered_1l", "product", "recovered 1l", e))
    ids = [p["entity_id"] for p in ps]
    workup = exception or "quenched with 6 mL H2O, then saturated aqueous Na2S2O3 at 0 °C"
    outcomes = [
        fld("NMR_yield_E3l", qty(y3_nmr, "%"), e, ["product_E3l"]),
        fld("E_Z_ratio_3l", ratio, e, ["product_E3l", "product_Z3l"]),
        fld("NMR_yield_E4l", qty(y4_nmr, "%"), e, ["product_E4l"]),
        fld("NMR_yield_measurement_basis", "CH2Br2 internal standard", e),
    ]
    if y3_iso is not None:
        outcomes.append(fld("isolated_yield_E3l", qty(y3_iso, "%"), e, ["product_E3l"]))
    if y4_iso is not None:
        outcomes.append(fld("isolated_yield_E4l", qty(y4_iso, "%"), e, ["product_E4l"]))
    if row == 7:
        outcomes.append(fld("recovered_starting_material_yield", qty(42, "%"), e, ["recovered_1l"]))
    records.append(record(
        f"table3_entry{row}", 3, "optimization_entry", ps,
        [reaction_step(ids, e, qty(temp, "°C"), qty(minutes, "min"), "anhydrous MeCN", workup)],
        outcomes, [f"Table 3 entry {row}."],
        unresolved=["Structures and E/Z assignments are not independently verified; saturated Na2S2O3 volume is not stated."],
    ))


# Page 4: Table 4 substrate scope.
table4 = [
    (1, "H", "CH3", "CH3", "1m", 15, 60, "E-3m", 1.2),
    (2, "H", "C2H5", "C2H5", "1n", 20, 71, "E-3n", 1.2),
    (3, "H", "C2H5", "Ph", "1o", 30, 64, "E-3o", 1.5),
    (4, "H", "CH3", "i-C4H9", "1p", 20, 67, "E-3p", 1.2),
    (5, "H", "CH3", "C2H5", "1q", 20, 63, "E-3q", 1.2),
    (6, "H", "CH3", "n-C3H7", "1r", 21, 69, "E-3r", 1.2),
    (7, "H", "CH3", "Ph", "1s", 21, 62, "E-3s", 1.2),
    (8, "n-C4H9", "CH3", "CH3", "1t", 19, 66, "E-3t", 1.2),
]
for row, r1, r2, r3, substrate, minutes, yld, product, i2eq in table4:
    e = ev(4)
    iodine_amounts = [fld("equivalents", qty(i2eq, "equiv"), e), fld("solution_volume", qty(1.8, "mL"), e)]
    if row != 3:
        iodine_amounts.append(fld("amount", qty(0.48, "mmol"), e))
    ps = [
        participant("substrate", "reactant", f"poly-substituted 1,2-allenyl sulfoxide {substrate} (R1={r1}, R2={r2}, R3={r3})", e,
                    [fld("amount", qty(0.4, "mmol"), e)]),
        participant("bnsh", "reagent", "BnSH", e, [fld("amount", qty(0.4, "mmol"), e), fld("equivalents", qty(1, "equiv"), e)]),
        participant("water", "reagent", "H2O", e,
                    [fld("amount", qty(4, "mmol"), e), fld("volume", qty(72, "uL"), e),
                     fld("equivalents", qty(10, "equiv"), e)], smiles_key="H2O"),
        participant("iodine", "reagent", "I2", e, iodine_amounts),
        participant("mecn", "solvent", "anhydrous MeCN", e,
                    [fld("substrate_solution_volume", qty(4.2, "mL"), e),
                     fld("iodine_solution_volume", qty(1.8, "mL"), e)], smiles_key="MeCN"),
        participant("product_E3", "product", product, e),
    ]
    ids = [p["entity_id"] for p in ps]
    records.append(record(
        f"table4_entry{row}_{substrate}", 4, "substrate_scope_entry", ps,
        [reaction_step(ids, e, qty(-40, "°C"), qty(minutes, "min"), "anhydrous MeCN",
                       "after TLC completion, quenched with 6 mL H2O at -40 °C; saturated aqueous Na2S2O3 at 0 °C")],
        [
            fld("isolated_yield_E3", qty(yld, "%"), e, ["product_E3"]),
            fld("E_Z_ratio_3", ">99/1", e, ["product_E3"]),
            fld("selectivity_measurement_basis", "1H NMR analysis using CH2Br2 as internal standard", e),
        ], [f"Table 4 entry {row}."],
        unresolved=["Substituent-defined structures were not converted into independently verified SMILES."],
    ))


# Page 4: Scheme 2 control experiments, one record per arrow.
scheme2 = [
    ("i2_only", [("iodine", "reagent", "I2")], "no reaction", None),
    ("bnsh_only", [("bnsh", "reagent", "BnSH")], "no reaction", None),
    ("bnsh_i2", [("bnsh", "reagent", "BnSH"), ("iodine", "reagent", "I2")], None,
     [("yield_E3a", 18, "product_E3a"), ("recovered_starting_material_yield", 78, "recovered_E4a"),
      ("yield_BnSSBn", 100, "product_BnSSBn")]),
    ("bnssbn_i2", [("bnssbn", "reagent", "BnSSBn"), ("iodine", "reagent", "I2")], "no reaction", None),
    ("bnssbn_only", [("bnssbn", "reagent", "BnSSBn")], "no reaction", None),
]
for suffix, agents, no_reaction, product_data in scheme2:
    e = ev(4)
    ps = [
        participant("substrate_E4a", "reactant", "E-4a", e),
        participant("water", "reagent", "H2O", e, [fld("equivalents", qty(2, "equiv"), e)], smiles_key="H2O"),
        participant("mecn", "solvent", "anhydrous MeCN", e, smiles_key="MeCN"),
    ]
    for entity_id, role, label in agents:
        ps.append(participant(entity_id, role, label, e, smiles_key=label))
    outcomes = []
    if no_reaction:
        outcomes.append(fld("reaction_outcome", no_reaction, e))
    else:
        ps += [
            participant("product_E3a", "product", "E-3a", e),
            participant("recovered_E4a", "product", "recovered E-4a", e),
            participant("product_BnSSBn", "product", "BnSSBn", e, smiles_key="BnSSBn"),
        ]
        for name, number, target in product_data:
            outcomes.append(fld(name, qty(number, "%"), e, [target]))
    ids = [p["entity_id"] for p in ps]
    records.append(record(
        f"scheme2_control_{suffix}", 4, "reported_experiment", ps,
        [reaction_step(ids, e, qty(5, "°C"), qty(2, "h"), "anhydrous MeCN")],
        outcomes, [f"Scheme 2 control branch: {suffix}."],
        extra_evidence=ev(3) if suffix in {"i2_only", "bnsh_only", "bnsh_i2"} else None,
        unresolved=["Scheme 2 does not state substrate scale, agent equivalents (except water), workup, or yield measurement basis."],
    ))


# Page 5: equations 2--4 and mechanistic Scheme 3.
e = ev(5)
records.append(record(
    "eq2_1a_bnssbn_i2", 5, "reported_experiment",
    participants=[
        participant("substrate_1a", "reactant", "1a", e),
        participant("bnssbn", "reagent", "BnSSBn", e, smiles_key="BnSSBn"),
        participant("iodine", "reagent", "I2", e),
        participant("water", "reagent", "H2O", e, [fld("equivalents", qty(2, "equiv"), e)], smiles_key="H2O"),
        participant("mecn", "solvent", "anhydrous MeCN", e, smiles_key="MeCN"),
        participant("product_E3a", "product", "E-3a", e),
        participant("product_E4a", "product", "E-4a", e),
        participant("recovered_1a", "product", "recovered 1a", e),
    ],
    steps=[reaction_step(["substrate_1a", "bnssbn", "iodine", "water", "mecn", "product_E3a", "product_E4a", "recovered_1a"],
                         e, qty(5, "°C"), qty(2, "h"), "anhydrous MeCN")],
    outcomes=[
        fld("isolated_yield_E3a", qty(13, "%"), e, ["product_E3a"]),
        fld("isolated_yield_E4a", qty(57, "%"), e, ["product_E4a"]),
        fld("recovered_starting_material_yield", qty(25, "%"), e, ["recovered_1a"]),
    ],
    extra_evidence=ev(3) + ev(4),
    unresolved=["Amounts of 1a, BnSSBn, and I2 and workup are not stated in Eq. 2."],
))
records.append(record(
    "eq3_chiral_1g_iodohydroxylation", 5, "reported_experiment",
    participants=[
        participant("substrate_R1g", "reactant", "R-1g", e),
        participant("iodine", "reagent", "I2", e, [fld("equivalents", qty(1.5, "equiv"), e)]),
        participant("bnsh", "reagent", "BnSH", e),
        participant("water", "reagent", "H2O", e, [fld("equivalents", qty(2, "equiv"), e)], smiles_key="H2O"),
        participant("mecn", "solvent", "anhydrous MeCN", e, smiles_key="MeCN"),
        participant("product_RE3g", "product", "(R)-E-3g", e),
    ],
    steps=[reaction_step(["substrate_R1g", "iodine", "bnsh", "water", "mecn", "product_RE3g"],
                         e, qty(-20, "°C"), qty(48, "min"), "anhydrous MeCN")],
    outcomes=[
        fld("reactant_ee", qty(99.4, "%"), e, ["substrate_R1g"]),
        fld("isolated_yield_RE3g", qty(78, "%"), e, ["product_RE3g"]),
        fld("product_ee", qty(98.5, "%"), e, ["product_RE3g"]),
    ],
    unresolved=["Reaction scale, BnSH amount, workup, and ee measurement method are not shown in Eq. 3."],
))
records.append(record(
    "eq4_RE3g_oxidation", 5, "reported_experiment",
    participants=[
        participant("substrate_RE3g", "reactant", "(R)-E-3g", e),
        participant("mcpba", "reagent", "m-CPBA", e, smiles_key="m-CPBA"),
        participant("ch2cl2", "solvent", "CH2Cl2", e, smiles_key="CH2Cl2"),
        participant("product_RE4g", "product", "(R)-E-4g", e),
    ],
    steps=[reaction_step(["substrate_RE3g", "mcpba", "ch2cl2", "product_RE4g"],
                         e, qty(0, "°C"), qty(1, "h"), "CH2Cl2")],
    outcomes=[
        fld("reactant_ee", qty(98.0, "%"), e, ["substrate_RE3g"]),
        fld("isolated_yield_RE4g", qty(83, "%"), e, ["product_RE4g"]),
        fld("product_ee", qty(96.9, "%"), e, ["product_RE4g"]),
    ],
    notes=["Figure 1 on page 6 is an ORTEP representation of (R)-E-4g and supports the assigned product identity."],
    extra_evidence=ev(6),
    unresolved=["Reaction scale, m-CPBA amount, workup, and ee measurement method are not shown in Eq. 4."],
))
records.append(record(
    "scheme3_proposed_mechanism", 5, "mechanism",
    participants=[
        participant("generic_1", "reactant", "generic 1,2-allenyl sulfoxide 1", e),
        participant("iodine", "reagent", "I2", e),
        participant("bnsh", "reagent", "BnSH", e),
        participant("water", "reagent", "H2O", e, smiles_key="H2O"),
        participant("intermediate_2", "product", "five-membered charged intermediate 2", e),
        participant("intermediate_E5", "product", "intermediate E-5", e),
        participant("product_E3", "product", "generic E-3", e),
        participant("product_E4", "product", "generic E-4", e),
        participant("bnssbn", "product", "BnSSBn", e, smiles_key="BnSSBn"),
    ],
    steps=[reaction_step(["generic_1", "iodine", "bnsh", "water", "intermediate_2", "intermediate_E5", "product_E3", "product_E4", "bnssbn"],
                         e, operation="proposed major and minor mechanistic pathways")],
    notes=["Scheme 3 is explicitly a proposed mechanistic rationale, not a batch experiment.",
           "Major path: intermediate 2 reacts with BnSH through E-5 to E-3 and BnSSBn; minor path: water gives E-4, which may be reduced to E-3."],
    unresolved=["Generic substituents and transient intermediate structures are not unique batch molecules."],
))


# Page 6: Table 5 isomerization entries.
table5 = [(1, 0.5, 13, 83, "62/38"), (2, 1.0, 15, 90, "11/89"),
          (3, 1.5, 15, 91, "5/95"), (4, 2.0, 24, 83, "5/95")]
for row, i2eq, hours, yld, ratio in table5:
    e = ev(6)
    ps = [
        participant("substrate_E3a", "reactant", "E-3a", e),
        participant("iodine", "reagent", "I2", e, [fld("equivalents", qty(i2eq, "equiv"), e)]),
        participant("mecn", "solvent", "anhydrous MeCN", e, smiles_key="MeCN"),
        participant("product_3a", "product", "3a (E-3a/Z-3a mixture)", e),
    ]
    records.append(record(
        f"table5_entry{row}", 6, "optimization_entry", ps,
        [reaction_step([p["entity_id"] for p in ps], e, qty(0, "°C"), qty(hours, "h"), "anhydrous MeCN")],
        [
            fld("isolated_yield_3a", qty(yld, "%"), e, ["product_3a"]),
            fld("E_Z_ratio_3a", ratio, e, ["product_3a"]),
            fld("selectivity_measurement_basis", "1H NMR analysis", e),
        ], [f"Table 5 entry {row}."],
        unresolved=["Reaction scale and workup are not given in Table 5."],
    ))

e = ev(6)
records.append(record(
    "eq5_Z3a_isomerization", 6, "reported_experiment",
    participants=[
        participant("substrate_Z3a", "reactant", "Z-3a", e),
        participant("iodine", "reagent", "I2", e, [fld("equivalents", qty(0.5, "equiv"), e)]),
        participant("mecn", "solvent", "anhydrous MeCN", e, smiles_key="MeCN"),
        participant("product_E3a", "product", "E-3a", e),
        participant("product_Z3a", "product", "Z-3a", e),
    ],
    steps=[reaction_step(["substrate_Z3a", "iodine", "mecn", "product_E3a", "product_Z3a"],
                         e, qty(0, "°C"), qty(12, "h"), "anhydrous MeCN")],
    outcomes=[fld("E_Z_ratio_3a", "4/96", e, ["product_E3a", "product_Z3a"])],
    unresolved=["Reaction scale, workup, total material yield, and ratio measurement basis are not stated in Eq. 5."],
))

# Page 6: Scheme 4, one record per product-forming arrow.
records.append(record(
    "scheme4_sonogashira_product6", 6, "reported_experiment",
    participants=[
        participant("substrate_E3f", "reactant", "E-3f", e),
        participant("hexyne", "reactant", "1-hexyne", e, smiles_key="1-hexyne"),
        participant("pd_cat", "catalyst", "Pd(PPh3)2Cl2", e),
        participant("cui", "catalyst", "CuI", e),
        participant("et3n", "reagent", "Et3N", e, smiles_key="triethylamine"),
        participant("dmso", "solvent", "DMSO", e, smiles_key="DMSO"),
        participant("product_6", "product", "product 6", e),
    ],
    steps=[reaction_step(["substrate_E3f", "hexyne", "pd_cat", "cui", "et3n", "dmso", "product_6"],
                         e, qty(40, "°C"), qty(5, "h"), "Et3N/DMSO")],
    outcomes=[fld("isolated_yield_product_6", qty(90, "%"), e, ["product_6"])],
    unresolved=["Scheme 4 does not state scale, reagent/catalyst amounts, workup, or purification."],
))
records.append(record(
    "scheme4_suzuki_product7", 6, "reported_experiment",
    participants=[
        participant("substrate_E3f", "reactant", "E-3f", e),
        participant("phenylboronic", "reactant", "phenylboronic acid", e, smiles_key="phenylboronic acid"),
        participant("pd_cat", "catalyst", "Pd(OAc)2", e),
        participant("na2co3", "reagent", "Na2CO3", e, smiles_key="sodium carbonate"),
        participant("water", "solvent", "H2O", e, smiles_key="water"),
        participant("dme", "solvent", "DME", e, smiles_key="DME"),
        participant("product_7", "product", "product 7", e),
    ],
    steps=[reaction_step(["substrate_E3f", "phenylboronic", "pd_cat", "na2co3", "water", "dme", "product_7"],
                         e, "r.t.", qty(12, "h"), "H2O/DME")],
    outcomes=[fld("isolated_yield_product_7", qty(60, "%"), e, ["product_7"])],
    unresolved=["Scheme 4 does not state scale, reagent/catalyst amounts, solvent ratio, workup, or purification."],
))
records.append(record(
    "scheme4_E3f_oxidation_E4f", 6, "reported_experiment",
    participants=[
        participant("substrate_E3f", "reactant", "E-3f", e),
        participant("mcpba", "reagent", "m-CPBA", e, smiles_key="m-CPBA"),
        participant("ch2cl2", "solvent", "CH2Cl2", e, smiles_key="CH2Cl2"),
        participant("product_E4f", "product", "E-4f", e),
    ],
    steps=[reaction_step(["substrate_E3f", "mcpba", "ch2cl2", "product_E4f"],
                         e, qty(0, "°C"), qty(2, "h"), "CH2Cl2")],
    outcomes=[fld("isolated_yield_E4f", qty(85, "%"), e, ["product_E4f"])],
    unresolved=["Scheme 4 does not state scale, m-CPBA amount, workup, or purification."],
))


OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"records": len(records), "output": str(OUT)}, ensure_ascii=False))
