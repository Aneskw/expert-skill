"""Build the evidence-linked raw model extraction for PDF pages 1--3.

This is intentionally separate from dataset.json.  The supported merge command
normalizes and quarantines these records as needs_review.
"""
import json
from pathlib import Path

DOC = "doc_71cc616fcd8cae7a"
P1T, P1I = f"{DOC}:page1:text", f"{DOC}:page1:image"
P2T, P2I = f"{DOC}:page2:text", f"{DOC}:page2:image"
P3T, P3I = f"{DOC}:page3:text", f"{DOC}:page3:image"


def fact(value, evidence):
    return {
        "value": value,
        "evidence_ids": list(evidence) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def field(name, value, evidence, targets=None):
    result = {"name": name, "fact": fact(value, evidence)}
    if targets:
        result["target_entity_ids"] = targets
    return result


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


def record(source_id, kind, evidence, participants, steps, outcomes, notes, unresolved):
    return {
        "record_id": f"{DOC}:{source_id}",
        "document_id": DOC,
        "source_reaction_id": source_id,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": list(evidence),
        "participants": participants,
        "steps": steps,
        "outcomes": outcomes,
        "notes": [fact(value, ev) for value, ev in notes],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved,
        },
    }


def q(number, unit, raw_text=None):
    result = {"number": number, "unit": unit}
    if raw_text:
        result["raw_text"] = raw_text
    return result


def base_1a(ev, amounts=None):
    return participant(
        "reactant_1a", "reactant", "1a", ev,
        "4-phenyl-2-propyl-2,3-butadienoic acid",
        "O=C(O)C(CCC)=C=Cc1ccccc1", amounts,
    )


def base_2a(ev, amounts=None):
    return participant(
        "reactant_2a", "reactant", "2a", ev,
        "homoallylic bromide (4-bromo-1-butene)", "C=CCCBr", amounts,
    )


def product(label, ev, entity=None):
    return participant(entity or f"product_{label}", "product", label, ev, None, None)


CATALYSTS = {
    1: ("PdCl2", "palladium(II) chloride", "[Cl-].[Cl-].[Pd+2]"),
    2: ("PdCl2", "palladium(II) chloride", "[Cl-].[Cl-].[Pd+2]"),
    3: ("PdCl2", "palladium(II) chloride", "[Cl-].[Cl-].[Pd+2]"),
    4: ("PdCl2", "palladium(II) chloride", "[Cl-].[Cl-].[Pd+2]"),
    5: ("PdCl2", "palladium(II) chloride", "[Cl-].[Cl-].[Pd+2]"),
    6: ("PdCl2", "palladium(II) chloride", "[Cl-].[Cl-].[Pd+2]"),
    7: ("depicted palladacycle catalyst", None, None),
    8: ("[PdCl2(dppf)]", "[PdCl2(dppf)]", None),
    9: ("[PdCl2(PPh3)2]", "bis(triphenylphosphine)palladium(II) dichloride", None),
    10: ("[PdCl2(PhCN)2]", "bis(benzonitrile)palladium(II) dichloride", None),
    11: ("Pd(OAc)2", "palladium(II) acetate", "CC(=O)[O-].CC(=O)[O-].[Pd+2]"),
    12: ("Pd(OAc)2", "palladium(II) acetate", "CC(=O)[O-].CC(=O)[O-].[Pd+2]"),
    13: ("Pd(OAc)2", "palladium(II) acetate", "CC(=O)[O-].CC(=O)[O-].[Pd+2]"),
}

SOLVENTS = {
    "DMF": ("N,N-dimethylformamide", "CN(C)C=O"),
    "ethanol": ("ethanol", "CCO"),
    "HMPA": ("hexamethylphosphoramide", "CN(C)P(=O)(N(C)C)N(C)C"),
    "dioxane": ("dioxane", "O1CCOCC1"),
}

TABLE1 = [
    (1, "DMF", 50, 22, 41),
    (2, "DMF", 50, 46, 44),
    (3, "ethanol", 50, 38, 44),
    (4, "HMPA", 50, 45, 40),
    (5, "dioxane", 50, 33.5, 17),
    (6, "DMF", 80, 10.5, 46),
    (7, "HMPA", 50, 34.5, 40),
    (8, "DMF", 50, 67, 30),
    (9, "DMF", 50, 110, 30),
    (10, "DMF", {"minimum": 80, "maximum": 90, "unit": "°C", "raw_text": "80–90 °C"}, 1, 51),
    (11, "DMF", 50, 33, 43),
    (12, "DMF", 80, 2, 51),
    (13, "DMF", 100, 1, 58),
]

records = []
for entry, solvent_label, temperature, hours, yield_pct in TABLE1:
    ev = [P2I, P2T]
    if entry in (1, 13):
        ev += [P1I, P1T]
    if entry == 13:
        ev += [P3I, P3T]
    catalyst_label, catalyst_name, catalyst_smiles = CATALYSTS[entry]
    loading = 10 if entry == 2 else 5
    if entry == 13:
        a1_amounts = [field("mass", q(50, "mg"), [P3I, P3T]), field("amount", q(0.25, "mmol"), [P3I, P3T])]
        a2_amounts = [
            field("mass", q(170, "mg"), [P3I, P3T]),
            field("amount", q(1.26, "mmol"), [P3I, P3T]),
            field("equivalents", q(5, "equiv"), [P1I, P1T]),
        ]
        cat_amounts = [
            field("mass", q(3, "mg"), [P3I, P3T]),
            field("amount", q(0.013, "mmol"), [P3I, P3T]),
            field("catalyst_loading", q(5, "mol%"), [P2I, P2T]),
        ]
        solv_amounts = [field("volume", q(2, "mL"), [P3I, P3T])]
    else:
        a1_amounts, a2_amounts, solv_amounts = [], [], []
        cat_amounts = [field("catalyst_loading", q(loading, "mol%"), [P2I, P2T])]
    solv_name, solv_smiles = SOLVENTS[solvent_label]
    participants = [
        base_1a(ev, a1_amounts),
        base_2a(ev, a2_amounts),
        participant("catalyst", "catalyst", catalyst_label, ev, catalyst_name, catalyst_smiles, cat_amounts),
        participant("reaction_solvent", "solvent", solvent_label, ev, solv_name, solv_smiles, solv_amounts),
        product("3a", ev),
    ]
    temp_value = temperature if isinstance(temperature, dict) else q(temperature, "°C")
    steps = [{
        "step_id": "reaction",
        "participant_ids": ["reactant_1a", "reactant_2a", "catalyst", "reaction_solvent"],
        "conditions": [
            field("solvent", solvent_label, ev),
            field("temperature", temp_value, ev),
            field("time", q(hours, "h"), ev),
        ],
    }]
    outcomes = [
        field("yield", q(yield_pct, "%"), ev, ["product_3a"]),
        field("yield_measurement_basis", None, [], ["product_3a"]),
    ]
    unresolved = [
        "Table 1 does not state the yield measurement basis for this entry.",
        "No explicitly associated supporting information was provided.",
    ]
    notes = [(f"Table 1 optimization entry {entry}.", [P2I, P2T])]
    if entry == 7:
        unresolved.append("The entry 7 catalyst is structure-only in the table and has not been converted to a verified identity or SMILES.")
    if entry == 13:
        participants.extend([
            participant("diethyl_ether", "solvent", "diethyl ether", [P3I, P3T], "diethyl ether", "CCOCC"),
            participant("water", "solvent", "water", [P3I, P3T], "water", "O"),
            participant("magnesium_sulfate", "reagent", "MgSO4", [P3I, P3T], "magnesium sulfate", "[Mg+2].[O-]S(=O)(=O)[O-]"),
            participant("silica_gel", "reagent", "silica gel", [P3I, P3T], "silica gel", None),
            participant("petroleum_ether", "solvent", "petroleum ether", [P3I, P3T], "petroleum ether", None),
            participant("ethyl_acetate", "solvent", "ethyl acetate", [P3I, P3T], "ethyl acetate", "CCOC(C)=O"),
        ])
        steps.extend([
            {
                "step_id": "workup",
                "participant_ids": ["diethyl_ether", "water", "magnesium_sulfate"],
                "conditions": [field("workup", "Diluted with diethyl ether; washed twice with water; organic layer dried over MgSO4 and concentrated by evaporation.", [P3I, P3T])],
            },
            {
                "step_id": "purification",
                "participant_ids": ["silica_gel", "petroleum_ether", "ethyl_acetate", "product_3a"],
                "conditions": [field("purification", "Column chromatography on silica gel (petroleum ether/ethyl acetate = 10:1).", [P3I, P3T])],
            },
        ])
        outcomes = [
            field("isolated_yield", q(58, "%"), [P3I, P3T], ["product_3a"]),
            field("product_mass", q(37, "mg"), [P3I, P3T], ["product_3a"]),
            field("yield_measurement_basis", "isolated after column chromatography", [P3I, P3T], ["product_3a"]),
            field("physical_form", "oil", [P3I, P3T], ["product_3a"]),
        ]
        unresolved = [
            "No explicitly associated supporting information was provided.",
            "Reaction atmosphere is not reported in the supplied main-text procedure.",
            "The depicted product 3a structure has not been independently structure-verified; SMILES remains null.",
        ]
        notes.extend([
            ("The same 100 °C, 1 h, 58% experiment is Table 1 entry 13, Table 2 entry 1, the page-1 best-result prose, and the page-3 typical procedure; these appearances are merged rather than duplicated.", [P1I, P1T, P2I, P2T, P3I, P3T]),
            ("Product 3a characterization is reported on page 3 (1H NMR, 13C NMR, EIMS, IR, and HRMS); spectral peaks are retained in the source evidence rather than expanded as reaction conditions.", [P3I, P3T]),
        ])
    records.append(record(
        f"table1_entry_{entry:02d}", "optimization_entry", ev,
        participants, steps, outcomes, notes, unresolved,
    ))


def scope_record(entry, substrate_label, substrate_name, substrate_smiles,
                 halide_label, halide_name, n_value, hours, product_label,
                 yield_pct, halide_amount):
    ev = [P2I, P2T]
    participants = [
        participant(
            "allenoic_acid", "reactant", substrate_label, ev,
            substrate_name, substrate_smiles,
            [field("amount", q(0.25, "mmol"), ev)],
        ),
        participant(
            "omega_bromoalkene", "reactant", halide_label, ev,
            halide_name, None,
            [field(halide_amount[0], halide_amount[1], ev)],
        ),
        participant(
            "catalyst", "catalyst", "Pd(OAc)2", ev, "palladium(II) acetate",
            "CC(=O)[O-].CC(=O)[O-].[Pd+2]",
            [field("catalyst_loading", q(5, "mol%"), ev)],
        ),
        participant("reaction_solvent", "solvent", "DMF", ev, "N,N-dimethylformamide", "CN(C)C=O"),
        product(product_label, ev),
    ]
    return record(
        f"table2_entry_{entry:02d}", "substrate_scope_entry", ev,
        participants,
        [{
            "step_id": "reaction",
            "participant_ids": ["allenoic_acid", "omega_bromoalkene", "catalyst", "reaction_solvent"],
            "conditions": [
                field("solvent", "DMF", ev),
                field("temperature", {"minimum": 90, "maximum": 100, "unit": "°C", "raw_text": "90–100 °C"}, ev),
                field("time", q(hours, "h"), ev),
            ],
        }],
        [
            field("yield", q(yield_pct, "%"), ev, [f"product_{product_label}"]),
            field("yield_measurement_basis", None, [], [f"product_{product_label}"]),
        ],
        [
            (f"Table 2 substrate-scope entry {entry}; omega-bromoalkene chain parameter n = {n_value}.", ev),
            ("The omega-bromoalkenes 2a–d are stated to have been prepared by literature methods; their preparations are not experiments reported in this paper.", ev),
        ],
        [
            "Table 2 gives a shared 90–100 °C range but not the exact temperature used for this individual row.",
            "Table 2 does not state the yield measurement basis for this entry.",
            "No explicitly associated supporting information was provided.",
            f"The depicted product {product_label} structure has not been independently structure-verified; SMILES remains null.",
        ],
    )


records.extend([
    scope_record(2, "1c", "2-benzyl-4-phenyl-2,3-butadienoic acid", "O=C(O)C(Cc1ccccc1)=C=Cc1ccccc1", "2a", "4-bromo-1-butene", 2, 1.5, "3b", 48, ("amount", q(1.25, "mmol"))),
    scope_record(3, "1a", "4-phenyl-2-propyl-2,3-butadienoic acid", "O=C(O)C(CCC)=C=Cc1ccccc1", "2b", "omega-bromoalkene 2b (n = 3)", 3, 10, "3c", 45, ("amount", q(1.25, "mmol"))),
    scope_record(4, "1a", "4-phenyl-2-propyl-2,3-butadienoic acid", "O=C(O)C(CCC)=C=Cc1ccccc1", "2d", "omega-bromoalkene 2d (n = 9)", 9, 21, "3d", 30, ("equivalents", q(10, "equiv"))),
    scope_record(5, "1a", "4-phenyl-2-propyl-2,3-butadienoic acid", "O=C(O)C(CCC)=C=Cc1ccccc1", "2e", "omega-bromoalkene 2e (n = 14)", 14, 9, "3e", 18, ("amount", q(1.25, "mmol"))),
])

# Two discrete mechanistic-probe experiments shown as equations on page 2.
ev = [P2I, P2T]
records.append(record(
    "equation_1_deuterium_probe", "reported_experiment", ev,
    [
        base_1a(ev),
        participant("reactant_2c", "reactant", "2c", ev, "deuterated homoallylic bromide 2c", None),
        participant("catalyst", "catalyst", "Pd(OAc)2", ev, "palladium(II) acetate", "CC(=O)[O-].CC(=O)[O-].[Pd+2]", [field("catalyst_loading", q(5, "mol%"), ev)]),
        participant("reaction_solvent", "solvent", "DMF", ev, "N,N-dimethylformamide", "CN(C)C=O"),
        product("3i", ev),
    ],
    [{
        "step_id": "reaction",
        "participant_ids": ["reactant_1a", "reactant_2c", "catalyst", "reaction_solvent"],
        "conditions": [
            field("solvent", "DMF", ev),
            field("temperature", {"minimum": 80, "maximum": 90, "unit": "°C", "raw_text": "80–90 °C"}, ev),
            field("time", q(1.5, "h"), ev),
        ],
    }],
    [
        field("yield", q(52, "%"), ev, ["product_3i"]),
        field("yield_measurement_basis", None, [], ["product_3i"]),
    ],
    [("The text states that only 3i was obtained and that both deuterium atoms were located at the terminal carbon of the acyclic C=C bond.", ev)],
    [
        "Yield measurement basis and reactant quantities are not reported in the supplied main text.",
        "The isotopically labelled structures of 2c and 3i have not been converted to independently verified SMILES.",
        "No explicitly associated supporting information was provided.",
    ],
))

records.append(record(
    "equation_2_pd0_probe", "reported_experiment", ev,
    [
        base_1a(ev),
        base_2a(ev),
        participant("catalyst", "catalyst", "[Pd(PPh3)4]", ev, "tetrakis(triphenylphosphine)palladium(0)", None, [field("catalyst_loading", q(5, "mol%"), ev)]),
        participant("potassium_carbonate", "reagent", "K2CO3", ev, "potassium carbonate", "[K+].[K+].[O-]C([O-])=O", [field("equivalents", q(1, "equiv"), ev)]),
        participant("tetrabutylammonium_bromide", "reagent", "Bu4NBr", ev, "tetrabutylammonium bromide", "CCCC[N+](CCCC)(CCCC)CCCC.[Br-]", [field("equivalents", q(1, "equiv"), ev)]),
        participant("reaction_solvent", "solvent", "DMF", ev, "N,N-dimethylformamide", "CN(C)C=O"),
        product("9", ev),
    ],
    [{
        "step_id": "reaction",
        "participant_ids": ["reactant_1a", "reactant_2a", "catalyst", "potassium_carbonate", "tetrabutylammonium_bromide", "reaction_solvent"],
        "conditions": [
            field("solvent", "DMF", ev),
            field("temperature", q(100, "°C"), ev),
            field("time", q(3, "h"), ev),
        ],
    }],
    [
        field("yield", q(96, "%"), ev, ["product_9"]),
        field("yield_measurement_basis", None, [], ["product_9"]),
    ],
    [("The text states that only product 9 was obtained under the Pd(0) conditions.", ev)],
    [
        "Yield measurement basis and substrate quantities are not reported in the supplied main text.",
        "The depicted product 9 structure has not been independently structure-verified; SMILES remains null.",
        "No explicitly associated supporting information was provided.",
    ],
))

# Non-experimental diagrams are retained and explicitly typed so they are not
# mistaken for reported experiments.
records.extend([
    record(
        "scheme_1_heck_pathways", "mechanism", [P1I, P1T], [], [], [],
        [("Scheme 1 presents generic possible Pd(0)/Pd(II)- and Pd(II)-catalyzed Heck-type mechanistic pathways with R groups; it is not a reported experiment in this paper.", [P1I, P1T])],
        ["Generic R groups and intermediates do not define complete molecular structures or experimental conditions."],
    ),
    record(
        "scheme_2_prior_work_generic", "literature_example", [P1I, P1T], [], [], [],
        [("Scheme 2 is a generic depiction of the authors' previously reported Pd(II)-catalyzed coupling of functionalized allenes with coordinating organic halides (references 6 and 7), not a new individual experiment here.", [P1I, P1T])],
        ["CG, FG, and R groups are generic; no individual substrates, quantities, conditions, or outcomes are specified."],
    ),
    record(
        "scheme_3_proposed_pathways", "mechanism", [P2I, P2T], [], [], [],
        [("Scheme 3 compares proposed path A (coordination-directed substitution) with path B (cyclic oxypalladation/carbopalladation followed by repeated dehydropalladation/hydropalladation and dehalopalladation).", [P2I, P2T])],
        ["Intermediates 4–8 and substituent variables are mechanistic/generic and are not standalone reported experiments."],
    ),
])

out = Path(__file__).with_name("records.json")
out.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"output": str(out), "records": len(records)}, ensure_ascii=False))
