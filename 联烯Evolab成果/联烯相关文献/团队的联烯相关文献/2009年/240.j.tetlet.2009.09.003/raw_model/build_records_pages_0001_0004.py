#!/usr/bin/env python3
"""Build evidence-linked machine records for doc_a4641608feaee53c, PDF pages 1-4."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOC = "doc_a4641608feaee53c"
OUT = Path(__file__).with_name("records_pages_0001_0004.json")
P = {
    n: [f"{DOC}:page{n}:text", f"{DOC}:page{n}:image"] for n in range(1, 5)
}


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
    item = {"name": name, "fact": fact(value, evidence)}
    if targets:
        item["target_entity_ids"] = list(targets)
    return item


def participant(entity_id, role, label, evidence, *, name=None, smiles=None, amounts=None):
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


def record(suffix, kind, evidence, participants, steps=None, outcomes=None, notes=None, unresolved=None):
    return {
        "record_id": f"{DOC}:{suffix}",
        "document_id": DOC,
        "source_reaction_id": suffix,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": list(dict.fromkeys(evidence)),
        "participants": participants,
        "steps": steps or [],
        "outcomes": outcomes or [],
        "notes": [fact(x, evidence) for x in (notes or [])],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved or [],
        },
    }


records = []

# Scheme 1 contains a cited/prior generic propargylic-alcohol route and a separate
# generic route proposed for the present alkenynol chemistry. Neither is a batch.
ev = P[1]
prior_parts = [
    participant("generic_propargylic_alcohol", "reactant", "generic propargylic alcohol", ev),
    participant("generic_grignard", "reagent", "R2MgX", ev),
    participant("generic_copper", "catalyst", "Cu(I)", ev),
    participant("intermediate_A", "product", "cyclic magnesium intermediate A", ev),
    participant("generic_allenol", "product", "generic 2,3-allenol", ev),
]
records.append(record(
    "scheme1_prior_propargylic_route", "literature_example", ev, prior_parts,
    steps=[
        {"step_id": "carbometallation", "participant_ids": ["generic_propargylic_alcohol", "generic_grignard", "generic_copper", "intermediate_A"],
         "conditions": [field("operation", "Cu(I)-mediated carbometallation as summarized from prior work", ev)]},
        {"step_id": "hydrolysis", "participant_ids": ["intermediate_A", "generic_allenol"],
         "conditions": [field("operation", "acidic hydrolysis (H+)", ev)]},
    ],
    notes=["Scheme 1 summarizes cited prior carbometallation chemistry; it is not a newly reported experiment in this paper."],
    unresolved=["Generic R groups and Cu(I)/X identities are unspecified; structures remain unverified."],
))

ev = P[1] + P[2]
current_parts = [
    participant("generic_alkenynol", "reactant", "generic 4-alken-2-ynol (R3-substituted)", ev),
    participant("generic_grignard", "reagent", "R2MgX", ev),
    participant("generic_copper", "catalyst", "Cu(I)", ev),
    participant("intermediate_B", "product", "cyclic magnesium intermediate B", ev),
    participant("intermediate_C", "product", "allene-containing magnesium intermediate C", ev),
    participant("expected_allenol", "product", "expected 2,3-allenol", ev),
    participant("generic_trienol", "product", "6-perfluoroalkyl-6-fluoro-2,3,5(Z)-trienol (this report)", ev),
]
records.append(record(
    "scheme1_current_generic_route", "general_scheme", ev, current_parts,
    steps=[
        {"step_id": "generic_carbometallation", "participant_ids": ["generic_alkenynol", "generic_grignard", "generic_copper", "intermediate_B"],
         "conditions": [field("operation", "generic carbometallation", ev)]},
        {"step_id": "generic_rearrangement", "participant_ids": ["intermediate_B", "intermediate_C"],
         "conditions": [field("operation", "allylic rearrangement with loss of 2 X−", ev)]},
        {"step_id": "generic_product_paths", "participant_ids": ["intermediate_C", "expected_allenol", "generic_trienol"],
         "conditions": [field("operation", "hydrolysis gives the expected allenol path; R3=RfCF2 gives the trienol path reported here", ev)]},
    ],
    notes=["This is a generic reaction concept, not an individual batch or a source of row-specific yield."],
    unresolved=["Generic R groups, X, and exact structures are unspecified; the scheme does not report batch quantities."],
))


table1 = [
    (1, 50, -78, True, "Toluene", 1.0, 92, 80, "PhMgBr", 4.5, 2.0, 0.45, 0.9),
    (2, 50, 0, True, "Toluene", 1.0, 95, 91, "PhMgBr", 4.5, 2.0, 0.45, 0.9),
    (3, 50, 0, True, "THF", 1.0, 18, 13, "PhMgBr", 4.5, 2.0, 0.45, 0.9),
    (4, 50, 0, True, "Et2O", 1.0, 96, 92, "PhMgBr", 4.5, 2.0, 0.45, 0.9),
    (5, 0, 0, True, "Et2O", 1.0, 96, 86, "PhMgBr", 4.5, 2.0, 0.45, 0.9),
    (6, 0, None, False, "Et2O", 1.0, 97, 85, "PhMgBr", 4.5, 2.0, 0.45, 0.9),
    (7, 0, None, False, "Et2O", 0.5, 99, 89, "PhMgCl", 4.5, 1.73, None, None),
    (8, 0, None, False, "Et2O", 0.5, 99, 94, "PhMgCl", 4.0, 1.73, None, None),
]
solvent_smiles = {"Toluene": "Cc1ccccc1", "THF": "C1CCOC1", "Et2O": "CCOCC"}

for entry, cu_loading, initial_temp, warms, solvent, solv_vol, conversion, nmr_yield, grignard, equiv, conc, soln_vol, mmol in table1:
    ev = P[2]
    sub_amounts = [field("amount", qty(0.20, "mmol"), ev)]
    reagent_amounts = [field("equivalents", qty(equiv, "equiv"), ev), field("concentration", qty(conc, "M"), ev)]
    if soln_vol is not None:
        reagent_amounts.append(field("volume", qty(soln_vol, "mL"), ev))
    if mmol is not None:
        reagent_amounts.append(field("amount", qty(mmol, "mmol"), ev))
    parts = [
        participant("E1a", "reactant", "E-1a (R1=n-C4H9, Rf=n-C3F7)", ev, amounts=sub_amounts),
        participant("grignard", "reagent", f"{grignard} in THF", ev, amounts=reagent_amounts),
        participant("reaction_solvent", "solvent", solvent, ev, smiles=solvent_smiles[solvent], amounts=[field("volume", qty(solv_vol, "mL"), ev)]),
        participant("Z2a", "product", "Z-2a", ev),
    ]
    if entry == 1:
        parts.append(participant("product_3a", "product", "expected allenol 3a", ev))
    if cu_loading:
        parts.insert(2, participant("CuCl", "catalyst", "CuCl", ev, amounts=[field("catalyst_loading", qty(cu_loading, "mol%"), ev)]))
    conditions = [field("solvent", solvent, ev), field("time", qty(2, "h"), ev)]
    if initial_temp is None:
        conditions.append(field("temperature", "r.t.", ev))
    else:
        conditions.append(field("initial_temperature", qty(initial_temp, "°C"), ev))
        if warms:
            conditions.append(field("warm_to", "r.t.", ev))
    conditions.append(field("operation", "CuCl omitted" if cu_loading == 0 else "CuCl present", ev))
    outcomes = [
        field("conversion", qty(conversion, "%"), ev, ["E1a"]),
        field("nmr_yield", qty(nmr_yield, "%"), ev, ["Z2a"]),
        field("yield_measurement_basis", "1H NMR", ev, ["Z2a"]),
    ]
    if entry == 1:
        outcomes.append(field("expected_product_result", "not formed", ev, ["product_3a"]))
    records.append(record(
        f"table1_entry{entry}", "optimization_entry", ev, parts,
        steps=[{"step_id": "reaction", "participant_ids": [p["entity_id"] for p in parts], "conditions": conditions}],
        outcomes=outcomes,
        notes=["Expected product 3a is drawn in brackets, while the observed product is Z-2a."],
        unresolved=["Atmosphere, workup, purification, conversion basis, and exact product structure are not reported in this optimization row; SI was not provided."],
    ))


scope = [
    (1, "n-C4H9", "n-C3F7", "E-1a", "Ph", "PhMgCl", "Z-2a", 95, None),
    (2, "n-C4H9", "n-C3F7", "E-1a", "p-CH3C6H4", "p-CH3C6H4MgBr", "Z-2b", 87, None),
    (3, "n-C4H9", "n-C3F7", "E-1a", "p-CH3OC6H4", "p-CH3OC6H4MgBr", "Z-2c", 93, 4),
    (4, "n-C4H9", "n-C3F7", "E-1a", "p-FC6H4", "p-FC6H4MgBr", "Z-2d", 89, 4),
    (5, "n-C4H9", "n-C3F7", "E-1a", "n-C4H9", "n-C4H9MgCl", "Z-2e", 68, None),
    (6, "n-C4H9", "n-C3F7", "E-1a", "n-C5H11", "n-C5H11MgCl", "Z-2f", 66, None),
    (7, "n-C4H9", "n-C3F7", "E-1a", "i-Pr", "i-PrMgCl", "Z-2g", 84, None),
    (8, "n-C6H13", "n-C3F7", "E-1b", "Ph", "PhMgCl", "Z-2h", 94, None),
    (9, "n-C6H13", "n-C3F7", "E-1b", "p-CH3C6H4", "p-CH3C6H4MgBr", "Z-2i", 83, None),
    (10, "n-C6H13", "n-C3F7", "E-1b", "p-CH3OC6H4", "p-CH3OC6H4MgBr", "Z-2j", 82, None),
    (11, "n-C6H13", "n-C3F7", "E-1b", "p-FC6H4", "p-FC6H4MgBr", "Z-2k", 93, 4),
    (12, "n-C6H13", "n-C3F7", "E-1b", "n-C4H9", "n-C4H9MgCl", "Z-2l", 73, None),
    (13, "n-C4H9", "n-C5F11", "E-1c", "Ph", "PhMgCl", "Z-2m", 91, 5),
    (14, "n-C6H13", "n-C5F11", "E-1d", "Ph", "PhMgCl", "Z-2n", 92, None),
    (15, "n-C4H9", "n-C7F15", "E-1e", "Ph", "PhMgCl", "Z-2o", 95, 4),
    (16, "Ph", "n-C5F11", "E-1f", "Ph", "PhMgBr", "Z-2p", 80, 4),
    (17, "Ph", "n-C7F15", "E-1g", "Ph", "PhMgBr", "Z-2q", 83, 4),
]

for entry, r1, rf, substrate, r2, reagent, product, isolated_yield, recovery_bound in scope:
    base_ev = P[2]
    detailed = entry == 1
    ev = base_ev + (P[3] if detailed else [])
    sub_amounts = []
    reagent_amounts = [field("equivalents", qty(3 if entry in (16, 17) else 4, "equiv"), base_ev)]
    product_amounts = []
    parts = []
    if detailed:
        sub_amounts = [field("mass", qty(70.0, "mg"), P[3]), field("amount", qty(0.20, "mmol"), P[3])]
        reagent_amounts.extend([
            field("concentration", qty(1.73, "M"), P[3]),
            field("volume", qty(0.48, "mL"), P[3]),
            field("amount", qty(0.83, "mmol"), P[3]),
        ])
        product_amounts = [field("mass", qty(75.5, "mg"), P[3])]
    parts.extend([
        participant("substrate", "reactant", f"{substrate} (R1={r1}, Rf={rf})", base_ev, amounts=sub_amounts),
        participant("grignard", "reagent", reagent + (" in THF" if detailed else ""), ev, amounts=reagent_amounts),
        participant("reaction_ether", "solvent", "anhydrous Et2O" if detailed else "Et2O", ev, smiles="CCOCC",
                    amounts=[field("volume", qty(0.5, "mL"), P[3])] if detailed else []),
        participant("product", "product", f"{product} (R2={r2})", base_ev, amounts=product_amounts),
    ])
    reaction_ids = ["substrate", "grignard", "reaction_ether", "product"]
    steps = [{
        "step_id": "reaction",
        "participant_ids": reaction_ids,
        "conditions": [
            field("solvent", "Et2O", base_ev),
            field("temperature", "r.t.", base_ev),
            field("time", qty(2, "h") if detailed else {"minimum": 2, "maximum": 2.5, "unit": "h", "raw_text": "2–2.5 h"}, P[3] if detailed else base_ev),
        ] + ([field("atmosphere", "nitrogen", P[3]), field("operation", "PhMgCl solution added dropwise by syringe to a dry Schlenk tube; reaction monitored by TLC", P[3])] if detailed else []),
    }]
    outcomes = [
        field("isolated_yield", qty(isolated_yield, "%"), base_ev, ["product"]),
        field("yield_measurement_basis", "isolated yield", base_ev, ["product"]),
    ]
    notes = ["Table 2 applies the standard-condition loading stated in the adjacent prose; entries 16 and 17 explicitly override this to 3 equivalents of PhMgBr."]
    if recovery_bound is not None:
        outcomes.append(field(
            "recovered_starting_material_yield",
            qty(recovery_bound, "%", qualifier="le", raw_text=f"≤{recovery_bound}%"),
            base_ev,
            ["substrate"],
        ))
    if detailed:
        parts.extend([
            participant("sat_nh4cl", "reagent", "saturated aqueous NH4Cl", P[3], amounts=[field("volume", qty(5, "mL"), P[3])]),
            participant("extraction_ether", "solvent", "diethyl ether (extraction)", P[3], smiles="CCOCC", amounts=[field("volume", qty(25, "mL"), P[3])]),
            participant("brine", "reagent", "brine", P[3], amounts=[field("volume", qty(10, "mL"), P[3])]),
            participant("sodium_sulfate", "reagent", "anhydrous Na2SO4", P[3]),
            participant("petroleum_ether", "solvent", "petroleum ether", P[3]),
            participant("ethyl_acetate", "solvent", "ethyl acetate", P[3], smiles="CCOC(C)=O"),
        ])
        steps.extend([
            {"step_id": "workup", "participant_ids": ["sat_nh4cl", "extraction_ether", "brine", "sodium_sulfate"],
             "conditions": [field("workup", "Quenched with saturated aqueous NH4Cl; extracted with diethyl ether (25 mL × 3); washed with brine (10 mL × 2); dried over anhydrous Na2SO4; evaporated.", P[3])]},
            {"step_id": "purification", "participant_ids": ["product", "petroleum_ether", "ethyl_acetate"],
             "conditions": [field("purification", "Silica-gel column chromatography, petroleum ether/ethyl acetate = 20/1", P[3])]},
        ])
        outcomes.extend([
            field("recovered_starting_material_yield", qty(1.4, "%"), P[3], ["substrate"]),
            field("recovery_measurement_basis", "1H and 19F NMR analysis of the crude reaction mixture before separation", P[3], ["substrate"]),
            field("alkene_geometry_selectivity", "exclusively Z", base_ev, ["product"]),
            field("selectivity_measurement_basis", "crude 1H NMR; Z configuration assigned by 19F{1H}-HOESY", base_ev, ["product"]),
        ])
        notes.append("The detailed typical procedure on page 3 is merged with Table 2 entry 1, not duplicated as a separate batch.")
    unresolved = ["Complex substrate/product connectivity and stereochemistry remain unverified; SI was referenced but not provided."]
    if not detailed:
        unresolved.append("The scope row does not report batch scale, reagent concentration, atmosphere, workup, or purification.")
    records.append(record(
        f"table2_entry{entry}_{product.lower().replace('-', '')}", "substrate_scope_entry", ev, parts,
        steps=steps, outcomes=outcomes, notes=notes, unresolved=unresolved,
    ))


# Scheme 2 is a separate secondary-alcohol experiment with two isolated isomers.
ev = P[2] + P[3]
scheme2_parts = [
    participant("E1h", "reactant", "E-1h: 5-(n-butyl)-7,7,8,8,9,9,10,10,10-nonafluoro-5-decen-3-yn-2-ol", ev),
    participant("PhMgCl", "reagent", "PhMgCl in THF", P[3], amounts=[field("equivalents", qty(4.0, "equiv"), P[3]), field("concentration", qty(1.8, "M"), P[3])]),
    participant("Et2O", "solvent", "Et2O", P[3], smiles="CCOCC"),
    participant("Z2r_major", "product", "Z-2r major isomer", P[3]),
    participant("Z2r_minor", "product", "Z-2r minor isomer", P[3]),
]
records.append(record(
    "scheme2_secondary_alcohol_E1h", "reported_experiment", ev, scheme2_parts,
    steps=[{"step_id": "reaction", "participant_ids": [p["entity_id"] for p in scheme2_parts], "conditions": [
        field("solvent", "Et2O", P[3]), field("temperature", "r.t.", P[3]), field("time", qty(2, "h"), P[3]),
        field("purification", "flash chromatography on silica gel", P[3]),
    ]}],
    outcomes=[
        field("dr_ratio", "83/17", P[3], ["Z2r_major", "Z2r_minor"]),
        field("isolated_yield_major_isomer", qty(75, "%"), P[3], ["Z2r_major"]),
        field("isolated_yield_minor_isomer", qty(14, "%"), P[3], ["Z2r_minor"]),
        field("yield_measurement_basis", "isolated yields after flash chromatography", P[3], ["Z2r_major", "Z2r_minor"]),
    ],
    notes=["The two isolated isomers are retained as separate product entities because the source gives separate yields."],
    unresolved=["Reaction scale, exact ether volume, atmosphere, workup, and minor-isomer stereochemical assignment are not reported; SI was not provided."],
))


# Scheme 3 is explicitly labeled a possible mechanism and is not a reported batch.
ev = P[3]
mechanism_parts = [
    participant("M1", "reactant", "magnesium intermediate M1", ev),
    participant("M2", "product", "favored conformer/intermediate M2", ev),
    participant("M3", "product", "unfavored conformer/intermediate M3", ev),
    participant("Z2", "product", "generic Z-2 product", ev),
    participant("E2", "product", "generic E-2 product", ev),
    participant("MgXF", "product", "MgXF", ev),
]
records.append(record(
    "scheme3_possible_mechanism", "mechanism", ev, mechanism_parts,
    steps=[
        {"step_id": "conformational_paths", "participant_ids": ["M1", "M2", "M3"], "conditions": [field("operation", "M1 is proposed to access favored M2 or unfavored M3", ev)]},
        {"step_id": "anti_defluorometallation", "participant_ids": ["M2", "M3", "Z2", "E2", "MgXF"], "conditions": [field("operation", "Proposed anti-defluorometallation gives Z-2 preferentially and E-2 from the unfavored path", ev)]},
    ],
    notes=["The source calls Scheme 3 a possible mechanism; stereoelectronic and steric effects are proposed as the origin of Z selectivity."],
    unresolved=["Mechanistic intermediates are proposed rather than isolated; generic substituents and structures remain unverified."],
))


OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")

# Mark the four prepared page tasks as attempted after original-image inspection.
tasks_path = ROOT / "tasks.json"
tasks = json.loads(tasks_path.read_text())
for task in tasks:
    if task["document_id"] == DOC and task["evidence_id"] in {f"{DOC}:page{n}:text" for n in range(1, 5)}:
        task["state"] = "attempted"
        task["reason"] = "Original page image and extracted text inspected; records and coverage ledger generated, with unresolved chemistry retained."
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

table1_ids = [f"{DOC}:table1_entry{n}" for n in range(1, 9)]
table2_ids = [f"{DOC}:table2_entry{n}_{product.lower().replace('-', '')}" for n, *_rest, product, _yield, _recovery in scope]
coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1,
            "state": "attempted",
            "regions": [
                {"region": "title, abstract, and introduction", "finding": "Context and broad scope claims only; no individual batch or row-specific yield was created from the abstract.", "evidence_ids": P[1]},
                {"region": "lower-page Scheme 1", "finding": "Separated the cited generic propargylic-alcohol route from the present paper's generic alkenynol/trienol route; both are non-batch records.", "evidence_ids": P[1]},
            ],
            "record_ids": [f"{DOC}:scheme1_prior_propargylic_route", f"{DOC}:scheme1_current_generic_route"],
            "unresolved": ["Scheme 1 uses generic R groups and does not supply batch quantities or yields."],
        },
        {
            "page": 2,
            "state": "attempted",
            "regions": [
                {"region": "upper-page Table 1, reaction drawing, and footnotes a-d", "finding": "Eight optimization rows extracted independently with CuCl loading, temperature program, solvent, conversion, NMR yield, and PhMgCl footnote overrides.", "evidence_ids": P[2]},
                {"region": "lower-right Table 2, reaction drawing, and footnotes a-g", "finding": "Seventeen substrate-scope rows extracted independently; isolated yields, bromide/chloride reagent overrides, three-equivalent overrides, and ≤4%/≤5% starting-material recoveries were retained.", "evidence_ids": P[2]},
                {"region": "body prose surrounding Tables 1 and 2", "finding": "Standard 4-equivalent PhMgCl conditions and exclusive Z assignment were linked to the relevant records; the E-1h paragraph continues to Scheme 2 on page 3.", "evidence_ids": P[2]},
            ],
            "record_ids": [f"{DOC}:scheme1_current_generic_route"] + table1_ids + table2_ids + [f"{DOC}:scheme2_secondary_alcohol_E1h"],
            "unresolved": ["Most table rows omit batch scale, atmosphere, workup, and purification; complex structures remain unverified."],
        },
        {
            "page": 3,
            "state": "attempted",
            "regions": [
                {"region": "top-left Scheme 2 and continuation prose", "finding": "One secondary-alcohol experiment extracted with 4 equiv PhMgCl, 1.8 M THF solution, Et2O, room temperature, 2 h, 83/17 dr, and separate 75%/14% isolated isomer yields.", "evidence_ids": P[3]},
                {"region": "left-column typical procedure and Z-2a characterization", "finding": "Detailed preparation, workup, chromatography, 75.5 mg/95% product, and 1.4% recovered E-1a were merged into Table 2 entry 1 rather than duplicated.", "evidence_ids": P[3]},
                {"region": "lower-left Scheme 3 and selectivity discussion", "finding": "Classified as a possible mechanism with favored M2/unfavored M3 paths, not as an experimental batch.", "evidence_ids": P[3]},
                {"region": "right-column acknowledgments, SI notice, and references", "finding": "No new experiment; online supplementary data are mentioned but no SI file was supplied or associated.", "evidence_ids": P[3]},
            ],
            "record_ids": [f"{DOC}:table2_entry1_z2a", f"{DOC}:scheme2_secondary_alcohol_E1h", f"{DOC}:scheme3_possible_mechanism"],
            "unresolved": ["SI association remains unestablished; Scheme 2 omits scale and full operational details."],
        },
        {
            "page": 4,
            "state": "attempted",
            "regions": [
                {"region": "reference-list continuation across the top of the page", "finding": "References only; no reaction scheme, table, arrow, footnote-defined batch, or new experimental procedure is present.", "evidence_ids": P[4]},
                {"region": "blank remainder of page", "finding": "No chemical content or experiment to extract.", "evidence_ids": P[4]},
            ],
            "record_ids": [],
            "unresolved": [],
        },
    ],
}
(ROOT / "coverage" / "pages_0001_0004.json").write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"records": len(records), "output": str(OUT), "coverage_pages": len(coverage["pages"])}, ensure_ascii=False))
