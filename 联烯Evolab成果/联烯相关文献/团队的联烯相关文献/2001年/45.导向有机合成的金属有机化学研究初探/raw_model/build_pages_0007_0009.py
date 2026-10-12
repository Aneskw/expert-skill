#!/usr/bin/env python3
"""Build evidence-linked machine records for source PDF pages 7-9."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / "runs/current"
DOC = "doc_5f6aebaf6cda0211"


def ev(page):
    return [f"{DOC}:page{page}:image", f"{DOC}:page{page}:text"]


def uniq(values):
    return list(dict.fromkeys(values))


def fact(value, evidence):
    return {
        "value": value,
        "evidence_ids": uniq(evidence),
        "verification": "missing" if value is None else "unreviewed",
    }


def qty(number, unit, **extra):
    value = {"number": number, "unit": unit}
    value.update(extra)
    return value


def field(name, value, evidence, targets=()):
    result = {"name": name, "fact": fact(value, evidence)}
    if targets:
        result["target_entity_ids"] = list(targets)
    return result


def participant(suffix, index, role, label, evidence, smiles=None, amounts=()):
    entity_id = f"{suffix}_{role}_{index}"
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(label, evidence),
        "smiles": fact(smiles, evidence) if smiles else fact(None, evidence),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": [field(name, value, evidence) for name, value in amounts],
    }


def condition_participants(suffix, condition, evidence):
    """Instantiate Table 1 footnote conditions as structured participants."""
    rows = []
    if condition == "A":
        rows = [
            ("catalyst", "Pd(PPh3)4", None, (("loading", qty(10, "mol%")),)),
            ("reagent", "K2CO3", "O=C([O-])[O-].[K+].[K+]", (("equivalents", qty(10, "equiv")),)),
            ("reagent", "n-Bu4NCl", "CCCC[N+](CCCC)(CCCC)CCCC.[Cl-]", (("equivalents", qty(2, "equiv")),)),
            ("solvent", "xylene", None, ()),
        ]
    elif condition == "A_c":
        rows = [
            ("catalyst", "Pd(PPh3)4", None, (("loading", qty(10, "mol%")),)),
            ("reagent", "Ag2CO3", None, (("equivalents", qty(2.5, "equiv")),)),
            ("reagent", "n-Bu4NCl", "CCCC[N+](CCCC)(CCCC)CCCC.[Cl-]", (("equivalents", qty(2, "equiv")),)),
            ("solvent", "xylene", None, ()),
        ]
    elif condition in ("B", "B_b"):
        halide = "n-Bu4NBr" if condition == "B_b" else "n-Bu4NCl"
        halide_smiles = "CCCC[N+](CCCC)(CCCC)CCCC.[Br-]" if condition == "B_b" else "CCCC[N+](CCCC)(CCCC)CCCC.[Cl-]"
        rows = [
            ("catalyst", "Pd(PPh3)4", None, (("loading", qty(10, "mol%")),)),
            ("reagent", "K2CO3", "O=C([O-])[O-].[K+].[K+]", (("equivalents", qty(5, "equiv")),)),
            ("reagent", halide, halide_smiles, (("equivalents", qty(1, "equiv")),)),
            ("solvent", "xylene", None, ()),
        ]
    elif condition == "C":
        rows = [
            ("catalyst", "Pd(PPh3)4", None, (("loading", qty(5, "mol%")),)),
            ("reagent", "K2CO3", "O=C([O-])[O-].[K+].[K+]", (("equivalents", qty(5, "equiv")),)),
            ("reagent", "n-Bu4NCl", "CCCC[N+](CCCC)(CCCC)CCCC.[Cl-]", (("equivalents", qty(1, "equiv")),)),
            ("solvent", "xylene", None, ()),
        ]
    return [participant(suffix, i + 3, role, label, evidence, smiles, amounts)
            for i, (role, label, smiles, amounts) in enumerate(rows)]


def table_record(entry, page, condition, temperature, time_h, yield_pct,
                 substrate_detail="", product_detail="", extra_outcomes=(), explicit=None):
    suffix = f"table1_entry{entry}"
    row_evidence = ev(page)
    footnote_evidence = ev(8)
    all_evidence = uniq(row_evidence + footnote_evidence)
    substrate_label = f"Table 1 entry {entry} drawn tethered 1,1-dibromoalkene substrate (E = CO2Me{substrate_detail})"
    product_label = f"Table 1 entry {entry} drawn bicyclic product{product_detail}"
    parts = [
        participant(suffix, 1, "reactant", substrate_label, row_evidence),
        participant(suffix, 2, "product", product_label, row_evidence),
    ]
    if explicit is None:
        parts += condition_participants(suffix, condition, footnote_evidence)
    else:
        parts += [participant(suffix, i + 3, role, label, row_evidence, smiles, amounts)
                  for i, (role, label, smiles, amounts) in enumerate(explicit)]
    product_id = parts[1]["entity_id"]
    conditions = [
        field("table_condition_code", condition if explicit is None else "explicit", row_evidence),
        field("temperature", qty(temperature, "°C") if temperature is not None else None, row_evidence),
        field("time", qty(time_h, "h"), row_evidence),
    ]
    outcomes = [
        field("yield", qty(yield_pct, "%"), row_evidence, (product_id,)),
        field("yield_measurement_basis", None, row_evidence),
    ]
    outcomes += [field(name, value, row_evidence, (product_id,)) for name, value in extra_outcomes]
    unresolved = [
        "The account does not state the yield measurement basis for this Table 1 row.",
        "Reaction scale, atmosphere, concentration, workup, purification, and isolated mass are not reported in the table.",
        "The complex drawn substrate and product structures have no compound numbers; candidate SMILES remain null pending structure review.",
    ]
    if temperature is None:
        unresolved.append("Temperature is not printed for this row's explicit condition set.")
    return {
        "record_id": f"{DOC}:{suffix}",
        "document_id": DOC,
        "source_reaction_id": suffix,
        "record_kind": "literature_example",
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": all_evidence,
        "participants": parts,
        "steps": [{
            "step_id": f"{suffix}_step1",
            "participant_ids": [p["entity_id"] for p in parts],
            "conditions": conditions,
        }],
        "outcomes": outcomes,
        "notes": [fact(
            "Individual row of Table 1, 'Synthesis of bicycles via bicarbopalladation'; E is defined as CO2Me. The article is an account summarizing cited earlier work.",
            all_evidence,
        )],
        "review": {"method": "none", "reviewer": None, "checked_fields": [], "unresolved": unresolved},
    }


explicit_entry2 = [
    ("catalyst", "Pd2(dba)3-CHCl3", None, (("loading", qty(5, "mol%")),)),
    ("reagent", "K2CO3", "O=C([O-])[O-].[K+].[K+]", (("equivalents", qty(5, "equiv")),)),
    ("reagent", "dppe", None, (("loading", qty(20, "mol%")),)),
    ("solvent", "DMF", "CN(C)C=O", ()),
]
explicit_entry7 = [
    ("catalyst", "Pd2(dba)3-CHCl3", None, (("loading", qty(5, "mol%")),)),
    ("reagent", "PPh3", "c1ccc(P(c2ccccc2)c2ccccc2)cc1", (("loading", qty(20, "mol%")),)),
    ("reagent", "Ag2CO3", None, (("equivalents", qty(3, "equiv")),)),
    ("solvent", "xylene", None, ()),
]

records = [
    table_record(1, 7, "A", 85, 15.5, 83, "; symmetric dioxa tether"),
    table_record(2, 7, "explicit", None, 11, 63, "; unsymmetrical O/C(E)2 tether", explicit=explicit_entry2),
    table_record(3, 7, "B", 85, 24, 37, "; X = O and one phenyl-substituted alkenyl tether"),
    table_record(4, 7, "B", 90, 22, 46, "; X = C(E)2 and one phenyl-substituted alkenyl tether"),
    table_record(5, 7, "B", 85, 22.5, 39, "; symmetric phenyl-substituted carbon tether"),
    table_record(6, 7, "C", 85, 23.5, 19, "; symmetric phenyl-substituted dioxa tether"),
    table_record(7, 7, "explicit", 90, 14, 94, "; ester-substituted side chains", explicit=explicit_entry7),
    table_record(8, 7, "C", 85, 20, 55, "; methyl-substituted dioxa tether", extra_outcomes=(("diastereomer_ratio", "1:1",),)),
    table_record(9, 7, "C", 85, 21, 55, "; S,S-configured dioxa tether", product_detail=" annotated S,S"),
    table_record(10, 7, "B_b", 85, 26, 67, "; unsymmetrical dioxa/C(E)2 tether"),
    table_record(11, 7, "B_b", 85, 14.5, 67, "; S-configured dioxa/C(E)2 tether", product_detail=" with an S stereochemical annotation"),
    table_record(12, 7, "C", 85, 13.5, 33, "; carbocyclic/C(E)2 tether"),
    table_record(13, 8, "A", 85, 23, 60, "; extended carbocyclic/C(E)2 tether", product_detail=" retaining one bromide"),
    table_record(14, 8, "A", 83, 15, 57, "; X = O extended tether", product_detail=" shown as a fused 7/6 bicycle"),
    table_record(15, 8, "A", 85, 11, 56, "; X = C(E)2 extended tether", product_detail=" shown as a fused 7/6 bicycle"),
    table_record(16, 8, "A_c", 80, 5, 38, "; symmetric extended tether", product_detail=" shown as a fused 7/7 bicycle"),
]


def mechanism_record():
    suffix = "scheme14_bicarbopalladation_cycle"
    evidence = ev(8)
    parts = [
        participant(suffix, 1, "reactant", "generic tethered 1,1-dibromoalkene (m,n variables)", evidence),
        participant(suffix, 2, "product", "generic fused bicyclic diene", evidence),
        participant(suffix, 3, "catalyst", "Pd(0)", evidence),
        participant(suffix, 4, "unspecified_agent", "base", evidence),
        participant(suffix, 5, "unspecified_agent", "depicted organopalladium intermediates in Scheme 14", evidence),
    ]
    return {
        "record_id": f"{DOC}:{suffix}",
        "document_id": DOC,
        "source_reaction_id": suffix,
        "record_kind": "mechanism",
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": evidence,
        "participants": parts,
        "steps": [{
            "step_id": f"{suffix}_step1",
            "participant_ids": [p["entity_id"] for p in parts],
            "conditions": [field("temperature", None, evidence), field("time", None, evidence)],
        }],
        "outcomes": [field("yield", None, evidence, (parts[1]["entity_id"],)), field("yield_measurement_basis", None, evidence)],
        "notes": [fact(
            "Scheme 14 is a proposed catalytic cycle featuring Pd(0), successive organopalladium intermediates, base/HBr handling, and formation of the fused bicyclic product; the intermediates are not presented as isolated observations.",
            evidence,
        )],
        "review": {
            "method": "none", "reviewer": None, "checked_fields": [],
            "unresolved": [
                "Scheme 14 is mechanistic and generic; m, n, ligand identity Lx, base identity, and operating conditions are not specified.",
                "The depicted organopalladium intermediates are proposed rather than independently observed or isolated.",
            ],
        },
    }


records.append(mechanism_record())

entry_ids = {i: f"{DOC}:table1_entry{i}" for i in range(1, 17)}
coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 7,
            "state": "attempted",
            "regions": [{
                "region": "full-page Table 1 rows 1-12 (title, structures, condition column, times, products, yields)",
                "finding": "Twelve distinct cited bicarbopalladation examples were read row by row; shared A/B/C definitions continue on page 8.",
                "evidence_ids": [f"{DOC}:page7:image", f"{DOC}:page7:text", f"{DOC}:page8:image"],
            }],
            "record_ids": [entry_ids[i] for i in range(1, 13)],
            "unresolved": [
                "Complex unnumbered structures require later structure review; yield bases, scales, atmospheres, workups, purifications, and isolated masses are not printed.",
                "Entry 2 has no printed temperature.",
            ],
        },
        {
            "page": 8,
            "state": "attempted",
            "regions": [
                {
                    "region": "top continuation of Table 1, rows 13-16 and footnotes a-c",
                    "finding": "Four additional cited bicarbopalladation rows plus A/B/C condition definitions and b/c reagent substitutions; footnote reagents and amounts were structured on every affected row.",
                    "evidence_ids": [f"{DOC}:page8:image", f"{DOC}:page8:text"],
                },
                {
                    "region": "middle Scheme 14 catalytic-cycle drawing",
                    "finding": "Generic proposed Pd(0) bicarbopalladation cycle; represented as a mechanism, not an observed experiment.",
                    "evidence_ids": [f"{DOC}:page8:image"],
                },
                {
                    "region": "bottom acknowledgments and beginning of references",
                    "finding": "Acknowledgments and references 1-3 only; no additional reaction record.",
                    "evidence_ids": [f"{DOC}:page8:image", f"{DOC}:page8:text"],
                },
            ],
            "record_ids": [entry_ids[i] for i in range(1, 17)] + [f"{DOC}:scheme14_bicarbopalladation_cycle"],
            "unresolved": [
                "Scheme 14 ligand/base identities and all operating details are unspecified; intermediates are proposed.",
                "Table 1 yield measurement bases are not stated.",
            ],
        },
        {
            "page": 9,
            "state": "attempted",
            "regions": [{
                "region": "two-column references 4-30 and article footer",
                "finding": "Bibliography only; no reaction arrow, table row, experimental procedure, or new mechanistic figure.",
                "evidence_ids": [f"{DOC}:page9:image", f"{DOC}:page9:text"],
            }],
            "record_ids": [],
            "unresolved": ["Bibliographic entries were not imported as experiments and no cited external papers were supplied for procedure-level extraction."],
        },
    ],
}


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


write(RUN / "raw_model/records_pages_0007_0009.json", records)
write(RUN / "coverage/pages_0007_0009.json", coverage)

tasks_path = RUN / "tasks.json"
tasks = json.loads(tasks_path.read_text())
for task in tasks:
    page = int(task["evidence_id"].split(":page", 1)[1].split(":", 1)[0])
    if 7 <= page <= 9:
        task["state"] = "attempted"
        task["visual_evidence_id"] = f"{DOC}:page{page}:image"
        task["reason"] = "Original page image visually inspected; records and coverage ledger generated for pages 7-9."
write(tasks_path, tasks)

print(json.dumps({
    "records": len(records),
    "by_kind": {kind: sum(r["record_kind"] == kind for r in records)
                for kind in sorted({r["record_kind"] for r in records})},
    "pages": [p["page"] for p in coverage["pages"]],
}, ensure_ascii=False))
