#!/usr/bin/env python3
"""Build machine extraction records and coverage for PDF pages 1-4."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "runs/current/raw_model/extracted_records_pages_0001_0004.json"
COVERAGE = ROOT / "runs/current/coverage/pages_0001_0004.json"
DOC = "doc_1f6b8c33c844c427"


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


def record(suffix, source_id, kind, evidence, participants, steps, outcomes, notes, unresolved):
    return {
        "record_id": f"{DOC}:{suffix}",
        "document_id": DOC,
        "source_reaction_id": source_id,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": list(evidence),
        "participants": participants,
        "steps": steps,
        "outcomes": outcomes,
        "notes": [fact(value, ev) for value, ev in notes],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved,
        },
    }


p2t = [f"{DOC}:page2:text"]
p2i = [f"{DOC}:page2:image"]
p2 = p2t + p2i
p3t = [f"{DOC}:page3:text"]
p3i = [f"{DOC}:page3:image"]
p3 = p3t + p3i
p23 = p2 + p3

records = []

# Scheme 1 is explicitly generic and has no experimental amounts or product data.
records.append(record(
    "scheme1_general_addition", "Scheme 1", "general_scheme", p2,
    [
        participant("scheme1_allene", "reactant", "allene (R1/R2)", "generic substituted allene", None, p2i),
        participant("scheme1_boronic_acid", "reactant", "R3B(OH)2", "generic organoboronic acid", None, p2i),
        participant("scheme1_pd0", "catalyst", "Pd0", "palladium(0)", None, p2i),
        participant("scheme1_acid", "reagent", "acid", "acid (unspecified)", None, p2i),
        participant("scheme1_alkene", "product", "addition product", "generic tri- or tetrasubstituted alkene", None, p2i),
    ],
    [{"step_id": "generic_addition", "participant_ids": ["scheme1_allene", "scheme1_boronic_acid", "scheme1_pd0", "scheme1_acid", "scheme1_alkene"], "conditions": []}],
    [],
    [("Scheme 1 is a generic reaction class, not an individually quantified experiment.", p2)],
    ["R-group structures, quantities, time, temperature, yield, selectivity, workup, and purification are not specified in Scheme 1."],
))


def scheme2_participants(aryl_label, acid_name, acid_smiles, product3, product4, p3_smiles, p4_smiles):
    return [
        participant("allenoate_1", "reactant", "1", "ethyl 2-benzylbuta-2,3-dienoate", "C=C=C(Cc1ccccc1)C(=O)OCC", p2,
                    [field("amount", {"number": 0.05, "unit": "mmol"}, p2t)]),
        participant("boronic_acid_2", "reactant", aryl_label, acid_name, acid_smiles, p2,
                    [field("amount", {"number": 0.1, "unit": "mmol"}, p2t)]),
        participant("pd_pph3_4", "catalyst", "[Pd(PPh3)4]", "tetrakis(triphenylphosphine)palladium(0)", None, p2,
                    [field("amount", {"number": 0.005, "unit": "mmol"}, p2t),
                     field("catalyst_loading", {"number": 10, "unit": "mol%"}, p2i)]),
        participant("acoh", "reagent", "AcOH", "acetic acid", "CC(=O)O", p2,
                    [field("amount", {"number": 0.05, "unit": "mmol"}, p2t),
                     field("reagent_loading", {"number": 100, "unit": "mol%"}, p2i)]),
        participant("thf", "solvent", "THF", "tetrahydrofuran", "C1CCOC1", p2,
                    [field("volume", {"number": 6, "unit": "mL"}, p2t)]),
        participant("methanol", "solvent", "methanol", "methanol", "CO", p2t,
                    [field("sample_dilution_volume", {"number": 80, "unit": "uL"}, p2t)]),
        participant("product_3", "product", product3, "internal-alkene hydroarylation product", p3_smiles, p2i),
        participant("product_4", "product", product4, "terminal-alkene regioisomer", p4_smiles, p2i),
    ]


common_conditions = [
    field("temperature", "r.t.", p2),
    field("atmosphere", "N2", p2),
    field("solvent", "THF", p2),
]

participants_2a = scheme2_participants(
    "2a", "phenylboronic acid", "OB(O)c1ccccc1", "3a", "4a",
    "CCOC(=O)C(Cc1ccccc1)=C(C)c1ccccc1",
    "C=C(c1ccccc1)C(Cc1ccccc1)C(=O)OCC",
)
participants_2a += [
    participant("ion_5", "product", "5", "cationic acetoxypalladium bis(triphenylphosphine) species", None, p23),
    participant("byproduct_6", "product", "6", "hydrogen-bonded allenoate/acetic-acid by-product ion", None, p2),
    participant("ion_7", "product", "7", "cationic alkenylpalladium intermediate", None, p23),
    participant("ion_8", "product", "8", "oxidized palladium-hydride/vinyl ion", None, p23),
    participant("ion_9", "product", "9", "cationic pi-allylpalladium ion", None, p3),
]

records.append(record(
    "scheme2_monitoring_2a", "Scheme 2 / Figure 1, organoboronic acid 2a", "reported_experiment", p23,
    participants_2a,
    [
        {"step_id": "reaction_mixture", "participant_ids": ["allenoate_1", "boronic_acid_2", "pd_pph3_4", "acoh", "thf", "product_3", "product_4", "ion_5", "byproduct_6", "ion_7", "ion_8", "ion_9"], "conditions": common_conditions},
        {"step_id": "sample_after_3_min", "participant_ids": ["methanol", "ion_5", "byproduct_6", "ion_7", "ion_8"], "conditions": [
            field("time", {"number": 3, "unit": "min"}, p2),
            field("sample_aliquot_volume", {"number": 20, "unit": "uL"}, p2t),
            field("operation", "Dilute the aliquot with 80 uL methanol and transfer to the positive-ion ESI source.", p2t),
            field("esi_source_flow_rate", "10 uL min-1", p2t),
        ]},
        {"step_id": "sample_after_2_h", "participant_ids": ["methanol", "ion_5", "byproduct_6", "ion_8", "ion_9"], "conditions": [
            field("time", {"number": 2, "unit": "h"}, p2i),
            field("sample_aliquot_volume", {"number": 20, "unit": "uL"}, p2t),
            field("operation", "Dilute the aliquot with 80 uL methanol and transfer to the positive-ion ESI source.", p2t),
            field("esi_source_flow_rate", "10 uL min-1", p2t),
        ]},
    ],
    [
        field("product_3a_yield", None, [], ["product_3"]),
        field("product_4a_yield", None, [], ["product_4"]),
        field("ion_5_observed_mz", "m/z 689.1004 (principal ion; calculated 689.1003)", p2t, ["ion_5"]),
        field("byproduct_6_observed_mz", "m/z 465.2276 (principal ion; calculated 465.2277)", p2t, ["byproduct_6"]),
        field("ion_7_observed_mz", "m/z 833.1993 (principal ion; calculated 833.1945)", p23, ["ion_7"]),
        field("ion_7_disappearance_time", {"number": 5, "unit": "min"}, p2t, ["ion_7"]),
        field("ion_8_observed_mz", "m/z 834.2025 (principal ion; calculated 834.2023)", p23, ["ion_8"]),
        field("ion_9_observed_mz", "m/z 909.2265 (principal ion; calculated 909.2259)", p3t, ["ion_9"]),
    ],
    [
        ("Figure 1a is the 3 min sample; Figure 1c is the 2 h sample.", p2),
        ("Ion 8 is proposed to arise by oxidation of a neutral HPd(PPh3)2-vinyl species during ESI; ion 9 may arise by sequential ESI oxidation and gas-phase H radical elimination.", p23),
        ("The palladium-containing experimental isotope distributions matched simulations made with Bruker Xmass 6.1.2.", p3t),
    ],
    [
        "No yield, product ratio/selectivity, isolation, workup, or purification is reported for products 3a and 4a in the supplied main-text pages.",
        "Candidate organic-product SMILES encode connectivity only; drawn alkene geometry has not been independently structure-verified.",
        "The source does not establish whether ion 8 or ion 9 existed in solution rather than being generated during ESI/gas-phase analysis.",
        "Supporting information is mentioned but was not explicitly supplied or associated.",
    ],
))

participants_2b = scheme2_participants(
    "2b", "4-methoxyphenylboronic acid", "COc1ccc(B(O)O)cc1", "3b", "4b",
    "CCOC(=O)C(Cc1ccccc1)=C(C)c1ccc(OC)cc1",
    "C=C(c1ccc(OC)cc1)C(Cc1ccccc1)C(=O)OCC",
)
records.append(record(
    "scheme2_monitoring_2b", "Scheme 2, organoboronic acid 2b", "reported_experiment", p23,
    participants_2b,
    [{"step_id": "reaction_and_esi_monitoring", "participant_ids": [p["entity_id"] for p in participants_2b], "conditions": common_conditions + [
        field("reaction_time", None, []),
        field("sample_aliquot_volume", {"number": 20, "unit": "uL"}, p2t),
        field("operation", "Dilute the aliquot with 80 uL methanol and transfer to the positive-ion ESI source.", p2t),
        field("esi_source_flow_rate", "10 uL min-1", p2t),
    ]}],
    [
        field("product_3b_yield", None, [], ["product_3"]),
        field("product_4b_yield", None, [], ["product_4"]),
        field("monitoring_result", "Similar results were observed for organoboronic acid 2b; details are referred to the Supporting Information.", p3t),
    ],
    [("The main text reports similar results for 2b but places the detailed spectra/results in Supporting Information.", p3t)],
    [
        "Exact sampling times, detected-ion assignments for 2b, product yields/ratio, workup, and purification are not reported in the supplied main text.",
        "Candidate organic-product SMILES encode connectivity only and have not been independently structure-verified.",
        "Supporting information is mentioned but was not explicitly supplied or associated.",
    ],
))


def msms_record(label, product, precursor_mz, product_mz, calc_mz, formula):
    precursor_id = f"ion_{label}"
    product_id = f"ion_{product}"
    return record(
        f"figure2_sori_cad_{label}", f"Figure 2{chr(96 + {'7': 1, '8': 2, '9': 3}[label])}", "reported_experiment", p3,
        [
            participant(precursor_id, "reactant", label, f"palladium precursor ion {label}", None, p3),
            participant("argon", "reagent", "Ar", "argon", "[Ar]", p3),
            participant(product_id, "product", product, f"one-PPh3-loss palladium fragment {product}", None, p3),
        ],
        [{"step_id": "sori_cad", "participant_ids": [precursor_id, "argon", product_id], "conditions": [
            field("operation", "Positive-ion ESI tandem MS using SORI-CAD with argon; all isotopolog ions in the precursor cluster were isolated.", p3t),
            field("temperature", None, []),
            field("time", None, []),
        ]}],
        [
            field("precursor_principal_mz", f"m/z {precursor_mz}", p3, [precursor_id]),
            field("fragment_principal_mz", f"m/z {product_mz} (calculated {calc_mz})", p3, [product_id]),
            field("fragmentation_assignment", "loss of one PPh3 ligand", p3t, [product_id]),
        ],
        [
            (f"The text assigns fragment {product} formula {formula}.", p3t),
            ("Figure 2 also displays PPh3H+ at m/z 263.1; the figure does not explicitly make it a stoichiometric reaction product.", p3i),
        ],
        [
            "Collision energy, pressure, temperature, duration, and absolute ion abundance are not reported on the supplied pages.",
            "Organopalladium structures are retained as labels rather than asserted SMILES.",
        ],
    )


records.extend([
    msms_record("7", "7A", "833.1993", "571.1046", "571.1029", "C31H30O2P-106Pd+"),
    msms_record("8", "8A", "834.2025", "572.1105", "572.1107", "C31H31O2P-106Pd radical cation as printed"),
    msms_record("9", "9A", "909.2265", "647.1342", "647.1344", "C37H34O2P-106Pd+"),
])

mechanism_participants = [
    participant("pd_pph3_4", "catalyst", "Pd(PPh3)4", "tetrakis(triphenylphosphine)palladium(0)", None, p3),
    participant("acoh", "reagent", "HOAc", "acetic acid", "CC(=O)O", p3),
    participant("allenoate_1", "reactant", "1", "ethyl 2-benzylbuta-2,3-dienoate", "C=C=C(Cc1ccccc1)C(=O)OCC", p3),
    participant("phenylboronic_acid", "reactant", "PhB(OH)2", "phenylboronic acid", "OB(O)c1ccccc1", p3),
    participant("species_10", "unspecified_agent", "10", "palladium hydride acetate species", None, p3),
    participant("species_7", "unspecified_agent", "7", "cationic alkenylpalladium intermediate", None, p3),
    participant("species_11", "unspecified_agent", "11", "aryl-alkenylpalladium intermediate", None, p3),
    participant("product_3a", "product", "3a", "internal-alkene hydroarylation product", "CCOC(=O)C(Cc1ccccc1)=C(C)c1ccccc1", p3),
]
records.append(record(
    "scheme3_proposed_catalytic_cycle", "Scheme 3", "mechanism", p3,
    mechanism_participants,
    [
        {"step_id": "oxidative_addition", "participant_ids": ["pd_pph3_4", "acoh", "species_10"], "conditions": [field("operation", "Proposed oxidative addition of AcOH to Pd0 to form palladium hydride 10.", p3t)]},
        {"step_id": "hydropalladation", "participant_ids": ["species_10", "allenoate_1", "species_7"], "conditions": [field("operation", "Proposed hydropalladation of the less hindered terminal allene C=C bond with acetate elimination.", p3t)]},
        {"step_id": "aryl_transfer", "participant_ids": ["species_7", "phenylboronic_acid", "species_11"], "conditions": [field("operation", "Proposed aryl transfer from phenylboronic acid to intermediate 7.", p3t)]},
        {"step_id": "reductive_elimination", "participant_ids": ["species_11", "product_3a", "pd_pph3_4"], "conditions": [field("operation", "Proposed reductive elimination to afford product 3a and regenerate Pd0.", p3t)]},
    ],
    [],
    [
        ("Scheme 3 is explicitly presented as a proposed catalytic cycle based on the mass-spectrometric study.", p3),
        ("The cationic ESI ions 5 and 9 are shown beside proposed neutral/catalytic species, but ESI oxidation/gas-phase generation is discussed separately.", p3),
    ],
    ["This is a proposed mechanism, not an independently quantified experimental reaction; no stepwise kinetic, yield, workup, or purification data are reported."],
))

coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1,
            "state": "attempted",
            "regions": [
                {"region": "title, author block, and opening paragraph", "finding": "No reaction arrow, table, or individual experiment; the page introduces the mechanistic study.", "evidence_ids": [f"{DOC}:page1:image", f"{DOC}:page1:text"]},
                {"region": "supporting-information notice", "finding": "The article states that supporting information exists, but no SI file is explicitly supplied or associated in this workspace.", "evidence_ids": [f"{DOC}:page1:image", f"{DOC}:page1:text"]},
            ],
            "record_ids": [],
            "unresolved": ["No experiment-specific chemistry is present on this page; SI association remains unestablished."],
        },
        {
            "page": 2,
            "state": "attempted",
            "regions": [
                {"region": "left column, Scheme 1", "finding": "Generic Pd0/acid-catalyzed addition of an organoboronic acid to an allene; classified as a general scheme, not a reported quantified experiment.", "evidence_ids": [f"{DOC}:page2:image", f"{DOC}:page2:text"]},
                {"region": "left column, Scheme 2 and adjacent procedure paragraph", "finding": "Two distinct monitored reactions (2a and 2b) share explicit allenoate/boronic acid/catalyst/AcOH/THF quantities and room-temperature N2 conditions; structures 3a/4a and 3b/4b are shown without yields.", "evidence_ids": [f"{DOC}:page2:image", f"{DOC}:page2:text"]},
                {"region": "right column, Figure 1 and surrounding text", "finding": "Time-resolved positive-ion ESI-FTMS for reaction 2a at 3 min and 2 h detects ions 5-9 and by-product 6; these observations are merged into the 2a experiment rather than duplicated.", "evidence_ids": [f"{DOC}:page2:image", f"{DOC}:page2:text"]},
            ],
            "record_ids": [f"{DOC}:scheme1_general_addition", f"{DOC}:scheme2_monitoring_2a", f"{DOC}:scheme2_monitoring_2b"],
            "unresolved": ["No product yields, 3:4 regioisomer ratios, workup, or purification are stated; detailed 2b spectra are deferred to unavailable/unassociated SI."],
        },
        {
            "page": 3,
            "state": "attempted",
            "regions": [
                {"region": "upper-left prose continuing Figure 1 discussion", "finding": "Ion 9 assignment and the statement that 2b gave similar results are reported; 2b details remain in unassociated SI.", "evidence_ids": [f"{DOC}:page3:image", f"{DOC}:page3:text"]},
                {"region": "left column, Figure 2a-c", "finding": "Three distinct SORI-CAD tandem-MS experiments fragment precursor ions 7, 8, and 9 to 7A, 8A, and 9A respectively with argon and loss of one PPh3 ligand.", "evidence_ids": [f"{DOC}:page3:image", f"{DOC}:page3:text"]},
                {"region": "upper-right, Scheme 3 and explanatory prose", "finding": "Proposed Pd catalytic cycle; classified as mechanism and not as a newly quantified experiment.", "evidence_ids": [f"{DOC}:page3:image", f"{DOC}:page3:text"]},
            ],
            "record_ids": [f"{DOC}:scheme2_monitoring_2a", f"{DOC}:scheme2_monitoring_2b", f"{DOC}:figure2_sori_cad_7", f"{DOC}:figure2_sori_cad_8", f"{DOC}:figure2_sori_cad_9", f"{DOC}:scheme3_proposed_catalytic_cycle"],
            "unresolved": ["SORI-CAD collision energy/pressure and acquisition duration are absent; organopalladium structures remain label-only; the solution-versus-ESI origin of ions 8 and 9 is not resolved."],
        },
        {
            "page": 4,
            "state": "attempted",
            "regions": [
                {"region": "both columns, references 2-21", "finding": "Reference list only; cited prior literature is not converted into current-paper experiments.", "evidence_ids": [f"{DOC}:page4:image", f"{DOC}:page4:text"]},
                {"region": "reference 14", "finding": "States that starting allenoate 1 was prepared by a literature procedure; classified as cited prior work, not an experiment reported here.", "evidence_ids": [f"{DOC}:page4:image", f"{DOC}:page4:text"]},
            ],
            "record_ids": [],
            "unresolved": ["The cited preparation details for allenoate 1 are outside this paper and were not inferred."],
        },
    ],
}

OUT.parent.mkdir(parents=True, exist_ok=True)
COVERAGE.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
COVERAGE.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"records": len(records), "raw": str(OUT), "coverage": str(COVERAGE)}, ensure_ascii=False))
