#!/usr/bin/env python3
"""Build evidence-linked machine records for 224.ol9004273.pdf, PDF pages 1-4."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / "runs" / "current"
DOC = "doc_244bce29f8eb89d5"


def ev(page: int) -> list[str]:
    return [f"{DOC}:page{page}:image", f"{DOC}:page{page}:text"]


def unique(values):
    return list(dict.fromkeys(values))


def fact(value, evidence=None):
    return {
        "value": value,
        "evidence_ids": [] if value is None else list(evidence or []),
        "verification": "missing" if value is None else "unreviewed",
    }


def field(name, value, evidence, targets=None):
    result = {"name": name, "fact": fact(value, evidence)}
    if targets:
        result["target_entity_ids"] = list(targets)
    return result


def participant(entity_id, role, label, evidence, *, name=None, smiles=None, amounts=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence) if name is not None else fact(None),
        "smiles": fact(smiles, evidence) if smiles is not None else fact(None),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": list(amounts or []),
    }


def record(suffix, kind, evidence, participants, steps, outcomes, *, notes=None, unresolved=None):
    evidence = unique(evidence)
    return {
        "record_id": f"{DOC}:{suffix}",
        "document_id": DOC,
        "source_reaction_id": suffix,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": evidence,
        "participants": participants,
        "steps": steps,
        "outcomes": outcomes,
        "notes": [fact(text, evidence) for text in (notes or [])],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": list(unresolved or []),
        },
    }


def missing_conditions():
    return [
        field("atmosphere", None, []),
        field("workup", None, []),
        field("purification", None, []),
    ]


SMILES = {
    "oxalyl_chloride": "O=C(Cl)C(=O)Cl",
    "dmso": "CS(C)=O",
    "triethylamine": "CCN(CC)CC",
    "dipea": "CCN(C(C)C)C(C)C",
    "pyridine": "n1ccccc1",
    "dcm": "ClCCl",
    "toluene": "Cc1ccccc1",
}

R = {
    "a": ("n-C5H11", "CCCCC"),
    "b": ("C2H5", "CC"),
    "c": ("n-C3H7", "CCC"),
    "d": ("i-C3H7", "C(C)C"),
    "e": ("Ph", "c1ccccc1"),
    "f": ("p-CH3C6H4", "c1ccc(C)cc1"),
    "g": ("p-BrC6H4", "c1ccc(Br)cc1"),
    "h": ("n-C4H9C≡C", "C#CCCCC"),
}


def allenol_smiles(code):
    return f"C=C=C(C(=O)OC)C(O){R[code][1]}"


def enyne_smiles(code):
    return f"COC(=O)C(C#C)=C({R[code][1]})"


def diene_smiles(code):
    return f"C=C(Cl)C(C(=O)OC)=C({R[code][1]})"


def common_participant(entity_id, label, name, smiles, evidence, equiv=None):
    amounts = []
    if equiv is not None:
        amounts.append(field("equivalents", {"number": equiv, "unit": "equiv"}, evidence))
    return participant(entity_id, "reagent", label, evidence, name=name, smiles=smiles, amounts=amounts)


records = []

# Page 1 graphical abstract: a generic scope summary, not a batch experiment.
e = ev(1)
parts = [
    participant("generic_1", "reactant", "2-(methoxycarbonyl)-2,3-allenol 1 (R = alkyl, aryl, alkynyl)", e),
    participant("generic_e2", "product", "methyl 2-(ethynyl)alk-2(E)-enoate (E)-2", e),
    participant("generic_z3", "product", "methyl 2-(1'-chlorovinyl)alk-2(Z)-enoate (Z)-3", e),
    common_participant("oxalyl", "(ClCO)2", "oxalyl chloride", SMILES["oxalyl_chloride"], e),
    common_participant("dmso", "DMSO", "dimethyl sulfoxide", SMILES["dmso"], e),
    common_participant("et3n", "Et3N", "triethylamine", SMILES["triethylamine"], e),
    participant("dcm", "solvent", "CH2Cl2", e, name="dichloromethane", smiles=SMILES["dcm"]),
]
records.append(record(
    "graphical_abstract_general_scope", "general_scheme", e, parts,
    [{"step_id": "generic_two_branch_scope", "participant_ids": [p["entity_id"] for p in parts],
      "conditions": [field("operation", "two alternative one-pot branches summarized in the graphical abstract", e)]}],
    [field("e2_yield_scope", {"minimum": 56, "maximum": 85, "unit": "%", "raw_text": "56-85%"}, e, ["generic_e2"]),
     field("z3_yield_scope", {"minimum": 64, "maximum": 85, "unit": "%", "raw_text": "64-85%"}, e, ["generic_z3"])],
    notes=["Generic scope summary; it is not a single experimental batch."],
    unresolved=["Generic R groups are not expanded into complete structures.", "Yield basis is not stated in the graphical abstract."]
))


def scheme1_record(suffix, *, ox_eq, dmso_eq, base, base_eq, stage1_temp, stage1_time,
                   stage2_temp, stage2_time, y_e2, y_z3, recovery=None, evidence=None):
    evidence = evidence or ev(2)
    parts = [
        participant("one_a", "reactant", "1a", evidence,
                    name="3-(methoxycarbonyl)-1,2-nonadien-4-ol", smiles=allenol_smiles("a")),
        participant("e_two_a", "product", "(E)-2a", evidence,
                    name="methyl 2-ethynyloct-2(E)-enoate", smiles=enyne_smiles("a")),
        participant("z_three_a", "product", "(Z)-3a", evidence,
                    name="methyl 2-(1'-chlorovinyl)oct-2(Z)-enoate", smiles=diene_smiles("a")),
        common_participant("oxalyl", "(ClCO)2", "oxalyl chloride", SMILES["oxalyl_chloride"], evidence, ox_eq),
        participant("dcm", "solvent", "CH2Cl2", evidence, name="dichloromethane", smiles=SMILES["dcm"]),
    ]
    if dmso_eq is not None:
        parts.append(common_participant("dmso", "DMSO", "dimethyl sulfoxide", SMILES["dmso"], evidence, dmso_eq))
    if base:
        smi = SMILES[{"Et3N": "triethylamine", "EtN(Pr-i)2": "dipea", "pyridine": "pyridine"}[base]]
        parts.append(common_participant("base", base, {"Et3N": "triethylamine", "EtN(Pr-i)2": "Hünig's base", "pyridine": "pyridine"}[base], smi, evidence, base_eq))
    conditions = []
    if stage1_temp == "-78 °C to r.t.":
        conditions.extend([
            field("temperature_stage_1_initial", {"number": -78, "unit": "°C"}, evidence),
            field("operation_stage_1", "allowed to warm from -78 °C to r.t.", evidence),
        ])
    else:
        conditions.append(field("temperature_stage_1", stage1_temp, evidence))
    conditions.append(field("time_stage_1", stage1_time, evidence))
    if stage2_temp == "-78 °C to r.t.":
        conditions.extend([
            field("temperature_stage_2_initial", {"number": -78, "unit": "°C"}, evidence),
            field("operation_stage_2", "allowed to warm from -78 °C to r.t.", evidence),
        ])
    else:
        conditions.append(field("temperature_stage_2", stage2_temp, evidence))
    conditions.extend([field("time_stage_2", stage2_time, evidence), field("solvent", "CH2Cl2", evidence)])
    conditions += missing_conditions()
    outcomes = [
        field("reported_yield_e2a", {"number": y_e2, "unit": "%"}, evidence, ["e_two_a"]),
        field("reported_yield_z3a", ({"number": y_z3, "unit": "%"} if isinstance(y_z3, (int, float)) else y_z3), evidence, ["z_three_a"]),
        field("yield_measurement_basis", "NMR yield using 1,3,5-trimethylbenzene as internal standard", evidence),
    ]
    if recovery is not None:
        outcomes.append(field("recovered_starting_material_yield", {"number": recovery, "unit": "%"}, evidence, ["one_a"]))
    return record(suffix, "optimization_entry", evidence, parts,
                  [{"step_id": "one_pot_reaction", "participant_ids": [p["entity_id"] for p in parts], "conditions": conditions}],
                  outcomes,
                  unresolved=["Atmosphere, workup, and purification are not reported on the covered pages.",
                              "Candidate structures and alkene geometry remain unverified."])


# Scheme 1 entries 1-2 and the Scheme 1 entry 3/Table 1 entry 1 identity.
records.append(scheme1_record(
    "scheme1_entry1_swern_conditions", ox_eq=6, dmso_eq=6, base="Et3N", base_eq=6,
    stage1_temp={"number": -78, "unit": "°C"}, stage1_time={"number": 5, "unit": "h"},
    stage2_temp="-78 °C to r.t.", stage2_time={"number": 13, "unit": "h"},
    y_e2=2, y_z3=54, recovery=16, evidence=unique(ev(1) + ev(2))))
records.append(scheme1_record(
    "scheme1_entry2_without_triethylamine", ox_eq=6, dmso_eq=6, base=None, base_eq=None,
    stage1_temp="-78 °C to r.t.", stage1_time={"number": 23, "unit": "h"},
    stage2_temp=None, stage2_time=None, y_e2=0, y_z3=48, recovery=15,
    evidence=unique(ev(1) + ev(2))))

table1 = [
    (1, "-78 °C to r.t.", 4, "Et3N", "r.t.", 1, 68, 7),
    (2, "r.t.", 2, "Et3N", "r.t.", 3, 66, 5),
    (3, "reflux", 2, "Et3N", "reflux", 3, 64, 6),
    (4, "reflux", 2, "Et3N", "r.t.", 5, 87, {"number": 0.5, "unit": "%", "qualifier": "lt", "raw_text": "<0.5%"}),
    (5, "reflux", 2, "EtN(Pr-i)2", "r.t.", 3, 71, 8),
    (6, "reflux", 2, "pyridine", "r.t.", 21, 0, 25),
]
for idx, t1, h1, base, t2, h2, y2, y3 in table1:
    evidence = ev(2) if idx != 1 else unique(ev(1) + ev(2))
    suffix = "scheme1_entry3_table1_entry1" if idx == 1 else f"table1_entry{idx}"
    rec = scheme1_record(
        suffix, ox_eq=3, dmso_eq=None, base=base, base_eq=3,
        stage1_temp=t1, stage1_time={"number": h1, "unit": "h"},
        stage2_temp=t2, stage2_time={"number": h2, "unit": "h"},
        y_e2=y2, y_z3=y3, evidence=evidence)
    if idx == 1:
        rec["notes"].append(fact("Scheme 1 entry 3 and Table 1 entry 1 describe the same experiment and are merged.", evidence))
    records.append(rec)


# Scheme 2: reduction used for stereochemical assignment.
e = ev(3)
parts = [
    participant("e_two_a", "reactant", "(E)-2a", e, name="methyl 2-ethynyloct-2(E)-enoate", smiles=enyne_smiles("a")),
    participant("e_four_a", "product", "(E)-4a", e, name="allylic alcohol (E)-4a", smiles="OCC(C#C)=C(CCCCC)"),
    participant("dibal", "reagent", "DIBAL-H", e, name="diisobutylaluminium hydride",
                amounts=[field("equivalents", {"number": 2.5, "unit": "equiv"}, e)]),
    participant("toluene", "solvent", "toluene", e, name="toluene", smiles=SMILES["toluene"]),
]
records.append(record(
    "scheme2_dibal_reduction_e2a_to_e4a", "reported_experiment", e, parts,
    [{"step_id": "dibal_reduction", "participant_ids": [p["entity_id"] for p in parts],
      "conditions": [field("temperature_initial", {"number": -78, "unit": "°C"}, e),
                     field("operation", "allowed to warm from -78 °C to r.t.", e),
                     field("time", None, []), field("solvent", "toluene", e)] + missing_conditions()}],
    [field("reported_yield_e4a", {"number": 82, "unit": "%"}, e, ["e_four_a"]),
     field("yield_measurement_basis", None, []),
     field("stereochemical_assignment_method", "NOESY analysis of (E)-4a", e, ["e_four_a"])],
    unresolved=["Reaction duration, atmosphere, workup, purification, and yield basis are not reported.",
                "The candidate product structure and E geometry remain unverified."]
))


def table2_record(idx, code, h1, h2, y, *, scale=0.4, eq=3, side_z3=None):
    e = ev(3)
    rlabel = R[code][0]
    parts = [
        participant("one", "reactant", f"1{code} (R = {rlabel})", e, smiles=allenol_smiles(code),
                    amounts=[field("amount", {"number": scale, "unit": "mmol"}, e)]),
        participant("e_two", "product", f"(E)-2{code}", e, name=f"methyl 2-(ethynyl)alk-2(E)-enoate (E)-2{code}, R = {rlabel}", smiles=enyne_smiles(code)),
        common_participant("oxalyl", "(ClCO)2", "oxalyl chloride", SMILES["oxalyl_chloride"], e, eq),
        common_participant("et3n", "Et3N", "triethylamine", SMILES["triethylamine"], e, eq),
        participant("dcm", "solvent", "CH2Cl2", e, name="dichloromethane", smiles=SMILES["dcm"]),
    ]
    outcomes = [field("reported_yield_e2", {"number": y, "unit": "%"}, e, ["e_two"]), field("yield_measurement_basis", None, [])]
    if side_z3 is not None:
        parts.append(participant("z_three", "product", f"(Z)-3{code}", e,
                                 name=f"methyl 2-(1'-chlorovinyl)alk-2(Z)-enoate (Z)-3{code}, R = {rlabel}", smiles=diene_smiles(code)))
        outcomes.extend([
            field("nmr_yield_z3_side_product", {"number": side_z3, "unit": "%"}, e, ["z_three"]),
            field("side_product_yield_measurement_basis", "NMR yield", e),
        ])
    return record(
        f"table2_entry{idx}_e2{code}", "substrate_scope_entry", e, parts,
        [{"step_id": "oxalyl_chloride_then_base", "participant_ids": [p["entity_id"] for p in parts],
          "conditions": [field("temperature_stage_1", "reflux", e), field("time_stage_1", {"number": h1, "unit": "h"}, e),
                         field("temperature_stage_2", "r.t.", e), field("time_stage_2", {"number": h2, "unit": "h"}, e),
                         field("solvent", "CH2Cl2", e)] + missing_conditions()}],
        outcomes,
        unresolved=["Yield basis for the main (E)-2 product is not stated in Table 2.",
                    "Atmosphere, workup, and purification are not reported.",
                    "Candidate connectivity and E/Z assignments remain unverified."])


table2 = [
    (1, "a", 2, 5, 83, 0.4, 3, None),
    (2, "b", 2.5, 4.5, 62, 0.4, 3, None),
    (3, "c", 2, 4, 65, 0.4, 3, None),
    (4, "d", 2, 3.5, 67, 0.4, 3, None),
    (5, "e", 7, 10.5, 83, 0.4, 3, None),
    (6, "e", 7, 15, 85, 4.0, 3, None),
    (7, "f", 4, 7, 69, 0.4, 3, None),
    (8, "g", 7, 10.5, 83, 0.4, 5, None),
    (9, "h", 9, 12, 56, 0.4, 5, 12),
]
for row in table2:
    records.append(table2_record(*row[:5], scale=row[5], eq=row[6], side_z3=row[7]))


def table3_record(idx, code, hours, y):
    e = ev(3)
    rlabel = R[code][0]
    parts = [
        participant("one", "reactant", f"1{code} (R = {rlabel})", e, smiles=allenol_smiles(code)),
        participant("z_three", "product", f"(Z)-3{code}", e,
                    name=f"methyl 2-(1'-chlorovinyl)alk-2(Z)-enoate (Z)-3{code}, R = {rlabel}", smiles=diene_smiles(code)),
        common_participant("oxalyl", "(ClCO)2", "oxalyl chloride", SMILES["oxalyl_chloride"], e, 3),
        common_participant("dmso", "DMSO", "dimethyl sulfoxide", SMILES["dmso"], e, 6),
        participant("dcm", "solvent", "CH2Cl2", e, name="dichloromethane", smiles=SMILES["dcm"]),
    ]
    return record(
        f"table3_entry{idx}_z3{code}", "substrate_scope_entry", e, parts,
        [{"step_id": "activated_dmso_then_allenol", "participant_ids": [p["entity_id"] for p in parts],
          "conditions": [
              field("temperature_stage_1", {"number": -78, "unit": "°C"}, e),
              field("time_stage_1", {"minimum": 8, "maximum": 11, "unit": "min", "raw_text": "8-11 min"}, e),
              field("temperature_stage_2", {"number": -78, "unit": "°C"}, e),
              field("time_stage_2", {"minimum": 17, "maximum": 21, "unit": "min", "raw_text": "17-21 min"}, e),
              field("temperature_stage_3", "r.t.", e),
              field("time_stage_3", {"number": hours, "unit": "h"}, e),
              field("solvent", "CH2Cl2", e),
          ] + missing_conditions()}],
        [field("reported_yield_z3", {"number": y, "unit": "%"}, e, ["z_three"]), field("yield_measurement_basis", None, [])],
        unresolved=["Reaction scale, yield basis, atmosphere, workup, and purification are not reported.",
                    "Candidate connectivity and Z geometry remain unverified."])


for row in [(1, "a", 5, 83), (2, "b", 5, 76), (3, "c", 5, 85), (4, "d", 5, 76),
            (5, "e", 5, 78), (6, "g", 6, 80), (7, "h", 6, 64)]:
    records.append(table3_record(*row))


# Scheme 3 spans page-3 prose and the page-4 drawing.
e = unique(ev(3) + ev(4))
parts = [
    participant("e_one_i", "reactant", "E-1i", e,
                name="4-(methoxycarbonyl)-1(E)-phenyl-1,4,5-hexatrien-3-ol",
                smiles="C=C=C(C(=O)OC)C(O)C=Cc1ccccc1"),
    participant("ze_three_i", "product", "(Z,E)-3i", e,
                name="methyl 2-(1'-chlorovinyl)-5-phenylpenta-(2Z,4E)-dienoate",
                smiles="C=C(Cl)C(C(=O)OC)=CC=Cc1ccccc1"),
    common_participant("oxalyl", "(ClCO)2", "oxalyl chloride", SMILES["oxalyl_chloride"], e, 3),
    participant("dcm", "solvent", "CH2Cl2", e, name="dichloromethane", smiles=SMILES["dcm"]),
]
records.append(record(
    "scheme3_e1i_to_ze3i", "reported_experiment", e, parts,
    [{"step_id": "direct_oxalyl_chloride_reaction", "participant_ids": [p["entity_id"] for p in parts],
      "conditions": [field("temperature", "r.t.", e), field("time", {"number": 18.5, "unit": "h"}, e), field("solvent", "CH2Cl2", e)] + missing_conditions()}],
    [field("reported_yield_ze3i", {"number": 66, "unit": "%"}, e, ["ze_three_i"]),
     field("yield_measurement_basis", None, []),
     field("structure_assignment_method", "X-ray diffraction", e, ["ze_three_i"])],
    unresolved=["Reaction scale, yield basis, atmosphere, workup, and purification are not reported.",
                "Candidate connectivity and Z,E geometry remain unverified."]
))


def scheme4_failure(branch):
    e = ev(4)
    parts = [
        participant("one_j", "reactant", "1j", e,
                    name="1-(4'-chlorophenyl)-2-(ethoxycarbonyl)deca-2,3-dien-1-ol",
                    smiles="CCOC(=O)C(C(O)c1ccc(Cl)cc1)=C=C(CCCCCC)"),
        participant("expected", "product", "2j" if branch == "E" else "3j", e,
                    name="expected enyne 2j" if branch == "E" else "expected chlorodiene 3j"),
        common_participant("oxalyl", "(ClCO)2", "oxalyl chloride", SMILES["oxalyl_chloride"], e, 5 if branch == "E" else 3),
        participant("dcm", "solvent", "CH2Cl2", e, name="dichloromethane", smiles=SMILES["dcm"]),
    ]
    if branch == "E":
        parts.append(common_participant("et3n", "Et3N", "triethylamine", SMILES["triethylamine"], e, 5))
        cond = [field("temperature_stage_1", "reflux", e), field("time_stage_1", {"number": 6, "unit": "h"}, e),
                field("temperature_stage_2", "r.t.", e), field("time_stage_2", {"number": 6, "unit": "h"}, e),
                field("solvent", "CH2Cl2", e)]
        suffix = "scheme4_1j_failed_e2j_conditions"
    else:
        parts.append(common_participant("dmso", "DMSO", "dimethyl sulfoxide", SMILES["dmso"], e, 6))
        cond = [field("temperature_stage_1", {"number": -78, "unit": "°C"}, e), field("time_stage_1", {"number": 10, "unit": "min"}, e),
                field("temperature_stage_2", {"number": -78, "unit": "°C"}, e), field("time_stage_2", {"number": 20, "unit": "min"}, e),
                field("temperature_stage_3", "r.t.", e), field("time_stage_3", {"number": 5, "unit": "h"}, e),
                field("solvent", "CH2Cl2", e)]
        suffix = "scheme4_1j_failed_z3j_conditions"
    return record(
        suffix, "reported_experiment", e, parts,
        [{"step_id": "failed_standard_conditions", "participant_ids": [p["entity_id"] for p in parts], "conditions": cond + missing_conditions()}],
        [field("expected_product_formation", "failed to afford the corresponding product", e, ["expected"]),
         field("reported_yield", None, [])],
        unresolved=["The source does not quantify conversion, recovery, or alternative products.",
                    "Reaction scale, atmosphere, workup, and purification are not reported.",
                    "Candidate substrate connectivity and expected-product structure remain unverified."])


records.extend([scheme4_failure("E"), scheme4_failure("Z")])


# Scheme 5 is explicitly proposed mechanism.
e = ev(4)
parts = [
    participant("generic_1", "reactant", "allenol 1", e),
    participant("m1", "unspecified_agent", "M1", e, name="proposed oxalylated intermediate M1"),
    participant("m2", "unspecified_agent", "M2", e, name="proposed activated DMSO species M2"),
    participant("m3", "unspecified_agent", "M3", e, name="proposed sulfonium intermediate M3"),
    participant("generic_e2", "product", "(E)-2", e),
    participant("generic_z3", "product", "(Z)-3", e),
    common_participant("oxalyl", "(ClCO)2", "oxalyl chloride", SMILES["oxalyl_chloride"], e),
    common_participant("dmso", "DMSO", "dimethyl sulfoxide", SMILES["dmso"], e),
    common_participant("et3n", "Et3N", "triethylamine", SMILES["triethylamine"], e),
]
records.append(record(
    "scheme5_proposed_mechanism", "mechanism", e, parts,
    [
        {"step_id": "proposed_e2_path", "participant_ids": ["generic_1", "oxalyl", "m1", "et3n", "generic_e2"],
         "conditions": [field("operation", "formation of M1, allenyl-proton deprotonation, and elimination", e)]},
        {"step_id": "proposed_z3_path", "participant_ids": ["generic_1", "oxalyl", "dmso", "m2", "m3", "generic_z3"],
         "conditions": [field("operation", "formation of M2/M3 followed by chloride SN2'-type reaction", e)]},
    ],
    [],
    notes=["Scheme 5 is a possible mechanism proposed by the authors, not a set of isolated intermediates."],
    unresolved=["M1-M3 and generic R-group structures are proposed and remain unverified."]
))


assert len(records) == 30, len(records)
assert len({r["record_id"] for r in records}) == len(records)

out = RUN / "raw_model" / "records_pages_0001_0004.json"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")

# Coverage ledger: page regions cite their own original image evidence.
ids = [r["record_id"] for r in records]
by_suffix = {r["source_reaction_id"]: r["record_id"] for r in records}
coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1,
            "state": "attempted",
            "regions": [
                {"region": "title and graphical abstract", "finding": "Generic two-branch present-paper scope retained as one general scheme; yield ranges are scope claims, not a batch.", "evidence_ids": ev(1)},
                {"region": "lower-right opening Results prose", "finding": "Three outcomes for 1a correspond to Scheme 1 on page 2 and are linked to those optimization records rather than duplicated.", "evidence_ids": ev(1)},
                {"region": "introduction and references", "finding": "Citation-only prior methods and broad claims were not reconstructed as present-paper experiments.", "evidence_ids": ev(1)},
            ],
            "record_ids": [
                by_suffix["graphical_abstract_general_scope"],
                by_suffix["scheme1_entry1_swern_conditions"],
                by_suffix["scheme1_entry2_without_triethylamine"],
                by_suffix["scheme1_entry3_table1_entry1"],
            ],
            "unresolved": ["The page gives no experimental workup or purification details.", "Graphical-abstract R groups and structures are generic."],
        },
        {
            "page": 2,
            "state": "attempted",
            "regions": [
                {"region": "upper-left Scheme 1 and footnotes", "finding": "Three condition sets inspected; entry 3 is the same experiment as Table 1 entry 1. NMR yields and two starting-material recoveries were retained.", "evidence_ids": ev(2)},
                {"region": "upper-right Table 1 and footnote", "finding": "Six independent optimization rows extracted with two-stage temperature/time programs, base identity, two product yields, and NMR/internal-standard basis.", "evidence_ids": ev(2)},
                {"region": "remaining prose and references", "finding": "Narrative interpretation supports Table 1; citation-only chemistry was not expanded into records.", "evidence_ids": ev(2)},
            ],
            "record_ids": [
                by_suffix["scheme1_entry1_swern_conditions"], by_suffix["scheme1_entry2_without_triethylamine"],
                by_suffix["scheme1_entry3_table1_entry1"],
                *[by_suffix[f"table1_entry{i}"] for i in range(2, 7)],
            ],
            "unresolved": ["Atmosphere, workup, and purification are absent.", "The Table 1 experiments do not state reaction scale."],
        },
        {
            "page": 3,
            "state": "attempted",
            "regions": [
                {"region": "upper-left Scheme 2 and discussion", "finding": "DIBAL-H reduction of (E)-2a to (E)-4a extracted as one reported experiment; NOESY is retained as assignment evidence.", "evidence_ids": ev(3)},
                {"region": "left-center Table 2 and footnotes", "finding": "Nine independent enyne-scope rows extracted. Scale and 5-equivalent overrides were applied row-wise; the 12% NMR (Z)-3h side product stays in entry 9.", "evidence_ids": ev(3)},
                {"region": "right-center Table 3 and reaction header", "finding": "Seven independent chlorodiene-scope rows extracted with the staged -78 °C time ranges and row reaction times.", "evidence_ids": ev(3)},
                {"region": "upper-right Figure 1 and lower-right prose", "finding": "ORTEP structures support (E)-2e and (Z,E)-3i identity; Figure 1 is not an additional reaction. Scheme 3 outcome prose is linked across pages 3-4.", "evidence_ids": ev(3)},
            ],
            "record_ids": [
                by_suffix["scheme2_dibal_reduction_e2a_to_e4a"],
                *[by_suffix[f"table2_entry{i}_e2{code}"] for i, code in enumerate(["a", "b", "c", "d", "e", "e", "f", "g", "h"], 1)],
                *[by_suffix[f"table3_entry{i}_z3{code}"] for i, code in enumerate(["a", "b", "c", "d", "e", "g", "h"], 1)],
                by_suffix["scheme3_e1i_to_ze3i"],
            ],
            "unresolved": ["Tables 2 and 3 do not state main-product yield basis.", "Most scope rows omit scale, atmosphere, workup, and purification.", "Candidate connectivity and stereochemistry remain unverified."],
        },
        {
            "page": 4,
            "state": "attempted",
            "regions": [
                {"region": "upper-left Scheme 3", "finding": "Direct oxalyl-chloride reaction of E-1i to (Z,E)-3i extracted with 18.5 h, room temperature, and 66% yield; linked to page-3 prose/X-ray statement.", "evidence_ids": ev(4)},
                {"region": "middle-left Scheme 4", "finding": "Two failed standard-condition experiments for 1j were separated: expected 2j and expected 3j were not afforded.", "evidence_ids": ev(4)},
                {"region": "upper-right Scheme 5 and explanatory prose", "finding": "M1-M3 routes classified as a proposed mechanism, not isolated experimental stages.", "evidence_ids": ev(4)},
                {"region": "conclusion, SI notice, and references", "finding": "No new independent experiment. SI is advertised but no SI file is supplied or associated.", "evidence_ids": ev(4)},
            ],
            "record_ids": [
                by_suffix["scheme3_e1i_to_ze3i"], by_suffix["scheme4_1j_failed_e2j_conditions"],
                by_suffix["scheme4_1j_failed_z3j_conditions"], by_suffix["scheme5_proposed_mechanism"],
            ],
            "unresolved": ["Scheme 4 does not report conversion, recovery, or alternative products.", "SI association remains unestablished.", "Mechanistic intermediates and complex structures remain unverified."],
        },
    ],
}
cov = RUN / "coverage" / "pages_0001_0004.json"
cov.parent.mkdir(parents=True, exist_ok=True)
cov.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

# Mark exactly the covered page tasks attempted.
tasks_path = RUN / "tasks.json"
tasks = json.loads(tasks_path.read_text())
for task in tasks:
    if task["document_id"] == DOC and task["task_id"] in {f"{DOC}:page{i}:text" for i in range(1, 5)}:
        task["state"] = "attempted"
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"records": len(records), "raw": str(out), "coverage": str(cov)}, ensure_ascii=False))
