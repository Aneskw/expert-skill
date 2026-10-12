#!/usr/bin/env python3
"""Build evidence-linked machine records for ar020133k PDF pages 7-12."""
from __future__ import annotations

import json
from pathlib import Path


DOC = "doc_e26f259781f314bb"
ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "raw_model" / "extracted_records_pages_0007_0012.json"
COVERAGE = ROOT / "coverage" / "pages_0007_0012.json"
TASKS = ROOT / "tasks.json"
I = {p: f"{DOC}:page{p}:image" for p in range(7, 13)}
T = {p: f"{DOC}:page{p}:text" for p in range(7, 13)}


def fact(value, page=None, *, text=False, evidence_ids=None):
    if value is None:
        return {"value": None, "evidence_ids": [], "verification": "missing"}
    ev = list(evidence_ids or ([] if page is None else [T[page] if text else I[page]]))
    return {"value": value, "evidence_ids": ev, "verification": "unreviewed"}


def field(name, value, page, target=None, *, text=False, evidence_ids=None):
    item = {"name": name, "fact": fact(value, page if value is not None else None, text=text, evidence_ids=evidence_ids)}
    if target:
        item["target_entity_ids"] = [target] if isinstance(target, str) else list(target)
    return item


def participant(entity_id, role, label, page, *, name=None, smiles=None, amounts=None, text=False):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, page, text=text),
        "name": fact(name, page, text=text) if name else fact(None),
        "smiles": fact(smiles, page, text=text) if smiles else fact(None),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": amounts or [],
    }


def qty(number, unit, raw_text=None, **extra):
    value = {"number": number, "unit": unit}
    if raw_text:
        value["raw_text"] = raw_text
    value.update(extra)
    return value


def rng(minimum, maximum, unit, raw_text):
    return {"minimum": minimum, "maximum": maximum, "unit": unit, "raw_text": raw_text}


def make_step(step_id, ids, page, conditions=(), *, fill_missing=True):
    result = [field(name, value, page, text=is_text) for name, value, is_text in conditions]
    names = {item["name"] for item in result}
    if fill_missing and "temperature" not in names:
        result.append(field("temperature", None, page))
    if fill_missing and "time" not in names:
        result.append(field("time", None, page))
    return {"step_id": step_id, "participant_ids": list(ids), "conditions": result}


def record(suffix, page, kind, participants, steps, outcomes=(), *, notes=(), unresolved=(), extra_pages=()):
    outcomes = list(outcomes)
    if kind != "mechanism" and not any(item["name"] == "yield" for item in outcomes):
        outcomes.append(field("yield", None, page))
    evidence = [I[page], T[page]]
    for other in extra_pages:
        evidence.extend([I[other], T[other]])
    evidence = list(dict.fromkeys(evidence))
    if kind == "mechanism":
        standard = ["This is a proposed mechanistic or selectivity diagram, not a reported preparative experiment."]
    else:
        standard = [
            "The Account does not provide a complete experimental procedure, workup, purification, atmosphere, or yield measurement basis for this record.",
            "No supporting-information file was supplied or explicitly associated; missing details remain missing.",
        ]
        if kind in {"general_scheme", "literature_example"}:
            standard.append("Generic R-group structures and/or summarized yields are not individual fully specified compounds.")
    return {
        "record_id": f"{DOC}:{suffix}",
        "document_id": DOC,
        "source_reaction_id": suffix,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": evidence,
        "participants": participants,
        "steps": steps,
        "outcomes": outcomes,
        "notes": [fact(value, p, text=is_text) for value, p, is_text in notes],
        "review": {"method": "none", "reviewer": None, "checked_fields": [], "unresolved": standard + list(unresolved)},
    }


records = []

# Page 7: Schemes 30-37.
p = 7
ps = [
    participant("s30_allenol", "reactant", "generic substituted 2,3-allenol", p),
    participant("s30_halide", "reactant", "R3X", p),
    participant("s30_pd0", "catalyst", "Pd(0)", p),
    participant("s30_epoxide", "product", "three-membered vinylic epoxide (Path A)", p),
    participant("s30_dihydrofuran", "product", "five-membered 2,5-dihydrofuran (Path B)", p),
]
records.append(record("p07_scheme30_product_pathways", p, "general_scheme", ps, [
    make_step("path_a_pd0_coupling_cyclization", ["s30_allenol", "s30_halide", "s30_pd0", "s30_epoxide"], p),
    make_step("path_b_catalytic_coupling_cyclization", ["s30_allenol", "s30_halide", "s30_dihydrofuran"], p),
], notes=[("Scheme 30 contrasts the observed three-membered Pd(0) path with a desired five-membered path; it is not a single fully specified experiment.", p, False)]))

ps = [
    participant("s31_allenol", "reactant", "n-C4H9/CH3-substituted 2,3-allenol", p),
    participant("s31_allylbr", "reactant", "allyl bromide", p, smiles="C=CCBr"),
    participant("s31_pdcl2", "catalyst", "PdCl2", p, smiles="[Pd+2].[Cl-].[Cl-]"),
    participant("s31_product", "product", "allyl-substituted 2,5-dihydrofuran", p),
]
records.append(record("p07_scheme31_pdcl2_allyl_bromide_coupling", p, "reported_experiment", ps, [
    make_step("pdcl2_coupling_cyclization", [x["entity_id"] for x in ps], p),
], [field("yield", qty(76, "%"), p, "s31_product")], unresolved=["Scheme 31 does not state catalyst loading, solvent, temperature, or time for the 76% example."]))

ps = [
    participant("s31m_allenol", "reactant", "n-C4H9/CH3-substituted 2,3-allenol", p),
    participant("s31m_pdcl2", "catalyst", "PdCl2", p, smiles="[Pd+2].[Cl-].[Cl-]"),
    participant("s31m_allylbr", "reactant", "allyl bromide", p, smiles="C=CCBr"),
    participant("s31m_product", "product", "allyl-substituted 2,5-dihydrofuran", p),
]
records.append(record("p07_scheme31_pdii_catalytic_cycle", p, "mechanism", ps, [
    make_step("cyclization_and_hcl_loss", ["s31m_allenol", "s31m_pdcl2"], p, fill_missing=False),
    make_step("allyl_bromide_capture_and_dehalopalladation", ["s31m_allylbr", "s31m_product"], p, fill_missing=False),
], notes=[("The palladium intermediates and Pd(II) regeneration in Scheme 31 are proposed mechanistic species.", p, False)]))

for suffix, allyl_equiv, time_h, desired, dimer in [
    ("5_equiv", 5, 4, qty(4, "%"), qty(65, "%")),
    ("0_25_equiv", 0.25, 10, "trace", qty(73, "%")),
    ("0_equiv", 0, 48, "not detected", qty(24, "%")),
]:
    ps = [
        participant(f"s32_{suffix}_allenol", "reactant", "unsubstituted terminal 2,3-allenol bearing a cyclohexyl carbinol center", p),
        participant(f"s32_{suffix}_allylbr", "reactant", "allyl bromide", p, smiles="C=CCBr", amounts=[field("equivalents", qty(allyl_equiv, "equiv"), p)]),
        participant(f"s32_{suffix}_pdcl2", "catalyst", "PdCl2", p, smiles="[Pd+2].[Cl-].[Cl-]", amounts=[field("catalyst_loading", qty(5, "mol%"), p)]),
        participant(f"s32_{suffix}_dma", "solvent", "DMA", p, name="N,N-dimethylacetamide", smiles="CC(=O)N(C)C"),
        participant(f"s32_{suffix}_desired", "product", "allyl-substituted spiro 2,5-dihydrofuran", p),
        participant(f"s32_{suffix}_dimer", "product", "allenol dimerization product", p),
    ]
    records.append(record(f"p07_scheme32_{suffix}", p, "optimization_entry", ps, [
        make_step("competitive_coupling_or_dimerization", [x["entity_id"] for x in ps], p, [
            ("solvent", "DMA", False), ("temperature", "r.t.", False), ("time", qty(time_h, "h"), False),
        ]),
    ], [
        field("yield", desired, p, f"s32_{suffix}_desired"),
        field("yield", dimer, p, f"s32_{suffix}_dimer"),
    ]))

ps = [
    participant("s33_allenol", "reactant", "generic 2,3-allenol", p),
    participant("s33_r2pdi", "reactant", "R2PdI species derived from an organic iodide", p),
    participant("s33_amine", "reactant", "generic amine R3R4NH", p),
    participant("s33_alpha", "product", "alpha-amino homoallylic alcohol", p),
    participant("s33_gamma", "product", "gamma-amino allylic alcohol", p),
]
records.append(record("p07_scheme33_three_component_regioselectivity", p, "mechanism", ps, [
    make_step("carbopalladation", ["s33_allenol", "s33_r2pdi"], p, fill_missing=False),
    make_step("amine_capture_and_regioselective_product_formation", ["s33_amine", "s33_alpha", "s33_gamma"], p, fill_missing=False),
], notes=[("Scheme 33 proposes two regioisomeric pathways and separates regioselectivity control from stereoselectivity control.", p, False)]))

scope34 = [
    ("aryl_chiral", "optically active aryl-substituted 2,3-allenol (98% ee)", None, 70, 42, 57, 98, "R,R alpha-amino homoallylic alcohol"),
    ("perfluoroalkyl", "C8F17-n-substituted 2,3-allenol", 1.5, 77, 36, 87, None, "Z gamma-benzylamino allylic alcohol bearing n-C8F17"),
    ("alkyl_chiral", "(S)-n-C8H17-substituted 2,3-allenol (97% ee)", None, 74, 44, 58, 96, "(S) Z gamma-benzylamino allylic alcohol bearing n-C8H17"),
]
for suffix, allenol, amine_equiv, temp, time_h, yield_pct, ee_pct, product in scope34:
    amounts = [field("equivalents", qty(amine_equiv, "equiv"), p)] if amine_equiv is not None else []
    ps = [
        participant(f"s34_{suffix}_allenol", "reactant", allenol, p),
        participant(f"s34_{suffix}_phi", "reactant", "PhI", p, name="iodobenzene", smiles="Ic1ccccc1"),
        participant(f"s34_{suffix}_bnnh2", "reactant", "BnNH2", p, name="benzylamine", smiles="NCC1=CC=CC=C1", amounts=amounts),
        participant(f"s34_{suffix}_pd", "catalyst", "Pd(PPh3)4", p, amounts=[field("catalyst_loading", qty(5, "mol%"), p)]),
        participant(f"s34_{suffix}_et3n", "solvent", "Et3N", p, name="triethylamine", smiles="CCN(CC)CC"),
        participant(f"s34_{suffix}_product", "product", product, p),
    ]
    outcomes = [field("yield", qty(yield_pct, "%"), p, f"s34_{suffix}_product")]
    if ee_pct is not None:
        outcomes.append(field("ee", qty(ee_pct, "%"), p, f"s34_{suffix}_product"))
    records.append(record(f"p07_scheme34_{suffix}", p, "substrate_scope_entry", ps, [
        make_step("three_component_aminative_coupling", [x["entity_id"] for x in ps], p, [
            ("solvent", "Et3N", False), ("temperature", qty(temp, "°C"), False), ("time", qty(time_h, "h"), False),
        ]),
    ], outcomes, unresolved=["The stereochemical drawings and generic R group in Scheme 34 were retained as labels rather than asserted stereochemical SMILES."]))

ps = [
    participant("s35_intermediate", "reactant", "proposed palladium intermediate 13", p),
    participant("s35_alpha", "product", "alpha-amino homoallylic alcohol pathway", p),
    participant("s35_gamma", "product", "gamma-amino allylic alcohol pathway", p),
]
records.append(record("p07_scheme35_regio_stereocontrol", p, "mechanism", ps, [
    make_step("stereoelectronic_control_path_a", ["s35_intermediate", "s35_alpha"], p, fill_missing=False),
    make_step("steric_control_path_b", ["s35_intermediate", "s35_gamma"], p, fill_missing=False),
], notes=[("The prose assigns alpha-regioselectivity to a stereoelectronic effect and gamma-regioselectivity to steric effects.", p, True)]))

ps = [
    participant("s36_allenylketone", "reactant", "generic 1,2-allenyl ketone", p),
    participant("s36_ag", "catalyst", "Ag+", p),
    participant("s36_rh", "catalyst", "(PPh3)3RhCl", p),
    participant("s36_furan", "product", "substituted furan", p),
]
records.append(record("p07_scheme36_cycloisomerization_prior_work", p, "literature_example", ps, [
    make_step("transition_metal_catalyzed_cycloisomerization", [x["entity_id"] for x in ps], p),
], notes=[("The prose explicitly attributes these cycloisomerizations to Marshall and Hashmi (refs. 30b, 38, and 39).", p, True)]))

for suffix, catalyst, products in [
    ("pdii", "Pd(II)", ["substituted furan", "dimeric furanyl enone"]),
    ("aucl3", "AuCl3", ["substituted furan", "furanyl enone and its further dimerization product"]),
]:
    ps = [participant(f"s37_{suffix}_ketone", "reactant", "terminal 1,2-allenyl ketone", p), participant(f"s37_{suffix}_cat", "catalyst", catalyst, p)]
    for idx, label in enumerate(products, 1):
        ps.append(participant(f"s37_{suffix}_p{idx}", "product", label, p))
    records.append(record(f"p07_scheme37_{suffix}_dimerization_prior_work", p, "literature_example", ps, [
        make_step("catalyzed_cyclization_dimerization", [x["entity_id"] for x in ps], p),
    ], notes=[("The prose presents Scheme 37 as Hashmi's prior AuCl3- or Pd(II)-catalyzed dimeric cyclization work, not as a new experiment in this Account.", p, True)]))

# Page 8: Schemes 38-42.
p = 8
for suffix, additive_label, additive_role, additive_amount, et3n_equiv, temp, y14, y15 in [
    ("et3n", "NEt3", "reagent", qty(1.5, "equiv"), 1.5, 100, 53, 42),
    ("ag2co3", "Ag2CO3", "catalyst", qty(10, "mol%"), 2, 80, 88, 9),
]:
    ps = [
        participant(f"s38_{suffix}_ketone", "reactant", "n-C12H25-substituted 1,2-allenyl methyl ketone", p),
        participant(f"s38_{suffix}_phx", "reactant", "PhX", p),
        participant(f"s38_{suffix}_pd", "catalyst", "Pd(PPh3)4", p, amounts=[field("catalyst_loading", qty(5, "mol%"), p)]),
        participant(f"s38_{suffix}_et3n", "reagent", "NEt3", p, name="triethylamine", smiles="CCN(CC)CC", amounts=[field("equivalents", qty(et3n_equiv, "equiv"), p)]),
        participant(f"s38_{suffix}_toluene", "solvent", "PhMe", p, name="toluene", smiles="Cc1ccccc1"),
        participant(f"s38_{suffix}_p14", "product", "coupling-cyclization furan 14", p),
        participant(f"s38_{suffix}_p15", "product", "cycloisomerization furan 15", p),
    ]
    if suffix == "ag2co3":
        ps.insert(4, participant(f"s38_{suffix}_ag", additive_role, additive_label, p, smiles="[Ag+].[Ag+].[O-]C([O-])=O", amounts=[field("catalyst_loading", additive_amount, p)]))
    records.append(record(f"p08_scheme38_{suffix}", p, "optimization_entry", ps, [
        make_step("competitive_coupling_cyclization", [x["entity_id"] for x in ps], p, [
            ("solvent", "PhMe", False), ("temperature", qty(temp, "°C"), False), ("time", qty(12, "h"), False),
        ]),
    ], [field("yield", qty(y14, "%"), p, f"s38_{suffix}_p14"), field("yield", qty(y15, "%"), p, f"s38_{suffix}_p15")]))

for suffix, aryl_label, aryl_smiles, yield_pct in [
    ("r_h", "iodobenzene (R=H)", "Ic1ccccc1", 74),
    ("r_co2me", "methyl 4-iodobenzoate (R=CO2Me)", "COC(=O)c1ccc(I)cc1", 68),
]:
    ps = [
        participant(f"s39_{suffix}_ketone", "reactant", "C7H15/t-Bu-substituted 1,2-allenyl ketone 16", p),
        participant(f"s39_{suffix}_aryl", "reactant", aryl_label, p, smiles=aryl_smiles),
        participant(f"s39_{suffix}_pd", "catalyst", "Pd(PPh3)4", p, amounts=[field("catalyst_loading", qty(5, "mol%"), p)]),
        participant(f"s39_{suffix}_ag", "catalyst", "Ag2CO3", p, smiles="[Ag+].[Ag+].[O-]C([O-])=O", amounts=[field("catalyst_loading", qty(10, "mol%"), p)]),
        participant(f"s39_{suffix}_et3n", "reagent", "Et3N", p, smiles="CCN(CC)CC"),
        participant(f"s39_{suffix}_tol", "solvent", "toluene", p, smiles="Cc1ccccc1"),
        participant(f"s39_{suffix}_product", "product", f"polysubstituted furan 17 ({aryl_label})", p),
    ]
    records.append(record(f"p08_scheme39_{suffix}", p, "substrate_scope_entry", ps, [
        make_step("pd_ag_coupling_cyclization", [x["entity_id"] for x in ps], p, [
            ("solvent", "toluene", False), ("temperature", qty(80, "°C"), False), ("time", qty(18, "h"), False),
        ]),
    ], [field("yield", qty(yield_pct, "%"), p, f"s39_{suffix}_product")]))

ps = [
    participant("s40_ketone", "reactant", "generic 1,2-allenyl ketone", p),
    participant("s40_allylbr", "reactant", "allyl bromide", p, smiles="C=CCBr"),
    participant("s40_pd", "catalyst", "Pd catalyst", p),
    participant("s40_furan", "product", "3-allyl polysubstituted furan", p),
]
records.append(record("p08_scheme40_allyl_furan_general", p, "general_scheme", ps, [
    make_step("pd_catalyzed_allylic_coupling_cyclization", [x["entity_id"] for x in ps], p),
], [field("yield", rng(50, 79, "%", "50-79%"), p, "s40_furan")]))

ps = [
    participant("s41_ketone", "reactant", "3-methyl-1,2-pentadien-4-one", p, smiles="C=C=C(C)C(C)=O"),
    participant("s41_bromide", "reactant", "3-phenyl-2(E)-propenyl bromide", p, smiles="BrC/C=C/c1ccccc1"),
    participant("s41_pd", "catalyst", "PdCl2(PhCN)2", p, amounts=[field("catalyst_loading", qty(5, "mol%"), p)]),
    participant("s41_k2co3", "reagent", "K2CO3", p, smiles="[K+].[K+].[O-]C([O-])=O", amounts=[field("equivalents", qty(1, "equiv"), p)]),
    participant("s41_mecn", "solvent", "CH3CN", p, smiles="CC#N"),
    participant("s41_linear", "product", "2,3-dimethyl-4-(3-phenyl-2(E)-propenyl)furan", p),
    participant("s41_branched", "product", "2,3-dimethyl-4-(1-phenyl-2-propenyl)furan", p),
]
records.append(record("p08_scheme41_cinnamyl_bromide_linear_product", p, "reported_experiment", ps, [
    make_step("pd_catalyzed_allylic_coupling_cyclization", [x["entity_id"] for x in ps], p, [
        ("solvent", "CH3CN", False), ("temperature", qty(25, "°C"), False), ("time", qty(20, "h"), False),
    ]),
], [
    field("yield", qty(50, "%"), p, "s41_linear"),
    field("formation", "not formed", p, "s41_branched"),
], notes=[("The branched allylic regioisomer is explicitly drawn and labeled 'not formed'.", p, False)]))

ps = [
    participant("s42_acid", "reactant", "generic 2,3-allenoic acid", p),
    participant("s42_ketone", "reactant", "generic 1,2-allenyl ketone", p),
    participant("s42_pd", "catalyst", "PdCl2(MeCN)2", p, amounts=[field("catalyst_loading", qty(5, "mol%"), p)]),
    participant("s42_mecn", "solvent", "CH3CN", p, smiles="CC#N"),
    participant("s42_product", "product", "dumbbell-type bicyclic compound 19", p),
]
records.append(record("p08_scheme42_biallene_bicyclization_general", p, "general_scheme", ps, [
    make_step("pdii_oxidative_bicyclization", [x["entity_id"] for x in ps], p, [
        ("solvent", "CH3CN", False), ("temperature", "r.t.", False), ("time", qty(4, "h"), False),
    ]),
], [field("yield", rng(69, 92, "%", "69-92%"), p, "s42_product")]))

# Page 9: Schemes 43-47.
p = 9
ps = [
    participant("s43_acid", "reactant", "generic 2,3-allenoic acid", p),
    participant("s43_ketone", "reactant", "1,2-allenyl methyl ketone", p, amounts=[field("equivalents", qty(2, "equiv"), p)]),
    participant("s43_pdcl2", "catalyst", "LnPdCl2", p),
    participant("s43_product", "product", "dumbbell-type bicyclic product 19", p),
    participant("s43_diketones", "product", "1,6-diketone isomers 21, 22, and 23", p),
]
records.append(record("p09_scheme43_biallene_catalytic_cycle", p, "mechanism", ps, [
    make_step("formation_of_intermediate_20_and_product_19", ["s43_acid", "s43_ketone", "s43_pdcl2", "s43_product"], p, fill_missing=False),
    make_step("cyclometalation_and_pdii_regeneration", ["s43_ketone", "s43_pdcl2"], p, fill_missing=False),
    make_step("protonolysis_to_diketones", ["s43_diketones"], p, fill_missing=False),
], notes=[("Scheme 43 proposes a catalytic cycle involving two equivalents of allenyl ketone and in-situ HCl; the prose says diketones 21-23 were isolated after protonolysis of intermediate 24.", p, True)]))

for suffix, nbu, time_h, yield_pct in [
    ("without_tbab", False, 19.5, 32),
    ("with_tbab", True, 15, 80),
]:
    ps = [
        participant(f"s44_{suffix}_malonate", "reactant", "dimethyl 2-(2,3-butadienyl)malonate 25a", p),
        participant(f"s44_{suffix}_phi", "reactant", "PhI", p, smiles="Ic1ccccc1"),
        participant(f"s44_{suffix}_pd", "catalyst", "Pd(PPh3)4", p, amounts=[field("catalyst_loading", qty(5, "mol%"), p)]),
        participant(f"s44_{suffix}_k2co3", "reagent", "K2CO3", p, smiles="[K+].[K+].[O-]C([O-])=O", amounts=[field("equivalents", qty(4, "equiv"), p)]),
        participant(f"s44_{suffix}_mecn", "solvent", "CH3CN", p, smiles="CC#N"),
        participant(f"s44_{suffix}_product", "product", "vinylic cyclopropane 26a", p),
    ]
    if nbu:
        ps.insert(4, participant(f"s44_{suffix}_tbab", "reagent", "n-Bu4NBr", p, amounts=[field("loading", qty(10, "mol%"), p)]))
    records.append(record(f"p09_scheme44_{suffix}", p, "optimization_entry", ps, [
        make_step("pd_coupling_cyclization", [x["entity_id"] for x in ps], p, [
            ("solvent", "CH3CN", False), ("temperature", "reflux", False), ("time", qty(time_h, "h"), False),
        ]),
    ], [field("yield", qty(yield_pct, "%"), p, f"s44_{suffix}_product")], unresolved=[] if not nbu else ["The 10 mol% n-Bu4NBr loading is shown in Conditions A on the same page and is associated with the Scheme 44 promoted condition by the article's discussion. "]))

ps = [
    participant("s45_malonate", "reactant", "generic 2-(2,3-allenyl)malonate", p),
    participant("s45_rpdx", "reactant", "RPdX", p),
    participant("s45_cyclopropane", "product", "vinylic cyclopropane pathway a", p),
    participant("s45_cyclopentene", "product", "cyclopentene pathway b", p),
]
records.append(record("p09_scheme45_regioselectivity_paths", p, "mechanism", ps, [
    make_step("carbopalladation_and_base_activation", ["s45_malonate", "s45_rpdx"], p, fill_missing=False),
    make_step("path_a_or_b_ring_closure", ["s45_cyclopropane", "s45_cyclopentene"], p, fill_missing=False),
]))

def malonate_base(prefix, page, *, substrate="dimethyl 2-(2-benzyl-2,3-butadienyl)malonate 25b", halide="PhI", halide_smiles="Ic1ccccc1"):
    return [
        participant(f"{prefix}_malonate", "reactant", substrate, page),
        participant(f"{prefix}_halide", "reactant", halide, page, smiles=halide_smiles),
    ]


# Scheme 46 Conditions A is repeated qualitatively in Scheme 49 on page 10; keep one record with both pages as evidence.
ps = malonate_base("s46a", p) + [
    participant("s46a_pd", "catalyst", "Pd(PPh3)4", p, amounts=[field("catalyst_loading", qty(5, "mol%"), p)]),
    participant("s46a_k2co3", "reagent", "K2CO3", p, smiles="[K+].[K+].[O-]C([O-])=O", amounts=[field("equivalents", qty(4, "equiv"), p)]),
    participant("s46a_tbab", "reagent", "n-Bu4NBr", p, amounts=[field("loading", qty(10, "mol%"), p)]),
    participant("s46a_mecn", "solvent", "CH3CN", p, smiles="CC#N"),
    participant("s46a_26b", "product", "vinylic cyclopropane 26b", p),
    participant("s46a_27b", "product", "cyclopentene 27b", p),
]
records.append(record("p09_scheme46_conditions_a", p, "optimization_entry", ps, [
    make_step("conditions_a_coupling_cyclization", [x["entity_id"] for x in ps], p, [
        ("solvent", "CH3CN", False), ("temperature", "reflux", False), ("time", qty(15, "h"), False),
    ]),
], [
    field("yield", qty(80, "%"), p, "s46a_26b"),
    field("yield", rng(2, 3, "%", "2-3%"), p, "s46a_27b"),
], notes=[("Scheme 49 repeats this PhI/Conditions A experiment and labels 27b qualitatively as trace; Scheme 46 provides the more specific 2-3% value.", 10, False)], extra_pages=[10]))

ps = malonate_base("s46b", p) + [
    participant("s46b_pd", "catalyst", "Pd(PPh3)4", p, amounts=[field("catalyst_loading", qty(5, "mol%"), p)]),
    participant("s46b_k2co3", "reagent", "K2CO3", p, smiles="[K+].[K+].[O-]C([O-])=O", amounts=[field("equivalents", qty(4, "equiv"), p)]),
    participant("s46b_thf", "solvent", "THF", p, smiles="C1CCOC1"),
    participant("s46b_26b", "product", "vinylic cyclopropane 26b", p),
    participant("s46b_27b", "product", "cyclopentene 27b", p),
]
records.append(record("p09_scheme46_conditions_b", p, "optimization_entry", ps, [
    make_step("conditions_b_coupling_cyclization", [x["entity_id"] for x in ps], p, [
        ("solvent", "THF", False), ("temperature", "reflux", False), ("time", qty(24, "h"), False),
    ]),
], [field("yield", "trace amount of products", p, ["s46b_26b", "s46b_27b"])], unresolved=["Scheme 46 does not assign the trace product amount separately to 26b and 27b."]))

scheme47 = [
    ("pd2dba3_k2co3", "Pd2(dba)3·CHCl3", 2, "dppe", 4, "K2CO3", qty(4, "equiv"), True, 24, 49, 13),
    ("pd2dba3_nah", "Pd2(dba)3·CHCl3", 2, "dppe", 4, "NaH", qty(1.1, "equiv"), False, 12.5, 14, 58),
    ("conditions_c", "Pd(PPh3)4", 5, None, None, "NaH", qty(1.1, "equiv"), False, 12, 0, 88),
]
for suffix, catalyst, cat_load, ligand, ligand_load, base_label, base_amt, tbab, time_h, y26, y27 in scheme47:
    ps = malonate_base(f"s47_{suffix}", p) + [
        participant(f"s47_{suffix}_pd", "catalyst", catalyst, p, amounts=[field("catalyst_loading", qty(cat_load, "mol%"), p)]),
        participant(f"s47_{suffix}_base", "reagent", base_label, p, smiles={"K2CO3": "[K+].[K+].[O-]C([O-])=O", "NaH": "[Na+].[H-]"}[base_label], amounts=[field("equivalents", base_amt, p)]),
        participant(f"s47_{suffix}_dmso", "solvent", "DMSO", p, smiles="CS(C)=O"),
        participant(f"s47_{suffix}_26b", "product", "vinylic cyclopropane 26b", p),
        participant(f"s47_{suffix}_27b", "product", "cyclopentene 27b", p),
    ]
    if ligand:
        ps.insert(3, participant(f"s47_{suffix}_ligand", "reagent", ligand, p, amounts=[field("loading", qty(ligand_load, "mol%"), p)]))
    if tbab:
        ps.insert(4, participant(f"s47_{suffix}_tbab", "reagent", "n-Bu4NBr", p, amounts=[field("loading", qty(10, "mol%"), p)]))
    extra = [10] if suffix == "conditions_c" else []
    notes = [("Scheme 51 repeats the simultaneous Conditions C experiment as an 88% cyclopentene result.", 10, False)] if extra else []
    unresolved = []
    if suffix == "conditions_c":
        unresolved = ["Scheme 51 labels the repeated substrate/product as 25a/3b although the benzyl-substituted drawings and surrounding prose correspond to the 25b/27b comparison; the label discrepancy is preserved."]
    records.append(record(f"p09_scheme47_{suffix}", p, "optimization_entry", ps, [
        make_step("regioselective_coupling_cyclization", [x["entity_id"] for x in ps], p, [
            ("solvent", "DMSO", False), ("temperature", qty(85, "°C"), False), ("time", qty(time_h, "h"), False),
        ]),
    ], [field("yield", qty(y26, "%"), p, f"s47_{suffix}_26b"), field("yield", qty(y27, "%"), p, f"s47_{suffix}_27b")], notes=notes, unresolved=unresolved, extra_pages=extra))

# Page 10: Scheme 48 table, Scheme 49 ortho-tolyl entry, Scheme 50 mechanism, Scheme 51 sequential experiment.
p = 10
entries48 = [
    ("entry1_d", "H", "p-MeC6H4", "conditions D", "NaOH", 2.0, "DMF", None, 0, 63),
    ("entry2_d", "H", "p-MeOC6H4", "conditions D", "NaOH", 2.0, "DMF", None, 0, 57),
    ("entry3_d", "n-Pr", "p-MeOC6H4", "conditions D", "NaOH", 2.0, "DMF", None, 0, 51),
    ("entry3_c", "n-Pr", "p-MeOC6H4", "conditions C", "NaH", 1.1, "DMSO", 12, 7, 47),
    ("entry4_d_nah", "n-Pr", "p-MeOC6H4", "conditions D with footnote a", "NaH", 1.1, "DMF", None, 0, 70),
    ("entry5_d", "n-Pr", "p-MeO2CC6H4", "conditions D", "NaOH", 2.0, "DMF", None, 0, 52),
    ("entry5_c", "n-Pr", "p-MeO2CC6H4", "conditions C", "NaH", 1.1, "DMSO", 12, 8, 54),
]
for suffix, r1, r2, condition_label, base_label, base_equiv, solvent, time_h, y26, y27 in entries48:
    r2_smiles = {"p-MeC6H4": "Cc1ccc(I)cc1", "p-MeOC6H4": "COc1ccc(I)cc1", "p-MeO2CC6H4": "COC(=O)c1ccc(I)cc1"}[r2]
    ps = [
        participant(f"s48_{suffix}_malonate", "reactant", f"2-(2,3-butadienyl)malonate substrate (R1={r1})", p),
        participant(f"s48_{suffix}_iodide", "reactant", f"aryl iodide R2={r2}", p, smiles=r2_smiles),
        participant(f"s48_{suffix}_pd", "catalyst", "Pd(PPh3)4", p, amounts=[field("catalyst_loading", qty(5, "mol%"), p)]),
        participant(f"s48_{suffix}_base", "reagent", base_label, p, smiles={"NaOH": "[Na+].[OH-]", "NaH": "[Na+].[H-]"}[base_label], amounts=[field("equivalents", qty(base_equiv, "equiv"), p)]),
        participant(f"s48_{suffix}_solvent", "solvent", solvent, p, smiles={"DMF": "CN(C)C=O", "DMSO": "CS(C)=O"}[solvent]),
        participant(f"s48_{suffix}_26", "product", f"vinylic cyclopropane 26 ({r1}, {r2})", p),
        participant(f"s48_{suffix}_27", "product", f"cyclopentene 27 ({r1}, {r2})", p),
    ]
    conditions = [("solvent", solvent, False), ("temperature", qty(85, "°C"), False)]
    if time_h is not None:
        conditions.append(("time", qty(time_h, "h"), False))
    records.append(record(f"p10_scheme48_{suffix}", p, "substrate_scope_entry", ps, [
        make_step("regioselective_coupling_cyclization", [x["entity_id"] for x in ps], p, conditions),
    ], [field("yield", qty(y26, "%"), p, f"s48_{suffix}_26"), field("yield", qty(y27, "%"), p, f"s48_{suffix}_27")], notes=[(f"Scheme 48 reports this row under {condition_label}.", p, False)], unresolved=[] if time_h is not None else ["Scheme 48 does not state a reaction time for Conditions D on this page."]))

ps = malonate_base("s49_ortho", p, halide="o-methylphenyl iodide", halide_smiles="Cc1ccccc1I") + [
    participant("s49_ortho_pd", "catalyst", "Pd(PPh3)4", p, amounts=[field("catalyst_loading", qty(5, "mol%"), p)]),
    participant("s49_ortho_k2co3", "reagent", "K2CO3", p, smiles="[K+].[K+].[O-]C([O-])=O", amounts=[field("equivalents", qty(4, "equiv"), p)]),
    participant("s49_ortho_tbab", "reagent", "n-Bu4NBr", p, amounts=[field("loading", qty(10, "mol%"), p)]),
    participant("s49_ortho_mecn", "solvent", "CH3CN", p, smiles="CC#N"),
    participant("s49_ortho_27c", "product", "o-tolyl cyclopentene 27c", p),
]
records.append(record("p10_scheme49_o_tolyl_conditions_a", p, "substrate_scope_entry", ps, [
    make_step("conditions_a_coupling_cyclization", [x["entity_id"] for x in ps], p, [
        ("solvent", "CH3CN", False), ("temperature", "reflux", False), ("time", qty(3.5, "d"), False),
    ]),
], [field("yield", qty(80, "%"), p, "s49_ortho_27c")], notes=[("The prose states that 27c was formed exclusively when o-methylphenyl iodide replaced PhI.", p, True)]))

ps = [
    participant("s50_syn", "reactant", "syn-pi-allylpalladium intermediate 28", p),
    participant("s50_anti", "reactant", "anti-pi-allylpalladium intermediate 28", p),
    participant("s50_26", "product", "vinylic cyclopropane 26", p),
    participant("s50_27", "product", "cyclopentene 27", p),
]
records.append(record("p10_scheme50_syn_anti_regioselectivity", p, "mechanism", ps, [
    make_step("syn_intermediate_to_cyclopropane", ["s50_syn", "s50_26"], p, fill_missing=False),
    make_step("anti_intermediate_to_cyclopentene", ["s50_anti", "s50_27"], p, fill_missing=False),
], notes=[("The prose proposes syn-28 for cyclopropane formation and anti-28 for cyclopentene formation.", p, True)]))

ps = malonate_base("s51_seq", p) + [
    participant("s51_seq_pd", "catalyst", "Pd(PPh3)4", p, amounts=[field("catalyst_loading", qty(20, "mol%"), p)]),
    participant("s51_seq_dmso", "solvent", "DMSO", p, smiles="CS(C)=O"),
    participant("s51_seq_nah", "reagent", "NaH", p, smiles="[Na+].[H-]", amounts=[field("equivalents", qty(1.1, "equiv"), p)]),
    participant("s51_seq_product", "product", "vinylic cyclopropane 26b", p),
]
records.append(record("p10_scheme51_sequential_pd_then_nah", p, "reported_experiment", ps, [
    make_step("preincubate_with_pd", ["s51_seq_malonate", "s51_seq_halide", "s51_seq_pd", "s51_seq_dmso"], p, [
        ("solvent", "DMSO", False), ("temperature", qty(85, "°C"), False), ("time", qty(6, "h"), False),
    ]),
    make_step("add_nah_and_cyclize", ["s51_seq_nah", "s51_seq_product"], p, [
        ("temperature", qty(85, "°C"), False), ("time", qty(4.5, "h"), False),
    ]),
], [field("yield", qty(29, "%"), p, "s51_seq_product")], notes=[("The article contrasts this sequential addition experiment with simultaneous Conditions C, which is already represented by p09_scheme47_conditions_c.", p, True)]))


def ids(prefix):
    return [rec["record_id"] for rec in records if rec["record_id"].startswith(f"{DOC}:{prefix}")]


page7_ids = ids("p07_")
page8_ids = ids("p08_")
page9_ids = ids("p09_")
page10_unique = ids("p10_")
page10_ids = [f"{DOC}:p09_scheme46_conditions_a", f"{DOC}:p09_scheme47_conditions_c"] + page10_unique

coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 7,
            "state": "attempted",
            "regions": [
                {"region": "upper-left Schemes 30-32", "finding": "Product-path overview, a 76% PdCl2/allyl-bromide example with its proposed Pd(II) cycle, and three separate allyl-bromide-equivalent optimization rows were inventoried.", "evidence_ids": [I[7], T[7]]},
                {"region": "lower-left Scheme 33", "finding": "Three-component aminative coupling regioselectivity/stereoselectivity proposal classified as mechanism.", "evidence_ids": [I[7], T[7]]},
                {"region": "upper-right Schemes 34-35", "finding": "Three quantified amino-alcohol scope examples were split; the adjacent selectivity rationale was classified as mechanism.", "evidence_ids": [I[7], T[7]]},
                {"region": "lower-right Schemes 36-37", "finding": "Ag/Rh cycloisomerization and Pd(II)/AuCl3 dimerizations are explicitly cited prior work and were not represented as new experiments.", "evidence_ids": [I[7], T[7]]},
            ],
            "record_ids": page7_ids,
            "unresolved": ["Scheme 31 omits catalyst loading and operational details.", "Several Scheme 34 stereochemical structures contain generic groups and therefore retain null SMILES.", "Schemes 36-37 give no yields or full conditions in this Account."],
        },
        {
            "page": 8,
            "state": "attempted",
            "regions": [
                {"region": "top Scheme 38", "finding": "Two additive/temperature optimization rows were separated with product-specific yields for coupling product 14 and cycloisomerization product 15.", "evidence_ids": [I[8], T[8]]},
                {"region": "upper-middle Schemes 39-40", "finding": "Two aryl-iodide substrate rows and one generic allyl-bromide coupling scheme were extracted.", "evidence_ids": [I[8], T[8]]},
                {"region": "middle-right Scheme 41", "finding": "Specific cinnamyl-bromide experiment extracted with 50% linear product and the branched regioisomer explicitly not formed.", "evidence_ids": [I[8], T[8]]},
                {"region": "lower-right Scheme 42 and prose", "finding": "General Pd(II) biallene bicyclization and its 69-92% summarized yield range were captured; mechanistic discussion points to Scheme 43 on page 9.", "evidence_ids": [I[8], T[8]]},
            ],
            "record_ids": page8_ids,
            "unresolved": ["Scheme 38 uses generic PhX without identifying X on the page.", "Schemes 40 and 42 summarize generic scopes rather than individual compounds."],
        },
        {
            "page": 9,
            "state": "attempted",
            "regions": [
                {"region": "upper-left Scheme 43", "finding": "Biallene catalytic cycle, in-situ HCl role, two-equivalent allenyl ketone, and protonolysis byproducts were classified as mechanistic evidence.", "evidence_ids": [I[9], T[9]]},
                {"region": "lower-left Scheme 44", "finding": "Without- and with-n-Bu4NBr experiments were kept as separate optimization records.", "evidence_ids": [I[9], T[9]]},
                {"region": "upper-right Schemes 45-46", "finding": "Generic regioselectivity mechanism plus Conditions A and B were inventoried; Conditions A is cross-linked to its repeat in Scheme 49 rather than duplicated.", "evidence_ids": [I[9], T[9]]},
                {"region": "lower-right Scheme 47", "finding": "Three distinct catalyst/base condition rows were split with product-specific 26b/27b yields.", "evidence_ids": [I[9], T[9]]},
            ],
            "record_ids": page9_ids,
            "unresolved": ["The Scheme 44 promoted row does not print the n-Bu4NBr loading beside the arrow; 10 mol% is associated from Conditions A on the same page and retained as an unresolved association.", "No yield measurement basis or workup is supplied."],
        },
        {
            "page": 10,
            "state": "attempted",
            "regions": [
                {"region": "top Scheme 48 table", "finding": "Five Conditions D substrate rows and the two populated Conditions C rows were represented as seven records; footnote a's NaH substitution was structured as a reagent amount.", "evidence_ids": [I[10], T[10]]},
                {"region": "middle Scheme 49", "finding": "The PhI/Conditions A branch repeats Scheme 46 and was merged as cross-page evidence; the o-tolyl iodide branch is a separate 80% scope experiment.", "evidence_ids": [I[10], T[10]]},
                {"region": "lower-left Scheme 50", "finding": "Syn/anti pi-allylpalladium regioselectivity proposal classified as mechanism.", "evidence_ids": [I[10], T[10]]},
                {"region": "lower-right Scheme 51 and adjacent prose", "finding": "Simultaneous Conditions C repeats Scheme 47 and was cross-linked; the sequential 20 mol% Pd then NaH experiment was extracted separately with its two timed stages and 29% yield.", "evidence_ids": [I[10], T[10]]},
            ],
            "record_ids": page10_ids,
            "unresolved": ["Scheme 48 omits reaction times for Conditions D.", "Scheme 51's 25a/3b labels conflict with the benzyl-substituted drawings, Scheme 47 labels, and surrounding prose; no silent correction was made."],
        },
        {
            "page": 11,
            "state": "attempted",
            "regions": [
                {"region": "upper-left conclusion, acknowledgments, and Note Added after ASAP Posting", "finding": "No reaction arrow or new experiment; the note states that Scheme 14 was corrected on 6/25/2003.", "evidence_ids": [I[11], T[11]]},
                {"region": "remaining two-column References 1-19", "finding": "Bibliographic citations only; cited papers were not expanded into experimental records.", "evidence_ids": [I[11], T[11]]},
            ],
            "record_ids": [],
            "unresolved": ["No supporting information is supplied or explicitly associated."],
        },
        {
            "page": 12,
            "state": "attempted",
            "regions": [
                {"region": "full-page References 20-48 and article identifier", "finding": "Bibliographic citations only; no reaction schemes, tables, arrows, or new experimental conditions appear on this page.", "evidence_ids": [I[12], T[12]]},
            ],
            "record_ids": [],
            "unresolved": ["Reference titles summarize cited chemistry but are not treated as experiments in the source Account."],
        },
    ],
}


RAW.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
COVERAGE.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

if TASKS.exists():
    tasks = json.loads(TASKS.read_text())
    wanted = {T[p] for p in range(7, 13)}
    for task in tasks:
        if task.get("task_id") in wanted:
            page = int(task["task_id"].split("page")[1].split(":")[0])
            task["state"] = "attempted"
            task["visual_evidence_id"] = I[page]
            task["reason"] = "Original page image and extracted page text inspected; findings, record links, and unresolved issues are recorded in coverage/pages_0007_0012.json."
    TASKS.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"records": len(records), "raw": str(RAW), "coverage": str(COVERAGE)}, ensure_ascii=False))
