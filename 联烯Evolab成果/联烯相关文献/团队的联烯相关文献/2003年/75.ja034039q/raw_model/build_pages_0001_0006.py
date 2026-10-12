#!/usr/bin/env python3
"""Build evidence-linked machine records for source.pdf pages 1-6.

This is a raw extraction artifact.  The merge tool remains responsible for
normalization and for enforcing needs_review/unreviewed/unverified states.
"""
from __future__ import annotations

import json
from pathlib import Path

DOC = "doc_eae2cf05b16fe8b6"
BASE = Path(__file__).resolve().parents[1]
OUT = Path(__file__).with_name("extracted_records_pages_0001_0006.json")
COVERAGE = BASE / "coverage" / "pages_0001_0006.json"
TASKS = BASE / "tasks.json"


def evidence(page: int) -> list[str]:
    return [f"{DOC}:page{page}:text", f"{DOC}:page{page}:image"]


def evidence_pages(*pages: int) -> list[str]:
    result: list[str] = []
    for page in pages:
        result.extend(evidence(page))
    return result


def fact(value, pages=(1,)):
    return {
        "value": value,
        "evidence_ids": evidence_pages(*pages) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def field(name, value, pages=(1,), targets=None):
    result = {"name": name, "fact": fact(value, pages)}
    if targets:
        result["target_entity_ids"] = list(targets)
    return result


COMMON_SMILES = {
    "1a": "C=C=C[S](=O)c1ccccc1",
    "iodine": "[I][I]",
    "water": "O",
    "sodium iodide": "[Na+].[I-]",
    "lithium bromide": "[Li+].[Br-]",
    "acetic acid": "CC(=O)O",
    "hydrogen peroxide": "OO",
    "sodium acetate": "[Na+].CC(=O)[O-]",
    "acetic anhydride": "CC(=O)OC(C)=O",
    "lithium acetate dihydrate": "[Li+].CC(=O)[O-].O.O",
    "bromine": "BrBr",
    "NBS": "O=C1CCC(=O)N1Br",
    "copper(II) bromide": "[Cu+2].[Br-].[Br-]",
    "copper(II) chloride dihydrate": "[Cu+2].[Cl-].[Cl-].O.O",
    "triethylamine": "CCN(CC)CC",
    "dichloromethane": "ClCCl",
    "acetonitrile": "CC#N",
    "acetone": "CC(C)=O",
    "THF": "C1CCOC1",
    "DMF": "CN(C)C=O",
    "DMSO": "CS(C)=O",
    "1-hexyne": "CCCCC#C",
    "potassium carbonate": "[K+].[K+].[O-]C([O-])=O",
    "TBAB": "CCCC[N+](CCCC)(CCCC)CCCC.[Br-]",
    "m-CPBA": "O=C(OO)c1cccc(Cl)c1",
}


def participant(entity_id, role, label, pages=(1,), name=None, smiles=None, amounts=None):
    if smiles is None:
        smiles = COMMON_SMILES.get(name or label)
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, pages),
        "name": fact(name, pages) if name is not None else fact(None),
        "smiles": fact(smiles, pages) if smiles is not None else fact(None),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": amounts or [],
    }


def rec(rid, kind, pages, participants, conditions, outcomes, *, notes=None, unresolved=None, source_id=None):
    ids = [p["entity_id"] for p in participants if p["role"] != "product"]
    return {
        "record_id": f"{DOC}:{rid}",
        "document_id": DOC,
        "source_reaction_id": source_id or rid,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": evidence_pages(*pages),
        "participants": participants,
        "steps": [{"step_id": "step1", "participant_ids": ids, "conditions": conditions}],
        "outcomes": outcomes,
        "notes": [fact(n, pages) for n in (notes or [])],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved or [
                "Supporting information was not supplied or explicitly associated.",
                "Machine extraction requires source review; structures are not verified.",
            ],
        },
    }


def q(number, unit, **extra):
    value = {"number": number, "unit": unit}
    value.update(extra)
    return value


records = []


# Pages 1-2: introductory examples, generic route, equation 1, and Table 1.
records.append(rec(
    "scheme2_nai_30pct", "literature_example", (1, 2),
    [participant("s2_1a", "reactant", "1a", (1, 2)),
     participant("s2_nai", "reagent", "NaI", (1, 2), name="sodium iodide"),
     participant("s2_hoac", "solvent", "HOAc", (1, 2), name="acetic acid"),
     participant("s2_z2aa", "product", "Z-2aa", (1, 2), name="3-thiophenyl-2-iodo-2(Z)-propenyl acetate")],
    [field("temperature", q(80, "°C"), (1, 2)), field("time", None), field("solvent", "HOAc", (1, 2))],
    [field("yield", q(30, "%"), (1, 2), ["s2_z2aa"]), field("yield_measurement_basis", None, targets=["s2_z2aa"])],
    unresolved=["The introductory 30% result differs from the 41% anhydrous-HOAc entry in Scheme 3; they are retained as separate source conditions.", "Reaction time and yield basis are not reported in this region.", "Supporting information association is unestablished."],
))
records.append(rec(
    "scheme2_oxidation", "literature_example", (2,),
    [participant("s2ox_z2aa", "reactant", "Z-2aa", (2,)),
     participant("s2ox_h2o2", "reagent", "H2O2", (2,), name="hydrogen peroxide"),
     participant("s2ox_hoac", "solvent", "HOAc", (2,), name="acetic acid"),
     participant("s2ox_prod", "product", "Z-2aa'", (2,), name="Z-2-iodo-3-(phenylsulfinyl)-2-propenyl acetate")],
    [field("temperature", None), field("time", None), field("solvent", "HOAc", (2,))],
    [field("yield", None, targets=["s2ox_prod"]), field("yield_measurement_basis", None, targets=["s2ox_prod"])],
    unresolved=["Scheme 2 gives no time, temperature, amount, or yield for this oxidation.", "Supporting information association is unestablished."],
))
records.append(rec(
    "scheme2_esterification", "literature_example", (2,),
    [participant("s2est_e3aa", "reactant", "E-3aa", (2,)),
     participant("s2est_naoac", "reagent", "NaOAc", (2,), name="sodium acetate"),
     participant("s2est_ac2o", "reagent", "Ac2O", (2,), name="acetic anhydride"),
     participant("s2est_prod", "product", "E-2aa'", (2,), name="E-2-iodo-3-(phenylsulfinyl)-2-propenyl acetate")],
    [field("temperature", None), field("time", None), field("solvent", None)],
    [field("yield", None, targets=["s2est_prod"]), field("yield_measurement_basis", None, targets=["s2est_prod"])],
    unresolved=["Scheme 2 gives no time, temperature, solvent, amount, or yield for this esterification.", "Supporting information association is unestablished."],
))

for suffix, salt_label, salt_name, product, yield_value in [
    ("nai", "NaI", "sodium iodide", "Z-2aa", 41),
    ("libr", "LiBr", "lithium bromide", "Z-2ab", 55),
]:
    records.append(rec(
        f"scheme3_{suffix}", "literature_example", (2,),
        [participant(f"s3_{suffix}_1a", "reactant", "1a", (2,)),
         participant(f"s3_{suffix}_salt", "reagent", salt_label, (2,), name=salt_name),
         participant(f"s3_{suffix}_hoac", "solvent", "anhydrous HOAc", (2,), name="acetic acid"),
         participant(f"s3_{suffix}_prod", "product", product, (2,))],
        [field("temperature", "heated", (2,)), field("time", None), field("solvent", "anhydrous HOAc", (2,))],
        [field("yield", q(yield_value, "%"), (2,), [f"s3_{suffix}_prod"]), field("yield_measurement_basis", None, targets=[f"s3_{suffix}_prod"])],
        unresolved=["Scheme 3 specifies heating but does not give a numeric temperature or reaction time.", "Yield basis is not stated.", "Supporting information association is unestablished."],
    ))

records.append(rec(
    "scheme4_generic_halohydroxylation", "general_scheme", (2,),
    [participant("s4_allene", "reactant", "generic 1,2-allenyl phenyl sulfoxide", (2,)),
     participant("s4_x", "reagent", "X+", (2,)),
     participant("s4_water", "reagent", "H2O", (2,), name="water"),
     participant("s4_mecn", "solvent", "CH3CN", (2,), name="acetonitrile"),
     participant("s4_product", "product", "generic E-2-halo-3-hydroxy-1-alkenyl sulfoxide", (2,))],
    [field("temperature", None), field("time", None), field("solvent", "CH3CN", (2,))],
    [field("stereochemical_outcome", "E-selective product family", (2,), ["s4_product"]), field("yield", None, targets=["s4_product"])],
    unresolved=["This is a generic synthetic concept with R groups, not a single quantified experiment.", "Halogen source, time, temperature, and yield are unspecified."],
))

records.append(rec(
    "eq1_e3aa", "reported_experiment", (2, 3),
    [participant("eq1_1a", "reactant", "1a", (2, 3)),
     participant("eq1_i2", "reagent", "I2", (2, 3), name="iodine"),
     participant("eq1_lioac", "reagent", "LiOAc·2H2O", (2, 3), name="lithium acetate dihydrate"),
     participant("eq1_water", "reagent", "H2O", (2, 3), name="water"),
     participant("eq1_mecn", "solvent", "MeCN", (2, 3), name="acetonitrile"),
     participant("eq1_product", "product", "E-3aa", (2, 3), name="E-2-iodo-3-(phenylsulfinyl)-2-propen-1-ol")],
    [field("temperature", "r.t.", (2, 3)), field("time", q(1, "h"), (2,)), field("solvent", "MeCN/H2O (7:1)", (2,))],
    [field("yield", q(96, "%"), (2, 3), ["eq1_product"]), field("stereochemical_outcome", "E", (2,), ["eq1_product"]), field("yield_measurement_basis", None, targets=["eq1_product"])],
    unresolved=["The page-2 equation does not state reagent amounts or yield basis.", "The later detailed procedure is outside this six-page visual coverage and is not used to claim completeness.", "Supporting information association is unestablished."],
))

table1 = [
    (1, "1b", "E-3ab", 1.6, 1.5, 87), (2, "1c", "E-3ac", 1.6, 2, 89),
    (3, "1d", "E-3ad", 1.6, 1, 89), (4, "1e", "E-3ae", 1.2, 3.2, 87),
    (5, "1f", "E-3af", 1.2, 0.5, 87), (6, "1g", "E-3ag", 1.2, 0.3, 74),
    (7, "1h", "E-3ah", 1.6, 1.5, 82), (8, "1i", "E-3ai", 1.6, 2.2, 79),
    (9, "1j", "E-3aj", 1.2, 1.3, 88), (10, "1k", "E-3ak", 1.6, 1, 82),
    (11, "1l", "E-3al", 1.6, 1, 92),
]
for entry, substrate, product, equiv, time_h, yield_value in table1:
    prefix = f"t1e{entry}"
    records.append(rec(
        f"table1_entry_{entry:02d}", "substrate_scope_entry", (2,),
        [participant(f"{prefix}_sub", "reactant", substrate, (2,)),
         participant(f"{prefix}_i2", "reagent", "I2", (2,), name="iodine", amounts=[field("equivalents", q(equiv, "equiv"), (2,))]),
         participant(f"{prefix}_lioac", "reagent", "LiOAc·2H2O", (2,), name="lithium acetate dihydrate"),
         participant(f"{prefix}_water", "reagent", "H2O", (2,), name="water"),
         participant(f"{prefix}_mecn", "solvent", "MeCN", (2,), name="acetonitrile"),
         participant(f"{prefix}_prod", "product", product, (2,))],
        [field("temperature", "r.t.", (2,)), field("time", q(time_h, "h"), (2,)), field("solvent", "MeCN/H2O (7:1)", (2,))],
        [field("yield", q(yield_value, "%"), (2,), [f"{prefix}_prod"]), field("stereochemical_outcome", "E", (2,), [f"{prefix}_prod"]), field("yield_measurement_basis", None, targets=[f"{prefix}_prod"])],
        unresolved=["Table 1 does not report substrate/reagent masses, reaction scale, or yield basis.", "Generic table structures are retained by source labels; structures are unverified.", "Supporting information association is unestablished."],
    ))


# Page 3: control reactions and the 1m mechanistic experiment.
records.append(rec(
    "scheme6_allene_diiodination", "reported_experiment", (3,),
    [participant("s6a_sub", "reactant", "n-C7H15-substituted allene", (3,)),
     participant("s6a_i2", "reagent", "I2", (3,), name="iodine"),
     participant("s6a_water", "reagent", "H2O", (3,), name="water"),
     participant("s6a_lioac", "reagent", "LiOAc·2H2O", (3,), name="lithium acetate dihydrate"),
     participant("s6a_prod", "product", "4", (3,), name="1,2-diiodo-2-decene")],
    [field("temperature", "r.t.", (3,)), field("time", q(1, "h"), (3,)), field("solvent", "aqueous MeCN", (3,))],
    [field("yield", q(66, "%"), (3,), ["s6a_prod"]), field("Z_E_ratio", "88:12", (3,), ["s6a_prod"]), field("yield_measurement_basis", None, targets=["s6a_prod"])],
    unresolved=["Reagent quantities and yield basis are not shown in Scheme 6.", "The full stereochemical structure is not encoded as SMILES."],
))
records.append(rec(
    "scheme6_allenoate_unidentified", "reported_experiment", (3,),
    [participant("s6b_sub", "reactant", "n-C6H13-substituted ethyl 2,3-allenoate", (3,)),
     participant("s6b_i2", "reagent", "I2", (3,), name="iodine"),
     participant("s6b_water", "reagent", "H2O", (3,), name="water"),
     participant("s6b_lioac", "reagent", "LiOAc·2H2O", (3,), name="lithium acetate dihydrate"),
     participant("s6b_prod", "product", "unidentified mixture", (3,))],
    [field("temperature", "r.t.", (3,)), field("time", q(1, "h"), (3,)), field("solvent", "aqueous MeCN", (3,))],
    [field("reaction_outcome", "unidentified mixture", (3,), ["s6b_prod"]), field("yield", None, targets=["s6b_prod"])],
    unresolved=["Products and product yields are not identified.", "Reagent quantities are not shown in Scheme 6."],
))
records.append(rec(
    "scheme6_sulfone_no_reaction", "reported_experiment", (3,),
    [participant("s6c_sub", "reactant", "5a", (3,), name="1,2-allenic sulfone"),
     participant("s6c_i2", "reagent", "I2", (3,), name="iodine"),
     participant("s6c_lioac", "reagent", "LiOAc·2H2O", (3,), name="lithium acetate dihydrate")],
    [field("temperature", {"minimum": 55, "maximum": 60, "unit": "°C", "raw_text": "55-60 °C"}, (3,)), field("time", q(1, "h"), (3,)), field("solvent", "MeCN/H2O (7:1)", (3,))],
    [field("reaction_outcome", "no reaction", (3,), ["s6c_sub"]), field("starting_material_recovered", q(80, "%"), (3,), ["s6c_sub"])],
    unresolved=["Reagent quantities and recovery measurement basis are not stated."],
))
records.append(rec(
    "scheme7_1m_to_e3am", "reported_experiment", (3,),
    [participant("s7_sub", "reactant", "1m", (3,)),
     participant("s7_i2", "reagent", "I2", (3,), name="iodine", amounts=[field("equivalents", q(1.2, "equiv"), (3,))]),
     participant("s7_lioac", "reagent", "LiOAc·2H2O", (3,), name="lithium acetate dihydrate"),
     participant("s7_prod", "product", "E-3am", (3,))],
    [field("temperature", "r.t.", (3,)), field("time", None), field("solvent", "MeCN/H2O (7:1)", (3,))],
    [field("yield", q(97, "%"), (3,), ["s7_prod"]), field("sulfur_configuration_outcome", "inversion", (3,), ["s7_prod"]), field("yield_measurement_basis", None, targets=["s7_prod"])],
    unresolved=["Scheme 7 does not give reaction time, scale, or yield basis.", "Absolute structures are shown but machine SMILES are not assigned."],
))
records.append(rec(
    "scheme7_proposed_mechanism", "mechanism", (3,),
    [participant("s7m_start", "reactant", "1m", (3,)), participant("s7m_i6", "unspecified_agent", "iodonium intermediate 6", (3,)), participant("s7m_i7", "unspecified_agent", "five-membered cyclic intermediate 7", (3,)), participant("s7m_water", "reagent", "H2O", (3,), name="water"), participant("s7m_prod", "product", "E-3am", (3,))],
    [field("operation", "proposed iodonium formation, intramolecular sulfinyl-oxygen attack, then hydrolysis", (3,)), field("temperature", None), field("time", None)],
    [field("mechanistic_outcome", "stereospecific sulfur-center inversion", (3,), ["s7m_prod"])],
    unresolved=["Intermediates 6 and 7 are proposed, not isolated reported products.", "This mechanism record must not be counted as an independent yield experiment."],
))


# Page 4: Scheme 8, Tables 2-4, Scheme 9, and Scheme 10.
for suffix, substrate, product, solvent, yield_value in [
    ("1n", "1n", "E-3an", "H2O/CH3CN", 82),
    ("1o", "1o", "E-3ao", "CH3CN/H2O", 85),
]:
    records.append(rec(
        f"scheme8_{suffix}", "reported_experiment", (4,),
        [participant(f"s8_{suffix}_sub", "reactant", substrate, (4,)), participant(f"s8_{suffix}_i2", "reagent", "I2", (4,), name="iodine"), participant(f"s8_{suffix}_lioac", "reagent", "LiOAc·2H2O", (4,), name="lithium acetate dihydrate"), participant(f"s8_{suffix}_prod", "product", product, (4,))],
        [field("temperature", "r.t.", (4,)), field("time", q(1, "h"), (4,)), field("solvent", solvent, (4,))],
        [field("yield", q(yield_value, "%"), (4,), [f"s8_{suffix}_prod"]), field("yield_measurement_basis", None, targets=[f"s8_{suffix}_prod"])],
        unresolved=["Scheme 8 does not report reagent quantities, reaction scale, or yield basis.", "Product structures remain unverified."],
    ))

table2 = [
    (1, "1a", "CuBr2", "E-3ba", 1.5, {"minimum": 40, "maximum": 45, "unit": "°C", "raw_text": "40-45 °C"}, 88),
    (2, "1c", "NBS", "E-3bc", 2, "r.t.", 90),
    (3, "1d", "NBS", "E-3bd", 2, "r.t.", 98),
    (4, "1e", "CuBr2", "E-3be", 2.5, None, 87),
    (5, "1f", "NBS", "E-3bf", 0.5, "r.t.", 68),
    (6, "1h", "CuBr2", "E-3bh", 3.5, None, 86),
    (7, "1j", "CuBr2", "E-3bj", 1, None, 92),
    (8, "1m", "CuBr2", "E-3bm", 1.5, None, 95),
]
for entry, substrate, reagent, product, time_h, temperature, yield_value in table2:
    prefix = f"t2e{entry}"
    reagent_name = "NBS" if reagent == "NBS" else "copper(II) bromide"
    parts = [participant(f"{prefix}_sub", "reactant", substrate, (4,)), participant(f"{prefix}_halogen", "reagent", reagent, (4,), name=reagent_name)]
    solvent = "MeCN/H2O" if reagent == "NBS" else "acetone/H2O"
    if reagent == "NBS":
        parts.append(participant(f"{prefix}_lioac", "reagent", "LiOAc·2H2O", (4,), name="lithium acetate dihydrate"))
    parts += [participant(f"{prefix}_solv", "solvent", solvent, (4,)), participant(f"{prefix}_prod", "product", product, (4,))]
    records.append(rec(
        f"table2_entry_{entry:02d}", "substrate_scope_entry", (4,), parts,
        [field("temperature", temperature, (4,)) if temperature is not None else field("temperature", None), field("time", q(time_h, "h"), (4,)), field("solvent", solvent, (4,))],
        [field("yield", q(yield_value, "%"), (4,), [f"{prefix}_prod"]), field("stereochemical_outcome", "E", (4,), [f"{prefix}_prod"]), field("yield_measurement_basis", None, targets=[f"{prefix}_prod"])],
        unresolved=["Table 2 does not state reaction scale, reagent amounts, or yield basis.", *( ["Temperature is not printed for this CuBr2 row and is left missing."] if temperature is None else []), "Structures are retained by source labels and remain unverified."],
    ))

records.append(rec(
    "scheme9_solution_chlorohydroxylation", "optimization_entry", (4,),
    [participant("s9a_sub", "reactant", "1g", (4,)), participant("s9a_cucl2", "reagent", "CuCl2·2H2O", (4,), name="copper(II) chloride dihydrate", amounts=[field("equivalents", q(4, "equiv"), (4,))]), participant("s9a_solvent", "solvent", "acetone/water (2:1)", (4,)), participant("s9a_prod", "product", "E-3cg", (4,))],
    [field("temperature", "r.t.", (4,)), field("time", q(48, "h"), (4,)), field("solvent", "acetone/water (2:1)", (4,))],
    [field("yield", q(20, "%"), (4,), ["s9a_prod"]), field("starting_material_recovered", q(72, "%"), (4,), ["s9a_sub"]), field("yield_measurement_basis", None, targets=["s9a_prod"])],
    unresolved=["Yield and recovery measurement bases are not stated.", "No higher-temperature product was isolated in the prose, but that separate qualitative observation lacks a fully specified temperature/time combination."],
))
records.append(rec(
    "scheme9_table3_entry_04", "optimization_entry", (4,),
    [participant("s9b_sub", "reactant", "1g", (4,)), participant("s9b_cucl2", "reagent", "CuCl2·2H2O", (4,), name="copper(II) chloride dihydrate", amounts=[field("equivalents", q(4, "equiv"), (4,))]), participant("s9b_silica", "unspecified_agent", "silica gel", (4,)), participant("s9b_prod", "product", "E-3cg", (4,))],
    [field("operation", "mixed and milled four times with intermittent heating", (4,)), field("heating_program", "room temperature to 65 °C", (4,)), field("time", None), field("solvent", "no solvent", (4,))],
    [field("yield", q(73, "%"), (4,), ["s9b_prod"]), field("yield_measurement_basis", None, targets=["s9b_prod"])],
    unresolved=["The duration of each milling/heating cycle and yield basis are not reported.", "This Scheme 9 experiment is the same as Table 3 entry 4 and is represented once."],
))

table3 = [(1, "1a", "E-3ca", 49), (2, "1e", "E-3ce", 84), (3, "1f", "E-3cf", 61), (5, "1h", "E-3ch", 51)]
for entry, substrate, product, yield_value in table3:
    prefix = f"t3e{entry}"
    records.append(rec(
        f"table3_entry_{entry:02d}", "substrate_scope_entry", (4,),
        [participant(f"{prefix}_sub", "reactant", substrate, (4,)), participant(f"{prefix}_cucl2", "reagent", "CuCl2·2H2O", (4,), name="copper(II) chloride dihydrate", amounts=[field("equivalents", q(4, "equiv"), (4,))]), participant(f"{prefix}_silica", "unspecified_agent", "silica gel", (4,)), participant(f"{prefix}_prod", "product", product, (4,))],
        [field("operation", "solventless milling with silica gel and intermittent heating", (4,)), field("heating_program", "room temperature to 65 °C", (4,)), field("time", None), field("solvent", "no solvent", (4,))],
        [field("yield", q(yield_value, "%"), (4,), [f"{prefix}_prod"]), field("stereochemical_outcome", "E", (4,), [f"{prefix}_prod"]), field("yield_measurement_basis", None, targets=[f"{prefix}_prod"])],
        unresolved=["Table 3 does not state reaction scale, milling duration, or yield basis.", "Structures are retained by source labels and remain unverified."],
    ))

table4 = [
    (1, "(R)-1c", 96, "I2", "(R)-3ac", 98, 95, False),
    (2, "(R)-1c", 96, "Br2", "(R)-3bc", 96, 96, False),
    (3, "(R)-1c", 96, "CuBr2", "(R)-3bc", 92, 97, False),
    (4, "(S)-1d", 96, "Br2", "(S)-3bd", 99, 97, False),
    (5, "(S)-1d", 96, "CuBr2", "(S)-3bd", 97, 96, False),
    (6, "(S)-1e", ">99", "I2", "(S)-3ae", 88, ">99", False),
    (7, "(S)-1e", ">99", "Br2", "(S)-3be", 85, ">99", False),
    (8, "(S)-1e", ">99", "CuBr2", "(S)-3be", 69, ">99", False),
    (9, "(S)-1e", ">99", "CuCl2·2H2O", "(S)-3ce", 82, ">99", True),
]


def ee_value(value):
    if value == ">99":
        return q(99, "%", qualifier="gt", raw_text=">99%")
    return q(value, "%")


for entry, substrate, sub_ee, source, product, yield_value, prod_ee, solventless in table4:
    prefix = f"t4e{entry}"
    name_map = {"I2": "iodine", "Br2": "bromine", "CuBr2": "copper(II) bromide", "CuCl2·2H2O": "copper(II) chloride dihydrate"}
    parts = [participant(f"{prefix}_sub", "reactant", substrate, (4,), amounts=[field("starting_material_ee", ee_value(sub_ee), (4,))]), participant(f"{prefix}_source", "reagent", source, (4,), name=name_map[source]), participant(f"{prefix}_prod", "product", product, (4,))]
    records.append(rec(
        f"table4_entry_{entry:02d}", "substrate_scope_entry", (4,), parts,
        [field("temperature", "r.t.", (4,)), field("time", None), field("solvent", "no solvent", (4,)) if solventless else field("solvent", None)],
        [field("isolated_yield", q(yield_value, "%"), (4,), [f"{prefix}_prod"]), field("product_ee", ee_value(prod_ee), (4,), [f"{prefix}_prod"]), field("yield_measurement_basis", "isolated", (4,), [f"{prefix}_prod"])],
        unresolved=["Table 4 does not report time, reaction scale, or reagent amounts.", *( ["The footnote states solventless conditions; milling details are not printed in this table row."] if solventless else ["Solvent is not specified in Table 4 and is left missing."]), "Structures and absolute configurations remain machine-unverified."],
    ))

scheme10 = [
    ("a", "(R)-A", "R2=n-C4H9, R3=H", 96, "(R)-1c", 84, 95.5),
    ("b", "(S)-B", "R2=H, R3=n-C8H17", 96, "(S)-1d", 86, 95.7),
    ("c", "(S)-C", "R2=H, R3=t-C4H9", ">99", "(S)-1e", 89, ">99"),
]
for suffix, substrate, substituents, start_ee, product, yield_value, prod_ee in scheme10:
    prefix = f"s10{suffix}"
    records.append(rec(
        f"scheme10_starting_material_{suffix}", "reported_experiment", (4,),
        [participant(f"{prefix}_sub", "reactant", substrate, (4,), name=f"optically active propargylic alcohol ({substituents})", amounts=[field("starting_material_ee", ee_value(start_ee), (4,))]), participant(f"{prefix}_rscl", "reagent", "RSCl", (4,), name="sulfinyl chloride"), participant(f"{prefix}_et3n", "reagent", "Et3N", (4,), name="triethylamine"), participant(f"{prefix}_solv", "solvent", "CH2Cl2", (4,), name="dichloromethane"), participant(f"{prefix}_prod", "product", product, (4,))],
        [field("temperature", {"minimum": -85, "maximum": -80, "unit": "°C", "raw_text": "-80 to -85 °C"}, (4,)), field("time", None), field("solvent", "CH2Cl2", (4,))],
        [field("yield", q(yield_value, "%"), (4,), [f"{prefix}_prod"]), field("product_ee", ee_value(prod_ee), (4,), [f"{prefix}_prod"]), field("yield_measurement_basis", None, targets=[f"{prefix}_prod"])],
        unresolved=["Scheme 10 does not give reagent amounts, reaction time, or yield basis.", "RSCl is retained as the printed generic reagent label; its R group is not inferred."],
    ))


# Page 5: equation 2, Suzuki variants, Table 5, and equation 3.
records.append(rec(
    "eq2_sonogashira", "reported_experiment", (5,),
    [participant("eq2_sub", "reactant", "E-3aa", (5,)), participant("eq2_alkyne", "reactant", "CH3(CH2)3C≡CH", (5,), name="1-hexyne"), participant("eq2_pd", "catalyst", "Pd(PPh3)2Cl2", (5,)), participant("eq2_cui", "catalyst", "CuI", (5,)), participant("eq2_et3n", "solvent", "Et3N", (5,), name="triethylamine"), participant("eq2_dmso", "solvent", "DMSO", (5,), name="DMSO"), participant("eq2_prod", "product", "Z-4g", (5,))],
    [field("temperature", {"minimum": 40, "maximum": 45, "unit": "°C", "raw_text": "40-45 °C"}, (5,)), field("time", q(5, "h"), (5,)), field("solvent", "Et3N/DMSO", (5,))],
    [field("yield", q(92, "%"), (5,), ["eq2_prod"]), field("stereochemical_outcome", "Z", (5,), ["eq2_prod"]), field("yield_measurement_basis", None, targets=["eq2_prod"])],
    unresolved=["Equation 2 does not report reagent/catalyst amounts, reaction scale, or yield basis."],
))

for suffix, tbab, yield_value, ratio in [("without_tbab", None, 70, "20:80"), ("with_tbab", 10, 90, "3:97")]:
    prefix = f"s11ph_{suffix}"
    parts = [participant(f"{prefix}_sub", "reactant", "E-3aa", (5,)), participant(f"{prefix}_boron", "reactant", "phenylboronic acid", (5,)), participant(f"{prefix}_pd", "catalyst", "Pd(PPh3)4", (5,)), participant(f"{prefix}_base", "reagent", "K2CO3", (5,), name="potassium carbonate"), participant(f"{prefix}_thf", "solvent", "THF", (5,), name="THF")]
    if tbab is not None:
        parts.append(participant(f"{prefix}_tbab", "reagent", "TBAB", (5,), name="TBAB", amounts=[field("loading", q(tbab, "mol%"), (5,))]))
    parts.append(participant(f"{prefix}_prod", "product", "4a", (5,)))
    records.append(rec(
        f"scheme11_phenyl_{suffix}", "optimization_entry", (5,), parts,
        [field("temperature", "reflux", (5,)), field("time", q(3, "h"), (5,)) if tbab is not None else field("time", None), field("solvent", "THF", (5,))],
        [field("yield", q(yield_value, "%"), (5,), [f"{prefix}_prod"]), field("E_Z_ratio", ratio, (5,), [f"{prefix}_prod"]), field("yield_measurement_basis", None, targets=[f"{prefix}_prod"])],
        unresolved=[*( ["The no-TBAB prose result does not state reaction time."] if tbab is None else []), "Reaction scale, participant amounts other than TBAB loading, and yield basis are not stated."],
    ))

records.append(rec(
    "scheme11_hexenyl_suzuki", "reported_experiment", (5,),
    [participant("s11h_sub", "reactant", "E-3aa", (5,)), participant("s11h_boron", "reactant", "E-1-hexenylboronic acid", (5,)), participant("s11h_pd", "catalyst", "Pd(PPh3)4", (5,)), participant("s11h_base", "reagent", "K2CO3", (5,), name="potassium carbonate"), participant("s11h_tbab", "reagent", "TBAB", (5,), name="TBAB"), participant("s11h_thf", "solvent", "THF", (5,), name="THF"), participant("s11h_prod", "product", "Z-4h", (5,))],
    [field("temperature", "reflux", (5,)), field("time", q(3, "h"), (5,)), field("solvent", "THF", (5,))],
    [field("yield", q(90, "%"), (5,), ["s11h_prod"]), field("stereochemical_outcome", "Z", (5,), ["s11h_prod"]), field("yield_measurement_basis", None, targets=["s11h_prod"])],
    unresolved=["Scheme 11 does not state TBAB loading for this arrow, reaction scale, other participant amounts, or yield basis."],
))

table5 = [
    (1, "E-3aa", "PhZnBr", "THF", 3, 0, "Z-4a", None, None, None),
    (2, "E-3aa", "PhZnBr", "THF/DMF", 1, 94, "Z-4a", None, None, None),
    (3, "E-3ah", "PhZnBr", "THF/DMF", 2, 82, "Z-4b", None, None, None),
    (4, "E-3ac", "PhZnBr", "THF/DMF", 1, 71, "Z-4c", None, None, None),
    (5, "(R)-E-3ac", "PhZnBr", "THF/DMF", 1, 74, "(R)-Z-4c", 97.1, 99.1, None),
    (6, "E-3ad", "PhZnBr", "THF/DMF", 2, 76, "Z-4d", None, None, None),
    (7, "E-3ad", "PhZnBr", "THF/DMF", 2, 78, "(R)-Z-4d", None, 98.1, 94.0),
    (8, "E-3ad", "PhZnBr", "THF/DMF", 2, 77, "(S)-Z-4d", None, 94.7, 95.7),
    (9, "E-3aa", "EtZnBr", "THF/DMF", 1, 86, "Z-4e", None, None, None),
    (10, "E-3aa", "PhC2ZnBr", "THF/DMF", 7, 0, "Z-4f", None, None, None),
    (11, "E-3aa", "PhC2ZnBr", "THF/HMPA", 1.5, 94, "Z-4f", None, None, None),
    (12, "E-3ba", "PhC2ZnBr", "THF/HMPA", 1.5, 92, "Z-4f", None, None, None),
]
for entry, substrate, orgzn, solvent, time_h, yield_value, product, sub_ee, prod_ee, precursor_ee in table5:
    prefix = f"t5e{entry}"
    amounts = [field("starting_material_ee", q(sub_ee, "%"), (5,))] if sub_ee is not None else []
    parts = [participant(f"{prefix}_sub", "reactant", substrate, (5,), amounts=amounts), participant(f"{prefix}_orgzn", "reagent", orgzn, (5,)), participant(f"{prefix}_pd", "catalyst", "Pd(PPh3)4", (5,)), participant(f"{prefix}_solv", "solvent", solvent, (5,)), participant(f"{prefix}_prod", "product", product, (5,))]
    outcomes = [field("yield", q(yield_value, "%"), (5,), [f"{prefix}_prod"]), field("stereochemical_outcome", "Z", (5,), [f"{prefix}_prod"]), field("yield_measurement_basis", None, targets=[f"{prefix}_prod"])]
    if prod_ee is not None:
        outcomes.append(field("product_ee", q(prod_ee, "%"), (5,), [f"{prefix}_prod"]))
    if precursor_ee is not None:
        outcomes.append(field("propargylic_alcohol_precursor_ee", q(precursor_ee, "%"), (5,)))
    records.append(rec(
        f"table5_entry_{entry:02d}", "optimization_entry", (5,), parts,
        [field("temperature", "r.t.", (5,)), field("time", q(time_h, "h"), (5,)), field("solvent", solvent, (5,))], outcomes,
        unresolved=["Table 5 does not report reaction scale, organozinc amount, catalyst loading, or yield basis.", *( ["The precursor ee belongs to the propargylic alcohol used upstream, not directly to the coupling substrate."] if precursor_ee is not None else []), "Structures and stereochemical assignments remain machine-unverified."],
    ))

records.append(rec(
    "eq3_tbs_negishi", "reported_experiment", (5,),
    [participant("eq3_sub", "reactant", "E-3aa-TBS", (5,)), participant("eq3_orgzn", "reagent", "PhC2ZnBr", (5,)), participant("eq3_pd", "catalyst", "Pd(PPh3)4", (5,)), participant("eq3_thf", "solvent", "THF", (5,), name="THF"), participant("eq3_prod", "product", "Z-4f-TBS", (5,))],
    [field("temperature", None), field("time", None), field("solvent", "THF", (5,))],
    [field("yield", q(94, "%"), (5,), ["eq3_prod"]), field("stereochemical_outcome", "Z", (5,), ["eq3_prod"]), field("yield_measurement_basis", None, targets=["eq3_prod"])],
    unresolved=["Equation 3 does not report reaction scale, amounts, catalyst loading, temperature, time, or yield basis."],
))


# Page 6: Tables 6-8, Scheme 13, equation 4, and equation 5.
table6 = [
    (1, "NiCl2(PPh3)2", "E-3aa", "Z-5c", 1, 1.3, 77, 80, None, None),
    (2, "NiCl2(dppe)", "E-3aa", "Z-5c", 1, 2, 40, 80, None, None),
    (3, "Ni(acac)2", "E-3aa", "Z-5c", 1, 4.5, 84, 80, None, None),
    (4, "Ni(acac)2", "E-3ad", "Z-5e", 1.2, 11, 44, 80, None, None),
    (5, "Ni(acac)2", "E-3ad", "(S)-Z-5e", 1, 4, 34, 80, 95.4, 95.7),
    (6, "Ni(acac)2", "E-3ad", "Z-5e", 1.6, 12, 54, 40, None, None),
]
for entry, ni, substrate, product, time1, time2, yield_value, temp2, prod_ee, precursor_ee in table6:
    prefix = f"t6e{entry}"
    parts = [participant(f"{prefix}_sub", "reactant", substrate, (6,)), participant(f"{prefix}_orgzn", "reagent", "PhZnBr", (6,), amounts=[field("equivalents", q(5, "equiv"), (6,))]), participant(f"{prefix}_pd", "catalyst", "Pd(PPh3)4", (6,)), participant(f"{prefix}_ni", "catalyst", ni, (6,)), participant(f"{prefix}_solv", "solvent", "THF/DMF", (6,)), participant(f"{prefix}_prod", "product", product, (6,))]
    outcomes = [field("yield", q(yield_value, "%"), (6,), [f"{prefix}_prod"]), field("stereochemical_outcome", "Z", (6,), [f"{prefix}_prod"]), field("yield_measurement_basis", None, targets=[f"{prefix}_prod"])]
    if prod_ee is not None:
        outcomes.append(field("product_ee", q(prod_ee, "%"), (6,), [f"{prefix}_prod"]))
        outcomes.append(field("propargylic_alcohol_precursor_ee", q(precursor_ee, "%"), (6,)))
    record = rec(
        f"table6_entry_{entry:02d}", "optimization_entry", (6,), parts,
        [field("step_one_temperature", "r.t.", (6,)), field("step_one_time", q(time1, "h"), (6,)), field("step_two_temperature", q(temp2, "°C"), (6,)), field("step_two_time", q(time2, "h"), (6,)), field("solvent", "THF/DMF", (6,))], outcomes,
        unresolved=["Table 6 does not report reaction scale, catalyst loadings, or yield basis.", *( ["The precursor ee belongs to an upstream propargylic alcohol."] if precursor_ee is not None else []), "Structures remain machine-unverified."],
    )
    record["steps"] = [
        {"step_id": "step1_pd_c_i_coupling", "participant_ids": [f"{prefix}_sub", f"{prefix}_orgzn", f"{prefix}_pd", f"{prefix}_solv"], "conditions": [field("temperature", "r.t.", (6,)), field("time", q(time1, "h"), (6,)), field("solvent", "THF/DMF", (6,))]},
        {"step_id": "step2_ni_c_s_coupling", "participant_ids": [f"{prefix}_orgzn", f"{prefix}_ni", f"{prefix}_solv"], "conditions": [field("temperature", q(temp2, "°C"), (6,)), field("time", q(time2, "h"), (6,)), field("solvent", "THF/DMF", (6,))]},
    ]
    records.append(record)

records.append(rec(
    "scheme13_ni_only_mixture", "optimization_entry", (6,),
    [participant("s13_sub", "reactant", "E-3aa", (6,)), participant("s13_orgzn", "reagent", "PhZnBr", (6,), amounts=[field("equivalents", q(5, "equiv"), (6,))]), participant("s13_ni", "catalyst", "Ni(acac)2", (6,)), participant("s13_solv", "solvent", "THF/DMF", (6,)), participant("s13_z4a", "product", "Z-4a", (6,)), participant("s13_z5c", "product", "Z-5c", (6,)), participant("s13_other", "product", "other byproducts", (6,))],
    [field("temperature", None), field("time", None), field("solvent", "THF/DMF", (6,))],
    [field("reaction_outcome", "mixture of Z-4a, Z-5c, and other byproducts", (6,), ["s13_z4a", "s13_z5c", "s13_other"]), field("yield", None, targets=["s13_z4a", "s13_z5c"])],
    unresolved=["Scheme 13 does not report temperature, time, scale, catalyst loading, or component yields."],
))

records.append(rec(
    "eq4_hydroxyl_control", "reported_experiment", (6,),
    [participant("eq4_e3aa", "reactant", "E-3aa", (6,), amounts=[field("amount", q(0.4, "mmol"), (6,))]), participant("eq4_control", "reactant", "2-phenylethenyl phenyl sulfoxide", (6,), amounts=[field("amount", q(0.4, "mmol"), (6,))]), participant("eq4_orgzn", "reagent", "PhZnBr", (6,), amounts=[field("equivalents", q(9, "equiv"), (6,))]), participant("eq4_ni", "catalyst", "Ni(acac)2", (6,)), participant("eq4_solv", "solvent", "DMF/THF (1:1)", (6,)), participant("eq4_z5c", "product", "Z-5c", (6,)), participant("eq4_stilbene", "product", "stilbene", (6,))],
    [field("temperature", None), field("time", None), field("solvent", "DMF/THF (1:1)", (6,))],
    [field("yield", q(85, "%"), (6,), ["eq4_z5c"]), field("yield", q(24, "%"), (6,), ["eq4_stilbene"]), field("yield_measurement_basis", None, targets=["eq4_z5c", "eq4_stilbene"])],
    unresolved=["Equation 4 does not report temperature, time, catalyst loading, or yield basis."],
))

table7 = [
    (1, "Z-4a", "p-Cl", 80, 1.5, 68, "Z-5a", None, None),
    (2, "Z-4a", "p-OMe", 80, 3, 73, "Z-5b", None, None),
    (3, "Z-4a", "H", 40, 15.5, 84, "Z-5c", None, None),
    (4, "Z-4a", "o-OMe", 40, 15, 68, "Z-5d", None, None),
    (5, "Z-4d", "H", 40, 15, 69, "Z-5e", None, None),
    (6, "(S)-Z-4d", "H", 40, 12, 64, "(S)-Z-5e", 94.7, 95.6),
    (7, "Z-4d", "p-OMe", 40, 19, 60, "Z-5f", None, None),
    (8, "(S)-Z-4d", "p-OMe", 40, 19, 57, "(S)-Z-5f", 94.7, 95.8),
    (9, "Z-4c", "p-N(CH3)2", 40, 12, 76, "Z-5g", None, None),
    (10, "(R)-Z-4c", "p-N(CH3)2", 40, 12, 73, "(R)-Z-5g", 99.1, 94.0),
]
for entry, substrate, aryl, temp_c, time_h, yield_value, product, sub_ee, prod_ee in table7:
    prefix = f"t7e{entry}"
    sub_amounts = [field("starting_material_ee", q(sub_ee, "%"), (6,))] if sub_ee is not None else []
    parts = [participant(f"{prefix}_sub", "reactant", substrate, (6,), amounts=sub_amounts), participant(f"{prefix}_orgzn", "reagent", f"ArZnBr (R2={aryl})", (6,)), participant(f"{prefix}_ni", "catalyst", "Ni(acac)2", (6,)), participant(f"{prefix}_solv", "solvent", "THF/DMF", (6,)), participant(f"{prefix}_prod", "product", product, (6,))]
    outcomes = [field("yield", q(yield_value, "%"), (6,), [f"{prefix}_prod"]), field("stereochemical_outcome", "Z", (6,), [f"{prefix}_prod"]), field("yield_measurement_basis", None, targets=[f"{prefix}_prod"])]
    if prod_ee is not None:
        outcomes.append(field("product_ee", q(prod_ee, "%"), (6,), [f"{prefix}_prod"]))
    records.append(rec(
        f"table7_entry_{entry:02d}", "substrate_scope_entry", (6,), parts,
        [field("temperature", q(temp_c, "°C"), (6,)), field("time", q(time_h, "h"), (6,)), field("solvent", "THF/DMF", (6,))], outcomes,
        unresolved=["Table 7 does not report reaction scale, arylzinc amount, catalyst loading, or yield basis.", "Structures and ee assignments remain machine-unverified."],
    ))

table8 = [
    (1, "Z-6e", "m-Me", 19, 63, "Z-5h", None, None),
    (2, "(S)-Z-6e", "m-Me", 19, 57, "(S)-Z-5h", 96.0, 94.5),
    (3, "Z-6e", "p-Me", 12, 66, "Z-5i", None, None),
    (4, "(S)-Z-6e", "p-Me", 12, 65, "(S)-Z-5i", 96.0, 96.6),
    (5, "Z-6e", "p-OMe", 11, 60, "Z-5f", None, None),
    (6, "Z-6e", "p-N(CH3)2", 12, 70, "Z-5j", None, None),
]
for entry, substrate, aryl, time_h, yield_value, product, sub_ee, prod_ee in table8:
    prefix = f"t8e{entry}"
    sub_amounts = [field("starting_material_ee", q(sub_ee, "%"), (6,))] if sub_ee is not None else []
    parts = [participant(f"{prefix}_sub", "reactant", substrate, (6,), amounts=sub_amounts), participant(f"{prefix}_orgzn", "reagent", f"ArZnBr (R1={aryl})", (6,)), participant(f"{prefix}_ni", "catalyst", "Ni(acac)2", (6,)), participant(f"{prefix}_prod", "product", product, (6,))]
    outcomes = [field("yield", q(yield_value, "%"), (6,), [f"{prefix}_prod"]), field("stereochemical_outcome", "Z", (6,), [f"{prefix}_prod"]), field("yield_measurement_basis", None, targets=[f"{prefix}_prod"])]
    if prod_ee is not None:
        outcomes.append(field("product_ee", q(prod_ee, "%"), (6,), [f"{prefix}_prod"]))
    records.append(rec(
        f"table8_entry_{entry:02d}", "substrate_scope_entry", (6,), parts,
        [field("temperature", q(40, "°C"), (6,)), field("time", q(time_h, "h"), (6,)), field("solvent", None)], outcomes,
        unresolved=["Table 8 does not report solvent, reaction scale, arylzinc amount, catalyst loading, or yield basis.", "Structures and ee assignments remain machine-unverified."],
    ))

records.append(rec(
    "eq5_sulfoxide_oxidation", "reported_experiment", (6,),
    [participant("eq5_sub", "reactant", "Z-4e (label printed in eq 5)", (6,)), participant("eq5_mcpba", "reagent", "m-CPBA", (6,), name="m-CPBA"), participant("eq5_solvent", "solvent", "CH2Cl2", (6,), name="dichloromethane"), participant("eq5_prod", "product", "Z-6e", (6,))],
    [field("temperature", None), field("time", None), field("solvent", "CH2Cl2", (6,))],
    [field("yield", None, targets=["eq5_prod"]), field("reaction_outcome", "sulfoxide oxidized to sulfone", (6,), ["eq5_prod"])],
    unresolved=["Equation 5 reports no scale, reagent amount, temperature, time, or yield.", "The printed substrate label Z-4e is retained; its drawn n-C8H17 structure conflicts with Table 5's Z-4e assignment and is not silently corrected."],
))


def ids(prefix: str) -> list[str]:
    return [r["record_id"] for r in records if r["source_reaction_id"].startswith(prefix)]


page1_ids = [f"{DOC}:scheme2_nai_30pct"]
page2_ids = [r["record_id"] for r in records if 2 in [int(e.split(":page")[1].split(":")[0]) for e in r["evidence_ids"] if ":page" in e]]
page3_ids = [r["record_id"] for r in records if 3 in [int(e.split(":page")[1].split(":")[0]) for e in r["evidence_ids"] if ":page" in e]]
page4_ids = [r["record_id"] for r in records if r["source_reaction_id"].startswith(("scheme8_", "table2_", "scheme9_", "table3_", "table4_", "scheme10_"))]
page5_ids = [r["record_id"] for r in records if r["source_reaction_id"].startswith(("eq2_", "scheme11_", "table5_", "eq3_"))]
page6_ids = [r["record_id"] for r in records if r["source_reaction_id"].startswith(("table6_", "scheme13_", "eq4_", "table7_", "table8_", "eq5_"))]

coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1, "state": "attempted",
            "regions": [
                {"region": "title and abstract", "finding": "Article-level summary of halohydroxylation and subsequent coupling; no row-specific quantities extracted from the abstract.", "evidence_ids": [f"{DOC}:page1:image", f"{DOC}:page1:text"]},
                {"region": "Scheme 1", "finding": "Conceptual selectivity target with generic R groups; not a reported experiment.", "evidence_ids": [f"{DOC}:page1:image"]},
                {"region": "Introduction, lower columns", "finding": "Prior/example NaI-HOAc reaction of 1a at 80 °C to Z-2aa in 30% yield; merged with Scheme 2 on page 2.", "evidence_ids": [f"{DOC}:page1:image", f"{DOC}:page1:text"]},
            ],
            "record_ids": page1_ids,
            "unresolved": ["Scheme 1 is generic and has no exact structures or experiment-specific conditions.", "The 30% introductory yield differs from Scheme 3's 41% anhydrous-HOAc result; records remain separate."],
        },
        {
            "page": 2, "state": "attempted",
            "regions": [
                {"region": "Schemes 2 and 3, upper left", "finding": "Five distinct literature/example arrows: NaI substitution, oxidation, esterification, and two anhydrous-HOAc halide variants.", "evidence_ids": [f"{DOC}:page2:image", f"{DOC}:page2:text"]},
                {"region": "Scheme 4 and equation 1", "finding": "Generic halohydroxylation route plus the specific 1a iodohydroxylation giving E-3aa; the latter is a reported experiment.", "evidence_ids": [f"{DOC}:page2:image", f"{DOC}:page2:text"]},
                {"region": "Figure 1", "finding": "ORTEP characterization of E-3aa; no additional reaction record.", "evidence_ids": [f"{DOC}:page2:image"]},
                {"region": "Table 1", "finding": "Eleven independently recorded substrate-scope rows with row-specific I2 equivalents, times, and yields.", "evidence_ids": [f"{DOC}:page2:image", f"{DOC}:page2:text"]},
            ],
            "record_ids": page2_ids,
            "unresolved": ["Most Scheme 2/3 arrows omit time, exact temperature, or yield basis.", "Table 1 provides labels/R groups rather than independently verified machine structures."],
        },
        {
            "page": 3, "state": "attempted",
            "regions": [
                {"region": "Scheme 5", "finding": "Chemoselectivity illustration for allyl/homoallyl substrates; generic explanatory scheme, not a new quantified experiment.", "evidence_ids": [f"{DOC}:page3:image"]},
                {"region": "Scheme 6", "finding": "Three separate controls: diiodination product, unidentified mixture, and sulfone no-reaction/recovery result.", "evidence_ids": [f"{DOC}:page3:image", f"{DOC}:page3:text"]},
                {"region": "Figure 2 and top arrow of Scheme 7", "finding": "Crystallographic structures plus the 1m to E-3am experiment (97%); experiment recorded independently of the proposed mechanism.", "evidence_ids": [f"{DOC}:page3:image", f"{DOC}:page3:text"]},
                {"region": "Scheme 7 lower arrows and mechanism prose", "finding": "Proposed iodonium/cyclic-intermediate mechanism; classified as mechanism, not an additional yield experiment.", "evidence_ids": [f"{DOC}:page3:image", f"{DOC}:page3:text"]},
            ],
            "record_ids": page3_ids,
            "unresolved": ["The unidentified Scheme 6 mixture has no assigned products or yield.", "Proposed intermediates 6 and 7 are not isolated structures."],
        },
        {
            "page": 4, "state": "attempted",
            "regions": [
                {"region": "Scheme 8", "finding": "Two independent iodohydroxylation experiments for 1n and 1o.", "evidence_ids": [f"{DOC}:page4:image", f"{DOC}:page4:text"]},
                {"region": "Table 2", "finding": "Eight bromohydroxylation rows recorded independently; visual reading resolves entry 7 time as 1 h.", "evidence_ids": [f"{DOC}:page4:image", f"{DOC}:page4:text"]},
                {"region": "Scheme 9 and chlorohydroxylation prose", "finding": "Solution-phase 20%/72%-recovery control and solventless 73% milling experiment recorded separately.", "evidence_ids": [f"{DOC}:page4:image", f"{DOC}:page4:text"]},
                {"region": "Table 3", "finding": "Five solventless chlorohydroxylation rows; entry 4 merged with the same Scheme 9 experiment rather than duplicated.", "evidence_ids": [f"{DOC}:page4:image", f"{DOC}:page4:text"]},
                {"region": "Table 4", "finding": "Nine optically active halohydroxylation rows with isolated yields and substrate/product ee values.", "evidence_ids": [f"{DOC}:page4:image", f"{DOC}:page4:text"]},
                {"region": "Scheme 10", "finding": "Three starting-material synthesis arrows recorded independently with yield and ee transfer data.", "evidence_ids": [f"{DOC}:page4:image"]},
            ],
            "record_ids": page4_ids,
            "unresolved": ["Several CuBr2 Table 2 rows omit temperature.", "Table 3 omits milling duration and yield basis.", "Table 4 omits times, scales, and most solvents."],
        },
        {
            "page": 5, "state": "attempted",
            "regions": [
                {"region": "equation 2", "finding": "Sonogashira coupling to Z-4g recorded with temperature range, time, and yield.", "evidence_ids": [f"{DOC}:page5:image", f"{DOC}:page5:text"]},
                {"region": "Scheme 11 and Suzuki prose", "finding": "No-TBAB and 10 mol% TBAB phenyl variants plus E-1-hexenylboronic-acid coupling recorded separately.", "evidence_ids": [f"{DOC}:page5:image", f"{DOC}:page5:text"]},
                {"region": "Table 5", "finding": "Twelve independent Pd-catalyzed organozinc rows, including two explicit 0% failures and chiral footnotes.", "evidence_ids": [f"{DOC}:page5:image", f"{DOC}:page5:text"]},
                {"region": "equation 3", "finding": "Protected-alcohol coupling to Z-4f-TBS at 94% recorded as a separate experiment.", "evidence_ids": [f"{DOC}:page5:image", f"{DOC}:page5:text"]},
                {"region": "bottom-right double-coupling discussion", "finding": "Narrative preview of page-6 Scheme 12/Table 6; no duplicate page-5 record created.", "evidence_ids": [f"{DOC}:page5:image", f"{DOC}:page5:text"]},
            ],
            "record_ids": page5_ids,
            "unresolved": ["Most coupling rows omit reaction scale, organozinc loading, catalyst loading, and yield basis.", "Equation 3 omits time and temperature."],
        },
        {
            "page": 6, "state": "attempted",
            "regions": [
                {"region": "Scheme 12 and Table 6", "finding": "Six two-stage Pd/Ni coupling rows recorded independently; visual reading resolves entry 2 yield as 40%.", "evidence_ids": [f"{DOC}:page6:image", f"{DOC}:page6:text"]},
                {"region": "Scheme 13", "finding": "Ni-only control retained as an unresolved product mixture without invented component yields.", "evidence_ids": [f"{DOC}:page6:image", f"{DOC}:page6:text"]},
                {"region": "equation 4", "finding": "Hydroxyl-group control with two product-specific yields linked to Z-5c and stilbene.", "evidence_ids": [f"{DOC}:page6:image", f"{DOC}:page6:text"]},
                {"region": "Table 7", "finding": "Ten independent C-S(O)Ph coupling rows including three chiral-footnote variants.", "evidence_ids": [f"{DOC}:page6:image", f"{DOC}:page6:text"]},
                {"region": "Table 8", "finding": "Six independent C-SO2Ph coupling rows including two chiral-footnote variants.", "evidence_ids": [f"{DOC}:page6:image", f"{DOC}:page6:text"]},
                {"region": "equation 5", "finding": "Sulfoxide-to-sulfone oxidation inventoried; the printed substrate-label inconsistency is preserved as unresolved.", "evidence_ids": [f"{DOC}:page6:image", f"{DOC}:page6:text"]},
            ],
            "record_ids": page6_ids,
            "unresolved": ["Scheme 13 has no component yields, time, or temperature.", "Tables 6-8 omit several amounts/loadings and yield bases.", "Equation 5's printed Z-4e label conflicts with the drawn n-C8H17 structure and is not silently corrected."],
        },
    ],
}


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    COVERAGE.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
    COVERAGE.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")
    tasks = json.loads(TASKS.read_text())
    for task in tasks:
        if task.get("document_id") == DOC and 1 <= int(task["evidence_id"].split(":page")[1].split(":")[0]) <= 6:
            task["state"] = "attempted"
            task["reason"] = "Original page image inspected; regions and linked machine records are in coverage/pages_0001_0006.json."
    TASKS.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"records": len(records), "coverage_pages": len(coverage["pages"]), "output": str(OUT)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
