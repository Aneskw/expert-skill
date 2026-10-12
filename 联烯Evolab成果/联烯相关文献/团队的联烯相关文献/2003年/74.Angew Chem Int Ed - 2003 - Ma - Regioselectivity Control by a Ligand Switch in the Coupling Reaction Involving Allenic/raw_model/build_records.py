#!/usr/bin/env python3
"""Build source-linked machine candidates for doc_116c6d59dc695465.

This is a raw extraction artifact, not a source review.  The merge tool will
quarantine every record as needs_review and every non-null fact as unreviewed.
"""
import json
from pathlib import Path

DOC = "doc_116c6d59dc695465"
P1 = [f"{DOC}:page1:text", f"{DOC}:page1:image"]
P2 = [f"{DOC}:page2:text", f"{DOC}:page2:image"]
P3 = [f"{DOC}:page3:text", f"{DOC}:page3:image"]


def fact(value, ev=None):
    return {
        "value": value,
        "evidence_ids": list(ev or []) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def field(name, value, ev=None, targets=None):
    item = {"name": name, "fact": fact(value, ev)}
    if targets:
        item["target_entity_ids"] = list(targets)
    return item


def participant(entity_id, role, label, ev, *, name=None, smiles=None, amounts=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, ev),
        "name": fact(name, ev) if name else fact(None),
        "smiles": fact(smiles, ev) if smiles else fact(None),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": amounts or [],
    }


def record(suffix, kind, ev, participants, steps, outcomes, *, notes=None, unresolved=None, source_id=None):
    return {
        "record_id": f"{DOC}:{suffix}",
        "document_id": DOC,
        "source_reaction_id": source_id or suffix,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": list(dict.fromkeys(ev)),
        "participants": participants,
        "steps": steps,
        "outcomes": outcomes,
        "notes": [fact(x, ev) for x in (notes or [])],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": list(unresolved or []),
        },
    }


def amt(name, value, ev):
    return field(name, value, ev)


SMILES = {
    "thf": "C1CCOC1",
    "pph3": "P(c1ccccc1)(c1ccccc1)c1ccccc1",
    "iproh": "CC(C)O",
    "phenol": "Oc1ccccc1",
    "water": "O",
    "ether": "CCOCC",
    "hexane": "CCCCCC",
    "mgso4": "[Mg+2].[O-]S(=O)(=O)[O-]",
    "1a": "CC(C)(C)[Si](C)(C)C#CC(CCCC)OS(=O)(=O)C",
    "1b": "C[Si](C)(C)C#CC(CCCCCCCC)OS(=O)(=O)C",
    "3a": "CC(C)(C)[Si](C)(C)C#CC(CCCC)/C=C/C(=O)OCC",
    "4a": "CC(C)(C)[Si](C)(C)C=C=C(CCCC)/C=C/C(=O)OCC",
    "3b": "C[Si](C)(C)C#CC(CCCCCCCC)/C=C/C(=O)OCC",
    "4b": "C[Si](C)(C)C=C=C(CCCCCCCC)/C=C/C(=O)OCC",
    "5": "CC(C)(C)[Si](C)(C)C#CC(CCCC)c1ccccc1",
    "6": "CC(C)(C)[Si](C)(C)C=C=C(CCCC)c1ccccc1",
}


def substrate(label, ev, *, detailed=False):
    names = {
        "1a": "propargylic mesylate 1a (R1=TBS, R2=n-C4H9)",
        "1b": "propargylic mesylate 1b (R1=TMS, R2=n-C8H17)",
        "1c": "propargylic mesylate 1c (R1=TMS, R2=allyl)",
        "1d": "propargylic mesylate 1d (R1=TMS, R2=Bn)",
        "1e": "propargylic mesylate 1e (R1=TBSOCH2, R2=n-C8H17)",
        "1f": "propargylic mesylate 1f (R1=tBu, R2=n-C4H9)",
        "1g": "propargylic bromide 1g (R1=n-C5H11, R2=H)",
    }
    amounts = []
    if detailed and label == "1b":
        # Added by the caller because the two preparations used different scales.
        amounts = []
    return participant(f"substrate_{label}", "reactant", label, ev, name=names[label], smiles=SMILES.get(label), amounts=amounts)


def organozinc(ev, amounts=None):
    return participant(
        "organozinc_2", "reactant", "2", ev,
        name="(Z)-(2)-ethoxycarbonylethenyl zinc iodide",
        amounts=amounts or [amt("equivalents", {"number": 1.5, "unit": "equiv"}, ev)],
    )


def pd_allyl(ev, amounts=None):
    return participant(
        "pd_allyl_chloride_dimer", "catalyst", "[PdCl(pi-C3H5)]2", ev,
        name="allylpalladium chloride dimer",
        amounts=amounts or [amt("loading", {"number": 2, "unit": "mol%"}, ev)],
    )


def ligand(label, ev, amounts=None):
    names = {
        "PPh3": "triphenylphosphane",
        "L1": "2-diphenylphosphinophenyl carboxylic acid",
        "L2": "4-hydroxybutyldiphenylphosphane",
        "L3": "2-diphenylphosphino-2'-hydroxy-1,1'-binaphthalene",
        "L4": "binaphthol L4",
        "L5": "methoxy analogue L5",
    }
    return participant(
        f"ligand_{label}", "reagent", label, ev, name=names[label],
        smiles=SMILES.get("pph3") if label == "PPh3" else None,
        amounts=amounts or [amt("loading", {"number": 10, "unit": "mol%"}, ev)],
    )


def thf(ev, amounts=None):
    return participant("solvent_thf", "solvent", "THF", ev, name="tetrahydrofuran", smiles=SMILES["thf"], amounts=amounts or [])


def products(pair, ev):
    a, b = pair
    return [
        participant(f"product_{a}", "product", a, ev, name=f"alkyne/en-yne product {a}", smiles=SMILES.get(a.lstrip("Z-"))),
        participant(f"product_{b}", "product", b, ev, name=f"allene product {b}", smiles=SMILES.get(b.lstrip("E-"))),
    ]


records = []

# Page 1: three arrows summarize prior work [5c], not experiments reported here.
scheme1_notes = [
    ("scheme1_arrow_r2_h", "Prior-work generic rule: R2=H is depicted as favoring an alkyne product."),
    ("scheme1_arrow_r2_non_h", "Prior-work generic rule: R2=non-H is depicted as favoring an allene product."),
    ("scheme1_arrow_steric", "Prior-work generic steric rule compares R1, R2 and R3 and depicts an alkyne product."),
]
for suffix, note in scheme1_notes:
    parts = [
        participant("generic_organopalladium", "reactant", "generic propargylic/allenic palladium species", P1),
        participant("generic_product", "product", "generic regioisomeric product", P1),
    ]
    records.append(record(
        suffix, "literature_example", P1, parts,
        [{"step_id": "depicted_arrow", "participant_ids": [p["entity_id"] for p in parts], "conditions": []}],
        [], notes=[note, "Scheme 1 is attributed in the prose to earlier work [5c]."],
        unresolved=["Generic R-group structures and experimental conditions are not specified in this paper."],
    ))

# Page 1: Scheme 2 is a mechanistic proposal, split by product-forming pathway.
for suffix, intermediate, product_label in [
    ("scheme2_propargyl_pathway", "propargyl palladium intermediate", "generic alkyne product"),
    ("scheme2_allenyl_pathway", "allenyl palladium intermediate", "generic allene product"),
]:
    parts = [
        participant("pd_intermediate", "reactant", intermediate, P1),
        participant("generic_product", "product", product_label, P1),
    ]
    records.append(record(
        suffix, "mechanism", P1, parts,
        [{"step_id": "proposed_product_formation", "participant_ids": [p["entity_id"] for p in parts], "conditions": []}],
        [], notes=["Scheme 2 proposes ligand-electronic control of the propargyl/allenyl palladium equilibrium."],
        unresolved=["Mechanistic drawing is not an isolated experimental transformation and uses generic R groups."],
    ))

# Page 1 prose: carbonate and acetate screens did not react under the stated model conditions.
for leaving_group in ["carbonate", "acetate"]:
    ev = P1
    parts = [
        participant(f"propargylic_{leaving_group}", "reactant", f"propargylic {leaving_group}", ev),
        organozinc(ev),
        participant("pd_pph3_4", "catalyst", "[Pd(PPh3)4]", ev, name="tetrakis(triphenylphosphine)palladium(0)"),
        thf(ev),
    ]
    records.append(record(
        f"initial_screen_{leaving_group}_nr", "reported_experiment", ev, parts,
        [{"step_id": "screen", "participant_ids": [p["entity_id"] for p in parts], "conditions": [field("temperature", "r.t.", ev), field("time", None)]}],
        [field("reaction_result", "no reaction", ev), field("yield", None)],
        notes=["The prose states that the carbonate and acetate did not react at room temperature; individual duration and structures are not given."],
        unresolved=["Reaction duration, substrate structure, expected products, catalyst loading, atmosphere, workup and yield basis are missing.", "No supporting information was explicitly provided or associated."],
    ))


def table1_parts(entry, ligand_label, ev):
    parts = [
        substrate("1a", ev), organozinc(ev),
        participant("product_3a", "product", "3a", ev, name="enyne/alkyne product 3a", smiles=SMILES["3a"]),
        participant("product_4a", "product", "4a", ev, name="allene product 4a", smiles=SMILES["4a"]),
        thf(ev),
    ]
    if entry == 1:
        parts.append(participant("pd_pph3_4", "catalyst", "[Pd(PPh3)4]", ev, name="tetrakis(triphenylphosphine)palladium(0)"))
    else:
        parts.append(pd_allyl(ev))
        parts.append(ligand(ligand_label, ev))
    if entry == 4:
        parts.append(participant("additive_iproh", "reagent", "iPrOH", ev, name="2-propanol", smiles=SMILES["iproh"], amounts=[amt("loading", {"number": 10, "unit": "mol%"}, ev)]))
    if entry == 6:
        parts.append(participant("additive_phoh", "reagent", "PhOH", ev, name="phenol", smiles=SMILES["phenol"], amounts=[amt("loading", {"number": 10, "unit": "mol%"}, ev)]))
    if entry == 8:
        parts.append(ligand("PPh3", ev))
    return parts


table1 = [
    # entry, ligand, time h, yield, ratio
    (1, None, 26, 68, ">97:3"),
    (2, "L1", 24, 25, "12:88"),
    (3, "L2", 24, 43, "16:84"),
    (4, "PPh3", 24, 46, "96:4"),
    (5, "L3", 16, 49, "<3:97"),
    (6, "PPh3", 9, 59, ">97:3"),
    (7, "L4", 48, None, None),
    (8, "L4", 12, 65, ">97:3"),
    (9, "L5", 48, 43, "92:8"),
]
for entry, lig, hours, yld, ratio in table1:
    ev = P2 + (P1 if entry in {1, 2, 3, 5, 7, 8, 9} else [])
    parts = table1_parts(entry, lig, ev)
    ids = [p["entity_id"] for p in parts]
    outcomes = []
    if entry == 7:
        outcomes = [field("reaction_result", "NR (no reaction)", ev), field("yield", None)]
    else:
        outcomes = [field("yield", {"number": yld, "unit": "%"}, ev, ["product_3a", "product_4a"]), field("product_ratio_3a_to_4a", ratio, ev, ["product_3a", "product_4a"])]
    notes = ["Table 1 yield basis is not stated; the yield is associated with the displayed product pair rather than assigned to one regioisomer."]
    unresolved = ["Yield measurement basis and atmosphere are not reported.", "Candidate SMILES for 1a/3a/4a require human comparison with the drawing.", "No supporting information was explicitly provided or associated."]
    if entry == 1:
        unresolved.append("The table footnote replaces the standard catalyst with [Pd(PPh3)4], but does not state its loading.")
    if entry == 9:
        notes.append("Table 1 reports 43% yield, whereas the page-1 narrative says 45% combined yield.")
        outcomes.append(field("narrative_combined_yield", {"number": 45, "unit": "%"}, P1, ["product_3a", "product_4a"]))
        unresolved.append("The 43% table yield versus 45% narrative yield discrepancy requires source review.")
    suffix = "table1_entry5_table2_entry2" if entry == 5 else f"table1_entry{entry}"
    if entry == 5:
        notes.append("The same 1a/L3 result is repeated in Table 2 entry 2 (49%, 3a/4a=3:97); it is retained once.")
    records.append(record(
        suffix, "optimization_entry", ev, parts,
        [{"step_id": "coupling", "participant_ids": ids, "conditions": [field("solvent", "THF", ev), field("temperature", "r.t.", ev), field("time", {"number": hours, "unit": "h"}, P2)]}],
        outcomes, notes=notes, unresolved=unresolved,
        source_id=f"Table 1 entry {entry}" + (" / Table 2 entry 2" if entry == 5 else ""),
    ))


table2 = [
    # row, substrate, ligand, yield, listed product, ratio
    (1, "1a", "PPh3", 68, ["3a"], ">97:3"),
    # Row 2 is the duplicate of Table 1 entry 5 and was merged above.
    (3, "1b", "PPh3", 68, ["3b"], "94:6"),
    (4, "1b", "L3", 82, ["4b"], "5:95"),
    (5, "1c", "PPh3", 44, ["3c"], "95:5"),
    (6, "1c", "L3", 51, ["4c"], "4:96"),
    (7, "1d", "PPh3", 42, ["3d"], ">93:7"),
    (8, "1d", "L3", 66, ["4d"], "<3:97"),
    (9, "1e", "L3", 68, ["4e"], "<3:97"),
    (10, "1f", "PPh3", 69, ["3f", "4f"], "50:50"),
    (11, "1f", "L3", 64, ["4f"], "0:100"),
    (12, "1g", "L3", 63, ["4g"], "0:100"),
]


def scope_products(labels, ev):
    result = []
    suffix = labels[0][-1]
    for prefix in ["3", "4"]:
        label = f"{prefix}{suffix}"
        result.append(participant(
            f"product_{label}", "product", label, ev,
            name=("enyne/alkyne product " if prefix == "3" else "allene product ") + label,
            smiles=SMILES.get(label),
        ))
    return result


for row, sub, lig, yld, listed_products, ratio in table2:
    ev = P2 + (P3 if row in {3, 4} else [])
    detailed = row in {3, 4}
    subp = substrate(sub, ev, detailed=detailed)
    if row == 3:
        subp["amounts"] = [amt("mass", {"number": 60, "unit": "mg"}, P3), amt("amount", {"number": 0.19, "unit": "mmol"}, P3)]
        zinc_amounts = [amt("volume", {"number": 0.28, "unit": "mL"}, P3), amt("concentration", {"number": 1.0, "unit": "M"}, P3), amt("amount", {"number": 0.28, "unit": "mmol"}, P3)]
        cat_amounts = [amt("mass", {"number": 1.4, "unit": "mg"}, P3), amt("amount", {"number": 0.0038, "unit": "mmol"}, P3), amt("loading", {"number": 2, "unit": "mol%"}, P2)]
        lig_amounts = [amt("mass", {"number": 4.9, "unit": "mg"}, P3), amt("amount", {"number": 0.019, "unit": "mmol"}, P3), amt("loading", {"number": 10, "unit": "mol%"}, P2)]
    elif row == 4:
        subp["amounts"] = [amt("mass", {"number": 73.2, "unit": "mg"}, P3), amt("amount", {"number": 0.23, "unit": "mmol"}, P3)]
        zinc_amounts = [amt("volume", {"number": 0.46, "unit": "mL"}, P3), amt("concentration", {"number": 1.0, "unit": "M"}, P3), amt("amount", {"number": 0.46, "unit": "mmol"}, P3)]
        cat_amounts = [amt("mass", {"number": 1.8, "unit": "mg"}, P3), amt("amount", {"number": 0.0046, "unit": "mmol"}, P3), amt("loading", {"number": 2, "unit": "mol%"}, P2)]
        lig_amounts = [amt("mass", {"number": 10.4, "unit": "mg"}, P3), amt("amount", {"number": 0.023, "unit": "mmol"}, P3), amt("loading", {"number": 10, "unit": "mol%"}, P2)]
    else:
        zinc_amounts = [amt("equivalents", {"number": 1.5, "unit": "equiv", "qualifier": "approx", "raw_text": "≈1.5 equiv"}, P2)]
        cat_amounts = [amt("loading", {"number": 2, "unit": "mol%"}, P2)]
        lig_amounts = [amt("loading", {"number": 10, "unit": "mol%"}, P2)]
    parts = [subp, organozinc(ev, zinc_amounts), pd_allyl(ev, cat_amounts), ligand(lig, ev, lig_amounts), thf(ev, [amt("volume", {"number": 5, "unit": "mL"}, P2 + P3)] if detailed else [])]
    parts += scope_products(listed_products, ev)
    ids = [p["entity_id"] for p in parts]
    target_ids = [f"product_{x}" for x in listed_products]
    steps = [{"step_id": "coupling", "participant_ids": ids, "conditions": [field("solvent", "THF", P2), field("temperature", "r.t.", P2), field("time", "overnight", P2)]}]
    notes = ["Table 2 yield is assigned to the product label(s) printed in parentheses in that row."]
    unresolved = ["Yield measurement basis and atmosphere are not reported.", "Structures not encoded as SMILES remain dependent on R-group/drawing review.", "No supporting information was explicitly provided or associated."]
    if row in {3, 4}:
        workup = [
            participant("workup_water", "reagent", "water", P2, smiles=SMILES["water"]),
            participant("extract_ether", "solvent", "diethyl ether", P2, smiles=SMILES["ether"]),
            participant("wash_brine", "reagent", "brine", P2),
            participant("dry_mgso4", "reagent", "MgSO4", P2, name="magnesium sulfate", smiles=SMILES["mgso4"]),
            participant("chrom_silica", "reagent", "silica gel", P2),
            participant("eluent_hexane", "solvent", "hexane", P2, smiles=SMILES["hexane"]),
        ]
        parts.extend(workup)
        ids = [p["entity_id"] for p in parts]
        steps = [
            {"step_id": "preactivation", "participant_ids": [subp["entity_id"], "pd_allyl_chloride_dimer", f"ligand_{lig}", "solvent_thf"], "conditions": [field("temperature", "r.t.", P2), field("time", {"number": 20, "unit": "min"}, P2)]},
            {"step_id": "coupling", "participant_ids": [subp["entity_id"], "organozinc_2", "pd_allyl_chloride_dimer", f"ligand_{lig}", "solvent_thf"], "conditions": [field("temperature", "r.t.", P2), field("time", "overnight", P2), field("monitoring", "TLC until complete", P2)]},
            {"step_id": "workup", "participant_ids": ["workup_water", "extract_ether", "wash_brine", "dry_mgso4"], "conditions": [field("workup", "quenched with water; extracted with diethyl ether; washed with water and brine; dried over MgSO4; solvent removed by rotary evaporation", P2)]},
            {"step_id": "purification", "participant_ids": ["chrom_silica", "eluent_hexane", "extract_ether"], "conditions": [field("purification", "silica-gel column chromatography, hexane/diethyl ether 50:1", P2)]},
        ]
        product_mass = 41.4 if row == 3 else 60.4
        outcomes_extra = field("product_mass", {"number": product_mass, "unit": "mg"}, P3, target_ids)
        notes.append("The detailed page-3 preparation is the same Table 2 entry and is merged into this record.")
        if row == 4:
            notes.append("The explicit 4b preparation used 0.46 mmol reagent 2 with 0.23 mmol 1b; this exact amount supersedes the approximate 1.5-equiv scheme header for this run.")
    else:
        outcomes_extra = None
    outcomes = [field("yield", {"number": yld, "unit": "%"}, ev, target_ids), field("product_ratio_3_to_4", ratio, P2, [p["entity_id"] for p in scope_products(listed_products, ev)])]
    if outcomes_extra:
        outcomes.append(outcomes_extra)
    if row == 1:
        unresolved.append("This row resembles Table 1 entry 1 numerically, but Table 2 depicts [PdCl(pi-C3H5)]2/PPh3 whereas Table 1 explicitly uses [Pd(PPh3)4]; retained as distinct conditions.")
    records.append(record(
        f"table2_entry{row}", "substrate_scope_entry", ev, parts, steps, outcomes,
        notes=notes, unresolved=unresolved, source_id=f"Table 2 entry {row}",
    ))

# Page 2 Scheme 3: one reaction scheme with two explicitly separate ligand runs.
for lig, yld, ratio in [("PPh3", 74, "5:6 = 9:1"), ("L3", 77, "5:6 = 1:8")]:
    ev = P2
    parts = [
        substrate("1a", ev),
        participant("phznbr", "reactant", "PhZnBr", ev, name="phenylzinc bromide", amounts=[amt("equivalents", {"number": 2, "unit": "equiv"}, ev)]),
        pd_allyl(ev), ligand(lig, ev), thf(ev),
        participant("product_5", "product", "5", ev, name="alkyne product 5", smiles=SMILES["5"]),
        participant("product_6", "product", "6", ev, name="allene product 6", smiles=SMILES["6"]),
    ]
    records.append(record(
        f"scheme3_{lig.lower()}", "substrate_scope_entry", ev, parts,
        [{"step_id": "coupling", "participant_ids": [p["entity_id"] for p in parts], "conditions": [field("solvent", "THF", ev), field("temperature", "r.t.", ev), field("time", "overnight", ev)]}],
        [field("combined_yield", {"number": yld, "unit": "%"}, ev, ["product_5", "product_6"]), field("product_ratio_5_to_6", ratio, ev, ["product_5", "product_6"])],
        notes=["PhZnBr is stated in the prose to have been prepared by transmetalation of PhMgBr with ZnBr2 in THF; no separate preparation details are given."],
        unresolved=["Yield measurement basis, atmosphere, workup and purification are not reported for Scheme 3.", "Candidate SMILES for 5 and 6 require human comparison with the drawing.", "No supporting information was explicitly provided or associated."],
        source_id=f"Scheme 3, L={lig}",
    ))

# Page 2 prose: additional catalyst/solvent observations are real source claims but
# cannot be mapped to fully specified table rows, so they remain unresolved records.
for catalyst_label in ["Pd2(dba)3", "PdCl2"]:
    ev = P2
    parts = [substrate("1a", ev), organozinc(ev), participant("screen_catalyst", "catalyst", catalyst_label, ev), thf(ev)]
    records.append(record(
        "precatalyst_" + catalyst_label.replace("(", "_").replace(")", "").replace("[", "").replace("]", "").replace("2", "2").lower(),
        "unresolved", ev, parts,
        [{"step_id": "precatalyst_screen", "participant_ids": [p["entity_id"] for p in parts], "conditions": [field("solvent", "THF", ev)]}],
        [field("reaction_result", "same ligand-dependent regioselectivity control was observed", ev)],
        notes=["The prose does not state which ligand run(s), product ratios, yields, loadings or times correspond to this precatalyst."],
        unresolved=["Exact experiment identity, ligand pairing, quantities, time, temperature and outcomes are not reported."],
    ))

for solvent_label, solvent_smiles in [("CH2Cl2", "ClCCl"), ("CH3CN", "CC#N"), ("DMF", "CN(C)C=O"), ("1,4-dioxane", "O1CCOCC1")]:
    ev = P2
    parts = [substrate("1a", ev), organozinc(ev), participant("screen_solvent", "solvent", solvent_label, ev, smiles=solvent_smiles)]
    records.append(record(
        "solvent_screen_" + solvent_label.replace(",", "").replace("-", "_").lower(),
        "unresolved", ev, parts,
        [{"step_id": "solvent_screen", "participant_ids": [p["entity_id"] for p in parts], "conditions": [field("solvent", solvent_label, ev)]}],
        [field("reaction_result", "complicated results", ev), field("yield", None)],
        notes=["The prose groups these solvents together and does not provide row-level catalyst/ligand assignments, yields or product ratios."],
        unresolved=["Exact catalyst, ligand, quantities, time, temperature, products and yield are not reported."],
    ))


assert len(records) == 35, len(records)
out = Path(__file__).with_name("extracted_records.json")
out.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
print(f"wrote {len(records)} records to {out}")
