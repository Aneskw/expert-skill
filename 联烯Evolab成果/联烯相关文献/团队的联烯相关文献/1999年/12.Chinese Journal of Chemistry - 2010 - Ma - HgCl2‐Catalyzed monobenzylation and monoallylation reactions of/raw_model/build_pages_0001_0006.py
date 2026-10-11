#!/usr/bin/env python3
"""Build evidence-linked machine records for source.pdf pages 1-6."""
import json
from pathlib import Path

DOC = "doc_aef3035bf01be80f"
OUT = Path(__file__).resolve().parent


def ev(*pages):
    ids = []
    for page in pages:
        ids.extend([f"{DOC}:page{page}:text", f"{DOC}:page{page}:image"])
    return ids


def fact(value, evidence=()):
    return {
        "value": value,
        "evidence_ids": list(evidence) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def field(name, value, evidence=()):
    return {"name": name, "fact": fact(value, evidence)}


def participant(entity_id, role, label, name, evidence, amounts=()):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence),
        "smiles": fact(None),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": [field(n, v, evidence) for n, v in amounts],
    }


def step(step_id, participant_ids, conditions):
    return {
        "step_id": step_id,
        "participant_ids": participant_ids,
        "conditions": conditions,
    }


def record(suffix, source_id, kind, evidence, participants=(), steps=(), outcomes=(), notes=(), unresolved=()):
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
        "notes": [fact(v, e) for v, e in notes],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": list(unresolved),
        },
    }


records = []

# Introductory equation: explicitly attributed to the authors' earlier Ref. 5 work.
e = ev(1)
records.append(record(
    "intro_eq1_prior_benzylation", "Eq. 1", "literature_example", e,
    participants=[
        participant("eq1_1a", "reactant", "1a", "1-phenyl-1-propyne", e),
        participant("eq1_hgcl2", "catalyst", "HgCl2", "mercury(II) chloride", e,
                    [("catalyst_loading", {"number": 1.5, "unit": "mol%"})]),
        participant("eq1_nbuli", "reagent", "n-BuLi", "n-butyllithium", e),
        participant("eq1_benzyl_bromide", "reagent", "PhCH2Br", "benzyl bromide", e),
        participant("eq1_product", "product", None, "1,4-diphenyl-1-butyne", e),
    ],
    steps=[step("eq1_lithiation_and_benzylation", ["eq1_1a", "eq1_hgcl2", "eq1_nbuli", "eq1_benzyl_bromide", "eq1_product"], [
        field("lithiation_temperature", {"number": -78, "unit": "°C"}, e),
        field("reaction_time", None),
    ])],
    notes=[("Introductory Eq. 1 is presented as the authors' previously developed method (Ref. 5), not as a new experiment of this paper.", e)],
    unresolved=["No yield, charge, solvent, workup, or purification is reported in Eq. 1.", "The depicted structure has not been encoded as verified SMILES."],
))


def benzylation_participants(prefix, substrate_label, substrate_name, products, evidence, detailed=None):
    detailed = detailed or {}
    return [
        participant(f"{prefix}_substrate", "reactant", substrate_label, substrate_name, evidence, detailed.get("substrate", ())),
        participant(f"{prefix}_hgcl2", "catalyst", "HgCl2", "mercury(II) chloride", evidence,
                    detailed.get("hgcl2", (("catalyst_loading", {"number": 1.5, "unit": "mol%"}),))),
        participant(f"{prefix}_nbuli", "reagent", "n-BuLi", "n-butyllithium", evidence, detailed.get("nbuli", ())),
        participant(f"{prefix}_benzyl_bromide", "reagent", "PhCH2Br", "benzyl bromide", evidence, detailed.get("benzyl_bromide", ())),
        participant(f"{prefix}_product_alkyne", "product", products[0][0], products[0][1], evidence),
        participant(f"{prefix}_product_allene", "product", products[1][0], products[1][1], evidence),
    ]


# Scheme 1 optimization at -78 °C: explicit failed reaction.
e = ev(2)
prefix = "scheme1_minus78"
parts = benzylation_participants(prefix, "1b", "1-phenyl-1-butyne",
                                 (("2b", "3-methyl-1,4-diphenyl-1-butyne"), ("3b", "1,2-diphenyl-2,3-pentadiene")), e)
records.append(record(
    prefix, "Scheme 1, -78 °C row", "optimization_entry", e, parts,
    [step("lithiation_and_benzylation", [p["entity_id"] for p in parts], [
        field("temperature", {"number": -78, "unit": "°C"}, e),
        field("reaction_time", {"number": 10, "unit": "h"}, e),
    ])],
    [field("yield_2b", {"number": 0, "unit": "%"}, e), field("yield_3b", {"number": 0, "unit": "%"}, e),
     field("result", "no reaction / neither product detected as reported by 0% yields", e)],
    unresolved=["Reagent charges, solvent, workup, purification, and yield measurement basis are not stated for this row."],
))

# Scheme 1 room-temperature result merged with the page-6 typical procedure.
e = ev(2, 5, 6)
prefix = "scheme1_25c"
parts = benzylation_participants(prefix, "1b", "1-phenyl-1-butyne",
    (("2b", "3-methyl-1,4-diphenyl-1-butyne"), ("3b", "1,2-diphenyl-2,3-pentadiene")), e,
    {
        "substrate": (("mass", {"number": 130, "unit": "mg"}), ("amount", {"number": 1.0, "unit": "mmol"})),
        "hgcl2": (("mass", {"number": 4, "unit": "mg"}), ("catalyst_loading", {"number": 1.5, "unit": "mol%"})),
        "nbuli": (("concentration", {"number": 1.6, "unit": "mol/L"}), ("solution_volume", {"number": 0.63, "unit": "mL"}), ("amount", {"number": 1.0, "unit": "mmol"})),
        "benzyl_bromide": (("mass", {"number": 205, "unit": "mg"}), ("amount", {"number": 1.2, "unit": "mmol"})),
    })
parts.append(participant(f"{prefix}_thf", "solvent", "THF", "tetrahydrofuran", e, (("volume", {"number": 5, "unit": "mL"}),)))
records.append(record(
    prefix, "Scheme 1, 25 °C row / typical procedure", "optimization_entry", e, parts,
    [
        step("lithiation", [f"{prefix}_substrate", f"{prefix}_hgcl2", f"{prefix}_nbuli", f"{prefix}_thf"], [
            field("addition_temperature", {"number": -78, "unit": "°C"}, ev(6)),
            field("warming", "warmed immediately to room temperature", ev(6)),
            field("time_at_room_temperature_before_benzyl_bromide", {"number": 0.5, "unit": "h"}, ev(6)),
        ]),
        step("benzylation", [f"{prefix}_substrate", f"{prefix}_benzyl_bromide", f"{prefix}_product_alkyne", f"{prefix}_product_allene"], [
            field("scheme_1_reaction_time", {"number": 5, "unit": "h"}, ev(2)),
            field("typical_procedure_time_after_benzyl_bromide", {"number": 6, "unit": "h"}, ev(6)),
            field("temperature", "room temperature", ev(6)),
        ]),
        step("workup_and_purification", [f"{prefix}_product_alkyne", f"{prefix}_product_allene"], [
            field("quench", "saturated NH4Cl", ev(6)),
            field("extraction", "petroleum ether (60-90 °C)", ev(6)),
            field("wash", "saturated NaCl", ev(6)),
            field("drying", "MgSO4", ev(6)),
            field("purification", "silica-gel chromatography (petroleum ether)", ev(6)),
        ]),
    ],
    [field("isolated_mass_2b", {"number": 138, "unit": "mg"}, ev(6)), field("yield_2b", {"number": 67, "unit": "%"}, e),
     field("isolated_mass_3b", {"number": 45, "unit": "mg"}, ev(6)), field("yield_3b", {"number": 22, "unit": "%"}, e)],
    notes=[("Scheme 1 lists 5 h, while the typical procedure says quenching 6 h after benzyl bromide addition; both source statements are retained.", e)],
    unresolved=["The 5 h versus 6 h reaction-time discrepancy is unresolved.", "Atmosphere and reaction concentration are not reported.", "No SI was supplied for additional verification."],
))

# Equation 2 merged with the page-6 preparation.
e = ev(2, 6)
prefix = "eq2_1c_benzylation"
parts = benzylation_participants(prefix, "1c", "1-phenyl-1-hexyne",
    (("2c", "1-phenyl-3-benzyl-1-hexyne"), ("3c", "1,2-diphenyl-2,3-heptadiene")), e,
    {
        "substrate": (("mass", {"number": 158, "unit": "mg"}), ("amount", {"number": 1.0, "unit": "mmol"})),
        "hgcl2": (("mass", {"number": 4, "unit": "mg"}), ("catalyst_loading", {"number": 1.5, "unit": "mol%"})),
        "nbuli": (("concentration", {"number": 1.6, "unit": "mol/L"}), ("solution_volume", {"number": 0.63, "unit": "mL"}), ("amount", {"number": 1.0, "unit": "mmol"})),
        "benzyl_bromide": (("mass", {"number": 205, "unit": "mg"}), ("amount", {"number": 1.2, "unit": "mmol"})),
    })
records.append(record(
    prefix, "Eq. 2 / preparation 2c and 3c", "substrate_scope_entry", e, parts,
    [step("monolithiation_and_benzylation", [p["entity_id"] for p in parts], [
        field("monolithiation_temperature", {"number": 25, "unit": "°C"}, ev(2)),
        field("specific_reaction_time", None),
    ])],
    [field("isolated_mass_2c", {"number": 104, "unit": "mg"}, ev(6)), field("yield_2c", {"number": 42, "unit": "%"}, e),
     field("isolated_mass_3c", {"number": 97, "unit": "mg"}, ev(6)), field("yield_3c", {"number": 39, "unit": "%"}, e)],
    notes=[("Page 6 states that these compounds were prepared similarly to the preceding typical benzylation procedure.", ev(6))],
    unresolved=["The page-6 'prepared similarly' statement does not restate time, solvent volume, workup, or purification for this individual run.", "Atmosphere and concentration are missing."],
))


# Table 1: nine independent monoallylation experiments.
table_rows = [
    (1, "1a", "1-phenyl-1-propyne", "H", "Br", 6, "4a", 70, "5a", 27),
    (2, "1a", "1-phenyl-1-propyne", "Cl", "Cl", 5, "4b", 60, "5b", 37),
    (3, "1a", "1-phenyl-1-propyne", "Me", "Cl", 6, "4c", 48, "5c", 45),
    (4, "1a", "1-phenyl-1-propyne", "Br", "Br", 4, "4d", 52, "5d", 31),
    (5, "1b", "1-phenyl-1-butyne", "H", "Br", 5, "4e", 25, "5e", 51),
    (6, "1b", "1-phenyl-1-butyne", "Me", "Cl", 9, "4f", 36, "5f", 50),
    (7, "1c", "1-phenyl-1-hexyne", "H", "Br", 5, "4g", 30, "5g", 53),
    (8, "1c", "1-phenyl-1-hexyne", "Me", "Cl", 9, "4h", 32, "5h", 48),
    (9, "1d", "1,4-diphenyl-1-butyne", "H", "Br", 5, "4i", 28, "5i", 48),
]
electrophiles = {
    ("H", "Br"): "allyl bromide",
    ("Cl", "Cl"): "2,3-dichloro-1-propene",
    ("Me", "Cl"): "3-chloro-2-methyl-1-propene",
    ("Br", "Br"): "2,3-dibromo-1-propene",
}
product_names = {
    "4a": "1-phenyl-5-hexen-1-yne", "5a": "3-phenyl-1,2,5-hexatriene",
    "4b": "1-phenyl-5-chloro-5-hexen-1-yne", "5b": "3-phenyl-5-chloro-1,2,5-hexatriene",
    "4c": "5-methyl-1-phenyl-5-hexen-1-yne", "5c": "5-methyl-3-phenyl-1,2,5-hexatriene",
    "4d": "5-bromo-1-phenyl-5-hexen-1-yne", "5d": "5-bromo-3-phenyl-1,2,5-hexatriene",
    "4e": "3-methyl-1-phenyl-5-hexen-1-yne", "5e": "3-phenyl-1,3,5-heptatriene",
}
detail_pages = {1: (4, 5), 2: (5,), 3: (5,), 4: (5,), 5: (6,)}
charge_data = {
    1: (116, 4, 0.63, 145, 1.2, 109, 42),
    2: (116, 4, 0.63, 133, 1.2, 114, 70),
    3: (116, 4, 0.63, 107, 1.2, 82, 77),
    4: (116, 4, 0.63, 240, 1.2, 122, 73),
    5: (130, 4, 0.63, 145, 1.2, 43, 88),
}
for row, sub_label, sub_name, r2, x, hours, p4, y4, p5, y5 in table_rows:
    pages = (3,) + detail_pages.get(row, ())
    e = ev(*pages)
    prefix = f"table1_entry{row}"
    amounts = charge_data.get(row)
    sub_amounts = (("mass", {"number": amounts[0], "unit": "mg"}), ("amount", {"number": 1.0, "unit": "mmol"})) if amounts else ()
    hg_amounts = (("mass", {"number": amounts[1], "unit": "mg"}), ("catalyst_loading", {"number": 1.5, "unit": "mol%"})) if amounts else (("catalyst_loading", {"number": 1.5, "unit": "mol%"}),)
    nb_amounts = (("concentration", {"number": 1.6, "unit": "mol/L"}), ("solution_volume", {"number": amounts[2], "unit": "mL"}), ("amount", {"number": 1.0, "unit": "mmol"})) if amounts else ()
    allyl_amounts = (("mass", {"number": amounts[3], "unit": "mg"}), ("amount", {"number": amounts[4], "unit": "mmol"})) if amounts else ()
    parts = [
        participant(f"{prefix}_substrate", "reactant", sub_label, sub_name, e, sub_amounts),
        participant(f"{prefix}_hgcl2", "catalyst", "HgCl2", "mercury(II) chloride", e, hg_amounts),
        participant(f"{prefix}_nbuli", "reagent", "n-BuLi", "n-butyllithium", e, nb_amounts),
        participant(f"{prefix}_allyl_halide", "reagent", f"R2={r2}, X={x}", electrophiles[(r2, x)], e, allyl_amounts),
        participant(f"{prefix}_product4", "product", p4, product_names.get(p4), e),
        participant(f"{prefix}_product5", "product", p5, product_names.get(p5), e),
    ]
    if row == 1:
        parts.append(participant(f"{prefix}_thf", "solvent", "THF", "tetrahydrofuran", e, (("volume", {"number": 5, "unit": "mL"}),)))
    lith_temp = {"number": -78, "unit": "°C"} if sub_label == "1a" else "room temperature"
    steps = [step("monolithiation_and_allylation", [p["entity_id"] for p in parts], [
        field("monolithiation_temperature", lith_temp, ev(3)),
        field("reaction_time", {"number": hours, "unit": "h"}, ev(3)),
    ])]
    if row == 1:
        steps = [
            step("monolithiation", [f"{prefix}_substrate", f"{prefix}_hgcl2", f"{prefix}_nbuli", f"{prefix}_thf"], [
                field("temperature", {"number": -78, "unit": "°C"}, ev(4)),
                field("time_before_allyl_bromide", {"number": 10, "unit": "min"}, ev(4)),
            ]),
            step("allylation", [f"{prefix}_substrate", f"{prefix}_allyl_halide", f"{prefix}_product4", f"{prefix}_product5"], [
                field("addition_temperature", {"number": -78, "unit": "°C"}, ev(4)),
                field("warming", "allowed to warm naturally to room temperature", ev(4)),
                field("time_at_room_temperature", {"number": 6, "unit": "h"}, ev(4)),
            ]),
            step("workup_and_purification", [f"{prefix}_product4", f"{prefix}_product5"], [
                field("quench", "saturated NH4Cl", ev(4)), field("extraction", "petroleum ether (60-90 °C)", ev(4)),
                field("wash", "saturated NaCl", ev(4)), field("drying", "MgSO4", ev(4)),
                field("purification", "silica-gel chromatography (petroleum ether)", ev(4)),
            ]),
        ]
    outcomes = [field(f"isolated_yield_{p4}", {"number": y4, "unit": "%"}, ev(3)), field(f"isolated_yield_{p5}", {"number": y5, "unit": "%"}, ev(3))]
    if amounts:
        outcomes += [field(f"isolated_mass_{p4}", {"number": amounts[5], "unit": "mg"}, ev(detail_pages[row][-1])),
                     field(f"isolated_mass_{p5}", {"number": amounts[6], "unit": "mg"}, ev(detail_pages[row][-1]))]
    notes = [("Table 1 footnote c states that yields are isolated yields.", ev(3)),
             ("Table 1 footnote b reports satisfactory 1H NMR, IR, MS, and elemental-analysis or HRMS data for new compounds.", ev(3))]
    unresolved = ["Participant structures are retained as source labels/names; no SMILES has been verified.", "Atmosphere and reaction concentration are not reported."]
    if row in (2, 3, 4):
        notes.append(("Page 5 says the following compounds were prepared similarly to the page-4 typical procedure; exact inheritance of unstated operational details was not normalized.", ev(5)))
        unresolved.append("The extent to which the page-4 typical workup applies to this row is not explicit.")
    if row == 3:
        outcomes += [field("reported_yield_range_4c", "48-60%", ev(5)), field("reported_yield_range_5c", "37-45%", ev(5))]
        unresolved.append("Page 5 reports yield ranges (48-60% and 37-45%) whereas Table 1 lists 48% and 45%; both are retained.")
    if row == 5:
        notes.append(("Page 6 says the monobenzylation procedure was used with an allylic halide instead of benzyl bromide.", ev(6)))
        unresolved.append("The referenced procedure is not restated for this run, and its Table 1 time is 5 h rather than the 6 h used in the benzylation procedure.")
    if row >= 6:
        unresolved += ["Only the Table 1 row was within the required page scope; row-specific charge, solvent, workup, purification, and mass are missing."]
    records.append(record(prefix, f"Table 1 entry {row}", "substrate_scope_entry", e, parts, steps, outcomes, notes, unresolved))

# Scheme 2 is a mechanistic/regioselectivity rationale, not a separate experiment.
e = ev(3)
records.append(record(
    "scheme2_regioselective_lithiation", "Scheme 2", "mechanism", e,
    participants=[participant("scheme2_1d", "reactant", "1d", "1,4-diphenyl-1-butyne", e)],
    notes=[
        ("Scheme 2 depicts favored lithiation at C3 and crosses out lithiation at the benzylic C4 position.", e),
        ("The accompanying prose states that C4 monolithiation was not observed and links the scheme to Table 1 entry 9.", e),
    ],
    unresolved=["The displayed terminal product glyphs are not fully legible; they were not promoted to structured product identities.", "The scheme is a rationale and does not report an independent yield or procedure."],
))

# Prose-only ether control.
e = ev(2)
records.append(record(
    "ether_control_1a", "page 2 ether control", "reported_experiment", e,
    participants=[
        participant("ether_1a", "reactant", "1a", "1-phenyl-1-propyne", e),
        participant("ether_nbuli", "reagent", "n-BuLi", "n-butyllithium", e),
        participant("ether_allyl_bromide", "reagent", None, "allyl bromide", e),
        participant("ether_solvent", "solvent", "ether", "ether (identity not further specified)", e),
    ],
    outcomes=[field("result", "reaction did not occur", e), field("recovered_1a_nmr_yield", {"number": 92, "unit": "%"}, e)],
    notes=[("This is described only as a similar reaction in ether after the discussion of HgCl2-free THF controls.", e)],
    unresolved=["Whether HgCl2 was absent in this ether experiment is not explicit in the sentence.", "Temperature, time, quantities, workup, and NMR internal standard are missing."],
))

# Scheme 3 comparison rows. The catalyst status is deliberately not normalized because the figure and prose conflict.
for suffix, source_id, substrate_label, substrate_name, hours, y4, y5, temp in [
    ("scheme3_1c", "Scheme 3, 1c row", "1c", "1-phenyl-1-hexyne", 5, 0, 0, "25 °C shown in common arrow"),
    ("scheme3_1b", "Scheme 3, 1b row", "1b", "1-phenyl-1-butyne", 5, 0, 0, "25 °C shown in common arrow"),
    ("scheme3_1a", "Scheme 3, 1a row", "1a", "1-phenyl-1-propyne", 6, 11, 13, "-78 °C footnote override for monolithiation"),
]:
    e = ev(2, 4)
    parts = [
        participant(f"{suffix}_substrate", "reactant", substrate_label, substrate_name, e),
        participant(f"{suffix}_nbuli", "reagent", "n-BuLi", "n-butyllithium", e),
        participant(f"{suffix}_allyl_bromide", "reagent", None, "allyl bromide", e),
    ]
    if y4 or y5:
        parts += [participant(f"{suffix}_product4", "product", "4", "alkyne product family 4", e), participant(f"{suffix}_product5", "product", "5", "allene product family 5", e)]
    records.append(record(
        suffix, source_id, "optimization_entry", e, parts,
        [step("monoallylation_control", [p["entity_id"] for p in parts], [field("temperature", temp, ev(4)), field("reaction_time", {"number": hours, "unit": "h"}, ev(4)), field("HgCl2_status", None)])],
        [field("yield_product_4", {"number": y4, "unit": "%"}, ev(4)), field("yield_product_5", {"number": y5, "unit": "%"}, ev(4)),
         field("result", "no products 4 or 5 reported" if y4 == 0 and y5 == 0 else "low-yield products 4 and 5 reported", ev(4))],
        notes=[
            ("The Scheme 3 arrow visually prints '1.5 mol% HgCl2'.", ev(4)),
            ("The page-2 prose explicitly describes Scheme 3 as monoallylation in the absence of HgCl2.", ev(2)),
        ],
        unresolved=["Source conflict: Scheme 3 visually lists 1.5 mol% HgCl2, while the accompanying prose says HgCl2 is absent; catalyst status remains null.", "Charges, solvent volume, workup, purification, and yield basis are missing."],
    ))

# Scheme 4 first arrow: cited preparation of the organomercury reagent.
e = ev(3, 4)
records.append(record(
    "scheme4_mercury_reagent_preparation", "Scheme 4, first arrow", "literature_example", e,
    participants=[
        participant("scheme4_propargyl_bromide", "reactant", None, "3-phenyl-3-propargyl bromide (source wording)", e),
        participant("scheme4_hg", "reagent", "Hg", "mercury", e),
        participant("scheme4_mercury_reagent", "product", None, "phenyl-propargyl mercury bromide (source nomenclature varies)", e),
    ],
    steps=[step("sunlight_mediated_preparation", ["scheme4_propargyl_bromide", "scheme4_hg", "scheme4_mercury_reagent"], [field("irradiation", "sunlight", ev(4)), field("time", None), field("temperature", None)])],
    notes=[("The Materials paragraph says this reagent was prepared by a published procedure (Ref. 9).", ev(4))],
    unresolved=["No charge, solvent, time, temperature, workup, purification, or yield is stated locally.", "The source uses inconsistent nomenclature for the organomercury compound; structure remains unverified."],
))

# Scheme 4 second arrow: current no-coupling control.
e = ev(3, 4)
records.append(record(
    "scheme4_allyl_bromide_control", "Scheme 4, second arrow", "reported_experiment", e,
    participants=[
        participant("scheme4_control_mercury", "reactant", None, "phenyl-propargyl mercury bromide", e),
        participant("scheme4_control_allyl_bromide", "reagent", None, "allyl bromide", e),
        participant("scheme4_control_thf", "solvent", "THF", "tetrahydrofuran", e),
    ],
    steps=[step("coupling_attempt", ["scheme4_control_mercury", "scheme4_control_allyl_bromide", "scheme4_control_thf"], [field("temperature", "room temperature", ev(4)), field("reaction_time", {"number": 10, "unit": "h"}, ev(4))])],
    outcomes=[field("cross_coupling_products_4a_and_5a", "not detected", ev(3)), field("recovered_organomercury_yield", {"number": 90, "unit": "%"}, ev(3))],
    notes=[("The control was used to argue against coupling via a propargylic mercury-halide intermediate.", ev(3))],
    unresolved=["Reactant charges, workup, purification, and recovery-yield measurement basis are not stated within pages 1-6.", "A detailed procedure may occur outside the required page scope and was not claimed as covered."],
))

# Materials paragraph: four explicitly cited preparations, kept as literature examples.
e = ev(4)
for suffix, source_id, product_label, product_name, alkyl_halide, yield_value in [
    ("materials_1a", "Materials: 1a preparation", "1a", "1-phenyl-1-propyne", "MeI", 90),
    ("materials_1b", "Materials: 1b preparation", "1b", "1-phenyl-1-butyne", "EtI", 81),
]:
    records.append(record(
        suffix, source_id, "literature_example", e,
        participants=[
            participant(f"{suffix}_alkyl_halide", "reagent", alkyl_halide, "methyl iodide" if alkyl_halide == "MeI" else "ethyl iodide", e),
            participant(f"{suffix}_hmpa", "reagent", "HMPA", "hexamethylphosphoramide", e),
            participant(f"{suffix}_product", "product", product_label, product_name, e),
        ],
        steps=[step("published_preparation", [f"{suffix}_alkyl_halide", f"{suffix}_hmpa", f"{suffix}_product"], [field("temperature", "room temperature", e), field("time", None)])],
        outcomes=[field("reported_yield", {"number": yield_value, "unit": "%"}, e)],
        notes=[("The material was prepared according to published procedures (Refs. 5 and 10); the local paragraph only states alkyl-halide/HMPA addition and room-temperature operation.", e)],
        unresolved=["Starting reactant identity, quantities, time, solvent, workup, purification, and yield basis are not explicitly stated in the local paragraph."],
    ))

for suffix, source_id, product_name, yield_value in [
    ("materials_dichloro_propene", "Materials: 2,3-dichloro-1-propene preparation", "2,3-dichloro-1-propene", 70),
    ("materials_dibromo_propene", "Materials: 2,3-dibromo-1-propene preparation", "2,3-dibromo-1-propene", 49),
]:
    records.append(record(
        suffix, source_id, "literature_example", e,
        participants=[participant(f"{suffix}_product", "product", None, product_name, e)],
        outcomes=[field("reported_yield", {"number": yield_value, "unit": "%"}, e)],
        notes=[("The material was prepared according to a published procedure (Ref. 13), and its 1H NMR data were said to match cited references.", e)],
        unresolved=["Reactants, quantities, conditions, workup, purification, and yield basis are not stated locally."],
    ))


records_path = OUT / "records_pages_0001_0006.json"
records_path.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")

coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1,
            "state": "attempted",
            "regions": [
                {"region": "title, abstract, and introductory prose", "finding": "Article scope and prior organolithium background; no current-paper run is instantiated here.", "evidence_ids": ev(1)},
                {"region": "Equation (1), lower half", "finding": "One benzylation arrow attributed in prose to earlier Ref. 5 work; classified as literature_example.", "evidence_ids": ev(1)},
            ],
            "record_ids": [f"{DOC}:intro_eq1_prior_benzylation"],
            "unresolved": ["Eq. (1) gives no yield or complete procedure.", "The source filename says 2010, while the rendered article identifies Vol. 17 (1999); this bibliographic mismatch is not normalized."],
        },
        {
            "page": 2,
            "state": "attempted",
            "regions": [
                {"region": "Scheme 1 and two-row condition table", "finding": "Two independent benzylation conditions: -78 °C/10 h gives 0%/0%; 25 °C/5 h gives 67% 2b and 22% 3b.", "evidence_ids": ev(2)},
                {"region": "Equation (2)", "finding": "1c benzylation gives 2c (42%) and allene 3c (39%).", "evidence_ids": ev(2)},
                {"region": "lower discussion paragraph", "finding": "Links Table 1/Schemes 2-3; reports an ether no-reaction control with 92% NMR recovery of 1a.", "evidence_ids": ev(2)},
            ],
            "record_ids": [f"{DOC}:scheme1_minus78", f"{DOC}:scheme1_25c", f"{DOC}:eq2_1c_benzylation", f"{DOC}:ether_control_1a"] + [f"{DOC}:scheme3_{x}" for x in ("1c", "1b", "1a")],
            "unresolved": ["The prose describes Scheme 3 as HgCl2-free, conflicting with the visual reagent line on page 4.", "The ether control omits detailed conditions."],
        },
        {
            "page": 3,
            "state": "attempted",
            "regions": [
                {"region": "Table 1 including header, nine rows, and footnotes", "finding": "Nine independent substrate-scope rows with row-specific allyl halide, time, two product yields, temperature footnote, and isolated-yield footnote.", "evidence_ids": ev(3)},
                {"region": "Scheme 2", "finding": "Regioselective-lithiation rationale; lower benzylic-lithiation pathway is crossed out, so it is classified as mechanism rather than experiment.", "evidence_ids": ev(3)},
                {"region": "control-experiment prose below Scheme 2", "finding": "Phenyl-propargyl mercury bromide plus allyl bromide gave no 4a/5a and 90% recovered organomercury; linked to Scheme 4.", "evidence_ids": ev(3)},
            ],
            "record_ids": [f"{DOC}:table1_entry{i}" for i in range(1, 10)] + [f"{DOC}:scheme2_regioselective_lithiation", f"{DOC}:scheme4_allyl_bromide_control"],
            "unresolved": ["Scheme 2 product-label glyphs are not fully legible and were not encoded as structures.", "Table entries 6-9 lack local detailed procedures within the required page range."],
        },
        {
            "page": 4,
            "state": "attempted",
            "regions": [
                {"region": "Scheme 3 and footnote", "finding": "Three comparison rows: 1c and 1b give 0/0; 1a gives 11% product 4 and 13% product 5, with -78 °C monolithiation footnote.", "evidence_ids": ev(4)},
                {"region": "Scheme 4, two arrows", "finding": "First arrow is a cited sunlight/Hg preparation; second is a 10 h room-temperature THF coupling failure linked to the page-3 control prose.", "evidence_ids": ev(4)},
                {"region": "Experimental—Materials paragraph", "finding": "Four cited starting-material preparations with reported yields plus an incompletely specified organomercury preparation.", "evidence_ids": ev(4)},
                {"region": "Typical monoallylation procedure for 4a/5a", "finding": "Detailed charges, staged temperature/time, workup, purification, masses, and yields; merged into Table 1 entry 1.", "evidence_ids": ev(4)},
            ],
            "record_ids": [f"{DOC}:scheme3_{x}" for x in ("1c", "1b", "1a")] + [f"{DOC}:scheme4_mercury_reagent_preparation", f"{DOC}:scheme4_allyl_bromide_control", f"{DOC}:materials_1a", f"{DOC}:materials_1b", f"{DOC}:materials_dichloro_propene", f"{DOC}:materials_dibromo_propene", f"{DOC}:table1_entry1"],
            "unresolved": ["Scheme 3 catalyst status conflicts with page-2 prose.", "Cited Materials preparations omit most experimental detail.", "The 4a/5a characterization continues onto page 5."],
        },
        {
            "page": 5,
            "state": "attempted",
            "regions": [
                {"region": "top continuation: 4a/5a characterization", "finding": "Characterization continues the page-4/Table 1 entry-1 experiment; not counted as a new reaction.", "evidence_ids": ev(5)},
                {"region": "preparations (b)-(d)", "finding": "Detailed charges, masses, and yields for Table 1 entries 2-4; merged with their table rows.", "evidence_ids": ev(5)},
                {"region": "preparation (c), 4c/5c", "finding": "Page text gives yield ranges 48-60% and 37-45%, unlike the single Table 1 values; both presentations retained.", "evidence_ids": ev(5)},
                {"region": "bottom monobenzylation heading", "finding": "Names products 2b and 3b; procedure continues on page 6 and is merged with Scheme 1's 25 °C row.", "evidence_ids": ev(5)},
            ],
            "record_ids": [f"{DOC}:table1_entry{i}" for i in range(1, 5)] + [f"{DOC}:scheme1_25c"],
            "unresolved": ["The phrase 'prepared similarly' does not restate all operational details for entries 2-4.", "The 4c/5c yield-range versus table-value discrepancy is unresolved."],
        },
        {
            "page": 6,
            "state": "attempted",
            "regions": [
                {"region": "typical monobenzylation procedure for 2b/3b", "finding": "Detailed charges, staged operation, workup, purification, masses, and yields merged into Scheme 1's 25 °C row.", "evidence_ids": ev(6)},
                {"region": "preparation (b), 2c/3c", "finding": "Charges, masses, and yields merged into Equation (2); procedure is stated only as similar to the preceding one.", "evidence_ids": ev(6)},
                {"region": "monoallylation preparation (a), 4e/5e", "finding": "Charges, masses, and yields merged into Table 1 entry 5.", "evidence_ids": ev(6)},
                {"region": "bottom heading for preparation (b), 4f/5f", "finding": "Only the next compound heading is visible; substantive preparation details continue beyond page 6 and are not claimed as covered.", "evidence_ids": ev(6)},
            ],
            "record_ids": [f"{DOC}:scheme1_25c", f"{DOC}:eq2_1c_benzylation", f"{DOC}:table1_entry5"],
            "unresolved": ["Scheme 1 lists 5 h, but the typical procedure states 6 h after benzyl bromide addition.", "The 2c/3c paragraph does not restate the complete procedure.", "The 4f/5f detailed preparation lies outside the required page range."],
        },
    ],
}
(OUT.parent / "coverage" / "pages_0001_0006.json").parent.mkdir(parents=True, exist_ok=True)
(OUT.parent / "coverage" / "pages_0001_0006.json").write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"records": len(records), "records_path": str(records_path), "coverage_pages": [p["page"] for p in coverage["pages"]]}, ensure_ascii=False))
