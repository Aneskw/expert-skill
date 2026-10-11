#!/usr/bin/env python3
"""Build source-linked records for jo981592v, original PDF pages 1-3."""
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "runs/current/raw_model/records_pages_0001_0003.json"
COVERAGE = ROOT / "runs/current/coverage/pages_0001_0003.json"
DOC = "doc_6b8676db1cc8edad"
P1T, P1I = f"{DOC}:page1:text", f"{DOC}:page1:image"
P2T, P2I = f"{DOC}:page2:text", f"{DOC}:page2:image"
P3T, P3I = f"{DOC}:page3:text", f"{DOC}:page3:image"


def fact(value, ev):
    return {
        "value": value,
        "evidence_ids": list(dict.fromkeys(ev)) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def fld(name, value, ev):
    return {"name": name, "fact": fact(value, ev)}


def participant(entity_id, role, label, name, ev, amounts=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, ev),
        "name": fact(name, ev),
        "smiles": fact(None, []),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": amounts or [],
    }


def rec(suffix, kind, ev, participants, conditions=None, outcomes=None, notes=None,
        unresolved=None, source_reaction_id=None):
    return {
        "record_id": f"{DOC}:{suffix}",
        "document_id": DOC,
        "source_reaction_id": source_reaction_id or suffix,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": list(dict.fromkeys(ev)),
        "participants": participants,
        "steps": [{
            "step_id": "step1",
            "participant_ids": [p["entity_id"] for p in participants],
            "conditions": conditions or [],
        }],
        "outcomes": outcomes or [],
        "notes": [fact(x, ev) for x in (notes or [])],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved or [
                "No associated SI was supplied; missing experimental details remain unresolved.",
                "All depicted or label-derived structures remain unverified and SMILES are intentionally null.",
            ],
        },
    }


names = {
    "3a": "1-(methylsulfonyl)-1,2-propadiene",
    "3b": "(1,2-propadienylsulfonyl)benzene",
    "3c": "(1-methyl-1,2-propadienylsulfonyl)benzene",
    "3d": "(3-methyl-1,2-butadienylsulfonyl)benzene",
    "4aa": "2-Iodo-3-(methylsulfonyl)-1-propene",
    "4ab": "2-Bromo-3-(methylsulfonyl)-1-propene",
    "4ac": "2-Chloro-3-(methylsulfonyl)-1-propene",
    "4ba": "((2-Iodo-2-propenyl)sulfonyl)benzene",
    "4bb": "((2-Bromo-2-propenyl)sulfonyl)benzene",
    "4bc": "((2-Chloro-2-propenyl)sulfonyl)benzene",
    "4ca": "((2-Iodo-1-methyl-2-propenyl)sulfonyl)benzene",
    "4cb": "((2-Bromo-1-methyl-2-propenyl)sulfonyl)benzene",
    "4da": "((2-Iodo-3-methyl-2-butenyl)sulfonyl)benzene",
}


records = []

# Scheme 1 contains two successive generic stages. The paper states that the
# four 3-series compounds were prepared by this chemistry according to cited
# procedures, but supplies no row-specific charges, conditions, or yields.
records.append(rec(
    "scheme1_step1_propargylic_alcohol_to_allenic_sulfoxide", "general_scheme",
    [P1T, P1I],
    [
        participant("scheme1_1", "reactant", "1", "generic propargylic alcohol", [P1I]),
        participant("scheme1_rscl", "reagent", "RSCl", "sulfenyl chloride (generic)", [P1I]),
        participant("scheme1_et3n", "reagent", "Et3N", "triethylamine", [P1I]),
        participant("scheme1_2", "product", "2", "generic 1,2-allenic sulfoxide", [P1I]),
    ],
    outcomes=[fld("reported_yield", None, [])],
    notes=["Scheme 1 first arrow; the generic R groups do not define a single structure."],
    unresolved=[
        "No quantities, solvent, temperature, time, workup, purification, or yield are printed for this generic stage.",
        "The locally depicted chemistry is attributed to published procedures (references 12 and 17); no external procedure was imported.",
        "Generic structures and R groups remain unverified; SMILES are null.",
    ],
))
records.append(rec(
    "scheme1_step2_allenic_sulfoxide_oxidation", "general_scheme", [P1T, P1I],
    [
        participant("scheme1_2", "reactant", "2", "generic 1,2-allenic sulfoxide", [P1I]),
        participant("scheme1_h2o2", "reagent", "H2O2", "hydrogen peroxide", [P1I]),
        participant("scheme1_3", "product", "3", "generic 1,2-allenic sulfone", [P1I]),
    ],
    outcomes=[fld("reported_yield", None, [])],
    notes=["Scheme 1 second arrow; the printed substitution table maps 3a-d to R1/R2/R combinations."],
    unresolved=[
        "No quantities, solvent, temperature, time, workup, purification, or yield are printed for this generic stage.",
        "The paper states that 3a-d were prepared according to published procedures; no external procedure was imported.",
        "Generic structures and R groups remain unverified; SMILES are null.",
    ],
))
records.append(rec(
    "scheme2_general_hydrohalogenation", "general_scheme", [P1T, P1I],
    [
        participant("scheme2_3", "reactant", "3", "generic 1,2-allenic sulfone", [P1I]),
        participant("scheme2_x", "reagent", "X-", "chloride, bromide, or iodide", [P1I]),
        participant("scheme2_h", "reagent", "H+", "proton source", [P1I]),
        participant("scheme2_4", "product", "4", "generic 2-haloallylic sulfone", [P1I]),
    ],
    notes=[
        "Conditions A: MX (M = Na or Li), HOAc as solvent.",
        "Conditions B: MX (M = Na or Li), 1 equivalent HOAc, CH3CN as solvent.",
        "Conditions C: HX as both solvent and reagent.",
    ],
    unresolved=[
        "This is a generic reaction scheme, not an individual experimental run.",
        "Generic R groups and X identity are not fixed; SMILES are null.",
    ],
))

# Prose-only observations on page 1 are kept as partial current-paper results.
records.append(rec(
    "prose_3a_lii_hoac_room_temperature_slow", "reported_experiment", [P1T, P1I],
    [
        participant("rt_3a", "reactant", "3a", names["3a"], [P1T]),
        participant("rt_lii", "reagent", "LiI", "lithium iodide", [P1T]),
        participant("rt_hoac", "solvent", "HOAc", "acetic acid", [P1T]),
    ],
    conditions=[fld("temperature", "room temperature", [P1T])],
    outcomes=[fld("observation", "very slow reaction observed", [P1T])],
    unresolved=[
        "Reaction time, quantities, product identity, conversion, yield, workup, and analytical basis are not reported.",
        "The observation is qualitative and does not establish a complete experiment.",
        "Structures remain unverified; SMILES are null.",
    ],
))
records.append(rec(
    "prose_4ac_hoac_thermal_stability", "reported_experiment", [P1T, P1I],
    [
        participant("stability_4ac", "reactant", "4ac", names["4ac"], [P1T]),
        participant("stability_hoac", "solvent", "HOAc", "acetic acid", [P1T]),
    ],
    conditions=[
        fld("temperature", {"number": 118, "unit": "°C"}, [P1T]),
        fld("time", {"number": 11, "unit": "h"}, [P1T]),
    ],
    outcomes=[fld("C=C_bond_migration", "not observed", [P1T])],
    unresolved=[
        "Substrate quantity, solvent volume, atmosphere, workup, detection limit, and analytical method are not reported.",
        "The no-migration statement does not provide a numerical recovery or conversion.",
        "Structures remain unverified; SMILES are null.",
    ],
))


def add_amount(p, name, value, ev):
    p["amounts"].append(fld(name, value, ev))


def detailed(record, data):
    """Add page-3 source-local charges/outcome details to a matching table row."""
    ev = [P3T, P3I]
    record["evidence_ids"] = list(dict.fromkeys(record["evidence_ids"] + ev))
    by_role = {p["role"]: p for p in record["participants"]}
    reactant = by_role["reactant"]
    reagent = next(p for p in record["participants"] if p["role"] == "reagent" and p["label"]["value"] not in {"HOAc"})
    product = by_role["product"]
    add_amount(reactant, "mass", {"number": data["r_mg"], "unit": "mg"}, ev)
    add_amount(reactant, "amount", {"number": data["r_mmol"], "unit": "mmol"}, ev)
    add_amount(reagent, "mass", {"number": data["x_mg"], "unit": "mg"}, ev)
    add_amount(reagent, "amount", {"number": data["x_mmol"], "unit": "mmol"}, ev)
    if data.get("p_mg") is not None:
        add_amount(product, "isolated_mass", {"number": data["p_mg"], "unit": "mg"}, ev)
    if data.get("state"):
        record["outcomes"].append(fld("physical_state", data["state"], ev))
    if data.get("mp"):
        record["outcomes"].append(fld("melting_point", data["mp"], ev))
    record["notes"].append(fact("The product paragraph states that this compound was prepared similarly under conditions A; exact repeated operations are not reprinted.", ev))


def table_record(table, entry, substrate, reagent_label, equiv, condset, temp, time_h,
                 product, yield_value, yield_basis, acid_conc=None, recovery=None):
    suffix = f"table{table}_entry{entry:02d}"
    ev = [P2T, P2I]
    ps = [participant(f"{suffix}_{substrate}", "reactant", substrate, names[substrate], ev)]
    reagent_names = {
        "NaI": "sodium iodide", "LiI": "lithium iodide", "NaBr": "sodium bromide",
        "LiBr·H2O": "lithium bromide hydrate (printed LiBr·H2O)", "NaCl": "sodium chloride",
        "LiCl·H2O": "lithium chloride hydrate (printed LiCl·H2O)", "HI": "hydriodic acid",
        "HBr": "hydrobromic acid", "HCl": "hydrochloric acid",
    }
    amounts = []
    if equiv is not None:
        amounts.append(fld("equivalents", equiv if isinstance(equiv, str) else {"number": equiv, "unit": "equiv"}, ev))
    if acid_conc is not None:
        amounts.append(fld("aqueous_acid_concentration", {"number": acid_conc, "unit": "%"}, ev))
    ps.append(participant(f"{suffix}_halide", "reagent", reagent_label, reagent_names[reagent_label], ev, amounts))
    if condset == "A":
        ps.append(participant(f"{suffix}_hoac", "solvent", "HOAc", "acetic acid", ev))
    elif condset == "B":
        ps.append(participant(f"{suffix}_hoac", "reagent", "HOAc", "acetic acid", ev,
                              [fld("equivalents", {"number": 1, "unit": "equiv"}, [P1T, P1I])]))
        ps.append(participant(f"{suffix}_mecn", "solvent", "CH3CN", "acetonitrile", ev))
    ps.append(participant(f"{suffix}_{product}", "product", product, names[product], ev))
    conds = [fld("condition_set", condset, ev), fld("temperature", temp, ev),
             fld("time", {"number": time_h, "unit": "h"}, ev)]
    outcomes = [fld("yield", {"number": yield_value, "unit": "%"}, ev),
                fld("yield_measurement_basis", yield_basis, ev)]
    if recovery is not None:
        outcomes.append(fld("starting_material_recovered", {"number": recovery, "unit": "%"}, ev))
    notes = []
    if condset == "C":
        notes.append("Under conditions C, HX is both the solvent and the reagent.")
    unresolved = [
        "Atmosphere and concentration are not reported.",
        "Row-specific workup and purification are not reported unless supplemented by a linked detailed procedure.",
        "No associated SI was supplied; SI-only spectra and missing experimental details remain unavailable.",
        "All structures remain unverified and SMILES are null.",
    ]
    return rec(suffix, "optimization_entry" if table == 1 else "substrate_scope_entry",
               ev, ps, conds, outcomes, notes, unresolved)


table1 = [
    (1, "3a", "NaI", "1.1–2 equiv", "A", {"number": 80, "unit": "°C"}, 0.5, "4aa", 80, "isolated", None, None),
    (2, "3a", "LiI", 1.7, "A", "reflux", 0.5, "4aa", 87, "isolated", None, None),
    (3, "3a", "NaBr", 2, "A", "reflux", 4, "4ab", 61, "isolated", None, 30),
    (4, "3a", "LiBr·H2O", 2, "A", "reflux", 1.5, "4ab", 79, "isolated", None, None),
    (5, "3a", "NaCl", 4.4, "A", "reflux", 11, "4ac", 28, "isolated", None, 70),
    (6, "3a", "LiCl·H2O", 5, "A", "reflux", 11, "4ac", 83, "isolated", None, None),
    (7, "3a", "LiI", 2, "B", {"number": 80, "unit": "°C"}, 12, "4aa", 76, "isolated", None, None),
    (8, "3a", "LiBr·H2O", 2, "B", {"number": 80, "unit": "°C"}, 12, "4ab", 76, "isolated", None, None),
    (9, "3a", "LiCl·H2O", 2, "B", {"number": 80, "unit": "°C"}, 12, "4ac", 85, "isolated", None, None),
    (10, "3a", "HI", None, "C", {"number": 80, "unit": "°C"}, 8, "4aa", 65, "isolated", 45, None),
    (11, "3a", "HCl", None, "C", {"number": 80, "unit": "°C"}, 8, "4ac", 83, "isolated", 37, None),
]
for row in table1:
    records.append(table_record(1, *row))

table2 = [
    (1, "3b", "NaI", 2, "A", {"number": 80, "unit": "°C"}, 0.5, "4ba", 82, "isolated", None, None),
    (2, "3b", "LiBr·H2O", 2, "A", {"number": 90, "unit": "°C"}, 0.5, "4bb", 78, "isolated", None, None),
    (3, "3b", "NaBr", 5, "A", {"number": 90, "unit": "°C"}, 8, "4bb", 67, "isolated", None, None),
    (4, "3b", "LiCl·H2O", 2, "A", {"number": 90, "unit": "°C"}, 2, "4bc", 69, "isolated", None, None),
    (5, "3b", "NaCl", 5, "A", {"number": 90, "unit": "°C"}, 13, "4bc", 14, "isolated", None, 36),
    (6, "3b", "LiI", 2.5, "B", {"number": 80, "unit": "°C"}, 12, "4ba", 76, "isolated", None, None),
    (7, "3b", "LiBr·H2O", 2.5, "B", {"number": 80, "unit": "°C"}, 12, "4bb", 67, "isolated", None, None),
    (8, "3b", "LiCl·H2O", 2.5, "B", {"number": 80, "unit": "°C"}, 12, "4bc", 76, "isolated", None, None),
    (9, "3b", "HI", None, "C", {"number": 80, "unit": "°C"}, 0.5, "4ba", 44, "isolated", 45, None),
    (10, "3b", "HBr", None, "C", {"number": 80, "unit": "°C"}, 2, "4bb", 53, "isolated", 40, None),
    (11, "3b", "HCl", None, "C", {"number": 80, "unit": "°C"}, 2, "4bc", 81, "isolated", 37, None),
    (12, "3c", "NaI", 3.5, "A", {"number": 80, "unit": "°C"}, 4, "4ca", 88, "isolated", None, None),
    (13, "3c", "NaI", 1.2, "A", "reflux", 4, "4ca", 83, "isolated", None, None),
    (14, "3c", "LiBr·H2O", 5, "A", {"number": 110, "unit": "°C"}, 20, "4cb", 77, "isolated", None, None),
    (15, "3c", "LiBr·H2O", 2, "A", "reflux", 10, "4cb", 74, "isolated", None, None),
    (16, "3c", "NaBr", 5, "A", {"number": 110, "unit": "°C"}, 20, "4cb", 41, "NMR", None, None),
    (17, "3d", "NaI", 3, "A", "reflux", 2, "4da", 74, "isolated", None, None),
    (18, "3d", "NaI", 1.2, "A", "reflux", 2.5, "4da", 69, "isolated", None, None),
]
for row in table2:
    records.append(table_record(2, *row))

by_id = {r["record_id"].split(":", 1)[1]: r for r in records}

# Merge the detailed procedures/product paragraphs into their matching table rows.
detailed(by_id["table1_entry04"], dict(r_mg=60, r_mmol=0.51, x_mg=104, x_mmol=1, p_mg=80, state="liquid"))
detailed(by_id["table1_entry06"], dict(r_mg=25, r_mmol=0.21, x_mg=60, x_mmol=1, p_mg=27.2, state="liquid"))
detailed(by_id["table2_entry01"], dict(r_mg=36, r_mmol=0.2, x_mg=60, x_mmol=0.4, p_mg=51, state="solid", mp="90.5–91.5 °C"))
detailed(by_id["table2_entry02"], dict(r_mg=36, r_mmol=0.2, x_mg=42, x_mmol=0.4, p_mg=41, state="solid", mp="75.5–76.5 °C"))
detailed(by_id["table2_entry04"], dict(r_mg=36, r_mmol=0.2, x_mg=24, x_mmol=0.4, p_mg=30, state="solid", mp="54–55.5 °C"))
detailed(by_id["table2_entry12"], dict(r_mg=29, r_mmol=0.15, x_mg=80, x_mmol=0.53, p_mg=42, state="liquid"))
detailed(by_id["table2_entry14"], dict(r_mg=21, r_mmol=0.11, x_mg=52, x_mmol=0.5, p_mg=23, state="liquid"))
detailed(by_id["table2_entry17"], dict(r_mg=36, r_mmol=0.17, x_mg=80, x_mmol=0.53, p_mg=43, state="solid", mp="85–86 °C"))

# Table 1 entry 1 is the Conditions-A typical procedure. The table and prose
# disagree on reaction time (0.5 h vs 1.5 h), so both source values are kept.
r = by_id["table1_entry01"]
r["evidence_ids"] += [P3T, P3I]
add_amount(r["participants"][0], "mass", {"number": 118, "unit": "mg"}, [P2T, P3T])
add_amount(r["participants"][0], "amount", {"number": 1, "unit": "mmol"}, [P2T, P3T])
add_amount(r["participants"][1], "mass", {"number": 165, "unit": "mg"}, [P2T, P3T])
add_amount(r["participants"][1], "amount", {"number": 1.1, "unit": "mmol"}, [P2T, P3T])
add_amount(r["participants"][2], "volume", {"number": 0.5, "unit": "mL"}, [P2T])
add_amount(r["participants"][3], "isolated_mass", {"number": 197, "unit": "mg"}, [P3T])
r["steps"][0]["conditions"].append(fld("procedure_reported_time", {"number": 1.5, "unit": "h"}, [P2T, P2I]))
r["steps"].append({
    "step_id": "workup_and_purification",
    "participant_ids": [],
    "conditions": [
        fld("monitoring", "TLC; petroleum ether/ethyl acetate 1:1", [P2T, P2I]),
        fld("quench", "water, 3 mL", [P2T, P2I]),
        fld("neutralization", "NaHCO3", [P2T, P2I]),
        fld("extraction", "ether, 4 × 10 mL", [P2T, P2I]),
        fld("drying", "MgSO4", [P2T, P2I]),
        fld("purification", "flash chromatography on silica gel; petroleum ether/ethyl acetate 2:1", [P2T, P3T]),
    ],
})
r["outcomes"].extend([fld("physical_state", "solid", [P3T, P3I]), fld("melting_point", "56–57 °C", [P3T, P3I])])
r["notes"].append(fact("Table 1 entry 1 prints 0.5 h, while the matching Conditions-A typical procedure prints 1.5 h; both are retained.", [P2T, P2I]))
r["review"]["unresolved"].append("Resolve the source-internal 0.5 h versus 1.5 h reaction-time discrepancy.")

# Conditions-B typical procedure = Table 1 entry 7.
r = by_id["table1_entry07"]
r["evidence_ids"] += [P3T, P3I]
add_amount(r["participants"][0], "mass", {"number": 59, "unit": "mg"}, [P3T])
add_amount(r["participants"][0], "amount", {"number": 0.5, "unit": "mmol"}, [P3T])
add_amount(r["participants"][1], "mass", {"number": 134, "unit": "mg"}, [P3T])
add_amount(r["participants"][1], "amount", {"number": 1, "unit": "mmol"}, [P3T])
add_amount(r["participants"][2], "volume", {"number": 0.03, "unit": "mL"}, [P3T])
add_amount(r["participants"][2], "amount", {"number": 0.52, "unit": "mmol"}, [P3T])
add_amount(r["participants"][3], "volume", {"number": 1, "unit": "mL"}, [P3T])
add_amount(r["participants"][4], "isolated_mass", {"number": 93, "unit": "mg"}, [P3T])
r["steps"].append({"step_id": "workup_and_purification", "participant_ids": [], "conditions": [
    fld("quench", "water, 1 mL", [P3T]), fld("neutralization", "NaHCO3", [P3T]),
    fld("extraction", "ether, 4 × 5 mL", [P3T]), fld("drying", "MgSO4", [P3T]),
    fld("purification", "flash chromatography on silica gel; petroleum ether/ethyl acetate 2:1", [P3T]),
]})

# Conditions-C typical procedure = Table 1 entry 10.
r = by_id["table1_entry10"]
r["evidence_ids"] += [P3T, P3I]
add_amount(r["participants"][0], "mass", {"number": 59, "unit": "mg"}, [P3T])
add_amount(r["participants"][0], "amount", {"number": 0.5, "unit": "mmol"}, [P3T])
add_amount(r["participants"][1], "volume", {"number": 1, "unit": "mL"}, [P3T])
add_amount(r["participants"][2], "isolated_mass", {"number": 80, "unit": "mg"}, [P3T])
r["steps"].append({"step_id": "workup_and_purification", "participant_ids": [], "conditions": [
    fld("quench", "water, 1 mL", [P3T]), fld("neutralization", "NaHCO3", [P3T]),
    fld("extraction", "ether, 4 × 5 mL", [P3T]), fld("drying", "MgSO4", [P3T]),
    fld("purification", "flash chromatography on silica gel; petroleum ether/ethyl acetate 2:1", [P3T]),
]})

# Equation 1 / detailed deuterium-labeling preparation.
records.append(rec(
    "eq1_3a_nai_doac_deuteration", "reported_experiment", [P2T, P2I, P3T, P3I],
    [
        participant("eq1_3a", "reactant", "3a", names["3a"], [P2T, P2I, P3T], [
            fld("mass", {"number": 118, "unit": "mg"}, [P3T]), fld("amount", {"number": 1, "unit": "mmol"}, [P3T])]),
        participant("eq1_nai", "reagent", "NaI", "sodium iodide", [P2T, P2I, P3T], [
            fld("mass", {"number": 300, "unit": "mg"}, [P3T]), fld("amount", {"number": 2, "unit": "mmol"}, [P3T])]),
        participant("eq1_doac", "solvent", "DOAc", "deuterated acetic acid", [P2T, P2I, P3T], [
            fld("volume", {"number": 1, "unit": "mL"}, [P3T])]),
        participant("eq1_4aap", "product", "4aa′", "3-Deuterio-2-iodo-3-(methylsulfonyl)-1-propene", [P2T, P2I, P3T], [
            fld("isolated_mass", {"number": 191, "unit": "mg"}, [P3T])]),
    ],
    outcomes=[
        fld("yield", {"number": 77, "unit": "%"}, [P2T, P3T]),
        fld("yield_measurement_basis", "isolated", [P3T]),
        fld("deuterium_incorporation", ">97%", [P2T, P2I]),
        fld("physical_state", "liquid", [P3T]),
    ],
    notes=["Page 2 calls the product methyl 1-deuterio-2-iodo-2-propenyl sulfone; page 3 prints the systematic heading retained in the product name."],
    unresolved=[
        "Reaction temperature, time, atmosphere, concentration, workup, and purification are not reported in the supplied main text.",
        "No SI was supplied; the announced spectra are unavailable.",
        "The isotopologue structure remains unverified and SMILES is null.",
    ],
))

# Scheme 3 / page-3 comparison paragraph is one mixed-substrate experiment.
records.append(rec(
    "scheme3_competition_3b_3c_3d", "reported_experiment", [P2T, P2I, P3T, P3I],
    [
        participant("cmp_3b", "reactant", "3b", names["3b"], [P2T, P2I, P3T], [
            fld("mass", {"number": 11.8, "unit": "mg"}, [P3T]), fld("amount", {"number": 0.1, "unit": "mmol"}, [P2T, P3T])]),
        participant("cmp_3c", "reactant", "3c", names["3c"], [P2T, P2I, P3T], [
            fld("mass", {"number": 19.4, "unit": "mg"}, [P3T]), fld("amount", {"number": 0.1, "unit": "mmol"}, [P2T, P3T])]),
        participant("cmp_3d", "reactant", "3d", names["3d"], [P2T, P2I, P3T], [
            fld("mass", {"number": 20.8, "unit": "mg"}, [P3T]), fld("amount", {"number": 0.1, "unit": "mmol"}, [P2T, P3T])]),
        participant("cmp_nai", "reagent", "NaI", "sodium iodide", [P2T, P2I, P3T], [
            fld("mass", {"number": 15, "unit": "mg"}, [P3T]), fld("amount", {"number": 0.1, "unit": "mmol"}, [P2T, P3T])]),
        participant("cmp_hoac", "solvent", "HOAc", "acetic acid", [P2T, P2I, P3T], [
            fld("volume", {"number": 1.5, "unit": "mL"}, [P3T])]),
        participant("cmp_4ba", "product", "4ba", names["4ba"], [P2T, P2I, P3T]),
        participant("cmp_4ca", "product", "4ca", names["4ca"], [P2T, P2I, P3T]),
        participant("cmp_4da", "product", "4da", names["4da"], [P2T, P2I, P3T]),
    ],
    conditions=[fld("temperature", {"number": 85, "unit": "°C"}, [P2T, P2I, P3T]),
                fld("time", {"number": 4, "unit": "h"}, [P2T, P2I, P3T]),
                fld("workup", "usual workup (not specified)", [P3T])],
    outcomes=[
        fld("4ba_yield", {"number": 69, "unit": "%"}, [P2T, P2I, P3T]),
        fld("4ba_yield_measurement_basis", "NMR", [P2T, P2I, P3T]),
        fld("4ca_formation", "not observed", [P2T, P2I, P3T]),
        fld("4da_formation", "not observed", [P2T, P2I, P3T]),
    ],
    unresolved=[
        "The printed 11.8 mg for 3b and stated 0.1 mmol may be internally inconsistent; both values are retained without correction.",
        "Atmosphere, concentration, detailed workup, NMR internal standard for this specific run, and detection limits for 4ca/4da are not reported.",
        "All structures remain unverified and SMILES are null.",
    ],
))

# Normalize record-level evidence order after augmenting records.
for item in records:
    item["evidence_ids"] = list(dict.fromkeys(item["evidence_ids"]))

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")

page1_ids = [r["record_id"] for r in records if P1T in r["evidence_ids"] or P1I in r["evidence_ids"]]
page2_ids = [r["record_id"] for r in records if P2T in r["evidence_ids"] or P2I in r["evidence_ids"]]
page3_ids = [r["record_id"] for r in records if P3T in r["evidence_ids"] or P3I in r["evidence_ids"]]
coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1,
            "state": "attempted",
            "regions": [
                {"region": "upper-right Scheme 1", "finding": "Two successive generic preparation arrows: propargylic alcohol/RSCl/Et3N to allenic sulfoxide 2, then H2O2 oxidation to generic allenic sulfone 3; 3a-d substitution table shown; attributed to cited preparation methods and not treated as fully specified individual runs.", "evidence_ids": [P1I, P1T]},
                {"region": "mid-right Scheme 2 and footnote", "finding": "Generic hydrohalogenation scheme and definitions of conditions A, B, and C; classified as general scheme, not a measured run.", "evidence_ids": [P1I, P1T]},
                {"region": "lower-right Results and Discussion", "finding": "Qualitative very-slow 3a/LiI/HOAc room-temperature observation and a separate 4ac/HOAc 118 °C, 11 h no-C=C-migration stability result.", "evidence_ids": [P1I, P1T]},
                {"region": "left-column introduction and references", "finding": "Prior hydrohalogenation and historical synthesis methods are cited background; no current-paper experiment was fabricated from these prose references.", "evidence_ids": [P1I, P1T]},
            ],
            "record_ids": page1_ids,
            "unresolved": [
                "Scheme 1 lacks row-specific charges, times, temperatures, yields, and workups.",
                "The room-temperature slow-reaction observation lacks product identity, time, conversion, yield, and analytical basis.",
                "All drawing-derived structures remain unverified and have null SMILES.",
            ],
        },
        {
            "page": 2,
            "state": "attempted",
            "regions": [
                {"region": "upper-left Table 1", "finding": "Eleven hydrohalogenation rows for 3a were split row by row, including recovered-starting-material footnotes and aqueous-acid concentrations.", "evidence_ids": [P2I, P2T]},
                {"region": "mid-left Table 2", "finding": "Eighteen rows for 3b-d were split row by row; isolated versus NMR yield footnotes and 3b recovery were applied only to their rows.", "evidence_ids": [P2I, P2T]},
                {"region": "lower-left equation 1 and prose", "finding": "3a/NaI/DOAc deuterium-labeling experiment gives 4aa′ in 77% yield with >97% D incorporation; merged with page-3 preparation details.", "evidence_ids": [P2I, P2T]},
                {"region": "upper-right Scheme 3 and adjacent prose", "finding": "One mixed-substrate competition experiment: 4ba 69% by NMR; 4ca and 4da not formed; merged with page-3 charge details.", "evidence_ids": [P2I, P2T]},
                {"region": "lower-right Experimental Section start", "finding": "General analytical statements and the Conditions-A 4aa procedure begin; linked to Table 1 entry 1 rather than duplicated.", "evidence_ids": [P2I, P2T]},
            ],
            "record_ids": page2_ids,
            "unresolved": [
                "Table 1 entry 1 prints 0.5 h while its matching typical procedure prints 1.5 h.",
                "Most table rows lack row-specific charges, atmosphere, concentration, workup, purification, and isolated mass.",
                "No detection limits are reported for not-observed products in Scheme 3.",
            ],
        },
        {
            "page": 3,
            "state": "attempted",
            "regions": [
                {"region": "upper-left continuation of Conditions-A 4aa procedure", "finding": "Completes isolation, chromatography, 197 mg/80% yield, physical state, and melting point for the run matched to Table 1 entry 1.", "evidence_ids": [P3I, P3T]},
                {"region": "left column Conditions-B and Conditions-C typical procedures", "finding": "Detailed 4aa procedures correspond to Table 1 entries 7 and 10 and were merged into those rows.", "evidence_ids": [P3I, P3T]},
                {"region": "left/lower and right/upper product preparation paragraphs b-i", "finding": "Exact charges, isolated masses, states, and melting points where printed were linked to Table 1 entries 4 and 6 and Table 2 entries 1, 2, 4, 12, 14, and 17; characterization paragraphs were not duplicated as reactions.", "evidence_ids": [P3I, P3T]},
                {"region": "right-lower deuteration and reactivity-comparison paragraphs", "finding": "Detailed Eq. 1 and Scheme 3 charge/outcome information was merged into the two existing page-2 experiments.", "evidence_ids": [P3I, P3T]},
                {"region": "bottom-right Supporting Information notice", "finding": "The article announces spectra in SI, but no SI file is supplied or explicitly associated; SI-only information remains unavailable.", "evidence_ids": [P3I, P3T]},
            ],
            "record_ids": page3_ids,
            "unresolved": [
                "The paper's announced SI is absent and no association was inferred.",
                "The printed 11.8 mg and 0.1 mmol values for 3b in the competition experiment may be internally inconsistent.",
                "Characterization was not used to certify any depicted structure; all SMILES remain null and structures unverified.",
            ],
        },
    ],
}
COVERAGE.parent.mkdir(parents=True, exist_ok=True)
COVERAGE.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"records": len(records), "output": str(OUT), "coverage": str(COVERAGE)}, ensure_ascii=False))
