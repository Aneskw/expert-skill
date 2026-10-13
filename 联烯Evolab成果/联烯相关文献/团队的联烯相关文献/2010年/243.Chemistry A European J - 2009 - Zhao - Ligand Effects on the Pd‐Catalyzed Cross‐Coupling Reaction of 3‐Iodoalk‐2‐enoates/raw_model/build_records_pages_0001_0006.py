import json
from pathlib import Path

DOC = "doc_ef875e24c663dcfb"
BASE = Path(__file__).resolve().parents[1]


def ev(page):
    return [f"{DOC}:page{page}:text", f"{DOC}:page{page}:image"]


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


def q(number, unit, **extra):
    value = {"number": number, "unit": unit}
    value.update(extra)
    return value


def qr(minimum, maximum, unit, raw_text):
    return {"minimum": minimum, "maximum": maximum, "unit": unit, "raw_text": raw_text}


def participant(entity_id, role, evidence, label=None, name=None, smiles=None, amounts=None):
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


def rec(suffix, page_evidence, kind, participants=None, steps=None, outcomes=None, notes=None, unresolved=None):
    return {
        "record_id": f"{DOC}:{suffix}",
        "document_id": DOC,
        "source_reaction_id": suffix,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": list(dict.fromkeys(page_evidence)),
        "participants": participants or [],
        "steps": steps or [],
        "outcomes": outcomes or [],
        "notes": [fact(n, page_evidence) for n in (notes or [])],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved or [
                "Machine-extracted record; molecular structures and field assignments require source review.",
                "Supporting information was not explicitly supplied or associated.",
            ],
        },
    }


def standard_agent(entity_id, name, evidence, role="reagent", amounts=None, smiles=None, label=None):
    return participant(entity_id, role, evidence, label=label, name=name, smiles=smiles, amounts=amounts)


def amount(name, value, evidence):
    return field(name, value, evidence)


def substrate(label, evidence, amounts=None, name=None, smiles=None, entity_id="substrate"):
    return participant(entity_id, "reactant", evidence, label=label, name=name, smiles=smiles, amounts=amounts)


def product(label, evidence, name=None, smiles=None, entity_id="product"):
    return participant(entity_id, "product", evidence, label=label, name=name, smiles=smiles)


records = []

# Page 1: generic modes and the split prior-work/this-work branches in Scheme 2.
e = ev(1)
records.append(rec(
    "scheme1_mode_i_generic", e, "general_scheme",
    participants=[
        participant("generic_propargyl_allenyl_palladium", "reactant", e, label="propargyl/1,2-allenyl palladium species"),
        participant("generic_organozinc", "reactant", e, label="R'ZnX"),
        product("generic_mode_i_product", e, entity_id="generic_product"),
    ],
    steps=[{"step_id": "mode_i_cross_coupling", "participant_ids": ["generic_propargyl_allenyl_palladium", "generic_organozinc", "generic_product"], "conditions": []}],
    notes=["Scheme 1 presents Mode I as a generic reaction manifold rather than an individual reported batch."],
    unresolved=["Generic R groups prevent assignment of complete structures or batch quantities."],
))
records.append(rec(
    "scheme1_mode_ii_generic", e, "general_scheme",
    participants=[
        participant("generic_propargyl_allenyl_zinc", "reactant", e, label="propargyl/1,2-allenyl zinc species"),
        participant("generic_organic_halide", "reactant", e, label="R'X"),
        standard_agent("palladium", "palladium catalyst", e, role="catalyst", label="Pd0"),
        product("generic_mode_ii_product", e, entity_id="generic_product"),
    ],
    steps=[{"step_id": "mode_ii_cross_coupling", "participant_ids": ["generic_propargyl_allenyl_zinc", "generic_organic_halide", "palladium", "generic_product"], "conditions": []}],
    notes=["Scheme 1 presents Mode II as a generic reaction manifold rather than an individual reported batch."],
    unresolved=["Generic R groups prevent assignment of complete structures or batch quantities."],
))
scheme2_common = [
    participant("arylalkyne", "reactant", e, label="1-arylalk-1-yne"),
    standard_agent("lithium_reagent", "lithium reagent", e),
    standard_agent("zinc_bromide", "zinc bromide", e, smiles="[Zn+2].[Br-].[Br-]"),
    standard_agent("palladium", "palladium catalyst", e, role="catalyst", label="[Pd]"),
]
records.append(rec(
    "scheme2_aryl_iodide_prior_work", e, "literature_example",
    participants=scheme2_common + [participant("aryl_iodide", "reactant", e, label="ArI"), product("allene (R'=ArI)", e, name="trisubstituted allene", entity_id="product")],
    steps=[
        {"step_id": "lithiation", "participant_ids": ["arylalkyne", "lithium_reagent"], "conditions": [field("temperature", q(-20, "°C"), e), field("time", q(1, "h"), e)]},
        {"step_id": "transmetalation_and_coupling", "participant_ids": ["zinc_bromide", "palladium", "aryl_iodide", "product"], "conditions": []},
    ],
    notes=["Scheme 2 labels the aryl-iodide branch as reference 8a; it is prior work, not a new batch in this paper."],
    unresolved=["The scheme is generic and does not report a batch scale, temperature for coupling, time, or yield."],
))
records.append(rec(
    "scheme2_iodoenoate_this_work_generic", e, "general_scheme",
    participants=scheme2_common + [participant("iodoenoate", "reactant", e, label="3-iodoalk-2-enoate"), product("allene (R'=iodoenoate fragment)", e, name="trienoate", entity_id="product")],
    steps=[
        {"step_id": "lithiation", "participant_ids": ["arylalkyne", "lithium_reagent"], "conditions": [field("temperature", qr(-78, 25, "°C", "-78 °C to room temperature"), e), field("time", q(1, "h"), e)]},
        {"step_id": "transmetalation_and_coupling", "participant_ids": ["zinc_bromide", "palladium", "iodoenoate", "product"], "conditions": []},
    ],
    notes=["Scheme 2 marks this generic iodoenoate branch as 'this work'."],
    unresolved=["The scheme is generic and does not specify one substrate, batch scale, coupling conditions, or yield."],
))

# Page 2: reassigned prior procedure and Table 1 optimization rows.
e2 = ev(2)
records.append(rec(
    "eq1_reassigned_prior_protocol", e2, "literature_example",
    participants=[
        substrate("1a", e2, name="1-phenylhex-1-yne", smiles="CCCCC#Cc1ccccc1", entity_id="alkyne_1a"),
        participant("iodoenoate_2", "reactant", e2, label="2"),
        standard_agent("mercury_chloride", "mercury(II) chloride", e2, amounts=[amount("loading", q(1.5, "mol%"), e2)], smiles="Cl[Hg]Cl"),
        standard_agent("n_butyllithium", "n-butyllithium", e2),
        standard_agent("zinc_bromide", "zinc bromide", e2, smiles="[Zn+2].[Br-].[Br-]"),
        standard_agent("pd_pph3_4", "tetrakis(triphenylphosphine)palladium(0)", e2, role="catalyst", amounts=[amount("loading", q(5, "mol%"), e2)]),
        product("actual regioisomer, exclusively E", e2, entity_id="actual_product"),
    ],
    steps=[
        {"step_id": "prior_protocol", "participant_ids": ["alkyne_1a", "iodoenoate_2", "mercury_chloride", "n_butyllithium", "zinc_bromide", "pd_pph3_4", "actual_product"], "conditions": [field("nBuLi_temperature", "r.t.", e2), field("ZnBr2_temperature", qr(-78, 25, "°C", "-78 °C to room temperature"), e2)]},
    ],
    notes=["Equation 1 reassigns products from an earlier reported procedure as the shown actual regioisomers; the proposed boxed regioisomer was not formed."],
    unresolved=["This is a reassessment of cited prior work; substrate 2 is generic and no batch yield or time is shown on this page."],
))


def table1_participants(entry):
    e = e2
    lda_eq = {2: 2.5, 3: 2.0}.get(entry, 3.3)
    parts = [
        substrate("1a", e, name="1-phenylhex-1-yne", smiles="CCCCC#Cc1ccccc1", entity_id="alkyne_1a", amounts=[amount("amount", q(0.50, "mmol"), e), amount("equivalents", q(1.7, "equiv"), e)]),
        substrate("(E)-2a", e, name="methyl 3-iodoprop-2(E)-enoate", smiles="COC(=O)/C=C/I", entity_id="iodide_E_2a", amounts=[amount("amount", q(0.30, "mmol"), e)]),
        standard_agent("lda", "lithium diisopropylamide", e, amounts=[amount("equivalents", q(lda_eq, "equiv"), e)]),
        standard_agent("zinc_bromide", "zinc bromide", e, amounts=[amount("amount", q(2.0, "mmol"), e), amount("equivalents", q(6.7, "equiv"), e)], smiles="[Zn+2].[Br-].[Br-]"),
        standard_agent("thf", "tetrahydrofuran", e, role="solvent", smiles="C1CCOC1"),
        product("(E)-3aa", e, name="methyl 4-propyl-6-phenylhexa-2(E),4,5-trienoate", smiles="COC(=O)/C=C/C(CCC)=C=Cc1ccccc1", entity_id="product_E_3aa"),
        product("(Z)-4aa", e, entity_id="product_Z_4aa"),
    ]
    if entry <= 5:
        parts.append(standard_agent("pd_pph3_4", "tetrakis(triphenylphosphine)palladium(0)", e, role="catalyst", amounts=[amount("loading", q(5, "mol%"), e)]))
    else:
        parts.append(standard_agent("pd_allyl_chloride_dimer", "bis(allylchloropalladium)", e, role="catalyst", label="[Pd(π-allyl)Cl]2", amounts=[amount("loading", q(2.5, "mol%"), e)]))
        ligand = "tri(o-tolyl)phosphine" if entry == 6 else "tri(2-furyl)phosphine"
        parts.append(standard_agent("ligand", ligand, e, amounts=[amount("loading", q(10, "mol%"), e)]))
    return parts


table1 = {
    1: (28, 2, 58, "81:19"), 2: (28, 2, "table dash (–)", "81:19"),
    3: (28, 2, "table dash (–)", "80:20"), 4: (27, 2, 44, "79:21"),
    5: (0, 17, 22, "89:11"), 6: (25, 3, 45, "78:22"),
    7: (25, 0.67, 64, "94:6"), 8: (0, 1, 77, "98:2"),
}
for entry, (temp, time, yld, ratio) in table1.items():
    parts = table1_participants(entry)
    lith_temp = q(0, "°C") if entry == 4 else qr(-78, 25, "°C", "-78 °C to room temperature")
    notes = []
    unresolved = ["Supporting information was not explicitly supplied or associated.", "Product structures and assignments remain machine-unverified."]
    if entry in (2, 3):
        notes.append("The isolated products were contaminated with an unidentified impurity; the table reports a dash for combined yield.")
        unresolved.append("A numerical combined yield is not reported because the products were contaminated with an unidentified impurity.")
    records.append(rec(
        f"table1_entry{entry}", e2, "optimization_entry", participants=parts,
        steps=[
            {"step_id": "lithiation", "participant_ids": ["alkyne_1a", "lda"], "conditions": [field("temperature", lith_temp, e2), field("time", q(1, "h"), e2)]},
            {"step_id": "transmetalation", "participant_ids": ["zinc_bromide"], "conditions": [field("temperature", "r.t.", e2), field("time", qr(0, 10, "min", "0–10 min"), e2)]},
            {"step_id": "cross_coupling", "participant_ids": [p["entity_id"] for p in parts], "conditions": [field("temperature", q(temp, "°C"), e2), field("time", q(time, "h"), e2)]},
        ],
        outcomes=[
            field("combined_yield", q(yld, "%") if isinstance(yld, (int, float)) else yld, e2, ["product_E_3aa", "product_Z_4aa"]),
            field("product_ratio_(E)-3aa/(Z)-4aa", ratio, e2, ["product_E_3aa", "product_Z_4aa"]),
            field("yield_measurement_basis", "isolated; selectivity determined after isolation", e2),
        ], notes=notes, unresolved=unresolved,
    ))

# Page 3: Table 2 scope and Scheme 3 isomerization controls.
e3 = ev(3)


def conditions_a_participants(alkyne_label, iodide_label, product_a, product_b, evidence, detailed=False):
    alkyne_name = "1-phenylhex-1-yne" if alkyne_label == "1a" else None
    alkyne_smiles = "CCCCC#Cc1ccccc1" if alkyne_label == "1a" else None
    iodide_names = {"(E)-2a": "methyl 3-iodoprop-2(E)-enoate", "(Z)-2a": "methyl 3-iodoprop-2(Z)-enoate", "(E)-2b": "ethyl 3-iodoprop-2(E)-enoate", "(Z)-2b": "ethyl 3-iodoprop-2(Z)-enoate"}
    parts = [
        substrate(alkyne_label, evidence, name=alkyne_name, smiles=alkyne_smiles, entity_id="alkyne", amounts=[amount("amount", q(0.50, "mmol"), evidence), amount("equivalents", q(1.7, "equiv"), evidence)]),
        substrate(iodide_label, evidence, name=iodide_names.get(iodide_label), entity_id="iodide", amounts=[amount("amount", q(0.30, "mmol"), evidence)]),
        standard_agent("lda", "lithium diisopropylamide", evidence, amounts=[amount("amount", q(1.0, "mmol"), evidence), amount("equivalents", q(3.3, "equiv"), evidence)]),
        standard_agent("zinc_bromide", "zinc bromide", evidence, amounts=[amount("amount", q(2.0, "mmol"), evidence), amount("equivalents", q(6.7, "equiv"), evidence)], smiles="[Zn+2].[Br-].[Br-]"),
        standard_agent("pd_allyl_chloride_dimer", "bis(allylchloropalladium)", evidence, role="catalyst", label="[Pd(π-allyl)Cl]2", amounts=[amount("loading", q(2.5, "mol%"), evidence)]),
        standard_agent("tfp", "tri(2-furyl)phosphine", evidence, amounts=[amount("loading", q(10, "mol%"), evidence)]),
        standard_agent("thf", "tetrahydrofuran", evidence, role="solvent", smiles="C1CCOC1"),
        product(product_a, evidence, entity_id="major_product"),
        product(product_b, evidence, entity_id="minor_product"),
    ]
    if detailed:
        parts[0]["amounts"].append(amount("mass", q(80, "mg"), evidence))
        parts[1]["amounts"].append(amount("mass", q(64, "mg"), evidence))
        parts[2]["amounts"] += [amount("volume", q(0.50, "mL"), evidence), amount("concentration", q(2.0, "M"), evidence)]
        parts[3]["amounts"].append(amount("mass", q(450, "mg"), evidence))
        parts[4]["amounts"] += [amount("mass", q(3, "mg"), evidence), amount("amount", q(0.0075, "mmol"), evidence)]
        parts[5]["amounts"] += [amount("mass", q(7, "mg"), evidence), amount("amount", q(0.030, "mmol"), evidence)]
    return parts


table2 = {
    1: ("1a", "(E)-2a", 0, 1, 77, "98:2", "(E)-3aa", "(Z)-4aa"),
    2: ("1a", "(E)-2b", 21, 1, 80, "96:4", "(E)-3ab", "(Z)-4ab"),
    3: ("1a", "(Z)-2a", 15, 0.5, 63, "98:2", "(E)-3aa", "(Z)-4aa"),
    4: ("1a", "(Z)-2b", 20, 0.5, 60, ">98:2", "(E)-3ab", "(Z)-4ab"),
    5: ("1b", "(E)-2a", 0, 1, 64, "98:2", "(E)-3ba", "(Z)-4ba"),
}
for entry, (alkyne, iodide, temp, time, yld, ratio, prod1, prod2) in table2.items():
    evidence = list(dict.fromkeys(e3 + (ev(6) if entry == 1 else [])))
    parts = conditions_a_participants(alkyne, iodide, prod1, prod2, evidence, detailed=(entry == 1))
    cross_conditions = [field("temperature", q(temp, "°C"), evidence), field("time", q(time, "h"), evidence)]
    steps = [
        {"step_id": "lithiation", "participant_ids": ["alkyne", "lda"], "conditions": [field("temperature", qr(-78, 25, "°C", "-78 °C to room temperature"), evidence), field("time", qr(1, 1.5, "h", "1–1.5 h"), evidence)]},
        {"step_id": "transmetalation", "participant_ids": ["zinc_bromide"], "conditions": [field("temperature", "r.t.", evidence), field("time", qr(20, 60, "min", "20–60 min"), evidence)]},
        {"step_id": "cross_coupling", "participant_ids": [p["entity_id"] for p in parts], "conditions": cross_conditions},
    ]
    notes = []
    if entry == 1:
        steps += [
            {"step_id": "workup", "participant_ids": ["major_product", "minor_product"], "conditions": [field("workup", "quench with saturated NH4Cl; extract with diethyl ether; dry over MgSO4; filter and evaporate", evidence)]},
            {"step_id": "purification", "participant_ids": ["major_product", "minor_product"], "conditions": [field("purification", "flash chromatography", evidence)]},
        ]
        notes.append("Typical procedure I on page 6 reports 56 mg of the inseparable product mixture.")
    records.append(rec(
        f"table2_entry{entry}", evidence, "substrate_scope_entry", participants=parts, steps=steps,
        outcomes=[
            field("combined_isolated_yield", q(yld, "%"), evidence, ["major_product", "minor_product"]),
            field("product_ratio_major/minor", ratio, evidence, ["major_product", "minor_product"]),
            field("yield_measurement_basis", "combined isolated yield; ratio by NMR after chromatography", evidence),
        ], notes=notes,
        unresolved=["Supporting information was not explicitly supplied or associated.", "Structures are retained as labels/candidate structures and remain machine-unverified."],
    ))

scheme3 = {
    1: ("96:4", 2.0, q(0, "°C"), q(1.5, "h"), 64, "96:4"),
    2: ("96:4", 2.0, "r.t.", q(1.5, "h"), 63, "92:8"),
    3: ("≤3:97", 2.0, q(0, "°C"), q(1.5, "h"), 55, "≤3:97"),
    4: ("≤3:97", 2.0, "r.t.", q(1.5, "h"), 45, "8:92"),
    5: ("96:4", 9.3, "r.t.", q(24, "h"), 50, "68:32"),
    6: ("<1:99", 9.3, "r.t.", q(24, "h"), 17, "67:33"),
}
for entry, (initial_ratio, equivalents, temp, time, yld, final_ratio) in scheme3.items():
    parts = [
        substrate("initial (E)-3aa", e3, entity_id="initial_E_3aa"),
        substrate("initial (Z)-4aa", e3, entity_id="initial_Z_4aa"),
        standard_agent("alkyne_1a", "1-phenylhex-1-yne", e3, role="reagent", label="1a", amounts=[amount("equivalents", q(equivalents, "equiv"), e3)], smiles="CCCCC#Cc1ccccc1"),
        standard_agent("lda", "lithium diisopropylamide", e3),
        standard_agent("zinc_bromide", "zinc bromide", e3, smiles="[Zn+2].[Br-].[Br-]"),
        product("recovered/equilibrated (E)-3aa", e3, entity_id="final_E_3aa"),
        product("recovered/equilibrated (Z)-4aa", e3, entity_id="final_Z_4aa"),
    ]
    records.append(rec(
        f"scheme3_entry{entry}", e3, "reported_experiment", participants=parts,
        steps=[
            {"step_id": "generate_organozinc_species", "participant_ids": ["alkyne_1a", "lda", "zinc_bromide"], "conditions": []},
            {"step_id": "isomerization_test", "participant_ids": ["initial_E_3aa", "initial_Z_4aa", "alkyne_1a", "final_E_3aa", "final_Z_4aa"], "conditions": [field("temperature", temp, e3), field("time", time, e3)]},
        ],
        outcomes=[
            field("initial_(E)-3aa/(Z)-4aa_ratio", initial_ratio, e3, ["initial_E_3aa", "initial_Z_4aa"]),
            field("NMR_yield", q(yld, "%"), e3, ["final_E_3aa", "final_Z_4aa"]),
            field("final_(E)-3aa/(Z)-4aa_ratio", final_ratio, e3, ["final_E_3aa", "final_Z_4aa"]),
            field("yield_measurement_basis", "NMR yield", e3),
        ],
        unresolved=["Exact LDA and ZnBr2 quantities are not stated in Scheme 3.", "Product structures remain machine-unverified."],
    ))

# Page 4: mechanism, Table 3 scope, and Table 4 parameter screen.
e4 = ev(4)
records.append(rec(
    "scheme4_interconversion_mechanism", e4, "mechanism",
    participants=[substrate("(E)-3aa", e4, entity_id="E_3aa"), substrate("(Z)-4aa", e4, entity_id="Z_4aa"), standard_agent("base", "base", e4), participant("intermediates_C_D", "unspecified_agent", e4, label="deprotonated intermediates C and D")],
    steps=[{"step_id": "proposed_interconversion", "participant_ids": ["E_3aa", "Z_4aa", "base", "intermediates_C_D"], "conditions": []}],
    notes=["Scheme 4 is explicitly a possible mechanism for interconversion, not a separate measured batch."],
    unresolved=["Generic base identity and kinetic details are not specified in the mechanism."],
))

table3 = {
    1: ("1a", "(Z)-2c", 20, 8, 48, "(E)-3ac"),
    2: ("1a", "(Z)-2d", 15, 1.5, 71, "(E)-3ad"),
    3: ("1a", "(Z)-2e", 19, 4.7, 34, "(E)-3ae"),
    4: ("1c", "(Z)-2d", 20, 1, 54, "(E)-3cd"),
    5: ("1d", "(Z)-2d", 24, 2, 74, "(E)-3dd"),
    6: ("1e", "(Z)-2d", 15, 1.5, 72, "(E)-3ed"),
    7: ("1f", "(Z)-2d", 18, 2, 53, "(E)-3fd"),
    8: ("1g", "(Z)-2d", 15, 1, 70, "(E)-3gd"),
}
alkyne_aliases = {"1a": "Ph/nC3H7", "1c": "Ph/Me", "1d": "p-PhC6H4/nC3H7", "1e": "p-MeOC6H4/nC3H7", "1f": "p-PhC6H4/nC5H11", "1g": "α-naphthyl/nC3H7"}
iodide_aliases = {"(Z)-2c": "R2=Ph", "(Z)-2d": "R2=Me", "(Z)-2e": "R2=Bn"}
for entry, (alkyne, iodide, temp, time, yld, prod) in table3.items():
    if entry == 1:
        alkyne_amounts = [amount("amount", q(0.44, "mmol"), e4)]
        iodide_amounts = [amount("amount", q(0.20, "mmol"), e4)]
        pd_loading, tfp_loading = 5, 20
    else:
        alkyne_amounts = [amount("amount", q(0.50, "mmol"), e4), amount("equivalents", q(1.7, "equiv"), e4)]
        iodide_amounts = [amount("amount", q(0.30, "mmol"), e4)]
        pd_loading, tfp_loading = 2.5, 10
    parts = [
        substrate(alkyne, e4, name="1-phenylhex-1-yne" if alkyne == "1a" else None, smiles="CCCCC#Cc1ccccc1" if alkyne == "1a" else None, entity_id="alkyne", amounts=alkyne_amounts),
        substrate(iodide, e4, entity_id="iodide", amounts=iodide_amounts),
        standard_agent("lda", "lithium diisopropylamide", e4, amounts=[amount("amount", q(1.0, "mmol"), e4)] + ([] if entry == 1 else [amount("equivalents", q(3.3, "equiv"), e4)])),
        standard_agent("zinc_bromide", "zinc bromide", e4, amounts=[amount("amount", q(2.0, "mmol"), e4)] + ([] if entry == 1 else [amount("equivalents", q(6.7, "equiv"), e4)])),
        standard_agent("pd_allyl_chloride_dimer", "bis(allylchloropalladium)", e4, role="catalyst", label="[Pd(π-allyl)Cl]2", amounts=[amount("loading", q(pd_loading, "mol%"), e4)]),
        standard_agent("tfp", "tri(2-furyl)phosphine", e4, amounts=[amount("loading", q(tfp_loading, "mol%"), e4)]),
        standard_agent("thf", "tetrahydrofuran", e4, role="solvent", smiles="C1CCOC1"),
        product(prod, e4, entity_id="product"),
    ]
    outcomes = [field("isolated_yield", q(yld, "%"), e4, ["product"]), field("yield_measurement_basis", "isolated yield", e4)]
    notes = [f"Table substituent mapping: alkyne {alkyne}={alkyne_aliases[alkyne]}; iodide {iodide}={iodide_aliases[iodide]}. The enyne regioisomer (Z)-4 was not observed."]
    if entry == 1:
        outcomes.append(field("iodide_conversion", q(64, "%"), e4, ["iodide"]))
        notes.append("Yield was calculated based on 64% conversion of the iodide.")
    records.append(rec(
        f"table3_entry{entry}", e4, "substrate_scope_entry", participants=parts,
        steps=[
            {"step_id": "lithiation", "participant_ids": ["alkyne", "lda"], "conditions": [field("temperature", qr(-78, 25, "°C", "-78 °C to room temperature"), e4), field("time", q(1, "h"), e4)]},
            {"step_id": "transmetalation", "participant_ids": ["zinc_bromide"], "conditions": [field("temperature", "r.t.", e4), field("time", qr(20, 50, "min", "20–50 min"), e4)]},
            {"step_id": "cross_coupling", "participant_ids": [p["entity_id"] for p in parts], "conditions": [field("temperature", q(temp, "°C"), e4), field("time", q(time, "h"), e4)]},
        ], outcomes=outcomes, notes=notes,
        unresolved=["Supporting information was not explicitly supplied or associated.", "Full structures are not assigned from generic substituent columns; labels are preserved."],
    ))

table4 = {
    1: (0, 1, "r.t.", 2, 23), 2: (-3, 1, 0, 1, 22), 3: (0, 1.5, -20, 11, 32),
    4: (-3, 2, -20, 10.5, 26), 5: (-3, 1.5, -20, 16, 18),
    6: (0, 1.5, -20, 16.5, 29), 7: (-20, 1.5, -20, 9, 20),
}
for entry, (t1temp, t1time, t2temp, t2time, yld) in table4.items():
    iodide_amount = 0.40 if entry == 5 else (0.20 if entry == 6 else 0.30)
    parts = [
        substrate("1a", e4, name="1-phenylhex-1-yne", smiles="CCCCC#Cc1ccccc1", entity_id="alkyne_1a", amounts=[amount("amount", q(0.50, "mmol"), e4), amount("equivalents", q(1.7, "equiv"), e4)]),
        substrate("(E)-2a", e4, name="methyl 3-iodoprop-2(E)-enoate", smiles="COC(=O)/C=C/I", entity_id="iodide_E_2a", amounts=[amount("amount", q(iodide_amount, "mmol"), e4)]),
        standard_agent("n_butyllithium", "n-butyllithium", e4, amounts=[amount("amount", qr(0.60, 0.64, "mmol", "0.60–0.64 mmol"), e4), amount("equivalents", qr(2.0, 2.1, "equiv", "2.0–2.1 equiv"), e4)]),
        standard_agent("zinc_bromide", "zinc bromide", e4, amounts=[amount("amount", q(1.0, "mmol"), e4), amount("equivalents", q(6.7, "equiv"), e4)]),
        standard_agent("thf", "tetrahydrofuran", e4, role="solvent", smiles="C1CCOC1"),
        product("(E)-5aa", e4, name="methyl 6-phenyl-4-propyl-5-yn-2(E)-enoate", smiles="COC(=O)/C=C/C(CCC)C#Cc1ccccc1", entity_id="product_E_5aa"),
    ]
    notes = []
    unresolved = ["Supporting information was not explicitly supplied or associated.", "Product structure remains machine-unverified."]
    if entry == 5:
        parts += [
            standard_agent("pd_pph3_2cl2", "bis(triphenylphosphine)palladium(II) dichloride", e4, role="catalyst", amounts=[amount("loading", q(5, "mol%"), e4)]),
            standard_agent("pd_pph3_4", "tetrakis(triphenylphosphine)palladium(0)", e4, role="catalyst", amounts=[amount("amount", q(0.020, "mmol"), e4), amount("loading", q(5, "mol%"), e4)]),
        ]
        notes.append("Table 4 footnotes c and d both attach to entry 5: c specifies Pd(PPh3)2Cl2, while d states 0.020 mmol Pd(PPh3)4; both statements are retained without reconciliation.")
        unresolved.append("Catalyst identity is internally inconsistent between footnotes c and d.")
    else:
        catalyst_amounts = [amount("loading", q(5, "mol%"), e4)]
        if entry == 6:
            catalyst_amounts.append(amount("amount", q(0.010, "mmol"), e4))
        parts.append(standard_agent("pd_pph3_4", "tetrakis(triphenylphosphine)palladium(0)", e4, role="catalyst", amounts=catalyst_amounts))
    records.append(rec(
        f"table4_entry{entry}", e4, "optimization_entry", participants=parts,
        steps=[
            {"step_id": "lithiation", "participant_ids": ["alkyne_1a", "n_butyllithium"], "conditions": [field("temperature", q(t1temp, "°C"), e4), field("time", q(t1time, "h"), e4)]},
            {"step_id": "transmetalation", "participant_ids": ["zinc_bromide"], "conditions": [field("operation", f"temperature changed from T1 to T2 ({t1temp} °C to {t2temp if isinstance(t2temp, int) else t2temp})", e4), field("time", qr(20, 42, "min", "20–42 min"), e4)]},
            {"step_id": "cross_coupling", "participant_ids": [p["entity_id"] for p in parts], "conditions": [field("temperature", q(t2temp, "°C") if isinstance(t2temp, int) else t2temp, e4), field("time", q(t2time, "h"), e4)]},
        ],
        outcomes=[field("isolated_yield", q(yld, "%"), e4, ["product_E_5aa"]), field("yield_measurement_basis", "isolated yield", e4)],
        notes=notes, unresolved=unresolved,
    ))

# Page 5: Table 5 ligand screen, Scheme 5 mechanism, and Table 6 catalyst efficiency.
e5 = ev(5)
table5 = {
    1: ("L1", "triphenyl phosphite", "overnight", 32, "100:0"),
    2: ("L2", "tri(2-furyl)phosphine", q(3, "h"), 26, "<7:1"),
    3: ("(R)-L3", "(R)-2-diphenylphosphino-2'-hydroxy-1,1'-binaphthalene", q(5, "min"), "table dash (–)", "0:100"),
}
for entry, (liglabel, ligname, time, yld, ratio) in table5.items():
    iodide_amount = 0.20 if entry == 1 else 0.30
    pd_loading = 5 if entry == 1 else 2.5
    parts = [
        substrate("1a", e5, name="1-phenylhex-1-yne", smiles="CCCCC#Cc1ccccc1", entity_id="alkyne_1a", amounts=[amount("amount", q(0.50, "mmol"), e5), amount("equivalents", q(1.7, "equiv"), e5)]),
        substrate("(E)-2a", e5, name="methyl 3-iodoprop-2(E)-enoate", smiles="COC(=O)/C=C/I", entity_id="iodide_E_2a", amounts=[amount("amount", q(iodide_amount, "mmol"), e5)]),
        standard_agent("n_butyllithium", "n-butyllithium", e5, amounts=[amount("amount", q(0.60, "mmol"), e5), amount("equivalents", q(2.0, "equiv"), e5)]),
        standard_agent("zinc_bromide", "zinc bromide", e5, amounts=[amount("equivalents", q(3.3, "equiv"), e5)]),
        standard_agent("pd_allyl_chloride_dimer", "bis(allylchloropalladium)", e5, role="catalyst", label="[Pd(π-allyl)Cl]2", amounts=[amount("loading", q(pd_loading, "mol%"), e5)]),
        standard_agent("ligand", ligname, e5, label=liglabel, amounts=[amount("loading", q(10, "mol%"), e5)]),
        product("(E)-5aa", e5, entity_id="product_E_5aa"),
        product("(E)-6aa", e5, name="methyl 4-phenylnona-2(E),4,5-trienoate", smiles="COC(=O)/C=C/C(c1ccccc1)=C=CCCC", entity_id="product_E_6aa"),
    ]
    if entry == 1:
        parts[4]["amounts"] += [amount("mass", q(4, "mg"), e5), amount("amount", q(0.010, "mmol"), e5)]
        parts[5]["amounts"] += [amount("mass", q(13, "mg"), e5), amount("amount", q(0.040, "mmol"), e5)]
    outcomes = [
        field("combined_yield", q(yld, "%") if isinstance(yld, (int, float)) else yld, e5, ["product_E_5aa", "product_E_6aa"]),
        field("product_ratio_(E)-5aa/(E)-6aa", ratio, e5, ["product_E_5aa", "product_E_6aa"]),
    ]
    notes, unresolved = [], ["Supporting information was not explicitly supplied or associated.", "Product structures remain machine-unverified."]
    if entry == 1:
        outcomes += [field("iodide_conversion", q(90, "%"), e5, ["iodide_E_2a"]), field("yield_measurement_basis", "combined yield based on 90% conversion; ratio by NMR of isolated product", e5)]
    elif entry == 2:
        outcomes.append(field("yield_measurement_basis", "combined yield; ratio is inaccurate because (E)-6aa is unstable during separation", e5))
        unresolved.append("The product ratio is explicitly described as inaccurate because (E)-6aa is unstable during separation.")
    else:
        outcomes.append(field("yield_measurement_basis", "yield unavailable due to instability; ratio by NMR analysis of the reaction mixture", e5))
        notes.append("Essentially no enantiomeric excess was observed with (R)-L3.")
        unresolved.append("No numerical yield is available because (E)-6aa is unstable.")
    records.append(rec(
        f"table5_entry{entry}", e5, "optimization_entry", participants=parts,
        steps=[
            {"step_id": "lithiation", "participant_ids": ["alkyne_1a", "n_butyllithium"], "conditions": [field("temperature", q(-20, "°C"), e5), field("time", q(1, "h"), e5)]},
            {"step_id": "transmetalation", "participant_ids": ["zinc_bromide"], "conditions": [field("operation", "temperature changed from -20 °C to room temperature", e5), field("time", qr(10, 34, "min", "10–34 min"), e5)]},
            {"step_id": "cross_coupling", "participant_ids": [p["entity_id"] for p in parts], "conditions": [field("time", time, e5), field("temperature", None, e5)]},
        ], outcomes=outcomes, notes=notes, unresolved=unresolved,
    ))

records.append(rec(
    "scheme5_proposed_ligand_effect", e5, "mechanism",
    participants=[participant("organopalladium_E", "unspecified_agent", e5, label="organopalladium intermediate E"), participant("intermediate_F", "unspecified_agent", e5, label="intermediate F"), participant("intermediate_G", "unspecified_agent", e5, label="intermediate G"), product("5", e5, entity_id="product_5"), product("6", e5, entity_id="product_6"), standard_agent("L3", "2-diphenylphosphino-2'-hydroxy-1,1'-binaphthalene", e5, label="L3")],
    steps=[{"step_id": "proposed_regiodivergence", "participant_ids": ["organopalladium_E", "intermediate_F", "intermediate_G", "product_5", "product_6", "L3"], "conditions": []}],
    notes=["Scheme 5 is a proposed explanation of ligand-controlled regioselectivity, not an independent experiment."],
    unresolved=["The intermediates are mechanistic proposals with generic substituents."],
))


def conditions_b_parts(evidence, catalyst_loading, ligand_loading, scale_large=False, product_label="(E)-6ad", iodide_label="(Z)-2d", alkyne_label="1a"):
    if scale_large:
        alkyne_amounts = [amount("amount", q(2.5, "mmol"), evidence), amount("equivalents", q(1.7, "equiv"), evidence)]
        iodide_amounts = [amount("amount", q(1.5, "mmol"), evidence)]
        nbu_amounts = [amount("equivalents", q(3.3, "equiv"), evidence)]
        zn_amounts = [amount("equivalents", q(3.3, "equiv"), evidence)]
    else:
        alkyne_amounts = [amount("amount", q(0.50, "mmol"), evidence), amount("equivalents", q(1.7, "equiv"), evidence)]
        iodide_amounts = [amount("amount", q(0.30, "mmol"), evidence)]
        nbu_amounts = [amount("amount", q(0.60, "mmol"), evidence), amount("equivalents", q(2.0, "equiv"), evidence)]
        zn_amounts = [amount("amount", q(1.0, "mmol"), evidence), amount("equivalents", q(3.3, "equiv"), evidence)]
    return [
        substrate(alkyne_label, evidence, name="1-phenylhex-1-yne" if alkyne_label == "1a" else None, smiles="CCCCC#Cc1ccccc1" if alkyne_label == "1a" else None, entity_id="alkyne", amounts=alkyne_amounts),
        substrate(iodide_label, evidence, name="methyl 3-iodobut-2(Z)-enoate" if iodide_label == "(Z)-2d" else None, entity_id="iodide", amounts=iodide_amounts),
        standard_agent("n_butyllithium", "n-butyllithium", evidence, amounts=nbu_amounts),
        standard_agent("zinc_bromide", "zinc bromide", evidence, amounts=zn_amounts),
        standard_agent("pd_allyl_chloride_dimer", "bis(allylchloropalladium)", evidence, role="catalyst", label="[Pd(π-allyl)Cl]2", amounts=[amount("loading", q(catalyst_loading, "mol%"), evidence)]),
        standard_agent("ligand", "racemic 2-diphenylphosphino-2'-hydroxy-1,1'-binaphthalene", evidence, label="(±)-L3", amounts=[amount("loading", q(ligand_loading, "mol%"), evidence)]),
        standard_agent("thf", "tetrahydrofuran", evidence, role="solvent", smiles="C1CCOC1"),
        product(product_label, evidence, name="methyl 3-methyl-4-phenylnona-2(E),4,5-trienoate" if product_label == "(E)-6ad" else None, entity_id="product"),
    ]


table6 = {1: (5, 20, q(4, "h"), 16), 2: (2.5, 10, q(5, "min"), 91), 3: (0.5, 2, q(5, "min"), 74), 4: (0.17, 0.67, q(30, "min"), 59)}
for entry, (pdload, ligload, time, yld) in table6.items():
    evidence = list(dict.fromkeys(e5 + (ev(6) if entry == 2 else [])))
    parts = conditions_b_parts(evidence, pdload, ligload, scale_large=(entry in (3, 4)))
    notes = []
    if entry == 1:
        parts[5]["name"] = fact("triphenyl phosphite", evidence)
        parts[5]["label"] = fact("L1", evidence)
        notes.append("The 16% yield is based on product isolated after flash chromatography and preparative TLC.")
    if entry == 2:
        parts[0]["amounts"] += [amount("mass", q(79, "mg"), evidence)]
        parts[2]["amounts"] += [amount("volume", q(0.38, "mL"), evidence), amount("concentration", q(1.6, "M"), evidence)]
        parts[3]["amounts"] += [amount("mass", q(225, "mg"), evidence)]
        parts[4]["amounts"] += [amount("mass", q(3, "mg"), evidence)]
        notes.append("This optimization row is the same batch as Table 7 entry 1 and the Typical procedure II begun on page 6; it is recorded once with combined evidence.")
    records.append(rec(
        "table6_entry2_table7_entry1" if entry == 2 else f"table6_entry{entry}", evidence,
        "reported_experiment" if entry == 2 else "optimization_entry", participants=parts,
        steps=[
            {"step_id": "lithiation", "participant_ids": ["alkyne", "n_butyllithium"], "conditions": [field("temperature", q(-20, "°C"), evidence), field("time", q(1, "h"), evidence)]},
            {"step_id": "transmetalation_cold", "participant_ids": ["zinc_bromide"], "conditions": [field("temperature", q(-20, "°C"), evidence), field("time", q(10, "min"), evidence)]},
            {"step_id": "warm_zinc_reagent", "participant_ids": ["zinc_bromide"], "conditions": [field("warm_to", "r.t.", evidence), field("time", q(20, "min"), evidence)]},
            {"step_id": "cross_coupling", "participant_ids": [p["entity_id"] for p in parts], "conditions": [field("temperature", "r.t.", evidence), field("time", time, evidence)]},
        ],
        outcomes=[field("isolated_yield", q(yld, "%"), evidence, ["product"]), field("yield_measurement_basis", "isolated yield", evidence)],
        notes=notes,
        unresolved=["Supporting information was not explicitly supplied or associated.", "The full Typical procedure II continues beyond page 6; continuation details were not imported into this page-bounded extraction.", "Product structure remains machine-unverified."],
    ))

# Page 6: Eq. 2 reduction, remaining Table 7 scope rows, and Scheme 6 mechanism.
e6 = ev(6)
records.append(rec(
    "eq2_dibalh_reduction_E6ae", e6, "reported_experiment",
    participants=[
        substrate("(E)-6ae", e6, entity_id="allene_E_6ae"),
        standard_agent("dibalh", "diisobutylaluminum hydride", e6, amounts=[amount("equivalents", q(2.4, "equiv"), e6)]),
        standard_agent("toluene", "toluene", e6, role="solvent", smiles="Cc1ccccc1"),
        product("(E)-7", e6, entity_id="alcohol_E_7"),
    ],
    steps=[{"step_id": "reduction", "participant_ids": ["allene_E_6ae", "dibalh", "toluene", "alcohol_E_7"], "conditions": [field("temperature", q(-78, "°C"), e6), field("time", q(10, "min"), e6)]}],
    outcomes=[field("isolated_yield", q(82, "%"), e6, ["alcohol_E_7"])],
    notes=["Equation 2 is used with NOE information to support alkene configuration."],
    unresolved=["Starting amount, workup, purification, and full structures are not reported on page 6."],
))

table7 = {
    2: ("1a", "(E)-2h", "Me/Et", q(5, "min"), 78, "(E)-6ah"),
    3: ("1a", "(Z)-2c", "Ph/Me", q(16, "h"), 32, "(E)-6ac"),
    4: ("1a", "(Z)-2f", "nC4H9/Me", q(1, "h"), 80, "(E)-6af"),
    5: ("1a", "(Z)-2e", "Bn/Me", q(2, "h"), 74, "(E)-6ae"),
    6: ("1c", "(Z)-2d", "Me/Me", q(1, "h"), 72, "(E)-6cd"),
    7: ("1d", "(Z)-2d", "Me/Me", q(1, "h"), 86, "(E)-6dd"),
    8: ("1d", "(Z)-2g", "nC6H13/Me", q(2, "h"), 75, "(E)-6dg"),
    9: ("1h", "(Z)-2d", "Me/Me", q(1, "h"), 77, "(E)-6hd"),
}
table7_alkyne_alias = {"1a": "Ph/nC3H7", "1c": "Ph/Me", "1d": "p-PhC6H4/nC3H7", "1h": "p-C4H9C≡CC6H4/nC3H7"}
for entry, (alkyne, iodide, iodide_subs, time, yld, prod) in table7.items():
    high_loading = entry in (5, 8)
    iodide_scale = 0.20 if entry in (5, 8, 9) else 0.30
    parts = conditions_b_parts(e6, 3.75 if high_loading else 2.5, 15 if high_loading else 10, product_label=prod, iodide_label=iodide, alkyne_label=alkyne)
    parts[1]["amounts"] = [amount("amount", q(iodide_scale, "mmol"), e6)]
    notes = [f"Table substituent mapping: alkyne {alkyne}={table7_alkyne_alias[alkyne]}; iodide {iodide} has R2/R3={iodide_subs}."]
    basis = "isolated yield"
    if entry == 8:
        basis = "isolated pure product after flash chromatography on silica gel and preparative TLC"
    records.append(rec(
        f"table7_entry{entry}", e6, "substrate_scope_entry", participants=parts,
        steps=[
            {"step_id": "lithiation", "participant_ids": ["alkyne", "n_butyllithium"], "conditions": [field("temperature", q(-20, "°C"), e6), field("time", q(1, "h"), e6)]},
            {"step_id": "transmetalation_cold", "participant_ids": ["zinc_bromide"], "conditions": [field("temperature", q(-20, "°C"), e6), field("time", q(10, "min"), e6)]},
            {"step_id": "warm_zinc_reagent", "participant_ids": ["zinc_bromide"], "conditions": [field("warm_to", "r.t.", e6), field("time", q(20, "min"), e6)]},
            {"step_id": "cross_coupling", "participant_ids": [p["entity_id"] for p in parts], "conditions": [field("temperature", "r.t.", e6), field("time", time, e6)]},
        ],
        outcomes=[field("isolated_yield", q(yld, "%"), e6, ["product"]), field("yield_measurement_basis", basis, e6)],
        notes=notes,
        unresolved=["Supporting information was not explicitly supplied or associated.", "Full structures are not assigned from generic substituent columns; labels are preserved."],
    ))

records.append(rec(
    "scheme6_proposed_Z_E_isomerization_paths", e6, "mechanism",
    participants=[participant("organopalladium_H", "unspecified_agent", e6, label="organopalladium intermediate H"), participant("organopalladium_I", "unspecified_agent", e6, label="organopalladium intermediate I"), participant("complex_J", "unspecified_agent", e6, label="palladium complex J"), participant("complex_K", "unspecified_agent", e6, label="palladium complex K"), product("(Z)-5", e6, entity_id="Z_5"), product("(Z)-3 or (Z)-6", e6, entity_id="Z_allene"), product("(E)-3 or (E)-6", e6, entity_id="E_allene")],
    steps=[{"step_id": "proposed_paths_a_and_b", "participant_ids": ["organopalladium_H", "organopalladium_I", "complex_J", "complex_K", "Z_5", "Z_allene", "E_allene"], "conditions": []}],
    notes=["Scheme 6 presents two possible pathways for Z/E isomerization and is not an independent measured experiment."],
    unresolved=["The pathways and generic structures are mechanistic proposals; no isolated batch or yield is assigned."],
))

raw_path = BASE / "raw_model" / "records_pages_0001_0006.json"
raw_path.parent.mkdir(parents=True, exist_ok=True)
raw_path.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")

ids = [r["record_id"] for r in records]
by_prefix = lambda *prefixes: [rid for rid in ids if any(rid.split(":", 1)[1].startswith(p) for p in prefixes)]
coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1,
            "state": "attempted",
            "regions": [
                {"region": "lower-left Scheme 1", "finding": "Two generic complementary Negishi coupling modes were classified as general schemes; generic R groups and no batch outcomes prevent treating them as reported experiments.", "evidence_ids": ev(1)},
                {"region": "lower-right Scheme 2 and adjacent prose", "finding": "The aryl-iodide branch is explicitly cited prior work, while the iodoenoate branch is a generic overview of this work; both were kept separate from batch experiments.", "evidence_ids": ev(1)},
            ],
            "record_ids": by_prefix("scheme1_", "scheme2_"),
            "unresolved": ["Generic structures A/A'/B/B' and R groups were not converted into fully specified molecules."]
        },
        {
            "page": 2,
            "state": "attempted",
            "regions": [
                {"region": "lower-left Equation 1 and reassignment prose", "finding": "The cited HgCl2/nBuLi/ZnBr2/Pd(PPh3)4 protocol was retained as a literature example with the paper's corrected E-regioisomer assignment, not as a new optimization row.", "evidence_ids": ev(2)},
                {"region": "upper-right Table 1 and footnotes", "finding": "All eight ligand/temperature optimization rows were extracted independently, including dash yields for impurity-contaminated entries 2–3 and LDA/ligand footnote overrides.", "evidence_ids": ev(2)},
                {"region": "middle-right Figure 1", "finding": "NOE drawings support assignments of (Z)-4aa and (E)-3ac; they are characterization evidence rather than independent reaction batches.", "evidence_ids": ev(2)},
            ],
            "record_ids": by_prefix("eq1_", "table1_"),
            "unresolved": ["Table 1 entries 2–3 do not report numerical combined yields because of an unidentified impurity."]
        },
        {
            "page": 3,
            "state": "attempted",
            "regions": [
                {"region": "left-column Table 2 and footnotes", "finding": "Five Conditions A scope rows were extracted separately with combined yields and post-chromatography product ratios; entry 1 is linked to its detailed page-6 procedure.", "evidence_ids": ev(3)},
                {"region": "upper-right Scheme 3 table and discussion", "finding": "Six temperature/loading isomerization controls were extracted separately with initial ratios, NMR yields, and final ratios.", "evidence_ids": ev(3)},
            ],
            "record_ids": by_prefix("table2_", "scheme3_"),
            "unresolved": ["Scheme 3 does not state exact LDA or ZnBr2 quantities."]
        },
        {
            "page": 4,
            "state": "attempted",
            "regions": [
                {"region": "top Scheme 4", "finding": "The C/D deprotonated-species interconversion was classified as a proposed mechanism, not a batch experiment.", "evidence_ids": ev(4)},
                {"region": "middle-left Table 3 and footnotes", "finding": "All eight 3-substituted iodoenoate scope rows were extracted; entry 1 scale/catalyst overrides and its yield based on 64% conversion were preserved.", "evidence_ids": ev(4)},
                {"region": "middle-right Table 4 and footnotes", "finding": "All seven nBuLi parameter-screen rows were extracted independently with T1/t1 and T2/t2; entry 5 retains the conflicting catalyst statements from footnotes c and d.", "evidence_ids": ev(4)},
            ],
            "record_ids": by_prefix("scheme4_", "table3_", "table4_"),
            "unresolved": ["Table 4 entry 5 footnotes conflict on Pd(PPh3)2Cl2 versus Pd(PPh3)4 catalyst identity."]
        },
        {
            "page": 5,
            "state": "attempted",
            "regions": [
                {"region": "upper-left Table 5 and footnotes", "finding": "Three ligand-screen rows were extracted, preserving the conversion-based entry-1 yield, the explicitly inaccurate entry-2 ratio, and missing entry-3 yield due to product instability.", "evidence_ids": ev(5)},
                {"region": "lower-left Scheme 5", "finding": "The F/G ligand-effect diagram was classified as a proposed mechanism, not an experiment.", "evidence_ids": ev(5)},
                {"region": "upper-right Table 6 and footnotes", "finding": "Four catalyst-efficiency rows were extracted; entry 2 is merged with duplicate Table 7 entry 1 and page-6 Typical procedure II.", "evidence_ids": ev(5)},
            ],
            "record_ids": by_prefix("table5_", "scheme5_", "table6_"),
            "unresolved": ["Table 5 entry 3 has no numerical yield; Table 5 entry 2 states that its product ratio is inaccurate."]
        },
        {
            "page": 6,
            "state": "attempted",
            "regions": [
                {"region": "upper-left Equation 2", "finding": "The DIBALH reduction of (E)-6ae to alcohol (E)-7 was extracted as a separate reported experiment with 2.4 equiv, -78 °C, 10 min, and 82% yield.", "evidence_ids": ev(6)},
                {"region": "left-column Table 7 and footnotes", "finding": "All nine scope rows were accounted for; entry 1 was deduplicated against Table 6 entry 2, while entries 2–9 remain independent scope records with loading/scale footnotes.", "evidence_ids": ev(6)},
                {"region": "right-column Typical procedure I", "finding": "Detailed quantities, workup, purification, 56 mg combined product, 77% yield, and 98:2 ratio were merged into Table 2 entry 1.", "evidence_ids": ev(6)},
                {"region": "lower-right beginning of Typical procedure II", "finding": "Only details visible on page 6 were merged with Table 6 entry 2/Table 7 entry 1; the continuation beyond page 6 was not imported.", "evidence_ids": ev(6)},
                {"region": "lower-left Scheme 6", "finding": "Possible paths a and b for Z/E isomerization were classified as a mechanism rather than measured experiments.", "evidence_ids": ev(6)},
            ],
            "record_ids": by_prefix("eq2_", "table7_", "table2_entry1", "table6_entry2_", "scheme6_"),
            "unresolved": ["Typical procedure II continues beyond page 6; continuation details were deliberately excluded from the page-bounded extraction."]
        },
    ],
}
coverage_path = BASE / "coverage" / "pages_0001_0006.json"
coverage_path.parent.mkdir(parents=True, exist_ok=True)
coverage_path.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"records": len(records), "raw": str(raw_path), "coverage": str(coverage_path)}, ensure_ascii=False))
