#!/usr/bin/env python3
"""Build evidence-linked machine records for source PDF pages 1-6."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "runs/current/raw_model/extracted_records_pages_0001_0006.json"
COVERAGE = ROOT / "runs/current/coverage/pages_0001_0006.json"
TASKS = ROOT / "runs/current/tasks.json"
DOC = "doc_a92716bc66b648fb"


def ev(page: int) -> list[str]:
    return [f"{DOC}:page{page}:image", f"{DOC}:page{page}:text"]


def unique(items):
    return list(dict.fromkeys(items))


def fact(value, evidence=None):
    return {
        "value": value,
        "evidence_ids": unique(evidence or []) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def field(name, value, evidence=None, targets=None):
    item = {"name": name, "fact": fact(value, evidence)}
    if targets:
        item["target_entity_ids"] = targets
    return item


def participant(entity_id, role, label, name, evidence, smiles=None, amounts=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence),
        "smiles": fact(smiles, evidence),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": amounts or [],
    }


def record(rid, kind, evidence, participants, steps, outcomes, notes, unresolved):
    return {
        "record_id": f"{DOC}:{rid}",
        "document_id": DOC,
        "source_reaction_id": rid,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": unique(evidence),
        "participants": participants,
        "steps": steps,
        "outcomes": outcomes,
        "notes": [fact(x, evidence) for x in notes],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved,
        },
    }


def q(number, unit, qualifier=None, raw_text=None):
    value = {"number": number, "unit": unit}
    if qualifier:
        value["qualifier"] = qualifier
    if raw_text:
        value["raw_text"] = raw_text
    return value


def missing_condition(name):
    return field(name, None)


RECORDS = []

# Page 1: explicitly cited prior work, retained as a literature example.
e1 = ev(1)
lit_parts = [
    participant("lit_racemic_allenol", "reactant", "racemic 2,3-allenol", "generic racemic 2,3-allenol (R1 = methyl or ethyl in cited work)", e1),
    participant("lit_vinyl_acetate", "reactant", "AcOCH=CH2", "vinyl acetate", e1, "C=COC(C)=O"),
    participant("lit_novozym435", "catalyst", "Novozym 435", "Novozym 435 (Candida antarctica lipase B formulation)", e1),
    participant("lit_S_allenol", "product", "(S)-2,3-allenol", "generic (S)-2,3-allenol", e1),
    participant("lit_R_acetate", "product", "(R)-2,3-allenyl acetate", "generic (R)-2,3-allenyl acetate", e1),
]
RECORDS.append(record(
    "eq1_prior_work_kinetic_resolution", "literature_example", e1, lit_parts,
    [{"step_id": "resolution", "participant_ids": [p["entity_id"] for p in lit_parts[:3]],
      "conditions": [field("temperature", q(30, "°C"), e1), missing_condition("time")]}],
    [], ["Equation (1) summarizes the authors' previously reported work and cites reference 13."],
    ["Generic R-group structures are not fully specified.", "No experiment-specific time or yields are shown on this page."]
))

# Page 2 Scheme 1 is a retrosynthetic/conceptual sequence, not a reported experiment.
e2 = ev(2)
scheme1_parts = [
    participant("scheme1_target", "product", "target 2,3-allenol", "generic substituted 2,3-allenol", e2),
    participant("scheme1_alkynyl_precursor", "reactant", "1-alkynyl-2,3-allenol precursor", "generic 1-alkynyl-2,3-allenol", e2),
    participant("scheme1_terminal_precursor", "reactant", "1-ethynyl-2,3-allenol precursor", "generic terminal-alkyne allenol", e2),
]
RECORDS.append(record(
    "scheme1_retrosynthetic_concept", "general_scheme", e2, scheme1_parts,
    [{"step_id": "retrosynthetic_relationship", "participant_ids": [p["entity_id"] for p in scheme1_parts], "conditions": []}],
    [], ["Scheme 1 is a retrosynthetic proposal with R-group placeholders."],
    ["No reagents, quantities, conditions, or experimental outcomes are supplied.", "Structures are generic R-group drawings."]
))


STARTING = {
    "1a": dict(sec="3.1.1", page=4, name="(±)-4-(n-butyl)hexa-4,5-dien-1-yn-3-ol", smiles="C=C=C(CCCC)C(O)C#C",
               bromide="1-bromohept-2-yne", bromide_smiles="BrCC#CCCCC", sn=(10.43,55), br=(8.74,50), nai=(8.25,55), dmf=100, aldehyde="propynal", ald_smiles="C#CC=O", ald=(2.18,40), product=(4.46,59)),
    "1b": dict(sec="3.1.2", page=4, name="(±)-4-allylhexa-4,5-dien-1-yn-3-ol", smiles="C=C=C(CC=C)C(O)C#C",
               bromide="5-hexen-2-ynyl bromide", bromide_smiles="BrCC#CCC=C", sn=(4.17,22), br=(3.17,20), nai=(3.30,22), dmf=40, aldehyde="propynal", ald_smiles="C#CC=O", ald=(1.08,20), product=(1.32,49)),
    "1c": dict(sec="3.1.3", page=4, extra_page=5, name="(±)-4-(n-hexyl)hexa-4,5-dien-1-yn-3-ol", smiles="C=C=C(CCCCCC)C(O)C#C",
               bromide="1-bromonon-2-yne", bromide_smiles="BrCC#CCCCCCC", sn=(6.43,34), br=(6.23,31), nai=(5.08,34), dmf=60, aldehyde="propynal", ald_smiles="C#CC=O", ald=(1.70,31), product=(4.04,74)),
    "1d": dict(sec="3.1.4", page=5, name="(±)-4-benzylhexa-4,5-dien-1-yn-3-ol", smiles="C=C=C(Cc1ccccc1)C(O)C#C",
               bromide="4-phenylbut-2-ynyl bromide", bromide_smiles="BrCC#CCc1ccccc1", sn=(2.30,12), br=(2.26,11), nai=(1.82,12), dmf=20, aldehyde="propynal", ald_smiles="C#CC=O", ald=(0.59,11), product=(1.27,63)),
    "1e": dict(sec="3.1.5", page=5, name="(±)-4-(ethoxymethyl)hexa-4,5-dien-1-yn-3-ol", smiles="C=C=C(COCC)C(O)C#C",
               bromide="4-ethoxybut-2-ynyl bromide", bromide_smiles="BrCC#CCOCC", sn=(5.22,28), br=(4.43,25), nai=(4.13,28), dmf=50, aldehyde="propynal", ald_smiles="C#CC=O", ald=(1.35,25), product=(2.58,68)),
    "1f": dict(sec="3.1.6", page=5, name="(±)-4-(2-phenylethyl)hexa-4,5-dien-1-yn-3-ol", smiles="C=C=C(CCc1ccccc1)C(O)C#C",
               bromide="5-phenylpent-2-ynyl bromide", bromide_smiles="BrCC#CCCc1ccccc1", sn=(2.30,12), br=(2.54,11), nai=(1.84,12), dmf=20, aldehyde="propynal", ald_smiles="C#CC=O", ald=(0.59,11), product=(1.27,56)),
    "1g": dict(sec="3.1.7", page=5, name="(±)-4-allylhexa-1,4,5-trien-3-ol", smiles="C=C=C(CC=C)C(O)C=C",
               bromide="5-hexen-2-ynyl bromide", bromide_smiles="BrCC#CCC=C", sn=(4.17,22), br=(3.15,20), nai=(3.38,23), dmf=40, aldehyde="acrolein", ald_smiles="C=CC=O", ald=(1.12,20), product=(1.21,44)),
    "1h": dict(sec="3.1.8", page=5, name="(±)-4-(n-butyl)hexa-1,4,5-trien-3-ol", smiles="C=C=C(CCCC)C(O)C=C",
               bromide="1-bromohept-2-yne", bromide_smiles="BrCC#CCCCC", sn=(6.26,33), br=(5.32,31), nai=(4.95,33), dmf=60, aldehyde="acrolein", ald_smiles="C=CC=O", ald=(1.34,24), product=(2.43,53)),
    "1i": dict(sec="3.1.9", page=5, name="(±)-4-benzylhexa-1,4,5-trien-3-ol", smiles="C=C=C(Cc1ccccc1)C(O)C=C",
               bromide="1-bromo-4-phenylbut-2-yne", bromide_smiles="BrCC#CCc1ccccc1", sn=(3.08,16), br=(2.35,11), nai=(1.88,13), dmf=20, aldehyde="acrolein", ald_smiles="C=CC=O", ald=(0.63,11), product=(1.06,51)),
}


for label, d in STARTING.items():
    evidence = unique(e2 + ev(d["page"]) + (ev(d["extra_page"]) if d.get("extra_page") else []))
    ids = {k: f"{label}_{k}" for k in ("sncl2", "bromide", "nai", "dmf", "aldehyde", "product")}
    parts = [
        participant(ids["sncl2"], "reagent", "SnCl2", "stannous chloride", evidence, "[Cl-].[Cl-].[Sn+2]", [field("mass", q(d["sn"][0], "g"), evidence), field("amount", q(d["sn"][1], "mmol"), evidence)]),
        participant(ids["bromide"], "reactant", d["bromide"], d["bromide"], evidence, d["bromide_smiles"], [field("mass", q(d["br"][0], "g"), evidence), field("amount", q(d["br"][1], "mmol"), evidence)]),
        participant(ids["nai"], "reagent", "NaI", "sodium iodide", evidence, "[Na+].[I-]", [field("mass", q(d["nai"][0], "g"), evidence), field("amount", q(d["nai"][1], "mmol"), evidence)]),
        participant(ids["dmf"], "solvent", "DMF", "N,N-dimethylformamide", evidence, "CN(C)C=O", [field("volume", q(d["dmf"], "mL"), evidence)]),
        participant(ids["aldehyde"], "reactant", d["aldehyde"], d["aldehyde"], evidence, d["ald_smiles"], [field("mass", q(d["ald"][0], "g"), evidence), field("amount", q(d["ald"][1], "mmol"), evidence)]),
        participant(ids["product"], "product", label, d["name"], evidence, d["smiles"]),
    ]
    if label == "1a":
        steps = [
            {"step_id": "premix", "participant_ids": [ids[x] for x in ("sncl2", "bromide", "nai", "dmf")],
             "conditions": [field("temperature", "r.t.", evidence), field("time", q(1, "h"), evidence), field("operation", "stirred", evidence)]},
            {"step_id": "aldehyde_addition_and_reaction", "participant_ids": [ids[x] for x in ("sncl2", "bromide", "nai", "dmf", "aldehyde")],
             "conditions": [field("temperature", q(0, "°C"), evidence), field("time", q(12, "h"), evidence), field("operation", "propynal added after cooling; mixture stirred", evidence), field("workup", "quenched with water; extracted with ether; organic layer washed with saturated NaCl and dried over anhydrous MgSO4", evidence), field("purification", "flash chromatography on silica gel; petroleum ether/ether 15:1", evidence)]},
        ]
        unresolved = ["No explicitly associated Supporting Information was supplied.", "Candidate SMILES are connectivity proposals and remain unverified."]
    else:
        steps = [{"step_id": "reported_reaction", "participant_ids": [ids[x] for x in ("sncl2", "bromide", "nai", "dmf", "aldehyde")],
                  "conditions": [missing_condition("temperature"), missing_condition("time"), field("operation", "reacted to afford the named product", evidence)]}]
        unresolved = ["This individual paragraph does not restate reaction temperature, duration, workup, or purification; these were not imported by inference from the typical procedure.", "No explicitly associated Supporting Information was supplied.", "Candidate SMILES are connectivity proposals and remain unverified."]
    outcomes = [
        field("isolated_product_mass", q(d["product"][0], "g"), evidence, [ids["product"]]),
        field("isolated_yield", q(d["product"][1], "%"), evidence, [ids["product"]]),
    ]
    RECORDS.append(record(f"sec{d['sec']}_{label}_preparation", "reported_experiment", evidence, parts, steps, outcomes, [], unresolved))


RESOLUTION = {
    "1a": ("Ethynyl", "C4H9", 95, 41, (99,"gt"), 46, (97,None), 5, (41,59)),
    "1b": ("Ethynyl", "Allyl", 96, 55, (88,None), 40, (98,None), 5, (55,52)),
    "1c": ("Ethynyl", "C6H13", 96, 38, (97,None), 40, (99,"gt"), 5, (38,49)),
    "1d": ("Ethynyl", "PhCH2", 95, 42, (99,"gt"), 43, (98,None), 6, (42,53)),
    "1e": ("Ethynyl", "CH2OEt", 94.5, 44, (98,None), 42, (98,None), 6, (44,53)),
    "1f": ("Ethynyl", "PhCH2CH2", 94, 40, (99,"gt"), 44, (99,"gt"), 6, (40,53)),
    "1g": ("Ethenyl", "Allyl", 79.5, 39, (99,"gt"), 46, (98,None), 6, (39,61)),
    "1h": ("Ethenyl", "C4H9", 97, 50, (98,None), 46, (98,None), None, (None,None)),
    "1i": ("Ethenyl", "PhCH2", 95, 42, (99,"gt"), 42, (99,"gt"), None, (None,None)),
}


def ee_value(pair):
    number, qualifier = pair
    return q(number, "%", qualifier, f">{number}%" if qualifier == "gt" else None)


for idx, (label, values) in enumerate(RESOLUTION.items(), start=1):
    r1, r2, time_h, sy, see, ry, ree, detail_page, masses = values
    evidence = unique(e2 + ev(3) + (ev(detail_page) if detail_page else []))
    base = STARTING[label]
    alcohol_smiles = base["smiles"]
    acetate_smiles = alcohol_smiles.replace("C(O)", "C(OC(C)=O)")
    pids = {"sub": f"kr_{label}_substrate", "vinyl": f"kr_{label}_vinyl_acetate", "enzyme": f"kr_{label}_enzyme", "salc": f"kr_{label}_S_alcohol", "rac": f"kr_{label}_R_acetate"}
    substrate_mass = q(101 if label == "1g" else 100, "mg") if detail_page else q(100, "mg", "approx", "~100 mg")
    parts = [
        participant(pids["sub"], "reactant", f"racemic {label}", base["name"], evidence, alcohol_smiles, [field("mass", substrate_mass, evidence)]),
        participant(pids["vinyl"], "reactant", "vinyl acetate", "vinyl acetate", evidence, "C=COC(C)=O", [field("volume", q(5, "mL"), evidence)]),
        participant(pids["enzyme"], "catalyst", "Novozym 435", "Novozym 435", evidence, None, [field("mass", q(70, "mg"), evidence)]),
        participant(pids["salc"], "product", f"(S)-{label}", f"(S)-enriched {base['name'].replace('(±)-','')}", evidence, alcohol_smiles),
        participant(pids["rac"], "product", f"(R)-2{label[-1]}", f"(R)-allenyl acetate derived from {label}", evidence, acetate_smiles),
    ]
    outcomes = [
        field("isolated_yield", q(sy, "%"), evidence, [pids["salc"]]),
        field("product_ee", ee_value(see), evidence, [pids["salc"]]),
        field("isolated_yield", q(ry, "%"), evidence, [pids["rac"]]),
        field("product_ee", ee_value(ree), evidence, [pids["rac"]]),
        field("yield_measurement_basis", "isolated yield based on alcohol", evidence, [pids["salc"], pids["rac"]]),
    ]
    if masses[0] is not None:
        outcomes.extend([
            field("isolated_product_mass", q(masses[0], "mg"), evidence, [pids["salc"]]),
            field("isolated_product_mass", q(masses[1], "mg"), evidence, [pids["rac"]]),
        ])
    notes = ["Enantiomeric excess was determined by GC or HPLC.", "The acetate products' absolute configuration is tentatively assigned as (R) in the source."]
    if label in ("1a", "1b", "1d", "1e", "1g", "1h", "1i"):
        notes.append("The alcohol ee was determined after conversion to the corresponding acetate.")
    if label == "1c":
        notes.append("The alcohol and acetate ee values were determined through the corresponding benzoate procedures described by the source.")
    if label == "1b":
        notes.append("Section 3.2.2 names a different racemic alcohol in its reaction sentence than the heading/table label 1b; the table/heading identity is retained and the discrepancy is unresolved.")
    step_conditions = [field("temperature", q(30, "°C"), evidence), field("time", q(time_h, "h"), evidence)]
    if label == "1a":
        step_conditions += [field("workup", "filtered with ether; evaporated", evidence), field("purification", "flash chromatography on silica gel; petroleum ether/ether from 40:1 to 10:1", evidence)]
    RECORDS.append(record(
        f"table1_entry{idx}_{label}_kinetic_resolution", "substrate_scope_entry", evidence, parts,
        [{"step_id": "novozym_resolution", "participant_ids": [pids["sub"], pids["vinyl"], pids["enzyme"]], "conditions": step_conditions}],
        outcomes, notes,
        ["No explicitly associated Supporting Information was supplied.", "All candidate structures remain unverified."] + (["Section 3.2.2 substrate-name discrepancy requires source review."] if label == "1b" else [])
    ))


# Page 3, Equation (2): initial coupling experiment, distinct from racemic optimization rows.
e3 = ev(3)
eq2_parts = [
    participant("eq2_S1a", "reactant", "(S)-1a", "(S)-4-(n-butyl)hexa-4,5-dien-1-yn-3-ol", e3, STARTING["1a"]["smiles"], [field("input_ee", q(98, "%"), e3)]),
    participant("eq2_phi", "reactant", "PhI", "iodobenzene", e3, "Ic1ccccc1"),
    participant("eq2_pd", "catalyst", "Pd(PPh3)2Cl2", "bis(triphenylphosphine)palladium(II) dichloride", e3, None, [field("amount", q(5, "mol%"), e3)]),
    participant("eq2_cui", "catalyst", "CuI", "copper(I) iodide", e3, "[Cu]I", [field("amount", q(10, "mol%"), e3)]),
    participant("eq2_k2co3", "reagent", "K2CO3", "potassium carbonate", e3, "[K+].[K+].[O-]C([O-])=O", [field("equivalents", q(1.1, "equiv"), e3)]),
    participant("eq2_ch3cn", "solvent", "CH3CN", "acetonitrile", e3, "CC#N"),
    participant("eq2_S3a", "product", "(S)-3a", "(S)-1-phenyl-4-(n-butyl)hexa-4,5-dien-1-yn-3-ol", e3, "C=C=C(CCCC)C(O)C#Cc1ccccc1"),
]
RECORDS.append(record(
    "eq2_initial_sonogashira_S1a", "reported_experiment", e3, eq2_parts,
    [{"step_id": "coupling", "participant_ids": [p["entity_id"] for p in eq2_parts[:-1]], "conditions": [field("temperature", "r.t.", e3), missing_condition("time")]}],
    [field("isolated_yield", q(62, "%"), e3, ["eq2_S3a"]), field("product_ee", q(98, "%"), e3, ["eq2_S3a"])],
    ["The text reports no obvious racemization."], ["Reaction time and experiment-specific workup/purification are not reported on page 3.", "Candidate structures remain unverified."]
))


TABLE2 = [
    (1, "Pd(PhCN)2Cl2", "NEt3", "NEt3", "r.t.", 33, "NR", 5, 10),
    (2, "Pd(CH3CN)2Cl2", "NEt3", "NEt3", "r.t.", 33, "NR", 5, 10),
    (3, "Pd(PPh3)2Cl2", "NEt3", "NEt3", "r.t.", 11.5, 63, 5, 10),
    (4, "Pd(PPh3)2Cl2", "1,4-dioxane", "NEt3", "r.t.", 3.0, 41, 5, 10),
    (5, "Pd(PPh3)2Cl2", "1,4-dioxane", "piperidine", "r.t.", 3.0, 60, 5, 10),
    (6, "Pd(PPh3)2Cl2", "1,4-dioxane", "i-Pr2NH", "r.t.", 2.5, 67, 5, 10),
    (7, "Pd(PPh3)2Cl2", "CH3CN", "i-Pr2NH", "r.t.", 5.5, 68, 2, 2),
    (8, "Pd(PPh3)2Cl2", "THF", "i-Pr2NH", "r.t.", 2.2, 82, 2, 2),
    (9, "Pd(PPh3)2Cl2", "THF", "piperidine", "r.t.", 3.5, 59, 2, 2),
    (10, "Pd(PPh3)2Cl2", "THF", "i-Pr2NH", "r.t.", 16.5, 79, 1, 1),
    (11, "Pd(PPh3)2Cl2", "THF", "i-Pr2NH", -2, 5.0, 90, 2, 2),
]
SMILES = {"NEt3":"CCN(CC)CC", "1,4-dioxane":"C1COCCO1", "piperidine":"C1CCNCC1", "i-Pr2NH":"CC(C)NC(C)C", "CH3CN":"CC#N", "THF":"C1CCOC1"}
for entry, catalyst, solvent, base, temp, time_h, yield_value, pdload, cuload in TABLE2:
    prefix = f"t2e{entry}"
    parts = [
        participant(prefix+"_1a", "reactant", "racemic 1a", STARTING["1a"]["name"], e3, STARTING["1a"]["smiles"]),
        participant(prefix+"_phi", "reactant", "PhI", "iodobenzene", e3, "Ic1ccccc1"),
        participant(prefix+"_pd", "catalyst", catalyst, catalyst, e3, None, [field("amount", q(pdload, "mol%"), e3)]),
        participant(prefix+"_cui", "catalyst", "CuI", "copper(I) iodide", e3, "[Cu]I", [field("amount", q(cuload, "mol%"), e3)]),
        participant(prefix+"_solvent", "solvent", solvent, solvent, e3, SMILES.get(solvent)),
        participant(prefix+"_base", "reagent", base, base, e3, SMILES.get(base)),
        participant(prefix+"_3a", "product", "3a", "1-phenyl-4-(n-butyl)hexa-4,5-dien-1-yn-3-ol", e3, "C=C=C(CCCC)C(O)C#Cc1ccccc1"),
    ]
    temp_value = "r.t." if temp == "r.t." else q(temp, "°C")
    out = yield_value if isinstance(yield_value, str) else q(yield_value, "%")
    RECORDS.append(record(
        f"table2_entry{entry}_sonogashira_optimization", "optimization_entry", e3, parts,
        [{"step_id": "coupling", "participant_ids": [p["entity_id"] for p in parts[:-1]], "conditions": [field("temperature", temp_value, e3), field("time", q(time_h, "h"), e3)]}],
        [field("yield", out, e3, [prefix+"_3a"])],
        ["NR is preserved as the source's qualitative no-reaction outcome." if yield_value == "NR" else "Table 2 optimization result."],
        ["Substrate and iodobenzene quantities, experiment-specific workup, and yield measurement basis are not reported in Table 2.", "Candidate structures remain unverified."]
    ))


# Page 3 prose: hydrolysis is a distinct reported transformation, but only qualitative outcome is given here.
hyd_parts = [
    participant("hyd_R2a", "reactant", "(R)-2a", "(R)-4-(n-butyl)hexa-4,5-dien-1-yn-3-yl acetate", e3, "C=C=C(CCCC)C(OC(C)=O)C#C"),
    participant("hyd_k2co3", "reagent", "K2CO3", "potassium carbonate", e3, "[K+].[K+].[O-]C([O-])=O"),
    participant("hyd_meoh", "solvent", "MeOH", "methanol", e3, "CO"),
    participant("hyd_R1a", "product", "(R)-1a", "(R)-4-(n-butyl)hexa-4,5-dien-1-yn-3-ol", e3, STARTING["1a"]["smiles"]),
]
RECORDS.append(record(
    "page3_R2a_hydrolysis_to_R1a", "reported_experiment", e3, hyd_parts,
    [{"step_id": "hydrolysis", "participant_ids": ["hyd_R2a", "hyd_k2co3", "hyd_meoh"], "conditions": [missing_condition("temperature"), missing_condition("time")]}],
    [field("yield", "good yield", e3, ["hyd_R1a"])], [],
    ["Only a qualitative yield is given in the inspected page-3 prose; quantities, time, temperature, workup, and exact yield are missing here.", "Candidate structures remain unverified."]
))


# Page 4 Table 3 substrate-scope rows.
e4 = ev(4)
TABLE3 = [
    (1, "(R)-1a", 99, "H", "iodobenzene", "Ic1ccccc1", 5.0, 86, 98, "3a", "c1ccccc1"),
    (2, "(R)-1a", 99, "p-COOMe", "methyl 4-iodobenzoate", "COC(=O)c1ccc(I)cc1", 3.5, 92, 99, "3b", "c1ccc(C(=O)OC)cc1"),
    (3, "(R)-1a", 99, "p-NO2", "1-iodo-4-nitrobenzene", "O=[N+]([O-])c1ccc(I)cc1", 6.0, 86, 99, "3c", "c1ccc([N+](=O)[O-])cc1"),
    (4, "(S)-1a", 98, "p-Me", "4-iodotoluene", "Cc1ccc(I)cc1", 4.0, 86, 98, "3d", "c1ccc(C)cc1"),
    (5, "(S)-1a", 98, "p-MeO", "4-iodoanisole", "COc1ccc(I)cc1", 5.0, 84, 98, "3e", "c1ccc(OC)cc1"),
    (6, "(S)-1a", 98, "p-Br", "1-bromo-4-iodobenzene", "Brc1ccc(I)cc1", 4.0, 80, 98, "3f", "c1ccc(Br)cc1"),
    (7, "(S)-1a", 98, "p-CN", "4-iodobenzonitrile", "N#Cc1ccc(I)cc1", 4.5, 86, 98, "3g", "c1ccc(C#N)cc1"),
    (8, "(R)-1a", 98, "o-Me", "2-iodotoluene", "Cc1ccccc1I", 21, 87, 97, "3h", "c1ccccc1C"),
]
for entry, config, input_ee, rlabel, aryl_name, aryl_smiles, time_h, yld, product_ee, plabel, aryl_product in TABLE3:
    prefix = f"t3e{entry}"
    product_smiles = f"C=C=C(CCCC)C(O)C#C{aryl_product}"
    parts = [
        participant(prefix+"_1a", "reactant", config, f"{config} 4-(n-butyl)hexa-4,5-dien-1-yn-3-ol", e4, STARTING["1a"]["smiles"], [field("input_ee", q(input_ee, "%"), e4)]),
        participant(prefix+"_aryl", "reactant", rlabel+" aryl iodide", aryl_name, e4, aryl_smiles),
        participant(prefix+"_pd", "catalyst", "Pd(PPh3)2Cl2", "bis(triphenylphosphine)palladium(II) dichloride", e4),
        participant(prefix+"_cui", "catalyst", "CuI", "copper(I) iodide", e4, "[Cu]I"),
        participant(prefix+"_thf", "solvent", "THF", "tetrahydrofuran", e4, "C1CCOC1"),
        participant(prefix+"_base", "reagent", "i-Pr2NH", "diisopropylamine", e4, "CC(C)NC(C)C"),
        participant(prefix+"_product", "product", plabel, f"Sonogashira product {plabel}", e4, product_smiles),
    ]
    RECORDS.append(record(
        f"table3_entry{entry}_{plabel}_aryl_scope", "substrate_scope_entry", e4, parts,
        [{"step_id": "coupling", "participant_ids": [p["entity_id"] for p in parts[:-1]], "conditions": [field("temperature", q(-2, "°C"), e4), field("time", q(time_h, "h"), e4)]}],
        [field("isolated_yield", q(yld, "%"), e4, [prefix+"_product"]), field("yield_measurement_basis", "isolated yield based on 1a", e4, [prefix+"_product"]), field("product_ee", q(product_ee, "%"), e4, [prefix+"_product"]), field("ee_measurement_basis", "determined by HPLC", e4, [prefix+"_product"])],
        [], ["Catalyst loadings and reactant/solvent/base quantities are not stated in the Table 3 header.", "The prose says standard conditions correspond to Table 2 entry 10, while the Table 3 arrow visibly states -2 °C; the explicit Table 3 temperature was retained and the discrepancy requires review.", "Candidate structures remain unverified."]
    ))


# Page 4 Scheme 3: two branch-specific multistep reported sequences.
for suffix, rlabel, total_yield, ee_out in (("4a", "CH3", 75, 98), ("4b", "Et", 62, None)):
    prefix = f"s3_{suffix}"
    parts = [
        participant(prefix+"_S1a", "reactant", "(S)-1a", "(S)-4-(n-butyl)hexa-4,5-dien-1-yn-3-ol", e4, STARTING["1a"]["smiles"], [field("input_ee", q(98, "%"), e4)]),
        participant(prefix+"_vinyl_ether", "reactant", "vinyl ethyl ether", "ethyl vinyl ether", e4, "CCOC=C"),
        participant(prefix+"_ppts1", "reagent", "PPTS", "pyridinium p-toluenesulfonate", e4),
        participant(prefix+"_5", "product", "5", "protected intermediate 5", e4),
        participant(prefix+"_nbuli", "reagent", "n-BuLi", "n-butyllithium", e4, "[Li]CCCC"),
        participant(prefix+"_ri", "reactant", f"RI (R={rlabel})", f"alkyl iodide branch R={rlabel}", e4),
        participant(prefix+"_6", "product", "6a" if suffix == "4a" else "6b", f"alkylated protected intermediate for {suffix}", e4),
        participant(prefix+"_meoh", "solvent", "CH3OH", "methanol", e4, "CO"),
        participant(prefix+"_ppts2", "reagent", "PPTS", "pyridinium p-toluenesulfonate", e4),
        participant(prefix+"_product", "product", suffix, f"substituted 1,2-allenyl-1-alkynyl carbinol {suffix}", e4),
    ]
    steps = [
        {"step_id": "protection", "participant_ids": [prefix+x for x in ("_S1a", "_vinyl_ether", "_ppts1", "_5")], "conditions": [missing_condition("temperature"), missing_condition("time")]},
        {"step_id": "alkylation", "participant_ids": [prefix+x for x in ("_5", "_nbuli", "_ri", "_6")], "conditions": [field("initial_temperature", q(-78, "°C"), e4), field("warm_to", "r.t.", e4), missing_condition("time")]},
        {"step_id": "deprotection", "participant_ids": [prefix+x for x in ("_6", "_meoh", "_ppts2", "_product")], "conditions": [missing_condition("temperature"), missing_condition("time")]},
    ]
    outcomes = [field("total_yield", q(total_yield, "%"), e4, [prefix+"_product"])]
    outcomes.append(field("product_ee", q(ee_out, "%") if ee_out is not None else None, e4 if ee_out is not None else [], [prefix+"_product"]))
    RECORDS.append(record(
        f"scheme3_{suffix}_multistep_alkylation", "reported_experiment", e4, parts, steps, outcomes,
        ["The yield is explicitly labeled total yield in Scheme 3."],
        ["Reagent quantities, solvent for the first two stages, stage durations, workup, and purification are absent from Scheme 3.", "The alkyl iodide is retained as the source label RI for the branch rather than silently expanded.", "Product 4b ee is not reported in Scheme 3."] if suffix == "4b" else ["Reagent quantities, solvent for the first two stages, stage durations, workup, and purification are absent from Scheme 3.", "The alkyl iodide is retained as the source label RI for the branch rather than silently expanded."]
    ))


OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(RECORDS, ensure_ascii=False, indent=2) + "\n")

ids = {r["source_reaction_id"]: r["record_id"] for r in RECORDS}
start_ids = [ids[f"sec{STARTING[x]['sec']}_{x}_preparation"] for x in STARTING]
res_ids = [ids[f"table1_entry{i}_{x}_kinetic_resolution"] for i, x in enumerate(RESOLUTION, 1)]
t2_ids = [ids[f"table2_entry{i}_sonogashira_optimization"] for i in range(1, 12)]
t3_ids = [ids[f"table3_entry{i}_{TABLE3[i-1][9]}_aryl_scope"] for i in range(1, 9)]
coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {"page": 1, "state": "attempted", "regions": [
            {"region": "title, abstract, and introductory prose", "finding": "Context and motivation only; no new page-specific experimental procedure.", "evidence_ids": [f"{DOC}:page1:image", f"{DOC}:page1:text"]},
            {"region": "Equation (1) at page bottom", "finding": "Prior-literature Novozym-435 kinetic-resolution scheme, explicitly linked to reference 13; classified as literature_example.", "evidence_ids": [f"{DOC}:page1:image", f"{DOC}:page1:text"]}],
         "record_ids": [ids["eq1_prior_work_kinetic_resolution"]], "unresolved": ["Equation (1) uses generic R groups and gives no experiment-specific time or yields."]},
        {"page": 2, "state": "attempted", "regions": [
            {"region": "Scheme 1, upper-left", "finding": "Retrosynthetic/conceptual sequence with generic R groups; classified as general_scheme rather than an experiment.", "evidence_ids": [f"{DOC}:page2:image", f"{DOC}:page2:text"]},
            {"region": "Scheme 2, upper-right, and section 2.1 prose", "finding": "Generic synthesis arrow and labels 1a-1i; linked to nine individual preparations detailed on pages 4-5.", "evidence_ids": [f"{DOC}:page2:image", f"{DOC}:page2:text"]},
            {"region": "Figure 1, middle-right", "finding": "Empirical stereoselectivity model, not a reported transformation; no experiment record fabricated.", "evidence_ids": [f"{DOC}:page2:image", f"{DOC}:page2:text"]},
            {"region": "Table 1 and footnotes, lower half", "finding": "Nine independent Novozym-435 kinetic-resolution scope rows; common footnote quantities structured for every row.", "evidence_ids": [f"{DOC}:page2:image", f"{DOC}:page2:text"]}],
         "record_ids": [ids["scheme1_retrosynthetic_concept"]] + start_ids + res_ids,
         "unresolved": ["Absolute configuration of acetate products is only tentatively assigned.", "Table rows provide connectivity through R-group labels; structures remain unverified."]},
        {"page": 3, "state": "attempted", "regions": [
            {"region": "section 2.3 and Equation (2)", "finding": "One initial enantioenriched Sonogashira experiment: (S)-1a with iodobenzene, 62% yield and 98% ee.", "evidence_ids": [f"{DOC}:page3:image", f"{DOC}:page3:text"]},
            {"region": "Table 2 and footnotes", "finding": "Eleven independent optimization rows, including two NR outcomes and catalyst-load footnotes.", "evidence_ids": [f"{DOC}:page3:image", f"{DOC}:page3:text"]},
            {"region": "right-column hydrolysis prose", "finding": "Distinct hydrolysis of (R)-2a with K2CO3/MeOH to (R)-1a; only qualitative good yield on this inspected page.", "evidence_ids": [f"{DOC}:page3:image", f"{DOC}:page3:text"]}],
         "record_ids": [ids["eq2_initial_sonogashira_S1a"]] + t2_ids + [ids["page3_R2a_hydrolysis_to_R1a"]] + res_ids,
         "unresolved": ["Equation (2) lacks time and workup.", "Table 2 omits substrate/reagent amounts and yield basis.", "Hydrolysis exact yield and detailed conditions are absent on page 3."]},
        {"page": 4, "state": "attempted", "regions": [
            {"region": "Table 3 and footnotes, upper half", "finding": "Eight independent aryl-iodide Sonogashira scope rows with time, isolated yield, and product ee.", "evidence_ids": [f"{DOC}:page4:image", f"{DOC}:page4:text"]},
            {"region": "Scheme 3, page bottom", "finding": "Two branch-specific multistep protection/alkylation/deprotection sequences to 4a and 4b, with total yields 75% and 62%.", "evidence_ids": [f"{DOC}:page4:image", f"{DOC}:page4:text"]},
            {"region": "section 3.1.1-3.1.3, right column", "finding": "Detailed preparation 1a, complete reagent lists for 1b, and beginning of 1c; merged into the corresponding preparation records.", "evidence_ids": [f"{DOC}:page4:image", f"{DOC}:page4:text"]}],
         "record_ids": t3_ids + [ids["scheme3_4a_multistep_alkylation"], ids["scheme3_4b_multistep_alkylation"]] + start_ids[:3],
         "unresolved": ["Table 3 catalyst loadings are absent and its -2 °C header conflicts with prose referring to Table 2 entry 10.", "Scheme 3 omits most stage quantities and durations."]},
        {"page": 5, "state": "attempted", "regions": [
            {"region": "section 3.1.3 continuation and sections 3.1.4-3.1.9, left column", "finding": "Individual starting-allenol preparations 1c-1i with reactant quantities and isolated product mass/yield.", "evidence_ids": [f"{DOC}:page5:image", f"{DOC}:page5:text"]},
            {"region": "section 3.2.1, lower-left to upper-right", "finding": "Detailed typical kinetic resolution for 1a; merged with Table 1 entry 1.", "evidence_ids": [f"{DOC}:page5:image", f"{DOC}:page5:text"]},
            {"region": "sections 3.2.2 and 3.2.3, right column", "finding": "Detailed product masses/ees for resolution 1b and beginning of 1c; merged with Table 1 entries 2-3.", "evidence_ids": [f"{DOC}:page5:image", f"{DOC}:page5:text"]}],
         "record_ids": start_ids[2:] + res_ids[:3],
         "unresolved": ["Individual preparation paragraphs 1b-1i do not restate the typical time/temperature/workup.", "Section 3.2.2 reaction sentence conflicts with its heading/table substrate identity.", "The 1c resolution continues on page 6."]},
        {"page": 6, "state": "attempted", "regions": [
            {"region": "section 3.2.3 continuation, upper-left", "finding": "Completion of kinetic resolution 1c, including acetate product data; merged with Table 1 entry 3.", "evidence_ids": [f"{DOC}:page6:image", f"{DOC}:page6:text"]},
            {"region": "sections 3.2.4-3.2.6", "finding": "Individual kinetic-resolution results for 1d-1f with product masses and ee; merged with Table 1 entries 4-6.", "evidence_ids": [f"{DOC}:page6:image", f"{DOC}:page6:text"]},
            {"region": "section 3.2.7, lower-right", "finding": "Kinetic-resolution experiment for 1g begins and reports substrate/product masses, yields, and alcohol ee; merged with Table 1 entry 7.", "evidence_ids": [f"{DOC}:page6:image", f"{DOC}:page6:text"]}],
         "record_ids": res_ids[2:7],
         "unresolved": ["Characterization of 2g continues beyond the requested page range; no coverage claim is made for page 7.", "All structures and extracted facts remain machine-generated and need source review."]},
    ],
}
COVERAGE.parent.mkdir(parents=True, exist_ok=True)
COVERAGE.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

if TASKS.exists():
    tasks = json.loads(TASKS.read_text())
    for task in tasks:
        page = int(task["evidence_id"].split(":page", 1)[1].split(":", 1)[0])
        if 1 <= page <= 6:
            task["state"] = "attempted"
            task["visual_evidence_id"] = f"{DOC}:page{page}:image"
            task["reason"] = "Original page image visually inspected; findings and record links are in coverage/pages_0001_0006.json."
    TASKS.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"records": len(RECORDS), "coverage_pages": [p["page"] for p in coverage["pages"]], "output": str(OUT)}, ensure_ascii=False))
