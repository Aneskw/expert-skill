#!/usr/bin/env python3
"""Build evidence-linked machine records for jo034511q PDF pages 1-4."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "runs/current/raw_model/extracted_records_pages_0001_0004.json"
COVERAGE = ROOT / "runs/current/coverage/pages_0001_0004.json"
TASKS = ROOT / "runs/current/tasks.json"
DOC = "doc_bd82d052f651be5e"
P1T, P1I = f"{DOC}:page1:text", f"{DOC}:page1:image"
P2T, P2I = f"{DOC}:page2:text", f"{DOC}:page2:image"
P3T, P3I = f"{DOC}:page3:text", f"{DOC}:page3:image"
P4T, P4I = f"{DOC}:page4:text", f"{DOC}:page4:image"


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


def participant(entity_id, role, label, evidence, name=None, smiles=None, amounts=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence) if name else fact(None, ()),
        "smiles": fact(smiles, evidence) if smiles else fact(None, ()),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": amounts or [],
    }


def record(source_id, kind, evidence, participants, steps, outcomes=None, notes=None,
           unresolved=None):
    return {
        "record_id": f"{DOC}:{source_id}",
        "document_id": DOC,
        "source_reaction_id": source_id,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": list(dict.fromkeys(evidence)),
        "participants": participants,
        "steps": steps,
        "outcomes": outcomes or [],
        "notes": [fact(v, ev) for v, ev in (notes or [])],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved or [],
        },
    }


SMILES = {
    "1a": "O=C(O)C(CCC)=C=C(c1ccccc1)",
    "1b": "O=C(O)C(C)=C=C(c1ccccc1)",
    "1c": "O=C(O)C(CCC)=C=C(c1cccc2ccccc12)",
    "1d": "O=C(O)C(C)=C=C(c1cccc2ccccc12)",
    "1e": "O=C(O)C(Cc1ccccc1)=C=C(c1ccccc1)",
    "1f": "O=C(O)C(CC=C)=C=C(c1ccccc1)",
    "1g": "O=C(O)C(Cc1ccccc1)=C=CC",
    "1h": "O=C(O)C(C)=C=C(c1ccccc1)CC",
    "1i": "O=C(O)C(CCC)=C=C(c1ccc(Br)cc1)",
    "2a": "C=CCBr",
    "2b": "C=C(c1ccccc1)CBr",
    "2c": "C=C(C)CCl",
    "2d": "C=C(Br)CBr",
    "2e": "C=CC(Cl)C",
    "2f": "ClCC=CC",
    "3a": "O=C1OC(c2ccccc2)C(CC=C)=C1CCC",
    "3b": "O=C1OC(c2ccccc2)C(CC=C)=C1C",
    "3c": "O=C1OC(c2cccc3ccccc23)C(CC=C)=C1CCC",
    "3d": "O=C1OC(c2cccc3ccccc23)C(CC=C)=C1C",
    "3e": "O=C1OC(c2ccccc2)C(CC=C)=C1Cc2ccccc2",
    "3f": "O=C1OC(c2cccc3ccccc23)C(CC(=C)c2ccccc2)=C1CCC",
    "3g": "O=C1OC(c2ccccc2)C(CC(=C)C)=C1CCC",
    "3h": "O=C1OC(c2cccc3ccccc23)C(CC(=C)C)=C1CCC",
    "3i": "O=C1OC(c2ccccc2)C(CC(=C)Br)=C1CCC",
    "3j": "O=C1OC(c2cccc3ccccc23)C(CC(=C)Br)=C1CCC",
    "3k": "O=C1OC(c2cccc3ccccc23)C(CC(=C)Br)=C1C",
    "3l": "O=C1OC(c2ccccc2)C(CC=C)=C1CC=C",
    "3m": "O=C1OC(c2cccc3ccccc23)C(CC(=C)C)=C1C",
    "3n": "O=C1OC(C)C(CC=C)=C1Cc2ccccc2",
    "3o": "O=C1OC(c2ccccc2)(CC)C(CC=C)=C1C",
    "3p": "O=C1OC(c2ccc(Br)cc2)C(CC=C)=C1CCC",
    "3q": "O=C1OC(c2ccccc2)C(CC=CC)=C1CCC",
    "3qA": "O=C1OC(c2ccccc2)C(C(C)C=C)=C1CCC",
    "6": "C=CCOC(=O)C(CCC)=C=C(c1ccccc1)",
    "PdCl2": "Cl[Pd]Cl",
    "Pd(OAc)2": "CC(=O)O[Pd]OC(C)=O",
    "K2CO3": "[K+].[K+].[O-]C([O-])=O",
    "DMA": "CC(=O)N(C)C",
    "acetonitrile": "CC#N",
    "THF": "C1CCOC1",
    "water": "O",
    "MgSO4": "[Mg+2].[O-]S(=O)(=O)[O-]",
    "ethyl acetate": "CCOC(C)=O",
}

SUB_NAMES = {
    "1a": "4-phenyl-2-propyl-2,3-butadienoic acid",
    "1b": "2,3-allenoic acid 1b (R1=Ph, R2=CH3, R3=H)",
    "1c": "2,3-allenoic acid 1c (R1=1-naphthyl, R2=n-C3H7, R3=H)",
    "1d": "2,3-allenoic acid 1d (R1=1-naphthyl, R2=CH3, R3=H)",
    "1e": "2,3-allenoic acid 1e (R1=Ph, R2=PhCH2, R3=H)",
    "1f": "2,3-allenoic acid 1f (R1=Ph, R2=allyl, R3=H)",
    "1g": "2,3-allenoic acid 1g (R1=CH3, R2=PhCH2, R3=H)",
    "1h": "2,3-allenoic acid 1h (R1=Ph, R2=CH3, R3=Et)",
    "1i": "2,3-allenoic acid 1i (R1=4-Br-C6H5, R2=n-C3H7, R3=H)",
}
ALLYL_NAMES = {
    "2a": "allyl bromide",
    "2b": "allylic bromide 2b (R4=Ph)",
    "2c": "allylic chloride 2c (R4=CH3)",
    "2d": "allylic dibromide 2d (R4=Br, X=Br)",
    "2e": "3-chloro-1-butene",
    "2f": "1-chloro-2-butene",
}


def mol(label, role, evidence, amounts=None, display_label=None):
    name = SUB_NAMES.get(label) or ALLYL_NAMES.get(label)
    if label == "3a":
        name = "4-allyl-5-phenyl-3-propyl-2(5H)-furanone"
    elif label.startswith("3"):
        name = f"butenolide {label}"
    elif label == "6":
        name = "allyl 4-phenyl-2-propyl-2,3-butadienoate"
    return participant(label, role, display_label or label, evidence, name, SMILES.get(label), amounts)


def catalyst(label, evidence, amounts=None):
    names = {
        "PdCl2": "palladium chloride",
        "Pd(OAc)2": "palladium acetate",
        "Pd(PPh3)4": "tetrakis(triphenylphosphine)palladium(0)",
        "Pd2(dba)3·CHCl3": "tris(dibenzylideneacetone)dipalladium chloroform adduct",
    }
    return participant(label, "catalyst", label, evidence, names[label], SMILES.get(label), amounts)


def solvent(label, evidence, amounts=None):
    names = {"DMA": "N,N-dimethylacetamide", "acetonitrile": "acetonitrile", "THF": "tetrahydrofuran"}
    return participant(label, "solvent", label, evidence, names.get(label, label), SMILES.get(label), amounts)


records = []
table1_ids = []
scope_ids = []
chirality_ids = []

# Table 1: each row is independent. Entry 6 also appears as Table 2 entry 1
# and as the detailed 3a experiment on page 4, so all three appearances are merged.
table1 = [
    (1, 5, "DMA", "r.t.", 38, 68),
    (2, 5, "DMA", "r.t.", 96, 65),
    (3, 5, "DMA", "r.t.", 24, 0),
    (4, 5, "acetonitrile", 50, 61, 47),
    (5, 5, "THF", 50, 84, 63),
    (6, 5, "DMA", 50, 17, 88),
    (7, 1.1, "DMA", 50, 38, 40),
    (8, 2, "DMA", 50, 38, 77),
    (9, 10, "DMA", 50, 24.5, 90),
]
for entry, equiv, solv, temp, hours, yld in table1:
    shared = entry == 6
    source_id = "table1_entry06_table2_entry01_3a" if shared else f"table1_entry{entry:02d}"
    evidence = [P2T, P2I] + ([P4T, P4I] if shared else [])
    reactant_amounts = []
    allyl_amounts = [field("equivalents", {"number": equiv, "unit": "equiv"}, [P2T, P2I])]
    cat_label = "Pd(OAc)2" if entry == 2 else "PdCl2"
    cat_amounts = [field("catalyst_loading", {"number": 5, "unit": "mol%"}, [P2T, P2I])]
    solv_amounts = []
    product_amounts = []
    unresolved = [
        "Supporting Information was mentioned but was not supplied or explicitly associated.",
        "Atmosphere is not reported.",
        "Structures are machine-assembled candidates from the displayed scaffold and remain unverified.",
    ]
    if shared:
        reactant_amounts += [
            field("amount_table2_footnote", {"number": 0.5, "unit": "mmol"}, [P2T, P2I]),
            field("mass", {"number": 50, "unit": "mg"}, [P4T, P4I]),
            field("amount_detailed_procedure", {"number": 0.25, "unit": "mmol"}, [P4T, P4I]),
        ]
        allyl_amounts += [
            field("amount_table2_footnote", {"number": 2.5, "unit": "mmol"}, [P2T, P2I]),
            field("volume", {"number": 0.11, "unit": "mL"}, [P4T, P4I]),
            field("mass", {"number": 153, "unit": "mg"}, [P4T, P4I]),
            field("amount_detailed_procedure", {"number": 1.25, "unit": "mmol"}, [P4T, P4I]),
        ]
        cat_amounts += [
            field("amount_table2_footnote", {"number": 0.022, "unit": "mmol"}, [P2T, P2I]),
            field("mass", {"number": 2, "unit": "mg"}, [P4T, P4I]),
            field("amount_detailed_procedure", {"number": 0.011, "unit": "mmol"}, [P4T, P4I]),
        ]
        solv_amounts.append(field("volume", {"number": 2, "unit": "mL"}, [P4T, P4I]))
        product_amounts.append(field("mass", {"number": 53, "unit": "mg"}, [P4T, P4I]))
        unresolved.append("The table footnote states a 0.5 mmol substrate scale, while the detailed 3a procedure states 0.25 mmol; both source values are retained without reconciliation.")
    parts = [
        mol("1a", "reactant", evidence, reactant_amounts),
        mol("2a", "reactant", evidence, allyl_amounts),
        catalyst(cat_label, evidence, cat_amounts),
        solvent(solv, evidence, solv_amounts),
        mol("3a", "product", evidence, product_amounts),
    ]
    if entry == 3:
        parts += [
            participant("K2CO3", "reagent", "K2CO3", [P2T, P2I], "potassium carbonate", SMILES["K2CO3"],
                        [field("equivalents", {"number": 1, "unit": "equiv"}, [P2T, P2I])]),
            mol("6", "product", [P2T, P2I]),
        ]
    ids = [p["entity_id"] for p in parts]
    steps = [{
        "step_id": "reaction",
        "participant_ids": ids,
        "conditions": [
            field("temperature", temp if isinstance(temp, str) else {"number": temp, "unit": "°C"}, [P2T, P2I]),
            field("time", {"number": hours, "unit": "h"}, [P2T, P2I] + ([P4T, P4I] if shared else [])),
        ],
    }]
    if shared:
        steps += [
            {"step_id": "workup", "participant_ids": ["3a"], "conditions": [
                field("workup", "Diluted with ether, washed with water, dried over MgSO4, and evaporated.", [P4T, P4I])]},
            {"step_id": "purification", "participant_ids": ["3a"], "conditions": [
                field("purification", "Flash chromatography on silica gel; petroleum ether/ethyl acetate 20:1.", [P4T, P4I])]},
        ]
    outcomes = [field("yield", {"number": yld, "unit": "%"}, [P2T, P2I] + ([P4T, P4I] if shared else []), ["3a"])]
    notes = []
    if entry == 1:
        outcomes.append(field("recovered_starting_material_yield", {"number": 20, "unit": "%"}, [P2T, P2I], ["1a"]))
    if entry == 3:
        outcomes.append(field("yield", {"number": 95, "unit": "%"}, [P2T, P2I], ["6"]))
        notes.append(("Base addition diverted the reaction to allyl allenoate 6; desired 3a was reported as 0%.", [P2T, P2I]))
    if shared:
        outcomes.append(field("yield_measurement_basis", "isolated after flash chromatography", [P4T, P4I], ["3a"]))
    else:
        outcomes.append(field("yield_measurement_basis", None, (), ["3a"]))
        unresolved.append("Yield measurement basis is not stated for this optimization row.")
    rec = record(source_id, "optimization_entry", evidence, parts, steps, outcomes, notes, unresolved)
    records.append(rec)
    table1_ids.append(rec["record_id"])
    if shared:
        scope_ids.append(rec["record_id"])

# Table 2 rows 2-17. Row 1 is represented by the shared record above.
scope_rows = [
    (2, "1b", "2a", 17.5, "3b", 83),
    (3, "1c", "2a", 21, "3c", 78),
    (4, "1d", "2a", 16, "3d", 81),
    (5, "1e", "2a", 16, "3e", 71),
    (6, "1c", "2b", 24, "3f", 93),
    (7, "1a", "2c", 24, "3g", 89),
    (8, "1c", "2c", 15.5, "3h", 95),
    (9, "1a", "2d", 21, "3i", 77),
    (10, "1c", "2d", 23, "3j", 79),
    (11, "1d", "2d", 23.5, "3k", 69),
    (12, "1f", "2a", 17, "3l", 72),
    (13, "1d", "2c", 24, "3m", 76),
    (14, "1g", "2a", 17, "3n", 52),
    (15, "1g", "2a", 17.5, "3n", 73),
    (16, "1h", "2a", 19, "3o", 83),
    (17, "1i", "2a", 11.5, "3p", 75),
]
for entry, acid, halide, hours, product, yld in scope_rows:
    ev = [P2T, P2I]
    acid_amounts = [field("amount", {"number": 0.5, "unit": "mmol"}, ev)]
    halide_amounts = ([field("equivalents", {"number": 10, "unit": "equiv"}, ev)] if entry == 15 else
                      [field("amount", {"number": 2.5, "unit": "mmol"}, ev)])
    cat_amounts = [
        field("amount", {"number": 0.022, "unit": "mmol"}, ev),
        field("catalyst_loading", {"number": 5, "unit": "mol%"}, ev),
    ]
    parts = [
        mol(acid, "reactant", ev, acid_amounts),
        mol(halide, "reactant", ev, halide_amounts),
        catalyst("PdCl2", ev, cat_amounts),
        solvent("DMA", ev),
        mol(product, "product", ev),
    ]
    rec = record(
        f"table2_entry{entry:02d}", "substrate_scope_entry", ev, parts,
        [{"step_id": "reaction", "participant_ids": [p["entity_id"] for p in parts], "conditions": [
            field("temperature", {"number": 50, "unit": "°C"}, ev),
            field("time", {"number": hours, "unit": "h"}, ev),
        ]}],
        [
            field("yield", {"number": yld, "unit": "%"}, ev, [product]),
            field("yield_measurement_basis", None, (), [product]),
        ],
        unresolved=[
            "Supporting Information was mentioned but was not supplied or explicitly associated.",
            "Yield measurement basis and atmosphere are not stated for this table row.",
            "Structures are machine-assembled candidates from the displayed R-group scaffold and remain unverified.",
        ],
    )
    records.append(rec)
    scope_ids.append(rec["record_id"])

# Scheme 1: six distinct chirality-transfer experiments.
chirality = [
    (1, "(+)-1a", "1a", ">98%", 50, 16, "(+)-3a", "3a", 90, "94%"),
    (2, "(+)-1a", "1a", ">98%", 25, 36.5, "(+)-3a", "3a", 80, ">98%"),
    (3, "(-)-1a", "1a", ">97%", 25, 36.5, "(-)-3a", "3a", 82, "99%"),
    (4, "(+)-1d", "1d", ">98%", 25, 40, "(+)-3d", "3d", 91, "90%"),
    (5, "(+)-1d", "1d", ">98%", 0, 84.5, "(+)-3d", "3d", 39, "98%"),
    (6, "(-)-1d", "1d", ">97%", 25, 40, "(-)-3d", "3d", 85, "92%"),
]


def percent_value(raw):
    if raw.startswith(">"):
        return {"number": float(raw[1:-1]), "unit": "%", "qualifier": "gt", "raw_text": raw}
    return {"number": float(raw[:-1]), "unit": "%", "raw_text": raw}


for entry, in_label, core_in, in_ee, temp, hours, out_label, core_out, yld, out_ee in chirality:
    detailed = entry == 2
    ev = [P3T, P3I] + ([P4T, P4I] if detailed else [])
    acid_amounts = [field("starting_material_ee", percent_value(in_ee), [P3T, P3I])]
    allyl_amounts = []
    cat_amounts = [field("catalyst_loading", {"number": 5, "unit": "mol%"}, [P3T, P3I])]
    dma_amounts = []
    product_amounts = []
    if detailed:
        acid_amounts += [field("mass", {"number": 50, "unit": "mg"}, [P4T, P4I]), field("amount", {"number": 0.25, "unit": "mmol"}, [P4T, P4I])]
        allyl_amounts += [field("volume", {"number": 0.11, "unit": "mL"}, [P4T, P4I]), field("mass", {"number": 153, "unit": "mg"}, [P4T, P4I]), field("amount", {"number": 1.25, "unit": "mmol"}, [P4T, P4I])]
        cat_amounts += [field("mass", {"number": 2, "unit": "mg"}, [P4T, P4I]), field("amount", {"number": 0.011, "unit": "mmol"}, [P4T, P4I])]
        dma_amounts.append(field("volume", {"number": 2, "unit": "mL"}, [P4T, P4I]))
        product_amounts.append(field("mass", {"number": 48, "unit": "mg"}, [P4T, P4I]))
    parts = [
        participant(core_in, "reactant", in_label, ev, SUB_NAMES[core_in], SMILES[core_in], acid_amounts),
        mol("2a", "reactant", ev, allyl_amounts),
        catalyst("PdCl2", ev, cat_amounts),
        solvent("DMA", ev, dma_amounts),
        participant(core_out, "product", out_label, ev,
                    "4-allyl-5-phenyl-3-propyl-2(5H)-furanone" if core_out == "3a" else "butenolide 3d",
                    SMILES[core_out], product_amounts),
    ]
    outcomes = [
        field("yield", {"number": yld, "unit": "%"}, [P3T, P3I] + ([P4T, P4I] if detailed else []), [core_out]),
        field("product_scheme_ee", percent_value(out_ee), [P3T, P3I], [core_out]),
    ]
    unresolved = [
        "Supporting Information was mentioned but was not supplied or explicitly associated.",
        "Absolute configuration was only tentatively assigned by the authors; the candidate SMILES omits stereochemistry and remains unverified.",
        "Atmosphere is not reported.",
    ]
    if detailed:
        outcomes += [
            field("product_detailed_procedure_ee", {"number": 99, "unit": "%", "qualifier": "gt", "raw_text": ">99% ee"}, [P4T, P4I], [core_out]),
            field("yield_measurement_basis", "isolated product mass reported after reaction", [P4T, P4I], [core_out]),
        ]
        unresolved.append("Scheme 1 reports product ee >98%, while the detailed procedure reports >99%; both values are retained with separate evidence.")
    else:
        outcomes.append(field("yield_measurement_basis", None, (), [core_out]))
        unresolved.append("Yield measurement basis is not stated in Scheme 1.")
    rec = record(
        f"scheme1_chirality_entry{entry:02d}", "optimization_entry", ev, parts,
        [{"step_id": "reaction", "participant_ids": [p["entity_id"] for p in parts], "conditions": [
            field("temperature", {"number": temp, "unit": "°C"}, [P3T, P3I] + ([P4T, P4I] if detailed else [])),
            field("time", {"number": hours, "unit": "h"}, [P3T, P3I] + ([P4T, P4I] if detailed else [])),
        ]}],
        outcomes,
        unresolved=unresolved,
    )
    records.append(rec)
    chirality_ids.append(rec["record_id"])

# Mechanistic schemes are explicitly classified and carry no experimental yield.
for source_id, page_ev, note in [
    ("scheme2_pdii_pathway", [P3T, P3I], "Proposed Pd(II) pathway: cyclic oxypalladation, allylic-halide insertion, and beta-dehalopalladation."),
    ("scheme3_unusual_3q_pathways", [P3T, P3I], "Proposed alternative pathways A and B for formation of unusual product 3q; this is a mechanistic proposal, not a reported yield experiment."),
    ("scheme4_2e_2f_interconversion", [P4T, P4I], "Proposed PdCl2-mediated interconversion of 2e and 2f; prose reports both isomers were observed by gas chromatography, without quantitative conversion data."),
]:
    rec = record(source_id, "mechanism", page_ev, [], [], notes=[(note, page_ev)], unresolved=[
        "Mechanistic structures and intermediates are not encoded as verified molecular structures.",
        "This record inventories a mechanism/proposal and must not be interpreted as an independent reaction yield.",
    ])
    records.append(rec)

# Probe experiments eqs 1-3.
probe_ids = []
for source_id, ev, halides, hours, products, total_yield, ratio in [
    ("equation1_probe_2e", [P3T, P3I], [("2e", None)], 16, [("3q", 91)], None, None),
    ("equation2_probe_2f", [P3T, P3I], [("2f", None)], 35.5, [("3q", None), ("3qA", None)], 19, "17:1"),
    ("equation3_probe_2e_2f_mixture", [P4T, P4I], [("2e", None), ("2f", None)], 16, [("3q", None), ("3qA", None)], 96, "98:2"),
]:
    parts = [mol("1a", "reactant", ev)] + [mol(h, "reactant", ev) for h, _ in halides]
    parts += [catalyst("PdCl2", ev, [field("catalyst_loading", {"number": 5, "unit": "mol%"}, ev)]), solvent("DMA", ev)]
    parts += [mol(p, "product", ev) for p, _ in products]
    conditions = [
        field("temperature", {"number": 50, "unit": "°C"}, ev),
        field("time", {"number": hours, "unit": "h"}, ev),
    ]
    if source_id.endswith("mixture"):
        conditions.append(field("allylic_halide_input_ratio_2e_to_2f", "1:10", ev))
    outcomes = []
    for prod, individual in products:
        if individual is not None:
            outcomes.append(field("yield", {"number": individual, "unit": "%"}, ev, [prod]))
    if total_yield is not None:
        outcomes.append(field("combined_yield", {"number": total_yield, "unit": "%"}, ev, [p for p, _ in products]))
    if ratio:
        outcomes.append(field("product_ratio_3q_to_3qA", ratio, ev, ["3q", "3qA"]))
    outcomes.append(field("yield_measurement_basis", None, (), [p for p, _ in products]))
    rec = record(source_id, "reported_experiment", ev, parts,
                 [{"step_id": "reaction", "participant_ids": [p["entity_id"] for p in parts], "conditions": conditions}],
                 outcomes,
                 unresolved=[
                     "Supporting Information was mentioned but was not supplied or explicitly associated.",
                     "Yield measurement basis, reagent quantities, and atmosphere are not stated for this equation.",
                     "Alkene geometry and product stereochemistry are not fully specified; candidate SMILES remain unverified.",
                 ])
    records.append(rec)
    probe_ids.append(rec["record_id"])

# Catalyst controls in page-3 prose.
ev = [P3T, P3I]
parts = [mol("1a", "reactant", ev), mol("2e", "reactant", ev), catalyst("Pd(PPh3)4", ev), mol("3q", "product", ev)]
control1 = record(
    "control_pdpph3_no_3q", "optimization_entry", ev, parts,
    [{"step_id": "reaction", "participant_ids": [p["entity_id"] for p in parts], "conditions": [
        field("atmosphere", "inert atmosphere", ev), field("temperature", None, ()), field("time", None, ())]}],
    [field("yield", "not obtained", ev, ["3q"]), field("yield_measurement_basis", None, (), ["3q"])],
    unresolved=[
        "The sentence does not state time, temperature, quantities, solvent, or analytical detection limit.",
        "The 1a/2e pairing is assigned from the immediately preceding 3q probe context and requires source review.",
        "Supporting Information was not supplied or explicitly associated.",
    ],
)
records.append(control1)

parts = [
    mol("1a", "reactant", ev), mol("2a", "reactant", ev),
    catalyst("Pd2(dba)3·CHCl3", ev, [field("catalyst_loading", {"number": 5, "unit": "mol%"}, ev)]),
    mol("3a", "product", ev), mol("6", "product", ev),
]
control2 = record(
    "control_pd2dba3_chcl3", "optimization_entry", ev, parts,
    [{"step_id": "reaction", "participant_ids": [p["entity_id"] for p in parts], "conditions": [field("temperature", None, ()), field("time", None, ())]}],
    [
        field("yield", {"number": 15, "unit": "%"}, ev, ["3a"]),
        field("yield", {"number": 82, "unit": "%"}, ev, ["6"]),
        field("yield_measurement_basis", None, (), ["3a", "6"]),
    ],
    unresolved=[
        "The sentence does not state time, temperature, quantities other than catalyst loading, solvent, atmosphere, or yield measurement basis.",
        "The 1a/2a pairing is assigned from the 3a/6 context and requires source review.",
        "The organopalladium catalyst structure is not encoded.",
        "Supporting Information was not supplied or explicitly associated.",
    ],
)
records.append(control2)

# Starting-material route is explicitly a known method and is not claimed as a new experiment.
ev = [P4T, P4I]
parts = [
    participant("acid_chlorides", "reactant", "acid chlorides", ev, "acid chlorides"),
    participant("ylide", "reagent", "ethyl 2-(triphenylphosphoranylidene)propionate", ev, "ethyl 2-(triphenylphosphoranylidene)propionate"),
    participant("allenoic_esters", "product", "2,3-allenoic esters", ev, "2,3-allenoic esters"),
    participant("NaOH", "reagent", "NaOH", ev, "sodium hydroxide", "[Na+].[OH-]", [field("equivalents", {"number": 1.5, "unit": "equiv"}, ev)]),
    participant("allenoic_acids", "product", "2,3-allenoic acids", ev, "2,3-allenoic acids"),
]
lit = record(
    "known_method_allenoic_acid_preparation", "literature_example", ev, parts,
    [
        {"step_id": "ylide_treatment", "participant_ids": ["acid_chlorides", "ylide", "allenoic_esters"], "conditions": []},
        {"step_id": "hydrolysis", "participant_ids": ["allenoic_esters", "NaOH", "allenoic_acids"], "conditions": []},
    ],
    notes=[("The paper states that this preparation followed a known method (reference 9).", ev)],
    unresolved=[
        "Generic substrates only; no specific product, yield, time, temperature, solvent, or workup is supplied on the inspected page.",
        "Generic structures are not encoded as SMILES.",
    ],
)
records.append(lit)

# General procedure is retained as a generic arrow/procedure, not as a row yield.
parts = [
    participant("1", "reactant", "2,3-allenoic acid 1", ev, "2,3-allenoic acid 1", amounts=[field("amount", {"number": 0.5, "unit": "mmol"}, ev)]),
    participant("2", "reactant", "allylic halide 2", ev, "allylic halide 2", amounts=[field("amount", {"number": 2.5, "unit": "mmol"}, ev)]),
    catalyst("PdCl2", ev, [field("amount", {"number": 0.025, "unit": "mmol"}, ev)]),
    solvent("DMA", ev, [field("volume", {"number": 3, "unit": "mL"}, ev)]),
    participant("3", "product", "butenolide 3", ev, "butenolide 3"),
    participant("ether", "solvent", "ether", ev, "diethyl ether", "CCOCC"),
    participant("water", "unspecified_agent", "water", ev, "water", SMILES["water"]),
    participant("MgSO4", "reagent", "MgSO4", ev, "magnesium sulfate", SMILES["MgSO4"]),
    participant("silica_gel", "reagent", "silica gel", ev, "silica gel"),
    participant("petroleum_ether", "solvent", "petroleum ether", ev, "petroleum ether"),
    participant("ethyl_acetate", "solvent", "ethyl acetate", ev, "ethyl acetate", SMILES["ethyl acetate"]),
]
general = record(
    "general_coupling_cyclization_procedure", "general_scheme", ev, parts,
    [
        {"step_id": "reaction", "participant_ids": ["1", "2", "PdCl2", "DMA", "3"], "conditions": [
            field("temperature", {"number": 50, "unit": "°C"}, ev), field("time", "stated time", ev)]},
        {"step_id": "workup", "participant_ids": ["3", "ether", "water", "MgSO4"], "conditions": [
            field("workup", "Dilute with ether, wash with water, dry over MgSO4, then evaporate.", ev)]},
        {"step_id": "purification", "participant_ids": ["3", "silica_gel", "petroleum_ether", "ethyl_acetate"], "conditions": [
            field("purification", "Flash chromatography on silica gel with petroleum ether/ethyl acetate; solid products recrystallized from ethyl acetate and petroleum ether.", ev)]},
    ],
    notes=[("Generic general procedure; product-specific time and yield are supplied by the individual table rows.", ev)],
    unresolved=[
        "This generic procedure has no single product identity or yield and must not be counted as a product-specific experiment.",
        "Atmosphere and chromatography solvent ratio are not stated in the general procedure.",
        "Generic reactant/product structures and petroleum ether/silica composition are not encoded as SMILES.",
    ],
)
records.append(general)

# Coverage ledger: exactly the visually inspected original PDF pages 1-4.
page2_ids = list(dict.fromkeys(table1_ids + scope_ids))
page3_ids = chirality_ids + [
    f"{DOC}:scheme2_pdii_pathway", f"{DOC}:scheme3_unusual_3q_pathways",
    f"{DOC}:equation1_probe_2e", f"{DOC}:equation2_probe_2f",
    control1["record_id"], control2["record_id"],
]
page4_ids = [
    f"{DOC}:scheme4_2e_2f_interconversion", f"{DOC}:equation3_probe_2e_2f_mixture",
    lit["record_id"], general["record_id"],
    f"{DOC}:table1_entry06_table2_entry01_3a", f"{DOC}:scheme1_chirality_entry02",
]
coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1,
            "state": "attempted",
            "regions": [
                {"region": "title and abstract", "finding": "Article metadata and a generic method summary; no individual experimental record or quantified arrow.", "evidence_ids": [P1I, P1T]},
                {"region": "introduction and references 1-5", "finding": "Background and cited prior work only; no experiment newly reported by this paper on this page.", "evidence_ids": [P1I, P1T]},
            ],
            "record_ids": [],
            "unresolved": ["No reaction structures are drawn on page 1; cited papers were not followed beyond the supplied source."],
        },
        {
            "page": 2,
            "state": "attempted",
            "regions": [
                {"region": "Table 1, optimization scheme, rows 1-9, and footnotes a-c", "finding": "Nine optimization rows inspected individually, including recovered 1a, Pd(OAc)2 substitution, and K2CO3 diversion to ester 6. Entry 6 is merged with the duplicate Table 2 entry 1 and detailed 3a procedure.", "evidence_ids": [P2I, P2T]},
                {"region": "Table 2, generic arrow, rows 1-17, and footnotes a-b", "finding": "Seventeen scope rows inspected; row 1 shares the merged 3a record, and rows 2-17 are independent substrate-scope records. Entry 15's 10 equiv footnote overrides the generic allylic-halide amount assignment.", "evidence_ids": [P2I, P2T]},
                {"region": "Results and discussion prose", "finding": "Narrative repeats the table outcomes and supplies interpretation; no additional independent arrow beyond the table rows.", "evidence_ids": [P2I, P2T]},
            ],
            "record_ids": page2_ids,
            "unresolved": [
                "Table yields do not state measurement basis.",
                "The Table 2 catalyst amount (0.022 mmol at 0.5 mmol scale) and arrow label (5 mol%) are both retained without silently reconciling the numerical difference.",
                "Table 2 row 1 scale conflicts with the detailed page-4 3a scale (0.5 vs 0.25 mmol).",
            ],
        },
        {
            "page": 3,
            "state": "attempted",
            "regions": [
                {"region": "Scheme 1, six condition/result lines", "finding": "Six independent chirality-transfer experiments extracted with starting ee, temperature, time, yield, and product ee.", "evidence_ids": [P3I, P3T]},
                {"region": "Scheme 2", "finding": "Proposed Pd(II)-catalyzed mechanism only; classified as mechanism, not as a reported-yield experiment.", "evidence_ids": [P3I, P3T]},
                {"region": "Scheme 3", "finding": "Two proposed pathways for unusual product 3q; classified as mechanism, not as an experimental arrow.", "evidence_ids": [P3I, P3T]},
                {"region": "equations 1 and 2", "finding": "Two independent probe experiments extracted: 2e gives 3q in 91%; 2f gives a 17:1 3q/3qA mixture in 19% combined yield.", "evidence_ids": [P3I, P3T]},
                {"region": "prose below equations 1 and 2", "finding": "Two catalyst controls extracted: Pd(PPh3)4 gives no 3q in inert atmosphere; 5 mol% Pd2(dba)3·CHCl3 gives 3a (15%) and ester 6 (82%).", "evidence_ids": [P3I, P3T]},
            ],
            "record_ids": page3_ids,
            "unresolved": [
                "The authors state that absolute configurations are tentative; stereochemical SMILES are therefore not asserted.",
                "Catalyst-control time, temperature, scale, solvent, and yield basis are not provided in the page-3 prose.",
            ],
        },
        {
            "page": 4,
            "state": "attempted",
            "regions": [
                {"region": "Scheme 4 and adjoining GC prose", "finding": "PdCl2-mediated 2e/2f interconversion is a mechanistic scheme; both isomers were observed by GC, but no quantitative conversion is given.", "evidence_ids": [P4I, P4T]},
                {"region": "equation 3", "finding": "Independent 1a plus 2e/2f (1:10) experiment extracted with 96% combined yield and 98:2 product ratio.", "evidence_ids": [P4I, P4T]},
                {"region": "Starting Materials paragraph", "finding": "Generic route explicitly attributed to a known method; classified as literature_example, not a new product-specific experiment.", "evidence_ids": [P4I, P4T]},
                {"region": "General Procedure paragraph", "finding": "Generic reaction, workup, chromatography, and recrystallization procedure inventoried without assigning a product-specific yield.", "evidence_ids": [P4I, P4T]},
                {"region": "racemic 3a detailed procedure", "finding": "Detailed 17 h/88% procedure merged with Table 1 entry 6 and Table 2 entry 1; explicit quantities, workup, purification, and product mass retained.", "evidence_ids": [P4I, P4T]},
                {"region": "(+)-3a detailed procedure", "finding": "Detailed 25 °C/36.5 h/80% experiment merged with Scheme 1 entry 2; the >99% ee detail is retained alongside Scheme 1's >98% ee.", "evidence_ids": [P4I, P4T]},
                {"region": "Supporting Information notice", "finding": "The article states SI availability, but no SI file was supplied or explicitly associated in this workspace.", "evidence_ids": [P4I, P4T]},
            ],
            "record_ids": page4_ids,
            "unresolved": [
                "SI association remains unestablished.",
                "The duplicate 3a source appearances contain a scale discrepancy (0.5 vs 0.25 mmol).",
                "Scheme 1 and the detailed (+)-3a procedure report different ee lower bounds (>98% vs >99%).",
            ],
        },
    ],
}

OUT.parent.mkdir(parents=True, exist_ok=True)
COVERAGE.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
COVERAGE.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

# Mark only this session's four pre-existing page tasks as attempted.
tasks = json.loads(TASKS.read_text())
for task in tasks:
    if task.get("document_id") == DOC and task.get("evidence_id") in {P1T, P2T, P3T, P4T}:
        page = int(task["evidence_id"].split(":page", 1)[1].split(":", 1)[0])
        task["state"] = "attempted"
        task["visual_evidence_id"] = f"{DOC}:page{page}:image"
        task["reason"] = "Original page image inspected; findings and unresolved items recorded in coverage/pages_0001_0004.json."
TASKS.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"records": len(records), "coverage_pages": [p["page"] for p in coverage["pages"]]}, ensure_ascii=False))
