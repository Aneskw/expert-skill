#!/usr/bin/env python3
"""Build evidence-linked records for ol006504j, original PDF pages 1-3."""
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / "runs" / "current"
DOC = "doc_486ee2ff11ca63ca"
E = {
    1: [f"{DOC}:page1:image", f"{DOC}:page1:text"],
    2: [f"{DOC}:page2:image", f"{DOC}:page2:text"],
    3: [f"{DOC}:page3:image", f"{DOC}:page3:text"],
}


def fact(value, evidence=()):
    return {
        "value": value,
        "evidence_ids": list(dict.fromkeys(evidence)) if value is not None else [],
        "verification": "source_checked" if value is not None else "missing",
    }


def field(name, value, evidence):
    return {"name": name, "fact": fact(value, evidence)}


def participant(entity_id, role, label, name, evidence):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence),
        "smiles": fact(None),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": [],
    }


def record(suffix, kind, evidence, participants, conditions=(), outcomes=(), notes=(), unresolved=()):
    evidence = list(dict.fromkeys(evidence))
    return {
        "record_id": f"{DOC}:{suffix}",
        "document_id": DOC,
        "source_reaction_id": suffix,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": evidence,
        "participants": participants,
        "steps": [{
            "step_id": "step1",
            "participant_ids": [p["entity_id"] for p in participants],
            "conditions": [field(n, v, ev) for n, v, ev in conditions],
        }] if conditions or participants else [],
        "outcomes": [field(n, v, ev) for n, v, ev in outcomes],
        "notes": [fact(v, ev) for v, ev in notes],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": list(unresolved),
        },
    }


def substrate(label, descriptor, evidence):
    return participant(f"substrate_{label}", "reactant", label, descriptor, evidence)


def product(label, descriptor, evidence):
    return participant(f"product_{label}", "product", label, descriptor, evidence)


def reagent(entity_id, label, name, evidence):
    return participant(entity_id, "reagent", label, name, evidence)


records = []

# Page 1: a generic current-paper transformation, not an individual run.
records.append(record(
    "graphical_abstract_general", "general_scheme", E[1],
    [
        substrate("generic_1", "generic 2,3-allenamide with R1-R4 substituents", E[1]),
        reagent("reagent_cux2", "CuX2", "copper(II) chloride or copper(II) bromide", E[1]),
        product("generic_2_or_3", "4-halo pyrrol-2(5H)-one family; hydroxylated when R2=H", E[1]),
    ],
    outcomes=[("scope_rule", "R2 = H gives R5 = OH; R2 != H gives R5 = R2", E[1])],
    notes=[("The graphical abstract summarizes the current transformation and is not a row-level experiment.", E[1])],
    unresolved=["Generic R groups do not define complete structures.", "No row-specific quantities, time, temperature, workup, or yield is stated in this generic scheme."],
))

# Page 2 Scheme 2 is the authors' conceptual plan, not an observed experiment.
records.append(record(
    "scheme2_conceptual_sequence", "general_scheme", E[2],
    [
        substrate("scheme2_allenamide", "generic 2,3-dienamide", E[2]),
        participant("scheme2_pyrrolone", "unspecified_agent", "generic pyrrol-2(5H)-one", "conceptual cyclization intermediate", E[2]),
        product("scheme2_hydroxypyrrolone", "generic 5-hydroxypyrrol-2(5H)-one", E[2]),
    ],
    notes=[("Scheme 2 uses question-mark arrows to present the envisioned lactamization-hydroxylation sequence.", E[2])],
    unresolved=["The scheme is conceptual and supplies no reagent, yield, or observed intermediate.", "Generic R groups do not define complete structures."],
))


table1 = [
    # entry, solvent, time h, yield, base, recovered, CuBr2 equiv
    (1, "H2O", 22, 10, None, 68, 1.1),
    (2, "THF-H2O (1:1)", 22, 38, "Et3N (1 equiv)", 43, 1.1),
    (3, "THF-H2O (1:1)", 17.5, None, "K2CO3 (1 equiv)", None, 1.1),
    (4, "DMF", 19, 60, None, None, 1.1),
    (5, "acetone-H2O (3:2)", 19, 70, None, None, 1.1),
    (6, "THF-H2O (1:1)", 16, 65, None, None, 2.0),
    (7, "THF-H2O (1:1)", 18.5, 72, None, None, 1.1),
]
for entry, solvent, hours, yld, base, recovered, cbr_equiv in table1:
    ev = E[2]
    ps = [
        substrate("1a", "N-benzyl 2-methyl-2,3-decadienamide", ev),
        reagent("cubr2", "CuBr2", "copper(II) bromide", ev),
    ]
    if entry != 3:
        ps.append(product("2a", "bromolactamization-hydroxylation product 2a", ev))
    if base:
        ps.append(reagent(f"base_entry{entry}", base.split()[0], base, ev))
    conditions = [
        ("solvent", solvent, ev),
        ("reaction_time", {"number": hours, "unit": "h"}, ev),
        ("CuBr2_equivalents", {"number": cbr_equiv, "unit": "equiv"}, ev),
        ("temperature", {"number": 50, "unit": "°C"} if entry == 7 else None, ev),
    ]
    outcomes = []
    if yld is not None:
        outcomes.append(("reported_yield_of_2a", {"number": yld, "unit": "%"}, ev))
    else:
        outcomes.append(("reaction_result", "No reaction", ev))
    outcomes.append(("recovered_1a", {"number": recovered, "unit": "%"} if recovered is not None else None, ev))
    outcomes.append(("yield_measurement_basis", None, ev))
    notes = []
    if entry == 7:
        notes.append(("This is the same 1a-to-2a experiment shown in Equation (1) and Table 2 entry 1; the evidence is merged rather than duplicated.", ev))
        notes.append(("The normal bromolactamization product 3a was expected but the one-shot hydroxylated product 2a was obtained.", ev))
    records.append(record(
        f"table1_entry{entry}", "optimization_entry", ev, ps, conditions, outcomes, notes,
        ["Yield measurement basis is not stated in the supplied main text.", "Reaction scale, atmosphere, concentration, workup, purification, and isolated mass are unavailable without the unsupplied SI."] + ([] if entry == 7 else ["Temperature is not stated for this Table 1 row."]),
    ))


table2 = [
    # entry, substrate, descriptor, X, equiv, solvent, temp, time value/unit, yield, product
    (2, "1a", "N-benzyl 2-methyl-2,3-decadienamide", "Cl", 1.1, "THF-H2O (1:1)", "reflux", 21, "h", 57, "2b"),
    (3, "1b", "2,3-allenamide 1b (R1=H, R2=Me, R3=Bn)", "Br", 2.0, "EtOH-H2O (3:2)", 50, 19, "h", 78, "2c"),
    (4, "1b", "2,3-allenamide 1b (R1=H, R2=Me, R3=Bn)", "Cl", 2.0, "EtOH-H2O (3:2)", 50, 22, "h", 60, "2d"),
    (5, "1c", "2,3-allenamide 1c (R1=Ph, R2=Me, R3=n-C4H9)", "Br", 2.0, "THF-H2O (1:1)", "reflux", 24, "h", 94, "2e"),
    (6, "1c", "2,3-allenamide 1c (R1=Ph, R2=Me, R3=n-C4H9)", "Cl", 4.0, "THF-H2O (1:1)", "reflux", 5, "d", 71, "2f"),
    (7, "1d", "2,3-allenamide 1d (R1=n-C7H15, R2=H, R3=H)", "Br", 1.1, "THF-H2O (1:1)", 50, 22, "h", 69, "2g"),
    (8, "1e", "2,3-allenamide 1e (R1=n-C7H15, R2=H, R3=Bn)", "Br", 1.1, "THF-H2O (1:1)", 50, 32, "h", 78, "2h"),
    (9, "1e", "2,3-allenamide 1e (R1=n-C7H15, R2=H, R3=Bn)", "Cl", 2.0, "THF-H2O (1:1)", 50, 3, "d", 78, "2i"),
]
for entry, slabel, sdesc, x, equiv, solvent, temp, tnum, tunit, yld, plabel in table2:
    ev = E[2]
    copper = "CuBr2" if x == "Br" else "CuCl2"
    records.append(record(
        f"table2_entry{entry}", "substrate_scope_entry", ev,
        [substrate(slabel, sdesc, ev), reagent("cux2", copper, "copper(II) bromide" if x == "Br" else "copper(II) chloride", ev), product(plabel, f"{x.lower()}-halolactamization-hydroxylation product {plabel}", ev)],
        [
            ("solvent", solvent, ev),
            ("CuX2_equivalents", {"number": equiv, "unit": "equiv"}, ev),
            ("temperature", temp if isinstance(temp, str) else {"number": temp, "unit": "°C"}, ev),
            ("reaction_time", {"number": tnum, "unit": tunit}, ev),
        ],
        [("reported_yield", {"number": yld, "unit": "%"}, ev), ("yield_measurement_basis", None, ev)],
        unresolved=["Yield measurement basis is not stated in the supplied main text.", "Reaction scale, atmosphere, concentration, workup, purification, and isolated mass are unavailable without the unsupplied SI."],
    ))

# Table 2 footnote reports a materially different, extra 1b condition.
records.append(record(
    "table2_footnote_1b_cubr2_thf", "optimization_entry", E[2],
    [
        substrate("1b", "2,3-allenamide 1b (R1=H, R2=Me, R3=Bn)", E[2]),
        reagent("cubr2", "CuBr2", "copper(II) bromide", E[2]),
        product("2c", "bromolactamization-hydroxylation product 2c", E[2]),
    ],
    [
        ("solvent", "THF-H2O (1:1)", E[2]),
        ("CuBr2_equivalents", {"number": 1.1, "unit": "equiv"}, E[2]),
        ("temperature", None, E[2]),
        ("reaction_time", None, E[2]),
    ],
    [("reported_yield_of_2c", {"number": 48, "unit": "%"}, E[2]), ("yield_measurement_basis", None, E[2])],
    notes=[("This is the alternative condition reported in Table 2 footnote a, not Table 2 entry 3 itself.", E[2])],
    unresolved=["Temperature, reaction time, yield basis, scale, atmosphere, concentration, workup, purification, and isolated mass are not stated for this footnote experiment."],
))

# Proposed pathway is kept separate from observed runs.
records.append(record(
    "proposed_cu2_oxidation_pathway", "mechanism", E[2] + E[3],
    [
        participant("intermediate_3", "unspecified_agent", "3", "4-halopyrrol-2(5H)-one proposed intermediate", E[2] + E[3]),
        product("2", "4-halo-5-hydroxypyrrol-2(5H)-one product family", E[2] + E[3]),
        reagent("cu2plus", "Cu2+", "copper(II) oxidant", E[3]),
    ],
    outcomes=[("mechanistic_status", "Proposed Cu2+-mediated oxidation of 3 to 2; intermediate 3 was not reported as observed for the monosubstituted series.", E[3])],
    notes=[("The source uses 'may be formed'; this is a mechanistic proposal rather than an experimental record.", E[3])],
    unresolved=["The intermediate and oxidation sequence are not directly observed in the supplied main text.", "No mechanistic operating conditions are supplied."],
))


# Page 3 Equation (2): two distinct CuX2 experiments on fully substituted 1f.
for x, hours, yld, plabel in [("Cl", 3.5, 80, "3b"), ("Br", 1, 89, "3c")]:
    ev = E[3]
    copper = "CuCl2" if x == "Cl" else "CuBr2"
    records.append(record(
        f"eq2_{copper.lower()}_{plabel}", "reported_experiment", ev,
        [
            substrate("1f", "fully substituted 2,3-allenamide 1f", ev),
            reagent("cux2", copper, "copper(II) chloride" if x == "Cl" else "copper(II) bromide", ev),
            product(plabel, f"4-{x.lower()}-pyrrol-2(5H)-one {plabel}", ev),
        ],
        [
            ("solvent", "THF-H2O (1:1)", ev),
            ("CuX2_equivalents", {"number": 4, "unit": "equiv"}, ev),
            ("temperature", "room temperature", ev),
            ("reaction_time", {"number": hours, "unit": "h"}, ev),
        ],
        [("reported_yield", {"number": yld, "unit": "%"}, ev), ("yield_measurement_basis", None, ev)],
        notes=[("The fully substituted substrate gives the normal halolactamization product without the 5-hydroxyl group.", ev)],
        unresolved=["Yield measurement basis, scale, atmosphere, concentration, workup, purification, and isolated mass are unavailable without the unsupplied SI."],
    ))


coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1,
            "state": "attempted",
            "regions": [
                {"region": "graphical abstract beneath ABSTRACT heading", "finding": "Current generic CuX2 halolactamization/hydroxylation transformation; recorded as a general scheme, not an individual experiment.", "evidence_ids": E[1]},
                {"region": "Scheme 1 and adjacent introductory prose", "finding": "Structures A, A1, and A2 illustrate biological background; cited prior syntheses and bioactivity are not locally reported experiments.", "evidence_ids": E[1]},
            ],
            "record_ids": [f"{DOC}:graphical_abstract_general"],
            "unresolved": ["Generic R-group structures are not fully specified.", "No local experimental procedure occurs on this page."],
        },
        {
            "page": 2,
            "state": "attempted",
            "regions": [
                {"region": "Scheme 2, upper-left", "finding": "Question-mark conceptual lactamization/hydroxylation sequence; classified as a general scheme rather than an observed experiment.", "evidence_ids": E[2]},
                {"region": "Equation (1) and surrounding prose", "finding": "1a/CuBr2 gives hydroxylated 2a rather than expected 3a; merged with Table 1 entry 7 and Table 2 entry 1.", "evidence_ids": E[2]},
                {"region": "Table 1, upper-right", "finding": "Seven bromolactamization-hydroxylation optimization rows, including one explicit no-reaction row and recovered-starting-material footnotes.", "evidence_ids": E[2]},
                {"region": "Table 2, lower-right", "finding": "Nine scope rows; entry 1 duplicates the optimized 1a run, entries 2-9 are separate records, and footnote a adds a separate 48% 1b condition.", "evidence_ids": E[2]},
            ],
            "record_ids": [
                f"{DOC}:scheme2_conceptual_sequence",
                *[f"{DOC}:table1_entry{i}" for i in range(1, 8)],
                *[f"{DOC}:table2_entry{i}" for i in range(2, 10)],
                f"{DOC}:table2_footnote_1b_cubr2_thf",
                f"{DOC}:proposed_cu2_oxidation_pathway",
            ],
            "unresolved": ["The main text does not state yield measurement bases.", "The SI-referenced typical procedure and analytical data are not supplied.", "Most rows omit scale, atmosphere, concentration, workup, purification, and isolated mass."],
        },
        {
            "page": 3,
            "state": "attempted",
            "regions": [
                {"region": "top-left prose and Equation (2)", "finding": "Proposed oxidation pathway for monosubstituted allenamides plus two distinct fully substituted 1f halolactamizations: CuCl2 to 3b and CuBr2 to 3c.", "evidence_ids": E[3]},
                {"region": "Supporting Information notice, upper-right", "finding": "The article advertises a typical procedure and analytical data online, but no SI is supplied or explicitly associated in this pilot.", "evidence_ids": E[3]},
                {"region": "reference 15, upper-right/lower text", "finding": "Cited routes to allenamide starting materials are prior literature and are not expanded into local experiment records.", "evidence_ids": E[3]},
            ],
            "record_ids": [f"{DOC}:proposed_cu2_oxidation_pathway", f"{DOC}:eq2_cucl2_3b", f"{DOC}:eq2_cubr2_3c"],
            "unresolved": ["Equation (2) omits yield bases, scale, atmosphere, concentration, workup, purification, and isolated masses.", "No SI association is inferred from the availability notice."],
        },
    ],
}


assert len(records) == 21
assert [p["page"] for p in coverage["pages"]] == [1, 2, 3]
assert all(p["regions"] for p in coverage["pages"])

(RUN / "raw_model").mkdir(parents=True, exist_ok=True)
(RUN / "coverage").mkdir(parents=True, exist_ok=True)
(RUN / "raw_model" / "records_pages_0001_0003.json").write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
(RUN / "coverage" / "pages_0001_0003.json").write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

tasks_path = RUN / "tasks.json"
tasks = json.loads(tasks_path.read_text())
for task in tasks:
    if task.get("document_id") == DOC and task.get("evidence_id") in {f"{DOC}:page{i}:text" for i in (1, 2, 3)}:
        task["state"] = "attempted"
        task["reason"] = "Original page image and extracted text inspected; reaction regions represented in coverage/pages_0001_0003.json."
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"records": len(records), "coverage_pages": [1, 2, 3]}, ensure_ascii=False))
