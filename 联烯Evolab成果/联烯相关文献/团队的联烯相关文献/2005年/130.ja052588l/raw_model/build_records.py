"""Build the raw, evidence-linked extraction for ja052588l pages 1--5."""
import json
from pathlib import Path

DOC = "doc_a4fc8c6aed2bb7b5"
OUT = Path(__file__).with_name("records_pages_0001_0005.json")


def ev(page, kinds=("text", "image")):
    return [f"{DOC}:page{page}:{kind}" for kind in kinds]


def fact(value, evidence=()):
    return {
        "value": value,
        "evidence_ids": list(evidence),
        "verification": "missing" if value is None else "unreviewed",
    }


def field(name, value, evidence=(), targets=None):
    item = {"name": name, "fact": fact(value, evidence)}
    if targets:
        item["target_entity_ids"] = targets
    return item


def participant(entity_id, role, label, name, evidence, smiles=None, amounts=()):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence),
        "smiles": fact(smiles, evidence) if smiles else fact(None),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": list(amounts),
    }


def amount(value, evidence):
    return field("amount", value, evidence)


def record(suffix, source_id, kind, evidence, participants, steps, outcomes,
           notes=(), unresolved=()):
    return {
        "record_id": f"{DOC}:{suffix}",
        "document_id": DOC,
        "source_reaction_id": source_id,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": list(dict.fromkeys(evidence)),
        "participants": participants,
        "steps": steps,
        "outcomes": outcomes,
        "notes": [fact(n, evidence) for n in notes],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": list(unresolved),
        },
    }


SMILES = {
    "1": "C=C=CCC(C(=O)OC)C(=O)OC",
    "2": "Ic1ccccc1",
    "3": "Cc1ccc(S(=O)(=O)N=Cc2ccccc2)cc1",
    "k2co3": "[K+].[K+].[O-]C([O-])=O",
    "thf": "C1CCOC1",
    "acn": "CC#N",
    "methanol": "CO",
    "water": "O",
    "argon": "[Ar]",
}


def common_inputs(evidence, include_imine=False, include_base=False):
    ps = [
        participant("allene_1", "reactant", "1", "2-(2,3-allenyl)malonate",
                    evidence, SMILES["1"], [amount({"number": 0.05, "unit": "mmol"}, evidence)]),
        participant("iodobenzene_2", "reactant", "2", "iodobenzene",
                    evidence, SMILES["2"], [amount({"number": 0.06, "unit": "mmol"}, evidence)]),
    ]
    if include_imine:
        ps.append(participant("imine_3", "reactant", "3", "N-tosyl benzaldimine",
                              evidence, SMILES["3"], [amount({"number": 0.06, "unit": "mmol"}, evidence)]))
    ps.append(participant("pd_pph3_4", "catalyst", "Pd(PPh3)4", "tetrakis(triphenylphosphine)palladium(0)",
                          evidence, None, [amount({"number": 0.0025, "unit": "mmol"}, evidence)]))
    if include_base:
        ps.append(participant("k2co3", "reagent", "K2CO3", "potassium carbonate",
                              evidence, SMILES["k2co3"], [amount({"number": 0.05, "unit": "mmol"}, evidence)]))
    ps.append(participant("thf", "solvent", "THF", "tetrahydrofuran", evidence, SMILES["thf"],
                          [field("volume", {"number": 6, "unit": "mL"}, evidence)]))
    return ps


def reaction_step(step_id, ids, evidence, time=None, temp={"number": 85, "unit": "°C"}):
    conditions = [field("temperature", temp, evidence), field("atmosphere", "nitrogen", evidence)]
    if time is not None:
        conditions.append(field("time", time, evidence))
    return {"step_id": step_id, "participant_ids": ids, "conditions": conditions}


def sampling_step(evidence):
    return {
        "step_id": "esi_sampling",
        "participant_ids": ["acetonitrile"],
        "conditions": [
            field("sample_volume", {"number": 5, "unit": "uL"}, evidence),
            field("dilution_volume", {"number": 100, "unit": "uL"}, evidence),
            field("operation", "diluted with acetonitrile and introduced by syringe pump at 10 µL min−1; CapExit 52.6 V", evidence),
        ],
    }


records = []

# Page 1, equation 1: explicitly identified in the prose as previously developed work (ref. 6).
e1 = ev(1)
lit_parts = [
    participant("allene_1", "reactant", "1", "2-(2,3-allenyl)malonate", e1, SMILES["1"]),
    participant("iodobenzene_2", "reactant", "2", "iodobenzene", e1, SMILES["2"]),
    participant("imine_3", "reactant", "3", "N-tosyl benzaldimine", e1, SMILES["3"]),
    participant("pd_pph3_4", "catalyst", "Pd(PPh3)4", "tetrakis(triphenylphosphine)palladium(0)", e1),
    participant("k2co3", "reagent", "K2CO3", "potassium carbonate", e1, SMILES["k2co3"]),
    participant("thf", "solvent", "THF", "tetrahydrofuran", e1, SMILES["thf"]),
    participant("pyrrolidine_4", "product", "4", "cis-pyrrolidine derivative", e1),
]
records.append(record(
    "literature_eq1", "eq_1", "literature_example", e1, lit_parts,
    [{"step_id": "reported_transformation", "participant_ids": [p["entity_id"] for p in lit_parts],
      "conditions": [field("temperature", {"number": 85, "unit": "°C"}, e1), field("solvent", "THF", e1)]}],
    [field("selectivity", "cis-pyrrolidine derivative", e1, ["pyrrolidine_4"]),
     field("yield", None, targets=["pyrrolidine_4"])],
    notes=["Equation 1 summarizes the authors' previously published transformation (reference 6), not a new preparative experiment in this paper."],
    unresolved=["Substrate amounts, reaction time, atmosphere, yield, workup and purification are not reported in equation 1.",
                "The stereochemically complete product SMILES was not assigned from the drawing by the machine extraction."],
))

# Page 2: oxidative-addition / method-establishment experiment.
e2 = ev(2)
parts = [
    participant("iodobenzene_2", "reactant", "2", "iodobenzene", e2, SMILES["2"],
                [amount({"number": 0.06, "unit": "mmol"}, e2)]),
    participant("pd_pph3_4", "catalyst", "Pd(PPh3)4", "tetrakis(triphenylphosphine)palladium(0)", e2, None,
                [amount({"number": 0.0025, "unit": "mmol"}, e2)]),
    participant("thf", "solvent", "THF", "tetrahydrofuran", e2, SMILES["thf"],
                [field("volume", {"number": 6, "unit": "mL"}, e2)]),
    participant("ion_5", "product", "5", "[PhPd(PPh3)2]+", e2),
    participant("acn_meoh", "solvent", "CH3CN/CH3OH (1:1 v/v)", "acetonitrile/methanol mixture", e2),
]
records.append(record(
    "oxidative_addition_probe_rt", "results_initial_probe", "reported_experiment", e2, parts,
    [reaction_step("reaction", ["iodobenzene_2", "pd_pph3_4", "thf"], e2,
                   {"number": 30, "unit": "min"}, "r.t."),
     {"step_id": "esi_sampling", "participant_ids": ["acn_meoh"], "conditions": [
         field("sample_volume", {"number": 5, "unit": "uL"}, e2),
         field("dilution_volume", {"number": 100, "unit": "uL"}, e2),
         field("operation", "diluted in CH3CN/CH3OH (1:1 v/v), introduced at 10 µL min−1, CapExit 52.6 V", e2),
     ]}],
    [field("detected_ion", "ion 5, principal m/z 707.1263", e2, ["ion_5"]), field("yield", None, targets=["ion_5"])],
    notes=["Ion 5 remained visible when the reaction temperature was subsequently raised to 85 °C; CapExit values 45–65 V gave no obvious difference."],
    unresolved=["This is a mechanistic ESI-MS probe; no isolated yield, workup or purification is reported.",
                "The duration after raising the mixture to 85 °C is not stated."],
))

# Numbered experiments (1) and (2) on page 2.
for suffix, source, with_imine, start, end in [
    ("mixture_1_allene_iodobenzene_pd", "results_experiment_1", False, None, None),
    ("mixture_2_no_base", "results_experiment_2", True, {"number": 30, "unit": "min"}, {"number": 2, "unit": "h"}),
]:
    ps = common_inputs(e2, include_imine=with_imine)
    ps.append(participant("ion_5", "product", "5", "[PhPd(PPh3)2]+", e2))
    ps.append(participant("ion_7", "product", "7", "π-allyl palladium intermediate", e2))
    ps.append(participant("acetonitrile", "solvent", "CH3CN", "acetonitrile", e2, SMILES["acn"]))
    ids = [p["entity_id"] for p in ps if p["entity_id"] not in {"ion_5", "ion_7", "acetonitrile"}]
    cond = [field("temperature", {"number": 85, "unit": "°C"}, e2), field("atmosphere", "nitrogen", e2)]
    if start:
        cond += [field("sampling_time_start", start, e2), field("sampling_time_end", end, e2)]
    records.append(record(
        suffix, source, "reported_experiment", e2, ps,
        [{"step_id": "reaction", "participant_ids": ids, "conditions": cond}, sampling_step(e2)],
        [field("detected_species", ["ion 5", "ion 7"], e2, ["ion_5", "ion_7"]), field("yield", None)],
        notes=["Only ions 5 and 7 were reported for the sampled mixture."] if with_imine else ["Ions 5 and 7 were detected after the standard ESI-MS sample treatment."],
        unresolved=["No isolated synthetic product, yield, workup or purification is reported."] +
                   (["The reaction time before sampling is not stated."] if not start else []),
    ))


# Full five-component time course. Page 3 is additional visual evidence for 5, 20 and 40 min.
timepoints = [
    ("5min", {"number": 5, "unit": "min"}, ["ion 5", "ion 6"], 3,
     "ions 5 and 6 detected"),
    ("20min", {"number": 20, "unit": "min"}, ["ion 5", "ion 6", "ion 7"], 3,
     "ions 5–7 detected"),
    ("40min", {"number": 40, "unit": "min"}, ["ion 5", "ion 6", "ion 7", "ion 8", "ion 9", "ion 10", "ion 11", "ion 12"], 3,
     "ions 5–12 reported; signals 9–12 started to appear"),
    ("5h", {"number": 5, "unit": "h"}, ["ion 5 weaker", "ion 6 disappeared"], 2,
     "ion 5 became weaker and ion 6 disappeared"),
    ("15h", {"number": 15, "unit": "h"}, ["ion 5 disappeared", "ion 8 disappeared", "ion 9 disappeared"], 2,
     "ions 5, 8 and 9 disappeared"),
    ("24h", {"number": 24, "unit": "h"}, ["ion 7 very weak"], 2,
     "ion 7 became very weak"),
    ("36h", {"number": 36, "unit": "h"}, ["ion 7 disappeared", "ions 10–12 very strong"], 2,
     "ion 7 disappeared; only very strong signals of ions 10–12 were detected"),
]
for suffix, duration, signals, max_page, result_note in timepoints:
    evidence = e2 + (ev(3) if max_page == 3 else [])
    ps = common_inputs(evidence, include_imine=True, include_base=True)
    ps.append(participant("pyrrolidine_4", "product", "4", "cis-pyrrolidine derivative", evidence))
    ps.append(participant("acetonitrile", "solvent", "CH3CN", "acetonitrile", evidence, SMILES["acn"]))
    ids = [p["entity_id"] for p in ps if p["entity_id"] not in {"pyrrolidine_4", "acetonitrile"}]
    outcomes = [field("ESI_MS_signal_result", signals, evidence)]
    if suffix in {"40min", "36h"}:
        outcomes.append(field("product_derived_ion_signal", "ions 11 and 12 detected" if suffix == "40min" else "ions 11 and 12 very strong", evidence, ["pyrrolidine_4"]))
    outcomes.append(field("yield", None, targets=["pyrrolidine_4"]))
    records.append(record(
        f"full_mixture_{suffix}", f"results_experiment_3_{suffix}", "reported_experiment", evidence, ps,
        [reaction_step("reaction", ids, evidence, duration), sampling_step(evidence)], outcomes,
        notes=[result_note, "Ion 11 is assigned as a potassium-bound species formed from product 4; ion 12 is assigned as the K+-bound dimer of 4." if suffix in {"40min", "36h"} else "No synthetic yield is stated for this time point."],
        unresolved=["No isolated yield, workup or purification is reported.",
                    "Absence of unlisted ions at this time point was not inferred unless the text explicitly says disappeared or only."],
    ))


# Individual-component ESI controls: keep the two sample-preparation conditions separate.
control_specs = [
    ("allene_1", "1", "2-(2,3-allenyl)malonate", SMILES["1"]),
    ("iodobenzene_2", "2", "iodobenzene", SMILES["2"]),
    ("imine_3", "3", "N-tosyl benzaldimine", SMILES["3"]),
]
for ent, label, name, smiles in control_specs:
    ps = [participant(ent, "reactant", label, name, e2, smiles),
          participant("acetonitrile", "solvent", "CH3CN", "acetonitrile", e2, SMILES["acn"])]
    records.append(record(
        f"control_{label}_standard_esi", f"component_{label}_standard_esi", "reported_experiment", e2, ps,
        [{"step_id": "standard_esi_sample_treatment", "participant_ids": [ent, "acetonitrile"], "conditions": [field("operation", "standard ESI-MS detection procedure", e2)]}],
        [field("ESI_MS_result", "no MS data observed", e2)],
        notes=["The paper reports no MS data for reactant %s under the standard detection procedure." % label],
        unresolved=["Component concentration and amount are not stated; this is an analytical control, not a preparative reaction."],
    ))

modified_results = {
    "1": "ion 9 detected (derived from reactant 1)",
    "2": "not detected in any form",
    "3": "ion 10 detected (derived from reactant 3)",
}
for ent, label, name, smiles in control_specs:
    ps = [participant(ent, "reactant", label, name, e2, smiles),
          participant("acetonitrile", "solvent", "CH3CN", "acetonitrile", e2, SMILES["acn"]),
          participant("k2co3", "reagent", "K2CO3", "potassium carbonate", e2, SMILES["k2co3"])]
    records.append(record(
        f"control_{label}_k2co3_saturated_esi", f"component_{label}_k2co3_saturated_esi", "reported_experiment", e2, ps,
        [{"step_id": "modified_esi_sample_treatment", "participant_ids": [ent, "acetonitrile", "k2co3"],
          "conditions": [field("operation", "sample prepared using acetonitrile saturated with K2CO3", e2)]}],
        [field("ESI_MS_result", modified_results[label], e2)],
        notes=["Individual-component ESI-FTMS control with K2CO3-saturated acetonitrile."],
        unresolved=["Component amount, concentration and exact sampling time are not stated; this is an analytical control."],
    ))


# Page 4 MS/MS and MS/MS/MS fragmentation experiments; accurate masses are corroborated by Table 1 on page 5.
e45 = ev(2) + ev(4) + ev(5)
frag_specs = [
    ("msms_ion5_to_5a", "Figure_2a", "5", "[PhPd(PPh3)2]+", [("5A", "C24H20P+ fragment", "m/z 339.1301")], "SORI-CAD MS/MS with argon"),
    ("msms_ion6_to_5_5a", "Figure_2b", "6", "acetonitrile adduct ion 6", [("5", "[PhPd(PPh3)2]+", "m/z 707.1263"), ("5A", "C24H20P+ fragment", "m/z 339.1301")], "SORI-CAD MS/MS with argon; loss of acetonitrile is reported as the first step"),
    ("msms_ion7_to_7a", "Figure_2c", "7", "π-allyl palladium intermediate", [("7A", "C33H32O4PPd+ fragment", "m/z 629.1088")], "SORI-CAD MS/MS with argon; loss of one PPh3 ligand"),
    ("ms3_ion5a_to_5b_5c", "Figure_3", "5A", "C24H20P+ fragment", [("5B", "C18H14P+ fragment", "m/z 261.0831"), ("5C", "C12H8P+ fragment", "m/z 183.0360")], "MS/MS/MS with argon; loss of one or two benzene molecules"),
]
for suffix, source, parent_label, parent_name, products, operation in frag_specs:
    parent_id = f"ion_{parent_label.lower()}"
    ps = [participant(parent_id, "reactant", parent_label, parent_name, e45),
          participant("argon", "reagent", "Ar", "argon", e45, SMILES["argon"])]
    target_ids = []
    for plabel, pname, mz in products:
        pid = f"ion_{plabel.lower()}"
        target_ids.append(pid)
        ps.append(participant(pid, "product", plabel, pname, e45))
    records.append(record(
        suffix, source, "reported_experiment", e45, ps,
        [{"step_id": "collision_induced_fragmentation", "participant_ids": [parent_id, "argon"] + target_ids,
          "conditions": [field("operation", operation, e45)]}],
        [field("fragment_ion", mz, e45, [f"ion_{plabel.lower()}"]) for plabel, _, mz in products] + [field("yield", None)],
        notes=[operation],
        unresolved=["Collision energy and fragment intensities are not stated in the article text; no synthetic yield applies."],
    ))


# Page 5 Scheme 1: proposed mechanism, not a separately performed reaction sequence.
e_mech = ev(4) + ev(5)
mech_parts = [
    participant("allene_1", "reactant", "1", "2-(2,3-allenyl)malonate", e_mech, SMILES["1"]),
    participant("iodobenzene_2", "reactant", "2", "iodobenzene", e_mech, SMILES["2"]),
    participant("imine_3", "reactant", "3", "N-tosyl benzaldimine", e_mech, SMILES["3"]),
    participant("k2co3", "reagent", "K2CO3", "potassium carbonate", e_mech, SMILES["k2co3"]),
    participant("pd_pph3_4", "catalyst", "Pd(PPh3)4", "tetrakis(triphenylphosphine)palladium(0)", e_mech),
    participant("pd_pph3_2", "catalyst", "Pd(PPh3)2", "bis(triphenylphosphine)palladium(0)", e_mech),
    participant("ion_5", "product", "5", "oxidative-addition palladium intermediate", e_mech),
    participant("ion_7", "product", "7", "π-allyl palladium intermediate", e_mech),
    participant("ion_8", "product", "8", "post-imine-addition palladium intermediate", e_mech),
    participant("pyrrolidine_4", "product", "4", "cis-pyrrolidine derivative", e_mech),
]
records.append(record(
    "proposed_mechanism_scheme1", "Scheme_1", "mechanism", e_mech, mech_parts,
    [
        {"step_id": "catalyst_ligand_dissociation", "participant_ids": ["pd_pph3_4", "pd_pph3_2"], "conditions": [field("operation", "dissociation of two PPh3 ligands", e_mech)]},
        {"step_id": "oxidative_addition", "participant_ids": ["pd_pph3_2", "iodobenzene_2", "ion_5"], "conditions": [field("operation", "proposed oxidative addition of PhI to Pd(PPh3)2", e_mech)]},
        {"step_id": "carbopalladation", "participant_ids": ["ion_5", "allene_1", "ion_7"], "conditions": [field("operation", "proposed carbopalladation", e_mech)]},
        {"step_id": "deprotonation_and_imine_addition", "participant_ids": ["ion_7", "k2co3", "imine_3", "ion_8"], "conditions": [field("operation", "proposed malonate deprotonation followed by addition to imine 3", e_mech)]},
        {"step_id": "intramolecular_allylic_amination", "participant_ids": ["ion_8", "pyrrolidine_4", "pd_pph3_2"], "conditions": [field("operation", "proposed intramolecular allylic amination with catalyst regeneration", e_mech)]},
    ],
    [field("mechanistic_conclusion", "carbopalladation pathway proposed; azapalladation–reductive-elimination pathway excluded by the authors", e_mech), field("yield", None, targets=["pyrrolidine_4"])],
    notes=["Scheme 1 is a proposed mechanism based on ESI-FTMS observations, not a standalone preparative experiment."],
    unresolved=["No kinetic constants, step-specific conditions or step-specific yields are reported.",
                "Organopalladium structures and the stereochemically complete product structure were not encoded as machine SMILES."],
))


OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"output": str(OUT), "records": len(records)}, ensure_ascii=False))
