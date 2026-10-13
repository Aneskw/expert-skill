#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "runs/current/raw_model"
DOC = "doc_8ca16f5f6530b9bb"


def ev(page, kind="text"):
    return f"{DOC}:page{page}:{kind}"


def fact(value, evidence):
    return {
        "value": value,
        "evidence_ids": list(evidence) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def fld(name, value, evidence, targets=None):
    result = {"name": name, "fact": fact(value, evidence)}
    if targets:
        result["target_entity_ids"] = list(targets)
    return result


def participant(entity_id, role, label, evidence, *, name=None, smiles=None, amounts=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence) if name is not None else fact(None, evidence),
        "smiles": fact(smiles, evidence) if smiles is not None else fact(None, evidence),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": amounts or [],
    }


def record(rid, kind, evidence, participants, steps, outcomes, notes, unresolved):
    return {
        "record_id": f"{DOC}:{rid}",
        "document_id": DOC,
        "source_reaction_id": rid,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": list(dict.fromkeys(evidence)),
        "participants": participants,
        "steps": steps,
        "outcomes": outcomes,
        "notes": [fact(x, evidence) for x in notes],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved,
        },
    }


smiles_1 = {
    "a": "O=S(c1ccccc1)C=C=CC",
    "b": "O=S(c1ccccc1)C=C=C",
    "c": "O=S(c1ccccc1)C=C=C(CC)",
    "d": "O=S(c1ccccc1)C=C=C(C(C)C)",
    "e": "O=S(c1ccccc1)C=C=C(CCCC)",
    "f": "O=S(c1ccccc1)C=C=C(CCCCCCC)",
    "g": "O=S(c1ccccc1)C=C=C(c1ccccc1)",
    "h": "O=S(c1ccccc1)C=C=C(Cc1ccccc1)",
    "i": "O=S(c1ccccc1)C=C=C(C)CCC",
    "j": "O=S(c1ccccc1)C=C=C(CC)CC",
    "k": "O=S(c1ccccc1)C=C=C1CCCCC1",
    "l": "O=S(c1ccccc1)C=C=C(CCCC)CCCC",
    "m": "CCCCCCCC(S(=O)c1ccccc1)=C=CC",
    "n": "CCCCC(S(=O)c1ccccc1)=C=C(C)C",
}

smiles_2 = {
    "a": "O=S(c1ccccc1)C=C([Se]c1ccccc1)C(O)C",
    "b": "O=S(c1ccccc1)C=C([Se]c1ccccc1)CO",
    "c": "O=S(c1ccccc1)C=C([Se]c1ccccc1)C(O)CC",
    "d": "O=S(c1ccccc1)C=C([Se]c1ccccc1)C(O)C(C)C",
    "e": "O=S(c1ccccc1)C=C([Se]c1ccccc1)C(O)CCCC",
    "f": "O=S(c1ccccc1)C=C([Se]c1ccccc1)C(O)CCCCCCC",
    "g": "O=S(c1ccccc1)C=C([Se]c1ccccc1)C(O)c1ccccc1",
    "h": "O=S(c1ccccc1)C=C([Se]c1ccccc1)C(O)Cc1ccccc1",
    "i": "O=S(c1ccccc1)C=C([Se]c1ccccc1)C(O)(C)CCC",
    "j": "O=S(c1ccccc1)C=C([Se]c1ccccc1)C(O)(CC)CC",
    "k": "O=S(c1ccccc1)C=C([Se]c1ccccc1)C1(O)CCCCC1",
    "l": "O=S(c1ccccc1)C=C([Se]c1ccccc1)C(O)(CCCC)CCCC",
    "m": "CCCCCCCC(S(=O)c1ccccc1)=C([Se]c1ccccc1)C(O)C",
    "n": "CCCCC(S(=O)c1ccccc1)=C([Se]c1ccccc1)C(O)(C)C",
}

names_2 = {
    "a": "E-3-phenylselanyl-4-phenylsulfinyl-3-buten-2-ol",
    "b": "E-2-phenylselanyl-3-phenylsulfinyl-2-propen-1-ol",
    "c": "E-2-phenylselanyl-1-phenylsulfinyl-1-penten-3-ol",
    "d": "E-4-methyl-2-phenylselanyl-1-phenylsulfinyl-1-penten-3-ol",
    "e": "E-2-phenylselanyl-1-phenylsulfinyl-1-hepten-3-ol",
    "f": "E-2-phenylselanyl-1-phenylsulfinyl-1-decen-3-ol",
    "g": "E-1-phenyl-2-phenylselanyl-3-phenylsulfinyl-2-propen-1-ol",
    "h": "E-1-phenyl-3-phenylselanyl-4-phenylsulfinyl-3-buten-2-ol",
    "i": "E-3-methyl-2-phenylselanyl-1-phenylsulfinyl-1-hexen-3-ol",
    "j": "E-3-ethyl-2-phenylselanyl-1-phenylsulfinyl-1-penten-3-ol",
    "k": "E-1,1-(pentamethylene)-2-phenylselanyl-3-phenylsulfinyl-2-propenol",
    "l": "E-3-n-butyl-2-phenylselanyl-1-phenylsulfinyl-hepten-3-ol",
    "m": "E-3-phenylselanyl-4-phenylsulfinyl-3-undecen-2-ol",
    "n": "E-1-methyl-3-phenylselanyl-4-phenylsulfinyl-3-octen-2-ol",
}


def solvent_participants(solvent_text, evidence):
    mapping = {
        "CH2Cl2": ("dichloromethane", "ClCCl"),
        "THF": ("tetrahydrofuran", "C1CCOC1"),
        "Toluene": ("toluene", "Cc1ccccc1"),
        "CH3CN": ("acetonitrile", "CC#N"),
        "DMF": ("N,N-dimethylformamide", "CN(C)C=O"),
        "H2O": ("water", "O"),
    }
    tokens = [x for x in mapping if x in solvent_text]
    return [participant(f"solvent_{x.lower()}", "solvent", x, evidence,
                        name=mapping[x][0], smiles=mapping[x][1]) for x in tokens]


records = []

# Table 1 optimization. Entry 11 is augmented below with the identical Table 2 entry 1
# and the compound-specific typical procedure on page 2.
table1 = [
    (1, 2.0, "CH2Cl2", 10, 10, 32, "72/28"),
    (2, 2.0, "THF", 8, 25, 19, "63/37"),
    (3, 2.0, "Toluene", 8, 30, 50, "63/37"),
    (4, 2.0, "CH3CN", 12, 90, 0, "table dash (—)"),
    (5, 2.0, "THF/H2O=10/1", 10, 90, 77, "60/40"),
    (6, 2.0, "DMF/H2O=10/1", 10, 90, 81, "61/39"),
    (7, 2.0, "CH3CN/H2O=10/1", 11, 10, 84, "60/40"),
    (8, 2.0, "CH3CN/H2O=20/1", 11, 15, 66, "61/39"),
    (9, 1.2, "CH3CN/H2O=10/1", 15, 14, 78, "60/40"),
    (10, 2.0, "CH3CN/H2O=3/1", 12, 240, 77, "59/41"),
    (11, 1.5, "CH3CN/H2O=10/1", 15, 14, 86, "60/40"),
    (12, 2.5, "CH3CN/H2O=10/1", 15, 6, 67, "60/40"),
]

for entry, equiv, solvent_text, temp, minutes, yld, dr in table1:
    evidence = [ev(1, "text"), ev(1, "image")]
    rid = f"table1_entry{entry}"
    extra_notes = []
    unresolved = [
        "Absolute scale, workup, and purification are not reported for this optimization row.",
        "Candidate substrate/product constitutions and E geometry require independent structure review.",
    ]
    substrate_amounts = []
    reagent_amounts = [fld("equivalents", {"number": equiv, "unit": "equiv"}, evidence)]
    product_amounts = []
    solvent_parts = solvent_participants(solvent_text, evidence)
    step_conditions = [
        fld("solvent", solvent_text, evidence),
        fld("temperature", {"number": temp, "unit": "°C"}, evidence),
        fld("time", {"number": minutes, "unit": "min"}, evidence),
    ]
    if entry == 1:
        step_conditions.append(fld("atmosphere", "N2", evidence))
    if entry == 11:
        rid = "table1_entry11_table2_entry1_e2a"
        evidence = [ev(1, "text"), ev(1, "image"), ev(2, "text"), ev(2, "image")]
        substrate_amounts = [
            fld("mass", {"number": 35.4, "unit": "mg"}, evidence),
            fld("amount", {"number": 0.2, "unit": "mmol"}, evidence),
        ]
        reagent_amounts = [
            fld("mass", {"number": 57.2, "unit": "mg"}, evidence),
            fld("amount", {"number": 0.3, "unit": "mmol"}, evidence),
            fld("equivalents", {"number": 1.5, "unit": "equiv"}, evidence),
        ]
        product_amounts = [fld("mass", {"number": 59.8, "unit": "mg"}, evidence)]
        solvent_parts = [
            participant("meoh_no", "solvent", "MeCN", evidence, name="acetonitrile", smiles="CC#N", amounts=[
                fld("initial_solution_volume", {"number": 3, "unit": "mL"}, evidence),
                fld("substrate_solution_volume", {"number": 1, "unit": "mL"}, evidence),
            ]),
            participant("water", "solvent", "H2O", evidence, name="water", smiles="O", amounts=[
                fld("volume", {"number": 0.4, "unit": "mL"}, evidence)
            ]),
        ]
        step_conditions = [
            fld("solvent", "MeCN/H2O=10/1", evidence),
            fld("table_temperature", {"number": 15, "unit": "°C"}, evidence),
            fld("detailed_procedure_temperature", "room temperature", evidence),
            fld("time", {"number": 14, "unit": "min"}, evidence),
            fld("operation", "TLC monitoring to complete consumption; eluent petroleum ether/ethyl acetate=2/1", evidence),
            fld("workup", "Quenched with 10 mL H2O; extracted with diethyl ether (3×20 mL); washed with brine; dried over anhydrous Na2SO4; filtered and evaporated", evidence),
            fld("purification", "Flash chromatography on silica gel, petroleum ether/ethyl acetate=2/1", evidence),
        ]
        extra_notes = [
            "Table 1 entry 11, Table 2 entry 1, and the typical E-2a preparation describe the same 1a/PhSeCl experiment and are merged.",
            "The table prints 15 °C, while the detailed procedure and arrow state room temperature; both source statements are retained.",
            "X-ray diffraction/ORTEP confirms the authors' structural assignment of 2a, but the machine SMILES remains unverified.",
        ]
        unresolved = [
            "The source uses both 15 °C (Table 1) and room temperature (detailed procedure) for the same reported experiment.",
            "Reaction atmosphere is not stated for the optimized experiment.",
            "Candidate constitution and E geometry require independent structure review.",
        ]
    participants = [
        participant("substrate_1a", "reactant", "1a", evidence,
                    name="1,2-butadienyl phenyl sulfoxide", smiles=smiles_1["a"], amounts=substrate_amounts),
        participant("phsecl", "reagent", "PhSeCl", evidence,
                    name="phenylselenyl chloride", smiles="Cl[Se]c1ccccc1", amounts=reagent_amounts),
        *solvent_parts,
        participant("product_2a", "product", "E-2a", evidence,
                    name=names_2["a"], smiles=smiles_2["a"], amounts=product_amounts),
    ]
    outcomes = [
        fld("isolated_product_yield", {"number": yld, "unit": "%"}, evidence, ["product_2a"]),
        fld("yield_measurement_basis", "isolated", evidence, ["product_2a"]),
        fld("diastereomeric_ratio", dr, evidence, ["product_2a"]),
    ]
    notes = ["Table 1 optimization row for selenohydroxylation of 1a to E-2a.", *extra_notes]
    records.append(record(rid, "optimization_entry", evidence, participants,
                          [{"step_id": "selenohydroxylation", "participant_ids": [p["entity_id"] for p in participants], "conditions": step_conditions}],
                          outcomes, notes, unresolved))


# Exact preparation of the otherwise literature-derived starting material 1m.
evidence = [ev(2, "text"), ev(2, "image")]
participants = [
    participant("undec_3_yn_2_ol", "reactant", "undec-3-yn-2-ol", evidence,
                smiles="CC(O)C#CCCCCCCC", amounts=[
                    fld("mass", {"number": 6.72, "unit": "g"}, evidence),
                    fld("amount", {"number": 40, "unit": "mmol"}, evidence),
                ]),
    participant("phscl", "reactant", "PhSCl", evidence, name="phenylsulfenyl chloride",
                smiles="ClSc1ccccc1", amounts=[
                    fld("mass", {"number": 5.50, "unit": "g"}, evidence),
                    fld("amount", {"number": 38, "unit": "mmol"}, evidence),
                ]),
    participant("triethylamine", "reagent", "Et3N", evidence, name="triethylamine",
                smiles="CCN(CC)CC", amounts=[
                    fld("volume", {"number": 5.5, "unit": "mL"}, evidence),
                    fld("amount", {"number": 40, "unit": "mmol"}, evidence),
                ]),
    participant("methyl_iodide", "reagent", "MeI", evidence, name="methyl iodide",
                smiles="CI", amounts=[fld("volume", {"number": 0.5, "unit": "mL"}, evidence)]),
    participant("dcm", "solvent", "CH2Cl2", evidence, name="dichloromethane", smiles="ClCCl",
                amounts=[fld("volume", {"number": 150, "unit": "mL"}, evidence)]),
    participant("product_1m", "product", "1m", evidence, name="undeca-2,3-dien-4-yl phenyl sulfoxide",
                smiles=smiles_1["m"], amounts=[fld("mass", {"number": 7.82, "unit": "g"}, evidence)]),
]
steps = [
    {"step_id": "sulfenyl_chloride_addition", "participant_ids": ["undec_3_yn_2_ol", "phscl", "triethylamine", "dcm"], "conditions": [
        fld("temperature", {"number": -78, "unit": "°C"}, evidence),
        fld("operation", "Phenylsulfenyl chloride solution added dropwise to the cooled stirred mixture", evidence),
        fld("time", {"number": 8, "unit": "min"}, evidence),
    ]},
    {"step_id": "methyl_iodide_treatment_and_warmup", "participant_ids": ["methyl_iodide", "product_1m"], "conditions": [
        fld("operation", "Methyl iodide added, then mixture allowed to warm naturally to room temperature", evidence),
        fld("warm_to", "room temperature", evidence),
        fld("workup", "Quenched with 20 mL water; aqueous layer extracted with CH2Cl2 (2×20 mL); combined extracts washed with water and brine, dried over anhydrous Na2SO4, and evaporated", evidence),
        fld("purification", "Silica-gel chromatography, petroleum ether/ethyl acetate=20/1", evidence),
    ]},
]
records.append(record(
    "starting_material_1m_preparation", "reported_experiment", evidence, participants, steps,
    [fld("isolated_product_yield", {"number": 75, "unit": "%"}, evidence, ["product_1m"]),
     fld("yield_measurement_basis", "isolated", evidence, ["product_1m"])],
    ["The procedure is printed as a typical procedure citing reference 5, but this compound-specific preparation is executed and reported in the present paper."],
    ["Atmosphere and duration after methyl iodide addition are not reported.",
     "Candidate structures are machine-derived and unverified."],
))


# Table 2 entries 2-14. Entry 1 is already merged with Table 1 entry 11 above.
scope = {
    "b": (2, 3, 48.5, 0.30, 86.1, 0.45, 0.6, 6, 10, 48.3, 48, "table dash (—)"),
    "c": (3, 3, 38.4, 0.20, 58.2, 0.30, 0.4, 4, 15, 55.2, 76, "50/50"),
    "d": (4, 3, 61.7, 0.30, 87.0, 0.45, 0.6, 6, 19, 90.8, 80, "50/50"),
    "e": (5, 3, 65.5, 0.30, 86.8, 0.45, 0.6, 6, 60, 99.4, 85, "76/24"),
    "f": (6, 3, 52.6, 0.20, 57.9, 0.30, 0.4, 4, 18, 66.2, 76, "60/40"),
    "g": (7, 4, 72.7, 0.30, 86.4, 0.45, 0.6, 6, 18, 88.7, 71, "65/35"),
    "h": (8, 4, 75.9, 0.30, 85.7, 0.45, 0.6, 6, 12, 101.9, 80, "50/50"),
    "i": (9, 4, 45.0, 0.20, 58.1, 0.30, 0.4, 4, 15, 62.2, 77, "69/31"),
    "j": (10, 4, 44.8, 0.20, 58.3, 0.30, 0.4, 4, 11, 68.2, 85, "table dash (—)"),
    "k": (11, 4, 46.4, 0.20, 57.6, 0.30, 0.4, 4, 14, 72.2, 89, "table dash (—)"),
    "l": (12, 5, 83.4, 0.30, 87.2, 0.45, 0.6, 6, 11, 102.1, 75, "table dash (—)"),
    "m": (13, 5, 82.5, 0.30, 85.9, 0.45, 0.6, 6, 21, 125.5, 93, "50/50"),
    "n": (14, 5, 74.0, 0.30, 88.1, 0.45, 0.6, 6, 15, 64.1, 51, "table dash (—)"),
}

for letter, values in scope.items():
    entry, page, smass, samount, rmass, ramount, water_v, mecn_v, minutes, pmass, yld, dr = values
    pages = [2, page]
    if letter == "f":
        pages.append(4)
    if letter == "k":
        pages.append(5)
    evidence = []
    for p in pages:
        evidence.extend([ev(p, "text"), ev(p, "image")])
    evidence = list(dict.fromkeys(evidence))
    substrate_id = f"substrate_1{letter}"
    product_id = f"product_2{letter}"
    participants = [
        participant(substrate_id, "reactant", f"1{letter}", evidence, smiles=smiles_1[letter], amounts=[
            fld("mass", {"number": smass, "unit": "mg"}, evidence),
            fld("amount", {"number": samount, "unit": "mmol"}, evidence),
        ]),
        participant("phsecl", "reagent", "PhSeCl", evidence, name="phenylselenyl chloride", smiles="Cl[Se]c1ccccc1", amounts=[
            fld("mass", {"number": rmass, "unit": "mg"}, evidence),
            fld("amount", {"number": ramount, "unit": "mmol"}, evidence),
            fld("equivalents", {"number": 1.5, "unit": "equiv"}, evidence),
        ]),
        participant("water", "solvent", "H2O", evidence, name="water", smiles="O", amounts=[
            fld("volume", {"number": water_v, "unit": "mL"}, evidence)
        ]),
        participant("mecn", "solvent", "MeCN", evidence, name="acetonitrile", smiles="CC#N", amounts=[
            fld("volume", {"number": mecn_v, "unit": "mL"}, evidence)
        ]),
        participant(product_id, "product", f"E-2{letter}", evidence, name=names_2[letter], smiles=smiles_2[letter], amounts=[
            fld("mass", {"number": pmass, "unit": "mg"}, evidence)
        ]),
    ]
    outcomes = [
        fld("isolated_product_yield", {"number": yld, "unit": "%"}, evidence, [product_id]),
        fld("yield_measurement_basis", "isolated", evidence, [product_id]),
        fld("diastereomeric_ratio", dr, evidence, [product_id]),
    ]
    steps = [{
        "step_id": "selenohydroxylation",
        "participant_ids": [p["entity_id"] for p in participants],
        "conditions": [
            fld("solvent", "MeCN/H2O=10/1", evidence),
            fld("temperature", "room temperature", evidence),
            fld("time", {"number": minutes, "unit": "min"}, evidence),
        ],
    }]
    records.append(record(
        f"table2_entry{entry}_e2{letter}", "substrate_scope_entry", evidence,
        participants, steps, outcomes,
        [f"Table 2 entry {entry} merged with the compound-specific E-2{letter} experimental paragraph."],
        ["Atmosphere, workup, and purification are not restated for this abbreviated preparation.",
         "Candidate constitution and E geometry require independent structure review."],
    ))


coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1,
            "state": "attempted",
            "regions": [
                {"region": "title, abstract, introduction, and Results and Discussion prose", "finding": "High-level present-paper claims and narrative interpretation of Table 1/Table 2; no duplicate abstract-level experiment created.", "evidence_ids": [ev(1, "image"), ev(1, "text")]},
                {"region": "right-column Table 1 and reaction arrow", "finding": "Twelve independent optimization rows extracted; entry 1 nitrogen footnote applied only to that row.", "evidence_ids": [ev(1, "image"), ev(1, "text")]},
            ],
            "record_ids": [f"{DOC}:table1_entry{x}" for x in range(1, 11)] + [f"{DOC}:table1_entry11_table2_entry1_e2a", f"{DOC}:table1_entry12"],
            "unresolved": ["Most optimization rows omit absolute scale, workup, and purification.", "Machine-derived structures and stereochemistry remain unverified."],
        },
        {
            "page": 2,
            "state": "attempted",
            "regions": [
                {"region": "upper-left Figure 1 and Table 2", "finding": "ORTEP of 2a linked to the optimized experiment; all fourteen Table 2 scope rows inventoried, with entry 1 merged into Table 1 entry 11.", "evidence_ids": [ev(2, "image"), ev(2, "text")]},
                {"region": "upper-right section 4.1.1", "finding": "Exact preparation of starting material 1m extracted as a reported experiment.", "evidence_ids": [ev(2, "image"), ev(2, "text")]},
                {"region": "lower-right section 4.2.1", "finding": "Detailed E-2a procedure merged with Table 1 entry 11/Table 2 entry 1, including quantities, TLC, workup, purification, mass, yield, and dr.", "evidence_ids": [ev(2, "image"), ev(2, "text")]},
            ],
            "record_ids": [f"{DOC}:starting_material_1m_preparation", f"{DOC}:table1_entry11_table2_entry1_e2a"] + [f"{DOC}:table2_entry{x}_e2{chr(96+x)}" for x in range(2, 15)],
            "unresolved": ["The detailed E-2a procedure states room temperature while Table 1 prints 15 °C.", "No supporting-information source is associated."],
        },
        {
            "page": 3,
            "state": "attempted",
            "regions": [
                {"region": "sections 4.2.2-4.2.6 across both columns", "finding": "Compound-specific preparations E-2b through E-2f extracted and merged into their Table 2 rows; the 2f paragraph continues onto page 4.", "evidence_ids": [ev(3, "image"), ev(3, "text")]},
            ],
            "record_ids": [f"{DOC}:table2_entry{x}_e2{chr(96+x)}" for x in range(2, 7)],
            "unresolved": ["Abbreviated preparations do not restate atmosphere, workup, or purification."],
        },
        {
            "page": 4,
            "state": "attempted",
            "regions": [
                {"region": "top-left continuation of E-2f characterization", "finding": "Continuation linked to Table 2 entry 6; no additional reaction created.", "evidence_ids": [ev(4, "image"), ev(4, "text")]},
                {"region": "sections 4.2.7-4.2.11", "finding": "Compound-specific preparations E-2g through E-2k extracted and merged into Table 2 entries 7-11; E-2k characterization continues onto page 5.", "evidence_ids": [ev(4, "image"), ev(4, "text")]},
            ],
            "record_ids": [f"{DOC}:table2_entry{x}_e2{chr(96+x)}" for x in range(6, 12)],
            "unresolved": ["Abbreviated preparations do not restate atmosphere, workup, or purification."],
        },
        {
            "page": 5,
            "state": "attempted",
            "regions": [
                {"region": "top-left continuation of E-2k characterization", "finding": "Continuation linked to Table 2 entry 11; no duplicate reaction created.", "evidence_ids": [ev(5, "image"), ev(5, "text")]},
                {"region": "sections 4.2.12-4.2.14", "finding": "Compound-specific preparations E-2l, E-2m, and E-2n extracted and merged into Table 2 entries 12-14.", "evidence_ids": [ev(5, "image"), ev(5, "text")]},
                {"region": "acknowledgements and references", "finding": "No present-paper experiment; citations were not mined as associated sources.", "evidence_ids": [ev(5, "image"), ev(5, "text")]},
            ],
            "record_ids": [f"{DOC}:table2_entry{x}_e2{chr(96+x)}" for x in range(11, 15)],
            "unresolved": ["Abbreviated preparations do not restate atmosphere, workup, or purification."],
        },
        {
            "page": 6,
            "state": "attempted",
            "regions": [
                {"region": "crystal-data note 4", "finding": "Crystallographic characterization of 2a linked to the existing optimized experiment; not treated as a new reaction.", "evidence_ids": [ev(6, "image"), ev(6, "text")]},
                {"region": "reference 5 and remaining page", "finding": "Citation and journal whitespace only; no additional present-paper reaction.", "evidence_ids": [ev(6, "image"), ev(6, "text")]},
            ],
            "record_ids": [f"{DOC}:table1_entry11_table2_entry1_e2a"],
            "unresolved": ["The cited starting-material literature procedure is not supplied as an associated source.", "No CIF or supporting-information file is supplied or associated."],
        },
    ],
}

# Add page-6 characterization evidence to the existing 2a record.
for item in records:
    if item["record_id"].endswith("table1_entry11_table2_entry1_e2a"):
        item["evidence_ids"].extend([ev(6, "text"), ev(6, "image")])
        item["evidence_ids"] = list(dict.fromkeys(item["evidence_ids"]))
        item["notes"].append(fact("Page 6 reports crystal data for 2a (space group P2 and refinement data); this is characterization, not another experiment.", [ev(6, "text"), ev(6, "image")]))

OUT.mkdir(parents=True, exist_ok=True)
(OUT / "records_pages_0001_0006.json").write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
coverage_path = ROOT / "runs/current/coverage/pages_0001_0006.json"
coverage_path.parent.mkdir(parents=True, exist_ok=True)
coverage_path.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

tasks_path = ROOT / "runs/current/tasks.json"
tasks = json.loads(tasks_path.read_text())
for task in tasks:
    if task.get("document_id") == DOC and task.get("evidence_id") in {ev(p, "text") for p in range(1, 7)}:
        task["state"] = "attempted"
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"records": len(records), "coverage_pages": [p["page"] for p in coverage["pages"]]}, ensure_ascii=False))
