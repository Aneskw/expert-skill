#!/usr/bin/env python3
"""Build the machine-extracted page 1--6 records for the Jiang whisky-lactone paper."""

import json
from pathlib import Path

DOC = "doc_fac6b7e158197ca3"
OUT = Path(__file__).with_name("records_pages_0001_0006.json")


def evidence(*pages):
    result = []
    for page in pages:
        result.extend([f"{DOC}:page{page}:image", f"{DOC}:page{page}:text"])
    return result


def fact(value, ev):
    return {
        "value": value,
        "evidence_ids": list(ev) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def qty(number, unit, **extra):
    return {"number": number, "unit": unit, **extra}


def field(name, value, ev, targets=None):
    result = {"name": name, "fact": fact(value, ev)}
    if targets:
        result["target_entity_ids"] = targets
    return result


def participant(entity_id, role, label, ev, *, name=None, smiles=None, amounts=()):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, ev),
        "name": fact(name, ev) if name is not None else fact(None, ev),
        "smiles": fact(smiles, ev) if smiles is not None else fact(None, ev),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": [field(n, v, ev) for n, v in amounts],
    }


def step(step_id, participant_ids, ev, **conditions):
    return {
        "step_id": step_id,
        "participant_ids": participant_ids,
        "conditions": [field(name, value, ev) for name, value in conditions.items()],
    }


def record(
    suffix,
    pages,
    kind,
    participants,
    steps,
    outcomes=(),
    notes=(),
    unresolved=(),
):
    ev = evidence(*pages)
    return {
        "record_id": f"{DOC}:{suffix}",
        "document_id": DOC,
        "source_reaction_id": suffix,
        "record_kind": kind,
        "status": "needs_review",
        "completeness": "partial",
        "evidence_ids": ev,
        "participants": participants(ev),
        "steps": steps(ev),
        "outcomes": [field(n, v, ev, t) for n, v, t in outcomes],
        "notes": [fact(value, ev) for value in notes],
        "review": {
            "method": "model",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": list(unresolved),
        },
    }


P = participant
S = step
Q = qty
records = []

# Page 1: prior-work generic iodolactonization, explicitly kept out of current experiments.
records.append(record(
    "equation1_prior_iodolactonization", (1,), "literature_example",
    lambda ev: [
        P("generic_allenoic_acid", "reactant", "generic gamma-allenoic acid", ev),
        P("iodine", "reagent", "I2", ev, name="iodine", smiles="II"),
        P("cyclohexane", "solvent", "cyclohexane", ev, smiles="C1CCCCC1"),
        P("generic_iodolactone", "product", "generic trans iodolactone", ev),
    ],
    lambda ev: [S("prior_iodolactonization", ["generic_allenoic_acid", "iodine", "cyclohexane"], ev,
                         temperature="r.t.", operation="electrophilic iodolactonization")],
    notes=("Equation (1) is attributed to the authors' earlier work [14a], not a newly reported batch in this paper.",),
    unresolved=("Generic R1/R2 structures cannot be expanded to unique SMILES.", "No batch quantities, duration, or yield are stated in Equation (1)."),
))

# Scheme 2: the racemic route, one record per arrow/stage.
records.append(record(
    "scheme2_a_claisen_rearrangement_to_ethyl_allenoate", (2, 3), "reported_experiment",
    lambda ev: [
        P("rac_1", "reactant", "1", ev, name="pent-1-yn-3-ol", smiles="CCC(O)C#C", amounts=(("mass", Q(2.0492, "g")), ("amount", Q(0.024, "mol")))),
        P("triethyl_orthoacetate", "reagent", "EtC(OEt)3", ev, name="triethyl orthoacetate", amounts=(("mass", Q(12.6643, "g")), ("amount", Q(0.072, "mol")))),
        P("propionic_acid", "catalyst", "EtCO2H", ev, name="propionic acid", smiles="CCC(=O)O", amounts=(("volume", Q(0.7, "mL")), ("mass", Q(0.693, "g")), ("amount", Q(0.0094, "mol")))),
        P("ethyl_allenoate", "product", "ethyl 2-methylhepta-3,4-dienoate", ev, smiles="CCOC(=O)C(C)C=C=CCC"),
    ],
    lambda ev: [S("heat_with_dean_stark", ["rac_1", "triethyl_orthoacetate", "propionic_acid"], ev,
                         temperature=Q(140, "°C"), time=Q(3.5, "h"), operation="Dean–Stark removal of formed ethanol and excess orthoester; low-boiling material removed; silica chromatography")],
    notes=("The ethyl allenoate intermediate was used in the next step without further characterization.",),
    unresolved=("No stage-specific yield was reported; only the two-step yield to alcohol 2 is available.",),
))
records.append(record(
    "scheme2_b_lialh4_reduction_to_rac_2", (2, 3), "reported_experiment",
    lambda ev: [
        P("ethyl_allenoate", "reactant", "ethyl 2-methylhepta-3,4-dienoate", ev, smiles="CCOC(=O)C(C)C=C=CCC"),
        P("lialh4", "reagent", "LiAlH4", ev, name="lithium aluminium hydride", smiles="[Li+].[AlH4-]", amounts=(("mass", Q(1.1154, "g")), ("amount", Q(0.029, "mol")))),
        P("thf", "solvent", "THF", ev, name="tetrahydrofuran", smiles="C1CCOC1", amounts=(("volume", Q(30, "mL")),)),
        P("rac_2", "product", "2", ev, name="2-methylhepta-3,4-dien-1-ol", smiles="CCC=C=CC(C)CO"),
    ],
    lambda ev: [S("lialh4_reduction", ["ethyl_allenoate", "lialh4", "thf"], ev,
                         temperature=Q(0, "°C"), time=Q(2.3, "h"), atmosphere="N2", operation="dropwise addition to ice-cold suspension; TLC monitoring; NaOH quench; filtration; silica chromatography")],
    outcomes=(("combined_isolated_yield", Q(68, "%"), ["rac_2"]), ("product_mass", Q(2.0799, "g"), ["rac_2"]), ("yield_measurement_basis", "combined yield for Scheme 2 steps a and b", ["rac_2"])),
    unresolved=("The carried-forward ethyl allenoate amount is not independently reported.",),
))
records.append(record(
    "scheme2_c_tosylation_of_rac_2", (2, 3), "reported_experiment",
    lambda ev: [
        P("rac_2", "reactant", "2", ev, name="2-methylhepta-3,4-dien-1-ol", smiles="CCC=C=CC(C)CO", amounts=(("mass", Q(4.2457, "g")), ("amount", Q(0.034, "mol")))),
        P("ptscl", "reagent", "pTsCl", ev, name="p-toluenesulfonyl chloride", smiles="Cc1ccc(S(=O)(=O)Cl)cc1", amounts=(("mass", Q(19.5171, "g")), ("amount", Q(0.102, "mol")))),
        P("pyridine", "solvent", "pyridine", ev, smiles="n1ccccc1", amounts=(("volume", Q(30, "mL")),)),
        P("rac_tosylate", "product", "tosylate derived from 2", ev),
    ],
    lambda ev: [S("tosylation", ["rac_2", "ptscl", "pyridine"], ev,
                         temperature={"minimum": 0, "maximum": 4, "unit": "°C", "raw_text": "0–4 °C"}, time=Q(6, "h"), operation="portionwise addition; ice-water quench; ether extraction; water/brine wash; drying and concentration")],
    notes=("The tosylate was carried directly to the NaCN displacement without purification.",),
    unresolved=("No stage-specific yield or isolated tosylate mass was reported.",),
))
records.append(record(
    "scheme2_d_cyanide_displacement_to_rac_3", (2, 3), "reported_experiment",
    lambda ev: [
        P("rac_tosylate", "reactant", "tosylate derived from 2", ev),
        P("nacn", "reagent", "NaCN", ev, name="sodium cyanide", smiles="[Na+].[C-]#N", amounts=(("mass", Q(1.7913, "g")), ("amount", Q(0.037, "mol")))),
        P("dmso", "solvent", "DMSO", ev, name="dimethyl sulfoxide", smiles="CS(C)=O", amounts=(("volume", Q(30, "mL")),)),
        P("rac_3", "product", "3", ev, name="3-methylocta-4,5-dienenitrile", smiles="CCC=C=CC(C)CC#N"),
    ],
    lambda ev: [S("cyanide_displacement", ["rac_tosylate", "nacn", "dmso"], ev,
                         temperature="r.t.", time=Q(1.5, "d"), operation="water quench; ether extraction; water/brine wash; drying; evaporation; silica chromatography")],
    outcomes=(("combined_isolated_yield", Q(71, "%"), ["rac_3"]), ("product_mass", Q(3.2459, "g"), ["rac_3"]), ("yield_measurement_basis", "combined yield for Scheme 2 steps c and d", ["rac_3"])),
    unresolved=("The carried-forward tosylate amount is not independently reported.",),
))
records.append(record(
    "scheme2_e_nitrile_hydrolysis_to_rac_4", (2, 3, 4), "reported_experiment",
    lambda ev: [
        P("rac_3", "reactant", "3", ev, name="3-methylocta-4,5-dienenitrile", smiles="CCC=C=CC(C)CC#N", amounts=(("mass", Q(1.0716, "g")), ("amount", Q(7.5, "mmol")))),
        P("naoh", "reagent", "NaOH", ev, name="sodium hydroxide", smiles="[Na+].[OH-]", amounts=(("mass", Q(4.0802, "g")), ("amount", Q(100, "mmol")))),
        P("water", "solvent", "H2O", ev, name="water", smiles="O", amounts=(("volume", Q(5, "mL")),)),
        P("ethanol", "solvent", "EtOH", ev, name="ethanol", smiles="CCO", amounts=(("volume", Q(15, "mL")),)),
        P("rac_4", "product", "4", ev, name="3-methylocta-4,5-dienoic acid", smiles="CCC=C=CC(C)CC(=O)O"),
    ],
    lambda ev: [S("basic_hydrolysis", ["rac_3", "naoh", "water", "ethanol"], ev,
                         temperature=Q(80, "°C"), time=Q(10.5, "h"), operation="concentrate; add water; remove neutral impurities; acidify with 5% HCl to pH 1; ether extraction; silica chromatography")],
    outcomes=(("isolated_yield", Q(74, "%"), ["rac_4"]), ("product_mass", Q(0.8990, "g"), ["rac_4"]), ("diastereomeric_ratio", "3.3:1", ["rac_4"]), ("yield_measurement_basis", "isolated after silica chromatography", ["rac_4"])),
    notes=("The dr was reported as determined by inverse-gated decoupling 13C NMR analysis.",),
    unresolved=(),
))

# Scheme 3: three independently conditioned halolactonization rows.
for suffix, halogen, solvent_label, solvent_smiles, duration, product_label, yield_value in [
    ("scheme3_nbs_cyclohexane", "NBS", "cyclohexane", "C1CCCCC1", Q(17, "h"), "(±)-trans-Z-5", 24),
    ("scheme3_nbs_dcm_thf", "NBS", "CH2Cl2/THF 4:1", None, Q(11.5, "h"), "(±)-trans-Z-5", 42),
    ("scheme3_i2_cyclohexane", "I2", "cyclohexane", "C1CCCCC1", Q(1.5, "h"), "(±)-trans-Z-6", 83),
]:
    reagent_name = "N-bromosuccinimide" if halogen == "NBS" else "iodine"
    reagent_smiles = "O=C1CCC(=O)N1Br" if halogen == "NBS" else "II"
    product_smiles = "CCC=C(Br)C1OC(=O)CC1C" if halogen == "NBS" else "CCC=C(I)C1OC(=O)CC1C"
    records.append(record(
        suffix, (2, 4) if halogen == "I2" else (2,), "optimization_entry",
        lambda ev, h=halogen, rn=reagent_name, rs=reagent_smiles, sl=solvent_label, ss=solvent_smiles, pl=product_label, ps=product_smiles: [
            P("rac_4", "reactant", "racemic 4", ev, name="3-methylocta-4,5-dienoic acid", smiles="CCC=C=CC(C)CC(=O)O"),
            P("halogenating_agent", "reagent", h, ev, name=rn, smiles=rs),
            P("reaction_solvent", "solvent", sl, ev, smiles=ss),
            P("major_lactone", "product", pl, ev, smiles=ps),
            P("other_isomers", "product", "other isomers", ev),
        ],
        lambda ev, d=duration: [S("halolactonization", ["rac_4", "halogenating_agent", "reaction_solvent"], ev,
                                      temperature="r.t.", time=d, operation="halolactonization")],
        outcomes=(("isolated_yield", Q(yield_value, "%"), ["major_lactone"]),) + (("Z_E_ratio", "97:3", ["major_lactone"]),) if halogen == "I2" else (("isolated_yield", Q(yield_value, "%"), ["major_lactone"]),),
        notes=("Other stereoisomeric products are shown but not individually quantified.",),
        unresolved=("Exact quantities are not stated for the NBS screening row.",) if halogen == "NBS" else ("Detailed quantities and workup are supplied by the page-4 experimental batch.",),
    ))

# Replace the detailed iodine screening row with its explicit batch quantities.
iodine_row = records[-1]
iev = iodine_row["evidence_ids"]
iodine_row["participants"] = [
    P("rac_4", "reactant", "racemic 4", iev, name="3-methylocta-4,5-dienoic acid", smiles="CCC=C=CC(C)CC(=O)O", amounts=(("mass", Q(46.7, "mg")), ("amount", Q(0.3, "mmol")))),
    P("halogenating_agent", "reagent", "I2", iev, name="iodine", smiles="II", amounts=(("mass", Q(0.1137, "g")), ("amount", Q(0.45, "mmol")))),
    P("reaction_solvent", "solvent", "cyclohexane", iev, smiles="C1CCCCC1", amounts=(("volume", Q(4, "mL")),)),
    P("major_lactone", "product", "(±)-trans-Z-6", iev, smiles="CCC=C(I)C1OC(=O)CC1C"),
]
iodine_row["steps"] = [S("halolactonization", ["rac_4", "halogenating_agent", "reaction_solvent"], iev,
                           temperature="r.t.", time=Q(1.5, "h"), operation="TLC monitoring; water then saturated Na2S2O3 quench; ether extraction; brine wash; drying; silica chromatography")]
iodine_row["outcomes"].insert(1, field("product_mass", Q(0.0708, "g"), iev, ["major_lactone"]))

# Scheme 4: (−)-series and the direct trace experiment.
records.extend([
record(
    "scheme4_a_tms_propargyl_alcohol_8", (2,), "reported_experiment",
    lambda ev: [P("propargyl_alcohol_7", "reactant", "7", ev, name="propargyl alcohol", smiles="C#CCO"), P("etmgbr", "reagent", "EtMgBr", ev, name="ethylmagnesium bromide"), P("thf", "solvent", "THF", ev, smiles="C1CCOC1"), P("tmscl", "reagent", "TMSCl", ev, name="trimethylsilyl chloride", smiles="C[Si](C)(C)Cl"), P("tms_propargyl_alcohol_8", "product", "8", ev, name="3-(trimethylsilyl)prop-2-yn-1-ol", smiles="C[Si](C)(C)C#CCO")],
    lambda ev: [S("deprotonation", ["propargyl_alcohol_7", "etmgbr", "thf"], ev, operation="EtMgBr treatment in THF"), S("silylation", ["tmscl"], ev, operation="TMSCl addition")],
    outcomes=(("isolated_yield", Q(95, "%"), ["tms_propargyl_alcohol_8"]),),
    notes=("Preparation is cited to reference [17].",), unresolved=("Batch quantities, temperatures, times, and workup are not restated in the covered pages.",),
),
record(
    "scheme4_b_pcc_oxidation_to_9", (2,), "reported_experiment",
    lambda ev: [P("tms_propargyl_alcohol_8", "reactant", "8", ev, name="3-(trimethylsilyl)prop-2-yn-1-ol", smiles="C[Si](C)(C)C#CCO"), P("pcc", "reagent", "PCC", ev, name="pyridinium chlorochromate"), P("dcm", "solvent", "CH2Cl2", ev, name="dichloromethane", smiles="ClCCl"), P("tms_propynal_9", "product", "9", ev, name="3-(trimethylsilyl)propynal", smiles="C[Si](C)(C)C#CC=O")],
    lambda ev: [S("pcc_oxidation", ["tms_propargyl_alcohol_8", "pcc", "dcm"], ev, operation="PCC oxidation in CH2Cl2")],
    outcomes=(("isolated_yield", Q(54, "%"), ["tms_propynal_9"]),), notes=("Preparation is cited to reference [18].",), unresolved=("Batch quantities, temperature, duration, workup, and purification are not restated.",),
),
record(
    "scheme4_c_asymmetric_beta_lactone_10", (2, 4), "reported_experiment",
    lambda ev: [
        P("tms_propynal_9", "reactant", "9", ev, name="3-(trimethylsilyl)propynal", smiles="C[Si](C)(C)C#CC=O", amounts=(("mass", Q(0.9921, "g")), ("amount", Q(8, "mmol")))),
        P("propionyl_chloride", "reactant", "EtCOCl", ev, name="propionyl chloride", smiles="CCC(=O)Cl", amounts=(("mass", Q(1.4811, "g")), ("amount", Q(16, "mmol")))),
        P("tms_quinidine", "catalyst", "TMS-quinidine", ev, name="O-(trimethylsilyl)quinidine", amounts=(("mass", Q(0.3205, "g")), ("amount", Q(0.8, "mmol")))),
        P("mgcl2", "unspecified_agent", "MgCl2", ev, name="magnesium chloride", smiles="[Mg+2].[Cl-].[Cl-]", amounts=(("mass", Q(0.7536, "g")), ("amount", Q(8, "mmol")))),
        P("dipea", "reagent", "EtN(iPr)2", ev, name="N,N-diisopropylethylamine", smiles="CCN(C(C)C)C(C)C", amounts=(("mass", Q(2.5826, "g")), ("amount", Q(20, "mmol")))),
        P("ether", "solvent", "Et2O", ev, name="diethyl ether", smiles="CCOCC", amounts=(("volume", Q(12, "mL")),)),
        P("dcm", "solvent", "CH2Cl2", ev, name="dichloromethane", smiles="ClCCl", amounts=(("volume", Q(40, "mL")),)),
        P("beta_lactone_10_ss", "product", "(3S,4S)-(+)-10", ev, name="(3S,4S)-3-methyl-4-(trimethylsilyl)ethynyloxetan-2-one", smiles="O=C1OC(C#C[Si](C)(C)C)C1C"),
    ],
    lambda ev: [S("assemble_at_low_temperature", ["mgcl2", "dipea", "tms_quinidine", "ether", "dcm", "tms_propynal_9"], ev, temperature=Q(-80, "°C"), time=Q(20, "min"), atmosphere="N2"), S("syringe_pump_addition_and_reaction", ["propionyl_chloride"], ev, temperature=Q(-80, "°C"), time=Q(15, "h"), operation="propionyl chloride solution added at 2 mL/h; saturated NH4Cl quench; ether extraction; water/brine wash; drying; flash chromatography")],
    outcomes=(("isolated_yield", Q(94, "%"), ["beta_lactone_10_ss"]), ("product_mass", Q(1.3669, "g"), ["beta_lactone_10_ss"]), ("specific_rotation", "+10.7 (c 2.72, CHCl3, 20 °C)", ["beta_lactone_10_ss"])), unresolved=(),
),
record(
    "scheme4_direct_propynal_to_11_trace", (2,), "optimization_entry",
    lambda ev: [P("propynal", "reactant", "propynal", ev, name="prop-2-ynal", smiles="C#CC=O"), P("propionyl_chloride", "reactant", "EtCOCl", ev, name="propionyl chloride", smiles="CCC(=O)Cl"), P("tms_quinidine", "catalyst", "TMS-quinidine", ev), P("mgcl2", "unspecified_agent", "MgCl2", ev, smiles="[Mg+2].[Cl-].[Cl-]"), P("dipea", "reagent", "EtN(iPr)2", ev, name="N,N-diisopropylethylamine", smiles="CCN(C(C)C)C(C)C"), P("ether_dcm", "solvent", "Et2O/CH2Cl2", ev), P("beta_lactone_11_ss", "product", "(3S,4S)-(−)-11", ev, name="(3S,4S)-3-methyl-4-ethynyloxetan-2-one", smiles="O=C1OC(C#C)C1C")],
    lambda ev: [S("direct_asymmetric_cyclocondensation", ["propynal", "propionyl_chloride", "tms_quinidine", "mgcl2", "dipea", "ether_dcm"], ev, temperature=Q(-80, "°C"), operation="conditions c of Scheme 4")],
    outcomes=(("product_yield", "trace", ["beta_lactone_11_ss"]),), unresolved=("No exact quantities, duration, workup, or numeric yield are given for this failed direct experiment.",),
),
record(
    "scheme4_d_desilylation_to_11", (2, 4), "reported_experiment",
    lambda ev: [P("beta_lactone_10_ss", "reactant", "(3S,4S)-(+)-10", ev, smiles="O=C1OC(C#C[Si](C)(C)C)C1C", amounts=(("mass", Q(0.7184, "g")), ("amount", Q(4, "mmol")))), P("tbaf", "reagent", "TBAF", ev, name="tetrabutylammonium fluoride", amounts=(("volume", Q(4, "mL")), ("concentration", Q(1, "M")), ("amount", Q(4, "mmol")))), P("thf", "solvent", "THF", ev, smiles="C1CCOC1", amounts=(("volume", Q(4, "mL")),)), P("beta_lactone_11_ss", "product", "(3S,4S)-(−)-11", ev, name="(3S,4S)-3-methyl-4-ethynyloxetan-2-one", smiles="O=C1OC(C#C)C1C")],
    lambda ev: [S("tbaf_desilylation", ["beta_lactone_10_ss", "tbaf", "thf"], ev, temperature=Q(-15, "°C"), time=Q(15, "min"), operation="dropwise TBAF addition; short silica filtration with CH2Cl2; concentration; flash chromatography")],
    outcomes=(("isolated_yield", Q(64, "%"), ["beta_lactone_11_ss"]), ("product_mass", Q(0.2798, "g"), ["beta_lactone_11_ss"])), unresolved=(),
),
record(
    "scheme4_e_ring_opening_to_12", (2, 4), "reported_experiment",
    lambda ev: [P("beta_lactone_11_ss", "reactant", "(3S,4S)-(−)-11", ev, smiles="O=C1OC(C#C)C1C", amounts=(("mass", Q(120.5, "mg")), ("amount", Q(11.3, "mmol", raw_text="11.3 mmol as printed")))), P("etmgbr", "reagent", "EtMgBr", ev, name="ethylmagnesium bromide", amounts=(("volume", Q(3.3, "mL")), ("concentration", Q(1, "M")), ("amount", Q(3.3, "mmol")))), P("cubr_sme2", "catalyst", "CuBr·SMe2", ev, name="copper(I) bromide dimethyl sulfide complex", amounts=(("mass", Q(22.8, "mg")), ("amount", Q(0.11, "mmol")))), P("dimethyl_sulfide", "unspecified_agent", "Me2S", ev, name="dimethyl sulfide", smiles="CSC", amounts=(("volume", Q(0.5, "mL")),)), P("thf", "solvent", "THF", ev, smiles="C1CCOC1", amounts=(("volume", Q(10, "mL")),)), P("allenoic_acid_12_rs", "product", "(Ra,S)-(−)-12", ev, name="(Ra,S)-2-methylhepta-3,4-dienoic acid", smiles="CCC=C=CC(C)C(=O)O")],
    lambda ev: [S("cu_catalyzed_ring_opening", ["beta_lactone_11_ss", "etmgbr", "cubr_sme2", "dimethyl_sulfide", "thf"], ev, temperature=Q(-78, "°C"), time=Q(25, "min"), atmosphere="N2", operation="EtMgBr added over 10 min, then 25 min; NH4Cl quench; acidify to pH 1; ether extraction; wash; dry; flash chromatography")],
    outcomes=(("isolated_yield", Q(74, "%"), ["allenoic_acid_12_rs"]), ("product_mass", Q(113.5, "mg"), ["allenoic_acid_12_rs"])),
    unresolved=("The printed 120.5 mg / 11.3 mmol substrate pair is internally inconsistent for compound 11; it is preserved verbatim and not corrected.",),
),
record(
    "scheme4_f_reduction_to_2_minus", (2, 4), "reported_experiment",
    lambda ev: [P("allenoic_acid_12_rs", "reactant", "(Ra,S)-(−)-12", ev, smiles="CCC=C=CC(C)C(=O)O", amounts=(("mass", Q(0.7273, "g")), ("amount", Q(5.2, "mmol")))), P("lialh4", "reagent", "LiAlH4", ev, smiles="[Li+].[AlH4-]", amounts=(("mass", Q(0.2478, "g")), ("amount", Q(6.5, "mmol")))), P("ether", "solvent", "Et2O", ev, smiles="CCOCC", amounts=(("volume", Q(40, "mL")),)), P("allene_alcohol_2_minus", "product", "(Ra,S)-(−)-2", ev, name="(Ra,S)-2-methylhepta-3,4-dien-1-ol", smiles="CCC=C=CC(C)CO")],
    lambda ev: [S("lialh4_reduction", ["allenoic_acid_12_rs", "lialh4", "ether"], ev, temperature={"minimum": 0, "maximum": 4, "unit": "°C", "raw_text": "0–4 °C"}, time=Q(50, "min"), atmosphere="N2", operation="dropwise addition; TLC; ether dilution; NaOH quench; filtration; silica chromatography")],
    outcomes=(("isolated_yield", Q(77, "%"), ["allene_alcohol_2_minus"]), ("product_mass", Q(0.5024, "g"), ["allene_alcohol_2_minus"])), unresolved=(),
),
record(
    "scheme4_g_tosylation_cyanide_to_3_minus", (2, 4, 5), "reported_experiment",
    lambda ev: [P("allene_alcohol_2_minus", "reactant", "(Ra,S)-(−)-2", ev, smiles="CCC=C=CC(C)CO", amounts=(("mass", Q(0.4209, "g")), ("amount", Q(3.3, "mmol")))), P("ptscl", "reagent", "pTsCl", ev, smiles="Cc1ccc(S(=O)(=O)Cl)cc1", amounts=(("mass", Q(1.9081, "g")), ("amount", Q(10.0, "mmol")))), P("pyridine", "solvent", "pyridine", ev, smiles="n1ccccc1", amounts=(("volume", Q(10, "mL")),)), P("nacn", "reagent", "NaCN", ev, smiles="[Na+].[C-]#N", amounts=(("mass", Q(0.1747, "g")), ("amount", Q(3.6, "mmol")))), P("dmso", "solvent", "DMSO", ev, smiles="CS(C)=O", amounts=(("volume", Q(5, "mL")),)), P("allene_nitrile_3_minus", "product", "(Ra,R)-(−)-3", ev, name="(Ra,R)-3-methylocta-4,5-dienenitrile", smiles="CCC=C=CC(C)CC#N")],
    lambda ev: [S("tosylation", ["allene_alcohol_2_minus", "ptscl", "pyridine"], ev, temperature={"minimum": 0, "maximum": 5, "unit": "°C", "raw_text": "0–5 °C"}, operation="following the racemic tosylation procedure; intermediate used without purification"), S("cyanide_displacement", ["nacn", "dmso"], ev, temperature=Q(30, "°C"), operation="following the racemic NaCN displacement procedure")],
    outcomes=(("combined_isolated_yield", Q(77, "%"), ["allene_nitrile_3_minus"]), ("product_mass", Q(0.3470, "g"), ["allene_nitrile_3_minus"]), ("yield_measurement_basis", "combined yield for tosylation and cyanide displacement", ["allene_nitrile_3_minus"])), unresolved=("The abbreviated procedure does not restate stage durations or workup volumes.",),
),
record(
    "scheme4_h_hydrolysis_to_4_minus", (2, 5), "reported_experiment",
    lambda ev: [P("allene_nitrile_3_minus", "reactant", "(Ra,R)-(−)-3", ev, smiles="CCC=C=CC(C)CC#N", amounts=(("mass", Q(0.2883, "g")), ("amount", Q(2.1, "mmol")))), P("naoh", "reagent", "NaOH", ev, smiles="[Na+].[OH-]", amounts=(("mass", Q(1.4630, "g")), ("amount", Q(36, "mmol")))), P("water", "solvent", "H2O", ev, smiles="O", amounts=(("volume", Q(1.8, "mL")),)), P("ethanol", "solvent", "EtOH", ev, smiles="CCO", amounts=(("volume", Q(5, "mL")),)), P("allenoic_acid_4_minus", "product", "(Ra,R)-(−)-4", ev, name="(Ra,R)-3-methylocta-4,5-dienoic acid", smiles="CCC=C=CC(C)CC(=O)O")],
    lambda ev: [S("nitrile_hydrolysis", ["allene_nitrile_3_minus", "naoh", "water", "ethanol"], ev, temperature=Q(80, "°C"), operation="following the racemic hydrolysis procedure, including acidification")],
    outcomes=(("isolated_yield", Q(97, "%"), ["allenoic_acid_4_minus"]), ("product_mass", Q(0.3182, "g"), ["allenoic_acid_4_minus"]), ("diastereomeric_ratio", "(Ra,R)-4/(Sa,R)-4 = 12.5:1", ["allenoic_acid_4_minus"])), notes=("The dr was reported as determined by inverse-gated decoupling 13C NMR analysis.",), unresolved=("The abbreviated batch does not restate the reaction duration.",),
),
record(
    "scheme4_i_iodolactonization_to_6_minus", (2, 5), "reported_experiment",
    lambda ev: [P("allenoic_acid_4_minus", "reactant", "(Ra,R)-(−)-4", ev, smiles="CCC=C=CC(C)CC(=O)O", amounts=(("mass", Q(77.3, "mg")), ("amount", Q(0.5, "mmol")))), P("iodine", "reagent", "I2", ev, smiles="II", amounts=(("mass", Q(191.6, "mg")), ("amount", Q(0.75, "mmol")))), P("cyclohexane", "solvent", "cyclohexane", ev, smiles="C1CCCCC1", amounts=(("volume", Q(7.5, "mL")),)), P("iodolactone_6_minus", "product", "(4R,5R)-(−)-Z-6", ev, name="(4R,5R)-5-[(1Z)-1-iodo-1-butenyl]-4-methyl-4,5-dihydro-2(3H)-furanone", smiles="CCC=C(I)C1OC(=O)CC1C")],
    lambda ev: [S("iodolactonization", ["allenoic_acid_4_minus", "iodine", "cyclohexane"], ev, temperature="r.t.", operation="following the racemic trans-Z-6 preparation")],
    outcomes=(("isolated_yield", Q(84, "%"), ["iodolactone_6_minus"]), ("product_mass", Q(0.1179, "g"), ["iodolactone_6_minus"]), ("Z_E_ratio", "97:3", ["iodolactone_6_minus"]), ("ee", Q(98.6, "%"), ["iodolactone_6_minus"])), unresolved=("The abbreviated batch does not restate reaction duration or workup details.",),
),
])

# Four unsuccessful deiodination conditions described separately in prose.
for suffix, agents in [
    ("failed_deiodination_pdc_h2", (("pd_c", "catalyst", "Pd/C"), ("hydrogen", "reagent", "H2"))),
    ("failed_deiodination_t_buli", (("tbuli", "reagent", "tBuLi"),)),
    ("failed_deiodination_ttmss", (("ttmss", "reagent", "TTMSS"),)),
    ("failed_deiodination_pdpph3_ammonium_formate", (("pdpph3", "catalyst", "Pd(PPh3)4"), ("ammonium_formate", "reagent", "HCO2NH4"))),
]:
    records.append(record(
        suffix, (2,), "optimization_entry",
        lambda ev, aa=agents: [P("rac_iodolactone_6", "reactant", "(±)-trans-Z-6", ev, smiles="CCC=C(I)C1OC(=O)CC1C")] + [P(eid, role, label, ev) for eid, role, label in aa] + [P("desired_butenyl_lactone", "product", "trans-4-methyl-5-(1-butenyl)-gamma-butyrolactone", ev, smiles="CCC=CC1OC(=O)CC1C")],
        lambda ev, aa=agents: [S("attempted_deiodination", ["rac_iodolactone_6"] + [eid for eid, _, _ in aa], ev, operation="attempted deiodination")],
        outcomes=(("desired_product_yield", "not obtained in an acceptable yield", ["desired_butenyl_lactone"]),),
        unresolved=("No exact quantities, solvent, temperature, duration, workup, product distribution, or numeric yield are given; the paper refers to SI Table S1, but SI was not provided or associated.",),
    ))

# Scheme 5: final two stages of the (−)-series.
records.extend([
record(
    "scheme5_a_dehydroiodination_to_13_minus", (2, 3, 5), "reported_experiment",
    lambda ev: [P("iodolactone_6_minus", "reactant", "(4R,5R)-(−)-Z-6", ev, smiles="CCC=C(I)C1OC(=O)CC1C", amounts=(("mass", Q(0.1018, "g")), ("amount", Q(0.36, "mmol")))), P("tbaf", "reagent", "TBAF", ev, name="tetrabutylammonium fluoride", amounts=(("volume", Q(1.1, "mL")), ("concentration", Q(1, "M")), ("amount", Q(1.1, "mmol")), ("equivalents", Q(3, "equiv")))), P("dmf", "solvent", "DMF", ev, name="N,N-dimethylformamide", smiles="CN(C)C=O", amounts=(("volume", Q(4, "mL")),)), P("alkynyl_lactone_13_minus", "product", "(4R,5R)-(−)-13", ev, name="(4R,5R)-5-(but-1-ynyl)-4-methyl-4,5-dihydro-2(3H)-furanone", smiles="CCC#CC1OC(=O)CC1C")],
    lambda ev: [S("dehydroiodination", ["iodolactone_6_minus", "tbaf", "dmf"], ev, temperature=Q(25, "°C"), time=Q(5, "h"), operation="TLC monitoring; water quench; acidify with 5% HCl to pH 1; ether extraction; wash; dry; silica chromatography")],
    outcomes=(("isolated_yield", Q(92, "%"), ["alkynyl_lactone_13_minus"]), ("product_mass", Q(0.0509, "g"), ["alkynyl_lactone_13_minus"]), ("ee", Q(98.8, "%"), ["alkynyl_lactone_13_minus"])), unresolved=(),
),
record(
    "scheme5_b_hydrogenation_to_whisky_lactone_minus", (2, 3, 5), "reported_experiment",
    lambda ev: [P("alkynyl_lactone_13_minus", "reactant", "(4R,5R)-(−)-13", ev, smiles="CCC#CC1OC(=O)CC1C", amounts=(("mass", Q(46.1, "mg")), ("amount", Q(0.30, "mmol")))), P("hydrogen", "reagent", "H2", ev, name="hydrogen", smiles="[H][H]"), P("pd_c", "catalyst", "Pd/C", ev, name="palladium on carbon", amounts=(("mass", Q(33.1, "mg")), ("amount", Q(0.03, "mmol")), ("catalyst_loading", Q(10, "mol%")))), P("ethyl_acetate", "solvent", "ethyl acetate", ev, smiles="CCOC(C)=O", amounts=(("volume", Q(6, "mL")),)), P("whisky_lactone_minus", "product", "(−)-trans-whisky lactone (14)", ev, smiles="CCCCC1OC(=O)CC1C")],
    lambda ev: [S("high_pressure_hydrogenation", ["alkynyl_lactone_13_minus", "hydrogen", "pd_c", "ethyl_acetate"], ev, temperature="r.t.", time=Q(1, "d"), operation="H2 at 25 atm in an autoclave; silica filtration with ether; concentration; silica chromatography")],
    outcomes=(("isolated_yield", Q(86, "%"), ["whisky_lactone_minus"]), ("product_mass", Q(0.0405, "g"), ["whisky_lactone_minus"]), ("ee", Q(98.5, "%"), ["whisky_lactone_minus"]), ("specific_rotation", "−82.5 (c 1.02, MeOH, 20 °C)", ["whisky_lactone_minus"])), unresolved=(),
),
])

# Scheme 6: natural (+)-enantiomer route, separating the b/c chemical stages.
records.extend([
record(
    "scheme6_a_asymmetric_beta_lactone_10_rr", (3, 5), "reported_experiment",
    lambda ev: [P("tms_propynal_9", "reactant", "9", ev, smiles="C[Si](C)(C)C#CC=O", amounts=(("mass", Q(2.5013, "g")), ("amount", Q(20, "mmol")))), P("propionyl_chloride", "reactant", "EtCOCl", ev, smiles="CCC(=O)Cl", amounts=(("mass", Q(3.7112, "g")), ("amount", Q(40, "mmol")))), P("tms_quinine", "catalyst", "TMS-quinine", ev, name="O-trimethylsilylquinine", amounts=(("mass", Q(0.8006, "g")), ("amount", Q(2.0, "mmol")))), P("mgcl2", "unspecified_agent", "MgCl2", ev, smiles="[Mg+2].[Cl-].[Cl-]", amounts=(("mass", Q(1.9010, "g")), ("amount", Q(20, "mmol")))), P("dipea", "reagent", "EtN(iPr)2", ev, smiles="CCN(C(C)C)C(C)C", amounts=(("mass", Q(6.4613, "g")), ("amount", Q(50, "mmol")))), P("ether", "solvent", "Et2O", ev, smiles="CCOCC", amounts=(("volume", Q(30, "mL")),)), P("dcm", "solvent", "CH2Cl2", ev, smiles="ClCCl", amounts=(("volume", Q(80, "mL")),)), P("beta_lactone_10_rr", "product", "(3R,4R)-(−)-10", ev, name="(3R,4R)-3-methyl-4-(trimethylsilyl)ethynyloxetan-2-one", smiles="O=C1OC(C#C[Si](C)(C)C)C1C")],
    lambda ev: [S("asymmetric_cyclocondensation", ["tms_propynal_9", "propionyl_chloride", "tms_quinine", "mgcl2", "dipea", "ether", "dcm"], ev, temperature=Q(-80, "°C"), operation="following the procedure for (3S,4S)-10")],
    outcomes=(("isolated_yield", Q(88, "%"), ["beta_lactone_10_rr"]), ("product_mass", Q(3.2181, "g"), ["beta_lactone_10_rr"])), unresolved=("The abbreviated batch does not restate the duration or workup.",),
),
record(
    "scheme6_b_desilylation_to_11_rr", (3, 5), "reported_experiment",
    lambda ev: [P("beta_lactone_10_rr", "reactant", "(3R,4R)-(−)-10", ev, smiles="O=C1OC(C#C[Si](C)(C)C)C1C", amounts=(("mass", Q(2.7344, "g")), ("amount", Q(15, "mmol")))), P("tbaf", "reagent", "TBAF", ev, amounts=(("volume", Q(15, "mL")), ("concentration", Q(1, "M")), ("amount", Q(15, "mmol")))), P("thf", "solvent", "THF", ev, smiles="C1CCOC1", amounts=(("volume", Q(15, "mL")),)), P("beta_lactone_11_rr", "product", "(3R,4R)-(+)-11", ev, name="(3R,4R)-3-methyl-4-ethynyloxetan-2-one", smiles="O=C1OC(C#C)C1C")],
    lambda ev: [S("tbaf_desilylation", ["beta_lactone_10_rr", "tbaf", "thf"], ev, temperature=Q(-15, "°C"), operation="following the (3S,4S)-11 procedure; product carried forward without purification")],
    notes=("No stage-specific yield is reported; the combined yield through Scheme 6 step c is 57%.",), unresolved=("The abbreviated stage does not restate duration or workup.",),
),
record(
    "scheme6_c_ring_opening_to_12_plus", (3, 5), "reported_experiment",
    lambda ev: [P("beta_lactone_11_rr", "reactant", "(3R,4R)-(+)-11", ev, smiles="O=C1OC(C#C)C1C"), P("etmgbr", "reagent", "EtMgBr", ev, amounts=(("volume", Q(34, "mL")), ("concentration", Q(1, "M")), ("amount", Q(34, "mmol")))), P("cubr_sme2", "catalyst", "CuBr·SMe2", ev, amounts=(("mass", Q(234.1, "mg")), ("amount", Q(1.13, "mmol")))), P("dimethyl_sulfide", "unspecified_agent", "Me2S", ev, smiles="CSC", amounts=(("volume", Q(7.5, "mL")),)), P("thf", "solvent", "THF", ev, smiles="C1CCOC1", amounts=(("volume", Q(128, "mL")),)), P("allenoic_acid_12_plus", "product", "(Sa,R)-(+)-12", ev, name="(Sa,R)-2-methylhepta-3,4-dienoic acid", smiles="CCC=C=CC(C)C(=O)O")],
    lambda ev: [S("cu_catalyzed_ring_opening", ["beta_lactone_11_rr", "etmgbr", "cubr_sme2", "dimethyl_sulfide", "thf"], ev, temperature=Q(-78, "°C"), time=Q(2.2, "h"), operation="following the (Ra,S)-12 preparation")],
    outcomes=(("combined_isolated_yield", Q(57, "%"), ["allenoic_acid_12_plus"]), ("product_mass", Q(1.1887, "g"), ["allenoic_acid_12_plus"]), ("yield_measurement_basis", "combined yield for Scheme 6 steps b and c", ["allenoic_acid_12_plus"])), unresolved=("The amount of carried-forward (3R,4R)-11 is not independently reported.",),
),
record(
    "scheme6_d_reduction_to_2_plus", (3, 5, 6), "reported_experiment",
    lambda ev: [P("allenoic_acid_12_plus", "reactant", "(Sa,R)-(+)-12", ev, smiles="CCC=C=CC(C)C(=O)O", amounts=(("mass", Q(1.6390, "g")), ("amount", Q(11.7, "mmol")))), P("lialh4", "reagent", "LiAlH4", ev, smiles="[Li+].[AlH4-]", amounts=(("mass", Q(0.5382, "g")), ("amount", Q(14.2, "mmol")))), P("ether", "solvent", "Et2O", ev, smiles="CCOCC", amounts=(("volume", Q(70, "mL")),)), P("allene_alcohol_2_plus", "product", "(Sa,R)-(+)-2", ev, name="(Sa,R)-2-methylhepta-3,4-dien-1-ol", smiles="CCC=C=CC(C)CO")],
    lambda ev: [S("lialh4_reduction", ["allenoic_acid_12_plus", "lialh4", "ether"], ev, temperature={"minimum": 0, "maximum": 4, "unit": "°C", "raw_text": "0–4 °C"}, atmosphere="N2", operation="following the racemic alcohol 2 procedure")],
    outcomes=(("isolated_yield", Q(74, "%"), ["allene_alcohol_2_plus"]), ("product_mass", Q(1.0931, "g"), ["allene_alcohol_2_plus"])), unresolved=("The abbreviated procedure does not restate the reaction duration.",),
),
record(
    "scheme6_e_tosylation_cyanide_to_3_plus", (3, 6), "reported_experiment",
    lambda ev: [P("allene_alcohol_2_plus", "reactant", "(Sa,R)-(+)-2", ev, smiles="CCC=C=CC(C)CO", amounts=(("mass", Q(0.8450, "g")), ("amount", Q(6.7, "mmol")))), P("ptscl", "reagent", "pTsCl", ev, smiles="Cc1ccc(S(=O)(=O)Cl)cc1", amounts=(("mass", Q(3.9297, "g")), ("amount", Q(20.6, "mmol")))), P("pyridine", "solvent", "pyridine", ev, smiles="n1ccccc1", amounts=(("volume", Q(10, "mL")),)), P("nacn", "reagent", "NaCN", ev, smiles="[Na+].[C-]#N", amounts=(("mass", Q(0.3528, "g")), ("amount", Q(7.2, "mmol")))), P("dmso", "solvent", "DMSO", ev, smiles="CS(C)=O", amounts=(("volume", Q(10, "mL")),)), P("allene_nitrile_3_plus", "product", "(Sa,S)-(+)-3", ev, name="(Sa,S)-3-methylocta-4,5-dienenitrile", smiles="CCC=C=CC(C)CC#N")],
    lambda ev: [S("tosylation", ["allene_alcohol_2_plus", "ptscl", "pyridine"], ev, temperature=Q(0, "°C"), operation="following racemic tosylation; intermediate used without purification"), S("cyanide_displacement", ["nacn", "dmso"], ev, temperature=Q(30, "°C"), operation="following racemic NaCN displacement")],
    outcomes=(("combined_isolated_yield", Q(73, "%"), ["allene_nitrile_3_plus"]), ("product_mass", Q(0.6637, "g"), ["allene_nitrile_3_plus"]), ("yield_measurement_basis", "combined yield for tosylation and cyanide displacement", ["allene_nitrile_3_plus"])), unresolved=("Stage durations and workup details are not restated in the abbreviated batch.",),
),
record(
    "scheme6_f_hydrolysis_to_4_plus", (3, 6), "reported_experiment",
    lambda ev: [P("allene_nitrile_3_plus", "reactant", "(Sa,S)-(+)-3", ev, smiles="CCC=C=CC(C)CC#N", amounts=(("mass", Q(0.6011, "g")), ("amount", Q(4.5, "mmol")))), P("naoh", "reagent", "NaOH", ev, smiles="[Na+].[OH-]", amounts=(("mass", Q(3.0831, "g")), ("amount", Q(77, "mmol")))), P("water", "solvent", "H2O", ev, smiles="O", amounts=(("volume", Q(4, "mL")),)), P("ethanol", "solvent", "EtOH", ev, smiles="CCO", amounts=(("volume", Q(11, "mL")),)), P("hcl", "reagent", "aq. HCl", ev, name="hydrochloric acid"), P("allenoic_acid_4_plus", "product", "(Sa,S)-(+)-4", ev, name="(Sa,S)-3-methylocta-4,5-dienoic acid", smiles="CCC=C=CC(C)CC(=O)O")],
    lambda ev: [S("basic_hydrolysis", ["allene_nitrile_3_plus", "naoh", "water", "ethanol"], ev, temperature=Q(80, "°C"), operation="following racemic hydrolysis"), S("acidification", ["hcl"], ev, operation="aqueous HCl acidification")],
    outcomes=(("isolated_yield", Q(92, "%"), ["allenoic_acid_4_plus"]), ("product_mass", Q(0.6282, "g"), ["allenoic_acid_4_plus"]), ("diastereomeric_ratio", "(Sa,S)-4/(Ra,S)-4 = 12.5:1", ["allenoic_acid_4_plus"])), unresolved=("Reaction duration and detailed workup are not restated in the abbreviated batch.",),
),
record(
    "scheme6_g_iodolactonization_to_6_plus", (3, 6), "reported_experiment",
    lambda ev: [P("allenoic_acid_4_plus", "reactant", "(Sa,S)-(+)-4", ev, smiles="CCC=C=CC(C)CC(=O)O", amounts=(("mass", Q(243.4, "mg")), ("amount", Q(1.6, "mmol")))), P("iodine", "reagent", "I2", ev, smiles="II", amounts=(("mass", Q(0.6061, "g")), ("amount", Q(2.4, "mmol")))), P("cyclohexane", "solvent", "cyclohexane", ev, smiles="C1CCCCC1", amounts=(("volume", Q(24, "mL")),)), P("iodolactone_6_plus", "product", "(4S,5S)-(+)-Z-6", ev, name="(4S,5S)-5-[(1Z)-1-iodo-1-butenyl]-4-methyl-4,5-dihydro-2(3H)-furanone", smiles="CCC=C(I)C1OC(=O)CC1C")],
    lambda ev: [S("iodolactonization", ["allenoic_acid_4_plus", "iodine", "cyclohexane"], ev, temperature="r.t.", time=Q(2, "h"), operation="following trans-Z-6 preparation")],
    outcomes=(("isolated_yield", Q(86, "%"), ["iodolactone_6_plus"]), ("product_mass", Q(0.3810, "g"), ["iodolactone_6_plus"]), ("Z_E_ratio", "98:2", ["iodolactone_6_plus"]), ("ee", Q(99.3, "%"), ["iodolactone_6_plus"])), unresolved=(),
),
record(
    "scheme6_h_dehydroiodination_to_13_plus", (3, 6), "reported_experiment",
    lambda ev: [P("iodolactone_6_plus", "reactant", "(4S,5S)-(+)-Z-6", ev, smiles="CCC=C(I)C1OC(=O)CC1C", amounts=(("mass", Q(0.2768, "g")), ("amount", Q(0.99, "mmol")))), P("tbaf", "reagent", "TBAF", ev, amounts=(("volume", Q(3, "mL")), ("concentration", Q(1, "M")), ("amount", Q(3, "mmol")))), P("dmf", "solvent", "DMF", ev, smiles="CN(C)C=O", amounts=(("volume", Q(11, "mL")),)), P("alkynyl_lactone_13_plus", "product", "(4S,5S)-(+)-13", ev, name="(4S,5S)-5-(but-1-ynyl)-4-methyl-4,5-dihydro-2(3H)-furanone", smiles="CCC#CC1OC(=O)CC1C")],
    lambda ev: [S("dehydroiodination", ["iodolactone_6_plus", "tbaf", "dmf"], ev, temperature=Q(25, "°C"), time=Q(5, "h"), operation="following (4R,5R)-13 preparation")],
    outcomes=(("isolated_yield", Q(89, "%"), ["alkynyl_lactone_13_plus"]), ("product_mass", Q(0.1361, "g"), ["alkynyl_lactone_13_plus"]), ("ee", Q(98.9, "%"), ["alkynyl_lactone_13_plus"])), unresolved=("The abbreviated batch does not restate workup and purification details.",),
),
record(
    "scheme6_i_hydrogenation_to_whisky_lactone_plus", (3, 6), "reported_experiment",
    lambda ev: [P("alkynyl_lactone_13_plus", "reactant", "(4S,5S)-(+)-13", ev, smiles="CCC#CC1OC(=O)CC1C", amounts=(("mass", Q(117.9, "mg")), ("amount", Q(0.78, "mmol")))), P("hydrogen", "reagent", "H2", ev, smiles="[H][H]"), P("pd_c", "catalyst", "Pd/C", ev, amounts=(("mass", Q(84.1, "mg")), ("amount", Q(0.078, "mmol")), ("catalyst_loading", Q(10, "mol%")))), P("ethyl_acetate", "solvent", "ethyl acetate", ev, smiles="CCOC(C)=O", amounts=(("volume", Q(16, "mL")),)), P("whisky_lactone_plus", "product", "(+)-trans-whisky lactone (14)", ev, smiles="CCCCC1OC(=O)CC1C")],
    lambda ev: [S("high_pressure_hydrogenation", ["alkynyl_lactone_13_plus", "hydrogen", "pd_c", "ethyl_acetate"], ev, temperature="r.t.", time=Q(1, "d"), operation="H2 at 25 atm; following the (−)-trans-whisky lactone procedure")],
    outcomes=(("isolated_yield", Q(90, "%"), ["whisky_lactone_plus"]), ("product_mass", Q(0.1090, "g"), ["whisky_lactone_plus"]), ("ee", Q(98.5, "%"), ["whisky_lactone_plus"]), ("specific_rotation", "+81.2 (c 1.24, MeOH, 20 °C)", ["whisky_lactone_plus"])), unresolved=("The abbreviated batch inherits workup and purification by reference rather than restating them.",),
),
])

OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
print(f"wrote {len(records)} records to {OUT}")
