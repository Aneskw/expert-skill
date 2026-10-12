#!/usr/bin/env python3
"""Build raw evidence-linked records and coverage for PDF pages 1-2."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "runs/current"
DOC = "doc_f6723fa2d1f5d0ad"
P1I = f"{DOC}:page1:image"
P1T = f"{DOC}:page1:text"
P2I = f"{DOC}:page2:image"
P2T = f"{DOC}:page2:text"
EV1 = [P1I, P1T]
EV2 = [P2I, P2T]


def fact(value, evidence=None):
    return {
        "value": value,
        "evidence_ids": [] if value is None else list(evidence or []),
        "verification": "missing" if value is None else "unreviewed",
    }


def field(name, value, evidence=None, target=None):
    result = {"name": name, "fact": fact(value, evidence)}
    if target:
        result["target_entity_ids"] = list(target)
    return result


def participant(entity_id, role, label, name, evidence, smiles=None, amounts=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence) if name else fact(None),
        "smiles": fact(smiles, evidence) if smiles else fact(None),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": list(amounts or []),
    }


def record(suffix, source_id, kind, evidence, participants, steps, outcomes,
           notes=None, unresolved=None):
    return {
        "record_id": f"{DOC}:{suffix}",
        "document_id": DOC,
        "source_reaction_id": source_id,
        "record_kind": kind,
        "status": "needs_review",
        "completeness": "partial",
        "evidence_ids": list(dict.fromkeys(evidence)),
        "participants": participants,
        "steps": steps,
        "outcomes": outcomes,
        "notes": list(notes or []),
        "review": {
            "method": "model",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": list(unresolved or []),
        },
    }


def standard_agents(evidence, solvent_label="toluene", solvent_name="toluene",
                    solvent_smiles="Cc1ccccc1"):
    return [
        participant(
            "catalyst_pd2dba3_chcl3", "catalyst", "Pd2(dba)3·CHCl3",
            "bis(dibenzylideneacetone)palladium(0) complex, chloroform adduct",
            evidence, amounts=[field("catalyst_loading", {"number": 5, "unit": "mol%"}, evidence)],
        ),
        participant(
            "ligand_pph3", "reagent", "PPh3", "triphenylphosphine", evidence,
            "P(c1ccccc1)(c1ccccc1)c1ccccc1",
            [field("ligand_loading", {"number": 20, "unit": "mol%"}, evidence)],
        ),
        participant(
            "tbab", "reagent", "TBAB", "tetrabutylammonium bromide", evidence,
            "[Br-].CCCC[N+](CCCC)(CCCC)CCCC",
            [field("amount", {"number": 0.1, "unit": "mmol"}, evidence)],
        ),
        participant(
            "solvent", "solvent", solvent_label, solvent_name, evidence,
            solvent_smiles,
            [field("solvent_volume", {"number": 3, "unit": "mL"}, evidence)],
        ),
    ]


records = []

# Scheme 1: current-paper baseline experiment with the free acid.
scheme1_participants = [
    participant(
        "acid_1a", "reactant", "Sa-(+)-1a", "Sa-(+)-2-methyl-4-phenyl-2,3-butadienoic acid",
        EV1, "CC(=C=Cc1ccccc1)C(=O)O",
        [field("starting_material_ee", {"number": 96, "unit": "%"}, EV1)],
    ),
    participant("phi", "reactant", "PhI", "iodobenzene", EV1, "Ic1ccccc1"),
    participant(
        "catalyst", "catalyst", "Pd2(dba)3·CHCl3",
        "bis(dibenzylideneacetone)palladium(0) complex, chloroform adduct", EV1,
        amounts=[field("catalyst_loading", {"number": 2.5, "unit": "mol%"}, EV1)],
    ),
    participant(
        "pph3", "reagent", "PPh3", "triphenylphosphine", EV1,
        "P(c1ccccc1)(c1ccccc1)c1ccccc1",
        [field("ligand_loading", {"number": 10, "unit": "mol%"}, EV1)],
    ),
    participant(
        "dipea", "reagent", "i-Pr2NEt", "N,N-diisopropylethylamine", EV1,
        "CCN(C(C)C)C(C)C",
        [field("equivalents", {"number": 1.1, "unit": "equiv"}, EV1)],
    ),
    participant("toluene", "solvent", "toluene", "toluene", EV1, "Cc1ccccc1"),
    participant(
        "product_3a", "product", "(+)-3a", "3a butenolide (configuration not printed in Scheme 1)",
        EV1, "O=C1OC(c2ccccc2)C(c2ccccc2)=C1C",
    ),
]
records.append(record(
    "scheme1_free_acid_1a_phi", "Scheme 1", "optimization_entry", EV1,
    scheme1_participants,
    [{"step_id": "coupling_cyclization", "participant_ids": [p["entity_id"] for p in scheme1_participants],
      "conditions": [field("reaction_temperature", {"number": 50, "unit": "°C"}, EV1),
                     field("reaction_time", None)]}],
    [field("yield", {"number": 58, "unit": "%"}, EV1, ["product_3a"]),
     field("product_ee", {"number": 60, "unit": "%"}, EV1, ["product_3a"]),
     field("yield_measurement_basis", None, target=["product_3a"])],
    notes=[fact("The prose describes 60% ee as the highest ee observed for the free-acid route and discusses a pi-allylpalladium pathway.", EV1)],
    unresolved=["Reaction time, scale, atmosphere, workup, purification, and yield measurement basis are not reported on the supplied page.",
                "Candidate SMILES omit axial and product stereochemistry and remain unverified."],
))

# Equation 1: DIPEA salt 2a-prime.
eq1_participants = [
    participant(
        "salt_2a_prime", "reactant", "Sa-(+)-2a′", "1:1 salt of Sa-(+)-1a and N,N-diisopropylethylamine",
        EV1, "CC(=C=Cc1ccccc1)C(=O)[O-].CC[NH+](C(C)C)C(C)C",
        [field("starting_material_ee", {"number": 97, "unit": "%"}, EV1)],
    ),
    participant("phi", "reactant", "PhI", "iodobenzene", EV1, "Ic1ccccc1"),
    participant("catalyst", "catalyst", "Pd2(dba)3·CHCl3", "palladium(0) catalyst chloroform adduct", EV1,
                amounts=[field("catalyst_loading", {"number": 5, "unit": "mol%"}, EV1)]),
    participant("pph3", "reagent", "PPh3", "triphenylphosphine", EV1,
                "P(c1ccccc1)(c1ccccc1)c1ccccc1",
                [field("ligand_loading", {"number": 20, "unit": "mol%"}, EV1)]),
    participant("toluene", "solvent", "toluene", "toluene", EV1, "Cc1ccccc1"),
    participant("product_3a", "product", "S-(+)-3a", "S-(+)-3a butenolide", EV1,
                "O=C1OC(c2ccccc2)C(c2ccccc2)=C1C"),
]
records.append(record(
    "eq1_dipea_salt_2a_prime", "Equation 1", "optimization_entry", EV1,
    eq1_participants,
    [{"step_id": "coupling_cyclization", "participant_ids": [p["entity_id"] for p in eq1_participants],
      "conditions": [field("reaction_temperature", {"number": 5, "unit": "°C"}, EV1),
                     field("reaction_time", {"number": 60, "unit": "h"}, EV1)]}],
    [field("yield", {"number": 62, "unit": "%"}, EV1, ["product_3a"]),
     field("product_ee", {"number": 91, "unit": "%"}, EV1, ["product_3a"]),
     field("yield_measurement_basis", None, target=["product_3a"])],
    unresolved=["Reaction scale, atmosphere, workup, purification, and yield measurement basis are not reported on the supplied page.",
                "Candidate SMILES do not encode the source's axial or product stereochemistry and remain unverified."],
))

# Direct use of cinchonidine salt 2a at room temperature.
direct_rt_participants = [
    participant("salt_2a", "reactant", "Sa-(+)-2a", "1:1 salt of allenoic acid 1a and L-(-)-cinchonidine", EV1),
    participant("phi", "reactant", "PhI", "iodobenzene", EV1, "Ic1ccccc1"),
    participant("tbab", "reagent", "TBAB", "tetrabutylammonium bromide", EV1, "[Br-].CCCC[N+](CCCC)(CCCC)CCCC"),
    participant("toluene", "solvent", "toluene", "toluene", EV1, "Cc1ccccc1"),
    participant("product_3a", "product", "S-(+)-3a", "S-(+)-3a butenolide", EV1,
                "O=C1OC(c2ccccc2)C(c2ccccc2)=C1C"),
]
records.append(record(
    "prose_direct_salt_2a_rt", "page 1 direct-salt room-temperature experiment", "optimization_entry", EV1,
    direct_rt_participants,
    [{"step_id": "coupling_cyclization", "participant_ids": [p["entity_id"] for p in direct_rt_participants],
      "conditions": [field("reaction_temperature", "r.t.", EV1), field("reaction_time", None)]}],
    [field("yield", {"number": 95, "unit": "%"}, EV1, ["product_3a"]),
     field("product_ee", {"number": 87, "unit": "%"}, EV1, ["product_3a"]),
     field("yield_measurement_basis", None, target=["product_3a"])],
    notes=[fact("TBAB is included because the immediately following control states that no reaction was observed in its absence.", EV1)],
    unresolved=["Reaction time, exact catalyst/ligand identity and loadings, amounts, scale, atmosphere, workup, purification, and yield measurement basis are not specified for this prose result.",
                "The full salt structure and stereochemical candidate SMILES are unresolved."],
))

# Explicit failure when TBAB is omitted.
failure_participants = [
    participant("salt_2a", "reactant", "Sa-(+)-2a", "1:1 salt of allenoic acid 1a and L-(-)-cinchonidine", EV1),
    participant("phi", "reactant", "PhI", "iodobenzene", EV1, "Ic1ccccc1"),
    participant("toluene", "solvent", "toluene", "toluene", EV1, "Cc1ccccc1"),
    participant("expected_product_3a", "product", "S-(+)-3a", "expected 3a butenolide", EV1,
                "O=C1OC(c2ccccc2)C(c2ccccc2)=C1C"),
]
records.append(record(
    "prose_no_tbab_failure", "page 1 control without TBAB", "optimization_entry", EV1,
    failure_participants,
    [{"step_id": "coupling_cyclization_control", "participant_ids": [p["entity_id"] for p in failure_participants],
      "conditions": [field("tbab_condition", "absence of TBAB", EV1),
                     field("reaction_temperature", None), field("reaction_time", None)]}],
    [field("reaction_result", "no reaction", EV1, ["expected_product_3a"]),
     field("yield", None, target=["expected_product_3a"])],
    notes=[fact("The authors attribute the failure probably to low solubility of Sa-(+)-2a in toluene.", EV1)],
    unresolved=["The exact temperature, time, catalyst system, amounts, and detection criterion for 'no reaction' are not reported in this sentence.",
                "The expected product is represented only to attach the failed-formation result; it was not reported as isolated."],
))

# Equation 2: bromophenyl stereochemical probe.
eq2_evidence = EV1 + EV2
eq2_participants = [
    participant(
        "salt_2f", "reactant", "Sa-(+)-2f", "L-(-)-cinchonidine salt of 2-(n-propyl)-4-(4-bromophenyl)-2,3-butadienoic acid",
        EV1, amounts=[field("starting_material_ee", {"number": 99, "unit": "%"}, EV1)],
    ),
    participant("phi", "reactant", "PhI", "iodobenzene", EV1, "Ic1ccccc1"),
    participant("catalyst", "catalyst", "Pd2(dba)3·CHCl3", "palladium(0) catalyst chloroform adduct", EV1,
                amounts=[field("catalyst_loading", {"number": 5, "unit": "mol%"}, EV1)]),
    participant("pph3", "reagent", "PPh3", "triphenylphosphine", EV1,
                "P(c1ccccc1)(c1ccccc1)c1ccccc1",
                [field("ligand_loading", {"number": 20, "unit": "mol%"}, EV1)]),
    participant("toluene", "solvent", "toluene", "toluene", EV1, "Cc1ccccc1"),
    participant("product_3g", "product", "S-(+)-3g", "S-(+)-3g bromophenyl butenolide", EV1,
                "O=C1OC(c2ccc(Br)cc2)C(c2ccccc2)=C1CCC"),
]
records.append(record(
    "eq2_salt_2f_phi", "Equation 2", "reported_experiment", eq2_evidence,
    eq2_participants,
    [{"step_id": "coupling_cyclization", "participant_ids": [p["entity_id"] for p in eq2_participants],
      "conditions": [field("reaction_temperature", {"number": 5, "unit": "°C"}, EV1),
                     field("reaction_time", {"number": 72, "unit": "h"}, EV1)]}],
    [field("yield", {"number": 76, "unit": "%"}, EV1, ["product_3g"]),
     field("product_ee", {"number": 94, "unit": "%"}, EV1, ["product_3g"]),
     field("configuration_assignment_method", "X-ray diffraction using bromine as reference", EV2, ["product_3g"]),
     field("yield_measurement_basis", None, target=["product_3g"])],
    notes=[fact("Page 2 states that the absolute configurations of the corresponding acid Sa-(+)-1f and product S-(+)-3g were determined by X-ray diffraction.", EV2)],
    unresolved=["Reaction scale, atmosphere, workup, purification, and yield measurement basis are not reported on the supplied pages.",
                "The cinchonidine salt SMILES is unresolved; the product connectivity SMILES omits stereochemistry and remains unverified."],
))

# Table 1 substrate-scope rows. Entry 1 also has page-1 prose evidence.
rows = [
    (1, "Ph", "Me", "A", "(+)-2a", 97, "Ph", 48, 90, "S-(+)-3a", 91),
    (2, "Ph", "Me", "A", "(+)-2a", 97, "p-MeC6H4", 48, 66, "S-(+)-3b", 92),
    (3, "Ph", "n-Pr", "A", "(+)-2b", 98, "Ph", 60, 72, "S-(+)-3c", 91),
    (4, "Ph", "n-Pr", "A", "(+)-2b", 98, "p-MeC6H4", 60, 75, "S-(+)-3d", 91),
    (5, "Ph", "Me", "B", "(+)-2c", 97, "Ph", 72, 60, "S-(+)-3a", 93),
    (6, "Ph", "Me", "B", "(+)-2c", 97, "p-MeC6H4", 72, 65, "S-(+)-3b", 95),
    (7, "Ph", "Me", "C", "(-)-2c", 98, "Ph", 60, 66, "R-(-)-3a", 96),
    (8, "Ph", "Me", "C", "(-)-2c", 98, "p-MeC6H4", 60, 72, "R-(-)-3b", 98),
    (9, "Ph", "Me", "C", "(-)-2c", 98, "p-E C6H4", 60, 58, "R-(-)-3e", 94),
    (10, "n-Hep", "H", "A", "(+)-2e", 97, "Ph", 48, 55, "(+)-3f", 94),
]
base_names = {
    "A": "L-(-)-cinchonidine",
    "B": "L-(-)-alpha-methylbenzylamine",
    "C": "D-(+)-alpha-methylbenzylamine",
}
aryl = {
    "Ph": ("PhI", "iodobenzene", "Ic1ccccc1"),
    "p-MeC6H4": ("p-MeC6H4I", "1-iodo-4-methylbenzene", "Cc1ccc(I)cc1"),
    "p-E C6H4": ("p-EC6H4I", "methyl 4-iodobenzoate (E = CO2Me)", "COC(=O)c1ccc(I)cc1"),
}
product_smiles = {
    "3a": "O=C1OC(c2ccccc2)C(c2ccccc2)=C1C",
    "3b": "O=C1OC(c2ccccc2)C(c2ccc(C)cc2)=C1C",
    "3c": "O=C1OC(c2ccccc2)C(c2ccccc2)=C1CCC",
    "3d": "O=C1OC(c2ccccc2)C(c2ccc(C)cc2)=C1CCC",
    "3e": "O=C1OC(c2ccccc2)C(c2ccc(C(=O)OC)cc2)=C1C",
    "3f": "O=C1OC(CCCCCCC)C(c2ccccc2)=C1",
}

for entry, r1, r2, base, salt_label, salt_ee, aryl_key, hours, yld, product_label, product_ee in rows:
    evidence = EV2 + (EV1 if entry == 1 else [])
    aryl_label, aryl_name, aryl_smiles = aryl[aryl_key]
    product_code = product_label.split("-")[-1].rstrip(")") if "-" in product_label else "3f"
    # Labels such as S-(+)-3a split cleanly only at the final token; use explicit lookup.
    product_code = next(code for code in product_smiles if product_label.endswith(code))
    solvent_label, solvent_name, solvent_smiles = (
        ("MeCN", "acetonitrile", "CC#N") if entry == 10 else ("toluene", "toluene", "Cc1ccccc1")
    )
    salt_name = f"1:1 acid-base salt {salt_label}; R1={r1}, R2={r2}; base {base}={base_names[base]}"
    salt = participant(
        "salt_2", "reactant", salt_label, salt_name, EV2,
        amounts=[field("amount", {"number": 0.1, "unit": "mmol"}, EV2),
                 field("starting_material_ee", {"number": salt_ee, "unit": "%"}, EV2)],
    )
    aryl_iodide = participant(
        "aryl_iodide", "reactant", aryl_label, aryl_name, EV2, aryl_smiles,
        [field("amount", {"number": 0.12, "unit": "mmol"}, EV2)],
    )
    product = participant(
        "product_3", "product", product_label,
        f"butenolide {product_code}; R1={r1}, R2={r2}, Ar2={aryl_key}", EV2,
        product_smiles[product_code],
    )
    participants = [salt, aryl_iodide] + standard_agents(EV2, solvent_label, solvent_name, solvent_smiles) + [product]
    yield_basis = "isolated yield" if entry == 1 else None
    outcomes = [
        field("yield", {"number": yld, "unit": "%"}, EV2, ["product_3"]),
        field("product_ee", {"number": product_ee, "unit": "%"}, EV2, ["product_3"]),
        field("yield_measurement_basis", yield_basis, EV1 if entry == 1 else None, ["product_3"]),
    ]
    unresolved = [
        "Atmosphere, concentration, workup, purification, and isolated mass are not reported in Table 1.",
        "Salt structures and stereochemical product SMILES are not fully resolved; connectivity candidates remain unverified.",
    ]
    if entry != 1:
        unresolved.append("The yield measurement basis is not stated for this table row.")
    if entry == 10:
        unresolved.append("The absolute configuration of (+)-3f is explicitly not determined.")
    records.append(record(
        f"table1_entry_{entry:02d}", f"Table 1 entry {entry}", "substrate_scope_entry", evidence,
        participants,
        [{"step_id": "coupling_cyclization", "participant_ids": [p["entity_id"] for p in participants],
          "conditions": [field("reaction_temperature", {"number": 5, "unit": "°C"}, EV2),
                         field("reaction_time", {"number": hours, "unit": "h"}, EV2)]}],
        outcomes,
        notes=[fact("The starting-salt ee refers to the allene moiety; the product ee was determined by HPLC on a Chiralcel OD column.", EV2)],
        unresolved=unresolved,
    ))

# Scheme 2: proposed catalytic mechanism, not a reported experiment.
mechanism_evidence = EV1 + EV2
mechanism_participants = [
    participant("generic_salt_2", "reactant", "2", "generic 1:1 acid-base salt of a 2,3-allenoic acid", EV1),
    participant("generic_aryl_halide", "reactant", "R4X", "generic organic halide", EV1),
    participant("pd0_l", "catalyst", "Pd(0)L", "generic palladium(0) catalyst", EV1),
    participant("generic_product_3", "product", "3", "generic 3-aryl polysubstituted butenolide", EV1),
]
records.append(record(
    "scheme2_proposed_mechanism", "Scheme 2", "mechanism", mechanism_evidence,
    mechanism_participants,
    [{"step_id": "proposed_catalytic_cycle", "participant_ids": [p["entity_id"] for p in mechanism_participants],
      "conditions": [field("operation", "oxidative addition–coordinative cyclization–reductive elimination", EV1)]}],
    [],
    notes=[fact("The authors present this as a possible mechanism and state on page 2 that the stereochemical outcome is consistent with it.", mechanism_evidence)],
    unresolved=["Scheme 2 is a mechanistic proposal with generic R groups and intermediates, not an independently reported experiment.",
                "Generic structures are intentionally left without SMILES."],
))


coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1,
            "state": "attempted",
            "regions": [
                {"region": "left column lower area, Scheme 1 and adjacent prose",
                 "finding": "Current-paper free-acid baseline coupling-cyclization; Scheme 1 reports 58% yield and 60% ee and is not a literature-only example.",
                 "evidence_ids": [P1I, P1T]},
                {"region": "upper-right reaction arrow, Equation 1",
                 "finding": "DIPEA salt Sa-(+)-2a′ plus PhI gives S-(+)-3a under explicit Pd/PPh3/toluene/5 °C/60 h conditions.",
                 "evidence_ids": [P1I, P1T]},
                {"region": "right-column prose below Equation 1",
                 "finding": "Separate room-temperature direct-salt result, explicit no-reaction control without TBAB, and the 5 °C result corresponding to Table 1 entry 1.",
                 "evidence_ids": [P1I, P1T]},
                {"region": "middle-right reaction arrow, Equation 2",
                 "finding": "Bromophenyl allenoate salt 2f stereochemical probe gives S-(+)-3g in 76% yield and 94% ee.",
                 "evidence_ids": [P1I, P1T]},
                {"region": "lower-right catalytic cycle, Scheme 2",
                 "finding": "Proposed oxidative-addition/coordinative-cyclization/reductive-elimination mechanism; classified as mechanism, not an experiment.",
                 "evidence_ids": [P1I, P1T]},
                {"region": "bottom-left ESI footnote",
                 "finding": "The paper advertises electronic supplementary experimental details, but no SI file is supplied or explicitly associated in this workspace.",
                 "evidence_ids": [P1I, P1T]},
            ],
            "record_ids": [
                f"{DOC}:scheme1_free_acid_1a_phi", f"{DOC}:eq1_dipea_salt_2a_prime",
                f"{DOC}:prose_direct_salt_2a_rt", f"{DOC}:prose_no_tbab_failure",
                f"{DOC}:eq2_salt_2f_phi", f"{DOC}:table1_entry_01",
                f"{DOC}:scheme2_proposed_mechanism",
            ],
            "unresolved": [
                "The supplied main text lacks the advertised ESI procedures; detailed workup, purification, atmosphere, and some reaction scales/bases remain unavailable.",
                "The sentence about unspecified higher temperatures gives no row-level temperatures, yields, or ee values and was not fabricated into experiments.",
            ],
        },
        {
            "page": 2,
            "state": "attempted",
            "regions": [
                {"region": "top half, Table 1 reaction header and entries 1-10",
                 "finding": "Ten independent substrate-scope rows with shared 5 °C Pd/PPh3/TBAB conditions, row-specific salt/base/ArI/time/yield/ee, and MeCN override for entry 10.",
                 "evidence_ids": [P2I, P2T]},
                {"region": "Table 1 footnotes a-g",
                 "finding": "Shared quantities, base definitions, starting-allene ee method, product-ee HPLC method, MeCN exception, E=CO2Me, and unknown absolute configuration of 3f were applied only where supported.",
                 "evidence_ids": [P2I, P2T]},
                {"region": "lower-left discussion and conclusion",
                 "finding": "X-ray assignment context for 1f/3g and mechanistic interpretation; no additional numbered experimental row beyond Equation 2 and Table 1.",
                 "evidence_ids": [P2I, P2T]},
                {"region": "lower reference columns",
                 "finding": "Bibliography and cited prior work only; no experiments were reconstructed from references.",
                 "evidence_ids": [P2I, P2T]},
            ],
            "record_ids": [f"{DOC}:table1_entry_{i:02d}" for i in range(1, 11)] + [
                f"{DOC}:eq2_salt_2f_phi", f"{DOC}:scheme2_proposed_mechanism"
            ],
            "unresolved": [
                "Yield measurement basis is not stated for Table 1 entries 2-10; entry 1 alone is described as isolated in page-1 prose.",
                "The full structures of chiral acid-base salts and stereochemically explicit product SMILES require expert review; all candidates remain unverified.",
                "The external cited papers and advertised SI were not supplied and were not treated as associated source documents.",
            ],
        },
    ],
}


raw_path = OUT / "raw_model/records_pages_0001_0002.json"
coverage_path = OUT / "coverage/pages_0001_0002.json"
raw_path.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
coverage_path.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"records": len(records), "raw": str(raw_path), "coverage": str(coverage_path)}, ensure_ascii=False))
