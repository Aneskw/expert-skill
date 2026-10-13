import copy
import json
from pathlib import Path


DOC = "doc_ef875e24c663dcfb"
BASE = Path(__file__).resolve().parents[1]
DATASET = BASE / "dataset.json"
PAGE6 = [f"{DOC}:page6:text", f"{DOC}:page6:image"]
PAGE7 = [f"{DOC}:page7:text", f"{DOC}:page7:image"]
RECORD_ID = f"{DOC}:table6_entry2_table7_entry1"


def fact(value, evidence):
    return {
        "value": value,
        "evidence_ids": list(evidence) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def field(name, value, evidence, targets=None):
    result = {"name": name, "fact": fact(value, evidence)}
    if targets:
        result["target_entity_ids"] = targets
    return result


def q(number, unit):
    return {"number": number, "unit": unit}


def participant(entity_id, role, label=None, name=None, smiles=None, amounts=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, PAGE7),
        "name": fact(name, PAGE7),
        "smiles": fact(smiles, PAGE7),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": amounts or [],
    }


def add_evidence(fact_obj, evidence):
    if fact_obj.get("value") is not None:
        fact_obj["evidence_ids"] = list(dict.fromkeys(fact_obj["evidence_ids"] + list(evidence)))


data = json.loads(DATASET.read_text())
record = copy.deepcopy(next(r for r in data["experiments"] if r["record_id"] == RECORD_ID))
record["evidence_ids"] = list(dict.fromkeys(record["evidence_ids"] + PAGE7))
parts = {p["entity_id"]: p for p in record["participants"]}

# Make reruns deterministic when the page-7-enriched record is already present.
record["participants"] = [
    p for p in record["participants"]
    if p["entity_id"] not in {"saturated_ammonium_chloride", "diethyl_ether", "magnesium_sulfate"}
]
parts = {p["entity_id"]: p for p in record["participants"]}
parts["pd_allyl_chloride_dimer"]["amounts"] = [
    a for a in parts["pd_allyl_chloride_dimer"]["amounts"]
    if not (a["name"] == "amount" and a["fact"]["value"] == q(0.0075, "mmol"))
]
parts["iodide"]["amounts"] = [a for a in parts["iodide"]["amounts"] if a["name"] != "mass"]
parts["ligand"]["amounts"] = [a for a in parts["ligand"]["amounts"] if a["name"] not in {"mass", "amount"}]
parts["thf"]["amounts"] = [
    a for a in parts["thf"]["amounts"]
    if a["name"] not in {"catalyst_solution_THF_volume", "ligand_solution_THF_volume", "iodide_solution_THF_volume"}
]
record["steps"] = [s for s in record["steps"] if s["step_id"] not in {"workup", "purification"}]
cross = next(s for s in record["steps"] if s["step_id"] == "cross_coupling")
cross["conditions"] = [c for c in cross["conditions"] if c["name"] not in {"addition_operation", "completion_monitoring"}]
record["outcomes"] = [o for o in record["outcomes"] if o["name"] not in {"isolated_product_mass", "physical_form"}]

# Page 7 completes the catalyst phrase split across the page boundary.
catalyst = parts["pd_allyl_chloride_dimer"]
catalyst["amounts"].append(field("amount", q(0.0075, "mmol"), PAGE6 + PAGE7))

# The substrate is restated on page 7 with a mass and amount.
iodide = parts["iodide"]
add_evidence(iodide["label"], PAGE7)
add_evidence(iodide["name"], PAGE7)
add_evidence(iodide["amounts"][0]["fact"], PAGE7)
iodide["amounts"].append(field("mass", q(68, "mg"), PAGE7))
iodide["smiles"] = fact("COC(=O)/C=C(\\I)C", PAGE7)

# Page 7 gives the exact rac-L3 quantity.
ligand = parts["ligand"]
add_evidence(ligand["label"], PAGE7)
add_evidence(ligand["name"], PAGE7)
ligand["amounts"].extend([
    field("mass", q(14, "mg"), PAGE7),
    field("amount", q(0.030, "mmol"), PAGE7),
])

# Preserve the three separately stated 1 mL THF portions instead of silently summing them.
thf = parts["thf"]
add_evidence(thf["name"], PAGE7)
add_evidence(thf["smiles"], PAGE7)
thf["amounts"].extend([
    field("catalyst_solution_THF_volume", q(1, "mL"), PAGE7),
    field("ligand_solution_THF_volume", q(1, "mL"), PAGE7),
    field("iodide_solution_THF_volume", q(1, "mL"), PAGE7),
])

# The systematic name and formula on page 7 support candidate connectivity only;
# stereochemistry and source identity remain unverified machine assignments.
product = parts["product"]
add_evidence(product["label"], PAGE7)
add_evidence(product["name"], PAGE7)
product["smiles"] = fact("COC(=O)/C=C(\\C)C(c1ccccc1)=C=CCCC", PAGE7)

# Workup materials are explicitly introduced in the source and therefore structured.
record["participants"].extend([
    participant("saturated_ammonium_chloride", "reagent", name="saturated aqueous ammonium chloride"),
    participant("diethyl_ether", "solvent", name="diethyl ether", smiles="CCOCC"),
    participant("magnesium_sulfate", "reagent", name="magnesium sulfate", smiles="[Mg+2].[O-]S(=O)(=O)[O-]"),
])

temperature = next(c for c in cross["conditions"] if c["name"] == "temperature")
add_evidence(temperature["fact"], PAGE7)
cross["conditions"].extend([
    field("addition_operation", "prepared zinc reagent transferred by syringe to the catalyst/substrate mixture at room temperature", PAGE7),
    field("completion_monitoring", "reaction complete as monitored by TLC", PAGE7),
])
record["steps"].extend([
    {
        "step_id": "workup",
        "participant_ids": ["product", "saturated_ammonium_chloride", "diethyl_ether", "magnesium_sulfate"],
        "conditions": [
            field("workup", "quench with saturated aqueous NH4Cl; extract with diethyl ether; dry combined organic phase over MgSO4; filter; evaporate solvent in vacuo", PAGE7)
        ],
    },
    {
        "step_id": "purification",
        "participant_ids": ["product"],
        "conditions": [field("purification", "flash chromatography", PAGE7)],
    },
])

yield_field = next(o for o in record["outcomes"] if o["name"] == "isolated_yield")
basis_field = next(o for o in record["outcomes"] if o["name"] == "yield_measurement_basis")
add_evidence(yield_field["fact"], PAGE7)
add_evidence(basis_field["fact"], PAGE7)
record["outcomes"].extend([
    field("isolated_product_mass", q(70, "mg"), PAGE7, ["product"]),
    field("physical_form", "oil", PAGE7, ["product"]),
])

record["notes"] = [
    fact("Table 6 entry 2, Table 7 entry 1, and Typical procedure II on pages 6–7 describe the same batch and are represented once.", record["evidence_ids"]),
    fact("Page 7 reports 1H NMR, 13C NMR, IR, EI-MS, and HRMS characterization for isolated (E)-6ad.", PAGE7),
]
record["review"]["unresolved"] = [
    "Supporting information was not explicitly supplied or associated.",
    "Candidate SMILES were generated from fully specified names; connectivity and E/Z assignments remain machine-unverified against a structure drawing.",
]

raw_path = BASE / "raw_model" / "records_pages_0007_0007.json"
raw_path.write_text(json.dumps([record], ensure_ascii=False, indent=2) + "\n")

coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 7,
            "state": "attempted",
            "regions": [
                {
                    "region": "upper-left continuation of Typical procedure II",
                    "finding": "Continuation of the existing Table 6 entry 2/Table 7 entry 1 batch: exact catalyst, rac-L3, iodide and THF quantities; room-temperature zinc-reagent transfer; TLC completion; NH4Cl/ether/MgSO4 workup; flash chromatography; and 70 mg (91%) of (E)-6ad were merged into the existing record rather than duplicated.",
                    "evidence_ids": PAGE7,
                },
                {
                    "region": "upper-left analytical characterization paragraph",
                    "finding": "NMR, IR, EI-MS and HRMS characterize (E)-6ad but do not constitute another reaction experiment.",
                    "evidence_ids": PAGE7,
                },
                {
                    "region": "middle-left acknowledgements and keywords",
                    "finding": "No reaction arrows, tables or new experimental batches; reproduction acknowledgements refer back to already extracted Table 3 and Table 7 rows.",
                    "evidence_ids": PAGE7,
                },
                {
                    "region": "lower-left and full right-column references",
                    "finding": "Bibliographic references and cited prior-work remarks only; they were not converted into experiments of this paper.",
                    "evidence_ids": PAGE7,
                },
            ],
            "record_ids": [RECORD_ID],
            "unresolved": [
                "No supporting-information file was explicitly supplied or associated.",
                "Candidate substrate/product connectivity and E/Z assignments remain machine-unverified; analytical spectra were noted but not atom-by-atom interpreted.",
            ],
        }
    ],
}
coverage_path = BASE / "coverage" / "pages_0007_0007.json"
coverage_path.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

tasks_path = BASE / "tasks.json"
tasks = json.loads(tasks_path.read_text())
for task in tasks:
    if task["task_id"] == f"{DOC}:page7:text":
        task["state"] = "attempted"
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"records": 1, "raw": str(raw_path), "coverage": str(coverage_path)}, ensure_ascii=False))
