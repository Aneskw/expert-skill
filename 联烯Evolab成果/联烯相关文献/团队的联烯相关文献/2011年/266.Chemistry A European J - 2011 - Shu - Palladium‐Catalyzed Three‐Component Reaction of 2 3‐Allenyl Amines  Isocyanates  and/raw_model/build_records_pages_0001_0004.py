#!/usr/bin/env python3
"""Build evidence-linked machine records for source.pdf pages 1--4."""
import json
from pathlib import Path

DOC = "doc_67d18eb52e5c651f"
OUT = Path(__file__).with_name("records_pages_0001_0004.json")


def ev(page):
    return [f"{DOC}:page{page}:image", f"{DOC}:page{page}:text"]


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


def amount(name, number, unit, evidence):
    return field(name, {"number": number, "unit": unit}, evidence)


def participant(entity_id, role, label, name, evidence, smiles=None, amounts=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence) if name is not None else fact(None, []),
        "smiles": fact(smiles, evidence) if smiles is not None else fact(None, []),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": amounts or [],
    }


def record(suffix, source_id, kind, evidence, participants, conditions, outcomes,
           notes=None, unresolved=None):
    ids = [p["entity_id"] for p in participants]
    return {
        "record_id": f"{DOC}:{suffix}",
        "document_id": DOC,
        "source_reaction_id": source_id,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": list(dict.fromkeys(evidence)),
        "participants": participants,
        "steps": [{"step_id": "reaction", "participant_ids": ids,
                   "conditions": conditions}] if conditions or ids else [],
        "outcomes": outcomes,
        "notes": [fact(n, evidence) for n in (notes or [])],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved or [
                "No explicitly associated supporting information was supplied; missing operational details remain missing.",
                "Machine-extracted structures and facts require independent source review.",
            ],
        },
    }


SMILES_1A = "C=C=CCNCC1=CC=C(OC)C=C1"
SMILES_2A = "O=C=NC1=CC=CC=C1"
SMILES_3A = "IC1=CC=CC=C1"
SMILES_4A = "O=C1N(C2=CC=CC=C2)C(C(=C)C2=CC=CC=C2)CN1CC2=CC=C(OC)C=C2"


def shared_1a_2a_3a(evidence, a1=None, a2=None, a3=None):
    return [
        participant("amine_1a", "reactant", "1a", "N-(4-methoxybenzyl)-2,3-allenylamine", evidence,
                    SMILES_1A, a1 or []),
        participant("isocyanate_2a", "reactant", "2a", "phenyl isocyanate", evidence,
                    SMILES_2A, a2 or []),
        participant("halide_3a", "reactant", "3a", "iodobenzene", evidence,
                    SMILES_3A, a3 or []),
    ]


def product_4a(evidence):
    return participant("product_4a", "product", "4a",
        "1-(4-methoxybenzyl)-3-phenyl-4-(1-phenylvinyl)imidazolidin-2-one",
        evidence, SMILES_4A)


def catalyst_pdpph3(evidence):
    return participant("pd_pph3_4", "catalyst", "[Pd(PPh3)4]", "tetrakis(triphenylphosphine)palladium(0)",
                       evidence, None, [amount("catalyst_loading", 5, "mol%", evidence)])


def base_k2co3(evidence, equiv=2):
    return participant("base", "reagent", "K2CO3", "potassium carbonate", evidence,
                       "[K+].[K+].[O-]C([O-])=O", [amount("equivalents", equiv, "equiv", evidence)])


def solvent(name, evidence, volume=4):
    smiles = {"THF": "C1CCOC1", "DME": "COCCOC", "DMF": "CN(C)C=O",
              "DMSO": "CS(C)=O", "DCE": "ClCCCl", "CH3CN": "CC#N",
              "anisole": "COC1=CC=CC=C1", "toluene": "CC1=CC=CC=C1"}.get(name)
    return participant("solvent", "solvent", name, name, evidence, smiles,
                       [amount("volume", volume, "mL", evidence)] if volume is not None else [])


records = []

# The 96% standard experiment is repeated in three table rows and the detailed procedure.
e_std = ev(1) + ev(2) + ev(3)
p_std = shared_1a_2a_3a(
    e_std,
    [amount("amount", 0.20, "mmol", e_std), amount("mass", 37, "mg", ev(3))],
    [amount("amount", 0.30, "mmol", e_std), amount("mass", 36, "mg", ev(3))],
    [amount("table_amount", 0.30, "mmol", ev(2)), amount("typical_procedure_amount", 0.28, "mmol", ev(3)),
     amount("mass", 58, "mg", ev(3))],
)
cat = catalyst_pdpph3(e_std)
cat["amounts"] += [amount("amount", 0.010, "mmol", ev(3)), amount("mass", 12, "mg", ev(3))]
base = base_k2co3(e_std)
base["amounts"] += [amount("amount", 0.40, "mmol", ev(3)), amount("mass", 55, "mg", ev(3))]
p_std += [cat, base, solvent("CH3CN", e_std), product_4a(e_std)]
records.append(record(
    "standard_4a", "Table 1 entry 6 / Table 2 entry 4 / Table 3 entry 1 / typical procedure for 4a",
    "optimization_entry", e_std, p_std,
    [field("temperature", {"number": 70, "unit": "°C"}, e_std),
     field("time", {"number": 26.5, "unit": "h"}, ev(2)),
     field("atmosphere", "argon", ev(3)),
     field("operation", "Flame-dried Schlenk tube; reagents added sequentially; completion monitored by TLC.", ev(3)),
     field("workup", "Solvent evaporated under reduced pressure.", ev(3)),
     field("purification", "Silica-gel chromatography, petroleum ether/ethyl acetate 7:1.", ev(3))],
    [field("isolated_yield", {"number": 96, "unit": "%"}, e_std, ["product_4a"]),
     field("product_mass", {"number": 72, "unit": "mg"}, ev(3), ["product_4a"]),
     field("yield_measurement_basis", "isolated product", ev(2), ["product_4a"])],
    ["The same 96% standard reaction is repeated as Table 1 entry 6, Table 2 entry 4, Table 3 entry 1, and the typical procedure; it is represented once.",
     "The table footnotes give 3a as 0.30 mmol, whereas the detailed procedure gives 58 mg, 0.28 mmol; both source values are retained."],
    ["Supporting information is mentioned in the article but was not explicitly provided or associated in this dataset.",
     "The 0.30 versus 0.28 mmol values reported for 3a were not reconciled by inference.",
     "Candidate SMILES require independent comparison with the source drawings."]
))

# Table 1: solvent optimization. Entry 6 is the canonical record above.
table1 = [
    (1, "THF", 22, 72), (2, "DME", 11, 70), (3, "DMF", 13, 87),
    (4, "DMSO", 13, 76), (5, "DCE", 26.5, 77),
    (7, "CH3CN", 12, 92), (8, "anisole", 11, 83), (9, "toluene", 13, 54),
]
for entry, solv, hours, yld in table1:
    evidence = ev(2) + (ev(1) if entry == 1 else [])
    ps = shared_1a_2a_3a(
        evidence,
        [amount("amount", 0.20, "mmol", evidence)],
        [amount("amount", 0.30, "mmol", evidence)],
        [amount("amount", 0.30, "mmol", evidence)],
    )
    if entry == 7:
        ps += [
            participant("pd2_dba3_chcl3", "catalyst", "[Pd2(dba)3]·CHCl3", "tris(dibenzylideneacetone)dipalladium chloroform adduct",
                        evidence, None, [amount("catalyst_loading", 2.5, "mol%", evidence)]),
            participant("pph3", "reagent", "PPh3", "triphenylphosphine", evidence, "P(C1=CC=CC=C1)(C1=CC=CC=C1)C1=CC=CC=C1",
                        [amount("reagent_loading", 10, "mol%", evidence)]),
        ]
    else:
        ps.append(catalyst_pdpph3(evidence))
    ps += [base_k2co3(evidence), solvent(solv, evidence), product_4a(evidence)]
    records.append(record(
        f"table1_entry{entry}", f"Table 1 entry {entry}", "optimization_entry", evidence, ps,
        [field("temperature", {"number": 70, "unit": "°C"}, evidence),
         field("time", {"number": hours, "unit": "h"}, evidence),
         field("operation", "Reaction conducted in a Schlenk tube.", ev(2))],
        [field("isolated_yield", {"number": yld, "unit": "%"}, evidence, ["product_4a"]),
         field("yield_measurement_basis", "isolated product", ev(2), ["product_4a"])],
    ))

# Table 2: base and stoichiometry optimization. Entry 4 is the canonical record above.
table2 = [
    (1, "Cs2CO3", 2, 1.5, 1.5, 11, 82),
    (2, "Na2CO3", 2, 1.5, 1.5, 11, 57),
    (3, "K3PO4·3H2O", 2, 1.5, 1.5, 11, 75),
    (5, "K2CO3", 1.5, 1.5, 1.5, 12, 83),
    (6, "K2CO3", 2, 1.2, 1.5, 10, 83),
    (7, "K2CO3", 2, 2.0, 1.5, 10, 61),
    (8, "K2CO3", 2, 1.5, 1.2, 16, 73),
    (9, "K2CO3", 2, 1.5, 2.0, 16, 75),
]
for entry, base_label, base_eq, n2, n3, hours, yld in table2:
    evidence = ev(2)
    ps = shared_1a_2a_3a(
        evidence,
        [amount("amount", 0.20, "mmol", evidence), amount("equivalents", 1, "equiv", evidence)],
        [amount("equivalents", n2, "equiv", evidence)],
        [amount("equivalents", n3, "equiv", evidence)],
    )
    ps += [catalyst_pdpph3(evidence),
           participant("base", "reagent", base_label, base_label, evidence, None,
                       [amount("equivalents", base_eq, "equiv", evidence)]),
           solvent("CH3CN", evidence), product_4a(evidence)]
    records.append(record(
        f"table2_entry{entry}", f"Table 2 entry {entry}", "optimization_entry", evidence, ps,
        [field("temperature", {"number": 70, "unit": "°C"}, evidence),
         field("time", {"number": hours, "unit": "h"}, evidence),
         field("operation", "Reaction conducted in a Schlenk tube.", evidence)],
        [field("isolated_yield", {"number": yld, "unit": "%"}, evidence, ["product_4a"]),
         field("yield_measurement_basis", "isolated product", evidence, ["product_4a"])],
    ))

# Table 3: organic-halide scope. Entry 1 is the canonical record above.
table3 = [
    (2, "4-MeO2C-C6H4 (3b)", "methyl 4-iodobenzoate", "COC(=O)C1=CC=C(I)C=C1", 16, 90, "4b"),
    (3, "4-MeOC-C6H4 (3c)", "organic iodide 3c (source condensed notation)", None, 16, 93, "4c"),
    (4, "3-Me-C6H4 (3d)", "1-iodo-3-methylbenzene", "CC1=CC=CC(I)=C1", 12, 83, "4d"),
    (5, "4-Me-C6H4 (3e)", "1-iodo-4-methylbenzene", "CC1=CC=C(I)C=C1", 10, 90, "4e"),
    (6, "4-MeO-C6H4 (3f)", "1-iodo-4-methoxybenzene", "COC1=CC=C(I)C=C1", 16, 74, "4f"),
    (7, "4-Ph-C6H4 (3g)", "4-iodobiphenyl", "IC1=CC=C(C2=CC=CC=C2)C=C1", 16, 92, "4g"),
    (8, "4-CN-C6H4 (3h)", "4-iodobenzonitrile", "N#CC1=CC=C(I)C=C1", 12, 75, "4h"),
    (9, "4-(4-BrC6H4)C6H4 (3i)", "4-bromo-4'-iodobiphenyl", "BrC1=CC=C(C2=CC=C(I)C=C2)C=C1", 16, 86, "4i"),
    (10, "4-iPr-C6H4 (3j)", "1-iodo-4-isopropylbenzene", "CC(C)C1=CC=C(I)C=C1", 17, 87, "4j"),
    (11, "3-thienyl (3k)", "3-iodothiophene", "IC1=CSC=C1", 17, 64, "4k"),
    (12, "3,5-Me2-C6H3 (3l)", "1-iodo-3,5-dimethylbenzene", "CC1=CC(I)=CC(C)=C1", 17, 81, "4l"),
    (13, "3,4-Me2-C6H3 (3m)", "1-iodo-3,4-dimethylbenzene", "CC1=C(C)C=C(I)C=C1", 15.5, 84, "4m"),
    (14, "3,4-(OCH2)2-C6H3 (3n)", "iodo-methylenedioxybenzene 3n", "IC1=CC2=COCOC2=C1", 15.5, 82, "4n"),
    (15, "(E)-C6H13CH=CH (3o)", "(E)-alkenyl iodide 3o", None, 15.5, 70, "4o"),
    (16, "(E)-MeO2CCH=CH (3p)", "(E)-alkenyl iodide 3p", None, 16, 77, "4p"),
    (17, "4-NH2-C6H4 (3q)", "4-iodoaniline", "NC1=CC=C(I)C=C1", 11, 63, "4q"),
]
for entry, hal_label, hal_name, hal_smiles, hours, yld, product_label in table3:
    evidence = ev(2) + (ev(3) if entry in (11, 15, 16, 17) else [])
    ps = [
        participant("amine_1a", "reactant", "1a", "N-(4-methoxybenzyl)-2,3-allenylamine", evidence,
                    SMILES_1A, [amount("amount", 0.20, "mmol", evidence)]),
        participant("isocyanate_2a", "reactant", "2a", "phenyl isocyanate", evidence,
                    SMILES_2A, [amount("amount", 0.30, "mmol", evidence)]),
        participant("organic_halide", "reactant", hal_label, hal_name, evidence, hal_smiles,
                    [amount("amount", 0.30, "mmol", evidence)]),
        catalyst_pdpph3(evidence), base_k2co3(evidence), solvent("CH3CN", evidence),
        participant("product", "product", product_label,
                    f"imidazolidinone {product_label} corresponding to {hal_label}", evidence),
    ]
    notes = []
    unresolved = None
    if entry == 3:
        notes.append("The condensed substituent text for 3c is retained verbatim; its carbonyl connectivity was not expanded to SMILES.")
        unresolved = ["The exact connectivity encoded by the source notation '4-MeOC-C6H4' for 3c needs chemical source review.",
                      "Product-specific structure and missing operational details require SI/source review."]
    records.append(record(
        f"table3_entry{entry}", f"Table 3 entry {entry}", "substrate_scope_entry", evidence, ps,
        [field("temperature", {"number": 70, "unit": "°C"}, evidence),
         field("time", {"number": hours, "unit": "h"}, evidence)],
        [field("isolated_yield", {"number": yld, "unit": "%"}, evidence, ["product"]),
         field("yield_measurement_basis", "isolated product", ev(2), ["product"])],
        notes, unresolved,
    ))

# Scheme 3: six distinct substrate combinations under a shared condition header.
scheme3 = [
    ("4r", "Bn", "Ph", "Me", 77),
    ("4s", "Bn", "Bn", "Me", 58),
    ("4t", "nBu", "Ph", "Me", 67),
    ("4u", "Bn", "4-MeOC6H4", "Me", 75),
    ("4v", "Bn", "4-NO2C6H4", "Me", 83),
    ("4w", "Bn", "4-ClC6H4", "Me", 81),
]
for product_label, r1, r2, r3, yld in scheme3:
    evidence = ev(3) + (ev(4) if product_label == "4r" else [])
    ps = [
        participant("allenyl_amine", "reactant", f"1 (R1={r1})", f"2,3-allenylamine with R1={r1}", evidence),
        participant("isocyanate", "reactant", f"2 (R2={r2})", f"isocyanate with R2={r2}", evidence),
        participant("aryl_iodide", "reactant", f"3 (R3={r3})", "4-iodotoluene", evidence,
                    "CC1=CC=C(I)C=C1"),
        catalyst_pdpph3(evidence), base_k2co3(evidence), solvent("CH3CN", evidence, None),
        participant("product", "product", product_label,
                    f"imidazolidinone {product_label} (R1={r1}, R2={r2}, R3={r3})", evidence),
    ]
    notes = []
    if product_label == "4r":
        notes.append("The article reports X-ray diffraction confirmation of 4r; CCDC-778290 is cited with crystal data on page 4.")
    records.append(record(
        f"scheme3_{product_label}", f"Scheme 3 row {product_label}", "substrate_scope_entry", evidence, ps,
        [field("temperature", {"number": 70, "unit": "°C"}, ev(3))],
        [field("reported_yield", {"number": yld, "unit": "%"}, ev(3), ["product"]),
         field("yield_measurement_basis", None, [], ["product"])],
        notes,
        ["Scheme 3 does not report reaction time, substrate scale, solvent volume, or yield measurement basis.",
         "R-group structures and product structures remain unverified machine interpretations.",
         "No explicitly associated supporting information was supplied."],
    ))

# Equation (1): free allenylamine hydrochloride example.
e_eq = ev(3)
eq_parts = [
    participant("amine_1d", "reactant", "1d", "2,3-allenylamine hydrochloride", e_eq,
                "C=C=CC[NH3+].[Cl-]"),
    participant("isocyanate_2a", "reactant", "2a", "phenyl isocyanate", e_eq, SMILES_2A),
    participant("halide_3a", "reactant", "3a", "iodobenzene", e_eq, SMILES_3A),
    catalyst_pdpph3(e_eq), base_k2co3(e_eq, 3), solvent("CH3CN", e_eq, None),
    participant("product_4x", "product", "4x", "3-phenyl-4-(1-phenylvinyl)imidazolidin-2-one", e_eq,
                "O=C1N(C2=CC=CC=C2)C(C(=C)C2=CC=CC=C2)CN1"),
]
records.append(record(
    "equation1_4x", "Equation (1)", "substrate_scope_entry", e_eq, eq_parts,
    [field("temperature", {"number": 70, "unit": "°C"}, e_eq),
     field("time", {"number": 12, "unit": "h"}, e_eq)],
    [field("reported_yield", {"number": 54, "unit": "%"}, e_eq, ["product_4x"]),
     field("yield_measurement_basis", None, [], ["product_4x"])],
    unresolved=["Equation (1) does not report scale, solvent volume, or yield measurement basis.",
                "Candidate structures require independent comparison with the source drawing.",
                "No explicitly associated supporting information was supplied."],
))

# Scheme 2 is a proposed mechanistic network, not a batch experiment.
e_mech = ev(1) + ev(2)
mech_parts = [
    participant("generic_allenyl_amine", "reactant", "1", "generic 2,3-allenylamine", e_mech),
    participant("generic_isocyanate", "reactant", "2", "generic isocyanate", e_mech),
    participant("generic_organic_halide", "reactant", "3", "generic organic halide", e_mech),
    participant("generic_imidazolidinone", "product", "4", "generic imidazolidinone", e_mech),
]
records.append(record(
    "scheme2_proposed_mechanism", "Scheme 2", "mechanism", e_mech, mech_parts,
    [field("operation", "Proposed carbopalladation/urea-anion pathway through syn-M2 to imidazolidinone; syn-M1 and anti-M1/anti-M2 paths are depicted as competing possibilities.", e_mech)],
    [],
    ["Scheme 2 is a mechanistic reaction scheme and challenge analysis, not an independently reported experimental batch; no yield is assigned."],
    ["Generic R groups and proposed intermediates do not define unique molecular structures."]
))

OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
print(f"wrote {len(records)} records to {OUT}")
