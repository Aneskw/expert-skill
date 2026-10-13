import json
from pathlib import Path

DOC = "doc_87efb2969bf767fc"
OUT = Path(__file__).with_name("records_pages_0001_0004.json")


def ev(page):
    return [f"{DOC}:page{page}:image", f"{DOC}:page{page}:text"]


def fact(value, evidence):
    return {
        "value": value,
        "evidence_ids": evidence if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def qty(number, unit, **extra):
    return {"number": number, "unit": unit, **extra}


def fld(name, value, evidence, targets=None):
    result = {"name": name, "fact": fact(value, evidence)}
    if targets:
        result["target_entity_ids"] = targets
    return result


def participant(entity_id, role, label, name, evidence, smiles=None, amounts=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence),
        "smiles": fact(smiles, evidence) if smiles else fact(None, []),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": amounts or [],
    }


def rec(suffix, page, kind, participants, steps, outcomes, notes=None, unresolved=None, evidence=None):
    evidence = evidence or ev(page)
    return {
        "record_id": f"{DOC}:{suffix}",
        "document_id": DOC,
        "source_reaction_id": suffix,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": evidence,
        "participants": participants,
        "steps": steps,
        "outcomes": outcomes,
        "notes": [fact(x, evidence) for x in (notes or [])],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved or ["Supporting information was not provided or explicitly associated; operational details may be missing."],
        },
    }


def amount(name, number, unit, evidence):
    return fld(name, qty(number, unit), evidence)


def table1_participants(page, substrate, substrate_name, aldehyde, aldehyde_name, amine, amine_name, product):
    e = ev(page)
    amine_eq = 1.1 if amine in ("4", "5") else 1.25
    return [
        participant("substrate_1", "reactant", substrate, substrate_name, e, amounts=[amount("reaction_scale", 1.0, "mmol", e)]),
        participant("aldehyde_2", "reactant", aldehyde, aldehyde_name, e, amounts=[amount("equivalents", 1.8, "equiv", e)]),
        participant("chiral_amine", "reagent", amine, amine_name, e, amounts=[amount("equivalents", amine_eq, "equiv", e)]),
        participant("zinc_iodide", "catalyst", "ZnI2", "zinc iodide", e, "[Zn+2].[I-].[I-]", [amount("equivalents", 0.8, "equiv", e)]),
        participant("toluene", "solvent", None, "toluene", e, "Cc1ccccc1", [amount("volume", 3 if amine in ("4", "5") else 5, "mL", e)]),
        participant("product_3", "product", product, f"allene {product}", e),
    ]


records = []

# Page 1: the abstract graphic is a generic protocol, not an individual batch.
e = ev(1)
records.append(rec(
    "abstract_graphical_protocol", 1, "general_scheme",
    [
        participant("propargylic_alcohol_1", "reactant", "1", "terminal propargylic alcohol", e),
        participant("aldehyde_2", "reactant", "2", "aldehyde", e, amounts=[amount("equivalents", 1.1, "equiv", e)]),
        participant("pyrrolidine", "reactant", None, "pyrrolidine", e, "C1CCNC1", [amount("equivalents", 1.1, "equiv", e)]),
        participant("cubr", "catalyst", "CuBr", "copper(I) bromide", e, "[Cu]Br", [amount("loading", 5, "mol%", e)]),
        participant("ligand_9", "catalyst", "9", "(R,R)-N-PINAP", e, amounts=[amount("loading", 5.5, "mol%", e)]),
        participant("molecular_sieves", "reagent", "4 Å MS", "4 angstrom molecular sieves", e),
        participant("zinc_iodide", "catalyst", "ZnI2", "zinc iodide", e, "[Zn+2].[I-].[I-]", [amount("equivalents", 0.45, "equiv", e)]),
        participant("sodium_iodide", "reagent", "NaI", "sodium iodide", e, "[Na+].[I-]", [amount("equivalents", 0.5, "equiv", e)]),
        participant("toluene", "solvent", None, "toluene", e, "Cc1ccccc1"),
        participant("allenol_3", "product", "3", "axially chiral allenol", e),
    ],
    [
        {"step_id": "propargylic_amine_formation", "participant_ids": ["propargylic_alcohol_1", "aldehyde_2", "pyrrolidine", "cubr", "ligand_9", "molecular_sieves", "toluene"], "conditions": [fld("temperature", qty(25, "°C"), e), fld("solvent", "toluene", e)]},
        {"step_id": "copper_removal", "participant_ids": [], "conditions": [fld("operation", "removal of Cu(I) with filtration", e)]},
        {"step_id": "allene_formation", "participant_ids": ["zinc_iodide", "sodium_iodide", "toluene", "allenol_3"], "conditions": [fld("temperature", qty(110, "°C"), e), fld("solvent", "toluene", e)]},
    ], [],
    notes=["The graphical abstract gives a general two-stage protocol and R-group structures, not a single substrate-specific experiment."],
    unresolved=["R1/R2/R3 are generic substituents; no batch-specific time, yield, or full product structure is stated in this graphic."]
))

# Page 2 Scheme 1: conceptual alternatives only.
e = ev(2)
records.append(rec(
    "scheme1_conceptual_routes", 2, "general_scheme",
    [
        participant("terminal_alkyne_1", "reactant", "1", "terminal alkyne", e),
        participant("aldehyde_2", "reactant", "2", "aldehyde", e),
        participant("chiral_amine", "reagent", None, "chiral amine", e),
        participant("zinc_iodide", "catalyst", "ZnI2", "zinc iodide", e, "[Zn+2].[I-].[I-]"),
        participant("allene_3", "product", "3", "optically active 1,3-disubstituted allene", e),
    ],
    [{"step_id": "conceptual_routes", "participant_ids": ["terminal_alkyne_1", "aldehyde_2", "chiral_amine", "zinc_iodide", "allene_3"], "conditions": []}], [],
    notes=["Scheme 1 presents a chiral-amine route and a catalytic asymmetric propargylic-amine route as concepts."],
    unresolved=["The scheme is conceptual and supplies no batch-specific quantities, time, temperature, yield, or complete structures."]
))

# Page 2 Table 1: six independent optimization rows.
table1_rows = [
    (1, "1a", "terminal alkyne 1a (R = p-NO2C6H4CH2OCH2)", "2a", "pentanal (n-BuCHO)", "4", "methyl prolinate 4", "3aa", 37, 34, 12, 120, 16, "isolated"),
    (2, "1a", "terminal alkyne 1a (R = p-NO2C6H4CH2OCH2)", "2a", "pentanal (n-BuCHO)", "5", "prolinol 5", "3aa", "trace", None, 12, 120, 40, "isolated"),
    (3, "1a", "terminal alkyne 1a (R = p-NO2C6H4CH2OCH2)", "2a", "pentanal (n-BuCHO)", "6", "diphenyl-substituted prolinol 6", "3aa", 46, 98, 16, 120, 19, "isolated"),
    (4, "1a", "terminal alkyne 1a (R = p-NO2C6H4CH2OCH2)", "2a", "pentanal (n-BuCHO)", "6", "diphenyl-substituted prolinol 6", "3aa", 63, 94, 16, 130, 3, "isolated"),
    (5, "1b", "terminal alkyne 1b (R = n-C10H21)", "2b", "benzaldehyde", "6", "diphenyl-substituted prolinol 6", "3bb", 26, None, 12, 120, None, "NMR"),
    (6, "1c", "propargyl alcohol", "2c", "cyclohexanecarbaldehyde", "6", "diphenyl-substituted prolinol 6", "3cc", "trace", None, 12, 120, None, "isolated"),
]
for row, sub, subname, ald, aldname, amine, aminename, prod, yld, ee, time, temp, recovery, basis in table1_rows:
    e = ev(2)
    parts = table1_participants(2, sub, subname, ald, aldname, amine, aminename, prod)
    # Add source-supported candidates only where the condensed identity is unambiguous.
    smiles = {"2a": "CCCCC=O", "2b": "O=Cc1ccccc1", "2c": "O=CC1CCCCC1", "1b": "C#CCCCCCCCCCC", "1c": "C#CCO"}
    for p in parts:
        if p["label"]["value"] in smiles:
            p["smiles"] = fact(smiles[p["label"]["value"]], e)
    outcomes = [fld(f"{basis.lower()}_yield", "trace" if yld == "trace" else qty(yld, "%"), e, ["product_3"]), fld("yield_measurement_basis", basis, e, ["product_3"])]
    if ee is not None:
        outcomes.append(fld("enantiomeric_excess", qty(ee, "%"), e, ["product_3"]))
    else:
        outcomes.append(fld("enantiomeric_excess", None, [], ["product_3"]))
    if recovery is not None:
        outcomes.append(fld("recovered_starting_material_yield", qty(recovery, "%"), e, ["substrate_1"]))
    records.append(rec(
        f"table1_entry{row}", 2, "optimization_entry", parts,
        [{"step_id": "allene_formation", "participant_ids": [p["entity_id"] for p in parts], "conditions": [fld("temperature", qty(temp, "°C"), e), fld("time", qty(time, "h"), e), fld("solvent", "toluene", e)]}],
        outcomes,
        notes=["Table 1 selected example; table footnotes override the shared header where applicable."],
        unresolved=["Supporting information was not provided or explicitly associated; workup and purification are missing.", "The product/substrate structures are represented by labels and condensed R groups; stereochemical structure candidates are not independently verified."] + (["Enantiomeric excess was not determined by the authors."] if ee is None else [])
    ))

# Page 2 Scheme 2 racemic preparation.
e = ev(2)
records.append(rec(
    "scheme2_racemic_3dc", 2, "reported_experiment",
    [
        participant("phenylacetylene_1d", "reactant", "1d", "phenylacetylene", e, "C#Cc1ccccc1"),
        participant("aldehyde_2c", "reactant", "2c", "cyclohexanecarbaldehyde", e, "O=CC1CCCCC1", [amount("equivalents", 1.1, "equiv", e)]),
        participant("pyrrolidine", "reactant", None, "pyrrolidine", e, "C1CCNC1", [amount("equivalents", 1.1, "equiv", e)]),
        participant("cubr", "catalyst", "CuBr", "copper(I) bromide", e, "[Cu]Br", [amount("loading", 5, "mol%", e)]),
        participant("molecular_sieves", "reagent", "4 Å MS", "4 angstrom molecular sieves", e),
        participant("zinc_iodide", "catalyst", "ZnI2", "zinc iodide", e, "[Zn+2].[I-].[I-]", [amount("equivalents", 0.45, "equiv", e)]),
        participant("sodium_iodide", "reagent", "NaI", "sodium iodide", e, "[Na+].[I-]", [amount("equivalents", 0.5, "equiv", e)]),
        participant("toluene", "solvent", None, "toluene", e, "Cc1ccccc1"),
        participant("product_3dc", "product", "3dc", "racemic allene 3dc", e, "c1ccccc1C=C=CC1CCCCC1"),
    ],
    [
        {"step_id": "propargylic_amine_formation", "participant_ids": ["phenylacetylene_1d", "aldehyde_2c", "pyrrolidine", "cubr", "molecular_sieves", "toluene"], "conditions": [fld("temperature", qty(25, "°C"), e), fld("time", qty(11.5, "h"), e), fld("solvent", "toluene", e)]},
        {"step_id": "copper_removal", "participant_ids": [], "conditions": [fld("operation", "removal of Cu(I) with filtration", e)]},
        {"step_id": "allene_formation", "participant_ids": ["zinc_iodide", "sodium_iodide", "toluene", "product_3dc"], "conditions": [fld("temperature", qty(110, "°C"), e), fld("time", qty(7, "h"), e), fld("solvent", "toluene", e)]},
    ],
    [fld("isolated_yield", qty(57, "%"), e, ["product_3dc"]), fld("yield_measurement_basis", "isolated", e, ["product_3dc"])],
    unresolved=["Supporting information was not provided or explicitly associated; detailed filtration, workup, and purification are missing.", "The drawn allene structure was converted to a non-stereochemical candidate SMILES and remains unverified."]
))

# Page 3 Scheme 3 optically active 3dc.
e = ev(3)
records.append(rec(
    "scheme3_optically_active_r-3dc", 3, "reported_experiment",
    [
        participant("phenylacetylene_1d", "reactant", "1d", "phenylacetylene", e, "C#Cc1ccccc1"),
        participant("aldehyde_2c", "reactant", "2c", "cyclohexanecarbaldehyde", e, "O=CC1CCCCC1", [amount("equivalents", 1.1, "equiv", e)]),
        participant("pyrrolidine", "reactant", None, "pyrrolidine", e, "C1CCNC1", [amount("equivalents", 1.1, "equiv", e)]),
        participant("cubr", "catalyst", "CuBr", "copper(I) bromide", e, "[Cu]Br", [amount("loading", 5, "mol%", e)]),
        participant("ligand_9", "catalyst", "9", "(R,R)-N-PINAP", e, amounts=[amount("loading", 5.5, "mol%", e)]),
        participant("molecular_sieves", "reagent", "4 Å MS", "4 angstrom molecular sieves", e),
        participant("zinc_iodide", "catalyst", "ZnI2", "zinc iodide", e, "[Zn+2].[I-].[I-]", [amount("equivalents", 0.45, "equiv", e)]),
        participant("sodium_iodide", "reagent", "NaI", "sodium iodide", e, "[Na+].[I-]", [amount("equivalents", 0.5, "equiv", e)]),
        participant("toluene", "solvent", None, "toluene", e, "Cc1ccccc1"),
        participant("product_r-3dc", "product", "(R)-(−)-3dc", "optically active allene (R)-(−)-3dc", e, "c1ccccc1C=C=CC1CCCCC1"),
    ],
    [
        {"step_id": "asymmetric_propargylic_amine_formation", "participant_ids": ["phenylacetylene_1d", "aldehyde_2c", "pyrrolidine", "cubr", "ligand_9", "molecular_sieves", "toluene"], "conditions": [fld("temperature", qty(25, "°C"), e), fld("time", qty(15, "h"), e), fld("solvent", "toluene", e)]},
        {"step_id": "copper_removal", "participant_ids": [], "conditions": [fld("operation", "removal of Cu(I) with filtration", e)]},
        {"step_id": "allene_formation", "participant_ids": ["zinc_iodide", "sodium_iodide", "toluene", "product_r-3dc"], "conditions": [fld("temperature", qty(110, "°C"), e), fld("time", qty(7, "h"), e), fld("solvent", "toluene", e)]},
    ],
    [fld("isolated_yield", qty(60, "%"), e, ["product_r-3dc"]), fld("yield_measurement_basis", "isolated", e, ["product_r-3dc"]), fld("enantiomeric_excess", qty(35, "%"), e, ["product_r-3dc"])],
    unresolved=["Supporting information was not provided or explicitly associated; detailed workup and purification are missing.", "The candidate SMILES does not encode the depicted axial stereochemistry and remains unverified."]
))

# Page 3 Scheme 4 is a proposed mechanism, not an experiment.
e = ev(3)
records.append(rec(
    "scheme4_proposed_mechanism", 3, "mechanism",
    [
        participant("cu_coordinated_propargylic_alcohol", "unspecified_agent", None, "Cu-coordinated terminal propargylic alcohol", e),
        participant("intermediate_s-10", "unspecified_agent", "(S)-10", "propargylic amine intermediate (S)-10", e),
        participant("intermediate_a", "unspecified_agent", "A", "Zn-coordinated intermediate A", e),
        participant("intermediate_b", "unspecified_agent", "B", "Zn-coordinated intermediate B", e),
        participant("allene_r-3", "product", "(R)-3", "predicted (R)-allene", e),
    ],
    [{"step_id": "proposed_cycle", "participant_ids": ["cu_coordinated_propargylic_alcohol", "intermediate_s-10", "intermediate_a", "intermediate_b", "allene_r-3"], "conditions": []}], [],
    notes=["Scheme 4 is explicitly labeled as a proposed mechanism and prediction of absolute configuration."],
    unresolved=["Intermediates A, B, and (S)-10 are mechanistic proposals; no independent batch outcomes or fully specified R groups are supplied."]
))


def table2_participants(row, substrate_label, substrate_name, substrate_smiles, aldehyde_label, aldehyde_name, aldehyde_smiles, product_label, ligand, zinc):
    e = ev(3)
    zinc_name = {"ZnI2": "zinc iodide", "ZnBr2": "zinc bromide", "ZnCl2": "zinc chloride"}[zinc]
    zinc_smiles = {"ZnI2": "[Zn+2].[I-].[I-]", "ZnBr2": "[Zn+2].[Br-].[Br-]", "ZnCl2": "[Zn+2].[Cl-].[Cl-]"}[zinc]
    parts = [
        participant("substrate_1", "reactant", substrate_label, substrate_name, e, substrate_smiles, [amount("reaction_scale", 1.0, "mmol", e)]),
        participant("aldehyde_2", "reactant", aldehyde_label, aldehyde_name, e, aldehyde_smiles, [amount("equivalents", 1.1, "equiv", e)]),
        participant("pyrrolidine", "reactant", None, "pyrrolidine", e, "C1CCNC1", [amount("equivalents", 1.1, "equiv", e)]),
        participant("cubr", "catalyst", "CuBr", "copper(I) bromide", e, "[Cu]Br", [amount("loading", 5, "mol%", e)]),
        participant("chiral_ligand", "catalyst", "8" if ligand.startswith("(R,S)") else "9", ligand, e, amounts=[amount("loading", 5.5, "mol%", e)]),
        participant("molecular_sieves", "reagent", "4 Å MS", "4 angstrom molecular sieves", e),
        participant("zinc_halide", "catalyst", zinc, zinc_name, e, zinc_smiles, [amount("equivalents", 0.5 if zinc != "ZnI2" else 0.45, "equiv", e)]),
        participant("toluene", "solvent", None, "toluene", e, "Cc1ccccc1"),
        participant("product_3", "product", product_label, f"allenol {product_label}", e),
    ]
    if zinc == "ZnI2":
        parts.insert(-2, participant("sodium_iodide", "reagent", "NaI", "sodium iodide", e, "[Na+].[I-]", [amount("equivalents", 0.5, "equiv", e)]))
    else:
        parts.insert(-2, participant("propargylic_amine_intermediate", "product", None, "propargylic amine intermediate", e))
    return parts


table2_rows = [
    (1, "1e", "1-ethynylcyclohexan-1-ol", "C#CC1(O)CCCCC1", "2c", "cyclohexanecarbaldehyde", "O=CC1CCCCC1", 12, 8, 68, "(R)-3ec", 96, "(R,R)-N-PINAP", "ZnI2"),
    (2, "1e", "1-ethynylcyclohexan-1-ol", "C#CC1(O)CCCCC1", "2c", "cyclohexanecarbaldehyde", "O=CC1CCCCC1", 12, 4, 70, "(S)-3ec", 93, "(R,S)-N-PINAP", "ZnI2"),
    (3, "1e", "1-ethynylcyclohexan-1-ol", "C#CC1(O)CCCCC1", "2c", "cyclohexanecarbaldehyde", "O=CC1CCCCC1", 12, 12, 58, "(S)-3ec", 94, "(R,S)-N-PINAP", "ZnBr2"),
    (4, "1e", "1-ethynylcyclohexan-1-ol", "C#CC1(O)CCCCC1", "2c", "cyclohexanecarbaldehyde", "O=CC1CCCCC1", 12, 12, 54, "(S)-3ec", 93, "(R,S)-N-PINAP", "ZnCl2"),
    (5, "1f", "2-methylbut-3-yn-2-ol", "C#CC(O)(C)C", "2c", "cyclohexanecarbaldehyde", "O=CC1CCCCC1", 13, 2, 66, "(R)-3fc", 97, "(R,R)-N-PINAP", "ZnI2"),
    (6, "1f", "2-methylbut-3-yn-2-ol", "C#CC(O)(C)C", "2c", "cyclohexanecarbaldehyde", "O=CC1CCCCC1", 12, 1.5, 71, "(S)-3fc", 95, "(R,S)-N-PINAP", "ZnI2"),
    (7, "1g", "1-ethynylcyclopentan-1-ol", "C#CC1(O)CCCC1", "2c", "cyclohexanecarbaldehyde", "O=CC1CCCCC1", 12, 2.5, 69, "(R)-3gc", 95, "(R,R)-N-PINAP", "ZnI2"),
    (8, "1h", "3-ethylpent-1-yn-3-ol", "C#CC(O)(CC)CC", "2c", "cyclohexanecarbaldehyde", "O=CC1CCCCC1", 12, 1.5, 77, "(R)-3hc", 96, "(R,R)-N-PINAP", "ZnI2"),
    (9, "1e", "1-ethynylcyclohexan-1-ol", "C#CC1(O)CCCCC1", "2d", "2-methylpropanal", "CC(C)C=O", 19, 2.7, 50, "(R)-3ed", 95, "(R,R)-N-PINAP", "ZnI2"),
    (10, "1e", "1-ethynylcyclohexan-1-ol", "C#CC1(O)CCCCC1", "2e", "3-methylbutanal", "CC(C)CC=O", 13, 1.5, 75, "(R)-3ee", 90, "(R,R)-N-PINAP", "ZnI2"),
    (11, "1e", "1-ethynylcyclohexan-1-ol", "C#CC1(O)CCCCC1", "2f", "octanal", "CCCCCCCC=O", 20.5, 1.4, 54, "(R)-3ef", 92, "(R,R)-N-PINAP", "ZnI2"),
    (12, "1e", "1-ethynylcyclohexan-1-ol", "C#CC1(O)CCCCC1", "2g", "benzaldehyde", "O=Cc1ccccc1", 17, 4.5, 78, "(R)-3eg", 93, "(R,R)-N-PINAP", "ZnI2"),
]
product_smiles = {
    "3ec": "C1CCCCC1C=C=CC2(O)CCCCC2",
    "3fc": "CC(C)(O)C=C=CC1CCCCC1",
    "3gc": "C1CCCCC1C=C=CC2(O)CCCC2",
    "3hc": "CCC(O)(CC)C=C=CC1CCCCC1",
    "3ed": "CC(C)C=C=CC1(O)CCCCC1",
    "3ee": "CC(C)CC=C=CC1(O)CCCCC1",
    "3ef": "CCCCCCCC=C=CC1(O)CCCCC1",
    "3eg": "c1ccccc1C=C=CC2(O)CCCCC2",
}
for row, sub, subname, subsmiles, ald, aldname, aldsmiles, t1, t2, yld, prod, eevalue, ligand, zinc in table2_rows:
    e = ev(3)
    parts = table2_participants(row, sub, subname, subsmiles, ald, aldname, aldsmiles, prod, ligand, zinc)
    base_label = prod.replace("(R)-", "").replace("(S)-", "")
    for p in parts:
        if p["entity_id"] == "product_3":
            p["smiles"] = fact(product_smiles[base_label], e)
    stage1_ids = ["substrate_1", "aldehyde_2", "pyrrolidine", "cubr", "chiral_ligand", "molecular_sieves", "toluene"] + (["propargylic_amine_intermediate"] if zinc != "ZnI2" else [])
    stage2_ids = ["zinc_halide", "toluene", "product_3"] + (["sodium_iodide"] if zinc == "ZnI2" else ["propargylic_amine_intermediate"])
    outcomes = [fld("isolated_yield", qty(yld, "%"), e, ["product_3"]), fld("yield_measurement_basis", "isolated", e, ["product_3"]), fld("enantiomeric_excess", qty(eevalue, "%"), e, ["product_3"])]
    if zinc in ("ZnBr2", "ZnCl2"):
        outcomes.append(fld("recovered_propargylic_amine_yield", qty(3, "%"), e, ["propargylic_amine_intermediate"]))
    records.append(rec(
        f"table2_entry{row}", 3, "substrate_scope_entry", parts,
        [
            {"step_id": "asymmetric_propargylic_amine_formation", "participant_ids": stage1_ids, "conditions": [fld("temperature", qty(25, "°C"), e), fld("time", qty(t1, "h"), e), fld("solvent", "toluene", e)]},
            {"step_id": "copper_removal", "participant_ids": [], "conditions": [fld("operation", "removal of Cu(I) with filtration", e)]},
            {"step_id": "allene_formation", "participant_ids": stage2_ids, "conditions": [fld("temperature", qty(110, "°C"), e), fld("time", qty(t2, "h"), e), fld("solvent", "toluene", e)]},
        ], outcomes,
        notes=[f"Table 2 entry {row}; ligand and zinc-halide exceptions from footnotes were applied to this row."],
        unresolved=["Supporting information was not provided or explicitly associated; detailed workup and purification are missing.", "Product candidate SMILES does not encode the depicted axial configuration and remains unverified."]
    ))

# Page 4 Scheme 5: two failed/trace control rows.
for catalyst, loading, recovery in [("KAuCl4", 10, 59), ("AgNO3", 50, 31)]:
    e = ev(4)
    catalyst_name = "potassium tetrachloroaurate" if catalyst == "KAuCl4" else "silver nitrate"
    catalyst_smiles = "[K+].[Au-](Cl)(Cl)(Cl)Cl" if catalyst == "KAuCl4" else "[Ag+].[O-][N+](=O)[O-]"
    records.append(rec(
        f"scheme5_{catalyst.lower()}_control", 4, "optimization_entry",
        [
            participant("substrate_10ec", "reactant", "10ec", "propargylic amine 10ec", e),
            participant("metal_salt", "catalyst", catalyst, catalyst_name, e, catalyst_smiles, [amount("loading", loading, "mol%", e)]),
            participant("acetonitrile", "solvent", "CH3CN", "acetonitrile", e, "CC#N"),
            participant("product_3ec", "product", "3ec", "allenol 3ec", e, product_smiles["3ec"]),
        ],
        [{"step_id": "control_allene_formation", "participant_ids": ["substrate_10ec", "metal_salt", "acetonitrile", "product_3ec"], "conditions": [fld("temperature", qty(40, "°C"), e), fld("time", qty(24, "h"), e), fld("solvent", "acetonitrile", e)]}],
        [fld("nmr_yield", "trace", e, ["product_3ec"]), fld("yield_measurement_basis", "NMR", e, ["product_3ec"]), fld("recovered_starting_material_yield", qty(recovery, "%"), e, ["substrate_10ec"])],
        notes=["Control experiment reported only trace allene formation."],
        unresolved=["The full structure of 10ec and the basis of the reported recovery are not completely specified on the covered page."]
    ))


def scheme6_parts(page, start_label, start_name, start_ee, ligand, products):
    e = ev(page)
    parts = [
        participant("substrate_1i", "reactant", start_label, start_name, e, "C#CC(O)c1ccccc1"),
        participant("aldehyde_2c", "reactant", "2c", "cyclohexanecarbaldehyde", e, "O=CC1CCCCC1", [amount("equivalents", 1.1, "equiv", e)]),
        participant("pyrrolidine", "reactant", None, "pyrrolidine", e, "C1CCNC1", [amount("equivalents", 1.1, "equiv", e)]),
        participant("cubr", "catalyst", "CuBr", "copper(I) bromide", e, "[Cu]Br", [amount("loading", 5, "mol%", e)]),
        participant("chiral_ligand", "catalyst", "9" if ligand.startswith("(R,R)") else "8", ligand, e, amounts=[amount("loading", 5.5, "mol%", e)]),
        participant("molecular_sieves", "reagent", "4 Å MS", "4 angstrom molecular sieves", e),
        participant("zinc_iodide", "catalyst", "ZnI2", "zinc iodide", e, "[Zn+2].[I-].[I-]", [amount("equivalents", 0.45, "equiv", e)]),
        participant("sodium_iodide", "reagent", "NaI", "sodium iodide", e, "[Na+].[I-]", [amount("equivalents", 0.5, "equiv", e)]),
        participant("toluene", "solvent", None, "toluene", e, "Cc1ccccc1"),
    ]
    for idx, label in enumerate(products, 1):
        parts.append(participant(f"product_{idx}", "product", label, f"allenol {label}", e, "c1ccccc1C(O)C=C=CC1CCCCC1"))
    return parts


scheme6_rows = [
    (1, "(±)-1i", "racemic 1-phenylprop-2-yn-1-ol", None, "(R,R)-N-PINAP", 13, 74, ["(R,R)-3ic", "(R,S)-3ic"], None, None),
    (2, "(S)-1i", "(S)-1-phenylprop-2-yn-1-ol", ">99", "(R,R)-N-PINAP", 13, 60, ["(R,S)-3ic"], 92, ">99"),
    (3, "(S)-1i", "(S)-1-phenylprop-2-yn-1-ol", ">99", "(R,S)-N-PINAP", 12, 56, ["(S,S)-3ic"], 89, ">99"),
    (4, "(R)-1i", "(R)-1-phenylprop-2-yn-1-ol", 98, "(R,R)-N-PINAP", 12, 61, ["(R,R)-3ic"], 94, 97),
    (5, "(R)-1i", "(R)-1-phenylprop-2-yn-1-ol", 98, "(R,S)-N-PINAP", 12, 68, ["(S,R)-3ic"], 93, ">99"),
]
for equation, start_label, start_name, start_ee, ligand, t1, yld, products, devalue, product_ee in scheme6_rows:
    e = ev(4)
    parts = scheme6_parts(4, start_label, start_name, start_ee, ligand, products)
    product_ids = [f"product_{i}" for i in range(1, len(products) + 1)]
    outcomes = [fld("isolated_yield", qty(yld, "%"), e, product_ids), fld("yield_measurement_basis", "isolated", e, product_ids)]
    if start_ee is not None:
        start_value = qty(start_ee if isinstance(start_ee, int) else 99, "%", qualifier="gt", raw_text=">99% ee")
        outcomes.append(fld("starting_material_ee", start_value, e, ["substrate_1i"]))
    if equation == 1:
        outcomes.append(fld("diastereomeric_ratio", "1:1", e, product_ids))
        outcomes.append(fld("enantiomeric_excess_product_1", qty(93, "%"), e, ["product_1"]))
        outcomes.append(fld("enantiomeric_excess_product_2", qty(93, "%"), e, ["product_2"]))
    else:
        outcomes.append(fld("diastereomeric_excess", qty(devalue, "%"), e, product_ids))
        ee_obj = qty(product_ee if isinstance(product_ee, int) else 99, "%", qualifier="gt", raw_text=">99% ee")
        outcomes.append(fld("enantiomeric_excess_major_isomer", ee_obj, e, product_ids))
    records.append(rec(
        f"scheme6_equation{equation}", 4, "substrate_scope_entry", parts,
        [
            {"step_id": "asymmetric_propargylic_amine_formation", "participant_ids": ["substrate_1i", "aldehyde_2c", "pyrrolidine", "cubr", "chiral_ligand", "molecular_sieves", "toluene"], "conditions": [fld("temperature", qty(25, "°C"), e), fld("time", qty(t1, "h"), e), fld("solvent", "toluene", e)]},
            {"step_id": "copper_removal", "participant_ids": [], "conditions": [fld("operation", "removal of Cu(I) with filtration", e)]},
            {"step_id": "allene_formation", "participant_ids": ["zinc_iodide", "sodium_iodide", "toluene"] + product_ids, "conditions": [fld("temperature", qty(110, "°C"), e), fld("time", qty(1.5, "h"), e), fld("solvent", "toluene", e)]},
        ], outcomes,
        notes=[f"Scheme 6 equation {equation}."],
        unresolved=["Supporting information was not provided or explicitly associated; detailed workup and purification are missing.", "Candidate SMILES do not encode the depicted central/axial stereochemistry and remain unverified."]
    ))

OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
print(f"wrote {len(records)} records to {OUT}")
