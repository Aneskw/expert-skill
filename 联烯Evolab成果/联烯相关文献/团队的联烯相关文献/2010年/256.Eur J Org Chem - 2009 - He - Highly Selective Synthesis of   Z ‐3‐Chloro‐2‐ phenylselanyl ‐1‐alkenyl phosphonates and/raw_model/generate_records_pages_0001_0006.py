#!/usr/bin/env python3
"""Build the source-linked machine records for PDF pages 1--6.

This is intentionally a record builder rather than a chemistry validator.  The
merge tool remains responsible for schema normalization and quarantine.
"""
from __future__ import annotations

import json
from pathlib import Path

DOC = "doc_c4d18a33a17c9cf6"
ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).with_name("records_pages_0001_0006.json")


def evidence(*pages: int) -> list[str]:
    result: list[str] = []
    for page in pages:
        result += [f"{DOC}:page{page}:image", f"{DOC}:page{page}:text"]
    return result


def fact(value, *pages: int):
    return {
        "value": value,
        "evidence_ids": evidence(*pages) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def q(number, unit, **extra):
    value = {"number": number, "unit": unit}
    value.update(extra)
    return value


def fld(name, value, *pages: int, targets=None):
    result = {"name": name, "fact": fact(value, *pages)}
    if targets:
        result["target_entity_ids"] = list(targets)
    return result


def mol(entity_id, role, label, pages, *, name=None, smiles=None, amounts=()):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, *pages),
        "name": fact(name, *pages) if name is not None else fact(None),
        "smiles": fact(smiles, *pages) if smiles is not None else fact(None),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": [fld(n, v, *p) for n, v, p in amounts],
    }


def rec(suffix, kind, pages, participants=(), conditions=(), outcomes=(), notes=(), unresolved=()):
    e = evidence(*pages)
    return {
        "record_id": f"{DOC}:{suffix}",
        "document_id": DOC,
        "source_reaction_id": suffix,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": e,
        "participants": list(participants),
        "steps": ([{
            "step_id": "reaction",
            "participant_ids": [p["entity_id"] for p in participants],
            "conditions": list(conditions),
        }] if conditions else []),
        "outcomes": list(outcomes),
        "notes": [fact(value, *note_pages) for value, note_pages in notes],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": list(unresolved),
        },
    }


SMILES = {
    "PhSeCl": "Cl[Se]c1ccccc1",
    "pBrPhSeCl": "Cl[Se]c1ccc(Br)cc1",
    "water": "O",
    "THF": "C1CCOC1",
    "dioxane": "O1CCOCC1",
    "MeCN": "CC#N",
    "DMF": "CN(C)C=O",
    "MeOH": "CO",
    "CHCl3": "ClC(Cl)Cl",
    "Et2O": "CCOCC",
    "Et3N": "CCN(CC)CC",
    "ClP(OEt)2": "CCOP(Cl)OCC",
    "1a": "CCOP(=O)(OCC)C=C=CCCCC",
    "1b": "CCOP(=O)(OCC)C=C=CC",
    "1c": "CCOP(=O)(OCC)C=C=CCCC",
    "1d": "CCOP(=O)(OCC)C=C=CCCCCC",
    "1e": "CCOP(=O)(OCC)C=C=CCCCCCC",
    "1f": "CCOP(=O)(OCC)C=C=CC(C)C",
    "1g": "CCOP(=O)(OCC)C=C=CCc1ccccc1",
    "1h": "CCOP(=O)(OCC)C=C=C",
    "2a": "CCOP(=O)(OCC)C=C([Se]c1ccccc1)C(Cl)CCCC",
    "2b": "CCOP(=O)(OCC)C=C([Se]c1ccccc1)C(Cl)C",
    "2c": "CCOP(=O)(OCC)C=C([Se]c1ccccc1)C(Cl)CCC",
    "2d": "CCOP(=O)(OCC)C=C([Se]c1ccccc1)C(Cl)CCCCC",
    "2e": "CCOP(=O)(OCC)C=C([Se]c1ccccc1)C(Cl)CCCCCC",
    "2f": "CCOP(=O)(OCC)C=C([Se]c1ccccc1)C(Cl)C(C)C",
    "2g": "CCOP(=O)(OCC)C=C([Se]c1ccccc1)C(Cl)Cc1ccccc1",
    "2h": "CCOP(=O)(OCC)C=C([Se]c1ccccc1)CCl",
    "3a": "CCOP1(=O)OC(CCCC)C([Se]c2ccccc2)=C1",
}


def solvent(entity_id, label, pages, volume=None):
    amounts = [] if volume is None else [("volume", q(volume, "mL"), pages)]
    return mol(entity_id, "solvent", label, pages, smiles=SMILES.get(label), amounts=amounts)


def common_phsecl(pages, equiv=None, mmol=None, mg=None, entity_id="phsecl"):
    amounts = []
    if equiv is not None:
        amounts.append(("equivalents", q(equiv, "equiv"), pages))
    if mmol is not None:
        amounts.append(("amount", q(mmol, "mmol"), pages))
    if mg is not None:
        amounts.append(("mass", q(mg, "mg"), pages))
    return mol(entity_id, "reagent", "PhSeCl", pages,
               name="phenylselanyl chloride", smiles=SMILES["PhSeCl"], amounts=amounts)


records = []

# Scheme 1: retain both arrows as non-batch, generic records.
records.append(rec(
    "scheme1_prior_e_halohydroxylation", "general_scheme", (1,),
    participants=[
        mol("generic_phosphane_oxide_allene", "reactant", "generic allenyl diphenylphosphane oxide", (1,)),
        mol("electrophile", "reagent", "E+ (I+ or PhSe+)", (1,)),
        solvent("mecn_s1", "MeCN", (1,)), solvent("water_s1", "water", (1,)),
        mol("e_products", "product", "generic E products", (1,)),
    ],
    conditions=[fld("solvent", "MeCN/H2O", 1)],
    notes=[("Prior-work generic transformation shown in Scheme 1; not a batch experiment in this paper.", (1,))],
    unresolved=["Generic R groups and electrophile prevent a fully specified structure.", "No batch quantities, time, temperature, or yield are stated in Scheme 1."],
))
records.append(rec(
    "scheme1_this_work_z_selenochlorination", "general_scheme", (1,),
    participants=[
        mol("generic_allenylphosphonate", "reactant", "generic 1,2-alkadienylphosphonate", (1,)),
        common_phsecl((1,)),
        solvent("thf_or_dioxane", "THF or dioxane", (1,)), solvent("water_scheme1", "water", (1,), None),
        mol("z_products", "product", "generic Z selenochlorination products", (1,)),
    ],
    conditions=[fld("solvent", "THF/H2O or dioxane/H2O (10:1)", 1)],
    notes=[("This-work generic transformation shown in Scheme 1; substrate-specific batches are recorded separately.", (1,))],
    unresolved=["Generic R groups prevent fully specified structures.", "Scheme 1 does not state batch quantities, time, or yield."],
))


def table1_record(entry, equiv, solvent_name, ratio, temp, time_h, y2a, y3a, product_ratio, impurity=False):
    pages = (2,)
    suffix = f"table1_entry{entry}"
    if entry == 6:
        suffix = "table1_entry6_table2_entry2_typical_iii_2a"
        pages = (2, 5)
    elif entry == 10:
        suffix = "table1_entry10_table2_entry1_typical_ii_2a"
        pages = (2, 5)
    parts = [
        mol("substrate_1a", "reactant", "1a", pages, name="diethyl hepta-1,2-dienylphosphonate", smiles=SMILES["1a"],
            amounts=[("amount", q(0.2, "mmol"), pages)]),
        common_phsecl(pages, equiv=equiv),
        solvent("organic_solvent", solvent_name, pages, 4.0),
        solvent("water", "water", pages),
        mol("product_2a", "product", "(Z)-2a", pages,
            name="diethyl [(Z)-3-chloro-2-(phenylselanyl)-1-heptenyl]phosphonate", smiles=SMILES["2a"]),
        mol("product_3a", "product", "3a", pages,
            name="5-(n-butyl)-2-ethoxy-4-(phenylselanyl)-2,5-dihydro-1,2-oxaphosphole 2-oxide", smiles=SMILES["3a"]),
    ]
    conditions = [
        fld("solvent", f"{solvent_name}/H2O ({ratio})", *pages),
        fld("temperature", temp if isinstance(temp, str) else q(temp, "°C"), *pages),
        fld("time", q(time_h, "h"), *pages),
        fld("atmosphere", None), fld("workup", None), fld("purification", None),
    ]
    outcomes = [
        fld("isolated_yield_2a", q(y2a, "%"), *pages, targets=["product_2a"]),
        fld("isolated_yield_3a", q(y3a, "%"), *pages, targets=["product_3a"]),
        fld("yield_measurement_basis", "isolated", *pages, targets=["product_2a", "product_3a"]),
        fld("product_ratio_2a_to_3a", product_ratio, *pages, targets=["product_2a", "product_3a"]),
    ]
    notes = []
    unresolved = ["No atmosphere is reported for the table row."]
    if impurity:
        notes.append(("Another impurity formed and could not be separated from 3a.", pages))
        unresolved.append("The additional impurity is unidentified and the reported 3a fraction is not pure 3a.")
    if entry in (6, 10):
        notes.append(("The matching Table 2 row applies a table-wide 0.3 mmol scale, whereas Table 1 and the detailed procedure state 0.2 mmol; 0.2 mmol is retained and the discrepancy is unresolved.", pages))
        unresolved.append("Table 2 scale conflicts with Table 1 and the detailed procedure.")
        conditions[-2] = fld("workup", "quenched with H2O; extracted with diethyl ether; brine wash; dried over anhydrous Na2SO4", 5)
        conditions[-1] = fld("purification", "flash chromatography on silica gel (petroleum ether/ethyl acetate 2:1)", 5)
    return rec(suffix, "optimization_entry", pages, parts, conditions, outcomes, notes, unresolved)


table1 = [
    (1, 2.0, "MeCN", "40:1", "r.t.", 2.3, 33, 36, "48:52", False),
    (2, 2.0, "MeCN", "3:1", "r.t.", 2.0, 18, 49, "27:73", False),
    (3, 2.0, "MeCN", "10:1", "r.t.", 23.0, 37, 3, ">92:8", True),
    (4, 1.5, "MeCN", "10:1", 70, 3.5, 42, 6, ">88:12", True),
    (5, 2.0, "MeCN", "10:1", 50, 11.3, 44, 0, "99:1", False),
    (6, 1.5, "dioxane", "10:1", 70, 4.0, 69, 0, "99:1", False),
    (7, 1.5, "DMF", "10:1", 70, 4.0, 48, 28, ">63:37", True),
    (8, 1.5, "MeOH", "10:1", 70, 2.0, 15, 20, ">43:57", True),
    (9, 1.2, "THF", "10:1", 70, 2.0, 62, 0, "99:1", False),
    (10, 1.5, "THF", "10:1", 70, 2.5, 69, 0, "99:1", False),
    (11, 2.0, "THF", "10:1", 70, 2.0, 64, 0, "99:1", False),
]
for row in table1:
    records.append(table1_record(*row))

# Add page-1 prose as corroboration for the two opening optimization rows.
for r in records:
    if r["source_reaction_id"] in {"table1_entry1", "table1_entry2"}:
        r["evidence_ids"] = evidence(1, 2)


SUBSTRATE = {
    3: ("1b", "Me", "diethyl buta-1,2-dienylphosphonate", "2b"),
    4: ("1b", "Me", "diethyl buta-1,2-dienylphosphonate", "2b"),
    5: ("1c", "n-Pr", "diethyl hexa-1,2-dienylphosphonate", "2c"),
    6: ("1d", "n-C5H11", "diethyl octa-1,2-dienylphosphonate", "2d"),
    7: ("1e", "n-C6H13", "diethyl nona-1,2-dienylphosphonate", "2e"),
    8: ("1f", "i-Pr", "diethyl 4-methylpenta-1,2-dienylphosphonate", "2f"),
    9: ("1g", "Bn", "diethyl (4-phenylbuta-1,2-dienyl)phosphonate", "2g"),
    10: ("1h", "H", "diethyl propa-1,2-dienylphosphonate", "2h"),
}
SCOPE = {
    3: ("THF", 1.0, 52, (2, 5), 0.30, 56.4, 86.4, 58.6),
    4: ("dioxane", 5.0, 53, (2, 5), 0.30, 57.8, 86.1, 62.0),
    5: ("THF", 1.5, 64, (2, 5, 6), 0.30, 64.9, 86.8, 77.7),
    6: ("THF", 1.0, 66, (2, 6), 0.30, 74.4, 85.5, 87.8),
    7: ("THF", 1.0, 68, (2, 6), 0.20, 51.6, 58.0, 60.7),
    8: ("THF", 1.5, 74, (2, 6), 0.30, 64.1, 85.9, 89.6),
    9: ("THF", 3.3, 78, (2, 6), 0.20, 54.1, 59.1, 66.1),
    10: ("THF", 3.0, 81, (2, 6), 0.30, 52.6, 85.5, 89.2),
}
for entry, (solv, time_h, yld, pages, scale, smass, rmass, pmass) in SCOPE.items():
    sub, rgroup, subname, prod = SUBSTRATE[entry]
    product_name = {
        "2b": "diethyl [(Z)-3-chloro-2-(phenylselanyl)-1-butenyl]phosphonate",
        "2c": "diethyl [(Z)-3-chloro-2-(phenylselanyl)-1-hexenyl]phosphonate",
        "2d": "diethyl [(Z)-3-chloro-2-(phenylselanyl)-1-octenyl]phosphonate",
        "2e": "diethyl [(Z)-3-chloro-2-(phenylselanyl)-1-nonenyl]phosphonate",
        "2f": "diethyl [(Z)-3-chloro-4-methyl-2-(phenylselanyl)-1-pentenyl]phosphonate",
        "2g": "diethyl [(Z)-3-chloro-4-phenyl-2-(phenylselanyl)-1-butenyl]phosphonate",
        "2h": "diethyl [(Z)-3-chloro-2-(phenylselanyl)-1-propenyl]phosphonate",
    }[prod]
    solvent_volume = 6.0 if scale == 0.30 else 4.0
    water_volume = 0.6 if scale == 0.30 else 0.4
    parts = [
        mol("substrate", "reactant", sub, pages, name=subname, smiles=SMILES[sub],
            amounts=[("amount", q(scale, "mmol"), pages), ("mass", q(smass, "mg"), pages)] +
                    ([("purity", q(91, "%"), pages)] if entry == 9 else [])),
        common_phsecl(pages, mmol=1.5 * scale, mg=rmass),
        solvent("organic_solvent", solv, pages, solvent_volume),
        solvent("water", "water", pages, water_volume),
        mol("product", "product", f"(Z)-{prod}", pages, name=product_name, smiles=SMILES[prod]),
    ]
    conditions = [
        fld("solvent", f"{solv}/H2O (10:1)", *pages), fld("temperature", q(70, "°C"), *pages),
        fld("time", q(time_h, "h"), *pages), fld("atmosphere", None),
        fld("workup", "quenched with H2O; extracted with diethyl ether; brine wash; dried over anhydrous Na2SO4", *pages),
        fld("purification", "flash chromatography on silica gel", *pages),
    ]
    outcomes = [
        fld(f"isolated_yield_{prod}", q(yld, "%"), *pages, targets=["product"]),
        fld("isolated_product_mass", q(pmass, "mg"), *pages, targets=["product"]),
        fld("yield_measurement_basis", "isolated", *pages, targets=["product"]),
    ]
    notes = [(f"Table 2 substituent R={rgroup}.", (2,))]
    unresolved = ["Atmosphere is not reported.", "Candidate SMILES are not source-verified."]
    if entry in (7, 9):
        notes.append(("The detailed batch uses 0.20 mmol, while the Table 2 footnote states a table-wide 0.30 mmol scale; the detailed quantity is retained.", pages))
        unresolved.append("Detailed batch scale conflicts with the Table 2 table-wide scale.")
    records.append(rec(f"table2_entry{entry}_{prod}", "substrate_scope_entry", pages, parts, conditions, outcomes, notes, unresolved))

# Two failed/complicated phenyl-substituted substrate experiments described across pages 2--3.
for location, label in (("1-substituted", "diethyl (1-phenylpropa-1,2-dienyl)phosphonate"),
                        ("3-substituted", "diethyl (3-phenylpropa-1,2-dienyl)phosphonate")):
    pages = (2, 3)
    records.append(rec(
        f"phenyl_{location.replace('-', '_')}_complicated", "reported_experiment", pages,
        participants=[
            mol("substrate", "reactant", label, pages, name=label), common_phsecl(pages, equiv=1.5),
            solvent("thf", "THF", pages), solvent("water", "water", pages),
            mol("unresolved_products", "product", "complicated product mixture", pages),
        ],
        conditions=[fld("solvent", "THF/H2O (10:1)", *pages), fld("temperature", q(70, "°C"), *pages),
                    fld("time", None), fld("atmosphere", None), fld("workup", None), fld("purification", None)],
        outcomes=[fld("reaction_outcome", "complicated reaction", *pages, targets=["unresolved_products"]),
                  fld("isolated_yield", None, targets=["unresolved_products"])],
        unresolved=["No product identity, yield, reaction time, workup, or purification is reported.", "The substrate structure is identified by name only."],
    ))

# Scheme 2 current experiments and the explicitly cited Macomber literature result.
def pbr_reagent(pages, equiv, mmol=None, mg=None):
    amounts = [("equivalents", q(equiv, "equiv"), pages)]
    if mmol is not None: amounts.append(("amount", q(mmol, "mmol"), pages))
    if mg is not None: amounts.append(("mass", q(mg, "mg"), pages))
    return mol("selenyl_chloride", "reagent", "4-BrC6H4SeCl", pages,
               name="p-bromophenylselanyl chloride", smiles=SMILES["pBrPhSeCl"], amounts=amounts)

scheme2_specs = [
    ("scheme2_eq1_2i", "1h", "diethyl propa-1,2-dienylphosphonate", 0.30, 52.3, pbr_reagent, 2.0, 0.60, 163.1,
     "THF/H2O (10:1)", 70, 3.5, "(Z)-2i", "diethyl [(Z)-2-(4-bromophenylselanyl)-3-chloro-1-propenyl]phosphonate", 74, 98.6),
    ("scheme2_eq2_conditions_a_2j", "1j", "cyclic allenylphosphonate 1j", 0.30, 56.5, pbr_reagent, 2.0, 0.60, 161.9,
     "THF/H2O (10:1)", 70, 2.0, "(Z)-2j", "2-[(1Z)-2-(4-bromophenylselanyl)-3-chloro-1-propenyl]-5,5-dimethyl-1,3,2-dioxaphosphorinane 2-oxide", 72, 99.6),
    ("scheme2_eq3_conditions_a_2k", "1k", "dimethyl propa-1,2-dienylphosphonate", 0.40, 59.5, common_phsecl, 1.5, 0.60, 114.8,
     "THF/H2O (10:1)", 70, 4.0, "(Z)-2k", "dimethyl [(Z)-3-chloro-2-(phenylselanyl)-1-propenyl]phosphonate", 80, 108.9),
]
for suffix, slabel, sname, smmol, smg, reagent_fn, equiv, rmmol, rmg, solv, temp, time_h, plabel, pname, yld, pmg in scheme2_specs:
    pages = (3,)
    # Scheme 2 itself states equivalents and conditions, but not batch masses,
    # volumes, workup, or product mass.  Those later-page details are outside
    # this extraction range and are deliberately not projected back here.
    reagent = reagent_fn(pages, equiv) if reagent_fn is pbr_reagent else reagent_fn(pages, equiv=equiv)
    records.append(rec(
        suffix, "reported_experiment", pages,
        participants=[
            mol("substrate", "reactant", slabel, pages, name=sname, smiles=SMILES.get(slabel)),
            reagent, solvent("thf", "THF", pages), solvent("water", "water", pages),
            mol("product", "product", plabel, pages, name=pname),
        ],
        conditions=[fld("solvent", solv, 3), fld("temperature", q(temp, "°C"), 3), fld("time", q(time_h, "h"), 3),
                    fld("atmosphere", None), fld("workup", None), fld("purification", None)],
        outcomes=[fld("isolated_yield", q(yld, "%"), 3, targets=["product"]),
                  fld("yield_measurement_basis", "isolated", 3, targets=["product"])],
        unresolved=["Product candidate SMILES was not assigned because the cyclic/stereochemical depiction requires independent structure review.", "Scheme 2 does not state scale, atmosphere, workup, purification, or product mass for Conditions A."],
    ))

for suffix, slabel, sname, smmol, smg, reagent_label, rmmol, rmg, time_h, plabel, pname, yld, pmg, recovery in [
    ("scheme2_eq2_conditions_b_2j", "1j", "cyclic allenylphosphonate 1j", 0.40, 75.4, "4-BrC6H4SeCl", 0.40, 108.5, 26.0,
     "(Z)-2j", "2-[(1Z)-2-(4-bromophenylselanyl)-3-chloro-1-propenyl]-5,5-dimethyl-1,3,2-dioxaphosphorinane 2-oxide", 54, 98.7, 13),
    ("scheme2_eq3_conditions_b_2k", "1k", "dimethyl propa-1,2-dienylphosphonate", 0.70, 103.3, "PhSeCl", 0.70, 134.8, 19.0,
     "(Z)-2k", "dimethyl [(Z)-3-chloro-2-(phenylselanyl)-1-propenyl]phosphonate", 71, 167.5, None),
]:
    pages = (3,)
    reagent = pbr_reagent(pages, 1.0) if reagent_label.startswith("4-Br") else common_phsecl(pages, equiv=1.0)
    outcomes = [fld("isolated_yield", q(yld, "%"), 3, targets=["product"]),
                fld("yield_measurement_basis", "isolated", 3, targets=["product"])]
    if recovery is not None:
        outcomes.append(fld("recovered_starting_material_yield", q(recovery, "%"), 3, targets=["substrate"]))
        outcomes.append(fld("recovery_measurement_basis", None, targets=["substrate"]))
    records.append(rec(
        suffix, "reported_experiment", pages,
        participants=[
            mol("substrate", "reactant", slabel, pages, name=sname),
            reagent, solvent("chloroform", "CHCl3", pages),
            mol("product", "product", plabel, pages, name=pname),
        ],
        conditions=[fld("solvent", "anhydrous CHCl3", 3), fld("atmosphere", "N2", 3),
                    fld("temperature", q(46, "°C"), 3), fld("time", q(time_h, "h"), 3),
                    fld("workup", None), fld("purification", None)],
        outcomes=outcomes,
        unresolved=["Product candidate SMILES was not assigned pending independent stereochemical structure review.", "Scheme 2 does not state scale, workup, purification, product mass, or the 13% recovery basis."],
    ))

records.append(rec(
    "macomber_1983_literature_1k", "literature_example", (1, 3),
    participants=[
        mol("substrate", "reactant", "dimethyl propa-1,2-dienylphosphonate", (1, 3)),
        common_phsecl((1, 3), equiv=1.0), solvent("chloroform", "CHCl3", (1, 3)),
        mol("product", "product", "literature-assigned (E)-2k; reassigned here as (Z)-2k", (1, 3)),
    ],
    conditions=[fld("solvent", "anhydrous CHCl3", 1, 3), fld("atmosphere", "N2", 3),
                fld("temperature", q(46, "°C"), 3), fld("time", q(7, "h"), 3)],
    outcomes=[fld("reported_yield", q(46, "%"), 3, targets=["product"]),
              fld("yield_measurement_basis", None, targets=["product"])],
    notes=[("Prior-literature example from Macomber et al.; the current paper argues that its E assignment was incorrect and that the product is Z-2k.", (1, 3))],
    unresolved=["The cited external paper was not supplied, so its batch details and yield basis were not independently checked."],
))

# Scheme 3 scale-up batches.
records.append(rec(
    "scheme3_large_scale_1a_to_2a", "reported_experiment", (3, 5),
    participants=[
        mol("substrate", "reactant", "1a", (3, 5), name="diethyl hepta-1,2-dienylphosphonate", smiles=SMILES["1a"],
            amounts=[("amount", q(4.8, "mmol"), (3, 5)), ("mass", q(1.1134, "g"), (3, 5))]),
        common_phsecl((3, 5), equiv=1.5, mmol=7.2), solvent("dioxane", "dioxane", (3, 5), 48.0),
        solvent("water", "water", (3, 5), 2.4),
        mol("product", "product", "(Z)-2a", (3, 5), name="diethyl [(Z)-3-chloro-2-(phenylselanyl)-1-heptenyl]phosphonate", smiles=SMILES["2a"]),
    ],
    conditions=[fld("solvent", "dioxane/H2O", 3, 5), fld("temperature", q(70, "°C"), 3, 5), fld("time", q(5.5, "h"), 3, 5),
                fld("operation", "substrate solution added dropwise over 3 min", 5),
                fld("workup", "water quench; diethyl ether extraction; brine wash; anhydrous Na2SO4 drying", 5),
                fld("purification", "flash chromatography on silica gel (petroleum ether/ethyl acetate 3:1 to 2:1)", 5)],
    outcomes=[fld("isolated_yield", q(72, "%"), 3, 5, targets=["product"]),
              fld("isolated_product_mass", q(1.4637, "g"), 5, targets=["product"]),
              fld("yield_measurement_basis", "isolated", 3, 5, targets=["product"])],
    unresolved=["Atmosphere is not reported."],
))
records.append(rec(
    "scheme3_large_scale_1j_to_2l", "reported_experiment", (3,),
    participants=[
        mol("substrate", "reactant", "1j", (3,), name="cyclic allenylphosphonate 1j",
            amounts=[("amount", q(5.5, "mmol"), (3,)), ("mass", q(1.0336, "g"), (3,))]),
        common_phsecl((3,), equiv=2.0), solvent("thf", "THF", (3,)),
        solvent("water", "water", (3,)), mol("product", "product", "(Z)-2l", (3,),
            name="2-[(1Z)-3-chloro-2-(phenylselanyl)-1-propenyl]-5,5-dimethyl-1,3,2-dioxaphosphorinane 2-oxide"),
    ],
    conditions=[fld("solvent", "THF/H2O (10:1)", 3), fld("temperature", q(70, "°C"), 3), fld("time", q(2.0, "h"), 3),
                fld("atmosphere", None), fld("workup", None), fld("purification", None)],
    outcomes=[fld("isolated_yield", q(80, "%"), 3, targets=["product"]),
              fld("yield_measurement_basis", "isolated", 3, targets=["product"])],
    unresolved=["Detailed workup and purification appear after page 6 and were not imported in this pass.", "Atmosphere is not reported."],
))

# Table 3, one independent row per condition/substrate.
for entry, rgroup, substrate, time_h, y2, p2, y3, p3, solv in [
    (1, "n-C4H9", "1m", 3.0, 74, "2m", 12, "3m", "dioxane"),
    (2, "n-C4H9", "1m", 2.0, 57, "2m", 7, "3m", "THF"),
    (3, "Me", "1n", 3.0, 63, "2n", 6, "3n", "dioxane"),
    (4, "n-C7H15", "1o", 3.0, 69, "2o", 9, "3o", "dioxane"),
]:
    pages = (3,)
    records.append(rec(
        f"table3_entry{entry}", "substrate_scope_entry", pages,
        participants=[
            mol("substrate", "reactant", substrate, pages, name=f"diethyl 1-substituted allenylphosphonate ({rgroup})",
                amounts=[("amount", q(0.3, "mmol"), pages)]),
            common_phsecl(pages, mmol=0.45, equiv=1.5), solvent("organic_solvent", solv, pages, 6.0),
            solvent("water", "water", pages, 0.6), mol("product_2", "product", f"(Z)-{p2}", pages),
            mol("product_3", "product", p3, pages),
        ],
        conditions=[fld("solvent", f"{solv}/H2O (10:1)", 3), fld("temperature", q(70, "°C"), 3),
                    fld("time", q(time_h, "h"), 3), fld("atmosphere", None), fld("workup", None), fld("purification", None)],
        outcomes=[fld(f"isolated_yield_{p2}", q(y2, "%"), 3, targets=["product_2"]),
                  fld(f"isolated_yield_{p3}", q(y3, "%"), 3, targets=["product_3"]),
                  fld("yield_measurement_basis", "isolated", 3, targets=["product_2", "product_3"])],
        unresolved=["Table 3 does not state atmosphere, workup, purification, or exact batch masses.", "Structures are retained by labels because stereochemical drawings were not independently verified."],
    ))

# Scheme 4 is a mechanistic proposal, not an experiment.
records.append(rec(
    "scheme4_proposed_selenonium_pathway", "mechanism", (3, 4),
    participants=[
        mol("generic_allene", "reactant", "generic allenylphosphonate", (3, 4)), common_phsecl((3, 4)),
        mol("intermediate_e4", "unspecified_agent", "proposed selenonium intermediate (E)-4", (3, 4)),
        mol("intermediate_z5", "unspecified_agent", "proposed selenonium intermediate (Z)-5", (3, 4)),
        mol("z2", "product", "generic (Z)-2", (3, 4)), mol("e2", "product", "generic (E)-2", (3, 4)),
        mol("cyclic_3", "product", "generic cyclic product 3", (3, 4)),
    ],
    conditions=[fld("operation", "proposed equilibrium and competing chloride attack/O-attack pathways", 3, 4)],
    notes=[("Scheme 4 is explicitly presented as a proposed explanation of regio- and stereoselectivity, not as an isolated batch.", (3, 4))],
    unresolved=["Generic substituents and proposed intermediates are not structure-verified."],
))

# Table 4: multisubstituted substrates, one row each.
for entry, r1, r2, r3, substrate, time_h, yld, product, temp in [
    (1, "H", "Me", "Me", "1p", 3.0, 55, "3p", "r.t."),
    (2, "n-C4H9", "H", "Et", "1q", 0.3, 92, "3q", q(70, "°C")),
    (3, "n-C4H9", "Me", "Me", "1r", 4.0, 87, "3r", "r.t."),
]:
    pages = (4,)
    records.append(rec(
        f"table4_entry{entry}", "substrate_scope_entry", pages,
        participants=[
            mol("substrate", "reactant", substrate, pages, name=f"multisubstituted diethyl allenylphosphonate R1={r1}, R2={r2}, R3={r3}",
                amounts=[("amount", q(0.3, "mmol"), pages)]),
            common_phsecl(pages, mmol=0.45, equiv=1.5), solvent("thf", "THF", pages, 6.0),
            solvent("water", "water", pages, 0.6), mol("product", "product", product, pages,
                name="2-ethoxy-4-(phenylselanyl)-2,5-dihydro-1,2-oxaphosphole 2-oxide derivative"),
        ],
        conditions=[fld("solvent", "THF/H2O (10:1)", 4), fld("temperature", temp, 4), fld("time", q(time_h, "h"), 4),
                    fld("atmosphere", None), fld("workup", None), fld("purification", None)],
        outcomes=[fld(f"isolated_yield_{product}", q(yld, "%"), 4, targets=["product"]),
                  fld("yield_measurement_basis", "isolated", 4, targets=["product"])],
        unresolved=["Table 4 does not state atmosphere, workup, purification, or exact masses.", "Product structure and stereochemistry are not independently verified."],
    ))

# Page 4 starting-material preparations.  Page 5 is included for 1q only as its
# characterization paragraph continues there; no new reaction facts are inferred.
prep_specs = [
    ("prep_1e", (4,), "non-1-yn-3-ol", 15.0, 2.0943, 20.0, 2.04, 22.5, 3.5282, 75.0, "1e", "diethyl nona-1,2-dienylphosphonate", 2.8568, 73),
    ("prep_1g", (4,), "1-phenylbut-3-yn-2-ol", 8.0, 1.1690, 11.9, 1.20, 12.1, 1.9000, 35.0, "1g", "diethyl (4-phenylbuta-1,2-dienyl)phosphonate", 1.0919, 46),
    ("prep_1q", (4, 5), "non-4-yn-3-ol", 10.0, 1.3951, 14.4, 1.46, 15.0, 2.3572, 50.0, "1q", "diethyl nona-3,4-dien-5-ylphosphonate", 1.7718, 68),
]
for suffix, pages, alcohol, ammol, ag, bmmol, bg, cmmol, cg, thf_ml, plabel, pname, pg, yld in prep_specs:
    conditions = [
        fld("solvent", "THF", 4), fld("temperature", q(-78, "°C"), 4),
        fld("operation", "diethyl chlorophosphite solution added dropwise at -78 °C", 4),
        fld("time", q(15, "min"), 4) if suffix == "prep_1e" else fld("time", None),
        fld("operation", "warmed naturally to room temperature and heated at reflux until TLC showed complete conversion", 4),
        fld("workup", "water quench; diethyl ether extraction; brine wash; anhydrous Na2SO4 drying", 4),
        fld("purification", "silica-gel chromatography (petroleum ether/ethyl acetate 2:1)", 4),
        fld("atmosphere", None),
    ]
    records.append(rec(
        suffix, "reported_experiment", pages,
        participants=[
            mol("alcohol", "reactant", alcohol, pages, name=alcohol,
                amounts=[("amount", q(ammol, "mmol"), pages), ("mass", q(ag, "g"), pages)]),
            mol("triethylamine", "reagent", "Et3N", pages, name="triethylamine", smiles=SMILES["Et3N"],
                amounts=[("amount", q(bmmol, "mmol"), pages), ("mass", q(bg, "g"), pages)]),
            mol("chlorophosphite", "reagent", "ClP(OEt)2", pages, name="diethyl chlorophosphite", smiles=SMILES["ClP(OEt)2"],
                amounts=[("amount", q(cmmol, "mmol"), pages), ("mass", q(cg, "g"), pages)]),
            solvent("thf", "THF", pages, thf_ml),
            mol("product", "product", plabel, pages, name=pname, smiles=SMILES.get(plabel)),
        ],
        conditions=conditions,
        outcomes=[fld("isolated_yield", q(yld, "%"), 4, targets=["product"]),
                  fld("isolated_product_mass", q(pg, "g"), 4, targets=["product"]),
                  fld("yield_measurement_basis", "isolated after chromatography", 4, targets=["product"])] +
                 ([fld("reported_purity", q(91, "%"), 4, targets=["product"])] if suffix == "prep_1g" else []),
        notes=[("Preparations 1g and 1q are stated to follow Typical Procedure I; only their batch-specific quantities and outcomes are separately reported.", (4,))] if suffix != "prep_1e" else [],
        unresolved=["Atmosphere is not reported."] + (["Exact addition duration and reaction duration are not restated for this abbreviated batch."] if suffix != "prep_1e" else ["Reflux duration is governed by TLC and is not numerically stated."]),
    ))

# Page-5 MeCN batch is not merged into Table 1 entry 2 because its 0.30 mmol
# scale differs from the table footnote's 0.20 mmol scale.
records.append(rec(
    "page5_scaled_mecn_3to1_2a_3a", "reported_experiment", (5,),
    participants=[
        mol("substrate", "reactant", "1a", (5,), name="diethyl hepta-1,2-dienylphosphonate", smiles=SMILES["1a"],
            amounts=[("amount", q(0.3, "mmol"), (5,)), ("mass", q(70.6, "mg"), (5,))]),
        common_phsecl((5,), equiv=2.0, mmol=0.6, mg=115.4), solvent("mecn", "MeCN", (5,), 4.8),
        solvent("water", "water", (5,), 1.6),
        mol("product_2a", "product", "(Z)-2a", (5,), name="diethyl [(Z)-3-chloro-2-(phenylselanyl)-1-heptenyl]phosphonate", smiles=SMILES["2a"]),
        mol("product_3a", "product", "3a", (5,), name="5-(n-butyl)-2-ethoxy-4-(phenylselanyl)-2,5-dihydro-1,2-oxaphosphole 2-oxide", smiles=SMILES["3a"]),
    ],
    conditions=[fld("solvent", "MeCN/H2O (3:1)", 5), fld("temperature", "r.t.", 5), fld("time", q(2, "h"), 5),
                fld("atmosphere", None), fld("workup", "water workup; diethyl ether extraction; brine wash; anhydrous Na2SO4 drying", 5),
                fld("purification", "flash chromatography on silica gel (petroleum ether/ethyl acetate 3:1)", 5)],
    outcomes=[fld("isolated_yield_2a", q(18, "%"), 5, targets=["product_2a"]),
              fld("isolated_product_mass_2a", q(22.8, "mg"), 5, targets=["product_2a"]),
              fld("isolated_yield_3a", q(49, "%"), 5, targets=["product_3a"]),
              fld("isolated_product_mass_3a", q(53.3, "mg"), 5, targets=["product_3a"]),
              fld("yield_measurement_basis", "isolated", 5, targets=["product_2a", "product_3a"]),
              fld("diastereomeric_ratio_3a", "35:65", 5, targets=["product_3a"])],
    notes=[("Nominal conditions and yields match Table 1 entry 2, but the explicitly reported batch scale differs; retained as a separate experiment.", (2, 5))],
    unresolved=["Atmosphere is not reported.", "The relationship between this 0.30 mmol batch and the 0.20 mmol Table 1 row is not stated."],
))

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"output": str(OUT.relative_to(ROOT)), "records": len(records)}, ensure_ascii=False))
