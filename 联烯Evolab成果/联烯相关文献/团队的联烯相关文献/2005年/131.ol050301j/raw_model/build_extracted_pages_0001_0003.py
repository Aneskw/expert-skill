#!/usr/bin/env python3
"""Build the raw machine extraction for PDF pages 1--3.

All assertions below are tied to the supplied page-text/page-image evidence.
The merge tool remains responsible for quarantining these records as
needs_review and recomputing SMILES parseability.
"""

import json
from pathlib import Path


DOC = "doc_1116ae85807a1260"
P2 = [f"{DOC}:page2:text", f"{DOC}:page2:image"]
P3 = [f"{DOC}:page3:text", f"{DOC}:page3:image"]
OUT = Path(__file__).with_name("extracted_pages_0001_0003.json")


def fact(value, evidence):
    return {
        "value": value,
        "evidence_ids": list(evidence) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def field(name, value, evidence, targets=None):
    item = {"name": name, "fact": fact(value, evidence)}
    if targets:
        item["target_entity_ids"] = targets
    return item


def participant(entity_id, role, label, name, smiles, evidence, amounts=None):
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


def common_agents(evidence, include_silver=True):
    agents = [
        participant(
            "pd_pph3_4", "catalyst", "Pd(PPh3)4", "tetrakis(triphenylphosphine)palladium(0)",
            None, evidence, [field("amount", {"number": 5, "unit": "mol%"}, evidence)],
        )
    ]
    if include_silver:
        agents.append(
            participant(
                "ag2co3", "catalyst", "Ag2CO3", "silver carbonate", None, evidence,
                [field("amount", {"number": 5, "unit": "mol%"}, evidence)],
            )
        )
    agents.append(
        participant(
            "k2co3", "reagent", "K2CO3", "potassium carbonate", None, evidence,
            [field("equivalents", {"number": 4, "unit": "equiv"}, evidence)],
        )
    )
    return agents


def solvent_participant(solvent, evidence):
    names = {
        "toluene": "toluene", "THF": "tetrahydrofuran", "dioxane": "dioxane",
        "MeCN": "acetonitrile", "DMF": "N,N-dimethylformamide",
    }
    smiles = {
        "toluene": "Cc1ccccc1", "THF": "C1CCOC1", "dioxane": "C1COCCO1",
        "MeCN": "CC#N", "DMF": "CN(C)C=O",
    }
    return participant("solvent", "solvent", solvent, names[solvent], smiles[solvent], evidence)


ALLENES = {
    "1a": ("1,2-pentadienyl phenyl sulfone", "CCC=C=CS(=O)(=O)c1ccccc1"),
    "1b": ("1,2-allenic phenyl sulfone, R1 = Me", "CC=C=CS(=O)(=O)c1ccccc1"),
    "1c": ("1,2-allenic phenyl sulfone, R1 = n-pentyl", "CCCCCC=C=CS(=O)(=O)c1ccccc1"),
    "1d": ("3,3-disubstituted 1,2-allenic phenyl sulfone, R1 = Me, R2 = Et", "CCC(C)=C=CS(=O)(=O)c1ccccc1"),
    "1e": ("3,3-disubstituted 1,2-allenic phenyl sulfone, R1 = Et, R2 = Et", "CCC(CC)=C=CS(=O)(=O)c1ccccc1"),
    "1g": ("3,3-disubstituted 1,2-allenic phenyl sulfone, R1 = Et, R2 = Ph", "CCC(c1ccccc1)=C=CS(=O)(=O)c1ccccc1"),
}

ARYL_IODIDES = {
    "2a": ("PhI", "iodobenzene", "Ic1ccccc1"),
    "2b": ("p-MeC6H4I", "4-iodotoluene", "Cc1ccc(I)cc1"),
    "2c": ("p-MeCO2C6H4I", "methyl 4-iodobenzoate", "COC(=O)c1ccc(I)cc1"),
    "2d": ("p-MeCOC6H4I", "4-iodoacetophenone", "CC(=O)c1ccc(I)cc1"),
    "2e": ("p-ClC6H4I", "1-chloro-4-iodobenzene", "Clc1ccc(I)cc1"),
    "2f": ("p-BrC6H4I", "1-bromo-4-iodobenzene", "Brc1ccc(I)cc1"),
}

PRODUCTS = {
    "3a": ("1,3-diphenyl-1,2-pentadienyl phenyl sulfone", "CCC(c1ccccc1)=C=C(c1ccccc1)S(=O)(=O)c1ccccc1"),
    "3b": ("1,3-diphenylated allenyl phenyl sulfone, R1 = Me", "CC(c1ccccc1)=C=C(c1ccccc1)S(=O)(=O)c1ccccc1"),
    "3c": ("1,3-diphenylated allenyl phenyl sulfone, R1 = n-pentyl", "CCCCCC(c1ccccc1)=C=C(c1ccccc1)S(=O)(=O)c1ccccc1"),
    "3d": ("1,3-bis(p-tolyl) allenyl phenyl sulfone, R1 = Et", "CCC(c1ccc(C)cc1)=C=C(c1ccc(C)cc1)S(=O)(=O)c1ccccc1"),
    "3e": ("1,3-bis(p-CO2Me-phenyl) allenyl phenyl sulfone, R1 = Et", "CCC(c1ccc(C(=O)OC)cc1)=C=C(c1ccc(C(=O)OC)cc1)S(=O)(=O)c1ccccc1"),
    "3f": ("1,3-bis(p-Ac-phenyl) allenyl phenyl sulfone, R1 = Et", "CCC(c1ccc(C(C)=O)cc1)=C=C(c1ccc(C(C)=O)cc1)S(=O)(=O)c1ccccc1"),
    "3g": ("1,3-bis(p-chlorophenyl) allenyl phenyl sulfone, R1 = Et", "CCC(c1ccc(Cl)cc1)=C=C(c1ccc(Cl)cc1)S(=O)(=O)c1ccccc1"),
    "3h": ("1,3-bis(p-bromophenyl) allenyl phenyl sulfone, R1 = Et", "CCC(c1ccc(Br)cc1)=C=C(c1ccc(Br)cc1)S(=O)(=O)c1ccccc1"),
    "4a": ("monoarylation product 4a (R1 = Me, R2 = Et)", "CCC(C)=C=C(c1ccccc1)S(=O)(=O)c1ccccc1"),
    "4b": ("monoarylation product 4b (R1 = Et, R2 = Et)", "CCC(CC)=C=C(c1ccccc1)S(=O)(=O)c1ccccc1"),
}


def allene(label, evidence, scale=None):
    name, smiles = ALLENES[label]
    amounts = [field("amount", scale, evidence)] if scale else []
    return participant("allene", "reactant", label, name, smiles, evidence, amounts)


def aryl_iodide(label, evidence, equiv):
    shown, name, smiles = ARYL_IODIDES[label]
    return participant(
        "aryl_iodide", "reactant", label, f"{name} ({shown})", smiles, evidence,
        [field("equivalents", {"number": equiv, "unit": "equiv"}, evidence)],
    )


def product(label, evidence, name=None, smiles=None):
    if name is None:
        name, smiles = PRODUCTS[label]
    return participant("product", "product", label, name, smiles, evidence)


def base_record(record_id, source_id, kind, evidence, participants, conditions, outcomes, unresolved, notes=None):
    return {
        "record_id": f"{DOC}:{record_id}",
        "document_id": DOC,
        "source_reaction_id": source_id,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": list(evidence),
        "participants": participants,
        "steps": [{
            "step_id": "reaction",
            "participant_ids": [p["entity_id"] for p in participants],
            "conditions": conditions,
        }],
        "outcomes": outcomes,
        "notes": [fact(x, evidence) for x in (notes or [])],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved,
        },
    }


def table1_record(entry, solvent, temperature, time_h, yield_pct, include_silver=True, duplicate_p3=False):
    evidence = P2 + P3 if duplicate_p3 else P2
    scale = {"minimum": 0.3, "maximum": 0.6, "unit": "mmol", "raw_text": "0.3-0.6 mmol"} if duplicate_p3 else None
    participants = [
        allene("1a", evidence, scale),
        aryl_iodide("2a", evidence, 1),
        product("3a", evidence),
        *common_agents(evidence, include_silver=include_silver),
        solvent_participant(solvent, evidence),
    ]
    conditions = [
        field("solvent", solvent, evidence),
        field("temperature", temperature, evidence),
        field("time", {"number": time_h, "unit": "h"}, evidence),
        field("atmosphere", "N2", evidence),
    ]
    outcomes = [
        field("isolated_yield", {"number": yield_pct, "unit": "%"}, evidence, ["product"]),
        field("yield_measurement_basis", "isolated yield based on PhI", P2, ["product"]),
    ]
    notes = []
    unresolved = [
        "No explicitly associated SI was provided; exact allene charge, setup, workup, purification, and characterization details are missing.",
        "All molecular structures are unverified machine interpretations of the depicted structures/labels.",
    ]
    if entry == 1:
        notes.append("The prose reports the toluene/80 °C/3 h/6% result but calls it entry 4; Table 1 visibly lists it as entry 1.")
        unresolved.append("The prose/table entry-number discrepancy for the 6% toluene result requires external source review.")
    if entry == 6:
        notes.append("Table 1 footnote b: reaction conducted in the absence of Ag2CO3.")
    if entry == 8:
        outcomes.append(field("monophenylation_product_detection", "not detected", P2))
    rid = "table1-entry5_table2-entry1" if duplicate_p3 else f"table1-entry{entry}"
    sid = "Table 1 entry 5 / Table 2 entry 1" if duplicate_p3 else f"Table 1 entry {entry}"
    return base_record(rid, sid, "optimization_entry", evidence, participants, conditions, outcomes, unresolved, notes)


def table2_record(entry, allene_label, aryl_label, time_h, yield_pct, product_label):
    evidence = P3
    participants = [
        allene(allene_label, evidence, {"minimum": 0.3, "maximum": 0.6, "unit": "mmol", "raw_text": "0.3-0.6 mmol"}),
        aryl_iodide(aryl_label, evidence, 1),
        product(product_label, evidence),
        *common_agents(evidence),
        solvent_participant("DMF", evidence),
    ]
    conditions = [
        field("solvent", "DMF", evidence),
        field("temperature", {"number": 80, "unit": "°C"}, evidence),
        field("time", {"number": time_h, "unit": "h"}, evidence),
        field("atmosphere", "N2", evidence),
    ]
    outcomes = [
        field("isolated_yield", {"number": yield_pct, "unit": "%"}, evidence, ["product"]),
        field("yield_measurement_basis", "isolated yield", evidence, ["product"]),
    ]
    unresolved = [
        "No explicitly associated SI was provided; setup, workup, purification, and characterization details are missing.",
        "The 0.3-0.6 mmol footnote gives a range, not the exact scale for this row.",
        "All molecular structures are unverified machine interpretations of the depicted generic structures and row substituents.",
    ]
    return base_record(
        f"table2-entry{entry}", f"Table 2 entry {entry}", "substrate_scope_entry", evidence,
        participants, conditions, outcomes, unresolved,
    )


def scheme2_record(row, allene_label, time_h, yield_pct, product_label, product_smiles):
    evidence = P3
    participants = [
        allene(allene_label, evidence),
        aryl_iodide("2a", evidence, 0.5),
        product(product_label, evidence, f"monoarylation product printed as {product_label}", product_smiles),
        *common_agents(evidence),
        solvent_participant("DMF", evidence),
    ]
    conditions = [
        field("solvent", "DMF", evidence),
        field("temperature", {"number": 80, "unit": "°C"}, evidence),
        field("time", {"number": time_h, "unit": "h"}, evidence),
        field("atmosphere", "N2", evidence),
    ]
    outcomes = [
        field("yield", {"number": yield_pct, "unit": "%"}, evidence, ["product"]),
        field("yield_measurement_basis", None, []),
    ]
    unresolved = [
        "Scheme 2 does not state whether the reported yield is isolated or measured by another method.",
        "No explicitly associated SI was provided; exact allene scale, setup, workup, purification, and characterization details are missing.",
        "All molecular structures are unverified machine interpretations of the depicted generic structures and row substituents.",
    ]
    return base_record(
        f"scheme2-row{row}", f"Scheme 2 row {row}", "substrate_scope_entry", evidence,
        participants, conditions, outcomes, unresolved,
    )


records = [
    table1_record(1, "toluene", {"number": 80, "unit": "°C"}, 3, 6),
    table1_record(2, "THF", {"number": 80, "unit": "°C"}, 3, 4),
    table1_record(3, "dioxane", {"number": 80, "unit": "°C"}, 3, 5),
    table1_record(4, "MeCN", {"number": 80, "unit": "°C"}, 3, 77),
    table1_record(5, "DMF", {"number": 80, "unit": "°C"}, 3, 87, duplicate_p3=True),
    table1_record(6, "DMF", {"number": 80, "unit": "°C"}, 3, 11, include_silver=False),
    table1_record(7, "DMF", {"number": 60, "unit": "°C"}, 7, 70),
    table1_record(8, "DMF", "r.t.", 12, 49),
    table2_record(2, "1b", "2a", 3, 66, "3b"),
    table2_record(3, "1c", "2a", 3, 70, "3c"),
    table2_record(4, "1a", "2b", 3, 77, "3d"),
    table2_record(5, "1a", "2c", 3, 74, "3e"),
    table2_record(6, "1a", "2d", 2.5, 81, "3f"),
    table2_record(7, "1a", "2e", 2, 77, "3g"),
    table2_record(8, "1a", "2f", 2, 76, "3h"),
    scheme2_record(1, "1d", 16, 70, "4a", PRODUCTS["4a"][1]),
    scheme2_record(2, "1e", 3, 62, "4b", PRODUCTS["4b"][1]),
    scheme2_record(3, "1g", 3, 76, "3a", PRODUCTS["3a"][1]),
]

OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
print(f"wrote {len(records)} raw records to {OUT}")
