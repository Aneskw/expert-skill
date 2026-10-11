#!/usr/bin/env python3
"""Build evidence-linked machine records for jo991243g, PDF pages 1-5."""
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "runs/current/raw_model/records_pages_0001_0005.json"
COVERAGE = ROOT / "runs/current/coverage/pages_0001_0005.json"
DOC = "doc_3183f5db8d11b31a"


def evid(page: int) -> list[str]:
    return [f"{DOC}:page{page}:image", f"{DOC}:page{page}:text"]


def ev(*pages: int) -> list[str]:
    result: list[str] = []
    for page in pages:
        for item in evid(page):
            if item not in result:
                result.append(item)
    return result


def fact(value, evidence=()):
    return {
        "value": value,
        "evidence_ids": list(evidence) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def fld(name, value, evidence=()):
    return {"name": name, "fact": fact(value, evidence)}


def participant(entity_id, role, label, evidence, name=None, amounts=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence) if name is not None else fact(None),
        "smiles": fact(None),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": amounts or [],
    }


def rec(suffix, kind, evidence, participants, conditions, outcomes, notes=(), unresolved=()):
    return {
        "record_id": f"{DOC}:{suffix}",
        "document_id": DOC,
        "source_reaction_id": suffix,
        "record_kind": kind,
        "status": "needs_review",
        "completeness": "partial",
        "evidence_ids": list(evidence),
        "participants": participants,
        "steps": [{
            "step_id": "step1",
            "participant_ids": [p["entity_id"] for p in participants],
            "conditions": conditions,
        }] if participants or conditions else [],
        "outcomes": outcomes,
        "notes": [fact(x, evidence) for x in notes],
        "review": {
            "method": "model",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": list(unresolved) or [
                "No associated SI was supplied; unreported experimental details remain missing.",
                "Participant structures were not machine-certified from the drawings.",
            ],
        },
    }


def q(number, unit):
    return {"number": number, "unit": unit}


records = []

# Generic chemistry and the proposed catalytic cycle.
e = ev(1)
records.append(rec(
    "scheme1_generic_pathways", "general_scheme", e,
    [participant("organic_halide", "reactant", "RPdX / organic-halide coupling partner", e),
     participant("allenyl_propargyl_metal", "reactant", "allenic/propargylic organometallic reagent (M)", e),
     participant("allene_product", "product", "Pathway I allene", e),
     participant("alkyne_product", "product", "Pathway II alkyne", e)],
    [], [],
    notes=["Scheme 1 is a generic two-pathway relationship, not an individual experimental run."],
    unresolved=["Generic R, X, Pd, and M identities are not fully specified; structures and conditions remain unresolved."]
))
e = ev(3, 4)
records.append(rec(
    "scheme6_proposed_cycle", "mechanism", e,
    [participant("generic_alkenyl_iodide", "reactant", "electron-deficient alkenyl iodide", e),
     participant("generic_organozinc", "reactant", "allenyl/propargylic zinc reagent", e),
     participant("pd0", "catalyst", "Pd(0)", e),
     participant("product4", "product", "alkynic product family 4", e),
     participant("product7", "product", "allenic product family 7", e)],
    [], [],
    notes=["Scheme 6 proposes interconverting palladium intermediates 8-10 and alternative reductive-elimination paths."],
    unresolved=["Intermediates 8-10 are proposed, not observed; generic substituents and exact structures remain unresolved."]
))


def procedure_a_conditions(evidence):
    return [
        fld("organozinc_preparation", "1-phenylprop-1-yne + 1.5 mol% HgCl2 in THF; n-BuLi at -78 °C; then ZnBr2 at -78 °C and warm to room temperature", evidence),
        fld("coupling_catalyst", "5 mol% Pd(PPh3)4", evidence),
        fld("atmosphere", None), fld("concentration", None), fld("workup", None), fld("purification", None),
    ]


# Scheme 2 and adjacent prose; the two no-coupling statements coexist with a displayed <5% label.
for suffix, halide, r_group in [
    ("scheme2_e_1_iodostyrene", "(E)-1-iodostyrene", "Ph"),
    ("scheme2_e_1_iodohexene", "(E)-1-iodohexene", "n-C4H9"),
]:
    e = ev(1, 2)
    records.append(rec(
        suffix, "reported_experiment", e,
        [participant("alkyne1", "reactant", "1", e, "1-phenylprop-1-yne"),
         participant("alkenyl_halide", "reactant", halide, e),
         participant("product_family", "product", f"Scheme 2 allene product, R={r_group}", e)],
        procedure_a_conditions(e) + [fld("coupling_temperature", "room temperature", e), fld("coupling_time", q(20, "h"), e)],
        [fld("coupling_result", "no coupling product observed in prose", e),
         fld("scheme_displayed_yield", "<5%", e),
         fld("yield_measurement_basis", None)],
        notes=["The prose reports no coupling product, while Scheme 2 prints <5% for R = Ph and n-C4H9."],
        unresolved=["The relation between the prose 'no coupling product' statement and the Scheme 2 <5% label requires review; detection and yield bases are not stated."]
    ))

for suffix, halide, yld, detailed in [
    ("scheme2_alpha_bromostyrene", "alpha-bromostyrene", 29, False),
    ("scheme2_alpha_iodostyrene", "alpha-iodostyrene", 33, True),
]:
    e = ev(1, 2, 4) if detailed else ev(1, 2)
    cond = procedure_a_conditions(e) + [fld("coupling_temperature", "room temperature", e),
                                       fld("coupling_time", q(2 if detailed else 1.5, "h"), e)]
    if detailed:
        cond += [
            fld("charge_and_sequence", "HgCl2 2 mg (0.007 mmol), 1-phenylprop-1-yne 58 mg (0.5 mmol), THF 2 mL; n-BuLi 0.35 mL (1.6 M, 0.55 mmol) at -78 °C under N2 for 100 min; ZnBr2 169 mg (0.75 mmol) in THF 3 mL; warm to room temperature for 20 min; add Pd(PPh3)4 29 mg (0.025 mmol) and alpha-iodostyrene 112 mg (0.5 mmol) in THF 1 mL", e),
            fld("workup", "water quench; petroleum-ether extraction; MgSO4 drying; rotary evaporation", e),
            fld("purification", "silica-gel chromatography, petroleum ether", e),
        ]
    records.append(rec(
        suffix, "reported_experiment", e,
        [participant("alkyne1", "reactant", "1", e, "1-phenylprop-1-yne"),
         participant("alkenyl_halide", "reactant", halide, e),
         participant("product3a", "product", "3a", e, "2,3-diphenylpenta-1,3,4-triene")],
        cond,
        [fld("yield", q(yld, "%"), e), fld("yield_measurement_basis", "isolated" if detailed else None, e if detailed else ())] +
        ([fld("isolated_mass", q(36, "mg"), e)] if detailed else []),
        notes=["The coupling affords pathway-I allene 3a rather than alkynic product 3b."],
        unresolved=["Yield basis and full charge/workup are not reported for the alpha-bromostyrene run."] if not detailed else ["Reaction completion time was monitored by TLC but not numerically reported; concentration remains missing."]
    ))


# Table 1. Scheme 3's iodide/60% presentation is merged into entry 1.
t1 = [
    (1, "2a", "ethyl (Z)-3-iodopropenoate", "0", 1, "(Z)-4a", "ethyl 6-phenylhex-5-yn-2(Z)-enoate", 60, True, "Pd(PPh3)4", (2, 3)),
    (2, "2a", "ethyl (Z)-3-iodopropenoate", "0", 1.5, "(Z)-4a", "ethyl 6-phenylhex-5-yn-2(Z)-enoate", 66, False, "Pd(PPh3)4", (3, 4)),
    (3, "2a", "ethyl (Z)-3-iodopropenoate", "0", 2.5, "(Z)-4a", "ethyl 6-phenylhex-5-yn-2(Z)-enoate", 62, True, "PdCl2(PPh3)2", (3,)),
    (4, "2b", "methyl (Z)-3-iodopropenoate", "-3 to 0", 1, "(Z)-4b", "methyl 6-phenylhex-5-yn-2(Z)-enoate", 62, True, "Pd(PPh3)4", (3, 4)),
    (5, "2b", "methyl (Z)-3-iodopropenoate", "-3 to 0", 1.5, "(Z)-4b", "methyl 6-phenylhex-5-yn-2(Z)-enoate", 54, False, "Pd(PPh3)4", (3,)),
    (6, "2e", "methyl (Z)-3-phenyl-3-iodopropenoate", "50", 2.5, "(Z)-4e", "methyl 3,6-diphenylhex-5-yn-2(Z)-enoate", 49, True, "Pd(PPh3)4", (3, 4)),
    (7, "2e", "methyl (Z)-3-phenyl-3-iodopropenoate", "50", 0.5, "(Z)-4e", "methyl 3,6-diphenylhex-5-yn-2(Z)-enoate", 39, False, "Pd(PPh3)4", (3,)),
    (8, "2f", "(Z)-3-iodopropenitrile", "-15 to 0", 1.2, "(Z)-4f", "6-phenylhex-5-yn-2(Z)-enitrile", 90, True, "Pd(PPh3)4", (3, 5)),
    (9, "2f", "(Z)-3-iodopropenitrile", "-15 to 0", 1, "(Z)-4f", "6-phenylhex-5-yn-2(Z)-enitrile", 87, False, "Pd(PPh3)4", (3,)),
]
for entry, label, substrate, temp, time, plabel, pname, yld, hg, catalyst, pages in t1:
    e = ev(*pages)
    participants = [
        participant("alkyne1", "reactant", "1", e, "1-phenylprop-1-yne"),
        participant("substrate2", "reactant", label, e, substrate),
        participant("n_buli", "reagent", "n-BuLi", e), participant("znbr2", "reagent", "ZnBr2", e),
        participant("hgcl2", "catalyst", "HgCl2", e) if hg else participant("hgcl2_absent", "unspecified_agent", "HgCl2 absent", e),
        participant("pd", "catalyst", catalyst, e), participant("product", "product", plabel, e, pname),
        participant("thf", "solvent", "THF", e),
    ]
    cond = [fld("table_entry", entry, e), fld("coupling_temperature_C", temp, e), fld("coupling_time", q(time, "h"), e),
            fld("HgCl2_status", "present (1.5 mol%)" if hg else "absent", e), fld("palladium_catalyst", catalyst, e),
            fld("atmosphere", None), fld("concentration", None), fld("workup", None), fld("purification", None)]
    outcomes = [fld("isolated_yield", q(yld, "%"), e), fld("yield_measurement_basis", "isolated", e)]
    notes = []
    unresolved = ["Row-specific charge, atmosphere, concentration, workup, and purification are not all reported; no missing detail was inferred."]
    if entry == 2:
        cond += [fld("reported_starting_charges", "1 99 mg (0.85 mmol) and 2a 113 mg (0.5 mmol)", e)]
        outcomes += [fld("isolated_mass", q(71, "mg"), e)]
        notes.append("The product paragraph says this run was prepared similarly; the full procedure is not repeated.")
    if entry == 4:
        cond += [fld("reported_starting_charges", "1 99 mg (0.85 mmol) and 2b 106 mg (0.5 mmol)", e)]
        outcomes += [fld("isolated_mass", q(62, "mg"), e)]
    if entry == 6:
        cond += [fld("reported_starting_charges", "1 99 mg (0.85 mmol) and 2e 144 mg (0.5 mmol)", e)]
        outcomes += [fld("isolated_mass", q(67, "mg"), e)]
    if entry == 8:
        cond += [fld("detailed_sequence", "HgCl2 3 mg (0.011 mmol), 1 99 mg (0.85 mmol), THF 2 mL; n-BuLi 0.7 mL (1.6 M, 0.94 mmol) at -78 °C under N2 for 100 min; ZnBr2 278 mg (1.275 mmol) in THF 3 mL at -78 °C for 10 min; warm to room temperature for 20 min; add Pd(PPh3)4 29 mg (0.025 mmol) and 2f 90 mg (0.5 mmol) in THF 1 mL at -15 °C", e),
                 fld("workup", "water quench; ether extraction; MgSO4 drying; evaporation", e), fld("purification", "silica gel, petroleum ether/ethyl acetate 100:1", e)]
        outcomes += [fld("isolated_mass", q(76, "mg"), e)]
        unresolved = ["Reaction completion time was TLC-determined; concentration and extraction count/volumes are missing."]
    records.append(rec(f"table1_entry_{entry:02d}", "optimization_entry", e, participants, cond, outcomes, notes, unresolved))


# Scheme 3 halide-identity comparisons not duplicated in Table 1.
for suffix, substrate, time, result, yld in [
    ("scheme3_z_ethyl_bromopropenoate", "ethyl (Z)-3-bromopropenoate", 4, "(Z)-4a", 69),
    ("scheme3_z_ethyl_chloropropenoate", "ethyl (Z)-3-chloropropenoate", 4, "no coupling product", 0),
]:
    e = ev(2)
    parts = [participant("alkyne1", "reactant", "1", e, "1-phenylprop-1-yne"), participant("alkenyl_halide", "reactant", substrate, e),
             participant("pd", "catalyst", "Pd(PPh3)4", e)]
    if yld:
        parts.append(participant("product", "product", result, e, "ethyl 6-phenylhex-5-yn-2(Z)-enoate"))
    records.append(rec(suffix, "optimization_entry", e, parts,
        procedure_a_conditions(e) + [fld("coupling_temperature_C", 0, e), fld("coupling_time", q(time, "h"), e)],
        [fld("yield", q(yld, "%"), e), fld("yield_measurement_basis", None), fld("reaction_result", result, e)],
        unresolved=["Yield basis, row-specific charge, atmosphere, workup, and purification are not stated."]))


# Scheme 4: direct coupling, migration controls, and zinc-reagent amount/temperature study.
e = ev(2)
records.append(rec(
    "scheme4_e_iodopropenoate_low_temperature", "optimization_entry", e,
    [participant("alkyne1", "reactant", "1", e, "1-phenylprop-1-yne"), participant("substrate2c", "reactant", "2c", e, "ethyl (E)-3-iodopropenoate"),
     participant("pd", "catalyst", "Pd(PPh3)4", e), participant("product", "product", "(E)-4a", e, "ethyl 6-phenylhex-5-yn-2(E)-enoate")],
    [fld("n_BuLi_stage", "-78 °C", e), fld("ZnBr2_stage", "-78 °C to room temperature", e), fld("Pd_loading", "5 mol%", e),
     fld("coupling_temperature_C", -5, e), fld("coupling_time", q(0.75, "h"), e), fld("atmosphere", None), fld("workup", None), fld("purification", None)],
    [fld("yield", q(88, "%"), e), fld("yield_measurement_basis", None), fld("selectivity", "(E)-4a sole product", e)],
    unresolved=["HgCl2 status is not printed on this Scheme-4 arrow; yield basis, scale, atmosphere, workup, and purification are missing."]
))

e = ev(2, 4)
records.append(rec(
    "scheme4_e_iodopropenoate_procedure_a_mixture", "optimization_entry", e,
    [participant("alkyne1", "reactant", "1", e, "1-phenylprop-1-yne"), participant("substrate2c", "reactant", "2c", e, "ethyl (E)-3-iodopropenoate"),
     participant("product_e4a", "product", "(E)-4a", e, "ethyl 6-phenylhex-5-yn-2(E)-enoate"),
     participant("product_z5a", "product", "(Z)-5a", e, "ethyl 6-phenylhex-5-yn-3(Z)-enoate"),
     participant("product_e5a", "product", "(E)-5a", e, "ethyl 6-phenylhex-5-yn-3(E)-enoate")],
    procedure_a_conditions(e) + [fld("coupling_temperature_C", 20, e), fld("starting_charges", "1 99 mg (0.85 mmol); 2c 113 mg (0.5 mmol)", e),
                               fld("workup", None), fld("purification", None)],
    [fld("isolated_yield_E_4a", q(25, "%"), e), fld("isolated_mass_E_4a", q(27, "mg"), e),
     fld("isolated_yield_Z_5a", q(21, "%"), e), fld("isolated_mass_Z_5a", q(22, "mg"), e),
     fld("isolated_yield_E_5a", q(12, "%"), e), fld("isolated_mass_E_5a", q(13, "mg"), e),
     fld("combined_yield", q(58, "%"), e), fld("product_ratio_Z5a_E5a_E4a", "35:21:44", e), fld("yield_measurement_basis", "isolated", e)],
    unresolved=["The experimental paragraph says 'starting from' without repeating the full procedure; concentration and run-specific workup/purification are missing."]
))

e = ev(2)
records.append(rec(
    "scheme4_pnitrobenzyl_low_temperature", "optimization_entry", e,
    [participant("alkyne1", "reactant", "1", e, "1-phenylprop-1-yne"),
     participant("pnitro_substrate", "reactant", "p-nitrobenzyl (E)-3-iodopropenoate", e),
     participant("product4c", "product", "4c", e), participant("product5b", "product", "5b (Z/E mixture)", e)],
    procedure_a_conditions(e) + [fld("coupling_temperature_C", "-13 to -2", e), fld("coupling_time", q(1, "h"), e)],
    [fld("yield_4c", q(71, "%"), e), fld("yield_5b", q(15, "%"), e), fld("Z_E_ratio_5b", "2:1", e), fld("yield_measurement_basis", None)],
    unresolved=["The two Scheme-4 percentages do not match the separate experimental paragraph's 80% combined-yield/0.54:2:1 result; run identity and yield basis require review."]
))

e = ev(2, 4)
records.append(rec(
    "pnitrobenzyl_experimental_combined_yield", "reported_experiment", e,
    [participant("alkyne1", "reactant", "1", e, "1-phenylprop-1-yne", [fld("mass", q(99, "mg"), e), fld("amount", q(0.85, "mmol"), e)]),
     participant("pnitro_substrate", "reactant", "p-nitrobenzyl (E)-3-iodopropenoate", e, amounts=[fld("mass", q(167, "mg"), e), fld("amount", q(0.5, "mmol"), e)]),
     participant("hgcl2", "catalyst", "HgCl2", e), participant("product4c", "product", "4c", e),
     participant("product_z5b", "product", "(Z)-5b", e), participant("product_e5b", "product", "(E)-5b", e, "p-nitrobenzyl 6-phenylhex-5-yn-3(E)-enoate")],
    [fld("HgCl2_status", "present", e), fld("reaction_temperature", None), fld("reaction_time", None),
     fld("recrystallization", "petroleum ether/ethyl acetate afforded single crystals of (E)-5b", e)],
    [fld("combined_yield", q(80, "%"), e), fld("NMR_ratio_4c_Z5b_E5b", "0.54:2:1", e), fld("yield_measurement_basis", None)],
    notes=["This experimental-section result is kept separate from the low-temperature Scheme-4 percentages because the printed outcomes differ materially."],
    unresolved=["Reaction temperature/time, full catalyst/reagent charges, workup, purification before recrystallization, and combined-yield basis are missing; relation to the low-temperature Scheme-4 run requires review."]
))

e = ev(2)
records.append(rec(
    "scheme4_e4a_hg_pd_no_migration", "reported_experiment", e,
    [participant("e4a", "reactant", "(E)-4a", e, "ethyl 6-phenylhex-5-yn-2(E)-enoate", [fld("amount", q(0.25, "mmol"), e)]),
     participant("hgcl2", "catalyst", "HgCl2", e), participant("pd", "catalyst", "Pd(PPh3)4", e), participant("thf", "solvent", "THF", e)],
    [fld("HgCl2_loading", "1.5 mol%", e), fld("Pd_loading", "5 mol%", e), fld("temperature_C", 28, e), fld("reaction_time", None)],
    [fld("C_C_double_bond_migration", "not observed", e)],
    unresolved=["Reaction time, workup, analytical detection limit, and product recovery are not reported."]
))

for idx, zinc, temp, time, yields in [
    (1, 0.17, "22", 8.5, (69, 12, 5)),
    (2, 0.25, "-15 to -10", 1, (84, 0, 0)),
    (3, 0.25, "22", 4, (20, 45, 22)),
    (4, 0.35, "22", 4, (5, 44, 25)),
]:
    e = ev(2, 5)
    records.append(rec(
        f"scheme4_zinc_isomerization_row_{idx}", "optimization_entry", e,
        [participant("e4a", "reactant", "(E)-4a", e, "ethyl 6-phenylhex-5-yn-2(E)-enoate", [fld("amount", q(0.25, "mmol"), e)]),
         participant("zinc_reagent", "reagent", "in-situ allenic/propargylic zinc reagent", e),
         participant("e4a_out", "product", "(E)-4a", e), participant("z5a", "product", "(Z)-5a", e), participant("e5a", "product", "(E)-5a", e)],
        [fld("zinc_reagent_amount_as_3_phenylprop_1_yne", q(zinc, "mmol"), e), fld("temperature_C", temp, e), fld("time", q(time, "h"), e),
         fld("zinc_preparation", "n-BuLi at -78 °C for 100 min; ZnBr2 at -78 °C for 10 min; warm to room temperature for 20 min; add (E)-4a at the specified temperature", e),
         fld("atmosphere", "N2", e), fld("workup", "water quench; ether extraction; MgSO4 drying; rotary evaporation", e)],
        [fld("NMR_yield_E4a", q(yields[0], "%"), e), fld("NMR_yield_Z5a", q(yields[1], "%"), e), fld("NMR_yield_E5a", q(yields[2], "%"), e),
         fld("yield_measurement_basis", "300 MHz 1H NMR using CH2Br2 as internal standard", e)],
        unresolved=["Scheme 4 supplies the reagent amounts; the detailed paragraph defers exact n-BuLi/ZnBr2 amounts to the scheme and does not state concentration or extraction volumes."]
    ))

e = ev(4, 5)
records.append(rec(
    "e_iodopropenoate_no_hg_76_percent", "reported_experiment", e,
    [participant("alkyne1", "reactant", "1", e, "1-phenylprop-1-yne"), participant("substrate2c", "reactant", "2c", e, "ethyl (E)-3-iodopropenoate"),
     participant("n_buli", "reagent", "n-BuLi", e), participant("znbr2", "reagent", "ZnBr2", e), participant("pd", "catalyst", "Pd(PPh3)4", e),
     participant("product", "product", "(E)-4a", e, "ethyl 6-phenylhex-5-yn-2(E)-enoate")],
    [fld("HgCl2_status", "absent", e), fld("detailed_sequence", "1 99 mg (0.85 mmol) in THF 2 mL; n-BuLi 0.7 mL (1.6 M, 0.94 mmol) at -78 °C under N2 for 100 min; ZnBr2 278 mg (1.275 mmol) in THF 3 mL at -78 °C for 10 min; warm to room temperature for 20 min; add Pd(PPh3)4 29 mg (0.025 mmol) and 2c 113 mg (0.5 mmol) in THF 1 mL at 0 °C", e),
     fld("workup", "water quench; ether extraction; MgSO4 drying; rotary evaporation", e), fld("purification", "silica gel, petroleum ether/ethyl acetate 100:1", e)],
    [fld("isolated_mass", q(82, "mg"), e), fld("isolated_yield", q(76, "%"), e), fld("yield_measurement_basis", "isolated", e)],
    unresolved=["Reaction completion time was TLC-determined; concentration and extraction count/volumes are missing."]
))

e = ev(2, 5)
records.append(rec(
    "z4a_dmf_isomerization", "reported_experiment", e,
    [participant("z4a", "reactant", "(Z)-4a", e, "ethyl 6-phenylhex-5-yn-2(Z)-enoate", [fld("mass", q(30, "mg"), e), fld("amount", q(0.14, "mmol"), e)]),
     participant("dmf", "solvent", "DMF", e, amounts=[fld("volume", q(1, "mL"), e)]),
     participant("z5a", "product", "(Z)-5a", e), participant("e5a", "product", "(E)-5a", e)],
    [fld("temperature_C", 50, e), fld("time", q(2, "h"), e), fld("workup", "ether extraction; water wash; MgSO4 drying; rotary evaporation", e), fld("purification", None)],
    [fld("crude_product_mass", q(26, "mg"), e), fld("product_ratio_Z5a_E5a", "1:4", e), fld("scheme_yield_Z5a", q(25, "%"), e), fld("scheme_yield_E5a", q(62, "%"), e), fld("yield_measurement_basis", None)],
    unresolved=["The basis of the two Scheme-4 percentages and their relation to the detailed crude 1:4 ratio are not explicitly stated; purification is absent."]
))


# Table 2 scope. Detailed product paragraphs enrich entries 3, 5, 7, and 8.
t2 = [
    (1, "2a", "ethyl (Z)-3-iodopropenoate", 2.25, "(E)-7a", "ethyl 4-phenylnona-2(E),4,5-trienoate", 73, True, (3,)),
    (2, "2a", "ethyl (Z)-3-iodopropenoate", 2.5, "(E)-7a", "ethyl 4-phenylnona-2(E),4,5-trienoate", 30, False, (3,)),
    (3, "2b", "methyl (Z)-3-iodopropenoate", 2, "(E)-7b", "methyl 4-phenylnona-2(E),4,5-trienoate", 85, True, (3, 5)),
    (4, "2b", "methyl (Z)-3-iodopropenoate", 3, "(E)-7b", "methyl 4-phenylnona-2(E),4,5-trienoate", 58, False, (3,)),
    (5, "2c", "ethyl (E)-3-iodopropenoate", 2.5, "(E)-7a", "ethyl 4-phenylnona-2(E),4,5-trienoate", 86, True, (3, 5)),
    (6, "2c", "ethyl (E)-3-iodopropenoate", 2, "(E)-7a", "ethyl 4-phenylnona-2(E),4,5-trienoate", 78, False, (3,)),
    (7, "2d", "methyl (Z)-3-iodobutenoate", 2.5, "(Z)-7d", "methyl 3-methyl-4-phenylnona-2(Z),4,5-trienoate", 77, True, (3, 5)),
    (8, "2e", "methyl (Z)-3-phenyl-3-iodopropenoate", 23, "(Z)-7e", "methyl 3,4-diphenylnona-2(Z),4,5-trienoate", 47, True, (3, 5)),
    (9, "2e", "methyl (Z)-3-phenyl-3-iodopropenoate", 18, "(Z)-7e", "methyl 3,4-diphenylnona-2(Z),4,5-trienoate", 40, False, (3,)),
]
for entry, label, substrate, time, plabel, pname, yld, hg, pages in t2:
    e = ev(*pages)
    parts = [participant("alkyne6", "reactant", "6", e, "1-phenylhex-1-yne"), participant("substrate2", "reactant", label, e, substrate),
             participant("n_buli", "reagent", "n-BuLi", e), participant("znbr2", "reagent", "ZnBr2", e),
             participant("hgcl2", "catalyst", "HgCl2", e) if hg else participant("hgcl2_absent", "unspecified_agent", "HgCl2 absent", e),
             participant("pd", "catalyst", "Pd(PPh3)4", e), participant("product", "product", plabel, e, pname), participant("thf", "solvent", "THF", e)]
    cond = [fld("table_entry", entry, e), fld("reaction_time", q(time, "h"), e), fld("HgCl2_status", "present (1.5 mol%)" if hg else "absent", e),
            fld("common_sequence", "n-BuLi at room temperature; ZnBr2 at -78 °C then warm to room temperature; Pd(PPh3)4 coupling at room temperature", e),
            fld("atmosphere", None), fld("concentration", None), fld("workup", None), fld("purification", None)]
    outcomes = [fld("isolated_yield", q(yld, "%"), e), fld("yield_measurement_basis", "isolated", e)]
    unresolved = ["Row-specific charges, atmosphere, concentration, workup, and purification are not all reported; the detailed procedure was not generalized across rows."]
    if entry == 3:
        cond += [fld("detailed_sequence", "HgCl2 3 mg (0.011 mmol), 6 134 mg (0.85 mmol), THF 2 mL; n-BuLi 0.7 mL (1.6 M, 0.94 mmol) at room temperature under N2 for 100 min; ZnBr2 278 mg (1.275 mmol) in THF 3 mL at -78 °C for 10 min; warm to room temperature for 20 min; add Pd(PPh3)4 29 mg (0.025 mmol) and 2b 106 mg (0.5 mmol) in THF 1 mL at room temperature", e), fld("workup", "water quench; ether extraction; MgSO4 drying; rotary evaporation", e), fld("purification", "silica gel, petroleum ether/ethyl acetate 100:1", e)]
        outcomes += [fld("isolated_mass", q(103, "mg"), e)]
        unresolved = ["Concentration and extraction count/volumes are missing."]
    elif entry == 5:
        cond += [fld("reported_starting_charges", "6 134 mg (0.85 mmol) and 2c 113 mg (0.5 mmol)", e)]
        outcomes += [fld("isolated_mass", q(110, "mg"), e)]
    elif entry == 7:
        cond += [fld("reported_starting_charges", "6 134 mg (0.85 mmol) and 2d 113 mg (0.5 mmol)", e)]
        outcomes += [fld("isolated_mass", q(99, "mg"), e), fld("stereochemical_assignment", "Z by 2D 1H-1H NOESY", e)]
    elif entry == 8:
        cond += [fld("reported_starting_charges", "6 134 mg (0.85 mmol) and 2e 143 mg (0.5 mmol)", e)]
        outcomes += [fld("isolated_mass", q(37, "mg"), e), fld("recovered_2e_mass", q(71, "mg"), e), fld("conversion", q(50, "%"), e), fld("yield_basis_note", "47% based on 50% conversion", e)]
    if entry in (8, 9):
        outcomes += [fld("recovered_starting_material", q(50, "%"), e)]
    records.append(rec(f"table2_entry_{entry:02d}", "substrate_scope_entry", e, parts, cond, outcomes, unresolved=unresolved))


# Further controls/probes and a prose-only complicated reaction.
e = ev(3)
records.append(rec(
    "no_pd_control", "reported_experiment", e,
    [participant("substrate2a", "reactant", "2a", e, "ethyl (Z)-3-iodopropenoate"), participant("organozinc", "reactant", "in-situ organozinc from 1-phenylprop-1-yne/n-BuLi/ZnBr2", e)],
    [fld("Pd(PPh3)4_status", "absent", e), fld("temperature", None), fld("time", None), fld("workup", None)],
    [fld("reaction_result", "did not occur", e), fld("yield", None)],
    notes=["This control was used to rule out uncatalyzed Michael addition/elimination."],
    unresolved=["Exact charge, temperature, time, workup, and analytical detection limit are not reported in this sentence."]
))

e = ev(3, 5)
records.append(rec(
    "scheme5_competition", "reported_experiment", e,
    [participant("alkyne1", "reactant", "1", e, "1-phenylprop-1-yne"), participant("phenyl_iodide", "reactant", "phenyl iodide", e),
     participant("substrate2a", "reactant", "2a", e, "ethyl (Z)-3-iodopropenoate"), participant("pd", "catalyst", "Pd(PPh3)4", e),
     participant("allene", "product", "1,1-diphenylpropa-1,2-diene", e), participant("z4a", "product", "(Z)-4a", e)],
    [fld("detailed_sequence", "HgCl2 3 mg (0.011 mmol), 1 99 mg (0.85 mmol), THF 2 mL; n-BuLi 0.7 mL (1.6 M, 0.94 mmol) at -78 °C under N2 for 100 min; ZnBr2 278 mg (1.275 mmol) in THF 3 mL; warm to room temperature for 20 min; add Pd(PPh3)4 29 mg (0.025 mmol), 2a 113 mg (0.5 mmol), and phenyl iodide 102 mg (0.5 mmol) in THF 1 mL at room temperature", e),
     fld("workup", "water quench; ether extraction; MgSO4 drying; rotary evaporation", e), fld("purification", None)],
    [fld("NMR_product_ratio_allene_to_Z4a", "4:1", e), fld("yield", None), fld("yield_measurement_basis", "NMR ratio; internal standard not stated for this experiment", e)],
    unresolved=["Absolute yields, reaction time, purification, concentration, and NMR internal standard are missing."]
))

e = ev(2)
records.append(rec(
    "methyl_alpha_bromopropenoate_complicated", "reported_experiment", e,
    [participant("alkyne1", "reactant", "1", e, "1-phenylprop-1-yne"), participant("substrate", "reactant", "methyl alpha-bromopropenoate", e),
     participant("organozinc", "reactant", "in-situ organozinc reagent", e)],
    [fld("reaction_conditions", "corresponding coupling conditions", e), fld("temperature", None), fld("time", None)],
    [fld("reaction_result", "reaction was complicated", e), fld("product_identity", None), fld("yield", None)],
    unresolved=["The phrase 'corresponding reaction' does not establish exact catalyst/HgCl2 status, temperature, time, products, or yields."]
))


# Locally reported but incomplete starting-material preparations.
for suffix, product, acid, organic_halide in [
    ("materials_prepare_2c", "ethyl (E)-3-iodopropenoate (2c)", "(E)-3-iodopropenoic acid", "ethylating organic halide (not named)"),
    ("materials_prepare_e_bromopropenoate", "ethyl (E)-3-bromopropenoate", "(E)-3-bromopropenoic acid", "ethylating organic halide (not named)"),
    ("materials_prepare_pnitrobenzyl", "4-nitrobenzyl (E)-3-iodopropenoate", "(E)-3-iodopropenoic acid", "4-nitrobenzyl organic halide (exact halide not named)"),
]:
    e = ev(4)
    records.append(rec(
        suffix, "reported_experiment", e,
        [participant("acid", "reactant", acid, e), participant("organic_halide", "reactant", organic_halide, e),
         participant("k2co3", "reagent", "K2CO3", e), participant("dmf", "solvent", "DMF", e), participant("product", "product", product, e)],
        [fld("reaction_description", "reaction of the (E)-3-halopropenoic acid, K2CO3, and the corresponding organic halide in DMF", e),
         fld("temperature", None), fld("time", None), fld("workup", None), fld("purification", None)],
        [fld("yield", None)],
        unresolved=["Exact alkylating-halide identity where not named, quantities, temperature, time, workup, purification, and yield are not reported."]
    ))

e = ev(4)
records.append(rec(
    "materials_cited_preparations", "literature_example", e,
    [participant("starting_material_family", "product", "(E)-1-iodostyrene, (E)-1-iodohexene, 2a, 2b, ethyl (Z)-3-bromopropenoate, ethyl (Z)-3-chloropropenoate, 2d, 2e, and 2f", e)],
    [fld("preparation_method", "prepared according to cited literature methods", e)],
    [fld("local_yield", None)],
    notes=["This is a grouped prior-literature preparation statement, not a set of locally detailed current-paper runs."],
    unresolved=["Individual cited procedures, charges, conditions, workups, purifications, and yields are not reproduced locally and were not imported."]
))


OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")

by_page = {page: [] for page in range(1, 6)}
for record in records:
    for page in range(1, 6):
        if f"{DOC}:page{page}:image" in record["evidence_ids"] or f"{DOC}:page{page}:text" in record["evidence_ids"]:
            by_page[page].append(record["record_id"])

coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1,
            "state": "attempted",
            "regions": [
                {"region": "Scheme 1 and introduction", "finding": "Generic allene-versus-alkyne coupling pathways; classified as a general scheme, not an experiment.", "evidence_ids": evid(1)},
                {"region": "Results and Discussion, lower-right column", "finding": "Two no-coupling tests, alpha-bromo/alpha-iodostyrene couplings, and Scheme-3 halide comparison context; individual runs linked to page-2 schemes.", "evidence_ids": evid(1)},
            ],
            "record_ids": by_page[1],
            "unresolved": ["Scheme 2's displayed <5% label conflicts in granularity with the prose 'no coupling product' statement; yield/detection basis is not given."],
        },
        {
            "page": 2,
            "state": "attempted",
            "regions": [
                {"region": "Schemes 2 and 3", "finding": "Alkenyl-halide comparison, including explicit no-reaction and zero-yield results; Scheme-3 iodide run merged with Table 1 entry 1.", "evidence_ids": evid(2)},
                {"region": "Scheme 4 and adjacent prose", "finding": "Direct coupling, double-bond migration, no-migration control, four zinc-reagent/temperature rows, and p-nitrobenzyl outcomes split by materially different printed results.", "evidence_ids": evid(2)},
            ],
            "record_ids": by_page[2],
            "unresolved": ["Low-temperature p-nitrobenzyl percentages and the experimental-section 80% combined-yield result cannot be proven to be the same run.", "Several Scheme-4 yields lack an explicit measurement basis."],
        },
        {
            "page": 3,
            "state": "attempted",
            "regions": [
                {"region": "Table 1", "finding": "Nine optimization rows extracted separately with HgCl2/catalyst footnote overrides and isolated yields.", "evidence_ids": evid(3)},
                {"region": "Table 2 and Figure 1", "finding": "Nine substrate-scope rows extracted separately; no-Hg and 50%-recovery footnotes applied row-wise; Figure 1 linked to the (Z)-7d stereochemical assignment.", "evidence_ids": evid(3)},
                {"region": "Scheme 5, control prose, and mechanism discussion", "finding": "No-Pd control and mixed-halide competition retained as experiments; proposed palladium cycle classified separately as mechanism.", "evidence_ids": evid(3)},
            ],
            "record_ids": by_page[3],
            "unresolved": ["Most table rows omit row-specific charges, atmosphere, concentration, workup, and purification.", "The no-Pd control does not state a numerical detection limit."],
        },
        {
            "page": 4,
            "state": "attempted",
            "regions": [
                {"region": "Scheme 6 and conclusion", "finding": "Proposed regioselectivity cycle recorded as mechanism; no observed intermediates were asserted.", "evidence_ids": evid(4)},
                {"region": "Materials and experimental section", "finding": "Incomplete local precursor preparations and detailed/abbreviated product preparations linked to Scheme 2, Table 1, and Scheme 4 records rather than duplicated.", "evidence_ids": evid(4)},
            ],
            "record_ids": by_page[4],
            "unresolved": ["The paper cites methods for several starting materials without reproducing their individual procedures.", "The main text points to SI for X-ray information, but no SI file is supplied or associated."],
        },
        {
            "page": 5,
            "state": "attempted",
            "regions": [
                {"region": "Detailed coupling preparations, left column", "finding": "No-Hg (E)-4a, (Z)-4f, and Table-2 products 7a/7b/7d/7e were merged into their matching scheme/table records.", "evidence_ids": evid(5)},
                {"region": "Isomerization and competition procedures, right column", "finding": "DMF isomerization, Scheme-5 competition, and the detailed (E)-4a/zinc-reagent procedure linked to existing records.", "evidence_ids": evid(5)},
                {"region": "Supporting Information notice", "finding": "SI availability is mentioned in the article, but the pilot provides no associated SI; missing details remain unresolved.", "evidence_ids": evid(5)},
            ],
            "record_ids": by_page[5],
            "unresolved": ["Several 'prepared similarly' paragraphs do not restate all reagent charges or workup details.", "The supplied pilot has no SI, so spectra and X-ray details named in the notice were not imported."],
        },
    ],
}
COVERAGE.parent.mkdir(parents=True, exist_ok=True)
COVERAGE.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"records": len(records), "record_file": str(OUT), "coverage_file": str(COVERAGE)}, ensure_ascii=False))
