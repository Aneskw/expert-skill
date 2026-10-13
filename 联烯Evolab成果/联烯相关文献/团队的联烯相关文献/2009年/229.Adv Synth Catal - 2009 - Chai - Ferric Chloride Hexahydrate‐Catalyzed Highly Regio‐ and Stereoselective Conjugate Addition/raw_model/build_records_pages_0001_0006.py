#!/usr/bin/env python3
"""Build source-faithful machine records for doc_35087b7314dcb02b, PDF pages 1-6."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / "runs/current"
DOC = "doc_35087b7314dcb02b"


def ev(page: int):
    return [f"{DOC}:page{page}:image", f"{DOC}:page{page}:text"]


def fact(value, evidence):
    return {
        "value": value,
        "evidence_ids": list(evidence) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


SMILES = {
    "triethylamine": "CCN(CC)CC",
    "dichloromethane": "ClCCl",
    "sodium hydroxide": "[Na+].[OH-]",
    "ethanol": "CCO",
    "water": "O",
    "potassium carbonate": "[K+].[K+].[O-]C([O-])=O",
    "DMF": "CN(C)C=O",
    "methyl iodide": "CI",
    "benzyl bromide": "BrCc1ccccc1",
    "allyl bromide": "C=CCBr",
    "toluene": "Cc1ccccc1",
    "THF": "C1CCOC1",
    "ammonium chloride": "[Cl-].[NH4+]",
    "D2O": "[2H]O[2H]",
    "acetyl chloride": "CC(=O)Cl",
    "allyl acetate": "C=CCOC(C)=O",
    "3a": "CCOC(=O)C(CCC)=C=Cc1ccccc1",
    "3e": "CCOC(=O)C(C)=C=Cc1ccccc1",
    "Z-5a": "CCOC(=O)C(CCC)C(C)=Cc1ccccc1",
    "Z-5e": "CCOC(=O)C(C)C(C)=Cc1ccccc1",
    "6a": "CCOC(=O)C(CCC)=C(C)Cc1ccccc1",
}


def field(name, value, evidence, targets=None):
    item = {"name": name, "fact": fact(value, evidence)}
    if targets:
        item["target_entity_ids"] = list(targets)
    return item


def part(entity_id, role, label, evidence, amounts=(), name=None, smiles=None):
    s = SMILES.get(label) if smiles is None else smiles
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence) if name else fact(None, []),
        "smiles": fact(s, evidence) if s else fact(None, []),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": [field(n, v, evidence) for n, v in amounts],
    }


def rec(rid, kind, page, participants, conditions, outcomes, notes=(), unresolved=(), extra_pages=()):
    evidence = []
    for p in (page, *extra_pages):
        for e in ev(p):
            if e not in evidence:
                evidence.append(e)
    pids = [p["entity_id"] for p in participants]
    return {
        "record_id": f"{DOC}:{rid}",
        "document_id": DOC,
        "source_reaction_id": rid,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": evidence,
        "participants": participants,
        "steps": [{"step_id": "step1", "participant_ids": pids, "conditions": [field(n, v, evidence) for n, v in conditions]}],
        "outcomes": [field(n, v, evidence, t) for n, v, t in outcomes],
        "notes": [fact(x, evidence) for x in notes],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": list(unresolved),
        },
    }


records = []

# Page 2, Scheme 1: each displayed product/yield is a separate preparation.
scheme1 = [
    ("3a", "R1=Ph; R2=H; R3=n-Pr; CO2Et", 65, "ylide branch"),
    ("3g", "R1=4-BrC6H4; R2=H; R3=n-Pr; CO2Et", 60, "ylide branch"),
    ("3i", "R1=n-C7H15; R2=H; R3=n-Pr; CO2Et", 61, "ylide branch"),
    ("3e", "R1=Ph; R2=H; R3=Me; CO2Et", 67, "variable-ylide branch"),
    ("3f", "R1=4-BrC6H4; R2=H; R3=Me; CO2Et", 47, "variable-ylide branch"),
    ("3h", "R1=4-MeOC6H4; R2=H; R3=Me; CO2Et", 31, "variable-ylide branch"),
    ("3j", "R1=n-C4H9; R2=H; R3=Bn; CO2Et", 75, "variable-ylide branch"),
    ("3k", "R1=n-C4H9; R2=H; R3=Me; CO2Et", 56, "variable-ylide branch"),
    ("3l", "R1=n-C4H9; R2=H; R3=H; CO2Et", 46, "variable-ylide branch"),
    ("3m", "R1=4-ClC6H4; R2=H; R3=Me; CO2Et", 30, "variable-ylide branch"),
    ("3n", "R1=n-C7H15; R2=H; R3=Me; CO2Et", 54, "variable-ylide branch"),
    ("3o", "R1=4-FC6H4; R2=H; R3=Me; CO2Et", 61, "variable-ylide branch"),
]
for label, desc, y, branch in scheme1:
    e = ev(2)
    participants = [
        part("ylide_1", "reactant", "Wittig reagent 1", e),
        part("acyl_chloride_2", "reactant", "acyl chloride 2", e),
        part("et3n", "reagent", "triethylamine", e),
        part("ch2cl2", "solvent", "dichloromethane", e),
        part("product", "product", label, e),
    ]
    records.append(rec(
        f"scheme1_{label}", "substrate_scope_entry", 2, participants,
        [("operation", "Et3N/CH2Cl2; 0 °C to room temperature"), ("reaction_time", None), ("atmosphere", None), ("workup", None), ("purification", None)],
        [("reported_yield", {"number": y, "unit": "%"}, ["product"]), ("yield_measurement_basis", None, ["product"])],
        notes=[f"Scheme 1 {branch}; product substituents: {desc}."],
        unresolved=["Reaction scale, duration, atmosphere, workup, purification, and yield basis are not stated.", "Product connectivity is machine-interpreted from the drawing; stereochemistry is not encoded."],
    ))

# Page 2, Scheme 2: hydrolysis and esterification are successive, independently reported operations.
for acid, start, r3 in [("4a", "3a", "n-C3H7"), ("4b", "3e", "Me")]:
    e = ev(2)
    ps = [part("start", "reactant", start, e), part("naoh", "reagent", "sodium hydroxide", e),
          part("etoh", "solvent", "ethanol", e), part("water", "solvent", "water", e), part("product", "product", acid, e)]
    records.append(rec(
        f"scheme2_hydrolysis_{acid}", "reported_experiment", 2, ps,
        [("temperature", "reflux"), ("reaction_time", None), ("atmosphere", None), ("workup", None), ("purification", None)],
        [("reported_yield", {"number": 64, "unit": "%"}, ["product"]), ("yield_measurement_basis", None, ["product"])],
        notes=[f"Allenoic acid {acid}; R3={r3}."],
        unresolved=["Scale, reagent quantities, duration, atmosphere, workup, purification, and yield basis are not stated."],
    ))

ester_rows = [
    ("3b", "4a", "methyl iodide", "R3=n-C3H7; R4=Me; X=I", 92),
    ("3c", "4a", "benzyl bromide", "R3=n-C3H7; R4=Bn; X=Br", 93),
    ("3d", "4b", "allyl bromide", "R3=Me; R4=allyl; X=Br", 75),
]
for product, acid, alkyl_halide, desc, y in ester_rows:
    e = ev(2)
    ps = [part("acid", "reactant", acid, e), part("alkyl_halide", "reagent", alkyl_halide, e),
          part("k2co3", "reagent", "potassium carbonate", e), part("dmf", "solvent", "DMF", e), part("product", "product", product, e)]
    records.append(rec(
        f"scheme2_esterification_{product}", "reported_experiment", 2, ps,
        [("reaction_time", None), ("temperature", None), ("atmosphere", None), ("workup", None), ("purification", None)],
        [("reported_yield", {"number": y, "unit": "%"}, ["product"]), ("yield_measurement_basis", None, ["product"])],
        notes=[f"Scheme 2 esterification: {desc}."],
        unresolved=["Scale, reagent quantities, temperature, duration, atmosphere, workup, purification, and yield basis are not stated."],
    ))

# Page 3, Table 1: catalyst optimization; all five rows are independent.
table1 = [
    (1, "FeCl3·6H2O", 5, 93, None, 0.7),
    (2, "FeCl3·6H2O", 2, 98, None, 0.7),
    (3, "FeCl3·6H2O", 0.5, 46, 46, 1.2),
    (4, None, None, 13, 84, 0.9),
    (5, "Fe(acac)3", 5, 81, None, 0.8),
]
for idx, catalyst, loading, yield5, recovery, yield6 in table1:
    e = ev(3)
    ps = [
        part("allenoate", "reactant", "3a", e, [("amount", {"number": 0.4, "unit": "mmol"})]),
        part("grignard", "reagent", "methylmagnesium chloride", e, [("equivalents", {"number": 3, "unit": "equiv"}), ("concentration", {"number": 3, "unit": "M"})]),
        part("thf", "solvent", "THF", e), part("toluene", "solvent", "toluene", e, [("volume", {"number": 5, "unit": "mL"})]),
        part("quench", "reagent", "ammonium chloride", e),
        part("main_product", "product", "Z-5a", e), part("byproduct", "product", "6a", e),
    ]
    if catalyst:
        ps.insert(2, part("catalyst", "catalyst", catalyst, e, [("catalyst_loading", {"number": loading, "unit": "mol%"})]))
    outs = [("NMR_yield_Z_5a", {"number": yield5, "unit": "%"}, ["main_product"]),
            ("NMR_yield_6a", {"number": yield6, "unit": "%"}, ["byproduct"]),
            ("yield_measurement_basis", "1H NMR using 1,3,5-trimethylbenzene as internal standard", ["main_product", "byproduct"])]
    if recovery is not None:
        outs.append(("recovered_starting_material_yield", {"number": recovery, "unit": "%"}, ["allenoate"]))
    records.append(rec(
        f"table1_entry{idx}", "optimization_entry", 3, ps,
        [("temperature", {"number": -78, "unit": "°C"}), ("reaction_time", {"number": 2.5, "unit": "h"}),
         ("operation", "quench with saturated aqueous NH4Cl at -78 °C, then warm to room temperature"),
         ("atmosphere", None), ("workup", None), ("purification", None)], outs,
        notes=["No E isomer of the conjugate-addition product was observed in the catalyst study."],
        unresolved=["Atmosphere, full workup, and purification are not stated for the optimization rows."],
    ))

# Page 3, equation 1: deuterium trapping of the in-situ dienolate.
e = ev(3)
ps = [part("allenoate", "reactant", "3e", e), part("grignard", "reagent", "methylmagnesium chloride", e, [("equivalents", {"number": 3, "unit": "equiv"})]),
      part("thf", "solvent", "THF", e), part("catalyst", "catalyst", "FeCl3·6H2O", e, [("catalyst_loading", {"number": 5, "unit": "mol%"})]),
      part("toluene", "solvent", "toluene", e), part("d2o", "reagent", "D2O", e), part("product", "product", "8", e)]
records.append(rec(
    "equation1_d2o_trapping", "reported_experiment", 3, ps,
    [("temperature", {"number": -78, "unit": "°C"}), ("reaction_time", {"number": 1, "unit": "h"}), ("operation", "D2O at -78 °C, then warm to room temperature"),
     ("atmosphere", None), ("workup", None), ("purification", None)],
    [("reported_yield", {"number": 70, "unit": "%"}, ["product"]), ("deuterium_incorporation", {"number": 96, "unit": "%"}, ["product"]), ("yield_measurement_basis", None, ["product"])],
    notes=["The authors use this result as evidence for magnesium 1,3(Z)-dienolate Z-7a."],
    unresolved=["Scale, solvent volume, atmosphere, workup, purification, and measurement bases are not stated."],
))

# Page 4, Table 2: alkyl Grignard scope.
table2 = [
    (1, "Ph", "n-Pr", "Et", "3a", "Me", "chloride", 2.5, 88, "Z-5a", 2),
    (2, "Ph", "n-Pr", "Me", "3b", "Me", "chloride", 2.4, 89, "Z-5b", 2),
    (3, "Ph", "n-Pr", "Bn", "3c", "Me", "chloride", 3.5, 78, "Z-5c", 2),
    (4, "Ph", "Me", "allyl", "3d", "Me", "chloride", 3, 72, "Z-5d", 2),
    (5, "Ph", "Me", "Et", "3e", "Me", "chloride", 3.5, 62, "Z-5e", 2),
    (6, "p-BrC6H4", "Me", "Et", "3f", "Me", "chloride", 3, 87, "Z-5f", 2),
    (7, "p-BrC6H4", "n-Pr", "Et", "3g", "Me", "chloride", 2.4, 99, "Z-5g", 5),
    (8, "p-MeOC6H4", "Me", "Et", "3h", "Me", "chloride", 1, 67, "Z-5h", 2),
    (9, "n-C7H15", "n-Pr", "Et", "3i", "Me", "chloride", 3, 85, "Z-5i", 5),
    (10, "n-C4H9", "Bn", "Et", "3j", "Me", "chloride", 3, 89, "Z-5j", 5),
    (11, "n-C4H9", "Me", "Et", "3k", "Me", "chloride", 2, 76, "Z-5k", 2),
    (12, "n-C4H9", "H", "Et", "3l", "n-C5H11", "bromide", 3.5, 61, "Z-5l", 2),
    (13, "Ph", "Me", "Et", "3e", "c-Hex", "chloride", 2, 79, "Z-5m", 2),
    (14, "n-C7H15", "n-Pr", "Et", "3i", "s-Bu", "bromide", 1.5, 85, "Z-5n", 2),
    (15, "Ph", "Me", "Et", "3e", "t-Bu", "chloride", 1.5, 81, "E-5o", 2),
]
for idx, r1, r2, r3, substrate, r4, halide, time, y, product, catload in table2:
    extra = (6,) if idx == 1 else ()
    evidence = ev(4) + (ev(6) if idx == 1 else [])
    amounts_sub = [("amount", {"number": 0.4, "unit": "mmol"})]
    if idx == 1:
        amounts_sub += [("mass", {"number": 91.7, "unit": "mg"})]
    grignard_amounts = [("equivalents", {"number": 3, "unit": "equiv"})]
    if idx == 1:
        grignard_amounts += [("concentration", {"number": 3, "unit": "M"}), ("volume", {"number": 0.4, "unit": "mL"})]
    ps = [part("allenoate", "reactant", substrate, evidence, amounts_sub),
          part("grignard", "reagent", f"{r4}magnesium {halide}", evidence, grignard_amounts),
          part("thf", "solvent", "THF", evidence),
          part("catalyst", "catalyst", "FeCl3·6H2O", evidence, [("catalyst_loading", {"number": catload, "unit": "mol%"})]),
          part("toluene", "solvent", "toluene", evidence, [("volume", {"number": 5, "unit": "mL"})]),
          part("quench", "reagent", "ammonium chloride", evidence), part("product", "product", product, evidence)]
    if idx == 1:
        ps[3]["amounts"] += [field("mass", {"number": 2.2, "unit": "mg"}, evidence), field("amount", {"number": 0.008, "unit": "mmol"}, evidence)]
    records.append(rec(
        f"table2_entry{idx}", "substrate_scope_entry", 4, ps,
        [("temperature", {"number": -78, "unit": "°C"}), ("reaction_time", {"number": time, "unit": "h"}),
         ("operation", "quench with saturated aqueous NH4Cl at -78 °C, then warm to room temperature"),
         ("atmosphere", "nitrogen" if idx == 1 else None), ("workup", None), ("purification", None)],
        [("isolated_yield", {"number": y, "unit": "%"}, ["product"]), ("yield_measurement_basis", "isolated yield", ["product"])],
        notes=[f"Table 2 substituents: R1={r1}; R2={r2}; R3={r3}; R4={r4}."] + (["Page 6 begins the detailed typical procedure; only the visible initial setup and quantities are imported in this page range."] if idx == 1 else []),
        unresolved=["Product connectivity and alkene geometry are machine-interpreted and remain unverified.", "Full workup and purification are not stated in the covered range." if idx == 1 else "Atmosphere, workup, and purification are not stated."],
        extra_pages=extra,
    ))

# Page 4, Table 3: vinyl/aryl/thienyl Grignard scope.
table3 = [
    (1, "Ph", "n-Pr", "3a", "vinyl", "chloride", 1.5, 84, "Z-5p", 5, -78),
    (2, "p-ClC6H4", "Me", "3m", "vinyl", "bromide", 3, 85, "Z-5q", 2, -78),
    (3, "n-C4H9", "Me", "3k", "vinyl", "chloride", 3, 75, "Z-5r", 2, -78),
    (4, "p-MeOC6H4", "Me", "3h", "Ph", "chloride", 3, 81, "E-5s", 2, -78),
    (5, "n-C4H9", "H", "3l", "Ph", "chloride", 2.5, 64, "E-5t", 2, -78),
    (6, "n-C7H15", "H", "3n", "Ph", "chloride", 3, 60, "E-5u", 2, -78),
    (7, "n-C4H9", "Me", "3k", "Ph", "chloride", 3, 70, "E-5v", 2, -78),
    (8, "Ph", "Me", "3e", "2-thienyl", "bromide", 11, 63, "E-5w", 2, "room temperature"),
]
for idx, r1, r2, substrate, r4, halide, time, y, product, catload, temp in table3:
    e = ev(4)
    ps = [part("allenoate", "reactant", substrate, e, [("amount", {"number": 0.4, "unit": "mmol"})]),
          part("grignard", "reagent", f"{r4}magnesium {halide}", e, [("equivalents", {"number": 3, "unit": "equiv"})]),
          part("thf", "solvent", "THF", e), part("catalyst", "catalyst", "FeCl3·6H2O", e, [("catalyst_loading", {"number": catload, "unit": "mol%"})]),
          part("toluene", "solvent", "toluene", e, [("volume", {"number": 5, "unit": "mL"})]), part("quench", "reagent", "ammonium chloride", e),
          part("product", "product", product, e)]
    tempv = {"number": temp, "unit": "°C"} if isinstance(temp, (int, float)) else temp
    notes = [f"Table 3 substituents: R1={r1}; R2={r2}; R4={r4}."]
    if idx <= 3:
        notes.append("Freshly prepared vinyl Grignard reagent was required.")
    if idx == 8:
        notes.append("The reaction was run at room temperature because no reaction occurred at -78 °C.")
    records.append(rec(
        f"table3_entry{idx}", "substrate_scope_entry", 4, ps,
        [("temperature", tempv), ("reaction_time", {"number": time, "unit": "h"}), ("operation", "quench with saturated aqueous NH4Cl at -78 °C, then warm to room temperature"),
         ("atmosphere", None), ("workup", None), ("purification", None)],
        [("isolated_yield", {"number": y, "unit": "%"}, ["product"]), ("yield_measurement_basis", "isolated yield", ["product"])],
        notes=notes,
        unresolved=["Atmosphere, workup, and purification are not stated.", "Product connectivity and alkene geometry remain unverified."],
    ))

# Page 5, Table 4: A and B are distinct experiments for every entry.
table4 = [
    (1, "Ph", "3e", "FeCl3·6H2O", 65, ">99/1", 50, "93/7", "9a"),
    (2, "Ph", "3e", "Fe(acac)3", 68, ">99/1", 50, "95/5", "9a"),
    (3, "p-BrC6H4", "3f", "FeCl3·6H2O", 70, ">99/1", 45, "95/5", "9b"),
    (4, "p-BrC6H4", "3f", "Fe(acac)3", 87, ">99/1", 62, "97/3", "9b"),
    (5, "p-ClC6H4", "3m", "FeCl3·6H2O", 82, ">99/1", 55, "96/4", "9c"),
    (6, "p-ClC6H4", "3m", "Fe(acac)3", 84, ">99/1", 50, "98/2", "9c"),
    (7, "p-FC6H4", "3o", "FeCl3·6H2O", 77, ">99/1", 50, "94/6", "9d"),
    (8, "p-FC6H4", "3o", "Fe(acac)3", 76, ">99/1", 69, "98/2", "9d"),
]
for idx, r1, substrate, iron, ya, ratioa, yb, ratiob, baseprod in table4:
    for branch in ("A", "B"):
        e = ev(5)
        product = ("Z-" if branch == "A" else "E-") + baseprod
        electrophile = "acetyl chloride" if branch == "A" else "allyl acetate"
        ps = [part("allenoate", "reactant", substrate, e), part("grignard", "reagent", "methylmagnesium chloride", e, [("equivalents", {"number": 3, "unit": "equiv"})]),
              part("thf", "solvent", "THF", e), part("iron_catalyst", "catalyst", iron, e, [("catalyst_loading", {"number": 5, "unit": "mol%"})]),
              part("toluene", "solvent", "toluene", e), part("electrophile", "reagent", electrophile, e, [("amount", {"number": 2, "unit": "mmol"})]),
              part("product", "product", product, e)]
        y, ratio = (ya, ratioa) if branch == "A" else (yb, ratiob)
        conditions = [("temperature", {"number": -78, "unit": "°C"}), ("first_stage_time", {"number": 3, "unit": "h"}),
                      ("second_stage_time", {"minimum": 1, "maximum": 1.5, "unit": "h", "raw_text": "1-1.5 h"}) if branch == "A" else ("operation", "allyl acetate added at -78 °C, then warmed naturally to room temperature overnight"),
                      ("atmosphere", None), ("workup", None), ("purification", None)]
        outcomes = [("isolated_yield", {"number": y, "unit": "%"}, ["product"]),
                    (("Z_E_ratio" if branch == "A" else "E_Z_ratio"), ratio, ["product"]),
                    ("yield_measurement_basis", "isolated yield", ["product"]),
                    ("ratio_measurement_basis", "1H NMR analysis of crude products", ["product"])]
        notes = [f"Table 4 entry {idx}, Conditions {branch}; R1={r1}."]
        if branch == "B":
            notes.append("Across Conditions B, 6-31% hydrolysis product was observed by 1H NMR of the crude mixture; the source does not assign a row-specific value.")
        records.append(rec(
            f"table4_entry{idx}_conditions_{branch.lower()}", "substrate_scope_entry", 5, ps, conditions, outcomes,
            notes=notes,
            unresolved=["Reaction atmosphere, scale of allenoate before the stated 0.4 mmol dienolate amount, workup, and purification are not stated.", "The shared hydrolysis-product range cannot be assigned to an individual Conditions B row." if branch == "B" else "Product structure and Z geometry remain unverified."],
        ))

# Page 5, Scheme 3: proposed, not an observed batch.
e = ev(5)
ps = [part("z7", "reactant", "Z-7", e), part("anti", "unspecified_agent", "anti-allylic MgCl intermediate", e),
      part("syn", "unspecified_agent", "syn-allylic metallic intermediate", e), part("e7", "unspecified_agent", "E-7", e), part("products", "product", "E-9/E-10", e)]
records.append(rec(
    "scheme3_proposed_isomerization", "mechanism", 5, ps,
    [("operation", "proposed Z/E dienolate isomerization via anti- and syn-allylic metallic intermediates"), ("reaction_time", None), ("temperature", None)],
    [("reported_yield", None, ["products"])],
    notes=["M is MgCl or Cu and the ligand/metal identity is generic in the proposed scheme."],
    unresolved=["This is a proposed mechanism, not an isolated sequence; intermediate structures and speciation are unverified."],
))

# Page 6, Table 5: C and D are distinct experiments for every entry.
table5 = [
    (1, "Ph", "3e", "FeCl3·6H2O", 76, "98/2", 52, "96/4", "10a"),
    (2, "Ph", "3e", "Fe(acac)3", 67, "96/4", 51, "96/4", "10a"),
    (3, "p-BrC6H4", "3f", "FeCl3·6H2O", 70, "97/3", 71, ">99/1", "10b"),
    (4, "p-BrC6H4", "3f", "Fe(acac)3", 80, "93/7", 65, "97/3", "10b"),
    (5, "p-ClC6H4", "3m", "FeCl3·6H2O", 72, "97/3", 63, "97/3", "10c"),
    (6, "p-ClC6H4", "3m", "Fe(acac)3", 66, "96/4", 71, "97/3", "10c"),
    (7, "p-FC6H4", "3o", "FeCl3·6H2O", 69, "96/4", 69, "98/2", "10d"),
    (8, "p-FC6H4", "3o", "Fe(acac)3", 74, "94/6", 72, "97/3", "10d"),
]
for idx, r1, substrate, iron, yc, ratioc, yd, ratiod, baseprod in table5:
    for branch in ("C", "D"):
        e = ev(6)
        product = ("Z-" if branch == "C" else "E-") + baseprod
        allyl = "allyl acetate" if branch == "C" else "allyl bromide"
        transition = "Pd(PPh3)4" if branch == "C" else "CuI"
        transload = 5 if branch == "C" else 10
        ps = [part("allenoate", "reactant", substrate, e), part("grignard", "reagent", "methylmagnesium chloride", e, [("equivalents", {"number": 3, "unit": "equiv"})]),
              part("thf", "solvent", "THF", e), part("iron_catalyst", "catalyst", iron, e, [("catalyst_loading", {"number": 5, "unit": "mol%"})]),
              part("toluene", "solvent", "toluene", e), part("allyl_reagent", "reagent", allyl, e, [("amount", {"number": 2, "unit": "mmol"})]),
              part("transition_catalyst", "catalyst", transition, e, [("catalyst_loading", {"number": transload, "unit": "mol%"})]), part("product", "product", product, e)]
        y, ratio = (yc, ratioc) if branch == "C" else (yd, ratiod)
        operation = "allyl acetate and Pd(PPh3)4 at -78 °C, then warm naturally to room temperature overnight" if branch == "C" else "CuI and allyl bromide at room temperature; overnight"
        records.append(rec(
            f"table5_entry{idx}_conditions_{branch.lower()}", "substrate_scope_entry", 6, ps,
            [("first_stage_temperature", {"number": -78, "unit": "°C"}), ("first_stage_time", {"number": 3, "unit": "h"}), ("operation", operation),
             ("atmosphere", None), ("workup", None), ("purification", None)],
            [("isolated_yield", {"number": y, "unit": "%"}, ["product"]), (("Z_E_ratio" if branch == "C" else "E_Z_ratio"), ratio, ["product"]),
             ("yield_measurement_basis", "isolated yield", ["product"]), ("ratio_measurement_basis", "1H NMR analysis of crude products", ["product"])],
            notes=[f"Table 5 entry {idx}, Conditions {branch}; R1={r1}.", "Across Table 5, 1-13% hydrolysis product was observed by 1H NMR of the crude mixture; the source does not assign a row-specific value."],
            unresolved=["Reaction scale before the stated 0.4 mmol dienolate amount, atmosphere, workup, and purification are not stated.", "The shared hydrolysis-product range cannot be assigned to an individual row.", "Product connectivity and alkene geometry remain unverified."],
        ))

assert len(records) == 79, len(records)

raw_path = RUN / "raw_model/records_pages_0001_0006.json"
raw_path.parent.mkdir(parents=True, exist_ok=True)
raw_path.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")

# Required page coverage ledger.
ids = lambda prefix: [r["record_id"] for r in records if r["source_reaction_id"].startswith(prefix)]
page2_ids = ids("scheme1_") + ids("scheme2_")
page3_ids = ids("table1_") + ids("equation1_")
page4_ids = ids("table2_") + ids("table3_")
page5_ids = ids("table4_") + ids("scheme3_")
page6_ids = ids("table5_") + [f"{DOC}:table2_entry1"]
coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {"page": 1, "state": "attempted", "regions": [
            {"region": "title, abstract, and two-column introduction", "finding": "No batch-specific present-paper experiment is reported on this page. Abstract scope claims and cited prior reactions were not duplicated as records; the page only announces online supporting information, which was not supplied or associated.", "evidence_ids": ev(1)}
        ], "record_ids": [], "unresolved": ["Supporting information is advertised but no SI file was supplied or explicitly associated."]},
        {"page": 2, "state": "attempted", "regions": [
            {"region": "lower Scheme 1", "finding": "Twelve product-specific Wittig/acyl-chloride preparations were extracted separately from the two displayed reaction branches.", "evidence_ids": ev(2)},
            {"region": "upper-right Scheme 2", "finding": "Two ester hydrolyses and three subsequent alkylation/esterification operations were separated by chemical stage.", "evidence_ids": ev(2)},
            {"region": "Results and Discussion prose", "finding": "Narrative catalyst-screen outcomes were reconciled with page-3 Table 1 rather than duplicated.", "evidence_ids": ev(2)}
        ], "record_ids": page2_ids, "unresolved": ["Schemes 1-2 omit most scales, durations, atmospheres, workups, purifications, and yield bases."]},
        {"page": 3, "state": "attempted", "regions": [
            {"region": "upper-left Table 1 and Figure 1", "finding": "Five independent catalyst-loading/control rows were extracted with NMR yields, recovery, byproduct yield, and footnote conditions; Figure 1 is stereochemical assignment evidence, not another experiment.", "evidence_ids": ev(3)},
            {"region": "upper-right equation (1)", "finding": "The D2O trapping experiment was extracted separately with 70% yield and 96% D incorporation.", "evidence_ids": ev(3)},
            {"region": "lower prose", "finding": "Table 2/Table 3 scope and Table 4/Table 5 trapping discussions were used as context; the row-level records cite the pages carrying the actual tables.", "evidence_ids": ev(3)}
        ], "record_ids": page3_ids, "unresolved": ["Table 1 does not provide a full workup or purification; equation (1) omits scale and measurement bases."]},
        {"page": 4, "state": "attempted", "regions": [
            {"region": "Table 2 and footnotes", "finding": "All 15 alkyl-Grignard scope rows were extracted independently, including the 5 mol% catalyst overrides and the two alkylmagnesium-bromide rows.", "evidence_ids": ev(4)},
            {"region": "Table 3 and footnotes", "finding": "All eight vinyl/aryl/2-thienyl Grignard rows were extracted independently, including fresh-vinyl-Grignard, bromide, 5 mol%, and room-temperature overrides.", "evidence_ids": ev(4)},
            {"region": "bottom continuation prose", "finding": "Narrative allylation selectivity continues into the page-6 Table 5 records and was not counted separately.", "evidence_ids": ev(4)}
        ], "record_ids": page4_ids, "unresolved": ["Tables 2-3 omit atmosphere, workup, purification, and structure-verification details."]},
        {"page": 5, "state": "attempted", "regions": [
            {"region": "Table 4, reaction drawing, and footnotes", "finding": "Each of eight rows was split into separate Conditions A and Conditions B experiments, for 16 records total; electrophile quantities, catalyst substitutions, yields, ratios, and shared hydrolysis-product range were preserved.", "evidence_ids": ev(5)},
            {"region": "Scheme 3 and adjacent prose", "finding": "The Z/E dienolate-isomerization pathway was classified as a proposed mechanism, not an experimental batch.", "evidence_ids": ev(5)}
        ], "record_ids": page5_ids, "unresolved": ["The 6-31% hydrolysis-product range is not assigned to individual Conditions B rows; atmosphere, workup, and purification are absent."]},
        {"page": 6, "state": "attempted", "regions": [
            {"region": "Table 5, reaction drawing, and footnotes", "finding": "Each of eight rows was split into separate Conditions C and Conditions D experiments, for 16 records total; transition-metal loadings, allyl reagents, yields, ratios, and shared hydrolysis-product range were retained.", "evidence_ids": ev(6)},
            {"region": "lower-right opening Experimental Section", "finding": "The visible initial setup for the typical Z-5a preparation was merged into Table 2 entry 1 with exact FeCl3·6H2O, 3a, toluene, CH3MgCl, and nitrogen details. The continuation on page 7 was not imported or claimed.", "evidence_ids": ev(6)}
        ], "record_ids": page6_ids, "unresolved": ["The typical Z-5a procedure continues on page 7, outside this session's claimed range; full workup, purification, product mass, and characterization were not imported.", "The 1-13% hydrolysis-product range is not mapped to individual Table 5 rows."]},
    ],
}
cov_path = RUN / "coverage/pages_0001_0006.json"
cov_path.parent.mkdir(parents=True, exist_ok=True)
cov_path.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

# Mark only this session's six page tasks attempted.
tasks_path = RUN / "tasks.json"
tasks = json.loads(tasks_path.read_text())
for task in tasks:
    if task["document_id"] == DOC and task["task_id"] in {f"{DOC}:page{i}:text" for i in range(1, 7)}:
        task["state"] = "attempted"
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"records": len(records), "raw": str(raw_path), "coverage": str(cov_path)}, ensure_ascii=False))
