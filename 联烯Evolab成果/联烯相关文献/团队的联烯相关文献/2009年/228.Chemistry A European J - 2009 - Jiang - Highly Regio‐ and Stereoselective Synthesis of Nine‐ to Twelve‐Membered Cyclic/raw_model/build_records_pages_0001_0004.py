#!/usr/bin/env python3
"""Build source-derived machine records for doc_bda162199698e71c, PDF pages 1-4."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOC = "doc_bda162199698e71c"


def ev(page: int) -> list[str]:
    return [f"{DOC}:page{page}:image", f"{DOC}:page{page}:text"]


def fact(value, evidence):
    return {
        "value": value,
        "evidence_ids": list(dict.fromkeys(evidence)) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def fld(name, value, evidence, targets=None):
    out = {"name": name, "fact": fact(value, evidence)}
    if targets:
        out["target_entity_ids"] = targets
    return out


def part(entity_id, role, label, evidence, *, name=None, smiles=None, amounts=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence) if name else fact(None, []),
        "smiles": fact(smiles, evidence) if smiles else fact(None, []),
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
        "evidence_ids": list(dict.fromkeys(evidence)),
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


SMILES = {
    "1a": "COC(=O)C(Cc1ccccc1CC(C(=O)OC)(C(=O)OC)CC=C=C)C(=O)OC",
    "PhI": "Ic1ccccc1",
    "Pd(PPh3)4": "[Pd](P(c1ccccc1)(c1ccccc1)c1ccccc1)(P(c1ccccc1)(c1ccccc1)c1ccccc1)(P(c1ccccc1)(c1ccccc1)c1ccccc1)P(c1ccccc1)(c1ccccc1)c1ccccc1",
    "K2CO3": "[K+].[K+].[O-]C([O-])=O",
    "Na2CO3": "[Na+].[Na+].[O-]C([O-])=O",
    "Cs2CO3": "[Cs+].[Cs+].[O-]C([O-])=O",
    "KOAc": "CC(=O)[O-].[K+]",
    "KHCO3": "O=C([O-])O.[K+]",
    "THF": "C1CCOC1",
    "DMSO": "CS(C)=O",
    "DMF": "CN(C)C=O",
    "DMA": "CC(=O)N(C)C",
    "p-MeOOCC6H4I": "COC(=O)c1ccc(I)cc1",
    "p-MeCOC6H4I": "CC(=O)c1ccc(I)cc1",
    "p-MeC6H4I": "Cc1ccc(I)cc1",
    "p-ClC6H4I": "Clc1ccc(I)cc1",
    "4-pyridinyl iodide": "Ic1ccncc1",
    "(E)-1-iodohex-1-ene": "CCCCC=CI",
    "(E)-styryl iodide": "IC=Cc1ccccc1",
}


records = []

# Scheme 1 is a generic conceptual map, not a batch experiment.
e1 = ev(1)
generic_parts = [
    part("scheme1_allene", "reactant", "allene bearing a tethered NuH group", e1),
    part("scheme1_rpdx", "reagent", "RPdX", e1),
    part("scheme1_a", "product", "generic cyclic product A (route a)", e1),
    part("scheme1_b", "product", "generic cyclic alkene B (route b)", e1),
]
records.append(record(
    "scheme1_generic_routes", "general_scheme", e1, generic_parts,
    [{"step_id": "scheme1", "participant_ids": [p["entity_id"] for p in generic_parts],
      "conditions": [fld("operation", "carbopalladation followed by base-enabled intramolecular nucleophilic trapping", e1)]}],
    [],
    ["Scheme 1 contrasts generic route a and route b and is not an individual experimental batch."],
    ["R, X, Nu, tether length, catalyst ligands, time, temperature, scale, and yields are unspecified."],
))


def shared_table1_participants(evidence, base_label, solvent_label, *, detailed=False):
    p = [
        part("substrate_1a", "reactant", "1a", evidence,
             name="methyl 3-{2-[2,2-bis(methoxycarbonyl)hexa-4,5-dienyl]phenyl}-2-(methoxycarbonyl)propionate",
             smiles=SMILES["1a"],
             amounts=[fld("concentration", {"number": 0.07, "unit": "M"}, ev(2))]),
        part("iodobenzene", "reactant", "PhI", evidence, name="iodobenzene", smiles=SMILES["PhI"],
             amounts=[fld("equivalents", {"number": 2, "unit": "equiv"}, ev(2))]),
        part("pdpph3_4", "catalyst", "[Pd(PPh3)4]", evidence, name="tetrakis(triphenylphosphine)palladium(0)",
             smiles=SMILES["Pd(PPh3)4"], amounts=[fld("catalyst_loading", {"number": 5, "unit": "mol%"}, ev(2))]),
        part("base", "reagent", base_label, evidence, smiles=SMILES.get(base_label),
             amounts=[fld("equivalents", {"number": 4, "unit": "equiv"}, ev(2))]),
        part("solvent", "solvent", solvent_label, evidence, smiles=SMILES.get(solvent_label)),
        part("product_2a", "product", "(E)-2a (ten-membered cycloalkene)", evidence),
        part("possible_product_3a", "product", "3a (eight-membered regioisomer)", evidence),
    ]
    if detailed:
        by_id = {x["entity_id"]: x for x in p}
        by_id["substrate_1a"]["amounts"] += [
            fld("mass", {"number": 41.8, "unit": "mg"}, ev(3)),
            fld("amount", {"number": 0.1, "unit": "mmol"}, ev(3)),
        ]
        by_id["iodobenzene"]["amounts"] += [
            fld("mass", {"number": 40.9, "unit": "mg"}, ev(3)),
            fld("amount", {"number": 0.2, "unit": "mmol"}, ev(3)),
        ]
        by_id["pdpph3_4"]["amounts"] += [
            fld("mass", {"number": 5.7, "unit": "mg"}, ev(3)),
            fld("amount", {"number": 0.005, "unit": "mmol"}, ev(3)),
        ]
        by_id["base"]["amounts"] += [
            fld("mass", {"number": 55.6, "unit": "mg"}, ev(3)),
            fld("amount", {"number": 0.4, "unit": "mmol"}, ev(3)),
        ]
        by_id["solvent"]["amounts"] += [fld("volume", {"number": 1.5, "unit": "mL"}, ev(3))]
    return p


table1 = [
    (1, "K2CO3", "THF", 72, 0, None, 84),
    (2, "K2CO3", "DMSO", 14.5, 76, None, None),
    (3, "K2CO3", "DMF", 11, 69, None, None),
    (4, "K2CO3", "DMA", 11, 93, 91, None),
    (5, "Na2CO3", "DMA", 24, 36, None, 43),
    (6, "Cs2CO3", "DMA", 11, 58, None, None),
    (7, "KOAc", "DMA", 24, 0, None, None),
    (8, "KHCO3", "DMA", 24, 43, None, None),
]

for entry, base, solvent, hours, nmr_yield, isolated_yield, recovery in table1:
    detailed = entry == 4
    evidence = ev(2) + (ev(3) if detailed else []) + (ev(1) if entry == 1 else [])
    rid = "table1_entry4_table2_entry1_2a" if entry == 4 else f"table1_entry{entry}"
    participants = shared_table1_participants(evidence, base, solvent, detailed=detailed)
    conds = [
        fld("temperature", {"number": 80, "unit": "°C"}, ev(2)),
        fld("time", {"number": hours, "unit": "h"}, ev(2)),
        fld("atmosphere", "nitrogen", ev(2)),
    ]
    if detailed:
        conds += [
            fld("operation", "reagents and DMA added sequentially to a Schlenk tube containing K2CO3", ev(3)),
            fld("operation", "cooled in a dry-ice/acetone bath and back-filled with nitrogen three times", ev(3)),
            fld("operation", "stirred until TLC completion; TLC eluent petroleum ether/ethyl acetate 5:1", ev(3)),
            fld("workup", "quenched with H2O (10 mL), extracted with diethyl ether (3 x 30 mL), washed with water and brine, dried over anhydrous Na2SO4, filtered, and evaporated", ev(3)),
            fld("purification", "silica-gel chromatography; petroleum ether/ethyl acetate/dichloromethane 5:1:1", ev(3)),
        ]
    else:
        conds += [fld("workup", None, []), fld("purification", None, [])]
    outcomes = [
        fld("product_2a_NMR_yield", {"number": nmr_yield, "unit": "%"}, ev(2), ["product_2a"]),
        fld("yield_measurement_basis", "1H NMR (300 MHz) with CH2Br2 as internal standard", ev(2), ["product_2a"]),
    ]
    if isolated_yield is not None:
        outcomes += [
            fld("product_2a_isolated_yield", {"number": isolated_yield, "unit": "%"}, ev(2) + ev(3), ["product_2a"]),
            fld("product_2a_mass", {"number": 44.9, "unit": "mg"}, ev(3), ["product_2a"]),
            fld("product_2a_physical_form", "white solid", ev(3), ["product_2a"]),
            fld("product_2a_alkene_geometry", "E", ev(2), ["product_2a"]),
            fld("product_3a_formation", "not observed", ev(2), ["possible_product_3a"]),
        ]
    elif entry == 1:
        outcomes += [fld("expected_products_2a_or_3a", "not afforded", ev(1) + ev(2), ["product_2a", "possible_product_3a"])]
    else:
        outcomes += [fld("product_3a_formation", "not observed in the regioselectivity study", ev(2), ["possible_product_3a"])]
    if recovery is not None:
        outcomes.append(fld("recovered_starting_material_yield", {"number": recovery, "unit": "%"}, ev(2), ["substrate_1a"]))
    unresolved = ["Product 2a/3a connectivity and E assignment remain unverified machine interpretations."]
    if not detailed:
        unresolved.append("Reaction scale, solvent volume, workup, and purification are not stated for this table row.")
    records.append(record(rid, "optimization_entry", evidence, participants,
                          [{"step_id": "cyclization", "participant_ids": [p["entity_id"] for p in participants], "conditions": conds}],
                          outcomes, [f"Table 1 entry {entry}."], unresolved))


table2 = [
    (2, "p-MeOOCC6H4", "p-MeOOCC6H4I", "2b", 11.5, 84),
    (3, "p-MeCOC6H4", "p-MeCOC6H4I", "2c", 14, 89),
    (4, "p-MeC6H4", "p-MeC6H4I", "2d", 12, 90),
    (5, "p-ClC6H4", "p-ClC6H4I", "2e", 17, 85),
    (6, "4-pyridinyl", "4-pyridinyl iodide", "2f", 14, 84),
    (7, "(E)-1-hexenyl", "(E)-1-iodohex-1-ene", "2g", 72, 60),
    (8, "(E)-styryl", "(E)-styryl iodide", "2h", 72, 62),
]

for entry, r_group, halide, product, hours, yield_value in table2:
    evidence = ev(2)
    halide_equiv = 3 if entry in (7, 8) else 2
    participants = [
        part("substrate_1a", "reactant", "1a", evidence,
             name="methyl 3-{2-[2,2-bis(methoxycarbonyl)hexa-4,5-dienyl]phenyl}-2-(methoxycarbonyl)propionate",
             smiles=SMILES["1a"], amounts=[fld("concentration", {"number": 0.07, "unit": "M"}, evidence)]),
        part("organic_iodide", "reactant", halide, evidence, smiles=SMILES.get(halide),
             amounts=[fld("equivalents", {"number": halide_equiv, "unit": "equiv"}, evidence)]),
        part("pdpph3_4", "catalyst", "[Pd(PPh3)4]", evidence, smiles=SMILES["Pd(PPh3)4"],
             amounts=[fld("catalyst_loading", {"number": 5, "unit": "mol%"}, evidence)]),
        part("k2co3", "reagent", "K2CO3", evidence, smiles=SMILES["K2CO3"],
             amounts=[fld("equivalents", {"number": 4, "unit": "equiv"}, evidence)]),
        part("dma", "solvent", "DMA", evidence, smiles=SMILES["DMA"]),
        part(f"product_{product}", "product", f"(E)-{product}, R={r_group} (ten-membered ring)", evidence),
    ]
    conditions = [
        fld("temperature", {"number": 80, "unit": "°C"}, evidence),
        fld("time", {"number": hours, "unit": "h"}, evidence),
        fld("atmosphere", "nitrogen", evidence),
        fld("workup", None, []),
        fld("purification", None, []),
    ]
    outcomes = [
        fld(f"product_{product}_isolated_yield", {"number": yield_value, "unit": "%"}, evidence, [f"product_{product}"]),
        fld("yield_measurement_basis", "isolated yield", evidence, [f"product_{product}"]),
        fld("product_alkene_geometry", "E", evidence, [f"product_{product}"]),
    ]
    records.append(record(
        f"table2_entry{entry}_{product}", "substrate_scope_entry", evidence, participants,
        [{"step_id": "coupling_cyclization", "participant_ids": [p["entity_id"] for p in participants], "conditions": conditions}],
        outcomes, [f"Table 2 entry {entry}; the organic iodide installs R={r_group}."],
        ["Complex product connectivity and E geometry are not independently verified.",
         "Scale, solvent volume, workup, and purification are not stated for this row."],
    ))


table3 = [
    (1, "4a", "5a", 9, 11.5, 70, "PhI", "CO2Me"),
    (2, "4b", "5b", 10, 16.7, 89, "PhI", "CO2Me"),
    (3, "4c", "5c", 10, 8, 82, "4-chlorophenyl iodide", "CO2Me"),
    (4, "4d", "5d", 11, 11, 73, "PhI", "CO2Me"),
    (5, "4e", "5e", 12, 13, 73, "PhI", "CO2Me"),
    (6, "4f", "5f", 10, 16, 83, "PhI", "CO2Et"),
]

for entry, substrate, product, ring_size, hours, yield_value, aryl_iodide, ester in table3:
    evidence = ev(3) + (ev(4) if entry in (3, 6) else [])
    halide_smiles = SMILES["p-ClC6H4I"] if entry == 3 else SMILES["PhI"]
    participants = [
        part("substrate", "reactant", f"{substrate} (E={ester})", evidence,
             amounts=[fld("concentration", {"number": 0.07, "unit": "M"}, ev(3))]),
        part("aryl_iodide", "reactant", aryl_iodide, evidence, smiles=halide_smiles,
             amounts=[fld("equivalents", {"number": 2, "unit": "equiv"}, ev(3))]),
        part("pdpph3_4", "catalyst", "[Pd(PPh3)4]", evidence, smiles=SMILES["Pd(PPh3)4"],
             amounts=[fld("catalyst_loading", {"number": 5, "unit": "mol%"}, ev(3))]),
        part("k2co3", "reagent", "K2CO3", evidence, smiles=SMILES["K2CO3"],
             amounts=[fld("equivalents", {"number": 4, "unit": "equiv"}, ev(3))]),
        part("dma", "solvent", "DMA", evidence, smiles=SMILES["DMA"]),
        part("product", "product", f"{product} ({ring_size}-membered cyclic product)", evidence),
    ]
    conditions = [
        fld("temperature", {"number": 80, "unit": "°C"}, ev(3)),
        fld("time", {"number": hours, "unit": "h"}, ev(3)),
        fld("atmosphere", None, []),
        fld("workup", None, []),
        fld("purification", None, []),
    ]
    outcomes = [
        fld(f"product_{product}_isolated_yield", {"number": yield_value, "unit": "%"}, ev(3), ["product"]),
        fld("yield_measurement_basis", "isolated yield", ev(3), ["product"]),
        fld("product_ring_size", f"{ring_size}-membered ring", ev(3), ["product"]),
    ]
    notes = [f"Table 3 entry {entry}; E denotes {ester}."]
    if entry == 3:
        notes.append("The source states that 5c was established by X-ray diffraction; CCDC 721795 is listed on page 4.")
    if entry == 6:
        notes.append("The source states that 5f structure and C=C configuration were established by X-ray diffraction; CCDC 702170 is listed on page 4.")
    records.append(record(
        f"table3_entry{entry}_{product}", "substrate_scope_entry", evidence, participants,
        [{"step_id": "coupling_cyclization", "participant_ids": [p["entity_id"] for p in participants], "conditions": conditions}],
        outcomes, notes,
        ["Substrate and product connectivity/stereochemistry were read from the drawing but are not encoded as verified SMILES.",
         "Scale, atmosphere, solvent volume, workup, and purification are not stated for this row."],
    ))


# Scheme 2 is explicitly explanatory/proposed and not an isolated experiment.
e23 = ev(2) + ev(3)
mech_parts = [
    part("aryl_palladium", "reagent", "RPdI", e23),
    part("functionalized_allene", "reactant", "allene bearing tethered NuH/Nu−", e23),
    part("anti_pi_allyl_intermediate", "unspecified_agent", "anti pi-allyl palladium intermediate", e23),
    part("cyclic_product", "product", "medium-ring cyclic alkene", e23),
]
records.append(record(
    "scheme2_proposed_mechanism", "mechanism", e23, mech_parts,
    [
        {"step_id": "anti_intermediate_formation", "participant_ids": ["aryl_palladium", "functionalized_allene", "anti_pi_allyl_intermediate"],
         "conditions": [fld("operation", "carbopalladation gives the anti intermediate to reduce steric repulsion", e23)]},
        {"step_id": "intramolecular_attack", "participant_ids": ["anti_pi_allyl_intermediate", "cyclic_product"],
         "conditions": [fld("operation", "nucleophilic attack at the less substituted terminal affords the cyclic product", e23)]},
    ],
    [], ["Scheme 2 is the authors' stereochemical/regiochemical explanation, not a reported isolated batch."],
    ["Generic R/Nu/tether identities, elementary-step kinetics, and organopalladium structures are not experimentally resolved here."],
))


assert len(records) == 23

raw_path = ROOT / "raw_model" / "records_pages_0001_0004.json"
raw_path.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")

ids = {r["source_reaction_id"]: r["record_id"] for r in records}
table1_ids = [ids[f"table1_entry{i}"] if i != 4 else ids["table1_entry4_table2_entry1_2a"] for i in range(1, 9)]
table2_ids = [ids["table1_entry4_table2_entry1_2a"]] + [ids[f"table2_entry{i}_2{chr(96+i)}"] for i in range(2, 9)]
table3_ids = [ids[f"table3_entry{i}_5{chr(96+i)}"] for i in range(1, 7)]

coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1,
            "state": "attempted",
            "regions": [
                {"region": "title, introduction, and lower-right Scheme 1/opening experiment prose",
                 "finding": "Scheme 1 is a generic route map; cited prior syntheses were not reconstructed. The opening sentence identifies the 1a/PhI experiment continued on page 2.",
                 "evidence_ids": ev(1)},
            ],
            "record_ids": [ids["scheme1_generic_routes"], ids["table1_entry1"]],
            "unresolved": ["Scheme 1 uses generic R, X, Nu, and tether variables and supplies no batch-specific yield."],
        },
        {
            "page": 2,
            "state": "attempted",
            "regions": [
                {"region": "upper-left Table 1 and adjacent optimization discussion",
                 "finding": "Eight independent solvent/base rows extracted, including two zero yields, two starting-material recoveries, NMR basis, and the parenthesized isolated yield.",
                 "evidence_ids": ev(2)},
                {"region": "upper-right Table 2 and footnotes",
                 "finding": "Eight organic-iodide scope rows represented; Table 2 entry 1 is merged with Table 1 entry 4 because both are the same optimized 1a/PhI/2a experiment.",
                 "evidence_ids": ev(2)},
                {"region": "middle-to-lower Results and Discussion",
                 "finding": "Narrative scope, Table 3 X-ray statements, and the proposed anti-intermediate explanation were linked without duplicating experiments.",
                 "evidence_ids": ev(2)},
            ],
            "record_ids": sorted(set(table1_ids + table2_ids + [ids["scheme2_proposed_mechanism"], table3_ids[2], table3_ids[5]])),
            "unresolved": ["Most table rows omit scale, solvent volume, workup, and purification; complex product structures remain unverified."],
        },
        {
            "page": 3,
            "state": "attempted",
            "regions": [
                {"region": "upper-left Table 3 and footnotes",
                 "finding": "Six independent nine- to twelve-membered ring scope rows extracted with row-specific substrate/product drawings, times, isolated yields, the 4-chlorophenyl-iodide override, and the CO2Et footnote.",
                 "evidence_ids": ev(3)},
                {"region": "lower-left Experimental Section",
                 "finding": "The complete 1a/PhI preparation was merged with the shared Table 1 entry 4/Table 2 entry 1 record, adding exact quantities, nitrogen handling, workup, purification, product mass, and isolated yield.",
                 "evidence_ids": ev(3)},
                {"region": "upper-right Figure 2 and lower-right Scheme 2",
                 "finding": "ORTEP drawings support 5c/5f assignments; Scheme 2 was classified as a proposed mechanism rather than an experiment.",
                 "evidence_ids": ev(3)},
            ],
            "record_ids": table3_ids + [ids["table1_entry4_table2_entry1_2a"], ids["scheme2_proposed_mechanism"]],
            "unresolved": ["Table 3 omits scale, atmosphere, solvent volume, workup, and purification; exact complex connectivity and stereochemistry remain unverified."],
        },
        {
            "page": 4,
            "state": "attempted",
            "regions": [
                {"region": "acknowledgements, keywords, references, and crystal-data notes",
                 "finding": "No independent reaction appears. Crystal data/CCDC identifiers support compounds 5c and 5f; bibliography entries were not expanded into reaction records.",
                 "evidence_ids": ev(4)},
            ],
            "record_ids": [table3_ids[2], table3_ids[5]],
            "unresolved": ["Crystallographic metadata support identity but do not supply additional experimental reaction conditions."],
        },
    ],
}

coverage_path = ROOT / "coverage" / "pages_0001_0004.json"
coverage_path.parent.mkdir(parents=True, exist_ok=True)
coverage_path.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

tasks_path = ROOT / "tasks.json"
tasks = json.loads(tasks_path.read_text())
for task in tasks:
    if task.get("document_id") == DOC and task.get("evidence_id") in {f"{DOC}:page{i}:text" for i in range(1, 5)}:
        task["state"] = "attempted"
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"records": len(records), "raw": str(raw_path), "coverage": str(coverage_path)}, ensure_ascii=False))
