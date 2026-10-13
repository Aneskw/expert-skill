#!/usr/bin/env python3
"""Build evidence-linked records for DOI 10.1021/ol8012815, PDF pages 1--4."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "runs/current/raw_model/records_pages_0001_0004.json"
COVERAGE_OUT = ROOT / "runs/current/coverage/pages_0001_0004.json"
DOC = "doc_4451793c559aa6b1"


def ev(page):
    return [f"{DOC}:page{page}:text", f"{DOC}:page{page}:image"]


def fact(value, evidence):
    return {
        "value": value,
        "evidence_ids": list(evidence) if value is not None else [],
        "verification": "source_checked" if value is not None else "missing",
    }


def qty(number, unit, **extra):
    value = {"number": number, "unit": unit}
    value.update(extra)
    return value


def participant(entity_id, role, label, evidence, name=None, smiles=None, amounts=None):
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


def field(name, value, evidence, targets=None):
    item = {"name": name, "fact": fact(value, evidence)}
    if targets:
        item["target_entity_ids"] = targets
    return item


def record(suffix, page, kind, participants, steps, outcomes, notes, unresolved):
    evidence = ev(page)
    return {
        "record_id": f"{DOC}:{suffix}",
        "document_id": DOC,
        "source_reaction_id": suffix,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": evidence,
        "participants": participants,
        "steps": steps,
        "outcomes": outcomes,
        "notes": [fact(note, evidence) for note in notes],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved,
        },
    }


STARTING = {
    "4a": ("Ph", "Me", "CCOC(=O)C(C)=C=Cc1ccccc1"),
    "4b": ("Ph", "n-Pr", "CCOC(=O)C(CCC)=C=Cc1ccccc1"),
    "4c": ("p-FC6H4", "Me", "CCOC(=O)C(C)=C=Cc1ccc(F)cc1"),
    "4d": ("p-ClC6H4", "Me", "CCOC(=O)C(C)=C=Cc1ccc(Cl)cc1"),
    "4e": ("p-BrC6H4", "Me", "CCOC(=O)C(C)=C=Cc1ccc(Br)cc1"),
    "4f": ("p-MeOC6H4", "Me", "CCOC(=O)C(C)=C=Cc1ccc(OC)cc1"),
}

ARYL = {
    "Ph": "c1ccccc1",
    "p-FC6H4": "c1ccc(F)cc1",
    "p-ClC6H4": "c1ccc(Cl)cc1",
    "p-BrC6H4": "c1ccc(Br)cc1",
    "p-MeOC6H4": "c1ccc(OC)cc1",
}

R2_BRANCH = {"Me": "C", "n-Pr": "CCC"}
ACYL = {
    "Me": ("acetyl chloride", "CC(=O)Cl", "allyl acetate", "CC(=O)OCC=C", "C(=O)C"),
    "Bn": ("phenylacetyl chloride", "O=C(Cl)Cc1ccccc1", "allyl phenylacetate", "O=C(Cc1ccccc1)OCC=C", "C(=O)Cc1ccccc1"),
    "Ph": ("benzoyl chloride", "O=C(Cl)c1ccccc1", "allyl benzoate", "O=C(OCC=C)c1ccccc1", "C(=O)c1ccccc1"),
}


def product_smiles(start_label, electrophile_branch):
    r1, r2, _ = STARTING[start_label]
    return f"CCOC(=O)C(C)({electrophile_branch})C({R2_BRANCH[r2]})=C{ARYL[r1]}"


def amount_field(name, value, evidence):
    return field(name, value, evidence)


def common_stage_participants(page, start_label, include_dienolate_amount=True):
    evidence = ev(page)
    r1, r2, start_smiles = STARTING[start_label]
    parts = [
        participant("allenoate", "reactant", start_label, evidence,
                    f"2,3-allenoate {start_label} (R1={r1}, R2={r2})", start_smiles),
        participant("methylmagnesium_chloride", "reagent", "CH3MgCl", evidence,
                    "methylmagnesium chloride", "C[Mg]Cl",
                    [amount_field("solution_concentration", qty(3, "M"), evidence)]),
        participant("iron_catalyst", "catalyst", "Fe(acac)3", evidence,
                    "iron(III) acetylacetonate", None,
                    [amount_field("catalyst_loading", qty(5, "mol%"), evidence)]),
        participant("thf", "solvent", "THF", evidence, "tetrahydrofuran", "C1CCOC1"),
    ]
    if include_dienolate_amount:
        parts.append(participant(
            "dienolate", "reactant", f"in situ magnesium dienolate 5 from {start_label}", evidence,
            None, None, [amount_field("amount", qty(0.4, "mmol"), evidence)]
        ))
    return parts


def stage1(page, start_label):
    evidence = ev(page)
    return {
        "step_id": "generate_magnesium_dienolate",
        "participant_ids": ["allenoate", "methylmagnesium_chloride", "iron_catalyst", "thf"],
        "conditions": [
            field("temperature", qty(-78, "°C"), evidence),
            field("time", qty(1, "h"), evidence),
            field("operation", f"Generate magnesium dienolate 5 in situ from {start_label}.", evidence),
            field("atmosphere", None, evidence),
        ],
    }


records = []

# Page 1: two non-experimental, generic reaction summaries.
e1 = ev(1)
records.append(record(
    "graphical_abstract_controlled_dienolate_trapping", 1, "general_scheme",
    [
        participant("generic_allenoate", "reactant", "4-aryl-2,3-allenoate (R1/R2 generic)", e1),
        participant("methylmagnesium_chloride", "reagent", "CH3MgCl", e1, "methylmagnesium chloride", "C[Mg]Cl",
                    [amount_field("solution_concentration", qty(3, "M"), e1)]),
        participant("iron_catalyst", "catalyst", "Fe(acac)3", e1, "iron(III) acetylacetonate", None,
                    [amount_field("catalyst_loading", qty(5, "mol%"), e1)]),
        participant("generic_electrophile", "reagent", "E+ (acyl or allylic group)", e1),
        participant("generic_z_product", "product", "Z alk-3-enoate", e1),
        participant("generic_e_product", "product", "E alk-3-enoate", e1),
    ],
    [{
        "step_id": "graphical_summary",
        "participant_ids": ["generic_allenoate", "methylmagnesium_chloride", "iron_catalyst", "generic_electrophile", "generic_z_product", "generic_e_product"],
        "conditions": [field("temperature", qty(-78, "°C"), e1), field("time", qty(1, "h"), e1)],
    }],
    [],
    ["Graphical abstract summarizes controlled direct trapping versus isomerization then trapping; it is not an individual experimental run."],
    ["R1, R2, electrophile identity, and the branch-specific conditions are generic; no yield is reported in this graphic."],
))
records.append(record(
    "scheme1_generic_1_3_dienolate_reactivity", 1, "general_scheme",
    [
        participant("generic_dienolate", "reactant", "1,3-dienolate 1", e1),
        participant("generic_electrophile", "reagent", "E+", e1),
        participant("alpha_product", "product", "alpha-substituted product 2", e1),
        participant("gamma_product", "product", "gamma-substituted product 3", e1),
    ],
    [{"step_id": "generic_electrophilic_trapping", "participant_ids": ["generic_dienolate", "generic_electrophile", "alpha_product", "gamma_product"], "conditions": []}],
    [],
    ["Scheme 1 is a generic introductory reaction pattern and is associated with cited background literature, not a present-paper experiment."],
    ["Generic R/M/E groups, conditions, and yields are not specified."],
))

# Page 2: explicit prior-work result discussed separately from the current Table 1 row.
e2 = ev(2)
prior_parts = common_stage_participants(2, "4a")
prior_parts += [
    participant("acetyl_chloride", "reagent", "CH3COCl", e2, "acetyl chloride", "CC(=O)Cl"),
    participant("product", "product", "Z-6a", e2, "Z-6a (R1=Ph, R2=Me, R3=Me)", product_smiles("4a", "C(=O)C")),
]
records.append(record(
    "prior_ref5_z6a_61pct", 2, "literature_example", prior_parts,
    [stage1(2, "4a"), {
        "step_id": "prior_acylation",
        "participant_ids": ["dienolate", "acetyl_chloride", "product"],
        "conditions": [field("temperature", qty(-78, "°C"), e2), field("time", None, e2), field("atmosphere", None, e2), field("workup", None, e2), field("purification", None, e2)],
    }],
    [field("reported_yield", qty(61, "%"), e2, ["product"]), field("yield_measurement_basis", None, e2, ["product"])],
    ["The prose marks this 61% Z-6a result as 'originally noted' in reference 5; it is retained as a literature example and not merged with current Table 1 entry 1 (68%)."],
    ["Electrophile amount, trapping duration, yield basis, atmosphere, workup, and purification are not stated in this prior-work sentence."],
))

# Page 2 Table 1: each A/B cell is an independent experiment.
table1 = [
    (1, "4a", "Me", 68, ">99/1", 50, "95/5", "6a"),
    (2, "4a", "Bn", 87, ">99/1", 47, ">98/2", "6b"),
    (3, "4a", "Ph", 70, ">99/1", 57, ">98/2", "6c"),
    (4, "4b", "Me", 69, ">99/1", 50, ">98/2", "6d"),
    (5, "4c", "Me", 76, ">99/1", 69, "98/2", "6e"),
    (6, "4d", "Me", 84, ">99/1", 50, "98/2", "6f"),
    (7, "4e", "Me", 87, ">99/1", 62, "97/3", "6g"),
]

for entry, start, r3, yield_a, ratio_a, yield_b, ratio_b, code in table1:
    acyl_name, acyl_smiles, ester_name, ester_smiles, branch = ACYL[r3]
    for condition, reagent_label, reagent_name, reagent_smiles, product_label, product_geom, yld, ratio in [
        ("A", f"R3COCl (R3={r3})", acyl_name, acyl_smiles, f"Z-{code}", "Z", yield_a, ratio_a),
        ("B", f"allyl O2CR3 (R3={r3})", ester_name, ester_smiles, f"E-{code}", "E", yield_b, ratio_b),
    ]:
        parts = common_stage_participants(2, start)
        parts += [
            participant("electrophile", "reagent", reagent_label, e2, reagent_name, reagent_smiles,
                        [amount_field("amount", qty(2, "mmol"), e2)]),
            participant("product", "product", product_label, e2,
                        f"{product_label} (R1={STARTING[start][0]}, R2={STARTING[start][1]}, R3={r3})",
                        product_smiles(start, branch)),
        ]
        if condition == "A":
            trap_conditions = [
                field("temperature", qty(-78, "°C"), e2),
                field("time", qty(1, "h"), e2),
                field("atmosphere", None, e2), field("workup", None, e2), field("purification", None, e2),
            ]
        else:
            trap_conditions = [
                field("initial_temperature", qty(-78, "°C"), e2),
                field("warm_to", "r.t.", e2),
                field("time", "overnight", e2),
                field("atmosphere", None, e2), field("workup", None, e2), field("purification", None, e2),
            ]
        outcomes = [
            field("isolated_yield", qty(yld, "%"), e2, ["product"]),
            field("yield_measurement_basis", "isolated yield", e2, ["product"]),
            field(f"{product_geom}_to_opposite_isomer_ratio", ratio, e2, ["product"]),
            field("ratio_measurement_basis", "1H NMR analysis of the crude products", e2, ["product"]),
        ]
        records.append(record(
            f"table1_entry{entry}_condition_{condition.lower()}_{product_label.lower().replace('-', '')}",
            2, "substrate_scope_entry", parts,
            [stage1(2, start), {"step_id": "electrophilic_trapping", "participant_ids": ["dienolate", "electrophile", "product"], "conditions": trap_conditions}],
            outcomes,
            [f"Table 1 entry {entry}, Conditions {condition}; product geometry is retained in the source label and selectivity outcome."],
            ["Atmosphere, workup, and purification are not stated in the covered main text; product and starting-material candidate structures remain unverified."],
        ))

# Page 3 Table 2.
e3 = ev(3)
table2 = [
    (1, "4a", "H", "H", 67, "96/4", 51, "96/4", "7a"),
    (2, "4c", "H", "H", 74, "94/6", 72, "97/3", "7b"),
    (3, "4d", "H", "H", 66, "96/4", 71, "97/3", "7c"),
    (4, "4e", "H", "H", 80, "93/7", 65, "97/3", "7d"),
    (5, "4f", "H", "H", 72, "98/2", 53, "97/3", "7e"),
    (6, "4a", "H", "Ph", 61, "89/11", 58, ">99/1", "7f"),
    (7, "4b", "H", "Ph", 58, "91/9", 39, ">99/1", "7g"),
    (8, "4a", "Ph", "H", 77, "94/6", 39, "table dash (—)", "7h"),
]


def allylic_reagent(r3, r4, acetate):
    if (r3, r4) == ("H", "H"):
        return (("allyl acetate", "CC(=O)OCC=C") if acetate else ("allyl bromide", "C=CCBr"))
    if (r3, r4) == ("H", "Ph"):
        return (("1-phenylallyl acetate", "CC(=O)OC(c1ccccc1)C=C") if acetate else ("1-phenylallyl bromide", "C=CC(Br)c1ccccc1"))
    return (("cinnamyl acetate", "CC(=O)OCC=Cc1ccccc1") if acetate else ("cinnamyl bromide", "BrCC=Cc1ccccc1"))


def allyl_branch(r3, r4):
    if (r3, r4) == ("H", "H"):
        return "CC=C"
    if (r3, r4) == ("H", "Ph"):
        return "C(c1ccccc1)C=C"
    return "CC=Cc1ccccc1"


for entry, start, r3, r4, yield_c, ratio_c, yield_d, ratio_d, code in table2:
    for condition, acetate, yld, ratio, geom in [
        ("C", True, yield_c, ratio_c, "Z"),
        ("D", False, yield_d, ratio_d, "E"),
    ]:
        reagent_name, reagent_smiles = allylic_reagent(r3, r4, acetate)
        product_label = f"{geom}-{code}"
        parts = common_stage_participants(3, start)
        parts += [
            participant("allylic_reagent", "reagent", f"allylic {'acetate' if acetate else 'bromide'} (R3={r3}, R4={r4})", e3,
                        reagent_name, reagent_smiles, [amount_field("equivalents", qty(5, "equiv"), e3)]),
            participant("product", "product", product_label, e3,
                        f"{product_label} (R1={STARTING[start][0]}, R2={STARTING[start][1]}, R3={r3}, R4={r4})",
                        product_smiles(start, allyl_branch(r3, r4))),
        ]
        if condition == "C":
            parts.append(participant("palladium_catalyst", "catalyst", "Pd(PPh3)4", e3, "tetrakis(triphenylphosphine)palladium(0)", None,
                                     [amount_field("catalyst_loading", qty(5, "mol%"), e3)]))
            trap_ids = ["dienolate", "allylic_reagent", "palladium_catalyst", "product"]
            conditions = [
                field("initial_temperature", qty(-78, "°C"), e3),
                field("time_at_initial_temperature", qty(1, "h"), e3),
                field("warm_to", "r.t.", e3),
                field("post_warming_time", "overnight", e3),
                field("atmosphere", None, e3), field("workup", None, e3), field("purification", None, e3),
            ]
        else:
            parts.append(participant("copper_catalyst", "catalyst", "CuI", e3, "copper(I) iodide", "[Cu]I",
                                     [amount_field("catalyst_loading", qty(10, "mol%"), e3)]))
            trap_ids = ["dienolate", "allylic_reagent", "copper_catalyst", "product"]
            conditions = [
                field("temperature", "r.t.", e3),
                field("time", qty(2, "h"), e3),
                field("atmosphere", None, e3), field("workup", None, e3), field("purification", None, e3),
            ]
        outcomes = [
            field("isolated_yield", qty(yld, "%"), e3, ["product"]),
            field("yield_measurement_basis", "isolated yield", e3, ["product"]),
            field(f"{geom}_to_opposite_isomer_ratio", ratio, e3, ["product"]),
            field("ratio_measurement_basis", "1H NMR analysis of the crude products", e3, ["product"]),
        ]
        notes = [f"Table 2 entry {entry}, Conditions {condition}; the overall starting-allenoate/dienolate stage and allylic trapping are represented separately."]
        unresolved = ["Atmosphere, workup, and purification are not stated in the covered main text; candidate structures and stereochemistry remain unverified."]
        if entry == 8 and condition == "D":
            notes.append("Footnote d states that the other isomer was not isolated; the ratio cell is preserved as a table dash and is not converted to zero or a numeric selectivity.")
            unresolved.append("No numeric E/Z ratio is reported for Table 2 entry 8 under Conditions D.")
        records.append(record(
            f"table2_entry{entry}_condition_{condition.lower()}_{product_label.lower().replace('-', '')}",
            3, "substrate_scope_entry", parts,
            [stage1(3, start), {"step_id": "allylic_trapping", "participant_ids": trap_ids, "conditions": conditions}],
            outcomes, notes, unresolved,
        ))

# Page 4 Scheme 2: proposed stereochemical rationale, not an experiment.
e4 = ev(4)
records.append(record(
    "scheme2_stereochemical_isomerization_rationale", 4, "mechanism",
    [
        participant("z_dienoate", "reactant", "Z-1,3-dienoate", e4),
        participant("anti_allyl_magnesium", "unspecified_agent", "anti-allylic MgCl species", e4),
        participant("syn_allyl_metal", "unspecified_agent", "syn-allylic metal species (M=MgCl or Cu)", e4),
        participant("e_dienoate", "product", "E-1,3-dienoate", e4),
        participant("z_products", "product", "Z-6 or Z-7", e4),
        participant("e_products", "product", "E-6 or E-7", e4),
    ],
    [{
        "step_id": "proposed_isomerization_network",
        "participant_ids": ["z_dienoate", "anti_allyl_magnesium", "syn_allyl_metal", "e_dienoate", "z_products", "e_products"],
        "conditions": [field("operation", "Proposed interconversion mediated by ligand (L) or metal (M).", e4)],
    }],
    [],
    ["Scheme 2 is the authors' rationale for stereoselectivity and is classified as a proposed mechanism, not an observed experimental run."],
    ["Generic R1/R2/L/M groups and organometallic structures are not fully specified; no kinetic or yield data are reported for the proposed intermediates."],
))

# Page 4 Scheme 3: three distinct present-paper control experiments.
scheme3 = [
    ("acyl_chloride_at_rt", "acetyl_chloride", "reagent", "CH3COCl", "acetyl chloride", "CC(=O)Cl", None,
     "6a", product_smiles("4a", "C(=O)C"), 70, "Z/E", "96/4"),
    ("allyl_acetate_at_rt_no_pd", "allyl_acetate", "reagent", "allyl acetate", "allyl acetate", "CC(=O)OCC=C", None,
     "6a", product_smiles("4a", "C(=O)C"), 37, "E/Z", "76/24"),
    ("pd_allylation_at_rt", "allyl_acetate", "reagent", "allyl acetate", "allyl acetate", "CC(=O)OCC=C", "pd",
     "7a", product_smiles("4a", "CC=C"), 71, "Z/E", "69/31"),
]
for suffix, electrophile_id, electrophile_role, electrophile_label, electrophile_name, electrophile_smiles, catalyst, product_label, prod_smiles, yld, ratio_name, ratio in scheme3:
    parts = common_stage_participants(4, "4a", include_dienolate_amount=False)
    parts += [
        participant(electrophile_id, electrophile_role, electrophile_label, e4, electrophile_name, electrophile_smiles),
        participant("product", "product", product_label, e4, f"Scheme 3 product {product_label}", prod_smiles),
    ]
    trap_ids = [electrophile_id, "product"]
    if catalyst == "pd":
        parts.append(participant("palladium_catalyst", "catalyst", "Pd(PPh3)4", e4, "tetrakis(triphenylphosphine)palladium(0)", None,
                                 [amount_field("catalyst_loading", qty(5, "mol%"), e4)]))
        trap_ids.append("palladium_catalyst")
    steps = [stage1(4, "4a"), {
        "step_id": "warm_then_trap_at_room_temperature",
        "participant_ids": trap_ids,
        "conditions": [
            field("operation", "Warm the in situ dienolate from -78 °C to r.t. naturally, then add the indicated electrophile at r.t.", e4),
            field("temperature", "r.t.", e4),
            field("time", None, e4), field("atmosphere", None, e4), field("workup", None, e4), field("purification", None, e4),
        ],
    }]
    outcomes = [
        field("NMR_yield", qty(yld, "%"), e4, ["product"]),
        field("yield_measurement_basis", "NMR", e4, ["product"]),
        field(f"{ratio_name.replace('/', '_to_')}_ratio", ratio, e4, ["product"]),
        field("ratio_measurement_basis", "NMR", e4, ["product"]),
    ]
    records.append(record(
        f"scheme3_{suffix}", 4, "reported_experiment", parts, steps, outcomes,
        ["Scheme 3 mechanistic-study condition; electrophile addition occurs only after the in situ dienolate has warmed to room temperature."],
        ["Reaction scale, post-addition duration, atmosphere, workup, and purification are not stated; candidate product structure and stereochemical assignment remain unverified."],
    ))


OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")


def page_record_ids(page):
    page_image = f"{DOC}:page{page}:image"
    return [item["record_id"] for item in records if page_image in item["evidence_ids"]]


coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1,
            "state": "attempted",
            "regions": [
                {
                    "region": "title, graphical abstract, and abstract in the upper and middle page",
                    "finding": "The graphical abstract is a generic present-paper summary of Fe-catalyzed dienolate generation followed by direct trapping or isomerization/trapping; classified as a general scheme, not an individual experiment.",
                    "evidence_ids": [f"{DOC}:page1:image", f"{DOC}:page1:text"],
                },
                {
                    "region": "Scheme 1 at lower right",
                    "finding": "Generic alpha/gamma electrophilic trapping of a 1,3-dienolate, presented as introductory chemistry associated with cited background literature; classified as a general scheme.",
                    "evidence_ids": [f"{DOC}:page1:image", f"{DOC}:page1:text"],
                },
                {
                    "region": "introduction columns below the abstract",
                    "finding": "Background statements about prior protonation, alkylation, and aldol reactions lack experiment-specific structures/conditions and were not expanded into additional records.",
                    "evidence_ids": [f"{DOC}:page1:image", f"{DOC}:page1:text"],
                },
            ],
            "record_ids": page_record_ids(1),
            "unresolved": [
                "Graphical-abstract R groups and branch-specific electrophile conditions are generic.",
                "No SI file is supplied or explicitly associated; the main-text statement of SI availability does not establish an association.",
            ],
        },
        {
            "page": 2,
            "state": "attempted",
            "regions": [
                {
                    "region": "Table 1 reaction diagram, seven rows, and footnotes in the upper half",
                    "finding": "Fourteen independent substrate-scope experiments extracted: seven acyl-chloride Conditions A records and seven allyl-carboxylate Conditions B records. Shared scale, electrophile amount, temperature program, isolated-yield basis, and crude-1H-NMR ratio basis were applied to each appropriate row.",
                    "evidence_ids": [f"{DOC}:page2:image", f"{DOC}:page2:text"],
                },
                {
                    "region": "left-column paragraph beginning 'As originally noted'",
                    "finding": "The explicitly prior-reported reference-5 Z-6a result (61%) was classified as a literature example and kept separate from current Table 1 entry 1 (68%).",
                    "evidence_ids": [f"{DOC}:page2:image", f"{DOC}:page2:text"],
                },
                {
                    "region": "Figure 1 NOE drawings and surrounding discussion in the lower half",
                    "finding": "NOE evidence supports the source's Z/E labels for 6a and 7a but is not an additional reaction; it remains linked through same-page evidence to the corresponding records.",
                    "evidence_ids": [f"{DOC}:page2:image", f"{DOC}:page2:text"],
                },
            ],
            "record_ids": page_record_ids(2),
            "unresolved": [
                "The prior 61% result omits electrophile amount, trapping duration, yield basis, atmosphere, workup, and purification.",
                "Table 1 omits atmosphere, workup, and purification; candidate structures and stereochemistry remain unverified.",
            ],
        },
        {
            "page": 3,
            "state": "attempted",
            "regions": [
                {
                    "region": "Table 2 reaction diagram, eight rows, and footnotes in the upper half",
                    "finding": "Sixteen independent substrate-scope experiments extracted: eight Pd(PPh3)4/allylic-acetate Conditions C records and eight CuI/allylic-bromide Conditions D records, including row-specific R groups, isolated yields, and selectivity.",
                    "evidence_ids": [f"{DOC}:page3:image", f"{DOC}:page3:text"],
                },
                {
                    "region": "Table 2 entry 8 Conditions D ratio cell and footnote d",
                    "finding": "The table dash was preserved as a source marker; footnote d says the other isomer was not isolated, so no numeric E/Z ratio was invented.",
                    "evidence_ids": [f"{DOC}:page3:image", f"{DOC}:page3:text"],
                },
                {
                    "region": "Figure 2 ORTEP and lower-page discussion",
                    "finding": "The Z-7h crystal structure and narrative discussion support Table 2 identities/selectivity but do not constitute additional reactions. The final paragraph begins the proposed rationale continued on page 4.",
                    "evidence_ids": [f"{DOC}:page3:image", f"{DOC}:page3:text"],
                },
            ],
            "record_ids": page_record_ids(3),
            "unresolved": [
                "Table 2 omits atmosphere, workup, and purification.",
                "Entry 8 Conditions D has no numeric selectivity ratio; candidate structures and stereochemistry remain unverified.",
            ],
        },
        {
            "page": 4,
            "state": "attempted",
            "regions": [
                {
                    "region": "Scheme 2 at upper left and its explanatory prose",
                    "finding": "Proposed Z/E dienolate isomerization through anti-allylic MgCl and syn-allylic metal species; classified as mechanism, not an observed experiment.",
                    "evidence_ids": [f"{DOC}:page4:image", f"{DOC}:page4:text"],
                },
                {
                    "region": "Scheme 3 at upper right",
                    "finding": "Three distinct room-temperature trapping/control experiments extracted: acetyl chloride to 6a (70% NMR, Z/E 96/4), allyl acetate without Pd to 6a (37% NMR, E/Z 76/24), and Pd(PPh3)4/allyl acetate to 7a (71% NMR, Z/E 69/31).",
                    "evidence_ids": [f"{DOC}:page4:image", f"{DOC}:page4:text"],
                },
                {
                    "region": "conclusion, acknowledgements, and Supporting Information Available notice",
                    "finding": "No additional experiment is reported. The notice says procedures and spectra are available online, but no SI file is supplied here, so SI association remains unestablished.",
                    "evidence_ids": [f"{DOC}:page4:image", f"{DOC}:page4:text"],
                },
            ],
            "record_ids": page_record_ids(4),
            "unresolved": [
                "Scheme 3 omits scale, post-addition duration, atmosphere, workup, and purification.",
                "Generic mechanism structures and all candidate stereochemical structures remain unverified.",
            ],
        },
    ],
}
COVERAGE_OUT.parent.mkdir(parents=True, exist_ok=True)
COVERAGE_OUT.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({
    "output": str(OUT.relative_to(ROOT)),
    "coverage": str(COVERAGE_OUT.relative_to(ROOT)),
    "records": len(records),
}, ensure_ascii=False))
