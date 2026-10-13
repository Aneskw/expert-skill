import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "runs/current/raw_model/records_pages_0001_0006.json"
COVERAGE = ROOT / "runs/current/coverage/pages_0001_0006.json"
TASKS = ROOT / "runs/current/tasks.json"
DOC = "doc_eee7fbd3c3a2bc18"


def ev(page):
    return [f"{DOC}:page{page}:text", f"{DOC}:page{page}:image"]


def fact(value, evidence=()):
    return {
        "value": value,
        "evidence_ids": list(evidence) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def fld(name, value, evidence=(), targets=None):
    item = {"name": name, "fact": fact(value, evidence)}
    if targets:
        item["target_entity_ids"] = targets
    return item


def part(entity_id, role, label, evidence, *, name=None, smiles=None, amounts=()):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence) if name else fact(None),
        "smiles": fact(smiles, evidence) if smiles else fact(None),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": list(amounts),
    }


def rec(rid, kind, evidence, participants=(), steps=(), outcomes=(), notes=(), unresolved=()):
    return {
        "record_id": f"{DOC}:{rid}",
        "document_id": DOC,
        "source_reaction_id": rid,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": list(dict.fromkeys(evidence)),
        "participants": list(participants),
        "steps": list(steps),
        "outcomes": list(outcomes),
        "notes": [fact(n, evidence) for n in notes],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": list(unresolved),
        },
    }


def step(step_id, participant_ids, conditions):
    return {"step_id": step_id, "participant_ids": participant_ids, "conditions": conditions}


records = []

# Page 1: prior-work scheme and starting-material preparations described in prose.
e1 = ev(1)
records.append(rec(
    "scheme1_prior_propargylic_alcohol_carbometallation",
    "literature_example", e1,
    participants=[
        part("scheme1_primary_or_secondary_propargylic_alcohol", "reactant", "generic propargylic alcohol (Scheme 1)", e1),
        part("scheme1_organometallic_r2m", "reagent", "R2M", e1),
        part("scheme1_electrophile", "reagent", "E+", e1),
        part("scheme1_products", "product", "generic branched/linear allylic alcohol products A/B", e1),
    ],
    notes=["Scheme 1 summarizes cited propargylic-alcohol carbometallation patterns and limitations; it is not a present-paper experiment."],
    unresolved=["Generic R groups, organometallic reagent, electrophile, conditions, and product structures are not specified at experiment level."],
))
records.append(rec(
    "starting_allenol_1a_preparation",
    "reported_experiment", e1,
    participants=[
        part("chlorobutynol", "reactant", "4-chlorobut-2-ynol", e1),
        part("n_butylmagnesium_bromide", "reactant", "n-C4H9MgBr", e1),
        part("cubr", "catalyst", "CuBr", e1),
        part("allenol_1a", "product", "allenol 1a", e1),
    ],
    outcomes=[fld("reported_yield", {"number": 61, "unit": "%"}, e1, ["allenol_1a"]), fld("yield_measurement_basis", None)],
    notes=["The paper states that 1a was prepared by this CuBr-catalyzed reaction."],
    unresolved=["Reactant quantities, catalyst loading, solvent, temperature, time, atmosphere, workup, purification, yield basis, and candidate product structure are not reported here."],
))
records.append(rec(
    "starting_allenols_1b_to_1f_literature_procedure",
    "literature_example", e1 + ev(2),
    participants=[
        part("propargylic_bromide", "reactant", "propargylic bromide", e1 + ev(2)),
        part("aldehyde", "reactant", "aldehyde", e1 + ev(2)),
        part("nai", "reagent", "NaI", e1 + ev(2), smiles="[Na+].[I-]"),
        part("sncl2", "reagent", "SnCl2", e1 + ev(2)),
        part("dmf", "solvent", "DMF", e1 + ev(2), smiles="CN(C)C=O"),
        part("allenols_1b_1f", "product", "allenols 1b–f", e1 + ev(2)),
    ],
    outcomes=[fld("reported_group_yield_range", {"minimum": 40, "maximum": 67, "unit": "%", "raw_text": "40–67%"}, e1 + ev(2), ["allenols_1b_1f"]), fld("yield_measurement_basis", None)],
    notes=["The grouped preparation is attributed to reference 8; individual substrate-to-yield assignments are not printed."],
    unresolved=["Individual aldehydes, product-specific yields, quantities, time, temperature, atmosphere, workup, purification, and structures are missing."],
))
records.append(rec(
    "starting_allenols_1g_1h_crabbe_literature_procedure",
    "literature_example", ev(2),
    participants=[part("crabbe_reaction_substrates", "reactant", "substrates for the Crabbé reaction", ev(2)), part("allenols_1g_1h", "product", "allenols 1g and 1h", ev(2))],
    outcomes=[fld("reported_group_yield_range", {"minimum": 60, "maximum": 64, "unit": "%", "raw_text": "60–64%"}, ev(2), ["allenols_1g_1h"]), fld("yield_measurement_basis", None)],
    notes=["The grouped preparation is attributed to reference 9."],
    unresolved=["Individual yields, reagents, quantities, conditions, workup, purification, and structures are not given on the inspected pages."],
))
records.append(rec(
    "starting_s1b_kinetic_resolution_literature_procedure",
    "literature_example", ev(2),
    participants=[
        part("racemic_1b", "reactant", "racemic 1b", ev(2)),
        part("vinyl_acetate", "reagent", "vinyl acetate", ev(2), smiles="C=COC(C)=O"),
        part("novozym_435", "catalyst", "Novozym 435", ev(2)),
        part("s_1b", "product", "(S)-1b", ev(2)),
    ],
    outcomes=[fld("reported_yield", {"number": 31, "unit": "%"}, ev(2), ["s_1b"]), fld("yield_measurement_basis", None)],
    notes=["The kinetic-resolution preparation is attributed to reference 8."],
    unresolved=["Quantities, solvent, time, temperature, atmosphere, workup, purification, and product ee at this preparation stage are not given here."],
))

# Page 2, Scheme 2: present-paper reproduction of prior conditions.
e2 = ev(2)
records.append(rec(
    "scheme2_reproduction_1a_to_2a",
    "reported_experiment", e2,
    participants=[
        part("cu_i", "reagent", "CuI", e2, amounts=[fld("equivalents", {"number": 2, "unit": "equiv"}, e2)]),
        part("ether_s2", "solvent", "Et2O", e2, smiles="CCOCC"),
        part("iprmgb", "reactant", "i-PrMgBr", e2, amounts=[fld("equivalents", {"number": 2.5, "unit": "equiv"}, e2)]),
        part("one_a_s2", "reactant", "allenol 1a", e2),
        part("two_a", "product", "allylic alcohol 2a", e2),
    ],
    steps=[
        step("organocopper_formation", ["cu_i", "ether_s2", "iprmgb"], [fld("temperature", {"number": -70, "unit": "°C"}, e2), fld("time", {"number": 2, "unit": "h"}, e2)]),
        step("carbometallation_and_warming", ["one_a_s2", "two_a"], [fld("initial_temperature", {"number": -60, "unit": "°C"}, e2), fld("time", {"number": 3, "unit": "h"}, e2), fld("warm_to", {"number": 0, "unit": "°C", "raw_text": "−60 to 0 °C"}, e2)]),
    ],
    outcomes=[
        fld("reported_yield", {"number": 12, "unit": "%"}, e2, ["two_a"]),
        fld("recovered_starting_material_yield", {"number": 57, "unit": "%"}, e2, ["one_a_s2"]),
        fld("yield_measurement_basis", None),
    ],
    notes=["The authors state that they ran the reported Gelin–Albrand conditions in their own laboratory."],
    unresolved=["Absolute quantities, atmosphere, workup, purification, and yield basis are not reported."],
))


def table1_record(entry, metal, equiv, solvent, time_h, yield_value, recovery_value, prose_yield=None):
    rid = f"table1_entry{entry}"
    evidence = e2
    metal_role = "catalyst" if metal.startswith("Pd") else "reagent"
    ps = [
        part(f"one_b_t1_{entry}", "reactant", "3-(n-butyl)-penta-3,4-dien-2-ol (1b)", evidence),
        part(f"pentyl_mgbr_t1_{entry}", "reactant", "n-C5H11MgBr", evidence, amounts=[fld("equivalents", {"number": 5, "unit": "equiv"}, evidence), fld("concentration", {"number": 1, "unit": "M"}, evidence)]),
        part(f"metal_t1_{entry}", metal_role, metal, evidence, amounts=[fld("equivalents", {"number": equiv, "unit": "equiv"}, evidence)]),
        part(f"solvent_t1_{entry}", "solvent", solvent, evidence, smiles={"Et2O": "CCOCC", "THF": "C1CCOC1", "toluene": "Cc1ccccc1"}.get(solvent), amounts=[fld("volume", {"number": 1.5, "unit": "mL"}, evidence)]),
        part(f"two_b_t1_{entry}", "product", "E-2b", evidence),
    ]
    y = "table dash (–)" if yield_value is None else {"number": yield_value, "unit": "%"}
    r = "table dash (–)" if recovery_value is None else {"number": recovery_value, "unit": "%"}
    outs = [
        fld("table_reported_yield", y, evidence, [f"two_b_t1_{entry}"]),
        fld("recovered_starting_material_yield", r, evidence, [f"one_b_t1_{entry}"]),
        fld("yield_measurement_basis", None),
    ]
    if prose_yield is not None:
        outs.append(fld("prose_reported_yield", {"number": prose_yield, "unit": "%"}, evidence, [f"two_b_t1_{entry}"]))
    unresolved = ["Workup, purification, atmosphere, substrate amount, and yield measurement basis are not stated for this optimization row."]
    if prose_yield is not None and prose_yield != yield_value:
        unresolved.append(f"Table 1 reports {yield_value}% whereas the page-2 prose reports {prose_yield}% for this entry.")
    if yield_value is None or recovery_value is None:
        unresolved.append("A printed table dash is retained as an undefined source marker, not converted to zero or not detected.")
    return rec(rid, "optimization_entry", evidence, participants=ps,
               steps=[step("carbometallation", [p["entity_id"] for p in ps], [fld("initial_temperature", {"number": -78, "unit": "°C"}, evidence), fld("warm_to", "r.t.", evidence), fld("time", {"number": time_h, "unit": "h"}, evidence)])],
               outcomes=outs, notes=["Table 1 evaluates copper- or palladium-mediated addition followed by hydrolytic product formation."], unresolved=unresolved)


table1 = [
    (1, "CuI", 2, "Et2O", 11.5, 33, 41, 32),
    (2, "CuI", 2, "THF", 12, 6, 78, None),
    (3, "CuCl", 2, "toluene", 18, 71, None, None),
    (4, "CuCl", 2, "Et2O", 11.5, 80, 3, 81),
    (5, "CuCl2", 2, "Et2O", 11.5, None, 77, None),
    (6, "CuCl", 1, "Et2O", 11, 71, 9, None),
    (7, "CuCl", 0.5, "Et2O", 11, 54, 20, None),
    (8, "PdCl2", 0.05, "Et2O", 11.5, None, 83, None),
    (9, "Pd(PPh3)2Cl2", 0.05, "Et2O", 11.5, None, 68, None),
]
records.extend(table1_record(*row) for row in table1)

# Page 3 Scheme 3, with detailed D2O procedure continuing on pages 4–5.
e345 = ev(3) + ev(4) + ev(5)
records.append(rec(
    "scheme3_d2o_quench_e3b",
    "reported_experiment", e345,
    participants=[
        part("one_b_d", "reactant", "allenol 1b", e345, amounts=[fld("mass", {"number": 0.1435, "unit": "g"}, ev(4)), fld("amount", {"number": 1, "unit": "mmol"}, ev(4))]),
        part("cucl_d", "reagent", "CuCl", e345, amounts=[fld("mass", {"number": 0.1981, "unit": "g"}, ev(4)), fld("amount", {"number": 2, "unit": "mmol"}, ev(4)), fld("equivalents", {"number": 2, "unit": "equiv"}, ev(4))]),
        part("ether_d", "solvent", "anhydrous Et2O", e345, smiles="CCOCC", amounts=[fld("volume", {"number": 1.5, "unit": "mL"}, ev(4))]),
        part("pentyl_mgbr_d", "reactant", "n-C5H11MgBr in Et2O", e345, amounts=[fld("volume", {"number": 5, "unit": "mL"}, ev(4)), fld("amount", {"number": 5, "unit": "mmol"}, ev(4)), fld("equivalents", {"number": 5, "unit": "equiv"}, ev(4)), fld("concentration", {"number": 1, "unit": "M"}, ev(4))]),
        part("d2o", "reagent", "D2O", e345, smiles="[2H]O[2H]", amounts=[fld("volume", {"number": 0.5, "unit": "mL"}, ev(4))]),
        part("e3b", "product", "(E)-4-deutero-3-butyldec-3-en-2-ol (E-3b)", e345),
    ],
    steps=[
        step("carbometallation", ["one_b_d", "cucl_d", "ether_d", "pentyl_mgbr_d"], [fld("atmosphere", "nitrogen", ev(4)), fld("initial_temperature", {"number": -78, "unit": "°C"}, ev(4)), fld("warm_to", "r.t.", ev(4)), fld("time", {"number": 11, "unit": "h"}, ev(4)), fld("operation", "monitored by TLC", ev(4))]),
        step("d2o_quench", ["d2o", "e3b"], [fld("temperature", {"number": -5, "unit": "°C"}, ev(4)), fld("time", {"number": 1, "unit": "h"}, ev(4))]),
        step("isolation", ["e3b"], [fld("workup", "water treatment; Et2O extraction (3 × 30 mL); sequential 5% aqueous HCl, saturated aqueous NaHCO3, and brine washes; anhydrous Na2SO4 drying", ev(4) + ev(5)), fld("purification", "silica-gel column chromatography, petroleum ether/ethyl acetate 30:1", ev(5))]),
    ],
    outcomes=[fld("isolated_yield", {"number": 74, "unit": "%"}, e345, ["e3b"]), fld("product_mass", {"number": 0.1616, "unit": "g"}, ev(5), ["e3b"]), fld("deuterium_incorporation_percentage", {"number": 98, "unit": "%"}, e345, ["e3b"]), fld("yield_measurement_basis", "isolated", e345, ["e3b"])],
    unresolved=["The candidate constitutional and E-isomer SMILES, including isotopic placement, remains unverified."],
))
records.append(rec(
    "scheme3_iodination_z4b",
    "reported_experiment", ev(3),
    participants=[
        part("one_b_z4b", "reactant", "allenol 1b", ev(3)),
        part("pentyl_mgbr_z4b", "reactant", "n-C5H11MgBr in Et2O", ev(3), amounts=[fld("equivalents", {"number": 5, "unit": "equiv"}, ev(3))]),
        part("cucl_z4b", "reagent", "CuCl", ev(3), amounts=[fld("equivalents", {"number": 2, "unit": "equiv"}, ev(3))]),
        part("ether_z4b", "solvent", "Et2O", ev(3), smiles="CCOCC"),
        part("iodine_z4b", "reagent", "I2 in THF", ev(3), smiles="II"),
        part("z4b", "product", "Z-4b", ev(3)),
    ],
    steps=[step("carbometallation_and_iodination", ["one_b_z4b", "pentyl_mgbr_z4b", "cucl_z4b", "ether_z4b", "iodine_z4b", "z4b"], [fld("initial_temperature", {"number": -78, "unit": "°C"}, ev(3)), fld("warm_to", "r.t.", ev(3)), fld("iodination_temperature", {"number": -5, "unit": "°C"}, ev(3))])],
    outcomes=[fld("isolated_yield", {"number": 56, "unit": "%"}, ev(3), ["z4b"]), fld("yield_measurement_basis", "isolated", ev(3), ["z4b"])],
    notes=["Compounds 5 and 6 may be present at 3–4%, if any; E-4b and Z-3b were not observed."],
    unresolved=["Reaction time, exact iodine loading, atmosphere, workup, purification, and candidate structures are not reported for this depicted case."],
))
records.append(rec(
    "scheme3_cyclic_intermediate_c",
    "mechanism", ev(2) + ev(3),
    participants=[part("intermediate_c", "unspecified_agent", "proposed C-type cyclic organometallic intermediate C", ev(3))],
    notes=["The authors propose regioselective carbometallation and use the C-type cyclic intermediate to rationalize Z stereochemistry."],
    unresolved=["The metal identity and exact intermediate structure are generic/unverified; this is a proposal, not an isolated experiment."],
))


scope_rows = [
    (1, "1a", "R1=n-C4H9; R2=H; R3=H", "n-C5H11MgBr", 10, 70, "4a"),
    (2, "(S)-1b", "R1=n-C4H9; R2=CH3; R3=H", "n-C5H11MgBr", 15, 81, "(S)-4b"),
    (3, "1c", "R1=n-C7H15; R2=CH3; R3=H", "n-C5H11MgBr", 17, 74, "4c"),
    (4, "1d", "R1=Ph; R2=CH3; R3=H", "n-C5H11MgBr", 16, 80, "4d"),
    (5, "1e", "R1=allyl; R2=CH3; R3=H", "n-C5H11MgBr", 17, 60, "4e"),
    (6, "1f", "R1=n-C4H9; R2=Ph; R3=H", "n-C5H11MgBr", 19, 59, "4f"),
    (7, "1g", "R1=H; R2=Ph; R3=H", "n-C5H11MgBr", 17, 72, "4g"),
    (8, "1h", "R1=H; R2=Ph; R3=Me", "n-C5H11MgBr", 11.5, 71, "4h"),
    (9, "1b", "R1=n-C4H9; R2=CH3; R3=H", "cyclohexylmagnesium bromide", 17, 84, "4i"),
    (10, "1f", "R1=n-C4H9; R2=Ph; R3=H", "cyclohexylmagnesium bromide", 17, 64, "4j"),
    (11, "1b", "R1=n-C4H9; R2=CH3; R3=H", "isobutylmagnesium bromide", 13, 59, "4k"),
    (12, "1b", "R1=n-C4H9; R2=CH3; R3=H", "phenylmagnesium bromide", 16, 67, "4l"),
    (13, "1b", "R1=n-C4H9; R2=CH3; R3=H", "p-tolylmagnesium bromide", 12, 60, "4m"),
]


def scope_record(entry, substrate, substituents, grignard, time_h, yld, product):
    evidence = ev(3) + ev(4)
    sid = f"substrate_t2_{entry}"
    gid = f"grignard_t2_{entry}"
    cid = f"cucl_t2_{entry}"
    iid = f"iodine_t2_{entry}"
    pid = f"product_t2_{entry}"
    solvent_id = f"ether_t2_{entry}"
    g_eq = 8 if entry in (9, 10) else 5
    iodine_eq = 4 if entry == 1 else 5
    iodine_temp = -78 if entry == 1 else -5
    ps = [
        part(sid, "reactant", f"{substrate} ({substituents})", evidence, amounts=[fld("amount", {"number": 1, "unit": "mmol"}, evidence)]),
        part(gid, "reactant", grignard, evidence, amounts=[fld("equivalents", {"number": g_eq, "unit": "equiv"}, ev(3)), fld("concentration", {"number": 1, "unit": "M"}, ev(3))]),
        part(cid, "reagent", "CuCl", evidence, amounts=[fld("amount", {"number": 2, "unit": "mmol"}, ev(4)), fld("equivalents", {"number": 2, "unit": "equiv"}, evidence)]),
        part(solvent_id, "solvent", "anhydrous Et2O", evidence, smiles="CCOCC", amounts=[fld("volume", {"number": 1.5, "unit": "mL"}, evidence)]),
        part(iid, "reagent", "I2 in anhydrous THF", evidence, smiles="II", amounts=[fld("equivalents", {"number": iodine_eq, "unit": "equiv"}, ev(3))]),
        part(pid, "product", product, evidence, name="(Z)-3-iodo-2-butylnon-2-enol" if entry == 1 else None),
    ]
    # Exact compound-specific amounts are printed only for 4a.
    if entry == 1:
        ps[0]["amounts"] += [fld("mass", {"number": 0.1244, "unit": "g"}, ev(4))]
        ps[1]["amounts"] += [fld("volume", {"number": 5, "unit": "mL"}, ev(4)), fld("amount", {"number": 5, "unit": "mmol"}, ev(4))]
        ps[2]["amounts"] += [fld("mass", {"number": 0.1974, "unit": "g"}, ev(4))]
        ps[4]["amounts"] += [fld("mass", {"number": 1.0, "unit": "g"}, ev(4)), fld("amount", {"number": 4, "unit": "mmol"}, ev(4))]
    outcomes = [fld("table_reported_yield", {"number": yld, "unit": "%"}, ev(3), [pid]), fld("yield_measurement_basis", None)]
    if entry == 1:
        outcomes += [fld("product_mass", {"number": 0.2254, "unit": "g"}, ev(4), [pid]), fld("compound_specific_yield", {"number": 70, "unit": "%"}, ev(4), [pid])]
    if entry == 2:
        outcomes += [fld("starting_material_ee", {"number": 98, "unit": "%"}, ev(3), [sid]), fld("product_ee", {"number": 98, "unit": "%"}, ev(3), [pid]), fld("isolated_yield", {"number": 81, "unit": "%"}, ev(2), [pid])]
    notes = []
    if entry == 2:
        notes.append("Starting-material ee was measured after acetate conversion by chiral GC; product ee was measured by chiral HPLC.")
    unresolved = ["Except where compound-specific data are printed for 4a, substrate/product masses and detailed characterization are not supplied in the main text; complex structures and stereochemical SMILES remain unverified."]
    if entry != 2:
        unresolved.append("The table does not state the yield measurement basis.")
    return rec(
        f"table2_entry{entry}_{product.replace('(', '').replace(')', '').replace('-', '').lower()}",
        "substrate_scope_entry", evidence,
        participants=ps,
        steps=[
            step("carbometallation", [sid, gid, cid, solvent_id], [fld("atmosphere", "nitrogen", ev(4)), fld("initial_temperature", {"number": -78, "unit": "°C"}, evidence), fld("warm_to", {"minimum": 25, "maximum": 30, "unit": "°C", "raw_text": "about 25–30 °C"}, evidence), fld("time", {"number": time_h, "unit": "h"}, ev(3)), fld("operation", "monitored by TLC", ev(4))]),
            step("iodination", [iid, pid], [fld("temperature", {"number": iodine_temp, "unit": "°C"}, evidence), fld("time", {"number": 1, "unit": "h"}, ev(4))]),
            step("workup_and_purification", [pid], [fld("workup", "saturated aqueous Na2S2O3 treatment; Et2O extraction (3 × 30 mL); sequential saturated aqueous Na2S2O3, 5% aqueous HCl, saturated aqueous NaHCO3, and brine washes; anhydrous Na2SO4 drying", ev(4)), fld("purification", "silica-gel column chromatography, petroleum ether/ethyl acetate 60:1–20:1", ev(4))]),
        ], outcomes=outcomes, notes=notes, unresolved=unresolved,
    )


records.extend(scope_record(*row) for row in scope_rows)

records.append(rec(
    "standard_conditions_3butyl_34pentadienol_no_reaction",
    "reported_experiment", ev(3),
    participants=[part("three_butyl_34_pentadienol", "reactant", "3-butyl-3,4-pentadienol", ev(3)), part("expected_product_unknown", "product", "expected carbometallation–iodination product (not specified)", ev(3))],
    outcomes=[fld("reaction_outcome", "no reaction observed", ev(3), ["expected_product_unknown"])],
    notes=["The source states that no reaction was observed under the same reaction conditions."],
    unresolved=["The exact Grignard reagent, quantities, and expected product structure are not restated for this failed case; they were not guessed from context."],
))

# Scheme 4 and detailed page-5 procedure.
e345 = ev(3) + ev(4) + ev(5)
records.append(rec(
    "scheme4_allyl_bromide_coupling_z7",
    "reported_experiment", e345,
    participants=[
        part("one_b_z7", "reactant", "allenol 1b", e345, amounts=[fld("mass", {"number": 0.1427, "unit": "g"}, ev(5)), fld("amount", {"number": 1, "unit": "mmol"}, ev(5))]),
        part("cucl_z7", "reagent", "CuCl", e345, amounts=[fld("mass", {"number": 0.2007, "unit": "g"}, ev(5)), fld("amount", {"number": 2, "unit": "mmol"}, ev(5)), fld("equivalents", {"number": 2, "unit": "equiv"}, ev(5))]),
        part("ether_z7", "solvent", "anhydrous Et2O", e345, smiles="CCOCC", amounts=[fld("volume", {"number": 1.5, "unit": "mL"}, ev(5))]),
        part("pentyl_mgbr_z7", "reactant", "n-C5H11MgBr", e345, amounts=[fld("volume", {"number": 5, "unit": "mL"}, ev(5)), fld("amount", {"number": 5, "unit": "mmol"}, ev(5)), fld("equivalents", {"number": 5, "unit": "equiv"}, ev(5))]),
        part("allyl_bromide_z7", "reagent", "allyl bromide", e345, smiles="C=CCBr", amounts=[fld("volume", {"number": 0.43, "unit": "mL"}, ev(5)), fld("mass", {"number": 0.6, "unit": "g"}, ev(5)), fld("amount", {"number": 5, "unit": "mmol"}, ev(5))]),
        part("z7", "product", "(Z)-4-allyl-3-butyldec-3-en-2-ol (Z-7)", e345),
    ],
    steps=[
        step("carbometallation", ["one_b_z7", "cucl_z7", "ether_z7", "pentyl_mgbr_z7"], [fld("atmosphere", "nitrogen", ev(5)), fld("initial_temperature", {"number": -78, "unit": "°C"}, ev(5)), fld("warm_to", "r.t.", ev(5)), fld("time", {"number": 10, "unit": "h"}, ev(5)), fld("operation", "monitored by TLC", ev(5))]),
        step("allyl_bromide_coupling", ["allyl_bromide_z7", "z7"], [fld("temperature", "r.t.", ev(4) + ev(5)), fld("time", {"number": 16, "unit": "h"}, ev(5))]),
        step("isolation", ["z7"], [fld("workup", "water and 5% aqueous HCl treatment; Et2O extraction (3 × 30 mL); saturated aqueous NaHCO3 and brine washes; anhydrous Na2SO4 drying", ev(5)), fld("purification", "silica-gel column chromatography, petroleum ether/ethyl acetate 40:1", ev(5))]),
    ],
    outcomes=[fld("isolated_yield", {"number": 52, "unit": "%"}, e345, ["z7"]), fld("product_mass", {"number": 0.1339, "unit": "g"}, ev(5), ["z7"]), fld("yield_measurement_basis", "isolated", e345, ["z7"])],
    unresolved=["The product constitutional and Z-stereochemical SMILES remains unverified."],
))


records.append(rec(
    "scheme5_sonogashira_8a",
    "reported_experiment", ev(4) + ev(5),
    participants=[
        part("four_b_8a", "reactant", "iodide 4b", ev(4) + ev(5), amounts=[fld("mass", {"number": 0.0843, "unit": "g"}, ev(5)), fld("amount", {"number": 0.25, "unit": "mmol"}, ev(5))]),
        part("phenylacetylene_8a", "reactant", "phenylacetylene", ev(4) + ev(5), smiles="C#Cc1ccccc1", amounts=[fld("mass", {"number": 0.0541, "unit": "g"}, ev(5)), fld("amount", {"number": 0.50, "unit": "mmol"}, ev(5))]),
        part("pdpph3_8a", "catalyst", "Pd(PPh3)2Cl2", ev(4) + ev(5), amounts=[fld("mass", {"number": 0.0038, "unit": "g"}, ev(5)), fld("catalyst_loading", {"number": 2, "unit": "mol%"}, ev(5))]),
        part("cui_8a", "catalyst", "CuI", ev(4) + ev(5), amounts=[fld("mass", {"number": 0.0012, "unit": "g"}, ev(5)), fld("catalyst_loading", {"number": 2, "unit": "mol%"}, ev(5))]),
        part("et3n_8a", "reagent", "Et3N", ev(4) + ev(5), smiles="CCN(CC)CC", amounts=[fld("volume", {"number": 1, "unit": "mL"}, ev(5))]),
        part("dmso_8a", "solvent", "DMSO", ev(4) + ev(5), smiles="CS(C)=O", amounts=[fld("volume", {"number": 1, "unit": "mL"}, ev(5))]),
        part("z8a", "product", "(Z)-3-butyl-4-hexyl-6-phenylhex-5-yn-3-en-2-ol (Z-8a)", ev(4) + ev(5)),
    ],
    steps=[step("sonogashira_coupling", ["four_b_8a", "phenylacetylene_8a", "pdpph3_8a", "cui_8a", "et3n_8a", "dmso_8a", "z8a"], [fld("atmosphere", "nitrogen", ev(5)), fld("temperature", {"minimum": 40, "maximum": 45, "unit": "°C", "raw_text": "40–45 °C"}, ev(4) + ev(5)), fld("time", {"number": 48, "unit": "h"}, ev(5)), fld("operation", "monitored by TLC to complete conversion", ev(5))]), step("isolation", ["z8a"], [fld("workup", "cool to room temperature; quench with 5 mL water; separate layers; Et2O extraction (3 × 30 mL); anhydrous Na2SO4 drying", ev(5)), fld("purification", "silica-gel column chromatography, petroleum ether/ethyl acetate 60:1", ev(5))])],
    outcomes=[fld("isolated_yield", {"number": 88, "unit": "%"}, ev(4) + ev(5), ["z8a"]), fld("product_mass", {"number": 0.0684, "unit": "g"}, ev(5), ["z8a"]), fld("yield_measurement_basis", "isolated", ev(4) + ev(5), ["z8a"])],
    unresolved=["The product constitutional and Z-stereochemical SMILES remains unverified."],
))
records.append(rec(
    "scheme5_sonogashira_8b",
    "reported_experiment", ev(4),
    participants=[
        part("four_b_8b", "reactant", "iodide 4b", ev(4)),
        part("one_hexyne_8b", "reactant", "terminal alkyne, R=n-C4H9 (1-hexyne)", ev(4), smiles="CCCCC#C"),
        part("pdpph3_8b", "catalyst", "Pd(PPh3)2Cl2", ev(4)),
        part("cui_8b", "catalyst", "CuI", ev(4)),
        part("et3n_8b", "reagent", "Et3N", ev(4), smiles="CCN(CC)CC"),
        part("dmso_8b", "solvent", "DMSO", ev(4), smiles="CS(C)=O"),
        part("z8b", "product", "Z-8b (R=n-C4H9)", ev(4)),
    ],
    steps=[step("sonogashira_coupling", ["four_b_8b", "one_hexyne_8b", "pdpph3_8b", "cui_8b", "et3n_8b", "dmso_8b", "z8b"], [fld("temperature", {"minimum": 40, "maximum": 45, "unit": "°C", "raw_text": "40–45 °C"}, ev(4))])],
    outcomes=[fld("reported_yield", {"number": 69, "unit": "%"}, ev(4), ["z8b"]), fld("yield_measurement_basis", None)],
    unresolved=["Reactant/catalyst quantities, time, atmosphere, workup, purification, yield basis, and product structure are not reported in the main text; characterization is stated to be in unassociated SI."],
))
records.append(rec(
    "scheme5_carbonylation_9",
    "reported_experiment", ev(4) + ev(5),
    participants=[
        part("four_b_9", "reactant", "iodide 4b", ev(4) + ev(5), amounts=[fld("mass", {"number": 0.0690, "unit": "g"}, ev(5)), fld("amount", {"number": 0.2, "unit": "mmol"}, ev(5))]),
        part("pdpph3_9", "catalyst", "Pd(PPh3)4", ev(4) + ev(5), amounts=[fld("mass", {"number": 0.0117, "unit": "g"}, ev(5)), fld("catalyst_loading", {"number": 5, "unit": "mol%"}, ev(4) + ev(5))]),
        part("k2co3_9", "reagent", "K2CO3", ev(5), smiles="[K+].[K+].[O-]C([O-])=O", amounts=[fld("mass", {"number": 0.0598, "unit": "g"}, ev(5)), fld("amount", {"number": 0.4, "unit": "mmol"}, ev(5))]),
        part("mecn_9", "solvent", "CH3CN", ev(4) + ev(5), smiles="CC#N", amounts=[fld("volume", {"number": 1, "unit": "mL"}, ev(5))]),
        part("co_9", "reagent", "CO", ev(4) + ev(5), smiles="[C-]#[O+]"),
        part("product_9", "product", "3-hexyl-4-butyl-2(5H)-furanone (9)", ev(4) + ev(5)),
    ],
    steps=[step("carbonylation", ["four_b_9", "pdpph3_9", "k2co3_9", "mecn_9", "co_9", "product_9"], [fld("atmosphere", "carbon monoxide, CO balloon", ev(5)), fld("pressure", "1 atm CO", ev(4)), fld("temperature", {"number": 70, "unit": "°C"}, ev(4) + ev(5)), fld("time", {"number": 20, "unit": "h"}, ev(5)), fld("operation", "monitored by TLC to complete conversion", ev(5))]), step("isolation", ["product_9"], [fld("workup", "cool to room temperature; quench with 5 mL water; dilute with 50 mL Et2O; brine wash; anhydrous Na2SO4 drying", ev(5)), fld("purification", "silica-gel column chromatography, petroleum ether/ethyl acetate 20:1", ev(5))])],
    outcomes=[fld("isolated_yield", {"number": 84, "unit": "%"}, ev(4) + ev(5), ["product_9"]), fld("product_mass", {"number": 0.0410, "unit": "g"}, ev(5), ["product_9"]), fld("yield_measurement_basis", "isolated", ev(4) + ev(5), ["product_9"])],
    unresolved=["The lactone candidate structure has not been independently verified against a structure editor."],
))

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")

ids = {r["source_reaction_id"]: r["record_id"] for r in records}
table1_ids = [ids[f"table1_entry{i}"] for i in range(1, 10)]
table2_ids = [r["record_id"] for r in records if r["source_reaction_id"].startswith("table2_entry")]
coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {"page": 1, "state": "attempted", "regions": [
            {"region": "lower-left Scheme 1", "finding": "Two generic propargylic-alcohol carbometallation patterns summarize cited prior work/limitations; classified together as a literature example, not a present-paper experiment.", "evidence_ids": ev(1)},
            {"region": "title, abstract, introduction, and lower-right Results opening", "finding": "Abstract-level claims were not duplicated; the explicit 1a preparation was extracted, while grouped later starting-material preparations continue on page 2.", "evidence_ids": ev(1)},
        ], "record_ids": [ids["scheme1_prior_propargylic_alcohol_carbometallation"], ids["starting_allenol_1a_preparation"], ids["starting_allenols_1b_to_1f_literature_procedure"]], "unresolved": ["Scheme 1 is generic and lacks experiment-level conditions and structures.", "The online SI availability statement does not establish an associated SI file."]},
        {"page": 2, "state": "attempted", "regions": [
            {"region": "top Scheme 2", "finding": "Present-paper reproduction of cited CuI/i-PrMgBr conditions extracted with 12% product and 57% recovered 1a.", "evidence_ids": ev(2)},
            {"region": "middle Table 1 and lower discussion", "finding": "All nine optimization rows extracted independently; prose/table yield conflicts for entries 1 and 4 retained.", "evidence_ids": ev(2)},
            {"region": "upper-left starting-material paragraph", "finding": "Grouped literature-procedure preparations for 1b–f, 1g–h, and (S)-1b retained without inventing individual yields.", "evidence_ids": ev(2)},
        ], "record_ids": [ids["scheme2_reproduction_1a_to_2a"], ids["starting_allenols_1b_to_1f_literature_procedure"], ids["starting_allenols_1g_1h_crabbe_literature_procedure"], ids["starting_s1b_kinetic_resolution_literature_procedure"]] + table1_ids, "unresolved": ["Table 1 yield basis, workups, and purifications are not stated.", "Printed table dashes remain undefined source markers."]},
        {"page": 3, "state": "attempted", "regions": [
            {"region": "upper Scheme 3", "finding": "D2O and I2 quench branches extracted as separate experiments; proposed cyclic intermediate C classified as mechanism; possible minor products 5/6 retained as uncertain context.", "evidence_ids": ev(3)},
            {"region": "middle Table 2 and footnotes", "finding": "All 13 substrate-scope entries extracted independently with row-specific time, yield, iodine-temperature exception, ee data, and 8-equivalent Grignard exceptions.", "evidence_ids": ev(3)},
            {"region": "lower-right prose", "finding": "No-reaction case for 3-butyl-3,4-pentadienol and the allyl-bromide coupling statement were captured without duplicating later detailed evidence.", "evidence_ids": ev(3)},
        ], "record_ids": [ids["scheme3_d2o_quench_e3b"], ids["scheme3_iodination_z4b"], ids["scheme3_cyclic_intermediate_c"], ids["standard_conditions_3butyl_34pentadienol_no_reaction"], ids["scheme4_allyl_bromide_coupling_z7"]] + table2_ids, "unresolved": ["Table 2 generally omits yield basis and compound-specific masses.", "Complex structures and stereochemical SMILES remain unverified."]},
        {"page": 4, "state": "attempted", "regions": [
            {"region": "upper-left Scheme 4", "finding": "Allyl-bromide trapping of intermediate C to Z-7 linked to the detailed page-5 procedure.", "evidence_ids": ev(4)},
            {"region": "right-column Procedure I and 4a/E-3b paragraphs", "finding": "General iodination workup was merged into Table 2 rows; exact 4a and E-3b quantities were merged into their corresponding records.", "evidence_ids": ev(4)},
            {"region": "bottom Scheme 5", "finding": "Two Sonogashira cases (8a, 8b) and one carbonylation case (9) extracted as three independent experiments.", "evidence_ids": ev(4)},
        ], "record_ids": [ids["scheme4_allyl_bromide_coupling_z7"], ids["scheme3_d2o_quench_e3b"], ids["scheme5_sonogashira_8a"], ids["scheme5_sonogashira_8b"], ids["scheme5_carbonylation_9"], table2_ids[0]], "unresolved": ["Procedure I supplies common workup but not compound-specific masses for 4b–m.", "The main text does not give a detailed procedure for 8b."]},
        {"page": 5, "state": "attempted", "regions": [
            {"region": "left column E-3b continuation and Z-7 procedure", "finding": "Cross-page E-3b isolation and full two-stage Z-7 experiment merged into existing Scheme 3/Scheme 4 records.", "evidence_ids": ev(5)},
            {"region": "left-lower/right-upper Sonogashira procedure", "finding": "Exact 8a quantities, 48 h reaction, workup, purification, product mass, and 88% isolated yield extracted.", "evidence_ids": ev(5)},
            {"region": "right-middle carbonylation procedure", "finding": "Exact 4b-to-9 carbonylation quantities, CO atmosphere, workup, purification, mass, and 84% isolated yield extracted.", "evidence_ids": ev(5)},
        ], "record_ids": [ids["scheme3_d2o_quench_e3b"], ids["scheme4_allyl_bromide_coupling_z7"], ids["scheme5_sonogashira_8a"], ids["scheme5_carbonylation_9"]], "unresolved": ["The SI is mentioned but not supplied or explicitly associated; 4b–m and 8b characterization was not imported.", "Complex product connectivity/stereochemistry remains unverified."]},
        {"page": 6, "state": "attempted", "regions": [
            {"region": "both columns, references [1]–[12]", "finding": "Reference list and journal furniture only; no present-paper reaction arrow, table, experimental procedure, result, or condition was found.", "evidence_ids": ev(6)},
        ], "record_ids": [], "unresolved": ["Cited publications were not supplied as associated sources and were not mined for additional experiments."]},
    ],
}
COVERAGE.parent.mkdir(parents=True, exist_ok=True)
COVERAGE.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

tasks = json.loads(TASKS.read_text())
target = {f"{DOC}:page{i}:text" for i in range(1, 7)}
for task in tasks:
    if task["task_id"] in target:
        task["state"] = "attempted"
TASKS.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"records": len(records), "coverage_pages": [p["page"] for p in coverage["pages"]]}, ensure_ascii=False))
