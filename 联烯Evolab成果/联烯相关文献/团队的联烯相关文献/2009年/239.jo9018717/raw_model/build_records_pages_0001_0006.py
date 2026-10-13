#!/usr/bin/env python3
"""Build machine extraction records for doc_7f9dc494dd9537a1, PDF pages 1-6."""
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / "runs" / "current"
DATASET = RUN / "dataset.json"
DOC = "doc_7f9dc494dd9537a1"


def ev(*pages: int) -> list[str]:
    values = []
    for page in pages:
        values += [f"{DOC}:page{page}:image", f"{DOC}:page{page}:text"]
    return values


def fact(value, evidence):
    return {
        "value": value,
        "evidence_ids": list(evidence) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def field(name, value, evidence, targets=None):
    item = {"name": name, "fact": fact(value, evidence)}
    if targets:
        item["target_entity_ids"] = list(targets)
    return item


def participant(entity_id, role, label, evidence, *, name=None, smiles=None, amounts=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence) if name else fact(None, []),
        "smiles": fact(smiles, evidence) if smiles else fact(None, []),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": amounts or [],
    }


def record(suffix, kind, evidence, participants, steps, outcomes, *, notes=None, unresolved=None):
    return {
        "record_id": f"{DOC}:{suffix}",
        "document_id": DOC,
        "source_reaction_id": suffix,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": list(evidence),
        "participants": participants,
        "steps": steps,
        "outcomes": outcomes,
        "notes": [fact(x, evidence) for x in (notes or [])],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved or [
                "Machine extraction requires chemistry review; candidate structures are not source-verified.",
                "No supporting-information file was explicitly associated; unreported operations remain missing.",
            ],
        },
    }


def q(number, unit, **extra):
    return {"number": number, "unit": unit, **extra}


def qr(low, high, unit, raw):
    return {"minimum": low, "maximum": high, "unit": unit, "raw_text": raw}


SMILES = {
    "1a": "C=C=CC1(O)CCCCC1",
    "1b": "C=C=CC1(O)CCCC1",
    "1c": "C=C=CC1(O)CCCCCC1",
    "1d": "C=C=CC1(O)CCCCCCC1",
    "1g": "C=C=CC(C)(O)c1ccccc1",
    "3a": "C=C(Br)C1CCCCC(=O)C1",
    "3b": "C=C(Br)C1CCCCC1=O",
    "3g": "C=C(Br)C(c1ccccc1)C(C)=O",
    "4g": "C=C=C(c1ccccc1)C(C)=O",
    "NBS": "O=C1CCC(=O)N1Br",
    "H2O": "O",
    "MeCN": "CC#N",
    "THF": "C1CCOC1",
    "MeNO2": "C[N+](=O)[O-]",
    "CH2Cl2": "ClCCl",
    "CCl4": "ClC(Cl)(Cl)Cl",
    "MeOH": "CO",
    "dioxane": "O1CCOCC1",
    "Et3N": "CCN(CC)CC",
    "LiAlH4": "[Li+].[AlH4-]",
    "AcOH": "CC(=O)O",
    "CH2Br2": "BrCBr",
    "Et2O": "CCOCC",
}


def molecule(label, role, evidence, *, entity=None, name=None, smiles=None, amounts=None):
    entity = entity or label.replace(" ", "_").replace("/", "_")
    return participant(entity, role, label, evidence, name=name, smiles=smiles or SMILES.get(label), amounts=amounts)


def solvents(spec, evidence):
    if spec == "H2O":
        return [molecule("H2O", "solvent", evidence, name="water", entity="water")]
    if spec.startswith("MeCN/H2O"):
        return [
            molecule("MeCN", "solvent", evidence, name="acetonitrile", entity="mecn"),
            molecule("H2O", "solvent", evidence, name="water", entity="water"),
        ]
    mapping = {
        "THF": ("tetrahydrofuran", "THF"),
        "MeCN": ("acetonitrile", "MeCN"),
        "MeNO2": ("nitromethane", "MeNO2"),
        "CH2Cl2": ("dichloromethane", "CH2Cl2"),
        "CCl4": ("carbon tetrachloride", "CCl4"),
        "MeOH": ("methanol", "MeOH"),
        "1,4-dioxane": ("1,4-dioxane", "dioxane"),
    }
    name, key = mapping[spec]
    return [molecule(spec, "solvent", evidence, name=name, smiles=SMILES[key], entity="solvent")]


def basic_step(participants, solvent, temperature, time, evidence, *, step_id="reaction"):
    conditions = [
        field("solvent", solvent, evidence),
        field("temperature", temperature, evidence),
        field("time", q(time, "h") if isinstance(time, (int, float)) else time, evidence),
    ]
    return {"step_id": step_id, "participant_ids": [p["entity_id"] for p in participants if p["role"] != "product"], "conditions": conditions}


def detailed_workup_step(evidence, purification):
    return {
        "step_id": "workup_and_purification",
        "participant_ids": ["thiosulfate", "ether", "brine", "sodium_sulfate", "silica"],
        "conditions": [
            field("workup", "quenched with saturated aqueous Na2S2O3; extracted with ether; washed with brine; dried over anhydrous Na2SO4; filtered and evaporated", evidence),
            field("purification", purification, evidence),
        ],
    }


def detailed_workup_participants(evidence):
    return [
        molecule("saturated aqueous Na2S2O3", "reagent", evidence, name="sodium thiosulfate solution", entity="thiosulfate", amounts=[field("volume", q(1, "mL"), evidence)]),
        molecule("ether", "solvent", evidence, name="diethyl ether", smiles=SMILES["Et2O"], entity="ether", amounts=[field("extraction_volume", q(10, "mL"), evidence)]),
        molecule("brine", "reagent", evidence, entity="brine", amounts=[field("volume", q(10, "mL"), evidence)]),
        molecule("anhydrous Na2SO4", "reagent", evidence, name="sodium sulfate", entity="sodium_sulfate"),
        molecule("silica gel", "reagent", evidence, entity="silica"),
    ]


records = []

# Page 1 graphical abstract: generic summary, deliberately not a reported batch.
e = ev(1)
p = [
    molecule("tertiary 2,3-allenol 1", "reactant", e, entity="generic_allenol"),
    molecule("NBS", "reagent", e, name="N-bromosuccinimide", amounts=[field("equivalents", q(1, "equiv"), e)]),
    molecule("2-bromoallylic ketone 3", "product", e, entity="generic_ketone"),
    molecule("1,2-allenyl ketone 4", "product", e, entity="generic_allenyl_ketone"),
    molecule("3-bromo-2,5-dihydrofuran 5", "product", e, entity="generic_dihydrofuran"),
]
records.append(record(
    "graphical_abstract_general_scheme", "general_scheme", e, p,
    [{"step_id": "generic_br_electrophilic_reaction", "participant_ids": ["generic_allenol", "NBS"], "conditions": [field("solvent", "CH3CN/H2O = 15/1 or H2O", e)]}],
    [
        field("reported_scope_yield", qr(53, 97, "%", "53-97%"), e, ["generic_ketone"]),
        field("reported_scope_yield", qr(47, 89, "%", "47-89%"), e, ["generic_allenyl_ketone"]),
        field("reported_scope_yield", qr(61, 84, "%", "61-84%"), e, ["generic_dihydrofuran"]),
    ],
    notes=["Graphical abstract summarizes substrate-dependent branches and is not an individual experimental batch."],
))


# Table 1, page 2. Each optimization row is independent.
table1 = [
    (1, "MeCN/H2O = 15/1", "r.t.", 1, 50, 19, 0, 1.1),
    (2, "MeCN/H2O = 15/1", q(0, "°C"), 2, 54, 25, 0, 1.1),
    (3, "THF", "r.t.", 3, 29, 13, 6, 1.1),
    (4, "MeCN", "r.t.", 10, 22, 21, 33, 1.1),
    (5, "MeNO2", "r.t.", 2, 6, 17, 29, 1.1),
    (6, "CH2Cl2", "r.t.", 3, 5, 4, 62, 1.1),
    (7, "CCl4", "r.t.", 3, 0, 0, 60, 1.1),
    (8, "MeOH", "r.t.", 2, None, None, None, 1.1),
    (9, "1,4-dioxane", "r.t.", 2, 10, 7, 52, 1.1),
    (10, "MeCN/H2O = 5/1", "r.t.", 10, 50, 34, 0, 1.1),
    (11, "MeCN/H2O = 1/1", "r.t.", 10, 26, 48, 0, 1.1),
    (12, "MeCN/H2O = 1/10", "r.t.", 2, 12, 55, 0, 1.1),
    (13, "H2O", "r.t.", 2, 10, 58, 0, 1.1),
    (14, "H2O", "r.t.", 2, 8, 60, 0, 1.0),
    (15, "H2O", "r.t.", 2, 7, 51, 0, 1.2),
    (16, "H2O", "r.t.", 2, 7, 50, 0, 1.5),
    (17, "H2O", "r.t.", 2, 4, 20, 0, 2.0),
    (18, "H2O", q(60, "°C"), 2, 6, 51, 0, 1.0),
    (19, "H2O", q(80, "°C"), 2, 8, 49, 0, 1.0),
]

for entry, solvent, temp, hours, y2, y3, recovery, nbs_eq in table1:
    evidence = ev(2, 5) if entry == 14 else ev(2)
    p = [
        molecule("1a", "reactant", evidence, name="1-(propadienyl)cyclohexanol", amounts=[]),
        molecule("NBS", "reagent", evidence, name="N-bromosuccinimide", amounts=[field("equivalents", q(nbs_eq, "equiv"), evidence)]),
        *solvents(solvent, evidence),
        molecule("2a", "product", evidence, name="2-bromovinyl-substituted epoxide", entity="product_2a"),
        molecule("3a", "product", evidence, name="2-(1-bromovinyl)cycloheptanone", entity="product_3a"),
    ]
    outcomes = []
    if entry == 8:
        outcomes += [
            field("product_distribution", "complicated", evidence, ["product_2a", "product_3a"]),
            field("NMR_yield_2a", None, evidence, ["product_2a"]),
            field("NMR_yield_3a", None, evidence, ["product_3a"]),
            field("recovered_starting_material_yield", None, evidence, ["1a"]),
        ]
    else:
        outcomes += [
            field("NMR_yield_2a", q(y2, "%"), evidence, ["product_2a"]),
            field("NMR_yield_3a", q(y3, "%"), evidence, ["product_3a"]),
            field("recovered_starting_material_yield", q(recovery, "%"), evidence, ["1a"]),
            field("yield_measurement_basis", "1H NMR using CH2Br2 as internal standard", evidence, ["product_2a", "product_3a"]),
        ]
    if entry == 1:
        outcomes += [
            field("combined_NMR_yield", q(69, "%"), evidence, ["product_2a", "product_3a"]),
            field("product_selectivity_2a_to_3a", "2.6:1", evidence, ["product_2a", "product_3a"]),
        ]
    if entry == 14:
        outcomes += [field("isolated_yield_3a", q(58, "%"), evidence, ["product_3a"])]
        p[0]["amounts"] = [field("mass", q(41.3, "mg"), evidence), field("amount", q(0.30, "mmol"), evidence)]
        p[1]["amounts"] += [field("mass", q(54.8, "mg"), evidence), field("amount", q(0.31, "mmol"), evidence)]
        water = next(x for x in p if x["entity_id"] == "water")
        water["amounts"] = [field("volume", q(4.0, "mL"), evidence)]
        p += [
            molecule("CH2Br2", "reagent", evidence, name="dibromomethane", entity="internal_standard"),
            molecule("AcOH", "reagent", evidence, name="acetic acid", entity="acoh", amounts=[field("amount", "10 drops", evidence)]),
            *detailed_workup_participants(evidence),
        ]
        steps = [basic_step(p, solvent, temp, hours, evidence), detailed_workup_step(evidence, "silica-gel chromatography pre-eluted with petroleum ether then 10 drops AcOH; petroleum ether/ethyl acetate = 30/1")]
        outcomes += [field("isolated_product_mass", q(37.8, "mg"), evidence, ["product_3a"])]
    else:
        steps = [basic_step(p, solvent, temp, hours, evidence)]
    records.append(record(f"table1_entry{entry}", "optimization_entry", evidence, p, steps, outcomes))


# Two prose controls adjacent to Table 1.
e = ev(2)
p = [
    molecule("1a", "reactant", e, name="1-(propadienyl)cyclohexanol"),
    molecule("NBS", "reagent", e, name="N-bromosuccinimide"),
    *solvents("MeCN/H2O = 15/1", e),
    molecule("2a", "product", e, name="2-bromovinyl-substituted epoxide", entity="product_2a"),
    molecule("3a", "product", e, name="2-(1-bromovinyl)cycloheptanone", entity="product_3a"),
]
records.append(record(
    "prose_entry1_extended_4h", "optimization_entry", e, p,
    [basic_step(p, "MeCN/H2O = 15/1", "r.t.", 4, e)],
    [field("product_ratio_relative_to_table1_entry1", "essentially the same ratio", e, ["product_2a", "product_3a"])],
    unresolved=["Only the qualitative ratio comparison is reported; individual four-hour yields are missing."],
))

p = [
    molecule("2a", "reactant", e, name="pure 2-bromovinyl-substituted epoxide", entity="reactant_2a"),
    molecule("NBS", "reagent", e, name="N-bromosuccinimide"),
    *solvents("MeCN/H2O = 15/1", e),
    molecule("3a", "product", e, name="2-(1-bromovinyl)cycloheptanone", entity="product_3a"),
]
records.append(record(
    "control_epoxide_2a_12h", "reported_experiment", e, p,
    [basic_step(p, "conditions listed in Table 1 entry 1", "r.t.", 12, e)],
    [field("formation_of_3a", "not observed", e, ["product_3a"])],
    unresolved=["Starting amount and recovery of pure epoxide 2a are not reported."],
))


# Table 2 scope rows.
table2 = [
    (1, "(CH2)4 (1b)", None, "3b", 59, "NMR", 0, "H2O"),
    (2, "(CH2)4 (1b)", None, "3b", 53, "isolated", 0, "MeCN/H2O = 15/1"),
    (3, "(CH2)6 (1c)", None, "3c", 62, "isolated", 12, "H2O"),
    (4, "(CH2)7 (1d)", None, "3d", 58, "isolated", 8, "H2O"),
    (5, "n-C3H7", "n-C3H7 (1e)", "3e", 60, "isolated", 4, "H2O"),
    (6, "n-C4H9", "n-C4H9 (1f)", "3f", 60, "isolated", 4, "H2O"),
    (7, "Ph", "CH3 (1g)", "3g", 97, "isolated", 0, "H2O"),
    (8, "Ph", "C2H5 (1h)", "3h", 93, "isolated", 0, "H2O"),
    (9, "m-CH3C6H4", "CH3 (1i)", "3i", 82, "isolated", 0, "H2O"),
    (10, "p-CH3C6H4", "CH3 (1j)", "3j", 79, "isolated", 0, "H2O"),
    (11, "Ph", "Ph (1k)", "3k", 79, "isolated", 0, "H2O"),
]

for entry, r1, r2, product, y3, basis, y2, solvent in table2:
    evidence = ev(3, 5) if entry == 2 else ev(3)
    substrate = f"1{chr(97+entry)}" if entry <= 11 else f"1_entry{entry}"
    # Explicit source labels, rather than inferred systematic names, are retained for all rows.
    if entry == 1 or entry == 2:
        substrate = "1b"
    elif entry == 3:
        substrate = "1c"
    elif entry == 4:
        substrate = "1d"
    else:
        substrate = f"1{chr(96+entry)}"
    p = [
        molecule(substrate, "reactant", evidence, entity="substrate", smiles=SMILES.get(substrate)),
        molecule("NBS", "reagent", evidence, name="N-bromosuccinimide", amounts=[field("equivalents", q(1.0, "equiv"), evidence)]),
        *solvents(solvent, evidence),
        molecule(product, "product", evidence, entity="product_3"),
        molecule(f"2{product[-1]}", "product", evidence, entity="product_2"),
    ]
    outcomes = [
        field(f"{basis}_yield_{product}", q(y3, "%"), evidence, ["product_3"]),
        field("NMR_yield_epoxide_2", q(y2, "%"), evidence, ["product_2"]),
        field("yield_measurement_basis", basis, evidence, ["product_3"]),
        field("epoxide_yield_measurement_basis", "NMR", evidence, ["product_2"]),
    ]
    notes = [f"Table substituents: R1 = {r1}; R2 = {r2 if r2 is not None else 'cyclic linkage'}." ]
    if entry == 1:
        p.append(molecule("unidentified product", "product", evidence, entity="unidentified_product"))
        outcomes.append(field("unidentified_product_formation", "reported together with 3b", evidence, ["unidentified_product"]))
    if entry == 2:
        p[0]["amounts"] = [field("mass", q(37.8, "mg"), evidence), field("amount", q(0.30, "mmol"), evidence)]
        p[1]["amounts"] += [field("mass", q(54.2, "mg"), evidence), field("amount", q(0.30, "mmol"), evidence)]
        next(x for x in p if x["entity_id"] == "mecn")["amounts"] = [field("volume", q(4.0, "mL"), evidence)]
        next(x for x in p if x["entity_id"] == "water")["amounts"] = [field("volume", q(0.27, "mL"), evidence)]
        p += [
            molecule("CH2Br2", "reagent", evidence, name="dibromomethane", entity="internal_standard"),
            molecule("AcOH", "reagent", evidence, name="acetic acid", entity="acoh", amounts=[field("amount", "10 drops", evidence)]),
            *detailed_workup_participants(evidence),
        ]
        outcomes += [
            field("crude_NMR_yield_3b", q(55, "%"), evidence, ["product_3"]),
            field("isolated_product_mass", q(33.1, "mg"), evidence, ["product_3"]),
        ]
        steps = [basic_step(p, solvent, "r.t.", 2, evidence), detailed_workup_step(evidence, "silica-gel chromatography pre-eluted with 10 drops AcOH; petroleum ether/ether = 10/1")]
    else:
        steps = [basic_step(p, solvent, "r.t.", 2, evidence)]
    records.append(record(f"table2_entry{entry}", "substrate_scope_entry", evidence, p, steps, outcomes, notes=notes))


# Scheme 1: four scale-distinct batches.
scheme1 = [
    ("1l_0p3mmol", "1l", 55.1, "mg", 0.30, "H2O", 2, "3l", 76),
    ("1l_3p0mmol", "1l", 557.6, "mg", 3.0, "H2O", 5, "3l", 92),
    ("1m_0p3mmol", "1m", 32.8, "mg", 0.30, "MeCN/H2O = 15/1", 2, "3m", 64),
    ("1m_10p0mmol", "1m", 1.1018, "g", 10.0, "MeCN/H2O = 15/1", 2, "3m", 71),
]
for suffix, substrate, mass, mass_unit, amount, solvent, hours, product, yield_value in scheme1:
    evidence = ev(3)
    p = [
        molecule(substrate, "reactant", evidence, amounts=[field("mass", q(mass, mass_unit), evidence), field("amount", q(amount, "mmol"), evidence)]),
        molecule("NBS", "reagent", evidence, name="N-bromosuccinimide", amounts=[field("equivalents", q(1.0, "equiv"), evidence)]),
        *solvents(solvent, evidence),
        molecule(product, "product", evidence, entity="product"),
    ]
    records.append(record(
        f"scheme1_{suffix}", "reported_experiment", evidence, p,
        [basic_step(p, solvent, "r.t.", hours, evidence)],
        [field(f"isolated_yield_{product}", q(yield_value, "%"), evidence, ["product"])],
    ))


# Scheme 2: sequential NBS rearrangement, base-treated chromatography, LiAlH4 reduction.
e = ev(4)
p = [
    molecule("1l", "reactant", e, entity="substrate"),
    molecule("NBS", "reagent", e, name="N-bromosuccinimide", amounts=[field("equivalents", q(1.0, "equiv"), e)]),
    molecule("H2O", "solvent", e, name="water", entity="water"),
    molecule("3l", "product", e, entity="intermediate_3l"),
    molecule("Et3N", "reagent", e, name="triethylamine", entity="et3n", amounts=[field("amount", "10 drops", e)]),
    molecule("silica gel", "reagent", e, entity="silica"),
    molecule("4l", "product", e, entity="intermediate_4l"),
    molecule("LiAlH4", "reagent", e, name="lithium aluminium hydride", entity="lialh4"),
    molecule("THF", "solvent", e, name="tetrahydrofuran", entity="thf"),
    molecule("1r", "product", e, entity="product_1r"),
]
records.append(record(
    "scheme2_three_step_1l_to_1r", "reported_experiment", e, p,
    [
        {"step_id": "nbs_rearrangement", "participant_ids": ["substrate", "NBS", "water"], "conditions": [field("solvent", "H2O", e), field("temperature", "r.t.", e), field("time", q(2, "h"), e)]},
        {"step_id": "base_treated_chromatography", "participant_ids": ["intermediate_3l", "et3n", "silica"], "conditions": [field("purification", "column chromatography on silica gel pre-eluted with 10 drops Et3N", e)]},
        {"step_id": "reduction", "participant_ids": ["intermediate_4l", "lialh4", "thf"], "conditions": [field("solvent", "THF", e), field("temperature", q(0, "°C"), e), field("time", q(35, "min"), e)]},
    ],
    [
        field("combined_three_step_yield_1r", q(51, "%"), e, ["product_1r"]),
        field("product_purity", q(91, "%"), e, ["product_1r"]),
    ],
    unresolved=["Amounts and stage-specific yields are not reported; 51% is explicitly the combined three-step yield.", "Intermediate 4l is reported as unstable."],
))


# Table 3: one-pot NBS/rearrangement/elimination scope.
table3 = [
    (1, "Ph", "CH3 (1g)", "1g", "4g", 74),
    (2, "Ph", "C2H5 (1h)", "1h", "4h", 77),
    (3, "m-CH3C6H4", "CH3 (1i)", "1i", "4i", 88),
    (4, "p-CH3C6H4", "CH3 (1j)", "1j", "4j", 89),
    (5, "Ph", "Ph (1k)", "1k", "4k", 74),
    (6, "p-NO2C6H4", "CH3 (1n)", "1n", "4n", 47),
]
for entry, r1, r2, substrate, product, y in table3:
    evidence = ev(4, 5) if entry == 1 else ev(4)
    p = [
        molecule(substrate, "reactant", evidence, entity="substrate", smiles=SMILES.get(substrate)),
        molecule("NBS", "reagent", evidence, name="N-bromosuccinimide", amounts=[field("equivalents", q(1.0, "equiv"), evidence)]),
        molecule("H2O", "solvent", evidence, name="water", entity="water"),
        molecule("Et3N", "reagent", evidence, name="triethylamine", entity="et3n", amounts=[field("amount", "10 drops", evidence)]),
        molecule("silica gel", "reagent", evidence, entity="silica"),
        molecule(product, "product", evidence, entity="product", smiles=SMILES.get(product)),
    ]
    if entry == 1:
        p[0]["amounts"] = [field("mass", q(46.2, "mg"), evidence), field("amount", q(0.29, "mmol"), evidence)]
        p[1]["amounts"] += [field("mass", q(53.0, "mg"), evidence), field("amount", q(0.30, "mmol"), evidence)]
        p[2]["amounts"] = [field("volume", q(4.0, "mL"), evidence)]
        outcomes = [field("isolated_yield", q(y, "%"), evidence, ["product"]), field("isolated_product_mass", q(33.6, "mg"), evidence, ["product"])]
    else:
        outcomes = [field("isolated_yield", q(y, "%"), evidence, ["product"])]
    steps = [
        {"step_id": "nbs_reaction", "participant_ids": ["substrate", "NBS", "water"], "conditions": [field("solvent", "H2O", evidence), field("temperature", "r.t.", evidence), field("time", q(2, "h"), evidence)]},
        {"step_id": "chromatographic_elimination", "participant_ids": ["et3n", "silica"], "conditions": [field("purification", "silica-gel chromatography pre-eluted with 10 drops Et3N" + ("; petroleum ether/ethyl acetate = 20/1" if entry == 1 else ""), evidence)]},
    ]
    records.append(record(f"table3_entry{entry}", "substrate_scope_entry", evidence, p, steps, outcomes, notes=[f"Table substituents: R1 = {r1}; R2 = {r2}."]))


# Table 4: cyclization scope; entry 1 is enriched with its page-5 detailed paragraph.
table4 = [
    (1, "(CH2)4", None, "Me", "Me (1o)", "1o", "5o", 71, "MeCN/H2O = 15/1", 1.0),
    (2, "(CH2)4", None, "Me", "Me (1o)", "1o", "5o", 67, "H2O", 1.0),
    (3, "Ph", "Me", "Me", "Me (1p)", "1p", "5p", 84, "MeCN/H2O = 15/1", 1.0),
    (4, "Ph", "Me", "Me", "Me (1p)", "1p", "5p", 69, "H2O", 1.0),
    (5, "(CH2)4", None, "n-C5H11", "H (1q)", "1q", "5q", 73, "MeCN/H2O = 15/1", 1.0),
    (6, "(CH2)4", None, "n-C5H11", "H (1q)", "1q", "5q", 61, "H2O", 1.2),
]
for entry, r1, r2, r3, r4, substrate, product, y, solvent, nbs_eq in table4:
    evidence = ev(4, 5) if entry == 1 else ev(4)
    p = [
        molecule(substrate, "reactant", evidence, entity="substrate"),
        molecule("NBS", "reagent", evidence, name="N-bromosuccinimide", amounts=[field("equivalents", q(nbs_eq, "equiv"), evidence)]),
        *solvents(solvent, evidence),
        molecule(product, "product", evidence, entity="product"),
        molecule("3-type ketone", "product", evidence, entity="ketone_not_formed"),
        molecule("2-type epoxide", "product", evidence, entity="epoxide_not_formed"),
    ]
    outcomes = [
        field("isolated_yield", q(y, "%"), evidence, ["product"]),
        field("formation_of_3_type_ketone", "not observed", evidence, ["ketone_not_formed"]),
        field("formation_of_2_type_epoxide", "not observed", evidence, ["epoxide_not_formed"]),
    ]
    if entry == 1:
        p[0]["amounts"] = [field("mass", q(45.8, "mg"), evidence), field("amount", q(0.30, "mmol"), evidence)]
        p[1]["amounts"] += [field("mass", q(53.8, "mg"), evidence), field("amount", q(0.30, "mmol"), evidence)]
        next(x for x in p if x["entity_id"] == "mecn")["amounts"] = [field("volume", q(4.0, "mL"), evidence)]
        next(x for x in p if x["entity_id"] == "water")["amounts"] = [field("volume", q(0.27, "mL"), evidence)]
        outcomes.append(field("isolated_product_mass", q(49.5, "mg"), evidence, ["product"]))
    steps = [basic_step(p, solvent, "r.t.", 2, evidence)]
    if entry == 1:
        steps.append({"step_id": "purification", "participant_ids": [], "conditions": [field("purification", "petroleum ether/ethyl ether = 50/1; following Typical Procedure 2", evidence)]})
    records.append(record(
        f"table4_entry{entry}", "substrate_scope_entry", evidence, p, steps, outcomes,
        notes=[f"Table substituents: R1 = {r1}; R2 = {r2 if r2 is not None else 'cyclic linkage'}; R3 = {r3}; R4 = {r4}."],
        unresolved=["Machine extraction requires chemistry review; candidate structures are not source-verified.", "For abbreviated scope rows, scale and workup details are not stated in the main text."],
    ))


# Scheme 3 is mechanistic interpretation, not an experimental batch.
e = ev(4, 5)
records.append(record(
    "scheme3_proposed_mechanism", "mechanism", e, [], [], [],
    notes=[
        "Proposed bromonium pathways A-C rationalize ketone 3, epoxide 2, allenyl ketone 4, and dihydrofuran 5 formation.",
        "Path a is 1,2-shift and proton loss; path b is intramolecular oxygen attack; path c is cyclization at the substituted allene terminus.",
    ],
    unresolved=["Intermediates A-C are proposed and are not reported as isolated or directly observed species."],
))


assert len(records) == 51, len(records)
assert len({r["record_id"] for r in records}) == len(records)

raw_path = RUN / "raw_model" / "records_pages_0001_0006.json"
raw_path.parent.mkdir(parents=True, exist_ok=True)
raw_path.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")


def ids(prefixes):
    return [r["record_id"] for r in records if any(r["source_reaction_id"].startswith(p) for p in prefixes)]


coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1,
            "state": "attempted",
            "regions": [
                {"region": "title, graphical abstract, and abstract", "finding": "The graphical abstract is a generic substrate-dependent reaction summary and was classified as a general scheme; abstract scope ranges were not duplicated as individual batches.", "evidence_ids": ev(1)},
                {"region": "opening Introduction at page bottom", "finding": "Prior electrophilic-addition work is cited literature/context, not a new experiment from this paper.", "evidence_ids": ev(1)},
            ],
            "record_ids": ids(["graphical_abstract"]),
            "unresolved": ["Generic R-group structures in the graphical abstract were not converted to complete SMILES."],
        },
        {
            "page": 2,
            "state": "attempted",
            "regions": [
                {"region": "upper half, Table 1 reaction drawing, entries 1-19, and footnotes", "finding": "All 19 optimization rows were extracted independently, including solvent ratios, temperature, time, NMR product yields, recovery, isolated yield in parentheses, and NBS-equivalent overrides.", "evidence_ids": ev(2)},
                {"region": "lower columns, Results and Discussion around Table 1", "finding": "The four-hour same-ratio observation and the 12-hour pure-2a control were extracted as distinct controls; cited Okamoto work was treated as prior literature.", "evidence_ids": ev(2)},
            ],
            "record_ids": ids(["table1_", "prose_entry1_", "control_epoxide_"]),
            "unresolved": ["Table 1 entry 8 reports only a complicated mixture; component yields and recovery are missing."],
        },
        {
            "page": 3,
            "state": "attempted",
            "regions": [
                {"region": "upper half, Table 2 reaction drawing, entries 1-11, and footnotes", "finding": "All 11 substrate-scope rows were extracted independently; entry 1's 59% NMR footnote and unidentified product and entry 2's mixed-solvent override were retained.", "evidence_ids": ev(3)},
                {"region": "middle-right Scheme 1 and adjacent prose", "finding": "The two 1l scales and two 1m scales are four distinct batches with their own mass, amount, time, and isolated yield.", "evidence_ids": ev(3)},
                {"region": "lower-right one-pot allenyl-ketone discussion", "finding": "Narrative introduces the Table 3 transformation and the 1l sequence continued on page 4; no duplicate record was made from prose alone.", "evidence_ids": ev(3)},
            ],
            "record_ids": ids(["table2_", "scheme1_"]),
            "unresolved": ["Most Table 2 rows omit reaction scale, workup, and purification in the supplied main text."],
        },
        {
            "page": 4,
            "state": "attempted",
            "regions": [
                {"region": "top, Scheme 2", "finding": "The NBS reaction, Et3N-pre-eluted chromatography, and LiAlH4 reduction were retained as three successive stages of one reported sequence with 51% combined yield and 91% purity.", "evidence_ids": ev(4)},
                {"region": "middle-left, Table 3 entries 1-6", "finding": "Six one-pot allenyl-ketone scope rows were extracted independently under their shared reaction and chromatographic conditions.", "evidence_ids": ev(4)},
                {"region": "middle-right, Table 4 entries 1-6 and footnotes", "finding": "Six cyclization rows were extracted independently, including solvent and NBS-equivalent footnote overrides and absence of ketone/epoxide branches stated in the prose.", "evidence_ids": ev(4)},
                {"region": "lower columns, mechanistic discussion", "finding": "Mechanistic interpretation was linked to the Scheme 3 mechanism record and not treated as observed intermediates.", "evidence_ids": ev(4)},
            ],
            "record_ids": ids(["scheme2_", "table3_", "table4_", "scheme3_"]),
            "unresolved": ["Generic R-group structures and proposed bromonium intermediates remain unverified."],
        },
        {
            "page": 5,
            "state": "attempted",
            "regions": [
                {"region": "upper-left, Scheme 3", "finding": "The drawing is a proposed mechanism with paths a-c and was classified as mechanism, not as isolated experiments.", "evidence_ids": ev(5)},
                {"region": "lower-left and right column, Experimental Section for 3a and 3b", "finding": "Exact quantities, workup, NMR versus isolated outcomes, product masses, and chromatography were merged into Table 1 entry 14 and Table 2 entry 2 without duplication.", "evidence_ids": ev(5)},
                {"region": "right-column procedures for 4g and 5o", "finding": "Exact quantities, product masses, and stated purification were merged into Table 3 entry 1 and Table 4 entry 1 without duplication.", "evidence_ids": ev(5)},
                {"region": "starting-material paragraph and analytical characterization", "finding": "Cited starting-material methods and spectra are context/identity evidence, not additional reaction batches.", "evidence_ids": ev(5)},
            ],
            "record_ids": [f"{DOC}:scheme3_proposed_mechanism", f"{DOC}:table1_entry14", f"{DOC}:table2_entry2", f"{DOC}:table3_entry1", f"{DOC}:table4_entry1"],
            "unresolved": ["Only representative detailed procedures are present in the main text; procedures for the remaining scope products are in unavailable SI."],
        },
        {
            "page": 6,
            "state": "attempted",
            "regions": [
                {"region": "acknowledgment at upper left", "finding": "No new experiment is reported; it states that Table 1 entry 14 and Table 2 entries 5 and 11 were reproduced, without presenting separate conditions or outcomes.", "evidence_ids": ev(6)},
                {"region": "Supporting Information Available notice at upper right", "finding": "The notice says SI exists online, but no SI file was explicitly supplied or associated; no SI content was imported.", "evidence_ids": ev(6)},
            ],
            "record_ids": [],
            "unresolved": ["Supporting-information association remains unestablished."],
        },
    ],
}

coverage_path = RUN / "coverage" / "pages_0001_0006.json"
coverage_path.parent.mkdir(parents=True, exist_ok=True)
coverage_path.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

data = json.loads(DATASET.read_text())
assert data["documents"][0]["document_id"] == DOC
tasks_path = RUN / "tasks.json"
tasks = json.loads(tasks_path.read_text())
for task in tasks:
    if task["document_id"] == DOC and task["task_id"].endswith(":text"):
        page = int(task["task_id"].split(":page", 1)[1].split(":", 1)[0])
        if 1 <= page <= 6:
            task["state"] = "attempted"
            task["reason"] = "Original page image and extracted text inspected; coverage ledger records findings and unresolved items."
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"records": len(records), "raw": str(raw_path), "coverage": str(coverage_path)}, ensure_ascii=False))
