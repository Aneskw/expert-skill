#!/usr/bin/env python3
"""Build evidence-linked machine extraction for jo0108616 PDF pages 1-6."""
from __future__ import annotations

import json
from pathlib import Path


DOC = "doc_6d3edd1b61c89bf4"
ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / "runs/current/raw_model/records_pages_0001_0006.json"
COVERAGE = ROOT / "runs/current/coverage/pages_0001_0006.json"
TASKS = ROOT / "runs/current/tasks.json"


def evid(page: int) -> list[str]:
    return [f"{DOC}:page{page}:image", f"{DOC}:page{page}:text"]


def fact(value, evidence_ids):
    return {
        "value": value,
        "evidence_ids": list(evidence_ids) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def quantity(number, unit, **extra):
    value = {"number": number, "unit": unit}
    value.update(extra)
    return value


def qrange(minimum, maximum, unit, raw_text):
    return {"minimum": minimum, "maximum": maximum, "unit": unit, "raw_text": raw_text}


def field(name, value, evidence_ids, targets=None):
    item = {"name": name, "fact": fact(value, evidence_ids)}
    if targets:
        item["target_entity_ids"] = list(targets)
    return item


SMILES = {
    "1a": "C=C=CCC(C(=O)OC)C(=O)OC",
    "iodobenzene": "Ic1ccccc1",
    "4-bromophenyl iodide": "Brc1ccc(I)cc1",
    "4-iodotoluene": "Cc1ccc(I)cc1",
    "4-iodoanisole": "COc1ccc(I)cc1",
    "methyl 4-iodobenzoate": "COC(=O)c1ccc(I)cc1",
    "(E)-1-iodo-2-phenylethylene": "I/C=C/c1ccccc1",
    "1-iodonaphthalene": "Ic1cccc2ccccc12",
    "(E)-1-iodo-1-hexene": "CCCC/C=C/I",
    "(Z)-1-iodo-1-hexene": "CCCC/C=C\\I",
    "2-iodothiophene": "Ic1cccs1",
    "o-iodotoluene": "Cc1ccccc1I",
    "K2CO3": "[K+].[K+].[O-]C([O-])=O",
    "NaH": "[Na+].[H-]",
    "NaOH": "[Na+].[OH-]",
    "KOH": "[K+].[OH-]",
    "LiOH": "[Li+].[OH-]",
    "CH3CN": "CC#N",
    "THF": "C1CCOC1",
    "DMF": "CN(C)C=O",
    "DMSO": "CS(C)=O",
    "toluene": "Cc1ccccc1",
    "benzene": "c1ccccc1",
    "Et3N": "CCN(CC)CC",
    "CH2Cl2": "ClCCl",
    "acetyl chloride": "CC(=O)Cl",
    "methanol": "CO",
    "diethyl ether": "CCOCC",
    "ethyl acetate": "CCOC(C)=O",
    "dimethyl malonate": "COC(=O)CC(=O)OC",
    "6b": "CCOC(=O)C(=C=C)Cc1ccccc1",
    "7b": "C=C=C(Cc1ccccc1)CO",
}


SUBSTRATES = {
    "1a": "dimethyl 2-(2′,3′-butadienyl)malonate",
    "1b": "dimethyl 2-(2′-benzyl-2′,3′-butadienyl)malonate",
    "1c": "dimethyl 2-(2′-propyl-2′,3′-butadienyl)malonate",
    "1d": "dimethyl 2-(deca-2′,3′-dienyl)malonate",
    "1e": "dimethyl 2-(2′-methylhepta-2′,3′-dienyl)malonate",
}


HALIDES = {
    "PhI": ("iodobenzene", "iodobenzene"),
    "p-BrC6H4I": ("4-bromophenyl iodide", "4-bromophenyl iodide"),
    "p-MeC6H4I": ("4-iodotoluene", "4-iodotoluene"),
    "p-MeOC6H4I": ("4-iodoanisole", "4-iodoanisole"),
    "p-MeO2CC6H4I": ("methyl 4-iodobenzoate", "methyl 4-iodobenzoate"),
    "E-styryl-I": ("(E)-1-iodo-2-phenylethylene", "(E)-1-iodo-2-phenylethylene"),
    "1-iodonaphthalene": ("1-iodonaphthalene", "1-iodonaphthalene"),
    "E-hexenyl-I": ("(E)-1-iodo-1-hexene", "(E)-1-iodo-1-hexene"),
    "Z-hexenyl-I": ("(Z)-1-iodo-1-hexene", "(Z)-1-iodo-1-hexene"),
    "2-iodothiophene": ("2-iodothiophene", "2-iodothiophene"),
    "o-MeC6H4I": ("o-iodotoluene", "o-iodotoluene"),
}


def participant(entity_id, role, label, name, evidence_ids, smiles=None, amounts=None):
    smiles_value = SMILES.get(smiles or name or label)
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence_ids),
        "name": fact(name, evidence_ids) if name is not None else fact(None, []),
        "smiles": fact(smiles_value, evidence_ids) if smiles_value else fact(None, []),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": amounts or [],
    }


def amount(name, value, evidence_ids):
    return field(name, value, evidence_ids)


def base_part(label, equiv, ev):
    return participant(
        "base", "reagent", label, label, ev, label,
        [amount("equivalents", quantity(equiv, "equiv"), ev)] if equiv is not None else [],
    )


def catalyst_parts(system, ev):
    if system == "Pd(PPh3)4-5":
        return [participant("catalyst", "catalyst", "Pd(PPh3)4", "tetrakis(triphenylphosphine)palladium(0)", ev,
                            amounts=[amount("catalyst_loading", quantity(5, "mol%"), ev)])]
    if system == "Pd(PPh3)4-20":
        return [participant("catalyst", "catalyst", "Pd(PPh3)4", "tetrakis(triphenylphosphine)palladium(0)", ev,
                            amounts=[amount("catalyst_loading", quantity(20, "mol%"), ev)])]
    if system == "Pd2dba3-dppe":
        return [
            participant("catalyst", "catalyst", "Pd2(dba)3·CHCl3", "tris(dibenzylideneacetone)dipalladium chloroform adduct", ev,
                        amounts=[amount("catalyst_loading", quantity(2, "mol%"), ev)]),
            participant("ligand", "reagent", "dppe", "1,2-bis(diphenylphosphino)ethane", ev,
                        amounts=[amount("ligand_loading", quantity(4, "mol%"), ev)]),
        ]
    if system == "Pd2dba3-2.5-PPh3":
        return [
            participant("catalyst", "catalyst", "Pd2(dba)3·CHCl3", "tris(dibenzylideneacetone)dipalladium chloroform adduct", ev,
                        amounts=[amount("catalyst_loading", quantity(2.5, "mol%"), ev)]),
            participant("ligand", "reagent", "PPh3", "triphenylphosphine", ev,
                        amounts=[amount("ligand_loading", quantity(10, "mol%"), ev)]),
        ]
    raise ValueError(system)


def product(entity_id, label, family, ev):
    return participant(entity_id, "product", label, f"{family} {label}", ev)


records = []


def add_record(suffix, kind, pages, participants, steps, outcomes, notes=None, unresolved=None, extra_evidence=None):
    ev = []
    for page in pages:
        ev.extend(evid(page))
    if extra_evidence:
        ev.extend(extra_evidence)
    ev = list(dict.fromkeys(ev))
    rec = {
        "record_id": f"{DOC}:{suffix}",
        "document_id": DOC,
        "source_reaction_id": suffix,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": ev,
        "participants": participants,
        "steps": steps,
        "outcomes": outcomes,
        "notes": [fact(x, ev) for x in (notes or [])],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved or [
                "Machine extraction requires source review; structures are unverified.",
                "No supporting-information file was explicitly supplied or associated.",
            ],
        },
    }
    records.append(rec)
    return rec


def coupling_record(
    suffix, pages, kind, substrate, halide_key, time_value, temperature, solvent,
    catalyst_system, base, base_equiv, prod2, yield2, prod3, yield3,
    halide_equiv=1.2, additive=False, solvent_volume=None, extra_outcomes=None,
    notes=None, extra_evidence=None, extra_participants=None,
):
    ev = []
    for page in pages:
        ev.extend(evid(page))
    halide_label, halide_name = HALIDES[halide_key]
    parts = [
        participant("substrate", "reactant", substrate, SUBSTRATES[substrate], ev, substrate),
        participant("organic_halide", "reactant", halide_key, halide_name, ev, halide_name,
                    [amount("equivalents", quantity(halide_equiv, "equiv"), ev)] if halide_equiv is not None else []),
        base_part(base, base_equiv, ev),
        participant("solvent", "solvent", solvent, solvent, ev, solvent,
                    [amount("volume", quantity(solvent_volume, "mL"), ev)] if solvent_volume is not None else []),
    ]
    parts.extend(catalyst_parts(catalyst_system, ev))
    if additive:
        parts.append(participant("additive", "reagent", "n-Bu4NBr", "tetrabutylammonium bromide", ev,
                                 amounts=[amount("additive_loading", quantity(10, "mol%"), ev)]))
    if extra_participants:
        parts.extend(extra_participants)
    p2_id = "product_2"
    p3_id = "product_3"
    parts.extend([
        product(p2_id, prod2, "cyclopropane product", ev),
        product(p3_id, prod3, "cyclopentene product", ev),
    ])
    conditions = [
        field("operation", "Pd(0)-catalyzed coupling-cyclization", ev),
        field("solvent", solvent, ev),
        field("temperature", temperature, ev),
        field("time", time_value, ev),
        field("atmosphere", None, []),
    ]
    outcomes = [
        field(f"yield_{prod2}", yield2, ev, [p2_id]),
        field(f"yield_{prod3}", yield3, ev, [p3_id]),
        field("yield_measurement_basis", None, []),
    ]
    if extra_outcomes:
        outcomes.extend(extra_outcomes(p2_id, p3_id, ev))
    return add_record(
        suffix, kind, pages, parts,
        [{"step_id": "coupling_cyclization", "participant_ids": [p["entity_id"] for p in parts], "conditions": conditions}],
        outcomes, notes=notes,
        unresolved=[
            "Yield measurement basis is not stated for this table/scheme result unless separately noted.",
            "Reaction scale, atmosphere, workup, purification, and isolated mass are not reported in this region.",
            "Depicted substrate/product structures and stereochemistry remain machine candidates, not verified structures.",
            "No supporting-information file was explicitly supplied or associated.",
        ],
        extra_evidence=extra_evidence,
    )


# Page 1: generic mechanistic/regioselectivity framework, not a reported experiment.
ev1 = evid(1)
add_record(
    "scheme1_generic_carbopalladation", "mechanism", [1],
    [
        participant("generic_allene", "reactant", "generic functionalized allene", None, ev1),
        participant("organic_halide", "reactant", "RPdX precursor", None, ev1),
        participant("pi_allyl_intermediate", "unspecified_agent", "π-allyl palladium intermediate", None, ev1),
        participant("path_a_product", "product", "path a cyclic product", None, ev1),
        participant("path_b_product", "product", "path b product", None, ev1),
    ], [], [],
    notes=["Scheme 1 is a generic pathway with R groups and variable n; it is not counted as a current-paper experimental run."],
    unresolved=["Generic R groups and n prevent assignment of complete structures or experimental quantities."],
)


# Page 2, Table 1. Rows 6 and 7 are the same experiments as Table 2 entry 1 A/B.
table1 = [
    (1, "DMF", None, quantity(60, "°C"), quantity(25, "h"), 65, 8),
    (2, "DMSO", None, quantity(62, "°C"), quantity(22, "h"), 49, 21),
    (3, "toluene", None, quantity(82, "°C"), quantity(15.5, "h"), 30, 0),
    (4, "benzene", None, quantity(80, "°C"), quantity(15, "h"), 40, 0),
    (5, "CH3CN", None, "reflux", quantity(19.5, "h"), 32, 0),
    (6, "CH3CN", "n-Bu4NBr", "reflux", quantity(15, "h"), 80, 0),
    (7, "THF", None, "reflux", quantity(15.5, "h"), 85, 0),
]
table1_records = {}
for row, solvent, additive_name, temp, tm, y2, y3 in table1:
    pages = [2, 6] if row == 6 else [2]
    extra = [f"{DOC}:page7:text"] if row == 6 else None
    rec = coupling_record(
        f"table1_entry_{row}", pages, "optimization_entry", "1a", "PhI", tm, temp, solvent,
        "Pd(PPh3)4-5", "K2CO3", 4, "2a", quantity(y2, "%"), "3a", quantity(y3, "%"),
        additive=bool(additive_name), solvent_volume=3 if row == 6 else None,
        notes=["Table 1 footnote: PhI was used at 1.2 equivalents."], extra_evidence=extra,
    )
    if row == 6:
        ev6 = evid(6) + [f"{DOC}:page7:text"]
        by_id = {p["entity_id"]: p for p in rec["participants"]}
        by_id["substrate"]["amounts"] = [amount("mass", quantity(117, "mg"), ev6), amount("amount", quantity(0.64, "mmol"), ev6)]
        by_id["organic_halide"]["amounts"] += [amount("mass", quantity(156, "mg"), ev6), amount("amount", quantity(0.76, "mmol"), ev6)]
        by_id["base"]["amounts"] += [amount("mass", quantity(352, "mg"), ev6), amount("amount", quantity(2.55, "mmol"), ev6)]
        by_id["additive"]["amounts"] += [amount("mass", quantity(20, "mg"), ev6), amount("amount", quantity(0.064, "mmol"), ev6)]
        by_id["catalyst"]["amounts"] += [amount("mass", quantity(37, "mg"), ev6), amount("amount", quantity(0.032, "mmol"), ev6)]
        rec["steps"][0]["conditions"][4] = field("atmosphere", "nitrogen", ev6)
        rec["steps"].append({
            "step_id": "workup_and_purification",
            "participant_ids": ["product_2"],
            "conditions": [
                field("workup", "filtered, washed with ether, and evaporated", [f"{DOC}:page7:text"]),
                field("purification", "flash chromatography on silica gel; petroleum ether/ethyl acetate 20:1", [f"{DOC}:page7:text"]),
            ],
        })
        rec["outcomes"][0]["fact"] = fact(quantity(80, "%"), evid(2) + [f"{DOC}:page7:text"])
        rec["outcomes"][2] = field("yield_measurement_basis", "isolated after flash chromatography", [f"{DOC}:page7:text"])
    table1_records[row] = rec


# Table 2 entries 2-8 under A and B; entry 1 is already Table 1 entries 6 and 7.
for rec, label in [(table1_records[6], "Table 2 entry 1, Conditions A"), (table1_records[7], "Table 2 entry 1, Conditions B")]:
    rec["notes"].append(fact(f"Duplicate presentation merged: {label} reports the same conditions, time, and yield.", evid(2)))

table2_rows = [
    (2, "p-BrC6H4I", 17, 83, 25.3, 76, "2b"),
    (3, "p-MeC6H4I", 24, 82, 23, 57, "2c"),
    (4, "p-MeOC6H4I", 17, 69, 24.5, 59, "2d"),
    (5, "E-styryl-I", 16, 46, 25.3, 45, "2e"),
    (6, "1-iodonaphthalene", 23, 86, 23, 91, "2f"),
    (7, "p-MeO2CC6H4I", 24, 58, 24.67, 73, "2g"),
    (8, "E-hexenyl-I", 16, 67, 23.83, 61, "2h"),
]
for row, halide, ta, ya, tb, yb, prod in table2_rows:
    coupling_record(
        f"table2_entry_{row}_conditions_A", [2], "substrate_scope_entry", "1a", halide,
        quantity(ta, "h"), "reflux", "CH3CN", "Pd(PPh3)4-5", "K2CO3", 4,
        prod, quantity(ya, "%"), f"3 counterpart of {prod}", None,
        halide_equiv=1.2, additive=True,
        extra_outcomes=lambda a, b, ev: [field("regioselectivity", "cyclopropane product 2 reported as the sole product", ev, [a])],
        notes=["Conditions A; the text describes cyclopropane derivatives as the sole products."],
    )
    coupling_record(
        f"table2_entry_{row}_conditions_B", [2], "substrate_scope_entry", "1a", halide,
        quantity(tb, "h"), "reflux", "THF", "Pd(PPh3)4-5", "K2CO3", 4,
        prod, quantity(yb, "%"), f"3 counterpart of {prod}", None,
        halide_equiv=1.3, additive=False,
        extra_outcomes=lambda a, b, ev: [field("regioselectivity", "cyclopropane product 2 reported as the sole product", ev, [a])],
        notes=["Conditions B; the text describes cyclopropane derivatives as the sole products."],
    )


# Scheme 3 B is separate; Scheme 3 A duplicates Table 3 entry 1 below.
coupling_record(
    "scheme3_conditions_B_trace", [2], "optimization_entry", "1b", "PhI", quantity(24, "h"),
    "reflux", "THF", "Pd(PPh3)4-5", "K2CO3", 4, "2i", None, "3i", None,
    halide_equiv=1.3, additive=False,
    extra_outcomes=lambda a, b, ev: [field("combined_trace_products", "trace amount of 2i or 3i", ev, [a, b])],
    notes=["Scheme 3 states only a trace amount of 2i or 3i; the trace amount cannot be assigned separately to either product."],
)

table3_rows = [
    (1, "1b", "PhI", 15, "2i", 80, "3i", qrange(2, 3, "%", "2-3%")),
    (2, "1b", "p-MeOC6H4I", 29, "2j", 63, "3j", 0),
    (3, "1b", "p-MeO2CC6H4I", 24, "2k", 82, "3k", 16),
    (4, "1b", "E-styryl-I", 24, "2l", 84, "3l", 0),
    (5, "1b", "E-hexenyl-I", 15, "2m", 67, "3m", 0),
    (6, "1b", "Z-hexenyl-I", 12, "2n", 45, "3n", 0),
    (7, "1b", "2-iodothiophene", 14, "2o", 97, "3o", 0),
    (8, "1c", "PhI", 44, "2p", 77, "3p", 0),
    (9, "1c", "p-MeOC6H4I", 26, "2q", 45, "3q", 0),
    (10, "1c", "p-MeO2CC6H4I", 26, "2r", 71, "3r", 0),
    (11, "1c", "E-styryl-I", 15, "2s", 71, "3s", 0),
    (12, "1c", "E-hexenyl-I", 15, "2t", 70, "3t", 0),
    (13, "1c", "Z-hexenyl-I", 12, "2u", 57, "3u", 0),
    (14, "1c", "2-iodothiophene", 14, "2v", 79, "3v", 0),
]
for row, substrate, halide, tm, p2, y2, p3, y3 in table3_rows:
    rec = coupling_record(
        f"table3_entry_{row}", [2], "substrate_scope_entry", substrate, halide, quantity(tm, "h"),
        "reflux", "CH3CN", "Pd(PPh3)4-5", "K2CO3", 4, p2, quantity(y2, "%"),
        p3, y3 if isinstance(y3, dict) else quantity(y3, "%"), additive=True,
        notes=["Conditions A; organic iodide was used at 1.2 equivalents."],
    )
    if row == 1:
        rec["notes"].append(fact("Scheme 3 Conditions A is the same experiment and was merged with this row.", evid(2)))


# Page 3, Table 4.
table4_rows = [
    (1, "PhI", quantity(12, "h"), "2w", 72, "25:75", "3w", 6),
    (2, "p-MeC6H4I", quantity(12, "h"), "2x", 88, "44:56", "3x", 4),
    (3, "p-MeOC6H4I", quantity(17, "h"), "2y", 57, "42:58", "3y", 9),
    (4, "p-MeO2CC6H4I", quantity(7, "d"), "2z", 71, "48:52", "3z", 8),
    (5, "E-styryl-I", quantity(19, "h"), "2α", 88, "19:81", "3α", 0),
]
for row, halide, tm, p2, y2, ratio, p3, y3 in table4_rows:
    coupling_record(
        f"table4_entry_{row}", [3], "substrate_scope_entry", "1d", halide, tm, "reflux", "CH3CN",
        "Pd(PPh3)4-5", "K2CO3", 4, p2, quantity(y2, "%"), p3, quantity(y3, "%"),
        additive=True,
        extra_outcomes=lambda a, b, ev, ratio=ratio, p2=p2: [
            field(f"E_Z_ratio_{p2}", ratio, ev, [a]),
            field("E_Z_ratio_measurement_basis", "300 MHz 1H NMR", ev, [a]),
        ],
    )
coupling_record(
    "table4_entry_6", [3], "substrate_scope_entry", "1e", "PhI", quantity(16, "h"), "reflux", "CH3CN",
    "Pd(PPh3)4-5", "K2CO3", 4, "2β", quantity(42, "%"), "3β", quantity(21, "%"), additive=True,
    extra_outcomes=lambda a, b, ev: [
        field("E_Z_ratio_2β", "0:100", ev, [a]),
        field("E_Z_ratio_measurement_basis", "300 MHz 1H NMR", ev, [a]),
    ],
)


# Page 3, Scheme 4 optimization entries.
coupling_record(
    "scheme4_condition_1", [3], "optimization_entry", "1b", "PhI", quantity(24, "h"), quantity(85, "°C"),
    "DMSO", "Pd2dba3-dppe", "K2CO3", 4, "2i", quantity(49, "%"), "3i", quantity(13, "%"), additive=True,
    halide_equiv=None,
)
coupling_record(
    "scheme4_condition_2", [3], "optimization_entry", "1b", "PhI", quantity(12.5, "h"), quantity(85, "°C"),
    "DMSO", "Pd2dba3-dppe", "NaH", 1.1, "2i", quantity(14, "%"), "3i", quantity(58, "%"), additive=False,
    halide_equiv=None,
)
coupling_record(
    "scheme4_conditions_C", [3], "optimization_entry", "1b", "PhI", quantity(12, "h"), quantity(85, "°C"),
    "DMSO", "Pd(PPh3)4-5", "NaH", 1.1, "2i", quantity(0, "%"), "3i", quantity(88, "%"), additive=False,
    extra_evidence=[f"{DOC}:page7:text"],
    notes=["The 12 h duration is supplied by the matching Conditions C typical procedure on PDF page 7 text; page 7 was context only, not part of this visual-coverage claim."],
)


# Page 3, Table 5 (Conditions C); entry 9 substitutes THF for DMSO.
table5_rows = [
    (1, "1b", "p-MeC6H4I", 11, "2 (Table 5 entry 1)", 0, "3 (Table 5 entry 1)", 79, None),
    (2, "1b", "p-MeOC6H4I", 11, "2j", 0, "3j", 98, None),
    (3, "1b", "p-MeO2CC6H4I", 14, "2k", 0, "3k", 77, None),
    (4, "1c", "PhI", 12, "2p", 0, "3p", 65, None),
    (5, "1c", "p-MeC6H4I", 10, "2δ", 0, "3δ", 54, None),
    (6, "1c", "p-MeOC6H4I", 15, "2q", 7, "3q", 47, None),
    (7, "1c", "p-MeO2CC6H4I", 15, "2r", 8, "3r", 54, None),
    (8, "1d", "PhI", 9, "2w", 0, "3w", 81, None),
    (9, "1d", "PhI", 9, "2w", 0, "3w", 95, "THF"),
    (10, "1d", "p-MeC6H4I", 9, "2x", 5, "3x", 82, "53:47"),
    (11, "1d", "p-MeOC6H4I", 9.5, "2y", 20, "3y", 78, "56:44"),
    (12, "1b", "E-styryl-I", 37, "2l", 39, "3l", 32, None),
    (13, "1b", "E-hexenyl-I", 11, "2m", 40, "3m", 24, None),
    (14, "1c", "E-hexenyl-I", 11, "2t", 32, "3t", 18, None),
    (15, "1a", "E-styryl-I", 12, "2e", 45, "3e", 0, None),
]
for row, substrate, halide, tm, p2, y2, p3, y3, special in table5_rows:
    solvent = "THF" if special == "THF" else "DMSO"
    ratio = special if special not in (None, "THF") else None
    coupling_record(
        f"table5_entry_{row}", [3], "substrate_scope_entry", substrate, halide, quantity(tm, "h"), quantity(85, "°C"),
        solvent, "Pd(PPh3)4-5", "NaH", 1.1, p2, quantity(y2, "%"), p3, quantity(y3, "%"),
        additive=False,
        extra_outcomes=(lambda a, b, ev, ratio=ratio, p2=p2: [
            field(f"E_Z_ratio_{p2}", ratio, ev, [a]),
            field("E_Z_ratio_measurement_basis", "300 MHz 1H NMR", ev, [a]),
        ]) if ratio else None,
        notes=["Table 5 footnote: organic iodide was used at 1.2 equivalents."] + (["Table 5 footnote b: THF was used as the solvent."] if row == 9 else []),
    )


# Page 4, Scheme 5 conversion controls.
ev4 = evid(4)
def scheme5_record(suffix, with_base, recovered):
    parts = [
        participant("starting_2i", "reactant", "2i", "cyclopropane 2i", ev4),
        participant("expected_3i", "product", "3i", "cyclopentene 3i", ev4),
        participant("catalyst", "catalyst", "Pd(PPh3)4", "tetrakis(triphenylphosphine)palladium(0)", ev4,
                    amounts=[amount("catalyst_loading", quantity(5, "mol%"), ev4)]),
        participant("solvent", "solvent", "DMSO", "DMSO", ev4, "DMSO"),
    ]
    if with_base:
        parts.append(base_part("NaH", 1.1, ev4))
    add_record(
        suffix, "optimization_entry", [4], parts,
        [{"step_id": "conversion_test", "participant_ids": [p["entity_id"] for p in parts], "conditions": [
            field("temperature", quantity(85, "°C"), ev4), field("time", quantity(13, "h"), ev4),
            field("solvent", "DMSO", ev4), field("atmosphere", None, []),
        ]}],
        [
            field("formation_of_3i", "not formed", ev4, ["expected_3i"]),
            field("recovered_starting_material_yield", quantity(recovered, "%"), ev4, ["starting_2i"]),
            field("yield_measurement_basis", None, []),
        ],
        notes=["Scheme 5 tests whether isolated 2i converts to 3i under Conditions C or in the absence of NaH."],
        unresolved=["Recovery/yield measurement basis and detection limit for 'no 3i formed' are not reported."],
    )
scheme5_record("scheme5_conditions_C", True, 71)
scheme5_record("scheme5_without_NaH", False, 79)


# Page 4, Table 6.
table6_rows = [
    (1, "DMSO", "NaH", 1.1, quantity(85, "°C"), 12, 8, 42, "Pd(PPh3)4-5"),
    (2, "DMSO", "NaH", 1.1, quantity(85, "°C"), 12, 22, 51, "Pd2dba3-dppe"),
    (3, "DMF", "NaH", 1.1, quantity(85, "°C"), 12, 5, 60, "Pd2dba3-dppe"),
    (4, "DMF", "NaH", 1.1, quantity(85, "°C"), 10, 5, 67, "Pd(PPh3)4-5"),
    (5, "DMF", "KOH", 2.0, quantity(85, "°C"), 10, 4, 51, "Pd2dba3-dppe"),
    (6, "toluene", "NaH", 1.1, quantity(85, "°C"), 12, 0, "trace", "Pd2dba3-dppe"),
    (7, "CH3CN", "NaH", 1.1, "reflux", 12, 9, 22, "Pd2dba3-dppe"),
    (8, "THF", "NaH", 1.1, "reflux", 7, 0, 26, "Pd2dba3-dppe"),
    (9, "THF", "LiOH", 2.0, "reflux", 12, 0, 3, "Pd2dba3-dppe"),
    (10, "THF", "NaOH", 2.0, "reflux", 12, 0, 20, "Pd2dba3-dppe"),
    (11, "THF", "LDA", 1.1, "reflux", 12, "trace", "trace", "Pd2dba3-dppe"),
    (12, "THF", "n-BuLi", 1.1, "reflux", 12, "trace", "trace", "Pd2dba3-dppe"),
]
for row, solvent, base, equiv, temp, tm, y2, y3, cat in table6_rows:
    coupling_record(
        f"table6_entry_{row}", [4], "optimization_entry", "1a", "PhI", quantity(tm, "h"), temp, solvent,
        cat, base, equiv, "2a", quantity(y2, "%") if isinstance(y2, (int, float)) else y2,
        "3a", quantity(y3, "%") if isinstance(y3, (int, float)) else y3,
        notes=["Table 6 footnote: PhI was used at 1.2 equivalents."] + (["Footnote c: Pd(PPh3)4 (5 mol%) replaced Pd2(dba)3·CHCl3/dppe."] if row in (1, 4) else []),
    )


# Page 4, Table 7: combined yield and NMR product ratio are retained without deriving individual yields.
table7_rows = [
    (1, "n-BuLi", 1.1, 10.5, 46, "0:100"),
    (2, "KOH", 2.0, 10.5, 31, "0:100"),
    (3, "NaOH", 1.2, 12, 75, "13:87"),
    (4, "NaOH", 1.5, 12, 40, "0:100"),
    (5, "NaOH", 2.0, 10.5, 66, "0:100"),
]
for row, base, equiv, tm, combined, ratio in table7_rows:
    ev = evid(4)
    parts = [
        participant("substrate", "reactant", "1a", SUBSTRATES["1a"], ev, "1a"),
        participant("organic_halide", "reactant", "PhI", "iodobenzene", ev, "iodobenzene", [amount("equivalents", quantity(1.2, "equiv"), ev)]),
        base_part(base, equiv, ev),
        participant("solvent", "solvent", "DMF", "DMF", ev, "DMF"),
        *catalyst_parts("Pd(PPh3)4-5", ev),
        product("product_2", "2a", "cyclopropane product", ev),
        product("product_3", "3a", "cyclopentene product", ev),
    ]
    add_record(
        f"table7_entry_{row}", "optimization_entry", [4], parts,
        [{"step_id": "coupling_cyclization", "participant_ids": [p["entity_id"] for p in parts], "conditions": [
            field("solvent", "DMF", ev), field("temperature", quantity(85, "°C"), ev),
            field("time", quantity(tm, "h"), ev), field("atmosphere", None, []),
        ]}],
        [
            field("combined_yield_2a_plus_3a", quantity(combined, "%"), ev, ["product_2", "product_3"]),
            field("product_ratio_2a_3a", ratio, ev, ["product_2", "product_3"]),
            field("product_ratio_measurement_basis", "300 MHz 1H NMR", ev, ["product_2", "product_3"]),
            field("yield_measurement_basis", None, []),
        ],
        notes=["Individual product yields were not calculated from the combined yield and ratio."],
        unresolved=["Combined yield measurement basis is not stated; individual yields are not explicitly reported."],
    )


# Page 4, Table 8 (Conditions D); rows 4 and 6 replace NaOH with NaH.
table8_rows = [
    (1, "1a", "p-MeC6H4I", 11, "2c", 0, "3c", 63, "NaOH", 2.0),
    (2, "1a", "p-MeOC6H4I", 11, "2d", 0, "3d", 57, "NaOH", 2.0),
    (3, "1c", "p-MeOC6H4I", 10.5, "2q", 0, "3q", 51, "NaOH", 2.0),
    (4, "1c", "p-MeOC6H4I", 11, "2q", 0, "3q", 70, "NaH", 1.1),
    (5, "1c", "p-MeO2CC6H4I", 10.5, "2r", 0, "3r", 52, "NaOH", 2.0),
    (6, "1c", "p-MeO2CC6H4I", 11, "2r", 13, "3r", 59, "NaH", 1.1),
]
for row, substrate, halide, tm, p2, y2, p3, y3, base, equiv in table8_rows:
    coupling_record(
        f"table8_entry_{row}", [4], "substrate_scope_entry", substrate, halide, quantity(tm, "h"), quantity(85, "°C"),
        "DMF", "Pd(PPh3)4-5", base, equiv, p2, quantity(y2, "%"), p3, quantity(y3, "%"),
        notes=["Table 8 footnote: organic iodide was used at 1.2 equivalents."] + (["Footnote b: NaH (1.1 equiv) replaced NaOH."] if row in (4, 6) else []),
    )


# Page 5, Scheme 6: Conditions D and a Cazes-condition comparison.
ev5 = evid(5)
def scheme6_record(suffix, time_hours, condition_name, y2, y3, recovered=None):
    ev_scheme = evid(4) + evid(5)
    parts = [
        participant("substrate", "reactant", "1a", SUBSTRATES["1a"], ev_scheme, "1a"),
        participant("organic_halide", "reactant", "p-MeO2CC6H4I", "methyl 4-iodobenzoate", ev_scheme, "methyl 4-iodobenzoate",
                    [amount("equivalents", quantity(1.2, "equiv"), ev_scheme)] if condition_name == "Conditions D" else []),
        product("product_2", "2g", "cyclopropane product", ev_scheme),
        product("product_3", "3g", "cyclopentene product", ev_scheme),
    ]
    if condition_name == "Conditions D":
        parts += [base_part("NaOH", 2.0, ev_scheme), participant("solvent", "solvent", "DMF", "DMF", ev_scheme, "DMF"), *catalyst_parts("Pd(PPh3)4-5", ev_scheme)]
        temp = quantity(85, "°C")
    else:
        parts += [base_part("NaH", 1.06, ev_scheme), participant("solvent", "solvent", "THF", "THF", ev_scheme, "THF"), *catalyst_parts("Pd2dba3-dppe", ev_scheme)]
        temp = "reflux"
    outs = [
        field("yield_2g", y2, ev_scheme, ["product_2"]),
        field("yield_3g", y3, ev_scheme, ["product_3"]),
        field("yield_measurement_basis", None, []),
    ]
    if condition_name == "Conditions D":
        outs += [
            field("combined_yield_2g_plus_3g", quantity(55, "%"), ev_scheme, ["product_2", "product_3"]),
            field("product_ratio_2g_3g", "34:66", ev_scheme, ["product_2", "product_3"]),
            field("product_ratio_measurement_basis", "300 MHz 1H NMR", ev_scheme, ["product_2", "product_3"]),
        ]
    if recovered is not None:
        outs.append(field("recovered_1a", quantity(recovered, "%"), ev_scheme, ["substrate"]))
    if condition_name == "Conditions D":
        steps = [{"step_id": "coupling_cyclization", "participant_ids": [p["entity_id"] for p in parts], "conditions": [
            field("condition_set", condition_name, ev_scheme), field("temperature", temp, ev_scheme),
            field("time", quantity(time_hours, "h"), ev_scheme), field("atmosphere", None, []),
        ]}]
    else:
        steps = [
            {"step_id": "base_pretreatment", "participant_ids": ["substrate", "base", "solvent"], "conditions": [
                field("temperature", "r.t.", ev_scheme),
                field("time", qrange(1, 2, "h", "1-2 h"), ev_scheme),
            ]},
            {"step_id": "catalytic_coupling", "participant_ids": [p["entity_id"] for p in parts], "conditions": [
                field("operation", "pretreated solution added to the catalyst/ligand flask and then treated with the depicted aryl iodide", ev_scheme),
                field("temperature", temp, ev_scheme), field("time", quantity(time_hours, "h"), ev_scheme), field("atmosphere", None, []),
            ]},
        ]
    add_record(
        suffix, "optimization_entry", [4, 5], parts,
        steps, outs,
        notes=(["Scheme 6 reports 55% combined yield and a 34:66 product ratio; 34 and 66 are not individual yields."]
               if condition_name == "Conditions D" else
               ["The Cazes-condition sequence is described in footnote 8 on PDF page 4; the scheme substrate is methyl 4-iodobenzoate even though the footnote cites the original PhI procedure."]),
        unresolved=(["Individual product yields and the combined-yield measurement basis are not stated."]
                    if condition_name == "Conditions D" else
                    ["Trace product detection limits and product-specific yield basis are not stated."]),
    )
scheme6_record("scheme6_conditions_D", 11, "Conditions D", None, None)
scheme6_record("scheme6_Cazes_conditions", 48, "Cazes conditions", "trace", "trace", 37)


# Page 5, Scheme 7 single-substrate and competition experiments.
coupling_record(
    "scheme7_o_iodotoluene", [5], "substrate_scope_entry", "1b", "o-MeC6H4I", quantity(3.5, "d"), "reflux", "CH3CN",
    "Pd(PPh3)4-5", "K2CO3", 4, "2i-o-Me", None, "3i-o-Me", quantity(80, "%"), additive=True,
    extra_outcomes=lambda a, b, ev: [field("regioselectivity", "3i-o-Me reported as the sole product", ev, [b])],
    notes=["Scheme 7 and prose describe 3i-o-Me as the sole product under Conditions A."],
)
ev5 = evid(5)
parts = [
    participant("substrate", "reactant", "1b", SUBSTRATES["1b"], ev5, "1b", [amount("equivalents", quantity(1, "equiv"), ev5)]),
    participant("PhI", "reactant", "PhI", "iodobenzene", ev5, "iodobenzene", [amount("equivalents", quantity(1, "equiv"), ev5)]),
    participant("o_iodotoluene", "reactant", "o-MeC6H4I", "o-iodotoluene", ev5, "o-iodotoluene", [amount("equivalents", quantity(1, "equiv"), ev5)]),
    base_part("K2CO3", 4, ev5),
    participant("additive", "reagent", "n-Bu4NBr", "tetrabutylammonium bromide", ev5, amounts=[amount("additive_loading", quantity(10, "mol%"), ev5)]),
    participant("solvent", "solvent", "CH3CN", "CH3CN", ev5, "CH3CN"),
    *catalyst_parts("Pd(PPh3)4-5", ev5),
    product("product_2i", "2i", "cyclopropane product", ev5),
    product("product_3i", "3i", "cyclopentene product", ev5),
    product("product_3i_oMe", "3i-o-Me", "cyclopentene product", ev5),
]
add_record(
    "scheme7_competition", "reported_experiment", [5], parts,
    [{"step_id": "competition_coupling", "participant_ids": [p["entity_id"] for p in parts], "conditions": [
        field("solvent", "CH3CN", ev5), field("temperature", "reflux", ev5), field("time", quantity(17, "h"), ev5),
        field("atmosphere", None, []),
    ]}],
    [
        field("yield_2i", quantity(64, "%"), ev5, ["product_2i"]),
        field("yield_3i", quantity(8, "%"), ev5, ["product_3i"]),
        field("yield_3i_oMe", quantity(19, "%"), ev5, ["product_3i_oMe"]),
        field("yield_measurement_basis", None, []),
    ],
    unresolved=["Yield measurement basis, scale, atmosphere, workup, and purification are not stated."],
)


# Page 5, Scheme 8 mechanism.
add_record(
    "scheme8_syn_anti_intermediates", "mechanism", [5],
    [
        participant("anti_4", "unspecified_agent", "anti-4", "anti π-allyl palladium intermediate", ev5),
        participant("syn_4", "unspecified_agent", "syn-4", "syn π-allyl palladium intermediate", ev5),
        participant("product_3", "product", "3", "generic cyclopentene product", ev5),
        participant("product_2", "product", "2", "generic cyclopropane product", ev5),
    ], [], [],
    notes=["Scheme 8 is a mechanistic proposal: anti-4 leads to 3 and syn-4 leads to 2."],
    unresolved=["Generic R/R1/E groups prevent complete structure assignment; no experimental quantities are attached to this mechanism."],
)


# Page 5, Scheme 9 sequential addition experiment.
parts = [
    participant("substrate", "reactant", "1b", SUBSTRATES["1b"], ev5, "1b"),
    participant("organic_halide", "reactant", "PhI", "iodobenzene", ev5, "iodobenzene"),
    participant("catalyst", "catalyst", "Pd(PPh3)4", "tetrakis(triphenylphosphine)palladium(0)", ev5,
                amounts=[amount("catalyst_loading", quantity(20, "mol%"), ev5)]),
    participant("solvent", "solvent", "DMSO", "DMSO", ev5, "DMSO"),
    base_part("NaH", 1.1, ev5),
    product("product_2", "2i", "cyclopropane product", ev5),
]
add_record(
    "scheme9_delayed_base_addition", "reported_experiment", [5], parts,
    [
        {"step_id": "carbopalladation_before_base", "participant_ids": ["substrate", "organic_halide", "catalyst", "solvent"], "conditions": [
            field("solvent", "DMSO", ev5), field("temperature", quantity(85, "°C"), ev5), field("time", quantity(6, "h"), ev5),
        ]},
        {"step_id": "after_NaH_addition", "participant_ids": ["base", "product_2"], "conditions": [
            field("temperature", quantity(85, "°C"), ev5), field("time", quantity(4.5, "h"), ev5),
        ]},
    ],
    [field("yield_2i", quantity(29, "%"), ev5, ["product_2"]), field("yield_measurement_basis", None, [])],
    notes=["The prose states 2i was formed exclusively after delayed addition of NaH."],
    unresolved=["Reactant scale, PhI equivalents, atmosphere, workup, purification, and yield basis are not stated."],
)


# Page 5, Scheme 10 generic Wittig-type route.
add_record(
    "scheme10_generic_allenoate_synthesis", "general_scheme", [5],
    [
        participant("ylide_4", "reactant", "4", "generic phosphorane 4", ev5),
        participant("acid_chloride_5", "reactant", "5", "generic acid chloride 5", ev5),
        participant("triethylamine", "reagent", "Et3N", "triethylamine", ev5, "Et3N"),
        participant("solvent", "solvent", "CH2Cl2", "dichloromethane", ev5, "CH2Cl2"),
        participant("allenoate_6", "product", "6", "generic 2,3-allenoic acid ethyl ester 6", ev5),
    ],
    [{"step_id": "wittig_type_allenoate_formation", "participant_ids": ["ylide_4", "acid_chloride_5", "triethylamine", "solvent", "allenoate_6"], "conditions": [field("solvent", "CH2Cl2", ev5)]}],
    [], notes=["Scheme 10 is a generic series map (b-e), not one experimental run."],
    unresolved=["R1/R2 variables prevent a single complete structure; row-level quantities are supplied only in the experimental prose."],
)


# Pages 5-6: detailed preparation of allenoate 6b.
ev56 = evid(5) + evid(6)
parts = [
    participant("ylide_4b", "reactant", "4b", "phosphorane 4b (R1 = Bn)", ev56,
                amounts=[amount("mass", quantity(87.6, "g"), ev56), amount("amount", quantity(0.2, "mol"), ev56)]),
    participant("acetyl_chloride", "reactant", "5b", "acetyl chloride", ev56, "acetyl chloride",
                [amount("volume", quantity(18.5, "mL"), ev56), amount("amount", quantity(0.26, "mol"), ev56)]),
    participant("triethylamine", "reagent", "Et3N", "triethylamine", ev56, "Et3N",
                [amount("volume", quantity(36.2, "mL"), ev56), amount("amount", quantity(0.26, "mol"), ev56)]),
    participant("solvent", "solvent", "CH2Cl2", "dichloromethane", ev56, "CH2Cl2",
                [amount("volume_initial", quantity(300, "mL"), ev56), amount("volume_with_Et3N", quantity(30, "mL"), ev56), amount("volume_with_5b", quantity(20, "mL"), ev56)]),
    participant("ether", "solvent", "ether", "diethyl ether", ev56, "diethyl ether", [amount("volume", quantity(150, "mL"), ev56)]),
    participant("drying_agent", "reagent", "Na2SO4", "anhydrous sodium sulfate", ev56),
    participant("product", "product", "6b", "2-benzylbuta-2,3-dienoic acid ethyl ester", ev56, "6b"),
]
add_record(
    "preparation_6b", "reported_experiment", [5, 6], parts,
    [
        {"step_id": "amine_addition", "participant_ids": ["ylide_4b", "triethylamine", "solvent"], "conditions": [
            field("addition_time", quantity(45, "min"), ev56), field("temperature", "r.t.", ev56), field("time_after_addition", quantity(5, "min"), ev56),
        ]},
        {"step_id": "acid_chloride_reaction", "participant_ids": ["acetyl_chloride"], "conditions": [
            field("operation", "acetyl chloride solution added dropwise", ev56), field("temperature", "r.t.", ev56), field("time", "overnight", ev56),
        ]},
        {"step_id": "workup_purification", "participant_ids": ["ether", "drying_agent", "product"], "conditions": [
            field("workup", "remove solvent in vacuo; treat with ether; filter; dry organic phase over anhydrous sodium sulfate; evaporate", ev56),
            field("purification", "flash chromatography on silica gel; petroleum ether/ethyl acetate 40:1", ev56),
        ]},
    ],
    [
        field("isolated_mass", quantity(19.4, "g"), ev56, ["product"]),
        field("yield_6b", quantity(56, "%"), ev56, ["product"]),
        field("yield_measurement_basis", "isolated after flash chromatography", ev56, ["product"]),
    ],
    unresolved=["Atmosphere and concentration are not stated; the exact structure of phosphorane 4b was not encoded as SMILES."],
)


# Page 6, Scheme 11 general routes.
ev6 = evid(6)
add_record(
    "scheme11_allenoate_reduction", "general_scheme", [6],
    [
        participant("allenoate_6", "reactant", "6", "generic allenoate 6", ev6),
        participant("DIBAL_H", "reagent", "DIBAL-H", "diisobutylaluminium hydride", ev6),
        participant("allenol_7", "product", "7", "generic 2,3-allen-1-ol 7", ev6),
    ],
    [{"step_id": "reduction", "participant_ids": ["allenoate_6", "DIBAL_H", "allenol_7"], "conditions": [field("temperature", quantity(-78, "°C"), ev6)]}],
    [], unresolved=["Generic R1/R2 groups and absent scale/time prevent a complete experiment record."],
)
add_record(
    "scheme11_bromination_and_malonate_alkylation", "general_scheme", [6],
    [
        participant("allenol_7", "reactant", "7", "generic 2,3-allen-1-ol 7", ev6),
        participant("PBr3", "reagent", "PBr3", "phosphorus tribromide", ev6),
        participant("pyridine", "reagent", "pyridine", "pyridine", ev6),
        participant("ether", "solvent", "Et2O", "diethyl ether", ev6, "diethyl ether"),
        participant("dimethyl_malonate", "reactant", "dimethyl malonate", "dimethyl malonate", ev6, "dimethyl malonate"),
        participant("NaH", "reagent", "NaH", "sodium hydride", ev6, "NaH"),
        participant("THF", "solvent", "THF", "THF", ev6, "THF"),
        participant("product_1", "product", "1", "generic 2-(2′,3′-dienyl)malonate 1", ev6),
    ],
    [
        {"step_id": "bromination", "participant_ids": ["allenol_7", "PBr3", "pyridine", "ether"], "conditions": [field("solvent", "Et2O", ev6)]},
        {"step_id": "malonate_alkylation", "participant_ids": ["dimethyl_malonate", "NaH", "THF", "product_1"], "conditions": [field("solvent", "THF", ev6)]},
    ], [], unresolved=["The bromide intermediate, quantities, temperatures, and times are not specified in Scheme 11."],
)


# Page 6: 6e synthesis using the Scheme 10 method.
parts = [
    participant("ylide_4e", "reactant", "4e", "phosphorane 4e (R1 = CH3)", ev6,
                amounts=[amount("mass", quantity(19, "g"), ev6), amount("amount", quantity(52.5, "mmol"), ev6)]),
    participant("acid_chloride_5e", "reactant", "5e", "acid chloride 5e (R2 = n-C3H7)", ev6,
                amounts=[amount("mass", quantity(6.4, "g"), ev6), amount("amount", quantity(53.1, "mmol"), ev6)]),
    participant("triethylamine", "reagent", "Et3N", "triethylamine", ev6, "Et3N"),
    participant("solvent", "solvent", "CH2Cl2", "dichloromethane", ev6, "CH2Cl2"),
    participant("product", "product", "6e", "2-methylhepta-2,3-dienoic acid ethyl ester", ev6),
]
add_record(
    "preparation_6e", "reported_experiment", [6], parts,
    [{"step_id": "wittig_type_allenoate_formation", "participant_ids": [p["entity_id"] for p in parts], "conditions": [
        field("operation", "prepared according to the Wittig-type reaction of Scheme 10", ev6), field("time", None, []), field("temperature", None, []),
    ]}],
    [field("isolated_mass", quantity(7.6, "g"), ev6, ["product"]), field("yield_6e", quantity(86, "%"), ev6, ["product"]), field("yield_measurement_basis", None, [])],
    unresolved=["Et3N/solvent amounts, time, temperature, workup, purification, and yield basis are not restated for 6e."],
)


# Page 6: allenol reductions. Only 7b has a complete local procedure; variants retain missing details.
parts = [
    participant("starting_6b", "reactant", "6b", "2-benzylbuta-2,3-dienoic acid ethyl ester", ev6, "6b",
                [amount("mass", quantity(10.1, "g"), ev6), amount("amount", quantity(50, "mmol"), ev6)]),
    participant("DIBAL_H", "reagent", "DIBAL-H", "diisobutylaluminium hydride", ev6,
                amounts=[amount("concentration", quantity(1.0, "M"), ev6), amount("volume", quantity(105, "mL"), ev6), amount("equivalents", quantity(2.1, "equiv"), ev6)]),
    participant("toluene", "solvent", "toluene", "toluene", ev6, "toluene", [amount("volume", quantity(130, "mL"), ev6)]),
    participant("methanol", "reagent", "methanol", "methanol", ev6, "methanol", [amount("volume", quantity(50, "mL"), ev6)]),
    participant("brine", "reagent", "brine", "brine", ev6, amounts=[amount("volume", quantity(150, "mL"), ev6)]),
    participant("ether", "solvent", "ether", "diethyl ether", ev6, "diethyl ether", [amount("extraction_volume", quantity(50, "mL"), ev6)]),
    participant("drying_agent", "reagent", "Na2SO4", "anhydrous sodium sulfate", ev6),
    participant("product", "product", "7b", "2-benzylbuta-2,3-dien-1-ol", ev6, "7b"),
]
add_record(
    "preparation_7b", "reported_experiment", [6], parts,
    [
        {"step_id": "DIBAL_reduction", "participant_ids": ["starting_6b", "DIBAL_H", "toluene"], "conditions": [
            field("operation", "DIBAL-H added dropwise to rapidly stirred solution", ev6), field("temperature", quantity(-78, "°C"), ev6),
            field("time", quantity(4, "h"), ev6), field("atmosphere", "nitrogen", ev6), field("monitoring", "TLC until 6b disappeared", ev6),
        ]},
        {"step_id": "quench_workup", "participant_ids": ["methanol", "brine", "ether", "drying_agent"], "conditions": [
            field("temperature", quantity(0, "°C"), ev6), field("workup_time", quantity(5, "min"), ev6),
            field("workup", "methanol quench; add brine and stir 5 min; filter and separate; extract aqueous layer with ether 3 × 50 mL; dry over Na2SO4", ev6),
        ]},
        {"step_id": "purification", "participant_ids": ["product"], "conditions": [field("purification", "evaporation and flash chromatography; petroleum ether/ethyl acetate 10:1", ev6)]},
    ],
    [field("isolated_mass", quantity(5.3, "g"), ev6, ["product"]), field("yield_7b", quantity(67, "%"), ev6, ["product"]), field("yield_measurement_basis", "isolated after flash chromatography", ev6, ["product"])],
    notes=["Ether extraction was reported as 3 × 50 mL; the structured volume retains the per-extraction value and the multiplier is preserved in workup text."],
    unresolved=["Final concentration is not stated; product structure remains unverified despite a candidate SMILES."],
)


def abbreviated_reduction(suffix, start_label, start_name, start_mass, start_amount, product_label, product_name, product_mass, product_yield, note=None):
    parts = [
        participant("starting_material", "reactant", start_label, start_name, ev6,
                    amounts=[amount("mass", quantity(start_mass, "g"), ev6), amount("amount", quantity(start_amount, "mmol"), ev6)]),
        participant("DIBAL_H", "reagent", "DIBAL-H", "diisobutylaluminium hydride", ev6),
        participant("product", "product", product_label, product_name, ev6),
    ]
    add_record(
        suffix, "reported_experiment", [6], parts,
        [{"step_id": "reduction", "participant_ids": [p["entity_id"] for p in parts], "conditions": [
            field("operation", "DIBAL-H reduction in the 2,3-allen-1-ol synthesis series", ev6), field("time", None, []), field("temperature", None, []),
        ]}],
        [field("isolated_mass", quantity(product_mass, "g"), ev6, ["product"]), field(f"yield_{product_label}", quantity(product_yield, "%"), ev6, ["product"]), field("yield_measurement_basis", None, [])],
        notes=[note] if note else None,
        unresolved=["DIBAL-H amount, solvent, time, temperature, atmosphere, workup, purification, and yield basis are not restated for this abbreviated preparation."],
    )


abbreviated_reduction("preparation_7c", "6c", "2-propylbuta-2,3-dienoic acid ester 6c", 7.7, 50, "7c", "2-propylbuta-2,3-dien-1-ol", 2.94, 53)
abbreviated_reduction("preparation_7d_from_ethyl_ester", "6d", "deca-2,3-dienoic acid ethyl ester 6d", 15.7, 80, "7d", "deca-2,3-dien-1-ol", 1.64, 13)
parts = [
    participant("starting_material", "reactant", "corresponding methyl ester", "methyl deca-2,3-dienoate", ev6),
    participant("DIBAL_H", "reagent", "DIBAL-H", "diisobutylaluminium hydride", ev6),
    participant("product", "product", "7d", "deca-2,3-dien-1-ol", ev6),
]
add_record(
    "preparation_7d_from_methyl_ester", "optimization_entry", [6], parts,
    [{"step_id": "reduction", "participant_ids": [p["entity_id"] for p in parts], "conditions": [field("time", None, []), field("temperature", None, [])]}],
    [field("yield_7d", quantity(42, "%"), ev6, ["product"]), field("yield_measurement_basis", None, [])],
    notes=["The paper states that the yield was improved to 42% using the corresponding methyl ester."],
    unresolved=["Starting scale, DIBAL-H amount, solvent, time, temperature, workup, purification, and yield basis are not reported for this variant."],
)
abbreviated_reduction("preparation_7e", "6e", "2-methylhepta-2,3-dienoic acid ethyl ester", 2.6, 16.8, "7e", "2-methylhepta-2,3-dien-1-ol", 1.34, 63)


# Page 6: abbreviated NaH/THF malonate alkylations reported for 1a-e.
alkylations = [
    ("1a", "4-bromo-1,2-butadiene", 5.3, 40, 5.15, 70),
    ("1b", "3-bromomethyl-4-phenyl-1,2-butadiene", 4.2, 19, 4.27, 82),
    ("1c", "3-bromomethyl-1,2-hexadiene", 3.15, 18, 3.7, 91),
    ("1d", "1-bromo-2,3-decadiene", 1.09, 5.0, 0.80, 60),
    ("1e", "1-bromo-2-methyl-2,3-heptadiene", 0.47, 2.46, 0.31, 53),
]
for product_label, bromide_name, start_mass, start_amount, product_mass, yld in alkylations:
    parts = [
        participant("allenyl_bromide", "reactant", bromide_name, bromide_name, ev6,
                    amounts=[amount("mass", quantity(start_mass, "g"), ev6), amount("amount", quantity(start_amount, "mmol"), ev6)]),
        participant("dimethyl_malonate", "reactant", "dimethyl malonate", "dimethyl malonate", ev6, "dimethyl malonate"),
        participant("NaH", "reagent", "NaH", "sodium hydride", ev6, "NaH"),
        participant("THF", "solvent", "THF", "THF", ev6, "THF"),
        participant("product", "product", product_label, SUBSTRATES[product_label], ev6, product_label),
    ]
    add_record(
        f"preparation_{product_label}", "reported_experiment", [6], parts,
        [{"step_id": "malonate_alkylation", "participant_ids": [p["entity_id"] for p in parts], "conditions": [
            field("operation", "alkylation of dimethyl malonate with the corresponding allenyl bromide and NaH in THF as reported", ev6),
            field("solvent", "THF", ev6), field("time", None, []), field("temperature", None, []), field("atmosphere", None, []),
        ]}],
        [field("isolated_mass", quantity(product_mass, "g"), ev6, ["product"]), field(f"yield_{product_label}", quantity(yld, "%"), ev6, ["product"]), field("yield_measurement_basis", None, [])],
        notes=["The allenyl bromide preparation from the corresponding allenol and PBr3 is cited to prior literature and is not merged into this alkylation record."],
        unresolved=["Dimethyl malonate and NaH amounts, time, temperature, atmosphere, workup, purification, and yield basis are not restated."],
    )


# Write raw model output.
RAW.parent.mkdir(parents=True, exist_ok=True)
RAW.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")


# Coverage is limited to the six visually inspected original pages.
record_ids_by_page = {page: [] for page in range(1, 7)}
for rec in records:
    for page in range(1, 7):
        if f"{DOC}:page{page}:image" in rec["evidence_ids"]:
            record_ids_by_page[page].append(rec["record_id"])

coverage_pages = [
    {
        "page": 1,
        "state": "attempted",
        "regions": [
            {"region": "Scheme 1, center-right", "finding": "Generic carbopalladation/π-allyl-palladium pathway with paths a and b; classified as mechanism, not a reported experiment.", "evidence_ids": [f"{DOC}:page1:image", f"{DOC}:page1:text"]},
            {"region": "Title, abstract, and two-column introduction", "finding": "Current-paper overview and prior-work citations; prose previews Conditions A/B and Table 1 but contains no additional row-level experiment beyond later pages.", "evidence_ids": [f"{DOC}:page1:image", f"{DOC}:page1:text"]},
        ],
        "record_ids": record_ids_by_page[1],
        "unresolved": ["Generic Scheme 1 R groups and variable n do not support complete structures or quantities."],
    },
    {
        "page": 2,
        "state": "attempted",
        "regions": [
            {"region": "Table 1, upper left", "finding": "Seven independent solvent/additive optimization rows for 1a + PhI; row 6 and row 7 duplicate Table 2 entry 1 Conditions A/B and were merged.", "evidence_ids": [f"{DOC}:page2:image", f"{DOC}:page2:text"]},
            {"region": "Scheme 2 and Table 2, lower left", "finding": "Definitions of Conditions A/B and eight substrate-scope rows, each with A and B times/yields; entry 1 A/B merged with Table 1 rows 6/7.", "evidence_ids": [f"{DOC}:page2:image", f"{DOC}:page2:text"]},
            {"region": "Scheme 3, upper right", "finding": "1b + PhI under Conditions A (same as Table 3 entry 1) and a separate Conditions B trace-result experiment.", "evidence_ids": [f"{DOC}:page2:image", f"{DOC}:page2:text"]},
            {"region": "Table 3, right column", "finding": "Fourteen Conditions A substrate-scope experiments with row-specific organic iodides, times, and product-2/product-3 yields.", "evidence_ids": [f"{DOC}:page2:image", f"{DOC}:page2:text"]},
        ],
        "record_ids": record_ids_by_page[2],
        "unresolved": ["Most table yields lack an explicit isolated/NMR basis; product drawings and stereochemistry remain unverified machine candidates."],
    },
    {
        "page": 3,
        "state": "attempted",
        "regions": [
            {"region": "Table 4, upper left", "finding": "Six Conditions A scope rows for 4′-substituted allenyl malonates, including E/Z ratios and both cyclopropane/cyclopentene yields.", "evidence_ids": [f"{DOC}:page3:image", f"{DOC}:page3:text"]},
            {"region": "Figure 1, middle left", "finding": "NOE-based configuration assignments for E-2x, Z-2x, and Z-2β; structure-assignment evidence, not a separate reaction experiment.", "evidence_ids": [f"{DOC}:page3:image", f"{DOC}:page3:text"]},
            {"region": "Scheme 4, upper right", "finding": "Three independent catalyst/base optimization experiments for 1b + PhI, including Conditions C (3i, 88%).", "evidence_ids": [f"{DOC}:page3:image", f"{DOC}:page3:text"]},
            {"region": "Table 5, right column", "finding": "Fifteen Conditions C scope rows; entry 9 uses THF by footnote and entries 10-11 report E/Z ratios.", "evidence_ids": [f"{DOC}:page3:image", f"{DOC}:page3:text"]},
        ],
        "record_ids": record_ids_by_page[3],
        "unresolved": ["The exact Greek product label in Table 5 entry 1 is visually ambiguous and is retained as a table-entry label rather than guessed."],
    },
    {
        "page": 4,
        "state": "attempted",
        "regions": [
            {"region": "Scheme 5, upper left", "finding": "Two 2i-to-3i conversion controls, with and without NaH; no 3i formed and 71%/79% 2i recovered.", "evidence_ids": [f"{DOC}:page4:image", f"{DOC}:page4:text"]},
            {"region": "Table 6, left", "finding": "Twelve solvent/base/catalyst optimization rows, including zero and trace outcomes and catalyst footnote overrides.", "evidence_ids": [f"{DOC}:page4:image", f"{DOC}:page4:text"]},
            {"region": "Table 7, upper right", "finding": "Five base-loading optimization rows reporting combined yield and 2a:3a NMR ratio; individual yields were not derived.", "evidence_ids": [f"{DOC}:page4:image", f"{DOC}:page4:text"]},
            {"region": "Table 8, middle right", "finding": "Six Conditions D scope rows; footnote rows 4 and 6 replace NaOH with NaH (1.1 equiv).", "evidence_ids": [f"{DOC}:page4:image", f"{DOC}:page4:text"]},
            {"region": "Footnote 8, bottom right", "finding": "Cazes-condition sequence supplies NaH/catalyst/ligand/THF context for Scheme 6; its wording cites the original PhI procedure and is not used to replace Scheme 6's depicted aryl iodide.", "evidence_ids": [f"{DOC}:page4:image", f"{DOC}:page4:text"]},
        ],
        "record_ids": record_ids_by_page[4],
        "unresolved": ["Table 6/7/8 yield bases and trace detection limits are unstated."],
    },
    {
        "page": 5,
        "state": "attempted",
        "regions": [
            {"region": "Scheme 6, upper left", "finding": "Conditions D experiment (55% combined, 2g:3g 34:66 by NMR) and separate Cazes-condition trace-result control with 37% 1a recovered.", "evidence_ids": [f"{DOC}:page5:image", f"{DOC}:page5:text"]},
            {"region": "Scheme 7, middle left", "finding": "o-Iodotoluene scope experiment (3i-o-Me 80%) and a three-reactant competition experiment giving 2i/3i/3i-o-Me in 64%/8%/19%.", "evidence_ids": [f"{DOC}:page5:image", f"{DOC}:page5:text"]},
            {"region": "Scheme 8, lower left", "finding": "Proposed anti-4/syn-4 regioselectivity mechanism; not a reported experiment.", "evidence_ids": [f"{DOC}:page5:image", f"{DOC}:page5:text"]},
            {"region": "Scheme 9, upper right", "finding": "Sequential delayed-base experiment: Pd(PPh3)4/DMSO at 85 °C for 6 h, then NaH for 4.5 h, affording 2i in 29%.", "evidence_ids": [f"{DOC}:page5:image", f"{DOC}:page5:text"]},
            {"region": "Scheme 10 and Experimental Section, right", "finding": "Generic Wittig-type allenoate route plus the beginning of the detailed 6b preparation, continued/identified on page 6.", "evidence_ids": [f"{DOC}:page5:image", f"{DOC}:page5:text"]},
        ],
        "record_ids": record_ids_by_page[5],
        "unresolved": ["Scheme 6 trace detection limits and most scheme yield bases are not stated; Scheme 10 generic R groups are not complete molecules."],
    },
    {
        "page": 6,
        "state": "attempted",
        "regions": [
            {"region": "Scheme 11, upper left", "finding": "Generic allenoate-to-allenol reduction and two-stage bromination/malonate-alkylation routes; classified as general schemes.", "evidence_ids": [f"{DOC}:page6:image", f"{DOC}:page6:text"]},
            {"region": "Left column, allenoates and allenols", "finding": "Completion/identity of 6b; abbreviated 6e preparation; detailed 7b DIBAL-H procedure; abbreviated 7c, two distinct 7d variants, and 7e preparations.", "evidence_ids": [f"{DOC}:page6:image", f"{DOC}:page6:text"]},
            {"region": "Right column, malonates 1a-e", "finding": "Five reported NaH/THF malonate alkylations with starting allenyl-bromide amounts, isolated masses, and yields.", "evidence_ids": [f"{DOC}:page6:image", f"{DOC}:page6:text"]},
            {"region": "Bottom right, Conditions A typical procedure", "finding": "Detailed quantities and setup for the same 1a + PhI experiment already represented by Table 1 entry 6/Table 2 entry 1A; evidence merged into that record, with the page-7 textual continuation used only as context.", "evidence_ids": [f"{DOC}:page6:image", f"{DOC}:page6:text"]},
            {"region": "Statement that 6c and 6d are known", "finding": "Prior-literature preparation only; no current-paper procedure is reconstructed from citations.", "evidence_ids": [f"{DOC}:page6:image", f"{DOC}:page6:text"]},
        ],
        "record_ids": record_ids_by_page[6],
        "unresolved": ["Most abbreviated preparations omit time, temperature, reagent amounts, workup, purification, and yield basis; no SI was supplied to fill them."],
    },
]
COVERAGE.parent.mkdir(parents=True, exist_ok=True)
COVERAGE.write_text(json.dumps({
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": coverage_pages,
}, ensure_ascii=False, indent=2) + "\n")


# Mark only this session's six page tasks as attempted; later pages remain pending.
tasks = json.loads(TASKS.read_text())
for task in tasks:
    page_prefix = f"{DOC}:page"
    if task["document_id"] == DOC and task["task_id"].startswith(page_prefix):
        page = int(task["task_id"].split(":page", 1)[1].split(":", 1)[0])
        if 1 <= page <= 6:
            task["state"] = "attempted"
            task["visual_evidence_id"] = f"{DOC}:page{page}:image"
TASKS.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({
    "records": len(records),
    "kinds": {kind: sum(r["record_kind"] == kind for r in records) for kind in sorted({r["record_kind"] for r in records})},
    "coverage_pages": [p["page"] for p in coverage_pages],
}, ensure_ascii=False, indent=2))
