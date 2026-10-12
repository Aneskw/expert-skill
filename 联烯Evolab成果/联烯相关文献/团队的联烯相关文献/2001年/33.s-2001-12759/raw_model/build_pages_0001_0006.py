#!/usr/bin/env python3
"""Build evidence-linked machine records for source PDF pages 1-6."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / "runs/current"
DOC = "doc_0f68a8cc21860341"
OUT = RUN / "raw_model/records_pages_0001_0006.json"
COVERAGE = RUN / "coverage/pages_0001_0006.json"


def ev(page: int, kind: str = "image") -> str:
    return f"{DOC}:page{page}:{kind}"


def fact(value, page=None):
    return {
        "value": value,
        "evidence_ids": [] if value is None else [ev(page)],
        "verification": "missing" if value is None else "unreviewed",
    }


def field(name, value, page=None):
    return {"name": name, "fact": fact(value, page)}


def participant(entity_id, role, label, page, amounts=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, page),
        "name": fact(None),
        "smiles": fact(None),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": [field(k, v, page) for k, v in (amounts or [])],
    }


def q(number, unit):
    return {"number": number, "unit": unit}


def record(
    rid,
    page,
    kind,
    reactants,
    reagents,
    solvents,
    products,
    temperature,
    time,
    outcomes,
    *,
    yield_basis=None,
    extra_evidence=(),
    notes=(),
    unresolved=(),
):
    parts = []
    for i, label in enumerate(reactants, 1):
        parts.append(participant(f"reactant_{i}", "reactant", label, page))
    for i, item in enumerate(reagents, 1):
        label, equiv = item if isinstance(item, tuple) else (item, None)
        amounts = [("equivalents", q(equiv, "equiv"))] if equiv is not None else []
        parts.append(participant(f"reagent_{i}", "reagent", label, page, amounts))
    for i, label in enumerate(solvents, 1):
        parts.append(participant(f"solvent_{i}", "solvent", label, page))
    for i, label in enumerate(products, 1):
        parts.append(participant(f"product_{i}", "product", label, page))
    conditions = [
        field("temperature", temperature, page if temperature is not None else None),
        field("time", time, page if time is not None else None),
        field("yield_measurement_basis", yield_basis, page if yield_basis is not None else None),
        field("reaction_scale", None),
        field("concentration", None),
        field("atmosphere", None),
        field("workup", None),
        field("purification", None),
    ]
    evidence_ids = [ev(page, "text"), ev(page)]
    for eid in extra_evidence:
        if eid not in evidence_ids:
            evidence_ids.append(eid)
    default_unresolved = [
        "No supporting information is supplied or associated in this pilot.",
        "Participant structures are not machine-certified; SMILES remain null.",
        "Reaction scale, concentration, atmosphere, workup, and purification are missing unless explicitly printed on pages 1-6.",
    ]
    if yield_basis is None:
        default_unresolved.append("Yield measurement basis is not stated in the source-local presentation.")
    return {
        "record_id": f"{DOC}:{rid}",
        "document_id": DOC,
        "source_reaction_id": rid,
        "record_kind": kind,
        "status": "needs_review",
        "completeness": "partial",
        "evidence_ids": evidence_ids,
        "participants": parts,
        "steps": [{
            "step_id": "reaction",
            "participant_ids": [p["entity_id"] for p in parts],
            "conditions": conditions,
        }],
        "outcomes": [field(name, value, page) for name, value in outcomes],
        "notes": [fact(text, page) for text in notes],
        "review": {
            "method": "model",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": default_unresolved + list(unresolved),
        },
    }


records = []

# Page 1: Scheme 1, four condition rows for 1a + NaI -> E/Z-2aa.
scheme1 = [
    (1.2, "HOAc", q(40, "h"), "r.t.", 87, "4.3:1", None),
    (2, "THF", q(24, "h"), q(50, "°C"), 94, "5.7:1", "10 equiv HOAc added"),
    (2, "THF", q(4.5, "h"), "reflux", 94, "8.5:1", "10 equiv HOAc added"),
    (1.2, "HOAc", q(6.5, "h"), "reflux", 95, "9.4:1", None),
]
for i, (eq, solv, t, temp, y, ratio, note) in enumerate(scheme1, 1):
    records.append(record(
        f"scheme1_entry{i}", 1, "optimization_entry", ["1a (2,3-octadienoic acid)"],
        [("NaI", eq)], [solv], ["(E)-2aa", "(Z)-2aa"], temp, t,
        [("yield", q(y, "%")), ("Z/E_ratio", ratio)],
        yield_basis="1H NMR with CH2Br2 internal standard",
        notes=([note] if note else []),
    ))

# Page 2: Table 1. HOAc/reflux is the table-wide condition.
table1 = [
    ("1a", "LiBr·H2O", q(6.5, "h"), "2ab", 89, "70:30"),
    ("1a", "LiCl·H2O", q(6.5, "h"), "2ac", 87, "37.5:62.5"),
    ("1b", "NaI", q(7, "h"), "2ba", 99, "80:20"),
    ("1b", "LiBr·H2O", q(7, "h"), "2bb", 82, "64:36"),
    ("1b", "LiCl·H2O", q(7, "h"), "2bc", 87, "43:57"),
]
for i, (sub, mx, t, prod, y, ratio) in enumerate(table1, 1):
    extra = (ev(1),) if i in (3, 5) else ()
    records.append(record(
        f"table1_entry{i}", 2, "substrate_scope_entry", [sub], [(mx, None)], ["HOAc"],
        [f"(E)-{prod}", f"(Z)-{prod}"], "reflux", t,
        [("yield", q(y, "%")), ("Z/E_ratio", ratio)], extra_evidence=extra,
        notes=("Figure 1 provides NOESY-based stereochemical evidence." if extra else "",) if extra else (),
    ))

# Page 2: Scheme 2.
for i, (mx, t, prod, y) in enumerate([
    ("NaI", q(2.5, "h"), "2ca", 72),
    ("LiBr·H2O", q(3, "h"), "2cb", 61),
], 1):
    records.append(record(
        f"scheme2_entry{i}", 2, "substrate_scope_entry", ["1c"], [(mx, None)],
        ["CF3CO2H"], [prod], "r.t.", t, [("yield", q(y, "%"))],
    ))

# Page 2: Scheme 3; each HX row has ester and hydrolyzed-acid outcomes.
scheme3 = [
    ("HI", "I", q(4, "h"), "4aa", 40, "2.3:1", "2da", 48, "1.05:1"),
    ("HBr", "Br", q(24, "h"), "4ab", "trace", None, "2db", 58, "1.7:1"),
    ("HCl", "Cl", q(48, "h"), "4ac", "trace", None, "2dc", 83, "1:1.1"),
]
for i, (hx, x, t, ester, ey, er, acid, ay, ar) in enumerate(scheme3, 1):
    outs = [(f"yield_{ester}", q(ey, "%") if isinstance(ey, (int, float)) else ey)]
    if er is not None:
        outs.append((f"Z/E_ratio_{ester}", er))
    outs += [(f"yield_{acid}", q(ay, "%")), (f"Z/E_ratio_{acid}", ar)]
    records.append(record(
        f"scheme3_entry{i}", 2, "substrate_scope_entry", ["3a"], [(hx, None)],
        [], [ester, acid], q(80, "°C"), t, outs,
        notes=(f"HX hydrohalogenation with X = {x}; ester hydrolysis gives acid coproduct.",
               "Z/E ratios were determined by 1H NMR."),
    ))

# Page 3: Table 2.
table2 = [
    ("3a", "NaI", 2, "HOAc", q(80, "°C"), q(6, "h"), "4aa", 94, "4.7:1"),
    ("3a", "NaI", 1.5, "CF3CO2H", "r.t.", q(6, "h"), "4aa", 76, "1:2.5"),
    ("3a", "LiBr·H2O", 2, "HOAc", q(80, "°C"), q(24, "h"), "4ab", 83, "5.5:1"),
    ("3a", "LiCl·H2O", 2, "HOAc", q(80, "°C"), q(38, "h"), "4ac", 70, "1:1.3"),
    ("3b", "NaI", 1.5, "CF3CO2H", "r.t.", q(1, "h"), "4ba", 98, "1:3"),
    ("3b", "LiBr·H2O", 1.5, "CF3CO2H", "r.t.", q(2.5, "h"), "4bb", 90, "1:3"),
    ("3b", "LiBr·H2O", 1.5, "HOAc", q(80, "°C"), q(29, "h"), "4bb", 72, "1:1"),
    ("3b", "LiCl·H2O", 3, "CF3CO2H", "r.t.", q(54, "h"), None, 0, None),
    ("3b", "LiCl·H2O", 3, "CF3CO2H", "reflux", q(2.1, "h"), "4bc", 84, "1:3"),
]
for i, (sub, mx, eq, solv, temp, t, prod, y, ratio) in enumerate(table2, 1):
    products = [] if prod is None else [f"(E)-{prod}", f"(Z)-{prod}"]
    outs = [("yield", q(y, "%"))]
    if ratio is not None:
        outs.append(("Z/E_ratio", ratio))
    if prod is None:
        outs.append(("reaction_observed", False))
    extra = (ev(2),) if i in (1, 5) else ()
    records.append(record(
        f"table2_entry{i}", 3, "optimization_entry", [sub], [(mx, eq)], [solv],
        products, temp, t, outs, extra_evidence=extra,
        notes=(("Figure 2 provides NOESY-based stereochemical evidence.",) if extra else ()) +
              (("Table footnote: no reaction.",) if prod is None else ()),
    ))

# Page 3: Scheme 4, self-cyclization of fully substituted 3h.
for i, (solv, t, y) in enumerate([
    ("HOAc", q(17, "h"), 65),
    ("HOAc-CF3CO2H", q(10, "min"), 67),
    ("CF3CO2H", q(10, "min"), 57),
], 1):
    records.append(record(
        f"scheme4_entry{i}", 3, "optimization_entry", ["3h"], [("LiBr", 2)],
        [solv], ["6h"], q(80, "°C"), t, [("yield_6h", q(y, "%"))],
        notes=("Self-cyclization to butenolide 6h; hydrohalogenation product was not shown.",),
    ))

# Page 4: Table 3. Header temperature is 80 °C except footnoted entry 4 at 40 °C.
table3 = [
    ("NaI", 1.5, "3c", "HOAc", q(24, "h"), "4ca", 41, "4′ca", 10, "isolated"),
    ("NaI", 4, "3c", "HOAc", q(72, "h"), "4ca", 53, "4′ca", 14, "1H NMR"),
    ("LiBr·H2O", 1.3, "3c", "HOAc", q(72, "h"), "4cb", "<5", "4′cb", "<5", "isolated"),
    ("LiBr·H2O", 1.5, "3c", "HOAc", q(120, "h"), "4cb", "<5", "4′cb", "<5", "isolated"),
    ("LiCl·H2O", 1.8, "3c", "HOAc", q(74, "h"), "4cc", "~10", "4′cc", "~5", "isolated"),
    ("NaI", 3, "3c", "HOAc-CF3CO2H", q(4, "h"), "4ca", 95, None, None, "isolated"),
    ("LiBr·H2O", 3, "3c", "HOAc-CF3CO2H", q(12, "h"), "4cb", 80, None, None, "isolated"),
    ("NaI", 2, "3c", "CF3CO2H", q(10, "min"), "4ca", 90, None, None, "isolated"),
    ("LiBr·H2O", 2, "3c", "CF3CO2H", q(40, "min"), "4cb", 88, None, None, "isolated"),
    ("NaI", 2, "3d", "CF3CO2H", q(20, "min"), "4da", 98, None, None, "isolated"),
    ("LiBr·H2O", 2, "3d", "CF3CO2H", q(50, "min"), "4db", 76, None, None, "isolated"),
    ("LiCl·H2O", 3, "3d", "CF3CO2H", q(10, "h"), "4dc", 63, None, None, "isolated"),
]
for i, (mx, eq, sub, solv, t, p1, y1, p2, y2, basis) in enumerate(table3, 1):
    prods = [p1] + ([p2] if p2 else [])
    outs = [(f"yield_{p1}", q(y1, "%") if isinstance(y1, (int, float)) else y1)]
    if p2:
        outs.append((f"yield_{p2}", q(y2, "%") if isinstance(y2, (int, float)) else y2))
    else:
        outs.append(("alpha_beta_unsaturated_product_observed", False))
    records.append(record(
        f"table3_entry{i}", 4, "optimization_entry", [sub], [(mx, eq)], [solv], prods,
        q(40, "°C") if i == 4 else q(80, "°C"), t, outs, yield_basis=basis,
        notes=(("Table footnote: alpha,beta-unsaturated product 4′ was not observed.",) if p2 is None else ()),
    ))

# Page 4: Scheme 5, five cross-couplings.
scheme5 = [
    ("4ca", "n-BuZnBr", ["Pd(PPh3)4 (5 mol%)"], "THF", q(3, "h"), "7a", 90, None),
    ("4ca", "PhZnBr", ["Pd(PPh3)4 (5 mol%)"], "THF", q(6, "h"), "7b", 70, None),
    ("4ca", "phenylacetylene", ["PdCl2(PPh3)2 (5 mol%)", "CuI (10 mol%)", "Et3N"], None, q(6.5, "h"), "7c", 85, None),
    ("4aa (E/Z = 2.5:1)", "PhZnBr", ["Pd(PPh3)4 (5 mol%)"], "THF", q(8, "h"), "7d", 76, "2.5:1"),
    ("4aa (E/Z = 2.5:1)", "phenylacetylene", ["PdCl2(PPh3)2 (5 mol%)", "CuI (10 mol%)", "Et3N"], None, q(6, "h"), "7e", 82, "2.5:1"),
]
for i, (sub, partner, agents, solv, t, prod, y, ratio) in enumerate(scheme5, 1):
    outs = [("yield", q(y, "%"))] + ([("E/Z_ratio", ratio)] if ratio else [])
    records.append(record(
        f"scheme5_entry{i}", 4, "reported_experiment", [sub, partner],
        [(x, None) for x in agents], [solv] if solv else [], [prod], None,
        t, outs,
        unresolved=(("Reaction solvent is not printed on the Scheme 5 arrow.",) if solv is None else ()) +
                   ("Reaction temperature is not printed on the Scheme 5 arrow.",),
    ))

# Page 4: Scheme 6, two couplings of 9ca.
for i, (partner, agents, solv, t, prod, y) in enumerate([
    ("PhZnBr", ["Pd(PPh3)4 (5 mol%)"], "THF", q(8, "h"), "7f", 87),
    ("phenylacetylene", ["PdCl2(PPh3)2 (5 mol%)", "CuI (10 mol%)", "Et3N"], None, q(19, "h"), "7g", 83),
], 1):
    records.append(record(
        f"scheme6_entry{i}", 4, "reported_experiment", ["9ca", partner],
        [(x, None) for x in agents], [solv] if solv else [], [prod], "r.t.", t,
        [("yield", q(y, "%"))],
        unresolved=(("Reaction solvent is not printed on the Scheme 6 arrow.",) if solv is None else ()),
    ))

# Page 5: Table 4, including isolated butenolide coproducts from footnotes.
table4 = [
    ("3e", "NaI", 1.5, "CF3CO2H", "r.t.", q(1.1, "h"), "4ea", 78, "3:2", None),
    ("3e", "LiBr·H2O", 1.5, "CF3CO2H", "r.t.", q(3, "h"), "4eb", 89, "3:2", None),
    ("3e", "LiCl·H2O", 3, "CF3CO2H", "r.t.", q(54, "h"), None, 0, None, None),
    ("3e", "LiCl·H2O", 3, "CF3CO2H", "reflux", q(17, "h"), "4ec", 63, "3:2", ("6e", 19)),
    ("3f", "NaI", 1.5, "CF3CO2H", "r.t.", q(50, "min"), "4fa", 78, "1:1", None),
    ("3f", "NaI", 2, "CF3CO2H", "reflux", q(10, "min"), "4fa", 58, "1:1.2", None),
    ("3f", "LiBr·H2O", 1.5, "CF3CO2H", "r.t.", q(2.5, "h"), "4fb", 74, "1:1", None),
    ("3f", "LiBr·H2O", 2, "CF3CO2H", "reflux", q(20, "min"), "4fb", 71, "1:1.3", None),
    ("3f", "LiBr·H2O", 2, "CF3CO2H-HOAc", q(80, "°C"), q(20, "min"), "4fb", 63, "1:2.2", None),
    ("3f", "LiCl·H2O", 4, "CF3CO2H", "reflux", q(40, "min"), "4fc", 55, "1.5:1", None),
    ("3f", "LiCl·H2O", 3, "CF3CO2H", "r.t.", q(2, "h"), "4fc", 39, "2:1", None),
    ("3g", "NaI", 2, "CH3CO2H", q(80, "°C"), q(4, "h"), "4ga", 23, None, ("6g", 15)),
    ("3g", "LiBr·H2O", 2, "CH3CO2H", q(80, "°C"), q(15, "h"), "4gb", 23, None, ("6g", 42)),
]
for i, (sub, mx, eq, solv, temp, t, prod, y, ratio, byp) in enumerate(table4, 1):
    products = [] if prod is None else [prod]
    outs = [("yield", q(y, "%"))]
    if ratio:
        outs.append(("E/Z_ratio", ratio))
    if prod is None:
        outs.append(("reaction_observed", False))
    if byp:
        products.append(byp[0])
        outs.append((f"yield_{byp[0]}", q(byp[1], "%")))
    records.append(record(
        f"table4_entry{i}", 5, "substrate_scope_entry", [sub], [(mx, eq)], [solv],
        products, temp, t, outs, yield_basis="isolated",
        notes=(("Butenolide was isolated as a coproduct.",) if byp else ()) +
              (("Table reports 0%; no hydrohalogenation product was obtained.",) if prod is None else ()),
    ))

# Page 6: Table 5, 18 dienamide hydrohalogenations.
table5 = [
    ("8a", "NaI", "HOAc", q(70, "°C"), q(4, "h"), [("9aa", 87)]),
    ("8a", "LiBr·H2O", "HOAc", q(70, "°C"), q(4, "h"), [("9ab", 96)]),
    ("8a", "LiCl·H2O", "HOAc", q(70, "°C"), q(7, "h"), [("9ac", 75)]),
    ("8b", "NaI", "HOAc", "r.t.", q(4, "h"), [("(E)-9ba", 36), ("(Z)-9ba", 62)]),
    ("8b", "LiBr·H2O", "HOAc", q(70, "°C"), q(22, "h"), [("(E)-9bb", 34), ("(Z)-9bb", 56)]),
    ("8b", "LiCl·H2O", "HOAc", q(70, "°C"), q(22, "h"), [("(E)-9bc", 56), ("(Z)-9bc", 23)]),
    ("8b", "NaI", "CF3CO2H", "r.t.", q(0.5, "h"), [("(E)-9ba", 64), ("(Z)-9ba", 34)]),
    ("8b", "LiBr·H2O", "CF3CO2H", q(70, "°C"), q(4, "h"), [("(E)-9bb", 48), ("(Z)-9bb", 21)]),
    ("8b", "LiCl·H2O", "CF3CO2H", q(70, "°C"), q(26, "h"), [("(E)-9bc", 15), ("(Z)-9bc", 8)]),
    ("8c", "NaI", "HOAc", q(70, "°C"), q(18, "h"), [("9ca", 97)]),
    ("8c", "LiBr·H2O", "HOAc", q(70, "°C"), q(23, "h"), [("9cb", 93)]),
    ("8c", "LiCl·H2O", "HOAc", q(70, "°C"), q(23, "h"), [("9cc", 91)]),
    ("8d", "NaI", "CF3CO2H", "r.t.", q(1, "h"), [("9da", 97)]),
    ("8d", "LiBr·H2O", "CF3CO2H", "r.t.", q(24, "h"), [("9db", 99)]),
    ("8d", "LiCl·H2O", "CF3CO2H", q(40, "°C"), q(70, "h"), [("9dc", 87)]),
    ("8d", "aqueous HI", "aqueous HI", "r.t.", q(11, "h"), [("9da", 77)]),
    ("8d", "aqueous HBr", "aqueous HBr", "r.t.", q(11, "h"), [("9db", 86)]),
    ("8d", "aqueous HCl", "aqueous HCl", "r.t.", q(11, "h"), [("9dc", 94)]),
]
for i, (sub, mx, solv, temp, t, prods) in enumerate(table5, 1):
    products = [x[0] for x in prods]
    outs = [(f"yield_{p.replace('(', '').replace(')', '')}", q(y, "%")) for p, y in prods]
    extra = (ev(3),) if i in (4, 7) else ()
    records.append(record(
        f"table5_entry{i}", 6, "substrate_scope_entry", [sub], [(mx, None)], [solv],
        products, temp, t, outs, extra_evidence=extra,
        notes=(("Figure 3 provides NOESY-based assignment of (E)-9ba and (Z)-9ba.",) if extra else ()),
    ))

# Page 6: Scheme 7, two couplings of nitrile 11ba.
for i, (partner, agents, solvents, t, prod, y) in enumerate([
    ("PhZnBr", ["Pd(PPh3)4 (5 mol%)"], ["THF"], q(7, "h"), "7h", 74),
    ("phenylacetylene", ["PdCl2(PPh3)2 (5 mol%)", "CuI (10 mol%)", "K2CO3"], [], q(20, "h"), "7i", 91),
], 1):
    records.append(record(
        f"scheme7_entry{i}", 6, "reported_experiment", ["11ba", partner],
        [(x, None) for x in agents], solvents, [prod], "r.t.", t,
        [("yield", q(y, "%"))],
        unresolved=(("Reaction solvent is not printed on the Scheme 7 arrow.",) if not solvents else ()),
    ))

assert len(records) == 78, len(records)

page_record_ids = {p: [] for p in range(1, 7)}
for rec in records:
    for eid in rec["evidence_ids"]:
        marker = f"{DOC}:page"
        if eid.startswith(marker):
            page = int(eid[len(marker):].split(":", 1)[0])
            if page in page_record_ids and rec["record_id"] not in page_record_ids[page]:
                page_record_ids[page].append(rec["record_id"])

coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1,
            "state": "attempted",
            "regions": [
                {"region": "right column, Scheme 1 and four-row condition table", "finding": "Four current-paper NaI hydrohalogenation optimization experiments for 1a were extracted row by row.", "evidence_ids": [ev(1)]},
                {"region": "right column, Figure 1", "finding": "NOE/NOESY stereochemical evidence for 2ba and 2bc; not an independent reaction.", "evidence_ids": [ev(1)]},
                {"region": "left column, abstract/introduction", "finding": "Article scope and prior-work context; no extra current experiment fabricated from citations.", "evidence_ids": [ev(1, "text"), ev(1)]},
            ],
            "record_ids": page_record_ids[1],
            "unresolved": ["Scheme 1 structures remain unverified and have null SMILES.", "No SI is supplied or explicitly associated."],
        },
        {
            "page": 2,
            "state": "attempted",
            "regions": [
                {"region": "top, Table 1", "finding": "Five alkadienoic-acid hydrohalogenation rows extracted separately.", "evidence_ids": [ev(2)]},
                {"region": "lower left, Scheme 2", "finding": "Two current-paper 1c hydrohalogenation rows extracted separately.", "evidence_ids": [ev(2)]},
                {"region": "lower right, Scheme 3", "finding": "Three HX rows extracted, each retaining ester and hydrolyzed-acid outcomes and NMR Z/E ratios.", "evidence_ids": [ev(2)]},
                {"region": "lower left, Figure 2", "finding": "NOESY stereochemical evidence for 4aa and 4ba; linked to matching Table 2 records, not counted as a synthesis.", "evidence_ids": [ev(2)]},
            ],
            "record_ids": page_record_ids[2],
            "unresolved": ["Table 1 and Schemes 2-3 do not state a source-local yield measurement basis.", "Participant structures remain unverified."],
        },
        {
            "page": 3,
            "state": "attempted",
            "regions": [
                {"region": "top, Table 2", "finding": "Nine optimization rows extracted; entry 8 preserves the explicit 0% no-reaction result.", "evidence_ids": [ev(3)]},
                {"region": "middle right, Scheme 4", "finding": "Three LiBr/solvent rows for self-cyclization of 3h to 6h extracted separately.", "evidence_ids": [ev(3)]},
                {"region": "middle left, Figure 3", "finding": "NOESY assignment of E/Z-9ba; linked to matching Table 5 records and not counted independently.", "evidence_ids": [ev(3)]},
                {"region": "bottom prose", "finding": "Discussion of Tables 3-5 and prior literature; no additional row invented from prose.", "evidence_ids": [ev(3, "text"), ev(3)]},
            ],
            "record_ids": page_record_ids[3],
            "unresolved": ["Table 2 and Scheme 4 yield bases are not stated on this page.", "Scheme 4 reaction-solvent compositions are retained as printed without inferred proportions."],
        },
        {
            "page": 4,
            "state": "attempted",
            "regions": [
                {"region": "top, Table 3", "finding": "Twelve 2-substituted allenoate rows extracted separately, including bounded/approximate yields and explicit absence of 4′ in entries 6-12.", "evidence_ids": [ev(4)]},
                {"region": "lower left, Scheme 5", "finding": "Five distinct Pd-catalyzed couplings extracted arrow by arrow.", "evidence_ids": [ev(4)]},
                {"region": "lower right, Scheme 6", "finding": "Two distinct couplings of 9ca extracted arrow by arrow.", "evidence_ids": [ev(4)]},
            ],
            "record_ids": page_record_ids[4],
            "unresolved": ["Scheme 5/6 arrows do not print a solvent for the Sonogashira rows.", "Coupling yield bases and complete workups are not stated in pages 1-6."],
        },
        {
            "page": 5,
            "state": "attempted",
            "regions": [
                {"region": "top, Table 4", "finding": "Thirteen dienoate rows extracted, including the 0% result and butenolide coproduct yields from footnotes.", "evidence_ids": [ev(5)]},
                {"region": "lower left, Figure 4", "finding": "NOESY evidence for 11ca/11da, but the corresponding Table 6 is on page 7 and is outside this session; no page-5 synthesis record fabricated.", "evidence_ids": [ev(5)]},
                {"region": "lower prose", "finding": "Dienenitrile discussion and isomerization statement refer to Table 6 outside the covered pages.", "evidence_ids": [ev(5, "text"), ev(5)]},
            ],
            "record_ids": page_record_ids[5],
            "unresolved": ["Dienenitrile Table 6 rows are outside pages 1-6 and were not extracted in this session.", "Figure 4 structures remain unverified."],
        },
        {
            "page": 6,
            "state": "attempted",
            "regions": [
                {"region": "top and middle, Table 5", "finding": "Eighteen dienamide hydrohalogenation rows extracted separately, retaining separate E/Z yields where printed.", "evidence_ids": [ev(6)]},
                {"region": "lower left, Scheme 7", "finding": "Two distinct Pd-catalyzed couplings of 11ba extracted arrow by arrow.", "evidence_ids": [ev(6)]},
                {"region": "lower right prose", "finding": "Phosphine-oxide discussion points to Scheme 8/Table 7 on later pages; no experiment was fabricated from the summary prose alone.", "evidence_ids": [ev(6, "text"), ev(6)]},
            ],
            "record_ids": page_record_ids[6],
            "unresolved": ["Table 5 and Scheme 7 yield bases are not stated on page 6.", "Table 7 and Scheme 8 are outside this session.", "Scheme 7 does not print a solvent for the phenylacetylene row."],
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
    if task.get("document_id") == DOC and task.get("evidence_id") in {ev(p, "text") for p in range(1, 7)}:
        task["state"] = "attempted"
        task["reason"] = "Original page image and page text inspected; records and coverage ledger generated for this session."
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"records": len(records), "coverage_pages": [p["page"] for p in coverage["pages"]]}, ensure_ascii=False))
