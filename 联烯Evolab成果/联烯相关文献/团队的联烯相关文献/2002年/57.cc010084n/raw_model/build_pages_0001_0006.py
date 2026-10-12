#!/usr/bin/env python3
"""Build evidence-linked raw records for cc010084n PDF pages 1-6."""
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / "runs/current"
DOC = "doc_d48f453fffb612b1"
OUT = RUN / "raw_model/extracted_records_pages_0001_0006.json"
COVERAGE = RUN / "coverage/pages_0001_0006.json"


def evid(page: int) -> list[str]:
    return [f"{DOC}:page{page}:text", f"{DOC}:page{page}:image"]


def fact(value, evidence=None):
    return {
        "value": value,
        "evidence_ids": list(evidence or []) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def fld(name, value, evidence=None, targets=None):
    result = {"name": name, "fact": fact(value, evidence)}
    if targets:
        result["target_entity_ids"] = list(targets)
    return result


def qty(number, unit, **extra):
    return {"number": number, "unit": unit, **extra}


def part(entity_id, role, label, name, evidence, amounts=None, smiles=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence) if label is not None else fact(None),
        "name": fact(name, evidence) if name is not None else fact(None),
        "smiles": fact(smiles, evidence) if smiles is not None else fact(None),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": list(amounts or []),
    }


def rec(source_id, kind, evidence, participants, steps, outcomes=None, notes=None, unresolved=None):
    return {
        "record_id": f"{DOC}:{source_id}",
        "document_id": DOC,
        "source_reaction_id": source_id,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": list(dict.fromkeys(evidence)),
        "participants": participants,
        "steps": steps,
        "outcomes": list(outcomes or []),
        "notes": [fact(x, evidence) for x in (notes or [])],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": list(unresolved or []),
        },
    }


records = []


def add(record):
    records.append(record)
    return record


COMMON_UNRESOLVED = [
    "Supporting Information is mentioned by the article but was not supplied or explicitly associated.",
    "Participant structures are retained as source labels/descriptions unless an explicit candidate SMILES is supplied; all structures remain unverified.",
]


def arrow(source_id, page, kind, participant_specs, conditions, note):
    ev = evid(page)
    participants = [part(spec[0], spec[1], spec[2], spec[3], ev, spec[4], spec[5])
                    for spec in participant_specs]
    return add(rec(
        source_id, kind, ev, participants,
        [{"step_id": "arrow", "participant_ids": [p["entity_id"] for p in participants],
          "conditions": [fld(n, v, ev) for n, v in conditions]}],
        notes=[note],
        unresolved=COMMON_UNRESOLVED + ["This arrow is a general/cited transformation, not an independently quantified substrate-scope experiment."],
    ))


# Page 1: cited solution-phase precedent, explicitly not a new experiment in this paper.
arrow(
    "eq1_prior_solution_coupling_cyclization", 1, "literature_example",
    [
        ("aryl_iodide", "reactant", "ArI", "aryl iodide", [], None),
        ("allenoic_acid", "reactant", None, "2,3-allenoic acid", [], None),
        ("pd", "catalyst", None, "Pd(PPh3)4", [], None),
        ("ag", "catalyst", "Ag+", "silver(I) cocatalyst (described in prose)", [], None),
        ("base", "reagent", None, "base (unspecified)", [], None),
        ("mecn", "solvent", None, "acetonitrile", [], "CC#N"),
        ("butenolide", "product", None, "aryl-substituted butenolide", [], None),
    ],
    [("solvent", "CH3CN"), ("reaction_temperature", None), ("reaction_time", None)],
    "Equation (1) is explicitly introduced as the authors' 1998 Pd(0)/Ag+ solution-phase precedent (reference 7h).",
)


# Page 2: Scheme 1 (cited prior SPOS model), one record per arrow.
arrow(
    "scheme1_prior_polymer_coupling", 2, "literature_example",
    [
        ("polyaryl", "reactant", None, "polymer-supported aryl iodide", [], None),
        ("acid", "reactant", None, "2,3-allenoic acid", [], None),
        ("pd0", "catalyst", "Pd(0)", "palladium(0) catalyst", [], None),
        ("mecn", "solvent", None, "acetonitrile", [], "CC#N"),
        ("resin_product", "product", None, "polymer-supported butenolide", [], None),
    ],
    [("solvent", "CH3CN"), ("reaction_temperature", None), ("reaction_time", None)],
    "Scheme 1 coupling arrow summarizes the previously reported solid-phase model cited as reference 12.",
)
arrow(
    "scheme1_prior_cleavage", 2, "literature_example",
    [
        ("resin_product", "reactant", None, "polymer-supported butenolide", [], None),
        ("lewis_acid", "reagent", None, "Lewis acid", [], None),
        ("additive", "reagent", None, "additive", [], None),
        ("released", "product", None, "released butenolide derivative", [], None),
    ],
    [("operation", "Lewis-acid-assisted cleavage"), ("reaction_temperature", None), ("reaction_time", None)],
    "Scheme 1 cleavage arrow is a cited/general SPOS operation; the Lewis acid and additive are not identified in this region.",
)


# Page 2: Scheme 2 general arrows.
arrow(
    "scheme2_anchor_iodobenzoic_acids", 2, "general_scheme",
    [
        ("merrifield", "reactant", None, "Merrifield resin", [], None),
        ("iodobenzoic", "reactant", None, "iodobenzoic acid positional isomer", [], None),
        ("cs2co3", "reagent", None, "cesium carbonate", [], None),
        ("ki", "reagent", None, "potassium iodide", [], None),
        ("dmf", "solvent", None, "DMF", [], "CN(C)C=O"),
        ("resin1", "product", "1a-1c", "carboxyl-linked polymer-supported aryl iodide", [], None),
    ],
    [("solvent", "DMF"), ("reaction_temperature", qty(80, "°C")), ("reaction_time", qty(24, "h"))],
    "Scheme 2 anchoring arrow applies to positional isomers 1a-1c; the detailed 1a preparation on page 6 is recorded separately.",
)
arrow(
    "scheme2_conditionsA_coupling", 2, "general_scheme",
    [
        ("resin1", "reactant", "1a-1c", "carboxyl-linked polymer-supported aryl iodide", [], None),
        ("acid", "reactant", "2a-2j", "alkyl-substituted 2,3-allenoic acid", [fld("equivalents", qty(4, "equiv"), evid(2))], None),
        ("pd", "catalyst", None, "Pd(PPh3)4", [fld("amount", qty(15, "mol%"), evid(2))], None),
        ("base", "reagent", None, "N,N-diisopropylethylamine", [], "CCN(C(C)C)C(C)C"),
        ("mecn", "solvent", None, "acetonitrile", [], "CC#N"),
        ("resin3", "product", "3aa-3cj", "polymer-supported butenolide", [], None),
    ],
    [("solvent", "CH3CN"), ("reaction_temperature", qty(70, "°C")), ("reaction_time", qty(3, "d")), ("atmosphere", "argon")],
    "Scheme 2 Conditions A coupling arrow; the page-2 definition does not state a numeric base amount.",
)
arrow(
    "scheme2_AlCl3_cleavage", 2, "general_scheme",
    [
        ("resin3", "reactant", "3aa-3cj", "polymer-supported butenolide", [], None),
        ("alcl3", "reagent", None, "aluminum chloride", [], None),
        ("men2o", "solvent", "MeNO2", "nitromethane", [], "C[N+](=O)[O-]"),
        ("dcm", "solvent", "CH2Cl2", "dichloromethane", [], "ClCCl"),
        ("product4", "product", "4aa-4cj", "carboxyphenyl butenolide", [], None),
    ],
    [("reaction_temperature", qty(0, "°C")), ("reaction_time", qty(30, "min"))],
    "Scheme 2 AlCl3-assisted cleavage arrow.",
)


ACIDS = {
    "2a": "2,3-allenoic acid 2a (R1=n-heptyl, R2=H, R3=H)",
    "2b": "2,3-allenoic acid 2b (R1=n-butyl, R2=H, R3=H)",
    "2c": "2,3-allenoic acid 2c (R1=cyclohexyl, R2=H, R3=H)",
    "2d": "5,5-dimethyl-2,3-hexadienoic acid 2d (R1=tert-butyl, R2=H, R3=H)",
    "2e": "2,3-allenoic acid 2e (R1=n-hexyl, R2=Me, R3=H)",
    "2f": "2,3-allenoic acid 2f (R1=n-propyl, R2=Me, R3=H)",
    "2g": "2,3-allenoic acid 2g (R1=n-propyl, R2=allyl, R3=H)",
    "2h": "2,3-allenoic acid 2h (R1=Me, R2=benzyl, R3=H)",
    "2i": "2,3-allenoic acid 2i (R1=H, R2=benzyl, R3=H)",
    "2j": "2,3-allenoic acid 2j (R1=Me, R2=Me, R3=Me)",
    "2k": "2,3-allenoic acid 2k (Ar=phenyl, R2=Me, R3=H)",
    "2l": "2,3-allenoic acid 2l (Ar=phenyl, R2=n-propyl, R3=H)",
    "2m": "2,3-allenoic acid 2m (Ar=phenyl, R2=benzyl, R3=H)",
    "2n": "2,3-allenoic acid 2n (Ar=alpha-naphthyl, R2=Me, R3=H)",
    "2o": "2,3-allenoic acid 2o (Ar=alpha-naphthyl, R2=n-propyl, R3=H)",
    "2p": "2-methyl-4-phenyl-2,3-hexadienoic acid 2p (Ar=phenyl, R2=Me, R3=Et)",
}


def scope_record(table, entry, page, resin_label, acid_label, intermediate_label, product_label,
                 yield_value, purity_value, condition, linkage, cleavage, prior=False,
                 isolated_yield=None, extra_evidence=None, notes=None, unresolved=None):
    base_ev = evid(page)
    all_ev = list(base_ev)
    if extra_evidence:
        for x in extra_evidence:
            if x not in all_ev:
                all_ev.append(x)
    condition_page = {"A": 4 if table == 4 else page, "B": 3, "C": page, "D": 5}[condition]
    cev = evid(condition_page)
    for x in cev:
        if x not in all_ev:
            all_ev.append(x)
    acid_smiles = "CC(C)(C)C=C=CC(=O)O" if acid_label == "2d" else None
    product_smiles = None
    product_name = f"butenolide product {product_label}"
    if product_label == "4aa":
        product_name = "5-(n-heptyl)-4-(2-carboxyphenyl)-2(5H)-furanone (4aa)"
        product_smiles = "O=C(O)c1ccccc1C2=C(C(CCCCCCC)OC2=O)"
    participants = [
        part("resin", "reactant", resin_label, f"{linkage} polymer-supported aryl iodide {resin_label}", base_ev),
        part("acid", "reactant", acid_label, ACIDS[acid_label], base_ev,
             [fld("equivalents", qty(4, "equiv"), cev)], acid_smiles),
        part("pd", "catalyst", None, "Pd(PPh3)4", cev, [fld("amount", qty(15, "mol%"), cev)]),
        part("base", "reagent", None, "N,N-diisopropylethylamine", cev,
             [fld("equivalents", qty(8, "equiv"), cev)] if condition in {"B", "C", "D"} or table in {3, 4} else [],
             "CCN(C(C)C)C(C)C"),
        part("solvent", "solvent", None, "acetonitrile" if condition == "A" else "toluene", cev,
             smiles="CC#N" if condition == "A" else "Cc1ccccc1"),
        part("intermediate", "product", intermediate_label, f"polymer-supported cyclized intermediate {intermediate_label}", base_ev),
        part("product", "product", product_label, product_name, base_ev, smiles=product_smiles),
    ]
    cleavage_ids = ["intermediate"]
    cleavage_conditions = []
    if cleavage == "AlCl3":
        participants.extend([
            part("cleavage_reagent", "reagent", None, "aluminum chloride", base_ev),
            part("cleavage_solvent", "solvent", "MeNO2", "nitromethane", base_ev, smiles="C[N+](=O)[O-]"),
            part("dcm", "solvent", "CH2Cl2", "dichloromethane", base_ev, smiles="ClCCl"),
        ])
        cleavage_ids += ["cleavage_reagent", "cleavage_solvent", "dcm", "product"]
        cleavage_conditions = [fld("reaction_temperature", qty(0, "°C"), base_ev), fld("reaction_time", qty(30, "min"), base_ev)]
    elif cleavage in {"AcBr2", "AcBr6"}:
        equiv = 2 if cleavage == "AcBr2" else 6
        participants.extend([
            part("znbr2", "reagent", None, "zinc bromide", base_ev, [fld("equivalents", qty(0.5, "equiv"), base_ev)]),
            part("acetyl_bromide", "reagent", "CH3COBr", "acetyl bromide", base_ev, [fld("equivalents", qty(equiv, "equiv"), base_ev)]),
            part("dcm", "solvent", "CH2Cl2", "dichloromethane", base_ev, smiles="ClCCl"),
        ])
        cleavage_ids += ["znbr2", "acetyl_bromide", "dcm", "product"]
        cleavage_conditions = [fld("reaction_temperature", "r.t.", base_ev), fld("reaction_time", qty(24, "h"), base_ev)]
    else:
        participants.extend([
            part("dcm", "solvent", "CH2Cl2", "dichloromethane", evid(5), smiles="ClCCl"),
            part("tfa", "reagent", "TFA", "trifluoroacetic acid", evid(5), smiles="O=C(O)C(F)(F)F"),
            part("methanol", "solvent", "MeOH", "methanol", evid(5), smiles="CO"),
        ])
        cleavage_ids += ["dcm", "tfa", "methanol", "product"]
        cleavage_conditions = [fld("solvent_ratio", "CH2Cl2/TFA/MeOH = 5:1:1", evid(5)), fld("reaction_temperature", "r.t.", evid(5)), fld("reaction_time", qty(12, "h"), evid(5))]
    temp = 90 if condition == "B" else 70
    coupling_conditions = [
        fld("solvent", "CH3CN" if condition == "A" else "toluene", cev),
        fld("reaction_temperature", qty(temp, "°C"), cev),
        fld("reaction_time", qty(3, "d"), cev),
        fld("atmosphere", "argon", cev),
    ]
    if condition == "D":
        coupling_conditions.insert(0, fld("operation", "add N,N-diisopropylethylamine before the 2,3-allenoic acid", cev))
    outcomes = [
        fld("overall_yield", qty(yield_value, "%"), base_ev, ["product"]),
        fld("HPLC_purity", qty(purity_value, "%"), base_ev, ["product"]),
        fld("yield_measurement_basis", "overall yield based on the maximum theoretical loading of aryl iodide on resin", base_ev, ["product"]),
        fld("purity_measurement_basis", "HPLC", base_ev, ["product"]),
    ]
    if isolated_yield is not None:
        outcomes.append(fld("isolated_yield", qty(isolated_yield, "%"), base_ev, ["product"]))
    kind = "literature_example" if prior else "substrate_scope_entry"
    row_notes = [f"Table {table}, entry {entry}; product label and row-specific yield/purity were read from the page image."] + list(notes or [])
    row_unresolved = COMMON_UNRESOLVED + list(unresolved or [])
    return add(rec(
        f"table{table}_entry{entry:02d}", kind, all_ev, participants,
        [
            {"step_id": "coupling_cyclization", "participant_ids": ["resin", "acid", "pd", "base", "solvent", "intermediate"], "conditions": coupling_conditions},
            {"step_id": "cleavage", "participant_ids": cleavage_ids, "conditions": cleavage_conditions},
        ], outcomes, row_notes, row_unresolved,
    ))


# Table 1: 20 independent rows.
T1 = [
    ("1a", "2a", "3aa", "4aa", 100, 90, 100, False),
    ("1b", "2a", "3ba", "4ba", 75, 82, 69, False),
    ("1c", "2a", "3ca", "4ca", 99, 93, 99, False),
    ("1a", "2b", "3ab", "4ab", 100, 85, None, False),
    ("1b", "2b", "3bb", "4bb", 83, 91, None, False),
    ("1c", "2b", "3cb", "4cb", 93, 95, None, True),
    ("1a", "2c", "3ac", "4ac", 100, 96, None, True),
    ("1b", "2c", "3bc", "4bc", 100, 86, None, False),
    ("1c", "2c", "3cc", "4cc", 100, 94, None, True),
    ("1a", "2d", "3ad", "4ad", 87, 95, None, False),
    ("1b", "2d", "3bd", "4bd", 85, 86, None, False),
    ("1c", "2d", "3cd", "4cd", 92, 96, None, False),
    ("1b", "2e", "3be", "4be", 74, 94, None, False),
    ("1c", "2e", "3ce", "4ce", 84, 85, 84, False),
    ("1a", "2f", "3af", "4af", 84, 73, None, False),
    ("1b", "2f", "3bf", "4bf", 100, 91, None, False),
    ("1b", "2g", "3bg", "4bg", 76, 80, None, False),
    ("1b", "2h", "3bh", "4bh", 71, 81, None, False),
    ("1b", "2i", "3bi", "4bi", 70, 73, None, False),
    ("1c", "2j", "3cj", "4cj", 41, 75, None, False),
]
for i, row in enumerate(T1, 1):
    resin, acid, intermediate, product, yld, purity, isolated, prior = row
    scope_record(1, i, 2, resin, acid, intermediate, product, yld, purity, "A", "carboxyl-linked", "AlCl3", prior, isolated)


# Page 3: Scheme 3 solution-phase optimization rows.
def scheme3_record(entry, base_name, solvent_name, yield_i, yield_ii, use_ag=False, use_tbab=False):
    ev = evid(3)
    participants = [
        part("aryl_iodide", "reactant", None, "p-methoxycarbonylphenyl iodide", ev),
        part("acid2k", "reactant", "2k", ACIDS["2k"], ev),
        part("pd", "catalyst", None, "Pd(PPh3)4", ev),
        part("base", "reagent", None, base_name, ev),
        part("solvent", "solvent", None, solvent_name, ev, smiles="CC#N" if solvent_name == "acetonitrile" else "Cc1ccccc1"),
        part("product_i", "product", "I", "coupling-cyclization product I", ev),
        part("product_ii", "product", "II", "cycloisomerization product II", ev),
    ]
    if use_ag:
        participants.append(part("ag2co3", "catalyst", None, "silver carbonate (catalytic)", ev))
    if use_tbab:
        participants.append(part("tbab", "reagent", "TBAB", "tetrabutylammonium bromide phase-transfer catalyst", ev))
    outcomes = [
        fld("yield", "not detected" if yield_i == "no" else ("trace" if yield_i == "trace" else qty(yield_i, "%")), ev, ["product_i"]),
        fld("yield", "not detected" if yield_ii == "no" else ("trace" if yield_ii == "trace" else qty(yield_ii, "%")), ev, ["product_ii"]),
    ]
    return add(rec(
        f"scheme3_entry{entry}", "optimization_entry", ev, participants,
        [{"step_id": "model_reaction", "participant_ids": [p["entity_id"] for p in participants],
          "conditions": [fld("solvent", solvent_name, ev), fld("reaction_temperature", None), fld("reaction_time", None)]}],
        outcomes, [f"Scheme 3 condition row {entry}; each product-specific result is attached to its own product entity."],
        COMMON_UNRESOLVED + ["Reaction temperature, time, reagent amounts, and yield measurement basis are not reported in the inspected Scheme 3 region."],
    ))


scheme3_record(1, "potassium carbonate", "acetonitrile", "no", 99, use_ag=True)
scheme3_record(2, "N,N-diisopropylethylamine", "acetonitrile", "no", 99)
scheme3_record(3, "potassium carbonate", "toluene", 65, "trace", use_tbab=True)
scheme3_record(4, "N,N-diisopropylethylamine", "toluene", 35, "trace")


# Table 2: eight independent rows.
T2 = [
    ("1c", "2k", "5ck", "6ck", 33, 93, None, "B"),
    ("1c", "2l", "5cl", "6cl", 42, 74, None, "B"),
    ("1c", "2m", "5cm", "6cm", 42, 81, None, "B"),
    ("1c", "2n", "5cn", "6cn", 42, 95, 42, "B"),
    ("1a", "2o", "5ao", "6ao", 96, 89, None, "C"),
    ("1b", "2o", "5bo", "6bo", 77, 82, None, "C"),
    ("1c", "2o", "5co", "6co", 52, 90, None, "B"),
    ("1c", "2p", "5cp", "6cp", 70, 93, None, "B"),
]
for i, row in enumerate(T2, 1):
    resin, acid, intermediate, product, yld, purity, isolated, cond = row
    unresolved = []
    notes = []
    if i == 1:
        notes.append("The adjacent prose reports 33% yield and 91% purity for the organic-base SPOS comparison, whereas Table 2 gives 33% and 93%.")
        unresolved.append("Source-internal purity discrepancy for the organic-base SPOS experiment: prose 91% versus Table 2 93%.")
    scope_record(2, i, 3, resin, acid, intermediate, product, yld, purity, cond, "carboxyl-linked", "AlCl3", False, isolated, notes=notes, unresolved=unresolved)


# Distinct inorganic-base SPOS comparison described in page-3 prose.
ev3 = evid(3)
add(rec(
    "page3_spos_inorganic_base_comparison", "optimization_entry", ev3,
    [
        part("resin", "reactant", "1c", "carboxyl-linked polymer-supported aryl iodide 1c", ev3),
        part("acid", "reactant", "2k", ACIDS["2k"], ev3),
        part("k2co3", "reagent", None, "potassium carbonate", ev3),
        part("tbab", "reagent", "TBAB", "tetrabutylammonium bromide", ev3),
        part("toluene", "solvent", "PhMe", "toluene", ev3, smiles="Cc1ccccc1"),
        part("product", "product", None, "SPOS coupling-cyclization product from acid 2k", ev3),
    ],
    [{"step_id": "spos_comparison", "participant_ids": ["resin", "acid", "k2co3", "tbab", "toluene", "product"],
      "conditions": [fld("solvent", "toluene", ev3), fld("reaction_temperature", None), fld("reaction_time", None)]}],
    [fld("overall_yield", qty(50, "%"), ev3, ["product"]), fld("HPLC_purity", qty(28, "%"), ev3, ["product"])],
    ["The prose compares this inorganic-base SPOS trial with the organic-base trial represented by Table 2 entry 1."],
    COMMON_UNRESOLVED + ["The prose does not restate temperature, time, reagent amounts, or the exact product label for this comparison."],
))


# Page 3: Scheme 4 arrows.
arrow(
    "scheme4_conditionsB_coupling", 3, "general_scheme",
    [
        ("resin1", "reactant", "1a-1c", "carboxyl-linked polymer-supported aryl iodide", [], None),
        ("acid", "reactant", "2k-2p", "aryl-substituted 2,3-allenoic acid", [fld("equivalents", qty(4, "equiv"), evid(3))], None),
        ("pd", "catalyst", None, "Pd(PPh3)4", [fld("amount", qty(15, "mol%"), evid(3))], None),
        ("base", "reagent", None, "N,N-diisopropylethylamine", [fld("equivalents", qty(8, "equiv"), evid(3))], "CCN(C(C)C)C(C)C"),
        ("toluene", "solvent", None, "toluene", [], "Cc1ccccc1"),
        ("resin5", "product", "5", "polymer-supported butenolide resin 5", [], None),
    ],
    [("solvent", "toluene"), ("reaction_temperature", qty(90, "°C")), ("reaction_time", qty(3, "d")), ("atmosphere", "argon")],
    "Scheme 4 Conditions B coupling arrow.",
)
arrow(
    "scheme4_AlCl3_cleavage", 3, "general_scheme",
    [
        ("resin5", "reactant", "5", "polymer-supported butenolide resin 5", [], None),
        ("alcl3", "reagent", None, "aluminum chloride", [], None),
        ("men2o", "solvent", "MeNO2", "nitromethane", [], "C[N+](=O)[O-]"),
        ("dcm", "solvent", "CH2Cl2", "dichloromethane", [], "ClCCl"),
        ("product6", "product", "6", "carboxyphenyl butenolide 6", [], None),
    ],
    [("reaction_temperature", qty(0, "°C")), ("reaction_time", qty(30, "min"))],
    "Scheme 4 AlCl3-assisted cleavage arrow.",
)


# Page 4: Scheme 5 arrows.
arrow(
    "scheme5_anchor_iodophenols", 4, "general_scheme",
    [
        ("merrifield", "reactant", None, "Merrifield resin", [], None),
        ("iodophenol", "reactant", None, "iodophenol positional isomer", [], None),
        ("meona", "reagent", "MeONa", "sodium methoxide", [], None),
        ("dmf", "solvent", None, "DMF", [], "CN(C)C=O"),
        ("resin7", "product", "7a-7c", "phenolic-ether-linked polymer-supported aryl iodide", [], None),
    ],
    [("solvent", "DMF"), ("reaction_temperature", qty(80, "°C")), ("reaction_time", None)],
    "Scheme 5 anchoring arrow; reaction time is not printed next to this arrow.",
)
arrow(
    "scheme5_conditionsA_or_C_coupling", 4, "general_scheme",
    [
        ("resin7", "reactant", "7a-7c", "phenolic-ether-linked polymer-supported aryl iodide", [], None),
        ("acid", "reactant", "2", "2,3-allenoic acid", [fld("equivalents", qty(4, "equiv"), evid(4))], None),
        ("pd", "catalyst", None, "Pd(PPh3)4", [fld("amount", qty(15, "mol%"), evid(4))], None),
        ("base", "reagent", None, "N,N-diisopropylethylamine", [fld("equivalents", qty(8, "equiv"), evid(4))], "CCN(C(C)C)C(C)C"),
        ("resin8", "product", "8", "polymer-supported butenolide resin 8", [], None),
    ],
    [("operation", "Conditions A for 2a-2e; Conditions C for 2k-2p"), ("reaction_temperature", qty(70, "°C")), ("reaction_time", qty(3, "d")), ("atmosphere", "argon")],
    "Scheme 5 coupling arrow; Conditions A use CH3CN and Conditions C use toluene.",
)
arrow(
    "scheme5_ZnBr2_AcBr_cleavage", 4, "general_scheme",
    [
        ("resin8", "reactant", "8", "polymer-supported butenolide resin 8", [], None),
        ("znbr2", "reagent", None, "zinc bromide", [fld("equivalents", qty(0.5, "equiv"), evid(4))], None),
        ("acbr", "reagent", "CH3COBr", "acetyl bromide", [fld("equivalents", qty(2, "equiv"), evid(4))], None),
        ("dcm", "solvent", "CH2Cl2", "dichloromethane", [], "ClCCl"),
        ("product9", "product", "9", "acetoxyphenyl butenolide 9", [], None),
    ],
    [("reaction_temperature", "r.t."), ("reaction_time", qty(24, "h"))],
    "Scheme 5 ZnBr2/acetyl bromide cleavage arrow.",
)


# Table 3: 23 independent rows. The printed 8cc/9cc labels in entry 17 are retained.
T3 = [
    ("7a", "2a", "8aa", "9aa", 55, 92, "A", False),
    ("7b", "2a", "8ba", "9ba", 100, 98, "A", False),
    ("7c", "2a", "8ca", "9ca", 89, 94, "A", True),
    ("7a", "2b", "8ab", "9ab", 57, 91, "A", False),
    ("7b", "2b", "8bb", "9bb", 100, 91, "A", False),
    ("7c", "2b", "8cb", "9cb", 87, 83, "A", True),
    ("7a", "2c", "8ac", "9ac", 72, 95, "A", False),
    ("7b", "2c", "8bc", "9bc", 100, 93, "A", False),
    ("7c", "2c", "8cc", "9cc", 84, 87, "A", True),
    ("7a", "2d", "8ad", "9ad", 82, 90, "A", False),
    ("7b", "2d", "8bd", "9bd", 100, 98, "A", False),
    ("7c", "2d", "8cd", "9cd", 75, 82, "A", False),
    ("7b", "2e", "8be", "9be", 89, 94, "A", False),
    ("7c", "2e", "8ce", "9ce", 82, 76, "A", True),
    ("7c", "2k", "8ck", "9ck", 80, 59, "C", False),
    ("7c", "2l", "8cl", "9cl", 74, 73, "C", False),
    ("7c", "2m", "8cc", "9cc", 63, 82, "C", False),
    ("7c", "2n", "8cn", "9cn", 75, 92, "C", False),
    ("7a", "2o", "8ao", "9ao", 63, 90, "C", False),
    ("7b", "2o", "8bo", "9bo", 65, 92, "C", False),
    ("7c", "2o", "8co", "9co", 84, 89, "C", False),
    ("7b", "2p", "8bp", "9bp", 93, 82, "C", False),
    ("7c", "2p", "8cp", "9cp", 71, 82, "C", False),
]
for i, row in enumerate(T3, 1):
    resin, acid, intermediate, product, yld, purity, cond, prior = row
    unresolved = []
    notes = []
    if i == 17:
        notes.append("The page image prints intermediate/product labels as 8cc/9cc for acid 2m; these labels are retained rather than silently corrected.")
        unresolved.append("Table 3 entry 17 label conflicts with the table's stated second-letter acid-label convention (acid 2m versus printed 8cc/9cc).")
    scope_record(3, i, 4, resin, acid, intermediate, product, yld, purity, cond, "phenolic-ether-linked", "AcBr2", prior, notes=notes, unresolved=unresolved)


# Page 4: Scheme 6 coupling arrow and three distinct cleavage-condition rows.
arrow(
    "scheme6_coupling_to_11ca", 4, "general_scheme",
    [
        ("resin10c", "reactant", "10c", "benzyl-ether-linked polymer-supported aryl iodide 10c", [], None),
        ("acid2a", "reactant", "2a", ACIDS["2a"], [], None),
        ("pd0", "catalyst", "Pd(0)", "palladium(0) catalyst", [], None),
        ("base", "reagent", None, "N,N-diisopropylethylamine", [], "CCN(C(C)C)C(C)C"),
        ("mecn", "solvent", "CH3CN", "acetonitrile", [], "CC#N"),
        ("resin11ca", "product", "11ca", "polymer-supported butenolide resin 11ca", [], None),
    ],
    [("solvent", "CH3CN"), ("reaction_temperature", qty(70, "°C")), ("reaction_time", None)],
    "Scheme 6 coupling arrow leading to resin 11ca; the cleavage optimization is represented by three separate records.",
)


def scheme6_cleavage(letter, acbr_equiv, kind, iii_yield=None, iii_purity=None, iii_isolated=None,
                     bromide_yield=None, bromide_purity=None, mixture=False):
    ev = evid(4)
    participants = [
        part("resin11ca", "reactant", "11ca", "polymer-supported butenolide resin 11ca", ev),
        part("znbr2", "reagent", None, "zinc bromide", ev, [fld("equivalents", qty(0.5, "equiv"), ev)]),
        part("acbr", "reagent", "CH3COBr", "acetyl bromide", ev, [fld("equivalents", qty(acbr_equiv, "equiv"), ev)]),
        part("dcm", "solvent", "CH2Cl2", "dichloromethane", ev, smiles="ClCCl"),
        part("iii", "product", "III", "benzyl acetate product III", ev),
        part("product12ca", "product", "12ca", "benzyl bromide product 12ca", ev),
    ]
    outcomes = []
    if mixture:
        outcomes.append(fld("product_distribution", "mixture of III and 12ca", ev, ["iii", "product12ca"]))
    else:
        if iii_yield is not None:
            outcomes.append(fld("overall_yield", "trace" if iii_yield == "trace" else qty(iii_yield, "%"), ev, ["iii"]))
        if iii_purity is not None:
            outcomes.append(fld("HPLC_purity", qty(iii_purity, "%"), ev, ["iii"]))
        if iii_isolated is not None:
            outcomes.append(fld("isolated_yield", qty(iii_isolated, "%"), ev, ["iii"]))
        if bromide_yield is not None:
            outcomes.append(fld("overall_yield", "trace" if bromide_yield == "trace" else qty(bromide_yield, "%"), ev, ["product12ca"]))
        if bromide_purity is not None:
            outcomes.append(fld("HPLC_purity", qty(bromide_purity, "%"), ev, ["product12ca"]))
    return add(rec(
        f"scheme6_entry_{letter}", kind, ev, participants,
        [{"step_id": "cleavage", "participant_ids": [p["entity_id"] for p in participants],
          "conditions": [fld("reaction_temperature", "r.t.", ev), fld("reaction_time", qty(24, "h"), ev)]}],
        outcomes,
        [f"Scheme 6 entry {letter}; acetyl bromide loading is the varied parameter."],
        COMMON_UNRESOLVED + (["No numeric component yields or purities are reported for the mixture in entry b."] if mixture else []),
    ))


scheme6_cleavage("a", 2.0, "literature_example", iii_yield=75, iii_purity=82, iii_isolated=68, bromide_yield="trace")
scheme6_cleavage("b", 4.0, "optimization_entry", mixture=True)
scheme6_cleavage("c", 6.0, "optimization_entry", iii_yield="trace", bromide_yield=70, bromide_purity=86)


# Page 5: Scheme 7 arrows.
arrow(
    "scheme7_anchor_iodobenzyl_alcohols", 5, "general_scheme",
    [
        ("merrifield", "reactant", None, "Merrifield resin", [], None),
        ("iodobenzyl_alcohol", "reactant", None, "iodobenzyl alcohol positional isomer", [], None),
        ("nah", "reagent", None, "sodium hydride", [], None),
        ("thf", "solvent", None, "THF", [], "C1CCOC1"),
        ("resin10", "product", "10", "benzyl-ether-linked polymer-supported aryl iodide", [], None),
    ],
    [("solvent", "THF"), ("reaction_temperature", "reflux"), ("reaction_time", qty(3, "d"))],
    "Scheme 7 anchoring arrow.",
)
arrow(
    "scheme7_conditionsC_coupling", 5, "general_scheme",
    [
        ("resin10", "reactant", "10", "benzyl-ether-linked polymer-supported aryl iodide", [], None),
        ("acid", "reactant", "2", "2,3-allenoic acid", [fld("equivalents", qty(4, "equiv"), evid(5))], None),
        ("pd", "catalyst", None, "Pd(PPh3)4", [fld("amount", qty(15, "mol%"), evid(5))], None),
        ("base", "reagent", None, "N,N-diisopropylethylamine", [fld("equivalents", qty(8, "equiv"), evid(5))], "CCN(C(C)C)C(C)C"),
        ("toluene", "solvent", None, "toluene", [], "Cc1ccccc1"),
        ("resin11", "product", "11", "polymer-supported butenolide resin 11", [], None),
    ],
    [("solvent", "toluene"), ("reaction_temperature", qty(70, "°C")), ("reaction_time", qty(3, "d")), ("atmosphere", "argon")],
    "Scheme 7 Conditions C coupling arrow.",
)
arrow(
    "scheme7_ZnBr2_AcBr_cleavage", 5, "general_scheme",
    [
        ("resin11", "reactant", "11", "polymer-supported butenolide resin 11", [], None),
        ("znbr2", "reagent", None, "zinc bromide", [fld("equivalents", qty(0.5, "equiv"), evid(5))], None),
        ("acbr", "reagent", "CH3COBr", "acetyl bromide", [fld("equivalents", qty(6, "equiv"), evid(5))], None),
        ("dcm", "solvent", "CH2Cl2", "dichloromethane", [], "ClCCl"),
        ("product12", "product", "12", "benzyl bromide butenolide 12", [], None),
    ],
    [("reaction_temperature", "r.t."), ("reaction_time", qty(24, "h"))],
    "Scheme 7 ZnBr2/acetyl bromide cleavage arrow; the explicit loading is structured on the acetyl bromide participant.",
)


# Table 4: ten independent rows.
T4 = [
    ("10c", "2a", "11ca", "12ca", 70, 86, "A"),
    ("10a", "2b", "11ab", "12ab", 96, 84, "A"),
    ("10c", "2b", "11cb", "12cb", 77, 74, "A"),
    ("10a", "2c", "11ac", "12ac", 100, 89, "A"),
    ("10c", "2c", "11cc", "12cc", 75, 93, "A"),
    ("10a", "2d", "11ad", "12ad", 100, 82, "A"),
    ("10c", "2d", "11cd", "12cd", 81, 77, "C"),
    ("10c", "2e", "11ce", "12ce", 59, 85, "C"),
    ("10c", "2o", "11co", "12co", 99, 81, "C"),
    ("10c", "2p", "11cp", "12cp", 87, 90, "C"),
]
for i, row in enumerate(T4, 1):
    resin, acid, intermediate, product, yld, purity, cond = row
    unresolved = []
    notes = []
    if i in {9, 10}:
        notes.append("Table 4 footnote explicitly assigns Conditions C only to entries 7 and 8, while Scheme 7 and the acid-class discussion indicate Conditions C for the aryl-substituted acids; the row is provisionally linked to Conditions C.")
        unresolved.append("Condition assignment for Table 4 entries 9-10 is not enumerated in the table footnote and requires source review.")
    extra = evid(4) if cond == "A" else None
    scope_record(4, i, 5, resin, acid, intermediate, product, yld, purity, cond, "benzyl-ether-linked", "AcBr6", False, extra_evidence=extra, notes=notes, unresolved=unresolved)


# Page 5: explicit unsuccessful THP addition-order trial.
ev5 = evid(5)
add(rec(
    "page5_thp_acid_before_base_failure", "optimization_entry", ev5,
    [
        part("thp_resin", "reactant", "13 or 14", "THP-linked polymer-supported aryl iodide", ev5),
        part("acid", "reactant", "2", "2,3-allenoic acid", ev5),
        part("base", "reagent", None, "N,N-diisopropylethylamine", ev5, smiles="CCN(C(C)C)C(C)C"),
        part("cleaved_material", "product", None, "acid-cleaved linker material", ev5),
    ],
    [{"step_id": "failed_addition_order", "participant_ids": ["thp_resin", "acid", "base", "cleaved_material"],
      "conditions": [fld("operation", "2,3-allenoic acid added before organic base", ev5), fld("reaction_temperature", None), fld("reaction_time", None)]}],
    [fld("result", "unsuccessful; the 2,3-allenoic acid cleaved the linker from Merrifield resin", ev5, ["cleaved_material"])],
    ["The failed result is explicitly reported in the page-5 prose and is retained as an optimization entry."],
    COMMON_UNRESOLVED + ["No substrate identity, temperature, time, or quantitative outcome is reported for the failed initial experiment."],
))


# Page 5: Scheme 8, one record per arrow.
arrow(
    "scheme8_prepare_DHP_resin", 5, "general_scheme",
    [
        ("merrifield", "reactant", None, "Merrifield resin", [], None),
        ("dhp_alkoxide", "reactant", None, "sodium alkoxide of (2-hydroxymethyl)-3,4-dihydro-2H-pyran", [], None),
        ("dma", "solvent", "DMA", "N,N-dimethylacetamide", [], "CC(=O)N(C)C"),
        ("dhp_resin", "product", None, "DHP-functionalized resin", [], None),
    ],
    [("solvent", "DMA"), ("reaction_temperature", "r.t."), ("reaction_time", qty(16, "h"))],
    "Scheme 8 DHP-resin preparation arrow.",
)
arrow(
    "scheme8_anchor_iodobenzyl_alcohol_or_iodophenol", 5, "general_scheme",
    [
        ("dhp_resin", "reactant", None, "DHP-functionalized resin", [], None),
        ("aryl_iodide", "reactant", None, "iodobenzyl alcohol or iodophenol", [], None),
        ("ppts", "reagent", "PPTS", "pyridinium p-toluenesulfonate", [], None),
        ("dce", "solvent", None, "1,2-dichloroethane", [], "ClCCCl"),
        ("resin13_14", "product", "13 or 14", "THP-linked polymer-supported aryl iodide", [], None),
    ],
    [("solvent", "1,2-dichloroethane"), ("reaction_temperature", qty(80, "°C")), ("reaction_time", qty(16, "h"))],
    "Scheme 8 anchoring arrow for alcohol-derived resin 13 or phenol-derived resin 14.",
)
arrow(
    "scheme8_conditionsD_coupling", 5, "general_scheme",
    [
        ("resin13_14", "reactant", "13 or 14", "THP-linked polymer-supported aryl iodide", [], None),
        ("base", "reagent", None, "N,N-diisopropylethylamine", [fld("equivalents", qty(8, "equiv"), evid(5))], "CCN(C(C)C)C(C)C"),
        ("acid", "reactant", "2", "2,3-allenoic acid", [fld("equivalents", qty(4, "equiv"), evid(5))], None),
        ("pd", "catalyst", None, "Pd(PPh3)4", [fld("amount", qty(15, "mol%"), evid(5))], None),
        ("toluene", "solvent", None, "toluene", [], "Cc1ccccc1"),
        ("resin15_16", "product", "15 or 16", "THP-linked polymer-supported butenolide", [], None),
    ],
    [("operation", "add base before 2,3-allenoic acid"), ("solvent", "toluene"), ("reaction_temperature", qty(70, "°C")), ("reaction_time", qty(3, "d")), ("atmosphere", "argon")],
    "Scheme 8 Conditions D coupling arrow; addition order is explicitly significant.",
)
arrow(
    "scheme8_TFA_cleavage", 5, "general_scheme",
    [
        ("resin15_16", "reactant", "15 or 16", "THP-linked polymer-supported butenolide", [], None),
        ("dcm", "solvent", "CH2Cl2", "dichloromethane", [], "ClCCl"),
        ("tfa", "reagent", "TFA", "trifluoroacetic acid", [], "O=C(O)C(F)(F)F"),
        ("methanol", "solvent", "MeOH", "methanol", [], "CO"),
        ("product17_18", "product", "17 or 18", "released benzyl alcohol or phenol butenolide", [], None),
    ],
    [("solvent_ratio", "CH2Cl2/TFA/MeOH = 5:1:1"), ("reaction_temperature", "r.t."), ("reaction_time", qty(12, "h"))],
    "Scheme 8 THP-linker cleavage arrow.",
)


# Page 6: Table 5, fifteen independent rows.
T5 = [
    ("13c", "2a", "15ca", "17ca", 64, 83),
    ("13c", "2b", "15cb", "17cb", 65, 88),
    ("13c", "2c", "15cc", "17cc", 75, 82),
    ("13c", "2d", "15cd", "17cd", 67, 77),
    ("13c", "2k", "15ck", "17ck", 68, 66),
    ("13c", "2l", "15cl", "17cl", 52, 51),
    ("13a", "2n", "15an", "17an", 36, 54),
    ("13c", "2n", "15cn", "17cn", 73, 75),
    ("13c", "2o", "15co", "17co", 63, 81),
    ("13c", "2p", "15cp", "17cp", 34, 92),
    ("14a", "2a", "16aa", "18aa", 22, 89),
    ("14c", "2a", "16ca", "18ca", 42, 72),
    ("14c", "2l", "16cl", "18cl", 43, 68),
    ("14c", "2o", "16co", "18co", 45, 78),
    ("14c", "2p", "16cp", "18cp", 23, 83),
]
for i, row in enumerate(T5, 1):
    resin, acid, intermediate, product, yld, purity = row
    linkage = "benzyl-alcohol THP-linked" if resin.startswith("13") else "phenolic THP-linked"
    scope_record(5, i, 6, resin, acid, intermediate, product, yld, purity, "D", linkage, "TFA", False, extra_evidence=evid(5))


# Page 6: cited starting-material preparations (not claimed as experiments of this paper).
arrow(
    "page6_prior_preparation_acids_2a_2d", 6, "literature_example",
    [
        ("allene", "reactant", None, "corresponding 1,2-allene", [], None),
        ("nbuli", "reagent", "n-BuLi", "n-butyllithium", [], "[Li]CCCC"),
        ("allenyl_lithium", "product", None, "corresponding 1,2-allenic lithium", [], None),
        ("co2", "reactant", "CO2", "carbon dioxide", [], "O=C=O"),
        ("acids", "product", "2a-2d", "2,3-allenoic acids 2a-2d", [], None),
    ],
    [("operation", "lithiation followed by reaction with CO2"), ("reaction_temperature", None), ("reaction_time", None)],
    "The Starting Materials section attributes this preparation to known method 13b.",
)
arrow(
    "page6_prior_preparation_acids_2e_2p", 6, "literature_example",
    [
        ("acid_chloride", "reactant", None, "acid chloride", [], None),
        ("ylide", "reactant", None, "ethyl 2-(triphenylphosphoranylidene)propionate", [], None),
        ("allenoate", "product", None, "2,3-allenoate intermediate", [], None),
        ("naoh", "reagent", "NaOH", "sodium hydroxide", [], "[Na+].[OH-]"),
        ("acids", "product", "2e-2p", "2,3-allenoic acids 2e-2p", [], None),
    ],
    [("operation", "ylide reaction followed by hydrolysis with 2 N NaOH"), ("reaction_temperature", None), ("reaction_time", None)],
    "The Starting Materials section attributes this preparation to known methods 18 and 7d,e; the unsupported normality unit is preserved verbatim rather than converted.",
)


# Page 6: fully reported anchoring experiment for resin 1a.
ev6 = evid(6)
add(rec(
    "page6_anchor_resin1a_typical", "reported_experiment", ev6,
    [
        part("merrifield", "reactant", None, "Merrifield resin", ev6, [fld("mass", qty(2.724, "g"), ev6), fld("amount", qty(6.80, "mmol"), ev6)]),
        part("iodobenzoic", "reactant", None, "2-iodobenzoic acid", ev6, [fld("mass", qty(2.534, "g"), ev6), fld("amount", qty(10.20, "mmol"), ev6)]),
        part("cs2co3", "reagent", None, "cesium carbonate", ev6, [fld("mass", qty(6.648, "g"), ev6), fld("amount", qty(20.40, "mmol"), ev6)]),
        part("ki", "reagent", None, "potassium iodide", ev6, [fld("mass", qty(0.560, "g"), ev6), fld("amount", qty(3.40, "mmol"), ev6)]),
        part("dmf", "solvent", "DMF", "N,N-dimethylformamide", ev6, [fld("volume", qty(80, "mL"), ev6)], "CN(C)C=O"),
        part("resin1a", "product", "1a", "loaded resin 1a", ev6),
    ],
    [{"step_id": "anchoring", "participant_ids": ["merrifield", "iodobenzoic", "cs2co3", "ki", "dmf", "resin1a"],
      "conditions": [
          fld("reaction_temperature", qty(80, "°C"), ev6),
          fld("reaction_time", qty(24, "h"), ev6),
          fld("workup", "cool to room temperature; filter; wash with DMF, 1:1 DMF/H2O, H2O, DMF, and MeOH; dry under vacuum overnight", ev6),
      ]}],
    [fld("product_mass", qty(4.095, "g"), ev6, ["resin1a"])],
    ["The product is reported with maximum loading 1.636 mequiv/g; this unsupported compound unit is preserved in notes instead of forced into a structured quantity."],
    COMMON_UNRESOLVED + ["The reported loading unit mequiv/g is not supported by the quantity schema and remains unstructured."],
))


# Enrich Table 1 entry 10 with the detailed Conditions A/cutting procedure on page 6.
by_id = {r["source_reaction_id"]: r for r in records}
t1e10 = by_id["table1_entry10"]
for e in ev6:
    if e not in t1e10["evidence_ids"]:
        t1e10["evidence_ids"].append(e)
detail_amounts = {
    "resin": [("mass", qty(92, "mg")), ("amount", qty(0.15, "mmol"))],
    "acid": [("mass", qty(84, "mg")), ("amount", qty(0.60, "mmol"))],
    "base": [("volume", qty(0.21, "mL")), ("amount", qty(1.20, "mmol"))],
    "pd": [("mass", qty(26, "mg")), ("amount", qty(22.5, "umol"))],
    "solvent": [("volume", qty(4, "mL"))],
}
for p in t1e10["participants"]:
    for name, value in detail_amounts.get(p["entity_id"], []):
        p["amounts"].append(fld(name, value, ev6))
t1e10["outcomes"].append(fld("intermediate_mass", qty(92, "mg"), ev6, ["intermediate"]))
t1e10["outcomes"].append(fld("product_mass", qty(34, "mg"), ev6, ["product"]))
t1e10["steps"][1]["conditions"].append(fld("operation", "swell resin in CH2Cl2 for 30 min at room temperature; add 0.50 M AlCl3 in MeNO2 at 0 °C; stir 30 min; filter and perform acidic extraction workup", ev6))
t1e10["notes"].append(fact("Page 6 gives the typical Conditions A experiment for 1a + 2d and the subsequent cleavage to 4ad.", ev6))


# Enrich Table 1 entry 1 with the explicit product name/characterization paragraph on page 6.
t1e1 = by_id["table1_entry01"]
for e in ev6:
    if e not in t1e1["evidence_ids"]:
        t1e1["evidence_ids"].append(e)
t1e1["notes"].append(fact("Page 6 explicitly names and characterizes product 4aa by 1H NMR, EI-MS, FT-IR, and HRMS.", ev6))


# Enrich Table 2 entry 8 with the detailed, page-6-starting Conditions B procedure.
t2e8 = by_id["table2_entry08"]
for e in ev6:
    if e not in t2e8["evidence_ids"]:
        t2e8["evidence_ids"].append(e)
detail_b = {
    "resin": [("mass", qty(122, "mg")), ("amount", qty(0.20, "mmol"))],
    "acid": [("mass", qty(162, "mg")), ("amount", qty(0.80, "mmol"))],
    "base": [("volume", qty(0.28, "mL")), ("amount", qty(1.60, "mmol"))],
    "pd": [("mass", qty(36, "mg")), ("amount", qty(30, "umol"))],
    "solvent": [("volume", qty(4, "mL"))],
}
for p in t2e8["participants"]:
    for name, value in detail_b.get(p["entity_id"], []):
        p["amounts"].append(fld(name, value, ev6))
t2e8["notes"].append(fact("The detailed Conditions B paragraph begins on page 6 and continues beyond the inspected page range; only page-6 facts are added here.", ev6))
t2e8["review"]["unresolved"].append("The detailed Conditions B workup and cleavage continue on page 7, which was not visually covered in this session.")


# Coverage ledger. Every region cites its own page-image evidence.
def ids(prefixes):
    result = []
    for r in records:
        if any(r["source_reaction_id"].startswith(p) for p in prefixes):
            result.append(r["record_id"])
    return result


page_records = {
    1: ids(["eq1_"]),
    2: ids(["scheme1_", "scheme2_", "table1_"]),
    3: ids(["scheme3_", "table2_", "page3_", "scheme4_"]),
    4: ids(["scheme5_", "table3_", "scheme6_"]),
    5: ids(["scheme7_", "table4_", "page5_", "scheme8_"]),
    6: ids(["table5_", "page6_"]) + [t1e1["record_id"], t1e10["record_id"], t2e8["record_id"]],
}


coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1,
            "state": "attempted",
            "regions": [
                {"region": "title, abstract, and introduction", "finding": "Article-level scope and claimed 77-member library; no row-level experimental quantities in this region.", "evidence_ids": [f"{DOC}:page1:image", f"{DOC}:page1:text"]},
                {"region": "equation (1), lower-right column", "finding": "Cited 1998 solution-phase Pd(0)/Ag+ coupling-cyclization precedent; classified as literature_example, not a new experiment.", "evidence_ids": [f"{DOC}:page1:image", f"{DOC}:page1:text"]},
            ],
            "record_ids": page_records[1],
            "unresolved": ["Equation (1) does not report temperature, time, yield, or a specified base in this page region."],
        },
        {
            "page": 2,
            "state": "attempted",
            "regions": [
                {"region": "Table 1, entries 1-20 and footnotes", "finding": "Twenty independent substrate-scope rows; prior-results footnote f and isolated-yield footnote e retained.", "evidence_ids": [f"{DOC}:page2:image", f"{DOC}:page2:text"]},
                {"region": "Scheme 1, two arrows", "finding": "Previously reported solid-phase coupling and Lewis-acid cleavage model; classified as cited literature examples.", "evidence_ids": [f"{DOC}:page2:image", f"{DOC}:page2:text"]},
                {"region": "Scheme 2, anchoring/coupling/cleavage arrows", "finding": "Three general-scheme stage records; Table 1 rows remain the quantified experiments.", "evidence_ids": [f"{DOC}:page2:image", f"{DOC}:page2:text"]},
            ],
            "record_ids": page_records[2],
            "unresolved": ["Most structures are generic R-group drawings; source labels are retained and SMILES are not asserted."],
        },
        {
            "page": 3,
            "state": "attempted",
            "regions": [
                {"region": "Table 2, entries 1-8 and footnotes", "finding": "Eight independent aryl-allenoic-acid scope rows; entries 5-6 use Conditions C per footnote f.", "evidence_ids": [f"{DOC}:page3:image", f"{DOC}:page3:text"]},
                {"region": "Scheme 3 condition matrix", "finding": "Four independent solution-phase optimization rows with product-specific I/II yields, including not-detected and trace results.", "evidence_ids": [f"{DOC}:page3:image", f"{DOC}:page3:text"]},
                {"region": "prose SPOS base comparison", "finding": "Distinct inorganic-base SPOS trial (50% yield, 28% purity); organic-base result merged with Table 2 entry 1 and source purity discrepancy retained.", "evidence_ids": [f"{DOC}:page3:image", f"{DOC}:page3:text"]},
                {"region": "Scheme 4 coupling and cleavage arrows", "finding": "Two general-scheme stage records for Conditions B and AlCl3 cleavage.", "evidence_ids": [f"{DOC}:page3:image", f"{DOC}:page3:text"]},
            ],
            "record_ids": page_records[3],
            "unresolved": ["Scheme 3 omits temperature, time, reagent amounts, and yield basis.", "Table 2 entry 1 purity conflicts: table 93%, adjacent prose 91%."],
        },
        {
            "page": 4,
            "state": "attempted",
            "regions": [
                {"region": "Scheme 5 anchoring/coupling/cleavage arrows", "finding": "Three general-scheme stage records with Conditions A/C and 0.5 equiv ZnBr2 plus 2 equiv acetyl bromide cleavage.", "evidence_ids": [f"{DOC}:page4:image", f"{DOC}:page4:text"]},
                {"region": "Table 3, entries 1-23 and footnotes", "finding": "Twenty-three independent scope rows; footnote-f prior results classified as literature examples.", "evidence_ids": [f"{DOC}:page4:image", f"{DOC}:page4:text"]},
                {"region": "Scheme 6 coupling arrow and cleavage entries a-c", "finding": "One general coupling arrow plus three separate acetyl-bromide-loading experiments; entry a is cited prior work, b is a mixture, c favors benzyl bromide 12ca.", "evidence_ids": [f"{DOC}:page4:image", f"{DOC}:page4:text"]},
            ],
            "record_ids": page_records[4],
            "unresolved": ["Table 3 entry 17 prints 8cc/9cc for acid 2m, conflicting with the stated labeling convention; labels are preserved verbatim."],
        },
        {
            "page": 5,
            "state": "attempted",
            "regions": [
                {"region": "Scheme 7 anchoring/coupling/cleavage arrows", "finding": "Three general-scheme stage records for benzyl-ether support and 6 equiv acetyl bromide cleavage.", "evidence_ids": [f"{DOC}:page5:image", f"{DOC}:page5:text"]},
                {"region": "Table 4, entries 1-10 and footnotes", "finding": "Ten independent scope rows; Conditions A/C assignment retained with an explicit ambiguity for entries 9-10.", "evidence_ids": [f"{DOC}:page5:image", f"{DOC}:page5:text"]},
                {"region": "THP-linker prose before Scheme 8", "finding": "Initial acid-before-base addition order explicitly failed by cleaving the linker; recorded as a failed optimization experiment.", "evidence_ids": [f"{DOC}:page5:image", f"{DOC}:page5:text"]},
                {"region": "Scheme 8, four arrows", "finding": "Four general-scheme stages: DHP-resin preparation, aryl-iodide anchoring, Conditions D coupling, and TFA cleavage.", "evidence_ids": [f"{DOC}:page5:image", f"{DOC}:page5:text"]},
            ],
            "record_ids": page_records[5],
            "unresolved": ["Table 4 footnote enumerates Conditions C only for entries 7-8 although entries 9-10 are aryl-acid rows shown under the Conditions C scheme."],
        },
        {
            "page": 6,
            "state": "attempted",
            "regions": [
                {"region": "Table 5, entries 1-15 and footnotes", "finding": "Fifteen independent THP-linker scope rows with overall yield and HPLC purity.", "evidence_ids": [f"{DOC}:page6:image", f"{DOC}:page6:text"]},
                {"region": "Starting Materials", "finding": "Two cited preparation routes for acids 2a-2d and 2e-2p; classified as literature examples.", "evidence_ids": [f"{DOC}:page6:image", f"{DOC}:page6:text"]},
                {"region": "Typical anchoring of 2-iodobenzoic acid", "finding": "One detailed reported experiment producing loaded resin 1a; all explicit masses, amounts, volume, time, and temperature structured.", "evidence_ids": [f"{DOC}:page6:image", f"{DOC}:page6:text"]},
                {"region": "Typical Conditions A and AlCl3 cleavage", "finding": "Detailed stages merged into Table 1 entry 10; 4aa characterization merged into Table 1 entry 1.", "evidence_ids": [f"{DOC}:page6:image", f"{DOC}:page6:text"]},
                {"region": "Typical Conditions B paragraph at page bottom", "finding": "Page-6 starting quantities merged into Table 2 entry 8; continuation beyond page 6 not claimed as visually covered.", "evidence_ids": [f"{DOC}:page6:image", f"{DOC}:page6:text"]},
            ],
            "record_ids": list(dict.fromkeys(page_records[6])),
            "unresolved": ["The Conditions B procedure continues on page 7 outside this session's visual page scope.", "Reported resin loading uses unsupported unit mequiv/g and is preserved in notes rather than forced into a quantity object."],
        },
    ],
}


assert len(records) == 107, len(records)
assert [p["page"] for p in coverage["pages"]] == [1, 2, 3, 4, 5, 6]
assert all(p["regions"] for p in coverage["pages"])
OUT.parent.mkdir(parents=True, exist_ok=True)
COVERAGE.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
COVERAGE.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")


# Mark only the six visually inspected page tasks attempted.
tasks_path = RUN / "tasks.json"
tasks = json.loads(tasks_path.read_text())
for task in tasks:
    if task.get("document_id") == DOC and task.get("task_id", "").startswith(f"{DOC}:page"):
        page = int(task["task_id"].split(":page", 1)[1].split(":", 1)[0])
        if 1 <= page <= 6:
            task["state"] = "attempted"
            task["visual_evidence_id"] = f"{DOC}:page{page}:image"
            task["reason"] = "Page image and text were inspected; findings and unresolved issues are recorded in coverage/pages_0001_0006.json."
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")


print(json.dumps({"records": len(records), "raw": str(OUT.relative_to(ROOT)), "coverage": str(COVERAGE.relative_to(ROOT))}, ensure_ascii=False))
