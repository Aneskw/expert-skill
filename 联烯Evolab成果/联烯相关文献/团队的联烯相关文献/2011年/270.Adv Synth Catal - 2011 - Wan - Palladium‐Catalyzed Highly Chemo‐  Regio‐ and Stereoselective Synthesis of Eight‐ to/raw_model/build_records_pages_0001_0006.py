#!/usr/bin/env python3
"""Build evidence-linked machine records for PDF pages 1--6 of doc_e5379ddb5b502c43."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
DOC = "doc_e5379ddb5b502c43"


def ev(page, kind="image"):
    return f"{DOC}:page{page}:{kind}"


def fact(value, evidence=()):
    return {
        "value": value,
        "evidence_ids": list(evidence),
        "verification": "missing" if value is None else "unreviewed",
    }


def fld(name, value, evidence=(), targets=None):
    item = {"name": name, "fact": fact(value, evidence)}
    if targets:
        item["target_entity_ids"] = list(targets)
    return item


def participant(entity_id, role, label, evidence, name=None, amounts=(), smiles=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence) if name is not None else fact(None),
        "smiles": fact(smiles, evidence) if smiles is not None else fact(None),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": [fld(n, v, evidence) for n, v in amounts],
    }


def record(suffix, kind, evidence, participants, steps=(), outcomes=(), notes=(), unresolved=()):
    return {
        "record_id": f"{DOC}:{suffix}",
        "document_id": DOC,
        "source_reaction_id": suffix,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": list(dict.fromkeys(evidence)),
        "participants": participants,
        "steps": list(steps),
        "outcomes": list(outcomes),
        "notes": [fact(n, evidence) for n in notes],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": list(unresolved),
        },
    }


def step(step_id, participant_ids, conditions):
    return {
        "step_id": step_id,
        "participant_ids": participant_ids,
        "conditions": conditions,
    }


records = []

# Page 2, Scheme 1: three explicitly reported starting-material routes.
e2 = [ev(2, "image"), ev(2, "text")]
for label, r1, r2, r3, n, yld in [
    ("1a", "H", "H", "H", 1, 82),
    ("1g", "H", "H", "H", 2, 75),
    ("1h", "H", "H", "H", 3, 68),
    ("1k", "H", "H", "CH3", 1, 78),
    ("1l", "CH3", "H", "H", 1, 70),
    ("1m", "H", "n-C4H9", "H", 1, 70),
]:
    rid = f"scheme1_dmap_{label}"
    ps = [
        participant("allenol", "reactant", f"allenol (R1={r1}, R2={r2}, n={n})", e2),
        participant("beta_methylene_beta_lactone", "reactant", "beta-methylene-beta-lactone", e2),
        participant("dmap", "catalyst", "DMAP", e2, amounts=(("catalyst_loading", {"number": 10, "unit": "mol%"}),)),
        participant("thf", "solvent", "THF", e2),
        participant("product", "product", label, e2),
    ]
    cond = [
        fld("temperature", "r.t.", e2),
        fld("time", None),
        fld("atmosphere", None),
        fld("workup", None),
        fld("purification", None),
    ]
    records.append(record(rid, "substrate_scope_entry", e2, ps,
        [step("scheme1_route_a", [p["entity_id"] for p in ps], cond)],
        [fld("reported_yield", {"number": yld, "unit": "%"}, e2, ["product"])],
        [f"Scheme 1 substituents: R1={r1}, R2={r2}, R3={r3}, n={n}."],
        ["Reaction time, atmosphere, workup, purification, and yield basis are not reported in the visible scheme.", "Product structure is retained by label; SMILES is not source-verified."]))

for label, r1, r2, yld in [("1b", "i-Pr", "CH3", 47), ("1c", "Ph", "Et", 68)]:
    rid = f"scheme1_exchange_{label}"
    ps = [
        participant("oxoalkanoate", "reactant", f"3-oxoalkanoate (R1={r1}, R2={r2})", e2),
        participant("pentadienol", "reactant", "3,4-pentadienol", e2, amounts=(("equivalents", {"number": 2.5, "unit": "equiv"}),)),
        participant("pph3", "catalyst", "PPh3", e2, amounts=(("catalyst_loading", {"number": 20, "unit": "mol%"}),)),
        participant("toluene", "solvent", "toluene", e2),
        participant("product", "product", label, e2),
    ]
    cond = [fld("temperature", "reflux", e2), fld("time", None), fld("atmosphere", None), fld("workup", None), fld("purification", None)]
    records.append(record(rid, "substrate_scope_entry", e2, ps,
        [step("scheme1_route_b", [p["entity_id"] for p in ps], cond)],
        [fld("reported_yield", {"number": yld, "unit": "%"}, e2, ["product"])],
        [f"Scheme 1 substituents: R1={r1}, R2={r2}."],
        ["Reaction time, atmosphere, workup, purification, and yield basis are not reported in the visible scheme.", "Product structure is retained by label; SMILES is not source-verified."]))

for label, r, x, yld in [("1d", "Me", "I", 60), ("1e", "Et", "I", 45), ("1f", "allyl", "Br", 62), ("1i", "n-Pr", "I", 29), ("1j", "Bn", "Br", 46)]:
    rid = f"scheme1_alkylation_{label}"
    ps = [
        participant("substrate_1a", "reactant", "1a", e2),
        participant("rx", "reactant", f"RX (R={r}, X={x})", e2),
        participant("nah", "reagent", "NaH", e2),
        participant("thf", "solvent", "THF", e2),
        participant("product", "product", label, e2),
    ]
    cond = [fld("temperature", None), fld("time", None), fld("atmosphere", None), fld("workup", None), fld("purification", None)]
    records.append(record(rid, "substrate_scope_entry", e2, ps,
        [step("scheme1_route_c", [p["entity_id"] for p in ps], cond)],
        [fld("reported_yield", {"number": yld, "unit": "%"}, e2, ["product"])],
        [f"Scheme 1 alkylating agent identity is given by R={r}, X={x}.", "The source temperature program is 0 °C to r.t.; it is preserved as text because it is not a single scalar temperature."],
        ["Reagent quantities, reaction time, atmosphere, workup, purification, and yield basis are not reported in the visible scheme.", "Product structure is retained by label; SMILES is not source-verified."]))

# Page 2, Scheme 2: conceptual product map, not a reported batch experiment.
mech2_ps = [
    participant("substrate_1a", "reactant", "1a", e2),
    participant("phi", "reactant", "PhI", e2, name="iodobenzene", smiles="Ic1ccccc1"),
    participant("product_2a", "product", "2a", e2),
    participant("product_4a", "product", "4a", e2),
    participant("product_3a", "product", "3a", e2),
    participant("product_5a", "product", "5a", e2),
]
records.append(record("scheme2_possible_products", "mechanism", e2, mech2_ps, notes=(
    "Scheme 2 depicts anti/syn pi-allylic palladium intermediates and possible C-attack products 2a/4a and O-attack products 3a/5a.",
    "The scheme is a mechanistic/product-possibility diagram and carries no independent experimental yield.",
), unresolved=("Intermediate and product structures remain unverified machine interpretations.",)))


def coupling_participants(evidence, catalyst, ligand=None, base="K2CO3", solvent="CH3CN", substrate_amount=None, phi_amount=None):
    ps = [
        participant("substrate_1a", "reactant", "1a", evidence, amounts=substrate_amount or ()),
        participant("phi", "reactant", "PhI", evidence, name="iodobenzene", amounts=phi_amount or (), smiles="Ic1ccccc1"),
        participant("catalyst", "catalyst", catalyst[0], evidence, amounts=(("catalyst_loading", {"number": catalyst[1], "unit": "mol%"}),)),
    ]
    if ligand:
        ps.append(participant("ligand", "reagent", ligand[0], evidence, amounts=(("ligand_loading", {"number": ligand[1], "unit": "mol%"}),)))
    ps.extend([
        participant("base", "reagent", base, evidence, amounts=(("equivalents", {"number": 2, "unit": "equiv"}),)),
        participant("solvent", "solvent", solvent, evidence, amounts=(("volume", {"number": 2, "unit": "mL"}),)),
        participant("product_2a", "product", "2a", evidence),
    ])
    return ps


def add_opt(rid, evidence, catalyst, ligand, base, solvent, temp, duration, product_yield, recovery=None,
            isolated=None, extra_products=False, note=None):
    ps = coupling_participants(evidence, catalyst, ligand, base, solvent,
        (("amount", {"number": 0.250, "unit": "mmol"}),),
        (("amount", {"number": 0.375, "unit": "mmol"}), ("equivalents", {"number": 1.5, "unit": "equiv"})))
    if extra_products:
        ps += [participant("product_4a", "product", "4a", evidence), participant("product_3a", "product", "3a", evidence), participant("product_5a", "product", "5a", evidence)]
    cond = [fld("temperature", temp, evidence), fld("time", duration, evidence), fld("atmosphere", "argon", evidence), fld("workup", None), fld("purification", None)]
    outcomes = [fld("nmr_yield", product_yield, evidence, ["product_2a"]), fld("yield_measurement_basis", "1H NMR using 1,3,5-trimethylbenzene as internal standard", evidence, ["product_2a"])]
    if recovery is not None:
        outcomes.append(fld("recovered_starting_material_yield", recovery, evidence, ["substrate_1a"]))
    if isolated is not None:
        outcomes.append(fld("isolated_yield", isolated, evidence, ["product_2a"]))
    notes = [note] if note else []
    records.append(record(rid, "optimization_entry", evidence, ps,
        [step("coupling_cyclization", [p["entity_id"] for p in ps], cond)], outcomes, notes,
        ["Workup and purification are not reported for the optimization row.", "Reactant and product structures identified by labels remain unverified."]))


e23 = [ev(2, "image"), ev(2, "text"), ev(3, "image"), ev(3, "text")]
add_opt("table1_entry1", e23, ("Pd(PPh3)4", 5), None, "K2CO3", "CH3CN", {"number": 85, "unit": "°C"}, {"number": 46, "unit": "h"}, {"number": 66, "unit": "%"}, extra_products=True,
        note="Narrative reports 4a at <2% by NMR, if any, and O-attack products 3a and 5a not observed.")
# Add product-specific side outcomes to entry 1.
records[-1]["outcomes"] += [
    fld("nmr_yield_4a", {"number": 2, "unit": "%", "qualifier": "lt", "raw_text": "<2%"}, e23, ["product_4a"]),
    fld("observed_3a", "not observed", e23, ["product_3a"]),
    fld("observed_5a", "not observed", e23, ["product_5a"]),
]

add_opt("table1_entry2_table2_entry1", [ev(3, "image"), ev(3, "text")], ("Pd(OAc)2", 5), ("PPh3", 10), "K2CO3", "CH3CN", {"number": 85, "unit": "°C"}, {"number": 6, "unit": "h"}, {"number": 81, "unit": "%"}, recovery={"number": 0, "unit": "%"}, isolated={"number": 75, "unit": "%"}, extra_products=True,
        note="Table 1 entry 2 and Table 2 entry 1 report the same conditions and 81% NMR yield; they are represented once. Narrative reports 4a at <2.3% by NMR, if any, and O-attack product was not observed.")
records[-1]["outcomes"] += [
    fld("nmr_yield_4a", {"number": 2.3, "unit": "%", "qualifier": "lt", "raw_text": "<2.3%"}, [ev(3, "image"), ev(3, "text")], ["product_4a"]),
    fld("observed_3a_and_5a", "not observed", [ev(3, "image"), ev(3, "text")], ["product_3a", "product_5a"]),
]
add_opt("table1_entry3", [ev(3, "image"), ev(3, "text")], ("Pd(dba)2", 5), ("PPh3", 15), "K2CO3", "CH3CN", {"number": 85, "unit": "°C"}, {"number": 6, "unit": "h"}, {"number": 64, "unit": "%"}, recovery={"number": 5, "unit": "%"})
add_opt("table1_entry4", [ev(3, "image"), ev(3, "text")], ("Pd(OAc)2", 5), ("PPh3", 10), "K2CO3", "CH3CN", {"number": 50, "unit": "°C"}, {"number": 21.7, "unit": "h"}, {"number": 69, "unit": "%"}, recovery={"number": 14, "unit": "%"})
add_opt("prose_90min", [ev(3, "image"), ev(3, "text")], ("Pd(OAc)2", 5), ("PPh3", 10), "K2CO3", "CH3CN", {"number": 85, "unit": "°C"}, {"number": 90, "unit": "min"}, {"number": 59, "unit": "%"}, recovery={"number": 29, "unit": "%"}, extra_products=True,
        note="Narrative states that only C-attack product 2a was detected and the O-attack product was not observed.")
records[-1]["outcomes"].append(fld("observed_3a_and_5a", "not observed", [ev(3, "image"), ev(3, "text")], ["product_3a", "product_5a"]))

for entry, base, solvent, hours, recovery, yld in [
    (2, "K2CO3", "toluene", 26, 25, 42),
    (3, "K2CO3", "THF", 26, 22, 59),
    (4, "K2CO3", "DCE", 30.5, 28, 42),
    (5, "K2CO3", "CH3NO2", 24, 0, 68),
    (6, "Na2CO3", "CH3CN", 34, 55, 27),
    (7, "Cs2CO3", "CH3CN", 11, 0, 8),
    (8, "Et3N", "CH3CN", 46.5, 39, 16),
    (9, "KOH", "CH3CN", 15.5, 0, 20),
    (10, "K3PO4", "CH3CN", 15.5, 0, 28),
    (11, "CaH2", "CH3CN", 45.5, 16, "trace"),
]:
    yval = yld if isinstance(yld, str) else {"number": yld, "unit": "%"}
    add_opt(f"table2_entry{entry}", [ev(3, "image"), ev(3, "text")], ("Pd(OAc)2", 5), ("PPh3", 10), base, solvent,
            {"number": 85, "unit": "°C"}, {"number": hours, "unit": "h"}, yval, recovery={"number": recovery, "unit": "%"})


def scope_common(evidence, substrate_label, substrate_amount, halide_label, halide_amount, product_label,
                 temperature, time_h, yld, extra_participants=(), product_name=None, extra_conditions=(), extra_outcomes=(), notes=(), unresolved=()):
    ps = [
        participant("substrate", "reactant", substrate_label, evidence, amounts=substrate_amount),
        participant("halide", "reactant", halide_label, evidence, amounts=halide_amount),
        participant("pd_oac2", "catalyst", "Pd(OAc)2", evidence, amounts=(("catalyst_loading", {"number": 5, "unit": "mol%"}),)),
        participant("pph3", "reagent", "PPh3", evidence, amounts=(("ligand_loading", {"number": 10, "unit": "mol%"}),)),
        participant("k2co3", "reagent", "K2CO3", evidence, amounts=(("equivalents", {"number": 2, "unit": "equiv"}),)),
        participant("ch3cn", "solvent", "CH3CN", evidence, amounts=(("volume", {"number": 4, "unit": "mL"}),)),
        participant("product", "product", product_label, evidence, name=product_name),
    ] + list(extra_participants)
    cond = [fld("temperature", temperature, evidence), fld("time", time_h, evidence), fld("atmosphere", None), fld("workup", None), fld("purification", None)] + list(extra_conditions)
    outcomes = [fld("isolated_yield", {"number": yld, "unit": "%"}, evidence, ["product"]), fld("yield_measurement_basis", "isolated yield", evidence, ["product"])] + list(extra_outcomes)
    return ps, [step("coupling_cyclization", [p["entity_id"] for p in ps], cond)], outcomes, list(notes), ["Atmosphere, workup, and purification are not reported in the scope table unless separately stated.", "Substrate and product structures retained by source labels remain unverified."] + list(unresolved)


# Page 4, Table 3; page 6 detailed batches are merged for 2a and visible portion of 2b.
table3 = [
    ("1", "1a", "Me", "H", 4.5, 73, "2a", 85, 1.5),
    ("2", "1b", "i-Pr", "H", 6, 83, "2b", 85, 1.5),
    ("3", "1c", "Ph", "H", 1.5, 79, "2c", 85, 1.5),
    ("4", "1d", "Me", "Me", 10.5, 81, "2d", 100, 1.5),
    ("row_1j", "1j", "Me", "Bn", 22, 75, "2w", 100, 1.5),
    ("5", "1e", "Me", "Et", 81.5, 63, "2e", 100, 2.5),
    ("6", "1i", "Me", "n-Pr", 82, 67, "2v", 100, 2.5),
    ("7", "1f", "Me", "CH2=CHCH2", 29, 69, "2f", 100, 1.5),
]
for entry, sub, r1, r2, hours, yld, prod, temp, phi_eq in table3:
    evidence = [ev(4, "image"), ev(4, "text")]
    sub_amount = (("amount", {"number": 0.50, "unit": "mmol"}),)
    phi_amount = (("equivalents", {"number": phi_eq, "unit": "equiv"}),)
    product_name = None
    extra_conditions = []
    extra_outcomes = []
    notes = [f"Table 3 substituents: R1={r1}, R2={r2}."]
    unresolved = []
    if sub == "1a":
        evidence += [ev(6, "image"), ev(6, "text")]
        sub_amount += (("mass", {"number": 83.2, "unit": "mg"}),)
        phi_amount += (("amount", {"number": 0.75, "unit": "mmol"}), ("mass", {"number": 153.6, "unit": "mg"}))
        product_name = "3-acetyl-5-phenyl-5(E)-3,4,7,8-tetrahydro-2H-oxocin-2-one"
        extra_conditions = [
            fld("operation", "Reagents were added sequentially to a flame-dried Schlenk tube under argon; the mixture was stirred in a preheated oil bath and monitored by TLC.", [ev(6, "image"), ev(6, "text")]),
            fld("workup", "Filtered through a short column of silica gel and concentrated.", [ev(6, "image"), ev(6, "text")]),
            fld("purification", "Silica-gel chromatography; petroleum ether (b.p. 30-60 °C)/ethyl ether = 10/1.", [ev(6, "image"), ev(6, "text")]),
            fld("atmosphere", "argon", [ev(6, "image"), ev(6, "text")]),
        ]
        extra_outcomes = [fld("product_mass", {"number": 88.6, "unit": "mg"}, [ev(6, "image"), ev(6, "text")], ["product"])]
        notes.append("The detailed page-6 batch matches Table 3 entry 1 by substrate, scale, conditions, product label, and 73% yield.")
    elif sub == "1b":
        evidence += [ev(6, "image"), ev(6, "text")]
        sub_amount += (("mass", {"number": 97.6, "unit": "mg"}),)
        phi_amount += (("amount", {"number": 0.75, "unit": "mmol"}), ("mass", {"number": 152.9, "unit": "mg"}))
        product_name = "3-isobutyryl-5-phenyl-5(E)-3,4,7,8-tetrahydro-2H-oxocin-2-one"
        notes.append("Page 6 gives the visible beginning of the 2b batch; its outcome continues beyond the claimed page range, so the yield is taken only from Table 3.")
        unresolved.append("The page-6 2b procedure continues on page 7; continuation details are not claimed as covered.")
    ps, st, outs, ns, ur = scope_common(evidence, sub, sub_amount, "PhI", phi_amount, prod,
        {"number": temp, "unit": "°C"}, {"number": hours, "unit": "h"}, yld,
        product_name=product_name, extra_conditions=extra_conditions, extra_outcomes=extra_outcomes, notes=notes, unresolved=unresolved)
    if sub == "1a":
        # Detailed page-6 fields replace the table-level null placeholders.
        stated = {"atmosphere", "workup", "purification"}
        st[0]["conditions"] = [c for c in st[0]["conditions"] if not (c["name"] in stated and c["fact"]["value"] is None)]
    # Add exact page-6 masses for shared reagents on the two detailed batches.
    if sub in ("1a", "1b"):
        mass_map = {
            "1a": {"pd_oac2": 5.7, "pph3": 13.3, "k2co3": 138.3},
            "1b": {"pd_oac2": 5.4, "pph3": 13.3, "k2co3": 138.1},
        }[sub]
        mmol_map = {"pd_oac2": 0.025, "pph3": 0.050, "k2co3": 1.0}
        for p in ps:
            if p["entity_id"] in mass_map:
                p["amounts"] += [fld("mass", {"number": mass_map[p["entity_id"]], "unit": "mg"}, [ev(6, "image"), ev(6, "text")]), fld("amount", {"number": mmol_map[p["entity_id"]], "unit": "mmol"}, [ev(6, "image"), ev(6, "text")])]
    records.append(record(f"table3_entry{entry}", "substrate_scope_entry", evidence, ps, st, outs, ns, ur))

# Page 4, Table 4.
for entry, rlabel, hours, yld, prod in [
    (1, "RI (R=4-MeC6H4)", 2, 75, "2g"),
    (2, "RI (R=4-MeOC6H4)", 5, 69, "2h"),
    (3, "RI (R=3-MeC6H4)", 2, 78, "2i"),
    (4, "RI (R=3,4-Me2C6H3)", 1.6, 72, "2j"),
    (5, "RI (R=3,4-(OCH2)2C6H3)", 2.5, 66, "2k"),
    (6, "RI (R=4-EtO2CC6H4)", 3, 58, "2l"),
    (7, "RI (R=4-BrC6H4)", 3.5, 63, "2m"),
    (8, "RI (R=3-thienyl)", 2, 70, "2n"),
    (9, "RI (R=1-(E)-hexenyl)", 2.5, 59, "2o"),
    (10, "RI (R=(E)-styryl)", 1.5, 58, "2p"),
]:
    evidence = [ev(4, "image"), ev(4, "text")]
    ps, st, outs, ns, ur = scope_common(evidence, "1c", (("amount", {"number": 0.50, "unit": "mmol"}),), rlabel,
        (("amount", {"number": 0.75, "unit": "mmol"}), ("equivalents", {"number": 1.5, "unit": "equiv"})), prod,
        {"number": 85, "unit": "°C"}, {"number": hours, "unit": "h"}, yld,
        notes=("The organic-halide identity is preserved in the condensed R/RI notation printed in Table 4.",))
    records.append(record(f"table4_entry{entry}", "substrate_scope_entry", evidence, ps, st, outs, ns, ur))

# Page 4 Scheme 3, with page-5 narrative support where available.
for prod, sub, ar, hours, yld, extra_ev, extra_note in [
    ("E-2q", "1g", "Ph", 11, 82, [ev(5, "image"), ev(5, "text")], "Narrative states that 2q was obtained on a one-gram scale."),
    ("E-2r", "1g", "4-MeOC6H4", 9, 78, [], None),
    ("E-2s", "1g", "4-NO2C6H4", 11, 74, [ev(5, "image"), ev(5, "text")], "The product structure was additionally studied by single-crystal X-ray diffraction; machine structure verification remains false."),
    ("E-2t", "1h", "Ph", 14, 71, [], None),
    ("E-2u", "1h", "4-BrC6H4", 6, 69, [ev(5, "image"), ev(5, "text")], "The product was reported as a single stereoisomer and its C=C configuration was studied by single-crystal X-ray diffraction; machine structure verification remains false."),
]:
    evidence = [ev(4, "image"), ev(4, "text")] + extra_ev
    ps, st, outs, ns, ur = scope_common(evidence, sub, (), f"ArI (Ar={ar})", (("equivalents", {"number": 1.5, "unit": "equiv"}),), prod,
        {"number": 85, "unit": "°C"}, {"number": hours, "unit": "h"}, yld,
        notes=tuple(x for x in [extra_note] if x), unresolved=("Exact reaction scale and yield basis are not stated in Scheme 3, except the qualitative one-gram-scale note for 2q.",))
    # Scheme 3 does not state a 4 mL solvent volume; remove the inherited volume claim.
    next(p for p in ps if p["entity_id"] == "ch3cn")["amounts"] = []
    outs[0] = fld("reported_yield", {"number": yld, "unit": "%"}, evidence, ["product"])
    outs[1] = fld("yield_measurement_basis", None, (), ["product"])
    records.append(record(f"scheme3_{prod.lower().replace('-', '_')}", "substrate_scope_entry", evidence, ps, st, outs, ns, ur))

# Page 5, Scheme 4: success, explicit failure, and complicated outcome.
e5 = [ev(5, "image"), ev(5, "text")]
ps, st, outs, ns, ur = scope_common(e5, "1k", (), "1-iodo-4-nitrobenzene", (("equivalents", {"number": 1.5, "unit": "equiv"}),), "2x",
    {"number": 85, "unit": "°C"}, {"number": 4.5, "unit": "h"}, 65,
    extra_outcomes=(fld("diastereomeric_ratio", {"minimum": 8, "maximum": 1000, "unit": ":1", "raw_text": ">8:1 dr"}, e5, ["product"]),),
    notes=("The trans major isomer was studied by single-crystal X-ray diffraction (Figure 4 on page 6); machine structure verification remains false.",),
    unresolved=("The upper bound of the reported >8:1 dr is not finite in the source; it is therefore retained separately below as source text.",))
# Replace unsupported synthetic ratio object by qualitative source text before merge.
outs[-1] = fld("diastereomeric_ratio", ">8:1 dr", e5, ["product"])
next(p for p in ps if p["entity_id"] == "ch3cn")["amounts"] = []
outs[0] = fld("reported_yield", {"number": 65, "unit": "%"}, e5, ["product"])
outs[1] = fld("yield_measurement_basis", None, (), ["product"])
records.append(record("scheme4_1k_to_2x", "substrate_scope_entry", e5 + [ev(6, "image"), ev(6, "text")], ps, st, outs, ns, ur))

for sub, hours, outcome in [("1l", 26.5, "no reaction"), ("1m", 55, "complicated")]:
    ps = [
        participant("substrate", "reactant", sub, e5),
        participant("phi", "reactant", "PhI", e5, name="iodobenzene", amounts=(("equivalents", {"number": 1.5, "unit": "equiv"}),), smiles="Ic1ccccc1"),
        participant("pd_oac2", "catalyst", "Pd(OAc)2", e5, amounts=(("catalyst_loading", {"number": 5, "unit": "mol%"}),)),
        participant("pph3", "reagent", "PPh3", e5, amounts=(("ligand_loading", {"number": 10, "unit": "mol%"}),)),
        participant("k2co3", "reagent", "K2CO3", e5, amounts=(("equivalents", {"number": 2, "unit": "equiv"}),)),
        participant("ch3cn", "solvent", "CH3CN", e5),
        participant("expected_product", "product", f"expected eight-membered lactone from {sub}", e5),
    ]
    cond = [fld("temperature", {"number": 85, "unit": "°C"}, e5), fld("time", {"number": hours, "unit": "h"}, e5), fld("atmosphere", None), fld("workup", None), fld("purification", None)]
    records.append(record(f"scheme4_{sub}_{outcome.replace(' ', '_')}", "substrate_scope_entry", e5, ps,
        [step("coupling_cyclization", [p["entity_id"] for p in ps], cond)],
        [fld("reaction_outcome", outcome, e5, ["expected_product"])],
        ("The source explicitly reports failure/complex outcome rather than an isolated product yield.",),
        ("No product identity, yield, workup, or purification is reported.", "Substrate structure remains unverified.")))

# Page 6, Scheme 5: mechanistic rationale, not a separate experiment.
e56 = [ev(5, "image"), ev(5, "text"), ev(6, "image"), ev(6, "text")]
mech5_ps = [
    participant("substrate_1a", "reactant", "1a", e56),
    participant("phpdi", "reactant", "PhPdI", e56),
    participant("anti_6", "unspecified_agent", "anti-6 pi-allylic palladium intermediate", e56),
    participant("syn_6", "unspecified_agent", "syn-6 pi-allylic palladium intermediate", e56),
    participant("product_2a", "product", "2a", e56),
    participant("product_3a", "product", "3a", e56),
]
records.append(record("scheme5_regio_stereochemical_rationale", "mechanism", e56, mech5_ps, notes=(
    "The authors propose that steric effects favor anti-6 over syn-6 and that carbon attack at the less substituted terminus affords 2a; the depicted route to 3a is disfavored.",
    "Scheme 5 is a mechanistic rationale and does not represent an independent reported batch.",
), unresolved=("Mechanistic intermediate structures and causal interpretation remain unverified machine extraction.",)))

# Sanity checks and output.
ids = [r["record_id"] for r in records]
assert len(ids) == len(set(ids))
assert len(records) == 56, len(records)

OUT.mkdir(parents=True, exist_ok=True)
(OUT / "records_pages_0001_0006.json").write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")

# Required page coverage ledger. Every region cites its same-page original image.
by_suffix = {r["source_reaction_id"]: r["record_id"] for r in records}
scheme1_ids = [r["record_id"] for r in records if r["source_reaction_id"].startswith("scheme1_")]
table1_ids = [by_suffix[x] for x in ["table1_entry1", "table1_entry2_table2_entry1", "table1_entry3", "table1_entry4", "prose_90min"]]
table2_ids = [by_suffix["table1_entry2_table2_entry1"]] + [by_suffix[f"table2_entry{i}"] for i in range(2, 12)]
table3_ids = [r["record_id"] for r in records if r["source_reaction_id"].startswith("table3_")]
table4_ids = [r["record_id"] for r in records if r["source_reaction_id"].startswith("table4_")]
scheme3_ids = [r["record_id"] for r in records if r["source_reaction_id"].startswith("scheme3_")]
scheme4_ids = [r["record_id"] for r in records if r["source_reaction_id"].startswith("scheme4_")]
coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {"page": 1, "state": "attempted", "regions": [
            {"region": "title, abstract, introduction, and Figure 1", "finding": "No new batch experiment is reported. Figure 1 shows cited natural lactones, and the prose summarizes prior literature; these were classified as background rather than experiments from this paper.", "evidence_ids": [ev(1, "image"), ev(1, "text")]}
        ], "record_ids": [], "unresolved": ["Supporting information is mentioned but was not explicitly supplied or associated, so it was not imported."]},
        {"page": 2, "state": "attempted", "regions": [
            {"region": "upper Scheme 1", "finding": "Thirteen individually yielded starting-material preparations were extracted from three reaction arrows: six DMAP/lactone couplings, two PPh3 ester-exchange reactions, and five NaH alkylations.", "evidence_ids": [ev(2, "image"), ev(2, "text")]},
            {"region": "middle Scheme 2", "finding": "Possible C-attack/O-attack products and anti/syn pi-allylic palladium intermediates were classified as a mechanism/product map, not an independent experiment.", "evidence_ids": [ev(2, "image"), ev(2, "text")]},
            {"region": "lower-right opening Results and Discussion", "finding": "Table 1 entry 1 conditions and negative side-product observations were linked to the corresponding page-3 optimization row instead of duplicated.", "evidence_ids": [ev(2, "image"), ev(2, "text"), ev(3, "image"), ev(3, "text")]}
        ], "record_ids": scheme1_ids + [by_suffix["scheme2_possible_products"], by_suffix["table1_entry1"]], "unresolved": ["Scheme 1 omits times, most reagent quantities, workups, purification, and yield bases.", "Scheme 2 structures are mechanistic candidates and remain unverified."]},
        {"page": 3, "state": "attempted", "regions": [
            {"region": "upper-left Table 1 and footnotes", "finding": "Four catalyst/temperature optimization rows were extracted; recovery of 1a and isolated versus NMR yields were kept separate. The 90-minute narrative trial was extracted as an additional condition.", "evidence_ids": [ev(3, "image"), ev(3, "text")]},
            {"region": "upper-right Table 2 and footnotes", "finding": "Eleven solvent/base rows were represented; Table 2 entry 1 was merged with identical Table 1 entry 2. Trace yield in entry 11 was preserved qualitatively.", "evidence_ids": [ev(3, "image"), ev(3, "text")]},
            {"region": "lower discussion", "finding": "Scope commentary and the standard-condition statement were used only to interpret Tables 3 and 4 on page 4; broad claims were not duplicated as experiments.", "evidence_ids": [ev(3, "image"), ev(3, "text")]}
        ], "record_ids": list(dict.fromkeys(table1_ids + table2_ids)), "unresolved": ["Optimization rows omit workup and purification.", "Structures identified by 1a/2a and related labels remain machine-unverified."]},
        {"page": 4, "state": "attempted", "regions": [
            {"region": "upper-left Table 3 and footnotes", "finding": "Eight substrate rows were extracted, including the visually separate 1j row with the source's duplicated/missing entry numbering, all 100 °C overrides, and the 2.5-equivalent PhI overrides.", "evidence_ids": [ev(4, "image"), ev(4, "text")]},
            {"region": "upper-right Table 4 and footnotes", "finding": "Ten organic-halide scope rows were extracted with distinct R labels, times, isolated yields, and shared conditions.", "evidence_ids": [ev(4, "image"), ev(4, "text")]},
            {"region": "lower Scheme 3", "finding": "Five nine- and ten-membered lactone reactions (E-2q through E-2u) were extracted with times and yields.", "evidence_ids": [ev(4, "image"), ev(4, "text")]},
            {"region": "Figure 2", "finding": "ORTEP of 2m supports the paper's structural assignment discussion but was not treated as an additional reaction or as automatic structure verification.", "evidence_ids": [ev(4, "image"), ev(4, "text")]}
        ], "record_ids": table3_ids + table4_ids + scheme3_ids, "unresolved": ["Scope tables omit atmosphere, workup, purification, and most exact masses.", "The 1j row's printed entry number is ambiguous, so its record ID uses row_1j."]},
        {"page": 5, "state": "attempted", "regions": [
            {"region": "upper Figure 3 and adjacent prose", "finding": "X-ray representations of E-2s and E-2u and the one-gram-scale 2q statement were linked to their Scheme 3 records without certifying structures.", "evidence_ids": [ev(5, "image"), ev(5, "text")]},
            {"region": "lower Scheme 4", "finding": "Three distinct outcomes were extracted: 1k to 2x (65%, >8:1 dr), 1l with no reaction, and 1m with a complicated outcome.", "evidence_ids": [ev(5, "image"), ev(5, "text")]},
            {"region": "middle mechanistic discussion", "finding": "The anti-6/syn-6 rationale was classified with Scheme 5 as mechanism, not as an extra batch experiment.", "evidence_ids": [ev(5, "image"), ev(5, "text"), ev(6, "image"), ev(6, "text")]}
        ], "record_ids": [by_suffix["scheme3_e_2q"], by_suffix["scheme3_e_2s"], by_suffix["scheme3_e_2u"]] + scheme4_ids + [by_suffix["scheme5_regio_stereochemical_rationale"]], "unresolved": ["The source does not identify products or yields for the no-reaction and complicated rows.", "X-ray depictions do not by themselves make machine SMILES verified."]},
        {"page": 6, "state": "attempted", "regions": [
            {"region": "upper-left Figure 4", "finding": "ORTEP of 2x was linked to the page-5 Scheme 4 success record as structural evidence, without machine certification.", "evidence_ids": [ev(6, "image"), ev(6, "text"), ev(5, "image"), ev(5, "text")]},
            {"region": "right-column General Information and Typical Procedure for 2a", "finding": "Exact reagent masses/amounts, argon atmosphere, 85 °C operation, workup, chromatography, product mass, and 73% yield were merged into Table 3 entry 1.", "evidence_ids": [ev(6, "image"), ev(6, "text"), ev(4, "image"), ev(4, "text")]},
            {"region": "lower-right beginning of 2b preparation", "finding": "Visible reagent masses and amounts were merged into Table 3 entry 2; the continuation on page 7 was not imported or claimed as covered.", "evidence_ids": [ev(6, "image"), ev(6, "text"), ev(4, "image"), ev(4, "text")]},
            {"region": "bottom Scheme 5", "finding": "Regio-/stereoselectivity rationale was stored as a mechanism record, not an independent experiment.", "evidence_ids": [ev(6, "image"), ev(6, "text")]}
        ], "record_ids": [by_suffix["scheme4_1k_to_2x"], by_suffix["table3_entry1"], by_suffix["table3_entry2"], by_suffix["scheme5_regio_stereochemical_rationale"]], "unresolved": ["The 2b paragraph continues beyond page 6, so the missing continuation operations and product mass are not claimed.", "SI was not associated and missing operational details remain missing."]},
    ],
}
cov_dir = ROOT / "runs/current/coverage"
cov_dir.mkdir(parents=True, exist_ok=True)
(cov_dir / "pages_0001_0006.json").write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

# Mark only the six page tasks actually attempted in this session.
tasks_path = ROOT / "runs/current/tasks.json"
tasks = json.loads(tasks_path.read_text())
for task in tasks:
    if task["document_id"] == DOC and task["task_id"] in {ev(i, "text") for i in range(1, 7)}:
        task["state"] = "attempted"
        task["reason"] = "Page image and text inspected for experiments, schemes, tables, footnotes, failures, and missing details in session pages 1-6."
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"records": len(records), "coverage_pages": [p["page"] for p in coverage["pages"]]}, ensure_ascii=False))
