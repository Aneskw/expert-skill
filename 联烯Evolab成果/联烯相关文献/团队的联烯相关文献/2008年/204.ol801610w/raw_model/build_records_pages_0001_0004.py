#!/usr/bin/env python3
"""Build evidence-linked machine records for doc_f253050572b06387, PDF pages 1-4."""

import json
from pathlib import Path


DOC = "doc_f253050572b06387"
OUT = Path(__file__).with_name("records_pages_0001_0004.json")


def evid(page):
    return [f"{DOC}:page{page}:image", f"{DOC}:page{page}:text"]


def fact(value, evidence_ids=()):
    return {
        "value": value,
        "evidence_ids": list(evidence_ids) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def field(name, value, evidence_ids, targets=None):
    item = {"name": name, "fact": fact(value, evidence_ids)}
    if targets:
        item["target_entity_ids"] = targets
    return item


def participant(entity_id, role, label, name, smiles, evidence_ids, amounts=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence_ids),
        "name": fact(name, evidence_ids) if name is not None else fact(None),
        "smiles": fact(smiles, evidence_ids) if smiles is not None else fact(None),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": amounts or [],
    }


def record(suffix, source_id, kind, evidence_ids, participants, steps, outcomes,
           notes=None, unresolved=None):
    return {
        "record_id": f"{DOC}:{suffix}",
        "document_id": DOC,
        "source_reaction_id": source_id,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": list(dict.fromkeys(evidence_ids)),
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


def null_procedure_fields():
    return [
        field("atmosphere", None, []),
        field("workup", None, []),
        field("purification", None, []),
    ]


def amount(name, value, ev):
    return field(name, value, ev)


solvent_smiles = {
    "DMSO": "CS(C)=O",
    "DMF": "CN(C)C=O",
    "THF": "C1CCOC1",
    "dioxane": "O1CCOCC1",
    "Et2O": "CCOCC",
    "Cl3CMe": "CC(Cl)(Cl)Cl",
}


allene_smiles = {
    ("Ph", "Me"): "O=C(O)C(C)=C=Cc1ccccc1",
    ("Ph", "Et"): "O=C(O)C(CC)=C=Cc1ccccc1",
    ("Ph", "n-Pr"): "O=C(O)C(CCC)=C=Cc1ccccc1",
    ("p-FC6H4", "Me"): "O=C(O)C(C)=C=Cc1ccc(F)cc1",
    ("n-C4H9", "Me"): "O=C(O)C(C)=C=CCCCC",
    ("n-C6H13", "Me"): "O=C(O)C(C)=C=CCCCCCC",
    ("n-C7H15", "Me"): "O=C(O)C(C)=C=CCCCCCCC",
}


alkynone_smiles = {
    "Ph": "C#CC(=O)c1ccccc1",
    "p-ClC6H4": "C#CC(=O)c1ccc(Cl)cc1",
    "p-MeOC6H4": "C#CC(=O)c1ccc(OC)cc1",
    "n-C6H13": "C#CC(=O)CCCCCC",
}


r1_branch = {
    "Ph": "c2ccccc2",
    "p-FC6H4": "c2ccc(F)cc2",
    "n-C4H9": "CCCC",
    "n-C6H13": "CCCCCC",
    "n-C7H15": "CCCCCCC",
}
r2_branch = {"Me": "C", "Et": "CC", "n-Pr": "CCC"}
r3_carbonyl = {
    "Ph": "C(=O)c2ccccc2",
    "p-ClC6H4": "C(=O)c2ccc(Cl)cc2",
    "p-MeOC6H4": "C(=O)c2ccc(OC)cc2",
    "n-C6H13": "C(=O)CCCCCC",
}


def product_smiles(r1, r2, r3):
    return f"O=C1OC({r1_branch[r1]})C(/C=C/{r3_carbonyl[r3]})=C1{r2_branch[r2]}"


records = []

# Page 1 graphical abstract and the lower branch of page 2 Scheme 1 are a
# present-paper general scheme, not an additional executed experiment.
ev_general = evid(1) + evid(2)
general_parts = [
    participant("general_allenoic_acid_1", "reactant", "1", "generic 2,3-allenoic acid", None, ev_general),
    participant("general_terminal_alkynone_2", "reactant", "2", "generic terminal alpha,beta-unsaturated alkynone", None, ev_general),
    participant("general_pd_oac2", "catalyst", "Pd(OAc)2", "palladium(II) acetate", None, ev_general,
                [amount("catalyst_loading", {"number": 5, "unit": "mol%"}, ev_general)]),
    participant("general_bf3_etherate", "reagent", "BF3.Et2O", "boron trifluoride diethyl etherate", None, ev_general,
                [amount("equivalents", {"number": 1.0, "unit": "equiv"}, ev_general)]),
    participant("general_cl3cme", "solvent", "Cl3CMe", "1,1,1-trichloroethane", solvent_smiles["Cl3CMe"], ev_general),
    participant("general_dmso", "solvent", "DMSO", "dimethyl sulfoxide", solvent_smiles["DMSO"], ev_general),
    participant("general_e4", "product", "E-4", "generic 4-(3'-oxo-1'(E)-alkenyl)-2(5H)-furanone", None, ev_general),
]
records.append(record(
    "general_scheme_cyclization_isomerization", "graphical_abstract_and_scheme1_this_work",
    "general_scheme", ev_general, general_parts,
    [
        {"step_id": "cyclization", "participant_ids": [p["entity_id"] for p in general_parts[:5]],
         "conditions": [
             field("temperature", {"minimum": 30, "maximum": 35, "unit": "°C", "raw_text": "30-35 °C"}, ev_general),
             field("solvent", "Cl3CMe", ev_general),
             field("time", None, []),
         ] + null_procedure_fields()},
        {"step_id": "evaporation_and_isomerization", "participant_ids": ["general_dmso", "general_e4"],
         "conditions": [
             field("operation", "evaporation followed by addition of DMSO", evid(1)),
             field("temperature", {"number": 90, "unit": "°C"}, evid(1)),
             field("time", {"number": 7, "unit": "h"}, evid(1)),
         ] + null_procedure_fields()},
    ], [],
    notes=[fact("Graphical abstract and Scheme 1 summarize the present work with generic R groups.", ev_general)],
    unresolved=["Generic R-group structures cannot be assigned complete SMILES.",
                "The general scheme is not counted as an independently executed experiment.",
                "Reaction scale, atmosphere, workup, and purification are not stated here."]
))

# Page 2 Scheme 1 upper branch explicitly points to previous work (ref. 6b).
ev2 = evid(2)
lit_parts = [
    participant("lit_generic_allenoic_acid", "reactant", "generic allenoic acid", None, None, ev2),
    participant("lit_methyl_propiolate", "reactant", "CO2Me-substituted alkyne", "methyl propiolate", "COC(=O)C#C", ev2),
    participant("lit_pd_oac2", "catalyst", "Pd(OAc)2", "palladium(II) acetate", None, ev2),
    participant("lit_initial_adduct", "product", "previous-work initial adduct", None, None, ev2),
    participant("lit_rearranged_product", "product", "previous-work rearranged product", None, None, ev2),
]
records.append(record(
    "scheme1_previous_methyl_propiolate", "scheme1_previous_work", "literature_example", ev2,
    lit_parts,
    [{"step_id": "prior_work_pathway", "participant_ids": [p["entity_id"] for p in lit_parts],
      "conditions": [field("operation", "prior-work incorporation of methyl propiolate followed by rearrangement", ev2),
                     field("temperature", None, []), field("time", None, [])]}],
    [], notes=[fact("Scheme 1 labels this branch 'previous work'; it is not a present-paper experiment.", ev2)],
    unresolved=["Generic R/E substituents prevent complete structure assignment.",
                "The cited prior-work procedure and yields are not reproduced on this page."]
))


def common_table1_participants(entry, solvent, alkyne_equiv, bf3_equiv, include_volume):
    ev = ev2
    participants = [
        participant(f"t1e{entry}_1a", "reactant", "1a", "2-methyl-4-phenyl-2,3-butadienoic acid",
                    allene_smiles[("Ph", "Me")], ev,
                    [amount("reaction_scale", {"number": 0.25, "unit": "mmol"}, ev)]),
        participant(f"t1e{entry}_2a", "reactant", "2a", "1-phenyl-2-propyn-1-one",
                    alkynone_smiles["Ph"], ev,
                    [amount("equivalents", {"number": alkyne_equiv, "unit": "equiv"}, ev)]),
        participant(f"t1e{entry}_pd", "catalyst", "Pd(OAc)2", "palladium(II) acetate", None, ev,
                    [amount("catalyst_loading", {"number": 5, "unit": "mol%"}, ev)]),
        participant(f"t1e{entry}_bf3", "reagent", "BF3.Et2O", "boron trifluoride diethyl etherate", None, ev,
                    [amount("equivalents", {"number": bf3_equiv, "unit": "equiv"}, ev)]),
        participant(f"t1e{entry}_solvent", "solvent", solvent, solvent, solvent_smiles[solvent], ev,
                    [amount("volume", {"number": 0.5, "unit": "mL"}, ev)] if include_volume else []),
        participant(f"t1e{entry}_3a", "product", "3a", "cycloisomerization product 3a",
                    "O=C1OC(c2ccccc2)C=C1C", ev),
        participant(f"t1e{entry}_4a", "product", "4a", "E/Z mixture of 4-(3'-oxo-1'-alkenyl)-2(5H)-furanone 4a",
                    "O=C1OC(c2ccccc2)C(C=CC(=O)c2ccccc2)=C1C", ev),
    ]
    return participants


table1 = [
    (1, "DMSO", 1.1, 1.0, 33, 0, True),
    (2, "DMF", 1.1, 1.0, 6, 30, True),
    (3, "THF", 1.1, 1.0, 19, 59, True),
    (4, "dioxane", 1.1, 1.0, 17, 59, True),
    (5, "Et2O", 1.1, 1.0, 25, 55, True),
    (6, "Cl3CMe", 1.1, 1.0, 12, 71, True),
    (7, "Cl3CMe", 1.5, 1.0, 12, 71, True),
    (8, "Cl3CMe", 1.1, 1.5, 11, 70, True),
    (9, "Cl3CMe", 1.1, 1.0, 14, 67, False),
]
for entry, solv, ae, be, y3, y4, include_volume in table1:
    parts = common_table1_participants(entry, solv, ae, be, include_volume)
    cond = [
        field("solvent", solv, ev2),
        field("temperature", {"number": 35, "unit": "°C"}, ev2),
        field("time", "overnight", ev2),
    ]
    if entry == 9:
        cond.append(field("substrate_1a_concentration", {"number": 0.125, "unit": "M"}, ev2))
    cond += null_procedure_fields()
    notes = [fact("The E/Z ratio of 4a changed constantly.", ev2)]
    if entry == 9:
        notes.append(fact("Entry 9 reports 0.125 M 1a; the standard 0.5 mL solvent volume is not copied to this overridden row.", ev2))
    records.append(record(
        f"table1_entry{entry}", f"Table 1 entry {entry}", "optimization_entry", ev2, parts,
        [{"step_id": "cyclization", "participant_ids": [p["entity_id"] for p in parts[:5]], "conditions": cond}],
        [
            field("nmr_yield_3a", {"number": y3, "unit": "%"}, ev2, [f"t1e{entry}_3a"]),
            field("nmr_yield_4a", {"number": y4, "unit": "%"}, ev2, [f"t1e{entry}_4a"]),
            field("yield_measurement_basis", "1H NMR analysis with CH2Br2 or mesitylene as internal standard", ev2),
            field("reported_E_Z_behavior", "E/Z ratio changed constantly", ev2, [f"t1e{entry}_4a"]),
        ], notes=notes,
        unresolved=["The row-specific choice of CH2Br2 versus mesitylene is not stated.",
                    "Atmosphere, workup, and purification are not reported in the supplied main text.",
                    "Candidate product stereochemistry/structure remains unverified."]
    ))


table2 = [
    (1, "Ph", "Me", "Ph", 70, 52, "4a"),
    (2, "Ph", "Me", "p-ClC6H4", 54, 49, "4b"),
    (3, "Ph", "Me", "p-MeOC6H4", 64, 48, "4c"),
    (4, "Ph", "Et", "Ph", 57, 42, "4d"),
    (5, "Ph", "Et", "p-MeOC6H4", 61, 46, "4e"),
    (6, "Ph", "n-Pr", "Ph", 56, 48, "4f"),
    (7, "Ph", "n-Pr", "p-MeOC6H4", 66, 59, "4g"),
    (8, "p-FC6H4", "Me", "p-MeOC6H4", 62, 47, "4h"),
    (9, "n-C4H9", "Me", "p-MeOC6H4", 49, 42, "4i"),
    (10, "n-C6H13", "Me", "Ph", 51, 51, "4j"),
    (11, "n-C6H13", "Me", "p-MeOC6H4", 53, 49, "4k"),
    (12, "n-C7H15", "Me", "Ph", 51, 51, "4l"),
    (13, "n-C7H15", "Me", "p-MeOC6H4", 57, 45, "4m"),
    (14, "Ph", "Me", "n-C6H13", 42, 36, "4n"),
]
for entry, r1, r2, r3, nmr_yield, isolated_yield, label in table2:
    ev = evid(3)
    # Scheme 2 is the same entry-1 two-stage experiment; page 4 states that
    # entries 2, 8, and 14 were reproduced, so those records carry page-4 evidence.
    if entry == 1:
        ev = evid(2) + evid(3)
    if entry in (2, 8, 14):
        ev = ev + evid(4)
    prefix = f"t2e{entry}"
    parts = [
        participant(f"{prefix}_allenoic", "reactant", "1", f"2,3-allenoic acid (R1={r1}, R2={r2})",
                    allene_smiles[(r1, r2)], ev,
                    [amount("reaction_scale", {"minimum": 0.25, "maximum": 0.5, "unit": "mmol", "raw_text": "0.25-0.5 mmol"}, evid(3))]),
        participant(f"{prefix}_alkynone", "reactant", "2", f"terminal alkynone (R3={r3})", alkynone_smiles[r3], ev,
                    [amount("equivalents", {"number": 1.1, "unit": "equiv"}, evid(3))]),
        participant(f"{prefix}_pd", "catalyst", "Pd(OAc)2", "palladium(II) acetate", None, ev,
                    [amount("catalyst_loading", {"number": 5, "unit": "mol%"}, evid(3))]),
        participant(f"{prefix}_bf3", "reagent", "BF3.Et2O", "boron trifluoride diethyl etherate", None, ev,
                    [amount("equivalents", {"number": 1.0, "unit": "equiv"}, evid(3))]),
        participant(f"{prefix}_cl3cme", "solvent", "Cl3CMe", "1,1,1-trichloroethane", solvent_smiles["Cl3CMe"], ev,
                    [amount("volume", {"minimum": 0.5, "maximum": 1.0, "unit": "mL", "raw_text": "0.5-1 mL"}, evid(3))]),
        participant(f"{prefix}_dmso", "solvent", "DMSO", "dimethyl sulfoxide", solvent_smiles["DMSO"], ev,
                    [amount("volume", {"minimum": 2, "maximum": 4, "unit": "mL", "raw_text": "2-4 mL"}, evid(3))]),
        participant(f"{prefix}_product", "product", f"E-{label}", f"E-isomer product {label}",
                    product_smiles(r1, r2, r3), ev),
    ]
    notes = []
    if entry == 1:
        notes.append(fact("Scheme 2 and Table 2 entry 1 describe the same two-stage E-4a experiment and are merged here.", evid(2) + evid(3)))
        notes.append(fact("The E-4a structure was additionally supported by an ORTEP drawing in Figure 1.", evid(3)))
    if entry in (2, 8, 14):
        notes.append(fact(f"The authors state that Table 2 entry {entry} was reproduced by Jing Li.", evid(4)))
    records.append(record(
        f"table2_entry{entry}_{label}", f"Table 2 entry {entry}", "substrate_scope_entry", ev, parts,
        [
            {"step_id": "cyclization", "participant_ids": [p["entity_id"] for p in parts[:5]],
             "conditions": [
                 field("solvent", "Cl3CMe", evid(3)),
                 field("temperature", {"number": 35, "unit": "°C"}, evid(3)),
                 field("time", "overnight", evid(3)),
                 field("atmosphere", None, []), field("workup", None, []), field("purification", None, []),
             ]},
            {"step_id": "evaporation_and_isomerization", "participant_ids": [f"{prefix}_dmso", f"{prefix}_product"],
             "conditions": [
                 field("operation", "evaporation followed by addition of DMSO", evid(3)),
                 field("temperature", {"number": 90, "unit": "°C"}, evid(3)),
                 field("time", {"number": 7, "unit": "h"}, evid(3)),
                 field("atmosphere", None, []), field("workup", None, []), field("purification", None, []),
             ]},
        ],
        [
            field("nmr_yield", {"number": nmr_yield, "unit": "%"}, evid(3), [f"{prefix}_product"]),
            field("isolated_yield", {"number": isolated_yield, "unit": "%"}, evid(3), [f"{prefix}_product"]),
            field("nmr_yield_measurement_basis", "1H NMR analysis with CH2Br2 or mesitylene as internal standard", evid(3)),
            field("isolated_yield_measurement_basis", "isolated product; value printed in parentheses", evid(3)),
            field("reported_E_Z_ratio", ">=99/1", evid(3), [f"{prefix}_product"]),
        ], notes=notes,
        unresolved=["The row-specific reaction scale, solvent volume, DMSO volume, and NMR internal standard are not assigned within the reported ranges/options.",
                    "Atmosphere, workup, and purification are absent from the supplied main text.",
                    "Candidate structures and E stereochemistry remain unverified against an external structure review."]
    ))

# Page 3 Scheme 3: nonterminal alkynone gives only cycloisomerization product.
ev3 = evid(3)
scheme3_parts = [
    participant("s3_1c", "reactant", "1c", "2,3-allenoic acid 1c (R1=Ph, R2=n-Pr)", allene_smiles[("Ph", "n-Pr")], ev3),
    participant("s3_2e", "reactant", "2e", "nonterminal alkynone 2e (n-Bu-C#C-C(O)-Et)", "CCCCC#CC(=O)CC", ev3),
    participant("s3_pd", "catalyst", "Pd(OAc)2", "palladium(II) acetate", None, ev3,
                [amount("catalyst_loading", {"number": 5, "unit": "mol%"}, ev3)]),
    participant("s3_bf3", "reagent", "BF3.Et2O", "boron trifluoride diethyl etherate", None, ev3,
                [amount("equivalents", {"number": 1.0, "unit": "equiv"}, ev3)]),
    participant("s3_cl3cme", "solvent", "Cl3CMe", "1,1,1-trichloroethane", solvent_smiles["Cl3CMe"], ev3),
    participant("s3_3c", "product", "3c", "cycloisomerization product 3c", "O=C1OC(c2ccccc2)C=C1CCC", ev3),
]
records.append(record(
    "scheme3_nonterminal_alkynone_cycloisomerization", "Scheme 3", "reported_experiment", ev3,
    scheme3_parts,
    [{"step_id": "cycloisomerization", "participant_ids": [p["entity_id"] for p in scheme3_parts[:5]],
      "conditions": [
          field("solvent", "Cl3CMe", ev3),
          field("temperature", {"minimum": 30, "maximum": 35, "unit": "°C", "raw_text": "30-35 °C"}, ev3),
          field("time", "overnight", ev3),
      ] + null_procedure_fields()}],
    [
        field("nmr_yield_3c", {"number": 87, "unit": "%"}, ev3, ["s3_3c"]),
        field("yield_measurement_basis", "NMR", ev3),
        field("desired_coupling_product_result", "not formed; only cycloisomerization product 3c was afforded", ev3),
    ],
    notes=[fact("The drawing labels the alkynone 2e, whereas the adjacent prose calls the nonterminal alkynone 2d.", ev3)],
    unresolved=["Source disagreement between alkynone labels 2e (Scheme 3) and 2d (prose) is unresolved.",
                "Amounts of 1c and 2e, solvent volume, atmosphere, workup, and purification are not stated.",
                "Candidate structures remain unverified."]
))

# Page 3 Scheme 4 is a proposed mechanism, not a reported reaction record.
mechanism_parts = [
    participant("mech_1", "reactant", "1", "generic 2,3-allenoic acid", None, ev3),
    participant("mech_2", "reactant", "2", "generic terminal alkynone", None, ev3),
    participant("mech_pd", "catalyst", "Pd(OAc)2", "palladium(II) acetate", None, ev3),
    participant("mech_m1", "unspecified_agent", "M1", "proposed furanonyl palladium intermediate", None, ev3),
    participant("mech_m2", "unspecified_agent", "M2", "proposed insertion intermediate", None, ev3),
    participant("mech_m3", "unspecified_agent", "M3", "proposed enolate intermediate", None, ev3),
    participant("mech_m4", "unspecified_agent", "M4", "proposed protonated allene intermediate", None, ev3),
    participant("mech_e4", "product", "E-4", "generic E product", None, ev3),
    participant("mech_z4", "product", "Z-4", "generic Z product", None, ev3),
]
records.append(record(
    "scheme4_proposed_mechanism", "Scheme 4", "mechanism", ev3, mechanism_parts,
    [{"step_id": "proposed_pathway", "participant_ids": [p["entity_id"] for p in mechanism_parts],
      "conditions": [field("operation", "proposed anti-oxypalladation, alkyne insertion, enolate interconversion, and protonolysis", ev3)]}],
    [], notes=[fact("Scheme 4 is explicitly presented as a rationale and is not an executed experiment.", ev3)],
    unresolved=["Generic R groups and palladium intermediates are not assigned complete SMILES.",
                "The mechanism is proposed and is not experimentally quantified on this page."]
))


OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
print(f"wrote {len(records)} records to {OUT}")
