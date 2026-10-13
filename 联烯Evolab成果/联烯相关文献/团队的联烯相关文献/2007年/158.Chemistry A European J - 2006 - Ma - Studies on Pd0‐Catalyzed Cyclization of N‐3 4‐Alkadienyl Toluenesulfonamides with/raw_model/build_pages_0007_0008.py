#!/usr/bin/env python3
"""Build evidence-linked machine records for original PDF pages 7--8."""

from __future__ import annotations

import copy
import json
from pathlib import Path


DOC = "doc_45c8b9340dcc6c98"
HERE = Path(__file__).resolve().parent
RUN = HERE.parent
DATASET = RUN / "dataset.json"


def page_ev(page: int) -> list[str]:
    return [f"{DOC}:page{page}:image", f"{DOC}:page{page}:text"]


def fact(value, evidence):
    return {
        "value": value,
        "evidence_ids": list(evidence) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def qty(number, unit, **extra):
    value = {"number": number, "unit": unit}
    value.update(extra)
    return value


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
        "name": fact(name, evidence) if name else fact(None, []),
        "smiles": fact(smiles, evidence) if smiles else fact(None, []),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": amounts or [],
    }


def make_record(rid, kind, evidence, participants, steps, outcomes, *, notes=(), unresolved=()):
    return {
        "record_id": f"{DOC}:{rid}",
        "document_id": DOC,
        "source_reaction_id": rid,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": list(evidence),
        "participants": participants,
        "steps": steps,
        "outcomes": outcomes,
        "notes": [fact(note, evidence) for note in notes],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": list(unresolved),
        },
    }


def add_unique(values, additions):
    for value in additions:
        if value not in values:
            values.append(value)


def by_entity(record, entity_id):
    return next(p for p in record["participants"] if p["entity_id"] == entity_id)


data = json.loads(DATASET.read_text())
existing = {record["record_id"]: record for record in data["experiments"]}
records = []


# Complete the page-6/page-7 preparation of allenol 3w without duplicating it.
rid = f"{DOC}:page6_partial_procedure_allenol_3w"
rec = copy.deepcopy(existing[rid])
ev6 = page_ev(6)
ev7 = page_ev(7)
add_unique(rec["evidence_ids"], ev7)
rec["participants"].extend([
    participant("ethyl_bromide", "reactant", "EtBr", ev7, smiles="CCBr", amounts=[
        field("volume", qty(4.4, "mL"), ev7),
        field("mass", qty(6.16, "g"), ev7),
        field("amount", qty(56.5, "mmol"), ev7),
    ]),
    participant("magnesium", "reagent", "Mg turnings", ev7, smiles="[Mg]", amounts=[
        field("mass", qty(1.38, "g"), ev7),
        field("amount", qty(57.5, "mmol"), ev7),
    ]),
    participant("grignard", "unspecified_agent", "ethylmagnesium bromide (Grignard reagent prepared in situ)", ev7),
    participant("thf", "solvent", "THF", ev7, smiles="C1CCOC1", amounts=[
        field("volume", qty(60, "mL"), ev7),
    ]),
    participant("aqueous_hcl", "reagent", "aqueous 1 N HCl", ev7),
])
by_entity(rec, "product")["amounts"] = [field("mass", qty(1.252, "g"), ev7)]
rec["steps"] = [
    {
        "step_id": "step_1_dess_martin_oxidation",
        "participant_ids": ["substrate", "dess_martin", "solvent_substrate", "solvent_reagent"],
        "conditions": [
            field("temperature", "r.t.", ev6),
            field("time", "until complete by TLC", ev6),
            field("workup", "quenched and washed with saturated aqueous Na2S2O3 and saturated aqueous NaHCO3; organic extracts dried over MgSO4 and filtered", ev6 + ev7),
        ],
    },
    {
        "step_id": "step_2_grignard_addition",
        "participant_ids": ["ethyl_bromide", "magnesium", "grignard", "thf", "aqueous_hcl", "product"],
        "conditions": [
            field("grignard_addition_temperature", "r.t.", ev7),
            field("reaction_temperature", "reflux", ev7),
            field("time", "until complete by TLC", ev7),
            field("workup", "water quench; adjusted to pH 3 with aqueous 1 N HCl; extracted with Et2O three times", ev7),
            field("extraction_volume_each", qty(50, "mL"), ev7),
            field("purification", "flash chromatography on silica gel; petroleum ether/Et2O 10:1 to 3:1", ev7),
        ],
    },
]
rec["outcomes"] = [
    field("isolated_yield", qty(60, "%"), ev7, ["product"]),
    field("yield_measurement_basis", "isolated product mass after flash chromatography", ev7),
]
rec["notes"] = [fact("The oxidation and in-situ Grignard-addition sequence begins on PDF page 6 and is completed on PDF page 7.", ev6 + ev7)]
rec["review"]["unresolved"] = [
    "No numerical duration is reported for either the Dess-Martin oxidation or the Grignard addition.",
    "The unisolated oxidation intermediate and product connectivity remain machine-unverified.",
    "No SI file was explicitly associated.",
]
records.append(rec)


# Exact three-stage preparation of allenyl sulfonamide 4d (Procedure III).
ev = ev7
participants = [
    participant("allenol_3d", "reactant", "2-methyl-3-(n-heptyl)penta-3,4-dienol 3d", ev, amounts=[
        field("mass", qty(1.690, "g"), ev), field("amount", qty(8.6, "mmol"), ev),
    ]),
    participant("dead", "reagent", "diethyl azodicarboxylate (40% in toluene)", ev, smiles="CCOC(=O)N=NC(=O)OCC", amounts=[
        field("volume", qty(6.6, "mL"), ev), field("amount", qty(15.2, "mmol"), ev), field("reported_solution_strength", qty(40, "%"), ev),
    ]),
    participant("triphenylphosphine", "reagent", "triphenylphosphine", ev, smiles="P(c1ccccc1)(c1ccccc1)c1ccccc1", amounts=[
        field("mass", qty(4.060, "g"), ev), field("amount", qty(15.5, "mmol"), ev),
    ]),
    participant("phthalimide", "reagent", "phthalimide", ev, smiles="O=C1NC(=O)c2ccccc21", amounts=[
        field("mass", qty(1.313, "g"), ev), field("amount", qty(8.9, "mmol"), ev),
    ]),
    participant("thf", "solvent", "anhydrous THF", ev, smiles="C1CCOC1", amounts=[field("volume", qty(40, "mL"), ev)]),
    participant("phthalimide_intermediate", "product", "corresponding phthalimide intermediate", ev, amounts=[field("mass", qty(2.254, "g"), ev)]),
    participant("hydrazine_hydrate", "reagent", "hydrazine hydrate (85% purity)", ev, amounts=[
        field("volume", qty(0.80, "mL"), ev), field("amount", qty(13.9, "mmol"), ev), field("reported_purity", qty(85, "%"), ev),
    ]),
    participant("methanol", "solvent", "dry MeOH", ev, smiles="CO", amounts=[field("volume", qty(30, "mL"), ev)]),
    participant("concentrated_hcl", "reagent", "concentrated HCl", ev, amounts=[field("volume", qty(2.5, "mL"), ev)]),
    participant("aqueous_naoh", "reagent", "aqueous 1 N NaOH", ev),
    participant("crude_amine", "unspecified_agent", "crude amine intermediate", ev),
    participant("triethylamine", "reagent", "triethylamine", ev, smiles="CCN(CC)CC", amounts=[
        field("volume", qty(1.2, "mL"), ev), field("amount", qty(8.4, "mmol"), ev),
    ]),
    participant("tosyl_chloride", "reactant", "tosyl chloride", ev, smiles="Cc1ccc(S(=O)(=O)Cl)cc1", amounts=[
        field("mass", qty(1.541, "g"), ev), field("amount", qty(8.1, "mmol"), ev),
    ]),
    participant("dichloromethane", "solvent", "dichloromethane", ev, smiles="ClCCl", amounts=[field("volume", qty(20, "mL"), ev)]),
    participant("product_4d", "product", "N-(2-methyl-3-(n-heptyl)penta-3,4-dienyl)-p-toluenesulfonamide (4d)", ev,
                smiles="C=C=C(CCCCCCC)C(C)CNS(=O)(=O)c1ccc(C)cc1", amounts=[field("mass", qty(1.801, "g"), ev)]),
]
steps = [
    {
        "step_id": "step_1_mitsunobu_phthalimide",
        "participant_ids": ["allenol_3d", "dead", "triphenylphosphine", "phthalimide", "thf", "phthalimide_intermediate"],
        "conditions": [
            field("initial_temperature", qty(0, "°C"), ev), field("warm_to", "r.t.", ev), field("time", "overnight", ev),
            field("operation", "DEAD was added dropwise with ice-bath cooling; after warming overnight the solvent was removed, ether was added, solids were filtered, and the filtrate was evaporated", ev),
            field("purification", "flash chromatography on silica gel", ev),
        ],
    },
    {
        "step_id": "step_2_hydrazinolysis",
        "participant_ids": ["phthalimide_intermediate", "hydrazine_hydrate", "methanol", "concentrated_hcl", "aqueous_naoh", "crude_amine"],
        "conditions": [
            field("temperature", "reflux", ev), field("time", qty(2, "h"), ev),
            field("workup", "concentrated HCl was added under ice-bath cooling; precipitate removed; filtrate adjusted to pH 13 with aqueous 1 N NaOH; extracted with Et2O three times; dried over MgSO4 and evaporated", ev),
            field("extraction_volume_each", qty(50, "mL"), ev),
        ],
    },
    {
        "step_id": "step_3_tosylation",
        "participant_ids": ["crude_amine", "triethylamine", "tosyl_chloride", "dichloromethane", "product_4d"],
        "conditions": [
            field("initial_temperature", qty(0, "°C"), ev), field("warm_to", "r.t.", ev), field("time", "overnight", ev),
            field("operation", "tosyl chloride was added in one portion with ice-bath cooling", ev),
            field("purification", "solvent removal followed by flash chromatography on silica gel", ev),
        ],
    },
]
records.append(make_record(
    "page7_procedure3_allenyl_amide_4d", "reported_experiment", ev, participants, steps,
    [
        field("final_step_isolated_yield", qty(75, "%"), ev, ["product_4d"]),
        field("overall_isolated_yield_three_steps", qty(60, "%"), ev, ["product_4d"]),
        field("yield_measurement_basis", "isolated after flash chromatography", ev),
    ],
    unresolved=(
        "No numerical duration is reported for the two overnight stages.",
        "The phthalimide and crude amine intermediate structures remain machine-unverified.",
        "No SI file was explicitly associated.",
    ),
))


def procedure_record(rid, base_label, base_smiles, solvent_label, solvent_smiles, temperature, scope):
    participants = [
        participant("allenyl_amide", "reactant", "3,4-allenyl amide 4", ev, amounts=[field("amount", qty(0.3, "mmol"), ev)]),
        participant("organic_halide", "reactant", scope, ev, amounts=[field("amount", qty(0.45, "mmol"), ev)]),
        participant("base", "reagent", base_label, ev, smiles=base_smiles, amounts=[field("amount", qty(1.2, "mmol"), ev)]),
        participant("catalyst", "catalyst", "Pd(PPh3)4", ev, amounts=[field("catalyst_loading", qty(5, "mol%"), ev)]),
        participant("solvent", "solvent", solvent_label, ev, smiles=solvent_smiles, amounts=[field("volume", qty(2, "mL"), ev)]),
        participant("product", "product", "pure coupling-cyclization product(s)", ev),
    ]
    return make_record(
        rid, "general_scheme", ev, participants,
        [{
            "step_id": "step_1",
            "participant_ids": [p["entity_id"] for p in participants],
            "conditions": [
                field("temperature", qty(temperature, "°C"), ev),
                field("time", "until complete by TLC", ev),
                field("workup", "diluted with Et2O; washed with brine three times; dried over Na2SO4; evaporated", ev),
                field("brine_wash_volume_each", qty(10, "mL"), ev),
                field("purification", "flash chromatography on silica gel; petroleum ether/Et2O 5:1", ev),
            ],
        }],
        [],
        notes=("This is a generic experimental procedure and is not counted as an additional substrate-scope result.",),
        unresolved=(
            "The generic procedure gives no fixed reaction time or numerical product yield.",
            "Generic substrate/product structures cannot be fully assigned.",
            "No SI file was explicitly associated.",
        ),
    )


records.append(procedure_record(
    "page7_general_procedure4_condition_a", "K2CO3", "[K+].[K+].[O-]C([O-])=O", "DMF", "CN(C)C=O", 70, "organic halide 6",
))
records.append(procedure_record(
    "page7_general_procedure5_condition_b", "NaOH", "[Na+].[OH-]", "toluene", "Cc1ccccc1", 80, "aryl or vinyl halide 6",
))


# Enrich Table 2 entry 3 with the exact 4c/iodobenzene preparation and split 8ca isomers.
rid = f"{DOC}:table2_entry_3"
rec = copy.deepcopy(existing[rid])
add_unique(rec["evidence_ids"], ev7)
by_entity(rec, "substrate")["amounts"].extend([
    field("mass", qty(0.086, "g"), ev7), field("reaction_scale", qty(0.32, "mmol"), ev7),
])
by_entity(rec, "halide")["amounts"].extend([
    field("volume", qty(51, "uL"), ev7), field("mass", qty(0.093, "g"), ev7), field("reaction_scale", qty(0.46, "mmol"), ev7),
])
by_entity(rec, "solvent")["amounts"].append(field("volume", qty(2, "mL"), ev7))
by_entity(rec, "product7")["name"] = fact("5-benzyl-3,4-dimethyl-1-(p-toluenesulfonyl)-2,3-dihydro-1H-pyrrole", ev7)
rec["participants"].extend([
    participant("product8_trans", "product", "trans-8ca", ev7,
                name="trans-3,4-dimethyl-2-methylene-3-phenyl-1-(p-toluenesulfonyl)pyrrolidine",
                amounts=[field("mass", qty(0.009, "g"), ev7)]),
    participant("product8_cis", "product", "cis-8ca", ev7,
                name="cis-3,4-dimethyl-2-methylene-3-phenyl-1-(p-toluenesulfonyl)pyrrolidine",
                amounts=[field("mass", qty(0.003, "g"), ev7)]),
])
by_entity(rec, "product7")["amounts"] = [field("mass", qty(0.073, "g"), ev7)]
add_unique(rec["steps"][0]["participant_ids"], ["product8_trans", "product8_cis"])
rec["steps"][0]["conditions"].extend([
    field("workup", "after TLC completion, diluted with Et2O; washed with brine three times; dried over Na2SO4; evaporated", ev7),
    field("brine_wash_volume_each", qty(10, "mL"), ev7),
    field("purification", "flash chromatography on silica gel; petroleum ether/Et2O 5:1", ev7),
])
rec["outcomes"].extend([
    field("isolated_yield_trans_8ca", qty(8.5, "%"), ev7, ["product8_trans"]),
    field("isolated_yield_cis_8ca", qty(2.4, "%"), ev7, ["product8_cis"]),
])
rec["notes"] = [fact("The table reports 8ca as 11% total, while the exact procedure reports 8.5% trans-8ca and 2.4% cis-8ca; both source presentations are retained.", ev7 + page_ev(3))]
rec["review"]["unresolved"] = [
    "Table 2 gives a nominal 0.30 mmol substrate scale, while the exact example uses 0.32 mmol; both are retained.",
    "Substrate and product structures and stereochemistry remain machine-unverified.",
    "No SI file was explicitly associated.",
]
records.append(rec)


# Enrich the repeated Conditions-B 4k result with its exact preparation and page-8 identity.
rid = f"{DOC}:table4_entry_15"
rec = copy.deepcopy(existing[rid])
add_unique(rec["evidence_ids"], ev7 + page_ev(8))
by_entity(rec, "substrate")["amounts"].extend([
    field("mass", qty(0.060, "g"), ev7), field("reaction_scale", qty(0.20, "mmol"), ev7),
])
by_entity(rec, "halide")["amounts"].extend([
    field("volume", qty(34, "uL"), ev7), field("mass", qty(0.062, "g"), ev7), field("reaction_scale", qty(0.30, "mmol"), ev7),
])
by_entity(rec, "base")["amounts"].extend([
    field("mass", qty(0.033, "g"), ev7), field("reaction_scale", qty(0.83, "mmol"), ev7),
])
by_entity(rec, "catalyst")["amounts"].append(field("mass", qty(0.013, "g"), ev7))
by_entity(rec, "solvent")["amounts"].append(field("volume", qty(2, "mL"), ev7))
by_entity(rec, "product10")["name"] = fact("cis-2-(n-butyl)-5-methyl-3-phenyl-1-(p-toluenesulfonyl)-1,2,5,6-tetrahydropyridine", ev7)
by_entity(rec, "product10")["amounts"] = [field("mass", qty(0.031, "g"), ev7)]
by_entity(rec, "product11")["name"] = fact("trans-3-methyl-2-(1'-phenylhex-1'(Z)-enyl)-1-(p-toluenesulfonyl)azetidine", page_ev(8))
by_entity(rec, "product11")["amounts"] = [field("mass", qty(0.009, "g"), ev7)]
rec["steps"][0]["conditions"].extend([
    field("workup", "after TLC completion, diluted with Et2O; washed with brine three times; dried over Na2SO4; evaporated", ev7),
    field("brine_wash_volume_each", qty(10, "mL"), ev7),
    field("purification", "flash chromatography on silica gel; petroleum ether/Et2O 5:1", ev7),
])
rec["outcomes"].append(field("yield_measurement_basis", "isolated after flash chromatography", ev7))
rec["notes"].append(fact("The page-8 11ka characterization is a continuation of the page-7 exact reaction and is not a separate experiment.", page_ev(8)))
rec["review"]["unresolved"] = [
    "Table 4/Table 5 time conflict (100 h versus shared 48 h arrow) requires review; the repeated result was merged, not duplicated.",
    "Table 4 gives a nominal 0.30 mmol substrate scale, while the exact example uses 0.20 mmol; both are retained.",
    "Product connectivity and stereochemical encoding remain machine-unverified.",
    "No SI file was explicitly associated.",
]
records.append(rec)


# Figure 4 is structural evidence for the already extracted Scheme 7 product 15.
rid = f"{DOC}:page6_scheme7_4q_with_6r"
rec = copy.deepcopy(existing[rid])
add_unique(rec["evidence_ids"], ev7)
rec["outcomes"].append(field("major_stereoisomer_structure_assignment", "established by single-crystal X-ray diffraction (Figure 4)", ev7, ["product"]))
rec["notes"].append(fact("Figure 4 is a molecular-structure determination for product 15, not a separate synthetic experiment.", ev7))
rec["review"]["unresolved"] = [
    "Conditions B do not specify reaction time, scale, workup, purification, or yield basis for Scheme 7.",
    "The candidate product structure and stereochemistry remain machine-unverified despite the reported X-ray assignment.",
    "No SI file was explicitly associated.",
]
records.append(rec)


coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 7,
            "state": "attempted",
            "regions": [
                {
                    "region": "Figure 4, upper-left",
                    "finding": "Single-crystal molecular structure of the major stereoisomer of product 15; merged as structural evidence for the existing Scheme 7 experiment, not counted as a new reaction.",
                    "evidence_ids": [f"{DOC}:page7:image"],
                },
                {
                    "region": "left column, continuation of the 3w preparation",
                    "finding": "Completes the page-6 Dess-Martin/Grignard sequence with EtBr/Mg/THF, reflux, workup, chromatography, 1.252 g product, and 60% isolated yield; merged into the existing partial record.",
                    "evidence_ids": [f"{DOC}:page7:image"],
                },
                {
                    "region": "left column, Procedure III",
                    "finding": "Exact three-stage preparation of allenyl sulfonamide 4d through phthalimide formation, hydrazinolysis, and tosylation; 75% final-step and 60% overall isolated yields.",
                    "evidence_ids": [f"{DOC}:page7:image"],
                },
                {
                    "region": "right column, Procedure IV and 4c example",
                    "finding": "Generic Conditions-A coupling-cyclization procedure plus an exact 4c/iodobenzene experiment giving 7ca and separated trans-/cis-8ca; the exact result was merged into Table 2 entry 3.",
                    "evidence_ids": [f"{DOC}:page7:image"],
                },
                {
                    "region": "right column, Procedure V and 4k example",
                    "finding": "Generic Conditions-B procedure plus the exact 4k/iodobenzene preparation giving 10ka and 11ka; merged into the repeated Table 4 entry 15 record.",
                    "evidence_ids": [f"{DOC}:page7:image"],
                },
            ],
            "record_ids": [
                f"{DOC}:page6_scheme7_4q_with_6r",
                f"{DOC}:page6_partial_procedure_allenol_3w",
                f"{DOC}:page7_procedure3_allenyl_amide_4d",
                f"{DOC}:page7_general_procedure4_condition_a",
                f"{DOC}:table2_entry_3",
                f"{DOC}:page7_general_procedure5_condition_b",
                f"{DOC}:table4_entry_15",
            ],
            "unresolved": [
                "The oxidation and Grignard stages of the 3w sequence have no numerical reaction times.",
                "The exact examples and table footnotes use differing nominal scales for 4c and 4k; all printed values are retained.",
                "Candidate structures and stereochemical encoding remain unverified.",
            ],
        },
        {
            "page": 8,
            "state": "attempted",
            "regions": [
                {
                    "region": "upper-left, trans-11ka characterization",
                    "finding": "Continuation of the product characterization for 11ka from the page-7 4k experiment; linked to the existing Table 4 entry 15 record and not counted as a new experiment.",
                    "evidence_ids": [f"{DOC}:page8:image"],
                },
                {
                    "region": "acknowledgements and references",
                    "finding": "No new reaction experiment. Reference citations and crystallographic-data notices were not used to backfill missing experimental details or infer SI association.",
                    "evidence_ids": [f"{DOC}:page8:image"],
                },
            ],
            "record_ids": [f"{DOC}:table4_entry_15"],
            "unresolved": [
                "The page provides characterization but no additional reaction conditions or outcomes.",
                "No supporting-information file was explicitly provided or associated.",
            ],
        },
    ],
}


records_path = HERE / "pages_0007_0008_records.json"
coverage_path = RUN / "coverage" / "pages_0007_0008.json"
records_path.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
coverage_path.parent.mkdir(parents=True, exist_ok=True)
coverage_path.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({
    "submitted_records": len(records),
    "new_record_ids": [r["record_id"] for r in records if r["record_id"] not in existing],
    "updated_record_ids": [r["record_id"] for r in records if r["record_id"] in existing],
    "records_path": str(records_path),
    "coverage_path": str(coverage_path),
}, ensure_ascii=False, indent=2))
