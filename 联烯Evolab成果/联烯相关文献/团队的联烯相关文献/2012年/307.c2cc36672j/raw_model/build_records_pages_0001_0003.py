#!/usr/bin/env python3
"""Build machine extraction records for doc_69077f1238736cdd, PDF pages 1-3."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "runs/current"
DOC = "doc_69077f1238736cdd"

P1T = f"{DOC}:page1:text"
P1I = f"{DOC}:page1:image"
P2T = f"{DOC}:page2:text"
P2I = f"{DOC}:page2:image"
P3T = f"{DOC}:page3:text"
P3I = f"{DOC}:page3:image"


def fact(value, evidence=()):
    return {
        "value": value,
        "evidence_ids": list(evidence) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def field(name, value, evidence=(), targets=None):
    item = {"name": name, "fact": fact(value, evidence)}
    if targets:
        item["target_entity_ids"] = list(targets)
    return item


def participant(entity_id, role, label, evidence, *, name=None, smiles=None, amounts=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence) if name is not None else fact(None),
        "smiles": fact(smiles, evidence) if smiles is not None else fact(None),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": amounts or [],
    }


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
        "notes": [fact(value, ev) for value, ev in notes],
        "review": {
            "method": "model",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": list(unresolved),
        },
    }


SMILES = {
    "TMSCl": "C[Si](C)(C)Cl",
    "TMSBr": "C[Si](C)(C)Br",
    "CH2Cl2": "ClCCl",
    "CH3CN": "CC#N",
    "THF": "C1CCOC1",
    "DMF": "CN(C)C=O",
    "DMSO": "CS(C)=O",
    "CH3NO2": "C[N+](=O)[O-]",
    "1,1,1-trichloroethane": "CC(Cl)(Cl)Cl",
    "1,1,2-trichloroethane": "ClCC(Cl)Cl",
    "EtOH": "CCO",
    "NaOH": "[Na+].[OH-]",
    "HCl": "Cl",
    "FeCl3": "[Fe+3].[Cl-].[Cl-].[Cl-]",
    "Sc(OTf)3": "[Sc+3].[O-]S(=O)(=O)C(F)(F)F.[O-]S(=O)(=O)C(F)(F)F.[O-]S(=O)(=O)C(F)(F)F",
    "Zn(OTf)2": "[Zn+2].[O-]S(=O)(=O)C(F)(F)F.[O-]S(=O)(=O)C(F)(F)F",
    "AgOTf": "[Ag+].[O-]S(=O)(=O)C(F)(F)F",
    "Cu(OTf)2": "[Cu+2].[O-]S(=O)(=O)C(F)(F)F.[O-]S(=O)(=O)C(F)(F)F",
    "ZnCl2": "[Zn+2].[Cl-].[Cl-]",
    "TiCl4": "Cl[Ti](Cl)(Cl)Cl",
}


def q(number, unit, raw_text=None):
    value = {"number": number, "unit": unit}
    if raw_text is not None:
        value["raw_text"] = raw_text
    return value


records = []

# Page 1: the authors' hypothetical Scheme 1 is not a reported experiment.
records.append(
    record(
        "scheme1_assumption",
        "general_scheme",
        [P1T, P1I],
        participants=[
            participant("substrate_1", "reactant", "1", [P1T, P1I]),
            participant("intermediate_M1", "unspecified_agent", "M1", [P1T, P1I]),
            participant("hypothetical_product_2", "product", "2", [P1T, P1I]),
            participant("lewis_acid", "catalyst", "LA", [P1T, P1I]),
            participant("nucleophile", "reagent", "Nu−", [P1T, P1I]),
        ],
        notes=[
            (
                "Scheme 1 is explicitly captioned as an assumption of the reaction and proposes ring opening to M1 followed by formation of cyclohexene 2; it is not a reported experiment.",
                [P1T, P1I],
            )
        ],
        unresolved=[
            "Generic R-group structures do not define unique molecules; SMILES are intentionally null.",
            "No experimental quantities or outcome belong to this hypothetical scheme.",
        ],
    )
)


# Page 1 prose reports nine failed solvent-screen rows from unavailable Table S1.
solvent_rows = [
    (2, "CH3CN", "CH3CN"),
    (3, "DCE", None),
    (4, "THF", "THF"),
    (5, "DMF", "DMF"),
    (6, "DMSO", "DMSO"),
    (7, "CH3NO2", "CH3NO2"),
    (8, "dioxane", None),
    (9, "1,1,1-trichloroethane", "1,1,1-trichloroethane"),
    (10, "1,1,2-trichloroethane", "1,1,2-trichloroethane"),
]
for entry, solvent_label, smiles_key in solvent_rows:
    ev = [P1T, P1I]
    records.append(
        record(
            f"tableS1_entry{entry}",
            "optimization_entry",
            ev,
            participants=[
                participant("substrate_1a", "reactant", "1a", ev),
                participant("product_3a", "product", "3a", ev),
                participant("solvent", "solvent", solvent_label, ev, smiles=SMILES.get(smiles_key)),
            ],
            steps=[
                {
                    "step_id": "solvent_screen",
                    "participant_ids": ["substrate_1a", "solvent", "product_3a"],
                    "conditions": [
                        field("solvent", solvent_label, ev),
                        field("reaction_temperature", None),
                        field("reaction_time", None),
                        field("atmosphere", None),
                        field("workup", None),
                        field("purification", None),
                    ],
                }
            ],
            outcomes=[
                field("reported_result", "reaction could not proceed to afford product 3a", ev, ["product_3a"])
            ],
            notes=[
                (f"Main-text solvent list is associated in order with Table S1 entry {entry}; Table S1 itself was not supplied.", ev)
            ],
            unresolved=[
                "The cited Supporting Information/Table S1 was not supplied or explicitly associated.",
                "Per-row reagent, catalyst, scale, temperature, time, atmosphere, workup, purification, and numeric yield are not reported in the supplied main-text statement.",
                "DCE and dioxane are retained as source labels without selecting an isomer where the main text does not expand the abbreviation/name.",
            ],
        )
    )


def table_common_participants(catalyst_label, loading, *, tms="TMSCl", catalyst=True):
    ev = [P2T, P2I]
    parts = [
        participant("substrate_1a", "reactant", "1a", ev, amounts=[field("amount", q(0.2, "mmol"), ev)]),
        participant("product_3a", "product", "3a", ev),
        participant("solvent", "solvent", "CH2Cl2", ev, smiles=SMILES["CH2Cl2"], amounts=[field("volume", q(5, "mL"), ev)]),
    ]
    if tms:
        parts.append(
            participant(
                "tmsx",
                "reagent",
                tms,
                ev,
                smiles=SMILES[tms],
                amounts=[
                    field("reported_volume", q(31, "uL"), ev),
                    field("reported_density", "0.846 g mL−1", ev),
                    field("amount", q(0.24, "mmol"), ev),
                    field("equivalents", q(1.2, "equiv"), ev),
                ],
            )
        )
    if catalyst:
        parts.append(
            participant(
                "lewis_acid",
                "catalyst",
                catalyst_label,
                ev,
                smiles=SMILES.get(catalyst_label),
                amounts=[field("catalyst_loading", q(loading, "mol%"), ev)],
            )
        )
    return parts


def common_step(time_hours, participant_ids):
    ev = [P2T, P2I]
    return {
        "step_id": "ring_opening_cyclization",
        "participant_ids": participant_ids,
        "conditions": [
            field("initial_temperature", q(-10, "°C"), ev),
            field("initial_time", q(5, "min"), ev),
            field("reaction_temperature", q(30, "°C"), ev),
            field("reaction_time", q(time_hours, "h"), ev),
            field("solvent", "CH2Cl2", ev),
            field("atmosphere", "nitrogen", ev),
            field("workup", None),
            field("purification", None),
        ],
    }


# Table 1. Entry 9 is the same standard experiment as Table 2 entry 1 and is added below once.
table1 = [
    (1, "FeCl3", 10, 1, 75, "isolated yield", None),
    (2, "Sc(OTf)3", 10, 1.5, 74, "isolated yield", None),
    (3, "Zn(OTf)2", 10, 1.5, 81, "isolated yield", None),
    (4, "AgOTf", 10, 2.3, 61, "isolated yield", None),
    (5, "Cu(OTf)2", 10, 2, 73, "isolated yield", None),
    (6, "ZnCl2", 10, 24, 71, "1H NMR yield using 1,3,5-trimethylbenzene as internal standard", 10),
    (7, "TiCl4", 10, 30, 0, "isolated yield", None),
    (8, "BF3·Et2O", 10, 30, 33, "1H NMR yield using 1,3,5-trimethylbenzene as internal standard", 23),
    (10, None, None, 27, 0, "1H NMR yield using 1,3,5-trimethylbenzene as internal standard", None),
    (11, "Zn(OTf)2", 5, 27, 0, "1H NMR yield using 1,3,5-trimethylbenzene as internal standard", 100),
]
for entry, catalyst_label, loading, time_hours, yield_value, basis, recovery in table1:
    ev = [P2T, P2I]
    no_tms = entry == 11
    no_catalyst = entry == 10
    parts = table_common_participants(catalyst_label, loading, tms=None if no_tms else "TMSCl", catalyst=not no_catalyst)
    ids = [p["entity_id"] for p in parts]
    outcomes = [
        field("reported_yield_3a", q(yield_value, "%"), ev, ["product_3a"]),
        field("yield_measurement_basis", basis, ev, ["product_3a"]),
    ]
    unresolved = [
        "Substrate and product structures are legible but complex; no machine SMILES was assigned without independent structure verification.",
        "Workup and purification are not reported in the supplied main-text table.",
    ]
    notes = []
    if entry == 1:
        ev = [P1T, P1I, P2T, P2I]
        parts = table_common_participants(catalyst_label, loading)
        for p in parts:
            for obj in [p["label"], p["name"], p["smiles"], *[a["fact"] for a in p["amounts"]]]:
                if obj["value"] is not None:
                    obj["evidence_ids"] = list(dict.fromkeys(obj["evidence_ids"] + [P1T, P1I]))
        ids = [p["entity_id"] for p in parts]
        notes.append(("This row is the same initial FeCl3/CH2Cl2 trial described on page 1 and also corresponds to the DCM-best solvent context (Table S1 entry 1); it is not duplicated.", ev))
    if entry == 3:
        outcomes.append(field("narrative_loading_comparison_yield", q(84, "%"), [P2T, P2I], ["product_3a"]))
        notes.append(("The table and preceding narrative report 81%, whereas the later loading-comparison sentence says 84% for the 10 mol% Zn(OTf)2 condition.", [P2T, P2I]))
        unresolved.append("Source discrepancy: Table 1 entry 3 and one narrative sentence give 81%, but another narrative comparison gives 84%; both are preserved.")
    if recovery is not None:
        outcomes.extend(
            [
                field("recovered_starting_material_yield", q(recovery, "%"), [P2T, P2I], ["substrate_1a"]),
                field("recovery_measurement_basis", basis, [P2T, P2I], ["substrate_1a"]),
            ]
        )
    if entry == 10:
        notes.append(("Table 1 entry 10 uses no Lewis acid.", [P2T, P2I]))
    if entry == 11:
        notes.append(("Table 1 entry 11 is explicitly run in the absence of TMSCl.", [P2T, P2I]))
    records.append(
        record(
            f"table1_entry{entry}",
            "optimization_entry",
            ev,
            participants=parts,
            steps=[common_step(time_hours, ids)],
            outcomes=outcomes,
            notes=notes,
            unresolved=unresolved,
        )
    )


# The standard reaction appears as both Table 1 entry 9 and Table 2 entry 1.
ev = [P2T, P2I]
standard_parts = table_common_participants("Zn(OTf)2", 5)
records.append(
    record(
        "standard_table1_entry9_table2_entry1",
        "reported_experiment",
        ev,
        participants=standard_parts,
        steps=[common_step(2, [p["entity_id"] for p in standard_parts])],
        outcomes=[
            field("isolated_yield_3a", q(94, "%"), ev, ["product_3a"]),
            field("yield_measurement_basis", "isolated yield", ev, ["product_3a"]),
        ],
        notes=[("The identical 1a/3a, 5 mol% Zn(OTf)2, 2 h, 94% experiment is shown in both Table 1 entry 9 and Table 2 entry 1 and is represented once.", ev)],
        unresolved=[
            "Workup and purification are not reported in the supplied main-text table.",
            "Complex substrate/product structures remain machine-unverified and have null SMILES.",
        ],
    )
)


table2 = [
    (2, "Et", "n-C4H9", "Me", "1b", 5, 87, "3b", 5, "TMSCl"),
    (3, "Et", "Bn", "Me", "1c", 3, 81, "3c", 5, "TMSCl"),
    (4, "Et", "Et", "Me", "1d", 3.5, 89, "3d", 6, "TMSCl"),
    (5, "Et", "C10H21", "Me", "1e", 6, 96, "3e", 5, "TMSCl"),
    (6, "Et", "Allyl", "Me", "1f", 4, 44, "3f", 5, "TMSCl"),
    (7, "Et", "CH3", "Me", "1g", 2, 74, "3g", 6, "TMSCl"),
    (8, "Et", "n-C6H13", "Et", "1h", 4, 90, "3h", 6, "TMSCl"),
    (9, "Et", "n-C6H13", "Bn", "1i", 4.5, 76, "3i", 5, "TMSCl"),
    (10, "−(CH2)5−", "n-C6H13", "Me", "1j", 5.5, 74, "3j", 5, "TMSCl"),
    (11, "−(CH2)4−", "n-C6H13", "Me", "1k", 5, 50, "3k", 5, "TMSCl"),
    (12, "Me", "Me", "Me", "1l", 3, 79, "3l", 5, "TMSCl"),
    (13, "−(CH2)5−", "Bn", "Me", "1m", 12, 62, "3m", 5, "TMSCl"),
    (14, "Et", "n-C4H9", "Me", "1b", 7, 62, "3n", 5, "TMSBr"),
]
for entry, r1, r2, r3, substrate_label, time_hours, yield_value, product_label, loading, tms in table2:
    ev = [P2T, P2I]
    substrate = participant(
        "substrate",
        "reactant",
        substrate_label,
        ev,
        name=f"Table 2 substrate {substrate_label}: R1={r1}, R2={r2}, R3={r3}",
        amounts=[field("amount", q(0.2, "mmol"), ev)],
    )
    product = participant("product", "product", product_label, ev, name=f"cyclopentene product {product_label}")
    tms_amounts = [field("amount", q(0.24, "mmol"), ev), field("equivalents", q(1.2, "equiv"), ev)]
    if tms == "TMSBr":
        tms_amounts = [
            field("reported_volume", q(31.5, "uL"), ev),
            field("reported_density", "1.16 g mL−1", ev),
            field("amount", q(0.24, "mmol"), ev),
            field("equivalents", q(1.2, "equiv"), ev),
        ]
    parts = [
        substrate,
        product,
        participant("tmsx", "reagent", tms, ev, smiles=SMILES[tms], amounts=tms_amounts),
        participant("catalyst", "catalyst", "Zn(OTf)2", ev, smiles=SMILES["Zn(OTf)2"], amounts=[field("catalyst_loading", q(loading, "mol%"), ev)]),
        participant("solvent", "solvent", "CH2Cl2", ev, smiles=SMILES["CH2Cl2"], amounts=[field("volume", q(5, "mL"), ev)]),
    ]
    note_evidence = list(ev)
    notes = [(f"Table 2 substituents: R1={r1}, R2={r2}, R3={r3}; TMSX={tms}; product X={'Br' if tms == 'TMSBr' else 'Cl'}.", ev)]
    if entry in (5, 10, 13):
        note_evidence += [P3T, P3I]
        notes.append(("The acknowledgements state that the preparation result for this Table 2 entry was reproduced by Mr Youai Qiu.", [P3T, P3I]))
    records.append(
        record(
            f"table2_entry{entry}",
            "substrate_scope_entry",
            note_evidence,
            participants=parts,
            steps=[common_step(time_hours, [p["entity_id"] for p in parts])],
            outcomes=[
                field(f"isolated_yield_{product_label}", q(yield_value, "%"), ev, ["product"]),
                field("yield_measurement_basis", "isolated yield", ev, ["product"]),
            ],
            notes=notes,
            unresolved=[
                "Workup and purification are not reported in the supplied main-text table.",
                "The depicted substrate/product connectivity has not been independently structure-verified; SMILES are null.",
            ],
        )
    )


# Table 2 entry 1 footnote c is a separate scale-up experiment, not the 0.2 mmol row.
ev = [P2T, P2I]
scale_parts = [
    participant(
        "substrate_1a",
        "reactant",
        "1a",
        ev,
        amounts=[field("amount", q(4.7, "mmol"), ev), field("mass", q(1.7014, "g"), ev)],
    ),
    participant("product_3a", "product", "3a", ev),
    participant("tmscl", "reagent", "TMSCl", ev, smiles=SMILES["TMSCl"], amounts=[field("amount", q(5.64, "mol", "5.64 mol"), ev)]),
    participant("catalyst", "catalyst", "Zn(OTf)2", ev, smiles=SMILES["Zn(OTf)2"], amounts=[field("catalyst_loading", q(5, "mol%"), ev)]),
    participant("solvent", "solvent", "CH2Cl2", ev, smiles=SMILES["CH2Cl2"], amounts=[field("volume", q(35, "mL"), ev)]),
]
records.append(
    record(
        "table2_entry1_scaleup",
        "reported_experiment",
        ev,
        participants=scale_parts,
        steps=[common_step(2, [p["entity_id"] for p in scale_parts])],
        outcomes=[
            field("isolated_yield_3a", q(83, "%"), ev, ["product_3a"]),
            field("yield_measurement_basis", "isolated yield", ev, ["product_3a"]),
        ],
        notes=[("The footnote visibly prints TMSCl as 5.64 mol; this source value is preserved without silently changing it to mmol.", ev)],
        unresolved=[
            "The printed 5.64 mol TMSCl is inconsistent with a 4.7 mmol substrate charge and the stated 1.2-equivalent standard condition; the likely unit typo is not corrected without another source.",
            "Workup and purification are not reported.",
            "Complex substrate/product structures remain machine-unverified and have null SMILES.",
        ],
    )
)


# Scheme 2: a distinct two-operation hydrolysis/quench experiment.
ev = [P2T, P2I, P3T, P3I]
hydrolysis_parts = [
    participant("reactant_3l", "reactant", "3l", [P2T, P2I]),
    participant("naoh", "reagent", "NaOH", [P2T, P2I], smiles=SMILES["NaOH"], amounts=[field("concentration", q(2, "M"), [P2T, P2I])]),
    participant("ethanol", "solvent", "EtOH", [P2T, P2I], smiles=SMILES["EtOH"]),
    participant("hcl", "reagent", "HCl", [P2T, P2I], smiles=SMILES["HCl"]),
    participant("product_4", "product", "4", [P2T, P2I]),
]
records.append(
    record(
        "scheme2_hydrolysis_3l_to_4",
        "reported_experiment",
        ev,
        participants=hydrolysis_parts,
        steps=[
            {
                "step_id": "hydrolysis",
                "participant_ids": ["reactant_3l", "naoh", "ethanol"],
                "conditions": [
                    field("solvent", "EtOH", [P2T, P2I]),
                    field("reaction_temperature", q(60, "°C"), [P2T, P2I]),
                    field("reaction_time", q(1, "h"), [P2T, P2I]),
                    field("atmosphere", None),
                    field("workup", None),
                    field("purification", None),
                ],
            },
            {
                "step_id": "acid_quench",
                "participant_ids": ["hcl", "product_4"],
                "conditions": [field("operation", "quench with HCl", [P2T, P2I])],
            },
        ],
        outcomes=[
            field("isolated_yield_4", q(94, "%"), [P2T, P2I], ["product_4"]),
            field("yield_measurement_basis", "isolated yield", [P2T, P2I], ["product_4"]),
            field("physical_form", "solid product", [P2T, P2I], ["product_4"]),
        ],
        notes=[
            ("Product 4 was confirmed by X-ray diffraction; the ORTEP is shown in Scheme 2.", [P2T, P2I]),
            ("Note 14 on page 3 reports crystal data for compound 4; this is characterization evidence, not a separate reaction.", [P3T, P3I]),
        ],
        unresolved=[
            "Reaction scale, reagent/solvent volumes, atmosphere, workup before the HCl quench, and purification are not reported in the supplied main text.",
            "Structures of 3l and 4 remain machine-unverified; SMILES are null.",
        ],
    )
)


# A separate negative substrate-control result described in the mechanistic discussion.
ev = [P2T, P2I]
records.append(
    record(
        "prose_R2_H_control",
        "optimization_entry",
        ev,
        participants=[
            participant("r2_h_substrate", "reactant", "cyclopropylvinylallene with R2 = H", ev),
            participant("generic_product_3", "product", "3", ev),
        ],
        steps=[
            {
                "step_id": "reported_control",
                "participant_ids": ["r2_h_substrate", "generic_product_3"],
                "conditions": [
                    field("reaction_temperature", None),
                    field("reaction_time", None),
                    field("solvent", None),
                    field("atmosphere", None),
                    field("workup", None),
                    field("purification", None),
                ],
            }
        ],
        outcomes=[field("reported_result", "reaction was completely shut down when R2 was a proton", ev, ["generic_product_3"])],
        notes=[("The authors discuss this negative result as evidence that substitution at R2 is essential to ring opening.", ev)],
        unresolved=[
            "The exact substrate label/structure, scale, reagents, catalyst, solvent, temperature, time, atmosphere, workup, purification, and numeric yield are not stated in the supplied sentence.",
            "The generic R-group structure cannot be assigned a unique SMILES.",
        ],
    )
)


# Pages 2-3: proposed mechanism, not an experiment.
ev = [P2T, P2I, P3T, P3I]
records.append(
    record(
        "scheme3_plausible_mechanism",
        "mechanism",
        ev,
        participants=[
            participant("substrate_1", "reactant", "1", ev),
            participant("product_3", "product", "3", ev),
            participant("tmsx", "reagent", "TMSX", ev),
            participant("lewis_acid", "catalyst", "LA", ev),
            participant("proton", "reagent", "H+", ev),
        ],
        notes=[
            ("Scheme 3 is captioned as a plausible mechanism and depicts intermediates A-E: Lewis-acid activation/ring opening, X− attack at the allene, intramolecular cyclopropanation, ring expansion, and protonation to product 3.", ev)
        ],
        unresolved=[
            "This is a proposed catalytic mechanism rather than a reported experiment; no experimental yield or conditions are assigned.",
            "Generic R groups, LA, and TMSX do not define unique molecular structures; SMILES remain null.",
        ],
    )
)


record_ids = [r["record_id"] for r in records]
assert len(record_ids) == len(set(record_ids)) == 38

dataset = json.loads((OUT / "dataset.json").read_text())
existing = {r["record_id"] for r in dataset["experiments"]}
overlap = existing.intersection(record_ids)
if overlap:
    raise SystemExit(f"Refusing to overwrite existing records: {sorted(overlap)}")

raw_path = OUT / "raw_model/records_pages_0001_0003.json"
raw_path.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")


page1_ids = [f"{DOC}:scheme1_assumption", f"{DOC}:table1_entry1"] + [f"{DOC}:tableS1_entry{i}" for i in range(2, 11)]
page2_ids = (
    [f"{DOC}:table1_entry{i}" for i in range(1, 9)]
    + [f"{DOC}:standard_table1_entry9_table2_entry1", f"{DOC}:table1_entry10", f"{DOC}:table1_entry11"]
    + [f"{DOC}:table2_entry{i}" for i in range(2, 15)]
    + [
        f"{DOC}:table2_entry1_scaleup",
        f"{DOC}:scheme2_hydrolysis_3l_to_4",
        f"{DOC}:prose_R2_H_control",
        f"{DOC}:scheme3_plausible_mechanism",
    ]
)
page3_ids = [
    f"{DOC}:scheme3_plausible_mechanism",
    f"{DOC}:table2_entry5",
    f"{DOC}:table2_entry10",
    f"{DOC}:table2_entry13",
    f"{DOC}:scheme2_hydrolysis_3l_to_4",
]

coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1,
            "state": "attempted",
            "regions": [
                {
                    "region": "page 1 upper-right, Scheme 1 reaction drawing and caption",
                    "finding": "Hypothetical ring-opening/cyclization assumption from generic substrate 1 through M1 to proposed cyclohexene 2; classified as a general scheme, not a reported experiment.",
                    "evidence_ids": [P1T, P1I],
                },
                {
                    "region": "page 1 lower-left and center introduction",
                    "finding": "Background and cited prior intramolecular cycloaddition/allene literature; not imported as experiments of this paper.",
                    "evidence_ids": [P1T, P1I],
                },
                {
                    "region": "page 1 lower-right initial trial and solvent-screen prose",
                    "finding": "Initial 1a/TMSCl/10 mol% FeCl3 trial in CH2Cl2 is merged with Table 1 entry 1 on page 2. Nine named non-CH2Cl2 solvent trials from cited Table S1 entries 2-10 are retained separately as qualitative failures; the SI table itself is unavailable.",
                    "evidence_ids": [P1T, P1I, P2T, P2I],
                },
                {
                    "region": "page 1 footnote describing ESI availability",
                    "finding": "The paper advertises Table S1, experimental details, analytical data, and spectra as ESI, but no SI file was supplied or explicitly associated; no SI-only details were inferred.",
                    "evidence_ids": [P1T, P1I],
                },
            ],
            "record_ids": page1_ids,
            "unresolved": [
                "Table S1 and the remainder of the cited ESI are not supplied/associated, so solvent-row conditions and numeric outcomes beyond the main-text qualitative statement remain missing.",
                "Generic and complex drawn structures have not been independently structure-verified; their SMILES remain null.",
            ],
        },
        {
            "page": 2,
            "state": "attempted",
            "regions": [
                {
                    "region": "page 2 upper-left, Table 1 scheme, rows 1-11, and footnotes a-e",
                    "finding": "Eleven Lewis-acid/control optimization rows were read individually. Table 1 entry 9 is merged with identical Table 2 entry 1. NMR yields and recovered 1a in rows 6, 8, 10, and 11 are kept distinct from isolated product yields.",
                    "evidence_ids": [P2T, P2I],
                },
                {
                    "region": "page 2 upper-right, Table 2 scheme, rows 1-14, and footnotes a-e",
                    "finding": "Fourteen substrate-scope rows were read row-by-row; rows 4, 7, and 8 use 6 mol% Zn(OTf)2 and row 14 uses TMSBr to give bromide 3n. The 4.7 mmol/83% footnote is a separate scale-up experiment.",
                    "evidence_ids": [P2T, P2I],
                },
                {
                    "region": "page 2 Table 2 footnote c",
                    "finding": "The scale-up footnote visibly prints TMSCl as 5.64 mol for 4.7 mmol of 1a. This apparent source-unit error is preserved and flagged, not silently corrected.",
                    "evidence_ids": [P2T, P2I],
                },
                {
                    "region": "page 2 lower-left narrative below Tables 1 and 2",
                    "finding": "Narrative duplicates the standard/scale-up results. A source discrepancy for the 10 mol% Zn(OTf)2 result (81% in table/one sentence versus 84% in a later comparison) is retained in Table 1 entry 3.",
                    "evidence_ids": [P2T, P2I],
                },
                {
                    "region": "page 2 center-right, Scheme 2 hydrolysis arrow and ORTEP",
                    "finding": "Distinct hydrolysis of 3l with 2 M NaOH in EtOH at 60 °C for 1 h, followed by HCl quench, affords solid 4 in 94% isolated yield; X-ray/ORTEP is characterization, not another experiment.",
                    "evidence_ids": [P2T, P2I],
                },
                {
                    "region": "page 2 lower-right mechanistic discussion",
                    "finding": "A separate R2=H substrate control is reported as completely shut down, with most operational details unstated. The remaining prose proposes the A-E mechanism shown on page 3 and is classified as mechanism, not experiment.",
                    "evidence_ids": [P2T, P2I, P3T, P3I],
                },
            ],
            "record_ids": page2_ids,
            "unresolved": [
                "Most table rows omit workup and purification; the R2=H control also omits exact substrate identity and all operational conditions.",
                "The source disagreement 81% versus 84% for 10 mol% Zn(OTf)2 remains unresolved.",
                "The scale-up footnote's printed 5.64 mol TMSCl is chemically inconsistent with 4.7 mmol substrate and is retained as printed pending source review.",
                "No SI was supplied, so product analytical data and detailed procedures were not imported.",
            ],
        },
        {
            "page": 3,
            "state": "attempted",
            "regions": [
                {
                    "region": "page 3 upper-left, Scheme 3 catalytic cycle",
                    "finding": "Plausible Lewis-acid-promoted ring-opening/cyclization mechanism through generic intermediates A-E; classified as mechanism and not assigned an experimental yield.",
                    "evidence_ids": [P3T, P3I, P2T, P2I],
                },
                {
                    "region": "page 3 left column below Scheme 3, conclusion and acknowledgements",
                    "finding": "No new reaction arrow. The acknowledgement says preparations for Table 2 entries 5, 10, and 13 were reproduced; this is linked to those existing rows without creating duplicates.",
                    "evidence_ids": [P3T, P3I],
                },
                {
                    "region": "page 3 references and crystal-data note 14",
                    "finding": "References are prior literature and not experiments of this paper. Note 14 characterizes compound 4 crystallographically and is linked to the Scheme 2 hydrolysis record, not counted as a new reaction.",
                    "evidence_ids": [P3T, P3I],
                },
            ],
            "record_ids": page3_ids,
            "unresolved": [
                "Generic mechanistic structures and intermediates A-E do not define unique machine-verifiable SMILES.",
                "No SI or CIF was supplied/associated; only the printed main-text crystal note is available.",
            ],
        },
    ],
}

coverage_path = OUT / "coverage/pages_0001_0003.json"
coverage_path.parent.mkdir(parents=True, exist_ok=True)
coverage_path.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

# Mark only this document's page tasks as attempted.
tasks_path = OUT / "tasks.json"
tasks = json.loads(tasks_path.read_text())
for task in tasks:
    if task.get("document_id") == DOC and task.get("evidence_id") in {P1T, P2T, P3T}:
        task["state"] = "attempted"
        task["reason"] = "Original page image and extracted text inspected; records and coverage ledger created."
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"records": len(records), "raw": str(raw_path), "coverage": str(coverage_path)}, ensure_ascii=False))
