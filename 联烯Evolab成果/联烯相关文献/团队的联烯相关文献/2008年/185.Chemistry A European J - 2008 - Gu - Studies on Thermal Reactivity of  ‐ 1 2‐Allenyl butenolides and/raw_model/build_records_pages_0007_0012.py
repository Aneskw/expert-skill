import copy
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "runs/current"
DOC = "doc_efbb5564c1bec50d"
DATA = json.loads((OUT / "dataset.json").read_text())
EXISTING = {r["record_id"]: r for r in DATA["experiments"]}


def evidence(*pages):
    result = []
    for page in pages:
        result.extend([f"{DOC}:page{page}:text", f"{DOC}:page{page}:image"])
    return result


def fact(value, ev):
    return {
        "value": value,
        "evidence_ids": list(ev) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def field(name, value, ev, targets=None):
    item = {"name": name, "fact": fact(value, ev)}
    if targets:
        item["target_entity_ids"] = list(targets)
    return item


def q(number, unit, **extra):
    value = {"number": number, "unit": unit}
    value.update(extra)
    return value


def participant(entity_id, role, label, ev, *, name=None, smiles=None, amounts=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, ev),
        "name": fact(name, ev) if name is not None else fact(None, []),
        "smiles": fact(smiles, ev) if smiles is not None else fact(None, []),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": amounts or [],
    }


def record(suffix, kind, pages, participants=None, conditions=None, outcomes=None,
           notes=None, unresolved=None, steps=None, retain_old_evidence=True):
    rid = f"{DOC}:{suffix}"
    ev = []
    if retain_old_evidence and rid in EXISTING:
        ev.extend(EXISTING[rid]["evidence_ids"])
    ev.extend(evidence(*pages))
    ev = list(dict.fromkeys(ev))
    participants = participants or []
    if steps is None:
        steps = []
        if conditions is not None:
            steps = [{
                "step_id": "step1",
                "participant_ids": [p["entity_id"] for p in participants],
                "conditions": conditions,
            }]
    return {
        "record_id": rid,
        "document_id": DOC,
        "source_reaction_id": suffix,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": ev,
        "participants": participants,
        "steps": steps,
        "outcomes": outcomes or [],
        "notes": [fact(n, ev) for n in (notes or [])],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved or [],
        },
    }


records = []


# Page 7: mechanisms, summary scheme, and isotope-synthesis arrows.
records.append(record(
    "scheme19_stereochemical_15h_shift_pathways", "mechanism", [7],
    notes=[
        "Scheme 19 proposes that two conformations/transition states 17 and 19 give tetraenes 18 and 20 by separate 1,5-hydrogen shifts.",
        "The scheme is a stereochemical rationale and does not report isolated intermediates 17–20 as separate experiments.",
    ],
    unresolved=["Generic R-group structures and the transition-state stereochemistry remain unverified."],
    retain_old_evidence=False,
))
records.append(record(
    "scheme25_reactivity_summary", "general_scheme", [8],
    notes=[
        "Scheme 25 summarizes three substrate-dependent pathways: 1,5-H/1,7-H shifts to triene 3, 6pi electrocyclization to 5, and 8pi electrocyclization to 6 or 15.",
        "This is a generic conclusion scheme; the underlying executed experiments remain in their individual records.",
    ],
    unresolved=["Generic R-group structures are not complete molecule assignments."],
    retain_old_evidence=False,
))

ev7 = evidence(7)
records.append(record(
    "d5_hexyl_propiolate_22_esterification", "reported_experiment", [7],
    participants=[
        participant("propiolic_acid_21", "reactant", "propiolic acid 21", ev7, name="propiolic acid", smiles="C#CC(=O)O"),
        participant("n_hexanol", "reactant", "n-C6H13OH", ev7, name="1-hexanol", smiles="CCCCCCO"),
        participant("ptsoh", "catalyst", "pTsOH (catalytic)", ev7),
        participant("benzene", "solvent", "benzene", ev7, smiles="c1ccccc1"),
        participant("hexyl_propiolate_22", "product", "hexyl propiolate 22", ev7, smiles="C#CC(=O)OCCCCCC"),
    ],
    conditions=[
        field("solvent", "benzene", ev7), field("temperature", None, ev7),
        field("reaction_time", None, ev7), field("atmosphere", None, ev7),
    ],
    outcomes=[field("reported_yield", q(100, "%"), ev7, ["hexyl_propiolate_22"]), field("yield_measurement_basis", None, ev7, ["hexyl_propiolate_22"])],
    unresolved=["Scheme 20 omits scale, temperature, time, atmosphere, workup, purification, and yield basis for this esterification."],
    retain_old_evidence=False,
))

ev710 = evidence(7, 10)
records.append(record(
    "d1_hexyl_3_deuteropropiolate_23_exchange", "reported_experiment", [7, 10],
    participants=[
        participant("hexyl_propiolate_22", "reactant", "hexyl propiolate 22", ev710, amounts=[field("mass", q(10.0, "g"), evidence(10)), field("amount", q(65, "mmol"), evidence(10))]),
        participant("d2o", "reagent", "D2O", ev710, amounts=[field("volume_per_cycle", q(5.0, "mL"), evidence(10))]),
        participant("k2co3", "reagent", "K2CO3", ev710, amounts=[field("mass_per_cycle", q(0.25, "g"), evidence(10)), field("amount_per_cycle", q(1.8, "mmol"), evidence(10))]),
        participant("tbab", "reagent", "TBAB", ev710, name="tetrabutylammonium bromide", amounts=[field("initial_mass", q(0.75, "g"), evidence(10)), field("initial_amount", q(2.3, "mmol"), evidence(10)), field("subsequent_mass_per_cycle", q(75, "mg"), evidence(10)), field("subsequent_amount_per_cycle", q(0.23, "mmol"), evidence(10))]),
        participant("na2so4", "reagent", "Na2SO4", evidence(10)),
        participant("product_d1_23", "product", "hexyl 3-deuteropropiolate [D]-23", ev710),
    ],
    conditions=[
        field("temperature", "r.t.", evidence(10)), field("reaction_time_per_cycle", q(24, "h"), evidence(10)),
        field("atmosphere", "argon", evidence(10)),
        field("operation", "Discard the aqueous layer, repeat the D2O/K2CO3/TBAB exchange procedure four times, then dry the organic layer over Na2SO4", evidence(10)),
    ],
    outcomes=[
        field("deuterium_content", q(96, "%", raw_text="96% [D]"), ev7, ["product_d1_23"]),
        field("reported_yield", None, evidence(10), ["product_d1_23"]),
    ],
    notes=["The crude [D]-23 was described as pure enough for the next step."],
    unresolved=["No isolated mass/yield or purification is reported; the exact total number of exchange contacts should be read from the stated repeat-four-times operation rather than inferred."],
    retain_old_evidence=False,
))


# Detailed [D5] sequence.
ev5710 = evidence(5, 7, 10)
records.append(record(
    "d5_allyl_mesylate_24_synthesis", "reported_experiment", [5, 7, 10],
    participants=[
        participant("d1_23", "reactant", "[D]-23", ev5710),
        participant("liald4", "reagent", "LiAlD4", evidence(10), amounts=[field("mass", q(5.92, "g"), evidence(10)), field("amount", q(141.0, "mmol"), evidence(10))]),
        participant("et2o", "solvent", "anhydrous Et2O", evidence(10), amounts=[field("initial_volume", q(180, "mL"), evidence(10)), field("substrate_solution_volume", q(20, "mL"), evidence(10))]),
        participant("d2o", "reagent", "D2O", evidence(10), amounts=[field("volume", q(6.0, "mL"), evidence(10)), field("amount", q(300, "mmol"), evidence(10))]),
        participant("naoh", "reagent", "10% NaOH", evidence(10), amounts=[field("volume", q(12, "mL"), evidence(10))]),
        participant("water", "reagent", "H2O", evidence(10), smiles="O", amounts=[field("volume", q(18, "mL"), evidence(10))]),
        participant("et3n", "reagent", "Et3N", evidence(10), amounts=[field("volume", q(9.74, "mL"), evidence(10)), field("amount", q(70, "mmol"), evidence(10))]),
        participant("mscl", "reagent", "MsCl", evidence(10), amounts=[field("volume", q(5.4, "mL"), evidence(10)), field("mass", q(8.02, "g"), evidence(10)), field("amount", q(70, "mmol"), evidence(10))]),
        participant("product_d5_24", "product", "[D5]-24-(allyl)", ev5710, amounts=[field("isolated_mass", q(3.61, "g"), evidence(10))]),
    ],
    steps=[
        {"step_id": "reduction", "participant_ids": ["d1_23", "liald4", "et2o", "d2o", "naoh", "water"], "conditions": [field("addition_time", q(1, "h"), evidence(10)), field("addition_temperature", q(-10, "°C", qualifier="lt", raw_text="below -10 °C"), evidence(10)), field("reaction_temperature", "warm to r.t.", evidence(10)), field("reaction_time_at_room_temperature", q(6, "h"), evidence(10)), field("d2o_quench_temperature", q(0, "°C"), evidence(10)), field("time_after_d2o_addition", q(2, "h"), evidence(10)), field("atmosphere", "argon", evidence(10)), field("operation", "Filter and distill the filtrate to obtain a deuterated allyl alcohol/ether mixture", evidence(10))]},
        {"step_id": "mesylation", "participant_ids": ["et3n", "mscl", "product_d5_24"], "conditions": [field("temperature", q(0, "°C"), evidence(10)), field("addition_time", q(20, "min"), evidence(10)), field("operation", "Filter, evaporate, and purify by flash chromatography on silica gel", evidence(10))]},
    ],
    outcomes=[field("reported_overall_yield_for_three_steps", q(39, "%", raw_text="39% for three steps"), evidence(7, 10), ["product_d5_24"]), field("yield_measurement_basis", "isolated", evidence(10), ["product_d5_24"])],
    unresolved=["The phrase '39% for three steps' is retained as printed; the source does not independently report the allyl-alcohol intermediate yield."],
))

records.append(record(
    "d5_25_cui_coupling", "reported_experiment", [5, 7, 10],
    participants=[
        participant("phenyl_propynol", "reactant", "1-phenylprop-2-yn-1-ol", ev5710, amounts=[field("mass", q(1.32, "g"), evidence(10)), field("amount", q(10.0, "mmol"), evidence(10))]),
        participant("d5_24", "reactant", "[D5]-24-(allyl)", ev5710, amounts=[field("mass", q(1.55, "g"), evidence(10)), field("amount", q(11.0, "mmol"), evidence(10))]),
        participant("cui", "catalyst", "CuI", ev5710, amounts=[field("mass", q(0.19, "g"), evidence(10)), field("amount", q(1.0, "mmol"), evidence(10))]),
        participant("k2co3", "reagent", "K2CO3", ev5710, amounts=[field("mass", q(2.76, "g"), evidence(10)), field("amount", q(20.0, "mmol"), evidence(10))]),
        participant("dmf", "solvent", "DMF", ev5710, smiles="CN(C)C=O", amounts=[field("volume", q(30, "mL"), evidence(10))]),
        participant("product_d5_25", "product", "[D5]-25-(allyl)", ev5710, amounts=[field("isolated_mass", q(1.31, "g"), evidence(10))]),
    ],
    conditions=[field("temperature", q(30, "°C"), evidence(10)), field("reaction_time", q(12, "h"), evidence(10)), field("atmosphere", "argon", evidence(10)), field("workup", "Filter through a short silica column, dilute with water (100 mL), extract with Et2O (50 mL ×3), wash with brine, dry over Na2SO4, and evaporate", evidence(10)), field("purification", "flash chromatography on silica gel", evidence(10))],
    outcomes=[field("reported_yield", q(74, "%"), evidence(7, 10), ["product_d5_25"]), field("yield_measurement_basis", "isolated", evidence(10), ["product_d5_25"])],
    unresolved=["The product's isotope-specific structure remains unverified."],
))

records.append(record(
    "d5_26_palladium_carbonylation", "reported_experiment", [5, 7, 10],
    participants=[
        participant("d5_25", "reactant", "[D5]-25-(allyl)", ev5710, amounts=[field("mass", q(1.06, "g"), evidence(10)), field("amount", q(6.0, "mmol"), evidence(10))]),
        participant("libr", "reagent", "LiBr", evidence(10), amounts=[field("amount", q(6.0, "mmol"), evidence(10))]),
        participant("nbuli", "reagent", "nBuLi (2.5 M in hexanes)", evidence(10), amounts=[field("volume", q(2.64, "mL"), evidence(10)), field("amount", q(6.6, "mmol"), evidence(10)), field("concentration", q(2.5, "M"), evidence(10))]),
        participant("ptscl", "reagent", "pTsCl", evidence(10), amounts=[field("mass", q(1.26, "g"), evidence(10)), field("amount", q(6.6, "mmol"), evidence(10))]),
        participant("pd_pph3_4", "catalyst", "Pd(PPh3)4", ev5710, amounts=[field("mass", q(138, "mg"), evidence(10)), field("amount", q(0.12, "mmol"), evidence(10))]),
        participant("co", "reagent", "CO", ev5710, smiles="[C-]#[O+]"),
        participant("thf", "solvent", "THF", ev5710, smiles="C1CCOC1", amounts=[field("volume", q(35, "mL"), evidence(10))]),
        participant("water", "reagent", "H2O", evidence(10), smiles="O", amounts=[field("volume", q(1.2, "mL"), evidence(10))]),
        participant("product_d5_26", "product", "[D5]-26-(allyl)", ev5710, amounts=[field("isolated_mass", q(0.53, "g"), evidence(10))]),
    ],
    steps=[
        {"step_id": "tosylation_rearrangement", "participant_ids": ["d5_25", "libr", "nbuli", "ptscl", "thf"], "conditions": [field("addition_temperature", q(-78, "°C"), evidence(10)), field("time_before_ptscl", q(30, "min"), evidence(10)), field("reaction_temperature_after_ptscl", "warm to r.t.", evidence(10)), field("reaction_time_after_ptscl", q(1.5, "h"), evidence(10))]},
        {"step_id": "carbonylation", "participant_ids": ["pd_pph3_4", "co", "water", "product_d5_26"], "conditions": [field("co_pressure", "300 psi", evidence(10)), field("temperature", "r.t.", evidence(10)), field("reaction_time", q(2, "h"), evidence(10)), field("workup", "Deflate excess CO, dry over Na2SO4, evaporate, and filter through a short silica column", evidence(10)), field("purification", "recrystallization from Et2O/petroleum ether", evidence(10))]},
    ],
    outcomes=[field("reported_yield_for_two_steps", q(43, "%", raw_text="43% for two steps"), evidence(7, 10), ["product_d5_26"]), field("yield_measurement_basis", "isolated", evidence(10), ["product_d5_26"])],
    unresolved=["The source reports a two-step yield without separate yields for the tosylation/rearrangement and carbonylation stages."],
))

records.append(record(
    "d5_1g_cross_coupling", "reported_experiment", [5, 7, 10, 11],
    participants=[
        participant("d5_26", "reactant", "[D5]-26-(allyl)", evidence(5, 7, 10), amounts=[field("mass", q(123, "mg"), evidence(10)), field("amount", q(0.60, "mmol"), evidence(10))]),
        participant("methyl_propargyl_carbonate", "reactant", "methyl 2-methylbut-3-yn-2-yl carbonate", evidence(5, 7, 10), amounts=[field("mass", q(170, "mg"), evidence(10)), field("amount", q(1.20, "mmol"), evidence(10))]),
        participant("pd_oac2", "catalyst", "Pd(OAc)2", evidence(7, 10), amounts=[field("mass", q(7, "mg"), evidence(10)), field("amount", q(0.030, "mmol"), evidence(10))]),
        participant("tfp", "catalyst", "TFP", evidence(7, 10), amounts=[field("mass", q(14, "mg"), evidence(10)), field("amount", q(0.060, "mmol"), evidence(10))]),
        participant("k2co3", "reagent", "K2CO3", evidence(7, 10), amounts=[field("mass", q(83, "mg"), evidence(10)), field("amount", q(0.60, "mmol"), evidence(10))]),
        participant("dmso", "solvent", "DMSO", evidence(7, 10), smiles="CS(C)=O", amounts=[field("volume", q(2.5, "mL"), evidence(10))]),
        participant("product_d5_1g", "product", "[D5]-1g-(allyl)", evidence(5, 7, 10, 11), amounts=[field("isolated_mass", q(86, "mg"), evidence(10))]),
    ],
    conditions=[field("temperature", None, evidence(10)), field("reaction_time", None, evidence(10)), field("atmosphere", None, evidence(10)), field("workup", None, evidence(10)), field("purification", None, evidence(10))],
    outcomes=[
        field("scheme20_reported_yield", q(62, "%"), evidence(7), ["product_d5_1g"]),
        field("detailed_paragraph_reported_yield", q(53, "%"), evidence(10), ["product_d5_1g"]),
        field("allenyl_center_deuterium_content", q(93, "%"), evidence(5), ["product_d5_1g"]),
        field("yield_measurement_basis", None, evidence(10), ["product_d5_1g"]),
    ],
    unresolved=["Scheme 20 reports 62%, whereas the detailed paragraph reports 86 mg (53%); both source values are retained.", "Temperature, duration, atmosphere, workup, purification, and yield basis are not restated in the detailed paragraph."],
))

records.append(record(
    "d5_1g_cycloisomerization", "reported_experiment", [5, 7, 11],
    participants=[
        participant("substrate_d5_1g", "reactant", "[D5]-1g-(allyl)", evidence(5, 7, 11), amounts=[field("mass", q(72, "mg"), evidence(11)), field("amount", q(0.27, "mmol"), evidence(11))]),
        participant("xylene", "solvent", "xylene", evidence(5, 7, 11), amounts=[field("volume", q(4, "mL"), evidence(11))]),
        participant("product_d5_6g", "product", "[D5]-6g", evidence(5, 7, 11), amounts=[field("isolated_mass", q(46, "mg"), evidence(11))]),
    ],
    conditions=[field("solvent", "xylene", evidence(5, 7, 11)), field("temperature", q(110, "°C"), evidence(5, 7, 11)), field("reaction_time", q(6, "h"), evidence(5, 7, 11)), field("atmosphere", "argon", evidence(11)), field("operation", "Monitor complete consumption by TLC and purify directly by flash chromatography on silica gel", evidence(11))],
    outcomes=[
        field("reported_yield", q(64, "%"), evidence(5, 7, 11), ["product_d5_6g"]),
        field("deuterium_incorporation_at_4_position", q(82, "%"), evidence(5, 7), ["product_d5_6g"]),
        field("approximate_deuterium_incorporation_in_two_methyl_groups", q(3, "%", qualifier="approx", raw_text="~3%"), evidence(5), ["product_d5_6g"]),
        field("yield_measurement_basis", "isolated", evidence(11), ["product_d5_6g"]),
    ],
    notes=["Unidentified products (10 mg) were also obtained; Figure 5 compares the [D5], [D6], and undeuterated 1H NMR spectra."],
    unresolved=["Isotope-specific structure assignments remain machine-unverified."],
))


# Detailed [D6] sequence.
records.append(record(
    "d6_27_synthesis", "reported_experiment", [5, 7],
    participants=[
        participant("ethyl_bromide", "reactant", "C2H5Br", evidence(7), name="bromoethane", smiles="CCBr"),
        participant("mg", "reagent", "Mg", evidence(7), smiles="[Mg]"),
        participant("acetylene", "reactant", "acetylene", evidence(7), smiles="C#C"),
        participant("thf", "solvent", "THF", evidence(7), smiles="C1CCOC1"),
        participant("acetone_d6", "reactant", "CD3COCD3", evidence(5, 7)),
        participant("product_d6_27", "product", "[D6]-27-(CD3)2-H(D)", evidence(5, 7)),
    ],
    steps=[
        {"step_id": "grignard_preparation", "participant_ids": ["ethyl_bromide", "mg", "acetylene", "thf"], "conditions": [field("solvent", "THF", evidence(7)), field("temperature", None, evidence(7)), field("reaction_time", None, evidence(7))]},
        {"step_id": "addition_to_acetone_d6", "participant_ids": ["acetone_d6", "product_d6_27"], "conditions": [field("temperature", None, evidence(7)), field("reaction_time", None, evidence(7)), field("atmosphere", None, evidence(7))]},
    ],
    outcomes=[field("reported_yield", q(34, "%"), evidence(7), ["product_d6_27"]), field("yield_measurement_basis", None, evidence(7), ["product_d6_27"])],
    unresolved=["Scheme 22 omits all absolute quantities, times, temperatures, atmosphere, workup, purification, yield basis, and the exact terminal H/D composition."],
))

records.append(record(
    "d6_28_carbonate_synthesis", "reported_experiment", [5, 7, 11],
    participants=[
        participant("d6_27", "reactant", "[D6]-27-(CD3)2-H(D) according to Scheme 22", evidence(5, 7, 11), amounts=[field("mass", q(2.70, "g"), evidence(11)), field("amount", q(30, "mmol"), evidence(11))]),
        participant("nah", "reagent", "NaH, 60% in mineral oil", evidence(7, 11), amounts=[field("mass", q(2.10, "g"), evidence(11)), field("amount", q(51, "mmol"), evidence(11))]),
        participant("methyl_chloroformate", "reagent", "ClCO2Me", evidence(7, 11), name="methyl chloroformate", amounts=[field("volume", q(3.48, "mL"), evidence(11)), field("amount", q(45, "mmol"), evidence(11))]),
        participant("et2o", "solvent", "Et2O", evidence(7, 11), amounts=[field("initial_volume", q(150, "mL"), evidence(11)), field("substrate_solution_volume", q(5, "mL"), evidence(11)), field("methyl_chloroformate_solution_volume", q(5, "mL"), evidence(11))]),
        participant("product_d6_28_hd", "product", "[D6]-28-(CD3)2-H(D)", evidence(5, 7, 11), amounts=[field("isolated_mass", q(2.55, "g"), evidence(11))]),
    ],
    conditions=[field("solvent", "Et2O", evidence(7, 11)), field("initial_reaction_temperature", "reflux", evidence(11)), field("initial_reaction_time", q(3, "h"), evidence(11)), field("methyl_chloroformate_addition_temperature", "r.t.", evidence(11)), field("addition_time", q(30, "min"), evidence(11)), field("time_after_addition", "overnight", evidence(11)), field("atmosphere", None, evidence(11)), field("workup", "Quench with water, extract with Et2O, wash with brine, dry over Na2SO4, and evaporate", evidence(11)), field("purification", "distillation; b.p. 49–50 °C at 10 mmHg", evidence(11))],
    outcomes=[field("reported_yield", q(71, "%"), evidence(7, 11), ["product_d6_28_hd"]), field("yield_measurement_basis", "isolated", evidence(11), ["product_d6_28_hd"])],
    unresolved=["The detailed paragraph heading and first sentence label the starting material as [D6]-28, whereas Scheme 22 identifies the precursor as [D6]-27; the Scheme-22 assignment is retained with this source conflict explicit."],
))

records.append(record(
    "d6_28_terminal_h_d_exchange", "reported_experiment", [5, 7, 11],
    participants=[
        participant("d6_28_hd", "reactant", "[D6]-28-(CD3)2-H(D)", evidence(5, 7, 11), amounts=[field("mass", q(1.51, "g"), evidence(11)), field("amount", q(10.2, "mmol"), evidence(11))]),
        participant("nbuli", "reagent", "nBuLi (1.6 M in hexane)", evidence(5, 7, 11), amounts=[field("volume", q(9.56, "mL"), evidence(11)), field("amount", q(15.3, "mmol"), evidence(11)), field("concentration", q(1.6, "M"), evidence(11))]),
        participant("et2o", "solvent", "Et2O", evidence(7, 11), amounts=[field("volume", q(30, "mL"), evidence(11))]),
        participant("water", "reagent", "H2O", evidence(5, 7, 11), smiles="O"),
        participant("product_d6_28", "product", "[D6]-28-(CD3)2", evidence(5, 7, 11), amounts=[field("isolated_mass", q(0.58, "g"), evidence(11))]),
    ],
    conditions=[field("solvent", "Et2O", evidence(7, 11)), field("addition_temperature", q(-78, "°C"), evidence(5, 7, 11)), field("addition_time", q(50, "min"), evidence(11)), field("reaction_time_after_addition", q(20, "min"), evidence(11)), field("quench", "H2O at -78 °C, then allow to warm spontaneously to r.t.", evidence(5, 7, 11)), field("atmosphere", "argon", evidence(11)), field("workup", "Wash the organic layer with brine, dry over Na2SO4, and evaporate", evidence(11)), field("purification", "flash chromatography on silica gel (pentane/Et2O 50:1)", evidence(11))],
    outcomes=[field("reported_yield", q(38, "%"), evidence(7, 11), ["product_d6_28"]), field("yield_measurement_basis", "isolated", evidence(11), ["product_d6_28"])],
    notes=["The isolated product was used directly in the next step without further characterization."],
    unresolved=["The source calls this a terminal H/D exchange but does not report a final terminal-D percentage."],
))

records.append(record(
    "d6_1g_cross_coupling", "reported_experiment", [5, 7, 11],
    participants=[
        participant("allenoic_acid_allyl_ph", "reactant", "2-allyl-4-phenylbuta-2,3-dienoic acid", evidence(5, 7, 11), amounts=[field("mass", q(150, "mg"), evidence(11)), field("amount", q(0.75, "mmol"), evidence(11))]),
        participant("d6_28", "reactant", "[D6]-28-(CD3)2", evidence(5, 7, 11), amounts=[field("mass", q(221, "mg"), evidence(11)), field("amount", q(1.50, "mmol"), evidence(11))]),
        participant("pd_oac2", "catalyst", "Pd(OAc)2", evidence(7, 11), amounts=[field("mass", q(5, "mg"), evidence(11)), field("amount", q(0.020, "mmol"), evidence(11))]),
        participant("tfp", "catalyst", "TFP", evidence(7, 11), amounts=[field("mass", q(9, "mg"), evidence(11)), field("amount", q(0.040, "mmol"), evidence(11))]),
        participant("k2co3", "reagent", "K2CO3", evidence(7, 11), amounts=[field("mass", q(104, "mg"), evidence(11)), field("amount", q(0.75, "mmol"), evidence(11))]),
        participant("dmso", "solvent", "DMSO", evidence(7, 11), smiles="CS(C)=O", amounts=[field("volume", q(3, "mL"), evidence(11))]),
        participant("product_d6_1g", "product", "[D6]-1g-(CD3)2", evidence(5, 7, 11), amounts=[field("isolated_mass", q(110, "mg"), evidence(11))]),
    ],
    conditions=[field("solvent", "DMSO", evidence(7, 11)), field("temperature", None, evidence(11)), field("reaction_time", None, evidence(11)), field("atmosphere", None, evidence(11)), field("workup", None, evidence(11)), field("purification", None, evidence(11))],
    outcomes=[field("reported_yield", q(54, "%"), evidence(5, 7, 11), ["product_d6_1g"]), field("deuterium_content", q(95, "%"), evidence(5), ["product_d6_1g"]), field("yield_measurement_basis", None, evidence(11), ["product_d6_1g"])],
    unresolved=["Temperature, time, atmosphere, workup, purification, and yield basis are not reported in this abbreviated paragraph."],
))

records.append(record(
    "d6_1g_cycloisomerization", "reported_experiment", [5, 6, 7, 11],
    participants=[
        participant("substrate_d6_1g", "reactant", "[D6]-1g-(CD3)2", evidence(5, 6, 7, 11), amounts=[field("mass", q(90, "mg"), evidence(11)), field("amount", q(0.33, "mmol"), evidence(11))]),
        participant("xylene", "solvent", "xylene", evidence(5, 6, 7, 11), amounts=[field("volume", q(4, "mL"), evidence(11))]),
        participant("product_d6_6g", "product", "[D6]-6g", evidence(5, 6, 7, 11), amounts=[field("crude_product_mass", q(76, "mg"), evidence(11)), field("recrystallized_product_mass", q(66, "mg"), evidence(11))]),
    ],
    conditions=[field("solvent", "xylene", evidence(5, 6, 7, 11)), field("temperature", q(110, "°C"), evidence(5, 6, 7, 11)), field("reaction_time", q(6, "h"), evidence(5, 6, 7, 11)), field("atmosphere", None, evidence(11)), field("operation", "Monitor complete consumption by TLC and purify directly by flash chromatography on silica gel", evidence(11)), field("purification", "one recrystallization from ethyl acetate/petroleum ether", evidence(11))],
    outcomes=[field("reported_yield", q(73, "%"), evidence(5, 7, 11), ["product_d6_6g"]), field("deuterium_incorporation_at_4_position", q(60, "%"), evidence(5, 6, 7), ["product_d6_6g"]), field("methyl_group_deuterium_content_after_reaction", q(85, "%"), evidence(6, 7), ["product_d6_6g"]), field("yield_measurement_basis", "isolated after recrystallization", evidence(11), ["product_d6_6g"])],
    notes=["The precursor methyl-group deuterium content was reported to drop from 95% to 85%; Figure 5 supplies comparative 1H NMR evidence."],
    unresolved=["The detailed paragraph does not state an atmosphere; isotope-specific structures remain unverified."],
))

records.append(record(
    "scheme24_isotope_supported_pathway", "mechanism", [6, 7],
    notes=["Scheme 24 proposes 1A to 18A/20A by 1,5-H shift, 18A to 6A by 8pi electrocyclization, and 18A/20A equilibration through 29A by sequential 1,7-H shifts; the deuterium experiments are supporting evidence."],
    unresolved=["Intermediates 18A, 20A, and 29A are proposed rather than isolated; generic structures remain unverified."],
))


# Pages 8–10: exact preparations that refine existing scheme/scope records.
ev28 = evidence(2, 8)
records.append(record(
    "scheme5_prepare_1b", "substrate_scope_entry", [2, 8],
    participants=[
        participant("allenoic_acid_1b", "reactant", "2-isobutyl-4-phenylbuta-2,3-dienoic acid", ev28, amounts=[field("mass", q(217, "mg"), evidence(8)), field("amount", q(1.00, "mmol"), evidence(8))]),
        participant("propargyl_carbonate_1b", "reactant", "methyl 2-methylbut-3-yn-2-yl carbonate", ev28, amounts=[field("mass", q(282, "mg"), evidence(8)), field("amount", q(2.00, "mmol"), evidence(8))]),
        participant("pd_oac2", "catalyst", "Pd(OAc)2", ev28, amounts=[field("mass", q(11, "mg"), evidence(8)), field("amount", q(0.05, "mmol"), evidence(8))]),
        participant("tfp", "catalyst", "TFP", ev28, name="tri-2-furylphosphine", amounts=[field("mass", q(23, "mg"), evidence(8)), field("amount", q(0.10, "mmol"), evidence(8))]),
        participant("k2co3", "reagent", "K2CO3", ev28, amounts=[field("mass", q(138, "mg"), evidence(8)), field("amount", q(1.00, "mmol"), evidence(8))]),
        participant("dmso", "solvent", "DMSO", ev28, smiles="CS(C)=O", amounts=[field("volume", q(4, "mL"), evidence(8))]),
        participant("product_1b", "product", "3-isobutyl-4-(3-methylbuta-1,2-dienyl)-5-phenylfuran-2(5H)-one (1b)", ev28, amounts=[field("isolated_mass", q(106, "mg"), evidence(8))]),
    ],
    conditions=[field("solvent", "DMSO", ev28), field("temperature", q(30, "°C"), evidence(8)), field("reaction_time", q(3, "h"), evidence(8)), field("atmosphere", "argon", evidence(8)), field("operation", "Monitor complete consumption by TLC and purify the mixture directly", evidence(8)), field("purification", "flash chromatography on silica gel (petroleum ether/ethyl acetate 15:1)", evidence(8))],
    outcomes=[field("reported_yield", q(38, "%"), ev28, ["product_1b"]), field("yield_measurement_basis", "isolated", evidence(8), ["product_1b"])],
    unresolved=["The candidate molecular structure remains unverified despite the full name and analytical data."],
))

records.append(record(
    "scheme6_prepare_2a", "substrate_scope_entry", [2, 8],
    participants=[
        participant("zinc", "reagent", "flame-dried zinc", evidence(8), amounts=[field("mass", q(0.448, "g"), evidence(8)), field("amount", q(7.0, "mmol"), evidence(8))]),
        participant("dibromoethane", "reagent", "BrCH2CH2Br", evidence(8), name="1,2-dibromoethane", smiles="BrCCBr", amounts=[field("volume", q(20, "uL"), evidence(8))]),
        participant("tmscl", "reagent", "TMSCl", evidence(8), amounts=[field("volume", q(20, "uL"), evidence(8))]),
        participant("bromo_allene", "reactant", "1-bromo-3-methylbuta-1,2-diene", evidence(8)),
        participant("allenyl_zinc", "reactant", "allenylic zinc reagent (0.625 M in THF)", evidence(2, 8), amounts=[field("concentration", q(0.625, "M"), evidence(8)), field("volume_used", q(1.60, "mL"), evidence(8)), field("amount_used", q(1.00, "mmol"), evidence(8))]),
        participant("enone_iodide_2a", "reactant", "2-allyl-3-iodocyclohex-2-enone", evidence(2, 8), amounts=[field("mass", q(130, "mg"), evidence(8)), field("amount", q(0.5, "mmol"), evidence(8))]),
        participant("pd_pph3_2cl2", "catalyst", "Pd(PPh3)2Cl2", evidence(2, 8), amounts=[field("mass", q(18, "mg"), evidence(8)), field("amount", q(0.026, "mmol"), evidence(8))]),
        participant("thf", "solvent", "THF", evidence(2, 8), smiles="C1CCOC1", amounts=[field("zinc_preparation_volume", q(5, "mL"), evidence(8)), field("bromo_allene_solution_volume", q(3, "mL"), evidence(8)), field("coupling_volume", q(4, "mL"), evidence(8))]),
        participant("product_2a", "product", "2-allyl-3-(3-methylbuta-1,2-dienyl)cyclohex-2-enone (2a)", evidence(2, 8), amounts=[field("isolated_mass", q(64, "mg"), evidence(8))]),
    ],
    steps=[
        {"step_id": "allenylic_zinc_preparation", "participant_ids": ["zinc", "dibromoethane", "tmscl", "bromo_allene", "allenyl_zinc", "thf"], "conditions": [field("operation", "Heat zinc/THF with 1,2-dibromoethane to gentle reflux, cool to r.t., add TMSCl, then add the bromoallene solution dropwise after a gray suspension forms", evidence(8)), field("temperature_after_bromoallene_addition", "r.t.", evidence(8)), field("reaction_time_after_bromoallene_addition", q(4, "h"), evidence(8)), field("atmosphere", "flame-dried Schlenk tube", evidence(8))]},
        {"step_id": "negishi_coupling", "participant_ids": ["allenyl_zinc", "enone_iodide_2a", "pd_pph3_2cl2", "thf", "product_2a"], "conditions": [field("temperature", "r.t.", evidence(8)), field("reaction_time", q(1.5, "h"), evidence(8)), field("atmosphere", "flame-dried Schlenk tube", evidence(8)), field("operation", "Monitor complete consumption by TLC and remove THF by evaporation", evidence(8)), field("purification", "flash chromatography on silica gel (petroleum ether/ethyl acetate 25:1)", evidence(8))]},
    ],
    outcomes=[field("reported_yield", q(64, "%"), evidence(2, 8), ["product_2a"]), field("yield_measurement_basis", "isolated", evidence(8), ["product_2a"])],
    unresolved=["The allenylic zinc reagent is generated in situ and has no independently reported yield; complex participant structures remain unverified."],
))

records.append(record(
    "scheme7_1a_to_3a_isomers", "reported_experiment", [2, 3, 8, 9, 12],
    participants=[
        participant("substrate_1a", "reactant", "beta-allenylfuranone 1a", evidence(2, 3, 8), amounts=[field("printed_mass", q(140, "g"), evidence(8)), field("amount", q(0.40, "mmol"), evidence(8))]),
        participant("xylene", "solvent", "xylene", evidence(2, 3, 8), amounts=[field("volume", q(6, "mL"), evidence(8))]),
        participant("product_ee_3a", "product", "(E,E)-3a", evidence(2, 3, 8, 9), amounts=[field("isolated_mass", q(41, "mg"), evidence(8))]),
        participant("product_ez_3a", "product", "(E,Z)-3a", evidence(2, 3, 8, 12), amounts=[field("isolated_mass", q(10, "mg"), evidence(8))]),
        participant("unidentified_products", "product", "unidentified products", evidence(8), amounts=[field("mass", q(70, "mg"), evidence(8))]),
    ],
    conditions=[field("solvent", "xylene", evidence(2, 3, 8)), field("temperature", "reflux", evidence(2, 3, 8)), field("reaction_time", q(6, "h"), evidence(8)), field("atmosphere", "argon", evidence(8)), field("operation", "Monitor complete consumption by TLC and purify directly by flash chromatography on silica gel", evidence(8))],
    outcomes=[field("isolated_yield_ee_3a", q(29, "%"), evidence(8), ["product_ee_3a"]), field("isolated_yield_ez_3a", q(7, "%"), evidence(8), ["product_ez_3a"]), field("yield_measurement_basis", "isolated", evidence(8), ["product_ee_3a", "product_ez_3a"])],
    notes=["(E,Z)-3a was the less-polar fraction and (E,E)-3a the more-polar fraction; CCDC 647592 contains crystallographic data for (E,Z)-3a."],
    unresolved=["The detailed paragraph visibly prints '140 g' for 0.40 mmol 1a, an internally inconsistent mass; the printed value is retained and no correction to mg is silently inferred.", "The identities of the 70 mg unidentified products and complex structures/stereochemistry remain unverified."],
))

records.append(record(
    "scheme9_1d_to_5d", "reported_experiment", [3, 9, 12],
    participants=[
        participant("substrate_1d", "reactant", "1d", evidence(3, 9), amounts=[field("mass", q(53, "mg"), evidence(9)), field("amount", q(0.17, "mmol"), evidence(9))]),
        participant("xylene", "solvent", "xylene", evidence(3, 9), amounts=[field("volume", q(4, "mL"), evidence(9))]),
        participant("trans_5d", "product", "trans-5d", evidence(3, 9, 12), amounts=[field("isolated_mass", q(24, "mg"), evidence(9))]),
        participant("cis_5d", "product", "cis-5d", evidence(3, 9), amounts=[field("isolated_mass", q(13, "mg"), evidence(9))]),
    ],
    conditions=[field("solvent", "xylene", evidence(3, 9)), field("temperature", q(200, "°C"), evidence(3, 9)), field("reaction_time", q(5, "h"), evidence(3, 9)), field("atmosphere", "argon", evidence(9)), field("operation", "Heat in a screw-cap Schlenk tube and purify the mixture directly", evidence(3, 9)), field("purification", "flash chromatography on silica gel", evidence(9))],
    outcomes=[field("combined_reported_yield", q(70, "%"), evidence(3), ["trans_5d", "cis_5d"]), field("isolated_yield_trans_5d", q(45, "%"), evidence(9), ["trans_5d"]), field("isolated_yield_cis_5d", q(25, "%"), evidence(9), ["cis_5d"]), field("trans_cis_ratio", "1.9:1", evidence(3), ["trans_5d", "cis_5d"]), field("yield_measurement_basis", "isolated", evidence(9), ["trans_5d", "cis_5d"])],
    notes=["CCDC 647595 contains crystallographic data for trans-5d."],
    unresolved=["Complex product structures and relative stereochemistry remain machine-unverified."],
))

# Characterization-only page-12 links for existing experiments.
for suffix, note, unresolved in [
    ("scheme10_1e_to_5e", "CCDC 647594 contains crystallographic data for trans-5e.", "No supplied CIF was explicitly associated; the machine structure remains unverified."),
    ("scheme12_1s_to_6s_7s", "CCDC 647593 contains crystallographic data for 7s.", "No supplied CIF was explicitly associated; the complex structures remain unverified."),
]:
    old = copy.deepcopy(EXISTING[f"{DOC}:{suffix}"])
    old["status"] = "candidate"
    old["evidence_ids"] = list(dict.fromkeys(old["evidence_ids"] + evidence(12)))
    if not any(n.get("value") == note for n in old["notes"]):
        old["notes"].append(fact(note, evidence(12)))
    old["review"]["method"] = "none"
    old["review"]["checked_fields"] = []
    old["review"]["unresolved"] = list(dict.fromkeys(old["review"]["unresolved"] + [unresolved]))
    records.append(old)

records.append(record(
    "scheme12_1r_to_6r_7r", "reported_experiment", [4, 9],
    participants=[
        participant("substrate_1r", "reactant", "1r", evidence(4, 9), amounts=[field("mass", q(52, "mg"), evidence(9)), field("amount", q(0.178, "mmol"), evidence(9))]),
        participant("xylene", "solvent", "xylene", evidence(4, 9), amounts=[field("volume", q(4, "mL"), evidence(9))]),
        participant("product_6r", "product", "6r", evidence(4, 9), amounts=[field("isolated_mass", q(35, "mg"), evidence(9))]),
        participant("product_7r", "product", "7r", evidence(4, 9), amounts=[field("isolated_mass", q(6, "mg"), evidence(9))]),
    ],
    conditions=[field("solvent", "xylene", evidence(4, 9)), field("temperature", q(100, "°C"), evidence(4, 9)), field("reaction_time", q(6, "h"), evidence(4, 9)), field("atmosphere", None, evidence(9)), field("operation", "Monitor complete consumption by TLC and purify directly by flash chromatography on silica gel", evidence(9))],
    outcomes=[field("isolated_yield_6r", q(67, "%"), evidence(4, 9), ["product_6r"]), field("isolated_yield_7r", q(12, "%"), evidence(4, 9), ["product_7r"]), field("diastereomer_ratio_7r", "1:1", evidence(4), ["product_7r"]), field("yield_measurement_basis", "isolated", evidence(9), ["product_6r", "product_7r"])],
    unresolved=["The detailed paragraph does not state atmosphere or chromatography eluent; complex structures and the 7r diastereomer assignments remain unverified."],
))

records.append(record(
    "scheme13_2a_dimerization", "reported_experiment", [4, 6, 9],
    participants=[
        participant("substrate_2a", "reactant", "2a", evidence(4, 6, 9), amounts=[field("mass", q(74, "mg"), evidence(9)), field("amount", q(0.37, "mmol"), evidence(9))]),
        participant("xylene", "solvent", "xylene", evidence(4, 6, 9), amounts=[field("volume", q(4, "mL"), evidence(9))]),
        participant("product_8aa", "product", "8aa", evidence(4, 6, 9), amounts=[field("isolated_mass", q(26, "mg"), evidence(9))]),
        participant("product_8ab", "product", "8ab", evidence(4, 6, 9), amounts=[field("isolated_mass", q(34, "mg"), evidence(9))]),
    ],
    conditions=[field("solvent", "xylene", evidence(4, 6, 9)), field("temperature", q(80, "°C"), evidence(4, 6, 9)), field("reaction_time", q(3, "h"), evidence(4, 6, 9)), field("atmosphere", "argon", evidence(9)), field("operation", "Monitor complete consumption by TLC and purify directly", evidence(9)), field("purification", "flash chromatography on silica gel (petroleum ether/ethyl acetate 20:1 then 10:1)", evidence(9))],
    outcomes=[field("combined_reported_yield", q(81, "%"), evidence(6), ["product_8aa", "product_8ab"]), field("isolated_yield_8aa", q(35, "%"), evidence(9), ["product_8aa"]), field("isolated_yield_8ab", q(46, "%"), evidence(9), ["product_8ab"]), field("product_ratio", "8aa:8ab = 1:1.3", evidence(6), ["product_8aa", "product_8ab"]), field("yield_measurement_basis", "isolated", evidence(9), ["product_8aa", "product_8ab"])],
    notes=["The products are described as intermolecular Diels–Alder products of two molecules of possible intermediate 9a."],
    unresolved=["Complex product structures and stereochemistry remain unverified."],
))

records.append(record(
    "scheme13_bromination_8ab", "reported_experiment", [4, 6, 9, 12],
    participants=[
        participant("substrate_8ab", "reactant", "8ab", evidence(4, 6, 9), amounts=[field("mass", q(41, "mg"), evidence(9)), field("amount", q(0.10, "mmol"), evidence(9))]),
        participant("br2", "reagent", "Br2 (0.188 M in CH2Cl2)", evidence(4, 6, 9), smiles="BrBr", amounts=[field("solution_volume", q(1.0, "mL"), evidence(9)), field("concentration", q(0.188, "M"), evidence(9))]),
        participant("ch2cl2", "solvent", "CH2Cl2", evidence(4, 6, 9), smiles="ClCCl", amounts=[field("reaction_volume", q(3, "mL"), evidence(9))]),
        participant("na2s2o3", "reagent", "aqueous Na2S2O3", evidence(9)),
        participant("product_10aba", "product", "10aba", evidence(4, 6, 9, 12), amounts=[field("isolated_mass", q(28, "mg"), evidence(9))]),
        participant("product_10abb", "product", "10abb", evidence(4, 6, 9), amounts=[field("isolated_mass", q(19, "mg"), evidence(9))]),
    ],
    conditions=[field("solvent", "CH2Cl2", evidence(4, 6, 9)), field("temperature", "r.t.", evidence(9)), field("reaction_time", q(15, "min"), evidence(9)), field("atmosphere", None, evidence(9)), field("workup", "Add aqueous Na2S2O3, extract with ether (50 mL), wash with brine, dry over anhydrous Na2SO4, and evaporate", evidence(9)), field("purification", "flash chromatography on silica gel (petroleum ether/ethyl acetate 10:1)", evidence(9))],
    outcomes=[field("combined_reported_yield", q(96, "%"), evidence(6), ["product_10aba", "product_10abb"]), field("isolated_yield_10aba", q(57, "%"), evidence(9), ["product_10aba"]), field("isolated_yield_10abb", q(39, "%"), evidence(9), ["product_10abb"]), field("product_ratio", "10aba:10abb = 1.5:1", evidence(6), ["product_10aba", "product_10abb"]), field("yield_measurement_basis", "isolated", evidence(9), ["product_10aba", "product_10abb"])],
    notes=["CCDC 647590 contains crystallographic data for 10aba."],
    unresolved=["The atmosphere and aqueous Na2S2O3 concentration/amount are not stated; complex structures remain unverified."],
))

def trapping_record(suffix, pages, trap_id, trap_label, trap_amounts, product_id, product_label,
                    product_mass, reaction_time, reported_yield, solvent_volume, eluent, extra_notes=None):
    ev = evidence(*pages)
    return record(
        suffix, "substrate_scope_entry", pages,
        participants=[
            participant("substrate_2a", "reactant", "2a", ev, amounts=[field("mass", q(40 if trap_id == "13a" else 41, "mg"), evidence(max(pages))), field("amount", q(0.20, "mmol"), evidence(max(pages)))]),
            participant(f"reactant_{trap_id}", "reactant", trap_label, ev, amounts=trap_amounts),
            participant("xylene", "solvent", "xylene", ev, amounts=[field("volume", q(solvent_volume, "mL"), evidence(max(pages)))]),
            participant(f"product_{product_id}", "product", product_label, ev, amounts=[field("isolated_mass", q(product_mass, "mg"), evidence(max(pages)))]),
        ],
        conditions=[field("solvent", "xylene", ev), field("temperature", q(55, "°C"), ev), field("reaction_time", q(reaction_time, "h"), ev), field("atmosphere", "argon", evidence(max(pages))), field("operation", "Monitor complete consumption by TLC and purify directly", evidence(max(pages))), field("purification", f"flash chromatography on silica gel ({eluent})", evidence(max(pages)))],
        outcomes=[field("reported_yield", q(reported_yield, "%"), ev, [f"product_{product_id}"]), field("yield_measurement_basis", "isolated", evidence(max(pages)), [f"product_{product_id}"])],
        notes=(extra_notes or []) + ["The product was reported as a single/highly favored diastereomer in the discussion."],
        unresolved=["Complex product connectivity and stereochemistry remain unverified."],
    )

records.append(trapping_record(
    "scheme15_2a_13a_to_14aa", [5, 6, 9, 12], "13a", "maleic anhydride 13a",
    [field("mass", q(98, "mg"), evidence(9)), field("amount", q(1.00, "mmol"), evidence(9))],
    "14aa", "14aa", 29, 24, 49, 8, "petroleum ether/ethyl acetate 5:1",
    ["CCDC 647591 contains crystallographic data for 14aa."],
))
records.append(trapping_record(
    "scheme15_2a_13c_to_14ac", [5, 6, 9], "13c", "N-phenylmaleimide 13c",
    [field("mass", q(69, "mg"), evidence(9)), field("amount", q(0.40, "mmol"), evidence(9))],
    "14ac", "14ac", 69, 36, 91, 3, "petroleum ether/ethyl acetate 4:1",
))
records.append(trapping_record(
    "scheme15_2a_13d_to_14ad", [5, 6, 9, 10], "13d", "dimethyl but-2-ynedioate 13d",
    [field("mass", q(114, "mg"), evidence(9)), field("amount", q(0.80, "mmol"), evidence(9))],
    "14ad", "14ad", 36, 34, 52, 8, "petroleum ether/ethyl acetate 5:1",
))

records.append(record(
    "scheme16_2c_cycloisomerization", "reported_experiment", [5, 6, 10],
    participants=[
        participant("substrate_2c", "reactant", "2c (R=nBu)", evidence(5, 6, 10), amounts=[field("mass", q(62, "mg"), evidence(10)), field("amount", q(0.24, "mmol"), evidence(10))]),
        participant("xylene", "solvent", "xylene", evidence(5, 6, 10), amounts=[field("volume", q(4, "mL"), evidence(10))]),
        participant("product_15c", "product", "15c", evidence(5, 6, 10), amounts=[field("isolated_mass", q(35, "mg"), evidence(10))]),
        participant("product_9c", "product", "9c", evidence(5, 6, 10), amounts=[field("isolated_mass", q(5, "mg"), evidence(10))]),
    ],
    conditions=[field("solvent", "xylene", evidence(5, 6, 10)), field("temperature", q(90, "°C"), evidence(5, 6, 10)), field("reaction_time", q(2, "h"), evidence(5, 6, 10)), field("atmosphere", "argon", evidence(10)), field("operation", "Monitor complete consumption by TLC and purify directly", evidence(10)), field("purification", "flash chromatography on silica gel (petroleum ether/ethyl acetate 50:1)", evidence(10))],
    outcomes=[field("scheme16_reported_yield_15c", q(57, "%"), evidence(6), ["product_15c"]), field("detailed_paragraph_isolated_yield_15c", q(56, "%"), evidence(10), ["product_15c"]), field("isolated_yield_9c", q(8, "%"), evidence(5, 6, 10), ["product_9c"]), field("yield_measurement_basis", "isolated", evidence(10), ["product_15c", "product_9c"])],
    unresolved=["Scheme 16 reports 57% for 15c, whereas the detailed paragraph reports 35 mg (56%); both values are retained.", "Complex product structures remain unverified."],
))

records.append(record(
    "scheme16_2d_cycloisomerization", "reported_experiment", [5, 6, 10],
    participants=[
        participant("substrate_2d", "reactant", "2d (R=Ph)", evidence(5, 6, 10), amounts=[field("mass", q(64, "mg"), evidence(10)), field("amount", q(0.23, "mmol"), evidence(10))]),
        participant("xylene", "solvent", "xylene", evidence(5, 6, 10), amounts=[field("volume", q(4, "mL"), evidence(10))]),
        participant("product_15d", "product", "15d", evidence(5, 6, 10), amounts=[field("isolated_mass", q(49, "mg"), evidence(10))]),
    ],
    conditions=[field("solvent", "xylene", evidence(5, 6, 10)), field("temperature", q(90, "°C"), evidence(5, 6, 10)), field("reaction_time", q(2, "h"), evidence(5, 6, 10)), field("atmosphere", "argon", evidence(10)), field("operation", "Monitor complete consumption by TLC and purify directly", evidence(10)), field("purification", "flash chromatography on silica gel (petroleum ether/ethyl acetate 25:1)", evidence(10))],
    outcomes=[field("reported_yield", q(77, "%"), evidence(5, 6, 10), ["product_15d"]), field("yield_measurement_basis", "isolated", evidence(10), ["product_15d"])],
    unresolved=["Complex product structure and stereochemistry remain unverified."],
))

records.append(record(
    "scheme17_16_to_9e", "reported_experiment", [5, 6, 10],
    participants=[
        participant("substrate_16", "reactant", "16", evidence(5, 6, 10), amounts=[field("mass", q(58, "mg"), evidence(10)), field("amount", q(0.25, "mmol"), evidence(10))]),
        participant("triethyl_orthoacetate", "reactant", "CH3C(OEt)3", evidence(5, 6, 10), name="triethyl orthoacetate", smiles="CC(OCC)(OCC)OCC", amounts=[field("initial_mass", q(162, "mg"), evidence(10)), field("initial_amount", q(1.00, "mmol"), evidence(10)), field("second_mass", q(162, "mg"), evidence(10)), field("second_amount", q(1.00, "mmol"), evidence(10))]),
        participant("xylene", "solvent", "xylene", evidence(5, 6, 10), amounts=[field("volume", q(6, "mL"), evidence(10))]),
        participant("product_9e", "product", "9e", evidence(5, 6, 10), amounts=[field("isolated_mass", q(31, "mg"), evidence(10))]),
    ],
    steps=[
        {"step_id": "initial_heating", "participant_ids": ["substrate_16", "triethyl_orthoacetate", "xylene"], "conditions": [field("temperature", q(140, "°C"), evidence(6, 10)), field("reaction_time", q(1, "h"), evidence(10)), field("atmosphere", "argon", evidence(10)), field("operation", "Remove ethanol by distillation", evidence(10))]},
        {"step_id": "second_addition_and_heating", "participant_ids": ["triethyl_orthoacetate", "product_9e"], "conditions": [field("reaction_time", q(2, "h"), evidence(10)), field("temperature", q(140, "°C"), evidence(10)), field("operation", "Cool to r.t. and purify directly by flash chromatography on silica gel (petroleum ether/ethyl acetate 20:1)", evidence(10))]},
    ],
    outcomes=[field("reported_yield", q(41, "%"), evidence(5, 6, 10), ["product_9e"]), field("yield_measurement_basis", "isolated", evidence(10), ["product_9e"])],
    notes=["Other unidentified products were also obtained; the text describes tetraene 2e as formed in situ and 9e as the tricyclic product."],
    unresolved=["No yield for the in-situ 2e intermediate or identities/yields for the other products are reported; complex structures remain unverified."],
))


# Exact coverage for pages 7–12.
page_records = {
    7: [
        "scheme19_stereochemical_15h_shift_pathways", "d5_hexyl_propiolate_22_esterification",
        "d1_hexyl_3_deuteropropiolate_23_exchange", "d5_allyl_mesylate_24_synthesis",
        "d5_25_cui_coupling", "d5_26_palladium_carbonylation", "d5_1g_cross_coupling",
        "d5_1g_cycloisomerization", "d6_27_synthesis", "d6_28_carbonate_synthesis",
        "d6_28_terminal_h_d_exchange", "d6_1g_cross_coupling", "d6_1g_cycloisomerization",
        "scheme24_isotope_supported_pathway",
    ],
    8: ["scheme25_reactivity_summary", "scheme5_prepare_1b", "scheme6_prepare_2a", "scheme7_1a_to_3a_isomers"],
    9: ["scheme7_1a_to_3a_isomers", "scheme9_1d_to_5d", "scheme12_1r_to_6r_7r", "scheme13_2a_dimerization", "scheme13_bromination_8ab", "scheme15_2a_13a_to_14aa", "scheme15_2a_13c_to_14ac", "scheme15_2a_13d_to_14ad"],
    10: ["scheme15_2a_13d_to_14ad", "scheme16_2c_cycloisomerization", "scheme16_2d_cycloisomerization", "scheme17_16_to_9e", "d1_hexyl_3_deuteropropiolate_23_exchange", "d5_allyl_mesylate_24_synthesis", "d5_25_cui_coupling", "d5_26_palladium_carbonylation", "d5_1g_cross_coupling"],
    11: ["d5_1g_cross_coupling", "d5_1g_cycloisomerization", "d6_28_carbonate_synthesis", "d6_28_terminal_h_d_exchange", "d6_1g_cross_coupling", "d6_1g_cycloisomerization"],
    12: ["scheme7_1a_to_3a_isomers", "scheme9_1d_to_5d", "scheme10_1e_to_5e", "scheme12_1s_to_6s_7s", "scheme13_bromination_8ab", "scheme15_2a_13a_to_14aa"],
}

coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 7, "state": "attempted",
            "regions": [
                {"region": "upper-left Scheme 19", "finding": "Proposed stereochemical 1,5-H-shift pathways classified as mechanism, not isolated experiments.", "evidence_ids": evidence(7)},
                {"region": "middle/lower-left Schemes 20–21 and Figure 5", "finding": "The [D5] precursor sequence was split into executed stages; isotope redistribution and NMR evidence were merged into the existing cycloisomerization record.", "evidence_ids": evidence(7)},
                {"region": "upper/middle-right Schemes 22–23", "finding": "The [D6] precursor stages and isotope-probe cycloisomerization were linked to their existing records with scheme yields and isotope percentages preserved.", "evidence_ids": evidence(7)},
            ],
            "record_ids": [f"{DOC}:{x}" for x in page_records[7]],
            "unresolved": ["Many scheme-only stages omit scale, time, temperature, atmosphere, workup, purification, or yield basis.", "Isotope-specific and mechanistic structures remain unverified."],
        },
        {
            "page": 8, "state": "attempted",
            "regions": [
                {"region": "upper-left Scheme 24 and middle-left Scheme 25/conclusion", "finding": "Scheme 24 is an isotope-supported proposed pathway; Scheme 25 is a generic reaction-family summary, not an extra experiment.", "evidence_ids": evidence(8)},
                {"region": "right-column preparations of 1b and 2a", "finding": "Exact 1b preparation and two-stage 2a/allenyl-zinc procedure merged into existing Scheme-5/6 records.", "evidence_ids": evidence(8)},
                {"region": "lower-right preparation of (E,E)/(E,Z)-3a", "finding": "Detailed 1a thermal isomerization quantities, operations, product masses, and yields merged into the existing Scheme-7 record.", "evidence_ids": evidence(8)},
            ],
            "record_ids": [f"{DOC}:{x}" for x in page_records[8]],
            "unresolved": ["The 1a paragraph visibly prints 140 g for 0.40 mmol; the inconsistency is retained without silently changing the unit.", "The paper refers analytical data/general methods to SI of references [4] and [15], but no SI source was supplied or associated."],
        },
        {
            "page": 9, "state": "attempted",
            "regions": [
                {"region": "left column: 3a continuation, 5d, 6r/7r, and 8aa/8ab", "finding": "Compound-specific procedures merged into four existing thermal/cycloisomerization records with individual product masses and yields.", "evidence_ids": evidence(9)},
                {"region": "right column: 8ab bromination and 14aa/14ac/14ad trapping", "finding": "Exact bromination and three trapping procedures merged; the 14ad procedure continues onto page 10.", "evidence_ids": evidence(9)},
            ],
            "record_ids": [f"{DOC}:{x}" for x in page_records[9]],
            "unresolved": ["The bromination atmosphere and aqueous Na2S2O3 concentration/amount are not stated.", "Complex products and stereochemistry remain unverified."],
        },
        {
            "page": 10, "state": "attempted",
            "regions": [
                {"region": "left column: 14ad completion, 2c/2d cycloisomerizations, and 16-to-9e", "finding": "Exact procedures merged into existing records; the 15c scheme/detailed yield conflict (57% vs 56%) is retained.", "evidence_ids": evidence(10)},
                {"region": "right column: [D]-23, [D5]-24, [D5]-25, [D5]-26, and start of [D5]-1g", "finding": "Detailed isotope-synthesis stages extracted or merged with quantities, staged operations, yields, and missing fields explicit.", "evidence_ids": evidence(10)},
            ],
            "record_ids": [f"{DOC}:{x}" for x in page_records[10]],
            "unresolved": ["Scheme 20 gives 62% for [D5]-1g while the detailed paragraph gives 53%; both are retained.", "Several isotope-specific structures and stage boundaries require expert review."],
        },
        {
            "page": 11, "state": "attempted",
            "regions": [
                {"region": "left column experimental continuation", "finding": "[D5]-1g/[D5]-6g and [D6]-28/[D6]-1g/[D6]-6g detailed procedures merged into existing isotope records.", "evidence_ids": evidence(11)},
                {"region": "right column acknowledgements and references", "finding": "No additional present-paper experiment; citations were not mined as associated sources.", "evidence_ids": evidence(11)},
            ],
            "record_ids": [f"{DOC}:{x}" for x in page_records[11]],
            "unresolved": ["The detailed [D6]-28 carbonate paragraph appears to mislabel its precursor as [D6]-28, conflicting with Scheme 22's [D6]-27 precursor.", "Several abbreviated cross-couplings omit temperature, time, atmosphere, workup, purification, or yield basis."],
        },
        {
            "page": 12, "state": "attempted",
            "regions": [
                {"region": "left/right crystallographic notes [10]–[12] and [19]–[21]", "finding": "Crystal-data notes for (E,Z)-3a, trans-5d, trans-5e, 7s, 10aba, and 14aa were linked as characterization evidence; no duplicate reaction was created.", "evidence_ids": evidence(12)},
                {"region": "remaining reference list and publication metadata", "finding": "No new present-paper reaction, table, experimental procedure, or mechanism; references remain citations only.", "evidence_ids": evidence(12)},
            ],
            "record_ids": [f"{DOC}:{x}" for x in page_records[12]],
            "unresolved": ["The cited CCDC files and other external sources were not supplied or explicitly associated and were not imported.", "Crystal characterization does not verify the machine molecular structures."],
        },
    ],
}


raw_path = OUT / "raw_model/records_pages_0007_0012.json"
raw_path.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
(OUT / "coverage").mkdir(parents=True, exist_ok=True)
(OUT / "coverage/pages_0007_0012.json").write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

tasks_path = OUT / "tasks.json"
tasks = json.loads(tasks_path.read_text())
for task in tasks:
    if task["document_id"] == DOC and any(task["task_id"] == f"{DOC}:page{page}:text" for page in range(7, 13)):
        task["state"] = "attempted"
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"records": len(records), "new_record_ids": [r["record_id"] for r in records if r["record_id"] not in EXISTING], "coverage_pages": [p["page"] for p in coverage["pages"]]}, ensure_ascii=False, indent=2))
