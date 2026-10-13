#!/usr/bin/env python3
"""Build the machine extraction for doc_7cfc7ed9404aa03d, PDF pages 1-5."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
DOC = "doc_7cfc7ed9404aa03d"


def ev(page):
    return [f"{DOC}:page{page}:image", f"{DOC}:page{page}:text"]


def uniq(values):
    return list(dict.fromkeys(values))


def fact(value, evidence):
    return {
        "value": value,
        "evidence_ids": uniq(evidence) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def qty(number, unit, raw_text=None, **extra):
    value = {"number": number, "unit": unit}
    if raw_text is not None:
        value["raw_text"] = raw_text
    value.update(extra)
    return value


def rng(minimum, maximum, unit, raw_text):
    return {"minimum": minimum, "maximum": maximum, "unit": unit, "raw_text": raw_text}


def field(name, value, evidence, targets=None):
    item = {"name": name, "fact": fact(value, evidence)}
    if targets:
        item["target_entity_ids"] = targets
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


def step(step_id, participant_ids, conditions):
    return {"step_id": step_id, "participant_ids": participant_ids, "conditions": conditions}


def record(suffix, kind, evidence, participants, steps, outcomes, notes=None, unresolved=None):
    evidence = uniq(evidence)
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
        "notes": [fact(value, evidence) for value in (notes or [])],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved or [
                "Supporting Information was mentioned but not supplied or explicitly associated.",
                "Machine-extracted structures and chemical roles require source review.",
            ],
        },
    }


SMILES = {
    "1a": "COC(=O)C(C)=C=Cc1ccccc1",
    "1b": "CCOC(=O)C(C)=C=Cc1ccccc1",
    "2a": "CC(=C=Cc1ccccc1)C(=O)C(F)(F)C(F)(F)C(F)(F)C(F)(F)F",
    "2b": "CC(=C=Cc1ccccc1)C(=O)C(F)(F)C(F)(F)C(F)(F)C(F)(F)C(F)(F)C(F)(F)F",
    "7a": "CC(=C=Cc1ccccc1)C(C)(O)C(F)(F)C(F)(F)C(F)(F)C(F)(F)F",
    "7b": "CC(=C=Cc1ccccc1)C(O)(CCCC)C(F)(F)C(F)(F)C(F)(F)C(F)(F)F",
    "8a": "C=CCc1c(-c2ccccc2)oc(C(F)(F)C(F)(F)C(F)(F)C(F)(F)F)c1C",
    "8b": "Cc1cc(-c2ccccc2)oc1C(F)(F)C(F)(F)C(F)(F)C(F)(F)F",
}


records = []

# Scheme 1 contains two cited prior-work arrows and one generic arrow for this work.
e1 = ev(1)
generic_allenoate = participant("allenoate_generic", "reactant", "generic 2,3-allenoate", e1)
records.append(record(
    "scheme1_prior_fe_grignard", "literature_example", e1,
    [generic_allenoate,
     participant("r4mgbr", "reagent", "R4MgBr", e1),
     participant("fe_catalyst", "catalyst", "Fe(acac)3 or FeCl3·6H2O", e1),
     participant("alkenoate_generic", "product", "3-(Z)-alkenoate generic product", e1)],
    [step("cited_transformation", ["allenoate_generic", "r4mgbr", "fe_catalyst", "alkenoate_generic"], [])], [],
    notes=["Scheme 1 identifies this arrow as cited prior work, not a new batch in this paper."],
    unresolved=["Generic R groups prevent a complete structure assignment; no batch quantities are shown."]
))
records.append(record(
    "scheme1_prior_allylmagnesium", "literature_example", e1,
    [generic_allenoate,
     participant("allylmagnesium_chloride", "reagent", "allylmagnesium chloride", e1, name="allylmagnesium chloride"),
     participant("allenol_generic", "product", "tertiary 2,3-allenol generic product", e1)],
    [step("cited_transformation", ["allenoate_generic", "allylmagnesium_chloride", "allenol_generic"], [])], [],
    notes=["Scheme 1 and the introduction classify this as cited prior work."],
    unresolved=["Generic R groups prevent a complete structure assignment; no batch quantities are shown."]
))
records.append(record(
    "scheme1_general_perfluoroalkylation", "general_scheme", e1,
    [generic_allenoate,
     participant("rfmgx", "reagent", "RfMgX", e1),
     participant("allenyl_rf_ketone", "product", "generic allenyl perfluoroalkyl ketone", e1)],
    [step("generic_transformation", ["allenoate_generic", "rfmgx", "allenyl_rf_ketone"], [])], [],
    notes=["The lower Scheme 1 arrow is a generic summary of this work; individual batches are recorded from Tables 1-2 and Equation 1."],
    unresolved=["Generic R groups and Rf prevent a complete structure assignment; no row-specific quantities are shown."]
))


def table1_record(entry, substrate, ester_r, equivalents, hours, product_yield, recovery):
    page_evidence = ev(2)
    if entry in (1, 2, 3, 7, 8):
        page_evidence = uniq(ev(1) + page_evidence)
    substrate_name = f"{substrate}, 2-methyl-4-phenyl-2,3-butadienoate (R={ester_r})"
    parts = [
        participant("substrate", "reactant", substrate, page_evidence, name=substrate_name, smiles=SMILES.get(substrate)),
        participant("product_2a", "product", "2a", page_evidence,
                    name="4-phenyl-2,3-butadien-2-yl perfluorobutyl ketone", smiles=SMILES["2a"]),
    ]
    conditions = []
    if entry == 7:
        parts.append(participant("rf_reagent", "reagent", "n-C4F9Ti(Oi-Pr)4MgX", page_evidence,
                                 amounts=[field("equivalents", qty(3.0, "equiv"), ev(2))]))
        conditions.extend([
            field("temperature_start", qty(-78, "°C"), ev(2)),
            field("warm_to", "r.t.", ev(2)),
            field("reaction_time", qty(hours, "h"), ev(2)),
        ])
    else:
        parts.append(participant("rf_reagent", "reagent", "n-C4F9MgX", page_evidence,
                                 amounts=[field("equivalents", qty(equivalents, "equiv"), ev(2))]))
        if entry == 1:
            parts.append(participant("feacac3", "catalyst", "Fe(acac)3", page_evidence,
                                     name="iron(III) acetylacetonate",
                                     amounts=[field("catalyst_loading", qty(10, "mol%"), ev(2))]))
            conditions.extend([
                field("reaction_temperature", qty(-78, "°C"), ev(2)),
                field("reaction_time", qty(hours, "h"), ev(2)),
            ])
        else:
            conditions.extend([
                field("temperature_start", qty(-80, "°C"), ev(2)),
                field("warm_to", qty(-70, "°C"), ev(2)),
                field("warming_time", qty(35, "min"), ev(2)),
                field("reaction_temperature", qty(-70, "°C"), ev(2)),
                field("reaction_time", qty(hours, "h"), ev(2)),
            ])
    solvent_label = "anhydrous THF" if entry == 3 else "anhydrous Et2O"
    parts.append(participant("solvent", "solvent", solvent_label, page_evidence, name=solvent_label))
    outcomes = [
        field("NMR_yield_2a", qty(product_yield, "%"), ev(2), ["product_2a"]),
        field("yield_measurement_basis", "NMR", ev(2), ["product_2a"]),
        field("recovered_starting_material_yield", qty(recovery, "%"), ev(2), ["substrate"]),
    ]
    row_notes = ["Table 1 optimization row; footnotes override the shared header where applicable."]
    row_unresolved = ["Exact substrate amount, workup, purification, and atmosphere are not reported in the visible main-text row."]
    if entry == 1:
        row_notes.append("The page-1 prose states 5 mol% Fe(acac)3, whereas Table 1 footnote a states 10 mol%; the table-specific value is structured and the conflict is retained for review.")
        row_unresolved.append("Conflicting Fe(acac)3 loading: 5 mol% in page-1 prose versus 10 mol% in Table 1 footnote a.")
    return record(
        f"table1_entry{entry}", "optimization_entry", page_evidence, parts,
        [step("reaction", [p["entity_id"] for p in parts], conditions)], outcomes,
        notes=row_notes,
        unresolved=row_unresolved
    )


table1_rows = [
    (1, "1a", "Me", 3.0, 5, 48, 30),
    (2, "1a", "Me", 3.5, 6, 78, 0),
    (3, "1a", "Me", 3.5, 20.5, 0, 63),
    (4, "1a", "Me", 3.0, 16, 75, 2),
    (5, "1a", "Me", 2.5, 16, 78, 8),
    (6, "1a", "Me", 2.0, 16, 58, 10),
    (7, "1a", "Me", 3.0, 11, 47, 0),
    (8, "1b", "Et", 3.5, 6, 88, 0),
]
records.extend(table1_record(*row) for row in table1_rows)

# Equation 1: a separate substrate example outside Table 2.
e2 = ev(2)
records.append(record(
    "equation1_1k_to_2o", "reported_experiment", e2,
    [participant("substrate_1k", "reactant", "1k", e2,
                 name="methyl 4,5-dodecadienoate (R=n-C6H13)"),
     participant("rf_reagent", "reagent", "n-C4F9MgX", e2,
                 amounts=[field("equivalents", qty(3.5, "equiv"), e2)]),
     participant("solvent", "solvent", "Et2O", e2, name="diethyl ether"),
     participant("product_2o", "product", "2o", e2)],
    [step("reaction", ["substrate_1k", "rf_reagent", "solvent", "product_2o"], [
        field("temperature_start", qty(-80, "°C"), e2),
        field("warm_to", qty(-70, "°C"), e2),
        field("warming_time", qty(35, "min"), e2),
        field("reaction_temperature", qty(-70, "°C"), e2),
        field("reaction_time", qty(16, "h"), e2),
    ])],
    [field("reported_yield_2o", qty(77, "%"), e2, ["product_2o"]),
     field("yield_measurement_basis", None, [], ["product_2o"])],
    unresolved=["The source does not state the yield measurement basis, exact scale, workup, purification, or atmosphere for Equation 1."]
))

# Scheme 2: two distinct stability/no-further-reaction tests.
for suffix, warm_to, reaction_temp, hours, recovered in [
    ("lowtemp", qty(-70, "°C"), qty(-70, "°C"), 15.5, 80),
    ("warm", "r.t.", None, 16, 85),
]:
    cond = [field("temperature_start", qty(-80, "°C"), e2)]
    if suffix == "lowtemp":
        cond += [field("warm_to", warm_to, e2), field("warming_time", qty(30, "min"), e2),
                 field("reaction_temperature", reaction_temp, e2)]
    else:
        cond += [field("warm_to", warm_to, e2)]
    cond.append(field("reaction_time", qty(hours, "h"), e2))
    records.append(record(
        f"scheme2_{suffix}_no_reaction", "reported_experiment", e2,
        [participant("substrate_2a", "reactant", "2a", e2,
                     name="4-phenyl-2,3-butadien-2-yl perfluorobutyl ketone", smiles=SMILES["2a"]),
         participant("rf_reagent", "reagent", "n-C4F9MgX", e2,
                     amounts=[field("equivalents", qty(3.5, "equiv"), e2)]),
         participant("solvent", "solvent", "anhydrous Et2O", e2, name="anhydrous diethyl ether")],
        [step("stability_test", ["substrate_2a", "rf_reagent", "solvent"], cond)],
        [field("recovered_starting_material_yield", qty(recovered, "%"), e2, ["substrate_2a"]),
         field("further_reaction_observed", "no further reaction observed", e2)],
        notes=["Scheme 2 reports recovery of ketone 2a rather than a product yield."],
        unresolved=["Exact scale, workup, recovery measurement basis, and atmosphere are not shown."]
    ))


table2_rows = [
    # entry, substrate, R1, R2, R3, Rf, method, time, product, yield, equivalents, temp, scale, recovery
    (1, "1b", "Ph", "H", "Me", "n-C4F9", "A", 6, "2a", 74, 3.5, -70, None, None),
    (2, "1b", "Ph", "H", "Me", "n-C4F9", "A", 23, "2a", 83, 3.5, -70, 5.0, None),
    (3, "1b", "Ph", "H", "Me", "n-C6F13", "B", 16, "2b", 70, 3.5, -70, None, None),
    (4, "1c", "n-Bu", "H", "Me", "n-C4F9", "A", 15, "2c", 66, 3.5, -70, None, None),
    (5, "1c", "n-Bu", "H", "Me", "n-C6F13", "A", 16, "2d", 63, 4.0, -70, None, None),
    (6, "1d", "n-C7H15", "H", "Me", "n-C4F9", "A", 6, "2e", 75, 3.5, -70, None, None),
    (7, "1d", "n-C7H15", "H", "Me", "n-C6F13", "A", 16, "2f", 68, 4.0, -70, None, None),
    (8, "1e", "H", "H", "Bn", "n-C4F9", "A", 16, "2g", 58, 3.5, -70, None, None),
    (9, "1f", "H", "H", "n-Pr", "n-C6F13", "A", 12, "2h", 61, 3.5, -70, None, None),
    (10, "1g", "Ph", "Et", "H", "n-C4F9", "A", 21, "2i", 53, 4.0, -70, None, 23),
    (11, "1h", "(CH2)5", "", "Me", "n-C4F9", "A", 17, "2j", 74, 3.5, -60, None, None),
    (12, "1h", "(CH2)5", "", "Me", "n-C6F13", "A", 16.5, "2k", 55, 4.0, -70, None, None),
    (13, "1i", "Ph", "Et", "Me", "n-C4F9", "A", 16, "2l", 71, 3.5, -70, None, None),
    (14, "1i", "Ph", "Et", "Me", "n-C6F13", "A", 16.5, "2m", 85, 4.0, -70, None, None),
    (15, "1j", "Ph", "Ph", "n-Pr", "n-C4F9", "B", 25, "2n", 83, 3.5, -70, None, None),
]


def table2_record(row):
    entry, substrate, r1, r2, r3, rf, method, hours, product, yld, equivalents, temp, scale, recovery = row
    evidence = ev(3)
    if entry in (1, 3):
        evidence = uniq(evidence + ev(4))
    substrate_name = f"ethyl 2,3-allenoate {substrate} (R1={r1}, R2={r2 or '(CH2)5 ring partner'}, R3={r3})"
    product_name = f"allenyl perfluoroalkyl ketone {product} (R1={r1}, R2={r2 or '(CH2)5 ring partner'}, R3={r3}, Rf={rf})"
    sub_amounts = []
    if scale is not None:
        sub_amounts.append(field("reaction_scale", qty(scale, "mmol"), ev(3)))
    product_smiles = SMILES.get(product)
    substrate_smiles = SMILES.get(substrate)
    parts = [
        participant("substrate", "reactant", substrate, evidence, name=substrate_name,
                    smiles=substrate_smiles, amounts=sub_amounts),
        participant("product", "product", product, evidence, name=product_name, smiles=product_smiles),
        participant("rfmgx", "reagent", f"{rf}MgX", ev(3),
                    amounts=[field("equivalents", qty(equivalents, "equiv"), ev(3))]),
        participant("rfi", "reagent", f"{rf}I", ev(3),
                    amounts=[field("equivalents", qty(1.5, "equiv"), ev(3))]),
        participant("exchange_reagent", "reagent", "EtMgBr" if method == "A" else "PhMgBr", ev(3)),
        participant("solvent", "solvent", "anhydrous Et2O", evidence, name="anhydrous diethyl ether"),
    ]
    prep_conditions = [
        field("preparation_method", f"Method {method}: {rf}MgX generated in situ from {rf}I and " +
              ("EtMgBr" if method == "A" else "PhMgBr"), ev(3)),
        field("preparation_temperature", qty(-80, "°C"), ev(3)),
    ]
    reaction_conditions = [field("temperature_start", qty(-80, "°C"), ev(3))]
    if temp == -60:
        reaction_conditions += [field("reaction_temperature", qty(-60, "°C"), ev(3))]
    else:
        reaction_conditions += [
            field("warm_to", qty(-70, "°C"), ev(3)),
            field("warming_time", rng(30, 40, "min", "30–40 min"), ev(3)),
            field("reaction_temperature", qty(-70, "°C"), ev(3)),
        ]
    reaction_conditions.append(field("reaction_time", qty(hours, "h"), ev(3)))

    # Exact Method A/B batches on page 4 correspond to Table 2 entries 1 and 3.
    if entry == 1:
        parts[0]["amounts"] += [field("mass", qty(81.0, "mg"), ev(4)), field("amount", qty(0.40, "mmol"), ev(4))]
        parts[1]["amounts"] += [field("isolated_mass", qty(111.0, "mg"), ev(4), ["product"])]
        parts[3]["amounts"] += [field("volume", qty(0.36, "mL"), ev(4)), field("mass", qty(0.72, "g"), ev(4)), field("amount", qty(2.09, "mmol"), ev(4))]
        parts[4]["amounts"] += [field("volume", qty(0.47, "mL"), ev(4)), field("concentration", qty(3.0, "M"), ev(4)), field("amount", qty(1.41, "mmol"), ev(4))]
        parts[3]["amounts"] += [field("reported_density", "d = 2.01 g/mL", ev(4))]
        parts[5]["amounts"] += [field("initial_volume", qty(2.5, "mL"), ev(4)), field("rinse_volume", qty(0.7, "mL"), ev(4)), field("substrate_solution_volume", qty(1, "mL"), ev(4)), field("extraction_portion_volume", qty(20, "mL"), ev(4))]
        prep_conditions += [field("preparation_time", qty(70, "min"), ev(4))]
        reaction_conditions = [field("temperature_start", qty(-80, "°C"), ev(4)), field("warm_to", qty(-70, "°C"), ev(4)), field("warming_time", qty(30, "min"), ev(4)), field("reaction_temperature", qty(-70, "°C"), ev(4)), field("reaction_time", qty(6, "h"), ev(4))]
    elif entry == 3:
        parts[0]["amounts"] += [field("mass", qty(80.3, "mg"), ev(4)), field("amount", qty(0.40, "mmol"), ev(4))]
        parts[1]["amounts"] += [field("isolated_mass", qty(132.1, "mg"), ev(4), ["product"])]
        parts[3]["amounts"] += [field("volume", qty(0.45, "mL"), ev(4)), field("mass", qty(0.93, "g"), ev(4)), field("amount", qty(2.09, "mmol"), ev(4))]
        parts[4]["amounts"] += [field("volume", qty(0.48, "mL"), ev(4)), field("concentration", qty(3.0, "M"), ev(4)), field("amount", qty(1.44, "mmol"), ev(4))]
        parts[3]["amounts"] += [field("reported_density", "d = 2.06 g/mL", ev(4))]
        parts[5]["amounts"] += [field("initial_volume", qty(2.5, "mL"), ev(4)), field("rinse_volume", qty(0.7, "mL"), ev(4)), field("substrate_solution_volume", qty(1, "mL"), ev(4)), field("extraction_portion_volume", qty(20, "mL"), ev(4))]
        prep_conditions += [field("organomagnesium_addition_time", qty(5, "min"), ev(4)), field("preparation_time", qty(85, "min"), ev(4))]
        reaction_conditions = [field("temperature_start", qty(-80, "°C"), ev(4)), field("warm_to", qty(-70, "°C"), ev(4)), field("warming_time", qty(30, "min"), ev(4)), field("reaction_temperature", qty(-70, "°C"), ev(4)), field("reaction_time", qty(16, "h"), ev(4))]

    steps = [step("prepare_rfmgx", ["rfi", "exchange_reagent", "solvent", "rfmgx"], prep_conditions),
             step("reaction", ["substrate", "rfmgx", "solvent", "product"], reaction_conditions)]
    if entry in (1, 3):
        parts.extend([
            participant("nh4cl", "reagent", "saturated aqueous NH4Cl", ev(4), amounts=[field("volume", qty(5, "mL"), ev(4))]),
            participant("brine", "reagent", "brine", ev(4), amounts=[field("volume", qty(5, "mL"), ev(4))]),
            participant("drying_agent", "reagent", "anhydrous Na2SO4", ev(4)),
            participant("chromatography_eluent", "solvent", "petroleum ether (bp 60–90 °C)", ev(4)),
        ])
        steps.append(step("workup_and_purification", ["product", "nh4cl", "brine", "drying_agent", "chromatography_eluent"], [
            field("workup", "quenched at –70 °C; warmed naturally to r.t.; extracted with Et2O; washed with brine; dried over anhydrous Na2SO4", ev(4)),
            field("operation", "Et2O extraction repeated 3 times", ev(4)),
            field("purification", "filtration, evaporation, and silica-gel chromatography", ev(4)),
        ]))
    outcomes = [field("isolated_yield", qty(yld, "%"), ev(3), ["product"]),
                field("yield_measurement_basis", "isolated", ev(3), ["product"])]
    if recovery is not None:
        outcomes.append(field("recovered_starting_material_yield", qty(recovery, "%"), ev(3), ["substrate"]))
    unresolved = ["Candidate structures expanded from table R-group labels remain machine-unverified."]
    if entry not in (1, 3):
        unresolved.append("Exact batch masses, workup, purification, atmosphere, and preparation duration are not reported for this row in the visible main text.")
    else:
        unresolved.append("An inert atmosphere is not stated; solvent sub-volumes were retained separately and were not silently summed.")
    return record(f"table2_entry{entry}", "substrate_scope_entry", evidence, parts, steps, outcomes,
                  notes=[f"Table 2 row using Method {method}; row footnotes were applied."], unresolved=unresolved)


records.extend(table2_record(row) for row in table2_rows)


def derivatization_record(suffix, reagent_label, product_label, yld, hours=None, temp=None, equivalents=None, basis=None):
    evidence = uniq(ev(2) + ev(3))
    parts = [
        participant("substrate_2a", "reactant", "2a", evidence,
                    name="4-phenyl-2,3-butadien-2-yl perfluorobutyl ketone", smiles=SMILES["2a"]),
        participant("reagent", "reagent", reagent_label, evidence,
                    amounts=[field("equivalents", qty(equivalents, "equiv"), ev(3))] if equivalents is not None else []),
        participant("solvent", "solvent", "anhydrous Et2O", ev(3), name="anhydrous diethyl ether"),
        participant("product", "product", product_label, evidence, smiles=SMILES.get(product_label)),
    ]
    conditions = []
    if temp is not None:
        conditions.append(field("reaction_temperature", temp, ev(3)))
    if hours is not None:
        conditions.append(field("reaction_time", qty(hours, "h"), ev(3)))
    outcomes = [field((basis + "_yield") if basis else "reported_yield", qty(yld, "%"), evidence, ["product"]),
                field("yield_measurement_basis", basis, evidence if basis else [], ["product"])]
    return record(suffix, "reported_experiment", evidence, parts,
                  [step("reaction", ["substrate_2a", "reagent", "solvent", "product"], conditions)] if conditions else [], outcomes,
                  unresolved=["Exact scale, atmosphere, workup, and purification are not reported for this transformation in the visible main text."])


# The low-yield MeMgCl result appears only in the page-2 prose.
records.append(record(
    "scheme3_memgcl_7a", "reported_experiment", e2,
    [participant("substrate_2a", "reactant", "2a", e2, smiles=SMILES["2a"]),
     participant("memgcl", "reagent", "MeMgCl", e2, name="methylmagnesium chloride"),
     participant("product_7a", "product", "7a", e2, smiles=SMILES["7a"])],
    [],
    [field("NMR_yield_7a", qty(41, "%"), e2, ["product_7a"]),
     field("yield_measurement_basis", "NMR", e2, ["product_7a"])],
    unresolved=["Reagent loading, solvent, temperature, duration, scale, atmosphere, workup, and purification are not stated for the MeMgCl result."]
))
records.append(derivatization_record("scheme3_meli_7a", "MeLi", "7a", 80, 19, qty(-60, "°C"), 1.6, None))
records.append(derivatization_record("scheme3_nbuli_7b", "n-BuLi", "7b", 70, 18, qty(-60, "°C"), 1.6, None))

# Pd-catalyzed 8a: Scheme 3 plus the exact experiment in note 17 (pages 4-5).
e8a = uniq(ev(2) + ev(3) + ev(4) + ev(5))
records.append(record(
    "scheme3_pd_8a", "reported_experiment", e8a,
    [participant("substrate_2a", "reactant", "2a", e8a, smiles=SMILES["2a"],
                 amounts=[field("mass", qty(76.2, "mg"), ev(4)), field("amount", qty(0.20, "mmol"), ev(4))]),
     participant("allyl_bromide", "reagent", "allyl bromide", e8a,
                 amounts=[field("mass", qty(128.2, "mg"), ev(4)), field("amount", qty(1.0, "mmol"), ev(4)), field("equivalents", qty(5, "equiv"), ev(3)), field("purity", qty(97, "%"), ev(4))]),
     participant("pdcl2", "catalyst", "PdCl2", e8a,
                 amounts=[field("mass", qty(2.2, "mg"), ev(4)), field("amount", qty(0.01, "mmol"), ev(4)), field("catalyst_loading", qty(5, "mol%"), ev(3))]),
     participant("dma", "solvent", "DMA", e8a, amounts=[field("volume", qty(2, "mL"), ev(4))]),
     participant("product_8a", "product", "8a", e8a,
                 name="4-allyl-3-methyl-2-(n-perfluorobutyl)-5-phenylfuran", smiles=SMILES["8a"],
                 amounts=[field("isolated_mass", qty(69.8, "mg"), ev(4), ["product_8a"])]),
     participant("water", "reagent", "H2O", ev(4), amounts=[field("volume", qty(5, "mL"), ev(4))]),
     participant("extraction_solvent", "solvent", "Et2O", ev(4)),
     participant("drying_agent", "reagent", "anhydrous Na2SO4", ev(4)),
     participant("eluent", "solvent", "n-hexane", ev(4))],
    [step("reaction", ["substrate_2a", "allyl_bromide", "pdcl2", "dma", "product_8a"], [
        field("addition_temperature", "r.t.", ev(4)), field("reaction_temperature", qty(50, "°C"), ev(4)),
        field("reaction_time", qty(20.5, "h"), ev(4)), field("operation", "monitored by TLC (PE)", ev(4))]),
     step("workup", ["product_8a", "water", "extraction_solvent", "drying_agent"], [
         field("workup", "quenched with H2O; aqueous layer extracted with Et2O (5 × 15 mL); dried over anhydrous Na2SO4", ev(4))]),
     step("purification", ["product_8a", "eluent"], [field("purification", "filtration, evaporation, and silica-gel chromatography with n-hexane", ev(4))])],
    [field("isolated_yield_8a", qty(83, "%"), uniq(ev(3) + ev(4)), ["product_8a"]),
     field("yield_measurement_basis", "isolated", ev(4), ["product_8a"])],
    unresolved=["No reaction atmosphere is stated. Candidate connectivity remains machine-unverified; page 5 supplies continuation characterization only."]
))

# Au-catalyzed 8b: exact experiment begins on page 5 and continues in the right column.
e8b = uniq(ev(2) + ev(3) + ev(5))
records.append(record(
    "scheme3_au_8b", "reported_experiment", e8b,
    [participant("substrate_2a", "reactant", "2a", e8b, smiles=SMILES["2a"],
                 amounts=[field("mass", qty(112.1, "mg"), ev(5)), field("amount", qty(0.30, "mmol"), ev(5))]),
     participant("aucl3", "catalyst", "AuCl3", e8b,
                 amounts=[field("mass", qty(4.5, "mg"), ev(5)), field("catalyst_loading", qty(5, "mol%"), ev(5))]),
     participant("solvent", "solvent", "anhydrous CH2Cl2", e8b, amounts=[field("volume", qty(1.5, "mL"), ev(5))]),
     participant("product_8b", "product", "8b", e8b,
                 name="3-methyl-2-n-perfluorobutyl-5-phenylfuran", smiles=SMILES["8b"],
                 amounts=[field("isolated_mass", qty(103.4, "mg"), ev(5), ["product_8b"])]),
     participant("postreaction_ether", "solvent", "Et2O", ev(5), amounts=[field("volume", qty(20, "mL"), ev(5))]),
     participant("eluent", "solvent", "petroleum ether (bp 60–90 °C)", ev(5))],
    [step("reaction", ["substrate_2a", "aucl3", "solvent", "product_8b"], [
        field("atmosphere", "N2", ev(5)), field("reaction_temperature", "r.t.", ev(5)),
        field("reaction_time", qty(24, "h"), ev(5)), field("operation", "monitored by TLC (petroleum ether)", ev(5))]),
     step("workup_and_purification", ["product_8b", "postreaction_ether", "eluent"], [
         field("workup", "Et2O added, followed by evaporation", ev(5)),
         field("purification", "flash chromatography on silica gel with petroleum ether (bp 60–90 °C)", ev(5))])],
    [field("isolated_yield_8b", qty(92, "%"), uniq(ev(3) + ev(5)), ["product_8b"]),
     field("yield_measurement_basis", "isolated", ev(5), ["product_8b"])],
    unresolved=["Candidate connectivity remains machine-unverified."]
))


raw_path = OUT / "records_pages_0001_0005.json"
raw_path.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")


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
                {"region": "lower-left Scheme 1 (three arrows)",
                 "finding": "Two arrows are cited prior transformations and one is the generic perfluoroalkylation developed here; each was classified separately and no generic yield was invented.",
                 "evidence_ids": [f"{DOC}:page1:image", f"{DOC}:page1:text"]},
                {"region": "right-column opening Results and Discussion",
                 "finding": "Narrative corroborates Table 1 entries 1-3, 7-8, including the 48% NMR result, catalyst-free improvement, THF no-reaction result, titanium reagent result, and ester comparison; cited older perfluoroalkyl chemistry remains literature context.",
                 "evidence_ids": [f"{DOC}:page1:image", f"{DOC}:page1:text", f"{DOC}:page2:image"]},
            ],
            "record_ids": [rid("scheme1_prior_fe_grignard"), rid("scheme1_prior_allylmagnesium"), rid("scheme1_general_perfluoroalkylation"),
                           rid("table1_entry1"), rid("table1_entry2"), rid("table1_entry3"), rid("table1_entry7"), rid("table1_entry8")],
            "unresolved": ["Generic Scheme 1 R groups are not fully specified; introduction citations were not treated as this-paper batches."],
        },
        {
            "page": 2,
            "state": "attempted",
            "regions": [
                {"region": "upper Table 1 including reaction drawing, eight rows, and footnotes a-c",
                 "finding": "Eight optimization rows were extracted independently with reagent equivalents, time, NMR yield, starting-material recovery, THF/catalyst/titanium overrides, and shared temperature program.",
                 "evidence_ids": [f"{DOC}:page2:image", f"{DOC}:page2:text"]},
                {"region": "middle-left Equation 1",
                 "finding": "The 1k to 2o experiment was extracted as a separate reported experiment with 77% reported yield.",
                 "evidence_ids": [f"{DOC}:page2:image", f"{DOC}:page2:text"]},
                {"region": "lower-left Scheme 2",
                 "finding": "Two distinct stability tests were extracted; both report recovered 2a and no further reaction rather than product yields.",
                 "evidence_ids": [f"{DOC}:page2:image", f"{DOC}:page2:text"]},
                {"region": "lower-right derivatization prose and SI statement",
                 "finding": "MeMgCl, MeLi, n-BuLi, PdCl2/allyl bromide, and AuCl3 results were reconciled with Scheme 3; the advertised Supporting Information was not associated because it was not supplied.",
                 "evidence_ids": [f"{DOC}:page2:image", f"{DOC}:page2:text", f"{DOC}:page3:image"]},
            ],
            "record_ids": [*[rid(f"table1_entry{i}") for i in range(1, 9)], rid("equation1_1k_to_2o"), rid("scheme2_lowtemp_no_reaction"), rid("scheme2_warm_no_reaction"),
                           rid("scheme3_memgcl_7a"), rid("scheme3_meli_7a"), rid("scheme3_nbuli_7b"), rid("scheme3_pd_8a"), rid("scheme3_au_8b")],
            "unresolved": ["Most optimization rows omit exact batch scale, workup, purification, and atmosphere; Equation 1 does not state its yield basis."],
        },
        {
            "page": 3,
            "state": "attempted",
            "regions": [
                {"region": "upper Table 2 drawing, rows 1-15, and footnotes a-e",
                 "finding": "Fifteen substrate-scope rows were extracted independently; Method A/B precursors, 4.0-equivalent overrides, 5.0 mmol scale, 23% recovery, and -60 °C override were structured.",
                 "evidence_ids": [f"{DOC}:page3:image", f"{DOC}:page3:text"]},
                {"region": "lower Scheme 3 (four drawn arrows)",
                 "finding": "MeLi, n-BuLi, Pd-catalyzed allylation/cyclization, and Au-catalyzed cyclization were recorded as four experiments; the separate MeMgCl result remains its own prose-derived record.",
                 "evidence_ids": [f"{DOC}:page3:image", f"{DOC}:page3:text"]},
            ],
            "record_ids": [*[rid(f"table2_entry{i}") for i in range(1, 16)], rid("scheme3_meli_7a"), rid("scheme3_nbuli_7b"), rid("scheme3_pd_8a"), rid("scheme3_au_8b")],
            "unresolved": ["Most Table 2 rows lack exact batch quantities and workup in the supplied main text; candidate R-group structure expansions remain unverified."],
        },
        {
            "page": 4,
            "state": "attempted",
            "regions": [
                {"region": "left column references 1-14",
                 "finding": "Bibliographic prior-work citations were inspected and classified as references, not new experiments of this paper.",
                 "evidence_ids": [f"{DOC}:page4:image", f"{DOC}:page4:text"]},
                {"region": "footnote 15 Method A and Method B",
                 "finding": "Exact preparation, reaction, workup, purification, masses, amounts, and isolated outcomes were merged into Table 2 entries 1 and 3, respectively, rather than duplicated.",
                 "evidence_ids": [f"{DOC}:page4:image", f"{DOC}:page4:text", f"{DOC}:page3:image"]},
                {"region": "footnote 17 preparation of 8a",
                 "finding": "The detailed PdCl2/allyl bromide batch was merged into the Scheme 3 8a record; characterization continues on page 5.",
                 "evidence_ids": [f"{DOC}:page4:image", f"{DOC}:page4:text", f"{DOC}:page3:image"]},
            ],
            "record_ids": [rid("table2_entry1"), rid("table2_entry3"), rid("scheme3_pd_8a")],
            "unresolved": ["Spectral characterization was retained only as identity context and was not interpreted peak by peak."],
        },
        {
            "page": 5,
            "state": "attempted",
            "regions": [
                {"region": "upper-left continuation of footnote 17",
                 "finding": "Continuation characterization for isolated 8a was linked to the existing Pd-catalyzed record; no duplicate experiment was created.",
                 "evidence_ids": [f"{DOC}:page5:image", f"{DOC}:page5:text", f"{DOC}:page4:image"]},
                {"region": "footnote 19 preparation and characterization of 8b across both columns",
                 "finding": "The exact AuCl3 batch, nitrogen atmosphere, room-temperature duration, workup, chromatography, mass, and 92% isolated yield were merged into the Scheme 3 8b record.",
                 "evidence_ids": [f"{DOC}:page5:image", f"{DOC}:page5:text", f"{DOC}:page3:image"]},
                {"region": "remaining lower page",
                 "finding": "Blank publication area; no additional arrows, tables, footnotes, or experiments are present.",
                 "evidence_ids": [f"{DOC}:page5:image"]},
            ],
            "record_ids": [rid("scheme3_pd_8a"), rid("scheme3_au_8b")],
            "unresolved": ["Spectral assignments were not independently interpreted; candidate product structures remain unverified."],
        },
    ],
}

coverage_dir = ROOT / "runs/current/coverage"
coverage_dir.mkdir(parents=True, exist_ok=True)
(coverage_dir / "pages_0001_0005.json").write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

# Mark only this document's page tasks as attempted.
tasks_path = ROOT / "runs/current/tasks.json"
tasks = json.loads(tasks_path.read_text())
for task in tasks:
    if task.get("document_id") == DOC and task.get("evidence_id") in {f"{DOC}:page{i}:text" for i in range(1, 6)}:
        task["state"] = "attempted"
        task["reason"] = "Original page image and extracted text inspected; experiment records and coverage ledger generated."
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"records": len(records), "raw": str(raw_path), "coverage_pages": len(coverage["pages"])}, ensure_ascii=False))
