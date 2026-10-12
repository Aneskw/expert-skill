#!/usr/bin/env python3
"""Build evidence-linked machine records for PDF pages 1-3."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DATASET = ROOT / "runs/current/dataset.json"
OUT = ROOT / "runs/current/raw_model/extracted_records_pages_0001_0003.json"
DOC = "doc_137fed090ec84c10"


def fact(value, evidence):
    return {
        "value": value,
        "evidence_ids": list(evidence) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def field(name, value, evidence, targets=None):
    item = {"name": name, "fact": fact(value, evidence)}
    if targets:
        item["target_entity_ids"] = list(targets)
    return item


def qty(number, unit, raw_text=None, **extra):
    value = {"number": number, "unit": unit}
    if raw_text is not None:
        value["raw_text"] = raw_text
    value.update(extra)
    return value


def rng(minimum, maximum, unit, raw_text):
    return {"minimum": minimum, "maximum": maximum, "unit": unit, "raw_text": raw_text}


def participant(entity_id, role, label, name, smiles, evidence, amounts=()):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence),
        "smiles": fact(smiles, evidence),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": list(amounts),
    }


def record(suffix, kind, evidence, participants, steps, outcomes=(), notes=(), unresolved=()):
    return {
        "record_id": f"{DOC}:{suffix}",
        "document_id": DOC,
        "source_reaction_id": suffix,
        "record_kind": kind,
        "status": "needs_review",
        "completeness": "partial",
        "evidence_ids": list(dict.fromkeys(evidence)),
        "participants": participants,
        "steps": steps,
        "outcomes": list(outcomes),
        "notes": [fact(value, ev) for value, ev in notes],
        "review": {
            "method": "model",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": list(unresolved),
        },
    }


P1T = [f"{DOC}:page1:text"]
P1I = [f"{DOC}:page1:image"]
P2T = [f"{DOC}:page2:text"]
P2I = [f"{DOC}:page2:image"]
P3T = [f"{DOC}:page3:text"]
P3I = [f"{DOC}:page3:image"]
P1 = P1T + P1I
P2 = P2T + P2I
P3 = P3T + P3I


def generic_scheme_records():
    recs = []
    common_unresolved = [
        "Generic or drawn structures contain an R group; complete structures and SMILES are intentionally unresolved.",
        "The scheme is presented as cited starting-material preparation, not as a fully described target-scope experiment.",
        "Reagent quantities and product yields are not reported for this arrow.",
    ]

    def gp(eid, role, label, name=None):
        return participant(eid, role, label, name, None, P1I)

    # Scheme 1: five visually distinct arrows.
    ps = [
        gp("s1a_start", "reactant", "Scheme 1 terminal alkynol"),
        gp("s1a_linh2", "reagent", "LiNH2", "lithium amide"),
        gp("s1a_nh3", "solvent", "NH3", "ammonia"),
        gp("s1a_rx", "reagent", "RX", "alkyl halide (generic)"),
        gp("s1a_product", "product", "Scheme 1 R-substituted alkynol"),
    ]
    recs.append(record("scheme1_arrow1_alkynol_alkylation", "literature_example", P1, ps,
        [{"step_id": "alkynol_alkylation", "participant_ids": [p["entity_id"] for p in ps], "conditions": []}],
        unresolved=common_unresolved))

    ps = [gp("s1b_start", "reactant", "Scheme 1 R-substituted alkynol"),
          gp("s1b_lialh4", "reagent", "LiAlH4", "lithium aluminium hydride"),
          gp("s1b_thf", "solvent", "THF", "tetrahydrofuran"),
          gp("s1b_product", "product", "Scheme 1 allylic alcohol")]
    recs.append(record("scheme1_arrow2_alkyne_reduction", "literature_example", P1, ps,
        [{"step_id": "alkyne_reduction", "participant_ids": [p["entity_id"] for p in ps],
          "conditions": [field("temperature", "reflux", P1I)]}], unresolved=common_unresolved))

    ps = [gp("s1c_start", "reactant", "Scheme 1 allylic alcohol"),
          gp("s1c_ti", "unspecified_agent", "Ti(O-i-Pr)4", "titanium tetraisopropoxide"),
          gp("s1c_tartrate", "unspecified_agent", "tartrate"),
          gp("s1c_ms", "reagent", "4A MS", "4 Å molecular sieves"),
          gp("s1c_tbhp", "reagent", "TBHP", "tert-butyl hydroperoxide"),
          gp("s1c_dcm", "solvent", "CH2Cl2", "dichloromethane"),
          gp("s1c_product", "product", "Scheme 1 epoxy alcohol")]
    recs.append(record("scheme1_arrow3_asymmetric_epoxidation", "literature_example", P1, ps,
        [{"step_id": "asymmetric_epoxidation", "participant_ids": [p["entity_id"] for p in ps],
          "conditions": [field("temperature", qty(-20, "°C"), P1I),
                         field("time", rng(3.5, 5, "h", "3.5–5 h"), P1I)]}], unresolved=common_unresolved))

    ps = [gp("s1d_start", "reactant", "Scheme 1 epoxy alcohol"),
          gp("s1d_pph3", "reagent", "PPh3", "triphenylphosphine"),
          gp("s1d_ccl4", "reagent", "CCl4", "carbon tetrachloride"),
          gp("s1d_product", "product", "Scheme 1 chloromethyl epoxide")]
    recs.append(record("scheme1_arrow4_epoxy_alcohol_chlorination", "literature_example", P1, ps,
        [{"step_id": "chlorination", "participant_ids": [p["entity_id"] for p in ps],
          "conditions": [field("temperature", "reflux", P1I), field("time", qty(2, "h"), P1I)]}],
        unresolved=common_unresolved))

    ps = [gp("s1e_start", "reactant", "Scheme 1 chloromethyl epoxide"),
          gp("s1e_nbuli", "reagent", "n-BuLi", "n-butyllithium"),
          gp("s1e_thf", "solvent", "THF", "tetrahydrofuran"),
          gp("s1e_product", "product", "Scheme 1 optically active terminal propargylic alcohol")]
    recs.append(record("scheme1_arrow5_epoxide_to_propargylic_alcohol", "literature_example", P1, ps,
        [{"step_id": "epoxide_to_propargylic_alcohol", "participant_ids": [p["entity_id"] for p in ps],
          "conditions": [field("temperature", qty(-35, "°C"), P1I)]}], unresolved=common_unresolved))

    # Scheme 2: three visually distinct arrows, with fully specified n-octyl substrate skeletons.
    ps = [
        participant("s2a_aldehyde", "reactant", "n-C8H17CHO", "nonanal", "CCCCCCCCC=O", P1I),
        participant("s2a_grignard", "reagent", "HC≡CMgBr", "ethynylmagnesium bromide", "C#[C-].[Mg+2].[Br-]", P1I),
        participant("s2a_product", "product", "Scheme 2 propargylic alcohol", "undec-1-yn-3-ol", "C#CC(O)CCCCCCCC", P1I),
    ]
    recs.append(record("scheme2_arrow1_grignard_addition", "literature_example", P1, ps,
        [{"step_id": "grignard_addition", "participant_ids": [p["entity_id"] for p in ps], "conditions": []}],
        unresolved=["Reagent quantities, temperature, time, stereochemical composition, workup, and yield are not reported for this arrow.",
                    "This starting-material preparation is associated in the prose with cited methods rather than a full experimental procedure."]))

    ps = [
        participant("s2b_start", "reactant", "Scheme 2 propargylic alcohol", "undec-1-yn-3-ol", "C#CC(O)CCCCCCCC", P1I),
        participant("s2b_cro3", "reagent", "CrO3", "chromium trioxide", "O=[Cr](=O)=O", P1I),
        participant("s2b_h2so4", "reagent", "H2SO4", "sulfuric acid", "OS(=O)(=O)O", P1I),
        participant("s2b_acetone", "solvent", "acetone", "acetone", "CC(C)=O", P1I),
        participant("s2b_product", "product", "Scheme 2 ynone", "undec-1-yn-3-one", "C#CC(=O)CCCCCCCC", P1I),
    ]
    recs.append(record("scheme2_arrow2_propargylic_alcohol_oxidation", "literature_example", P1, ps,
        [{"step_id": "oxidation", "participant_ids": [p["entity_id"] for p in ps],
          "conditions": [field("temperature", qty(0, "°C"), P1I)]}],
        unresolved=["Reagent quantities, time, workup, and yield are not reported for this arrow.",
                    "This starting-material preparation is associated in the prose with cited methods rather than a full experimental procedure."]))

    ps = [
        participant("s2c_start", "reactant", "Scheme 2 ynone", "undec-1-yn-3-one", "C#CC(=O)CCCCCCCC", P1I),
        participant("s2c_binol", "unspecified_agent", "BINOL", "1,1'-bi-2-naphthol", None, P1I),
        participant("s2c_lialh4", "reagent", "LiAlH4", "lithium aluminium hydride", "[Li+].[AlH4-]", P1I),
        participant("s2c_meoh", "reagent", "MeOH", "methanol", "CO", P1I),
        participant("s2c_thf", "solvent", "THF", "tetrahydrofuran", "C1CCOC1", P1I),
        participant("s2c_product", "product", "Scheme 2 optically active propargylic alcohol", "undec-1-yn-3-ol", "C#CC(O)CCCCCCCC", P1I),
    ]
    recs.append(record("scheme2_arrow3_enantioselective_reduction", "literature_example", P1, ps,
        [{"step_id": "enantioselective_reduction", "participant_ids": [p["entity_id"] for p in ps],
          "conditions": [field("temperature_program", rng(-100, -78, "°C", "-100→-78 °C"), P1I)]}],
        unresolved=["Reagent quantities, time, absolute configuration, workup, yield, and ee are not reported for this arrow.",
                    "This starting-material preparation is associated in the prose with cited methods rather than a full experimental procedure."]))
    return recs


def scheme3_records():
    recs = []
    substrate_smiles = "C[Si](C)(C)C#CC(=O)CCCCCCCC"
    alcohol_smiles = "C[Si](C)(C)C#CC(O)CCCCCCCC"
    final_smiles = "C#CC(O)CCCCCCCC"
    branches = [
        ("s", "(S,S)-complex", "(S,S)-Ru complex", 100),
        ("r", "(R,R)-complex", "(R,R)-Ru complex", 97),
    ]
    for key, catalyst_label, catalyst_name, reduction_yield in branches:
        ev = P1T + P2
        ps = [
            participant(f"sch3_{key}_ketone", "reactant", "TMS ynone", "1-trimethylsilylundec-1-yn-3-one", substrate_smiles, P2I),
            participant(f"sch3_{key}_cat", "catalyst", catalyst_label, catalyst_name, None, P2I,
                        [field("catalyst_loading", qty(2, "mol%"), P2I)]),
            participant(f"sch3_{key}_iproh", "solvent", "i-PrOH", "2-propanol", "CC(C)O", P2I),
            participant(f"sch3_{key}_tms_alcohol", "product", f"{key.upper()}-configured TMS propargylic alcohol", None, alcohol_smiles, P2I),
        ]
        target = f"sch3_{key}_tms_alcohol"
        recs.append(record(f"scheme3_{key}_asymmetric_reduction", "reported_experiment", ev, ps,
            [{"step_id": "asymmetric_reduction", "participant_ids": [p["entity_id"] for p in ps], "conditions": []}],
            outcomes=[field("yield", qty(reduction_yield, "%"), P2I, [target]),
                      field("yield_measurement_basis", "not stated", P2I, [target])],
            unresolved=["Substrate/reagent masses, reaction time and temperature, workup, and yield measurement basis are not reported.",
                        "The candidate product SMILES does not encode the source-drawn absolute stereochemistry and is not structure-verified."]))

        ps = [
            participant(f"sch3_{key}_tms_alcohol_in", "reactant", f"{key.upper()}-configured TMS propargylic alcohol", None, alcohol_smiles, P2I),
            participant(f"sch3_{key}_k2co3", "reagent", "K2CO3", "potassium carbonate", "[K+].[K+].[O-]C([O-])=O", P2I),
            participant(f"sch3_{key}_meoh", "solvent", "MeOH", "methanol", "CO", P2I),
            participant(f"sch3_{key}_water", "solvent", "H2O", "water", "O", P2I),
            participant(f"sch3_{key}_final", "product", f"({key.upper()})-1c", f"({key.upper()})-undec-1-yn-3-ol", final_smiles, P2I),
        ]
        target = f"sch3_{key}_final"
        recs.append(record(f"scheme3_{key}_desilylation", "reported_experiment", ev, ps,
            [{"step_id": "desilylation", "participant_ids": [p["entity_id"] for p in ps],
              "conditions": [field("solvent_ratio", "MeOH/H2O (15:1)", P2I)]}],
            outcomes=[field("yield", qty(99, "%"), P2I, [target]),
                      field("product_ee", qty(98, "%"), P2I, [target]),
                      field("yield_measurement_basis", "not stated", P2I, [target])],
            unresolved=["Substrate/reagent quantities, reaction time and temperature, workup, and yield measurement basis are not reported.",
                        "The candidate product SMILES does not encode absolute stereochemistry and is not structure-verified."]))
    return recs


def mass_amounts(evidence, mass=None, mmol=None, volume=None, ee=None):
    values = []
    if mass is not None:
        values.append(field("mass", qty(mass, "mg"), evidence))
    if mmol is not None:
        values.append(field("amount", qty(mmol, "mmol"), evidence))
    if volume is not None:
        values.append(field("volume", qty(volume, "mL"), evidence))
    if ee is not None:
        values.append(field("starting_material_ee", qty(ee, "%"), evidence))
    return values


def homologation_records():
    rows = [
        # suffix, cfg, key, substrate name, substrate SMILES, product name, product SMILES,
        # CuBr mg/mmol, PFA mg/mmol, amine mg/mmol/mL, substrate mg/mmol/ee, dioxane mL,
        # product mg/yield/ee, rotation, detailed page evidence
        ("table1_entry1_s_2a", "S", "a", "(S)-hept-1-yn-3-ol", "C#CC(O)CCCC", "(S)-octa-1,2-dien-4-ol", "C=C=CC(O)CCCC",
         96, .67, 98, 3.3, 250, 2.5, .35, 221, 2.0, 80, 3.5, 196, 79, 80, "−17.8 (c 1.00, MeOH)", P2),
        ("table1_entry2_s_2b", "S", "b", "(S)-dec-1-yn-3-ol", "C#CC(O)CCCCCCC", "(S)-undeca-1,2-dien-4-ol", "C=C=CC(O)CCCCCCC",
         142, .99, 144, 4.8, 364, 3.6, .51, 462, 3.0, 92, 3.5, 395, 79, 92, "−16.5 (c 0.95, MeOH)", P3),
        ("table1_entry3_s_2c", "S", "c", "(S)-undec-1-yn-3-ol", "C#CC(O)CCCCCCCC", "(S)-dodeca-1,2-dien-4-ol", "C=C=CC(O)CCCCCCCC",
         94, .66, 96, 3.2, 242, 2.4, .34, 336, 2.0, 96, 3.0, 262, 72, 95, "−19.6 (c 0.95, MeOH)", P3),
        ("table1_entry4_s_2d", "S", "d", "(S)-1-phenylprop-2-yn-1-ol", "C#CC(O)c1ccccc1", "(S)-1-phenylbuta-2,3-dien-1-ol", "C=C=CC(O)c1ccccc1",
         94, .66, 96, 3.2, 242, 2.4, .34, 264, 2.0, 96, 3.0, 225, 77, 96, "−130.6 (c 0.95, MeOH)", P3),
        ("table2_entry1_r_2a", "R", "a", "(R)-hept-1-yn-3-ol", "C#CC(O)CCCC", "(R)-octa-1,2-dien-4-ol", "C=C=CC(O)CCCC",
         142, .99, 144, 4.8, 364, 3.6, .51, 336, 3.0, 97, 4.0, 242, 64, 97, "+22.8 (c 1.05, MeOH)", P2),
        ("table2_entry2_r_2b", "R", "b", "(R)-dec-1-yn-3-ol", "C#CC(O)CCCCCCC", "(R)-undeca-1,2-dien-4-ol", "C=C=CC(O)CCCCCCC",
         94, .66, 96, 3.2, 242, 2.4, .34, 308, 2.0, 89, 3.0, 234, 70, 89, "+18.9 (c 0.95, MeOH)", P2 + P3),
        ("table2_entry3_r_2c_94ee", "R", "c", "(R)-undec-1-yn-3-ol", "C#CC(O)CCCCCCCC", "(R)-dodeca-1,2-dien-4-ol", "C=C=CC(O)CCCCCCCC",
         94, .66, 96, 3.2, 242, 2.4, .34, 331, 2.0, 94, 3.0, 248, 69, 97, "+15.3 (c 1.05, MeOH)", P3),
        ("table2_entry4_r_2d", "R", "d", "(R)-1-phenylprop-2-yn-1-ol", "C#CC(O)c1ccccc1", "(R)-1-phenylbuta-2,3-dien-1-ol", "C=C=CC(O)c1ccccc1",
         94, .66, 96, 3.2, 242, 2.4, .34, 264, 2.0, 97, 3.0, 182, 69, 97, "+121.4 (c 1.10, MeOH)", P3),
        ("table2_entry5_r_2c_98ee", "R", "c", "(R)-undec-1-yn-3-ol", "C#CC(O)CCCCCCCC", "(R)-dodeca-1,2-dien-4-ol", "C=C=CC(O)CCCCCCCC",
         94, .66, 96, 3.2, 242, 2.4, .34, 332, 2.0, 98, 3.0, 256, 71, 98, "+20.3 (c 1.30, MeOH)", P3),
    ]
    recs = []
    for row in rows:
        (suffix, cfg, key, sub_name, sub_smiles, prod_name, prod_smiles,
         cu_mg, cu_mmol, pf_mg, pf_mmol, am_mg, am_mmol, am_ml,
         sub_mg, sub_mmol, sub_ee, diox_ml, prod_mg, yield_pct, prod_ee,
         rotation, detail_ev) = row
        ev = list(dict.fromkeys(P1T + P2 + detail_ev))
        pfx = suffix
        participants = [
            participant(f"{pfx}_substrate", "reactant", f"({cfg})-1{key}", sub_name, sub_smiles, detail_ev,
                        mass_amounts(detail_ev, sub_mg, sub_mmol, ee=sub_ee)),
            participant(f"{pfx}_cubr", "reagent", "CuBr", "copper(I) bromide", "[Cu]Br", detail_ev,
                        mass_amounts(detail_ev, cu_mg, cu_mmol)),
            participant(f"{pfx}_pfa", "reagent", "(HCHO)n", "paraformaldehyde", None, detail_ev,
                        mass_amounts(detail_ev, pf_mg, pf_mmol)),
            participant(f"{pfx}_amine", "reagent", "i-Pr2NH", "diisopropylamine", "CC(C)NC(C)C", detail_ev,
                        mass_amounts(detail_ev, am_mg, am_mmol, am_ml)),
            participant(f"{pfx}_dioxane", "solvent", "1,4-dioxane", "1,4-dioxane", "O1CCOCC1", detail_ev,
                        mass_amounts(detail_ev, volume=diox_ml)),
            participant(f"{pfx}_product", "product", f"({cfg})-2{key}", prod_name, prod_smiles, detail_ev,
                        mass_amounts(detail_ev, prod_mg)),
        ]
        target = f"{pfx}_product"
        conditions = [
            field("atmosphere", "argon", P1T),
            field("temperature", qty(120, "°C"), P2T),
            field("time", qty(2, "h"), P2T),
            field("operation", "heated; cooled after reaction", P2T),
            field("workup", "mixture evaporated after cooling", P2T),
            field("purification", "silica gel chromatography; petroleum ether–EtOAc 10:1", P2T),
        ]
        notes = []
        unresolved = [
            "Candidate substrate/product SMILES omit absolute stereochemical encoding and are not structure-verified.",
            "No Supporting Information was explicitly supplied or associated; unreported experimental details remain missing.",
        ]
        if suffix == "table1_entry4_s_2d":
            notes.append(("The paragraph prints '225 mg (77 mg, 96% ee)', while Table 1 reports 77% yield; the structured yield follows the table and the discrepancy remains unresolved.", P2I + P3T))
            unresolved.append("Resolve the apparent '77 mg' versus 77% typographical discrepancy in the (S)-2d paragraph.")
        if suffix == "table2_entry2_r_2b":
            notes.append(("The paragraph heading visually reads '(R)-1,2-Undeca-1,2-dien-4-ol'; the table label and drawn homologation identify (R)-2b, retained without silently editing the printed heading.", P2I + P3I))
            unresolved.append("The printed (R)-2b heading contains an apparent duplicated locant and has not been silently corrected as a source fact.")
        if suffix == "table2_entry5_r_2c_98ee":
            notes.append(("The prose states that the same experiment was carried out with the 98% ee substrate; reagent quantities and conditions are inherited from the immediately preceding (R)-2c experiment.", P3T))
        recs.append(record(suffix, "substrate_scope_entry", ev, participants,
            [{"step_id": "cubr_mediated_homologation", "participant_ids": [p["entity_id"] for p in participants], "conditions": conditions}],
            outcomes=[field("yield", qty(yield_pct, "%"), detail_ev, [target]),
                      field("yield_measurement_basis", "isolated after silica gel chromatography", P2T, [target]),
                      field("product_ee", qty(prod_ee, "%"), detail_ev, [target]),
                      field("specific_rotation", rotation, P2I, [target])],
            notes=notes, unresolved=unresolved))
    return recs


def main():
    dataset = json.loads(DATASET.read_text())
    existing = {r["record_id"] for r in dataset["experiments"]}
    records = generic_scheme_records() + scheme3_records() + homologation_records()
    duplicate = existing.intersection(r["record_id"] for r in records)
    if duplicate:
        raise SystemExit(f"Refusing to overwrite existing records: {sorted(duplicate)}")
    if len(records) != len({r["record_id"] for r in records}):
        raise SystemExit("Duplicate generated record IDs")
    OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"records": len(records), "output": str(OUT.relative_to(ROOT))}, ensure_ascii=False))


if __name__ == "__main__":
    main()
