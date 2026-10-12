#!/usr/bin/env python3
"""Build evidence-linked machine records for jo050183d PDF pages 1-3."""
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "runs/current"
DOC = "doc_e64c3f8986f6b83a"
P = {
    1: [f"{DOC}:page1:text", f"{DOC}:page1:image"],
    2: [f"{DOC}:page2:text", f"{DOC}:page2:image"],
    3: [f"{DOC}:page3:text", f"{DOC}:page3:image"],
}


def fact(value, evidence):
    return {
        "value": value,
        "evidence_ids": list(evidence) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def fld(name, value, evidence, targets=None):
    item = {"name": name, "fact": fact(value, evidence)}
    if targets:
        item["target_entity_ids"] = list(targets)
    return item


def part(entity_id, role, name, evidence, *, label=None, smiles=None, amounts=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence),
        "smiles": fact(smiles, evidence),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": amounts or [],
    }


def rec(suffix, source_id, kind, evidence, participants, steps, outcomes, *, notes=(), unresolved=()):
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


def q(number, unit, **extra):
    return {"number": number, "unit": unit, **extra}


def table1_records():
    evidence = P[1]
    rows = [
        (1, "n-BuLi", -78, 65, q(0, "%"), None),
        (2, "LDA", -78, 33, q(0, "%"), None),
        (3, "n-BuLi", -40, 49, q(0, "%"), None),
        (4, "LDA", -40, 19, q(0, "%"), None),
        (5, "n-BuLi", -20, 57, q(0, "%"), None),
        (6, "LDA", -20, 0, "trace", None),
        (7, "n-BuLi", 0, 28, q(13, "%"), None),
        (8, "LDA", 0, 0, q(14, "%"), None),
        (9, "n-BuLi", 15, 0, q(39, "%"), None),
        (10, "LDA", 15, 0, q(43, "%"), None),
        (11, "n-BuLi", "reflux", 0, q(39, "%"), None),
        (12, "LDA", "reflux", 0, q(41, "%"), None),
        (13, "n-BuLi", 90, 0, q(0, "%"), "dioxane"),
        (14, "LDA", 90, 0, q(20, "%"), "dioxane"),
        (15, "n-BuLi", -78, 0, q(0, "%"), "hmpa"),
        (16, "LDA", 17, 0, q(0, "%"), "hmpa"),
    ]
    result = []
    for entry, base, temp, yield2, yield3, special in rows:
        solvent_name = "1,4-dioxane" if special == "dioxane" else "tetrahydrofuran"
        solvent_smiles = "O1CCOCC1" if special == "dioxane" else "C1CCOC1"
        base_smiles = "[Li+].CC(C)[N-]C(C)C" if base == "LDA" else None
        participants = [
            part("t1_substrate_1a", "reactant", "1-phenyl-1-propyne", evidence, label="1a", smiles="CC#Cc1ccccc1"),
            part("t1_iodobenzene", "reactant", "iodobenzene", evidence, smiles="Ic1ccccc1"),
            part("t1_base", "reagent", base, evidence, smiles=base_smiles),
            part("t1_znbr2", "reagent", "zinc bromide", evidence, smiles="[Zn+2].[Br-].[Br-]"),
            part("t1_pd", "catalyst", "tetrakis(triphenylphosphine)palladium(0)", evidence, label="Pd(PPh3)4"),
            part("t1_solvent", "solvent", solvent_name, evidence, smiles=solvent_smiles),
            part("t1_product_2a", "product", "1,1-diphenylpropadiene", evidence, label="2a", smiles="C=C=C(c1ccccc1)c1ccccc1"),
            part("t1_product_3a", "product", "1,3-diphenyl-1-propyne", evidence, label="3a", smiles="c1ccccc1C#CCc1ccccc1"),
            part("t1_internal_standard", "unspecified_agent", "dibromomethane", evidence, label="CH2Br2", smiles="BrCBr"),
        ]
        lithiation_conditions = [
            fld("temperature", "reflux" if temp == "reflux" else q(temp, "°C"), evidence),
            fld("time", q(1, "h"), evidence),
        ]
        steps = [{
            "step_id": "lithiation",
            "participant_ids": ["t1_substrate_1a", "t1_base", "t1_solvent"],
            "conditions": lithiation_conditions,
        }]
        if special == "hmpa":
            participants.append(part(
                "t1_hmpa", "reagent", "hexamethylphosphoramide", evidence,
                label="HMPA", smiles="CN(C)P(=O)(N(C)C)N(C)C",
                amounts=[fld("equivalents", q(2, "equiv"), evidence)],
            ))
            steps.append({
                "step_id": "hmpa_addition",
                "participant_ids": ["t1_hmpa"],
                "conditions": [fld("temperature", "r.t.", evidence), fld("time", q(1, "h"), evidence)],
            })
        steps.extend([
            {"step_id": "transmetalation", "participant_ids": ["t1_znbr2"], "conditions": []},
            {"step_id": "cross_coupling", "participant_ids": ["t1_iodobenzene", "t1_pd"], "conditions": []},
        ])
        outcomes = [
            fld("NMR_yield", q(yield2, "%"), evidence, ["t1_product_2a"]),
            fld("NMR_yield", yield3, evidence, ["t1_product_3a"]),
            fld(
                "yield_measurement_basis",
                "Based on 1-phenyl-1-propyne; determined by 300 MHz 1H NMR with CH2Br2 as internal standard.",
                evidence,
                ["t1_product_2a", "t1_product_3a"],
            ),
        ]
        result.append(rec(
            f"table1_entry_{entry:02d}", f"Table 1 entry {entry}", "optimization_entry", evidence,
            participants, steps, outcomes,
            notes=("Table 1 reports both allene 2a and alkyne 3a outcomes for this condition.",),
            unresolved=(
                "Exact reactant/reagent amounts and the coupling completion time are not reported in Table 1.",
                "Workup and purification for this optimization run are not stated.",
                "Supporting information is mentioned by the paper but was not supplied or explicitly associated.",
                "Candidate structures require source review and remain unverified.",
            ),
        ))
    return result


AR2 = {
    1: ("phenyl", "iodobenzene", "Ic1ccccc1", "c1ccccc1", "2a", "3a"),
    2: ("1-naphthyl", "1-iodonaphthalene", "Ic1cccc2ccccc12", "c1ccc2ccccc2c1", "2b", "3b"),
    3: ("4-methoxyphenyl", "1-iodo-4-methoxybenzene", "COc1ccc(I)cc1", "c1ccc(OC)cc1", "2c", "3c"),
    4: ("4-(methoxycarbonyl)phenyl", "methyl 4-iodobenzoate", "COC(=O)c1ccc(I)cc1", "c1ccc(C(=O)OC)cc1", "2d", "3d"),
    5: ("2-methylphenyl", "1-iodo-2-methylbenzene", "Cc1ccccc1I", "c1ccccc1C", "2e", "3e"),
    6: ("4-cyanophenyl", "4-iodobenzonitrile", "N#Cc1ccc(I)cc1", "c1ccc(C#N)cc1", "2f", "3f"),
    7: ("phenyl", "iodobenzene", "Ic1ccccc1", "c1ccccc1", "2g", "3g"),
}


def scope_smiles(entry, condition):
    ar1 = "c1ccc(-c2ccccc2)cc1" if entry == 7 else "c1ccccc1"
    ar2 = AR2[entry][3]
    if condition == "A":
        return f"C=C=C({ar1}){ar2}"
    return f"{ar2}C#CC{ar1}"


def exact_entry1_participants(condition, evidence, participants):
    by_id = {p["entity_id"]: p for p in participants}
    by_id["scope_substrate"]["amounts"] = [fld("mass", q(46, "mg"), evidence), fld("amount", q(0.40, "mmol"), evidence)]
    by_id["scope_znbr2"]["amounts"] = [fld("mass", q(180, "mg"), evidence), fld("amount", q(0.80, "mmol"), evidence), fld("equivalents", q(2, "equiv"), evidence)]
    by_id["scope_thf"]["amounts"] = [fld("initial_volume", q(3, "mL"), evidence), fld("ZnBr2_solution_volume", q(4, "mL"), evidence)]
    by_id["scope_pd"]["amounts"] = [fld("mass", q(16, "mg"), evidence), fld("catalyst_loading", q(5, "mol%"), evidence)]
    by_id["scope_aryl_iodide"]["amounts"] = [fld("volume", q(30, "uL"), evidence), fld("amount", q(0.27, "mmol"), evidence)]
    if condition == "A":
        by_id["scope_base"]["amounts"] = [fld("volume", q(0.30, "mL"), evidence), fld("concentration", q(1.6, "M"), evidence), fld("amount", q(0.48, "mmol"), evidence), fld("equivalents", q(1.2, "equiv"), evidence)]
        participants.append(part("scope_hexanes", "solvent", "hexanes", evidence))
    else:
        by_id["scope_base"]["amounts"] = [fld("volume", q(0.40, "mL"), evidence), fld("concentration", q(2.0, "M"), evidence), fld("amount", q(0.80, "mmol"), evidence), fld("equivalents", q(2, "equiv"), evidence)]
        participants.extend([
            part("scope_pentane", "solvent", "pentane", evidence, smiles="CCCCC"),
            part("scope_ethylbenzene", "solvent", "ethylbenzene", evidence, smiles="CCc1ccccc1"),
        ])
    participants.extend([
        part("scope_nh4cl", "reagent", "saturated ammonium chloride", evidence, label="saturated NH4Cl"),
        part("scope_ether", "solvent", "ether", evidence, label="ether"),
        part("scope_mgso4", "reagent", "magnesium sulfate", evidence, label="MgSO4", smiles="[Mg+2].[O-]S(=O)(=O)[O-]"),
        part("scope_petroleum_ether", "solvent", "petroleum ether (60-90 °C)", evidence),
        part("scope_silica", "reagent", "silica gel", evidence),
    ])


def table2_record(entry, condition, yield_value):
    evidence = list(P[3])
    if entry == 1 and condition == "A":
        evidence = P[2] + P[3]
    if entry == 5 and condition == "B":
        evidence = P[2] + P[3]
    ar2_name, iodide_name, iodide_smiles, _, label_a, label_b = AR2[entry]
    product_label = label_a if condition == "A" else label_b
    substrate_name = "1-(4-biphenylyl)-1-propyne" if entry == 7 else "1-phenyl-1-propyne"
    substrate_smiles = "CC#Cc1ccc(-c2ccccc2)cc1" if entry == 7 else "CC#Cc1ccccc1"
    base_name = "n-butyllithium" if condition == "A" else "lithium diisopropylamide"
    base_label = "n-BuLi" if condition == "A" else "LDA"
    base_smiles = None if condition == "A" else "[Li+].CC(C)[N-]C(C)C"
    product_name = (
        f"1-({ar2_name})-1-(phenyl)propadiene" if condition == "A" and entry != 7
        else f"1-({ar2_name})-1-(4-biphenylyl)propadiene" if condition == "A"
        else f"1-({ar2_name})-3-phenyl-1-propyne" if entry != 7
        else "1-phenyl-3-(4-biphenylyl)-1-propyne"
    )
    participants = [
        part("scope_substrate", "reactant", substrate_name, evidence, label="1", smiles=substrate_smiles),
        part("scope_aryl_iodide", "reactant", iodide_name, evidence, label=f"Ar2I ({ar2_name})", smiles=iodide_smiles),
        part("scope_base", "reagent", base_name, evidence, label=base_label, smiles=base_smiles,
             amounts=[fld("equivalents", q(1.2 if condition == "A" else 2, "equiv"), evidence)]),
        part("scope_znbr2", "reagent", "zinc bromide", evidence, label="ZnBr2", smiles="[Zn+2].[Br-].[Br-]", amounts=[fld("equivalents", q(2, "equiv"), evidence)]),
        part("scope_pd", "catalyst", "tetrakis(triphenylphosphine)palladium(0)", evidence, label="Pd(PPh3)4"),
        part("scope_thf", "solvent", "tetrahydrofuran", evidence, label="THF", smiles="C1CCOC1"),
        part("scope_product", "product", product_name, evidence, label=product_label, smiles=scope_smiles(entry, condition)),
    ]
    exact = entry == 1
    if exact:
        exact_entry1_participants(condition, evidence, participants)
        next(p for p in participants if p["entity_id"] == "scope_product")["amounts"] = [
            fld("mass", q(44 if condition == "A" else 50, "mg"), evidence)
        ]
    if condition == "A":
        steps = [
            {"step_id": "lithiation", "participant_ids": ["scope_substrate", "scope_base", "scope_thf"], "conditions": [fld("temperature", q(-78, "°C"), evidence), fld("time", q(1, "h"), evidence)]},
            {"step_id": "transmetalation", "participant_ids": ["scope_znbr2", "scope_thf"], "conditions": ([fld("temperature", q(-78, "°C"), evidence), fld("hold_time", q(10, "min"), evidence), fld("warm_to", "r.t.", evidence), fld("warming_time", q(20, "min"), evidence)] if exact else [fld("addition_temperature", q(-78, "°C"), evidence), fld("warm_to", "r.t.", evidence)])},
            {"step_id": "cross_coupling", "participant_ids": ["scope_aryl_iodide", "scope_pd"], "conditions": [fld("temperature", "r.t.", evidence), fld("reaction_time", None, evidence)]},
        ]
    else:
        steps = [
            {"step_id": "lithiation_and_warming", "participant_ids": ["scope_substrate", "scope_base", "scope_thf"], "conditions": [fld("addition_temperature", q(-78, "°C"), evidence), fld("stir_temperature", "r.t.", evidence), fld("time", q(1, "h"), evidence)]},
            {"step_id": "transmetalation", "participant_ids": ["scope_znbr2", "scope_thf"], "conditions": [fld("temperature", "r.t.", evidence), fld("time", q(25 if exact else 20, "min"), evidence)]},
            {"step_id": "cross_coupling", "participant_ids": ["scope_aryl_iodide", "scope_pd"], "conditions": [fld("temperature", "r.t.", evidence), fld("reaction_time", None, evidence)]},
        ]
    if exact:
        steps.append({
            "step_id": "workup_and_purification",
            "participant_ids": ["scope_nh4cl", "scope_ether", "scope_mgso4", "scope_petroleum_ether", "scope_silica"],
            "conditions": [
                fld("operation", "Reaction completion monitored by TLC; quenched with saturated NH4Cl, extracted with ether, dried over MgSO4, and concentrated by rotary evaporation.", evidence),
                fld("purification", "Flash chromatography on silica gel using petroleum ether.", evidence),
            ],
        })
    basis = "isolated yield based on the amount of aryl halide used"
    if entry == 7 and condition == "A":
        basis = "isolated yield based on the amount of 1-(4-biphenylyl)-1-propyne used"
    outcomes = [
        fld("isolated_yield", q(yield_value, "%"), evidence, ["scope_product"]),
        fld("yield_measurement_basis", basis, evidence, ["scope_product"]),
    ]
    if entry == 6 and condition == "A":
        participants.append(part(
            "scope_byproduct_3f_prime", "product", "1-phenyl-3-(4-cyanophenyl)-1-propyne", evidence,
            label="3f'", smiles="c1ccccc1C#CCc1ccc(C#N)cc1",
        ))
        outcomes.append(fld(
            "byproduct_yield", {"number": 4, "unit": "%", "qualifier": "lt", "raw_text": "<4%"},
            evidence, ["scope_byproduct_3f_prime"],
        ))
    notes = []
    unresolved = [
        "Reaction completion time is not numerically reported.",
        "Supporting information is mentioned by the paper but was not supplied or explicitly associated.",
        "Candidate structures require source review and remain unverified.",
    ]
    if not exact:
        unresolved.append("Entry-specific reactant scale, workup, purification, and product mass are not reported in the main-text table.")
    else:
        notes.append("The Table 2 conditions-B footnote gives 20 min after ZnBr2, while the entry-specific experimental procedure gives 25 min; the specific procedure value is retained.")
        unresolved.append("The duration after catalyst/aryl iodide addition is reported only as until TLC completion.")
    if entry == 5 and condition == "B":
        notes.append("Scheme 3 and Table 2 entry 5 conditions B describe the same 3e experiment; their evidence is merged rather than duplicated.")
    return rec(
        f"table2_entry_{entry}_{condition.lower()}", f"Table 2 entry {entry}, conditions {condition}",
        "substrate_scope_entry", evidence, participants, steps, outcomes, notes=notes, unresolved=unresolved,
    )


def table2_records():
    yields = {1: (85, 96), 2: (77, 67), 3: (85, 94), 4: (99, 99), 5: (47, 52), 6: (96, 92), 7: (79, 66)}
    return [table2_record(entry, cond, yields[entry][0 if cond == "A" else 1]) for entry in range(1, 8) for cond in ("A", "B")]


def scheme2_records():
    evidence = P[2]
    first_participants = [
        part("s2a_propargylic", "reactant", "3-phenyl-1-propyne", evidence, smiles="C#CCc1ccccc1"),
        part("s2a_iodide", "reactant", "1-iodo-2-methylbenzene", evidence, smiles="Cc1ccccc1I"),
        part("s2a_pd", "catalyst", "bis(triphenylphosphine)palladium(II) dichloride", evidence, label="Pd(PPh3)2Cl2"),
        part("s2a_cui", "catalyst", "copper(I) iodide", evidence, label="CuI", smiles="[Cu+].[I-]"),
        part("s2a_et3n", "reagent", "triethylamine", evidence, label="Et3N", smiles="CCN(CC)CC"),
        part("s2a_thf", "solvent", "tetrahydrofuran", evidence, label="THF", smiles="C1CCOC1"),
        part("s2a_product", "product", "1-(2-methylphenyl)-3-phenyl-1-propyne", evidence, label="3e", smiles="Cc1ccccc1C#CCc1ccccc1"),
    ]
    first = rec(
        "scheme2_sonogashira_3e", "Scheme 2, preparation of 3e", "reported_experiment", evidence,
        first_participants,
        [{"step_id": "sonogashira_coupling", "participant_ids": [p["entity_id"] for p in first_participants[:-1]], "conditions": [fld("temperature", q(50, "°C"), evidence), fld("time", q(4, "h"), evidence)]}],
        [fld("reported_yield", q(77, "%"), evidence, ["s2a_product"]), fld("yield_measurement_basis", None, evidence, ["s2a_product"])],
        unresolved=(
            "Reactant quantities, catalyst loadings, atmosphere, workup, purification, and yield basis are not given in Scheme 2.",
            "Supporting information was not supplied or explicitly associated.",
            "Candidate structures require source review and remain unverified.",
        ),
    )
    second_participants = [
        part("s2b_phenylacetylene", "reactant", "phenylacetylene", evidence, smiles="C#Cc1ccccc1"),
        part("s2b_nbuli", "reagent", "n-butyllithium", evidence, label="n-BuLi"),
        part("s2b_benzyl_chloride", "reactant", "1-(chloromethyl)-2-methylbenzene", evidence, smiles="Cc1ccccc1CCl"),
        part("s2b_nai", "reagent", "sodium iodide", evidence, label="NaI", smiles="[Na+].[I-]"),
        part("s2b_product", "product", "1-phenyl-3-(2-methylphenyl)-1-propyne", evidence, label="3e'", smiles="c1ccccc1C#CCc1ccccc1C"),
    ]
    second = rec(
        "scheme2_benzylation_3e_prime", "Scheme 2, preparation of 3e'", "reported_experiment", evidence,
        second_participants,
        [
            {"step_id": "lithiation", "participant_ids": ["s2b_phenylacetylene", "s2b_nbuli"], "conditions": [fld("temperature", q(-78, "°C"), evidence), fld("time", None, evidence)]},
            {"step_id": "benzylation", "participant_ids": ["s2b_benzyl_chloride", "s2b_nai"], "conditions": [fld("initial_temperature", q(-78, "°C"), evidence), fld("final_temperature", "r.t.", evidence), fld("time", None, evidence)]},
        ],
        [fld("reported_yield", q(25, "%"), evidence, ["s2b_product"]), fld("yield_measurement_basis", None, evidence, ["s2b_product"])],
        unresolved=(
            "Reactant quantities, solvent, step durations, atmosphere, workup, purification, and yield basis are not given in Scheme 2.",
            "Supporting information was not supplied or explicitly associated.",
            "Candidate structures require source review and remain unverified.",
        ),
    )
    return [first, second]


def scheme5_records():
    evidence = P[2]
    result = []
    for suffix, branch_temp in (("40c", q(40, "°C")), ("reflux", "reflux")):
        participants = [
            part("s5_substrate", "reactant", "1-phenyl-1-propyne", evidence, smiles="CC#Cc1ccccc1"),
            part("s5_nbuli", "reagent", "n-butyllithium", evidence, label="n-BuLi"),
            part("s5_znbr2", "reagent", "zinc bromide", evidence, label="ZnBr2", smiles="[Zn+2].[Br-].[Br-]"),
            part("s5_iodobenzene", "reactant", "iodobenzene", evidence, label="PhI", smiles="Ic1ccccc1"),
            part("s5_pd", "catalyst", "tetrakis(triphenylphosphine)palladium(0)", evidence, label="Pd(PPh3)4"),
            part("s5_product", "product", "1,1-diphenylpropadiene", evidence, label="2a", smiles="C=C=C(c1ccccc1)c1ccccc1"),
            part("s5_internal_standard", "unspecified_agent", "dibromomethane", evidence, label="CH2Br2", smiles="BrCBr"),
        ]
        result.append(rec(
            f"scheme5_high_temperature_{suffix}", f"Scheme 5, {suffix} branch", "reported_experiment", evidence,
            participants,
            [
                {"step_id": "lithiation", "participant_ids": ["s5_substrate", "s5_nbuli"], "conditions": [fld("temperature", q(-78, "°C"), evidence), fld("time", q(1, "h"), evidence)]},
                {"step_id": "transmetalation_and_heating", "participant_ids": ["s5_znbr2"], "conditions": [fld("initial_temperature", q(-78, "°C"), evidence), fld("final_temperature", branch_temp, evidence), fld("time_at_final_temperature", q(30, "min"), evidence)]},
                {"step_id": "cross_coupling", "participant_ids": ["s5_iodobenzene", "s5_pd"], "conditions": [fld("temperature", branch_temp, evidence), fld("reaction_time", None, evidence)]},
            ],
            [
                fld("scheme_shared_NMR_yield", q(45, "%"), evidence, ["s5_product"]),
                fld("yield_measurement_basis", "Based on 1-phenyl-1-propyne; determined by 300 MHz 1H NMR with CH2Br2 as internal standard.", evidence, ["s5_product"]),
            ],
            notes=(
                "Scheme 5 depicts two alternative temperature branches leading to the same product and prints one shared 45% value.",
                "The adjacent prose describes tests at 40 and 100 °C, whereas the drawn Scheme 5 branches are labeled 40 °C and reflux.",
            ),
            unresolved=(
                "The source does not separately attribute the printed 45% yield between the 40 °C and reflux branches.",
                "The prose/scheme difference between 100 °C and reflux is retained rather than silently reconciled.",
                "Reagent quantities, solvent, atmosphere, workup, purification, and coupling completion time are not reported in Scheme 5.",
                "Supporting information was not supplied or explicitly associated.",
                "Candidate structures require source review and remain unverified.",
            ),
        ))
    return result


records = table1_records() + scheme2_records() + scheme5_records() + table2_records()

raw_path = OUT / "raw_model/extracted_records_pages_0001_0003.json"
raw_path.parent.mkdir(parents=True, exist_ok=True)
raw_path.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")

page1_ids = [f"{DOC}:table1_entry_{i:02d}" for i in range(1, 17)]
page2_ids = [
    f"{DOC}:scheme2_sonogashira_3e",
    f"{DOC}:scheme2_benzylation_3e_prime",
    f"{DOC}:table2_entry_5_b",
    f"{DOC}:scheme5_high_temperature_40c",
    f"{DOC}:scheme5_high_temperature_reflux",
    f"{DOC}:table2_entry_1_a",
]
page3_ids = [f"{DOC}:table2_entry_{i}_{c}" for i in range(1, 8) for c in ("a", "b")]
coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1,
            "state": "attempted",
            "regions": [
                {"region": "upper-left title, abstract graphic, and introductory text", "finding": "Article overview and generic product-selectivity presentation; not a separate reported experiment.", "evidence_ids": P[1]},
                {"region": "upper-right Scheme 1", "finding": "General reaction scheme defining conditions A/B; classified as a general scheme and not duplicated as an experiment.", "evidence_ids": P[1]},
                {"region": "right-column Table 1 including footnotes", "finding": "Sixteen distinct optimization experiments extracted row-by-row, including zero and trace outcomes and the dioxane/HMPA footnotes.", "evidence_ids": P[1]},
                {"region": "lower prose and references", "finding": "Discussion and cited prior work; no additional current-paper experiment extracted from this region.", "evidence_ids": P[1]},
            ],
            "record_ids": page1_ids,
            "unresolved": ["Table 1 does not state exact scales, full workups, or coupling completion times.", "Supporting information is mentioned but not supplied or explicitly associated."],
        },
        {
            "page": 2,
            "state": "attempted",
            "regions": [
                {"region": "upper-left Scheme 2", "finding": "Two independent authentic-sample preparations (3e and 3e') extracted as reported experiments.", "evidence_ids": P[2]},
                {"region": "middle-left Scheme 3 and adjacent prose", "finding": "The 52% preparation of 3e is the same experiment as Table 2 entry 5 conditions B; evidence merged into one record.", "evidence_ids": P[2]},
                {"region": "lower Scheme 4", "finding": "Proposed double 1,3-lithium-shift mechanism; not promoted to a reported experiment.", "evidence_ids": P[2]},
                {"region": "upper-right Scheme 5", "finding": "Two temperature branches extracted separately; the single printed 45% yield remains explicitly branch-ambiguous.", "evidence_ids": P[2]},
                {"region": "right-column Experimental Section start", "finding": "Conditions-A procedure for Table 2 entry 1 begins here and continues on page 3; evidence merged into that scope record.", "evidence_ids": P[2]},
            ],
            "record_ids": page2_ids,
            "unresolved": ["Scheme 5 does not separately assign the shared 45% value to its two temperature branches.", "Scheme 5 labels the second branch reflux while the adjacent prose says 100 °C.", "Several scheme-only reactions omit scale, workup, purification, or yield basis."],
        },
        {
            "page": 3,
            "state": "attempted",
            "regions": [
                {"region": "upper-left Table 2 and footnotes", "finding": "Fourteen distinct substrate-scope experiments extracted from seven rows under conditions A and B; footnote byproduct and yield-basis exceptions preserved.", "evidence_ids": P[3]},
                {"region": "upper-right and middle Experimental Section", "finding": "Detailed conditions A/B for entry 1 merged with the matching Table 2 records rather than duplicated.", "evidence_ids": P[3]},
                {"region": "lower acknowledgments, SI notice, and references", "finding": "No additional current-paper reaction; SI availability is stated, but no SI file was provided or associated.", "evidence_ids": P[3]},
            ],
            "record_ids": page3_ids,
            "unresolved": ["Most Table 2 entries lack entry-specific scale and workup in the supplied main text.", "The entry-1 conditions-B specific procedure gives 25 min after ZnBr2 while the Table 2 footnote gives 20 min; the specific value is retained and conflict noted.", "SI association remains unestablished."],
        },
    ],
}
coverage_path = OUT / "coverage/pages_0001_0003.json"
coverage_path.parent.mkdir(parents=True, exist_ok=True)
coverage_path.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

tasks_path = OUT / "tasks.json"
tasks = json.loads(tasks_path.read_text())
for task in tasks:
    if task.get("document_id") == DOC and task.get("evidence_id") in {P[i][0] for i in (1, 2, 3)}:
        page = int(task["evidence_id"].split(":page", 1)[1].split(":", 1)[0])
        task["state"] = "attempted"
        task["visual_evidence_id"] = P[page][1]
        task["reason"] = "Original page image inspected; extraction decisions and record IDs are mapped in coverage/pages_0001_0003.json."
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"records": len(records), "raw": str(raw_path), "coverage": str(coverage_path)}, ensure_ascii=False))
