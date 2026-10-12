#!/usr/bin/env python3
"""Build machine-extracted records and coverage for PDF pages 1-2."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / "runs" / "current"
DOC = "doc_bfc61b953a4e78b8"
P1T = f"{DOC}:page1:text"
P1I = f"{DOC}:page1:image"
P2T = f"{DOC}:page2:text"
P2I = f"{DOC}:page2:image"
P1 = [P1T, P1I]
P2 = [P2T, P2I]


def fact(value, evidence):
    return {
        "value": value,
        "evidence_ids": list(evidence) if value is not None else list(evidence),
        "verification": "missing" if value is None else "unreviewed",
    }


def field(name, value, evidence, target=None):
    item = {"name": name, "fact": fact(value, evidence)}
    if target:
        item["target_entity_ids"] = list(target)
    return item


def participant(entity_id, role, label, evidence, *, name=None, smiles=None, amounts=None):
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


def qty(number, unit, raw_text=None):
    value = {"number": number, "unit": unit}
    if raw_text:
        value["raw_text"] = raw_text
    return value


def rng(minimum, maximum, unit, raw_text):
    return {"minimum": minimum, "maximum": maximum, "unit": unit, "raw_text": raw_text}


SMILES_1 = {
    "1a": "CC(=C=Cc1ccccc1)C(=O)O",
    "1b": "CC(=C=CC)C(=O)O",
    "1c": "O=C(O)C(Cc1ccccc1)=C=CC",
    "1d": "CC(=C=C1CCCCC1)C(=O)O",
    "1e": "O=C(O)C=C=CCCCCCCC",
    "1f": "O=C(O)C(Cc1ccccc1)=C=C",
    "1g": "CC(=C=Cc1cccc2ccccc12)C(=O)O",
    "1h": "CC(=C=C(CC)c1ccccc1)C(=O)O",
    "1i": "CC(=C=C(C)C)C(=O)O",
}

DESC_1 = {
    "1a": "2,3-allenoic acid 1a (R1=Me, R2=Ph, R3=H)",
    "1b": "2,3-allenoic acid 1b (R1=Me, R2=Me, R3=H)",
    "1c": "2,3-allenoic acid 1c (R1=Bn, R2=Me, R3=H)",
    "1d": "2,3-allenoic acid 1d (R1=Me; R2/R3=(CH2)5)",
    "1e": "2,3-allenoic acid 1e (R1=H, R2=n-C7H15, R3=H)",
    "1f": "2,3-allenoic acid 1f (R1=Bn, R2=H, R3=H)",
    "1g": "2,3-allenoic acid 1g (R1=Me, R2=1-Nap, R3=H)",
    "1h": "2,3-allenoic acid 1h (R1=Me, R2=Ph, R3=Et)",
    "1i": "2,3-allenoic acid 1i (R1=Me, R2=Me, R3=Me)",
}

SMILES_2 = {
    "2a": "C=C=CC1(O)CCCCC1",
    "2b": "C=C=CC(O)(C)C",
    "2c": "C=C=CCO",
    "2d": "C=C=CC(O)CCCCC",
    "2e": "C=C=CC(O)c1ccccc1",
    "2f": "C=C=CC(O)Cc1ccccc1",
}

DESC_2 = {
    "2a": "2,3-allenol 2a (R4/R5=(CH2)5)",
    "2b": "2,3-allenol 2b (R4=Me, R5=Me)",
    "2c": "2,3-allenol 2c (R4=H, R5=H)",
    "2d": "2,3-allenol 2d (R4=n-C5H11, R5=H)",
    "2e": "2,3-allenol 2e (R4=Ph, R5=H)",
    "2f": "2,3-allenol 2f (R4=Bn, R5=H)",
}


def acid(label, evidence, amount=None, entity="acid"):
    amounts = [field("amount", amount, evidence)] if amount else []
    return participant(entity, "reactant", label, evidence, name=DESC_1[label], smiles=SMILES_1[label], amounts=amounts)


def allenol(label, evidence, amount=None, entity="allenol"):
    amounts = [field("amount", amount, evidence)] if amount else []
    return participant(entity, "reactant", label, evidence, name=DESC_2[label], smiles=SMILES_2[label], amounts=amounts)


def pdcl2(evidence):
    return participant(
        "pdcl2", "catalyst", "PdCl2", evidence,
        name="palladium(II) chloride", smiles="[Cl-].[Cl-].[Pd+2]",
        amounts=[field("catalyst_loading", qty(5, "mol%", "5 mol %"), evidence)],
    )


def dma(evidence, volume):
    return participant(
        "dma", "solvent", "DMA", evidence,
        name="N,N-dimethylacetamide", smiles="CC(=O)N(C)C",
        amounts=[field("volume", volume, evidence)],
    )


def product(label, evidence, entity="product"):
    return participant(
        entity, "product", label, evidence,
        name=f"4-(1',3'-dien-2'-yl)-2(5H)-furanone derivative {label}",
    )


COMMON_UNRESOLVED = [
    "Yield measurement basis (for example isolated or assay) is not stated in the supplied main-text pages.",
    "The paper points to Supporting Information, but no SI was supplied or explicitly associated; workup, purification, and full procedures remain unavailable.",
    "Candidate SMILES were transcribed from the drawn substitution patterns and remain unverified against an independent chemical-structure review.",
]


def record(record_id, source_id, kind, evidence, participants, steps, outcomes, notes=None, unresolved=None):
    return {
        "record_id": f"{DOC}:{record_id}",
        "document_id": DOC,
        "source_reaction_id": source_id,
        "record_kind": kind,
        "status": "needs_review",
        "completeness": "partial",
        "evidence_ids": list(dict.fromkeys(evidence)),
        "participants": participants,
        "steps": steps,
        "outcomes": outcomes,
        "notes": [fact(value, ev) for value, ev in (notes or [])],
        "review": {
            "method": "model",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": list(unresolved or COMMON_UNRESOLVED),
        },
    }


def missing_operations(evidence):
    return [
        field("atmosphere", None, evidence),
        field("workup", None, evidence),
        field("purification", None, evidence),
    ]


def scope_record(table, entry, acid_label, allenol_label, product_label, yield_percent, evidence, allenol_amount,
                 *, exact_scheme1=False, stereochemistry=None):
    rid = f"{table}_entry{entry:02d}_{product_label.lower().replace('(e)-', 'e_')}"
    source = f"{table.replace('table', 'Table ')} entry {entry}"
    acid_amt = qty(0.25, "mmol", "0.25 mmol")
    participants = [
        acid(acid_label, evidence, acid_amt),
        allenol(allenol_label, evidence, allenol_amount),
        pdcl2(evidence),
        dma(evidence, qty(2, "mL", "2 mL") if exact_scheme1 else rng(2, 3, "mL", "2-3 mL")),
        product(product_label, evidence),
    ]
    if exact_scheme1:
        participants.append(product("4aa", evidence, "side_product"))
        time = qty(22, "h", "22 h")
    else:
        time = rng(8, 28, "h", "8-28 h")
    conditions = [field("temperature", qty(30, "°C", "30 °C"), evidence), field("time", time, evidence)]
    conditions.extend(missing_operations(evidence))
    outcomes = [
        field("yield", qty(yield_percent, "%", f"{yield_percent}%"), evidence, ["product"]),
        field("yield_measurement_basis", None, evidence, ["product"]),
    ]
    if exact_scheme1:
        outcomes.extend([
            field("yield", qty(4, "%", "4%"), evidence, ["side_product"]),
            field("yield_measurement_basis", None, evidence, ["side_product"]),
        ])
    if stereochemistry:
        outcomes.append(field("stereoselectivity", stereochemistry, evidence, ["product"]))
    notes = []
    if not exact_scheme1:
        notes.append(("The 8-28 h duration is the table-wide reported range; an entry-specific duration is not supplied.", evidence))
    else:
        notes.append(("Scheme 1 and Table 1 entry 1 are the same 1a/2a experiment and are represented once.", evidence))
    return record(rid, source, "substrate_scope_entry", evidence, participants,
                  [{"step_id": "cross_coupling_cyclization", "participant_ids": [p["entity_id"] for p in participants], "conditions": conditions}],
                  outcomes, notes)


records = []

# Table 1; Scheme 1 is deduplicated with entry 1 and contributes the exact 22 h and 4aa outcome.
table1 = [
    (1, "1a", "2a", "3aa", 67, qty(0.375, "mmol", "0.375 mmol"), True),
    (2, "1b", "2a", "3ba", 61, qty(0.375, "mmol", "0.375 mmol"), False),
    (3, "1a", "2b", "3ab", 59, qty(0.50, "mmol", "0.50 mmol"), False),
    (4, "1c", "2b", "3cb", 52, qty(0.375, "mmol", "0.375 mmol"), False),
    (5, "1d", "2a", "3da", 75, qty(0.375, "mmol", "0.375 mmol"), False),
    (6, "1a", "2c", "3ac", 59, qty(0.625, "mmol", "0.625 mmol"), False),
    (7, "1e", "2a", "3ea", 52, qty(0.50, "mmol", "0.50 mmol"), False),
    (8, "1f", "2a", "3fa", 62, qty(0.375, "mmol", "0.375 mmol"), False),
    (9, "1g", "2a", "3ga", 56, qty(0.375, "mmol", "0.375 mmol"), False),
]
for entry, acid_label, allenol_label, product_label, yield_percent, allenol_amount, exact_scheme1 in table1:
    records.append(scope_record(
        "table1", entry, acid_label, allenol_label, product_label, yield_percent,
        P1, allenol_amount, exact_scheme1=exact_scheme1,
    ))

# Two explicitly described control experiments.
control_ev = P1
records.append(record(
    "control_n2_3aa", "controlled experiment: N2 atmosphere", "reported_experiment", control_ev,
    [acid("1a", control_ev), allenol("2a", control_ev), participant("n2", "unspecified_agent", "N2", control_ev, name="nitrogen", smiles="N#N"), product("3aa", control_ev)],
    [{"step_id": "n2_control", "participant_ids": ["acid", "allenol", "n2", "product"], "conditions": [field("atmosphere", "N2", control_ev), field("temperature", None, control_ev), field("time", None, control_ev), field("workup", None, control_ev), field("purification", None, control_ev)]}],
    [field("yield", qty(52, "%", "52%"), control_ev, ["product"]), field("yield_measurement_basis", None, control_ev, ["product"])],
    [("The prose identifies the product as 3aa but does not restate the complete control recipe.", control_ev)],
    COMMON_UNRESOLVED + ["Catalyst, solvent, scale, temperature, and time are not restated for this control and were not copied from the standard scope conditions."],
))

records.append(record(
    "control_k2co3_3aa", "controlled experiment: 1.0 equiv K2CO3", "reported_experiment", control_ev,
    [acid("1a", control_ev), allenol("2a", control_ev), participant("k2co3", "reagent", "K2CO3", control_ev, name="potassium carbonate", smiles="[K+].[K+].[O-]C([O-])=O", amounts=[field("equivalents", qty(1.0, "equiv", "1.0 equiv"), control_ev)]), product("3aa", control_ev)],
    [{"step_id": "base_control", "participant_ids": ["acid", "allenol", "k2co3", "product"], "conditions": [field("temperature", None, control_ev), field("time", None, control_ev), field("atmosphere", None, control_ev), field("workup", None, control_ev), field("purification", None, control_ev)]}],
    [field("yield", "not detected", control_ev, ["product"]), field("yield_measurement_basis", None, control_ev, ["product"])],
    [("The paper states that the reaction did not yield 3aa in the presence of K2CO3.", control_ev)],
    COMMON_UNRESOLVED + ["Catalyst, solvent, scale, temperature, time, and detection limit are not restated for this control."],
))


def scheme2_record(with_tfa):
    evidence = [P1T, P1I, P2T, P2I]
    participants = [
        acid("1a", evidence, entity="r_1a"),
        allenol("2b", evidence, entity="r_2b"),
        pdcl2(evidence),
        dma([P1T, P2I], qty(2, "mL", "2 mL")),
        product("3ab", evidence),
    ]
    participants[0]["label"] = fact("(R)-(-)-1a", evidence)
    participants[0]["amounts"].append(field("enantiomeric_excess", qty(98, "%", "98% ee"), P2))
    if with_tfa:
        participants.append(participant("tfa", "reagent", "TFA", evidence, name="trifluoroacetic acid", smiles="O=C(O)C(F)(F)F", amounts=[field("equivalents", qty(0.8, "equiv", "0.8 equiv"), evidence)]))
    conditions = [
        field("temperature", qty(30, "°C", "30 °C"), P2),
        field("time", None, evidence),
        field("atmosphere", None, evidence),
        field("workup", None, evidence),
        field("purification", None, evidence),
    ]
    yield_value, ee_value = (62, 98) if with_tfa else (58, 36)
    notes = [] if with_tfa else [("No TFA was added.", P2)]
    return record(
        "scheme2_tfa_3ab" if with_tfa else "scheme2_no_tfa_3ab",
        "Scheme 2: 0.8 equiv TFA" if with_tfa else "Scheme 2: no TFA",
        "reported_experiment", evidence, participants,
        [{"step_id": "mechanistic_probe_reaction", "participant_ids": [p["entity_id"] for p in participants], "conditions": conditions}],
        [
            field("yield", qty(yield_value, "%", f"{yield_value}%"), P2, ["product"]),
            field("product_enantiomeric_excess", qty(ee_value, "%", f"{ee_value}% ee"), P2, ["product"]),
            field("yield_measurement_basis", None, evidence, ["product"]),
        ],
        notes,
        COMMON_UNRESOLVED + ["Reactant scale, reaction time, atmosphere, workup, and purification are not supplied in the main text."],
    )


records.extend([scheme2_record(False), scheme2_record(True)])

# Table 2; page 1 prose supplies the claim that these E products were exclusive.
table2_ev = [P1T, P1I, P2T, P2I]
table2 = [
    (1, "1b", "2d", "(E)-3bd", 52, qty(0.625, "mmol", "0.625 mmol")),
    (2, "1d", "2d", "(E)-3dd", 55, qty(0.375, "mmol", "0.375 mmol")),
    (3, "1d", "2e", "(E)-3de", 63, qty(0.375, "mmol", "0.375 mmol")),
    (4, "1d", "2f", "(E)-3df", 74, qty(0.375, "mmol", "0.375 mmol")),
    (5, "1h", "2e", "(E)-3he", 66, qty(0.375, "mmol", "0.375 mmol")),
    (6, "1h", "2f", "(E)-3hf", 82, qty(0.375, "mmol", "0.375 mmol")),
    (7, "1i", "2f", "(E)-3if", 71, qty(0.375, "mmol", "0.375 mmol")),
]
for entry, acid_label, allenol_label, product_label, yield_percent, allenol_amount in table2:
    records.append(scope_record(
        "table2", entry, acid_label, allenol_label, product_label, yield_percent,
        table2_ev, allenol_amount, stereochemistry="E (reported exclusively)",
    ))

# Proposed mechanisms are represented as mechanism records, never as reported experiments.
mech3_ev = [P1T, P1I, P2T, P2I]
mech3_parts = [
    acid("1a", mech3_ev, entity="r_1a"),
    allenol("2b", mech3_ev, entity="r_2b"),
    participant("pdx2", "catalyst", "PdX2", mech3_ev),
    participant("m1", "unspecified_agent", "M1", mech3_ev, name="4-furanonyl palladium intermediate M1"),
    participant("m2", "unspecified_agent", "M2", mech3_ev, name="pi-allylic palladium intermediate M2"),
    product("(R)-(-)-3ab", mech3_ev),
    participant("xpdoh", "unspecified_agent", "XPd+[OH-]", mech3_ev),
    participant("hx", "reagent", "HX", mech3_ev),
    participant("water", "unspecified_agent", "H2O", mech3_ev, smiles="O"),
]
records.append(record(
    "mechanism_scheme3", "Scheme 3", "mechanism", mech3_ev, mech3_parts,
    [
        {"step_id": "cyclic_oxypalladation", "participant_ids": ["r_1a", "pdx2", "m1"], "conditions": [field("operation", "proposed cyclic oxypalladation", mech3_ev)]},
        {"step_id": "carbopalladation", "participant_ids": ["m1", "r_2b", "m2"], "conditions": [field("operation", "proposed regioselective carbopalladation", mech3_ev)]},
        {"step_id": "beta_hydroxide_elimination", "participant_ids": ["m2", "product", "xpdoh"], "conditions": [field("operation", "proposed beta-hydroxide elimination", mech3_ev)]},
        {"step_id": "catalyst_regeneration", "participant_ids": ["xpdoh", "hx", "pdx2", "water"], "conditions": [field("operation", "proposed reaction with H+ to regenerate PdX2", mech3_ev)]},
    ], [],
    [("Scheme 3 is explicitly titled a possible mechanism and is not an experimental procedure or measured reaction entry.", P2)],
    ["Proposed intermediates M1/M2, PdX2/XPd species, and elementary steps are mechanistic assignments rather than isolated or directly measured species."],
))

mech4_parts = [
    participant("m3", "unspecified_agent", "M3", P2, name="pi-allylic palladium intermediate M3"),
    participant("m4", "unspecified_agent", "M4", P2, name="pi-allylic palladium intermediate M4"),
    participant("e_isomer", "product", "E-isomer", P2),
    participant("z_isomer", "product", "Z-isomer", P2),
]
records.append(record(
    "mechanism_scheme4", "Scheme 4", "mechanism", P2, mech4_parts,
    [
        {"step_id": "sigma_pi_sigma_equilibration", "participant_ids": ["m3", "m4"], "conditions": [field("operation", "proposed sigma-pi-sigma interconversion; M3 described as thermodynamically favored", P2)]},
        {"step_id": "m3_trans_elimination", "participant_ids": ["m3", "e_isomer"], "conditions": [field("operation", "proposed trans-beta-hydroxide elimination to E-isomer", P2)]},
        {"step_id": "m4_trans_elimination", "participant_ids": ["m4", "z_isomer"], "conditions": [field("operation", "proposed trans-beta-hydroxide elimination to Z-isomer", P2)]},
    ], [],
    [("The Z-isomer branch is marked 'not detected' in the mechanistic rationale; this was not converted into a measured yield.", P2)],
    ["Scheme 4 is a stereochemical rationale, not an independently reported experiment; no quantitative equilibrium or elementary-step data are supplied."],
))


def ids(prefixes):
    return [r["record_id"] for r in records if any(r["record_id"].startswith(f"{DOC}:{p}") for p in prefixes)]


table1_ids = ids(["table1_"])
table2_ids = ids(["table2_"])
control_ids = ids(["control_"])
scheme2_ids = ids(["scheme2_"])
mechanism_ids = ids(["mechanism_"])

coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1,
            "state": "attempted",
            "regions": [
                {"region": "left and lower-right prose: introduction and citations to prior allene dimerization work", "finding": "Prior literature/context only; no detailed current-paper experiment was created from these citations.", "evidence_ids": [P1I, P1T]},
                {"region": "upper-right Scheme 1", "finding": "One 1a+2a experiment at 5 mol% PdCl2/DMA/30 °C/22 h gives 3aa (67%) and 4aa (4%); deduplicated with Table 1 entry 1.", "evidence_ids": [P1I, P1T]},
                {"region": "right-center Table 1 and footnotes", "finding": "Nine substrate-scope rows extracted separately; footnote overrides for the amount of 2 were applied to entries 3, 6, and 7.", "evidence_ids": [P1I, P1T]},
                {"region": "lower prose: N2 and K2CO3 controls", "finding": "Two distinct controlled experiments extracted, including the failed 1.0 equiv K2CO3 result as 'not detected'.", "evidence_ids": [P1I, P1T]},
                {"region": "lower-left prose: Table 2 stereochemical statement", "finding": "Cross-page context states E products are exclusive when R4 is non-H and R5 is H; linked to the seven Table 2 rows on page 2.", "evidence_ids": [P1I, P1T]},
                {"region": "lower-right prose: chiral probe/TFA and initial mechanistic proposal", "finding": "Cross-page evidence for the two Scheme 2 conditions and proposed cyclic oxypalladation in Scheme 3.", "evidence_ids": [P1I, P1T]},
            ],
            "record_ids": table1_ids + control_ids + scheme2_ids + table2_ids + [f"{DOC}:mechanism_scheme3"],
            "unresolved": [
                "The supplied main paper refers to Supporting Information, but its association is unestablished and no SI was used.",
                "Table-wide 8-28 h durations do not reveal entry-specific times; yield measurement bases and procedures are absent.",
                "Product structures and candidate reactant SMILES remain machine transcriptions requiring chemical review.",
            ],
        },
        {
            "page": 2,
            "state": "attempted",
            "regions": [
                {"region": "upper-left Table 2 and footnotes", "finding": "Seven E-selective substrate-scope rows extracted separately; entry 1 uses the footnote override of 0.625 mmol 2.", "evidence_ids": [P2I, P2T]},
                {"region": "middle-left Scheme 2", "finding": "Two distinct chiral-probe experiments extracted: no TFA (58%, 36% ee) and 0.8 equiv TFA (62%, 98% ee).", "evidence_ids": [P2I, P2T]},
                {"region": "lower-left Scheme 3 and adjoining prose", "finding": "Possible catalytic mechanism classified as a mechanism record with proposed oxypalladation, carbopalladation, elimination, and catalyst-regeneration steps.", "evidence_ids": [P2I, P2T]},
                {"region": "lower-left Scheme 4 and adjoining prose", "finding": "Stereochemical rationale classified as a mechanism record; the Z-isomer is marked not detected but no quantitative yield was inferred.", "evidence_ids": [P2I, P2T]},
                {"region": "upper/right conclusion, acknowledgments, SI notice, and references", "finding": "Conclusion/context and cited literature only; no additional current-paper experiment was created.", "evidence_ids": [P2I, P2T]},
            ],
            "record_ids": table2_ids + scheme2_ids + mechanism_ids,
            "unresolved": [
                "Scheme 2 does not report reaction time, reactant scale, atmosphere, workup, purification, or yield basis.",
                "Mechanistic intermediates and elementary steps are proposals rather than directly verified experimental observations.",
                "The SI notice does not establish an SI file association in this workspace.",
            ],
        },
    ],
}


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


write_json(RUN / "raw_model" / "pages_0001_0002_records.json", records)
write_json(RUN / "coverage" / "pages_0001_0002.json", coverage)

# Mark only this session's two page tasks attempted; this is a coverage state, not accuracy certification.
tasks_path = RUN / "tasks.json"
tasks = json.loads(tasks_path.read_text())
for task in tasks:
    page = int(task["evidence_id"].split(":page", 1)[1].split(":", 1)[0])
    if page in (1, 2):
        task["state"] = "attempted"
        task["visual_evidence_id"] = f"{DOC}:page{page}:image"
        task["reason"] = "Original page image inspected; extraction remains machine-generated and needs review."
write_json(tasks_path, tasks)

print(json.dumps({"records": len(records), "page1_records": len(coverage["pages"][0]["record_ids"]), "page2_records": len(coverage["pages"][1]["record_ids"])}, ensure_ascii=False))
