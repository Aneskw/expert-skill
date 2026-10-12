#!/usr/bin/env python3
"""Enrich existing reaction records with source evidence from PDF pages 7-8."""
import copy
import json
from pathlib import Path


DOC = "doc_d84cc3c252b14204"
BASE = Path(__file__).resolve().parents[1]
DATASET = BASE / "dataset.json"


def evidence(page):
    return [f"{DOC}:page{page}:text", f"{DOC}:page{page}:image"]


def fact(value, evidence_ids):
    return {
        "value": value,
        "evidence_ids": list(evidence_ids),
        "verification": "missing" if value is None else "unreviewed",
    }


def field(name, value, evidence_ids, targets=None):
    result = {"name": name, "fact": fact(value, evidence_ids)}
    if targets:
        result["target_entity_ids"] = list(targets)
    return result


def quantity(number, unit):
    return {"number": number, "unit": unit}


def add_unique(items, values):
    for value in values:
        if value not in items:
            items.append(value)


def participant(record, entity_id):
    return next(item for item in record["participants"] if item["entity_id"] == entity_id)


def add_amount(record, entity_id, name, value, evidence_ids):
    amounts = participant(record, entity_id)["amounts"]
    if not any(item["name"] == name for item in amounts):
        amounts.append(field(name, value, evidence_ids))


def add_outcome(record, name, value, evidence_ids, targets):
    existing = next((item for item in record["outcomes"] if item["name"] == name), None)
    if existing is None:
        record["outcomes"].append(field(name, value, evidence_ids, targets))
    else:
        add_unique(existing["fact"]["evidence_ids"], evidence_ids)


def support_outcomes(record, evidence_ids, names):
    for outcome in record["outcomes"]:
        if outcome["name"] in names:
            add_unique(outcome["fact"]["evidence_ids"], evidence_ids)


def add_note(record, value, evidence_ids):
    if not any(item["value"] == value for item in record["notes"]):
        record["notes"].append(fact(value, evidence_ids))


data = json.loads(DATASET.read_text())
by_source_id = {record["source_reaction_id"]: record for record in data["experiments"]}
selected_ids = [
    "table3_entry08",
    "table3_entry09",
    "table3_entry10",
    "table4_entry02",
    "table4_entry03",
    "table4_entry04",
    "table4_entry05",
    "eq1_hydroalkenylation_7af",
    "eq2_hydroarylation_product9",
    "eq3_hydroarylation_1_2_decadiene",
    "eq4_hydroarylation_1e",
]
records = [copy.deepcopy(by_source_id[source_id]) for source_id in selected_ids]
records_by_id = {record["source_reaction_id"]: record for record in records}
page7 = evidence(7)
page8 = evidence(8)


# Page 7 begins with the analytical continuation of the 7db experiment.
record = records_by_id["table3_entry08"]
add_unique(record["evidence_ids"], page7)
add_note(
    record,
    "PDF page 7 begins with the HRMS continuation for product 7db; no additional reaction condition or outcome is introduced there.",
    page7,
)


# Detailed experimental paragraphs for Table 3 entries 9 and 10.
for source_id, substrate_mass, substrate_amount, boronic_mass, boronic_amount, product_mass in [
    ("table3_entry09", 108, 0.50, 152, 1.0, 28),
    ("table3_entry10", 98, 0.50, 152, 1.0, 72),
]:
    record = records_by_id[source_id]
    add_unique(record["evidence_ids"], page7)
    add_amount(record, "substrate", "mass", quantity(substrate_mass, "mg"), page7)
    add_amount(record, "substrate", "amount", quantity(substrate_amount, "mmol"), page7)
    add_amount(record, "boronic_acid", "mass", quantity(boronic_mass, "mg"), page7)
    add_amount(record, "boronic_acid", "amount", quantity(boronic_amount, "mmol"), page7)
    add_outcome(record, "isolated_product_mass", quantity(product_mass, "mg"), page7, ["major", "minor"])
    support_outcomes(record, page7, {"7_to_6_ratio", "E_to_Z_ratio_of_7"})

add_outcome(
    records_by_id["table3_entry09"],
    "combined_yield_reported_in_experimental_prose",
    quantity(18, "%"),
    page7,
    ["major", "minor"],
)
add_outcome(
    records_by_id["table3_entry10"],
    "combined_yield_reported_in_experimental_prose",
    quantity(47, "%"),
    page7,
    ["major", "minor"],
)
add_note(
    records_by_id["table3_entry10"],
    "Table 3 reports 46% yield of product 7fa, whereas the page-7 experimental paragraph reports 47% for the combined 6fa/7fa material; both source statements are retained separately.",
    page7,
)


# Detailed experimental paragraphs for Table 4 entries 2-5.
table4_details = {
    "table4_entry02": (61, 0.50, 42, "ethyl 2-benzyl-3-phenylbut-2-enoate"),
    "table4_entry03": (68, 0.50, 45, "ethyl 2-benzyl-3-(4-methylphenyl)but-2-enoate"),
    "table4_entry04": (84, 0.50, 51, "ethyl 2-benzyl-3-(3-nitrophenyl)but-2-enoate"),
    "table4_entry05": (99, 0.50, 56, "ethyl 2-benzyl-3-(4-phenylphenyl)but-2-enoate"),
}
for source_id, (boronic_mass, boronic_amount, product_mass, product_name) in table4_details.items():
    record = records_by_id[source_id]
    add_unique(record["evidence_ids"], page7)
    add_amount(record, "substrate", "mass", quantity(51, "mg"), page7)
    add_amount(record, "substrate", "amount", quantity(0.25, "mmol"), page7)
    add_amount(record, "boronic_acid", "mass", quantity(boronic_mass, "mg"), page7)
    add_amount(record, "boronic_acid", "amount", quantity(boronic_amount, "mmol"), page7)
    add_outcome(record, "isolated_product_mass", quantity(product_mass, "mg"), page7, ["major", "minor"])
    support_outcomes(record, page7, {"combined_yield", "7_to_6_ratio", "E_to_Z_ratio_of_7"})
    major = participant(record, "major")
    major["name"] = fact(product_name, page7)

add_note(
    records_by_id["table4_entry03"],
    "The page-7 paragraph prints (E)-7ac/(E)-7ac = 98:2, while Table 4 assigns the ratio as (E)-7ac/(Z)-7ac = 98:2; the structured selectivity follows the explicit Table 4 heading and the prose typo remains logged.",
    page7,
)


# Page 8 reference [20] is structural characterization for 7ac, not a new synthesis.
record = records_by_id["table4_entry03"]
add_unique(record["evidence_ids"], page8)
add_note(
    record,
    "Reference [20] reports X-ray crystal data for (E)-7ac and identifies CCDC 213522; this is structural characterization, not a separate reaction experiment or an associated SI file in this workspace.",
    page8,
)


# Detailed paragraphs for Equations 1-4. The reaction identity and time remain
# sourced from the earlier equation pages; page 7 adds scale, mass, and repeated outcomes.
equation_details = {
    "eq1_hydroalkenylation_7af": ("substrate", 32, 0.16, 50, 0.32, 26,
                                   {"combined_yield", "7af_to_6af_ratio", "2E4E_to_2Z4E_ratio"}, ["major", "minor"]),
    "eq2_hydroarylation_product9": ("substrate", 32, 0.25, 76, 0.50, 25,
                                     {"combined_yield", "9_to_10_ratio", "E9_to_Z9_ratio"}, ["major", "minor"]),
    "eq3_hydroarylation_1_2_decadiene": ("substrate", 69, 0.50, 152, 1.00, 88,
                                          {"combined_yield", "12_to_13_ratio", "E13_to_Z13_ratio"}, ["p12", "p13"]),
    "eq4_hydroarylation_1e": ("substrate", 65, 0.24, 73, 0.48, 82,
                              {"combined_yield", "5ea_to_4ea_ratio", "stereochemical_assignment"}, ["p5ea", "p4ea"]),
}
for source_id, (substrate_id, substrate_mass, substrate_amount, boronic_mass, boronic_amount,
                product_mass, outcome_names, targets) in equation_details.items():
    record = records_by_id[source_id]
    add_unique(record["evidence_ids"], page7)
    add_amount(record, substrate_id, "mass", quantity(substrate_mass, "mg"), page7)
    add_amount(record, substrate_id, "amount", quantity(substrate_amount, "mmol"), page7)
    add_amount(record, "boronic_acid", "mass", quantity(boronic_mass, "mg"), page7)
    add_amount(record, "boronic_acid", "amount", quantity(boronic_amount, "mmol"), page7)
    add_outcome(record, "isolated_product_mass", quantity(product_mass, "mg"), page7, targets)
    support_outcomes(record, page7, outcome_names)


coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 7,
            "state": "attempted",
            "regions": [
                {
                    "region": "upper-left margin, continuation from page 6",
                    "finding": "HRMS characterization continues for product 7db; no new reaction conditions or outcome are introduced.",
                    "evidence_ids": page7,
                },
                {
                    "region": "left column, paragraphs for 7ea and 7fa",
                    "finding": "Detailed scales and product masses for the existing Table 3 entries 9 and 10; the 7fa prose combined yield (47%) is retained separately from the Table 3 product-7 yield (46%).",
                    "evidence_ids": page7,
                },
                {
                    "region": "left column, paragraphs for 7ab, 7ac, 7ad, and 7ae",
                    "finding": "Detailed scales and product masses for existing Table 4 entries 2-5. The apparent (E)-7ac/(E)-7ac source typo is logged rather than silently normalized.",
                    "evidence_ids": page7,
                },
                {
                    "region": "right column, paragraphs for 7af and product 9",
                    "finding": "Detailed scales and product masses for the existing Equation 1 hydroalkenylation and Equation 2 hydroarylation experiments.",
                    "evidence_ids": page7,
                },
                {
                    "region": "right column, paragraphs for products 12/13 and 5ea/4ea",
                    "finding": "Detailed scales and product masses for the existing Equation 3 and Equation 4 hydroarylation experiments.",
                    "evidence_ids": page7,
                },
                {
                    "region": "lower-right acknowledgment",
                    "finding": "Funding acknowledgment only; no reaction, scheme, table, arrow, or experimental footnote.",
                    "evidence_ids": page7,
                },
            ],
            "record_ids": [record["record_id"] for record in records if f"{DOC}:page7:image" in record["evidence_ids"]],
            "unresolved": [
                "Page 7 provides names and characterization but no molecular drawings; product SMILES remain unverified or absent.",
                "Yield measurement basis is not explicitly stated for every paragraph.",
                "No Supporting Information file is explicitly associated in this workspace.",
            ],
        },
        {
            "page": 8,
            "state": "attempted",
            "regions": [
                {
                    "region": "two-column references [1]-[19] and [21]-[25]",
                    "finding": "Reviews and cited prior work; these are bibliography entries, not experiments newly reported in this paper.",
                    "evidence_ids": page8,
                },
                {
                    "region": "right column, reference [20]",
                    "finding": "Crystal data and CCDC 213522 for (E)-7ac; treated as structural characterization linked to the existing Table 4 entry 3, not as a separate synthetic experiment.",
                    "evidence_ids": page8,
                },
                {
                    "region": "lower-right received-date line",
                    "finding": "Publication metadata only; no reaction information.",
                    "evidence_ids": page8,
                },
            ],
            "record_ids": [records_by_id["table4_entry03"]["record_id"]],
            "unresolved": [
                "The external CCDC deposit was not supplied and was not inspected.",
                "Reference [20] does not establish an associated Supporting Information file in this workspace.",
            ],
        },
    ],
}


(BASE / "raw_model").mkdir(parents=True, exist_ok=True)
(BASE / "coverage").mkdir(parents=True, exist_ok=True)
(BASE / "raw_model" / "extracted_records_pages_0007_0008.json").write_text(
    json.dumps(records, ensure_ascii=False, indent=2) + "\n"
)
(BASE / "coverage" / "pages_0007_0008.json").write_text(
    json.dumps(coverage, ensure_ascii=False, indent=2) + "\n"
)


tasks_path = BASE / "tasks.json"
tasks = json.loads(tasks_path.read_text())
for task in tasks:
    if task.get("document_id") != DOC:
        continue
    page = int(task["evidence_id"].split(":page", 1)[1].split(":", 1)[0])
    if page in (7, 8):
        task["state"] = "attempted"
        task["visual_evidence_id"] = f"{DOC}:page{page}:image"
        task["reason"] = (
            "Original rendered page image inspected; regions and linked records are documented "
            "in coverage/pages_0007_0008.json."
        )
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"submitted_records": len(records), "coverage_pages": [7, 8]}, ensure_ascii=False))
