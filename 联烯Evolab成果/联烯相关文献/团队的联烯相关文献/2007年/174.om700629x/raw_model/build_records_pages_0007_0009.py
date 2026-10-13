#!/usr/bin/env python3
import copy
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / "runs" / "current"
DOC = "doc_d88f44f799f3b8b2"


def ev(page, kind):
    return f"{DOC}:page{page}:{kind}"


def dedupe(values):
    return list(dict.fromkeys(values))


def fact(value, evidence):
    return {
        "value": value,
        "evidence_ids": dedupe(evidence) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def field(name, value, evidence, targets=None):
    item = {"name": name, "fact": fact(value, evidence)}
    if targets:
        item["target_entity_ids"] = list(targets)
    return item


def amount(name, number, unit, evidence, **extra):
    value = {"number": number, "unit": unit, **extra}
    return field(name, value, evidence)


def participant(entity_id, role, label, name, smiles, evidence, amounts=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence) if name is not None else fact(None, []),
        "smiles": fact(smiles, evidence) if smiles is not None else fact(None, []),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": amounts or [],
    }


def add_fact_evidence(item, evidence):
    if item.get("value") is not None:
        item["evidence_ids"] = dedupe(item.get("evidence_ids", []) + list(evidence))
        item["verification"] = "unreviewed"


def add_record_evidence(record, evidence):
    record["evidence_ids"] = dedupe(record["evidence_ids"] + list(evidence))
    record["status"] = "needs_review"
    record["completeness"] = "partial"
    record["review"]["method"] = "none"
    record["review"]["reviewer"] = None
    record["review"]["checked_fields"] = []


dataset = json.loads((RUN / "dataset.json").read_text())
existing = {record["record_id"]: record for record in dataset["experiments"]}


def get(suffix):
    return copy.deepcopy(existing[f"{DOC}:{suffix}"])


page8 = [ev(8, "image"), ev(8, "text")]
page7 = [ev(7, "image"), ev(7, "text")]
page9 = [ev(9, "image"), ev(9, "text")]
records = []


def update_existing_participants(record, evidence):
    for p in record["participants"]:
        add_fact_evidence(p["label"], evidence)
        add_fact_evidence(p["name"], evidence)
        add_fact_evidence(p["smiles"], evidence)
        p["structure_verified"] = False


def add_common_experimental_note(record):
    record["notes"].append(fact(
        "The experimental section states that manipulations used standard Schlenk techniques under nitrogen unless otherwise stated; reaction solvents were dried under nitrogen as described in the source.",
        page8,
    ))
    record["review"]["unresolved"] = dedupe(record["review"]["unresolved"] + [
        "Supporting information is mentioned on page 9, but no SI document was supplied or explicitly associated; no SI-derived facts were used.",
    ])


# Compound 2: replace the provisional equation-only record with its exact page-8 preparation.
r = get("equation2_ru_methyl_allenoate_allyl_2")
add_record_evidence(r, page8 + page9)
update_existing_participants(r, page8)
by_id = {p["entity_id"]: p for p in r["participants"]}
by_id["eq2_ru_hydride_1"]["amounts"] = [
    amount("mass", 143, "mg", page8),
    amount("amount", 0.15, "mmol", page8),
]
by_id["eq2_methyl_allenoate"]["amounts"] = [
    amount("mass", 29, "mg", page8),
    amount("amount", 0.30, "mmol", page8),
]
r["participants"].extend([
    participant("eq2_dichloromethane", "solvent", "dichloromethane", "dichloromethane", "ClCCl", page8,
                [amount("reaction_volume", 6, "mL", page8)]),
    participant("eq2_diethyl_ether", "solvent", "ether", "diethyl ether", "CCOCC", page8,
                [amount("precipitation_volume", 25, "mL", page8), amount("wash_volume", 25, "mL", page8)]),
])
r["steps"] = [
    {
        "step_id": "allene_insertion",
        "participant_ids": ["eq2_ru_hydride_1", "eq2_methyl_allenoate", "eq2_dichloromethane", "eq2_product_2"],
        "conditions": [
            field("time", {"number": 15, "unit": "min"}, page8),
            field("temperature", "room temperature", page8),
            field("atmosphere", "nitrogen", page8),
            field("operation", "stirred to give a clear green solution", page8),
        ],
    },
    {
        "step_id": "isolation",
        "participant_ids": ["eq2_product_2", "eq2_diethyl_ether"],
        "conditions": [
            field("workup", "solution concentrated to dryness under vacuum; oily residue treated with ether; solid collected by filtration", page8),
            field("purification", "solid washed with ether and dried under vacuum", page8),
        ],
    },
]
for outcome in r["outcomes"]:
    if outcome["name"] == "reported_product_formation":
        add_fact_evidence(outcome["fact"], page8)
    if outcome["name"] == "structure_confirmation":
        add_fact_evidence(outcome["fact"], page8 + page9)
r["outcomes"].extend([
    field("isolated_product_mass", {"number": 115, "unit": "mg"}, page8, ["eq2_product_2"]),
    field("isolated_yield", {"number": 83, "unit": "%"}, page8, ["eq2_product_2"]),
    field("yield_measurement_basis", "isolated solid", page8, ["eq2_product_2"]),
    field("dichloromethane_content_by_1H_NMR", {"number": 15, "unit": "mol%", "qualifier": "approx", "raw_text": "ca. 15 mol %"}, page8, ["eq2_product_2"]),
])
for note in r["notes"]:
    if note["value"] and note["value"].startswith("Page 3 reports allylic"):
        add_fact_evidence(note, page8)
r["notes"].append(fact(
    "Single-crystal diffraction for 2 is structural characterization of the isolated product, not a separate synthesis.",
    page8 + page9,
))
r["review"]["unresolved"] = [
    "Room temperature is qualitative; no numerical reaction temperature is reported.",
    "The organoruthenium product structure is retained as a formula/name; no standard SMILES was assigned.",
]
add_common_experimental_note(r)
records.append(r)


# Compound 4: exact phenylallene preparation and isolation.
r = get("equation3_os_phenyl_allene_allyl")
add_record_evidence(r, page8 + page9)
update_existing_participants(r, page8)
by_id = {p["entity_id"]: p for p in r["participants"]}
by_id["eq3_phenyl_os_hydride_3"]["amounts"] = [amount("mass", 215, "mg", page8), amount("amount", 0.207, "mmol", page8)]
by_id["eq3_phenyl_allene"]["amounts"] = [amount("mass", 70, "mg", page8), amount("amount", 0.60, "mmol", page8)]
r["participants"].extend([
    participant("eq3_phenyl_dichloromethane", "solvent", "dichloromethane", "dichloromethane", "ClCCl", page8,
                [amount("reaction_volume", 8, "mL", page8)]),
    participant("eq3_phenyl_hexane", "solvent", "hexane", "hexane", "CCCCCC", page8,
                [amount("allene_solution_volume", 0.3, "mL", page8)]),
    participant("eq3_phenyl_ether", "solvent", "ether", "diethyl ether", "CCOCC", page8,
                [amount("precipitation_volume", 2, "mL", page8)]),
    participant("eq3_phenyl_benzene", "solvent", "benzene", "benzene", "c1ccccc1", page8,
                [amount("redissolution_volume", 5, "mL", page8)]),
])
r["steps"] = [
    {
        "step_id": "allene_insertion",
        "participant_ids": ["eq3_phenyl_os_hydride_3", "eq3_phenyl_allene", "eq3_phenyl_dichloromethane", "eq3_phenyl_hexane", "eq3_phenyl_product"],
        "conditions": [
            field("time", {"number": 14, "unit": "h"}, page8),
            field("temperature", None, []),
            field("atmosphere", "nitrogen", page8),
            field("operation", "phenylallene solution added to a suspension and the resulting mixture stirred", page8),
        ],
    },
    {
        "step_id": "isolation",
        "participant_ids": ["eq3_phenyl_product", "eq3_phenyl_ether", "eq3_phenyl_benzene", "eq3_phenyl_hexane"],
        "conditions": [
            field("workup", "solution filtered and filtrate concentrated to dryness under vacuum; oily residue treated with ether; solid redissolved in benzene and filtered", page8),
            field("purification", "filtrate concentrated to dryness; residue washed with hexane and dried under vacuum", page8),
        ],
    },
]
for outcome in r["outcomes"]:
    add_fact_evidence(outcome["fact"], page8 + (page9 if outcome["name"] == "structure_confirmation" else []))
r["outcomes"].extend([
    field("isolated_product_mass", {"number": 86, "unit": "mg"}, page8, ["eq3_phenyl_product"]),
    field("isolated_yield", {"number": 48, "unit": "%"}, page8, ["eq3_phenyl_product"]),
    field("yield_measurement_basis", "isolated solid", page8, ["eq3_phenyl_product"]),
])
r["notes"].append(fact(
    "The isolated yellow solid was characterized by NMR and elemental analysis; single-crystal diffraction for 4 is characterization, not a separate reaction.",
    page8 + page9,
))
r["review"]["unresolved"] = [
    "The reaction temperature is not stated in the compound-specific procedure and was not inferred.",
    "The amount of hexane used for the final wash is not reported.",
    "The organo-osmium product structure is retained as a formula/name; no standard SMILES was assigned.",
]
add_common_experimental_note(r)
records.append(r)


# Compound 5: exact benzyl-substituted allene preparation and isolation.
r = get("equation3_os_benzyl_allene_allyl")
add_record_evidence(r, page8)
update_existing_participants(r, page8)
by_id = {p["entity_id"]: p for p in r["participants"]}
by_id["eq3_benzyl_os_hydride_3"]["amounts"] = [amount("mass", 200, "mg", page8), amount("amount", 0.19, "mmol", page8)]
by_id["eq3_benzyl_allene"]["amounts"] = [amount("mass", 74, "mg", page8), amount("amount", 0.57, "mmol", page8)]
r["participants"].extend([
    participant("eq3_benzyl_dichloromethane", "solvent", "dichloromethane", "dichloromethane", "ClCCl", page8,
                [amount("reaction_volume", 15, "mL", page8)]),
    participant("eq3_benzyl_ether", "solvent", "ether", "diethyl ether", "CCOCC", page8,
                [amount("precipitation_volume", 15, "mL", page8), amount("wash_volume_each", 15, "mL", page8)]),
])
r["steps"] = [
    {
        "step_id": "allene_insertion",
        "participant_ids": ["eq3_benzyl_os_hydride_3", "eq3_benzyl_allene", "eq3_benzyl_dichloromethane", "eq3_benzyl_product"],
        "conditions": [
            field("time", {"number": 2, "unit": "d"}, page8),
            field("temperature", "room temperature", page8),
            field("atmosphere", "nitrogen", page8),
            field("operation", "mixture stirred to give a clear yellow solution", page8),
        ],
    },
    {
        "step_id": "isolation",
        "participant_ids": ["eq3_benzyl_product", "eq3_benzyl_ether"],
        "conditions": [
            field("workup", "solution concentrated to dryness under vacuum; oily residue treated with ether; solid collected by filtration", page8),
            field("purification", "solid washed three times with ether and dried under vacuum", page8),
        ],
    },
]
for outcome in r["outcomes"]:
    add_fact_evidence(outcome["fact"], page8)
r["outcomes"].extend([
    field("isolated_product_mass", {"number": 63, "unit": "mg"}, page8, ["eq3_benzyl_product"]),
    field("isolated_yield", {"number": 35, "unit": "%"}, page8, ["eq3_benzyl_product"]),
    field("yield_measurement_basis", "isolated solid", page8, ["eq3_benzyl_product"]),
])
r["notes"].append(fact("The isolated white solid was characterized by NMR and elemental analysis.", page8))
r["review"]["unresolved"] = [
    "Room temperature is qualitative; no numerical reaction temperature is reported.",
    "The organo-osmium product structure is retained as a formula/name; no standard SMILES was assigned.",
]
add_common_experimental_note(r)
records.append(r)


# Compound 11: exact Ru/PPh3 preparation and isolation.
r = get("equation5_ru_tertbutyl_allene_vinyl_11")
add_record_evidence(r, page8)
update_existing_participants(r, page8)
by_id = {p["entity_id"]: p for p in r["participants"]}
by_id["eq5_ru_hydride_10"]["amounts"] = [amount("mass", 308, "mg", page8), amount("amount", 0.333, "mmol", page8)]
by_id["eq5_allene"]["amounts"] = [amount("mass", 65, "mg", page8), amount("amount", 0.67, "mmol", page8)]
r["participants"].extend([
    participant("eq5_dichloromethane", "solvent", "dichloromethane", "dichloromethane", "ClCCl", page8,
                [amount("reaction_volume", 8, "mL", page8)]),
    participant("eq5_pentane", "solvent", "pentane", "pentane", "CCCCC", page8,
                [amount("allene_solution_volume", 0.5, "mL", page8)]),
    participant("eq5_diethyl_ether", "solvent", "diethyl ether", "diethyl ether", "CCOCC", page8,
                [amount("precipitation_volume", 5, "mL", page8), amount("wash_volume_each", 3, "mL", page8)]),
])
r["steps"] = [
    {
        "step_id": "vinyl_complex_formation",
        "participant_ids": ["eq5_ru_hydride_10", "eq5_allene", "eq5_dichloromethane", "eq5_pentane", "eq5_product_11"],
        "conditions": [
            field("time", {"number": 7, "unit": "h"}, page8),
            field("temperature", "room temperature", page8),
            field("atmosphere", "nitrogen", page8),
            field("operation", "allene solution added dropwise at room temperature, then stirred", page8),
        ],
    },
    {
        "step_id": "isolation",
        "participant_ids": ["eq5_product_11", "eq5_diethyl_ether"],
        "conditions": [
            field("workup", "mixture concentrated to dryness to form a paste; ether added to produce a yellow solid; solid collected by filtration", page8),
            field("purification", "solid washed three times with ether and dried under vacuum", page8),
        ],
    },
]
for outcome in r["outcomes"]:
    add_fact_evidence(outcome["fact"], page8)
r["outcomes"].extend([
    field("isolated_product_mass", {"number": 100, "unit": "mg"}, page8, ["eq5_product_11"]),
    field("isolated_yield", {"number": 35, "unit": "%"}, page8, ["eq5_product_11"]),
    field("yield_measurement_basis", "isolated solid", page8, ["eq5_product_11"]),
])
for note in r["notes"]:
    add_fact_evidence(note, page8)
r["review"]["unresolved"] = [
    "Room temperature is qualitative; no numerical reaction temperature is reported.",
    "The organoruthenium product structure is retained as a formula/name; no standard SMILES was assigned.",
]
add_common_experimental_note(r)
records.append(r)


# Mechanistic model records: add page-7 structures/charges, page-8 conclusion, and page-9 methods.
for suffix, model_label in [
    ("scheme1_pc1_phosphine_computational_pathways", "PC1 tris-phosphine model"),
    ("scheme1_pc2_carbonyl_computational_pathways", "PC2 carbonyl/phosphine model"),
]:
    r = get(suffix)
    add_record_evidence(r, page7 + page8 + page9)
    update_existing_participants(r, page7 + page9)
    for outcome in r["outcomes"]:
        add_fact_evidence(outcome["fact"], page7 + page8)
    r["notes"].extend([
        fact(
            f"Figure 5 gives calculated precursor structures for the {model_label}; Figure 6 gives Mulliken atomic charges from ECP and all-electron basis sets. These are computational evidence, not wet experiments.",
            page7,
        ),
        fact(
            "The authors attribute the reversed regiochemical preference to the larger electron-density increase at the central allene carbon in PC1; the carbonyl ligand in PC2 reduces metal-to-allene back-donation.",
            page7 + page8,
        ),
        fact(
            "Geometries and frequencies were calculated at B3LYP; LanL2DZ ECPs were used for Os, P, and Cl and 6-31G** for C, O, and H; transition states were checked by IRC calculations in Gaussian 03.",
            page9,
        ),
        fact(
            "PH3 modeled PPh3 in the small calculations; selected species were also evaluated by two-layer ONIOM (B3LYP/BSI:HF/LanL2MB) with phenyl groups in the second layer.",
            page9,
        ),
    ])
    r["review"]["unresolved"] = dedupe(r["review"]["unresolved"] + [
        "Figure 6 charges combine sigma and pi components and are presented by the authors as qualitative support rather than a standalone regiochemical criterion.",
        "Supporting information with calculated Cartesian coordinates is mentioned but was not supplied or explicitly associated.",
    ])
    records.append(r)


records_path = RUN / "raw_model" / "records_pages_0007_0009.json"
records_path.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")


def rid(suffix):
    return f"{DOC}:{suffix}"


mechanism_ids = [
    rid("scheme1_pc1_phosphine_computational_pathways"),
    rid("scheme1_pc2_carbonyl_computational_pathways"),
]
experimental_ids = [
    rid("equation2_ru_methyl_allenoate_allyl_2"),
    rid("equation3_os_phenyl_allene_allyl"),
    rid("equation3_os_benzyl_allene_allyl"),
    rid("equation5_ru_tertbutyl_allene_vinyl_11"),
]

coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 7,
            "state": "attempted",
            "regions": [
                {
                    "region": "upper-left Figure 5",
                    "finding": "Calculated PC1-vinyl/PC1-allyl and PC2-vinyl/PC2-allyl precursor structures and bond lengths; associated with the two existing computational mechanism records, not treated as reactions.",
                    "evidence_ids": [ev(7, "image"), ev(7, "text")],
                },
                {
                    "region": "upper-right Figure 6",
                    "finding": "Mulliken atomic-charge comparison for free allene and the PC1/PC2 precursor variants using ECP and all-electron basis sets; computational evidence only.",
                    "evidence_ids": [ev(7, "image"), ev(7, "text")],
                },
                {
                    "region": "lower two-column mechanistic discussion and conclusion opening",
                    "finding": "The prose explains the ligand-dependent reversal in hydride migration using differential metal-to-allene back-donation and explicitly treats the charge analysis as qualitative support; no new wet experiment, table row, or reaction arrow appears.",
                    "evidence_ids": [ev(7, "image"), ev(7, "text")],
                },
            ],
            "record_ids": mechanism_ids,
            "unresolved": [
                "Calculated organometallic structures and transition states were not converted to SMILES.",
                "The source cautions that the reported total atomic charges do not separate sigma and pi contributions.",
            ],
        },
        {
            "page": 8,
            "state": "attempted",
            "regions": [
                {
                    "region": "upper-left conclusion",
                    "finding": "Conclusion restates the computational rationale for phosphine systems giving vinyl complexes and carbonyl-containing systems giving eta3-allyl complexes; merged into the existing mechanism records.",
                    "evidence_ids": [ev(8, "image"), ev(8, "text")],
                },
                {
                    "region": "left-column Experimental Section general methods",
                    "finding": "General nitrogen/Schlenk atmosphere and solvent-drying statements apply to the four compound preparations on this page unless otherwise stated; no SI was associated from this text.",
                    "evidence_ids": [ev(8, "image"), ev(8, "text")],
                },
                {
                    "region": "left-column preparation of complex 2",
                    "finding": "Exact Ru hydride and methyl-allenoate quantities, dichloromethane volume, room-temperature 15 min reaction, ether isolation, 115 mg product mass, and 83% yield merged into the existing equation-2 record.",
                    "evidence_ids": [ev(8, "image"), ev(8, "text")],
                },
                {
                    "region": "right-column preparations of complexes 4, 5, and 11",
                    "finding": "Three distinct existing equation records augmented with their exact reactant/solvent quantities, durations, isolation sequences, product masses, and 48%, 35%, and 35% yields; no duplicate experiments created.",
                    "evidence_ids": [ev(8, "image"), ev(8, "text")],
                },
                {
                    "region": "lower-right Crystal Structure Analyses of 2 and 4",
                    "finding": "Crystallization and diffraction methods characterize products 2 and 4 and were linked to those existing reaction records; they are not separate syntheses.",
                    "evidence_ids": [ev(8, "image"), ev(8, "text")],
                },
            ],
            "record_ids": experimental_ids + mechanism_ids,
            "unresolved": [
                "The compound-4 reaction temperature is not stated; it was not inferred from nearby procedures.",
                "Room temperature is qualitative for compounds 2, 5, and 11.",
                "Complex organometallic structures remain without verified SMILES.",
            ],
        },
        {
            "page": 9,
            "state": "attempted",
            "regions": [
                {
                    "region": "upper-left continuation of Crystal Structure Analyses",
                    "finding": "Continuation of refinement details for products 2 and 4; linked as structural characterization and not counted as another reaction.",
                    "evidence_ids": [ev(9, "image"), ev(9, "text")],
                },
                {
                    "region": "upper and middle Computational Details",
                    "finding": "B3LYP, basis-set/ECP, frequency, IRC, all-electron single-point, PH3-model, and ONIOM details merged into the two existing computational mechanism records; no wet experiment appears.",
                    "evidence_ids": [ev(9, "image"), ev(9, "text")],
                },
                {
                    "region": "middle-right acknowledgments and Supporting Information Available statement",
                    "finding": "No reaction record. The page states that calculated coordinates and CIF files are available online, but no SI file was supplied or explicitly associated in the workspace.",
                    "evidence_ids": [ev(9, "image"), ev(9, "text")],
                },
                {
                    "region": "lower reference list and blank lower page",
                    "finding": "Method references and journal furniture only; no additional reaction, condition, yield, table, or arrow.",
                    "evidence_ids": [ev(9, "image"), ev(9, "text")],
                },
            ],
            "record_ids": [experimental_ids[0], experimental_ids[1]] + mechanism_ids,
            "unresolved": [
                "The advertised supporting information and crystallographic files were not supplied or explicitly associated and were not mined.",
                "Computational geometries and charge decompositions remain unverified machine records.",
            ],
        },
    ],
}

coverage_path = RUN / "coverage" / "pages_0007_0009.json"
coverage_path.parent.mkdir(parents=True, exist_ok=True)
coverage_path.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

tasks_path = RUN / "tasks.json"
tasks = json.loads(tasks_path.read_text())
target_tasks = {ev(page, "text") for page in range(7, 10)}
for task in tasks:
    if task["task_id"] in target_tasks:
        task["state"] = "attempted"
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"replacement_records": len(records), "coverage_pages": len(coverage["pages"])}, ensure_ascii=False))
