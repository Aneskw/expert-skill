#!/usr/bin/env python3
"""Build the page 1--5 machine extraction for doc_1c07b578cf3ed9be."""
import json
from pathlib import Path

DOC = "doc_1c07b578cf3ed9be"
ROOT = Path(__file__).resolve().parents[1]


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


def participant(entity_id, role, label, evidence, name=None, smiles=None, amounts=()):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence) if name else fact(None, ()),
        "smiles": fact(smiles, evidence) if smiles else fact(None, ()),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": [field(n, v, evidence) for n, v in amounts],
    }


def step(step_id, ids, conditions):
    return {"step_id": step_id, "participant_ids": list(ids), "conditions": conditions}


def record(suffix, kind, evidence, participants, steps=(), outcomes=(), notes=(), unresolved=()):
    return {
        "record_id": f"{DOC}:{suffix}",
        "document_id": DOC,
        "source_reaction_id": suffix,
        "record_kind": kind,
        "status": "needs_review",
        "completeness": "partial",
        "evidence_ids": list(dict.fromkeys(evidence)),
        "participants": list(participants),
        "steps": list(steps),
        "outcomes": list(outcomes),
        "notes": [fact(x, evidence) for x in notes],
        "review": {
            "method": "model",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": list(unresolved),
        },
    }


records = []

# Page 1, Scheme 1: cited prior work and the authors' untested/unspecified proposal.
e1 = ev(1)
records.append(record(
    "scheme1_ref7_monoallene", "literature_example", e1,
    [
        participant("s1_acid", "reactant", "generic 2,3-allenoic acid", e1),
        participant("s1_monoallene", "reactant", "generic monoallene", e1),
        participant("s1_libr", "reagent", "LiBr", e1, name="lithium bromide"),
        participant("s1_bq", "reagent", "BQ", e1, name="p-benzoquinone", smiles="O=C1C=CC(=O)C=C1"),
        participant("s1_hoac", "solvent", "HOAc", e1, name="acetic acid", smiles="CC(=O)O"),
        participant("s1_product", "product", "4-(bromo-2(E)-alken-2-yl)-2(5H)-furanone type product", e1),
    ],
    [step("cited_cyclization", ["s1_acid", "s1_monoallene", "s1_libr", "s1_bq", "s1_hoac"], [
        field("operation", "Pd(II)-catalyzed cyclization reported in Ref. 7", e1),
        field("time", None, ()), field("temperature", None, ()),
    ])],
    notes=("Scheme 1 upper branch is prior work cited as Ref. 7, not a new experiment in this paper.",),
    unresolved=("Generic structures, palladium catalyst identity/loading, time, temperature and yield are not stated in Scheme 1.",),
))
records.append(record(
    "scheme1_hypothetical_product3", "general_scheme", e1,
    [
        participant("s1g_acid", "reactant", "generic 2,3-allenoic acid", e1),
        participant("s1g_bisallene", "reactant", "generic 1,5-bisallene 1", e1),
        participant("s1g_product", "product", "hypothetical product 3", e1),
    ],
    [step("proposed_cyclization", ["s1g_acid", "s1g_bisallene"], [
        field("operation", "Proposed cyclization indicated by a question mark in Scheme 1", e1),
        field("time", None, ()), field("temperature", None, ()),
    ])],
    notes=("This is a conceptual reaction proposal, not a reported batch or observed product.",),
    unresolved=("All operational conditions and outcome are unspecified; product 3 was only hypothesized.",),
))

# Scheme 2 exploratory experiments, supported by pages 1 and 2.
e12 = e1 + ev(2)
records.append(record(
    "scheme2_ref7_conditions_failure", "reported_experiment", e12,
    [
        participant("fail_1a", "reactant", "1a", e12, name="bis(2,3-butadienyl)tosylamide", smiles="C=C=CCN(CC=C=C)S(=O)(=O)c1ccc(C)cc1"),
        participant("fail_2a", "reactant", "2a", e12, name="2,4-dimethyl-2,3-pentadienoic acid", smiles="O=C(O)C(C)=C=C(C)C"),
        participant("fail_pd", "catalyst", "Pd(OAc)2", e12, name="palladium(II) acetate", amounts=(("catalyst_loading", {"number": 2, "unit": "mol%"}),)),
        participant("fail_libr", "reagent", "LiBr·H2O", e12, name="lithium bromide hydrate"),
        participant("fail_bq", "reagent", "BQ", e12, name="p-benzoquinone", smiles="O=C1C=CC(=O)C=C1"),
        participant("fail_hoac", "solvent", "HOAc", e12, name="acetic acid", smiles="CC(=O)O"),
        participant("fail_3a", "product", "3a (expected; not observed)", e12),
        participant("fail_mix", "product", "unidentified inseparable mixture", e12),
    ],
    [step("reaction", ["fail_1a", "fail_2a", "fail_pd", "fail_libr", "fail_bq", "fail_hoac"], [
        field("temperature", {"number": 60, "unit": "°C"}, e12),
        field("time", None, ()),
    ])],
    [
        field("expected_product_result", "not observed", e12, ["fail_3a"]),
        field("reaction_result", "unidentified inseparable mixture", e12, ["fail_mix"]),
    ],
    unresolved=("Duration, substrate quantities, LiBr·H2O/BQ amounts, workup and product identities are not reported.",),
))
records.append(record(
    "scheme2_dmso_60c", "reported_experiment", e12,
    [
        participant("dmso_1a", "reactant", "1a", e12, name="bis(2,3-butadienyl)tosylamide", smiles="C=C=CCN(CC=C=C)S(=O)(=O)c1ccc(C)cc1"),
        participant("dmso_2a", "reactant", "2a", e12, name="2,4-dimethyl-2,3-pentadienoic acid", smiles="O=C(O)C(C)=C=C(C)C"),
        participant("dmso_pd", "catalyst", "[PdCl2(PhCN)2]", e12, name="bis(benzonitrile)palladium(II) dichloride", amounts=(("catalyst_loading", {"number": 5, "unit": "mol%"}),)),
        participant("dmso_bq", "reagent", "BQ", e12, name="p-benzoquinone", smiles="O=C1C=CC(=O)C=C1"),
        participant("dmso_solvent", "solvent", "DMSO", e12, name="dimethyl sulfoxide", smiles="CS(C)=O"),
        participant("dmso_4a", "product", "cis-4a", e12),
        participant("dmso_5a", "product", "5a", e12),
    ],
    [step("reaction", ["dmso_1a", "dmso_2a", "dmso_pd", "dmso_bq", "dmso_solvent"], [
        field("temperature", {"number": 60, "unit": "°C"}, e12),
        field("time", {"number": 2, "unit": "h"}, e12),
        field("operation", "Reaction conducted in the absence of LiBr", e12),
    ])],
    [
        field("reported_yield_cis_4a", {"number": 32, "unit": "%"}, e12, ["dmso_4a"]),
        field("reported_yield_5a", {"number": 10, "unit": "%"}, e12, ["dmso_5a"]),
        field("yield_measurement_basis", None, ()),
    ],
    unresolved=("The source does not state quantities, atmosphere, workup, purification or the yield basis for this 60 °C experiment.",),
))


def table1_participants(entry, catalyst_label, solvent_label, ligand=None, ligand_loading=None):
    e = ev(2)
    smiles_by_solvent = {"DMSO": "CS(C)=O", "DMF": "CN(C)C=O", "DCE": "ClCCCl", "toluene": "Cc1ccccc1", "MeCN": "CC#N", "THF": "C1CCOC1"}
    p = [
        participant(f"t1e{entry}_1a", "reactant", "1a", e, name="bis(2,3-butadienyl)tosylamide", smiles="C=C=CCN(CC=C=C)S(=O)(=O)c1ccc(C)cc1", amounts=(("amount", {"number": 0.2, "unit": "mmol"}),)),
        participant(f"t1e{entry}_2a", "reactant", "2a", e, name="2,4-dimethyl-2,3-pentadienoic acid", smiles="O=C(O)C(C)=C=C(C)C", amounts=(("amount", {"number": 0.6, "unit": "mmol"}),)),
        participant(f"t1e{entry}_pd", "catalyst", catalyst_label, e, amounts=(("catalyst_loading", {"number": 5, "unit": "mol%"}),)),
        participant(f"t1e{entry}_bq", "reagent", "BQ", e, name="p-benzoquinone", smiles="O=C1C=CC(=O)C=C1", amounts=(("amount", {"number": 0.25, "unit": "mmol"}), ("equivalents", {"number": 1.25, "unit": "equiv"}))),
        participant(f"t1e{entry}_solvent", "solvent", solvent_label, e, smiles=smiles_by_solvent.get(solvent_label), amounts=(("volume", {"number": 3, "unit": "mL"}),)),
        participant(f"t1e{entry}_4a", "product", "cis-4a", e),
        participant(f"t1e{entry}_5a", "product", "5a", e),
    ]
    if ligand:
        amounts = (("ligand_loading", {"number": ligand_loading, "unit": "mol%"}),) if ligand_loading else ()
        p.insert(4, participant(f"t1e{entry}_ligand", "reagent", ligand, e, amounts=amounts))
    return p


table1 = [
    (1, "[PdCl2(PhCN)2]", "DMSO", None, None, 32, 10),
    (2, "[PdCl2(PhCN)2]", "DMF", None, None, 35, 10),
    (3, "[PdCl2(PhCN)2]", "DCE", None, None, 6, "not determined"),
    (4, "[PdCl2(PhCN)2]", "toluene", None, None, 8, "not determined"),
    (5, "[PdCl2(PhCN)2]", "MeCN", None, None, 45, 15),
    (6, "[PdCl2(PhCN)2]", "THF", None, None, 24, 7),
    (7, "[PdCl2(PhCN)2]", "MeCN", None, None, 25, "not determined"),
    (8, "[PdCl2(Sphos)2]", "MeCN", None, None, 44, "not determined"),
    (9, "[PdCl2(PhCN)2]", "MeCN", "dppb", 5, 69, "not determined"),
    (10, "[PdCl2(PhCN)2]", "MeCN", "dppe", None, 79, "not determined"),
    (11, "[PdCl2(PhCN)2]", "MeCN", "binap", None, 41, 21),
]
for entry, catalyst, solvent, ligand, ligand_loading, y4, y5 in table1:
    e = ev(2)
    p = table1_participants(entry, catalyst, solvent, ligand, ligand_loading)
    if entry == 9:
        # The 5 mol% dppb loading is stated in the page-1 prose, not in the table row.
        p[4]["amounts"][0]["fact"] = fact({"number": 5, "unit": "mol%"}, e1)
    ids = [x["entity_id"] for x in p if x["role"] != "product"]
    outs = [
        field("1H_NMR_yield_cis_4a", {"number": y4, "unit": "%"}, e, [f"t1e{entry}_4a"]),
        field("1H_NMR_yield_5a", {"number": y5, "unit": "%"} if isinstance(y5, int) else y5, e, [f"t1e{entry}_5a"]),
        field("yield_measurement_basis", "1H NMR analysis with 1,3,5-trimethylbenzene as internal standard", e, [f"t1e{entry}_4a", f"t1e{entry}_5a"]),
    ]
    if entry == 5:
        outs += [
            field("isolated_yield_cis_4a", {"number": 41, "unit": "%"}, e1, [f"t1e{entry}_4a"]),
            field("isolated_yield_5a", {"number": 10, "unit": "%"}, e1, [f"t1e{entry}_5a"]),
        ]
    unresolved = ["Product structures, workup and purification are not supplied for this optimization row."]
    evidence = e
    if entry in (5, 9, 10):
        evidence = e1 + e
    if entry == 7:
        unresolved.append("Entry 7 appears to show the same catalyst/solvent and shared conditions as entry 5 but a different yield; no visible footnote explains the difference.")
    if ligand and ligand_loading is None:
        unresolved.append(f"The amount of {ligand} is not explicitly stated for this row.")
    records.append(record(
        f"table1_entry{entry}", "optimization_entry", evidence, p,
        [step("reaction", ids, [
            field("atmosphere", "argon", e),
            field("operation", "Schlenk tube", e),
            field("temperature", {"number": 70, "unit": "°C"}, e),
            field("time", {"number": 2, "unit": "h"}, e),
        ])], outs,
        unresolved=unresolved,
    ))

# Page 2, Scheme 3: two independent RCM rows.
for label_in, label_out, z_value, hours, yld in [
    ("cis-4c", "cis-6a", "TsN", 6, 83),
    ("cis-4g", "cis-6b", "CH2", 4, 67),
]:
    e = ev(2)
    key = label_out.replace("cis-", "")
    p = [
        participant(f"rcm_{key}_sub", "reactant", label_in, e),
        participant(f"rcm_{key}_cat", "catalyst", "Grubbs 2nd", e, name="Grubbs second-generation ruthenium catalyst", amounts=(("catalyst_loading", {"number": 10, "unit": "mol%"}),)),
        participant(f"rcm_{key}_dcm", "solvent", "DCM", e, name="dichloromethane", smiles="ClCCl"),
        participant(f"rcm_{key}_prod", "product", label_out, e),
    ]
    records.append(record(
        f"scheme3_rcm_{key}", "reported_experiment", e, p,
        [step("ring_closing_metathesis", [f"rcm_{key}_sub", f"rcm_{key}_cat", f"rcm_{key}_dcm"], [
            field("temperature", "reflux", e), field("time", {"number": hours, "unit": "h"}, e),
        ])],
        [field(f"reported_yield_{label_out}", {"number": yld, "unit": "%"}, e, [f"rcm_{key}_prod"]), field("yield_measurement_basis", None, ())],
        notes=(f"The Scheme 3 row identifies the tether as Z = {z_value}.",),
        unresolved=("Atmosphere, reagent quantities other than catalyst loading, workup, purification and yield basis are not stated.",),
    ))

# Page 2 prose: racemic 2e gives a diastereomeric mixture.
e2 = ev(2)
records.append(record(
    "prose_racemic_2e_diastereomeric_mixture", "reported_experiment", e2,
    [
        participant("rac_2e", "reactant", "racemic 2e", e2, name="racemic axially chiral 2,3-allenoic acid 2e"),
        participant("rac_mix", "product", "diastereomeric mixture", e2),
    ],
    [],
    [field("reaction_result", "diastereomeric mixture", e2, ["rac_mix"]), field("reported_yield", None, ())],
    unresolved=("The sentence does not restate the coupling partner, conditions, product labels, ratio or yield; these were not inferred from the adjacent enantioenriched experiment.",),
))


def table2_record(entry, acid_label, bis_label, product_label, yld, r1, r2, z):
    e = ev(3)
    p = [
        participant(f"t2e{entry}_bis", "reactant", bis_label, e, amounts=(("amount", {"number": 0.2, "unit": "mmol"}),)),
        participant(f"t2e{entry}_acid", "reactant", acid_label, e, amounts=(("amount", {"number": 0.6, "unit": "mmol"}),)),
        participant(f"t2e{entry}_pd", "catalyst", "[PdCl2(PhCN)2]", e, amounts=(("catalyst_loading", {"number": 5, "unit": "mol%"}),)),
        participant(f"t2e{entry}_dppe", "reagent", "dppe", e, name="1,2-bis(diphenylphosphino)ethane", amounts=(("ligand_loading", {"number": 5, "unit": "mol%"}),)),
        participant(f"t2e{entry}_bq", "reagent", "BQ", e, name="p-benzoquinone", smiles="O=C1C=CC(=O)C=C1", amounts=(("amount", {"number": 0.25, "unit": "mmol"}), ("equivalents", {"number": 1.25, "unit": "equiv"}))),
        participant(f"t2e{entry}_mecn", "solvent", "MeCN", e, name="acetonitrile", smiles="CC#N", amounts=(("volume", {"number": 3, "unit": "mL"}),)),
        participant(f"t2e{entry}_prod", "product", product_label, e),
    ]
    evidence = e
    notes = [f"Table 2 substituent assignment: R1 = {r1}; R2 = {r2}; Z = {z}.", "Only the cis product was reported for the substrate-scope reactions."]
    unresolved = ["Full batch workup, purification and product structure verification are unavailable in the main-text table."]
    if entry == 1:
        evidence = e + ev(4)
        e4 = ev(4)
        # Add detailed typical-procedure quantities without erasing rounded table values.
        p[0]["amounts"] += [field("mass", {"number": 55, "unit": "mg"}, e4), field("amount_detailed_batch", {"number": 0.20, "unit": "mmol"}, e4)]
        p[1]["amounts"] += [field("mass", {"number": 74, "unit": "mg"}, e4), field("amount_detailed_batch", {"number": 0.59, "unit": "mmol"}, e4)]
        p[2]["amounts"] += [field("mass", {"number": 4, "unit": "mg"}, e4), field("amount_detailed_batch", {"number": 0.010, "unit": "mmol"}, e4)]
        p[3]["amounts"] += [field("mass", {"number": 5, "unit": "mg"}, e4), field("amount_detailed_batch", {"number": 0.013, "unit": "mmol"}, e4)]
        p[4]["amounts"] += [field("mass", {"number": 29, "unit": "mg"}, e4), field("amount_detailed_batch", {"number": 0.27, "unit": "mmol"}, e4)]
        p[-1]["amounts"] += [field("mass", {"number": 76, "unit": "mg"}, e4)]
        p += [
            participant("t2e1_ch2cl2", "solvent", "CH2Cl2", e4, name="dichloromethane", smiles="ClCCl", amounts=(("volume", {"number": 50, "unit": "mL"}),)),
            participant("t2e1_k2co3", "reagent", "aqueous K2CO3 (10%)", e4, name="aqueous potassium carbonate", amounts=(("concentration", {"number": 10, "unit": "%"}), ("volume", {"number": 30, "unit": "mL"}))),
            participant("t2e1_water", "reagent", "water", e4, smiles="O", amounts=(("volume", {"number": 30, "unit": "mL"}),)),
            participant("t2e1_na2so4", "reagent", "Na2SO4", e4, name="sodium sulfate"),
            participant("t2e1_eluent", "solvent", "CH2Cl2/diethyl ether (10:1)", e4),
        ]
        notes += ["The detailed batch uses 0.59 mmol 2a and 0.27 mmol BQ whereas Table 2 reports rounded/common amounts of 0.6 and 0.25 mmol."]
        unresolved = ["Reaction completion was monitored by TLC; the detailed paragraph does not independently state an elapsed time, while the Table 2 reaction arrow states 2 h.", "Structures and stereochemistry remain machine-unverified; SI is unassociated."]
    # Explicit reaction participants only; workup participants are assigned below for entry 1.
    rxn_ids = [f"t2e{entry}_bis", f"t2e{entry}_acid", f"t2e{entry}_pd", f"t2e{entry}_dppe", f"t2e{entry}_bq", f"t2e{entry}_mecn"]
    steps = [step("reaction", rxn_ids, [
        field("atmosphere", "argon", e), field("temperature", {"number": 70, "unit": "°C"}, e), field("time", {"number": 2, "unit": "h"}, e),
    ])]
    if entry == 1:
        e4 = ev(4)
        steps += [
            step("workup", ["t2e1_ch2cl2", "t2e1_k2co3", "t2e1_water", "t2e1_na2so4"], [
                field("operation", "Diluted with CH2Cl2; washed sequentially with aqueous K2CO3 and water; dried over Na2SO4; filtered and evaporated", e4),
            ]),
            step("purification", ["t2e1_eluent"], [field("purification", "Silica-gel column chromatography, CH2Cl2/diethyl ether = 10:1", e4)]),
        ]
    outs = [
        field(f"isolated_yield_{product_label}", {"number": yld, "unit": "%"}, evidence, [f"t2e{entry}_prod"]),
        field("yield_measurement_basis", "isolated yield", e, [f"t2e{entry}_prod"]),
    ]
    return record(f"table2_entry{entry}", "substrate_scope_entry", evidence, p, steps, outs, notes, unresolved)


table2 = [
    (1, "2a", "1a", "cis-4a", 73, "Me", "Me", "TsN"),
    (2, "2b", "1a", "cis-4b", 81, "H", "Me", "TsN"),
    (3, "2c", "1a", "cis-4c", 59, "allyl", "Me", "TsN"),
    (4, "2d", "1a", "cis-4d", 59, "H", "-(CH2)5-", "TsN"),
    (5, "2a", "1b", "cis-4e", 68, "Me", "Me", "CH2"),
    (6, "2b", "1b", "cis-4f", 79, "H", "Me", "CH2"),
    (7, "2c", "1b", "cis-4g", 52, "allyl", "Me", "CH2"),
    (8, "2a (as printed)", "1c", "cis-4h", 54, "H", "Me", "O"),
]
for row in table2:
    rec = table2_record(*row)
    if row[0] == 8:
        rec["review"]["unresolved"].append("Table 2 entry 8 prints acid label 2a although its R1 = H, R2 = Me assignment matches 2b in the other rows; the printed label was preserved without correction.")
    records.append(rec)

# Page 3, Scheme 4: three enantioenriched reactions.
scheme4 = [
    ("scheme4_r2e_to_4i", "1a", "(R)-2e", 98.8, "(R,S,R,R)-4i", 63, "n-C5H11"),
    ("scheme4_s2f_to_4j", "1d", "(S)-2f", 98.1, "(S,R,S,S)-4j", 63, "Et"),
    ("scheme4_s2g_to_4k", "1d", "(S)-2g", 87.7, "(S,R,S,S)-4k", 61, "Me"),
]
for suffix, bis_label, acid_label, ee, product_label, yld, r_group in scheme4:
    e = ev(3)
    key = suffix.split("_")[-1]
    p = [
        participant(f"{key}_bis", "reactant", bis_label, e),
        participant(f"{key}_acid", "reactant", acid_label, e, amounts=(("starting_material_ee", {"number": ee, "unit": "%"}),)),
        participant(f"{key}_pd", "catalyst", "[PdCl2(PhCN)2]", e, amounts=(("catalyst_loading", {"number": 5, "unit": "mol%"}),)),
        participant(f"{key}_dppe", "reagent", "dppe", e, amounts=(("ligand_loading", {"number": 5, "unit": "mol%"}),)),
        participant(f"{key}_bq", "reagent", "BQ", e, name="p-benzoquinone", smiles="O=C1C=CC(=O)C=C1", amounts=(("equivalents", {"number": 1.25, "unit": "equiv"}),)),
        participant(f"{key}_mecn", "solvent", "MeCN", e, name="acetonitrile", smiles="CC#N"),
        participant(f"{key}_prod", "product", product_label, e),
    ]
    records.append(record(
        suffix, "substrate_scope_entry", e, p,
        [step("reaction", [x["entity_id"] for x in p[:-1]], [field("temperature", {"number": 70, "unit": "°C"}, e), field("time", {"number": 2, "unit": "h"}, e)])],
        [field(f"reported_yield_{key}", {"number": yld, "unit": "%"}, e, [f"{key}_prod"]), field("yield_measurement_basis", None, ())],
        notes=(f"Scheme 4 assigns R = {r_group} for this row.",),
        unresolved=("Substrate quantities, atmosphere, workup, purification, product ee and yield basis are not stated in Scheme 4; absolute configurations remain machine-unverified.",),
    ))

# Page 4, Scheme 5: proposed mechanism, not an experimental batch.
e34 = ev(3) + ev(4)
mech_parts = [
    participant("m_s2g_1", "reactant", "first molecule of (S)-2g", e34),
    participant("m_s2g_2", "reactant", "second molecule of (S)-2g", e34),
    participant("m_1d", "reactant", "1d", e34),
    participant("m_pdii", "catalyst", "Pd(II)", e34),
    participant("m_bq", "reagent", "BQ", e34, name="p-benzoquinone", smiles="O=C1C=CC(=O)C=C1"),
    participant("m_m1", "unspecified_agent", "M1", e34),
    participant("m_m2a", "unspecified_agent", "M2-a", e34),
    participant("m_m2b", "unspecified_agent", "M2-b (disfavored)", e34),
    participant("m_m3", "unspecified_agent", "cis-M3", e34),
    participant("m_m4", "unspecified_agent", "cis-M4", e34),
    participant("m_4k", "product", "(S,R,S,S)-4k", e34),
]
records.append(record(
    "scheme5_proposed_mechanism", "mechanism", e34, mech_parts,
    [
        step("anti_oxypalladation_1", ["m_s2g_1", "m_pdii", "m_m1"], [field("operation", "Proposed cyclic anti-oxypalladation to M1", e34)]),
        step("intermolecular_carbopalladation", ["m_m1", "m_1d", "m_m2a", "m_m2b"], [field("operation", "Proposed carbopalladation; M2-a favored over M2-b on steric grounds", e34)]),
        step("intramolecular_carbopalladation", ["m_m2a", "m_m3"], [field("operation", "Proposed intramolecular carbopalladation to cis-M3", e34)]),
        step("anti_oxypalladation_2", ["m_m3", "m_s2g_2", "m_m4"], [field("operation", "Proposed coordination and second anti-oxypalladation to cis-M4", e34)]),
        step("reductive_elimination", ["m_m4", "m_4k"], [field("operation", "Proposed reductive elimination releasing 4k and Pd(0)", e34)]),
        step("catalyst_regeneration", ["m_bq", "m_pdii"], [field("operation", "Proposed oxidation of Pd(0) by BQ and H+ to regenerate Pd(II)", e34)]),
    ],
    notes=("Scheme 5 is explicitly labeled a plausible catalytic cycle and must not be treated as direct observation of intermediates.",),
    unresolved=("All intermediates and elementary steps are mechanistic proposals; their structures and kinetics are not experimentally established here.",),
))

assert len(records) == 30, len(records)
(ROOT / "raw_model" / "records_pages_0001_0005.json").write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"records": len(records), "output": str(ROOT / "raw_model" / "records_pages_0001_0005.json")}, ensure_ascii=False))
