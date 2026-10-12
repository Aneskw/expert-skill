#!/usr/bin/env python3
"""Build page-7 additions/enrichments for the jo0342469 extraction."""
import copy
import json
from pathlib import Path


DOC = "doc_70cf3d194c2f126f"
BASE = Path(__file__).resolve().parents[1]
DATASET = json.loads((BASE / "dataset.json").read_text())
P7 = [f"{DOC}:page7:text", f"{DOC}:page7:image"]


def fact(value, evidence=P7):
    return {
        "value": value,
        "evidence_ids": list(evidence) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def field(name, value, targets=None, evidence=P7):
    item = {"name": name, "fact": fact(value, evidence)}
    if targets:
        item["target_entity_ids"] = list(targets)
    return item


def qty(number, unit, raw_text=None):
    item = {"number": number, "unit": unit}
    if raw_text is not None:
        item["raw_text"] = raw_text
    return item


def participant(entity_id, role, label, amounts=None, name=None, smiles=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label),
        "name": fact(name),
        "smiles": fact(smiles),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": amounts or [],
    }


def existing(suffix):
    rid = f"{DOC}:{suffix}"
    record = next(copy.deepcopy(r) for r in DATASET["experiments"] if r["record_id"] == rid)
    for evidence_id in P7:
        if evidence_id not in record["evidence_ids"]:
            record["evidence_ids"].append(evidence_id)
    return record


def by_entity(record, suffix):
    return next(p for p in record["participants"] if p["entity_id"].endswith(suffix))


def add_amount(participant_obj, name, value):
    participant_obj["amounts"].append(field(name, value))


records = []

# The (R)-2n preparation starts on page 6 and only its characterization continues on page 7.
r = existing("scheme5_R1n_to_R2n")
r["notes"].append(fact("Analytical characterization of (R)-2n continues at the top of page 7; it is not a new reaction."))
records.append(r)

# Detailed typical procedure corresponding to Table 1 entry 1.
r = existing("table1_entry_01")
add_amount(by_entity(r, "_substrate"), "mass", qty(0.048, "g"))
add_amount(by_entity(r, "_substrate"), "amount", qty(0.15, "mmol"))
add_amount(by_entity(r, "_allyl"), "mass", qty(0.112, "g"))
add_amount(by_entity(r, "_allyl"), "amount", qty(0.93, "mmol"))
add_amount(by_entity(r, "_solv"), "volume", qty(1, "mL"))
add_amount(by_entity(r, "_7a"), "mass", qty(0.033, "g"))
r["steps"][0]["conditions"].append(field("temperature", qty(25, "°C")))
r["outcomes"].extend([
    field("workup", "add ether; wash with brine three times; dry over Na2SO4; evaporate"),
    field("purification", "column chromatography on silica gel, petroleum ether/ether 5:1"),
])
r["review"]["unresolved"] = [
    "Table 1 states 5 equiv allyl bromide, whereas the detailed masses and amounts are 0.112 g/0.93 mmol for 0.15 mmol 2a; both source statements are retained.",
    "Structures remain represented by source labels and are unverified; no SI was explicitly provided.",
]
records.append(r)

# The detailed 8a paragraph has the same time/yields as Table 1 entry 2, but explicitly says THF,
# while the table says DMA. Preserve this as a cross-source condition conflict in one record.
r = existing("table1_entry_02")
add_amount(by_entity(r, "_substrate"), "mass", qty(0.046, "g"))
add_amount(by_entity(r, "_substrate"), "amount", qty(0.15, "mmol"))
add_amount(by_entity(r, "_allyl"), "mass", qty(0.111, "g"))
add_amount(by_entity(r, "_allyl"), "amount", qty(0.92, "mmol"))
add_amount(by_entity(r, "_base"), "mass", qty(0.033, "g"))
add_amount(by_entity(r, "_base"), "amount", qty(0.24, "mmol"))
r["participants"].append(participant("table1_entry_02_thf_text", "solvent", "THF", [field("volume", qty(2.5, "mL"))], name="THF", smiles="C1CCOC1"))
add_amount(by_entity(r, "_7a"), "mass", qty(0.023, "g"))
add_amount(by_entity(r, "_8a"), "mass", qty(0.009, "g"))
r["steps"][0]["conditions"].extend([
    field("temperature", qty(25, "°C")),
    field("experimental_section_solvent", "THF"),
])
r["review"]["unresolved"] = [
    "Table 1 entry 2 reports DMA, but the detailed experimental paragraph reports 2.5 mL THF for the matching 23 h, 44% 7a/17% 8a experiment; the conflict is retained without choosing one solvent.",
    "Table 1 states 5 equiv allyl bromide and 1.5 equiv K2CO3, whereas the detailed amounts correspond to 0.92 mmol allyl bromide and 0.24 mmol K2CO3 for 0.15 mmol 2a; both source statements are retained.",
    "Structures remain represented by source labels and are unverified; no SI was explicitly provided.",
]
records.append(r)

# Detailed asymmetric coupling examples corresponding to Table 2 entries 12 and 13.
for suffix, sub_mass, sub_mmol, sub_ee, allyl_vol, allyl_mmol, dma_vol, prod_mass, prod_ee in [
    ("table2_entry_12", 0.093, 0.32, 87, 0.14, 1.58, 2.0, 0.097, 86),
    ("table2_entry_13", 0.020, 0.07, 78, 0.03, 0.34, 1.5, 0.020, 76),
]:
    r = existing(suffix)
    sub = by_entity(r, "_substrate")
    product = next(p for p in r["participants"] if p["role"] == "product")
    add_amount(sub, "mass", qty(sub_mass, "g"))
    add_amount(sub, "amount", qty(sub_mmol, "mmol"))
    add_amount(sub, "experimental_section_enantiomeric_excess", qty(sub_ee, "%"))
    add_amount(by_entity(r, "_allyl"), "volume", qty(allyl_vol, "mL"))
    add_amount(by_entity(r, "_allyl"), "amount", qty(allyl_mmol, "mmol"))
    add_amount(by_entity(r, "_solv"), "volume", qty(dma_vol, "mL"))
    add_amount(product, "mass", qty(prod_mass, "g"))
    r["steps"][0]["conditions"].append(field("temperature", qty(25, "°C")))
    r["outcomes"].append(field("experimental_section_product_ee", qty(prod_ee, "%"), [product["entity_id"]]))
    r["review"]["unresolved"] = list(dict.fromkeys(r["review"]["unresolved"] + [
        "Rounded ee values in the detailed experimental paragraph are retained alongside the more precise Scheme 5 values where they differ.",
        "Absolute configurations are reported as tentatively assigned; structures remain unverified and no SI was explicitly provided.",
    ]))
    records.append(r)

# Detailed 9a procedure corresponding to Table 4 entry 1. It conflicts with the table footnote scale.
r = existing("table4_entry_01")
add_amount(by_entity(r, "_substrate"), "detailed_experiment_mass", qty(0.083, "g"))
add_amount(by_entity(r, "_substrate"), "detailed_experiment_amount", qty(0.27, "mmol"))
add_amount(by_entity(r, "_allyl"), "mass", qty(0.167, "g"))
add_amount(by_entity(r, "_allyl"), "amount", qty(1.38, "mmol"))
add_amount(by_entity(r, "_solv"), "detailed_experiment_volume", qty(1.6, "mL"))
add_amount(by_entity(r, "_9a"), "mass", qty(0.085, "g"))
r["steps"][0]["conditions"].append(field("temperature", qty(25, "°C")))
r["review"]["unresolved"] = [
    "Table 4 footnote gives 0.50 mmol substrate in 3 mL DMA for the table reactions, while the detailed 9a procedure gives 0.27 mmol 6a in 1.6 mL DMA; both scale statements are retained.",
    "Structures remain represented by source labels and are unverified; no SI was explicitly provided.",
]
records.append(r)

# Detailed quantities for the three Scheme 8 mechanistic experiments.
mechanistic_details = {
    "scheme8_entry_01": {
        "2b": (0.052, 0.16), "pd": (0.055, 0.15), "dma": 1.0, "product_mass": 0.019,
    },
    "scheme8_entry_02": {
        "2b": (0.108, 0.34), "pd": (0.146, 0.37), "dma": 2.0, "product_mass": 0.044,
    },
    "scheme8_entry_03": {
        "2b": (0.089, 0.28), "pd": (0.100, 0.27), "dma": 2.0, "product_mass": 0.075,
        "added": (0.506, 5.59),
    },
}
for suffix, values in mechanistic_details.items():
    r = existing(suffix)
    add_amount(by_entity(r, "_2b"), "mass", qty(values["2b"][0], "g"))
    add_amount(by_entity(r, "_2b"), "amount", qty(values["2b"][1], "mmol"))
    add_amount(by_entity(r, "_pd"), "mass", qty(values["pd"][0], "g"))
    add_amount(by_entity(r, "_pd"), "amount", qty(values["pd"][1], "mmol"))
    add_amount(by_entity(r, "_dma"), "volume", qty(values["dma"], "mL"))
    if "added" in values:
        add_amount(by_entity(r, "_added"), "mass", qty(values["added"][0], "g"))
        add_amount(by_entity(r, "_added"), "amount", qty(values["added"][1], "mmol"))
    r["outcomes"].append(field("combined_product_mass", qty(values["product_mass"], "g"), [p["entity_id"] for p in r["participants"] if p["role"] == "product"]))
    r["review"]["unresolved"] = [
        "Mixture component structures and stereoisomer distribution remain unverified; no SI was explicitly provided."
    ]
    records.append(r)

# Authentic 15 preparation is a separate reported experiment, not the Scheme 8 mixture.
auth_suffix = "authentic_15"
auth_product = f"{auth_suffix}_product"
auth_participants = [
    participant(f"{auth_suffix}_2b", "reactant", "2b", [field("mass", qty(0.072, "g")), field("amount", qty(0.22, "mmol"))]),
    participant(f"{auth_suffix}_agno3", "unspecified_agent", "AgNO3", [field("amount", qty(20, "mol%"))]),
    participant(f"{auth_suffix}_acetone", "solvent", "acetone", [field("volume", qty(2.5, "mL"))], name="acetone", smiles="CC(C)=O"),
    participant(auth_product, "product", "2-hexyl-4-methyl-1-(p-toluenesulfonyl)-2,5-dihydro-1H-pyrrole (15)", [field("mass", qty(0.069, "g"))]),
]
records.append({
    "record_id": f"{DOC}:{auth_suffix}",
    "document_id": DOC,
    "source_reaction_id": auth_suffix,
    "record_kind": "reported_experiment",
    "status": "candidate",
    "completeness": "partial",
    "evidence_ids": P7,
    "participants": auth_participants,
    "steps": [{
        "step_id": "cycloisomerization",
        "participant_ids": [p["entity_id"] for p in auth_participants if p["role"] != "product"],
        "conditions": [
            field("time", qty(5, "h")), field("temperature", qty(25, "°C")), field("solvent", "acetone"),
        ],
    }],
    "outcomes": [
        field("isolated_yield", qty(96, "%"), [auth_product]),
        field("yield_measurement_basis", "isolated yield", [auth_product]),
    ],
    "notes": [],
    "review": {
        "method": "none", "reviewer": None, "checked_fields": [],
        "unresolved": [
            "The source gives AgNO3 at 20 mol% but does not explicitly name its role; it is retained as unspecified_agent rather than inferred as catalyst.",
            "No reaction workup or purification is reported in the visible paragraph.",
            "The product is named in text but no structure drawing occurs on page 7; SMILES is left missing and unverified.",
            "No SI was explicitly associated with the supplied PDF.",
        ],
    },
})

out = Path(__file__).with_name("extracted_records_page_0007.json")
out.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"output": str(out), "records_submitted": len(records)}, ensure_ascii=False))
