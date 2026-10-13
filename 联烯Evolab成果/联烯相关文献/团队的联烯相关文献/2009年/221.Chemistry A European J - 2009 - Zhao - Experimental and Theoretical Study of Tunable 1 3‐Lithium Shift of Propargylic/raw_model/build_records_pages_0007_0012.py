#!/usr/bin/env python3
"""Enrich Zhao et al. records from PDF pages 7--12."""
from __future__ import annotations

import copy
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
DATASET = ROOT / "runs/current/dataset.json"
OUT = ROOT / "runs/current/raw_model/records_pages_0007_0012.json"
COVERAGE = ROOT / "runs/current/coverage/pages_0007_0012.json"
TASKS = ROOT / "runs/current/tasks.json"
DOC = "doc_3e906dbef45cd67b"


def ev(*pages: int) -> list[str]:
    result: list[str] = []
    for page in pages:
        result.extend([f"{DOC}:page{page}:image", f"{DOC}:page{page}:text"])
    return result


def uniq(values):
    return list(dict.fromkeys(values))


def fact(value, evidence=()):
    return {
        "value": value,
        "evidence_ids": list(evidence),
        "verification": "missing" if value is None else "unreviewed",
    }


def field(name, value, evidence=(), targets=None):
    result = {"name": name, "fact": fact(value, evidence)}
    if targets:
        result["target_entity_ids"] = list(targets)
    return result


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


def add_record_evidence(record, evidence):
    record["evidence_ids"] = uniq(record["evidence_ids"] + list(evidence))


def participant(record, entity_id):
    return next(p for p in record["participants"] if p["entity_id"] == entity_id)


def upsert_amount(record, entity_id, name, value, evidence):
    p = participant(record, entity_id)
    p["amounts"] = [x for x in p["amounts"] if x["name"] != name]
    p["amounts"].append(field(name, value, evidence))


def add_participant(record, item):
    record["participants"] = [p for p in record["participants"] if p["entity_id"] != item["entity_id"]]
    record["participants"].append(item)
    for step in record["steps"]:
        step["participant_ids"] = uniq(step["participant_ids"] + [item["entity_id"]])


def upsert_condition(record, name, value, evidence):
    step = record["steps"][0]
    step["conditions"] = [x for x in step["conditions"] if x["name"] != name]
    step["conditions"].append(field(name, value, evidence))


def upsert_outcome(record, name, value, evidence, targets=None):
    record["outcomes"] = [x for x in record["outcomes"] if x["name"] != name]
    record["outcomes"].append(field(name, value, evidence, targets))


data = json.loads(DATASET.read_text())
by_id = {r["record_id"]: r for r in data["experiments"]}
records = []


# Pages 7--8 extend the existing LDA/diisopropylamine computational mechanism.
rid = f"{DOC}:schemes11_12_computational_lda_mechanism"
lda = copy.deepcopy(by_id[rid])
e78 = ev(7, 8)
add_record_evidence(lda, e78)
lda["steps"].append({
    "step_id": "mixed_thf_solvation_model",
    "participant_ids": ["b1", "lda", "e1_e2", "c1"],
    "conditions": [
        field("operation", "mixed explicit-THF plus IEFPCM continuum-solvation calculation for Scheme 12 steps 1-3", e78),
        field("temperature", {"number": 298, "unit": "K"}, ev(7)),
        field("optimization_method", "B3LYP/6-31G**; single-point and long-range solvation terms at B3LYP/6-311G**", e78),
        field("thf_dielectric_constant", 7.58, ev(7)),
        field("solvated_rate_determining_barrier", "16.4 kcal mol-1", ev(8)),
        field("overall_lda_isomerization_barrier", "approximately 21.0 kcal mol-1", ev(8)),
    ],
})
lda["notes"].extend([
    fact("Figure 2 locates bridged, linear-allenyl, and propargyl solvated isomers; THF-B1-a and THF-C2-b are reported as the most stable B-1 and C-1 solvated structures, respectively.", ev(7)),
    fact("THF solvation is reported to lower the transition-state relative energies and accelerate deprotonation/isomerization steps 1-3.", e78),
])
lda["review"]["unresolved"] = [
    "This is a computational/proposed pathway rather than a synthetic batch; coordination structures, aggregation equilibria, and energy-reference conventions require specialist review.",
    "The approximately 21.0 kcal mol-1 overall barrier includes an approximate dimer/monomer correction rather than a directly optimized single transition state.",
]
records.append(lda)


# Pages 8--10: Conditions-D additive/deaggregation and dilithiated-species model.
e810 = ev(8, 9, 10)
cond_d = {
    "record_id": f"{DOC}:schemes13_15_computational_condition_d_mechanism",
    "document_id": DOC,
    "source_reaction_id": "schemes13_15_computational_condition_d_mechanism",
    "record_kind": "mechanism",
    "status": "candidate",
    "completeness": "partial",
    "evidence_ids": e810,
    "participants": [
        part("allenyllithium_monomer", "reactant", "monomeric 1-phenylbuta-1,2-dien-1-yllithium", e810),
        part("allenyllithium_dimer", "unspecified_agent", "dimeric 1-phenylbuta-1,2-dien-1-yllithium", e810),
        part("dilithium_species", "unspecified_agent", "1-phenylbuta-1,2-dien-1,3-yl dilithium species", ev(9, 10)),
        part("shifted_allenyllithium", "product", "isomerized 1-phenylbuta-1,2-dien-3-yllithium model", ev(9, 10)),
        part("thf", "solvent", "THF", e810, name="tetrahydrofuran", smiles="C1CCOC1"),
        part("pyridine", "unspecified_agent", "pyridine (Py)", e810, name="pyridine", smiles="n1ccccc1"),
        part("tmeda", "reagent", "TMEDA", e810, name="N,N,N',N'-tetramethylethylenediamine", smiles="CN(C)CCN(C)C"),
        part("hmpa", "reagent", "HMPA", e810, name="hexamethylphosphoramide"),
    ],
    "steps": [
        {
            "step_id": "global_minimum_models",
            "participant_ids": ["allenyllithium_monomer", "allenyllithium_dimer", "thf", "pyridine", "tmeda", "hmpa"],
            "conditions": [
                field("operation", "compare solvated monomer and dimer free energies for the Conditions-D system", ev(8, 9)),
                field("temperature", {"number": 298, "unit": "K"}, ev(8)),
                field("optimization_method", "B3LYP/6-31G* with thermal corrections; single-point energy at B3LYP/6-311G**", ev(8)),
            ],
        },
        {
            "step_id": "possible_pathways_p1_to_p5",
            "participant_ids": ["allenyllithium_monomer", "dilithium_species", "shifted_allenyllithium", "thf", "pyridine", "tmeda"],
            "conditions": [
                field("operation", "evaluate concerted P1, stepwise P2, separated-ion-pair P3, allene-mediated P4, and dilithium-catalyzed P5 isomerization pathways", ev(9)),
                field("p2_p3_activation_energy", "over 30 kcal mol-1", ev(9)),
                field("p5_thf_overall_barrier", "approximately 22.6 kcal mol-1", ev(9, 10)),
                field("p5_pyridine_overall_barrier", "21.4 kcal mol-1", ev(10)),
                field("p5_tmeda_overall_barrier", "approximately 19.7 kcal mol-1", ev(9, 10)),
            ],
        },
    ],
    "outcomes": [],
    "notes": [
        fact("THF- and pyridine-solvated dimers are reported as global minima, whereas TMEDA- and HMPA-solvated monomers are reported as global minima.", ev(8, 9)),
        fact("The P1 transition state could not be located; P2 and P3 were judged too high in energy; P4 was not considered under the stated excess-BuLi conditions; P5 was identified as the most probable pathway.", ev(9)),
        fact("HMPA transition-state models were not calculated because of computational-size limitations; its proposed acceleration is inferred by analogy to additive-driven deaggregation.", ev(9, 10)),
    ],
    "review": {
        "method": "none",
        "reviewer": None,
        "checked_fields": [],
        "unresolved": [
            "This is a computational/proposed mechanism, not an isolated synthetic experiment.",
            "Exact coordination geometries, aggregation states, and the correspondence between calculated solvent models and experimental HMPA conditions require specialist review.",
        ],
    },
}
records.append(cond_d)


def enrich_common(record, evidence, *, substrate_name, product_name, atmosphere="N2"):
    add_record_evidence(record, evidence)
    participant(record, "substrate")["name"] = fact(substrate_name, evidence)
    participant(record, "product")["name"] = fact(product_name, evidence)
    add_participant(record, part("thf", "solvent", "THF", evidence, name="tetrahydrofuran", smiles="C1CCOC1"))
    upsert_condition(record, "atmosphere", atmosphere, evidence)
    upsert_condition(record, "reaction_endpoint", "reaction complete as monitored by TLC", evidence)
    upsert_condition(record, "workup", "quench with saturated NH4Cl; extract with diethyl ether; dry over MgSO4; filter; rotary evaporation", evidence)
    upsert_condition(record, "purification", "flash chromatography on silica gel with petroleum ether", evidence)
    upsert_outcome(record, "yield_measurement_basis", "isolated yield", evidence)


# Pages 10--11: detailed Conditions A preparation for Table 1 entry 9 (2i).
e1011 = ev(10, 11)
r = copy.deepcopy(by_id[f"{DOC}:table1_entry9_conditionA_2i"])
enrich_common(
    r,
    e1011,
    substrate_name="1-(p-phenylphenyl)pent-1-yne",
    product_name="1-(p-phenylphenyl)-1-(4-bromophenyl)penta-1,2-diene",
)
participant(r, "aryl_halide")["name"] = fact("4-bromoiodobenzene", ev(11))
upsert_amount(r, "substrate", "mass", {"number": 68, "unit": "mg"}, ev(10))
upsert_amount(r, "substrate", "amount", {"number": 0.31, "unit": "mmol"}, ev(10))
upsert_amount(r, "base", "volume", {"number": 0.23, "unit": "mL"}, ev(10))
upsert_amount(r, "base", "concentration", {"number": 1.6, "unit": "M"}, ev(10))
upsert_amount(r, "base", "amount", {"number": 0.37, "unit": "mmol"}, ev(10))
upsert_amount(r, "znbr2", "mass", {"number": 140, "unit": "mg"}, ev(11))
upsert_amount(r, "znbr2", "amount", {"number": 0.62, "unit": "mmol"}, ev(11))
upsert_amount(r, "pdpph3", "mass", {"number": 18, "unit": "mg"}, ev(11))
upsert_amount(r, "pdpph3", "loading", {"number": 5, "unit": "mol%"}, ev(11))
upsert_amount(r, "aryl_halide", "mass", {"number": 105, "unit": "mg"}, ev(11))
upsert_amount(r, "aryl_halide", "amount", {"number": 0.37, "unit": "mmol"}, ev(11))
upsert_amount(r, "thf", "substrate_solution_volume", {"number": 3, "unit": "mL"}, ev(10))
upsert_amount(r, "thf", "znbr2_solution_volume", {"number": 4, "unit": "mL"}, ev(11))
upsert_condition(r, "vessel", "dry Schlenk tube", ev(10))
upsert_condition(r, "transmetallation_temperature", {"number": -20, "unit": "°C"}, ev(11))
upsert_condition(r, "transmetallation_time", {"number": 5, "unit": "min"}, ev(11))
upsert_condition(r, "warming_time_to_room_temperature", {"number": 13, "unit": "min"}, ev(11))
upsert_condition(r, "tlc_eluent", "petroleum ether (60-90 °C fraction)", ev(11))
upsert_outcome(r, "isolated_product_mass", {"number": 80, "unit": "mg"}, ev(11), ["product"])
upsert_outcome(r, "product_yield", {"number": 69, "unit": "%"}, ev(3, 11), ["product"])
upsert_outcome(r, "physical_form", "liquid", ev(11), ["product"])
r["review"]["unresolved"] = [
    "Coupling duration is reported only as completion by TLC; candidate structure and analytical assignment remain unverified.",
    "No supporting-information file was supplied or associated.",
]
records.append(r)


# Page 11: detailed Conditions B preparation for Table 1 entry 9 (3i).
e11 = ev(11)
r = copy.deepcopy(by_id[f"{DOC}:table1_entry9_conditionB_3i"])
enrich_common(
    r,
    e11,
    substrate_name="1-(p-phenylphenyl)pent-1-yne",
    product_name="1-(p-phenylphenyl)-3-(4-bromophenyl)penta-1,2-diene",
)
participant(r, "aryl_halide")["name"] = fact("4-bromoiodobenzene", e11)
participant(r, "base")["name"] = fact("lithium diisopropylamide, commercial Aldrich product", e11)
upsert_amount(r, "substrate", "mass", {"number": 80, "unit": "mg"}, e11)
upsert_amount(r, "substrate", "amount", {"number": 0.37, "unit": "mmol"}, e11)
upsert_amount(r, "base", "volume", {"number": 0.37, "unit": "mL"}, e11)
upsert_amount(r, "base", "concentration", {"number": 2.0, "unit": "M"}, e11)
upsert_amount(r, "base", "amount", {"number": 0.73, "unit": "mmol"}, e11)
upsert_amount(r, "znbr2", "mass", {"number": 407, "unit": "mg"}, e11)
upsert_amount(r, "znbr2", "amount", {"number": 1.81, "unit": "mmol"}, e11)
upsert_amount(r, "pdpph3", "mass", {"number": 21, "unit": "mg"}, e11)
upsert_amount(r, "pdpph3", "loading", {"number": 5, "unit": "mol%"}, e11)
upsert_amount(r, "aryl_halide", "mass", {"number": 207, "unit": "mg"}, e11)
upsert_amount(r, "aryl_halide", "amount", {"number": 0.73, "unit": "mmol"}, e11)
upsert_amount(r, "thf", "substrate_solution_volume", {"number": 3, "unit": "mL"}, e11)
upsert_amount(r, "thf", "znbr2_solution_volume", {"number": 4, "unit": "mL"}, e11)
upsert_condition(r, "vessel", "dry Schlenk tube", e11)
upsert_condition(r, "lda_addition_temperature", {"number": -78, "unit": "°C"}, e11)
upsert_condition(r, "warming_time_to_room_temperature", {"number": 1, "unit": "h"}, e11)
upsert_condition(r, "transmetallation_temperature", "r.t.", e11)
upsert_condition(r, "transmetallation_time", {"number": 25, "unit": "min"}, e11)
upsert_outcome(r, "isolated_product_mass", {"number": 97, "unit": "mg"}, e11, ["product"])
upsert_outcome(r, "product_yield", {"number": 71, "unit": "%"}, ev(3, 11), ["product"])
upsert_outcome(r, "physical_form", "solid", e11, ["product"])
upsert_outcome(r, "melting_point", {"minimum": 107, "maximum": 108, "unit": "°C", "raw_text": "107-108 °C"}, e11, ["product"])
r["review"]["unresolved"] = [
    "Coupling duration is reported only as completion by TLC; candidate structure and analytical assignment remain unverified.",
    "The commercial LDA carrier mixture is stated as THF/ethylbenzene/pentane, but its component proportions are not reported.",
    "No supporting-information file was supplied or associated.",
]
records.append(r)


def enrich_4b_5b(record, *, condition, product_name, product_mass, yield_value, nbuli_volume):
    enrich_common(
        record,
        e11,
        substrate_name="1-phenylbut-3-en-1-yne",
        product_name=product_name,
    )
    participant(record, "aryl_iodide")["name"] = fact("2-methyliodobenzene", e11)
    upsert_amount(record, "substrate", "mass", {"number": 52, "unit": "mg"}, e11)
    upsert_amount(record, "substrate", "amount", {"number": 0.41, "unit": "mmol"}, e11)
    upsert_amount(record, "rli", "volume", {"number": nbuli_volume, "unit": "mL"}, e11)
    upsert_amount(record, "rli", "concentration", {"number": 1.6, "unit": "M"}, e11)
    upsert_amount(record, "rli", "amount", {"number": 0.49, "unit": "mmol"}, e11)
    upsert_amount(record, "pdpph3", "mass", {"number": 16, "unit": "mg"}, e11)
    upsert_amount(record, "pdpph3", "loading", {"number": 5, "unit": "mol%"}, e11)
    upsert_amount(record, "aryl_iodide", "volume", {"number": 34, "unit": "uL"}, e11)
    upsert_amount(record, "aryl_iodide", "amount", {"number": 0.27, "unit": "mmol"}, e11)
    upsert_amount(record, "thf", "substrate_solution_volume", {"number": 4, "unit": "mL"}, e11)
    upsert_amount(record, "thf", "organolithium_solution_volume", {"number": 2, "unit": "mL"}, e11)
    upsert_amount(record, "thf", "znbr2_solution_volume", {"number": 4, "unit": "mL"}, e11)
    upsert_condition(record, "vessel", "reaction conducted under nitrogen", e11)
    upsert_outcome(record, "isolated_product_mass", {"number": product_mass, "unit": "mg"}, e11, ["product"])
    upsert_outcome(record, "product_yield", {"number": yield_value, "unit": "%"}, ev(4, 11), ["product"])
    upsert_outcome(record, "physical_form", "liquid", e11, ["product"])
    record["review"]["unresolved"] = [
        "Coupling duration is reported only as completion by TLC; candidate structure and analytical assignment remain unverified.",
        "No supporting-information file was supplied or associated.",
    ]


# Page 11: detailed Conditions C preparation for Table 4 entry 2 (4b).
r = copy.deepcopy(by_id[f"{DOC}:table4_entry2_conditionC_4b"])
enrich_4b_5b(
    r,
    condition="C",
    product_name="1-phenyl-1-(2-methylphenyl)octa-1,2-diene",
    product_mass=58,
    yield_value=78,
    nbuli_volume=0.30,
)
upsert_amount(r, "znbr2", "mass", {"number": 186, "unit": "mg"}, e11)
upsert_amount(r, "znbr2", "amount", {"number": 0.82, "unit": "mmol"}, e11)
upsert_condition(r, "transmetallation_temperature", {"number": -78, "unit": "°C"}, e11)
upsert_condition(r, "transmetallation_time", {"number": 10, "unit": "min"}, e11)
upsert_condition(r, "warming_time_to_room_temperature", {"number": 25, "unit": "min"}, e11)
records.append(r)


# Page 11: detailed Conditions D preparation for Table 4 entry 2 (5b).
r = copy.deepcopy(by_id[f"{DOC}:table4_entry2_conditionD_5b"])
enrich_4b_5b(
    r,
    condition="D",
    product_name="1-phenyl-3-(2-methylphenyl)octa-1,2-diene",
    product_mass=56,
    yield_value=75,
    nbuli_volume=0.31,
)
upsert_amount(r, "hmpa", "volume", {"number": 0.14, "unit": "mL"}, e11)
upsert_amount(r, "hmpa", "amount", {"number": 0.82, "unit": "mmol"}, e11)
upsert_amount(r, "znbr2", "mass", {"number": 185, "unit": "mg"}, e11)
upsert_amount(r, "znbr2", "amount", {"number": 0.82, "unit": "mmol"}, e11)
upsert_condition(r, "warming_time_to_room_temperature", {"number": 1, "unit": "h"}, e11)
upsert_condition(r, "transmetallation_temperature", "r.t.", e11)
upsert_condition(r, "transmetallation_time", {"number": 25, "unit": "min"}, e11)
records.append(r)


OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")


coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 7,
            "state": "attempted",
            "regions": [
                {
                    "region": "full original page, including Figure 2 and solvated-model discussion",
                    "finding": "Continuation of the B3LYP LDA/diisopropylamine mechanism: mixed THF solvation models, relative free energies, coordination isomers, and transition states; no new synthetic batch.",
                    "evidence_ids": ev(7),
                }
            ],
            "record_ids": [f"{DOC}:schemes11_12_computational_lda_mechanism"],
            "unresolved": ["Coordination structures and calculated energy references are not independently verified."],
        },
        {
            "page": 8,
            "state": "attempted",
            "regions": [
                {
                    "region": "upper-left continuation of solvated Scheme-12 discussion",
                    "finding": "Reports a 16.4 kcal mol-1 solvated rate-determining barrier and an approximately 21.0 kcal mol-1 overall LDA isomerization barrier; merged into the existing computational mechanism.",
                    "evidence_ids": ev(8),
                },
                {
                    "region": "right column and lower Figure 3",
                    "finding": "Begins the Conditions-D computational study and compares monomer/dimer global minima for THF, pyridine, TMEDA, and HMPA models; classified as mechanism.",
                    "evidence_ids": ev(8),
                },
            ],
            "record_ids": [
                f"{DOC}:schemes11_12_computational_lda_mechanism",
                f"{DOC}:schemes13_15_computational_condition_d_mechanism",
            ],
            "unresolved": ["The paper refers to unsupplied SI for additional model structures and energies."],
        },
        {
            "page": 9,
            "state": "attempted",
            "regions": [
                {
                    "region": "full original page, including Schemes 13 and 14",
                    "finding": "Five possible Conditions-D pathways are evaluated computationally; P5, catalyzed by a dilithiated species, is proposed as most probable. This is mechanistic modeling, not an isolated experiment.",
                    "evidence_ids": ev(9),
                }
            ],
            "record_ids": [f"{DOC}:schemes13_15_computational_condition_d_mechanism"],
            "unresolved": ["HMPA transition-state models were not calculated; P4 was not evaluated under the stated excess-BuLi assumption."],
        },
        {
            "page": 10,
            "state": "attempted",
            "regions": [
                {
                    "region": "upper half Figure 4 and lower-left Scheme 15",
                    "finding": "Completes the Conditions-D dilithium-catalyzed model and reports THF, pyridine, and TMEDA overall barriers; classified as mechanism.",
                    "evidence_ids": ev(10),
                },
                {
                    "region": "lower-right Experimental Section, beginning of Conditions A for 2i",
                    "finding": "Detailed Table 1 entry-9 Conditions-A batch begins with nBuLi/substrate quantities, THF volume, dry Schlenk vessel, -20 °C, and nitrogen; continued on page 11 and merged into the existing 2i record.",
                    "evidence_ids": ev(10),
                },
                {
                    "region": "middle-right Conclusions",
                    "finding": "Summary statements only; no additional independent experiment was created.",
                    "evidence_ids": ev(10),
                },
            ],
            "record_ids": [
                f"{DOC}:schemes13_15_computational_condition_d_mechanism",
                f"{DOC}:table1_entry9_conditionA_2i",
            ],
            "unresolved": ["The 2i procedure crosses onto page 11; coupling duration is stated only by TLC completion."],
        },
        {
            "page": 11,
            "state": "attempted",
            "regions": [
                {
                    "region": "left column, completion of Conditions A and full Conditions B for 2i/3i",
                    "finding": "Exact quantities, staged temperatures/times, nitrogen atmosphere, workup, purification, isolated masses, and yields were merged into the existing Table 1 entry-9 records.",
                    "evidence_ids": ev(11),
                },
                {
                    "region": "left-to-middle column, Conditions C and D for 4b/5b",
                    "finding": "Exact quantities, HMPA loading, staged operations, nitrogen atmosphere, workup, purification, isolated masses, and yields were merged into existing Table 4 entry-2 records.",
                    "evidence_ids": ev(11),
                },
                {
                    "region": "right column analytical continuation, acknowledgements, and references",
                    "finding": "Characterization supports product identity but is not an additional reaction; acknowledgements and references contain no present-paper batch.",
                    "evidence_ids": ev(11),
                },
            ],
            "record_ids": [
                f"{DOC}:table1_entry9_conditionA_2i",
                f"{DOC}:table1_entry9_conditionB_3i",
                f"{DOC}:table4_entry2_conditionC_4b",
                f"{DOC}:table4_entry2_conditionD_5b",
            ],
            "unresolved": ["All four coupling durations are reported only as completion by TLC; analytical assignments and candidate structures remain unverified."],
        },
        {
            "page": 12,
            "state": "attempted",
            "regions": [
                {
                    "region": "full original page, references 12-34 and publication dates",
                    "finding": "Bibliography only; no reaction arrow, table, procedure, condition, yield, selectivity result, or present-paper experiment.",
                    "evidence_ids": ev(12),
                }
            ],
            "record_ids": [],
            "unresolved": ["Cited primary papers were not supplied and were not expanded into reaction records from bibliography alone."],
        },
    ],
}
COVERAGE.parent.mkdir(parents=True, exist_ok=True)
COVERAGE.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")


tasks = json.loads(TASKS.read_text())
requested = {f"{DOC}:page{page}:text" for page in range(7, 13)}
for task in tasks:
    if task.get("document_id") == DOC and task.get("task_id") in requested:
        task["state"] = "attempted"
TASKS.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"submitted_records": len(records), "new_records": 1, "updated_records": 5, "coverage_pages": list(range(7, 13))}, ensure_ascii=False))
