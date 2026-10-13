#!/usr/bin/env python3
"""Build source-faithful machine records for DOI 10.1039/b912108k, PDF pages 1-3."""
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "runs/current/raw_model/records_pages_0001_0003.json"
COVERAGE = ROOT / "runs/current/coverage/pages_0001_0003.json"
TASKS = ROOT / "runs/current/tasks.json"
DOC = "doc_0a2adab5f5ab9136"


def ev(page: int):
    return [f"{DOC}:page{page}:image", f"{DOC}:page{page}:text"]


P1, P2, P3 = ev(1), ev(2), ev(3)


def fact(value, evidence=()):
    return {
        "value": value,
        "evidence_ids": list(evidence),
        "verification": "missing" if value is None else "unreviewed",
    }


def q(number, unit, **extra):
    return {"number": number, "unit": unit, **extra}


def qr(minimum, maximum, unit, raw_text):
    return {"minimum": minimum, "maximum": maximum, "unit": unit, "raw_text": raw_text}


def fld(name, value, evidence=(), targets=None):
    item = {"name": name, "fact": fact(value, evidence)}
    if targets:
        item["target_entity_ids"] = list(targets)
    return item


def participant(entity_id, role, label, name, smiles, evidence, amounts=()):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence),
        "smiles": fact(smiles, evidence) if smiles is not None else fact(None),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": list(amounts),
    }


def record(rid, kind, evidence, participants, conditions, outcomes, notes=(), unresolved=()):
    return {
        "record_id": f"{DOC}:{rid}",
        "document_id": DOC,
        "source_reaction_id": rid,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": list(dict.fromkeys(evidence)),
        "participants": participants,
        "steps": [{
            "step_id": "cyclization",
            "participant_ids": [p["entity_id"] for p in participants],
            "conditions": conditions,
        }],
        "outcomes": outcomes,
        "notes": [fact(x, evidence) for x in notes],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": list(unresolved),
        },
    }


def amount(name, value, evidence=P2):
    return fld(name, value, evidence)


SMILES = {
    "PhI": "Ic1ccccc1",
    "2b": "Cc1ccc(I)cc1",
    "2c": "Cc1cccc(I)c1",
    "2d": "Brc1ccc(I)cc1",
    "2e": "COc1ccc(I)cc1",
    "2f": "COC(=O)c1ccc(I)cc1",
    "2g": "N#Cc1ccc(I)cc1",
    "2h": "Ic1ccc(-c2ccccc2)cc1",
    "2i": "Brc1ccc(-c2ccc(I)cc2)cc1",
    "2j": "Ic1cc(C)c(C)cc1",
    "2k": "Ic1cc(C)cc(C)c1",
    "2l": "Ic1ccc2c(c1)OCO2",
    "2m": "Ic1ccsc1",
    "THF": "C1CCOC1",
    "DME": "COCCOC",
    "anisole": "COc1ccccc1",
    "Ag3PO4": "[Ag+].[Ag+].[Ag+].[O-]P(=O)([O-])[O-]",
    "mesitylene": "Cc1cc(C)cc(C)c1",
}


def substrate(label, r1, r2, evidence=P2):
    return participant(
        "substrate", "reactant", label,
        f"3,4-allenyl hydrazine {label} (R1={r1}, R2={r2})",
        None, evidence,
        [amount("amount", q(0.1, "mmol"), evidence)],
    )


def aryl(label, name, smiles, evidence=P2, table1=False):
    amounts = [amount("amount", q(0.12, "mmol"), evidence)] if table1 else [amount("equivalents", q(1.2, "equiv"), evidence)]
    return participant("aryl_iodide", "reactant", label, name, smiles, evidence, amounts)


def product(label, evidence=P2):
    return participant(
        "product", "product", label,
        f"optically active pyrazolidine {label}", None, evidence,
    )


def silver(evidence=P2, table1=False):
    values = [amount("amount", q(0.045, "mmol"), evidence)] if table1 else [amount("equivalents", q(0.45, "equiv"), evidence)]
    return participant("silver_phosphate", "reagent", "Ag3PO4", "silver phosphate", SMILES["Ag3PO4"], evidence, values)


def palladium(load, evidence=P2):
    return participant("palladium", "catalyst", "Pd(dba)2", "bis(dibenzylideneacetone)palladium(0)", None, evidence, [amount("catalyst_loading", q(load, "mol%"), evidence)])


def ligand(label, load, evidence=P2):
    return participant("ligand", "catalyst", label, f"spirobisoxazoline ligand {label}", None, evidence, [amount("ligand_loading", q(load, "mol%"), evidence)])


def solvent(name, evidence=P2):
    return participant("solvent", "solvent", name, name, SMILES.get(name), evidence, [amount("volume", q(2, "mL"), evidence)])


def missing_conditions():
    return [
        fld("atmosphere", None),
        fld("workup", None),
        fld("purification", None),
    ]


records = []
table1_ids = []

# Table 1 rows. Row 7 is identical to Table 2 row 1 and is built below as one cross-table record.
table1 = [
    (1, "(Ra,S,S)-L2", "THF", 70, 70, "isolated; calculated based on converted 1a", 91, 53, None),
    (2, "(Sa,S,S)-L2", "THF", 70, 47, "isolated; calculated based on converted 1a", 29, 46, "−29%"),
    (3, "(Ra,S,S)-L2", "THF", 100, 89, "isolated yield", 91, None, None),
    (4, "(Ra,S,S)-L3", "THF", 100, 69, "NMR yield using mesitylene as internal standard", 94, None, None),
    (5, "(Ra,S,S)-L3", "DME", 100, 36, "NMR yield using mesitylene as internal standard", None, None, None),
    (6, "(Ra,S,S)-L3", "anisole", 100, 48, "NMR yield using mesitylene as internal standard", None, None, None),
    (8, "(Ra,S,S)-L4", "THF", 100, "trace", "isolated yield unless otherwise stated", None, None, None),
    (9, "(Ra,S,S)-L5", "THF", 100, "trace", "isolated yield unless otherwise stated", None, None, None),
    (10, "(Ra,S,S)-L6", "THF", 100, 91, "isolated yield", 88, None, None),
]

for entry, lig, solv, temp, yld, basis, ee_value, recovery, signed in table1:
    rid = f"table1_entry{entry}"
    table1_ids.append(f"{DOC}:{rid}")
    parts = [
        substrate("1a", "Bn", "Bn"),
        aryl("2a", "iodobenzene", SMILES["PhI"], table1=True),
        product("(R)-3aa"), silver(table1=True), palladium(5), ligand(lig, 6), solvent(solv),
    ]
    if basis.startswith("NMR"):
        parts.append(participant("internal_standard", "unspecified_agent", "mesitylene", "mesitylene internal standard", SMILES["mesitylene"], P2))
    cond = [
        fld("temperature", q(temp, "°C"), P2),
        fld("time", None),
        fld("vessel", "Schlenk tube with a screw cap", P2),
    ] + missing_conditions()
    outcomes = [
        fld("product_yield", q(yld, "%") if isinstance(yld, (int, float)) else yld, P2, ["product"]),
        fld("yield_measurement_basis", basis, P2, ["product"]),
        fld("ee", q(ee_value, "%") if ee_value is not None else "not determined", P2, ["product"]),
        fld("ee_measurement_basis", "chiral HPLC analysis" if ee_value is not None else "not determined", P2, ["product"]),
    ]
    if recovery is not None:
        outcomes.append(fld("recovered_starting_material_yield", q(recovery, "%"), P2, ["substrate"]))
    if signed:
        outcomes.append(fld("signed_ee_source_notation", signed, P2, ["product"]))
    if entry in (8, 9):
        outcomes.append(fld("starting_material_conversion", "complete consumption", P2, ["substrate"]))
    narrative = []
    unresolved = ["Reaction time, atmosphere, workup, and purification are not reported in the supplied main text.", "Substrate and product structures require chemistry review; SMILES are not assigned."]
    if entry == 1:
        narrative.append("The paper describes the 70 °C reaction as very slow.")
    if entry in (4, 5, 6):
        narrative.append("The product was reported to remain contaminated with an inseparable impurity under this condition.")
    if entry == 2:
        unresolved.append("The source prints ee as −29%; the magnitude is retained separately and the negative sign is not converted into an inferred absolute configuration.")
    records.append(record(rid, "optimization_entry", P1 + P2, parts, cond, outcomes, narrative, unresolved))


scope_rows = [
    # entry, substrate, R1, R2, aryl label, aryl name, smiles key, product, yield, ee/minmax
    (1, "1a", "Bn", "Bn", "2a", "iodobenzene", "PhI", "(R)-3aa", 85, (93, 94)),
    (2, "1a", "Bn", "Bn", "2b", "1-iodo-4-methylbenzene", "2b", "(R)-3ab", 71, 93),
    (3, "1a", "Bn", "Bn", "2c", "1-iodo-3-methylbenzene", "2c", "(R)-3ac", 90, 92),
    (4, "1a", "Bn", "Bn", "2d", "1-bromo-4-iodobenzene", "2d", "(R)-3ad", 83, 93),
    (5, "1a", "Bn", "Bn", "2e", "1-iodo-4-methoxybenzene", "2e", "(R)-3ae", 75, 95),
    (6, "1a", "Bn", "Bn", "2f", "methyl 4-iodobenzoate", "2f", "(R)-3af", 76, 93),
    (7, "1a", "Bn", "Bn", "2g", "4-iodobenzonitrile", "2g", "(R)-3ag", 78, 94),
    (8, "1a", "Bn", "Bn", "2h", "4-iodobiphenyl", "2h", "(R)-3ah", 88, 92),
    (9, "1a", "Bn", "Bn", "2i", "4-bromo-4'-iodobiphenyl", "2i", "(R)-3ai", 71, 92),
    (10, "1a", "Bn", "Bn", "2j", "1-iodo-3,4-dimethylbenzene", "2j", "(R)-3aj", 76, 95),
    (11, "1a", "Bn", "Bn", "2k", "1-iodo-3,5-dimethylbenzene", "2k", "(R)-3ak", 83, 93),
    (12, "1a", "Bn", "Bn", "2l", "iodobenzodioxole isomer 2l", "2l", "(R)-3al", 74, 93),
    (13, "1b", "Et", "Et", "2e", "1-iodo-4-methoxybenzene", "2e", "(R)-3be", 83, 93),
    (14, "1c", "Bn", "Et", "2d", "1-bromo-4-iodobenzene", "2d", "(R)-3cd", 86, 95),
    (15, "1a", "Bn", "Bn", "2m", "3-iodothiophene", "2m", "(R)-3am", 85, 92),
]

scope_ids = []
for entry, sub, r1, r2, aryl_label, aryl_name, smi_key, prod, yld, ee_value in scope_rows:
    if entry == 1:
        rid = "table1_entry7_table2_entry1_3aa"
        table1_ids.append(f"{DOC}:{rid}")
        evidence = P1 + P2
        aryl_part = aryl(aryl_label, aryl_name, SMILES[smi_key], P2, table1=False)
        aryl_part["amounts"].append(amount("amount", q(0.12, "mmol"), P2))
        ag = silver(P2, table1=False)
        ag["amounts"].append(amount("amount", q(0.045, "mmol"), P2))
    else:
        rid = f"table2_entry{entry}_{prod.replace('(R)-', '').lower()}"
        evidence = P2
        aryl_part = aryl(aryl_label, aryl_name, SMILES[smi_key])
        ag = silver()
    scope_ids.append(f"{DOC}:{rid}")
    pd_load, lig_load = (10, 12) if entry in (4, 14) else (5, 6)
    parts = [
        substrate(sub, r1, r2), aryl_part, product(prod), ag,
        palladium(pd_load), ligand("(Ra,S,S)-L3", lig_load), solvent("THF"),
    ]
    cond = [
        fld("temperature", q(80, "°C"), P2),
        fld("time", qr(44, 66, "h", "44–66 h"), P2),
        fld("vessel", "Schlenk tube with a screw cap", P2),
    ] + missing_conditions()
    ee_struct = qr(ee_value[0], ee_value[1], "%", "93–94%") if isinstance(ee_value, tuple) else q(ee_value, "%")
    outcomes = [
        fld("isolated_yield", q(yld, "%"), P2, ["product"]),
        fld("yield_measurement_basis", "isolated yield", P2, ["product"]),
        fld("ee", ee_struct, P2, ["product"]),
        fld("ee_measurement_basis", "chiral HPLC analysis", P2, ["product"]),
        fld("absolute_configuration", "R", P2, ["product"]),
    ]
    notes = []
    unresolved = [
        "The shared 44–66 h range is reported for the scope; the exact row-specific duration is not stated.",
        "Atmosphere, workup, and purification are not reported in the supplied main text.",
        "Complex substrate/product connectivity and stereochemistry require chemistry review; their SMILES are not assigned.",
    ]
    if entry in (4, 9, 14):
        outcomes.append(fld("chemoselectivity", "C–I bond reacted preferentially over C–Br; the aryl bromide was retained", P2, ["product"]))
    if entry == 14:
        notes.append("The R assignment for 3cd was supported by comparison of chiral HPLC and specific rotation with known (S)-3cd.")
    if entry == 1:
        notes.append("Table 1 entry 7 and Table 2 entry 1 report the same substrates, loadings, THF volume, 80 °C condition, 85% yield, and 93–94% ee; they are one cross-table experiment record.")
    records.append(record(rid, "optimization_entry" if entry == 1 else "substrate_scope_entry", evidence, parts, cond, outcomes, notes, unresolved))


# Restore source order: Table 1 rows 1-6, merged row 7, rows 8-10, then remaining Table 2 rows.
order = {f"{DOC}:table1_entry{i}": i for i in (1, 2, 3, 4, 5, 6, 8, 9, 10)}
order[f"{DOC}:table1_entry7_table2_entry1_3aa"] = 7
for i, rid in enumerate(scope_ids[1:], start=11):
    order[rid] = i
records.sort(key=lambda r: order[r["record_id"]])

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")

coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1,
            "state": "attempted",
            "regions": [
                {
                    "region": "title, abstract, introduction, and right-column optimization narrative",
                    "finding": "Present-paper narrative discusses Table 1 entries 1–10 and the optimized cyclization; those facts are linked to the corresponding table records rather than duplicated. Citation-only prior-work summaries are classified as background and not expanded into unsupported primary-paper experiments.",
                    "evidence_ids": P1,
                },
                {
                    "region": "Figure 1, upper-right ligand evolution graphic",
                    "finding": "Design evolution from L1 to spiro-BOX ligands L2–L6; arrows are conceptual ligand evolution, not source-supported synthesis arrows. L3 is only said to have been prepared by a known procedure, with no precursor, conditions, or yield supplied.",
                    "evidence_ids": P1,
                },
            ],
            "record_ids": sorted(table1_ids),
            "unresolved": [
                "The supplied main text does not provide an experimental preparation for ligand L3; no SI was supplied or associated.",
                "Citation-only prior-work statements lack sufficient reaction-level detail for faithful reconstruction.",
            ],
        },
        {
            "page": 2,
            "state": "attempted",
            "regions": [
                {
                    "region": "upper-left Table 1 reaction drawing, entries 1–10, and footnotes",
                    "finding": "Ten optimization rows were extracted. Table 1 entry 7 was merged with identical Table 2 entry 1; recovery, converted-substrate yield basis, NMR-yield basis, trace outcomes, complete consumption, and not-determined ee values were preserved row-wise.",
                    "evidence_ids": P2,
                },
                {
                    "region": "lower half Table 2 reaction drawing, entries 1–15, and footnotes",
                    "finding": "Fifteen substrate-scope rows were extracted, with row-specific substrates, isolated yields, ee values, shared 44–66 h range, and the 10/12 mol% catalyst/ligand overrides for entries 4 and 14. Entry 1 is the cross-table record shared with Table 1 entry 7.",
                    "evidence_ids": P2,
                },
                {
                    "region": "upper-right scope discussion and conclusion",
                    "finding": "C–I/C–Br chemoselectivity for entries 4, 9, and 14 and the R assignment discussion for 3cd were linked to their scope records; summary claims were not duplicated as experiments.",
                    "evidence_ids": P2,
                },
            ],
            "record_ids": sorted(set(table1_ids + scope_ids)),
            "unresolved": [
                "Table 1 omits reaction time; Table 2 gives only a shared 44–66 h range rather than row-specific times.",
                "Atmosphere, workup, and purification are absent from the supplied main text.",
                "Complex substrate/product structures and stereochemical encodings remain unverified.",
            ],
        },
        {
            "page": 3,
            "state": "attempted",
            "regions": [
                {
                    "region": "two-column Notes and references, references 1–12",
                    "finding": "Bibliography only; no reaction arrow, table, present-paper procedure, condition, yield, selectivity, or experimental footnote appears on this page. Citations were not expanded into inferred experiments.",
                    "evidence_ids": P3,
                }
            ],
            "record_ids": [],
            "unresolved": ["The cited primary papers were not supplied and were not used to infer reaction records."],
        },
    ],
}
COVERAGE.parent.mkdir(parents=True, exist_ok=True)
COVERAGE.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

tasks = json.loads(TASKS.read_text())
for task in tasks:
    if task.get("document_id") == DOC and task.get("evidence_id") in {f"{DOC}:page{i}:text" for i in range(1, 4)}:
        task["state"] = "attempted"
TASKS.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"records": len(records), "coverage_pages": [p["page"] for p in coverage["pages"]]}, ensure_ascii=False))
