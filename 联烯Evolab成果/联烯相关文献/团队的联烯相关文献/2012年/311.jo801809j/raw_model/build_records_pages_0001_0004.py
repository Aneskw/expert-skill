#!/usr/bin/env python3
"""Build evidence-linked machine records for jo801809j PDF pages 1--4."""

import json
from pathlib import Path


DOC = "doc_ac48d7dda59da009"
ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "runs/current/raw_model/records_pages_0001_0004.json"
COVERAGE = ROOT / "runs/current/coverage/pages_0001_0004.json"
TASKS = ROOT / "runs/current/tasks.json"


def evidence(*pages):
    result = []
    for page in pages:
        result.extend([f"{DOC}:page{page}:text", f"{DOC}:page{page}:image"])
    return result


def fact(value, ev=()):
    return {
        "value": value,
        "evidence_ids": list(ev) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def field(name, value, ev=(), targets=None):
    item = {"name": name, "fact": fact(value, ev)}
    if targets:
        item["target_entity_ids"] = list(targets)
    return item


def q(number, unit, **extra):
    value = {"number": number, "unit": unit}
    value.update(extra)
    return value


def participant(entity_id, role, label, ev, name=None, smiles=None, amounts=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, ev),
        "name": fact(name, ev) if name is not None else fact(None),
        "smiles": fact(smiles, ev) if smiles is not None else fact(None),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": amounts or [],
    }


def step(step_id, participant_ids, conditions):
    return {"step_id": step_id, "participant_ids": participant_ids, "conditions": conditions}


def record(rid, kind, pages, participants=None, steps=None, outcomes=None, notes=None, unresolved=None):
    ev = evidence(*pages)
    return {
        "record_id": f"{DOC}:{rid}",
        "document_id": DOC,
        "source_reaction_id": rid,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": ev,
        "participants": participants or [],
        "steps": steps or [],
        "outcomes": outcomes or [],
        "notes": [fact(text, ev) for text in (notes or [])],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved or [],
        },
    }


SUBSTRATE_SMILES = {
    "1a": "CCOC(=O)C(CCC)=C=Cc1ccccc1",
    "1b": "CCOC(=O)C(CCC)=C=Cc1ccc(Br)cc1",
    "1c": "CCOC(=O)C(C)=C=Cc1ccccc1",
    "1d": "CCOC(=O)C(C)=C=Cc1ccc(Cl)cc1",
    "1e": "CCOC(=O)C(C)=C=Cc1ccc(F)cc1",
    "1f": "CCOC(=O)C(C)=C=Cc1ccc(OC)cc1",
    "1g": "CCOC(=O)C(CC)=C=Cc1ccccc1",
    "1h": "CCOC(=O)C(C)=C=CCCCC",
    "1i": "CCOC(=O)C(Cc1ccccc1)=C=CCCCC",
    "1j": "CCOC(=O)C=C=C(c1ccccc1)c1ccccc1",
    "1k": "CCOC(=O)C=C=CCCCCCCC",
    "1l": "CCOC(=O)C(C)=C=C(C)c1ccccc1",
    "1m": "CCOC(=O)C(C)=C=C(CC)c1ccccc1",
    "1n": "CCOC(=O)C(C)=C=C(c1ccccc1)c1ccccc1",
    "1o": "CCOC(=O)C(C)=C=C(CC)CC",
    "1p": "CCOC(=O)C(C)=C=C1CCCCC1",
    "1q": "CCOC(=O)C(C)=C=C",
    "1r": "COC(=O)C=C=C",
}

PRODUCT_SMILES = {
    "2a": "C=CCC(O)(CC=C)C(CCC)=C=Cc1ccccc1",
    "2b": "C=CCC(O)(CC=C)C(CCC)=C=Cc1ccc(Br)cc1",
    "2c": "C=CCC(O)(CC=C)C(C)=C=Cc1ccccc1",
    "2d": "C=CCC(O)(CC=C)C(C)=C=Cc1ccc(Cl)cc1",
    "2e": "C=CCC(O)(CC=C)C(C)=C=Cc1ccc(F)cc1",
    "2f": "C=CCC(O)(CC=C)C(C)=C=Cc1ccc(OC)cc1",
    "2g": "C=CCC(O)(CC=C)C(CC)=C=Cc1ccccc1",
    "2h": "C=CCC(O)(CC=C)C(C)=C=CCCCC",
    "2i": "C=CCC(O)(CC=C)C(Cc1ccccc1)=C=CCCCC",
    "2j": "C=CCC(O)(CC=C)C=C=C(c1ccccc1)c1ccccc1",
    "2k": "C=CCC(O)(CC=C)C=C=CCCCCCCC",
    "2l": "C=CCC(O)(CC=C)C(C)=C=C(C)c1ccccc1",
    "2m": "C=CCC(O)(CC=C)C(C)=C=C(CC)c1ccccc1",
    "2n": "C=CCC(O)(CC=C)C(C)=C=C(c1ccccc1)c1ccccc1",
    "2o": "C=CCC(O)(CC=C)C(C)=C=C(CC)CC",
    "2p": "C=CCC(O)(CC=C)C(C)=C=C1CCCCC1",
    "2q": "C=CCC(O)(CC=C)C(C)=C=C",
    "2r": "C=CCC(O)(CC=C)C=C=C",
    "2s": "C=C(C)CC(O)(CC(C)=C)C(Cc1ccccc1)=C=CCCCC",
}

SUBSTRATE_NAMES = {
    "1a": "ethyl 4-phenyl-2-(n-propyl)-2,3-butadienoate",
    "1b": "ethyl 4-(p-bromophenyl)-2-propyl-2,3-butadienoate",
    "1c": "ethyl 2-methyl-4-phenyl-2,3-butadienoate",
    "1i": "ethyl 2-benzylocta-2,3-dienoate",
    "1r": "methyl 2,3-butadienoate",
}

PRODUCT_NAMES = {
    "2a": "4-allyl-1-phenyl-3-(n-propyl)-1,2,6-heptatrien-4-ol",
    "2b": "double 1,2-addition allenol 2b",
    "2c": "double 1,2-addition allenol 2c",
    "2i": "4-allyl-5-benzyl-1,5,6-undecatrien-4-ol",
    "2s": "double 1,2-addition allenol 2s",
}


def substrate(label, ev, amounts=None, entity_id=None, display_label=None):
    return participant(
        entity_id or f"substrate_{label}", "reactant", display_label or label, ev,
        SUBSTRATE_NAMES.get(label), SUBSTRATE_SMILES.get(label), amounts,
    )


def product(label, ev, amounts=None, entity_id=None, display_label=None, name=None, smiles=None):
    return participant(
        entity_id or f"product_{label}", "product", display_label or label, ev,
        name if name is not None else PRODUCT_NAMES.get(label),
        smiles if smiles is not None else PRODUCT_SMILES.get(label), amounts,
    )


def allyl_mg(ev, equiv=None, concentration=None, volume=None, amount=None, entity_id="reagent_allyl_mgcl"):
    amounts = []
    if equiv is not None:
        amounts.append(field("equivalents", q(equiv, "equiv"), ev))
    if concentration is not None:
        amounts.append(field("concentration", q(concentration, "M"), ev))
    if volume is not None:
        amounts.append(field("volume", q(volume, "mL"), ev))
    if amount is not None:
        amounts.append(field("amount", q(amount, "mmol"), ev))
    return participant(entity_id, "reagent", "allyl magnesium chloride", ev,
                       "allylmagnesium chloride", None, amounts)


def solvent(entity_id, label, name, smiles, ev, volume=None):
    amounts = [field("volume", q(volume, "mL"), ev)] if volume is not None else []
    return participant(entity_id, "solvent", label, ev, name, smiles, amounts)


records = []

# Page 1 graphical abstract: an article-level reaction summary, not an individual batch.
ev1 = evidence(1)
abstract_parts = [
    participant("generic_allenoate", "reactant", "generic 2,3-allenoate", ev1),
    allyl_mg(ev1, equiv=3),
    solvent("solvent_thf", "THF", "tetrahydrofuran", "C1CCOC1", ev1),
    participant("generic_alpha_allenol", "product", "generic tertiary alpha-allenol", ev1),
]
records.append(record(
    "graphical_abstract_general_double_addition", "general_scheme", [1],
    participants=abstract_parts,
    steps=[step("general_double_1_2_addition", [p["entity_id"] for p in abstract_parts[:-1]], [
        field("temperature", "r.t.", ev1),
        field("time", {"minimum": 2, "maximum": 35, "unit": "min", "raw_text": "2–35 min"}, ev1),
    ])],
    outcomes=[field("reported_yield_range", {"minimum": 60, "maximum": 100, "unit": "%", "raw_text": "60–100%"}, ev1,
                    ["generic_alpha_allenol"])],
    notes=["The graphical abstract is a generic summary with R-group placeholders, not a uniquely specified experiment."],
    unresolved=["Generic R-group structures cannot be converted into unique molecules; scale and yield basis are not stated in the graphic."],
))

# Page 1 Scheme 1: conceptual possible pathways, classified separately from experiments.
scheme1_parts = [
    participant("generic_2_3_allenoate", "reactant", "generic 2,3-allenoate", ev1),
    participant("generic_organometallic", "reagent", "R4M", ev1),
    participant("generic_1_2_addition_product", "product", "possible 1,2-addition product", ev1),
    participant("generic_1_4_addition_product", "product", "possible 1,4-addition product", ev1),
    participant("generic_migration_product", "product", "possible double-bond-migration product", ev1),
]
records.append(record(
    "scheme1_possible_organometallic_pathways", "general_scheme", [1],
    participants=scheme1_parts,
    steps=[step("conceptual_pathways", ["generic_2_3_allenoate", "generic_organometallic"], [])],
    outcomes=[
        field("possible_1_2_addition_pathway", "depicted", ev1, ["generic_1_2_addition_product"]),
        field("possible_1_4_addition_pathway", "depicted", ev1, ["generic_1_4_addition_product"]),
        field("possible_double_bond_migration_pathway", "depicted", ev1, ["generic_migration_product"]),
    ],
    notes=["Scheme 1 presents possible generic outcomes and is not a reported experimental batch."],
    unresolved=["R1–R4 and M are generic placeholders; no conditions or outcomes are assigned."],
))

# Equation 1: Fe-catalyzed trial with 1a.
eq1_parts = [
    substrate("1a", ev1),
    allyl_mg(ev1, equiv=3, concentration=1.7),
    participant("catalyst_fe_acac3", "catalyst", "Fe(acac)3", ev1, "iron(III) acetylacetonate", None,
                [field("catalyst_loading", q(5, "mol%"), ev1)]),
    solvent("solvent_toluene", "toluene", "toluene", "Cc1ccccc1", ev1),
    product("2a", ev1),
]
records.append(record(
    "eq1_fe_catalyzed_1a_to_2a", "reported_experiment", [1], participants=eq1_parts,
    steps=[step("double_1_2_addition", [p["entity_id"] for p in eq1_parts[:-1]], [
        field("temperature", q(-78, "°C"), ev1), field("time", q(1.5, "h"), ev1),
        field("solvent", "toluene", ev1),
    ])],
    outcomes=[
        field("isolated_yield_2a", q(85, "%"), ev1, ["product_2a"]),
        field("yield_measurement_basis", "isolated yield", ev1, ["product_2a"]),
        field("1_4_addition_product_observation", "not observed", ev1),
    ],
    unresolved=["Reaction scale, solvent volume, atmosphere, workup, and purification are not stated."],
))

# Table 1: four distinct optimization rows for 1b.
table1 = [
    (1, "toluene", -78, 51, 86),
    (2, "toluene", "r.t.", 52, 90),
    (3, "THF", "r.t.", 33, 91),
    (4, "Et2O", "r.t.", 26, 89),
]
solvent_data = {
    "toluene": ("toluene", "Cc1ccccc1"),
    "THF": ("tetrahydrofuran", "C1CCOC1"),
    "Et2O": ("diethyl ether", "CCOCC"),
}
for entry, solv_label, temp, minutes, yld in table1:
    pages = [1, 2] if entry in (1, 3) else [2]
    ev = evidence(*pages)
    sub_amounts = [field("amount", q(0.4, "mmol"), ev)] if entry == 3 else []
    solvent_volume = 5 if entry == 3 else None
    parts = [
        substrate("1b", ev, sub_amounts), allyl_mg(ev, equiv=3, concentration=1.7),
        solvent(f"solvent_{solv_label.lower()}", solv_label, *solvent_data[solv_label], ev, solvent_volume),
        product("2b", ev),
    ]
    notes = ["Table 1 reports NMR yield of 2b."]
    if entry == 1:
        notes.append("Page 1 states that this reaction was conducted in the absence of the iron catalyst.")
    if entry == 3:
        notes.append("Page 1 defines entry 3 as the standard 0.4 mmol, THF (5 mL), room-temperature experiment.")
    records.append(record(
        f"table1_entry{entry}", "optimization_entry", pages, participants=parts,
        steps=[step("double_1_2_addition", [p["entity_id"] for p in parts[:-1]], [
            field("temperature", q(temp, "°C") if isinstance(temp, (int, float)) else temp, ev),
            field("time", q(minutes, "min"), ev), field("solvent", solv_label, ev),
        ])],
        outcomes=[field("NMR_yield_2b", q(yld, "%"), ev, ["product_2b"]),
                  field("yield_measurement_basis", "NMR yield", ev, ["product_2b"])],
        notes=notes,
        unresolved=["Atmosphere, workup, purification, and NMR standard are not stated."
                    + (" Reaction scale and solvent volume are also missing." if entry != 3 else "")],
    ))

# Table 2: nineteen row-level substrate-scope records. Entry 10 footnote overrides the 0.4 mmol header.
table2 = [
    (1, "1a", "Ph", "H", "n-Pr", 3, 94, "2a"),
    (2, "1b", "p-BrC6H4", "H", "n-Pr", 33, 95, "2b"),
    (3, "1c", "Ph", "H", "Me", 20, 85, "2c"),
    (4, "1d", "p-ClC6H4", "H", "Me", 4, 90, "2d"),
    (5, "1e", "p-FC6H4", "H", "Me", 19, 88, "2e"),
    (6, "1f", "p-MeOC6H4", "H", "Me", 3, 79, "2f"),
    (7, "1g", "Ph", "H", "Et", 4, 94, "2g"),
    (8, "1h", "n-C4H9", "H", "Me", 4, 86, "2h"),
    (9, "1i", "n-C4H9", "H", "Bn", 8, 100, "2i"),
    (10, "1i", "n-C4H9", "H", "Bn", 4, 97, "2i"),
    (11, "1j", "Ph", "Ph", "H", 3, 83, "2j"),
    (12, "1k", "n-C7H15", "H", "H", 6, 97, "2k"),
    (13, "1l", "Ph", "Me", "Me", 33, 97, "2l"),
    (14, "1m", "Ph", "Et", "Me", 3, 91, "2m"),
    (15, "1n", "Ph", "Ph", "Me", 2, 90, "2n"),
    (16, "1o", "Et", "Et", "Me", 35, 60, "2o"),
    (17, "1p", "(CH2)5", "", "Me", 3, 94, "2p"),
    (18, "1q", "H", "H", "Me", 2, 63, "2q"),
    (19, "1r", "H", "H", "H", 20, 64, "2r"),
]
for entry, sub, r1, r2, r3, minutes, yld, prod in table2:
    pages = [2, 3] if entry == 1 else [2]
    ev = evidence(*pages)
    scale = 2 if entry == 10 else 0.4
    sub_amounts = [field("amount", q(scale, "mmol"), ev)]
    allyl = allyl_mg(ev, equiv=3, concentration=1.7)
    thf = solvent("solvent_thf", "THF", "tetrahydrofuran", "C1CCOC1", ev, 5)
    parts = [substrate(sub, ev, sub_amounts), allyl, thf, product(prod, ev)]
    conditions = [field("temperature", "r.t.", ev), field("time", q(minutes, "min"), ev),
                  field("solvent", "THF", ev)]
    notes = [f"Table 2 substituents: R1={r1}, R2={r2 or '(joined to R1)'}, R3={r3}."]
    unresolved = ["Atmosphere, workup, and purification are not reported for this table row; candidate structures remain unverified."]
    if entry == 10:
        notes.append("Table 2 footnote a explicitly changes the allenoate scale to 2 mmol.")
    if entry == 19:
        notes.append("Table 2 footnote b identifies 1r as methyl 2,3-butadienoate.")
    if entry == 1:
        # Merge the detailed page-3 batch into the same experiment rather than duplicating it.
        parts = [
            substrate("1a", ev, [field("mass", q(92.5, "mg"), ev), field("amount", q(0.4, "mmol"), ev)]),
            allyl_mg(ev, equiv=3, concentration=1.7, volume=0.7, amount=1.2),
            thf,
            participant("workup_nh4cl", "reagent", "saturated NH4Cl", ev, "ammonium chloride", "[Cl-].[NH4+]",
                        [field("volume", q(1, "mL"), ev)]),
            solvent("extraction_ether", "ether", "diethyl ether", "CCOCC", ev, 60),
            participant("wash_hcl", "reagent", "1% aqueous HCl", ev, "hydrochloric acid", "Cl"),
            participant("wash_nahco3", "reagent", "saturated aqueous NaHCO3", ev, "sodium bicarbonate", "O=C([O-])O.[Na+]"),
            participant("wash_brine", "reagent", "brine", ev),
            participant("drying_na2so4", "reagent", "anhydrous Na2SO4", ev, "sodium sulfate", "[Na+].[Na+].[O-]S(=O)(=O)[O-]"),
            product("2a", ev),
        ]
        conditions.extend([
            field("atmosphere", "nitrogen", ev),
            field("workup", "slow quench with saturated NH4Cl; ether extraction; sequential 1% HCl, saturated NaHCO3, and brine washes; drying over anhydrous Na2SO4", ev),
            field("purification", "silica gel column chromatography, petroleum ether/ethyl acetate = 100/1", ev),
        ])
        notes.append("The page-3 detailed 2a procedure is the same 0.4 mmol, 3 min, 94% batch as Table 2 entry 1.")
        unresolved = ["Candidate structures and the interpretation of the drawn allene connectivity remain machine-unverified."]
    outcomes = [
        field("isolated_yield_2", q(yld, "%"), ev, [f"product_{prod}"]),
        field("yield_measurement_basis", "isolated yield", ev, [f"product_{prod}"]),
    ]
    if entry == 1:
        outcomes.append(field("isolated_product_mass", q(101.8, "mg"), ev, ["product_2a"]))
    records.append(record(
        f"table2_entry{entry}", "substrate_scope_entry", pages, participants=parts,
        steps=[step("double_1_2_addition", [p["entity_id"] for p in parts if p["role"] != "product"], conditions)],
        outcomes=outcomes, notes=notes, unresolved=unresolved,
    ))

# Equation 2: double addition at both ester termini.
ev2 = evidence(2)
eq2_parts = [
    participant("substrate_3", "reactant", "3", ev2,
                "diethyl 2,9-dimethyl-2,3,7,8-decatetraenedioate",
                "CCOC(=O)C(C)=C=CCCC=C=C(C)C(=O)OCC"),
    allyl_mg(ev2, equiv=6, concentration=1.7),
    solvent("solvent_thf", "THF", "tetrahydrofuran", "C1CCOC1", ev2),
    participant("product_4", "product", "4", ev2, "tetraallyl-substituted bis-allenol 4",
                "C=CCC(O)(CC=C)C(C)=C=CCCC=C=C(C)C(O)(CC=C)CC=C"),
]
records.append(record(
    "eq2_bis_allenoate_3_to_4", "reported_experiment", [2], participants=eq2_parts,
    steps=[step("double_addition_at_two_esters", [p["entity_id"] for p in eq2_parts[:-1]], [
        field("temperature", "r.t.", ev2), field("time", q(19, "min"), ev2), field("solvent", "THF", ev2),
    ])],
    outcomes=[field("reported_yield_4", q(82, "%"), ev2, ["product_4"]),
              field("diastereomeric_ratio", "dr ≈ 1:1", ev2, ["product_4"]),
              field("yield_measurement_basis", None, targets=["product_4"])],
    unresolved=["Scale, solvent volume, atmosphere, workup, purification, and yield basis are not stated; candidate structures remain unverified."],
))

# Equation 3: axial-chirality retention experiment.
eq3_parts = [
    substrate("1c", ev2, [field("starting_material_ee", q(98, "%"), ev2)], display_label="(R)-(−)-1c"),
    allyl_mg(ev2, equiv=3, concentration=1.7),
    solvent("solvent_thf", "THF", "tetrahydrofuran", "C1CCOC1", ev2),
    product("2c", ev2, display_label="(R)-(−)-2c"),
]
records.append(record(
    "eq3_optically_active_1c_to_2c", "reported_experiment", [2], participants=eq3_parts,
    steps=[step("enantiospecific_double_1_2_addition", [p["entity_id"] for p in eq3_parts[:-1]], [
        field("temperature", "r.t.", ev2), field("time", q(2, "min"), ev2), field("solvent", "THF", ev2),
    ])],
    outcomes=[field("isolated_yield_2c", q(90, "%"), ev2, ["product_2c"]),
              field("yield_measurement_basis", "isolated yield", ev2, ["product_2c"]),
              field("product_ee", q(97, "%"), ev2, ["product_2c"])],
    notes=["The paper reports no obvious racemization of axial chirality; stereochemical labels and ee values are retained verbatim."],
    unresolved=["Scale, solvent volume, atmosphere, workup, and purification are not stated; axial stereochemistry is not encoded in the candidate SMILES."],
))

# Equation 4: 2-methylallyl magnesium chloride example.
eq4_parts = [
    substrate("1i", ev2),
    participant("reagent_2_methylallyl_mgcl", "reagent", "2-methylallyl magnesium chloride", ev2,
                "2-methylallylmagnesium chloride", None,
                [field("equivalents", q(3, "equiv"), ev2), field("concentration", q(0.4, "M"), ev2)]),
    solvent("solvent_thf", "THF", "tetrahydrofuran", "C1CCOC1", ev2),
    product("2s", ev2),
]
records.append(record(
    "eq4_2_methylallyl_addition_1i_to_2s", "reported_experiment", [2], participants=eq4_parts,
    steps=[step("double_1_2_addition", [p["entity_id"] for p in eq4_parts[:-1]], [
        field("temperature", "r.t.", ev2), field("time", q(35, "min"), ev2), field("solvent", "THF", ev2),
    ])],
    outcomes=[field("reported_yield_2s", q(98, "%"), ev2, ["product_2s"]),
              field("yield_measurement_basis", None, targets=["product_2s"])],
    unresolved=["Scale, solvent volume, atmosphere, workup, purification, and yield basis are not stated; the complex product candidate is unverified."],
))

# Explicitly reported complicated or diverted reactions; each reagent is a distinct experiment.
ev23 = evidence(2, 3)
complex_reagents = [
    ("1_buten_3_yl", "1-buten-3-yl magnesium chloride", 0.5, "THF", None),
    ("2_butenyl", "2-butenyl magnesium chloride", 0.5, "THF", None),
    ("3_phenyl_2_propenyl", "3-phenyl-2-propenyl magnesium chloride", 0.4, "Et2O", None),
]
for tag, label, concentration, solution_solvent, smiles in complex_reagents:
    parts = [
        substrate("1i", ev23),
        participant(f"reagent_{tag}_mgcl", "reagent", label, ev23, label, smiles,
                    [field("solution_concentration", q(concentration, "M"), ev23)]),
        solvent(f"solution_solvent_{solution_solvent.lower()}", solution_solvent,
                "tetrahydrofuran" if solution_solvent == "THF" else "diethyl ether",
                "C1CCOC1" if solution_solvent == "THF" else "CCOCC", ev23),
        participant("product_complicated_mixture", "product", "complicated mixture", ev23),
    ]
    records.append(record(
        f"negative_1i_with_{tag}_mgcl", "reported_experiment", [2, 3], participants=parts,
        steps=[step("addition_attempt", [p["entity_id"] for p in parts[:-1]], [
            field("temperature", None), field("time", None),
        ])],
        outcomes=[field("reaction_outcome", "complicated mixture", ev23, ["product_complicated_mixture"])],
        notes=["The authors attribute the complicated mixture probably to regioselectivity issues; reagent solution concentration/solvent comes from the Materials section."],
        unresolved=["Reagent amount, reaction scale, temperature, time, workup, purification, and product identities are not stated."],
    ))

# Vinyl reagent under the stated standard conditions.
vinyl_parts = [
    substrate("1i", ev2, [field("amount", q(0.4, "mmol"), ev2)]),
    participant("reagent_vinyl_mgcl", "reagent", "vinyl magnesium chloride", ev2, "vinylmagnesium chloride", None,
                [field("equivalents", q(3, "equiv"), ev2)]),
    solvent("solvent_thf", "THF", "tetrahydrofuran", "C1CCOC1", ev2, 5),
    participant("product_complicated_mixture", "product", "complicated mixture", ev2),
]
records.append(record(
    "negative_1i_with_vinyl_mgcl", "reported_experiment", [2], participants=vinyl_parts,
    steps=[step("addition_attempt_under_standard_conditions", [p["entity_id"] for p in vinyl_parts[:-1]], [
        field("temperature", "r.t.", ev2), field("time", None), field("solvent", "THF", ev2),
    ])],
    outcomes=[field("reaction_outcome", "complicated", ev2, ["product_complicated_mixture"])],
    notes=["The prose explicitly says this reaction used the standard conditions; only standard values stated elsewhere in the supplied main text are carried into the record."],
    unresolved=["Vinylmagnesium chloride concentration, reaction time, workup, purification, and product identities are missing."],
))

for tag, label in [("methyl", "methyl magnesium chloride"), ("phenyl", "phenyl magnesium chloride")]:
    parts = [
        substrate("1i", ev2), participant(f"reagent_{tag}_mgcl", "reagent", label, ev2, label),
        solvent("solvent_thf", "THF", "tetrahydrofuran", "C1CCOC1", ev2),
        participant("product_conjugate_addition", "product", "related conjugate addition product(s)", ev2),
    ]
    records.append(record(
        f"diverted_1i_with_{tag}_mgcl", "reported_experiment", [2], participants=parts,
        steps=[step("conjugate_addition", [p["entity_id"] for p in parts[:-1]], [
            field("temperature", "r.t.", ev2), field("time", None), field("solvent", "THF", ev2),
        ])],
        outcomes=[field("reaction_outcome", "related conjugate addition product(s)", ev2, ["product_conjugate_addition"])],
        unresolved=["Reagent amount/concentration, scale, reaction time, product identity, yield, workup, and purification are missing."],
    ))

# Scheme 2 and detailed experimental paragraphs: four independent transformations.
ev123 = evidence(2, 3)
p5_parts = [
    product("2i", ev123, entity_id="reactant_2i", display_label="2i"),
    participant("reagent_i2", "reagent", "I2", ev123, "iodine", "II", [
        field("mass", q(131.0, "mg"), ev123), field("amount", q(0.5, "mmol"), ev123),
        field("equivalents", q(2.5, "equiv"), ev123)]),
    solvent("solvent_mecn", "CH3CN", "acetonitrile", "CC#N", ev123, 2),
    solvent("solvent_water", "H2O", "water", "O", ev123, 0.13),
    participant("workup_na2s2o3", "reagent", "saturated aqueous Na2S2O3", ev123, "sodium thiosulfate"),
    solvent("extraction_ether", "ether", "diethyl ether", "CCOCC", ev123, 75),
    participant("wash_nacl", "reagent", "aqueous NaCl", ev123, "sodium chloride", "[Na+].[Cl-]"),
    participant("drying_na2so4", "reagent", "Na2SO4", ev123, "sodium sulfate", "[Na+].[Na+].[O-]S(=O)(=O)[O-]"),
    product("5", ev123, name="2,2-diallyl-3-benzyl-5-butyl-4-iodo-2,5-dihydrofuran",
            smiles="C=CCC1(CC=C)OC(CCCC)C(I)=C1Cc2ccccc2"),
]
p5_parts[0]["role"] = "reactant"
p5_parts[0]["amounts"] = [field("mass", q(58.9, "mg"), ev123), field("amount", q(0.2, "mmol"), ev123)]
records.append(record(
    "scheme2_iodocyclization_2i_to_5", "reported_experiment", [2, 3], participants=p5_parts,
    steps=[step("iodocyclization", [p["entity_id"] for p in p5_parts[:-1]], [
        field("temperature", "r.t.", ev123), field("time", q(2, "h"), ev123),
        field("solvent_composition_ratio", "CH3CN/H2O = 15:1", ev123),
        field("workup", "quench with saturated aqueous Na2S2O3; extract with ether (3 × 25 mL); wash with aqueous NaCl; dry over Na2SO4", ev123),
        field("purification", "silica gel column chromatography: first petroleum ether, then petroleum ether/ethyl acetate = 40:1", ev123),
    ])],
    outcomes=[field("isolated_yield_5", q(89, "%"), ev123, ["product_5"]),
              field("yield_measurement_basis", "isolated yield", ev123, ["product_5"]),
              field("isolated_product_mass", q(74.4, "mg"), ev123, ["product_5"])],
    unresolved=["The product candidate structure remains machine-unverified."],
))

p6_parts = [
    product("2i", ev123, entity_id="reactant_2i", display_label="2i"),
    participant("reagent_allyl_bromide", "reagent", "allyl bromide", ev123, "allyl bromide", "C=CCBr", [
        field("mass", q(188.0, "mg"), ev123), field("amount", q(1.5, "mmol"), ev123),
        field("equivalents", q(5, "equiv"), ev123)]),
    participant("catalyst_pdcl2", "catalyst", "PdCl2", ev123, "palladium(II) chloride", "[Cl-].[Cl-].[Pd+2]", [
        field("mass", q(3.0, "mg"), ev123), field("amount", q(0.015, "mmol"), ev123),
        field("catalyst_loading", q(5, "mol%"), ev123)]),
    solvent("solvent_dma", "DMA", "N,N-dimethylacetamide", "CC(=O)N(C)C", ev123, 1),
    solvent("workup_ether", "ether", "diethyl ether", "CCOCC", ev123, 60),
    participant("wash_hcl", "reagent", "1% aqueous HCl", ev123, "hydrochloric acid", "Cl"),
    participant("wash_nahco3", "reagent", "saturated aqueous NaHCO3", ev123, "sodium bicarbonate", "O=C([O-])O.[Na+]"),
    participant("wash_brine", "reagent", "brine", ev123),
    participant("drying_na2so4", "reagent", "anhydrous Na2SO4", ev123, "sodium sulfate", "[Na+].[Na+].[O-]S(=O)(=O)[O-]"),
    product("6", ev123, name="2,2,4-triallyl-3-benzyl-5-butyl-2,5-dihydrofuran",
            smiles="C=CCC1(CC=C)OC(CCCC)C(CC=C)=C1Cc2ccccc2"),
]
p6_parts[0]["role"] = "reactant"
p6_parts[0]["amounts"] = [field("mass", q(89.0, "mg"), ev123), field("amount", q(0.3, "mmol"), ev123)]
records.append(record(
    "scheme2_pd_allyl_cyclization_2i_to_6", "reported_experiment", [2, 3], participants=p6_parts,
    steps=[step("palladium_mediated_allyl_cyclization", [p["entity_id"] for p in p6_parts[:-1]], [
        field("temperature", "r.t.", ev123), field("time", q(48, "h"), ev123), field("solvent", "DMA", ev123),
        field("workup", "dilute with ether; wash with 1% aqueous HCl, saturated NaHCO3, and brine; dry over anhydrous Na2SO4", ev123),
        field("purification", "silica gel column chromatography: first petroleum ether, then petroleum ether/ethyl acetate = 100:1", ev123),
    ])],
    outcomes=[field("isolated_yield_6", q(76, "%"), ev123, ["product_6"]),
              field("yield_measurement_basis", "isolated yield", ev123, ["product_6"]),
              field("isolated_product_mass", q(76.8, "mg"), ev123, ["product_6"])],
    unresolved=["The product candidate structure remains machine-unverified."],
))

ev234 = evidence(2, 3, 4)
p7_parts = [
    product("2i", ev234, entity_id="reactant_2i", display_label="2i"),
    participant("catalyst_agno3", "catalyst", "AgNO3", ev234, "silver nitrate", "[Ag+].[O-][N+](=O)[O-]", [
        field("mass", q(6.9, "mg"), ev234), field("amount", q(0.04, "mmol"), ev234),
        field("catalyst_loading", q(20, "mol%"), ev234)]),
    solvent("solvent_dcm", "CH2Cl2", "dichloromethane", "ClCCl", ev234, 2),
    solvent("quench_ether", "ether", "diethyl ether", "CCOCC", ev234, 10),
    product("7", ev234, name="2,2-diallyl-3-benzyl-5-butyl-2,5-dihydrofuran",
            smiles="C=CCC1(CC=C)OC(CCCC)C=C1Cc2ccccc2"),
]
p7_parts[0]["role"] = "reactant"
p7_parts[0]["amounts"] = [field("mass", q(58.9, "mg"), ev234), field("amount", q(0.2, "mmol"), ev234)]
records.append(record(
    "scheme2_ag_cyclization_2i_to_7", "reported_experiment", [2, 3, 4], participants=p7_parts,
    steps=[step("silver_catalyzed_cyclization", [p["entity_id"] for p in p7_parts[:-1]], [
        field("temperature", "r.t.", ev234), field("time", q(11, "h"), ev234), field("solvent", "CH2Cl2", ev234),
        field("workup", "add ether to quench; concentrate", ev234),
        field("purification", "silica gel column chromatography: first petroleum ether, then petroleum ether/ethyl acetate = 100:1", ev234),
    ])],
    outcomes=[field("isolated_yield_7", q(99, "%"), ev234, ["product_7"]),
              field("yield_measurement_basis", "isolated yield", ev234, ["product_7"]),
              field("isolated_product_mass", q(58.5, "mg"), ev234, ["product_7"])],
    notes=["Page 4 begins with continuation of product 7 characterization; it does not add another reaction."],
    unresolved=["The product candidate structure remains machine-unverified."],
))

p8_parts = [
    product("7", ev234, entity_id="reactant_7", display_label="7",
            name="2,2-diallyl-3-benzyl-5-butyl-2,5-dihydrofuran",
            smiles="C=CCC1(CC=C)OC(CCCC)C=C1Cc2ccccc2"),
    participant("catalyst_grubbs_ii", "catalyst", "Grubbs II catalyst", ev234, "second-generation Grubbs catalyst", None, [
        field("mass", q(9.2, "mg"), ev234), field("amount", q(0.01, "mmol"), ev234),
        field("catalyst_loading", q(5, "mol%"), ev234)]),
    solvent("solvent_dcm", "CH2Cl2/DCM", "dichloromethane", "ClCCl", ev234, 4),
    product("8", ev234, name="4-benzyl-2-(n-butyl)-1-oxaspiro[4.4]nona-3,7-diene",
            smiles="CCCCC1OC2(CC=CC2)C(Cc2ccccc2)=C1"),
]
p8_parts[0]["role"] = "reactant"
p8_parts[0]["amounts"] = [field("reported_mass", q(41.8, "mg"), ev234), field("reported_amount", q(0.2, "mmol"), ev234)]
records.append(record(
    "scheme2_rcm_7_to_8", "reported_experiment", [2, 3, 4], participants=p8_parts,
    steps=[step("ring_closing_metathesis", [p["entity_id"] for p in p8_parts[:-1]], [
        field("temperature", "reflux", ev234), field("time", q(2, "h"), ev234),
        field("atmosphere", "N2", ev234), field("solvent", "CH2Cl2 (DCM)", ev234),
        field("workup", "concentrated", ev234),
        field("purification", "flash silica gel chromatography, petroleum ether/Et2O = 100:1", ev234),
    ])],
    outcomes=[field("isolated_yield_8", q(86, "%"), ev234, ["product_8"]),
              field("yield_measurement_basis", "isolated yield", ev234, ["product_8"]),
              field("isolated_product_mass", q(32.5, "mg"), ev234, ["product_8"])],
    notes=["The source explicitly prints 41.8 mg and 0.2 mmol for reactant 7; both values are retained without correction."],
    unresolved=["The printed 41.8 mg/0.2 mmol charge is internally inconsistent with the named reactant formula and the reported product mass/yield; source values require review.",
                "The complex catalyst and product candidate structures remain unverified."],
))


ids = lambda *suffixes: [f"{DOC}:{s}" for s in suffixes]
table1_ids = ids(*[f"table1_entry{i}" for i in range(1, 5)])
table2_ids = ids(*[f"table2_entry{i}" for i in range(1, 20)])
negative_ids = ids(
    "negative_1i_with_1_buten_3_yl_mgcl", "negative_1i_with_2_butenyl_mgcl",
    "negative_1i_with_3_phenyl_2_propenyl_mgcl", "negative_1i_with_vinyl_mgcl",
    "diverted_1i_with_methyl_mgcl", "diverted_1i_with_phenyl_mgcl",
)
scheme2_ids = ids("scheme2_iodocyclization_2i_to_5", "scheme2_pd_allyl_cyclization_2i_to_6",
                  "scheme2_ag_cyclization_2i_to_7", "scheme2_rcm_7_to_8")

coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1,
            "state": "attempted",
            "regions": [
                {"region": "page 1 upper-left graphical abstract reaction arrow",
                 "finding": "Generic 2,3-allenoate plus allylmagnesium chloride summary (THF, r.t., 2–35 min, 60–100%); classified as a general scheme, not a unique batch.",
                 "evidence_ids": evidence(1)},
                {"region": "page 1 upper-right Scheme 1",
                 "finding": "Conceptual possible 1,2-addition, 1,4-addition, and double-bond-migration pathways for generic R-group substrates; no experimental yield assigned.",
                 "evidence_ids": evidence(1)},
                {"region": "page 1 right-center equation (1)",
                 "finding": "Distinct Fe(acac)3-catalyzed trial of 1a with allylmagnesium chloride in toluene at −78 °C for 1.5 h, giving 2a in 85% isolated yield; 1,4-addition product not observed.",
                 "evidence_ids": evidence(1)},
                {"region": "page 1 lower-right prose introducing Table 1",
                 "finding": "Corroborates Table 1 entry 1 as iron-free and defines entry 3 as the 0.4 mmol, THF (5 mL), room-temperature standard experiment; linked to those page-2 rows without duplication.",
                 "evidence_ids": evidence(1)},
                {"region": "page 1 introduction and references",
                 "finding": "Prior reviews and cited allene/Grignard work are literature context, not new experiments of this paper.",
                 "evidence_ids": evidence(1)},
            ],
            "record_ids": ids("graphical_abstract_general_double_addition", "scheme1_possible_organometallic_pathways",
                              "eq1_fe_catalyzed_1a_to_2a", "table1_entry1", "table1_entry3"),
            "unresolved": ["Generic R-group structures in the overview graphics are not unique molecules.",
                           "Equation (1) omits scale, volume, atmosphere, workup, and purification."],
        },
        {
            "page": 2,
            "state": "attempted",
            "regions": [
                {"region": "page 2 upper-left Table 1 reaction drawing and entries 1–4",
                 "finding": "Four solvent/temperature optimization experiments were retained row-by-row with times and NMR yields; entry 3 incorporates only the standard scale/volume explicitly stated on page 1.",
                 "evidence_ids": evidence(2)},
                {"region": "page 2 left-center Table 2 reaction drawing, entries 1–19, and footnotes a–b",
                 "finding": "Nineteen distinct substrate-scope rows were retained with common 0.4 mmol/3 equiv/1.7 M/THF 5 mL/r.t. header conditions, isolated yields, and times. Footnote a overrides entry 10 to 2 mmol; footnote b identifies 1r as methyl 2,3-butadienoate.",
                 "evidence_ids": evidence(2)},
                {"region": "page 2 upper-right equations (2), (3), and (4)",
                 "finding": "Three distinct experiments retained: bis-allenoate 3 to 4 (82%, dr≈1:1), optically active 1c to 2c (90%, 97% ee), and 1i with 2-methylallylmagnesium chloride to 2s (98%).",
                 "evidence_ids": evidence(2)},
                {"region": "page 2 right-center negative and diverted-reaction prose",
                 "finding": "Six reagent-specific outcomes retained separately: three substituted allylmagnesium chlorides and vinylmagnesium chloride gave complicated results; methyl- and phenylmagnesium chloride gave conjugate-addition products.",
                 "evidence_ids": evidence(2)},
                {"region": "page 2 lower-right cyclization discussion",
                 "finding": "Narrative points to the four Scheme 2 transformations and the 86% RCM product 8; linked to page-3/4 records without creating duplicate experiments.",
                 "evidence_ids": evidence(2)},
            ],
            "record_ids": [*table1_ids, *table2_ids, *ids("eq2_bis_allenoate_3_to_4", "eq3_optically_active_1c_to_2c",
                                                        "eq4_2_methylallyl_addition_1i_to_2s"),
                           *negative_ids, *scheme2_ids],
            "unresolved": ["Most table rows omit atmosphere, workup, and purification; Table 1 omits scale/volume except entry 3.",
                           "Several negative reactions lack conditions and product identities.",
                           "Yield basis is absent for equations (2) and (4)."],
        },
        {
            "page": 3,
            "state": "attempted",
            "regions": [
                {"region": "page 3 upper Scheme 2, four reaction arrows",
                 "finding": "Four independent transformations inspected: iodocyclization 2i→5 (89%), Pd/allyl bromide cyclization 2i→6 (76%), AgNO3 cyclization 2i→7 (99%), and Grubbs-II RCM 7→8 (86%).",
                 "evidence_ids": evidence(3)},
                {"region": "page 3 lower-left detailed preparation of 2a",
                 "finding": "Detailed 0.4 mmol, 3 min, 94% procedure matches Table 2 entry 1 and was merged into that row with charges, nitrogen atmosphere, workup, purification, and product mass.",
                 "evidence_ids": evidence(3)},
                {"region": "page 3 lower-left/right detailed preparations of 5 and 6",
                 "finding": "Detailed charges, solvent volumes, workups, chromatography, and product masses support the existing Scheme 2 records; no duplicate records created.",
                 "evidence_ids": evidence(3)},
                {"region": "page 3 lower-right detailed preparation of 7 (continues characterization on page 4)",
                 "finding": "Detailed AgNO3-catalyzed batch supports the 2i→7 Scheme 2 record; page-4 continuation is characterization, not a new reaction.",
                 "evidence_ids": evidence(3)},
                {"region": "page 3 Materials section",
                 "finding": "Reagent solution concentrations/solvents were attached to the three complicated-mixture records only where explicitly stated; preparations by cited procedures were not imported as current-paper experiments.",
                 "evidence_ids": evidence(3)},
            ],
            "record_ids": [f"{DOC}:table2_entry1", *scheme2_ids, *negative_ids[:3]],
            "unresolved": ["Candidate structures remain machine-unverified.",
                           "The detailed text provides characterization but does not independently verify the machine SMILES."],
        },
        {
            "page": 4,
            "state": "attempted",
            "regions": [
                {"region": "page 4 upper-left continuation of product 7 characterization",
                 "finding": "Continuation of the page-3 2i→7 experiment characterization; no additional reaction record created.",
                 "evidence_ids": evidence(4)},
                {"region": "page 4 left/upper-right detailed RCM preparation of 8",
                 "finding": "Grubbs-II-catalyzed RCM of 7 in CH2Cl2 under N2 at reflux for 2 h, with chromatography and 86% isolated yield; merged with Scheme 2. The printed 41.8 mg/0.2 mmol charge is preserved as an unresolved source inconsistency.",
                 "evidence_ids": evidence(4)},
                {"region": "page 4 right-center Supporting Information notice",
                 "finding": "The paper states that experimental details and spectra are available as Supporting Information, but no SI file was supplied or explicitly associated; no SI data were inferred.",
                 "evidence_ids": evidence(4)},
                {"region": "page 4 acknowledgments and publication metadata",
                 "finding": "No additional reaction experiment; the reproduction acknowledgment does not supply new conditions or results beyond Table 2.",
                 "evidence_ids": evidence(4)},
            ],
            "record_ids": ids("scheme2_ag_cyclization_2i_to_7", "scheme2_rcm_7_to_8"),
            "unresolved": ["Supporting Information association remains unestablished.",
                           "The reactant-7 mass/mmol values printed for the RCM batch are internally inconsistent and require source review."],
        },
    ],
}


OUT.parent.mkdir(parents=True, exist_ok=True)
COVERAGE.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
COVERAGE.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

tasks = json.loads(TASKS.read_text())
for item in tasks:
    if item.get("document_id") == DOC and item.get("task_id", "").endswith(":text"):
        item["state"] = "attempted"
        item["reason"] = "Original page image and extracted text inspected; coverage ledger records experiments, classifications, and unresolved details."
TASKS.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"records": len(records), "raw_records": str(OUT), "coverage": str(COVERAGE)}, ensure_ascii=False))
