#!/usr/bin/env python3
"""Build evidence-linked machine records for Shu, Yu & Ma (2009), PDF pages 1–4."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "runs/current/raw_model/records_pages_0001_0004.json"
COVERAGE = ROOT / "runs/current/coverage/pages_0001_0004.json"
TASKS = ROOT / "runs/current/tasks.json"
DOC = "doc_d2c6112d1354f749"


def ev(page):
    return [f"{DOC}:page{page}:image", f"{DOC}:page{page}:text"]


def uniq(values):
    return list(dict.fromkeys(values))


def fact(value, evidence):
    return {
        "value": value,
        "evidence_ids": uniq(evidence) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def qty(number, unit, **extra):
    value = {"number": number, "unit": unit}
    value.update(extra)
    return value


def rng(minimum, maximum, unit, raw_text):
    return {"minimum": minimum, "maximum": maximum, "unit": unit, "raw_text": raw_text}


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


def record(suffix, kind, evidence, participants, steps, outcomes, notes, unresolved):
    return {
        "record_id": f"{DOC}:{suffix}",
        "document_id": DOC,
        "source_reaction_id": suffix,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": uniq(evidence),
        "participants": participants,
        "steps": steps,
        "outcomes": outcomes,
        "notes": [fact(value, evs) for value, evs in notes],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved,
        },
    }


smiles = {
    "1a": "Cc1ccc(S(=O)(=O)Nc2ccccc2I)cc1",
    "1b": "Cc1ccc(S(=O)(=O)Nc2c(I)ccc(Cl)c2)cc1",
    "1c": "Cc1ccc(S(=O)(=O)Nc2c(I)cc(F)cc2)cc1",
    "2a": "C=C=CCCCCCCC",
    "2b": "C=C=CCCN1C(=O)c2ccccc2C1=O",
    "2c": "C=C=CCCOCOC",
    "2f": "C=C=CCCCCCCCC",
    "2g": "C=C=CCCCCC",
    "2h": "CCCC=C=CCCC",
    "2i": "C=C=CCCCCCC",
    "2j": "C=C=CCCCCCCCCC",
    "2k": "C=C=CCCCCCCCCCC",
    "3aa": "Cc1ccc(S(=O)(=O)N2c3ccccc3C(=C)C2CCCCCCC)cc1",
    "3ab": "Cc1ccc(S(=O)(=O)N2c3ccccc3C(=C)C2CCN4C(=O)c5ccccc5C4=O)cc1",
    "3ac": "Cc1ccc(S(=O)(=O)N2c3ccccc3C(=C)C2CCOCOC)cc1",
    "3af": "Cc1ccc(S(=O)(=O)N2c3ccccc3C(=C)C2CCCCCCCC)cc1",
    "3ag": "Cc1ccc(S(=O)(=O)N2c3ccccc3C(=C)C2CCCCC)cc1",
    "3ah": "Cc1ccc(S(=O)(=O)N2c3ccccc3C(=CCCC)C2CCC)cc1",
    "3ai": "Cc1ccc(S(=O)(=O)N2c3ccccc3C(=C)C2CCCCCC)cc1",
    "3aj": "Cc1ccc(S(=O)(=O)N2c3ccccc3C(=C)C2CCCCCCCCC)cc1",
    "3ak": "Cc1ccc(S(=O)(=O)N2c3ccccc3C(=C)C2CCCCCCCCCC)cc1",
    "ag3po4": "[Ag+].[Ag+].[Ag+].[O-]P([O-])([O-])=O",
    "dmf": "CN(C)C=O",
    "toluene": "Cc1ccccc1",
    "dce": "ClCCCl",
    "thf": "C1CCOC1",
    "dioxane": "C1COCCO1",
}


records = []

# Page 1 Scheme 1 is a conceptual comparison, not a performed experiment.
p1 = ev(1)
records.append(record(
    "scheme1_conceptual_allylation_protocols",
    "general_scheme",
    p1,
    [
        participant("scheme1_generic_substrate", "reactant", "generic allylic substrate/allene", None, None, p1),
        participant("scheme1_generic_nucleophile", "reactant", "Nu−", "generic nucleophile", None, p1),
        participant("scheme1_generic_metal_ligand", "catalyst", "M(L*)", "generic chiral metal complex", None, p1),
        participant("scheme1_generic_product", "product", "generic chiral cyclic allylation product", None, None, p1),
    ],
    [{
        "step_id": "conceptual_comparison",
        "participant_ids": ["scheme1_generic_substrate", "scheme1_generic_nucleophile", "scheme1_generic_metal_ligand", "scheme1_generic_product"],
        "conditions": [],
    }],
    [],
    [
        ("The upper pathway is labeled a well-established process; the lower allene/carbometallation pathway is labeled as awaiting new chiral ligands.", p1),
        ("Scheme 1 is a generic conceptual comparison with LG, Nu, R, n, M and L* variables, not a batch-specific experiment.", p1),
    ],
    ["Generic variables prevent complete structures and experiment-level conditions from being assigned."],
))


ligands = {
    1: ("(Ra,S,S)-L2", "spiro-BOX L2, R = Bn"),
    2: ("(Sa,S,S)-L2", "spiro-BOX L2, R = Bn"),
    3: ("(Ra,S,S)-L3", "spiro-BOX L3, R = Ph"),
    4: ("(Ra,S,S)-L4", "spiro-BOX L4, R = i-Pr"),
    5: ("(Ra,S,S)-L5", "spiro-BOX L5, R = Me"),
    6: ("(Ra,S,S)-L6", "spiro-BOX L6, R = alpha-naphthylmethyl"),
    7: ("(Ra,S,S)-L7", "spiro-BOX L7, R = beta-naphthylmethyl"),
    8: ("(Ra,S,S)-L7", "spiro-BOX L7, R = beta-naphthylmethyl"),
    9: ("(Ra,S,S)-L7", "spiro-BOX L7, R = beta-naphthylmethyl"),
    10: ("(Ra,S,S)-L7", "spiro-BOX L7, R = beta-naphthylmethyl"),
    11: ("(Ra,S,S)-L7", "spiro-BOX L7, R = beta-naphthylmethyl"),
    12: ("(Ra,S,S)-L7", "spiro-BOX L7, R = beta-naphthylmethyl"),
    13: ("(Ra,S,S)-L7", "spiro-BOX L7, R = beta-naphthylmethyl"),
    14: ("(Ra,S,S)-L7", "spiro-BOX L7, R = beta-naphthylmethyl"),
}

table1 = {
    1: ("DMF", 90, 24, 74, None, 79),
    2: ("DMF", 90, 10, 66, 17, 70),
    3: ("DMF", 90, 37, 60, 21, 16),
    4: ("DMF", 90, 18, 75, None, 9),
    5: ("DMF", 90, 32, 76, None, 87),
    6: ("DMF", 90, 24, 59, 15, 87),
    7: ("DMF", 90, 22, 67, 15, 90),
    8: ("toluene", 90, 36, 68, 17, 82),
    9: ("DCE", 90, 36, 42, 39, 68),
    10: ("THF", 90, 86, 34, 43, 97),
    11: ("dioxane", 90, 65, 31, 40, 95),
    12: ("THF", 110, 48, 36, 40, 95),
    13: ("THF", 110, 48, 46, 16, 95),
    14: ("THF", 110, 48, 57, None, 96),
}

solvent_key = {"DMF": "dmf", "toluene": "toluene", "DCE": "dce", "THF": "thf", "dioxane": "dioxane"}


def common_table1_participants(entry, evidence):
    solvent_name, _, _, _, _, _ = table1[entry]
    allene_mmol = 0.4 if entry <= 12 else (0.6 if entry == 13 else 0.8)
    product_label = "(S)-3aa" if entry == 2 else "(R)-3aa"
    ligand_label, ligand_name = ligands[entry]
    return [
        participant("1a", "reactant", "1a", "N-(2-iodophenyl)-4-methylbenzenesulfonamide", smiles["1a"], evidence,
                    [field("amount", qty(0.2, "mmol"), evidence)]),
        participant("2a", "reactant", "2a", "1,2-decadiene (terminal allene bearing n-C7H15)", smiles["2a"], evidence,
                    [field("amount", qty(allene_mmol, "mmol"), evidence)]),
        participant("pd_dba2", "catalyst", "Pd(dba)2", "bis(dibenzylideneacetone)palladium(0)", None, evidence,
                    [field("catalyst_loading", qty(5, "mol%"), evidence)]),
        participant("ligand", "catalyst", ligand_label, ligand_name, None, evidence,
                    [field("ligand_loading", qty(5, "mol%"), evidence)]),
        participant("ag3po4", "reagent", "Ag3PO4", "silver phosphate", smiles["ag3po4"], evidence,
                    [field("amount", qty(0.08, "mmol"), evidence), field("equivalents", qty(0.4, "equiv"), evidence)]),
        participant("solvent", "solvent", solvent_name, solvent_name, smiles[solvent_key[solvent_name]], evidence,
                    [field("volume", qty(2, "mL"), evidence)]),
        participant("3aa", "product", product_label, "3aa, N-tosyl-3-methylene-2-n-heptylindoline", smiles["3aa"], evidence),
    ]


for entry in range(1, 15):
    evidence = ev(2)
    if entry == 14:
        evidence = ev(2) + ev(3) + ev(4)
    solvent_name, temperature, duration, product_yield, recovery, ee = table1[entry]
    participants = common_table1_participants(entry, evidence)
    ids = [p["entity_id"] for p in participants]
    conditions = [
        field("temperature", qty(temperature, "°C"), ev(2)),
        field("time", qty(duration, "h"), ev(2)),
        field("solvent", solvent_name, ev(2)),
        field("reaction_vessel", "Schlenk tube with a screw cap", ev(2)),
        field("atmosphere", None, []),
        field("workup", None, []),
        field("purification", None, []),
    ]
    steps = [{"step_id": "cyclization", "participant_ids": ids, "conditions": conditions}]
    outcomes = [
        field("isolated_product_yield", qty(product_yield, "%"), ev(2), ["3aa"]),
        field("enantiomeric_excess", qty(ee, "%"), ev(2), ["3aa"]),
        field("ee_measurement_basis", "chiral HPLC", ev(2), ["3aa"]),
    ]
    notes = [(f"Table 1 optimization entry {entry}.", ev(2))]
    unresolved = ["Atmosphere and complete workup/purification are not stated for this optimization row.",
                  "Candidate structures and stereochemical encoding remain unverified."]
    if recovery is not None:
        outcomes.append(field("recovered_starting_material_yield", qty(recovery, "%"), ev(2), ["1a"]))
    if entry == 2:
        notes.append(("The table prints −70 in the ee column; the prose identifies this as the (S)-product in 70% ee, so the magnitude and product assignment are retained separately.", ev(2)))
        unresolved.append("The table's signed ee notation is represented as 70% ee plus the stated (S) assignment, not as a negative percentage.")
    if entry == 6:
        outcomes.append(field("prose_enantiomeric_excess", qty(86, "%"), ev(2), ["3aa"]))
        unresolved.append("The prose reports 86% ee for L6, while Table 1 entry 6 reports 87% ee; both are retained.")
    if entry == 14:
        outcomes.append(field("starting_material_conversion", "complete consumption", ev(2), ["1a"]))
        # Replace the table-only step with the detailed two-stage page-4 procedure.
        for p in participants:
            if p["entity_id"] == "pd_dba2":
                p["amounts"] += [field("mass", qty(6, "mg"), ev(4)), field("amount", qty(0.011, "mmol"), ev(4))]
            elif p["entity_id"] == "ligand":
                p["amounts"] += [field("mass", qty(7, "mg"), ev(4)), field("amount", qty(0.011, "mmol"), ev(4))]
            elif p["entity_id"] == "ag3po4":
                p["amounts"] += [field("mass", qty(34, "mg"), ev(4)), field("detailed_amount", qty(0.081, "mmol"), ev(4))]
            elif p["entity_id"] == "1a":
                p["amounts"] += [field("mass", qty(75, "mg"), ev(4))]
            elif p["entity_id"] == "2a":
                p["amounts"] += [field("mass", qty(112, "mg"), ev(4)), field("detailed_amount", qty(0.81, "mmol"), ev(4))]
            elif p["entity_id"] == "solvent":
                p["amounts"] = [field("initial_volume", qty(1, "mL"), ev(4)), field("additional_volume", qty(1, "mL"), ev(4))]
        steps = [
            {
                "step_id": "catalyst_ligand_premixing",
                "participant_ids": ["pd_dba2", "ligand", "solvent"],
                "conditions": [
                    field("time", qty(2, "h"), ev(4)),
                    field("temperature", "room temperature", ev(4)),
                    field("operation", "Pd(dba)2 and L7 were stirred in 1 mL THF", ev(4)),
                    field("atmosphere", None, []),
                ],
            },
            {
                "step_id": "cyclization",
                "participant_ids": ids,
                "conditions": [
                    field("operation", "Ag3PO4, 1a, 2a, and a further 1 mL THF were introduced sequentially at room temperature", ev(4)),
                    field("temperature", qty(110, "°C"), ev(2) + ev(3) + ev(4)),
                    field("time", qty(48, "h"), ev(2)),
                    field("endpoint", "reaction completion monitored by TLC", ev(4)),
                    field("reaction_vessel", "Schlenk tube with a screw cap", ev(2) + ev(3) + ev(4)),
                    field("atmosphere", None, []),
                ],
            },
            {
                "step_id": "isolation",
                "participant_ids": ["3aa"],
                "conditions": [
                    field("workup", "solvent evaporated under vacuum", ev(4)),
                    field("purification", "silica-gel chromatography; petroleum ether/ethyl acetate = 70:1", ev(4)),
                ],
            },
        ]
        outcomes += [
            field("isolated_product_mass", qty(44, "mg"), ev(4), ["3aa"]),
            field("physical_form", "oil", ev(4), ["3aa"]),
            field("hplc_column", "Chiralcel AD-H", ev(4), ["3aa"]),
            field("hplc_mobile_phase", "hexane/i-PrOH = 85/15", ev(4), ["3aa"]),
            field("hplc_flow_rate", "0.7 mL min−1", ev(4), ["3aa"]),
            field("hplc_detection_wavelength", "230 nm", ev(4), ["3aa"]),
            field("minor_enantiomer_retention_time", qty(4.8, "min"), ev(4), ["3aa"]),
            field("major_enantiomer_retention_time", qty(6.6, "min"), ev(4), ["3aa"]),
            field("specific_rotation", "+9.4 (c 0.50, EtOAc, 20 °C)", ev(4), ["3aa"]),
        ]
        notes += [
            ("This single record merges Table 1 entry 14, Table 2 product 3aa, and the typical preparation because substrate identities, conditions, yield, and ee coincide.", ev(2) + ev(3) + ev(4)),
            ("Table 2 gives the scope-wide 25–67 h range; Table 1 entry 14 gives the row-specific 48 h duration.", ev(2) + ev(3)),
        ]
        unresolved = ["Atmosphere is not stated.", "Candidate structures and absolute stereochemical encoding remain unverified."]
    records.append(record(
        f"table1_entry{entry}", "optimization_entry", evidence, participants, steps, outcomes, notes, unresolved
    ))


scope = [
    # product, aniline, allene, allene name, product name, yield, ee, geometry
    ("3aa", "1a", "2a", "1,2-decadiene (terminal allene bearing n-C7H15)", "3aa, N-tosyl-3-methylene-2-n-heptylindoline", 57, 96, None),
    ("3ab", "1a", "2b", "phthalimide-functionalized terminal allene 2b", "3ab, phthalimide-functionalized alkylideneindoline", 87, 97, None),
    ("3ac", "1a", "2c", "MOM-protected hydroxyalkyl terminal allene 2c", "3ac, MOM-functionalized alkylideneindoline", 52, 96, None),
    ("3ad", "1a", "2d", "n-heptyloxy-functionalized terminal allene 2d", "3ad, n-heptyloxy-functionalized alkylideneindoline", 76, 95, None),
    ("3ae", "1a", "2e", "oxygen-heterocycle-functionalized terminal allene 2e", "3ae, oxygen-heterocycle-functionalized alkylideneindoline", 69, 95, None),
    ("3af", "1a", "2f", "terminal allene bearing n-C8H17", "3af, N-tosyl-3-methylene-2-n-octylindoline", 79, 96, None),
    ("3ag", "1a", "2g", "terminal allene bearing n-C5H11", "3ag, N-tosyl-3-methylene-2-n-pentylindoline", 67, 95, None),
    ("3ah", "1a", "2h", "1,3-disubstituted allene bearing two n-C3H7 groups", "(E)-3ah, E-alkylideneindoline bearing two n-propyl groups", 53, 98, "E"),
    ("3ai", "1a", "2i", "terminal allene bearing n-C6H13", "3ai, N-tosyl-3-methylene-2-n-hexylindoline", 63, 95, None),
    ("3aj", "1a", "2j", "terminal allene bearing n-C9H19", "3aj, N-tosyl-3-methylene-2-n-nonylindoline", 63, 95, None),
    ("3ak", "1a", "2k", "terminal allene bearing n-C10H21", "3ak, N-tosyl-3-methylene-2-n-decylindoline", 69, 95, None),
    ("3ba", "1b", "2a", "1,2-decadiene (terminal allene bearing n-C7H15)", "3ba, chloro-substituted 3aa analogue", 78, 95, None),
    ("3ca", "1c", "2a", "1,2-decadiene (terminal allene bearing n-C7H15)", "3ca, fluoro-substituted 3aa analogue", 69, 94, None),
    ("3bh", "1b", "2h", "1,3-disubstituted allene bearing two n-C3H7 groups", "(E)-3bh, chloro-substituted E-alkylideneindoline", 56, 94, "E"),
    ("3bf", "1b", "2f", "terminal allene bearing n-C8H17", "3bf, chloro-substituted 3af analogue", 76, 95, None),
]


for product_code, aniline_code, allene_code, allene_name, product_name, product_yield, ee_value, geometry in scope:
    if product_code == "3aa":
        continue  # already represented by the cross-table/detailed Table 1 entry 14 record
    evidence = ev(3)
    aniline_name = {
        "1a": "N-(2-iodophenyl)-4-methylbenzenesulfonamide",
        "1b": "N-(5-chloro-2-iodophenyl)-4-methylbenzenesulfonamide",
        "1c": "N-(4-fluoro-2-iodophenyl)-4-methylbenzenesulfonamide",
    }[aniline_code]
    product_smiles = smiles.get(product_code)
    participants = [
        participant(aniline_code, "reactant", aniline_code, aniline_name, smiles.get(aniline_code), evidence,
                    [field("amount", qty(0.2, "mmol"), evidence)]),
        participant(allene_code, "reactant", allene_code, allene_name, smiles.get(allene_code), evidence,
                    [field("amount", qty(0.8, "mmol"), evidence), field("equivalents", qty(4, "equiv"), evidence)]),
        participant("pd_dba2", "catalyst", "Pd(dba)2", "bis(dibenzylideneacetone)palladium(0)", None, evidence,
                    [field("catalyst_loading", qty(5, "mol%"), evidence)]),
        participant("l7", "catalyst", "(Ra,S,S)-L7", "beta-naphthylmethyl-substituted spiro-BOX L7", None, evidence,
                    [field("ligand_loading", qty(5, "mol%"), evidence)]),
        participant("ag3po4", "reagent", "Ag3PO4", "silver phosphate", smiles["ag3po4"], evidence,
                    [field("amount", qty(0.08, "mmol"), evidence), field("equivalents", qty(0.4, "equiv"), evidence)]),
        participant("thf", "solvent", "THF", "tetrahydrofuran", smiles["thf"], evidence,
                    [field("volume", qty(2, "mL"), evidence)]),
        participant(product_code, "product", f"(R)-{product_code}" if geometry is None else f"(R)-({geometry})-{product_code}", product_name, product_smiles, evidence),
    ]
    outcomes = [
        field("isolated_product_yield", qty(product_yield, "%"), evidence, [product_code]),
        field("enantiomeric_excess", qty(ee_value, "%"), evidence, [product_code]),
        field("ee_measurement_basis", "chiral HPLC", evidence, [product_code]),
    ]
    notes = [(f"Table 2 substrate-scope result for {product_code}.", evidence)]
    unresolved = [
        "The source gives only a shared 25–67 h duration range; the row-specific duration is not identified.",
        "Atmosphere, workup, and purification are not stated for this scope row.",
        "Candidate structures, substituent positions, and stereochemical encoding remain unverified.",
    ]
    if geometry:
        outcomes.append(field("alkene_geometry", geometry, evidence, [product_code]))
    if product_code == "3ah":
        notes.append(("The E double-bond configuration is supported by the Figure 2 NOE study.", evidence))
    if product_code == "3af":
        notes.append(("Footnote 9 states that the R configuration was assigned by comparison of specific rotation with reference 5b; the cited SI details were not supplied.", ev(4)))
        evidence = evidence + ev(4)
    records.append(record(
        f"table2_{product_code}",
        "substrate_scope_entry",
        evidence,
        participants,
        [{
            "step_id": "asymmetric_cyclization",
            "participant_ids": [p["entity_id"] for p in participants],
            "conditions": [
                field("temperature", qty(110, "°C"), ev(3)),
                field("time", rng(25, 67, "h", "25–67 h"), ev(3)),
                field("solvent", "THF", ev(3)),
                field("reaction_vessel", "Schlenk tube with a screw cap", ev(3)),
                field("atmosphere", None, []),
                field("workup", None, []),
                field("purification", None, []),
            ],
        }],
        outcomes,
        notes,
        unresolved,
    ))


OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")

table1_ids = [f"{DOC}:table1_entry{i}" for i in range(1, 15)]
table2_ids = [f"{DOC}:table1_entry14"] + [f"{DOC}:table2_{row[0]}" for row in scope if row[0] != "3aa"]
coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1,
            "state": "attempted",
            "regions": [
                {
                    "region": "title, abstract, introduction, and lower-right Scheme 1 on the original page",
                    "finding": "Scheme 1 is a generic comparison of established allylation and an envisioned allene/carbometallation route; classified as a general scheme. Abstract and introduction contain broad claims and cited prior work, not independent present-paper batches.",
                    "evidence_ids": ev(1),
                }
            ],
            "record_ids": [f"{DOC}:scheme1_conceptual_allylation_protocols"],
            "unresolved": ["Generic LG/Nu/R/n/M/L* structures and experiment-level conditions are not defined."],
        },
        {
            "page": 2,
            "state": "attempted",
            "regions": [
                {
                    "region": "upper Figure 1 ligand evolution",
                    "finding": "Ligand structures L1–L7 and substituent identities were inspected; the arrows describe ligand-design evolution, not reported ligand-synthesis experiments on this page.",
                    "evidence_ids": ev(2),
                },
                {
                    "region": "middle discussion and lower Table 1 with footnotes",
                    "finding": "Fourteen independent optimization rows extracted. Parenthesized values are recoveries of 1a, not product yields; entries 13 and 14 use 0.6 and 0.8 mmol 2a, respectively. Entry 14 is merged with Table 2 3aa and the page-4 typical procedure.",
                    "evidence_ids": ev(2),
                },
            ],
            "record_ids": table1_ids,
            "unresolved": [
                "Table 1 entry 6 reports 87% ee while the prose states 86%; both are retained.",
                "The signed −70 entry is represented as 70% ee for the prose-identified (S)-product.",
                "Most rows omit atmosphere, workup, and purification.",
            ],
        },
        {
            "page": 3,
            "state": "attempted",
            "regions": [
                {
                    "region": "upper and middle Table 2 reaction drawing, 15 structures, and footnote",
                    "finding": "Fifteen substrate-scope outcomes inspected. The shared 0.2 mmol 1, 0.8 mmol 2, 0.08 mmol Ag3PO4, 5 mol% Pd(dba)2/L7, 2 mL THF, 110 °C, 25–67 h conditions and isolated-yield/chiral-HPLC bases were applied. The 3aa row is merged with Table 1 entry 14.",
                    "evidence_ids": ev(3),
                },
                {
                    "region": "lower-left Figure 2 NOE study and adjacent scope discussion",
                    "finding": "Figure 2 supports the E assignment of 3ah; it is evidence for the scope record rather than a separate experiment. The prose identifies ether, amide, MOM and 1,3-disubstituted-allene tolerance.",
                    "evidence_ids": ev(3),
                },
            ],
            "record_ids": table2_ids,
            "unresolved": [
                "Only a shared 25–67 h range is given; row-specific scope durations are unknown.",
                "Atmosphere, workup, and purification are absent for the abbreviated scope entries.",
                "Complex structures and stereochemistry remain unverified machine candidates.",
            ],
        },
        {
            "page": 4,
            "state": "attempted",
            "regions": [
                {
                    "region": "upper-left Experimental Section typical procedure for (R)-3",
                    "finding": "Detailed preparation of (R)-3aa merged into Table 1 entry 14/Table 2 3aa, adding exact masses and mmol, 2 h catalyst-ligand premixing, sequential additions, TLC endpoint, vacuum evaporation, chromatography, product mass, HPLC details, and rotation.",
                    "evidence_ids": ev(4),
                },
                {
                    "region": "remaining acknowledgements and references",
                    "finding": "No additional present-paper reaction batch. Footnote 9 supports the R assignment of 3af by comparison to prior data but points to unavailable SI for details.",
                    "evidence_ids": ev(4),
                },
            ],
            "record_ids": [f"{DOC}:table1_entry14", f"{DOC}:table2_3af"],
            "unresolved": [
                "The typical procedure does not state atmosphere.",
                "SI is advertised but was not supplied or explicitly associated.",
                "Analytical characterization supports identity but does not independently verify candidate connectivity or absolute stereochemistry.",
            ],
        },
    ],
}
COVERAGE.parent.mkdir(parents=True, exist_ok=True)
COVERAGE.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

tasks = json.loads(TASKS.read_text())
page_ids = {f"{DOC}:page{i}:text" for i in range(1, 5)}
for task in tasks:
    if task.get("task_id") in page_ids:
        task["state"] = "attempted"
TASKS.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"records": len(records), "output": str(OUT), "coverage": str(COVERAGE)}, ensure_ascii=False))
