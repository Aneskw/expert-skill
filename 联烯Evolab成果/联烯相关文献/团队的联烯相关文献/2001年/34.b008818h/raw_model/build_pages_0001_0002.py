#!/usr/bin/env python3
"""Build evidence-linked records for doc_5777406518096b18, PDF pages 1-2."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / "runs/current"
DOC = "doc_5777406518096b18"
P1T = f"{DOC}:page1:text"
P1I = f"{DOC}:page1:image"
P2T = f"{DOC}:page2:text"
P2I = f"{DOC}:page2:image"


def fact(value, evidence=()):
    return {
        "value": value,
        "evidence_ids": list(evidence) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def field(name, value, evidence=()):
    return {"name": name, "fact": fact(value, evidence)}


def participant(entity_id, role, label, evidence, name=None, amounts=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence) if name is not None else fact(None),
        "smiles": fact(None),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": amounts or [],
    }


def record(rid, kind, evidence, participants, conditions, outcomes, notes, unresolved):
    return {
        "record_id": f"{DOC}:{rid}",
        "document_id": DOC,
        "source_reaction_id": rid,
        "record_kind": kind,
        "status": "needs_review",
        "completeness": "partial",
        "evidence_ids": list(dict.fromkeys(evidence)),
        "participants": participants,
        "steps": [{
            "step_id": "step1",
            "participant_ids": [p["entity_id"] for p in participants],
            "conditions": conditions,
        }],
        "outcomes": outcomes,
        "notes": [fact(x, evidence) for x in notes],
        "review": {
            "method": "model",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved,
        },
    }


def missing_operational_fields(evidence, include_time=True):
    fields = []
    if include_time:
        fields.append(field("reaction_time", None))
    fields.extend([
        field("reaction_scale", None),
        field("concentration", None),
        field("atmosphere", None),
        field("workup", None),
        field("purification", None),
    ])
    return fields


records = []

# Scheme 1: resolution and subsequent acid release are separate stages.
ev = [P1I, P1T]
records.append(record(
    "scheme1_resolution_to_plus_2a", "reported_experiment", ev,
    [
        participant("s1_rac_1a", "reactant", "racemate 1a", ev,
                    "racemic 2-methyl-4-phenylbuta-2,3-dienoic acid"),
        participant("s1_l_cinchonidine", "reagent", "(L)-cinchonidine", ev,
                    amounts=[field("equivalents", {"number": 0.5, "unit": "equiv"}, ev)]),
        participant("s1_ethyl_acetate", "solvent", "ethyl acetate", ev),
        participant("s1_plus_2a", "product", "(+)-2a", ev,
                    "optically active acid-(L)-cinchonidine salt"),
    ],
    [field("operation", "recrystallization", ev)] + missing_operational_fields(ev),
    [
        field("yield", {"number": 43, "unit": "%"}, ev),
        field("specific_optical_rotation", "[alpha]D20 = +85.4 degrees", ev),
        field("yield_measurement_basis", None),
    ],
    ["The source describes resolution of racemate 1a and isolation of salt (+)-2a."],
    ["Initial solvent volume, temperature, time, atmosphere, workup details, isolated mass, and yield basis are not reported.",
     "The salt stoichiometry is not independently structure-verified; the prose reports use of 0.5 equivalent of (L)-cinchonidine."],
))

records.append(record(
    "scheme1_release_s_plus_1a", "reported_experiment", ev,
    [
        participant("s1b_plus_2a", "reactant", "(+)-2a", ev,
                    "optically active acid-(L)-cinchonidine salt"),
        participant("s1b_h2so4", "reagent", "dilute H2SO4", ev, "dilute sulfuric acid"),
        participant("s1b_s_plus_1a", "product", "S-(+)-1a", ev,
                    "S-(+)-2-methyl-4-phenylbuta-2,3-dienoic acid"),
    ],
    missing_operational_fields(ev),
    [field("yield", None), field("specific_optical_rotation", None)],
    ["The S assignment is stated to follow the Lowe-Brewster rule."],
    ["Acid concentration, charge, solvent, temperature, time, workup, purification, yield, and measured rotation are not reported."],
))


def add_cyclization(rid, kind, ev, substrate_label, substrate_name, reagent, product_label,
                    product_name, time_h, yield_pct, ee_pct, extra_notes=(), extra_unresolved=()):
    participants = [
        participant(f"{rid}_substrate", "reactant", substrate_label, ev, substrate_name),
        participant(f"{rid}_{reagent.lower()}", "reagent", reagent, ev,
                    amounts=[field("equivalents", {"number": 4, "unit": "equiv"}, ev)]),
        participant(f"{rid}_acetone", "solvent", "acetone", ev),
        participant(f"{rid}_water", "solvent", "H2O", ev, "water"),
        participant(f"{rid}_product", "product", product_label, ev, product_name),
    ]
    conditions = [
        field("solvent_ratio", "acetone-H2O (2:1)", ev),
        field("temperature", "60-65 degrees C", ev),
        field("reaction_time", {"number": time_h, "unit": "h"}, ev) if time_h is not None else field("reaction_time", None),
        field("reaction_scale", None), field("concentration", None), field("atmosphere", None),
        field("workup", None), field("purification", None),
    ]
    outcomes = [
        field("yield", {"number": yield_pct, "unit": "%"}, ev),
        field("enantiomeric_excess", {"number": ee_pct, "unit": "%"}, ev),
        field("ee_measurement_method", "HPLC on a Chiralpack AS column; n-hexane-isopropyl alcohol (65:35)", [P2T]),
        field("yield_measurement_basis", None),
    ]
    records.append(record(
        rid, kind, ev, participants, conditions, outcomes,
        list(extra_notes),
        ["Reaction scale, concentration, atmosphere, workup, purification, isolated mass, and yield basis are not reported."] + list(extra_unresolved),
    ))


# Scheme 2: direct cyclization of the resolved cinchonidine salt.
add_cyclization(
    "scheme2_plus_2a_cubr2", "reported_experiment", [P1I, P1T, P2T],
    "(+)-2a", "optically active acid-(L)-cinchonidine salt", "CuBr2",
    "S-(+)-3a", "S-(+)-beta-bromobutenolide 3a", 3, 95, 98,
)
add_cyclization(
    "scheme2_plus_2a_cucl2", "reported_experiment", [P1I, P1T, P2T],
    "(+)-2a", "optically active acid-(L)-cinchonidine salt", "CuCl2",
    "S-(+)-3b", "S-(+)-beta-chlorobutenolide 3b", None, 90, 99,
    extra_unresolved=["The chlorination time is not explicitly stated; it was not copied from the bromination experiment."],
)


# Scheme 3: free-acid comparison reactions.
add_cyclization(
    "scheme3_s_plus_1a_cubr2", "reported_experiment", [P1I, P1T, P2T],
    "S-(+)-1a", "S-(+)-2-methyl-4-phenylbuta-2,3-dienoic acid", "CuBr2",
    "S-(+)-3a", "S-(+)-beta-bromobutenolide 3a", None, 87, 97,
)
add_cyclization(
    "scheme3_s_plus_1a_cucl2", "reported_experiment", [P1I, P1T, P2T],
    "S-(+)-1a", "S-(+)-2-methyl-4-phenylbuta-2,3-dienoic acid", "CuCl2",
    "S-(+)-3b", "S-(+)-beta-chlorobutenolide 3b", None, 81, 98,
    extra_notes=["The Scheme 3 arrow visibly prints CuBr2 while the product list includes X = Cl; adjacent prose states that analogous chlorinations use CuCl2."],
    extra_unresolved=["The Scheme 3 graphical reagent label and the chlorinated outcome are presented inconsistently; CuCl2 is supported by adjacent prose rather than the arrow label."],
)


# Table 1: six row-level experiments.
table_rows = [
    (1, "1b", "R1 = C6H13, R2 = H, R3 = Me", "-9.10", "CuCl2", 6, "S-(-)-3c", 90, 94),
    (2, "1b", "R1 = C6H13, R2 = H, R3 = Me", "-9.10", "CuBr2", 3, "S-(-)-3d", 95, 95),
    (3, "1c", "R1 = alpha-naphthyl, R2 = H, R3 = Me", "+58.3", "CuCl2", 10, "S-(+)-3e", 88, 98),
    (4, "1c", "R1 = alpha-naphthyl, R2 = H, R3 = Me", "+58.3", "CuBr2", 3, "S-(+)-3f", 86, 98),
    (5, "1d", "R1 = Ph, R2 = H, R3 = C3H7", "+37.8", "CuCl2", 8, "S-(+)-3g", 92, 96),
    (6, "1d", "R1 = Ph, R2 = H, R3 = C3H7", "+37.8", "CuBr2", 3, "S-(+)-3h", 96, 96),
]
for entry, acid, substituents, rotation, reagent, hours, product, yield_pct, ee_pct in table_rows:
    rid = f"table1_entry{entry}"
    ev = [P2I, P2T]
    participants = [
        participant(f"{rid}_salt", "reactant", f"(L)-cinchonidine salt of acid {acid}", ev,
                    f"{acid}: {substituents}"),
        participant(f"{rid}_{reagent.lower()}", "reagent", reagent, ev,
                    amounts=[field("equivalents", {"number": 4, "unit": "equiv"}, ev)]),
        participant(f"{rid}_acetone", "solvent", "acetone", ev),
        participant(f"{rid}_water", "solvent", "H2O", ev, "water"),
        participant(f"{rid}_product", "product", product, ev),
    ]
    conditions = [
        field("salt_specific_optical_rotation", rotation, ev),
        field("solvent_ratio", "acetone-H2O (2:1)", ev),
        field("temperature", "60-65 degrees C", ev),
        field("reaction_time", {"number": hours, "unit": "h"}, ev),
        field("reaction_scale", None), field("concentration", None), field("atmosphere", None),
        field("workup", None), field("purification", None),
    ]
    outcomes = [
        field("yield", {"number": yield_pct, "unit": "%"}, ev),
        field("enantiomeric_excess", {"number": ee_pct, "unit": "%"}, ev),
        field("ee_measurement_method", "HPLC on a Chiralpack AS column; n-hexane-isopropyl alcohol (65:35)", [P2T]),
        field("yield_measurement_basis", None),
    ]
    notes = ["Table 1 is split row by row; the common header and footnotes apply to this row."]
    if entry in (3, 4):
        notes.append("The table footnote defines C10H7 as alpha-naphthyl.")
    if entry in (1, 2):
        notes.append("The paper states that the absolute configurations of products 3c and 3d were determined by X-ray diffraction.")
    else:
        notes.append("The paper states that other product configurations are based on the X-ray studies and further supported by CD spectra.")
    records.append(record(
        rid, "substrate_scope_entry", ev, participants, conditions, outcomes, notes,
        ["Reaction scale, concentration, atmosphere, workup, purification, isolated mass, yield basis, and full salt preparation are not reported.",
         "Structures are conveyed by the table drawing and R-group labels and remain unverified with null SMILES."],
    ))


# Scheme 4: two salt-resolution arrows and four separate CuX2 cyclizations.
ev4 = [P2I, P1T]
for suffix, base_label, product_label in [
    ("r_minus_base_to_plus_4a", "(R)-(-)-alpha-methylbenzylamine", "(+)-4a"),
    ("s_plus_base_to_minus_4a", "(S)-(+)-alpha-methylbenzylamine", "(-)-4a"),
]:
    rid = f"scheme4_{suffix}"
    records.append(record(
        rid, "reported_experiment", ev4,
        [
            participant(f"{rid}_rac_1a", "reactant", "racemate 1a", ev4,
                        "racemic 2-methyl-4-phenylbuta-2,3-dienoic acid"),
            participant(f"{rid}_base", "reagent", base_label, ev4),
            participant(f"{rid}_salt", "product", product_label, ev4,
                        "alpha-methylbenzylammonium salt of resolved acid 1a"),
        ],
        missing_operational_fields(ev4),
        [field("yield", None), field("specific_optical_rotation", None)],
        ["Scheme 4 depicts resolution of racemate 1a to the indicated diastereomeric acid-base salt."],
        ["Base amount, solvent, temperature, time, isolation method, yield, and numerical optical rotation are not reported."],
    ))

scheme4_cyclizations = [
    ("plus_4a_cubr2", "(+)-4a", "CuBr2", "S-(+)-3a", "S-(+)-beta-bromobutenolide 3a", 3, 92, 98),
    ("plus_4a_cucl2", "(+)-4a", "CuCl2", "S-(+)-3b", "S-(+)-beta-chlorobutenolide 3b", 6, 90, 97),
    ("minus_4a_cubr2", "(-)-4a", "CuBr2", "R-(-)-3a", "R-(-)-beta-bromobutenolide 3a", 3, 90, 98),
    ("minus_4a_cucl2", "(-)-4a", "CuCl2", "R-(-)-3b", "R-(-)-beta-chlorobutenolide 3b", 6, 93, 98),
]
for suffix, salt, reagent, product, product_name, hours, yield_pct, ee_pct in scheme4_cyclizations:
    add_cyclization(
        f"scheme4_{suffix}", "reported_experiment", [P2I, P1T, P2T],
        salt, "alpha-methylbenzylammonium salt of resolved acid 1a", reagent,
        product, product_name, hours, yield_pct, ee_pct,
    )


assert len(records) == 18

raw_path = RUN / "raw_model/records_pages_0001_0002.json"
raw_path.parent.mkdir(parents=True, exist_ok=True)
raw_path.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")

ids = [r["record_id"] for r in records]
page1_ids = [r["record_id"] for r in records if P1I in r["evidence_ids"] or P1T in r["evidence_ids"]]
page2_ids = [r["record_id"] for r in records if P2I in r["evidence_ids"] or P2T in r["evidence_ids"]]
coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1,
            "state": "attempted",
            "regions": [
                {
                    "region": "page 1 title, abstract, and introductory/current-method prose",
                    "finding": "Current aqueous CuX2-mediated cyclization conditions and the distinction between current work and cited prior halolactonization methods were inspected; cited background was not converted into current experiments.",
                    "evidence_ids": [P1T, P1I],
                },
                {
                    "region": "page 1 lower-left Scheme 1 and adjacent resolution prose",
                    "finding": "Two successive current-paper stages: resolution/recrystallization to salt (+)-2a, then dilute-H2SO4 release of S-(+)-1a.",
                    "evidence_ids": [P1I, P1T],
                },
                {
                    "region": "page 1 upper-right Scheme 2 and adjacent prose",
                    "finding": "Two separate salt cyclizations, CuBr2 to S-(+)-3a and CuCl2 to S-(+)-3b, with distinct yields and ee values.",
                    "evidence_ids": [P1I, P1T],
                },
                {
                    "region": "page 1 lower-right Scheme 3 and comparison prose",
                    "finding": "Two free-acid comparison cyclizations. The Scheme 3 arrow prints CuBr2 while the chlorinated outcome is supported by prose stating analogous use of CuCl2; the discrepancy is retained.",
                    "evidence_ids": [P1I, P1T],
                },
                {
                    "region": "page 1 right-column Scheme 4 discussion",
                    "finding": "Prose reports both alpha-methylbenzylamine resolutions and four salt cyclizations; graphical confirmation appears on page 2 and is linked rather than duplicated.",
                    "evidence_ids": [P1T, P1I],
                },
            ],
            "record_ids": page1_ids,
            "unresolved": [
                "The main article supplies no complete experimental procedure, scales, concentrations, workups, purification details, or isolated masses.",
                "The Scheme 2 CuCl2 reaction time is not explicitly stated.",
                "The Scheme 3 arrow/reagent presentation for the chlorinated product is internally ambiguous.",
                "No supplied SI is associated; missing details were not inferred.",
            ],
        },
        {
            "page": 2,
            "state": "attempted",
            "regions": [
                {
                    "region": "page 2 top Table 1, including reaction header, six rows, and footnotes",
                    "finding": "Six distinct substrate-scope experiments were transcribed row by row with R-group labels, salt rotations, CuX2 identity, reaction time, yield, ee, and applicable footnotes.",
                    "evidence_ids": [P2I, P2T],
                },
                {
                    "region": "page 2 left-center Scheme 4",
                    "finding": "Two salt-resolution arrows and four separate CuBr2/CuCl2 cyclizations were identified; each condition/outcome pair is an independent record.",
                    "evidence_ids": [P2I, P2T],
                },
                {
                    "region": "page 2 notes and references, especially notes 9-10",
                    "finding": "HPLC ee method and X-ray assignment context were linked to matching records; bibliography and crystallographic-data citation were not fabricated into reactions.",
                    "evidence_ids": [P2T, P2I],
                },
            ],
            "record_ids": page2_ids,
            "unresolved": [
                "Table 1 and Scheme 4 omit reaction scales, workups, purifications, isolated masses, and yield bases.",
                "Structures are represented by drawings and R-group labels; all SMILES remain null and unverified.",
                "The article cites crystallographic data online, but no experimental SI file is supplied or explicitly associated in this pilot.",
            ],
        },
    ],
}
coverage_path = RUN / "coverage/pages_0001_0002.json"
coverage_path.parent.mkdir(parents=True, exist_ok=True)
coverage_path.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

tasks_path = RUN / "tasks.json"
tasks = json.loads(tasks_path.read_text())
for task in tasks:
    if task.get("document_id") == DOC and task.get("evidence_id") in (P1T, P2T):
        task["state"] = "attempted"
        task["visual_evidence_id"] = P1I if task["evidence_id"] == P1T else P2I
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"records": len(records), "record_ids": ids, "coverage": str(coverage_path)}, ensure_ascii=False, indent=2))
