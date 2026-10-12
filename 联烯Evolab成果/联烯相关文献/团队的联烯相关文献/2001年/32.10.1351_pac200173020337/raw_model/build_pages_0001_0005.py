#!/usr/bin/env python3
"""Build machine extraction records for doc_10be2f53cc32047e, PDF pages 1-5."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / "runs" / "current"
DOC = "doc_10be2f53cc32047e"


def ev(page: int, kind: str) -> str:
    return f"{DOC}:page{page}:{kind}"


def fact(value, evidence=()):
    return {
        "value": value,
        "evidence_ids": list(dict.fromkeys(evidence)) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def field(name, value, evidence=()):
    return {"name": name, "fact": fact(value, evidence)}


def participant(entity_id, role, label, evidence, name=None, amounts=()):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence) if name is not None else fact(None),
        "smiles": fact(None),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": [field(n, v, evidence) for n, v in amounts],
    }


def record(
    suffix,
    kind,
    evidence,
    participants,
    conditions=(),
    outcomes=(),
    notes=(),
    unresolved=(),
):
    evidence = list(dict.fromkeys(evidence))
    pids = [p[0] for p in participants]
    rec = {
        "record_id": f"{DOC}:{suffix}",
        "document_id": DOC,
        "source_reaction_id": suffix,
        "record_kind": kind,
        "status": "needs_review",
        "completeness": "partial",
        "evidence_ids": evidence,
        "participants": [participant(*p) for p in participants],
        "steps": [
            {
                "step_id": "step1",
                "participant_ids": pids,
                "conditions": [field(n, v, evidence) for n, v in conditions]
                + [
                    field("reaction_scale", None),
                    field("atmosphere", None),
                    field("concentration", None),
                    field("workup", None),
                    field("purification", None),
                ],
            }
        ],
        "outcomes": [field(n, v, evidence) for n, v in outcomes],
        "notes": [fact(n, evidence) for n in notes],
        "review": {
            "method": "model",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": list(unresolved)
            + [
                "No supporting-information file is supplied or explicitly associated.",
                "All structures are represented only by source labels/names; SMILES and structure verification remain unavailable.",
            ],
        },
    }
    return rec


I1, T1 = ev(1, "image"), ev(1, "text")
I2, T2 = ev(2, "image"), ev(2, "text")
I3, T3 = ev(3, "image"), ev(3, "text")
I4, T4 = ev(4, "image"), ev(4, "text")
I5, T5 = ev(5, "image"), ev(5, "text")

records = []

# Page 1: prior-work summaries and the generic two-pathway diagram.
records.append(record(
    "intro_benzylation_ref3", "literature_example", [T1, I1],
    [
        ("arylalkyne", "reactant", "1-arylalk-1-yne-derived lithium reagent", [T1, I1], None, ()),
        ("benzyl_halide", "reactant", "benzylic halide", [T1, I1], None, ()),
        ("alkyne_product", "product", "substituted 1-aryl-1-alkyne", [T1, I1], None, ()),
    ],
    outcomes=(("yield", "good yield (qualitative)"),),
    notes=("Cited prior work, reference 3; not a current-paper experimental procedure.",),
    unresolved=("Individual substrate identities, conditions, numerical yields, and experimental procedure are not reported here.",),
))
records.append(record(
    "intro_allylation_ref4", "literature_example", [T1, I1],
    [
        ("arylalkyne", "reactant", "1-arylalk-1-yne-derived lithium reagent", [T1, I1], None, ()),
        ("allyl_halide", "reactant", "allylic halide", [T1, I1], None, ()),
        ("allene_product", "product", "1-phenyl-1,2-allene", [T1, I1], None, ()),
    ],
    outcomes=(("yield", "good yield (qualitative)"),),
    notes=("Cited prior work, reference 4; not a current-paper experimental procedure.",),
    unresolved=("Individual substrate identities, conditions, numerical yields, and experimental procedure are not reported here.",),
))
records.append(record(
    "scheme1_pathways", "general_scheme", [T1, I1],
    [
        ("organopalladium", "reactant", "RPdX", [T1, I1], None, ()),
        ("allenyl_propargyl_metal", "reactant", "allenic/propargylic metallic reagent", [T1, I1], None, ()),
        ("allene", "product", "Pathway I allene", [T1, I1], None, ()),
        ("alkyne", "product", "Pathway II alkyne", [T1, I1], None, ()),
    ],
    outcomes=(("possible_products", ["allene (Pathway I)", "alkyne (Pathway II)"]),),
    notes=("Generic conceptual scheme; R and M are unspecified variables, not one experimental run.",),
    unresolved=("Specific participants, conditions, and yields do not apply to this generic scheme.",),
))

# Scheme 2: generic aryl-halide coupling family, with footnote 7 linked from page 5.
records.append(record(
    "scheme2_aryl_coupling_family", "general_scheme", [T2, I2, T5, I5],
    [
        ("phenylalkyne", "reactant", "1-phenylalk-1-yne (R = H or n-C3H7)", [T2, I2], None, ()),
        ("aryl_halide", "reactant", "ArX", [T2, I2], None, ()),
        ("hgcl2", "catalyst", "HgCl2", [T2, I2], "mercury(II) chloride", (("loading", {"number": 1.5, "unit": "mol%"}),)),
        ("nbuli", "reagent", "n-BuLi", [T2, I2], "n-butyllithium", ()),
        ("znbr2", "reagent", "ZnBr2", [T2, I2], "zinc bromide", (("amount", {"number": 1.5, "unit": "equiv"}),)),
        ("pd0", "catalyst", "Pd(0) catalyst", [T2, I2], None, ()),
        ("diaryl_allene", "product", "1,2-diaryl-1,2-diene family", [T2, I2], None, ()),
    ],
    conditions=(("coupling_temperature", "room temperature"),),
    outcomes=(("yield", "moderate to good yields (qualitative family statement)"),
              ("selectivity", "allene products; alkynic Pathway-II products not formed")),
    notes=(
        "Cited prior results in reference 5; Scheme 2 is a generic family presentation.",
        "The reaction can proceed without HgCl2, and Pd(PPh3)4 is generally more reactive than PdCl2(PPh3)2; no row-level values are supplied.",
        "Footnote 7 states that under Procedure A, 1-phenylprop-1-yne afforded a mixture of allenic and propargylic zinc reagents.",
    ),
    unresolved=("No individual aryl-halide rows, reaction times, numerical yields, solvent, workup, or purification are reported in this account.",),
))


def scheme3_record(suffix, halide_label, product_label, temp, time_h, yield_value, extra_notes=()):
    e = [T2, I2]
    common = [
        ("alkyne1", "reactant", "1-phenyl-1-propyne (1)", e, "1-phenyl-1-propyne", ()),
        ("halide", "reactant", halide_label, e, None, ()),
        ("hgcl2", "catalyst", "HgCl2", e, "mercury(II) chloride", (("loading", {"number": 1.5, "unit": "mol%"}),)),
        ("nbuli", "reagent", "n-BuLi", e, "n-butyllithium", ()),
        ("znbr2", "reagent", "ZnBr2", e, "zinc bromide", ()),
        ("pdpph3", "catalyst", "Pd(PPh3)4", e, "tetrakis(triphenylphosphine)palladium(0)", (("loading", {"number": 5, "unit": "mol%"}),)),
        ("product", "product", product_label, e, None, ()),
    ]
    cond = [
        ("lithiation_temperature", {"number": -78, "unit": "°C"}),
        ("transmetallation_temperature_program", "-78 °C to room temperature"),
        ("coupling_temperature", temp),
        ("coupling_time", {"number": time_h, "unit": "h"}),
    ]
    return record(
        suffix, "literature_example", e, common, conditions=cond,
        outcomes=(("yield", yield_value), ("yield_measurement_basis", None)),
        notes=("Summarized cited result from reference 6.",) + tuple(extra_notes),
        unresolved=("Solvent, reaction scale, yield basis, workup, purification, and isolated mass are not reported in this account.",),
    )


records.extend([
    scheme3_record("scheme3_e_iodostyrene", "(E)-1-iodostyrene", "corresponding allene coupling product (R = Ph)", "room temperature", 20, "<5%", ("Prose describes the product as not obtained in a decent yield.",)),
    scheme3_record("scheme3_e_iodohexene", "(E)-1-iodohexene", "corresponding allene coupling product (R = n-C4H9)", "room temperature", 20, "<5%", ("Prose describes the product as not obtained in a decent yield.",)),
    scheme3_record("scheme3_alpha_bromostyrene", "alpha-bromostyrene", "2,3-diphenyl-1,3,4-pentatriene (2)", "room temperature", 1.5, {"number": 29, "unit": "%"}, ("Pathway-I allene-forming product.",)),
    scheme3_record("scheme3_alpha_iodostyrene", "alpha-iodostyrene", "2,3-diphenyl-1,3,4-pentatriene (2)", "room temperature", 2, {"number": 33, "unit": "%"}, ("Pathway-I allene-forming product.",)),
    scheme3_record("scheme3_z_iodopropenoate", "ethyl (Z)-3-iodopropenoate", "ethyl 6-phenylhex-5-yn-2(Z)-enoate (Z-3)", {"number": 0, "unit": "°C"}, 1, {"number": 66, "unit": "%"}, ("Pathway-II alkynic product; C=C configuration remained intact and the product was exclusive.",)),
    scheme3_record("scheme3_z_bromopropenoate", "ethyl (Z)-3-bromopropenoate", "ethyl 6-phenylhex-5-yn-2(Z)-enoate (Z-3)", {"number": 0, "unit": "°C"}, 4, {"number": 69, "unit": "%"}, ("Pathway-II alkynic product.",)),
    scheme3_record("scheme3_z_chloropropenoate", "ethyl (Z)-3-chloropropenoate", "ethyl 6-phenylhex-5-yn-2(Z)-enoate (Z-3)", {"number": 0, "unit": "°C"}, 4, {"number": 0, "unit": "%"}, ("Explicit zero-yield result retained.",)),
    scheme3_record("scheme3_e_iodopropenoate", "ethyl (E)-3-iodopropenoate", "ethyl 6-phenylhex-5-yn-2(E)-enoate (E-3)", {"number": -5, "unit": "°C"}, 0.75, {"number": 88, "unit": "%"}, ("Pathway-II alkynic product.",)),
])

records.append(record(
    "scheme3_z_iodopropenitrile", "literature_example", [T2, I2],
    [
        ("alkyne1", "reactant", "1-phenyl-1-propyne", [T2, I2], "1-phenyl-1-propyne", ()),
        ("nitrile", "reactant", "(Z)-3-iodopropenitrile", [T2, I2], None, ()),
        ("hgcl2", "catalyst", "HgCl2", [T2, I2], "mercury(II) chloride", ()),
        ("nbuli", "reagent", "n-BuLi", [T2, I2], "n-butyllithium", ()),
        ("znbr2", "reagent", "ZnBr2", [T2, I2], "zinc bromide", ()),
        ("pdpph3", "catalyst", "Pd(PPh3)4", [T2, I2], "tetrakis(triphenylphosphine)palladium(0)", ()),
        ("product", "product", "6-phenylhex-5-yn-2(Z)-enitrile", [T2, I2], None, ()),
    ],
    outcomes=(("yield", None), ("selectivity", "reacted similarly to the (Z)-iodopropenoate case")),
    notes=("Prose-only cited result from reference 6.",),
    unresolved=("Catalyst/reagent loadings, temperature, time, numerical yield, solvent, scale, workup, and purification are not reported for this nitrile example.",),
))

# Page 3, Scheme 4: stability and migration are distinct condition sets.
records.append(record(
    "scheme4_no_migration", "literature_example", [T3, I3],
    [
        ("e3", "reactant", "ethyl 6-phenylhex-5-yn-2(E)-enoate (E-3)", [T3, I3], None, ()),
        ("hgcl2", "catalyst", "HgCl2", [T3, I3], "mercury(II) chloride", (("loading", {"number": 1.5, "unit": "mol%"}),)),
        ("thf", "solvent", "THF", [T3, I3], "tetrahydrofuran", ()),
        ("pdpph3", "catalyst", "Pd(PPh3)4", [T3, I3], "tetrakis(triphenylphosphine)palladium(0)", (("loading", {"number": 5, "unit": "mol%"}),)),
    ],
    conditions=(("temperature", {"number": 28, "unit": "°C"}), ("reaction_time", None)),
    outcomes=(("c_c_bond_migration", "not observed"), ("yield", None)),
    notes=("Cited condition-control result summarized with Scheme 4.",),
    unresolved=("Time, recovery/yield, scale, and operational details are not reported.",),
))
records.append(record(
    "scheme4_base_heat_migration", "literature_example", [T3, I3],
    [
        ("e3", "reactant", "ethyl 6-phenylhex-5-yn-2(E)-enoate (E-3)", [T3, I3], None, ()),
        ("base_or_heat", "unspecified_agent", "base or heat", [T3, I3], None, ()),
        ("product4", "product", "C=C-migrated enyne product 4", [T3, I3], None, ()),
    ],
    conditions=(("temperature", None), ("reaction_time", None)),
    outcomes=(("c_c_bond_migration", "observed"), ("yield", None)),
    notes=("The prose states that excess zinc reagent and coupling temperature were responsible for C=C migration; Scheme 4 labels this arrow only as base or heat.",),
    unresolved=("Base identity, temperature, time, product stereoisomer distribution, numerical yield, scale, workup, and purification are not reported.",),
))


def scheme5_text_record(suffix, geometry, yield_percent):
    e = [T3, I3]
    return record(
        suffix, "literature_example", e,
        [
            ("alkyne", "reactant", "1-phenylhex-1-yne", e, "1-phenylhex-1-yne", ()),
            ("iodoester", "reactant", f"ethyl ({geometry})-3-iodopropenoate", e, None, ()),
            ("product", "product", "ethyl 4-phenyl-2(E),4,5-nonatrienoate", e, None, ()),
        ],
        outcomes=(("yield", {"number": yield_percent, "unit": "%"}), ("yield_measurement_basis", None), ("selectivity", "same allenic product formed exclusively")),
        notes=("Prose result summarized from the cited coupling study; distinct from Scheme 5's drawn methyl-ester R = CH3/Ph examples.",),
        unresolved=("Catalyst/reagent loadings, time, solvent, scale, yield basis, workup, and purification are not reported for this prose example.",),
    )


records.extend([
    scheme5_text_record("scheme5_z_iodopropenoate", "Z", 73),
    scheme5_text_record("scheme5_e_iodopropenoate", "E", 86),
])


def scheme5_drawn_record(suffix, r_value, yield_percent, time_h):
    e = [T3, I3]
    return record(
        suffix, "literature_example", e,
        [
            ("alkyne", "reactant", "1-phenylhex-1-yne", e, "1-phenylhex-1-yne", ()),
            ("iodoester", "reactant", f"Scheme 5 alkenyl iodide (R = {r_value}, COOCH3)", e, None, ()),
            ("hgcl2", "catalyst", "HgCl2", e, "mercury(II) chloride", (("loading", {"number": 1.5, "unit": "mol%"}),)),
            ("nbuli", "reagent", "n-BuLi", e, "n-butyllithium", ()),
            ("znbr2", "reagent", "ZnBr2", e, "zinc bromide", ()),
            ("pdpph3", "catalyst", "Pd(PPh3)4", e, "tetrakis(triphenylphosphine)palladium(0)", (("loading", {"number": 5, "unit": "mol%"}),)),
            ("product", "product", f"Scheme 5 allenic methyl-ester product (R = {r_value})", e, None, ()),
        ],
        conditions=(("lithiation_temperature", "room temperature"),
                    ("transmetallation_temperature_program", "-78 °C to room temperature"),
                    ("reaction_time", {"number": time_h, "unit": "h"})),
        outcomes=(("yield", {"number": yield_percent, "unit": "%"}), ("yield_measurement_basis", None), ("c_c_configuration", "remained intact")),
        notes=("Drawn Scheme 5 methyl-ester example summarized from cited work.",),
        unresolved=("Exact systematic substrate/product names, coupling temperature, solvent, scale, yield basis, workup, and purification are not reported.",),
    )


records.extend([
    scheme5_drawn_record("scheme5_r_methyl", "CH3", 77, 2.5),
    scheme5_drawn_record("scheme5_r_phenyl", "Ph", 47, 23),
])

# Proposed catalytic rationale spans page-3 prose and page-4 Scheme 6.
records.append(record(
    "scheme6_mechanism", "mechanism", [T3, I3, I4],
    [
        ("organic_halide", "reactant", "R'X", [T3, I4], None, ()),
        ("pd0", "catalyst", "Pd(0)", [T3, I4], None, ()),
        ("organozinc", "reactant", "allenic/propargylic zinc species 5/6", [T3, I4], None, ()),
        ("palladium_intermediates", "unspecified_agent", "proposed palladium intermediates 7/8", [T3, I4], None, ()),
        ("allene_or_alkyne", "product", "allene or alkyne coupling product", [T3, I4], None, ()),
    ],
    outcomes=(("mechanistic_status", "plausible/proposed, not directly observed"),),
    notes=(
        "Oxidative addition gives R'PdX, trapping by isomeric organozinc species gives palladium intermediates, and reductive elimination gives the coupling products.",
        "The account attributes aryl-halide allene formation to rearrangement of propargylic intermediate 8 to allenic intermediate 7; alkenyl-halide regioselectivity depends on alkyne substitution.",
    ),
    unresolved=("The relative contributions of competing organozinc versus palladium isomers are not experimentally resolved in this account.",),
))

# Scheme 7 has two successive, independently sourced stages.
records.append(record(
    "scheme7_complex_mixture", "literature_example", [T3, I4],
    [
        ("bromide", "reactant", "3-phenylpropargyl bromide", [T3, I4], None, ()),
        ("pdpph3", "reagent", "Pd(PPh3)4", [T3, I4], "tetrakis(triphenylphosphine)palladium(0)", ()),
        ("thf", "solvent", "THF", [T3, I4], "tetrahydrofuran", ()),
        ("complex_a", "product", "eta1-propargylic palladium complex A", [T3, I4], None, ()),
        ("complex_b", "product", "eta1-allenylic palladium complex B", [T3, I4], None, ()),
    ],
    conditions=(("temperature", {"number": 25, "unit": "°C"}), ("reaction_time", None)),
    outcomes=(("A_to_B_ratio", "1.7:1"), ("yield", None)),
    notes=("Cited literature preparation/mixture from reference 8; the ratio is stated in the page-3 prose.",),
    unresolved=("Reaction time, scale, reagent stoichiometry, yield, workup, purification, and direct ratio measurement details are not reported here.",),
))
records.append(record(
    "scheme7_zinc_coupling", "literature_example", [T3, I4],
    [
        ("complex_mix", "reactant", "palladium complexes A + B (A/B = 1.7:1)", [T3, I4], None, ()),
        ("vinylzinc", "reactant", "ethoxycarbonyl ethenyl zinc iodide", [T3, I4], None, ()),
        ("thf", "solvent", "THF", [T3, I4], "tetrahydrofuran", ()),
        ("product", "product", "ethyl 6-phenylhex-5-yn-2(Z)-enoate", [T3, I4], None, ()),
    ],
    conditions=(("temperature", "room temperature"), ("reaction_time", {"number": 1, "unit": "h"})),
    outcomes=(("yield", {"number": 57, "unit": "%"}), ("yield_measurement_basis", None), ("selectivity", "alkynic product exclusively")),
    notes=("Scheme 7's second stage is attributed to reference 9, listed as 'To be published'.",),
    unresolved=("Scale, stoichiometry, yield basis, workup, purification, and isolated mass are not reported.",),
))


by_page = {
    1: [r["record_id"] for r in records if r["source_reaction_id"] in {
        "intro_benzylation_ref3", "intro_allylation_ref4", "scheme1_pathways"
    }],
    2: [r["record_id"] for r in records if r["source_reaction_id"].startswith("scheme2_") or r["source_reaction_id"].startswith("scheme3_")],
    3: [r["record_id"] for r in records if r["source_reaction_id"].startswith("scheme4_") or r["source_reaction_id"].startswith("scheme5_") or r["source_reaction_id"].startswith("scheme6_") or r["source_reaction_id"].startswith("scheme7_")],
    4: [r["record_id"] for r in records if r["source_reaction_id"].startswith("scheme6_") or r["source_reaction_id"].startswith("scheme7_")],
    5: [f"{DOC}:scheme2_aryl_coupling_family"],
}

coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1,
            "state": "attempted",
            "regions": [
                {"region": "title/abstract and introduction prose", "finding": "Abstract and introduction define Pd-catalyzed allene/alkyne coupling scope; cited benzylation and allylation summaries were classified as prior literature.", "evidence_ids": [T1, I1]},
                {"region": "Scheme 1", "finding": "Generic Pathway I allene versus Pathway II alkyne map; not an individual experiment.", "evidence_ids": [I1, T1]},
                {"region": "lower introduction and conference footnote", "finding": "States that this personal account summarizes prior results and identifies the conference presentation; no additional current experimental run.", "evidence_ids": [T1, I1]},
            ],
            "record_ids": by_page[1],
            "unresolved": ["No numerical details or procedures are given for the cited benzylation/allylation families."],
        },
        {
            "page": 2,
            "state": "attempted",
            "regions": [
                {"region": "Scheme 2 and aryl-halide discussion", "finding": "Generic cited aryl-halide coupling family; no per-substrate aryl-halide rows or numerical yields.", "evidence_ids": [I2, T2]},
                {"region": "Scheme 3 top two arrows", "finding": "Two <5% E-alkenyl-iodide cases and two alpha-halostyrene allene-forming cases were split by substrate/halide.", "evidence_ids": [I2, T2]},
                {"region": "Scheme 3 lower two arrows", "finding": "Z-I/Br/Cl and E-I ethyl 3-halopropenoate cases were split by halide/geometry; 0% chloride retained.", "evidence_ids": [I2, T2]},
                {"region": "nitrile prose above Scheme 3", "finding": "Prose-only (Z)-3-iodopropenitrile coupling retained with missing numerical yield and time.", "evidence_ids": [T2, I2]},
            ],
            "record_ids": by_page[2],
            "unresolved": ["Yield measurement bases, reaction scales, solvents, workups, and purification are absent."],
        },
        {
            "page": 3,
            "state": "attempted",
            "regions": [
                {"region": "Scheme 4", "finding": "No-migration control and base/heat migration arrow were kept as distinct cited examples.", "evidence_ids": [I3, T3]},
                {"region": "Scheme 5 and preceding prose", "finding": "Two prose ethyl-(Z/E)-iodopropenoate results and two drawn methyl-ester R=CH3/Ph results were retained separately.", "evidence_ids": [I3, T3]},
                {"region": "mechanism discussion", "finding": "Plausible palladium/organozinc rationale linked forward to Scheme 6; not an observed experiment.", "evidence_ids": [T3, I3]},
                {"region": "Scheme 7 lead-in prose", "finding": "A/B complex mixture and subsequent zinc coupling identified as successive, separately sourced stages.", "evidence_ids": [T3, I3]},
            ],
            "record_ids": by_page[3],
            "unresolved": ["Scheme 4 base identity and exact migration conditions are unspecified; many Scheme 5 operating details and all yield bases are missing."],
        },
        {
            "page": 4,
            "state": "attempted",
            "regions": [
                {"region": "Scheme 6", "finding": "Proposed catalytic/regioselectivity mechanism; intermediates 5-8 were not treated as observed experiments.", "evidence_ids": [I4, T3]},
                {"region": "Scheme 7 first arrow", "finding": "Literature preparation of palladium complexes A/B from 3-phenylpropargyl bromide.", "evidence_ids": [I4, T3]},
                {"region": "Scheme 7 second arrow", "finding": "A/B mixture coupling with ethoxycarbonyl ethenyl zinc iodide gives alkynic product, 57%, exclusively.", "evidence_ids": [I4, T3]},
                {"region": "conclusion, acknowledgments, references 1-6", "finding": "No additional experimental arrow or procedure; bibliography only.", "evidence_ids": [T4, I4]},
            ],
            "record_ids": by_page[4],
            "unresolved": ["Scheme 7 lacks scale, stoichiometry, yield basis, workup, and purification."],
        },
        {
            "page": 5,
            "state": "attempted",
            "regions": [
                {"region": "reference footnote 7", "finding": "Procedure-A note says 1-phenylprop-1-yne afforded a mixture of allenic and propargylic zinc reagents; linked to the Scheme 2 family record rather than duplicated.", "evidence_ids": [T5, I5]},
                {"region": "references 8-9 and remaining blank area", "finding": "Bibliographic continuation only; no additional reaction arrow or procedure.", "evidence_ids": [T5, I5]},
            ],
            "record_ids": by_page[5],
            "unresolved": ["Procedure A is only cross-referenced to reference 5; full conditions and mixture ratio are unavailable in this account."],
        },
    ],
}


def write(path: Path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n")


write(RUN / "raw_model" / "records_pages_0001_0005.json", records)
write(RUN / "coverage" / "pages_0001_0005.json", coverage)

tasks_path = RUN / "tasks.json"
tasks = json.loads(tasks_path.read_text())
for task in tasks:
    if task.get("document_id") == DOC and task.get("evidence_id") in {T1, T2, T3, T4, T5}:
        task["state"] = "attempted"
        task["reason"] = "Original page image and text inspected; findings mapped in coverage/pages_0001_0005.json."
write(tasks_path, tasks)

print(json.dumps({"records": len(records), "coverage_pages": [p["page"] for p in coverage["pages"]]}, ensure_ascii=False))
