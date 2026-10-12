#!/usr/bin/env python3
"""Build evidence-linked machine records for PDF pages 1-4 of doc_7036fe92c245e3a6."""
import json
from pathlib import Path

DOC = "doc_7036fe92c245e3a6"
OUT = Path(__file__).with_name("records_pages_0001_0004.json")
E = {
    n: [f"{DOC}:page{n}:image", f"{DOC}:page{n}:text"]
    for n in range(1, 5)
}


def fact(value, evidence):
    return {
        "value": value,
        "evidence_ids": [] if value is None else list(evidence),
        "verification": "missing" if value is None else "unreviewed",
    }


def field(name, value, evidence, targets=None):
    result = {"name": name, "fact": fact(value, evidence)}
    if targets:
        result["target_entity_ids"] = list(targets)
    return result


def participant(entity_id, role, label, evidence, *, name=None, smiles=None, amounts=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence) if name is not None else fact(None, ()),
        "smiles": fact(smiles, evidence) if smiles is not None else fact(None, ()),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": amounts or [],
    }


def step(step_id, participant_ids, conditions):
    return {
        "step_id": step_id,
        "participant_ids": list(participant_ids),
        "conditions": conditions,
    }


def record(suffix, kind, evidence, participants=None, steps=None, outcomes=None, notes=None, unresolved=None):
    return {
        "record_id": f"{DOC}:{suffix}",
        "document_id": DOC,
        "source_reaction_id": suffix,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": list(dict.fromkeys(evidence)),
        "participants": participants or [],
        "steps": steps or [],
        "outcomes": outcomes or [],
        "notes": [fact(v, evidence) for v in (notes or [])],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved or [],
        },
    }


P = "P(=O)(OCC)OCC"
SMILES_2 = {
    "2a": f"C=C=C(CCCC){P}",
    "2b": f"C=C=C(C){P}",
    "2c": f"C=C=C(C(C)(C)C){P}",
    "2d": f"C=C=C(CCCCCCC){P}",
    "2e": f"C=C=C(c1ccccc1){P}",
    "2f": f"C=C=C(c1ccc(OC)cc1){P}",
    "2g": f"C=C=C(c1ccc(C)cc1){P}",
    "2h": f"C=C=C(c1ccc([N+](=O)[O-])cc1){P}",
    "2i": f"C=C=C(c1ccc(C(=O)OC)cc1){P}",
    "2j": f"C=C=C{P}",
}
SMILES_3 = {
    "3a": f"CC=C(CCCC){P}",
    "3b": f"CC=C(C){P}",
    "3c": f"CC=C(C(C)(C)C){P}",
    "3d": f"CC=C(CCCCCCC){P}",
    "3e": f"CC=C(c1ccccc1){P}",
    "3f": f"CC=C(c1ccc(OC)cc1){P}",
    "3g": f"CC=C(c1ccc(C)cc1){P}",
    "3h": f"CC=C(c1ccc([N+](=O)[O-])cc1){P}",
    "3i": f"CC=C(c1ccc(C(=O)OC)cc1){P}",
    "3j": f"CC=C{P}",
}
SOLVENTS = {
    "CH3CN": ("acetonitrile", "CC#N"),
    "THF": ("tetrahydrofuran", "C1CCOC1"),
    "diethyl ether": ("diethyl ether", "CCOCC"),
    "dioxane": ("dioxane", "O1CCOCC1"),
    "N,N-dimethylformamide": ("N,N-dimethylformamide", "CN(C)C=O"),
    "dimethyl sulfoxide": ("dimethyl sulfoxide", "CS(C)=O"),
    "CH2Cl2": ("dichloromethane", "ClCCl"),
    "CH3CCl3": ("1,1,1-trichloroethane", "CC(Cl)(Cl)Cl"),
    "toluene": ("toluene", "Cc1ccccc1"),
    "CH3NO2": ("nitromethane", "C[N+](=O)[O-]"),
    "CH3OH": ("methanol", "CO"),
    "AcOH": ("acetic acid", "CC(=O)O"),
    "Et3N": ("triethylamine", "CCN(CC)CC"),
}


def catalyst(label, evidence, loading=True, detailed=False):
    amounts = []
    if loading:
        amounts.append(field("catalyst_loading", {"number": 1, "unit": "mol%"}, evidence))
    if detailed:
        amounts.extend([
            field("mass", {"number": 1, "unit": "mg"}, evidence),
            field("amount", {"number": 0.002, "unit": "mmol"}, evidence),
        ])
    name = "Pd(Ar-BIAN)(alkene) complex " + label
    return participant(f"cat_{label}", "catalyst", label, evidence, name=name, amounts=amounts)


def hydrogen(evidence):
    return participant("hydrogen", "reagent", "H2", evidence, name="molecular hydrogen", smiles="[H][H]")


def solvent(label, evidence, *, volume=None, anhydrous=False):
    name, smiles = SOLVENTS[label]
    if anhydrous:
        name = "anhydrous " + name
    amounts = [] if volume is None else [field("volume", {"number": volume, "unit": "mL"}, evidence)]
    return participant("solvent", "solvent", label, evidence, name=name, smiles=smiles, amounts=amounts)


def substrate(label, evidence, *, amount=True, detailed=False, smiles=None):
    amounts = []
    if amount:
        amounts.append(field("amount", {"number": 0.2, "unit": "mmol"}, evidence))
    if detailed:
        amounts.insert(0, field("mass", {"number": 46, "unit": "mg"}, evidence))
    return participant("substrate", "reactant", label, evidence,
                       name=f"1,2-allenyl phosphonate {label}",
                       smiles=smiles or SMILES_2.get(label), amounts=amounts)


def product(label, evidence, *, smiles=None, mass=None):
    amounts = [] if mass is None else [field("mass", {"number": mass, "unit": "mg"}, evidence)]
    return participant("product", "product", label, evidence,
                       name=f"1-alkenyl phosphonate {label}", smiles=smiles, amounts=amounts)


records = []

# Page 1: conceptual reaction map only; it is not a reported experiment.
records.append(record(
    "scheme1_general_hydrogenation_map", "general_scheme", E[1],
    participants=[
        participant("generic_allene", "reactant", "R1R2C=C=CR3R4", E[1]),
        participant("generic_products", "product", "possible alkene/alkane product classes", E[1]),
    ],
    notes=["Scheme 1 enumerates conceptual 1,2-hydrogenation, 2,3-hydrogenation, and complete hydrogenation outcomes."],
    unresolved=["Generic R-group structures are not expanded to SMILES.", "Scheme 1 supplies no experiment-specific conditions or outcomes."],
))

# Page 2 prose: each listed solvent is an explicit failed solvent-screening condition.
failed_solvents = [
    "diethyl ether", "dioxane", "N,N-dimethylformamide", "dimethyl sulfoxide",
    "CH2Cl2", "CH3CCl3", "toluene", "CH3NO2", "CH3OH", "AcOH", "Et3N",
]
for idx, solv in enumerate(failed_solvents, 1):
    ps = [substrate("2a", E[2], amount=False), hydrogen(E[2]), solvent(solv, E[2])]
    records.append(record(
        f"solvent_screen_no_reaction_{idx:02d}", "optimization_entry", E[2],
        participants=ps,
        steps=[step("hydrogenation_attempt", [p["entity_id"] for p in ps], [
            field("solvent", solv, E[2]),
            field("temperature", {"number": 20, "unit": "°C"}, E[2]),
        ])],
        outcomes=[field("reaction_result", "no reaction", E[2])],
        unresolved=[
            "The prose does not state the catalyst identity, reaction time, solvent volume, substrate amount, or hydrogen pressure for this failed solvent example.",
            "No product was reported because the hydrogenation did not proceed.",
            "Candidate structures remain unverified; stereochemistry is not applicable to the no-reaction result.",
            "Supporting information was mentioned by the paper but was not supplied or explicitly associated in this dataset.",
        ],
    ))

# Table 1: five independent optimization rows. Entry 5 is enriched with the page 3 typical procedure.
table1 = [
    (1, "CH3CN", "1a", 20, 92),
    (2, "THF", "1a", 20, 94),
    (3, "THF", "1a", 30, 94),
    (4, "THF", "1a", 50, 92),
    (5, "THF", "1b", 20, 94),
]
for entry, solv, cat, temp, yld in table1:
    ev = E[2] + E[3] if entry == 5 else E[2]
    if entry == 5:
        ps = [
            substrate("2a", ev, detailed=True),
            catalyst("1b", ev, detailed=True),
            hydrogen(ev),
            solvent("THF", ev, volume=3, anhydrous=True),
            product("(Z)-3a", ev, smiles=SMILES_3["3a"], mass=44),
        ]
        steps = [
            step("charge", ["substrate", "cat_1b", "solvent"], [
                field("operation", "added to a Schlenk tube", E[3]),
                field("atmosphere", "N2", E[3]),
            ]),
            step("hydrogenation", ["substrate", "cat_1b", "hydrogen", "solvent"], [
                field("atmosphere", "N2 replaced with H2 (1 atm)", E[3]),
                field("temperature", {"number": 20, "unit": "°C"}, ev),
                field("time", {"number": 24, "unit": "h"}, ev),
                field("solvent", "THF", ev),
            ]),
            step("isolation", ["product"], [
                field("workup", "reaction mixture filtered; solvent evaporated", E[3]),
                field("purification", "flash chromatography on silica gel; petroleum ether/diethyl ether 1:2", E[3]),
            ]),
        ]
        basis = "isolated after flash chromatography"
        unresolved = [
            "Candidate SMILES encodes connectivity but not the reported Z stereochemistry and remains structure-unverified.",
            "Supporting information was mentioned by the paper but was not supplied or explicitly associated in this dataset.",
        ]
    else:
        ps = [
            substrate("2a", ev), catalyst(cat, ev), hydrogen(ev), solvent(solv, ev, volume=3),
            product("(Z)-3a", ev, smiles=SMILES_3["3a"]),
        ]
        steps = [step("hydrogenation", [p["entity_id"] for p in ps if p["role"] != "product"], [
            field("atmosphere", "H2 (1 atm)", ev),
            field("temperature", {"number": temp, "unit": "°C"}, ev),
            field("time", {"number": 24, "unit": "h"}, ev),
            field("solvent", solv, ev),
        ])]
        basis = None
        unresolved = [
            "The yield measurement basis is not stated for this Table 1 row.",
            "Workup and purification are not reported for this Table 1 row.",
            "Candidate SMILES encodes connectivity but not the reported Z stereochemistry and remains structure-unverified.",
            "Supporting information was mentioned by the paper but was not supplied or explicitly associated in this dataset.",
        ]
    records.append(record(
        f"table1_entry{entry}", "optimization_entry", ev,
        participants=ps, steps=steps,
        outcomes=[
            field("product_yield", {"number": yld, "unit": "%"}, ev, ["product"]),
            field("yield_measurement_basis", basis, E[3] if basis else ()),
            field("stereochemical_assignment", "Z", ev, ["product"]),
            field("selectivity_method", "chemo-, regio-, and stereoselectivities determined by 1H NMR analysis of the crude reaction product", E[2], ["product"]),
        ],
        unresolved=unresolved,
    ))

# Table 2: ten independent rows, including the explicitly failed entry 1.
table2 = [
    (1, "2b", "Me", None, None, "1a"),
    (2, "2b", "Me", "3b", 91, "1b"),
    (3, "2c", "tBu", "3c", 90, "1b"),
    (4, "2d", "n-C7H15", "3d", 94, "1b"),
    (5, "2e", "Ph", "3e", 95, "1b"),
    (6, "2f", "p-MeOC6H4", "3f", 99, "1b"),
    (7, "2g", "p-MeC6H4", "3g", 93, "1b"),
    (8, "2h", "p-NO2C6H4", "3h", 90, "1b"),
    (9, "2i", "p-MeO2CC6H4", "3i", 93, "1b"),
    (10, "2j", "H", "3j", 91, "1b"),
]
for entry, sub, rgroup, prod, yld, cat in table2:
    ps = [substrate(sub, E[2]), catalyst(cat, E[2]), hydrogen(E[2]), solvent("THF", E[2], volume=3)]
    if prod:
        ps.append(product(f"(Z)-{prod}", E[2], smiles=SMILES_3[prod]))
    conditions = [
        field("atmosphere", "H2 (1 atm)", E[2]),
        field("temperature", "room temperature", E[2]),
        field("time", {"number": 24, "unit": "h"}, E[2]),
        field("solvent", "THF", E[2]),
    ]
    if prod:
        outcomes = [
            field("product_yield", {"number": yld, "unit": "%"}, E[2], ["product"]),
            field("yield_measurement_basis", None, ()),
            field("stereochemical_assignment", "Z", E[2], ["product"]),
            field("selectivity_method", "chemo-, regio-, and stereoselectivities determined by 1H NMR analysis of the crude reaction product", E[2], ["product"]),
        ]
        unresolved = [
            "The yield measurement basis is not stated for this Table 2 row.",
            "Workup and purification are not reported for this Table 2 row.",
            "Candidate SMILES encodes connectivity but not the reported Z stereochemistry and remains structure-unverified.",
            "Supporting information was mentioned by the paper but was not supplied or explicitly associated in this dataset.",
        ]
    else:
        outcomes = [field("reaction_result", "no reaction", E[2])]
        unresolved = [
            "No product was reported because Table 2 entry 1 states no reaction.",
            "Workup and analytical detection limit are not reported.",
            "Candidate substrate connectivity remains structure-unverified.",
            "Supporting information was mentioned by the paper but was not supplied or explicitly associated in this dataset.",
        ]
    records.append(record(
        f"table2_entry{entry}", "substrate_scope_entry", E[2],
        participants=ps,
        steps=[step("hydrogenation", [p["entity_id"] for p in ps if p["role"] != "product"], conditions)],
        outcomes=outcomes,
        notes=[f"Table 2 identifies substituent R as {rgroup}."],
        unresolved=unresolved,
    ))

# Scheme 2: selective reduction of both the allene and the isolated allylic C=C bond in 2k.
ev = E[2]
ps = [
    participant("substrate", "reactant", "2k", ev, name="allyl-substituted 1,2-allenyl phosphonate 2k", smiles=f"C=CCC(=C=C){P}", amounts=[field("amount", {"number": 0.2, "unit": "mmol"}, ev)]),
    catalyst("1b", ev), hydrogen(ev), solvent("THF", ev, volume=3),
    product("(Z)-3k", ev, smiles=f"CCCC(=CC){P}"),
]
records.append(record(
    "scheme2_2k_to_3k", "substrate_scope_entry", ev, participants=ps,
    steps=[step("hydrogenation", [p["entity_id"] for p in ps if p["role"] != "product"], [
        field("atmosphere", "H2 (1 atm)", ev), field("temperature", "room temperature", ev),
        field("time", {"number": 24, "unit": "h"}, ev), field("solvent", "THF", ev),
    ])],
    outcomes=[
        field("product_yield", {"number": 93, "unit": "%"}, ev, ["product"]),
        field("yield_measurement_basis", None, ()),
        field("stereochemical_assignment", "Z", ev, ["product"]),
    ],
    notes=["The isolated allylic C=C bond was also hydrogenated, while the conjugated electron-deficient C=C bond remained; (Z)-3k was reported as the only product."],
    unresolved=[
        "The yield measurement basis, workup, and purification are not reported.",
        "Candidate SMILES connectivity and unencoded Z stereochemistry remain structure-unverified.",
        "Supporting information was mentioned by the paper but was not supplied or explicitly associated in this dataset.",
    ],
))

# Scheme 3: three separate substrate-scope arrows under the Table 2 conditions.
scheme3 = [
    ("2l", "3l", "R8=nPr, R9=H", f"CCCC=C=C(CCCC){P}", f"CCCCC=C(CCCC){P}", 92),
    ("2m", "3m", "R8=Me, R9=Me", f"CC(=C=C(CCCC){P})C", f"CC(C)C=C(CCCC){P}", 95),
    ("2n", "3n", "R8=Me, R9=Et", f"CCC(=C=C(CCCC){P})C", f"CCC(C)C=C(CCCC){P}", 85),
]
for sub, prod, substitution, s_smiles, p_smiles, yld in scheme3:
    ps = [
        participant("substrate", "reactant", sub, E[2], name=f"substituted 1,2-allenyl phosphonate {sub}", smiles=s_smiles, amounts=[field("amount", {"number": 0.2, "unit": "mmol"}, E[2])]),
        catalyst("1b", E[2]), hydrogen(E[2]), solvent("THF", E[2], volume=3),
        product(f"(Z)-{prod}", E[2], smiles=p_smiles),
    ]
    records.append(record(
        f"scheme3_{sub}_to_{prod}", "substrate_scope_entry", E[2], participants=ps,
        steps=[step("hydrogenation", [p["entity_id"] for p in ps if p["role"] != "product"], [
            field("atmosphere", "H2 (1 atm)", E[2]), field("temperature", "room temperature", E[2]),
            field("time", {"number": 24, "unit": "h"}, E[2]), field("solvent", "THF", E[2]),
        ])],
        outcomes=[
            field("product_yield", {"number": yld, "unit": "%"}, E[2], ["product"]),
            field("yield_measurement_basis", None, ()),
            field("stereochemical_assignment", "Z", E[2], ["product"]),
        ],
        notes=[f"Scheme 3 specifies {sub}: {substitution}."],
        unresolved=[
            "The yield measurement basis, workup, and purification are not reported.",
            "Candidate SMILES connectivity and unencoded Z stereochemistry remain structure-unverified.",
            "Supporting information was mentioned by the paper but was not supplied or explicitly associated in this dataset.",
        ],
    ))

# Page 3 Scheme 4 is a proposed mechanism, not an experimental transformation.
records.append(record(
    "scheme4_proposed_mechanism", "mechanism", E[3],
    notes=["Scheme 4 proposes ligand loss, allene coordination, heterolytic H2 cleavage, stereoselective hydropalladation, and reductive elimination through intermediates 5-8 and 7a/7b."],
    unresolved=["The depicted catalytic intermediates are mechanistic proposals and are not treated as isolated experimental products."],
))

# Page 3 Scheme 5: three distinct related-substrate experiments.
ev = E[3]
scheme5_specs = [
    {
        "suffix": "scheme5_9_to_10", "sub": "9", "prod_labels": ["10"],
        "sub_name": "1,2-allenyl phosphine oxide 9", "sub_smiles": "C=C=C(CCCC)P(=O)(c1ccccc1)c1ccccc1",
        "prod_smiles": ["CC=C(CCCC)P(=O)(c1ccccc1)c1ccccc1"],
        "solvent": "THF", "yield": 68, "ratio": None,
    },
    {
        "suffix": "scheme5_11_to_12", "sub": "11", "prod_labels": ["(Z)-12", "(E)-12"],
        "sub_name": "1,2-allenyl sulfone 11", "sub_smiles": "C=C=CS(=O)(=O)c1ccccc1",
        "prod_smiles": ["CC=CS(=O)(=O)c1ccccc1", "CC=CS(=O)(=O)c1ccccc1"],
        "solvent": "THF", "yield": 77, "ratio": "Z:E = 94:6",
    },
    {
        "suffix": "scheme5_13_to_14", "sub": "13", "prod_labels": ["(Z)-14", "(E)-14"],
        "sub_name": "2,3-allenoate 13", "sub_smiles": "C=C=C(Cc1ccccc1)C(=O)OCC",
        "prod_smiles": ["CC=C(Cc1ccccc1)C(=O)OCC", "CC=C(Cc1ccccc1)C(=O)OCC"],
        "solvent": "toluene", "yield": 80, "ratio": "Z:E = 94:6",
    },
]
for spec in scheme5_specs:
    ps = [
        participant("substrate", "reactant", spec["sub"], ev, name=spec["sub_name"], smiles=spec["sub_smiles"]),
        catalyst("1b", ev), hydrogen(ev), solvent(spec["solvent"], ev),
    ]
    target_ids = []
    for i, (label, smiles) in enumerate(zip(spec["prod_labels"], spec["prod_smiles"]), 1):
        entity_id = "product" if len(spec["prod_labels"]) == 1 else f"product_{i}"
        target_ids.append(entity_id)
        ps.append(participant(entity_id, "product", label, ev, name=f"semihydrogenation product {label}", smiles=smiles))
    outcomes = [
        field("combined_product_yield" if len(target_ids) > 1 else "product_yield",
              {"number": spec["yield"], "unit": "%"}, ev, target_ids),
        field("yield_measurement_basis", None, ()),
    ]
    if spec["ratio"]:
        outcomes.append(field("product_ratio", spec["ratio"], ev, target_ids))
    records.append(record(
        spec["suffix"], "substrate_scope_entry", ev, participants=ps,
        steps=[step("hydrogenation", [p["entity_id"] for p in ps if p["role"] != "product"], [
            field("atmosphere", "H2 (1 atm)", ev), field("temperature", "room temperature", ev),
            field("time", {"number": 24, "unit": "h"}, ev), field("solvent", spec["solvent"], ev),
        ])],
        outcomes=outcomes,
        unresolved=[
            "The reaction scale, solvent volume, yield measurement basis, workup, and purification are not reported in the main text.",
            "Candidate connectivity remains structure-unverified; product E/Z stereochemistry is preserved in labels/ratio but not encoded in SMILES.",
            "Supporting information was mentioned by the paper but was not supplied or explicitly associated in this dataset.",
        ],
    ))

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
print(f"wrote {len(records)} records to {OUT}")
