#!/usr/bin/env python3
"""Build source-linked machine extraction records for PDF pages 1-2."""
from __future__ import annotations

import json
from pathlib import Path


DOC = "doc_899532adc73b0cce"
BASE = Path(__file__).resolve().parent
P1 = [f"{DOC}:page1:text", f"{DOC}:page1:image"]
P2 = [f"{DOC}:page2:text", f"{DOC}:page2:image"]


def fact(value, evidence):
    return {
        "value": value,
        "evidence_ids": [] if value is None else list(evidence),
        "verification": "missing" if value is None else "unreviewed",
    }


def field(name, value, evidence, targets=None):
    result = {"name": name, "fact": fact(value, evidence)}
    if targets:
        result["target_entity_ids"] = list(targets)
    return result


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


def record(source_id, kind, evidence, participants, steps, outcomes, notes, unresolved):
    return {
        "record_id": f"{DOC}:{source_id}",
        "document_id": DOC,
        "source_reaction_id": source_id,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": list(evidence),
        "participants": participants,
        "steps": steps,
        "outcomes": outcomes,
        "notes": [fact(value, evidence) for value in notes],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": list(unresolved),
        },
    }


COMMON_SI = (
    "The article mentions ESI, but no supplementary file was supplied or explicitly "
    "associated with this dataset; unreported experimental details remain missing."
)


def table1_record(row):
    ev = P1
    parts = [
        participant("t1_substrate_1a", "reactant", "1a", "phenyl 1,2-propadienyl selenide", ev,
                    "C=C=C[Se]c1ccccc1"),
        participant("t1_iodine", "reagent", "I2", "iodine", ev, "II",
                    [field("equivalents", {"number": 2, "unit": "equiv"}, ev)]),
        participant("t1_product_2a", "product", "Z-2a", "Z-2a iodohydroxylation product", ev,
                    "OCC(I)=C[Se]c1ccccc1"),
        participant("t1_product_3a", "product", "Z-3a",
                    "N-(2-iodo-3-phenylseleno-2(Z)-propenyl)acetamide", ev,
                    "CC(=O)NCC(I)=C[Se]c1ccccc1"),
        participant("t1_mecn", "solvent", "MeCN", "acetonitrile", ev, "CC#N"),
    ]
    if row["entry"] == 1:
        parts.extend([
            participant("t1_water", "solvent", "H2O", "water", ev, "O"),
            participant("t1_lithium_acetate_dihydrate", "reagent", "LiOAc·2H2O",
                        "lithium acetate dihydrate", ev, None,
                        [field("equivalents", {"number": 2, "unit": "equiv"}, ev)]),
        ])
        solvent = "MeCN/H2O (7:1)"
    else:
        parts.extend([
            participant("t1_n_hexane", "solvent", "A", "n-hexane", ev, "CCCCCC"),
            participant("t1_water", "reagent", "H2O", "water", ev, "O",
                        [field("equivalents", {"number": row["water"], "unit": "equiv"}, ev)]),
        ])
        solvent = "MeCN/n-hexane (1:1); Table 1 footnote b defines A as n-hexane"

    reactive_ids = [p["entity_id"] for p in parts if p["role"] != "product"]
    step = {
        "step_id": "reaction",
        "participant_ids": reactive_ids,
        "conditions": [
            field("solvent", solvent, ev),
            field("temperature", {"number": row["temperature"], "unit": "°C"}, ev),
            field("time", {"number": row["time"], "unit": "h"}, ev),
        ],
    }
    outcomes = [
        field("yield_2a", {"number": row["yield_2a"], "unit": "%"}, ev, ["t1_product_2a"]),
        field("yield_3a", {"number": row["yield_3a"], "unit": "%"}, ev, ["t1_product_3a"]),
    ]
    if row.get("ratio_2a"):
        outcomes.extend([
            field("Z_E_ratio_2a", row["ratio_2a"], ev, ["t1_product_2a"]),
            field("Z_E_ratio_measurement_basis_2a",
                  "Determined by 300 MHz 1H NMR spectra of the crude product", ev,
                  ["t1_product_2a"]),
        ])
    if row.get("ratio_3a"):
        outcomes.extend([
            field("Z_E_ratio_3a", row["ratio_3a"], ev, ["t1_product_3a"]),
            field("Z_E_ratio_measurement_basis_3a",
                  "Determined by 300 MHz 1H NMR spectra of the crude product", ev,
                  ["t1_product_3a"]),
        ])
    unresolved = [
        COMMON_SI,
        "Yield measurement basis is not stated by the table except that the prose calls the 28% yield of 2a in entry 1 isolated.",
        "Candidate SMILES omit the alkene stereochemical encoding and remain structure-unverified.",
    ]
    if row["entry"] == 1:
        outcomes.append(field("yield_measurement_basis_2a", "isolated", ev, ["t1_product_2a"]))
    return record(
        f"table1_entry_{row['entry']}", "optimization_entry", ev, parts, [step], outcomes,
        [f"Table 1 entry {row['entry']}; zero yields are explicit reported outcomes, not missing values."],
        unresolved,
    )


TABLE1 = [
    {"entry": 1, "water": None, "temperature": 21, "time": 10, "yield_2a": 28, "ratio_2a": "12.5:1", "yield_3a": 0, "ratio_3a": None},
    {"entry": 2, "water": 8, "temperature": 25, "time": 12.5, "yield_2a": 27, "ratio_2a": "26:1", "yield_3a": 15, "ratio_3a": "30:1"},
    {"entry": 3, "water": 4, "temperature": 25, "time": 12.5, "yield_2a": 18, "ratio_2a": "20:1", "yield_3a": 36, "ratio_3a": "22:1"},
    {"entry": 4, "water": 3, "temperature": 25, "time": 11.5, "yield_2a": 22, "ratio_2a": "15:1", "yield_3a": 44, "ratio_3a": "44:1"},
    {"entry": 5, "water": 16, "temperature": 25, "time": 10, "yield_2a": 63, "ratio_2a": "6.8:1", "yield_3a": 0, "ratio_3a": None},
    {"entry": 6, "water": 12, "temperature": 25, "time": 11, "yield_2a": 60, "ratio_2a": "3.6:1", "yield_3a": 0, "ratio_3a": None},
    {"entry": 7, "water": 1, "temperature": 25, "time": 17, "yield_2a": 0, "ratio_2a": None, "yield_3a": 64, "ratio_3a": "28:1"},
]


def typical_procedure():
    ev = P1
    parts = [
        participant("tp_1a", "reactant", "1a", "phenyl 1,2-propadienyl selenide", ev,
                    "C=C=C[Se]c1ccccc1", [
                        field("mass", {"number": 195, "unit": "mg"}, ev),
                        field("amount", {"number": 1, "unit": "mmol"}, ev),
                    ]),
        participant("tp_iodine", "reagent", "I2", "iodine", ev, "II", [
            field("mass", {"number": 507.6, "unit": "mg"}, ev),
            field("amount", {"number": 2, "unit": "mmol"}, ev),
        ]),
        participant("tp_mecn", "solvent", "MeCN", "acetonitrile", ev, "CC#N", [
            field("volume", {"number": 5, "unit": "mL", "raw_text": "2 mL + 3 mL"}, ev),
        ]),
        participant("tp_n_hexane", "solvent", "n-hexane", "n-hexane", ev, "CCCCCC", [
            field("volume", {"number": 5, "unit": "mL"}, ev),
        ]),
        participant("tp_product_3a", "product", "Z-3a",
                    "N-(2-iodo-3-phenylseleno-2(Z)-propenyl)acetamide", ev,
                    "CC(=O)NCC(I)=C[Se]c1ccccc1"),
    ]
    reactive = ["tp_1a", "tp_iodine", "tp_mecn", "tp_n_hexane"]
    steps = [
        {"step_id": "addition", "participant_ids": reactive, "conditions": [
            field("operation", "The 1a solution in 2 mL MeCN was added slowly to the iodine solution in 3 mL MeCN and 5 mL n-hexane", ev),
            field("addition_time", {"number": 30, "unit": "min"}, ev),
            field("atmosphere", "N2", ev),
        ]},
        {"step_id": "reaction", "participant_ids": reactive, "conditions": [
            field("temperature", {"number": 25, "unit": "°C"}, ev),
            field("time", {"number": 9, "unit": "h"}, ev),
            field("atmosphere", "N2", ev),
        ]},
        {"step_id": "workup_and_purification", "participant_ids": [], "conditions": [
            field("workup", "Diluted with ether; saturated aqueous NaHCO3 and Na2S2O3 were added; extracted with ether (25 mL × 3); dried over MgSO4; evaporated", ev),
            field("purification", "Silica-gel column chromatography, petroleum ether/ethyl acetate = 1:1", ev),
            field("operation", "White solid; crystallization solvent CH2Cl2/n-hexane", ev),
        ]},
    ]
    outcomes = [
        field("isolated_product_form", "white solid", ev, ["tp_product_3a"]),
        field("melting_point", {"minimum": 100, "maximum": 102, "unit": "°C", "raw_text": "100–102 °C"}, ev,
              ["tp_product_3a"]),
        field("yield", None, ev, ["tp_product_3a"]),
    ]
    return record(
        "typical_procedure_z_3a", "reported_experiment", ev, parts, steps, outcomes,
        ["The printed typical procedure reports isolation of Z-3a but gives no yield in this paragraph."],
        [
            COMMON_SI,
            "No water addition or water quantity is stated in the printed typical procedure, despite the four-component reaction context.",
            "Product yield is not reported in the procedure and is retained as null/missing rather than borrowed from a table row with different reaction time.",
            "Candidate product SMILES omits alkene stereochemical encoding and remains structure-unverified.",
        ],
    )


TABLE2 = [
    {"entry": 1, "r": "C6H5", "r_name": "phenyl", "rp": "Me", "nitrile": "acetonitrile", "water": 1, "time": 10.5, "yield": 59, "product": "3a", "ratio": "≥18:1"},
    {"entry": 2, "r": "C6H5", "r_name": "phenyl", "rp": "n-Pr", "nitrile": "butanenitrile", "water": 1, "time": 10, "yield": 46, "product": "3b", "ratio": "≥21:1"},
    {"entry": 3, "r": "p-CH3C6H4", "r_name": "p-tolyl", "rp": "Me", "nitrile": "acetonitrile", "water": 1, "time": 14.5, "yield": 62, "product": "3c", "ratio": "≥22:1"},
    {"entry": 4, "r": "p-CH3C6H4", "r_name": "p-tolyl", "rp": "Me", "nitrile": "acetonitrile", "water": 0, "time": 21, "yield": 45, "product": "3c", "ratio": "≥21:1"},
    {"entry": 5, "r": "o-CH3C6H4", "r_name": "o-tolyl", "rp": "Me", "nitrile": "acetonitrile", "water": 1, "time": 11.5, "yield": 60, "product": "3d", "ratio": "≥43:1"},
    {"entry": 6, "r": "p-BrC6H4", "r_name": "p-bromophenyl", "rp": "Me", "nitrile": "acetonitrile", "water": 1, "time": 12, "yield": 51, "product": "3e", "ratio": "≥65:1"},
    {"entry": 7, "r": "p-ClC6H4", "r_name": "p-chlorophenyl", "rp": "Me", "nitrile": "acetonitrile", "water": 1, "time": 10, "yield": 54, "product": "3f", "ratio": "≥26:1"},
    {"entry": 8, "r": "p-CH3OC6H4", "r_name": "p-methoxyphenyl", "rp": "Me", "nitrile": "acetonitrile", "water": 1, "time": 9.5, "yield": 51, "product": "3g", "ratio": "≥19:1"},
    {"entry": 9, "r": "p-CH3OC6H4", "r_name": "p-methoxyphenyl", "rp": "Me", "nitrile": "acetonitrile", "water": 0, "time": 11.5, "yield": 23, "product": "3g", "ratio": "≥30:1"},
]


def table2_record(row):
    ev = P2
    nitrile_smiles = "CC#N" if row["rp"] == "Me" else "CCCC#N"
    parts = [
        participant("t2_allene", "reactant", f"1 (R={row['r']})",
                    f"1,2-propadienyl {row['r_name']} selenide", ev),
        participant("t2_nitrile", "reactant", f"R'CN (R'={row['rp']})", row["nitrile"], ev,
                    nitrile_smiles),
        participant("t2_iodine", "reagent", "I2", "iodine", ev, "II",
                    [field("equivalents", {"number": 2, "unit": "equiv"}, ev)]),
        participant("t2_water", "reagent", "H2O", "water", ev, "O",
                    [field("equivalents", {"number": row["water"], "unit": "equiv"}, ev)]),
        participant("t2_n_hexane", "solvent", "n-hexane", "n-hexane", ev, "CCCCCC"),
        participant("t2_product", "product", f"Z-{row['product']}", None, ev),
    ]
    step = {
        "step_id": "reaction",
        "participant_ids": ["t2_allene", "t2_nitrile", "t2_iodine", "t2_water", "t2_n_hexane"],
        "conditions": [
            field("solvent", "R'CN/n-hexane (1:1)", ev),
            field("atmosphere", "N2", ev),
            field("temperature", {"number": 25, "unit": "°C"}, ev),
            field("time", {"number": row["time"], "unit": "h"}, ev),
        ],
    }
    outcomes = [
        field("yield_of_3", {"number": row["yield"], "unit": "%"}, ev, ["t2_product"]),
        field("Z_E_ratio_of_3", row["ratio"], ev, ["t2_product"]),
        field("Z_E_ratio_measurement_basis",
              "Determined by 300 MHz 1H NMR spectra of the crude product", ev,
              ["t2_product"]),
    ]
    return record(
        f"table2_entry_{row['entry']}", "substrate_scope_entry", ev, parts, [step], outcomes,
        [
            f"Table 2 entry {row['entry']}; R={row['r']}, R'={row['rp']}.",
            "The table explicitly reports that no water was added; this is not a missing value."
            if row["water"] == 0 else "Water was explicitly added at 1 equiv.",
        ],
        [
            COMMON_SI,
            "Yield measurement basis is not stated in Table 2.",
            "The allene and product are represented through a generic R/R' scheme; complete SMILES are not inferred from R-group substitution and remain missing.",
        ],
    )


def scheme2_records():
    ev = P2
    common_input = participant(
        "s2_3a", "reactant", "Z-3a", "N-(2-iodo-3-phenylseleno-2(Z)-propenyl)acetamide",
        ev, "CC(=O)NCC(I)=C[Se]c1ccccc1",
    )
    reduction = record(
        "scheme2_dibal_reduction", "reported_experiment", ev,
        [
            common_input,
            participant("s2_dibal", "reagent", "DIBAL", "diisobutylaluminium hydride", ev, None,
                        [field("equivalents", {"number": 5, "unit": "equiv"}, ev)]),
            participant("s2_toluene", "solvent", "toluene", "toluene", ev, "Cc1ccccc1"),
            participant("s2_8a", "product", "Z-8a",
                        "N-(3'-phenylseleno-2-iodo-(2E)-propenyl) N-ethyl amine", ev,
                        "CCNCC(I)=C[Se]c1ccccc1"),
        ],
        [{"step_id": "reduction", "participant_ids": ["s2_3a", "s2_dibal", "s2_toluene"],
          "conditions": [
              field("temperature", {"number": 90, "unit": "°C"}, ev),
              field("time", {"number": 12.5, "unit": "h"}, ev),
              field("atmosphere", "N2", ev),
          ]}],
        [field("yield", {"number": 79, "unit": "%"}, ev, ["s2_8a"])],
        ["Scheme 2 upper arrow: carbonyl reduction of Z-3a."],
        [COMMON_SI, "Yield measurement basis and workup/purification are not stated on the inspected page.",
         "Candidate alkene SMILES omits stereochemical encoding and remains structure-unverified."],
    )
    cyclization = record(
        "scheme2_nah_cyclization", "reported_experiment", ev,
        [
            participant("s2b_3a", "reactant", "Z-3a",
                        "N-(2-iodo-3-phenylseleno-2(Z)-propenyl)acetamide", ev,
                        "CC(=O)NCC(I)=C[Se]c1ccccc1"),
            participant("s2b_nah", "reagent", "NaH", "sodium hydride", ev, "[Na+].[H-]",
                        [field("equivalents", {"number": 1.2, "unit": "equiv"}, ev)]),
            participant("s2b_thf", "solvent", "THF", "tetrahydrofuran", ev, "C1CCOC1"),
            participant("s2b_9a", "product", "9a", "2-methyl-5-(phenylselenomethyl)oxazole", ev,
                        "Cc1ncc(C[Se]c2ccccc2)o1"),
        ],
        [{"step_id": "cyclization", "participant_ids": ["s2b_3a", "s2b_nah", "s2b_thf"],
          "conditions": [
              field("temperature", "rt", ev),
              field("time", {"number": 5, "unit": "h"}, ev),
          ]}],
        [field("yield", {"number": 96, "unit": "%"}, ev, ["s2b_9a"])],
        ["Scheme 2 lower arrow: NaH-promoted formation of oxazole 9a."],
        [COMMON_SI, "Yield measurement basis and workup/purification are not stated on the inspected page.",
         "Candidate structures remain source-unverified."],
    )
    return [reduction, cyclization]


records = [table1_record(row) for row in TABLE1]
records.append(typical_procedure())
records.extend(table2_record(row) for row in TABLE2)
records.extend(scheme2_records())

output = BASE / "extracted_records_pages_0001_0002.json"
output.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"output": str(output), "records": len(records)}, ensure_ascii=False))
