#!/usr/bin/env python3
"""Build source-faithful machine records for Zhao et al., PDF pages 1--6."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "runs/current/raw_model/records_pages_0001_0006.json"
COVERAGE = ROOT / "runs/current/coverage/pages_0001_0006.json"
TASKS = ROOT / "runs/current/tasks.json"
DOC = "doc_3e906dbef45cd67b"


def ev(*pages: int) -> list[str]:
    result = []
    for page in pages:
        result.extend([f"{DOC}:page{page}:image", f"{DOC}:page{page}:text"])
    return result


def fact(value, evidence=()):
    return {
        "value": value,
        "evidence_ids": list(evidence),
        "verification": "missing" if value is None else "unreviewed",
    }


def field(name, value, evidence=(), targets=None):
    item = {"name": name, "fact": fact(value, evidence)}
    if targets:
        item["target_entity_ids"] = list(targets)
    return item


def part(entity_id, role, label, evidence, *, name=None, smiles=None, amounts=()):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence) if name is not None else fact(None),
        "smiles": fact(smiles, evidence) if smiles is not None else fact(None),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": list(amounts),
    }


def missing_ops():
    return [field("atmosphere", None), field("workup", None), field("purification", None)]


def rec(rid, kind, evidence, participants, steps, outcomes=(), notes=(), unresolved=()):
    return {
        "record_id": f"{DOC}:{rid}",
        "document_id": DOC,
        "source_reaction_id": rid,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": list(dict.fromkeys(evidence)),
        "participants": participants,
        "steps": steps,
        "outcomes": list(outcomes),
        "notes": [fact(x, evidence) for x in notes],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": list(unresolved),
        },
    }


records = []


# Page 2: three non-batch overview/mechanistic schemes.
e2 = ev(2)
records.append(rec(
    "scheme1_observed_13_lithium_shift", "general_scheme", e2,
    [part("generic_propargyl_allenyllithium", "reactant", "generic propargyl/1,2-allenyllithium species", e2),
     part("generic_shifted_lithium", "product", "generic 1,3-lithium-shifted species", e2)],
    [{"step_id": "controlled_13_lithium_shift", "participant_ids": ["generic_propargyl_allenyllithium", "generic_shifted_lithium"],
      "conditions": [field("operation", "controlled 1,3-lithium shift", e2)]}],
    notes=("Overview of the observed, controllable equilibration; R is alkyl and products are not specified in Scheme 1.",),
    unresolved=("Generic Ar/R structures and batch conditions are not specified; this is not represented as an individual experiment.",),
))
records.append(rec(
    "scheme4_controlled_lithium_shift_overview", "general_scheme", e2,
    [part("generic_1a_d", "reactant", "generic 1-aryl-1-alkyne 1a-d (R != H)", e2),
     part("generic_2", "product", "generic 1,1-diarylallene 2 (conditions A)", e2),
     part("generic_3", "product", "generic 1,3-diarylallene 3 (conditions B)", e2),
     part("znbr2", "reagent", "ZnBr2", e2, name="zinc bromide", smiles="[Zn+2].[Br-].[Br-]"),
     part("pdpph3", "catalyst", "[Pd(PPh3)4]", e2),
     part("ari", "reactant", "Ar2I", e2)],
    [{"step_id": "controlled_lithiation_and_coupling", "participant_ids": ["generic_1a_d", "znbr2", "pdpph3", "ari", "generic_2", "generic_3"],
      "conditions": [field("operation", "deprotonation, controlled lithium shift, transmetallation, and Pd-catalyzed coupling", e2)]}],
    unresolved=("Generic R groups and batch quantities are unresolved; Table 1 supplies concrete substrate/outcome rows.",),
))


# Page 2, Scheme 2: eight starting-material preparations.
scheme2_rows = [
    ("1a", "Ph", "C2H5", "ethyl iodide", 87, "CCC#Cc1ccccc1", "alkylation"),
    ("1b", "Ph", "nC3H7", "1-iodopropane", 51, "CCCC#Cc1ccccc1", "alkylation"),
    ("1c", "nC4H9", "Ph", "iodobenzene", 78, "CCCCC#Cc1ccccc1", "sonogashira"),
    ("1d", "nC3H7", "p-PhC6H4", "4-bromobiphenyl", 74, "CCCC#Cc1ccc(-c2ccccc2)cc1", "sonogashira"),
    ("1e", "nC3H7", "p-MeOC6H4", "4-iodoanisole", 82, "CCCC#Cc1ccc(OC)cc1", "sonogashira"),
    ("1f", "Ph", "vinyl", "vinyl bromide", 57, "C=CC#Cc1ccccc1", "sonogashira"),
    ("1g", "p-CH3C6H4", "vinyl", "vinyl bromide", 78, "C=CC#Cc1ccc(C)cc1", "sonogashira"),
    ("1h", "p-CH3OC6H4", "vinyl", "vinyl bromide", 85, "C=CC#Cc1ccc(OC)cc1", "sonogashira"),
]
for label, r1, r2, electrophile, yld, smiles, mode in scheme2_rows:
    rid = f"scheme2_preparation_{label}"
    product_id = f"product_{label}"
    if mode == "alkylation":
        participants = [
            part("terminal_alkyne", "reactant", f"R1-C#CH (R1={r1})", e2),
            part("nbuli", "reagent", "nBuLi", e2),
            part("hmpa", "reagent", "HMPA", e2),
            part("electrophile", "reactant", electrophile, e2),
            part("thf", "solvent", "THF", e2, name="tetrahydrofuran", smiles="C1CCOC1"),
            part(product_id, "product", label, e2, smiles=smiles),
        ]
        conditions = [field("temperature", {"number": -78, "unit": "°C"}, e2),
                      field("operation", "nBuLi deprotonation followed by HMPA/electrophile addition and warming from -78 °C to room temperature", e2)]
    else:
        participants = [
            part("terminal_alkyne", "reactant", f"R1-C#CH (R1={r1})", e2),
            part("electrophile", "reactant", electrophile, e2),
            part("pd_catalyst", "catalyst", "Pd catalyst", e2, amounts=[field("loading", {"minimum": 1, "maximum": 5, "unit": "mol%", "raw_text": "1-5 mol%"}, e2)]),
            part("cui", "catalyst", "CuI", e2, name="copper(I) iodide", smiles="[Cu]I"),
            part("amine", "solvent", "Et3N or NHEt2", e2),
            part(product_id, "product", label, e2, smiles=smiles),
        ]
        conditions = [field("operation", "Pd/Cu-catalyzed coupling", e2)]
    conditions += missing_ops()
    records.append(rec(rid, "substrate_scope_entry", e2, participants,
                       [{"step_id": "preparation", "participant_ids": [p["entity_id"] for p in participants], "conditions": conditions}],
                       [field("product_yield", {"number": yld, "unit": "%"}, e2, [product_id]), field("yield_measurement_basis", None)],
                       unresolved=("The covered main text does not state atmosphere, workup, purification, duration, or yield basis.",)))


# Page 2, Scheme 3: three successive preparation stages for [D]-1c.
scheme3 = [
    ("scheme3_methyl_butyrate_reduction", "methyl_butyrate", "methyl butyrate", "liad4", "LiAlD4", "deuterated_butanol", "nC3H7CD2OH", 43),
    ("scheme3_tosylation", "deuterated_butanol", "nC3H7CD2OH", "tscl", "TsCl", "deuterated_tosylate", "nC3H7CD2OTs", 89),
    ("scheme3_alkylation_to_d1c", "phenylacetylene", "phenylacetylene", "deuterated_tosylate", "nC3H7CD2OTs", "d1c", "[D]-1c", 53),
]
for rid, a_id, a_label, b_id, b_label, p_id, p_label, yld in scheme3:
    ps = [part(a_id, "reactant", a_label, e2), part(b_id, "reagent" if b_id in {"liad4", "tscl"} else "reactant", b_label, e2), part(p_id, "product", p_label, e2)]
    if rid.endswith("d1c"):
        ps.extend([part("nbuli", "reagent", "nBuLi", e2), part("hmpa", "reagent", "HMPA", e2)])
    records.append(rec(rid, "reported_experiment", e2, ps,
                       [{"step_id": "stage", "participant_ids": [p["entity_id"] for p in ps], "conditions": [field("operation", "reaction as depicted in Scheme 3", e2)] + missing_ops()}],
                       [field("stage_yield", {"number": yld, "unit": "%"}, e2, [p_id]), field("yield_measurement_basis", None)],
                       unresolved=("Stage time, temperature, atmosphere, workup, purification, and yield basis are not stated on the covered page.",)))


# Pages 2--3, Table 1: each Conditions A/B result is an independent experiment.
e23 = ev(2, 3)
table1 = [
    (1, "1a", "Ph", "C2H5", "Ph", 55, "2a", 84, "3a", None, None, "isolated"),
    (2, "1c", "Ph", "nC4H9", "Ph", 71, "2b", 89, "3b", "99:1", None, "isolated"),
    (3, "1c", "Ph", "nC4H9", "p-MeC6H4", 79, "2c", 99, "3c", "99:1", None, "isolated"),
    (4, "1c", "Ph", "nC4H9", "alpha-naphthyl", 63, "2d", 56, "3d", None, None, "isolated"),
    (5, "1c", "Ph", "nC4H9", "p-MeOC6H4", 74, "2e", 83, "3e", "98:2", None, "isolated"),
    (6, "1c", "Ph", "nC4H9", "p-MeO2CC6H4", 93, "2f", 71, "3f", None, None, "isolated"),
    (7, "1b", "Ph", "nC3H7", "Ph", 76, "2g", 96, "3g", None, None, "B_NMR"),
    (8, "1d", "p-PhC6H4", "nC3H7", "Ph", 77, "2h", 72, "3h", None, None, "isolated"),
    (9, "1d", "p-PhC6H4", "nC3H7", "p-BrC6H4", 69, "2i", 71, "3i", None, None, "isolated"),
]
for row, start, ar1, chain, ar2, ya, pa, yb, pb, ratio_a, ratio_b, basis in table1:
    for cond, yld, prod, ratio in [("A", ya, pa, ratio_a), ("B", yb, pb, ratio_b)]:
        rid = f"table1_entry{row}_condition{cond}_{prod}"
        reagent = "nBuLi" if cond == "A" else "LDA"
        ps = [part("substrate", "reactant", f"{start}: Ar1={ar1}, alkyl={chain}", e23),
              part("base", "reagent", reagent, e23), part("znbr2", "reagent", "ZnBr2", e23),
              part("pdpph3", "catalyst", "[Pd(PPh3)4]", e23), part("aryl_halide", "reactant", f"Ar2I (Ar2={ar2})", e23),
              part("product", "product", prod, e23)]
        if ratio:
            minor_label = pb if cond == "A" else pa
            ps.append(part("minor_product", "product", minor_label, e23))
        lith_temp = {"number": -20, "unit": "°C"} if cond == "A" else "r.t."
        cs = [field("lithiation_temperature", lith_temp, e23), field("lithiation_time", {"number": 1, "unit": "h"}, e23),
              field("coupling_temperature", "r.t.", e23), field("operation", "lithiation, ZnBr2 transmetallation, and Pd-catalyzed coupling", e23)] + missing_ops()
        outs = [field("product_yield", {"number": yld, "unit": "%"}, e23, ["product"]),
                field("yield_measurement_basis", "300 MHz 1H NMR with CH2Br2 internal standard" if basis == "B_NMR" and cond == "B" else "isolated yield", e23)]
        if ratio:
            outs.append(field("2_to_3_ratio", ratio, e23, ["product", "minor_product"]))
            outs.append(field("ratio_measurement_basis", "300 MHz 1H NMR", e23))
        records.append(rec(rid, "substrate_scope_entry", e23, ps,
                           [{"step_id": "sequential_reaction", "participant_ids": [p["entity_id"] for p in ps], "conditions": cs}], outs,
                           unresolved=("The table and covered prose omit reagent quantities, atmosphere, workup, and purification.",)))


# Page 3, Scheme 5 overview.
e3 = ev(3)
records.append(rec(
    "scheme5_carbolithiation_shift_overview", "general_scheme", e3,
    [part("generic_enyne", "reactant", "generic 1-arylbut-3-en-1-yne 1f-h", e3),
     part("rli", "reagent", "RLi", e3), part("generic_4", "product", "generic 1,1-diarylallene 4", e3),
     part("generic_5", "product", "generic 1,3-diarylallene 5", e3), part("znbr2", "reagent", "ZnBr2", e3),
     part("pdpph3", "catalyst", "[Pd(PPh3)4]", e3), part("ari", "reactant", "Ar2I", e3)],
    [{"step_id": "carbolithiation_shift_and_coupling", "participant_ids": ["generic_enyne", "rli", "znbr2", "pdpph3", "ari", "generic_4", "generic_5"],
      "conditions": [field("operation", "conjugate carbolithiation, optional 1,3-lithium shift, transmetallation and coupling", e3)]}],
    unresolved=("Generic R groups and batch conditions are not specified; Tables 2-4 contain independent concrete rows.",),
))


# Page 3, Table 2 temperature optimization.
table2 = [(-78, "100:0", 54), (-40, "57:43", 42), (-20, "14:86", 44), (-78, "0:100", 18)]
for idx, (temp, ratio, yld) in enumerate(table2, 1):
    ps = [part("1f", "reactant", "1-phenylbut-3-en-1-yne (1f)", e3, smiles="C=CC#Cc1ccccc1"),
          part("nbuli", "reagent", "nBuLi", e3), part("znbr2", "reagent", "ZnBr2", e3),
          part("phi", "reactant", "phenyl iodide", e3, smiles="Ic1ccccc1"), part("pdpph3", "catalyst", "[Pd(PPh3)4]", e3),
          part("4a", "product", "1,1-diphenylocta-1,2-diene (4a)", e3), part("5a", "product", "1,3-diphenylocta-1,2-diene (5a)", e3)]
    if idx == 4:
        cs = [field("carbolithiation_temperature", {"number": -78, "unit": "°C"}, e3), field("carbolithiation_time", {"number": 1, "unit": "h"}, e3),
              field("warming_time_to_room_temperature", {"number": 2, "unit": "h"}, e3), field("transmetallation_temperature", "r.t.", e3),
              field("operation", "ZnBr2 addition at room temperature followed by Pd-catalyzed coupling", e3)] + missing_ops()
    else:
        cs = [field("carbolithiation_temperature", {"number": temp, "unit": "°C"}, e3), field("carbolithiation_time", {"number": 1, "unit": "h"}, e3),
              field("transmetallation_time", {"number": 10, "unit": "min", "qualifier": "approx", "raw_text": "~10 min"}, e3),
              field("warming_time_to_room_temperature", {"number": 20, "unit": "min"}, e3), field("coupling_temperature", "r.t.", e3),
              field("coupling_time", {"number": 2, "unit": "h"}, e3)] + missing_ops()
    records.append(rec(f"table2_entry{idx}_temperature", "optimization_entry", e3, ps,
                       [{"step_id": "temperature_screen", "participant_ids": [p["entity_id"] for p in ps], "conditions": cs}],
                       [field("4a_to_5a_ratio", ratio, e3, ["4a", "5a"]), field("combined_product_yield", {"number": yld, "unit": "%"}, e3, ["4a", "5a"]),
                        field("yield_measurement_basis", "300 MHz 1H NMR; based on 1f; CH2Br2 internal standard", e3), field("ratio_measurement_basis", "300 MHz 1H NMR", e3)],
                       unresolved=("Atmosphere, workup, and purification are not stated.",)))


# Page 3, Table 3 additive optimization.
table3 = [
    (1, "pyridine", 1.2, "100:0", {"number": 34, "unit": "%"}, "NMR"),
    (2, "nBu4NI", 1.2, "100:0", {"number": 92, "unit": "%"}, "NMR"),
    (3, "N,N-diisopropylethylamine", 1.2, "98:2", {"number": 98, "unit": "%"}, "NMR"),
    (4, "DMAP", 1.2, "95:5", {"number": 98, "unit": "%"}, "NMR"),
    (5, "TMEDA", 1.2, "0:100", {"minimum": 50, "maximum": 70, "unit": "%", "qualifier": "approx", "raw_text": "~50-~70%"}, "isolated_contaminated"),
    (6, "HMPA", 1.2, "100:0-0:100", "quantitative", "NMR_variable"),
    (7, "HMPA", 2.0, "0:100", {"number": 83, "unit": "%"}, "isolated"),
]
for idx, additive, equiv, ratio, yld, basis in table3:
    ps = [part("1f", "reactant", "1-phenylbut-3-en-1-yne (1f)", e3, smiles="C=CC#Cc1ccccc1"), part("nbuli", "reagent", "nBuLi", e3),
          part("additive", "reagent", additive, e3, amounts=[field("equivalents", {"number": equiv, "unit": "equiv"}, e3)]),
          part("znbr2", "reagent", "ZnBr2", e3), part("phi", "reactant", "phenyl iodide", e3, smiles="Ic1ccccc1"),
          part("pdpph3", "catalyst", "[Pd(PPh3)4]", e3, amounts=[field("loading", {"number": 5, "unit": "mol%"}, e3)]),
          part("4a", "product", "4a", e3), part("5a", "product", "5a", e3)]
    cs = [field("carbolithiation_temperature", {"number": -78, "unit": "°C"}, e3), field("carbolithiation_time", {"number": 1, "unit": "h"}, e3),
          field("additive_temperature", {"number": -78, "unit": "°C"}, e3), field("additive_stage_time", {"minimum": 1, "maximum": 1.3, "unit": "h", "raw_text": "1-1.3 h"}, e3),
          field("warming_time_to_room_temperature", {"number": 20, "unit": "min"}, e3), field("transmetallation_time", {"number": 10, "unit": "min"}, e3),
          field("coupling_temperature", "r.t.", e3), field("coupling_time", {"number": 2, "unit": "h"}, e3)] + missing_ops()
    outs = [field("4a_to_5a_ratio", ratio, e3, ["4a", "5a"]), field("combined_product_yield", yld, e3, ["4a", "5a"])]
    if basis == "NMR":
        outs += [field("yield_measurement_basis", "300 MHz 1H NMR; based on aryl halide; CH2Br2 internal standard", e3), field("ratio_measurement_basis", "300 MHz 1H NMR", e3)]
    elif basis == "isolated_contaminated":
        outs += [field("yield_measurement_basis", "isolated product contaminated with an impurity", e3)]
    elif basis == "isolated":
        outs += [field("yield_measurement_basis", "isolated yield", e3)]
    else:
        outs += [field("yield_measurement_basis", "300 MHz 1H NMR; based on aryl halide; CH2Br2 internal standard", e3), field("ratio_measurement_basis", "ratio changed constantly", e3)]
    records.append(rec(f"table3_entry{idx}_{additive.lower().replace(',', '').replace(' ', '_')}", "optimization_entry", e3, ps,
                       [{"step_id": "additive_screen", "participant_ids": [p["entity_id"] for p in ps], "conditions": cs}], outs,
                       unresolved=("Rows 5-6 were reported as poorly reproducible; row 5 product was contaminated and row 6 ratio changed constantly.",) if idx in (5, 6) else ("Atmosphere, workup, and purification are not stated.",)))


# Page 4, Table 4: 14 Conditions C results and 13 reported Conditions D results.
e4 = ev(4)
table4 = [
    (1, "1f", "Ph", "nBu", "Ph", 81, "4a", 83, "5a", 2),
    (2, "1f", "Ph", "nBu", "o-CH3C6H4", 78, "4b", 75, "5b", 2),
    (3, "1f", "Ph", "nBu", "alpha-naphthyl", 92, "4c", 91, "5c", 2),
    (4, "1f", "Ph", "nBu", "p-MeOC6H4", 97, "4d", 98, "5d", 2),
    (5, "1f", "Ph", "nBu", "p-MeO2CC6H4", 96, "4e", 93, "5e", 2),
    (6, "1f", "Ph", "nBu", "p-CNC6H4", 95, "4f", 95, "5f", 2),
    (7, "1f", "Ph", "sBu", "Ph", 84, "4g", 76, "5g", 2),
    (8, "1f", "Ph", "tBu", "Ph", 92, "4h", 85, "5h", 2),
    (9, "1f", "Ph", "tBu", "o-CH3C6H4", 95, "4i", 79, "5i", 2),
    (10, "1f", "Ph", "tBu", "alpha-naphthyl", 99, "4j", 62, "5j", 2),
    (11, "1f", "Ph", "tBu", "p-MeOC6H4", 97, "4k", 69, "5k", 3),
    (12, "1f", "Ph", "tBu", "p-NCC6H4", 76, "4l", 69, "5l", 3),
    (13, "1g", "p-MeC6H4", "nBu", "Ph", 89, "4m", 59, "5m", 2),
    (14, "1h", "p-MeOC6H4", "nBu", "Ph", 61, "4d", None, None, 2),
]
for row, substrate, ar1, rli, ar2, yc, pc, yd, pd, hmpa_eq in table4:
    for cond, yld, product in [("C", yc, pc), ("D", yd, pd)]:
        if yld is None:
            continue
        ps = [part("substrate", "reactant", f"{substrate} (Ar1={ar1})", e4), part("rli", "reagent", f"{rli}Li", e4),
              part("znbr2", "reagent", "ZnBr2", e4), part("aryl_iodide", "reactant", f"Ar2I (Ar2={ar2})", e4),
              part("pdpph3", "catalyst", "[Pd(PPh3)4]", e4), part("product", "product", product, e4)]
        cs = [field("carbolithiation_temperature", {"number": -78, "unit": "°C"}, e4), field("carbolithiation_time", {"number": 1, "unit": "h"}, e4)]
        if cond == "D":
            ps.insert(2, part("hmpa", "reagent", "HMPA", e4, amounts=[field("equivalents", {"number": hmpa_eq, "unit": "equiv"}, e4)]))
            cs += [field("hmpa_addition_temperature", {"number": -78, "unit": "°C"}, e4), field("operation", "warm naturally to room temperature, then transmetallation and coupling at room temperature", e4)]
        else:
            cs += [field("operation", "transmetallation and coupling at room temperature", e4)]
        cs += missing_ops()
        outs = [field("product_yield", {"number": yld, "unit": "%"}, e4, ["product"]), field("yield_measurement_basis", "isolated yield", e4)]
        if row == 4 and cond == "D":
            ps.append(part("minor_product", "product", "4d", e4))
            outs.append(field("5d_to_4d_ratio", "97:3", e4, ["product", "minor_product"]))
        records.append(rec(f"table4_entry{row}_condition{cond}_{product}", "substrate_scope_entry", e4, ps,
                           [{"step_id": f"condition_{cond}", "participant_ids": [p["entity_id"] for p in ps], "conditions": cs}], outs,
                           unresolved=("Exact organolithium/ZnBr2/aryl iodide/catalyst quantities, atmosphere, workup, and purification are absent from the covered source.",)))


# Page 4, Scheme 6: two isotopic cross experiments.
scheme6_cases = [
    ("scheme6_cross_experiment_condition1", "LDA", [part("lda", "reagent", "LDA", e4, amounts=[field("equivalents", {"number": 2, "unit": "equiv"}, e4)]),
                                                     part("ipr2nh", "reagent", "diisopropylamine", e4), part("nbuli", "reagent", "nBuLi", e4)],
     [field("operation", "LDA prepared from diisopropylamine and nBuLi in a 1:1.5 molar ratio; cross experiment under conditions B", e4)], 57, "80:20", 78, "71:29"),
    ("scheme6_cross_experiment_condition2", "nBuLi/HMPA", [part("nbuli", "reagent", "nBuLi", e4), part("hmpa", "reagent", "HMPA", e4)],
     [field("lithiation_temperature", {"number": -20, "unit": "°C"}, e4), field("lithiation_time", {"number": 1, "unit": "h"}, e4),
      field("hmpa_addition_temperature", {"number": -20, "unit": "°C"}, e4), field("warming_time_to_room_temperature", {"number": 1, "unit": "h"}, e4)], 36, "58:42", 52, "62:38"),
]
for rid, label, extra, extra_conditions, y1, r1, y2, r2 in scheme6_cases:
    ps = [part("d1c", "reactant", "[D]-1c", e4), part("1e", "reactant", "1e", e4), *extra,
          part("znbr2", "reagent", "ZnBr2", e4), part("phi", "reactant", "phenyl iodide", e4, smiles="Ic1ccccc1"),
          part("pdpph3", "catalyst", "[Pd(PPh3)4]", e4, amounts=[field("loading", {"number": 5, "unit": "mol%"}, e4)]),
          part("3b", "product", "3b", e4), part("d3b", "product", "[D]-3b", e4), part("6", "product", "6", e4), part("d6", "product", "[D]-6", e4)]
    cs = [field("starting_material_ratio", "[D]-1c/1e = 1:1", e4), *extra_conditions,
          field("operation", "sequential transmetallation and Pd-catalyzed coupling", e4)] + missing_ops()
    outs = [field("combined_3b_d3b_yield", {"number": y1, "unit": "%"}, e4, ["3b", "d3b"]), field("3b_to_d3b_ratio", r1, e4, ["3b", "d3b"]),
            field("combined_6_d6_yield", {"number": y2, "unit": "%"}, e4, ["6", "d6"]), field("6_to_d6_ratio", r2, e4, ["6", "d6"]),
            field("yield_measurement_basis", None), field("ratio_measurement_basis", None)]
    records.append(rec(rid, "reported_experiment", e4, ps,
                       [{"step_id": "cross_experiment", "participant_ids": [p["entity_id"] for p in ps], "conditions": cs}], outs,
                       unresolved=("The covered source does not state reaction scale, several reagent amounts, yield/ratio measurement basis, atmosphere, workup, or purification.",)))


# Page 5: proposed paths, allene preparation, coupling tests, and deuterium-quench tests.
e5 = ev(5)
records.append(rec(
    "scheme7_proposed_lithium_shift_paths", "mechanism", e5,
    [part("lithiated_substrate", "reactant", "lithiated 1-aryl-1-alkyne/propargyl-allenyllithium", e5),
     part("allene_e", "unspecified_agent", "allene intermediate E", e5), part("dilithium_f", "unspecified_agent", "1,3-dilithium intermediate F", e5),
     part("shifted_lithium", "product", "1,3-lithium-shifted intermediate", e5), part("znbr2", "reagent", "ZnBr2", e5),
     part("pdpph3", "catalyst", "[Pd(PPh3)4]", e5), part("phi", "reactant", "phenyl iodide", e5, smiles="Ic1ccccc1"),
     part("coupled_allene", "product", "generic coupled allene product", e5)],
    [{"step_id": "path_a", "participant_ids": ["lithiated_substrate", "allene_e", "shifted_lithium"], "conditions": [field("operation", "iPr2NH-induced proton-shuttle pathway", e5)]},
     {"step_id": "path_b", "participant_ids": ["lithiated_substrate", "allene_e", "dilithium_f", "shifted_lithium"], "conditions": [field("operation", "proposed bimolecular intermolecular-lithiation pathway", e5)]},
     {"step_id": "downstream_coupling", "participant_ids": ["shifted_lithium", "znbr2", "pdpph3", "phi", "coupled_allene"], "conditions": [field("operation", "depicted ZnBr2 transmetallation and Pd-catalyzed coupling", e5)]}],
    unresolved=("Scheme 7 is proposed mechanistic interpretation, not an isolated batch; generic R structures remain unresolved.",),
))

ps8 = [part("1f", "reactant", "1-phenylbut-3-en-1-yne (1f)", e5, smiles="C=CC#Cc1ccccc1"), part("nbuli", "reagent", "nBuLi", e5),
       part("proton_source", "reagent", "H+", e5), part("7", "product", "1-phenylocta-1,2-diene (7)", e5)]
records.append(rec("scheme8_synthesis_allene_7", "reported_experiment", e5, ps8,
                   [{"step_id": "carbolithiation_protonation", "participant_ids": [p["entity_id"] for p in ps8],
                     "conditions": [field("temperature", {"number": -78, "unit": "°C"}, e5), field("time", {"number": 1, "unit": "h"}, e5),
                                    field("operation", "nBuLi conjugate addition followed by protonation", e5)] + missing_ops()}],
                   [field("product_yield", {"number": 37, "unit": "%"}, e5, ["7"]), field("yield_measurement_basis", None)],
                   unresolved=("Scale, reagent amounts, atmosphere, workup, purification, and yield basis are not stated.",)))

scheme9 = [("prepared_lda_1_to_1_5", "N,N-diisopropylamine:nBuLi = 1:1.5", 70),
           ("prepared_lda_1_to_1_1", "N,N-diisopropylamine:nBuLi = 1:1.1", 67),
           ("commercial_lda", "commercial LDA", 62)]
for suffix, lda_source, yld in scheme9:
    ps = [part("7", "reactant", "1-phenylocta-1,2-diene (7)", e5),
          part("lda", "reagent", "LDA", e5, amounts=[field("equivalents", {"number": 2, "unit": "equiv"}, e5)]),
          part("znbr2", "reagent", "ZnBr2", e5), part("phi", "reactant", "phenyl iodide", e5, smiles="Ic1ccccc1"),
          part("pdpph3", "catalyst", "[Pd(PPh3)4]", e5), part("5a", "product", "1,3-diphenylocta-1,2-diene (5a)", e5)]
    cs = [field("lda_source", lda_source, e5), field("lithiation_temperature", "r.t.", e5), field("lithiation_time", {"number": 1, "unit": "h"}, e5),
          field("transmetallation_temperature", "r.t.", e5), field("operation", "ZnBr2 transmetallation and Pd-catalyzed coupling with phenyl iodide", e5)] + missing_ops()
    records.append(rec(f"scheme9_{suffix}", "reported_experiment", e5, ps,
                       [{"step_id": "lithiation_coupling", "participant_ids": [p["entity_id"] for p in ps], "conditions": cs}],
                       [field("product_yield", {"number": yld, "unit": "%"}, e5, ["5a"]), field("yield_measurement_basis", "isolated yield", e5)],
                       unresolved=("Scale, ZnBr2/phenyl iodide/catalyst quantities, coupling time, atmosphere, workup, and purification are not stated.",)))

scheme10 = [("prepared_lda_1_to_1_5", "LDA", 2, "N,N-diisopropylamine:nBuLi = 1:1.5", 92),
            ("prepared_lda_1_to_1_1", "LDA", 2, "N,N-diisopropylamine:nBuLi = 1:1.1", 85),
            ("commercial_lda", "LDA", 2, "commercial LDA", 79),
            ("nbuli", "nBuLi", 1.2, "nBuLi", 97)]
for suffix, reagent, equiv, source, dpercent in scheme10:
    ps = [part("7", "reactant", "1-phenylocta-1,2-diene (7)", e5),
          part("base", "reagent", reagent, e5, amounts=[field("equivalents", {"number": equiv, "unit": "equiv"}, e5)]),
          part("d2o", "reagent", "D2O", e5, smiles="[2H]O[2H]"), part("d7", "product", "1-phenyl-3-d-octa-1,2-diene ([D]-7)", e5)]
    cs = [field("base_source", source, e5), field("lithiation_temperature", "r.t.", e5), field("lithiation_time", {"number": 1, "unit": "h"}, e5),
          field("quench_temperature", "r.t.", e5), field("operation", "lithiation followed by D2O quench", e5)] + missing_ops()
    records.append(rec(f"scheme10_{suffix}", "reported_experiment", e5, ps,
                       [{"step_id": "lithiation_deuteration", "participant_ids": [p["entity_id"] for p in ps], "conditions": cs}],
                       [field("isotopic_incorporation", {"number": dpercent, "unit": "%"}, e5, ["d7"]), field("measurement_basis", None)],
                       unresolved=("Scale, D2O amount, atmosphere, workup, purification, and D-percent measurement basis are not stated.",)))


# Pages 5--6: one connected computational mechanism record.
e56 = ev(5, 6)
records.append(rec(
    "schemes11_12_computational_lda_mechanism", "mechanism", e56,
    [part("b1", "reactant", "1-phenyl-1,2-butadien-1-yllithium model B-1/B1/B2", e56),
     part("lda", "unspecified_agent", "LDA/diisopropylamine ligand", e56), part("e1_e2", "unspecified_agent", "1-phenylbuta-1,2-diene-LDA complexes E1/E2", e56),
     part("c1", "product", "isomerized 1-phenyl-1,2-butadien-3-yllithium model C-1/C1/C2", e56), part("g", "product", "1-phenyl-2-butyne model G", e56)],
    [{"step_id": "gas_phase_path", "participant_ids": ["b1", "lda", "e1_e2", "c1", "g"],
      "conditions": [field("operation", "B3LYP gas-phase optimization and harmonic-frequency calculations", e56), field("temperature", {"number": 298, "unit": "K"}, ev(6)),
                     field("rate_determining_step_activation_energy", "19.9 kcal mol-1", ev(6)),
                     field("third_step_activation_energy", "6.8 kcal mol-1", ev(6)),
                     field("second_proton_transfer_barrier", "25.9 kcal mol-1", ev(6))]}],
    notes=("Step 2 is identified as rate-determining; C2 is reported 4.0 kcal mol-1 more stable than B1, while G is 16.9 kcal mol-1 less stable than C2.",),
    unresolved=("This is a computational/proposed pathway rather than a reported synthetic experiment; exact coordination structures and energy-reference conventions require specialist review.",),
))


OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")

ids = [r["record_id"] for r in records]
by_prefix = lambda prefix: [x for x in ids if x.startswith(f"{DOC}:{prefix}")]

page2_ids = by_prefix("scheme1_") + by_prefix("scheme2_") + by_prefix("scheme3_") + by_prefix("scheme4_") + by_prefix("table1_")
page3_ids = by_prefix("table1_") + by_prefix("scheme5_") + by_prefix("table2_") + by_prefix("table3_")
page4_ids = by_prefix("table4_") + by_prefix("scheme6_")
page5_ids = by_prefix("scheme7_") + by_prefix("scheme8_") + by_prefix("scheme9_") + by_prefix("scheme10_") + by_prefix("schemes11_")
page6_ids = by_prefix("schemes11_")

coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {"page": 1, "state": "attempted", "regions": [
            {"region": "full original page: title, abstract, introduction, and SI-availability notice",
             "finding": "No row-level experiment, reaction arrow, table, or experimental footnote. Abstract-level reaction and mechanism claims were not duplicated as experiments.",
             "evidence_ids": ev(1)}], "record_ids": [],
         "unresolved": ["The paper states that supporting information is available online, but no SI file was supplied or explicitly associated."]},
        {"page": 2, "state": "attempted", "regions": [
            {"region": "upper-left Scheme 1", "finding": "Generic overview of the observed controllable 1,3-lithium shift; classified as a general scheme.", "evidence_ids": ev(2)},
            {"region": "lower-left Scheme 2", "finding": "Eight starting-material preparations 1a-1h extracted row-wise with depicted reagents and yields.", "evidence_ids": ev(2)},
            {"region": "upper-right Scheme 3", "finding": "Three successive stages for [D]-1c extracted separately with 43%, 89%, and 53% yields.", "evidence_ids": ev(2)},
            {"region": "middle-right Scheme 4 and adjacent conditions prose", "finding": "Generic A/B pathway classified as a general scheme; explicit A/B lithiation temperature and time are linked to the eighteen Table 1 records on page 3.", "evidence_ids": ev(2)}],
         "record_ids": page2_ids,
         "unresolved": ["Scheme 2/3 procedures omit several durations, amounts, atmospheres, workups, purifications, and yield bases.", "Generic Scheme 1/4 structures are not complete molecules."]},
        {"page": 3, "state": "attempted", "regions": [
            {"region": "upper-left Table 1 and footnotes", "finding": "Nine substrate rows under each of Conditions A and B extracted as eighteen independent experiments; isolated/NMR bases and ratio footnotes retained.", "evidence_ids": ev(3)},
            {"region": "lower-left Scheme 5", "finding": "Generic conjugate-addition/1,3-lithium-shift map classified as a general scheme rather than a batch experiment.", "evidence_ids": ev(3)},
            {"region": "upper-right Table 2 and footnote", "finding": "Four temperature-screen experiments extracted separately, including the entry-4 warm-to-room-temperature override.", "evidence_ids": ev(3)},
            {"region": "lower-right Table 3 and footnotes", "finding": "Seven additive-screen experiments extracted; HMPA two-equivalent override, variable ratio, contaminated product, and isolated-yield footnote retained.", "evidence_ids": ev(3)}],
         "record_ids": page3_ids,
         "unresolved": ["Most table rows omit scale, atmosphere, workup, and purification.", "Table 3 entries 5 and 6 were explicitly poorly reproducible."]},
        {"page": 4, "state": "attempted", "regions": [
            {"region": "upper-right Table 4 and conditions prose", "finding": "Fourteen Conditions C results and thirteen reported Conditions D results extracted independently; the row-14 Conditions D dash was not interpreted as zero or as proof of a performed experiment.", "evidence_ids": ev(4)},
            {"region": "lower half Scheme 6 and footnote", "finding": "Two isotope cross experiments extracted, each retaining two combined yields and two isotopologue ratios.", "evidence_ids": ev(4)},
            {"region": "lower-left mechanistic discussion", "finding": "Narrative proposes intermolecular pathways and introduces Scheme 7; no extra batch beyond Scheme 6 was created.", "evidence_ids": ev(4)}],
         "record_ids": page4_ids,
         "unresolved": ["Table 4 row 14 Conditions D contains only a table dash; its meaning is not defined.", "Table 4 and Scheme 6 omit several reagent quantities, atmosphere, workup, purification, and measurement bases."]},
        {"page": 5, "state": "attempted", "regions": [
            {"region": "upper-left Scheme 7", "finding": "Two proposed 1,3-lithium-shift pathways captured as one mechanism record, not as observed isolated experiments.", "evidence_ids": ev(5)},
            {"region": "middle-left Scheme 8", "finding": "Synthesis of allene 7 extracted as a 37%-yield reported experiment.", "evidence_ids": ev(5)},
            {"region": "lower-left Scheme 9", "finding": "Three LDA-source variants extracted separately with isolated yields of 70%, 67%, and 62%.", "evidence_ids": ev(5)},
            {"region": "upper-right Scheme 10", "finding": "Four D2O-quench variants extracted separately with the reported D percentages.", "evidence_ids": ev(5)},
            {"region": "right-column Scheme 11 and computational introduction", "finding": "Computational isomerization model linked with page-6 Scheme 12 as a mechanism record.", "evidence_ids": ev(5)}],
         "record_ids": page5_ids,
         "unresolved": ["Schemes 8-10 omit scale and several operational details; D-percent measurement method is not stated.", "Scheme 11 is computational rather than a synthetic batch."]},
        {"page": 6, "state": "attempted", "regions": [
            {"region": "full original page: Figure 1, Scheme 12, and gas-phase mechanism prose", "finding": "DFT structures, transition states, relative energies, and proposed LDA proton-transfer pathway linked to the computational mechanism record; no new synthetic experiment is present.", "evidence_ids": ev(6)}],
         "record_ids": page6_ids,
         "unresolved": ["Calculated coordination structures and energy-reference conventions are not independently verified; computational validation is distinct from experimental chemistry verification."]},
    ],
}
COVERAGE.parent.mkdir(parents=True, exist_ok=True)
COVERAGE.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

tasks = json.loads(TASKS.read_text())
for task in tasks:
    if task.get("document_id") == DOC and task.get("task_id") in {f"{DOC}:page{i}:text" for i in range(1, 7)}:
        task["state"] = "attempted"
TASKS.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"records": len(records), "coverage_pages": [p["page"] for p in coverage["pages"]]}, ensure_ascii=False))
