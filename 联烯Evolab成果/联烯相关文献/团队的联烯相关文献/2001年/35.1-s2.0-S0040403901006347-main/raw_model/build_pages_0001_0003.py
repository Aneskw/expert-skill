#!/usr/bin/env python3
"""Build source-linked records for doc_1132074d14c1193b, PDF pages 1-3."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[3]
DOC = "doc_1132074d14c1193b"
OUT = ROOT / "runs/current/raw_model/records_pages_0001_0003.json"
COVERAGE = ROOT / "runs/current/coverage/pages_0001_0003.json"
TASKS = ROOT / "runs/current/tasks.json"


def ev(page):
    return [f"{DOC}:page{page}:text", f"{DOC}:page{page}:image"]


def fact(value, evidence):
    return {
        "value": value,
        "evidence_ids": list(evidence) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def field(name, value, evidence):
    return {"name": name, "fact": fact(value, evidence)}


def participant(entity_id, role, label, name, evidence, amounts=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence),
        "smiles": fact(None, []),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": amounts or [],
    }


def record(suffix, kind, evidence, participants, conditions, outcomes, notes, unresolved):
    return {
        "record_id": f"{DOC}:{suffix}",
        "document_id": DOC,
        "source_reaction_id": suffix,
        "record_kind": kind,
        "status": "needs_review",
        "completeness": "partial",
        "evidence_ids": list(dict.fromkeys(evidence)),
        "participants": participants,
        "steps": [{
            "step_id": "step1",
            "participant_ids": [p["entity_id"] for p in participants],
            "conditions": conditions,
        }],
        "outcomes": outcomes,
        "notes": [fact(n, evidence) for n in notes],
        "review": {
            "method": "model",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved,
        },
    }


records = []

# Scheme 1: prior chemistry, hydrolysis problem, and the proposed direct ester route.
e1 = ev(1)
records.append(record(
    "scheme1_prior_allenoic_acid_halolactonization", "literature_example", e1,
    [
        participant("acid", "reactant", "2,3-allenoic acid", "generic 2,3-allenoic acid (R1/R2)", e1),
        participant("cux2", "reagent", "CuX2", "copper(II) halide; X = Cl or Br", e1),
        participant("acetone_water", "solvent", "acetone-H2O", "acetone/water", e1),
        participant("halolactone", "product", "beta-halobutenolide", "generic beta-halobutenolide", e1),
    ],
    [field("temperature", "65-70 °C", e1), field("time", None, []), field("solvent_ratio", None, [])],
    [field("yield", None, []), field("halogen", "X = Cl or Br", e1)],
    ["Scheme 1 and the text attribute this allenoic-acid halolactonization to the authors' earlier work (reference 8)."],
    ["Generic R1/R2 structures are not resolved.", "Reaction time, scale, CuX2 amount, solvent ratio, workup, purification, and yield are not reported here."],
))
records.append(record(
    "scheme1_generic_ester_hydrolysis_problem", "literature_example", e1,
    [
        participant("ester", "reactant", "2,3-allenoate", "generic 2,3-allenoate", e1),
        participant("hydroxide", "reagent", "1. OH-; 2. H+", "base hydrolysis followed by acidification", e1),
        participant("acid", "product", "2,3-allenoic acid", "generic 2,3-allenoic acid", e1),
        participant("alkynoic_acid", "product", "3-alkynoic acid", "generic 3-alkynoic acid byproduct", e1),
    ],
    [field("temperature", None, []), field("time", None, [])],
    [field("yield", None, []), field("byproduct_observed", True, e1)],
    ["The prose states that ester hydrolysis sometimes gave low yields and often formed 3-alkynoic acids, sometimes as the sole products."],
    ["Generic R/R1/R2 structures, quantities, solvent, temperature, time, product ratio, workup, purification, and yield are missing."],
))
records.append(record(
    "scheme1_direct_allenoate_halolactonization_target", "general_scheme", e1,
    [
        participant("ester", "reactant", "2,3-allenoate", "generic 2,3-allenoate", e1),
        participant("halolactone", "product", "beta-halobutenolide", "generic beta-halobutenolide", e1),
    ],
    [field("conditions", None, [])],
    [field("yield", None, [])],
    ["The upward arrow in Scheme 1 carries a question mark and represents the desired direct ester-to-lactone transformation, not an observed run."],
    ["Reagent, conditions, substituent identities, and outcome are intentionally unspecified in this conceptual arrow."],
))

# Scheme 2 screening. Page 1 prose and page 2 drawing/rows are the same experiments.
e12 = ev(1) + ev(2)


def scheme2_record(suffix, reagent, solvent, ratio, temperature, time, recovery, y2a, y3a, isolated=False):
    parts = [
        participant("1a", "reactant", "1a", "ethyl 2-methyl-2,3-decadienoate", e12),
        participant("halogenating_reagent", "reagent", reagent, reagent, e12),
        participant("solvent", "solvent", solvent, solvent, e12),
        participant("2a", "product", "2a", "beta-bromobutenolide 2a", e12),
        participant("3a", "product", "3a", "ethyl 3-bromo-4-oxo-2-decenoate", e12),
    ]
    return record(
        suffix, "optimization_entry", e12, parts,
        [field("temperature", temperature, e12), field("time", time, e12), field("solvent_ratio", ratio, ev(1)), field("reagent_amount", None, [])],
        [field("recovery_of_1a", {"number": recovery, "unit": "%"}, ev(2)),
         field("yield_2a", {"number": y2a, "unit": "%"}, ev(2)),
         field("yield_3a", {"number": y3a, "unit": "%"}, ev(2)),
         field("yield_2a_measurement_basis", "isolated" if isolated else None, ev(1) if isolated else [])],
        ["Scheme 2 condition row; 3a is the competing brominated oxo-enoate product."],
        ["Reaction scale, reagent amount, atmosphere, concentration, workup, and purification are missing.", "Yield basis is unreported except where the prose explicitly calls 2a isolated."],
    )


records.append(scheme2_record("scheme2_acetone_water", "CuBr2", "acetone/H2O", "2:1", "65-70 °C", {"number": 12, "unit": "h"}, 27, 62, 0))
records.append(scheme2_record("scheme2_ethanol_water", "CuBr2", "ethanol/H2O", "3:2", "80-85 °C", {"number": 12, "unit": "h"}, 0, 86, 0, isolated=True))
records.append(scheme2_record("scheme2_nbs_water", "NBS", "H2O", None, "room temperature", {"number": 14, "unit": "h"}, 0, 53, 15))

# Table 1: one record per row, with only the table's common footnote/header applied.
table_rows = [
    (1, "n-C6H13", "H", "n-C3H7", "1b", "2b", 95),
    (2, "n-C6H13", "H", "C6H5CH2", "1c", "2c", 97),
    (3, "n-C3H7", "H", "C6H5CH2", "1d", "2d", 78),
    (4, "n-C3H7", "H", "n-C3H7", "1e", "2e", 68),
    (5, "n-C3H7", "H", "CH3", "1f", "2f", 86),
    (6, "CH3", "H", "CH3", "1g", "2g", 72),
    (7, "CH3", "H", "n-C3H7", "1h", "2h", 84),
    (8, "CH3", "CH3", "CH3", "1i", "2i", 68),
    (9, "CH3", "CH3", "n-C3H7", "1j", "2j", 66),
    (10, "n-C3H7", "H", "Allyl", "1k", "2k", 54),
]
e2 = ev(2)
for entry, r1, r2, r3, substrate, product, yld in table_rows:
    parts = [
        participant("substrate", "reactant", substrate, f"ethyl 2,3-allenoate {substrate} (R1={r1}; R2={r2}; R3={r3})", e2,
                    [field("amount", {"number": 0.5, "unit": "mmol"}, e2)]),
        participant("cubr2", "reagent", "CuBr2", "copper(II) bromide", e2,
                    [field("amount", {"number": 4, "unit": "equiv"}, e2)]),
        participant("ethanol_water", "solvent", "ethanol:H2O", "ethanol/water", e2,
                    [field("volume", {"number": 4, "unit": "mL"}, e2), field("ratio", "3:2", e2)]),
        participant("product", "product", product, f"beta-bromobutenolide {product}", e2),
    ]
    extra = [field("yield", {"number": yld, "unit": "%"}, e2), field("yield_measurement_basis", None, [])]
    notes = ["Table 1 entry %d; the prose states that the starting allenoates reacted completely and the reactions proceeded smoothly and cleanly." % entry]
    if entry == 10:
        extra.append(field("dibromination_of_allylic_C_C_bond_observed", False, e2))
        notes.append("For allyl-bearing 1k, the prose explicitly states that dibromination of the allylic C=C bond was not observed.")
    records.append(record(
        f"table1_entry{entry}", "substrate_scope_entry", e2, parts,
        [field("temperature", "80-85 °C", e2), field("time", {"number": 12, "unit": "h"}, e2), field("atmosphere", None, []), field("concentration", None, [])],
        extra, notes,
        ["Exact structures and stereochemistry are not machine-verified.", "Atmosphere, concentration, workup, purification, isolated mass, and yield measurement basis are not reported."],
    ))

# Prior molecular-bromine comparison mentioned in the Table 1 discussion.
records.append(record(
    "prior_br2_bromolactonization_1i", "literature_example", e2,
    [
        participant("1i", "reactant", "1i", "ethyl 2,4-dimethyl-2,3-pentadienoate", e2),
        participant("br2", "reagent", "Br2", "molecular bromine", e2),
        participant("2i", "product", "2i", "beta-bromobutenolide 2i", e2),
    ],
    [field("temperature", None, []), field("time", None, []), field("solvent", None, [])],
    [field("yield", {"number": 58, "unit": "%"}, e2), field("yield_measurement_basis", None, [])],
    ["The text explicitly attributes this 58% molecular-bromine result to prior reference 13."],
    ["Scale, Br2 amount, solvent, temperature, time, workup, purification, and yield basis are absent from this paper."],
))

# Scheme 3: three aryl-allenoate runs. Page 2 prose and page 3 scheme are linked.
e23 = ev(2) + ev(3)
scheme3_rows = [
    ("scheme3_1l_ethyl_ester", "1l", "H", "C2H5", "2l", 40, True),
    ("scheme3_1l_benzyl_ester", "1l'", "H", "CH2C6H5", "2l", 67, False),
    ("scheme3_1m_benzyl_ester", "1m'", "C2H5", "CH2C6H5", "2m", 66, False),
]
for suffix, substrate, r1, ester_r, product, yld, unidentified in scheme3_rows:
    parts = [
        participant("substrate", "reactant", substrate, f"4-phenyl-2-methyl-2,3-allenoate {substrate} (R1={r1}; ester R={ester_r})", e23),
        participant("cubr2", "reagent", "CuBr2", "copper(II) bromide", e23),
        participant("ethanol_water", "solvent", "ethanol-H2O", "ethanol/water", e23),
        participant("product", "product", product, f"beta-bromobutenolide {product}", e23),
    ]
    outcomes = [field("yield", {"number": yld, "unit": "%"}, e23), field("yield_measurement_basis", None, [])]
    if unidentified:
        parts.append(participant("unidentified_product", "product", "unidentified product", "unidentified coproduct", e23))
        outcomes.append(field("unidentified_product_observed", True, e23))
    records.append(record(
        suffix, "substrate_scope_entry", e23, parts,
        [field("temperature", "80-85 °C", e23), field("time", None, []), field("solvent_ratio", None, []), field("CuBr2_amount", None, [])],
        outcomes,
        ["Scheme 3 aryl-allenoate bromolactonization; only the first row explicitly shows an unidentified coproduct."],
        ["Exact structures are not machine-verified.", "Scale, CuBr2 amount, solvent ratio/volume, time, atmosphere, concentration, workup, purification, isolated mass, and yield basis are not reported in the supplied main text."],
    ))

# Specific hydrolysis example printed in reference note 10 on page 3.
e13 = ev(1) + ev(3)
records.append(record(
    "ref10_1a_naoh_hydrolysis", "literature_example", e13,
    [
        participant("1a", "reactant", "1a", "ethyl 2-methyl-2,3-decadienoate", e13),
        participant("naoh", "reagent", "NaOH", "sodium hydroxide", ev(3)),
        participant("allenoic_acid", "product", "2-methyl-2,3-decadienoic acid", "2-methyl-2,3-decadienoic acid", ev(3)),
        participant("alkynoic_acid", "product", "2-methyl-3-decynoic acid", "2-methyl-3-decynoic acid", ev(3)),
    ],
    [field("temperature", None, []), field("time", None, []), field("solvent", None, [])],
    [field("product_mixture_observed", True, ev(3)), field("yield", None, [])],
    ["Reference note 10 states that the two acids formed a mixture that could not be thoroughly separated by silica-gel chromatography."],
    ["Whether this example was newly performed for this article or belongs to prior unpublished/contextual work is not explicit.", "Scale, NaOH amount, solvent, temperature, time, workup, product ratio, and yields are missing."],
))

assert len(records) == 21
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")

ids = {r["source_reaction_id"]: r["record_id"] for r in records}
coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1,
            "state": "attempted",
            "regions": [
                {"region": "title, abstract, and introductory prose", "finding": "Current paper scope and prior-work context; no additional row-level experiment beyond the linked schemes/prose.", "evidence_ids": ev(1)},
                {"region": "Scheme 1 and adjacent lower-page prose", "finding": "Prior allenoic-acid halolactonization, generic ester-hydrolysis problem, and question-mark direct-ester target were classified separately.", "evidence_ids": ev(1)},
                {"region": "right-column screening prose", "finding": "Three Scheme 2 condition rows are described across pages 1-2; 86% 2a is explicitly isolated, other yield bases are unstated.", "evidence_ids": ev(1)},
            ],
            "record_ids": [
                ids["scheme1_prior_allenoic_acid_halolactonization"], ids["scheme1_generic_ester_hydrolysis_problem"],
                ids["scheme1_direct_allenoate_halolactonization_target"], ids["scheme2_acetone_water"],
                ids["scheme2_ethanol_water"], ids["scheme2_nbs_water"], ids["ref10_1a_naoh_hydrolysis"],
            ],
            "unresolved": ["Scheme 1 generic structures and most prior-work quantities are absent.", "No SI is supplied or associated."],
        },
        {
            "page": 2,
            "state": "attempted",
            "regions": [
                {"region": "Scheme 2", "finding": "Three distinct optimization/comparison rows with separate recovery and product outcomes.", "evidence_ids": ev(2)},
                {"region": "Table 1 header, ten rows, and footnote", "finding": "Ten independent substrate-scope entries; the common 0.5 mmol/4 equiv/4 mL 3:2 ethanol-water and 80-85 °C/12 h conditions were applied row by row.", "evidence_ids": ev(2)},
                {"region": "Table 1 discussion and right-column aryl-allenoate prose", "finding": "Prior Br2/1i literature result separated from current Scheme 3 experiments; three Scheme 3 rows identified.", "evidence_ids": ev(2)},
            ],
            "record_ids": [ids["scheme2_acetone_water"], ids["scheme2_ethanol_water"], ids["scheme2_nbs_water"]]
                + [ids[f"table1_entry{i}"] for i in range(1, 11)]
                + [ids["prior_br2_bromolactonization_1i"]]
                + [ids[x[0]] for x in scheme3_rows],
            "unresolved": ["Table 1 yield basis, atmosphere, concentration, workup, purification, and isolated masses are not reported.", "Scheme 3 time, scale, CuBr2 amount, solvent ratio, and yield basis are missing."],
        },
        {
            "page": 3,
            "state": "attempted",
            "regions": [
                {"region": "Scheme 3", "finding": "Three current-paper aryl-allenoate bromolactonizations; the ethyl ester row alone explicitly gives an unidentified coproduct.", "evidence_ids": ev(3)},
                {"region": "conclusion and acknowledgments", "finding": "No additional individual experiment or mechanism.", "evidence_ids": ev(3)},
                {"region": "references, especially note 10", "finding": "Most content is bibliography; note 10 gives a specific 1a/NaOH hydrolysis mixture and was retained as contextual prior/example chemistry.", "evidence_ids": ev(3)},
            ],
            "record_ids": [ids[x[0]] for x in scheme3_rows] + [ids["ref10_1a_naoh_hydrolysis"]],
            "unresolved": ["The provenance status of the note-10 'in our case' hydrolysis relative to the current article is not explicit.", "No SI is supplied or associated."],
        },
    ],
}
COVERAGE.parent.mkdir(parents=True, exist_ok=True)
COVERAGE.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

tasks = json.loads(TASKS.read_text())
for task in tasks:
    page = int(task["evidence_id"].split(":page", 1)[1].split(":", 1)[0])
    if page in (1, 2, 3):
        task["state"] = "attempted"
        task["visual_evidence_id"] = f"{DOC}:page{page}:image"
TASKS.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"records": len(records), "coverage_pages": [1, 2, 3]}, ensure_ascii=False))
