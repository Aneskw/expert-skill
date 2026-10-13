import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "runs" / "current"
DOC = "doc_8e2572f72396a218"

P1T = f"{DOC}:page1:text"
P1I = f"{DOC}:page1:image"
P2T = f"{DOC}:page2:text"
P2I = f"{DOC}:page2:image"
P3T = f"{DOC}:page3:text"
P3I = f"{DOC}:page3:image"
E1 = [P1T, P1I]
E2 = [P2T, P2I]
E3 = [P3T, P3I]


def fact(value, evidence):
    return {
        "value": value,
        "evidence_ids": list(evidence) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def quantity(number=None, unit=None, *, minimum=None, maximum=None,
             qualifier=None, raw_text=None):
    value = {"unit": unit}
    if number is not None:
        value["number"] = number
    else:
        value["minimum"] = minimum
        value["maximum"] = maximum
    if qualifier:
        value["qualifier"] = qualifier
    if raw_text:
        value["raw_text"] = raw_text
    return value


def field(name, value, evidence, targets=None):
    item = {"name": name, "fact": fact(value, evidence)}
    if targets:
        item["target_entity_ids"] = list(targets)
    return item


def participant(entity_id, role, label, evidence, *, name=None, smiles=None,
                amounts=None):
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


def missing_conditions(*names):
    return [field(name, None, []) for name in names]


def record(suffix, kind, evidence, participants, steps, outcomes=None,
           notes=None, unresolved=None):
    return {
        "record_id": f"{DOC}:{suffix}",
        "document_id": DOC,
        "source_reaction_id": suffix,
        "record_kind": kind,
        "status": "needs_review",
        "completeness": "partial",
        "evidence_ids": list(dict.fromkeys(evidence)),
        "participants": participants,
        "steps": steps,
        "outcomes": outcomes or [],
        "notes": [fact(value, ev) for value, ev in (notes or [])],
        "review": {
            "method": "model",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved or [],
        },
    }


def common_cyclization_participants(allene_label, allene_name, allene_smiles,
                                    product_label, evidence, condition,
                                    byproduct_mode=None):
    solvent_amounts = [
        field("total_volume", quantity(12, "mL"), evidence),
        field("receiving_solution_volume", quantity(2, "mL"), evidence),
    ]
    if condition == "B":
        solvent_amounts.insert(
            1, field("added_solution_volume", quantity(10, "mL"), evidence)
        )
    parts = [
        participant(
            "bisallene_1a", "reactant", "1a", evidence,
            name="1,5-bisallene 1a",
            amounts=[field("amount", quantity(0.25, "mmol"), evidence)],
        ),
        participant(
            "monoallene", "reactant", allene_label, evidence,
            name=allene_name, smiles=allene_smiles,
            amounts=[field("amount", quantity(0.625, "mmol"), evidence)],
        ),
        participant(
            "rhodium_catalyst", "catalyst", "trans-RhCl(CO)(PPh3)2", evidence,
            name="trans-chlorocarbonylbis(triphenylphosphine)rhodium(I)",
            amounts=[field("catalyst_loading", quantity(5, "mol%"), evidence)],
        ),
        participant(
            "toluene", "solvent", "toluene", evidence,
            name="toluene", smiles="Cc1ccccc1", amounts=solvent_amounts,
        ),
        participant("product_4", "product", product_label, evidence),
    ]
    if byproduct_mode:
        parts.append(participant("byproduct_2a", "product", "2a", evidence))
    return parts


records = []

# Page-1 prose reports an earlier cross-bisallene study without row-level details.
records.append(record(
    "prior_cross_bisallene_cyclization",
    "literature_example",
    E1,
    [
        participant(
            "bisallene_a", "reactant", "first 1,5-bisallene", E1,
            name="one of two different 1,5-bisallenes",
        ),
        participant(
            "bisallene_b", "reactant", "second 1,5-bisallene", E1,
            name="the other of two different 1,5-bisallenes",
        ),
        participant(
            "product_mixture", "product", "mixture of four products", E1,
            name="four cyclization products including two cross 18,19-norsteroid-like scaffolds",
        ),
    ],
    [{
        "step_id": "prior_bimolecular_cyclization",
        "participant_ids": ["bisallene_a", "bisallene_b", "product_mixture"],
        "conditions": [],
    }],
    notes=[(
        "The paper explicitly describes this as the authors' previously reported continuing study (reference 5), not as a new present-paper experiment.",
        E1,
    )],
    unresolved=[
        "The page gives no compound labels, quantities, catalyst, solvent, temperature, time, yields, or individual product structures for this cited study.",
        "The four-product mixture and two isolated cross-scaffold structures require the cited publication for experiment-level resolution.",
    ],
))

# Equation 1 is also explicitly prior work and is generic in X.
records.append(record(
    "equation1_prior_bisallene_dimerization",
    "literature_example",
    E2,
    [
        participant(
            "prior_bisallene_1", "reactant", "1", E2,
            name="X-substituted 1,5-bisallene",
            amounts=[field("equivalents", quantity(2, "equiv"), E2)],
        ),
        participant(
            "prior_rhodium_catalyst", "catalyst", "trans-RhCl(CO)(PPh3)2", E2,
            name="trans-chlorocarbonylbis(triphenylphosphine)rhodium(I)",
        ),
        participant(
            "prior_tetracycle_2", "product", "2", E2,
            name="generic X-substituted steroid-like tetracyclic skeleton",
        ),
    ],
    [{
        "step_id": "prior_bisallene_dimerization",
        "participant_ids": [
            "prior_bisallene_1", "prior_rhodium_catalyst", "prior_tetracycle_2"
        ],
        "conditions": [],
    }],
    notes=[(
        "Equation 1 is introduced as a recently reported reaction (reference 4); it is classified as prior literature even though the acknowledgments say the displayed result was reproduced.",
        E2 + E3,
    )],
    unresolved=[
        "X is generic, and catalyst loading, solvent, time, temperature, yield, atmosphere, workup, and purification are not reported with equation 1.",
        "Generic substrate and tetracyclic product structures remain unverified.",
    ],
))

# Equation 2: the present-paper 1a/3a cyclization under Condition A.
eq2_ev = E1 + E2
eq2_parts = common_cyclization_participants(
    "3a", "dimethyl 2-(buta-2,3-dienyl)malonate 3a",
    "C=C=CC(C(=O)OC)C(=O)OC", "4aa", eq2_ev, "A",
)
eq2_parts[1]["amounts"].append(field("equivalents", quantity(2.5, "equiv"), E2))
records.append(record(
    "equation2_1a_3a_to_4aa",
    "reported_experiment",
    eq2_ev,
    eq2_parts,
    [{
        "step_id": "condition_A_cyclization",
        "participant_ids": [p["entity_id"] for p in eq2_parts],
        "conditions": [
            field("temperature", quantity(80, "°C"), E2),
            field(
                "syringe_pump_addition_time",
                quantity(10, "h", qualifier="approx", raw_text="~10 h"), E2,
            ),
            field(
                "operation",
                "Condition A: a solution of 1a was added by syringe pump to a 2 mL toluene solution of catalyst and 3a at 80 °C.",
                E2,
            ),
        ] + missing_conditions("reaction_time", "atmosphere", "workup", "purification"),
    }],
    outcomes=[
        field("isolated_yield", quantity(46, "%"), E2, ["product_4"]),
        field("yield_measurement_basis", "isolated", E2, ["product_4"]),
    ],
    notes=[(
        "The graphical abstract summarizes the same 1a + 3a to 4aa transformation and is linked as cross-page evidence rather than treated as a separate experiment.",
        E1,
    )],
    unresolved=[
        "The total post-addition reaction duration, atmosphere, workup, and purification are not stated in the main text.",
        "The 1a and 4aa structures, including stereochemical details, remain unverified; the 3a SMILES is a tentative candidate from the legible drawing.",
    ],
))


table_rows = [
    (1, "3b", "phenylallene 3b", "C=C=Cc1ccccc1", "B", 22, 55, "4ab", "contaminated"),
    (2, "3c", "N-Boc-protected buta-2,3-dienyl tosylamide 3c", "C=C=CCN(S(=O)(=O)c1ccc(C)cc1)C(=O)OC(C)(C)C", "A", 21, 55, "4ac", "contaminated"),
    (3, "3d", "N-Boc-protected penta-3,4-dienyl tosylamide 3d", "C=C=CCCN(S(=O)(=O)c1ccc(C)cc1)C(=O)OC(C)(C)C", "A", 24, 50, "4ad", "contaminated"),
    (4, "3e", "penta-3,4-dien-1-ol 3e", "OCCC=C=C", "A", 22, 54, "4ae", "lt18"),
    (5, "3f", "buta-2,3-dienyl phthalimide 3f", "C=C=CCN1C(=O)c2ccccc2C1=O", "A", 24, 56, "4af", "lt18"),
    (6, "3g", "penta-3,4-dienyl phthalimide 3g", "C=C=CCCN1C(=O)c2ccccc2C1=O", "A", 24, 50, "4ag", "contaminated"),
]

for entry, allene, allene_name, smiles, condition, hours, yield_value, product, byproduct in table_rows:
    parts = common_cyclization_participants(
        allene, allene_name, smiles, product, E2, condition, byproduct
    )
    operation = (
        "Condition B: a solution of 1a and the monoallene in 10 mL toluene was added by syringe pump to a 2 mL toluene solution of catalyst over ~10 h at 80 °C."
        if condition == "B" else
        "Condition A: a solution of 1a was added by syringe pump to a 2 mL toluene solution of catalyst and the monoallene over ~10 h at 80 °C."
    )
    outcomes = [
        field("reported_yield", quantity(yield_value, "%"), E2, ["product_4"]),
    ]
    if byproduct == "lt18":
        outcomes.append(field(
            "byproduct_2a_yield",
            quantity(18, "%", qualifier="lt", raw_text="less than 18%"),
            E2,
            ["byproduct_2a"],
        ))
    else:
        outcomes.append(field(
            "byproduct_2a_observation",
            "2a was contaminated with other uncharacterized mixtures",
            E2,
            ["byproduct_2a"],
        ))
    notes = []
    if entry == 1:
        notes.append(("The phenylallene 3b was described as freshly prepared.", E2))
        notes.append(("The structure of 4ab was confirmed by X-ray diffraction (Figure 1, left; CCDC 651338).", E2))
    records.append(record(
        f"table1_entry{entry}_{allene}_{product}",
        "substrate_scope_entry",
        E2,
        parts,
        [{
            "step_id": f"condition_{condition}_cyclization",
            "participant_ids": [p["entity_id"] for p in parts],
            "conditions": [
                field("reaction_time", quantity(hours, "h"), E2),
                field("temperature", quantity(80, "°C"), E2),
                field(
                    "syringe_pump_addition_time",
                    quantity(10, "h", qualifier="approx", raw_text="~10 h"), E2,
                ),
                field("operation", operation, E2),
            ] + missing_conditions("atmosphere", "workup", "purification"),
        }],
        outcomes=outcomes,
        notes=notes,
        unresolved=[
            "The table does not state the measurement basis for the product or byproduct yield.",
            "Atmosphere, workup, and purification are not reported in the main text.",
            "The complex 1a, 2a, and bicyclic product structures remain unverified; the monoallene SMILES is a tentative candidate from the legible structure/name.",
        ],
    ))


def maleimide(smiles, label, name):
    return participant("maleimide", "reactant", label, E2, name=name, smiles=smiles)


records.append(record(
    "scheme1_4ab_nphenylmaleimide_to_5ab",
    "reported_experiment",
    E2,
    [
        participant("diene_4ab", "reactant", "4ab", E2),
        maleimide("O=C1C=CC(=O)N1c1ccccc1", "N-phenyl maleimide", "N-phenylmaleimide"),
        participant("toluene", "solvent", "toluene", E2, name="toluene", smiles="Cc1ccccc1"),
        participant("tetracycle_5ab", "product", "(±)-5ab", E2),
    ],
    [{
        "step_id": "intermolecular_diels_alder",
        "participant_ids": ["diene_4ab", "maleimide", "toluene", "tetracycle_5ab"],
        "conditions": [
            field("temperature", "reflux", E2),
        ] + missing_conditions("time", "atmosphere", "workup", "purification"),
    }],
    outcomes=[
        field("reported_yield", quantity(91, "%"), E2, ["tetracycle_5ab"]),
        field("diastereomeric_ratio", "higher than 6.3:1", E2, ["tetracycle_5ab"]),
    ],
    notes=[(
        "The structure of tetracyclic product 5ab was confirmed by X-ray diffraction (Figure 1, right; CCDC 651339).",
        E2,
    )],
    unresolved=[
        "Reactant quantities, solvent volume, numerical reflux temperature, duration, atmosphere, workup, purification, and yield basis are not reported.",
        "The 4ab and 5ab connectivity and relative stereochemistry remain unverified.",
    ],
))

records.append(record(
    "scheme1_4ag_nethylmaleimide_to_5ag",
    "reported_experiment",
    E2,
    [
        participant("diene_4ag", "reactant", "4ag", E2),
        maleimide("CCN1C(=O)C=CC1=O", "N-ethyl maleimide", "N-ethylmaleimide"),
        participant("toluene", "solvent", "toluene", E2, name="toluene", smiles="Cc1ccccc1"),
        participant("tetracycle_5ag", "product", "(±)-5ag", E2),
    ],
    [{
        "step_id": "intermolecular_diels_alder",
        "participant_ids": ["diene_4ag", "maleimide", "toluene", "tetracycle_5ag"],
        "conditions": [
            field("temperature", "reflux", E2),
        ] + missing_conditions("time", "atmosphere", "workup", "purification"),
    }],
    outcomes=[
        field("reported_yield", quantity(81, "%"), E2, ["tetracycle_5ag"]),
        field("diastereomeric_ratio", "≥93.5:6.5", E2, ["tetracycle_5ag"]),
    ],
    unresolved=[
        "Reactant quantities, solvent volume, numerical reflux temperature, duration, atmosphere, workup, purification, and yield basis are not reported.",
        "The 4ag and 5ag connectivity and relative stereochemistry remain unverified.",
    ],
))


# Scheme 2: allylation followed immediately by intramolecular Diels-Alder.
s2_ev = E1 + E3
s2_parts = [
    participant("diene_4aa", "reactant", "4aa", s2_ev),
    participant(
        "bromocrotonate", "reactant", "ethyl 4-bromocrotonate", E3,
        name="ethyl 4-bromobut-2-enoate", smiles="CCOC(=O)C=CCBr",
    ),
    participant("potassium_carbonate", "reagent", "K2CO3", E3, name="potassium carbonate", smiles="[K+].[K+].[O-]C([O-])=O"),
    participant("tbab", "reagent", "TBAB", E3, name="tetrabutylammonium bromide", smiles="CCCC[N+](CCCC)(CCCC)CCCC.[Br-]"),
    participant("dmf", "solvent", "DMF", E3, name="N,N-dimethylformamide", smiles="CN(C)C=O"),
    participant("dichloromethane", "solvent", "CH2Cl2", E3, name="dichloromethane", smiles="ClCCl"),
    participant("petroleum_ether", "solvent", "petroleum ether", E3, name="petroleum ether"),
    participant("tetracycle_6", "product", "(±)-6", s2_ev),
]
records.append(record(
    "scheme2_4aa_to_tetracycle_6",
    "reported_experiment",
    s2_ev,
    s2_parts,
    [
        {
            "step_id": "allylation_intramolecular_diels_alder",
            "participant_ids": [
                "diene_4aa", "bromocrotonate", "potassium_carbonate", "tbab",
                "dmf", "tetracycle_6",
            ],
            "conditions": [
                field("temperature", quantity(35, "°C"), E3),
                field("operation", "Allylation was followed immediately by cyclic Diels-Alder reaction.", E3),
            ] + missing_conditions("time", "atmosphere", "workup"),
        },
        {
            "step_id": "major_diastereomer_recrystallization",
            "participant_ids": ["tetracycle_6", "dichloromethane", "petroleum_ether"],
            "conditions": [
                field("purification", "recrystallization from CH2Cl2 and petroleum ether", E3),
            ],
        },
    ],
    outcomes=[
        field("reported_yield", quantity(85, "%"), E3, ["tetracycle_6"]),
        field("diastereomeric_ratio", "≥10:1", E3, ["tetracycle_6"]),
        field("ring_junction_selectivity", "C/D ring junction of the major diastereomer is trans", E3, ["tetracycle_6"]),
    ],
    notes=[
        ("The graphical abstract summarizes formation of 6 from 4aa; it is linked to this same experiment rather than counted separately.", E1),
        ("The major diastereomer was confirmed by X-ray diffraction (Figure 2, left; CCDC 651340).", E3),
    ],
    unresolved=[
        "Reactant/reagent quantities, solvent volume, duration, atmosphere, workup, and yield basis are not reported.",
        "The alkene geometry of ethyl 4-bromocrotonate and the connectivity/relative stereochemistry of 4aa and 6 remain unverified.",
    ],
))


# Scheme 3 is three successive executed stages and is therefore split.
s3_common = [
    participant("diene_4aa", "reactant", "4aa", E3),
    participant("propargyl_bromide", "reactant", "propargyl bromide", E3, name="3-bromoprop-1-yne", smiles="C#CCBr"),
    participant("potassium_carbonate", "reagent", "K2CO3", E3, name="potassium carbonate", smiles="[K+].[K+].[O-]C([O-])=O"),
    participant("tbab", "reagent", "TBAB", E3, name="tetrabutylammonium bromide", smiles="CCCC[N+](CCCC)(CCCC)CCCC.[Br-]"),
    participant("dmf", "solvent", "DMF", E3, name="N,N-dimethylformamide", smiles="CN(C)C=O"),
    participant("alkylation_product_7", "product", "7", E3),
]
records.append(record(
    "scheme3_stage1_4aa_to_7",
    "reported_experiment",
    E3,
    s3_common,
    [{
        "step_id": "propargyl_alkylation",
        "participant_ids": [p["entity_id"] for p in s3_common],
        "conditions": [
            field("temperature", "r.t.", E3),
        ] + missing_conditions("time", "atmosphere", "workup", "purification"),
    }],
    outcomes=[
        field(
            "reported_yield",
            quantity(99, "%", qualifier="gt", raw_text=">99%"),
            E3,
            ["alkylation_product_7"],
        ),
        field(
            "cycloaddition_observation",
            "No further Diels-Alder reaction occurred in this stage.",
            E3,
            ["alkylation_product_7"],
        ),
    ],
    notes=[("The prose describes the yield as almost quantitative; Scheme 3 prints >99%.", E3)],
    unresolved=[
        "Reactant/reagent quantities, solvent volume, time, atmosphere, workup, purification, and yield basis are not reported.",
        "The 4aa and 7 structures remain unverified.",
    ],
))

s3_stage2_parts = [
    participant("alkylation_product_7", "reactant", "7", E3),
    participant(
        "rhodium_catalyst", "catalyst", "trans-RhCl(CO)(PPh3)2", E3,
        name="trans-chlorocarbonylbis(triphenylphosphine)rhodium(I)",
        amounts=[field("catalyst_loading", quantity(5, "mol%"), E3)],
    ),
    participant("toluene", "solvent", "toluene", E3, name="toluene", smiles="Cc1ccccc1"),
    participant("diels_alder_product_8", "product", "8", E3),
]
records.append(record(
    "scheme3_stage2_7_to_8",
    "reported_experiment",
    E3,
    s3_stage2_parts,
    [{
        "step_id": "rhodium_catalyzed_intramolecular_diels_alder",
        "participant_ids": [p["entity_id"] for p in s3_stage2_parts],
        "conditions": [
            field("temperature", "reflux", E3),
        ] + missing_conditions("time", "atmosphere", "workup", "purification"),
    }],
    outcomes=[
        field("reported_yield", quantity(98, "%"), E3, ["diels_alder_product_8"]),
        field("diastereomeric_outcome", "mixture of diastereomeric products", E3, ["diels_alder_product_8"]),
    ],
    notes=[(
        "The paper notes that ring C in compound 8 may become somewhat aromatized in solvent if exposed to air.",
        E3,
    )],
    unresolved=[
        "Substrate amount, solvent volume, numerical reflux temperature, time, atmosphere, workup, purification, yield basis, and diastereomer ratio are not reported.",
        "The 7 and 8 structures and diastereomer assignments remain unverified.",
    ],
))

s3_stage3_ev = E1 + E3
s3_stage3_parts = [
    participant("diels_alder_product_8", "reactant", "8", E3),
    participant(
        "ddq", "reagent", "DDQ", E3,
        name="2,3-dichloro-5,6-dicyano-1,4-benzoquinone",
        smiles="N#CC1=C(Cl)C(=O)C(Cl)=C(C#N)C1=O",
        amounts=[field("equivalents", quantity(3, "equiv"), E3)],
    ),
    participant("toluene", "solvent", "toluene", E3, name="toluene", smiles="Cc1ccccc1"),
    participant("aromatic_tetracycle_9", "product", "9", s3_stage3_ev),
]
records.append(record(
    "scheme3_stage3_8_to_9",
    "reported_experiment",
    s3_stage3_ev,
    s3_stage3_parts,
    [{
        "step_id": "ddq_aromatization_desulfonylation",
        "participant_ids": [p["entity_id"] for p in s3_stage3_parts],
        "conditions": [
            field("temperature", "reflux", E3),
        ] + missing_conditions("time", "atmosphere", "workup", "purification"),
    }],
    outcomes=[
        field(
            "reported_yield",
            quantity(minimum=55, maximum=85, unit="%", raw_text="55-85%"),
            E3,
            ["aromatic_tetracycle_9"],
        ),
        field(
            "reaction_outcome",
            "aromatization formed two aromatic six-membered rings, with desulfonylation accompanying dehydrogenation",
            E3,
            ["aromatic_tetracycle_9"],
        ),
    ],
    notes=[
        ("The graphical abstract summarizes formation of 9 from 4aa; the intervening Scheme 3 stages remain separate experiment records.", E1),
        ("The structure of 9 was confirmed by X-ray diffraction (Figure 2, right; CCDC 651337).", E3),
    ],
    unresolved=[
        "Substrate amount, solvent volume, numerical reflux temperature, time, atmosphere, workup, purification, and yield basis are not reported.",
        "The reason for the 55-85% yield range is not specified in the main text.",
        "The 8 and 9 structures remain unverified.",
    ],
))


raw_path = BASE / "raw_model" / "records_pages_0001_0003.json"
raw_path.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")

record_ids = {r["source_reaction_id"]: r["record_id"] for r in records}
coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1,
            "state": "attempted",
            "regions": [
                {
                    "region": "abstract graphical reaction sequence in the middle of the original page",
                    "finding": "The arrows summarize the present-paper 1a+3a→4aa cyclization and later routes from 4aa to 6 and 9; linked to the detailed equation/scheme records rather than duplicated.",
                    "evidence_ids": [P1I, P1T],
                },
                {
                    "region": "introduction prose in both lower columns",
                    "finding": "One cited prior study of two different bisallenes giving four products and two cross 18,19-norsteroid-like scaffolds was classified as a literature example; broad review citations were not converted into present-paper experiments.",
                    "evidence_ids": [P1I, P1T],
                },
            ],
            "record_ids": [
                record_ids["prior_cross_bisallene_cyclization"],
                record_ids["equation2_1a_3a_to_4aa"],
                record_ids["scheme2_4aa_to_tetracycle_6"],
                record_ids["scheme3_stage3_8_to_9"],
            ],
            "unresolved": [
                "The abstract drawing is a summary and omits experiment-level conditions for the arrows to 6 and 9.",
                "The prior cross-bisallene study lacks row-level identities, conditions, yields, and individual product structures on this page.",
            ],
        },
        {
            "page": 2,
            "state": "attempted",
            "regions": [
                {
                    "region": "upper-left equation 1 and accompanying introduction",
                    "finding": "Generic X-substituted bisallene dimerization is explicitly previously reported and was classified as a literature example.",
                    "evidence_ids": [P2I, P2T],
                },
                {
                    "region": "left-column equation 2",
                    "finding": "Present-paper Condition-A cyclization of 1a and 3a to 4aa extracted with scale, stoichiometry, catalyst, solvent, 80 °C addition program, and 46% isolated yield.",
                    "evidence_ids": [P2I, P2T],
                },
                {
                    "region": "lower-left Table 1 and footnotes",
                    "finding": "All six monoallene scope rows extracted independently; A/B addition programs and byproduct-2a footnotes were applied only to their marked rows.",
                    "evidence_ids": [P2I, P2T],
                },
                {
                    "region": "upper-right Figure 1 and middle-right Scheme 1 with surrounding prose",
                    "finding": "Figure 1 was linked as structural context; the two distinct 4ab/4ag maleimide Diels–Alder experiments were extracted separately with yield and diastereomeric ratio.",
                    "evidence_ids": [P2I, P2T],
                },
            ],
            "record_ids": [
                record_ids["equation1_prior_bisallene_dimerization"],
                record_ids["equation2_1a_3a_to_4aa"],
                *[record_ids[f"table1_entry{i}_{a}_{p}"] for i, a, p in [
                    (1, "3b", "4ab"), (2, "3c", "4ac"), (3, "3d", "4ad"),
                    (4, "3e", "4ae"), (5, "3f", "4af"), (6, "3g", "4ag"),
                ]],
                record_ids["scheme1_4ab_nphenylmaleimide_to_5ab"],
                record_ids["scheme1_4ag_nethylmaleimide_to_5ag"],
            ],
            "unresolved": [
                "Table 1 does not state yield measurement basis, atmosphere, workup, or purification.",
                "Scheme 1 omits quantities, time, atmosphere, workup, purification, and yield basis.",
                "Equation 1 is generic prior work; X and experiment-level conditions are missing.",
                "Complex fused-product connectivity and stereochemistry remain unverified.",
            ],
        },
        {
            "page": 3,
            "state": "attempted",
            "regions": [
                {
                    "region": "upper-left Scheme 2 and adjacent prose",
                    "finding": "One-pot allylation/intramolecular Diels–Alder of 4aa to 6 extracted with DMF/35 °C, 85% yield, ≥10:1 dr, trans C/D junction, and the stated recrystallization solvents.",
                    "evidence_ids": [P3I, P3T],
                },
                {
                    "region": "middle-left Figure 2",
                    "finding": "ORTEP structures of 6 and 9 were linked to their reaction records and were not counted as additional reactions.",
                    "evidence_ids": [P3I, P3T],
                },
                {
                    "region": "upper-right Scheme 3 and surrounding prose",
                    "finding": "The propargyl alkylation, Rh-catalyzed intramolecular Diels–Alder, and DDQ aromatization/desulfonylation were extracted as three successive experimental stages.",
                    "evidence_ids": [P3I, P3T],
                },
                {
                    "region": "lower-right supporting-information statement and end matter",
                    "finding": "The paper says experimental procedures and characterization data are available online, but no SI file is supplied or explicitly associated in this workspace; no SI facts were inferred.",
                    "evidence_ids": [P3I, P3T],
                },
            ],
            "record_ids": [
                record_ids["equation1_prior_bisallene_dimerization"],
                record_ids["scheme2_4aa_to_tetracycle_6"],
                record_ids["scheme3_stage1_4aa_to_7"],
                record_ids["scheme3_stage2_7_to_8"],
                record_ids["scheme3_stage3_8_to_9"],
            ],
            "unresolved": [
                "Schemes 2–3 omit most quantities, reaction times, atmospheres, workups, purifications, and yield bases.",
                "The 55-85% yield range for 9 is not assigned to specific runs or conditions.",
                "No SI source was explicitly provided or associated despite the online-availability statement.",
                "Complex intermediates/products and their stereochemistry remain unverified.",
            ],
        },
    ],
}

coverage_dir = BASE / "coverage"
coverage_dir.mkdir(parents=True, exist_ok=True)
(coverage_dir / "pages_0001_0003.json").write_text(
    json.dumps(coverage, ensure_ascii=False, indent=2) + "\n"
)

tasks_path = BASE / "tasks.json"
tasks = json.loads(tasks_path.read_text())
for task in tasks:
    if task.get("document_id") == DOC and task.get("evidence_id") in {P1T, P2T, P3T}:
        task["state"] = "attempted"
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"records": len(records), "raw": str(raw_path), "coverage_pages": 3}, ensure_ascii=False))
