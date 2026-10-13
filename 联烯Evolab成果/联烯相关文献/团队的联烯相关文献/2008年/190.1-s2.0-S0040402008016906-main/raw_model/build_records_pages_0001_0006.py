#!/usr/bin/env python3
"""Build source-linked machine records for PDF pages 1-6 of doc_b77579854e4d0662."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "runs/current/raw_model/records_pages_0001_0006.json"
COVERAGE = ROOT / "runs/current/coverage/pages_0001_0006.json"
TASKS = ROOT / "runs/current/tasks.json"
DOC = "doc_b77579854e4d0662"


def ev(page):
    return [f"{DOC}:page{page}:text", f"{DOC}:page{page}:image"]


def fact(value, evidence=()):
    return {
        "value": value,
        "evidence_ids": list(dict.fromkeys(evidence)),
        "verification": "missing" if value is None else "unreviewed",
    }


def q(number, unit, **extra):
    value = {"number": number, "unit": unit}
    value.update(extra)
    return value


def fld(name, value, evidence=(), targets=None):
    item = {"name": name, "fact": fact(value, evidence)}
    if targets:
        item["target_entity_ids"] = targets
    return item


def participant(entity_id, role, label, evidence, amounts=(), name=None, smiles=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence) if name else fact(None),
        "smiles": fact(smiles, evidence) if smiles else fact(None),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": list(amounts),
    }


def amount(name, value, evidence):
    return fld(name, value, evidence)


def missing_conditions(evidence, *, temperature=None, time=None, atmosphere=None,
                       workup=None, purification=None):
    return [
        fld("temperature", temperature, evidence if temperature is not None else ()),
        fld("reaction_time", time, evidence if time is not None else ()),
        fld("atmosphere", atmosphere, evidence if atmosphere is not None else ()),
        fld("workup", workup, evidence if workup is not None else ()),
        fld("purification", purification, evidence if purification is not None else ()),
    ]


def record(rid, kind, evidence, participants, steps, outcomes, notes=(), unresolved=()):
    return {
        "record_id": f"{DOC}:{rid}",
        "document_id": DOC,
        "source_reaction_id": rid,
        "record_kind": kind,
        "status": "needs_review",
        "completeness": "partial",
        "evidence_ids": list(dict.fromkeys(evidence)),
        "participants": participants,
        "steps": steps,
        "outcomes": outcomes,
        "notes": [fact(x, evidence) for x in notes],
        "review": {
            "method": "model",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": list(unresolved),
        },
    }


SIMPLE_SMILES = {
    "DCM": "ClCCl",
    "THF": "C1CCOC1",
    "DMF": "CN(C)C=O",
    "1,4-dioxane": "O1CCOCC1",
    "toluene": "Cc1ccccc1",
    "diethyl ether": "CCOCC",
    "2a": "Ic1ccccc1",
    "2b": "Cc1ccc(I)cc1",
    "2c": "Cc1cccc(I)c1",
    "2d": "COc1ccc(I)cc1",
    "2e": "COC(=O)c1ccc(I)cc1",
    "2f": "CC(=O)c1ccc(I)cc1",
    "2g": "Brc1ccc(I)cc1",
    "2h": "N#Cc1ccc(I)cc1",
    "2i": "Ic1ccc(-c2ccccc2)cc1",
    "2j": "CCCC/C=C/I",
    "2k": "I/C=C/c1ccccc1",
    "2m": "Ic1cccs1",
    "2n": "Brc1ccc(-c2ccc(I)cc2)cc1",
}


records = []


# Scheme 1 and sections 4.2.1-4.2.4: four distinct starting-material preparations.
starting = [
    {
        "label": "1a", "name": "dimethyl 2-(1',2'-bis(benzyloxycarbonyl)hydrazinyl)-2-(2'',3''-butadienyl)malonate",
        "pages": [2, 3, 4], "cu": (36, 0.099), "lig": (47, 0.14),
        "substrate": ("dimethyl 2-(2',3'-butadienyl)malonate", 184, 1.00),
        "azo": ("dibenzyl azodicarboxylate", 600, 1.21), "solvent_volumes": [5, 5],
        "product_mass": 425, "yield": 88, "time": "TLC completion",
        "workup": "solvent removed under vacuum",
        "purification": "flash chromatography on silica gel; petroleum ether/ethyl acetate 30:1 to 10:1 to 5:1",
        "notes": ["The printed 600 mg/1.21 mmol dibenzyl azodicarboxylate pair was retained without recalculation.",
                  "The product was difficult to purify and was used directly in the cyclization without further characterization."],
    },
    {
        "label": "1b", "name": "dibenzyl 2-(1',2'-bis(benzyloxycarbonyl)hydrazinyl)-2-(2'',3''-butadienyl)malonate",
        "pages": [2, 4], "cu": (90, 0.25), "lig": (90, 0.27),
        "substrate": ("dibenzyl 2-(2',3'-butadienyl)malonate", 520, 1.42),
        "azo": ("dibenzyl azodicarboxylate", 610, 1.84), "solvent_volumes": [20],
        "product_mass": 693, "yield": 77, "time": None, "workup": None, "purification": None,
        "notes": ["Scheme 1 prints nominal 10 mol% Cu(OTf)2 and 10 mol% Ph-BOX; the detailed paragraph gives the retained exact masses/mmol."],
    },
    {
        "label": "1c", "name": "diethyl 2-(1',2'-bis(ethoxycarbonyl)hydrazinyl)-2-(2'',3''-butadienyl)malonate",
        "pages": [2, 4], "cu": (40, 0.11), "lig": (36, 0.10),
        "substrate": ("diethyl 2-(2',3'-butadienyl)malonate", 212, 1.0),
        "azo": ("diethyl azodicarboxylate", 250, 1.2), "solvent_volumes": [10],
        "product_mass": 328, "yield": 85, "time": None, "workup": None, "purification": None,
        "notes": ["Scheme 1 supplies room temperature; the abbreviated compound paragraph does not restate time, workup, or purification."],
    },
    {
        "label": "1d", "name": "diethyl 2-(1',2'-bis(benzyloxycarbonyl)hydrazinyl)-2-(2'',3''-butadienyl)malonate",
        "pages": [2, 4], "cu": (7, 0.019), "lig": (7, 0.021),
        "substrate": ("diethyl 2-(2',3'-butadienyl)malonate", 44, 0.21),
        "azo": ("dibenzyl azodicarboxylate", 79, 0.24), "solvent_volumes": [],
        "product_mass": 57, "yield": 54, "time": None, "workup": None, "purification": None,
        "notes": ["Scheme 1 identifies DCM and room temperature, but the abbreviated detailed paragraph does not state a DCM volume."],
    },
]

for item in starting:
    evidence = sum((ev(p) for p in item["pages"]), [])
    p_cu = participant("cu_otf2", "catalyst", "Cu(OTf)2", evidence, [
        amount("mass", q(item["cu"][0], "mg"), evidence), amount("amount", q(item["cu"][1], "mmol"), evidence),
        amount("scheme_loading", q(10, "mol%"), ev(2)),
    ])
    p_lig = participant("ph_box", "catalyst", "(R,R)-Ph-BOX", evidence, [
        amount("mass", q(item["lig"][0], "mg"), evidence), amount("amount", q(item["lig"][1], "mmol"), evidence),
        amount("scheme_loading", q(10, "mol%"), ev(2)),
    ])
    sub_name, sub_mass, sub_mmol = item["substrate"]
    azo_name, azo_mass, azo_mmol = item["azo"]
    parts = [
        p_cu, p_lig,
        participant("allene_malonate", "reactant", sub_name, evidence, [amount("mass", q(sub_mass, "mg"), evidence), amount("amount", q(sub_mmol, "mmol"), evidence)]),
        participant("azodicarboxylate", "reactant", azo_name, evidence, [amount("mass", q(azo_mass, "mg"), evidence), amount("amount", q(azo_mmol, "mmol"), evidence)]),
        participant("product", "product", item["label"], evidence, [amount("isolated_mass", q(item["product_mass"], "mg"), evidence)], name=item["name"]),
    ]
    solvent_amounts = [amount(f"volume_stage_{i+1}", q(v, "mL"), evidence) for i, v in enumerate(item["solvent_volumes"])]
    parts.append(participant("dcm", "solvent", "DCM", evidence, solvent_amounts, name="dichloromethane", smiles=SIMPLE_SMILES["DCM"]))
    steps = []
    if item["label"] == "1a":
        steps.append({"step_id": "catalyst_preformation", "participant_ids": ["cu_otf2", "ph_box", "dcm"], "conditions": [
            fld("temperature", "r.t.", ev(3)), fld("reaction_time", q(1, "h"), ev(3)), fld("atmosphere", "argon", ev(3)),
        ]})
    steps.append({"step_id": "michael_addition", "participant_ids": [x["entity_id"] for x in parts], "conditions": missing_conditions(
        evidence, temperature="r.t.", time=item["time"], atmosphere="argon", workup=item["workup"], purification=item["purification"]
    )})
    records.append(record(
        f"scheme1_prepare_{item['label']}", "reported_experiment", evidence, parts, steps,
        [fld("reported_yield", q(item["yield"], "%"), evidence, ["product"]),
         fld("yield_measurement_basis", "isolated after flash chromatography" if item["label"] == "1a" else None,
             evidence if item["label"] == "1a" else (), ["product"])],
        notes=item["notes"],
        unresolved=["Product and chiral-ligand structures are machine-unverified.",
                    "Reaction duration is not numerically reported." if item["time"] is None else "TLC completion is qualitative, not a numeric duration.",
                    "Workup and purification are not restated for this abbreviated preparation." if item["label"] != "1a" else "No SI was supplied or associated."],
    ))


# Table 1: solvent/base optimization for 1a + PhI -> 3aa.
table1 = [
    (1, "DMF", 0.4, 80, 72, 63, "Pd(OAc)2"),
    (2, "1,4-dioxane", 0.4, 80, 69, 71, "Pd(OAc)2"),
    (3, "toluene", 0.4, 80, 68, 62, "Pd(OAc)2"),
    (4, "THF/DMF 1:1", 0.4, 80, 57, 77, "Pd(OAc)2"),
    (5, "THF", 0.4, 80, 54, 81, "Pd(OAc)2"),
    (6, "THF", 0.45, 80, 67, 82, "Pd(OAc)2"),
    (7, "THF", 0.5, 80, 61, 82, "Pd(OAc)2"),
    (8, "THF", 0.45, 70, 75, 84, "Pd(dba)2"),
]

for entry, solvent, silver_eq, temp, yld, ee_value, pd in table1:
    pages = [2] + ([4] if entry == 5 else [])
    evidence = sum((ev(p) for p in pages), []) + ev(3)
    solvent_key = solvent if solvent in SIMPLE_SMILES else None
    parts = [
        participant("1a", "reactant", "1a", evidence, [amount("amount", q(0.2, "mmol"), ev(2))] + ([amount("mass", q(97, "mg"), ev(4))] if entry == 5 else [])),
        participant("2a", "reactant", "2a", evidence, [amount("amount", q(0.24, "mmol"), ev(2))] + ([amount("detailed_amount", q(0.25, "mmol"), ev(4)), amount("mass", q(50, "mg"), ev(4))] if entry == 5 else []), name="iodobenzene", smiles=SIMPLE_SMILES["2a"]),
        participant("ag3po4", "reagent", "Ag3PO4", evidence, [amount("equivalents", q(silver_eq, "equiv"), ev(2))] + ([amount("mass", q(34, "mg"), ev(4)), amount("detailed_amount", q(0.081, "mmol"), ev(4))] if entry == 5 else [])),
        participant("pd", "catalyst", pd, evidence, [amount("loading", q(5, "mol%"), ev(2))]),
        participant("ligand", "catalyst", "(R,R)-Bn-BOX", evidence, [amount("loading", q(10, "mol%"), ev(2))]),
        participant("solvent", "solvent", solvent, evidence, [amount("volume", q(2, "mL"), ev(2))], smiles=SIMPLE_SMILES.get(solvent_key)),
        participant("3aa", "product", "(S)-3aa", evidence, ([amount("isolated_mass", q(60, "mg"), ev(4))] if entry == 5 else [])),
    ]
    steps = [{"step_id": "coupling_cyclization", "participant_ids": [p["entity_id"] for p in parts], "conditions": missing_conditions(
        evidence, temperature=q(temp, "°C"), time=None, atmosphere="argon", workup=None, purification=None
    )}]
    if entry == 5:
        notes = ["The detailed paragraph gives 0.25 mmol PhI, while the table footnote gives 0.24 mmol; both printed values are retained."]
    else:
        notes = []
    records.append(record(
        f"table1_entry{entry}", "optimization_entry", evidence, parts, steps,
        [fld("isolated_yield", q(yld, "%"), ev(2) + (ev(4) if entry == 5 else []), ["3aa"]),
         fld("product_ee", q(ee_value, "%"), ev(2) + (ev(4) if entry == 5 else []), ["3aa"]),
         fld("yield_measurement_basis", "isolated yield", ev(2), ["3aa"]),
         fld("ee_measurement_basis", "chiral HPLC", ev(2), ["3aa"])],
        notes=notes,
        unresolved=["Reaction time is not reported.", "Workup and purification are not reported for this optimization row.", "Complex structures are unverified."],
    ))


# Table 2: ligand screen for 1b + PhI -> 3ba.
table2 = [
    (1, "L1", q(75, "%"), q(83, "%")),
    (2, "L2", "Complex", "table dash (–)"),
    (3, "L3", "NR (no reaction)", "table dash (–)"),
    (4, "L4", q(75, "%"), q(80, "%")),
    (5, "L5", q(69, "%"), q(83, "%")),
    (6, "L6", "NR (no reaction)", "table dash (–)"),
]

for entry, lig, yld, ee_value in table2:
    evidence = ev(2) + ev(3)
    parts = [
        participant("1b", "reactant", "1b", evidence, [amount("amount", q(0.1, "mmol"), ev(2))]),
        participant("2a", "reactant", "2a", evidence, [amount("amount", q(0.12, "mmol"), ev(2))], name="iodobenzene", smiles=SIMPLE_SMILES["2a"]),
        participant("ag3po4", "reagent", "Ag3PO4", evidence, [amount("amount", q(0.045, "mmol"), ev(2)), amount("equivalents", q(0.45, "equiv"), ev(2))]),
        participant("pd", "catalyst", "Pd(dba)2", evidence, [amount("loading", q(5, "mol%"), ev(2))]),
        participant("ligand", "catalyst", lig, evidence, [amount("loading", q(10, "mol%"), ev(2))]),
        participant("thf", "solvent", "THF", evidence, [amount("volume", q(2, "mL"), ev(2))], smiles=SIMPLE_SMILES["THF"]),
        participant("3ba", "product", "3ba", evidence),
    ]
    records.append(record(
        f"table2_entry{entry}", "optimization_entry", evidence, parts,
        [{"step_id": "coupling_cyclization", "participant_ids": [p["entity_id"] for p in parts], "conditions": missing_conditions(
            evidence, temperature=q(70, "°C"), time=None, atmosphere="argon", workup=None, purification=None
        )}],
        [fld("isolated_yield", yld, ev(2), ["3ba"]), fld("product_ee", ee_value, ev(2), ["3ba"]),
         fld("yield_measurement_basis", "isolated yield", ev(2), ["3ba"]), fld("ee_measurement_basis", "chiral HPLC", ev(2), ["3ba"])],
        notes=["The Table 2 yield header prints 3aa although the reaction drawing and prose identify product 3ba."],
        unresolved=["Reaction time, workup, and purification are not reported.", "Ligand and product structures remain unverified."],
    ))


# Table 3 plus compound-specific paragraphs on pages 4-6.
scope = [
    (1, "1b", "2a", "3ba", 74, 83, 4, (4, .0071), (6, .016), (27, .064), (97, .15), (37, .18), 81),
    (2, "1b", "2b", "3bb", 72, 82, 4, (4, .0071), (5, .014), (28, .067), (93, .15), (41, .19), 76),
    (3, "1b", "2c", "3bc", 68, 83, 4, (4, .0071), (6, .016), (28, .067), (96, .15), (39, .18), 74),
    (4, "1b", "2d", "3bd", 77, 84, 5, (4, .0071), (6, .016), (28, .067), (99, .16), (42, .18), 89),
    (5, "1b", "2e", "3be", 71, 81, 5, (4, .0071), (6, .016), (28, .067), (93, .15), (49, .19), 80),
    (6, "1b", "2f", "3bf", 63, 81, 5, (3, .0053), (4, .011), (20, .048), (69, .11), (37, .15), 51),
    (7, "1b", "2g", "3bg", 75, 80, 5, (3, .0053), (4, .011), (19, .045), (64, .10), (37, .15), 60),
    (8, "1b", "2h", "3bh", 69, 81, 5, (3, .0053), (4, .011), (19, .045), (63, .099), (30, .13), 50),
    (9, "1b", "2i", "3bi", 74, 81, 5, (3, .0053), (4, .011), (20, .048), (63, .099), (35, .12), 58),
    (10, "1b", "2j", "3bj", 51, 80, 5, (3, .0053), (4, .011), (19, .045), (63, .099), (29, .14), 37),
    (11, "1b", "2k", "3bk", 71, 75, 6, (3, .0053), (4, .011), (19, .045), (63, .099), (29, .13), 52),
    (12, "1b", "2l", "3bl", 73, 77, 6, (3, .0053), (5, .014), (19, .045), (68, .11), (35, .16), 57),
    (13, "1b", "2m", "3bm", 70, 82, 6, (3, .0053), (5, .014), (19, .045), (49, .077), (25, .12), 39),
    (14, "1b", "2g", "R-3bg", 75, 81, 6, (3, .0053), (5, .014), (19, .045), (60, .094), (37, .15), 56),
    (15, "1b", "2n", "3bn", 70, 84, 6, (4, .0071), (5, .014), (20, .048), (65, .10), (46, .13), 62),
    (16, "1c", "2g", "3cg", 70, 79, 6, (4, .0071), (5, .014), (26, .062), (54, .14), (48, .17), 53),
]

halide_names = {
    "2a": "iodobenzene", "2b": "4-iodotoluene", "2c": "3-iodotoluene", "2d": "4-iodoanisole",
    "2e": "methyl 4-iodobenzoate", "2f": "4-iodoacetophenone", "2g": "1-bromo-4-iodobenzene",
    "2h": "4-iodobenzonitrile", "2i": "4-iodobiphenyl", "2j": "(E)-1-iodohex-1-ene",
    "2k": "(E)-beta-iodostyrene", "2l": "3-oxocyclohexenyl iodide", "2m": "2-iodothiophene",
    "2n": "4-(4-bromophenyl)iodobenzene",
}

for row in scope:
    entry, sub, halide, prod, table_yld, table_ee, detail_page, pdv, ligv, agv, subv, halv, prod_mass = row
    evidence = ev(3) + ev(detail_page)
    lig_label = "(S,S)-Bn-BOX" if entry == 14 else "(R,R)-Bn-BOX"
    sub_mass, sub_mmol = subv
    hal_mass, hal_mmol = halv
    parts = [
        participant(sub, "reactant", sub, evidence, [amount("table_reaction_scale", "0.1–0.15 mmol", ev(3)), amount("mass", q(sub_mass, "mg"), ev(detail_page)), amount("detailed_amount", q(sub_mmol, "mmol"), ev(detail_page))]),
        participant(halide, "reactant", halide, evidence, [amount("table_equivalents", q(1.2, "equiv"), ev(3)), amount("mass", q(hal_mass, "mg"), ev(detail_page)), amount("detailed_amount", q(hal_mmol, "mmol"), ev(detail_page))], name=halide_names[halide], smiles=SIMPLE_SMILES.get(halide)),
        participant("ag3po4", "reagent", "Ag3PO4", evidence, [amount("table_equivalents", q(.45, "equiv"), ev(3)), amount("mass", q(agv[0], "mg"), ev(detail_page)), amount("detailed_amount", q(agv[1], "mmol"), ev(detail_page))]),
        participant("pd", "catalyst", "Pd(dba)2", evidence, [amount("table_loading", q(5, "mol%"), ev(3)), amount("mass", q(pdv[0], "mg"), ev(detail_page)), amount("detailed_amount", q(pdv[1], "mmol"), ev(detail_page))]),
        participant("ligand", "catalyst", lig_label, evidence, [amount("table_loading", q(10, "mol%"), ev(3)), amount("mass", q(ligv[0], "mg"), ev(detail_page)), amount("detailed_amount", q(ligv[1], "mmol"), ev(detail_page))]),
        participant("thf", "solvent", "THF", evidence, [amount("volume", q(2, "mL"), evidence)], smiles=SIMPLE_SMILES["THF"]),
        participant("product", "product", prod, evidence, [amount("isolated_mass", q(prod_mass, "mg"), ev(detail_page))]),
    ]
    outcomes = [
        fld("isolated_yield", q(table_yld, "%"), evidence, ["product"]),
        fld("table_product_ee", q(table_ee, "%"), ev(3), ["product"]),
        fld("yield_measurement_basis", "isolated yield", ev(3), ["product"]),
        fld("ee_measurement_basis", "chiral HPLC", evidence, ["product"]),
    ]
    notes = []
    unresolved = ["Reaction time is not reported.", "Abbreviated compound paragraph does not restate workup or purification.", "Complex reactant/product structures and stereochemistry remain unverified."]
    if entry == 1:
        workup = "extracted with ether; organic layer washed with water and brine and dried over sodium sulfate; filtration"
        purification = "silica-gel chromatography; petroleum ether/ethyl acetate 10:1 to 5:1"
        unresolved = ["Reaction time is reported only as TLC completion, without a numerical duration.", "Complex reactant/product structures and stereochemistry remain unverified."]
    else:
        workup = None
        purification = None
    if entry == 14:
        outcomes.append(fld("detailed_product_ee", q(82, "%"), ev(6), ["product"]))
        notes.append("Table 3 reports 81% ee, while section 4.3.15 reports 82% ee for R-3bg; both source values are retained.")
        unresolved.append("The 81%/82% ee conflict requires source review.")
    records.append(record(
        f"table3_entry{entry}_{prod.lower().replace('-', '_')}", "substrate_scope_entry", evidence, parts,
        [{"step_id": "coupling_cyclization", "participant_ids": [p["entity_id"] for p in parts], "conditions": missing_conditions(
            evidence, temperature=q(70, "°C"), time="TLC completion" if entry == 1 else None,
            atmosphere="argon", workup=workup, purification=purification
        )}],
        outcomes, notes=notes, unresolved=unresolved,
    ))


# Equation 1 is explicitly identified in the prose as an authentic sample from prior study 16.
eq1_evidence = ev(3)
eq1_parts = [
    participant("allenyl_ketoester", "reactant", "ethyl 2-(2',3'-butadienyl)-3-oxobutyrate", eq1_evidence),
    participant("dbad", "reactant", "dibenzyl azodicarboxylate", eq1_evidence),
    participant("cu_otf2", "catalyst", "Cu(OTf)2", eq1_evidence, [amount("loading", q(5, "mol%"), eq1_evidence)]),
    participant("s_ph_box", "catalyst", "(S)-Ph-BOX", eq1_evidence, [amount("loading", q(5, "mol%"), eq1_evidence)]),
    participant("dcm", "solvent", "DCM", eq1_evidence, smiles=SIMPLE_SMILES["DCM"]),
    participant("pdpph3", "catalyst", "Pd(PPh3)4", eq1_evidence, [amount("loading", q(5, "mol%"), eq1_evidence)]),
    participant("k2co3", "reagent", "K2CO3", eq1_evidence, [amount("equivalents", q(2, "equiv"), eq1_evidence)]),
    participant("2g", "reactant", "p-BrC6H4I", eq1_evidence, [amount("equivalents", q(1.2, "equiv"), eq1_evidence)], name="1-bromo-4-iodobenzene", smiles=SIMPLE_SMILES["2g"]),
    participant("dioxane", "solvent", "1,4-dioxane", eq1_evidence, smiles=SIMPLE_SMILES["1,4-dioxane"]),
    participant("rr4dg", "product", "(3R,5R)-4dg", eq1_evidence),
    participant("rs4dg", "product", "(3R,5S)-4dg", eq1_evidence),
]
records.append(record(
    "equation1_prior_authentic_4dg", "literature_example", eq1_evidence, eq1_parts,
    [
        {"step_id": "cu_stage", "participant_ids": ["allenyl_ketoester", "dbad", "cu_otf2", "s_ph_box", "dcm"], "conditions": [fld("temperature", "r.t.", eq1_evidence), fld("reaction_time", None)]},
        {"step_id": "pd_stage", "participant_ids": ["pdpph3", "k2co3", "2g", "dioxane", "rr4dg", "rs4dg"], "conditions": [fld("temperature", q(100, "°C"), eq1_evidence), fld("reaction_time", None)]},
    ],
    [],
    notes=["The text identifies these authentic samples as prepared in previous study 16 and confirmed by X-ray; this arrow is not classified as a new present-paper experiment."],
    unresolved=["Yields, durations, scale, atmosphere, workup, and purification are not reported on page 3.", "Complex structures remain unverified."],
))


# Scheme 2 first arrow: present-paper formation of (S)-3dg, detailed on page 6.
evidence = ev(3) + ev(6)
parts = [
    participant("1d", "reactant", "1d", evidence, [amount("mass", q(51, "mg"), ev(6)), amount("amount", q(.10, "mmol"), ev(6))]),
    participant("2g", "reactant", "2g", evidence, [amount("mass", q(34, "mg"), ev(6)), amount("amount", q(.12, "mmol"), ev(6))], name="1-bromo-4-iodobenzene", smiles=SIMPLE_SMILES["2g"]),
    participant("pd", "catalyst", "Pd(dba)2", evidence, [amount("loading", q(5, "mol%"), ev(3)), amount("mass", q(3, "mg"), ev(6)), amount("amount", q(.0053, "mmol"), ev(6))]),
    participant("ligand", "catalyst", "(R,R)-Bn-BOX", evidence, [amount("loading", q(10, "mol%"), ev(3)), amount("mass", q(4, "mg"), ev(6)), amount("amount", q(.011, "mmol"), ev(6))]),
    participant("ag3po4", "reagent", "Ag3PO4", evidence, [amount("equivalents", q(.45, "equiv"), ev(3)), amount("mass", q(19, "mg"), ev(6)), amount("amount", q(.045, "mmol"), ev(6))]),
    participant("thf", "solvent", "THF", evidence, [amount("volume", q(2, "mL"), ev(6))], smiles=SIMPLE_SMILES["THF"]),
    participant("3dg", "product", "(S)-3dg", evidence, [amount("isolated_mass", q(48, "mg"), ev(6))]),
]
records.append(record(
    "scheme2_prepare_s_3dg", "reported_experiment", evidence, parts,
    [{"step_id": "coupling_cyclization", "participant_ids": [p["entity_id"] for p in parts], "conditions": missing_conditions(
        evidence, temperature=q(70, "°C"), time=q(38, "h"), atmosphere="argon", workup=None, purification=None
    )}],
    [fld("isolated_yield", q(72, "%"), evidence, ["3dg"]), fld("product_ee", q(81, "%"), evidence, ["3dg"]),
     fld("yield_measurement_basis", "isolated yield", ev(3), ["3dg"]), fld("ee_measurement_basis", "chiral HPLC", ev(6), ["3dg"])],
    unresolved=["The abbreviated detailed paragraph does not state workup or purification.", "Complex structures and absolute stereochemistry remain machine-unverified."],
))


# Scheme 2 second arrow: MeMgBr conversion used to assign absolute configuration.
evidence = ev(3)
parts = [
    participant("3dg", "reactant", "(S)-3dg", evidence),
    participant("memgbr", "reagent", "MeMgBr", evidence, [amount("equivalents", q(1.1, "equiv"), evidence)]),
    participant("ether", "solvent", "Et2O", evidence, name="diethyl ether", smiles=SIMPLE_SMILES["diethyl ether"]),
    participant("4dg", "product", "(3S,5S)-4dg", evidence),
]
records.append(record(
    "scheme2_memgbr_to_3s5s_4dg", "reported_experiment", evidence, parts,
    [{"step_id": "grignard_acyl_conversion", "participant_ids": [p["entity_id"] for p in parts], "conditions": missing_conditions(
        evidence, temperature=q(-78, "°C"), time=q(3.5, "h"), atmosphere="argon", workup=None, purification=None
    )}],
    [fld("reported_yield", q(30, "%"), evidence, ["4dg"]), fld("product_ee", q(88, "%"), evidence, ["4dg"]),
     fld("yield_measurement_basis", None, (), ["4dg"]), fld("ee_measurement_basis", "chiral HPLC comparison is described in the prose", evidence, ["4dg"])],
    notes=["The page-3 prose assigns (3S,5S) by comparison with authentic (3R,5R)-4dg and concludes that 3dg formed with (R,R)-Bn-BOX has S configuration."],
    unresolved=["Reactant scale, solvent volume, workup, purification, and yield basis are not reported within pages 1-6.", "Absolute stereochemistry remains machine-unverified."],
))


assert len(records) == 37, len(records)
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")


ids = {r["source_reaction_id"]: r["record_id"] for r in records}
start_ids = [ids[f"scheme1_prepare_1{x}"] for x in "abcd"]
t1_ids = [ids[f"table1_entry{i}"] for i in range(1, 9)]
t2_ids = [ids[f"table2_entry{i}"] for i in range(1, 7)]
t3_ids = [next(r["record_id"] for r in records if r["source_reaction_id"].startswith(f"table3_entry{i}_")) for i in range(1, 17)]
eq1_id = ids["equation1_prior_authentic_4dg"]
dg_id = ids["scheme2_prepare_s_3dg"]
mg_id = ids["scheme2_memgbr_to_3s5s_4dg"]

coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1, "state": "attempted",
            "regions": [{"region": "title, abstract, and two-column introduction on the original page", "finding": "No row-level present-paper experiment, reaction arrow, table, or footnote. Abstract-level reaction and proposed-pathway claims are summarized later by explicit records and were not duplicated.", "evidence_ids": ev(1)}],
            "record_ids": [],
            "unresolved": ["Abstract-level mechanism wording was not promoted to an executed experiment."],
        },
        {
            "page": 2, "state": "attempted",
            "regions": [
                {"region": "upper-left Scheme 1", "finding": "Four distinct starting-material preparations 1a-1d inventoried with nominal Cu/Ph-BOX conditions and yields.", "evidence_ids": ev(2)},
                {"region": "lower-left Table 1 and footnotes", "finding": "Eight independent solvent/Ag3PO4 optimization rows extracted; THF/DMF and Pd(dba)2 footnote overrides applied only to their rows.", "evidence_ids": ev(2)},
                {"region": "upper-right Table 2, ligand drawings, and footnotes", "finding": "Six independent ligand-screen rows extracted, including complex-mixture and no-reaction outcomes; the printed 3aa/3ba product-label tension is retained.", "evidence_ids": ev(2)},
                {"region": "Results and Discussion prose", "finding": "Narrative interpretation of Tables 1-3 linked as context; no duplicate scope records created from prose.", "evidence_ids": ev(2)},
            ],
            "record_ids": start_ids + t1_ids + t2_ids,
            "unresolved": ["Complex structures and ligand identities remain machine-unverified.", "Table 1-2 rows omit reaction times and most operational details."],
        },
        {
            "page": 3, "state": "attempted",
            "regions": [
                {"region": "upper-left Table 3 and footnotes", "finding": "All 16 substrate-scope rows extracted independently with isolated yields and chiral-HPLC ee values; (S,S)-Bn-BOX override applied only to entry 14.", "evidence_ids": ev(3)},
                {"region": "upper-right equation 1", "finding": "Authentic-sample synthesis explicitly attributed to previous study 16 and classified as a literature example, not a new present-paper experiment.", "evidence_ids": ev(3)},
                {"region": "lower Scheme 2 and associated prose", "finding": "Split into present-paper formation of (S)-3dg and its MeMgBr conversion to (3S,5S)-4dg; yields and ee values retained separately.", "evidence_ids": ev(3)},
                {"region": "lower-right General and section 4.2.1 opening", "finding": "General argon/Schlenk statement applied to covered experiments; the 1a preparation begins here and continues on page 4.", "evidence_ids": ev(3)},
            ],
            "record_ids": t3_ids + [eq1_id, dg_id, mg_id, start_ids[0]],
            "unresolved": ["Most Table 3 rows lack reaction time and row-specific workup/purification.", "Equation 1 omits scale, yields, durations, and operations on this page."],
        },
        {
            "page": 4, "state": "attempted",
            "regions": [
                {"region": "left column sections 4.2.1-4.2.4", "finding": "Exact reactant/catalyst quantities and product masses for 1a-1d merged into the four Scheme 1 records; full workup/purification is explicit only for 1a.", "evidence_ids": ev(4)},
                {"region": "lower-left and upper-right typical procedure for (S)-3ba", "finding": "Exact catalyst pre-stirring, substrate/PhI quantities, extraction, washing, drying, chromatography, product mass, yield, and ee merged into Table 3 entry 1.", "evidence_ids": ev(4)},
                {"region": "right column sections 4.3.2-4.3.4", "finding": "Compound-specific quantities and product masses for 3aa, 3bb, and 3bc merged into Table 1 entry 5 and Table 3 entries 2-3.", "evidence_ids": ev(4)},
            ],
            "record_ids": start_ids + [t1_ids[4]] + t3_ids[:3],
            "unresolved": ["The 1a paragraph prints an internally questionable 600 mg/1.21 mmol DBAD pair; retained verbatim.", "Abbreviated preparations do not restate workup/purification."],
        },
        {
            "page": 5, "state": "attempted",
            "regions": [
                {"region": "sections 4.3.5-4.3.11 across both columns", "finding": "Exact quantities, product masses, yields, and ee values for 3bd-3bj merged into Table 3 entries 4-10.", "evidence_ids": ev(5)},
            ],
            "record_ids": t3_ids[3:10],
            "unresolved": ["These abbreviated preparations do not report reaction time, workup, or purification.", "Complex structures and stereochemical encodings remain unverified."],
        },
        {
            "page": 6, "state": "attempted",
            "regions": [
                {"region": "sections 4.3.12-4.3.18 across both columns", "finding": "Exact quantities, product masses, yields, and ee values for 3bk-3dg inventoried; Table 3 entries 11-16 and the separate Scheme 2 3dg experiment were merged rather than duplicated.", "evidence_ids": ev(6)},
                {"region": "section 4.3.15 R-3bg", "finding": "Detailed paragraph reports 82% ee while Table 3 reports 81% ee; both values are retained as an unresolved source conflict.", "evidence_ids": ev(6)},
            ],
            "record_ids": t3_ids[10:] + [dg_id],
            "unresolved": ["The R-3bg 81%/82% ee conflict requires review.", "Abbreviated paragraphs omit reaction times, workups, and purifications."],
        },
    ],
}
COVERAGE.parent.mkdir(parents=True, exist_ok=True)
COVERAGE.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")


tasks = json.loads(TASKS.read_text())
for task in tasks:
    if task.get("document_id") == DOC and task.get("evidence_id") in {f"{DOC}:page{p}:text" for p in range(1, 7)}:
        task["state"] = "attempted"
        task["reason"] = "Original page image and extracted text inspected; reaction inventory recorded in pages_0001_0006 coverage ledger."
TASKS.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"records": len(records), "coverage_pages": [p["page"] for p in coverage["pages"]]}, ensure_ascii=False))
