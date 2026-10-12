#!/usr/bin/env python3
"""Build evidence-linked raw records for visually inspected PDF pages 7-9."""

import json
from pathlib import Path


DOC = "doc_2da56877b1a5d32e"
OUT = Path(__file__).with_name("extracted_records_pages_0007_0009.json")
records = []


def fact(value, evidence):
    return {
        "value": value,
        "evidence_ids": list(evidence) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def p(role, label, *, smiles=None, amounts=None):
    return {
        "role": role,
        "label": label,
        "smiles": smiles,
        "amounts": amounts or [],
    }


def q(name, value):
    return (name, value)


def add(page, suffix, kind, participants, *, conditions=None, outcomes=None,
        notes=None, unresolved=None, missing_conditions=None,
        missing_outcomes=None):
    evidence = [f"{DOC}:page{page}:text", f"{DOC}:page{page}:image"]
    built = []
    product_ids = []
    for idx, spec in enumerate(participants, 1):
        entity_id = f"e{idx:02d}"
        amounts = [
            {"name": name, "fact": fact(value, evidence)}
            for name, value in spec.get("amounts", [])
        ]
        item = {
            "entity_id": entity_id,
            "role": spec["role"],
            "label": fact(spec["label"], evidence),
            "name": fact(None, evidence),
            "smiles": fact(spec.get("smiles"), evidence),
            "smiles_parseable": None,
            "structure_verified": False,
            "amounts": amounts,
        }
        built.append(item)
        if item["role"] == "product":
            product_ids.append(entity_id)

    fields = []
    for outcome in outcomes or []:
        name, value = outcome[:2]
        target_ordinals = outcome[2] if len(outcome) > 2 else None
        field = {"name": name, "fact": fact(value, evidence)}
        if target_ordinals is not None:
            field["target_entity_ids"] = [product_ids[i] for i in target_ordinals]
        elif product_ids:
            field["target_entity_ids"] = list(product_ids)
        fields.append(field)
    for name in missing_outcomes or []:
        field = {"name": name, "fact": fact(None, evidence)}
        if product_ids:
            field["target_entity_ids"] = list(product_ids)
        fields.append(field)

    step_conditions = [
        {"name": name, "fact": fact(value, evidence)}
        for name, value in (conditions or [])
    ]
    step_conditions.extend(
        {"name": name, "fact": fact(None, evidence)}
        for name in (missing_conditions or [])
    )
    record_id = f"{DOC}:{suffix}"
    base_unresolved = [
        "This record is a review summary of prior literature or a proposed mechanism, not a new experiment reported by this Microreview.",
        "No explicitly associated Supporting Information was supplied; scale, detailed procedure, workup, purification, and yield measurement basis are missing unless shown.",
    ]
    record = {
        "record_id": record_id,
        "document_id": DOC,
        "source_reaction_id": suffix,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": evidence,
        "participants": built,
        "steps": ([{
            "step_id": "s1",
            "participant_ids": [x["entity_id"] for x in built],
            "conditions": step_conditions,
        }] if built or step_conditions else []),
        "outcomes": fields,
        "notes": [fact(x, evidence) for x in (notes or [])],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": base_unresolved + (unresolved or []),
        },
    }
    records.append(record)
    return record_id


# Page 7, Scheme 28: six distinct hydride/catalyst/substrate rows.
scheme28_common_top = [
    p("reactant", "3-bromooct-1-yne", smiles="C#CC(Br)CCCCC"),
    p("catalyst", "Pd(PPh3)4"),
    p("product", "octa-1,2-diene (drawn allene product)", smiles="C=C=CCCCCC"),
    p("product", "oct-1-yne (drawn alkyne product)", smiles="C#CCCCCCC"),
]
for suffix, hydride, yld in [
    ("lialh4", "LiAlH4", 42),
    ("et3bhli", "Et3BHLi", 82),
]:
    add(7, f"p7_scheme28_terminal_{suffix}", "literature_example",
        [scheme28_common_top[0], p("reagent", hydride), *scheme28_common_top[1:]],
        outcomes=[
            ("combined_yield", {"number": yld, "unit": "%"}),
            ("allene_to_alkyne_ratio", "100:0"),
        ],
        missing_conditions=["solvent", "temperature", "time"],
        unresolved=["The source does not state the yield measurement basis for this Scheme 28 row."])

add(7, "p7_scheme28_undec_et3bhli", "literature_example", [
    p("reactant", "1-bromoundec-2-yne (C8H17-substituted drawing)",
      smiles="BrCC#CCCCCCCCC"),
    p("reagent", "Et3BHLi"), p("catalyst", "Pd(PPh3)4"),
    p("product", "undeca-1,2-diene", smiles="C=C=CCCCCCCCC"),
    p("product", "undeca-2-yne", smiles="CC#CCCCCCCCC"),
], outcomes=[
    ("combined_yield", {"number": 85, "unit": "%"}),
    ("allene_to_alkyne_ratio", "0:100"),
], missing_conditions=["solvent", "temperature", "time"],
    unresolved=["The source does not state the yield measurement basis for this Scheme 28 row."])

for suffix, leaving_group, yld, ratio in [
    ("oms", "OMs", 89, "80:20"),
    ("br", "Br", 66, "65:35"),
    ("phosphonate", "OP(O)(OEt)2", 61, "79:21"),
]:
    add(7, f"p7_scheme28_internal_{suffix}", "literature_example", [
        p("reactant", f"C4H9-substituted internal propargylic derivative (X={leaving_group})"),
        p("reagent", "Et3BHLi"), p("catalyst", "Pd(PPh3)4"),
        p("product", "C4H9-substituted allene product"),
        p("product", "C4H9-substituted alkyne product"),
    ], outcomes=[
        ("combined_yield", {"number": yld, "unit": "%"}),
        ("allene_to_alkyne_ratio", ratio),
    ], missing_conditions=["solvent", "temperature", "time"],
        unresolved=[
            "C4H9 is not isomer-resolved in the scheme, so no complete substrate or product SMILES is assigned.",
            "The source does not state the yield measurement basis for this Scheme 28 row.",
        ])


# Page 7, Scheme 29 and its explicitly stated undeca-2-ynyl example.
scheme29_conditions = [
    q("solvent", "THF"), q("atmosphere", "Ar"),
    q("temperature", {"minimum": 20, "maximum": 30, "unit": "°C", "raw_text": "20–30 °C"}),
]
scheme29_catalysts = [
    p("catalyst", "Pd2(dba)3·CHCl3"), p("reagent", "P(nBu)3"),
]
add(7, "p7_scheme29_generic_hydrogenolysis", "literature_example", [
    p("reactant", "alk-2-ynyl methyl carbonate (R1,R2 = alkyl or aryl)"),
    p("reagent", "HCO2NH4", smiles="[NH4+].[O-]C=O"),
    *scheme29_catalysts, p("solvent", "THF", smiles="C1CCOC1"),
    p("product", "1,1-disubstituted allene 61"),
], conditions=scheme29_conditions, missing_conditions=["time"],
    missing_outcomes=["yield"],
    notes=["Scheme 29 states that ammonium formate is the hydride source."],
    unresolved=["R1 and R2 are generic; no substrate-specific yield is printed in Scheme 29."])

add(7, "p7_scheme29_undeca2ynyl", "literature_example", [
    p("reactant", "undeca-2-ynyl methyl carbonate"),
    p("reagent", "HCO2NH4", smiles="[NH4+].[O-]C=O"),
    *scheme29_catalysts, p("solvent", "THF", smiles="C1CCOC1"),
    p("product", "undeca-1,2-diene", smiles="C=C=CCCCCCCCC"),
    p("product", "undeca-2-yne", smiles="CC#CCCCCCCCC"),
], conditions=scheme29_conditions, missing_conditions=["time"], outcomes=[
    ("combined_yield", {"number": 81, "unit": "%"}),
    ("undeca_1_2_diene_to_undeca_2_yne_ratio", "5:1"),
], unresolved=["The prose gives a combined yield but no measurement basis or reaction time."])


# Page 7, Scheme 30: two epoxide rows under the immediately preceding 'idem' conditions.
for suffix, substrate, allene, alkyne, y_allene, y_alkyne in [
    ("phenyl", "phenyl-substituted 1-alkynyl epoxide",
     "2,3-dienol 62", "3-alkyn-1-ol 63", 26, 74),
    ("pentyl", "C5H11-substituted 1-alkynyl epoxide",
     "2,3-dienol 64", "3-alkyn-1-ol 65", 43, 57),
]:
    add(7, f"p7_scheme30_epoxide_{suffix}", "literature_example", [
        p("reactant", substrate),
        p("reagent", "HCO2NH4", smiles="[NH4+].[O-]C=O"),
        *scheme29_catalysts, p("solvent", "THF", smiles="C1CCOC1"),
        p("product", allene), p("product", alkyne),
    ], conditions=scheme29_conditions, missing_conditions=["time"], outcomes=[
        (f"yield_{allene.split()[-1]}", {"number": y_allene, "unit": "%"}, [0]),
        (f"yield_{alkyne.split()[-1]}", {"number": y_alkyne, "unit": "%"}, [1]),
    ], notes=[
        "The arrow is marked 'idem'; only the immediately preceding Scheme 29 catalyst, solvent, atmosphere, and temperature conditions are carried forward.",
    ], unresolved=[
        "The review does not state reaction time or yield measurement basis, and the stereochemical drawings were not converted to SMILES.",
    ])


# Page 7, Scheme 31: split the proposed allene and alkyne branches.
add(7, "p7_scheme31_allene_mechanism", "mechanism", [
    p("reactant", "propargylic methyl carbonate"),
    p("catalyst", "Pd(0)Ln"),
    p("reagent", "HCO2NH4", smiles="[NH4+].[O-]C=O"),
    p("unspecified_agent", "η1-allenylic Pd formate/hydride intermediates"),
    p("product", "allene"),
], notes=[
    "Scheme 31 proposes decarboxylation/formate transfer and reductive elimination through an η1-allenylic Pd pathway.",
], unresolved=["Generic R groups and proposed intermediates preclude structure-specific SMILES."])
add(7, "p7_scheme31_alkyne_mechanism", "mechanism", [
    p("reactant", "propargylic methyl carbonate"),
    p("catalyst", "Pd(0)Ln"),
    p("reagent", "HCO2NH4", smiles="[NH4+].[O-]C=O"),
    p("unspecified_agent", "η1-propargylic Pd formate/hydride intermediates"),
    p("product", "alkyne"),
], notes=[
    "Scheme 31 proposes an equilibrating η1-propargylic Pd pathway followed by decarboxylation and reductive elimination to alkyne.",
], unresolved=["Generic R groups and proposed intermediates preclude structure-specific SMILES."])


# Page 8, Scheme 32: two distinct Pd(0)-catalyzed propargylic-formate rows.
for suffix, substrate, allene, alkyne, yld, ratio in [
    ("linear", "linear methoxyethoxy-undecynyl formate (upper row)",
     "linear long-chain allene", "linear long-chain alkyne", 93, "91:9"),
    ("tethered", "tethered methoxyethoxy propargylic formate (lower row)",
     "tethered long-chain allene", "tethered long-chain alkyne", 86, "99:1"),
]:
    add(8, f"p8_scheme32_{suffix}", "literature_example", [
        p("reactant", substrate), p("catalyst", "Pd(0)"),
        p("product", allene), p("product", alkyne),
    ], missing_conditions=["solvent", "temperature", "time"], outcomes=[
        ("combined_yield", {"number": yld, "unit": "%"}),
        ("allene_to_alkyne_ratio", ratio),
    ], unresolved=[
        "The Pd(0) catalyst identity/loading, solvent, temperature, time, and yield basis are not printed.",
        "The long-chain drawings were retained as labels without candidate SMILES.",
    ])


# Page 8, Scheme 33: two substrate rows; 'idem' carries catalyst/ligand/solvent only.
scheme33_agents = [
    p("catalyst", "Pd(acac)2"), p("reagent", "nBu3P", smiles="CCCCP(CCCC)CCCC"),
    p("solvent", "benzene", smiles="c1ccccc1"),
]
add(8, "p8_scheme33_formate66", "literature_example", [
    p("reactant", "propargylic formate 66"), *scheme33_agents,
    p("product", "alkynylic product 67"),
    p("product", "corresponding allene regioisomer (not numbered)"),
], conditions=[q("solvent", "benzene"), q("time", {"number": 3, "unit": "h"})],
    missing_conditions=["temperature"], outcomes=[
        ("combined_yield", {"number": 92, "unit": "%"}),
        ("alkyne_to_allene_ratio", "99:1"),
    ], unresolved=["Temperature and yield measurement basis are not printed."])
add(8, "p8_scheme33_formate68", "literature_example", [
    p("reactant", "Boc-protected cyclic propargylic formate 68"), *scheme33_agents,
    p("product", "alkynylic product 69"),
    p("product", "corresponding allene regioisomer (not numbered)"),
], conditions=[q("solvent", "benzene"), q("time", {"number": 20, "unit": "h"})],
    missing_conditions=["temperature"], outcomes=[
        ("alkyne_to_allene_ratio", "99:1"),
    ], missing_outcomes=["combined_yield"], notes=[
        "The arrow is marked 'idem'; Pd(acac)2/nBu3P in benzene is carried from the immediately preceding row, while the printed time is 20 h.",
    ], unresolved=["No yield or temperature is printed for formate 68."])


# Page 8, Scheme 34: four ligand-tether-length rows.
for n, yld, ratio in [
    (1, {"number": 56, "unit": "%"}, "72:28"),
    (3, {"minimum": 74, "maximum": 76, "unit": "%", "raw_text": "74–76%"}, "0:100"),
    (4, {"number": 61, "unit": "%"}, "18:82"),
    (6, {"number": 62, "unit": "%"}, "83:17"),
]:
    add(8, f"p8_scheme34_ligand_n{n}", "literature_example", [
        p("reactant", "cyclic alkynyl carbonate 70"),
        p("reagent", "HCO2H", smiles="O=CO"),
        p("reagent", "NEt3", smiles="CCN(CC)CC"),
        p("catalyst", "Pd(dba)2"),
        p("reagent", f"Ph2P(CH2){n}PPh2"),
        p("solvent", "THF", smiles="C1CCOC1"),
        p("product", "alkynic product 71"), p("product", "allenic product 72"),
    ], conditions=[
        q("solvent", "THF"), q("temperature", {"number": 60, "unit": "°C"}),
    ], missing_conditions=["time"], outcomes=[
        ("combined_yield_71_and_72", yld),
        ("product_ratio_71_to_72", ratio),
    ], unresolved=[
        "Catalyst/ligand loadings, reaction time, and yield measurement basis are not printed.",
        "The product drawings were retained as labels without candidate SMILES.",
    ])


# Page 8, Scheme 35: four phosphine rows, including the explicit no-reaction result.
add(8, "p8_scheme35_pr3_ibu", "literature_example", [
    p("reactant", "steroidal propargylic formate 73"),
    p("catalyst", "Pd(acac)2"), p("reagent", "P(iBu)3"),
    p("solvent", "toluene", smiles="Cc1ccccc1"),
], conditions=[
    q("catalyst_to_phosphine_ratio", "1:4"), q("solvent", "toluene"),
    q("temperature", {"number": 65, "unit": "°C"}),
], missing_conditions=["time"], outcomes=[
    ("reaction_result", "no reaction"),
], notes=["The table explicitly prints 'No reaction' for PR3 = iBu."],
    unresolved=["Reaction time and conversion/recovery details are not printed."])

for suffix, ligand, ratio in [
    ("nbu", "P(nBu)3", "87:13"),
    ("et", "PEt3", "91:9"),
    ("me", "PMe3", "95:5"),
]:
    ligand_smiles = "CCCCP(CCCC)CCCC" if suffix == "nbu" else None
    add(8, f"p8_scheme35_pr3_{suffix}", "literature_example", [
        p("reactant", "steroidal propargylic formate 73"),
        p("catalyst", "Pd(acac)2"), p("reagent", ligand, smiles=ligand_smiles),
        p("solvent", "toluene", smiles="Cc1ccccc1"),
        p("product", "steroidal alkynic product 74"),
        p("product", "steroidal allenic product 75"),
    ], conditions=[
        q("catalyst_to_phosphine_ratio", "1:4"), q("solvent", "toluene"),
        q("temperature", {"number": 65, "unit": "°C"}),
    ], missing_conditions=["time"], outcomes=[
        ("product_ratio_74_to_75", ratio),
    ], missing_outcomes=["combined_yield"], unresolved=[
        "No total yield, reaction time, or ratio measurement basis is printed.",
        "The stereochemically detailed substrate/products were retained as labels without candidate SMILES.",
    ])


# Page 8, Scheme 36: split the proposed fast alkyne and slow allene branches.
add(8, "p8_scheme36_fast_alkyne_branch", "mechanism", [
    p("unspecified_agent", "η3-allenyl/propargyl Pd-phosphine manifold"),
    p("unspecified_agent", "less sterically demanding Pd intermediate 76"),
    p("product", "alkyne 74 (generic R1/R2 depiction)"),
], notes=[
    "Scheme 36 labels conversion of intermediate 76 to the alkyne as the fast branch after phosphine dissociation/equilibration.",
], unresolved=["This is a generic proposed mechanism with R1/R2 groups, not an isolated experiment."])
add(8, "p8_scheme36_slow_allene_branch", "mechanism", [
    p("unspecified_agent", "η3-allenyl/propargyl Pd-phosphine manifold"),
    p("unspecified_agent", "sterically demanding Pd intermediate 77"),
    p("product", "allene (generic R1/R2 depiction)"),
], notes=[
    "Scheme 36 labels conversion of intermediate 77 to the allene as the slow branch.",
], unresolved=["This is a generic proposed mechanism with R1/R2 groups, not an isolated experiment."])


# Page 9, Scheme 37: four distinct R-group homocoupling rows.
for suffix, rval, yld, printed_ratio in [
    ("sime3", "SiMe3", 48, "79:21"),
    ("siibu3", "Si(iBu)3", 73, "93:7"),
    ("siipr3", "Si(iPr)3", 85, "95:5"),
    ("tbu", "tBu", 7, "71:29"),
]:
    add(9, f"p9_scheme37_r_{suffix}", "literature_example", [
        p("reactant", f"propargylic carbonate (R={rval}; carbonate OR' group generic)"),
        p("catalyst", "Pd(PPh3)4", amounts=[
            q("catalyst_loading", {"number": 5, "unit": "mol%"}),
        ]),
        p("solvent", "toluene", smiles="Cc1ccccc1"),
        p("product", f"1,2-alkadien-5-yne 78 (R={rval})"),
        p("product", f"1,5-alkadiyne 79 (R={rval})"),
    ], conditions=[q("solvent", "toluene"), q("temperature", "reflux")],
        missing_conditions=["time"], outcomes=[
            ("combined_yield", {"number": yld, "unit": "%"}),
            ("printed_product_ratio_header_77_to_78", printed_ratio),
        ], notes=[
            "The product structures in Scheme 37 are numbered 78 and 79, but the printed table header reads 'ratio of 77:78'; the header/value are preserved without silent correction.",
        ], unresolved=[
            "The Scheme 37 product-number/header discrepancy (products 78/79 versus printed ratio header 77:78) is unresolved.",
            "The carbonate OR' group, reaction time, and yield measurement basis are not specified.",
        ])


OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")

current_dir = OUT.parent.parent
image_evidence = lambda page: [f"{DOC}:page{page}:image"]
ids_by_page = {
    page: [r["record_id"] for r in records if r["source_reaction_id"].startswith(f"p{page}_")]
    for page in range(7, 10)
}
coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 7,
            "state": "attempted",
            "regions": [
                {"region": "Scheme 28, upper half", "finding": "Six separate prior-literature hydride reduction rows were visually checked: two hydrides for the terminal substrate, one C8H17 row, and three leaving-group rows; yields and allene/alkyne ratios were retained per row.", "evidence_ids": image_evidence(7)},
                {"region": "Scheme 29 and adjacent prose, middle-left", "finding": "One generic ammonium-formate hydrogenolysis scheme plus the separately stated undeca-2-ynyl carbonate result (81% combined yield, 5:1 diene/alkyne) were recorded as prior-literature examples.", "evidence_ids": image_evidence(7)},
                {"region": "Scheme 30, bottom", "finding": "Two 1-alkynyl-epoxide rows with product-specific percentages (62/63 and 64/65) were recorded separately under the immediately preceding 'idem' conditions.", "evidence_ids": image_evidence(7)},
                {"region": "Scheme 31, right column", "finding": "The proposed η1-allenylic and η1-propargylic palladium branches were represented as two mechanism records, not experiments.", "evidence_ids": image_evidence(7)},
                {"region": "bottom-left prose leading to Scheme 32", "finding": "Narrative lead-in only; Scheme 32 is located on original PDF page 8 and is not assigned to page 7.", "evidence_ids": image_evidence(7)},
            ],
            "record_ids": ids_by_page[7],
            "unresolved": [
                "Schemes 28-30 are review summaries and generally omit scale, time, workup, purification, and yield measurement basis.",
                "Several structures use generic R/C4H9 groups or detailed drawings not converted to SMILES.",
            ],
        },
        {
            "page": 8,
            "state": "attempted",
            "regions": [
                {"region": "Scheme 32, upper-left", "finding": "Two distinct Pd(0)-catalyzed propargylic-formate rows with 93%/91:9 and 86%/99:1 yield/selectivity data were recorded.", "evidence_ids": image_evidence(8)},
                {"region": "Scheme 33, middle-left", "finding": "Two internal-alkyne formate reductions were separated: 66→67 (3 h, 92%, 99:1) and 68→69 ('idem', 20 h, 99:1; no yield printed).", "evidence_ids": image_evidence(8)},
                {"region": "Scheme 34, lower-middle", "finding": "Four diphosphine tether-length rows (n=1,3,4,6) were recorded independently with their own combined yields and 71:72 ratios.", "evidence_ids": image_evidence(8)},
                {"region": "Scheme 35, bottom", "finding": "Four phosphine rows were separated, including the explicit P(iBu)3 no-reaction result and three 74:75 product-ratio rows.", "evidence_ids": image_evidence(8)},
                {"region": "Scheme 36, upper-right", "finding": "The proposed fast alkyne and slow allene branches were classified as two mechanism records.", "evidence_ids": image_evidence(8)},
                {"region": "Homocoupling section lead-in, lower-right", "finding": "Narrative lead-in only; the Scheme 37 reaction/table appears on original PDF page 9.", "evidence_ids": image_evidence(8)},
            ],
            "record_ids": ids_by_page[8],
            "unresolved": [
                "Schemes 32-35 omit reaction scale, workup, purification, and most yield/ratio measurement bases; several rows also omit catalyst loading or time.",
                "Detailed long-chain and steroidal drawings were retained as source labels with null SMILES.",
            ],
        },
        {
            "page": 9,
            "state": "attempted",
            "regions": [
                {"region": "Scheme 37, upper-left", "finding": "Four R-group homocoupling rows were recorded independently with 5 mol% Pd(PPh3)4, toluene reflux, combined yields, and printed ratio values.", "evidence_ids": image_evidence(9)},
                {"region": "Scheme 37 table header", "finding": "Source discrepancy retained: products in the drawing are numbered 78 and 79, while the table header prints 'ratio of 77:78'. No correction was inferred.", "evidence_ids": image_evidence(9)},
                {"region": "Concluding Remarks and Acknowledgments", "finding": "Review-level conclusions and acknowledgments only; no additional reaction experiment.", "evidence_ids": image_evidence(9)},
                {"region": "reference list [1]-[42]", "finding": "Bibliographic citations only; no reaction records were fabricated from reference entries.", "evidence_ids": image_evidence(9)},
            ],
            "record_ids": ids_by_page[9],
            "unresolved": [
                "The Scheme 37 product-number/table-header discrepancy remains unresolved.",
                "The carbonate OR' group, reaction times, and yield measurement bases are not reported in the scheme.",
            ],
        },
    ],
}
coverage_path = current_dir / "coverage" / "pages_0007_0009.json"
coverage_path.parent.mkdir(parents=True, exist_ok=True)
coverage_path.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

tasks_path = current_dir / "tasks.json"
if tasks_path.exists():
    tasks = json.loads(tasks_path.read_text())
    for task in tasks:
        if task.get("document_id") != DOC:
            continue
        for page in range(7, 10):
            if task.get("evidence_id") == f"{DOC}:page{page}:text":
                task["state"] = "attempted"
                task["visual_evidence_id"] = f"{DOC}:page{page}:image"
                task["reason"] = "Original page image inspected; extraction attempted and documented in coverage/pages_0007_0009.json."
    tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({
    "records": len(records),
    "per_page": {str(page): len(ids_by_page[page]) for page in range(7, 10)},
    "out": str(OUT),
    "coverage": str(coverage_path),
}, ensure_ascii=False))
