"""Build the source-linked machine extraction for PDF pages 1--6.

This is intentionally a machine submission: merge will quarantine every record as
needs_review and remove any accidental self-certification.
"""
from __future__ import annotations

import json
from pathlib import Path


DOC = "doc_3f267ff48aec9258"
BASE = Path(__file__).resolve().parents[1]


def ev(*pages: int) -> list[str]:
    ids: list[str] = []
    for page in pages:
        ids.extend([f"{DOC}:page{page}:text", f"{DOC}:page{page}:image"])
    return ids


def fact(value, evidence=None):
    return {
        "value": value,
        "evidence_ids": list(evidence or []),
        "verification": "missing" if value is None else "unreviewed",
    }


def field(name, value, evidence=None, targets=None):
    out = {"name": name, "fact": fact(value, evidence)}
    if targets:
        out["target_entity_ids"] = targets
    return out


SMILES = {
    "PhI": "Ic1ccccc1",
    "K2CO3": "[K+].[K+].[O-]C([O-])=O",
    "Ag2CO3": "[Ag+].[Ag+].[O-]C([O-])=O",
    "NaH": "[Na+].[H-]",
    "NaOH": "[Na+].[OH-]",
    "PPh3": "c1ccc(P(c2ccccc2)c2ccccc2)cc1",
    "NMP": "CN1CCCC1=O",
    "DMA": "CC(=O)N(C)C",
    "MeCN": "CC#N",
    "toluene": "Cc1ccccc1",
    "MeOH": "CO",
    "CO": "[C-]#[O+]",
    "DMSO": "CS(C)=O",
    "DMF": "CN(C)C=O",
    "THF": "C1CCOC1",
    "dioxane": "O1CCOCC1",
    "n-Bu4NBr": "[Br-].CCCC[N+](CCCC)(CCCC)CCCC",
}


def participant(entity_id, role, label, evidence, *, name=None, smiles=None, amounts=None):
    if smiles is None:
        smiles = SMILES.get(label)
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence) if name else fact(None),
        "smiles": fact(smiles, evidence) if smiles else fact(None),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": amounts or [],
    }


def qty(name, value, evidence):
    return field(name, value, evidence)


def record(suffix, kind, pages, participants, *, conditions=None, outcomes=None,
           notes=None, unresolved=None, source=None, steps=None):
    evidence = ev(*pages)
    if steps is None:
        steps = [{
            "step_id": "step1",
            "participant_ids": [p["entity_id"] for p in participants],
            "conditions": conditions or [],
        }]
    return {
        "record_id": f"{DOC}:{suffix}",
        "document_id": DOC,
        "source_reaction_id": source or suffix,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": evidence,
        "participants": participants,
        "steps": steps,
        "outcomes": outcomes or [],
        "notes": [fact(x, evidence) for x in (notes or [])],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved or [],
        },
    }


records = []

# Page 1: conceptual pathways, not an experiment.
e = ev(1)
p = [
    participant("s1_allene", "reactant", "generic allene", e),
    participant("s1_rm", "reactant", "R-M", e),
    participant("s1_i1", "product", "pi-allyl metallic species 1", e),
    participant("s1_i2", "product", "sp2 C-M species 2", e),
]
records.append(record(
    "scheme1_carbometallation_paths", "mechanism", [1], p,
    conditions=[field("operation", "alternative regioselective insertion pathways", e)],
    notes=["Scheme 1 is a generic mechanistic comparison (path 1 versus path 2), not a reported experiment."],
    unresolved=["R and M are generic labels; structures, quantities, and operating conditions are unspecified."],
))

# Page 2, Scheme 2 upper: cited Tsuji-type literature example.
e = ev(2)
p = [
    participant("s2a_allene", "reactant", "n-butyl-substituted allene", e),
    participant("s2a_phi", "reactant", "PhI", e, name="iodobenzene"),
    participant("s2a_cat", "catalyst", "Pd(OAc)2-dppe", e),
    participant("s2a_nmp", "solvent", "NMP", e, name="N-methyl-2-pyrrolidone"),
    participant("s2a_product", "product", "1,3-diene (Scheme 2, upper)", e),
]
records.append(record(
    "scheme2_upper_tsuji_example", "literature_example", [2], p,
    conditions=[field("solvent", "NMP", e), field("time", None), field("temperature", None)],
    outcomes=[field("yield", None, targets=["s2a_product"]), field("stereoselectivity", "low", e, ["s2a_product"])],
    notes=["The prose attributes this transformation to Tsuji et al. (reference 6).", "The drawn pathway includes a pi-allylpalladium species followed by beta-H elimination."],
    unresolved=["No catalyst loading, temperature, time, yield, or product stereoisomer assignment is reported on this page."],
))

# Page 2, Scheme 2 lower: cited Cheng example.
e = ev(2)
p = [
    participant("s2b_enone", "reactant", "brominated cyclic enone (Scheme 2, lower)", e),
    participant("s2b_allene", "reactant", "phenyl/methyl-substituted allene (Scheme 2, lower)", e),
    participant("s2b_pddba2", "catalyst", "Pd(dba)2", e),
    participant("s2b_pph3", "catalyst", "PPh3", e),
    participant("s2b_k2co3", "reagent", "K2CO3", e),
    participant("s2b_dma", "solvent", "DMA", e, name="N,N-dimethylacetamide"),
    participant("s2b_product", "product", "1,3-diene adduct (Scheme 2, lower)", e),
]
records.append(record(
    "scheme2_lower_cheng_example", "literature_example", [2], p,
    conditions=[field("solvent", "DMA", e), field("temperature", {"number": 120, "unit": "°C"}, e), field("time", {"number": 12, "unit": "h"}, e)],
    outcomes=[field("yield", {"number": 53, "unit": "%"}, e, ["s2b_product"]), field("Z_E_ratio", "1:1", e, ["s2b_product"]), field("yield_measurement_basis", None, targets=["s2b_product"])],
    notes=["The prose attributes the poorly stereoselective reaction to Cheng et al. (reference 7)."],
    unresolved=["Catalyst/base quantities and yield measurement basis are not stated; drawn reactant/product structures remain unverified."],
))

# Page 2, Scheme 3: one arrow, two separately linked product yields.
e = ev(2)
p = [
    participant("s3_3", "reactant", "3", e, name="3,4-alkadienoate 3"),
    participant("s3_4", "reactant", "4", e, name="p-ethoxycarbonylphenyl iodide", smiles="CCOC(=O)c1ccc(I)cc1"),
    participant("s3_pddba2", "catalyst", "Pd(dba)2", e, amounts=[qty("catalyst_loading", {"number": 5, "unit": "mol%"}, e)]),
    participant("s3_pph3", "catalyst", "PPh3", e, amounts=[qty("catalyst_loading", {"number": 5, "unit": "mol%"}, e)]),
    participant("s3_k2co3", "reagent", "K2CO3", e, amounts=[qty("equivalents", {"number": 2, "unit": "equiv"}, e)]),
    participant("s3_dma", "solvent", "DMA", e, name="N,N-dimethylacetamide"),
    participant("s3_e6", "product", "E-6", e, name="4-aryl-2,4-alkadienoate E-6"),
    participant("s3_e7", "product", "E-7", e, name="E-4-(p-ethoxycarbonylphenyl)-3-butylidene-4-pentenoate"),
]
records.append(record(
    "scheme3_products_e6_e7", "literature_example", [2], p,
    conditions=[field("solvent", "DMA", e), field("temperature", {"number": 120, "unit": "°C"}, e), field("time", None)],
    outcomes=[field("yield", {"number": 16, "unit": "%"}, e, ["s3_e6"]), field("yield", {"number": 16, "unit": "%"}, e, ["s3_e7"]), field("yield_measurement_basis", None, targets=["s3_e6", "s3_e7"])],
    notes=["A single Scheme 3 reaction arrow gives products E-6 and E-7, each at 16%; the review cites reference 8."],
    unresolved=["Reaction time and yield measurement basis are missing; the full structures and stereochemical assignments were not independently verified."],
))

# Page 3, Scheme 4 generic substrate scope.
e = ev(3)
p = [
    participant("s4_allenoate", "reactant", "generic 3,4-alkadienoate", e),
    participant("s4_arx", "reactant", "ArX", e, name="aryl halide"),
    participant("s4_pd", "catalyst", "Pd(PPh3)4", e, amounts=[qty("catalyst_loading", {"number": 5, "unit": "mol%"}, e)]),
    participant("s4_ag", "catalyst", "Ag2CO3", e, amounts=[qty("catalyst_loading", {"number": 5, "unit": "mol%"}, e)]),
    participant("s4_base", "reagent", "K2CO3", e, amounts=[qty("equivalents", {"number": 4, "unit": "equiv"}, e)]),
    participant("s4_mecn", "solvent", "MeCN", e, name="acetonitrile"),
    participant("s4_product", "product", "generic 4-aryl-2,4-alkadienoate", e),
]
records.append(record(
    "scheme4_general_scope", "general_scheme", [3], p,
    conditions=[field("solvent", "MeCN", e), field("temperature", {"number": 75, "unit": "°C"}, e), field("atmosphere", "N2", e), field("time", None)],
    outcomes=[field("yield", {"minimum": 44, "maximum": 85, "unit": "%", "raw_text": "44-85%"}, e, ["s4_product"]), field("regioselectivity", "high", e, ["s4_product"]), field("stereoselectivity", "high", e, ["s4_product"]), field("yield_measurement_basis", None, targets=["s4_product"])],
    notes=["Scheme 4 is a generic R-group scope summary from reference 8, not one individual experiment."],
    unresolved=["Individual scope entries, reaction times, exact yields, and yield bases are not provided on this page."],
))

# Page 3, Scheme 5 reported literature transformation.
e = ev(3)
p = [
    participant("s5_8", "reactant", "8", e, name="N-(2-methylallyl)-N-(4-methoxycarbonyloxy-2-butynyl)benzenesulfonamide"),
    participant("s5_pd", "catalyst", "Pd(OAc)2", e, amounts=[qty("catalyst_loading", {"number": 10, "unit": "mol%"}, e)]),
    participant("s5_pph3", "catalyst", "PPh3", e, amounts=[qty("catalyst_loading", {"number": 20, "unit": "mol%"}, e)]),
    participant("s5_tol", "solvent", "toluene", e),
    participant("s5_co", "reagent", "CO", e, name="carbon monoxide"),
    participant("s5_meoh", "reagent", "MeOH", e, name="methanol"),
    participant("s5_12", "product", "12", e, name="bicyclic propenoate 12"),
]
steps = [
    {"step_id": "step1_cyclization", "participant_ids": ["s5_8", "s5_pd", "s5_pph3", "s5_tol"], "conditions": [field("solvent", "toluene", e), field("temperature", {"number": 85, "unit": "°C"}, e), field("time", {"number": 16, "unit": "h"}, e)]},
    {"step_id": "step2_carbonylation", "participant_ids": ["s5_co", "s5_meoh", "s5_12"], "conditions": [field("operation", "CO/MeOH conversion of intermediate 11 to product 12", e), field("time", None), field("temperature", None)]},
]
records.append(record(
    "scheme5_grigg_example", "literature_example", [3], p, steps=steps,
    outcomes=[field("yield", None, targets=["s5_12"])],
    notes=["The prose explicitly identifies this as the Grigg et al. literature example (reference 9)."],
    unresolved=["The CO pressure/amount, methanol amount, second-stage conditions, and product yield are not reported on this page."],
))

# Page 3, Scheme 5 mechanistic arrow sequence.
e = ev(3)
p = [participant("s5m_8", "reactant", "8", e), participant("s5m_9", "product", "9", e), participant("s5m_10", "product", "10", e), participant("s5m_11", "product", "11", e), participant("s5m_12", "product", "12", e)]
records.append(record(
    "scheme5_mechanistic_sequence", "mechanism", [3], p,
    conditions=[field("operation", "8 -> 9 -> 10 by 5-exo insertion -> 11 by 3-exo insertion -> 12 under CO/MeOH", e)],
    notes=["Species 9-11 are depicted palladium intermediates, not isolated experimental products."],
    unresolved=["Intermediate structures and the identity of X/L are not fully specified."],
))

# Scheme 6 spans the prose on page 3 and drawing on page 4.
e = ev(3, 4)
p = [
    participant("s6a_13", "reactant", "13", e, name="3-methyl-1,2-pentadienyl phenyl sulfone"),
    participant("s6a_phi", "reactant", "PhI", e, name="iodobenzene", amounts=[qty("equivalents", {"number": 1, "unit": "equiv"}, e)]),
    participant("s6a_pd", "catalyst", "Pd(PPh3)4", e, amounts=[qty("catalyst_loading", {"number": 5, "unit": "mol%"}, e)]),
    participant("s6a_ag", "catalyst", "Ag2CO3", e, amounts=[qty("catalyst_loading", {"number": 5, "unit": "mol%"}, e)]),
    participant("s6a_base", "reagent", "K2CO3", e, amounts=[qty("equivalents", {"number": 4, "unit": "equiv"}, e)]),
    participant("s6a_dmf", "solvent", "DMF", e),
    participant("s6a_14", "product", "14", e, name="phenyl-substituted 1,2-allenyl sulfone 14"),
]
records.append(record(
    "scheme6_allenyl_sulfone_14", "literature_example", [3, 4], p,
    conditions=[field("solvent", "DMF", e), field("temperature", {"number": 80, "unit": "°C"}, e), field("time", None)],
    outcomes=[field("yield", {"number": 42, "unit": "%"}, e, ["s6a_14"]), field("yield_measurement_basis", None, targets=["s6a_14"])],
    notes=["The review describes this as a recently observed Heck-type reaction and cites reference 10."],
    unresolved=["Reaction time and yield measurement basis are absent; drawn structures remain unverified."],
))

e = ev(4)
p = [
    participant("s6b_16", "reactant", "16", e, name="generic 1,3-monosubstituted allenyl phenyl sulfone"),
    participant("s6b_ari", "reactant", "ArI", e, name="aryl iodide"),
    participant("s6b_pd", "catalyst", "Pd(PPh3)4", e, amounts=[qty("catalyst_loading", {"number": 5, "unit": "mol%"}, e)]),
    participant("s6b_ag", "catalyst", "Ag2CO3", e, amounts=[qty("catalyst_loading", {"number": 5, "unit": "mol%"}, e)]),
    participant("s6b_base", "reagent", "K2CO3", e, amounts=[qty("equivalents", {"number": 4, "unit": "equiv"}, e)]),
    participant("s6b_dmf", "solvent", "DMF", e),
    participant("s6b_17", "product", "17", e, name="bisarylated allene 17"),
]
records.append(record(
    "scheme6_bisarylation_general", "general_scheme", [4], p,
    conditions=[field("solvent", "DMF", e), field("temperature", {"number": 80, "unit": "°C"}, e), field("atmosphere", "N2", e), field("time", None)],
    outcomes=[field("yield", None, targets=["s6b_17"])],
    notes=["The Scheme 6 lower arrow is a generic R/Ar transformation; no individual scope rows are shown."],
    unresolved=["Yield, time, individual aryl groups, and exact substrate structures are not supplied."],
))

e = ev(3, 4)
p = [participant("s6m_phi", "reactant", "PhI", e, name="iodobenzene"), participant("s6m_13", "reactant", "13", e), participant("s6m_phpdi", "product", "PhPdI", e), participant("s6m_15", "product", "15", e), participant("s6m_14", "product", "14", e)]
records.append(record(
    "scheme6_beta_h_elimination_mechanism", "mechanism", [3, 4], p,
    conditions=[field("operation", "oxidative addition to PhPdI, carbopalladation to 15, then beta-H elimination to 14", e)],
    notes=["The prose says the reaction may proceed through vinylic palladium intermediate 15."],
    unresolved=["This proposed mechanism is not an independent experiment and catalyst ligands are abbreviated."],
))

# Scheme 7: retain four distinct condition sets instead of merging them.
scheme7 = [
    ("A", "19", [("Pd(PPh3)4", "catalyst", {"number": 5, "unit": "mol%"}), ("K2CO3", "reagent", {"number": 4, "unit": "equiv"}), ("n-Bu4NBr", "reagent", {"number": 10, "unit": "mol%"}), ("MeCN", "solvent", None)]),
    ("B", "19", [("Pd(PPh3)4", "catalyst", {"number": 5, "unit": "mol%"}), ("K2CO3", "reagent", {"number": 4, "unit": "equiv"}), ("THF", "solvent", None)]),
    ("C", "20", [("Pd(PPh3)4", "catalyst", {"number": 5, "unit": "mol%"}), ("NaH", "reagent", {"number": 1.1, "unit": "equiv"}), ("DMSO", "solvent", None)]),
    ("D", "20", [("Pd(PPh3)4", "catalyst", {"number": 5, "unit": "mol%"}), ("NaOH", "reagent", {"number": 1.1, "unit": "equiv"}), ("DMF", "solvent", None)]),
]
for letter, product_label, agents in scheme7:
    e = ev(4)
    p = [participant(f"s7{letter}_18", "reactant", "18", e, name="generic 2-(2',3'-allenyl)malonate"), participant(f"s7{letter}_rx", "reactant", "R1-X", e, name="generic organic halide")]
    for idx, (label, role, amount) in enumerate(agents):
        p.append(participant(f"s7{letter}_a{idx}", role, label, e, amounts=[qty("loading" if amount and amount["unit"] == "mol%" else "equivalents", amount, e)] if amount else []))
    p.append(participant(f"s7{letter}_{product_label}", "product", product_label, e, name="vinylic cyclopropane 19" if product_label == "19" else "cyclopentene 20"))
    solvent = agents[-1][0]
    records.append(record(
        f"scheme7_condition_{letter.lower()}", "general_scheme", [4], p,
        conditions=[field("solvent", solvent, e), field("temperature", None), field("time", None)],
        outcomes=[field("yield", None, targets=[f"s7{letter}_{product_label}"])],
        notes=[f"Scheme 7 condition {letter} is kept separate from conditions A-D; the prose assigns conditions A/B to product family 19 and C/D to product family 20."],
        unresolved=["Generic R groups and organic halide identity are unspecified; no temperature, time, or yield is given for this condition set."],
    ))

# Scheme 8, direct condition C example: page 4 prose + page 5 drawing.
e = ev(4, 5)
p = [
    participant("s8a_18a", "reactant", "18a", e),
    participant("s8a_phi", "reactant", "PhI", e, name="iodobenzene"),
    participant("s8a_pd", "catalyst", "Pd(PPh3)4", e, amounts=[qty("catalyst_loading", {"number": 5, "unit": "mol%"}, e)]),
    participant("s8a_nah", "reagent", "NaH", e, amounts=[qty("equivalents", {"number": 1.1, "unit": "equiv"}, e)]),
    participant("s8a_dmso", "solvent", "DMSO", e),
    participant("s8a_20a", "product", "20a", e, name="cyclopentene derivative 20a"),
]
records.append(record(
    "scheme8_condition_c_20a", "literature_example", [4, 5], p,
    conditions=[field("solvent", "DMSO", e), field("temperature", "reflux", e), field("time", None)],
    outcomes=[field("yield", {"number": 88, "unit": "%"}, e, ["s8a_20a"]), field("selectivity", "20a formed highly selectively", e, ["s8a_20a"]), field("yield_measurement_basis", None, targets=["s8a_20a"])],
    notes=["The page 4 prose identifies this as the reaction of 18a with phenyl iodide under condition C; Scheme 8 on page 5 supplies the drawn conditions."],
    unresolved=["Reaction time and yield measurement basis are not stated; the complete drawn structure of 18a/20a remains unverified."],
))

# Scheme 8 staged catalyst/base experiment.
e = ev(4, 5)
p = [
    participant("s8b_18a", "reactant", "18a", e), participant("s8b_phi", "reactant", "PhI", e, name="iodobenzene"),
    participant("s8b_pd", "catalyst", "Pd(PPh3)4", e, amounts=[qty("catalyst_loading", {"number": 20, "unit": "mol%"}, e)]),
    participant("s8b_nah", "reagent", "NaH", e, amounts=[qty("equivalents", {"number": 1.1, "unit": "equiv"}, e)]),
    participant("s8b_dmso", "solvent", "DMSO", e), participant("s8b_19a", "product", "19a", e, name="vinylic cyclopropane 19a"),
]
steps = [
    {"step_id": "step1_palladium_only", "participant_ids": ["s8b_18a", "s8b_phi", "s8b_pd", "s8b_dmso"], "conditions": [field("solvent", "DMSO", e), field("temperature", {"number": 85, "unit": "°C"}, e), field("time", {"number": 6, "unit": "h"}, e)]},
    {"step_id": "step2_after_NaH_addition", "participant_ids": ["s8b_nah", "s8b_19a"], "conditions": [field("operation", "NaH added after the initial palladium-only stage", e), field("temperature", {"number": 85, "unit": "°C"}, e), field("time", {"number": 4.5, "unit": "h"}, e)]},
]
records.append(record(
    "scheme8_staged_nah_19a", "literature_example", [4, 5], p, steps=steps,
    outcomes=[field("yield", {"number": 29, "unit": "%"}, e, ["s8b_19a"]), field("selectivity", "19a as the only product", e, ["s8b_19a"]), field("yield_measurement_basis", None, targets=["s8b_19a"])],
    notes=["The 6 h and 4.5 h stages are preserved separately rather than summed."],
    unresolved=["Yield measurement basis and workup are absent; full structures remain unverified."],
))

# Scheme 8 mechanistic interpretation of the staged experiment.
e = ev(5)
p = [participant("s8m_18a", "reactant", "18a", e), participant("s8m_anti21a", "product", "anti-21a", e), participant("s8m_syn21a", "product", "syn-21a", e), participant("s8m_syn22a", "product", "syn-22a", e), participant("s8m_19a", "product", "19a", e)]
records.append(record(
    "scheme8_intermediate_isomerization", "mechanism", [5], p,
    conditions=[field("operation", "18a -> anti-21a -> syn-21a -> syn-22a after deprotonation -> cyclic allylation product 19a", e)],
    notes=["The prose explicitly introduces this sequence as the authors' reasoning; intermediates are not presented as isolated experiments."],
    unresolved=["Ligand identity is abbreviated as L and intermediate structures are not independently verified."],
))

# Page 5, Scheme 9 generic three-component cyclization.
e = ev(5)
p = [
    participant("s9_allene", "reactant", "generic allenyl malonate", e), participant("s9_imine", "reactant", "generic N-tosyl imine", e),
    participant("s9_pd", "catalyst", "Pd(PPh3)4", e, amounts=[qty("catalyst_loading", {"number": 5, "unit": "mol%"}, e)]),
    participant("s9_base", "reagent", "K2CO3", e, amounts=[qty("equivalents", {"number": 4, "unit": "equiv"}, e)]),
    participant("s9_thf", "solvent", "THF", e), participant("s9_dioxane", "solvent", "dioxane", e),
    participant("s9_23", "product", "23", e, name="2,5-cis pyrrolidine 23"),
]
records.append(record(
    "scheme9_pyrrolidine_general", "general_scheme", [5], p,
    conditions=[field("solvent", "THF or dioxane", e), field("temperature", None), field("time", None)],
    outcomes=[field("yield", None, targets=["s9_23"]), field("stereoselectivity", "high; 2,5-cis product", e, ["s9_23"])],
    notes=["E is defined in the figure as COOMe; R1 is generic. The review cites reference 13."],
    unresolved=["No individual R1 scope entries, temperature, time, or yields are shown."],
))

# Scheme 10 first reaction: page 5 prose and page 6 figure.
e = ev(5, 6)
p = [
    participant("s10a_24", "reactant", "24", e, name="2-methyl-3,4-pentadienyl toluenesulfonamide"),
    participant("s10a_phi", "reactant", "PhI", e, name="iodobenzene", amounts=[qty("equivalents", {"number": 1.5, "unit": "equiv"}, e)]),
    participant("s10a_pd", "catalyst", "Pd(PPh3)4", e, amounts=[qty("catalyst_loading", {"number": 5, "unit": "mol%"}, e)]),
    participant("s10a_base", "reagent", "K2CO3", e, amounts=[qty("equivalents", {"number": 4, "unit": "equiv"}, e)]),
    participant("s10a_dmf", "solvent", "DMF", e), participant("s10a_25", "product", "25", e, name="azetidine 25"), participant("s10a_26", "product", "26", e, name="tetrahydropyridine 26"),
]
records.append(record(
    "scheme10_substrate24_products25_26", "literature_example", [5, 6], p,
    conditions=[field("solvent", "DMF", e), field("temperature", {"number": 70, "unit": "°C"}, e), field("time", None)],
    outcomes=[field("yield", None, targets=["s10a_25"]), field("yield", None, targets=["s10a_26"]), field("product_ratio", None, targets=["s10a_25", "s10a_26"])],
    notes=["The page 5 prose identifies products 25 and 26 and cites references 14 and 15; Scheme 10 supplies the conditions."],
    unresolved=["Time, product-specific yields, ratio, and yield bases are not supplied."],
))

# Scheme 10 second reaction: specific 28 -> 29.
e = ev(6)
p = [
    participant("s10b_28", "reactant", "28", e, name="N-(2-methyl-3-butyl-3,4-pentadienyl)toluenesulfonamide"),
    participant("s10b_phi", "reactant", "PhI", e, name="iodobenzene", amounts=[qty("equivalents", {"number": 1.5, "unit": "equiv"}, e)]),
    participant("s10b_pd", "catalyst", "Pd(PPh3)4", e, amounts=[qty("catalyst_loading", {"number": 5, "unit": "mol%"}, e)]),
    participant("s10b_base", "reagent", "K2CO3", e, amounts=[qty("equivalents", {"number": 4, "unit": "equiv"}, e)]),
    participant("s10b_dmf", "solvent", "DMF", e), participant("s10b_29", "product", "29", e, name="2,3-dihydropyrrole 29"),
]
records.append(record(
    "scheme10_substrate28_product29", "literature_example", [6], p,
    conditions=[field("solvent", "DMF", e), field("temperature", {"number": 70, "unit": "°C"}, e), field("time", {"number": 7.5, "unit": "h"}, e)],
    outcomes=[field("yield", {"number": 78, "unit": "%"}, e, ["s10b_29"]), field("selectivity", "29 as the only product", e, ["s10b_29"]), field("yield_measurement_basis", None, targets=["s10b_29"])],
    notes=["This is the specific n-butyl/2-methyl substrate example within Scheme 10, cited to reference 14."],
    unresolved=["Yield measurement basis, atmosphere, workup, and purification are absent."],
))

# Scheme 10 third reaction: generic 30 -> 31 + 32.
e = ev(6)
p = [
    participant("s10c_30", "reactant", "30", e, name="3-butyl-3,4-pentadienyl toluenesulfonamide 30"),
    participant("s10c_ari", "reactant", "ArI", e, name="aryl iodide", amounts=[qty("equivalents", {"number": 1.5, "unit": "equiv"}, e)]),
    participant("s10c_pd", "catalyst", "Pd(PPh3)4", e, amounts=[qty("catalyst_loading", {"number": 5, "unit": "mol%"}, e)]),
    participant("s10c_base", "reagent", "K2CO3", e, amounts=[qty("equivalents", {"number": 4, "unit": "equiv"}, e)]),
    participant("s10c_solvent", "solvent", "unspecified solvent", e), participant("s10c_31", "product", "31", e, name="2,3-dihydropyrrole 31"), participant("s10c_32", "product", "32", e, name="2-methylenetetrahydropyrrole 32"),
]
records.append(record(
    "scheme10_substrate30_products31_32", "general_scheme", [6], p,
    conditions=[field("solvent", None), field("temperature", {"number": 70, "unit": "°C"}, e), field("time", None)],
    outcomes=[field("yield", None, targets=["s10c_31"]), field("yield", None, targets=["s10c_32"]), field("product_ratio", "mixture", e, ["s10c_31", "s10c_32"])],
    notes=["The arrow says 'Solvent' without naming it; different ArI substrates give mixtures of 31 and 32."],
    unresolved=["Solvent identity, reaction time, individual aryl groups, yields, and product ratios are missing."],
))

# Scheme 10 lower mechanistic branches.
e = ev(6)
p = [participant("s10m_ari", "reactant", "ArI", e), participant("s10m_33", "reactant", "33", e), participant("s10m_pdar", "product", "PdAr", e), participant("s10m_34", "product", "pi-allylpalladium intermediate 34", e), participant("s10m_29", "product", "29", e), participant("s10m_31", "product", "31", e), participant("s10m_32", "product", "32", e)]
records.append(record(
    "scheme10_nucleometallation_mechanism", "mechanism", [6], p,
    conditions=[field("operation", "ArI -> PdAr; nucleometallation with 33 -> intermediate 34; reductive elimination gives 31/32 for R1=n-C4H9,R2=H or 29 for R1=n-C4H9,R2=Me", e)],
    notes=["The prose states that the reaction may proceed through intermediate 34; the branches are mechanistic, not separate isolated experiments."],
    unresolved=["The aryl group, palladium ligation, and structures of generic intermediates are not fully specified."],
))


records_path = Path(__file__).with_name("pages_0001_0006_records.json")
records_path.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")

record_ids_by_page = {page: [] for page in range(1, 7)}
for item in records:
    for page in range(1, 7):
        if f"{DOC}:page{page}:image" in item["evidence_ids"]:
            record_ids_by_page[page].append(item["record_id"])

coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1,
            "state": "attempted",
            "regions": [
                {"region": "top and middle: title, abstract, introduction", "finding": "No individual experiment; review framing and scope only.", "evidence_ids": ev(1)},
                {"region": "bottom: Scheme 1", "finding": "Generic mechanism with two alternative carbometallation insertion pathways to species 1 and 2.", "evidence_ids": ev(1)},
            ],
            "record_ids": record_ids_by_page[1],
            "unresolved": ["Generic R and M labels prevent complete structures; no experimental conditions are present."],
        },
        {
            "page": 2,
            "state": "attempted",
            "regions": [
                {"region": "upper half: Scheme 2", "finding": "Two cited literature reactions: an upper Tsuji-type allene carbopalladation with no yield and a lower Cheng reaction giving 53% and Z/E 1:1.", "evidence_ids": ev(2)},
                {"region": "lower half: Scheme 3 and accompanying prose", "finding": "One reaction of 3 and 4 under Cheng-type conditions gives products E-6 and E-7, each 16%.", "evidence_ids": ev(2)},
            ],
            "record_ids": record_ids_by_page[2],
            "unresolved": ["Several catalyst quantities, reaction times, yield bases, and visually drawn structures are not fully specified or independently verified."],
        },
        {
            "page": 3,
            "state": "attempted",
            "regions": [
                {"region": "top: Scheme 4", "finding": "Generic cited scope: aryl halides plus 3,4-alkadienoates give 4-aryl-2,4-alkadienoates in 44-85% under Pd(PPh3)4/Ag2CO3.", "evidence_ids": ev(3)},
                {"region": "middle: Scheme 5", "finding": "Grigg literature example and its depicted 5-exo/3-exo palladium mechanism; product yield and second-stage details are absent.", "evidence_ids": ev(3)},
                {"region": "bottom prose introducing Scheme 6", "finding": "Text identifies the 13 + PhI -> 14 Heck-type reaction and bisarylation of 16; drawing/conditions continue on page 4.", "evidence_ids": ev(3)},
            ],
            "record_ids": record_ids_by_page[3],
            "unresolved": ["Scheme 4 is a range summary rather than row-level scope; Scheme 5 lacks yield and CO/MeOH quantities; Scheme 6 must be read with page 4."],
        },
        {
            "page": 4,
            "state": "attempted",
            "regions": [
                {"region": "top: Scheme 6", "finding": "Specific 13 + PhI -> 14 reaction gives 42%; lower generic 16 + ArI -> 17 bisarylation has no yield; proposed beta-H-elimination mechanism is depicted.", "evidence_ids": ev(4)},
                {"region": "middle and bottom: Scheme 7 plus following prose", "finding": "Four distinct condition sets A-D are enumerated; A/B map to cyclopropanes 19, C/D to cyclopentenes 20. Prose introduces specific 18a + PhI examples continued on page 5.", "evidence_ids": ev(4)},
            ],
            "record_ids": record_ids_by_page[4],
            "unresolved": ["Scheme 7 has generic R groups and no row-level yields/times/temperatures; the specific examples require page 5 for drawn conditions and results."],
        },
        {
            "page": 5,
            "state": "attempted",
            "regions": [
                {"region": "top and middle: Scheme 8", "finding": "Direct condition C gives 20a in 88%; staged palladium-only then NaH experiment gives 19a in 29%, with two separate timed stages. The anti/syn intermediate sequence is mechanistic.", "evidence_ids": ev(5)},
                {"region": "lower middle: Scheme 9", "finding": "Generic three-component coupling/cyclization to 2,5-cis pyrrolidines 23 under Pd(PPh3)4/K2CO3 in THF or dioxane; no yield/time/temperature shown.", "evidence_ids": ev(5)},
                {"region": "bottom prose", "finding": "Introduces coupling/cyclization of substrate 24 with PhI to products 25 and 26; the reaction drawing continues on page 6.", "evidence_ids": ev(5)},
            ],
            "record_ids": record_ids_by_page[5],
            "unresolved": ["Yield bases and full experimental operations/workups are absent; Scheme 9 is generic; Scheme 10 conditions require page 6."],
        },
        {
            "page": 6,
            "state": "attempted",
            "regions": [
                {"region": "top: Scheme 10 first arrow", "finding": "Specific 24 + PhI coupling gives products 25 and 26 under Pd(PPh3)4/K2CO3 in DMF at 70 °C; yields, ratio, and time are not shown.", "evidence_ids": ev(6)},
                {"region": "middle: Scheme 10 second and third arrows", "finding": "Specific 28 + PhI gives only 29 in 78% after 7.5 h; generic 30 + ArI gives a mixture of 31 and 32 with solvent identity and yields absent.", "evidence_ids": ev(6)},
                {"region": "bottom: Scheme 10 mechanistic branches", "finding": "Proposed PdAr nucleometallation through intermediate 34 branches to 31/32 or 29 depending on R2; not an independent experiment.", "evidence_ids": ev(6)},
            ],
            "record_ids": record_ids_by_page[6],
            "unresolved": ["No product-specific yields/ratio for 25/26 or 31/32; solvent for 30 is printed only as generic 'Solvent'; all detailed workups are unavailable."],
        },
    ],
}
coverage_dir = BASE / "coverage"
coverage_dir.mkdir(parents=True, exist_ok=True)
(coverage_dir / "pages_0001_0006.json").write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

tasks_path = BASE / "tasks.json"
tasks = json.loads(tasks_path.read_text())
covered_task_ids = {f"{DOC}:page{page}:text" for page in range(1, 7)}
for task in tasks:
    if task.get("task_id") in covered_task_ids:
        task["state"] = "attempted"
        task["reason"] = "Page text and original rendered page image were inspected; see coverage/pages_0001_0006.json."
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"records": len(records), "records_path": str(records_path), "coverage_pages": len(coverage["pages"])}, ensure_ascii=False))
