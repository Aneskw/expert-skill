#!/usr/bin/env python3
"""Build evidence-linked reaction records for ja0035553, original PDF pages 1-2."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / "runs/current"
DOC = "doc_55d8d908f1901512"
P1 = [f"{DOC}:page1:text", f"{DOC}:page1:image"]
P2 = [f"{DOC}:page2:text", f"{DOC}:page2:image"]


def fact(value, evidence):
    return {
        "value": value,
        "evidence_ids": list(evidence) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def field(name, value, evidence):
    return {"name": name, "fact": fact(value, evidence)}


def participant(entity_id, role, label, evidence, *, name=None, amounts=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence),
        "smiles": fact(None, evidence),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": [field(n, v, evidence) for n, v in (amounts or [])],
    }


def common_missing(evidence, *, yield_basis=True):
    conditions = [
        field("reaction_scale", None, evidence),
        field("atmosphere", None, evidence),
        field("concentration", None, evidence),
        field("workup", None, evidence),
        field("purification", None, evidence),
    ]
    outcomes = [field("yield_measurement_basis", None, evidence)] if yield_basis else []
    return conditions, outcomes


def record(suffix, kind, evidence, participants, conditions, outcomes, notes=None, unresolved=None):
    return {
        "record_id": f"{DOC}:{suffix}",
        "document_id": DOC,
        "source_reaction_id": suffix,
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
        "notes": [fact(v, evidence) for v in (notes or [])],
        "review": {
            "method": "model",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved or [],
        },
    }


def standard_unresolved(*extra):
    return [
        "Structures are conveyed by drawings or compact substituent labels; SMILES remain unverified and null.",
        "Reaction scale, atmosphere, concentration, workup, purification, and yield basis are not reported in the supplied main text.",
        "The article advertises Supporting Information, but no SI file is supplied or explicitly associated in this pilot.",
        *extra,
    ]


records = []

# Scheme 1: generic regiochemical/stereochemical problem statement, not an individual run.
cm, _ = common_missing(P1, yield_basis=False)
records.append(record(
    "scheme1_general", "general_scheme", P1,
    [
        participant("allenol", "reactant", "generic 1-substituted 2,3-allenol", P1),
        participant("organopalladium", "reagent", "R2PdI", P1),
        participant("nucleophile", "reagent", "NuH = R3R4NH", P1),
        participant("alpha_product", "product", "generic alpha-amino alkenol (path a)", P1),
        participant("gamma_product", "product", "generic gamma-amino alkenol (path b)", P1),
    ],
    cm, [],
    notes=["Scheme 1 is a generic selectivity map and does not report an individual yield."],
    unresolved=standard_unresolved("Generic R groups and the depicted organopalladium species are not complete structures."),
))


def table1_record(entry, substrate_label, ar, aryl_label, amine_label, temp, time_h, product, yield_pct,
                  amine_equiv=None, solvent="Et3N", extra_notes=None, extra_outcomes=None, extra_unresolved=None):
    ev = P1
    ps = [
        participant("substrate", "reactant", substrate_label, ev,
                    name=f"1-aryl-2,3-allenol 1 (Ar = {ar})"),
        participant("aryl_iodide", "reactant", aryl_label, ev,
                    name=f"aryl iodide 2 (R2 = {aryl_label})"),
        participant("amine", "reagent", amine_label, ev,
                    amounts=([("equivalents", {"number": amine_equiv, "unit": "equiv"})]
                             if amine_equiv is not None else [])),
        participant("catalyst", "catalyst", "Pd(PPh3)4", ev,
                    amounts=[("catalyst_loading", {"number": 5, "unit": "mol%"})]),
        participant("solvent", "solvent", solvent, ev),
        participant("product", "product", product, ev,
                    name="2-amino-3-alken-1-ol product 4"),
    ]
    missing_conditions, missing_outcomes = common_missing(ev)
    cond = [
        field("temperature", temp if temp == "reflux" else {"number": temp, "unit": "°C"}, ev),
        field("time", {"number": time_h, "unit": "h"}, ev),
        *missing_conditions,
    ]
    outs = [field("yield", {"number": yield_pct, "unit": "%"}, ev), *missing_outcomes]
    outs.extend(extra_outcomes or [])
    return record(
        f"table1_entry{entry}", "substrate_scope_entry", ev, ps, cond, outs,
        notes=[f"Table 1 entry {entry}.", *(extra_notes or [])],
        unresolved=standard_unresolved(*(extra_unresolved or [])),
    )


table1_rows = [
    (1, "1a", "Ph", "Ph", "Et2NH", "reflux", 50, "4a", 82, None, "Et2NH"),
    (2, "1a", "Ph", "Ph", "Et2NH", "reflux", 46, "4a", 79, 2, "Et3N"),
    (3, "1a", "Ph", "Ph", "n-BuNH2", 77, 47, "4b", 66, 11, "Et3N"),
    (4, "1a", "Ph", "Ph", "n-BuNH2", 77, 46, "4b", 78, 1.5, "Et3N"),
    (5, "1a", "Ph", "Ph", "BnNH2", 70, 72, "4c", 63, 1.5, "Et3N"),
    (6, "1a", "Ph", "p-Me-C6H4", "BnNH2", 70, 72, "4d", 67, 1.5, "Et3N"),
    (7, "1a", "Ph", "p-Me-C6H4", "n-BuNH2", 70, 72, "4e", 44, 1.5, "Et3N"),
    (8, "1b", "p-MeO-C6H4", "Ph", "n-BuNH2", 75, 69, "4f", 53, 1.5, "Et3N"),
    (9, "1c", "o-CF3-C6H4", "Ph", "n-BuNH2", 75, 66, "4g", 85, 1.5, "Et3N"),
]
for row in table1_rows:
    extra_outcomes = []
    extra_notes = []
    extra_unresolved = []
    if row[0] == 1:
        extra_notes.append("Footnote a replaces Et3N solvent with Et2NH; no amine equivalent is assigned.")
    if row[0] == 4:
        extra_outcomes.append(field("regio_and_stereoselectivity_observation", "Only 4b was observed in the crude 1H NMR spectrum; relative configuration assigned as (1R*,2S*) after derivatization to 6b.", P1))
        extra_unresolved.append("The prose does not explicitly state whether the 'only 4b' observation also applies to Table 1 entry 3.")
    records.append(table1_record(*row, extra_notes=extra_notes, extra_outcomes=extra_outcomes,
                                 extra_unresolved=extra_unresolved))

# Equation 1: derivatization used for relative-configuration assignment.
cm, co = common_missing(P1)
records.append(record(
    "eq1_4b_to_6b", "reported_experiment", P1,
    [
        participant("starting_material", "reactant", "4b", P1,
                    name="2-(n-butylamino)-1,3-diphenyl-3-butenol 4b"),
        participant("triphosgene", "reagent", "triphosgene", P1),
        participant("sodium_hydroxide", "reagent", "aqueous NaOH", P1,
                    amounts=[("concentration", {"number": 2, "unit": "N"})]),
        participant("thf", "solvent", "THF", P1),
        participant("product", "product", "6b", P1,
                    name="cyclic carbamate derivative 6b"),
    ],
    [field("temperature", "room temperature", P1), field("time", "overnight", P1), *cm],
    [field("yield", {"number": 71, "unit": "%"}, P1),
     field("NOE_relative_configuration_assignment", "NOE of 6b supports (1R*,2S*) for 4b", P1), *co],
    notes=["Equation (1) is a derivatization experiment used to assign the relative configuration of 4b."],
    unresolved=standard_unresolved("The exact identity/name and absolute stereochemistry of 6b are not fully specified in text."),
))

# Equation 2: protected allenol analogue.
cm, co = common_missing(P2)
records.append(record(
    "eq2_1a_prime_to_7", "reported_experiment", P2,
    [
        participant("substrate", "reactant", "1a'", P2,
                    name="1-phenyl-2,3-propadienyl methyl ether"),
        participant("ph_i", "reactant", "PhI", P2),
        participant("benzylamine", "reagent", "BnNH2", P2,
                    amounts=[("equivalents", {"number": 1.5, "unit": "equiv"})]),
        participant("catalyst", "catalyst", "Pd(PPh3)4", P2,
                    amounts=[("catalyst_loading", {"number": 5, "unit": "mol%"})]),
        participant("solvent", "solvent", "Et3N", P2),
        participant("product", "product", "7", P2,
                    name="alpha-aminomethoxide product 7"),
    ],
    [field("temperature", {"number": 74, "unit": "°C"}, P2),
     field("time", {"number": 47, "unit": "h"}, P2), *cm],
    [field("yield", {"number": 83, "unit": "%"}, P2),
     field("selectivity", "high regio- and stereoselectivity", P2), *co],
    notes=["Equation (2) tests the methyl-ether analogue of allenol 1a."],
    unresolved=standard_unresolved("No numerical regio- or stereoselectivity ratio is reported."),
))


def chiral_record(suffix, evidence, substrate_label, substrate_ee, aryl_label, product, temp, time_h,
                  yield_pct, product_ee, family):
    cm, co = common_missing(evidence)
    ps = [
        participant("substrate", "reactant", substrate_label, evidence,
                    amounts=[("starting_material_ee", {"number": substrate_ee, "unit": "%"})]),
        participant("aryl_iodide", "reactant", aryl_label, evidence),
        participant("benzylamine", "reagent", "BnNH2", evidence),
        participant("catalyst", "catalyst", "Pd(PPh3)4", evidence,
                    amounts=[("catalyst_loading", {"number": 5, "unit": "mol%"})]),
        participant("solvent", "solvent", "Et3N", evidence),
        participant("product", "product", product, evidence,
                    name=family),
    ]
    return record(
        suffix, "reported_experiment", evidence, ps,
        [field("temperature", {"number": temp, "unit": "°C"}, evidence),
         field("time", {"number": time_h, "unit": "h"}, evidence), *cm],
        [field("yield", {"number": yield_pct, "unit": "%"}, evidence),
         field("product_ee", {"number": product_ee, "unit": "%"}, evidence), *co],
        notes=["Product ee was determined by HPLC with a CHIRALPAK OD or AS column according to footnote 12."],
        unresolved=standard_unresolved("The exact amine amount and HPLC column used for this individual product are not specified."),
    )


records.append(chiral_record("scheme2_4c_chiral", P2, "(R)-1a", 98, "PhI", "4c", 70, 42, 57, 98,
                              "optically enriched 2-amino alcohol 4c"))
records.append(chiral_record("scheme2_4d_chiral", P2, "(R)-1a", 98, "4-Me-PhI", "4d", 74, 44, 65, 97,
                              "optically enriched 2-amino alcohol 4d"))


def table2_record(entry, substrate, r1, aryl, amine, temp, time_h, product, yield_pct):
    ev = P2
    ps = [
        participant("substrate", "reactant", substrate, ev,
                    name=f"1-substituted 2,3-allenol 1 (R1 = {r1})"),
        participant("aryl_iodide", "reactant", aryl, ev,
                    name=f"aryl iodide 2 (R2 = {aryl})"),
        participant("amine", "reagent", amine, ev,
                    amounts=[("equivalents", {"number": 1.5, "unit": "equiv"})]),
        participant("catalyst", "catalyst", "Pd(PPh3)4", ev,
                    amounts=[("catalyst_loading", {"number": 5, "unit": "mol%"})]),
        participant("solvent", "solvent", "Et3N", ev),
        participant("product", "product", product, ev,
                    name="4-amino-2(E)-alken-1-ol product 5"),
    ]
    cm, co = common_missing(ev)
    return record(
        f"table2_entry{entry}", "substrate_scope_entry", ev, ps,
        [field("temperature", {"number": temp, "unit": "°C"}, ev),
         field("time", {"number": time_h, "unit": "h"}, ev), *cm],
        [field("yield", {"number": yield_pct, "unit": "%"}, ev),
         field("alkene_configuration", "E", ev), *co],
        notes=[f"Table 2 entry {entry}; the E assignment for products 5 is supported by the NOE experiment of 5b (footnote 15)."],
        unresolved=standard_unresolved("No numerical stereoselectivity ratio is reported."),
    )


table2_rows = [
    (1, "1e", "n-C4H9", "PhI", "BnNH2", 77, 45, "5b", 92),
    (2, "1f", "n-C8H17", "PhI", "BnNH2", 70, 72, "5c", 72),
    (3, "1f", "n-C8H17", "PhI", "n-BuNH2", 70, 72, "5d", 57),
    (4, "1f", "n-C8H17", "p-Me-C6H4I", "BnNH2", 70, 72, "5e", 78),
    (5, "1g", "cyclohexyl", "PhI", "BnNH2", 74, 47, "5f", 45),
    (6, "1h", "E-1-propenyl", "PhI", "BnNH2", 75, 67, "5g", 58),
]
for row in table2_rows:
    records.append(table2_record(*row))

# Equation 3: perfluoroalkyl-substituted substrate.
cm, co = common_missing(P2)
records.append(record(
    "eq3_1j_to_5i", "reported_experiment", P2,
    [
        participant("substrate", "reactant", "1j", P2,
                    name="C8F17-substituted 2,3-allenol 1j"),
        participant("ph_i", "reactant", "PhI", P2),
        participant("benzylamine", "reagent", "BnNH2", P2,
                    amounts=[("equivalents", {"number": 1.5, "unit": "equiv"})]),
        participant("catalyst", "catalyst", "Pd(PPh3)4", P2,
                    amounts=[("catalyst_loading", {"number": 5, "unit": "mol%"})]),
        participant("solvent", "solvent", "Et3N", P2),
        participant("product", "product", "5i", P2,
                    name="gamma-amino alcohol 5i"),
    ],
    [field("temperature", {"number": 77, "unit": "°C"}, P2),
     field("time", {"number": 36, "unit": "h"}, P2), *cm],
    [field("yield", {"number": 87, "unit": "%"}, P2),
     field("regioselectivity", "same gamma regioselectivity as the alkyl-substituted series", P2), *co],
    notes=["Equation (3) probes replacement of C8H17 by electron-withdrawing C8F17."],
    unresolved=standard_unresolved("No numerical regio- or stereoselectivity ratio is reported."),
))

records.append(chiral_record("scheme3_5c_chiral", P2, "(S)-1f", 97, "PhI", "(S)-5c", 74, 44, 58, 96,
                              "optically enriched 4-amino-2(E)-alken-1-ol (S)-5c"))
records.append(chiral_record("scheme3_5e_chiral", P2, "(S)-1f", 97, "p-Me-PhI", "(S)-5e", 74, 44, 63, 96,
                              "optically enriched 4-amino-2(E)-alken-1-ol (S)-5e"))

# Scheme 4: proposed rationale, not an observed reaction.
cm, _ = common_missing(P2, yield_basis=False)
records.append(record(
    "scheme4_regioselectivity_mechanism", "mechanism", P2,
    [
        participant("intermediate8", "unspecified_agent", "proposed pi-allylpalladium intermediate 8", P2),
        participant("amine", "reagent", "R3R4NH", P2),
        participant("alpha_path", "product", "generic alpha-amino product 4 or 7 (path a)", P2),
        participant("gamma_path", "product", "generic gamma-amino product 5 (path b)", P2),
    ],
    cm, [],
    notes=[
        "Scheme 4 is a proposed steric/stereoelectronic rationale, not an observed experimental run.",
        "For R2 = aryl, alpha selectivity is proposed; for R2 = alkyl or alkenyl, gamma selectivity is proposed.",
    ],
    unresolved=standard_unresolved("The paper states that the mechanism is not clear; proposed intermediate 8 is not reported as observed."),
))

assert len(records) == 24
raw_path = RUN / "raw_model/records_pages_0001_0002.json"
raw_path.parent.mkdir(parents=True, exist_ok=True)
raw_path.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")

page1_ids = [r["record_id"] for r in records if r["source_reaction_id"] in {
    "scheme1_general", "eq1_4b_to_6b", *(f"table1_entry{i}" for i in range(1, 10))
}]
page2_ids = [r["record_id"] for r in records if r["record_id"] not in page1_ids]

coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1,
            "state": "attempted",
            "regions": [
                {"region": "upper-right Scheme 1", "finding": "Generic regio-/stereoselectivity map; classified as a general scheme, not an individual experiment.", "evidence_ids": P1},
                {"region": "middle-right Table 1 and footnotes", "finding": "Nine Pd(0)-catalyzed 1-aryl-2,3-allenol scope rows extracted separately; solvent and amine-equivalent footnotes applied row by row.", "evidence_ids": P1},
                {"region": "lower-right equation (1) and adjacent prose", "finding": "4b-to-6b derivatization extracted once and linked to the (1R*,2S*) relative-configuration assignment; not duplicated as a Table 1 run.", "evidence_ids": P1},
                {"region": "left column introduction and references", "finding": "Background and cited prior work only; no additional current-paper experiment fabricated.", "evidence_ids": P1},
            ],
            "record_ids": page1_ids,
            "unresolved": [
                "No SI file is supplied despite the article's SI notice on page 2.",
                "Most structures are drawing-based; all SMILES remain null and unverified.",
                "The exact scope of the prose statement that only 4b formed is not explicit for both Table 1 entries 3 and 4.",
            ],
        },
        {
            "page": 2,
            "state": "attempted",
            "regions": [
                {"region": "upper-left equation (2) and Scheme 2", "finding": "One methyl-ether experiment and two distinct enantioenriched allenol experiments extracted; their different times/yields prevent merging with Table 1.", "evidence_ids": P2},
                {"region": "middle-left Table 2 and footnotes", "finding": "Six 1-alkyl/alkenyl-2,3-allenol scope rows extracted separately, including E-configuration evidence from the 5b NOE statement.", "evidence_ids": P2},
                {"region": "upper-right equation (3) and Scheme 3", "finding": "One perfluoroalkyl experiment and two enantioenriched preparations extracted; repeated product labels were not merged across different conditions.", "evidence_ids": P2},
                {"region": "middle-right Scheme 4 and rationale prose", "finding": "Proposed pi-allylpalladium regioselectivity rationale classified as mechanism, not an observed experiment.", "evidence_ids": P2},
                {"region": "bottom columns, conclusion, references, and SI notice", "finding": "No additional current-paper runs; SI is advertised but absent from the supplied pilot.", "evidence_ids": P2},
            ],
            "record_ids": page2_ids,
            "unresolved": [
                "No numerical regio-/stereoselectivity ratios are reported for most claims.",
                "Yield bases, scales, atmosphere, concentration, workup, purification, and isolated masses are absent from the main text.",
                "The individual CHIRALPAK column assignment for each ee value is not specified.",
                "No SI association is inferred.",
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
    if task.get("document_id") == DOC and task.get("evidence_id") in {P1[0], P2[0]}:
        task["state"] = "attempted"
        task["visual_evidence_id"] = P1[1] if task["evidence_id"] == P1[0] else P2[1]
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"records": len(records), "raw": str(raw_path), "coverage": str(coverage_path)}, ensure_ascii=False))
