#!/usr/bin/env python3
"""Build source-derived machine records for PDF pages 1-6.

This is a reproducible extraction snapshot.  It does not certify chemistry or
structures; reaction_tools.merge deliberately quarantines every fact for review.
"""
from __future__ import annotations

import json
from pathlib import Path


DOC = "doc_065298449e790f13"
OUT = Path(__file__).with_name("pages_0001_0006_records.json")


def evid(*pages: int) -> list[str]:
    result = []
    for page in pages:
        result += [f"{DOC}:page{page}:text", f"{DOC}:page{page}:image"]
    return result


def fact(value, ev):
    return {
        "value": value,
        "evidence_ids": list(ev) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def field(name, value, ev, targets=None):
    item = {"name": name, "fact": fact(value, ev)}
    if targets:
        item["target_entity_ids"] = list(targets)
    return item


def participant(entity_id, role, label, name, ev, smiles=None, amounts=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, ev),
        "name": fact(name, ev),
        "smiles": fact(smiles, ev) if smiles else fact(None, []),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": amounts or [],
    }


def amount(name, number, unit, ev):
    return field(name, {"number": number, "unit": unit}, ev)


def range_amount(name, minimum, maximum, unit, raw_text, ev):
    return field(
        name,
        {"minimum": minimum, "maximum": maximum, "unit": unit, "raw_text": raw_text},
        ev,
    )


def base_record(rid, kind, ev, participants, steps, outcomes, notes=None, unresolved=None):
    return {
        "record_id": f"{DOC}:{rid}",
        "document_id": DOC,
        "source_reaction_id": rid,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": list(dict.fromkeys(ev)),
        "participants": participants,
        "steps": steps,
        "outcomes": outcomes,
        "notes": notes or [],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved or [],
        },
    }


PHSECL = "Cl[Se]c1ccccc1"
MECN = "CC#N"
WATER = "O"


def optimization_record(entry, ratio, hours, yield_percent, water_first=False):
    ev = evid(1)
    substrate = participant(
        "substrate_1a", "reactant", "1a", "ethyl 2-methyl-2,3-octadienoate", ev,
        "CCOC(=O)C(C)=C=C(CCCC)",
        [amount("amount", 0.2, "mmol", ev)],
    )
    reagent = participant(
        "phsecl", "reagent", "PhSeCl", "phenylselenyl chloride", ev, PHSECL,
        [amount("equivalents", 2, "equiv", ev)],
    )
    mecn = participant(
        "mecn", "solvent", "CH3CN", "acetonitrile", ev, MECN,
        [amount("volume", 2, "mL", ev)],
    )
    participants = [substrate, reagent, mecn]
    if ratio != "100:0":
        participants.append(participant("water", "solvent", "H2O", "water", ev, WATER))
    product = participant(
        "product_2a", "product", "2a",
        "5-(n-butyl)-3-methyl-4-phenylselanyl-5H-furan-2-one", ev,
        "O=C1OC(CCCC)C([Se]c2ccccc2)=C1C",
    )
    participants.append(product)
    operations = "H2O was added to PhSeCl in CH3CN before immediate addition of 1a." if water_first else None
    conditions = [
        field("temperature", "r.t.", ev),
        field("time", {"number": hours, "unit": "h"}, ev),
        field("solvent_ratio", f"CH3CN/H2O={ratio}", ev),
        field("operation", operations, ev),
        field("atmosphere", None, ev),
        field("workup", None, ev),
        field("purification", None, ev),
    ]
    return base_record(
        f"table1_entry_{entry}", "optimization_entry", ev, participants,
        [{"step_id": "reaction", "participant_ids": [p["entity_id"] for p in participants], "conditions": conditions}],
        [
            field("isolated_yield", {"number": yield_percent, "unit": "%"}, ev, ["product_2a"]),
            field("yield_measurement_basis", "isolated", ev, ["product_2a"]),
        ],
        notes=[fact("Table 1 optimization row; page-image reading controls where OCR differs.", ev)],
        unresolved=[
            "Atmosphere, workup, and purification are not reported for this optimization row.",
            "Candidate structures are machine interpretations and require chemical review.",
            "No supporting-information file was explicitly associated.",
        ],
    )


records = [
    optimization_record(1, "100:0", 6.5, 13, False),
    optimization_record(2, "800:1", 1.5, 26, True),
    # Original page image clearly reads 1 h and 45%; extracted text incorrectly reads 14 and 5.
    optimization_record(3, "100:1", 1, 45, True),
    optimization_record(4, "10:1", 1, 100, True),
]


# A prose-described low-yield attempt is not assigned to a Table 1 row because
# the cited Ref. 10 protocol is not reproduced in the supplied source.
ev1 = evid(1)
low_participants = [
    participant("substrate_1a", "reactant", "1a", "ethyl 2-methyl-2,3-octadienoate", ev1,
                "CCOC(=O)C(C)=C=C(CCCC)"),
    participant("phsecl", "reagent", "PhSeCl", "phenylselenyl chloride", ev1, PHSECL),
    participant("product_2a", "product", "2a",
                "5-(n-butyl)-3-methyl-4-phenylselanyl-5H-furan-2-one", ev1,
                "O=C1OC(CCCC)C([Se]c2ccccc2)=C1C"),
    participant("unidentified_product", "product", "unidentified product", "unidentified product", ev1),
]
records.append(base_record(
    "prose_ref10_protocol_attempt", "reported_experiment", ev1, low_participants,
    [{"step_id": "reaction", "participant_ids": [p["entity_id"] for p in low_participants], "conditions": [
        field("operation", "Reaction conducted according to the procedure described in Ref. 10.", ev1),
        field("temperature", None, ev1), field("time", None, ev1), field("atmosphere", None, ev1),
        field("workup", None, ev1), field("purification", None, ev1),
    ]}],
    [field("reported_yield", "low", ev1, ["product_2a"]), field("yield_measurement_basis", None, ev1, ["product_2a"])],
    notes=[fact("An unidentified product was also formed.", ev1)],
    unresolved=[
        "The Ref. 10 procedure, numerical yield, time, temperature, scale, and isolation details are absent from the supplied pages.",
        "This prose experiment may overlap a screening attempt, but the source does not identify it as a Table 1 entry.",
        "No supporting-information file was explicitly associated.",
    ],
))


# Prior literature is retained as literature_example, not attributed to this paper.
lit_parts = [
    participant("allenoic_acids", "reactant", "2,3-allenoic acids", "generic 2,3-allenoic acids", ev1),
    participant("phy_cl", "reagent", "PhYCl (Y=S, Se)", "phenylsulfenyl or phenylselenyl chloride", ev1),
    participant("butenolides", "product", "beta-organosulfur/selenium butenolides",
                "generic beta-organosulfur- or beta-organoselenium-substituted butenolides", ev1),
]
records.append(base_record(
    "prior_allenoic_acid_electrophilic_cyclization", "literature_example", ev1, lit_parts, [],
    [field("reported_yield", "moderate", ev1, ["butenolides"]), field("yield_measurement_basis", None, ev1, ["butenolides"])],
    notes=[fact("Cited as prior work (Ref. 8), not a new experiment in this paper.", ev1)],
    unresolved=["Generic structures and detailed primary-source conditions are not supplied on page 1."],
))


scope_rows = [
    # entry, R1, R2, R3, substrate, product, time, yield, ratio, page(s), exact masses/mmol/volumes/product mass
    (1, "n-C4H9", "H", "CH3", "1a", "2a", 1, 100, "10:1", (2, 3), (37.1, .20, 77.2, .40, .4, 4, 64.9)),
    (2, "n-C4H9", "H", "n-C3H7", "1b", "2b", 1, 92, "10:1", (2, 4), (41.8, .20, 77.4, .40, .4, 4, 62.2)),
    (3, "n-C4H9", "H", "Bn", "1c", "2c", 1, 96, "10:1", (2, 4), (52.6, .20, 79.0, .41, .4, 4, 75.8)),
    (4, "n-C7H15", "H", "CH3", "1d", "2d", 2, 94, "10:1", (2, 4), (43.7, .20, 75.2, .40, .4, 4, 64.7)),
    (5, "n-C7H15", "H", "n-C3H7", "1e", "2e", 1, 95, "10:1", (2, 4), (51.7, .21, 76.1, .40, .4, 4, 73.7)),
    (6, "n-C6H13", "H", "Bn", "1f", "2f", 3, 82, "10:1", (2, 4), (56.8, .20, 76.2, .40, .4, 4, 67.5)),
    (7, "Ph", "H", "CH3", "1g", "2g", 1, 95, "10:1", (2, 5), (39.9, .20, 75.9, .40, .4, 4, 61.8)),
    (8, "Ph", "H", "n-C3H7", "1h", "2h", 1, 99, "10:1", (2, 5), (45.6, .20, 79.2, .41, .4, 4, 70.0)),
    (9, "Ph", "H", "Bn", "1i", "2i", 1, 80, "10:1", (2, 5), (52.1, .19, 79.3, .41, .4, 4, 60.5)),
    (10, "alpha-Naphthyl", "H", "CH3", "1j", "2j", 1, 79, "10:1", (2, 5), (53.0, .21, 77.0, .40, .4, 4, 63.0)),
    (11, "alpha-Naphthyl", "H", "n-C3H7", "1k", "2k", 1, 77, "10:1", (2, 5, 6), (55.1, .20, 77.8, .41, .4, 4, 61.4)),
    (12, "CH3", "CH3", "H", "1m", "2m", 1, 55, "10:1", (2, 6), (42.4, .30, 116.8, .61, .6, 6, 44.6)),
    (13, "n-C4H9", "H", "H", "1n", "2n", 3.5, 55, "10:1", (2, 6), (36.9, .22, 77.9, .41, .4, 4, 35.8)),
    (14, "n-C7H15", "H", "H", "1o", "2o", 1.5, 52, "10:1", (2, 6), (43.6, .21, 77.2, .40, .4, 4, 36.7)),
    (15, "H", "H", "n-C3H7", "1p", "2p", 1, 22, "10:1", (2, 6), (47.6, .31, 117.1, .61, .6, 6, 19.2)),
    (16, "H", "H", "n-C3H7", "1p", "2p", 1, 49, "1:1", (2, 6), (47.3, .31, 111.5, .58, 2, 2, 42.3)),
    (17, "H", "H", "Bn", "1q", "2q", 1, 48, "1:1", (2, 6), (59.8, .30, 115.3, .60, 2, 2, 46.8)),
    (18, "Ph", "CH3", "CH3", "1r", "2r", 1, 100, "10:1", (2,), None),
    (19, "Ph", "CH3", "CH3", "1r", "2r", 1, 92, "no water", (2,), None),
    (20, "-(CH2)5-", "linked", "CH3", "1s", "2s", 1, 96, "10:1", (2,), None),
    (21, "-(CH2)5-", "linked", "CH3", "1s", "2s", 1, 84, "no water", (2,), None),
]


product_names = {
    "2a": "5-(n-butyl)-3-methyl-4-phenylselanyl-5H-furan-2-one",
    "2b": "5-(n-butyl)-4-phenylselanyl-3-(n-propyl)-5H-furan-2-one",
    "2c": "3-benzyl-5-(n-butyl)-4-phenylselanyl-5H-furan-2-one",
    "2d": "5-(n-heptyl)-3-methyl-4-phenylselanyl-5H-furan-2-one",
    "2e": "5-(n-heptyl)-4-phenylselanyl-3-(n-propyl)-5H-furan-2-one",
    "2f": "3-benzyl-5-(n-hexyl)-4-phenylselanyl-5H-furan-2-one",
    "2g": "3-methyl-5-phenyl-4-phenylselanyl-5H-furan-2-one",
    "2h": "5-phenyl-4-phenylselanyl-3-(n-propyl)-5H-furan-2-one",
    "2i": "3-benzyl-5-phenyl-4-phenylselanyl-5H-furan-2-one",
    "2j": "3-methyl-5-(1-naphthyl)-4-phenylselanyl-5H-furan-2-one",
    "2k": "5-(1-naphthyl)-4-phenylselanyl-3-(n-propyl)-5H-furan-2-one",
    "2m": "5,5-dimethyl-4-phenylselanyl-5H-furan-2-one",
    "2n": "5-(n-butyl)-4-phenylselanyl-5H-furan-2-one",
    "2o": "5-(n-heptyl)-4-phenylselanyl-5H-furan-2-one",
    "2p": "4-phenylselanyl-3-(n-propyl)-5H-furan-2-one",
    "2q": "3-benzyl-4-phenylselanyl-5H-furan-2-one",
    "2r": "3,5-dimethyl-5-phenyl-4-phenylselanyl-5H-furan-2-one",
    "2s": "3-methyl-4-phenylselanyl-1-oxaspiro[4.5]dec-3-en-2-one",
}


product_smiles = {
    "2a": "O=C1OC(CCCC)C([Se]c2ccccc2)=C1C",
    "2b": "O=C1OC(CCCC)C([Se]c2ccccc2)=C1CCC",
    "2c": "O=C1OC(CCCC)C([Se]c2ccccc2)=C1Cc2ccccc2",
    "2d": "O=C1OC(CCCCCCC)C([Se]c2ccccc2)=C1C",
    "2e": "O=C1OC(CCCCCCC)C([Se]c2ccccc2)=C1CCC",
    "2f": "O=C1OC(CCCCCC)C([Se]c2ccccc2)=C1Cc2ccccc2",
    "2g": "O=C1OC(c2ccccc2)C([Se]c2ccccc2)=C1C",
    "2h": "O=C1OC(c2ccccc2)C([Se]c2ccccc2)=C1CCC",
    "2i": "O=C1OC(c2ccccc2)C([Se]c2ccccc2)=C1Cc2ccccc2",
    "2j": "O=C1OC(c2cccc3ccccc23)C([Se]c2ccccc2)=C1C",
    "2k": "O=C1OC(c2cccc3ccccc23)C([Se]c2ccccc2)=C1CCC",
    "2m": "O=C1OC(C)(C)C([Se]c2ccccc2)=C1",
    "2n": "O=C1OC(CCCC)C([Se]c2ccccc2)=C1",
    "2o": "O=C1OC(CCCCCCC)C([Se]c2ccccc2)=C1",
    "2p": "O=C1OCC([Se]c2ccccc2)=C1CCC",
    "2q": "O=C1OCC([Se]c2ccccc2)=C1Cc2ccccc2",
    "2r": "O=C1OC(C)(c2ccccc2)C([Se]c2ccccc2)=C1C",
    "2s": "O=C1OC2(CCCCC2)C([Se]c2ccccc2)=C1C",
}


def allene_smiles(r1, r2, r3):
    frag = {
        "n-C4H9": "CCCC", "n-C7H15": "CCCCCCC", "n-C6H13": "CCCCCC",
        "CH3": "C", "n-C3H7": "CCC", "Bn": "Cc1ccccc1", "Ph": "c1ccccc1",
        "alpha-Naphthyl": "c1cccc2ccccc12",
    }
    if r1 == "-(CH2)5-":
        terminal = "C1CCCCC1"
    elif r1 == "H" and r2 == "H":
        terminal = "C"
    elif r2 == "H":
        terminal = f"C({frag[r1]})"
    else:
        terminal = f"C({frag[r1]}){frag[r2]}"
    alpha = "C" if r3 == "H" else f"C({frag[r3]})"
    return f"CCOC(=O){alpha}=C={terminal}"


for entry, r1, r2, r3, substrate_label, product_label, hours, yld, ratio, pages, exact in scope_rows:
    ev = evid(*pages)
    sub_amounts = []
    reagent_amounts = [amount("reported_equivalents", 2, "equiv", evid(2))]
    mecn_amounts = []
    water_amounts = []
    product_amounts = []
    if exact:
        smass, smmol, rmass, rmmol, water_ml, mecn_ml, pmass = exact
        proc_ev = evid(*[p for p in pages if p != 2])
        sub_amounts = [amount("mass", smass, "mg", proc_ev), amount("amount", smmol, "mmol", proc_ev)]
        reagent_amounts += [amount("mass", rmass, "mg", proc_ev), amount("amount", rmmol, "mmol", proc_ev)]
        mecn_amounts = [amount("volume", mecn_ml, "mL", proc_ev)]
        water_amounts = [amount("volume", water_ml, "mL", proc_ev)]
        product_amounts = [amount("mass", pmass, "mg", proc_ev)]
    else:
        sub_amounts = [range_amount("reaction_scale", .2, .3, "mmol", "0.2-0.3 mmol", evid(2))]
        mecn_amounts = [range_amount("volume", 4, 6, "mL", "4-6 mL", evid(2))]

    substrate = participant(
        f"substrate_{substrate_label}", "reactant", substrate_label,
        f"ethyl 2,3-allenoate {substrate_label} (R1={r1}, R2={r2}, R3={r3})", ev,
        allene_smiles(r1, r2, r3), sub_amounts,
    )
    reagent = participant("phsecl", "reagent", "PhSeCl", "phenylselenyl chloride", ev, PHSECL, reagent_amounts)
    mecn = participant("mecn", "solvent", "CH3CN", "acetonitrile", ev, MECN, mecn_amounts)
    product = participant(
        f"product_{product_label}", "product", product_label, product_names[product_label], ev,
        product_smiles[product_label], product_amounts,
    )
    participants = [substrate, reagent, mecn]
    if ratio != "no water":
        participants.append(participant("water", "solvent", "H2O", "water", ev, WATER, water_amounts))
    participants.append(product)
    if entry in (15, 16, 17):
        participants.append(participant("unidentified_product", "product", "unidentified product", "unidentified product", ev))

    conditions = [
        field("temperature", "r.t.", evid(2)),
        field("time", {"number": hours, "unit": "h"}, evid(2)),
        field("solvent_ratio", f"CH3CN/H2O={ratio}" if ratio != "no water" else "no water added", evid(2)),
        field("atmosphere", None, ev),
        field("workup", "mixture evaporated directly" if entry == 1 else None, evid(3) if entry == 1 else ev),
        field("purification", "silica-gel column chromatography; petroleum ether/ethyl acetate 10:1" if entry == 1 else None,
              evid(3) if entry == 1 else ev),
    ]
    notes = [fact(f"Table 2 substituents: R1={r1}; R2={r2}; R3={r3}.", evid(2))]
    if entry in (15, 16, 17):
        notes.append(fact("Another unidentified product was also formed.", evid(2)))
    if ratio == "no water":
        notes.append(fact("Table 2 footnote e: no water was added.", evid(2)))
    if ratio == "1:1":
        notes.append(fact("Table 2 footnote d overrides the standard solvent ratio to CH3CN/H2O=1:1.", evid(2)))

    unresolved = [
        "Atmosphere is not reported.",
        "Candidate structures are machine interpretations and require chemical review.",
        "No supporting-information file was explicitly associated.",
    ]
    if entry != 1:
        unresolved.append("Workup and purification are not reported on the inspected pages for this entry.")
    if exact is None:
        unresolved.append("Only the Table 2 shared scale/solvent ranges are available; entry-specific masses and volumes are missing on pages 1-6.")
    if entry in (15, 16, 17):
        unresolved.append("The co-formed product is unidentified and has no reported amount or structure.")

    records.append(base_record(
        f"table2_entry_{entry}", "substrate_scope_entry", ev, participants,
        [{"step_id": "reaction", "participant_ids": [p["entity_id"] for p in participants], "conditions": conditions}],
        [
            field("isolated_yield", {"number": yld, "unit": "%"}, evid(2), [f"product_{product_label}"]),
            field("yield_measurement_basis", "isolated", evid(2), [f"product_{product_label}"]),
        ],
        notes=notes, unresolved=unresolved,
    ))


# Scheme 1, first arrow: 1t gives Z-3t rather than butenolide 2t.
ev23 = evid(2, 3)
scheme1a_parts = [
    participant("substrate_1t", "reactant", "1t", "methyl 2,3-butadienoate", ev23, "COC(=O)C=C=C"),
    participant("phsecl", "reagent", "PhSeCl", "phenylselenyl chloride", ev23, PHSECL,
                [amount("equivalents", 2, "equiv", evid(2))]),
    participant("mecn", "solvent", "MeCN", "acetonitrile", ev23, MECN),
    participant("water", "solvent", "H2O", "water", ev23, WATER),
    participant("product_3t", "product", "Z-3t", "methyl 4-chloro-3-phenylselanylbut-2(Z)-enoate", ev23,
                "COC(=O)C=C(CCl)[Se]c1ccccc1"),
]
records.append(base_record(
    "scheme1_1t_to_3t", "reported_experiment", ev23, scheme1a_parts,
    [{"step_id": "reaction", "participant_ids": [p["entity_id"] for p in scheme1a_parts], "conditions": [
        field("temperature", "r.t.", ev23), field("time", None, ev23),
        field("solvent_ratio", "MeCN/H2O=10:1", evid(2)), field("atmosphere", None, ev23),
        field("workup", None, ev23), field("purification", None, ev23),
    ]}],
    [
        field("isolated_yield", {"number": 81, "unit": "%"}, evid(3), ["product_3t"]),
        field("yield_measurement_basis", "isolated", evid(3), ["product_3t"]),
        field("stereoselectivity", "only Z-3t was isolated", evid(3), ["product_3t"]),
    ],
    notes=[fact("Butenolide 2t was not obtained; stereochemistry was assigned by NOE study of 3t and 4t.", evid(2, 3))],
    unresolved=[
        "Reaction time, scale, solvent volumes, atmosphere, workup, and purification are not reported on pages 1-6.",
        "The candidate SMILES preserves connectivity but does not encode the reported Z geometry.",
        "No supporting-information file was explicitly associated.",
    ],
))


# Scheme 1, second arrow is a separate reduction stage; its detailed procedure is outside pages 1-6.
scheme1b_parts = [
    participant("substrate_3t", "reactant", "3t", "methyl 4-chloro-3-phenylselanylbut-2(Z)-enoate", evid(2),
                "COC(=O)C=C(CCl)[Se]c1ccccc1"),
    participant("dibal_h", "reagent", "DIBAL-H", "diisobutylaluminium hydride", evid(2)),
    participant("product_4t", "product", "4t", "4-chloro-3-phenylselanylbut-2(Z)-en-1-ol", evid(2),
                "OCC=C(CCl)[Se]c1ccccc1"),
]
records.append(base_record(
    "scheme1_3t_to_4t", "reported_experiment", evid(2, 3), scheme1b_parts,
    [{"step_id": "reduction", "participant_ids": [p["entity_id"] for p in scheme1b_parts], "conditions": [
        field("temperature", None, evid(2)), field("time", None, evid(2)), field("solvent", None, evid(2)),
        field("atmosphere", None, evid(2)), field("workup", None, evid(2)), field("purification", None, evid(2)),
    ]}],
    [field("reported_yield", None, evid(2), ["product_4t"]), field("yield_measurement_basis", None, evid(2), ["product_4t"])],
    notes=[fact("Scheme 1 shows 4t was prepared for the NOE-based stereochemical study.", evid(2, 3))],
    unresolved=[
        "Pages 1-6 show only DIBAL-H above the arrow; quantities, solvent, time, temperature, workup, purification, and yield are absent from the covered range.",
        "The candidate SMILES does not encode the reported Z geometry.",
    ],
))


# Scheme 2 is explicitly proposed and remains a mechanism record.
mechanism_parts = [
    participant("generic_allenoate_1", "reactant", "1", "generic 2,3-allenoate", evid(3)),
    participant("phse_electrophile", "reagent", "PhSe+", "phenylselenyl electrophile", evid(3)),
    participant("water", "reagent", "H2O", "water", evid(3), WATER),
    participant("chloride", "reagent", "Cl-", "chloride", evid(3), "[Cl-]"),
    participant("intermediate_5", "unspecified_agent", "5", "proposed seleniranium-like intermediate 5", evid(3)),
    participant("intermediate_6", "unspecified_agent", "6", "proposed cyclic oxonium intermediate 6", evid(3)),
    participant("butenolide_2", "product", "2", "generic phenylselanyl butenolide", evid(3)),
    participant("alcohol_7", "product", "7", "alcohol R4OH", evid(3)),
    participant("product_3t", "product", "3t", "methyl 4-chloro-3-phenylselanylbut-2(Z)-enoate", evid(3),
                "COC(=O)C=C(CCl)[Se]c1ccccc1"),
]
records.append(base_record(
    "scheme2_proposed_mechanism", "mechanism", evid(3), mechanism_parts, [], [],
    notes=[
        fact("Proposed sequence: electrophilic addition to 1 gives 5; carbonyl-oxygen cyclization gives 6; water attack, proton transfer, and R4OH elimination give 2 and 7.", evid(3)),
        fact("For unsubstituted 1t, chloride attack on 5t is proposed to give 3t.", evid(3)),
    ],
    unresolved=[
        "The source labels this pathway plausible; the interaction of PhSeCl with water and the stereochemical outcome remain unclear.",
        "Generic R-group intermediates are not assigned SMILES.",
    ],
))


# Scheme 3 mechanistic experiment gives two isolated products with separate yields.
scheme3_parts = [
    participant("substrate_1u", "reactant", "1u",
                "3-phenylpropyl 2-methyl-3-phenyl-2,3-butadienoate", evid(3),
                "CC(=C=C(c1ccccc1))C(=O)OCCCc1ccccc1"),
    participant("phsecl", "reagent", "PhSeCl", "phenylselenyl chloride", evid(3), PHSECL,
                [amount("equivalents", 2, "equiv", evid(3))]),
    participant("mecn", "solvent", "CH3CN", "acetonitrile", evid(3), MECN),
    participant("water", "solvent", "H2O", "water", evid(3), WATER),
    participant("product_2g", "product", "2g", product_names["2g"], evid(3), product_smiles["2g"]),
    participant("product_7u", "product", "7u", "3-phenylpropanol", evid(3), "OCCCc1ccccc1"),
]
records.append(base_record(
    "scheme3_mechanistic_probe", "reported_experiment", evid(3), scheme3_parts,
    [{"step_id": "reaction", "participant_ids": [p["entity_id"] for p in scheme3_parts], "conditions": [
        field("temperature", "r.t.", evid(3)), field("time", None, evid(3)),
        field("solvent_ratio", "CH3CN/H2O=10:1", evid(3)), field("atmosphere", None, evid(3)),
        field("workup", None, evid(3)), field("purification", None, evid(3)),
    ]}],
    [
        field("isolated_yield_2g", {"number": 89, "unit": "%"}, evid(3), ["product_2g"]),
        field("isolated_yield_7u", {"number": 80, "unit": "%"}, evid(3), ["product_7u"]),
        field("yield_measurement_basis", "isolated", evid(3), ["product_2g", "product_7u"]),
    ],
    notes=[fact("The authors state that this experiment supports the proposed alcohol-elimination mechanism and the importance of water.", evid(3))],
    unresolved=[
        "Reaction time, scale, solvent volumes, atmosphere, workup, and purification are not reported on pages 1-6.",
        "Candidate structures are machine interpretations and require chemical review.",
        "No supporting-information file was explicitly associated.",
    ],
))


OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"records": len(records), "output": str(OUT)}, ensure_ascii=False))
