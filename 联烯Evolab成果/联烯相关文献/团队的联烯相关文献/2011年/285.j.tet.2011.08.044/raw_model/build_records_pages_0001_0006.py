#!/usr/bin/env python3
"""Build evidence-linked machine records for source.pdf pages 1--6.

This is a source transcription helper, not a chemistry validator.  It deliberately
leaves structures unverified and the records in candidate state for the merge tool.
"""
from __future__ import annotations

import json
from pathlib import Path

DOC = "doc_e07c8acc21fad353"
ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).with_name("records_pages_0001_0006.json")
COVERAGE = ROOT / "coverage" / "pages_0001_0006.json"


def evidence(*pages: int) -> list[str]:
    return [f"{DOC}:page{p}:{kind}" for p in pages for kind in ("text", "image")]


def fact(value, ev):
    return {"value": value, "evidence_ids": list(ev) if value is not None else [],
            "verification": "unreviewed" if value is not None else "missing"}


def q(number, unit, **extra):
    return {"number": number, "unit": unit, **extra}


def qr(lo, hi, unit, raw):
    return {"minimum": lo, "maximum": hi, "unit": unit, "raw_text": raw}


def field(name, value, ev, targets=None):
    result = {"name": name, "fact": fact(value, ev)}
    if targets:
        result["target_entity_ids"] = list(targets)
    return result


def participant(entity_id, role, label, ev, amounts=(), name=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, ev),
        "name": fact(name, ev) if name else fact(None, ()),
        "smiles": fact(None, ()),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": list(amounts),
    }


def amount(name, value, ev):
    return field(name, value, ev)


def record(rid, kind, pages, participants, conditions, outcomes, notes=(), unresolved=()):
    ev = evidence(*pages)
    return {
        "record_id": f"{DOC}:{rid}",
        "document_id": DOC,
        "source_reaction_id": rid,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": ev,
        "participants": participants,
        "steps": [{
            "step_id": "reaction",
            "participant_ids": [p["entity_id"] for p in participants],
            "conditions": conditions,
        }],
        "outcomes": outcomes,
        "notes": [fact(x, ev) for x in notes],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": [
                "Structures are transcribed by source labels; SMILES are omitted and structures remain unverified.",
                "Supporting-information association is unestablished; no SI-derived details were used.",
                *unresolved,
            ],
        },
    }


def chemical(entity_id, role, label, ev, eq=None, loading=None):
    amounts = []
    if eq is not None:
        amounts.append(amount("equivalents", q(eq, "equiv"), ev))
    if loading is not None:
        amounts.append(amount("catalyst_loading", q(loading, "mol%"), ev))
    return participant(entity_id, role, label, ev, amounts)


records = []

# Page 1: the only arrow is a generic two-stage route, not an individual batch.
ev = evidence(1)
parts = [
    chemical("generic_allenol_1", "reactant", "generic 2,3-allenol 1", ev),
    chemical("generic_RfI", "reactant", "RfI", ev),
    chemical("generic_EZ_3", "product", "E/Z-3", ev),
    chemical("generic_Z_3", "product", "Z-3", ev),
    chemical("propargyl_alcohol_4", "reactant", "propargyl alcohol 4", ev),
    chemical("generic_E_5", "product", "E-5", ev),
    chemical("Na2S2O4", "reagent", "Na2S2O4", ev),
    chemical("Na2CO3", "reagent", "Na2CO3", ev),
    chemical("PdPPh3_2Cl2", "catalyst", "Pd(PPh3)2Cl2", ev),
    chemical("CuI", "catalyst", "CuI", ev),
    chemical("Et2NH", "reagent", "Et2NH", ev),
    chemical("MeOH", "solvent", "CH3OH", ev),
    chemical("H2O", "solvent", "H2O", ev),
    chemical("CH3CN", "solvent", "CH3CN", ev),
]
records.append(record(
    "scheme1_general_route", "general_scheme", (1,), parts,
    [field("stage_1_temperature", qr(40, 45, "°C", "40-45 °C"), ev),
     field("stage_2_temperature", q(0, "°C"), ev)], [],
    notes=("Scheme 1 is a generic two-stage route and has no batch scale or product-specific yield.",),
    unresolved=("Generic R groups prevent fully specified structures.",),
))


def radical_parts(substrate, product, ev, rf="2a", base="Na2CO3", x=2.0,
                  product_labels=None):
    product_labels = product_labels or [(product, product)]
    parts = [chemical(substrate, "reactant", substrate, ev),
             chemical(rf, "reactant", f"n-C{'4F9I' if rf == '2a' else '6F13I'} {rf}", ev, eq=x),
             chemical("Na2S2O4", "reagent", "Na2S2O4", ev, eq=x),
             chemical("base", "reagent", base, ev, eq=x),
             chemical("MeOH", "solvent", "CH3OH", ev),
             chemical("H2O", "solvent", "H2O", ev)]
    parts += [chemical(pid, "product", label, ev) for pid, label in product_labels]
    return parts


def radical_conditions(ev, time=q(1, "h"), temp=None, conc=None, solvent_ratio="3/1",
                       atmosphere=True):
    out = [field("reaction_time", time, ev)]
    if temp is not None:
        out.append(field("temperature", temp, ev))
    if conc is not None:
        out.append(field("concentration", conc, ev))
    out.append(field("solvent_ratio_CH3OH_H2O", solvent_ratio, ev))
    if atmosphere:
        out.append(field("atmosphere", "air", evidence(4)))
    return out


# Page 2, Table 1: base screen, eleven independent rows.
table1 = [
    (1, "NaHCO3", 34, "80/20", None, "isolated"),
    (2, "(i-Pr)2NH", 17, "81/19", 12, "isolated"),
    (3, "Et3N", 28, "75/25", 12, "NMR"),
    (4, "Li2CO3", 29, "80/20", None, "isolated"),
    (5, "Na2CO3", 39, "80/20", None, "isolated"),
    (6, "K2CO3", 39, "77/23", None, "isolated"),
    (7, "Cs2CO3", 32, "80/20", None, "isolated"),
    (8, "Na3PO4", 35, "80/20", None, "isolated"),
    (9, "NaOH", 39, "79/21", None, "isolated"),
    (10, "KOH", 28, "76/24", None, "isolated"),
    (11, "Cy2NH", "not determined", "table dash (—)", None, "not determined"),
]
for n, base, yld, ratio, recovery, basis in table1:
    ev = evidence(2)
    sub_amounts = []
    rf_amounts = [amount("equivalents", q(1.5, "equiv"), ev)]
    dith_amounts = [amount("equivalents", q(1.5, "equiv"), ev)]
    base_amounts = [amount("equivalents", q(1.5, "equiv"), ev)]
    if n == 1:
        sub_amounts = [amount("amount", q(0.3, "mmol"), ev)]
        rf_amounts = [amount("amount", q(0.2, "mmol"), ev)]
        dith_amounts = [amount("amount", q(0.2, "mmol"), ev)]
        base_amounts = [amount("amount", q(0.2, "mmol"), ev)]
    parts = [participant("1a", "reactant", "1a", ev, sub_amounts),
             participant("2a", "reactant", "n-C4F9I 2a", ev, rf_amounts),
             participant("Na2S2O4", "reagent", "Na2S2O4", ev, dith_amounts),
             participant("base", "reagent", base, ev, base_amounts),
             chemical("dioxane", "solvent", "1,4-dioxane", ev),
             chemical("H2O", "solvent", "H2O", ev),
             chemical("3a", "product", "E/Z-3a", ev)]
    outcomes = [field(("nmr_yield_3a" if basis == "NMR" else "isolated_yield_3a"),
                      q(yld, "%") if isinstance(yld, (int, float)) else yld, ev, ["3a"]),
                field("E_Z_ratio", ratio, ev, ["3a"]),
                field("yield_measurement_basis", basis, ev, ["3a"])]
    if recovery is not None:
        outcomes.append(field("recovered_starting_material_yield", q(recovery, "%"), ev, ["1a"]))
    notes = ("Cy2NH gave a complicated reaction.",) if n == 11 else ()
    records.append(record(f"table1_entry{n}", "optimization_entry", (2,), parts,
                          [field("temperature", "r.t.", ev),
                           field("reaction_time", qr(1, 1.5, "h", "1-1.5 h"), ev),
                           field("solvent_ratio_1_4_dioxane_H2O", "3/1", ev)],
                          outcomes, notes=notes))


# Page 2, Table 2: solvent screen. Entry 19 is the same standard 3a batch
# reported again in Table 3 and in the detailed procedure on page 5.
table2 = [
    (1, "benzene", "NR", "table dash (—)"), (2, "toluene", "NR", "table dash (—)"),
    (3, "hexane", "NR", "table dash (—)"), (4, "ethyl acetate", "NR", "table dash (—)"),
    (5, "DMSO", None, "table dash (—)"), (6, "DMF", 20, "82/18"),
    (7, "DMA", 16, "84/16"), (8, "CH3CN", 30, "79/21"),
    (9, "pyridine", 36, "80/20"), (10, "acetone", 34, "82/18"),
    (11, "EtOH", 32, "79/21"), (12, "glycol", "trace", "table dash (—)"),
    (13, "i-butanol", "NR", "table dash (—)"), (14, "MeOH", 46, "80/20"),
    (15, "MeOH", 44, "78/22"), (16, "MeOH", 27, "79/21"),
    (17, "MeOH", 35, "81/19"), (18, "MeOH", 42, "78/22"),
    (19, "MeOH", 48, "75/25"), (20, "i-PrOH", 5, "table dash (—)"),
]
for n, solvent, yld, ratio in table2:
    pages = (2, 4, 5) if n == 19 else (2,)
    ev = evidence(*pages)
    solvent_ratio = "3/1"
    conc = q(0.2, "M")
    temp = "r.t."
    rf_eq = 1.5
    time = None
    if n == 15:
        conc = q(0.4, "M")
    if n == 16:
        conc = q(0.1, "M")
    if n == 17:
        solvent_ratio = "2/1"
    if n == 18:
        solvent_ratio = "4/1"
    if n in (19, 20):
        temp = qr(40, 45, "°C", "40-45 °C")
        rf_eq = 2.0
    if n == 19:
        time = q(1, "h")
    parts = [chemical("1a", "reactant", "1a", ev),
             chemical("2a", "reactant", "n-C4F9I 2a", ev, eq=rf_eq),
             chemical("Na2S2O4", "reagent", "Na2S2O4", ev, eq=2.0 if n == 19 else 1.5),
             chemical("Na2CO3", "reagent", "Na2CO3", ev, eq=2.0 if n == 19 else 1.5),
             chemical("organic_solvent", "solvent", solvent, ev),
             chemical("H2O", "solvent", "H2O", ev),
             chemical("3a", "product", "E/Z-3a", ev)]
    outcomes = []
    if n == 5:
        outcomes.append(field("reaction_result", "mixture of 3a, 1a, and unknown products after flash chromatography", ev))
    else:
        name = "nmr_yield_3a" if n == 20 else "isolated_yield_3a"
        outcomes.append(field(name, q(yld, "%") if isinstance(yld, (int, float)) else yld, ev, ["3a"]))
    outcomes.append(field("E_Z_ratio", ratio, ev, ["3a"]))
    if n in (14, 17):
        outcomes.append(field("recovered_starting_material_yield", q(1.4, "%"), ev, ["1a"]))
    if n == 16:
        outcomes.append(field("recovered_starting_material_yield", q(3, "%"), ev, ["1a"]))
    if n == 18:
        outcomes.append(field("recovered_starting_material_yield", q(2.5, "%"), ev, ["1a"]))
    if n == 20:
        outcomes.append(field("recovered_starting_material_yield", q(45, "%"), ev, ["1a"]))
    conditions = [field("temperature", temp, ev), field("concentration", conc, ev),
                  field("solvent_ratio_organic_solvent_H2O", solvent_ratio, ev)]
    if time is not None:
        conditions.append(field("reaction_time", time, evidence(5)))
    rid = "table2_entry19_standard_3a" if n == 19 else f"table2_entry{n}"
    rec = record(rid, "optimization_entry", pages, parts, conditions, outcomes,
                 unresolved=("Table 2 does not report reaction duration for this row.",) if n != 19 else ())
    records.append(rec)


# Page 2, Table 3 entries 2--4. Entry 1 is already the standard 3a record above.
table3 = [(2, "1b", "3b", 40, "68/32", q(1, "h")),
          (3, "1c", "3c", 43, "75/25", q(1, "h")),
          (4, "1m", "3p", 34, "76/24", q(1.5, "h"))]
for n, substrate, product, yld, ratio, duration in table3:
    ev = evidence(2, 5)
    parts = radical_parts(substrate, product, ev)
    outcomes = [field(f"isolated_yield_{product}", q(yld, "%"), ev, [product]),
                field("E_Z_ratio", ratio, ev, [product])]
    records.append(record(f"table3_entry{n}_{product}", "substrate_scope_entry", (2, 5), parts,
                          radical_conditions(ev, duration, qr(40, 45, "°C", "40-45 °C")), outcomes,
                          notes=("The E and Z isomers were reported as inseparable by flash chromatography.",)))


# Page 2 equations 1 and 2: explicit failed reactions.
for tag, substrate, duration, result, recovery in [
    ("eq1_failed_1q", "1q", q(1.5, "h"), "complicated reaction", None),
    ("eq2_failed_1r", "1r", q(1, "h"), "no major products", 35),
]:
    ev = evidence(2)
    parts = radical_parts(substrate, f"expected_product_from_{substrate}", ev)
    outcomes = [field("reaction_result", result, ev)]
    if recovery is not None:
        outcomes.append(field("recovered_starting_material_yield", q(recovery, "%"), ev, [substrate]))
    records.append(record(tag, "reported_experiment", (2,), parts,
                          radical_conditions(ev, duration, qr(40, 45, "°C", "40-45 °C")), outcomes,
                          unresolved=("The expected product is depicted generically and was not isolated.",)))


# Page 3, Table 4: four optimization rows. Entry 3 is detailed on page 5.
table4 = [(1, 1.5, 1.5, "r.t.", 0.2, 23, 27, 11),
          (2, 2.0, 2.0, "r.t.", 0.4, 33, 31, 1.4),
          (3, 2.0, 2.0, qr(40, 45, "°C", "40-45 °C"), 0.4, 31, 35, None),
          (4, 2.5, 2.5, qr(40, 45, "°C", "40-45 °C"), 0.4, 29, 31, None)]
for n, x, rf_eq, temp, conc, ey, zy, recovery in table4:
    pages = (3, 5) if n == 3 else (3,)
    ev = evidence(*pages)
    parts = radical_parts("1d", "3d", ev, x=x,
                          product_labels=[("E_3d", "E-3d"), ("Z_3d", "Z-3d")])
    # RfI can differ from x, though it is equal in the four reported rows.
    next(p for p in parts if p["entity_id"] == "2a")["amounts"] = [amount("equivalents", q(rf_eq, "equiv"), ev)]
    outcomes = [field("isolated_yield_E_3d", q(ey, "%"), ev, ["E_3d"]),
                field("isolated_yield_Z_3d", q(zy, "%"), ev, ["Z_3d"])]
    if recovery is not None:
        outcomes.append(field("recovered_starting_material_yield", q(recovery, "%"), ev, ["1d"]))
    records.append(record(f"table4_entry{n}", "optimization_entry", pages, parts,
                          [field("reaction_time", q(1.5, "h"), ev),
                           field("temperature", temp, ev), field("concentration", q(conc, "M"), ev),
                           field("solvent_ratio_CH3OH_H2O", "3/1", ev),
                           field("atmosphere", "air", evidence(4))], outcomes,
                          unresolved=("The visual table repeats E-3d in both yield subheaders; product identities were assigned from the reaction drawing and adjacent prose as E-3d and Z-3d.",)))


# Page 3, Table 5: fifteen substrate-scope experiments. Detailed starts on pages 5--6
# are linked to entries 1--3 without importing continuation data from page 7.
table5 = [
    (1, "1d", "3d", "2a", 69, "46/54", "Ph", "H"),
    (2, "1e", "3e", "2a", 61, "41/59", "4-CH3C6H4", "H"),
    (3, "1f", "3f", "2a", 69, "44/56", "4-FC6H4", "H"),
    (4, "1g", "3g", "2a", 77, "38/62", "n-C4H9", "H"),
    (5, "1h", "3h", "2a", 68, "39/61", "n-C5H11", "H"),
    (6, "1i", "3i", "2a", 60, "37/63", "n-C6H13", "H"),
    (7, "1j", "3j", "2a", 60, "43/57", "Bn", "H"),
    (8, "1n", "3q", "2a", 67, "40/60", "i-C3H7", "H"),
    (9, "1o", "3r", "2a", 83, "37/63", "t-C4H9", "H"),
    (10, "1g", "3k", "2b", 73, "38/62", "n-C4H9", "H"),
    (11, "1h", "3l", "2b", 61, "37/63", "n-C5H11", "H"),
    (12, "1i", "3m", "2b", 83, "36/64", "n-C6H13", "H"),
    (13, "1k", "3n", "2a", (56, 6), "91/9", "Ph", "CH3"),
    (14, "1p", "3s", "2a", 49, "87/13", "n-C4H9", "n-C4H9"),
    (15, "1l", "3o", "2a", (59, 6), "90/10", "-(CH2)5-", "cyclic"),
]
for n, substrate, product, rf, yld, ratio, r1, r2 in table5:
    pages = (3, 5, 6) if n == 1 else ((3, 6) if n in (2, 3) else (3,))
    ev = evidence(*pages)
    labels = [(product, f"E/Z-{product}")]
    if n in (13, 14, 15):
        labels = [(f"E_{product}", f"E-{product}"), (f"Z_{product}", f"Z-{product}")]
    parts = radical_parts(substrate, product, ev, rf=rf, product_labels=labels)
    outcomes = []
    if isinstance(yld, tuple):
        outcomes += [field(f"isolated_yield_E_{product}", q(yld[0], "%"), ev, [f"E_{product}"]),
                     field(f"isolated_yield_Z_{product}", q(yld[1], "%"), ev, [f"Z_{product}"])]
    elif n == 14:
        outcomes.append(field(f"isolated_yield_E_{product}", q(yld, "%"), ev, [f"E_{product}"]))
        outcomes.append(field(f"isolated_yield_Z_{product}", "not isolated in pure form", ev, [f"Z_{product}"]))
    else:
        outcomes.append(field(f"isolated_yield_E_Z_{product}", q(yld, "%"), ev, [product]))
    outcomes.append(field("E_Z_ratio", ratio, ev, [p[0] for p in labels]))
    duration = q(50, "min") if n == 1 else q(1, "h")
    notes = [f"Table 5 substituent mapping: R1={r1}; R2={r2}."]
    unresolved = []
    if n == 14:
        notes.append("The E/Z ratio was determined by 1H NMR of the crude product.")
    if n == 3:
        unresolved.append("Section 4.2.8 continues on page 7; no page-7 batch quantities were imported or claimed as covered.")
    records.append(record(f"table5_entry{n}_{product}", "substrate_scope_entry", pages, parts,
                          radical_conditions(ev, duration, qr(40, 45, "°C", "40-45 °C")),
                          outcomes, notes=notes, unresolved=unresolved))


def kinetic_parts(substrate, ev, rf_label, r_label, substrate_eq=None, reagent_eq=0.7,
                  pd=5.0, cu=5.0, products=None):
    products = products or [("Z_3", "Z-3"), ("E_5", "E-5")]
    subs_amounts = [] if substrate_eq is None else [amount("equivalents", q(substrate_eq, "equiv"), ev)]
    parts = [participant(substrate, "reactant", substrate, ev, subs_amounts),
             chemical("4", "reactant", "propargyl alcohol 4", ev, eq=reagent_eq),
             chemical("PdPPh3_2Cl2", "catalyst", "Pd(PPh3)2Cl2", ev, loading=pd),
             chemical("CuI", "catalyst", "CuI", ev, loading=cu),
             chemical("Et2NH", "reagent", "Et2NH", ev, eq=reagent_eq),
             chemical("CH3CN", "solvent", "CH3CN", ev)]
    parts += [chemical(pid, "product", label, ev) for pid, label in products]
    return parts


# Page 4, Table 6: four kinetic-resolution optimization rows.
table6 = [(1, 2, 31, 0.6, 960, [("Z_3h", 45, "NMR"), ("E_3h", 6, "NMR"), ("E_5h", 20, "NMR"), ("Z_5h", 5, "NMR")]),
          (2, 2, 32, 0.7, 60, [("Z_3h", 40, "NMR"), ("E_3h", "table dash (—)", "NMR"), ("E_5h", 29, "NMR"), ("Z_5h", 13, "NMR")]),
          (3, 3, 0, 0.7, 140, [("Z_3h", 55, "isolated"), ("E_3h", 10, "isolated"), ("E_5h", 22, "isolated"), ("Z_5h", "table dash (—)", "source marker")]),
          (4, 5, 0, 0.7, 70, [("Z_3h", (49, 46), "NMR/isolated"), ("E_3h", 1, "NMR"), ("E_5h", (28, 25), "NMR/isolated"), ("Z_5h", 3, "NMR")])]
for n, cat, temp, eq, minutes, values in table6:
    ev = evidence(4)
    product_labels = [(x, x.replace("_", "-")) for x in ("Z_3h", "E_3h", "E_5h", "Z_5h")]
    parts = kinetic_parts("E_Z_3h", ev, "n-C4F9", "n-C5H11", reagent_eq=eq, pd=cat, cu=cat,
                          products=product_labels)
    outcomes = []
    for pid, value, basis in values:
        if isinstance(value, tuple):
            prefix = "recovered_starting_material_" if pid in ("Z_3h", "E_3h") else ""
            outcomes.append(field(f"{prefix}nmr_yield_{pid}", q(value[0], "%"), ev, [pid]))
            outcomes.append(field(f"{prefix}isolated_yield_{pid}", q(value[1], "%"), ev, [pid]))
        else:
            prefix = "recovered_starting_material_" if pid in ("Z_3h", "E_3h") else ""
            outcomes.append(field(f"{prefix}{basis.lower().replace(' ', '_')}_yield_{pid}",
                                  q(value, "%") if isinstance(value, (int, float)) else value, ev, [pid]))
    records.append(record(f"table6_entry{n}", "optimization_entry", (4,), parts,
                          [field("temperature", q(temp, "°C"), ev),
                           field("reaction_time", q(minutes, "min"), ev),
                           field("atmosphere", "nitrogen", ev)], outcomes,
                          notes=("Starting material 3h was an E/Z=39/61 mixture.",)))


# Page 4, Table 7: seven independent kinetic-resolution scope entries.
table7 = [(1, "3d", "Z_3d", "E_5d", "Ph", "n-C4F9", 55, 48, 40, 0.9),
          (2, "3e", "Z_3e", "E_5e", "p-MeC6H4", "n-C4F9", 45, 45, 30, 0.9),
          (3, "3g", "Z_3g", "E_5g", "n-C4H9", "n-C4F9", 50, 45, 29, 0.7),
          (4, "3j", "Z_3j", "E_5j", "Bn", "n-C4F9", 70, 39, 39, 0.7),
          (5, "3k", "Z_3k", "E_5k", "n-C4H9", "n-C6F13", 75, 49, 27, 0.7),
          (6, "3l", "Z_3l", "E_5l", "n-C5H11", "n-C6F13", 55, 49, 23, 0.7),
          (7, "3m", "Z_3m", "E_5m", "n-C6H13", "n-C6F13", 45, 52, 22, 0.7)]
for n, substrate, zprod, eprod, r, rf, minutes, zy, ey, eq in table7:
    pages = (4, 6) if n in (1, 2) else (4,)
    ev = evidence(*pages)
    pd, cu = (5.0, 5.6) if n == 1 else ((5.0, 5.3) if n == 2 else (5.0, 5.0))
    parts = kinetic_parts(substrate, ev, rf, r, reagent_eq=eq, pd=pd, cu=cu,
                          products=[(zprod, zprod.replace("_", "-")), (eprod, eprod.replace("_", "-"))])
    outcomes = [field(f"recovered_starting_material_isolated_yield_{zprod}", q(zy, "%"), ev, [zprod]),
                field(f"isolated_yield_{eprod}", q(ey, "%"), ev, [eprod])]
    records.append(record(f"table7_entry{n}_{substrate}", "substrate_scope_entry", pages, parts,
                          [field("temperature", q(0, "°C"), ev),
                           field("reaction_time", q(minutes, "min"), ev),
                           field("atmosphere", "nitrogen", ev)], outcomes,
                          notes=(f"Table 7 substituent mapping: R={r}; Rf={rf}.",)))


# Enrich exact detailed batches visible on pages 5--6.  These are additions to
# their corresponding table records, not duplicate experiments.
by_id = {r["source_reaction_id"]: r for r in records}


def add_exact(rid, page, specs, product_mass=None, workup=False, purification=None):
    rec = by_id[rid]
    ev = evidence(page)
    lookup = {p["entity_id"]: p for p in rec["participants"]}
    for entity, vals in specs.items():
        if entity not in lookup:
            continue
        for name, value in vals:
            lookup[entity]["amounts"].append(amount(name, value, ev))
    if product_mass:
        entity, mass = product_mass
        lookup[entity]["amounts"].append(amount("mass", mass, ev))
    if workup:
        rec["steps"][0]["conditions"] += [
            field("workup", "quenched with brine, extracted with diethyl ether, dried over anhydrous Na2SO4", ev),
            field("operation", "filtration and evaporation", ev),
        ]
    if purification:
        rec["steps"][0]["conditions"].append(field("purification", purification, ev))


add_exact("table2_entry19_standard_3a", 5, {
    "1a": [("mass", q(111.5, "mg")), ("amount", q(0.80, "mmol"))],
    "2a": [("mass", q(555.1, "mg")), ("amount", q(1.60, "mmol"))],
    "Na2S2O4": [("mass", q(280.1, "mg")), ("amount", q(1.61, "mmol"))],
    "Na2CO3": [("mass", q(170.8, "mg")), ("amount", q(1.61, "mmol"))],
    "organic_solvent": [("volume", q(1.5, "mL"))], "H2O": [("volume", q(0.5, "mL"))],
}, ("3a", q(187.6, "mg")), True, "silica-gel column chromatography; petroleum ether/ethyl acetate 20/1")

for rid, specs, product, mass, purif in [
    ("table3_entry2_3b", {"1b": [("mass", q(79.7, "mg")), ("amount", q(0.38, "mmol"))],
                          "2a": [("mass", q(280.3, "mg")), ("amount", q(0.81, "mmol"))],
                          "Na2S2O4": [("mass", q(140.1, "mg")), ("amount", q(0.81, "mmol"))],
                          "base": [("mass", q(85.2, "mg")), ("amount", q(0.80, "mmol"))],
                          "MeOH": [("volume", q(0.75, "mL"))], "H2O": [("volume", q(0.25, "mL"))]},
     "3b", q(84.5, "mg"), "silica-gel column chromatography; petroleum ether/ethyl acetate 60/1"),
    ("table3_entry3_3c", {"1c": [("mass", q(83.0, "mg")), ("amount", q(0.41, "mmol"))],
                          "2a": [("mass", q(280.1, "mg")), ("amount", q(0.81, "mmol"))],
                          "Na2S2O4": [("mass", q(139.3, "mg")), ("amount", q(0.80, "mmol"))],
                          "base": [("mass", q(84.4, "mg")), ("amount", q(0.80, "mmol"))],
                          "MeOH": [("volume", q(0.75, "mL"))], "H2O": [("volume", q(0.25, "mL"))]},
     "3c", q(95.9, "mg"), "silica-gel column chromatography; petroleum ether/ethyl acetate 40/1"),
    ("table3_entry4_3p", {"1m": [("mass", q(62.0, "mg")), ("amount", q(0.49, "mmol"))],
                          "2a": [("mass", q(341.7, "mg")), ("amount", q(0.99, "mmol"))],
                          "Na2S2O4": [("mass", q(175.0, "mg")), ("amount", q(1.0, "mmol"))],
                          "base": [("mass", q(105.9, "mg")), ("amount", q(1.0, "mmol"))],
                          "MeOH": [("volume", q(1.5, "mL"))], "H2O": [("volume", q(0.5, "mL"))]},
     "3p", q(79.5, "mg"), "silica-gel column chromatography; petroleum ether/ethyl acetate 40/1 to 10/1"),
]:
    add_exact(rid, 5, specs, (product, mass), True, purif)

add_exact("table4_entry3", 5, {
    "1d": [("mass", q(57.1, "mg")), ("amount", q(0.39, "mmol"))],
    "2a": [("mass", q(276.0, "mg")), ("amount", q(0.80, "mmol"))],
    "Na2S2O4": [("mass", q(140.5, "mg")), ("amount", q(0.81, "mmol"))],
    "base": [("mass", q(85.2, "mg")), ("amount", q(0.80, "mmol"))],
    "MeOH": [("volume", q(0.75, "mL"))], "H2O": [("volume", q(0.25, "mL"))],
    "E_3d": [("mass", q(59.7, "mg"))], "Z_3d": [("mass", q(68.0, "mg"))],
}, None, True, "silica-gel column chromatography; petroleum ether/ethyl acetate 12/1")

add_exact("table5_entry1_3d", 5, {
    "1d": [("mass", q(351.4, "mg")), ("amount", q(2.41, "mmol"))],
    "2a": [("mass", q(1669.8, "mg")), ("amount", q(4.83, "mmol"))],
    "Na2S2O4": [("mass", q(835.6, "mg")), ("amount", q(4.80, "mmol"))],
    "base": [("mass", q(508.7, "mg")), ("amount", q(4.80, "mmol"))],
    "MeOH": [("volume", q(4.5, "mL"))], "H2O": [("volume", q(1.5, "mL"))],
    "3d": [("mass", q(813.5, "mg"))],
}, None, True, "silica-gel column chromatography; petroleum ether/ethyl acetate 10/1")

add_exact("table5_entry2_3e", 6, {
    "1e": [("mass", q(384.1, "mg")), ("amount", q(2.40, "mmol"))],
    "2a": [("mass", q(1692.4, "mg")), ("amount", q(4.89, "mmol"))],
    "Na2S2O4": [("mass", q(835.2, "mg")), ("amount", q(4.80, "mmol"))],
    "base": [("mass", q(509.0, "mg")), ("amount", q(4.80, "mmol"))],
    "MeOH": [("volume", q(4.5, "mL"))], "H2O": [("volume", q(1.5, "mL"))],
    "3e": [("mass", q(745.9, "mg"))],
}, None, True, "silica-gel column chromatography; petroleum ether/ethyl acetate 10/1")

add_exact("table7_entry1_3d", 6, {
    "3d": [("mass", q(123.5, "mg")), ("amount", q(0.251, "mmol"))],
    "4": [("mass", q(12.7, "mg")), ("amount", q(0.227, "mmol"))],
    "PdPPh3_2Cl2": [("mass", q(8.8, "mg")), ("amount", q(0.013, "mmol"))],
    "CuI": [("mass", q(2.4, "mg")), ("amount", q(0.014, "mmol"))],
    "Et2NH": [("mass", q(16.5, "mg")), ("amount", q(0.226, "mmol"))],
    "CH3CN": [("volume", q(0.5, "mL"))],
    "Z_3d": [("mass", q(59.1, "mg"))], "E_5d": [("mass", q(42.0, "mg"))],
}, None, True, "silica-gel chromatography; Z-3d petroleum ether/ethyl acetate 10/1; E-5d 3/1")
by_id["table7_entry1_3d"]["steps"][0]["conditions"].append(field("operation", "monitored by GC", evidence(6)))

add_exact("table7_entry2_3e", 6, {
    "3e": [("mass", q(101.2, "mg")), ("amount", q(0.200, "mmol"))],
    "4": [("mass", q(10.3, "mg")), ("amount", q(0.184, "mmol"))],
    "PdPPh3_2Cl2": [("mass", q(7.0, "mg")), ("amount", q(0.010, "mmol"))],
    "CuI": [("mass", q(2.0, "mg")), ("amount", q(0.011, "mmol"))],
    "Et2NH": [("mass", q(13.1, "mg")), ("amount", q(0.179, "mmol"))],
    "CH3CN": [("volume", q(0.4, "mL"))],
    "Z_3e": [("mass", q(45.4, "mg"))], "E_5e": [("mass", q(26.4, "mg"))],
}, None, False, "column chromatography; Z-3e petroleum ether/ethyl acetate 10/1; E-5e dichloromethane/ethyl acetate 10/1")


assert len(records) == 67, len(records)
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")


ids = lambda *prefixes: [r["record_id"] for r in records
                          if any(r["source_reaction_id"].startswith(p) for p in prefixes)]
coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1, "state": "attempted",
            "regions": [
                {"region": "title, abstract, introduction, and opening Results and Discussion",
                 "finding": "Abstract and prose summarize the study and cite prior work; they were not duplicated as batch experiments. Opening prose points to the optimization rows on page 2.",
                 "evidence_ids": evidence(1)},
                {"region": "lower-left Scheme 1",
                 "finding": "Generic two-stage radical-addition/kinetic-resolution route; classified as a general scheme with no batch scale or row-specific yield.",
                 "evidence_ids": evidence(1)},
            ],
            "record_ids": ids("scheme1_general_route"),
            "unresolved": ["Generic R groups prevent complete structures; abstract-level yield ranges were not duplicated as experiments."],
        },
        {
            "page": 2, "state": "attempted",
            "regions": [
                {"region": "upper-left Table 1 and footnotes", "finding": "Eleven base-screen rows extracted independently, including NMR basis, recoveries, and the complicated Cy2NH result.", "evidence_ids": evidence(2)},
                {"region": "lower-left Table 2 and footnotes", "finding": "Twenty solvent-screen rows extracted independently; concentration, solvent-ratio, temperature, recovery, and NMR-yield footnotes were applied only to marked rows.", "evidence_ids": evidence(2)},
                {"region": "upper-right Table 3", "finding": "Four substrate-scope rows checked; entry 1 was merged with Table 2 entry 19 and the page-5 standard 3a batch, while entries 2-4 remain separate experiments.", "evidence_ids": evidence(2)},
                {"region": "lower-right equations 1 and 2", "finding": "Two explicit failed reactions extracted: 1q gave a complicated reaction; 1r gave no major product with 35% starting material recovered.", "evidence_ids": evidence(2)},
            ],
            "record_ids": ids("table1_", "table2_", "table3_", "eq1_", "eq2_"),
            "unresolved": ["Most optimization rows provide labels/generic drawings rather than machine-verified structures; Table 2 omits duration except where the detailed page-5 batch supplies it."],
        },
        {
            "page": 3, "state": "attempted",
            "regions": [
                {"region": "top Table 4 and footnotes", "finding": "Four condition-optimization rows extracted independently with separate E-3d and Z-3d yields and marked starting-material recoveries.", "evidence_ids": evidence(3)},
                {"region": "middle-left Fig. 1", "finding": "NOESY drawings support the paper's E/Z assignments for 3d and 3o; no standalone experiment record was created and structures remain unverified.", "evidence_ids": evidence(3)},
                {"region": "lower Table 5 and footnotes", "finding": "Fifteen radical-addition scope rows extracted, including separate E/Z isolated yields for entries 13 and 15 and the impure Z-3s result for entry 14.", "evidence_ids": evidence(3)},
                {"region": "right-column kinetic-resolution discussion", "finding": "Narrative introduces Tables 6 and 7 on page 4; it was used as context rather than duplicate experiments.", "evidence_ids": evidence(3)},
            ],
            "record_ids": ids("table4_", "table5_"),
            "unresolved": ["The Table 4 visual repeats E-3d in both yield subheaders; E/Z assignment follows the reaction drawing and adjacent prose and is flagged for review."],
        },
        {
            "page": 4, "state": "attempted",
            "regions": [
                {"region": "upper Table 6 and footnote", "finding": "Four kinetic-resolution optimization rows extracted with recovered Z/E-3h separated from coupled E/Z-5h products; parenthesized isolated values remain separate from NMR values.", "evidence_ids": evidence(4)},
                {"region": "middle Table 7 and footnote", "finding": "Seven kinetic-resolution scope rows extracted independently; recovered Z-3 is classified as recovery rather than product yield, and the 0.9-equivalent override was applied to entries 1 and 2.", "evidence_ids": evidence(4)},
                {"region": "lower-left conclusions and general experimental text", "finding": "No new batch in conclusions. General text supplies air atmosphere for radical additions and nitrogen/dried-glassware context for kinetic resolutions.", "evidence_ids": evidence(4)},
                {"region": "lower-right section 4.2.1 reaction drawing", "finding": "The 3a drawing is the same standard experiment detailed on page 5 and was merged with its Table 2/Table 3 record.", "evidence_ids": evidence(4)},
            ],
            "record_ids": ids("table6_", "table7_", "table2_entry19_standard_3a"),
            "unresolved": ["Table 6 dash cells were preserved as source markers, not converted to zero."],
        },
        {
            "page": 5, "state": "attempted",
            "regions": [
                {"region": "section 4.2.1.1 typical procedure 1", "finding": "Exact quantities, operations, workup, purification, product mass, yield, and E/Z ratio were merged into the standard 3a record.", "evidence_ids": evidence(5)},
                {"region": "sections 4.2.2-4.2.4", "finding": "Exact batches for 3b, 3c, and 3p were merged with Table 3 entries 2-4, including masses, mmol, solvent volumes, time, yield, ratio, and eluents.", "evidence_ids": evidence(5)},
                {"region": "section 4.2.5", "finding": "Separate E-3d and Z-3d batch merged with Table 4 entry 3; characterization text was inspected but not decomposed into reaction outcomes.", "evidence_ids": evidence(5)},
                {"region": "section 4.2.6.1 start", "finding": "Large-scale 3d E/Z-mixture batch merged with Table 5 entry 1; its product characterization continues on page 6.", "evidence_ids": evidence(5)},
            ],
            "record_ids": ids("table2_entry19_standard_3a", "table3_", "table4_entry3", "table5_entry1_3d"),
            "unresolved": ["Spectroscopic characterization was retained as source context rather than converted into reaction-condition fields."],
        },
        {
            "page": 6, "state": "attempted",
            "regions": [
                {"region": "upper-left continuation of section 4.2.6.1", "finding": "3d mixture yield, E/Z ratio, product mass, and purification complete the Table 5 entry-1 batch.", "evidence_ids": evidence(6)},
                {"region": "left section 4.2.6.2-4.2.6.5", "finding": "Detailed Sonogashira kinetic-resolution batch merged with Table 7 entry 1, including exact catalyst/reagent quantities, nitrogen atmosphere, GC monitoring, workup, two product masses and isolated yields.", "evidence_ids": evidence(6)},
                {"region": "right sections 4.2.7.1-4.2.7.4", "finding": "Detailed 3e radical-addition and kinetic-resolution batches merged with Table 5 entry 2 and Table 7 entry 2 respectively.", "evidence_ids": evidence(6)},
                {"region": "bottom-right section 4.2.8 reaction drawing", "finding": "Start of the 3f preparation linked to Table 5 entry 3; continuation details on page 7 were not imported or claimed as covered.", "evidence_ids": evidence(6)},
            ],
            "record_ids": ids("table5_entry1_3d", "table5_entry2_3e", "table5_entry3_3f", "table7_entry1_3d", "table7_entry2_3e"),
            "unresolved": ["Section 4.2.8 continues onto page 7, outside the claimed page range; no page-7 details are included."],
        },
    ],
}
COVERAGE.parent.mkdir(parents=True, exist_ok=True)
COVERAGE.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"records": len(records), "records_file": str(OUT), "coverage_file": str(COVERAGE)}, ensure_ascii=False))
