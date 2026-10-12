#!/usr/bin/env python3
"""Build evidence-linked machine records for ar020133k PDF pages 1-6."""
from __future__ import annotations

import json
from pathlib import Path


DOC = "doc_e26f259781f314bb"
ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "raw_model" / "extracted_records_pages_0001_0006.json"
COVERAGE = ROOT / "coverage" / "pages_0001_0006.json"
TASKS = ROOT / "tasks.json"
I = {p: f"{DOC}:page{p}:image" for p in range(1, 7)}
T = {p: f"{DOC}:page{p}:text" for p in range(1, 7)}


def fact(value, page=None, text=False):
    if value is None:
        return {"value": None, "evidence_ids": [], "verification": "missing"}
    evidence = [] if page is None else [T[page] if text else I[page]]
    return {"value": value, "evidence_ids": evidence, "verification": "unreviewed"}


def field(name, value, page, target=None, text=False):
    result = {"name": name, "fact": fact(value, page if value is not None else None, text=text)}
    if target:
        result["target_entity_ids"] = [target] if isinstance(target, str) else list(target)
    return result


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


def make_step(step_id, ids, page, conditions=(), *, fill_missing=True):
    conditions = [field(name, value, page, text=text) for name, value, text in conditions]
    names = {item["name"] for item in conditions}
    if fill_missing and "temperature" not in names:
        conditions.append(field("temperature", None, page))
    if fill_missing and "time" not in names:
        conditions.append(field("time", None, page))
    return {"step_id": step_id, "participant_ids": list(ids), "conditions": conditions}


def record(suffix, page, kind, participants, steps, outcomes=(), *, notes=(), unresolved=(), extra_pages=()):
    outcomes = list(outcomes)
    if kind != "mechanism" and not any(item["name"] == "yield" for item in outcomes):
        outcomes.append(field("yield", None, page))
    evidence = [I[page], T[page]]
    for other in extra_pages:
        evidence.extend([I[other], T[other]])
    evidence = list(dict.fromkeys(evidence))
    standard_unresolved = [
        "The Account does not provide a complete experimental procedure, workup, purification, or atmosphere for this record.",
        "No supporting-information file was supplied or explicitly associated; missing details remain missing.",
    ]
    if kind == "mechanism":
        standard_unresolved = ["This is a proposed mechanistic diagram, not a reported preparative experiment."]
    elif kind in {"general_scheme", "literature_example"}:
        standard_unresolved.append("Generic R-group structures and/or summarized yield ranges are not individual fully specified compounds.")
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
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": standard_unresolved + list(unresolved),
        },
    }


def qty(number, unit, raw_text=None, **extra):
    value = {"number": number, "unit": unit}
    if raw_text:
        value["raw_text"] = raw_text
    value.update(extra)
    return value


def rng(minimum, maximum, unit, raw_text):
    return {"minimum": minimum, "maximum": maximum, "unit": unit, "raw_text": raw_text}


records = []

# Page 1: conceptual overview and the proposed carbopalladation/cyclization pathway.
p = 1
ps = [
    participant("s1_start", "reactant", "Starting materials", p),
    participant("s1_allene", "product", "substituted allene / cumulated C-C bonds", p),
    participant("s1_optical", "product", "optically active products", p),
]
records.append(record("p01_scheme01_allene_design", p, "general_scheme", ps, [
    make_step("establish_allene", ["s1_start", "s1_allene"], p, fill_missing=False),
    make_step("control_reactivity_regioselectivity_chirality", ["s1_allene", "s1_optical"], p, fill_missing=False),
], notes=[("Scheme 1 is a conceptual design overview and reports no concrete experiment.", p, False)]))

ps = [
    participant("s2_acid", "reactant", "generic 2,3-allenoic acid", p),
    participant("s2_halide", "reactant", "R2X", p),
    participant("s2_pd0", "catalyst", "Pd(0)", p),
    participant("s2_product", "product", "generic butenolide", p),
]
records.append(record("p01_scheme02_carbopalladation_mechanism", p, "mechanism", ps, [
    make_step("oxidative_addition_and_carbopalladation", ["s2_acid", "s2_halide", "s2_pd0"], p, fill_missing=False),
    make_step("intramolecular_c_o_bond_formation", ["s2_product"], p, fill_missing=False),
], notes=[("Scheme 2 proposes carbopalladation followed by intramolecular C-O bond formation.", p, False)]))

# Page 2: Schemes 3-9.
p = 2
ps = [
    participant("s3_acid", "reactant", "generic 2,3-allenoic acid", p),
    participant("s3_halide", "reactant", "R2X", p),
    participant("s3_pd", "catalyst", "Pd(PPh3)4 (catalytic)", p),
    participant("s3_ag", "catalyst", "Ag2CO3 (catalytic)", p, smiles="[Ag+].[Ag+].[O-]C([O-])=O"),
    participant("s3_k2co3", "reagent", "K2CO3", p, smiles="[K+].[K+].[O-]C([O-])=O"),
    participant("s3_mecn", "solvent", "MeCN", p, name="acetonitrile", smiles="CC#N"),
    participant("s3_product", "product", "butenolide 3", p),
]
records.append(record("p02_scheme03_pd_ag_coupling_cyclization", p, "general_scheme", ps, [
    make_step("coupling_cyclization", [x["entity_id"] for x in ps], p, [
        ("solvent", "MeCN", False), ("temperature", qty(70, "°C"), False),
    ]),
], [field("yield", rng(59, 79, "%", "59-79%"), p, "s3_product")]))

ps = [
    participant("s4_resin_iodide", "reactant", "polymer-supported aryl iodide", p),
    participant("s4_acid", "reactant", "generic 2,3-allenoic acid", p),
    participant("s4_resin_product", "product", "polymer-supported butenolide", p),
    participant("s4_product", "product", "cleaved aryl-substituted butenolide", p),
]
records.append(record("p02_scheme04_solid_phase_butenolides", p, "general_scheme", ps, [
    make_step("solid_phase_coupling_cyclization", ["s4_resin_iodide", "s4_acid", "s4_resin_product"], p),
    make_step("cleavage", ["s4_resin_product", "s4_product"], p),
], [
    field("yield", rng(22, 100, "%", "22-100%"), p, "s4_product"),
    field("purity", rng(51, 98, "%", "51-98%"), p, "s4_product"),
]))

for suffix, linker, reagents in [
    ("carboxyl", "carboxyl-linked polymer-supported butenolide", [("AlCl3", None)]),
    ("ether", "ether-linked polymer-supported butenolide", [("ZnBr2", None), ("CH3COBr", "CC(=O)Br")]),
    ("thp", "THP-linked polymer-supported butenolide", [("TFA", "O=C(O)C(F)(F)F"), ("MeOH", "CO")]),
]:
    ps = [participant(f"s5_{suffix}_bound", "reactant", linker, p)]
    for idx, (label, smiles) in enumerate(reagents, 1):
        role = "solvent" if label == "MeOH" else "reagent"
        ps.append(participant(f"s5_{suffix}_r{idx}", role, label, p, smiles=smiles))
    ps.append(participant(f"s5_{suffix}_product", "product", f"cleaved butenolide ({suffix} linker protocol)", p))
    records.append(record(f"p02_scheme05_{suffix}_linker_cleavage", p, "general_scheme", ps, [
        make_step("linker_cleavage", [x["entity_id"] for x in ps], p),
    ], notes=[(f"The prose assigns this reagent set specifically to cleavage of the {suffix} linkage.", p, True)]))

ps = [
    participant("s6_halo", "reactant", "generic beta-halobutenolide", p),
    participant("s6_rm", "reactant", "R2M organometallic reagent", p),
    participant("s6_product", "product", "beta-substituted butenolide", p),
]
records.append(record("p02_scheme06_coupling_concept", p, "general_scheme", ps, [
    make_step("coupling_reaction", [x["entity_id"] for x in ps], p),
], notes=[("Scheme 6 is a retrosynthetic/general coupling concept; concrete conditions appear in Scheme 8.", p, False)]))

ps = [
    participant("s7i_acid", "reactant", "generic 2,3-allenoic acid", p),
    participant("s7i_i2", "reagent", "I2", p, smiles="II"),
    participant("s7i_thf", "solvent", "THF", p, smiles="C1CCOC1"),
    participant("s7i_k2co3", "reagent", "K2CO3", p, smiles="[K+].[K+].[O-]C([O-])=O"),
    participant("s7i_product", "product", "iodobutenolide", p),
]
records.append(record("p02_scheme07_iodolactonization", p, "general_scheme", ps, [
    make_step("iodination", ["s7i_acid", "s7i_i2", "s7i_thf"], p, [
        ("solvent", "THF", False), ("temperature", qty(0, "°C"), False), ("time", qty(1, "h"), False),
    ]),
    make_step("base_promoted_cyclization", ["s7i_k2co3", "s7i_product"], p, [
        ("time", qty(10, "h"), False),
    ]),
], [field("yield", {"number": 90, "unit": "%", "qualifier": "gt", "raw_text": ">90%"}, p, "s7i_product")]))

ps = [
    participant("s7b_acid", "reactant", "generic 2,3-allenoic acid", p),
    participant("s7b_nbs", "reagent", "NBS", p, name="N-bromosuccinimide", smiles="O=C1CCC(=O)N1Br"),
    participant("s7b_k2co3", "reagent", "K2CO3", p, smiles="[K+].[K+].[O-]C([O-])=O", amounts=[field("equivalents", qty(1, "equiv"), p)]),
    participant("s7b_water", "solvent", "H2O", p, smiles="O"),
    participant("s7b_product", "product", "bromobutenolide", p),
]
records.append(record("p02_scheme07_bromolactonization", p, "general_scheme", ps, [
    make_step("bromolactonization", [x["entity_id"] for x in ps], p, [
        ("solvent", "H2O", False), ("temperature", "r.t.", False), ("time", qty(6, "h"), False),
    ]),
], [field("yield", {"number": 80, "unit": "%", "qualifier": "gt", "raw_text": ">80%"}, p, "s7b_product")]))

ps = [
    participant("s8a_halo", "reactant", "generic beta-halobutenolide", p),
    participant("s8a_alkyne", "reactant", "terminal alkyne R'-CCH", p),
    participant("s8a_pd", "catalyst", "PdCl2(PPh3)2", p),
    participant("s8a_cui", "catalyst", "CuI", p, smiles="[Cu]I"),
    participant("s8a_product", "product", "beta-alkynyl butenolide", p),
]
records.append(record("p02_scheme08_alkynyl_coupling", p, "general_scheme", ps, [
    make_step("sonogashira_type_coupling", [x["entity_id"] for x in ps], p, [("temperature", "r.t.", False)]),
], [field("yield", rng(65, 99, "%", "65-99%"), p, "s8a_product")], notes=[("Reported terminal-alkyne classes are R'=TMS, CH2OH, alkyl, or phenyl.", p, False)]))

ps = [
    participant("s8b_halo", "reactant", "generic beta-halobutenolide", p),
    participant("s8b_organo", "reactant", "R''ZnBr or R''B(OH)2", p),
    participant("s8b_pd", "catalyst", "Pd(PPh3)4 (catalytic)", p),
    participant("s8b_solvent", "solvent", "THF/DMF", p),
    participant("s8b_product", "product", "beta-substituted butenolide", p),
]
records.append(record("p02_scheme08_organozinc_or_boronic_coupling", p, "general_scheme", ps, [
    make_step("cross_coupling", [x["entity_id"] for x in ps], p, [
        ("solvent", "THF/DMF", False), ("temperature", "r.t.", False),
    ]),
], [field("yield", rng(70, 99, "%", "70-99%"), p, "s8b_product")], notes=[("Reported R'' classes are aryl, 1-alkenyl, or alkyl.", p, False)]))

acid_smiles = "CC(=C=Cc1ccccc1)C(=O)O"
for suffix, x, reagent_smiles, time_h, yield_pct, lix, lix_smiles, added_yield in [
    ("cl", "Cl", "[Cu+2].[Cl-].[Cl-]", 24, 83, None, None, None),
    ("cl_licl", "Cl", "[Cu+2].[Cl-].[Cl-]", 24, 92, "LiCl", "[Li+].[Cl-]", 4),
    ("br", "Br", "[Cu+2].[Br-].[Br-]", 12, 70, None, None, None),
    ("br_libr", "Br", "[Cu+2].[Br-].[Br-]", 12, 84, "LiBr", "[Li+].[Br-]", 4),
]:
    product_smiles = f"CC1=C({x})C(c2ccccc2)OC1=O"
    ps = [
        participant(f"s9_{suffix}_acid", "reactant", "allenoic acid 1a", p, name="2-methyl-4-phenyl-2,3-butadienoic acid", smiles=acid_smiles),
        participant(f"s9_{suffix}_cu", "reagent", f"Cu{x}2", p, smiles=reagent_smiles),
        participant(f"s9_{suffix}_mecn", "solvent", "CH3CN", p, name="acetonitrile", smiles="CC#N"),
    ]
    if lix:
        ps.append(participant(f"s9_{suffix}_li", "reagent", lix, p, smiles=lix_smiles, amounts=[field("equivalents", qty(added_yield, "equiv"), p)]))
    target = f"s9_{suffix}_product"
    ps.append(participant(target, "product", f"halobutenolide 2a (X={x})", p, smiles=product_smiles))
    records.append(record(f"p02_scheme09_{suffix}", p, "optimization_entry", ps, [
        make_step("halolactonization", [x["entity_id"] for x in ps], p, [
            ("solvent", "CH3CN", False), ("temperature", qty(25, "°C"), False), ("time", qty(time_h, "h"), False),
        ]),
    ], [field("yield", qty(yield_pct, "%"), p, target)]))

ps = [
    participant("s9g_acid", "reactant", "generic 4-alkyl-substituted 2,3-allenoic acid", p),
    participant("s9g_cux2", "reagent", "CuX2 (X=Cl or Br)", p, amounts=[field("equivalents", qty(4, "equiv"), p)]),
    participant("s9g_acetone", "solvent", "acetone", p, smiles="CC(=O)C"),
    participant("s9g_water", "solvent", "H2O", p, smiles="O"),
    participant("s9g_product", "product", "beta-halobutenolide", p),
]
records.append(record("p02_scheme09_aqueous_general", p, "general_scheme", ps, [
    make_step("aqueous_halolactonization", [x["entity_id"] for x in ps], p, [
        ("solvent", "acetone/H2O 2:1", False), ("temperature", rng(65, 70, "°C", "65-70 °C"), False),
    ]),
], [field("yield", {"number": 89, "unit": "%", "qualifier": "gt", "raw_text": ">89%"}, p, "s9g_product")]))

# Page 3: Schemes 10-13.
p = 3
ps = [
    participant("s10mix_acid", "reactant", "n-C7H15-substituted 2,3-allenoic acid", p),
    participant("s10mix_cux2", "reagent", "CuX2", p, amounts=[field("equivalents", qty(2, "equiv"), p)]),
    participant("s10mix_acetone", "solvent", "acetone", p, smiles="CC(=O)C"),
    participant("s10mix_water", "solvent", "H2O", p, smiles="O"),
    participant("s10mix_product", "product", "halobutenolide/cycloisomerization product mixture (X=Br or Cl / H)", p),
]
records.append(record("p03_scheme10_two_equiv_cux2_competition", p, "optimization_entry", ps, [
    make_step("competitive_cyclization", [x["entity_id"] for x in ps], p, [
        ("solvent", "acetone/H2O", False), ("temperature", rng(65, 70, "°C", "65-70 °C"), False),
    ]),
], unresolved=["The small Scheme 10 product annotation is visually read with prose context as halogenated versus X=H products; no quantitative ratio is reported."]))

ps = [
    participant("s10cucl_acid", "reactant", "generic 2,3-allenoic acid", p),
    participant("s10cucl", "catalyst", "CuCl", p, amounts=[field("catalyst_loading", qty(4, "mol%"), p)]),
    participant("s10cucl_meoh", "solvent", "MeOH", p, smiles="CO"),
    participant("s10cucl_product", "product", "beta-unsubstituted butenolide", p),
]
records.append(record("p03_scheme10_cucl_cycloisomerization", p, "general_scheme", ps, [
    make_step("cycloisomerization", [x["entity_id"] for x in ps], p, [
        ("solvent", "MeOH", False), ("temperature", "reflux", False), ("time", qty(2, "h"), False),
    ]),
], [field("yield", rng(77, 97, "%", "77-97%"), p, "s10cucl_product")]))

ps = [
    participant("s11_racemate", "reactant", "racemic 2,3-allenoic acid", p),
    participant("s11_base", "reagent", "optically active base (Base*)", p),
    participant("s11_salt_a", "product", "diastereomeric acid-base salt A", p),
    participant("s11_salt_b", "product", "diastereomeric acid-base salt B", p),
    participant("s11_product_s", "product", "one enantiomer of beta-halobutenolide", p),
    participant("s11_product_r", "product", "opposite enantiomer of beta-halobutenolide", p),
]
records.append(record("p03_scheme11_resolution_halolactonization_concept", p, "general_scheme", ps, [
    make_step("diastereomeric_salt_formation", ["s11_racemate", "s11_base", "s11_salt_a", "s11_salt_b"], p),
    make_step("halolactonization", ["s11_salt_a", "s11_salt_b", "s11_product_s", "s11_product_r"], p),
], notes=[("Scheme 11 contrasts direct salt halolactonization with the usual free-acid route.", p, False)]))

ps = [
    participant("s12_racemate", "reactant", "racemic 2-methyl-4-phenyl-2,3-butadienoic acid", p, smiles=acid_smiles),
    participant("s12_cinch", "reagent", "L-(-)-cinchonidine", p),
    participant("s12_salt", "product", "Sa-(+)-5a cinchonidine salt", p),
    participant("s12_h2so4", "reagent", "dilute H2SO4", p, smiles="OS(=O)(=O)O"),
    participant("s12_acid", "product", "Sa-(+)-6a", p, name="Sa-(+)-2-methyl-4-phenyl-2,3-butadienoic acid"),
]
records.append(record("p03_scheme12_cinchonidine_resolution", p, "reported_experiment", ps, [
    make_step("salt_formation_and_recrystallization", ["s12_racemate", "s12_cinch", "s12_salt"], p),
    make_step("acid_release", ["s12_salt", "s12_h2so4", "s12_acid"], p),
], notes=[("Absolute allene configuration was established by single-crystal X-ray analysis of salt (+)-5a containing water.", p, True)]))

for suffix, reagent, solvent, temp, time_h, yield_pct, ee_pct, reagent_smiles in [
    ("nbs_6h", "NBS", "H2O", "r.t.", 6, 21, 94, "O=C1CCC(=O)N1Br"),
    ("nbs_24h", "NBS", "H2O", "r.t.", 24, 50, 64, "O=C1CCC(=O)N1Br"),
    ("cubr2", "CuBr2", "acetone/H2O 2:1", rng(60, 65, "°C", "60-65 °C"), 3, 95, 98, "[Cu+2].[Br-].[Br-]"),
]:
    ps = [
        participant(f"s13_{suffix}_salt", "reactant", "Sa-(+)-5a cinchonidine salt", p),
        participant(f"s13_{suffix}_reagent", "reagent", reagent, p, smiles=reagent_smiles),
        participant(f"s13_{suffix}_solvent", "solvent", solvent, p),
        participant(f"s13_{suffix}_product", "product", "(S)-(+)-7a bromobutenolide", p),
    ]
    target = f"s13_{suffix}_product"
    records.append(record(f"p03_scheme13_{suffix}", p, "optimization_entry", ps, [
        make_step("halolactonization", [x["entity_id"] for x in ps], p, [
            ("solvent", solvent, False), ("temperature", temp, False), ("time", qty(time_h, "h"), False),
        ]),
    ], [field("yield", qty(yield_pct, "%"), p, target), field("ee", qty(ee_pct, "%"), p, target)]))

# Page 4: Schemes 14-17.
p = 4
ps = [
    participant("s14res_racemate", "reactant", "racemic 2-methyl-4-phenyl-2,3-butadienoic acid", p, smiles=acid_smiles),
    participant("s14res_samine", "reagent", "(S)-(-)-alpha-methylbenzylamine", p),
    participant("s14res_ramine", "reagent", "(R)-(+)-alpha-methylbenzylamine", p),
    participant("s14res_plus", "product", "(+)-4a acid-base salt", p),
    participant("s14res_minus", "product", "(-)-4a acid-base salt", p),
]
records.append(record("p04_scheme14_alpha_methylbenzylamine_resolution", p, "general_scheme", ps, [
    make_step("resolve_with_s_amine", ["s14res_racemate", "s14res_samine", "s14res_plus"], p),
    make_step("resolve_with_r_amine", ["s14res_racemate", "s14res_ramine", "s14res_minus"], p),
]))

for suffix, salt_label, x, time_h, yield_pct, ee_pct, product_label, reagent_smiles in [
    ("s_br", "(+)-4a salt from (S)-amine", "Br", 3, 92, 98, "S-(+)-7a", "[Cu+2].[Br-].[Br-]"),
    ("s_cl", "(+)-4a salt from (S)-amine", "Cl", 6, 90, 97, "S-(+)-7b", "[Cu+2].[Cl-].[Cl-]"),
    ("r_br", "(-)-4a salt from (R)-amine", "Br", 3, 90, 98, "R-(-)-7a", "[Cu+2].[Br-].[Br-]"),
    ("r_cl", "(-)-4a salt from (R)-amine", "Cl", 6, 93, 98, "R-(-)-7b", "[Cu+2].[Cl-].[Cl-]"),
]:
    ps = [
        participant(f"s14_{suffix}_salt", "reactant", salt_label, p),
        participant(f"s14_{suffix}_cu", "reagent", f"Cu{x}2", p, smiles=reagent_smiles),
        participant(f"s14_{suffix}_acetone", "solvent", "acetone", p, smiles="CC(=O)C"),
        participant(f"s14_{suffix}_water", "solvent", "H2O", p, smiles="O"),
        participant(f"s14_{suffix}_product", "product", product_label, p),
    ]
    target = f"s14_{suffix}_product"
    records.append(record(f"p04_scheme14_{suffix}", p, "substrate_scope_entry", ps, [
        make_step("enantiospecific_halolactonization", [x["entity_id"] for x in ps], p, [
            ("solvent", "acetone/H2O 2:1", False), ("temperature", rng(60, 65, "°C", "60-65 °C"), False), ("time", qty(time_h, "h"), False),
        ]),
    ], [field("yield", qty(yield_pct, "%"), p, target), field("ee", qty(ee_pct, "%"), p, target)]))

ps = [
    participant("s15_acid", "reactant", "Sa-(+)-6a", p, name="Sa-(+)-2-methyl-4-phenyl-2,3-butadienoic acid", smiles=acid_smiles, amounts=[field("starting_material_ee", qty(96, "%"), p)]),
    participant("s15_phi", "reactant", "PhI", p, name="iodobenzene", smiles="Ic1ccccc1"),
    participant("s15_pd", "catalyst", "Pd2(dba)3·CHCl3", p, amounts=[field("catalyst_loading", qty(2.5, "mol%"), p)]),
    participant("s15_pph3", "reagent", "PPh3", p, name="triphenylphosphine", smiles="P(c1ccccc1)(c1ccccc1)c1ccccc1", amounts=[field("loading", qty(10, "mol%"), p)]),
    participant("s15_toluene", "solvent", "toluene", p, smiles="Cc1ccccc1"),
    participant("s15_product", "product", "S-(+)-8a", p),
]
records.append(record("p04_scheme15_free_acid_pd_coupling", p, "reported_experiment", ps, [
    make_step("pd_coupling_cyclization", [x["entity_id"] for x in ps], p, [("solvent", "toluene", False)]),
], [field("product_ee_highest", qty(60, "%"), p, "s15_product", text=True)], unresolved=["Scheme 15 reports 'lower ee' and the prose reports a highest ee of 60%; reaction time, temperature, and yield are absent."]))

for suffix, note in [
    ("scheme16_carbopalladation_chirality_loss", "Scheme 16 proposes a pi-allylpalladium pathway that may lose stereochemical information."),
    ("scheme17_oxypalladation_reductive_elimination", "Scheme 17 proposes coordination-directed oxypalladation/reductive elimination with efficient chirality transfer."),
]:
    ps = [
        participant(f"{suffix}_salt", "reactant", "generic allenoate acid-base salt", p),
        participant(f"{suffix}_halide", "reactant", "R4X", p),
        participant(f"{suffix}_pd", "catalyst", "Pd(0)L", p),
        participant(f"{suffix}_product", "product", "generic chiral butenolide 3", p),
    ]
    records.append(record(f"p04_{suffix}", p, "mechanism", ps, [
        make_step("proposed_catalytic_cycle", [x["entity_id"] for x in ps], p, fill_missing=False),
    ], notes=[(note, p, False)]))

# Page 5: Schemes 18-21.
p = 5
ps = [
    participant("s18salt_acid", "reactant", "Sa-(+)-6a", p, amounts=[field("starting_material_ee", qty(97, "%"), p)]),
    participant("s18salt_dipea", "reagent", "NEt(i-Pr)2", p, name="DIPEA", smiles="CCN(C(C)C)C(C)C"),
    participant("s18salt_etoac", "solvent", "CH3CO2Et", p, name="ethyl acetate", smiles="CCOC(C)=O"),
    participant("s18salt_product", "product", "Sa-(+)-9a DIPEA salt", p, amounts=[field("product_ee", qty(97, "%"), p)]),
]
records.append(record("p05_scheme18_dipea_salt_preparation", p, "reported_experiment", ps, [
    make_step("salt_formation", [x["entity_id"] for x in ps], p, [
        ("solvent", "ethyl acetate", False), ("temperature", "r.t.", True),
    ]),
], extra_pages=[4], unresolved=["No salt-isolation yield or reaction time is reported."]))

ps = [
    participant("s18cp_salt", "reactant", "Sa-(+)-9a DIPEA salt", p, amounts=[field("starting_material_ee", qty(97, "%"), p)]),
    participant("s18cp_phi", "reactant", "PhI", p, name="iodobenzene", smiles="Ic1ccccc1"),
    participant("s18cp_pd", "catalyst", "Pd2(dba)3·CHCl3", p, amounts=[field("catalyst_loading", qty(5, "mol%"), p)]),
    participant("s18cp_pph3", "reagent", "PPh3", p, smiles="P(c1ccccc1)(c1ccccc1)c1ccccc1", amounts=[field("loading", qty(20, "mol%"), p)]),
    participant("s18cp_toluene", "solvent", "toluene", p, smiles="Cc1ccccc1"),
    participant("s18cp_product", "product", "S-(+)-8a", p),
]
records.append(record("p05_scheme18_salt_pd_coupling", p, "reported_experiment", ps, [
    make_step("pd_coupling_cyclization", [x["entity_id"] for x in ps], p, [
        ("solvent", "toluene", False), ("temperature", qty(5, "°C"), False), ("time", qty(60, "h"), False),
    ]),
], [field("yield", qty(62, "%"), p, "s18cp_product"), field("ee", qty(91, "%"), p, "s18cp_product")]))

for suffix, salt, salt_ee, product, yield_pct, prod_ee in [
    ("8f", "Sa-(+)-4f cinchonidine salt", 99, "S-(+)-8f", 60, 94),
    ("8g", "Sa-(+)-4g cinchonidine salt", 98, "S-(+)-8g", 72, 91),
]:
    ps = [
        participant(f"s19_{suffix}_salt", "reactant", salt, p, amounts=[field("starting_material_ee", qty(salt_ee, "%"), p)]),
        participant(f"s19_{suffix}_phi", "reactant", "PhI", p, smiles="Ic1ccccc1"),
        participant(f"s19_{suffix}_pd", "catalyst", "Pd2(dba)3·CHCl3", p, amounts=[field("catalyst_loading", qty(5, "mol%"), p)]),
        participant(f"s19_{suffix}_pph3", "reagent", "PPh3", p, smiles="P(c1ccccc1)(c1ccccc1)c1ccccc1", amounts=[field("loading", qty(20, "mol%"), p)]),
        participant(f"s19_{suffix}_toluene", "solvent", "toluene", p, smiles="Cc1ccccc1"),
        participant(f"s19_{suffix}_product", "product", product, p),
    ]
    target = f"s19_{suffix}_product"
    records.append(record(f"p05_scheme19_coupling_{suffix}", p, "substrate_scope_entry", ps, [
        make_step("pd_coupling_cyclization", [x["entity_id"] for x in ps], p, [
            ("solvent", "toluene", False), ("temperature", qty(5, "°C"), False), ("time", qty(60, "h"), False),
        ]),
    ], [field("yield", qty(yield_pct, "%"), p, target), field("ee", qty(prod_ee, "%"), p, target)]))

for suffix, source_label, product_label in [
    ("salt_4f_to_4g", "Sa-(+)-4f cinchonidine salt", "Sa-(+)-4g cinchonidine salt"),
    ("product_8f_to_8g", "S-(+)-8f", "S-(+)-8g"),
]:
    ps = [
        participant(f"s19_{suffix}_source", "reactant", source_label, p),
        participant(f"s19_{suffix}_nbuli", "reagent", "n-BuLi", p),
        participant(f"s19_{suffix}_h3o", "reagent", "H3O+", p),
        participant(f"s19_{suffix}_product", "product", product_label, p),
    ]
    records.append(record(f"p05_scheme19_{suffix}", p, "reported_experiment", ps, [
        make_step("lithium_halogen_exchange", [f"s19_{suffix}_source", f"s19_{suffix}_nbuli"], p),
        make_step("acidic_workup", [f"s19_{suffix}_h3o", f"s19_{suffix}_product"], p),
    ], unresolved=["Scheme 19 gives no reagent amounts, solvent, temperature, time, or yield for this conversion."]))

ps = [
    participant("s19res_acid", "reactant", "racemic p-H-substituted n-propyl allenoic acid", p),
    participant("s19res_agent", "unspecified_agent", "resolution agent (not shown on this arrow)", p),
    participant("s19res_salt", "product", "Sa-(+)-4g cinchonidine salt", p, amounts=[field("product_ee", qty(98, "%"), p)]),
]
records.append(record("p05_scheme19_resolution_to_4g", p, "reported_experiment", ps, [
    make_step("resolution", [x["entity_id"] for x in ps], p),
], unresolved=["The Scheme 19 resolution arrow does not identify the resolving-agent amount, solvent, temperature, time, or yield."]))

ps = [
    participant("s20_ester", "reactant", "generic 2,3-allenoate", p),
    participant("s20_oh", "reagent", "OH-", p),
    participant("s20_h", "reagent", "H+", p),
    participant("s20_acid", "product", "2,3-allenoic acid / 3-alkynoic acid mixture", p),
]
records.append(record("p05_scheme20_hydrolysis_literature_route", p, "literature_example", ps, [
    make_step("hydrolysis_and_acidification", [x["entity_id"] for x in ps], p),
], notes=[("The article presents this as the usual preparation route and notes that an acid/alkynoic-acid mixture can result.", p, True)]))

ps = [
    participant("s20lit_acid", "reactant", "generic 2,3-allenoic acid", p),
    participant("s20lit_product", "product", "beta-halobutenolide", p),
]
records.append(record("p05_scheme20_prior_acid_halolactonization", p, "literature_example", ps, [
    make_step("reported_prior_halolactonization", [x["entity_id"] for x in ps], p),
], notes=[("Scheme 20 explicitly labels this arrow refs. 15-17; it is not a new individual experiment in this Account.", p, False)]))

ps = [
    participant("s21_ester", "reactant", "generic ethyl 2,3-allenoate", p),
    participant("s21_cubr2", "reagent", "CuBr2", p, smiles="[Cu+2].[Br-].[Br-]"),
    participant("s21_etoh", "solvent", "EtOH", p, smiles="CCO"),
    participant("s21_water", "solvent", "H2O", p, smiles="O"),
    participant("s21_product", "product", "beta-bromobutenolide", p),
]
records.append(record("p05_scheme21_direct_allenoate_bromolactonization", p, "general_scheme", ps, [
    make_step("direct_bromolactonization", [x["entity_id"] for x in ps], p, [
        ("solvent", "EtOH/H2O 3:2", False), ("temperature", rng(80, 85, "°C", "80-85 °C"), False), ("time", qty(12, "h"), False),
    ]),
], [field("yield", rng(54, 97, "%", "54-97%"), p, "s21_product")]))

# Page 6: Schemes 22-29.
p = 6
for suffix, r1, ester_r, yield_pct, substrate_smiles, product_smiles in [
    ("h_et", "H", "C2H5", 40, "CCOC(=O)C(C)=C=Cc1ccccc1", "CC1=C(Br)C(c2ccccc2)OC1=O"),
    ("h_bn", "H", "CH2C6H5", 67, "CC(=C=Cc1ccccc1)C(=O)OCc1ccccc1", "CC1=C(Br)C(c2ccccc2)OC1=O"),
    ("et_bn", "C2H5", "CH2C6H5", 66, "CC(=C=C(c1ccccc1)CC)C(=O)OCc1ccccc1", "CC1=C(Br)C(c2ccccc2)(CC)OC1=O"),
]:
    ps = [
        participant(f"s22_{suffix}_ester", "reactant", f"Scheme 22 allenoate (R1={r1}, R={ester_r})", p, smiles=substrate_smiles),
        participant(f"s22_{suffix}_cubr2", "reagent", "CuBr2", p, smiles="[Cu+2].[Br-].[Br-]"),
        participant(f"s22_{suffix}_etoh", "solvent", "ethanol", p, smiles="CCO"),
        participant(f"s22_{suffix}_water", "solvent", "H2O", p, smiles="O"),
        participant(f"s22_{suffix}_product", "product", f"bromobutenolide 2 (R1={r1}, R={ester_r})", p, smiles=product_smiles),
    ]
    target = f"s22_{suffix}_product"
    records.append(record(f"p06_scheme22_{suffix}", p, "substrate_scope_entry", ps, [
        make_step("bromolactonization", [x["entity_id"] for x in ps], p, [
            ("solvent", "ethanol/H2O", False), ("temperature", rng(80, 85, "°C", "80-85 °C"), False),
        ]),
    ], [field("yield", qty(yield_pct, "%"), p, target)], unresolved=["Scheme 22 does not state the ethanol/water ratio or reaction time for these three rows."]))

ps = [
    participant("s24_amide", "reactant", "n-C6H13/Me-substituted N-benzyl 2,3-allenamide", p, smiles="CCCCCCC=C=C(C)C(=O)NCc1ccccc1"),
    participant("s24_cubr2", "reagent", "CuBr2", p, smiles="[Cu+2].[Br-].[Br-]", amounts=[field("equivalents", qty(1.1, "equiv"), p)]),
    participant("s24_air", "reagent", "oxygen in air", p, name="oxygen", smiles="O=O"),
    participant("s24_product", "product", "4-bromo-5-hydroxy-N-benzyl pyrrol-2(5H)-one", p, smiles="CC1=C(Br)C(O)(CCCCCC)N(Cc2ccccc2)C1=O"),
]
records.append(record("p06_scheme24_cubr2_allenamide_cyclization_oxidation", p, "reported_experiment", ps, [
    make_step("halolactamization", ["s24_amide", "s24_cubr2"], p, [("temperature", qty(50, "°C"), False)]),
    make_step("oxidation", ["s24_air", "s24_product"], p, [("atmosphere", "air", True)]),
], [field("yield", qty(72, "%"), p, "s24_product")], notes=[("The prose states that the initially formed 4-halopyrrol-2(5H)-one is oxidized by oxygen in air and that Cu(II) may mediate this step.", p, True)]))

ps = [
    participant("s25_amide", "reactant", "generic 2,3-allenamide", p),
    participant("s25_r5pdi", "catalyst", "R5PdI", p),
    participant("s25_lactam", "product", "5-hydroxypyrrol-2(5H)-one", p),
    participant("s25_imino", "product", "iminolactone", p),
]
records.append(record("p06_scheme25_n_vs_o_attack_mechanism", p, "mechanism", ps, [
    make_step("carbopalladation", ["s25_amide", "s25_r5pdi"], p, fill_missing=False),
    make_step("n_attack_or_o_attack", ["s25_lactam", "s25_imino"], p, fill_missing=False),
], notes=[("N attack is assigned to R2=H, while O attack is assigned to R1/R2 not equal to H in the scheme.", p, False)]))

ps = [
    participant("s26_allenol", "reactant", "generic 2,3-allenol", p),
    participant("s26_ag", "catalyst", "Ag+", p),
    participant("s26_product", "product", "2,5-dihydrofuran", p),
]
records.append(record("p06_scheme26_ag_cycloisomerization_prior_work", p, "literature_example", ps, [
    make_step("ag_catalyzed_cycloisomerization", [x["entity_id"] for x in ps], p),
], notes=[("The prose attributes this reaction to Claesson and Marshall (refs. 29 and 30).", p, True)]))

ps = [
    participant("s27tsuji_allenol", "reactant", "generic 2,3-allenol", p),
    participant("s27tsuji_halide", "reactant", "R2X", p),
    participant("s27tsuji_pd", "catalyst", "Pd(0)", p),
    participant("s27tsuji_product", "product", "alpha,beta-unsaturated enone", p),
]
records.append(record("p06_scheme27_tsuji_enone_prior_work", p, "literature_example", ps, [
    make_step("pd_coupling_beta_h_elimination", [x["entity_id"] for x in ps], p),
], notes=[("Scheme 27 labels this branch Tsuji et al.; the prose attributes it to ref. 31.", p, False)]))

ps = [
    participant("s27try_allenol", "reactant", "generic 2,3-allenol", p),
    participant("s27try_halide", "reactant", "R2X", p),
    participant("s27try_pd", "catalyst", "Pd(0)", p),
    participant("s27try_furan", "product", "4-substituted 2,5-dihydrofuran 10", p),
    participant("s27try_epoxide", "product", "vinylic epoxide", p),
]
records.append(record("p06_scheme27_proposed_product_paths", p, "general_scheme", ps, [
    make_step("coupling_cyclization_possibilities", [x["entity_id"] for x in ps], p),
], notes=[("Scheme 27 frames two possible products; Scheme 28 reports exclusive trans-vinylic epoxide formation under the selected conditions.", p, False)]))

ps = [
    participant("s28_allenol", "reactant", "generic 2,3-allenol", p),
    participant("s28_ri", "reactant", "R2I", p),
    participant("s28_pd", "catalyst", "Pd(PPh3)4", p, amounts=[field("catalyst_loading", qty(5, "mol%"), p)]),
    participant("s28_k2co3", "reagent", "K2CO3", p, smiles="[K+].[K+].[O-]C([O-])=O"),
    participant("s28_dmf", "solvent", "DMF", p, smiles="CN(C)C=O"),
    participant("s28_product", "product", "trans-vinylic epoxide", p),
]
records.append(record("p06_scheme28_pd_vinylic_epoxide_general", p, "general_scheme", ps, [
    make_step("pd_insertion_cyclization", [x["entity_id"] for x in ps], p, [
        ("solvent", "DMF", False), ("temperature", rng(55, 65, "°C", "55-65 °C"), False),
    ]),
], [
    field("yield", rng(46, 95, "%", "46-95%"), p, "s28_product"),
    field("diastereomeric_ratio", "92:8-100:0", p, "s28_product"),
    field("regioselectivity", "trans three-membered vinylic epoxide exclusively", p, "s28_product", text=True),
]))

for suffix, iodide_label, iodide_smiles, yield_pct, ee_pct, product_label in [
    ("vinyl_iodide", "n-C4H9-substituted vinyl iodide", None, 52, 98, "R,R vinylic epoxide (n-C4H9 alkenyl substituent)"),
    ("p_iodotoluene", "p-iodotoluene", "Cc1ccc(I)cc1", 85, 96, "R,R vinylic epoxide (p-tolyl substituent)"),
]:
    ps = [
        participant(f"s29_{suffix}_allenol", "reactant", "optically active n-C8H17-substituted 2,3-allenol", p),
        participant(f"s29_{suffix}_iodide", "reactant", iodide_label, p, smiles=iodide_smiles),
        participant(f"s29_{suffix}_pd", "catalyst", "Pd(PPh3)4", p, amounts=[field("catalyst_loading", qty(5, "mol%"), p)]),
        participant(f"s29_{suffix}_k2co3", "reagent", "K2CO3", p, smiles="[K+].[K+].[O-]C([O-])=O"),
        participant(f"s29_{suffix}_dmf", "solvent", "DMF", p, smiles="CN(C)C=O"),
        participant(f"s29_{suffix}_product", "product", product_label, p),
    ]
    target = f"s29_{suffix}_product"
    records.append(record(f"p06_scheme29_{suffix}", p, "substrate_scope_entry", ps, [
        make_step("enantiospecific_pd_insertion_cyclization", [x["entity_id"] for x in ps], p, [
            ("solvent", "DMF", False), ("temperature", rng(55, 65, "°C", "55-65 °C"), False),
        ]),
    ], [field("yield", qty(yield_pct, "%"), p, target), field("ee", qty(ee_pct, "%"), p, target), field("absolute_configuration", "R,R", p, target)]))


def ids(prefix):
    return [r["record_id"] for r in records if r["record_id"].startswith(f"{DOC}:{prefix}")]


coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1,
            "state": "attempted",
            "regions": [
                {"region": "upper-right Scheme 1", "finding": "Conceptual allene/chirality design diagram; no concrete experiment or quantities.", "evidence_ids": [I[1]]},
                {"region": "middle-right Scheme 2 and adjacent section text", "finding": "Proposed Pd carbopalladation/intramolecular C-O bond-formation mechanism, not a preparative experiment.", "evidence_ids": [I[1], T[1]]},
                {"region": "title, abstract, and introduction", "finding": "Document identity and scope context; no additional individual experiment.", "evidence_ids": [I[1], T[1]]},
            ],
            "record_ids": ids("p01_"),
            "unresolved": ["Scheme 1 uses placeholders rather than molecular structures.", "No SI was supplied or explicitly associated."],
        },
        {
            "page": 2,
            "state": "attempted",
            "regions": [
                {"region": "left/top Schemes 3-5", "finding": "General Pd/Ag coupling-cyclization, solid-phase sequence, and three linker-cleavage protocols were separated by condition set.", "evidence_ids": [I[2], T[2]]},
                {"region": "right/top Schemes 6-9", "finding": "Coupling concept, two halolactonizations, two cross-coupling classes, four Scheme 9 optimization rows, and one aqueous general condition were extracted.", "evidence_ids": [I[2], T[2]]},
                {"region": "lower prose", "finding": "Prose assignments for cleavage reagents and cited method context were used; no unshown conditions were inferred.", "evidence_ids": [I[2], T[2]]},
            ],
            "record_ids": ids("p02_"),
            "unresolved": ["Schemes 3-8 summarize generic R-group scopes rather than individual substrate structures.", "Yield measurement bases, workups, and purification are not stated on this page."],
        },
        {
            "page": 3,
            "state": "attempted",
            "regions": [
                {"region": "upper-left Schemes 10-11", "finding": "Competitive two-equivalent CuX2 condition, CuCl cycloisomerization, and conceptual resolution/halolactonization paths were classified separately.", "evidence_ids": [I[3], T[3]]},
                {"region": "upper-right Schemes 12-13", "finding": "Cinchonidine resolution/acid release and three explicit halolactonization rows were extracted independently.", "evidence_ids": [I[3], T[3]]},
                {"region": "lower prose", "finding": "Prose confirms Scheme 13 yields and ee values and distinguishes short/long NBS reactions from CuBr2 conditions.", "evidence_ids": [I[3], T[3]]},
            ],
            "record_ids": ids("p03_"),
            "unresolved": ["Scheme 10's tiny product label is not fully legible; the halogen-vs-H assignment is retained as unresolved with prose context.", "Resolution yields and most operational details are absent."],
        },
        {
            "page": 4,
            "state": "attempted",
            "regions": [
                {"region": "upper-left Scheme 14", "finding": "Alpha-methylbenzylamine resolution overview plus four Br/Cl enantiospecific halolactonization entries were extracted.", "evidence_ids": [I[4], T[4]]},
                {"region": "middle-left Schemes 15-16", "finding": "Low-ee free-acid coupling is a reported experiment; the carbopalladation drawing is a proposed mechanism.", "evidence_ids": [I[4], T[4]]},
                {"region": "upper-right Scheme 17", "finding": "Coordination-directed oxypalladation/reductive-elimination catalytic cycle classified as mechanism.", "evidence_ids": [I[4], T[4]]},
                {"region": "right-column Sections III-IV prose", "finding": "Context points forward to Schemes 18-24; no extra arrow or table row appears on page 4.", "evidence_ids": [I[4], T[4]]},
            ],
            "record_ids": ids("p04_"),
            "unresolved": ["Scheme 15 omits time, temperature, yield, and exact product ee except the prose maximum of 60%.", "Generic mechanism structures retain null SMILES."],
        },
        {
            "page": 5,
            "state": "attempted",
            "regions": [
                {"region": "upper Scheme 18", "finding": "DIPEA salt preparation and the subsequent quantified Pd coupling were separated into successive records.", "evidence_ids": [I[5], T[5]]},
                {"region": "center Scheme 19", "finding": "Two quantified couplings, two n-BuLi/H3O+ conversions, one resolution arrow, and X-ray characterization annotations were inventoried; X-ray arrows were not misclassified as reactions.", "evidence_ids": [I[5], T[5]]},
                {"region": "lower Schemes 20-21", "finding": "Prior hydrolysis/acid routes were classified as literature examples; the direct CuBr2 allenoate method is a general scheme with explicit conditions.", "evidence_ids": [I[5], T[5]]},
                {"region": "lower prose", "finding": "Allenamide and allenol section text provides context only for figures on page 6.", "evidence_ids": [I[5], T[5]]},
            ],
            "record_ids": ids("p05_"),
            "unresolved": ["Scheme 19 omits conditions and yields for the dehalogenation and resolution arrows.", "Scheme 20 is conceptual/cited context rather than a fully specified new experiment."],
        },
        {
            "page": 6,
            "state": "attempted",
            "regions": [
                {"region": "upper-left Schemes 22-24", "finding": "Three Scheme 22 substrate rows were split; Scheme 23 is a structure-only set of biological examples; Scheme 24 is a sequential cyclization/air-oxidation experiment.", "evidence_ids": [I[6], T[6]]},
                {"region": "middle-left Schemes 25-26", "finding": "Scheme 25 is a proposed N-vs-O attack mechanism; Scheme 26 is explicitly prior Ag-catalyzed literature.", "evidence_ids": [I[6], T[6]]},
                {"region": "right Schemes 27-29", "finding": "Tsuji prior work, a conceptual product fork, the generic epoxide method, and two optically active scope examples were classified separately.", "evidence_ids": [I[6], T[6]]},
                {"region": "lower prose", "finding": "Prose confirms DMF, lack of Ag2CO3, exclusive trans epoxides, and literature/new-work distinctions.", "evidence_ids": [I[6], T[6]]},
            ],
            "record_ids": ids("p06_"),
            "unresolved": ["Scheme 22 does not show reaction time or solvent ratio.", "Scheme 24 omits solvent and time.", "Scheme 28/29 omit reaction time and K2CO3 amount; chiral drawings were not converted into asserted stereochemical SMILES."],
        },
    ],
}


RAW.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
COVERAGE.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

if TASKS.exists():
    tasks = json.loads(TASKS.read_text())
    wanted = {f"{DOC}:page{p}:text" for p in range(1, 7)}
    for task in tasks:
        if task.get("task_id") in wanted:
            task["state"] = "attempted"
            task["visual_evidence_id"] = I[int(task["task_id"].split("page")[1].split(":")[0])]
            task["reason"] = "Original page image and extracted page text inspected; findings and unresolved issues are recorded in coverage/pages_0001_0006.json."
    TASKS.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"records": len(records), "raw": str(RAW), "coverage": str(COVERAGE)}, ensure_ascii=False))
