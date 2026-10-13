#!/usr/bin/env python3
"""Build source-linked machine records for Zhang, Fu & Ma, Org. Lett. 2011, PDF pp. 1-4."""
import json
from pathlib import Path

DOC = "doc_f2387aac509ba979"
ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).with_name("records_pages_0001_0004.json")


def eids(page):
    return [f"{DOC}:page{page}:image", f"{DOC}:page{page}:text"]


def fact(value, page=None):
    return {
        "value": value,
        "evidence_ids": eids(page) if value is not None and page else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def field(name, value, page, targets=None):
    item = {"name": name, "fact": fact(value, page)}
    if targets:
        item["target_entity_ids"] = targets
    return item


def participant(entity_id, role, label, page, name=None, smiles=None, amounts=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, page),
        "name": fact(name, page) if name else fact(None),
        "smiles": fact(smiles, page) if smiles else fact(None),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": amounts or [],
    }


def amount(name, number, unit, page, raw_text=None, qualifier=None):
    value = {"number": number, "unit": unit}
    if raw_text:
        value["raw_text"] = raw_text
    if qualifier:
        value["qualifier"] = qualifier
    return field(name, value, page)


def missing_conditions():
    return [field("atmosphere", None, None), field("workup", None, None), field("purification", None, None)]


def record(suffix, page, kind, participants, steps=None, outcomes=None, notes=None, unresolved=None, extra_evidence=None):
    evidence = eids(page)
    for eid in extra_evidence or []:
        if eid not in evidence:
            evidence.append(eid)
    return {
        "record_id": f"{DOC}:{suffix}",
        "document_id": DOC,
        "source_reaction_id": suffix,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": evidence,
        "participants": participants,
        "steps": steps or [],
        "outcomes": outcomes or [],
        "notes": notes or [],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved or [],
        },
    }


records = []

# Page 1 graphical abstract: generic transformation, not a batch experiment.
records.append(record(
    "graphical_abstract_general_rearrangement", 1, "general_scheme",
    [participant("generic_allenyl_carboxylate", "reactant", "generic 2,3-allenyl carboxylate (R1/R2/R3)", 1),
     participant("generic_diene_carboxylate", "product", "generic 2-carboxy-1,3(E)-alkadiene", 1),
     participant("rh_a", "catalyst", "Rh(PPh3)3Cl", 1, amounts=[amount("catalyst_loading", 1, "mol%", 1)]),
     participant("pph3", "reagent", "PPh3", 1, amounts=[amount("ligand_loading", 3, "mol%", 1)]),
     participant("rh_b", "catalyst", "Rh(CO)(PPh3)2Cl", 1, amounts=[amount("alternative_catalyst_loading", 2, "mol%", 1)]),
     participant("toluene", "solvent", "toluene", 1, smiles="Cc1ccccc1")],
    steps=[{"step_id": "generic_rearrangement", "participant_ids": ["generic_allenyl_carboxylate", "rh_a", "pph3", "rh_b", "toluene"],
            "conditions": [field("temperature", {"number": 120, "unit": "°C"}, 1)]}],
    outcomes=[field("maximum_reported_yield", {"number": 92, "unit": "%", "qualifier": "le", "raw_text": "yield up to 92%"}, 1, ["generic_diene_carboxylate"]),
              field("reported_E_Z_selectivity", "E/Z up to >99/1", 1, ["generic_diene_carboxylate"])],
    unresolved=["Graphical abstract is a generic scope summary, not an individual experiment.", "R-group structures and the choice between the two catalyst systems are generic."]
))

# Page 2 Scheme 1: explicitly cited prior literature, retained as literature examples.
records.append(record(
    "scheme1_eq1_prior_propargylic_rearrangement", 2, "literature_example",
    [participant("lit1_substrate", "reactant", "TMS-substituted propargylic carboxylate (generic R groups)", 2),
     participant("lit1_diene", "product", "1,3-alkadien-2-yl carboxylate", 2),
     participant("lit1_enone", "product", "3-alken-2-one", 2),
     participant("lit1_propargyl", "product", "propargylic carboxylate", 2),
     participant("lit1_auag", "catalyst", "Au(I)/Ag(I)", 2)],
    outcomes=[field("reported_diene_yield", {"number": 84, "unit": "%"}, 2, ["lit1_diene"]),
              field("reported_enone_yield", {"number": 4, "unit": "%"}, 2, ["lit1_enone"]),
              field("reported_propargylic_carboxylate_yield", {"number": 3, "unit": "%"}, 2, ["lit1_propargyl"])],
    unresolved=["This is cited prior work (reference 14a), not a newly reported experiment in this paper.", "Generic R groups and full operating conditions are not specified here."]
))
records.append(record(
    "scheme1_eq2_prior_pivalate_migration", 2, "literature_example",
    [participant("lit2_substrate", "reactant", "generic propargylic pivalate", 2),
     participant("lit2_diene", "product", "(1Z,3E)-2-pivaloxy-1,3-diene", 2),
     participant("lit2_enone", "product", "alpha,beta-unsaturated enone", 2),
     participant("lit2_au", "catalyst", "Au(I)", 2)],
    outcomes=[field("reported_diene_yield", {"number": 86, "unit": "%"}, 2, ["lit2_diene"]),
              field("reported_enone_yield", {"number": 8, "unit": "%"}, 2, ["lit2_enone"])],
    unresolved=["This is cited prior work (reference 14b), not a newly reported experiment in this paper.", "Generic R groups and full operating conditions are not specified here."]
))
records.append(record(
    "scheme1_eq3_prior_au_allenyl_isomerization", 2, "literature_example",
    [participant("lit3_substrate", "reactant", "generic 2,3-allenyl carboxylate", 2),
     participant("lit3_product", "product", "generic 1,3-dien-2-yl carboxylate", 2),
     participant("lit3_au", "catalyst", "Au(I)", 2)],
    outcomes=[field("reported_Z_E_ratio_range", "Z/E from 1:1 to 0:1", 2, ["lit3_product"])],
    unresolved=["This is cited prior work (reference 16), not a newly reported experiment in this paper.", "Yield and exact Au(I) catalyst are not stated in Scheme 1 eq 3."]
))

# Page 2 Scheme 2 is a proposed catalytic cycle, not an experiment.
records.append(record(
    "scheme2_proposed_rh_mechanism", 2, "mechanism",
    [participant("mech_substrate_1", "reactant", "generic allenyl carboxylate 1", 2),
     participant("mech_complex_3", "unspecified_agent", "Rh-coordinated complex 3", 2),
     participant("mech_trans_4", "unspecified_agent", "trans cyclic intermediate 4 (favored)", 2),
     participant("mech_cis_4", "unspecified_agent", "cis cyclic intermediate 4", 2),
     participant("mech_product_e2", "product", "E-2", 2),
     participant("mech_rh", "catalyst", "RhL3+", 2)],
    notes=[fact("Proposed sequence: allene coordination, oxametalation, then beta-elimination; E selectivity is rationalized by favored trans-4.", 2)],
    unresolved=["Scheme 2 is a mechanistic proposal; intermediates and stereochemical rationale are not experimental records.", "Generic R groups prevent fully specified structures."]
))

SMILES_1A = "C=C=C(CCCC)C(C)OC(C)=O"
SMILES_E2A = "C=C(OC(C)=O)/C(CCCC)=C/C"
SMILES_1E = "C=C=C(CCCC)C(OC(C)=O)c1ccccc1"
SMILES_E2E = "C=C(OC(C)=O)/C(CCCC)=C/c1ccccc1"

# Page 3 Table 1 optimization rows.
t1 = [
    (1, "Rh(CO)(PPh3)2Cl", 5, "toluene", 120, 8, 74, ">98/2", 14),
    (2, "[Rh(COD)Cl]2", 2.5, "toluene", 120, 6, 0, None, 99),
    (3, "Rh(PPh3)3Cl", 5, "toluene", 120, 4, 84, ">98/2", 0),
    (4, "Rh(PPh3)3Cl", 5, "1,4-dioxane", 120, 6, 44, ">99/1", 0),
    (5, "Rh(PPh3)3Cl", 5, "DMF", 120, 6, 0, None, 93),
    (6, "Rh(PPh3)3Cl", 5, "DMSO", 120, 6, 2, None, 66),
    (7, "Rh(PPh3)3Cl", 5, "toluene", 80, 6, 18, "99/1", 75),
    (8, "Rh(PPh3)3Cl", 2, "toluene", 120, 6, 88, "98/2", 0),
    (9, "Rh(PPh3)3Cl", 1, "toluene", 120, 10, 85, "98/2", 0),
    (10, "Rh(PPh3)3Cl", 1, "toluene", 120, 10, 89, ">99/1", 0),
    (11, "Rh(PMe3)3Cl", 1, "toluene", 120, 10, 84, ">98/2", 0),
]
solvent_smiles = {"toluene": "Cc1ccccc1", "1,4-dioxane": "O1CCOCC1", "DMF": "CN(C)C=O", "DMSO": "CS(C)=O"}
for n, cat, catload, solvent, temp, time, yld, ratio, recovery in t1:
    scale = 0.5 if n >= 9 else 0.25
    volume = 3 if n >= 9 else 6
    parts = [
        participant("substrate_1a", "reactant", "1a", 3, "3-butyl-3,4-pentadien-2-yl acetate", SMILES_1A,
                    [amount("reaction_scale", scale, "mmol", 3)]),
        participant("product_E_2a", "product", "E-2a", 3, "3-butyl-1,3(E)-pentadien-2-yl acetate", SMILES_E2A),
        participant("product_Z_2a", "product", "Z-2a", 3),
        participant("catalyst", "catalyst", cat, 3, amounts=[amount("catalyst_loading", catload, "mol%", 3)]),
        participant("solvent", "solvent", solvent, 3, smiles=solvent_smiles.get(solvent), amounts=[amount("volume", volume, "mL", 3)]),
    ]
    if n == 10:
        parts.append(participant("added_ligand", "reagent", "PPh3", 3, smiles="P(c1ccccc1)(c1ccccc1)c1ccccc1", amounts=[amount("ligand_loading", 3, "mol%", 3)]))
    if n == 11:
        parts.append(participant("added_ligand", "reagent", "PMe3", 3, amounts=[amount("ligand_loading", 3, "mol%", 3)]))
    out = [field("NMR_yield_of_2a", {"number": yld, "unit": "%"}, 3, ["product_E_2a", "product_Z_2a"]),
           field("yield_measurement_basis", "1H NMR using 1,3,5-trimethylbenzene as internal standard", 3),
           field("E_Z_ratio", ratio, 3, ["product_E_2a", "product_Z_2a"]) if ratio else field("E_Z_ratio", None, None, ["product_E_2a", "product_Z_2a"]),
           field("recovered_starting_material_yield", {"number": recovery, "unit": "%"}, 3, ["substrate_1a"])]
    if n == 10:
        out += [field("isolated_yield_of_2a", {"number": 81, "unit": "%"}, 3, ["product_E_2a", "product_Z_2a"]),
                field("isolated_yield_measurement_basis", "isolated yield", 3)]
    notes = []
    if n == 2:
        notes.append(fact("[Rh(COD)Cl]2 did not promote the reaction.", 2))
    if n == 5:
        notes.append(fact("The DMF experiment was described as no reaction.", 2))
    records.append(record(
        f"table1_entry{n}", 3, "optimization_entry", parts,
        steps=[{"step_id": "isomerization", "participant_ids": [p["entity_id"] for p in parts if p["role"] != "product"],
                "conditions": [field("oil_bath_temperature", {"number": temp, "unit": "°C"}, 3), field("time", {"number": time, "unit": "h"}, 3), field("solvent", solvent, 3)] + missing_conditions()}],
        outcomes=out, notes=notes,
        unresolved=["No SI was supplied or explicitly associated.", "Atmosphere, workup and purification are not reported in the table."] + (["E/Z ratio is not reported for this row."] if ratio is None else []),
        extra_evidence=eids(2) if n in range(1, 12) else None,
    ))

# Page 3 Table 2 substrate-scope rows.
t2 = [
    (1, "Me", "n-C4H9", "1a", "2a", "A", 10, 81, ">99/1"),
    (2, "n-C6H13", "n-C4H9", "1b", "2b", "A", 10, 89, "99/1"),
    (3, "i-C4H9", "n-C4H9", "1c", "2c", "A", 4.5, 88, ">99/1"),
    (4, "n-hexynyl", "n-C4H9", "1d", "2d", "A", 6, 76, "97/3"),
    (5, "Ph", "n-C4H9", "1e", "2e", "A", 9, 74, "92/8"),
    (6, "Ph", "n-C4H9", "1e", "2e", "B", 8, 92, ">99/1"),
    (7, "Ph", "n-C4H9", "1e", "2e", "B", 9, 88, ">99/1"),
    (8, "Ph", "Allyl", "1f", "2f", "B", 4.5, 65, "99/1"),
    (9, "Me", "Ph", "1g", "2g", "B", 12, 75, "98/2"),
    (10, "p-MeOC6H4", "Ph", "1h", "2h", "B", 12, 80, "96/4"),
    (11, "Ph", "H", "1i", "2i", "B", 2.5, 53, ">99/1"),
    (12, "p-ClC6H4", "H", "1j", "2j", "B", 1.5, 49, ">99/1"),
]
for n, r1, r2, sublab, prodlab, cond, time, yld, ratio in t2:
    is_1a = sublab == "1a"
    is_1e = sublab == "1e"
    scale = 4 if n == 7 else (0.5 if cond == "A" else 1)
    cat = "Rh(PPh3)3Cl" if cond == "A" else "Rh(CO)(PPh3)2Cl"
    catload = 1 if cond == "A" or n == 7 else 2
    volume = 3 if cond == "A" else 6
    parts = [
        participant("substrate", "reactant", sublab, 3, f"{sublab} (R1={r1}, R2={r2})", SMILES_1A if is_1a else (SMILES_1E if is_1e else None), [amount("reaction_scale", scale, "mmol", 3)]),
        participant("product", "product", f"E-{prodlab}", 3, f"E-{prodlab} (R1={r1}, R2={r2})", SMILES_E2A if is_1a else (SMILES_E2E if is_1e else None)),
        participant("catalyst", "catalyst", cat, 3, amounts=[amount("catalyst_loading", catload, "mol%", 3)]),
        participant("solvent", "solvent", "toluene", 3, smiles="Cc1ccccc1", amounts=[amount("volume", volume, "mL", 3)]),
    ]
    if cond == "A":
        parts.append(participant("added_ligand", "reagent", "PPh3", 3, smiles="P(c1ccccc1)(c1ccccc1)c1ccccc1", amounts=[amount("ligand_loading", 3, "mol%", 3)]))
    unresolved = ["No SI was supplied or explicitly associated.", "Atmosphere, workup and purification are not reported in the table.", "R-group-derived connectivity and stereochemistry remain machine-unverified."]
    if n == 7:
        unresolved.append("Footnote d changes scale and catalyst loading; the table does not explicitly state whether the 6 mL solvent volume was scaled.")
    records.append(record(
        f"table2_entry{n}_{prodlab}", 3, "substrate_scope_entry", parts,
        steps=[{"step_id": "isomerization", "participant_ids": [p["entity_id"] for p in parts if p["role"] != "product"],
                "conditions": [field("temperature", {"number": 120, "unit": "°C"}, 3), field("time", {"number": time, "unit": "h"}, 3), field("solvent", "toluene", 3)] + missing_conditions()}],
        outcomes=[field("isolated_yield", {"number": yld, "unit": "%"}, 3, ["product"]), field("yield_measurement_basis", "isolated yield", 3), field("E_Z_ratio_before_silica_chromatography", ratio, 3, ["product"])],
        unresolved=unresolved,
    ))

# Page 3 Scheme 3 Au comparison values are marked ref. 16 and retained as cited literature examples.
au_rows = [
    ("1a", "2a", "Me", "n-C4H9", 24, 63, "96/4", 28, SMILES_1A, SMILES_E2A),
    ("1e", "2e", "Ph", "n-C4H9", 19, 30, "58/42", 70, SMILES_1E, SMILES_E2E),
    ("1i", "2i", "Ph", "H", 5, 91, "95/5", 0, None, None),
]
for sublab, prodlab, r1, r2, time, yld, ratio, recovery, ssmiles, psmiles in au_rows:
    parts = [
        participant("substrate", "reactant", sublab, 3, f"{sublab} (R1={r1}, R2={r2})", ssmiles, [amount("reaction_scale", 0.5, "mmol", 3)]),
        participant("product", "product", prodlab, 3, f"{prodlab} under Au protocol", psmiles),
        participant("au_catalyst", "catalyst", "Au(X-Phos)NTf2", 3, amounts=[amount("catalyst_loading", 1, "mol%", 3)]),
        participant("solvent", "solvent", "CH2Cl2", 3, smiles="ClCCl", amounts=[amount("volume", 2, "mL", 3)]),
    ]
    records.append(record(
        f"scheme3_au_ref16_{sublab}", 3, "literature_example", parts,
        steps=[{"step_id": "au_protocol", "participant_ids": ["substrate", "au_catalyst", "solvent"], "conditions": [field("temperature", "r.t.", 3), field("time", {"number": time, "unit": "h"}, 3), field("solvent", "CH2Cl2", 3)]}],
        outcomes=[field("reported_yield", {"number": yld, "unit": "%"}, 3, ["product"]), field("yield_measurement_basis", None, None), field("E_Z_ratio", ratio, 3, ["product"]), field("recovered_starting_material_yield", {"number": recovery, "unit": "%"}, 3, ["substrate"])],
        unresolved=["Scheme 3 labels these Au data as protocol ref. 16; they are classified as cited literature examples, not experiments newly established by this paper.", "Yield measurement basis is not stated in the comparison table."],
    ))

# Page 3 Scheme 3 eq 4: E/Z mixture heating test.
parts = [
    participant("input_E_2e", "reactant", "E-2e", 3, smiles=SMILES_E2E),
    participant("input_Z_2e", "reactant", "Z-2e", 3),
    participant("output_E_2e", "product", "E-2e after heating", 3, smiles=SMILES_E2E),
    participant("output_Z_2e", "product", "Z-2e after heating", 3),
    participant("catalyst", "catalyst", "Rh(CO)(PPh3)2Cl", 3, amounts=[amount("catalyst_loading", 2, "mol%", 3)]),
    participant("solvent", "solvent", "toluene", 3, smiles="Cc1ccccc1"),
]
records.append(record(
    "scheme3_eq4_EZ_heating_test", 3, "reported_experiment", parts,
    steps=[{"step_id": "heat_EZ_mixture", "participant_ids": ["input_E_2e", "input_Z_2e", "catalyst", "solvent"], "conditions": [field("temperature", {"number": 120, "unit": "°C"}, 3), field("time", {"number": 5, "unit": "h"}, 3), field("solvent", "toluene", 3)] + missing_conditions()}],
    outcomes=[field("initial_E_Z_ratio", "59/41", 3, ["input_E_2e", "input_Z_2e"]), field("final_E_Z_ratio", "64/36", 3, ["output_E_2e", "output_Z_2e"]), field("product_yield", None, None, ["output_E_2e", "output_Z_2e"])],
    unresolved=["Reaction scale, solvent volume, product yield, atmosphere, workup and purification are not reported.", "No SI was supplied or explicitly associated."],
))

# Page 4 Scheme 4 scope extensions.
scheme4 = [
    ("eq5_1k_E2k", "1k", "E-2k", "A", 8, 81, ">99/1"),
    ("eq6_1l_E2l", "1l", "E-2l", "B", 5, 77, "96/4"),
]
for suffix, sublab, prodlab, cond, time, yld, ratio in scheme4:
    cat = "Rh(PPh3)3Cl" if cond == "A" else "Rh(CO)(PPh3)2Cl"
    parts = [participant("substrate", "reactant", sublab, 4), participant("product", "product", prodlab, 4),
             participant("catalyst", "catalyst", cat, 4, amounts=[amount("catalyst_loading", 1 if cond == "A" else 2, "mol%", 4)]),
             participant("solvent", "solvent", "toluene", 4, smiles="Cc1ccccc1", amounts=[amount("volume", 3 if cond == "A" else 6, "mL", 4)])]
    if cond == "A":
        parts.append(participant("added_ligand", "reagent", "PPh3", 4, smiles="P(c1ccccc1)(c1ccccc1)c1ccccc1", amounts=[amount("ligand_loading", 3, "mol%", 4)]))
    records.append(record(
        f"scheme4_{suffix}", 4, "substrate_scope_entry", parts,
        steps=[{"step_id": "isomerization", "participant_ids": [p["entity_id"] for p in parts if p["role"] != "product"], "conditions": [field("temperature", {"number": 120, "unit": "°C"}, 4), field("time", {"number": time, "unit": "h"}, 4), field("solvent", "toluene", 4)] + missing_conditions()}],
        outcomes=[field("reported_yield", {"number": yld, "unit": "%"}, 4, ["product"]), field("yield_measurement_basis", None, None), field("E_Z_ratio", ratio, 4, ["product"])],
        unresolved=["Yield measurement basis, atmosphere, workup and purification are not stated in Scheme 4.", "No SI was supplied or explicitly associated.", "The depicted structures remain machine-unverified."],
    ))

parts = [participant("substrate", "reactant", "1m", 4, "2-methyl-3-phenylpenta-2,3-dienyl acetate"), participant("product", "product", "E-2m", 4),
         participant("catalyst", "catalyst", "Rh(PPh3)3Cl", 4, amounts=[amount("catalyst_loading", 5, "mol%", 4)]),
         participant("added_ligand", "reagent", "PPh3", 4, smiles="P(c1ccccc1)(c1ccccc1)c1ccccc1", amounts=[amount("ligand_loading", 15, "mol%", 4)]),
         participant("solvent", "solvent", "toluene", 4, smiles="Cc1ccccc1")]
records.append(record(
    "scheme4_eq7_1m_E2m", 4, "substrate_scope_entry", parts,
    steps=[{"step_id": "isomerization", "participant_ids": ["substrate", "catalyst", "added_ligand", "solvent"], "conditions": [field("temperature", {"number": 120, "unit": "°C"}, 4), field("time", {"number": 22, "unit": "h"}, 4), field("solvent", "toluene", 4)] + missing_conditions()}],
    outcomes=[field("reported_yield", {"number": 43, "unit": "%"}, 4, ["product"]), field("yield_measurement_basis", None, None), field("E_Z_ratio", None, None, ["product"])],
    unresolved=["Reaction scale, solvent volume, yield basis, E/Z ratio, atmosphere, workup and purification are not reported.", "No SI was supplied or explicitly associated."],
))

# Page 4 Scheme 5: one 1n experiment and two distinct 1o condition rows.
parts = [participant("substrate", "reactant", "1n", 4, "6-propyl-6,7-pentadecadien-5-yl acetate"),
         participant("product_EZ", "product", "5(E),7(Z)-2n", 4, "6-propyl-5(E),7(Z)-pentadecadien-7-yl acetate"),
         participant("product_EE", "product", "5(E),7(E)-2n", 4, "6-propyl-5(E),7(E)-pentadecadien-7-yl acetate"),
         participant("catalyst", "catalyst", "Rh(PPh3)2(CO)Cl", 4, amounts=[amount("catalyst_loading", 2, "mol%", 4)]),
         participant("solvent", "solvent", "toluene", 4, smiles="Cc1ccccc1")]
records.append(record(
    "scheme5_1n", 4, "substrate_scope_entry", parts,
    steps=[{"step_id": "isomerization", "participant_ids": ["substrate", "catalyst", "solvent"], "conditions": [field("temperature", {"number": 120, "unit": "°C"}, 4), field("time", {"number": 12, "unit": "h"}, 4), field("solvent", "toluene", 4)] + missing_conditions()}],
    outcomes=[field("combined_reported_yield", {"number": 69, "unit": "%"}, 4, ["product_EZ", "product_EE"]), field("yield_measurement_basis", None, None), field("EZ_EE_ratio", "68/32", 4, ["product_EZ", "product_EE"])],
    unresolved=["Reaction scale, solvent volume, yield basis, atmosphere, workup and purification are not reported.", "No SI was supplied or explicitly associated."],
))

for suffix, solvent, temp, time, yld, ratio, recovery in [
    ("toluene_120C", "toluene", 120, 12, 37, "88.5/11.5", 58),
    ("trimethylbenzene_160C", "1,3,5-trimethylbenzene", 160, 10, 59, "87.5/12.5", 0),
]:
    parts = [participant("substrate", "reactant", "1o", 4, "3-butyl-1-phenyl-1,2-nonadien-4-yl acetate"),
             participant("product_ZE", "product", "1(Z),3(E)-2o", 4), participant("product_EE", "product", "1(E),3(E)-2o", 4),
             participant("catalyst", "catalyst", "Rh(PPh3)2(CO)Cl", 4, amounts=[amount("catalyst_loading", 2, "mol%", 4)]),
             participant("solvent", "solvent", solvent, 4, smiles="Cc1ccccc1" if solvent == "toluene" else "Cc1cc(C)cc1C")]
    records.append(record(
        f"scheme5_1o_{suffix}", 4, "optimization_entry", parts,
        steps=[{"step_id": "isomerization", "participant_ids": ["substrate", "catalyst", "solvent"], "conditions": [field("temperature", {"number": temp, "unit": "°C"}, 4), field("time", {"number": time, "unit": "h"}, 4), field("solvent", solvent, 4)] + missing_conditions()}],
        outcomes=[field("combined_reported_yield", {"number": yld, "unit": "%"}, 4, ["product_ZE", "product_EE"]), field("yield_measurement_basis", None, None), field("ZE_EE_ratio", ratio, 4, ["product_ZE", "product_EE"]), field("recovered_starting_material_yield", {"number": recovery, "unit": "%"}, 4, ["substrate"])],
        unresolved=["Reaction scale, solvent volume, yield basis, atmosphere, workup and purification are not reported.", "No SI was supplied or explicitly associated."],
    ))

# Page 4 Scheme 6 synthetic applications: three independent arrows.
scheme6_common = participant("substrate", "reactant", "E-2e", 4, "3-butyl-4-phenyl-1,3(E)-butadien-2-yl acetate", SMILES_E2E)
parts = [scheme6_common, participant("product", "product", "E-5", 4, "3-butyl-4-phenyl-3(E)-buten-2-one", "CC(=O)/C(CCCC)=C/c1ccccc1"),
         participant("lioh", "reagent", "LiOH·H2O", 4, amounts=[amount("equivalents", 1.6, "equiv", 4)]),
         participant("solvent_mix", "solvent", "EtOH/H2O/THF = 1/1/1", 4)]
records.append(record(
    "scheme6_hydrolysis_E5", 4, "reported_experiment", parts,
    steps=[{"step_id": "hydrolysis", "participant_ids": ["substrate", "lioh", "solvent_mix"], "conditions": [field("temperature", {"number": 80, "unit": "°C"}, 4), field("time", {"number": 5, "unit": "h"}, 4), field("solvent", "EtOH/H2O/THF = 1/1/1", 4)] + missing_conditions()}],
    outcomes=[field("reported_yield", {"number": 75, "unit": "%"}, 4, ["product"]), field("yield_measurement_basis", None, None)],
    unresolved=["Reaction scale, total solvent volume, yield basis, atmosphere, workup and purification are not reported.", "No SI was supplied or explicitly associated."],
))

parts = [participant("substrate", "reactant", "E-2e", 4, "3-butyl-4-phenyl-1,3(E)-butadien-2-yl acetate", SMILES_E2E),
         participant("product", "product", "E-6", 4, "3-butyl-1-iodo-4-phenyl-3(E)-buten-2-one", "ICC(=O)/C(CCCC)=C/c1ccccc1"),
         participant("nis", "reagent", "NIS", 4, amounts=[amount("equivalents", 1.5, "equiv", 4)]),
         participant("solvent", "solvent", "1,4-dioxane", 4, smiles="O1CCOCC1")]
records.append(record(
    "scheme6_iodination_E6", 4, "reported_experiment", parts,
    steps=[{"step_id": "iodination", "participant_ids": ["substrate", "nis", "solvent"], "conditions": [field("temperature", {"number": 80, "unit": "°C"}, 4), field("time", {"number": 3, "unit": "h"}, 4), field("solvent", "1,4-dioxane", 4)] + missing_conditions()}],
    outcomes=[field("reported_yield", {"number": 77, "unit": "%"}, 4, ["product"]), field("yield_measurement_basis", None, None)],
    unresolved=["Reaction scale, solvent volume, yield basis, atmosphere, workup and purification are not reported.", "No SI was supplied or explicitly associated."],
))

parts = [participant("substrate", "reactant", "E-2e", 4, "3-butyl-4-phenyl-1,3(E)-butadien-2-yl acetate", SMILES_E2E),
         participant("product", "product", "7", 4, "dimethyl 5-acetoxy-3-butyl-4-phenylcyclohexa-1,3-diene-1,2-dicarboxylate"),
         participant("dmad", "reagent", "DMAD", 4, "dimethyl acetylenedicarboxylate", "COC(=O)C#CC(=O)OC", [amount("equivalents", 5, "equiv", 4)]),
         participant("hydroquinone", "reagent", "hydroquinone", 4, smiles="Oc1ccc(O)cc1", amounts=[amount("reagent_loading", 14, "mol%", 4)]),
         participant("solvent", "solvent", "xylene", 4)]
records.append(record(
    "scheme6_diels_alder_product7", 4, "reported_experiment", parts,
    steps=[{"step_id": "diels_alder", "participant_ids": ["substrate", "dmad", "hydroquinone", "solvent"], "conditions": [field("temperature", {"number": 150, "unit": "°C"}, 4), field("time", {"number": 12, "unit": "h"}, 4), field("solvent", "xylene", 4)] + missing_conditions()}],
    outcomes=[field("reported_yield", {"number": 60, "unit": "%"}, 4, ["product"]), field("yield_measurement_basis", None, None)],
    unresolved=["Reaction scale, solvent volume, xylene isomer, yield basis, atmosphere, workup and purification are not reported.", "No SI was supplied or explicitly associated."],
))

OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"output": str(OUT.relative_to(ROOT)), "records": len(records)}, ensure_ascii=False))
