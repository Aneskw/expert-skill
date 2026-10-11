#!/usr/bin/env python3
"""Build evidence-linked records for doc_9331c99d2a46165f, PDF pages 1-4."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / "runs/current"
DOC = "doc_9331c99d2a46165f"
OUT = RUN / "raw_model/records_pages_0001_0004.json"
COVERAGE = RUN / "coverage/pages_0001_0004.json"


def ev(page, kind="image"):
    return f"{DOC}:page{page}:{kind}"


def fact(value, evidence=()):
    return {
        "value": value,
        "evidence_ids": list(dict.fromkeys(evidence)) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def field(name, value, evidence=()):
    return {"name": name, "fact": fact(value, evidence)}


def participant(entity_id, role, evidence, label=None, name=None, amounts=()):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence) if label is not None else fact(None),
        "name": fact(name, evidence) if name is not None else fact(None),
        "smiles": fact(None),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": list(amounts),
    }


def record(suffix, kind, evidence, participants, steps, outcomes=(), notes=(), unresolved=()):
    return {
        "record_id": f"{DOC}:{suffix}",
        "document_id": DOC,
        "source_reaction_id": suffix,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": list(dict.fromkeys(evidence)),
        "participants": participants,
        "steps": steps,
        "outcomes": list(outcomes),
        "notes": [fact(v, e) for v, e in notes],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": list(unresolved),
        },
    }


records = []
P1 = [ev(1, "image"), ev(1, "text")]
P2 = [ev(2, "image"), ev(2, "text")]
P3 = [ev(3, "image"), ev(3, "text")]
P4 = [ev(4, "image"), ev(4, "text")]


# Scheme 1 precursor-resin preparation arrows.
records.append(record(
    "scheme1_resin1_preparation", "reported_experiment", P2,
    [
        participant("merrifield_resin", "reactant", P2, name="Merrifield resin"),
        participant("iodobenzoic_acid", "reactant", P2, label="p- or o-iodobenzoic acid"),
        participant("cs2co3", "reagent", P2, name="CsCO3"),
        participant("ki", "reagent", P2, name="KI"),
        participant("dmf", "solvent", P2, name="DMF"),
        participant("resin1", "product", P2, label="resin 1 (1a para-substituted; 1b ortho-substituted)"),
    ],
    [{"step_id": "anchoring", "participant_ids": ["merrifield_resin", "iodobenzoic_acid", "cs2co3", "ki", "dmf", "resin1"], "conditions": []}],
    notes=[("The paper says p- and o-iodobenzoic acids were anchored to Merrifield resin to provide 1a and 1b, respectively, and cites reference 7.", P2)],
    unresolved=["Separate amounts, temperature, time, atmosphere, workup, yield, and loading result are not reported locally.", "The cited external preparation was not imported."]
))
records.append(record(
    "scheme1_resin2_preparation", "reported_experiment", P2,
    [
        participant("merrifield_resin", "reactant", P2, name="Merrifield resin"),
        participant("p_iodophenol", "reactant", P2, name="p-iodophenol"),
        participant("naome", "reagent", P2, name="NaOMe"),
        participant("dmf", "solvent", P2, name="DMF"),
        participant("resin2", "product", P2, label="resin 2 (phenolic ether linkage)"),
    ],
    [{"step_id": "anchoring", "participant_ids": ["merrifield_resin", "p_iodophenol", "naome", "dmf", "resin2"], "conditions": []}],
    notes=[("The preparation is depicted and the prose cites reference 8.", P2)],
    unresolved=["Amounts, temperature, time, atmosphere, workup, yield, and loading result are not reported locally.", "The cited external preparation was not imported."]
))
records.append(record(
    "scheme1_resin3_preparation", "reported_experiment", P2,
    [
        participant("merrifield_resin", "reactant", P2, name="Merrifield resin"),
        participant("p_iodobenzyl_alcohol", "reactant", P2, name="p-iodobenzyl alcohol"),
        participant("nah", "reagent", P2, name="NaH"),
        participant("thf", "solvent", P2, name="THF"),
        participant("resin3", "product", P2, label="resin 3 (benzylic ether linkage)"),
    ],
    [{"step_id": "anchoring", "participant_ids": ["merrifield_resin", "p_iodobenzyl_alcohol", "nah", "thf", "resin3"], "conditions": []}],
    notes=[("The preparation is depicted and the prose cites reference 9.", P2)],
    unresolved=["Amounts, temperature, time, atmosphere, workup, yield, and loading result are not reported locally.", "The cited external preparation was not imported."]
))


# The graphical abstract and lower part of Scheme 1 are the same generic two-stage sequence.
records.append(record(
    "general_solid_phase_cyclization", "general_scheme", P1 + P2,
    [
        participant("polymer_aryl_iodide", "reactant", P1 + P2, label="polymer-supported aryl iodide 1, 2, or 3"),
        participant("allenoic_acid4", "reactant", P1 + P2, label="1,2-allenic carboxylic acid 4 (R1/R2 variable)"),
        participant("pd0", "catalyst", P1 + P2, name="Pd(0)"),
        participant("mecn", "solvent", P1, name="CH3CN"),
        participant("resin5", "product", P1 + P2, label="polymer-supported butenolide 5"),
    ],
    [{"step_id": "generic_cyclization", "participant_ids": ["polymer_aryl_iodide", "allenoic_acid4", "pd0", "mecn", "resin5"], "conditions": []}],
    notes=[("The graphical abstract specifies Pd(0)/CH3CN; Scheme 1 leaves the remaining condition as a question mark. This is a generic transformation, not an individual run.", P1 + P2)],
    unresolved=["Generic R groups and polymer attachment prevent a single complete structure assignment.", "Catalyst identity, base, temperature, time, and quantities are not defined by the generic arrow."]
))
records.append(record(
    "general_resin_cleavage", "general_scheme", P1 + P2,
    [
        participant("resin5", "reactant", P1 + P2, label="polymer-supported butenolide 5"),
        participant("lewis_acid_additive", "reagent", P1, label="Lewis acid additive"),
        participant("butenolide6", "product", P1 + P2, label="butenolide 6"),
    ],
    [{"step_id": "generic_cleavage", "participant_ids": ["resin5", "lewis_acid_additive", "butenolide6"], "conditions": []}],
    notes=[("The graphical abstract presents a generic Lewis-acid-assisted cleavage; Scheme 1 shows the cleavage arrow as initially unresolved. Specific Methods A and B are represented by the matching experiment records.", P1 + P2)],
    unresolved=["The generic arrow does not specify one reagent set, scale, time, temperature, or yield."]
))


# Method A cleavage screens described in prose on page 2.
method_a_screens = [
    ("net3_meoh_dmf_no_cleavage", "NEt3", ["MeOH", "DMF"], "no cleavage took place"),
    ("tfa_ch2cl2_no_cleavage", "50% TFA", ["CH2Cl2"], "no cleavage took place"),
    ("lioh_unidentified_acyclic", "LiOH", [], "unidentified acyclic products"),
    ("k2co3_unidentified_acyclic", "K2CO3", [], "unidentified acyclic products"),
    ("naome_unidentified", "NaOMe", [], "unidentified products"),
]
for suffix, reagent, solvents, result in method_a_screens:
    parts = [
        participant("resin5aa", "reactant", P2, label="resin 5aa"),
        participant("cleavage_reagent", "reagent", P2, name=reagent),
    ]
    ids = ["resin5aa", "cleavage_reagent"]
    for i, solvent in enumerate(solvents, 1):
        eid = f"solvent{i}"
        parts.append(participant(eid, "solvent", P2, name=solvent))
        ids.append(eid)
    records.append(record(
        f"cleavage_screen_{suffix}", "optimization_entry", P2, parts,
        [{"step_id": "cleavage_screen", "participant_ids": ids, "conditions": []}],
        [field("result", result, P2)],
        unresolved=["Reagent amount, temperature, time, scale, atmosphere, and analytical basis are not reported in the article."]
    ))


table1 = [
    (1, "K2CO3", 3, 10, 2, 33, 52),
    (2, "i-Pr2NEt", 3, 10, 2, 55, 51),
    (3, "K2CO3", 4, 15, 3, 50, 26),
    (4, "i-Pr2NEt", 2, 15, 3, 49, 82),
    (5, "i-Pr2NEt", 3, 15, 3, 66, 88),
    (6, "i-Pr2NEt", 4, 10, 3, 81, 94),
    (7, "i-Pr2NEt", 4, 10, 2, 77, 97),
    (8, "i-Pr2NEt", 4, 15, 1, 33, 95),
    (9, "i-Pr2NEt", 4, 15, 2, 90, 96),
    (10, "i-Pr2NEt", 6, 20, 4, 85, 65),
    (11, "i-Pr2NEt", 6, 20, 3, 94, 89),
    (12, "i-Pr2NEt", 4, 15, 3, 99, 93),
]


def table1_record(row):
    entry, base, acid_eq, pd_mol, days, yld, purity = row
    evidence = P2 if entry != 12 else P2 + P3
    resin_amounts = []
    acid_amounts = [field("equivalents", {"number": acid_eq, "unit": "equiv"}, P2)]
    base_amounts = []
    pd_amounts = [field("catalyst_loading", {"number": pd_mol, "unit": "mol%"}, P2)]
    solvent_amounts = []
    parts = [
        participant("resin1a", "reactant", P2, label="polymer-supported p-iodobenzoic acid 1a", amounts=resin_amounts),
        participant("acid4a", "reactant", P2, label="2,3-undecadienoic acid 4a", amounts=acid_amounts),
        participant("base", "reagent", P2, name=base, amounts=base_amounts),
        participant("pdpph3_4", "catalyst", P2, name="Pd(PPh3)4", amounts=pd_amounts),
        participant("mecn", "solvent", P2, name="MeCN", amounts=solvent_amounts),
        participant("alcl3", "reagent", P2, name="AlCl3"),
        participant("men02", "solvent", P2, name="MeNO2"),
        participant("ch2cl2", "solvent", P2, name="CH2Cl2"),
        participant("product6aa", "product", P2, label="butenolide 6aa"),
    ]
    cyclization_ids = ["resin1a", "acid4a", "base", "pdpph3_4", "mecn"]
    notes = []
    unresolved = ["Row-specific reaction scale, base amount, atmosphere, workup, and isolated mass are not given in Table 1.", "Method A is named by the table, but row-specific cleavage charges are not reported."]
    if base == "K2CO3":
        parts.append(participant("ag2co3", "catalyst", P2, name="Ag2CO3", amounts=[field("loading_based_on_acid4a", {"number": 5, "unit": "mol%"}, P2)]))
        cyclization_ids.append("ag2co3")
    if entry == 12:
        # Exact printed procedure values are preserved, including the equiv/basis issue.
        parts = [
            participant("resin1a", "reactant", P2 + P3, label="polymer-supported p-iodobenzoic acid 1a", amounts=[
                field("mass", {"number": 92, "unit": "mg"}, P3),
                field("maximum_loading", {"number": 1.636, "unit": "mequiv/g"}, P3),
            ]),
            participant("acid4a", "reactant", P2 + P3, label="2,3-undecadienoic acid 4a", amounts=[
                field("mass", {"number": 110, "unit": "mg"}, P3),
                field("equivalents", {"number": 4.0, "unit": "equiv"}, P2 + P3),
            ]),
            participant("base", "reagent", P2 + P3, name="i-Pr2NEt", amounts=[
                field("volume", {"number": 0.21, "unit": "mL"}, P3),
                field("typical_procedure_reported_equivalents", {"number": 8.0, "unit": "equiv"}, P3),
                field("adjacent_prose_reported_equivalents", {"number": 2.0, "unit": "equiv"}, P3),
            ]),
            participant("pdpph3_4", "catalyst", P2 + P3, name="Pd(PPh3)4", amounts=[
                field("mass", {"number": 26, "unit": "mg"}, P3),
                field("catalyst_loading", {"number": 15, "unit": "mol%"}, P2 + P3),
            ]),
            participant("mecn", "solvent", P2 + P3, name="dry CH3CN", amounts=[field("volume", {"number": 4, "unit": "mL"}, P3)]),
            participant("resin5aa", "reactant", P2 + P3, label="resin 5aa", amounts=[
                field("cyclization_product_mass", {"number": 101, "unit": "mg"}, P3),
                field("cleavage_charge_mass", {"number": 67, "unit": "mg"}, P3),
                field("maximum_loading", {"number": 1.503, "unit": "mequiv/g"}, P3),
            ]),
            participant("alcl3", "reagent", P2 + P3, name="AlCl3", amounts=[
                field("printed_equivalents", {"number": 0.6, "unit": "equiv"}, P3),
                field("amount", {"number": 0.6, "unit": "mmol"}, P3),
            ]),
            participant("meno2", "solvent", P2 + P3, name="MeNO2", amounts=[
                field("volume", {"number": 2, "unit": "mL"}, P3),
                field("alcl3_concentration", {"number": 0.3, "unit": "M"}, P3),
            ]),
            participant("ch2cl2", "solvent", P2 + P3, name="CH2Cl2", amounts=[field("volume", {"number": 2, "unit": "mL"}, P3)]),
            participant("product6aa", "product", P2 + P3, label="butenolide 6aa", amounts=[field("isolated_mass", {"number": 30, "unit": "mg"}, P3)]),
        ]
        cyclization_ids = ["resin1a", "acid4a", "base", "pdpph3_4", "mecn", "resin5aa"]
        notes.extend([
            ("Table 1 entry 12, Table 2 entry 1, Scheme 2, and the two typical procedures describe the same optimized 1a/4a to 6aa sequence and are merged here.", P2 + P3),
            ("The cyclization resin was washed successively with DMF, DMF/H2O (1:1), H2O, DMF, THF, and MeOH, then dried under high vacuum overnight.", P3),
            ("Method A workup: filter and wash resin with EtOAc; wash filtrate twice with 0.5 N HCl; extract aqueous layer with EtOAc; dry combined extracts and evaporate.", P3),
            ("The prose states that four to six equivalents of AlCl3 at 0.3-0.5 M gave the best results.", P2),
        ])
        unresolved = [
            "The method-A procedure prints AlCl3 as 0.6 equiv but also 0.6 mmol for about 0.10 mmol maximum resin loading, which is internally inconsistent and may represent 6 equiv; the printed values are preserved.",
            "The source reports i-Pr2NEt as 2 equiv in the adjacent prose and 8.0 equiv in the typical procedure without explicitly naming the reference basis for either value; both are retained without assigning a basis.",
            "The approximately 100% resin-5aa yield is reported on a maximum-loading basis and is not treated as a chemically verified mass balance.",
            "Product structure is not machine-certified and SI analytical data are unavailable.",
        ]
    steps = [
        {"step_id": "pd_cyclization", "participant_ids": cyclization_ids, "conditions": [
            field("temperature", {"number": 70, "unit": "°C"}, P2 if entry != 12 else P2 + P3),
            field("time", {"number": days, "unit": "d"}, P2 if entry != 12 else P2 + P3),
            field("atmosphere", "argon", P3) if entry == 12 else field("atmosphere", None),
            field("degassed_suspension", True, P3) if entry == 12 else field("degassed_suspension", None),
        ]},
        {"step_id": "method_A_cleavage", "participant_ids": (["resin5aa"] if entry == 12 else []) + ["alcl3", "men02" if entry != 12 else "meno2", "ch2cl2", "product6aa"], "conditions": (
            [field("resin_preswell_time", {"number": 30, "unit": "min"}, P3), field("resin_preswell_temperature", "room temperature", P3), field("cleavage_temperature", {"number": 0, "unit": "°C"}, P3), field("cleavage_time", {"number": 30, "unit": "min"}, P3)] if entry == 12 else []
        )},
    ]
    outcomes = [
        field("overall_yield_from_1a_to_6aa", {"number": yld, "unit": "%"}, P2 if entry != 12 else P2 + P3),
        field("yield_basis", "maximum loading of aryl iodide on resin", P2 if entry != 12 else P2 + P3),
        field("purity", {"number": purity, "unit": "%"}, P2 if entry != 12 else P2 + P3),
        field("purity_method", "HPLC", P2 if entry != 12 else P2 + P3),
    ]
    if entry == 12:
        outcomes.append(field("resin5aa_overall_yield_from_Merrifield_resin", "~100%", P3))
    return record(f"table1_entry_{entry:02d}", "optimization_entry", evidence, parts, steps, outcomes, notes, unresolved)


records.extend(table1_record(row) for row in table1)


# Ether-linkage cleavage screening before Method B.
for reagent in ["SnCl4", "AlCl3", "ZnCl2", "ZnBr2", "FeCl3"]:
    safe = reagent.lower().replace("cl", "cl").replace("br", "br")
    records.append(record(
        f"ether_cleavage_screen_{safe}", "optimization_entry", P3,
        [
            participant("resin5ca", "reactant", P3, label="Merrifield-resin-bound ether 5ca"),
            participant("lewis_acid", "reagent", P3, name=reagent),
        ],
        [{"step_id": "ether_cleavage_screen", "participant_ids": ["resin5ca", "lewis_acid"], "conditions": []}],
        [field("result", "trace of unidentified products", P3)],
        unresolved=["Reagent amount, solvent, temperature, time, scale, and analytical basis are not stated for this individual screen."]
    ))

records.append(record(
    "ether_cleavage_alcl3_acbr", "optimization_entry", P3,
    [
        participant("resin5ca", "reactant", P3, label="Merrifield-resin-bound ether 5ca"),
        participant("alcl3", "reagent", P3, name="AlCl3", amounts=[field("equivalents", {"number": 0.5, "unit": "equiv"}, P3)]),
        participant("acbr", "reagent", P3, name="acetyl bromide", amounts=[field("equivalents", {"number": 2.0, "unit": "equiv"}, P3)]),
        participant("product6ca", "product", P3, label="6ca"),
    ],
    [{"step_id": "ether_cleavage", "participant_ids": ["resin5ca", "alcl3", "acbr", "product6ca"], "conditions": []}],
    [field("yield", {"number": 52, "unit": "%"}, P3), field("purity", {"number": 84, "unit": "%"}, P3)],
    unresolved=["Solvent, temperature, time, scale, workup, yield basis, and purity method are not specified in the comparison sentence."]
))


acid_names = {
    "4a": "2,3-undecadienoic acid 4a (R1=n-Hep, R2=H)",
    "4b": "allenoic acid 4b (R1=n-Bu, R2=H)",
    "4c": "allenoic acid 4c (R1=c-Hex, R2=H)",
    "4d": "2-methyl-2,3-decadienoic acid 4d (R1=n-Hex, R2=Me)",
}
table2 = [
    (1, "1a", "4a", "5aa", "A", "6aa", 99, 93),
    (2, "1a", "4b", "5ab", "A", "6ab", 93, 95),
    (3, "1a", "4c", "5ac", "A", "6ac", "~100", 94),
    (4, "1a", "4d", "5ad", "A", "6ad", 84, 85),
    (5, "1b", "4a", "5ba", "A", "6ba", "~100", 90),
    (6, "1b", "4c", "5bb", "A", "6bb", "~100", 96),
    (7, "2", "4a", "5ca", "B", "6ca", 89, 94),
    (8, "2", "4b", "5cb", "B", "6cb", 87, 83),
    (9, "2", "4c", "5cc", "B", "6cc", 84, 87),
    (10, "2", "4d", "5cd", "B", "6cd", 82, 76),
    (11, "3", "4a", "5da", "B", "6da", 75, 82),
]


def table2_record(row):
    entry, resin, acid, intermediate, method, product, yld, purity = row
    evidence = P3 + (P4 if entry == 7 else [])
    parts = [
        participant("resin", "reactant", P3, label=f"resin {resin}", amounts=[field("amount", "0.15-0.20 mmol", P3)]),
        participant("acid", "reactant", P3, label=acid_names[acid], amounts=[field("equivalents", {"number": 4, "unit": "equiv"}, P3)]),
        participant("pdpph3_4", "catalyst", P3, name="Pd(PPh3)4", amounts=[field("catalyst_loading", {"number": 15, "unit": "mol%"}, P3)]),
        participant("ipr2net", "reagent", P3, name="i-Pr2NEt"),
        participant("mecn", "solvent", P3, name="MeCN", amounts=[field("volume", {"number": 4, "unit": "mL"}, P3)]),
        participant("intermediate", "reactant", P3, label=f"resin {intermediate}"),
        participant("product", "product", P3, label=f"butenolide {product}"),
    ]
    cleavage_ids = ["intermediate", "product"]
    cleavage_conditions = []
    notes = [("All new products in Table 2 are reported as characterized by 1H NMR, MS(EI), and HRMS.", P3)]
    unresolved = ["The common Table 2 footnote does not state the i-Pr2NEt amount.", "Row-specific cyclization workup, intermediate mass, and product isolated mass are not reported.", "Product structure is not machine-certified and SI analytical data are unavailable."]
    if method == "A":
        parts += [
            participant("alcl3", "reagent", P2 + P3, name="AlCl3"),
            participant("meno2", "solvent", P2 + P3, name="MeNO2"),
            participant("ch2cl2", "solvent", P2 + P3, name="CH2Cl2"),
        ]
        cleavage_ids = ["intermediate", "alcl3", "meno2", "ch2cl2", "product"]
        notes.append(("The row uses Method A; the article defines it as AlCl3 in MeNO2/CH2Cl2, but the detailed charge is shown only for 5aa.", P2 + P3))
    else:
        parts += [
            participant("znbr2", "reagent", P3, name="ZnBr2", amounts=[field("equivalents", {"number": 0.5, "unit": "equiv"}, P3)]),
            participant("acbr", "reagent", P3, name="acetyl bromide", amounts=[field("equivalents", {"number": 2.0, "unit": "equiv"}, P3)]),
            participant("ch2cl2", "solvent", P3, name="CH2Cl2"),
        ]
        cleavage_ids = ["intermediate", "znbr2", "acbr", "ch2cl2", "product"]
        cleavage_conditions = [field("temperature", "room temperature", P3), field("time", {"number": 24, "unit": "h"}, P3)]
    if entry == 7:
        # Detailed Method B procedure is specific to resin 5ca / product 6ca.
        parts = [p for p in parts if p["entity_id"] not in {"intermediate", "znbr2", "acbr", "ch2cl2", "product"}] + [
            participant("intermediate", "reactant", P3 + P4, label="resin 5ca", amounts=[field("mass", {"number": 96, "unit": "mg"}, P4), field("maximum_loading", {"number": 1.56, "unit": "mequiv/g"}, P4)]),
            participant("znbr2", "reagent", P3 + P4, name="ZnBr2", amounts=[field("mass", {"number": 17, "unit": "mg"}, P4), field("equivalents", {"number": 0.5, "unit": "equiv"}, P3 + P4)]),
            participant("acbr", "reagent", P3 + P4, name="acetyl bromide", amounts=[field("volume", {"number": 22, "unit": "µL"}, P4), field("equivalents", {"number": 2.0, "unit": "equiv"}, P3 + P4)]),
            participant("ch2cl2", "solvent", P3 + P4, name="CH2Cl2", amounts=[field("volume", {"number": 4, "unit": "mL"}, P4)]),
            participant("product", "product", P3 + P4, label="butenolide 6ca", amounts=[field("isolated_mass", {"number": 42, "unit": "mg"}, P4)]),
        ]
        cleavage_conditions = [field("temperature", "room temperature", P3 + P4), field("time", {"number": 24, "unit": "h"}, P3 + P4), field("atmosphere", "argon", P4)]
        notes += [
            ("Scheme 3, Table 2 entry 7, and the Method B typical procedure describe the same 5ca-to-6ca cleavage and are merged here.", P3 + P4),
            ("Method B workup: collect resin by filtration; wash filtrate successively with 5% NaHCO3, 5% HCl, and saturated aqueous NaCl; dry, filter, and concentrate.", P4),
        ]
    steps = [
        {"step_id": "pd_cyclization", "participant_ids": ["resin", "acid", "pdpph3_4", "ipr2net", "mecn", "intermediate"], "conditions": [field("temperature", {"number": 70, "unit": "°C"}, P3), field("time", {"number": 3, "unit": "d"}, P3), field("atmosphere", "argon", P3)]},
        {"step_id": f"method_{method}_cleavage", "participant_ids": cleavage_ids, "conditions": cleavage_conditions},
    ]
    outcomes = [
        field("overall_yield_from_resin_to_product", ({"number": yld, "unit": "%"} if isinstance(yld, int) else yld), evidence),
        field("yield_basis", "maximum loading of aryl iodide on resin", P3),
        field("purity", {"number": purity, "unit": "%"}, evidence),
        field("purity_method", "HPLC", P3),
    ]
    ir_note = "two approximately equal carbonyl absorptions at 1717 and 1757 cm-1" if intermediate in {"5aa", "5ab", "5ac", "5ad", "5ba", "5bb"} else "a single strong carbonyl absorption at 1755 cm-1"
    notes.append((f"Formation of resin {intermediate} was monitored by FT-IR and associated with {ir_note}.", P3))
    return record(f"table2_entry_{entry:02d}", "substrate_scope_entry", evidence, parts, steps, outcomes, notes, unresolved)


# Table 2 entry 1 is already merged into Table 1 entry 12.
records.extend(table2_record(row) for row in table2 if row[0] != 1)


record_ids = [r["record_id"] for r in records]
assert len(records) == 38, len(records)
assert len(record_ids) == len(set(record_ids))

table1_ids = [f"{DOC}:table1_entry_{i:02d}" for i in range(1, 13)]
table2_ids = [f"{DOC}:table1_entry_12"] + [f"{DOC}:table2_entry_{i:02d}" for i in range(2, 12)]
method_a_ids = [f"{DOC}:cleavage_screen_{x[0]}" for x in method_a_screens]
method_b_screen_ids = [f"{DOC}:ether_cleavage_screen_{x.lower()}" for x in ["SnCl4", "AlCl3", "ZnCl2", "ZnBr2", "FeCl3"]]

coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1,
            "state": "attempted",
            "regions": [
                {"region": "abstract graphical reaction sequence", "finding": "Generic two-stage Pd(0)-catalyzed solid-phase cyclization followed by Lewis-acid-assisted cleavage; no individual scale, time, or yield is shown.", "evidence_ids": [ev(1, "image"), ev(1, "text")]},
                {"region": "title, abstract, and introductory prose", "finding": "Article-level scope and prior-work background; no additional row-level current experiment is reported here.", "evidence_ids": [ev(1, "image"), ev(1, "text")]},
            ],
            "record_ids": [f"{DOC}:general_solid_phase_cyclization", f"{DOC}:general_resin_cleavage"],
            "unresolved": ["Generic R groups and polymer-supported structures are not assigned verified SMILES."]
        },
        {
            "page": 2,
            "state": "attempted",
            "regions": [
                {"region": "Scheme 1", "finding": "Three distinct precursor-resin preparation arrows plus the generic cyclization/cleavage sequence.", "evidence_ids": [ev(2, "image"), ev(2, "text")]},
                {"region": "Scheme 2 and adjacent cleavage-screen prose", "finding": "Method A depiction plus five separate failed or unidentified-product cleavage conditions; Scheme 2 matches the optimized 6aa sequence.", "evidence_ids": [ev(2, "image"), ev(2, "text")]},
                {"region": "Table 1 including header and footnotes", "finding": "Twelve independent optimization rows for resin 1a plus acid 4a; entry 12 is the optimized run later repeated as Table 2 entry 1.", "evidence_ids": [ev(2, "image"), ev(2, "text")]},
            ],
            "record_ids": [f"{DOC}:scheme1_resin1_preparation", f"{DOC}:scheme1_resin2_preparation", f"{DOC}:scheme1_resin3_preparation", f"{DOC}:general_solid_phase_cyclization", f"{DOC}:general_resin_cleavage"] + method_a_ids + table1_ids,
            "unresolved": ["Precursor-resin preparation yields and operating details are not given locally.", "Several cleavage screens omit scale, amount, temperature, time, and analytical basis."]
        },
        {
            "page": 3,
            "state": "attempted",
            "regions": [
                {"region": "upper-left discussion and Scheme 3", "finding": "Table 1 optimization interpretation, ether-linkage cleavage screening, and a generic Method B cleavage diagram.", "evidence_ids": [ev(3, "image"), ev(3, "text")]},
                {"region": "Table 2 including header and footnotes", "finding": "Eleven substrate-scope rows; Table 2 entry 1 is merged with Table 1 entry 12, and entries 2-11 are separate records.", "evidence_ids": [ev(3, "image"), ev(3, "text")]},
                {"region": "footnotes 15-18", "finding": "Detailed Method A and optimized cyclization procedures, FT-IR observations, and source-local characterization statements.", "evidence_ids": [ev(3, "image"), ev(3, "text")]},
            ],
            "record_ids": [f"{DOC}:table1_entry_12"] + method_b_screen_ids + [f"{DOC}:ether_cleavage_alcl3_acbr"] + table2_ids,
            "unresolved": ["The Method A footnote prints an AlCl3 equivalents value inconsistent with its printed mmol and resin loading.", "Only the matching optimized examples receive detailed procedure quantities; unreported row-specific details remain missing."]
        },
        {
            "page": 4,
            "state": "attempted",
            "regions": [
                {"region": "Table 2 discussion continuation", "finding": "Qualitative comparison of resin/linker and allenoic-acid effects; no new independent reaction row.", "evidence_ids": [ev(4, "image"), ev(4, "text")]},
                {"region": "footnote 19 Method B typical procedure", "finding": "Detailed resin 5ca to product 6ca cleavage, matching Table 2 entry 7 and not duplicated.", "evidence_ids": [ev(4, "image"), ev(4, "text")]},
                {"region": "Supporting Information notice", "finding": "Analytical data are announced online, but no SI file is supplied or explicitly associated in this pilot.", "evidence_ids": [ev(4, "image"), ev(4, "text")]},
            ],
            "record_ids": [f"{DOC}:table2_entry_07", f"{DOC}:table2_entry_04", f"{DOC}:table2_entry_10"],
            "unresolved": ["SI-only analytical data are unavailable and no SI association is inferred.", "Product structures and purities remain machine records requiring review."]
        },
    ]
}

OUT.parent.mkdir(parents=True, exist_ok=True)
COVERAGE.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
COVERAGE.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

# Mark only this session's four page tasks attempted; task completion is not a claim of semantic correctness.
tasks_path = RUN / "tasks.json"
tasks = json.loads(tasks_path.read_text())
for task in tasks:
    if task.get("document_id") == DOC and task.get("evidence_id") in {ev(i, "text") for i in range(1, 5)}:
        task["state"] = "attempted"
        task["reason"] = "Original page image inspected; extraction attempted, with unresolved and missing facts preserved in the coverage ledger."
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"records": len(records), "coverage_pages": [p["page"] for p in coverage["pages"]]}, ensure_ascii=False))
