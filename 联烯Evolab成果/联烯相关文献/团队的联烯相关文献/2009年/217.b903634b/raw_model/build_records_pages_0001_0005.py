#!/usr/bin/env python3
"""Build source-linked machine records for 217.b903634b.pdf, PDF pages 1-5."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "runs/current"
DOC = "doc_0fd29b6e9ef4e881"


def ev(page: int) -> list[str]:
    return [f"{DOC}:page{page}:image", f"{DOC}:page{page}:text"]


def fact(value, evidence=()):
    return {
        "value": value,
        "evidence_ids": list(evidence),
        "verification": "missing" if value is None else "unreviewed",
    }


def field(name, value, evidence, targets=()):
    item = {"name": name, "fact": fact(value, evidence)}
    if targets:
        item["target_entity_ids"] = list(targets)
    return item


def participant(entity_id, role, label, evidence, *, name=None, smiles=None, amounts=()):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence if name is not None else ()),
        "smiles": fact(smiles, evidence if smiles is not None else ()),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": list(amounts),
    }


def q(number, unit, **extra):
    return {"number": number, "unit": unit, **extra}


def base_record(suffix, kind, evidence, participants, steps, outcomes, *, notes=(), unresolved=()):
    return {
        "record_id": f"{DOC}:{suffix}",
        "document_id": DOC,
        "source_reaction_id": suffix,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": list(dict.fromkeys(evidence)),
        "participants": participants,
        "steps": steps,
        "outcomes": outcomes,
        "notes": [fact(x, evidence) for x in notes],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": list(unresolved),
        },
    }


def common_participants(evidence, substrate_label, substrate_name, aryl_label, aryl_name, aryl_smiles, product_specs):
    people = [
        participant(
            "substrate",
            "reactant",
            substrate_label,
            evidence,
            name=substrate_name,
            amounts=[field("equivalents", q(1.0, "equiv"), evidence)],
        ),
        participant(
            "aryl_iodide",
            "reactant",
            aryl_label,
            evidence,
            name=aryl_name,
            smiles=aryl_smiles,
            amounts=[field("equivalents", q(1.2, "equiv"), evidence)],
        ),
        participant(
            "pd_pph3_4",
            "catalyst",
            "Pd(PPh3)4",
            evidence,
            name="tetrakis(triphenylphosphine)palladium(0)",
            amounts=[field("catalyst_loading", q(5, "mol%"), evidence)],
        ),
        participant(
            "cs2co3",
            "reagent",
            "Cs2CO3",
            evidence,
            name="cesium carbonate",
            smiles="[Cs+].[Cs+].[O-]C([O-])=O",
            amounts=[field("equivalents", q(1.1, "equiv"), evidence)],
        ),
        participant(
            "mecn",
            "solvent",
            "MeCN",
            evidence,
            name="acetonitrile",
            smiles="CC#N",
        ),
    ]
    for entity_id, label, name in product_specs:
        people.append(participant(entity_id, "product", label, evidence, name=name))
    return people


def reaction_step(evidence, participant_ids, time_h):
    return [{
        "step_id": "coupling_cyclization",
        "participant_ids": participant_ids,
        "conditions": [
            field("temperature", q(80, "°C"), evidence),
            field("time", q(time_h, "h"), evidence),
            field("solvent", "MeCN", evidence),
            field("atmosphere", None, ()),
            field("workup", None, ()),
            field("purification", None, ()),
        ],
    }]


records = []

# Scheme 1: two experiments, each producing a four- and a five-membered product.
scheme1 = [
    ("scheme1_entry_br", "p-BrC6H4I", "1-bromo-4-iodobenzene", "Brc1ccc(I)cc1", 2, "2a", 44, "3a", 36),
    ("scheme1_entry_cn", "p-NCC6H4I", "4-iodobenzonitrile", "N#Cc1ccc(I)cc1", 3, "2b", 16, "3b", 59),
]
for suffix, aryl_label, aryl_name, aryl_smiles, time_h, p4, y4, p5, y5 in scheme1:
    evidence = ev(3)
    products = [
        ("diazetidine", p4, f"trans-1,2-diazetidine {p4}"),
        ("pyrazole", p5, f"2,3-dihydro-1H-pyrazole {p5}"),
    ]
    parts = common_participants(
        evidence,
        "1",
        "2,4-nonsubstituted 2,3-allenyl hydrazine 1",
        aryl_label,
        aryl_name,
        aryl_smiles,
        products,
    )
    records.append(base_record(
        suffix,
        "reported_experiment",
        evidence,
        parts,
        reaction_step(evidence, [p["entity_id"] for p in parts], time_h),
        [
            field("reported_yield", q(y4, "%"), evidence, ["diazetidine"]),
            field("reported_yield", q(y5, "%"), evidence, ["pyrazole"]),
            field("yield_measurement_basis", None, ()),
        ],
        notes=["Scheme 1 reports a mixture of four-membered and five-membered products under Conditions A."],
        unresolved=[
            "The yield measurement basis is not stated on the covered pages.",
            "Complex substrate and product structures are retained by source labels; candidate SMILES are not asserted.",
            "Atmosphere, workup, and purification are not reported in the covered main text.",
        ],
    ))

# Scheme 2: page-3 prose and page-4 arrow describe one experiment.
evidence = ev(3) + ev(4)
parts = common_participants(
    evidence,
    "4a",
    "4-nonsubstituted 2-substituted 2,3-allenyl hydrazine 4a (R1=n-C6H13, R2=Me, R3=Et)",
    "p-O2NC6H4I",
    "1-iodo-4-nitrobenzene",
    "O=[N+]([O-])c1ccc(I)cc1",
    [
        ("product_5a", "5a", "2,3-dihydro-1H-pyrazole 5a"),
        ("product_2c", "2c", "trans-1,2-diazetidine 2c"),
    ],
)
records.append(base_record(
    "scheme2_4a_p_nitro",
    "reported_experiment",
    evidence,
    parts,
    reaction_step(evidence, [p["entity_id"] for p in parts], 3),
    [
        field("reported_yield", q(74, "%"), evidence, ["product_5a"]),
        field("formation_of_2c", "not observed", evidence, ["product_2c"]),
        field("product_selectivity", "5a formed exclusively", evidence, ["product_5a"]),
        field("yield_measurement_basis", None, ()),
    ],
    unresolved=[
        "The 74% yield basis is not explicitly stated for Scheme 2.",
        "Complex substrate and product structures are retained by labels; candidate SMILES are not asserted.",
        "Atmosphere, workup, and purification are not reported in the covered main text.",
    ],
))

# Table 1: 4a with eight aryl iodides; footnote states isolated yield based on 4a.
table1 = [
    (1, "p-NCC6H4", "4-iodobenzonitrile", "N#Cc1ccc(I)cc1", 2.5, "5b", 79),
    (2, "p-Me(O)CC6H4", "4-iodoacetophenone", "CC(=O)c1ccc(I)cc1", 2.5, "5c", 73),
    (3, "p-MeO2CC6H4", "methyl 4-iodobenzoate", "COC(=O)c1ccc(I)cc1", 2.5, "5d", 77),
    (4, "o-MeO2CC6H4", "methyl 2-iodobenzoate", "COC(=O)c1ccccc1I", 3, "5e", 76),
    (5, "p-BrC6H4", "1-bromo-4-iodobenzene", "Brc1ccc(I)cc1", 3, "5f", 72),
    (6, "Ph", "iodobenzene", "Ic1ccccc1", 3, "5g", 68),
    (7, "p-MeC6H4", "1-iodo-4-methylbenzene", "Cc1ccc(I)cc1", 7, "5h", 49),
    (8, "p-MeOC6H4", "1-iodo-4-methoxybenzene", "COc1ccc(I)cc1", 5, "5i", 38),
]
for entry, aryl_label, aryl_name, aryl_smiles, time_h, product_label, yield_pct in table1:
    evidence = ev(4)
    parts = common_participants(
        evidence,
        "4a",
        "4-nonsubstituted 2-substituted 2,3-allenyl hydrazine 4a (R1=n-C6H13, R2=Me, R3=Et)",
        aryl_label,
        aryl_name,
        aryl_smiles,
        [("product", product_label, f"2,3-dihydro-1H-pyrazole {product_label}")],
    )
    records.append(base_record(
        f"table1_entry{entry}",
        "substrate_scope_entry",
        evidence,
        parts,
        reaction_step(evidence, [p["entity_id"] for p in parts], time_h),
        [
            field("isolated_yield", q(yield_pct, "%"), evidence, ["product"]),
            field("yield_measurement_basis", "isolated yield based on 4a", evidence, ["product"]),
            field("four_membered_product_formation", "not observed", evidence),
        ],
        unresolved=[
            "Complex substrate and product structures are retained by source labels; candidate SMILES are not asserted.",
            "Atmosphere, workup, and purification are not reported in the covered main text.",
        ],
    ))

# Table 2: substrate/aryl-iodide scope under Conditions A.
table2 = [
    (1, "n-C6H13", "Me", "i-Pr", "4b", "p-Me(O)CC6H4", "4-iodoacetophenone", "CC(=O)c1ccc(I)cc1", 3, "5j", 76),
    (2, "n-C6H13", "Me", "t-Bu", "4c", "p-Me(O)CC6H4", "4-iodoacetophenone", "CC(=O)c1ccc(I)cc1", 5, "5k", 70),
    (3, "n-C4H9", "n-C5H11", "Et", "4d", "p-O2NC6H4", "1-iodo-4-nitrobenzene", "O=[N+]([O-])c1ccc(I)cc1", 3.5, "5l", 66),
    (4, "Cyclopropyl", "n-C5H11", "Et", "4e", "p-O2NC6H4", "1-iodo-4-nitrobenzene", "O=[N+]([O-])c1ccc(I)cc1", 3.5, "5m", 63),
    (5, "n-C5H11", "n-C8H17", "i-Pr", "4f", "p-O2NC6H4", "1-iodo-4-nitrobenzene", "O=[N+]([O-])c1ccc(I)cc1", 7, "5n", 72),
    (6, "n-C5H11", "Cyclohexyl", "i-Pr", "4g", "p-NCC6H4", "4-iodobenzonitrile", "N#Cc1ccc(I)cc1", 4, "5o", 76),
    (7, "n-C4H9", "Me", "Et", "4h", "p-BnO2CC6H4", "benzyl 4-iodobenzoate", "O=C(OCc1ccccc1)c1ccc(I)cc1", 3, "5p", 78),
    (8, "n-C4H9", "Et", "Et", "4i", "o-MeO2CC6H4", "methyl 2-iodobenzoate", "COC(=O)c1ccccc1I", 3, "5q", 76),
    (9, "n-C5H11", "Me", "Et", "4j", "p-NCC6H4", "4-iodobenzonitrile", "N#Cc1ccc(I)cc1", 3, "5r", 82),
    (10, "n-C5H11", "H", "Et", "4k", "p-NCC6H4", "4-iodobenzonitrile", "N#Cc1ccc(I)cc1", 3, "5s", 73),
    (11, "n-C5H11", "Me", "t-Bu", "4l", "4-Pyridyl", "4-iodopyridine", "Ic1ccncc1", 11, "5t", 86),
    (12, "Ph(CH2)2", "Me", "Et", "4m", "Pyrazinyl", "iodopyrazine", "Ic1cnccn1", 4, "5u", 84),
    (13, "Ph(CH2)2", "Me", "Et", "4m", "p-PhthNC6H4", "N-(4-iodophenyl)phthalimide", "O=C1N(c2ccc(I)cc2)C(=O)c2ccccc21", 7, "5v", 47),
    (14, "n-C5H11", "Me", "Et", "4j", "m-MeOC6H4", "1-iodo-3-methoxybenzene", "COc1cccc(I)c1", 5, "5w", 72),
]
for entry, r1, r2, r3, substrate_label, aryl_label, aryl_name, aryl_smiles, time_h, product_label, yield_pct in table2:
    evidence = ev(4)
    substrate_name = f"2,3-allenyl hydrazine {substrate_label} (R1={r1}, R2={r2}, R3={r3})"
    parts = common_participants(
        evidence,
        substrate_label,
        substrate_name,
        aryl_label,
        aryl_name,
        aryl_smiles,
        [("product", product_label, f"2,3-dihydro-1H-pyrazole {product_label}")],
    )
    records.append(base_record(
        f"table2_entry{entry}",
        "substrate_scope_entry",
        evidence,
        parts,
        reaction_step(evidence, [p["entity_id"] for p in parts], time_h),
        [
            field("isolated_yield", q(yield_pct, "%"), evidence, ["product"]),
            field("yield_measurement_basis", "isolated yield based on 4", evidence, ["product"]),
            field("product_selectivity", "five-membered product formed exclusively", evidence, ["product"]),
        ],
        unresolved=[
            "Complex substrate and product structures are retained by source labels; candidate SMILES are not asserted.",
            "Atmosphere, workup, and purification are not reported in the covered main text.",
        ],
    ))

# Table 3: five enantioenriched-substrate experiments.
table3 = [
    (1, "n-C4H9", "Me", "R-4h", {"number": 99, "unit": "%", "qualifier": "gt", "raw_text": ">99%"}, "p-BnO2CC6H4", "benzyl 4-iodobenzoate", "O=C(OCc1ccccc1)c1ccc(I)cc1", "R-5p", 77, 99),
    (2, "n-C4H9", "Me", "S-4h", q(96, "%"), "p-BnO2CC6H4", "benzyl 4-iodobenzoate", "O=C(OCc1ccccc1)c1ccc(I)cc1", "S-5p", 77, 95),
    (3, "n-C5H11", "Me", "R-4j", {"number": 99, "unit": "%", "qualifier": "gt", "raw_text": ">99%"}, "p-NCC6H4", "4-iodobenzonitrile", "N#Cc1ccc(I)cc1", "R-5r", 82, 98),
    (4, "n-C5H11", "Me", "S-4j", {"number": 99, "unit": "%", "qualifier": "gt", "raw_text": ">99%"}, "p-NCC6H4", "4-iodobenzonitrile", "N#Cc1ccc(I)cc1", "S-5r", 83, 96),
    (5, "n-C6H13", "Me", "R-4a", {"number": 99, "unit": "%", "qualifier": "gt", "raw_text": ">99%"}, "p-Me(O)CC6H4", "4-iodoacetophenone", "CC(=O)c1ccc(I)cc1", "R-5c", 71, 97),
]
for entry, r1, r2, substrate_label, input_ee, aryl_label, aryl_name, aryl_smiles, product_label, yield_pct, product_ee in table3:
    evidence = ev(5)
    parts = common_participants(
        evidence,
        substrate_label,
        f"enantioenriched 2,3-allenyl hydrazine {substrate_label} (R1={r1}, R2={r2})",
        aryl_label,
        aryl_name,
        aryl_smiles,
        [("product", product_label, f"optically active 2,3-dihydro-1H-pyrazole {product_label}")],
    )
    parts[0]["amounts"].append(field("input_ee", input_ee, evidence))
    records.append(base_record(
        f"table3_entry{entry}",
        "substrate_scope_entry",
        evidence,
        parts,
        reaction_step(evidence, [p["entity_id"] for p in parts], 3),
        [
            field("isolated_yield", q(yield_pct, "%"), evidence, ["product"]),
            field("yield_measurement_basis", "isolated yield", evidence, ["product"]),
            field("product_ee", q(product_ee, "%"), evidence, ["product"]),
            field("ee_measurement_basis", "HPLC", evidence, ["product"]),
        ],
        notes=["The authors state that racemization of the chiral centers is not clearly evident."],
        unresolved=[
            "Absolute configuration and complex structures are retained by source labels; candidate SMILES are not asserted.",
            "Atmosphere, workup, and purification are not reported in the covered main text.",
        ],
    ))

# Proposed alternatives in the conclusion are classified as mechanism, not experiment.
evidence = ev(5)
mechanism_parts = [
    participant("generic_allenyl_hydrazine", "reactant", "2-substituted 2,3-allenyl hydrazine 4", evidence, name="generic 2,3-allenyl hydrazine"),
    participant("generic_aryl_iodide", "reactant", "ArI", evidence, name="aryl iodide"),
    participant("generic_product", "product", "5", evidence, name="2,3-dihydro-1H-pyrazole product"),
]
records.append(base_record(
    "proposed_reaction_pathways",
    "mechanism",
    evidence,
    mechanism_parts,
    [],
    [],
    notes=[
        "Proposed alternative 1: oxidative addition followed by carbopalladation to form a pi-allylic palladium intermediate.",
        "Proposed alternative 2: nucleometalation followed by reductive elimination.",
    ],
    unresolved=[
        "The paper presents these as possible pathways, not verified intermediates or completed experiments.",
        "Generic R-group and organopalladium structures are not assigned candidate SMILES.",
    ],
))


assert len(records) == 31

raw_path = OUT / "raw_model/records_pages_0001_0005.json"
raw_path.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")

ids = {r["source_reaction_id"]: r["record_id"] for r in records}
coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1,
            "state": "attempted",
            "regions": [{
                "region": "full journal cover, including the two artistic reaction arrows in the lower half",
                "finding": "Issue-cover artwork summarizes transformations visually but gives no conditions, labels, yields, or independently identifiable batch. It was not duplicated as an experiment because the article supplies the source reactions on later pages.",
                "evidence_ids": ev(1),
            }],
            "record_ids": [],
            "unresolved": ["The stylized cover structures are not sufficiently labeled for independent structure assignment."],
        },
        {
            "page": 2,
            "state": "attempted",
            "regions": [{
                "region": "full web-theme frontispiece",
                "finding": "Publication-theme notice and promotional image only; no reaction arrow, table, experimental procedure, condition, or outcome.",
                "evidence_ids": ev(2),
            }],
            "record_ids": [],
            "unresolved": [],
        },
        {
            "page": 3,
            "state": "attempted",
            "regions": [
                {
                    "region": "title, abstract, introduction, and cited-prior-work discussion",
                    "finding": "Background and abstract-level claims were not converted into duplicate present-paper experiments; cited prior transformations lack independent reaction details on this page.",
                    "evidence_ids": ev(3),
                },
                {
                    "region": "lower-right Scheme 1 and adjacent Conditions A prose",
                    "finding": "Two present-paper coupling-cyclization experiments extracted, each with one trans-1,2-diazetidine and one 2,3-dihydro-1H-pyrazole yield.",
                    "evidence_ids": ev(3),
                },
                {
                    "region": "right-column Scheme 2 narrative",
                    "finding": "The 4a/4-nitroiodobenzene experiment was linked to the Scheme 2 drawing on page 4 and represented once.",
                    "evidence_ids": ev(3) + [f"{DOC}:page4:image"],
                },
            ],
            "record_ids": [ids["scheme1_entry_br"], ids["scheme1_entry_cn"], ids["scheme2_4a_p_nitro"]],
            "unresolved": [
                "Scheme 1 does not state its yield measurement basis.",
                "The ESI notice establishes availability only; no SI file was supplied or explicitly associated.",
            ],
        },
        {
            "page": 4,
            "state": "attempted",
            "regions": [
                {
                    "region": "upper-left Scheme 2",
                    "finding": "One 4a/4-nitroiodobenzene experiment extracted with 74% 5a, exclusive five-membered-product formation, and 2c not observed.",
                    "evidence_ids": ev(4) + [f"{DOC}:page3:text"],
                },
                {
                    "region": "left-center Table 1 and footnote",
                    "finding": "Eight aryl-iodide substrate-scope rows extracted independently with row-specific time, product, and isolated yield based on 4a.",
                    "evidence_ids": ev(4),
                },
                {
                    "region": "lower Table 2 and footnote",
                    "finding": "Fourteen allenyl-hydrazine/aryl-iodide scope rows extracted independently with R1/R2/R3 values, time, product label, and isolated yield based on 4.",
                    "evidence_ids": ev(4),
                },
                {
                    "region": "right-center Figure 1",
                    "finding": "ORTEP of 5v supports Table 2 entry 13 identity and was not counted as an additional reaction.",
                    "evidence_ids": ev(4),
                },
            ],
            "record_ids": [ids["scheme2_4a_p_nitro"]]
            + [ids[f"table1_entry{i}"] for i in range(1, 9)]
            + [ids[f"table2_entry{i}"] for i in range(1, 15)],
            "unresolved": [
                "Complex substrate/product connectivity and stereochemistry remain unverified machine records.",
                "The covered main text omits atmosphere, workup, and purification.",
            ],
        },
        {
            "page": 5,
            "state": "attempted",
            "regions": [
                {
                    "region": "top Table 3 and footnotes",
                    "finding": "Five enantioenriched-substrate scope rows extracted independently with input ee, isolated yield, product ee, and HPLC measurement basis.",
                    "evidence_ids": ev(5),
                },
                {
                    "region": "left-column conclusion mechanism sentence",
                    "finding": "Two alternative possible pathways were classified together as a proposed mechanism, not as an observed experiment.",
                    "evidence_ids": ev(5),
                },
                {
                    "region": "remaining conclusion, acknowledgements, references, and crystal-data note",
                    "finding": "No additional present-paper reaction batch; bibliographic citations were not expanded, and crystal data for 5v were linked conceptually to the existing Table 2 entry rather than counted again.",
                    "evidence_ids": ev(5),
                },
            ],
            "record_ids": [ids[f"table3_entry{i}"] for i in range(1, 6)] + [ids["proposed_reaction_pathways"]],
            "unresolved": [
                "The main text does not provide the experimental procedures advertised as ESI.",
                "Absolute configurations and complex structures require chemistry review.",
            ],
        },
    ],
}

coverage_path = OUT / "coverage/pages_0001_0005.json"
coverage_path.parent.mkdir(parents=True, exist_ok=True)
coverage_path.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

tasks_path = OUT / "tasks.json"
tasks = json.loads(tasks_path.read_text())
for task in tasks:
    if task.get("document_id") == DOC and task.get("evidence_id") in {f"{DOC}:page{i}:text" for i in range(1, 6)}:
        task["state"] = "attempted"
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"records": len(records), "coverage_pages": len(coverage["pages"]), "raw": str(raw_path)}, ensure_ascii=False))
