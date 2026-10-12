#!/usr/bin/env python3
"""Build and enrich evidence-linked records for source PDF pages 7-12."""
from __future__ import annotations

import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / "runs/current"
DOC = "doc_0f68a8cc21860341"
OUT = RUN / "raw_model/records_pages_0007_0012.json"
COVERAGE = RUN / "coverage/pages_0007_0012.json"


def ev(page: int, kind: str = "image") -> str:
    return f"{DOC}:page{page}:{kind}"


def evidence(page: int) -> list[str]:
    return [ev(page, "text"), ev(page)]


def fact(value, pages=()):
    pages = [pages] if isinstance(pages, int) else list(pages)
    return {
        "value": value,
        "evidence_ids": [] if value is None else [ev(p) for p in pages],
        "verification": "missing" if value is None else "unreviewed",
    }


def field(name, value, pages=()):
    return {"name": name, "fact": fact(value, pages)}


def q(number, unit):
    return {"number": number, "unit": unit}


def participant(entity_id, role, label, page, amounts=()):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, page),
        "name": fact(None),
        "smiles": fact(None),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": [field(name, value, page) for name, value in amounts],
    }


def new_record(rid, page, kind, reactants, reagents, solvents, products,
               temperature, time, outcomes, *, notes=(), unresolved=()):
    parts = []
    for i, label in enumerate(reactants, 1):
        parts.append(participant(f"reactant_{i}", "reactant", label, page))
    for i, item in enumerate(reagents, 1):
        label, equiv = item if isinstance(item, tuple) else (item, None)
        amounts = [] if equiv is None else [("equivalents", q(equiv, "equiv"))]
        parts.append(participant(f"reagent_{i}", "reagent", label, page, amounts))
    for i, label in enumerate(solvents, 1):
        parts.append(participant(f"solvent_{i}", "solvent", label, page))
    for i, label in enumerate(products, 1):
        parts.append(participant(f"product_{i}", "product", label, page))
    conditions = [
        field("temperature", temperature, page if temperature is not None else ()),
        field("time", time, page if time is not None else ()),
        field("yield_measurement_basis", None),
        field("reaction_scale", None),
        field("concentration", None),
        field("atmosphere", None),
        field("workup", None),
        field("purification", None),
    ]
    return {
        "record_id": f"{DOC}:{rid}",
        "document_id": DOC,
        "source_reaction_id": rid,
        "record_kind": kind,
        "status": "needs_review",
        "completeness": "partial",
        "evidence_ids": evidence(page),
        "participants": parts,
        "steps": [{
            "step_id": "reaction",
            "participant_ids": [p["entity_id"] for p in parts],
            "conditions": conditions,
        }],
        "outcomes": [field(name, value, page) for name, value in outcomes],
        "notes": [fact(note, page) for note in notes],
        "review": {
            "method": "model",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": [
                "No supporting information is supplied or associated in this pilot.",
                "Participant structures are not machine-certified; SMILES remain null.",
                "Reaction scale, concentration, atmosphere, workup, purification, and yield basis are missing unless explicitly printed on pages 7-12.",
            ] + list(unresolved),
        },
    }


dataset = json.loads((RUN / "dataset.json").read_text())
existing = {r["source_reaction_id"]: r for r in dataset["experiments"]}
records = []


# Page 7: Table 6, one record per displayed row.
table6 = [
    ("10a", "LiBr·H2O", "HOAc", 70, q(21, "h"), [("11ab", 86)]),
    ("10a", "LiCl·H2O", "HOAc", 70, q(24, "h"), [("11ac", 78)]),
    ("10b", "NaI", "CF3CO2H-HOAc (1:1)", 70, q(1.5, "h"), [("11ba", 80)]),
    ("10b", "LiBr·H2O", "CF3CO2H-HOAc (1:1)", 70, q(7.5, "h"), [("11bb", 78)]),
    ("10b", "LiCl·H2O", "CF3CO2H-HOAc (1:1)", 70, q(8.5, "h"), [("11bc", 76)]),
    ("10b", "NaI", "HOAc", 70, q(12, "h"), [("11ba", 37)]),
    ("10b", "LiBr·H2O", "HOAc", 85, q(7.5, "h"), [("11bb", 17)]),
    ("10b", "LiCl·H2O", "HOAc", 80, q(21, "h"), [("11bc", 18)]),
    ("10c", "NaI", "CF3CO2H-HOAc (1:1)", 70, q(3.5, "h"), [("(E)-11ca", 63), ("(Z)-11ca", 16)]),
    ("10c", "LiBr·H2O", "CF3CO2H-HOAc (1:1)", 70, q(6, "h"), [("(E)-11cb", 58), ("(Z)-11cb", 22)]),
    ("10c", "LiCl·H2O", "CF3CO2H-HOAc (1:1)", 70, q(8, "h"), [("(E)-11cc", 50), ("(Z)-11cc", 22)]),
    ("10c", "NaI", "HOAc", 70, q(21, "h"), [("11ca", 70, "1:1")]),
    ("10c", "NaI", "CF3CO2H", 70, q(10, "min"), [("11ca", 58, "3.1:1")]),
    ("10d", "NaI", "CF3CO2H-HOAc (1:1)", 70, q(5, "h"), [("(E)-11da", 44)]),
    ("10d", "LiBr·H2O", "CF3CO2H-HOAc (1:1)", 70, q(5, "h"), [("(E)-11db", 82)]),
    ("10d", "LiCl·H2O", "CF3CO2H-HOAc (1:1)", 70, q(6, "h"), [("(E)-11dc", 37)]),
]
for i, (sub, mx, solv, temp, time, products) in enumerate(table6, 1):
    prod_labels = [p[0] for p in products]
    outs = []
    for item in products:
        outs.append((f"yield_{item[0].replace('(', '').replace(')', '')}", q(item[1], "%")))
        if len(item) == 3:
            outs.append(("E/Z_ratio", item[2]))
    records.append(new_record(
        f"table6_entry{i}", 7, "substrate_scope_entry", [sub], [(mx, None)],
        [solv], prod_labels, q(temp, "°C"), time, outs,
        notes=("Table 6 is the current-paper hydrohalogenation scope for 1,2-allenyl cyanides.",),
    ))


# Page 8: Table 7, one phosphine-oxide hydrohalogenation record per row.
table7 = [
    ("NaI", "HOAc", "reflux", 23, "13aa", 60, True),
    ("LiI", "HOAc", q(100, "°C"), 12, "13aa", 75, True),
    ("LiBr·H2O", "HOAc", q(100, "°C"), 36, "13ab", 70, True),
    ("LiCl·H2O", "HOAc", q(100, "°C"), 40, "13ac", 58, True),
    ("aqueous HI", "aqueous HI", "reflux", 48, "13aa", 46, False),
    ("aqueous HBr", "aqueous HBr", "reflux", 60, "13ab", 37, False),
    ("aqueous HCl", "aqueous HCl", "reflux", 60, "13ac", 31, False),
]
for i, (mx, solv, temp, hours, prod, yld, has_equiv) in enumerate(table7, 1):
    reagent = (mx, 1.1) if has_equiv else (mx, None)
    records.append(new_record(
        f"table7_entry{i}", 8, "optimization_entry", ["12a"], [reagent], [solv],
        [prod], temp, q(hours, "h"), [("yield", q(yld, "%"))],
        notes=("Table 7 compares MX/HOAc with aqueous HX for propadienyl diphenyl phosphine oxide 12a.",),
    ))


# Page 8: Scheme 8, two distinct Sonogashira-type couplings.
records.append(new_record(
    "scheme8_entry1", 8, "reported_experiment", ["13aa", "1-hexyne"],
    [("PdCl2(PPh3)2 (1 mol%)", None), ("CuI (1 mol%)", None), ("Et3N", None)],
    [], ["7j"], "r.t.", None, [("yield", q(93, "%"))],
    unresolved=("Reaction time and solvent are not printed on the Scheme 8 arrow.",),
))
records.append(new_record(
    "scheme8_entry2", 8, "reported_experiment", ["13aa", "phenylacetylene"],
    [("PdCl2(PPh3)2 (1 mol%)", None), ("CuI (1 mol%)", None), ("Et3N", None)],
    [], ["7k"], "r.t.", None, [("yield", q(95, "%"))],
    unresolved=("Reaction time and solvent are not printed on the Scheme 8 arrow.",),
))


def get_update(rid: str, pages):
    rec = copy.deepcopy(existing[rid])
    pages = [pages] if isinstance(pages, int) else list(pages)
    for page in pages:
        for eid in evidence(page):
            if eid not in rec["evidence_ids"]:
                rec["evidence_ids"].append(eid)
    rec["status"] = "needs_review"
    rec["completeness"] = "partial"
    rec["review"]["method"] = "model"
    rec["review"]["checked_fields"] = []
    rec["review"]["unresolved"] = [
        x.replace("pages 1-6", "pages 1-12") for x in rec["review"]["unresolved"]
    ]
    return rec


def upsert(items, name, value, pages):
    replacement = field(name, value, pages)
    for i, item in enumerate(items):
        if item["name"] == name:
            items[i] = replacement
            return
    items.append(replacement)


def entity(rec, entity_id):
    return next(p for p in rec["participants"] if p["entity_id"] == entity_id)


def add_amount(rec, entity_id, name, value, pages):
    upsert(entity(rec, entity_id)["amounts"], name, value, pages)


def add_condition(rec, name, value, pages, step_id="reaction"):
    step = next(s for s in rec["steps"] if s["step_id"] == step_id)
    upsert(step["conditions"], name, value, pages)


def add_outcome(rec, name, value, pages):
    upsert(rec["outcomes"], name, value, pages)


def add_note(rec, text, pages):
    if not any(n["value"] == text for n in rec["notes"]):
        rec["notes"].append(fact(text, pages))


def add_unresolved(rec, text):
    if text not in rec["review"]["unresolved"]:
        rec["review"]["unresolved"].append(text)


def add_participant(rec, entity_id, role, label, page, amounts=()):
    if any(p["entity_id"] == entity_id for p in rec["participants"]):
        return
    rec["participants"].append(participant(entity_id, role, label, page, amounts))
    rec["steps"][0]["participant_ids"].append(entity_id)


def apply_simple(rid, page, charges=(), outcomes=(), conditions=(), notes=(), unresolved=()):
    rec = get_update(rid, page)
    for entity_id, name, value in charges:
        add_amount(rec, entity_id, name, value, page)
    for name, value in outcomes:
        add_outcome(rec, name, value, page)
    for name, value in conditions:
        add_condition(rec, name, value, page)
    for note in notes:
        add_note(rec, note, page)
    for item in unresolved:
        add_unresolved(rec, item)
    records.append(rec)
    return rec


# Pages 7-8: typical 2aa procedure and three abbreviated acid preparations.
rec = get_update("scheme1_entry4", [7, 8])
for eid, name, value in [
    ("reactant_1", "mass", q(105, "mg")), ("reactant_1", "amount", q(0.75, "mmol")),
    ("reagent_1", "mass", q(135, "mg")), ("reagent_1", "amount", q(0.90, "mmol")),
    ("solvent_1", "volume", q(1.5, "mL")),
]:
    add_amount(rec, eid, name, value, [7, 8])
add_condition(rec, "atmosphere", "Ar", 7)
add_condition(rec, "monitoring", "TLC", 7)
add_condition(rec, "workup", "Add 2 N HCl (0.4 mL), quench with H2O (1 mL), extract with Et2O (5 × 5 mL), wash with 5% aq Na2S2O3 and saturated NH4Cl, dry over MgSO4, and remove solvent.", [7, 8])
add_condition(rec, "purification", "Flash chromatography; petroleum ether-ethyl acetate 5:1.", 8)
for name, value in [
    ("isolated_mass_pure_Z_2aa", q(135, "mg")), ("isolated_yield_pure_Z_2aa", q(67, "%")),
    ("isolated_mass_Z_E_mixture_2aa", q(57, "mg")), ("isolated_yield_Z_E_mixture_2aa", q(28, "%")),
    ("isolated_mixture_Z/E_ratio", "67.5:32.5"),
]:
    add_outcome(rec, name, value, 8)
add_note(rec, "The detailed typical procedure is the same 1a/NaI/HOAc/reflux/6.5 h run as Scheme 1 entry 4; NMR and fraction-specific isolated outcomes are both retained.", [7, 8])
records.append(rec)

simple = {
    "table1_entry1": (8, [("reactant_1", "mass", q(99, "mg")), ("reactant_1", "amount", q(0.71, "mmol")), ("reagent_1", "mass", q(89, "mg")), ("reagent_1", "amount", q(0.85, "mmol")), ("solvent_1", "volume", q(0.5, "mL"))], [("isolated_mass", q(139, "mg"))], [], [], []),
    "table1_entry2": (8, [("reactant_1", "mass", q(107, "mg")), ("reactant_1", "amount", q(0.76, "mmol")), ("reagent_1", "mass", q(55.4, "mg")), ("reagent_1", "amount", q(0.92, "mmol")), ("solvent_1", "volume", q(0.5, "mL"))], [("isolated_mass", q(117, "mg"))], [], [], []),
    "table1_entry3": (8, [("reactant_1", "mass", q(91, "mg")), ("reactant_1", "amount", q(0.50, "mmol")), ("reagent_1", "mass", q(90, "mg")), ("reagent_1", "amount", q(0.60, "mmol")), ("solvent_1", "volume", q(0.4, "mL"))], [("isolated_mass", q(153, "mg")), ("experimental_section_printed_yield", "9%")], [], ["The experimental paragraph visibly prints 153 mg (9%), while Table 1 reports 99%; both source presentations are retained."], ["Table 1 and the experimental paragraph conflict on the printed yield for 2ba (99% versus 9%)."]),
    "table1_entry4": (9, [("reactant_1", "mass", q(91, "mg")), ("reactant_1", "amount", q(0.50, "mmol")), ("reagent_1", "mass", q(63, "mg")), ("reagent_1", "amount", q(0.60, "mmol")), ("solvent_1", "volume", q(0.4, "mL"))], [("isolated_mass", q(108, "mg"))], [], [], []),
    "table1_entry5": (9, [("reactant_1", "mass", q(146, "mg")), ("reactant_1", "amount", q(0.80, "mmol")), ("reagent_1", "mass", q(58, "mg")), ("reagent_1", "amount", q(0.96, "mmol")), ("solvent_1", "volume", q(0.25, "mL"))], [("isolated_mass", q(149, "mg")), ("experimental_section_yield", q(85, "%"))], [], ["The experimental paragraph reports 85%, while Table 1 reports 87%."], ["Table 1 and the experimental paragraph conflict on the 2bc yield (87% versus 85%)."]),
    "scheme2_entry1": (9, [("reactant_1", "mass", q(20.6, "mg")), ("reactant_1", "amount", q(0.21, "mmol")), ("reagent_1", "mass", q(63, "mg")), ("reagent_1", "amount", q(0.42, "mmol")), ("solvent_1", "volume", q(0.5, "mL"))], [("isolated_mass", q(34.1, "mg"))], [("atmosphere", "Ar")], [], []),
    "scheme2_entry2": (9, [("reactant_1", "mass", q(40, "mg")), ("reactant_1", "amount", q(0.41, "mmol")), ("reagent_1", "mass", q(86, "mg")), ("reagent_1", "amount", q(0.82, "mmol")), ("solvent_1", "volume", q(0.50, "mL"))], [("isolated_mass", q(44.5, "mg"))], [], [], []),
    "table2_entry1": (9, [("reactant_1", "mass", q(72, "mg")), ("reactant_1", "amount", q(0.57, "mmol")), ("reagent_1", "mass", q(173, "mg")), ("reagent_1", "amount", q(1.15, "mmol")), ("solvent_1", "volume", q(0.50, "mL"))], [("isolated_mass", q(136, "mg"))], [], [], []),
    "scheme3_entry1": (9, [("reactant_1", "mass", q(83, "mg")), ("reactant_1", "amount", q(0.66, "mmol")), ("reagent_1", "solution_concentration", "45%"), ("reagent_1", "volume", q(0.25, "mL"))], [("isolated_mass_4aa", q(66, "mg")), ("isolated_mass_2da", q(71, "mg"))], [], [], []),
    "table2_entry3": (9, [("reactant_1", "mass", q(58, "mg")), ("reactant_1", "amount", q(0.46, "mmol")), ("reagent_1", "mass", q(100, "mg")), ("reagent_1", "amount", q(0.95, "mmol")), ("solvent_1", "volume", q(0.50, "mL"))], [("isolated_mass", q(79, "mg"))], [], [], []),
    "scheme3_entry2": (10, [("reactant_1", "mass", q(70, "mg")), ("reactant_1", "amount", q(0.56, "mmol")), ("reagent_1", "solution_concentration", "40%"), ("reagent_1", "volume", q(1, "mL"))], [("isolated_mass_2db", q(58, "mg"))], [], [], []),
    "table2_entry4": (10, [("reactant_1", "mass", q(83, "mg")), ("reactant_1", "amount", q(0.66, "mmol")), ("reagent_1", "mass", q(80, "mg")), ("reagent_1", "amount", q(1.32, "mmol")), ("solvent_1", "volume", q(0.50, "mL"))], [("isolated_mass", q(75, "mg"))], [], [], []),
    "scheme3_entry3": (10, [("reactant_1", "mass", q(70, "mg")), ("reactant_1", "amount", q(0.56, "mmol")), ("reagent_1", "solution_concentration", "36%"), ("reagent_1", "volume", q(1, "mL"))], [("isolated_mass_2dc", q(54.2, "mg"))], [], [], []),
    "table2_entry5": (10, [("reactant_1", "mass", q(102, "mg")), ("reactant_1", "amount", q(0.52, "mmol")), ("reagent_1", "mass", q(113, "mg")), ("reagent_1", "amount", q(0.75, "mmol")), ("solvent_1", "volume", q(0.50, "mL"))], [("isolated_mass", q(165, "mg"))], [], [], []),
    "table2_entry6": (10, [("reactant_1", "mass", q(135, "mg")), ("reactant_1", "amount", q(0.69, "mmol")), ("reagent_1", "mass", q(101, "mg")), ("reagent_1", "amount", q(0.97, "mmol")), ("solvent_1", "volume", q(0.50, "mL"))], [("isolated_mass", q(172, "mg"))], [], [], []),
    "table2_entry9": (10, [("reactant_1", "mass", q(105, "mg")), ("reactant_1", "amount", q(0.54, "mmol")), ("reagent_1", "mass", q(97, "mg")), ("reagent_1", "amount", q(1.61, "mmol")), ("solvent_1", "volume", q(0.50, "mL"))], [("isolated_mass", q(104, "mg"))], [], [], []),
    "table3_entry6": (10, [("reactant_1", "mass", q(91, "mg")), ("reactant_1", "amount", q(0.72, "mmol")), ("reagent_1", "mass", q(325, "mg")), ("reagent_1", "amount", q(2.17, "mmol")), ("solvent_1", "CF3CO2H_volume", q(1, "mL")), ("solvent_1", "HOAc_volume", q(1, "mL"))], [("isolated_mass", q(173, "mg"))], [], [], []),
    "table3_entry9": (10, [("reactant_1", "mass", q(108, "mg")), ("reactant_1", "amount", q(0.86, "mmol")), ("reagent_1", "mass", q(180, "mg")), ("reagent_1", "amount", q(1.72, "mmol")), ("solvent_1", "volume", q(0.5, "mL"))], [("isolated_mass", q(98, "mg")), ("experimental_section_printed_yield", "8%")], [("experimental_section_temperature", "reflux")], ["The experimental paragraph visibly prints 98 mg (8%), while Table 3 reports 88%; both are retained."], ["Table 3 and the experimental paragraph conflict on the printed 4cb yield (88% versus 8%)."]),
    "table3_entry10": (11, [("reactant_1", "mass", q(81, "mg")), ("reactant_1", "amount", q(0.52, "mmol")), ("reagent_1", "mass", q(157, "mg")), ("reagent_1", "amount", q(1.04, "mmol")), ("solvent_1", "volume", q(1, "mL"))], [("isolated_mass", q(144, "mg"))], [("experimental_section_temperature", "reflux")], [], ["Table 3 presents a general 80 °C condition, while the experimental paragraph says reflux."]),
    "table3_entry11": (11, [("reactant_1", "mass", q(74, "mg")), ("reactant_1", "amount", q(0.48, "mmol")), ("reagent_1", "mass", q(100, "mg")), ("reagent_1", "amount", q(0.96, "mmol")), ("solvent_1", "volume", q(1, "mL"))], [("isolated_mass", q(86, "mg"))], [("experimental_section_temperature", "reflux")], [], ["Table 3 presents a general 80 °C condition, while the experimental paragraph says reflux."]),
    "table3_entry12": (11, [("reactant_1", "mass", q(133, "mg")), ("reactant_1", "amount", q(0.86, "mmol")), ("reagent_1", "mass", q(156, "mg")), ("reagent_1", "amount", q(2.6, "mmol")), ("solvent_1", "volume", q(1, "mL"))], [("isolated_mass", q(98, "mg"))], [("experimental_section_temperature", "reflux")], [], ["Table 3 presents a general 80 °C condition, while the experimental paragraph says reflux."]),
    "table4_entry1": (11, [("reactant_1", "mass", q(91, "mg")), ("reactant_1", "amount", q(0.43, "mmol")), ("reagent_1", "mass", q(91, "mg")), ("reagent_1", "amount", q(0.61, "mmol")), ("solvent_1", "volume", q(0.5, "mL"))], [("isolated_mass", q(114, "mg"))], [], [], []),
    "table4_entry2": (11, [("reactant_1", "mass", q(97, "mg")), ("reactant_1", "amount", q(0.65, "mmol")), ("reagent_1", "mass", q(68, "mg")), ("reagent_1", "amount", q(0.97, "mmol")), ("solvent_1", "volume", q(0.5, "mL"))], [("isolated_mass", q(120, "mg"))], [], [], []),
    "table4_entry4": (11, [("reactant_1", "mass", q(117, "mg")), ("reactant_1", "amount", q(0.56, "mmol")), ("reagent_1", "mass", q(168, "mg")), ("reagent_1", "amount", q(2.78, "mmol")), ("solvent_1", "volume", q(0.5, "mL"))], [("isolated_mass_4ec", q(87, "mg")), ("isolated_mass_6e", q(19.1, "mg"))], [("experimental_section_temperature", q(80, "°C"))], [], ["Table 4 says reflux, while the experimental paragraph specifies 80 °C."]),
    "table4_entry5": (11, [("reactant_1", "mass", q(70, "mg")), ("reactant_1", "amount", q(0.50, "mmol")), ("reagent_1", "mass", q(112, "mg")), ("reagent_1", "amount", q(0.75, "mmol")), ("solvent_1", "volume", q(0.5, "mL"))], [("isolated_mass", q(104, "mg"))], [], [], []),
    "table4_entry7": (11, [("reactant_1", "mass", q(80, "mg")), ("reactant_1", "amount", q(0.57, "mmol")), ("reagent_1", "mass", q(90, "mg")), ("reagent_1", "amount", q(0.86, "mmol")), ("solvent_1", "volume", q(0.5, "mL"))], [("isolated_mass", q(94, "mg")), ("experimental_section_E/Z_ratio", "1.2:1")], [], ["Table 4 gives E/Z = 1:1, while the experimental paragraph gives E/Z = 1.2:1."], ["Table 4 and the experimental paragraph conflict on the 4fb E/Z ratio (1:1 versus 1.2:1)."]),
    "table4_entry10": (12, [("reactant_1", "mass", q(100, "mg")), ("reactant_1", "amount", q(0.71, "mmol")), ("reagent_1", "mass", q(186, "mg")), ("reagent_1", "amount", q(2.86, "mmol")), ("solvent_1", "volume", q(0.5, "mL"))], [("isolated_mass", q(69, "mg")), ("experimental_section_printed_yield", "5%")], [], ["The experimental paragraph visibly prints 69 mg (5%), while Table 4 reports 55%; both are retained."], ["Table 4 and the experimental paragraph conflict on the printed 4fc yield (55% versus 5%)."]),
    "table4_entry12": (12, [("reactant_1", "mass", q(65, "mg")), ("reactant_1", "amount", q(0.46, "mmol")), ("reagent_1", "mass", q(139, "mg")), ("reagent_1", "amount", q(0.93, "mmol")), ("solvent_1", "volume", q(0.5, "mL"))], [("isolated_mass_4ga", q(28.6, "mg")), ("isolated_mass_6g", q(7.7, "mg"))], [], [], []),
    "table4_entry13": (12, [("reactant_1", "mass", q(101, "mg")), ("reactant_1", "amount", q(0.72, "mmol")), ("reagent_1", "mass", q(152, "mg")), ("reagent_1", "amount", q(1.44, "mmol")), ("solvent_1", "volume", q(0.5, "mL"))], [("isolated_mass_halo_product", q(36.6, "mg")), ("isolated_mass_6g", q(33.7, "mg"))], [], ["The heading and characterization identify 4gb, but the experimental yield sentence prints 4ga; the product-label conflict is retained."], ["The page-12 experimental paragraph conflicts internally between 4gb and 4ga."]),
}

for rid, args in simple.items():
    apply_simple(rid, *args)


# Page 12: detailed 6h preparation corresponding to Scheme 4 entry 2.
rec = get_update("scheme4_entry2", 12)
for eid, name, value in [
    ("reactant_1", "mass", q(63, "mg")), ("reactant_1", "amount", q(0.41, "mmol")),
    ("reagent_1", "mass", q(86, "mg")), ("reagent_1", "amount", q(0.82, "mmol")),
    ("solvent_1", "HOAc_volume", q(0.25, "mL")), ("solvent_1", "CF3CO2H_volume", q(0.25, "mL")),
]:
    add_amount(rec, eid, name, value, 12)
add_outcome(rec, "isolated_mass_6h", q(35, "mg"), 12)
add_note(rec, "Scheme 4 labels the reagent LiBr, whereas the experimental paragraph specifies LiBr·H2O; the identity remains unresolved.", 12)
add_unresolved(rec, "Scheme 4 and the experimental paragraph differ on LiBr versus LiBr·H2O.")
records.append(rec)


# Page 12: detailed coupling procedures for Scheme 5 entries 1-4.
rec = get_update("scheme5_entry1", 12)
for eid, name, value in [
    ("reactant_1", "mass", q(111, "mg")), ("reactant_1", "amount", q(0.44, "mmol")),
    ("reagent_1", "mass", q(25, "mg")), ("reagent_1", "amount", q(0.022, "mmol")),
    ("solvent_1", "coupling_stage_volume", q(1, "mL")), ("product_1", "isolated_mass", q(55.1, "mg")),
]:
    add_amount(rec, eid, name, value, 12)
add_participant(rec, "precursor_zinc_bromide", "reagent", "dried ZnBr2", 12, [("mass", q(510, "mg")), ("amount", q(2.27, "mmol"))])
add_participant(rec, "precursor_n_butyllithium", "reagent", "n-BuLi", 12, [("molarity", q(2, "M")), ("volume", q(1, "mL"))])
add_condition(rec, "organozinc_preparation", "ZnBr2 in THF (3 mL); add n-BuLi at -78 °C, stir 20 min, warm to r.t., and stir 30 min.", 12)
add_condition(rec, "coupling_temperature", "r.t.", 12)
add_condition(rec, "atmosphere", "Ar", 12)
add_condition(rec, "workup", "Remove solvent by evaporation.", 12)
add_condition(rec, "purification", "Silica-gel chromatography; petroleum ether-ethyl acetate 50:1.", 12)
records.append(rec)

rec = get_update("scheme5_entry2", 12)
for eid, name, value in [
    ("reactant_1", "mass", q(113, "mg")), ("reactant_1", "amount", q(0.44, "mmol")),
    ("reagent_1", "mass", q(26, "mg")), ("reagent_1", "amount", q(0.02, "mmol")),
    ("solvent_1", "coupling_stage_volume", q(1, "mL")), ("product_1", "isolated_mass", q(88.3, "mg")),
]:
    add_amount(rec, eid, name, value, 12)
add_participant(rec, "precursor_phenyl_iodide", "reagent", "PhI", 12, [("mass", q(125.6, "mg")), ("amount", q(0.62, "mmol"))])
add_participant(rec, "precursor_n_butyllithium", "reagent", "n-BuLi", 12, [("molarity", q(2, "M")), ("volume", q(0.31, "mL"))])
add_participant(rec, "precursor_zinc_bromide", "reagent", "dried ZnBr2", 12, [("mass", q(680, "mg")), ("amount", q(3, "mmol"))])
add_condition(rec, "organozinc_preparation", "Add n-BuLi to PhI in THF (1 mL) at -78 °C, warm to -40 °C, then add ZnBr2 in THF (2 mL).", 12)
add_condition(rec, "atmosphere", "Ar", 12)
add_condition(rec, "workup", "Remove solvent by evaporation.", 12)
add_condition(rec, "purification", "Silica-gel chromatography; petroleum ether-ethyl acetate 60:1.", 12)
records.append(rec)

rec = get_update("scheme5_entry3", 12)
add_participant(rec, "experimental_solvent", "solvent", "MeCN", 12, [("total_volume", q(1, "mL"))])
for eid, name, value in [
    ("reactant_1", "mass", q(88, "mg")), ("reactant_1", "amount", q(0.35, "mmol")),
    ("reactant_2", "volume", q(0.05, "mL")), ("reactant_2", "amount", q(0.46, "mmol")),
    ("reagent_1", "mass", q(15, "mg")), ("reagent_1", "amount", q(0.019, "mmol")),
    ("reagent_2", "mass", q(10.9, "mg")), ("reagent_2", "amount", q(0.057, "mmol")),
    ("reagent_3", "volume", q(0.08, "mL")), ("reagent_3", "amount", q(0.52, "mmol")),
    ("product_1", "isolated_mass", q(67, "mg")),
]:
    add_amount(rec, eid, name, value, 12)
add_condition(rec, "temperature", "r.t.", 12)
add_condition(rec, "workup", "Remove solvent by evaporation.", 12)
add_condition(rec, "purification", "Silica-gel chromatography; petroleum ether-ethyl acetate 50:1.", 12)
records.append(rec)

rec = get_update("scheme5_entry4", 12)
for eid, name, value in [
    ("reactant_1", "mass", q(127, "mg")), ("reactant_1", "amount", q(0.5, "mmol")),
    ("reagent_1", "mass", q(28, "mg")), ("reagent_1", "amount", q(0.038, "mmol")),
    ("solvent_1", "coupling_stage_volume", q(1, "mL")),
]:
    add_amount(rec, eid, name, value, 12)
add_participant(rec, "precursor_phenyl_iodide", "reagent", "PhI", 12, [("mass", q(153, "mg")), ("amount", q(0.75, "mmol"))])
add_participant(rec, "precursor_n_butyllithium", "reagent", "n-BuLi", 12, [("molarity", q(2, "M")), ("volume", q(0.38, "mL"))])
add_participant(rec, "precursor_zinc_bromide", "reagent", "dried ZnBr2", 12, [("mass", q(680, "mg")), ("amount", q(3, "mmol"))])
add_condition(rec, "organozinc_preparation", "Add n-BuLi to PhI in THF (1 mL) at -78 °C, warm to -40 °C, then add ZnBr2 in THF (2 mL).", 12)
add_unresolved(rec, "The detailed 7d procedure continues on page 13, outside this session's claimed page coverage.")
records.append(rec)


assert len(records) == 60, len(records)
assert len({r["record_id"] for r in records}) == len(records)


page_record_ids = {
    7: [f"{DOC}:table6_entry{i}" for i in range(1, 17)] + [f"{DOC}:scheme1_entry4"],
    8: [f"{DOC}:table7_entry{i}" for i in range(1, 8)] + [f"{DOC}:scheme8_entry1", f"{DOC}:scheme8_entry2", f"{DOC}:scheme1_entry4"] + [f"{DOC}:table1_entry{i}" for i in range(1, 4)],
    9: [f"{DOC}:table1_entry{i}" for i in range(3, 6)] + [f"{DOC}:scheme2_entry1", f"{DOC}:scheme2_entry2", f"{DOC}:table2_entry1", f"{DOC}:scheme3_entry1", f"{DOC}:table2_entry3"],
    10: [f"{DOC}:scheme3_entry2", f"{DOC}:scheme3_entry3"] + [f"{DOC}:table2_entry{i}" for i in (4, 5, 6, 9)] + [f"{DOC}:table3_entry6", f"{DOC}:table3_entry9"],
    11: [f"{DOC}:table3_entry{i}" for i in (10, 11, 12)] + [f"{DOC}:table4_entry{i}" for i in (1, 2, 4, 5, 7)],
    12: [f"{DOC}:table4_entry{i}" for i in (10, 12, 13)] + [f"{DOC}:scheme4_entry2"] + [f"{DOC}:scheme5_entry{i}" for i in range(1, 5)],
}

coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 7,
            "state": "attempted",
            "regions": [
                {"region": "upper and middle page, Table 6", "finding": "Sixteen current-paper 1,2-allenyl-cyanide hydrohalogenation rows were inspected and extracted separately, including separate E/Z yields and solvent-dependent ratios.", "evidence_ids": [ev(7)]},
                {"region": "lower left, conclusion", "finding": "Conclusion summarizes the current work; it was not converted into duplicate experiments.", "evidence_ids": evidence(7)},
                {"region": "lower right, starting-material paragraph and beginning of 2aa typical procedure", "finding": "Cited starting-material preparations were not imported; the 2aa procedure continues on page 8 and enriches Scheme 1 entry 4.", "evidence_ids": evidence(7)},
            ],
            "record_ids": page_record_ids[7],
            "unresolved": ["Table 6 does not state a yield measurement basis or row-specific workup/purification.", "The 2aa procedure crosses the page-7/page-8 boundary."],
        },
        {
            "page": 8,
            "state": "attempted",
            "regions": [
                {"region": "upper page, Table 7", "finding": "Seven phosphine-oxide hydrohalogenation optimization rows were extracted separately.", "evidence_ids": [ev(8)]},
                {"region": "upper-middle left, Scheme 8", "finding": "Two Pd/Cu-catalyzed couplings of 13aa were extracted arrow by arrow; unprinted solvent and time remain missing.", "evidence_ids": [ev(8)]},
                {"region": "lower columns, 2aa-2ba experimental paragraphs", "finding": "The detailed 2aa procedure and abbreviated 2ab/2ac/2ba preparations were merged into matching page-1/page-2 records; the printed 2ba yield conflict was retained.", "evidence_ids": evidence(8)},
            ],
            "record_ids": page_record_ids[8],
            "unresolved": ["Scheme 8 omits solvent and reaction time.", "The 2ba paragraph visibly prints 9%, while Table 1 reports 99%."],
        },
        {
            "page": 9,
            "state": "attempted",
            "regions": [
                {"region": "left column, 2ba continuation and 2bb/2bc/2ca preparations", "finding": "Characterization continuation and four matching preparations were linked to existing records without duplication.", "evidence_ids": evidence(9)},
                {"region": "right column, 2cb and 4aa/2da/4ab preparations", "finding": "Two acid/ester hydrohalogenations, the HI hydrolysis coproduct experiment, and the 4ab preparation were merged into existing records with printed charges and isolated masses.", "evidence_ids": evidence(9)},
            ],
            "record_ids": page_record_ids[9],
            "unresolved": ["Most abbreviated preparations do not repeat workup, purification, atmosphere, or concentration."],
        },
        {
            "page": 10,
            "state": "attempted",
            "regions": [
                {"region": "left column, 2db/4ac/2dc/4ba preparations", "finding": "Four existing records were enriched with charges and isolated masses.", "evidence_ids": evidence(10)},
                {"region": "right column, 4bb/4bc/4ca/4cb preparations", "finding": "Four existing records were enriched; the 4cb experimental paragraph's printed 8% conflicts with Table 3's 88% and was retained explicitly.", "evidence_ids": evidence(10)},
            ],
            "record_ids": page_record_ids[10],
            "unresolved": ["The 4cb table/experimental yield conflict is unresolved.", "Abbreviated preparations omit full workup and purification."],
        },
        {
            "page": 11,
            "state": "attempted",
            "regions": [
                {"region": "left column, 4da/4db/4dc/4ea/4eb preparations", "finding": "Five matching Table 3/Table 4 records were enriched; table-versus-prose temperature presentations were retained separately.", "evidence_ids": evidence(11)},
                {"region": "right column, 4ec+6e/4fa/4fb preparations", "finding": "Three matching Table 4 records were enriched, including the 6e coproduct and the conflicting 4fb E/Z ratios.", "evidence_ids": evidence(11)},
            ],
            "record_ids": page_record_ids[11],
            "unresolved": ["Table 4 and the 4fb paragraph give E/Z 1:1 and 1.2:1, respectively.", "Some table temperatures are expressed differently in the experimental paragraphs."],
        },
        {
            "page": 12,
            "state": "attempted",
            "regions": [
                {"region": "left column, 4fc/4ga+6g/4gb+6g/6h preparations", "finding": "Four existing records were enriched; printed 4fc and 4ga/4gb conflicts were retained rather than silently corrected.", "evidence_ids": evidence(12)},
                {"region": "right column, 7a-7d coupling procedures", "finding": "Detailed 7a-7c procedures and the visible beginning of 7d were merged into Scheme 5 records, including organozinc-generation stages and purification where printed.", "evidence_ids": evidence(12)},
            ],
            "record_ids": page_record_ids[12],
            "unresolved": ["The 4fc paragraph visibly prints 5%, while Table 4 reports 55%.", "The 4gb paragraph's yield sentence prints 4ga despite the heading and characterization identifying 4gb.", "The 7d detailed procedure continues on page 13, outside this session's claimed coverage."],
        },
    ],
}

OUT.parent.mkdir(parents=True, exist_ok=True)
COVERAGE.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
COVERAGE.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

tasks_path = RUN / "tasks.json"
tasks = json.loads(tasks_path.read_text())
for task in tasks:
    if task.get("document_id") == DOC and task.get("evidence_id") in {ev(p, "text") for p in range(7, 13)}:
        task["state"] = "attempted"
        task["reason"] = "Original page image and page text inspected; records and coverage ledger generated for PDF pages 7-12."
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"submitted_records": len(records), "new_records": 25, "updated_records": 35, "coverage_pages": list(range(7, 13))}, ensure_ascii=False))
