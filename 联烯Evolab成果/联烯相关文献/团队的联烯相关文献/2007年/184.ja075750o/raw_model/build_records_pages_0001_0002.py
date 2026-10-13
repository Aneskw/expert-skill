#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "runs/current"
DOC = "doc_a39752c5fd485db5"
P1T = f"{DOC}:page1:text"
P1I = f"{DOC}:page1:image"
P2T = f"{DOC}:page2:text"
P2I = f"{DOC}:page2:image"


def fact(value, evidence):
    return {
        "value": value,
        "evidence_ids": list(evidence) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def field(name, value, evidence, targets=None):
    item = {"name": name, "fact": fact(value, evidence)}
    if targets:
        item["target_entity_ids"] = list(targets)
    return item


def participant(entity_id, role, label, evidence, *, name=None, smiles=None, amounts=()):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence) if name is not None else fact(None, ()),
        "smiles": fact(smiles, evidence) if smiles is not None else fact(None, ()),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": list(amounts),
    }


def record(suffix, kind, evidence, participants, steps, outcomes, notes=(), unresolved=()):
    return {
        "record_id": f"{DOC}:{suffix}",
        "document_id": DOC,
        "source_reaction_id": suffix,
        "record_kind": kind,
        "status": "needs_review",
        "completeness": "partial",
        "evidence_ids": list(evidence),
        "participants": participants,
        "steps": steps,
        "outcomes": outcomes,
        "notes": [fact(x, evidence) for x in notes],
        "review": {
            "method": "model",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": list(unresolved),
        },
    }


def q(number, unit, **extra):
    return {"number": number, "unit": unit, **extra}


SMILES = {
    "1a": "CCOC(=O)C(CCC)=C=Cc1ccccc1",
    "Z-2a": "CCOC(=O)C(CCC)C(C)=Cc1ccccc1",
    "3a": "CCOC(=O)C(CCC)=C(C)Cc1ccccc1",
    "THF": "C1CCOC1",
    "CH2Cl2": "ClCCl",
    "n-hexane": "CCCCCC",
    "Et2O": "CCOCC",
    "toluene": "Cc1ccccc1",
    "D2O": "[2H]O[2H]",
    "acrolein": "C=CC=O",
    "methyl chloroformate": "COC(=O)Cl",
    "acetyl chloride": "CC(=O)Cl",
}


records = []

# Table 1: every optimization row is a distinct experiment. Dashes are retained literally.
table1 = [
    # entry, catalyst, loading, solvent, 2a yield, Z/E, recovered 1a, 3a yield, Grignard equiv, time
    (1, None, None, "THF", "table dash (–)", None, 77, "table dash (–)", 3, 2),
    (2, "Fe(acac)3", 20, "THF", 78, "96/4", "table dash (–)", 0.5, 3, 2),
    (3, "Fe(acac)3", 20, "CH2Cl2", 50, "74/26", 2, 3, 3, 2),
    (4, "Fe(acac)3", 20, "n-hexane", 50, "83/17", 6, 1.5, 3, 2),
    (5, "Fe(acac)3", 20, "Et2O", 81, "98/2", "table dash (–)", 1.1, 3, 2),
    (6, "Fe(acac)3", 5, "Et2O", 77, "99/1", "table dash (–)", 0.4, 3, 2),
    (7, "Fe(acac)3", 20, "toluene", 71, "98/2", "table dash (–)", 1, 3, 2),
    (8, "Fe(acac)3", 10, "toluene", 75, "99/1", "table dash (–)", 0.4, 3, 2),
    (9, "Fe(acac)3", 5, "toluene", 81, ">99/1", "table dash (–)", 0.8, 3, 2),
    (10, "Fe(acac)3", 5, "toluene", 76, "91/9", "table dash (–)", 1.5, 1.2, 2),
    (11, "Fe(acac)3", 2, "toluene", 82, ">99/1", 2, 0.3, 3, 2),
    (12, "Fe(acac)3", 0.5, "toluene", 73, ">99/1", 6, 1.5, 3, 5),
    (13, None, None, "toluene", 29, ">99/1", 56, 2, 3, 2),
    (14, "CuCl2", 20, "toluene", 82, ">99/1", "table dash (–)", 3, 3, 2),
]

for entry, catalyst, loading, solvent, y2, ze, recovery, y3, equiv, hours in table1:
    ev = (P1T, P1I)
    parts = [
        participant("substrate_1a", "reactant", "1a", ev,
                    name="ethyl 2-(n-propyl)-4-phenylbuta-2,3-dienoate", smiles=SMILES["1a"]),
        participant("methylmagnesium_chloride", "reactant", "CH3MgCl", ev,
                    name="methylmagnesium chloride",
                    amounts=(field("equivalents", q(equiv, "equiv"), ev),
                             field("solution_concentration", q(3, "M"), ev))),
        participant("thf_carrier", "solvent", "THF", ev, name="tetrahydrofuran", smiles=SMILES["THF"]),
        participant("product_z2a", "product", "(Z)-2a", ev,
                    name="ethyl (Z)-2-(n-propyl)-3-methyl-4-phenylbut-3-enoate", smiles=SMILES["Z-2a"]),
        participant("product_3a", "product", "3a", ev,
                    name="ethyl 2-(n-propyl)-3-methyl-4-phenylbut-2-enoate", smiles=SMILES["3a"]),
    ]
    if solvent != "THF":
        parts.append(participant("reaction_solvent", "solvent", solvent, ev, name=solvent,
                                 smiles=SMILES.get(solvent)))
    if catalyst:
        parts.append(participant("catalyst", "catalyst", catalyst, ev, name=catalyst,
                                 amounts=(field("catalyst_loading", q(loading, "mol%"), ev),)))
    conditions = [
        field("temperature", q(-78, "°C"), ev),
        field("time", q(hours, "h"), ev),
        field("atmosphere", None, ()),
        field("workup", None, ()),
        field("purification", None, ()),
    ]
    outcomes = [
        field("nmr_yield_z2a", q(y2, "%") if isinstance(y2, (int, float)) else y2, ev, ("product_z2a",)),
    ]
    if ze is not None:
        outcomes.append(field("z_e_ratio_z2a", ze, ev, ("product_z2a",)))
    outcomes += [
        field("recovered_starting_material_yield", q(recovery, "%") if isinstance(recovery, (int, float)) else recovery, ev, ("substrate_1a",)),
        field("nmr_yield_3a", q(y3, "%") if isinstance(y3, (int, float)) else y3, ev, ("product_3a",)),
        field("yield_measurement_basis", "determined by NMR", ev),
    ]
    notes = [f"Table 1 entry {entry}; THF is also the carrier solvent of the Grignard solution."]
    if catalyst is None:
        notes.append("No Fe(acac)3 catalyst was used; the paper describes this condition as no reaction." if entry == 1
                     else "No Fe(acac)3 catalyst was used; the paper describes this condition as very slow.")
    if entry == 14:
        notes.append("CuCl2 was used instead of Fe(acac)3.")
    records.append(record(
        f"table1_entry{entry}", "optimization_entry", ev, parts,
        [{"step_id": "conjugate_addition", "participant_ids": [p["entity_id"] for p in parts], "conditions": conditions}],
        outcomes, notes,
        ("Substrate scale, atmosphere, workup, and purification are not reported for this optimization row.",
         "Candidate constitutional SMILES and alkene geometry require expert structure review."),
    ))


# Table 2: row substitutions and exact visual values.
table2 = [
    # entry, R1, R2, R3, substrate, R4, time, yield, product, footnote
    (1, "Ph", "n-Pr", "Et", "1a", "Me", 2, 77, "2a", "b"),
    (2, "Ph", "n-Pr", "Me", "1b", "Me", 3, 86, "2b", "c"),
    (3, "Ph", "n-Pr", "Bn", "1c", "Me", 2, 84, "2c", "b"),
    (4, "Ph", "Me", "Et", "1d", "Me", 1.5, 88, "2d", None),
    (5, "p-BrC6H4", "n-Pr", "Et", "1e", "Me", 1, 88, "2e", None),
    (6, "p-BrC6H4", "Me", "Et", "1f", "Me", 1.5, 88, "2f", "c"),
    (7, "n-C7H15", "n-Pr", "Et", "1g", "Me", 5, 85, "2g", "b"),
    (8, "n-C4H9", "Bn", "Me", "1h", "Me", 1.5, 85, "2h", None),
    (9, "Ph", "n-Pr", "Et", "1a", "n-Bu", 1, 70, "2i", "b"),
    (10, "Ph", "n-Pr", "Et", "1a", "c-Hex", 1.7, 86, "2j", "b"),
    (11, "n-C7H15", "n-Pr", "Et", "1g", "c-Hex", 1, 90, "2k", "b"),
    (12, "Ph", "Me", "Et", "1d", "c-Hex", 1, 78, "2l", "b"),
    (13, "n-C7H15", "n-Pr", "Et", "1g", "s-Bu", 1, 94, "1m", "b"),
    (14, "n-C4H9", "H", "Et", "1i", "Ph", 2, 63, "2n", None),
    (15, "n-C7H15", "H", "Et", "1j", "Ph", 1, 63, "2o", "b"),
    (16, "Ph", "n-Pr", "Et", "1a", "vinyl", 1, 82, "1p", "b"),
    (17, "n-C7H15", "n-Pr", "Et", "1g", "vinyl", 1, 86, "1q", "b"),
]

grignards = {
    "Me": ("MeMgCl", "methylmagnesium chloride"),
    "n-Bu": ("n-BuMgCl", "n-butylmagnesium chloride"),
    "c-Hex": ("c-HexMgCl", "cyclohexylmagnesium chloride"),
    "s-Bu": ("s-BuMgBr", "sec-butylmagnesium bromide"),
    "Ph": ("PhMgCl", "phenylmagnesium chloride"),
    "vinyl": ("vinylMgCl", "vinylmagnesium chloride"),
}

for entry, r1, r2, r3, substrate, r4, hours, yield_value, product, footnote in table2:
    ev = (P2T, P2I)
    loading = 5 if footnote == "b" else 0.5 if footnote == "c" else 2
    reagent_label, reagent_name = grignards[r4]
    sub_smiles = SMILES["1a"] if substrate == "1a" else None
    product_smiles = SMILES["Z-2a"] if product == "2a" else None
    parts = [
        participant("substrate", "reactant", substrate, ev,
                    name=f"2,3-allenoate {substrate} (R1={r1}, R2={r2}, R3={r3})", smiles=sub_smiles,
                    amounts=(field("reaction_scale", q(0.4, "mmol"), ev),)),
        participant("grignard", "reactant", reagent_label, ev, name=reagent_name,
                    amounts=(field("equivalents", q(3, "equiv"), ev),)),
        participant("fe_acac3", "catalyst", "Fe(acac)3", ev, name="iron(III) acetylacetonate",
                    amounts=(field("catalyst_loading", q(loading, "mol%"), ev),)),
        participant("toluene", "solvent", "toluene", ev, name="toluene", smiles=SMILES["toluene"],
                    amounts=(field("volume", q(5, "mL"), ev),)),
        participant("thf_carrier", "solvent", "THF", ev, name="tetrahydrofuran", smiles=SMILES["THF"]),
        participant("product", "product", product, ev,
                    name=f"beta,gamma-unsaturated alkenoate {product} (R1={r1}, R2={r2}, R3={r3}, R4={r4})",
                    smiles=product_smiles),
    ]
    conditions = [
        field("temperature", q(-78, "°C"), ev),
        field("time", q(hours, "h"), ev),
        field("atmosphere", None, ()),
        field("workup", None, ()),
        field("purification", None, ()),
    ]
    records.append(record(
        f"table2_entry{entry}_{product}", "substrate_scope_entry", ev, parts,
        [{"step_id": "carbomagnesiation", "participant_ids": [p["entity_id"] for p in parts], "conditions": conditions}],
        [field("isolated_yield", q(yield_value, "%"), ev, ("product",)),
         field("yield_measurement_basis", "isolated yield", ev)],
        (f"Table 2 entry {entry}; R1={r1}, R2={r2}, R3={r3}, R4={r4}.",),
        ("Atmosphere, workup, and purification are not reported in the supplied main text.",
         "Most substrate and product structures, including alkene stereochemistry, remain unverified machine interpretations."),
    ))


# Scheme 1 is explicitly proposed as a catalytic mechanism.
ev = (P1T, P1I, P2T, P2I)
mechanism_parts = [
    participant("allenoate_1", "reactant", "generic 2,3-allenoate 1", ev,
                name="generic 2,3-allenoate (R-group structure)"),
    participant("grignard", "reactant", "R4MgX", ev, name="generic Grignard reagent"),
    participant("fe_acac3", "catalyst", "Fe(acac)3", ev, name="iron(III) acetylacetonate"),
    participant("complex_4", "unspecified_agent", "4", ev, name="proposed iron-magnesium ate complex"),
    participant("intermediate_5", "unspecified_agent", "5", ev, name="proposed coordination intermediate"),
    participant("transition_state_6", "unspecified_agent", "6", ev, name="proposed stereodetermining transition state"),
    participant("dienolate_7", "unspecified_agent", "7", ev, name="proposed iron 1,3-dienolate"),
    participant("dienolate_8", "unspecified_agent", "8", ev, name="proposed magnesium 1,3-dienolate"),
]
records.append(record(
    "scheme1_proposed_catalytic_cycle", "mechanism", ev, mechanism_parts, [], [],
    ("The authors propose formation of ate complex 4, conjugate addition through 5/6, iron dienolate 7, and transmetalation to magnesium dienolate 8 with catalyst regeneration.",),
    ("Scheme 1 is a proposed mechanism, not a set of separately executed experiments.",
     "Generic R-group and organometallic structures are not assigned SMILES."),
))


# Scheme 2: D2O trapping is distinct from the normal Table 2 workup.
ev = (P1T, P1I, P2T, P2I)
scheme2_parts = [
    participant("substrate_1a", "reactant", "1a", ev,
                name="ethyl 2-(n-propyl)-4-phenylbuta-2,3-dienoate", smiles=SMILES["1a"]),
    participant("methylmagnesium_chloride", "reactant", "CH3MgCl", ev,
                name="methylmagnesium chloride",
                amounts=(field("equivalents", q(3, "equiv"), ev), field("solution_concentration", q(3, "M"), ev))),
    participant("fe_acac3", "catalyst", "Fe(acac)3", ev, name="iron(III) acetylacetonate",
                amounts=(field("catalyst_loading", q(5, "mol%"), ev),)),
    participant("toluene", "solvent", "toluene", ev, name="toluene", smiles=SMILES["toluene"]),
    participant("thf", "solvent", "THF", ev, name="tetrahydrofuran", smiles=SMILES["THF"]),
    participant("d2o", "reagent", "D2O", ev, name="deuterium oxide", smiles=SMILES["D2O"]),
    participant("product_9", "product", "9", ev,
                name="ethyl 2-deuterio-2-(n-propyl)-3-methyl-4-phenylbut-3-enoate"),
]
scheme2_steps = [
    {"step_id": "carbomagnesiation", "participant_ids": ["substrate_1a", "methylmagnesium_chloride", "fe_acac3", "toluene", "thf"],
     "conditions": [field("temperature", q(-78, "°C"), ev), field("time", q(2, "h"), ev), field("atmosphere", None, ())]},
    {"step_id": "d2o_trapping", "participant_ids": ["d2o", "product_9"],
     "conditions": [field("initial_temperature", q(-78, "°C"), ev), field("warm_to", "r.t.", ev),
                    field("time", None, ()), field("workup", None, ()), field("purification", None, ())]},
]
records.append(record(
    "scheme2_d2o_trapping", "reported_experiment", ev, scheme2_parts, scheme2_steps,
    [field("reported_yield_9", q(89, "%"), ev, ("product_9",)),
     field("deuterium_incorporation", q(97, "%"), ev, ("product_9",)),
     field("yield_measurement_basis", None, ())],
    ("D2O trapping supports in situ formation of magnesium dienolate 8a.",),
    ("Absolute scale, D2O amount, atmosphere, trapping duration, workup, purification, and yield basis are not reported.",
     "Product constitution and alkene geometry require expert structure review."),
))


# Scheme 3: three independent electrophile-trapping arrows from magnesium dienolate 8a.
scheme3 = [
    ("acrolein", "acrolein", "10", -78, None, 1.5, 71, "71/29"),
    ("methyl_chloroformate", "methyl chloroformate", "11", -78, "r.t.", 3.5, 59, None),
    ("acetyl_chloride", "acetyl chloride", "12", -78, None, 1, 61, None),
]
ev = (P2T, P2I)
for reagent_id, reagent_name, product, temperature, warm_to, hours, yield_value, dr in scheme3:
    parts = [
        participant("dienolate_8a", "reactant", "8a", ev, name="magnesium 1,3-dienolate 8a"),
        participant(reagent_id, "reactant", reagent_name, ev, name=reagent_name, smiles=SMILES[reagent_name]),
        participant("product", "product", product, ev, name=f"electrophile-trapping product {product}"),
    ]
    outcomes = [field(f"reported_yield_{product}", q(yield_value, "%"), ev, ("product",)),
                field("yield_measurement_basis", None, ())]
    if dr:
        outcomes.append(field("diastereomer_ratio", dr, ev, ("product",)))
    records.append(record(
        f"scheme3_dienolate_8a_{reagent_id}", "reported_experiment", ev, parts,
        [{"step_id": "electrophile_trapping", "participant_ids": [p["entity_id"] for p in parts],
          "conditions": [field("initial_temperature", q(temperature, "°C"), ev)]
                        + ([field("warm_to", warm_to, ev)] if warm_to else [])
                        + [field("time", q(hours, "h"), ev), field("atmosphere", None, ()),
                           field("workup", None, ()), field("purification", None, ())]}],
        outcomes,
        (f"Scheme 3 arrow from in situ magnesium dienolate 8a to product {product}.",),
        ("Electrophile and dienolate quantities, atmosphere, workup, purification, and yield basis are not reported.",
         "The complex product structure and stereochemistry remain unverified."),
    ))


raw_path = OUT / "raw_model/records_pages_0001_0002.json"
raw_path.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")

page1_ids = [r["record_id"] for r in records if r["record_id"].startswith(f"{DOC}:table1_")]
page1_ids += [f"{DOC}:scheme1_proposed_catalytic_cycle", f"{DOC}:scheme2_d2o_trapping"]
page2_ids = [r["record_id"] for r in records if r["record_id"].startswith(f"{DOC}:table2_")]
page2_ids += [f"{DOC}:scheme1_proposed_catalytic_cycle", f"{DOC}:scheme2_d2o_trapping"]
page2_ids += [r["record_id"] for r in records if r["record_id"].startswith(f"{DOC}:scheme3_")]

coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1,
            "state": "attempted",
            "regions": [
                {"region": "left-column introduction and results prose", "finding": "Background organocuprate/organolithium chemistry is cited prior work; present-paper prose was merged into Table 1, Table 2, Scheme 1, and Scheme 2 records rather than duplicated.", "evidence_ids": [P1I, P1T]},
                {"region": "upper-right Table 1 and footnotes", "finding": "All 14 optimization rows were extracted independently, including catalyst/solvent/load/time overrides, NMR yields, Z/E ratios, recovered 1a, byproduct 3a, and literal table dashes.", "evidence_ids": [P1I, P1T]},
                {"region": "lower-right mechanistic and D2O-trapping prose", "finding": "Proposed catalytic cycle classified as mechanism; the D2O trapping result was extracted as a distinct reported experiment and linked to the page-2 drawing.", "evidence_ids": [P1I, P1T, P2I, P2T]},
            ],
            "record_ids": page1_ids,
            "unresolved": [
                "Table 1 omits substrate scale, atmosphere, workup, and purification.",
                "The D2O-trapping result omits absolute scale, D2O amount, trapping time, workup, purification, and yield basis.",
                "Candidate structures and alkene stereochemistry remain unverified.",
            ],
        },
        {
            "page": 2,
            "state": "attempted",
            "regions": [
                {"region": "upper-left Table 2 and footnotes", "finding": "All 17 substrate-scope rows were extracted independently; entry 13 was visually read as 94% for product 1m, and catalyst-loading/bromide footnotes were applied only to their marked rows.", "evidence_ids": [P2I, P2T]},
                {"region": "lower-left Schemes 1 and 2", "finding": "Scheme 1 is a proposed catalytic mechanism; Scheme 2 is a distinct D2O-quench experiment giving 9 in 89% yield with 97% D incorporation.", "evidence_ids": [P2I, P2T, P1I, P1T]},
                {"region": "upper-right Scheme 3", "finding": "Three separate electrophile-trapping experiments from dienolate 8a were extracted for acrolein, methyl chloroformate, and acetyl chloride.", "evidence_ids": [P2I, P2T]},
                {"region": "right-column acknowledgments, SI statement, and references", "finding": "No new reaction row; the online Supporting Information statement does not establish an associated SI source in this workspace.", "evidence_ids": [P2I, P2T]},
            ],
            "record_ids": page2_ids,
            "unresolved": [
                "Table 2 omits atmosphere, workup, and purification; only isolated-yield basis is explicit.",
                "Scheme 3 omits participant quantities, atmosphere, workup, purification, and yield basis.",
                "Supporting Information is mentioned but was not supplied or explicitly associated.",
                "Generic mechanism and complex product structures remain unverified.",
            ],
        },
    ],
}
(OUT / "coverage").mkdir(parents=True, exist_ok=True)
(OUT / "coverage/pages_0001_0002.json").write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

tasks_path = OUT / "tasks.json"
tasks = json.loads(tasks_path.read_text())
for task in tasks:
    if task["document_id"] == DOC and task["evidence_id"] in {P1T, P2T}:
        task["state"] = "attempted"
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"records": len(records), "raw": str(raw_path), "coverage_pages": [1, 2]}, ensure_ascii=False))
