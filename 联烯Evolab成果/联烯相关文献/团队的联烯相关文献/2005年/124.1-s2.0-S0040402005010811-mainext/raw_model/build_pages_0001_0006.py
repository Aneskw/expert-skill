#!/usr/bin/env python3
"""Build evidence-linked machine records for source.pdf pages 1-6.

This file is intentionally data-driven and writes only the raw machine submission.
The project merge tool remains responsible for normalization and quarantine.
"""
from __future__ import annotations

import json
from pathlib import Path


DOC = "doc_b62df268eae80c99"
OUT = Path(__file__).with_name("extracted_records_pages_0001_0006.json")


def ev(*pages: int, corr: bool = False) -> list[str]:
    values: list[str] = []
    for page in pages:
        values.extend([f"{DOC}:page{page}:text", f"{DOC}:page{page}:image"])
    if corr:
        values.append(f"{DOC}:page8:text")
    return list(dict.fromkeys(values))


def fact(value, evidence=()):
    return {
        "value": value,
        "evidence_ids": list(evidence),
        "verification": "missing" if value is None else "unreviewed",
    }


def qty(number, unit, raw_text=None, **extra):
    value = {"number": number, "unit": unit}
    if raw_text is not None:
        value["raw_text"] = raw_text
    value.update(extra)
    return value


def field(name, value, evidence, targets=None):
    item = {"name": name, "fact": fact(value, evidence if value is not None else ())}
    if targets:
        item["target_entity_ids"] = targets
    return item


def participant(entity_id, role, label, name, smiles, evidence, amounts=()):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence if label is not None else ()),
        "name": fact(name, evidence if name is not None else ()),
        "smiles": fact(smiles, evidence if smiles is not None else ()),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": list(amounts),
    }


def amount_fields(evidence, mass=None, amount=None, volume=None, equivalents=None, loading=None):
    fields = []
    if mass:
        fields.append(field("mass", qty(*mass), evidence))
    if amount:
        fields.append(field("amount", qty(*amount), evidence))
    if volume:
        fields.append(field("volume", qty(*volume), evidence))
    if equivalents is not None:
        fields.append(field("equivalents", qty(equivalents, "equiv"), evidence))
    if loading is not None:
        fields.append(field("catalyst_loading", qty(loading, "mol%"), evidence))
    return fields


def record(rid, source_id, kind, evidence, participants, steps, outcomes, notes, unresolved):
    return {
        "record_id": f"{DOC}:{rid}",
        "document_id": DOC,
        "source_reaction_id": source_id,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": list(dict.fromkeys(evidence)),
        "participants": participants,
        "steps": steps,
        "outcomes": outcomes,
        "notes": [fact(value, note_ev) for value, note_ev in notes],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved,
        },
    }


ACID_NAMES = {
    "1a": "2-methyl-3-(n-butyl)penta-3,4-dienoic acid",
    "1b": "3-(n-butyl)penta-3,4-dienoic acid",
    "1c": "2-ethyl-3-(n-butyl)penta-3,4-dienoic acid",
    "1d": "2-(n-propyl)-3-(n-butyl)penta-3,4-dienoic acid",
    "1e": "2,3-dimethylpenta-3,4-dienoic acid",
    "1f": "2-methyl-3-(n-heptyl)penta-3,4-dienoic acid",
    "1g": "2-methyl-3-(tert-butyl)penta-3,4-dienoic acid",
    "1h": "2-methyl-3-allylpenta-3,4-dienoic acid",
    "1i": "2-methyl-3-benzylpenta-3,4-dienoic acid",
    "1j": "2-(n-propyl)penta-3,4-dienoic acid",
    "1k": "penta-3,4-dienoic acid",
}

ACID_SMILES = {
    "1a": "O=C(O)C(C)C(CCCC)=C=C",
    "1b": "O=C(O)CC(CCCC)=C=C",
    "1c": "O=C(O)C(CC)C(CCCC)=C=C",
    "1d": "O=C(O)C(CCC)C(CCCC)=C=C",
    "1e": "O=C(O)C(C)C(C)=C=C",
    "1f": "O=C(O)C(C)C(CCCCCCC)=C=C",
    "1g": "O=C(O)C(C)C(C(C)(C)C)=C=C",
    "1h": "O=C(O)C(C)C(CC=C)=C=C",
    "1i": "O=C(O)C(C)C(Cc1ccccc1)=C=C",
    "1j": "O=C(O)C(CCC)C=C=C",
    "1k": "O=C(O)CC=C=C",
}

PRODUCT_NAMES = {
    "3a": "3-methyl-4-(n-butyl)-5-methylene-2(5H)-furanone",
    "3b": "5-methylene-4-(n-butyl)-2(5H)-furanone",
    "3c": "3-ethyl-4-(n-butyl)-5-methylene-2(5H)-furanone",
    "3d": "3-(n-propyl)-4-(n-butyl)-5-methylene-2(5H)-furanone",
    "3e": "3,4-dimethyl-5-methylene-2(5H)-furanone",
    "3f": "3-methyl-4-(n-heptyl)-5-methylene-2(5H)-furanone",
    "3g": "3-methyl-4-(tert-butyl)-5-methylene-2(5H)-furanone",
    "3h": "3-methyl-4-allyl-5-methylene-2(5H)-furanone",
    "3i": "3-methyl-4-benzyl-5-methylene-2(5H)-furanone",
    "3j": "3-(n-propyl)-5-methylene-2(5H)-furanone",
    "3k": "5-methylene-2(5H)-furanone (protoanemonin)",
}

PRODUCT_SMILES = {
    "3a": "C=C1OC(=O)C(C)=C1CCCC",
    "3b": "C=C1OC(=O)C=C1CCCC",
    "3c": "C=C1OC(=O)C(CC)=C1CCCC",
    "3d": "C=C1OC(=O)C(CCC)=C1CCCC",
    "3e": "C=C1OC(=O)C(C)=C1C",
    "3f": "C=C1OC(=O)C(C)=C1CCCCCCC",
    "3g": "C=C1OC(=O)C(C)=C1C(C)(C)C",
    "3h": "C=C1OC(=O)C(C)=C1CC=C",
    "3i": "C=C1OC(=O)C(C)=C1Cc2ccccc2",
    "3j": "C=C1OC(=O)C(CCC)=C1",
    "3k": "C=C1OC(=O)C=C1",
}


records = []

# Prior-work generic Scheme 1: retained as literature context, not a current-paper experiment.
e = ev(1)
records.append(record(
    "scheme1_prior_alpha_allenoic_acid_cyclization", "Scheme 1", "literature_example", e,
    [
        participant("scheme1_alpha_allenoic_acid", "reactant", "generic alpha-allenoic acid", None, None, e),
        participant("scheme1_r4x", "reactant", "R4-X", None, None, e),
        participant("scheme1_pd_ag", "catalyst", "Pd(0)/Ag+", "palladium(0)/silver catalyst system", None, e),
        participant("scheme1_product", "product", "generic substituted butenolide", None, None, e),
    ],
    [{"step_id": "scheme1_arrow", "participant_ids": ["scheme1_alpha_allenoic_acid", "scheme1_r4x", "scheme1_pd_ag"],
      "conditions": [field("base", "unspecified base", e), field("solvent", "unspecified solvent", e)]}],
    [],
    [("Scheme 1 summarizes the authors' cited prior methodologies (reference 5) and is not a newly detailed experiment in this paper.", e)],
    ["Generic R groups prevent complete molecule structures.", "No scale, time, temperature, yield, workup, or purification is reported in Scheme 1."],
))

# Scheme 2 / detailed page-4 exploratory coupling-cyclization: one physical experiment, two products.
e = ev(1, 4)
parts = [
    participant("scheme2_1a", "reactant", "1a", ACID_NAMES["1a"], ACID_SMILES["1a"], e,
                amount_fields(ev(4), mass=(86, "mg"), amount=(5.0, "mmol"))),
    participant("scheme2_phi", "reactant", "PhI", "iodobenzene", "Ic1ccccc1", e,
                amount_fields(ev(4), volume=(85, "uL"), amount=(7.5, "mmol"))),
    participant("scheme2_k2co3", "reagent", "K2CO3", "potassium carbonate", "[K+].[K+].[O-]C([O-])=O", e,
                amount_fields(ev(4), mass=(273, "mg"), amount=(2.0, "mmol"), equivalents=4)),
    participant("scheme2_agno3", "catalyst", "AgNO3", "silver nitrate", "[Ag+].[O-][N+](=O)[O-]", e,
                amount_fields(ev(4), mass=(8, "mg"), amount=(0.05, "mmol"), loading=10)),
    participant("scheme2_pd", "catalyst", "Pd(PPh3)4", "tetrakis(triphenylphosphine)palladium(0)", None, e,
                amount_fields(ev(4), mass=(30, "mg"), amount=(0.025, "mmol"), loading=5)),
    participant("scheme2_mecn", "solvent", "CH3CN", "acetonitrile", "CC#N", e,
                amount_fields(ev(4), volume=(3, "mL"))),
    participant("scheme2_2a", "product", "2a", "3-methyl-4-(n-butyl)-5-benzyl-2(5H)-furanone",
                "O=C1OC(Cc2ccccc2)C(CCCC)=C1C", e, amount_fields(ev(4), mass=(30, "mg"))),
    participant("scheme2_3a", "product", "3a", PRODUCT_NAMES["3a"], PRODUCT_SMILES["3a"], e,
                amount_fields(ev(4), mass=(9, "mg"))),
]
records.append(record(
    "scheme2_exploratory_coupling_cyclization", "Scheme 2 / section 3.1 after 1k", "reported_experiment", e,
    parts,
    [{"step_id": "reaction", "participant_ids": [p["entity_id"] for p in parts[:6]], "conditions": [
        field("temperature", qty(70, "°C"), e), field("time", qty(33, "h"), ev(4)),
        field("solvent", "CH3CN", e), field("atmosphere", None, ()),
    ]},
     {"step_id": "separation", "participant_ids": ["scheme2_2a", "scheme2_3a"], "conditions": [
         field("purification", "silica-gel chromatography; petroleum ether/ether = 5/1", ev(4))
     ]}],
    [
        field("yield", qty(24, "%"), e, ["scheme2_2a"]),
        field("yield", qty(11, "%"), e, ["scheme2_3a"]),
        field("yield_measurement_basis", "isolated after chromatographic separation", ev(4), ["scheme2_2a", "scheme2_3a"]),
    ],
    [("The printed page-4 amounts 5.0 mmol for 86 mg of 1a and 7.5 mmol for 85 uL PhI are internally inconsistent with the printed mol%/equivalent values; they are preserved without decimal correction.", ev(4))],
    ["Printed scale/stoichiometry is internally inconsistent and requires source or author correction.", "Atmosphere is not stated for this exploratory experiment.", "Candidate structures remain unverified."],
))


# Table 1: one independent optimization record per row.
table1 = [
    (1, "Pd(PPh3)4", "PhI", 1.5, 24, qty(29, "%"), None),
    (2, "PdCl2(PPh3)2", "CuCl2", 4, 12, qty(87, "%", "<87%", qualifier="lt"), "air; product not pure"),
    (3, "PdCl2(PPh3)2", "CuCl2", 4, 12, qty(88, "%"), "N2"),
    (4, "PdCl2(PPh3)2", "CuBr2", 5, 24, "complicated", None),
    (5, "PdCl2(PPh3)2", "CuCl2", 4, 12, qty(50, "%", "<50%", qualifier="lt"), "1 atm pure O2; product not pure"),
    (6, "PdCl2(PPh3)2", "CuCl2", 4, 12, qty(70, "%", "<70%", qualifier="lt"), "water-addition footnote applied; product not pure"),
    (7, "PdCl2(PPh3)2", "CuCl2", 2.5, 24, qty(75, "%"), None),
    (8, "PdCl2(PPh3)2", "CuCl2", 0.8, 24, qty(22, "%"), None),
    (9, "PdCl2", "CuCl2", 4, 24, qty(54, "%"), None),
    (10, "Pd(OAc)2", "CuCl2", 4, 24, qty(40, "%"), None),
    (11, "PdCl2(CH3CN)2", "CuCl2", 4, 24, qty(34, "%"), None),
    (12, None, "CuCl2", 4, 24, qty(60, "%"), "no palladium catalyst"),
    (13, None, "CuCl2", 1, 12, qty(18, "%"), "no palladium catalyst"),
    (14, "PdCl2(PPh3)2", "CuCl2", 4, 12, qty(70, "%"), "no K2CO3"),
    (15, "PdCl2(PPh3)2", "CuCl2", 4, 12, qty(87, "%", "<87%", qualifier="lt"), "modified K2CO3-loading footnote applied; product not pure"),
    (16, "PdCl2(PPh3)2", "CuCl2", 4, 12, qty(89, "%"), "modified K2CO3-loading footnote applied"),
]

for entry, catalyst, additive, add_eq, time_h, result, exception in table1:
    e = ev(2)
    prefix = f"table1_e{entry}"
    parts = [
        participant(f"{prefix}_1a", "reactant", "1a", ACID_NAMES["1a"], ACID_SMILES["1a"], e),
        participant(f"{prefix}_3a", "product", "3a", PRODUCT_NAMES["3a"], PRODUCT_SMILES["3a"], e),
    ]
    reaction_ids = [f"{prefix}_1a"]
    if catalyst:
        parts.append(participant(f"{prefix}_catalyst", "catalyst", catalyst, catalyst, None, e,
                                 amount_fields(e, loading=5)))
        reaction_ids.append(f"{prefix}_catalyst")
    parts.append(participant(f"{prefix}_additive", "reagent", additive, additive,
                             {"PhI": "Ic1ccccc1", "CuCl2": "[Cl-].[Cl-].[Cu+2]", "CuBr2": "[Br-].[Br-].[Cu+2]"}[additive], e,
                             amount_fields(e, equivalents=add_eq)))
    reaction_ids.append(f"{prefix}_additive")
    if entry != 14:
        base_eq = 3 if entry == 15 else 5 if entry == 16 else 4
        parts.append(participant(f"{prefix}_base", "reagent", "K2CO3", "potassium carbonate",
                                 "[K+].[K+].[O-]C([O-])=O", e, amount_fields(e, equivalents=base_eq)))
        reaction_ids.append(f"{prefix}_base")
    if entry == 6:
        parts.append(participant(f"{prefix}_water", "reagent", "H2O", "water", "O", e,
                                 amount_fields(e, equivalents=4)))
        reaction_ids.append(f"{prefix}_water")
    parts.append(participant(f"{prefix}_dmf", "solvent", "DMF", "N,N-dimethylformamide", "CN(C)C=O", e))
    reaction_ids.append(f"{prefix}_dmf")
    if entry == 2:
        atmosphere = "air"
    elif entry == 3:
        atmosphere = "N2"
    elif entry == 5:
        atmosphere = "1 atm pure O2"
    else:
        atmosphere = None
    notes = []
    if exception:
        notes.append((exception, e))
    unresolved = ["Reaction scale, workup, purification, and yield measurement basis are not stated for this Table 1 row.",
                  "Candidate structures are not independently verified."]
    if atmosphere is None:
        unresolved.append("Atmosphere is not explicitly assigned to this row.")
    records.append(record(
        f"table1_optimization_entry_{entry:02d}", f"Table 1 entry {entry}", "optimization_entry", e, parts,
        [{"step_id": "reaction", "participant_ids": reaction_ids, "conditions": [
            field("temperature", qty(70, "°C"), e), field("time", qty(time_h, "h"), e),
            field("solvent", "DMF", e), field("atmosphere", atmosphere, e if atmosphere is not None else ()),
        ]}],
        [field("yield" if isinstance(result, dict) else "reaction_result", result, e, [f"{prefix}_3a"]),
         field("yield_measurement_basis", None, (), [f"{prefix}_3a"])],
        notes, unresolved,
    ))


# Individual hydrolyses furnishing 1a-1k. General-procedure volumes are not
# propagated to differently scaled examples; their nominal values remain notes.
hydrolysis = {
    "1a": ("A", 3, (1044, "mg"), (5.3, "mmol"), (250, "mg"), (10.4, "mmol"), (817, "mg"), 91),
    "1b": ("A", 3, (1.132, "g"), (6.2, "mmol"), (314, "mg"), (13, "mmol"), (275, "mg"), 29),
    "1c": ("A", 3, (3654, "mg"), (17.4, "mmol"), (945, "mg"), (39.4, "mmol"), (3060, "mg"), 97),
    "1d": ("A", 3, (4613, "mg"), (20.6, "mmol"), (1198, "mg"), (50, "mmol"), (3300, "mg"), 82),
    "1e": ("A", 4, (1.541, "g"), (10, "mmol"), (480, "mg"), (20, "mmol"), (639, "mg"), 51),
    "1f": ("A", 4, (1.357, "g"), (5.7, "mmol"), (297, "mg"), (12.4, "mmol"), (639, "mg"), 53),
    "1g": ("A", 4, (538, "mg"), (2.7, "mmol"), (145, "mg"), (5.5, "mmol"), (143, "mg"), 31),
    "1h": ("A", 4, (2745, "mg"), (15.2, "mmol"), (719, "mg"), (30, "mmol"), (553, "mg"), 24),
    "1i": ("A", 4, (1.798, "g"), (7.8, "mmol"), (402, "mg"), (16.8, "mmol"), (1.179, "g"), 75),
    "1j": ("B", 4, (1693, "mg"), (10, "mmol"), None, None, (453, "mg"), 33),
    "1k": ("B", 4, (2038, "mg"), (16.2, "mmol"), None, None, (1360, "mg"), 86),
}

for label, (proc, detail_page, ester_mass, ester_amount, reagent_mass, reagent_amount, product_mass, yield_pct) in hydrolysis.items():
    general_pages = (2, 3) if proc == "A" else (3,)
    e = ev(*tuple(dict.fromkeys((*general_pages, detail_page))))
    prefix = f"hydrolysis_{label}"
    detail_ev = ev(detail_page)
    parts = [
        participant(f"{prefix}_ester", "reactant", f"corresponding beta-allenoic acid ethyl ester for {label}",
                    f"corresponding ethyl ester precursor to {label}", None, detail_ev,
                    amount_fields(detail_ev, mass=ester_mass, amount=ester_amount)),
        participant(f"{prefix}_product", "product", label, ACID_NAMES[label], ACID_SMILES[label], detail_ev,
                    amount_fields(detail_ev, mass=product_mass)),
    ]
    reaction_ids = [f"{prefix}_ester"]
    if proc == "A":
        parts.extend([
            participant(f"{prefix}_lioh", "reagent", "LiOH", "lithium hydroxide", "[Li+].[OH-]", detail_ev,
                        amount_fields(detail_ev, mass=reagent_mass, amount=reagent_amount)),
            participant(f"{prefix}_water", "solvent", "H2O", "water", "O", ev(2, 3)),
            participant(f"{prefix}_meoh", "solvent", "MeOH", "methanol", "CO", ev(2, 3)),
        ])
        reaction_ids.extend([f"{prefix}_lioh", f"{prefix}_water", f"{prefix}_meoh"])
        procedure_note = "General conditions A state 12 mL H2O and 24 mL MeOH at a nominal 6 mmol ester scale; exact solvent volumes for this differently scaled example are not separately stated."
        workup = "acidify with 1 N HCl; extract with ether; dry over anhydrous Na2SO4; evaporate; flash chromatography on silica gel (CH2Cl2/MeOH = 10/1)"
    else:
        parts.extend([
            participant(f"{prefix}_hcl", "reagent", "20% HCl", "20% hydrochloric acid", None, ev(3)),
            participant(f"{prefix}_dioxane", "solvent", "1,4-dioxane", "1,4-dioxane", "O1CCOCC1", ev(3)),
            participant(f"{prefix}_thf", "solvent", "THF", "tetrahydrofuran", "C1CCOC1", ev(3)),
        ])
        reaction_ids.extend([f"{prefix}_hcl", f"{prefix}_dioxane", f"{prefix}_thf"])
        procedure_note = "General conditions B state 27 mL 20% HCl, 20 mL 1,4-dioxane, and 7 mL THF at a nominal 6.6 mmol ester scale; exact solvent/reagent volumes for this differently scaled example are not separately stated."
        workup = "extract with ether; dry over anhydrous Na2SO4; evaporate; flash chromatography on silica gel (CH2Cl2/MeOH = 10/1)"
    records.append(record(
        f"hydrolysis_to_{label}", f"Section 3.1.{ord(label[-1]) - 96}", "reported_experiment", e, parts,
        [{"step_id": "hydrolysis", "participant_ids": reaction_ids, "conditions": [
            field("operation", "stirred", e), field("temperature", qty(30, "°C"), e),
            field("time", qty(3, "d"), e), field("atmosphere", None, ()),
        ]},
         {"step_id": "workup_and_purification", "participant_ids": [f"{prefix}_product"],
          "conditions": [field("workup", workup, e), field("purification", "flash chromatography on silica gel; CH2Cl2/MeOH = 10/1", e)]}],
        [field("yield", qty(yield_pct, "%"), detail_ev, [f"{prefix}_product"]),
         field("yield_measurement_basis", "isolated after flash chromatography", e, [f"{prefix}_product"])],
        [(f"Conditions {proc} were explicitly invoked for this example.", detail_ev), (procedure_note, ev(*general_pages))],
        ["The ester precursor is referred to only as the corresponding ester, so its SMILES is left null.",
         "Exact general-procedure liquid volumes at this example's reported scale are not stated.",
         "Atmosphere is not stated.", "No supporting information was explicitly associated."],
    ))


# Scope Table 2 plus the matching detailed sections 3.2.1-3.2.11. The page-8
# corrigendum is necessary context: every printed Pd(PPh3)4 in 3.2.1-3.2.11 is
# corrected to PdCl2(PPh3)2.
cyclization = {
    "3a": ("1a", 4, (84, "mg"), (0.5, "mmol"), (266, "mg"), (2.0, "mmol"), (277, "mg"), (2.0, "mmol"), (73, "mg"), 88),
    "3b": ("1b", 5, (74, "mg"), (0.5, "mmol"), (267, "mg"), (2.0, "mmol"), (276, "mg"), (2.0, "mmol"), (57, "mg"), 78),
    "3c": ("1c", 5, (92, "mg"), (0.5, "mmol"), (282, "mg"), (2.0, "mmol"), (286, "mg"), (2.0, "mmol"), (74, "mg"), 81),
    "3d": ("1d", 5, (98, "mg"), (0.5, "mmol"), (272, "mg"), (2.0, "mmol"), (278, "mg"), (2.0, "mmol"), (81, "mg"), 84),
    "3e": ("1e", 5, (63, "mg"), (0.5, "mmol"), (270, "mg"), (2.0, "mmol"), (281, "mg"), (2.0, "mmol"), (40, "mg"), 64),
    "3f": ("1f", 5, (105, "mg"), (0.5, "mmol"), (277, "mg"), (2.0, "mmol"), (282, "mg"), (2.0, "mmol"), (90, "mg"), 84),
    "3g": ("1g", 5, (77, "mg"), (0.46, "mmol"), (250, "mg"), (1.85, "mmol"), (262, "mg"), (1.90, "mmol"), (53, "mg"), 71),
    "3h": ("1h", 5, (77, "mg"), (0.5, "mmol"), (269, "mg"), (2.0, "mmol"), (280, "mg"), (2.0, "mmol"), (50, "mg"), 66),
    "3i": ("1i", 5, (101, "mg"), (0.5, "mmol"), (264, "mg"), (2.0, "mmol"), (282, "mg"), (2.0, "mmol"), (90, "mg"), 89),
    "3j": ("1j", 5, (70, "mg"), (0.5, "mmol"), (270, "mg"), (2.0, "mmol"), (286, "mg"), (2.0, "mmol"), (36, "mg"), 51),
    "3k": ("1k", 5, (98, "mg"), (1.0, "mmol"), (545, "mg"), (4.0, "mmol"), (550, "mg"), (4.0, "mmol"), None, 31),
}

for product_label, data in cyclization.items():
    substrate_label, detail_page, sub_mass, sub_amount, cu_mass, cu_amount, k_mass, k_amount, prod_mass, yield_pct = data
    e = ev(2, 4, detail_page, corr=True)
    detail_ev = ev(detail_page)
    prefix = f"cyclization_{product_label}"
    parts = [
        participant(f"{prefix}_substrate", "reactant", substrate_label, ACID_NAMES[substrate_label], ACID_SMILES[substrate_label], detail_ev,
                    amount_fields(detail_ev, mass=sub_mass, amount=sub_amount)),
        participant(f"{prefix}_pd", "catalyst", "PdCl2(PPh3)2", "bis(triphenylphosphine)palladium(II) dichloride", None,
                    [f"{DOC}:page2:text", f"{DOC}:page2:image", f"{DOC}:page4:text", f"{DOC}:page4:image", f"{DOC}:page8:text"],
                    amount_fields([f"{DOC}:page2:text", f"{DOC}:page2:image", f"{DOC}:page8:text"], loading=5)),
        participant(f"{prefix}_cucl2", "reagent", "anhydrous CuCl2", "anhydrous copper(II) chloride", "[Cl-].[Cl-].[Cu+2]", detail_ev,
                    amount_fields(detail_ev, mass=cu_mass, amount=cu_amount)),
        participant(f"{prefix}_k2co3", "reagent", "K2CO3", "potassium carbonate", "[K+].[K+].[O-]C([O-])=O", detail_ev,
                    amount_fields(detail_ev, mass=k_mass, amount=k_amount)),
        participant(f"{prefix}_dmf", "solvent", "anhydrous DMF", "anhydrous N,N-dimethylformamide", "CN(C)C=O", ev(4, detail_page),
                    amount_fields(detail_ev, volume=(3, "mL"))),
        participant(f"{prefix}_product", "product", product_label, PRODUCT_NAMES[product_label], PRODUCT_SMILES[product_label], detail_ev,
                    amount_fields(detail_ev, mass=prod_mass) if prod_mass else ()),
    ]
    basis = "NMR yield using p-methoxyiodobenzene as internal standard" if product_label == "3k" else "isolated after column chromatography"
    notes = [
        ("The corrigendum on PDF page 8 states that Pd(PPh3)4 in Sections 3.2.1-3.2.11 must be read as PdCl2(PPh3)2.", [f"{DOC}:page8:text"]),
    ]
    unresolved = ["Candidate substrate and product SMILES are based on legible names/drawings but remain unverified.",
                  "Supporting-information association is unestablished."]
    if product_label == "3k":
        unresolved.append("Product mass and isolation details are not reported; only an NMR yield is given.")
    records.append(record(
        f"table2_cyclization_{substrate_label}_to_{product_label}", f"Table 2 / Section 3.2.{ord(product_label[-1]) - 96}",
        "substrate_scope_entry", e, parts,
        [{"step_id": "cyclization", "participant_ids": [p["entity_id"] for p in parts[:5]], "conditions": [
            field("operation", "stirred", ev(4, detail_page)), field("atmosphere", "N2", ev(2, 4)),
            field("temperature", qty(70, "°C"), ev(2, 4, detail_page)), field("time", qty(12, "h"), ev(2, 4, detail_page)),
            field("solvent", "anhydrous DMF", ev(4, detail_page)),
        ]},
         {"step_id": "workup_and_purification", "participant_ids": [f"{prefix}_product"], "conditions": [
             field("workup", "dilute with ether (50 mL), wash with brine, dry over anhydrous Na2SO4, evaporate", ev(4)),
             field("purification", "column chromatography on silica gel; petroleum ether/ether = 10/1", ev(4)),
         ]}],
        [field("yield", qty(yield_pct, "%"), detail_ev, [f"{prefix}_product"]),
         field("yield_measurement_basis", basis, ev(2, 4, detail_page), [f"{prefix}_product"])],
        notes, unresolved,
    ))


# Scheme 3 is explicitly proposed mechanism, not a performed experiment.
e = ev(2, 3)
records.append(record(
    "scheme3_proposed_catalytic_cycle", "Scheme 3", "mechanism", e,
    [
        participant("scheme3_1", "reactant", "generic beta-allenoic acid 1", None, None, e),
        participant("scheme3_base", "reagent", "Base", "unspecified base", None, e),
        participant("scheme3_cucl2", "reagent", "CuCl2", "copper(II) chloride", "[Cl-].[Cl-].[Cu+2]", e),
        participant("scheme3_pdx2l2", "catalyst", "PdX2L2", "generic palladium(II) complex", None, e),
        participant("scheme3_4", "unspecified_agent", "intermediate 4", "proposed oxypalladation intermediate", None, e),
        participant("scheme3_3", "product", "generic product 3", "generic gamma-methylene-2(5H)-furanone", None, e),
    ],
    [{"step_id": "proposed_cycle", "participant_ids": ["scheme3_1", "scheme3_base", "scheme3_cucl2", "scheme3_pdx2l2", "scheme3_4"],
      "conditions": [field("operation", "proposed endo-mode cyclic anti-oxypalladation followed by syn-beta-H elimination and catalyst reoxidation", e)]}],
    [],
    [("Scheme 3 is a proposed catalytic mechanism and does not constitute a separately reported experiment.", e)],
    ["Generic R1/R2/X/L groups and proposed intermediates prevent complete structures.", "No independent experimental outcome is assigned to this mechanism record."],
))


OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"output": str(OUT), "records": len(records)}, ensure_ascii=False))
