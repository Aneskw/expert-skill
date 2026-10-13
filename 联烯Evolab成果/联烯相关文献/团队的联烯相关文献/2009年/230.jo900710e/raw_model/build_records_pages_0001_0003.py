#!/usr/bin/env python3
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
DOC = "doc_871f2b557075944e"
P1 = [f"{DOC}:page1:image", f"{DOC}:page1:text"]
P2 = [f"{DOC}:page2:image", f"{DOC}:page2:text"]
P3 = [f"{DOC}:page3:image", f"{DOC}:page3:text"]


def fact(value, ev):
    return {"value": value, "evidence_ids": list(ev) if value is not None else [],
            "verification": "unreviewed" if value is not None else "missing"}


def qty(number, unit, **extra):
    return {"number": number, "unit": unit, **extra}


def fld(name, value, ev, targets=None):
    x = {"name": name, "fact": fact(value, ev)}
    if targets:
        x["target_entity_ids"] = targets
    return x


def part(entity_id, role, label, ev, smiles=None, amounts=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, ev),
        "name": fact(None, []),
        "smiles": fact(smiles, ev) if smiles else fact(None, []),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": amounts or [],
    }


def step(step_id, participant_ids, ev, temperature=None, time=None,
         atmosphere=None, operation=None, workup=None, purification=None):
    values = [
        ("temperature", temperature), ("time", time),
        ("atmosphere", atmosphere), ("operation", operation),
        ("workup", workup), ("purification", purification),
    ]
    return {"step_id": step_id, "participant_ids": participant_ids,
            "conditions": [fld(n, v, ev) for n, v in values]}


def rec(rid, kind, ev, participants, steps, outcomes, notes=None, unresolved=None):
    return {
        "record_id": f"{DOC}:{rid}", "document_id": DOC,
        "source_reaction_id": rid, "record_kind": kind,
        "status": "candidate", "completeness": "partial",
        "evidence_ids": list(dict.fromkeys(ev)), "participants": participants,
        "steps": steps, "outcomes": outcomes,
        "notes": [fact(x, ev) for x in (notes or [])],
        "review": {"method": "none", "reviewer": None, "checked_fields": [],
                   "unresolved": unresolved or []},
    }


records = []

# Page 1 graphical abstract: a scope-level summary, not a batch experiment.
ga_parts = [
    part("ga_path_a", "reactant", "optically active terminal propargylic alcohols 1", P1),
    part("ga_path_b", "reactant", "racemic 1-substituted 4-chloro-2-butyn-1-ols", P1),
    part("ga_chloro", "product", "optically active 1-substituted 4-chloro-2-butyn-1-ols 3", P1),
    part("ga_grignard", "reagent", "R2MgBr", P1,
         amounts=[fld("equivalents", qty(3, "equiv"), P1)]),
    part("ga_cucn", "catalyst", "CuCN", P1,
         amounts=[fld("catalyst_loading", qty(5, "mol%"), P1)]),
    part("ga_ether", "solvent", "Et2O", P1, "CCOCC"),
    part("ga_product", "product", "optically active secondary 2,3-allenols", P1),
]
records.append(rec(
    "graphical_abstract_general_route", "general_scheme", P1, ga_parts,
    [step("summary", [p["entity_id"] for p in ga_parts], P1,
          temperature=qty(-60, "°C"), operation="Two generic starting-material routes converge on CuCN-catalyzed Grignard conversion to allenols.")],
    [fld("scope_yield", {"minimum": 60, "maximum": 89, "unit": "%", "raw_text": "60–89%"}, P1, ["ga_product"]),
     fld("scope_ee", {"minimum": 96, "maximum": 99, "unit": "%", "raw_text": "96–>99%"}, P1, ["ga_product"])],
    unresolved=["This is a graphical scope summary, not an individual experimental batch.",
                "Generic R groups and absolute structures are unresolved."]))

# Scheme 1: five racemic starting-material preparations.
scheme1 = [
    ("3a", "Ph", "benzaldehyde", "O=Cc1ccccc1", "OC(c1ccccc1)C#CCCl", 42),
    ("3b", "p-CH3C6H4", "p-tolualdehyde", "Cc1ccc(C=O)cc1", "OC(c1ccc(C)cc1)C#CCCl", 46),
    ("3c", "n-C5H11", "hexanal", "CCCCCC=O", "CCCCCC(O)C#CCCl", 52),
    ("3d", "CH3", "acetaldehyde", "CC=O", "CC(O)C#CCCl", 88),
    ("3e", "C2H5", "propanal", "CCC=O", "CCC(O)C#CCCl", 93),
]
for label, rgroup, aldehyde, aldehyde_smiles, product_smiles, y in scheme1:
    rid = f"scheme1_{label}"
    ps = [
        part(f"{rid}_propargyl_chloride", "reactant", "propargylic chloride", P2, "C#CCCl"),
        part(f"{rid}_nbuli", "reagent", "n-BuLi", P2, "[Li]CCCC"),
        part(f"{rid}_aldehyde", "reactant", aldehyde, P2, aldehyde_smiles),
        part(f"{rid}_product", "product", f"racemic {label}, R={rgroup}", P2, product_smiles),
    ]
    records.append(rec(rid, "substrate_scope_entry", P2, ps,
        [step("formation", [x["entity_id"] for x in ps], P2,
              temperature=qty(-78, "°C"),
              operation="n-BuLi treatment, aldehyde addition at -78 °C, then warming from -78 °C to room temperature")],
        [fld("reported_yield", qty(y, "%"), P2, [f"{rid}_product"]),
         fld("yield_measurement_basis", None, P2)],
        unresolved=["Yield basis, scale, duration, atmosphere, workup, and purification are not stated.",
                    "Candidate connectivity is unverified. Absolute stereochemistry is not applicable to the racemate. "]))

# Scheme 2: three homologations and three selective chlorinations.
scheme2 = [
    ("a", "Ph", "(S)-1a", "C#CC(O)c1ccccc1", 98.7, "(R)-2a", "OCC#CC(O)c1ccccc1", 65,
     "(R)-3a", "OC(c1ccccc1)C#CCCl", 96.8, 63),
    ("b", "p-CH3C6H4", "(S)-1b", "C#CC(O)c1ccc(C)cc1", 99.9, "(R)-2b", "OCC#CC(O)c1ccc(C)cc1", 69,
     "(R)-3b", "OC(c1ccc(C)cc1)C#CCCl", 93.6, 51),
    ("c", "n-C5H11", "(R)-1c", "C#CC(O)CCCCC", 99.3, "(R)-2c", "OCC#CC(O)CCCCC", 66,
     "(R)-3c", "CCCCCC(O)C#CCCl", 96.8, 41),
]
for suffix, rgroup, s1, sm1, ee1, s2, sm2, y2, s3, sm3, ee3, y3 in scheme2:
    rid = f"scheme2_{s1.lower().replace('(','').replace(')','').replace('-','_')}_to_{s2.lower().replace('(','').replace(')','').replace('-','_')}"
    ps = [part(f"{rid}_start", "reactant", s1, P2, sm1,
               amounts=[fld("input_ee", qty(ee1, "%"), P2)]),
          part(f"{rid}_nbuli", "reagent", "n-BuLi", P2, "[Li]CCCC"),
          part(f"{rid}_formaldehyde", "reagent", "paraformaldehyde, (HCHO)n", P2),
          part(f"{rid}_thf", "solvent", "THF", P2, "C1CCOC1"),
          part(f"{rid}_product", "product", s2, P2, sm2)]
    records.append(rec(rid, "substrate_scope_entry", P2, ps,
        [step("homologation", [x["entity_id"] for x in ps], P2,
              temperature=qty(-78, "°C"), operation="n-BuLi addition in THF at -78 °C, paraformaldehyde addition at -78 °C, then warming to 0 °C")],
        [fld("reported_yield", qty(y2, "%"), P2, [f"{rid}_product"]), fld("yield_measurement_basis", None, P2)],
        unresolved=["Scale, duration, atmosphere, workup, purification, and yield basis are not stated.",
                    "Candidate stereochemistry is not encoded or verified."]))

    rid = f"scheme2_{s2.lower().replace('(','').replace(')','').replace('-','_')}_to_{s3.lower().replace('(','').replace(')','').replace('-','_')}"
    ps = [part(f"{rid}_start", "reactant", s2, P2, sm2),
          part(f"{rid}_licl", "reagent", "LiCl", P2, "[Li+].[Cl-]"),
          part(f"{rid}_collidine", "reagent", "s-collidine", P2, "Cc1cc(C)nc(C)c1"),
          part(f"{rid}_mscl", "reagent", "MsCl", P2, "CS(=O)(=O)Cl"),
          part(f"{rid}_dmf", "solvent", "DMF", P2, "CN(C)C=O"),
          part(f"{rid}_product", "product", s3, P2, sm3)]
    records.append(rec(rid, "substrate_scope_entry", P2, ps,
        [step("selective_chlorination", [x["entity_id"] for x in ps], P2,
              temperature=qty(-20, "°C"), operation="LiCl/s-collidine in DMF followed by MsCl at -20 °C, then warming to 0 °C")],
        [fld("reported_yield", qty(y3, "%"), P2, [f"{rid}_product"]),
         fld("product_ee", qty(ee3, "%"), P2, [f"{rid}_product"]), fld("yield_measurement_basis", None, P2)],
        unresolved=["Scale, duration, atmosphere, workup, purification, and yield basis are not stated.",
                    "Candidate stereochemistry is not encoded or verified."]))

# Scheme 3: kinetic resolution/enrichment and deacetylation operations.
rid = "scheme3_3d_initial_kinetic_resolution"
ps = [part(f"{rid}_start", "reactant", "racemic 3d", P2, "CC(O)C#CCCl"),
      part(f"{rid}_vinyl_acetate", "reagent", "vinyl acetate", P2, "C=COC(C)=O"),
      part(f"{rid}_enzyme", "catalyst", "Novozym 435", P2),
      part(f"{rid}_acetate", "product", "(R)-(+)-4d", P2, "CC(=O)OC(C)C#CCCl"),
      part(f"{rid}_recovered", "product", "recovered (S)-(-)-3d", P2, "CC(O)C#CCCl")]
records.append(rec(rid, "reported_experiment", P2, ps,
    [step("kinetic_resolution", [x["entity_id"] for x in ps], P2, temperature=qty(60, "°C"))],
    [fld("acetate_yield", qty(35, "%"), P2, [f"{rid}_acetate"]),
     fld("acetate_ee", qty(98.9, "%"), P2, [f"{rid}_acetate"]),
     fld("recovered_starting_material_yield", qty(42, "%"), P2, [f"{rid}_recovered"]),
     fld("recovered_starting_material_ee", qty(83.9, "%"), P2, [f"{rid}_recovered"]),
     fld("yield_measurement_basis", None, P2)],
    unresolved=["Scale, duration, solvent, atmosphere, workup, purification, and yield basis are not stated.",
                "Absolute stereochemistry is source-assigned but not encoded or verified."]))

rid = "scheme3_r_4d_deacetylation"
ps = [part(f"{rid}_start", "reactant", "(R)-(+)-4d, 98.9% ee", P2, "CC(=O)OC(C)C#CCCl"),
      part(f"{rid}_k2co3", "reagent", "K2CO3", P2, "[K+].[K+].[O-]C([O-])=O"),
      part(f"{rid}_meoh", "solvent", "CH3OH", P2, "CO"),
      part(f"{rid}_product", "product", "(R)-(+)-3d", P2, "CC(O)C#CCCl")]
records.append(rec(rid, "reported_experiment", P2, ps,
    [step("deacetylation", [x["entity_id"] for x in ps], P2)],
    [fld("reported_yield", qty(63, "%"), P2, [f"{rid}_product"]),
     fld("product_ee", qty(98.9, "%"), P2, [f"{rid}_product"]), fld("yield_measurement_basis", None, P2)],
    unresolved=["Scale, temperature, duration, atmosphere, workup, purification, and yield basis are not stated."]))

rid = "scheme3_s_3d_enrichment"
ps = [part(f"{rid}_start", "reactant", "(S)-(-)-3d, 83.9% ee", P2, "CC(O)C#CCCl"),
      part(f"{rid}_vinyl_acetate", "reagent", "vinyl acetate", P2, "C=COC(C)=O"),
      part(f"{rid}_enzyme", "catalyst", "Novozym 435", P2),
      part(f"{rid}_product", "product", "recovered (S)-(-)-3d", P2, "CC(O)C#CCCl")]
records.append(rec(rid, "reported_experiment", P2, ps,
    [step("kinetic_resolution_enrichment", [x["entity_id"] for x in ps], P2, temperature=qty(60, "°C"))],
    [fld("recovered_starting_material_yield", qty(76, "%"), P2, [f"{rid}_product"]),
     fld("recovered_starting_material_ee", qty(99.9, "%"), P2, [f"{rid}_product"]), fld("yield_measurement_basis", None, P2)],
    unresolved=["Scale, duration, solvent, atmosphere, workup, purification, and yield basis are not stated."]))

rid = "scheme3_3e_kinetic_resolution"
ps = [part(f"{rid}_start", "reactant", "racemic 3e", P2, "CCC(O)C#CCCl"),
      part(f"{rid}_vinyl_acetate", "reagent", "vinyl acetate", P2, "C=COC(C)=O"),
      part(f"{rid}_enzyme", "catalyst", "Novozym 435", P2),
      part(f"{rid}_acetate", "product", "(R)-(+)-4e", P2, "CC(=O)OC(CC)C#CCCl"),
      part(f"{rid}_recovered", "product", "recovered (S)-(-)-3e", P2, "CCC(O)C#CCCl")]
records.append(rec(rid, "reported_experiment", P2, ps,
    [step("kinetic_resolution", [x["entity_id"] for x in ps], P2, temperature=qty(60, "°C"))],
    [fld("acetate_yield", qty(44, "%"), P2, [f"{rid}_acetate"]),
     fld("acetate_ee", qty(92.9, "%"), P2, [f"{rid}_acetate"]),
     fld("recovered_starting_material_yield", qty(46, "%"), P2, [f"{rid}_recovered"]),
     fld("recovered_starting_material_ee", qty(98.3, "%"), P2, [f"{rid}_recovered"]), fld("yield_measurement_basis", None, P2)],
    unresolved=["Scale, duration, solvent, atmosphere, workup, purification, and yield basis are not stated."]))

# Table 1 and the preceding catalyst-free trial.
rid = "prose_table1_catalyst_free_trace"
ps = [part(f"{rid}_5", "reactant", "4-chloro-2-butyn-1-ol 5", P2, "OCC#CCCl"),
      part(f"{rid}_grignard", "reagent", "n-C4H9MgBr", P2, "[Mg+](Br)CCCC"),
      part(f"{rid}_ether", "solvent", "Et2O", P2, "CCOCC"),
      part(f"{rid}_product", "product", "2-butyl-2,3-butadien-1-ol 6a", P2, "C=C=C(CCCC)CO")]
records.append(rec(rid, "optimization_entry", P2, ps,
    [step("catalyst_free_trial", [x["entity_id"] for x in ps], P2)],
    [fld("reported_yield", "trace", P2, [f"{rid}_product"]), fld("yield_measurement_basis", None, P2)],
    notes=["No catalyst was used."],
    unresolved=["Scale, reagent loading, temperature, duration, atmosphere, workup, purification, and yield basis are not stated."]))

table1 = [(1, "n-C4H9", "[Mg+](Br)CCCC", "6a", "C=C=C(CCCC)CO", 4.7, 79),
          (2, "n-C7H15", "[Mg+](Br)CCCCCCC", "6b", "C=C=C(CCCCCCC)CO", 3.0, 59),
          (3, "n-C10H21", "[Mg+](Br)CCCCCCCCCC", "6c", "C=C=C(CCCCCCCCCC)CO", 3.3, 63),
          (4, "Ph", "[Mg+](Br)c1ccccc1", "6d", "C=C=C(c1ccccc1)CO", 5.4, 46)]
for ent, rgroup, gr_sm, prod, prod_sm, hours, y in table1:
    rid = f"table1_entry{ent}"
    ps = [part(f"{rid}_5", "reactant", "4-chloro-2-butyn-1-ol 5", P2, "OCC#CCCl"),
          part(f"{rid}_grignard", "reagent", f"{rgroup}MgBr", P2, gr_sm,
               amounts=[fld("concentration", qty(1, "M"), P2)]),
          part(f"{rid}_cubr", "catalyst", "CuBr", P2, "[Cu]Br",
               amounts=[fld("catalyst_loading", qty(20, "mol%"), P2)]),
          part(f"{rid}_ether", "solvent", "Et2O", P2, "CCOCC"),
          part(f"{rid}_product", "product", prod, P2, prod_sm)]
    records.append(rec(rid, "substrate_scope_entry", P2, ps,
        [step("allene_formation", [x["entity_id"] for x in ps], P2,
              temperature=qty(-60, "°C"), time=qty(hours, "h"))],
        [fld("reported_yield", qty(y, "%"), P2, [f"{rid}_product"]), fld("yield_measurement_basis", None, P2)],
        unresolved=["Scale, Grignard equivalents, atmosphere, workup, purification, and yield basis are not stated.",
                    "Candidate product connectivity is unverified."]))

# Table 2; entry 7 is also Table 3 entry 1.
table2 = [
    (1, 4, None, None, 16, 0, None, 84, -60),
    (2, 4, "CuCl", 20, 16, 38, None, 8, -60),
    (3, 4, "CuBr", 20, 16, 54, None, 8, -60),
    (4, 4, "CuI", 20, 16, 24, None, 43, -60),
    (5, 4, "CuCN", 20, 16, 75, None, 2, -60),
    (6, 3, "CuCN", 10, 19, 74, None, 5, -60),
    (7, 3, "CuCN", 5, 12.5, 71, 63, 2, -60),
    (8, 3, "CuCN", 2, 19, 55, None, 26, -60),
    (9, 3, "CuCN", 5, 12, 61, None, 13, -50),
    (10, 3, "CuCN", 5, 3.5, 46, None, 6, -40),
    (11, 3, "CuCN", 5, 3.5, 21, None, 0, "r.t."),
]
for ent, equiv, catalyst, loading, hours, nmr_y, iso_y, recovery, temp in table2:
    rid = "table2_entry7_table3_entry1" if ent == 7 else f"table2_entry{ent}"
    ev = P2 + P3 if ent == 7 else P2
    ps = [part(f"{rid}_3a", "reactant", "racemic 3a", ev, "OC(c1ccccc1)C#CCCl"),
          part(f"{rid}_etmgbr", "reagent", "C2H5MgBr", ev, "[Mg+](Br)CC",
               amounts=[fld("equivalents", qty(equiv, "equiv"), ev), fld("concentration", qty(1, "M"), ev)]),
          part(f"{rid}_ether", "solvent", "Et2O", ev, "CCOCC"),
          part(f"{rid}_7a", "product", "racemic 7a", ev, "C=C=C(CC)C(O)c1ccccc1")]
    if catalyst:
        sm = {"CuCl": "[Cu]Cl", "CuBr": "[Cu]Br", "CuI": "[Cu]I", "CuCN": "N#[C][Cu]"}[catalyst]
        ps.append(part(f"{rid}_catalyst", "catalyst", catalyst, ev, sm,
                       amounts=[fld("catalyst_loading", qty(loading, "mol%"), ev)]))
    if ent == 11:
        ps.append(part(f"{rid}_side_product", "product", "2-ethyl-1-phenyl-2-hexen-1-ol", P2))
    outs = [fld("nmr_yield", qty(nmr_y, "%"), ev, [f"{rid}_7a"]),
            fld("recovered_starting_material_yield", qty(recovery, "%"), ev, [f"{rid}_3a"]),
            fld("yield_measurement_basis", "1H NMR using 1,3,5-trimethylbenzene as internal standard", P2)]
    if iso_y is not None:
        outs.append(fld("isolated_yield", qty(iso_y, "%"), ev, [f"{rid}_7a"]))
    if ent == 11:
        outs.append(fld("side_product_nmr_yield", qty(18, "%"), P2, [f"{rid}_side_product"]))
    records.append(rec(rid, "optimization_entry", ev, ps,
        [step("allene_formation", [x["entity_id"] for x in ps], ev,
              temperature=temp if isinstance(temp, str) else qty(temp, "°C"), time=qty(hours, "h"))],
        outs, notes=["Entry 1 uses no copper catalyst."] if ent == 1 else
                    (["The room-temperature reaction was not clean; the side product was attributed to carbometalation of 7a."] if ent == 11 else []),
        unresolved=["Scale, atmosphere, workup, and purification are not stated for the table row.",
                    "Product candidate connectivity and stereochemistry are unverified."]))

# Table 3 entries 2-16; entry 1 is already cross-linked above.
start_map = {
    "3a": ("racemic 3a", "OC(c1ccccc1)C#CCCl", "Ph", "C(O)c1ccccc1"),
    "3b": ("racemic 3b", "OC(c1ccc(C)cc1)C#CCCl", "p-CH3C6H4", "C(O)c1ccc(C)cc1"),
    "3c": ("racemic 3c", "CCCCCC(O)C#CCCl", "n-C5H11", "C(O)CCCCC"),
    "3d": ("racemic 3d", "CC(O)C#CCCl", "CH3", "C(O)C"),
    "3e": ("racemic 3e", "CCC(O)C#CCCl", "C2H5", "C(O)CC"),
}
r2_map = {
    "C2H5": ("[Mg+](Br)CC", "CC"), "i-C3H7": ("[Mg+](Br)C(C)C", "C(C)C"),
    "n-C4H9": ("[Mg+](Br)CCCC", "CCCC"), "n-C5H11": ("[Mg+](Br)CCCCC", "CCCCC"),
    "n-C7H15": ("[Mg+](Br)CCCCCCC", "CCCCCCC"),
}
table3 = [
    (2, "3a", "i-C3H7", 10, 92, "7b"), (3, "3a", "n-C4H9", 18, 61, "7c"),
    (4, "3a", "n-C5H11", 17, 76, "7d"), (5, "3b", "C2H5", 11, 53, "7e"),
    (6, "3b", "n-C4H9", 18, 63, "7f"), (7, "3b", "n-C5H11", 17, 71, "7g"),
    (8, "3b", "n-C7H15", 17, 79, "7h"), (9, "3c", "C2H5", 11, 61, "7i"),
    (10, "3c", "n-C4H9", 5, 69, "7j"), (11, "3c", "n-C5H11", 17, 67, "7k"),
    (12, "3c", "n-C7H15", 17, 63, "7l"), (13, "3d", "n-C4H9", 17, 70, "7m"),
    (14, "3d", "n-C7H15", 17, 98, "7n"), (15, "3e", "n-C4H9", 11, 71, "7o"),
    (16, "3e", "n-C5H11", 13, 74, "7p"),
]
for ent, substrate, r2, hours, y, product in table3:
    rid = f"table3_entry{ent}"
    s_label, s_sm, r1_label, product_r1 = start_map[substrate]
    gr_sm, product_r2 = r2_map[r2]
    equiv = 4 if ent in (8, 12, 14) else 3
    prod_sm = f"C=C=C({product_r2}){product_r1}"
    ps = [part(f"{rid}_start", "reactant", s_label, P3, s_sm),
          part(f"{rid}_grignard", "reagent", f"{r2}MgBr", P3, gr_sm,
               amounts=[fld("equivalents", qty(equiv, "equiv"), P3), fld("concentration", qty(1, "M"), P3)]),
          part(f"{rid}_cucn", "catalyst", "CuCN", P3, "N#[C][Cu]",
               amounts=[fld("catalyst_loading", qty(5, "mol%"), P3)]),
          part(f"{rid}_ether", "solvent", "Et2O", P3, "CCOCC"),
          part(f"{rid}_product", "product", f"racemic {product} (R1={r1_label}, R2={r2})", P3, prod_sm)]
    records.append(rec(rid, "substrate_scope_entry", P3, ps,
        [step("allene_formation", [x["entity_id"] for x in ps], P3,
              temperature=qty(-60, "°C"), time=qty(hours, "h"))],
        [fld("reported_yield", qty(y, "%"), P3, [f"{rid}_product"]), fld("yield_measurement_basis", None, P3)],
        unresolved=["Scale, atmosphere, workup, purification, and yield basis are not stated.",
                    "Candidate product connectivity and stereochemistry are unverified."]))

# Table 4, with the full typical procedure merged into entry 1.
table4 = [
    (1, "(R)-3a", "OC(c1ccccc1)C#CCCl", 97.7, "C2H5", 13, 67, "(R)-7a", "C=C=C(CC)C(O)c1ccccc1", 97.7),
    (2, "(R)-3a", "OC(c1ccccc1)C#CCCl", 97.7, "i-C3H7", 10, 89, "(R)-7b", "C=C=C(C(C)C)C(O)c1ccccc1", 97.2),
    (3, "(R)-3a", "OC(c1ccccc1)C#CCCl", 96.8, "n-C4H9", 13, 60, "(R)-7c", "C=C=C(CCCC)C(O)c1ccccc1", 96.2),
    (4, "(R)-3c", "CCCCCC(O)C#CCCl", 96.8, "n-C4H9", 5, 73, "(R)-7j", "C=C=C(CCCC)C(O)CCCCC", None),
    (5, "(S)-3d", "CC(O)C#CCCl", 99.9, "n-C4H9", 11, 69, "(S)-7m", "C=C=C(CCCC)C(O)C", 99.9),
    (6, "(R)-3d", "CC(O)C#CCCl", 98.9, "n-C4H9", 11, 69, "(R)-7m", "C=C=C(CCCC)C(O)C", 99.0),
    (7, "(S)-3d", "CC(O)C#CCCl", 99.9, "n-C7H15", 9, 79, "(S)-7n", "C=C=C(CCCCCCC)C(O)C", 99.9),
    (8, "(S)-3e", "CCC(O)C#CCCl", 98.3, "n-C4H9", 11, 70, "(S)-7o", "C=C=C(CCCC)C(O)CC", 98.1),
    (9, "(S)-3e", "CCC(O)C#CCCl", 98.3, "n-C5H11", 7, 79, "(S)-7p", "C=C=C(CCCCC)C(O)CC", 98.2),
]
for ent, substrate, s_sm, input_ee, r2, hours, y, product, p_sm, product_ee in table4:
    rid = f"table4_entry{ent}"
    ev = P3
    gr_sm = r2_map[r2][0]
    start_amounts = [fld("input_ee", qty(input_ee, "%"), ev)]
    gr_amounts = [fld("equivalents", qty(3, "equiv"), ev), fld("concentration", qty(1, "M"), ev)]
    cat_amounts = [fld("catalyst_loading", qty(5, "mol%"), ev)]
    ether_amounts = []
    if ent == 1:
        start_amounts += [fld("mass", qty(54.4, "mg"), ev), fld("amount", qty(0.30, "mmol"), ev)]
        gr_amounts += [fld("volume", qty(0.9, "mL"), ev), fld("amount", qty(0.9, "mmol"), ev)]
        cat_amounts += [fld("mass", qty(1.4, "mg"), ev), fld("amount", qty(0.016, "mmol"), ev)]
        ether_amounts = [fld("volume", qty(2.1, "mL"), ev)]
    if ent == 8:
        start_amounts += [fld("mass", qty(65.1, "mg"), ev), fld("amount", qty(0.50, "mmol"), ev)]
    ps = [part(f"{rid}_start", "reactant", substrate, ev, s_sm, start_amounts),
          part(f"{rid}_grignard", "reagent", f"{r2}MgBr", ev, gr_sm, gr_amounts),
          part(f"{rid}_cucn", "catalyst", "CuCN", ev, "N#[C][Cu]", cat_amounts),
          part(f"{rid}_ether", "solvent", "anhydrous Et2O" if ent == 1 else "Et2O", ev, "CCOCC", ether_amounts),
          part(f"{rid}_product", "product", product, ev, p_sm)]
    operation = None
    atmosphere = None
    workup = None
    purification = None
    if ent == 1:
        operation = "Dried Schlenk vessel; substrate, CuCN, and ether charged at room temperature; EtMgBr added dropwise at -60 °C over 5 min; stirred 13 h with TLC monitoring."
        atmosphere = "nitrogen"
        workup = "Quenched with saturated NH4Cl solution (1 mL); extracted with ether (10 mL x 3); washed with brine (10 mL); dried over anhydrous Na2SO4; evaporated."
        purification = "Silica-gel column chromatography; petroleum ether/ethyl acetate 10:1"
    outs = [fld("isolated_yield" if ent == 1 else "reported_yield", qty(y, "%"), ev, [f"{rid}_product"]),
            fld("product_ee", "unable to determine" if product_ee is None else qty(product_ee, "%"), ev, [f"{rid}_product"]),
            fld("yield_measurement_basis", "isolated after column chromatography" if ent == 1 else None, ev)]
    if ent == 1:
        outs += [fld("product_mass", qty(34.9, "mg"), ev, [f"{rid}_product"]),
                 fld("ee_measurement_basis", "HPLC, Chiralcel OD-H, n-hexane/i-PrOH 90:10, 0.8 mL/min, 230 nm; major 7.6 min, minor 7.0 min", ev, [f"{rid}_product"])]
    if ent == 8:
        outs.append(fld("product_mass", qty(53.3, "mg"), ev, [f"{rid}_product"]))
    records.append(rec(rid, "substrate_scope_entry", ev, ps,
        [step("allene_formation", [x["entity_id"] for x in ps], ev,
              temperature=qty(-60, "°C"), time=qty(hours, "h"), atmosphere=atmosphere,
              operation=operation, workup=workup, purification=purification)], outs,
        unresolved=(["Candidate connectivity and absolute stereochemistry are unverified."] if ent == 1 else
                    ["Scale, atmosphere, workup, purification, and yield basis are not stated for the table row.",
                     "Candidate connectivity and absolute stereochemistry are unverified."])))

# Scheme 4, distinct 10 mmol scale-up. The 0.5 mmol result is linked to Table 4 entry 8 above.
rid = "scheme4_scaleup_s_3e_to_s_7o"
ps = [part(f"{rid}_start", "reactant", "(S)-3e", P3, "CCC(O)C#CCCl",
           amounts=[fld("mass", qty(1.3244, "g"), P3), fld("amount", qty(10.0, "mmol"), P3), fld("input_ee", qty(98.3, "%"), P3)]),
      part(f"{rid}_grignard", "reagent", "n-C4H9MgBr", P3, "[Mg+](Br)CCCC",
           amounts=[fld("equivalents", qty(3.0, "equiv"), P3), fld("concentration", qty(1, "M"), P3)]),
      part(f"{rid}_cucn", "catalyst", "CuCN", P3, "N#[C][Cu]",
           amounts=[fld("catalyst_loading", qty(5, "mol%"), P3)]),
      part(f"{rid}_ether", "solvent", "Et2O", P3, "CCOCC"),
      part(f"{rid}_product", "product", "(S)-7o", P3, "C=C=C(CCCC)C(O)CC")]
records.append(rec(rid, "reported_experiment", P3, ps,
    [step("scale_up_allene_formation", [x["entity_id"] for x in ps], P3, temperature=qty(-60, "°C"))],
    [fld("reported_yield", qty(71, "%"), P3, [f"{rid}_product"]),
     fld("product_mass", qty(1.1002, "g"), P3, [f"{rid}_product"]),
     fld("product_ee", qty(98.1, "%"), P3, [f"{rid}_product"]), fld("yield_measurement_basis", None, P3)],
    unresolved=["Duration, atmosphere, workup, purification, and yield basis are not stated for the scale-up.",
                "Candidate connectivity and absolute stereochemistry are unverified."]))

# Coverage ledger with exact requested pages.
def ids(prefixes):
    return [r["record_id"] for r in records if any(r["source_reaction_id"].startswith(p) for p in prefixes)]

page1_ids = [f"{DOC}:graphical_abstract_general_route"]
page2_ids = [r["record_id"] for r in records if f"{DOC}:page2:image" in r["evidence_ids"]]
page3_ids = [r["record_id"] for r in records if f"{DOC}:page3:image" in r["evidence_ids"]]
coverage = {
    "document_id": DOC, "semantic_accuracy_verified": False,
    "pages": [
        {"page": 1, "state": "attempted", "regions": [
            {"region": "upper and middle-left graphical abstract plus abstract text",
             "finding": "Generic two-route preparation of optically active chloroalkynols followed by CuCN/Grignard conversion to allenols; retained as a general scheme, not a batch experiment.",
             "evidence_ids": P1},
            {"region": "right-column introduction and lower-right starting-material discussion",
             "finding": "Prior-literature routes and broad scope claims were not expanded into experiments; the present-paper racemic starting-material statement is resolved by Scheme 1 on page 2.",
             "evidence_ids": P1}],
         "record_ids": page1_ids,
         "unresolved": ["The graphical abstract contains generic R groups and scope ranges rather than batch-specific structures."]},
        {"page": 2, "state": "attempted", "regions": [
            {"region": "upper-left Schemes 1 and 2",
             "finding": "Five racemic 3a-e preparations and six optically active homologation/chlorination stages were extracted independently.",
             "evidence_ids": P2},
            {"region": "middle-left Scheme 3",
             "finding": "Three 3d resolution/deacetylation/enrichment operations and one 3e kinetic resolution were extracted; product and recovered-material outcomes remain separate.",
             "evidence_ids": P2},
            {"region": "upper-right Table 1 and adjacent prose",
             "finding": "Four CuBr/Grignard scope rows and the separate catalyst-free trace trial were extracted.",
             "evidence_ids": P2},
            {"region": "right-column Table 2 and discussion",
             "finding": "Eleven Cu(I) optimization rows were extracted; entry 7 is cross-linked to Table 3 entry 1, and entry 11 retains the 18% NMR carbometalation side product.",
             "evidence_ids": P2}],
         "record_ids": page2_ids,
         "unresolved": ["Most scheme/table entries omit scale, atmosphere, workup, purification, or yield basis.",
                        "The catalyst-free trace trial does not restate temperature, duration, or Grignard loading."]},
        {"page": 3, "state": "attempted", "regions": [
            {"region": "upper-left Table 3",
             "finding": "Sixteen racemic scope rows were represented; entry 1 is the same optimized batch as Table 2 entry 7 and was merged, while the remaining fifteen rows stay independent.",
             "evidence_ids": P3},
            {"region": "middle-left Table 4",
             "finding": "Nine enantioenriched scope rows were extracted with input/product ee; entry 4 preserves the source's inability to determine product ee.",
             "evidence_ids": P3},
            {"region": "upper-right Scheme 4 and adjacent prose",
             "finding": "The 0.5 mmol result was linked to Table 4 entry 8; the 10 mmol, 71% scale-up was retained as a distinct experiment.",
             "evidence_ids": P3},
            {"region": "right-column Experimental Section",
             "finding": "The full (R)-7a typical procedure was merged into Table 4 entry 1, including exact quantities, staged addition, workup, chromatography, mass, yield, and HPLC ee method.",
             "evidence_ids": P3},
            {"region": "conclusion, acknowledgments, SI notice, and references",
             "finding": "No additional independent experiment was created; the SI availability statement does not establish an associated SI file.",
             "evidence_ids": P3}],
         "record_ids": page3_ids,
         "unresolved": ["Most Table 3/4 rows omit scale, atmosphere, workup, purification, and yield basis.",
                        "Candidate product connectivity and all absolute stereochemical assignments remain unverified.",
                        "The scale-up does not state reaction duration or operational workup."]},
    ]
}

# Mark page tasks attempted without changing any non-requested task.
tasks_path = ROOT / "tasks.json"
tasks = json.loads(tasks_path.read_text())
for task in tasks:
    if task["document_id"] == DOC and task["task_id"] in {f"{DOC}:page{i}:text" for i in (1, 2, 3)}:
        task["state"] = "attempted"

out_records = ROOT / "raw_model" / "records_pages_0001_0003.json"
out_coverage = ROOT / "coverage" / "pages_0001_0003.json"
out_records.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
out_coverage.parent.mkdir(parents=True, exist_ok=True)
out_coverage.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"records": len(records), "coverage_pages": [p["page"] for p in coverage["pages"]]}, ensure_ascii=False))
