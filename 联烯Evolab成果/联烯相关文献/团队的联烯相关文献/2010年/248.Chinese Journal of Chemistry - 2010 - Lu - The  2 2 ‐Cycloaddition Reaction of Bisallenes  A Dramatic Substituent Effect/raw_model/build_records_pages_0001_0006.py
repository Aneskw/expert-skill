#!/usr/bin/env python3
"""Build machine-extracted records for Lu and Ma, CJC 2010, PDF pages 1--6."""
from pathlib import Path
import json

DOC = "doc_647889476b7acf1a"
OUT = Path(__file__).with_name("records_pages_0001_0006.json")


def ev(page, kind="image"):
    return f"{DOC}:page{page}:{kind}"


def fact(value, evidence):
    return {
        "value": value,
        "evidence_ids": list(evidence),
        "verification": "missing" if value is None else "unreviewed",
    }


def field(name, value, evidence, targets=None):
    item = {"name": name, "fact": fact(value, evidence)}
    if targets:
        item["target_entity_ids"] = list(targets)
    return item


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


def amount(name, number, unit, evidence, **extra):
    value = {"number": number, "unit": unit}
    value.update(extra)
    return field(name, value, evidence)


def base_record(rid, kind, evidence, participants, steps, outcomes, notes, unresolved):
    return {
        "record_id": f"{DOC}:{rid}",
        "document_id": DOC,
        "source_reaction_id": rid,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": list(dict.fromkeys(evidence)),
        "participants": participants,
        "steps": steps,
        "outcomes": outcomes,
        "notes": [fact(note, evidence) for note in notes],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": list(unresolved),
        },
    }


def reaction_record(
    rid,
    kind,
    pages,
    reactant_label,
    products,
    substrate_mass=None,
    substrate_amount=None,
    solvent="toluene",
    solvent_volume=None,
    time=None,
    temperature="reflux",
    concentration=None,
    product_mass=None,
    product_mass_targets=None,
    product_yield=None,
    yield_targets=None,
    ratio=None,
    ratio_targets=None,
    recovered_mass=None,
    recovery=None,
    additional_outcomes=None,
    catalyst=None,
    catalyst_loading=None,
    atmosphere=None,
    operations=None,
    notes=None,
    unresolved=None,
):
    evidence = []
    for page in pages:
        evidence.extend([ev(page, "image"), ev(page, "text")])
    primary = [ev(pages[-1], "image"), ev(pages[-1], "text")]
    reactant_id = f"{rid}_reactant_{reactant_label}"
    reactant_amounts = []
    if substrate_mass:
        reactant_amounts.append(amount("mass", substrate_mass, "mg", primary))
    if substrate_amount:
        reactant_amounts.append(amount("amount", substrate_amount, "mmol", primary))
    participants = [participant(reactant_id, "reactant", evidence, label=reactant_label, amounts=reactant_amounts)]
    product_ids = []
    for label, name in products:
        product_id = f"{rid}_product_{label.replace("'", "prime")}"
        product_ids.append(product_id)
        participants.append(participant(product_id, "product", evidence, label=label, name=name))
    step_participants = [reactant_id] + product_ids
    solvent_id = None
    if solvent:
        solvent_id = f"{rid}_solvent"
        solvent_smiles = "Cc1ccccc1" if solvent == "toluene" else ("CC#N" if solvent == "acetonitrile" else None)
        solvent_amounts = [amount("volume", solvent_volume, "mL", primary)] if solvent_volume else []
        participants.append(participant(solvent_id, "solvent", evidence, name=solvent, smiles=solvent_smiles, amounts=solvent_amounts))
        step_participants.append(solvent_id)
    if catalyst:
        catalyst_id = f"{rid}_catalyst"
        catalyst_amounts = [amount("catalyst_loading", catalyst_loading, "mol%", evidence)] if catalyst_loading else []
        participants.append(participant(catalyst_id, "catalyst", evidence, name=catalyst, amounts=catalyst_amounts))
        step_participants.append(catalyst_id)
    conditions = []
    if solvent:
        conditions.append(field("solvent", solvent, evidence))
    if temperature is not None:
        conditions.append(field("temperature", temperature, evidence))
    if time is not None:
        unit = "d" if isinstance(time, tuple) and time[1] == "d" else "h"
        number = time[0] if isinstance(time, tuple) else time
        conditions.append(field("reaction_time", {"number": number, "unit": unit}, evidence))
    if concentration is not None:
        conditions.append(field("reaction_concentration", {"number": concentration, "unit": "M"}, evidence))
    if atmosphere is not None:
        conditions.append(field("atmosphere", atmosphere, evidence))
    for operation in operations or []:
        conditions.append(field("operation", operation, evidence))
    steps = [{"step_id": "reaction", "participant_ids": step_participants, "conditions": conditions}]
    outcomes = []
    if product_mass is not None:
        targets = product_mass_targets or yield_targets or product_ids
        outcomes.append(field("isolated_product_mass", {"number": product_mass, "unit": "mg"}, primary, targets))
    if product_yield is not None:
        targets = yield_targets or product_ids
        outcomes.append(field("reported_yield", {"number": product_yield, "unit": "%"}, evidence, targets))
    if ratio is not None:
        outcomes.append(field("regioisomer_ratio", ratio, evidence, ratio_targets or product_ids))
    if recovered_mass is not None:
        outcomes.append(field("residual_starting_material_mass", {"number": recovered_mass, "unit": "mg"}, primary, [reactant_id]))
    if recovery is not None:
        outcomes.append(field("recovered_starting_material_yield", {"number": recovery, "unit": "%"}, evidence, [reactant_id]))
    outcomes.extend(additional_outcomes or [])
    missing = [
        "Core substrate/product SMILES were not assigned from the complex 2D drawings and remain unverified.",
        "No supporting-information file was explicitly associated with this paper.",
    ]
    if atmosphere is None:
        missing.append("Atmosphere is not stated for this batch in the covered source pages.")
    if not operations:
        missing.append("Workup and purification details are not fully stated for this batch in the covered source pages.")
    missing.extend(unresolved or [])
    return base_record(rid, kind, evidence, participants, steps, outcomes, notes or [], missing)


records = []

# Prior-work Equation 1 contains two generic arrows and is not a batch reported in this paper.
p1 = [ev(1, "image"), ev(1, "text")]
for rid, conditions, outcome_label, outcome_note in [
    ("eq1_prior_thermal_path", [("solvent", "xylene"), ("temperature", "reflux")], "generic fused-cyclobutane product", "Prior-work generic thermal [2+2] path; reported range 38--74%."),
    ("eq1_prior_palladium_path", [("solvent", "toluene")], "generic alternative fused-cyclobutane product", "Prior-work generic Pd(PPh3)4/K2CO3/n-Bu4NI path."),
]:
    r = participant(f"{rid}_reactant", "reactant", p1, label="generic bisallene (X variable)")
    p = participant(f"{rid}_product", "product", p1, label=outcome_label)
    agents = []
    if "palladium" in rid:
        agents = [
            participant(f"{rid}_pd", "catalyst", p1, name="Pd(PPh3)4", amounts=[amount("catalyst_loading", 5, "mol%", p1)]),
            participant(f"{rid}_base", "reagent", p1, name="K2CO3", amounts=[amount("equivalents", 4, "equiv", p1)]),
            participant(f"{rid}_salt", "reagent", p1, name="n-Bu4NI", amounts=[amount("equivalents", 2, "equiv", p1)]),
        ]
    cond = [field(name, value, p1) for name, value in conditions]
    outcomes = []
    if "thermal" in rid:
        outcomes.append(field("reported_yield_range", {"minimum": 38, "maximum": 74, "unit": "%", "raw_text": "38%-74%"}, p1, [p["entity_id"]]))
    records.append(base_record(rid, "literature_example", p1, [r, p] + agents, [{"step_id": "generic_prior_path", "participant_ids": [x["entity_id"] for x in [r, p] + agents], "conditions": cond}], outcomes, [outcome_note, "Equation 1 is explicitly tied to reference 4e."], ["Generic X substituent prevents a unique complete structure assignment.", "This is prior work, not a new experiment of the present paper."]))

# Prior-work Scheme 1 has two substituent-dependent Rh(I) branches.
p2 = [ev(2, "image"), ev(2, "text"), ev(1, "text")]
for rid, branch, products in [
    ("scheme1_prior_r1_h", "R1 = H", ["cyclometallated Rh(III) intermediate", "ref. 4a product or ref. 4b product"]),
    ("scheme1_prior_r1_nonh", "R1 != H", ["alternative cyclometallated intermediate", "ref. 4c product"]),
]:
    items = [participant(f"{rid}_reactant", "reactant", p2, label=f"generic terminally substituted bisallene, {branch}"), participant(f"{rid}_rh", "catalyst", p2, name="Rh(I)")]
    for index, label in enumerate(products, 1):
        items.append(participant(f"{rid}_product_{index}", "product", p2, label=label))
    records.append(base_record(rid, "literature_example", p2, items, [{"step_id": "prior_rh_pathway", "participant_ids": [x["entity_id"] for x in items], "conditions": []}], [], [f"Scheme 1 prior-work branch {branch}; source points to references 4a--4c."], ["Generic X/R/R1 labels and metal-bound intermediates preclude unique structures.", "Amounts, solvent, time, temperature, and yields are not stated in this scheme.", "This is prior work, not a new experiment of the present paper."]))

# Rh-catalyzed unsuccessful trial in Scheme 2a.
rid = "scheme2_rh_failure_1a"
e12 = [ev(1, "image"), ev(1, "text"), ev(2, "image"), ev(2, "text")]
r = participant(f"{rid}_reactant_1a", "reactant", e12, label="1a")
c = participant(f"{rid}_catalyst", "catalyst", e12, name="[RhCl(CO)2]2", amounts=[amount("catalyst_loading", 2.5, "mol%", e12)])
s = participant(f"{rid}_solvent", "solvent", e12, name="acetonitrile", smiles="CC#N")
records.append(base_record(rid, "reported_experiment", e12, [r, c, s], [{"step_id": "reaction", "participant_ids": [x["entity_id"] for x in [r, c, s]], "conditions": [field("solvent", "acetonitrile", e12), field("temperature", "reflux", e12), field("reaction_time", {"number": 24, "unit": "h"}, e12)]}], [field("main_product_result", "no obvious main product", e12), field("recovered_starting_material_yield", {"number": 12, "unit": "%"}, e12, [r["entity_id"]])], ["No obvious main product was observed by TLC; starting material 1a was recovered."], ["Substrate amount, solvent volume, atmosphere, workup, and purification are not stated.", "No product structure is assigned because the source reports no obvious main product.", "No supporting-information file was explicitly associated with this paper."]))

# Present-paper thermal experiments. Conditions A is 0.05 M bisallene in refluxing toluene.
records.append(reaction_record("scheme2_thermal_1a_2a", "reported_experiment", [1, 2, 4], "1a", [("2a", "4,4-bis(methoxycarbonyl)-2-(phenylsulfonyl)bicyclo[5.2.0]nona-1,6-diene"), ("2a'", None)], substrate_mass=37.6, substrate_amount=0.1, solvent_volume=2, time=32, concentration=0.05, product_mass=33.3, product_mass_targets=["scheme2_thermal_1a_2a_product_2a"], product_yield=89, yield_targets=["scheme2_thermal_1a_2a_product_2a"], ratio="97:3", atmosphere="argon", operations=["cooled to room temperature and evaporated", "flash chromatography on silica gel; petroleum ether/ethyl acetate 4:1"], notes=["The scheme and experimental figure report 2a:2a' = 97:3, while page-1 prose reports >=97:3; the exact scheme value is structured and the discrepancy is retained."], unresolved=["The minor regioisomer 2a' is shown but not given a unique name or isolated yield."]))

records.append(reaction_record("scheme3_1b_2b", "substrate_scope_entry", [2, 3, 4], "1b", [("2b", "4,4-bis(methoxycarbonyl)-2-(phenylsulfonyl)-8-dimethylbicyclo[5.2.0]nona-1,6-diene")], substrate_mass=40, substrate_amount=0.1, solvent_volume=2, time=31, concentration=0.05, product_mass=36, product_yield=90))
records.append(reaction_record("scheme3_1c_2c", "substrate_scope_entry", [2, 3, 4], "1c", [("2c", "4,4-bis(methoxycarbonyl)-5-methyl-2-(phenylsulfonyl)bicyclo[5.2.0]nona-1,6-diene")], substrate_mass=100.2, substrate_amount=0.26, solvent_volume=5.1, time=24, concentration=0.05, product_mass=71.4, product_yield=71, notes=["The source reports two additional unknown TLC spots."], unresolved=["Two unknown spots are not structurally assigned or quantified."]))
records.append(reaction_record("scheme3_1d_2d", "substrate_scope_entry", [2, 3, 4, 5], "1d", [("2d", "N-tosyl-2-(phenylsulfonyl)-8-dimethyl-4-azabicyclo[5.2.0]nona-1,6-diene"), ("2d'", None)], substrate_mass=44, substrate_amount=0.1, solvent_volume=2, time=28, concentration=0.05, product_mass=37, product_mass_targets=["scheme3_1d_2d_product_2d"], product_yield=84, yield_targets=["scheme3_1d_2d_product_2d"], ratio="88.5:11.5", unresolved=["The minor regioisomer 2d' is not assigned an isolated yield."]))
records.append(reaction_record("scheme3_1e_2e", "substrate_scope_entry", [2, 3, 5], "1e", [("2e", "N-tosyl-2-(phenylsulfonyl)-4-azabicyclo[5.2.0]nona-1,6-diene"), ("2e'", None)], substrate_mass=41.8, substrate_amount=0.1, solvent_volume=2, time=29, concentration=0.05, product_mass=32.8, product_yield=78, ratio="90:10", operations=["major isomer 2e could be obtained by further recrystallization"], unresolved=["The 78% yield and 32.8 mg refer to the 2e/2e' mixture; no separate isolated yield for recrystallized 2e is stated."]))
records.append(reaction_record("scheme4_1f_2f", "substrate_scope_entry", [2, 3, 5], "1f", [("2f", "4,4-bis(benzyloxycarbonyl)-2-(phenylsulfonyl)bicyclo[6.2.0]deca-1,7-diene"), ("2f'", None)], substrate_mass=43.2, substrate_amount=0.08, solvent_volume=1.6, time=42, concentration=0.05, product_mass=31.4, product_mass_targets=["scheme4_1f_2f_product_2f"], product_yield=73, yield_targets=["scheme4_1f_2f_product_2f"], ratio="88.5:11.5", operations=["flash chromatography; petroleum ether/ethyl acetate 5:1"], unresolved=["The minor regioisomer 2f' is not assigned an isolated yield."]))
records.append(reaction_record("scheme4_1g_2g", "substrate_scope_entry", [2, 3, 5], "1g", [("2g", "N-tosyl-2-(phenylsulfonyl)-4-azabicyclo[6.2.0]deca-1,7-diene"), ("2g'", None)], substrate_mass=85.1, substrate_amount=0.2, solvent_volume=4, time=42, concentration=0.05, product_mass=51.5, product_mass_targets=["scheme4_1g_2g_product_2g"], product_yield=61, yield_targets=["scheme4_1g_2g_product_2g"], ratio=">95.4:4.6", operations=["flash chromatography; petroleum ether/ethyl acetate 4:1 to 3:1"], unresolved=["The minor regioisomer 2g' is not assigned an isolated yield."]))
records.append(reaction_record("scheme4_1h_2h", "substrate_scope_entry", [2, 3, 5, 6], "1h", [("2h", "N-tosyl-2-(phenylsulfonyl)-5-azabicyclo[6.2.0]deca-1,7-diene")], substrate_mass=43.1, substrate_amount=0.1, solvent_volume=2, time=48, concentration=0.05, product_mass=39.7, product_yield=92))
records.append(reaction_record("scheme4_1i_2i", "substrate_scope_entry", [2, 3, 6], "1i", [("2i", "N-tosyl-2-(phenylsulfonyl)-10-dimethyl-5-azabicyclo[6.2.0]deca-1,7-diene"), ("2i'", None)], substrate_mass=46, substrate_amount=0.1, solvent_volume=2, time=37, concentration=0.05, product_mass=35, product_yield=76, ratio=">=92:8", notes=["Products 2i and 2i' were inseparable."], unresolved=["The 35 mg and 76% values are combined outcomes for inseparable 2i/2i'."]))

# Comparative unsubstituted/n-butyl thermal reactions.
e5a = [ev(p, k) for p in [1, 2, 6] for k in ["image", "text"]]
recovery_conflict = field("recovered_starting_material_yield_narrative", {"number": 72, "unit": "%"}, [ev(1, "image"), ev(1, "text")], ["scheme2_thermal_3_5a_reactant_3"])
records.append(reaction_record("scheme2_thermal_3_5a", "reported_experiment", [1, 2, 6], "3", [("5a", "4,4-bis(methoxycarbonyl)bicyclo[5.2.0]nona-1,6-diene")], substrate_mass=136, substrate_amount=0.58, solvent_volume=11, time=103, product_mass=15, product_yield=11, recovered_mass=94, recovery=69, additional_outcomes=[recovery_conflict], operations=["flash chromatography; petroleum ether/ethyl acetate 50:1"], notes=["Scheme 2 and the experimental section report 69% recovered 3; page-1 narrative reports 72%. Both source values are retained."], unresolved=["The recovered-starting-material percentage conflicts between page-1 prose (72%) and the scheme/experimental section (69%)."]))
records.append(reaction_record("scheme2_thermal_4_5b", "reported_experiment", [1, 2, 6], "4", [("5b", "4,4-bis(methoxycarbonyl)-2-(n-butyl)bicyclo[5.2.0]nona-1,6-diene"), ("5b'", None)], substrate_mass=41.2, substrate_amount=0.14, solvent_volume=3, time=88, product_mass=24.9, product_mass_targets=["scheme2_thermal_4_5b_product_5b"], product_yield=60, yield_targets=["scheme2_thermal_4_5b_product_5b"], ratio="88.5:11.5", recovered_mass=4.1, recovery=10, operations=["flash chromatography; petroleum ether/ethyl acetate 30:1"], unresolved=["The minor regioisomer 5b' is not assigned an isolated yield."]))
records.append(reaction_record("eq2_6_7", "reported_experiment", [3, 6], "6", [("7", "N-tosyl-4-azabicyclo[6.2.0]deca-1,7-diene")], substrate_mass=216.7, substrate_amount=0.75, solvent_volume=6, time=(4.5, "d"), product_mass=31.4, product_yield=14, recovered_mass=142.7, recovery=66, operations=["flash chromatography; petroleum ether/ethyl acetate 40:1"], notes=["The Results text explicitly calls the 14% product yield isolated."]))

# Scheme 5 is a proposed mechanism, not an isolated experiment.
e345 = [ev(p, k) for p in [3, 4] for k in ["image", "text"]]
mech_parts = [
    participant("scheme5_biradical_mechanism_1", "reactant", e345, label="generic bisallene 1"),
    participant("scheme5_biradical_mechanism_M1", "unspecified_agent", e345, label="biradical intermediate M1"),
    participant("scheme5_biradical_mechanism_M2", "unspecified_agent", e345, label="biradical intermediate M2"),
    participant("scheme5_biradical_mechanism_2", "product", e345, label="bicyclic product 2"),
    participant("scheme5_biradical_mechanism_2prime", "product", e345, label="regioisomer 2'"),
]
records.append(base_record("scheme5_biradical_mechanism", "mechanism", e345, mech_parts, [
    {"step_id": "M1_pathway", "participant_ids": ["scheme5_biradical_mechanism_1", "scheme5_biradical_mechanism_M1", "scheme5_biradical_mechanism_2"], "conditions": [field("operation", "proposed central-carbon bond formation followed by intramolecular radical coupling", e345)]},
    {"step_id": "M2_pathway", "participant_ids": ["scheme5_biradical_mechanism_1", "scheme5_biradical_mechanism_M2", "scheme5_biradical_mechanism_2prime"], "conditions": [field("operation", "alternative proposed biradical pathway to regioisomer 2'", e345)]},
], [], ["The paper states that the thermal [2+2] cycloaddition may involve biradical intermediates."], ["Scheme 5 is a proposed generic mechanism, not a reported batch.", "Generic X and the open-shell intermediates preclude unique verified structures."]))

assert len(records) == 18
assert len({r["record_id"] for r in records}) == len(records)
OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
print(f"wrote {len(records)} records to {OUT}")
