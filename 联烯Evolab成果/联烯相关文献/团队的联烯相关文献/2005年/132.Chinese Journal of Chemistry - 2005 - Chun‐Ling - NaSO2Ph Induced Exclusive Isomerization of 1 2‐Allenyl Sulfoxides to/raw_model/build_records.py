import json
from pathlib import Path

DOC = "doc_55acfbb1564e2913"
BASE = Path(__file__).resolve().parents[1]


def ev(page):
    return [f"{DOC}:page{page}:text", f"{DOC}:page{page}:image"]


def fact(value, evidence):
    return {
        "value": value,
        "evidence_ids": list(evidence) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def field(name, value, evidence, targets=None):
    item = {"name": name, "fact": fact(value, evidence)}
    if targets:
        item["target_entity_ids"] = targets
    return item


def participant(entity_id, role, label, name, smiles, evidence, amounts=None):
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


def qty(number, unit, raw_text=None):
    value = {"number": number, "unit": unit}
    if raw_text:
        value["raw_text"] = raw_text
    return value


STARTING_SMILES = {
    "1a": "CC=C=CS(=O)c1ccccc1",
    "1b": "CCC=C=CS(=O)c1ccccc1",
    "1c": "CC(C)C=C=CS(=O)c1ccccc1",
    "1d": "CCCCC=C=CS(=O)c1ccccc1",
    "1e": "CCCCCC=C=CS(=O)c1ccccc1",
    "1f": "CCCCCCCC=C=CS(=O)c1ccccc1",
    "1g": "CCCCCCCCCC=C=CS(=O)c1ccccc1",
    "1h": "O=S(c1ccccc1)C=C=Cc1ccccc1",
}

PRODUCT_DATA = {
    "3a": ("2-butynyl phenyl sulfoxide", "CC#CCS(=O)c1ccccc1"),
    "3b": ("2-pentynyl phenyl sulfoxide", "CCC#CCS(=O)c1ccccc1"),
    "3c": ("4-methyl-2-pentynyl phenyl sulfoxide", "CC(C)C#CCS(=O)c1ccccc1"),
    "3d": ("2-heptynyl phenyl sulfoxide", "CCCCC#CCS(=O)c1ccccc1"),
    "3e": ("2-octynyl phenyl sulfoxide", "CCCCCC#CCS(=O)c1ccccc1"),
    "3f": ("2-decynyl phenyl sulfoxide", "CCCCCCCC#CCS(=O)c1ccccc1"),
    "3g": ("2-dodynyl phenyl sulfoxide", "CCCCCCCCCC#CCS(=O)c1ccccc1"),
    "3h": ("3-phenyl-2-propynyl phenyl sulfoxide", "O=S(c1ccccc1)CC#Cc1ccccc1"),
}

REAGENT_SMILES = "[Na+].[O-]S(=O)c1ccccc1"


def base_record(record_id, source_id, kind, evidence, participants, steps, outcomes,
                notes=None, unresolved=None):
    return {
        "record_id": f"{DOC}:{record_id}",
        "document_id": DOC,
        "source_reaction_id": source_id,
        "record_kind": kind,
        "status": "needs_review",
        "completeness": "partial",
        "evidence_ids": evidence,
        "participants": participants,
        "steps": steps,
        "outcomes": outcomes,
        "notes": [fact(n, evidence) for n in (notes or [])],
        "review": {
            "method": "model",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved or [],
        },
    }


def scheme_loading_record(tag, equivalents, yield_pct):
    evidence = ev(1)
    reactant = participant("reactant_1a", "reactant", "1a", "1,2-butadienyl phenyl sulfoxide",
                           STARTING_SMILES["1a"], evidence)
    product = participant("product_3a", "product", "3a", PRODUCT_DATA["3a"][0],
                          PRODUCT_DATA["3a"][1], evidence)
    reagent = participant(
        "reagent_nasoph", "reagent", "NaSO2Ph", "sodium benzenesulfinate", REAGENT_SMILES,
        evidence, [field("equivalents", qty(equivalents, "equiv"), evidence)],
    )
    solvent = participant("solvent_mecn", "solvent", "CH3CN", "acetonitrile", "CC#N", evidence)
    outcomes = [
        field("yield", qty(yield_pct, "%"), evidence, ["product_3a"]),
        field("yield_measurement_basis", "isolated yield" if equivalents == 2.0 else None,
              evidence if equivalents == 2.0 else [], ["product_3a"]),
    ]
    return base_record(
        f"scheme1_loading_{tag}", f"Scheme 1 loading {equivalents} equiv",
        "optimization_entry", evidence, [reactant, product, reagent, solvent],
        [{"step_id": "isomerization", "participant_ids": ["reactant_1a", "reagent_nasoph", "solvent_mecn"],
          "conditions": [field("reaction_temperature", "r.t.", evidence),
                         field("reaction_time", qty(6, "h"), evidence),
                         field("solvent", "CH3CN", evidence)]}],
        outcomes,
        notes=["3a was reported as the only observed product; the intended conjugate-addition product 2a was not obtained."],
        unresolved=[
            "Machine-proposed structures require source review.",
            "Reaction scale, product mass, workup, purification, and atmosphere were not reported for this screening row.",
            "Supporting-information association is unestablished.",
        ],
    )


SOLVENTS = {
    "acetone": ("Me2CO", "acetone", "CC(=O)C", 59, 0),
    "thf": ("THF", "tetrahydrofuran", "C1CCOC1", 60, 0),
    "dmf": ("DMF", "N,N-dimethylformamide", "CN(C)C=O", 60, 0),
    "dmso": ("DMSO", "dimethyl sulfoxide", "CS(C)=O", 67, 0),
    "benzene": ("PhH", "benzene", "c1ccccc1", 8, 57),
    "toluene": ("PhMe", "toluene", "Cc1ccccc1", 24, 43),
}


def solvent_record(tag, values):
    label, name, smiles, yield_pct, recovered = values
    evidence = ev(2)
    reactant = participant("reactant_1a", "reactant", "1a", "1,2-butadienyl phenyl sulfoxide",
                           STARTING_SMILES["1a"], evidence)
    product = participant("product_3a", "product", "3a", PRODUCT_DATA["3a"][0],
                          PRODUCT_DATA["3a"][1], evidence)
    reagent = participant(
        "reagent_nasoph", "reagent", "NaSO2Ph", "sodium benzenesulfinate", REAGENT_SMILES,
        evidence, [field("equivalents", qty(2, "equiv"), evidence)],
    )
    solvent = participant("solvent", "solvent", label, name, smiles, evidence)
    return base_record(
        f"table1_solvent_{tag}", f"Table 1 entry {label}", "optimization_entry", evidence,
        [reactant, product, reagent, solvent],
        [{"step_id": "isomerization", "participant_ids": ["reactant_1a", "reagent_nasoph", "solvent"],
          "conditions": [field("reaction_temperature", "r.t.", evidence),
                         field("reaction_time", qty(6, "h"), evidence),
                         field("solvent", label, evidence)]}],
        [field("isolated_yield", qty(yield_pct, "%"), evidence, ["product_3a"]),
         field("yield_measurement_basis", "isolated yield", evidence, ["product_3a"]),
         field("starting_material_recovered", qty(recovered, "%"), evidence, ["reactant_1a"])],
        unresolved=[
            "Machine-proposed structures require source review.",
            "Reaction scale, product mass, workup, purification, and atmosphere were not reported for this screening row.",
            "Supporting-information association is unestablished.",
        ],
    )


SCOPE = {
    "3a": {"start": "1a", "time": 6, "yield": 83, "page": 2, "rmass": 71.6, "mmol": 0.4,
            "gmass": 131.2, "gmmol": 0.8, "pmass": 59.3, "temperature": qty(16, "°C")},
    "3b": {"start": "1b", "time": 6, "yield": 85, "page": 2, "rmass": 76.8, "mmol": 0.4,
            "gmass": 137.7, "gmmol": 0.8, "pmass": 65.0, "temperature": "r.t."},
    "3c": {"start": "1c", "time": 21, "yield": 84, "page": 2, "rmass": 80.6, "mmol": 0.4,
            "gmass": 131.9, "gmmol": 0.8, "pmass": 67.6, "temperature": "r.t."},
    "3d": {"start": "1d", "time": 22, "yield": 86, "page": 2, "rmass": 88.6, "mmol": 0.4,
            "gmass": 132.6, "gmmol": 0.8, "pmass": 75.8, "temperature": "r.t."},
    "3e": {"start": "1e", "time": 5, "yield": 87, "page": 3, "rmass": 95.0, "mmol": 0.4,
            "gmass": 132.1, "gmmol": 0.8, "pmass": 81.7, "temperature": "r.t."},
    "3f": {"start": "1f", "time": 21, "yield": 92, "page": 3, "rmass": 80.4, "mmol": 0.3,
            "gmass": 100.3, "gmmol": 0.6, "pmass": 73.6, "temperature": "r.t."},
    "3g": {"start": "1g", "time": 6, "yield": 77, "page": 3, "rmass": 72.6, "mmol": 0.25,
            "gmass": 84.1, "gmmol": 0.5, "pmass": 55.8, "temperature": "r.t."},
    "3h": {"start": "1h", "time": 19, "yield": 55, "page": 3, "rmass": 96.4, "mmol": 0.4,
            "gmass": 133.4, "gmmol": 0.8, "pmass": 53.2, "temperature": "r.t.",
            "recovered_mass": 8.8, "recovered_pct": 9},
}


def scope_record(product_label, data):
    start = data["start"]
    detail_evidence = ev(data["page"])
    evidence = ev(2) if data["page"] == 2 else ev(2) + ev(3)
    reactant = participant(
        "reactant", "reactant", start, f"1,2-allenyl phenyl sulfoxide {start}", STARTING_SMILES[start],
        evidence,
        [field("mass", qty(data["rmass"], "mg"), detail_evidence),
         field("amount", qty(data["mmol"], "mmol"), detail_evidence)],
    )
    product_name, product_smiles = PRODUCT_DATA[product_label]
    product = participant("product", "product", product_label, product_name, product_smiles, evidence)
    reagent = participant(
        "reagent_nasoph", "reagent", "NaSO2Ph", "sodium benzenesulfinate", REAGENT_SMILES,
        evidence,
        [field("mass", qty(data["gmass"], "mg"), detail_evidence),
         field("amount", qty(data["gmmol"], "mmol"), detail_evidence),
         field("equivalents", qty(2, "equiv"), ev(2))],
    )
    solvent_amounts = [field("volume", qty(2, "mL"), ev(2))] if product_label == "3a" else []
    solvent = participant("solvent_mecn", "solvent", "CH3CN", "acetonitrile", "CC#N", evidence,
                          solvent_amounts)
    conditions = [
        field("reaction_temperature", data["temperature"], ev(2) if data["temperature"] == "r.t." else detail_evidence),
        field("reaction_time", qty(data["time"], "h"), ev(2)),
        field("solvent", "CH3CN", ev(2)),
    ]
    if product_label == "3a":
        conditions += [
            field("workup", "quenched with 5 mL water; extracted with diethyl ether (25 mL × 3); washed with brine; dried over anhydrous Na2SO4; solvent evaporated", detail_evidence),
            field("purification", "silica-gel column chromatography, petroleum ether/ethyl acetate = 3:1 (v/v)", detail_evidence),
        ]
    outcomes = [
        field("isolated_yield", qty(data["yield"], "%"), evidence, ["product"]),
        field("yield_measurement_basis", "isolated yield", ev(2), ["product"]),
        field("isolated_product_mass", qty(data["pmass"], "mg"), detail_evidence, ["product"]),
    ]
    if product_label == "3h":
        outcomes += [
            field("recovered_starting_material_mass", qty(data["recovered_mass"], "mg"), detail_evidence, ["reactant"]),
            field("starting_material_recovered", qty(data["recovered_pct"], "%"), ev(2), ["reactant"]),
        ]
    unresolved = [
        "Machine-proposed structures require source review.",
        "Reaction atmosphere was not reported.",
        "Supporting-information association is unestablished.",
    ]
    if product_label != "3a":
        unresolved.append("Workup and purification were not stated in the abbreviated preparation.")
    notes = ["Product was reported as an oil."]
    if product_label == "3a":
        notes.append("Table 1 MeCN/83% entry, Table 2 entry 1, and the typical procedure were treated as one repeated report of the same experiment.")
    return base_record(
        f"table2_{product_label}", f"Table 2 {start} to {product_label}", "substrate_scope_entry",
        evidence, [reactant, product, reagent, solvent],
        [{"step_id": "isomerization_and_isolation", "participant_ids": ["reactant", "reagent_nasoph", "solvent_mecn"],
          "conditions": conditions}],
        outcomes, notes=notes, unresolved=unresolved,
    )


records = []
for tag, equiv, result in [
    ("0p1eq", 0.1, 74), ("0p2eq", 0.2, 74), ("0p5eq", 0.5, 75),
    ("1p0eq", 1.0, 76), ("2p0eq", 2.0, 82),
]:
    records.append(scheme_loading_record(tag, equiv, result))
for tag, values in SOLVENTS.items():
    records.append(solvent_record(tag, values))
for product_label, data in SCOPE.items():
    records.append(scope_record(product_label, data))

raw_path = Path(__file__).with_name("records_pages_0001_0004.json")
raw_path.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")

ids = [record["record_id"] for record in records]
p1_ids = ids[:5]
p2_ids = ids[5:]
p3_ids = [f"{DOC}:table2_3{x}" for x in "efgh"]
coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1,
            "state": "attempted",
            "regions": [
                {"region": "Scheme 1 reaction arrow and NaSO2Ph-equivalent/yield table",
                 "finding": "Five distinct loading-screen experiments for 1a→3a were extracted; 3a is described as the only product, while intended product 2a was not obtained.",
                 "evidence_ids": ev(1)},
                {"region": "Introduction and discussion around Scheme 1",
                 "finding": "Narrative context and prior-work discussion; no additional independent current-paper experiment beyond Scheme 1 rows.",
                 "evidence_ids": ev(1)},
            ],
            "record_ids": p1_ids,
            "unresolved": ["No explicitly associated supporting information was supplied.",
                           "Machine-proposed molecular structures remain unverified."],
        },
        {
            "page": 2,
            "state": "attempted",
            "regions": [
                {"region": "Table 1 solvent screen",
                 "finding": "Seven solvent rows inspected. Six new optimization records were created; the MeCN/83% row was merged with Table 2 entry 1 and the typical procedure as the same experiment.",
                 "evidence_ids": ev(2)},
                {"region": "Table 2 substrate scope and footnotes",
                 "finding": "Eight substrate-scope rows extracted separately with row-specific time and isolated yield; footnote c preserves 9% recovery of 1h.",
                 "evidence_ids": ev(2)},
                {"region": "Scheme 2",
                 "finding": "Proposed/general base-catalyzed isomerization mechanism, classified as mechanism rather than a reported experiment.",
                 "evidence_ids": ev(2)},
                {"region": "Experimental typical procedure and preparations 3a–3d",
                 "finding": "Exact masses, amounts and product masses captured; workup and chromatography apply explicitly to 3a only.",
                 "evidence_ids": ev(2)},
            ],
            "record_ids": p2_ids,
            "unresolved": ["Atmosphere is not reported.",
                           "Abbreviated preparations 3b–3d do not state workup or purification.",
                           "Machine-proposed molecular structures remain unverified."],
        },
        {
            "page": 3,
            "state": "attempted",
            "regions": [
                {"region": "Experimental preparations 3e–3h",
                 "finding": "Four detailed product-preparation paragraphs inspected; exact reactant/reagent/product masses and isolated yields captured, including recovered 1h mass for 3h.",
                 "evidence_ids": ev(3)},
                {"region": "References 1–8 (partial)",
                 "finding": "Prior literature citations only; no current-paper experiments created from references.",
                 "evidence_ids": ev(3)},
            ],
            "record_ids": p3_ids,
            "unresolved": ["Workup and purification are not stated for 3e–3h.",
                           "Atmosphere is not reported.",
                           "Machine-proposed molecular structures remain unverified."],
        },
        {
            "page": 4,
            "state": "attempted",
            "regions": [
                {"region": "References 8–12 continuation",
                 "finding": "References and prior-work citations only; no current-paper reaction arrow, table row, or experimental procedure is present.",
                 "evidence_ids": ev(4)},
            ],
            "record_ids": [],
            "unresolved": [],
        },
    ],
}
(BASE / "coverage" / "pages_0001_0004.json").write_text(
    json.dumps(coverage, ensure_ascii=False, indent=2) + "\n"
)
print(json.dumps({"records": len(records), "raw": str(raw_path), "coverage_pages": 4}))
