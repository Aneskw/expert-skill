import json
from pathlib import Path

DOC = "doc_845edabe092493ff"
OUT = Path(__file__).with_name("records_pages_0001_0005.json")


def ev(page):
    return [f"{DOC}:page{page}:text", f"{DOC}:page{page}:image"]


def uniq(items):
    return list(dict.fromkeys(items))


def fact(value, evidence):
    return {
        "value": value,
        "evidence_ids": uniq(evidence) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def field(name, value, evidence, targets=None):
    item = {"name": name, "fact": fact(value, evidence)}
    if targets:
        item["target_entity_ids"] = targets
    return item


def participant(entity_id, role, name, evidence, label=None, smiles=None, amounts=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence),
        "smiles": fact(smiles, evidence),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": [field(n, v, evidence) for n, v in (amounts or [])],
    }


def record(rid, kind, evidence, participants, steps, outcomes, notes, unresolved):
    return {
        "record_id": f"{DOC}:{rid}",
        "document_id": DOC,
        "source_reaction_id": rid,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": uniq(evidence),
        "participants": participants,
        "steps": steps,
        "outcomes": outcomes,
        "notes": [fact(n, evidence) for n in notes],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved,
        },
    }


subs = {
    "1a": ("3,4-dichlorophenyl", "c1cc(Cl)c(Cl)cc1"),
    "1b": ("4-ethylphenyl", "c1ccc(CC)cc1"),
    "1c": ("4-cyanophenyl", "c1ccc(C#N)cc1"),
    "1d": ("2-chlorophenyl", "c1ccccc1Cl"),
    "1e": ("4-chlorophenyl", "c1ccc(Cl)cc1"),
    "1f": ("4-isopropylphenyl", "c1ccc(C(C)C)cc1"),
    "1g": ("phenyl", "c1ccccc1"),
    "1h": ("4-fluorophenyl", "c1ccc(F)cc1"),
    "1i": ("2-trifluoromethylphenyl", "c1ccccc1C(F)(F)F"),
    "1j": ("4-methylphenyl", "c1ccc(C)cc1"),
    "1k": ("2,6-dichlorophenyl", "c1c(Cl)cccc1Cl"),
    "1l": ("1-naphthyl", "c1cccc2ccccc12"),
}


def propargyl_smiles(label):
    return "C#CC(O)" + subs[label][1]


def allenol_smiles(label):
    return "C=C=CC(O)" + subs[label][1]


def acetate_smiles(label):
    return "C=C=CC(OC(C)=O)" + subs[label][1]


def alcohol_name(label):
    return f"1-({subs[label][0]})buta-2,3-dien-1-ol" if label != "1g" else "1-phenylbuta-2,3-dien-1-ol"


synthesis_data = {
    "1a": {"pages": [1, 2], "start": [("mass", {"number": 4.02, "unit": "g"}), ("amount", {"number": 20, "unit": "mmol"})], "pf": [("mass", {"number": 1.48, "unit": "g"}), ("amount", {"number": 49, "unit": "mmol"})], "cu": [("mass", {"number": 1.45, "unit": "g"}), ("amount", {"number": 10, "unit": "mmol"})], "amine": [("volume", {"number": 5, "unit": "mL"}), ("amount", {"number": 38.2, "unit": "mmol"})], "solvent": 30, "product_mass": 2.37, "yield": 55, "temperature": 120, "time": 1.5},
    "1b": {"pages": [1, 2, 3], "start": [("mass", {"number": 8.00, "unit": "g"}), ("amount", {"number": 50, "unit": "mmol"})], "pf": [("mass", {"number": 3.70, "unit": "g"}), ("amount", {"number": 123, "unit": "mmol"})], "cu": [("mass", {"number": 3.60, "unit": "g"}), ("amount", {"number": 25, "unit": "mmol"})], "amine": [("mass", {"number": 9.27, "unit": "g"}), ("amount", {"number": 92, "unit": "mmol"})], "solvent": 77, "product_mass": 4.52, "yield": 52},
    "1c": {"pages": [1, 3], "start": [("mass", {"number": 1.90, "unit": "g"}), ("amount", {"number": 12, "unit": "mmol"})], "pf": [("mass", {"number": 0.90, "unit": "g"}), ("amount", {"number": 30, "unit": "mmol"})], "cu": [("mass", {"number": 0.87, "unit": "g"}), ("amount", {"number": 6, "unit": "mmol"})], "amine": [("mass", {"number": 2.22, "unit": "g"}), ("amount", {"number": 22, "unit": "mmol"})], "solvent": 18.5, "product_mass": 1.27, "yield": 62},
    "1d": {"pages": [1, 3], "start": [("mass", {"number": 16.60, "unit": "g"}), ("amount", {"number": 100, "unit": "mmol"})], "pf": [("mass", {"number": 7.40, "unit": "g"}), ("amount", {"number": 246, "unit": "mmol"})], "cu": [("mass", {"number": 7.24, "unit": "g"}), ("amount", {"number": 50, "unit": "mmol"})], "amine": [("mass", {"number": 18.54, "unit": "g"}), ("amount", {"number": 184, "unit": "mmol"})], "solvent": 154, "product_mass": 8.20, "yield": 41},
    "1e": {"pages": [1, 3], "start": [("mass", {"number": 9.20, "unit": "g"}), ("amount", {"number": 55, "unit": "mmol"})], "pf": [("mass", {"number": 4.10, "unit": "g"}), ("amount", {"number": 137, "unit": "mmol"})], "cu": [("mass", {"number": 4.00, "unit": "g"}), ("amount", {"number": 27.8, "unit": "mmol"})], "amine": [("mass", {"number": 10.20, "unit": "g"}), ("amount", {"number": 100, "unit": "mmol"})], "solvent": 85, "product_mass": 6.18, "yield": 62},
    "1f": {"pages": [1, 3], "start": [("mass", {"number": 3.48, "unit": "g"}), ("amount", {"number": 20, "unit": "mmol"})], "pf": [("mass", {"number": 1.48, "unit": "g"}), ("amount", {"number": 49, "unit": "mmol"})], "cu": [("mass", {"number": 1.45, "unit": "g"}), ("amount", {"number": 10, "unit": "mmol"})], "amine": [("volume", {"number": 5.0, "unit": "mL"}), ("amount", {"number": 38.2, "unit": "mmol"})], "solvent": 30, "product_mass": 1.58, "yield": 42},
    "1g": {"pages": [1, 3], "start": [("mass", {"number": 13.2, "unit": "g"}), ("amount", {"number": 100, "unit": "mmol"})], "pf": [("mass", {"number": 7.40, "unit": "g"}), ("amount", {"number": 246, "unit": "mmol"})], "cu": [("mass", {"number": 7.24, "unit": "g"}), ("amount", {"number": 50, "unit": "mmol"})], "amine": [("mass", {"number": 18.54, "unit": "g"}), ("amount", {"number": 184, "unit": "mmol"})], "solvent": 154, "product_mass": 7.59, "yield": 52},
    "1h": {"pages": [1, 3], "start": [("mass", {"number": 7.50, "unit": "g"}), ("amount", {"number": 50, "unit": "mmol"})], "pf": [("mass", {"number": 3.70, "unit": "g"}), ("amount", {"number": 123, "unit": "mmol"})], "cu": [("mass", {"number": 3.62, "unit": "g"}), ("amount", {"number": 25.2, "unit": "mmol"})], "amine": [("mass", {"number": 9.27, "unit": "g"}), ("amount", {"number": 92, "unit": "mmol"})], "solvent": 77, "product_mass": 4.29, "yield": 52},
    "1i": {"pages": [1, 3], "start": [("mass", {"number": 8.85, "unit": "g"}), ("amount", {"number": 44.3, "unit": "mmol"})], "pf": [("mass", {"number": 3.70, "unit": "g"}), ("amount", {"number": 123, "unit": "mmol"})], "cu": [("mass", {"number": 3.62, "unit": "g"}), ("amount", {"number": 25.2, "unit": "mmol"})], "amine": [("volume", {"number": 13, "unit": "mL"}), ("amount", {"number": 92, "unit": "mmol"})], "solvent": 77, "product_mass": 5.87, "yield": 55},
    "1j": {"pages": [1, 3], "start": [("mass", {"number": 5.84, "unit": "g"}), ("amount", {"number": 40, "unit": "mmol"})], "pf": [("mass", {"number": 2.96, "unit": "g"}), ("amount", {"number": 99, "unit": "mmol"})], "cu": [("mass", {"number": 2.89, "unit": "g"}), ("amount", {"number": 20, "unit": "mmol"})], "amine": [("volume", {"number": 10.0, "unit": "mL"}), ("amount", {"number": 76.4, "unit": "mmol"})], "solvent": 62.8, "product_mass": 3.36, "yield": 53},
    "1k": {"pages": [1, 3], "start": [("mass", {"number": 11, "unit": "g"}), ("amount", {"number": 55, "unit": "mmol"})], "pf": [("mass", {"number": 4.44, "unit": "g"}), ("amount", {"number": 148, "unit": "mmol"})], "cu": [("mass", {"number": 4.34, "unit": "g"}), ("amount", {"number": 30, "unit": "mmol"})], "amine": [("mass", {"number": 11.12, "unit": "g"}), ("amount", {"number": 111, "unit": "mmol"})], "solvent": 92.4, "product_mass": 4.50, "yield": 39},
    "1l": {"pages": [1, 3], "start": [("mass", {"number": 3.64, "unit": "g"}), ("amount", {"number": 20, "unit": "mmol"})], "pf": [("mass", {"number": 1.48, "unit": "g"}), ("amount", {"number": 49, "unit": "mmol"})], "cu": [("mass", {"number": 1.45, "unit": "g"}), ("amount", {"number": 10, "unit": "mmol"})], "amine": [("volume", {"number": 5, "unit": "mL"}), ("amount", {"number": 38.2, "unit": "mmol"})], "solvent": 30, "product_mass": 1.99, "yield": 51},
}


records = []
for label, data in synthesis_data.items():
    evidence = uniq(sum((ev(p) for p in data["pages"]), []))
    sid = label[1:]
    parts = [
        participant(f"syn_{sid}_substrate", "reactant", f"1-({subs[label][0]})prop-2-yn-1-ol", evidence, smiles=propargyl_smiles(label), amounts=data["start"]),
        participant(f"syn_{sid}_paraformaldehyde", "reagent", "paraformaldehyde", evidence, smiles=None, amounts=data["pf"]),
        participant(f"syn_{sid}_cubr", "reagent", "copper(I) bromide", evidence, label="CuBr", smiles=None, amounts=data["cu"]),
        participant(f"syn_{sid}_amine", "reagent", "diisopropylamine", evidence, label="i-Pr2NH", smiles="CC(C)NC(C)C", amounts=data["amine"]),
        participant(f"syn_{sid}_dioxane", "solvent", "1,4-dioxane", evidence, smiles="O1CCOCC1", amounts=[("volume", {"number": data["solvent"], "unit": "mL"})]),
        participant(f"syn_{sid}_product", "product", alcohol_name(label), evidence, label=label, smiles=allenol_smiles(label), amounts=[("mass", {"number": data["product_mass"], "unit": "g"})]),
    ]
    temp = {"number": data["temperature"], "unit": "°C"} if "temperature" in data else None
    time = {"number": data["time"], "unit": "h"} if "time" in data else None
    conditions = [field("temperature", temp, evidence), field("time", time, evidence)]
    if label == "1a":
        conditions += [
            field("workup", "cooling; filtration; evaporation; add H2O and ethyl ether; filter; extract with ethyl ether; dry over anhydrous Na2SO4", evidence),
            field("purification", "silica-gel chromatography, petroleum ether/diethyl ether 10:1 (v/v)", evidence),
        ]
    steps = [{"step_id": f"syn_{sid}_step1", "participant_ids": [p["entity_id"] for p in parts if p["role"] != "product"], "conditions": conditions}]
    unresolved = ["No supporting information was explicitly provided or associated.", "Candidate structures are machine-transcribed from legible source structures and remain unverified."]
    if label != "1a":
        unresolved.append("The abbreviated individual procedure does not restate reaction temperature, duration, workup, or purification; these were not inherited from the 1a typical procedure.")
    records.append(record(f"synthesis_{label}", "reported_experiment", evidence, parts, steps, [
        field("reported_yield", {"number": data["yield"], "unit": "%"}, evidence, [f"syn_{sid}_product"]),
        field("yield_measurement_basis", None, evidence, [f"syn_{sid}_product"]),
    ], ["Scheme 1 and the corresponding experimental paragraph describe the same preparation and are merged as one record."], unresolved))


# Prior-work arrow in Eq. (1); it is retained but explicitly not treated as this paper's new experiment.
evidence = ev(1)
parts = [
    participant("lit_eq1_racemate", "reactant", "racemic 1-phenylbuta-2,3-dien-1-ol", evidence, smiles=allenol_smiles("1g")),
    participant("lit_eq1_vinyl_acetate", "reagent", "vinyl acetate", evidence, label="OAc donor", smiles="C=COC(C)=O"),
    participant("lit_eq1_catalyst", "catalyst", "CCL", evidence, label="CCL", smiles=None),
    participant("lit_eq1_alcohol", "product", "enantioenriched 1-phenylbuta-2,3-dien-1-ol", evidence, smiles=allenol_smiles("1g")),
    participant("lit_eq1_acetate", "product", "enantioenriched 1-phenylbuta-2,3-dien-1-ol acetate", evidence, smiles=acetate_smiles("1g")),
]
records.append(record("literature_eq1", "literature_example", evidence, parts, [{
    "step_id": "literature_eq1_step1",
    "participant_ids": ["lit_eq1_racemate", "lit_eq1_vinyl_acetate", "lit_eq1_catalyst"],
    "conditions": [field("temperature", {"number": 30, "unit": "°C"}, evidence), field("time", None, evidence)],
}], [
    field("yield", {"number": 50, "unit": "%"}, evidence, ["lit_eq1_alcohol"]),
    field("enantiomeric_excess", {"number": 21.1, "unit": "%"}, evidence, ["lit_eq1_alcohol"]),
    field("yield", {"number": 14, "unit": "%"}, evidence, ["lit_eq1_acetate"]),
    field("enantiomeric_excess", {"number": 30, "unit": "%"}, evidence, ["lit_eq1_acetate"]),
], ["Equation (1) is introduced as prior work and is not a new experiment of this article."], ["The prose context mentions Novozym-435, whereas the legible Eq. (1) catalyst label reads CCL; the source inconsistency is unresolved.", "Reaction time and experimental quantities are not reported here."]))


# Four distinct enzyme-screening failures described in the prose before Table 1.
for code, enzyme in [("ppl", "PPL"), ("lipase_g", "lipase G"), ("lipolase", "lipolase"), ("novozym_871", "Novozym 871")]:
    evidence = ev(2)
    parts = [
        participant(f"screen_{code}_substrate", "reactant", alcohol_name("1a"), evidence, label="1a", smiles=allenol_smiles("1a")),
        participant(f"screen_{code}_vinyl_acetate", "reagent", "vinyl acetate", evidence, smiles="C=COC(C)=O"),
        participant(f"screen_{code}_enzyme", "catalyst", enzyme, evidence, label=enzyme, smiles=None),
    ]
    records.append(record(f"enzyme_screen_{code}", "optimization_entry", evidence, parts, [{
        "step_id": f"screen_{code}_step1", "participant_ids": [p["entity_id"] for p in parts],
        "conditions": [field("temperature", None, evidence), field("time", None, evidence)],
    }], [field("reaction_result", "no reaction", evidence)], ["The prose reports that the reaction did not occur with this enzyme."], ["Enzyme amount, substrate amount, vinyl acetate amount, temperature, and duration are not stated for the screening attempt.", "No supporting information was explicitly associated."]))


kinetic_data = {
    "1a": {"pages": [2, 3], "time_d": 4, "reactant_mass": 100, "alcohol_mass": 57, "alcohol_yield": 57, "alcohol_ee": 22, "acetate_mass": 27, "acetate_yield": 22, "acetate_ee": 90},
    "1b": {"pages": [2, 4], "time_d": 7, "reactant_mass": 100, "alcohol_mass": 42, "alcohol_yield": 42, "alcohol_ee": 65, "acetate_mass": 30, "acetate_yield": 24, "acetate_ee": 93},
    "1c": {"pages": [2, 4], "time_d": 4, "reactant_mass": 100, "alcohol_mass": 53, "alcohol_yield": 53, "alcohol_ee": 36, "acetate_mass": 30, "acetate_yield": 24, "acetate_ee": 93},
    "1d": {"pages": [2, 4], "time_d": 4, "reactant_mass": 97, "alcohol_mass": 44, "alcohol_yield": 45, "alcohol_ee": 43, "acetate_mass": 52, "acetate_yield": 43, "acetate_ee": 80},
    "1e": {"pages": [2, 4], "time_d": 4, "reactant_mass": 95, "alcohol_mass": 34, "alcohol_yield": 37, "alcohol_ee": 57, "acetate_mass": 51, "acetate_yield": 44, "acetate_ee": 49},
    "1f": {"pages": [2, 4, 5], "time_d": 4, "reactant_mass": 96, "alcohol_mass": 60, "alcohol_yield": 63, "alcohol_ee": 9, "acetate_mass": 17, "acetate_yield": 17, "acetate_ee": 14},
    "1g": {"pages": [2, 5], "time_d": 4, "reactant_mass": 96, "alcohol_mass": 53, "alcohol_yield": 55, "alcohol_ee": 20, "acetate_mass": 25, "acetate_yield": 20, "acetate_ee": 62},
    "1l": {"pages": [2, 5], "time_d": None, "reactant_mass": 96, "alcohol_mass": 52, "alcohol_yield": 54, "alcohol_ee": 33, "acetate_mass": 25, "acetate_yield": 21, "acetate_ee": 93, "scheme_acetate_yield": 22},
}


for label, data in kinetic_data.items():
    evidence = uniq(sum((ev(p) for p in data["pages"]), []))
    sid = label[1:]
    alcohol_id = f"kr_{sid}_alcohol"
    acetate_id = f"kr_{sid}_acetate"
    parts = [
        participant(f"kr_{sid}_substrate", "reactant", f"racemic {alcohol_name(label)}", evidence, label=label, smiles=allenol_smiles(label), amounts=[("mass", {"number": data["reactant_mass"], "unit": "mg"})]),
        participant(f"kr_{sid}_vinyl_acetate", "reagent", "vinyl acetate", evidence, smiles="C=COC(C)=O", amounts=[("volume", {"number": 5, "unit": "mL"})]),
        participant(f"kr_{sid}_ccl", "catalyst", "Candida cylindracea lipase", evidence, label="CCL", smiles=None, amounts=[("mass", {"number": 70, "unit": "mg"})]),
        participant(alcohol_id, "product", f"(S)-{alcohol_name(label)}", evidence, label=f"(S)-{label}", smiles=allenol_smiles(label), amounts=[("mass", {"number": data["alcohol_mass"], "unit": "mg"})]),
        participant(acetate_id, "product", f"(R)-{alcohol_name(label)} acetate", evidence, label=f"(R)-2{sid}", smiles=acetate_smiles(label), amounts=[("mass", {"number": data["acetate_mass"], "unit": "mg"})]),
    ]
    temp = {"number": 30, "unit": "°C"} if label != "1l" else None
    time = {"number": data["time_d"], "unit": "d"} if data["time_d"] is not None else None
    conditions = [field("temperature", temp, evidence), field("time", time, evidence)]
    if label == "1a":
        conditions += [field("operation", "stirred and monitored by TLC; filtration and evaporation", evidence), field("purification", "flash chromatography on silica gel; petroleum ether/ether 40:1 to 10:1", evidence)]
    outcomes = [
        field("isolated_yield", {"number": data["alcohol_yield"], "unit": "%"}, evidence, [alcohol_id]),
        field("enantiomeric_excess", {"number": data["alcohol_ee"], "unit": "%"}, evidence, [alcohol_id]),
        field("isolated_yield", {"number": data["acetate_yield"], "unit": "%"}, evidence, [acetate_id]),
        field("enantiomeric_excess", {"number": data["acetate_ee"], "unit": "%"}, evidence, [acetate_id]),
        field("yield_measurement_basis", "isolated yield based on alcohol", ev(2), [alcohol_id, acetate_id]),
    ]
    unresolved = ["Absolute configurations are tentative in the article.", "No supporting information was explicitly provided or associated.", "Candidate structures are machine-transcribed and remain unverified."]
    notes = ["Table 1 row and the corresponding experimental paragraph are treated as the same kinetic-resolution experiment."]
    if label == "1b":
        unresolved.append("Table 1 footnote generally states HPLC for ee, but the detailed paragraph specifies GC for the residual alcohol 1b; the product-specific methods are retained only in this note.")
    if label == "1l":
        outcomes.append(field("scheme_isolated_yield", {"number": data["scheme_acetate_yield"], "unit": "%"}, ev(2), [acetate_id]))
        unresolved.append("Equation (2) reports 22% acetate yield, while the detailed experimental paragraph reports 21%; both source values are retained.")
        unresolved.append("Temperature and duration are not stated for the 1l kinetic-resolution experiment and were not inherited from Table 1.")
    records.append(record(f"kinetic_resolution_{label}", "substrate_scope_entry", evidence, parts, [{
        "step_id": f"kr_{sid}_step1", "participant_ids": [f"kr_{sid}_substrate", f"kr_{sid}_vinyl_acetate", f"kr_{sid}_ccl"], "conditions": conditions,
    }], outcomes, notes, unresolved))


# Table 1 entries 8-11: each is an independent, explicitly reported no-reaction result.
for label in ["1h", "1i", "1j", "1k"]:
    evidence = ev(2)
    sid = label[1:]
    parts = [
        participant(f"kr_{sid}_substrate", "reactant", f"racemic {alcohol_name(label)}", evidence, label=label, smiles=allenol_smiles(label), amounts=[("mass", {"number": 100, "unit": "mg", "qualifier": "approx", "raw_text": "ca. 100 mg"})]),
        participant(f"kr_{sid}_vinyl_acetate", "reagent", "vinyl acetate", evidence, smiles="C=COC(C)=O", amounts=[("volume", {"number": 5, "unit": "mL"})]),
        participant(f"kr_{sid}_ccl", "catalyst", "Candida cylindracea lipase", evidence, label="CCL", smiles=None, amounts=[("mass", {"number": 70, "unit": "mg"})]),
    ]
    records.append(record(f"kinetic_resolution_{label}", "substrate_scope_entry", evidence, parts, [{
        "step_id": f"kr_{sid}_step1", "participant_ids": [p["entity_id"] for p in parts], "conditions": [field("temperature", {"number": 30, "unit": "°C"}, evidence), field("time", {"number": 4, "unit": "d"}, evidence)],
    }], [field("reaction_result", "no reaction", evidence)], ["Table 1 footnote d states that no reaction was observed."], ["No product yield or ee applies because no reaction was observed.", "No supporting information was explicitly provided or associated."]))


assert len(records) == 29
OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
print(f"wrote {len(records)} records to {OUT}")
