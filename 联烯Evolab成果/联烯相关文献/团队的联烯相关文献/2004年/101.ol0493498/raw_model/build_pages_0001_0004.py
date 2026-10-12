#!/usr/bin/env python3
"""Build source-grounded candidate records for ol0493498 PDF pages 1-4."""

import json
from pathlib import Path


DOC = "doc_04da3d0a8abf70e1"
OUT = Path(__file__).with_name("extracted_records_pages_0001_0004.json")
P1I = f"{DOC}:page1:image"
P1T = f"{DOC}:page1:text"
P2I = f"{DOC}:page2:image"
P2T = f"{DOC}:page2:text"
P3I = f"{DOC}:page3:image"
P3T = f"{DOC}:page3:text"
P4I = f"{DOC}:page4:image"
P4T = f"{DOC}:page4:text"


def fact(value, evidence):
    return {
        "value": value,
        "evidence_ids": list(evidence) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def field(name, value, evidence, targets=None):
    result = {"name": name, "fact": fact(value, evidence)}
    if targets:
        result["target_entity_ids"] = targets
    return result


def participant(entity_id, role, label, evidence, name=None, smiles=None, amounts=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence) if name is not None else fact(None, ()),
        "smiles": fact(smiles, evidence) if smiles is not None else fact(None, ()),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": amounts or [],
    }


def step(step_id, participant_ids, conditions):
    return {"step_id": step_id, "participant_ids": participant_ids, "conditions": conditions}


def record(suffix, source_id, kind, evidence, participants, steps, outcomes, notes, unresolved):
    return {
        "record_id": f"{DOC}:{suffix}",
        "document_id": DOC,
        "source_reaction_id": source_id,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": list(dict.fromkeys(evidence)),
        "participants": participants,
        "steps": steps,
        "outcomes": outcomes,
        "notes": [fact(note, evidence) for note in notes],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved,
        },
    }


def amount(name, number, unit, evidence, **extra):
    value = {"number": number, "unit": unit}
    value.update(extra)
    return field(name, value, evidence)


def common_table1_participants(solvents, evidence):
    ev = evidence
    parts = [
        participant("substrate_5a", "reactant", "5a", ev,
                    "ethyl 2-acetylhexa-4,5-dienoate (candidate name)",
                    "CCOC(=O)C(CC=C=C)C(C)=O"),
        participant("dbad_6", "reactant", "6", ev, "dibenzyl azodicarboxylate (DBAD)",
                    "O=C(OCc1ccccc1)N=NC(=O)OCc1ccccc1",
                    [amount("equivalents", 1.2, "equiv", ev)]),
        participant("ph_i_7a", "reactant", "7a", ev, "iodobenzene", "Ic1ccccc1",
                    [amount("equivalents", 1.2, "equiv", ev)]),
        participant("product_1aa_rr", "product", "1aa (3R,5R)", ev,
                    "cis-1aa (3R,5R) as drawn"),
        participant("product_1aa_rs", "product", "1aa (3R,5S)", ev,
                    "trans-1aa (3R,5S) as drawn"),
        participant("ph_box_ss", "catalyst", "Ph-Box (S,S)", ev,
                    "(S,S)-Ph-Box ligand", None,
                    [amount("ligand_equiv_relative_to_Cu", 1.1, "equiv", ev)]),
        participant("cu_otf2", "catalyst", "Cu(OTf)2", ev, "copper(II) triflate", None,
                    [amount("catalyst_loading", 10, "mol%", ev)]),
        participant("k2co3", "reagent", "K2CO3", ev, "potassium carbonate", "[K+].[K+].[O-]C([O-])=O",
                    [amount("equivalents", 2.0, "equiv", ev)]),
        participant("pd_pph3_4", "catalyst", "Pd(PPh3)4", ev, "tetrakis(triphenylphosphine)palladium(0)", None,
                    [amount("catalyst_loading", 5, "mol%", ev)]),
    ]
    solvent_data = {
        "ch2cl2": ("CH2Cl2", "dichloromethane", "ClCCl"),
        "thf": ("THF", "tetrahydrofuran", "C1CCOC1"),
        "dioxane": ("1,4-dioxane", "1,4-dioxane", "O1CCOCC1"),
        "dmso": ("DMSO", "dimethyl sulfoxide", "CS(C)=O"),
        "dmf": ("DMF", "N,N-dimethylformamide", "CN(C)C=O"),
    }
    for key in dict.fromkeys(solvents):
        label, name, smiles = solvent_data[key]
        parts.append(participant(key, "solvent", label, ev, name, smiles))
    return parts


def table1_record(row):
    evidence = [P3I, P3T]
    if row["entry"] == 1:
        evidence = [P2I, P2T, P3I, P3T]
    source_id = f"Table 1 entry {row['entry']}"
    notes = []
    if row["entry"] == 1:
        source_id += "; Scheme 2 (S,S)-Ph-Box row"
        notes.append("Scheme 2 and Table 1 entry 1 report the same (S,S)-Ph-Box experiment and are represented once.")
        notes.append("Page 2 prose explicitly reports solvent removal after the first stage before THF addition.")
    if row["entry"] == 4:
        source_id += "; Table 2 entry 1"
        notes.append("Table 1 entry 4 and Table 2 entry 1 have the same substrates, standard conditions, yield, dr, and ee values and are represented once.")
    if row.get("temp1_note"):
        notes.append(row["temp1_note"])
    participants = common_table1_participants(row["solvent_keys"], evidence)
    step1_conditions = [field("solvent", row["solvent1"], evidence)]
    step1_conditions.append(field("temperature", row.get("temp1"), evidence))
    step1_conditions.append(field("time", {"number": row["time1"], "unit": "h"}, evidence))
    if row["entry"] == 1:
        step1_conditions.append(field("operation", "remove solvent in vacuo after stage 1", [P2I, P2T]))
    step2_conditions = [
        field("solvent", row["solvent2"], evidence),
        field("temperature", row["temp2"], evidence),
        field("time", {"number": 4, "unit": "h"}, evidence),
    ]
    outcomes = [
        field("yield", {"number": row["yield"], "unit": "%"}, evidence,
              ["product_1aa_rr", "product_1aa_rs"]),
        field("yield_measurement_basis", None, ()),
    ]
    if row["yield"] == 0:
        outcomes += [
            field("dr_ratio", None, ()),
            field("reported_dr_ee_cell", "0", evidence,
                  ["product_1aa_rr", "product_1aa_rs"]),
            field("rr_ee", None, ()),
            field("rs_ee", None, ()),
        ]
        notes.append("The combined dr (% ee) cell is printed as 0 at 0% yield; no diastereomer ratio or ee assignment was inferred.")
    else:
        outcomes += [
            field("dr_ratio", row["dr"], evidence, ["product_1aa_rr", "product_1aa_rs"]),
            field("rr_ee", {"number": row["ee_rr"], "unit": "%"}, evidence, ["product_1aa_rr"]),
            field("rs_ee", {"number": row["ee_rs"], "unit": "%"}, evidence, ["product_1aa_rs"]),
        ]
    unresolved = [
        "Final product structures were not transcribed to SMILES and require structure review.",
        "Reaction scale, concentration, atmosphere, workup, purification, and yield measurement basis are absent from the supplied main-text pages.",
        "The paper advertises Supporting Information, but no SI file was supplied or explicitly associated.",
    ]
    return record(
        f"table1_entry{row['entry']:02d}", source_id, "optimization_entry", evidence,
        participants,
        [
            step("stage1_cu_asymmetric_amination",
                 ["substrate_5a", "dbad_6", "ph_box_ss", "cu_otf2"] + row["stage1_solvents"],
                 step1_conditions),
            step("stage2_pd_addition_cyclization",
                 ["ph_i_7a", "k2co3", "pd_pph3_4"] + row["stage2_solvents"],
                 step2_conditions),
        ],
        outcomes, notes, unresolved,
    )


TABLE1 = [
    {"entry": 1, "solvent1": "CH2Cl2", "temp1": {"number": 0, "unit": "°C"}, "time1": 3,
     "solvent2": "THF", "temp2": "reflux", "yield": 92, "dr": "36:64", "ee_rr": 98, "ee_rs": 98,
     "solvent_keys": ["ch2cl2", "thf"], "stage1_solvents": ["ch2cl2"], "stage2_solvents": ["thf"]},
    {"entry": 2, "solvent1": "THF", "temp1": None, "time1": 57,
     "temp1_note": "Stage 1 temperature is printed as 0 °C to r.t.; the mixed numeric/qualitative program is preserved without coercing r.t. to a number.",
     "solvent2": "THF", "temp2": "reflux", "yield": 66, "dr": "48:52", "ee_rr": 99, "ee_rs": 96,
     "solvent_keys": ["thf"], "stage1_solvents": ["thf"], "stage2_solvents": ["thf"]},
    {"entry": 3, "solvent1": "CH2Cl2", "temp1": {"number": 0, "unit": "°C"}, "time1": 3,
     "solvent2": "CH2Cl2/THF (1:2)", "temp2": "reflux", "yield": 92, "dr": "40:60", "ee_rr": 98, "ee_rs": 98,
     "solvent_keys": ["ch2cl2", "thf"], "stage1_solvents": ["ch2cl2"], "stage2_solvents": ["ch2cl2", "thf"]},
    {"entry": 4, "solvent1": "CH2Cl2", "temp1": {"number": 0, "unit": "°C"}, "time1": 3,
     "solvent2": "CH2Cl2/1,4-dioxane (1:2)", "temp2": {"number": 100, "unit": "°C"}, "yield": 85,
     "dr": "33:67", "ee_rr": 98, "ee_rs": 98,
     "solvent_keys": ["ch2cl2", "dioxane"], "stage1_solvents": ["ch2cl2"], "stage2_solvents": ["ch2cl2", "dioxane"]},
    {"entry": 5, "solvent1": "CH2Cl2/1,4-dioxane (1:2)", "temp1": "r.t.", "time1": 3,
     "solvent2": "CH2Cl2/1,4-dioxane (1:2)", "temp2": {"number": 100, "unit": "°C"}, "yield": 95,
     "dr": "32:68", "ee_rr": 95, "ee_rs": 95,
     "solvent_keys": ["ch2cl2", "dioxane"], "stage1_solvents": ["ch2cl2", "dioxane"], "stage2_solvents": ["ch2cl2", "dioxane"]},
    {"entry": 6, "solvent1": "CH2Cl2", "temp1": "r.t.", "time1": 1.5,
     "solvent2": "CH2Cl2/1,4-dioxane (1:2)", "temp2": {"number": 100, "unit": "°C"}, "yield": 100,
     "dr": "37:63", "ee_rr": 97, "ee_rs": 97,
     "solvent_keys": ["ch2cl2", "dioxane"], "stage1_solvents": ["ch2cl2"], "stage2_solvents": ["ch2cl2", "dioxane"]},
    {"entry": 7, "solvent1": "CH2Cl2/1,4-dioxane (1:2)", "temp1": {"number": 0, "unit": "°C"}, "time1": 10,
     "solvent2": "CH2Cl2/1,4-dioxane (1:2)", "temp2": {"number": 100, "unit": "°C"}, "yield": 90,
     "dr": "36:64", "ee_rr": 97, "ee_rs": 98,
     "solvent_keys": ["ch2cl2", "dioxane"], "stage1_solvents": ["ch2cl2", "dioxane"], "stage2_solvents": ["ch2cl2", "dioxane"]},
    {"entry": 8, "solvent1": "CH2Cl2/DMSO (1:2)", "temp1": {"number": 0, "unit": "°C"}, "time1": 20,
     "solvent2": "CH2Cl2/DMSO (1:2)", "temp2": {"number": 100, "unit": "°C"}, "yield": 19,
     "dr": "76:24", "ee_rr": 13, "ee_rs": 8,
     "solvent_keys": ["ch2cl2", "dmso"], "stage1_solvents": ["ch2cl2", "dmso"], "stage2_solvents": ["ch2cl2", "dmso"]},
    {"entry": 9, "solvent1": "CH2Cl2/DMF (1:2)", "temp1": {"number": 0, "unit": "°C"}, "time1": 20,
     "solvent2": "CH2Cl2/DMF (1:2)", "temp2": {"number": 100, "unit": "°C"}, "yield": 0,
     "dr": None, "ee_rr": None, "ee_rs": None,
     "solvent_keys": ["ch2cl2", "dmf"], "stage1_solvents": ["ch2cl2", "dmf"], "stage2_solvents": ["ch2cl2", "dmf"]},
]


HALIDES = {
    2: ("7b", "1-iodo-4-methylbenzene", "Cc1ccc(I)cc1", "1ab", 95, "34:66", 98, 98),
    3: ("7c", "1-iodo-4-methoxybenzene", "COc1ccc(I)cc1", "1ac", 92, "33:67", 98, 98),
    4: ("7d", "methyl 4-iodobenzoate", "COC(=O)c1ccc(I)cc1", "1ad", 96, "38:62", 97, 98),
    5: ("7e", "1-bromo-4-iodobenzene", "Brc1ccc(I)cc1", "1ae", 94, "36:64", 97, ">98"),
    6: ("7f", "1-iodo-4-nitrobenzene", "[O-][N+](=O)c1ccc(I)cc1", "1af", 97, "40:60", ">98", 99),
    7: ("7g", "methyl (E)-3-iodoacrylate (candidate interpretation of drawing)", "COC(=O)/C=C/I", "1ag", 98, "45:55", 97, 98),
    8: ("7h", "(E)-1-iodo-2-phenylethene (candidate interpretation of drawing)", "I/C=C/c1ccccc1", "1ah", 86, "37:63", 99, 99),
    9: ("7i", "(E)-1-iodohex-1-ene (candidate interpretation of drawing)", "I/C=C/CCCC", "1ai", 75, "34:66", 97, 98),
    10: ("7j", "2-iodothiophene", "Ic1cccs1", "1aj", 71, "36:64", 91, 99),
}


def scope_record(entry, data):
    halide_label, halide_name, halide_smiles, product_label, yield_value, dr, ee_rr, ee_rs = data
    ev = [P3I, P3T, P4I, P4T] if entry == 5 else [P3I, P3T]
    product_rr = f"product_{product_label}_rr"
    product_rs = f"product_{product_label}_rs"
    parts = [
        participant("substrate_5a", "reactant", "5a", ev,
                    "ethyl 2-acetylhexa-4,5-dienoate (candidate name)",
                    "CCOC(=O)C(CC=C=C)C(C)=O"),
        participant("dbad_6", "reactant", "6", ev, "dibenzyl azodicarboxylate (DBAD)",
                    "O=C(OCc1ccccc1)N=NC(=O)OCc1ccccc1"),
        participant(f"halide_{halide_label}", "reactant", halide_label, ev, halide_name, halide_smiles),
        participant(product_rr, "product", f"{product_label} (3R,5R)", ev,
                    f"cis-{product_label} (3R,5R) as drawn"),
        participant(product_rs, "product", f"{product_label} (3R,5S)", ev,
                    f"trans-{product_label} (3R,5S) as drawn"),
        participant("ph_box_ss", "catalyst", "Ph-Box (S,S)", ev, "(S,S)-Ph-Box ligand"),
        participant("cu_otf2", "catalyst", "Cu(OTf)2", ev, "copper(II) triflate", None,
                    [amount("catalyst_loading", 10, "mol%", ev)]),
        participant("k2co3", "reagent", "K2CO3", ev, "potassium carbonate", "[K+].[K+].[O-]C([O-])=O",
                    [amount("equivalents", 2.0, "equiv", ev)]),
        participant("pd_pph3_4", "catalyst", "Pd(PPh3)4", ev, "tetrakis(triphenylphosphine)palladium(0)", None,
                    [amount("catalyst_loading", 5, "mol%", ev)]),
        participant("ch2cl2", "solvent", "CH2Cl2", ev, "dichloromethane", "ClCCl"),
        participant("dioxane", "solvent", "1,4-dioxane", ev, "1,4-dioxane", "O1CCOCC1"),
    ]
    def ee_value(value):
        if isinstance(value, str) and value.startswith(">"):
            return {"number": float(value[1:]), "unit": "%", "qualifier": "gt", "raw_text": f"{value}%"}
        return {"number": value, "unit": "%"}
    outcomes = [
        field("yield", {"number": yield_value, "unit": "%"}, ev, [product_rr, product_rs]),
        field("yield_measurement_basis", None, ()),
        field("dr_ratio", dr, ev, [product_rr, product_rs]),
        field("rr_ee", ee_value(ee_rr), ev, [product_rr]),
        field("rs_ee", ee_value(ee_rs), ev, [product_rs]),
    ]
    notes = []
    if entry in (7, 8, 9):
        notes.append("The paper states that the C=C configuration of the 1-alkenyl iodide remained unchanged; the candidate halide SMILES still requires visual structure review.")
    if entry == 5:
        notes.append("The text states that C-I cleavage was chemoselective and the bromine atom remained in product 1ae.")
        notes.append("Page 4 identifies cis-1ae (3R,5R; CCDC 232606) and trans-1ae (3R,5S; CCDC 232607) by X-ray diffraction; these are characterization evidence for Table 2 entry 5, not separate syntheses.")
    unresolved = [
        "Final product structures were not transcribed to SMILES and require structure review.",
        "Substrate/DBAD equivalents, reaction scale, concentration, atmosphere, workup, purification, and yield measurement basis are absent from the supplied main-text table.",
        "The paper advertises Supporting Information, but no SI file was supplied or explicitly associated.",
    ]
    if entry in (7, 8, 9):
        unresolved.insert(0, "The exact alkenyl-halide name and stereochemical SMILES are candidate interpretations of the source drawing.")
    return record(
        f"table2_entry{entry:02d}", f"Table 2 entry {entry}", "substrate_scope_entry", ev, parts,
        [
            step("stage1_cu_asymmetric_amination",
                 ["substrate_5a", "dbad_6", "ph_box_ss", "cu_otf2", "ch2cl2"],
                 [field("solvent", "CH2Cl2", ev), field("temperature", {"number": 0, "unit": "°C"}, ev),
                  field("time", {"number": 3, "unit": "h"}, ev)]),
            step("stage2_pd_addition_cyclization",
                 [f"halide_{halide_label}", "k2co3", "pd_pph3_4", "dioxane"],
                 [field("solvent", "1,4-dioxane", ev), field("temperature", {"number": 100, "unit": "°C"}, ev),
                  field("time", {"number": 4, "unit": "h"}, ev)]),
        ], outcomes, notes, unresolved,
    )


def scheme2_rr_record():
    ev = [P2I, P2T]
    parts = [
        participant("substrate_5a", "reactant", "5a", ev,
                    "ethyl 2-acetylhexa-4,5-dienoate (candidate name)", "CCOC(=O)C(CC=C=C)C(C)=O"),
        participant("dbad_6", "reactant", "6", ev, "dibenzyl azodicarboxylate (DBAD)",
                    "O=C(OCc1ccccc1)N=NC(=O)OCc1ccccc1"),
        participant("ph_i_7a", "reactant", "7a", ev, "iodobenzene", "Ic1ccccc1"),
        participant("product_1aa_ss", "product", "1aa (S,S)", ev, "cis-1aa (S,S) as drawn"),
        participant("product_1aa_sr", "product", "1aa (S,R)", ev, "trans-1aa (S,R) as drawn"),
        participant("ph_box_rr", "catalyst", "Ph-Box (R,R)", ev, "(R,R)-Ph-Box ligand"),
        participant("cu_otf2", "catalyst", "Cu(OTf)2", ev, "copper(II) triflate", None,
                    [amount("catalyst_loading", 10, "mol%", ev)]),
        participant("k2co3", "reagent", "K2CO3", ev, "potassium carbonate", "[K+].[K+].[O-]C([O-])=O",
                    [amount("equivalents", 2.0, "equiv", ev)]),
        participant("pd_pph3_4", "catalyst", "Pd(PPh3)4", ev, "tetrakis(triphenylphosphine)palladium(0)", None,
                    [amount("catalyst_loading", 5, "mol%", ev)]),
        participant("ch2cl2", "solvent", "CH2Cl2", ev, "dichloromethane", "ClCCl"),
        participant("thf", "solvent", "THF", ev, "tetrahydrofuran", "C1CCOC1"),
    ]
    return record(
        "scheme2_phbox_rr", "Scheme 2 (R,R)-Ph-Box row", "reported_experiment", ev, parts,
        [
            step("stage1_cu_asymmetric_amination",
                 ["substrate_5a", "dbad_6", "ph_box_rr", "cu_otf2", "ch2cl2"],
                 [field("solvent", "CH2Cl2", ev), field("temperature", {"number": 0, "unit": "°C"}, ev),
                  field("time", None, ())]),
            step("solvent_change", ["ch2cl2", "thf"],
                 [field("operation", "remove CH2Cl2 in vacuo, then add THF", ev)]),
            step("stage2_pd_addition_cyclization",
                 ["ph_i_7a", "k2co3", "pd_pph3_4", "thf"],
                 [field("solvent", "THF", ev), field("temperature", "reflux", ev), field("time", None, ())]),
        ],
        [
            field("yield", {"number": 86, "unit": "%"}, ev, ["product_1aa_ss", "product_1aa_sr"]),
            field("yield_measurement_basis", None, ()),
            field("dr_ratio", "35:65", ev, ["product_1aa_ss", "product_1aa_sr"]),
            field("ss_ee", {"number": 97, "unit": "%"}, ev, ["product_1aa_ss"]),
            field("sr_ee", {"number": 98, "unit": "%"}, ev, ["product_1aa_sr"]),
        ],
        ["This is the (R,R)-Ph-Box experiment; the (S,S)-Ph-Box row is represented by Table 1 entry 1."],
        [
            "Stage durations are not stated in Scheme 2 or its accompanying paragraph for this ligand row.",
            "Final product structures were not transcribed to SMILES and require structure review.",
            "Reaction scale, concentration, atmosphere, workup, purification, and yield measurement basis are absent from the supplied main-text pages.",
            "The paper advertises Supporting Information, but no SI file was supplied or explicitly associated.",
        ],
    )


def general_scheme_record():
    ev = [P1I, P1T]
    parts = [
        participant("generic_5", "reactant", "5", ev, "generic 2-(2',3'-alkadienyl)-beta-keto ester"),
        participant("generic_organic_iodide", "reactant", "R7I", ev, "generic organic iodide"),
        participant("dbad_6", "reactant", "6", ev, "dibenzyl azodicarboxylate (DBAD)",
                    "O=C(OCc1ccccc1)N=NC(=O)OCc1ccccc1"),
        participant("generic_product_1", "product", "1 (3R,5S)", ev, "generic pyrazolidine product"),
        participant("ph_box_ss", "catalyst", "Ph-Box (S,S)", ev, "(S,S)-Ph-Box ligand"),
        participant("cu_otf2", "catalyst", "Cu(OTf)2", ev, "copper(II) triflate", None,
                    [amount("catalyst_loading", 10, "mol%", ev)]),
        participant("k2co3", "reagent", "K2CO3", ev, "potassium carbonate", "[K+].[K+].[O-]C([O-])=O",
                    [amount("equivalents", 2.0, "equiv", ev)]),
        participant("pd_pph3_4", "catalyst", "Pd(PPh3)4", ev, "tetrakis(triphenylphosphine)palladium(0)", None,
                    [amount("catalyst_loading", 5, "mol%", ev)]),
        participant("ch2cl2", "solvent", "CH2Cl2", ev, "dichloromethane", "ClCCl"),
        participant("dioxane", "solvent", "1,4-dioxane", ev, "1,4-dioxane", "O1CCOCC1"),
    ]
    return record(
        "graphical_abstract_general_scheme", "Graphical abstract reaction scheme", "general_scheme", ev, parts,
        [
            step("stage1_cu_asymmetric_amination",
                 ["generic_5", "dbad_6", "ph_box_ss", "cu_otf2", "ch2cl2"],
                 [field("solvent", "CH2Cl2", ev), field("temperature", {"number": 0, "unit": "°C"}, ev),
                  field("time", None, ())]),
            step("stage2_pd_addition_cyclization",
                 ["generic_organic_iodide", "k2co3", "pd_pph3_4", "dioxane"],
                 [field("solvent", "1,4-dioxane", ev), field("temperature", {"number": 100, "unit": "°C"}, ev),
                  field("time", {"number": 4, "unit": "h"}, ev)]),
        ], [],
        ["The graphical abstract is a generic R-group transformation and is not counted as an individual reported experiment."],
        ["Generic R-group structures cannot be assigned complete SMILES.", "No experiment-specific yield or first-stage duration is shown."],
    )


def mechanism_record():
    ev = [P2I, P2T]
    parts = [
        participant("generic_5", "reactant", "5", ev, "generic alpha-allenic-substituted beta-keto ester"),
        participant("generic_6", "reactant", "6", ev, "generic azodicarboxylate"),
        participant("intermediate_4", "unspecified_agent", "4", ev, "optically active allenic amide intermediate"),
        participant("intermediate_3", "unspecified_agent", "3", ev, "organopalladium intermediate R3PdX"),
        participant("intermediate_2", "unspecified_agent", "2", ev, "pi-allylpalladium intermediate"),
        participant("generic_product_1", "product", "1", ev, "generic pyrazolidine"),
        participant("generic_cu", "catalyst", "[Cu]", ev, "unspecified copper catalyst"),
    ]
    return record(
        "scheme1_mechanistic_rationale", "Scheme 1", "mechanism", ev, parts,
        [
            step("conceptual_enantioselective_amination", ["generic_5", "generic_6", "generic_cu", "intermediate_4"],
                 [field("operation", "enantioselective alpha-amination", ev)]),
            step("proposed_carbopalladation", ["intermediate_4", "intermediate_3", "intermediate_2"],
                 [field("operation", "proposed carbopalladation to a pi-allylpalladium intermediate", ev)]),
            step("proposed_intramolecular_trapping", ["intermediate_2", "generic_product_1"],
                 [field("operation", "proposed intramolecular nitrogen trapping", ev)]),
        ], [],
        ["Scheme 1 is a mechanistic/retrosynthetic rationale, not a reported experiment."],
        ["All structures are generic R-group structures; no experiment-specific quantities or outcomes are supplied."],
    )


records = [general_scheme_record(), mechanism_record(), scheme2_rr_record()]
records.extend(table1_record(row) for row in TABLE1)
records.extend(scope_record(entry, data) for entry, data in HALIDES.items())

assert len(records) == 21
assert len({item["record_id"] for item in records}) == 21
OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"output": str(OUT), "records": len(records)}, ensure_ascii=False))
