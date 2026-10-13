#!/usr/bin/env python3
"""Build source-linked machine records for ol070632r PDF pages 1--3."""
import json
from pathlib import Path

DOC = "doc_fef636b0d6662bed"
OUT = Path(__file__).with_name("records_pages_0001_0003.json")


def fact(value, evidence=()):
    return {
        "value": value,
        "evidence_ids": list(evidence) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def field(name, value, evidence=(), targets=()):
    item = {"name": name, "fact": fact(value, evidence)}
    if targets:
        item["target_entity_ids"] = list(targets)
    return item


def participant(entity_id, role, label, evidence, *, name=None, smiles=None, amounts=()):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence if name is not None else ()),
        "smiles": fact(smiles, evidence if smiles is not None else ()),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": list(amounts),
    }


def record(suffix, kind, evidence, *, participants=(), steps=(), outcomes=(), notes=(), unresolved=()):
    return {
        "record_id": f"{DOC}:{suffix}",
        "document_id": DOC,
        "source_reaction_id": suffix,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": list(evidence),
        "participants": list(participants),
        "steps": list(steps),
        "outcomes": list(outcomes),
        "notes": [fact(value, ev) for value, ev in notes],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": list(unresolved),
        },
    }


def step(step_id, participants, conditions=()):
    return {
        "step_id": step_id,
        "participant_ids": list(participants),
        "conditions": list(conditions),
    }


P1 = (f"{DOC}:page1:text", f"{DOC}:page1:image")
P2 = (f"{DOC}:page2:text", f"{DOC}:page2:image")
P3 = (f"{DOC}:page3:text", f"{DOC}:page3:image")

SOLVENT_SMILES = {
    "toluene": "Cc1ccccc1",
    "dioxane": "O1CCOCC1",
    "DMF": "CN(C)C=O",
    "THF": "C1CCOC1",
    "acetonitrile": "CC#N",
    "nitromethane": "C[N+](=O)[O-]",
    "DMA": "CC(=O)N(C)C",
}

records = []

# Page 1: generic graphical abstract, not an individual experiment.
abstract_parts = [
    participant("bisallene_6", "reactant", "6", P1, name="generic substituted 1,5-bisallene"),
    participant("triene_7", "product", "7", P1, name="generic seven-membered cross-conjugated triene"),
    participant("rh_i", "catalyst", "Rh(I)", P1),
    participant("solvent_unspecified", "solvent", "Solvent", P1),
]
records.append(record(
    "abstract_generic_cycloisomerization", "general_scheme", P1,
    participants=abstract_parts,
    steps=[step("graphical_abstract_arrow", [p["entity_id"] for p in abstract_parts], [
        field("solvent", "unspecified solvent", P1),
    ])],
    outcomes=[field(
        "reported_yield_range", {"minimum": 48, "maximum": 78, "unit": "%", "raw_text": "48-78%"},
        P1, ("triene_7",),
    )],
    notes=[("Generic X/R-substituent scheme; X is listed as C(CO2Me)2, TsN, O, or C(COMe)CO2Me.", P1)],
    unresolved=[
        "This graphical abstract summarizes a reaction family and is not an individual experiment.",
        "Generic R groups prevent assignment of complete reactant/product structures.",
        "The graphical abstract does not specify solvent identity, time, temperature, atmosphere, workup, purification, or yield basis.",
    ],
))

# Page 2 Scheme 1: two prior-literature pathways and one conceptual generic pathway.
for suffix, catalyst_label, intermediate_label, product_label, kind, note in [
    ("scheme1_rh_prior_pathway", "[Rh(I)]", "1", "2", "literature_example",
     "Prior rhodium pathway shown as proceeding through rhodacycle 1 to steroid-like tetracyclic product 2."),
    ("scheme1_pd_prior_pathway", "[Pd(0)]", "3", "4", "literature_example",
     "Prior palladium pathway shown as proceeding through palladacycle 3 to bicyclo[3.2.0] product 4."),
    ("scheme1_generic_m_pathway", "[M]", "5", None, "general_scheme",
     "Conceptual 5-type metallacyclic pathway used to motivate the reported cycloisomerization pattern."),
]:
    parts = [
        participant("generic_bisallene", "reactant", "generic 1,5-bisallene", P2),
        participant("metal_species", "catalyst", catalyst_label, P2),
        participant("metallacycle", "product", intermediate_label, P2, name="depicted metallacyclic intermediate"),
    ]
    if product_label:
        parts.append(participant("depicted_product", "product", product_label, P2))
    records.append(record(
        suffix, kind, P2, participants=parts,
        steps=[step("scheme1_arrow", [p["entity_id"] for p in parts])],
        notes=[(note, P2)],
        unresolved=[
            "Scheme 1 is pathway context, not a fully specified present-paper experiment.",
            "Generic X and schematic metal labels prevent complete structure assignment.",
            "No experimental quantities, time, temperature, workup, purification, or outcome basis are provided in Scheme 1.",
        ],
    ))

# Page 2 prose catalyst screen and equation 1 are distinct conditions.
screen_parts = [
    participant("substrate_6a", "reactant", "6a", P2),
    participant("product_7a", "product", "7a", P2),
    participant("steroid_like_products", "product", "unidentified regioisomeric bimolecular steroid-like products", P2),
    participant("trans_rhclco_pph3_2", "catalyst", "trans-RhCl(CO)(PPh3)2", P2,
                amounts=[field("catalyst_loading", {"number": 5, "unit": "mol%"}, P2)]),
    participant("toluene", "solvent", "toluene", P2, smiles=SOLVENT_SMILES["toluene"]),
]
records.append(record(
    "prose_screen_trans_rh_trace_7a", "optimization_entry", P2,
    participants=screen_parts,
    steps=[step("screening_reaction", [p["entity_id"] for p in screen_parts], [
        field("solvent", "toluene", P2),
        field("temperature", "reflux", P2),
    ])],
    outcomes=[field("qualitative_yield_7a", "trace", P2, ("product_7a",))],
    notes=[("A mixture of not-yet-fully identified regioisomeric bimolecular steroid-like products was also formed.", P2)],
    unresolved=[
        "The amount/concentration of 6a, reaction time, numerical reflux temperature, atmosphere, workup, purification, and yield basis are not reported for this screen.",
        "The identities and proportions of the bimolecular products are unresolved.",
        "Complex substrate and product structures require independent structure review.",
    ],
))

eq1_parts = [
    participant("substrate_6a", "reactant", "6a", P2),
    participant("product_7a", "product", "7a", P2),
    participant("rhclco2_dimer", "catalyst", "[RhCl(CO)2]2", P2,
                amounts=[field("catalyst_loading", {"number": 2, "unit": "mol%"}, P2)]),
    participant("toluene", "solvent", "toluene", P2, smiles=SOLVENT_SMILES["toluene"]),
]
records.append(record(
    "equation1_6a_to_7a", "reported_experiment", P2,
    participants=eq1_parts,
    steps=[step("cycloisomerization", [p["entity_id"] for p in eq1_parts], [
        field("solvent", "toluene", P2),
        field("reaction_concentration", {"number": 0.0417, "unit": "M"}, P2),
        field("temperature", {"number": 80, "unit": "°C"}, P2),
    ])],
    outcomes=[
        field("isolated_yield", {"number": 30, "unit": "%"}, P2, ("product_7a",)),
        field("yield_measurement_basis", "isolated", P2, ("product_7a",)),
    ],
    notes=[("The cross-conjugated structure of 7a was reported as confirmed by an NOE study.", P2)],
    unresolved=[
        "Reaction time, substrate amount, atmosphere, workup, and purification are not reported in the main-text equation.",
        "Complex substrate/product SMILES and stereochemistry require independent review.",
    ],
))


def table1_participants(entry, solvent):
    ev = P2
    scale = 1.5 if entry == 9 else 0.25
    items = [
        participant("substrate_6a", "reactant", "6a", ev,
                    amounts=[field("amount", {"number": scale, "unit": "mmol"}, ev)]),
        participant("product_7a", "product", "7a", ev),
        participant("solvent", "solvent", solvent, ev, smiles=SOLVENT_SMILES[solvent]),
    ]
    if entry <= 6:
        items.append(participant(
            "rhodium_catalyst", "catalyst", "rhodium catalyst (identity not specified in Table 1 footnote)", ev,
            amounts=[field("catalyst_loading", {"number": 2, "unit": "mol%"}, ev)],
        ))
    else:
        loading = 5 if entry == 7 else 2.5
        items.append(participant(
            "rhclcod_dimer", "catalyst", "[RhCl(COD)]2", ev,
            amounts=[field("catalyst_loading", {"number": loading, "unit": "mol%"}, ev)],
        ))
        ligand = "dppe" if entry == 7 else "dppp"
        ligand_smiles = (
            "P(c1ccccc1)(c1ccccc1)CCP(c1ccccc1)c1ccccc1" if ligand == "dppe" else
            "P(c1ccccc1)(c1ccccc1)CCCP(c1ccccc1)c1ccccc1"
        )
        items.append(participant(
            ligand, "reagent", ligand, ev, smiles=ligand_smiles,
            amounts=[field("ligand_loading", {"number": 10 if entry == 7 else 5, "unit": "mol%"}, ev)],
        ))
    return items


table1_rows = [
    (1, "dioxane", 19, 33, "reflux"),
    (2, "DMF", 19, 53, {"number": 100, "unit": "°C"}),
    (3, "THF", 41.5, 44, "reflux"),
    (4, "acetonitrile", 17.5, 62, "reflux"),
    (5, "nitromethane", 18, 26, "reflux"),
    (6, "DMA", 7.5, 53, {"number": 100, "unit": "°C"}),
    (7, "acetonitrile", 20, 52, "reflux"),
    (8, "acetonitrile", 45, 56, "reflux"),
    (9, "acetonitrile", 24, 55, "reflux"),
]
for entry, solvent, hours, yield_value, temperature in table1_rows:
    parts = table1_participants(entry, solvent)
    records.append(record(
        f"table1_entry{entry}", "optimization_entry", P2,
        participants=parts,
        steps=[step("cycloisomerization", [p["entity_id"] for p in parts], [
            field("solvent", solvent, P2),
            field("reaction_concentration", {"number": 0.0417, "unit": "M"}, P2),
            field("temperature", temperature, P2),
            field("time", {"number": hours, "unit": "h"}, P2),
        ])],
        outcomes=[
            field("reported_table_yield_of_4a", {"number": yield_value, "unit": "%"}, P2, ("product_7a",)),
            field("yield_measurement_basis", None, (), ("product_7a",)),
        ],
        notes=[(
            "Table 1 column header reads 'yield of 4a (%)', whereas the surrounding prose identifies the product of 6a as 7a; the numeric value is linked to the contextual 7a entity but the printed conflict is unresolved.",
            P2,
        )],
        unresolved=[
            "Product numbering conflict: Table 1 prints 4a, while the surrounding prose describes 7a.",
            "The yield measurement basis, atmosphere, workup, and purification are not reported.",
            "The identity of the 2 mol% rhodium catalyst in Table 1 entries 1-6 is not explicit in the table footnote." if entry <= 6 else
            "Complex substrate/product structures require independent review.",
            "Complex substrate/product structures require independent review.",
        ],
    ))


def table2_condition(condition, ev):
    parts = []
    conditions = [field("reaction_concentration", {"number": 0.0417, "unit": "M"}, ev)]
    if condition == "A":
        parts.extend([
            participant("rhclco2_dimer", "catalyst", "[RhCl(CO)2]2", ev,
                        amounts=[field("catalyst_loading", {"number": 2, "unit": "mol%"}, ev)]),
            participant("solvent", "solvent", "acetonitrile", ev, smiles=SOLVENT_SMILES["acetonitrile"]),
        ])
        conditions.extend([field("solvent", "acetonitrile", ev), field("temperature", "reflux", ev)])
    elif condition == "B":
        parts.extend([
            participant("rhclcod_dimer", "catalyst", "[RhCl(COD)]2", ev,
                        amounts=[field("catalyst_loading", {"number": 2.5, "unit": "mol%"}, ev)]),
            participant("dppp", "reagent", "dppp", ev,
                        smiles="P(c1ccccc1)(c1ccccc1)CCCP(c1ccccc1)c1ccccc1",
                        amounts=[field("ligand_loading", {"number": 5, "unit": "mol%"}, ev)]),
            participant("solvent", "solvent", "acetonitrile", ev, smiles=SOLVENT_SMILES["acetonitrile"]),
        ])
        conditions.extend([field("solvent", "acetonitrile", ev), field("temperature", "reflux", ev)])
    else:
        parts.extend([
            participant("rhclco2_dimer", "catalyst", "[RhCl(CO)2]2", ev,
                        amounts=[field("catalyst_loading", {"number": 2, "unit": "mol%"}, ev)]),
            participant("solvent", "solvent", "DMF", ev, smiles=SOLVENT_SMILES["DMF"]),
        ])
        conditions.extend([field("solvent", "DMF", ev), field("temperature", {"number": 110, "unit": "°C"}, ev)])
    return parts, conditions


table2_rows = [
    # entry, substrate, product, raw substituent description, condition, time, yield, footnote result
    (1, "6b", "7b", "X=CE2, R3=H; R1,R1=-(CH2)5-; R2,R2=H,H; E=CO2Me", "A", 9.5, 68, "ratio_7b_7primeb"),
    (2, "6b", "7b", "X=CE2, R3=H; R1,R1=-(CH2)5-; R2,R2=H,H; E=CO2Me", "B", 22, 54, "no_7prime"),
    (3, "6c", "7c", "X=CE2, R3=H; table displays Me,Me (6c), with exact column assignment requiring structure review", "C", 5, 71, None),
    (4, "6d", "7d", "X=CE2, R3=H; table displays -(CH2)5- (6d), with exact column assignment requiring structure review", "C", 9, 56, None),
    (5, "6e", "7e", "X=AcCE, R3=H; R1,R1=Me,Me; R2,R2=H,H; E=CO2Me; Ac=CH3CO", "B", 21, 48, "no_7prime"),
    (6, "6f", "7f", "X=NTs, R3=H; R1,R1=Me,Me; R2,R2=H,H", "A", 69, 70, "lt5_7prime"),
    (7, "6g", "7g", "X=NTs, R3=H; R1,R1=Et,Et; R2,R2=H,H", "A", 57, 78, "lt5_7prime"),
    (8, "6h", "7h", "X=NTs, R3=H; R1,R1=-(CH2)5-; R2,R2=H,H", "A", 69, 65, "lt5_7prime"),
    (9, "(S)-6i", "(S)-7i", "X=NTs, R3=Me; R1,R1=-(CH2)5-; R2,R2=H,H", "A", 24, 67, "ee_and_no_7prime"),
    (10, "6j", "7j", "X=O, R3=H; R1,R1=Et,Et; R2,R2=H,H", "A", 2, 61, "ratio_7j_7primej"),
]

for entry, substrate_label, product_label, substituents, condition, hours, yield_value, special in table2_rows:
    ev = P2 + P3 if entry <= 9 else P3
    substrate_id = f"substrate_{substrate_label.replace('(', '').replace(')', '').replace('-', '_')}"
    product_id = f"product_{product_label.replace('(', '').replace(')', '').replace('-', '_')}"
    parts = [
        participant(substrate_id, "reactant", substrate_label, ev, name=f"1,5-bisallene {substrate_label}; {substituents}",
                    amounts=[field("amount", {"number": 0.25, "unit": "mmol"}, P3)]),
        participant(product_id, "product", product_label, ev, name=f"seven-membered triene {product_label}"),
    ]
    condition_parts, conditions = table2_condition(condition, P3)
    parts.extend(condition_parts)
    conditions.append(field("time", {"number": hours, "unit": "h"}, P3))
    outcomes = [
        field("reported_yield", {"number": yield_value, "unit": "%"}, P3, (product_id,)),
        field("yield_measurement_basis", None, (), (product_id,)),
    ]
    notes = [(f"Table 2 condition {condition}; raw substituent transcription: {substituents}.", P3)]
    unresolved = [
        "Yield measurement basis, atmosphere, workup, and purification are not reported in the supplied main text.",
        "Complex substrate/product SMILES and product stereochemistry require independent review.",
        "Supporting information is mentioned but was not supplied or explicitly associated.",
    ]
    if entry in (3, 4):
        unresolved.append("The compact Table 2 substituent placement for this row cannot be assigned to both R columns with sufficient confidence from the page image alone.")
    if special:
        prime_label = product_label.replace("7", "7′", 1)
        prime_id = f"regioisomer_{entry}"
        parts.append(participant(prime_id, "product", prime_label, P3, name="7′-type regioisomer"))
        if special == "ratio_7b_7primeb":
            outcomes.append(field("product_ratio_7b_to_7primeb", "7.3:1", P3, (product_id, prime_id)))
        elif special == "ratio_7j_7primej":
            outcomes.append(field("product_ratio_7j_to_7primej", "16:1", P3, (product_id, prime_id)))
        elif special == "no_7prime":
            outcomes.append(field("7_prime_type_product_formation", "not observed", P3, (prime_id,)))
        elif special == "lt5_7prime":
            outcomes.append(field(
                "7_prime_type_regioisomer_selectivity",
                {"number": 5, "unit": "%", "qualifier": "lt", "raw_text": "<5%, if any"},
                P3, (prime_id,),
            ))
        elif special == "ee_and_no_7prime":
            outcomes.extend([
                field("starting_material_ee", {"number": 84, "unit": "%"}, P3, (substrate_id,)),
                field("product_ee", {"number": 84, "unit": "%"}, P3, (product_id,)),
                field("7_prime_type_product_formation", "not observed", P3, (prime_id,)),
            ])
    if entry == 1:
        notes.append((
            "The page-2 prose says conditions A gave '7a with a lower purity', whereas Table 2 entry 1 reports 68% 7b and a 7b/7′b ratio; this numbering/purity statement is retained as an unresolved source conflict.",
            P2,
        ))
        unresolved.append("Page-2 prose/Table-2 conflict for the condition-A 6b product label/purity requires external source review.")
    records.append(record(
        f"table2_entry{entry}_{substrate_label.replace('(', '').replace(')', '').replace('-', '_')}",
        "substrate_scope_entry", ev,
        participants=parts,
        steps=[step("cycloisomerization", [p["entity_id"] for p in parts], conditions)],
        outcomes=outcomes,
        notes=notes,
        unresolved=unresolved,
    ))

# Page 3 Scheme 2 is a proposed mechanism, not an experimental row.
mechanism_parts = [
    participant("substrate_6a", "reactant", "6a", P3),
    participant("rh_i", "catalyst", "Rh(I)", P3),
    participant("intermediate_m1", "unspecified_agent", "M1", P3, name="seven-membered bisallylic rhodium intermediate"),
    participant("intermediate_m2", "unspecified_agent", "M2", P3, name="intermediate after regioselective beta-H elimination"),
    participant("product_7a", "product", "7a", P3),
]
records.append(record(
    "scheme2_proposed_mechanism", "mechanism", P3,
    participants=mechanism_parts,
    steps=[
        step("a_cyclometalation", ["substrate_6a", "rh_i", "intermediate_m1"], [field("operation", "cyclometalation", P3)]),
        step("b_beta_h_elimination", ["intermediate_m1", "intermediate_m2"], [field("operation", "beta-H elimination", P3)]),
        step("c_reductive_elimination", ["intermediate_m2", "product_7a", "rh_i"], [field("operation", "reductive elimination", P3)]),
    ],
    notes=[("The authors describe Scheme 2 as a possible mechanism.", P3)],
    unresolved=[
        "Scheme 2 is a proposed mechanism and not an independently reported experiment.",
        "Organometallic intermediate structures and oxidation-state depictions require specialist review; no SMILES are assigned.",
    ],
))

OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"output": str(OUT), "records": len(records)}, ensure_ascii=False))
