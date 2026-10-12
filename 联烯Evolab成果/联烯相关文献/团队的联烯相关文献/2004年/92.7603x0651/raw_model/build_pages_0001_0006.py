#!/usr/bin/env python3
"""Build raw, evidence-linked records for PDF pages 1-6 of doc_26e794dd8e61e4bf."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / "runs/current"
DOC = "doc_26e794dd8e61e4bf"


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def ev(*pages):
    result = []
    for page in pages:
        result.extend([f"{DOC}:page{page}:text", f"{DOC}:page{page}:image"])
    return result


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


def participant(entity_id, role, evidence, *, label=None, name=None, smiles=None, amounts=()):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence),
        "smiles": fact(smiles, evidence),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": list(amounts),
    }


def step(step_id, participants, conditions=()):
    return {"step_id": step_id, "participant_ids": list(participants), "conditions": list(conditions)}


def record(suffix, kind, evidence, *, participants=(), steps=(), outcomes=(), notes=(), unresolved=()):
    return {
        "record_id": f"{DOC}:{suffix}",
        "document_id": DOC,
        "source_reaction_id": suffix,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": list(evidence),
        "participants": list(participants),
        "steps": list(steps),
        "outcomes": list(outcomes),
        "notes": [fact(value, evidence) for value in notes],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": list(unresolved),
        },
    }


def literature_unresolved(*extra):
    return [
        "This review does not supply a complete original-paper procedure or explicitly associated SI.",
        *extra,
    ]


records = []

# Page 1: two explicitly drawn generic mechanistic pathways.
e = ev(1)
for suffix, path_note, intermediate in [
    ("scheme1_path1_carbometallation_allylation", "Path 1: intermolecular carbometallation followed by intramolecular allylation.", "pi-allyl metal intermediate"),
    ("scheme1_path2_oxymetallation_reductive_elimination", "Path 2: cyclic oxymetallation followed by reductive elimination.", "cyclic oxymetalated intermediate"),
]:
    ps = [
        participant("allenoic_acid", "reactant", e, name="generic 2,3-allenoic acid"),
        participant("MY", "unspecified_agent", e, label="MY", name="generic organometallic reagent"),
        participant("intermediate", "unspecified_agent", e, name=intermediate),
        participant("butenolide", "product", e, name="generic substituted butenolide"),
    ]
    records.append(record(
        suffix, "mechanism", e, participants=ps,
        steps=[step("metalation", ["allenoic_acid", "MY", "intermediate"]), step("ring_formation", ["intermediate", "butenolide"])],
        notes=[path_note],
        unresolved=["Generic R groups and MY are not fully specified; this is a mechanistic scheme, not an individual experiment."],
    ))

# Scheme 2 spans the introductory paragraph on page 1 and the arrow on page 2.
e = ev(1, 2)
ps = [
    participant("acid_1", "reactant", e, label="1", name="generic 2,3-allenoic acid"),
    participant("organic_halide", "reactant", e, label="R2X", name="aryl or 1-alkenyl halide"),
    participant("pd_pph3_4", "catalyst", e, name="Pd(PPh3)4", amounts=[field("catalyst_loading", "catalytic amount", e)]),
    participant("ag2co3", "catalyst", e, name="Ag2CO3", smiles="[Ag+].[Ag+].[O-]C([O-])=O", amounts=[field("catalyst_loading", "catalytic amount", e)]),
    participant("k2co3", "reagent", e, name="K2CO3", smiles="[K+].[K+].[O-]C([O-])=O"),
    participant("mecn", "solvent", e, name="MeCN", smiles="CC#N"),
    participant("butenolide_3", "product", e, label="3", name="beta-aryl or beta-(1-alkenyl)butenolide"),
]
records.append(record(
    "scheme2_pd_ag_coupling_cyclization", "literature_example", e, participants=ps,
    steps=[step("coupling_cyclization", [p["entity_id"] for p in ps[:-1]], [field("temperature", {"number": 70, "unit": "°C"}, e), field("time", None, e), field("solvent", "MeCN", e)])],
    outcomes=[field("yield", {"minimum": 59, "maximum": 79, "unit": "%", "raw_text": "59-79 %"}, e, ["butenolide_3"]), field("yield_measurement_basis", None, e, ["butenolide_3"])],
    notes=["The review states that catalytic Ag+ is key and may form cyclic silver intermediate 2."],
    unresolved=literature_unresolved("Catalyst loadings, reaction time, workup, purification, and yield basis are not reported here; structures are generic R-group drawings."),
))

# Scheme 3/text: three distinct solid-phase cleavage protocols, kept separate by linker/conditions.
e = ev(2)
cleavages = [
    ("scheme3_carboxyl_linker_alcl3_cleavage", "carboxyl linkage", [("alcl3", "AlCl3", "Cl[Al](Cl)Cl")]),
    ("scheme3_ether_linker_znbr2_acetyl_bromide_cleavage", "ether/benzylic ether linkage", [("znbr2", "ZnBr2", "Br[Zn]Br"), ("acetyl_bromide", "CH3COBr", "CC(=O)Br")]),
    ("scheme3_thp_linker_tfa_meoh_cleavage", "THP linkage", [("tfa", "TFA", "O=C(O)C(F)(F)F"), ("meoh", "MeOH", "CO")]),
]
for suffix, linker, reagents in cleavages:
    ps = [
        participant("polymer_aryl_iodide", "reactant", e, name=f"polymer-bound aryl iodide with {linker}"),
        participant("allenoic_acid", "reactant", e, name="generic 2,3-allenoic acid"),
        *[participant(pid, "reagent", e, name=name, smiles=smi) for pid, name, smi in reagents],
        participant("butenolide_4", "product", e, label="4", name="solid-phase-derived butenolide"),
    ]
    reagent_ids = [pid for pid, _, _ in reagents]
    records.append(record(
        suffix, "literature_example", e, participants=ps,
        steps=[
            step("coupling_cyclization", ["polymer_aryl_iodide", "allenoic_acid"], [field("temperature", None, e), field("time", None, e)]),
            step("selective_polymer_cleavage", reagent_ids + ["butenolide_4"], [field("temperature", None, e), field("time", None, e)]),
        ],
        outcomes=[field("yield", None, e, ["butenolide_4"]), field("yield_measurement_basis", None, e, ["butenolide_4"])],
        notes=[f"Scheme 3/text identifies selective removal of the {linker}; coupling-cyclization conditions are not shown."],
        unresolved=literature_unresolved("The substrate, linker substituents, quantities, temperatures, times, yields, workup, and purification are not specified in this review."),
    ))

# Scheme 4: specific chiral substrate with a maximum product ee stated in prose.
e = ev(2)
ps = [
    participant("Sa_5", "reactant", e, label="Sa-(+)-5", name="Sa-(+)-2-methyl-4-phenyl-2,3-butadienoic acid", smiles="CC(=C=Cc1ccccc1)C(=O)O", amounts=[field("enantiomeric_excess", {"number": 96, "unit": "%"}, e)]),
    participant("phi", "reactant", e, name="PhI", smiles="Ic1ccccc1"),
    participant("pd2dba3_chcl3", "catalyst", e, name="Pd2(dba)3·CHCl3", amounts=[field("catalyst_loading", {"number": 2.5, "unit": "mol%"}, e)]),
    participant("pph3", "reagent", e, name="PPh3", smiles="c1ccc(P(c2ccccc2)c2ccccc2)cc1", amounts=[field("reagent_loading", {"number": 10, "unit": "mol%"}, e)]),
    participant("toluene", "solvent", e, name="toluene", smiles="Cc1ccccc1"),
    participant("S_6", "product", e, label="S-(+)-6", name="chiral phenyl/methyl-substituted butenolide"),
]
records.append(record(
    "scheme4_Sa5_phi_low_ee", "literature_example", e, participants=ps,
    steps=[step("pd_catalyzed_coupling", [p["entity_id"] for p in ps[:-1]], [field("solvent", "toluene", e), field("temperature", None, e), field("time", None, e)])],
    outcomes=[field("yield", None, e, ["S_6"]), field("enantiomeric_excess", {"number": 60, "unit": "%", "raw_text": "highest ee of 60 %"}, e, ["S_6"]), field("yield_measurement_basis", None, e, ["S_6"])],
    notes=["The figure describes the product as low ee; the prose gives the highest ee as 60%."],
    unresolved=literature_unresolved("Temperature, time, yield, workup, purification, and yield basis are absent; the candidate reactant SMILES does not encode axial stereochemistry."),
))

# Page 3 Scheme 5 is explicitly a proposed catalytic/chirality-transfer cycle.
e = ev(3)
records.append(record(
    "scheme5_oxypalladation_cycle", "mechanism", e,
    participants=[
        participant("allenoate_salt", "reactant", e, name="generic chiral 2,3-allenoate salt"),
        participant("r4x", "reactant", e, label="R4X", name="generic organic halide"),
        participant("pd0l", "catalyst", e, label="Pd(0)L"),
        participant("butenolide", "product", e, name="generic chiral butenolide"),
    ],
    notes=["Proposed coordination-directed oxypalladation/reductive-elimination cycle with highly efficient chirality transfer."],
    unresolved=["Generic R groups, ligand, base/counterion, and halide are not fully specified; this is a mechanism rather than an individual experiment."],
))

# Scheme 6 contains two successive experimental stages and is separated accordingly.
e = ev(3)
ps = [
    participant("Sa_5", "reactant", e, label="Sa-(+)-5", name="Sa-(+)-2-methyl-4-phenyl-2,3-butadienoic acid", smiles="CC(=C=Cc1ccccc1)C(=O)O", amounts=[field("enantiomeric_excess", {"number": 97, "unit": "%"}, e)]),
    participant("dipea", "reactant", e, name="i-Pr2NEt", smiles="CCN(C(C)C)C(C)C", amounts=[field("stoichiometric_ratio", "1:1 acid/base salt", e)]),
    participant("ethyl_acetate", "solvent", e, name="ethyl acetate", smiles="CCOC(C)=O"),
    participant("salt_7", "product", e, label="Sa-(+)-7", name="1:1 diisopropylethylammonium allenoate salt"),
]
records.append(record(
    "scheme6_prepare_salt7", "literature_example", e, participants=ps,
    steps=[step("salt_formation", ["Sa_5", "dipea", "ethyl_acetate"], [field("solvent", "ethyl acetate", e), field("temperature", "room temperature", e), field("time", None, e)])],
    outcomes=[field("yield", None, e, ["salt_7"]), field("enantiomeric_excess", {"number": 97, "unit": "%"}, e, ["salt_7"]), field("yield_measurement_basis", None, e, ["salt_7"])],
    notes=["The text explicitly identifies the isolated material as the 1:1 salt of Sa-(+)-5 and i-Pr2NEt."],
    unresolved=literature_unresolved("Reaction time, isolated amount/yield, workup, purification, and yield basis are not supplied."),
))

ps = [
    participant("salt_7", "reactant", e, label="Sa-(+)-7", name="diisopropylethylammonium allenoate salt", amounts=[field("enantiomeric_excess", {"number": 97, "unit": "%"}, e)]),
    participant("phi", "reactant", e, name="PhI", smiles="Ic1ccccc1"),
    participant("pd2dba3_chcl3", "catalyst", e, name="Pd2(dba)3·CHCl3", amounts=[field("catalyst_loading", {"number": 5, "unit": "mol%"}, e)]),
    participant("pph3", "reagent", e, name="PPh3", smiles="c1ccc(P(c2ccccc2)c2ccccc2)cc1", amounts=[field("reagent_loading", {"number": 20, "unit": "mol%"}, e)]),
    participant("toluene", "solvent", e, name="toluene", smiles="Cc1ccccc1"),
    participant("S_8", "product", e, label="S-(+)-8", name="chiral phenyl/methyl-substituted butenolide"),
]
records.append(record(
    "scheme6_salt7_phi_coupling", "literature_example", e, participants=ps,
    steps=[step("pd_catalyzed_coupling", [p["entity_id"] for p in ps[:-1]], [field("solvent", "toluene", e), field("temperature", {"number": 5, "unit": "°C"}, e), field("time", {"number": 60, "unit": "h"}, e)])],
    outcomes=[field("yield", {"number": 62, "unit": "%"}, e, ["S_8"]), field("enantiomeric_excess", {"number": 91, "unit": "%"}, e, ["S_8"]), field("yield_measurement_basis", None, e, ["S_8"])],
    unresolved=literature_unresolved("Scale, workup, purification, and yield measurement basis are not reported in the review."),
))

ps = [
    participant("cinchonidine_salt", "reactant", e, name="cinchonidine salt of Sa-(+)-5"),
    participant("phi", "reactant", e, name="PhI", smiles="Ic1ccccc1"),
    participant("tbab", "catalyst", e, name="TBAB", amounts=[field("catalyst_loading", "phase-transfer catalyst; amount not stated", e)]),
    participant("butenolide", "product", e, name="corresponding chiral butenolide"),
]
records.append(record(
    "scheme6_text_cinchonidine_salt_tbab_variant", "literature_example", e, participants=ps,
    steps=[step("phase_transfer_coupling", ["cinchonidine_salt", "phi", "tbab"], [field("temperature", None, e), field("time", None, e)])],
    outcomes=[field("yield", None, e, ["butenolide"]), field("enantiomeric_excess", None, e, ["butenolide"]), field("yield_measurement_basis", None, e, ["butenolide"])],
    notes=["The review says the corresponding cinchonidine salt should be reacted in the presence of TBAB as phase-transfer catalyst."],
    unresolved=literature_unresolved("The exact substrate/product structure, catalyst system, quantities, solvent, temperature, time, yield, and ee are not supplied for this variant."),
))

# Scheme 7 generic allylic-halide scope.
e = ev(3)
ps = [
    participant("allenoic_acid", "reactant", e, name="generic 2,3-allenoic acid"),
    participant("allylic_halide", "reactant", e, name="generic allylic halide"),
    participant("pdcl2", "catalyst", e, name="PdCl2", amounts=[field("catalyst_loading", {"number": 5, "unit": "mol%"}, e)]),
    participant("dma", "solvent", e, name="DMA", smiles="CC(=O)N(C)C"),
    participant("butenolide_9", "product", e, label="9", name="generic beta-allylic butenolide"),
]
records.append(record(
    "scheme7_pdcl2_allylic_halide_coupling", "literature_example", e, participants=ps,
    steps=[step("coupling_cyclization", [p["entity_id"] for p in ps[:-1]], [field("solvent", "DMA", e), field("temperature", {"number": 50, "unit": "°C"}, e), field("time", None, e)])],
    outcomes=[field("yield", {"minimum": 69, "maximum": 95, "unit": "%", "raw_text": "69-95 %"}, e, ["butenolide_9"]), field("yield_measurement_basis", None, e, ["butenolide_9"])],
    unresolved=literature_unresolved("Substrate-specific rows, scale, time, workup, purification, and yield basis are not shown; structures are generic."),
))

# Page 4 Scheme 8: the explicitly chiral allyl-bromide variant.
e = ev(4)
ps = [
    participant("chiral_allenoic_acid", "reactant", e, name="optically active generic 2,3-allenoic acid"),
    participant("allyl_bromide", "reactant", e, name="allyl bromide", smiles="C=CCBr"),
    participant("pdcl2", "catalyst", e, name="PdCl2", amounts=[field("catalyst_loading", {"number": 5, "unit": "mol%"}, e)]),
    participant("dma", "solvent", e, name="DMA", smiles="CC(=O)N(C)C"),
    participant("chiral_butenolide", "product", e, name="chiral beta-allylic butenolide"),
]
records.append(record(
    "scheme8_chiral_allenoic_acid_allyl_bromide", "literature_example", e, participants=ps,
    steps=[step("coupling_cyclization", [p["entity_id"] for p in ps[:-1]], [field("solvent", "DMA", e), field("temperature", None, e), field("time", None, e)])],
    outcomes=[field("yield", None, e, ["chiral_butenolide"]), field("enantiomeric_excess", None, e, ["chiral_butenolide"]), field("yield_measurement_basis", None, e, ["chiral_butenolide"])],
    notes=["The text reports formation without obvious loss of chirality but gives no numeric ee on this page."],
    unresolved=literature_unresolved("Substituents, scale, temperature, time, yield, numeric ee, workup, purification, and yield basis are absent."),
))

# Scheme 9 reaction and its separately depicted pi-bond-walking mechanism.
e = ev(4)
ps = [
    participant("allenoic_acid", "reactant", e, name="generic phenyl-substituted 2,3-allenoic acid"),
    participant("alkenyl_bromide", "reactant", e, name="generic non-allylic (omega-1)-alkenyl bromide"),
    participant("pd_oac2", "catalyst", e, name="Pd(OAc)2", amounts=[field("catalyst_loading", {"number": 5, "unit": "mol%"}, e)]),
    participant("dmf", "solvent", e, name="DMF", smiles="CN(C)C=O"),
    participant("alkenyl_butenolide", "product", e, name="beta-(omega-1)-alkenyl butenolide"),
]
records.append(record(
    "scheme9_alkenyl_bromide_pi_walk_coupling", "literature_example", e, participants=ps,
    steps=[step("coupling_and_pi_bond_walk", [p["entity_id"] for p in ps[:-1]], [field("solvent", "DMF", e), field("temperature", {"number": 100, "unit": "°C"}, e), field("time", None, e)])],
    outcomes=[field("yield", {"minimum": 18, "maximum": 58, "unit": "%", "raw_text": "18-58 %"}, e, ["alkenyl_butenolide"]), field("yield_measurement_basis", None, e, ["alkenyl_butenolide"])],
    notes=["The generic scope states n = 2-14."],
    unresolved=literature_unresolved("Substrate-specific entries, scale, time, workup, purification, and yield basis are not supplied."),
))
records.append(record(
    "scheme9_pi_bond_walking_mechanism", "mechanism", e,
    participants=[
        participant("initial_palladium_intermediate", "unspecified_agent", e, name="initial alkylpalladium/bromide intermediate"),
        participant("walked_palladium_intermediate", "unspecified_agent", e, name="pi-bond-walked palladium intermediate"),
        participant("alkenyl_butenolide", "product", e, name="beta-(omega-1)-alkenyl butenolide"),
    ],
    notes=["The lower part of Scheme 9 depicts a generic pi-bond-walking sequence before product formation."],
    unresolved=["Ligand identity, elementary-step conditions, and generic R/n values are unspecified; this is a proposed pathway, not a separate experiment."],
))

# Scheme 10 bis-butenolide synthesis.
e = ev(4)
ps = [
    participant("allenoic_acid", "reactant", e, name="generic 2,3-allenoic acid"),
    participant("propyl_iodide", "reactant", e, name="C3H7I", smiles="CCCI", amounts=[field("reagent_equivalents", {"number": 5, "unit": "equiv"}, e)]),
    participant("pdcl2", "catalyst", e, name="PdCl2", amounts=[field("catalyst_loading", {"number": 5, "unit": "mol%"}, e)]),
    participant("dma", "solvent", e, name="DMA", smiles="CC(=O)N(C)C"),
    participant("bibutenolide_10", "product", e, label="10", name="generic bi-butenolide"),
]
records.append(record(
    "scheme10_alkyl_iodide_bibutenolide", "literature_example", e, participants=ps,
    steps=[step("oxidative_coupling_cyclization", [p["entity_id"] for p in ps[:-1]], [field("solvent", "DMA", e), field("temperature", {"number": 80, "unit": "°C"}, e), field("time", None, e), field("atmosphere", "air; oxygen participation reported as crucial", e)])],
    outcomes=[field("yield", {"minimum": 64, "maximum": 75, "unit": "%", "raw_text": "64-75 %"}, e, ["bibutenolide_10"]), field("yield_measurement_basis", None, e, ["bibutenolide_10"])],
    unresolved=literature_unresolved("Scale, time, workup, purification, yield basis, and substrate-specific structures are missing."),
))

# Scheme 11 is introduced on page 4 and drawn on page 5; its mechanistic prose is separate.
e = ev(4, 5)
ps = [
    participant("allenoic_acid", "reactant", e, name="generic 2,3-allenoic acid"),
    participant("allenyl_ketone", "reactant", e, name="generic 1,2-allenyl ketone"),
    participant("pdcl2_mecn2", "catalyst", e, name="PdCl2(MeCN)2", amounts=[field("catalyst_loading", {"number": 5, "unit": "mol%"}, e)]),
    participant("mecn", "solvent", e, name="CH3CN", smiles="CC#N"),
    participant("furanyl_butenolide_11", "product", e, label="11", name="generic beta-furanyl butenolide"),
]
records.append(record(
    "scheme11_allenoic_acid_allenyl_ketone", "literature_example", e, participants=ps,
    steps=[step("matched_cyclizative_coupling", [p["entity_id"] for p in ps[:-1]], [field("solvent", "CH3CN", e), field("temperature", "r.t.", e), field("time", {"number": 4, "unit": "h"}, e)])],
    outcomes=[field("yield", None, e, ["furanyl_butenolide_11"]), field("yield_measurement_basis", None, e, ["furanyl_butenolide_11"])],
    unresolved=literature_unresolved("Substrate-specific entries, scale, yield, workup, purification, and yield basis are not reported here."),
))
records.append(record(
    "scheme11_text_pd_regeneration_hypothesis", "mechanism", e,
    participants=[
        participant("allenyl_ketone", "reactant", e, name="generic 1,2-allenyl ketone"),
        participant("pd0", "unspecified_agent", e, name="in situ generated Pd(0)"),
        participant("hcl", "unspecified_agent", e, name="HCl generated in the first oxypalladation step", smiles="Cl"),
        participant("pdii", "catalyst", e, name="regenerated divalent palladium species"),
    ],
    notes=["The review proposes Pd(II) regeneration by cyclometallation of the allenyl ketone with Pd(0), followed by protonolysis with generated HCl."],
    unresolved=["This is a prose mechanistic hypothesis; no independent experimental conditions or outcome are assigned."],
))

# Page 5 prose reports I2/NBS successes and an NCS failure before Scheme 12.
e = ev(5)
for suffix, reagent_id, reagent_name, smiles, product_name in [
    ("text_i2_iodolactonization", "i2", "I2", "II", "beta-iodobutenolide"),
    ("text_nbs_bromolactonization", "nbs", "NBS", "O=C1CCC(=O)N1Br", "beta-bromobutenolide"),
]:
    ps = [
        participant("allenoic_acid", "reactant", e, name="generic 2,3-allenoic acid"),
        participant(reagent_id, "reagent", e, name=reagent_name, smiles=smiles),
        participant("halobutenolide", "product", e, name=product_name),
    ]
    records.append(record(
        suffix, "literature_example", e, participants=ps,
        steps=[step("halolactonization", ["allenoic_acid", reagent_id], [field("temperature", None, e), field("time", None, e)])],
        outcomes=[field("yield", None, e, ["halobutenolide"]), field("yield_measurement_basis", None, e, ["halobutenolide"])],
        unresolved=literature_unresolved("The review gives no substrate, quantity, solvent, temperature, time, yield, workup, purification, or yield basis for this cited method."),
    ))

ps = [
    participant("allenoic_acid", "reactant", e, name="generic 2,3-allenoic acid"),
    participant("ncs", "reagent", e, name="NCS", smiles="O=C1CCC(=O)N1Cl"),
    participant("chlorobutenolide", "product", e, name="corresponding beta-chlorobutenolide"),
]
records.append(record(
    "text_ncs_chlorolactonization_failure", "literature_example", e, participants=ps,
    steps=[step("attempted_chlorolactonization", ["allenoic_acid", "ncs"], [field("temperature", None, e), field("time", None, e)])],
    outcomes=[field("reaction_result", "does not work well or does not work at all", e, ["chlorobutenolide"]), field("yield", None, e, ["chlorobutenolide"])],
    notes=["The wording is qualitative and does not establish a numeric zero yield."],
    unresolved=literature_unresolved("Substrate identity, quantities, solvent, temperature, time, and the exact split between poor and failed cases are not given."),
))

# Scheme 12 top: X is explicitly Cl or Br in one generic arrow.
ps = [
    participant("allenoic_acid", "reactant", e, name="generic 2,3-allenoic acid"),
    participant("cux2", "reagent", e, label="CuX2", name="CuCl2 or CuBr2", amounts=[field("reagent_equivalents", {"number": 4, "unit": "equiv"}, e)]),
    participant("acetone", "solvent", e, name="acetone", smiles="CC(C)=O"),
    participant("water", "solvent", e, name="H2O", smiles="O"),
    participant("halobutenolide_12", "product", e, label="12", name="beta-chloro- or beta-bromobutenolide"),
]
records.append(record(
    "scheme12_cux2_halolactonization", "literature_example", e, participants=ps,
    steps=[step("cux2_halolactonization", [p["entity_id"] for p in ps[:-1]], [field("solvent", "acetone/H2O (2:1)", e), field("temperature", {"minimum": 65, "maximum": 70, "unit": "°C", "raw_text": "65-70 °C"}, e), field("time", None, e)])],
    outcomes=[field("yield", {"number": 89, "unit": "%", "qualifier": "gt", "raw_text": ">89 %"}, e, ["halobutenolide_12"]), field("yield_measurement_basis", None, e, ["halobutenolide_12"])],
    notes=["X is Cl or Br; the prose says bromination is usually faster and higher yielding than chlorination."],
    unresolved=literature_unresolved("The generic arrow does not separate Cl and Br substrate rows; reaction time, scale, workup, purification, and yield basis are absent."),
))

ps = [
    participant("allenoic_acid", "reactant", e, name="generic 2,3-allenoic acid"),
    participant("cucl", "catalyst", e, name="CuCl", smiles="[Cu]Cl", amounts=[field("catalyst_loading", {"number": 4, "unit": "mol%"}, e)]),
    participant("meoh", "solvent", e, name="MeOH", smiles="CO"),
    participant("butenolide_13", "product", e, label="13", name="cycloisomerization butenolide"),
]
records.append(record(
    "scheme12_cucl_cycloisomerization", "literature_example", e, participants=ps,
    steps=[step("cycloisomerization", [p["entity_id"] for p in ps[:-1]], [field("solvent", "MeOH", e), field("temperature", "reflux", e), field("time", {"number": 2, "unit": "h"}, e)])],
    outcomes=[field("yield", {"minimum": 77, "maximum": 97, "unit": "%", "raw_text": "77-97 %"}, e, ["butenolide_13"]), field("yield_measurement_basis", None, e, ["butenolide_13"])],
    unresolved=literature_unresolved("Substrate-specific entries, scale, reflux temperature, workup, purification, and yield basis are not supplied."),
))

# Three distinct chiral variants described below Scheme 12.
ps = [
    participant("Sa_5", "reactant", e, label="Sa-(+)-5", name="Sa-(+)-2-methyl-4-phenyl-2,3-butadienoic acid", smiles="CC(=C=Cc1ccccc1)C(=O)O"),
    participant("cux2", "reagent", e, label="CuX2", name="CuCl2 or CuBr2"),
    participant("chiral_12", "product", e, label="12", name="optically active beta-halobutenolide"),
]
records.append(record(
    "text_Sa5_cux2_chiral_halolactonization", "literature_example", e, participants=ps,
    steps=[step("chiral_halolactonization", ["Sa_5", "cux2"], [field("temperature", None, e), field("time", None, e)])],
    outcomes=[field("yield", "high yield", e, ["chiral_12"]), field("enantiomeric_excess", "high ee", e, ["chiral_12"]), field("yield_measurement_basis", None, e, ["chiral_12"])],
    unresolved=literature_unresolved("X, quantities, solvent, temperature, time, numeric yield/ee, workup, purification, and yield basis are not specified for this chiral example."),
))

ps = [
    participant("cinchonidine_salt", "reactant", e, name="L-cinchonidine salt of the corresponding allenoic acid"),
    participant("cubr2", "reagent", e, name="CuBr2"),
    participant("acetone_water", "solvent", e, name="aqueous acetone"),
    participant("chiral_12", "product", e, label="12", name="optically active beta-bromobutenolide"),
]
records.append(record(
    "text_cinchonidine_salt_cubr2_halolactonization", "literature_example", e, participants=ps,
    steps=[step("chiral_bromolactonization", ["cinchonidine_salt", "cubr2", "acetone_water"], [field("solvent", "aqueous acetone", e), field("temperature", None, e), field("time", None, e)])],
    outcomes=[field("yield", "high yield", e, ["chiral_12"]), field("enantiomeric_excess", "high ee", e, ["chiral_12"]), field("yield_measurement_basis", None, e, ["chiral_12"])],
    notes=["The review concludes that cinchonidine steric information does not influence the halolactonization stereochemistry."],
    unresolved=literature_unresolved("Exact acid/salt structure, quantities, solvent ratio, temperature, time, numeric yield/ee, workup, purification, and yield basis are absent."),
))

ps = [
    participant("racemic_allenoic_acid", "reactant", e, name="racemic allenoic acid precursor"),
    participant("alpha_methylbenzylamine", "reagent", e, name="alpha-methylbenzylamine"),
    participant("resolved_halobutenolides", "product", e, name="(R)- and (S)-beta-halobutenolides"),
]
records.append(record(
    "text_alpha_methylbenzylamine_resolution_route", "literature_example", e, participants=ps,
    steps=[step("resolution_and_halolactonization_route", ["racemic_allenoic_acid", "alpha_methylbenzylamine"], [field("temperature", None, e), field("time", None, e)])],
    outcomes=[field("yield", None, e, ["resolved_halobutenolides"]), field("enantiomeric_excess", None, e, ["resolved_halobutenolides"])],
    notes=["The review only states that alpha-methylbenzylamine can be used as resolving agent for synthesis of both enantiomers."],
    unresolved=literature_unresolved("Enantiomer of the resolving agent, salt formation/halolactonization conditions, structures, quantities, yields, and ee values are not supplied."),
))

raw_path = RUN / "raw_model/extracted_records_pages_0001_0006.json"
write(raw_path, records)

by_suffix = {r["source_reaction_id"]: r["record_id"] for r in records}
coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1,
            "state": "attempted",
            "regions": [
                {"region": "title, abstract, and introductory prose", "finding": "Review/lecture overview; no individual experiment is specified in this region.", "evidence_ids": [f"{DOC}:page1:image", f"{DOC}:page1:text"]},
                {"region": "Scheme 1, Path 1", "finding": "Generic carbometallation/intramolecular allylation mechanism, not a reported experiment.", "evidence_ids": [f"{DOC}:page1:image", f"{DOC}:page1:text"]},
                {"region": "Scheme 1, Path 2", "finding": "Generic cyclic oxymetallation/reductive-elimination mechanism, not a reported experiment.", "evidence_ids": [f"{DOC}:page1:image", f"{DOC}:page1:text"]},
                {"region": "bottom paragraph introducing Pd(0)/Ag+ coupling", "finding": "Cross-page introduction to the cited Scheme 2 literature example on page 2.", "evidence_ids": [f"{DOC}:page1:image", f"{DOC}:page1:text", f"{DOC}:page2:image"]},
            ],
            "record_ids": [by_suffix["scheme1_path1_carbometallation_allylation"], by_suffix["scheme1_path2_oxymetallation_reductive_elimination"], by_suffix["scheme2_pd_ag_coupling_cyclization"]],
            "unresolved": ["Scheme 1 contains generic R groups and MY; structures and experimental conditions are intentionally not inferred."],
        },
        {
            "page": 2,
            "state": "attempted",
            "regions": [
                {"region": "Scheme 2", "finding": "Cited Pd(PPh3)4/Ag2CO3 coupling-cyclization with 70 °C and 59-79% yield range.", "evidence_ids": [f"{DOC}:page2:image", f"{DOC}:page2:text"]},
                {"region": "Scheme 3 and preceding cleavage-protocol paragraph", "finding": "Solid-phase route plus three condition-distinct polymer-cleavage protocols; retained as three partial literature examples.", "evidence_ids": [f"{DOC}:page2:image", f"{DOC}:page2:text"]},
                {"region": "Scheme 4 and adjacent prose", "finding": "Specific Sa-(+)-5/PhI coupling with 96% starting ee and highest product ee 60%; yield, time, and temperature are absent.", "evidence_ids": [f"{DOC}:page2:image", f"{DOC}:page2:text"]},
                {"region": "bottom mechanistic sentence", "finding": "Prose transition to Scheme 5's proposed oxypalladation pathway; no separate experiment.", "evidence_ids": [f"{DOC}:page2:image", f"{DOC}:page2:text", f"{DOC}:page3:image"]},
            ],
            "record_ids": [by_suffix[x] for x in ["scheme2_pd_ag_coupling_cyclization", "scheme3_carboxyl_linker_alcl3_cleavage", "scheme3_ether_linker_znbr2_acetyl_bromide_cleavage", "scheme3_thp_linker_tfa_meoh_cleavage", "scheme4_Sa5_phi_low_ee", "scheme5_oxypalladation_cycle"]],
            "unresolved": ["Scheme 3 does not show coupling conditions or protocol-specific yields; Scheme 4 lacks reaction time, temperature, and yield."],
        },
        {
            "page": 3,
            "state": "attempted",
            "regions": [
                {"region": "Scheme 5", "finding": "Proposed Pd coordination/oxypalladation catalytic cycle; classified as mechanism.", "evidence_ids": [f"{DOC}:page3:image", f"{DOC}:page3:text"]},
                {"region": "Scheme 6 first vertical arrow", "finding": "1:1 salt preparation in ethyl acetate at room temperature, separated from the subsequent coupling stage.", "evidence_ids": [f"{DOC}:page3:image", f"{DOC}:page3:text"]},
                {"region": "Scheme 6 second arrow", "finding": "Salt 7/PhI coupling at 5 °C for 60 h, 62% yield and 91% ee.", "evidence_ids": [f"{DOC}:page3:image", f"{DOC}:page3:text"]},
                {"region": "Scheme 6 prose on cinchonidine salt/TBAB", "finding": "Condition variant retained separately because TBAB is explicitly required as phase-transfer catalyst.", "evidence_ids": [f"{DOC}:page3:image", f"{DOC}:page3:text"]},
                {"region": "Scheme 7", "finding": "Generic PdCl2-catalyzed allylic-halide coupling scope at 50 °C with 69-95% yields.", "evidence_ids": [f"{DOC}:page3:image", f"{DOC}:page3:text"]},
            ],
            "record_ids": [by_suffix[x] for x in ["scheme5_oxypalladation_cycle", "scheme6_prepare_salt7", "scheme6_salt7_phi_coupling", "scheme6_text_cinchonidine_salt_tbab_variant", "scheme7_pdcl2_allylic_halide_coupling"]],
            "unresolved": ["The cinchonidine/TBAB variant lacks numeric conditions and outcomes; Scheme 7 lacks row-level substrates, reaction time, and yield basis."],
        },
        {
            "page": 4,
            "state": "attempted",
            "regions": [
                {"region": "Scheme 8 and top prose", "finding": "Chiral allyl-bromide variant reports no obvious chirality loss but no numeric ee/yield on this page.", "evidence_ids": [f"{DOC}:page4:image", f"{DOC}:page4:text"]},
                {"region": "Scheme 9 upper arrow", "finding": "Generic non-allylic alkenyl-bromide coupling at 100 °C with 18-58% yields.", "evidence_ids": [f"{DOC}:page4:image", f"{DOC}:page4:text"]},
                {"region": "Scheme 9 lower cycle", "finding": "Depicted pi-bond-walking mechanism, separated from the literature reaction record.", "evidence_ids": [f"{DOC}:page4:image", f"{DOC}:page4:text"]},
                {"region": "Scheme 10", "finding": "Generic alkyl-iodide/air route to bi-butenolides at 80 °C with 64-75% yields.", "evidence_ids": [f"{DOC}:page4:image", f"{DOC}:page4:text"]},
                {"region": "bottom paragraph introducing Scheme 11", "finding": "Cross-page description of allenyl-ketone coupling and proposed Pd(II) regeneration; linked to page 5.", "evidence_ids": [f"{DOC}:page4:image", f"{DOC}:page4:text", f"{DOC}:page5:image"]},
            ],
            "record_ids": [by_suffix[x] for x in ["scheme8_chiral_allenoic_acid_allyl_bromide", "scheme9_alkenyl_bromide_pi_walk_coupling", "scheme9_pi_bond_walking_mechanism", "scheme10_alkyl_iodide_bibutenolide", "scheme11_allenoic_acid_allenyl_ketone", "scheme11_text_pd_regeneration_hypothesis"]],
            "unresolved": ["Schemes 8-10 are generic scopes without substrate rows or yield bases; Scheme 11 yield is not printed."],
        },
        {
            "page": 5,
            "state": "attempted",
            "regions": [
                {"region": "Scheme 11", "finding": "Generic PdCl2(MeCN)2-catalyzed matched coupling in MeCN at room temperature for 4 h; yield absent.", "evidence_ids": [f"{DOC}:page5:image", f"{DOC}:page5:text", f"{DOC}:page4:text"]},
                {"region": "halolactonization prose above Scheme 12", "finding": "Separate cited I2 and NBS successes and qualitative NCS failure; no numeric conditions/outcomes supplied.", "evidence_ids": [f"{DOC}:page5:image", f"{DOC}:page5:text"]},
                {"region": "Scheme 12 upper arrow", "finding": "Generic CuX2 (X=Cl or Br) halolactonization, 4 equiv, acetone/H2O 2:1, 65-70 °C, >89% yield.", "evidence_ids": [f"{DOC}:page5:image", f"{DOC}:page5:text"]},
                {"region": "Scheme 12 lower arrow", "finding": "CuCl-catalyzed cycloisomerization in refluxing MeOH for 2 h, 77-97% yield.", "evidence_ids": [f"{DOC}:page5:image", f"{DOC}:page5:text"]},
                {"region": "paragraph below Scheme 12", "finding": "Three partial chiral-route statements retained separately: Sa-(+)-5/CuX2, cinchonidine-salt/CuBr2, and alpha-methylbenzylamine resolution route.", "evidence_ids": [f"{DOC}:page5:image", f"{DOC}:page5:text"]},
                {"region": "references 1-9", "finding": "Bibliographic citations only; no additional reaction records generated from the reference list.", "evidence_ids": [f"{DOC}:page5:image", f"{DOC}:page5:text"]},
            ],
            "record_ids": [by_suffix[x] for x in ["scheme11_allenoic_acid_allenyl_ketone", "scheme11_text_pd_regeneration_hypothesis", "text_i2_iodolactonization", "text_nbs_bromolactonization", "text_ncs_chlorolactonization_failure", "scheme12_cux2_halolactonization", "scheme12_cucl_cycloisomerization", "text_Sa5_cux2_chiral_halolactonization", "text_cinchonidine_salt_cubr2_halolactonization", "text_alpha_methylbenzylamine_resolution_route"]],
            "unresolved": ["Generic X/R scope is not expanded into invented rows; several chiral outcomes are only qualitative, and yield bases are absent."],
        },
        {
            "page": 6,
            "state": "attempted",
            "regions": [
                {"region": "references 10-14 and page footer", "finding": "Reference continuation only; no reaction arrow, table, experimental procedure, or new outcome appears on this page.", "evidence_ids": [f"{DOC}:page6:image", f"{DOC}:page6:text"]},
            ],
            "record_ids": [],
            "unresolved": ["Original cited papers and their supporting information were not supplied or associated, so their missing procedures were not inferred."],
        },
    ],
}
write(RUN / "coverage/pages_0001_0006.json", coverage)

tasks_path = RUN / "tasks.json"
tasks = json.loads(tasks_path.read_text())
for task in tasks:
    if task.get("document_id") == DOC and 1 <= int(task["evidence_id"].split(":page", 1)[1].split(":", 1)[0]) <= 6:
        page = int(task["evidence_id"].split(":page", 1)[1].split(":", 1)[0])
        task["state"] = "attempted"
        task["visual_evidence_id"] = f"{DOC}:page{page}:image"
        task["reason"] = "Original page image and page text inspected; findings and unresolved items are recorded in coverage/pages_0001_0006.json."
write(tasks_path, tasks)

print(json.dumps({"records": len(records), "coverage_pages": [p["page"] for p in coverage["pages"]]}, ensure_ascii=False))
