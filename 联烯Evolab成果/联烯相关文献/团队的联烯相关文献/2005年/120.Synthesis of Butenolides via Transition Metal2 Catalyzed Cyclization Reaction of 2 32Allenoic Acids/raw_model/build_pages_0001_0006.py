#!/usr/bin/env python3
"""Build raw, evidence-linked records for visually inspected PDF pages 1--6."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "runs/current/raw_model/pages_0001_0006_records.json"
COVERAGE_OUT = ROOT / "runs/current/coverage/pages_0001_0006.json"
TASKS_OUT = ROOT / "runs/current/tasks.json"
DOC = "doc_8f7c32b36ec71a95"


def ev(page, include_text=True):
    ids = [f"{DOC}:page{page}:image"]
    if include_text:
        ids.append(f"{DOC}:page{page}:text")
    return ids


def fact(value, evidence):
    return {
        "value": value,
        "evidence_ids": list(evidence) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def field(name, value, evidence, targets=None):
    result = {"name": name, "fact": fact(value, evidence)}
    if targets:
        result["target_entity_ids"] = list(targets)
    return result


def participant(entity_id, role, label, name, evidence, smiles=None, amounts=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence),
        "smiles": fact(smiles, evidence if smiles is not None else []),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": amounts or [],
    }


def missing_fields():
    return [
        field("reaction_scale", None, []),
        field("workup", None, []),
        field("purification", None, []),
    ]


def record(suffix, source_id, evidence, participants, conditions, outcomes, citation, extra_notes=None, extra_unresolved=None):
    notes = [
        fact(f"The article assigns this experiment to prior publication {citation}; classified as a literature example.", evidence),
        fact("Only information visible on the inspected main-text page(s) was retained; no supporting information was associated.", evidence),
    ]
    notes.extend(extra_notes or [])
    unresolved = [
        "Reactant quantities, yield measurement basis, workup, and purification are not reported in the inspected page region.",
        "Substrate/product structures are presented through a generic R-group scaffold; complete source-verified SMILES were not assigned.",
        "Record is machine-extracted and requires independent chemical source review.",
    ]
    unresolved.extend(extra_unresolved or [])
    return {
        "record_id": f"{DOC}:{suffix}",
        "document_id": DOC,
        "source_reaction_id": source_id,
        "record_kind": "literature_example",
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": list(dict.fromkeys(evidence)),
        "participants": participants,
        "steps": [{
            "step_id": "reaction",
            "participant_ids": [p["entity_id"] for p in participants],
            "conditions": conditions + missing_fields(),
        }],
        "outcomes": outcomes + [field("yield_measurement_basis", None, [])],
        "notes": notes,
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved,
        },
    }


def nonexperimental_record(suffix, source_id, kind, evidence, participants, conditions, notes, unresolved):
    """Represent a visible general scheme or proposed mechanism without calling it an experiment."""
    return {
        "record_id": f"{DOC}:{suffix}",
        "document_id": DOC,
        "source_reaction_id": source_id,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": list(dict.fromkeys(evidence)),
        "participants": participants,
        "steps": [{
            "step_id": "depicted_scheme",
            "participant_ids": [p["entity_id"] for p in participants],
            "conditions": conditions,
        }],
        "outcomes": [],
        "notes": [fact(note, evidence) for note in notes],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved + ["Record is machine-extracted and requires independent chemical source review."],
        },
    }


records = []

# Page 2, Table 1: CuCl-catalyzed cyclization, 15 prior-work scope entries.
table1 = [
    (1, "Ph", "H", "n-C3H7", "1a", "2a", 97),
    (2, "Ph", "H", "CH3", "1b", "2b", 95),
    (3, "Ph", "H", "PhCH2", "1c", "2c", 90),
    (4, "Ph", "H", "allyl", "1d", "2d", 96),
    (5, "alpha-naphthyl", "H", "CH3", "1e", "2e", 92),
    (6, "alpha-naphthyl", "H", "n-C3H7", "1f", "2f", 96),
    (7, "alpha-naphthyl", "H", "allyl", "1g", "2g", 92),
    (8, "CH3", "H", "n-C3H7", "1h", "2h", 78),
    (9, "CH3", "H", "PhCH2", "1i", "2i", 90),
    (10, "n-C3H7", "H", "CH3", "1j", "2j", 87),
    (11, "n-C3H7", "H", "PhCH2", "1k", "2k", 85),
    (12, "n-C3H7", "H", "allyl", "1l", "2l", 91),
    (13, "n-C6H13", "H", "CH3", "1m", "2m", 85),
    (14, "Ph", "C2H5", "CH3", "1n", "2n", 93),
    (15, "n-C7H15", "H", "H", "1o", "2o", 81),
]
e2 = ev(2)
for entry, r1, r2, r3, substrate, product, yld in table1:
    s = participant("substrate", "reactant", substrate, f"2,3-allenoic acid {substrate} (R1={r1}, R2={r2}, R3={r3})", e2)
    p = participant("product", "product", product, f"beta-unsubstituted butenolide {product}", e2)
    cat = participant("cucl", "catalyst", "CuCl", "copper(I) chloride", e2, amounts=[field("amount", {"number": 4, "unit": "mol%", "raw_text": "x_CuCl = 4%"}, e2)])
    solv = participant("meoh", "solvent", "MeOH", "methanol", e2, smiles="CO")
    conditions = [
        field("solvent", "MeOH", e2),
        field("atmosphere", "Ar", e2),
        field("temperature", "reflux", e2),
        field("reaction_time", {"number": 2, "unit": "h"}, e2),
    ]
    outcomes = [field("yield", {"number": yld, "unit": "%"}, e2, ["product"])]
    records.append(record(f"p02_table1_entry{entry:02d}", f"Table 1 entry {entry}", e2, [s, p, cat, solv], conditions, outcomes, "[6]"))


# Page 3, Table 2: PdCl2-catalyzed coupling with allylic halides, 17 rows.
table2 = [
    (1, "Ph", "n-C3H7", "H", "1a", "H", "Br", "3a", 17, "4a", 88),
    (2, "Ph", "CH3", "H", "1b", "H", "Br", "3a", 17.5, "4b", 83),
    (3, "1-naphthyl", "n-C3H7", "H", "1c", "H", "Br", "3a", 21, "4c", 78),
    (4, "1-naphthyl", "CH3", "H", "1d", "H", "Br", "3a", 16, "4d", 81),
    (5, "Ph", "PhCH2", "H", "1e", "H", "Br", "3a", 16, "4e", 71),
    (6, "1-naphthyl", "n-C3H7", "H", "1c", "Ph", "Br", "3b", 24, "4f", 93),
    (7, "Ph", "n-C3H7", "H", "1a", "CH3", "Cl", "3c", 24, "4g", 89),
    (8, "1-naphthyl", "n-C3H7", "H", "1c", "CH3", "Cl", "3c", 15.5, "4h", 95),
    (9, "Ph", "n-C3H7", "H", "1a", "Br", "Br", "3d", 21, "4i", 77),
    (10, "1-naphthyl", "n-C3H7", "H", "1c", "Br", "Br", "3d", 23, "4j", 79),
    (11, "1-naphthyl", "CH3", "H", "1d", "Br", "Br", "3d", 23.5, "4k", 69),
    (12, "Ph", "allyl", "H", "1f", "H", "Br", "3a", 17, "4l", 72),
    (13, "1-naphthyl", "CH3", "H", "1d", "CH3", "Cl", "3c", 24, "4m", 76),
    (14, "CH3", "PhCH2", "H", "1g", "H", "Br", "3a", 17, "4n", 52),
    (15, "CH3", "PhCH2", "H", "1g", "H", "Br", "3a", 17.5, "4n", 73),
    (16, "Ph", "CH3", "Et", "1h", "H", "Br", "3a", 19, "4o", 83),
    (17, "4-Br-C6H5", "n-C3H7", "H", "1i", "H", "Br", "3a", 11.5, "4p", 75),
]
allyl_names = {
    "3a": ("allyl bromide", "C=CCBr"),
    "3b": ("2-phenylallyl bromide", "C=C(CBr)c1ccccc1"),
    "3c": ("methallyl chloride", "C=C(C)CCl"),
    "3d": ("2-bromoallyl bromide", "C=C(Br)CBr"),
}
e3 = ev(3)
for entry, r1, r2, r3, substrate, r4, x, halide, time_h, product, yld in table2:
    s = participant("substrate", "reactant", substrate, f"2,3-allenoic acid {substrate} (R1={r1}, R2={r2}, R3={r3})", e3)
    hname, hsmiles = allyl_names[halide]
    h = participant("allylic_halide", "reactant", halide, f"{hname} {halide} (R4={r4}, X={x})", e3, smiles=hsmiles)
    p = participant("product", "product", product, f"allyl-substituted butenolide {product}", e3)
    cat = participant("pdcl2", "catalyst", "PdCl2", "palladium(II) chloride", e3, amounts=[field("amount", {"number": 5, "unit": "mol%", "raw_text": "x_PdCl2 = 5%"}, e3)])
    solv = participant("dma", "solvent", "DMA", "N,N-dimethylacetamide", e3, smiles="CC(=O)N(C)C")
    conditions = [field("solvent", "DMA", e3), field("temperature", {"number": 50, "unit": "°C"}, e3), field("reaction_time", {"number": time_h, "unit": "h"}, e3)]
    outcomes = [field("yield", {"number": yld, "unit": "%"}, e3, ["product"])]
    extra_notes = []
    extra_unresolved = []
    if entry == 15:
        extra_notes.append(fact("The 73% yield carries superscript footnote b, but the definition of footnote b is not visible on the inspected page.", e3))
        extra_unresolved.append("Table 2 entry 15 footnote b could not be resolved from pages 1--6; its condition or yield qualification remains unknown.")
    records.append(record(f"p03_table2_entry{entry:02d}", f"Table 2 entry {entry}", e3, [s, h, p, cat, solv], conditions, outcomes, "[8]", extra_notes, extra_unresolved))


# Page 4, Scheme 1: each temperature/time line is a separate experiment.
scheme1 = [
    (1, "(+)-1a", "R1=H, R2=n-C3H7, R3=Ph", {"number": 98, "unit": "%", "qualifier": "gt", "raw_text": ">98% ee"}, 50, 16, "(+)-4a", 90, {"number": 94, "unit": "%"}),
    (2, "(+)-1a", "R1=H, R2=n-C3H7, R3=Ph", {"number": 98, "unit": "%", "qualifier": "gt", "raw_text": ">98% ee"}, 25, 35, "(+)-4a", 80, {"number": 99, "unit": "%", "qualifier": "gt", "raw_text": ">99% ee"}),
    (3, "(-)-1a", "R1=Ph, R2=n-C3H7, R3=H", {"number": 97, "unit": "%", "qualifier": "gt", "raw_text": ">97% ee"}, 25, 36.5, "(-)-4a", 82, {"number": 99, "unit": "%"}),
    (4, "(+)-1d", "R1=H, R2=CH3, R3=naphthyl", {"number": 98, "unit": "%", "qualifier": "gt", "raw_text": ">98% ee"}, 25, 40, "(+)-4d", 91, {"number": 90, "unit": "%"}),
    (5, "(+)-1d", "R1=H, R2=CH3, R3=naphthyl", {"number": 98, "unit": "%", "qualifier": "gt", "raw_text": ">98% ee"}, 0, 84.5, "(+)-4d", 39, {"number": 98, "unit": "%"}),
    (6, "(-)-1d", "R1=naphthyl, R2=CH3, R3=H", {"number": 97, "unit": "%", "qualifier": "gt", "raw_text": ">97% ee"}, 25, 40, "(-)-4d", 85, {"number": 92, "unit": "%"}),
]
e4 = ev(4)
for entry, substrate, subs, substrate_ee, temp, time_h, product, yld, product_ee in scheme1:
    s = participant("substrate", "reactant", substrate, f"optically active 2,3-allenoic acid {substrate} ({subs})", e4)
    h = participant("allyl_bromide", "reactant", "3a", "allyl bromide", e4, smiles="C=CCBr")
    p = participant("product", "product", product, f"optically active butenolide {product}", e4)
    cat = participant("pdcl2", "catalyst", "PdCl2", "palladium(II) chloride", e4, amounts=[field("amount", {"number": 5, "unit": "mol%", "raw_text": "x_PdCl2 = 5%"}, e4)])
    solv = participant("dma", "solvent", "DMA", "N,N-dimethylacetamide", e4, smiles="CC(=O)N(C)C")
    conditions = [field("solvent", "DMA", e4), field("temperature", {"number": temp, "unit": "°C"}, e4), field("reaction_time", {"number": time_h, "unit": "h"}, e4)]
    outcomes = [
        field("starting_material_ee", substrate_ee, e4, ["substrate"]),
        field("yield", {"number": yld, "unit": "%"}, e4, ["product"]),
        field("product_ee", product_ee, e4, ["product"]),
    ]
    records.append(record(f"p04_scheme1_condition{entry:02d}", f"Scheme 1 condition {entry}", e4, [s, h, p, cat, solv], conditions, outcomes, "[8]"))


# Page 4 equations (1) and (2), described on page 3 and drawn on page 4.
e34 = [f"{DOC}:page4:image", f"{DOC}:page4:text", f"{DOC}:page3:text"]
base_sub = participant("substrate", "reactant", "1a", "4-phenyl-2-propyl-2,3-butadienoic acid 1a", e34)
cat = participant("pdcl2", "catalyst", "PdCl2", "palladium(II) chloride", e34, amounts=[field("amount", {"number": 5, "unit": "mol%", "raw_text": "x_PdCl2 = 5%"}, e34)])
solv = participant("dma", "solvent", "DMA", "N,N-dimethylacetamide", e34, smiles="CC(=O)N(C)C")

h3e = participant("alkenyl_chloride", "reactant", "3e", "3-chloro-1-butene", e34, smiles="C=CC(Cl)C")
p4q = participant("product_4q", "product", "4q", "butenolide 4q", e34)
records.append(record(
    "p04_eq1_control", "Equation (1)", e34, [base_sub, h3e, p4q, cat, solv],
    [field("solvent", "DMA", e34), field("temperature", {"number": 50, "unit": "°C"}, e34), field("reaction_time", {"number": 16, "unit": "h"}, e34)],
    [field("yield", {"number": 91, "unit": "%"}, e34, ["product_4q"])], "[8]",
))

h3f = participant("alkenyl_chloride", "reactant", "3f", "1-chloro-2-butene", e34, smiles="CC=CCCl")
p4qa = participant("product_4qa", "product", "4qA", "butenolide regioisomer 4qA", e34)
records.append(record(
    "p04_eq2_control", "Equation (2)", e34, [base_sub, h3f, p4q, p4qa, cat, solv],
    [field("solvent", "DMA", e34), field("temperature", {"number": 50, "unit": "°C"}, e34), field("reaction_time", {"number": 35.5, "unit": "h"}, e34)],
    [field("combined_yield", {"number": 19, "unit": "%"}, e34, ["product_4q", "product_4qa"]), field("product_ratio", "4q:4qA = 17:1", e34, ["product_4q", "product_4qa"])], "[8]",
))


# Page 5, Table 3: eight coupling/cyclization rows under the page-4 header.
table3 = [
    (1, "H", "C3H7", "1a", 2, "5a", 1, "6a", 58),
    (2, "H", "CH3", "1b", 2, "5a", 1, "6b", 43),
    (3, "H", "PhCH2", "1c", 2, "5a", 1.5, "6c", 48),
    (4, "Et", "CH3", "1d", 2, "5a", 1, "6d", 36),
    (5, "H", "C3H7", "1a", 3, "5b", 10, "6e", 45),
    (6, "H", "CH3", "1b", 3, "5b", 2, "6f", 23),
    (7, "H", "PhCH2", "1c", 3, "5b", 4, "6g", 30),
    (8, "Et", "CH3", "1d", 3, "5b", 1.5, "6h", 27),
]
e45 = [f"{DOC}:page5:image", f"{DOC}:page5:text", f"{DOC}:page4:image", f"{DOC}:page4:text"]
alkenyl = {"5a": ("4-bromo-1-butene", "C=CCCBr"), "5b": ("5-bromo-1-pentene", "C=CCCCBr")}
for entry, r1, r2, substrate, n, halide, time_h, product, yld in table3:
    s = participant("substrate", "reactant", substrate, f"2,3-allenoic acid {substrate} (R1={r1}, R2={r2}; fixed Ph substituent in Table 3 scaffold)", e45)
    hname, hsmiles = alkenyl[halide]
    h = participant("alkenyl_halide", "reactant", halide, f"{hname} {halide} (n={n})", e45, smiles=hsmiles)
    p = participant("product", "product", product, f"alkenyl-substituted butenolide {product}", e45)
    cat = participant("palladium_acetate", "catalyst", "Pd(OAc)2", "palladium(II) acetate", e45, amounts=[field("amount", {"number": 5, "unit": "mol%", "raw_text": "x_Pd(OAc)2 = 5%"}, e45)])
    solv = participant("dmf", "solvent", "DMF", "N,N-dimethylformamide", e45, smiles="CN(C)C=O")
    conditions = [field("solvent", "DMF", e45), field("temperature", {"minimum": 90, "maximum": 100, "unit": "°C", "raw_text": "90–100 °C"}, e45), field("reaction_time", {"number": time_h, "unit": "h"}, e45)]
    outcomes = [field("yield", {"number": yld, "unit": "%"}, e45, ["product"])]
    records.append(record(f"p05_table3_entry{entry:02d}", f"Table 3 entry {entry}", e45, [s, h, p, cat, solv], conditions, outcomes, "[9]"))

# Page 5, Scheme 2 is a proposed mechanistic network, not a reported experiment.
mechanism_participants = [
    participant("generic_allenoic_acid", "reactant", "1", "generic 2,3-allenoic acid 1", ev(5)),
    participant("alkenyl_bromide", "reactant", "5a", "homoallyl bromide 5a", ev(5), smiles="C=CCCBr"),
    participant("palladium_species", "catalyst", "[PdX2]", "generic palladium(II) species", ev(5)),
    participant("intermediates", "unspecified_agent", "7–11", "proposed palladium intermediates 7 through 11", ev(5)),
    participant("generic_product", "product", "6", "generic alkenyl-substituted butenolide 6", ev(5)),
]
records.append(nonexperimental_record(
    "p05_scheme2_mechanism", "Scheme 2", "mechanism", ev(5), mechanism_participants,
    [field("operation", "Proposed alternative Path A and Path B; arrows depict catalytic intermediates rather than isolated experimental stages.", ev(5))],
    ["The figure is explicitly titled 'The possible reaction pathways' and was not promoted to a reported experiment."],
    ["Generic R groups, X ligands, and organopalladium intermediates prevent assignment of complete structures or source-verified SMILES."],
))


# Page 6 equations (3)--(5): isotope probe, Pd(0) comparison, and long-chain migration example.
e6 = ev(6)
base_sub6 = participant("substrate", "reactant", "1a", "4-phenyl-2-propyl-2,3-butadienoic acid 1a", e6)
dmf6 = participant("dmf", "solvent", "DMF", "N,N-dimethylformamide", e6, smiles="CN(C)C=O")

h5c = participant("alkenyl_halide", "reactant", "5c", "deuterated homoallyl bromide 5c", e6)
p6i = participant("product", "product", "6i", "dideuterated butenolide 6i", e6)
pdoac = participant("palladium_acetate", "catalyst", "Pd(OAc)2", "palladium(II) acetate", e6, amounts=[field("amount", {"number": 5, "unit": "mol%", "raw_text": "x_Pd(OAc)2 = 5%"}, e6)])
records.append(record(
    "p06_eq3_deuterium_probe", "Equation (3)", e6, [base_sub6, h5c, p6i, pdoac, dmf6],
    [field("solvent", "DMF", e6), field("temperature", {"minimum": 80, "maximum": 90, "unit": "°C", "raw_text": "80–90 °C"}, e6), field("reaction_time", {"number": 1.5, "unit": "h"}, e6)],
    [field("yield", {"number": 52, "unit": "%"}, e6, ["product"]), field("isotopic_observation", "Both deuterium atoms are located at the terminal carbon of the noncyclic C=C bond in 6i.", e6, ["product"])], "[9]",
    extra_unresolved=["No stereochemical/isotopic SMILES was assigned for 5c or 6i; placement is retained as source text."],
))

h5a = participant("alkenyl_halide", "reactant", "5a", "4-bromo-1-butene 5a", e6, smiles="C=CCCBr")
p12 = participant("product", "product", "12", "3-butenyl 4-phenyl-2-propyl-2,3-butadienoate 12", e6)
pdp4 = participant("palladium_tetrakis", "catalyst", "Pd(PPh3)4", "tetrakis(triphenylphosphine)palladium(0)", e6, amounts=[field("amount", {"number": 5, "unit": "mol%", "raw_text": "x_Pd(PPh3)4 = 5%"}, e6)])
k2co3 = participant("potassium_carbonate", "reagent", "K2CO3", "potassium carbonate", e6, smiles="[K+].[K+].[O-]C([O-])=O", amounts=[field("amount", {"number": 1, "unit": "equiv"}, e6)])
tbab = participant("tbab", "reagent", "Bu4NBr", "tetrabutylammonium bromide", e6, smiles="CCCC[N+](CCCC)(CCCC)CCCC.[Br-]", amounts=[field("amount", {"number": 1, "unit": "equiv"}, e6)])
records.append(record(
    "p06_eq4_pd0_comparison", "Equation (4)", e6, [base_sub6, h5a, p12, pdp4, k2co3, tbab, dmf6],
    [field("solvent", "DMF", e6), field("temperature", {"number": 100, "unit": "°C"}, e6), field("reaction_time", {"number": 3, "unit": "h"}, e6)],
    [field("yield", {"number": 96, "unit": "%"}, e6, ["product"])], "[9]",
))

h5d = participant("alkenyl_halide", "reactant", "5d", "16-bromohexadec-1-ene 5d", e6)
p6j = participant("product", "product", "6j", "long-chain alkenyl-substituted butenolide 6j", e6)
records.append(record(
    "p06_eq5_long_chain", "Equation (5)", e6, [base_sub6, h5d, p6j, pdoac, dmf6],
    [field("solvent", "DMF", e6), field("temperature", {"number": 100, "unit": "°C"}, e6), field("reaction_time", {"number": 9, "unit": "h"}, e6)],
    [field("yield", {"number": 18, "unit": "%"}, e6, ["product"])], "[9]",
))

# Page 6 only shows the header/general arrow of Table 4; its rows begin on page 7.
table4_participants = [
    participant("generic_allenoic_acid", "reactant", "1", "generic 2,3-allenoic acid 1 (R1/R2 variable)", e6),
    participant("printed_agent", "unspecified_agent", "C3H7I", "printed C3H7I agent; exact role not assigned from the header alone", e6),
    participant("generic_product", "product", "13", "generic bi-butenolide 13", e6),
    participant("pdcl2", "catalyst", "PdCl2", "palladium(II) chloride", e6, amounts=[field("amount", {"number": 5, "unit": "mol%", "raw_text": "x_PdCl2 = 5%"}, e6)]),
    participant("dma", "solvent", "DMA", "N,N-dimethylacetamide", e6, smiles="CC(=O)N(C)C"),
]
records.append(nonexperimental_record(
    "p06_table4_general_scheme", "Table 4 header", "general_scheme", e6, table4_participants,
    [field("solvent", "DMA", e6), field("temperature", {"number": 80, "unit": "°C"}, e6)],
    ["Table 4 is assigned to prior publication [10].", "Only the generic arrow and shared header conditions are on page 6; the row data begin on page 7."],
    ["The printed C3H7I agent's precise function and quantity are not established by the page-6 header.", "No Table 4 row was imported because page 7 is outside this extraction scope."],
))


OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")

ids = [r["record_id"] for r in records]
by_prefix = lambda prefix: [rid for rid in ids if rid.startswith(f"{DOC}:{prefix}")]
coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1,
            "state": "attempted",
            "regions": [
                {
                    "region": "整页标题、摘要、关键词与引言正文",
                    "finding": "无可逐项建模的实验；摘要只概述CuCl/Pd催化环化、偶联和氧化二聚，正文为背景及引用工作。",
                    "evidence_ids": ev(1),
                }
            ],
            "record_ids": [],
            "unresolved": ["摘要不提供单个实验的反应物配比、温度、时间或逐产物收率，未据此虚构记录。"],
        },
        {
            "page": 2,
            "state": "attempted",
            "regions": [
                {
                    "region": "Table 1顶部通式箭头与共享条件",
                    "finding": "引用文献[6]的CuCl催化2,3-联烯酸环化通式；共享条件为MeOH、CuCl 4 mol%、Ar、reflux、2 h。",
                    "evidence_ids": ev(2),
                },
                {
                    "region": "Table 1第1至15行",
                    "finding": "逐行建立15条prior-work literature_example记录；保留R1/R2/R3、底物/产物标签及78–97%逐行收率。",
                    "evidence_ids": ev(2),
                },
                {
                    "region": "Table 1下方正文",
                    "finding": "方法比较和Pd(0)既往工作讨论，不是额外的本篇逐项实验。",
                    "evidence_ids": ev(2),
                },
            ],
            "record_ids": by_prefix("p02_"),
            "unresolved": [
                "Table 1未在本页给出反应物用量、后处理、纯化或收率测定基础。",
                "底物/产物由通用R基骨架加逐行取代基表示，未强行生成完整SMILES。",
            ],
        },
        {
            "page": 3,
            "state": "attempted",
            "regions": [
                {
                    "region": "Table 2通式箭头、共享条件及第1至17行",
                    "finding": "引用文献[8]的PdCl2催化2,3-联烯酸与烯丙基卤化物偶联；逐行建立17条literature_example，保留50 °C、各行时间与收率。",
                    "evidence_ids": ev(3),
                },
                {
                    "region": "Table 2下方手性转移与两个对照实验正文",
                    "finding": "手性转移条件细节及Eq. (1)/(2)结构位于第4页；正文明确Eq. (1)为91% 4q、Eq. (2)为4q:4qA=17:1且合计19%，对应记录与第4页图像合并证据。",
                    "evidence_ids": ev(3),
                },
            ],
            "record_ids": by_prefix("p03_") + [f"{DOC}:p04_eq1_control", f"{DOC}:p04_eq2_control"],
            "unresolved": [
                "Table 2第15行73%带上标b，但第1–6页看不到脚注b定义；未猜测其条件或收率性质。",
                "Table 2未给反应物用量、后处理、纯化或收率测定基础。",
            ],
        },
        {
            "page": 4,
            "state": "attempted",
            "regions": [
                {
                    "region": "Scheme 1手性转移条件矩阵",
                    "finding": "按每条温度/时间线建立6条独立literature_example，分别保留起始ee、温度、时间、产率和产物ee；没有按相同产物标签合并。",
                    "evidence_ids": ev(4),
                },
                {
                    "region": "Equation (1)反应箭头",
                    "finding": "1a与3-chloro-1-butene 3e在PdCl2/DMA、50 °C、16 h下生成4q，91%；与第3页正文证据合并为一条。",
                    "evidence_ids": [f"{DOC}:page4:image", f"{DOC}:page4:text", f"{DOC}:page3:text"],
                },
                {
                    "region": "Equation (2)反应箭头",
                    "finding": "1a与1-chloro-2-butene 3f在PdCl2/DMA、50 °C、35.5 h下生成4q和4qA，合计19%，比例17:1；作为独立对照实验。",
                    "evidence_ids": [f"{DOC}:page4:image", f"{DOC}:page4:text", f"{DOC}:page3:text"],
                },
                {
                    "region": "Table 3标题、通式箭头与共享条件",
                    "finding": "通式给出Pd(OAc)2 5 mol%、DMF、90–100 °C；逐行数据在第5页，不把通式单独冒充实验。",
                    "evidence_ids": ev(4),
                },
            ],
            "record_ids": by_prefix("p04_"),
            "unresolved": [
                "Scheme 1未给反应物配比、后处理、纯化和收率测定基础。",
                "轴手性底物和产物的完整立体SMILES未从图示自动确定；保留标签、旋光符号与ee。",
            ],
        },
        {
            "page": 5,
            "state": "attempted",
            "regions": [
                {
                    "region": "Table 3第1至8行",
                    "finding": "结合第4页共享表头，逐行建立8条引用文献[9]的literature_example；保留n=2/3、时间和23–58%收率。",
                    "evidence_ids": [f"{DOC}:page5:image", f"{DOC}:page5:text", f"{DOC}:page4:image", f"{DOC}:page4:text"],
                },
                {
                    "region": "Scheme 2 possible reaction pathways全部箭头",
                    "finding": "机理图，包含Path A与Path B及中间体7–11；建立1条mechanism记录，但不作为reported_experiment或表格实验行。",
                    "evidence_ids": ev(5),
                },
            ],
            "record_ids": by_prefix("p05_"),
            "unresolved": [
                "Table 3未给反应物用量、后处理、纯化或收率测定基础。",
                "Scheme 2箭头为提议机理而非独立实验；未把中间体当作已分离产物。",
            ],
        },
        {
            "page": 6,
            "state": "attempted",
            "regions": [
                {
                    "region": "Equation (3)氘标记实验箭头",
                    "finding": "1a与氘代homoallyl bromide 5c在Pd(OAc)2/DMF、80–90 °C、1.5 h下给6i，52%；氘位点以原文观察保留。",
                    "evidence_ids": ev(6),
                },
                {
                    "region": "Equation (4)Pd(0)对照箭头",
                    "finding": "1a与5a在Pd(PPh3)4 5 mol%、K2CO3 1 equiv、Bu4NBr 1 equiv、DMF、100 °C、3 h下给酯12，96%；脚注式新增试剂及当量均已结构化。",
                    "evidence_ids": ev(6),
                },
                {
                    "region": "Equation (5)长链迁移实验箭头",
                    "finding": "1a与16-bromohexadec-1-ene 5d在Pd(OAc)2/DMF、100 °C、9 h下给6j，18%。",
                    "evidence_ids": ev(6),
                },
                {
                    "region": "Table 4标题与通式箭头",
                    "finding": "仅见引用文献[10]的氧化二聚通式和共享条件；建立1条general_scheme记录。逐行结果从第7页开始，超出本次覆盖范围，未从后页导入。",
                    "evidence_ids": ev(6),
                },
            ],
            "record_ids": by_prefix("p06_"),
            "unresolved": [
                "5c/6i的氘代结构未编码为立体/同位素SMILES；仅保留来源文字中的氘位置。",
                "Table 4逐行数据位于第7页，本次不声明覆盖且未建立其行记录。",
                "Eq. (3)–(5)未给反应物绝对用量、后处理、纯化或收率测定基础。",
            ],
        },
    ],
}
COVERAGE_OUT.parent.mkdir(parents=True, exist_ok=True)
COVERAGE_OUT.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

tasks = json.loads(TASKS_OUT.read_text())
for task in tasks:
    prefix = f"{DOC}:page"
    if task.get("document_id") != DOC or not task.get("task_id", "").startswith(prefix):
        continue
    try:
        page = int(task["task_id"].split(":page", 1)[1].split(":", 1)[0])
    except (IndexError, ValueError):
        continue
    if 1 <= page <= 6:
        task["state"] = "attempted"
        task["reason"] = "Original page image visually inspected; findings and unresolved limits are recorded in coverage/pages_0001_0006.json."
TASKS_OUT.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({
    "records_output": str(OUT.relative_to(ROOT)),
    "coverage_output": str(COVERAGE_OUT.relative_to(ROOT)),
    "records": len(records),
    "coverage_pages": len(coverage["pages"]),
    "tasks_attempted": sum(t.get("state") == "attempted" for t in tasks),
}, ensure_ascii=False))
