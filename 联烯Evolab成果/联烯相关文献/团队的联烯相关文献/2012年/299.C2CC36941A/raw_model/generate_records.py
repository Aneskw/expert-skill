import json
from pathlib import Path

DOC = "doc_17e13020010a003a"
P1 = [f"{DOC}:page1:image", f"{DOC}:page1:text"]
P2 = [f"{DOC}:page2:image", f"{DOC}:page2:text"]
P3 = [f"{DOC}:page3:image", f"{DOC}:page3:text"]


def fact(value, evidence):
    return {
        "value": value,
        "evidence_ids": list(evidence) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def field(name, value, evidence, targets=None):
    item = {"name": name, "fact": fact(value, evidence)}
    if targets:
        item["target_entity_ids"] = targets
    return item


def mol(entity_id, role, label, name, evidence, smiles=None, amounts=None):
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


def rec(rid, kind, evidence, participants, steps, outcomes, notes, unresolved):
    if kind in {"reported_experiment", "optimization_entry", "substrate_scope_entry"}:
        for step in steps:
            present = {item["name"] for item in step["conditions"]}
            for missing_name in ("atmosphere", "workup", "purification"):
                if missing_name not in present:
                    step["conditions"].append(field(missing_name, None, []))
    return {
        "record_id": f"{DOC}:{rid}",
        "document_id": DOC,
        "source_reaction_id": rid,
        "record_kind": kind,
        "status": "needs_review",
        "completeness": "partial",
        "evidence_ids": evidence,
        "participants": participants,
        "steps": steps,
        "outcomes": outcomes,
        "notes": [fact(x, evidence) for x in notes],
        "review": {
            "method": "model",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved,
        },
    }


def qty(number, unit):
    return {"number": number, "unit": unit}


SMILES = {
    "1a": "C=C=CCNS(=O)(=O)c1ccc(C)cc1",
    "1b": "C=C(c1ccccc1)CNS(=O)(=O)c1ccc(C)cc1",
    "2a": "O=Cc1cccc2ccccc12",
    "2b": "O=Cc1ccccc1",
    "2c_o": "O=Cc1ccccc1Cl",
    "2c_p": "O=Cc1ccc(Cl)cc1",
    "2d": "O=Cc1ccc([N+](=O)[O-])cc1",
    "2e": "O=Cc1ccccc1Br",
    "2f": "CCCCCCCC=O",
    "2g": "O=CCCCc1ccccc1",
    "2h": "O=CC1CCCCC1",
    "2i": "CC(C)(C)C=O",
    "2k": "O=Cc1ccc(Br)cc1",
    "2l": "O=Cc1ccc(F)cc1",
    "2m": "Cc1ccc(C=O)cc1",
    "2n": "COc1ccc(C=O)cc1",
    "2o": "COc1cccc(C=O)c1",
    "2p": "O=Cc1ccccc1F",
    "2q": "CCCC=O",
    "FeCl3": "Cl[Fe](Cl)Cl",
    "TMSCl": "C[Si](C)(C)Cl",
    "CH2Cl2": "ClCCl",
    "CH3CN": "CC#N",
    "mesitylene": "Cc1cc(C)cc(C)c1",
    "phenylboronic_acid": "OB(O)c1ccccc1",
    "furylboronic_acid": "OB(O)c1ccco1",
    "water": "O",
    "dioxane": "O1CCOCC1",
}


def base_1a(evidence):
    return mol(
        "reactant_1a", "reactant", "1a",
        "N-(buta-2,3-dienyl)-4-tolylsulfonamide", evidence, SMILES["1a"],
        [field("concentration", qty(0.1, "M"), evidence)],
    )


def aldehyde(entity_id, label, name, smiles, evidence, equivalents=None, concentration=None):
    amounts = []
    if equivalents is not None:
        amounts.append(field("equivalents", qty(equivalents, "equiv"), evidence))
    if concentration is not None:
        amounts.append(field("concentration", qty(concentration, "M"), evidence))
    return mol(entity_id, "reactant", label, name, evidence, smiles, amounts)


def reagent(entity_id, label, name, smiles, evidence, amount_name=None, amount=None, role="reagent"):
    amounts = [field(amount_name, amount, evidence)] if amount_name else []
    return mol(entity_id, role, label, name, evidence, smiles, amounts)


def product(entity_id, label, name, evidence):
    return mol(entity_id, "product", label, name, evidence, None)


records = []

# Table 1: each optimization row is an independent experiment.
table1 = [
    (1, "FeCl3", 20, 1.5, 1.5, "CH2Cl2", 21, 38, 19),
    (2, "FeCl3", 30, 1.5, 1.5, "CH2Cl2", 17, 50, 13),
    (3, "FeCl3", 45, 1.5, 1.5, "CH2Cl2", 21, 60, 10),
    (4, "FeCl3", 45, 1.2, 1.5, "CH2Cl2", 21, 78, 8),
    (5, "FeCl3", 45, 1.0, 1.5, "CH2Cl2", 21, 67, 9),
    (6, "FeCl3", 45, 1.2, 1.5, "CH2Cl2", 22, 73, 0),
    (7, "Fe(acac)3", 45, 1.2, 1.5, "CH2Cl2", 22, 8, 62),
    (8, "Fe(NO3)3·9H2O", 45, 1.2, 1.5, "CH2Cl2", 18, 7, 89),
    (9, "FeCl3", 45, 1.2, None, "CH2Cl2", 21, 48, 35),
    (10, "FeCl3", 45, 1.2, 0.5, "CH2Cl2", 21, 57, 24),
    (11, None, None, 1.2, 1.5, "CH2Cl2", 12, "table dash (—)", 95),
    (12, None, None, 1.2, 1.5, "CH3CN", 18.5, "table dash (—)", 98),
    (13, "FeCl3", 45, 1.2, None, "CH3CN", 12.5, "table dash (—)", 96),
]

for entry, catalyst, loading, aeq, teq, solvent_key, hours, yld, recovery in table1:
    ev = P2 + P1 if entry == 1 else P2
    parts = [
        base_1a(ev),
        aldehyde("reactant_2a", "2a", "1-naphthaldehyde", SMILES["2a"], ev, aeq),
    ]
    if catalyst:
        parts.append(reagent(
            "catalyst", catalyst, catalyst,
            SMILES["FeCl3"] if catalyst == "FeCl3" else None,
            ev, "catalyst_loading", qty(loading, "mol%"), "catalyst",
        ))
    if teq is not None:
        parts.append(reagent("reagent_tmscl", "TMSCl", "trimethylsilyl chloride", SMILES["TMSCl"], ev,
                             "equivalents", qty(teq, "equiv")))
    if entry == 6:
        parts.append(reagent("reagent_mgso4", "MgSO4", "anhydrous magnesium sulfate", None, ev,
                             "equivalents", qty(1.0, "equiv")))
    parts.extend([
        reagent("solvent", solvent_key, "dichloromethane" if solvent_key == "CH2Cl2" else "acetonitrile",
                SMILES[solvent_key], ev, role="solvent"),
        reagent("internal_standard", "mesitylene", "mesitylene", SMILES["mesitylene"], ev),
        product("product_3a", "3a", "cyclized 1,2,3,6-tetrahydropyridine product 3a", ev),
    ])
    conditions = [
        field("temperature", qty(30, "°C"), ev),
        field("time", qty(hours, "h"), ev),
        field("solvent", solvent_key, ev),
    ]
    outcomes = [
        field("NMR_yield", qty(yld, "%") if isinstance(yld, (int, float)) else yld, ev, ["product_3a"]),
        field("recovered_starting_material_yield", qty(recovery, "%"), ev, ["reactant_1a"]),
        field("yield_and_recovery_measurement_basis", "1H NMR analysis with mesitylene as internal standard", ev),
    ]
    if entry == 4:
        outcomes.insert(1, field("isolated_yield", qty(71, "%"), ev, ["product_3a"]))
    notes = []
    unresolved = [
        "Product 3a is depicted, but its SMILES was not encoded because the machine structure interpretation is not source-verified.",
        "Exact batch scale, atmosphere, workup, and purification are not reported in the supplied main-text table; SI was not supplied.",
    ]
    if catalyst is None:
        notes.append("Catalyst column contains a table dash; no catalyst participant was added.")
    if teq is None:
        notes.append("TMSCl column contains a table dash; no TMSCl participant was added.")
    if not isinstance(yld, (int, float)):
        unresolved.append("The product-yield cell is a table dash whose meaning is not defined; it was not converted to zero or not detected.")
    if entry == 1:
        notes.append("The prose calls this Table 1 entry 1 and states 16 h, whereas the table gives 21 h.")
        unresolved.append("Conflicting duration: page-1 prose reports 16 h and Table 1 reports 21 h; the structured time follows the table row.")
    records.append(rec(
        f"table1_entry{entry:02d}", "optimization_entry", ev, parts,
        [{"step_id": "aza_prins_cyclization", "participant_ids": [p["entity_id"] for p in parts], "conditions": conditions}],
        outcomes, notes, unresolved,
    ))


# Table 2 substrate scope.
table2 = [
    (1, "2b", "benzaldehyde", "2b", 1.2, 13, 78, "3b"),
    (2, "2c", "2-chlorobenzaldehyde", "2c_o", 1.2, 13, 80, "3c"),
    (3, "2d", "4-nitrobenzaldehyde", "2d", 1.2, 11, 79, "3d"),
    (4, "2e", "2-bromobenzaldehyde", "2e", 1.2, 11, 83, "3e"),
    (5, "2f", "octanal", "2f", 1.2, 7, 83, "3f"),
    (6, "2g", "4-phenylbutanal", "2g", 1.2, 10, 86, "3g"),
    (7, "2h", "cyclohexanecarbaldehyde", "2h", 1.5, 8, 84, "3h"),
    (8, "2i", "2,2-dimethylpropanal (pivaldehyde)", "2i", 2.0, 12.5, 58, "3i"),
    (9, "2j", "paraformaldehyde", None, 1.2, 11, 74, "3j"),
]

for entry, aldehyde_label, aldehyde_name, smiles_key, equivalents, hours, yld, product_label in table2:
    ev = P2
    parts = [
        base_1a(ev),
        aldehyde("aldehyde", aldehyde_label, aldehyde_name, SMILES.get(smiles_key), ev, equivalents),
        reagent("catalyst", "FeCl3", "iron(III) chloride", SMILES["FeCl3"], ev,
                "catalyst_loading", qty(45, "mol%"), "catalyst"),
        reagent("reagent_tmscl", "TMSCl", "trimethylsilyl chloride", SMILES["TMSCl"], ev,
                "equivalents", qty(1.5, "equiv")),
        reagent("solvent", "CH2Cl2", "dichloromethane", SMILES["CH2Cl2"], ev, role="solvent"),
        product("product", product_label, f"1,2,3,6-tetrahydropyridine derivative {product_label}", ev),
    ]
    outcomes = [
        field("isolated_yield", qty(yld, "%"), ev, ["product"]),
        field("yield_measurement_basis", "isolated product", ev),
    ]
    notes = []
    unresolved = [
        f"Product {product_label} is depicted, but its SMILES was not encoded because the machine structure interpretation is not source-verified.",
        "Exact batch scale, atmosphere, workup, and purification are absent from the supplied main text; SI was not supplied.",
    ]
    if entry == 8:
        parts.insert(-1, reagent("internal_standard", "mesitylene", "mesitylene", SMILES["mesitylene"], ev))
        outcomes.extend([
            field("conversion", qty(89, "%"), ev, ["reactant_1a"]),
            field("conversion_measurement_basis", "1H NMR analysis of the crude product with mesitylene as internal standard", ev),
        ])
    if entry == 9:
        unresolved.append("Paraformaldehyde is polymeric/generic in the source; no single molecular SMILES was assigned.")
    records.append(rec(
        f"table2_entry{entry:02d}", "substrate_scope_entry", ev, parts,
        [{"step_id": "aza_prins_cyclization", "participant_ids": [p["entity_id"] for p in parts], "conditions": [
            field("temperature", qty(30, "°C"), ev), field("time", qty(hours, "h"), ev), field("solvent", "CH2Cl2", ev)
        ]}], outcomes, notes, unresolved,
    ))


# Separate gram-scale experiment, not merged with Table 2 entry 9.
ev = P2
parts = [
    mol("reactant_1a", "reactant", "1a", "N-(buta-2,3-dienyl)-4-tolylsulfonamide", ev, SMILES["1a"],
        [field("mass", qty(1.1158, "g"), ev)]),
    aldehyde("reactant_2j", "2j", "paraformaldehyde", None, ev, 2.0),
    reagent("catalyst", "FeCl3", "iron(III) chloride", SMILES["FeCl3"], ev,
            "catalyst_loading", qty(45, "mol%"), "catalyst"),
    reagent("reagent_tmscl", "TMSCl", "trimethylsilyl chloride", SMILES["TMSCl"], ev,
            "equivalents", qty(1.5, "equiv")),
    reagent("solvent", "CH2Cl2", "dichloromethane", SMILES["CH2Cl2"], ev, role="solvent"),
    product("product_3j", "3j", "1,2,3,6-tetrahydropyridine derivative 3j", ev),
]
records.append(rec(
    "eq1_gram_scale_3j", "reported_experiment", ev, parts,
    [{"step_id": "gram_scale_aza_prins_cyclization", "participant_ids": [p["entity_id"] for p in parts], "conditions": [
        field("temperature", qty(30, "°C"), ev), field("time", qty(11, "h"), ev), field("solvent", "CH2Cl2", ev)
    ]}],
    [field("reported_yield", qty(70, "%"), ev, ["product_3j"]), field("yield_measurement_basis", None, [])],
    ["This one-gram-scale experiment is distinct from Table 2 entry 9, which reports 74% under the scope protocol."],
    [
        "Yield measurement basis is not stated for eqn (1).",
        "Product 3j is depicted, but its SMILES was not encoded because the machine structure interpretation is not source-verified.",
        "Atmosphere, workup, and purification are absent from the supplied main text; SI was not supplied.",
        "Paraformaldehyde is polymeric/generic in the source; no single molecular SMILES was assigned.",
    ],
))


# Table 3 substrate scope; the arrow gives the 10 h default and footnotes override entries 6 and 8.
table3 = [
    (1, "2c", "4-chlorobenzaldehyde", "2c_p", 10, 67, "4a"),
    (2, "2k", "4-bromobenzaldehyde", "2k", 10, 66, "4b"),
    (3, "2l", "4-fluorobenzaldehyde", "2l", 10, 74, "4c"),
    (4, "2m", "4-methylbenzaldehyde", "2m", 10, 81, "4d"),
    (5, "2n", "4-methoxybenzaldehyde", "2n", 10, 67, "4e"),
    (6, "2o", "3-methoxybenzaldehyde", "2o", 14, 66, "4f"),
    (7, "2p", "2-fluorobenzaldehyde", "2p", 10, 53, "4g"),
    (8, "2q", "butanal", "2q", 36, 46, "4h"),
]

for entry, aldehyde_label, aldehyde_name, smiles_key, hours, yld, product_label in table3:
    ev = P2
    parts = [
        aldehyde("aldehyde", aldehyde_label, aldehyde_name, SMILES[smiles_key], ev, concentration=0.1),
        mol("reactant_1b", "reactant", "1b", "N-(2-phenylbuta-2,3-dienyl)-4-tolylsulfonamide", ev, SMILES["1b"],
            [field("equivalents", qty(1.5, "equiv"), ev)]),
        reagent("catalyst", "FeCl3", "iron(III) chloride", SMILES["FeCl3"], ev,
                "catalyst_loading", qty(30, "mol%"), "catalyst"),
        reagent("reagent_tmscl", "TMSCl", "trimethylsilyl chloride", SMILES["TMSCl"], ev,
                "equivalents", qty(1.5, "equiv")),
        reagent("solvent", "CH2Cl2", "dichloromethane", SMILES["CH2Cl2"], ev, role="solvent"),
        product("product", product_label, f"2,5-dihydro-1H-pyrrole derivative {product_label}", ev),
    ]
    notes = []
    unresolved = [
        f"Product {product_label} is depicted, but its SMILES was not encoded because the machine structure interpretation is not source-verified.",
        "Exact batch scale, atmosphere, workup, and purification are absent from the supplied main text; SI was not supplied.",
    ]
    if entry == 1:
        notes.append("Table 3 assigns label 2c to 4-chlorobenzaldehyde, while Table 2 assigns label 2c to 2-chlorobenzaldehyde.")
        unresolved.append("Conflicting reuse of source label 2c between Tables 2 and 3 was preserved without reconciling the structures.")
    records.append(rec(
        f"table3_entry{entry:02d}", "substrate_scope_entry", ev, parts,
        [{"step_id": "aza_prins_cyclization", "participant_ids": [p["entity_id"] for p in parts], "conditions": [
            field("temperature", qty(30, "°C"), ev), field("time", qty(hours, "h"), ev), field("solvent", "CH2Cl2", ev)
        ]}],
        [field("isolated_yield", qty(yld, "%"), ev, ["product"]), field("yield_measurement_basis", "isolated product", ev)],
        notes, unresolved,
    ))


# Scheme 2 contains three distinct Suzuki experiments.
suzuki = [
    ("6a", "3j", "phenylboronic acid", "phenylboronic_acid", 85),
    ("6b", "3j", "2-furylboronic acid", "furylboronic_acid", 90),
    ("6c", "3b", "phenylboronic acid", "phenylboronic_acid", 85),
]

for product_label, start_label, boronic_name, boronic_key, yld in suzuki:
    ev = P2
    boronic_label = "5a" if boronic_key == "phenylboronic_acid" else "5b"
    parts = [
        mol("reactant_3", "reactant", start_label, f"chlorinated tetrahydropyridine derivative {start_label}", ev, None),
        aldehyde("reactant_boronic_acid", boronic_label, boronic_name, SMILES[boronic_key], ev, 2.0),
        reagent("catalyst_pd", "Pd(OAc)2", "palladium(II) acetate", None, ev,
                "catalyst_loading", qty(3, "mol%"), "catalyst"),
        reagent("ligand", "LB-Phos·HBF4", "LB-Phos tetrafluoroborate", None, ev,
                "catalyst_loading", qty(6, "mol%")),
        reagent("base", "K3PO4", "tripotassium phosphate", None, ev,
                "equivalents", qty(3.5, "equiv")),
        reagent("water", "H2O", "water", SMILES["water"], ev,
                "equivalents", qty(2.0, "equiv")),
        reagent("solvent", "dioxane", "1,4-dioxane", SMILES["dioxane"], ev, role="solvent"),
        product("product", product_label, f"Suzuki cross-coupling product {product_label}", ev),
    ]
    records.append(rec(
        f"scheme2_{product_label}", "reported_experiment", ev, parts,
        [{"step_id": "suzuki_cross_coupling", "participant_ids": [p["entity_id"] for p in parts], "conditions": [
            field("temperature", qty(110, "°C"), ev), field("time", qty(12, "h"), ev), field("solvent", "dioxane", ev)
        ]}],
        [field("reported_yield", qty(yld, "%"), ev, ["product"]), field("yield_measurement_basis", None, [])],
        [],
        [
            "Yield measurement basis is not stated in Scheme 2.",
            f"Starting material {start_label} and product {product_label} are depicted, but their SMILES were not encoded because the machine structure interpretation is not source-verified.",
            "Batch scale, atmosphere, workup, and purification are absent from the supplied main text; SI was not supplied.",
        ],
    ))


# Scheme 1 is a generic proposed pathway, not a reported experiment.
ev = P1
parts = [
    mol("generic_1", "reactant", "1", "generic alpha-sulfonamido-allene", ev, None),
    mol("generic_2", "reactant", "2", "generic aldehyde", ev, None),
    reagent("acid", "acid", "unspecified acid", None, ev, role="unspecified_agent"),
    reagent("nucleophile", "X−", "unspecified nucleophile", None, ev, role="unspecified_agent"),
    product("possible_A", "A", "possible six-membered product A", ev),
    product("possible_B", "B", "possible five-membered product B", ev),
    product("possible_C", "C", "possible five-membered product C", ev),
]
records.append(rec(
    "scheme1_possible_pathways", "mechanism", ev, parts,
    [
        {"step_id": "proposed_imine_formation", "participant_ids": ["generic_1", "generic_2", "acid"], "conditions": [field("operation", "proposed formation of Int-1 or Int-2 under acid", ev)]},
        {"step_id": "proposed_cyclization_and_capture", "participant_ids": ["generic_1", "generic_2", "nucleophile", "possible_A", "possible_B", "possible_C"], "conditions": [field("operation", "proposed cyclization followed by nucleophilic attack", ev)]},
    ], [],
    ["Scheme 1 is captioned 'Possible reaction pathways' and is not treated as a performed experiment."],
    ["Generic R groups and X− prevent assignment of fully specified molecular structures and experimental quantities."],
))


# Scheme 3 is the authors' mechanistic rationale, not a reported experiment.
ev = P3
parts = [
    mol("generic_1", "reactant", "1", "generic alpha-sulfonamido-allene", ev, None),
    mol("generic_2", "reactant", "2", "generic aldehyde", ev, None),
    reagent("fecl3", "FeCl3", "iron(III) chloride", SMILES["FeCl3"], ev, role="catalyst"),
    reagent("tmscl", "TMSCl", "trimethylsilyl chloride", SMILES["TMSCl"], ev),
    reagent("chloride", "Cl−", "chloride", "[Cl-]", ev),
    mol("intermediate_7", "unspecified_agent", "7", "proposed allylic cation intermediate 7", ev, None),
    mol("intermediate_8", "unspecified_agent", "8", "proposed six-membered intermediate 8", ev, None),
    mol("intermediate_9", "unspecified_agent", "9", "proposed phenyl-stabilized intermediate 9", ev, None),
    product("generic_3", "3", "generic 1,2,3,6-tetrahydropyridine product", ev),
    product("generic_4", "4", "generic 2,5-dihydro-1H-pyrrole product", ev),
]
records.append(rec(
    "scheme3_selectivity_rationale", "mechanism", ev, parts,
    [
        {"step_id": "proposed_condensation", "participant_ids": ["generic_1", "generic_2", "fecl3", "tmscl", "intermediate_7"], "conditions": [field("operation", "proposed FeCl3/TMSCl-promoted formation of intermediate 7", ev)]},
        {"step_id": "r1_h_branch", "participant_ids": ["intermediate_7", "intermediate_8", "chloride", "generic_3"], "conditions": [field("operation", "proposed R1 = H six-membered cyclization and chloride capture", ev)]},
        {"step_id": "r1_ph_branch", "participant_ids": ["intermediate_7", "intermediate_9", "chloride", "generic_4"], "conditions": [field("operation", "proposed R1 = Ph five-membered cyclization and chloride capture", ev)]},
    ], [],
    ["Scheme 3 is captioned as a rationale for selectivity and is not treated as a performed experiment."],
    ["Generic R groups and proposed intermediates prevent assignment of fully specified molecular structures or experimental quantities."],
))


output = Path(__file__).with_name("records_pages_0001_0003.json")
output.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
print(f"wrote {len(records)} records to {output}")
