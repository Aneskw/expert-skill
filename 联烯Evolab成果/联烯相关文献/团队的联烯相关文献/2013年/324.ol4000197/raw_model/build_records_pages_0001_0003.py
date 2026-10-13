#!/usr/bin/env python3
"""Build evidence-linked machine records for ol4000197, PDF pages 1--3."""

import json
from pathlib import Path


DOC = "doc_c08b5cfa9728ca66"
ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / "runs/current/raw_model/records_pages_0001_0003.json"
COVERAGE = ROOT / "runs/current/coverage/pages_0001_0003.json"
TASKS = ROOT / "runs/current/tasks.json"


def ev(*pages):
    result = []
    for page in pages:
        result.extend([f"{DOC}:page{page}:text", f"{DOC}:page{page}:image"])
    return result


def fact(value, evidence=None):
    return {
        "value": value,
        "evidence_ids": list(evidence or []) if value is not None else [],
        "verification": "missing" if value is None else "unreviewed",
    }


def field(name, value, evidence=None, targets=None):
    item = {"name": name, "fact": fact(value, evidence)}
    if targets:
        item["target_entity_ids"] = targets
    return item


def q(number, unit, **extra):
    value = {"number": number, "unit": unit}
    value.update(extra)
    return value


def participant(entity_id, role, label, evidence, name=None, smiles=None, amounts=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence) if name is not None else fact(None),
        "smiles": fact(smiles, evidence) if smiles is not None else fact(None),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": amounts or [],
    }


def step(step_id, participant_ids, conditions):
    return {"step_id": step_id, "participant_ids": participant_ids, "conditions": conditions}


def record(rid, kind, pages, participants=None, steps=None, outcomes=None, notes=None, unresolved=None):
    evidence = ev(*pages)
    return {
        "record_id": f"{DOC}:{rid}",
        "document_id": DOC,
        "source_reaction_id": rid,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": evidence,
        "participants": participants or [],
        "steps": steps or [],
        "outcomes": outcomes or [],
        "notes": [fact(text, evidence) for text in (notes or [])],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved or [],
        },
    }


SUBSTRATES = {
    "1a": ("2,3-allenol 1a (R1=n-Bu, R2=Ph, R3=H)", "C=C=C(CCCC)C(O)c1ccccc1"),
    "1b": ("2,3-allenol 1b (R1=H, R2=Ph, R3=Me)", "C=C=CC(O)(C)c1ccccc1"),
    "1c": ("2,3-allenol 1c (R1=H, R2=Ph, R3=H)", "C=C=CC(O)c1ccccc1"),
    "1d": ("2,3-allenol 1d (R1=n-C6H13, R2=H, R3=H)", "C=C=C(CCCCCC)CO"),
    "1e": ("2,3-allenol 1e (R1=n-C4H9, R2=H, R3=H)", "C=C=C(CCCC)CO"),
    "1f": ("2,3-allenol 1f (R1=Bn, R2=H, R3=H)", "C=C=C(Cc1ccccc1)CO"),
    "1g": ("2,3-allenol 1g (R1=H, R2=4-ClC6H4, R3=H)", "C=C=CC(O)c1ccc(Cl)cc1"),
    "1h": ("2,3-allenol 1h (R1=H, R2=1-naphthyl, R3=H)", "C=C=CC(O)c1cccc2ccccc12"),
    "1i": ("2,3-allenol 1i (R1=H, R2=n-C5H11, R3=H)", "C=C=CC(O)CCCCC"),
    "1j": ("2,3-allenol 1j (R1=H, R2=Cy, R3=H)", "C=C=CC(O)C1CCCCC1"),
    "1k": ("2,3-allenol 1k (R1=Ph, R2=Me, R3=H)", "C=C=C(c1ccccc1)C(O)C"),
    "1l": ("2,3-allenol 1l (R1=Ph, R2=Ph, R3=H)", "C=C=C(c1ccccc1)C(O)c1ccccc1"),
    "1m": ("2,3-allenol 1m (R1=H, R2=n-C6H13, R3=Me)", "C=C=CC(O)(C)CCCCCC"),
    "1n": ("optically active 2,3-allenol (S)-1n", None),
    "1o": ("optically active 2,3-allenol (R)-1o", None),
}

GRIGNARDS = {
    "nBuMgBr": ("n-C4H9MgBr", "n-butylmagnesium bromide", "CCCC[Mg]Br"),
    "nBuMgCl": ("n-C4H9MgCl", "n-butylmagnesium chloride", "CCCC[Mg]Cl"),
    "nBuMgI": ("n-C4H9MgI", "n-butylmagnesium iodide", "CCCC[Mg]I"),
    "CyMgCl": ("CyMgCl", "cyclohexylmagnesium chloride", "C1CCCCC1[Mg]Cl"),
    "iPrMgCl": ("i-PrMgCl", "isopropylmagnesium chloride", "CC(C)[Mg]Cl"),
    "PhMgCl": ("PhMgCl", "phenylmagnesium chloride", "c1ccccc1[Mg]Cl"),
}


def substrate(label, evidence, amounts=None, source_label=None):
    name, smiles = SUBSTRATES[label]
    return participant(f"substrate_{label}", "reactant", source_label or label, evidence, name, smiles, amounts)


def grignard(code, evidence, amounts=None, entity_id="grignard"):
    label, name, smiles = GRIGNARDS[code]
    return participant(entity_id, "reactant", label, evidence, name, smiles, amounts)


def cucl(evidence, amounts=None):
    return participant("copper_chloride", "reagent", "CuCl", evidence, "copper(I) chloride", "[Cu]Cl", amounts)


def ether(evidence, volume=None):
    amounts = [field("volume", q(volume, "mL"), evidence)] if volume is not None else []
    return participant("solvent_et2o", "solvent", "Et2O", evidence, "diethyl ether", "CCOCC", amounts)


def carbon_dioxide(evidence):
    return participant("carbon_dioxide", "reactant", "CO2 balloon", evidence, "carbon dioxide", "O=C=O")


def acid_workup(evidence, hcl=False):
    if hcl:
        return participant("acid_workup", "reagent", "1 M HCl", evidence, "hydrochloric acid", "Cl",
                           [field("concentration", q(1, "M"), evidence)])
    return participant("acid_workup", "reagent", "H+", evidence, "acidic workup; acid identity not specified")


def lactone(label, evidence, entity_id=None):
    return participant(entity_id or f"product_{label}", "product", label, evidence,
                       f"2(5H)-furanone {label}")


def shared_stages(evidence, hours, first_ids, second_ids, initial_minutes=20):
    return [
        step("carbomagnesiation", first_ids, [
            field("initial_temperature", q(-78, "°C"), evidence),
            field("initial_time", q(initial_minutes, "min"), evidence),
            field("warming_operation", "warm from -78 °C to room temperature", evidence),
            field("first_stage_time", q(hours, "h"), evidence),
        ]),
        step("carboxylation_and_lactonization", second_ids, [
            field("temperature", "r.t.", evidence),
            field("reaction_time", q(1.5, "h"), evidence),
            field("operation", "introduce carbon dioxide from a balloon, then acidic workup/lactonization", evidence),
        ]),
    ]


records = []


# Page 1 graphical abstract: a generic summary, not a uniquely identified batch.
e1 = ev(1)
records.append(record(
    "graphical_abstract_overview", "general_scheme", [1],
    participants=[
        participant("generic_allenol", "reactant", "generic 2,3-allenol", e1),
        participant("generic_grignard", "reactant", "R4MgCl (5 equiv)", e1,
                    amounts=[field("equivalents", q(5, "equiv"), e1)]),
        cucl(e1, [field("equivalents", q(2, "equiv"), e1)]),
        ether(e1), carbon_dioxide(e1),
        participant("generic_furanone", "product", "generic 2(5H)-furanone", e1),
    ],
    notes=["The graphical abstract summarizes the current reaction class at -78 °C to room temperature and reports an overall 58–93% yield range; it is not an individual experiment."],
    unresolved=["Generic R groups prevent unique substrate/product structures, experiment identity, scale, time assignment, and product-specific yield assignment."],
))


# Page 2 Scheme 1 combines prior iodination chemistry and the proposed CO2/lactonization concept.
e2 = ev(2)
records.append(record(
    "scheme1_previous_work_and_proposal", "general_scheme", [2],
    participants=[
        participant("generic_allenol", "reactant", "generic 2,3-allenol 1", e2),
        participant("generic_grignard", "reactant", "R4MgX", e2,
                    amounts=[field("equivalents", q(5, "equiv"), e2)]),
        cucl(e2, [field("equivalents", q(2, "equiv"), e2)]), ether(e2),
        participant("intermediate_A", "unspecified_agent", "cyclic organomagnesium intermediate A", e2),
        participant("iodine", "reagent", "I2", e2, "iodine", "II"),
        participant("prior_iodinated_product", "product", "iodinated fully substituted allylic alcohol", e2),
        carbon_dioxide(e2),
        participant("gamma_hydroxy_acid", "unspecified_agent", "proposed gamma-hydroxy Z-alkenoic acid", e2),
        participant("generic_furanone", "product", "generic 2(5H)-furanone", e2),
    ],
    notes=["Scheme 1 explicitly labels the iodination branch as previous work and depicts CO2 capture and lactonization with question marks as the proposed synthesis; neither branch is a uniquely identified experiment of this paper."],
    unresolved=["The generic R groups and proposed intermediates do not define unique structures, quantities, times, or experiment-specific outcomes."],
))


# Table 1: five separate optimization rows.
table1 = [
    (1, "nBuMgBr", None, None, 13, 45, None),
    (2, "nBuMgBr", "HMPA", 2, 13, 23, None),
    (3, "nBuMgBr", "CsF", 2, 13, 23, None),
    (4, "nBuMgBr", "LiCl", 2, 13, 79, None),
    (5, "nBuMgCl", None, None, 15, 85, 87),
]
additives = {
    "HMPA": ("hexamethylphosphoramide", "CN(C)P(=O)(N(C)C)N(C)C"),
    "CsF": ("cesium fluoride", "[Cs+].[F-]"),
    "LiCl": ("lithium chloride", "[Li+].[Cl-]"),
}
for entry, rg, additive, additive_equiv, hours, nmr_yield, isolated_yield in table1:
    evidence = ev(2)
    parts = [
        substrate("1a", evidence, [field("amount", q(1, "mmol"), evidence)]),
        grignard(rg, evidence, [field("equivalents", q(5, "equiv"), evidence),
                                field("amount", q(5, "mmol"), evidence),
                                field("concentration", q(2, "M"), evidence)]),
        cucl(evidence, [field("equivalents", q(2, "equiv"), evidence),
                        field("amount", q(2, "mmol"), evidence)]),
        ether(evidence, 6), carbon_dioxide(evidence), acid_workup(evidence),
        lactone("2aa", evidence),
    ]
    if additive:
        name, smiles = additives[additive]
        parts.insert(4, participant("additive", "reagent", additive, evidence, name, smiles,
                                    [field("equivalents", q(additive_equiv, "equiv"), evidence)]))
    first_ids = ["substrate_1a", "grignard", "copper_chloride", "solvent_et2o"]
    second_ids = ["carbon_dioxide", "acid_workup"] + (["additive"] if additive else [])
    outcomes = [
        field("NMR_yield_2aa", q(nmr_yield, "%"), evidence, ["product_2aa"]),
        field("NMR_yield_measurement_basis", "NMR yield", evidence, ["product_2aa"]),
    ]
    if isolated_yield is not None:
        outcomes += [
            field("isolated_yield_2aa", q(isolated_yield, "%"), evidence, ["product_2aa"]),
            field("isolated_yield_measurement_basis", "isolated yield", evidence, ["product_2aa"]),
        ]
    records.append(record(
        f"table1_entry{entry}", "optimization_entry", [2], parts,
        shared_stages(evidence, hours, first_ids, second_ids), outcomes,
        ["The additive, when present, was added before quenching intermediate A with CO2."],
        ["Atmosphere, exact warming profile, workup reagent identity, purification, product mass, and NMR internal standard are not reported in the supplied main text.",
         "Substrate connectivity is a machine candidate; product connectivity and stereochemistry remain label-based and unverified.",
         "Supporting Information is mentioned by the article but was not supplied or explicitly associated."],
    ))


# Table 2: five halide-anion comparison rows.
table2 = [
    (1, "1b", "nBuMgBr", 13, 48, "NMR", "2ba"),
    (2, "1b", "nBuMgCl", 14, 72, "isolated", "2ba"),
    (3, "1c", "nBuMgBr", 13, 44, "NMR", "2ca"),
    (4, "1c", "nBuMgCl", 13, 78, "isolated", "2ca"),
    (5, "1c", "nBuMgI", 24, None, "complicated", None),
]
for entry, sub, rg, hours, yld, basis, prod in table2:
    evidence = ev(2)
    parts = [
        substrate(sub, evidence, [field("amount", q(1, "mmol"), evidence)]),
        grignard(rg, evidence, [field("equivalents", q(5, "equiv"), evidence),
                                field("amount", q(5, "mmol"), evidence),
                                field("concentration", q(2, "M"), evidence)]),
        cucl(evidence, [field("equivalents", q(2, "equiv"), evidence),
                        field("amount", q(2, "mmol"), evidence)]),
        ether(evidence, 6), carbon_dioxide(evidence), acid_workup(evidence),
    ]
    if prod:
        parts.append(lactone(prod, evidence))
        pid = f"product_{prod}"
        outcomes = [
            field(f"{basis}_yield_{prod}", q(yld, "%"), evidence, [pid]),
            field("yield_measurement_basis", "NMR yield" if basis == "NMR" else "isolated yield", evidence, [pid]),
        ]
    else:
        parts.append(participant("product_mixture", "product", "complicated reaction mixture", evidence))
        outcomes = [field("reaction_outcome", "complicated", evidence, ["product_mixture"]),
                    field("reported_yield", None, targets=["product_mixture"])]
    records.append(record(
        f"table2_entry{entry}", "optimization_entry", [2], parts,
        shared_stages(evidence, hours,
                      [f"substrate_{sub}", "grignard", "copper_chloride", "solvent_et2o"],
                      ["carbon_dioxide", "acid_workup"]), outcomes,
        ["Table 2 footnote d explicitly marks entries 1 and 3 as NMR yields; the prose explicitly calls entry 2 an isolated 72% yield."],
        ["Atmosphere, exact warming profile, acid identity, workup, purification, product mass, and the composition of the entry-5 complicated mixture are not reported.",
         "Candidate substrate connectivity and all product structures/stereochemistry remain machine-unverified.",
         "No Supporting Information file was supplied or explicitly associated."],
    ))


# Table 3: fourteen separate substrate-scope rows, including a distinct 7 mmol scale-up.
table3 = [
    (1, "1d", "nBuMgCl", 10, 75, "2da"),
    (2, "1e", "nBuMgCl", 10, 73, "2ea"),
    (3, "1f", "nBuMgCl", 12, 88, "2fa"),
    (4, "1c", "CyMgCl", 13, 68, "2cb"),
    (5, "1c", "iPrMgCl", 13, 58, "2cc"),
    (6, "1c", "PhMgCl", 13, 75, "2cd"),
    (7, "1g", "nBuMgCl", 12, 76, "2ga"),
    (8, "1h", "nBuMgCl", 13.5, 61, "2ha"),
    (9, "1i", "nBuMgCl", 12, 65, "2ia"),
    (10, "1j", "nBuMgCl", 14, 67, "2ja"),
    (11, "1k", "nBuMgCl", 13, 76, "2ka"),
    (12, "1k", "nBuMgCl", 11, 81, "2ka"),
    (13, "1l", "nBuMgCl", 14, 82, "2la"),
    (14, "1m", "nBuMgCl", 13, 64, "2ma"),
]
for entry, sub, rg, hours, yld, prod in table3:
    pages = [2, 3] if entry in (4, 14) else [2]
    evidence = ev(*pages)
    if entry == 12:
        sub_amounts = [field("amount", q(7, "mmol"), ev(2)), field("scale_mass", q(1.12, "g"), ev(2))]
        rg_amounts = [field("equivalents", q(5, "equiv"), ev(2)), field("concentration", q(2, "M"), ev(2))]
        cu_amounts = [field("equivalents", q(2, "equiv"), ev(2))]
        solvent_volume = None
    else:
        sub_amounts = [field("amount", q(1, "mmol"), ev(2))]
        rg_amounts = [field("equivalents", q(5, "equiv"), ev(2)), field("amount", q(5, "mmol"), ev(2)),
                      field("concentration", q(2, "M"), ev(2))]
        cu_amounts = [field("equivalents", q(2, "equiv"), ev(2)), field("amount", q(2, "mmol"), ev(2))]
        solvent_volume = 6
    parts = [
        substrate(sub, evidence, sub_amounts), grignard(rg, evidence, rg_amounts),
        cucl(evidence, cu_amounts), ether(evidence, solvent_volume), carbon_dioxide(evidence),
        acid_workup(evidence), lactone(prod, evidence),
    ]
    notes = ["Each Table 3 row is retained as a distinct scope experiment."]
    if entry == 12:
        notes.append("Entry 12 is a separate 7 mmol (1.12 g) scale-up and is not merged with entry 11 despite the same substrate and product labels.")
    if entry == 4:
        notes.append("Page 3 acknowledges reproduction of the 2cb result by Pengbin Li; this is supporting context, not a separately specified experiment.")
    if entry == 14:
        notes.append("Page 3 acknowledges reproduction of the 2ma result by Pengbin Li; this is supporting context, not a separately specified experiment.")
    unresolved = [
        "Atmosphere, exact warming profile, acid identity, workup, purification, and isolated product mass are not reported in the supplied main text.",
        "Candidate substrate connectivity and product structure/stereochemistry remain machine-unverified.",
        "No Supporting Information file was supplied or explicitly associated.",
    ]
    if entry == 12:
        unresolved.append("The scale-up footnote gives 7 mmol/1.12 g substrate but does not print scaled CuCl, Grignard-solution, or ether-volume quantities; they are not inferred.")
    records.append(record(
        f"table3_entry{entry}", "substrate_scope_entry", pages, parts,
        shared_stages(evidence, hours,
                      [f"substrate_{sub}", "grignard", "copper_chloride", "solvent_et2o"],
                      ["carbon_dioxide", "acid_workup"]),
        [field("isolated_yield", q(yld, "%"), ev(2), [f"product_{prod}"]),
         field("yield_measurement_basis", "isolated yield", ev(2), [f"product_{prod}"])],
        notes, unresolved,
    ))


# Page 3 narrative: a distinct lower-loading/time comparison without a numerical yield.
e3 = ev(3)
parts = [
    substrate("1c", e3),
    grignard("nBuMgCl", e3, [field("equivalents", q(3, "equiv"), e3)]),
    lactone("2ca", e3),
]
records.append(record(
    "narrative_1c_3equiv_24h", "optimization_entry", [3], parts,
    [step("lower_grignard_loading_comparison", ["substrate_1c", "grignard"], [field("reaction_time", q(24, "h"), e3)])],
    [field("yield_observation", "lower yield", e3, ["product_2ca"]),
     field("reported_yield", None, targets=["product_2ca"]),
     field("yield_measurement_basis", None, targets=["product_2ca"])],
    ["The prose gives only a qualitative lower-yield comparison at the structured Grignard loading and duration; no numerical yield is printed."],
    ["CuCl amount, solvent, temperature program, CO2 details, workup, purification, numerical yield, and measurement basis are not restated and are not borrowed from another row.",
     "Product structure remains machine-unverified; no SI was supplied or explicitly associated."],
))


# Scheme 2: four distinct optically active substrate/product arrows.
scheme2 = [
    (1, "1k", "(S)-1k", 99, "gt", 13, "(S)-2ka", 73, 99, "gt"),
    (2, "1c", "(S)-1c", 99, "gt", 13, "(S)-2ca", 77, 99, "gt"),
    (3, "1n", "(S)-1n", 99, "gt", 12, "(S)-2na", 70, 99, "gt"),
    (4, "1o", "(R)-1o", 92, None, 12, "(R)-2oa", 93, 92, None),
]
for idx, sub, sub_label, start_ee, start_qual, hours, prod, yld, product_ee, product_qual in scheme2:
    evidence = ev(3)
    parts = [
        substrate(sub, evidence, source_label=sub_label),
        grignard("nBuMgCl", evidence, [field("equivalents", q(5, "equiv"), evidence)]),
        cucl(evidence, [field("equivalents", q(2, "equiv"), evidence)]),
        ether(evidence), carbon_dioxide(evidence), acid_workup(evidence),
        lactone(prod, evidence, "product"),
    ]
    start_q = q(start_ee, "%", **({"qualifier": start_qual, "raw_text": ">99% ee"} if start_qual else {}))
    prod_q = q(product_ee, "%", **({"qualifier": product_qual, "raw_text": ">99% ee"} if product_qual else {}))
    notes = ["Scheme 2 reports no obvious racemization; stereochemical labels and ee values are retained verbatim without independent certification."]
    if idx == 3:
        notes.append("Page 3 acknowledges reproduction of the (S)-2na result by Pengbin Li; this is supporting context, not a duplicate record.")
    records.append(record(
        f"scheme2_row{idx}_{sub}_to_{prod.replace('(', '').replace(')', '').replace('-', '_')}",
        "substrate_scope_entry", [3], parts,
        shared_stages(evidence, hours,
                      [f"substrate_{sub}", "grignard", "copper_chloride", "solvent_et2o"],
                      ["carbon_dioxide", "acid_workup"]),
        [field("starting_allenol_ee", start_q, evidence, [f"substrate_{sub}"]),
         field("reported_yield", q(yld, "%"), evidence, ["product"]),
         field("yield_measurement_basis", None, targets=["product"]),
         field("product_ee", prod_q, evidence, ["product"])],
        notes,
        ["Reaction scale, atmosphere, exact warming profile, acid identity, workup, purification, product mass, yield basis, and ee analytical method are not reported in Scheme 2.",
         "Chiral substrate/product structures and configurations remain label-based and machine-unverified.",
         "No Supporting Information file was supplied or explicitly associated."],
    ))


# Scheme 3: two separate one-pot sequences from chloropropargylic alcohol 3.
scheme3 = [
    ("H", "OCC#CCCl", 10, "2ea", 67),
    ("Ph", "OC(c1ccccc1)C#CCCl", 13, "2aa", 51),
]
for rgroup, smiles, hours, prod, yld in scheme3:
    evidence = ev(3)
    sid = "substrate_3_H" if rgroup == "H" else "substrate_3_Ph"
    parts = [
        participant(sid, "reactant", f"3 (R={rgroup})", evidence,
                    "4-chlorobut-2-yn-1-ol" if rgroup == "H" else "4-chloro-1-phenylbut-2-yn-1-ol",
                    smiles),
        grignard("nBuMgCl", evidence, [field("equivalents", q(6, "equiv"), evidence)]),
        cucl(evidence, [field("equivalents", q(2, "equiv"), evidence)]),
        ether(evidence), carbon_dioxide(evidence), acid_workup(evidence, hcl=True),
        participant("in_situ_allenol", "unspecified_agent", f"in situ allenol intermediate (R={rgroup})", evidence),
        lactone(prod, evidence),
    ]
    records.append(record(
        f"scheme3_R_{rgroup}_to_{prod}", "reported_experiment", [3], parts,
        [
            step("one_pot_allenol_formation_and_carbomagnesiation",
                 [sid, "grignard", "copper_chloride", "solvent_et2o", "in_situ_allenol"], [
                     field("initial_temperature", q(-78, "°C"), evidence),
                     field("initial_time", q(20, "min"), evidence),
                     field("warming_operation", "warm from -78 °C to room temperature", evidence),
                     field("first_stage_time", q(hours, "h"), evidence),
                 ]),
            step("carboxylation_and_lactonization", ["carbon_dioxide", "acid_workup"], [
                field("temperature", "r.t.", evidence), field("reaction_time", q(1.5, "h"), evidence),
                field("operation", "CO2 balloon followed by 1 M HCl workup", evidence),
            ]),
        ],
        [field("reported_yield", q(yld, "%"), evidence, [f"product_{prod}"]),
         field("yield_measurement_basis", None, targets=[f"product_{prod}"])],
        ["Scheme 3 presents this as a one-pot sequence from chloropropargylic alcohol 3 through in situ allenol formation, carbomagnesiation, carboxylation, and lactonization."],
        ["Reaction scale, atmosphere, ether volume, exact warming profile, workup volume, purification, product mass, and yield measurement basis are not reported.",
         "The substrate SMILES is a machine connectivity candidate; intermediate and product structures remain machine-unverified.",
         "No Supporting Information file was supplied or explicitly associated."],
    ))


assert len(records) == 33, len(records)

t1_ids = [f"{DOC}:table1_entry{i}" for i in range(1, 6)]
t2_ids = [f"{DOC}:table2_entry{i}" for i in range(1, 6)]
t3_ids = [f"{DOC}:table3_entry{i}" for i in range(1, 15)]
s2_ids = [r["record_id"] for r in records if r["source_reaction_id"].startswith("scheme2_row")]
s3_ids = [r["record_id"] for r in records if r["source_reaction_id"].startswith("scheme3_R_")]

coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1,
            "state": "attempted",
            "regions": [
                {"region": "page 1 title, abstract, and graphical reaction summary",
                 "finding": "The title/abstract and generic reaction drawing summarize CuCl-mediated carbomagnesiation/carboxylation of 2,3-allenols with R4MgCl and a CO2 balloon, with an overall 58–93% range. This is classified as a general overview, not an individual batch.",
                 "evidence_ids": ev(1)},
                {"region": "page 1 two-column introduction and lower-right prior-work/proposed-route prose",
                 "finding": "Prior alkynol/Grignard/CO2 literature and the authors' earlier iodination work are literature context. The proposed cyclic intermediate A and lactonization concept continue in Scheme 1 on page 2; no page-1 experiment beyond later table rows is created.",
                 "evidence_ids": ev(1)},
            ],
            "record_ids": [f"{DOC}:graphical_abstract_overview"],
            "unresolved": ["The graphical summary uses generic R groups and does not assign its yield range to a unique experiment.",
                           "No Supporting Information file was supplied or explicitly associated."],
        },
        {
            "page": 2,
            "state": "attempted",
            "regions": [
                {"region": "page 2 upper-left Scheme 1 and adjacent optimization prose",
                 "finding": "Scheme 1 combines a prior-work iodination branch with a proposed CO2 capture/lactonization branch. It is retained as a general scheme, while the prose is linked to Table 1 rows rather than duplicated.",
                 "evidence_ids": ev(2)},
                {"region": "page 2 left-center Table 1 reaction drawing, entries 1–5, and footnotes a–c",
                 "finding": "Five independent optimization experiments were retained with halide/additive identity, additive equivalents, two-stage conditions, substrate/CuCl/Grignard/ether quantities, NMR yields, and the separate 87% isolated yield in entry 5.",
                 "evidence_ids": ev(2)},
                {"region": "page 2 upper-right Table 2 reaction drawing, entries 1–5, and footnotes a–d",
                 "finding": "Five halide-comparison experiments were retained separately: bromide entries 1/3 have NMR yields, chloride entries 2/4 give 72%/78%, and iodide entry 5 is reported only as complicated after 24 h.",
                 "evidence_ids": ev(2)},
                {"region": "page 2 lower-right Table 3 reaction drawing, entries 1–14, and footnotes a–b",
                 "finding": "Fourteen substrate-scope experiments were retained row-by-row with R-group labels, Grignard identity, time, and isolated yield. Entry 12 is a distinct 7 mmol (1.12 g) scale-up and is not merged with entry 11.",
                 "evidence_ids": ev(2)},
            ],
            "record_ids": [f"{DOC}:scheme1_previous_work_and_proposal", *t1_ids, *t2_ids, *t3_ids],
            "unresolved": ["Most table rows omit atmosphere, exact warming profile, acid identity, workup, purification, and isolated masses.",
                           "The entry-12 scale-up does not print scaled reagent/solvent quantities.",
                           "Complex product structures and stereochemistry remain machine-unverified; SI is unassociated."],
        },
        {
            "page": 3,
            "state": "attempted",
            "regions": [
                {"region": "page 3 upper-left continuation of Table 3 discussion",
                 "finding": "The 7 mmol Table 3 entry 12 result is reiterated. A distinct 1c/3 equiv n-C4H9MgCl/24 h comparison is reported only as giving a lower yield of 2ca; the numerical yield is preserved as missing. Premature protonation is mentioned only as an unassigned minor byproduct in some cases and is not assigned to a fabricated row.",
                 "evidence_ids": ev(3)},
                {"region": "page 3 left-center Scheme 2, four optically active substrate/product arrows",
                 "finding": "Four independent chirality-transfer experiments were retained with substrate/product configurations, starting and product ee, row-specific first-stage times, and yields 70–93%. The acknowledgment that (S)-2na was reproduced is supporting context, not a duplicate experiment.",
                 "evidence_ids": ev(3)},
                {"region": "page 3 upper-right Scheme 3, two R rows from chloropropargylic alcohol 3",
                 "finding": "Two distinct one-pot experiments were retained: R=H to 2ea (10 h, 67%) and R=Ph to 2aa (13 h, 51%), with 6 equiv n-BuMgCl, 2 equiv CuCl, CO2 balloon, and 1 M HCl workup.",
                 "evidence_ids": ev(3)},
                {"region": "page 3 conclusion, acknowledgments, Supporting Information statement, and references",
                 "finding": "The conclusion summarizes the chloride effect. Reproduction statements for 2cb, 2ma, and (S)-2na were linked to existing records. The article says SI exists online, but no SI file is supplied or explicitly associated here; references were not expanded into current-paper experiments.",
                 "evidence_ids": ev(3)},
            ],
            "record_ids": [f"{DOC}:table3_entry4", f"{DOC}:table3_entry12", f"{DOC}:table3_entry14",
                           f"{DOC}:narrative_1c_3equiv_24h", *s2_ids, *s3_ids],
            "unresolved": ["The lower-yield 3-equiv comparison has no numerical yield or fully restated conditions.",
                           "The premature-protonation byproduct is not assigned to specific rows or a structure.",
                           "Scheme 2 omits scale, workup details, yield basis, and ee method; Scheme 3 omits scale, solvent volume, purification, and yield basis.",
                           "Supporting Information remains unassociated and all complex structures/configurations need review."],
        },
    ],
}

RAW.parent.mkdir(parents=True, exist_ok=True)
COVERAGE.parent.mkdir(parents=True, exist_ok=True)
RAW.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
COVERAGE.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

tasks = json.loads(TASKS.read_text())
for item in tasks:
    if item.get("document_id") == DOC and item.get("task_id", "").endswith(":text"):
        page = int(item["task_id"].split(":page", 1)[1].split(":", 1)[0])
        if 1 <= page <= 3:
            item["state"] = "attempted"
            item["reason"] = "Original rendered page image and extracted text inspected; coverage ledger records regions, experiment mapping, classifications, and unresolved details."
TASKS.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"records": len(records), "raw": str(RAW), "coverage": str(COVERAGE)}, ensure_ascii=False))
