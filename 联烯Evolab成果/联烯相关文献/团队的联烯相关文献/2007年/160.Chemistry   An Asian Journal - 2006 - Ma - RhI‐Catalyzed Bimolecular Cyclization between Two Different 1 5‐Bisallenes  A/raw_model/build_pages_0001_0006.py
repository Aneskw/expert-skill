#!/usr/bin/env python3
"""Build evidence-linked machine records for doc_5f2d35ba503c62a4, PDF pages 1-6."""
import json
from pathlib import Path

DOC = "doc_5f2d35ba503c62a4"
ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).with_name("pages_0001_0006_records.json")


def ev(page):
    return f"{DOC}:page{page}:image"


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


def q(number, unit, **extra):
    value = {"number": number, "unit": unit}
    value.update(extra)
    return value


def qr(minimum, maximum, unit, raw_text):
    return {"minimum": minimum, "maximum": maximum, "unit": unit, "raw_text": raw_text}


SMILES = {
    "1a": "C=C=CCN(CC=C=C)S(=O)(=O)c1ccc(C)cc1",
    "1d": "C=C=CCS(=O)(=O)CC=C=C",
    "1e": "C=C=CCOCC=C=C",
    "1f": "C=C=CCSCC=C=C",
    "2a": "COC(=O)C(CC=C=C)(CC=C=C)C(=O)OC",
    "2b": "N#CC(CC=C=C)(CC=C=C)C#N",
    "2c": "C=C=CCC(CC=C=C)(S(=O)(=O)c1ccccc1)S(=O)(=O)c1ccccc1",
    "toluene": "Cc1ccccc1",
}


def participant(entity_id, role, label, evidence, smiles=None, amounts=None, name=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence) if name is not None else fact(None, []),
        "smiles": fact(smiles, evidence) if smiles is not None else fact(None, []),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": amounts or [],
    }


def amount_fields(evidence, mass=None, amount=None, loading=None, volume=None):
    fields = []
    if mass is not None:
        fields.append(field("mass", q(mass, "mg"), evidence))
    if amount is not None:
        if isinstance(amount, tuple):
            fields.append(field("amount", qr(amount[0], amount[1], "mmol", amount[2]), evidence))
        else:
            fields.append(field("amount", q(amount, "mmol"), evidence))
    if loading is not None:
        fields.append(field("reported_catalyst_loading", q(loading, "mol%"), evidence))
    if volume is not None:
        if isinstance(volume, tuple):
            fields.append(field("solvent_volume", qr(volume[0], volume[1], "mL", volume[2]), evidence))
        else:
            fields.append(field("solvent_volume", q(volume, "mL"), evidence))
    return fields


def review(unresolved):
    return {"method": "none", "reviewer": None, "checked_fields": [], "unresolved": unresolved}


def base_record(rid, kind, evidence, participants, steps, outcomes, notes=None, unresolved=None):
    return {
        "record_id": f"{DOC}:{rid}",
        "document_id": DOC,
        "source_reaction_id": rid,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": evidence,
        "participants": participants,
        "steps": steps,
        "outcomes": outcomes,
        "notes": notes or [],
        "review": review(unresolved or []),
    }


table1 = [
    {
        "entry": 1, "a": "1a", "b": "2a", "vol": 72, "time": 7, "temp": "reflux", "loading": 5,
        "a_mass": 413, "a_mmol": 1.5, "b_mass": 357, "b_mmol": 1.5, "cat_mass": 108, "cat_mmol": 0.16,
        "products": [("3aa", 20, 82), ("4aa", 30, 106), ("5aa", 12, 88), ("6aa", 9, 68)],
        "proc_page": 3,
    },
    {
        "entry": 2, "a": "1a", "b": "2b", "vol": 72, "time": 4, "temp": "reflux", "loading": 5,
        "a_mass": 413, "a_mmol": 1.5, "b_mass": 255, "b_mmol": 1.5, "cat_mass": 109, "cat_mmol": 0.16,
        "products": [("3aa", 18, 76), ("4bb", 33, 84), ("5ab", 13, 88), ("6ba", 9, 57)],
        "proc_page": 4,
    },
    {
        "entry": 3, "a": "1a", "b": "2c", "vol": 36, "time": 9.5, "temp": "reflux", "loading": 5,
        "a_mass": 207, "a_mmol": 0.75, "b_mass": 300, "b_mmol": 0.75, "cat_mass": 54, "cat_mmol": 0.078,
        "products": [("3aa", 24, 49), ("4cc", 25, 74), ("5ac", 15, 74), ("6ca", 7, 37)],
        "proc_page": 4,
    },
    {
        "entry": 4, "a": "1d", "b": "2a", "vol": 48, "time": 4, "temp": "reflux", "loading": 5,
        "a_mass": 174, "a_mmol": 1.0, "b_mass": 238, "b_mmol": 1.0, "cat_mass": 69, "cat_mmol": 0.10,
        "products": [("3dd", 17, 29), ("4aa", 23, 54), ("5da", 8, 33), ("6ad", 17, 68)],
        "proc_page": 4,
    },
    {
        "entry": 5, "a": "1e", "b": "2c", "vol": 36, "time": 21, "temp": q(80, "°C"), "loading": 10,
        "a_mass": 184, "a_mmol": 1.5, "b_mass": 301, "b_mmol": 0.75, "cat_mass": 52, "cat_mmol": 0.075,
        "products": [("4cc", 38, 115), ("6ce", 13, 50)], "dashes": ["product_3_yield", "product_5_yield"],
        "proc_page": 5,
    },
    {
        "entry": 6, "a": "1a", "b": "1d", "vol": 48, "time": 19, "temp": "reflux", "loading": 5,
        "a_mass": 276, "a_mmol": 1.0, "b_mass": 172, "b_mmol": 1.0, "cat_mass": 69, "cat_mmol": 0.10,
        "products": [("3aa", 15, 41), ("3dd", 19, 32), ("5ad", 10, 45), ("6da", 9, 38)],
        "proc_page": 5,
    },
    {
        "entry": 7, "a": "1a", "b": "1e", "vol": 72, "time": 24, "temp": q(80, "°C"), "loading": 10,
        "a_mass": 413, "a_mmol": 1.5, "b_mass": 365, "b_mmol": 3.0, "cat_mass": 104, "cat_mmol": 0.15,
        "products": [("3aa", 19, 77), ("5ae", 5, 28)], "dashes": ["product_4_yield", "product_6_yield"],
        "proc_page": 5,
    },
]


records = []
table1_ids = []
for row in table1:
    rid = f"table1_entry_{row['entry']}"
    table1_ids.append(f"{DOC}:{rid}")
    evidence = [ev(2), ev(row["proc_page"])]
    if row["entry"] == 1:
        evidence = [ev(1), ev(2), ev(3)]
    proc_ev = [ev(row["proc_page"])]
    table_ev = [ev(2)]
    participants = [
        participant(
            "reactant_a", "reactant", row["a"], evidence,
            SMILES.get(row["a"]), amount_fields(proc_ev, row["a_mass"], row["a_mmol"]),
        ),
        participant(
            "reactant_b", "reactant", row["b"], evidence,
            SMILES.get(row["b"]), amount_fields(proc_ev, row["b_mass"], row["b_mmol"]),
        ),
        participant(
            "rh_catalyst", "catalyst", "trans-[RhCl(CO)(PPh3)2]", table_ev,
            None,
            amount_fields(proc_ev, row["cat_mass"], row["cat_mmol"]) + amount_fields(table_ev, loading=row["loading"]),
        ),
        participant(
            "toluene", "solvent", "toluene", evidence, SMILES["toluene"],
            amount_fields(proc_ev, volume=row["vol"]), name="dry toluene",
        ),
    ]
    outcomes = []
    product_ids = []
    for label, yield_value, mass in row["products"]:
        entity_id = f"product_{label}"
        product_ids.append(entity_id)
        participants.append(participant(entity_id, "product", label, evidence, None, amount_fields(proc_ev, mass=mass)))
        outcomes.append(field("isolated_yield", q(yield_value, "%"), evidence, [entity_id]))
    for dash_name in row.get("dashes", []):
        outcomes.append(field(dash_name, "table dash (–)", table_ev))
    outcomes.append(field("yield_measurement_basis", "isolated products", table_ev))
    conditions = [
        field("time", q(row["time"], "h"), table_ev),
        field("temperature", row["temp"], table_ev),
        field("atmosphere", "argon", table_ev),
        field("solvent", "dry toluene", proc_ev),
    ]
    if row["entry"] == 1:
        conditions.extend([
            field("operation", "reaction monitored by TLC (petroleum ether/ethyl acetate 5:1)", proc_ev),
            field("workup", "concentrated by evaporation", proc_ev),
            field("purification", "silica-gel column chromatography; petroleum ether/ethyl acetate 10:1→7:1→5:1", proc_ev),
        ])
    unresolved = [
        "No supporting-information file was explicitly associated; omitted experimental details remain missing.",
        "Product connectivity and stereochemistry were not encoded as SMILES and require chemical review.",
    ]
    if row["entry"] in (1, 2, 3, 4, 6):
        unresolved.append(
            "Source conflict: Table 1 reports 5 mol% trans-[RhCl(CO)(PPh3)2], while the exact procedure prints trans-[RhCl(CO)(PPh2)3] and gives a catalyst mmol amount near one tenth of substrate amount; both printed facts are retained without reconciliation."
        )
    if row["entry"] in (3, 4, 6):
        unresolved.append("The structures of the cross-products are described as tentatively assigned by NMR comparison.")
    if row["entry"] == 5:
        unresolved.append("The structure of 6ce is described as tentatively assigned; table dashes are not interpreted as zero or not detected.")
    if row["entry"] == 7:
        unresolved.append("Table dashes are not interpreted as zero or not detected.")
    notes = [fact("Scheme 1 is the same experiment as Table 1 entry 1 and the page-3 typical procedure; it is not counted again.", evidence)] if row["entry"] == 1 else []
    records.append(base_record(
        rid, "substrate_scope_entry", evidence, participants,
        [{"step_id": "cross_cyclization", "participant_ids": [p["entity_id"] for p in participants], "conditions": conditions}],
        outcomes, notes, unresolved,
    ))


table2 = [
    {"entry": 1, "ratio": "1:1", "loading": 10, "condition": "A", "time": 12, "y7": 29, "y4": 19},
    {"entry": 2, "ratio": "1:2", "loading": 10, "condition": "A", "time": 11, "y7": 28, "y4": 14},
    {"entry": 3, "ratio": "1:1", "loading": 10, "condition": "B", "time": 25, "y7": 30, "y4": 20},
    {"entry": 4, "ratio": "1:2", "loading": 10, "condition": "B", "time": 22, "y7": 29, "y4": 24},
    {"entry": 5, "ratio": "1:1", "loading": 5, "condition": "C", "time": 24, "y7": 36, "y4": 11},
    {"entry": 6, "ratio": "1:1.5", "loading": 5, "condition": "C", "time": 24, "y7": 44, "y4": 8},
]

table2_ids = []
for row in table2:
    rid = f"table2_entry_{row['entry']}"
    table2_ids.append(f"{DOC}:{rid}")
    evidence = [ev(3)] + ([ev(5)] if row["entry"] == 6 else [])
    e = [ev(3)]
    exact = [ev(5)]
    if row["condition"] == "A":
        a_amount = 0.5
        feed_vol, reactor_vol = 24, None
    elif row["condition"] == "B":
        a_amount = (0.25, 0.5, "0.25–0.5 mmol")
        feed_vol, reactor_vol = (6, 12, "6–12 mL"), (6, 12, "6–12 mL")
    else:
        a_amount = 0.5
        feed_vol, reactor_vol = 10, 2
    if row["entry"] == 6:
        p2a_amounts = amount_fields(exact, mass=119, amount=0.5)
        p1f_amounts = amount_fields(exact, mass=105, amount=0.75)
        cat_amounts = amount_fields(exact, mass=17, amount=0.025) + amount_fields(e, loading=5)
    else:
        p2a_amounts = amount_fields(e, amount=a_amount)
        p1f_amounts = []
        cat_amounts = amount_fields(e, loading=row["loading"])
    participants = [
        participant("reactant_2a", "reactant", "2a", evidence, SMILES["2a"], p2a_amounts,
                    name="dimethyl 2-bis(2,3-butadienyl)malonate"),
        participant("reactant_1f", "reactant", "1f", evidence, SMILES["1f"], p1f_amounts,
                    name="bis(2,3-butadienyl)sulfide"),
        participant("rh_catalyst", "catalyst", "trans-[RhCl(CO)(PPh3)2]", evidence, None, cat_amounts),
        participant("product_7af", "product", "7af", evidence, None,
                    amount_fields(exact, mass=83) if row["entry"] == 6 else []),
        participant("product_4aa", "product", "4aa", evidence, None,
                    amount_fields(exact, mass=9) if row["entry"] == 6 else []),
    ]
    if row["condition"] == "A":
        participants.append(participant("toluene", "solvent", "toluene", evidence, SMILES["toluene"], amount_fields(e, volume=feed_vol)))
    else:
        participants.extend([
            participant("feed_toluene", "solvent", "toluene (feed solution)", evidence, SMILES["toluene"], amount_fields(e if row["entry"] != 6 else exact, volume=feed_vol)),
            participant("reactor_toluene", "solvent", "toluene (reactor solution)", evidence, SMILES["toluene"], amount_fields(e if row["entry"] != 6 else exact, volume=reactor_vol)),
        ])
    conditions = [
        field("2a_to_1f_ratio", row["ratio"], e),
        field("time", q(row["time"], "h"), e),
        field("temperature", "reflux", e),
    ]
    if row["condition"] in ("B", "C"):
        conditions.append(field("operation", "syringe-pump injection", e))
    if row["entry"] == 6:
        conditions.extend([
            field("addition_time", q(10, "h"), exact),
            field("atmosphere", "argon", exact),
            field("operation", "two-necked flask equipped with condenser and argon inlet; stirred until complete by TLC", exact),
            field("workup", "solvent removed", exact),
            field("purification", "silica-gel column chromatography", exact),
        ])
    outcomes = [
        field("isolated_yield", q(row["y7"], "%"), evidence, ["product_7af"]),
        field("isolated_yield", q(row["y4"], "%"), evidence, ["product_4aa"]),
        field("yield_measurement_basis", "isolated products", e),
    ]
    unresolved = [
        "No supporting-information file was explicitly associated; omitted experimental details remain missing.",
        "Product connectivity and stereochemistry were not encoded as SMILES and require chemical review.",
        "The table gives the 2a/1f ratio but does not state a separate mmol amount for 1f except in the exact entry-6 procedure.",
    ]
    if row["entry"] != 6:
        unresolved.append("Workup, purification, atmosphere, and exact feed duration are not reported for this row.")
    records.append(base_record(
        rid, "optimization_entry", evidence, participants,
        [{"step_id": f"condition_{row['condition']}", "participant_ids": [p["entity_id"] for p in participants], "conditions": conditions}],
        outcomes, [], unresolved,
    ))


# A specific unsuccessful experiment stated in the Results section.
failure_id = f"{DOC}:bisallene_1e_self_cyclization_failure"
records.append(base_record(
    "bisallene_1e_self_cyclization_failure", "reported_experiment", [ev(2)],
    [
        participant("reactant_1e", "reactant", "1e", [ev(2)], SMILES["1e"]),
        participant("rh_i_catalyst", "catalyst", "Rh(I) catalyst", [ev(2)]),
        participant("product_3ee", "product", "3ee", [ev(2)]),
    ],
    [{"step_id": "attempted_self_cyclization", "participant_ids": ["reactant_1e", "rh_i_catalyst", "product_3ee"], "conditions": []}],
    [field("formation_of_3ee", "failed to afford", [ev(2)], ["product_3ee"])],
    [],
    [
        "The source does not report catalyst identity/loading, solvent, temperature, time, scale, workup, or detection limit for this failed experiment.",
        "No supporting-information file was explicitly associated.",
    ],
))


# Proposed Scheme 2 pathway; retained as mechanism rather than as an additional experiment.
mechanism_id = f"{DOC}:scheme2_proposed_mechanism"
mechanism_participants = [
    participant("bisallene_2", "reactant", "2 (Y=CE2)", [ev(4)]),
    participant("bisallene_1f", "reactant", "1f", [ev(4)], SMILES["1f"]),
    participant("rh_i", "catalyst", "[Rh(I)]", [ev(4)]),
]
for label in ("8", "9", "10", "11", "13", "14"):
    mechanism_participants.append(participant(f"intermediate_{label}", "unspecified_agent", label, [ev(4)]))
for label in ("7", "12", "4"):
    mechanism_participants.append(participant(f"product_{label}", "product", label, [ev(4)]))
mechanism_steps = [
    {"step_id": "step_1", "participant_ids": ["bisallene_2", "rh_i", "intermediate_8"], "conditions": [field("operation", "cyclometallation", [ev(4)])]},
    {"step_id": "step_2", "participant_ids": ["intermediate_8", "bisallene_1f", "intermediate_9"], "conditions": [field("operation", "sulfur coordination and regioselective carbometallation", [ev(2), ev(4)])]},
    {"step_id": "step_3", "participant_ids": ["intermediate_9", "intermediate_10", "intermediate_11"], "conditions": [field("operation", "intramolecular carbometallation", [ev(2), ev(4)])]},
    {"step_id": "step_4", "participant_ids": ["intermediate_10", "intermediate_11", "product_7", "rh_i"], "conditions": [field("operation", "reductive elimination", [ev(4)])]},
    {"step_id": "step_5", "participant_ids": ["intermediate_8", "bisallene_2", "intermediate_13"], "conditions": [field("operation", "carbometallation with a second bisallene molecule", [ev(2), ev(4)])]},
    {"step_id": "step_6", "participant_ids": ["intermediate_13", "intermediate_14", "rh_i"], "conditions": [field("operation", "reductive elimination", [ev(4)])]},
    {"step_id": "step_7", "participant_ids": ["intermediate_14", "product_4"], "conditions": [field("operation", "intramolecular Diels–Alder reaction", [ev(2), ev(4)])]},
]
records.append(base_record(
    "scheme2_proposed_mechanism", "mechanism", [ev(2), ev(4)], mechanism_participants, mechanism_steps,
    [field("product_12_observation", "not observed", [ev(2), ev(4)], ["product_12"])],
    [fact("The authors describe intermediate 8 as the major intermediate but state that it is too early to exclude completely a second pathway reported previously.", [ev(2)])],
    [
        "All intermediates and elementary steps are proposed, not independently isolated experimental facts.",
        "Generic E substituents and the detailed structures/stereochemistry were not encoded as SMILES.",
    ],
))


OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"records": len(records), "output": str(OUT)}, ensure_ascii=False))

