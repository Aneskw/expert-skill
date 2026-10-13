#!/usr/bin/env python3
"""Build the page-1--4 machine extraction for doc_b17729c68971d1bd.

This is a source transcription artifact, not a chemistry-verification program.
The canonical dataset is updated only through reaction_tools.py merge.
"""

from __future__ import annotations

import json
from pathlib import Path


DOC = "doc_b17729c68971d1bd"
OUTDIR = Path(__file__).resolve().parent
EV = {
    page: [f"{DOC}:page{page}:text", f"{DOC}:page{page}:image"]
    for page in range(1, 5)
}


def fact(value, evidence=None):
    return {
        "value": value,
        "evidence_ids": list(evidence or []),
        "verification": "missing" if value is None else "unreviewed",
    }


def field(name, value, evidence=None, targets=None):
    result = {"name": name, "fact": fact(value, evidence)}
    if targets:
        result["target_entity_ids"] = list(targets)
    return result


def participant(entity_id, role, label, name, evidence, smiles=None, amounts=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence if label is not None else []),
        "name": fact(name, evidence if name is not None else []),
        "smiles": fact(smiles, evidence if smiles is not None else []),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": list(amounts or []),
    }


def record(suffix, kind, evidence, participants, steps, outcomes=None, notes=None, unresolved=None):
    return {
        "record_id": f"{DOC}:{suffix}",
        "document_id": DOC,
        "source_reaction_id": suffix,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": list(dict.fromkeys(evidence)),
        "participants": participants,
        "steps": steps,
        "outcomes": list(outcomes or []),
        "notes": [fact(x, evidence) for x in (notes or [])],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": list(unresolved or []),
        },
    }


def mmol(number, evidence):
    return field("reaction_scale", {"number": number, "unit": "mmol"}, evidence)


def equiv(number, evidence):
    return field("equivalents", {"number": number, "unit": "equiv"}, evidence)


def volume(number, evidence):
    return field("volume", {"number": number, "unit": "mL"}, evidence)


def pct(number):
    return {"number": number, "unit": "%"}


def degc(number):
    return {"number": number, "unit": "°C"}


records = []

# Page 1 graphical abstract: a generic transformation, not an individual batch.
p1 = EV[1]
records.append(
    record(
        "graphical_abstract_general_transformation",
        "general_scheme",
        p1,
        [
            participant("generic_allenoic_acid", "reactant", "generic 2,3-allenoic acid", "R1/R2/R3-substituted 2,3-allenoic acid", p1),
            participant("generic_benzyne_precursor", "reactant", "generic benzyne precursor", "R4-substituted 2-(trimethylsilyl)aryl triflate", p1),
            participant("kf", "reagent", "KF", "potassium fluoride", p1, "[K+].[F-]"),
            participant("18c6", "reagent", "18-crown-6", "18-crown-6", p1, "O1CCOCCOCCOCCOCCOCC1"),
            participant("thf", "solvent", "THF", "tetrahydrofuran", p1, "C1CCOC1"),
            participant("generic_chromone", "product", "generic chromone", "polysubstituted chromone", p1),
        ],
        [
            {
                "step_id": "graphical_abstract_reaction",
                "participant_ids": ["generic_allenoic_acid", "generic_benzyne_precursor", "kf", "18c6", "thf"],
                "conditions": [
                    field("solvent", "THF", p1),
                    field("temperature", degc(80), p1),
                    field("reaction_time", {"number": 12, "unit": "h"}, p1),
                ],
            }
        ],
        [
            field(
                "scope_yield_upper_statement",
                {"number": 92, "unit": "%", "qualifier": "le", "raw_text": "up to 92% yield"},
                p1,
                ["generic_chromone"],
            )
        ],
        ["The graphical abstract summarizes a reaction class; it is not an individual reported batch."],
        [
            "Generic R-group structures are not representable as verified molecules; SMILES are omitted.",
            "KF and 18-crown-6 quantities are not printed in the graphical abstract.",
        ],
    )
)


# Page 2 Scheme 1: proposed/expected coumarin pathway, not a reported batch.
p2 = EV[2]
records.append(
    record(
        "scheme1_expected_coumarin_path",
        "mechanism",
        p2,
        [
            participant("scheme1_arylanion", "reactant", "generic aryl-anion allenoate", "generic allenoic-acid/benzyne adduct", p2),
            participant("scheme1_intermediate_a", "unspecified_agent", "A", "proposed cyclic intermediate A", p2),
            participant("scheme1_coumarin", "product", "coumarin", "generic substituted coumarin", p2),
        ],
        [
            {
                "step_id": "scheme1_michael_addition",
                "participant_ids": ["scheme1_arylanion", "scheme1_intermediate_a"],
                "conditions": [field("operation", "intramolecular Michael addition", p2)],
            },
            {
                "step_id": "scheme1_protonolysis",
                "participant_ids": ["scheme1_intermediate_a", "scheme1_coumarin"],
                "conditions": [field("operation", "protonolysis", p2)],
            },
        ],
        notes=["Scheme 1 depicts the initially expected coumarin-forming pathway, not an isolated experimental result."],
        unresolved=["All structures are generic R-group drawings; SMILES are omitted."],
    )
)


# Page 2 Scheme 2: proposed mechanism for 3aa formation.
records.append(
    record(
        "scheme2_proposed_chromone_mechanism",
        "mechanism",
        p2,
        [
            participant("s2_1a", "reactant", "1a", "2-methyl-4-phenyl-2,3-butadienoic acid", p2, "O=C(O)C(C)=C=Cc1ccccc1"),
            participant("s2_2a", "reactant", "2a", "2-(trimethylsilyl)phenyl triflate", p2, "C[Si](C)(C)c1ccccc1OS(=O)(=O)C(F)(F)F"),
            participant("s2_kf", "reagent", "KF", "potassium fluoride", p2, "[K+].[F-]"),
            participant("s2_18c6", "reagent", "18-crown-6", "18-crown-6", p2, "O1CCOCCOCCOCCOCCOCC1"),
            participant("s2_a1", "unspecified_agent", "A1", "proposed aryl-anion intermediate A1", p2),
            participant("s2_b1", "unspecified_agent", "B1", "proposed cyclic intermediate B1", p2),
            participant("s2_c1", "unspecified_agent", "C1", "proposed o-(1-oxo-2,3-allenyl)phenoxide C1", p2),
            participant("s2_d1", "unspecified_agent", "D1", "proposed bicyclic intermediate D1", p2),
            participant("s2_3aa", "product", "3aa", "chromone 3aa", p2),
        ],
        [
            {"step_id": "s2_nucleophilic_addition", "participant_ids": ["s2_1a", "s2_2a", "s2_kf", "s2_18c6", "s2_a1"], "conditions": [field("operation", "nucleophilic addition to benzyne", p2)]},
            {"step_id": "s2_cyclic_1_2_addition", "participant_ids": ["s2_a1", "s2_b1"], "conditions": [field("operation", "cyclic 1,2-addition to the carbonyl group", p2)]},
            {"step_id": "s2_ring_opening", "participant_ids": ["s2_b1", "s2_c1"], "conditions": [field("operation", "four-membered-ring opening", p2)]},
            {"step_id": "s2_oxa_michael", "participant_ids": ["s2_c1", "s2_d1"], "conditions": [field("operation", "intramolecular oxa-Michael addition", p2)]},
            {"step_id": "s2_hydrolysis", "participant_ids": ["s2_d1", "s2_3aa"], "conditions": [field("operation", "hydrolysis/protonolysis", p2)]},
        ],
        notes=["Scheme 2 is the authors' mechanistic explanation and is not counted as a batch experiment."],
        unresolved=["Intermediate structures and the product SMILES have not been independently structure-verified."],
    )
)


TABLE1 = [
    # entry, solvent label/name/smiles, additives [(id,label,name,smiles,equiv)], temp, time h, 2a equiv, 3aa, 4aa, recovered 1a
    (1, "CH3CN", "acetonitrile", "CC#N", [("csf", "CsF", "cesium fluoride", "[Cs+].[F-]", 4)], "r.t.", None, 1.5, 17, 33, 0),
    (2, "THF", "tetrahydrofuran", "C1CCOC1", [("kf", "KF", "potassium fluoride", "[K+].[F-]", 2), ("18c6", "18-crown-6", "18-crown-6", "O1CCOCCOCCOCCOCCOCC1", 2)], "r.t.", None, 1.5, 82, 9, 0),
    (3, "THF", "tetrahydrofuran", "C1CCOC1", [("kf", "KF", "potassium fluoride", "[K+].[F-]", 2), ("18c6", "18-crown-6", "18-crown-6", "O1CCOCCOCCOCCOCCOCC1", 2)], 40, None, 1.5, 84, 5, 0),
    (4, "THF", "tetrahydrofuran", "C1CCOC1", [("kf", "KF", "potassium fluoride", "[K+].[F-]", 2), ("18c6", "18-crown-6", "18-crown-6", "O1CCOCCOCCOCCOCCOCC1", 2)], 60, None, 1.5, 88, 0, 0),
    (5, "THF", "tetrahydrofuran", "C1CCOC1", [("kf", "KF", "potassium fluoride", "[K+].[F-]", 2), ("18c6", "18-crown-6", "18-crown-6", "O1CCOCCOCCOCCOCCOCC1", 2)], 80, None, 1.5, 95, 0, 0),
    (6, "THF", "tetrahydrofuran", "C1CCOC1", [("kf", "KF", "potassium fluoride", "[K+].[F-]", 2)], 80, 18, 1.5, 0, 0, 51),
    (7, "THF", "tetrahydrofuran", "C1CCOC1", [("kf", "KF", "potassium fluoride", "[K+].[F-]", 1.5), ("18c6", "18-crown-6", "18-crown-6", "O1CCOCCOCCOCCOCCOCC1", 1.5)], 80, 18, 1.5, 88, 0, 0),
    (8, "THF", "tetrahydrofuran", "C1CCOC1", [("kf", "KF", "potassium fluoride", "[K+].[F-]", 2), ("18c6", "18-crown-6", "18-crown-6", "O1CCOCCOCCOCCOCCOCC1", 2)], 80, 17, 1.2, 88, 0, 0),
    (9, "1,4-dioxane", "1,4-dioxane", "O1CCOCC1", [("kf", "KF", "potassium fluoride", "[K+].[F-]", 2), ("18c6", "18-crown-6", "18-crown-6", "O1CCOCCOCCOCCOCCOCC1", 2)], 80, None, 1.5, 37, 10, 0),
    (10, "CH3CN", "acetonitrile", "CC#N", [("kf", "KF", "potassium fluoride", "[K+].[F-]", 2), ("18c6", "18-crown-6", "18-crown-6", "O1CCOCCOCCOCCOCCOCC1", 2)], 80, None, 1.5, 15, 0, 0),
    (11, "toluene", "toluene", "Cc1ccccc1", [("kf", "KF", "potassium fluoride", "[K+].[F-]", 2), ("18c6", "18-crown-6", "18-crown-6", "O1CCOCCOCCOCCOCCOCC1", 2)], 80, None, 1.5, 76, 0, 0),
    (12, "2-MeTHF", "2-methyltetrahydrofuran", "CC1CCCO1", [("kf", "KF", "potassium fluoride", "[K+].[F-]", 2), ("18c6", "18-crown-6", "18-crown-6", "O1CCOCCOCCOCCOCCOCC1", 2)], 80, None, 1.5, 76, 0, 0),
    (13, "THF", "tetrahydrofuran", "C1CCOC1", [("csf", "CsF", "cesium fluoride", "[Cs+].[F-]", 2)], 80, None, 1.5, 49, 11, 14),
    (14, "THF", "tetrahydrofuran", "C1CCOC1", [("tbat", "TBAT", "tetrabutylammonium triphenyldifluorosilicate", None, 2)], 80, None, 1.5, 51, 0, 0),
    (15, "THF", "tetrahydrofuran", "C1CCOC1", [("tbaf", "TBAF", "tetrabutylammonium fluoride", "CCCC[N+](CCCC)(CCCC)CCCC.[F-]", 2)], 80, None, 1.5, 5, 0, 7),
]

for entry, solv_label, solv_name, solv_smiles, additives, temp, time_h, eq_2a, y3, y4, rec1 in TABLE1:
    evidence = list(p2)
    if entry >= 2:
        evidence += EV[3]
    ps = [
        participant("t1_1a", "reactant", "1a", "2-methyl-4-phenyl-2,3-butadienoic acid", evidence, "O=C(O)C(C)=C=Cc1ccccc1", [mmol(0.2, p2)]),
        participant("t1_2a", "reactant", "2a", "2-(trimethylsilyl)phenyl triflate", evidence, "C[Si](C)(C)c1ccccc1OS(=O)(=O)C(F)(F)F", [equiv(eq_2a, p2)]),
        participant("t1_solvent", "solvent", solv_label, solv_name, p2, solv_smiles, [volume(2, p2)]),
        participant("t1_3aa", "product", "3aa", "chromone 3aa", p2),
        participant("t1_4aa", "product", "4aa", "2,3-allenoic acid phenyl ester 4aa", p2),
        participant("t1_internal_standard", "reagent", "CH2Br2", "dibromomethane internal standard", p2, "BrCBr"),
    ]
    for aid, label, name, smiles, loading in additives:
        ps.append(participant(f"t1_{aid}", "reagent", label, name, p2, smiles, [equiv(loading, p2)]))
    reaction_ids = ["t1_1a", "t1_2a", "t1_solvent"] + [f"t1_{a[0]}" for a in additives]
    temp_value = temp if isinstance(temp, str) else degc(temp)
    conditions = [
        field("solvent", solv_label, p2),
        field("temperature", temp_value, p2),
        field("reaction_time", None if time_h is None else {"number": time_h, "unit": "h"}, [] if time_h is None else p2),
    ]
    if entry == 5:
        conditions.append(field("operation", "reaction conducted at 80 °C in a closed vial", EV[3]))
    records.append(
        record(
            f"table1_entry{entry}",
            "optimization_entry",
            evidence,
            ps,
            [
                {"step_id": "reaction", "participant_ids": reaction_ids, "conditions": conditions},
                {"step_id": "yield_analysis", "participant_ids": ["t1_internal_standard"], "conditions": [field("operation", "1H NMR analysis of the crude product using dibromomethane as internal standard", p2)]},
            ],
            [
                field("reported_yield_3aa", pct(y3), p2, ["t1_3aa"]),
                field("reported_yield_4aa", pct(y4), p2, ["t1_4aa"]),
                field("recovered_starting_material_yield", pct(rec1), p2, ["t1_1a"]),
                field("yield_measurement_basis", "1H NMR of crude product using dibromomethane as internal standard", p2, ["t1_3aa", "t1_4aa", "t1_1a"]),
            ],
            notes=[f"Table 1 optimization entry {entry}; explicit zeros are retained as printed values."],
            unresolved=[
                "Reaction time is not reported for this row." if time_h is None else "Operational workup and purification are not reported in the main-text row.",
                "Supporting Information is mentioned by the article but is not associated with this dataset.",
                "Product structures have not been independently structure-verified; product SMILES are omitted.",
            ],
        )
    )


TABLE2 = [
    (1, "1a", "Ph", "H", "Me", "3aa", 88),
    (2, "1b", "p-MeC6H4", "H", "Me", "3ba", 90),
    (3, "1c", "p-BrC6H4", "H", "Me", "3ca", 76),
    (4, "1d", "p-ClC6H4", "H", "Me", "3da", 78),
    (5, "1e", "Ph", "H", "Pr", "3ea", 92),
    (6, "1f", "n-C7H15", "H", "Pr", "3fa", 75),
    (7, "1g", "Ph", "Et", "Me", "3ga", 89),
    (8, "1h", "Ph", "Et", "Pr", "3ha", 89),
    (9, "1i", "Ph", "Ph", "Me", "3ia", 90),
    (10, "1j", "Ph", "Ph", "Pr", "3ja", 92),
    (11, "1k", "Et", "Et", "Ph", "3ka", 70),
    (12, "1l", "Me", "Me", "Me", "3la", 75),
    (13, "1m", "n-C8H17", "H", "H", "3ma", 60),
    (14, "1n", "H", "H", "Bn", "3na", 80),
    (15, "1a", "Ph", "H", "Me", "3aa", 91),
]

for entry, acid_label, r1, r2, r3, product_label, yield_value in TABLE2:
    evidence = list(EV[3])
    if entry in (3, 11):
        evidence += EV[4]
    scale = 6 if entry == 15 else 0.4
    acid_amounts = [mmol(scale, EV[3])]
    if entry == 15:
        acid_amounts.append(field("mass", {"number": 1.0480, "unit": "g"}, EV[3]))
    acid_smiles = "O=C(O)C(C)=C=Cc1ccccc1" if acid_label == "1a" else None
    ps = [
        participant("t2_acid", "reactant", acid_label, f"2,3-allenoic acid {acid_label} (R1={r1}, R2={r2}, R3={r3})", EV[3], acid_smiles, acid_amounts),
        participant("t2_2a", "reactant", "2a", "2-(trimethylsilyl)phenyl triflate", EV[3], "C[Si](C)(C)c1ccccc1OS(=O)(=O)C(F)(F)F", [equiv(1.5, EV[3])]),
        participant("t2_kf", "reagent", "KF", "potassium fluoride", EV[3], "[K+].[F-]", [equiv(2, EV[3])]),
        participant("t2_18c6", "reagent", "18-crown-6", "18-crown-6", EV[3], "O1CCOCCOCCOCCOCCOCC1", [equiv(2, EV[3])]),
        participant("t2_thf", "solvent", "THF", "tetrahydrofuran", EV[3], "C1CCOC1", [volume(4, EV[3])]),
        participant("t2_product", "product", product_label, f"chromone {product_label}", EV[3]),
    ]
    notes = [f"Table 2 substrate-scope entry {entry}; substituents transcribed as R1={r1}, R2={r2}, R3={r3}."]
    if entry in (3, 11):
        notes.append(f"The acknowledgment states that Table 2 entry {entry} was reproduced by Mr. B. Chen; this is not split into another record.")
    if entry == 15:
        notes.append("Footnote c changes the 1a scale to 6 mmol (1.0480 g); the shared table conditions are otherwise retained.")
    records.append(
        record(
            f"table2_entry{entry}",
            "substrate_scope_entry",
            evidence,
            ps,
            [{
                "step_id": "reaction",
                "participant_ids": ["t2_acid", "t2_2a", "t2_kf", "t2_18c6", "t2_thf"],
                "conditions": [
                    field("solvent", "THF", EV[3]),
                    field("temperature", degc(80), EV[3]),
                    field("reaction_time", {"number": 12, "unit": "h"}, EV[3]),
                    field("operation", "heated in a sealed pressure vessel", EV[3]),
                ],
            }],
            [
                field("isolated_yield", pct(yield_value), EV[3], ["t2_product"]),
                field("yield_measurement_basis", "isolated yield", EV[3], ["t2_product"]),
            ],
            notes,
            [
                "Supporting Information is mentioned by the article but is not associated with this dataset; workup and purification are missing.",
                "The allenoic-acid and product structures are transcribed by labels/R groups and have not been independently structure-verified.",
            ] + (["For the 6 mmol scale-up, the table does not state whether the 4 mL THF volume was proportionally changed."] if entry == 15 else []),
        )
    )


TABLE3 = [
    (1, "1a", "2b", "3ab", 80, None, None),
    (2, "1h", "2b", "3hb", 74, "4hb", 9),
    (3, "1a", "2c", "3ac", 85, None, None),
    (4, "1j", "2c", "3jc", 90, None, None),
    (5, "1a", "2d", "3ad", 31, "3ad_prime", 52),
]
ACID_DESC = {
    "1a": "2,3-allenoic acid 1a (R1=Ph, R2=H, R3=Me)",
    "1h": "2,3-allenoic acid 1h (R1=Ph, R2=Et, R3=Pr)",
    "1j": "2,3-allenoic acid 1j (R1=Ph, R2=Ph, R3=Pr)",
}
PRECURSOR_DESC = {
    "2b": "dimethoxy-disubstituted benzyne precursor 2b",
    "2c": "3-methoxy-substituted benzyne precursor 2c",
    "2d": "2-methyl-substituted benzyne precursor 2d",
}

for entry, acid_label, precursor_label, product1, yield1, product2, yield2 in TABLE3:
    evidence = list(EV[3])
    if entry in (4, 5):
        evidence += EV[4]
    ps = [
        participant("t3_acid", "reactant", acid_label, ACID_DESC[acid_label], EV[3], "O=C(O)C(C)=C=Cc1ccccc1" if acid_label == "1a" else None, [mmol(0.4, EV[3])]),
        participant("t3_precursor", "reactant", precursor_label, PRECURSOR_DESC[precursor_label], EV[3], None, [equiv(1.5, EV[3])]),
        participant("t3_kf", "reagent", "KF", "potassium fluoride", EV[3], "[K+].[F-]", [equiv(2, EV[3])]),
        participant("t3_18c6", "reagent", "18-crown-6", "18-crown-6", EV[3], "O1CCOCCOCCOCCOCCOCC1", [equiv(2, EV[3])]),
        participant("t3_thf", "solvent", "THF", "tetrahydrofuran", EV[3], "C1CCOC1", [volume(4, EV[3])]),
        participant("t3_product1", "product", product1.replace("_prime", "′"), f"chromone {product1.replace('_prime', '′')}", EV[3]),
    ]
    if product2:
        secondary_name = "2,3-allenoic acid aryl ester 4hb" if product2 == "4hb" else "chromone 3ad′"
        ps.append(participant("t3_product2", "product", product2.replace("_prime", "′"), secondary_name, EV[3]))
    outs = [
        field(f"isolated_yield_{product1}", pct(yield1), EV[3], ["t3_product1"]),
        field("yield_measurement_basis", "isolated yield", EV[3], ["t3_product1"] + (["t3_product2"] if product2 else [])),
    ]
    if product2:
        outs.append(field(f"isolated_yield_{product2}", pct(yield2), EV[3], ["t3_product2"]))
    if entry == 5:
        outs.append(field("regioisomer_ratio_3ad_to_3ad_prime", "1:1.7", evidence, ["t3_product1", "t3_product2"]))
    notes = [f"Table 3 substituted-benzyne scope entry {entry}."]
    if entry == 2:
        notes.append("Footnote c reports 2,3-allenoic acid aryl ester 4hb isolated in 9% yield; it is structured as a second product.")
    if entry == 4:
        notes.append("The acknowledgment states that Table 3 entry 4 was reproduced by Mr. B. Chen; this is not split into another record.")
    if entry == 5:
        notes.append("The two separable regioisomers are reported in a 1:1.7 ratio; the article states that attack ortho to methyl dominates.")
    records.append(
        record(
            f"table3_entry{entry}",
            "substrate_scope_entry",
            evidence,
            ps,
            [{
                "step_id": "reaction",
                "participant_ids": ["t3_acid", "t3_precursor", "t3_kf", "t3_18c6", "t3_thf"],
                "conditions": [
                    field("solvent", "THF", EV[3]),
                    field("temperature", degc(80), EV[3]),
                    field("reaction_time", {"number": 12, "unit": "h"}, EV[3]),
                    field("operation", "heated in a sealed pressure vessel", EV[3]),
                ],
            }],
            outs,
            notes,
            [
                "Supporting Information is mentioned by the article but is not associated with this dataset; workup and purification are missing.",
                "Benzyne-precursor and product structures are retained by labels/drawings and have not been independently structure-verified; SMILES are omitted.",
            ],
        )
    )


# Page 3 Scheme 3: qualitative regioselectivity rationale, not a batch experiment.
records.append(
    record(
        "scheme3_regioselectivity_rationale",
        "mechanism",
        EV[3],
        [
            participant("s3_methoxy_benzyne", "reactant", "methoxy-substituted benzyne", "generic methoxy-substituted benzyne", EV[3]),
            participant("s3_methyl_benzyne", "reactant", "methyl-substituted benzyne", "generic methyl-substituted benzyne", EV[3]),
            participant("s3_nucleophile", "unspecified_agent", "Nu−", "generic nucleophile", EV[3]),
        ],
        [
            {"step_id": "methoxy_regioselectivity", "participant_ids": ["s3_methoxy_benzyne", "s3_nucleophile"], "conditions": [field("operation", "steric and electronic effects both favor attack meta to methoxy", EV[3])]},
            {"step_id": "methyl_regioselectivity", "participant_ids": ["s3_methyl_benzyne", "s3_nucleophile"], "conditions": [field("operation", "electronic effect favors attack ortho to methyl despite steric preference", EV[3])]},
        ],
        notes=["Scheme 3 rationalizes regioselectivity qualitatively and is not an additional experiment."],
        unresolved=["The scheme uses generic Nu− and substituted-benzyne drawings; no product structures or quantities are specified."],
    )
)


records_path = OUTDIR / "records_pages_0001_0004.json"
records_path.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")

table1_ids = [f"{DOC}:table1_entry{i}" for i in range(1, 16)]
table2_ids = [f"{DOC}:table2_entry{i}" for i in range(1, 16)]
table3_ids = [f"{DOC}:table3_entry{i}" for i in range(1, 6)]
coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1,
            "state": "attempted",
            "regions": [
                {
                    "region": "title, graphical abstract, and abstract",
                    "finding": "The generic 2,3-allenoic-acid/benzyne-to-chromone transformation (KF, 18-crown-6, THF, 80 °C, 12 h; up to 92% yield) is classified as a general scheme, not an individual batch.",
                    "evidence_ids": EV[1],
                },
                {
                    "region": "two-column introduction and references",
                    "finding": "Biological context and prior allenoate/benzyne literature are citations and motivation; no new individual experiments are reported in this region.",
                    "evidence_ids": EV[1],
                },
            ],
            "record_ids": [f"{DOC}:graphical_abstract_general_transformation"],
            "unresolved": ["Generic R-group structures and reagent quantities in the graphical abstract are not fully specified."],
        },
        {
            "page": 2,
            "state": "attempted",
            "regions": [
                {
                    "region": "upper-left Scheme 1",
                    "finding": "Expected intramolecular Michael addition/protonolysis to a coumarin is a proposed pathway, not an observed experiment.",
                    "evidence_ids": EV[2],
                },
                {
                    "region": "middle-left Table 1 and footnotes",
                    "finding": "All 15 optimization rows were transcribed independently, including row-specific solvent, fluoride/additive loading, temperature, time overrides, 2a loading override, 3aa/4aa yields, recovered 1a, and the crude-1H-NMR/internal-standard basis.",
                    "evidence_ids": EV[2],
                },
                {
                    "region": "upper-right Figure 1 and adjacent prose",
                    "finding": "ORTEP and prose identify 3aa as a chromone; this is characterization/context for Table 1 entry 1 rather than a separate reaction record.",
                    "evidence_ids": EV[2],
                },
                {
                    "region": "lower-right Scheme 2",
                    "finding": "A1→B1→C1→D1→3aa is classified as the authors' proposed mechanism and not as successive batch experiments.",
                    "evidence_ids": EV[2],
                },
            ],
            "record_ids": [f"{DOC}:scheme1_expected_coumarin_path", f"{DOC}:scheme2_proposed_chromone_mechanism"] + table1_ids,
            "unresolved": ["Most Table 1 rows omit reaction duration and all rows omit main-text workup/purification details."],
        },
        {
            "page": 3,
            "state": "attempted",
            "regions": [
                {
                    "region": "upper-left continuation of Table 1 discussion",
                    "finding": "Narrative interprets entries 2–15 and identifies entry 5 as the standard condition; no duplicate experiments were created.",
                    "evidence_ids": EV[3],
                },
                {
                    "region": "middle/lower-left Table 2 and footnotes",
                    "finding": "All 15 allenoic-acid scope rows were transcribed separately, including the 6 mmol (1.0480 g) scale-up and isolated-yield basis.",
                    "evidence_ids": EV[3],
                },
                {
                    "region": "upper-right Table 3 and footnotes",
                    "finding": "All five substituted-benzyne rows were transcribed separately; entry 2 includes 4hb at 9%, and entry 5 includes both regioisomer-specific yields and the 1:1.7 ratio.",
                    "evidence_ids": EV[3],
                },
                {
                    "region": "lower-right Scheme 3",
                    "finding": "Methoxy/methyl benzyne attack preferences are a qualitative regioselectivity rationale, not an additional experiment.",
                    "evidence_ids": EV[3],
                },
            ],
            "record_ids": table1_ids[1:] + table2_ids + table3_ids + [f"{DOC}:scheme3_regioselectivity_rationale"],
            "unresolved": ["Table-derived product structures are not independently verified; operational workup and purification require the unassociated SI."],
        },
        {
            "page": 4,
            "state": "attempted",
            "regions": [
                {
                    "region": "upper-left continuation of Table 3 entry 5 discussion",
                    "finding": "The 1:1.7 separable-regioisomer result and electronically favored ortho attack to methyl are merged into the existing Table 3 entry 5 record.",
                    "evidence_ids": EV[4],
                },
                {
                    "region": "upper-right acknowledgment",
                    "finding": "Reproduction of Table 2 entries 3 and 11 and Table 3 entry 4 is recorded as provenance/context, not split into new rows because no new conditions or outcomes are supplied.",
                    "evidence_ids": EV[4],
                },
                {
                    "region": "right-column Supporting Information statement",
                    "finding": "The article states that general procedure and spectroscopic data are available as SI, but no SI file is explicitly associated in this workspace; no SI facts were imported.",
                    "evidence_ids": EV[4],
                },
                {
                    "region": "summary paragraph",
                    "finding": "General conclusion only; no new individual reaction record.",
                    "evidence_ids": EV[4],
                },
            ],
            "record_ids": [f"{DOC}:table2_entry3", f"{DOC}:table2_entry11", f"{DOC}:table3_entry4", f"{DOC}:table3_entry5"],
            "unresolved": ["Supporting Information association remains unestablished, so general procedure and spectra are outside the extracted evidence."],
        },
    ],
}

coverage_path = OUTDIR.parent / "coverage" / "pages_0001_0004.json"
coverage_path.parent.mkdir(parents=True, exist_ok=True)
coverage_path.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"records": len(records), "records_path": str(records_path), "coverage_path": str(coverage_path)}, ensure_ascii=False))
