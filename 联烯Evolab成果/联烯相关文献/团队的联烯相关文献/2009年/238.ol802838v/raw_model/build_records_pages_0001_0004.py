#!/usr/bin/env python3
"""Build evidence-linked machine records for PDF pages 1--4 of ol802838v."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
DATASET = ROOT / "runs/current/dataset.json"
OUT = ROOT / "runs/current/raw_model/records_pages_0001_0004.json"
DOC = "doc_88eb0eb0ea1fc9d6"

SMILES_BY_TEXT = {
    "1a": "c1ccc2[nH]ccc2c1",
    "1e": "Cn1ccc2ccccc21",
    "2a": "OCCC=C=CCCCCCC",
    "3aa": "CCCCCCC1(c2c[nH]c3ccccc23)CCCCO1",
    "4aa": "CCCCCCC1C=CCCO1",
    "indole": "c1ccc2[nH]ccc2c1",
    "N-methylindole": "Cn1ccc2ccccc21",
    "3,4-undecadien-1-ol": "OCCC=C=CCCCCCC",
    "3-(2-hexyl-tetrahydro-2H-pyran-2-yl)-1H-indole": "CCCCCCC1(c2c[nH]c3ccccc23)CCCCO1",
    "2-hexyl-5,6-dihydro-2H-pyran": "CCCCCCC1C=CCCO1",
    "THF": "C1CCOC1",
    "DMSO": "CS(C)=O",
    "CH3CN": "CC#N",
    "ClCH2CH2Cl": "ClCCCl",
    "toluene": "Cc1ccccc1",
    "MeOH": "CO",
    "Et2O": "CCOCC",
    "dibromomethane": "BrCBr",
    "triethyl orthoacetate": "CCOC(C)(OCC)OCC",
    "propionic acid": "CCC(=O)O",
    "lithium aluminium hydride": "[Li+].[H][Al-]([H])([H])[H]",
    "lithium aluminium deuteride": "[Li+].[2H][Al-]([2H])([2H])[2H]",
}


def ev(page):
    return [f"{DOC}:page{page}:image", f"{DOC}:page{page}:text"]


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


def participant(entity_id, role, label, name, evidence, amounts=None, smiles=None):
    candidate_smiles = smiles or SMILES_BY_TEXT.get(name) or SMILES_BY_TEXT.get(label)
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence) if name else fact(None, []),
        "smiles": fact(candidate_smiles, evidence) if candidate_smiles else fact(None, []),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": amounts or [],
    }


def missing_participant(entity_id, role, label, name, evidence):
    return participant(entity_id, role, label, name, evidence)


def step(step_id, participant_ids, conditions):
    return {"step_id": step_id, "participant_ids": participant_ids, "conditions": conditions}


def record(suffix, kind, evidence, participants=None, steps=None, outcomes=None, notes=None,
           unresolved=None, source_id=None):
    return {
        "record_id": f"{DOC}:{suffix}",
        "document_id": DOC,
        "source_reaction_id": source_id or suffix,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": list(dict.fromkeys(evidence)),
        "participants": participants or [],
        "steps": steps or [],
        "outcomes": outcomes or [],
        "notes": notes or [],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved or [],
        },
    }


def q(number, unit, raw_text=None, qualifier=None):
    value = {"number": number, "unit": unit}
    if raw_text is not None:
        value["raw_text"] = raw_text
    if qualifier is not None:
        value["qualifier"] = qualifier
    return value


def catalyst(name, loading, evidence):
    return participant(
        "catalyst", "catalyst", name, name, evidence,
        [field("catalyst_loading", q(loading, "mol%"), evidence)],
    )


def solvent(name, evidence):
    return participant("solvent", "solvent", name, name, evidence)


def common_table1(entry, catalyst_name, catalyst_loading, solvent_name, allenol_equiv,
                  duration, evidence, outcomes, extra_participants=None, include_product=True):
    participants = [
        participant("indole_1a", "reactant", "1a", "indole", evidence),
        participant(
            "allenol_2a", "reactant", "2a", "3,4-undecadien-1-ol", evidence,
            [field("equivalents", q(allenol_equiv, "equiv"), evidence)],
        ),
        catalyst(catalyst_name, catalyst_loading, evidence),
        solvent(solvent_name, evidence),
    ]
    if include_product:
        participants.append(participant(
            "product_3aa", "product", "3aa",
            "3-(2-hexyl-tetrahydro-2H-pyran-2-yl)-1H-indole", evidence,
        ))
    participants.extend(extra_participants or [])
    return record(
        f"table1_entry{entry}", "optimization_entry", evidence,
        participants=participants,
        steps=[step("cyclization", [p["entity_id"] for p in participants if p["role"] != "product"], [
            field("solvent", solvent_name, evidence),
            field("temperature", "r.t.", evidence),
            field("time", q(duration, "h"), evidence),
        ])],
        outcomes=outcomes,
        notes=[fact(f"Table 1 entry {entry}.", evidence)],
        unresolved=[
            "No explicitly associated Supporting Information was provided; operational details, workup, and purification are unavailable.",
            "Participant and product structures remain machine interpretations and are not source-verified.",
        ],
    )


records = []

# Page 1, Scheme 1 is a conceptual branching scheme, not a reported experiment.
e1 = ev(1)
records.append(record(
    "scheme1_general_concept", "general_scheme", e1,
    participants=[
        participant("generic_allene", "reactant", "generic nucleophile-bearing allene", None, e1),
        participant("generic_rx", "reactant", "RX", "organic halide", e1),
        participant("generic_indole", "reactant", "indole", "indole", e1),
    ],
    notes=[
        fact("Scheme 1 contrasts the cited metal-mediated reaction with RX against a proposed indole branch marked with a question mark.", e1),
        fact("The scheme is conceptual/general and carries no reported yield or batch procedure.", e1),
    ],
    unresolved=["Generic R/Nu structures cannot be encoded as complete molecules."],
))

# Table 1: each optimization row is independent. Entry 3 is merged with duplicate Table 2 entry 1.
e12 = ev(1) + ev(2)
records.append(common_table1(
    1, "AuCl3", 5, "THF", 1.2, 4, e12,
    outcomes=[
        field("formation_of_3aa", "not formed", e12, ["product_3aa"]),
        field("isolated_yield_4aa", q(84, "%"), e12, ["product_4aa"]),
        field("yield_measurement_basis_4aa", "isolated yield", e12, ["product_4aa"]),
    ],
    extra_participants=[participant(
        "product_4aa", "product", "4aa", "2-hexyl-5,6-dihydro-2H-pyran", e12,
    )],
))
records.append(common_table1(
    2, "AuCl(PPh3)", 5, "THF", 1.2, 27, e12,
    outcomes=[
        field("recovered_indole_yield", q(89, "%"), e12, ["indole_1a"]),
        field("recovered_allenol_yield", q(92, "%"), e12, ["allenol_2a"]),
    ],
    include_product=False,
))

e23 = ev(2) + ev(3)
entry3 = common_table1(
    3, "PtCl4", 5, "THF", 1.2, 4, e23,
    outcomes=[
        field("NMR_yield_3aa", q(77, "%"), ev(2), ["product_3aa"]),
        field("yield_measurement_basis_NMR", "1H NMR using CH2Br2 as internal standard", ev(2), ["product_3aa"]),
        field("isolated_yield_3aa", q(74, "%"), ev(2) + ev(3), ["product_3aa"]),
        field("yield_measurement_basis_isolated", "isolated yield", ev(2) + ev(3), ["product_3aa"]),
    ],
    extra_participants=[participant("internal_standard", "reagent", "CH2Br2", "dibromomethane", ev(2))],
)
entry3["record_id"] = f"{DOC}:table1_entry3_table2_entry1"
entry3["source_reaction_id"] = "table1_entry3_table2_entry1"
entry3["notes"].append(fact("The same standard-condition batch is reported as Table 1 entry 3 and Table 2 entry 1; it is represented once.", e23))
records.append(entry3)

records.append(common_table1(
    4, "PtCl4", 5, "DMSO", 1.2, 19, ev(2),
    outcomes=[
        field("recovered_indole_yield", q(100, "%"), ev(2), ["indole_1a"]),
        field("recovered_allenol_yield", q(94, "%"), ev(2), ["allenol_2a"]),
    ], include_product=False,
))
for number, solvent_name, duration, reported_yield in [
    (5, "CH3CN", 3.5, 60),
    (6, "ClCH2CH2Cl", 4, 64),
    (7, "toluene", 7, 72),
]:
    evidence = ev(2)
    records.append(common_table1(
        number, "PtCl4", 5, solvent_name, 1.2, duration, evidence,
        outcomes=[
            field("NMR_yield_3aa", q(reported_yield, "%"), evidence, ["product_3aa"]),
            field("yield_measurement_basis", "1H NMR using CH2Br2 as internal standard", evidence, ["product_3aa"]),
        ],
        extra_participants=[participant("internal_standard", "reagent", "CH2Br2", "dibromomethane", evidence)],
    ))
records.append(common_table1(
    8, "PtCl4", 5, "MeOH", 1.2, 24, ev(2),
    outcomes=[
        field("recovered_indole_yield", q(80, "%"), ev(2), ["indole_1a"]),
        field("allenol_fate", "decomposed", ev(2), ["allenol_2a"]),
    ], include_product=False,
))
for number, loading, equiv, duration, reported_yield in [
    (9, 5, 1.0, 6, 60),
    (10, 3, 1.2, 22.5, 59),
]:
    evidence = ev(2)
    records.append(common_table1(
        number, "PtCl4", loading, "THF", equiv, duration, evidence,
        outcomes=[
            field("isolated_yield_3aa", q(reported_yield, "%"), evidence, ["product_3aa"]),
            field("yield_measurement_basis", "isolated yield", evidence, ["product_3aa"]),
        ],
    ))


indoles = {
    "1a": "indole (R1=H, R2=H, R3=H)",
    "1b": "5-hydroxyindole (R1=H, R2=H, R3=OH)",
    "1c": "5-benzyloxyindole (R1=H, R2=H, R3=OBn)",
    "1d": "5-chloro-2-methylindole (R1=H, R2=CH3, R3=Cl)",
    "1e": "N-methylindole (R1=CH3, R2=H, R3=H)",
    "1f": "N-n-butylindole (R1=n-C4H9, R2=H, R3=H)",
    "1g": "N-phenylindole (R1=Ph, R2=H, R3=H)",
    "1h": "N-tosylindole (R1=Ts, R2=H, R3=H)",
}
allenols = {
    "2a": "beta-allenol 2a (R4=n-C6H13, R5=H)",
    "2b": "beta-allenol 2b (R4=n-C5H11, R5=H)",
    "2c": "beta-allenol 2c (R4=CH3, R5=H)",
    "2d": "beta-allenol 2d (R4=Ph, R5=CH3)",
}
table2_rows = [
    (2, "1a", "2b", 10, 74, "3ab"),
    (3, "1a", "2c", 11, 74, "3ac"),
    (4, "1a", "2d", 21.3, 71, "3ad"),
    (5, "1b", "2a", 4.6, 67, "3ba"),
    (6, "1b", "2b", 1.8, 77, "3bb"),
    (7, "1c", "2a", 5, 72, "3ca"),
    (8, "1d", "2a", 19, 42, "3da"),
    (9, "1e", "2a", 14.2, 70, "3ea"),
    (10, "1e", "2b", 6, 50, "3eb"),
    (11, "1e", "2c", 12, 68, "3ec"),
    (12, "1e", "2d", 23, 47, "3ed"),
    (13, "1f", "2a", 19, 55, "3fa"),
    (14, "1g", "2a", 10, 50, "3ga"),
    (15, "1g", "2b", 12, 55, "3gb"),
]
for number, indole_label, allenol_label, duration, reported_yield, product_label in table2_rows:
    evidence = ev(2) + ev(3)
    loading = 10 if number == 8 else 5
    equivalents = 2 if number == 8 else 1.2
    participants = [
        participant("indole", "reactant", indole_label, indoles[indole_label], ev(3)),
        participant(
            "allenol", "reactant", allenol_label, allenols[allenol_label], ev(3),
            [field("equivalents", q(equivalents, "equiv"), ev(3))],
        ),
        catalyst("PtCl4", loading, ev(3)),
        solvent("THF", ev(3)),
        participant("product", "product", product_label, f"Table 2 product {product_label}", ev(3)),
    ]
    records.append(record(
        f"table2_entry{number}", "substrate_scope_entry", evidence,
        participants=participants,
        steps=[step("cyclization", ["indole", "allenol", "catalyst", "solvent"], [
            field("solvent", "THF", ev(3)),
            field("temperature", "r.t.", ev(3)),
            field("time", q(duration, "h"), ev(3)),
        ])],
        outcomes=[
            field(f"isolated_yield_{product_label}", q(reported_yield, "%"), ev(3), ["product"]),
            field("yield_measurement_basis", "isolated yield", ev(3), ["product"]),
        ],
        notes=[fact(f"Table 2 entry {number}; entry-specific footnote overrides are structured where applicable.", ev(3))],
        unresolved=[
            "No explicitly associated Supporting Information was provided; operational details, workup, and purification are unavailable.",
            "The table uses generic R-group drawings; full structures and stereochemical assignments remain unverified.",
        ],
    ))

# Table 2 entry 16 is a failed scope reaction with recovery/decomposition rather than a product yield.
e3 = ev(3)
records.append(record(
    "table2_entry16", "substrate_scope_entry", ev(2) + e3,
    participants=[
        participant("indole_1h", "reactant", "1h", indoles["1h"], e3),
        participant(
            "allenol_2a", "reactant", "2a", allenols["2a"], e3,
            [field("equivalents", q(1.2, "equiv"), e3)],
        ),
        catalyst("PtCl4", 5, e3),
        solvent("THF", e3),
    ],
    steps=[step("attempted_cyclization", ["indole_1h", "allenol_2a", "catalyst", "solvent"], [
        field("solvent", "THF", e3),
        field("temperature", "r.t.", e3),
        field("time", q(18.6, "h"), e3),
    ])],
    outcomes=[
        field("recovered_indole_yield", q(100, "%"), e3, ["indole_1h"]),
        field("allenol_fate", "decomposed", e3, ["allenol_2a"]),
    ],
    notes=[fact("Table 2 entry 16 reports inhibition of cyclization by the tosyl-substituted indole.", e3)],
    unresolved=[
        "No product yield is reported because the indole was recovered and the allenol decomposed.",
        "No explicitly associated Supporting Information was provided; operational details are unavailable.",
    ],
))

# Scheme 2: separate control/no-reaction experiment.
records.append(record(
    "scheme2_no_reaction_control", "reported_experiment", e3,
    participants=[
        participant("indole_1a", "reactant", "1a", "indole", e3),
        participant("dihydropyran_4aa", "reactant", "4aa", "2-hexyl-5,6-dihydro-2H-pyran", e3),
        catalyst("PtCl4", 5, e3),
        solvent("THF", e3),
    ],
    steps=[step("control_reaction", ["indole_1a", "dihydropyran_4aa", "catalyst", "solvent"], [
        field("solvent", "THF", e3),
        field("time", None, []),
        field("temperature", None, []),
    ])],
    outcomes=[
        field("reaction_result", "no reaction", e3),
        field("recovered_indole_yield", q(100, "%"), e3, ["indole_1a"]),
        field("recovered_4aa_yield", q(77, "%"), e3, ["dihydropyran_4aa"]),
    ],
    unresolved=[
        "Scheme 2 does not report reaction duration or temperature.",
        "Recovery measurement method, workup, and purification are not stated in the main text.",
    ],
))

# Scheme 3: three experimentally distinct stages; the last arrow is a two-step combined outcome.
records.append(record(
    "scheme3_jones_oxidation", "reported_experiment", e3,
    participants=[
        participant("nonynol", "reactant", "non-1-yn-3-ol", "non-1-yn-3-ol", e3),
        participant("jones_reagent", "reagent", "Jones oxidation", "Jones oxidation reagent", e3),
        participant("nonynone", "product", "alkynyl ketone", "non-1-yn-3-one", e3),
    ],
    steps=[step("oxidation", ["nonynol", "jones_reagent"], [
        field("operation", "Jones oxidation", e3),
        field("temperature", None, []),
        field("time", None, []),
    ])],
    outcomes=[field("reported_yield_nonynone", q(56, "%"), e3, ["nonynone"])],
    unresolved=[
        "Jones reagent composition, amounts, solvent, time, workup, purification, and yield basis are absent from the main-text scheme.",
        "The preparation is linked to reference 7, but no external procedure is imported as source evidence.",
    ],
))
records.append(record(
    "scheme3_liald4_reduction", "reported_experiment", e3,
    participants=[
        participant("nonynone", "reactant", "alkynyl ketone", "non-1-yn-3-one", e3),
        participant("liald4", "reagent", "LiAlD4", "lithium aluminium deuteride", e3),
        solvent("Et2O", e3),
        participant("deuterated_propargyl_alcohol", "product", "deuterated propargylic alcohol", None, e3),
    ],
    steps=[step("deuteride_reduction", ["nonynone", "liald4", "solvent"], [
        field("solvent", "Et2O", e3),
        field("temperature", q(-40, "°C"), e3),
        field("time", None, []),
    ])],
    outcomes=[field("reported_yield_deuterated_propargyl_alcohol", q(84, "%"), e3, ["deuterated_propargyl_alcohol"])],
    unresolved=[
        "Amounts, time, workup, purification, and yield basis are absent from the main-text scheme.",
        "The preparation is linked to reference 8, but no external procedure is imported as source evidence.",
    ],
))
records.append(record(
    "scheme3_claisen_then_lialh4", "reported_experiment", e3,
    participants=[
        participant("deuterated_propargyl_alcohol", "reactant", "deuterated propargylic alcohol", None, e3),
        participant("triethyl_orthoacetate", "reagent", "CH3C(OEt)3", "triethyl orthoacetate", e3),
        participant("propionic_acid", "reagent", "CH3CH2COOH", "propionic acid", e3),
        participant("lialh4", "reagent", "LiAlH4", "lithium aluminium hydride", e3),
        solvent("THF", e3),
        participant("allenol_2a_d", "product", "2a-D", "deuterium-labeled beta-allenol 2a-D", e3),
    ],
    steps=[
        step("ortho_claisen_rearrangement", ["deuterated_propargyl_alcohol", "triethyl_orthoacetate", "propionic_acid"], [
            field("temperature", q(140, "°C"), e3),
            field("time", None, []),
        ]),
        step("lialh4_reduction", ["lialh4", "solvent"], [
            field("solvent", "THF", e3),
            field("temperature", "r.t.", e3),
            field("time", None, []),
        ]),
    ],
    outcomes=[field("two_step_reported_yield_2a_D", q(59, "%"), e3, ["allenol_2a_d"])],
    notes=[fact("Scheme 3 explicitly labels the 59% outcome as covering two steps.", e3)],
    unresolved=[
        "The ortho-Claisen intermediate is not drawn or named in Scheme 3 and is not invented as a participant.",
        "Amounts, times, workup, purification, and yield basis are absent from the main-text scheme.",
        "The preparation is linked to reference 9, but no external procedure is imported as source evidence.",
    ],
))

# Scheme 4 isotope-distribution experiment.
records.append(record(
    "scheme4_isotope_distribution", "reported_experiment", e3,
    participants=[
        participant("indole_1e", "reactant", "1e", "N-methylindole", e3),
        participant("allenol_2a_d", "reactant", "2a-D", "deuterium-labeled beta-allenol 2a-D", e3),
        catalyst("PtCl4", 5, e3),
        solvent("THF", e3),
        participant("product_3ea_d", "product", "3ea-D", "deuterium-labeled cyclization product 3ea-D", e3),
    ],
    steps=[step("isotope_distribution_cyclization", ["indole_1e", "allenol_2a_d", "catalyst", "solvent"], [
        field("solvent", "THF", e3),
        field("temperature", "r.t.", e3),
        field("time", None, []),
    ])],
    outcomes=[
        field("reported_yield_3ea_D", q(56, "%"), e3, ["product_3ea_d"]),
        field("C3_prime_D_incorporation", q(28, "%"), e3, ["product_3ea_d"]),
        field("C1_double_prime_D_incorporation", q(25, "%"), e3, ["product_3ea_d"]),
    ],
    notes=[fact("The paper directs readers to Supporting Information for determination of isotopic distribution, but no SI file was supplied or associated here.", e3)],
    unresolved=[
        "Reaction duration, amounts, yield basis, workup, purification, and isotope-distribution method are unavailable in the supplied main-text pages.",
        "The positional isotope assignment and complete product structure remain unverified machine interpretations.",
    ],
))

# Scheme 5 is explicitly proposed mechanism, not a batch experiment; page 4 continues its discussion.
e34 = ev(3) + ev(4)
records.append(record(
    "scheme5_proposed_mechanism", "mechanism", e34,
    participants=[
        participant("indole_1e", "reactant", "1e", "N-methylindole", e34),
        participant("allenol_2a_d", "reactant", "2a-D", "deuterium-labeled beta-allenol 2a-D", e34),
        participant("product_3ea_d", "product", "3ea-D", "deuterium-labeled cyclization product 3ea-D", e34),
    ],
    notes=[
        fact("Scheme 5 is the authors' proposed rationale involving intermediates 5-13, carbometalation, beta-D/beta-H elimination, hydrometalation, allylic substitution, and protonolysis.", e34),
        fact("Alternative cyclization through intermediate 9 and coexistence of HPtCl3/DPtCl3 are proposed to rationalize the isotope distribution.", e34),
        fact("No intermediate yield or direct isolation is reported; the scheme is not represented as an experimental batch.", e34),
    ],
    unresolved=[
        "Mechanistic intermediates and arrows are proposals rather than independently verified experimental entities.",
        "Detailed isotope-distribution evidence is said to be in SI, which was not supplied or explicitly associated.",
    ],
))


data = json.loads(DATASET.read_text())
assert [d["document_id"] for d in data["documents"]] == [DOC]
existing_ids = {r["record_id"] for r in data["experiments"]}
submitted_ids = [r["record_id"] for r in records]
assert len(submitted_ids) == len(set(submitted_ids))
assert not (existing_ids - set(submitted_ids))
assert len(records) == 32, len(records)
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"records": len(records), "output": str(OUT.relative_to(ROOT))}, ensure_ascii=False))
