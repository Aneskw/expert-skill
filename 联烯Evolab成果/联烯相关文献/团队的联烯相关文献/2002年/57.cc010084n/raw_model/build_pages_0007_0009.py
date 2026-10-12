#!/usr/bin/env python3
"""Build evidence-linked records for cc010084n PDF pages 7-9.

This batch enriches existing cross-page experiments rather than duplicating them,
and adds the four detailed support-loading preparations first reported on pages
7-8. Page 9 contains references only.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / "runs/current"
DOC = "doc_d48f453fffb612b1"
DATASET = RUN / "dataset.json"
OUT = RUN / "raw_model/extracted_records_pages_0007_0009.json"
COVERAGE = RUN / "coverage/pages_0007_0009.json"


def evid(page: int) -> list[str]:
    return [f"{DOC}:page{page}:text", f"{DOC}:page{page}:image"]


def fact(value, evidence=None):
    return {
        "value": value,
        "evidence_ids": list(evidence or []) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def fld(name, value, evidence=None, targets=None):
    result = {"name": name, "fact": fact(value, evidence)}
    if targets:
        result["target_entity_ids"] = list(targets)
    return result


def qty(number, unit, **extra):
    return {"number": number, "unit": unit, **extra}


def part(entity_id, role, label, name, evidence, amounts=None, smiles=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence) if label is not None else fact(None),
        "name": fact(name, evidence) if name is not None else fact(None),
        "smiles": fact(smiles, evidence) if smiles is not None else fact(None),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": list(amounts or []),
    }


def rec(source_id, evidence, participants, steps, outcomes=None, notes=None, unresolved=None):
    return {
        "record_id": f"{DOC}:{source_id}",
        "document_id": DOC,
        "source_reaction_id": source_id,
        "record_kind": "reported_experiment",
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": list(dict.fromkeys(evidence)),
        "participants": participants,
        "steps": steps,
        "outcomes": list(outcomes or []),
        "notes": [fact(x, evidence) for x in (notes or [])],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": list(unresolved or []),
        },
    }


COMMON_UNRESOLVED = [
    "Supporting Information is mentioned by the article but was not supplied or explicitly associated.",
    "Polymer-supported structures remain represented by source labels; all candidate molecular structures remain unverified.",
]


data = json.loads(DATASET.read_text())
existing = {r["source_reaction_id"]: r for r in data["experiments"]}
records = []


def get(source_id: str):
    record = copy.deepcopy(existing[source_id])
    record["status"] = "candidate"
    record["review"]["method"] = "none"
    record["review"]["reviewer"] = None
    record["review"]["checked_fields"] = []
    records.append(record)
    return record


def add_evidence(record, page: int):
    for evidence_id in evid(page):
        if evidence_id not in record["evidence_ids"]:
            record["evidence_ids"].append(evidence_id)


def participant(record, entity_id: str):
    return next(p for p in record["participants"] if p["entity_id"] == entity_id)


def step(record, step_id: str):
    return next(s for s in record["steps"] if s["step_id"] == step_id)


def add_amount(record, entity_id: str, name: str, value, evidence):
    participant(record, entity_id)["amounts"].append(fld(name, value, evidence))


def set_product_identity(record, name: str, smiles: str, evidence):
    product = participant(record, "product")
    product["name"] = fact(name, evidence)
    product["smiles"] = fact(smiles, evidence)
    product["smiles_parseable"] = None
    product["structure_verified"] = False


# Page 7: completion of Table 2 entry 8 (Conditions B and AlCl3 cleavage).
ev7 = evid(7)
t2e8 = get("table2_entry08")
add_evidence(t2e8, 7)
add_amount(t2e8, "intermediate", "mass", qty(173, "mg"), ev7)
add_amount(t2e8, "intermediate", "amount", qty(0.20, "mmol"), ev7)
add_amount(t2e8, "dcm", "volume", qty(4, "mL"), ev7)
add_amount(t2e8, "cleavage_reagent", "concentration", qty(0.50, "M"), ev7)
add_amount(t2e8, "cleavage_reagent", "amount", qty(2.0, "mmol"), ev7)
add_amount(t2e8, "cleavage_solvent", "solution_volume", qty(4, "mL"), ev7)
step(t2e8, "coupling_cyclization")["conditions"].append(
    fld("workup", "cool to room temperature; filter; wash with DMF, 1:1 DMF/H2O, H2O, DMF, and MeOH; dry under high vacuum overnight", ev7)
)
step(t2e8, "cleavage")["conditions"].extend([
    fld("pre_treatment_time", qty(30, "min"), ev7),
    fld("pre_treatment_temperature", "r.t.", ev7),
    fld("operation", "swell resin in CH2Cl2; cool to 0 °C; add AlCl3 solution in MeNO2; stir at 0 °C", ev7),
    fld("workup", "filter; wash resin with EtOAc; wash filtrate twice with 0.5 N HCl; extract aqueous layer with EtOAc; combine, dry, and evaporate extracts", ev7),
])
t2e8["outcomes"].extend([
    fld("intermediate_mass", qty(173, "mg"), ev7, ["intermediate"]),
    fld("product_mass", qty(34, "mg"), ev7, ["product"]),
])
set_product_identity(
    t2e8,
    "5-ethyl-4-(4-carboxyphenyl)-3-methyl-5-phenyl-2(5H)-furanone (6cp)",
    "O=C1OC(CC)(c2ccccc2)C(c3ccc(C(=O)O)cc3)=C1C",
    ev7,
)
t2e8["notes"].append(fact("Page 7 completes the page-6 Conditions B procedure, cleavage, and characterization of 6cp.", ev7))
t2e8["review"]["unresolved"] = [
    x for x in t2e8["review"]["unresolved"]
    if "continue on page 7" not in x
]


# Page 7: detailed preparation of phenolic-ether-linked resin 7b.
records.append(rec(
    "page7_anchor_resin7b_typical",
    ev7,
    [
        part("merrifield", "reactant", None, "Merrifield resin", ev7, [
            fld("mass", qty(4.000, "g"), ev7), fld("amount", qty(10.00, "mmol"), ev7),
        ]),
        part("iodophenol", "reactant", None, "3-iodophenol", ev7, [
            fld("mass", qty(4.404, "g"), ev7), fld("amount", qty(20.00, "mmol"), ev7),
        ], "Oc1cccc(I)c1"),
        part("meona", "reagent", "CH3ONa", "sodium methoxide", ev7, [
            fld("mass", qty(2.160, "g"), ev7), fld("amount", qty(40.00, "mmol"), ev7),
        ], "C[O-].[Na+]"),
        part("dmf", "solvent", "DMF", "N,N-dimethylformamide", ev7, [fld("volume", qty(120, "mL"), ev7)], "CN(C)C=O"),
        part("resin7b", "product", "7b", "phenolic-ether-linked polymer-supported 3-iodophenyl resin 7b", ev7),
    ],
    [{
        "step_id": "anchoring",
        "participant_ids": ["merrifield", "iodophenol", "meona", "dmf", "resin7b"],
        "conditions": [
            fld("reaction_temperature", qty(80, "°C"), ev7),
            fld("reaction_time", qty(24, "h"), ev7),
            fld("workup", "cool to room temperature; filter; wash with DMF, DMF/H2O, H2O, DMF, and MeOH; dry under vacuum overnight", ev7),
        ],
    }],
    [fld("product_mass", qty(5.343, "g"), ev7, ["resin7b"])],
    ["The reported maximum loading of resin 7b is 1.714 mequiv/g; the unsupported compound unit is preserved in this note."],
    COMMON_UNRESOLVED + ["The reported loading unit mequiv/g is not supported by the quantity schema and remains unstructured."],
))


# Page 7: detailed Conditions A experiment underlying Table 3 entry 11.
t3e11 = get("table3_entry11")
add_evidence(t3e11, 7)
for entity_id, values in {
    "resin": [("mass", qty(92, "mg")), ("amount", qty(0.15, "mmol"))],
    "acid": [("mass", qty(84, "mg")), ("amount", qty(0.60, "mmol"))],
    "base": [("volume", qty(0.21, "mL")), ("amount", qty(1.20, "mmol"))],
    "pd": [("mass", qty(26, "mg")), ("amount", qty(22.5, "umol"))],
    "solvent": [("volume", qty(4, "mL"))],
    "intermediate": [("mass", qty(92, "mg"))],
}.items():
    for name, value in values:
        add_amount(t3e11, entity_id, name, value, ev7)
step(t3e11, "coupling_cyclization")["conditions"].append(
    fld("workup", "cool to room temperature; filter; wash with DMF, 1:1 DMF/H2O, H2O, DMF, and MeOH; dry under high vacuum overnight", ev7)
)
t3e11["outcomes"].append(fld("intermediate_mass", qty(92, "mg"), ev7, ["intermediate"]))
t3e11["notes"].append(fact("Page 7 gives the detailed Conditions A coupling-cyclization producing resin 8bd; its cleavage remains represented by the separately reported general procedure.", ev7))


# Page 7: detailed Conditions C and cleavage experiment underlying Table 3 entry 22.
t3e22 = get("table3_entry22")
add_evidence(t3e22, 7)
for entity_id, values in {
    "resin": [("mass", qty(92, "mg")), ("amount", qty(0.15, "mmol"))],
    "acid": [("mass", qty(122, "mg")), ("amount", qty(0.60, "mmol"))],
    "base": [("volume", qty(0.21, "mL")), ("amount", qty(1.20, "mmol"))],
    "pd": [("mass", qty(26, "mg")), ("amount", qty(22.5, "umol"))],
    "solvent": [("volume", qty(4, "mL"))],
    "intermediate": [("mass", qty(100, "mg")), ("amount", qty(0.15, "mmol"))],
    "znbr2": [("mass", qty(17, "mg")), ("amount", qty(75.6, "umol"))],
    "acetyl_bromide": [("concentration", qty(0.15, "M")), ("amount", qty(0.30, "mmol"))],
    "dcm": [("solution_volume", qty(2, "mL"))],
}.items():
    for name, value in values:
        add_amount(t3e22, entity_id, name, value, ev7)
step(t3e22, "coupling_cyclization")["conditions"].append(
    fld("workup", "cool to room temperature; filter; wash with DMF, 1:1 DMF/H2O, H2O, DMF, and MeOH; dry under high vacuum overnight", ev7)
)
step(t3e22, "cleavage")["conditions"].extend([
    fld("atmosphere", "argon", ev7),
    fld("workup", "filter resin; wash filtrate successively with 5% NaHCO3, 5% HCl, and saturated NaCl; dry, filter, and concentrate the organic layer", ev7),
])
t3e22["outcomes"].append(fld("intermediate_mass", qty(100, "mg"), ev7, ["intermediate"]))
set_product_identity(
    t3e22,
    "4-(3-acetoxyphenyl)-5-ethyl-3-methyl-5-phenyl-2(5H)-furanone (9bp)",
    "O=C1OC(CC)(c2ccccc2)C(c3cccc(OC(C)=O)c3)=C1C",
    ev7,
)
t3e22["notes"].append(fact("Page 7 reports the detailed Conditions C preparation of 8bp, ZnBr2/acetyl bromide cleavage, and characterization of 9bp.", ev7))


# Page 7: detailed preparation of benzyl-ether-linked resin 10c.
records.append(rec(
    "page7_anchor_resin10c_typical",
    ev7,
    [
        part("merrifield", "reactant", None, "Merrifield resin", ev7, [
            fld("mass", qty(1.007, "g"), ev7), fld("amount", qty(2.50, "mmol"), ev7),
        ]),
        part("iodobenzyl_alcohol", "reactant", None, "4-iodobenzyl alcohol", ev7, [
            fld("mass", qty(1.200, "g"), ev7), fld("amount", qty(5.00, "mmol"), ev7),
        ], "OCc1ccc(I)cc1"),
        part("nah", "reagent", "NaH", "sodium hydride", ev7, [
            fld("mass", qty(0.180, "g"), ev7), fld("amount", qty(7.50, "mmol"), ev7),
        ], "[Na+].[H-]"),
        part("thf", "solvent", "THF", "tetrahydrofuran", ev7, [fld("volume", qty(30, "mL"), ev7)], "C1CCOC1"),
        part("resin10c", "product", "10c", "benzyl-ether-linked polymer-supported aryl iodide resin 10c", ev7),
    ],
    [{
        "step_id": "anchoring",
        "participant_ids": ["merrifield", "iodobenzyl_alcohol", "nah", "thf", "resin10c"],
        "conditions": [
            fld("reaction_temperature", "reflux", ev7),
            fld("reaction_time", qty(3, "d"), ev7),
            fld("workup", "cool to room temperature; filter; wash with DMF, 1:1 DMF/H2O, H2O, DMF, and MeOH; dry under vacuum overnight", ev7),
        ],
    }],
    [fld("product_mass", qty(1.385, "g"), ev7, ["resin10c"])],
    ["The reported loading of resin 10c is 1.674 mequiv/g; the unsupported compound unit is preserved in this note."],
    COMMON_UNRESOLVED + ["The reported loading unit mequiv/g is not supported by the quantity schema and remains unstructured."],
))


# Page 7: detailed prior cleavage experiment producing benzyl acetate III.
scheme6a = get("scheme6_entry_a")
add_evidence(scheme6a, 7)
for entity_id, values in {
    "dcm": [("volume", qty(2, "mL"))],
    "znbr2": [("mass", qty(12, "mg"))],
    "acbr": [("volume", qty(15, "uL"))],
}.items():
    for name, value in values:
        add_amount(scheme6a, entity_id, name, value, ev7)
step(scheme6a, "cleavage")["conditions"].append(
    fld("purification", "PTLC, ether/n-hexane = 1:4", ev7)
)
scheme6a["outcomes"].extend([
    fld("crude_product_mass", qty(29, "mg"), ev7, ["iii"]),
    fld("purified_product_mass", qty(22, "mg"), ev7, ["iii"]),
])
iii = participant(scheme6a, "iii")
iii["name"] = fact("4-(4-acetoxymethylphenyl)-5-(n-heptyl)-2(5H)-furanone (III)", ev7)
iii["smiles"] = fact("O=C1OC(CCCCCCC)C(c2ccc(COC(C)=O)cc2)=C1", ev7)
scheme6a["notes"].append(fact("Page 7 provides the detailed workup, PTLC purification, and characterization for the cited Scheme 6 entry a product III.", ev7))


# Pages 7-8: detailed cleavage and characterization of Table 4 entry 10.
t4e10 = get("table4_entry10")
add_evidence(t4e10, 7)
add_evidence(t4e10, 8)
for entity_id, values in {
    "intermediate": [("mass", qty(100, "mg")), ("amount", qty(0.15, "mmol"))],
    "znbr2": [("mass", qty(17, "mg")), ("amount", qty(75.6, "umol"))],
    "acetyl_bromide": [("concentration", qty(0.30, "M")), ("amount", qty(0.90, "mmol"))],
    "dcm": [("solution_volume", qty(3, "mL"))],
}.items():
    for name, value in values:
        add_amount(t4e10, entity_id, name, value, ev7)
step(t4e10, "cleavage")["conditions"].extend([
    fld("atmosphere", "argon", ev7),
    fld("workup", "filter resin; wash filtrate successively with 5% NaHCO3, 5% HCl, and saturated NaCl; dry, filter, and concentrate the organic layer", ev7),
])
set_product_identity(
    t4e10,
    "4-(4-bromomethylphenyl)-5-ethyl-3-methyl-5-phenyl-2(5H)-furanone (12cp)",
    "O=C1OC(CC)(c2ccccc2)C(c3ccc(CBr)cc3)=C1C",
    evid(8),
)
t4e10["notes"].append(fact("Page 7 explicitly assigns Conditions C to acids 2o and 2p and gives the detailed cleavage of 11cp; page 8 completes the characterization of 12cp.", ev7 + evid(8)))
t4e10["review"]["unresolved"] = [
    x for x in t4e10["review"]["unresolved"]
    if "Condition assignment for Table 4 entries 9-10" not in x
]


# Page 8: detailed preparation of the DHP-functionalized resin.
ev8 = evid(8)
records.append(rec(
    "page8_prepare_DHP_resin_typical",
    ev8,
    [
        part("dhp_alcohol", "reactant", None, "(2-hydroxymethyl)-3,4-dihydro-2H-pyran", ev8, [
            fld("mass", qty(1.710, "g"), ev8), fld("amount", qty(15.0, "mmol"), ev8),
        ], "OCC1OCCC=C1"),
        part("nah", "reagent", "NaH", "sodium hydride", ev8, [
            fld("mass", qty(0.480, "g"), ev8), fld("amount", qty(20.0, "mmol"), ev8),
        ], "[Na+].[H-]"),
        part("dma", "solvent", "DMA", "N,N-dimethylacetamide", ev8, [fld("volume", qty(75, "mL"), ev8)], "CC(=O)N(C)C"),
        part("merrifield", "reactant", None, "Merrifield resin", ev8, [
            fld("mass", qty(2.000, "g"), ev8), fld("amount", qty(5.00, "mmol"), ev8),
        ]),
        part("dhp_resin", "product", None, "DHP-functionalized resin", ev8),
    ],
    [
        {
            "step_id": "alkoxide_formation",
            "participant_ids": ["dhp_alcohol", "nah", "dma"],
            "conditions": [fld("reaction_temperature", "r.t.", ev8), fld("reaction_time", qty(30, "min"), ev8)],
        },
        {
            "step_id": "resin_loading",
            "participant_ids": ["dhp_alcohol", "nah", "dma", "merrifield", "dhp_resin"],
            "conditions": [
                fld("operation", "add Merrifield resin after the initial 30 min alkoxide-forming period", ev8),
                fld("reaction_temperature", "r.t.", ev8),
                fld("reaction_time", qty(16, "h"), ev8),
                fld("workup", "filter; wash with CH2Cl2, 1:1 DMF/H2O, DMF, and CH2Cl2; dry under vacuum overnight", ev8),
            ],
        },
    ],
    [fld("product_mass", qty(2.236, "g"), ev8, ["dhp_resin"])],
    ["The reported maximum loading of the DHP resin is 2.094 mequiv/g; the unsupported compound unit is preserved in this note."],
    COMMON_UNRESOLVED + ["The reported loading unit mequiv/g is not supported by the quantity schema and remains unstructured."],
))


# Page 8: detailed anchoring of 4-iodophenol to DHP resin, producing 14c.
records.append(rec(
    "page8_anchor_resin14c_typical",
    ev8,
    [
        part("dhp_resin", "reactant", None, "DHP-functionalized resin", ev8, [
            fld("mass", qty(1.000, "g"), ev8), fld("amount", qty(2.094, "mmol"), ev8),
        ]),
        part("iodophenol", "reactant", None, "4-iodophenol", ev8, [
            fld("mass", qty(2.304, "g"), ev8), fld("amount", qty(10.47, "mmol"), ev8),
        ], "Oc1ccc(I)cc1"),
        part("ppts", "reagent", "PPTS", "pyridinium p-toluenesulfonate", ev8, [
            fld("mass", qty(1.047, "g"), ev8), fld("amount", qty(4.29, "mmol"), ev8),
        ]),
        part("dce", "solvent", None, "1,2-dichloroethane", ev8, [fld("volume", qty(21, "mL"), ev8)], "ClCCCl"),
        part("resin14c", "product", "14c", "phenolic THP-linked polymer-supported aryl iodide resin 14c", ev8),
    ],
    [{
        "step_id": "anchoring",
        "participant_ids": ["dhp_resin", "iodophenol", "ppts", "dce", "resin14c"],
        "conditions": [
            fld("reaction_temperature", qty(80, "°C"), ev8),
            fld("reaction_time", qty(16, "h"), ev8),
            fld("workup", "cool to room temperature; filter; wash with CH2Cl2, 1:1 DMF/H2O, DMF, and CH2Cl2; dry under vacuum overnight", ev8),
        ],
    }],
    [fld("product_mass", qty(1.117, "g"), ev8, ["resin14c"])],
    ["The reported maximum loading of resin 14c is 1.434 mequiv/g; the unsupported compound unit is preserved in this note."],
    COMMON_UNRESOLVED + ["The reported loading unit mequiv/g is not supported by the quantity schema and remains unstructured."],
))


# Page 8: detailed Conditions D and cleavage experiment underlying Table 5 entry 12.
t5e12 = get("table5_entry12")
add_evidence(t5e12, 8)
for entity_id, values in {
    "resin": [("mass", qty(140, "mg")), ("amount", qty(0.20, "mmol"))],
    "base": [("volume", qty(0.28, "mL")), ("amount", qty(1.60, "mmol"))],
    "acid": [("mass", qty(146, "mg")), ("amount", qty(0.80, "mmol"))],
    "pd": [("mass", qty(36, "mg")), ("amount", qty(30, "umol"))],
    "solvent": [("initial_volume", qty(2, "mL")), ("additional_volume", qty(2, "mL"))],
    "intermediate": [("mass", qty(241, "mg"))],
    "dcm": [("cleavage_solution_volume", qty(4, "mL"))],
}.items():
    for name, value in values:
        add_amount(t5e12, entity_id, name, value, ev8)
step(t5e12, "coupling_cyclization")["conditions"].append(
    fld("workup", "cool to room temperature; filter; wash with DMF, 1:1 DMF/H2O, H2O, DMF, and MeOH; dry under high vacuum overnight", ev8)
)
step(t5e12, "cleavage")["conditions"].append(
    fld("workup", "filter; wash filtrate twice with saturated NaHCO3; extract aqueous phase twice with CH2Cl2; combine organic layers, dry over Na2SO4, filter, and concentrate", ev8)
)
t5e12["outcomes"].extend([
    fld("intermediate_mass", qty(241, "mg"), ev8, ["intermediate"]),
    fld("product_mass", qty(23, "mg"), ev8, ["product"]),
])
set_product_identity(
    t5e12,
    "5-(n-heptyl)-4-(4-hydroxyphenyl)-2(5H)-furanone (18ca)",
    "O=C1OC(CCCCCCC)C(c2ccc(O)cc2)=C1",
    ev8,
)
t5e12["notes"].append(fact("Page 8 reports the detailed Conditions D coupling, TFA cleavage, and characterization of 18ca.", ev8))


# Exact coverage for this session only. Page 9 was visually inspected and contains references, not experiments.
coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 7,
            "state": "attempted",
            "regions": [
                {
                    "region": "left column top, continuation of Conditions B and AlCl3 cleavage/6cp characterization",
                    "finding": "Continuation of the existing Table 2 entry 8 experiment; workup, cleavage quantities, 34 mg product, 70% overall yield, 93% purity, and characterization were merged into the existing record.",
                    "evidence_ids": ev7,
                },
                {
                    "region": "left column middle, anchoring iodophenol to Merrifield resin",
                    "finding": "Independent detailed preparation of loaded resin 7b from Merrifield resin, 3-iodophenol, sodium methoxide, and DMF.",
                    "evidence_ids": ev7,
                },
                {
                    "region": "left column lower half through right column upper half, phenol-ether Conditions A/C and ZnBr2 cleavage",
                    "finding": "Detailed executions corresponding to Table 3 entries 11 and 22; entry 22 includes the cleavage and characterization of 9bp.",
                    "evidence_ids": ev7,
                },
                {
                    "region": "right column middle, anchoring iodobenzyl alcohol and cross-referenced coupling procedure",
                    "finding": "Independent detailed preparation of resin 10c; the following coupling paragraph explicitly reuses the phenol-ether procedure and does not constitute a new standalone substrate experiment.",
                    "evidence_ids": ev7,
                },
                {
                    "region": "right column lower half, cleavage to III and cleavage of 11cp",
                    "finding": "Detailed purification of cited Scheme 6 entry a was merged into that literature-example record; the 11cp cleavage was merged into Table 4 entry 10 and continues on page 8.",
                    "evidence_ids": ev7,
                },
            ],
            "record_ids": [
                t2e8["record_id"],
                f"{DOC}:page7_anchor_resin7b_typical",
                t3e11["record_id"],
                t3e22["record_id"],
                f"{DOC}:page7_anchor_resin10c_typical",
                scheme6a["record_id"],
                t4e10["record_id"],
            ],
            "unresolved": [
                "Resin loadings are reported in mequiv/g, an unsupported structured quantity unit, and are retained verbatim in notes.",
                "The phrase 'usual workup' for the III experiment is not expanded beyond the source wording; the explicitly reported PTLC purification is structured.",
            ],
        },
        {
            "page": 8,
            "state": "attempted",
            "regions": [
                {
                    "region": "left column top, continuation of 12cp characterization",
                    "finding": "Completion of the Table 4 entry 10 product name and analytical characterization; merged with page-7 cleavage evidence.",
                    "evidence_ids": ev8,
                },
                {
                    "region": "left column upper-middle, DHP resin preparation",
                    "finding": "Independent two-stage detailed preparation of DHP-functionalized resin, including the initial 30 min alkoxide formation and 16 h resin loading.",
                    "evidence_ids": ev8,
                },
                {
                    "region": "left column middle, anchoring 4-iodophenol to DHP resin",
                    "finding": "Independent detailed preparation of loaded resin 14c with PPTS in 1,2-dichloroethane.",
                    "evidence_ids": ev8,
                },
                {
                    "region": "left column lower half, Conditions D coupling and TFA cleavage",
                    "finding": "Detailed execution corresponding to Table 5 entry 12, including significant base-before-acid order, resin 16ca isolation, cleavage, and 18ca characterization.",
                    "evidence_ids": ev8,
                },
                {
                    "region": "right column, acknowledgment, Supporting Information notice, and references 1-8",
                    "finding": "No new experiments in this region. SI is stated to exist online but was not supplied or explicitly associated, so no SI evidence was imported.",
                    "evidence_ids": ev8,
                },
            ],
            "record_ids": [
                t4e10["record_id"],
                f"{DOC}:page8_prepare_DHP_resin_typical",
                f"{DOC}:page8_anchor_resin14c_typical",
                t5e12["record_id"],
            ],
            "unresolved": [
                "Resin loadings are reported in mequiv/g, an unsupported structured quantity unit, and are retained verbatim in notes.",
                "The cited online Supporting Information was not provided and remains unassociated.",
            ],
        },
        {
            "page": 9,
            "state": "attempted",
            "regions": [
                {
                    "region": "both columns, references 8(c)-18 and article identifier",
                    "finding": "Reference list only; no experimental procedure, reaction arrow, table, footnote, or new paper-specific experiment is present.",
                    "evidence_ids": evid(9),
                }
            ],
            "record_ids": [],
            "unresolved": [],
        },
    ],
}


assert len(records) == 10, len(records)
assert len({r["record_id"] for r in records}) == len(records)
assert [p["page"] for p in coverage["pages"]] == [7, 8, 9]
assert all(p["regions"] for p in coverage["pages"])

OUT.parent.mkdir(parents=True, exist_ok=True)
COVERAGE.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
COVERAGE.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

# Mark only the three page tasks inspected in this session.
tasks_path = RUN / "tasks.json"
tasks = json.loads(tasks_path.read_text())
for task in tasks:
    if task.get("document_id") != DOC:
        continue
    for page in (7, 8, 9):
        if task.get("task_id") == f"{DOC}:page{page}:text":
            task["state"] = "attempted"
            task["visual_evidence_id"] = f"{DOC}:page{page}:image"
            task["reason"] = "Page image and text were inspected; findings and unresolved issues are recorded in coverage/pages_0007_0009.json."
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({
    "submitted_records": len(records),
    "new_record_ids": 4,
    "enriched_existing_record_ids": 6,
    "raw": str(OUT.relative_to(ROOT)),
    "coverage": str(COVERAGE.relative_to(ROOT)),
}, ensure_ascii=False))
