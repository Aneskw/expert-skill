#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "runs/current/raw_model/records_pages_0001_0003.json"
COVERAGE = ROOT / "runs/current/coverage/pages_0001_0003.json"
TASKS = ROOT / "runs/current/tasks.json"

DOC = "doc_efd191b32bc3ebd4"
P1T, P1I = f"{DOC}:page1:text", f"{DOC}:page1:image"
P2T, P2I = f"{DOC}:page2:text", f"{DOC}:page2:image"
P3T, P3I = f"{DOC}:page3:text", f"{DOC}:page3:image"


def fact(value, ev):
    return {"value": value, "evidence_ids": list(dict.fromkeys(ev)) if value is not None else [],
            "verification": "unreviewed" if value is not None else "missing"}


def fld(name, value, ev, targets=None):
    x = {"name": name, "fact": fact(value, ev)}
    if targets:
        x["target_entity_ids"] = targets
    return x


def missing_execution_fields():
    """Represent important absent procedure details explicitly."""
    return [
        fld("reaction_scale", None, []),
        fld("atmosphere", None, []),
        fld("workup", None, []),
        fld("purification", None, []),
    ]


def participant(entity_id, role, label, name, ev, smiles=None, amounts=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, ev),
        "name": fact(name, ev),
        "smiles": fact(smiles, ev) if smiles else fact(None, []),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": amounts or [],
    }


def record(rid, kind, ev, participants, conditions, outcomes, notes=None, unresolved=None):
    return {
        "record_id": f"{DOC}:{rid}",
        "document_id": DOC,
        "source_reaction_id": rid,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": list(dict.fromkeys(ev)),
        "participants": participants,
        "steps": [{
            "step_id": "reaction",
            "participant_ids": [p["entity_id"] for p in participants],
            "conditions": conditions,
        }],
        "outcomes": outcomes,
        "notes": [fact(x, ev) for x in (notes or [])],
        "review": {
            "method": "none", "reviewer": None, "checked_fields": [],
            "unresolved": unresolved or [],
        },
    }


def selectfluor(ev, equiv):
    return participant(
        "selectfluor_1", "reagent", "1", "Selectfluor (F-TEDA-BF4)", ev,
        None, [fld("equivalents", {"number": equiv, "unit": "equiv"}, ev)],
    )


def solvent_participants(solvent_text, ev, water_equiv=None):
    parts = []
    if "DMF" in solvent_text:
        parts.append(participant("dmf", "solvent", "DMF", "N,N-dimethylformamide", ev, "CN(C)C=O"))
    if "DMA" in solvent_text:
        parts.append(participant("dma", "solvent", "DMA", "N,N-dimethylacetamide", ev, "CC(=O)N(C)C"))
    if "EtOH" in solvent_text:
        parts.append(participant("ethanol", "solvent", "EtOH", "ethanol", ev, "CCO"))
    if "MeNO2" in solvent_text:
        parts.append(participant("nitromethane", "solvent", "MeNO2", "nitromethane", ev, "C[N+](=O)[O-]"))
    if "MeCN" in solvent_text:
        parts.append(participant("acetonitrile", "solvent", "MeCN", "acetonitrile", ev, "CC#N"))
    if "H2O" in solvent_text:
        amounts = [fld("equivalents", {"number": water_equiv, "unit": "equiv"}, ev)] if water_equiv else []
        parts.append(participant("water", "solvent", "H2O", "water", ev, "O", amounts))
    return parts


def allene_smiles(ar, r):
    ar_frag = {
        "Ph": "c1ccccc1", "m-MeC6H4": "c1cccc(C)c1", "m-CF3C6H4": "c1cccc(C(F)(F)F)c1",
        "p-MeC6H4": "c1ccc(C)cc1", "p-FC6H4": "c1ccc(F)cc1", "o-MeC6H4": "c1ccccc1C",
    }[ar]
    r_frag = {"H": "", "Et": "CC", "n-C4H9": "CCCC", "n-C6H13": "CCCCCC", "Ph": "c1ccccc1"}[r]
    return f"C=C=C({ar_frag}){r_frag}" if r_frag else f"C=C=C{ar_frag}"


def product_smiles(ar, r):
    ar_frag = {
        "Ph": "c1ccccc1", "m-MeC6H4": "c1cccc(C)c1", "m-CF3C6H4": "c1cccc(C(F)(F)F)c1",
        "p-MeC6H4": "c1ccc(C)cc1", "p-FC6H4": "c1ccc(F)cc1", "o-MeC6H4": "c1ccccc1C",
    }[ar]
    r_frag = {"H": "", "Et": "CC", "n-C4H9": "CCCC", "n-C6H13": "CCCCCC", "Ph": "c1ccccc1"}[r]
    return f"C=C(F)C(O)({ar_frag}){r_frag}" if r_frag else f"C=C(F)C(O){ar_frag}"


records = []

# Page-1 graphical abstract is a generic summary, not a row-level execution.
ev1 = [P1T, P1I]
generic_parts = [
    participant("generic_allene_2", "reactant", "2", "3-aryl-1,2-allene (generic Ar/R)", ev1),
    selectfluor(ev1, 1.2),
    participant("generic_product_3", "product", "3", "2-fluoroalken-3-ol (generic Ar/R)", ev1),
    participant("acetonitrile", "solvent", "MeCN", "acetonitrile", ev1, "CC#N"),
    participant("water", "solvent", "H2O", "water", ev1, "O"),
]
records.append(record(
    "graphical_abstract_general_scheme", "general_scheme", ev1, generic_parts,
    [fld("solvent", "MeCN/H2O = 10:1", ev1), fld("temperature", "r.t.", ev1),
     fld("reaction_time", None, []), *missing_execution_fields()],
    [fld("graphical_abstract_reported_yield", {"minimum": 37, "maximum": 78, "unit": "%", "raw_text": "37–78%"}, ev1, ["generic_product_3"]),
     fld("abstract_reported_yield", {"minimum": 37, "maximum": 88, "unit": "%", "raw_text": "37–88%"}, ev1, ["generic_product_3"])],
    notes=["Generic summary arrow; it does not represent an additional row-level experiment."],
    unresolved=["The graphical arrow prints 37–78%, while the abstract text prints 37–88%.",
                "Generic Ar/R structures are not complete molecular identities.",
                "Supporting information is mentioned later but was not supplied or associated."],
))

# Table 1: 11 independent optimization conditions. Entry 5 is also Table 2 entry 1.
table1 = [
    (1, "DMF/H2O = 10:1", 4.0, "complicated", None, None),
    (2, "DMA/H2O = 10:1", 4.0, "complicated", None, None),
    (3, "EtOH/H2O = 10:1", 4.0, "no reaction", None, None),
    (4, "MeNO2/H2O = 10:1", 1.0, None, 54, None),
    (5, "MeCN/H2O = 10:1", 2.0, None, 62, None),
    (6, "MeCN, 10 equiv H2O", 2.0, None, 51, 10),
    (7, "MeCN/H2O = 3:1", 2.0, None, 59, None),
    (8, "MeCN/H2O = 1:5", 2.0, None, 58, None),
    (9, "H2O", 22.0, None, 5, None),
    (10, "MeCN/H2O = 10:1", 12.0, None, 64, None),
    (11, "MeCN/H2O = 10:1", 22.0, None, 57, None),
]
for entry, solv, hours, qualitative, yld, water_eq in table1:
    ev = [P2T, P2I]
    rid = "optimized_2a_3a_table1_entry5_table2_entry1" if entry == 5 else f"table1_entry{entry}"
    ps = [
        participant("allene_2a", "reactant", "2a", "3-phenyl-1,2-heptadiene", ev, "C=C=C(c1ccccc1)CCCC"),
        selectfluor(ev, 1.2),
        participant("product_3a", "product", "3a", "2-fluoro-3-phenyl-1-hepten-3-ol", ev, "C=C(F)C(O)(c1ccccc1)CCCC"),
    ] + solvent_participants(solv, ev, water_eq)
    if entry == 9 and not any(p["entity_id"] == "water" for p in ps):
        ps.append(participant("water", "solvent", "H2O", "water", ev, "O"))
    temp = "r.t."
    if entry == 10:
        temp = {"number": 0, "unit": "°C"}
    elif entry == 11:
        temp = {"minimum": -40, "maximum": 0, "unit": "°C", "raw_text": "−40–0 °C"}
    conditions = [fld("solvent", solv, ev), fld("temperature", temp, ev),
                  fld("reaction_time", {"number": hours, "unit": "h"}, ev),
                  *missing_execution_fields()]
    outcomes = []
    if qualitative:
        outcomes.append(fld("reaction_result", qualitative, ev))
    else:
        outcomes += [fld("yield_3a", {"number": yld, "unit": "%"}, ev, ["product_3a"]),
                     fld("yield_measurement_basis", "NMR", ev, ["product_3a"])]
    if entry == 9:
        outcomes.append(fld("recovered_starting_material_yield", {"number": 95, "unit": "%"}, ev, ["allene_2a"]))
    notes = []
    unresolved = ["Absolute reaction scale, atmosphere, workup, and purification are not reported in the supplied main text."]
    if entry in (1, 2):
        unresolved.append("The components of the complicated mixture are not identified.")
    if entry == 3:
        unresolved.append("No analytical detection threshold is reported for the no-reaction result.")
    if entry == 4:
        notes.append("The prose describes 3a as the only product under this condition.")
    if entry == 5:
        notes.append("This condition is printed again as Table 2 entry 1 and is represented once.")
    unresolved.append("Table 1 has an orphan footnote 'b Isolated yield' with no visible row marker; the printed column heading is NMR yield and no isolated-yield assignment was guessed.")
    records.append(record(rid, "optimization_entry", ev, ps, conditions, outcomes, notes, unresolved))

# Table 2 entries 2–14. Entry 1 is already merged with Table 1 entry 5.
table2 = [
    (2, "Ph", "H", "2b", "3b", 12.0, 37, 1.2),
    (3, "Ph", "Et", "2c", "3c", 2.0, 65, 1.2),
    (4, "Ph", "n-C6H13", "2d", "3d", 2.0, 57, 1.2),
    (5, "Ph", "Ph", "2e", "3e", 2.0, 52, 1.2),
    (6, "m-MeC6H4", "n-C4H9", "2f", "3f", 3.0, 74, 1.2),
    (7, "m-MeC6H4", "n-C6H13", "2g", "3g", 3.0, 71, 1.2),
    (8, "m-CF3C6H4", "n-C4H9", "2h", "3h", 20.0, 40, 1.2),
    (9, "p-MeC6H4", "n-C4H9", "2i", "3i", 2.0, 77, 1.2),
    (10, "p-FC6H4", "n-C6H13", "2j", "3j", 3.0, 78, 1.2),
    (11, "o-MeC6H4", "n-C4H9", "2k", "3k", 15.0, 45, 1.2),
    (12, "o-MeC6H4", "n-C4H9", "2k", "3k", 24.0, 50, 1.5),
    (13, "o-MeC6H4", "n-C6H13", "2l", "3l", 15.0, 40, 1.2),
    (14, "o-MeC6H4", "n-C6H13", "2l", "3l", 24.0, 45, 1.5),
]
page3_context_entries = {3, 5, 6, 7, 9, 10, 11, 12, 13, 14}
reproduced_entries = {3, 7, 9, 14}
for entry, ar, r, sub, prod, hours, yld, equiv in table2:
    ev = [P2T, P2I]
    sid, pid = f"allene_{sub}", f"product_{prod}"
    ps = [
        participant(sid, "reactant", sub, f"aryl-substituted allene {sub} (Ar={ar}, R={r})", ev, allene_smiles(ar, r)),
        selectfluor(ev, equiv),
        participant(pid, "product", prod, f"2-fluoroalken-3-ol {prod} (Ar={ar}, R={r})", ev, product_smiles(ar, r)),
        participant("acetonitrile", "solvent", "MeCN", "acetonitrile", ev, "CC#N"),
        participant("water", "solvent", "H2O", "water", ev, "O"),
    ]
    page3_notes = []
    if entry == 5:
        page3_notes.append("The continuation prose restates that diphenyl propadiene afforded 3e in 52% yield within 2 h.")
    if entry in {6, 7, 9, 10}:
        page3_notes.append("The continuation prose groups Table 2 entries 6, 7, 9, and 10 as higher-yielding aryl-substitution cases.")
    if entry in reproduced_entries:
        page3_notes.append(f"The acknowledgment states that the result of Table 2 entry {entry} was reproduced by Bo Lu.")
    if entry in {11, 12, 13, 14}:
        page3_notes.append("The prose attributes the lower reactivity of ortho-methyl substrates to steric effects.")
    rec = record(
        f"table2_entry{entry}_{sub}_{prod}", "substrate_scope_entry", ev, ps,
        [fld("solvent", "MeCN/H2O = 10:1", ev), fld("temperature", "r.t.", ev),
         fld("reaction_time", {"number": hours, "unit": "h"}, ev),
         *missing_execution_fields()],
        [fld(f"yield_{prod}", {"number": yld, "unit": "%"}, ev, [pid]),
         fld("yield_measurement_basis", None, [])],
        notes=[],
        unresolved=["Table 2 does not state the yield measurement basis.",
                    "Absolute reaction scale, atmosphere, workup, and purification are not reported in the supplied main text.",
                    "The candidate constitutional SMILES and all stereochemical assignments remain unverified."],
    )
    if entry in page3_context_entries:
        rec["evidence_ids"].extend([P3T, P3I])
        rec["notes"].extend(fact(note, [P3T, P3I]) for note in page3_notes)
    records.append(rec)

# Scheme 1: three substrate rows under one collective failed/complex result.
scheme_rows = [
    ("2m", "n-C5H11", "H", "C=C=CCCCCC"),
    ("2n", "Bn", "H", "C=C=CCc1ccccc1"),
    ("2o", "n-C4H9", "n-C4H9", "C=C=C(CCCC)CCCC"),
]
for label, r1, r2, smiles in scheme_rows:
    ev = [P3T, P3I]
    ps = [
        participant(f"allene_{label}", "reactant", label, f"geminal bisalkyl-substituted allene {label} (R1={r1}, R2={r2})", ev, smiles),
        selectfluor(ev, 1.2),
        participant("acetonitrile", "solvent", "MeCN", "acetonitrile", ev, "CC#N"),
        participant("water", "solvent", "H2O", "water", ev, "O"),
    ]
    records.append(record(
        f"scheme1_{label}_failed_fluorohydroxylation", "substrate_scope_entry", ev, ps,
        [fld("solvent", "MeCN/H2O = 10:1", ev), fld("temperature", None, []),
         fld("reaction_time", None, []), *missing_execution_fields()],
        [fld("reaction_result", "no fluorinated products or complicated mixture", ev)],
        notes=["The prose says geminal bisalkyl-substituted allenes failed under the optimized conditions."],
        unresolved=["The scheme gives only a collective outcome and does not map 'no fluorinated products' versus 'complicated mixture' to individual substrate rows.",
                    "No analytical detection threshold, isolated product identity, explicit reaction time, explicit temperature, absolute scale, atmosphere, workup, or purification is reported in Scheme 1.",
                    "The prose says optimized conditions were used, but the specific 2 h and room-temperature values were not copied into these row records because Scheme 1 does not print them."],
    ))

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")

ids = [r["record_id"] for r in records]
page2_ids = [r["record_id"] for r in records if P2I in r["evidence_ids"]]
page3_ids = [r["record_id"] for r in records if P3I in r["evidence_ids"]]
coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1, "state": "attempted",
            "regions": [
                {"region": "title, abstract, and graphical abstract arrow in the middle of the original page",
                 "finding": "Generic fluorohydroxylation summary classified as a general scheme; its 37–78% graphical range conflicts with the abstract's 37–88% text and is not duplicated as a row-level experiment.",
                 "evidence_ids": [P1I, P1T]},
                {"region": "introduction and references in the lower half of the original page",
                 "finding": "Background electrophilic-fluorination discussion and citations; no independent present-paper experiment row.",
                 "evidence_ids": [P1I, P1T]},
            ],
            "record_ids": [f"{DOC}:graphical_abstract_general_scheme"],
            "unresolved": ["The graphical and abstract summary yield ranges disagree.",
                           "Generic Ar/R structures are not complete identities."],
        },
        {
            "page": 2, "state": "attempted",
            "regions": [
                {"region": "upper-right Table 1, reaction drawing, rows 1–11, and footnotes",
                 "finding": "Eleven optimization conditions extracted independently; Table 1 entry 5 is merged with identical Table 2 entry 1. Complicated, no-reaction, recovery, temperature, and water-loading results are preserved.",
                 "evidence_ids": [P2I, P2T]},
                {"region": "lower-right Table 2, reaction drawing, rows 1–14, and footnote",
                 "finding": "All fourteen scope rows inventoried; entry 1 is the merged optimized condition and entries 2–14 are independent records. The 1.5-equiv Selectfluor footnote is applied only to entries 12 and 14.",
                 "evidence_ids": [P2I, P2T]},
                {"region": "left-column results prose and cited background references",
                 "finding": "Narrative results are linked to table rows rather than duplicated; literature citations are not treated as present-paper experiments.",
                 "evidence_ids": [P2I, P2T]},
            ],
            "record_ids": page2_ids,
            "unresolved": ["Table 1's orphan footnote b says isolated yield but has no visible row marker; no row assignment was guessed.",
                           "Table 2 does not state yield measurement basis.",
                           "Absolute scales, atmospheres, workups, and purifications are absent."],
        },
        {
            "page": 3, "state": "attempted",
            "regions": [
                {"region": "upper-left continuation prose and Scheme 1",
                 "finding": "Three geminal bisalkyl-allene substrate rows extracted as failed/complex present-paper conditions; the collective outcome cannot be assigned more specifically per row.",
                 "evidence_ids": [P3I, P3T]},
                {"region": "upper-right conclusion, acknowledgment, and supporting-information availability statement",
                 "finding": "Table 2 discussion and reproduced-entry acknowledgments linked to existing rows; the online SI statement is not an SI association.",
                 "evidence_ids": [P3I, P3T]},
                {"region": "lower page references and journal whitespace",
                 "finding": "Citations and publication furniture; no additional present-paper reaction.",
                 "evidence_ids": [P3I, P3T]},
            ],
            "record_ids": page3_ids,
            "unresolved": ["Scheme 1 does not map the two collective failure descriptions to individual substrates.",
                           "The mentioned Supporting Information was not supplied or explicitly associated.",
                           "Complex structures and stereochemistry remain unverified."],
        },
    ],
}
COVERAGE.parent.mkdir(parents=True, exist_ok=True)
COVERAGE.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

tasks = json.loads(TASKS.read_text())
for task in tasks:
    if task["document_id"] == DOC and task["task_id"] in {P1T, P2T, P3T}:
        task["state"] = "attempted"
TASKS.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"records": len(records), "coverage_pages": [p["page"] for p in coverage["pages"]]}, ensure_ascii=False))
