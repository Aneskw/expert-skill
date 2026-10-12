#!/usr/bin/env python3
"""Build evidence-linked machine records for DOI 10.1021/ol0473389, PDF pages 1-3."""

import json
from pathlib import Path


DOC = "doc_74198b5720a3ca3a"
HERE = Path(__file__).resolve().parent
OUT = HERE / "records_pages_0001_0003.json"
COVERAGE = HERE.parent / "coverage" / "pages_0001_0003.json"

P1T = f"{DOC}:page1:text"
P1I = f"{DOC}:page1:image"
P2T = f"{DOC}:page2:text"
P2I = f"{DOC}:page2:image"
P3T = f"{DOC}:page3:text"
P3I = f"{DOC}:page3:image"


def fact(value, evidence):
    return {
        "value": value,
        "evidence_ids": list(evidence),
        "verification": "missing" if value is None else "unreviewed",
    }


def field(name, value, evidence, targets=None):
    item = {"name": name, "fact": fact(value, evidence)}
    if targets:
        item["target_entity_ids"] = list(targets)
    return item


def participant(entity_id, role, label, name, smiles, evidence, amounts=None):
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


def record(source_id, kind, evidence, participants, steps, outcomes, notes, unresolved):
    return {
        "record_id": f"{DOC}:{source_id}",
        "document_id": DOC,
        "source_reaction_id": source_id,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": list(evidence),
        "participants": participants,
        "steps": steps,
        "outcomes": outcomes,
        "notes": [fact(x, evidence) for x in notes],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": list(unresolved),
        },
    }


records = []

# Page 1: the graphical abstract is a generic transformation, not an individual experiment.
p1ev = [P1T, P1I]
generic_parts = [
    participant("allene_1", "reactant", "generic 3,4-alkadienoate", None, None, p1ev),
    participant("rx_2", "reactant", "RX", "organic halide", None, p1ev),
    participant("product_3", "product", "generic 2(E),4-alkadienoate", None, None, p1ev),
    participant("pdpph3_4", "catalyst", "Pd(PPh3)4", "tetrakis(triphenylphosphine)palladium(0)",
                "[Pd](P(c1ccccc1)(c1ccccc1)c1ccccc1)(P(c1ccccc1)(c1ccccc1)c1ccccc1)(P(c1ccccc1)(c1ccccc1)c1ccccc1)P(c1ccccc1)(c1ccccc1)c1ccccc1",
                p1ev, [field("catalyst_loading", {"number": 5, "unit": "mol%"}, p1ev)]),
    participant("ag2co3", "catalyst", "Ag2CO3", "silver carbonate", "[Ag+].[Ag+].[O-]C([O-])=O",
                p1ev, [field("catalyst_loading", {"number": 5, "unit": "mol%"}, p1ev)]),
    participant("k2co3", "reagent", "K2CO3", "potassium carbonate", "[K+].[K+].[O-]C([O-])=O",
                p1ev, [field("equivalents", {"number": 4, "unit": "equiv"}, p1ev)]),
    participant("mecn", "solvent", "CH3CN", "acetonitrile", "CC#N", p1ev),
]
records.append(record(
    "graphical_abstract_general_transformation", "general_scheme", p1ev, generic_parts,
    [{"step_id": "generic_coupling", "participant_ids": [p["entity_id"] for p in generic_parts],
      "conditions": [field("solvent", "CH3CN", p1ev),
                     field("temperature", {"number": 75, "unit": "°C"}, p1ev),
                     field("atmosphere", "N2", p1ev), field("time", None, p1ev)]}],
    [field("stereochemical_outcome", "2(E),4-alkadienoate", p1ev, ["product_3"])],
    ["The graphical abstract depicts a generic reaction class rather than a specific substrate experiment."],
    ["Generic R/RX substituents are not fully specified; structures and reaction time are unavailable.",
     "Supporting Information is mentioned in the paper but was not supplied or associated."],
))

# Page 1 Scheme 1: proposed mechanistic/regiochemical network, not a reported experiment.
mechanism_parts = [
    participant("generic_allene", "reactant", "generic substituted allene", None, None, p1ev),
    participant("ari", "reactant", "ArI", "aryl iodide", None, p1ev),
    participant("pd0", "catalyst", "Pd(0)", "palladium(0)", "[Pd]", p1ev),
    participant("pi_allyl_pd", "unspecified_agent", "pi-allylpalladium intermediate", None, None, p1ev),
    participant("desired_diene", "product", "regioselected conjugated diene", None, None, p1ev),
    participant("alternative_diene_1", "product", "alternative beta-H-elimination diene 1", None, None, p1ev),
    participant("alternative_diene_2", "product", "alternative beta-H-elimination diene 2", None, None, p1ev),
    participant("alternative_diene_3", "product", "alternative beta-H-elimination diene 3", None, None, p1ev),
]
records.append(record(
    "scheme1_proposed_mechanism", "mechanism", p1ev, mechanism_parts,
    [
        {"step_id": "oxidative_addition_carbopalladation", "participant_ids": ["generic_allene", "ari", "pd0", "pi_allyl_pd"],
         "conditions": [field("operation", "oxidative addition followed by carbopalladation", p1ev)]},
        {"step_id": "beta_h_elimination_desired", "participant_ids": ["pi_allyl_pd", "desired_diene"],
         "conditions": [field("operation", "beta-H elimination", p1ev)]},
        {"step_id": "beta_h_elimination_alternative_1", "participant_ids": ["pi_allyl_pd", "alternative_diene_1"],
         "conditions": [field("operation", "alternative beta-H elimination", p1ev)]},
        {"step_id": "beta_h_elimination_alternative_2", "participant_ids": ["pi_allyl_pd", "alternative_diene_2"],
         "conditions": [field("operation", "alternative beta-H elimination", p1ev)]},
        {"step_id": "beta_h_elimination_alternative_3", "participant_ids": ["pi_allyl_pd", "alternative_diene_3"],
         "conditions": [field("operation", "alternative beta-H elimination", p1ev)]},
    ], [],
    ["Scheme 1 presents regio- and stereochemical possibilities; the prose describes the pathway as proposed/believed."],
    ["Generic R groups and mechanistic structures cannot be encoded as complete molecules.",
     "No experiment-specific quantities or outcome are assigned to this mechanistic scheme."],
))


def common_table_participants(evidence, solvent_label, phi_equiv, k2co3_equiv, include_ag=True, scale=None):
    substrate_amounts = [field("reaction_scale", scale, evidence)]
    parts = [
        participant("substrate_1a", "reactant", "1a", "ethyl 3-butyl-3,4-pentadienoate",
                    "C=C=C(CCCC)CC(=O)OCC", evidence, substrate_amounts),
        participant("phi_2a", "reactant", "2a", "iodobenzene", "Ic1ccccc1", evidence,
                    [field("equivalents", {"number": phi_equiv, "unit": "equiv"}, evidence)]),
        participant("product_3a", "product", "3a", "ethyl 4-phenyl-3-butyl-2(E),4-pentadienoate",
                    "CCOC(=O)C=C(CCCC)C(=C)c1ccccc1", evidence),
        participant("pdpph3_4", "catalyst", "Pd(PPh3)4", "tetrakis(triphenylphosphine)palladium(0)", None,
                    evidence, [field("catalyst_loading", {"number": 5, "unit": "mol%"}, evidence)]),
        participant("k2co3", "reagent", "K2CO3", "potassium carbonate", "[K+].[K+].[O-]C([O-])=O",
                    evidence, [field("equivalents", {"number": k2co3_equiv, "unit": "equiv"}, evidence)]),
        participant("solvent", "solvent", solvent_label, solvent_label, None, evidence),
    ]
    if include_ag:
        parts.insert(4, participant("ag2co3", "catalyst", "Ag2CO3", "silver carbonate", "[Ag+].[Ag+].[O-]C([O-])=O",
                                    evidence, [field("catalyst_loading", {"number": 5, "unit": "mol%"}, evidence)]))
    return parts


table1 = [
    (1, "toluene", 75, 13, 1.5, 10, True, 4),
    (2, "THF", 75, 14, 1.5, 45, True, 4),
    (3, "dioxane", 75, 14, 1.5, 65, True, 4),
    (4, "DMF", 75, 14, 1.5, 76, True, 4),
    (5, "CH3CN", 75, 13, 1.5, 80, True, 4),
    (6, "CH3CN", 75, 13, 1.5, 63, False, 4),
    (7, "CH3CN", 60, 13, 1.5, 16, True, 4),
    (8, "CH3CN", 75, 13, 1.2, 63, True, 4),
    (9, "CH3CN", 75, 13, 1.5, 71, True, 2),
]

for entry, solvent, temp, hours, phi_eq, yield_pct, include_ag, base_eq in table1:
    evidence = [P2T, P2I]
    scale = None
    if entry == 5:
        # Table 2 entry 1 repeats this exact experiment and supplies the stated scope scale.
        evidence = [P2T, P2I, P3T, P3I]
        scale = {"minimum": 0.3, "maximum": 0.5, "unit": "mmol", "raw_text": "0.3-0.5 mmol"}
    parts = common_table_participants(evidence, solvent, phi_eq, base_eq, include_ag, scale)
    notes = [f"Table 1 entry {entry}."]
    if not include_ag:
        notes.append("Footnote b: reaction conducted in the absence of Ag2CO3.")
    if entry == 9:
        notes.append("Footnote c: reaction conducted with the reduced K2CO3 loading structured in the K2CO3 participant amounts.")
    if entry == 5:
        notes.append("The same 1a/2a/3a experiment is repeated as Table 2 entry 1; evidence is merged rather than duplicated.")
    outcomes = [
        field("isolated_yield", {"number": yield_pct, "unit": "%"}, evidence, ["product_3a"]),
        field("yield_measurement_basis", "isolated yield", evidence, ["product_3a"]),
    ]
    if entry == 5:
        outcomes.extend([
            field("stereoselectivity", "only the 2(E)-stereoisomer was formed", evidence, ["product_3a"]),
            field("2Z_isomer_selectivity", {"number": 4, "unit": "%", "qualifier": "lt", "raw_text": "<4%, if any"},
                  [P2T, P3T, P3I], ["product_3a"]),
        ])
    records.append(record(
        f"table1_entry_{entry:02d}", "optimization_entry", evidence, parts,
        [{"step_id": "coupling", "participant_ids": [p["entity_id"] for p in parts],
          "conditions": [field("solvent", solvent, evidence),
                         field("temperature", {"number": temp, "unit": "°C"}, evidence),
                         field("time", {"number": hours, "unit": "h"}, evidence),
                         field("atmosphere", "N2", evidence)]}],
        outcomes, notes,
        ["Supporting Information is mentioned but was not supplied or associated; detailed procedure, workup and purification are unavailable.",
         "Candidate SMILES are machine interpretations and remain unverified."],
    ))


halides = {
    "2a": ("PhI", "iodobenzene", "Ic1ccccc1"),
    "2b": ("p-MeOC6H4I", "4-iodoanisole", "COc1ccc(I)cc1"),
    "2c": ("p-CH3C6H4I", "4-iodotoluene", "Cc1ccc(I)cc1"),
    "2d": ("p-Me2NCOC6H4I", "4-iodo-N,N-dimethylbenzamide", "CN(C)C(=O)c1ccc(I)cc1"),
    "2e": ("p-CH3COC6H4I", "4-iodoacetophenone", "CC(=O)c1ccc(I)cc1"),
    "2f": ("p-NCC6H4I", "4-iodobenzonitrile", "N#Cc1ccc(I)cc1"),
    "2g": ("p-MeO2CC6H4I", "methyl 4-iodobenzoate", "COC(=O)c1ccc(I)cc1"),
    "2h": ("2-thienyl bromide", "2-bromothiophene", "Brc1cccs1"),
}

table2 = [
    (2, "CH3", "H", "1b", "2a", 1.5, 1.0, 23, 82, "3b"),
    (3, "C2H5", "H", "1c", "2a", 1.5, 1.0, 19, 77, "3c"),
    (4, "(CH2)4", "H", "1d", "2a", 1.5, 1.0, 11, 85, "3d"),
    (5, "(CH2)5", "H", "1e", "2a", 1.5, 1.0, 19, 77, "3e"),
    (6, "H", "Ph", "1f", "2a", 1.5, 1.0, 18, 44, "3f"),
    (7, "H", "n-C4H9", "1a", "2b", 1.2, 1.0, 11, 65, "3g"),
    (8, "H", "n-C4H9", "1a", "2c", 1.5, 1.0, 11, 65, "3h"),
    (9, "H", "n-C4H9", "1a", "2d", 1.0, 1.5, 11, 62, "3i"),
    (10, "H", "n-C4H9", "1a", "2e", 1.0, 1.2, 46, 75, "3j"),
    (11, "H", "n-C4H9", "1a", "2f", 1.0, 2.0, 60, 82, "3k"),
    (12, "H", "n-C4H9", "1a", "2g", 1.0, 2.0, 24, 85, "3l"),
    (13, "H", "n-C4H9", "1a", "2h", 1.5, 1.0, 21, 66, "3m"),
]

for entry, r1, r2, substrate_label, halide_label, halide_eq, substrate_eq, hours, yield_pct, product_label in table2:
    evidence = [P2T, P3T, P3I]
    h_display, h_name, h_smiles = halides[halide_label]
    is_1a = substrate_label == "1a"
    substrate_name = "ethyl 3-butyl-3,4-pentadienoate" if is_1a else f"3,4-alkadienoate {substrate_label} (R1={r1}, R2={r2})"
    substrate_smiles = "C=C=C(CCCC)CC(=O)OCC" if is_1a else None
    parts = [
        participant("substrate_1", "reactant", substrate_label, substrate_name, substrate_smiles, evidence,
                    [field("reaction_scale", {"minimum": 0.3, "maximum": 0.5, "unit": "mmol", "raw_text": "0.3-0.5 mmol"}, evidence),
                     field("equivalents", {"number": substrate_eq, "unit": "equiv"}, evidence)]),
        participant("halide_2", "reactant", halide_label, h_name, h_smiles, evidence,
                    [field("equivalents", {"number": halide_eq, "unit": "equiv"}, evidence)]),
        participant("product_3", "product", product_label, f"2(E),4-alkadienoate {product_label}", None, evidence),
        participant("pdpph3_4", "catalyst", "Pd(PPh3)4", "tetrakis(triphenylphosphine)palladium(0)", None,
                    evidence, [field("catalyst_loading", {"number": 5, "unit": "mol%"}, evidence)]),
        participant("ag2co3", "catalyst", "Ag2CO3", "silver carbonate", "[Ag+].[Ag+].[O-]C([O-])=O",
                    evidence, [field("catalyst_loading", {"number": 5, "unit": "mol%"}, evidence)]),
        participant("k2co3", "reagent", "K2CO3", "potassium carbonate", "[K+].[K+].[O-]C([O-])=O",
                    evidence, [field("equivalents", {"number": 4, "unit": "equiv"}, evidence)]),
        participant("mecn", "solvent", "CH3CN", "acetonitrile", "CC#N", evidence),
    ]
    records.append(record(
        f"table2_entry_{entry:02d}", "substrate_scope_entry", evidence, parts,
        [{"step_id": "coupling", "participant_ids": [p["entity_id"] for p in parts],
          "conditions": [field("solvent", "CH3CN", evidence),
                         field("temperature", {"number": 75, "unit": "°C"}, evidence),
                         field("time", {"number": hours, "unit": "h"}, evidence),
                         field("atmosphere", "N2", evidence)]}],
        [field("isolated_yield", {"number": yield_pct, "unit": "%"}, evidence, ["product_3"]),
         field("yield_measurement_basis", "isolated yield", evidence, ["product_3"]),
         field("2Z_isomer_selectivity", {"number": 4, "unit": "%", "qualifier": "lt", "raw_text": "<4%, if any"},
               [P2T, P3T, P3I], ["product_3"])],
        [f"Table 2 entry {entry}; printed RX is {h_display}; printed 2/1 ratio is {halide_eq:g}/{substrate_eq:g}."],
        ["Detailed procedure, workup and purification are unavailable because SI was not supplied or associated.",
         "Substrate/product structures reconstructed from generic R-group drawings are left without SMILES unless independently explicit.",
         "All candidate structures remain unverified."],
    ))


# Page 2 equation 1: stereochemical derivatization of 3a to allylic alcohol 4a.
p2ev = [P2T, P2I]
eq1_parts = [
    participant("compound_3a", "reactant", "3a", "ethyl 4-phenyl-3-butyl-2(E),4-pentadienoate",
                "CCOC(=O)C=C(CCCC)C(=C)c1ccccc1", p2ev,
                [field("reaction_scale", None, p2ev)]),
    participant("dibal_h", "reagent", "DIBAL-H", "diisobutylaluminium hydride", "CC(C)C[AlH]CC(C)C", p2ev,
                [field("amount", None, p2ev)]),
    participant("toluene", "solvent", "toluene", "toluene", "Cc1ccccc1", p2ev),
    participant("compound_4a", "product", "4a", "allylic alcohol 4a", "OCC=C(CCCC)C(=C)c1ccccc1", p2ev),
]
records.append(record(
    "equation1_3a_to_4a", "reported_experiment", p2ev, eq1_parts,
    [{"step_id": "dibal_reduction", "participant_ids": [p["entity_id"] for p in eq1_parts],
      "conditions": [field("solvent", "toluene", p2ev),
                     field("temperature", {"number": -78, "unit": "°C"}, p2ev),
                     field("time", None, p2ev)]}],
    [field("yield", {"number": 78, "unit": "%"}, p2ev, ["compound_4a"]),
     field("yield_measurement_basis", None, p2ev, ["compound_4a"])],
    ["The NOE of 4a, together with 3a, was used to establish the stereochemistry of 3a."],
    ["Reaction time, scale, DIBAL-H amount, yield basis, workup and purification are not reported in the main-text equation.",
     "SI was not supplied or associated; candidate structures and stereochemistry remain unverified."],
))


# Page 3 Scheme 2, first arrow: 1g + PhI -> 3n.
p3ev = [P3T, P3I]
s2_parts = [
    participant("substrate_1g", "reactant", "1g", "ethyl 2-methyl-3,4-pentadienoate", "C=C=CC(C)C(=O)OCC", p3ev,
                [field("reaction_scale", None, p3ev)]),
    participant("phi_2a", "reactant", "2a", "iodobenzene", "Ic1ccccc1", p3ev,
                [field("equivalents", {"number": 1.5, "unit": "equiv"}, p3ev)]),
    participant("product_3n", "product", "3n", "ethyl 2(E),4-pentadienoate 3n", "CCOC(=O)C(C)=CC(=C)c1ccccc1", p3ev),
    participant("pdpph3_4", "catalyst", "Pd(PPh3)4", "tetrakis(triphenylphosphine)palladium(0)", None, p3ev,
                [field("catalyst_loading", {"number": 5, "unit": "mol%"}, p3ev)]),
    participant("ag2co3", "catalyst", "Ag2CO3", "silver carbonate", "[Ag+].[Ag+].[O-]C([O-])=O", p3ev,
                [field("catalyst_loading", {"number": 5, "unit": "mol%"}, p3ev)]),
    participant("k2co3", "reagent", "K2CO3", "potassium carbonate", "[K+].[K+].[O-]C([O-])=O", p3ev,
                [field("equivalents", {"number": 4, "unit": "equiv"}, p3ev)]),
    participant("mecn", "solvent", "MeCN", "acetonitrile", "CC#N", p3ev),
]
records.append(record(
    "scheme2_1g_to_3n", "reported_experiment", p3ev, s2_parts,
    [{"step_id": "coupling", "participant_ids": [p["entity_id"] for p in s2_parts],
      "conditions": [field("solvent", "MeCN", p3ev),
                     field("temperature", {"number": 75, "unit": "°C"}, p3ev),
                     field("atmosphere", "N2", p3ev), field("time", None, p3ev)]}],
    [field("yield", {"number": 58, "unit": "%"}, p3ev, ["product_3n"]),
     field("yield_measurement_basis", None, p3ev, ["product_3n"]),
     field("stereoselectivity", "highly stereoselective 2(E) product; assignment established by NOE study of 3n and 4n", p3ev, ["product_3n"])],
    ["Scheme 2 first arrow."],
    ["Reaction time, reaction scale, yield basis, workup and purification are absent from the main-text scheme.",
     "SI was not supplied or associated; candidate structures and stereochemistry remain unverified."],
))


# Page 3 Scheme 2, second arrow: 3n -> 4n.
s2r_parts = [
    participant("compound_3n", "reactant", "3n", "ethyl 2(E),4-pentadienoate 3n", "CCOC(=O)C(C)=CC(=C)c1ccccc1", p3ev,
                [field("reaction_scale", None, p3ev)]),
    participant("dibal_h", "reagent", "DIBAL-H", "diisobutylaluminium hydride", "CC(C)C[AlH]CC(C)C", p3ev,
                [field("amount", None, p3ev)]),
    participant("toluene", "solvent", "toluene", "toluene", "Cc1ccccc1", p3ev),
    participant("compound_4n", "product", "4n", "allylic alcohol 4n", "OCC(C)=CC(=C)c1ccccc1", p3ev),
]
records.append(record(
    "scheme2_3n_to_4n", "reported_experiment", p3ev, s2r_parts,
    [{"step_id": "dibal_reduction", "participant_ids": [p["entity_id"] for p in s2r_parts],
      "conditions": [field("solvent", "toluene", p3ev),
                     field("temperature", {"number": -78, "unit": "°C"}, p3ev),
                     field("time", None, p3ev)]}],
    [field("yield", {"number": 84, "unit": "%"}, p3ev, ["compound_4n"]),
     field("yield_measurement_basis", None, p3ev, ["compound_4n"])],
    ["The NOE of 4n, together with 3n, was used to establish the stereochemistry of 3n."],
    ["Reaction time, scale, DIBAL-H amount, yield basis, workup and purification are absent from the main-text scheme.",
     "SI was not supplied or associated; candidate structures and stereochemistry remain unverified."],
))


page1_ids = [f"{DOC}:graphical_abstract_general_transformation", f"{DOC}:scheme1_proposed_mechanism"]
page2_ids = [f"{DOC}:table1_entry_{i:02d}" for i in range(1, 10)] + [f"{DOC}:equation1_3a_to_4a"]
page3_ids = [f"{DOC}:table1_entry_05"] + [f"{DOC}:table2_entry_{i:02d}" for i in range(2, 14)] + [
    f"{DOC}:scheme2_1g_to_3n", f"{DOC}:scheme2_3n_to_4n"
]

coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1,
            "state": "attempted",
            "regions": [
                {"region": "graphical abstract reaction arrow", "finding": "Generic Pd(0)/Ag2CO3-catalyzed transformation; classified as general_scheme, not an individual experiment.", "evidence_ids": [P1I, P1T]},
                {"region": "Scheme 1", "finding": "Proposed oxidative-addition/carbopalladation/beta-H-elimination network with alternative regioisomeric pathways; classified as mechanism.", "evidence_ids": [P1I, P1T]},
                {"region": "introductory prose", "finding": "Background and cited prior work; no additional current-paper experiment with complete conditions.", "evidence_ids": [P1I, P1T]},
            ],
            "record_ids": page1_ids,
            "unresolved": ["Generic R groups in the abstract and Scheme 1 do not define complete structures.", "No SI was provided or associated."],
        },
        {
            "page": 2,
            "state": "attempted",
            "regions": [
                {"region": "Table 1 and its reaction header/footnotes", "finding": "Nine distinct optimization experiments extracted row-by-row; footnote b removes Ag2CO3 in entry 6 and footnote c changes K2CO3 to 2 equiv in entry 9.", "evidence_ids": [P2I, P2T]},
                {"region": "equation 1", "finding": "DIBAL-H reduction of 3a to 4a at -78 °C in toluene, 78%; extracted as a reported experiment used for NOE assignment.", "evidence_ids": [P2I, P2T]},
                {"region": "scope discussion and references", "finding": "Current-paper narrative continues into Table 2; bibliography entries are prior work and were not extracted as current experiments.", "evidence_ids": [P2I, P2T]},
            ],
            "record_ids": page2_ids,
            "unresolved": ["Table 1 lacks reaction scale, detailed procedure, workup and purification except that entry 5 is repeated in Table 2 with a 0.3-0.5 mmol scale.", "Equation 1 lacks time, scale, DIBAL-H amount and yield basis."],
        },
        {
            "page": 3,
            "state": "attempted",
            "regions": [
                {"region": "Table 2 reaction header, rows 1-13 and footnotes", "finding": "Thirteen substrate-scope rows inspected. Entry 1 duplicates Table 1 entry 5 and was evidence-merged; entries 2-13 are separate substrate_scope_entry records. Footnotes supply 0.3-0.5 mmol scale and isolated-yield basis.", "evidence_ids": [P3I, P3T]},
                {"region": "prose immediately below Table 2", "finding": "Crude-product 2(Z)-isomer is reported as <4%, if any; linked as product-specific selectivity to the Table 2 records.", "evidence_ids": [P3I, P3T, P2T]},
                {"region": "Scheme 2 first arrow", "finding": "1g plus 1.5 equiv PhI under Pd(PPh3)4/Ag2CO3/K2CO3 in MeCN at 75 °C under N2 gives 3n in 58%; separate reported experiment.", "evidence_ids": [P3I, P3T]},
                {"region": "Scheme 2 second arrow", "finding": "DIBAL-H reduction of 3n to 4n in toluene at -78 °C gives 84%; separate reported experiment used for NOE assignment.", "evidence_ids": [P3I, P3T]},
                {"region": "Supporting Information statement", "finding": "Main text states SI exists, but no SI file was explicitly supplied; association remains unestablished.", "evidence_ids": [P3I, P3T]},
            ],
            "record_ids": page3_ids,
            "unresolved": ["Table 2 lacks detailed workup and purification in the supplied main text.", "Scheme 2 lacks reaction times, reaction scales, DIBAL-H amount and yield bases.", "Candidate structures derived from drawings remain unverified."],
        },
    ],
}

OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
COVERAGE.parent.mkdir(parents=True, exist_ok=True)
COVERAGE.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"records": len(records), "raw_output": str(OUT), "coverage": str(COVERAGE)}, ensure_ascii=False))
