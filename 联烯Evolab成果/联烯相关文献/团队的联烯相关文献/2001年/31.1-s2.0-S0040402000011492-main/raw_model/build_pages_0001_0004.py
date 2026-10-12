#!/usr/bin/env python3
"""Build evidence-linked machine records for source PDF pages 1-4."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / "runs" / "current"
DOC = "doc_8485474665684a0c"
EV = {p: [f"{DOC}:page{p}:text", f"{DOC}:page{p}:image"] for p in range(1, 5)}


def fact(value, evidence=()):
    return {
        "value": value,
        "evidence_ids": list(dict.fromkeys(evidence)) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def field(name, value, evidence=()):
    return {"name": name, "fact": fact(value, evidence)}


def participant(entity_id, role, label, name, evidence, amounts=()):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence) if name else fact(None),
        "smiles": fact(None),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": [field(n, v, evidence) for n, v in amounts],
    }


def record(suffix, source_id, kind, evidence, participants, steps, outcomes, notes, unresolved):
    return {
        "record_id": f"{DOC}:{suffix}",
        "document_id": DOC,
        "source_reaction_id": source_id,
        "record_kind": kind,
        "status": "needs_review",
        "completeness": "partial",
        "evidence_ids": list(dict.fromkeys(evidence)),
        "participants": participants,
        "steps": steps,
        "outcomes": outcomes,
        "notes": [fact(x, evidence) for x in notes],
        "review": {
            "method": "model",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved,
        },
    }


records = []

# Starting materials are explicitly said to have been made according to cited methods.
e2 = EV[2]
records.append(record(
    "starting_material_1l_ref11",
    "Section 1.1 preparation of 1l according to reference 11",
    "literature_example",
    e2,
    [
        participant("allene_1l_precursor", "reactant", "corresponding 1,2-allene", None, e2),
        participant("n_buli", "reagent", "n-BuLi", "n-Butyllithium", e2),
        participant("carbon_dioxide", "reagent", "CO2", "Carbon dioxide", e2),
        participant("product_1l", "product", "1l", "2,3-Undecadienoic acid", e2),
    ],
    [
        {"step_id": "form_allenic_lithium", "participant_ids": ["allene_1l_precursor", "n_buli"],
         "conditions": [field("operating_details", None)]},
        {"step_id": "carboxylation", "participant_ids": ["allene_1l_precursor", "carbon_dioxide", "product_1l"],
         "conditions": [field("procedure_source", "published procedure, reference 11", e2)]},
    ],
    [field("reported_yield", None)],
    ["The local article gives only a route summary and cites an external procedure."],
    ["Precursor identity beyond 'corresponding 1,2-allene', reagent amounts, temperature, time, atmosphere, workup, purification, and yield are not reported locally."],
))

records.append(record(
    "starting_material_1a_1k_1m_1n_ref12",
    "Section 1.1 preparation of 1a-1k and 1m,n according to reference 12",
    "literature_example",
    e2,
    [
        participant("acid_chlorides", "reactant", "acid chlorides", None, e2),
        participant("ylide", "reagent", "ethyl 2-(triphenylphosphoranylidene) propionate", None, e2),
        participant("allenoic_esters", "product", "2,3-allenoic esters", None, e2),
        participant("naoh", "reagent", "NaOH", "Sodium hydroxide", e2, [("amount", {"number": 1.5, "unit": "equiv"})]),
        participant("allenoic_acids", "product", "1a-1k and 1m,n", "2,3-Allenoic acids", e2),
    ],
    [
        {"step_id": "allenoate_formation", "participant_ids": ["acid_chlorides", "ylide", "allenoic_esters"],
         "conditions": [field("operating_details", None)]},
        {"step_id": "ester_hydrolysis", "participant_ids": ["allenoic_esters", "naoh", "allenoic_acids"],
         "conditions": [field("procedure_source", "known method, reference 12", e2)]},
    ],
    [field("reported_yield", None)],
    ["The article groups thirteen starting-acid preparations under one cited method and does not provide compound-specific yields."],
    ["Acid-chloride identities, individual scales, operating conditions, workups, purifications, and yields are not reported locally."],
))


# Table 1 optimization. Entry 11 is built below with Table 2 entry 1 and section 1.2.1.
table1 = [
    (1, "MeCOMe/H2O (3:2)", "200 mol%", "65-70 °C", {"number": 4.5, "unit": "h"}, 53),
    (2, "MeCOMe/H2O (3:2)", {"number": 12, "unit": "mol%"}, "65-70 °C", {"number": 1, "unit": "h"}, 81),
    (3, "MeCOMe/H2O (3:1)", {"number": 22, "unit": "mol%"}, "65-70 °C", {"number": 1, "unit": "h"}, 65),
    (4, "MeCOMe", {"number": 4, "unit": "mol%"}, {"number": 40, "unit": "°C"}, {"number": 27, "unit": "h"}, 83),
    (5, "MeCN/H2O (3:2)", {"number": 16, "unit": "mol%"}, "70-80 °C", {"number": 17.5, "unit": "h"}, 41),
    (6, "DMF/H2O (3:2)", {"number": 11, "unit": "mol%"}, "70-80 °C", {"number": 0.5, "unit": "h"}, 64),
    (7, "DMF/H2O (2:1)", {"number": 6, "unit": "mol%"}, "65-70 °C", {"number": 1, "unit": "h"}, 74),
    (8, "DMF/H2O (5:1)", {"number": 7, "unit": "mol%"}, "65-70 °C", {"number": 1, "unit": "h"}, 75),
    (9, "EtOH", {"number": 6, "unit": "mol%"}, {"number": 70, "unit": "°C"}, {"number": 3.5, "unit": "h"}, 90),
    (10, "CH2Cl2", {"number": 8, "unit": "mol%"}, {"number": 55, "unit": "°C"}, {"number": 5, "unit": "h"}, 0),
]

for entry, solvent, loading, temperature, duration, yield_value in table1:
    evidence = EV[2] + (EV[1] if entry == 10 else [])
    notes = ["Table 1 optimization of 2-methyl-4-phenyl-2,3-butadienoic acid (1a) to 2a."]
    if entry == 10:
        notes.append("The prose explicitly states that the reaction did not occur in CH2Cl2.")
    records.append(record(
        f"table1_entry_{entry:02d}",
        f"Table 1 entry {entry}",
        "optimization_entry",
        evidence,
        [
            participant("substrate_1a", "reactant", "1a", "2-Methyl-4-phenyl-2,3-butadienoic acid", evidence),
            participant("cucl", "catalyst", "CuCl", "Copper(I) chloride", evidence, [("loading", loading)]),
            participant("solvent", "solvent", solvent, None, evidence),
            participant("product_2a", "product", "2a", "3-Methyl-5-phenyl-2(5H)-furanone", evidence),
        ],
        [{"step_id": "cycloisomerization", "participant_ids": ["substrate_1a", "cucl", "solvent", "product_2a"],
          "conditions": [
              field("temperature", temperature, evidence), field("time", duration, evidence),
              field("reaction_scale", None), field("atmosphere", None), field("workup", None),
          ]}],
        [field("yield", {"number": yield_value, "unit": "%"}, evidence), field("yield_measurement_basis", None)],
        notes,
        ["Reaction scale, atmosphere, workup, purification, isolated mass, and yield measurement basis are not stated for this optimization row."],
    ))


scope = [
    # entry, substrate, R1, R2, R3, product, product name, substrate mg, mmol, product mg, yield, state, mp, eluent
    (1, "1a", "Ph", "H", "CH3", "2a", "3-Methyl-5-phenyl-2(5H)-furanone", 84, 0.48, 80, 95, "colorless oil", None, "petroleum ether/ethyl acetate 10:1"),
    (2, "1b", "Ph", "H", "n-C3H7", "2b", "5-Phenyl-3-propyl-2(5H)-furanone", 102, 0.50, 99, 97, "colorless oil", None, "petroleum ether/ethyl acetate 10:1"),
    (3, "1c", "Ph", "H", "PhCH2", "2c", "3-Benzyl-5-phenyl-2(5H)-furanone", 125, 0.50, 113, 90, "colorless platelet crystals", "65-66 °C", "petroleum ether/ethyl acetate 10:1"),
    (4, "1d", "Ph", "H", "Allyl", "2d", "3-Allyl-5-phenyl-2(5H)-furanone", 106, 0.53, 102, 96, "colorless oil", None, "petroleum ether/ethyl acetate 10:1"),
    (5, "1e", "1-naphthyl", "H", "CH3", "2e", "3-Methyl-5-naphthyl-2(5H)-furanone", 112, 0.50, 103, 92, "colorless needle crystals", "91-92 °C", "petroleum ether/ethyl acetate 10:1"),
    (6, "1f", "1-naphthyl", "H", "n-C3H7", "2f", "5-Naphthyl-3-propyl-2(5H)-furanone", 127, 0.50, 122, 96, "colorless crystal", "84-85 °C", "petroleum ether/ethyl acetate 10:1"),
    (7, "1g", "n-C3H7", "H", "CH3", "2g", "3-Methyl-5-propyl-2(5H)-furanone", 84, 0.60, 73, 87, "colorless oil", None, "petroleum ether/ethyl acetate 10:1"),
    (8, "1h", "n-C3H7", "H", "PhCH2", "2h", "3-Benzyl-5-propyl-2(5H)-furanone", 110, 0.51, 93, 85, "colorless oil", None, "petroleum ether/ethyl acetate 10:1"),
    (9, "1i", "CH3", "H", "n-C3H7", "2i", "5-Methyl-3-propyl-2(5H)-furanone", 81, 0.58, 63, 77, "colorless oil", None, "petroleum ether/ethyl acetate 10:1"),
    (10, "1j", "n-C6H13", "H", "CH3", "2j", "5-Hexyl-3-methyl-2(5H)-furanone", 100, 0.55, 85, 85, "colorless oil", None, "petroleum ether/ethyl acetate 10:1"),
    (11, "1k", "Ph", "C2H5", "CH3", "2k", "5-Ethyl-3-methyl-5-phenyl-2(5H)-furanone", 106, 0.52, 99, 93, "colorless oil", None, "petroleum ether/ethyl acetate 20:1"),
    (12, "1l", "n-C7H15", "H", "H", "2l", "5-Heptyl-2(5H)-furanone", 98, 0.54, 79, 81, "colorless oil", None, "petroleum ether/ethyl acetate 20:1"),
    (13, "1m", "n-C3H7", "H", "Allyl", "2m", "3-Propenyl-5-propyl-2(5H)-furanone", 86, 0.52, 78, 91, "colorless oil", None, "petroleum ether/ethyl acetate 20:1"),
    (14, "1n", "1-naphthyl", "H", "Allyl", "2n", "5-Naphthyl-3-propenyl-2(5H)-furanone", 125, 0.50, 115, 92, "colorless platelet crystals", "71-72 °C", "petroleum ether/ethyl acetate 20:1"),
]

scope_ids = []
for entry, substrate, r1, r2, r3, product, product_name, smg, smmol, pmg, yld, state, mp, eluent in scope:
    pages = [2] if entry <= 4 else [2, 3]
    evidence = [x for p in pages for x in EV[p]]
    suffix = "table1_entry_11_table2_entry_01_2a" if entry == 1 else f"table2_entry_{entry:02d}_{product}"
    scope_ids.append(f"{DOC}:{suffix}")
    unresolved = [
        "Substrate and product structures are conveyed by the table drawing/R-group labels and have not been encoded or verified as SMILES.",
        "Reaction concentration is not reported.",
    ]
    if entry in (13, 14):
        unresolved.append("Table 2 calls R3 'Allyl', whereas the product heading uses 'propenyl'; the source wording is preserved without structural certification.")
    rec_kind = "optimization_entry" if entry == 1 else "substrate_scope_entry"
    source_id = ("Table 1 entry 11 / Table 2 entry 1 / section 1.2.1" if entry == 1
                 else f"Table 2 entry {entry} / section 1.2.{entry}")
    parts = [
        participant("substrate", "reactant", substrate,
                    f"2,3-Alkadienoic acid {substrate} (R1={r1}, R2={r2}, R3={r3})", evidence,
                    [("mass", {"number": smg, "unit": "mg"}), ("amount", {"number": smmol, "unit": "mmol"})]),
        participant("cucl", "catalyst", "CuCl", "Copper(I) chloride", evidence,
                    [("loading", {"number": 4, "unit": "mol%"}), ("general_procedure_amount", {"number": 0.02, "unit": "mmol"})]),
        participant("methanol", "solvent", "MeOH", "Methanol", evidence, [("volume", {"number": 5, "unit": "mL"})]),
        participant("product", "product", product, product_name, evidence, [("isolated_mass", {"number": pmg, "unit": "mg"})]),
    ]
    conditions = [
        field("atmosphere", "N2", evidence),
        field("temperature", "reflux", evidence),
        field("time", {"number": 2, "unit": "h"}, evidence),
        field("postreaction_evaporation", True, evidence),
        field("purification", f"flash chromatography on silica gel; eluent {eluent}", evidence),
        field("concentration", None),
    ]
    if "crystal" in state:
        conditions.append(field("solid_product_recrystallization", "ethyl acetate and petroleum ether", evidence))
    outcomes = [
        field("isolated_yield", {"number": yld, "unit": "%"}, evidence),
        field("yield_measurement_basis", "isolated yield", evidence),
        field("physical_description", state, evidence),
    ]
    if mp:
        outcomes.append(field("melting_point", mp, evidence))
    notes = [
        "The Table 2 row and its matching product paragraph are represented as one experiment.",
        "Spectroscopic and analytical characterization is printed for the isolated product but is not expanded into separate reaction records.",
    ]
    if entry == 1:
        notes.append("This record also merges Table 1 entry 11 because substrate, conditions, product, time, and 95% yield match.")
    records.append(record(
        suffix, source_id, rec_kind, evidence, parts,
        [{"step_id": "cucl_catalyzed_cycloisomerization", "participant_ids": ["substrate", "cucl", "methanol", "product"], "conditions": conditions}],
        outcomes, notes, unresolved,
    ))


# Current-paper control described in reference note 10.
e4 = EV[4]
records.append(record(
    "h2so4_control_1a",
    "Reference note 10 control experiment with 1a",
    "reported_experiment",
    e4 + EV[1],
    [
        participant("substrate_1a", "reactant", "1a", "2-Methyl-4-phenyl-2,3-butadienoic acid", e4 + EV[1]),
        participant("h2so4", "reagent", "H2SO4", "Sulfuric acid", e4),
        participant("product_2a", "product", "2a", "3-Methyl-5-phenyl-2(5H)-furanone", e4 + EV[1]),
    ],
    [{"step_id": "acid_catalyzed_control", "participant_ids": ["substrate_1a", "h2so4", "product_2a"],
      "conditions": [field("procedure", "reported H2SO4 procedure cited as references 10a-c", e4),
                     field("reaction_scale", None), field("temperature", None), field("time", None),
                     field("solvent", None), field("workup", None)]}],
    [field("yield", {"number": 25, "unit": "%"}, e4), field("yield_measurement_basis", None)],
    ["The source explicitly calls this a control experiment and describes the yield as rather poor."],
    ["Exact sulfuric-acid amount, reaction scale, solvent, temperature, time, atmosphere, workup, purification, product mass, and yield basis are not reported locally."],
))

records.append(record(
    "literature_h2so4_yield_range",
    "Reference note 10 prior H2SO4 method",
    "literature_example",
    e4 + EV[1],
    [
        participant("allenoic_acid", "reactant", "2,3-allenoic acid", None, e4 + EV[1]),
        participant("h2so4", "reagent", "H2SO4", "Sulfuric acid", e4),
        participant("butenolide", "product", "butenolide", None, e4 + EV[1]),
    ],
    [{"step_id": "prior_acid_catalyzed_cyclization", "participant_ids": ["allenoic_acid", "h2so4", "butenolide"],
      "conditions": [field("procedure_source", "references 10a-c", e4), field("operating_details", None)]}],
    [field("reported_yield_range", "60-65%", e4), field("yield_measurement_basis", None)],
    ["This is a summarized prior-literature comparison, not a current-paper experiment."],
    ["Individual substrates/products, scales, conditions, workups, and yield basis are not given in the current article."],
))


raw_path = RUN / "raw_model" / "records_pages_0001_0004.json"
raw_path.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")

all_t1 = [f"{DOC}:table1_entry_{i:02d}" for i in range(1, 11)] + [scope_ids[0]]
coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1,
            "state": "attempted",
            "regions": [
                {"region": "title, abstract, and two-column introduction", "finding": "Current CuCl-catalyzed cycloisomerization is described; cited Pd/Ag and CuX2 chemistry is prior work and was not recast as current experiments.", "evidence_ids": EV[1]},
                {"region": "Table 1 discussion", "finding": "Optimization interpretation identifies CH2Cl2 entry 10 as no reaction and MeOH/4 mol% CuCl/reflux/2 h entry 11 as best conditions.", "evidence_ids": EV[1]},
                {"region": "Table 2 discussion and conclusion", "finding": "Scope trends, allyl-bearing entries 4/13/14, and fully substituted entry 11 are discussed; no separate mechanism is depicted.", "evidence_ids": EV[1]},
            ],
            "record_ids": [f"{DOC}:table1_entry_10", scope_ids[0], scope_ids[3], scope_ids[10], scope_ids[12], scope_ids[13]],
            "unresolved": ["The prose summaries do not replace row-level source review in Table 1 or Table 2.", "Cited prior reactions lack sufficient local detail for additional individual records."],
        },
        {
            "page": 2,
            "state": "attempted",
            "regions": [
                {"region": "Table 1, upper page", "finding": "Eleven optimization rows for 1a to 2a were read individually, including the 0% CH2Cl2 result.", "evidence_ids": EV[2]},
                {"region": "Section 1.1 Starting materials", "finding": "Two cited preparation families were retained as partial literature examples: 1l via allenyllithium/CO2 and 1a-1k/1m,n via acid chlorides, ylide, and NaOH hydrolysis.", "evidence_ids": EV[2]},
                {"region": "Table 2, lower-left", "finding": "Fourteen substrate-scope rows and the isolated-yield footnote were read; Table 2 entry 1 was merged with Table 1 entry 11.", "evidence_ids": EV[2]},
                {"region": "Section 1.2 general procedure and 2a-2d paragraphs", "finding": "N2, charge, MeOH volume, reflux time, purification, individual masses/yields, physical descriptions, and melting point for 2c were linked to matching rows.", "evidence_ids": EV[2]},
            ],
            "record_ids": [f"{DOC}:starting_material_1l_ref11", f"{DOC}:starting_material_1a_1k_1m_1n_ref12"] + all_t1 + scope_ids,
            "unresolved": ["No structures were certified from the drawings.", "General-procedure nominal 0.5 mmol scale and individual reported substrate amounts are both retained where they differ."],
        },
        {
            "page": 3,
            "state": "attempted",
            "regions": [
                {"region": "Sections 1.2.5-1.2.12, left column and upper right", "finding": "Detailed isolated masses, yields, physical descriptions, and reported melting points for 2e-2l were linked to Table 2 entries 5-12.", "evidence_ids": EV[3]},
                {"region": "Sections 1.2.13-1.2.14, right column", "finding": "Detailed 2m and 2n preparations were linked to Table 2 entries 13-14; Table 'Allyl' versus heading 'propenyl' wording was retained as unresolved.", "evidence_ids": EV[3]},
                {"region": "Acknowledgments and references 1-2", "finding": "No additional current-paper reaction experiment was found in this region.", "evidence_ids": EV[3]},
            ],
            "record_ids": scope_ids[4:],
            "unresolved": ["Spectral assignments were not treated as separate reaction runs.", "Product structures remain unverified and SMILES are null."],
        },
        {
            "page": 4,
            "state": "attempted",
            "regions": [
                {"region": "references 3-9", "finding": "Bibliographic and comparative background only; no local current-paper experiment was created.", "evidence_ids": EV[4]},
                {"region": "reference note 10", "finding": "Prior H2SO4 yields of 60-65% were classified as literature, while the explicitly named 1a control experiment at 25% was retained as a separate current-paper record.", "evidence_ids": EV[4]},
                {"region": "references 11-18", "finding": "Starting-material and product literature citations only; no further local reaction run was found.", "evidence_ids": EV[4]},
            ],
            "record_ids": [f"{DOC}:h2so4_control_1a", f"{DOC}:literature_h2so4_yield_range"],
            "unresolved": ["The H2SO4 control's exact conditions, product mass, and yield basis are absent.", "No supporting-information file is supplied or associated."],
        },
    ],
}
(RUN / "coverage" / "pages_0001_0004.json").write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

tasks_path = RUN / "tasks.json"
tasks = json.loads(tasks_path.read_text())
for task in tasks:
    if task.get("document_id") == DOC and task.get("evidence_id") in {f"{DOC}:page{p}:text" for p in range(1, 5)}:
        task["state"] = "attempted"
        task["reason"] = "Original page image inspected; experiments and unresolved findings recorded in coverage/pages_0001_0004.json."
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"records": len(records), "coverage_pages": [p["page"] for p in coverage["pages"]]}, ensure_ascii=False))
