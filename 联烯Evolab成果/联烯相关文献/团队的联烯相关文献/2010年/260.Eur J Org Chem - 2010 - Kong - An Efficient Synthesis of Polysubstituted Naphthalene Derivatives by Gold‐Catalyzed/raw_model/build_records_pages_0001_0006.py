#!/usr/bin/env python3
"""Build the source-linked machine extraction for Kong/Fu/Ma, PDF pages 1-6."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "runs/current/raw_model/records_pages_0001_0006.json"
COVERAGE = ROOT / "runs/current/coverage/pages_0001_0006.json"
TASKS = ROOT / "runs/current/tasks.json"
DOC = "doc_be03b7ebc068e9b9"


def ev(*pages):
    return [item for page in pages for item in (f"{DOC}:page{page}:text", f"{DOC}:page{page}:image")]


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


def participant(entity_id, role, label, evidence, name=None, smiles=None, amounts=()):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence) if name else fact(None, ()),
        "smiles": fact(smiles, evidence) if smiles else fact(None, ()),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": [field(n, v, evidence) for n, v in amounts],
    }


def step(step_id, participant_ids, conditions):
    return {
        "step_id": step_id,
        "participant_ids": list(participant_ids),
        "conditions": conditions,
    }


BASE_UNRESOLVED = [
    "Supporting information was not explicitly supplied or associated; SI-only details were not inferred.",
    "Source structures remain machine-unverified; uncertain or generic structures have null SMILES.",
]


def record(suffix, kind, evidence, participants=(), steps=(), outcomes=(), notes=(), unresolved=()):
    return {
        "record_id": f"{DOC}:{suffix}",
        "document_id": DOC,
        "source_reaction_id": suffix,
        "record_kind": kind,
        "status": "needs_review",
        "completeness": "partial",
        "evidence_ids": list(dict.fromkeys(evidence)),
        "participants": list(participants),
        "steps": list(steps),
        "outcomes": list(outcomes),
        "notes": [fact(note, evidence) for note in notes],
        "review": {
            "method": "model",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": BASE_UNRESOLVED + list(unresolved),
        },
    }


SMILES = {
    "triethylamine": "CCN(CC)CC",
    "DMAP": "CN(C)c1ccncc1",
    "acetic anhydride": "CC(=O)OC(C)=O",
    "diethyl ether": "CCOCC",
    "1,4-dioxane": "O1CCOCC1",
    "acetonitrile": "CC#N",
    "toluene": "Cc1ccccc1",
    "dichloromethane": "ClCCl",
    "acetone": "CC(C)=O",
    "THF": "C1CCOC1",
    "DMF": "CN(C)C=O",
    "water": "O",
    "DMSO": "CS(C)=O",
    "propargyl alcohol": "OCC#C",
    "phenylboronic acid": "OB(O)c1ccccc1",
    "potassium carbonate": "[K+].[K+].[O-]C([O-])=O",
}


def simple(entity_id, role, label, evidence, amounts=(), name=None):
    return participant(entity_id, role, label, evidence, name=name, smiles=SMILES.get(label), amounts=amounts)


records = []

# Page 1: this is explicitly a literature-method map, not a new experiment.
records.append(record(
    "scheme1_known_naphthalene_methods",
    "literature_example",
    ev(1),
    notes=(
        "Scheme 1 summarizes multiple previously known naphthalene syntheses (routes a-g and substitution/coupling); it is not a batch experiment reported in this paper.",
        "Generic R groups, halogen/metal variables, and citation-only arrows were not converted into concrete reactant/product structures.",
    ),
    unresolved=("Generic structures and conditions belong to cited literature and are intentionally not expanded.",),
))

# Page 2: generic prior-work/hypothesis scheme.
records.append(record(
    "scheme2_prior_work_and_proposed_extension",
    "general_scheme",
    ev(2),
    notes=(
        "The upper arrow is the authors' cited prior PtCl2-catalyzed indolyl allenol cyclization; the lower arrow is a generic proposed arene-to-naphthalene extension marked with a question mark.",
        "No source-specific batch, substrate identity, duration, or yield is assigned to the proposed lower transformation.",
    ),
    unresolved=("The generic R-group structures are not fully specified and were not assigned SMILES.",),
))

# Page 2 Scheme 3: two distinct experiments on allenol 1a.
e2 = ev(2)
records.append(record(
    "scheme3_ptcl2_allenol_1a",
    "reported_experiment",
    e2,
    participants=(
        participant("s3_1a", "reactant", "1a", e2, name="1-(2,5-dimethoxyphenyl)-2-phenylbuta-2,3-dienol"),
        simple("s3_ptcl2", "catalyst", "PtCl2", e2, (("reported_loading", {"number": 5, "unit": "mol%"}),)),
        simple("s3_tol", "solvent", "toluene", e2),
        participant("s3_3a", "product", "3a", e2, name="1,4-dimethoxy-6-phenylnaphthalene"),
    ),
    steps=(step("cyclization_attempt", ("s3_1a", "s3_ptcl2", "s3_tol"), (
        field("reaction_time", None, ()), field("temperature", None, ()),
    )),),
    outcomes=(field("reported_yield_3a", {"number": 0, "unit": "%"}, e2, ("s3_3a",)), field("reaction_result", "no reaction; 1a was recovered", e2)),
    unresolved=("The scheme gives no duration, temperature, or recovery percentage.",),
))
records.append(record(
    "scheme3_au_agotf_allenol_1a",
    "reported_experiment",
    e2,
    participants=(
        participant("s3b_1a", "reactant", "1a", e2, name="1-(2,5-dimethoxyphenyl)-2-phenylbuta-2,3-dienol"),
        simple("s3b_au", "catalyst", "AuCl(PPh3)", e2, (("reported_loading", {"number": 5, "unit": "mol%"}),)),
        simple("s3b_ag", "catalyst", "AgOTf", e2, (("reported_loading", {"number": 5, "unit": "mol%"}),)),
        simple("s3b_dcm", "solvent", "dichloromethane", e2),
        participant("s3b_3a", "product", "3a", e2, name="1,4-dimethoxy-6-phenylnaphthalene"),
        participant("s3b_dhf", "product", "depicted 2,5-dihydrofuran cycloisomerization product", e2),
    ),
    steps=(step("cycloisomerization", ("s3b_1a", "s3b_au", "s3b_ag", "s3b_dcm"), (
        field("reaction_time", None, ()), field("temperature", None, ()),
    )),),
    outcomes=(
        field("reported_yield_3a", {"number": 0, "unit": "%"}, e2, ("s3b_3a",)),
        field("reported_yield_dihydrofuran_product", {"number": 33, "unit": "%"}, e2, ("s3b_dhf",)),
    ),
    unresolved=("The scheme gives no duration, temperature, or yield measurement basis for the 33% byproduct.",),
))


def table1_participants(entry, catalyst, solvent):
    items = [
        participant(f"t1e{entry}_2a", "reactant", "2a", e2, name="1-(2,5-dimethoxyphenyl)-2-phenylbuta-2,3-dienyl acetate", amounts=(("amount", {"number": 0.2, "unit": "mmol"}),)),
        participant(f"t1e{entry}_3a", "product", "3a", e2, name="1,4-dimethoxy-6-phenylnaphthalene"),
        simple(f"t1e{entry}_solv", "solvent", solvent, e2),
        participant(f"t1e{entry}_std", "unspecified_agent", "CH2Br2 internal standard", e2),
    ]
    for idx, cat in enumerate(catalyst.split("/"), 1):
        items.append(simple(f"t1e{entry}_cat{idx}", "catalyst", cat, e2))
    return items


t1 = [
    (1, "AuCl3", "1,4-dioxane", 19.6, None, 86, None, None),
    (2, "PtCl2", "1,4-dioxane", None, None, 32, None, None),
    (3, "AuCl(PPh3)/AgOTf", "1,4-dioxane", 11.5, 17, None, None, None),
    (4, "AuCl(PPh3)/AgSbF6", "1,4-dioxane", 11.5, 56, None, None, None),
    (5, "AuCl(PPh3)/AgBF4", "1,4-dioxane", 4, 82, None, 77, None),
    (6, "AuCl(PPh3)/AgBF4", "acetonitrile", 10, None, 79, None, None),
    (7, "AuCl(PPh3)/AgBF4", "toluene", 12, None, None, None, "complicated reaction mixture"),
    (8, "AuCl(PPh3)/AgBF4", "dichloromethane", 12, None, None, None, "complicated reaction mixture"),
]
for entry, catalyst, solvent, hours, nmr_yield, recovery, isolated, qualitative in t1:
    parts = table1_participants(entry, catalyst, solvent)
    ids = [p["entity_id"] for p in parts if p["role"] != "product"]
    conditions = [field("temperature", "r.t.", e2), field("catalyst_system_loading", {"number": 5, "unit": "mol%"}, e2)]
    if hours is not None:
        conditions.append(field("reaction_time", {"number": hours, "unit": "h"}, e2))
        steps = (step("reaction", ids, conditions),)
    else:
        steps = (
            step("room_temperature_stage", ids, (field("temperature", "r.t.", e2), field("reaction_time", {"number": 1.3, "unit": "h"}, e2), field("catalyst_system_loading", {"number": 5, "unit": "mol%"}, e2))),
            step("heated_stage", ids, (field("temperature", {"number": 80, "unit": "°C"}, e2), field("reaction_time", {"number": 17, "unit": "h"}, e2))),
        )
    outcomes = []
    if nmr_yield is not None:
        outcomes += [field("reported_yield_3a", {"number": nmr_yield, "unit": "%"}, e2, (f"t1e{entry}_3a",)), field("yield_measurement_basis", "1H NMR using CH2Br2 as internal standard", e2, (f"t1e{entry}_3a",))]
    if recovery is not None:
        outcomes.append(field("recovered_starting_material_yield", {"number": recovery, "unit": "%"}, e2, (f"t1e{entry}_2a",)))
    if isolated is not None:
        outcomes.append(field("isolated_yield_3a", {"number": isolated, "unit": "%"}, e2, (f"t1e{entry}_3a",)))
    if qualitative:
        outcomes.append(field("reaction_result", qualitative, e2))
    records.append(record(
        f"table1_entry{entry}", "optimization_entry", e2, parts, steps, outcomes,
        notes=("Table 1 reports a 5 mol% catalyst system; for slash-separated systems the page does not unambiguously state whether 5 mol% applies to each component or to the combined system.",),
        unresolved=("Exact catalyst-component loading is ambiguous for slash-separated systems; workup and purification are not reported in the table.",),
    ))

# Page 3 Table 2, with detailed page-6 batches merged for entries 1-5.
e3 = ev(3)
t2 = [
    (1, "2a", "3a", 4, 77), (2, "2b", "3b", 19, 87), (3, "2c", "3c", 11, 85),
    (4, "2d", "3d", 9, 89), (5, "2e", "3e", 6, 86), (6, "2f", "3f", 12, 74),
    (7, "2g", "3g", 17, 84), (8, "2h", "3h", 19, 84), (9, "2i", "3i", 12, 80),
    (10, "2j", "3j", 17, 61),
]
t2_names = {
    "3a": "1,4-dimethoxy-6-phenylnaphthalene", "3b": "6-butyl-1,4-dimethoxynaphthalene",
    "3c": "7-phenylnaphtho[2,1-d][1,3]dioxole", "3d": "7-butylnaphtho[2,1-d][1,3]dioxole",
    "3e": "7-p-tolylnaphtho[2,1-d][1,3]dioxole", "3f": "7-(ethoxymethyl)naphtho[2,1-d][1,3]dioxole",
    "3g": "naphtho[2,1-d][1,3]dioxol-7-ylmethyl acetate", "3h": "1,2-dimethoxy-6-phenylnaphthalene",
    "3i": "6-butyl-1,2,3-trimethoxynaphthalene", "3j": "9-hexyl-7-methylnaphtho[2,1-d][1,3]dioxole",
}
details = {
    1: ((64.0, 0.20), (4.9, 0.01), (2.5, 0.013), 1.0, (40.0, 77), "petroleum ether/ethyl acetate 80:1"),
    2: ((90.7, 0.30), (7.5, 0.015), (3.2, 0.016), 1.5, (63.1, 87), "petroleum ether/ethyl acetate 60:1"),
    3: ((90.5, 0.29), (7.5, 0.015), (3.5, 0.018), 2.0, (61.7, 85), "petroleum ether/ethyl acetate 100:1"),
    4: ((87.1, 0.30), (7.4, 0.015), (3.1, 0.015), 2.0, (61.2, 89), "petroleum ether/ethyl acetate 100:1"),
    5: ((95.4, 0.30), (7.2, 0.015), (3.1, 0.015), 2.0, (66.8, 86), "petroleum ether/ethyl acetate 80:1"),
}
for entry, substrate, product, hours, yield_pct in t2:
    evidence = ev(3, 6) if entry <= 5 else e3
    sub_amounts = []
    au_amounts = [("reported_loading", {"number": 5, "unit": "mol%"})]
    ag_amounts = [("reported_loading", {"number": 5, "unit": "mol%"})]
    solv_amounts = []
    prod_amounts = []
    conditions = [field("temperature", "r.t.", evidence), field("reaction_time", {"number": hours, "unit": "h"}, evidence)]
    if entry in details:
        (smg, smmol), (aumg, aummol), (agmg, agmmol), vol, (pmg, _), purification = details[entry]
        sub_amounts = [("mass", {"number": smg, "unit": "mg"}), ("amount", {"number": smmol, "unit": "mmol"})]
        au_amounts += [("mass", {"number": aumg, "unit": "mg"}), ("amount", {"number": aummol, "unit": "mmol"})]
        ag_amounts += [("mass", {"number": agmg, "unit": "mg"}), ("amount", {"number": agmmol, "unit": "mmol"})]
        solv_amounts = [("volume", {"number": vol, "unit": "mL"})]
        prod_amounts = [("mass", {"number": pmg, "unit": "mg"})]
        conditions += [field("atmosphere", "N2", evidence), field("operation", "stirred until TLC indicated completion", evidence), field("purification", "silica-gel column chromatography; " + purification, evidence)]
    parts = [
        participant(f"t2e{entry}_{substrate}", "reactant", substrate, evidence, amounts=sub_amounts),
        simple(f"t2e{entry}_au", "catalyst", "AuCl(PPh3)", evidence, au_amounts),
        simple(f"t2e{entry}_ag", "catalyst", "AgBF4", evidence, ag_amounts),
        simple(f"t2e{entry}_diox", "solvent", "1,4-dioxane", evidence, solv_amounts),
        participant(f"t2e{entry}_{product}", "product", product, evidence, name=t2_names[product], amounts=prod_amounts),
    ]
    outcomes = [field("isolated_yield" if entry <= 5 else "reported_yield", {"number": yield_pct, "unit": "%"}, evidence, (f"t2e{entry}_{product}",))]
    if entry <= 5:
        outcomes.append(field("yield_measurement_basis", "isolated after chromatography", evidence, (f"t2e{entry}_{product}",)))
    notes = []
    unresolved = ["Entries without a page-5/6 detailed batch lack exact quantities, atmosphere, workup, purification, and an explicit yield basis in the covered pages."] if entry > 5 else []
    if entry in (6, 7):
        notes.append(f"The small table label beside the R6 substituent is visually ambiguous in the source; the record uses {substrate} consistently with the generic substrate series and the precursor preparation on page 5.")
        unresolved.append("The substrate label typography in Table 2 entry 6/7 should be independently checked against SI or a higher-resolution source.")
    records.append(record(f"table2_entry{entry}", "substrate_scope_entry", evidence, parts, (step("gold_cyclization", [p["entity_id"] for p in parts[:-1]], conditions),), outcomes, notes, unresolved))

# Page 3 Scheme 4: electron-poor substrates fail.
for label, solvent in (("2k", "toluene"), ("2l", "1,4-dioxane")):
    parts = [
        participant(f"s4_{label}", "reactant", label, e3),
        simple(f"s4_{label}_au", "catalyst", "AuCl(PPh3)", e3, (("reported_loading", {"number": 5, "unit": "mol%"}),)),
        simple(f"s4_{label}_ag", "catalyst", "AgBF4", e3, (("reported_loading", {"number": 5, "unit": "mol%"}),)),
        simple(f"s4_{label}_solv", "solvent", solvent, e3),
    ]
    records.append(record(
        f"scheme4_{label}_no_reaction", "reported_experiment", e3, parts,
        (step("cyclization_attempt", [p["entity_id"] for p in parts], (field("reaction_time", None, ()), field("temperature", None, ()))),),
        (field("reaction_result", "no reaction", e3),),
        unresolved=("Duration, temperature, recovery, and workup are not shown in Scheme 4.",),
    ))

# Page 3 Scheme 5 is mechanistic, not an experiment.
records.append(record(
    "scheme5_proposed_mechanisms", "mechanism", e3,
    participants=(
        participant("mech_2a", "reactant", "2a", e3), participant("mech_m1", "unspecified_agent", "M1 cyclohexenyl gold species", e3),
        participant("mech_m2", "unspecified_agent", "M2 proposed metal-carbene intermediate", e3), participant("mech_m3", "unspecified_agent", "M3 naphthyl gold intermediate", e3),
        participant("mech_3a", "product", "3a", e3), participant("mech_4a", "product", "4a", e3),
    ),
    notes=("Scheme 5 shows two proposed pathways and catalytic intermediates; arrows and intermediates are not treated as isolated batch experiments or assigned yields.",),
    unresolved=("Mechanistic intermediate structures and ligand/charge details remain proposed and unverified.",),
))

# Page 3 Scheme 6 D2O probe.
parts = [
    participant("d2o_2c", "reactant", "2c", e3),
    simple("d2o_probe", "reagent", "D2O", e3, (("equivalents", {"number": 4.9, "unit": "equiv"}),)),
    simple("d2o_au", "catalyst", "AuCl(PPh3)", e3, (("reported_loading", {"number": 5, "unit": "mol%"}),)),
    simple("d2o_ag", "catalyst", "AgBF4", e3, (("reported_loading", {"number": 5, "unit": "mol%"}),)),
    simple("d2o_solvent", "solvent", "1,4-dioxane", e3),
    participant("d2o_product", "product", "[D1]-3c", e3),
]
records.append(record(
    "scheme6_d2o_probe", "reported_experiment", e3, parts,
    (step("gold_cyclization_with_d2o", [p["entity_id"] for p in parts[:-1]], (field("temperature", "r.t.", e3), field("reaction_time", {"number": 36, "unit": "h"}, e3))),),
    (field("reported_yield_d1_3c", {"number": 42, "unit": "%"}, e3, ("d2o_product",)), field("deuterium_incorporation", {"number": 42, "unit": "%"}, e3, ("d2o_product",))),
    unresolved=("The page does not state the yield measurement basis, exact batch scale, workup, or purification.",),
))

# Page 3 Table 3 NIS optimization; entry 1 is the same batch depicted in Scheme 6.
t3 = [
    (1, 1.0, "1,4-dioxane", "r.t.", 7, 62, "81:19", None),
    (2, 1.5, "1,4-dioxane", "r.t.", 11, 72, "86:14", None),
    (3, 2.0, "1,4-dioxane", "r.t.", 17, 66, "81:19", None),
    (4, 1.5, "THF", "r.t.", 19.5, 56, "84:16", None),
    (5, 1.5, "diethyl ether", "r.t.", 19.5, 20, "83:17", None),
    (6, 1.5, "DMF", "r.t.", 19.5, None, None, 99),
    (7, 1.5, "acetone", "r.t.", 10.5, 64, "91:9", None),
    (8, 1.5, "acetone", {"number": 0, "unit": "°C"}, 21, 77, "94:6", None),
    (9, 1.5, "acetone", {"number": -20, "unit": "°C"}, 22, 71, "93:7", None),
    (10, 2.0, "acetone", {"number": 0, "unit": "°C"}, 15, 64, "94:6", None),
]
for entry, nis_eq, solvent, temp, hours, yld, ratio, recovery in t3:
    parts = [
        participant(f"t3e{entry}_2c", "reactant", "2c", e3),
        simple(f"t3e{entry}_nis", "reagent", "NIS", e3, (("equivalents", {"number": nis_eq, "unit": "equiv"}),)),
        simple(f"t3e{entry}_au", "catalyst", "AuCl(PPh3)", e3, (("reported_loading", {"number": 5, "unit": "mol%"}),)),
        simple(f"t3e{entry}_ag", "catalyst", "AgBF4", e3, (("reported_loading", {"number": 5, "unit": "mol%"}),)),
        simple(f"t3e{entry}_solvent", "solvent", solvent, e3),
        participant(f"t3e{entry}_4c", "product", "4c", e3),
        participant(f"t3e{entry}_3c", "product", "3c", e3),
        participant(f"t3e{entry}_std", "unspecified_agent", "CH2Br2 internal standard", e3),
    ]
    outcomes = []
    if yld is not None:
        outcomes += [
            field("reported_yield_4c", {"number": yld, "unit": "%"}, e3, (f"t3e{entry}_4c",)),
            field("ratio_4c_to_3c", ratio, e3, (f"t3e{entry}_4c", f"t3e{entry}_3c")),
            field("yield_measurement_basis", "1H NMR using CH2Br2 as internal standard", e3, (f"t3e{entry}_4c",)),
        ]
    else:
        outcomes.append(field("recovered_starting_material_yield", {"number": recovery, "unit": "%"}, e3, (f"t3e{entry}_2c",)))
    records.append(record(
        f"table3_entry{entry}", "optimization_entry", e3, parts,
        (step("iodocyclization", [p["entity_id"] for p in parts if p["role"] != "product"], (field("temperature", temp, e3), field("reaction_time", {"number": hours, "unit": "h"}, e3))),),
        outcomes,
        notes=(("This row is also depicted as the NIS experiment in Scheme 6; it is retained once and not duplicated." if entry == 1 else "Table 3 optimization row."),),
        unresolved=("Exact substrate/catalyst amounts, batch scale, workup, and purification are not reported in Table 3.",),
    ))

# Separate prose-only failed reaction of 2a with NIS.
parts = [participant("nis_fail_2a", "reactant", "2a", e3), simple("nis_fail_nis", "reagent", "NIS", e3, (("equivalents", {"number": 1.0, "unit": "equiv"}),)), simple("nis_fail_diox", "solvent", "1,4-dioxane", e3)]
records.append(record(
    "prose_2a_nis_no_reaction", "reported_experiment", e3, parts,
    (step("reaction_attempt", [p["entity_id"] for p in parts], (field("reaction_time", None, ()), field("temperature", None, ()))),),
    (field("reaction_result", "did not proceed", e3),),
    unresolved=("The sentence does not restate catalysts, time, temperature, batch scale, recovery, workup, or purification; these were not inferred from nearby experiments.",),
))

# Page 4 Table 4: each row is a distinct two-stage experiment.
e4 = ev(4)
t4 = [
    (1, "2a", 11, "4a", 84, "100:0", 31, "5a", 58),
    (2, "2b", 12, "4b", 79, "94:6", 14, "5b", 53),
    (3, "2c", 21, "4c", 77, "94:6", 24, "5c", 61),
    (4, "2d", 12, "4d", 89, "95:5", 18, "5d", 67),
    (5, "2e", 16, "4e", 89, "95:5", 14, "5e", 52),
    (6, "2f", 14, "4f", 71, "96:4", 23, "5f", 47),
    (7, "2g", 11, "4g", 62, "100:0", 11, "5g", 48),
    (8, "2h", 12, "4h", 71, "91:9", 37.5, "5h", 43),
    (9, "2i", 11, "4i", 62, "100:0", 32, "5i", 48),
]
for entry, substrate, time1, intermediate, y1, ratio, time2, final, y2 in t4:
    byproduct = "3" + substrate[-1]
    nis_eq = 1.56 if entry == 7 else 1.5
    parts = [
        participant(f"t4e{entry}_{substrate}", "reactant", substrate, e4),
        simple(f"t4e{entry}_nis", "reagent", "NIS", e4, (("equivalents", {"number": nis_eq, "unit": "equiv"}),)),
        simple(f"t4e{entry}_au", "catalyst", "AuCl(PPh3)", e4, (("reported_loading", {"number": 5, "unit": "mol%"}),)),
        simple(f"t4e{entry}_ag", "catalyst", "AgBF4", e4, (("reported_loading", {"number": 5, "unit": "mol%"}),)),
        simple(f"t4e{entry}_acetone", "solvent", "acetone", e4),
        participant(f"t4e{entry}_{intermediate}", "product", intermediate, e4),
        participant(f"t4e{entry}_{byproduct}", "product", byproduct, e4),
        simple(f"t4e{entry}_propargyl", "reactant", "propargyl alcohol", e4, (("equivalents", {"number": 2, "unit": "equiv"}),)),
        simple(f"t4e{entry}_pd", "catalyst", "PdCl2(PPh3)2", e4, (("reported_loading", {"number": 2, "unit": "mol%"}),)),
        simple(f"t4e{entry}_cui", "catalyst", "CuI", e4, (("reported_loading", {"minimum": 2, "maximum": 4, "unit": "mol%", "raw_text": "2-4 mol%"}),)),
        simple(f"t4e{entry}_dmso", "solvent", "DMSO", e4),
        simple(f"t4e{entry}_tea", "solvent", "triethylamine", e4),
        participant(f"t4e{entry}_{final}", "product", final, e4),
        participant(f"t4e{entry}_std", "unspecified_agent", "CH2Br2 internal standard", e4),
    ]
    stage1 = [f"t4e{entry}_{substrate}", f"t4e{entry}_nis", f"t4e{entry}_au", f"t4e{entry}_ag", f"t4e{entry}_acetone"]
    stage2 = [f"t4e{entry}_{intermediate}", f"t4e{entry}_propargyl", f"t4e{entry}_pd", f"t4e{entry}_cui", f"t4e{entry}_dmso", f"t4e{entry}_tea"]
    outcomes = [
        field("stage_1_yield_iodonaphthalene", {"number": y1, "unit": "%"}, e4, (f"t4e{entry}_{intermediate}",)),
        field("stage_1_yield_measurement_basis", "1H NMR using CH2Br2 as internal standard", e4, (f"t4e{entry}_{intermediate}",)),
        field("ratio_4_to_3", ratio, e4, (f"t4e{entry}_{intermediate}", f"t4e{entry}_{byproduct}")),
        field("combined_isolated_yield_final_product", {"number": y2, "unit": "%"}, e4, (f"t4e{entry}_{final}",)),
    ]
    notes = ["The reported final yield is a combined isolated yield over both stages from substrate 2; it is not the isolated yield of stage 2 alone."]
    if entry == 7:
        outcomes.append(field("isolated_yield_4g", {"number": 60, "unit": "%"}, e4, (f"t4e{entry}_{intermediate}",)))
        notes.append("For 4g, the more precise NIS loading printed in Scheme 7 overrides the rounded common loading in the Table 4 header; isolated and NMR yields are retained separately.")
    if entry == 9:
        outcomes.append(field("isolated_yield_4i", {"number": 50, "unit": "%"}, e4, (f"t4e{entry}_{intermediate}",)))
        notes.append("Scheme 7 additionally gives 50% isolated 4i for the same 11 h conditions; Table 4 reports 62% NMR yield.")
    records.append(record(
        f"table4_entry{entry}", "substrate_scope_entry", e4, parts,
        (
            step("gold_iodocyclization", stage1, (field("temperature", {"number": 0, "unit": "°C"}, e4), field("reaction_time", {"number": time1, "unit": "h"}, e4))),
            step("sonogashira_coupling", stage2, (field("temperature", {"number": 40, "unit": "°C"}, e4), field("reaction_time", {"number": time2, "unit": "h"}, e4), field("DMSO_Et3N_ratio", "1:1", e4))),
        ), outcomes, notes,
        unresolved=("The table does not provide exact batch masses/volumes, atmosphere, workup, or purification for either stage in the covered pages.",),
    ))

# Scheme 7 4a is a different batch from Table 4 entry 1 (20 h/75% isolated vs 11 h/84% NMR).
parts = [
    participant("s7_2a", "reactant", "2a", e4),
    simple("s7_nis", "reagent", "NIS", e4, (("equivalents", {"number": 1.5, "unit": "equiv"}),)),
    simple("s7_au", "catalyst", "AuCl(PPh3)", e4, (("reported_loading", {"number": 5, "unit": "mol%"}),)),
    simple("s7_ag", "catalyst", "AgBF4", e4, (("reported_loading", {"number": 5, "unit": "mol%"}),)),
    simple("s7_acetone", "solvent", "acetone", e4), participant("s7_4a", "product", "4a", e4, name="6-iodo-1,4-dimethoxy-7-phenylnaphthalene"),
]
records.append(record(
    "scheme7_4a_isolated_batch", "reported_experiment", e4, parts,
    (step("iodocyclization", [p["entity_id"] for p in parts[:-1]], (field("temperature", {"number": 0, "unit": "°C"}, e4), field("reaction_time", {"number": 20, "unit": "h"}, e4))),),
    (field("isolated_yield_4a", {"number": 75, "unit": "%"}, e4, ("s7_4a",)), field("yield_measurement_basis", "isolated yield", e4, ("s7_4a",))),
    unresolved=("Exact batch quantities, atmosphere, workup, and purification are not present on page 4.",),
))

# Page 4 Scheme 8: four distinct downstream couplings.
scheme8 = [
    ("6a", "phenylboronic acid", "Pd(PPh3)4", ["TBAB", "potassium carbonate"], ["THF", "water"], "reflux", 19, 80),
    ("7a", "PhB(OH)2 (as printed above the arrow)", "Pd(PPh3)4", ["TBAB", "potassium carbonate"], ["THF", "water"], "reflux", 12, 85),
    ("8a", "depicted (E)-styrylboronic acid", "Pd(PPh3)4", ["TBAB", "potassium carbonate"], ["THF", "water"], "reflux", 17, 73),
    ("9a", "PMP-ethyne", "PdCl2(PPh3)2", ["CuI"], ["DMSO", "triethylamine"], {"number": 40, "unit": "°C"}, 14, 91),
]
for product, coupling_partner, pdcat, additives, solvents, temp, hours, yld in scheme8:
    prefix = f"s8_{product}"
    parts = [participant(prefix + "_4a", "reactant", "4a", e4), participant(prefix + "_partner", "reactant", coupling_partner, e4)]
    parts.append(simple(prefix + "_pd", "catalyst", pdcat, e4))
    for i, additive in enumerate(additives):
        role = "catalyst" if additive == "CuI" else "reagent"
        parts.append(simple(prefix + f"_add{i}", role, additive, e4))
    for i, solvent in enumerate(solvents):
        parts.append(simple(prefix + f"_solv{i}", "solvent", solvent, e4))
    parts.append(participant(prefix + "_product", "product", product, e4))
    cond = [field("temperature", temp, e4), field("reaction_time", {"number": hours, "unit": "h"}, e4)]
    if product == "9a":
        cond.append(field("DMSO_Et3N_ratio", "1:1", e4))
    notes = []
    unresolved = ["Scheme 8 does not state exact batch quantities, catalyst loadings, atmosphere, workup, purification, or yield basis on page 4."]
    if product == "7a":
        notes.append("The arrow text appears as PhB(OH)2, whereas the drawn 7a product bears a p-methoxyphenyl group; the reagent identity is retained as printed and flagged rather than silently corrected from later pages.")
        unresolved.append("Reagent label/product substituent mismatch for the 7a arrow requires independent source review.")
    records.append(record(
        f"scheme8_to_{product}", "reported_experiment", e4, parts,
        (step("pd_coupling", [p["entity_id"] for p in parts[:-1]], cond),),
        (field(f"reported_yield_{product}", {"number": yld, "unit": "%"}, e4, (prefix + "_product",)),),
        notes, unresolved,
    ))

# Pages 5-6: independent acetylation batches preparing substrates 2a-2j.
prep_data = [
    ("a", 5, "1-(2,5-dimethoxyphenyl)-2-phenylbuta-2,3-dienyl acetate", (0.5645, 2.0), 0.5, (49.5, 0.41), (0.7524, 7.4, None), 8, (0.5421, 84), "petroleum ether/ethyl acetate 10:1"),
    ("b", 5, "1-(2,5-dimethoxyphenyl)-2-vinylidenehexyl acetate", (1.5410, 5.9), 3.4, (143.2, 11.7), (2.3804, 23, 2.2), 40, (1.4970, 84), "petroleum ether/ethyl acetate 10:1"),
    ("c", 5, "1-(benzo[d][1,3]dioxol-5-yl)-2-phenylbuta-2,3-dienyl acetate", (2.6615, 10), 5.0, (244.1, 2.0), (4.3280, 42.4, 4.0), 40, (2.0649, 67), "petroleum ether/ethyl acetate 10:1"),
    ("d", 5, "1-(benzo[d][1,3]dioxol-5-yl)-2-vinylidenehexyl acetate", (0.4901, 2.0), 1.0, (49.6, 0.41), (0.7201, 7.1, None), 10, (0.3400, 59), "petroleum ether/ethyl acetate 20:1"),
    ("e", 5, "1-(benzo[d][1,3]dioxol-5-yl)-2-p-tolylbuta-2,3-dienyl acetate", (1.4257, 5.1), 2.5, (125.1, 1.0), (1.9102, 18.7, None), 20, (1.1896, 73), "petroleum ether/ethyl acetate 80:1 to 40:1"),
    ("f", 5, "1-(benzo[d][1,3]dioxol-5-yl)-2-(ethoxymethyl)buta-2,3-dienyl acetate", (0.6011, 2.4), 0.5, (25.0, 0.2), (0.9125, 8.9, None), 10, (0.5887, 84), "petroleum ether/ethyl acetate 20:1 to 10:1"),
    ("g", 5, "1-(benzo[d][1,3]dioxol-5-yl)-2-vinylidenepropane-1,3-diyl diacetate", (0.3764, 1.7), 0.5, (42.5, 0.35), (0.6752, 6.6, None), 8, (0.4041, 78), "petroleum ether/ethyl acetate 10:1"),
    ("h", 6, "1-(3,4-dimethoxyphenyl)-2-phenylbuta-2,3-dienyl acetate", (1.0012, 3.6), 1.0, (86.4, 0.71), (1.2912, 12.7, None), 15, (0.9508, 83), "petroleum ether/ethyl acetate 10:1"),
    ("i", 6, "1-(3,4,5-trimethoxyphenyl)-2-vinylidenehexyl acetate", (0.8474, 2.9), 1.0, (70.0, 0.57), (1.1012, 10.8, None), 10, (0.8564, 88), "petroleum ether/ethyl acetate 10:1"),
    ("j", 6, "1-(benzo[d][1,3]dioxol-5-yl)-2-methyldeca-2,3-dienyl acetate", (0.8654, 3.0), 1.0, (74.9, 0.61), (1.0210, 10.0, None), 10, (0.7566, 77), "petroleum ether/ethyl acetate 40:1"),
]
for letter, page, product_name, (start_g, start_mmol), tea_ml, (dmap_mg, dmap_mmol), (ac2o_g, ac2o_mmol, ac2o_ml), ether_ml, (product_g, yld), chromatography in prep_data:
    evidence = ev(5, 6) if letter == "g" or page == 6 else ev(5)
    prefix = f"prep2{letter}"
    start_name = "1-(2,5-dimethoxyphenyl)-2-phenylbuta-2,3-dienol" if letter == "a" else None
    ac2o_amounts = [("mass", {"number": ac2o_g, "unit": "g"}), ("amount", {"number": ac2o_mmol, "unit": "mmol"})]
    if ac2o_ml is not None:
        ac2o_amounts += [("volume", {"number": ac2o_ml, "unit": "mL"}), ("reported_density", "1.082 g/mL")]
    parts = [
        participant(prefix + "_start", "reactant", "1" + letter, evidence, name=start_name, amounts=(("mass", {"number": start_g, "unit": "g"}), ("amount", {"number": start_mmol, "unit": "mmol"}))),
        simple(prefix + "_tea", "reagent", "triethylamine", evidence, (("volume", {"number": tea_ml, "unit": "mL"}),)),
        simple(prefix + "_dmap", "reagent", "DMAP", evidence, (("mass", {"number": dmap_mg, "unit": "mg"}), ("amount", {"number": dmap_mmol, "unit": "mmol"}))),
        simple(prefix + "_ac2o", "reagent", "acetic anhydride", evidence, ac2o_amounts),
        simple(prefix + "_ether", "solvent", "diethyl ether", evidence, (("volume", {"number": ether_ml, "unit": "mL"}),)),
        participant(prefix + "_product", "product", "2" + letter, evidence, name=product_name, amounts=(("mass", {"number": product_g, "unit": "g"}),)),
        simple(prefix + "_nahco3", "reagent", "saturated aqueous NaHCO3", evidence),
        simple(prefix + "_na2so4", "reagent", "anhydrous Na2SO4", evidence),
    ]
    conditions = (
        field("temperature", "r.t.", evidence),
        field("reaction_time", None, ()),
        field("operation", "stirred until complete as monitored by TLC", evidence),
        field("workup", "quenched with saturated aqueous NaHCO3; extracted with diethyl ether; organic layers washed with water and dried over anhydrous Na2SO4; filtered and evaporated", evidence),
        field("purification", "silica-gel column chromatography; " + chromatography, evidence),
    )
    notes = ["The abbreviated batch states 'according to the general procedure'; shared room-temperature reaction, TLC endpoint, workup, and silica-gel purification operations were linked from the representative 2a procedure on page 5."] if letter != "a" else []
    unresolved = ["Reaction duration is reported only as 'until complete' and remains missing as a numeric time."]
    if letter == "b":
        notes.append("The page prints DMAP as 143.2 mg and 11.7 mmol; both values are preserved without correcting the apparent mass/amount inconsistency.")
        unresolved.append("The printed DMAP mass and mmol for 2b are internally inconsistent and require source/SI review.")
    records.append(record(
        f"preparation_2{letter}", "reported_experiment", evidence, parts,
        (step("acetylation", [p["entity_id"] for p in parts[:5]], conditions),),
        (field("isolated_yield", {"number": yld, "unit": "%"}, evidence, (prefix + "_product",)), field("yield_measurement_basis", "isolated after chromatography", evidence, (prefix + "_product",))),
        notes, unresolved,
    ))


OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")

ids = lambda *suffixes: [f"{DOC}:{suffix}" for suffix in suffixes]
coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1,
            "state": "attempted",
            "regions": [
                {"region": "title, abstract, and introduction", "finding": "Article-level scope and context only; no individual batch experiment is specified.", "evidence_ids": ev(1)},
                {"region": "lower Scheme 1", "finding": "Map of cited known naphthalene methodologies a-g and substitution/coupling routes; classified as literature context, not experiments of this paper.", "evidence_ids": ev(1)},
            ],
            "record_ids": ids("scheme1_known_naphthalene_methods"),
            "unresolved": ["Generic cited structures and conditions were not expanded into source-paper experiments."],
        },
        {
            "page": 2,
            "state": "attempted",
            "regions": [
                {"region": "left-column Scheme 2", "finding": "Prior PtCl2 indolyl-allenol cyclization plus a question-marked generic arene extension; classified as prior/general scheme.", "evidence_ids": ev(2)},
                {"region": "upper-right Scheme 3", "finding": "Two distinct allenol 1a experiments: PtCl2 gives no 3a/no reaction; AuCl(PPh3)/AgOTf gives 0% 3a and 33% depicted dihydrofuran product.", "evidence_ids": ev(2)},
                {"region": "right-column Table 1 and footnotes", "finding": "Eight separate catalyst/solvent optimization rows extracted, retaining NMR versus isolated yield, recovery, staged temperature program, and complicated-mixture outcomes.", "evidence_ids": ev(2)},
            ],
            "record_ids": ids("scheme2_prior_work_and_proposed_extension", "scheme3_ptcl2_allenol_1a", "scheme3_au_agotf_allenol_1a", *[f"table1_entry{i}" for i in range(1, 9)]),
            "unresolved": ["Scheme 3 omits duration and temperature; slash-separated Table 1 catalyst component loadings are ambiguous beyond the reported 5 mol% catalyst-system notation."],
        },
        {
            "page": 3,
            "state": "attempted",
            "regions": [
                {"region": "upper-left Table 2 and footnote", "finding": "Ten independent gold-cyclization scope rows extracted; entries 1-5 were linked to their detailed page-6 batches.", "evidence_ids": ev(3)},
                {"region": "middle-left Scheme 4", "finding": "Electron-poor substrates 2k and 2l each give no reaction under the depicted Au/Ag conditions; retained as separate failed experiments.", "evidence_ids": ev(3)},
                {"region": "lower-left Scheme 5", "finding": "Two proposed mechanistic pathways through M1/M2/M3; classified as mechanism, not isolated experimental stages.", "evidence_ids": ev(3)},
                {"region": "upper-right Scheme 6 and adjacent prose", "finding": "D2O mechanistic probe extracted; the NIS/2c arrow is reconciled with Table 3 entry 1; a separate prose-only 2a/NIS no-reaction result is retained.", "evidence_ids": ev(3)},
                {"region": "lower-right Table 3 and footnotes", "finding": "Ten NIS optimization rows extracted independently, including 4c/3c ratios, 0 and -20 °C, NMR basis, and 99% recovery in DMF.", "evidence_ids": ev(3)},
            ],
            "record_ids": ids(*[f"table2_entry{i}" for i in range(1, 11)], "scheme4_2k_no_reaction", "scheme4_2l_no_reaction", "scheme5_proposed_mechanisms", "scheme6_d2o_probe", *[f"table3_entry{i}" for i in range(1, 11)], "prose_2a_nis_no_reaction"),
            "unresolved": ["Table-only batches omit exact quantities/workups; Table 2 entry 6/7 label typography is ambiguous; prose-only 2a/NIS failure omits most conditions."],
        },
        {
            "page": 4,
            "state": "attempted",
            "regions": [
                {"region": "upper-left Scheme 7", "finding": "4a isolated batch extracted separately from Table 4 entry 1; 4g and 4i isolated yields reconciled into Table 4 entries 7 and 9.", "evidence_ids": ev(4)},
                {"region": "upper-right Table 4 and two-stage arrow", "finding": "Nine separate iodocyclization/Sonogashira rows extracted with stage times, NMR intermediate yields, 4/3 ratios, and combined isolated final yields.", "evidence_ids": ev(4)},
                {"region": "lower Scheme 8", "finding": "Four distinct Pd-catalyzed transformations of 4a to 6a-9a extracted; arrow conditions and yields retained independently.", "evidence_ids": ev(4)},
                {"region": "mechanistic discussion and conclusions", "finding": "Narrative mechanism refers back to Scheme 5 and was not duplicated; conclusions contain no new batch.", "evidence_ids": ev(4)},
            ],
            "record_ids": ids(*[f"table4_entry{i}" for i in range(1, 10)], "scheme7_4a_isolated_batch", "scheme8_to_6a", "scheme8_to_7a", "scheme8_to_8a", "scheme8_to_9a"),
            "unresolved": ["Scheme 8 omits exact quantities/loadings and yield basis; the printed 7a reagent label conflicts with the drawn p-methoxyphenyl product."],
        },
        {
            "page": 5,
            "state": "attempted",
            "regions": [
                {"region": "top-left representative general procedure for 2a", "finding": "Detailed acetylation of 1a to 2a extracted with quantities, TLC endpoint, workup, chromatography, mass, and isolated yield.", "evidence_ids": ev(5)},
                {"region": "remaining page preparations 2b-2g", "finding": "Six abbreviated substrate-preparation batches extracted separately and linked to the representative operations; the 2g characterization continues on page 6.", "evidence_ids": ev(5)},
                {"region": "spectroscopic and analytical paragraphs", "finding": "Characterization supports compound identity context but was not interpreted as additional reaction experiments.", "evidence_ids": ev(5)},
            ],
            "record_ids": ids(*[f"preparation_2{x}" for x in "abcdefg"]),
            "unresolved": ["All acetylation durations are only 'until complete'; printed 2b DMAP mass/mmol values are internally inconsistent."],
        },
        {
            "page": 6,
            "state": "attempted",
            "regions": [
                {"region": "top-left continuation of 2g", "finding": "Continuation contains only characterization for the page-5 2g batch and is linked to that existing record.", "evidence_ids": ev(6)},
                {"region": "left-column preparations 2h-2j", "finding": "Three independent acetylation batches extracted with quantities, purification, product mass, and isolated yield.", "evidence_ids": ev(6)},
                {"region": "lower-left and right-column preparations 3a-3e", "finding": "Detailed Au/Ag cyclization batches merged into Table 2 entries 1-5; exact batch quantities, N2 atmosphere, time, purification, mass, and isolated yield retained without duplicate records.", "evidence_ids": ev(6)},
                {"region": "analytical data and cross-page boundary", "finding": "Spectral data were not treated as new reactions; 3e characterization continues on page 7, which is outside this coverage claim.", "evidence_ids": ev(6)},
            ],
            "record_ids": ids("preparation_2g", "preparation_2h", "preparation_2i", "preparation_2j", *[f"table2_entry{i}" for i in range(1, 6)]),
            "unresolved": ["Page 7 continuation was not claimed as covered; no characterization fields beyond page 6 were imported."],
        },
    ],
}
COVERAGE.parent.mkdir(parents=True, exist_ok=True)
COVERAGE.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

tasks = json.loads(TASKS.read_text())
for task in tasks:
    if task.get("document_id") == DOC and task.get("task_id", "").split(":page")[-1].split(":")[0].isdigit():
        page = int(task["task_id"].split(":page")[-1].split(":")[0])
        if 1 <= page <= 6:
            task["state"] = "attempted"
            task["reason"] = "Original page image and text inspected; experiments reconciled into source-linked records and coverage ledger."
TASKS.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"records": len(records), "coverage_pages": len(coverage["pages"]), "output": str(OUT.relative_to(ROOT))}, ensure_ascii=False))
