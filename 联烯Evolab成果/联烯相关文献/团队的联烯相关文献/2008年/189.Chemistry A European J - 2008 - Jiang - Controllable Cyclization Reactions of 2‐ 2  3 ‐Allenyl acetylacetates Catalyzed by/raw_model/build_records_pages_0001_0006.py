#!/usr/bin/env python3
"""Build evidence-linked machine records for PDF pages 1-6."""
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "runs/current/raw_model/records_pages_0001_0006.json"
COVERAGE = ROOT / "runs/current/coverage/pages_0001_0006.json"
TASKS = ROOT / "runs/current/tasks.json"
DOC = "doc_d204b16be54ce48f"


def evid(page: int) -> list[str]:
    return [f"{DOC}:page{page}:image", f"{DOC}:page{page}:text"]


P = {i: evid(i) for i in range(1, 7)}


def uniq(items):
    return list(dict.fromkeys(items))


def fact(value, ev=()):
    return {
        "value": value,
        "evidence_ids": list(ev) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def fld(name, value, ev=(), targets=None):
    item = {"name": name, "fact": fact(value, ev)}
    if targets:
        item["target_entity_ids"] = list(targets)
    return item


SMILES = {
    "1a": "C=C=CCC(C(C)=O)C(=O)OCC",
    "2a": "CCOC(=O)C1(C(C)=O)CC=CC1",
    "dichloromethane": "ClCCl",
    "1,2-dichloroethane": "ClCCCl",
    "acetonitrile": "CC#N",
    "toluene": "Cc1ccccc1",
    "nitromethane": "C[N+](=O)[O-]",
    "THF": "C1CCOC1",
    "DMF": "CN(C)C=O",
    "acetone": "CC(C)=O",
    "allyl bromide": "C=CCBr",
    "triethylamine": "CCN(CC)CC",
    "potassium carbonate": "[K+].[K+].[O-]C([O-])=O",
    "sodium carbonate": "[Na+].[Na+].[O-]C([O-])=O",
    "sodium bicarbonate": "[Na+].OC([O-])=O",
    "potassium acetate": "CC(=O)[O-].[K+]",
    "potassium fluoride": "[K+].[F-]",
    "potassium hydroxide": "[K+].[OH-]",
}


def part(entity_id, role, label, ev, name=None, smiles=None, amounts=()):
    if smiles is None:
        smiles = SMILES.get(label) or SMILES.get(name or "")
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, ev),
        "name": fact(name, ev) if name else fact(None),
        "smiles": fact(smiles, ev) if smiles else fact(None),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": [fld(n, v, e) for n, v, e in amounts],
    }


def amount(name, number, unit, ev, **extra):
    value = {"number": number, "unit": unit}
    value.update(extra)
    return (name, value, ev)


def range_amount(name, minimum, maximum, unit, ev, raw_text):
    return (name, {"minimum": minimum, "maximum": maximum, "unit": unit, "raw_text": raw_text}, ev)


def experimental(
    rid,
    kind,
    ev,
    participants,
    *,
    time=None,
    temperature=None,
    solvent=None,
    atmosphere="dry argon",
    outcomes=(),
    workup=None,
    purification=None,
    operation=None,
    notes=(),
    unresolved=(),
):
    ev = uniq(ev + P[5])  # page 5 explicitly states that all reactions used dry argon
    cond = [
        fld("temperature", temperature, ev if temperature is not None else ()),
        fld("time", time, ev if time is not None else ()),
        fld("atmosphere", atmosphere, P[5]),
        fld("solvent", solvent, ev if solvent is not None else ()),
        fld("operation", operation, ev if operation is not None else ()),
        fld("workup", workup, ev if workup is not None else ()),
        fld("purification", purification, ev if purification is not None else ()),
    ]
    return {
        "record_id": f"{DOC}:{rid}",
        "document_id": DOC,
        "source_reaction_id": rid,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": ev,
        "participants": participants,
        "steps": [{"step_id": "reaction", "participant_ids": [p["entity_id"] for p in participants], "conditions": cond}],
        "outcomes": list(outcomes),
        "notes": [fact(n, ev) for n in notes],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": list(unresolved) or [
                "Machine extraction requires expert source review; structures are unverified."
            ],
        },
    }


def conceptual(rid, kind, ev, participants, notes, unresolved):
    return {
        "record_id": f"{DOC}:{rid}",
        "document_id": DOC,
        "source_reaction_id": rid,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": uniq(ev),
        "participants": participants,
        "steps": [],
        "outcomes": [],
        "notes": [fact(n, ev) for n in notes],
        "review": {"method": "none", "reviewer": None, "checked_fields": [], "unresolved": list(unresolved)},
    }


def substrate(label, ev, amount_items=()):
    names = {
        "1a": "ethyl 2-acetyl-2-(2,3-butadienyl)acetate",
        "1b": "methyl 2-acetyl-2-(2,3-butadienyl)acetate",
        "1c": "methyl 2-propionyl-2-(2,3-butadienyl)acetate",
        "1d": "ethyl 2-butyryl-2-(2,3-butadienyl)acetate",
        "1e": "methyl 2-isobutyryl-2-(2,3-butadienyl)acetate",
        "1f": "methyl 2-(2,3-butadienyl)-4-phenylacetoacetate",
        "1g": "methyl 2-benzoyl-2-(2,3-butadienyl)acetate",
        "1h": "ethyl 2-(2-benzyl-2,3-butadienyl)acetylacetate",
        "1i": "tert-butyl 2-acetyl-2-(2,3-butadienyl)acetate",
        "1j": "methyl 2-butyryl-2-(2,3-butadienyl)acetate",
    }
    return part(label, "reactant", label, ev, names.get(label), amounts=amount_items)


def product(label, ev, name=None, amounts=()):
    return part(label, "product", label, ev, name, amounts=amounts)


def yield_field(name, number_or_text, ev, target, basis="isolated"):
    value = {"number": number_or_text, "unit": "%"} if isinstance(number_or_text, (int, float)) else number_or_text
    fields = [fld(name, value, ev, [target])]
    if basis is not None:
        fields.append(fld(name + "_measurement_basis", basis, ev, [target]))
    return fields


records = []

# Page 1: conceptual cyclization modes, not an executed experiment.
records.append(conceptual(
    "scheme1_possible_cyclization_modes",
    "general_scheme",
    P[1],
    [part("generic_1", "reactant", "generic 2-(2',3'-allenyl)acetylacetate", P[1])],
    ["Scheme 1 enumerates C-attack/O-attack and 3-exo/5-exo/5-endo/7-endo possibilities."],
    ["Generic R-group structures and metal identity are unspecified; no conditions or yields are reported."],
))

# Table 1. Entry 4 is also Table 2 Method A entry 1 and the detailed Method A procedure.
t1 = [
    (1, 5, None, 0, 24, 0),
    (2, 5, "AgBF4", 5, 17, 5),
    (3, 5, "AgOTf", 5, 3, 43),
    (4, 5, "AgSbF6", 5, 1, 68),
    (5, 0, "AgOTf", 5, 12, 8),
    (6, 5, "AgSbF6", 5, 24, 64),
]
for entry, au_loading, ag_label, ag_loading, hours, yld in t1:
    rid = f"table1_entry{entry}"
    ev = P[2]
    if entry == 4:
        rid += "_method_a_2a"
        ev = P[2] + P[5]
    parts = [
        substrate("1a", ev),
        product("2a", ev, "4-acetyl-4-(ethoxycarbonyl)cyclopentene"),
        part("au_cat", "catalyst", "[AuCl(PPh3)]", ev, amounts=[amount("catalyst_loading", au_loading, "mol%", P[2])]),
        part("solvent", "solvent", "dichloromethane", ev, amounts=[amount("volume", 2, "mL", P[2])] if entry == 4 else []),
    ]
    if ag_label:
        parts.append(part("ag_additive", "catalyst", ag_label, ev, amounts=[amount("catalyst_loading", ag_loading, "mol%", P[2])]))
    else:
        parts.append(part("ag_additive", "catalyst", "AgX", ev, amounts=[amount("catalyst_loading", 0, "mol%", P[2])]))
    if entry == 6:
        parts.append(part("allyl_bromide", "reagent", "allyl bromide", ev, amounts=[amount("equivalents", 5, "equiv", P[2])]))
    outs = yield_field("isolated_yield_2a", yld, P[2], "2a")
    notes = []
    unresolved = ["Most optimization rows do not report scale, workup, or purification; structures remain unverified."]
    if entry == 1:
        outs += [fld("recovered_starting_material_yield", {"number": 80, "unit": "%"}, P[2], ["1a"])]
    if entry == 2:
        outs += [fld("combined_isolated_yield_1a_and_2a", {"number": 77, "unit": "%"}, P[2], ["1a", "2a"]), fld("1a_to_2a_ratio", "100:7", P[2], ["1a", "2a"]), fld("ratio_measurement_basis", "1H NMR", P[2], ["1a", "2a"])]
        unresolved.append("The table also prints a 5% 2a value although the footnote describes an inseparable 1a/2a mixture.")
    if entry == 5:
        outs += [fld("combined_isolated_yield_1a_and_2a", {"number": 70, "unit": "%"}, P[2], ["1a", "2a"]), fld("1a_to_2a_ratio", "100:13", P[2], ["1a", "2a"]), fld("ratio_measurement_basis", "1H NMR", P[2], ["1a", "2a"])]
        unresolved.append("The table also prints an 8% 2a value although the footnote describes an inseparable 1a/2a mixture.")
    workup = purification = operation = None
    if entry == 4:
        parts[0]["amounts"] += [fld("mass", {"number": 47, "unit": "mg"}, P[5]), fld("amount", {"number": 0.26, "unit": "mmol"}, P[5])]
        parts[1]["amounts"] += [fld("isolated_mass", {"number": 32, "unit": "mg"}, P[5])]
        parts[2]["amounts"] += [fld("mass", {"number": 6, "unit": "mg"}, P[5]), fld("amount", {"number": 0.0121, "unit": "mmol"}, P[5])]
        parts[4]["amounts"] += [fld("mass", {"number": 3, "unit": "mg"}, P[5]), fld("amount", {"number": 0.0117, "unit": "mmol"}, P[5])]
        operation = "flame-dried Schlenk tube; TLC monitoring with petroleum ether/ethyl acetate 10:1; rotary evaporation"
        workup = "rotary evaporation"
        purification = "flash chromatography on silica gel, petroleum ether/ethyl ether 20:1"
        unresolved = ["Method A is source-complete operationally, but all machine-recognized structures remain unverified."]
    records.append(experimental(rid, "optimization_entry", ev, parts, time={"number": hours, "unit": "h"}, temperature="r.t.", solvent="dichloromethane", outcomes=outs, workup=workup, purification=purification, operation=operation, notes=notes, unresolved=unresolved))

# Table 2 Method A entries 2-8; entry 1 is merged into Table 1 entry 4.
table2 = [
    (1, "1a", "2a", 68, "3a", 73),
    (2, "1b", "2b", 51, "3b", 57),
    (3, "1c", "2c", 42, "3c", 60),
    (4, "1d", "2d", 93, "3d", 82),
    (5, "1e", "2e", 76, "3e", 77),
    (6, "1f", "2f", 71, "3f", 33),
    (7, "1g", "2g", 67, "3g", 60),
    (8, "1h", "2h", 73, "3h", 40),
]
for entry, s, pa, ya, pb, yb in table2:
    if entry != 1:
        ev = P[2] + (P[6] if entry == 7 else [])
        solvent_label = "1,2-dichloroethane" if entry == 5 else "dichloromethane"
        temp = "reflux" if entry == 5 else "r.t."
        parts = [
            substrate(s, ev, [range_amount("reaction_scale", 0.15, 0.50, "mmol", P[2], "0.15-0.50 mmol")]),
            product(pa, ev),
            part("au_cat", "catalyst", "[AuCl(PPh3)]", ev, amounts=[amount("catalyst_loading", 5, "mol%", P[2])]),
            part("ag_additive", "catalyst", "AgSbF6", ev, amounts=[amount("catalyst_loading", 5, "mol%", P[2])]),
            part("solvent", "solvent", solvent_label, ev, amounts=[amount("volume", 2, "mL", P[2])]),
        ]
        outs = yield_field(f"isolated_yield_{pa}", ya, P[2], pa)
        unresolved = ["Compound-specific workup, purification, and verified connectivity are not reported in the covered main text."]
        if entry == 7:
            parts.append(product("4g", ev, "hydrated product 4g"))
            outs += yield_field("reported_yield_hydrated_4g", 31, P[2], "4g", basis=None)
            unresolved.append("Page 6 gives crystal data for 2g but no independent reaction procedure.")
        records.append(experimental(f"table2_entry{entry}_method_a_{pa}", "substrate_scope_entry", ev, parts, time={"number": 1, "unit": "h"}, temperature=temp, solvent=solvent_label, outcomes=outs, unresolved=unresolved))

# Table 2 footnote b also reports a distinct standard-Method-A attempt for 1e:
# CH2Cl2/r.t. rather than the successful DCE/reflux override, with 76% 1e recovered.
ev = P[2]
records.append(experimental(
    "table2_entry5_method_a_standard_ch2cl2_recovery",
    "reported_experiment",
    ev,
    [
        substrate("1e", ev, [range_amount("reaction_scale", 0.15, 0.50, "mmol", P[2], "0.15-0.50 mmol")]),
        product("2e_expected", ev, "expected cyclopentene 2e"),
        part("au_cat", "catalyst", "[AuCl(PPh3)]", ev, amounts=[amount("catalyst_loading", 5, "mol%", P[2])]),
        part("ag_additive", "catalyst", "AgSbF6", ev, amounts=[amount("catalyst_loading", 5, "mol%", P[2])]),
        part("solvent", "solvent", "dichloromethane", ev, amounts=[amount("volume", 2, "mL", P[2])]),
    ],
    time={"number": 1, "unit": "h"},
    temperature="r.t.",
    solvent="dichloromethane",
    outcomes=[fld("recovered_starting_material_yield", {"number": 76, "unit": "%"}, P[2], ["1e"]), fld("reported_yield_2e", None)],
    unresolved=["The footnote reports only 76% recovered 1e for the standard CH2Cl2 Method A attempt; it does not state the 2e yield or workup."],
))

# Table 2 Method B. Entry 1 is also Table 3 entry 7 and the detailed Method B procedure.
for entry, s, pa, ya, pb, yb in table2:
    ev = P[2]
    rid = f"table2_entry{entry}_method_b_{pb}"
    if entry == 1:
        rid += "_table3_entry7"
        ev = P[2] + P[3] + P[5]
    parts = [
        substrate(s, ev, [amount("amount", 0.25, "mmol", P[2])]),
        product(pb, ev),
        part("pd_cat", "catalyst", "[PdCl2(PhCN)2]", ev, amounts=[range_amount("method_B_catalyst_loading", 5, 7, "mol%", P[2], "5-7 mol%")]),
        part("base", "reagent", "potassium carbonate", ev, amounts=[amount("equivalents", 2, "equiv", P[2])]),
        part("allyl_bromide", "reactant", "allyl bromide", ev, amounts=[amount("equivalents", 2, "equiv", P[2])]),
        part("solvent", "solvent", "acetonitrile", ev, amounts=[amount("volume", 2, "mL", P[2])]),
    ]
    outs = yield_field(f"isolated_yield_{pb}", yb, P[2], pb)
    unresolved = ["Compound-specific workup and verified structures are missing for this scope row."]
    workup = purification = operation = None
    if entry == 8:
        parts.append(product("5h", ev, "carbocyclic product 5h"))
        outs += yield_field("reported_yield_5h", 30, P[2], "5h", basis=None)
    if entry == 1:
        parts[0]["amounts"] = [fld("mass", {"number": 28, "unit": "mg"}, P[5]), fld("amount", {"number": 0.15, "unit": "mmol"}, P[5])]
        parts[1]["amounts"] = [fld("isolated_mass", {"number": 25, "unit": "mg"}, P[5])]
        parts[2]["amounts"] += [fld("mass", {"number": 4, "unit": "mg"}, P[5]), fld("amount", {"number": 0.010, "unit": "mmol"}, P[5]), fld("table3_catalyst_loading", {"number": 5, "unit": "mol%"}, P[3])]
        parts[3]["amounts"] += [fld("mass", {"number": 42, "unit": "mg"}, P[5]), fld("amount", {"number": 0.30, "unit": "mmol"}, P[5])]
        parts[4]["amounts"] += [fld("mass", {"number": 27, "unit": "mg"}, P[5]), fld("amount", {"number": 0.22, "unit": "mmol"}, P[5])]
        operation = "flame-dried Schlenk tube; TLC monitoring with petroleum ether/ethyl acetate 10:1; rotary evaporation"
        workup = "rotary evaporation"
        purification = "flash chromatography on silica gel, petroleum ether/ethyl ether 20:1"
        unresolved = ["Method B table conditions use 2 equiv allyl bromide at 0.25 mmol scale, while the detailed 0.15 mmol example uses 0.22 mmol allyl bromide; both source statements are retained."]
    records.append(experimental(rid, "substrate_scope_entry", ev, parts, time={"number": 4, "unit": "h"}, temperature="r.t.", solvent="acetonitrile", outcomes=outs, workup=workup, purification=purification, operation=operation, unresolved=unresolved))

# Table 3 entries 1-6. Entry 7 is merged with Table 2 Method B entry 1.
t3 = [
    (1, "[PdCl2(MeCN)2]", 5, 0, 0),
    (2, "[PdCl2(MeCN)2]", 5, 0, 0),
    (3, "[PdCl2(MeCN)2]", 4, 56, 0),
    (4, "PdCl2", 4, 47, 0),
    (5, "Pd(OAc)2", 4, 62, 0),
    (6, "[PdCl2(PPh3)2]", 3, 0, 95),
]
for entry, cat, hours, y3, y6 in t3:
    ev = P[3]
    parts = [substrate("1a", ev), product("3a", ev), product("6a", ev), part("pd_cat", "catalyst", cat, ev, amounts=[amount("catalyst_loading", 5, "mol%", P[3])]), part("solvent", "solvent", "acetonitrile", ev), part("base", "reagent", "potassium carbonate", ev, amounts=[amount("equivalents", 2, "equiv", P[3])])]
    if entry != 1:
        parts.append(part("allyl_bromide", "reactant", "allyl bromide", ev, amounts=[amount("equivalents", 2, "equiv", P[3])]))
    if entry == 2:
        parts = [p for p in parts if p["entity_id"] != "base"]
    outs = yield_field("isolated_yield_3a", y3, P[3], "3a") + yield_field("isolated_yield_6a", y6, P[3], "6a")
    unresolved = ["Absolute scale, solvent volume, workup, and purification are not reported for this catalyst-screen row."]
    if entry == 1:
        outs.append(fld("recovered_starting_material_yield", {"number": 39, "unit": "%"}, P[3], ["1a"]))
    if entry == 2:
        outs.append(fld("recovered_starting_material_yield", {"number": 59, "unit": "%"}, P[3], ["1a"]))
    records.append(experimental(f"table3_entry{entry}", "optimization_entry", ev, parts, time={"number": hours, "unit": "h"}, temperature="r.t.", solvent="acetonitrile", outcomes=outs, unresolved=unresolved))

# Tables 4 and 5. Table 4 entry 9 and Table 5 entry 1 are the same optimized condition.
t4 = [
    (1, "triethylamine", 4, "NR", 91),
    (2, "sodium carbonate", 12, "trace", None),
    (3, "sodium bicarbonate", 12, "trace", None),
    (4, "potassium acetate", 24, 0, None),
    (5, "potassium phthalimide", 24, "complicated", None),
    (6, "potassium tert-butoxide", 4, "complicated", None),
    (7, "potassium fluoride", 4, 44, None),
    (8, "potassium hydroxide", 4, 56, None),
    (9, "potassium carbonate", 4, 66, None),
    (10, "potassium phosphate trihydrate", 4, 66, None),
]
for entry, base, hours, result, recovered in t4:
    rid = f"table4_entry{entry}"
    if entry == 9:
        rid += "_table5_entry1"
    ev = P[3]
    parts = [substrate("1a", ev), product("3a", ev), part("pd_cat", "catalyst", "[Pd(dba)2]", ev, amounts=[amount("catalyst_loading", 5, "mol%", P[3])]), part("base", "reagent", base, ev, amounts=[amount("equivalents", 2, "equiv", P[3])]), part("allyl_bromide", "reactant", "allyl bromide", ev, amounts=[amount("equivalents", 1.2, "equiv", P[3])]), part("solvent", "solvent", "acetonitrile", ev)]
    outs = yield_field("isolated_yield_3a", result, P[3], "3a")
    if recovered is not None:
        outs.append(fld("recovered_starting_material_yield", {"number": recovered, "unit": "%"}, P[3], ["1a"]))
    records.append(experimental(rid, "optimization_entry", ev, parts, time={"number": hours, "unit": "h"}, temperature="r.t.", solvent="acetonitrile", outcomes=outs, unresolved=["Absolute scale, solvent volume, workup, and purification are not reported for this base-screen condition."]))

t5 = [
    (2, "toluene", 24, 40),
    (3, "dichloromethane", 24, 56),
    (4, "nitromethane", 19, 58),
    (5, "THF", 27, 52),
    (9, "DMF", 10, 49),
    (7, "acetone", 5, 63),
]
for entry, solv, hours, yld in t5:
    ev = P[3]
    parts = [substrate("1a", ev), product("3a", ev), part("pd_cat", "catalyst", "[Pd(dba)2]", ev, amounts=[amount("catalyst_loading", 5, "mol%", P[3])]), part("base", "reagent", "potassium carbonate", ev, amounts=[amount("equivalents", 2, "equiv", P[3])]), part("allyl_bromide", "reactant", "allyl bromide", ev, amounts=[amount("equivalents", 1.2, "equiv", P[3])]), part("solvent", "solvent", solv, ev)]
    records.append(experimental(f"table5_entry{entry}", "optimization_entry", ev, parts, time={"number": hours, "unit": "h"}, temperature="r.t.", solvent=solv, outcomes=yield_field("isolated_yield_3a", yld, P[3], "3a"), unresolved=["Absolute scale, solvent volume, workup, and purification are not reported; the source prints DMF as entry 9."]))

# Table 6 Method C, symmetric allylic halides.
t6 = [
    (1, "1f", "7a", "allyl bromide", "3f", 70),
    (2, "1h", "7a", "allyl bromide", "3h", 61),
    (3, "1c", "7b", "2-phenylallyl bromide", "3cb", 59),
    (4, "1e", "7b", "2-phenylallyl bromide", "3eb", 51),
    (5, "1e", "7c", "2-n-butylallyl bromide", "3ec", 66),
    (6, "1e", "7d", "methallyl chloride", "3ed", 55),
    (7, "1i", "7b", "2-phenylallyl bromide", "3ib", 52),
    (8, "1j", "7b", "2-phenylallyl bromide", "3jb", 53),
]
for entry, s, hal, hal_name, prod_label, yld in t6:
    ev = P[4] + (P[5] if entry == 3 else [])
    parts = [substrate(s, ev, [amount("amount", 0.25, "mmol", P[4])]), product(prod_label, ev), part("pd_cat", "catalyst", "[Pd(dba)2]", ev, amounts=[amount("catalyst_loading", 5, "mol%", P[4])]), part("base", "reagent", "potassium carbonate", ev, amounts=[amount("equivalents", 1.2, "equiv", P[4])]), part(hal, "reactant", hal, ev, hal_name, amounts=[amount("equivalents", 2, "equiv", P[4])]), part("solvent", "solvent", "acetonitrile", ev, amounts=[amount("volume", 2, "mL", P[4])])]
    outs = yield_field(f"isolated_yield_{prod_label}", yld, P[4], prod_label)
    unresolved = ["Method C prose on page 3 says 2 equiv K2CO3, whereas the Table 6 footnote and detailed example use 1.2 equiv; the structured row follows the table footnote."]
    workup = purification = operation = None
    duration = {"number": 4, "unit": "h"}
    if entry == 2:
        parts.append(product("5h", ev, "carbocyclic product 5h"))
        outs += yield_field("reported_yield_5h", 22, P[4], "5h", basis=None)
    if entry == 3:
        parts[0]["amounts"] += [fld("mass", {"number": 45, "unit": "mg"}, P[5])]
        parts[1]["amounts"] += [fld("isolated_mass", {"number": 43, "unit": "mg"}, P[5])]
        parts[2]["amounts"] += [fld("mass", {"number": 7, "unit": "mg"}, P[5]), fld("amount", {"number": 0.0122, "unit": "mmol"}, P[5])]
        parts[3]["amounts"] += [fld("mass", {"number": 42, "unit": "mg"}, P[5]), fld("amount", {"number": 0.30, "unit": "mmol"}, P[5])]
        parts[4]["amounts"] += [fld("mass", {"number": 99, "unit": "mg"}, P[5]), fld("amount", {"number": 0.50, "unit": "mmol"}, P[5])]
        duration = {"number": 13, "unit": "h"}
        operation = "flame-dried Schlenk tube; TLC monitoring with petroleum ether/ethyl acetate 10:1; rotary evaporation"
        workup = "rotary evaporation"
        purification = "flash chromatography on silica gel, petroleum ether/diethyl ether 50:1"
        unresolved.append("Table 6 reports the common Method C duration as 4 h, while the detailed 3cb example reports 13 h; both source statements are retained, with the detailed value used for the exact example.")
    records.append(experimental(f"table6_entry{entry}_{prod_label}", "substrate_scope_entry", ev, parts, time=duration, temperature="r.t.", solvent="acetonitrile", outcomes=outs, workup=workup, purification=purification, operation=operation, unresolved=unresolved))

# Table 7 Method C, unsymmetric allylic halides.
t7 = [
    (1, "1a", "7e", "(E)-cinnamyl bromide", "(E)-3ae", 58),
    (2, "1e", "7e", "(E)-cinnamyl bromide", "(E)-3ee", 49),
    (3, "1e", "7f", "3-chloro-1-butene", "(E)-3ef", 56),
    (4, "1i", "7f", "3-chloro-1-butene", "(E)-3if", 53),
]
for entry, s, hal, hal_name, prod_label, yld in t7:
    ev = P[4]
    parts = [substrate(s, ev, [amount("amount", 0.25, "mmol", P[4])]), product(prod_label, ev), part("pd_cat", "catalyst", "[Pd(dba)2]", ev, amounts=[amount("catalyst_loading", 5, "mol%", P[4])]), part("base", "reagent", "potassium carbonate", ev, amounts=[amount("equivalents", 1.2, "equiv", P[4])]), part(hal, "reactant", hal, ev, hal_name, amounts=[amount("equivalents", 2, "equiv", P[4])]), part("solvent", "solvent", "acetonitrile", ev, amounts=[amount("volume", 2, "mL", P[4])])]
    records.append(experimental(f"table7_entry{entry}_{prod_label.replace('(', '').replace(')', '')}", "substrate_scope_entry", ev, parts, time={"number": 4, "unit": "h"}, temperature="r.t.", solvent="acetonitrile", outcomes=yield_field(f"isolated_yield_{prod_label}", yld, P[4], prod_label), notes=["The allylic substituent is reported at the terminal position of the E carbon-carbon double bond."], unresolved=["Table 7 does not provide compound-specific scale, workup, purification, or independently verified product structures."]))

# Page 4 proposed Au/Pd pathways.
records.append(conceptual(
    "scheme2_proposed_gold_palladium_mechanisms",
    "mechanism",
    P[4] + P[5],
    [part("generic_1", "reactant", "generic 2-(2',3'-allenyl)acetylacetate 1", P[4]), part("generic_2", "product", "cyclopentene products 2", P[4]), part("generic_3", "product", "4,5-dihydrofuran products 3", P[4])],
    ["The authors propose Au-mediated C-attack/5-endo cyclization and Pd-mediated O-attack/5-exo cyclization, with separate Pd(II) and Pd(0) allylation pathways."],
    ["The intermediates and elementary steps are proposed rather than independently executed experiments; generic structures remain unverified."],
))


OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2))

ids = {r["source_reaction_id"]: r["record_id"] for r in records}
all_experimental = [r["record_id"] for r in records if r["record_kind"] in {"reported_experiment", "optimization_entry", "substrate_scope_entry"}]

def recs(prefixes):
    return [r["record_id"] for r in records if any(r["source_reaction_id"].startswith(p) for p in prefixes)]

coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1,
            "state": "attempted",
            "regions": [
                {"region": "title, abstract, introduction, and lower-right Scheme 1", "finding": "Scheme 1 is a generic map of possible cyclization modes, not an executed reaction; abstract-level claims are linked to later row-level records rather than duplicated.", "evidence_ids": P[1]},
            ],
            "record_ids": [ids["scheme1_possible_cyclization_modes"]],
            "unresolved": ["The main text states that Supporting Information is available online, but no SI file is supplied or explicitly associated."],
        },
        {
            "page": 2,
            "state": "attempted",
            "regions": [
                {"region": "left-center Table 1 and footnotes", "finding": "All six Au/Ag optimization entries were extracted independently, including recovery, combined-yield/ratio footnotes, and the allyl-bromide condition.", "evidence_ids": P[2]},
                {"region": "upper-right Table 2 and footnotes", "finding": "Both Method A and Method B conditions were represented for all eight substrates; exact duplicates with Table 1/Table 3 are merged, while catalyst-distinct conditions remain separate.", "evidence_ids": P[2]},
                {"region": "lower-right Figure 1", "finding": "ORTEP of 2g is linked to the Table 2 Method A entry for 1g and is not an additional reaction.", "evidence_ids": P[2]},
            ],
            "record_ids": recs(["table1_", "table2_"]),
            "unresolved": ["Most scope rows omit compound-specific workup, purification, and verified structures; Table 2 generally does not state yield basis beyond its isolated-yield heading."],
        },
        {
            "page": 3,
            "state": "attempted",
            "regions": [
                {"region": "left Table 3 and footnotes", "finding": "Seven Pd(II) catalyst-screen rows were inventoried; entry 7 is merged with Table 2 Method B entry 1 and the detailed Method B procedure.", "evidence_ids": P[3]},
                {"region": "upper-right Table 4 and footnote", "finding": "All ten base-screen rows were extracted, preserving NR, trace, complicated, zero, and recovered-starting-material outcomes.", "evidence_ids": P[3]},
                {"region": "lower-right Table 5", "finding": "All seven solvent-screen rows were inventoried; the exact MeCN/K2CO3 condition is merged with Table 4 entry 9.", "evidence_ids": P[3]},
            ],
            "record_ids": recs(["table3_", "table4_", "table5_"]) + [ids["table2_entry1_method_b_3a_table3_entry7"]],
            "unresolved": ["Optimization rows omit absolute scale, workup, and purification; the source numbers the DMF solvent row as entry 9."],
        },
        {
            "page": 4,
            "state": "attempted",
            "regions": [
                {"region": "upper-left Table 6 and footnotes", "finding": "All eight Method C symmetric-allylic-halide scope rows were extracted; entry 2 includes the 5h byproduct and entry 3 links to its exact page-5 procedure.", "evidence_ids": P[4]},
                {"region": "lower-left Table 7", "finding": "All four unsymmetric-allylic-halide rows were extracted with E product labels and isolated yields.", "evidence_ids": P[4]},
                {"region": "right-column Scheme 2 and mechanistic prose", "finding": "The Au/Pd pathways are classified as a proposed mechanism, not stepwise reported experiments.", "evidence_ids": P[4]},
            ],
            "record_ids": recs(["table6_", "table7_"]) + [ids["scheme2_proposed_gold_palladium_mechanisms"]],
            "unresolved": ["Method C prose on page 3 says 2 equiv K2CO3, whereas Table 6 and the detailed 3cb procedure use 1.2 equiv; complex structures remain unverified."],
        },
        {
            "page": 5,
            "state": "attempted",
            "regions": [
                {"region": "left-column general experimental section", "finding": "General dry-argon and solvent-drying statements were retained; the starting-material preparation is cited to prior work and is not reconstructed as a present-paper procedure.", "evidence_ids": P[5]},
                {"region": "Methods A, B, and C across both columns", "finding": "Exact quantities, operations, isolated masses, and chromatography were merged into the matching Table 1/2/3/6 records rather than duplicated.", "evidence_ids": P[5]},
                {"region": "upper-left mechanistic continuation and conclusion", "finding": "Narrative continuation supports the proposed Scheme 2 record; no additional wet experiment is introduced.", "evidence_ids": P[5]},
            ],
            "record_ids": all_experimental + [ids["scheme2_proposed_gold_palladium_mechanisms"]],
            "unresolved": ["The Method B detailed example uses 0.22 mmol allyl bromide for 0.15 mmol substrate, while the table's general Method B states 2 equiv; Table 6 reports 4 h for Method C while the detailed 3cb example reports 13 h."],
        },
        {
            "page": 6,
            "state": "attempted",
            "regions": [
                {"region": "both columns of references", "finding": "The page consists of cited literature and does not contain a new present-paper reaction table, arrow, or procedure.", "evidence_ids": P[6]},
                {"region": "upper-right reference 10 crystal-data paragraph", "finding": "Crystal data for 2g are linked as characterization context to Table 2 Method A entry 7, not counted as a reaction.", "evidence_ids": P[6]},
            ],
            "record_ids": [ids["table2_entry7_method_a_2g"]],
            "unresolved": ["The external CCDC file and online Supporting Information are not supplied or explicitly associated and were not imported."],
        },
    ],
}
COVERAGE.parent.mkdir(parents=True, exist_ok=True)
COVERAGE.write_text(json.dumps(coverage, ensure_ascii=False, indent=2))

tasks = json.loads(TASKS.read_text())
for task in tasks:
    if task["document_id"] == DOC and task["task_id"] in {f"{DOC}:page{i}:text" for i in range(1, 7)}:
        task["state"] = "attempted"
TASKS.write_text(json.dumps(tasks, ensure_ascii=False, indent=2))

print(json.dumps({"records": len(records), "experimental": len(all_experimental), "coverage_pages": [p["page"] for p in coverage["pages"]]}, ensure_ascii=False))
