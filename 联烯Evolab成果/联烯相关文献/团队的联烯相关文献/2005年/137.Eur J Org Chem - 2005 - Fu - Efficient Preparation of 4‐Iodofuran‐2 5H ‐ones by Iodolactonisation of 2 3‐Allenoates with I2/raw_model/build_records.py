"""Build the page-1--4 source-derived machine records for session 137.

This is retained beside the raw JSON so the grouping and normalization inputs are
reproducible.  It does not review or certify any chemical structure.
"""
import json
from pathlib import Path


DOC = "doc_3a2d12dbc6253192"
BASE = Path(__file__).resolve().parent


def ev(page):
    return [f"{DOC}:page{page}:text", f"{DOC}:page{page}:image"]


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


def participant(entity_id, role, evidence, *, label=None, name=None, smiles=None, amounts=()):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence),
        "smiles": fact(smiles, evidence),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": list(amounts),
    }


def record(rid, source_id, kind, evidence, participants, steps, outcomes, notes, unresolved):
    return {
        "record_id": f"{DOC}:{rid}",
        "document_id": DOC,
        "source_reaction_id": source_id,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": list(dict.fromkeys(evidence)),
        "participants": participants,
        "steps": steps,
        "outcomes": outcomes,
        "notes": [fact(v, e) for v, e in notes],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved,
        },
    }


SUBSTRATE_SMILES = {
    "3a": "CCOC(=O)C=C=C(CCC)",
    "3b": "CCOC(=O)C=C=C(CCCC)",
    "3c": "CCOC(=O)C=C=C(CCCCCCC)",
    "3d": "CCOC(=O)C(Cc1ccccc1)=C=C(CCC)",
    "3e": "CCOC(=O)C(Cc1ccccc1)=C=C(CCCC)",
    "3f": "CCOC(=O)C(C)=C=C(CCC)",
    "3g": "CCOC(=O)C(C)=C=C(CCCC)",
    "3h": "CCOC(=O)C(C)=C=C(CCCCCCC)",
    "3i": "CCOC(=O)C(C)=C=C(C)(C)",
    "3j": "CCOC(=O)C(C)=C=C(c1ccccc1)",
    "3k": "CCOC(=O)C(CCC)=C=C(c1ccccc1)",
    "3l": "CCOC(=O)C(Cc1ccccc1)=C=C(c1ccccc1)",
    "3m": "CCOC(=O)C=C=C(C)(C)",
}

PRODUCTS = {
    "4a": ("4-Iodo-5-propylfuran-2(5H)-one", "O=C1OC(CCC)C(I)=C1"),
    "4b": ("5-Butyl-4-iodofuran-2(5H)-one", "O=C1OC(CCCC)C(I)=C1"),
    "4c": ("5-Heptyl-4-iodofuran-2(5H)-one", "O=C1OC(CCCCCCC)C(I)=C1"),
    "4d": ("3-Benzyl-4-iodo-5-propylfuran-2(5H)-one", "O=C1OC(CCC)C(I)=C1Cc2ccccc2"),
    "4e": ("3-Benzyl-5-butyl-4-iodofuran-2(5H)-one", "O=C1OC(CCCC)C(I)=C1Cc2ccccc2"),
    "4f": ("4-Iodo-3-methyl-5-propylfuran-2(5H)-one", "O=C1OC(CCC)C(I)=C1C"),
    "4g": ("5-Butyl-4-iodo-3-methylfuran-2(5H)-one", "O=C1OC(CCCC)C(I)=C1C"),
    "4h": ("5-Heptyl-4-iodo-3-methylfuran-2(5H)-one", "O=C1OC(CCCCCCC)C(I)=C1C"),
    "4i": ("4-Iodo-3,5,5-trimethylfuran-2(5H)-one", "O=C1OC(C)(C)C(I)=C1C"),
    "4j": ("4-Iodo-3-methyl-5-phenylfuran-2(5H)-one", "O=C1OC(c2ccccc2)C(I)=C1C"),
    "4k": ("4-Iodo-5-phenyl-3-propylfuran-2(5H)-one", "O=C1OC(c2ccccc2)C(I)=C1CCC"),
    "4l": ("3-Benzyl-4-iodo-5-phenylfuran-2(5H)-one", "O=C1OC(c2ccccc2)C(I)=C1Cc2ccccc2"),
    "4m": ("4-Iodo-5,5-dimethylfuran-2(5H)-one", "O=C1OC(C)(C)C(I)=C1"),
}


records = []


# Table 1: optimization rows. Entry 4 is represented by the merged 4a record below.
optimization = [
    (1, "CH3CN/H2O (4:1)", 2, 61, {"minimum": 16, "maximum": 20, "unit": "°C", "raw_text": "16–20 °C"}, 2.0),
    (2, "CH3CN/H2O (20:1)", 26, 67, {"minimum": 16, "maximum": 20, "unit": "°C", "raw_text": "16–20 °C"}, 2.0),
    (3, "CH3CN/H2O (12:1)", 10, 70, {"minimum": 16, "maximum": 20, "unit": "°C", "raw_text": "16–20 °C"}, 2.0),
    (5, "CH3CN/H2O (15:1)", 19, 63, {"number": 30, "unit": "°C"}, 2.0),
    (6, "CH3CN", 43, 46, {"minimum": 16, "maximum": 20, "unit": "°C", "raw_text": "16–20 °C"}, 2.0),
    (7, "CH3CN/EtOH (2:1)", 11.5, 48, {"minimum": 0, "maximum": 5, "unit": "°C", "raw_text": "0–5 °C"}, 2.0),
    (8, "acetone/H2O (15:1)", 18, 36, {"minimum": 16, "maximum": 20, "unit": "°C", "raw_text": "16–20 °C"}, 2.0),
    (9, "THF/H2O (15:1)", 19, 39, {"minimum": 16, "maximum": 20, "unit": "°C", "raw_text": "16–20 °C"}, 2.0),
    (10, "CH3CN/H2O (12:1)", 21, 48, {"minimum": 16, "maximum": 20, "unit": "°C", "raw_text": "16–20 °C"}, 1.2),
]
for entry, solvent, hours, yield_pct, temperature, iodine_equiv in optimization:
    evidence = ev(2)
    if entry == 1:
        evidence = ev(1) + evidence
    substrate = participant(
        "substrate_3a", "reactant", evidence, label="3a", name="ethyl 2,3-allenoate 3a",
        smiles=SUBSTRATE_SMILES["3a"], amounts=[field("reaction_scale", {"minimum": 0.2, "maximum": 0.4, "unit": "mmol", "raw_text": "0.2–0.4 mmol"}, ev(2))],
    )
    iodine = participant(
        "iodine", "reagent", ev(2), name="iodine", smiles="[I][I]",
        amounts=[field("equivalents", {"number": iodine_equiv, "unit": "equiv"}, ev(2))],
    )
    product_name, product_smiles = PRODUCTS["4a"]
    product = participant("product_4a", "product", evidence, label="4a", name=product_name, smiles=product_smiles)
    records.append(record(
        f"table1_entry_{entry}", f"Table 1 entry {entry}", "optimization_entry", evidence,
        [substrate, iodine, product],
        [{"step_id": "iodolactonisation", "participant_ids": ["substrate_3a", "iodine", "product_4a"], "conditions": [
            field("solvent", solvent, ev(2)),
            field("temperature", temperature, ev(2)),
            field("time", {"number": hours, "unit": "h"}, ev(2)),
        ]}],
        [field("isolated_yield", {"number": yield_pct, "unit": "%"}, ev(2), ["product_4a"]),
         field("yield_measurement_basis", "isolated yield", ev(2), ["product_4a"])],
        [],
        ["No atmosphere or detailed workup is reported for this optimization row.", "Candidate structures are machine-generated from the displayed scheme and remain unverified.", "No supporting information was explicitly provided or associated."],
    ))


# Table 2 and the experimental section describe the same labeled products.  They
# are merged per label/yield, while source discrepancies remain explicit.
scope = [
    ("3a", "4a", 20, 71, 3, 81.9, 0.53, 254.0, 1.00, 94.9),
    ("3b", "4b", 12, 65, 3, 84.6, 0.50, 256.7, 1.00, 86.4),
    ("3c", "4c", 14, 69, 3, 63.6, 0.30, 152.4, 0.60, 63.4),
    ("3d", "4d", 11, 78, 3, 76.1, 0.31, 156.0, 0.61, 82.4),
    ("3e", "4e", 14, 72, 3, 79.3, 0.307, 152.6, 0.60, 78.4),
    ("3f", "4f", 10, 88, 3, 83.5, 0.50, 254.9, 1.00, 116.2),
    ("3g", "4g", 16, 89, 3, 91.9, 0.50, 254.0, 1.00, 125.3),
    ("3h", "4h", 3, 91, 3, 88.2, 0.40, 203.0, 0.80, 115.6),
    ("3i", "4i", 3, 77, 3, 79.3, 0.51, 254.0, 1.00, 99.7),
    ("3j", "4j", 3, 83, 3, 82.5, 0.41, 202.0, 0.80, 102.1),
    ("3k", "4k", 0.7, 94, 3, 94.0, 0.40, 206.8, 0.80, 125.5),
    ("3l", "4l", 0.7, 81, 3, 84.2, 0.30, 153.9, 0.60, 91.9),
    ("3m", "4m", 12, 60, 3, 71.2, 0.50, 257.4, 1.02, 71.0),
]
for substrate_label, product_label, table_time, yield_pct, page, smass, smmol, imass, immol, pmass in scope:
    pages = [2, 3]
    if product_label == "4a":
        pages = [1, 2, 3]
    if product_label == "4m":
        pages = [2, 3, 4]
    evidence = sum((ev(p) for p in pages), [])
    product_name, product_smiles = PRODUCTS[product_label]
    participants = [
        participant(
            f"substrate_{substrate_label}", "reactant", evidence, label=substrate_label,
            name=f"2,3-allenoate {substrate_label}", smiles=SUBSTRATE_SMILES[substrate_label],
            amounts=[
                field("mass", {"number": smass, "unit": "mg"}, ev(page)),
                field("amount", {"number": smmol, "unit": "mmol"}, ev(page)),
                field("table_reaction_scale", {"minimum": 0.2, "maximum": 0.4, "unit": "mmol", "raw_text": "0.2–0.4 mmol"}, ev(2)),
            ],
        ),
        participant(
            "iodine", "reagent", evidence, name="iodine", smiles="[I][I]",
            amounts=[
                field("mass", {"number": imass, "unit": "mg"}, ev(page)),
                field("amount", {"number": immol, "unit": "mmol"}, ev(page)),
                field("table_equivalents", {"number": 2, "unit": "equiv"}, ev(2)),
            ],
        ),
        participant("acetonitrile", "solvent", ev(2) + ev(3), name="acetonitrile", smiles="CC#N"),
        participant("water", "solvent", ev(2) + ev(3), name="water", smiles="O"),
        participant(
            f"product_{product_label}", "product", evidence, label=product_label, name=product_name, smiles=product_smiles,
            amounts=[field("mass", {"number": pmass, "unit": "mg"}, ev(page))],
        ),
    ]
    conditions = [
        field("solvent", "MeCN/H2O (15:1)", ev(2)),
        field("table_temperature", {"minimum": 15, "maximum": 22, "unit": "°C", "raw_text": "15–22 °C"}, ev(2)),
        field("table_time", {"number": table_time, "unit": "h"}, ev(2)),
        field("operation", "prepared similarly to the typical procedure for 4a", ev(3)),
    ]
    unresolved = [
        "Candidate substrate and product structures are machine-generated from the displayed scheme/names and remain unverified.",
        "The paper gives no reaction atmosphere.",
        "No supporting information was explicitly provided or associated.",
    ]
    if product_label == "4a":
        conditions.extend([
            field("optimization_table_temperature", {"minimum": 16, "maximum": 20, "unit": "°C", "raw_text": "16–20 °C"}, ev(2)),
            field("procedure_solvent_volume", {"number": 4, "unit": "mL"}, ev(3)),
            field("procedure_temperature", {"number": 16, "unit": "°C"}, ev(3)),
            field("procedure_time", {"number": 12, "unit": "h"}, ev(3)),
            field("workup", "quenched with 6 mL water; saturated aqueous Na2S2O3; extracted with diethyl ether (3 × 25 mL); washed with NaCl; dried over anhydrous Na2SO4", ev(3)),
            field("purification", "silica-gel column chromatography, petroleum ether/ethyl acetate 20:1", ev(3)),
        ])
        unresolved.append("Reaction time conflicts within the source: Table 1 entry 4 and Table 2 entry 1 report 20 h, while the typical procedure reports 12 h; both are preserved.")
    if smmol < 0.2 or smmol > 0.4:
        unresolved.append(f"The Table 2 footnote states a 0.2–0.4 mmol substrate scale, while the experimental paragraph reports {smmol:g} mmol; both are preserved.")
    outcomes = [
        field("isolated_yield", {"number": yield_pct, "unit": "%"}, ev(2) + ev(page), [f"product_{product_label}"]),
        field("yield_measurement_basis", "isolated yield", ev(2), [f"product_{product_label}"]),
    ]
    records.append(record(
        f"scope_{product_label}", f"Table 2 / experimental {product_label}", "substrate_scope_entry", evidence,
        participants,
        [{"step_id": "iodolactonisation", "participant_ids": [f"substrate_{substrate_label}", "iodine", "acetonitrile", "water", f"product_{product_label}"], "conditions": conditions}],
        outcomes,
        [(f"The experimental paragraph reports {product_label} as a white solid.", ev(page))],
        unresolved,
    ))


# Explicit starting-material preparations on page 2.
starting = [
    ("3c", "Ethyl undeca-2,3-dienoate", "1a", 17.4, 50, 7.6, 55, "2c", 11.47, 65, "CCCCCCCCC(=O)Cl", 7.48, 71),
    ("3e", "Ethyl 2-benzylocta-2,3-dienoate", "1d", 17.5, 40, 6.1, 44, "2b", 8.0, 60, "CCCCCC(=O)Cl", 7.11, 77),
    ("3h", "Ethyl 2-methylundeca-2,3-dienoate", "1b", 21.7, 60, 9.2, 66, "2c", 15.9, 90, "CCCCCCCCC(=O)Cl", 13.19, 98),
    ("3k", "Ethyl 4-phenyl-2-propylbuta-2,3-dienoate", "1c", 28.2, 60, 18.4, 132, "2e", 13.9, 90, "O=C(Cl)Cc1ccccc1", 9.03, 65),
    ("3l", "Ethyl 2-benzyl-4-phenylbuta-2,3-dienoate", "1d", 10.38, 20, 6.1, 44, "2e", 3.40, 22, "O=C(Cl)Cc1ccccc1", 2.52, 45),
]
for product_label, product_name, ylide, ymass, ymmol, base_vol, base_mmol, acid, amass, ammol, acid_smiles, pmass, yield_pct in starting:
    evidence = ev(2)
    participants = [
        participant(f"ylide_{ylide}", "reactant", evidence, label=ylide, name=f"phosphorus ylide {ylide}", smiles=None,
                    amounts=[field("mass", {"number": ymass, "unit": "g"}, evidence), field("amount", {"number": ymmol, "unit": "mmol"}, evidence)]),
        participant("triethylamine", "reagent", evidence, name="triethylamine", smiles="CCN(CC)CC",
                    amounts=[field("volume", {"number": base_vol, "unit": "mL"}, evidence), field("amount", {"number": base_mmol, "unit": "mmol"}, evidence)]),
        participant(f"acid_chloride_{acid}", "reactant", evidence, label=acid, name=f"acyl chloride {acid}", smiles=acid_smiles,
                    amounts=[field("mass", {"number": amass, "unit": "g"}, evidence), field("amount", {"number": ammol, "unit": "mmol"}, evidence)]),
        participant("dichloromethane", "solvent", evidence, name="dichloromethane", smiles="ClCCl"),
        participant(f"product_{product_label}", "product", evidence, label=product_label, name=product_name, smiles=SUBSTRATE_SMILES[product_label],
                    amounts=[field("mass", {"number": pmass, "unit": "g"}, evidence)]),
    ]
    if product_label == "3c":
        conditions = [
            field("initial_temperature", {"number": 0, "unit": "°C"}, evidence),
            field("time_before_acyl_chloride_addition", {"number": 5, "unit": "min"}, evidence),
            field("ylide_solution_volume", {"number": 20, "unit": "mL"}, evidence),
            field("acyl_chloride_solution_volume", {"number": 15, "unit": "mL"}, evidence),
            field("operation", "acyl chloride solution added dropwise at 0 °C with stirring", evidence),
            field("reaction_temperature", "room temp.", evidence),
            field("reaction_time", "overnight", evidence),
            field("workup", "solvent evaporated; residue treated repeatedly with 80 mL diethyl ether and filtered until no further OPPh3 precipitated", evidence),
            field("purification", "flash chromatography on silica gel, petroleum ether/ethyl acetate 50:1", evidence),
        ]
        unresolved = [
            "The exact identity/SMILES of phosphorus ylide 1a is retained unresolved rather than inferred from the generic drawing.",
            "No atmosphere is reported.",
            "No supporting information was explicitly provided or associated.",
        ]
    else:
        conditions = [field("operation", "prepared similarly to the typical procedure for 3c", evidence)]
        unresolved = [
            f"The exact identity/SMILES of phosphorus ylide {ylide} is retained unresolved rather than inferred from the generic drawing.",
            "The compound-specific paragraph does not repeat solvent volumes, staged times, temperatures, workup, or purification; it only states that the typical procedure was followed similarly.",
            "No atmosphere is reported.",
            "No supporting information was explicitly provided or associated.",
        ]
    records.append(record(
        f"starting_material_{product_label}", f"Experimental preparation of {product_label}", "reported_experiment", evidence,
        participants,
        [{"step_id": "wittig_type_allene_synthesis", "participant_ids": [p["entity_id"] for p in participants], "conditions": conditions}],
        [field("isolated_yield", {"number": yield_pct, "unit": "%"}, evidence, [f"product_{product_label}"]),
         field("yield_measurement_basis", "isolated after chromatography", evidence, [f"product_{product_label}"])],
        [(f"Product {product_label} was reported as an oil.", evidence)],
        unresolved,
    ))


assert len(records) == 27
(BASE / "records_pages_0001_0004.json").write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"records": len(records), "path": str(BASE / "records_pages_0001_0004.json")}, ensure_ascii=False))
