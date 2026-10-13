#!/usr/bin/env python3
"""Build the machine extraction for ja1108694 PDF pages 1--4."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
DOC = "doc_3d6ddb59e8a1632b"
EV = {
    page: [f"{DOC}:page{page}:text", f"{DOC}:page{page}:image"]
    for page in range(1, 5)
}


def fact(value, evidence):
    return {
        "value": value,
        "evidence_ids": list(evidence) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def qty(number, unit, **extra):
    value = {"number": number, "unit": unit}
    value.update(extra)
    return value


def rng(minimum, maximum, unit, raw_text):
    return {
        "minimum": minimum,
        "maximum": maximum,
        "unit": unit,
        "raw_text": raw_text,
    }


def fld(name, value, evidence, targets=None):
    item = {"name": name, "fact": fact(value, evidence)}
    if targets:
        item["target_entity_ids"] = list(targets)
    return item


def part(entity_id, role, label, evidence, *, name=None, smiles=None, amounts=None):
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


def rec(rid, kind, evidence, participants, steps, outcomes, *, notes=None, unresolved=None):
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
        "notes": [fact(value, evidence) for value in (notes or [])],
        "review": {
            "method": "model",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved or [
                "Supporting Information was not supplied or explicitly associated.",
                "Complex structures and stereochemistry remain machine-unverified.",
            ],
        },
    }


def step(step_id, participant_ids, conditions):
    return {
        "step_id": step_id,
        "participant_ids": participant_ids,
        "conditions": conditions,
    }


def solvent_part(label, evidence, amount=None, smiles=None, entity_id="solvent"):
    amounts = [fld("volume", amount, evidence)] if amount else []
    return part(entity_id, "solvent", label, evidence, smiles=smiles, amounts=amounts)


def organozinc(label, evidence, *, equiv=3, concentration=None, smiles=None, entity_id="organozinc"):
    amounts = [fld("equivalents", qty(equiv, "equiv"), evidence)]
    if concentration is not None:
        amounts.append(fld("concentration", qty(concentration, "M"), evidence))
    return part(entity_id, "reagent", label, evidence, smiles=smiles, amounts=amounts)


records = []


# Page 1, Scheme 1: prior routes and the generic concept are not experiments of this paper.
records.append(rec(
    "scheme1_prior_2plus2_routes", "literature_example", EV[1],
    [
        part("ketene_or_keteniminium", "reactant", "ketene or keteniminium salt", EV[1]),
        part("alkyne", "reactant", "substituted alkyne", EV[1]),
        part("cyclobutenone_prior", "product", "substituted cyclobutenone", EV[1]),
    ],
    [step("literature_cycloaddition", ["ketene_or_keteniminium", "alkyne"], [
        fld("operation", "[2+2] cycloaddition (generic prior-work route)", EV[1])
    ])],
    [],
    notes=["Scheme 1 labels this branch as previous work and cites references 6 and 7."],
    unresolved=["Generic R-group structures and exact literature conditions are not specified on this page."],
))

records.append(rec(
    "scheme1_generic_allenoate_cyclization_concept", "general_scheme", EV[1],
    [
        part("allenoate_1_generic", "reactant", "2,3-allenoate 1 (generic R groups)", EV[1]),
        part("organometallic_generic", "reagent", "R4M (generic organometallic)", EV[1]),
        part("cyclobutenone_2_generic", "product", "cyclobutenone 2 (generic R groups)", EV[1]),
        part("intermediate_A", "unspecified_agent", "proposed intermediate A", EV[1]),
        part("intermediate_B", "unspecified_agent", "proposed intermediate B", EV[1]),
    ],
    [step("generic_tandem_path", ["allenoate_1_generic", "organometallic_generic"], [
        fld("operation", "Michael addition / cyclic 1,2-addition / elimination concept", EV[1])
    ])],
    [],
    notes=["This is a generic conceptual route with proposed intermediates A and B, not a single batch experiment."],
    unresolved=["R groups, metal identity, scale, time, temperature, workup, and yield are generic or absent."],
))


# Page 1, Table 1: each catalyst/solvent/temperature row is independent.
table1 = [
    # entry, solvent, solvent SMILES, temperature, time(h), catalyst, 2a, 3a, recovery
    (1, "toluene", "Cc1ccccc1", "r.t.", 14, None, 40, 10, 35),
    (2, "toluene", "Cc1ccccc1", "r.t.", 24, "Fe(acac)3", 34, 7, 20),
    (3, "toluene", "Cc1ccccc1", "r.t.", 24, "CuCl", 53, 6, 25),
    (4, "toluene", "Cc1ccccc1", "r.t.", 24, "CuCl2", 32, 5, 39),
    (5, "toluene", "Cc1ccccc1", "r.t.", 13, "Ni(PPh3)2Cl2", 6, 9, 48),
    (6, "toluene", "Cc1ccccc1", qty(100, "°C"), 1.5, None, 95, 1.5, 1),
    (7, "Et2O", "CCOCC", "r.t.", 19, None, 32, 20, 48),
    (8, "CH3CN", "CC#N", qty(60, "°C"), 13, None, 0, 2.5, 97),
    (9, "THF", "C1CCOC1", qty(70, "°C"), 18.5, None, 58, 8, 19),
    (10, "n-hexane", "CCCCCC", qty(60, "°C"), 14, None, 96, 2, 0.4),
    (11, "dioxane", "O1CCOCC1", qty(100, "°C"), 1.5, None, 53, 0.8, 44),
]
for entry, solv, solv_smiles, temperature, duration, catalyst, y2a, y3a, recovery in table1:
    rid = f"table1_entry{entry}"
    ps = [
        part("substrate_1a", "reactant", "1a", EV[1],
             name="methyl 2-butyl-4-propyl-2,3-heptadienoate",
             smiles="COC(=O)C(CCCC)=C=C(CCC)CCC"),
        organozinc("Et2Zn", EV[1], concentration=1.5, smiles="CC[Zn]CC", entity_id="et2zn"),
        solvent_part(solv, EV[1], smiles=solv_smiles),
        part("product_2a", "product", "2a", EV[1],
             name="2-butyl-3-ethyl-4,4-dipropylcyclobut-2-enone",
             smiles="O=C1C(CCCC)=C(CC)C1(CCC)CCC"),
        part("product_3a", "product", "3a (hydrolysis product)", EV[1]),
        part("internal_standard", "reagent", "dibromomethane", EV[1], smiles="BrCBr"),
    ]
    participant_ids = ["substrate_1a", "et2zn", "solvent", "internal_standard"]
    if catalyst:
        ps.append(part("catalyst", "catalyst", catalyst, EV[1], amounts=[
            fld("catalyst_mol_percent", qty(5, "mol%"), EV[1])
        ]))
        participant_ids.append("catalyst")
    records.append(rec(
        rid, "optimization_entry", EV[1], ps,
        [step("reaction", participant_ids, [
            fld("solvent", solv, EV[1]),
            fld("temperature", temperature, EV[1]),
            fld("time", qty(duration, "h"), EV[1]),
        ])],
        [
            fld("NMR_yield_2a", qty(y2a, "%"), EV[1], ["product_2a"]),
            fld("NMR_yield_3a", qty(y3a, "%"), EV[1], ["product_3a"]),
            fld("recovered_starting_material_1a", qty(recovery, "%"), EV[1], ["substrate_1a"]),
            fld("yield_measurement_basis", "NMR using dibromomethane as internal standard", EV[1], ["product_2a", "product_3a"]),
        ],
        unresolved=[
            "Exact substrate scale, workup, purification, and atmosphere are not stated in Table 1.",
            "Candidate structures for 1a and 2a remain machine-unverified; 3a connectivity is not encoded.",
            "Supporting Information was not supplied or explicitly associated.",
        ],
    ))


# Page 2, Table 2 scope.
table2 = [
    # entry, R1, R2, R3, substrate, R4, time value/unit, yield, product
    (1, "n-Pr", "n-Pr", "n-Bu", "1a", "Et", 1.5, "h", 70, "2a"),
    (2, "n-Pr", "Me", "n-Bu", "1b", "Et", 1.5, "h", 78, "2b"),
    (3, "i-Pr", "Me", "n-Bu", "1c", "Et", 1.5, "h", 80, "2c"),
    (4, "t-Bu", "Me", "n-Bu", "1d", "Et", 4, "h", 74, "2d"),
    (5, "Me", "Me", "Ph", "1e", "Et", 3.5, "h", 72, "2e"),
    (6, "i-Pr", "Me", "Ph", "1f", "Et", 3.5, "h", 78, "2f"),
    (7, "Me", "Me", "p-FC6H4", "1g", "Et", 1.5, "h", 72, "2g"),
    (8, "Me", "Me", "1-naphthyl", "1h", "Et", 2, "h", 79, "2h"),
    (9, "-(CH2)4-", "-(CH2)4-", "t-Bu", "1i", "Et", 1, "h", 92, "2i"),
    (10, "-(CH2)5-", "-(CH2)5-", "Ph", "1j", "Et", 1.5, "h", 88, "2j"),
    (11, "n-Bu", "H", "n-Bu", "1k", "Et", 10, "min", 50, "2k"),
    (12, "n-Bu", "H", "t-Bu", "1l", "Et", 20, "min", 90, "2l"),
    (13, "n-Pr", "n-Pr", "n-Bu", "1a", "i-Pr", 2, "h", 82, "2m"),
    (14, "n-Bu", "H", "t-Bu", "1l", "i-Pr", 0.5, "h", 80, "2n"),
    (15, "Me", "Me", "p-FC6H4", "1g", "i-Pr", 3.5, "h", 72, "2o"),
    (16, "-(CH2)5-", "-(CH2)5-", "Ph", "1j", "i-Pr", 2, "h", 74, "2p"),
    (17, "n-Pr", "n-Pr", "n-Bu", "1a", "Ph", 3, "h", 69, "2q"),
    (18, "n-Bu", "H", "t-Bu", "1l", "Ph", 0.5, "h", 82, "2r"),
    (19, "Me", "Me", "Ph", "1e", "Ph", 1.5, "h", 89, "2s"),
    (20, "-(CH2)5-", "-(CH2)5-", "Ph", "1j", "Ph", 2.5, "h", 81, "2t"),
    (21, "n-Pr", "n-Pr", "n-Bu", "1a", "Et", 2, "h", 68, "2a"),
]
zinc_info = {
    "Et": ("Et2Zn", 1.5, "CC[Zn]CC"),
    "i-Pr": ("i-Pr2Zn", 1.0, "CC(C)[Zn]C(C)C"),
    "Ph": ("Ph2Zn", None, "c1ccccc1[Zn]c1ccccc1"),
}
for entry, r1, r2, r3, substrate, r4, duration, unit, main_yield, product in table2:
    evidence = EV[2]
    zinc_label, concentration, zinc_smiles = zinc_info[r4]
    scale = qty(5.0, "mmol") if entry == 21 else qty(0.4, "mmol")
    reactant = part(
        "substrate", "reactant", f"{substrate} (R1={r1}, R2={r2}, R3={r3})", evidence,
        smiles="COC(=O)C(CCCC)=C=C(CCC)CCC" if substrate == "1a" else None,
        amounts=[fld("reaction_scale", scale, evidence)],
    )
    solvent_label = "xylenes" if entry == 4 else "toluene"
    solvent_smiles = None if entry == 4 else "Cc1ccccc1"
    solvent_volume = None if entry in (4, 21) else qty(5, "mL")
    product_part = part(
        "main_product", "product", product, evidence,
        smiles="O=C1C(CCCC)=C(CC)C1(CCC)CCC" if product == "2a" else None,
    )
    hydrolysis = part("hydrolysis_product", "product", "hydrolysis product 3", evidence)
    ps = [
        reactant,
        organozinc(zinc_label, evidence, concentration=concentration, smiles=zinc_smiles),
        solvent_part(solvent_label, evidence, amount=solvent_volume, smiles=solvent_smiles),
        product_part,
        hydrolysis,
    ]
    hydrolysis_yield = qty(12, "%") if entry in (15, 16) else rng(1, 9, "%", "1-9%")
    notes = []
    unresolved = [
        "Atmosphere, workup, purification, and exact isolated product mass are not stated in the main-text table.",
        "Complex substrate and product structures remain machine-unverified.",
        "Supporting Information was not supplied or explicitly associated.",
    ]
    if r4 == "Ph":
        notes.append("Table 2 footnote a describes Ph2Zn as pure Ph2Zn.")
    if entry == 4:
        notes.append("Footnote b overrides the general solvent and temperature: xylenes at 140 °C for complete conversion.")
        unresolved.append("The xylenes volume is not restated under the entry-4 override.")
    if entry == 21:
        notes.append("Footnote d identifies this as the 5.0 mmol scale experiment.")
        unresolved.append("The toluene volume for the 5.0 mmol scale run is not stated; the general 5 mL value is not copied across the scale override.")
    records.append(rec(
        f"table2_entry{entry}", "substrate_scope_entry", evidence, ps,
        [step("tandem_reaction", ["substrate", "organozinc", "solvent"], [
            fld("solvent", solvent_label, evidence),
            fld("temperature", qty(140 if entry == 4 else 100, "°C"), evidence),
            fld("time", qty(duration, unit), evidence),
        ])],
        [
            fld("isolated_yield_main_product", qty(main_yield, "%"), evidence, ["main_product"]),
            fld("yield_measurement_basis", "isolated", evidence, ["main_product"]),
            fld("crude_H1_NMR_yield_hydrolysis_product", hydrolysis_yield, evidence, ["hydrolysis_product"]),
            fld("hydrolysis_product_measurement_basis", "1H NMR analysis of the crude reaction mixture", evidence, ["hydrolysis_product"]),
        ],
        notes=notes,
        unresolved=unresolved,
    ))


# Page 2, Table 3 functional-group scope.
table3 = [
    (1, "Br", "1m", 90, 62, "2u"),
    (2, "CN", "1n", 15, 73, "2v"),
    (3, "CO2CH3", "1o", 15, 75, "2w"),
    (4, "COCH3", "1p", 15, 45, "2x"),
]
for entry, r5, substrate, duration, product_yield, product in table3:
    evidence = EV[2]
    ps = [
        part("substrate", "reactant", f"{substrate} (R5={r5})", evidence, amounts=[
            fld("reaction_scale", qty(0.4, "mmol"), evidence)
        ]),
        organozinc("Et2Zn", evidence, concentration=1.5, smiles="CC[Zn]CC", entity_id="et2zn"),
        solvent_part("toluene", evidence, amount=qty(5, "mL"), smiles="Cc1ccccc1"),
        part("product", "product", product, evidence),
    ]
    records.append(rec(
        f"table3_entry{entry}", "substrate_scope_entry", evidence, ps,
        [step("tandem_reaction", ["substrate", "et2zn", "solvent"], [
            fld("solvent", "toluene", evidence),
            fld("temperature", qty(100, "°C"), evidence),
            fld("time", qty(duration, "min"), evidence),
        ])],
        [
            fld("isolated_yield_product", qty(product_yield, "%"), evidence, ["product"]),
            fld("yield_measurement_basis", "isolated", evidence, ["product"]),
        ],
        unresolved=[
            "Atmosphere, workup, purification, and product mass are not reported in the main-text table.",
            "Complex substrate and product connectivity remains machine-unverified.",
            "Supporting Information was not supplied or explicitly associated.",
        ],
    ))


# Pages 2--3, Scheme 2 control experiments.
ev23 = EV[2] + EV[3]
records.append(rec(
    "scheme2_et2zn_protonolysis_3b", "reported_experiment", ev23,
    [
        part("substrate_1n", "reactant", "1n", ev23),
        organozinc("Et2Zn", ev23, smiles="CC[Zn]CC", entity_id="et2zn"),
        solvent_part("toluene", ev23, smiles="Cc1ccccc1"),
        part("protonolysis", "reagent", "H+ (protonolysis; exact source not stated)", ev23),
        part("product_3b", "product", "3b", ev23),
    ],
    [
        step("conjugate_addition", ["substrate_1n", "et2zn", "solvent"], [
            fld("solvent", "toluene", ev23), fld("temperature", "r.t.", ev23), fld("time", qty(5, "min"), ev23)
        ]),
        step("protonolysis", ["protonolysis"], [fld("operation", "protonolysis of A1-Zn", ev23)]),
    ],
    [
        fld("isolated_yield_3b", qty(93, "%"), ev23, ["product_3b"]),
        fld("yield_measurement_basis", "isolated", ev23, ["product_3b"]),
    ],
    unresolved=[
        "The exact proton source, scale, workup, purification, and atmosphere are not stated.",
        "The depicted structures of A1-Zn and 3b remain machine-unverified.",
    ],
))

records.append(rec(
    "scheme2_et2zn_thermal_cyclization_2v", "reported_experiment", ev23,
    [
        part("substrate_1n", "reactant", "1n", ev23),
        organozinc("Et2Zn", ev23, smiles="CC[Zn]CC", entity_id="et2zn"),
        solvent_part("toluene", ev23, smiles="Cc1ccccc1"),
        part("product_2v", "product", "2v", ev23),
    ],
    [
        step("form_A1_Zn", ["substrate_1n", "et2zn", "solvent"], [
            fld("solvent", "toluene", ev23), fld("temperature", "r.t.", ev23), fld("time", qty(5, "min"), ev23)
        ]),
        step("thermal_cyclization", ["substrate_1n", "et2zn"], [
            fld("temperature", qty(100, "°C"), ev23), fld("time", qty(15, "min"), ev23)
        ]),
    ],
    [
        fld("H1_NMR_yield_2v", qty(75, "%"), ev23, ["product_2v"]),
        fld("yield_measurement_basis", "1H NMR", ev23, ["product_2v"]),
    ],
    unresolved=[
        "Scale, NMR standard, workup, purification, and atmosphere are not stated.",
        "The depicted structures of A1-Zn and 2v remain machine-unverified.",
    ],
))

records.append(rec(
    "scheme2_etmgbr_failed_cyclization", "reported_experiment", ev23,
    [
        part("substrate_1n", "reactant", "1n", ev23),
        part("etmgbr", "reagent", "EtMgBr", ev23, smiles="CC[Mg]Br", amounts=[
            fld("equivalents", qty(3, "equiv"), ev23)
        ]),
        part("feacac3", "catalyst", "Fe(acac)3", ev23, amounts=[
            fld("catalyst_mol_percent", qty(5, "mol%"), ev23)
        ]),
        solvent_part("toluene", ev23, smiles="Cc1ccccc1"),
    ],
    [
        step("form_A1_Mg", ["substrate_1n", "etmgbr", "feacac3", "solvent"], [
            fld("solvent", "toluene", ev23), fld("temperature", qty(-78, "°C"), ev23), fld("time", qty(5, "min"), ev23)
        ]),
        step("attempted_thermal_cyclization", ["substrate_1n", "etmgbr", "feacac3"], [
            fld("temperature", qty(100, "°C"), ev23), fld("time", qty(30, "min"), ev23)
        ]),
    ],
    [fld("reaction_result", "complicated mixture; 2v was not obtained", ev23)],
    unresolved=[
        "The components and amounts of the complicated mixture are not reported.",
        "Scale, workup, purification, and atmosphere are not stated.",
    ],
))


# Pages 2--3, Scheme 3: one explicitly cited prior result and one present high-temperature control.
records.append(rec(
    "scheme3_room_temperature_prior_result", "literature_example", ev23,
    [
        part("substrate_1q", "reactant", "1q", ev23),
        part("et2zn", "reagent", "Et2Zn", ev23, smiles="CC[Zn]CC"),
        part("prior_product", "product", "(Z)-5-benzylidenecyclohex-2-enone derivative shown in Scheme 3", ev23),
    ],
    [step("prior_reaction", ["substrate_1q", "et2zn"], [
        fld("temperature", "r.t.", ev23), fld("time", qty(1, "h"), ev23)
    ])],
    [
        fld("isolated_yield_prior_product", qty(65, "%"), ev23, ["prior_product"]),
        fld("yield_measurement_basis", "isolated", ev23, ["prior_product"]),
    ],
    notes=["The room-temperature arrow is marked ref. 13 in Scheme 3 and is classified as a literature example."],
    unresolved=["Exact scale, equivalents, solvent, workup, and product connectivity are not restated here."],
))

records.append(rec(
    "scheme3_high_temperature_control", "reported_experiment", ev23,
    [
        part("substrate_1q", "reactant", "1q", ev23),
        part("et2zn", "reagent", "Et2Zn", ev23, smiles="CC[Zn]CC"),
        part("cyclohexenone_product", "product", "(Z)-5-benzylidenecyclohex-2-enone derivative shown in Scheme 3", ev23),
        part("naphthol_product", "product", "naphthol derivative shown in Scheme 3", ev23),
    ],
    [step("high_temperature_control", ["substrate_1q", "et2zn"], [
        fld("temperature", qty(100, "°C"), ev23), fld("time", qty(30, "min"), ev23)
    ])],
    [
        fld("H1_NMR_yield_cyclohexenone_product", qty(48, "%"), ev23, ["cyclohexenone_product"]),
        fld("H1_NMR_yield_naphthol_product", qty(5, "%"), ev23, ["naphthol_product"]),
        fld("yield_measurement_basis", "1H NMR", ev23, ["cyclohexenone_product", "naphthol_product"]),
    ],
    unresolved=[
        "Exact scale, organozinc equivalents, solvent, NMR standard, workup, and atmosphere are not stated.",
        "The two product structures remain machine-unverified.",
    ],
))


# Pages 2--3, Scheme 4: successive stages are independent experiments.
for suffix, lithium_label, lithium_smiles, product, reported_yield in [
    ("4a", "n-BuLi", "[Li]CCCC", "4a (R6=n-Bu)", 87),
    ("4b", "MeLi", "[Li]C", "4b (R6=Me)", 85),
]:
    records.append(rec(
        f"scheme4_addition_to_{suffix}", "reported_experiment", ev23,
        [
            part("cyclobutenone_2a", "reactant", "2a", ev23, name="2-butyl-3-ethyl-4,4-dipropylcyclobut-2-enone", smiles="O=C1C(CCCC)=C(CC)C1(CCC)CCC"),
            part("organolithium", "reagent", lithium_label, ev23, smiles=lithium_smiles),
            solvent_part("THF", ev23, smiles="C1CCOC1"),
            part("cyclobutenol", "product", product, ev23),
        ],
        [step("one_two_addition", ["cyclobutenone_2a", "organolithium", "solvent"], [
            fld("solvent", "THF", ev23), fld("temperature", qty(-78, "°C"), ev23), fld("time", None, ev23)
        ])],
        [
            fld("reported_yield_cyclobutenol", qty(reported_yield, "%"), ev23, ["cyclobutenol"]),
            fld("yield_measurement_basis", None, ev23, ["cyclobutenol"]),
        ],
        unresolved=[
            "Organolithium equivalents, scale, reaction time, yield basis, workup, purification, and atmosphere are not stated in Scheme 4.",
            "Cyclobutenol structure and stereochemistry remain machine-unverified.",
        ],
    ))

for suffix, reactant_label, product_label, reported_yield in [
    ("5a", "4a (R6=n-Bu)", "5a (R6=n-Bu)", 83),
    ("5b", "4b (R6=Me)", "5b (R6=Me)", 89),
]:
    records.append(rec(
        f"scheme4_ring_opening_to_{suffix}", "reported_experiment", ev23,
        [
            part("cyclobutenol", "reactant", reactant_label, ev23),
            part("lda", "reagent", "LDA", ev23, smiles="CC(C)[N-]C(C)C.[Li+]"),
            solvent_part("toluene", ev23, smiles="Cc1ccccc1"),
            part("enone", "product", product_label, ev23),
        ],
        [step("ring_opening", ["cyclobutenol", "lda", "solvent"], [
            fld("solvent", "toluene", ev23), fld("temperature", None, ev23), fld("time", None, ev23)
        ])],
        [
            fld("reported_yield_enone", qty(reported_yield, "%"), ev23, ["enone"]),
            fld("yield_measurement_basis", None, ev23, ["enone"]),
        ],
        unresolved=[
            "LDA loading, scale, temperature, time, yield basis, workup, purification, and atmosphere are not stated in Scheme 4.",
            "Enone connectivity and alkene geometry remain machine-unverified.",
        ],
    ))


# Page 3, Table 4. Footnote c is preserved literally because it conflicts with R6=Me.
table4 = [
    (1, "2b (R1/R2/R3=Pr/Me/Bu)", "n-BuLi", "[Li]CCCC", qty(3, "equiv"), qty(2.5, "M"), "THF", 1, "cis-4c", 65, "trans-4c", 25),
    (2, "2c (R1/R2/R3=i-Pr/Me/Bu)", "n-BuLi", "[Li]CCCC", qty(3, "equiv"), qty(2.5, "M"), "THF", 0.5, "cis-4d", 76, "trans-4d", 9),
]
for entry, substrate, reagent, reagent_smiles, equiv, conc, solv, duration, cis, cis_y, trans, trans_y in table4:
    ps = [
        part("cyclobutenone", "reactant", substrate, EV[3]),
        part("organolithium", "reagent", reagent, EV[3], smiles=reagent_smiles, amounts=[
            fld("equivalents", equiv, EV[3]), fld("concentration", conc, EV[3])
        ]),
        solvent_part(solv, EV[3], smiles="C1CCOC1"),
        part("cis_product", "product", cis, EV[3]),
        part("trans_product", "product", trans, EV[3]),
    ]
    records.append(rec(
        f"table4_entry{entry}", "substrate_scope_entry", EV[3], ps,
        [step("one_two_addition", ["cyclobutenone", "organolithium", "solvent"], [
            fld("solvent", solv, EV[3]), fld("temperature", qty(-78, "°C"), EV[3]), fld("time", qty(duration, "h"), EV[3])
        ])],
        [
            fld("isolated_yield_cis_product", qty(cis_y, "%"), EV[3], ["cis_product"]),
            fld("isolated_yield_trans_product", qty(trans_y, "%"), EV[3], ["trans_product"]),
            fld("yield_measurement_basis", "isolated", EV[3], ["cis_product", "trans_product"]),
        ],
        notes=["The n-BuLi solution is stated as 2.5 M in n-hexane."],
        unresolved=[
            "Reaction scale, workup, purification, atmosphere, and product masses are not stated in Table 4.",
            "Product structures and relative stereochemistry remain machine-unverified.",
        ],
    ))

entry3_common_participants = [
    part("cyclobutenone", "reactant", "2f (R1/R2/R3=i-Pr/Me/Ph)", EV[3]),
    part("meli_header", "reagent", "MeLi (implied by R6=Me and footnote a)", EV[3], smiles="[Li]C", amounts=[
        fld("concentration", qty(1.3, "M"), EV[3])
    ]),
    part("nbuli_footnote", "unspecified_agent", "n-BuLi (as printed in footnote c)", EV[3], smiles="[Li]CCCC", amounts=[
        fld("equivalents", qty(4, "equiv"), EV[3]), fld("concentration", qty(2.5, "M"), EV[3])
    ]),
]
records.append(rec(
    "table4_entry3", "substrate_scope_entry", EV[3],
    entry3_common_participants + [
        solvent_part("Et2O", EV[3], smiles="CCOCC"),
        part("cis_product", "product", "cis-4e", EV[3]),
        part("trans_product", "product", "trans-4e", EV[3]),
    ],
    [step("one_two_addition", ["cyclobutenone", "meli_header", "nbuli_footnote", "solvent"], [
        fld("solvent", "Et2O", EV[3]), fld("temperature", qty(-78, "°C"), EV[3]), fld("time", qty(4, "h"), EV[3])
    ])],
    [
        fld("isolated_yield_cis_product", qty(70, "%"), EV[3], ["cis_product"]),
        fld("isolated_yield_trans_product", qty(13, "%"), EV[3], ["trans_product"]),
        fld("reported_conversion", qty(93, "%"), EV[3]),
        fld("yield_measurement_basis", "isolated", EV[3], ["cis_product", "trans_product"]),
    ],
    notes=["Footnote c explicitly prints n-BuLi (2.5 M in n-hexane), while the row gives R6=Me and footnote a maps Me to MeLi (1.3 M in Et2O). Both source statements are retained without correction."],
    unresolved=[
        "The organolithium identity in Table 4 entry 3 is internally inconsistent in the printed source.",
        "Reaction scale, workup, purification, atmosphere, and product masses are not stated.",
        "Product structures and relative stereochemistry remain machine-unverified.",
    ],
))

records.append(rec(
    "table4_entry3_thf_comparison", "optimization_entry", EV[3],
    entry3_common_participants + [solvent_part("THF", EV[3], smiles="C1CCOC1")],
    [step("comparison_run", ["cyclobutenone", "meli_header", "nbuli_footnote", "solvent"], [
        fld("solvent", "THF", EV[3]), fld("temperature", qty(-78, "°C"), EV[3]), fld("time", None, EV[3])
    ])],
    [fld("reported_conversion", qty(69, "%"), EV[3])],
    notes=["Footnote c reports 69% conversion in THF as the comparison to the 93% conversion in Et2O."],
    unresolved=[
        "The organolithium identity is internally inconsistent in the printed source, and the THF comparison time and product yields are not given.",
        "Scale, workup, purification, atmosphere, and product identities for the comparison run are not stated.",
    ],
))


# Page 3, Table 5.
table5 = [
    (1, "cis-4c", "n-Pr", "n-Bu", "n-Bu", 3.5, "r.t.", "Z-5c", 91, "single isomer detected"),
    (2, "cis-4d", "i-Pr", "n-Bu", "n-Bu", 2, "r.t.", "Z-5d", 87, "single isomer detected"),
    (3, "cis-4e", "i-Pr", "Ph", "Me", 36, qty(-20, "°C"), "Z-5e", 85, "single isomer detected"),
    (4, "trans-4c", "n-Pr", "n-Bu", "n-Bu", 4, "r.t.", "E-5c", 87, "single isomer detected"),
    (5, "trans-4e", "i-Pr", "Ph", "Me", 4, "r.t.", "E-5e", 85, "E/Z >= 98/2"),
]
for entry, substrate, r1, r3, r6, duration, temperature, product, product_yield, selectivity in table5:
    ps = [
        part("cyclobutenol", "reactant", f"{substrate} (R1={r1}, R3={r3}, R6={r6})", EV[3]),
        part("lda", "reagent", "LDA", EV[3], smiles="CC(C)[N-]C(C)C.[Li+]"),
        solvent_part("THF/toluene", EV[3], smiles=None),
        part("enone", "product", product, EV[3]),
    ]
    records.append(rec(
        f"table5_entry{entry}", "substrate_scope_entry", EV[3], ps,
        [step("lda_promoted_ring_opening", ["cyclobutenol", "lda", "solvent"], [
            fld("LDA_solution_concentration", qty(2.0, "M"), EV[3]),
            fld("solvent", "LDA in THF; reaction shown with toluene", EV[3]),
            fld("temperature", temperature, EV[3]),
            fld("time", qty(duration, "h"), EV[3]),
        ])],
        [
            fld("isolated_yield_enone", qty(product_yield, "%"), EV[3], ["enone"]),
            fld("yield_measurement_basis", "isolated", EV[3], ["enone"]),
            fld("stereoisomer_selectivity", selectivity, EV[3], ["enone"]),
        ],
        unresolved=[
            "Reaction scale, LDA equivalents, solvent volumes, workup, purification, atmosphere, and product mass are not stated.",
            "Product structure and alkene geometry remain machine-unverified; the paper states geometry was assigned by NOESY.",
        ],
    ))


# Page 3, Scheme 5 is a proposed stereochemical mechanism, not a reported batch.
records.append(rec(
    "scheme5_proposed_retro_4e_mechanism", "mechanism", EV[3],
    [
        part("cis_or_trans_4", "reactant", "cis-4 or trans-4 (generic R groups)", EV[3]),
        part("lda", "reagent", "LDA", EV[3], smiles="CC(C)[N-]C(C)C.[Li+]"),
        part("lithium_cyclobutenoxide", "unspecified_agent", "proposed lithium 2-cyclobutenoxide", EV[3]),
        part("z_or_e_5", "product", "Z-5 or E-5 (generic R groups)", EV[3]),
    ],
    [step("proposed_conrotatory_opening", ["cis_or_trans_4", "lda", "lithium_cyclobutenoxide"], [
        fld("operation", "proposed concerted conrotatory retro-4e-cycloaddition followed by protonation", EV[3])
    ])],
    [],
    notes=["Scheme 5 is explicitly an explanation for the observed stereochemistry and is classified as a mechanism."],
    unresolved=["Generic R groups and proposed intermediates are not encoded as verified structures; no batch-specific conditions or yield belong to this mechanism record."],
))


# Page 4, reference 10 contains a quantitative prior-literature example.
records.append(rec(
    "reference10_cobalt_prior_example", "literature_example", EV[4],
    [
        part("prior_substrate", "reactant", "ethyl 2,4,4-triphenyl-2,3-butadienoate", EV[4]),
        part("co2co8", "catalyst", "Co2(CO)8", EV[4]),
        part("prior_product", "product", "3-ethoxy-2,4,4-triphenylcyclobutenone", EV[4]),
    ],
    [step("prior_cobalt_transformation", ["prior_substrate", "co2co8"], [])],
    [
        fld("reported_yield_prior_product", qty(12, "%"), EV[4], ["prior_product"]),
        fld("reported_conversion", qty(20, "%"), EV[4]),
        fld("yield_measurement_basis", None, EV[4], ["prior_product"]),
    ],
    notes=["This is a prior-literature result cited as reference 10 (Trifonov, Orahovats, and Heimgartner, Helv. Chim. Acta 1987, 70, 1070)."],
    unresolved=["Catalyst loading, scale, solvent, temperature, time, workup, purification, and yield basis are absent from the citing text."],
))


def ids(prefix):
    return [r["record_id"] for r in records if r["source_reaction_id"].startswith(prefix)]


coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1,
            "state": "attempted",
            "regions": [
                {
                    "region": "upper-left title and abstract; lower-left introduction and opening optimization prose",
                    "finding": "The abstract and introduction give broad scope and prior-work context. The opening 1a/Et2Zn result is the same experiment as Table 1 entry 1 and was not duplicated.",
                    "evidence_ids": EV[1],
                },
                {
                    "region": "upper-right Scheme 1",
                    "finding": "The [2+2] branches are prior literature; the allenoate-to-cyclobutenone branch and A/B intermediates are a generic concept/mechanistic scheme, not batch experiments.",
                    "evidence_ids": EV[1],
                },
                {
                    "region": "middle/lower-right Table 1 including reaction drawing and footnote a",
                    "finding": "All 11 independent optimization rows were extracted with solvent, temperature, time, catalyst loading, NMR yields of 2a/3a, and recovered 1a.",
                    "evidence_ids": EV[1],
                },
            ],
            "record_ids": ids("scheme1_") + ids("table1_"),
            "unresolved": [
                "Table 1 omits exact scale, workup, purification, and atmosphere.",
                "The SI link is advertised but no SI file was supplied or explicitly associated.",
            ],
        },
        {
            "page": 2,
            "state": "attempted",
            "regions": [
                {
                    "region": "left column Table 2, generic reaction drawing, rows 1-21, and footnotes a-d",
                    "finding": "Twenty-one substrate-scope rows were extracted independently, including the xylenes/140 °C override, the 5.0 mmol run, and hydrolysis-product footnotes.",
                    "evidence_ids": EV[2],
                },
                {
                    "region": "upper-right Figure 1",
                    "finding": "ORTEP drawings characterize 2s and trans-4e; they do not create additional reaction experiments.",
                    "evidence_ids": EV[2],
                },
                {
                    "region": "middle-right Table 3, generic reaction drawing, and footnote a",
                    "finding": "Four functional-group scope rows were extracted with 0.4 mmol substrate, 5 mL toluene, 3 equiv 1.5 M Et2Zn, 100 °C, time, and isolated yield.",
                    "evidence_ids": EV[2],
                },
                {
                    "region": "lower-right mechanistic-control and application prose",
                    "finding": "Narrative details were linked to the page-3 Scheme 2-4 records: two Et2Zn branches, one failed EtMgBr branch, the Scheme 3 controls, and successive organolithium/LDA stages.",
                    "evidence_ids": EV[2],
                },
            ],
            "record_ids": ids("table2_") + ids("table3_") + ids("scheme2_") + ids("scheme3_") + ids("scheme4_"),
            "unresolved": [
                "Most scope rows omit atmosphere, workup, purification, product masses, and full structure verification.",
                "Entry 21 does not state the solvent volume for the 5.0 mmol scale run.",
            ],
        },
        {
            "page": 3,
            "state": "attempted",
            "regions": [
                {
                    "region": "upper-left Scheme 2",
                    "finding": "Two Et2Zn control branches and the failed EtMgBr heated branch were extracted as separate experiments; the complicated mixture remains compositionally unresolved.",
                    "evidence_ids": EV[3],
                },
                {
                    "region": "middle-left Scheme 3",
                    "finding": "The room-temperature arrow marked ref. 13 is a literature example; the 100 °C/30 min mixed-product control is a present reported experiment with product-specific NMR yields.",
                    "evidence_ids": EV[3],
                },
                {
                    "region": "lower-left Scheme 4",
                    "finding": "The two organolithium additions and two subsequent LDA ring openings were separated into four successive-stage experiment records.",
                    "evidence_ids": EV[3],
                },
                {
                    "region": "upper-right Table 4 and footnotes a-c",
                    "finding": "Three scope rows plus the distinct 69% THF conversion comparison were extracted. The printed entry-3 organolithium inconsistency is preserved without correction.",
                    "evidence_ids": EV[3],
                },
                {
                    "region": "middle-right Table 5 and footnotes a-c",
                    "finding": "Five LDA-promoted ring-opening rows were extracted with times, temperature override, isolated yields, and reported stereoselectivity.",
                    "evidence_ids": EV[3],
                },
                {
                    "region": "lower-right Scheme 5 and adjacent stereochemical discussion",
                    "finding": "The conrotatory retro-4e proposal was classified as a mechanism and not assigned experimental yields.",
                    "evidence_ids": EV[3],
                },
            ],
            "record_ids": ids("scheme2_") + ids("scheme3_") + ids("scheme4_") + ids("table4_") + ids("table5_") + ids("scheme5_"),
            "unresolved": [
                "Table 4 entry 3 prints R6=Me but footnote c names n-BuLi; the source inconsistency requires expert review.",
                "Many schemes and tables omit scale, reagent loading, workup, purification, atmosphere, or yield basis.",
                "Depicted complex structures and stereochemical assignments remain machine-unverified.",
            ],
        },
        {
            "page": 4,
            "state": "attempted",
            "regions": [
                {
                    "region": "upper-left conclusion continuation and Associated Content",
                    "finding": "No new experiment is reported. The page advertises Supporting Information, but no SI was provided or explicitly associated in this workspace.",
                    "evidence_ids": EV[4],
                },
                {
                    "region": "left-column author information and acknowledgments",
                    "finding": "Administrative content only; the reproducibility acknowledgment points to selected earlier table rows but does not create new experiments.",
                    "evidence_ids": EV[4],
                },
                {
                    "region": "two-column references, especially reference 10",
                    "finding": "References are prior literature, not experiments of this paper. The quantitative Co2(CO)8 example in reference 10 was retained as a literature-example record; other references lack sufficient batch detail or are general citations.",
                    "evidence_ids": EV[4],
                },
            ],
            "record_ids": ids("reference10_"),
            "unresolved": [
                "The cited reference-10 example omits most conditions and its yield measurement basis.",
                "No SI-only experimental details were imported because SI was not supplied or explicitly associated.",
            ],
        },
    ],
}


OUT.mkdir(parents=True, exist_ok=True)
(OUT / "records_pages_0001_0004.json").write_text(
    json.dumps(records, ensure_ascii=False, indent=2) + "\n"
)
coverage_path = ROOT / "runs/current/coverage/pages_0001_0004.json"
coverage_path.parent.mkdir(parents=True, exist_ok=True)
coverage_path.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

tasks_path = ROOT / "runs/current/tasks.json"
tasks = json.loads(tasks_path.read_text())
for task in tasks:
    if task["document_id"] == DOC and task["task_id"] in {f"{DOC}:page{p}:text" for p in range(1, 5)}:
        task["state"] = "attempted"
        task["reason"] = "Original page image and page text inspected; records and coverage ledger generated for this page."
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"records": len(records), "coverage_pages": [p["page"] for p in coverage["pages"]]}, ensure_ascii=False))
