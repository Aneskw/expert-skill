#!/usr/bin/env python3
"""Build evidence-linked machine records for PDF pages 1--4 of ol3007293."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "runs/current/raw_model/records_pages_0001_0004.json"
COVERAGE = ROOT / "runs/current/coverage/pages_0001_0004.json"
TASKS = ROOT / "runs/current/tasks.json"
DOC = "doc_3d88a448601b936d"


def ev(page):
    return [f"{DOC}:page{page}:image", f"{DOC}:page{page}:text"]


def fact(value, evidence):
    return {
        "value": value,
        "evidence_ids": list(evidence) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def qty(number, unit, raw_text=None):
    value = {"number": number, "unit": unit}
    if raw_text:
        value["raw_text"] = raw_text
    return value


def amount(name, value, evidence):
    return {"name": name, "fact": fact(value, evidence)}


def participant(entity_id, role, label, evidence, smiles=None, name=None, amounts=None):
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


def field(name, value, evidence, targets=None):
    item = {"name": name, "fact": fact(value, evidence)}
    if targets:
        item["target_entity_ids"] = targets
    return item


def record(suffix, kind, evidence, participants, steps=None, outcomes=None, notes=None, unresolved=None):
    return {
        "record_id": f"{DOC}:{suffix}",
        "document_id": DOC,
        "source_reaction_id": suffix,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": list(evidence),
        "participants": participants,
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


SMILES = {
    "1a": "C=C=CCNCc1ccccc1",
    "1b": "C=C=CCNCc1ccc(OC)cc1",
    "1c": "C=C=CCNCCCC",
    "1d": "C=C=CCN",
    "1f": "CC(C)=C=CCNCc1ccccc1",
    "2a": "COC(=O)OC(C)(C)C#Cc1ccccc1",
    "2b": "COC(=O)OC(CC)(CC)C#Cc1ccccc1",
    "2c": "COC(=O)OC1(CCCC1)C#Cc2ccccc2",
    "2d": "COC(=O)OC1(CCCCC1)C#Cc2ccccc2",
    "2e": "COC(=O)OC(C)(C)C#Cc1ccc([N+](=O)[O-])cc1",
    "2f": "COC(=O)OC(C)(C)C#CC",
    "2g": "COC(=O)OC(C)(C)C#CCCCC",
    "2h": "COC(=O)OC(C)(C)C#CCO[Si](C)(C)C(C)(C)C",
}


records = []

# Page 1 graphical abstract: a generic transformation, not an individual batch.
e1 = ev(1)
generic_participants = [
    participant("generic_1", "reactant", "2,3-allenyl amine 1", e1),
    participant("generic_2", "reactant", "propargylic carbonate 2", e1),
    participant("generic_3", "product", "5-(1,3,4-alkatrien-2-yl)oxazolidin-2-one 3", e1),
]
records.append(record(
    "graphical_abstract_general_route", "general_scheme", e1, generic_participants,
    outcomes=[field("reported_scope_yield_range", {"minimum": 70, "maximum": 92, "unit": "%", "raw_text": "70-92%"}, e1, ["generic_3"])],
    notes=["Graphical abstract and abstract-level scope summary; not a single reported batch experiment."],
    unresolved=["Generic R-group structures cannot be assigned unique SMILES.", "Yield values summarize the reported scope and are not a single-batch outcome."],
))

# Page 2 Scheme 1: conceptual selectivity map.
e2 = ev(2)
records.append(record(
    "scheme1_concepts_selectivity", "general_scheme", e2,
    [
        participant("scheme1_1", "reactant", "2,3-allenyl amine 1", e2),
        participant("scheme1_2", "reactant", "propargylic carbonate 2", e2),
        participant("scheme1_3", "product", "CO2-incorporated oxazolidin-2-one 3", e2),
        participant("scheme1_4", "product", "non-CO2-incorporated regioisomer 4", e2),
        participant("scheme1_5", "product", "non-CO2-incorporated regioisomer 5", e2),
        participant("scheme1_6", "product", "CO2-incorporated regioisomer 6", e2),
        participant("scheme1_int1", "unspecified_agent", "allenylpalladium Int 1", e2),
        participant("scheme1_co2", "reagent", "CO2", e2, smiles="O=C=O", name="carbon dioxide"),
    ],
    notes=["Conceptual route and selectivity issue; compounds 4, 5, and 6 are depicted alternatives rather than reported products from a separate batch."],
    unresolved=["Generic R-group structures and palladium intermediate are not encoded as unique SMILES."],
))


def table1_record(entry, catalyst, solvent, base, yld, temperature=70, carbonate_equiv=1.5, tfp=False, isolated=None):
    evidence = e2
    participants = [
        participant("reactant_1a", "reactant", "1a", evidence, SMILES["1a"], amounts=[amount("reaction_scale", qty(0.1, "mmol"), evidence)]),
        participant("reactant_2a", "reactant", "2a", evidence, SMILES["2a"], amounts=[amount("equivalents", qty(carbonate_equiv, "equiv"), evidence)]),
        participant("catalyst", "catalyst", catalyst, evidence, amounts=[amount("catalyst_loading", qty(5, "mol%"), evidence)]),
        participant("solvent", "solvent", solvent, evidence, amounts=[amount("volume", qty(1, "mL"), evidence)]),
        participant("product_3aa", "product", "3aa", evidence),
        participant("internal_standard", "unspecified_agent", "1,3,5-trimethylbenzene", evidence, smiles="Cc1cc(C)cc(C)c1", name="1,3,5-trimethylbenzene"),
    ]
    if tfp:
        participants.append(participant("ligand_tfp", "reagent", "TFP", evidence, name="tri(2-furyl)phosphine", amounts=[amount("ligand_loading", qty(10, "mol%"), evidence)]))
    if base:
        participants.append(participant("base", "reagent", base, evidence, amounts=[amount("equivalents", qty(2, "equiv"), evidence)]))
    step = {
        "step_id": "cyclization",
        "participant_ids": [p["entity_id"] for p in participants if p["entity_id"] != "internal_standard"],
        "conditions": [
            field("temperature", qty(temperature, "°C"), evidence),
            field("time", qty(4, "h"), evidence),
            field("operation", "Pd-catalyzed cyclization", evidence),
        ],
    }
    outcomes = [
        field("nmr_yield", qty(yld, "%"), evidence, ["product_3aa"]),
        field("yield_measurement_basis", "1H NMR of the crude reaction mixture using 1,3,5-trimethylbenzene as internal standard", evidence, ["product_3aa"]),
    ]
    if isolated is not None:
        outcomes.append(field("isolated_yield", qty(isolated, "%"), evidence, ["product_3aa"]))
    return record(
        f"table1_entry{entry}", "optimization_entry", evidence, participants, [step], outcomes,
        unresolved=[
            "Product 3aa structure is depicted but its candidate SMILES was not encoded; source-level structure review is required.",
            "Atmosphere, workup, and purification are not stated in the main-text row.",
            "Supporting Information is mentioned by the paper but was not provided or explicitly associated.",
        ],
    )


table1 = [
    (1, "Pd(PPh3)4", "DMSO", "K2CO3", 94, 70, 1.5, False, 88),
    (2, "Pd(dba)2", "DMSO", "K2CO3", 52, 70, 1.5, True, None),
    (3, "Pd(OAc)2", "DMSO", "K2CO3", 67, 70, 1.5, True, None),
    (4, "Pd(PPh3)4", "CH3CN", "K2CO3", 89, 70, 1.5, False, None),
    (5, "Pd(PPh3)4", "DMF", "K2CO3", 82, 70, 1.5, False, None),
    (6, "Pd(PPh3)4", "THF", "K2CO3", 39, 70, 1.5, False, None),
    (7, "Pd(PPh3)4", "DCE", "K2CO3", 77, 70, 1.5, False, None),
    (8, "Pd(PPh3)4", "DMSO", "Cs2CO3", 22, 70, 1.5, False, None),
    (9, "Pd(PPh3)4", "DMSO", "NEt3", 66, 70, 1.5, False, None),
    (10, "Pd(PPh3)4", "DMSO", None, 75, 70, 1.5, False, None),
    (11, "Pd(PPh3)4", "DMSO", "K2CO3", 72, 50, 1.5, False, None),
    (12, "Pd(PPh3)4", "DMSO", "K2CO3", 36, 90, 1.5, False, None),
    (13, "Pd(PPh3)4", "DMSO", "K2CO3", 99, 70, 1.2, False, None),
    (14, "Pd(PPh3)4", "DMSO", "K2CO3", 83, 70, 2.0, False, None),
]
records.extend(table1_record(*row) for row in table1)


e3 = ev(3)
table2_rows = [
    (1, "1a", "2a", "3aa", 92),
    (2, "1a", "2a", "3aa", 90),
    (3, "1a", "2b", "3ab", 90),
    (4, "1a", "2c", "3ac", 85),
    (5, "1a", "2d", "3ad", 86),
    (6, "1a", "2e", "3ae", 85),
    (7, "1a", "2f", "3af", 80),
    (8, "1a", "2g", "3ag", 83),
    (9, "1a", "2h", "3ah", 70),
    (10, "1b", "2a", "3ba", 87),
    (11, "1c", "2a", "3ca", 82),
    (12, "1d", "2a", "3da", 75),
]


def table2_record(entry, amine, carbonate, product, yld):
    evidence = e3
    amine_label = "1d·HCl" if entry == 12 else amine
    scale = 6.3 if entry == 2 else 0.3
    amine_amounts = [amount("reaction_scale", qty(scale, "mmol"), evidence)]
    carbonate_amounts = [amount("equivalents", qty(1.2, "equiv"), evidence)]
    if entry == 2:
        carbonate_amounts.append(amount("amount", qty(7.56, "mmol"), evidence))
    participants = [
        participant("amine", "reactant", amine_label, evidence, SMILES.get(amine), amounts=amine_amounts),
        participant("carbonate", "reactant", carbonate, evidence, SMILES.get(carbonate), amounts=carbonate_amounts),
        participant("catalyst", "catalyst", "Pd(PPh3)4", evidence, amounts=[amount("catalyst_loading", qty(5, "mol%"), evidence)]),
        participant("base", "reagent", "K2CO3", evidence, amounts=[amount("equivalents", qty(3 if entry == 12 else 2, "equiv"), evidence)]),
        participant("solvent", "solvent", "DMSO", evidence, amounts=[] if entry == 2 else [amount("volume", qty(3, "mL"), evidence)]),
        participant("product", "product", product, evidence),
    ]
    vessel = "three-necked flask" if entry == 2 else "Schlenk tube"
    step = {
        "step_id": "cyclization",
        "participant_ids": [p["entity_id"] for p in participants],
        "conditions": [
            field("temperature", qty(70, "°C"), evidence),
            field("time", qty(4, "h"), evidence),
            field("operation", vessel, evidence),
        ],
    }
    unresolved = [
        f"Product {product} structure is depicted but its candidate SMILES was not encoded; source-level structure review is required.",
        "Atmosphere, workup, and purification are not stated in the main-text row.",
        "Supporting Information is mentioned by the paper but was not provided or explicitly associated.",
    ]
    if entry == 2:
        unresolved.append("The gram-scale footnote does not restate the DMSO volume.")
    return record(
        f"table2_entry{entry}", "substrate_scope_entry", evidence, participants, [step],
        [
            field("isolated_yield", qty(yld, "%"), evidence, ["product"]),
            field("yield_measurement_basis", "isolated yield", evidence, ["product"]),
        ],
        unresolved=unresolved,
    )


records.extend(table2_record(*row) for row in table2_rows)

# Page 3 Scheme 2: one experiment with two isolated stereoisomer-labelled products.
scheme2_participants = [
    participant("amine_1e", "reactant", "1e", e3),
    participant("carbonate_2a", "reactant", "2a", e3, SMILES["2a"], amounts=[amount("equivalents", qty(1.2, "equiv"), e3)]),
    participant("catalyst", "catalyst", "Pd(PPh3)4", e3, amounts=[amount("catalyst_loading", qty(5, "mol%"), e3)]),
    participant("base", "reagent", "K2CO3", e3, amounts=[amount("equivalents", qty(2, "equiv"), e3)]),
    participant("solvent", "solvent", "DMSO", e3),
    participant("product_z", "product", "Z-3ea", e3),
    participant("product_e", "product", "E-3ea", e3),
]
records.append(record(
    "scheme2_1e_2a", "reported_experiment", e3, scheme2_participants,
    [{
        "step_id": "cyclization",
        "participant_ids": [p["entity_id"] for p in scheme2_participants],
        "conditions": [field("temperature", qty(70, "°C"), e3), field("time", qty(4, "h"), e3)],
    }],
    [
        field("reported_yield_Z_3ea", qty(55, "%"), e3, ["product_z"]),
        field("reported_yield_E_3ea", qty(10, "%"), e3, ["product_e"]),
        field("stereoisomer_ratio", "Z/E = 82:18", e3, ["product_z", "product_e"]),
        field("selectivity_measurement_basis", "1H NMR analysis of the crude reaction mixture", e3, ["product_z", "product_e"]),
        field("yield_measurement_basis", None, [], ["product_z", "product_e"]),
    ],
    unresolved=[
        "The 55% and 10% product yield measurement basis is not explicitly stated in Scheme 2 or adjacent prose.",
        "Structures of 1e, Z-3ea, and E-3ea require source-level stereochemical review; SMILES are left null.",
        "Reaction scale, DMSO volume, atmosphere, workup, and purification are not stated.",
        "Supporting Information is mentioned by the paper but was not provided or explicitly associated.",
    ],
))


def table3_record(entry, catalyst, ligand, hours, yld):
    participants = [
        participant("amine_1f", "reactant", "1f", e3, SMILES["1f"], amounts=[amount("reaction_scale", qty(0.1, "mmol"), e3)]),
        participant("carbonate_2a", "reactant", "2a", e3, SMILES["2a"], amounts=[amount("equivalents", qty(1.2, "equiv"), e3)]),
        participant("catalyst", "catalyst", catalyst, e3, amounts=[amount("catalyst_loading", qty(5, "mol%"), e3)]),
        participant("base", "reagent", "K2CO3", e3, amounts=[amount("equivalents", qty(2, "equiv"), e3)]),
        participant("solvent", "solvent", "DMSO", e3, amounts=[amount("volume", qty(1, "mL"), e3)]),
        participant("product_3fa", "product", "3fa", e3),
        participant("internal_standard", "unspecified_agent", "1,3,5-trimethylbenzene", e3, smiles="Cc1cc(C)cc(C)c1", name="1,3,5-trimethylbenzene"),
    ]
    if ligand:
        participants.append(participant("ligand", "reagent", ligand, e3, amounts=[amount("ligand_loading", qty(10 if ligand == "TFP" else 5, "mol%"), e3)]))
    return record(
        f"table3_entry{entry}", "optimization_entry", e3, participants,
        [{
            "step_id": "cyclization",
            "participant_ids": [p["entity_id"] for p in participants if p["entity_id"] != "internal_standard"],
            "conditions": [field("temperature", qty(70, "°C"), e3), field("time", qty(hours, "h"), e3), field("operation", "Schlenk tube", e3)],
        }],
        [
            field("nmr_yield", qty(yld, "%"), e3, ["product_3fa"]),
            field("yield_measurement_basis", "1H NMR analysis of the crude reaction mixture using 1,3,5-trimethylbenzene as internal standard", e3, ["product_3fa"]),
        ],
        unresolved=[
            "Product 3fa structure is depicted but its candidate SMILES was not encoded; source-level structure review is required.",
            "Atmosphere, workup, and purification are not stated in the main-text row.",
            "Supporting Information is mentioned by the paper but was not provided or explicitly associated.",
        ],
    )


table3 = [
    (1, "Pd(PPh3)4", None, 4, 22),
    (2, "Pd(dba)2", "TFP", 6, 68),
    (3, "Pd(OAc)2", "TFP", 6, 72),
    (4, "Pd(OAc)2", "dppe", 6, 39),
]
records.extend(table3_record(*row) for row in table3)


def scheme3_record(entry, amine, product, hours, yld):
    participants = [
        participant("amine", "reactant", amine, e3, SMILES.get(amine)),
        participant("carbonate_2a", "reactant", "2a", e3, SMILES["2a"], amounts=[amount("equivalents", qty(1.2, "equiv"), e3)]),
        participant("catalyst", "catalyst", "Pd(OAc)2", e3, amounts=[amount("catalyst_loading", qty(5, "mol%"), e3)]),
        participant("ligand", "reagent", "TFP", e3, name="tri(2-furyl)phosphine", amounts=[amount("ligand_loading", qty(10, "mol%"), e3)]),
        participant("base", "reagent", "K2CO3", e3, amounts=[amount("equivalents", qty(2, "equiv"), e3)]),
        participant("solvent", "solvent", "DMSO", e3),
        participant("product", "product", product, e3),
    ]
    return record(
        f"scheme3_entry{entry}", "substrate_scope_entry", e3, participants,
        [{
            "step_id": "cyclization",
            "participant_ids": [p["entity_id"] for p in participants],
            "conditions": [field("temperature", qty(70, "°C"), e3), field("time", qty(hours, "h"), e3)],
        }],
        [field("reported_yield", qty(yld, "%"), e3, ["product"]), field("yield_measurement_basis", None, [], ["product"])],
        unresolved=[
            f"Product {product} structure is depicted but its candidate SMILES was not encoded; source-level structure review is required.",
            "Reaction scale, DMSO volume, atmosphere, workup, purification, and yield measurement basis are not stated in Scheme 3.",
            "Supporting Information is mentioned by the paper but was not provided or explicitly associated.",
        ],
    )


records.append(scheme3_record(1, "1f", "3fa", 5.5, 70))
records.append(scheme3_record(2, "1g", "3ga", 2, 72))

# Page 4 Scheme 4: proposed mechanism only.
e4 = ev(4)
records.append(record(
    "scheme4_proposed_mechanism", "mechanism", e4,
    [
        participant("mechanism_1", "reactant", "2,3-allenyl amine 1", e4),
        participant("mechanism_2", "reactant", "propargylic carbonate 2", e4),
        participant("mechanism_3", "product", "oxazolidin-2-one 3", e4),
        participant("mechanism_int1", "unspecified_agent", "allenylpalladium Int 1", e4),
        participant("mechanism_int2", "unspecified_agent", "carbamate Int 2", e4),
        participant("mechanism_int3", "unspecified_agent", "pi-allylpalladium Int 3", e4),
        participant("mechanism_int4", "unspecified_agent", "palladium intermediate Int 4", e4),
        participant("mechanism_co2", "reagent", "CO2", e4, smiles="O=C=O", name="carbon dioxide"),
        participant("mechanism_pd", "catalyst", "Pd(0)/palladium species", e4),
        participant("mechanism_base", "reagent", "base", e4),
    ],
    steps=[
        {"step_id": "path_a", "participant_ids": ["mechanism_1", "mechanism_2", "mechanism_int1", "mechanism_int2", "mechanism_int3", "mechanism_3", "mechanism_co2", "mechanism_pd", "mechanism_base"], "conditions": [field("operation", "proposed carbopalladation followed by nucleophilic attack", e4)]},
        {"step_id": "path_b", "participant_ids": ["mechanism_1", "mechanism_2", "mechanism_int1", "mechanism_int2", "mechanism_int4", "mechanism_3", "mechanism_co2", "mechanism_pd", "mechanism_base"], "conditions": [field("operation", "proposed anti-oxypalladation followed by reductive elimination", e4)]},
    ],
    notes=["Scheme 4 is explicitly presented as a possible mechanism and does not represent separate reported batch experiments."],
    unresolved=["Generic R-group structures and organopalladium intermediates are not encoded as unique SMILES.", "The two pathways are proposals and are not assigned experimental yields."],
))


OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")

ids = lambda prefix: [r["record_id"] for r in records if r["source_reaction_id"].startswith(prefix)]
coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1,
            "state": "attempted",
            "regions": [
                {"region": "center graphical abstract reaction arrow and abstract text", "finding": "Generic Pd-catalyzed transformation from 2,3-allenyl amines 1 and propargylic carbonates 2 to oxazolidin-2-ones 3 with a scope-level 70-92% yield statement; classified as a general scheme, not a batch experiment.", "evidence_ids": ev(1)},
                {"region": "lower two-column introduction and references", "finding": "Background and cited prior syntheses only; no new experimental batch or outcome is reported on this page.", "evidence_ids": ev(1)},
            ],
            "record_ids": ids("graphical_abstract"),
            "unresolved": ["Generic R-group structures prevent unique product SMILES assignment."]
        },
        {
            "page": 2,
            "state": "attempted",
            "regions": [
                {"region": "upper-left Scheme 1 and adjacent retrosynthetic prose", "finding": "Conceptual CO2-recycling/selectivity map containing desired product 3, alternative products 4-6, Int 1, and CO2; classified as a general scheme rather than experimental rows.", "evidence_ids": ev(2)},
                {"region": "right column Table 1, reaction drawing, rows 1-14, and footnotes", "finding": "Fourteen independent optimization experiments extracted, including catalyst/ligand, solvent, base, temperature, carbonate-equivalent overrides, NMR yields, and the entry-1 isolated yield.", "evidence_ids": ev(2)},
                {"region": "lower-left citations and prior-work discussion", "finding": "Cited literature examples and reviews were not imported as experiments of this paper.", "evidence_ids": ev(2)},
            ],
            "record_ids": ids("scheme1_") + ids("table1_"),
            "unresolved": ["Main-text rows omit atmosphere, workup, purification, and most exact masses.", "No Supporting Information file was explicitly supplied or associated."]
        },
        {
            "page": 3,
            "state": "attempted",
            "regions": [
                {"region": "upper-left Table 2 reaction drawing, rows 1-12, and footnotes", "finding": "Twelve independent substrate-scope experiments extracted; isolated yields, gram-scale entry 2, and the 1d hydrochloride/base override in entry 12 were retained.", "evidence_ids": ev(3)},
                {"region": "upper-right Scheme 2 and adjacent prose", "finding": "One experiment of 1e with 2a gives Z-3ea and E-3ea with separate reported yields and a crude-mixture Z/E ratio; product-specific outcomes are linked to each stereoisomer.", "evidence_ids": ev(3)},
                {"region": "middle-right Table 3 reaction drawing, rows 1-4, and footnotes", "finding": "Four independent catalyst/ligand screening experiments extracted with row-specific times and NMR yields.", "evidence_ids": ev(3)},
                {"region": "lower-right Scheme 3 arrows and labels", "finding": "Two independent improved-condition reactions extracted for 1f and 1g with different times and products/yields.", "evidence_ids": ev(3)},
                {"region": "lower-left and inter-table Results and Discussion prose", "finding": "Narrative scope and optimization statements were reconciled to the corresponding table/scheme records and were not duplicated.", "evidence_ids": ev(3)},
            ],
            "record_ids": ids("table2_") + ids("scheme2_") + ids("table3_") + ids("scheme3_"),
            "unresolved": ["Scheme 2 does not explicitly state the basis of its 55% and 10% yields.", "Scheme 3 omits scale, DMSO volume, atmosphere, workup, purification, and yield basis.", "Many R-group-derived product structures require source-level chemical review."]
        },
        {
            "page": 4,
            "state": "attempted",
            "regions": [
                {"region": "upper-left Scheme 4 and upper-right mechanism prose", "finding": "Two proposed catalytic pathways through Int 1-4 were captured as one mechanism record; no branch was treated as a separate batch or assigned an experimental yield.", "evidence_ids": ev(4)},
                {"region": "middle-right conclusion, acknowledgments, and Supporting Information notice", "finding": "Conclusion summarizes the method; the page states that Supporting Information exists, but no SI file was supplied or explicitly associated, so no SI-only details were imported.", "evidence_ids": ev(4)},
                {"region": "lower-left references", "finding": "References are prior work and were not imported as experiments of this paper.", "evidence_ids": ev(4)},
            ],
            "record_ids": ids("scheme4_"),
            "unresolved": ["Proposed organopalladium intermediate structures remain generic and unverified.", "Supporting Information procedures and characterization remain unavailable in this dataset."]
        },
    ],
}
COVERAGE.parent.mkdir(parents=True, exist_ok=True)
COVERAGE.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

tasks = json.loads(TASKS.read_text())
for task in tasks:
    if task.get("document_id") == DOC and task.get("task_id", "").startswith(f"{DOC}:page"):
        task["state"] = "attempted"
        task["reason"] = "Original page image inspected; experiments, schemes, tables, footnotes, prose, and unresolved details logged in coverage/pages_0001_0004.json."
TASKS.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"records": len(records), "coverage_pages": [p["page"] for p in coverage["pages"]]}, ensure_ascii=False))
