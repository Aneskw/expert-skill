#!/usr/bin/env python3
"""Build evidence-linked machine records for PDF pages 1-3 of b513371h."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "runs/current/raw_model/pages_0001_0003_records.json"
COVERAGE = ROOT / "runs/current/coverage/pages_0001_0003.json"
TASKS = ROOT / "runs/current/tasks.json"
DOC = "doc_a8f3bfb4733e2453"

P1 = [f"{DOC}:page1:text", f"{DOC}:page1:image"]
P2 = [f"{DOC}:page2:text", f"{DOC}:page2:image"]
P3 = [f"{DOC}:page3:text", f"{DOC}:page3:image"]


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


def participant(entity_id, role, label, name, evidence, smiles=None, amounts=None):
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


def amount(value, evidence, name="amount"):
    return field(name, value, evidence)


def base_record(suffix, source_id, kind, evidence, unresolved):
    return {
        "record_id": f"{DOC}:{suffix}",
        "document_id": DOC,
        "source_reaction_id": source_id,
        "record_kind": kind,
        "status": "needs_review",
        "completeness": "partial",
        "evidence_ids": list(evidence),
        "participants": [],
        "steps": [],
        "outcomes": [],
        "notes": [],
        "review": {
            "method": "model",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": list(unresolved),
        },
    }


def common_missing():
    return [
        "The article advertises ESI, but no supporting-information file was explicitly associated with this dataset.",
        "Workup and purification are not reported on the cited main-text page.",
        "Candidate SMILES for complex labeled substrates/products require independent comparison with the chemical drawings.",
    ]


def catalyst(evidence):
    return participant(
        "pd_oac2", "catalyst", "Pd(OAc)2", "palladium(II) acetate", evidence,
        "CC(=O)[O-].CC(=O)[O-].[Pd+2]", [amount({"number": 5, "unit": "mol%"}, evidence)],
    )


def dmso(evidence, volume):
    return participant(
        "dmso", "solvent", "DMSO", "dimethyl sulfoxide", evidence, "CS(C)=O",
        [amount({"number": volume, "unit": "mL"}, evidence, "volume")],
    )


def ligand_smiles(label):
    return {
        "PCy3": "P(C1CCCCC1)(C1CCCCC1)C1CCCCC1",
        "P(o-tolyl)3": "P(c1ccccc1C)(c1ccccc1C)c1ccccc1C",
        "TFP": "P(c1ccco1)(c1ccco1)c1ccco1",
    }.get(label)


records = []

# Scheme 1 is a proposed generic route/mechanistic sequence, not a reported experiment.
scheme1 = base_record(
    "scheme1_proposed_route", "Scheme 1", "mechanism", P1,
    [
        "The scheme uses generic R groups and PdX/PdX2 species; exact structures and identities are intentionally unresolved.",
        "No experimental conditions or outcome are assigned because the figure is explicitly a proposed synthetic route.",
    ],
)
scheme1["participants"] = [
    participant("scheme1_acid_4", "reactant", "4", "generic 2,3-allenoic acid 4", P1),
    participant("scheme1_carbonate_3", "reactant", "3", "generic propargylic carbonate 3", P1),
    participant("scheme1_intermediate_2", "unspecified_agent", "2", "proposed palladium intermediate 2", P1),
    participant("scheme1_product_1", "product", "1", "generic beta-allenyl butenolide 1", P1),
    participant("scheme1_pdx2", "catalyst", "PdX2", "generic palladium(II) species", P1),
    participant("scheme1_pdx", "unspecified_agent", "PdX", "generic palladium species", P1),
]
scheme1["steps"] = [
    {"step_id": "proposed_cyclic_oxypalladation", "participant_ids": ["scheme1_acid_4", "scheme1_pdx2", "scheme1_intermediate_2"], "conditions": []},
    {"step_id": "proposed_coupling_and_elimination", "participant_ids": ["scheme1_intermediate_2", "scheme1_carbonate_3", "scheme1_product_1", "scheme1_pdx"], "conditions": []},
]
scheme1["notes"] = [fact("Proposed synthetic route; not counted as a present-paper experimental run.", P1)]
records.append(scheme1)


table1 = [
    (1, "(R)-BINAP", "(R)-BINAP", 5, 19.5, "trace"),
    (2, "Dppb", "1,4-bis(diphenylphosphino)butane", 5, 17.5, 10),
    (3, "Dppp", "1,3-bis(diphenylphosphino)propane", 5, 21, 14),
    (4, "Dppe", "1,2-bis(diphenylphosphino)ethane", 5, 17, 51),
    (5, "PCy3", "tricyclohexylphosphine", 10, 19.5, 14),
    (6, "P(o-tolyl)3", "tri(o-tolyl)phosphine", 10, 21, 17),
    (7, "TFP", "tri(2-furyl)phosphine", 10, 14, 59),
    (8, "TFP", "tri(2-furyl)phosphine", 10, 23, 50),
]

for entry, lig_label, lig_name, lig_loading, hours, yield_value in table1:
    rec = base_record(
        f"table1_entry_{entry}", f"Table 1 entry {entry}", "optimization_entry", P1,
        common_missing(),
    )
    ligand_id = f"ligand_{entry}"
    product_id = f"product_1aa_e{entry}"
    k_value = {"number": 5, "unit": "mol%"} if entry == 8 else {"number": 1.0, "unit": "equiv"}
    k_name = "amount" if entry == 8 else "equivalents"
    rec["participants"] = [
        participant("acid_4a", "reactant", "4a", "2,3-allenoic acid 4a (R1=Me, R2=Ph, R3=H)", P1, None,
                    [amount({"number": 0.25, "unit": "mmol"}, P1)]),
        participant("carbonate_3a", "reactant", "3a", "propargylic carbonate 3a (R4=Me, R5=Me, R6=H)", P1,
                    "C#CC(C)(C)OC(=O)OC", [amount({"number": 0.50, "unit": "mmol"}, P1)]),
        catalyst(P1),
        participant(ligand_id, "reagent", lig_label, lig_name, P1, ligand_smiles(lig_label),
                    [amount({"number": lig_loading, "unit": "mol%"}, P1)]),
        participant("k2co3", "reagent", "K2CO3", "potassium carbonate", P1,
                    "[K+].[K+].[O-]C([O-])=O", [amount(k_value, P1, k_name)]),
        dmso(P1, 3),
        participant(product_id, "product", "1aa", "beta-allenyl butenolide 1aa", P1),
    ]
    ids = [p["entity_id"] for p in rec["participants"]]
    rec["steps"] = [{
        "step_id": "cross_coupling_cyclization",
        "participant_ids": ids,
        "conditions": [
            field("atmosphere", "argon", P1),
            field("operation", "stirred", P1),
            field("temperature", {"number": 25, "unit": "°C"}, P1),
            field("time", {"number": hours, "unit": "h"}, P1),
        ],
    }]
    rec["outcomes"] = [
        field("isolated_yield", yield_value if yield_value == "trace" else {"number": yield_value, "unit": "%"}, P1, [product_id]),
        field("yield_measurement_basis", "isolated yield", P1, [product_id]),
    ]
    if entry == 8:
        rec["notes"] = [fact("Entry 8 uses the footnote-d potassium carbonate loading rather than the scheme's default base loading.", P1)]
    records.append(rec)


table2 = [
    (1, "4a", "Me", "Ph", "H", "3b", "-(CH2)5-", "H", 5, 35, 68, "1ab"),
    (2, "4a", "Me", "Ph", "H", "3c", "Et/Et", "H", 10, 35, 60, "1ac"),
    (3, "4b", "Pr", "Ph", "H", "3a", "Me/Me", "H", 11, 35, 54, "1ba"),
    (4, "4b", "Pr", "Ph", "H", "3c", "Et/Et", "H", 9, 35, 64, "1bc"),
    (5, "4c", "Me", "1'-Nap", "H", "3a", "Me/Me", "H", 10, 35, 63, "1ca"),
    (6, "4c", "Me", "1'-Nap", "H", "3b", "-(CH2)5-", "H", 10, 40, 52, "1cb"),
    (7, "4c", "Me", "1'-Nap", "H", "3c", "Et/Et", "H", 10, 40, 68, "1cc"),
    (8, "4d", "Pr", "1'-Nap", "H", "3c", "Et/Et", "H", 10, 35, 71, "1dc"),
    (9, "4e", "Me", "Me", "H", "3a", "Me/Me", "H", 6, 35, 54, "1ea"),
    (10, "4f", "H", "Ph", "Me", "3c", "Et/Et", "H", 12, 35, 82, "1fc"),
    (11, "4f", "H", "Ph", "Me", "3d", "Me/Me", "Bu", 16, 35, 93, "1fd"),
    (12, "4g", "H", "Ph", "Et", "3e", "Me/Me", "Ph", 17, 35, 91, "1ge"),
]

for entry, acid_label, r1, r2, r3, carbonate_label, r45, r6, hours, temp, yld, product_label in table2:
    unresolved = common_missing() + [
        "Table 2 does not state whether K2CO3 was used; it is not imported from Table 1 by inference.",
    ]
    rec = base_record(
        f"table2_entry_{entry}_{product_label}", f"Table 2 entry {entry}", "substrate_scope_entry", P2,
        unresolved,
    )
    acid_id = f"acid_{acid_label}_e{entry}"
    carbonate_id = f"carbonate_{carbonate_label}_e{entry}"
    product_id = f"product_{product_label}"
    rec["participants"] = [
        participant(acid_id, "reactant", acid_label,
                    f"2,3-allenoic acid {acid_label} (R1={r1}, R2={r2}, R3={r3})", P2, None,
                    [amount({"number": 0.25, "unit": "mmol"}, P2)]),
        participant(carbonate_id, "reactant", carbonate_label,
                    f"propargylic carbonate {carbonate_label} (R4/R5={r45}, R6={r6})", P2, None,
                    [amount({"number": 0.50, "unit": "mmol"}, P2)]),
        catalyst(P2),
        participant("tfp", "reagent", "TFP", "tri(2-furyl)phosphine", P2, ligand_smiles("TFP"),
                    [amount({"number": 10, "unit": "mol%"}, P2)]),
        dmso(P2, 1),
        participant(product_id, "product", product_label, f"beta-allenyl butenolide {product_label}", P2),
    ]
    rec["steps"] = [{
        "step_id": "cross_coupling_cyclization",
        "participant_ids": [p["entity_id"] for p in rec["participants"]],
        "conditions": [
            field("atmosphere", "argon", P2),
            field("operation", "stirred", P2),
            field("temperature", {"number": temp, "unit": "°C"}, P2),
            field("time", {"number": hours, "unit": "h"}, P2),
        ],
    }]
    rec["outcomes"] = [
        field("isolated_yield", {"number": yld, "unit": "%"}, P2, [product_id]),
        field("yield_measurement_basis", "isolated yield", P2, [product_id]),
    ]
    if entry in (6, 7):
        rec["notes"] = [fact("Table 2 footnote c overrides the shared 35 °C condition with 40 °C.", P2)]
    records.append(rec)


diels = [
    ("1fc", "R4=R5=Et, R6=H", "5a", "R=CO2Me", "6fca", 98),
    ("1fd", "R4=R5=Me, R6=n-Bu", "5a", "R=CO2Me", "6fda", 95),
    ("1fd", "R4=R5=Me, R6=n-Bu", "5b", "R=H", "6fdb", 62),
]

for substrate, substrate_desc, alkyne, alkyne_desc, product, yld in diels:
    product_id = f"product_{product}"
    rec = base_record(
        f"scheme2_{product}", f"Scheme 2 {product}", "reported_experiment", P2,
        [
            "Reaction time and reactant amounts are not printed in Scheme 2.",
            "The 7-14 mol% hydroquinone range is shared by the scheme; the exact loading for this arrow is not specified.",
            "Yield measurement basis is not stated for Scheme 2 and is retained as null/missing.",
            "The article advertises ESI, but no supporting-information file was explicitly associated with this dataset.",
            "Candidate SMILES for labeled substrate/product structures require independent comparison with the chemical drawings.",
        ],
    )
    rec["participants"] = [
        participant(f"substrate_{substrate}", "reactant", substrate,
                    f"beta-allenyl butenolide {substrate} ({substrate_desc})", P2, None,
                    [amount(None, P2)]),
        participant(f"alkyne_{alkyne}", "reactant", alkyne,
                    f"electron-deficient alkyne {alkyne} ({alkyne_desc})", P2, None,
                    [amount(None, P2)]),
        participant("hydroquinone", "reagent", "hydroquinone", "hydroquinone", P2, "Oc1ccc(O)cc1",
                    [amount({"minimum": 7, "maximum": 14, "unit": "mol%", "raw_text": "7-14 mol%"}, P2)]),
        participant("xylene", "solvent", "xylene", "xylene (isomer unspecified)", P2),
        participant(product_id, "product", product, f"polysubstituted benzo-gamma-lactone {product}", P2),
    ]
    rec["steps"] = [{
        "step_id": "diels_alder",
        "participant_ids": [p["entity_id"] for p in rec["participants"]],
        "conditions": [
            field("operation", "heated in a sealed vessel", P2),
            field("temperature", {"number": 170, "unit": "°C"}, P2),
            field("time", None, P2),
        ],
    }]
    rec["outcomes"] = [
        field("yield", {"number": yld, "unit": "%"}, P2, [product_id]),
        field("yield_measurement_basis", None, P2, [product_id]),
        field("regioselectivity", "highly regioselective", P2, [product_id]),
    ]
    records.append(rec)


page1_ids = [r["record_id"] for r in records if P1[1] in r["evidence_ids"]]
page2_ids = [r["record_id"] for r in records if P2[1] in r["evidence_ids"]]
coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1,
            "state": "attempted",
            "regions": [
                {
                    "region": "lower-left Scheme 1 proposed synthetic route",
                    "finding": "Generic proposed Pd sequence (4 to intermediate 2, then 2 plus 3 to 1); classified as mechanism, not a reported experiment.",
                    "evidence_ids": P1,
                },
                {
                    "region": "lower-right Table 1, entries 1-8 and footnotes a-d",
                    "finding": "Eight independent ligand/K2CO3 optimization experiments, including a trace result and entry-specific ligand/base loadings.",
                    "evidence_ids": P1,
                },
                {
                    "region": "title, abstract, two-column introduction and ESI footnote",
                    "finding": "Method summary and contextual/prior-work discussion; ESI is advertised but no SI file is explicitly associated here.",
                    "evidence_ids": P1,
                },
            ],
            "record_ids": page1_ids,
            "unresolved": [
                "Complex drawn structures 4a and 1aa require independent structure verification.",
                "Workup/purification and ESI-only experimental detail are unavailable in the supplied source.",
            ],
        },
        {
            "page": 2,
            "state": "attempted",
            "regions": [
                {
                    "region": "upper Fig. 1 ORTEP drawings",
                    "finding": "Crystallographic structure evidence for 1aa and 6fda; no independent synthetic experiment is created from the ORTEP panel.",
                    "evidence_ids": P2,
                },
                {
                    "region": "lower-left Table 2, entries 1-12 and footnotes a-c",
                    "finding": "Twelve independent substrate-scope experiments with explicit substituent assignments, times, temperatures and isolated yields.",
                    "evidence_ids": P2,
                },
                {
                    "region": "upper-right Scheme 2 reaction arrow and three product lines",
                    "finding": "Three present-paper Diels-Alder experiments (6fca, 6fda, 6fdb) at 170 °C in sealed xylene with 7-14 mol% hydroquinone.",
                    "evidence_ids": P2,
                },
                {
                    "region": "right-column conclusion and crystallographic footnotes",
                    "finding": "Conclusion and characterization metadata; no additional reaction arrow or independent experimental run.",
                    "evidence_ids": P2,
                },
            ],
            "record_ids": page2_ids,
            "unresolved": [
                "Table 2 does not explicitly state whether K2CO3 was used.",
                "Scheme 2 omits reaction time, reactant amounts and yield measurement basis.",
                "Complex labeled structures remain unverified machine interpretations.",
            ],
        },
        {
            "page": 3,
            "state": "attempted",
            "regions": [
                {
                    "region": "two-column references 3-12",
                    "finding": "Bibliographic citations and brief prior-literature context only; no present-paper reaction arrow, table row or experimental procedure is reported.",
                    "evidence_ids": P3,
                }
            ],
            "record_ids": [],
            "unresolved": [],
        },
    ],
}


OUT.parent.mkdir(parents=True, exist_ok=True)
COVERAGE.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
COVERAGE.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

tasks = json.loads(TASKS.read_text())
for task in tasks:
    page = int(task["evidence_id"].split(":page", 1)[1].split(":", 1)[0])
    if 1 <= page <= 3:
        task["state"] = "attempted"
        task["visual_evidence_id"] = f"{DOC}:page{page}:image"
        task["reason"] = "Original page image and page text inspected; findings and unresolved items are recorded in coverage/pages_0001_0003.json."
TASKS.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"records": len(records), "raw": str(OUT), "coverage": str(COVERAGE)}, ensure_ascii=False))
