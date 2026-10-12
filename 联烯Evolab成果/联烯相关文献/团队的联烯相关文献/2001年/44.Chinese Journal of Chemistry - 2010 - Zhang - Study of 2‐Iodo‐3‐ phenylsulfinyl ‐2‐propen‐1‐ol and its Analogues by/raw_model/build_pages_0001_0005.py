#!/usr/bin/env python3
"""Build evidence-linked records for doc_cb96b79d136f980f, PDF pages 1-5."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / "runs" / "current"
DOC = "doc_cb96b79d136f980f"


def write(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def fact(value, evidence=()):
    return {
        "value": value,
        "evidence_ids": list(evidence),
        "verification": "missing" if value is None else "unreviewed",
    }


def field(name, value, evidence=(), target_entity_ids=None):
    result = {"name": name, "fact": fact(value, evidence)}
    if target_entity_ids:
        result["target_entity_ids"] = list(target_entity_ids)
    return result


def participant(entity_id, role, label, name, evidence, smiles=None, amounts=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence) if name is not None else fact(None),
        "smiles": fact(smiles, evidence) if smiles is not None else fact(None),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": amounts or [],
    }


def record(suffix, kind, evidence, participants, steps, outcomes, notes, unresolved):
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
        "outcomes": outcomes,
        "notes": [fact(note, note_evidence) for note, note_evidence in notes],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved,
        },
    }


P1I = f"{DOC}:page1:image"
P2I = f"{DOC}:page2:image"
P3I = f"{DOC}:page3:image"
P4I = f"{DOC}:page4:image"
P5I = f"{DOC}:page5:image"


records = []

# The two displayed synthetic arrows are explicitly tied to reference 8 and are
# therefore prior-literature examples, not new synthetic experiments in this
# mass-spectrometry paper.
stage1_participants = [
    participant("generic_propargylic_alcohol", "reactant", "generic substituted propargylic alcohol", None, [P2I]),
    participant("phscl", "reagent", "PhSCl", "benzenesulfenyl chloride", [P2I], "ClSc1ccccc1"),
    participant("et3n", "reagent", "Et3N", "triethylamine", [P2I], "CCN(CC)CC"),
    participant("ch2cl2", "solvent", "CH2Cl2", "dichloromethane", [P2I], "ClCCl"),
    participant("generic_allenic_sulfoxide", "product", "generic 1,2-allenic sulfoxide", None, [P2I]),
]
records.append(
    record(
        "prior_synthesis_stage1_allenic_sulfoxide",
        "literature_example",
        [P2I],
        stage1_participants,
        [{
            "step_id": "allenic_sulfoxide_formation",
            "participant_ids": [p["entity_id"] for p in stage1_participants],
            "conditions": [field("temperature", {"number": -85, "unit": "°C"}, [P2I])],
        }],
        [],
        [
            ("The displayed R1/R2/R3 scheme is a generic preparation of the allenic-sulfoxide precursors used for samples A-G.", [P2I]),
            ("The paper cites reference 8 for synthesis/structure identification; it does not report a stage-specific yield here.", [P2I]),
        ],
        [
            "Generic R-group structures are not expanded to compound-specific structures.",
            "Reaction scale, reagent amounts, time, atmosphere, workup, purification, and yield are not reported on this page.",
            "The source does not provide row-specific stage-1 outcomes for samples A-G.",
        ],
    )
)

stage2_participants = [
    participant("generic_allenic_sulfoxide", "reactant", "generic 1,2-allenic sulfoxide", None, [P2I]),
    participant("iodine", "reagent", "I2", "iodine", [P2I], "II"),
    participant("lioac", "reagent", "LiOAc", "lithium acetate", [P2I], "[Li+].CC(=O)[O-]"),
    participant("mecn", "solvent", "MeCN", "acetonitrile", [P2I], "CC#N"),
    participant("water", "reagent", "H2O", "water", [P2I], "O"),
    participant("generic_iodo_allylic_alcohol", "product", "generic 2-iodo phenylsulfinyl allylic alcohol", None, [P2I]),
]
records.append(
    record(
        "prior_synthesis_stage2_halohydroxylation",
        "literature_example",
        [P2I],
        stage2_participants,
        [{
            "step_id": "iodohydroxylation",
            "participant_ids": [p["entity_id"] for p in stage2_participants],
            "conditions": [field("reaction_medium", "MeCN-H2O (7:1), ratio basis not stated", [P2I])],
        }],
        [],
        [
            ("The paper states that all samples were synthesized by halohydroxylation of 1,2-allenic sulfoxides with I2/H2O and cites reference 8.", [P2I]),
            ("The substituent table defines samples A-G, but the present paper supplies no row-specific synthesis yields.", [P2I]),
        ],
        [
            "This is cited prior synthesis rather than a new synthetic experiment in the mass-spectrometry study.",
            "Reaction scale, reagent amounts, temperature, time, atmosphere, workup, purification, and yield are missing.",
            "The MeCN-H2O 7:1 ratio is preserved as printed; its measurement basis is not stated.",
            "Generic and sample-specific structures remain unverified.",
        ],
    )
)


sample_names = {
    "A": "(E)-2-iodo-3-(phenylsulfinyl)-2-propen-1-ol",
    "B": "(E)-2-iodo-3-phenyl-3-(phenylsulfinyl)-2-propen-1-ol",
    "C": "(E)-2-iodo-3-(phenylsulfinyl)-2-hepten-1-ol",
    "D": "(E)-2-iodo-1-(phenylsulfinyl)-1-hepten-3-ol",
    "E": "(E)-2-iodo-4,4-dimethyl-1-(phenylsulfinyl)-1-penten-3-ol",
    "F": "1-[(E)-1'-iodo-2'-(phenylsulfinyl)ethenyl]-1-cyclohexanol",
    "G": "(E)-3-iodo-2-methyl-4-(phenylsulfinyl)-3-octen-2-ol",
}

mw = {"A": 308, "B": 384, "C": 364, "D": 364, "E": 364, "F": 376, "G": 392}
peaks = {
    "A": [("a", 309, 100), ("b", 291, 40), ("e", 165, 6), ("f", 163, 7), ("g", 125, 21), ("h", 109, 18)],
    "B": [("a", 385, 100), ("b", 367, 33), ("c", 241, 3), ("d", 240, 4), ("g", 125, 6), ("h", 109, 1)],
    "C": [("a", 365, 100), ("b", 347, 48), ("g", 125, 2), ("h", 109, 1)],
    "D": [("a", 365, 100), ("b", 347, 68), ("c", 221, 1), ("d", 220, 1), ("f", 189, 1), ("g", 125, 1), ("h", 109, 1)],
    "E": [("a", 365, 100), ("b", 347, 51), ("c", 221, 6), ("d", 220, 3), ("e", 191, 1), ("f", 189, 17), ("g", 125, 10), ("h", 109, 19)],
    "F": [("a", 377, 69), ("b", 359, 100), ("c", 233, 4), ("d", 232, 3), ("g", 125, 12), ("h", 109, 9)],
    "G": [("a", 393, 45), ("b", 375, 100), ("c", 249, 3), ("d", 248, 4), ("g", 125, 4), ("h", 109, 1)],
}


def analytical_participant(label):
    return participant(
        f"sample_{label}",
        "unspecified_agent",
        f"sample {label}",
        sample_names[label],
        [P2I],
        None,
        [field("sample_mass", {"number": 1, "unit": "ug", "qualifier": "approx", "raw_text": "about 1 μg"}, [P2I])],
    )


def ms_conditions(mode):
    return [
        field("instrument", "HP 5989A mass spectrometer", [P2I]),
        field("ionization_mode", mode, [P2I]),
        field("electron_energy", "70 eV", [P2I]),
        field("filament_emission_current", "300 μA", [P2I]),
        field("source_temperature", {"number": 300, "unit": "°C"}, [P2I]),
        field("scan_window", "m/z 40-600 amu as printed", [P2I]),
        field("pre_insertion_wait_time", "some minutes", [P2I]),
        field("probe_tip_temperature", {"number": 320, "unit": "°C", "qualifier": "approx", "raw_text": "about 320 °C"}, [P2I]),
        field("probe_heating_rate", "rapidly", [P2I]),
    ]


for label in "ABCDEFG":
    analyte = analytical_participant(label)
    peak_values = [
        {"fragment_code": code, "m_z": mz_value, "relative_abundance_percent": abundance}
        for code, mz_value, abundance in peaks[label]
    ]
    records.append(
        record(
            f"sci_sample_{label.lower()}",
            "reported_experiment",
            [P2I, P3I, P5I],
            [analyte],
            [{
                "step_id": "sci_mass_spectrometry",
                "participant_ids": [analyte["entity_id"]],
                "conditions": ms_conditions("self-chemical ionization (SCI)"),
            }],
            [
                field("nominal_molecular_weight", mw[label], [P5I]),
                field("sci_peak_list", peak_values, [P3I, P5I]),
                field("spectral_normalization", "relative to the base peak", [P2I, P3I]),
            ],
            [
                ("The analyte is represented as an analytical sample, not as a synthetic reactant or product.", [P2I]),
                ("Fragment codes a-h follow the generic ion structures drawn on page 4; blank Table 1 cells are not converted into zero-abundance peaks.", [P4I, P5I]),
                ("No reagent gas was applied in SCI.", [P4I]),
            ],
            [
                "The named sample structure and alkene/sulfoxide stereochemistry have not been independently structure-verified; SMILES remains null.",
                "Exact ion-source pressure, pre-insertion wait duration, and scan timing are not reported.",
                "The paper reports relative abundance values but no uncertainty or replicate count.",
                "The ion-fragment structural assignments remain mechanistic interpretations rather than verified structures.",
            ],
        )
    )


# The EI comparison is a distinct analytical run from the SCI record for E.
ei_analyte = analytical_participant("E")
records.append(
    record(
        "ei_sample_e_comparison",
        "reported_experiment",
        [P2I, P4I],
        [ei_analyte],
        [{
            "step_id": "electron_impact_mass_spectrometry",
            "participant_ids": [ei_analyte["entity_id"]],
            "conditions": ms_conditions("electron impact ionization (EI)"),
        }],
        [
            field("labeled_ei_m_z_peaks", [41, 57, 69, 77, 109, 127, 133, 149, 189, 273, 291], [P4I]),
            field("molecular_ion_observed", False, [P4I]),
        ],
        [
            ("Figure 2 is the EI mass spectrum of sample E; the paper states that EI spectra of these compounds show no molecular ions.", [P4I]),
            ("Only labeled m/z positions were transcribed; bar heights were not digitized into exact relative abundances.", [P4I]),
        ],
        [
            "The EI figure provides no tabulated exact relative abundance values.",
            "The named sample structure remains unverified and its SMILES is null.",
            "Exact ion-source pressure, pre-insertion wait duration, and scan timing are not reported.",
        ],
    )
)


# Generic SCI ion-molecule chemistry and the page-4 fragment map are a proposed
# mechanistic interpretation, not additional observed synthetic experiments.
mechanism_participants = [
    participant("xh_plus", "unspecified_agent", "XH+", "proton-donating fragment ion", [P1I]),
    participant("neutral_m", "reactant", "M", "neutral analyte molecule", [P1I]),
    participant("mh_plus", "product", "MH+", "protonated analyte molecule", [P1I, P4I]),
    participant("neutral_x", "product", "X", "neutral fragment after proton transfer", [P1I]),
]
records.append(
    record(
        "mechanism_sci_self_protonation_fragmentation",
        "mechanism",
        [P1I, P3I, P4I, P5I],
        mechanism_participants,
        [
            {
                "step_id": "electron_impact_fragment_generation",
                "participant_ids": ["neutral_m", "xh_plus"],
                "conditions": [field("operation", "initial electron-impact fragmentation produces fragment ions", [P4I])],
            },
            {
                "step_id": "self_protonation",
                "participant_ids": ["xh_plus", "neutral_m", "mh_plus", "neutral_x"],
                "conditions": [field("operation", "XH+ + M -> MH+ + X", [P1I])],
            },
        ],
        [
            field("proposed_fragment_codes", ["a", "b", "c", "d", "e", "f", "g", "h"], [P4I, P5I]),
            field("aromatic_fragment_m_z_values", [51, 77], [P4I]),
            field("alkene_fragment_m_z_values", [41, 55, 69], [P4I]),
        ],
        [
            ("The page-4 structures a-h are proposed pathways/ion assignments for the SCI spectra, not isolated products.", [P4I]),
            ("The paper describes an initial EI stage followed, at higher analyte concentration, by ion-molecule reactions that yield a mixed EI/CI spectrum.", [P4I]),
            ("The assignments of m/z 51/77 to aromatic structures and 41/55/69 to alkene structures are stated as possibilities.", [P4I]),
        ],
        [
            "Generic species XH+, M, MH+, and X are not fully specified molecules and have no SMILES.",
            "Fragment structures a-h contain generic R groups and remain unverified.",
            "The proposed pathway is not direct evidence of isolated or independently observed intermediates.",
        ],
    )
)


record_path = RUN / "raw_model" / "records_pages_0001_0005.json"
write(record_path, records)

ids = {record["source_reaction_id"]: record["record_id"] for record in records}
coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1,
            "state": "attempted",
            "regions": [
                {
                    "region": "title, abstract, and introduction",
                    "finding": "The paper is an SCI mass-spectrometry study of seven analytes; no preparative reaction experiment is reported on this page.",
                    "evidence_ids": [P1I],
                },
                {
                    "region": "Equation (1), lower right column",
                    "finding": "Generic self-protonation mechanism XH+ + M -> MH+ + X; classified as mechanism, not an observed synthetic reaction.",
                    "evidence_ids": [P1I],
                },
            ],
            "record_ids": [ids["mechanism_sci_self_protonation_fragmentation"]],
            "unresolved": ["Equation (1) uses generic species and does not identify a unique ion pair for any sample."],
        },
        {
            "page": 2,
            "state": "attempted",
            "regions": [
                {
                    "region": "sample list A-G and two-arrow synthesis scheme with R1/R2/R3 table",
                    "finding": "Two successive cited prior-synthesis stages are shown; the second stage defines samples A-G but supplies no row-specific synthesis yields.",
                    "evidence_ids": [P2I],
                },
                {
                    "region": "Experimental section, lower half",
                    "finding": "Common HP 5989A SCI/EI operating conditions, approximately 1 ug sample charge, impurity-evaporation wait, and rapid heating to about 320 C are reported.",
                    "evidence_ids": [P2I],
                },
                {
                    "region": "Results and discussion opening, lower right",
                    "finding": "Figure 1 is introduced as seven SCI spectra dominated by MH+ or [M-17]+ and other characteristic ions.",
                    "evidence_ids": [P2I],
                },
            ],
            "record_ids": [
                ids["prior_synthesis_stage1_allenic_sulfoxide"],
                ids["prior_synthesis_stage2_halohydroxylation"],
                *[ids[f"sci_sample_{label.lower()}"] for label in "ABCDEFG"],
                ids["ei_sample_e_comparison"],
            ],
            "unresolved": [
                "The cited synthesis lacks local row-specific scale, time, workup, purification, and yield data.",
                "The exact duration of the pre-insertion wait is stated only as some minutes.",
                "The filename says 2010, while the rendered article header and bibliographic data say 2001.",
            ],
        },
        {
            "page": 3,
            "state": "attempted",
            "regions": [
                {
                    "region": "Figure 1, seven panels A-G",
                    "finding": "Seven separate SCI spectra are shown. They are linked to the seven sample records and cross-checked against Table 1 rather than counted as duplicate experiments.",
                    "evidence_ids": [P3I],
                },
                {
                    "region": "text below Figure 1",
                    "finding": "The text links m/z 125 and 109 and other ions to Table 1 and introduces proposed ionic-product formation pathways.",
                    "evidence_ids": [P3I],
                },
            ],
            "record_ids": [*[ids[f"sci_sample_{label.lower()}"] for label in "ABCDEFG"], ids["mechanism_sci_self_protonation_fragmentation"]],
            "unresolved": ["Only labeled Figure-1 peaks and Table-1 relative abundances were transcribed; unlabeled minor peaks were not digitized."],
        },
        {
            "page": 4,
            "state": "attempted",
            "regions": [
                {
                    "region": "top fragment-ion map a-h",
                    "finding": "Proposed generic SCI fragmentation/ion structures; classified as mechanism and not as isolated products.",
                    "evidence_ids": [P4I],
                },
                {
                    "region": "left-column discussion and Figure 2",
                    "finding": "EI comparison for sample E; labeled m/z peaks were recorded, and the stated absence of a molecular ion was retained.",
                    "evidence_ids": [P4I],
                },
                {
                    "region": "right-column SCI process discussion",
                    "finding": "Textual two-stage SCI explanation and five qualitative sample requirements; no additional reaction run is reported.",
                    "evidence_ids": [P4I],
                },
            ],
            "record_ids": [ids["ei_sample_e_comparison"], ids["mechanism_sci_self_protonation_fragmentation"], *[ids[f"sci_sample_{label.lower()}"] for label in "ABCDEFG"]],
            "unresolved": [
                "Exact EI relative abundances are not tabulated and were not estimated from bar heights.",
                "Fragment structures contain generic R groups and are not independently structure-verified.",
            ],
        },
        {
            "page": 5,
            "state": "attempted",
            "regions": [
                {
                    "region": "Table 1, main mass spectral data",
                    "finding": "Seven rows A-G were transcribed as separate SCI analytical records with nominal molecular weight and listed m/z/relative-abundance pairs.",
                    "evidence_ids": [P5I],
                },
                {
                    "region": "references 1-8",
                    "finding": "Bibliography only; reference 8 supports the prior-synthesis classification but does not supply local experimental details.",
                    "evidence_ids": [P5I],
                },
            ],
            "record_ids": [*[ids[f"sci_sample_{label.lower()}"] for label in "ABCDEFG"], ids["mechanism_sci_self_protonation_fragmentation"]],
            "unresolved": [
                "Table 1 reports relative abundances without uncertainty or replicate count.",
                "Blank fragment-code cells were preserved as unreported rather than interpreted as zero.",
            ],
        },
    ],
}
write(RUN / "coverage" / "pages_0001_0005.json", coverage)

# Mark exactly these five page tasks attempted and repair the absent visual IDs
# with their actual rendered page-image evidence IDs.
task_path = RUN / "tasks.json"
tasks = json.loads(task_path.read_text())
for task in tasks:
    page = int(task["evidence_id"].split(":page", 1)[1].split(":", 1)[0])
    if page in range(1, 6):
        task["state"] = "attempted"
        task["visual_evidence_id"] = f"{DOC}:page{page}:image"
        task["reason"] = "Original page image inspected; findings and unresolved items are recorded in coverage/pages_0001_0005.json."
write(task_path, tasks)

print(json.dumps({"records": len(records), "coverage_pages": len(coverage["pages"]), "record_path": str(record_path.relative_to(ROOT))}, ensure_ascii=False))
