import json
from pathlib import Path

DOC = "doc_522a44a8ca0b8f55"
P1T, P1I = f"{DOC}:page1:text", f"{DOC}:page1:image"
P2T, P2I = f"{DOC}:page2:text", f"{DOC}:page2:image"
P3T, P3I = f"{DOC}:page3:text", f"{DOC}:page3:image"


def fact(value, evidence):
    return {
        "value": value,
        "evidence_ids": list(evidence) if value is not None else [],
        "verification": "source_checked" if value is not None else "missing",
    }


def field(name, value, evidence, target=None):
    result = {"name": name, "fact": fact(value, evidence)}
    if target:
        result["target_entity_ids"] = list(target)
    return result


def participant(entity_id, role, evidence, label=None, name=None, smiles=None, amounts=None):
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


def record(suffix, kind, evidence, participants, steps, outcomes=None, notes=None, unresolved=None):
    return {
        "record_id": f"{DOC}:{suffix}",
        "document_id": DOC,
        "source_reaction_id": suffix,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": list(evidence),
        "participants": participants,
        "steps": steps,
        "outcomes": outcomes or [],
        "notes": [fact(x, evidence) for x in (notes or [])],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved or [],
        },
    }


records = []

# Page 1: the abstract graphic is a general transformation, not an individual experiment.
ev = [P1I, P1T]
generic_parts = [
    participant("generic_allenyl_ketone", "reactant", ev, name="1,2-allenyl ketone"),
    participant("generic_ewg_acetate", "reactant", ev, name="electron-withdrawing-group-substituted acetate"),
    participant("generic_base", "unspecified_agent", ev, name="base"),
    participant("generic_alpha_pyrone", "product", ev, name="α-pyrone derivative"),
]
records.append(record(
    "abstract_general_transformation", "general_scheme", ev, generic_parts,
    [{"step_id": "generic_michael_addition_lactonization", "participant_ids": [p["entity_id"] for p in generic_parts],
      "conditions": [field("operation", "base-catalyzed or base-promoted Michael addition–C–C double-bond migration–lactonization", ev)]}],
    notes=["Abstract-level general reaction; no individual substrate, base identity, temperature, time, or yield is specified."],
    unresolved=["Generic R groups and EWG are not fully specified, so no SMILES are assigned.", "This is not counted as a reported individual experiment."],
))

# Page 2 Scheme 1: mechanistic proposal, represented as stages rather than reported experiments.
ev = [P2I, P2T]
mech_parts = [
    participant("scheme1_allenyl_ketone_1", "reactant", ev, label="1", name="generic 1,2-allenyl ketone 1"),
    participant("scheme1_carbanion_2", "reactant", ev, label="2", name="anion of CH(COOR)(EWG)"),
    participant("scheme1_intermediate_4", "unspecified_agent", ev, label="4", name="Michael-addition intermediate 4"),
    participant("scheme1_intermediate_5", "unspecified_agent", ev, label="5", name="double-bond-migrated intermediate 5"),
    participant("scheme1_intermediate_6", "unspecified_agent", ev, label="6", name="alternative double-bond-migrated intermediate 6"),
    participant("scheme1_product_3", "product", ev, label="3", name="generic α-pyrone 3"),
]
records.append(record(
    "scheme1_proposed_mechanism", "mechanism", ev, mech_parts,
    [
        {"step_id": "michael_addition", "participant_ids": ["scheme1_allenyl_ketone_1", "scheme1_carbanion_2", "scheme1_intermediate_4"], "conditions": []},
        {"step_id": "double_bond_migration", "participant_ids": ["scheme1_intermediate_4", "scheme1_intermediate_5", "scheme1_intermediate_6"], "conditions": []},
        {"step_id": "lactonization", "participant_ids": ["scheme1_intermediate_5", "scheme1_product_3"], "conditions": [field("operation", "loss of ROH", ev)]},
    ],
    notes=["Scheme 1 is presented as the believed reaction pathway; intermediate 4 may migrate to 5 or 6 before selective lactonization."],
    unresolved=["The scheme is mechanistic and does not report isolated intermediates or experimental conditions.", "Generic R groups and EWG prevent unique structures."],
))


def table1_record(entry, equiv, solvent, temp, time_h, yield_pct):
    ev = [P2I, P2T] + ([P3I, P3T] if entry == 4 else [])
    amounts_1a = []
    amounts_malonate = []
    amounts_base = [field("equivalents", {"number": equiv, "unit": "equiv"}, [P2I, P2T])]
    amounts_solvent = []
    amounts_product = []
    if entry == 4:
        amounts_1a = [field("mass", {"number": 166, "unit": "mg"}, [P3I, P3T]), field("amount", {"number": 1.2, "unit": "mmol"}, [P3I, P3T])]
        amounts_malonate = [field("mass", {"number": 160, "unit": "mg"}, [P3I, P3T]), field("amount", {"number": 1.0, "unit": "mmol"}, [P3I, P3T])]
        amounts_base += [field("mass", {"number": 14, "unit": "mg"}, [P3I, P3T]), field("catalyst_loading", {"number": 10, "unit": "mol%"}, [P3I, P3T])]
        amounts_solvent = [field("volume", {"number": 1, "unit": "mL"}, [P3I, P3T])]
        amounts_product = [field("mass", {"number": 199, "unit": "mg"}, [P3I, P3T])]
    parts = [
        participant("t1_1a", "reactant", ev, label="1a", name="1,2-nonadien-4-one", smiles="C=C=CC(=O)CCCCC", amounts=amounts_1a),
        participant("t1_diethyl_malonate", "reactant", ev, name="diethyl malonate", smiles="CCOC(=O)CC(=O)OCC", amounts=amounts_malonate),
        participant("t1_k2co3", "reagent", ev, name="potassium carbonate", smiles="[K+].[K+].[O-]C([O-])=O", amounts=amounts_base),
        participant("t1_solvent", "solvent", ev, name=solvent, smiles={"DMF": "CN(C)C=O", "acetone": "CC(=O)C"}[solvent], amounts=amounts_solvent),
        participant("t1_3a", "product", ev, label="3a", name="α-pyrone product 3a", smiles="CCOC(=O)C1=C(C)C=C(CCCCC)OC1=O", amounts=amounts_product),
    ]
    conditions = [field("solvent", solvent, [P2I, P2T]), field("temperature", temp, [P2I, P2T]), field("time", {"number": time_h, "unit": "h"}, [P2I, P2T])]
    steps = [{"step_id": "reaction", "participant_ids": ["t1_1a", "t1_diethyl_malonate", "t1_k2co3", "t1_solvent"], "conditions": conditions}]
    if entry == 4:
        steps += [
            {"step_id": "monitoring_and_evaporation", "participant_ids": ["t1_1a", "t1_diethyl_malonate", "t1_k2co3", "t1_solvent"], "conditions": [field("operation", "reaction monitored by TLC (6:1 hexane/ethyl acetate) until complete; solvent evaporated", [P3I, P3T])]},
            {"step_id": "purification", "participant_ids": ["t1_3a"], "conditions": [field("purification", "silica gel chromatography (6:1 hexane/ethyl acetate)", [P3I, P3T])]},
        ]
    return record(
        f"table1_entry{entry}", "optimization_entry", ev, parts, steps,
        outcomes=[field("yield", {"number": yield_pct, "unit": "%"}, [P2I, P2T] + ([P3I, P3T] if entry == 4 else []), target=["t1_3a"]), field("yield_measurement_basis", None, [])],
        notes=[f"Table 1 entry {entry}; entry 4 is cross-linked to the typical procedure in footnote 12." if entry == 4 else f"Table 1 entry {entry}."],
        unresolved=["Yield measurement basis is not explicitly named.", "Atmosphere is not reported.", "The candidate SMILES were transcribed from the displayed structures and remain unverified.", "Supporting information was mentioned but not supplied or associated."],
    )


for row in [
    (1, 0.5, "DMF", {"number": 50, "unit": "°C"}, 13, 31),
    (2, 1.0, "DMF", {"number": 80, "unit": "°C"}, 3, 31),
    (3, 1.0, "acetone", "reflux", 12, 67),
    (4, 0.1, "acetone", "reflux", 20, 79),
]:
    records.append(table1_record(*row))


table2_rows = [
    (1, "H", "H", "H", "Me", "1b", "EtOH", {"number": 60, "unit": "°C"}, 1.5, 74, "3b", False),
    (2, "H", "H", "H", "Ph", "1c", "acetone", "reflux", 4, 71, "3c", False),
    (3, "H", "H", "H", "Ph", "1c", "EtOH", "reflux", 1.5, 56, "3c", False),
    (4, "H", "H", "H", "Bn", "1d", "CH2Cl2", "reflux", 40, 69, "3d", False),
    (5, "H", "H", "C4H9", "Me", "1e", "acetone", "reflux", 48, 64, "3e", False),
    (6, "H", "H", "C4H9", "Me", "1e", "DMF", {"number": 80, "unit": "°C"}, 7, 55, "3e", True),
    (7, "H", "H", "C2H5", "Me", "1f", "EtOH", "reflux", 12, 53, "3f", False),
    (8, "H", "H", "C2H5", "Me", "1f", "DMF", {"number": 80, "unit": "°C"}, 12, 50, "3f", False),
    (9, "H", "H", "C2H5", "Me", "1f", "acetone", "reflux", 20, 33, "3f", False),
    (10, "H", "H", "Bn", "Me", "1g", "acetone", "reflux", 21, 92, "3g", False),
    (11, "H", "H", "Bn", "Me", "1g", "DMF", {"number": 60, "unit": "°C"}, 2.5, 90, "3g", False),
    (12, "H", "H", "allyl", "Me", "1h", "EtOH", "reflux", 15, 54, "3h", False),
    (13, "H", "H", "allyl", "Me", "1h", "acetone", "reflux", 20, 90, "3h", False),
    (14, "H", "C4H9", "H", "Me", "1i", "EtOH", {"number": 80, "unit": "°C"}, 7, 38, "3i", False),
    (15, "H", "C4H9", "H", "Me", "1i", "DMF", {"number": 80, "unit": "°C"}, 13, 54, "3i", False),
]
solvent_smiles = {"EtOH": "CCO", "acetone": "CC(=O)C", "DMF": "CN(C)C=O", "CH2Cl2": "ClCCl"}
for entry, r1, r2, r3, r4, substrate, solvent, temp, time_h, yield_pct, product, one_equiv in table2_rows:
    ev = [P2I, P2T]
    loading = {"number": 1, "unit": "equiv"} if one_equiv else {"number": 10, "unit": "mol%"}
    parts = [
        participant("t2_allenyl_ketone", "reactant", ev, label=substrate, name=f"1,2-allenyl ketone {substrate} (R1={r1}, R2={r2}, R3={r3}, R4={r4})"),
        participant("t2_diethyl_malonate", "reactant", ev, name="diethyl malonate", smiles="CCOC(=O)CC(=O)OCC"),
        participant("t2_k2co3", "reagent", ev, name="potassium carbonate", smiles="[K+].[K+].[O-]C([O-])=O", amounts=[field("loading", loading, ev)]),
        participant("t2_solvent", "solvent", ev, name=solvent, smiles=solvent_smiles[solvent]),
        participant("t2_product", "product", ev, label=product, name=f"α-pyrone product {product}"),
    ]
    records.append(record(
        f"table2_entry{entry}", "substrate_scope_entry", ev, parts,
        [{"step_id": "reaction", "participant_ids": ["t2_allenyl_ketone", "t2_diethyl_malonate", "t2_k2co3", "t2_solvent"], "conditions": [field("solvent", solvent, ev), field("temperature", temp, ev), field("time", {"number": time_h, "unit": "h"}, ev)]}],
        outcomes=[field("yield", {"number": yield_pct, "unit": "%"}, ev, target=["t2_product"]), field("yield_measurement_basis", None, [])],
        notes=[{"table": 2, "entry": entry, "R1": r1, "R2": r2, "R3": r3, "R4": r4}, "Entry 6 footnote overrides the 10 mol% scheme loading with one equivalent of K2CO3." if one_equiv else "K2CO3 loading is the 10 mol% value printed above the Table 2 reaction arrow."],
        unresolved=["Starting-material and product SMILES are left null because their structures require reconstruction from a generic R-group scheme.", "Yield measurement basis, atmosphere, workup, and purification are not reported in the table.", "Supporting information was mentioned but not supplied or associated."],
    ))


table3_rows = [
    (1, "CH2(CO2Me)2", "dimethyl malonate", "COC(=O)CC(=O)OC", "K2CO3", {"number": 80, "unit": "°C"}, {"number": 4, "unit": "h"}, 88, "3j", "COC(=O)C1=C(C)C(CCCC)=C(C)OC1=O"),
    (2, "CH2(CO2Me)2", "dimethyl malonate", "COC(=O)CC(=O)OC", "NaH", "rt", {"number": 5, "unit": "d"}, 87, "3j", "COC(=O)C1=C(C)C(CCCC)=C(C)OC1=O"),
    (3, "CH2(CO2Me)2", "dimethyl malonate", "COC(=O)CC(=O)OC", "NaH", {"number": 80, "unit": "°C"}, {"number": 4, "unit": "h"}, 88, "3j", "COC(=O)C1=C(C)C(CCCC)=C(C)OC1=O"),
    (4, "CH2(CO2Me)2", "dimethyl malonate", "COC(=O)CC(=O)OC", "NaOH", {"number": 80, "unit": "°C"}, {"number": 1, "unit": "h"}, 87, "3j", "COC(=O)C1=C(C)C(CCCC)=C(C)OC1=O"),
    (5, "CH2(CN)(CO2Et)", "ethyl cyanoacetate", "CCOC(=O)CC#N", "NaH", {"number": 50, "unit": "°C"}, {"number": 3, "unit": "h"}, 69, "3k", "N#CC1=C(C)C(CCCC)=C(C)OC1=O"),
    (6, "CH2(CN)(CO2Et)", "ethyl cyanoacetate", "CCOC(=O)CC#N", "NaH", {"number": 80, "unit": "°C"}, {"number": 4, "unit": "h"}, 39, "3k", "N#CC1=C(C)C(CCCC)=C(C)OC1=O"),
    (7, "CH2(CN)(CO2Et)", "ethyl cyanoacetate", "CCOC(=O)CC#N", "NaOAc", {"number": 50, "unit": "°C"}, {"number": 7, "unit": "h"}, 61, "3k", "N#CC1=C(C)C(CCCC)=C(C)OC1=O"),
    (8, "CH2(CN)(CO2Et)", "ethyl cyanoacetate", "CCOC(=O)CC#N", "K2CO3", {"number": 50, "unit": "°C"}, {"number": 2, "unit": "h"}, 60, "3k", "N#CC1=C(C)C(CCCC)=C(C)OC1=O"),
    (9, "CH2(COMe)(CO2Me)", "methyl acetoacetate", "COC(=O)CC(=O)C", "NaH", {"number": 80, "unit": "°C"}, {"number": 23, "unit": "h"}, 38, "3l", "CC(=O)C1=C(C)C(CCCC)=C(C)OC1=O"),
]
base_info = {
    "K2CO3": ("potassium carbonate", "[K+].[K+].[O-]C([O-])=O"),
    "NaH": ("sodium hydride", "[Na+].[H-]"),
    "NaOH": ("sodium hydroxide", "[Na+].[OH-]"),
    "NaOAc": ("sodium acetate", "[Na+].CC(=O)[O-]"),
}
for entry, reagent_label, reagent_name, reagent_smiles, base, temp, duration, yield_pct, product, product_smiles in table3_rows:
    ev = [P3I, P3T]
    base_name, base_smiles = base_info[base]
    parts = [
        participant("t3_1e", "reactant", ev, label="1e", name="1,2-dienyl ketone 1e", smiles="C=C=C(CCCC)C(=O)C"),
        participant("t3_active_methylene", "reactant", ev, label=reagent_label, name=reagent_name, smiles=reagent_smiles),
        participant("t3_base", "reagent", ev, label=base, name=base_name, smiles=base_smiles, amounts=[field("reported_base_loading", {"number": 10, "unit": "%", "raw_text": "10% base"}, ev)]),
        participant("t3_dmf", "solvent", ev, name="DMF", smiles="CN(C)C=O"),
        participant("t3_product", "product", ev, label=product, name=f"α-pyrone product {product}", smiles=product_smiles),
    ]
    records.append(record(
        f"table3_entry{entry}", "optimization_entry", ev, parts,
        [{"step_id": "reaction", "participant_ids": ["t3_1e", "t3_active_methylene", "t3_base", "t3_dmf"], "conditions": [field("solvent", "DMF", ev), field("temperature", temp, ev), field("time", duration, ev)]}],
        outcomes=[field("yield", {"number": yield_pct, "unit": "%"}, ev, target=["t3_product"]), field("yield_measurement_basis", None, [])],
        notes=[f"Table 3 entry {entry}; the arrow reports '10% base' without specifying the percentage basis."],
        unresolved=["The reported 10% base loading is preserved as printed; mol% is not inferred.", "Yield measurement basis, atmosphere, workup, and purification are not reported in the table.", "Candidate SMILES transcribed from the displayed structures remain unverified.", "Supporting information was mentioned but not supplied or associated."],
    ))


Path("runs/current/raw_model/records_pages_0001_0003.json").write_text(
    json.dumps(records, ensure_ascii=False, indent=2) + "\n"
)
print(json.dumps({"records": len(records), "path": "runs/current/raw_model/records_pages_0001_0003.json"}))
