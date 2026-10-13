#!/usr/bin/env python3
"""Build source-linked machine records for ol9009046, PDF pages 1--4."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "runs/current"
DOC = "doc_1d05b5291e31f06e"


def ev(page):
    return [f"{DOC}:page{page}:image", f"{DOC}:page{page}:text"]


def fact(value, evidence):
    return {
        "value": value,
        "evidence_ids": evidence if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def field(name, value, evidence, targets=None):
    item = {"name": name, "fact": fact(value, evidence)}
    if targets:
        item["target_entity_ids"] = targets
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


def record(suffix, kind, evidence, participants, steps, outcomes, notes=None, unresolved=None):
    return {
        "record_id": f"{DOC}:{suffix}",
        "document_id": DOC,
        "source_reaction_id": suffix,
        "record_kind": kind,
        "status": "needs_review",
        "completeness": "partial",
        "evidence_ids": evidence,
        "participants": participants,
        "steps": steps,
        "outcomes": outcomes,
        "notes": [fact(x, evidence) for x in (notes or [])],
        "review": {
            "method": "model",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved or [],
        },
    }


SMILES = {
    "1a": "O=C(NCc1ccccc1)C=C=C(C)C",
    "2a": "CC(C)C1=CC(=O)N(Cc2ccccc2)C(=O)O1",
    "3a": "C/C=C/C(=O)NCc1ccccc1",
    "3b": "O=C(NCc1ccccc1)C#CCCCC",
    "CO2": "O=C=O",
    "K2CO3": "[K+].[K+].[O-]C(=O)[O-]",
    "Cs2CO3": "[Cs+].[Cs+].[O-]C(=O)[O-]",
    "Na2CO3": "[Na+].[Na+].[O-]C(=O)[O-]",
    "Li2CO3": "[Li+].[Li+].[O-]C(=O)[O-]",
    "KHCO3": "[K+].O=C([O-])O",
    "KOH": "[K+].[OH-]",
    "Et3N": "CCN(CC)CC",
    "(i-Pr)2NH": "CC(C)NC(C)C",
    "DMSO": "CS(C)=O",
    "DMF": "CN(C)C=O",
    "DMA": "CC(=O)N(C)C",
    "mesitylene": "Cc1cc(C)cc(C)c1",
}


def amount(name, number, unit, evidence):
    return field(name, {"number": number, "unit": unit}, evidence)


def substrate_1a(evidence, scale=None, mass=None):
    amounts = []
    if scale:
        if isinstance(scale, tuple):
            amounts.append(field("reaction_scale", {"minimum": scale[0], "maximum": scale[1], "unit": "mmol", "raw_text": "0.2–0.4 mmol"}, evidence))
        else:
            amounts.append(amount("reaction_scale", scale, "mmol", evidence))
    if mass:
        amounts.append(amount("mass", mass, "g", evidence))
    return participant("substrate_1a", "reactant", "1a", "N-benzyl-4-methyl-2,3-pentadienamide", evidence, SMILES["1a"], amounts)


def product_2a(evidence):
    return participant("product_2a", "product", "2a", "6-isopropyl-1,3-oxazine-2,4-dione 2a (N-benzyl-substituted as drawn)", evidence, SMILES["2a"])


def reagent(label, evidence, equiv=None, molpct=None, role="reagent"):
    amounts = []
    if equiv is not None:
        amounts.append(amount("equivalents", equiv, "equiv", evidence))
    if molpct is not None:
        amounts.append(amount("loading", molpct, "mol%", evidence))
    names = {
        "K2CO3": "potassium carbonate", "Cs2CO3": "cesium carbonate",
        "Na2CO3": "sodium carbonate", "Li2CO3": "lithium carbonate",
        "KHCO3": "potassium bicarbonate", "KOH": "potassium hydroxide",
        "Et3N": "triethylamine", "(i-Pr)2NH": "diisopropylamine",
    }
    return participant(f"base_{label.replace('(', '').replace(')', '').replace('-', '_')}", role, label, names[label], evidence, SMILES[label], amounts)


def solvent(label, evidence):
    names = {"DMSO": "dimethyl sulfoxide", "DMF": "N,N-dimethylformamide", "DMA": "N,N-dimethylacetamide"}
    return participant(f"solvent_{label}", "solvent", label, names[label], evidence, SMILES[label])


def carbon_dioxide(evidence):
    return participant("carbon_dioxide", "reactant", "CO2", "carbon dioxide", evidence, SMILES["CO2"])


records = []

# Graphical abstract and Scheme 1 describe one generic transformation, not a batch experiment.
e_general = ev(1) + ev(2) + ev(4)
generic_parts = [
    participant("generic_allenamide_1", "reactant", "1", "generic 2,3-allenamide 1 (R-group structure)", e_general),
    carbon_dioxide(e_general),
    reagent("K2CO3", e_general, equiv=1.0),
    reagent("Cs2CO3", e_general, equiv=1.0),
    solvent("DMSO", e_general),
    participant("generic_oxazinedione_2", "product", "2", "generic 1,3-oxazine-2,4-dione 2 (R-group structure)", e_general),
]
records.append(record(
    "generic_co2_cyclization", "general_scheme", e_general, generic_parts,
    [{"step_id": "generic_cyclization", "participant_ids": [p["entity_id"] for p in generic_parts], "conditions": [
        field("atmosphere", "CO2 balloon", ev(1)),
        field("temperature", {"number": 70, "unit": "°C"}, ev(1)),
        field("time", {"number": 3, "unit": "h"}, ev(1)),
        field("solvent", "DMSO", ev(1)),
    ]}], [],
    notes=["K2CO3 and Cs2CO3 are alternative bases, not simultaneous additives.", "Scheme 1 is a retrosynthetic/general transformation proposal rather than a discrete reported batch."],
    unresolved=["Generic R-group structures cannot be encoded as complete source-verified SMILES.", "No batch scale, workup, purification, or product-specific outcome belongs to the general scheme."]
))

# Table 1: fifteen distinct optimization rows.
table1 = [
    (1, "K2CO3", "DMF", 4, 90, 1.0, 70, False, False),
    (2, "K2CO3", "DMA", 17, 77, 1.0, 70, False, False),
    (3, "K2CO3", "DMSO", 73, 0, 1.0, 70, False, False),
    (4, "Cs2CO3", "DMSO", 69, 0, 1.0, 70, False, False),
    (5, "Na2CO3", "DMSO", 32, 56, 1.0, 70, False, False),
    (6, "Li2CO3", "DMSO", 13, 83, 1.0, 70, False, False),
    (7, "K2CO3", "DMSO", 72, 6, 0.5, 70, False, False),
    (8, "K2CO3", "DMSO", 70, 0, 2.0, 70, False, False),
    (9, "K2CO3", "DMSO", 55, 34, 1.0, 60, False, False),
    (10, "K2CO3", "DMSO", 75, 0, 1.0, 70, True, False),
    (11, "KHCO3", "DMSO", 25, 21, 1.0, 70, True, False),
    (12, "KOH", "DMSO", 16, 20, 1.0, 70, True, False),
    (13, "Et3N", "DMSO", 5, 50, 1.0, 70, True, False),
    (14, "(i-Pr)2NH", "DMSO", 3, 70, 1.0, 70, True, False),
    (15, "K2CO3", "DMSO", 0, 90, 1.0, 70, True, True),
]
for entry, base, solv, yld, recovery, equiv, temp, closed, n2 in table1:
    evidence = ev(2) + ev(3)
    parts = [substrate_1a(ev(3), 0.2), reagent(base, ev(3), equiv=equiv), solvent(solv, ev(3)), product_2a(ev(3))]
    if not n2:
        parts.insert(1, carbon_dioxide(ev(3)))
    parts.append(participant("nmr_internal_standard", "unspecified_agent", "mesitylene", "mesitylene (1H NMR internal standard)", ev(3), SMILES["mesitylene"]))
    conditions = [
        field("temperature", {"number": temp, "unit": "°C"}, ev(3)),
        field("time", {"number": 3, "unit": "h"}, ev(3)),
        field("solvent", solv, ev(3)),
        field("atmosphere", "N2" if n2 else "CO2 balloon", ev(3)),
    ]
    if closed:
        conditions.append(field("vessel_configuration", "closed vessel without an outlet", ev(3)))
    outcomes = [
        field("NMR_yield_2a", {"number": yld, "unit": "%"}, ev(3), ["product_2a"]),
        field("recovered_starting_material_yield", {"number": recovery, "unit": "%"}, ev(3), ["substrate_1a"]),
        field("yield_measurement_basis", "1H NMR analysis with mesitylene as internal standard", ev(3), ["product_2a"]),
    ]
    records.append(record(
        f"table1_entry{entry}", "optimization_entry", evidence, parts,
        [{"step_id": "reaction", "participant_ids": [p["entity_id"] for p in parts if p["entity_id"] != "nmr_internal_standard"], "conditions": conditions}],
        outcomes,
        notes=["Table 1 optimization row; recovery is kept separate from product yield."],
        unresolved=["Workup and purification are not reported in the main text.", "The recovery measurement method is not explicitly stated separately from the table's NMR-yield footnote.", "Candidate substrate/product connectivity requires chemistry review."]
    ))

# Table 2: eighteen independent scope/condition rows.
scope = [
    (1, "Me", "Me", "H", "Bn", "1a", 75, "2a"),
    (2, "Me", "Me", "H", "Bn", "1a", 70, "2a"),
    (3, "Me", "Me", "H", "Bn", "1a", 64, "2a"),
    (4, "Et", "Me", "H", "Bn", "1b", 80, "2b"),
    (5, "i-Bu", "Me", "H", "Bn", "1c", 64, "2c"),
    (6, "Ph", "Me", "H", "Bn", "1d", 49, "2d"),
    (7, "Me", "Me", "H", "allyl", "1e", 47, "2e"),
    (8, "Me", "Me", "H", "propargyl", "1f", 58, "2f"),
    (9, "Me", "Me", "H", "n-Bu", "1g", 48, "2g"),
    (10, "Me", "Me", "H", "Ph", "1h", 0, "2h"),
    (11, "Me", "Me", "H", "H", "1i", 33, "2i"),
    (12, "Me", "Me", "H", "H", "1i", 55, "2i"),
    (13, "n-C5H11", "H", "H", "Bn", "1j", 59, "2j"),
    (14, "Me", "H", "Et", "Bn", "1k", 76, "2k"),
    (15, "Me", "H", "n-C7H15", "Bn", "1l", 70, "2l"),
    (16, "Me", "Me", "Me", "Bn", "1m", 92, "2m"),
    (17, "Me", "Me", "Et", "Bn", "1n", 94, "2n"),
    (18, "R1/R2 linked by -(CH2)5-", "linked to R1", "Me", "Bn", "1o", 78, "2o"),
]
for entry, r1, r2, r3, r4, slabel, yld, plabel in scope:
    evidence = ev(3)
    scale = 5.0 if entry == 3 else (0.2, 0.4)
    sub_name = "N-benzyl-4-methyl-2,3-pentadienamide" if slabel == "1a" else f"2,3-allenamide {slabel} (R1={r1}, R2={r2}, R3={r3}, R4={r4})"
    prod_name = "6-isopropyl-1,3-oxazine-2,4-dione 2a (N-benzyl-substituted as drawn)" if plabel == "2a" else f"1,3-oxazine-2,4-dione product {plabel} from {slabel}"
    sub_amounts = []
    if isinstance(scale, tuple):
        sub_amounts.append(field("reaction_scale", {"minimum": 0.2, "maximum": 0.4, "unit": "mmol", "raw_text": "0.2–0.4 mmol"}, evidence))
    else:
        sub_amounts.extend([amount("reaction_scale", 5.0, "mmol", evidence), amount("mass", 1.0, "g", evidence)])
    sub = participant("substrate", "reactant", slabel, sub_name, evidence, SMILES["1a"] if slabel == "1a" else None, sub_amounts)
    prod = participant("product", "product", plabel, prod_name, evidence, SMILES["2a"] if plabel == "2a" else None)
    if entry in (17, 18):
        base = reagent("Cs2CO3", evidence, equiv=1.0)
    elif entry == 2:
        base = reagent("K2CO3", evidence, molpct=10, role="catalyst")
    else:
        base = reagent("K2CO3", evidence, equiv=1.0)
    parts = [sub, carbon_dioxide(evidence), base, solvent("DMSO", evidence), prod]
    temp = 60 if entry == 12 else 70
    duration = 12 if entry == 2 else 3
    conditions = [
        field("temperature", {"number": temp, "unit": "°C"}, evidence),
        field("time", {"number": duration, "unit": "h"}, evidence),
        field("solvent", "DMSO", evidence),
        field("atmosphere", "CO2 balloon", evidence),
    ]
    if entry == 3:
        conditions.append(field("CO2_delivery_operation", "glass pipe used instead of relief needle", evidence))
    outcomes = [
        field("isolated_yield", {"number": yld, "unit": "%"}, evidence, ["product"]),
        field("yield_measurement_basis", "isolated yield", evidence, ["product"]),
    ]
    if entry == 10:
        outcomes.append(field("recovered_starting_material_yield", {"number": 74, "unit": "%"}, evidence, ["substrate"]))
    unresolved = ["Atmosphere beyond the CO2 balloon, workup, and purification are not reported in the supplied main text."]
    if slabel != "1a":
        unresolved.append("The fully substituted structure is defined by the table drawing/R groups but no source-reviewed SMILES is asserted.")
    else:
        unresolved.append("Candidate substrate/product connectivity requires chemistry review.")
    records.append(record(
        f"table2_entry{entry}", "substrate_scope_entry", evidence, parts,
        [{"step_id": "reaction", "participant_ids": [p["entity_id"] for p in parts], "conditions": conditions}], outcomes,
        notes=[f"Table 2 row: R1={r1}; R2={r2}; R3={r3}; R4={r4}."], unresolved=unresolved
    ))

# Scheme 2: two distinct unsuccessful comparison experiments.
for label, name, smiles, recovery in [
    ("3a", "N-benzyl but-2(E)-enamide", SMILES["3a"], 100),
    ("3b", "N-benzyl hept-2-ynamide", SMILES["3b"], 78),
]:
    evidence = ev(4)
    parts = [
        participant("substrate", "reactant", label, name, evidence, smiles),
        carbon_dioxide(evidence), reagent("K2CO3", evidence, equiv=1.0), solvent("DMSO", evidence),
    ]
    records.append(record(
        f"scheme2_{label}_no_reaction", "reported_experiment", evidence, parts,
        [{"step_id": "reaction", "participant_ids": [p["entity_id"] for p in parts], "conditions": [
            field("temperature", {"number": 70, "unit": "°C"}, evidence),
            field("time", {"number": 3, "unit": "h"}, evidence),
            field("solvent", "DMSO", evidence),
            field("atmosphere", "CO2 balloon", evidence),
        ]}],
        [
            field("reaction_result", "no reaction", evidence),
            field("recovered_starting_material_yield", {"number": recovery, "unit": "%"}, evidence, ["substrate"]),
        ],
        notes=["Scheme 2 comparison experiment under the same nominal cyclization conditions."],
        unresolved=["Reaction scale, recovery measurement basis, workup, and purification are not reported.", "No product structure or product yield is reported because the source states no reaction.", "Candidate substrate connectivity requires chemistry review."]
    ))

# Scheme 3 is a proposed rationale, not a set of isolated intermediates.
e4 = ev(4)
mechanism_parts = [
    participant("generic_allenamide_1", "reactant", "1", "generic 2,3-allenamide 1", e4),
    participant("generic_base", "reagent", "base", "unspecified base", e4),
    carbon_dioxide(e4),
    participant("intermediate_M1", "unspecified_agent", "M1", "proposed deprotonated allenamide M1", e4),
    participant("intermediate_M2", "unspecified_agent", "M2", "proposed CO2 adduct M2", e4),
    participant("intermediate_M3", "unspecified_agent", "M3", "proposed delocalized allylic intermediate M3", e4),
    participant("proton_source", "reagent", "+H+", "unspecified proton source", e4),
    participant("generic_oxazinedione_2", "product", "2", "generic 1,3-oxazine-2,4-dione 2", e4),
]
records.append(record(
    "scheme3_proposed_mechanism", "mechanism", e4, mechanism_parts,
    [
        {"step_id": "deprotonation", "participant_ids": ["generic_allenamide_1", "generic_base", "intermediate_M1"], "conditions": [field("operation", "proposed deprotonation under basic conditions", e4)]},
        {"step_id": "co2_capture_and_cyclization", "participant_ids": ["intermediate_M1", "carbon_dioxide", "intermediate_M2", "intermediate_M3"], "conditions": [field("operation", "proposed CO2 attack followed by intramolecular attack on the allene central carbon", e4)]},
        {"step_id": "protonolysis", "participant_ids": ["intermediate_M3", "proton_source", "generic_oxazinedione_2"], "conditions": [field("operation", "proposed protonolysis", e4)]},
    ], [],
    notes=["Scheme 3 is explicitly presented as a rationale; M1–M3 are proposed intermediates, not isolated products."],
    unresolved=["Generic R groups, charge localization, proton source, and complete structures remain unverified."]
))


raw_path = OUT / "raw_model/records_pages_0001_0004.json"
raw_path.parent.mkdir(parents=True, exist_ok=True)
raw_path.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")

table1_ids = [f"{DOC}:table1_entry{i}" for i in range(1, 16)]
table2_ids = [f"{DOC}:table2_entry{i}" for i in range(1, 19)]
coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1,
            "state": "attempted",
            "regions": [
                {"region": "title and graphical abstract", "finding": "Generic CO2/K2CO3-or-Cs2CO3 cyclization of 2,3-allenamides to 1,3-oxazine-2,4-diones; classified as a general scheme, not a discrete batch.", "evidence_ids": [f"{DOC}:page1:image", f"{DOC}:page1:text"]},
                {"region": "introduction and cited prior work", "finding": "Background and literature citations only; no cited reaction was reclassified as an experiment from this paper.", "evidence_ids": [f"{DOC}:page1:image", f"{DOC}:page1:text"]},
            ],
            "record_ids": [f"{DOC}:generic_co2_cyclization"],
            "unresolved": ["The generic R-group structures are not complete molecules and remain without SMILES."],
        },
        {
            "page": 2,
            "state": "attempted",
            "regions": [
                {"region": "upper-left Figure 1", "finding": "Examples of biologically active 1,3-oxazine-2,4-diones; illustrative compounds, not experiments reported in this paper.", "evidence_ids": [f"{DOC}:page2:image", f"{DOC}:page2:text"]},
                {"region": "upper-right Scheme 1", "finding": "Retrosynthetic/general proposal connecting oxazinedione 2 to allenamide 1 and CO2; merged with the graphical-abstract general scheme.", "evidence_ids": [f"{DOC}:page2:image", f"{DOC}:page2:text"]},
                {"region": "right-column optimization narrative", "finding": "Narrative evidence for Table 1 entries 1–15, including solvent/base comparisons, loading and temperature changes, closed-vessel standard conditions, and the N2 control.", "evidence_ids": [f"{DOC}:page2:image", f"{DOC}:page2:text", f"{DOC}:page3:image", f"{DOC}:page3:text"]},
            ],
            "record_ids": [f"{DOC}:generic_co2_cyclization"] + table1_ids,
            "unresolved": ["Detailed workup and purification are deferred to SI, which was not supplied or explicitly associated."],
        },
        {
            "page": 3,
            "state": "attempted",
            "regions": [
                {"region": "upper-left Table 1 and footnotes", "finding": "Fifteen independent optimization rows extracted with base, solvent, loading overrides, temperature override, closed-vessel/N2 overrides, NMR product yield, and starting-material recovery.", "evidence_ids": [f"{DOC}:page3:image", f"{DOC}:page3:text"]},
                {"region": "lower-left Figure 2 and adjacent text", "finding": "ORTEP/X-ray confirmation for 2a (CCDC 722623); identity evidence, not a new reaction experiment.", "evidence_ids": [f"{DOC}:page3:image", f"{DOC}:page3:text"]},
                {"region": "right-column Table 2 and footnotes", "finding": "Eighteen independent substrate-scope/condition rows extracted, including 10 mol% K2CO3/12 h, 5.0 mmol scale/glass pipe, 60 °C, Cs2CO3 overrides, and the 1h no-reaction/74% recovery row.", "evidence_ids": [f"{DOC}:page3:image", f"{DOC}:page3:text"]},
            ],
            "record_ids": table1_ids + table2_ids,
            "unresolved": ["Most substrate/product structures are fully specified only by the table drawing and R-group columns; candidate SMILES were not asserted for those rows.", "Operational details and recovery measurement basis are absent from the supplied main text."],
        },
        {
            "page": 4,
            "state": "attempted",
            "regions": [
                {"region": "upper-left Scheme 2", "finding": "Two distinct unsuccessful comparisons extracted: enamide 3a gives no reaction with 100% recovery, and ynamide 3b gives no reaction with 78% recovery under CO2/K2CO3/DMSO, 70 °C, 3 h.", "evidence_ids": [f"{DOC}:page4:image", f"{DOC}:page4:text"]},
                {"region": "upper-right Scheme 3 and rationale", "finding": "Proposed deprotonation/CO2-capture/cyclization/protonolysis mechanism; classified as mechanism, not reported isolation of M1–M3.", "evidence_ids": [f"{DOC}:page4:image", f"{DOC}:page4:text"]},
                {"region": "conclusion and Supporting Information notice", "finding": "Summary of the generic protocol and an availability notice only; no SI file was supplied, so no SI association or SI-only facts were inferred.", "evidence_ids": [f"{DOC}:page4:image", f"{DOC}:page4:text"]},
            ],
            "record_ids": [f"{DOC}:generic_co2_cyclization", f"{DOC}:scheme2_3a_no_reaction", f"{DOC}:scheme2_3b_no_reaction", f"{DOC}:scheme3_proposed_mechanism"],
            "unresolved": ["Scheme 2 omits scale, recovery measurement basis, workup, and purification.", "Mechanistic intermediates and proton source are proposed and unverified.", "SI association remains unestablished."],
        },
    ],
}
coverage_path = OUT / "coverage/pages_0001_0004.json"
coverage_path.parent.mkdir(parents=True, exist_ok=True)
coverage_path.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

tasks_path = OUT / "tasks.json"
tasks = json.loads(tasks_path.read_text())
for task in tasks:
    if task.get("document_id") == DOC and task.get("task_id", "").split(":")[-1] == "text":
        task["state"] = "attempted"
        task["reason"] = "Page image and text inspected; experiments classified and evidence-linked for this extraction pass."
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"records": len(records), "raw": str(raw_path), "coverage": str(coverage_path)}, ensure_ascii=False))
