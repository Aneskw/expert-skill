import json
from pathlib import Path


BASE = Path(__file__).resolve().parents[1]
DOC = "doc_d5f73b0e7de4203e"


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


def participant(entity_id, role, label, evidence, name=None, smiles=None, amounts=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence) if name is not None else fact(None, []),
        "smiles": fact(smiles, evidence) if smiles is not None else fact(None, []),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": amounts or [],
    }


def record(suffix, kind, evidence, participants=None, steps=None, outcomes=None,
           notes=None, unresolved=None):
    return {
        "record_id": f"{DOC}:{suffix}",
        "document_id": DOC,
        "source_reaction_id": suffix,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": list(dict.fromkeys(evidence)),
        "participants": participants or [],
        "steps": steps or [],
        "outcomes": outcomes or [],
        "notes": [fact(x, evidence) for x in (notes or [])],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved or [],
        },
    }


def step(step_id, participant_ids, conditions):
    return {"step_id": step_id, "participant_ids": participant_ids, "conditions": conditions}


def q(number, unit, raw_text=None, qualifier=None):
    value = {"number": number, "unit": unit}
    if raw_text is not None:
        value["raw_text"] = raw_text
    if qualifier is not None:
        value["qualifier"] = qualifier
    return value


records = []

# Page-2 prior-work and generic arrows. These are deliberately not present-paper experiments.
records.append(record(
    "scheme1_rh_bisallene_prior_work", "literature_example", ev(2),
    participants=[
        participant("bisallene", "reactant", "generic 1,5-bisallene", ev(2)),
        participant("rh_cat", "catalyst", "trans-RhCl(CO)(PPh3)2", ev(2),
                    amounts=[field("catalyst_loading", q(5, "mol%"), ev(2))]),
        participant("toluene", "solvent", "toluene", ev(2), smiles="Cc1ccccc1"),
        participant("diene14", "product", "1,4-diene cyclization product", ev(2)),
    ],
    steps=[step("cyclometallation_and_reductive_elimination",
                ["bisallene", "rh_cat", "toluene", "diene14"],
                [field("temperature", "reflux", ev(2))])],
    notes=["Scheme 1 upper pathway summarizes cited prior work (reference 2)."],
    unresolved=["Generic X-substituted structures and reaction duration are not specified on this page."]
))
records.append(record(
    "scheme1_pd_bisallene_prior_work", "literature_example", ev(2),
    participants=[
        participant("bisallene", "reactant", "generic 1,5-bisallene", ev(2)),
        participant("pdcat", "catalyst", "Pd(PPh3)4", ev(2),
                    amounts=[field("catalyst_loading", q(5, "mol%"), ev(2))]),
        participant("k2co3", "reagent", "K2CO3", ev(2),
                    amounts=[field("equivalents", q(4, "equiv"), ev(2))]),
        participant("tbai", "reagent", "n-Bu4NI", ev(2),
                    amounts=[field("equivalents", q(2, "equiv"), ev(2))]),
        participant("toluene", "solvent", "toluene", ev(2), smiles="Cc1ccccc1"),
        participant("diene15", "product", "1,5-diene cyclization product", ev(2)),
    ],
    steps=[step("cyclometallation_and_reductive_elimination",
                ["bisallene", "pdcat", "k2co3", "tbai", "toluene", "diene15"], [])],
    notes=["Scheme 1 lower pathway summarizes cited prior work (reference 3)."],
    unresolved=["Generic X-substituted structures, temperature, and duration are not specified on this page."]
))
records.append(record(
    "scheme2_allenyne_cyclometallation_prior_work", "literature_example", ev(2),
    participants=[
        participant("allenyne", "reactant", "generic 1,5-allenyne", ev(2)),
        participant("metal", "unspecified_agent", "M", ev(2)),
        participant("metallacycle", "unspecified_agent", "generic 1,3-diene metallacyclic intermediate", ev(2)),
        participant("unknown_product", "product", "?", ev(2)),
    ],
    notes=["Scheme 2 is a generic cyclometallation concept associated with cited allene-yne precedent, not a present-paper experiment."],
    unresolved=["Metal identity, final product, conditions, and complete structures are intentionally unspecified in the source."]
))

scheme3_rows = [
    ("ph", "Ph", 4, q(87, "%")),
    ("tms", "TMS", 8, q(77, "%")),
    ("npr", "n-Pr", 8, "complicated"),
]
for key, substituent, hours, result in scheme3_rows:
    evidence = ev(2)
    parts = [
        participant("substrate", "reactant", f"4-aryl-2,3-dienoate bearing internal alkyne R={substituent}", evidence),
        participant("rhcat", "catalyst", "trans-RhCl(CO)(PPh3)2", evidence,
                    amounts=[field("catalyst_loading", q(5, "mol%"), evidence)]),
        participant("toluene", "solvent", "toluene", evidence, smiles="Cc1ccccc1"),
        participant("product", "product", "intramolecular [2+2]-cycloaddition product" if key != "npr" else "product mixture not resolved", evidence),
    ]
    outcomes = ([field("reported_yield", result, evidence, ["product"]),
                 field("yield_measurement_basis", None, evidence, ["product"])]
                if isinstance(result, dict) else [field("reaction_result", result, evidence, ["product"])])
    records.append(record(
        f"scheme3_internal_alkyne_{key}_prior_work", "literature_example", evidence,
        participants=parts,
        steps=[step("rh_catalyzed_reaction", [p["entity_id"] for p in parts],
                    [field("temperature", "reflux", evidence), field("time", q(hours, "h"), evidence)])],
        outcomes=outcomes,
        notes=["Scheme 3 is tied to cited prior publication 9; it is retained as a literature example rather than a present-paper experiment."],
        unresolved=["Complete substrate/product connectivity and the yield measurement basis are not specified here."]
    ))

# Thermal control on 1f.
records.append(record(
    "equation1_thermal_control_1f", "reported_experiment", ev(2),
    participants=[
        participant("s1f", "reactant", "1f", ev(2)),
        participant("toluene", "solvent", "toluene", ev(2), smiles="Cc1ccccc1"),
        participant("p3f", "product", "3f", ev(2),
                    name="(Z)-3-benzyl-5-benzylidene-4-(prop-1-en-2-yl)-5,6-dihydropyran-2-one"),
    ],
    steps=[step("thermal_ene_cyclization", ["s1f", "toluene", "p3f"],
                [field("temperature", "reflux", ev(2)), field("time", q(24, "h"), ev(2))])],
    outcomes=[
        field("isolated_yield", q(18, "%"), ev(2), ["p3f"]),
        field("recovered_starting_material_yield", q(67, "%"), ev(2), ["s1f"]),
        field("yield_measurement_basis", "isolated", ev(2), ["p3f"]),
    ],
    unresolved=["Substrate/product SMILES and exact reflux temperature, scale, atmosphere, workup, and purification are not reported on page 2."]
))


def catalyst(evidence, mass_mg=None):
    amounts = [field("catalyst_loading", q(5, "mol%"), evidence)]
    if mass_mg is not None:
        amounts += [field("mass", q(mass_mg, "mg"), evidence), field("amount", q(0.0125, "mmol"), evidence)]
    return participant("rhcat", "catalyst", "trans-RhCl(CO)(PPh3)2", evidence, amounts=amounts)


def dimer_scope(suffix, substrate, ar, r_group, hours, y_major, y_epi, extra_evidence=(), catalyst_mass=8):
    evidence = list(dict.fromkeys(ev(3) + list(extra_evidence)))
    p_major = f"p2_{substrate}"
    p_epi = f"pepi2_{substrate}"
    parts = [
        participant("substrate", "reactant", substrate, evidence,
                    name=f"propargyl 2,3-dienoate {substrate}; Ar={ar}, R={r_group}",
                    amounts=[field("amount", q(0.25, "mmol"), evidence)]),
        catalyst(evidence, catalyst_mass),
        participant("xylene", "solvent", "dry xylene", evidence,
                    amounts=[field("volume", q(6, "mL"), evidence)]),
        participant(p_major, "product", substrate.replace("1", "2", 1), evidence),
        participant(p_epi, "product", "epi-" + substrate.replace("1", "2", 1), evidence),
    ]
    return record(
        suffix, "substrate_scope_entry", evidence,
        participants=parts,
        steps=[step("dimeric_cyclization", [p["entity_id"] for p in parts], [
            field("temperature", q(140, "°C"), evidence),
            field("time", q(hours, "h"), evidence),
            field("concentration", q(0.042, "M"), ev(3)),
            field("operation", "heated in a Schlenk tube with a screw cap", evidence),
            field("operation", "monitored by TLC (petroleum ether/ethyl acetate 3:1)", extra_evidence or evidence),
            field("workup", "rotary evaporation", extra_evidence or evidence),
            field("purification", "flash chromatography on silica gel (petroleum ether/ethyl acetate 5:1)", extra_evidence or evidence),
        ])],
        outcomes=[
            field("isolated_yield_major", q(y_major, "%"), ev(3), [p_major]),
            field("isolated_yield_epi", q(y_epi, "%"), ev(3), [p_epi]),
            field("yield_measurement_basis", "isolated", ev(3), [p_major, p_epi]),
        ],
        notes=["Major product is described as more polar and epi product as less polar in General Procedure II."],
        unresolved=["Complex product structures and stereochemistry remain unverified; atmosphere is not reported."]
    )


# Table 1 entries 1 and 3 remain independent optimization conditions.
for entry, concentration, y_major, y_epi in [(1, 0.0833, 30, 18), (3, 0.0278, 38, 22)]:
    evidence = ev(3)
    parts = [
        participant("s1b", "reactant", "1b", evidence,
                    name="propargyl 2-ethyl-4-phenylbuta-2,3-dienoate"),
        catalyst(evidence),
        participant("xylene", "solvent", "xylene", evidence),
        participant("p2b", "product", "2b", evidence),
        participant("pepi2b", "product", "epi-2b", evidence),
    ]
    records.append(record(
        f"table1_entry{entry}", "optimization_entry", evidence,
        participants=parts,
        steps=[step("dimeric_cyclization", [p["entity_id"] for p in parts], [
            field("temperature", q(140, "°C"), evidence),
            field("concentration", q(concentration, "M"), evidence),
            field("operation", "heated in a Schlenk tube with a screw cap", evidence),
        ])],
        outcomes=[
            field("isolated_yield_2b", q(y_major, "%"), evidence, ["p2b"]),
            field("isolated_yield_epi_2b", q(y_epi, "%"), evidence, ["pepi2b"]),
            field("yield_measurement_basis", "isolated", evidence, ["p2b", "pepi2b"]),
        ],
        unresolved=["Time, substrate scale, solvent volume, atmosphere, workup, purification, and complex structures are not reported for this concentration row."]
    ))

# Five Table 2 rows; entry 2 also represents Table 1 entry 2 and is not duplicated.
records.append(dimer_scope("table2_entry1_1a", "1a", "Ph", "Bn", 10, 27, 13, ev(1) + ev(6), catalyst_mass=9))
records.append(dimer_scope("table2_entry2_1b_merged_table1_entry2", "1b", "Ph", "Et", 12, 52, 23, ev(6)))
records[-1]["notes"].append(fact("This is the same 0.0417 M, 52%/23% condition as Table 1 entry 2; Table 2 rounds the concentration to 0.042 M.", ev(3)))
records.append(dimer_scope("table2_entry3_1c", "1c", "Ph", "n-Pr", 10, 45, 21, ev(6)))
records.append(dimer_scope("table2_entry4_1d", "1d", "Ph", "i-Bu", 10, 38, 28, ev(6)))
records.append(dimer_scope("table2_entry5_1e", "1e", "p-MeOC6H4", "n-Bu", 10, 45, 25, ev(6)))

# Add the exact page-6 quantities to the 1a scope record.
row_1a = next(r for r in records if r["record_id"].endswith("table2_entry1_1a"))
row_1a["participants"][0]["amounts"] = [
    field("mass", q(70, "mg"), ev(6)), field("amount", q(0.25, "mmol"), ev(6))
]
row_1a["participants"][0]["name"] = fact("prop-2-ynyl 2-benzyl-4-phenylbuta-2,3-dienoate", ev(6))
row_1a["participants"][0]["smiles"] = fact("C#CCOC(=O)C(Cc1ccccc1)=C=Cc1ccccc1", ev(6))
row_1a["review"]["unresolved"].append("The compound-specific preparation continues onto PDF page 7; this session retains only page-6 quantities and Table-2 outcomes.")


# Table 3 substrate scope.
table3 = [
    (1, "1f", "3f", "R1=H, R2=H, R3=Me, R4=Bn, R5=Ph", 15, 67),
    (2, "1g", "3g", "R1/R2=-(CH2)5-, R3=H, R4=H, R5=TMS", 8, 78),
    (3, "1h", "3h", "R1=H, R2=H, R3=Me, R4=Bn, R5=TMS", 34, 66),
    (4, "1i", "3i", "R1=H, R2=H, R3=Me, R4=Bn, R5=n-Bu", 48, 84),
    (5, "1j", "3j", "R1/R2=-(CH2)5-, R3=H, R4=H, R5=n-Bu", 27, 63),
    (6, "1k", "3k", "R1=H, R2=H, R3=Me, R4=Me, R5=n-Bu", 34, 58),
    (7, "1l", "3l", "R1=H, R2=H, R3=Me, R4=Me, R5=H", 17, 75),
    (8, "1m", "3m", "R1=H, R2=H, R3=Me, R4=Me, R5=TMS", 24, 53),
    (9, "1n", "3n", "R1=H, R2=H, R3=Me, R4=H, R5=Ph", 14, 63),
]
for entry, sub, prod, subs, hours, yld in table3:
    evidence = ev(3)
    parts = [
        participant("substrate", "reactant", sub, evidence, name=f"propargylic 2,3-alkadienoate {sub}; {subs}"),
        catalyst(evidence),
        participant("toluene", "solvent", "toluene", evidence, smiles="Cc1ccccc1"),
        participant("product", "product", prod, evidence,
                    name=("(Z)-3-benzyl-5-benzylidene-4-(prop-1-en-2-yl)-5,6-dihydropyran-2-one" if prod == "3f" else f"Z-configured lactone {prod}; {subs}")),
    ]
    records.append(record(
        f"table3_entry{entry}_{sub}", "substrate_scope_entry", evidence,
        participants=parts,
        steps=[step("unimolecular_cyclization", [p["entity_id"] for p in parts], [
            field("temperature", "reflux", evidence), field("time", q(hours, "h"), evidence)
        ])],
        outcomes=[field("isolated_yield", q(yld, "%"), evidence, ["product"]),
                  field("yield_measurement_basis", "isolated", evidence, ["product"])],
        notes=["The source states that the exocyclic C=C bond in products 3 is Z-configured."],
        unresolved=["Exact reflux temperature, scale, solvent volume, atmosphere, workup, purification, and complex structures are not reported on page 3."]
    ))

records.append(record(
    "equation2_1o_to_3o", "reported_experiment", ev(3),
    participants=[
        participant("s1o", "reactant", "1o", ev(3), name="propargylic 2,3-dienoate bearing phenyl and methyl at the allene 4-position"),
        catalyst(ev(3)),
        participant("toluene", "solvent", "toluene", ev(3), smiles="Cc1ccccc1"),
        participant("p3o", "product", "3o", ev(3), name="5-methylene-4-(1-phenylvinyl)-5,6-dihydropyran-2-one"),
    ],
    steps=[step("unimolecular_cyclization", ["s1o", "rhcat", "toluene", "p3o"],
                [field("temperature", "reflux", ev(3)), field("time", q(12, "h"), ev(3))])],
    outcomes=[field("reported_yield", q(50, "%"), ev(3), ["p3o"]),
              field("yield_measurement_basis", None, ev(3), ["p3o"])],
    unresolved=["Scale, atmosphere, workup, purification, yield basis, and structures remain unverified."]
))

scheme4_evidence = ev(3) + ev(4)
records.append(record(
    "scheme4_1p_trapping_with_3_methoxyprop_1_yne", "reported_experiment", scheme4_evidence,
    participants=[
        participant("s1p", "reactant", "1p", scheme4_evidence, name="propargyl 2-propyl-4-(p-bromophenyl)buta-2,3-dienoate"),
        participant("trap", "reactant", "3-methoxyprop-1-yne", scheme4_evidence, smiles="C#CCOC"),
        catalyst(scheme4_evidence),
        participant("toluene", "solvent", "toluene", scheme4_evidence, smiles="Cc1ccccc1"),
        participant("p4p", "product", "4p", scheme4_evidence, name="5-(4-bromophenyl)-6-(methoxymethyl)-4-propylisochroman-3-one"),
    ],
    steps=[step("cyclization_trapping_aromatization", ["s1p", "trap", "rhcat", "toluene", "p4p"], [
        field("temperature", "reflux", ev(4)), field("time", q(12, "h"), ev(4))
    ])],
    outcomes=[field("reported_yield", q(50, "%"), scheme4_evidence, ["p4p"]),
              field("yield_measurement_basis", None, scheme4_evidence, ["p4p"])],
    notes=["Intermediates 5 and 6 and the aromatization arrow in Scheme 4 are proposed mechanistic steps, not separately executed experiments; product 4p was confirmed by X-ray diffraction."],
    unresolved=["Scale, exact reflux temperature, trap stoichiometry, atmosphere, workup, purification, yield basis, and structures remain unverified within pages 1-6."]
))

records.append(record(
    "scheme5_proposed_mono_dimeric_mechanism", "mechanism", ev(4) + ev(6),
    participants=[
        participant("m1", "unspecified_agent", "propargylic 2,3-alkadienoate 1", ev(6)),
        participant("m7", "unspecified_agent", "rhodacyclic intermediate 7", ev(6)),
        participant("m10", "unspecified_agent", "rhodium hydride intermediate 10", ev(6)),
        participant("m3", "product", "monomeric lactone 3", ev(6)),
        participant("m8a", "unspecified_agent", "metallabicycle 8a", ev(6)),
        participant("m8b", "unspecified_agent", "metallabicycle 8b", ev(6)),
        participant("m9", "unspecified_agent", "dimeric precursor 9", ev(6)),
        participant("m2", "product", "polycyclic product 2", ev(6)),
        participant("mepi2", "product", "epi-2", ev(6)),
    ],
    notes=[
        "Proposed cyclometallation gives 7; beta-hydride elimination/reductive elimination gives 3 when beta-H is available.",
        "For aryl substitution without an available beta-H, intermolecular carbometallation gives 8a/8b, reductive elimination gives 9, and intramolecular Diels-Alder affords 2/epi-2.",
    ],
    unresolved=["This is a proposed mechanism; generic R-group structures and organorhodium intermediates are not independently verified."]
))

# Synthetic applications explicitly supported on pages 5-6.
records.append(record(
    "scheme6_dibal_reduction_3f_to_11f", "reported_experiment", ev(5) + ev(6),
    participants=[
        participant("s3f", "reactant", "3f", ev(5) + ev(6)),
        participant("dibal", "reagent", "DIBAL-H", ev(5) + ev(6)),
        participant("p11f", "product", "11f", ev(5) + ev(6), name="hemiacetal reduction product 11f"),
    ],
    steps=[step("carbonyl_reduction", ["s3f", "dibal", "p11f"], [])],
    outcomes=[field("reported_yield", "quantitative", ev(6), ["p11f"]),
              field("yield_measurement_basis", None, ev(5) + ev(6), ["p11f"])],
    unresolved=["Pages 5-6 omit reagent amount, solvent, temperature, time, atmosphere, workup, purification, yield basis, and verified structures."]
))
records.append(record(
    "scheme6_hydrogenation_3f_to_12f", "reported_experiment", ev(5) + ev(6),
    participants=[
        participant("s3f", "reactant", "3f", ev(5) + ev(6)),
        participant("pdc", "catalyst", "Pd/C", ev(5) + ev(6)),
        participant("h2", "reagent", "H2", ev(5) + ev(6), smiles="[H][H]"),
        participant("p12f", "product", "12f", ev(5) + ev(6), name="3,5-dibenzyl-4-isopropyl-5,6-dihydropyran-2-one"),
    ],
    steps=[step("selective_hydrogenation", ["s3f", "pdc", "h2", "p12f"], [])],
    outcomes=[field("reported_yield", q(88, "%"), ev(6), ["p12f"]),
              field("yield_measurement_basis", None, ev(5) + ev(6), ["p12f"])],
    notes=["Page 5 describes hydrogenation of the vinylic and exocyclic C=C bonds with high regioselectivity."],
    unresolved=["Pages 5-6 omit reagent/catalyst amounts, solvent, temperature, time, atmosphere, workup, purification, yield basis, and verified structures."]
))
records.append(record(
    "page5_nis_iodination_to_13m", "reported_experiment", ev(5),
    participants=[
        participant("silane", "reactant", "3l as printed in page-5 prose (vinylic silane context)", ev(5)),
        participant("nis", "reagent", "NIS", ev(5), name="N-iodosuccinimide", smiles="O=C1CCC(=O)N1I"),
        participant("p13m", "product", "13m", ev(5), name="vinylic iodide 13m"),
    ],
    steps=[step("iodination", ["silane", "nis", "p13m"], [])],
    outcomes=[field("reported_yield", q(88, "%"), ev(5), ["p13m"]),
              field("yield_measurement_basis", None, ev(5), ["p13m"])],
    notes=["The page-5 prose states that the vinylic silane was treated with NIS; detailed Scheme 7 and procedures lie beyond the claimed page range."],
    unresolved=["The page-5 label appears as 3l although Table 3 identifies the TMS substrate/product as 3m; the source identity conflict is retained. Conditions, yield basis, and structures are unverified."]
))

# Exact preparation of 1a, merged with General Procedure I.
prep_ev = ev(6)
records.append(record(
    "preparation_1a", "reported_experiment", prep_ev,
    participants=[
        participant("acid", "reactant", "2-benzyl-4-phenylbuta-2,3-dienoic acid", prep_ev,
                    smiles="O=C(O)C(Cc1ccccc1)=C=Cc1ccccc1",
                    amounts=[field("mass", q(1.003, "g"), prep_ev), field("amount", q(4, "mmol"), prep_ev)]),
        participant("propargyl_bromide", "reactant", "propargyl bromide", prep_ev, smiles="C#CCBr",
                    amounts=[field("mass", q(1.6, "g"), prep_ev), field("amount", q(13, "mmol"), prep_ev)]),
        participant("k2co3", "reagent", "K2CO3", prep_ev, smiles="[K+].[K+].[O-]C([O-])=O",
                    amounts=[field("mass", q(704, "mg"), prep_ev), field("amount", q(5, "mmol"), prep_ev)]),
        participant("acetone", "solvent", "acetone", prep_ev, smiles="CC(=O)C",
                    amounts=[field("volume", q(40, "mL"), prep_ev)]),
        participant("p1a", "product", "1a", prep_ev, name="prop-2-ynyl 2-benzyl-4-phenylbuta-2,3-dienoate",
                    smiles="C#CCOC(=O)C(Cc1ccccc1)=C=Cc1ccccc1",
                    amounts=[field("mass", q(859, "mg"), prep_ev)]),
    ],
    steps=[step("esterification", ["acid", "propargyl_bromide", "k2co3", "acetone", "p1a"], [
        field("temperature", "room temperature", prep_ev),
        field("time", q(12, "h"), prep_ev),
        field("operation", "stirred; completion monitored by TLC (petroleum ether/ethyl acetate 10:1)", prep_ev),
        field("workup", "filtration and rotary evaporation", prep_ev),
        field("purification", "flash chromatography on silica gel (petroleum ether/ethyl ether 30:1)", prep_ev),
    ])],
    outcomes=[field("isolated_yield", q(74, "%"), prep_ev, ["p1a"]),
              field("yield_measurement_basis", "isolated", prep_ev, ["p1a"])],
    notes=["General Procedure I is stated for 1a-p; only the compound-specific 1a execution is made into a quantitative record here."],
    unresolved=["Atmosphere is not reported; candidate structures are unverified despite being based on explicit names and the page drawing/text."]
))

# General Procedure II explicitly includes 1p although the pages in scope do not report its duration/yields.
gp2_ev = ev(6)
records.append(record(
    "general_procedure_ii_1p_to_2p_epi2p", "reported_experiment", gp2_ev,
    participants=[
        participant("s1p", "reactant", "1p", gp2_ev,
                    amounts=[field("amount", q(0.25, "mmol"), gp2_ev)]),
        catalyst(gp2_ev, 8),
        participant("xylene", "solvent", "dry xylene", gp2_ev,
                    amounts=[field("volume", q(6, "mL"), gp2_ev)]),
        participant("p2p", "product", "2p", gp2_ev),
        participant("pepi2p", "product", "epi-2p", gp2_ev),
    ],
    steps=[step("dimeric_cyclization", ["s1p", "rhcat", "xylene", "p2p", "pepi2p"], [
        field("temperature", q(140, "°C"), gp2_ev),
        field("operation", "heated in a Schlenk tube with a screw cap until complete by TLC (petroleum ether/ethyl acetate 3:1)", gp2_ev),
        field("workup", "rotary evaporation", gp2_ev),
        field("purification", "flash chromatography on silica gel (petroleum ether/ethyl acetate 5:1)", gp2_ev),
    ])],
    notes=["General Procedure II identifies 2p as more polar and epi-2p as less polar."],
    unresolved=["The pages in scope do not report reaction time, yields, atmosphere, or verified structures for 1p to 2p/epi-2p."]
))


out = BASE / "raw_model" / "records_pages_0001_0006.json"
out.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")

# Exact six-page coverage ledger.
rid = lambda suffix: f"{DOC}:{suffix}"
coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1,
            "state": "attempted",
            "regions": [
                {"region": "title, abstract, introduction, and lower-right Results and Discussion",
                 "finding": "No standalone arrow/table row appears. The qualitative abstract claims were not duplicated; the lower-right 1a cyclization discussion is merged with Table 2 entry 1.",
                 "evidence_ids": ev(1)},
            ],
            "record_ids": [rid("table2_entry1_1a")],
            "unresolved": ["Abstract-level pathway and application summaries were not converted into duplicate experiments."]
        },
        {
            "page": 2,
            "state": "attempted",
            "regions": [
                {"region": "upper-left Schemes 1 and 2", "finding": "Two cited prior-work bisallene pathways and one generic cited allenyne cyclometallation arrow were classified as literature examples.", "evidence_ids": ev(2)},
                {"region": "upper-right Scheme 3", "finding": "Three internal-alkyne cases are tied to cited prior publication 9 and retained as literature examples, including the complicated n-Pr result.", "evidence_ids": ev(2)},
                {"region": "lower-left equation 1", "finding": "Catalyst-free thermal conversion of 1f to 3f was extracted with 18% isolated yield and 67% recovered 1f.", "evidence_ids": ev(2)},
            ],
            "record_ids": [rid(x) for x in [
                "scheme1_rh_bisallene_prior_work", "scheme1_pd_bisallene_prior_work",
                "scheme2_allenyne_cyclometallation_prior_work", "scheme3_internal_alkyne_ph_prior_work",
                "scheme3_internal_alkyne_tms_prior_work", "scheme3_internal_alkyne_npr_prior_work",
                "equation1_thermal_control_1f"]],
            "unresolved": ["Cited prior-work schemes omit complete procedures and contain generic or unresolved structures."]
        },
        {
            "page": 3,
            "state": "attempted",
            "regions": [
                {"region": "upper-right Tables 1 and 2", "finding": "All concentration and dimeric-scope rows were extracted; Table 1 entry 2 was merged with identical Table 2 entry 2.", "evidence_ids": ev(3)},
                {"region": "lower-right Table 3", "finding": "All nine unimolecular cyclization rows were extracted independently with row time and isolated yield.", "evidence_ids": ev(3)},
                {"region": "lower-left equation 2 and bottom-right mechanistic-study prose", "finding": "The 1o-to-3o case and the 1p trapping experiment were extracted; ORTEP Figure 1 was treated as structural evidence, not another reaction.", "evidence_ids": ev(3)},
            ],
            "record_ids": [rid(x) for x in [
                "table1_entry1", "table2_entry2_1b_merged_table1_entry2", "table1_entry3",
                "table2_entry1_1a", "table2_entry3_1c", "table2_entry4_1d", "table2_entry5_1e",
                *[f"table3_entry{i}_{s}" for i, s in enumerate(["1f","1g","1h","1i","1j","1k","1l","1m","1n"], 1)],
                "equation2_1o_to_3o", "scheme4_1p_trapping_with_3_methoxyprop_1_yne"]],
            "unresolved": ["Most complex structures remain unverified; Table 1 non-optimal rows omit duration and scale."]
        },
        {
            "page": 4,
            "state": "attempted",
            "regions": [
                {"region": "left-center Scheme 4", "finding": "The reported 1p/3-methoxyprop-1-yne trapping reaction was extracted once; intermediates 5 and 6 are proposed mechanistic species.", "evidence_ids": ev(4)},
                {"region": "upper ORTEP Figures 2 and 3 and right-column mechanism prose", "finding": "Figures support structures of 3f and 4p but are not reactions; the prose supports the proposed Scheme 5 mechanism record.", "evidence_ids": ev(4)},
            ],
            "record_ids": [rid("scheme4_1p_trapping_with_3_methoxyprop_1_yne"), rid("scheme5_proposed_mono_dimeric_mechanism")],
            "unresolved": ["The trapping experiment's detailed scale and procedure occur beyond the claimed page range; proposed organorhodium structures are unverified."]
        },
        {
            "page": 5,
            "state": "attempted",
            "regions": [
                {"region": "upper Figure 4", "finding": "Natural-product structures are background examples from cited literature; no reaction arrow or present-paper experiment is present in the figure.", "evidence_ids": ev(5)},
                {"region": "lower-column derivatization prose", "finding": "The two 3f derivatizations and the NIS iodination were linked to application records; the unshown Scheme 7 coupling details were not guessed.", "evidence_ids": ev(5)},
            ],
            "record_ids": [rid("scheme6_dibal_reduction_3f_to_11f"), rid("scheme6_hydrogenation_3f_to_12f"), rid("page5_nis_iodination_to_13m")],
            "unresolved": ["Page 5 refers to later Scheme 7 for 14m-16m without assigning full per-product conditions here; those later pages are not claimed as covered.", "The vinylic-silane label appears as 3l although Table 3 identifies TMS-bearing product 3m."]
        },
        {
            "page": 6,
            "state": "attempted",
            "regions": [
                {"region": "upper Scheme 5", "finding": "Generic mono- and dimeric cyclization pathways were classified as a proposed mechanism, not experimental rows.", "evidence_ids": ev(6)},
                {"region": "lower-right Scheme 6", "finding": "DIBAL-H reduction and Pd/C-H2 hydrogenation were extracted as two separate present-paper application experiments.", "evidence_ids": ev(6)},
                {"region": "lower-left Experimental Section and lower-right General Procedure II", "finding": "Exact preparation of 1a was extracted; General Procedure II facts were merged into Table 2 rows and a separate partial 1p-to-2p/epi-2p record.", "evidence_ids": ev(6)},
            ],
            "record_ids": [rid(x) for x in [
                "scheme5_proposed_mono_dimeric_mechanism", "scheme6_dibal_reduction_3f_to_11f",
                "scheme6_hydrogenation_3f_to_12f", "preparation_1a", "general_procedure_ii_1p_to_2p_epi2p",
                "table2_entry1_1a", "table2_entry2_1b_merged_table1_entry2", "table2_entry3_1c",
                "table2_entry4_1d", "table2_entry5_1e"]],
            "unresolved": ["The compound-specific 2a/epi-2a preparation continues onto PDF page 7; no page-7 coverage is claimed.", "General Procedure II does not state atmosphere or numerical duration."]
        },
    ]
}
(BASE / "coverage").mkdir(parents=True, exist_ok=True)
(BASE / "coverage" / "pages_0001_0006.json").write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

# Mark only the six requested page tasks attempted.
tasks_path = BASE / "tasks.json"
tasks = json.loads(tasks_path.read_text())
for task in tasks:
    if task.get("document_id") == DOC and task.get("task_id") in {f"{DOC}:page{i}:text" for i in range(1, 7)}:
        task["state"] = "attempted"
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"records": len(records), "records_file": str(out), "coverage_pages": len(coverage["pages"])}, ensure_ascii=False))
