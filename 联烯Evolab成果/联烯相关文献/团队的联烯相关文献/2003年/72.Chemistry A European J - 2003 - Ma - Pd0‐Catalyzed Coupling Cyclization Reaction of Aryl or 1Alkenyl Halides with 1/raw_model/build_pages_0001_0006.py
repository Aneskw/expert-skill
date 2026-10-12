#!/usr/bin/env python3
"""Build machine extraction records for PDF pages 1-6 of doc_cc7b51233e5bb98b."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "runs/current/raw_model/extracted_records_pages_0001_0006.json"
COVERAGE = ROOT / "runs/current/coverage/pages_0001_0006.json"
TASKS = ROOT / "runs/current/tasks.json"
DOC = "doc_cc7b51233e5bb98b"


def ev(page: int) -> list[str]:
    return [f"{DOC}:page{page}:text", f"{DOC}:page{page}:image"]


def fact(value, evidence):
    return {
        "value": value,
        "evidence_ids": list(evidence) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def qty(number, unit, raw_text=None):
    value = {"number": number, "unit": unit}
    if raw_text:
        value["raw_text"] = raw_text
    return value


def rng(minimum, maximum, unit, raw_text):
    return {"minimum": minimum, "maximum": maximum, "unit": unit, "raw_text": raw_text}


def field(name, value, evidence, targets=None):
    item = {"name": name, "fact": fact(value, evidence)}
    if targets:
        item["target_entity_ids"] = list(targets)
    return item


SMILES = {
    "iodobenzene": "Ic1ccccc1",
    "bromobenzene": "Brc1ccccc1",
    "p-nitrophenyl iodide": "O=[N+]([O-])c1ccc(I)cc1",
    "methyl 4-iodobenzoate": "COC(=O)c1ccc(I)cc1",
    "5-bromopyrimidine": "Brc1cncnc1",
    "p-methoxyphenyl iodide": "COc1ccc(I)cc1",
    "triethylamine": "CCN(CC)CC",
    "diisopropylethylamine": "CCN(C(C)C)C(C)C",
    "potassium carbonate": "[K+].[K+].[O-]C([O-])=O",
    "silver carbonate": "[Ag+].[Ag+].[O-]C([O-])=O",
    "tetrabutylammonium bromide": "CCCC[N+](CCCC)(CCCC)CCCC.[Br-]",
    "acetonitrile": "CC#N",
    "THF": "C1CCOC1",
    "toluene": "Cc1ccccc1",
    "DMF": "CN(C)C=O",
    "DMA": "CC(=O)N(C)C",
    "DME": "COCCOC",
    "1,4-dioxane": "C1COCCO1",
    "dichloromethane": "ClCCl",
    "ether": "CCOCC",
    "magnesium sulfate": "[Mg+2].[O-]S(=O)(=O)[O-]",
    "hydrochloric acid": "Cl",
    "N,N-dimethylacetamide": "CC(=O)N(C)C",
    "N,N-dimethylpivalamide": "CC(C)(C)C(=O)N(C)C",
    "phenylacetyl chloride": "O=C(Cl)Cc1ccccc1",
}


def participant(entity_id, role, label, evidence, name=None, amounts=None, smiles=None):
    if smiles is None and name in SMILES:
        smiles = SMILES[name]
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


def amount(name, value, evidence):
    return field(name, value, evidence)


def record(rid, kind, pages, participants, steps=None, outcomes=None, notes=None, unresolved=None):
    evidence = []
    for page in pages:
        for item in ev(page):
            if item not in evidence:
                evidence.append(item)
    return {
        "record_id": f"{DOC}:{rid}",
        "document_id": DOC,
        "source_reaction_id": rid,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": evidence,
        "participants": participants,
        "steps": steps or [],
        "outcomes": outcomes or [],
        "notes": [fact(x, evidence) for x in (notes or [])],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved or [
                "Machine extraction requires chemical source review.",
                "No Supporting Information was explicitly supplied or associated.",
            ],
        },
    }


records = []

# Page 1: cited prior-work arrows. These are deliberately not current-paper experiments.
literature = [
    ("eq1_marshall_cycloisomerization", "Rh(I) or Ag(I)", "1,2-dienyl ketone", "substituted furan"),
    ("eq2_hashmi_dimerization", "Pd(II)", "terminal 1,2-allenyl ketone", "2,4-disubstituted furans"),
    ("eq3_hashmi_gold_coupling", "Au(III)", "terminal 1,2-allenyl ketone and alpha,beta-unsaturated ketone", "2,5-disubstituted furan"),
    ("eq4_ma_allenic_acid_coupling", "Pd(II)", "terminal 1,2-allenyl ketone and 1,2-allenic acid", "2,4-disubstituted furan"),
]
for rid, catalyst, substrate, product in literature:
    e = ev(1)
    parts = [
        participant("substrate", "reactant", substrate, e),
        participant("catalyst", "catalyst", catalyst, e),
        participant("product", "product", product, e),
    ]
    if rid in {"eq2_hashmi_dimerization", "eq4_ma_allenic_acid_coupling"}:
        parts.append(participant("solvent", "solvent", "CH3CN", e, "acetonitrile"))
    records.append(record(rid, "literature_example", [1], parts,
                          [{"step_id": "cited_arrow", "participant_ids": [p["entity_id"] for p in parts if p["role"] != "product"], "conditions": []}],
                          notes=["Prior literature reaction shown for context; not a newly reported experiment in this paper."],
                          unresolved=["Generic R-group structures and unreported experimental details remain unresolved."]))

e2 = ev(2)
records.append(record(
    "scheme1_retrosynthetic_analysis", "general_scheme", [2],
    [participant("target", "product", "polysubstituted furan 3", e2),
     participant("allene", "reactant", "generic 1,2-allenyl ketone 1", e2),
     participant("halide", "reactant", "R3-LG", e2),
     participant("pd", "catalyst", "Pd(0)", e2)],
    [{"step_id": "retrosynthetic_arrow", "participant_ids": ["allene", "halide", "pd"], "conditions": []}],
    notes=["Retrosynthetic analysis only; no experimental yield is assigned."],
    unresolved=["All structures are generic R-group drawings."]))


def prep_record(label, scheme, page, product_name, yield_value, substituent_note,
                reactant_label, reagent_labels, step_conditions, extra_pages=None):
    pages = [page] + (extra_pages or [])
    e = ev(page)
    parts = [participant("substrate", "reactant", reactant_label, e)]
    for idx, (lab, role, name) in enumerate(reagent_labels, 1):
        parts.append(participant(f"agent{idx}", role, lab, e, name))
    parts.append(participant("product", "product", label, e, product_name))
    step = {"step_id": scheme, "participant_ids": [p["entity_id"] for p in parts if p["role"] != "product"],
            "conditions": [field(n, v, e) for n, v in step_conditions]}
    return record(f"prep_{label}", "reported_experiment", pages, parts, [step],
                  [field("reported_yield", qty(yield_value, "%"), e, ["product"])],
                  notes=[substituent_note],
                  unresolved=["Yield basis is not stated in the scheme.", "No Supporting Information was explicitly supplied or associated."])


# Page 2, Schemes 2-5: each product/yield is a separate preparation.
scheme2 = [
    ("1a", "heptadeca-3,4-dien-2-one", 40, "R1=CH3; R4=n-C12H25", [5, 6]),
    ("1b", None, 50, "R1=CH3; R4=n-C4H9", []),
    ("1c", None, 44, "R1=CH3; R4=n-C7H15", []),
    ("1d", "1-cyclohexylundeca-2,3-dien-1-one", 37, "R1=cyclohexyl; R4=n-C7H15", [6]),
    ("1e", "2,2-dimethyltrideca-4,5-dien-3-one", 35, "R1=tert-butyl; R4=n-C7H15", [6]),
]
for label, name, y, note, more in scheme2:
    records.append(prep_record(
        label, "scheme2_two_stage", 2, name, y, note, "R4-substituted 1,2-allene",
        [("nBuLi", "reagent", None), ("R1CONMe2", "reactant", None), ("THF", "solvent", "THF")],
        [("temperature_stage_1", qty(-50, "°C")), ("time_stage_1", qty(2, "h")),
         ("temperature_stage_2", qty(-78, "°C"))], more))

for label, r1, y, more in [("1f", "CH3", 30, []), ("1g", "n-C3H7", 35, [6])]:
    records.append(prep_record(
        label, "scheme3_ylide_acylation", 2, "1-phenylhepta-1,2-dien-4-one" if label == "1g" else None,
        y, f"R1={r1}", "phenylacetyl chloride",
        [("Ph3P=CHCOR1", "reactant", None), ("Et3N", "reagent", "triethylamine"),
         ("CH2Cl2", "solvent", "dichloromethane")],
        [("temperature", rng(0, 5, "°C", "0-5 °C"))], more))

for label, r2, y in [("1h", "CH3", 50), ("1i", "n-C4H9", 76), ("1j", "allyl", 60)]:
    records.append(prep_record(
        label, "scheme4_bromination_elimination", 2, None, y, f"R2={r2}",
        "3-substituted 2,4-pentanedione",
        [("Ph3PBr2", "reagent", None), ("CH2Cl2", "solvent", "dichloromethane"),
         ("Et3N", "reagent", "triethylamine"), ("CH3CN", "solvent", "acetonitrile")],
        [("temperature_stage_1", "reflux"), ("temperature_stage_2", qty(80, "°C"))]))

scheme5 = [
    ("1k", "3-butyldeca-3,4-dien-2-one", 51, "R1=CH3; R2=n-C4H9; R4=n-C5H11"),
    ("1l", "3-pentylnona-3,4-dien-2-one", 66, "R1=CH3; R2=n-C5H11; R4=n-C4H9"),
    ("1m", "3-pentyldeca-3,4-dien-2-one", 57, "R1=CH3; R2=n-C5H11; R4=n-C5H11"),
    ("1n", "2-methyl-4-pentyldeca-4,5-dien-3-one", 70, "R1=i-C3H7; R2=n-C5H11; R4=n-C4H9"),
    ("1o", "7-methyl-3-pentylnona-3,4-dien-2-one", 61, "R1=CH3; R2=n-C5H11; R4=2-methylbutyl"),
    ("1p", "1-(4-methylphenyl)-2-butylnona-2,3-dien-1-one", 74, "R1=p-MeC6H4; R2=n-C4H9; R4=n-C5H11"),
    ("1q", "1-(4-trifluoromethylphenyl)-2-butylnona-2,3-dien-1-one", 75, "R1=p-CF3C6H4; R2=n-C4H9; R4=n-C5H11"),
]
for label, name, y, note in scheme5:
    records.append(prep_record(
        label, "scheme5_one_pot_stepwise", 2, name, y, note, "substituted enyne",
        [("R5Li", "reagent", None), ("R1CONMe2", "reactant", None), ("THF", "solvent", "THF")],
        [("temperature_stage_1", rng(-40, 15, "°C", "-40 to 15 °C")),
         ("temperature_stage_2", qty(-78, "°C"))], [6]))


def base_coupling_parts(e, ketone, halide, products, ketone_equiv=None, halide_equiv=None,
                        catalyst=True, catalyst_loading=5, base=None, base_equiv=None,
                        additive=None, additive_equiv=None, solvent=None):
    parts = [participant("ketone", "reactant", ketone, e,
                         amounts=[amount("equivalents", qty(ketone_equiv, "equiv"), e)] if ketone_equiv else [])]
    halide_name = {
        "2a": "iodobenzene", "PhI": "iodobenzene", "PhBr": "bromobenzene",
        "2b": "p-nitrophenyl iodide", "2c": "methyl 4-iodobenzoate",
        "2d": "5-bromopyrimidine", "2f": "p-methoxyphenyl iodide",
    }.get(halide)
    parts.append(participant("halide", "reactant", halide, e, halide_name,
                             amounts=[amount("equivalents", qty(halide_equiv, "equiv"), e)] if halide_equiv else []))
    if catalyst:
        parts.append(participant("catalyst", "catalyst", "Pd(PPh3)4", e,
                                 amounts=[amount("catalyst_loading", qty(catalyst_loading, "mol%"), e)]))
    if base:
        base_name = {"Et3N": "triethylamine", "iPr2NEt": "diisopropylethylamine", "K2CO3": "potassium carbonate"}.get(base)
        parts.append(participant("base", "reagent", base, e, base_name,
                                 amounts=[amount("equivalents", qty(base_equiv, "equiv"), e)] if base_equiv else []))
    if additive:
        additive_name = {"Ag2CO3": "silver carbonate", "TBAB": "tetrabutylammonium bromide"}.get(additive)
        parts.append(participant("additive", "reagent", additive, e, additive_name,
                                 amounts=[amount("equivalents", qty(additive_equiv, "equiv"), e)] if additive_equiv else []))
    if solvent:
        solvent_name = {"MeCN": "acetonitrile", "THF": "THF", "PhMe": "toluene", "DMF": "DMF", "DMA": "DMA", "DME": "DME", "dioxane": "1,4-dioxane"}.get(solvent)
        parts.append(participant("solvent", "solvent", solvent, e, solvent_name))
    for entity, label in products:
        parts.append(participant(entity, "product", label, e))
    return parts


def coupling_step(parts, e, temperature, time):
    conds = [field("temperature", temperature, e), field("time", qty(time, "h"), e)]
    solvent = next((p["label"]["value"] for p in parts if p["role"] == "solvent"), None)
    if solvent:
        conds.append(field("solvent", solvent, e))
    return {"step_id": "coupling_cyclization", "participant_ids": [p["entity_id"] for p in parts if p["role"] != "product"], "conditions": conds}


# Page 3, Table 1 optimization entries.
table1 = [
    (1, 1.5, "MeCN", "Et3N", 1.5, 60, 15, None, 29, None, 9, True),
    (2, 1.5, "THF", "Et3N", 1.5, "reflux", 10, 54, None, 15, None, False),
    (3, 1.2, "THF", "K2CO3", 1.0, "reflux", 11, 38, None, 33, None, False),
    (4, 2.0, "PhMe", "Et3N", 1.5, 100, 12, 53, None, 42, None, False),
    (5, 2.0, "PhMe", "iPr2NEt", 1.5, 100, 12, 30, None, 67, None, False),
    (6, 2.0, "MeCN", "K2CO3", 1.0, 80, 15, 33, None, 28, None, True),
    (7, 2.0, "DMF", "Et3N", 2.0, 80, 15, 39, None, 35, None, True),
    (8, 2.0, "THF", "Et3N", 2.0, "reflux", 12, 83, None, 15, None, False),
    (9, 2.0, "PhMe", "Et3N", 2.0, 80, 12, 88, 75, 9, None, True),
]
for row, ph_eq, solv, base, base_eq, temp, time, y3, iso3, y4, iso4, silver in table1:
    e = ev(3)
    parts = base_coupling_parts(e, "1a", "PhI", [("p3aa", "3aa"), ("p4a", "4a")],
                                halide_equiv=ph_eq, base=base, base_equiv=base_eq,
                                additive="Ag2CO3" if silver else None, additive_equiv=0.1 if silver else None,
                                solvent=solv)
    outs = []
    if y3 is not None:
        outs.append(field("NMR_yield", qty(y3, "%"), e, ["p3aa"]))
    if iso3 is not None:
        outs.append(field("isolated_yield", qty(iso3, "%"), e, ["p3aa"]))
    if y4 is not None:
        outs.append(field("NMR_yield", qty(y4, "%"), e, ["p4a"]))
    if iso4 is not None:
        outs.append(field("isolated_yield", qty(iso4, "%"), e, ["p4a"]))
    notes = ["NMR yields use CH2Br2 as internal standard; parenthesized values are isolated yields."]
    unresolved = ["No Supporting Information was explicitly supplied or associated."]
    if row == 9:
        unresolved.append("Table 1 reports 4a at 9%, whereas nearby prose describes 8%; the table value is retained.")
    records.append(record(f"table1_entry_{row}", "optimization_entry", [3], parts,
                          [coupling_step(parts, e, qty(temp, "°C") if isinstance(temp, (int, float)) else temp, time)], outs, notes, unresolved))


# Page 3, Table 2 substrate scope under Conditions A.
table2 = [
    (1, "1a", "2a", 12, "3aa", 75, 1.0, 2.0),
    (2, "1a", "2b", 13, "3ab", 90, 1.5, 1.0),
    (3, "1a", "2c", 14, "3ac", 94, 2.0, 1.0),
    (4, "1b", "2a", 12, "3ba", 73, 1.0, 2.0),
    (5, "1b", "2b", 9, "3bb", 92, 1.5, 1.0),
    (6, "1b", "2c", 9, "3bc", 85, 1.5, 1.0),
    (7, "1b", "2d", 11, "3bd", 71, 1.5, 1.0),
    (8, "1b", "2e", 11, "3be", 61, 1.5, 1.0),
    (9, "1b", "2f", 10, "3bf", 64, 1.5, 1.0),
    (10, "1c", "2c", 10, "3cc", 98, 2.0, 1.0),
    (11, "1c", "2f", 12, "3cf", 63, 1.5, 1.0),
    (12, "1d", "2a", 13, "3da", 74, 1.5, 1.0),
    (13, "1d", "2c", 16, "3dc", 76, 1.5, 1.0),
    (14, "1f", "2b", 10, "3fb", 51, 1.5, 1.0),
    (15, "1f", "2c", 10, "3fc", 51, 1.5, 1.0),
    (16, "1g", "2b", 12, "3gb", 77, 1.5, 1.0),
    (17, "1g", "2c", 12, "3gc", 73, 1.5, 1.0),
]
for row, ket, hal, time, prod, y, ket_eq, hal_eq in table2:
    pages = [3] + ([6] if row in (1, 2) else [])
    e = ev(3)
    parts = base_coupling_parts(e, ket, hal, [("product", prod)], ket_eq, hal_eq,
                                base="Et3N", base_equiv=2.0, additive="Ag2CO3", additive_equiv=0.1,
                                solvent="PhMe")
    notes = ["Conditions A. Yield basis is not specified in Table 2."]
    if row == 8:
        notes.append("The product alkene is E by the reported 15.6 Hz olefinic coupling constant.")
    records.append(record(f"table2_entry_{row}", "substrate_scope_entry", pages, parts,
                          [coupling_step(parts, e, qty(80, "°C"), time)],
                          [field("reported_yield", qty(y, "%"), e, ["product"])], notes,
                          ["Yield measurement basis is not stated in the table.", "No Supporting Information was explicitly supplied or associated."]))


# Page 3, Table 3 substrate scope. The table header explicitly gives 100 °C.
table3 = [(1, "1h", "2b", 11, "3hb", 79, 2.0), (2, "1h", "2c", 14, "3hc", 68, 1.5),
          (3, "1i", "2d", 17, "3id", 97, 1.5), (4, "1j", "2b", 12, "3jb", 79, 1.5)]
for row, ket, hal, time, prod, y, ket_eq in table3:
    e = ev(3)
    parts = base_coupling_parts(e, ket, hal, [("product", prod)], ket_eq, 1.0,
                                base="Et3N", base_equiv=2.0, additive="Ag2CO3", additive_equiv=0.1,
                                solvent="PhMe")
    records.append(record(f"table3_entry_{row}", "substrate_scope_entry", [3], parts,
                          [coupling_step(parts, e, qty(100, "°C"), time)],
                          [field("reported_yield", qty(y, "%"), e, ["product"])],
                          ["Table 3 header gives 100 °C; the footnote calls these Conditions A."],
                          ["Yield measurement basis is not stated in the table.", "No Supporting Information was explicitly supplied or associated."]))


# Page 4, Table 4 optimization entries.
table4 = [
    (1, "PhI", "PhMe", "Et3N", 2.0, 100, 18, 70, 57, 30, 11, False, True),
    (2, "PhI", "DME", "Et3N", 2.0, "reflux", 10.5, 87, None, 13, None, False, False),
    (3, "PhI", "dioxane", "Et3N", 2.0, 100, 10.5, 77, None, 8, None, False, False),
    (4, "PhI", "DMF", "Et3N", 2.0, 100, 10.5, 90, None, 9, None, False, False),
    (5, "PhI", "MeCN", "Et3N", 2.0, "reflux", 14, 88, None, 11, None, False, False),
    (6, "PhI", "DMA", "Et3N", 2.0, 100, 14, 80, None, 10, None, False, False),
    (7, "PhI", "DMA", "K2CO3", 2.0, 100, 14, 92, None, 8, None, False, False),
    (8, "PhI", "DMA", "K2CO3", 2.0, 100, 10, 90, 72, 0, None, True, False),
    (9, "PhBr", "DMA", "K2CO3", 2.0, 100, 19, 29, None, 1.3, None, True, False),
]
for row, hal, solv, base, beq, temp, time, y3, iso3, y4, iso4, tbab, silver in table4:
    e = ev(4)
    parts = base_coupling_parts(e, "1k", hal, [("p3ka", "3ka"), ("p4k", "4k")],
                                ketone_equiv=None, halide_equiv=2.0, base=base, base_equiv=beq,
                                additive="TBAB" if tbab else ("Ag2CO3" if silver else None),
                                additive_equiv=0.2 if tbab else (0.1 if silver else None), solvent=solv)
    outs = [field("NMR_yield", qty(y3, "%"), e, ["p3ka"]), field("NMR_yield", qty(y4, "%"), e, ["p4k"])]
    if iso3 is not None:
        outs.append(field("isolated_yield", qty(iso3, "%"), e, ["p3ka"]))
    if iso4 is not None:
        outs.append(field("isolated_yield", qty(iso4, "%"), e, ["p4k"]))
    records.append(record(f"table4_entry_{row}", "optimization_entry", [4], parts,
                          [coupling_step(parts, e, qty(temp, "°C") if isinstance(temp, (int, float)) else temp, time)], outs,
                          ["NMR yields use CH2Br2 as internal standard; parenthesized values are isolated yields."],
                          ["No Supporting Information was explicitly supplied or associated."]))


# Page 4, Table 5 scope under Conditions B.
table5 = [
    (1, "1k", "2a", 14, "3ka", 72, 1.0, 2.0, 0.2, None),
    (2, "1k", "2c", 12, "3kc", 94, 2.0, 1.0, 0.2, None),
    (3, "1k", "2e", 13, "3ke", 64, 1.6, 1.0, 0.2, None),
    (4, "1k", "2f", 9, "3kf", 51, 2.0, 1.0, 0.4, ("3ka", 27)),
    (5, "1l", "2a", 10, "3la", 69, 1.0, 2.0, 0.2, None),
    (6, "1m", "2a", 10, "3ma", 59, 1.0, 2.0, 0.2, None),
    (7, "1n", "2a", 10, "3na", 60, 1.0, 2.0, 0.2, None),
    (8, "1o", "2a", 10, "3oa", 67, 1.0, 2.0, 0.2, None),
]
for row, ket, hal, time, prod, y, ket_eq, hal_eq, tbab_eq, byproduct in table5:
    e = ev(4)
    prods = [("product", prod)] + ([('byproduct', byproduct[0])] if byproduct else [])
    parts = base_coupling_parts(e, ket, hal, prods, ket_eq, hal_eq, base="K2CO3", base_equiv=2.0,
                                additive="TBAB", additive_equiv=tbab_eq, solvent="DMA")
    outs = [field("isolated_yield" if row == 1 else "reported_yield", qty(y, "%"), e, ["product"])]
    if byproduct:
        outs.append(field("isolated_yield_based_on_organic_halide", qty(byproduct[1], "%"), e, ["byproduct"]))
    records.append(record(f"table5_entry_{row}", "substrate_scope_entry", [4], parts,
                          [coupling_step(parts, e, qty(100, "°C"), time)], outs,
                          ["Conditions B. The main-product yield basis is not stated in Table 5."],
                          ["Main-product yield measurement basis is not stated in the table.", "No Supporting Information was explicitly supplied or associated."]))


# Page 4 generic route and two mechanistic schemes.
records.append(record(
    "scheme6_general_tetrasubstituted_furan_route", "general_scheme", [4],
    [participant("enyne", "reactant", "generic enyne", ev(4)), participant("r5li", "reagent", "R5Li", ev(4)),
     participant("amide", "reactant", "R1CONMe2", ev(4)), participant("halide", "reactant", "R3X", ev(4)),
     participant("product", "product", "generic 2,3,4,5-tetrasubstituted furan", ev(4))],
    [{"step_id": "general_sequence", "participant_ids": ["enyne", "r5li", "amide", "halide"],
      "conditions": [field("temperature_stage_1", rng(-40, 15, "°C", "-40 to 15 °C"), ev(4)),
                     field("temperature_stage_2", qty(-78, "°C"), ev(4)), field("operation", "Conditions B", ev(4))]}],
    notes=["General synthetic route; individual experiments are represented by their own records."],
    unresolved=["Generic R-group structures are not expanded."]))

records.append(record(
    "scheme7_unexpected_3ka_mechanism", "mechanism", [4],
    [participant("ketone", "reactant", "1k", ev(4)), participant("halide", "reactant", "2f", ev(4), "p-methoxyphenyl iodide"),
     participant("p3kf", "product", "3kf", ev(4)), participant("p3ka", "product", "3ka", ev(4)),
     participant("pd", "catalyst", "Pd(PPh3)4", ev(4))],
    [{"step_id": "proposed_path", "participant_ids": ["ketone", "halide", "pd"], "conditions": [field("operation", "Conditions B", ev(4))]}],
    [field("reported_yield", qty(51, "%"), ev(4), ["p3kf"]), field("reported_yield", qty(27, "%"), ev(4), ["p3ka"])],
    notes=["Mechanistic proposal explaining formation of unexpected 3ka; the quantified experiment is Table 5 entry 4."],
    unresolved=["Intermediates 5 and 6 are proposed, not isolated experimental products."]))

records.append(record(
    "scheme8_plausible_coupling_mechanism", "mechanism", [4, 5],
    [participant("ketone", "reactant", "generic 1,2-allenyl ketone 1", ev(5)),
     participant("halide", "reactant", "R3X", ev(5)), participant("pd", "catalyst", "Pd(0)", ev(5)),
     participant("product", "product", "furan 3", ev(5))],
    [{"step_id": "paths_a_b_c", "participant_ids": ["ketone", "halide", "pd"], "conditions": []}],
    notes=["Plausible mechanism with proposed intermediates 7-13 and paths a-c; no yield is assigned."],
    unresolved=["Proposed intermediates are not treated as isolated compounds."]))


# Page 5 mechanistic control experiments.
controls = [
    ("eq5_deuterium_control", [("d1c", "reactant", "[D]1c", 1.0), ("halide", "reactant", "2c", 0.5)],
     [("product", "3cc", 89)], "Conditions A", ["Starting material is reported as 87% D; product is reported as 0% D."]),
    ("eq6_no_alpha_h_control", [("ketone", "reactant", "1e", 1.0), ("halide", "reactant", "PhI", 4.0)],
     [("product", "3ea", 74)], "Conditions A", ["Control substrate lacks the alpha-prime hydrogen discussed in the mechanistic analysis."]),
    ("scheme9_1p_individual", [("ketone", "reactant", "1p", 1.0), ("halide", "reactant", "2c", 0.5)],
     [("product", "3pc", 90)], "Conditions B", []),
    ("scheme9_1q_individual", [("ketone", "reactant", "1q", 1.0), ("halide", "reactant", "2c", 0.5)],
     [("product", "3qc", 21)], "Conditions B", []),
    ("scheme9_competition_1p_1q", [("ketone1", "reactant", "1p", 1.0), ("ketone2", "reactant", "1q", 1.0),
                                      ("halide", "reactant", "2c", 0.5)],
     [("product1", "3pc", 81), ("product2", "3qc", 11)], "Conditions B", ["One-pot competition experiment."]),
]
for rid, inputs, products, cond, notes in controls:
    e = ev(5)
    parts = [participant(entity, role, label, e,
                         "iodobenzene" if label == "PhI" else ("methyl 4-iodobenzoate" if label == "2c" else None),
                         [amount("equivalents", qty(eqv, "equiv"), e)]) for entity, role, label, eqv in inputs]
    for entity, label, _ in products:
        parts.append(participant(entity, "product", label, e))
    outs = [field("reported_yield", qty(y, "%"), e, [entity]) for entity, _, y in products]
    if rid == "eq5_deuterium_control":
        outs += [field("starting_deuterium_content", qty(87, "%"), e, ["d1c"]),
                 field("product_deuterium_content", qty(0, "%"), e, ["product"])]
    records.append(record(rid, "reported_experiment", [5], parts,
                          [{"step_id": "control_reaction", "participant_ids": [p["entity_id"] for p in parts if p["role"] != "product"],
                            "conditions": [field("operation", cond, e)]}], outs,
                          notes=notes,
                          unresolved=["Detailed operational conditions are referenced only by the named condition set on this page.",
                                      "Yield measurement basis is not explicitly stated here.",
                                      "No Supporting Information was explicitly supplied or associated."]))


# Enrich cross-page preparations and coupling records with explicit page 5-6 quantities/operations.
by_id = {r["source_reaction_id"]: r for r in records}


def add_amount(part, name, value, evidence):
    part["amounts"].append(amount(name, value, evidence))


def add_evidence(rec, page):
    for item in ev(page):
        if item not in rec["evidence_ids"]:
            rec["evidence_ids"].append(item)


# 1a detailed preparation spans pages 5-6.
r = by_id["prep_1a"]
for p in (5, 6):
    add_evidence(r, p)
e56 = ev(5) + ev(6)
sub = next(p for p in r["participants"] if p["entity_id"] == "substrate")
sub["label"] = fact("pentadeca-1,2-diene", e56)
add_amount(sub, "mass", qty(5.0, "g"), e56); add_amount(sub, "amount", qty(24, "mmol"), e56)
nbl = next(p for p in r["participants"] if p["label"]["value"] == "nBuLi")
add_amount(nbl, "concentration", qty(2.0, "M"), e56); add_amount(nbl, "amount", qty(20, "mmol"), e56)
amide = next(p for p in r["participants"] if p["label"]["value"] == "R1CONMe2")
amide["label"] = fact("N,N-dimethylacetamide", e56); amide["name"] = fact("N,N-dimethylacetamide", e56); amide["smiles"] = fact(SMILES["N,N-dimethylacetamide"], e56)
add_amount(amide, "mass", qty(1.7, "g"), e56); add_amount(amide, "amount", qty(20, "mmol"), e56)
prod = next(p for p in r["participants"] if p["entity_id"] == "product")
add_amount(prod, "mass", qty(2.0, "g"), e56)
r["steps"][0]["conditions"] += [field("time_stage_2", qty(2, "h"), e56),
    field("workup", "slow transfer into ice-cooled aqueous HCl, ether extraction, drying over MgSO4, rotary evaporation", e56),
    field("purification", "silica-gel column chromatography, hexanes/ether 100:1", e56)]
r["outcomes"][0]["name"] = "isolated_yield"

# Quantitative summaries for 1d, 1e, 1g, and 1k-q on page 6.
details = {
    "prep_1d": [("substrate", "mass", qty(2.76, "g")), ("substrate", "amount", qty(20.0, "mmol")),
                ("agent1", "amount", qty(20, "mmol")), ("agent2", "mass", qty(3.10, "g")),
                ("agent2", "amount", qty(20.0, "mmol")), ("product", "mass", qty(1.84, "g"))],
    "prep_1e": [("substrate", "mass", qty(3.4, "g")), ("substrate", "amount", qty(24.6, "mmol")),
                ("agent1", "volume", qty(10, "mL")), ("agent1", "concentration", qty(2.0, "M")),
                ("agent1", "amount", qty(20.0, "mmol")), ("agent2", "mass", qty(2.5, "g")),
                ("agent2", "amount", qty(19.3, "mmol")), ("product", "mass", qty(1.5, "g"))],
    "prep_1g": [("substrate", "mass", qty(3.70, "g")), ("substrate", "amount", qty(24, "mmol")),
                ("agent1", "mass", qty(6.92, "g")), ("agent1", "amount", qty(20, "mmol")),
                ("agent2", "mass", qty(3.03, "g")), ("agent2", "amount", qty(30, "mmol")),
                ("product", "mass", qty(1.30, "g"))],
    "prep_1k": [("substrate", "mass", qty(1.25, "g")), ("substrate", "amount", qty(11.5, "mmol")),
                ("agent1", "amount", qty(10, "mmol")), ("agent2", "mass", qty(1.30, "g")),
                ("agent2", "amount", qty(15, "mmol")), ("product", "mass", qty(1.07, "g"))],
    "prep_1l": [("substrate", "mass", qty(2.12, "g")), ("substrate", "amount", qty(16.5, "mmol")),
                ("agent1", "amount", qty(15, "mmol")), ("agent2", "mass", qty(1.44, "g")),
                ("agent2", "amount", qty(16.5, "mmol")), ("product", "mass", qty(2.04, "g"))],
    "prep_1m": [("substrate", "mass", qty(1.34, "g")), ("substrate", "amount", qty(11, "mmol")),
                ("agent1", "amount", qty(10, "mmol")), ("agent2", "mass", qty(1.04, "g")),
                ("agent2", "amount", qty(12, "mmol")), ("product", "mass", qty(1.27, "g"))],
    "prep_1n": [("substrate", "mass", qty(1.34, "g")), ("substrate", "amount", qty(11.0, "mmol")),
                ("agent1", "amount", qty(10.0, "mmol")), ("agent2", "mass", qty(1.72, "g")),
                ("agent2", "amount", qty(15.0, "mmol")), ("product", "mass", qty(1.65, "g"))],
    "prep_1o": [("substrate", "mass", qty(1.34, "g")), ("substrate", "amount", qty(11, "mmol")),
                ("agent1", "amount", qty(10, "mmol")), ("agent2", "mass", qty(1.04, "g")),
                ("agent2", "amount", qty(12, "mmol")), ("product", "mass", qty(1.34, "g"))],
    "prep_1p": [("substrate", "mass", qty(2.16, "g")), ("substrate", "amount", qty(20, "mmol")),
                ("agent1", "amount", qty(20, "mmol")), ("agent2", "mass", qty(4.08, "g")),
                ("agent2", "amount", qty(25, "mmol")), ("product", "mass", qty(4.20, "g"))],
    "prep_1q": [("substrate", "mass", qty(2.00, "g")), ("substrate", "amount", qty(18.5, "mmol")),
                ("agent1", "amount", qty(16, "mmol")), ("agent2", "mass", qty(4.00, "g")),
                ("agent2", "amount", qty(18.4, "mmol")), ("product", "mass", qty(4.04, "g"))],
}
for rid, rows in details.items():
    rec = by_id[rid]
    add_evidence(rec, 6)
    for entity, name, value in rows:
        add_amount(next(p for p in rec["participants"] if p["entity_id"] == entity), name, value, ev(6))
    rec["outcomes"][0]["name"] = "isolated_yield"

# Organolithium solution concentrations/carrier solvents are explicit on pages 5-6.
solution_details = {
    "prep_1a": (2.0, "cyclohexane"), "prep_1d": (2.0, "cyclohexane"),
    "prep_1e": (2.0, "cyclohexane"), "prep_1k": (2.0, "cyclohexane"),
    "prep_1l": (1.6, "Et2O"), "prep_1m": (2.0, "cyclohexane"),
    "prep_1n": (1.6, "Et2O"), "prep_1o": (1.1, "Et2O"),
    "prep_1p": (2.0, "cyclohexane"), "prep_1q": (1.6, "cyclohexane"),
}
for rid, (concentration, carrier) in solution_details.items():
    rec = by_id[rid]
    agent = next(p for p in rec["participants"] if p["entity_id"] == "agent1")
    if not any(x["name"] == "concentration" for x in agent["amounts"]):
        add_amount(agent, "concentration", qty(concentration, "M"), ev(5) if rid == "prep_1a" else ev(6))
    carrier_id = "organolithium_solution_solvent"
    if not any(p["entity_id"] == carrier_id for p in rec["participants"]):
        carrier_name = "ether" if carrier == "Et2O" else None
        rec["participants"].append(participant(carrier_id, "solvent", carrier, ev(5) if rid == "prep_1a" else ev(6), carrier_name))
        rec["steps"][0]["participant_ids"].append(carrier_id)

# Correct explicit identities from page 6 without claiming source verification of structures.
for rid, substrate_label, agent1_label, agent2_label in [
    ("prep_1d", "deca-1,2-diene", "nBuLi", "cyclohexanecarboxylic acid N,N-dimethylamide"),
    ("prep_1e", "deca-1,2-diene", "nBuLi", "N,N-dimethylpivalamide"),
    ("prep_1g", "phenylacetyl chloride", "1-(triphenylphosphoranylidene)pentan-2-one", "Et3N"),
    ("prep_1k", "oct-1-en-3-yne", "nBuLi", "N,N-dimethylacetamide"),
    ("prep_1l", "nona-1-en-3-yne", "nPrLi", "N,N-dimethylacetamide"),
    ("prep_1m", "nona-1-en-3-yne", "nBuLi", "N,N-dimethylacetamide"),
    ("prep_1n", "nona-1-en-3-yne", "nPrLi", "N,N-dimethylisobutyramide"),
    ("prep_1o", "nona-1-en-3-yne", "secBuLi", "N,N-dimethylacetamide"),
    ("prep_1p", "oct-1-en-3-yne", "nBuLi", "4-methylbenzoic acid N,N-dimethylamide"),
    ("prep_1q", "oct-1-en-3-yne", "nBuLi", "4-trifluoromethylbenzoic acid N,N-dimethylamide"),
]:
    rec = by_id[rid]
    for entity, label in [("substrate", substrate_label), ("agent1", agent1_label), ("agent2", agent2_label)]:
        p = next(x for x in rec["participants"] if x["entity_id"] == entity)
        p["label"] = fact(label, ev(6))
        if label in SMILES:
            p["name"] = fact(label, ev(6)); p["smiles"] = fact(SMILES[label], ev(6))

# Add the explicit detailed operations for 1g and 1k.
by_id["prep_1g"]["steps"][0]["conditions"] += [
    field("atmosphere", "Ar", ev(6)), field("operation", "dropwise addition to an ice-cooled solution; TLC monitoring", ev(6)),
    field("workup", "concentration, Et2O addition, Ph3PO precipitation and filtration", ev(6)),
    field("purification", "silica-gel column chromatography, hexanes/ether 100:1", ev(6))]
by_id["prep_1k"]["steps"][0]["conditions"] += [
    field("atmosphere", "Ar", ev(6)), field("solvent_volume", qty(60, "mL"), ev(6)),
    field("temperature_stage_1", qty(-50, "°C"), ev(6)),
    field("temperature_stage_1_warm_to", rng(-25, -10, "°C", "-25 to -10 °C"), ev(6)),
    field("time_stage_1", qty(0.5, "h"), ev(6)), field("temperature_stage_2", qty(-78, "°C"), ev(6)),
    field("time_stage_2", qty(2, "h"), ev(6)),
    field("workup", "pour into ice-cooled 0.2 M HCl, ether extraction, MgSO4 drying, evaporation", ev(6)),
    field("purification", "silica-gel column chromatography, hexanes/ether 100:1", ev(6))]

# Page 6 detailed Conditions A experiment enriches Table 2 entry 1; 3ab line enriches entry 2.
r = by_id["table2_entry_1"]
add_evidence(r, 6)
e6 = ev(6)
for entity, vals in {
    "ketone": [("mass", qty(100, "mg")), ("amount", qty(0.4, "mmol"))],
    "halide": [("mass", qty(163, "mg")), ("amount", qty(0.8, "mmol"))],
    "catalyst": [("mass", qty(23, "mg")), ("amount", qty(0.002, "mmol"))],
    "base": [("mass", qty(81, "mg")), ("amount", qty(0.8, "mmol"))],
    "additive": [("mass", qty(11, "mg")), ("amount", qty(0.04, "mmol"))],
    "solvent": [("volume", qty(5, "mL"))],
    "product": [("mass", qty(98, "mg"))],
}.items():
    part = next(p for p in r["participants"] if p["entity_id"] == entity)
    for name, value in vals:
        add_amount(part, name, value, e6)
r["steps"][0]["conditions"] += [field("atmosphere", "Ar", e6),
    field("operation", "stirred until complete by TLC; solvent removed", e6),
    field("purification", "silica-gel column chromatography with hexanes", e6)]
r["outcomes"][0]["name"] = "isolated_yield"
r["review"]["unresolved"].append("The printed Pd(PPh3)4 mass/amount is internally inconsistent with the nominal catalyst loading; source values are preserved without correction.")

r = by_id["table2_entry_2"]
add_evidence(r, 6)
for entity, vals in {
    "ketone": [("mass", qty(75, "mg")), ("amount", qty(0.3, "mmol"))],
    "halide": [("mass", qty(50, "mg")), ("amount", qty(0.2, "mmol"))],
    "product": [("mass", qty(67, "mg"))],
}.items():
    part = next(p for p in r["participants"] if p["entity_id"] == entity)
    for name, value in vals:
        add_amount(part, name, value, e6)
r["outcomes"][0]["name"] = "isolated_yield"

# Add condition-set participants to controls so footnote/default reagents are not stranded.
for rid in ["eq5_deuterium_control", "eq6_no_alpha_h_control"]:
    rec = by_id[rid]
    e = ev(5)
    extras = [
        participant("catalyst", "catalyst", "Pd(PPh3)4", e, amounts=[amount("catalyst_loading", qty(5, "mol%"), e)]),
        participant("base", "reagent", "Et3N", e, "triethylamine", [amount("equivalents", qty(2.0, "equiv"), e)]),
        participant("additive", "reagent", "Ag2CO3", e, "silver carbonate", [amount("equivalents", qty(0.1, "equiv"), e)]),
        participant("solvent", "solvent", "toluene", e, "toluene"),
    ]
    rec["participants"].extend(extras)
    rec["steps"][0]["participant_ids"].extend([p["entity_id"] for p in extras])
    rec["steps"][0]["conditions"] += [field("temperature", qty(80, "°C"), e), field("solvent", "toluene", e)]
for rid in ["scheme9_1p_individual", "scheme9_1q_individual", "scheme9_competition_1p_1q"]:
    rec = by_id[rid]
    e = ev(5)
    extras = [
        participant("catalyst", "catalyst", "Pd(PPh3)4", e, amounts=[amount("catalyst_loading", qty(5, "mol%"), e)]),
        participant("base", "reagent", "K2CO3", e, "potassium carbonate", [amount("equivalents", qty(2.0, "equiv"), e)]),
        participant("additive", "reagent", "TBAB", e, "tetrabutylammonium bromide", [amount("equivalents", qty(0.2, "equiv"), e)]),
        participant("solvent", "solvent", "DMA", e, "DMA"),
    ]
    rec["participants"].extend(extras)
    rec["steps"][0]["participant_ids"].extend([p["entity_id"] for p in extras])
    rec["steps"][0]["conditions"] += [field("temperature", qty(100, "°C"), e), field("solvent", "DMA", e)]


# Coverage ledger: page records are explicitly mapped to visually inspected regions.
page_ids = {
    1: [r["record_id"] for r in records if r["source_reaction_id"].startswith("eq") and r["record_kind"] == "literature_example"],
    2: [r["record_id"] for r in records if r["source_reaction_id"].startswith("prep_")] + [f"{DOC}:scheme1_retrosynthetic_analysis"],
    3: [r["record_id"] for r in records if r["source_reaction_id"].startswith(("table1_", "table2_", "table3_"))],
    4: [r["record_id"] for r in records if r["source_reaction_id"].startswith(("table4_", "table5_", "scheme6_", "scheme7_", "scheme8_"))],
    5: [r["record_id"] for r in records if r["source_reaction_id"].startswith(("eq5_", "eq6_", "scheme9_", "scheme8_"))] + [f"{DOC}:prep_1a"],
    6: [f"{DOC}:prep_{x}" for x in ["1a", "1d", "1e", "1g", "1k", "1l", "1m", "1n", "1o", "1p", "1q"]]
       + [f"{DOC}:table2_entry_1", f"{DOC}:table2_entry_2"],
}

regions = {
    1: [
        ("title/abstract and introduction", "Article metadata and current-work summary; no standalone experiment extracted from prose."),
        ("Equation (1)", "Prior-literature Rh(I)/Ag(I) cycloisomerization, classified as literature_example."),
        ("Equations (2)-(4)", "Three prior-literature reaction arrows, classified as literature_example rather than current experiments."),
    ],
    2: [
        ("Scheme 1", "Generic retrosynthetic analysis, classified as general_scheme."),
        ("Schemes 2 and 3", "Seven product-specific starting-material preparations with reported yields."),
        ("Schemes 4 and 5", "Ten product-specific starting-material preparations with reported yields and shared staged conditions."),
        ("lower-right coupling-cyclization prose", "Introduces Table 1 and the cycloisomerization side product; quantified rows are recorded on page 3."),
    ],
    3: [
        ("Table 1 including footnotes", "Nine independent optimization entries; NMR versus isolated yields and Ag2CO3 footnote are structured per row."),
        ("Table 2 including footnotes", "Seventeen substrate-scope entries; stoichiometric footnote overrides and E-alkene note are structured."),
        ("Table 3 including footnotes", "Four substrate-scope entries; the explicit 100 °C header and ketone-equivalent exception are retained."),
    ],
    4: [
        ("Table 4 including footnotes", "Nine optimization entries with solvent/base changes, PhBr substitution, TBAB addition, and product-specific yields."),
        ("Table 5 including footnotes", "Eight substrate-scope entries; altered ketone/TBAB loadings and unexpected 3ka coproduct are structured."),
        ("Scheme 6", "Generic multistep route classified as general_scheme."),
        ("Scheme 7", "Proposed pathway for unexpected 3ka classified as mechanism; its actual quantified reaction is Table 5 entry 4."),
        ("Scheme 8 beginning", "Beginning of plausible mechanism; completed and inventoried with page 5 evidence."),
    ],
    5: [
        ("Scheme 8 and mechanism prose", "Plausible mechanistic paths a-c; proposed intermediates are not experimental products."),
        ("Equation (5)", "Deuterium-label control experiment with starting/product D content and product yield."),
        ("Equation (6)", "No-alpha-prime-H control reaction of 1e with PhI."),
        ("Scheme 9", "Two individual electronic-effect reactions and one competition experiment, retained as three distinct records."),
        ("Experimental Section: preparation of 1a", "Detailed procedure begins here and continues on page 6; merged with Scheme 2 preparation record."),
    ],
    6: [
        ("left column: preparations of 1d, 1e, 1g and typical 1k procedure", "Detailed starting-material preparations and quantities merged into page-2 preparation records."),
        ("right column: preparations of 1l-1q", "Product-specific quantitative preparations merged into page-2 records."),
        ("right-lower column: Conditions A and 3aa", "Detailed 1a/PhI coupling operation merged into Table 2 entry 1; printed catalyst inconsistency preserved."),
        ("bottom-right: 3ab experimental paragraph", "Explicit masses, amounts, product mass and isolated yield merged into Table 2 entry 2; characterization continues beyond the scoped pages."),
    ],
}

coverage_pages = []
for page in range(1, 7):
    unresolved = []
    if page == 1:
        unresolved.append("Prior-literature arrows omit full experimental procedures and use generic R groups.")
    if page == 2:
        unresolved.append("Scheme yields do not state a measurement basis; several structures are generic or identified only by labels/substituents.")
    if page == 3:
        unresolved.append("Table 2 and Table 3 yield measurement bases are unstated; Table 1/prose disagree for side-product 4a in the standard condition.")
    if page == 4:
        unresolved.append("Main-product yield basis in Table 5 is not explicitly stated; mechanistic intermediates are proposals.")
    if page == 5:
        unresolved.append("Named condition sets omit repeated operational detail on this page; the 1a procedure continues onto page 6.")
    if page == 6:
        unresolved.append("The 3ab characterization continues on page 7, outside this session's claimed coverage; the printed Pd(PPh3)4 mass/amount is internally inconsistent.")
    coverage_pages.append({
        "page": page,
        "state": "attempted",
        "regions": [{"region": a, "finding": b, "evidence_ids": [f"{DOC}:page{page}:image", f"{DOC}:page{page}:text"]} for a, b in regions[page]],
        "record_ids": sorted(set(page_ids[page])),
        "unresolved": unresolved,
    })

coverage = {"document_id": DOC, "semantic_accuracy_verified": False, "pages": coverage_pages}

OUT.parent.mkdir(parents=True, exist_ok=True)
COVERAGE.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
COVERAGE.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

# Mark only the visually inspected page tasks attempted.
tasks = json.loads(TASKS.read_text())
for task in tasks:
    if task.get("document_id") == DOC and task.get("evidence_id") in {f"{DOC}:page{p}:text" for p in range(1, 7)}:
        task["state"] = "attempted"
        task["visual_evidence_id"] = f"{DOC}:page{task['evidence_id'].split(':page')[1].split(':')[0]}:image"
        task["reason"] = "Page text and original rendered page image were inspected; records and coverage ledger generated."
TASKS.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"records": len(records), "coverage_pages": [p["page"] for p in coverage_pages], "output": str(OUT)}, ensure_ascii=False))
