#!/usr/bin/env python3
"""Build evidence-linked machine records for jo049593c PDF pages 1-5."""
import json
from pathlib import Path

DOC = "doc_c1d24ef1513fb165"
BASE = Path(__file__).resolve().parents[1]
OUT = BASE / "raw_model" / "extracted_records_pages_0001_0005.json"


def ev(page):
    return [f"{DOC}:page{page}:text", f"{DOC}:page{page}:image"]


def fact(value, evidence):
    return {
        "value": value,
        "evidence_ids": list(evidence) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def fld(name, value, evidence, target=None, category=None):
    item = {"name": name, "fact": fact(value, evidence)}
    if target:
        item["target_entity_ids"] = list(target)
    if category:
        item["category"] = category
    return item


SMILES = {
    "I2": "II",
    "Br2": "BrBr",
    "water": "O",
    "acetone": "CC(=O)C",
    "MeCN": "CC#N",
    "CH2Cl2": "ClCCl",
    "2b": "C=C=CSc1ccccc1",
    "10b": "OCC(Br)=CSc1ccccc1",
    "4a": "C=C=C[Se]c1ccccc1",
    "11a": "OCC(I)=C[Se]c1ccccc1",
}


def part(entity_id, role, evidence, label=None, name=None, smiles=None, amounts=None):
    candidate = smiles if smiles is not None else SMILES.get(label or "")
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence),
        "smiles": fact(candidate, evidence),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": amounts or [],
    }


def equiv(value, evidence):
    return [fld("equivalents", {"number": value, "unit": "equiv"}, evidence)]


def rec(suffix, page, kind, participants, conditions=None, outcomes=None, notes=None,
        unresolved=None, extra_evidence=None, source_reaction_id=None, steps=True):
    evidence = ev(page)
    if extra_evidence:
        for item in extra_evidence:
            if item not in evidence:
                evidence.append(item)
    participant_ids = [p["entity_id"] for p in participants if p["role"] != "product"]
    return {
        "record_id": f"{DOC}:{suffix}",
        "document_id": DOC,
        "source_reaction_id": source_reaction_id or suffix,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": evidence,
        "participants": participants,
        "steps": ([{"step_id": "step1", "participant_ids": participant_ids,
                    "conditions": conditions or []}] if steps else []),
        "outcomes": outcomes or [],
        "notes": [fact(n, evidence) for n in (notes or [])],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved or [
                "Supporting Information was advertised but not supplied or explicitly associated; scale, detailed procedure, workup and purification are unavailable.",
                "Substrate and product structures represented through source labels/R-groups require independent structure review.",
            ],
        },
    }


records = []

# Page 2: starting-material preparation schemes and equation 1.
e = ev(2)
records.append(rec(
    "scheme1_general_sulfide_preparation", 2, "general_scheme",
    [part("s1_r", "reactant", e, "1", "1,2-allenylic sulfoxide"),
     part("s1_p2s5", "reagent", e, "P2S5", "phosphorus pentasulfide"),
     part("s1_pyridine", "reagent", e, "pyridine", "pyridine"),
     part("s1_solvent", "solvent", e, "CH2Cl2", "dichloromethane"),
     part("s1_p", "product", e, "2", "1,2-allenylic sulfide")],
    [fld("temperature", "r.t.", e), fld("solvent", "CH2Cl2", e)],
    notes=["Scheme 1 is a generalized conversion covering labeled series 1a-q/2a-q, not a yield-bearing individual experiment."],
))
records.append(rec(
    "scheme2_general_selenide_rearrangement", 2, "general_scheme",
    [part("s2_r", "reactant", e, "3", "propargyl aryl/alkyl selenide"),
     part("s2_naoet", "reagent", e, "C2H5ONa", "sodium ethoxide",
          amounts=[fld("concentration", "0.1 N", e)]),
     part("s2_p", "product", e, "4", "1,2-allenylic selenide")],
    [fld("temperature", {"number": 48, "unit": "°C"}, e),
     fld("time", {"number": 70, "unit": "min"}, e)],
    notes=["Scheme 2 is a generalized rearrangement covering labeled series 3a-j/4a-j; the source reports sodium ethoxide as 0.1 N."],
    unresolved=[
        "Normality is preserved as source text because N is not a supported structured unit.",
        "No yield, scale, atmosphere, workup or purification is reported in the main-text scheme.",
        "Generic RSe structures are not expanded to SMILES.",
    ],
))
records.append(rec(
    "equation1_sulfide_2s_preparation", 2, "reported_experiment",
    [part("eq1_r", "reactant", e, "3-phenylthio-1-butyne", "3-phenylthio-1-butyne"),
     part("eq1_base", "reagent", e, "t-C4H9OK", "potassium tert-butoxide"),
     part("eq1_solvent", "solvent", e, "t-C4H9OH", "tert-butanol"),
     part("eq1_p", "product", e, "2s", "1,2-butadien-3-yl phenyl sulfide")],
    [fld("solvent", "t-C4H9OH", e)],
    notes=["Equation 1 and the adjacent text identify rearrangement of 3-phenylthio-1-butyne to 2s."],
))

# Scheme 3 MeCN experiment (the acetone experiment is Table 1 entry 1 below).
records.append(rec(
    "scheme3_mecn_condition", 2, "optimization_entry",
    [part("sc3_r", "reactant", e, "2a", "3-benzyl-1,2-butadienyl phenyl sulfide"),
     part("sc3_i2", "reagent", e, "I2", "iodine", amounts=equiv(2, e)),
     part("sc3_mecn", "solvent", e, "MeCN", "acetonitrile"),
     part("sc3_water", "reagent", e, "H2O", "water"),
     part("sc3_p5", "product", e, "5a", "2-iodo-2-propenal product 5a"),
     part("sc3_p6", "product", e, "6a", "iodohydroxylation product 6a")],
    [fld("solvent", "MeCN/H2O (4:1 v/v)", e),
     fld("temperature", {"number": 28, "unit": "°C"}, e),
     fld("time", {"number": 16, "unit": "h"}, e)],
    [fld("yield", {"number": 16, "unit": "%"}, e, ["sc3_p5"]),
     fld("E_Z_ratio", "0.32/1", e, ["sc3_p5"]),
     fld("yield", {"number": 0, "unit": "%"}, e, ["sc3_p6"]),
     fld("yield_measurement_basis", None, e, ["sc3_p5", "sc3_p6"])],
    notes=["Scheme 3 reports only product 5a under this MeCN/H2O condition; 6a is listed at 0% yield."],
))

# Table 1: iodohydroxylation scope. The footnote assigns aldehyde 5 yields.
table1 = [
    (1, "Bn", "CH3", "2a", 13, 68, "6a", "99/1", 16, "5a", "1.09/1"),
    (2, "H", "H", "2b", 9, 41, "6b", "99/1", "trace", "5b", None),
    (3, "H", "CH3", "2c", 9, 61, "6c", "97/3", "trace", "5c", None),
    (4, "H", "i-Pr", "2d", 10, 56, "6d", "96/4", "trace", "5d", None),
    (5, "H", "n-C4H9", "2e", 13.5, 74, "6e", "98/2", 14, "5e", None),
    (6, "H", "n-C7H15", "2f", 9.5, 67, "6f", "96/4", 18, "5f", None),
    (7, "H", "Bn", "2g", 9.5, 65, "6g", "96/4", 18, "5g", None),
    (8, "CH3", "CH3", "2h", 10.5, 63, "6h", "94/6", "trace", "5h", None),
    (9, "CH3", "C2H5", "2i", 10, 94, "6i", "94/6", "trace", "5i", None),
    (10, "CH3", "i-Bu", "2j", 12, 53, "6j", "99/1", 14, "5j", None),
    (11, "CH3", "t-C4H9", "2k", 9, 85, "6k", "97/3", "trace", "5k", None),
    (12, "C2H5", "C2H5", "2l", 8, 72, "6l", "98/2", "trace", "5l", None),
    (13, "n-C4H9", "n-C4H9", "2m", 10, 93, "6m", "95/5", "trace", "5m", None),
    (14, "n-C5H11", "n-C5H11", "2n", 10, 80, "6n", "97/3", "trace", "5n", None),
]
for entry, r2, r3, substrate, hours, yld, product, ze, by_yld, by_product, by_ratio in table1:
    rid = f"table1_entry{entry:02d}"
    ps = [
        part(f"{rid}_r", "reactant", e, substrate, f"allenyl sulfide {substrate}; R2={r2}, R3={r3}"),
        part(f"{rid}_i2", "reagent", e, "I2", "iodine", amounts=equiv(2, e)),
        part(f"{rid}_acetone", "solvent", e, "acetone", "acetone"),
        part(f"{rid}_water", "reagent", e, "H2O", "water"),
        part(f"{rid}_p", "product", e, product, f"Z-iodohydroxylation product {product}"),
        part(f"{rid}_bp", "product", e, by_product, f"corresponding aldehyde {by_product}"),
    ]
    outcomes = [
        fld("yield", {"number": yld, "unit": "%"}, e, [f"{rid}_p"]),
        fld("Z_E_ratio", ze, e, [f"{rid}_p"]),
        fld("yield", ({"number": by_yld, "unit": "%"} if isinstance(by_yld, (int, float)) else by_yld), e, [f"{rid}_bp"]),
        fld("yield_measurement_basis", None, e, [f"{rid}_p", f"{rid}_bp"]),
    ]
    if by_ratio:
        outcomes.append(fld("E_Z_ratio", by_ratio, e, [f"{rid}_bp"]))
    notes = [f"Table 1 entry {entry}: R2={r2}, R3={r3}."]
    if entry == 1:
        notes.append("Scheme 3 labels its stereochemical ratio column E/Z for 6a (>99:1), while Table 1 labels 6a as Z/E=99/1; the table convention is retained and the inconsistency remains unresolved.")
    records.append(rec(
        rid, 2, "substrate_scope_entry", ps,
        [fld("solvent", "acetone/H2O (4:1 v/v)", e), fld("temperature", "r.t.", e),
         fld("time", {"number": hours, "unit": "h"}, e)],
        outcomes, notes=notes,
    ))

# Page 3: Scheme 4 specific cycloalkene products.
e = ev(3)
scheme4 = [
    ("2o", "I2", "9o", 35, ">99/1", "n=0"),
    ("2p", "I2", "9p", 85, "97/3", "n=1"),
    ("2p", "Br2", "11p", 65, ">99/1", "n=1"),
]
for i, (substrate, halogen, product, yld, ze, note) in enumerate(scheme4, 1):
    rid = f"scheme4_entry{i:02d}"
    records.append(rec(
        rid, 3, "reported_experiment",
        [part(f"{rid}_r", "reactant", e, substrate, f"cyclic allenyl sulfide {substrate} ({note})"),
         part(f"{rid}_x2", "reagent", e, halogen, "iodine" if halogen == "I2" else "bromine", amounts=equiv(2, e)),
         part(f"{rid}_acetone", "solvent", e, "acetone", "acetone"),
         part(f"{rid}_water", "reagent", e, "H2O", "water"),
         part(f"{rid}_p", "product", e, product, f"dehydrated halohydroxylation product {product}")],
        [fld("solvent", "acetone/H2O (4:1 v/v)", e),
         fld("temperature", {"number": 25, "unit": "°C"}, e),
         fld("time", {"number": 11, "unit": "h"}, e)],
        [fld("yield", {"number": yld, "unit": "%"}, e, [f"{rid}_p"]),
         fld("Z_E_ratio", ze, e, [f"{rid}_p"]),
         fld("yield_measurement_basis", None, e, [f"{rid}_p"])],
        notes=["The adjacent text states that iodination products 9o/9p arise by dehydration of the iodohydroxylation product." if halogen == "I2" else "Scheme 4 separately reports the bromination product 11p."],
    ))

# The opening prose on page 3 cites two alternative prior oxidation conditions from reference 9.
for suffix, oxidant, solvent in [
    ("mcpba", "m-CPBA", "CH2Cl2"),
    ("h2o2", "H2O2", "HOAc"),
]:
    rid = f"literature_oxidation_6e_{suffix}"
    records.append(rec(
        rid, 3, "literature_example",
        [part(f"{rid}_r", "reactant", e, "Z-6e", "Z-iodohydroxylation product Z-6e"),
         part(f"{rid}_ox", "reagent", e, oxidant, oxidant),
         part(f"{rid}_solv", "solvent", e, solvent, solvent),
         part(f"{rid}_p", "product", e, "Z-8e", "corresponding sulfoxide Z-8e")],
        [fld("solvent", solvent, e)],
        notes=["The page 3 prose cites this oxidation to reference 9; it is classified as prior literature rather than a new experiment in this article."],
        unresolved=[
            "The cited prose supplies no oxidant amount, temperature, time, yield, scale, workup or purification.",
            "Structures require independent review; the cited source was not supplied.",
        ],
    ))

# Table 2 optimization entries.
table2 = [
    (1, "CuBr2", 2, "CH3CN/H2O (4:1 v/v)", 15, 9, 34, "1.83/1"),
    (2, "CuBr2", 2, "CH3CN/H2O (4:1 v/v)", 25, 7.5, 39, "2.88/1"),
    (3, "CuBr2", 10, "CH3CN/H2O (4:1 v/v)", 25, 6, 30, "99/1"),
    (4, "NBS", 2, "CH3CN/H2O (4:1 v/v)", 50, 3, 10, "99/1"),
    (5, "NBS", 2, "CH3CN/H2O (4:1 v/v)", 25, 9, 31, "99/1"),
    (6, "NBS", 2, "CH3CN/H2O (4:1 v/v)", 0, 7, 49, "4.38/1"),
    (7, "Br2", 2, "CH3CN/H2O (4:1 v/v)", 0, 7, 26, "21/1"),
    (8, "Br2", 2, "CH3CN/H2O (4:1 v/v)", 50, 3, 29, "99/1"),
    (9, "Br2", 2, "CH3CN/H2O (4:1 v/v)", 25, 9, 47, "99/1"),
    (10, "Br2", 2, "CH2Cl2/H2O (4:1 v/v)", 25, 13, 12, "3.94/1"),
    (11, "Br2", 2, "MeCN/CH2Cl2/H2O (2:2:1 v/v/v)", 25, 13, 17, "16/1"),
]
for entry, reagent, eqv, solvent, temp, hours, yld, ze in table2:
    rid = f"table2_entry{entry:02d}"
    records.append(rec(
        rid, 3, "optimization_entry",
        [part(f"{rid}_r", "reactant", e, "2b", "1,2-propadienyl phenyl sulfide"),
         part(f"{rid}_br", "reagent", e, reagent, reagent, amounts=equiv(eqv, e)),
         part(f"{rid}_solv", "solvent", e, solvent, solvent),
         part(f"{rid}_p", "product", e, "10b", "bromohydroxylation product 10b")],
        [fld("solvent", solvent, e), fld("temperature", {"number": temp, "unit": "°C"}, e),
         fld("time", {"number": hours, "unit": "h"}, e)],
        [fld("yield", {"number": yld, "unit": "%"}, e, [f"{rid}_p"]),
         fld("Z_E_ratio", ze, e, [f"{rid}_p"]),
         fld("yield_measurement_basis", None, e, [f"{rid}_p"])],
        notes=[f"Table 2 entry {entry}; solvent identity/ratio follows footnotes a, c and d."],
    ))

# Table 3 optimization entries for 2e. Missing printed entry numbers are retained as printed.
table3 = [
    (1, "NBS", 2, None, None, 25, 12, 34, "27/1"),
    (2, "NBS", 2, None, None, 0, 7, 46, "34/1"),
    (3, "Br2", 1, None, None, 25, 15, 45, "99/1"),
    (4, "Br2", 1, None, None, 0, 6, 54, "99/1"),
    (5, "Br2", 1.5, None, None, 25, 12, 30, "99/1"),
    (7, "Br2", 2, None, None, 25, 12, 39, "99/1"),
    (8, "Br2", 2, "Na2CO3", 1, 25, 10, 51, "99/1"),
    (9, "Br2", 2, "NaHCO3", 1, 25, 6.5, 52, "99/1"),
    (10, "Br2", 2, "K2CO3", 1, 25, 9, 50, "99/1"),
    (11, "Br2", 2, "LiOAc·2H2O", 1, 25, 9, 41, "99/1"),
    (12, "Br2", 2, "Na2CO3", 1, 25, 10, 51, "99/1"),
    (14, "Br2", 2, "Na2CO3", 1, 0, 2, 58, "96/1"),
    (15, "Br2", 2, "Na2CO3", 1, -10, 13, 52, "99/1"),
    (16, "Br2", 2, "Na2CO3", 1.5, 0, 7, 46, "99/1"),
    (17, "Br2", 2, "Na2CO3", 2, 0, 16, 53, "99/1"),
    (18, "Br2", 2.5, "Na2CO3", 1, 0, 6, 45, "99/1"),
]
for entry, reagent, eqv, additive, add_eq, temp, hours, yld, ze in table3:
    rid = f"table3_entry{entry:02d}"
    ps = [part(f"{rid}_r", "reactant", e, "2e", "1,2-heptadienyl phenyl sulfide"),
          part(f"{rid}_br", "reagent", e, reagent, reagent, amounts=equiv(eqv, e)),
          part(f"{rid}_solv", "solvent", e, "MeCN/H2O (4:1 v/v)", "aqueous acetonitrile"),
          part(f"{rid}_p", "product", e, "10e", "bromohydroxylation product 10e")]
    if additive:
        ps.insert(2, part(f"{rid}_add", "reagent", e, additive, additive, amounts=equiv(add_eq, e)))
    records.append(rec(
        rid, 3, "optimization_entry", ps,
        [fld("solvent", "MeCN/H2O (4:1 v/v)", e),
         fld("temperature", {"number": temp, "unit": "°C"}, e),
         fld("time", {"number": hours, "unit": "h"}, e)],
        [fld("yield", {"number": yld, "unit": "%"}, e, [f"{rid}_p"]),
         fld("Z_E_ratio", ze, e, [f"{rid}_p"]),
         fld("yield_measurement_basis", None, e, [f"{rid}_p"])],
        notes=["The Table 3 yield-column header is printed as 10d, while the depicted structure and prose identify the product as 10e; 10e is retained with the source inconsistency flagged."],
        unresolved=[
            "Table 3 contains an internal product-label inconsistency: yield header 10d versus depicted/prose product 10e.",
            "Yield measurement basis, scale, detailed procedure, workup and purification are unavailable in the supplied main text.",
            "Substrate/product structures require independent review.",
        ],
    ))

# Page 4: Table 4 substrate scope.
e = ev(4)
table4 = [
    (1, "H", "H", "2b", 9, 47, "10b", "99/1", True, False),
    (2, "H", "CH3", "2c", 3, 60, "10c", "72/1", False, False),
    (3, "H", "i-Pr", "2d", 4, 61, "10d", "77/1", False, False),
    (4, "H", "n-C4H9", "2e", 2, 58, "10e", "96/1", False, False),
    (6, "H", "n-C7H15", "2f", 5, 72, "10f", "99/1", False, False),
    (7, "CH3", "CH3", "2h", 6, 86, "10h", "99/1", False, False),
    (8, "CH3", "C2H5", "2i", 3, 86, "10i", "99/1", False, False),
    (9, "CH3", "i-Bu", "2j", 5.5, 68, "10j", "56/1", False, False),
    (10, "CH3", "t-C4H9", "2k", 4.5, 85, "10k", "99/1", False, False),
    (11, "C2H5", "C2H5", "2l", 3, 70, "10l", "31/1", False, False),
    (12, "n-C4H9", "n-C4H9", "2m", 3, 54, "10m", "99/1", False, False),
    (13, "n-C5H11", "n-C5H11", "2n", 3, 68, "10n", "99/1", False, False),
    (14, "H", "n-C4H9", "2q", 3, 64, "10q", "36/1", False, True),
]
for entry, r1, r2, substrate, hours, yld, product, ze, no_base, pbr in table4:
    rid = f"table4_entry{entry:02d}"
    ps = [part(f"{rid}_r", "reactant", e, substrate,
               f"allenyl {'p-bromophenyl' if pbr else 'phenyl'} sulfide {substrate}; R1={r1}, R2={r2}"),
          part(f"{rid}_br2", "reagent", e, "Br2", "bromine", amounts=equiv(2, e)),
          part(f"{rid}_solv", "solvent", e, "MeCN/H2O (4:1 v/v)", "aqueous acetonitrile"),
          part(f"{rid}_p", "product", e, product, f"bromohydroxylation product {product}")]
    if not no_base:
        ps.insert(2, part(f"{rid}_base", "reagent", e, "Na2CO3", "sodium carbonate", amounts=equiv(1, e)))
    note = f"Table 4 entry {entry}: R1={r1}, R2={r2}."
    if no_base:
        note += " Footnote b states that no Na2CO3 was used."
    if pbr:
        note += " Footnote c states that p-bromophenyl sulfide was used instead of phenyl sulfide."
    records.append(rec(
        rid, 4, "substrate_scope_entry", ps,
        [fld("solvent", "MeCN/H2O (4:1 v/v)", e),
         fld("temperature", {"number": 0, "unit": "°C"}, e),
         fld("time", {"number": hours, "unit": "h"}, e)],
        [fld("yield", {"number": yld, "unit": "%"}, e, [f"{rid}_p"]),
         fld("Z_E_ratio", ze, e, [f"{rid}_p"]),
         fld("yield_measurement_basis", None, e, [f"{rid}_p"])],
        notes=[note],
    ))

# Scheme 5: two specific 1-alkyl-substituted examples. Page 5 prose repeats them and conflicts for 10s yield.
for substrate, r1, product, yld, ze in [("2r", "n-C4H9", "10r", 35, "43/1"), ("2s", "CH3", "10s", None, "36/1")]:
    rid = f"scheme5_{substrate}"
    extra = ev(5)
    outcomes = [fld("yield", ({"number": yld, "unit": "%"} if yld is not None else None), e, [f"{rid}_p"]),
                fld("Z_E_ratio", ze, e, [f"{rid}_p"]),
                fld("yield_measurement_basis", None, e, [f"{rid}_p"])]
    notes = [f"Scheme 5 example {substrate}, R1={r1}."]
    unresolved = [
        "Yield measurement basis, scale, detailed procedure, workup and purification are unavailable in the supplied main text.",
        "Substrate/product structures require independent review.",
    ]
    if substrate == "2s":
        notes.append("Scheme 5 on page 4 prints 44% for 10s, whereas the page 5 prose states 43%; the structured yield is left null/missing rather than choosing one value.")
        unresolved.append("Conflicting source values for 10s yield: 44% in Scheme 5 versus 43% in page 5 prose.")
    records.append(rec(
        rid, 4, "reported_experiment",
        [part(f"{rid}_r", "reactant", e, substrate, f"1-alkyl-substituted allenyl phenyl sulfide {substrate}; R1={r1}"),
         part(f"{rid}_br2", "reagent", e, "Br2", "bromine", amounts=equiv(2, e)),
         part(f"{rid}_base", "reagent", e, "Na2CO3", "sodium carbonate", amounts=equiv(1, e)),
         part(f"{rid}_solv", "solvent", e, "MeCN/H2O (4:1 v/v)", "aqueous acetonitrile"),
         part(f"{rid}_p", "product", e, product, f"bromohydroxylation product {product}")],
        [fld("solvent", "MeCN/H2O (4:1 v/v)", e), fld("temperature", {"number": 0, "unit": "°C"}, e)],
        outcomes, notes=notes, unresolved=unresolved, extra_evidence=extra,
    ))

# Table 5 optimization of 4a with iodine.
table5 = [
    (1, 2, "7:1", 21, 10, 28, "12.5/1", "default", True),
    (2, 1.2, "4:1", 27, 5.5, 26, None, "default", False),
    (3, 1.5, "4:1", 27, 5.5, 49, None, "default", False),
    (4, 2, "4:1", -10, 10.5, 54, "26/1", "30 min", False),
    (5, 2, "4:1", -5, 10, 70, "41/1", "default", False),
    (6, 2, "4:1", 0, 20, 68, "35/1", "default", False),
    (7, 2, "4:1", 13, 17, 66, "13.5/1", "default", False),
    (8, 2, "4:1", 25, 15, 46, "22/1", "default", False),
    (9, 2, "1:1", 9, 11, 37, "32/1", "default", False),
    (10, 2, "1:4", 5, 11, "trace", None, "default", False),
    (11, 2, "7:1", 22, 20, 75, "16/1", "default", False),
    (12, 2, "7:1", 21, 10, 28, "12.5/1", "default", False),
    (13, 3, "4:1", 0, 17, 73, "52/1", "default", False),
    (14, 4, "4:1", 27, 7.5, 61, "3.50/1", "default", False),
    (15, 4, "4:1", 14, 7, 75, "10/1", "default", False),
    (16, 2, "4:1", 0, 7.5, 61, "3.5/1", "default", False),
    (17, 4, "4:1", 0, 10.5, 69, "99/1", "default", False),
    (18, 5, "1:1", 0, 17.5, 70, "99/1", "default", False),
]
for entry, i_eq, ratio, temp, hours, yld, ze, addition, lioac in table5:
    rid = f"table5_entry{entry:02d}"
    ps = [part(f"{rid}_r", "reactant", e, "4a", "1,2-propadienyl phenyl selenide"),
          part(f"{rid}_i2", "reagent", e, "I2", "iodine", amounts=equiv(i_eq, e)),
          part(f"{rid}_solv", "solvent", e, f"MeCN/H2O ({ratio} v/v)", "aqueous acetonitrile"),
          part(f"{rid}_p", "product", e, "11a", "iodohydroxylation product 11a")]
    if lioac:
        ps.insert(2, part(f"{rid}_add", "reagent", e, "LiOAc·2H2O", "lithium acetate dihydrate", amounts=equiv(2, e)))
    addition_value = ({"number": 30, "unit": "min"} if addition == "30 min" else
                      {"number": 1, "unit": "min", "qualifier": "le", "raw_text": "within a minute"})
    outcomes = [fld("yield", ({"number": yld, "unit": "%"} if isinstance(yld, (int, float)) else yld), e, [f"{rid}_p"]),
                fld("Z_E_ratio", ze, e, [f"{rid}_p"]),
                fld("yield_measurement_basis", None, e, [f"{rid}_p"])]
    notes = [f"Table 5 entry {entry}; footnote {'c' if addition == '30 min' else 'a'} defines substrate-addition time."]
    unresolved = [
        "Yield measurement basis, scale, detailed workup and purification are unavailable in the supplied main text.",
        "Substrate/product structures require independent review.",
    ]
    if ze is None:
        notes.append("Table footnote e states that Z/E was not determined.")
        unresolved.append("Z/E ratio was not determined by the authors.")
    if entry == 18:
        notes.append("Adjacent prose attributes entry 18 to 0 °C in MeCN/H2O 4:1, but the printed row reports a different iodine loading and MeCN/H2O 1:1; the row's iodine amount is already structured on the I2 participant, and the discrepancy is flagged.")
        unresolved.append("Page 4 prose conflicts with Table 5 entry 18 on solvent ratio (4:1 prose versus 1:1 row) and omits the row's 5 equiv I2 detail.")
    records.append(rec(
        rid, 4, "optimization_entry", ps,
        [fld("solvent", f"MeCN/H2O ({ratio} v/v)", e),
         fld("atmosphere", "N2", e),
         fld("temperature", {"number": temp, "unit": "°C"}, e),
         fld("substrate_addition_time", addition_value, e),
         fld("time", {"number": hours, "unit": "h"}, e)],
        outcomes, notes=notes, unresolved=unresolved,
    ))

# Table 6 substrate scope under the printed shared conditions.
table6 = [
    (1, "Ph", "4a", 17.5, 69, "11a", "99/1"),
    (2, "p-CH3C6H4", "4b", 20.5, 72, "11b", "99/1"),
    (3, "o-CH3C6H4", "4c", 10, 72, "11c", "99/1"),
    (4, "m-CH3C6H4", "4d", 19.5, 74, "11d", "28/1"),
    (5, "p-BrC6H4", "4e", 19, 66, "11e", "99/1"),
    (6, "p-ClC6H4", "4f", 19, 72, "11f", "99/1"),
    (7, "p-CH3OC6H4", "4g", 11.5, 74, "11g", "25/1"),
    (8, "PhCH2", "4h", 11.5, 58, "11h", "99/1"),
    (9, "n-C7H15", "4i", 10.5, 64, "11i", "99/1"),
    (10, "n-C12H25", "4j", 8, 33, "11j", "64/1"),
]
for entry, rgrp, substrate, hours, yld, product, ze in table6:
    rid = f"table6_entry{entry:02d}"
    records.append(rec(
        rid, 4, "substrate_scope_entry",
        [part(f"{rid}_r", "reactant", e, substrate, f"allenyl selenide {substrate}; R={rgrp}"),
         part(f"{rid}_i2", "reagent", e, "I2", "iodine", amounts=equiv(4, e)),
         part(f"{rid}_solv", "solvent", e, "MeCN/H2O (4:1 v/v)", "aqueous acetonitrile"),
         part(f"{rid}_p", "product", e, product, f"iodohydroxylation product {product}")],
        [fld("solvent", "MeCN/H2O (4:1 v/v)", e), fld("atmosphere", "N2", e),
         fld("temperature", {"number": 0, "unit": "°C"}, e),
         fld("time", {"number": hours, "unit": "h"}, e)],
        [fld("yield", {"number": yld, "unit": "%"}, e, [f"{rid}_p"]),
         fld("Z_E_ratio", ze, e, [f"{rid}_p"]),
         fld("yield_measurement_basis", None, e, [f"{rid}_p"])],
        notes=[f"Table 6 entry {entry}: selenium substituent R={rgrp}."],
    ))

# Scheme 6 negative/trace results, one record per substrate row.
for substrate, aryl in [("4a", "Ph"), ("4b", "p-CH3C6H4"), ("4o", "o-CH3C6H4")]:
    rid = f"scheme6_{substrate}"
    records.append(rec(
        rid, 4, "reported_experiment",
        [part(f"{rid}_r", "reactant", e, substrate, f"allenyl selenide {substrate}; Ar={aryl}"),
         part(f"{rid}_br2", "reagent", e, "Br2", "bromine", amounts=equiv(2, e)),
         part(f"{rid}_base", "reagent", e, "Na2CO3", "sodium carbonate", amounts=equiv(1, e)),
         part(f"{rid}_solv", "solvent", e, "MeCN/H2O (4:1 v/v)", "aqueous acetonitrile"),
         part(f"{rid}_p", "product", e, "12", f"expected bromohydroxylation product 12 from {substrate}")],
        [fld("solvent", "MeCN/H2O (4:1 v/v)", e), fld("temperature", {"number": 0, "unit": "°C"}, e)],
        [fld("yield", "trace", e, [f"{rid}_p"]), fld("yield_measurement_basis", None, e, [f"{rid}_p"])],
        notes=["Scheme 6 prints trace product, while the adjacent prose describes these reactions as failing to yield the expected products; trace is preserved as the source outcome."],
        unresolved=[
            "Reaction time, yield basis, scale, detailed procedure, workup and purification are not reported in the supplied main text.",
            "Scheme 6 labels the ortho-tolyl substrate 4o; this label conflicts with Table 6, where o-tolyl is 4c, and is preserved without correction.",
            "Substrate/product structures require independent review.",
        ] if substrate == "4o" else [
            "Reaction time, yield basis, scale, detailed procedure, workup and purification are not reported in the supplied main text.",
            "Substrate/product structures require independent review.",
        ],
    ))

# Page 5: Scheme 7 is explicitly prior literature; two mechanistic branches are separate records.
e = ev(5)
for branch, intermediate, product, yld, descriptor in [
    ("z", "13", "Z-14", 83, "less hindered for trans attack of methoxide"),
    ("e", "15", "E-14", 17, "more hindered for trans attack of methoxide"),
]:
    rid = f"scheme7_literature_{branch}_branch"
    item = rec(
        rid, 5, "literature_example",
        [part(f"{rid}_r", "reactant", e, "literature allene", "allene shown in Scheme 7"),
         part(f"{rid}_hg", "reagent", e, "Hg(OAc)2", "mercuric acetate"),
         part(f"{rid}_ome", "unspecified_agent", e, "−OMe", "methoxide"),
         part(f"{rid}_int", "unspecified_agent", e, intermediate, f"sigma-bridged mercurinium intermediate {intermediate}"),
         part(f"{rid}_p", "product", e, product, f"methoxymercuration product {product}")],
        [],
        [fld("yield", {"number": yld, "unit": "%"}, e, [f"{rid}_p"]),
         fld("yield_measurement_basis", None, e, [f"{rid}_p"])],
        notes=[f"Scheme 7 is introduced as a reported prior-literature example (reference 18), not as a new experiment in this paper; branch is described as {descriptor}."],
        unresolved=[
            "Prior-literature experimental conditions, scale, time, temperature, solvent and yield basis are not provided here.",
            "The depicted structures require independent review; no SI/source article was supplied for reference 18.",
        ],
        steps=False,
        extra_evidence=ev(4),
    )
    item["steps"] = [
        {"step_id": "mercuration", "participant_ids": [f"{rid}_r", f"{rid}_hg"], "conditions": []},
        {"step_id": "methoxide_attack", "participant_ids": [f"{rid}_int", f"{rid}_ome"], "conditions": []},
    ]
    records.append(item)

# Scheme 8 is a proposed mechanism, not an individual reported experiment.
rid = "scheme8_proposed_mechanism"
item = rec(
    rid, 5, "mechanism",
    [part("sc8_r", "reactant", e, "1", "generic 1,2-allenyl sulfide/selenide"),
     part("sc8_x2", "reagent", e, "X2", "halogen source"),
     part("sc8_int1", "unspecified_agent", e, "halogen-associated allene", "proposed halogen-associated intermediate"),
     part("sc8_int2", "unspecified_agent", e, "Z-16", "proposed bridged cation intermediate"),
     part("sc8_water", "reagent", e, "H2O", "water"),
     part("sc8_p", "product", e, "halohydroxylation product", "generic Z haloallylic alcohol")],
    [], [],
    notes=["Scheme 8 is the authors' rationale: Y=S with X=I or Br, or Y=Se with X=I; it is classified as mechanism and carries no experimental yield."],
    unresolved=["Proposed generic intermediates and R-group structures are not assigned SMILES."],
    steps=False,
)
item["steps"] = [
    {"step_id": "halogen_association", "participant_ids": ["sc8_r", "sc8_x2"], "conditions": []},
    {"step_id": "bridged_cation_formation", "participant_ids": ["sc8_int1"], "conditions": []},
    {"step_id": "water_attack", "participant_ids": ["sc8_int2", "sc8_water"], "conditions": []},
]
records.append(item)

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"output": str(OUT), "records": len(records)}, ensure_ascii=False))
