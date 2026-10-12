#!/usr/bin/env python3
"""Build raw, evidence-linked machine records for source PDF pages 1-4."""
import json
from pathlib import Path

DOC = "doc_f3d88ca565868eb2"
T = {n: f"{DOC}:page{n}:text" for n in range(1, 5)}
I = {n: f"{DOC}:page{n}:image" for n in range(1, 5)}


def fact(value, evidence):
    return {
        "value": value,
        "evidence_ids": [] if value is None else list(evidence),
        "verification": "missing" if value is None else "unreviewed",
    }


def q(number, unit, **extra):
    value = {"number": number, "unit": unit}
    value.update(extra)
    return value


def field(name, value, evidence, targets=None):
    item = {"name": name, "fact": fact(value, evidence)}
    if targets:
        item["target_entity_ids"] = list(targets)
    return item


def participant(entity_id, role, label, evidence, name=None, smiles=None, amounts=None):
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


def record(source_id, kind, evidence, participants, steps, outcomes, notes=None, unresolved=None):
    return {
        "record_id": f"{DOC}:{source_id}",
        "document_id": DOC,
        "source_reaction_id": source_id,
        "record_kind": kind,
        "status": "needs_review",
        "completeness": "partial",
        "evidence_ids": list(dict.fromkeys(evidence)),
        "participants": participants,
        "steps": steps,
        "outcomes": outcomes,
        "notes": [fact(x, evidence) for x in (notes or [])],
        "review": {
            "method": "model",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved or [],
        },
    }


def step(step_id, participant_ids, conditions):
    return {"step_id": step_id, "participant_ids": participant_ids, "conditions": conditions}


SMILES = {
    "2": "COC(=O)C#C",
    "1a": "CCCC(=C=Cc1ccccc1)C(=O)O",
    "1b": "CCCC(=C=Cc1ccc(Br)cc1)C(=O)O",
    "1c": "CCCC(=C=Cc1cccc2ccccc12)C(=O)O",
    "1d": "CCCCC(=C=Cc1ccccc1)C(=O)O",
    "1e": "CCCCC(=C=Cc1ccc(Br)cc1)C(=O)O",
    "1f": "CCCCC(=C=Cc1ccc(Cl)cc1)C(=O)O",
    "1g": "CCCCC(=C=CC)C(=O)O",
    "1h": "CCCCCC(=C=Cc1ccccc1)C(=O)O",
    "1i": "CC(=C=Cc1ccccc1)C(=O)O",
    "1j": "CCC(=C=Cc1ccccc1)C(=O)O",
    "1k": "CC(C)CC(=C=Cc1ccccc1)C(=O)O",
    "Pd(OAc)2": "CC(=O)[O-].CC(=O)[O-].[Pd+2]",
    "PdCl2": "[Cl-].[Cl-].[Pd+2]",
    "CCl3Me": "CC(Cl)(Cl)Cl",
    "CH2Br2": "BrCBr",
}


def base_substrate(label, ev, amounts=None):
    return participant(label, "reactant", label, ev, "2,3-allenoic acid " + label, SMILES.get(label), amounts)


def propiolate(ev, amounts=None):
    return participant("2", "reactant", "2", ev, "methyl propiolate", SMILES["2"], amounts)


def catalyst(label, ev, loading=5):
    return participant(
        label.replace("(", "_").replace(")", "").replace("/", "_"),
        "catalyst",
        label,
        ev,
        label,
        SMILES.get(label),
        [field("catalyst_loading", q(loading, "mol%"), ev)] if loading is not None else [],
    )


def solvent(label, ev, smiles=None, amounts=None):
    return participant(label.replace("/", "_"), "solvent", label, ev, label, smiles, amounts)


def product(label, ev, name=None):
    return participant(label, "product", label, ev, name, None, [])


records = []

# Table 1: every optimization row is independent. The displayed dash is preserved
# literally instead of being silently converted to zero or "not detected".
table1 = [
    (1, 1.0, None, None, 12, [40, 10, None, None]),
    (2, 1.0, "BF3·Et2O", (100, "mol%"), 12, [28, 40, 15, None]),
    (3, 1.0, "BF3·Et2O", (10, "mol%"), 24, [43, 27, 6, None]),
    (4, 8.0, "BF3·Et2O", (100, "mol%"), 14, [20, 22, 28, 3]),
    (5, 1.0, "BF3·Et2O", (100, "mol%"), 12, [8, 6, 2, None]),
    (6, 3.0, "Sc(OTf)3", (100, "mol%"), 18, [51, 3, 37, 5]),
    (7, 3.0, "Sc(OTf)3", (10, "mol%"), 12, [28, 35, 20, None]),
]
ev1 = [T[1], I[1]]
for entry, eq2, additive, loading, hours, yields in table1:
    parts = [
        base_substrate("1a", ev1),
        propiolate(ev1, [field("equivalents", q(eq2, "equiv"), ev1)]),
        catalyst("PdCl2" if entry == 5 else "Pd(OAc)2", ev1),
        solvent("CCl3Me", ev1, SMILES["CCl3Me"]),
    ]
    if additive:
        amount = field("additive_loading", q(loading[0], loading[1]), ev1)
        parts.append(participant(additive, "reagent", additive, ev1, additive, None, [amount]))
    for lab in ("3a", "4a", "5a", "7a"):
        parts.append(product(lab, ev1))
    conditions = [
        field("temperature", q(35, "°C") if entry == 1 else {"minimum": 35, "maximum": 40, "unit": "°C", "raw_text": "35–40 °C"}, ev1),
        field("time", q(hours, "h"), ev1),
    ]
    outcomes = []
    for lab, value in zip(("3a", "4a", "5a", "7a"), yields):
        reported = q(value, "%") if value is not None else "table dash (–)"
        outcomes.append(field(f"reported_yield_{lab}", reported, ev1, [lab]))
    outcomes.append(field("yield_measurement_basis", "1H NMR with CH2Br2 internal standard", ev1, ["3a", "4a", "5a", "7a"]))
    if entry in (1, 5):
        recovery = 14 if entry == 1 else 67
        outcomes.append(field("recovered_starting_material_yield", q(recovery, "%"), ev1, ["1a"]))
    records.append(record(
        f"table1_entry{entry}", "optimization_entry", ev1, parts,
        [step("coupling_cyclization", [p["entity_id"] for p in parts if p["role"] != "product"], conditions)],
        outcomes,
        notes=["Table 1 optimization row; product structures are visually legible but candidate product SMILES were withheld because the conjugated lactone connectivity/stereochemistry was not independently resolved from the raster."],
        unresolved=["Supporting Information was not supplied or associated.", "Atmosphere, individual charge amounts, workup, and isolation details are not reported for this optimization row.", "A table dash is preserved literally and is not interpreted as zero yield."],
    ))

# Table 1 entry 8 = Table 2 entry 1 = the detailed typical experiment. Evidence is
# merged rather than counting these three presentations as separate experiments.
ev_opt = [T[1], I[1], T[2], I[2], T[3], I[3], T[4], I[4]]
parts = [
    base_substrate("1a", ev_opt, [field("mass", q(50, "mg"), [T[3], I[3]]), field("amount", q(0.248, "mmol"), [T[3], I[3]])]),
    propiolate(ev_opt, [
        field("feed_solution_mass", q(42, "mg"), [T[3], I[3]]),
        field("feed_solution_amount", q(0.50, "mmol"), [T[3], I[3]]),
        field("receiving_flask_mass", q(63, "mg"), [T[3], I[3]]),
        field("receiving_flask_amount", q(0.75, "mmol"), [T[3], I[3]]),
        field("total_equivalents", q(5.0, "equiv"), [T[1], I[1], T[2], I[2]]),
    ]),
    participant("Sc(OTf)3", "reagent", "Sc(OTf)3", ev_opt, "scandium triflate", None, [
        field("mass", q(37, "mg"), [T[3], I[3]]), field("amount", q(0.075, "mmol"), [T[3], I[3]]), field("additive_loading", q(30, "mol%"), [T[1], I[1], T[2], I[2]])]),
    participant("BF3_Et2O", "reagent", "BF3·Et2O", ev_opt, "boron trifluoride diethyl etherate", None, [
        field("volume", q(124, "uL"), [T[3], I[3]]), field("amount", q(1.00, "mmol"), [T[3], I[3]]), field("equivalents", q(4.0, "equiv"), [T[1], I[1], T[2], I[2], T[3], I[3]])]),
    participant("Pd_OAc_2", "catalyst", "Pd(OAc)2", ev_opt, "palladium(II) acetate", SMILES["Pd(OAc)2"], [
        field("mass", q(3, "mg"), [T[3], I[3]]), field("amount", q(0.0134, "mmol"), [T[3], I[3]]), field("catalyst_loading", q(5, "mol%"), [T[1], I[1], T[2], I[2]])]),
    solvent("CCl3Me", ev_opt, SMILES["CCl3Me"], [field("feed_solution_volume", q(1.2, "mL"), [T[3], I[3]]), field("receiving_flask_volume", q(1.0, "mL"), [T[3], I[3]]), field("total_volume", q(2.2, "mL"), [T[2], I[2]])]),
    participant("CH2Br2", "reagent", "CH2Br2", ev_opt, "dibromomethane internal standard", SMILES["CH2Br2"], [field("volume", q(9, "uL"), [T[3], I[3]]), field("amount", q(0.129, "mmol"), [T[3], I[3]])]),
    product("3a", ev_opt), product("4a", ev_opt), product("5a", ev_opt), product("7a", ev_opt),
]
steps = [
    step("syringe_pump_addition", ["1a", "2", "CCl3Me", "Sc(OTf)3", "BF3_Et2O", "Pd_OAc_2"], [
        field("temperature", q(40, "°C"), [T[3], I[3]]),
        field("operation", "solution of 1a and part of 2 added by syringe pump at 0.06 mL h−1 to the receiving mixture", [T[3], I[3]]),
    ]),
    step("post_addition_stirring", ["1a", "2", "CCl3Me", "Sc(OTf)3", "BF3_Et2O", "Pd_OAc_2"], [field("temperature", q(40, "°C"), [T[3], I[3]]), field("time", q(13, "h"), [T[3], I[3]])]),
    step("workup_and_analysis", ["CH2Br2"], [field("workup", "filtered through a short silica-gel column and evaporated; analyzed by 1H NMR", [T[3], I[3]])]),
    step("purification", ["4a", "5a"], [field("purification", "flash chromatography on silica gel; petroleum ether/ethyl acetate 10:1", [T[3], I[3]])]),
]
outcomes = [
    field("nmr_yield_3a", q(14, "%"), [T[1], I[1]], ["3a"]),
    field("nmr_yield_4a", q(4, "%"), [T[1], I[1]], ["4a"]),
    field("nmr_yield_5a", q(71, "%"), [T[1], I[1], T[2], I[2], T[3], I[3]], ["5a"]),
    field("reported_yield_7a", "table dash (–)", [T[1], I[1]], ["7a"]),
    field("isolated_yield_5a", q(54, "%"), [T[2], I[2], T[3], I[3]], ["5a"]),
    field("isolated_mass_5a", q(49, "mg"), [T[3], I[3]], ["5a"]),
    field("product_ratio_4a_to_5a", "1:16", [T[2], I[2], T[3], I[3]], ["4a", "5a"]),
    field("yield_measurement_basis", "1H NMR with CH2Br2 internal standard; isolated yield shown separately", [T[1], I[1], T[2], I[2], T[3], I[3]], ["3a", "4a", "5a", "7a"]),
    field("melting_point_4a", {"minimum": 97, "maximum": 99, "unit": "°C", "raw_text": "97–99 °C"}, [T[3], I[3]], ["4a"]),
]
records.append(record(
    "optimized_1a_table1e8_table2e1_typical", "optimization_entry", ev_opt, parts, steps, outcomes,
    notes=[
        "Table 1 entry 8, Table 2 entry 1, the surrounding prose, and the typical experimental procedure report the same 1a/2 optimized experiment and were deduplicated.",
        "Page 4 continues characterization: 4a has formula C17H18O4 by elemental analysis; 5a is an oil with HRMS [M+Na]+ calculated 393.1309 and found 393.1312.",
        "The detailed procedure says complete consumption was determined by TLC and states that 4a was obtained as a solid without an isolated mass or isolated yield.",
    ],
    unresolved=[
        "Supporting Information is mentioned but was not supplied or associated.",
        "Table 1 gives t = 12 h, Table 2 gives 35 °C, and the detailed procedure gives a syringe-pump addition followed by 13 h at 40 °C; the source presentations are not silently reconciled.",
        "The 0.06 mL h−1 addition rate is preserved as operation text because the schema's supported quantity units do not include compound rate units.",
        "Atmosphere is not reported.",
        "Candidate product SMILES are withheld because the conjugated lactone connectivity/stereochemistry was not independently resolved from the raster; labels and image evidence are retained.",
    ],
))

# Table 2 scope rows 2-8; row 1 is already merged above.
scope = [
    (2, "1b", "4b", "5b", "1:11", 75, 53, 5.0),
    (3, "1c", "4c", "5c", "1:9", 52, 45, 5.0),
    (4, "1d", "4d", "5d", "1:10", 65, 47, 5.0),
    (5, "1e", "4e", "5e", "1:12", 71, 51, 5.0),
    (6, "1f", "4f", "5f", "1:14", 70, 60, 5.0),
    (7, "1g", "4g", "5g", "1:9", 58, 44, 7.0),
    (8, "1h", "4h", "5h", "1:11", 64, None, 5.0),
]
ev2 = [T[2], I[2]]
for entry, sub, p4, p5, ratio, nmr_yield, iso_yield, eq2 in scope:
    parts = [
        base_substrate(sub, ev2, [field("reaction_scale", q(0.25, "mmol"), ev2)]),
        propiolate(ev2, [field("equivalents", q(eq2, "equiv"), ev2)]),
        catalyst("Pd(OAc)2", ev2, 5),
        participant("Sc(OTf)3", "reagent", "Sc(OTf)3", ev2, "scandium triflate", None, [field("additive_loading", q(30, "mol%"), ev2)]),
        participant("BF3_Et2O", "reagent", "BF3·Et2O", ev2, "boron trifluoride diethyl etherate", None, [field("equivalents", q(4.0, "equiv"), ev2)]),
        solvent("CCl3Me", ev2, SMILES["CCl3Me"], [field("volume", q(2.2, "mL"), ev2)]),
        product(p4, ev2), product(p5, ev2),
    ]
    if entry == 3:
        parts.append(product("7c", ev2))
    outcomes = [
        field(f"nmr_yield_{p5}", q(nmr_yield, "%"), ev2, [p5]),
        field(f"isolated_yield_{p5}", q(iso_yield, "%") if iso_yield is not None else None, ev2, [p5]),
        field(f"product_ratio_{p4}_to_{p5}", ratio, ev2, [p4, p5]),
        field("yield_measurement_basis", "1H NMR with CH2Br2 internal standard; parenthesized value is isolated yield", ev2, [p5]),
    ]
    if entry == 3:
        outcomes.append(field("approximate_nmr_yield_7c", q(9, "%", qualifier="approx", raw_text="approximately 9%"), ev2, ["7c"]))
    records.append(record(
        f"table2_entry{entry}_{sub}", "substrate_scope_entry", ev2, parts,
        [step("coupling_cyclization", [p["entity_id"] for p in parts if p["role"] != "product"], [field("temperature", q(35, "°C"), ev2), field("time", None, ev2)])],
        outcomes,
        notes=["Table 2 substrate-scope row; the two noncyclic C=C bonds of products 5 are reported as exclusively E."],
        unresolved=["Supporting Information was not supplied or associated.", "Reaction time, atmosphere, workup, and row-specific procedure are not printed in Table 2.", "Candidate product SMILES are withheld pending independent resolution of conjugated lactone connectivity and alkene stereochemistry."],
    ))

# Scheme 1: two distinct substrate experiments.
for sub, p4, p6, y4, y6, iy6 in [("1i", "4i", "6i", 4, 50, 49), ("1j", "4j", "6j", 3, 51, 40)]:
    parts = [base_substrate(sub, ev2), propiolate(ev2), catalyst("Pd(OAc)2", ev2, 5),
             participant("Sc(OTf)3", "reagent", "Sc(OTf)3", ev2, "scandium triflate"),
             participant("BF3_Et2O", "reagent", "BF3·Et2O", ev2, "boron trifluoride diethyl etherate"),
             solvent("CCl3Me", ev2, SMILES["CCl3Me"]), product(p4, ev2), product(p6, ev2)]
    outcomes = [field(f"nmr_yield_{p4}", q(y4, "%"), ev2, [p4]), field(f"nmr_yield_{p6}", q(y6, "%"), ev2, [p6]),
                field(f"isolated_yield_{p6}", q(iy6, "%"), ev2, [p6]), field("yield_measurement_basis", "1H NMR with CH2Br2 internal standard; isolated yield shown in parentheses", ev2, [p4, p6])]
    if sub == "1j":
        parts.append(product("5j", ev2, "pi-bond-migration adduct from 1j"))
        outcomes.append(field("yield_5j", q(5, "%", qualifier="lt", raw_text="less than 5%"), ev2, ["5j"]))
    records.append(record(
        f"scheme1_{sub}", "reported_experiment", ev2, parts,
        [step("coupling_cyclization", [p["entity_id"] for p in parts if p["role"] != "product"], [field("temperature", q(35, "°C"), ev2), field("time", None, ev2)])], outcomes,
        unresolved=["Exact methyl propiolate equivalents, additive loadings, reaction time, atmosphere, and workup are not printed in Scheme 1.", "Supporting Information was not supplied or associated.", "Candidate product SMILES are withheld pending source-structure review."],
    ))

# Low-temperature interception experiment reported in prose.
parts = [base_substrate("1a", ev2), propiolate(ev2), product("5a", ev2), product("6a", ev2)]
records.append(record(
    "low_temperature_5a_6a_mixture", "reported_experiment", ev2, parts,
    [step("low_temperature_reaction", ["1a", "2"], [field("temperature", q(12, "°C"), ev2), field("time", q(5, "h"), ev2)])],
    [field("isolated_mixture_ratio_5a_to_6a", "1:1.27", ev2, ["5a", "6a"])],
    notes=["Pure 6a was not obtained; a mixture of 5a and 6a was isolated."],
    unresolved=["The prose does not restate exact catalyst/additive amounts, solvent volume, yields, atmosphere, or workup for this 12 °C experiment.", "Supporting Information was not supplied or associated."],
))

# Subsequent catalyst-free conversion monitored by NMR; distinct from formation.
ev_conv = [T[2], I[2], T[3], I[3]]
parts = [participant("6a", "reactant", "6a", ev_conv), product("5a", ev_conv), solvent("CDCl3", ev_conv, "[2H]C(Cl)(Cl)Cl")]
records.append(record(
    "figure1_6a_to_5a_timecourse", "reported_experiment", ev_conv, parts,
    [step("solution_conversion", ["6a", "CDCl3"], [field("temperature", q(25, "°C"), ev_conv), field("time", q(27, "h"), [T[3], I[3]]), field("metal_catalyst", "absent", [T[2], I[2]])])],
    [field("ratio_6a_to_5a_immediately_after_isolation", "1.27:1.00", [I[3]], ["6a", "5a"]), field("ratio_6a_to_5a_after_6h", "0.25:1.00", [I[3]], ["6a", "5a"]), field("ratio_6a_to_5a_after_27h", "0.02:1.00", [I[3]], ["6a", "5a"]), field("measurement_basis", "1H NMR (300 MHz) in CDCl3", [T[3], I[3]], ["6a", "5a"])],
    notes=["The source states that complete conversion could not be achieved even at higher temperature or longer time, without printing those additional conditions."],
    unresolved=["Starting concentration and isolation details for the monitored mixture are not reported in the main text.", "Supporting Information was not supplied or associated."],
))

# Scheme 2, acid-source deuterium experiment.
ev_d = [T[2], I[2], T[3], I[3]]
parts = [participant("D1_1a", "reactant", "[D1]1a", ev_d), propiolate(ev_d, [field("equivalents", q(3, "equiv"), [I[3]])]),
         catalyst("Pd(OAc)2", ev_d, None), participant("BF3_Et2O", "reagent", "BF3·Et2O", ev_d, "boron trifluoride diethyl etherate"),
         solvent("CCl3Me", ev_d, SMILES["CCl3Me"]), solvent("CD3CO2D", ev_d), product("D1_4a", ev_d, "[D1]4a"), product("D1_5a", ev_d, "[D1]5a")]
records.append(record(
    "scheme2_D1_labeling", "reported_experiment", ev_d, parts,
    [step("deuterium_labeling_coupling", [p["entity_id"] for p in parts if p["role"] != "product"], [field("solvent_ratio", "CCl3Me/CD3CO2D = 10:1", [I[3]]), field("temperature", q(35, "°C"), [I[3]]), field("time", q(18.5, "h"), [I[3]])])],
    [field("yield_D1_4a", q(23, "%"), [I[3]], ["D1_4a"]), field("deuterium_incorporation_D1_4a", q(72, "%", qualifier="approx", raw_text="~72% D"), [T[2], I[2], I[3]], ["D1_4a"]), field("yield_D1_5a", q(18, "%"), [I[3]], ["D1_5a"]), field("deuterium_incorporation_D1_5a", q(68, "%", qualifier="approx", raw_text="~68% D"), [T[2], I[2], I[3]], ["D1_5a"]), field("yield_measurement_basis", None, [], ["D1_4a", "D1_5a"])],
    notes=["The deuterium atom in [D1]5a is assigned by the authors to the depicted 4′ position."],
    unresolved=["Catalyst and BF3·Et2O quantities, atmosphere, workup, yield basis, and isolation status are not printed in Scheme 2.", "Isotopologue SMILES are withheld because the exact atom mapping was not independently verified.", "Supporting Information was not supplied or associated."],
))

# Scheme 3, intramolecular deuterium-transfer experiment.
parts = [participant("D2_1a", "reactant", "[D2]1a", ev_d), propiolate(ev_d, [field("equivalents", q(4, "equiv"), [I[3]])]),
         catalyst("Pd(OAc)2", ev_d, None), participant("BF3_Et2O", "reagent", "BF3·Et2O", ev_d, "boron trifluoride diethyl etherate"),
         solvent("CCl3Me", ev_d, SMILES["CCl3Me"]), product("D2_4a", ev_d, "[D2]4a"), product("D2_5a", ev_d, "[D2]5a")]
records.append(record(
    "scheme3_D2_labeling", "reported_experiment", ev_d, parts,
    [step("deuterium_transfer_coupling", [p["entity_id"] for p in parts if p["role"] != "product"], [field("temperature", q(40, "°C"), [I[3]]), field("time", q(26, "h"), [I[3]])])],
    [field("yield_D2_4a", q(26, "%"), [I[3]], ["D2_4a"]), field("deuterium_incorporation_D2_4a", q(95, "%", qualifier="gt", raw_text=">95% D"), [I[3]], ["D2_4a"]), field("yield_D2_5a", q(27, "%"), [I[3]], ["D2_5a"]), field("deuterium_incorporation_D2_5a_depicted_3_prime_site", q(95, "%", qualifier="gt", raw_text=">95% D"), [T[2], I[2], I[3]], ["D2_5a"]), field("deuterium_incorporation_D2_5a_depicted_terminal_site", q(92, "%", qualifier="gt", raw_text=">92% D"), [I[3]], ["D2_5a"]), field("yield_measurement_basis", None, [], ["D2_4a", "D2_5a"])],
    notes=["The starting [D2]1a is printed as >95% D. The authors state that one deuterium atom is completely transferred to the 3′ position in [D2]5a."],
    unresolved=["Catalyst and BF3·Et2O quantities, atmosphere, workup, yield basis, and isolation status are not printed in Scheme 3.", "Isotopologue SMILES are withheld because the exact atom mapping was not independently verified.", "Supporting Information was not supplied or associated."],
))

# Scheme 4, branched-substituent experiment.
ev3 = [T[2], I[2], T[3], I[3]]
parts = [base_substrate("1k", ev3), propiolate(ev3, [field("equivalents", q(6.0, "equiv"), [I[3]])]), catalyst("Pd(OAc)2", ev3, None),
         participant("Sc(OTf)3", "reagent", "Sc(OTf)3", ev3, "scandium triflate"), participant("BF3_Et2O", "reagent", "BF3·Et2O", ev3, "boron trifluoride diethyl etherate"),
         solvent("CCl3Me", ev3, SMILES["CCl3Me"]), product("4k", ev3), product("5k", ev3), product("6k", ev3)]
records.append(record(
    "scheme4_1k", "reported_experiment", ev3, parts,
    [step("coupling_cyclization", [p["entity_id"] for p in parts if p["role"] != "product"], [field("temperature", q(35, "°C"), [T[2], I[2], I[3]]), field("time", q(69, "h"), [T[2], I[2], I[3]])])],
    [field("nmr_yield_4k", q(3, "%"), [I[3]], ["4k"]), field("nmr_yield_5k", q(72, "%"), [I[3]], ["5k"]), field("nmr_yield_6k", q(8, "%"), [T[2], I[2], I[3]], ["6k"]), field("yield_measurement_basis", "1H NMR with CH2Br2 internal standard", [I[3]], ["4k", "5k", "6k"])],
    unresolved=["Catalyst and additive quantities, atmosphere, workup, and isolation status are not printed in Scheme 4.", "Supporting Information was not supplied or associated.", "Candidate product SMILES are withheld pending source-structure review."],
))

# Scheme 5 is retained as a mechanism record, never as a reported experiment.
mechanism_parts = [participant(x, "unspecified_agent", x, ev3) for x in ("D2_1a", "2", "8", "9", "10", "D2_6a", "11", "D2_5a", "D2_4a", "PdX2", "HX")]
records.append(record(
    "scheme5_plausible_mechanism", "mechanism", ev3, mechanism_parts,
    [
        step("cyclic_oxypalladation", ["D2_1a", "PdX2", "8"], [field("operation", "proposed cyclic oxypalladation to intermediate 8", ev3)]),
        step("first_cis_carbopalladation", ["8", "2", "9"], [field("operation", "proposed stereoselective cis carbopalladation", ev3)]),
        step("second_cis_carbopalladation_and_protonolysis", ["9", "2", "10", "HX", "D2_6a"], [field("operation", "proposed second cis carbopalladation followed by protonolysis", ev3)]),
        step("double_1_7_hydrogen_migration", ["D2_6a", "11", "D2_5a"], [field("operation", "proposed two thermal antarafacial 1,7-hydrogen migrations", ev3)]),
    ],
    [],
    notes=["The authors explicitly call Scheme 5 a plausible catalytic cycle; intermediates 8-11 are proposed, not isolated experiments."],
    unresolved=["Mechanistic intermediates and atom mapping are proposals and were not independently verified.", "No experimental yield is assigned to this mechanism record."],
))

out = Path(__file__).with_name("pages_0001_0004_records.json")
out.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
print(f"wrote {len(records)} records to {out}")
