import json
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
DOC = "doc_920ad7ba402389e1"


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


def participant(entity_id, role, label, name, evidence, smiles=None, amounts=None):
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


def amount(name, number, unit, evidence, raw_text=None):
    value = {"number": number, "unit": unit}
    if raw_text:
        value["raw_text"] = raw_text
    return field(name, value, evidence)


def missing_conditions():
    return [field("atmosphere", None, []), field("workup", None, []), field("purification", None, [])]


def record(rid, kind, evidence, participants, steps, outcomes, notes=None, unresolved=None):
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
        "notes": [fact(x, evidence) for x in (notes or [])],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved or [],
        },
    }


SMILES = {
    "1a": "C=C=CCN(CC=C=C)S(=O)(=O)c1ccc(C)cc1",
    "1b": "C=C=CCN(CC=C=C)c1ccccc1",
    "1c": "COC(=O)C(CC=C=C)(CC=C=C)C(=O)OC",
    "BnNH2": "NCc1ccccc1",
    "p-MeOBnNH2": "COc1ccc(CN)cc1",
    "n-BuNH2": "CCCCN",
    "n-HexNH2": "CCCCCCN",
    "cyclopropylamine": "NC1CC1",
    "phenethylamine": "NCCc1ccccc1",
    "PhI": "Ic1ccccc1",
    "4-MePhI": "Cc1ccc(I)cc1",
    "3-MePhI": "Cc1cccc(I)c1",
    "3,4-Me2PhI": "Cc1ccc(I)cc1C",
    "4-ClPhI": "Clc1ccc(I)cc1",
    "4-BrPhI": "Brc1ccc(I)cc1",
    "3-BrPhI": "Brc1cccc(I)c1",
    "4-FPhI": "Fc1ccc(I)cc1",
    "4-EtOOCPhI": "CCOC(=O)c1ccc(I)cc1",
    "4-MeOPhI": "COc1ccc(I)cc1",
    "4-PhPhI": "Ic1ccc(-c2ccccc2)cc1",
    "DMF": "CN(C)C=O",
    "CH3CN": "CC#N",
    "THF": "C1CCOC1",
    "toluene": "Cc1ccccc1",
    "dioxane": "O1CCOCC1",
}


def p(entity_id, role, label, name, evidence, smiles_key=None, amounts=None):
    return participant(entity_id, role, label, name, evidence, SMILES.get(smiles_key), amounts)


records = []

# Page 1 graphical abstract is a generic reaction family, not an individual batch.
e1 = ev(1)
records.append(record(
    "graphical_abstract_general_reaction", "general_scheme", e1,
    [
        participant("generic_bisallene", "reactant", "1,5-bisallene", "generic 1,5-bisallene (Z = TsN, PhN, or C(CO2R)2)", e1),
        participant("generic_primary_amine", "reactant", "R1NH2", "generic primary amine", e1),
        participant("generic_organic_iodide", "reactant", "R2I", "generic organic iodide", e1),
        participant("generic_ten_membered_product", "product", "graphical-abstract product", "generic stereodefined ten-membered cyclic product", e1),
    ], [], [],
    notes=["Graphical abstract depicts the reaction class and shared standard conditions; it is not a separately reported batch experiment."],
    unresolved=["R-group structures are generic and therefore have no complete SMILES."]
))

# Page 2 Scheme 1 is a proposed pathway space, not a reported experiment.
e2 = ev(2)
records.append(record(
    "scheme1_possible_pathways", "mechanism", e2, [], [], [],
    notes=["Scheme 1 compares a literature-type monoallene carbopalladation/allylation with proposed bisallene intermediates Int-I to Int-III and possible products A-F."],
    unresolved=["Generic R, R', X, Nu, and ligand substituents preclude fully specified structures."]
))


def table1_participants(entry, catalyst, additive, solvent, ligand=None, ligand_loading=None):
    evidence = list(dict.fromkeys(e2 + ev(3))) if entry == 1 else ev(3)
    items = [
        p("t1_1a", "reactant", "1a", "bis(2,3-butadienyl)tosylamide", evidence, "1a", [amount("concentration", 0.1, "M", evidence)]),
        p("t1_benzylamine", "reactant", "BnNH2 (2a in Table 1 scheme)", "benzylamine", evidence, "BnNH2", [amount("equivalents", 1.0, "equiv", evidence)]),
        p("t1_phenyliodide", "reactant", "PhI (3a in Table 1 scheme)", "iodobenzene", evidence, "PhI", [amount("equivalents", 3.0, "equiv", evidence)]),
        participant("t1_catalyst", "catalyst", catalyst, catalyst, evidence, None, [amount("catalyst_loading", 5, "mol%", evidence)]),
        participant("t1_base_or_additive", "reagent", additive[0], additive[1], evidence, None, [amount("equivalents", additive[2], "equiv", evidence)]),
        p("t1_solvent", "solvent", solvent, solvent, evidence, solvent),
        participant("t1_4a", "product", "4a", "ten-membered cyclization product 4a", evidence),
    ]
    if ligand:
        items.append(participant("t1_ligand", "unspecified_agent", ligand, ligand, evidence, None, [amount("ligand_loading", ligand_loading, "mol%", evidence)]))
    if entry >= 13:
        items.append(participant("t1_ag3po4", "reagent", "Ag3PO4", "silver phosphate", evidence, None, [amount("equivalents", 0.7, "equiv", evidence)]))
    return evidence, items


t1_rows = [
    (1, "Pd(PPh3)4", ("K2CO3", "potassium carbonate", 1.0), "DMF", 10, 35, 0, None, None),
    (2, "Pd(PPh3)4", ("K2CO3", "potassium carbonate", 1.0), "CH3CN", 16.5, 28, 30, None, None),
    (3, "Pd(PPh3)4", ("K2CO3", "potassium carbonate", 1.0), "THF", 10, "not detected", 48, None, None),
    (4, "Pd(PPh3)4", ("K2CO3", "potassium carbonate", 1.0), "toluene", 17, "not detected", 60, None, None),
    (5, "Pd(PPh3)4", ("K2CO3", "potassium carbonate", 1.0), "dioxane", 22, "not detected", 45, None, None),
    (6, "Pd(dba)2", ("K2CO3", "potassium carbonate", 1.0), "DMF", 10, "not detected", 0, "2,2'-bipyridine (L)", 10),
    (7, "Pd(dba)2", ("K2CO3", "potassium carbonate", 1.0), "DMF", 10, 17, 0, "PPh3", 10),
    (8, "Pd(dba)2", ("K2CO3", "potassium carbonate", 1.0), "DMF", 10, "not detected", 0, "IPr", 6),
    (9, "Pd(PPh3)4", ("Ag3PO4", "silver phosphate", 0.7), "DMF", 10, 36, 0, None, None),
    (10, "Pd(PPh3)4", ("Ag2CO3", "silver carbonate", 1.0), "DMF", 10, "not detected", 25, None, None),
    (11, "Pd(PPh3)4", ("AgNO3", "silver nitrate", 2.0), "DMF", 10, "not detected", 0, None, None),
    (12, "Pd(PPh3)4", ("AgOAc", "silver acetate", 2.0), "DMF", 10, "not detected", 0, None, None),
    (13, "Pd(PPh3)4", ("K2CO3", "potassium carbonate", 1.0), "DMF", 10.5, 28, 0, None, None),
    (14, "Pd(PPh3)4", ("Cs2CO3", "cesium carbonate", 1.0), "DMF", 10, "not detected", 0, None, None),
    (15, "Pd(PPh3)4", ("K3PO4", "potassium phosphate", 1.0), "DMF", 10, 45, 0, None, None),
    (16, "Pd(PPh3)4", ("Na3PO4", "sodium phosphate", 1.0), "DMF", 10, 32, 0, None, None),
]

for entry, catalyst, additive, solvent, hours, yld, recovery, ligand, ligand_loading in t1_rows:
    evidence, parts = table1_participants(entry, catalyst, additive, solvent, ligand, ligand_loading)
    temp = "reflux" if entry in (2, 3) else {"number": 90, "unit": "°C"}
    outcomes = [
        field("product_yield_by_1H_NMR", yld if isinstance(yld, str) else {"number": yld, "unit": "%"}, evidence, ["t1_4a"]),
        field("yield_measurement_basis", "1H NMR with mesitylene as internal standard", evidence, ["t1_4a"]),
        field("recovered_starting_material_yield", {"number": recovery, "unit": "%"}, evidence, ["t1_1a"]),
    ]
    notes = []
    if entry == 1:
        notes.append("The prose reports exclusive formation of 4a and no B-F regio-/stereoisomers observed under this condition.")
        notes.append("The page-2 prose calls phenyl iodide 2a and benzylamine 3a, whereas the page-3 Table 1 reaction drawing labels BnNH2 as 2a and PhI as 3a; the scheme labels are retained and the discrepancy is unresolved.")
    if entry == 15:
        outcomes += [
            field("isolated_product_yield", {"number": 43, "unit": "%"}, evidence, ["t1_4a"]),
            field("stereoselectivity_observation", "only one stereoisomer in the crude reaction mixture", evidence, ["t1_4a"]),
        ]
    row_unresolved = ["Product structure candidate is not encoded because stereochemical detail requires dedicated structure review.", "Atmosphere, workup, and purification are not reported in the supplied main text; SI was not provided."]
    if entry == 1:
        row_unresolved.append("Compound-number assignment is reversed between the page-2 prose and page-3 Table 1 drawing (benzylamine/iodobenzene 2a/3a).")
    records.append(record(
        f"table1_entry{entry}", "optimization_entry", evidence, parts,
        [{"step_id": "cyclization", "participant_ids": [x["entity_id"] for x in parts if x["role"] != "product"],
          "conditions": [field("solvent", solvent, evidence), field("temperature", temp, evidence),
                         field("time", {"number": hours, "unit": "h"}, evidence)] + missing_conditions()}],
        outcomes, notes=notes,
        unresolved=row_unresolved
    ))


amine_rows = [
    (1, "Bn (2a)", "benzylamine", "BnNH2", 1.0, 43, "4a"),
    (2, "p-MeOC6H4CH2 (2b)", "4-methoxybenzylamine", "p-MeOBnNH2", 1.0, 35, "4b"),
    (3, "n-C4H9 (2c)", "n-butylamine", "n-BuNH2", 2.0, 49, "4c"),
    (4, "n-C6H13 (2d)", "n-hexylamine", "n-HexNH2", 1.0, 62, "4d"),
    (5, "cyclopropyl (2e)", "cyclopropylamine", "cyclopropylamine", 2.0, 48, "4e"),
    (6, "C6H5CH2CH2 (2f)", "2-phenylethylamine", "phenethylamine", 1.0, 56, "4f"),
]
e3 = ev(3)
for entry, label, amine_name, smiles_key, amine_equiv, yld, product_label in amine_rows:
    evidence = e3 + (e2 if entry == 1 else [])
    if entry == 2:
        evidence += ev(4)
    evidence = list(dict.fromkeys(evidence))
    parts = [
        p("t2_1a", "reactant", "1a", "bis(2,3-butadienyl)tosylamide", evidence, "1a", [amount("concentration", 0.1, "M", evidence)]),
        p("t2_amine", "reactant", label, amine_name, evidence, smiles_key, [amount("equivalents", amine_equiv, "equiv", evidence)]),
        p("t2_phi", "reactant", "PhI (3a in Table 2 scheme)", "iodobenzene", evidence, "PhI", [amount("equivalents", 3.0, "equiv", evidence)]),
        participant("t2_pd", "catalyst", "Pd(PPh3)4", "tetrakis(triphenylphosphine)palladium(0)", evidence, None, [amount("catalyst_loading", 5, "mol%", evidence)]),
        participant("t2_k3po4", "reagent", "K3PO4", "potassium phosphate", evidence, None, [amount("equivalents", 1.0, "equiv", evidence)]),
        participant("t2_ag3po4", "reagent", "Ag3PO4", "silver phosphate", evidence, None, [amount("equivalents", 0.7, "equiv", evidence)]),
        p("t2_dmf", "solvent", "DMF", "N,N-dimethylformamide", evidence, "DMF"),
        participant("t2_product", "product", product_label, f"ten-membered cyclization product {product_label}", evidence),
    ]
    notes = ["Preparation was reported as reproduced by Y. Qiu."] if entry == 2 else []
    records.append(record(
        f"table2_entry{entry}", "substrate_scope_entry", evidence, parts,
        [{"step_id": "cyclization", "participant_ids": [x["entity_id"] for x in parts if x["role"] != "product"],
          "conditions": [field("solvent", "DMF", evidence), field("temperature", {"number": 90, "unit": "°C"}, evidence),
                         field("time", {"number": 10, "unit": "h"}, evidence)] + missing_conditions()}],
        [field("isolated_product_yield", {"number": yld, "unit": "%"}, evidence, ["t2_product"]),
         field("yield_measurement_basis", "isolated product", evidence, ["t2_product"])],
        notes=notes,
        unresolved=["Product structure candidate is not encoded because stereochemical detail requires dedicated structure review.", "Atmosphere, workup, and purification are not reported in the supplied main text; SI was not provided."]
    ))


table3_rows = [
    (1, "1a", "TsN", "n-C6H13 (2d)", "n-hexylamine", "n-HexNH2", 1.0, "4-Me (3b)", "4-iodotoluene", "4-MePhI", 16, 50, "4g"),
    (2, "1a", "TsN", "n-C6H13 (2d)", "n-hexylamine", "n-HexNH2", 1.0, "3-Me (3c)", "3-iodotoluene", "3-MePhI", 10, 53, "4h"),
    (3, "1a", "TsN", "n-C6H13 (2d)", "n-hexylamine", "n-HexNH2", 1.0, "3,4-Me2 (3d)", "1-iodo-3,4-dimethylbenzene", "3,4-Me2PhI", 10, 61, "4i"),
    (4, "1a", "TsN", "n-C6H13 (2d)", "n-hexylamine", "n-HexNH2", 1.0, "4-Cl (3e)", "1-chloro-4-iodobenzene", "4-ClPhI", 10, 59, "4j"),
    (5, "1a", "TsN", "n-C6H13 (2d)", "n-hexylamine", "n-HexNH2", 1.0, "4-Br (3f)", "1-bromo-4-iodobenzene", "4-BrPhI", 10, 51, "4k"),
    (6, "1a", "TsN", "n-C6H13 (2d)", "n-hexylamine", "n-HexNH2", 1.0, "3-Br (3g)", "1-bromo-3-iodobenzene", "3-BrPhI", 10, 54, "4l"),
    (7, "1a", "TsN", "n-C6H13 (2d)", "n-hexylamine", "n-HexNH2", 1.0, "4-F (3h)", "1-fluoro-4-iodobenzene", "4-FPhI", 10, 61, "4m"),
    (8, "1a", "TsN", "n-C6H13 (2d)", "n-hexylamine", "n-HexNH2", 1.0, "4-EtOOC (3i)", "ethyl 4-iodobenzoate", "4-EtOOCPhI", 10, 51, "4n"),
    (9, "1a", "TsN", "n-C6H13 (2d)", "n-hexylamine", "n-HexNH2", 1.0, "4-MeO (3j)", "4-iodoanisole", "4-MeOPhI", 10, 44, "4o"),
    (10, "1a", "TsN", "n-C6H13 (2d)", "n-hexylamine", "n-HexNH2", 1.0, "4-C6H5 (3k)", "4-iodobiphenyl", "4-PhPhI", 9.5, 42, "4p"),
    (11, "1a", "TsN", "n-C4H9 (2c)", "n-butylamine", "n-BuNH2", 2.0, "4-Br (3f)", "1-bromo-4-iodobenzene", "4-BrPhI", 10, 54, "4q"),
    (12, "1a", "TsN", "Bn (2a)", "benzylamine", "BnNH2", 1.0, "4-Br (3f)", "1-bromo-4-iodobenzene", "4-BrPhI", 8, 45, "4r"),
    (13, "1b", "PhN", "n-C6H13 (2d)", "n-hexylamine", "n-HexNH2", 1.0, "4-EtOOC (3i)", "ethyl 4-iodobenzoate", "4-EtOOCPhI", 10, 38, "4s"),
    (14, "1c", "C(CO2Me)2", "n-C6H13 (2d)", "n-hexylamine", "n-HexNH2", 1.0, "H (3a)", "iodobenzene", "PhI", 10, 33, "4t"),
    (15, "1c", "C(CO2Me)2", "n-C6H13 (2d)", "n-hexylamine", "n-HexNH2", 1.0, "4-Br (3f)", "1-bromo-4-iodobenzene", "4-BrPhI", 10, 40, "4u"),
]
e4 = ev(4)
for entry, substrate_label, z_label, amine_label, amine_name, amine_smiles, amine_equiv, aryl_label, aryl_name, aryl_smiles, hours, yld, product_label in table3_rows:
    evidence = list(dict.fromkeys(e3 + e4 + (e2 if entry == 15 else [])))
    parts = [
        p("t3_bisallene", "reactant", f"{substrate_label} (Z = {z_label})", f"1,5-bisallene {substrate_label}", evidence, substrate_label, [amount("concentration", 0.1, "M", evidence)]),
        p("t3_amine", "reactant", amine_label, amine_name, evidence, amine_smiles, [amount("equivalents", amine_equiv, "equiv", evidence)]),
        p("t3_aryliodide", "reactant", aryl_label, aryl_name, evidence, aryl_smiles, [amount("equivalents", 3.0, "equiv", evidence)]),
        participant("t3_pd", "catalyst", "Pd(PPh3)4", "tetrakis(triphenylphosphine)palladium(0)", evidence, None, [amount("catalyst_loading", 5, "mol%", evidence)]),
        participant("t3_k3po4", "reagent", "K3PO4", "potassium phosphate", evidence, None, [amount("equivalents", 1.0, "equiv", evidence)]),
        participant("t3_ag3po4", "reagent", "Ag3PO4", "silver phosphate", evidence, None, [amount("equivalents", 0.7, "equiv", evidence)]),
        p("t3_dmf", "solvent", "DMF", "N,N-dimethylformamide", evidence, "DMF"),
        participant("t3_product", "product", product_label, f"ten-membered cyclization product {product_label}", evidence),
    ]
    notes = ["Preparation was reported as reproduced by Y. Qiu."] if entry in (3, 8, 14) else []
    records.append(record(
        f"table3_entry{entry}", "substrate_scope_entry", evidence, parts,
        [{"step_id": "cyclization", "participant_ids": [x["entity_id"] for x in parts if x["role"] != "product"],
          "conditions": [field("solvent", "DMF", evidence), field("temperature", {"number": 90, "unit": "°C"}, evidence),
                         field("time", {"number": hours, "unit": "h"}, evidence)] + missing_conditions()}],
        [field("isolated_product_yield", {"number": yld, "unit": "%"}, evidence, ["t3_product"]),
         field("yield_measurement_basis", "isolated product", evidence, ["t3_product"])],
        notes=notes,
        unresolved=["Product structure candidate is not encoded because stereochemical detail requires dedicated structure review.", "Atmosphere, workup, and purification are not reported in the supplied main text; SI was not provided."]
    ))

# Page 4 Scheme 2 is a distinct gram-scale batch, not the same record as Table 2 entry 4.
parts = [
    p("scale_1a", "reactant", "1a", "bis(2,3-butadienyl)tosylamide", e4, "1a", [amount("mass", 1, "g", e4, "1 g scale")]),
    p("scale_2d", "reactant", "C6H13NH2 (2d)", "n-hexylamine", e4, "n-HexNH2", [amount("equivalents", 1.0, "equiv", e4)]),
    p("scale_3a", "reactant", "PhI (3a)", "iodobenzene", e4, "PhI", [amount("equivalents", 3.0, "equiv", e4)]),
    participant("scale_pd", "catalyst", "Pd(PPh3)4", "tetrakis(triphenylphosphine)palladium(0)", e4, None, [amount("catalyst_loading", 5, "mol%", e4)]),
    participant("scale_k3po4", "reagent", "K3PO4", "potassium phosphate", e4, None, [amount("equivalents", 1.0, "equiv", e4)]),
    participant("scale_ag3po4", "reagent", "Ag3PO4", "silver phosphate", e4, None, [amount("equivalents", 0.7, "equiv", e4)]),
    p("scale_dmf", "solvent", "DMF", "N,N-dimethylformamide", e4, "DMF"),
    participant("scale_4d", "product", "4d", "ten-membered cyclization product 4d", e4),
]
records.append(record(
    "scheme2_gram_scale_4d", "reported_experiment", e4, parts,
    [{"step_id": "gram_scale_cyclization", "participant_ids": [x["entity_id"] for x in parts if x["role"] != "product"],
      "conditions": [field("solvent", "DMF", e4), field("temperature", {"number": 90, "unit": "°C"}, e4),
                     field("time", {"number": 10, "unit": "h"}, e4)] + missing_conditions()}],
    [field("reported_product_yield", {"number": 62, "unit": "%"}, e4, ["scale_4d"]),
     field("yield_measurement_basis", None, [], ["scale_4d"])],
    unresolved=["The main text does not explicitly state the measurement basis for the 62% scale-up yield.", "Product structure candidate is not encoded because stereochemical detail requires dedicated structure review.", "Atmosphere, workup, and purification are not reported in the supplied main text; SI was not provided."]
))

records.append(record(
    "scheme3_selectivity_rationale", "mechanism", e4, [], [], [],
    notes=["Scheme 3 proposes anti-7, intermediate 8, and anti-9 followed by regioselective intermolecular and intramolecular allylic substitution to form product 4."],
    unresolved=["The pathway is mechanistic rationale rather than a directly reported batch experiment; generic substituents and Pd ligand are not fully specified."]
))

out = BASE / "raw_model" / "records_pages_0001_0004.json"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
print(f"wrote {len(records)} records to {out}")
