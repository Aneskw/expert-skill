#!/usr/bin/env python3
"""Build evidence-linked raw records for doc_e5bb5a4a6325144a, PDF pages 1-4."""
import json
from pathlib import Path

DOC = "doc_e5bb5a4a6325144a"
OUT = Path(__file__).with_name("extracted_records_pages_0001_0004.json")

T = {n: f"{DOC}:page{n}:text" for n in range(1, 5)}
I = {n: f"{DOC}:page{n}:image" for n in range(1, 5)}


def q(number, unit, **extra):
    return {"number": number, "unit": unit, **extra}


def f(value, ev):
    return {
        "value": value,
        "evidence_ids": list(ev) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def fld(name, value, ev, targets=None):
    item = {"name": name, "fact": f(value, ev)}
    if targets:
        item["target_entity_ids"] = list(targets)
    return item


def part(entity_id, role, label, ev, name=None, smiles=None, amounts=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": f(label, ev),
        "name": f(name, ev) if name else f(None, ()),
        "smiles": f(smiles, ev) if smiles else f(None, ()),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": amounts or [],
    }


def amount(name, value, ev):
    return fld(name, value, ev)


def rec(suffix, kind, ev, participants, conditions, outcomes, notes=None, unresolved=None):
    return {
        "record_id": f"{DOC}:{suffix}",
        "document_id": DOC,
        "source_reaction_id": suffix,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": list(dict.fromkeys(ev)),
        "participants": participants,
        "steps": [{
            "step_id": "reaction",
            "participant_ids": [p["entity_id"] for p in participants],
            "conditions": conditions,
        }] if participants or conditions else [],
        "outcomes": outcomes,
        "notes": [f(x, ev) for x in (notes or [])],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved or [
                "No Supporting Information file was supplied or explicitly associated.",
                "Product structures are retained by source label and image; product SMILES remain unverified or missing.",
            ],
        },
    }


def p1a(ev, amounts=None):
    return part("r_1a", "reactant", "1a", ev,
                "dimethyl 2-(2,3-butadienyl)malonate",
                "COC(=O)C(CC=C=C)C(=O)OC", amounts)


def p4a(ev, amounts=None):
    return part("r_4a", "reactant", "4a", ev,
                "N-benzylidene p-toluenesulfonamide",
                "Cc1ccc(S(=O)(=O)N=Cc2ccccc2)cc1", amounts)


def phi(ev, amounts=None, label="PhI"):
    return part("r_halide", "reactant", label, ev, "iodobenzene", "Ic1ccccc1", amounts)


def catalyst(ev, amounts=None):
    return part("cat_pd", "catalyst", "[Pd(PPh3)4]", ev,
                "tetrakis(triphenylphosphine)palladium(0)", None, amounts or [amount("catalyst_loading", q(5, "mol%"), ev)])


def base_part(name, ev):
    info = {
        "K2CO3": ("potassium carbonate", "[K+].[K+].[O-]C([O-])=O"),
        "Na2CO3": ("sodium carbonate", "[Na+].[Na+].[O-]C([O-])=O"),
        "Cs2CO3": ("cesium carbonate", "[Cs+].[Cs+].[O-]C([O-])=O"),
        "NaH": ("sodium hydride", "[Na+].[H-]"),
    }[name]
    equiv = 1.1 if name == "NaH" else 4.0
    return part("base", "reagent", name, ev, info[0], info[1], [amount("equivalents", q(equiv, "equiv"), ev)])


SOLVENTS = {
    "CH3CN": ("acetonitrile", "CC#N"),
    "DMF": ("N,N-dimethylformamide", "CN(C)C=O"),
    "toluene": ("toluene", "Cc1ccccc1"),
    "THF": ("tetrahydrofuran", "C1CCOC1"),
    "1,4-dioxane": ("1,4-dioxane", "C1COCCO1"),
}


def solvent(name, ev, volume=None):
    nm, smi = SOLVENTS[name]
    amts = [amount("volume", q(volume, "mL"), ev)] if volume is not None else []
    return part("solvent", "solvent", name, ev, nm, smi, amts)


def product(entity_id, label, ev, name=None):
    return part(entity_id, "product", label, ev, name)


records = []

# Page 2, Scheme 1 is a conceptual/general protocol, not a reported experiment.
ev2 = [I[2], T[2]]
records.append(rec(
    "scheme1_general_protocol", "general_scheme", ev2,
    [part("generic_allene", "reactant", "1", ev2, "functionalized allene"),
     part("generic_rx", "reactant", "RX", ev2, "organohalide"),
     part("generic_imine", "reactant", "4", ev2, "imine"),
     product("generic_pyrrolidine", "5", ev2, "pyrrolidine derivative")],
    [], [],
    notes=["Scheme 1 contrasts path A products 2/3 with relay path B products 5/6; it is a protocol diagram without an experimental yield."],
    unresolved=["Generic R groups and the conceptual intermediate are not fully specified; no SMILES was assigned."]
))


def table1_participants(row, ev):
    if row["entry"] == 14:
        a1 = [amount("mass", q(46, "mg"), ev), amount("amount", q(0.25, "mmol"), ev)]
        ph = [amount("mass", q(61, "mg"), ev), amount("amount", q(0.3, "mmol"), ev), amount("equivalents", q(1.2, "equiv"), ev)]
        im = [amount("mass", q(78, "mg"), ev), amount("amount", q(0.3, "mmol"), ev), amount("equivalents", q(1.2, "equiv"), ev)]
        bp = base_part(row["base"], ev)
        bp["amounts"] = [amount("mass", q(138, "mg"), ev), amount("amount", q(1.0, "mmol"), ev), amount("equivalents", q(4.0, "equiv"), ev)]
        cp = catalyst(ev, [amount("mass", q(14.5, "mg"), ev), amount("amount", q(0.0125, "mmol"), ev), amount("catalyst_loading", q(5, "mol%"), ev)])
        sp = solvent(row["solvent"], ev, 3)
    else:
        a1 = []
        ph = [amount("equivalents", q(1.2, "equiv"), ev)]
        im = [amount("equivalents", q(row["imine"], "equiv"), ev)]
        bp, cp, sp = base_part(row["base"], ev), catalyst(ev), solvent(row["solvent"], ev)
    ps = [p1a(ev, a1), phi(ev, ph), p4a(ev, im), bp, cp, sp]
    if row["additive"] == "A":
        ps.append(part("additive", "reagent", "nBu4NBr", ev, "tetrabutylammonium bromide", "[Br-].CCCC[N+](CCCC)(CCCC)CCCC", [amount("loading", q(10, "mol%"), ev)]))
    elif row["additive"] == "B":
        ps.append(part("additive", "reagent", "Cu(OTf)2", ev, "copper(II) triflate", None, [amount("loading", q(10, "mol%"), ev)]))
    ps += [product("p_5a", "5a", ev, "cis-pyrrolidine derivative 5a"), product("p_2a", "2a", ev, "cyclopropane derivative 2a")]
    if row.get("y3") is not None:
        ps.append(product("p_3a", "3a", ev, "cyclopentene derivative 3a"))
    return ps


table1 = [
    dict(entry=1, base="K2CO3", additive=None, imine=1.2, solvent="CH3CN", temp="reflux", time=11, y5=71, ratio="86:14", y2=0),
    dict(entry=2, base="K2CO3", additive="A", imine=1.2, solvent="CH3CN", temp="reflux", time=10, y5=82, ratio="90:10", y2=0),
    dict(entry=3, base="Cs2CO3", additive="A", imine=1.2, solvent="CH3CN", temp="reflux", time=11, y5="trace", ratio=None, y2=43, y3=4),
    dict(entry=4, base="Na2CO3", additive="A", imine=1.2, solvent="CH3CN", temp="reflux", time=11, y5=89, ratio="95:5", y2=0),
    dict(entry=5, base="NaH", additive=None, imine=1.2, solvent="DMF", temp=85, time=11, y5=31, ratio="86:14", y2=0, y3=57),
    dict(entry=6, base="K2CO3", additive=None, imine=1.2, solvent="DMF", temp=85, time=12, y5=73, ratio="75:25", y2=0, y3=5),
    dict(entry=7, base="K2CO3", additive="A", imine=1.2, solvent="toluene", temp=85, time=12, y5=63, ratio="80:20", y2=8),
    dict(entry=8, base="K2CO3", additive=None, imine=1.2, solvent="THF", temp="reflux", time=11, y5=72, ratio=">99:1", y2=26),
    dict(entry=9, base="Na2CO3", additive=None, imine=1.2, solvent="THF", temp="reflux", time=36, y5=65, ratio=">99:1", y2=11),
    dict(entry=10, base="K2CO3", additive=None, imine=3.0, solvent="THF", temp=40, time=58, y5=82, ratio=">99:1", y2=10),
    dict(entry=11, base="K2CO3", additive=None, imine=3.0, solvent="THF", temp="reflux", time=12, y5=88, ratio=">99:1", y2=8),
    dict(entry=12, base="K2CO3", additive="B", imine=3.0, solvent="THF", temp="reflux", time=11, y5=89, ratio="96:4", y2=5),
    dict(entry=13, base="K2CO3", additive=None, imine=3.0, solvent="THF", temp=85, time=11, y5=90, ratio=">99:1", y2=0, screw=True),
    dict(entry=14, base="K2CO3", additive=None, imine=1.2, solvent="THF", temp=85, time=10, y5=86, ratio=">99:1", y2=0, screw=True),
    dict(entry=15, base="K2CO3", additive=None, imine=1.2, solvent="THF", temp=100, time=10, y5=87, ratio="98:2", y2=0, screw=True),
    dict(entry=16, base="K2CO3", additive=None, imine=1.2, solvent="1,4-dioxane", temp=85, time=7, y5=86, ratio=">99:1", y2=0),
    dict(entry=17, base="K2CO3", additive=None, imine=1.2, solvent="1,4-dioxane", temp="reflux", time=6, y5=75, ratio=">99:1", y2=0),
]

for row in table1:
    ev = [I[3], T[3]]
    if row["entry"] == 2:
        ev += [I[2], T[2]]  # Scheme 2 first row is the same conditions/result.
    if row["entry"] == 14:
        ev += [I[4], T[4]]  # characterization continues at the top of page 4.
    participants = table1_participants(row, ev)
    conditions = [fld("solvent", row["solvent"], ev),
                  fld("temperature", row["temp"] if isinstance(row["temp"], str) else q(row["temp"], "°C"), ev),
                  fld("time", q(row["time"], "h"), ev)]
    notes = []
    if row.get("screw"):
        conditions.append(fld("operation", "reaction carried out in a tube with a screw cap", ev))
    if row["entry"] == 14:
        conditions += [fld("atmosphere", "nitrogen", ev), fld("operation", "heated and monitored by TLC", ev),
                       fld("workup", "evaporation", ev),
                       fld("purification", "flash column chromatography on silica gel; petroleum ether/ether 3:1", ev)]
        notes += ["The typical procedure says 'overnight' while Table 1 entry 14 reports 10 h; the table time is structured and the wording discrepancy is retained.",
                  "cis-5a was reported as a white solid, m.p. 146-147 °C, with NMR, MS, IR, and elemental analysis continuing on page 4."]
    if row["entry"] == 2:
        notes.append("The page-2 prose says 89% and cis/trans 9:1 for the same displayed conditions, whereas Scheme 2 and Table 1 entry 2 report 82% and 90:10; the tabulated/diagrammed values are structured and the prose conflict is unresolved.")
    outcomes = [fld("yield_5a", row["y5"] if isinstance(row["y5"], str) else q(row["y5"], "%"), ev, ["p_5a"]),
                fld("cis_trans_ratio_5a", row["ratio"], ev, ["p_5a"]),
                fld("yield_2a", q(row["y2"], "%"), ev, ["p_2a"])]
    if row.get("y3") is not None:
        outcomes.append(fld("yield_3a", q(row["y3"], "%"), ev, ["p_3a"]))
    if row["entry"] == 14:
        outcomes += [fld("product_mass", q(111, "mg"), ev, ["p_5a"]),
                     fld("yield_measurement_basis", "pure product after flash chromatography", ev, ["p_5a"]),
                     fld("melting_point", {"minimum": 146, "maximum": 147, "unit": "°C", "raw_text": "146-147 °C"}, ev, ["p_5a"])]
    records.append(rec(f"table1_entry_{row['entry']:02d}", "optimization_entry", ev, participants, conditions, outcomes, notes=notes))


# Scheme 2 rows not already duplicated by Table 1 entry 2.
scheme2_rows = [
    ("ptol_k2co3", "p-CH3C6H4I", "4-iodotoluene", "Cc1ccc(I)cc1", 1.2, "K2CO3", 92, "5b", "86:14"),
    ("otol_k2co3", "o-CH3C6H4I", "2-iodotoluene", "Cc1ccccc1I", 3.0, "K2CO3", 36, "5c", "94:6"),
    ("otol_na2co3", "o-CH3C6H4I", "2-iodotoluene", "Cc1ccccc1I", 3.0, "Na2CO3", 57, "5c", ">99:1"),
]
for suffix, hal_label, hal_name, hal_smi, im_eq, base_name, yld, prod_label, ratio in scheme2_rows:
    ev = ev2
    ps = [p1a(ev), part("r_halide", "reactant", hal_label, ev, hal_name, hal_smi, [amount("equivalents", q(1.2, "equiv"), ev)]),
          p4a(ev, [amount("equivalents", q(im_eq, "equiv"), ev)]), base_part(base_name, ev), catalyst(ev), solvent("CH3CN", ev),
          part("additive", "reagent", "nBu4NBr", ev, "tetrabutylammonium bromide", "[Br-].CCCC[N+](CCCC)(CCCC)CCCC", [amount("loading", q(10, "mol%"), ev)]),
          product("p_main", prod_label, ev, f"pyrrolidine derivative {prod_label}")]
    records.append(rec(f"scheme2_{suffix}", "optimization_entry", ev, ps,
                       [fld("solvent", "CH3CN", ev), fld("temperature", "reflux", ev), fld("time", "overnight", ev)],
                       [fld("yield", q(yld, "%"), ev, ["p_main"]), fld("cis_trans_ratio", ratio, ev, ["p_main"])]))


HALIDES = {
    "p-CH3C6H4I": ("4-iodotoluene", "Cc1ccc(I)cc1"),
    "p-MeOC6H4I": ("4-iodoanisole", "COc1ccc(I)cc1"),
    "p-MeO2CC6H4I": ("methyl 4-iodobenzoate", "COC(=O)c1ccc(I)cc1"),
    "thienyl-I": ("iodothiophene (position not specified in table text)", None),
    "(E)-PhCH=CHI": ("(E)-phenylvinyl iodide", None),
    "(E)-nBuCH=CHI": ("(E)-butylvinyl iodide", None),
    "C6H5Br": ("bromobenzene", "Brc1ccccc1"),
    "C6H5OTf": ("phenyl triflate", "O=S(=O)(Oc1ccccc1)C(F)(F)F"),
}

table2 = [
    (1, "p-CH3C6H4I", 3.0, "THF", "reflux", 92, "5b", ">99:1", 6, "2b"),
    (2, "p-CH3C6H4I", 1.2, "THF", 85, 92, "5b", "97:3", 0, "2b"),
    (3, "p-MeOC6H4I", 1.2, "THF", 85, 85, "5d", "95:5", 3, "2d"),
    (4, "p-MeOC6H4I", 3.0, "THF", 85, 84, "5d", "95:5", 0, "2d"),
    (5, "p-MeOC6H4I", 1.2, "1,4-dioxane", 85, 90, "5d", ">98:2", 0, "2d"),
    (6, "p-MeOC6H4I", 1.2, "1,4-dioxane", "reflux", 81, "5d", ">98:2", 0, "2d"),
    (7, "p-MeO2CC6H4I", 3.0, "THF", 85, 92, "5e", ">99:1", 6, "2e"),
    (8, "p-MeO2CC6H4I", 3.0, "1,4-dioxane", "reflux", 92, "5e", ">99:1", 7, "2e"),
    (9, "p-MeO2CC6H4I", 1.2, "1,4-dioxane", "reflux", 64, "5e", ">99:1", 35, "2e"),
    (10, "thienyl-I", 3.0, "THF", 85, 100, "5f", ">99:1", 0, "2"),
    (11, "(E)-PhCH=CHI", 3.0, "THF", 85, 96, "5g", "97:3", 0, "2"),
    (12, "(E)-PhCH=CHI", 1.2, "1,4-dioxane", 85, 83, "5g", "95:5", 0, "2"),
    (13, "(E)-nBuCH=CHI", 1.2, "THF", 85, 84, "5h", "96:4", 0, "2"),
    (14, "(E)-nBuCH=CHI", 1.2, "1,4-dioxane", 85, 84, "5h", "97:3", 0, "2"),
    (15, "C6H5Br", 3.0, "THF", 85, 82, "5a", ">98:2", 0, "2a"),
    (16, "C6H5OTf", 3.0, "THF", 85, 86, "5a", "96:4", 0, "2a"),
]

for entry, hal_label, im_eq, solv, temp, y5, lab5, ratio, y2, lab2 in table2:
    ev = [I[3], T[3]]
    hname, hsmi = HALIDES[hal_label]
    ps = [p1a(ev), part("r_halide", "reactant", hal_label, ev, hname, hsmi, [amount("equivalents", q(1.2, "equiv"), ev)]),
          p4a(ev, [amount("equivalents", q(im_eq, "equiv"), ev)]), base_part("K2CO3", ev), catalyst(ev), solvent(solv, ev),
          product("p_main", lab5, ev, f"cis-pyrrolidine derivative {lab5}"), product("p_side", lab2, ev, f"cyclopropane derivative {lab2}")]
    conditions = [fld("solvent", solv, ev), fld("temperature", temp if isinstance(temp, str) else q(temp, "°C"), ev), fld("time", "overnight", ev)]
    outcomes = [fld("yield_main_product", q(y5, "%"), ev, ["p_main"]), fld("cis_trans_ratio", ratio, ev, ["p_main"]), fld("yield_cyclopropane_product", q(y2, "%"), ev, ["p_side"])]
    records.append(rec(f"table2_entry_{entry:02d}", "substrate_scope_entry", ev, ps, conditions, outcomes))


# A separately stated low-reactivity imine result on page 3.
ev3 = [I[3], T[3]]
ps = [p1a(ev3), phi(ev3, [amount("equivalents", q(1.2, "equiv"), ev3)]),
      part("r_imine", "reactant", "N-(4-chlorobenzylidene)aniline", ev3, "N-(4-chlorobenzylidene)aniline", "Clc1ccc(C=Nc2ccccc2)cc1"),
      product("p_2a", "2a", ev3, "cyclopropane derivative 2a")]
records.append(rec("prose_n_4_chlorobenzylidene_aniline", "substrate_scope_entry", ev3, ps, [],
                   [fld("yield_2a", q(92, "%"), ev3, ["p_2a"]), fld("product_distribution", "2a was the only product", ev3, ["p_2a"])],
                   notes=["The prose calls this the corresponding reaction but does not restate solvent, base, catalyst loading, temperature, time, or imine amount; those conditions were not inferred."],
                   unresolved=["Reaction conditions and imine amount are not explicitly restated for this prose-only result.", "No Supporting Information file was supplied or explicitly associated."]))


IMINES = {
    "4b": ("N-(4-nitrobenzylidene)-p-toluenesulfonamide", "Cc1ccc(S(=O)(=O)N=Cc2ccc([N+](=O)[O-])cc2)cc1"),
    "4c": ("N-(4-methoxybenzylidene)-p-toluenesulfonamide", "COc1ccc(C=NS(=O)(=O)c2ccc(C)cc2)cc1"),
    "4d": ("N-(4-chlorobenzylidene)-p-toluenesulfonamide", "Clc1ccc(C=NS(=O)(=O)c2ccc(C)cc2)cc1"),
}

table3 = [
    (1, "p-O2NC6H4", "4b", 1.2, "THF", 89, "5i", "95:5", 0),
    (2, "p-O2NC6H4", "4b", 1.2, "1,4-dioxane", 95, "5i", "97:3", 0),
    (3, "p-MeOC6H4", "4c", 1.2, "THF", 52, "5j", ">99:1", 42),
    (4, "p-MeOC6H4", "4c", 3.0, "THF", 99, "5j", ">99:1", 0),
    (5, "p-MeOC6H4", "4c", 1.2, "1,4-dioxane", 52, "5j", "97:3", 29),
    (6, "p-ClC6H4", "4d", 1.2, "THF", 95, "5k", ">98:2", 0),
]

for entry, r_label, im_label, im_eq, solv, y5, lab5, ratio, y2 in table3:
    ev = [I[4], T[4]]
    iname, ismi = IMINES[im_label]
    ps = [p1a(ev), phi(ev, [amount("equivalents", q(1.2, "equiv"), ev)]),
          part("r_imine", "reactant", f"{r_label} ({im_label})", ev, iname, ismi, [amount("equivalents", q(im_eq, "equiv"), ev)]),
          base_part("K2CO3", ev), catalyst(ev), solvent(solv, ev),
          product("p_main", lab5, ev, f"cis-pyrrolidine derivative {lab5}"), product("p_2a", "2a", ev, "cyclopropane derivative 2a")]
    records.append(rec(f"table3_entry_{entry:02d}", "substrate_scope_entry", ev, ps,
                       [fld("solvent", solv, ev), fld("temperature", q(85, "°C"), ev), fld("time", "overnight", ev)],
                       [fld("yield_main_product", q(y5, "%"), ev, ["p_main"]), fld("cis_trans_ratio", ratio, ev, ["p_main"]), fld("yield_2a", q(y2, "%"), ev, ["p_2a"])]))


# Scheme 3, supported by page-3 prose and the full arrow on page 4.
ev34 = [I[3], T[3], I[4], T[4]]
ps = [part("r_1b", "reactant", "1b", ev34, "dimethyl 2-(2,3-decadienyl)malonate", None),
      phi(ev34, [amount("equivalents", q(1.2, "equiv"), ev34)]),
      p4a(ev34, [amount("equivalents", q(3.0, "equiv"), ev34)]),
      base_part("K2CO3", ev34), catalyst(ev34), solvent("THF", ev34),
      product("p_5l", "5l", ev34, "cis-pyrrolidine derivative 5l")]
records.append(rec("scheme3_5l", "substrate_scope_entry", ev34, ps,
                   [fld("solvent", "THF", ev34), fld("temperature", q(85, "°C"), ev34), fld("time", q(8, "h"), ev34)],
                   [fld("yield_5l", q(85, "%"), ev34, ["p_5l"]), fld("alkene_E_Z_ratio", "79:21", ev34, ["p_5l"]), fld("cis_trans_ratio", ">99:1", ev34, ["p_5l"])],
                   notes=["The C=C configuration in 5l was assigned from 1H,1H NOESY spectra."]))


OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"output": str(OUT), "records": len(records)}, ensure_ascii=False))
