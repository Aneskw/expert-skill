#!/usr/bin/env python3
"""Build evidence-linked machine records for doc_f9e99ad106edda28, PDF pages 1-5."""
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "runs/current"
DOC = "doc_f9e99ad106edda28"


def ev(page: int) -> list[str]:
    return [f"{DOC}:page{page}:text", f"{DOC}:page{page}:image"]


def fact(value, evidence=None):
    evidence = [] if evidence is None else list(evidence)
    return {
        "value": value,
        "evidence_ids": evidence if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def field(name, value, evidence=None, targets=None):
    result = {"name": name, "fact": fact(value, evidence)}
    if targets:
        result["target_entity_ids"] = list(targets)
    return result


def participant(entity_id, role, label, evidence, *, name=None, smiles=None, amounts=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence) if name else fact(None),
        "smiles": fact(smiles, evidence) if smiles else fact(None),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": amounts or [],
    }


def amount(name, number, unit, evidence):
    return field(name, {"number": number, "unit": unit}, evidence)


def base_record(rid, kind, evidence, participants, steps, outcomes, notes, unresolved):
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
        "notes": [fact(note, evidence) for note in notes],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved,
        },
    }


SMILES = {
    "PPh3": "P(c1ccccc1)(c1ccccc1)c1ccccc1",
    "CO": "[C-]#[O+]",
    "H2": "[H][H]",
    "toluene": "Cc1ccccc1",
    "DMF": "CN(C)C=O",
    "DMSO": "CS(C)=O",
    "EtOH": "CCO",
    "CH3CN": "CC#N",
    "Dioxane": "O1CCOCC1",
    "THF": "C1CCOC1",
    "Benzene": "c1ccccc1",
    "CH2Br2": "BrCBr",
}

R1 = {
    "n-Pr": "CCC",
    "n-Bu": "CCCC",
    "n-Hex": "CCCCCC",
    "Cyclopropyl": "C1CC1",
    "Ph": "c1ccccc1",
}


def substrate_smiles(r1, r2):
    p = "P(=O)(c1ccccc1)c1ccccc1" if r2 == "Ph" else "P(=O)(OCC)OCC"
    return f"C=C=C({R1[r1]}){p}"


def product_smiles(r1, r2):
    p = "P(=O)(c1ccccc1)c1ccccc1" if r2 == "Ph" else "P(=O)(OCC)OCC"
    return f"O=CCCC({R1[r1]}){p}"


S1A = substrate_smiles("n-Pr", "Ph")
S2A = product_smiles("n-Pr", "Ph")


def common_species(evidence, *, catalyst, catalyst_loading, pph3_loading, solvent="toluene", solvent_volume=3.0,
                   scale=0.2, include_product=True, r1="n-Pr", r2="Ph", substrate_label="1a", product_label="2a"):
    parts = [
        participant("substrate", "reactant", substrate_label, evidence,
                    name=f"1,2-allenyl phosphorus substrate {substrate_label}",
                    smiles=substrate_smiles(r1, r2), amounts=[amount("amount", scale, "mmol", evidence)]),
    ]
    if include_product:
        parts.append(participant("product", "product", product_label, evidence,
                                 name=f"saturated linear gamma-phosphinyl aldehyde {product_label}",
                                 smiles=product_smiles(r1, r2)))
    parts.append(participant("catalyst", "catalyst", catalyst, evidence,
                             amounts=[amount("catalyst_loading", catalyst_loading, "mol%", evidence)]))
    if pph3_loading is not None:
        parts.append(participant("pph3", "reagent", "PPh3", evidence, name="triphenylphosphine",
                                 smiles=SMILES["PPh3"], amounts=[amount("reagent_loading", pph3_loading, "mol%", evidence)]))
    parts.extend([
        participant("co", "reagent", "CO", evidence, name="carbon monoxide", smiles=SMILES["CO"]),
        participant("h2", "reagent", "H2", evidence, name="hydrogen", smiles=SMILES["H2"]),
        participant("solvent", "solvent", solvent, evidence, smiles=SMILES.get(solvent),
                    amounts=[amount("volume", solvent_volume, "mL", evidence)]),
    ])
    return parts


def nmr_standard(evidence):
    return participant("internal_standard", "unspecified_agent", "CH2Br2", evidence,
                       name="dibromomethane internal standard", smiles=SMILES["CH2Br2"])


records = []

# Page 1: conceptual outcome map, not an executed experiment.
e = ev(1)
records.append(base_record(
    "scheme1_possible_hydroformylation_products", "general_scheme", e,
    [
        participant("generic_allene", "reactant", "generic allene (R1/R2)", e),
        participant("co", "reagent", "CO", e, name="carbon monoxide", smiles=SMILES["CO"]),
        participant("h2", "reagent", "H2", e, name="hydrogen", smiles=SMILES["H2"]),
        participant("enal_linear", "product", "generic unsaturated linear enal", e),
        participant("enal_branched_B", "product", "generic unsaturated branched enal leading to B", e),
        participant("enal_branched_C", "product", "generic unsaturated branched enal leading to C", e),
        participant("linear_A", "product", "linear saturated aldehyde A", e),
        participant("branched_B", "product", "branched saturated aldehyde B", e),
        participant("branched_C", "product", "branched saturated aldehyde C", e),
    ],
    [
        {"step_id": "conceptual_hydroformylation", "participant_ids": ["generic_allene", "co", "enal_linear", "enal_branched_B", "enal_branched_C"],
         "conditions": [field("operation", "generic hydroformylation to alternative unsaturated enals", e)]},
        {"step_id": "conceptual_hydrogenation", "participant_ids": ["h2", "enal_linear", "enal_branched_B", "enal_branched_C", "linear_A", "branched_B", "branched_C"],
         "conditions": [field("operation", "generic hydrogenation to saturated aldehydes A/B/C", e)]},
    ],
    [],
    ["Scheme 1 enumerates possible regioisomeric/unsaturated pathways and is not a row-level executed experiment."],
    ["R1 and R2 are generic substituents; structures and experiment-level quantities are intentionally missing."],
))


def table1_record(entry, rid, catalyst, time_h, nmr_yield, recovery=None, catalyst_loading=3, pph3_loading=10,
                  unidentified=False, no_reaction=False):
    e = ev(2)
    parts = common_species(e, catalyst=catalyst, catalyst_loading=catalyst_loading,
                           pph3_loading=pph3_loading, scale=0.2)
    if nmr_yield is not None:
        parts.append(nmr_standard(e))
    outcomes = []
    if no_reaction:
        outcomes.append(field("reaction_result", "NR (no reaction)", e))
    if nmr_yield is not None:
        outcomes += [field("nmr_yield_2a", {"number": nmr_yield, "unit": "%"}, e, ["product"]),
                     field("yield_measurement_basis", "300 MHz 1H NMR of crude mixture using CH2Br2 as internal standard", e, ["product"])]
    if recovery is not None:
        outcomes.append(field("recovered_starting_material_yield", {"number": recovery, "unit": "%"}, e, ["substrate"]))
    notes = [f"Table 1 entry {entry}."]
    if unidentified:
        notes.append("Other unidentified aldehydes were formed.")
    return base_record(
        rid, "optimization_entry", e, parts,
        [{"step_id": "hydroformylation_hydrogenation", "participant_ids": [p["entity_id"] for p in parts if p["entity_id"] != "internal_standard"],
          "conditions": [field("temperature", {"number": 100, "unit": "°C"}, e),
                         field("time", {"number": time_h, "unit": "h"}, e),
                         field("initial_CO_pressure", "2.4 × 10^6 Pa", e),
                         field("final_combined_CO_H2_pressure", "4.8 × 10^6 Pa", e),
                         field("atmosphere", None), field("workup", None), field("purification", None)]}],
        outcomes, notes,
        ["The table does not report atmosphere, workup, or purification.",
         "All candidate structures are machine-derived and unverified."],
    )


records.extend([
    table1_record(1, "table1_entry1_palladium", "Pd(Ar-BIAN)(dimethyl fumarate)", 2, None, recovery=77,
                  pph3_loading=None, no_reaction=True),
    table1_record(2, "table1_entry2_ruthenium", "RuHCl(CO)(PPh3)3", 48, 2, recovery=41, unidentified=True),
    table1_record(3, "table1_entry3_rhclco_dimer", "[RhCl(CO)2]2", 48, 13, unidentified=True),
    table1_record(4, "table1_entry4_rhacac", "Rh(acac)(CO)2", 48, 75),
    table1_record(5, "table1_entry5_rhh_low_loading", "RhH(CO)(PPh3)3", 24, 51,
                  catalyst_loading=1, pph3_loading=3, unidentified=True),
    table1_record(6, "table1_entry6_rhh_high_loading", "RhH(CO)(PPh3)3", 24, 85,
                  catalyst_loading=5, pph3_loading=15),
])

# One exact 0.2 mmol condition is printed as Table 1 entry 7, Table 2 entry 2, and Table 3 entry 10.
eopt = ev(2) + ev(3)
parts = common_species(eopt, catalyst="RhH(CO)(PPh3)3", catalyst_loading=3, pph3_loading=10, scale=0.2)
parts.append(nmr_standard(eopt))
records.append(base_record(
    "optimized_1a_to_2a_0p2mmol", "optimization_entry", eopt, parts,
    [{"step_id": "hydroformylation_hydrogenation", "participant_ids": [p["entity_id"] for p in parts if p["entity_id"] != "internal_standard"],
      "conditions": [field("temperature", {"number": 100, "unit": "°C"}, eopt),
                     field("time", {"number": 24, "unit": "h"}, eopt),
                     field("initial_CO_pressure", "2.4 × 10^6 Pa", eopt),
                     field("final_combined_CO_H2_pressure", "4.8 × 10^6 Pa", eopt),
                     field("atmosphere", None), field("workup", None), field("purification", None)]}],
    [field("nmr_yield_2a", {"number": 89, "unit": "%"}, eopt, ["product"]),
     field("isolated_yield_2a", {"number": 72, "unit": "%"}, eopt, ["product"]),
     field("nmr_yield_measurement_basis", "300 MHz 1H NMR of crude mixture using CH2Br2 as internal standard", eopt, ["product"]),
     field("isolated_yield_measurement_basis", "isolated yield", eopt, ["product"]),
     field("regioselectivity", "2a reported as the only product", ev(2), ["product"])],
    ["The identical 0.2 mmol/3 mL/100 °C/24 h pressure condition is printed in Table 1 entry 7, Table 2 entry 2, and Table 3 entry 10."],
    ["Atmosphere, workup, and purification are absent for this 0.2 mmol table experiment; the later 0.4 mmol detailed procedure is a distinct scaled experiment."],
))


def pressure_record(entry, initial, final, yld):
    e = ev(3)
    parts = common_species(e, catalyst="RhH(CO)(PPh3)3", catalyst_loading=3, pph3_loading=10, scale=0.2)
    parts.append(nmr_standard(e))
    return base_record(
        f"table2_entry{entry}_pressure_screen", "optimization_entry", e, parts,
        [{"step_id": "hydroformylation_hydrogenation", "participant_ids": [p["entity_id"] for p in parts if p["entity_id"] != "internal_standard"],
          "conditions": [field("temperature", {"number": 100, "unit": "°C"}, e),
                         field("time", {"number": 24, "unit": "h"}, e),
                         field("initial_CO_pressure", initial, e),
                         field("final_combined_CO_H2_pressure", final, e),
                         field("atmosphere", None), field("workup", None), field("purification", None)]}],
        [field("nmr_yield_2a", {"number": yld, "unit": "%"}, e, ["product"]),
         field("yield_measurement_basis", "300 MHz 1H NMR of crude mixture using CH2Br2 as internal standard", e, ["product"])],
        [f"Table 2 entry {entry}."],
        ["Atmosphere, workup, and purification are not reported."],
    )


records.extend([
    pressure_record(1, "1.4 × 10^6 Pa", "2.8 × 10^6 Pa", 70),
    pressure_record(3, "5.2 × 10^6 Pa", "10.3 × 10^6 Pa", 77),
    pressure_record(4, "1.4 × 10^6 Pa", "4.1 × 10^6 Pa", 67),
    pressure_record(5, "2.8 × 10^6 Pa", "4.1 × 10^6 Pa", 80),
])


SOLVENT_ROWS = [
    (1, "DMF", 56, None, 10),
    (2, "DMSO", 64, None, 10),
    (3, "EtOH", 67, None, 10),
    (4, "CH3CN", 68, None, 10),
    (5, "Dioxane", 70, None, 10),
    (6, "THF", 77, None, 10),
    (7, "Benzene", 77, None, 10),
    (8, "toluene", 84, 67, 10),
    (9, "toluene", 65, None, None),
]


for entry, solvent, yld, isolated, pph3_loading in SOLVENT_ROWS:
    e = ev(3)
    parts = common_species(e, catalyst="RhH(CO)(PPh3)3", catalyst_loading=3,
                           pph3_loading=pph3_loading, solvent=solvent, scale=0.2)
    parts.append(nmr_standard(e))
    outcomes = [field("nmr_yield_2a", {"number": yld, "unit": "%"}, e, ["product"]),
                field("nmr_yield_measurement_basis", "300 MHz 1H NMR of crude mixture using CH2Br2 as internal standard", e, ["product"])]
    if isolated is not None:
        outcomes += [field("isolated_yield_2a", {"number": isolated, "unit": "%"}, e, ["product"]),
                     field("isolated_yield_measurement_basis", "isolated yield", e, ["product"])]
    if entry <= 8:
        outcomes.append(field("regioselectivity", "2a reported as the only product", ev(2) + e, ["product"]))
    notes = [f"Table 3 entry {entry}."]
    if entry == 9:
        notes.append("Footnote d explicitly states that no PPh3 was applied.")
    records.append(base_record(
        f"table3_entry{entry}_{solvent.lower()}_solvent", "optimization_entry", e, parts,
        [{"step_id": "hydroformylation_hydrogenation", "participant_ids": [p["entity_id"] for p in parts if p["entity_id"] != "internal_standard"],
          "conditions": [field("temperature", {"number": 60, "unit": "°C"}, e),
                         field("time", {"number": 24, "unit": "h"}, e),
                         field("initial_CO_pressure", "2.4 × 10^6 Pa", e),
                         field("final_combined_CO_H2_pressure", "4.8 × 10^6 Pa", e),
                         field("atmosphere", None), field("workup", None), field("purification", None)]}],
        outcomes, notes,
        ["Atmosphere, workup, and purification are not reported."],
    ))


SCOPE = [
    (1, "n-Pr", "Ph", "1a", "2a", 72),
    (2, "n-Bu", "Ph", "1b", "2b", 68),
    (3, "n-Hex", "Ph", "1c", "2c", 64),
    (4, "Cyclopropyl", "Ph", "1d", "2d", 61),
    (5, "n-Pr", "OEt", "1e", "2e", 54),
    (6, "n-Bu", "OEt", "1f", "2f", 59),
    (7, "n-Hex", "OEt", "1g", "2g", 53),
    (8, "Cyclopropyl", "OEt", "1h", "2h", 50),
    (9, "Ph", "OEt", "1i", "2i", 54),
]


for entry, r1, r2, slabel, plabel, yld in SCOPE:
    e = ev(3)
    evidence = e + (ev(4) if entry in {1, 2, 4, 9} else [])
    parts = common_species(evidence, catalyst="RhH(CO)(PPh3)3", catalyst_loading=3,
                           pph3_loading=10, solvent="toluene", solvent_volume=4.0,
                           scale=0.4, r1=r1, r2=r2, substrate_label=slabel, product_label=plabel)
    steps = [{"step_id": "hydroformylation_hydrogenation", "participant_ids": [p["entity_id"] for p in parts],
              "conditions": [field("temperature", {"number": 100, "unit": "°C"}, e),
                             field("time", {"number": 24, "unit": "h"}, e),
                             field("initial_CO_pressure", "2.4 × 10^6 Pa", e),
                             field("final_combined_CO_H2_pressure", "4.8 × 10^6 Pa", e),
                             field("atmosphere", None), field("workup", None), field("purification", None)]}]
    outcomes = [field(f"isolated_yield_{plabel}", {"number": yld, "unit": "%"}, e, ["product"]),
                field("yield_measurement_basis", "isolated yield", e, ["product"]),
                field("regioselectivity", "linear saturated aldehyde reported as the only product", e, ["product"])]
    notes = [f"Table 4 entry {entry}; R1={r1}, R2={r2}."]
    unresolved = ["The abbreviated Table 4 row does not report atmosphere, workup, or purification.",
                  "Candidate substrate/product connectivity and stereochemistry remain unverified."]
    if entry == 1:
        # Replace nominal amounts/operations with the exact, cross-page typical procedure while retaining the table-level 4 mL statement.
        parts[0]["amounts"] += [amount("mass", 113, "mg", ev(3))]
        parts[2]["amounts"] += [amount("mass", 11, "mg", ev(3)), amount("amount", 0.012, "mmol", ev(3))]
        parts[3]["amounts"] += [amount("mass", 10, "mg", ev(3)), amount("amount", 0.038, "mmol", ev(3))]
        parts.append(participant("autoclave_toluene", "solvent", "anhydrous toluene in autoclave", ev(3),
                                 name="toluene", smiles=SMILES["toluene"], amounts=[amount("volume", 20, "mL", ev(3))]))
        steps = [
            {"step_id": "charge_reaction_vessel", "participant_ids": ["substrate", "catalyst", "pph3", "solvent"],
             "conditions": [field("operation", "PPh3, RhH(CO)(PPh3)3, 1a, and 4 mL anhydrous toluene were added sequentially in open air", ev(3)),
                            field("atmosphere", "open air during initial charging", ev(3))]},
            {"step_id": "transfer_and_CO_purge", "participant_ids": ["substrate", "catalyst", "pph3", "solvent", "autoclave_toluene", "co"],
             "conditions": [field("operation", "transferred to an autoclave containing 20 mL anhydrous toluene", ev(3)),
                            field("purge_CO_pressure", "6.9 × 10^5 Pa", ev(3)),
                            field("purge_repetitions", 3, ev(3))]},
            {"step_id": "hydroformylation_hydrogenation", "participant_ids": ["substrate", "catalyst", "pph3", "solvent", "autoclave_toluene", "co", "h2", "product"],
             "conditions": [field("initial_CO_pressure", "2.4 × 10^6 Pa", ev(3)),
                            field("final_combined_CO_H2_pressure", "4.8 × 10^6 Pa", ev(3)),
                            field("temperature", {"number": 100, "unit": "°C"}, ev(3) + ev(4)),
                            field("time", {"number": 24, "unit": "h"}, ev(4))]},
            {"step_id": "workup_and_analysis", "participant_ids": ["product"],
             "conditions": [field("workup", "cooled to room temperature; pressure carefully released in a well-ventilated hood; solvent evaporated to dryness", ev(4)),
                            field("operation", "residue analyzed by 300 MHz 1H NMR; 2a was the only product", ev(4))]},
            {"step_id": "purification", "participant_ids": ["product"],
             "conditions": [field("purification", "flash chromatography on silica gel; ethyl acetate eluent", ev(4))]},
        ]
        parts[1]["amounts"] = [amount("isolated_product_mass", 91, "mg", ev(4))]
        outcomes += [field("isolated_product_mass", {"number": 91, "unit": "mg"}, ev(4), ["product"])]
        notes += ["The Table 4 footnote states 4 mL toluene, while the detailed procedure uses 4 mL in the vessel plus 20 mL already in the autoclave; both source statements are retained.",
                  "The detailed experiment reports 2a as the only product by crude 300 MHz 1H NMR."]
        unresolved = ["Table 4 and the detailed procedure differ in how the toluene volume is summarized.",
                      "Candidate substrate/product structures remain unverified despite full characterization of 2a."]
    elif entry in {2, 4, 9}:
        notes.append("The acknowledgments state that the result for this Table 4 entry was reproduced by Mr. Shu Wei.")
    records.append(base_record(
        f"table4_entry{entry}_{slabel}_to_{plabel}", "substrate_scope_entry", evidence,
        parts, steps, outcomes, notes, unresolved,
    ))

# Proposed mechanism: page-2 prose plus page-4 Scheme 3.
emech = ev(2) + ev(4)
mechanism_parts = [
    participant("substrate_1", "reactant", "1 (generic 1,2-allenyl phosphine oxide/phosphonate)", emech),
    participant("product_2", "product", "2 (linear saturated gamma-phosphinyl aldehyde)", emech),
    participant("rh_species_3", "catalyst", "Rh species 3", emech),
    participant("intermediate_4", "unspecified_agent", "allene-Rh complex 4", emech),
    participant("intermediate_5", "unspecified_agent", "allylic Rh intermediate 5", emech),
    participant("intermediate_6", "unspecified_agent", "CO complex 6", emech),
    participant("intermediate_7", "unspecified_agent", "acyl-Rh intermediate 7", emech),
    participant("intermediate_8", "unspecified_agent", "beta,gamma-unsaturated enal 8", emech),
    participant("intermediate_9", "unspecified_agent", "carbo-Rh intermediate 9", emech),
    participant("intermediate_10", "unspecified_agent", "carbo-Rh intermediate 10", emech),
    participant("co", "reagent", "CO", emech, name="carbon monoxide", smiles=SMILES["CO"]),
    participant("h2", "reagent", "H2", emech, name="hydrogen", smiles=SMILES["H2"]),
]
records.append(base_record(
    "scheme3_proposed_mechanism", "mechanism", emech, mechanism_parts,
    [
        {"step_id": "ligand_dissociation_and_coordination", "participant_ids": ["substrate_1", "rh_species_3", "intermediate_4"], "conditions": [field("operation", "PPh3 dissociation followed by allene coordination", emech)]},
        {"step_id": "hydrorhodiation", "participant_ids": ["intermediate_4", "intermediate_5"], "conditions": [field("operation", "proposed hydrorhodiation", emech)]},
        {"step_id": "CO_coordination_and_insertion", "participant_ids": ["intermediate_5", "co", "intermediate_6", "intermediate_7"], "conditions": [field("operation", "CO coordination followed by migrative insertion", emech)]},
        {"step_id": "enal_release", "participant_ids": ["intermediate_7", "h2", "intermediate_8"], "conditions": [field("operation", "oxidative addition and reductive elimination to beta,gamma-unsaturated enal 8", emech)]},
        {"step_id": "hydrogenation", "participant_ids": ["intermediate_8", "rh_species_3", "h2", "intermediate_9", "intermediate_10", "product_2"], "conditions": [field("operation", "second hydrorhodiation and hydrogenolysis to saturated aldehyde 2", emech)]},
    ],
    [],
    ["Scheme 3 is explicitly proposed; L denotes PPh3."],
    ["Generic R groups, organorhodium connectivity, branching between intermediates 9/10, and stereochemistry remain unverified."],
))


assert len(records) == 31, len(records)

raw_path = OUT / "raw_model/records_pages_0001_0005.json"
raw_path.parent.mkdir(parents=True, exist_ok=True)
raw_path.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")

ids = {r["source_reaction_id"]: r["record_id"] for r in records}
table1_ids = [ids[x] for x in [
    "table1_entry1_palladium", "table1_entry2_ruthenium", "table1_entry3_rhclco_dimer",
    "table1_entry4_rhacac", "table1_entry5_rhh_low_loading", "table1_entry6_rhh_high_loading",
    "optimized_1a_to_2a_0p2mmol",
]]
table2_ids = [ids["table2_entry1_pressure_screen"], ids["optimized_1a_to_2a_0p2mmol"],
              ids["table2_entry3_pressure_screen"], ids["table2_entry4_pressure_screen"], ids["table2_entry5_pressure_screen"]]
table3_ids = [ids[f"table3_entry{i}_{name}_solvent"] for i, name in [
    (1, "dmf"), (2, "dmso"), (3, "etoh"), (4, "ch3cn"), (5, "dioxane"),
    (6, "thf"), (7, "benzene"), (8, "toluene"), (9, "toluene"),
]] + [ids["optimized_1a_to_2a_0p2mmol"]]
table4_ids = [ids[f"table4_entry{i}_{s}_to_{p}"] for i, _, _, s, p, _ in SCOPE]

coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1,
            "state": "attempted",
            "regions": [
                {"region": "title, abstract, and introduction", "finding": "High-level present-paper conditions and claims; merged into later table records rather than duplicated. Online SI availability is stated, but no SI file is supplied or associated.", "evidence_ids": ev(1)},
                {"region": "bottom Scheme 1", "finding": "Generic outcome map for hydroformylation/hydrogenation of allenes; classified as a general scheme, not an executed experiment.", "evidence_ids": ev(1)},
            ],
            "record_ids": [ids["scheme1_possible_hydroformylation_products"]],
            "unresolved": ["Scheme 1 uses generic R1/R2 substituents and has no experiment-level quantities or yields."],
        },
        {
            "page": 2,
            "state": "attempted",
            "regions": [
                {"region": "left Scheme 2", "finding": "Molecular structure of Pd(Ar-BIAN)(dimethyl fumarate), used as the Table 1 entry-1 catalyst; not a reaction arrow or independent experiment.", "evidence_ids": ev(2)},
                {"region": "upper-right Table 1 and footnotes", "finding": "Seven catalyst/loading optimization rows extracted; entry 7 is the same 0.2 mmol optimized condition repeated in Tables 2 and 3 and was merged once.", "evidence_ids": ev(2)},
                {"region": "lower columns results and proposed-mechanism prose", "finding": "Narrative recovery, unidentified-aldehyde, sole-product, and mechanism facts linked to Table 1 and Scheme 3 records.", "evidence_ids": ev(2)},
            ],
            "record_ids": table1_ids + [ids["scheme3_proposed_mechanism"]],
            "unresolved": ["Table 1 omits atmosphere, workup, and purification; most catalyst structures remain labels without verified SMILES."],
        },
        {
            "page": 3,
            "state": "attempted",
            "regions": [
                {"region": "upper-left Table 2 and footnotes", "finding": "Five pressure-screen rows inventoried; entry 2 merged with the same optimized condition in Table 1 entry 7 and Table 3 entry 10.", "evidence_ids": ev(3)},
                {"region": "lower-left Table 3 and footnotes", "finding": "Ten solvent/free-PPh3/temperature rows inventoried; entry 10 merged with the repeated optimized condition.", "evidence_ids": ev(3)},
                {"region": "upper-right Table 4 and footnotes", "finding": "Nine substrate-scope rows extracted independently with isolated yields and shared conditions A.", "evidence_ids": ev(3)},
                {"region": "lower-right typical procedure opening", "finding": "Exact charge quantities, initial open-air operation, autoclave transfer, CO purging, and pressure charging merged into the distinct 0.4 mmol Table 4 entry-1 experiment.", "evidence_ids": ev(3)},
            ],
            "record_ids": list(dict.fromkeys(table2_ids + table3_ids + table4_ids)),
            "unresolved": ["Pressure is retained as explicit source text because Pa is not a supported structured-quantity unit in the fixed schema.", "Table 4 summarizes 4 mL toluene, while the detailed procedure additionally places 20 mL toluene in the autoclave."],
        },
        {
            "page": 4,
            "state": "attempted",
            "regions": [
                {"region": "upper Scheme 3", "finding": "Proposed Rh catalytic cycle through intermediates 3-10; classified as a mechanism, not executed stepwise experiments.", "evidence_ids": ev(4)},
                {"region": "lower-left typical procedure continuation", "finding": "H2 charging continuation, 100 °C/24 h, cooling/depressurization, evaporation, crude NMR, flash chromatography, 91 mg and 72% isolated 2a merged into Table 4 entry 1.", "evidence_ids": ev(4)},
                {"region": "acknowledgment and references", "finding": "Acknowledgment says Table 4 entries 2, 4, and 9 were reproduced; this is not an additional condition and creates no duplicate records.", "evidence_ids": ev(4)},
            ],
            "record_ids": [ids["scheme3_proposed_mechanism"], ids["table4_entry1_1a_to_2a"],
                           ids["table4_entry2_1b_to_2b"], ids["table4_entry4_1d_to_2d"], ids["table4_entry9_1i_to_2i"]],
            "unresolved": ["Organorhodium intermediate structures and stereochemistry are unverified.", "The detailed procedure does not state a separate isolated-yield measurement method beyond isolation and mass."],
        },
        {
            "page": 5,
            "state": "attempted",
            "regions": [
                {"region": "full two-column page", "finding": "References [5]-[14] and journal furniture only; no present-paper reaction arrow, table, footnote, procedure, condition, or outcome.", "evidence_ids": ev(5)},
            ],
            "record_ids": [],
            "unresolved": ["Cited prior publications were not supplied as associated source documents and were not mined for experiment details."],
        },
    ],
}

coverage_path = OUT / "coverage/pages_0001_0005.json"
coverage_path.parent.mkdir(parents=True, exist_ok=True)
coverage_path.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

tasks_path = OUT / "tasks.json"
tasks = json.loads(tasks_path.read_text())
for task in tasks:
    if task.get("document_id") == DOC and task.get("task_id") in {f"{DOC}:page{i}:text" for i in range(1, 6)}:
        task["state"] = "attempted"
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"records": len(records), "raw": str(raw_path), "coverage": str(coverage_path)}, ensure_ascii=False))
