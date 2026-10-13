#!/usr/bin/env python3
"""Build evidence-linked machine records for PDF pages 7-10."""

import copy
import json
from pathlib import Path


BASE = Path(__file__).resolve().parents[2]
DATASET = BASE / "current" / "dataset.json"
DOC = "doc_04c178582cab751e"


def ev(page):
    return [f"{DOC}:page{page}:text", f"{DOC}:page{page}:image"]


def unique(values):
    return list(dict.fromkeys(values))


def fact(value, evidence):
    return {
        "value": value,
        "evidence_ids": unique(evidence) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def field(name, value, evidence, targets=None):
    item = {"name": name, "fact": fact(value, evidence)}
    if targets:
        item["target_entity_ids"] = list(targets)
    return item


def qty(name, number, unit, evidence):
    return field(name, {"number": number, "unit": unit}, evidence)


SMILES = {
    "platinum(II) chloride": "Cl[Pt]Cl",
    "toluene": "Cc1ccccc1",
    "tetrahydrofuran": "C1CCOC1",
    "diethyl ether": "CCOCC",
    "n-butyllithium": "[Li+].[CH2-]CCC",
    "copper(I) bromide": "Br[Cu]",
    "3-chloronon-1-yne": "C#CC(Cl)CCCCCC",
    "1-ethyl-1H-indole-2-carbaldehyde": "CCn1c(C=O)cc2ccccc21",
    "1-(1-ethyl-1H-indol-2-yl)-4-phenylbuta-2,3-dien-1-ol":
        "CCn1c(C(O)C=C=Cc2ccccc2)cc2ccccc21",
}


def participant(entity_id, role, evidence, *, label=None, name=None, amounts=None, smiles=None):
    if smiles is None and name in SMILES:
        smiles = SMILES[name]
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


def record(rid, kind, evidence, participants, steps, outcomes, notes=None, unresolved=None):
    return {
        "record_id": f"{DOC}:{rid}",
        "document_id": DOC,
        "source_reaction_id": rid,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": unique(evidence),
        "participants": participants,
        "steps": steps,
        "outcomes": outcomes,
        "notes": [fact(value, note_ev) for value, note_ev in (notes or [])],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved or [
                "Machine extraction requires source-level chemical review.",
                "Supporting Information was mentioned but was not supplied or explicitly associated.",
            ],
        },
    }


dataset = json.loads(DATASET.read_text())
existing = {item["record_id"]: item for item in dataset["experiments"]}
records = []


# Page 7 begins with characterization continuing from the page-6 preparation of 3j.
prep_3j_id = f"{DOC}:prep_3j"
prep_3j = copy.deepcopy(existing[prep_3j_id])
prep_3j["evidence_ids"] = unique(prep_3j["evidence_ids"] + ev(7))
prep_3j["notes"].append(fact(
    "IR, EI-MS, and elemental-analysis characterization of product 3j continues at the top of PDF page 7.",
    ev(7),
))
records.append(prep_3j)


# Page 7, Section 5: two-stage preparation of allenol 3e.
p7 = ev(7)
records.append(record(
    "prep_3e",
    "reported_experiment",
    p7,
    participants=[
        participant("prep_3e_8e", "reactant", p7, label="8e", name="protected propargylic substrate 8e",
                    amounts=[qty("mass", 1.4657, "g", p7), qty("amount", 10, "mmol", p7)]),
        participant("prep_3e_n_buli", "reagent", p7, name="n-butyllithium",
                    amounts=[qty("solution_volume", 4.0, "mL", p7), qty("concentration", 2.5, "M", p7), qty("amount", 10, "mmol", p7)]),
        participant("prep_3e_thf", "solvent", p7, name="tetrahydrofuran",
                    amounts=[qty("initial_volume", 25, "mL", p7), qty("aldehyde_solution_volume", 5, "mL", p7)]),
        participant("prep_3e_aldehyde", "reactant", p7, name="1-ethyl-1H-indole-2-carbaldehyde",
                    amounts=[qty("mass", 1.7314, "g", p7), qty("amount", 10, "mmol", p7)]),
        participant("prep_3e_9e", "unspecified_agent", p7, label="9e", name="unpurified intermediate 9e"),
        participant("prep_3e_cubr", "reagent", p7, name="copper(I) bromide",
                    amounts=[qty("mass", 0.7251, "g", p7), qty("amount", 5, "mmol", p7)]),
        participant("prep_3e_etmgbr", "reagent", p7, name="ethylmagnesium bromide",
                    amounts=[qty("solution_volume", 50, "mL", p7), qty("concentration", 1, "M", p7), qty("amount", 50, "mmol", p7)]),
        participant("prep_3e_ether", "solvent", p7, name="diethyl ether",
                    amounts=[qty("initial_volume", 50, "mL", p7), qty("reagent_solution_volume", 50, "mL", p7)]),
        participant("prep_3e_product", "product", p7, label="3e",
                    name="1-(1-ethyl-1H-indol-2-yl)-4-phenylbuta-2,3-dien-1-ol",
                    amounts=[qty("isolated_mass", 0.3225, "g", p7)]),
    ],
    steps=[
        {
            "step_id": "alkynyl_lithium_addition",
            "participant_ids": ["prep_3e_8e", "prep_3e_n_buli", "prep_3e_thf", "prep_3e_aldehyde", "prep_3e_9e"],
            "conditions": [
                field("temperature", {"number": -78, "unit": "°C"}, p7),
                field("n_buli_addition_time", {"number": 10, "unit": "min"}, p7),
                field("time_after_n_buli_addition", {"number": 40, "unit": "min"}, p7),
                field("aldehyde_addition_time", {"number": 10, "unit": "min"}, p7),
                field("warm_to", "r.t.", p7),
                field("warm_up_and_reaction_time", {"number": 10, "unit": "h"}, p7),
                field("atmosphere", "N2", p7),
                field("workup", "saturated aqueous NH4Cl (20 mL) quench; diethyl ether extraction (25 mL x3); Na2SO4 drying; filtration and concentration", p7),
                field("purification", "silica-gel chromatography, petroleum ether/ethyl acetate 10:1; intermediate 9e used in the next step", p7),
            ],
        },
        {
            "step_id": "copper_assisted_ethylmagnesium_bromide_reduction",
            "participant_ids": ["prep_3e_9e", "prep_3e_cubr", "prep_3e_etmgbr", "prep_3e_ether", "prep_3e_product"],
            "conditions": [
                field("temperature", {"number": -30, "unit": "°C"}, p7),
                field("addition_time", {"number": 40, "unit": "min"}, p7),
                field("time", {"number": 12, "unit": "h"}, p7),
                field("atmosphere", "N2", p7),
                field("operation", "reaction monitored by TLC", p7),
                field("workup", "saturated ammonium chloride (30 mL) quench; ether extraction (3 x 30 mL); water wash; Na2SO4 drying; filtration and evaporation", p7),
                field("purification", "silica-gel chromatography, petroleum ether/ethyl acetate 20:1 to 10:1", p7),
            ],
        },
    ],
    outcomes=[
        field("combined_isolated_yield", {"number": 11, "unit": "%"}, p7, ["prep_3e_product"]),
        field("yield_measurement_basis", "isolated after silica-gel chromatography over the two-stage sequence", p7, ["prep_3e_product"]),
    ],
    notes=[
        ("The candidate SMILES for 3e was transcribed from the fully specified structure in the page-7 reaction drawing; it remains machine-unverified.", p7),
        ("Intermediate 9e was used in the next step and has no separately reported yield.", p7),
    ],
    unresolved=[
        "The structure and stereochemical state of intermediate 9e were not encoded as a verified SMILES.",
        "Supporting Information was not supplied or explicitly associated.",
    ],
))


# Page 7, Section 6: one-pot preparation of allenol 3l.
records.append(record(
    "prep_3l",
    "reported_experiment",
    p7,
    participants=[
        participant("prep_3l_chloroalkyne", "reactant", p7, name="3-chloronon-1-yne",
                    amounts=[qty("mass", 1.1902, "g", p7), qty("amount", 7.5, "mmol", p7)]),
        participant("prep_3l_n_buli", "reagent", p7, name="n-butyllithium",
                    amounts=[qty("solution_volume", 3, "mL", p7), qty("concentration", 2.5, "M", p7), qty("amount", 7.5, "mmol", p7)]),
        participant("prep_3l_aldehyde", "reactant", p7, name="1-ethyl-1H-indole-2-carbaldehyde",
                    amounts=[qty("mass", 1.2995, "g", p7), qty("amount", 7.5, "mmol", p7)]),
        participant("prep_3l_cucn", "reagent", p7, name="copper(I) cyanide",
                    amounts=[qty("mass", 34.0, "mg", p7), qty("amount", 0.38, "mmol", p7)]),
        participant("prep_3l_memgbr", "reagent", p7, name="methylmagnesium bromide",
                    amounts=[qty("solution_volume", 7.5, "mL", p7), qty("concentration", 3, "M", p7), qty("amount", 22.5, "mmol", p7)]),
        participant("prep_3l_ether", "solvent", p7, name="diethyl ether",
                    amounts=[qty("initial_volume", 25, "mL", p7), qty("aldehyde_solution_volume", 5, "mL", p7), qty("grignard_solution_volume", 7.5, "mL", p7)]),
        participant("prep_3l_product", "product", p7, label="3l",
                    name="1-(1-ethyl-1H-indol-2-yl)-2-methyldeca-2,3-dien-1-ol",
                    amounts=[qty("isolated_mass", 0.4652, "g", p7)]),
    ],
    steps=[{
        "step_id": "sequential_lithiation_addition_and_copper_grignard_reaction",
        "participant_ids": ["prep_3l_chloroalkyne", "prep_3l_n_buli", "prep_3l_aldehyde", "prep_3l_cucn", "prep_3l_memgbr", "prep_3l_ether", "prep_3l_product"],
        "conditions": [
            field("initial_temperature", {"number": -78, "unit": "°C"}, p7),
            field("n_buli_addition_time", {"number": 10, "unit": "min"}, p7),
            field("time_after_n_buli_addition", {"number": 40, "unit": "min"}, p7),
            field("aldehyde_addition_time", {"number": 5, "unit": "min"}, p7),
            field("warm_to_minus_40_time", {"number": 1.2, "unit": "h"}, p7),
            field("copper_cyanide_addition_temperature", {"number": -60, "unit": "°C"}, p7),
            field("methylmagnesium_bromide_addition_temperature", {"number": -60, "unit": "°C"}, p7),
            field("methylmagnesium_bromide_addition_time", {"number": 15, "unit": "min"}, p7),
            field("reaction_temperature", {"number": -30, "unit": "°C"}, p7),
            field("reaction_time", {"number": 21, "unit": "h"}, p7),
            field("atmosphere", "N2", p7),
            field("operation", "reaction monitored by TLC", p7),
            field("workup", "saturated ammonium chloride (30 mL) quench; ether extraction (3 x 30 mL); water wash; Na2SO4 drying; filtration and evaporation", p7),
            field("purification", "silica-gel chromatography, petroleum ether/ethyl acetate 20:1", p7),
        ],
    }],
    outcomes=[
        field("isolated_yield", {"number": 20, "unit": "%"}, p7, ["prep_3l_product"]),
        field("yield_measurement_basis", "isolated after silica-gel chromatography", p7, ["prep_3l_product"]),
    ],
    unresolved=[
        "The complex product structure is represented by its fully specified source name but has no machine-verified SMILES.",
        "Supporting Information was not supplied or explicitly associated.",
    ],
))


def detailed_cyclization(
    rid, kind, detail_pages, substrate_label, substrate_name, substrate_mass_mg, substrate_mmol,
    catalyst_mass_mg, catalyst_mmol, solvent_ml, time_h, product_label, product_name,
    product_mass_mg, yield_pct, eluent, *, extra_outcomes=None, extra_notes=None,
    extra_unresolved=None, include_table_page=True,
):
    detail_ev = []
    for page in detail_pages:
        detail_ev += ev(page)
    context_ev = ev(7) if 7 not in detail_pages else []
    table_ev = ev(2) if include_table_page else []
    evidence = unique(table_ev + context_ev + detail_ev)
    prefix = rid
    sub_id = f"{prefix}_substrate"
    cat_id = f"{prefix}_ptcl2"
    solv_id = f"{prefix}_toluene"
    prod_id = f"{prefix}_product"
    outcomes = [
        field("isolated_yield", {"number": yield_pct, "unit": "%"}, detail_ev, [prod_id]),
        field("yield_measurement_basis", "isolated after silica-gel column chromatography", unique(context_ev + detail_ev), [prod_id]),
    ]
    outcomes.extend(extra_outcomes or [])
    unresolved = [
        "Complex substrate and product structures are represented by source labels/names with null SMILES and remain machine-unverified.",
        "Supporting Information was not supplied or explicitly associated.",
    ]
    unresolved.extend(extra_unresolved or [])
    records.append(record(
        rid,
        kind,
        evidence,
        participants=[
            participant(sub_id, "reactant", unique(table_ev + detail_ev), label=substrate_label, name=substrate_name,
                        amounts=[qty("mass", substrate_mass_mg, "mg", detail_ev), qty("amount", substrate_mmol, "mmol", detail_ev)]),
            participant(cat_id, "catalyst", detail_ev, name="platinum(II) chloride",
                        amounts=[qty("mass", catalyst_mass_mg, "mg", detail_ev), qty("amount", catalyst_mmol, "mmol", detail_ev)]),
            participant(solv_id, "solvent", detail_ev, name="toluene",
                        amounts=[qty("volume", solvent_ml, "mL", detail_ev)]),
            participant(prod_id, "product", unique(table_ev + detail_ev), label=product_label, name=product_name,
                        amounts=[qty("isolated_mass", product_mass_mg, "mg", detail_ev)]),
        ],
        steps=[{
            "step_id": "ptcl2_catalyzed_cyclization",
            "participant_ids": [sub_id, cat_id, solv_id, prod_id],
            "conditions": [
                field("temperature", "r.t.", detail_ev),
                field("time", {"number": time_h, "unit": "h"}, detail_ev),
                field("atmosphere", "N2", unique(context_ev + detail_ev)),
                field("operation", "stirred and monitored by TLC according to the Section 7 typical procedure", unique(context_ev + detail_ev)),
                field("workup", "solvent evaporation", unique(context_ev + detail_ev)),
                field("purification", f"silica-gel column chromatography, petroleum ether/ethyl acetate {eluent}", unique(context_ev + detail_ev)),
            ],
        }],
        outcomes=outcomes,
        notes=extra_notes,
        unresolved=unresolved,
    ))


# Pages 7-9: detailed isolated carbazole preparations enrich existing scope rows.
detailed_cyclization(
    "table1_entry5", "substrate_scope_entry", [7], "1e",
    "1-(1-ethyl-1H-indol-2-yl)-2-(p-tolyl)buta-2,3-dien-1-ol",
    92.5, 0.31, 4.1, 0.015, 1.5, 16, "2e", "9-ethyl-2-p-tolyl-9H-carbazole",
    60.2, 69, "100:1",
)
detailed_cyclization(
    "table1_entry6", "substrate_scope_entry", [8], "1f",
    "1-(1-ethyl-1H-indol-2-yl)-2-(4-methoxyphenyl)buta-2,3-dien-1-ol",
    320.0, 1.0, 14.0, 0.05, 5.0, 15, "2f", "9-ethyl-2-(4-methoxyphenyl)-9H-carbazole",
    230.1, 76, "40:1",
)
detailed_cyclization(
    "table1_entry10", "substrate_scope_entry", [8], "1j",
    "2-(ethoxymethyl)-1-(1-ethyl-1H-indol-2-yl)buta-2,3-dien-1-ol",
    82.0, 0.3, 4.1, 0.015, 1.5, 12, "2j", "2-(ethoxymethyl)-9-ethyl-9H-carbazole",
    64.5, 84, "20:1",
)
detailed_cyclization(
    "table1_entry11", "substrate_scope_entry", [8], "1k",
    "2-((1-ethyl-1H-indol-2-yl)(hydroxy)methyl)buta-2,3-dienyl acetate",
    85.1, 0.3, 4.1, 0.015, 1.5, 24, "2k", "2-acetoxymethyl-9-ethyl-9H-carbazole",
    64.7, 81, "10:1",
)
detailed_cyclization(
    "table1_entry12", "substrate_scope_entry", [8], "1l",
    "2-((1-ethyl-1H-indol-2-yl)(hydroxy)methyl)buta-2,3-dienyl methyl carbonate",
    151.1, 0.5, 6.1, 0.023, 2.5, 13, "2l", "2-(methoxycarbonyloxy)methyl-9-ethyl-9H-carbazole",
    109.0, 77, "20:1",
    extra_notes=[
        ("The compound heading and Table 1 identify 1l to 2l, but the page-8 body text prints 1k and 2k; the source inconsistency is preserved rather than silently treated as resolved.", ev(2) + ev(8)),
    ],
    extra_unresolved=[
        "Source-label conflict on page 8: heading/Table 1 indicate 1l/2l, whereas the detailed sentence prints 1k/2k; manual source review is required.",
    ],
)
detailed_cyclization(
    "table1_entry13", "substrate_scope_entry", [8], "1m",
    "1-(1-ethyl-4-methyl-1H-indol-2-yl)-2-butylbuta-2,3-dien-1-ol",
    172.5, 0.6, 8.0, 0.03, 3.0, 18, "2m", "9-ethyl-2-butyl-5-methyl-9H-carbazole",
    124.9, 77, "80:1",
)
detailed_cyclization(
    "table1_entry17", "substrate_scope_entry", [8], "1q",
    "1-(1-ethyl-1H-indol-2-yl)-2-(benzyloxy)buta-2,3-dien-1-ol",
    64.5, 0.2, 3.0, 0.01, 1.0, 11, "2q", "2-(benzyloxy)-9-ethyl-9H-carbazole",
    36.5, 60, "20:1",
)
detailed_cyclization(
    "table1_entry21", "substrate_scope_entry", [8], "1u",
    "1-(1-(4-methoxybenzyl)-1H-indol-2-yl)-2-phenylbuta-2,3-dien-1-ol",
    912.4, 2.39, 40.1, 0.15, 8.0, 16, "2u", "9-(4-methoxybenzyl)-2-phenyl-9H-carbazole",
    623.3, 72, "40:1",
)
detailed_cyclization(
    "table2_entry3", "substrate_scope_entry", [8, 9], "3c",
    "1-(1-ethyl-1H-indol-2-yl)-5-methylhexa-2,3-dien-1-ol",
    78.0, 0.31, 4.1, 0.015, 1.5, 20, "4c", "9-ethyl-4-isopropyl-9H-carbazole",
    27.2, 38, "100:1",
)
detailed_cyclization(
    "table2_entry5", "substrate_scope_entry", [9], "3e",
    "1-(1-ethyl-1H-indol-2-yl)-4-phenylbuta-2,3-dien-1-ol",
    84.1, 0.29, 4.2, 0.015, 1.5, 14, "4e", "9-ethyl-4-phenyl-9H-carbazole",
    72.2, 92, "20:1",
)


# The labeled 3f-D batch is the separate mechanistic experiment already recorded from page 3,
# not the unlabeled Table 2 entry 6 (75%).
isotope_extra = [
    field("deuterium_incorporation", {"number": 94, "unit": "%"}, ev(3) + ev(9), ["isotope_cyclization_3f_D_to_4f_D_product"]),
    field("deuterium_position", "3-position of the newly formed phenyl ring", ev(3) + ev(9), ["isotope_cyclization_3f_D_to_4f_D_product"]),
]
detailed_cyclization(
    "isotope_cyclization_3f_D_to_4f_D", "reported_experiment", [9], "3f-D",
    "1-(1-ethyl-5-methyl-1H-indol-2-yl)-4-deuterodeca-2,3-dien-1-ol (98% D)",
    93.2, 0.3, 4.2, 0.015, 2.0, 2, "4f-D", "3-deutero-9-ethyl-4-hexyl-6-methyl-9H-carbazole",
    75.2, 86, "100:1", extra_outcomes=isotope_extra, include_table_page=False,
    extra_notes=[
        ("This 86%, 94% D batch is the isotope-labeling experiment also described on page 3 and is distinct from unlabeled Table 2 entry 6 (75%).", ev(3) + ev(9)),
    ],
)
records[-1]["evidence_ids"] = unique(ev(3) + records[-1]["evidence_ids"])
detailed_cyclization(
    "table2_entry8", "substrate_scope_entry", [9], "3h",
    "1-(1-ethyl-4-methyl-1H-indol-2-yl)penta-2,3-dien-1-ol",
    73.0, 0.30, 4.1, 0.015, 1.5, 20, "4h", "9-ethyl-4,5-dimethyl-9H-carbazole",
    57.7, 85, "80:1",
)
detailed_cyclization(
    "table2_entry9", "substrate_scope_entry", [9], "3i",
    "1-(1-ethyl-4-methyl-1H-indol-2-yl)deca-2,3-dien-1-ol",
    62.1, 0.20, 2.8, 0.01, 1.0, 12, "4i", "9-ethyl-4-hexyl-5-methyl-9H-carbazole",
    47.5, 81, "80:1",
)
detailed_cyclization(
    "table2_entry10", "substrate_scope_entry", [9], "3j",
    "1-(5-bromo-1-ethyl-1H-indol-2-yl)deca-2,3-dien-1-ol",
    75.0, 0.20, 2.9, 0.011, 1.0, 16, "4j", "3-bromo-9-ethyl-5-hexyl-9H-carbazole",
    53.6, 75, "40:1",
)
detailed_cyclization(
    "table2_entry12", "substrate_scope_entry", [9], "3l",
    "1-(1-ethyl-1H-indol-2-yl)-2-methyldeca-2,3-dien-1-ol",
    61.0, 0.20, 3.1, 0.012, 1.0, 21, "4l", "9-ethyl-4-hexyl-2-methyl-9H-carbazole",
    44.7, 78, "80:1",
)


out = Path(__file__).with_name("records_pages_0007_0010.json")
out.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")


page_records = {
    7: [
        f"{DOC}:prep_3j", f"{DOC}:prep_3e", f"{DOC}:prep_3l", f"{DOC}:table1_entry5",
    ],
    8: [
        f"{DOC}:table1_entry6", f"{DOC}:table1_entry10", f"{DOC}:table1_entry11",
        f"{DOC}:table1_entry12", f"{DOC}:table1_entry13", f"{DOC}:table1_entry17",
        f"{DOC}:table1_entry21", f"{DOC}:table2_entry3",
    ],
    9: [
        f"{DOC}:table2_entry3", f"{DOC}:table2_entry5",
        f"{DOC}:isotope_cyclization_3f_D_to_4f_D", f"{DOC}:table2_entry8",
        f"{DOC}:table2_entry9", f"{DOC}:table2_entry10", f"{DOC}:table2_entry12",
    ],
    10: [],
}

coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 7,
            "state": "attempted",
            "regions": [
                {
                    "region": "page 7 upper-left, continuation above Section 5",
                    "finding": "Characterization continuation for allenol 3j prepared on page 6; linked to the existing preparation record, not counted as a new experiment.",
                    "evidence_ids": ev(7),
                },
                {
                    "region": "page 7 left column and lower reaction drawing, Section 5",
                    "finding": "Two-stage preparation of allenol 3e via unpurified 9e, CuBr, and EtMgBr; 0.3225 g product, 11% combined isolated yield.",
                    "evidence_ids": ev(7),
                },
                {
                    "region": "page 7 upper-right, Section 6",
                    "finding": "Sequential lithiation/addition/CuCN-MeMgBr preparation of allenol 3l; 0.4652 g, 20% isolated yield.",
                    "evidence_ids": ev(7),
                },
                {
                    "region": "page 7 lower-right, Section 7 item 1",
                    "finding": "Typical PtCl2 cyclization batch for 1e to 2e under N2; merged into existing Table 1 entry 5 with exact charges, workup, purification, mass, and yield.",
                    "evidence_ids": ev(7),
                },
            ],
            "record_ids": page_records[7],
            "unresolved": [
                "Supporting Information was not supplied or associated.",
                "Intermediate 9e lacks a separate yield and verified structure record.",
            ],
        },
        {
            "page": 8,
            "state": "attempted",
            "regions": [
                {
                    "region": "page 8 left column, Section 7 items 2-5",
                    "finding": "Detailed PtCl2 cyclization batches for 1f, 1j, 1k, and nominal 1l to products 2f, 2j, 2k, and 2l; merged with existing Table 1 entries.",
                    "evidence_ids": ev(8),
                },
                {
                    "region": "page 8 right column, Section 7 items 6-8",
                    "finding": "Detailed PtCl2 cyclization batches for 1m, 1q, and 1u to 2m, 2q, and 2u; merged with existing Table 1 entries.",
                    "evidence_ids": ev(8),
                },
                {
                    "region": "page 8 lower-right, Section 7 item 9 beginning",
                    "finding": "Detailed 3c to 4c batch begins here and its characterization continues on page 9; merged with existing Table 2 entry 3.",
                    "evidence_ids": ev(8),
                },
            ],
            "record_ids": page_records[8],
            "unresolved": [
                "The item-5 title and Table 1 say 1l/2l, but the page-8 body sentence prints 1k/2k; the source-label conflict remains unresolved.",
                "Complex structures remain machine-unverified; SI remains unassociated.",
            ],
        },
        {
            "page": 9,
            "state": "attempted",
            "regions": [
                {
                    "region": "page 9 upper-left before item 10",
                    "finding": "Characterization continuation for carbazole 4c; linked to the detailed batch beginning on page 8 and existing Table 2 entry 3.",
                    "evidence_ids": ev(9),
                },
                {
                    "region": "page 9 left column, Section 7 items 10-12",
                    "finding": "Detailed batches for 3e to 4e, the separate labeled 3f-D to 4f-D experiment, and 3h to 4h; merged with existing records. The labeled 86% batch was not conflated with unlabeled Table 2 entry 6 (75%).",
                    "evidence_ids": ev(9),
                },
                {
                    "region": "page 9 right column, Section 7 items 13-15",
                    "finding": "Detailed PtCl2 cyclization batches for 3i, 3j, and 3l to 4i, 4j, and 4l; merged with existing Table 2 entries 9, 10, and 12.",
                    "evidence_ids": ev(9),
                },
                {
                    "region": "page 9 lower-right, Acknowledgements",
                    "finding": "Funding and reproducibility acknowledgements only; no additional reaction experiment or condition row.",
                    "evidence_ids": ev(9),
                },
            ],
            "record_ids": page_records[9],
            "unresolved": [
                "Spectral assignments and complex structures were not chemically certified.",
                "Supporting Information remains unassociated.",
            ],
        },
        {
            "page": 10,
            "state": "attempted",
            "regions": [
                {
                    "region": "page 10, full two-column Notes and references section",
                    "finding": "Bibliographic references 1-24 only. Cited prior work was not imported as experiments of this paper; no reaction arrows, tables, footnotes with new experimental conditions, or reported batches are present.",
                    "evidence_ids": ev(10),
                },
            ],
            "record_ids": page_records[10],
            "unresolved": [
                "References were classified but not independently extracted as experiments.",
            ],
        },
    ],
}

coverage_out = BASE / "current" / "coverage" / "pages_0007_0010.json"
coverage_out.parent.mkdir(parents=True, exist_ok=True)
coverage_out.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

tasks_path = BASE / "current" / "tasks.json"
tasks = json.loads(tasks_path.read_text())
for task in tasks:
    if task["document_id"] == DOC and any(task["evidence_id"] == f"{DOC}:page{page}:text" for page in range(7, 11)):
        task["state"] = "attempted"
        task["reason"] = "Original page image inspected and page inventory recorded in coverage/pages_0007_0010.json."
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({
    "records_submitted": len(records),
    "new_record_ids": [f"{DOC}:prep_3e", f"{DOC}:prep_3l"],
    "coverage_pages": [page["page"] for page in coverage["pages"]],
    "output": str(out),
}, ensure_ascii=False))
