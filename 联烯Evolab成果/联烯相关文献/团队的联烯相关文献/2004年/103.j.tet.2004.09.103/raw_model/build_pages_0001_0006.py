#!/usr/bin/env python3
"""Build source-derived machine records and the page 1-6 coverage ledger."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
DOC = "doc_a746be3717c6f516"
OUT = ROOT / "runs/current/raw_model/extracted_records_pages_0001_0006.json"
COVERAGE = ROOT / "runs/current/coverage/pages_0001_0006.json"
TASKS = ROOT / "runs/current/tasks.json"


def ev(page, kind="image"):
    return f"{DOC}:page{page}:{kind}"


def fact(value, evidence):
    return {
        "value": value,
        "evidence_ids": list(evidence) if value is not None else list(evidence),
        "verification": "unreviewed" if value is not None else "missing",
    }


def field(name, value, evidence, targets=None):
    item = {"name": name, "fact": fact(value, evidence)}
    if targets:
        item["target_entity_ids"] = list(targets)
    return item


def qty(number, unit, raw_text=None, **extra):
    value = {"number": number, "unit": unit}
    if raw_text is not None:
        value["raw_text"] = raw_text
    value.update(extra)
    return value


def qrange(minimum, maximum, unit, raw_text):
    return {
        "minimum": minimum,
        "maximum": maximum,
        "unit": unit,
        "raw_text": raw_text,
    }


def participant(entity_id, role, label, name, evidence, smiles=None, amounts=()):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence),
        "smiles": fact(smiles, evidence if smiles is not None else ()),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": list(amounts),
    }


def record(suffix, source_id, kind, evidence, participants, steps, outcomes=(), notes=(), unresolved=()):
    return {
        "record_id": f"{DOC}:{suffix}",
        "document_id": DOC,
        "source_reaction_id": source_id,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": list(dict.fromkeys(evidence)),
        "participants": list(participants),
        "steps": list(steps),
        "outcomes": list(outcomes),
        "notes": [fact(value, note_ev) for value, note_ev in notes],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": list(unresolved),
        },
    }


def step(step_id, participant_ids, conditions=()):
    return {
        "step_id": step_id,
        "participant_ids": list(participant_ids),
        "conditions": list(conditions),
    }


records = []
p2 = [ev(2), ev(2, "text")]
p3 = [ev(3), ev(3, "text")]
p4 = [ev(4), ev(4, "text")]
p5 = [ev(5), ev(5, "text")]
p6 = [ev(6), ev(6, "text")]

# Scheme 1: four arrows are retained as general-scheme records because the text
# explicitly attributes the route to Ref. 17 rather than reporting these ranges
# as one newly executed experiment.
scheme1_common = (
    "Generic R-group structures are fully specified only as a family; SMILES is intentionally null.",
    "Reaction time, scale, atmosphere, workup, purification, and SI details are not stated in Scheme 1.",
)
records.append(record(
    "scheme1_arrow01_orthoester_rearrangement", "Scheme 1 arrow 1", "general_scheme", p2,
    [
        participant("s1_a1_start", "reactant", "generic propargylic alcohol", "R1-substituted propargylic alcohol bearing R3/R4", p2),
        participant("s1_a1_orthoacetate", "reagent", "CH3C(OEt)3", "triethyl orthoacetate", p2, "CCOC(C)(OCC)OCC"),
        participant("s1_a1_propionic_acid", "reagent", "CH3CH2COOH", "propionic acid", p2, "CCC(=O)O"),
        participant("s1_a1_product", "product", "generic allenoate", "generic ethyl allenoate intermediate", p2),
    ],
    [step("arrow_1", ["s1_a1_start", "s1_a1_orthoacetate", "s1_a1_propionic_acid", "s1_a1_product"], [
        field("temperature", qrange(140, 150, "°C", "140–150 °C"), p2),
    ])],
    notes=[("Known procedure cited as Ref. 17; this arrow is a general scheme, not a newly detailed experiment.", p2)],
    unresolved=scheme1_common,
))
records.append(record(
    "scheme1_arrow02_lialh4_reduction", "Scheme 1 arrow 2", "general_scheme", p2,
    [
        participant("s1_a2_start", "reactant", "generic allenoate", "generic ethyl allenoate intermediate", p2),
        participant("s1_a2_lialh4", "reagent", "LiAlH4", "lithium aluminium hydride", p2, "[Li+].[AlH4-]"),
        participant("s1_a2_thf", "solvent", "THF", "tetrahydrofuran", p2, "C1CCOC1"),
        participant("s1_a2_product", "product", "generic primary allenol", "generic substituted penta-3,4-dien-1-ol", p2),
    ],
    [step("arrow_2", ["s1_a2_start", "s1_a2_lialh4", "s1_a2_thf", "s1_a2_product"], [
        field("temperature", qrange(0, 25, "°C", "0–25 °C"), p2),
    ])],
    [
        field("two_step_yield", qrange(45, 95, "%", "45–95%"), p2, ["s1_a2_product"]),
        field("yield_measurement_basis", "total yield of Scheme 1 arrows 1 and 2", p2, ["s1_a2_product"]),
    ],
    notes=[("Known procedure cited as Ref. 17; the displayed yield spans two arrows.", p2)],
    unresolved=scheme1_common,
))
records.append(record(
    "scheme1_arrow03_dmp_oxidation", "Scheme 1 arrow 3", "general_scheme", p2,
    [
        participant("s1_a3_start", "reactant", "generic primary allenol", "generic substituted penta-3,4-dien-1-ol", p2),
        participant("s1_a3_dmp", "reagent", "DMP", "Dess–Martin periodinane", p2),
        participant("s1_a3_dcm", "solvent", "CH2Cl2", "dichloromethane", p2, "ClCCl"),
        participant("s1_a3_product", "product", "generic allenal", "generic substituted penta-3,4-dienal", p2),
    ],
    [step("arrow_3", ["s1_a3_start", "s1_a3_dmp", "s1_a3_dcm", "s1_a3_product"], [
        field("temperature", "r.t.", p2),
    ])],
    notes=[("Known procedure cited as Ref. 17; this arrow is a general scheme.", p2)],
    unresolved=scheme1_common,
))
records.append(record(
    "scheme1_arrow04_grignard_addition", "Scheme 1 arrow 4", "general_scheme", p2,
    [
        participant("s1_a4_start", "reactant", "generic allenal", "generic substituted penta-3,4-dienal", p2),
        participant("s1_a4_grignard", "reagent", "R2MgX", "generic Grignard reagent", p2),
        participant("s1_a4_ether", "solvent", "Et2O", "diethyl ether", p2, "CCOCC"),
        participant("s1_a4_product", "product", "1", "generic racemic beta-allenol 1", p2),
    ],
    [step("arrow_4", ["s1_a4_start", "s1_a4_grignard", "s1_a4_ether", "s1_a4_product"], [
        field("temperature", qty(-78, "°C", "−78 °C"), p2),
    ])],
    [
        field("two_step_yield", qrange(35, 80, "%", "35–80%"), p2, ["s1_a4_product"]),
        field("yield_measurement_basis", "total yield of Scheme 1 arrows 3 and 4", p2, ["s1_a4_product"]),
    ],
    notes=[("Known procedure cited as Ref. 17; the displayed yield spans two arrows.", p2)],
    unresolved=scheme1_common,
))


def kinetic_participants(prefix, evidence, substrate_mass, vinyl_volume, enzyme_mass, solvent=None, solvent_volume=None, products=True):
    participants = [
        participant(f"{prefix}_1a", "reactant", "1a", "racemic 5-(n-butyl)hepta-5,6-dien-3-ol", evidence,
                    "CCC(O)CC(CCCC)=C=C", [field("mass", qty(substrate_mass, "mg"), evidence)]),
        participant(f"{prefix}_va", "reagent", "AcOCH=CH2", "vinyl acetate", evidence,
                    "C=COC(C)=O", [field("volume", qty(vinyl_volume, "uL"), evidence)]),
        participant(f"{prefix}_enzyme", "catalyst", "Novozym 435", "Novozym 435 (immobilized Candida antarctica lipase B)", evidence,
                    None, [field("mass", qty(enzyme_mass, "mg"), evidence)]),
    ]
    if solvent:
        participants.append(participant(f"{prefix}_solvent", "solvent", solvent, solvent, evidence, None,
                                        [field("volume", qty(solvent_volume, "mL"), evidence)] if solvent_volume is not None else []))
    if products:
        participants.extend([
            participant(f"{prefix}_s1a", "product", "(S)-1a", "(S)-5-(n-butyl)hepta-5,6-dien-3-ol", evidence,
                        "CCC(O)CC(CCCC)=C=C"),
            participant(f"{prefix}_r2a", "product", "(R)-2a", "(R)-5-(n-butyl)hepta-5,6-dien-3-yl acetate", evidence,
                        "CCC(OC(C)=O)CC(CCCC)=C=C"),
        ])
    return participants


# Equation 1: initial condition set, distinct from the later selected conditions.
prefix = "eq1"
parts = kinetic_participants(prefix, p2, 100, 5, 70)
parts[1]["amounts"] = [field("volume", qty(5, "mL"), p2)]
records.append(record(
    "eq1_initial_kinetic_resolution", "Eq. 1", "optimization_entry", p2, parts,
    [step("kinetic_resolution", [x["entity_id"] for x in parts], [
        field("temperature", qty(30, "°C"), p2), field("time", qty(4, "d"), p2),
    ])],
    [
        field("alcohol_yield", qty(60, "%"), p2, [f"{prefix}_s1a"]),
        field("alcohol_ee", qty(46, "%"), p2, [f"{prefix}_s1a"]),
        field("ester_yield", qty(35, "%"), p2, [f"{prefix}_r2a"]),
        field("ester_ee", qty(96, "%"), p2, [f"{prefix}_r2a"]),
    ],
    unresolved=("Yield measurement basis, atmosphere, workup, purification, and SI details are not reported for Eq. 1.",
                "Candidate product SMILES encode constitution but not the depicted absolute configuration."),
))

# Scheme 2: each enzyme is a distinct failed screening condition.
for code, enzyme_name in (("ppl", "PPL"), ("crl", "CRL"), ("lipase_ak", "Lipase AK"), ("lipase_ps30", "Lipase Ps 30")):
    prefix = f"scheme2_{code}"
    parts = [
        participant(f"{prefix}_1a", "reactant", "1a", "racemic 5-(n-butyl)hepta-5,6-dien-3-ol", p2,
                    "CCC(O)CC(CCCC)=C=C", [field("mass", qty(100, "mg"), p2)]),
        participant(f"{prefix}_va", "reagent", "AcOCH=CH2", "vinyl acetate", p2, "C=COC(C)=O",
                    [field("volume", qty(5, "mL"), p2)]),
        participant(f"{prefix}_enzyme", "catalyst", enzyme_name, enzyme_name, p2, None,
                    [field("mass", qty(70, "mg"), p2)]),
    ]
    records.append(record(
        f"scheme2_{code}_no_reaction", f"Scheme 2 {enzyme_name}", "optimization_entry", p2, parts,
        [step("enzyme_screen", [x["entity_id"] for x in parts], [
            field("temperature", qty(30, "°C"), p2), field("time", qty(4, "d"), p2),
        ])],
        [field("reaction_result", "no reaction", p2)],
        notes=[("The prose qualifies the enzyme screen as extremely slow or no reaction; Scheme 2 labels the displayed outcome 'no reaction'.", p2)],
        unresolved=("Product yield and enantiomeric excess are not reported because Scheme 2 reports no reaction.",
                    "Atmosphere, workup, purification, and SI details are not reported."),
    ))

# Equation 2: elevated-temperature condition.
prefix = "eq2"
parts = kinetic_participants(prefix, p2, 50, 55, 35, "cyclohexane", 1.5)
records.append(record(
    "eq2_60c_kinetic_resolution", "Eq. 2", "optimization_entry", p2, parts,
    [step("kinetic_resolution", [x["entity_id"] for x in parts], [
        field("temperature", qty(60, "°C"), p2), field("time", qty(4, "d"), p2),
    ])],
    [
        field("alcohol_yield", qty(42, "%"), p2, [f"{prefix}_s1a"]),
        field("alcohol_ee", qty(60, "%"), p2, [f"{prefix}_s1a"]),
        field("ester_yield", qty(15, "%"), p2, [f"{prefix}_r2a"]),
        field("ester_ee", qty(97, "%"), p2, [f"{prefix}_r2a"]),
        field("enantioselectivity_E", 125, p2),
    ],
    unresolved=("Yield measurement basis, atmosphere, workup, purification, and SI details are not reported for Eq. 2.",
                "Candidate product SMILES encode constitution but not the depicted absolute configuration."),
))

# Table 1: solvent screen, one independent record per row.
table1 = [
    (1, 4, "1,4-dioxane", None, None, None, None, None),
    (2, 4, "vinyl acetate", 56, 43, 29, 95, 62),
    (3, 3, "hexane", 58, 77, 38, 97, 144),
    (4, 4, "benzene", 64, 67, 34, 97, 148),
    (5, 3, "acetone", 56, 74, 43, 97, 156),
    (6, 4, "acetonitrile", 64, 48, 35, 98, 178),
    (7, 4, "cyclohexane", 44, 74, 42, 98, 192),
]
solvent_smiles = {
    "1,4-dioxane": "C1COCCO1", "vinyl acetate": "C=COC(C)=O", "hexane": "CCCCCC",
    "benzene": "c1ccccc1", "acetone": "CC(C)=O", "acetonitrile": "CC#N", "cyclohexane": "C1CCCCC1",
}
for entry, days, solvent_name, ay, aee, ey, eee, evalue in table1:
    prefix = f"t1e{entry:02d}"
    evidence = p3 + (p2 if entry == 7 else [])
    parts = [
        participant(f"{prefix}_1a", "reactant", "1a", "racemic 5-(n-butyl)hepta-5,6-dien-3-ol", evidence,
                    "CCC(O)CC(CCCC)=C=C", [field("mass", qty(50, "mg"), evidence), field("amount", qty(0.3, "mmol"), evidence)]),
        participant(f"{prefix}_va", "reagent", "AcOCH=CH2", "vinyl acetate", evidence, "C=COC(C)=O",
                    [field("volume", qty(55, "uL"), evidence), field("amount", qty(0.6, "mmol"), evidence)]),
        participant(f"{prefix}_enzyme", "catalyst", "Novozym 435", "Novozym 435", evidence, None,
                    [field("mass", qty(35, "mg"), evidence)]),
        participant(f"{prefix}_solvent", "solvent", solvent_name, solvent_name, evidence, solvent_smiles[solvent_name],
                    [field("volume", qty(1.5, "mL"), evidence)]),
    ]
    if entry != 1:
        parts.extend([
            participant(f"{prefix}_s1a", "product", "(S)-1a", "(S)-5-(n-butyl)hepta-5,6-dien-3-ol", evidence,
                        "CCC(O)CC(CCCC)=C=C"),
            participant(f"{prefix}_r2a", "product", "(R)-2a", "(R)-5-(n-butyl)hepta-5,6-dien-3-yl acetate", evidence,
                        "CCC(OC(C)=O)CC(CCCC)=C=C"),
        ])
    outcomes = []
    if entry == 1:
        outcomes.append(field("reaction_result", "no reaction", p3))
    else:
        outcomes.extend([
            field("alcohol_yield", qty(ay, "%"), p3, [f"{prefix}_s1a"]),
            field("alcohol_ee", qty(aee, "%"), p3, [f"{prefix}_s1a"]),
            field("ester_yield", qty(ey, "%"), p3, [f"{prefix}_r2a"]),
            field("table_ester_ee", qty(eee, "%"), p3, [f"{prefix}_r2a"]),
            field("enantioselectivity_E", evalue, p3),
            field("yield_measurement_basis", "isolated yield based on 1a", p3, [f"{prefix}_s1a", f"{prefix}_r2a"]),
        ])
        if entry == 7:
            outcomes.append(field("prose_ester_ee", qty(97, "%"), p2, [f"{prefix}_r2a"]))
    unresolved = ["Atmosphere, workup, purification, and SI details are not reported for this optimization row."]
    if entry == 1:
        unresolved.append("Product yield and enantiomeric excess are not reported because the row is marked NR.")
    if entry == 7:
        unresolved.append("Table 1 gives ester ee 98%, while the page-2 prose gives 97% for the same cyclohexane condition.")
    records.append(record(
        f"table1_entry{entry:02d}", f"Table 1 entry {entry}", "optimization_entry", evidence, parts,
        [step("solvent_screen", [x["entity_id"] for x in parts], [
            field("temperature", qty(30, "°C"), p3), field("time", qty(days, "d"), p3),
        ])], outcomes,
        notes=[("Alcohol ee was determined after conversion to the corresponding acetate; ester ee was determined by GC.", p3)],
        unresolved=unresolved,
    ))

# Table 2: concentration/solvent-volume series. The row values conflict with the
# copied footnote's fixed 1.5 mL; both are preserved rather than reconciled.
table2 = [
    (1, 3.0, 68, 39, 32, 98, 172),
    (2, 2.5, 50, 58, 30, 98, 199),
    (3, 2.0, 48, 52, 37, 98, 176),
    (4, 1.0, 46, 45, 29, 98, 155),
]
for entry, solvent_volume, ay, aee, ey, eee, evalue in table2:
    prefix = f"t2e{entry:02d}"
    parts = kinetic_participants(prefix, p3, 50, 55, 35, "cyclohexane", solvent_volume)
    parts[0]["amounts"].append(field("amount", qty(0.3, "mmol"), p3))
    records.append(record(
        f"table2_entry{entry:02d}", f"Table 2 entry {entry}", "optimization_entry", p3, parts,
        [step("concentration_series", [x["entity_id"] for x in parts], [field("temperature", qty(30, "°C"), p3)])],
        [
            field("alcohol_yield", qty(ay, "%"), p3, [f"{prefix}_s1a"]),
            field("alcohol_ee", qty(aee, "%"), p3, [f"{prefix}_s1a"]),
            field("ester_yield", qty(ey, "%"), p3, [f"{prefix}_r2a"]),
            field("ester_ee", qty(eee, "%"), p3, [f"{prefix}_r2a"]),
            field("enantioselectivity_E", evalue, p3),
            field("yield_measurement_basis", "isolated yield based on 1a", p3, [f"{prefix}_s1a", f"{prefix}_r2a"]),
        ],
        notes=[("The row-specific cyclohexane volume is used; the copied Table 2 footnote separately states solvent (1.5 mL).", p3),
               ("Enantiomeric excess was determined by GC.", p3)],
        unresolved=("Table 2 row solvent volumes conflict with the footnote's fixed 1.5 mL; no correction was inferred.",
                    "Reaction time, atmosphere, workup, purification, and SI details are not reported."),
    ))

# Table 3 substrate scope. Candidate SMILES capture constitution only and do not
# encode the stated absolute configurations.
scope = [
    (1, "1a", "(S)-1a", "(R)-2a", "CCC(O)CC(CCCC)=C=C", "CCC(OC(C)=O)CC(CCCC)=C=C", 46, 83, 42, 97, 199),
    (2, "1b", "(S)-1b", "(R)-2b", "CCC(O)CC(CCC)=C=C", "CCC(OC(C)=O)CC(CCC)=C=C", 39, 82, 36, 96, 143),
    (3, "1c", "(S)-1c", "(R)-2c", "CCC(O)CC(CCCCCC)=C=C", "CCC(OC(C)=O)CC(CCCCCC)=C=C", 51, 58, 28, 98, 178),
    (4, "1d", "(S)-1d", "(R)-2d", "CCC(O)CC(CCCCCCC)=C=C", "CCC(OC(C)=O)CC(CCCCCCC)=C=C", 40, 54, 25, 98, 191),
    (5, "1e", "(S)-1e", "(R)-2e", "CCC(O)CC(CC=C)=C=C", "CCC(OC(C)=O)CC(CC=C)=C=C", 48, 50, 28, 97, 111),
    (6, "1f", "(S)-1f", "(R)-2f", "CCC(O)CC(Cc1ccccc1)=C=C", "CCC(OC(C)=O)CC(Cc1ccccc1)=C=C", 38, 71, 44, 72, 12),
    (7, "1g", "(S)-1g", "(R)-2g", "CCC(O)CC=C=C(C)C", "CCC(OC(C)=O)CC=C=C(C)C", 27, 93, 59, 22, 4),
    (8, "1h", "(S)-1h", "(R)-2h", "CCC(O)CC(CCCC)=C=C(C)C", "CCC(OC(C)=O)CC(CCCC)=C=C(C)C", 46, 44, 26, 95, 66),
    (9, "1i", "(S)-1i", "(R)-2i", "CCC(O)CC(CCCC)=C=C1CCCCC1", "CCC(OC(C)=O)CC(CCCC)=C=C1CCCCC1", 42, 96, 51, 82, 41),
    (10, "1j", "(S)-1j", "(R)-2j", "CC(O)CC(CCCC)=C=C", "CC(OC(C)=O)CC(CCCC)=C=C", 37, 88, 35, 89, 52),
    (11, "1k", "(S)-1k", "(R)-2k", "CC(O)CC(CCCC)=C=C(C)C", "CC(OC(C)=O)CC(CCCC)=C=C(C)C", 38, 91, 52, 42, 31),
    (12, "1l", "(R)-1l", "(S)-2l", "C=CC(O)CC(CCCC)=C=C", "C=CC(OC(C)=O)CC(CCCC)=C=C", 43, 93, 56, 75, 24),
    (13, "1m", "(R)-1m", "(S)-2m", "C=CC(O)CC(CCCCC)=C=C", "C=CC(OC(C)=O)CC(CCCCC)=C=C", 44, 93, 40, 85, 108),
    (14, "1n", "(R)-1n", "(S)-2n", "C#CC(O)CC(CCCC)=C=C", "C#CC(OC(C)=O)CC(CCCC)=C=C", 38, 88, 56, 44, 7),
    (15, "1o", "(R)-1o", "(S)-2o", "C#CC(O)CC(CCCCC)=C=C", "C#CC(OC(C)=O)CC(CCCCC)=C=C", 40, 90, 40, 60, 35),
]
detailed = {
    1: (p5, 110, 100, 46, 52), 2: (p5, 117, 100, 39, 46), 3: (p5, 94, 100, 51, 34),
    4: (p5 + p6, 88, 100, 40, 30), 5: (p6, 122, 70, 48, 36), 6: (p6, 92, 70, 38, 53),
    7: (p6, 132, 100, 27, 77), 8: (p6, 94, 100, 46, 31),
}
scope_names = {
    1: "5-(n-butyl)hepta-5,6-dien-3-ol", 2: "5-(n-propyl)hepta-5,6-dien-3-ol",
    3: "5-(n-hexyl)hepta-5,6-dien-3-ol", 4: "5-(n-heptyl)hepta-5,6-dien-3-ol",
    5: "5-allylhepta-5,6-dien-3-ol", 6: "5-benzylhepta-5,6-dien-3-ol",
    7: "7-methylocta-5,6-dien-3-ol", 8: "7-methyl-5-(n-butyl)octa-5,6-dien-3-ol",
}
for entry, substrate_label, alcohol_label, ester_label, alcohol_smiles, ester_smiles, ay, aee, ey, eee, evalue in scope:
    prefix = f"t3e{entry:02d}"
    extra_ev = detailed.get(entry, ([], None, None, None, None))[0]
    evidence = list(dict.fromkeys(p4 + list(extra_ev)))
    va_volume = detailed.get(entry, (None, None, None, None, None))[1]
    enzyme_mass = 70 if entry in (5, 6, 10, 12) else 100
    product_a_mass = detailed.get(entry, (None, None, None, None, None))[3]
    product_e_mass = detailed.get(entry, (None, None, None, None, None))[4]
    base_name = scope_names.get(entry, f"beta-allenol {substrate_label} as defined by Table 3 R groups")
    parts = [
        participant(f"{prefix}_substrate", "reactant", substrate_label, f"racemic {base_name}", evidence, alcohol_smiles,
                    [field("mass", qty(100, "mg"), p4)]),
        participant(f"{prefix}_va", "reagent", "AcOCH=CH2", "vinyl acetate", evidence, "C=COC(C)=O",
                    [field("equivalents", qty(2, "equiv"), p4)] + ([field("volume", qty(va_volume, "uL"), extra_ev)] if va_volume else [])),
        participant(f"{prefix}_enzyme", "catalyst", "Novozym 435", "Novozym 435", evidence, None,
                    [field("mass", qty(enzyme_mass, "mg"), p4)]),
        participant(f"{prefix}_solvent", "solvent", "cyclohexane", "cyclohexane", evidence, "C1CCCCC1",
                    [field("volume", qty(3.0, "mL"), p4)]),
        participant(f"{prefix}_alcohol", "product", alcohol_label, f"enantioenriched alcohol {alcohol_label}", evidence, alcohol_smiles,
                    [field("isolated_mass", qty(product_a_mass, "mg"), extra_ev)] if product_a_mass else []),
        participant(f"{prefix}_ester", "product", ester_label, f"enantioenriched acetate {ester_label}", evidence, ester_smiles,
                    [field("isolated_mass", qty(product_e_mass, "mg"), extra_ev)] if product_e_mass else []),
    ]
    time_value = qty(1 if entry == 7 else 4, "d")
    outcomes = [
        field("alcohol_yield", qty(ay, "%"), p4, [f"{prefix}_alcohol"]),
        field("table_alcohol_ee", qty(aee, "%"), p4, [f"{prefix}_alcohol"]),
        field("ester_yield", qty(ey, "%"), p4, [f"{prefix}_ester"]),
        field("ester_ee", qty(eee, "%"), p4, [f"{prefix}_ester"]),
        field("enantioselectivity_E", evalue, p4),
        field("yield_measurement_basis", "isolated yield based on starting allenol 1", p4, [f"{prefix}_alcohol", f"{prefix}_ester"]),
    ]
    unresolved = [
        "Candidate SMILES encode constitution only; the depicted/reported absolute configuration remains structure-unverified.",
        "Atmosphere and SI details are not reported or explicitly associated.",
    ]
    notes = [("Enantiomeric excess was determined by GC or HPLC; absolute configurations in Table 3 were tentatively assigned by the authors.", p4)]
    if entry == 1:
        notes.append(("The detailed procedure reports 96 h, equivalent to the 4 d Table 3 footnote; 96 h was not treated as a separate experiment.", p5))
    if entry == 2:
        outcomes.append(field("experimental_alcohol_ee", qty(81, "%"), p5, [f"{prefix}_alcohol"]))
        unresolved.append("Table 3 reports alcohol ee 82%, while section 3.2.2 reports 81% for the same 1b experiment.")
    if entry == 7:
        notes.append(("Section 3.2.7 and Table 3 identify 1g as 7-methylocta-5,6-dien-3-ol, but the reaction sentence prints 3-methylocta-5,6-dien-3-ol.", p6))
        unresolved.append("The internal 1g substrate-name discrepancy (7-methyl in heading/Table 3 versus 3-methyl in the reaction sentence) was not silently corrected.")
    if entry >= 9:
        unresolved.append("Pages 1–6 do not contain the complete individual experimental paragraph for this row; only Table 3 was used for quantities.")
    records.append(record(
        f"table3_entry{entry:02d}_{substrate_label}", f"Table 3 entry {entry}", "substrate_scope_entry", evidence, parts,
        [step("kinetic_resolution", [x["entity_id"] for x in parts], [
            field("temperature", qty(30, "°C"), p4), field("time", time_value, p4),
            field("purification", "flash chromatography on silica gel (petroleum ether/ether 40:1 to 10:1)", p5) if entry == 1 else field("purification", None, ()),
        ])], outcomes, notes=notes, unresolved=unresolved,
    ))

# Equation 3: Pd-catalyzed coupling/cyclization.
parts = [
    participant("eq3_r1a", "reactant", "(R)-1a", "(R)-5-(n-butyl)hepta-5,6-dien-3-ol", p4, "CCC(O)CC(CCCC)=C=C",
                [field("reactant_ee", qty(97, "%"), p4)]),
    participant("eq3_allyl_bromide", "reagent", "allylic bromide", "allyl bromide", p4, "C=CCBr",
                [field("equivalents", qty(5, "equiv"), p4)]),
    participant("eq3_pdcl2", "catalyst", "PdCl2", "palladium(II) chloride", p4, "Cl[Pd]Cl",
                [field("catalyst_loading", qty(5, "mol%"), p4)]),
    participant("eq3_dma", "solvent", "DMA", "N,N-dimethylacetamide", p4, "CC(=O)N(C)C"),
    participant("eq3_r3a", "product", "(R)-3a", "(R)-6-ethyl-3-allyl-4-(n-butyl)-5,6-dihydro-2H-pyran", p4),
]
records.append(record(
    "eq3_pd_coupling_cyclization", "Eq. 3", "reported_experiment", p4, parts,
    [step("coupling_cyclization", [x["entity_id"] for x in parts], [
        field("temperature", qty(25, "°C"), p4), field("time", qty(7, "h"), p4),
    ])],
    [field("product_yield", qty(64, "%"), p4, ["eq3_r3a"]), field("product_ee", qty(97, "%"), p4, ["eq3_r3a"])],
    unresolved=("Reactant scale, solvent volume, atmosphere, workup, purification, yield basis, and SI details are absent from Eq. 3 on page 4.",
                "The cyclic product SMILES is left null because its full stereochemical drawing was not encoded with confidence."),
))

# Section 3.1.1: split each successive transformation into an independent record.
parts = [
    participant("exp311a_alkyne", "reactant", "hepta-2-yn-1-ol", "hepta-2-yn-1-ol", p4, "CCCCC#CCO",
                [field("mass", qty(6.12, "g"), p4), field("amount", qty(54.7, "mmol"), p4)]),
    participant("exp311a_orthoacetate", "reagent", "triethyl orthoacetate", "triethyl orthoacetate", p4, "CCOC(C)(OCC)OCC",
                [field("volume", qty(34.8, "mL"), p4), field("amount", qty(189, "mmol"), p4)]),
    participant("exp311a_propionic", "reagent", "propionic acid", "propionic acid", p4, "CCC(=O)O",
                [field("initial_volume", qty(0.68, "mL"), p4), field("additional_volume", qty(0.5, "mL"), p4)]),
    participant("exp311a_product", "product", "ethyl 3-(n-butyl)penta-3,4-dienoate", "ethyl 3-(n-butyl)penta-3,4-dienoate", p4,
                "CCOC(=O)CC(CCCC)=C=C"),
]
records.append(record(
    "exp_3_1_1_stage1_allenoate", "Section 3.1.1 stage 1", "reported_experiment", p4, parts,
    [step("orthoester_rearrangement", [x["entity_id"] for x in parts], [
        field("atmosphere", "nitrogen", p4), field("temperature", qrange(140, 150, "°C", "140–150 °C"), p4),
        field("time", qty(5, "h"), p4), field("operation", "remove resulting ethanol with a Dean–Stark trap", p4),
        field("purification", "silica-gel chromatography", p4),
    ])],
    [field("product_yield", None, (), ["exp311a_product"]), field("yield_measurement_basis", None, (), ["exp311a_product"])],
    notes=[("An additional 0.5 mL of propionic acid was added after 145 min; this is structured on the propionic-acid participant.", p4),
           ("The allenoate was submitted directly to the next step without further characterization.", p4)],
    unresolved=("No stage-specific allenoate mass or yield is reported.", "The chromatography eluent is not specified for this stage.", "SI association is unestablished."),
))

parts = [
    participant("exp311b_allenoate", "reactant", "ethyl 3-(n-butyl)penta-3,4-dienoate", "ethyl 3-(n-butyl)penta-3,4-dienoate", p4,
                "CCOC(=O)CC(CCCC)=C=C"),
    participant("exp311b_lialh4", "reagent", "LiAlH4", "lithium aluminium hydride", p4, "[Li+].[AlH4-]",
                [field("mass", qty(2.13, "g"), p4), field("amount", qty(56.1, "mmol"), p4)]),
    participant("exp311b_thf", "solvent", "dried THF", "tetrahydrofuran", p4, "C1CCOC1",
                [field("suspension_volume", qty(72, "mL"), p4), field("substrate_solution_volume", qty(72, "mL"), p4)]),
    participant("exp311b_water", "reagent", "water", "water", p4, "O"),
    participant("exp311b_na2so4", "reagent", "anhydrous Na2SO4", "anhydrous sodium sulfate", p4, "[Na+].[Na+].[O-]S(=O)(=O)[O-]"),
    participant("exp311b_product", "product", "3-(n-butyl)penta-3,4-dien-1-ol", "3-(n-butyl)penta-3,4-dien-1-ol", p4,
                "OCCC(CCCC)=C=C", [field("isolated_mass", qty(4.65, "g"), p4)]),
]
records.append(record(
    "exp_3_1_1_stage2_lialh4_reduction", "Section 3.1.1 stage 2", "reported_experiment", p4, parts,
    [
        step("reduction", ["exp311b_allenoate", "exp311b_lialh4", "exp311b_thf", "exp311b_product"], [
            field("addition_temperature", qty(0, "°C"), p4), field("temperature", "r.t.", p4), field("time", qty(1, "h"), p4),
        ]),
        step("workup", ["exp311b_water", "exp311b_na2so4", "exp311b_product"], [
            field("quench_temperature", qty(0, "°C"), p4),
            field("purification", "silica-gel chromatography; petroleum ether/ethyl ether 10:1", p4),
        ]),
    ],
    [field("two_step_yield", qty(61, "%"), p4, ["exp311b_product"]),
     field("yield_measurement_basis", "two steps from hepta-2-yn-1-ol", p4, ["exp311b_product"])],
    unresolved=("The amount of allenoate carried into the reduction is not separately reported.", "Water quench volume is missing.", "SI association is unestablished."),
))

parts = [
    participant("exp311c_alcohol", "reactant", "3-(n-butyl)penta-3,4-dien-1-ol", "3-(n-butyl)penta-3,4-dien-1-ol", p4,
                "OCCC(CCCC)=C=C", [field("mass", qty(1.57, "g"), p4), field("amount", qty(11.2, "mmol"), p4)]),
    participant("exp311c_dmp", "reagent", "DMP", "Dess–Martin periodinane", p4, None,
                [field("mass", qty(6.61, "g"), p4), field("amount", qty(17.6, "mmol"), p4)]),
    participant("exp311c_dcm", "solvent", "CH2Cl2", "dichloromethane", p4, "ClCCl",
                [field("substrate_solution_volume", qty(5, "mL"), p4), field("dmp_suspension_volume", qty(15, "mL"), p4)]),
    participant("exp311c_ether", "solvent", "ethyl ether", "diethyl ether", p4, "CCOCC",
                [field("dilution_volume", qty(30, "mL"), p4), field("extraction_volume_each", qty(30, "mL"), p4)]),
    participant("exp311c_nahco3", "reagent", "saturated NaHCO3", "saturated sodium bicarbonate solution", p4, "[Na+].O=C([O-])O",
                [field("volume", qty(50, "mL"), p4)]),
    participant("exp311c_thiosulfate", "reagent", "sodium thiosulfate", "sodium thiosulfate", p4, "[Na+].[Na+].[O-]S(=O)([O-])=S",
                [field("mass", qty(30.00, "g"), p4), field("amount", qty(121, "mmol"), p4)]),
    participant("exp311c_na2so4", "reagent", "anhydrous Na2SO4", "anhydrous sodium sulfate", p4, "[Na+].[Na+].[O-]S(=O)(=O)[O-]"),
    participant("exp311c_allenal", "product", "allenal", "3-(n-butyl)penta-3,4-dienal", p4, "O=CCC(CCCC)=C=C"),
]
records.append(record(
    "exp_3_1_1_stage3_dmp_oxidation", "Section 3.1.1 stage 3", "reported_experiment", p4, parts,
    [
        step("oxidation", ["exp311c_alcohol", "exp311c_dmp", "exp311c_dcm", "exp311c_allenal"], [field("time", qty(0.5, "h"), p4), field("temperature", None, ())]),
        step("workup", ["exp311c_ether", "exp311c_nahco3", "exp311c_thiosulfate", "exp311c_na2so4", "exp311c_allenal"], [
            field("time", qty(30, "min"), p4), field("operation", "aqueous layer extracted three times; each extraction used 30 mL ethyl ether", p4),
        ]),
    ],
    [field("product_yield", None, (), ["exp311c_allenal"]), field("yield_measurement_basis", None, (), ["exp311c_allenal"])],
    notes=[("The allenal was used without further purification.", p4)],
    unresolved=("Oxidation temperature and allenal mass/yield are not reported.", "SI association is unestablished."),
))

parts = [
    participant("exp311d_allenal", "reactant", "allenal", "3-(n-butyl)penta-3,4-dienal", p5, "O=CCC(CCCC)=C=C"),
    participant("exp311d_etmgbr", "reagent", "EtMgBr", "ethylmagnesium bromide", p5, "CC[Mg]Br",
                [field("concentration", qty(1, "M"), p5), field("volume", qty(20, "mL"), p5)]),
    participant("exp311d_ether", "solvent", "ethyl ether", "diethyl ether", p5, "CCOCC",
                [field("reaction_volume", qty(20, "mL"), p5), field("extraction_volume_each", qty(30, "mL"), p5)]),
    participant("exp311d_nh4cl", "reagent", "saturated NH4Cl", "saturated ammonium chloride solution", p5, "[Cl-].[NH4+]"),
    participant("exp311d_na2so4", "reagent", "anhydrous Na2SO4", "anhydrous sodium sulfate", p5, "[Na+].[Na+].[O-]S(=O)(=O)[O-]"),
    participant("exp311d_1a", "product", "racemic 1a", "racemic 5-(n-butyl)hepta-5,6-dien-3-ol", p5, "CCC(O)CC(CCCC)=C=C",
                [field("isolated_mass", qty(0.90, "g"), p5)]),
]
records.append(record(
    "exp_3_1_1_stage4_etmgbr_addition", "Section 3.1.1 stage 4", "reported_experiment", p5, parts,
    [
        step("grignard_addition", ["exp311d_allenal", "exp311d_etmgbr", "exp311d_ether", "exp311d_1a"], [
            field("atmosphere", "nitrogen", p5), field("addition_temperature", qty(-78, "°C"), p5),
            field("temperature", qty(-78, "°C"), p5), field("time", qty(10, "h"), p5),
        ]),
        step("workup", ["exp311d_nh4cl", "exp311d_ether", "exp311d_na2so4", "exp311d_1a"], [
            field("quench_temperature", qty(-78, "°C"), p5), field("warm_to", "r.t.", p5),
            field("operation", "aqueous layer extracted three times; each extraction used 30 mL ethyl ether", p5),
            field("purification", "silica-gel chromatography; petroleum ether/ethyl ether 15:1", p5),
        ]),
    ],
    [field("product_yield", qty(48, "%"), p5, ["exp311d_1a"]), field("yield_measurement_basis", None, (), ["exp311d_1a"])],
    unresolved=("The allenal amount and the explicit basis of the reported 48% yield are not stated.", "NH4Cl volume is missing.", "SI association is unestablished."),
))


def rid(suffix):
    return f"{DOC}:{suffix}"


coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1,
            "state": "attempted",
            "regions": [
                {"region": "title, abstract, and two-column introduction", "finding": "Article metadata and background; cited prior syntheses and biocatalytic resolutions are literature context, not experiments reported in this paper.", "evidence_ids": [ev(1), ev(1, "text")]},
                {"region": "lower-right Results and discussion opening", "finding": "Section 2.1 points to the known Scheme 1 procedure and section 2.2 begins the 1a resolution discussion; the reaction drawing and complete conditions continue on page 2.", "evidence_ids": [ev(1), ev(1, "text")]},
            ],
            "record_ids": [],
            "unresolved": ["No independent, fully specified experiment is contained entirely on page 1; prior-work citations were not converted into records."],
        },
        {
            "page": 2,
            "state": "attempted",
            "regions": [
                {"region": "upper half, Scheme 1 arrows and 1a–1r R-group list", "finding": "Four-arrow generic preparation route attributed to Ref. 17; retained as four general-scheme records, not as new reported experiments.", "evidence_ids": [ev(2), ev(2, "text")]},
                {"region": "lower-left, Eq. 1", "finding": "Initial Novozym 435 kinetic resolution of 1a with product-specific yields and ee values.", "evidence_ids": [ev(2), ev(2, "text")]},
                {"region": "lower-left, Scheme 2", "finding": "Four separately enumerated enzyme screens (PPL, CRL, Lipase AK, Lipase Ps 30), each displayed as no reaction.", "evidence_ids": [ev(2), ev(2, "text")]},
                {"region": "lower-right, Eq. 2", "finding": "60 °C kinetic-resolution condition with two product yields/ee values and E=125.", "evidence_ids": [ev(2), ev(2, "text")]},
            ],
            "record_ids": [
                rid("scheme1_arrow01_orthoester_rearrangement"), rid("scheme1_arrow02_lialh4_reduction"),
                rid("scheme1_arrow03_dmp_oxidation"), rid("scheme1_arrow04_grignard_addition"),
                rid("eq1_initial_kinetic_resolution"), rid("scheme2_ppl_no_reaction"), rid("scheme2_crl_no_reaction"),
                rid("scheme2_lipase_ak_no_reaction"), rid("scheme2_lipase_ps30_no_reaction"), rid("eq2_60c_kinetic_resolution"),
            ],
            "unresolved": ["Scheme 1 generic structures cannot be expanded to a single SMILES.", "Eq. 1, Scheme 2, and Eq. 2 omit atmosphere/workup/purification details."],
        },
        {
            "page": 3,
            "state": "attempted",
            "regions": [
                {"region": "upper half, Table 1 including arrow, seven rows, and footnotes", "finding": "Seven independent solvent-screen entries; entry 1 is NR and entry 7 has a 98% table versus 97% prose ester-ee discrepancy.", "evidence_ids": [ev(3), ev(3, "text")]},
                {"region": "middle, Table 2 including arrow, four rows, and footnotes", "finding": "Four independent concentration/solvent-volume entries; row volumes conflict with the copied fixed 1.5 mL footnote and were not silently reconciled.", "evidence_ids": [ev(3), ev(3, "text")]},
                {"region": "bottom-right, Scheme 3", "finding": "Stereochemical assignment/comparison diagram for (+)-1r versus known (R)-(-)-1r; no reaction arrow or independent synthetic experiment.", "evidence_ids": [ev(3), ev(3, "text")]},
                {"region": "bottom prose", "finding": "Scope discussion and tentative absolute-configuration assignment; Table 3 itself continues on page 4.", "evidence_ids": [ev(3), ev(3, "text")]},
            ],
            "record_ids": [*[rid(f"table1_entry{i:02d}") for i in range(1, 8)], *[rid(f"table2_entry{i:02d}") for i in range(1, 5)]],
            "unresolved": ["Table 2 does not report reaction time.", "The Table 2 row-volume/footnote discrepancy remains unresolved."],
        },
        {
            "page": 4,
            "state": "attempted",
            "regions": [
                {"region": "upper half, Table 3 arrow, entries 1–15, and footnotes", "finding": "Fifteen independent substrate-scope rows with shared conditions, two product-specific yields/ee values, and E values; footnotes override enzyme mass for entries 5, 6, 10, 12 and time for entry 7.", "evidence_ids": [ev(4), ev(4, "text")]},
                {"region": "middle-left, Eq. 3", "finding": "PdCl2-catalyzed coupling/cyclization of (R)-1a with allyl bromide to (R)-3a.", "evidence_ids": [ev(4), ev(4, "text")]},
                {"region": "lower section 3.1.1, first two preparation stages", "finding": "Detailed orthoester rearrangement/allenoate formation followed by LiAlH4 reduction; stages were separated and the reported 61% two-step yield was attached to the second-stage product.", "evidence_ids": [ev(4), ev(4, "text")]},
                {"region": "lower-right section 3.1.1, DMP stage", "finding": "DMP oxidation and explicit workup to an unpurified allenal; stage-specific yield and temperature are missing.", "evidence_ids": [ev(4), ev(4, "text")]},
            ],
            "record_ids": [
                *[rid(f"table3_entry{i:02d}_{scope[i-1][1]}") for i in range(1, 16)], rid("eq3_pd_coupling_cyclization"),
                rid("exp_3_1_1_stage1_allenoate"), rid("exp_3_1_1_stage2_lialh4_reduction"), rid("exp_3_1_1_stage3_dmp_oxidation"),
            ],
            "unresolved": ["Table 3 absolute configurations are tentative in the source.", "Full experimental paragraphs for Table 3 entries 9–15 fall outside pages 1–6."],
        },
        {
            "page": 5,
            "state": "attempted",
            "regions": [
                {"region": "upper-left continuation of section 3.1.1", "finding": "EtMgBr addition to the preceding allenal at −78 °C and workup/purification to racemic 1a; isolated yield basis is not explicit.", "evidence_ids": [ev(5), ev(5, "text")]},
                {"region": "left column section 3.2.1", "finding": "Detailed typical kinetic resolution of 1a; merged with Table 3 entry 1 rather than duplicated.", "evidence_ids": [ev(5), ev(5, "text")]},
                {"region": "lower-left/right sections 3.2.2–3.2.4", "finding": "Detailed 1b, 1c, and beginning of 1d scope experiments; merged with Table 3 entries 2–4. Section 3.2.2 reports 81% alcohol ee versus 82% in Table 3.", "evidence_ids": [ev(5), ev(5, "text")]},
            ],
            "record_ids": [rid("exp_3_1_1_stage4_etmgbr_addition"), rid("table3_entry01_1a"), rid("table3_entry02_1b"), rid("table3_entry03_1c"), rid("table3_entry04_1d")],
            "unresolved": ["The 48% yield basis in the EtMgBr stage is not explicit.", "The 1b alcohol-ee discrepancy (81% experimental paragraph versus 82% table) remains unresolved."],
        },
        {
            "page": 6,
            "state": "attempted",
            "regions": [
                {"region": "upper-left continuation of section 3.2.4", "finding": "Continuation of 1d product characterization; no new reaction condition set.", "evidence_ids": [ev(6), ev(6, "text")]},
                {"region": "left/right columns sections 3.2.5–3.2.8", "finding": "Detailed 1e–1h kinetic-resolution experiments; merged with Table 3 entries 5–8 rather than duplicated.", "evidence_ids": [ev(6), ev(6, "text")]},
                {"region": "bottom-right start of section 3.2.9", "finding": "Heading and opening fragment for 1i; the complete individual procedure continues on page 7, so page-4 Table 3 data remain the record basis.", "evidence_ids": [ev(6), ev(6, "text")]},
            ],
            "record_ids": [*[rid(f"table3_entry{i:02d}_{scope[i-1][1]}") for i in range(4, 10)]],
            "unresolved": ["The complete 1i experimental paragraph is outside the requested page range.", "Spectroscopic characterization was inspected for context but not expanded into reaction-condition fields."],
        },
    ],
}


OUT.parent.mkdir(parents=True, exist_ok=True)
COVERAGE.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
COVERAGE.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

# Mark only this session's page tasks attempted; pages 7–9 remain pending.
tasks = json.loads(TASKS.read_text())
for item in tasks:
    page = int(item["evidence_id"].split(":page", 1)[1].split(":", 1)[0])
    if 1 <= page <= 6:
        item["state"] = "attempted"
        item["visual_evidence_id"] = ev(page)
        item["reason"] = "Original page image inspected; regions and record mappings saved in coverage/pages_0001_0006.json."
TASKS.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"records": len(records), "coverage_pages": [p["page"] for p in coverage["pages"]], "output": str(OUT)}, ensure_ascii=False))
