from pathlib import Path
import json


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "runs/current/raw_model/records_pages_0001_0003.json"
COVERAGE = ROOT / "runs/current/coverage/pages_0001_0003.json"
TASKS = ROOT / "runs/current/tasks.json"
DOC = "doc_074ea56d951ef806"
P1T, P1I = f"{DOC}:page1:text", f"{DOC}:page1:image"
P2T, P2I = f"{DOC}:page2:text", f"{DOC}:page2:image"
P3T, P3I = f"{DOC}:page3:text", f"{DOC}:page3:image"
E1, E2, E3 = [P1T, P1I], [P2T, P2I], [P3T, P3I]


def fact(value, evidence):
    return {
        "value": value,
        "evidence_ids": list(evidence) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def field(name, value, evidence, targets=None):
    result = {"name": name, "fact": fact(value, evidence)}
    if targets:
        result["target_entity_ids"] = list(targets)
    return result


def participant(entity_id, role, label, evidence, *, name=None, smiles=None, amounts=()):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence),
        "smiles": fact(smiles, evidence),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": list(amounts),
    }


def record(rid, kind, evidence, participants, conditions, outcomes, notes, unresolved):
    return {
        "record_id": f"{DOC}:{rid}",
        "document_id": DOC,
        "source_reaction_id": rid,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": list(dict.fromkeys(evidence)),
        "participants": participants,
        "steps": [{
            "step_id": "reaction",
            "participant_ids": [p["entity_id"] for p in participants if p["role"] != "product"],
            "conditions": conditions,
        }],
        "outcomes": outcomes,
        "notes": [fact(n, evidence) for n in notes],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved,
        },
    }


SUBSTRATE_SMILES = {
    "1a": "CCOC(=O)NN(C(=O)OCC)C(CCCCC)C=C=C",
    "1b": "CCOC(=O)NN(C(=O)OCC)C(CCCCCCC)C=C=C",
    "1c": "CCOC(=O)NN(C(=O)OCC)C(CCCCCCCC)C=C=C",
    "1d": "CCOC(=O)NN(C(=O)OCC)C(Cc1ccccc1)C=C=C",
}
ARYL = {
    "p-MeC6H4": ("4-iodotoluene", "Cc1ccc(I)cc1"),
    "m-MeC6H4": ("3-iodotoluene", "Cc1cccc(I)c1"),
    "Ph": ("iodobenzene", "Ic1ccccc1"),
    "p-MeOC6H4": ("4-iodoanisole", "COc1ccc(I)cc1"),
}
BASES = {
    "Na2CO3": ("sodium carbonate", "[Na+].[Na+].[O-]C([O-])=O"),
    "NaOH": ("sodium hydroxide", "[Na+].[OH-]"),
    "KOtBu": ("potassium tert-butoxide", "[K+].[O-]C(C)(C)C"),
    "Et3N": ("triethylamine", "CCN(CC)CC"),
    "Cy2NMe": ("N-methyldicyclohexylamine", "CN(C1CCCCC1)C1CCCCC1"),
    "Cs2CO3": ("cesium carbonate", "[Cs+].[Cs+].[O-]C([O-])=O"),
    "Ag2CO3": ("silver carbonate", "[Ag+].[Ag+].[O-]C([O-])=O"),
    "K2CO3": ("potassium carbonate", "[K+].[K+].[O-]C([O-])=O"),
    "CsF": ("cesium fluoride", "[Cs+].[F-]"),
    "KOH": ("potassium hydroxide", "[K+].[OH-]"),
}


def common_participants(substrate, aryl_key, product, evidence, *, base="Cs2CO3", base_equiv=1.1,
                        exact=False, include_4a=False):
    aryl_name, aryl_smiles = ARYL[aryl_key]
    base_name, base_smiles = BASES[base]
    substrate_amounts = []
    aryl_amounts = [field("equivalents", {"number": 1.2, "unit": "equiv"}, evidence)]
    catalyst_amounts = [field("catalyst_loading", {"number": 5, "unit": "mol%"}, evidence)]
    base_amounts = [field("equivalents", {"number": base_equiv, "unit": "equiv"}, evidence)]
    solvent_amounts = []
    if exact:
        substrate_amounts = [
            field("mass", {"number": 76, "unit": "mg"}, E2),
            field("amount", {"number": 0.25, "unit": "mmol"}, E2),
        ]
        aryl_amounts += [
            field("mass", {"number": 65, "unit": "mg"}, E2),
            field("amount", {"number": 0.30, "unit": "mmol"}, E2),
        ]
        catalyst_amounts += [
            field("mass", {"number": 15, "unit": "mg"}, E2),
            field("amount", {"number": 0.013, "unit": "mmol"}, E2),
        ]
        base_amounts += [
            field("mass", {"number": 90, "unit": "mg"}, E2),
            field("amount", {"number": 0.28, "unit": "mmol"}, E2),
        ]
        solvent_amounts = [field("volume", {"number": 3, "unit": "mL"}, E2)]
    ps = [
        participant("substrate", "reactant", substrate, evidence,
                    name="2,3-allenyl hydrazine " + substrate,
                    smiles=SUBSTRATE_SMILES[substrate], amounts=substrate_amounts),
        participant("aryl_iodide", "reactant", f"{aryl_key}I", evidence,
                    name=aryl_name, smiles=aryl_smiles, amounts=aryl_amounts),
        participant("pd_catalyst", "catalyst", "[Pd(PPh3)4]", evidence,
                    name="tetrakis(triphenylphosphine)palladium(0)", amounts=catalyst_amounts),
        participant("base", "reagent", base, evidence, name=base_name,
                    smiles=base_smiles, amounts=base_amounts),
        participant("mecn", "solvent", "MeCN", evidence, name="acetonitrile",
                    smiles="CC#N", amounts=solvent_amounts),
        participant("major_product", "product", product, evidence,
                    name="trans-1,2-diazetidine " + product),
    ]
    if include_4a:
        ps.append(participant("regioisomer_4a", "product", "4a", evidence,
                              name="five-membered-ring regioisomer 4a"))
    return ps


records = []

# Table 1 entries 1-10. Entry 11 is merged below with Table 2 entry 1 and the exact procedure.
t1 = [
    (1, "Na2CO3", 24, {"number": 11, "unit": "%"}, "100:0", {"number": 0, "unit": "%"}, 82),
    (2, "NaOH", 5, "n.d. (complicated reaction mixture)", None, None, None),
    (3, "KOtBu", 2, "n.d. (complicated reaction mixture)", None, None, None),
    (4, "Et3N", 20, {"number": 5, "unit": "%"}, "100:0", {"number": 0, "unit": "%"}, 87),
    (5, "Cy2NMe", 30.5, "trace", None, None, None),
    (6, "Cs2CO3", 2, {"number": 74, "unit": "%"}, "100:0",
     {"number": 7, "unit": "%", "qualifier": "lt", "raw_text": "<7%"}, None),
    (7, "Ag2CO3", 2, {"number": 53, "unit": "%"}, "100:0",
     {"number": 10, "unit": "%", "qualifier": "lt", "raw_text": "<10%"}, None),
    (8, "K2CO3", 6, {"number": 74, "unit": "%"}, "20:1", "trace", None),
    (9, "CsF", 24, {"number": 64, "unit": "%"}, "17:1", "trace", None),
    (10, "KOH", 2, {"number": 59, "unit": "%"}, "100:0",
     {"number": 6, "unit": "%", "qualifier": "lt", "raw_text": "<6%"}, None),
]
for entry, base, hours, y3, ratio, y4, recovered in t1:
    ps = common_participants("1a", "p-MeC6H4", "3a", E1, base=base, base_equiv=2, include_4a=True)
    outcomes = [field("reported_yield_3a", y3, E1, ["major_product"])]
    if ratio is not None:
        outcomes.append(field("trans_cis_ratio_3a", ratio, E1, ["major_product"]))
    if y4 is not None:
        outcomes.append(field("reported_yield_4a", y4, E1, ["regioisomer_4a"]))
    if recovered is not None:
        outcomes.append(field("recovered_starting_material_yield", {"number": recovered, "unit": "%"}, E1, ["substrate"]))
    if isinstance(y3, dict) or isinstance(y4, dict):
        outcomes.append(field("yield_measurement_basis", "isolated product", E1,
                              [x for x in ["major_product", "regioisomer_4a"] if x]))
    unresolved = [
        "Atmosphere, solvent volume, workup, and purification are not stated for this optimization row.",
        "The candidate substrate constitution and all product structures/stereochemistry remain unverified.",
        "Supporting information is mentioned but was not supplied or associated.",
    ]
    if entry in (2, 3):
        unresolved.append("The source reports n.d. because of a complicated mixture; individual product yields and selectivity are unavailable.")
    records.append(record(
        f"table1_entry{entry}", "optimization_entry", E1, ps,
        [
            field("temperature", {"number": 80, "unit": "°C"}, E1),
            field("time", {"number": hours, "unit": "h"}, E1),
            field("atmosphere", None, []),
            field("workup", None, []),
            field("purification", None, []),
        ], outcomes,
        [f"Table 1 entry {entry}; the common table-arrow reagents and loadings are represented in the structured participants and conditions."],
        unresolved,
    ))


# The optimized experiment is printed as Table 1 entry 11 and Table 2 entry 1, then detailed in the Experimental Section.
ps = common_participants("1a", "p-MeC6H4", "3a", E1 + E2, exact=True, include_4a=True)
ps += [
    participant("unidentified_mixture", "product", "unidentified mixture", E2,
                amounts=[field("mass", {"number": 7, "unit": "mg"}, E2)]),
]
ps_by_id = {p["entity_id"]: p for p in ps}
ps_by_id["major_product"]["amounts"] = [field("mass", {"number": 76, "unit": "mg"}, E2)]
records.append(record(
    "optimized_3a_table1_entry11_table2_entry1", "optimization_entry", E1 + E2 + E3, ps,
    [
        field("addition_order", "Cs2CO3, 4-iodotoluene, [Pd(PPh3)4], 1a, then CH3CN were added sequentially to an oven-dried Schlenk tube", E2),
        field("atmosphere", "argon", E2),
        field("temperature", {"number": 80, "unit": "°C"}, E1 + E2),
        field("time", {"number": 2, "unit": "h"}, E1 + E2),
        field("reaction_endpoint", "complete by TLC", E2),
        field("workup", "concentrated", E2),
        field("purification", "flash chromatography on silica gel", E2),
        field("eluent", "petroleum ether/ether = 10:1", E2),
    ],
    [
        field("isolated_yield_3a", {"number": 77, "unit": "%"}, E1 + E2, ["major_product"]),
        field("trans_cis_ratio_3a", "100:0", E1, ["major_product"]),
        field("reported_yield_4a", {"number": 7, "unit": "%", "qualifier": "lt", "raw_text": "<7%"}, E1 + E2, ["regioisomer_4a"]),
        field("yield_measurement_basis", "isolated product", E1 + E2, ["major_product", "regioisomer_4a"]),
    ],
    [
        "Table 1 entry 11, Table 2 entry 1, and the detailed synthesis of 3a describe the same optimized experiment and are merged here.",
        "The trans assignment was based on an approximately 5.2 Hz coupling between the two methine protons.",
        "Footnote 15 states that the spectrum of the unidentified mixture is complicated, so the conclusion assigning less than 7% 4a is not definite.",
    ],
    [
        "The 7 mg unidentified mixture is not equated with 4a because the source says that assignment is not definite.",
        "The candidate substrate constitution and all product structures/stereochemistry remain unverified.",
        "Supporting information is mentioned but was not supplied or associated.",
    ],
))


# Table 2 entries 2-16; entry 1 is the optimized record above.
t2 = [
    (2, "1a", "m-MeC6H4", 71, "3b"), (3, "1a", "Ph", 70, "3c"),
    (4, "1a", "p-MeOC6H4", 73, "3d"), (5, "1b", "p-MeC6H4", 75, "3e"),
    (6, "1b", "m-MeC6H4", 70, "3f"), (7, "1b", "Ph", 63, "3g"),
    (8, "1b", "p-MeOC6H4", 75, "3h"), (9, "1c", "p-MeC6H4", 72, "3i"),
    (10, "1c", "m-MeC6H4", 71, "3j"), (11, "1c", "Ph", 66, "3k"),
    (12, "1c", "p-MeOC6H4", 74, "3l"), (13, "1d", "p-MeC6H4", 68, "3m"),
    (14, "1d", "m-MeC6H4", 68, "3n"), (15, "1d", "Ph", 62, "3o"),
    (16, "1d", "p-MeOC6H4", 71, "3p"),
]
for entry, substrate, aryl, yld, product in t2:
    ps = common_participants(substrate, aryl, product, E2)
    records.append(record(
        f"table2_entry{entry}_{product}", "substrate_scope_entry", E2, ps,
        [
            field("temperature", {"number": 80, "unit": "°C"}, E2),
            field("time", {"number": 2, "unit": "h"}, E2),
            field("atmosphere", None, []),
            field("workup", None, []),
            field("purification", None, []),
        ],
        [
            field(f"isolated_yield_{product}", {"number": yld, "unit": "%"}, E2, ["major_product"]),
            field("diastereoselectivity", "trans product only", E2, ["major_product"]),
            field("yield_measurement_basis", "isolated product", E2, ["major_product"]),
        ],
        [f"Table 2 entry {entry}; the common Conditions A reagents and loadings are represented in the structured participants and conditions."],
        [
            "Absolute quantities, solvent volume, atmosphere, workup, and purification are not stated for this scope row.",
            "The candidate substrate constitution and product structure/stereochemistry remain unverified.",
            "Supporting information is mentioned but was not supplied or associated.",
        ],
    ))


# Table 3: enantioenriched substrates are distinct experiments from Table 2.
t3 = [
    (1, "1a", "p-MeC6H4", 74, 99.4, "3a"),
    (2, "1a", "p-MeOC6H4", 74, 99.4, "3d"),
    (3, "1b", "p-MeC6H4", 68, 98.5, "3e"),
    (4, "1b", "p-MeOC6H4", 75, 98.5, "3h"),
]
for entry, substrate, aryl, yld, ee, product in t3:
    ps = common_participants(substrate, aryl, f"(3S,4S)-{product}", E2)
    ps[0]["label"] = fact(f"(S)-{substrate}", E2)
    ps[0]["name"] = fact(f"enantioenriched (S)-2,3-allenyl hydrazine {substrate}", E2)
    ps[0]["amounts"].append(field("starting_material_ee", {"number": 99, "unit": "%", "qualifier": "gt", "raw_text": ">99% ee"}, E2))
    records.append(record(
        f"table3_entry{entry}_{product}", "substrate_scope_entry", E2, ps,
        [
            field("temperature", {"number": 80, "unit": "°C"}, E2),
            field("time", {"number": 2, "unit": "h"}, E2),
            field("atmosphere", None, []),
            field("workup", None, []),
            field("purification", None, []),
        ],
        [
            field(f"reported_yield_(3S,4S)-{product}", {"number": yld, "unit": "%"}, E2, ["major_product"]),
            field("product_ee", {"number": ee, "unit": "%"}, E2, ["major_product"]),
            field("ee_measurement_basis", "HPLC analysis; details stated to be in Supporting Information", E2, ["major_product"]),
            field("diastereoselectivity", "(S,S)-3 formed diastereoselectively", E2, ["major_product"]),
            field("yield_measurement_basis", None, []),
        ],
        [f"Table 3 entry {entry}; the common arrow reagents and loadings are represented in the structured participants and conditions."],
        [
            "Yield measurement basis, absolute quantities, solvent volume, atmosphere, workup, and purification are not stated for this row.",
            "The stated HPLC supporting information was not supplied or associated.",
            "The constitutional substrate candidate omits unverified stereochemical encoding; the product structure and absolute stereochemistry remain unverified.",
        ],
    ))


assert len(records) == 30
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")

ids_t1 = [f"{DOC}:table1_entry{i}" for i in range(1, 11)] + [f"{DOC}:optimized_3a_table1_entry11_table2_entry1"]
ids_t2 = [f"{DOC}:optimized_3a_table1_entry11_table2_entry1"] + [f"{DOC}:table2_entry{e}_{p}" for e, _, _, _, p in t2]
ids_t3 = [f"{DOC}:table3_entry{e}_{p}" for e, _, _, _, _, p in t3]
coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1,
            "state": "attempted",
            "regions": [
                {
                    "region": "title, introduction, and present-paper discussion in both columns",
                    "finding": "Introduction and cited background methods were classified as narrative prior work, not row-level present-paper experiments; prose introducing the base screen is merged into Table 1 rows.",
                    "evidence_ids": [P1I, P1T],
                },
                {
                    "region": "right-column Table 1, reaction arrow, rows 1-11, and footnotes a-d",
                    "finding": "Eleven independent optimization conditions inventoried; entry 11 is merged with Table 2 entry 1 and the detailed 3a procedure because they report the same optimized experiment.",
                    "evidence_ids": [P1I, P1T],
                },
                {
                    "region": "lower-left Supporting Information availability statement",
                    "finding": "Online availability statement only; no SI source was supplied or explicitly associated.",
                    "evidence_ids": [P1I, P1T],
                },
            ],
            "record_ids": ids_t1,
            "unresolved": [
                "Most optimization rows omit absolute scale, solvent volume, atmosphere, workup, and purification.",
                "Table 1 entries 2 and 3 report n.d. because of complicated mixtures, without product-resolved results.",
                "All complex structures and stereochemical assignments remain machine candidates requiring expert review.",
            ],
        },
        {
            "page": 2,
            "state": "attempted",
            "regions": [
                {
                    "region": "upper-left prose completing Conditions A and discussing stereochemistry/byproduct 4a",
                    "finding": "Common optimized conditions, trans assignment, and less-than-7% 4a statement linked to the merged optimized 3a record.",
                    "evidence_ids": [P2I, P2T],
                },
                {
                    "region": "left-column Table 2, reaction arrow, rows 1-16, and isolated-yield footnote",
                    "finding": "Sixteen scope rows inventoried; entry 1 is the same optimized 3a experiment as Table 1 entry 11, while entries 2-16 remain independent substrate/aryl-halide cases.",
                    "evidence_ids": [P2I, P2T],
                },
                {
                    "region": "upper-right Table 3, reaction arrow, rows 1-4, and HPLC footnote",
                    "finding": "Four enantioenriched-substrate experiments extracted independently with yields and product ee values; the unavailable SI was not inferred.",
                    "evidence_ids": [P2I, P2T],
                },
                {
                    "region": "right-column Experimental Section, Synthesis of 3a",
                    "finding": "Exact quantities, argon atmosphere, staged addition, 80 °C/2 h, TLC endpoint, concentration, chromatography, product mass, and isolated yield merged into the optimized 3a record.",
                    "evidence_ids": [P2I, P2T],
                },
            ],
            "record_ids": list(dict.fromkeys(ids_t2 + ids_t3)),
            "unresolved": [
                "Table 2 entries 2-16 and all Table 3 rows omit absolute quantities, solvent volume, atmosphere, workup, and purification.",
                "Table 3 does not explicitly state yield measurement basis; HPLC details are in unassociated SI.",
                "Product structures, relative stereochemistry, and absolute stereochemistry remain unverified.",
            ],
        },
        {
            "page": 3,
            "state": "attempted",
            "regions": [
                {
                    "region": "reference list across both columns",
                    "finding": "References only; cited publications were not treated as present-paper experiments or associated sources.",
                    "evidence_ids": [P3I, P3T],
                },
                {
                    "region": "right-column footnote 15",
                    "finding": "Footnote qualifies the optimized-reaction assignment of less than 7% 4a as not definite because the unidentified-mixture spectrum is complicated; linked to the merged optimized 3a record.",
                    "evidence_ids": [P3I, P3T, P2T],
                },
            ],
            "record_ids": [f"{DOC}:optimized_3a_table1_entry11_table2_entry1"],
            "unresolved": [
                "The cited literature was not supplied as associated source material and was not mined for experiment-level details.",
                "The identity and amount of 4a in the optimized experiment remain uncertain by the authors' own footnote.",
            ],
        },
    ],
}
COVERAGE.parent.mkdir(parents=True, exist_ok=True)
COVERAGE.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

tasks = json.loads(TASKS.read_text())
for task in tasks:
    if task["document_id"] == DOC and task["task_id"] in {P1T, P2T, P3T}:
        task["state"] = "attempted"
TASKS.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"records": len(records), "coverage_pages": [1, 2, 3]}, ensure_ascii=False))
