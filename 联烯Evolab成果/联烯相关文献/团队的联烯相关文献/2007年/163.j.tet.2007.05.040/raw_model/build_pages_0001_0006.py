#!/usr/bin/env python3
"""Build evidence-linked machine records for doc_e90694bb0bb41003, PDF pages 1--6."""

import json
from pathlib import Path


DOC = "doc_e90694bb0bb41003"
OUT = Path(__file__).with_name("pages_0001_0006_records.json")


def img(page):
    return f"{DOC}:page{page}:image"


def fact(value, evidence):
    return {
        "value": value,
        "evidence_ids": list(dict.fromkeys(evidence)) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def field(name, value, evidence, targets=None):
    item = {"name": name, "fact": fact(value, evidence)}
    if targets:
        item["target_entity_ids"] = targets
    return item


def participant(entity_id, role, label, name, evidence, smiles=None, amounts=None):
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


def record(suffix, source_id, kind, evidence, participants, steps, outcomes, notes, unresolved):
    evidence = list(dict.fromkeys(evidence))
    return {
        "record_id": f"{DOC}:{suffix}",
        "document_id": DOC,
        "source_reaction_id": source_id,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": evidence,
        "participants": participants,
        "steps": steps,
        "outcomes": outcomes,
        "notes": [fact(note, evs) for note, evs in notes],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved,
        },
    }


def step(step_id, participant_ids, conditions):
    return {"step_id": step_id, "participant_ids": participant_ids, "conditions": conditions}


records = []

# Page 2: cited background chemistry and the paper's retrosynthetic design.
for suffix, source_id, start, product, operation, note in [
    ("lit_scheme2_11_to_12_thermal", "Scheme 2, thermal allenene cycloaddition", "allenene 11", "methylenecyclobutane derivative 12", "thermal initiation (Δ)", "Generic, previously documented intramolecular [2+2]-cycloaddition of an allenene."),
    ("lit_scheme2_11_to_13_photochemical", "Scheme 2, photochemical allenene cycloaddition", "allenene 11", "methylenecyclobutane derivative 13", "photochemical irradiation (hν)", "Generic, previously documented photochemical intramolecular [2+2]-cycloaddition; X is shown as C=O for 13."),
    ("lit_scheme2_14_to_15_ohno", "Scheme 2, allenyne 14 to azabicycle 15", "allenyne 14", "azabicyclo[4.2.0]octadiene 15", "thermal [2+2]-cycloaddition", "Prior work attributed in the prose to Ohno et al.; no numerical conditions or yield are supplied here."),
]:
    ev = [img(2)]
    ps = [
        participant("substrate", "reactant", start.split()[-1], start, ev),
        participant("product", "product", product.split()[-1], product, ev),
    ]
    records.append(record(
        suffix, source_id, "literature_example", ev, ps,
        [step("cycloaddition", ["substrate", "product"], [field("operation", operation, ev), field("time", None, [])])],
        [field("reported_yield", None, [], ["product"])], [(note, ev)],
        ["Generic structures contain variable groups and were not converted to SMILES.", "Exact scale, solvent, time, temperature, workup, purification, and yield are not reported in this source."],
    ))

ev = [img(2)]
records.append(record(
    "general_scheme2_retrosynthetic_design", "Scheme 2, retrosynthetic relationship 2 + 1 to 16", "general_scheme", ev,
    [
        participant("cyclobutene_2", "reactant", "2", "cyclobutene unit 2", ev),
        participant("dihydropyranone_1", "reactant", "1", "5,6-dihydropyran-2-one unit 1", ev),
        participant("target_16", "product", "16", "propargylic 2,3-allenoate target/substrate class 16", ev),
    ],
    [step("retrosynthetic_design", ["cyclobutene_2", "dihydropyranone_1", "target_16"], [field("operation", "retrosynthetic design shown with retrosynthetic arrows", ev)])],
    [], [("This is a conceptual design relationship, not a reported experiment or isolated-yield claim.", ev)],
    ["The generic structures are not fully specified and have no SMILES."],
))

# Prose-only prior-work summaries on page 2.
for suffix, source_id, substrate_name, product_name, conditions in [
    ("lit_shen_moco6_gem_difluoro_allenyne", "Page 2 prose, Shen and Hammond", "electron-withdrawing gem-difluoro-substituted allenyne", "[2+2]-cycloaddition product", ["Mo(CO)6-mediated"]),
    ("lit_oh_pd_or_microwave_allenyne", "Page 2 prose, Oh et al.", "allenyne", "[2+2]-cycloaddition product", ["Pd-catalyzed or microwave-mediated"]),
]:
    ps = [
        participant("substrate", "reactant", None, substrate_name, ev),
        participant("product", "product", None, product_name, ev),
    ]
    if suffix.startswith("lit_shen"):
        ps.append(participant("moco6", "unspecified_agent", "Mo(CO)6", "molybdenum hexacarbonyl", ev))
    records.append(record(
        suffix, source_id, "literature_example", ev, ps,
        [step("reported_prior_transformation", [p["entity_id"] for p in ps], [field("operation", conditions[0], ev), field("time", None, []), field("temperature", None, [])])],
        [field("reported_yield", None, [], ["product"])],
        [("The current paper summarizes this prior work without substrate-specific conditions or yield.", ev)],
        ["Specific structures, scale, solvent, time, temperature, workup, purification, and yield are absent."],
    ))

# Brummond and Chen's specific prior-literature example at the bottom of Scheme 2.
ps = [
    participant("substrate", "reactant", None, "but-2-ynyl nona-2,3-dienoate", ev),
    participant("product_47", "product", None, "7-methyl-8-pentyl-3-oxabicyclo[4.2.0]octa-1(8),5-dien-4-one", ev),
    participant("byproduct_28", "product", None, "5-ethylidene-4-hex-1-enyl-5,6-dihydropyran-2-one", ev),
    participant("toluene", "solvent", "toluene", "toluene", ev, "Cc1ccccc1"),
    participant("ionic_liquid", "unspecified_agent", "ionic liquid", "unspecified ionic liquid", ev),
]
records.append(record(
    "lit_brummond_chen_microwave", "Scheme 2, Brummond and Chen microwave example", "literature_example", ev, ps,
    [step("microwave_cycloaddition", [p["entity_id"] for p in ps], [
        field("temperature", {"number": 250, "unit": "°C"}, ev),
        field("operation", "microwave irradiation (MWI)", ev),
        field("solvent", "ionic liquid/toluene", ev),
        field("time", None, []),
    ])],
    [
        field("reported_yield_main_product", {"number": 47, "unit": "%"}, ev, ["product_47"]),
        field("reported_yield_byproduct", {"number": 28, "unit": "%"}, ev, ["byproduct_28"]),
        field("yield_measurement_basis", None, []),
    ],
    [("The scheme prints '3M ionic liquid in toluene'; the ionic-liquid identity and the meaning/basis of '3M' are unresolved and are not forced into a concentration field.", ev)],
    ["Reaction time, scale, atmosphere, workup, purification, and yield basis are not reported in the current source."],
))

# Scheme 3 preliminary trials: keep the two distinct nonstandard outcomes separate.
for label, terminal_r, result in [("16a", "H", "no reaction (NR)"), ("16b", "n-Pr", "complicated reaction")]:
    ev = [img(2)]
    intended = label.replace("16", "17")
    ps = [
        participant("substrate", "reactant", label, f"propargylic 2,3-allenoate {label} (terminal alkynyl substituent R={terminal_r})", ev),
        participant("intended_product", "product", intended, f"intended [2+2]-cycloaddition product {intended}", ev),
        participant("toluene", "solvent", "toluene", "toluene", ev, "Cc1ccccc1"),
    ]
    records.append(record(
        f"scheme3_{label}", f"Scheme 3, {label}", "optimization_entry", ev, ps,
        [step("thermal_trial", [p["entity_id"] for p in ps], [field("temperature", "reflux", ev), field("time", {"number": 24, "unit": "h"}, ev)])],
        [field("reaction_result", result, ev, ["intended_product"]), field("reported_yield", None, [], ["intended_product"])],
        [("This preliminary condition is distinct from the later 16c/Table 1/Table 2 experiment.", ev)],
        ["Scale, solvent volume, atmosphere, detection details, workup, and purification are absent.", "No product structure was assigned beyond the depicted label."],
    ))


product_17c_name = "7,8-diphenyl-5-(n-propyl)-3-oxabicyclo[4.2.0]octa-1(8),5-dien-4-one"
product_18c_name = "10-phenyl-4-propyl-3,4-dihydro-1H-naphtho[2,3-c]pyrane-3-one"

# Table 1 entries 2--4. Entry 1 is the same experiment as Table 2 entry 1 and section 4.1.1.
for entry, solvent_label, solvent_name, smiles, time_h, y17, y18 in [
    (2, "dioxane", "dioxane (isomer not specified by the table)", None, 9, 41, 9),
    (3, "xylene", "xylene (isomer not specified)", None, 2, 61, 9),
    (4, "DMF", "N,N-dimethylformamide", "CN(C)C=O", 2, 52, 8),
]:
    ev = [img(2)]
    ps = [
        participant("substrate_16c", "reactant", "16c", "propargylic 2,3-allenoate 16c", ev),
        participant("product_17c", "product", "17c", product_17c_name, ev),
        participant("product_18c", "product", "18c", product_18c_name, ev),
        participant("solvent", "solvent", solvent_label, solvent_name, ev, smiles),
    ]
    records.append(record(
        f"table1_entry{entry}_{solvent_label.lower()}", f"Table 1 entry {entry}", "optimization_entry", ev, ps,
        [step("solvent_screen", [p["entity_id"] for p in ps], [field("temperature", "reflux", ev), field("time", {"number": time_h, "unit": "h"}, ev)])],
        [
            field("isolated_yield_17c", {"number": y17, "unit": "%"}, ev, ["product_17c"]),
            field("isolated_yield_18c", {"number": y18, "unit": "%"}, ev, ["product_18c"]),
            field("yield_measurement_basis", "isolated yield", ev),
        ], [],
        ["Reaction scale, solvent volume, atmosphere, workup, and purification are not specified for this optimization row."],
    ))


scope_rows = [
    # entry, label, R1, R2, R3, time, main yield, byproduct yield/status, exact page
    (1, "c", "Ph", "n-Pr", "Ph", 4, 65, 13, 4),
    (2, "d", "Ph", "Me", "Ph", 8, 82, "not detected by chromatographic isolation", 4),
    (3, "e", "Ph", "Bn", "Ph", 5, 66, 5, 4),
    (4, "f", "p-BrC6H4", "n-Pr", "Ph", 12, 61, 5, 5),
    (5, "g", "naphthyl", "n-Pr", "Ph", 12, 53, 25, 5),
    (6, "h", "Cyclohexanyl", "H", "Ph", 72, 36, "other unidentified products were found", 5),
    (7, "i", "Ph", "n-Bu", "TMS", 9, 69, "no Diels-Alder reaction products were found", 5),
    (8, "j", "Ph", "n-Pr", "TMS", 8, 74, "no Diels-Alder reaction products were found", 6),
    (9, "k", "Ph", "Et", "TMS", 24, 75, "no Diels-Alder reaction products were found", 6),
    (10, "l", "Ph", "Me", "TMS", 48, 50, "no Diels-Alder reaction products were found", 6),
    (11, "m", "Ph", "Bn", "TMS", 28, 70, "no Diels-Alder reaction products were found", 6),
    (12, "n", "p-BrC6H4", "n-Pr", "TMS", 48, 71, "no Diels-Alder reaction products were found", 6),
    (13, "o", "Ph", "Allyl", "TMS", 44, 64, "no Diels-Alder reaction products were found", None),
    (14, "p", "n-C6H13", "Me", "TMS", 72, 25, "no Diels-Alder reaction products were found", None),
]

exact = {
    "c": (72, 0.25, 6, 47, 9),
    "d": (71, 0.25, 6, 58, None),
    "e": (108, 0.29, 7, 71, 5),
    "f": (96, 0.25, 6, 59, 5),
    "g": (92, 0.25, 6, 49, 23),
    "h": (70, 0.25, 5, 25, None),
    "i": (80, 0.25, 6, 55, None),
    "j": (74, 0.24, 6, 55, None),
    "k": (97, 0.33, 8, 73, None),
    "l": (94, 0.33, 8, 47, None),
    "m": (92, 0.25, 6, 64, None),
    "n": (95, 0.25, 6, 67, None),
}

product_names = {
    "c": product_17c_name,
    "d": "5-methyl-7,8-diphenyl-3-oxabicyclo[4.2.0]octa-1(8),5-dien-4-one",
    "e": "5-benzyl-7,8-diphenyl-3-oxabicyclo[4.2.0]octa-1(8),5-dien-4-one",
    "f": "7-(4-bromophenyl)-8-phenyl-5-propyl-3-oxabicyclo[4.2.0]octa-1(8),5-dien-4-one",
    "g": "7-naphthalen-1-yl-8-phenyl-5-propyl-3-oxabicyclo[4.2.0]octa-1(8),5-dien-4-one",
    "h": "7-cyclohexyl-8-phenyl-3-oxabicyclo[4.2.0]octa-1(8),5-dien-4-one",
    "i": "5-butyl-7-phenyl-8-(trimethylsilyl)-3-oxabicyclo[4.2.0]octa-1(8),5-dien-4-one",
    "j": "7-phenyl-5-propyl-8-(trimethylsilyl)-3-oxabicyclo[4.2.0]octa-1(8),5-dien-4-one",
    "k": "5-ethyl-7-phenyl-8-(trimethylsilyl)-3-oxabicyclo[4.2.0]octa-1(8),5-dien-4-one",
    "l": "5-methyl-7-phenyl-8-(trimethylsilyl)-3-oxabicyclo[4.2.0]octa-1(8),5-dien-4-one",
    "m": "5-benzyl-7-phenyl-8-(trimethylsilyl)-3-oxabicyclo[4.2.0]octa-1(8),5-dien-4-one",
    "n": "7-(4-bromophenyl)-5-propyl-8-(trimethylsilyl)-3-oxabicyclo[4.2.0]octa-1(8),5-dien-4-one",
    "o": "Table 2 product 17o (R1=Ph, R2=allyl, R3=TMS)",
    "p": "Table 2 product 17p (R1=n-C6H13, R2=Me, R3=TMS)",
}

byproduct_names = {
    "c": product_18c_name,
    "e": "10-phenyl-4-benzyl-3,4-dihydro-1H-naphtho[2,3-c]pyrane-3-one",
    "f": "10-phenyl-8-bromo-4-propyl-3,4-dihydro-1H-naphtho[2,3-c]pyrane-3-one",
    "g": "7-phenyl-11-propyl-8,11-dihydro-9-oxabenzo[a]anthracen-10-one",
}

for entry, letter, r1, r2, r3, time_h, y17, secondary, exact_page in scope_rows:
    ev = [img(3)]
    if exact_page:
        ev.append(img(exact_page))
    if letter == "c":
        ev.insert(0, img(2))
    if letter == "f":
        ev.append(img(4))  # reaction drawing begins on page 4; procedure continues on page 5
    if letter == "k":
        ev.append(img(4))  # Figure 2 NOE assignment
    ev = list(dict.fromkeys(ev))
    exact_ev = [img(exact_page)] if exact_page else [img(3)]
    amounts = []
    solvent_amounts = []
    main_amounts = []
    by_amounts = []
    if letter in exact:
        smass, smmol, svol, pmass, bmass = exact[letter]
        amounts = [field("mass", {"number": smass, "unit": "mg"}, exact_ev), field("amount", {"number": smmol, "unit": "mmol"}, exact_ev)]
        solvent_amounts = [field("volume", {"number": svol, "unit": "mL"}, exact_ev)]
        main_amounts = [field("mass", {"number": pmass, "unit": "mg"}, exact_ev)]
        if bmass is not None:
            by_amounts = [field("mass", {"number": bmass, "unit": "mg"}, exact_ev)]
    else:
        # Pages 1--6 only provide the nominal general procedure for these entries.
        amounts = [field("general_procedure_amount", {"number": 0.25, "unit": "mmol"}, [img(3)])]
        solvent_amounts = [field("general_procedure_volume", {"number": 6, "unit": "mL"}, [img(3)])]

    ps = [
        participant("substrate", "reactant", f"16{letter}", f"propargylic 2,3-allenoate 16{letter} (R1={r1}, R2={r2}, R3={r3})", ev, amounts=amounts),
        participant("product_17", "product", f"17{letter}", product_names[letter], ev, amounts=main_amounts),
        participant("toluene", "solvent", "dry toluene", "toluene", ev, "Cc1ccccc1", solvent_amounts),
    ]
    outcomes = [
        field(f"isolated_yield_17{letter}", {"number": y17, "unit": "%"}, [img(3)] if not exact_page else [img(3), img(exact_page)], ["product_17"]),
        field("yield_measurement_basis", "isolated yield", [img(3)]),
    ]

    if isinstance(secondary, int):
        ps.append(participant("product_18", "product", f"18{letter}", byproduct_names[letter], ev, amounts=by_amounts))
        outcomes.append(field(f"isolated_yield_18{letter}", {"number": secondary, "unit": "%"}, [img(3)] if not exact_page else [img(3), img(exact_page)], ["product_18"]))
    elif letter == "d":
        ps.append(participant("product_18", "product", "18d", "corresponding Diels-Alder-aromatization product 18d", [img(3)]))
        outcomes.append(field("Diels_Alder_product_result", secondary, [img(3)], ["product_18"]))
    elif letter == "h":
        ps.append(participant("unidentified_products", "product", None, "other unidentified products", [img(3)]))
        outcomes.append(field("source_marker_for_18_column", "table dash (—)", [img(3)]))
        outcomes.append(field("other_unidentified_product_result", secondary, [img(3)], ["unidentified_products"]))
    else:
        ps.append(participant("diels_alder_product", "product", "18-type", "corresponding Diels-Alder-aromatization product", [img(3)]))
        outcomes.append(field("Diels_Alder_product_result", secondary, [img(3)], ["diels_alder_product"]))

    conditions = [
        field("temperature", "reflux", [img(3)]),
        field("time", {"number": time_h, "unit": "h"}, [img(3)] if not exact_page else [img(3), img(exact_page)]),
        field("atmosphere", "argon", [img(3)] if not exact_page else [img(exact_page)]),
        field("TLC_monitoring", "petroleum ether/ethyl acetate 5:1; until complete conversion", [img(3)]),
        field("workup", "rotary evaporation", [img(3)]),
        field("purification", "flash chromatography on silica gel; petroleum ether/ethyl ether 10:1", [img(3)]),
    ]
    notes = [(f"Table 2 substituents: R1={r1}, R2={r2}, R3={r3}.", [img(3)])]
    if letter == "g":
        notes.append(("The structure of 18g was reported as confirmed by X-ray diffraction (Figure 1).", [img(3)]))
    if letter == "k":
        notes.append(("Figure 2 reports an NOE between aromatic H2 and H1 at δ 4.64 ppm for 17k as structural support.", [img(4)]))
    if letter == "h":
        notes.append(("The table literally prints R1 as 'Cyclohexanyl'; the exact product heading uses cyclohexyl.", [img(3), img(5)]))
    if letter in ("o", "p"):
        notes.append(("Only the nominal page-3 general-procedure scale/volume are available within the bounded pages; no row-specific exact procedure was used.", [img(3)]))
    unresolved = [
        "The substrate/product drawings and stereochemistry have not been independently structure-verified; no SMILES was forced.",
        "Reflux is qualitative; no numerical bath or internal temperature is reported.",
    ]
    if letter in ("o", "p"):
        unresolved.append("Row-specific mass, exact scale, and product mass are absent from pages 1--6; the structured amount/volume are nominal general-procedure values.")
    if letter == "h":
        unresolved.append("The identities, quantities, and yields of the other products are not reported.")
    source_id = f"Table 2 entry {entry}"
    if entry <= 12:
        source_id += f"; section 4.1.{entry}"
    records.append(record(
        f"table2_entry{entry}_16{letter}", source_id, "substrate_scope_entry", ev, ps,
        [step("thermal_intramolecular_2plus2_cycloaddition", [p["entity_id"] for p in ps], conditions)],
        outcomes, notes, unresolved,
    ))


OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"output": str(OUT), "records": len(records)}, ensure_ascii=False))
