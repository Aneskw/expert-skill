#!/usr/bin/env python3
"""Build evidence-linked machine records for ja910503k PDF pages 1-2."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
DOC = "doc_2c944c2c55730a50"
P1T = f"{DOC}:page1:text"
P1I = f"{DOC}:page1:image"
P2T = f"{DOC}:page2:text"
P2I = f"{DOC}:page2:image"
EV1 = [P1T, P1I]
EV2 = [P2T, P2I]
EV12 = [P1T, P1I, P2T, P2I]


def fact(value, evidence):
    return {
        "value": value,
        "evidence_ids": list(dict.fromkeys(evidence)) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def field(name, value, evidence, targets=None):
    result = {"name": name, "fact": fact(value, evidence)}
    if targets:
        result["target_entity_ids"] = targets
    return result


def participant(entity_id, role, label, evidence, *, name=None, smiles=None, amounts=None):
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


def record(source_id, kind, evidence, participants, steps, outcomes, *, notes=None, unresolved=None):
    return {
        "record_id": f"{DOC}:{source_id}",
        "document_id": DOC,
        "source_reaction_id": source_id,
        "record_kind": kind,
        "status": "needs_review",
        "completeness": "partial",
        "evidence_ids": list(dict.fromkeys(evidence)),
        "participants": participants,
        "steps": steps,
        "outcomes": outcomes,
        "notes": [fact(x, evidence) for x in (notes or [])],
        "review": {
            "method": "model",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved or [],
        },
    }


def amount(name, number, unit, evidence):
    return field(name, {"number": number, "unit": unit}, evidence)


def missing_operations(extra=None):
    result = [
        "Supporting information was mentioned but was not supplied or explicitly associated.",
        "Atmosphere, workup, and purification are not stated in the supplied main-text pages.",
    ]
    result.extend(extra or [])
    return result


records = []

# Table 1: every catalyst row is an independent optimization experiment.
catalysts = {
    "FeCl3": "[Cl-].[Cl-].[Cl-].[Fe+3]",
    "MgI2": "[I-].[I-].[Mg+2]",
    "CdI2": "[I-].[I-].[Cd+2]",
    "ZnI2": "[I-].[I-].[Zn+2]",
    "ZnCl2": "[Cl-].[Cl-].[Zn+2]",
    "ZnBr2": "[Br-].[Br-].[Zn+2]",
}
table1 = [
    (1, "FeCl3", 20.0, 0, None),
    (2, "MgI2", 2.0, 0, None),
    (3, "CdI2", 2.6, 36, "isolated"),
    (4, "ZnI2", 2.6, 38, "isolated"),
    (5, "ZnCl2", 5.5, 16, "NMR"),
    (6, "ZnBr2", 5.5, 17, "NMR"),
]
for entry, catalyst, hours, reported_yield, basis in table1:
    ps = [
        participant("alkyne_1a", "reactant", "1a", EV1, name="1-decyne", smiles="CCCCCCCCC#C", amounts=[amount("reaction_scale", 0.3, "mmol", EV1)]),
        participant("aldehyde_2a", "reactant", "PhCHO (2a)", EV1, name="benzaldehyde", smiles="O=Cc1ccccc1", amounts=[amount("equivalents", 1.7, "equiv", EV1)]),
        participant("morpholine", "reagent", "morpholine", EV1, name="morpholine", smiles="C1COCCN1", amounts=[amount("equivalents", 1.5, "equiv", EV1)]),
        participant("catalyst", "catalyst", catalyst, EV1, name=catalyst, smiles=catalysts[catalyst], amounts=[amount("catalyst_equivalents", 0.6, "equiv", EV1)]),
        participant("toluene", "solvent", "toluene", EV1, name="toluene", smiles="Cc1ccccc1", amounts=[amount("volume", 0.9, "mL", EV1)]),
        participant("product_3aa", "product", "3aa", EV1, name="1-octyl-3-phenylallene (3aa)", smiles="CCCCCCCCC=C=Cc1ccccc1"),
    ]
    conditions = [
        field("temperature", {"number": 150, "unit": "°C"}, EV1),
        field("time", {"number": hours, "unit": "h"}, EV1),
        field("operation", "reaction tube sealed with a screw cap", EV1),
    ]
    outcomes = [
        field("reported_yield_3aa", {"number": reported_yield, "unit": "%"}, EV1, ["product_3aa"]),
        field("yield_measurement_basis", basis, EV1, ["product_3aa"]),
    ]
    if reported_yield == 0:
        outcomes.append(field("product_observation", "not observed", EV1, ["product_3aa"]))
    records.append(record(
        f"table1_entry{entry}", "optimization_entry", EV1, ps,
        [{"step_id": "one_pot_reaction", "participant_ids": [p["entity_id"] for p in ps if p["role"] != "product"], "conditions": conditions}],
        outcomes,
        unresolved=missing_operations(["The yield measurement basis is not stated for the zero-yield row."] if basis is None else []),
    ))

# Zn(OTf)2 is an explicit additional screening experiment in the paragraph next to Table 1.
znotf_smiles = "[Zn+2].O=S(=O)([O-])C(F)(F)F.O=S(=O)([O-])C(F)(F)F"
ps = [
    participant("alkyne_1a", "reactant", "1a", EV1, name="1-decyne", smiles="CCCCCCCCC#C", amounts=[amount("reaction_scale", 0.3, "mmol", EV1)]),
    participant("aldehyde_2a", "reactant", "PhCHO (2a)", EV1, name="benzaldehyde", smiles="O=Cc1ccccc1", amounts=[amount("equivalents", 1.7, "equiv", EV1)]),
    participant("morpholine", "reagent", "morpholine", EV1, name="morpholine", smiles="C1COCCN1", amounts=[amount("equivalents", 1.5, "equiv", EV1)]),
    participant("catalyst", "catalyst", "Zn(OTf)2", EV1, name="zinc triflate", smiles=znotf_smiles, amounts=[amount("catalyst_equivalents", 0.6, "equiv", EV1)]),
    participant("toluene", "solvent", "toluene", EV1, name="toluene", smiles="Cc1ccccc1", amounts=[amount("volume", 0.9, "mL", EV1)]),
    participant("product_3aa", "product", "3aa", EV1, name="1-octyl-3-phenylallene (3aa)", smiles="CCCCCCCCC=C=Cc1ccccc1"),
]
records.append(record(
    "prose_znotf2_screen", "optimization_entry", EV1, ps,
    [{"step_id": "one_pot_reaction", "participant_ids": [p["entity_id"] for p in ps if p["role"] != "product"], "conditions": [
        field("temperature", {"number": 150, "unit": "°C"}, EV1),
        field("time", {"number": 4.8, "unit": "h"}, EV1),
        field("operation", "reaction tube sealed with a screw cap", EV1),
    ]}],
    [
        field("reported_yield_3aa", {"number": 19, "unit": "%"}, EV1, ["product_3aa"]),
        field("yield_measurement_basis", "NMR", EV1, ["product_3aa"]),
    ],
    notes=["The Zn(OTf)2 result is reported in prose immediately after the Table 1 catalyst comparison."],
    unresolved=missing_operations(),
))

# Solvent-screen failures are explicit, but their SI-only loadings and times are unavailable.
solvents = [
    ("MeNO2", "nitromethane", "C[N+](=O)[O-]"),
    ("CHCl3", "chloroform", "ClC(Cl)Cl"),
    ("DCE", "1,2-dichloroethane", "ClCCCl"),
    ("MeCN", "acetonitrile", "CC#N"),
]
for label, name, smiles in solvents:
    ps = [
        participant("alkyne_1a", "reactant", "1a", EV1, name="1-decyne", smiles="CCCCCCCCC#C"),
        participant("aldehyde_2a", "reactant", "2a", EV1, name="benzaldehyde", smiles="O=Cc1ccccc1"),
        participant("morpholine", "reagent", "morpholine", EV1, name="morpholine", smiles="C1COCCN1"),
        participant("screened_solvent", "solvent", label, EV1, name=name, smiles=smiles),
        participant("product_3aa", "product", "3aa", EV1, name="allene 3aa", smiles="CCCCCCCCC=C=Cc1ccccc1"),
    ]
    records.append(record(
        f"prose_solvent_{label.lower()}", "optimization_entry", EV1, ps,
        [{"step_id": "solvent_screen", "participant_ids": [p["entity_id"] for p in ps if p["role"] != "product"], "conditions": [
            field("temperature", None, []), field("time", None, []),
        ]}],
        [field("reaction_result", "no product formed", EV1, ["product_3aa"])],
        unresolved=missing_operations([
            "Table S1 was not supplied; catalyst identity/loading, participant quantities, temperature, and time for this solvent row are missing.",
            "The qualitative no-product statement was not converted to a numeric zero yield.",
        ]),
    ))

# The main text explicitly summarizes one piperidine comparison from unavailable Table S2.
ps = [
    participant("alkyne_1a", "reactant", "1a", EV1, name="1-decyne", smiles="CCCCCCCCC#C"),
    participant("aldehyde_2a", "reactant", "2a", EV1, name="benzaldehyde", smiles="O=Cc1ccccc1"),
    participant("piperidine", "reagent", "piperidine", EV1, name="piperidine", smiles="C1CCNCC1"),
    participant("product_3aa", "product", "3aa", EV1, name="allene 3aa", smiles="CCCCCCCCC=C=Cc1ccccc1"),
]
records.append(record(
    "prose_piperidine_less_effective", "optimization_entry", EV1, ps,
    [{"step_id": "amine_screen", "participant_ids": ["alkyne_1a", "aldehyde_2a", "piperidine"], "conditions": [
        field("temperature", None, []), field("time", None, []),
    ]}],
    [field("comparative_result", "piperidine was less effective than morpholine", EV1, ["product_3aa"]), field("yield_measurement_basis", None, [], ["product_3aa"])],
    unresolved=missing_operations([
        "Table S2 was not supplied; catalyst, loadings, scale, solvent, temperature, time, numeric yield, and measurement basis are missing.",
        "The qualitative comparison was not converted to a numeric yield.",
    ]),
))

# Table S3 entry 7 is identified in prose with its optimized equivalents/temperature but no numeric yield.
ps = [
    participant("alkyne_1a", "reactant", "1a", EV1, name="1-decyne", smiles="CCCCCCCCC#C"),
    participant("aldehyde_2a", "reactant", "2a", EV1, name="benzaldehyde", smiles="O=Cc1ccccc1", amounts=[amount("equivalents", 1.8, "equiv", EV1)]),
    participant("morpholine", "reagent", "morpholine", EV1, name="morpholine", smiles="C1COCCN1", amounts=[amount("equivalents", 1.4, "equiv", EV1)]),
    participant("zni2", "reagent", "ZnI2", EV1, name="zinc iodide", smiles="[I-].[I-].[Zn+2]", amounts=[amount("equivalents", 0.8, "equiv", EV1)]),
    participant("toluene", "solvent", "toluene", EV1, name="toluene", smiles="Cc1ccccc1"),
    participant("product_3aa", "product", "3aa", EV1, name="allene 3aa", smiles="CCCCCCCCC=C=Cc1ccccc1"),
]
records.append(record(
    "prose_table_s3_entry7", "optimization_entry", EV1, ps,
    [{"step_id": "parameter_screen", "participant_ids": [p["entity_id"] for p in ps if p["role"] != "product"], "conditions": [
        field("temperature", {"number": 130, "unit": "°C"}, EV1), field("time", None, []),
    ]}],
    [field("comparative_result", "highest yield in Table S3", EV1, ["product_3aa"]), field("yield_measurement_basis", None, [], ["product_3aa"])],
    unresolved=missing_operations([
        "Table S3 was not supplied; reaction scale, toluene volume, time, numeric yield, and measurement basis for entry 7 are missing.",
        "This SI-table entry is kept separate from the subsequent 1 mmol concentration series because the source does not establish batch identity.",
    ]),
))

# Concentration study: the 5 mL/65% point is Table 2 entry 1 and is merged there.
for volume, isolated_yield in [(1, 37), (3, 56), (7, 61)]:
    ps = [
        participant("alkyne_1a", "reactant", "1a", EV1, name="1-decyne", smiles="CCCCCCCCC#C", amounts=[amount("reaction_scale", 1.0, "mmol", EV1)]),
        participant("aldehyde_2a", "reactant", "2a", EV1, name="benzaldehyde", smiles="O=Cc1ccccc1", amounts=[amount("equivalents", 1.8, "equiv", EV1)]),
        participant("morpholine", "reagent", "morpholine", EV1, name="morpholine", smiles="C1COCCN1", amounts=[amount("equivalents", 1.4, "equiv", EV1)]),
        participant("zni2", "reagent", "ZnI2", EV1, name="zinc iodide", smiles="[I-].[I-].[Zn+2]", amounts=[amount("equivalents", 0.8, "equiv", EV1)]),
        participant("toluene", "solvent", "toluene", EV1, name="toluene", smiles="Cc1ccccc1", amounts=[amount("volume", volume, "mL", EV1)]),
        participant("product_3aa", "product", "3aa", EV1, name="allene 3aa", smiles="CCCCCCCCC=C=Cc1ccccc1"),
    ]
    records.append(record(
        f"prose_concentration_{volume}ml", "optimization_entry", EV1, ps,
        [{"step_id": "concentration_study", "participant_ids": [p["entity_id"] for p in ps if p["role"] != "product"], "conditions": [
            field("temperature", {"number": 130, "unit": "°C"}, EV1), field("time", None, []),
        ]}],
        [
            field("isolated_yield_3aa", {"number": isolated_yield, "unit": "%"}, EV1, ["product_3aa"]),
            field("yield_measurement_basis", "isolated", EV1, ["product_3aa"]),
        ],
        notes=["The paper reports this result as one point in the 1, 3, 5, and 7 mL toluene concentration series."],
        unresolved=missing_operations(["Reaction time is not stated for the concentration-series point."]),
    ))

# Table 2 substrate scope.
alkynes = {
    "1a": ("CH3(CH2)7 (1a)", "1-decyne", "CCCCCCCCC#C"),
    "1b": ("CH3(CH2)9 (1b)", "1-dodecyne", "CCCCCCCCCCC#C"),
    "1c": ("p-O2NC6H4CH2O(CH2)2 (1c)", "terminal alkyne 1c", None),
    "1d": ("p-O2NC6H4CH2OCH2 (1d)", "terminal propargylic ether 1d", None),
}
aldehydes = {
    "2a": ("Ph (2a)", "benzaldehyde", "O=Cc1ccccc1"),
    "2b": ("p-ClC6H4 (2b)", "4-chlorobenzaldehyde", "O=Cc1ccc(Cl)cc1"),
    "2c": ("p-BrC6H4 (2c)", "4-bromobenzaldehyde", "O=Cc1ccc(Br)cc1"),
    "2d": ("3-thienyl (2d)", "thiophene-3-carbaldehyde", "O=Cc1ccsc1"),
    "2e": ("p-F3CC6H4 (2e)", "4-(trifluoromethyl)benzaldehyde", "O=Cc1ccc(C(F)(F)F)cc1"),
    "2f": ("i-Pr (2f)", "2-methylpropanal", "CC(C)C=O"),
    "2g": ("n-Bu (2g)", "pentanal", "CCCCC=O"),
}
table2 = [
    (1, "1a", "2a", 7.2, 65, "3aa", 5, 130, False, "CCCCCCCCC=C=Cc1ccccc1"),
    (2, "1a", "2b", 6.7, 52, "3ab", 3, 130, False, "CCCCCCCCC=C=Cc1ccc(Cl)cc1"),
    (3, "1a", "2c", 6.8, 53, "3ac", 3, 130, False, "CCCCCCCCC=C=Cc1ccc(Br)cc1"),
    (4, "1a", "2d", 13.7, 30, "3ad", 3, 130, False, "CCCCCCCCC=C=Cc1ccsc1"),
    (5, "1b", "2a", 9.7, 57, "3ba", 5, 130, False, "CCCCCCCCCCC=C=Cc1ccccc1"),
    (6, "1b", "2b", 8.5, 53, "3bb", 3, 130, False, "CCCCCCCCCCC=C=Cc1ccc(Cl)cc1"),
    (7, "1b", "2c", 8.5, 55, "3bc", 3, 130, False, "CCCCCCCCCCC=C=Cc1ccc(Br)cc1"),
    (8, "1b", "2e", 9.0, 58, "3be", 3, 130, False, "CCCCCCCCCCC=C=Cc1ccc(C(F)(F)F)cc1"),
    (9, "1c", "2a", 9.2, 51, "3ca", 5, 130, False, None),
    (10, "1d", "2f", 22.0, 56, "3df", 5, 130, True, None),
    (11, "1d", "2g", 6.0, 42, "3dg", 5, 150, True, None),
]
t2_ids = []
for entry, alkyne_code, aldehyde_code, hours, reported_yield, product_code, volume, temperature, sealed, product_smiles in table2:
    al_label, al_name, al_smiles = alkynes[alkyne_code]
    ad_label, ad_name, ad_smiles = aldehydes[aldehyde_code]
    product_id = f"product_{product_code}"
    ps = [
        participant("alkyne", "reactant", al_label, EV1, name=al_name, smiles=al_smiles, amounts=[amount("reaction_scale", 1.0, "mmol", EV1)]),
        participant("aldehyde", "reactant", ad_label, EV1, name=ad_name, smiles=ad_smiles, amounts=[amount("equivalents", 1.8, "equiv", EV1)]),
        participant("morpholine", "reagent", "morpholine", EV1, name="morpholine", smiles="C1COCCN1", amounts=[amount("equivalents", 1.4, "equiv", EV1)]),
        participant("zni2", "reagent", "ZnI2", EV1, name="zinc iodide", smiles="[I-].[I-].[Zn+2]", amounts=[amount("equivalents", 0.8, "equiv", EV1)]),
        participant("toluene", "solvent", "toluene", EV1, name="toluene", smiles="Cc1ccccc1", amounts=[amount("volume", volume, "mL", EV1)]),
        participant(product_id, "product", product_code, EV1, name=f"allene {product_code}", smiles=product_smiles),
    ]
    conditions = [
        field("temperature", {"number": temperature, "unit": "°C"}, EV1),
        field("time", {"number": hours, "unit": "h"}, EV1),
    ]
    if sealed:
        conditions.append(field("operation", "reaction tube sealed with a screw cap", EV1))
    basis = "isolated" if entry == 1 else None
    unresolved = missing_operations([] if basis else ["Table 2 does not state the yield measurement basis for this row."])
    if product_smiles is None:
        unresolved.append("The R-group-defined substrate/product structure was retained by label and not encoded as a complete SMILES candidate.")
    source_id = f"table2_entry{entry}_{product_code}"
    t2_ids.append(f"{DOC}:{source_id}")
    notes = []
    if entry == 1:
        notes.append("This row is the same 5 mL/65% isolated point reported in the prose concentration series; it is represented once.")
    records.append(record(
        source_id, "substrate_scope_entry", EV1, ps,
        [{"step_id": "one_pot_allene_formation", "participant_ids": [p["entity_id"] for p in ps if p["role"] != "product"], "conditions": conditions}],
        [
            field(f"reported_yield_{product_code}", {"number": reported_yield, "unit": "%"}, EV1, [product_id]),
            field("yield_measurement_basis", basis, EV1, [product_id]),
        ],
        notes=notes,
        unresolved=unresolved,
    ))

# Scheme 1, top: three propargylic alcohol rows.
alcohol_rows = [
    ("4a", "n-C7H15 (4a)", "1-decyn-3-ol", "C#CC(O)CCCCCCC", 7.8, 62, "5a", "CCCCCCCC(O)C=C=Cc1ccccc1"),
    ("4b", "n-C5H11 (4b)", "1-octyn-3-ol", "C#CC(O)CCCCC", 7.8, 56, "5b", "CCCCCC(O)C=C=Cc1ccccc1"),
    ("4c", "n-C9H19 (4c)", "1-dodecyn-3-ol", "C#CC(O)CCCCCCCCC", 8.2, 52, "5c", "CCCCCCCCCC(O)C=C=Cc1ccccc1"),
]
scheme1_ids = []
for substrate_code, label, name, smiles, hours, isolated_yield, product_code, product_smiles in alcohol_rows:
    product_id = f"product_{product_code}"
    ps = [
        participant("propargylic_alcohol", "reactant", label, EV12, name=name, smiles=smiles, amounts=[amount("concentration", 0.125, "M", EV12)]),
        participant("benzaldehyde", "reactant", "PhCHO (2a)", EV12, name="benzaldehyde", smiles="O=Cc1ccccc1", amounts=[amount("equivalents", 1.8, "equiv", EV12)]),
        participant("morpholine", "reagent", "morpholine", EV12, name="morpholine", smiles="C1COCCN1", amounts=[amount("equivalents", 1.4, "equiv", EV12)]),
        participant("zni2", "reagent", "ZnI2", EV12, name="zinc iodide", smiles="[I-].[I-].[Zn+2]", amounts=[amount("equivalents", 0.8, "equiv", EV12)]),
        participant("toluene", "solvent", "toluene", EV12, name="toluene", smiles="Cc1ccccc1"),
        participant(product_id, "product", product_code, EV12, name=f"2,3-allenol {product_code}", smiles=product_smiles),
    ]
    source_id = f"scheme1_{substrate_code}_to_{product_code}"
    scheme1_ids.append(f"{DOC}:{source_id}")
    records.append(record(
        source_id, "substrate_scope_entry", EV12, ps,
        [{"step_id": "one_pot_allenol_formation", "participant_ids": [p["entity_id"] for p in ps if p["role"] != "product"], "conditions": [
            field("temperature", {"number": 130, "unit": "°C"}, EV12),
            field("time", {"number": hours, "unit": "h"}, EV12),
        ]}],
        [
            field(f"isolated_yield_{product_code}", {"number": isolated_yield, "unit": "%"}, EV12, [product_id]),
            field("yield_measurement_basis", "isolated", EV12, [product_id]),
            field("diastereomer_ratio", "approximately 1:1", EV12, [product_id]),
        ],
        unresolved=missing_operations(["Relative configurations of the approximately 1:1 diastereomer mixture are not assigned."]),
    ))

# Scheme 1, bottom: two propargylic tosylamide rows.
tosylamide_smiles = "C#CC(NS(=O)(=O)c1ccc(C)cc1)CCCCCCC"
tosylamide_rows = [
    ("2a", "PhCHO (2a)", "benzaldehyde", "O=Cc1ccccc1", 130, 6.4, 59, "7a", "CCCCCCCC(NS(=O)(=O)c1ccc(C)cc1)C=C=Cc1ccccc1", False),
    ("2f", "i-PrCHO (2f)", "2-methylpropanal", "CC(C)C=O", 150, 9.6, 49, "7f", "CCCCCCCC(NS(=O)(=O)c1ccc(C)cc1)C=C=CC(C)C", True),
]
for aldehyde_code, aldehyde_label, aldehyde_name, aldehyde_smiles, temperature, hours, isolated_yield, product_code, product_smiles, sealed in tosylamide_rows:
    product_id = f"product_{product_code}"
    ps = [
        participant("tosylamide_6", "reactant", "6", EV12, name="terminal propargylic tosylamide 6", smiles=tosylamide_smiles, amounts=[amount("concentration", 0.33, "M", EV12)]),
        participant("aldehyde", "reactant", aldehyde_label, EV12, name=aldehyde_name, smiles=aldehyde_smiles, amounts=[amount("equivalents", 1.8, "equiv", EV12)]),
        participant("morpholine", "reagent", "morpholine", EV12, name="morpholine", smiles="C1COCCN1", amounts=[amount("equivalents", 1.4, "equiv", EV12)]),
        participant("zni2", "reagent", "ZnI2", EV12, name="zinc iodide", smiles="[I-].[I-].[Zn+2]", amounts=[amount("equivalents", 0.8, "equiv", EV12)]),
        participant("toluene", "solvent", "toluene", EV12, name="toluene", smiles="Cc1ccccc1"),
        participant(product_id, "product", product_code, EV12, name=f"2,3-allenyl tosylamide {product_code}", smiles=product_smiles),
    ]
    conditions = [field("temperature", {"number": temperature, "unit": "°C"}, EV12), field("time", {"number": hours, "unit": "h"}, EV12)]
    if sealed:
        conditions.append(field("operation", "reaction tube sealed with a screw cap", EV12))
    source_id = f"scheme1_6_{aldehyde_code}_to_{product_code}"
    scheme1_ids.append(f"{DOC}:{source_id}")
    records.append(record(
        source_id, "substrate_scope_entry", EV12, ps,
        [{"step_id": "one_pot_allenyl_tosylamide_formation", "participant_ids": [p["entity_id"] for p in ps if p["role"] != "product"], "conditions": conditions}],
        [
            field(f"isolated_yield_{product_code}", {"number": isolated_yield, "unit": "%"}, EV12, [product_id]),
            field("yield_measurement_basis", "isolated", EV12, [product_id]),
            field("diastereomer_ratio", "approximately 1:1", EV12, [product_id]),
        ],
        unresolved=missing_operations(["Relative configurations of the approximately 1:1 diastereomer mixture are not assigned."]),
    ))

# Formation of the isolated/observed propargylic amine used in eq 1.
amine_smiles = "CCCCCCCCC#CC(c1ccc(Cl)cc1)N1CCOCC1"
ps = [
    participant("alkyne_1a", "reactant", "1a", EV2, name="1-decyne", smiles="CCCCCCCCC#C"),
    participant("aldehyde_2b", "reactant", "p-chlorobenzaldehyde (2b)", EV2, name="4-chlorobenzaldehyde", smiles="O=Cc1ccc(Cl)cc1"),
    participant("morpholine", "reactant", "morpholine", EV2, name="morpholine", smiles="C1COCCN1"),
    participant("product_8ab", "product", "8ab", EV2, name="propargylic amine 8ab", smiles=amine_smiles),
]
records.append(record(
    "prose_formation_8ab", "reported_experiment", EV2, ps,
    [{"step_id": "formation_of_8ab", "participant_ids": ["alkyne_1a", "aldehyde_2b", "morpholine"], "conditions": [
        field("temperature", None, []), field("time", None, []),
    ]}],
    [field("product_observation", "8ab was formed", EV2, ["product_8ab"]), field("yield_measurement_basis", None, [], ["product_8ab"])],
    unresolved=missing_operations(["The main text gives no amounts, time, temperature, or yield for formation of 8ab."]),
))

# Equation 1: two ZnI2 loading/water conditions and one catalyst-omission control.
eq_rows = [
    ("eq1_zni2_0p8eq", 0.8, None, 9.0, 46, "NMR"),
    ("eq1_zni2_1p4eq_water", 1.4, 2.0, 3.0, 72, "NMR"),
]
eq_ids = []
for source_id, zni2_equiv, water_equiv, hours, reported_yield, basis in eq_rows:
    ps = [
        participant("amine_8ab", "reactant", "8ab", EV2, name="propargylic amine 8ab", smiles=amine_smiles, amounts=[amount("reaction_scale", 0.3, "mmol", EV2)]),
        participant("zni2", "reagent", "ZnI2", EV2, name="zinc iodide", smiles="[I-].[I-].[Zn+2]", amounts=[amount("equivalents", zni2_equiv, "equiv", EV2)]),
        participant("toluene", "solvent", "toluene", EV2, name="toluene", smiles="Cc1ccccc1", amounts=[amount("volume", 0.5, "mL", EV2)]),
        participant("product_3ab", "product", "3ab", EV2, name="allene 3ab", smiles="CCCCCCCCC=C=Cc1ccc(Cl)cc1"),
    ]
    if water_equiv is not None:
        ps.insert(2, participant("water", "reagent", "H2O", EV2, name="water", smiles="O", amounts=[amount("equivalents", water_equiv, "equiv", EV2)]))
    eq_ids.append(f"{DOC}:{source_id}")
    records.append(record(
        source_id, "optimization_entry", EV2, ps,
        [{"step_id": "conversion_of_8ab_to_3ab", "participant_ids": [p["entity_id"] for p in ps if p["role"] != "product"], "conditions": [
            field("temperature", {"number": 130, "unit": "°C"}, EV2),
            field("time", {"number": hours, "unit": "h"}, EV2),
        ]}],
        [
            field("reported_yield_3ab", {"number": reported_yield, "unit": "%"}, EV2, ["product_3ab"]),
            field("yield_measurement_basis", basis, EV2, ["product_3ab"]),
        ],
        unresolved=missing_operations(),
    ))

source_id = "eq1_no_zni2_control"
eq_ids.append(f"{DOC}:{source_id}")
ps = [
    participant("amine_8ab", "reactant", "8ab", EV2, name="propargylic amine 8ab", smiles=amine_smiles, amounts=[amount("reaction_scale", 0.3, "mmol", EV2)]),
    participant("toluene", "solvent", "toluene", EV2, name="toluene", smiles="Cc1ccccc1", amounts=[amount("volume", 0.5, "mL", EV2)]),
    participant("product_3ab", "product", "3ab", EV2, name="allene 3ab", smiles="CCCCCCCCC=C=Cc1ccc(Cl)cc1"),
]
records.append(record(
    source_id, "optimization_entry", EV2, ps,
    [{"step_id": "zni2_omission_control", "participant_ids": ["amine_8ab", "toluene"], "conditions": [
        field("temperature", {"number": 130, "unit": "°C"}, EV2), field("time", None, []),
    ]}],
    [field("reaction_result", "no reaction observed", EV2, ["product_3ab"])],
    notes=["ZnI2 is intentionally absent in this control."],
    unresolved=missing_operations(["The duration and numeric yield of the no-ZnI2 control are not stated; no zero yield was inferred."]),
))

# Scheme 2 is a proposed mechanism, not an isolated experimental sequence.
mechanism_participants = [
    participant("terminal_alkyne", "reactant", "R1-CCH", EV2, name="generic terminal alkyne", smiles=None),
    participant("zni2", "reagent", "ZnI2", EV2, name="zinc iodide", smiles="[I-].[I-].[Zn+2]"),
    participant("morpholine", "reagent", "morpholine", EV2, name="morpholine", smiles="C1COCCN1"),
    participant("aldehyde", "reactant", "R2CHO", EV2, name="generic aldehyde", smiles=None),
    participant("species_9", "unspecified_agent", "9", EV2, name="1-alkynyl zinc species 9", smiles=None),
    participant("species_10", "unspecified_agent", "10", EV2, name="iminium ion 10", smiles=None),
    participant("species_8", "unspecified_agent", "8", EV2, name="propargylic amine intermediate 8", smiles=None),
    participant("species_11", "unspecified_agent", "11", EV2, name="ZnI2-coordinated complex 11", smiles=None),
    participant("species_12", "unspecified_agent", "12", EV2, name="1,5-hydride-transfer intermediate 12", smiles=None),
    participant("allene_product", "product", "allene product", EV2, name="generic 1,3-disubstituted allene", smiles=None),
]
mechanism_id = f"{DOC}:scheme2_proposed_mechanism"
records.append(record(
    "scheme2_proposed_mechanism", "mechanism", EV2, mechanism_participants,
    [
        {"step_id": "proposed_alkynylzinc_formation", "participant_ids": ["terminal_alkyne", "zni2", "species_9"], "conditions": [field("operation", "proposed formation of 1-alkynyl zinc species 9", EV2)]},
        {"step_id": "proposed_propargylic_amine_formation", "participant_ids": ["species_9", "species_10", "species_8"], "conditions": [field("operation", "proposed addition to iminium ion 10 with regeneration of ZnI2", EV2)]},
        {"step_id": "proposed_rearrangement", "participant_ids": ["species_8", "zni2", "species_11", "species_12", "allene_product"], "conditions": [field("operation", "proposed ZnI2 coordination, 1,5-hydride transfer, and beta-elimination", EV2)]},
    ],
    [],
    notes=["The authors explicitly describe Scheme 2 as a proposed mechanistic framework requiring further study."],
    unresolved=["This mechanism is proposed rather than experimentally established; generic R-group structures are not encoded as complete SMILES."],
))

assert len(records) == 37, len(records)
assert len({r["record_id"] for r in records}) == len(records)

records_path = OUT / "records_pages_0001_0002.json"
records_path.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")

table1_ids = [f"{DOC}:table1_entry{i}" for i in range(1, 7)]
prose_screen_ids = [
    f"{DOC}:prose_znotf2_screen",
    *[f"{DOC}:prose_solvent_{x}" for x in ["meno2", "chcl3", "dce", "mecn"]],
    f"{DOC}:prose_piperidine_less_effective",
    f"{DOC}:prose_table_s3_entry7",
    *[f"{DOC}:prose_concentration_{x}ml" for x in [1, 3, 7]],
]
page1_ids = table1_ids + prose_screen_ids + t2_ids + scheme1_ids
page2_ids = scheme1_ids + [f"{DOC}:prose_formation_8ab"] + eq_ids + [mechanism_id]

coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1,
            "state": "attempted",
            "regions": [
                {
                    "region": "title and upper-column introduction/prior-work discussion",
                    "finding": "The article identity and cited Crabbe, CuI/paraformaldehyde, gold/enamine, and propargylic-amine methods were inspected as background literature; they were not converted into experiments of this paper.",
                    "evidence_ids": [P1I, P1T],
                },
                {
                    "region": "lower-left Table 1 reaction drawing, six catalyst rows, footnotes, and adjacent Zn(OTf)2 prose",
                    "finding": "Six independent catalyst-screen rows and the separate prose Zn(OTf)2 experiment were extracted with shared scale, equivalents, solvent volume, 150 °C sealed operation, row times, yields, and isolated/NMR bases where stated.",
                    "evidence_ids": [P1I, P1T],
                },
                {
                    "region": "middle-right optimization prose above Table 2",
                    "finding": "Four explicit no-product solvent screens, the qualitative piperidine comparison, prose-described Table S3 entry 7, and the 1/3/5/7 mL concentration series were inspected. The 5 mL/65% point is merged with Table 2 entry 1; unavailable Tables S1-S3 leave unstated row details missing.",
                    "evidence_ids": [P1I, P1T],
                },
                {
                    "region": "lower-right Table 2 reaction drawing, entries 1-11, and footnotes",
                    "finding": "All eleven substrate-scope rows were extracted independently, including 3 versus 5 mL footnotes, sealed-tube overrides, the 150 °C override, and image-verified entry 10 values of 22 h and 56%.",
                    "evidence_ids": [P1I, P1T],
                },
                {
                    "region": "bottom-right prose leading into cross-page Scheme 1",
                    "finding": "The 2,3-allenol/tosylamide scope statement, isolated-yield basis, and approximately 1:1 diastereomer statement were linked to the five Scheme 1 rows completed on page 2.",
                    "evidence_ids": [P1I, P1T, P2I, P2T],
                },
            ],
            "record_ids": page1_ids,
            "unresolved": [
                "Tables S1-S3 and the advertised Supporting Information were not supplied or explicitly associated; omitted numeric results and operational details for the prose-described comparisons were not inferred.",
                "Table 2 does not state yield basis for entries 2-11, and complex R-group structures 1c/1d and products 3ca/3df/3dg remain label-only/unverified.",
            ],
        },
        {
            "page": 2,
            "state": "attempted",
            "regions": [
                {
                    "region": "upper-left Scheme 1 and its continuation prose",
                    "finding": "Three propargylic-alcohol and two propargylic-tosylamide experiments were extracted row by row with concentrations/equivalents, temperatures, times, isolated yields, sealed-tube override, and approximate diastereomer ratio.",
                    "evidence_ids": [P2I, P2T, P1I, P1T],
                },
                {
                    "region": "middle-left propargylic amine 8ab paragraph and equation 1",
                    "finding": "Formation of 8ab was retained as a partial reported experiment; equation 1 was separated into the 0.8-equiv ZnI2 row, the 1.4-equiv ZnI2 plus 2-equiv water row, and the no-ZnI2 qualitative control.",
                    "evidence_ids": [P2I, P2T],
                },
                {
                    "region": "lower-left Scheme 2 and adjacent mechanistic prose",
                    "finding": "The 1-alkynyl zinc/iminium/propargylic amine/1,5-hydride-transfer pathway was classified as one proposed mechanism, not as isolated experimental batches.",
                    "evidence_ids": [P2I, P2T],
                },
                {
                    "region": "upper-right conclusion, Supporting Information notice, acknowledgments, and references",
                    "finding": "No additional current-paper experiment was identified. The notice says SI exists online but no SI file was supplied, so association remains unestablished; references remain background literature.",
                    "evidence_ids": [P2I, P2T],
                },
            ],
            "record_ids": page2_ids,
            "unresolved": [
                "Formation of 8ab lacks quantities, time, temperature, and yield; the no-ZnI2 control lacks a duration and numeric outcome.",
                "Scheme 2 is explicitly tentative, and all generic mechanistic intermediates remain unverified label-only structures.",
            ],
        },
    ],
}
coverage_path = ROOT / "runs/current/coverage/pages_0001_0002.json"
coverage_path.parent.mkdir(parents=True, exist_ok=True)
coverage_path.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

tasks_path = ROOT / "runs/current/tasks.json"
tasks = json.loads(tasks_path.read_text())
for task in tasks:
    if task["document_id"] == DOC and task["task_id"] in {P1T, P2T}:
        task["state"] = "attempted"
        task["visual_evidence_id"] = P1I if task["task_id"] == P1T else P2I
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"records": len(records), "records_path": str(records_path), "coverage_path": str(coverage_path)}, ensure_ascii=False))
