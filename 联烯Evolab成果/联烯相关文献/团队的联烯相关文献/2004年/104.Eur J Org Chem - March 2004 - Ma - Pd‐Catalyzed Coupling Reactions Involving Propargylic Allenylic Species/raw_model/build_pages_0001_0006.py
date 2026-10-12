#!/usr/bin/env python3
"""Build evidence-linked raw records for visually inspected PDF pages 1-6."""

import json
from pathlib import Path


DOC = "doc_2da56877b1a5d32e"
OUT = Path(__file__).with_name("extracted_records_pages_0001_0006.json")
records = []


def fact(value, evidence):
    return {
        "value": value,
        "evidence_ids": list(evidence) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def p(role, label, *, smiles=None, amounts=None):
    return {
        "role": role,
        "label": label,
        "smiles": smiles,
        "amounts": amounts or [],
    }


def q(name, value):
    return (name, value)


def add(page, suffix, kind, participants, *, conditions=None, outcomes=None,
        notes=None, unresolved=None):
    evidence = [f"{DOC}:page{page}:text", f"{DOC}:page{page}:image"]
    built = []
    product_ids = []
    for idx, spec in enumerate(participants, 1):
        entity_id = f"e{idx:02d}"
        amounts = [
            {"name": name, "fact": fact(value, evidence)}
            for name, value in spec.get("amounts", [])
        ]
        item = {
            "entity_id": entity_id,
            "role": spec["role"],
            "label": fact(spec["label"], evidence),
            "name": fact(None, evidence),
            "smiles": fact(spec.get("smiles"), evidence),
            "smiles_parseable": None,
            "structure_verified": False,
            "amounts": amounts,
        }
        built.append(item)
        if item["role"] == "product":
            product_ids.append(entity_id)

    fields = []
    for outcome in outcomes or []:
        name, value = outcome[:2]
        target_ordinals = outcome[2] if len(outcome) > 2 else None
        field = {"name": name, "fact": fact(value, evidence)}
        if target_ordinals is not None:
            field["target_entity_ids"] = [product_ids[i] for i in target_ordinals]
        elif product_ids:
            field["target_entity_ids"] = list(product_ids)
        fields.append(field)

    step_conditions = [
        {"name": name, "fact": fact(value, evidence)}
        for name, value in (conditions or [])
    ]
    record_id = f"{DOC}:{suffix}"
    base_unresolved = [
        "This record is a review summary of prior literature or a mechanistic/general scheme, not a new experiment reported by this review.",
        "No explicitly associated Supporting Information was supplied; scale, detailed procedure, workup, purification, and yield basis are missing unless shown.",
    ]
    record = {
        "record_id": record_id,
        "document_id": DOC,
        "source_reaction_id": suffix,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": evidence,
        "participants": built,
        "steps": ([{
            "step_id": "s1",
            "participant_ids": [x["entity_id"] for x in built],
            "conditions": step_conditions,
        }] if built or step_conditions else []),
        "outcomes": fields,
        "notes": [fact(x, evidence) for x in (notes or [])],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": base_unresolved + (unresolved or []),
        },
    }
    records.append(record)
    return record_id


# Page 1: conceptual catalytic cycle and the two regioselective product branches.
add(1, "p1_scheme1_pd_cross_coupling_cycle", "mechanism", [
    p("reactant", "R-LG"), p("reagent", "R'-M"), p("catalyst", "Pd(0)"),
    p("product", "R-R'"),
], notes=["Scheme 1 is a generic Pd-catalyzed cross-coupling cycle."],
    unresolved=["All structures are generic R-group representations."])
add(1, "p1_scheme2_allene_branch", "mechanism", [
    p("unspecified_agent", "allenyl-Pd species 1"), p("product", "allene 4"),
], notes=["Reductive elimination from allenyl-Pd species 1 is drawn to give allene 4."],
    unresolved=["Substituents R1-R4 are generic."])
add(1, "p1_scheme2_alkyne_branch", "mechanism", [
    p("unspecified_agent", "propargyl-Pd species 3"), p("product", "alkyne 5"),
], notes=["Reductive elimination from propargyl-Pd species 3 is drawn to give alkyne 5."],
    unresolved=["Substituents R1-R4 are generic."])


# Page 2, Scheme 3: four separately drawn preparations/outcomes.
add(2, "p2_scheme3_complex6", "literature_example", [
    p("reactant", "PdMe2(tmeda)"), p("reagent", "K[(pz)3BH]"),
    p("reactant", "2-butynyl bromide"), p("solvent", "acetone", smiles="CC(=O)C"),
    p("product", "η1-allenylic Pd complex 6"),
], conditions=[q("solvent", "acetone")],
    outcomes=[("yield", {"number": 73, "unit": "%"})])
add(2, "p2_scheme3_complex7", "literature_example", [
    p("reactant", "PdMe2(tmeda)"), p("reagent", "K[(pz)3BH]"),
    p("reactant", "2-propynyl bromide"), p("solvent", "acetone", smiles="CC(=O)C"),
    p("product", "η1-propargylic Pd complex 7"),
], conditions=[q("solvent", "acetone")],
    outcomes=[("yield", {"number": 87, "unit": "%"})])
add(2, "p2_scheme3_complex8", "literature_example", [
    p("reactant", "PdMe2(bpy)"), p("reactant", "2-butynyl bromide"),
    p("solvent", "acetone", smiles="CC(=O)C"), p("product", "η1-allenylic Pd complex 8"),
], conditions=[q("solvent", "acetone"), q("temperature", {"number": -30, "unit": "°C"})],
    outcomes=[("yield", {"number": 76, "unit": "%"})])
add(2, "p2_scheme3_complexes9_10", "literature_example", [
    p("reactant", "PdMe2(bpy)"), p("reactant", "excess 2-propynyl bromide"),
    p("solvent", "[D6]acetone"), p("product", "Pd complex 9"), p("product", "Pd complex 10"),
], conditions=[q("solvent", "[D6]acetone"), q("temperature", {"number": -20, "unit": "°C"})],
    outcomes=[("product_ratio_9_to_10", "2:1")],
    unresolved=["No combined or individual yield is printed for complexes 9 and 10."])

# Page 2, Scheme 4: two stereochemical oxidative-addition examples.
add(2, "p2_scheme4_11_to_12", "literature_example", [
    p("reactant", "(R)-propargylic acetate 11"), p("reagent", "LiCl"),
    p("catalyst", "Pd(PPh3)4"), p("solvent", "THF", smiles="C1CCOC1"),
    p("product", "(R)-(−)-allenylic Pd complex 12"),
], conditions=[q("solvent", "THF")], outcomes=[("stereochemical_course", "anti-process")])
add(2, "p2_scheme4_13_to_14", "literature_example", [
    p("reactant", "(S)-allenylic bromide 13"), p("catalyst", "Pd(PPh3)4"),
    p("solvent", "THF", smiles="C1CCOC1"), p("product", "(R)-(−)-allenylic Pd complex 14"),
], conditions=[q("solvent", "THF")], outcomes=[("stereochemical_course", "inversion")])

# Page 2, Scheme 5: cationic and neutral η3-complex preparations.
add(2, "p2_scheme5_cationic_complex17", "literature_example", [
    p("reactant", "η1-allenylic/propargylic Pd halide or tosylate 15/16"),
    p("reagent", "Ag+Y−"), p("solvent", "CH2Cl2", smiles="ClCCl"),
    p("product", "cationic η3-allenylic/propargylic Pd complex 17"),
], conditions=[q("solvent", "CH2Cl2"), q("temperature", "r.t.")],
    notes=["Y− is shown as BF4−, BPh4−, or OTf−; the starting leaving group X is Cl, Br, or TsO."],
    unresolved=["The alternatives are summarized together in the review and individual yields are absent."])
add(2, "p2_scheme5_neutral_complex20", "literature_example", [
    p("reactant", "tert-butyl-substituted propargylic chloride"),
    p("reagent", "Pd2(dba)3·CHCl3", amounts=[q("relative_amount", {"number": 1, "unit": "equiv"})]),
    p("reagent", "PPh3", amounts=[q("relative_amount", {"number": 2, "unit": "equiv"})]),
    p("reagent", "C6F5Li"), p("unspecified_agent", "equilibrating Pd species 18/19"),
    p("product", "neutral η3-Pd complex 20"),
], notes=["Complex 20 is stated to have been determined by X-ray diffraction."],
    unresolved=["The review does not print temperature, time, solvent, or yield for this summarized preparation."])


# Page 3, Scheme 6: four conceptual reactivity classes, one record per outgoing arrow.
for typ, label, product in [
    (1, "soft nucleophile addition", "soft-nucleophile substitution product"),
    (2, "SET or transmetallation followed by E+", "electrophile-trapped allene and/or alkyne"),
    (3, "CO/RNC insertion", "inserted acyl/imidoyl Pd species"),
    (4, "coupling with hard nucleophile R1-M", "allene plus alkyne regioisomer"),
]:
    add(3, f"p3_scheme6_type{typ}", "mechanism", [
        p("unspecified_agent", "η1/η3-allenyl/propargyl Pd manifold"),
        p("unspecified_agent", label), p("product", product),
    ], notes=[f"Scheme 6 labels this conceptual branch as Type {typ}."],
        unresolved=["This is a reactivity classification, not a fully specified experimental procedure."])

# Page 3, Schemes 7-10, including explicit control/failure observations.
add(3, "p3_scheme7_grignard_coupling", "literature_example", [
    p("reactant", "propargylic halide 21 or allenylic halide 22"), p("reagent", "RMgX"),
    p("catalyst", "PdCl2"), p("reagent", "PPh3"), p("reagent", "iBu2AlH"),
    p("product", "trisubstituted allene 23"),
], outcomes=[("yield", {"minimum": 48, "maximum": 98, "unit": "%", "raw_text": "48–98%"}),
             ("allene_to_alkyne_selectivity", "90–99:10–1")],
    unresolved=["Substituent-specific rows and exact catalyst/reagent loadings are not provided."])
add(3, "p3_scheme7_no_pd_control", "literature_example", [
    p("reactant", "propargylic/allenylic halide 21/22"), p("reagent", "RMgX"),
    p("product", "allene/alkyne mixture"),
], conditions=[q("operation", "reaction conducted in the absence of Pd catalyst")],
    outcomes=[("selectivity", "low selectivity")],
    notes=["The prose states that the same reaction without Pd gave an allene/alkyne mixture."])
add(3, "p3_scheme8_organozinc_coupling", "literature_example", [
    p("reactant", "allenylic halide 22 or propargylic halide/acetate 21"), p("reagent", "RZnCl"),
    p("catalyst", "Pd(PPh3)4"), p("solvent", "THF", smiles="C1CCOC1"),
    p("product", "allene 23"),
], conditions=[q("solvent", "THF or THF-Et2O")],
    outcomes=[("yield", {"minimum": 80, "maximum": 95, "unit": "%", "raw_text": "80–95%"})],
    unresolved=["The scheme is a generic scope summary with R groups."])
add(3, "p3_scheme9_epoxide_organozinc", "literature_example", [
    p("reactant", "α-acetylenic epoxide 24"), p("reagent", "R-ZnCl"),
    p("catalyst", "Pd(PPh3)4"), p("product", "2,3-allenol 25"),
], outcomes=[("conversion", {"number": 98, "unit": "%", "qualifier": "gt", "raw_text": ">98% conversion"})],
    unresolved=["No isolated yield or reaction time/temperature is printed."])
add(3, "p3_scheme9_alkynyllithium_magnesium_failure", "literature_example", [
    p("reactant", "α-acetylenic epoxide 24 (R=Ph)"),
    p("reagent", "1-alkynyllithium or 1-alkynylmagnesium chloride"),
    p("product", "unidentified products"),
], outcomes=[("reaction_result", "poor results; only unidentified products formed")],
    unresolved=["The prose does not assign separate results to the lithium and magnesium reagents."])
add(3, "p3_scheme10_24a_buzncl", "literature_example", [
    p("reactant", "1-methyl-1-(1'-propynyl)epoxide 24a", smiles="CC#CC1(C)CO1"),
    p("reagent", "BuZnCl"), p("catalyst", "Pd(PPh3)4"),
    p("product", "2,4-dimethylocta-2,3-dienol 25a", smiles="CCCC(C)=C=C(C)CO"),
    p("product", "2-methyl-2,3-pentadienol 26", smiles="CC=C=C(C)CO"),
], outcomes=[("yield_25a", {"number": 20, "unit": "%", "qualifier": "lt", "raw_text": "<20%"}, [0]),
             ("yield_26", {"number": 80, "unit": "%", "qualifier": "approx", "raw_text": "~80%"}, [1])],
    unresolved=["Yield measurement bases are not stated; candidate SMILES are unverified interpretations of the drawing/names."])
add(3, "p3_scheme10_beta_h_elimination_path", "mechanism", [
    p("reactant", "epoxide 24a"), p("unspecified_agent", "allenylic Pd intermediate"),
    p("unspecified_agent", "Bu-Pd intermediate 27"), p("product", "allene 26"),
], notes=["The review proposes β-H elimination from 27 followed by reductive elimination to explain formation of 26."],
    unresolved=["The intermediates are proposed, not isolated experimental outcomes in this review."])


# Page 4, Schemes 11-17.
add(4, "p4_scheme11_antistereoselective_coupling", "literature_example", [
    p("reactant", "(R)-1-phenyl propargyl derivative 28"), p("reagent", "PhZnCl"),
    p("catalyst", "Pd(PPh3)4", amounts=[q("catalyst_loading", {"minimum": 2.5, "maximum": 3.2, "unit": "mol%", "raw_text": "2.5–3.2% Pd(PPh3)4"})]),
    p("solvent", "THF-Et2O"), p("product", "(R)-(−)-1,3-diphenylallene 29"),
], conditions=[q("solvent", "THF-Et2O")], outcomes=[("anti_to_syn_ratio", "82:18")],
    notes=["The leaving group X is acetate, trifluoroacetate, or sulfate; the review says it has little effect on stereoselectivity."],
    unresolved=["Separate yields for the three leaving groups are not supplied."])
for rval in ("Ph", "tBu"):
    add(4, f"p4_scheme12_allenyl_bromide_{rval.lower()}", "literature_example", [
        p("reactant", f"(R)-allenyl bromide 30 (R={rval})"), p("reagent", "Ph2Zn"),
        p("catalyst", "Pd(PPh3)4"), p("solvent", "THF", smiles="C1CCOC1"),
        p("product", f"(S)-optically active allene 31 (R={rval})"),
    ], conditions=[q("solvent", "THF"), q("temperature", {"minimum": 0, "maximum": 20, "unit": "°C", "raw_text": "0–20 °C"})],
        outcomes=[("stereochemical_course", "configuration inverted")],
        unresolved=["No yield or reaction time is shown for this substrate."])
for rf, starting_ee, yld in [("CF3", 96, 77), ("C2F5", 94, 70)]:
    add(4, f"p4_scheme13_rf_{rf.lower()}", "literature_example", [
        p("reactant", f"fluorinated propargylic mesylate 32 (Rf={rf})"), p("reagent", "PhZnCl"),
        p("catalyst", "Pd(PPh3)4"), p("solvent", "THF", smiles="C1CCOC1"),
        p("product", f"fluorinated trisubstituted allene 33 (Rf={rf})"),
    ], conditions=[q("solvent", "THF")],
        outcomes=[("yield", {"number": yld, "unit": "%"}),
                  ("product_ee", {"number": 96, "unit": "%"})],
        notes=[f"Starting mesylate 32 is printed as {starting_ee}% ee."],
        unresolved=["Absolute structure SMILES was not assigned from the stereochemical drawing."])
add(4, "p4_scheme14_complex34_formation", "literature_example", [
    p("reactant", "3-methyl propargylic chloride"),
    p("reagent", "Pd(PPh3)4", amounts=[q("relative_amount", {"number": 1, "unit": "equiv"})]),
    p("solvent", "THF", smiles="C1CCOC1"), p("product", "3-methylbuta-1,2-dienylpalladium complex 34"),
], conditions=[q("solvent", "THF")], unresolved=["No yield, time, or temperature is printed for formation of 34."])
for rval in ("Ph", "TMSC≡C"):
    add(4, f"p4_scheme14_complex34_rzncl_{'ph' if rval == 'Ph' else 'tmsc'}", "literature_example", [
        p("reactant", "Pd complex 34"), p("reagent", f"RZnCl (R={rval})"),
        p("solvent", "THF", smiles="C1CCOC1"), p("unspecified_agent", "η1-allenylpalladium complex 35"),
        p("product", f"allene 36 (R={rval})"),
    ], conditions=[q("solvent", "THF"), q("temperature", {"number": 25, "unit": "°C"})],
        outcomes=[("yield", "quantitative")],
        unresolved=["The review does not give the reaction time or analytical yield basis."])
add(4, "p4_scheme15_aryl_halide_allenylzinc", "literature_example", [
    p("reactant", "propargylic precursor"),
    p("reagent", "HgCl2", amounts=[q("catalyst_loading", {"number": 1.5, "unit": "mol%"})]),
    p("reagent", "nBuLi"), p("reagent", "ZnBr2"), p("reactant", "ArX"),
    p("catalyst", "Pd(PPh3)4 or PdCl2(PPh3)2", amounts=[q("catalyst_loading", {"number": 5, "unit": "mol%"})]),
    p("product", "aryl-substituted allene"),
], conditions=[q("temperature", None)],
    outcomes=[("major_product", "allene")],
    notes=["The nBuLi step is printed as <−20 °C."],
    unresolved=["Generic R/Ar/X scope and exact yield are not given in the review scheme."])
add(4, "p4_scheme16_alkenyl_halide_to_alkyne38", "literature_example", [
    p("reactant", "1-phenyl-1-propyne"), p("reagent", "nBuLi"), p("reagent", "ZnBr2"),
    p("reactant", "3-halo-2-alkenoate or 3-iodo-2-alkenenitrile 37"),
    p("catalyst", "Pd(PPh3)4", amounts=[q("catalyst_loading", {"number": 5, "unit": "mol%"})]),
    p("product", "alkynic product 38"),
], conditions=[q("temperature", None)],
    notes=["The sequence is printed as nBuLi at −78 °C, followed by ZnBr2 at −78 °C to r.t."],
    unresolved=["R, R', X and yield are not specified for an individual substrate in the review scheme."])
for idx, (rval, arval, yld, ratio) in enumerate([
    ("Me3Si", "o-methylphenyl", 52, "100:0"),
    ("Ph", "phenyl", 85, "0:100"),
], 1):
    add(4, f"p4_scheme17_row{idx}", "literature_example", [
        p("reactant", f"propargylic precursor (R={rval})"), p("reagent", "nBuLi"),
        p("reagent", "ZnBr2"), p("reactant", f"ArX (Ar={arval})"),
        p("catalyst", "Pd(PPh3)4", amounts=[q("catalyst_loading", {"number": 5, "unit": "mol%"})]),
        p("product", "alkyne 39"), p("product", "allene 40"),
    ], conditions=[q("temperature", None)],
        outcomes=[("combined_yield", {"number": yld, "unit": "%"}),
                  ("product_ratio_39_to_40", ratio)],
        notes=["The sequence is printed as nBuLi at −78 °C, followed by ZnBr2 in THF from −78 °C to r.t."],
        unresolved=["The review table does not state the yield measurement basis or time."])


# Page 5, Scheme 18 generic organoboron coupling.
add(5, "p5_scheme18_organoboron_coupling", "literature_example", [
    p("reactant", "propargylic carbonate 41"), p("reagent", "organoboron reagent 42"),
    p("catalyst", "Pd(0)"), p("product", "1,2-allene 43"),
], notes=["42 encompasses alkenyl-, alkynyl-, or arylboronic acids/esters and 9-alkyl-9-BBN."],
    unresolved=["Scheme 18 is generic and gives no substrate-specific conditions or yields."])

# Page 5, Scheme 19: eight catalyst rows.
scheme19 = [
    ("H", "C5H11", "Pd2(dba)3·CHCl3", 47, 0),
    ("H", "C5H11", "PdCl2(PPh3)2", 16, 31),
    ("H", "C5H11", "Pd2(dba)3·CHCl3 + 8 PPh3", 0, 63),
    ("H", "C5H11", "Pd(PPh3)4", 0, 60),
    ("(CH2)5", "cyclic", "Pd2(dba)3·CHCl3", 65, 0),
    ("(CH2)5", "cyclic", "PdCl2(PPh3)2", 63, 0),
    ("(CH2)5", "cyclic", "Pd2(dba)3·CHCl3 + 8 PPh3", 63, 0),
    ("(CH2)5", "cyclic", "Pd(PPh3)4", 64, 0),
]
for idx, (r1, r2, catalyst, y45, y46) in enumerate(scheme19, 1):
    add(5, f"p5_scheme19_row{idx}", "literature_example", [
        p("reactant", f"propargylic carbonate (R1={r1}, R2={r2})"),
        p("reagent", "triethyl(1-methylindol-2-yl)borate 44"), p("catalyst", catalyst),
        p("solvent", "THF", smiles="C1CCOC1"), p("product", "allenyl indole 45"),
        p("product", "propargyl indole 46"),
    ], conditions=[q("solvent", "THF"), q("temperature", "reflux")],
        outcomes=[("yield_45", {"number": y45, "unit": "%"}, [0]),
                  ("yield_46", {"number": y46, "unit": "%"}, [1])],
        unresolved=["The yield measurement basis and reaction time are not stated in the review table."])

# Page 5, Scheme 20: four catalyst/nucleophile rows.
scheme20 = [
    ("Ph", "Pd(PPh3)4", 26, "99:1"),
    ("Ph", "1/2 Pd2(dba)3, PPh3", 95, "96:4"),
    ("Ph-C≡C", "Pd(PPh3)4", 100, "3:97"),
    ("Ph-C≡C", "1/2 Pd2(dba)3, PPh3", 73, "4:96"),
]
for idx, (rprime, catalyst, yld, ratio) in enumerate(scheme20, 1):
    add(5, f"p5_scheme20_row{idx}", "literature_example", [
        p("reactant", "tert-butyl-substituted propargylic chloride 47"),
        p("reagent", f"R'SnBu3 48 (R'={rprime})"), p("catalyst", catalyst),
        p("solvent", "THF", smiles="C1CCOC1"), p("product", "alkyne 49"), p("product", "allene 50"),
    ], conditions=[q("solvent", "THF"), q("temperature", {"number": 50, "unit": "°C"})],
        outcomes=[("combined_yield", {"number": yld, "unit": "%"}),
                  ("product_ratio_49_to_50", ratio)],
        unresolved=["Reaction time and yield measurement basis are absent."])

add(5, "p5_scheme21_pyrone_formation", "literature_example", [
    p("reactant", "3-iodo-2-alkenoic acid"), p("reactant", "allenyltin reagent"),
    p("catalyst", "Pd(OAc)2", amounts=[q("catalyst_loading", {"number": 5, "unit": "mol%"})]),
    p("reagent", "PPh3", amounts=[q("relative_loading", {"number": 10, "unit": "mol%"})]),
    p("reagent", "Na2CO3", amounts=[q("relative_amount", {"number": 4, "unit": "equiv"})]),
    p("reagent", "nBu4NBr"), p("solvent", "DMF"),
    p("unspecified_agent", "2,4,5-alkanetrienoic acid intermediate 51"), p("product", "2-pyrone derivative"),
], conditions=[q("solvent", "DMF")],
    outcomes=[("yield", {"minimum": 79, "maximum": 87, "unit": "%", "raw_text": "79–87%"})],
    unresolved=["Generic substituent scope is shown; no time or temperature is printed."])
add(5, "p5_scheme22_terminal_alkyne_coupling", "literature_example", [
    p("reactant", "propargylic carbonate"),
    p("catalyst", "Pd(PPh3)4", amounts=[q("catalyst_loading", {"number": 5, "unit": "mol%"})]),
    p("unspecified_agent", "allenylic Pd intermediate 52"),
    p("reactant", "terminal alkyne"),
    p("catalyst", "CuI", amounts=[q("catalyst_loading", {"number": 1, "unit": "mol%"})]),
    p("reagent", "Et2NH"), p("reagent", "LiCl", amounts=[q("relative_amount", {"number": 2, "unit": "equiv"})]),
    p("product", "alka-1,2-dien-4-yne 53"),
], conditions=[q("temperature", "r.t.")],
    notes=["The scheme shows initial decarboxylation to intermediate 52 before terminal-alkyne coupling."],
    unresolved=["Generic substituents and no yield/time are given."])


# Page 6, Scheme 23: two distinct substrate/condition rows.
add(6, "p6_scheme23_row1_halide_tosylate", "literature_example", [
    p("reactant", "propargylic halide or tosylate"),
    p("reactant", "terminal alkyne", amounts=[q("relative_amount", {"number": 1.1, "unit": "equiv"})]),
    p("catalyst", "Pd(PPh3)4", amounts=[q("catalyst_loading", {"number": 5, "unit": "mol%"})]),
    p("catalyst", "CuI", amounts=[q("relative_amount", {"number": 0.1, "unit": "equiv"})]),
    p("reagent", "iPr2NH", amounts=[q("relative_amount", {"number": 2, "unit": "equiv"})]),
    p("solvent", "benzene", smiles="c1ccccc1"), p("product", "allenyne product"),
], conditions=[q("solvent", "benzene")],
    outcomes=[("yield", {"minimum": 56, "maximum": 91, "unit": "%", "raw_text": "56–91%"})],
    unresolved=["No temperature or time is printed for this generic row."])
add(6, "p6_scheme23_row2_acetate", "literature_example", [
    p("reactant", "propargylic acetate"),
    p("reactant", "1-heptyne", amounts=[q("relative_amount", {"number": 1.4, "unit": "equiv"})]),
    p("catalyst", "Pd(PPh3)4", amounts=[q("catalyst_loading", {"number": 5, "unit": "mol%"})]),
    p("catalyst", "CuI", amounts=[q("catalyst_loading", {"number": 10, "unit": "mol%"})]),
    p("reagent", "ZnCl2", amounts=[q("relative_amount", {"number": 3, "unit": "equiv"})]),
    p("reagent", "iPr2NH", amounts=[q("relative_amount", {"number": 2, "unit": "equiv"})]),
    p("solvent", "THF", smiles="C1CCOC1"), p("product", "allenyne product"),
], conditions=[q("solvent", "THF"), q("temperature", {"number": 65, "unit": "°C"})],
    outcomes=[("yield", {"minimum": 42, "maximum": 74, "unit": "%", "raw_text": "42–74%"})],
    unresolved=["Reaction time is not printed for this generic row."])
add(6, "p6_scheme24_cyclic_carbonate", "literature_example", [
    p("reactant", "cyclic alkynyl carbonate 54"), p("reactant", "terminal alkyne"),
    p("catalyst", "Pd(PPh3)4", amounts=[q("catalyst_loading", {"number": 5, "unit": "mol%"})]),
    p("catalyst", "CuI", amounts=[q("catalyst_loading", {"number": 10, "unit": "mol%"})]),
    p("product", "cyclic 2,3-allenol product"),
], outcomes=[("yield", {"minimum": 76, "maximum": 98, "unit": "%", "raw_text": "76–98%"})],
    unresolved=["No solvent, time, or temperature is shown."])

# Page 6, Scheme 25: three separate cyclization/coupling arrows.
add(6, "p6_scheme25_gamma_lactone", "literature_example", [
    p("reactant", "4-alkynoic acid 55"), p("reagent", "K2CO3"),
    p("reagent", "KBr", amounts=[q("relative_amount", {"number": 0.5, "unit": "equiv"})]),
    p("catalyst", "Pd(OAc)2", amounts=[q("catalyst_loading", {"number": 5, "unit": "mol%"})]),
    p("reagent", "(2-furyl)3P", amounts=[q("relative_loading", {"number": 10, "unit": "mol%"})]),
    p("reactant", "propargylic acetate"), p("solvent", "DMSO", smiles="CS(C)=O"),
    p("product", "allenylic γ-lactone derivative"),
], conditions=[q("solvent", "DMSO"), q("temperature", {"number": 20, "unit": "°C"})],
    outcomes=[("yield", {"minimum": 50, "maximum": 61, "unit": "%", "raw_text": "50–61%"})],
    unresolved=["The numbered additions are shown but individual stage times are absent."])
add(6, "p6_scheme25_intramolecular_benzofuran", "literature_example", [
    p("reactant", "o-(1-alkynyl)phenyl propargyl ether 56"), p("catalyst", "Pd(PPh3)4"),
    p("reagent", "K2CO3"), p("solvent", "DME", smiles="COCCOC"),
    p("product", "allenyl benzo[b]furan"), p("product", "propargyl benzo[b]furan"),
], conditions=[q("solvent", "DME"), q("temperature", {"number": 110, "unit": "°C"})],
    outcomes=[("combined_yield", {"minimum": 52, "maximum": 90, "unit": "%", "raw_text": "52–90%"})],
    unresolved=["The product ratio and reaction time are not printed."])
add(6, "p6_scheme25_inter_benzofuran", "literature_example", [
    p("reactant", "o-(1-alkynyl)phenol 57"), p("reactant", "propargylic carbonate"),
    p("catalyst", "Pd(PPh3)4", amounts=[q("catalyst_loading", {"number": 5, "unit": "mol%"})]),
    p("solvent", "MeCN-THF (4:1)"), p("product", "allenylic benzo[b]furan"),
], conditions=[q("solvent", "MeCN-THF (4:1)"), q("temperature", {"number": 80, "unit": "°C"})],
    outcomes=[("yield", {"minimum": 15, "maximum": 77, "unit": "%", "raw_text": "15–77%"})],
    unresolved=["Reaction time and yield basis are absent; substituents remain generic."])

add(6, "p6_scheme26_cyanoallene", "literature_example", [
    p("reactant", "propargylic carbonate"), p("reagent", "Me3SiCN", smiles="C[Si](C)(C)C#N"),
    p("catalyst", "Pd(PPh3)4", amounts=[q("catalyst_loading", {"number": 5, "unit": "mol%"})]),
    p("solvent", "THF", smiles="C1CCOC1"), p("product", "cyanoallene 58"),
], conditions=[q("solvent", "THF"), q("temperature", "reflux"), q("time", {"number": 1, "unit": "h"})],
    unresolved=["No yield is printed for Scheme 26."])
add(6, "p6_scheme27_dicyanoallene59", "literature_example", [
    p("reactant", "primary propargylic ethyl carbonate"),
    p("reagent", "Me3SiCN", smiles="C[Si](C)(C)C#N"),
    p("catalyst", "Pd(PPh3)4", amounts=[q("catalyst_loading", {"number": 5, "unit": "mol%"})]),
    p("solvent", "THF", smiles="C1CCOC1"), p("product", "dicyanated product 59"),
], conditions=[q("solvent", "THF"), q("temperature", "reflux"), q("time", {"number": 20, "unit": "h"})],
    outcomes=[("yield", {"minimum": 82, "maximum": 83, "unit": "%", "raw_text": "82–83%"})],
    unresolved=["R1 is only specified as alkyl in this summarized scope."])
add(6, "p6_scheme27_dicyano_product60", "literature_example", [
    p("reactant", "n-C6H13-substituted tertiary propargylic methyl carbonate"),
    p("reagent", "Me3SiCN", smiles="C[Si](C)(C)C#N", amounts=[q("relative_amount", {"number": 6, "unit": "equiv"})]),
    p("catalyst", "Pd(PPh3)4", amounts=[q("catalyst_loading", {"number": 5, "unit": "mol%"})]),
    p("solvent", "THF", smiles="C1CCOC1"), p("product", "dicyanated product 60"),
], conditions=[q("solvent", "THF"), q("temperature", "reflux"), q("time", {"number": 20, "unit": "h"})],
    outcomes=[("yield", {"number": 77, "unit": "%"})],
    notes=["The arrow is marked 'idem', interpreted only as the immediately preceding printed catalyst/THF/reflux/20 h conditions."],
    unresolved=["Yield basis is absent; the product drawing was not converted to SMILES."])


OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")

current_dir = OUT.parent.parent
image_evidence = lambda page: [f"{DOC}:page{page}:image"]
ids_by_page = {
    page: [r["record_id"] for r in records if r["source_reaction_id"].startswith(f"p{page}_")]
    for page in range(1, 7)
}
coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1,
            "state": "attempted",
            "regions": [
                {"region": "title, abstract, and Introduction prose", "finding": "Review framing only; no individual experiment is reported in this region.", "evidence_ids": image_evidence(1)},
                {"region": "Scheme 1, lower-left", "finding": "Generic Pd(0) cross-coupling catalytic cycle; recorded as a mechanism, not an experiment.", "evidence_ids": image_evidence(1)},
                {"region": "Scheme 2, lower-right", "finding": "Generic allenyl/propargyl Pd interconversion with separate allene and alkyne reductive-elimination branches; two mechanism records.", "evidence_ids": image_evidence(1)},
                {"region": "author biography and journal footer", "finding": "No reaction experiment.", "evidence_ids": image_evidence(1)},
            ],
            "record_ids": ids_by_page[1],
            "unresolved": ["Scheme 1 and Scheme 2 use generic R groups and provide no experiment-specific quantities."],
        },
        {
            "page": 2,
            "state": "attempted",
            "regions": [
                {"region": "Scheme 3, left column", "finding": "Four separately drawn prior-literature Pd-complex preparation/outcome rows, including yields 73%, 87%, 76%, and a 9:10 ratio of 2:1.", "evidence_ids": image_evidence(2)},
                {"region": "Scheme 4, upper-right", "finding": "Two stereochemical oxidative-addition examples, anti-process and inversion, recorded separately.", "evidence_ids": image_evidence(2)},
                {"region": "Scheme 5, center-right", "finding": "Two prior-literature preparations: cationic complex 17 and neutral/X-ray-characterized complex 20.", "evidence_ids": image_evidence(2)},
                {"region": "bottom-right section heading and Scheme 7 lead-in", "finding": "Narrative lead-in only; Scheme 7 itself appears on page 3 and is not assigned to page 2.", "evidence_ids": image_evidence(2)},
            ],
            "record_ids": ids_by_page[2],
            "unresolved": ["Several complex structures are legible but organometallic connectivity/stereochemistry was not converted to SMILES.", "Scheme 5 omits several procedural quantities and yields."],
        },
        {
            "page": 3,
            "state": "attempted",
            "regions": [
                {"region": "Scheme 6, top", "finding": "Four conceptual reactivity arrows (Types 1-4), each classified as mechanism rather than experiment.", "evidence_ids": image_evidence(3)},
                {"region": "Scheme 7 and adjacent prose, middle-left", "finding": "Prior-literature Grignard coupling plus a separate no-Pd low-selectivity control observation.", "evidence_ids": image_evidence(3)},
                {"region": "Scheme 8, lower-left", "finding": "Generic organozinc coupling literature example with 80-95% yield range.", "evidence_ids": image_evidence(3)},
                {"region": "Scheme 9 and adjacent prose, middle-right", "finding": "Epoxide/organozinc literature example with >98% conversion and separate poor-result observation for alkynyllithium/magnesium reagents when R=Ph.", "evidence_ids": image_evidence(3)},
                {"region": "Scheme 10, lower-right", "finding": "One empirical 24a/BuZnCl reaction with product-specific approximate/bounded yields, plus a separate proposed beta-H-elimination mechanism record.", "evidence_ids": image_evidence(3)},
                {"region": "page-bottom prose after Scheme 10", "finding": "General leaving-group/reagent scope statement; not sufficiently row-specific to create further experiments.", "evidence_ids": image_evidence(3)},
            ],
            "record_ids": ids_by_page[3],
            "unresolved": ["Most Schemes 7-9 are generic scope summaries without substrate-row identities, times, temperatures, or yield bases.", "Scheme 9 failure prose does not separate the lithium and magnesium reagent results."],
        },
        {
            "page": 4,
            "state": "attempted",
            "regions": [
                {"region": "Scheme 11, upper-left", "finding": "Prior-literature anti-stereoselective coupling; three leaving-group alternatives summarized together, anti/syn 82:18.", "evidence_ids": image_evidence(4)},
                {"region": "Scheme 12, mid-left", "finding": "Two R-substrate variants (Ph and tBu) under common conditions, recorded separately.", "evidence_ids": image_evidence(4)},
                {"region": "Scheme 13, lower-left", "finding": "Two fluorinated substrate rows (CF3 and C2F5) with separate yields and product ee values.", "evidence_ids": image_evidence(4)},
                {"region": "Scheme 14, upper-right", "finding": "Complex 34 formation followed by two RZnCl product variants; three prior-literature records.", "evidence_ids": image_evidence(4)},
                {"region": "Scheme 15, center-right", "finding": "Generic aryl-halide coupling via an in-situ organozinc reagent; allene stated as major product.", "evidence_ids": image_evidence(4)},
                {"region": "Scheme 16, lower-right-middle", "finding": "Generic 3-halo-2-alkenoate/nitrile coupling giving alkynic product 38.", "evidence_ids": image_evidence(4)},
                {"region": "Scheme 17 table, bottom-right", "finding": "Two distinct substrate rows with yields 52%/85% and mutually reversed 39:40 product ratios; recorded separately.", "evidence_ids": image_evidence(4)},
            ],
            "record_ids": ids_by_page[4],
            "unresolved": ["Schemes 11-17 are review summaries and generally omit scale, time, workup, purification, and yield basis.", "Mixed numeric/qualitative temperature programs are preserved verbatim in notes rather than coerced into one quantity."],
        },
        {
            "page": 5,
            "state": "attempted",
            "regions": [
                {"region": "Scheme 18, upper-left", "finding": "Generic propargylic-carbonate/organoboron coupling literature example without row-specific yield.", "evidence_ids": image_evidence(5)},
                {"region": "Scheme 19 table, left column", "finding": "Eight distinct catalyst/substrate rows; product-specific yields for allenyl indole 45 and propargyl indole 46 are retained per row.", "evidence_ids": image_evidence(5)},
                {"region": "Scheme 20 table, upper-right", "finding": "Four distinct organotin/catalyst rows with combined yields and 49:50 ratios; recorded separately.", "evidence_ids": image_evidence(5)},
                {"region": "Scheme 21, middle-right", "finding": "Prior-literature allenyltin/iodoalkenoic-acid coupling to 2-pyrone through intermediate 51, yield range 79-87%.", "evidence_ids": image_evidence(5)},
                {"region": "Scheme 22, lower-right", "finding": "Prior-literature terminal-alkyne coupling with explicitly drawn Pd intermediate 52 and product 53; no yield printed.", "evidence_ids": image_evidence(5)},
            ],
            "record_ids": ids_by_page[5],
            "unresolved": ["Scheme 18 is generic; Schemes 19-22 omit reaction times and yield measurement bases.", "Generic R groups prevent source-certain product SMILES assignment."],
        },
        {
            "page": 6,
            "state": "attempted",
            "regions": [
                {"region": "Scheme 23, upper-left", "finding": "Two independent propargylic-halide/tosylate versus acetate coupling rows with distinct equivalents, catalysts, solvent/temperature, and yield ranges.", "evidence_ids": image_evidence(6)},
                {"region": "Scheme 24, middle-left", "finding": "Generic cyclic alkynyl-carbonate/terminal-alkyne coupling, yield range 76-98%.", "evidence_ids": image_evidence(6)},
                {"region": "Scheme 25, lower half across both columns", "finding": "Three separate cyclization/coupling arrows: gamma-lactone formation and two benzo[b]furan routes, each recorded independently.", "evidence_ids": image_evidence(6)},
                {"region": "Scheme 26, upper-right", "finding": "Cyanoallene formation with explicit 5 mol% catalyst, THF reflux, and 1 h; no yield printed.", "evidence_ids": image_evidence(6)},
                {"region": "Scheme 27, middle-right", "finding": "Two different propargylic-carbonate dicyanation rows with 82-83% and 77% yields; the second uses 6 equiv Me3SiCN and 'idem' conditions.", "evidence_ids": image_evidence(6)},
                {"region": "bottom-right hydride-section lead-in", "finding": "The sentence continues onto page 7 and no Scheme 28 arrow/result is visible within page 6; no record fabricated from the incomplete sentence.", "evidence_ids": image_evidence(6)},
            ],
            "record_ids": ids_by_page[6],
            "unresolved": ["The hydride-section sentence is incomplete on page 6; page 7 is outside this session's claimed coverage.", "Most depicted products retain generic substituents and null SMILES."],
        },
    ],
}
coverage_path = current_dir / "coverage" / "pages_0001_0006.json"
coverage_path.parent.mkdir(parents=True, exist_ok=True)
coverage_path.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

tasks_path = current_dir / "tasks.json"
if tasks_path.exists():
    tasks = json.loads(tasks_path.read_text())
    for task in tasks:
        if task.get("document_id") != DOC:
            continue
        for page in range(1, 7):
            if task.get("evidence_id") == f"{DOC}:page{page}:text":
                task["state"] = "attempted"
                task["visual_evidence_id"] = f"{DOC}:page{page}:image"
                task["reason"] = "Original page image inspected; extraction attempted and documented in coverage/pages_0001_0006.json."
    tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"records": len(records), "out": str(OUT), "coverage": str(coverage_path)}, ensure_ascii=False))
