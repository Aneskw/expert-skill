#!/usr/bin/env python3
"""Build evidence-linked records for jo9903205, original PDF pages 1-4."""
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "runs/current"
DOC = "doc_5d8520112c2f7906"


def ev(page: int, kind: str = "image") -> str:
    return f"{DOC}:page{page}:{kind}"


def fact(value, evidence=()):
    return {
        "value": value,
        "evidence_ids": list(evidence),
        "verification": "missing" if value is None else "unreviewed",
    }


def field(name, value, evidence=()):
    return {"name": name, "fact": fact(value, evidence)}


def participant(entity_id, role, label, name, evidence, amounts=()):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence),
        "smiles": fact(None),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": [field(n, v, evidence) for n, v in amounts],
    }


def record(rid, kind, evidence, participants=(), conditions=(), outcomes=(), notes=(), unresolved=()):
    evidence = list(dict.fromkeys(evidence))
    participants = list(participants)
    return {
        "record_id": f"{DOC}:{rid}",
        "document_id": DOC,
        "source_reaction_id": rid,
        "record_kind": kind,
        "status": "needs_review",
        "completeness": "partial",
        "evidence_ids": evidence,
        "participants": participants,
        "steps": ([{
            "step_id": "step1",
            "participant_ids": [p["entity_id"] for p in participants],
            "conditions": [field(n, v, evidence) for n, v in conditions],
        }] if participants or conditions else []),
        "outcomes": [field(n, v, evidence) for n, v in outcomes],
        "notes": [fact(v, evidence) for v in notes],
        "review": {
            "method": "model",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": list(unresolved),
        },
    }


records = []

# Page 1: retrosynthetic scheme, prior work, and starting-material preparations.
records.append(record(
    "scheme1_general_retrosynthesis", "general_scheme", [ev(1)],
    participants=[
        participant("generic_beta_halo_enone", "product", "generic beta-halo beta,gamma-unsaturated ketone", None, [ev(1)]),
        participant("generic_allenyl_ketone", "reactant", "generic 1,2-allenyl ketone", None, [ev(1)]),
    ],
    notes=["Retrosynthetic double arrow with generic R1-R4 and X groups; not an individual experiment."],
    unresolved=["Generic R groups and X are not instantiated; structures and operating conditions are not reported."],
))

records.append(record(
    "eq1_prior_hydrohalogenation", "literature_example", [ev(1)],
    participants=[
        participant("eq1_substrate", "reactant", "3,4-pentadien-2-one", "3,4-pentadien-2-one", [ev(1)]),
        participant("eq1_mx", "reagent", "MX", "metal halide", [ev(1)]),
        participant("eq1_product", "product", "4-halo-4-penten-2-one", "4-halo-4-penten-2-one", [ev(1)]),
        participant("eq1_hoac", "solvent", "HOAc", "acetic acid", [ev(1)]),
    ],
    conditions=[("temperature", {"number": 25, "unit": "°C"})],
    outcomes=[("yield", None)],
    notes=["The prose attributes this generic equation to the authors' earlier brief note (reference 7) and says high yields."],
    unresolved=["MX identity, reaction time, charge, workup, numerical yield, and yield basis are not specified in this presentation."],
))


def add_starting_material(rid, product_label, product_name, reactants, reagents, conditions, outcomes, evidence, notes, unresolved):
    ps = []
    for i, (label, name, amounts) in enumerate(reactants, 1):
        ps.append(participant(f"{rid}_reactant{i}", "reactant", label, name, evidence, amounts))
    for i, (label, name, amounts) in enumerate(reagents, 1):
        ps.append(participant(f"{rid}_reagent{i}", "reagent", label, name, evidence, amounts))
    ps.append(participant(f"{rid}_product", "product", product_label, product_name, evidence))
    records.append(record(rid, "reported_experiment", evidence, ps, conditions, outcomes, notes, unresolved))


add_starting_material(
    "scheme2_prepare_1", "1", "3,4-pentadien-2-one",
    [("2,4-pentanedione", "2,4-pentanedione", ())],
    [("bromination reagent not shown", None, ()), ("NEt3", "triethylamine", ())],
    [], [("yield", None)], [ev(1)],
    ["Scheme 2 depicts bromination followed by triethylamine elimination; the text says compound 1 was prepared by a known method with modification."],
    ["Brominating reagent, quantities, temperatures, times, workup, purification, and yield are missing."],
)
add_starting_material(
    "scheme2_prepare_2", "2", "3-methyl-3,4-pentadien-2-one",
    [("R-substituted 2,4-pentanedione (R = CH3)", None, ())],
    [("bromination reagent not shown", None, ()), ("NEt3", "triethylamine", ())],
    [], [("yield", None)], [ev(1)],
    ["Scheme 2 depicts bromination followed by triethylamine elimination; the text cites references 8 and 9."],
    ["Brominating reagent, quantities, temperatures, times, workup, purification, and yield are missing."],
)
add_starting_material(
    "scheme2_prepare_3", "3", "3-butyl-3,4-pentadien-2-one",
    [("4-bromo-3-butyl-4-penten-2-one", "4-bromo-3-butyl-4-penten-2-one", (("mass", {"number": 2.19, "unit": "g"}), ("amount", {"number": 10, "unit": "mmol"})))],
    [("NEt3", "triethylamine", (("mass", {"number": 1.01, "unit": "g"}), ("amount", {"number": 10, "unit": "mmol"}))),
     ("CH3CN", "acetonitrile", (("volume", {"number": 10, "unit": "mL"}),))],
    [("initial_temperature", "room temperature"), ("reaction_temperature", "reflux"), ("reaction_time", {"number": 20, "unit": "h"}),
     ("workup", "diluted with ether; washed with 5% HCl and cold water; dried over MgSO4; solvent evaporated"),
     ("purification", "silica gel chromatography, pentane/ether 200:1")],
    [("isolated_mass", {"number": 0.745, "unit": "g"}), ("isolated_yield", {"number": 54, "unit": "%"})],
    [ev(1), ev(3)],
    ["Detailed preparation is printed on page 3 and corresponds to compound 3 in Scheme 2."],
    ["Atmosphere and reaction concentration are not reported."],
)
add_starting_material(
    "scheme2_prepare_4", "4", "5-methyl-3,4-hexadien-2-one",
    [("1-bromo-3-methyl-1,2-butadiene", None, ())],
    [("n-BuLi", "n-butyllithium", ()), ("CH3CONMe2", "N,N-dimethylacetamide", ()), ("H3O+", "aqueous acid workup", ())],
    [("sequence", "1. n-BuLi; 2. CH3CONMe2; 3. H3O+")], [("yield", None)], [ev(1)],
    ["Scheme 2 and the text indicate preparation according to reference 10 with modification."],
    ["Charges, solvent, temperatures, times, workup detail, purification, and yield are missing."],
)
add_starting_material(
    "scheme2_prepare_5", "5", "3,4-nonadien-2-one",
    [("1,2-heptadiene", "1,2-heptadiene", (("mass", {"number": 1.92, "unit": "g"}), ("amount", {"number": 20, "unit": "mmol"})))],
    [("n-BuLi", "n-butyllithium", (("amount", {"number": 20, "unit": "mmol"}),)),
     ("CH3CONMe2", "N,N-dimethylacetamide", (("mass", {"number": 2.61, "unit": "g"}), ("amount", {"number": 30, "unit": "mmol"}))),
     ("THF", "tetrahydrofuran", (("volume", {"number": 20, "unit": "mL"}),))],
    [("stage1_temperature", {"number": -50, "unit": "°C"}), ("stage1_time", {"number": 2, "unit": "h"}),
     ("stage2_temperature", {"number": -78, "unit": "°C"}), ("stage2_time", {"number": 2, "unit": "h"}),
     ("quench", "slow transfer into ice-cold 0.1 N aqueous HCl, 400 mL"),
     ("workup", "ether extraction; MgSO4 drying; rotary evaporation"),
     ("purification", "silica gel chromatography, pentane/ether 40:1")],
    [("isolated_mass", {"number": 1.46, "unit": "g"}), ("isolated_yield", {"number": 53, "unit": "%"})],
    [ev(1), ev(3)],
    ["Detailed preparation on page 3 corresponds to compound 5 in Scheme 2."],
    ["Atmosphere and addition duration are not reported."],
)
add_starting_material(
    "scheme2_prepare_6", "6", "3,4-dodecadien-2-one",
    [("corresponding 1,2-allene precursor", None, ())],
    [("n-BuLi", "n-butyllithium", ()), ("CH3CONMe2", "N,N-dimethylacetamide", ()), ("H3O+", "aqueous acid workup", ())],
    [("sequence", "1. n-BuLi; 2. CH3CONMe2; 3. H3O+")], [("yield", None)], [ev(1), ev(3)],
    ["Scheme 2 and the text say compound 6 was prepared according to reference 10; page 3 supplies characterization but no local preparation quantities."],
    ["Exact precursor identity, charges, solvent, temperatures, times, workup, purification, and yield are missing."],
)


def hydro_participants(prefix, substrate_label, substrate_name, mx, products, evidence, substrate_amount=None, mx_amount=None, solvent=None):
    ps = [participant(f"{prefix}_substrate", "reactant", substrate_label, substrate_name, evidence,
                      (("amount", substrate_amount),) if substrate_amount else ())]
    ps.append(participant(f"{prefix}_mx", "reagent", mx, mx, evidence,
                          (("amount", mx_amount),) if mx_amount else ()))
    if solvent:
        ps.append(participant(f"{prefix}_solvent", "solvent", solvent, solvent, evidence))
    for i, (label, name) in enumerate(products, 1):
        ps.append(participant(f"{prefix}_product{i}", "product", label, name, evidence))
    return ps


# Table 1: all rows share the explicitly printed experimental procedure across pages 3-4.
table1_rows = [
    (1, "NaI", "HOAc-MeCN", 25, 3, 25, 3, "89/11"),
    (2, "NaI", "HOAc", 25, 3, 44, 3, "94/6"),
    (3, "NaI", "HOAc", 25, 5, 74, 7, "91/9"),
    (4, "NaI", "HOAc-THF (1:1)", 25, 5, 58, 9, "87/13"),
    (5, "NaI", "HOAc (1 N)-THF", 0, 5, 56, 0.9, "98/2"),
    (6, "LiI", "HOAc (1 N)-THF", 0, 5, 63, 2.2, "97/3"),
    (7, "NaI", "HOAc (3 N)-THF", 25, 5, 64, 7, "90/10"),
    (8, "LiI", "HOAc (3 N)-THF", 25, 5, 59, 7, "89/11"),
    (9, "LiI", "HOAc (3 N)-THF", 0, 5, 76, 1.7, "98/2"),
    (10, "NaI", "HOAc (3 N)-THF", 0, 10, 79, 1.9, "98/2"),
]
for entry, mx, solvent, temp, time, y7, y8, ratio in table1_rows:
    rid = f"table1_entry_{entry}"
    evidence = [ev(2), ev(3), ev(4)]
    ps = hydro_participants(
        rid, "1", "3,4-pentadien-2-one", mx,
        [("7", "4-iodo-4-penten-2-one"), ("8", "4-iodo-3-penten-2-one")], evidence,
        {"number": 2.0, "unit": "mmol"}, {"number": 2.2, "unit": "mmol"}, solvent,
    )
    records.append(record(
        rid, "optimization_entry", evidence, ps,
        [("temperature", {"number": temp, "unit": "°C"}), ("time", {"number": time, "unit": "h"}),
         ("workup", "diluted with ether; neutralized with aqueous K2CO3 at 0 °C; layers separated; aqueous layer extracted with ether; combined ether layers dried over MgSO4; solvent evaporated"),
         ("analysis", "300 MHz 1H NMR using CH2Br2 as internal standard")],
        [("NMR_yield_7", {"number": y7, "unit": "%"}), ("NMR_yield_8", {"number": y8, "unit": "%"}), ("ratio_7_to_8", ratio)],
        ["The product spectral data for 7 are stated to match reference 7."],
        ["Atmosphere, exact solvent volume/concentration (except printed HOAc normality/ratio), and purity are not reported."],
    ))


def add_scope_row(rid, substrate_label, substrate_name, mx, solvent, temp, time, products, outcomes, evidence, notes=(), unresolved=(), extra_conditions=()):
    ps = hydro_participants(rid, substrate_label, substrate_name, mx, products, evidence, solvent=solvent)
    conditions = [("temperature", {"number": temp, "unit": "°C"})]
    if time is not None:
        conditions.append(("time", {"number": time, "unit": "h"}))
    conditions.extend(extra_conditions)
    records.append(record(rid, "substrate_scope_entry", evidence, ps, conditions, outcomes, notes, unresolved))


# Scheme 3, including the detailed 9a preparation on page 4.
scheme3 = [
    ("NaI", 24, "9a", "4-iodo-4-nonen-2-one", 90, 76, 3.6, None),
    ("LiBr-H2O", 38, "9b", "4-bromo-4-nonen-2-one", 93, 82, 5, None),
    ("LiCl-H2O", 62, "9c", "4-chloro-4-nonen-2-one", 25, 17, 55, 50),
]
for i, (mx, time, label, pname, znmr, ziso, enmr, eiso) in enumerate(scheme3, 1):
    rid = f"scheme3_{label}"
    evidence = [ev(2), ev(4)] if label in ("9a", "9b", "9c") else [ev(2)]
    outcomes = [("NMR_yield_Z", {"number": znmr, "unit": "%"}), ("isolated_yield_Z", {"number": ziso, "unit": "%"}),
                ("NMR_yield_E", {"number": enmr, "unit": "%"}),
                ("isolated_yield_E", {"number": eiso, "unit": "%"}) if eiso is not None else ("isolated_yield_E", None),
                ("alpha_beta_unsaturated_product_observed", False)]
    notes = ["LiX monohydrate was used."] if mx.startswith("Li") else []
    extra = []
    unresolved = ["Atmosphere and concentration are not reported; row-specific charge/workup is not printed."]
    if label == "9a":
        ps = hydro_participants(rid, "5", "3,4-nonadien-2-one", mx,
                               [("Z-9a", f"Z-{pname}"), ("E-9a", f"E-{pname}")], evidence,
                               {"number": 1.0, "unit": "mmol"}, {"number": 1.2, "unit": "mmol"}, "HOAc")
        ps[0]["amounts"].append(field("mass", {"number": 138, "unit": "mg"}, evidence))
        ps[1]["amounts"].append(field("mass", {"number": 180, "unit": "mg"}, evidence))
        ps[2]["amounts"].append(field("volume", {"number": 1, "unit": "mL"}, evidence))
        conditions = [("temperature", {"number": 25, "unit": "°C"}), ("time", {"number": 24, "unit": "h"}),
                      ("monitoring", "TLC to complete conversion"),
                      ("workup", "diluted with ether; neutralized with aqueous K2CO3 at 0 °C; aqueous layer extracted with ether; combined ether layers dried over MgSO4; solvent evaporated"),
                      ("purification", "silica gel chromatography, petroleum ether/ether 100:1")]
        outcomes += [("isolated_mass_Z", {"number": 202, "unit": "mg"})]
        notes += ["The crude NMR spectrum contained discernible E-isomer signals."]
        records.append(record(rid, "substrate_scope_entry", evidence, ps, conditions, outcomes, notes,
                              ["Atmosphere and reaction concentration are not reported."]))
    else:
        if label == "9c":
            outcomes.append(("configuration_assignment_method", "2D NOESY (Scheme 5)"))
        add_scope_row(rid, "5", "3,4-nonadien-2-one", mx, "HOAc", 25, time,
                      [(f"Z-{label}", f"Z-{pname}"), (f"E-{label}", f"E-{pname}")], outcomes, evidence,
                      notes=[*notes, "Prepared similarly to 9a using the conditions shown in Scheme 3."], unresolved=unresolved)


# Scheme 4.
scheme4 = [
    ("NaI", 36, "9d", "4-iodo-4-dodecen-2-one", 87, 3.5),
    ("LiBr-H2O", 48, "9e", "4-bromo-4-dodecen-2-one", 75, 3.1),
    ("LiCl-H2O", 72, "9f", "4-chloro-4-dodecen-2-one", 18, 54),
]
for mx, time, label, name, zy, ey in scheme4:
    outcomes = [("isolated_yield_Z", {"number": zy, "unit": "%"}), ("isolated_yield_E", {"number": ey, "unit": "%"}),
                ("alpha_beta_unsaturated_product_observed", False)]
    if label == "9d":
        outcomes.append(("configuration_assignment_method", "2D NOESY (Scheme 5)"))
    add_scope_row(f"scheme4_{label}", "6", "3,4-dodecadien-2-one", mx, "HOAc", 25, time,
                  [(f"Z-{label}", f"Z-{name}"), (f"E-{label}", f"E-{name}")], outcomes, [ev(2), ev(4)],
                  notes=["Prepared similarly to 9a using the conditions shown in Scheme 4.", *( ["LiX monohydrate was used."] if mx.startswith("Li") else [] )],
                  unresolved=["Row-specific charges, atmosphere, concentration, detailed workup, and purification are not printed."])


# Scheme 6.
for mx, time, label, name, y in [
    ("NaI", 25, "10a", "4-iodo-5-methyl-4-hexen-2-one", 89),
    ("LiBr-H2O", 48, "10b", "4-bromo-5-methyl-4-hexen-2-one", 90),
    ("LiCl-H2O", 48, "10c", "4-chloro-5-methyl-4-hexen-2-one", 96),
]:
    add_scope_row(f"scheme6_{label}", "4", "5-methyl-3,4-hexadien-2-one", mx, "HOAc", 25, time,
                  [(label, name)], [("yield", {"number": y, "unit": "%"}), ("yield_measurement_basis", None),
                                   ("alpha_beta_unsaturated_product_observed", False)], [ev(2), ev(4)],
                  notes=["Prepared similarly to 9a using the conditions shown in Scheme 6.", *( ["LiX monohydrate was used."] if mx.startswith("Li") else [] )],
                  unresolved=["Yield basis, row-specific charges, atmosphere, concentration, detailed workup, and purification are not reported."])


# Table 2.
table2 = [
    (1, "NaI", "HOAc", 50, 22, 25, 55, "31/69"),
    (2, "NaI", "HOAc", 25, 24, 43, 41, "51/49"),
    (3, "NaI", "CF3CO2H", 25, 24, 25, 1.1, "96/4"),
    (4, "NaI", "CF3CO2H (3 N)-THF", 25, 24, 78, 19, "80/20"),
    (5, "LiI", "CF3CO2H (3 N)-THF", 25, 24, 74, 23, "76/24"),
    (6, "NaI", "HOAc-CF3CO2H (1:1)", 25, 24, 82, 3, "96/4"),
    (7, "LiI", "HOAc-CF3CO2H (1:1)", 25, 24, 70, 2, "97/3"),
]
for entry, mx, solvent, temp, time, y11, y12, ratio in table2:
    add_scope_row(f"table2_entry_{entry}", "2", "3-methyl-3,4-pentadien-2-one", mx, solvent, temp, time,
                  [("11a", "4-iodo-3-methyl-4-penten-2-one"), ("12a", "4-iodo-3-methyl-3-penten-2-one")],
                  [("NMR_yield_11a", {"number": y11, "unit": "%"}), ("NMR_yield_12a", {"number": y12, "unit": "%"}),
                   ("ratio_11a_to_12a", ratio), ("analysis", "1H NMR using CH2Br2 as internal standard")], [ev(3), ev(4)],
                  unresolved=["Charges, atmosphere, concentration, workup, purification, and isolated yields are not reported for this row."])


# Scheme 7.
for mx, label11, name11, nmr11, iso11, label12, name12, nmr12, iso12 in [
    ("LiBr-H2O", "11b", "4-bromo-3-methyl-4-penten-2-one", 75, 65, "12b", "alpha,beta-unsaturated bromo isomer 12b", 5, 5),
    ("LiCl-H2O", "11c", "4-chloro-3-methyl-4-penten-2-one", 70, 69, "12c", "alpha,beta-unsaturated chloro isomer 12c", 5, 4),
]:
    add_scope_row(f"scheme7_{label11}", "2", "3-methyl-3,4-pentadien-2-one", mx, "CF3CO2H-HOAc", 25, None,
                  [(label11, name11), (label12, name12)],
                  [(f"NMR_yield_{label11}", {"number": nmr11, "unit": "%"}), (f"isolated_yield_{label11}", {"number": iso11, "unit": "%"}),
                   (f"NMR_yield_{label12}", {"number": nmr12, "unit": "%"}), (f"isolated_yield_{label12}", {"number": iso12, "unit": "%"}),
                   ("minor_product_isomer_count", 1), ("minor_product_C_C_configuration", None)], [ev(3), ev(4)],
                  notes=["LiX monohydrate was used; the mixed acid is described in prose as 1:1."],
                  unresolved=["Reaction time, charges, atmosphere, concentration, workup, purification, and minor-product C=C configuration are not reported/determined."])


# Scheme 8, with a full typical procedure for 13a.
scheme8 = [
    ("NaI", "13a", "4-iodo-3-butyl-4-penten-2-one", 89, 99, "3.3"),
    ("LiBr-H2O", "13b", "4-bromo-3-butyl-4-penten-2-one", 85, 99, "2.1"),
    ("LiCl-H2O", "13c", "3-butyl-4-chloro-4-penten-2-one", 74, 88, "<2"),
]
for mx, label, name, iso13, nmr13, iso14 in scheme8:
    rid = f"scheme8_{label}"
    evidence = [ev(3), ev(4)]
    nmr14 = {"number": float(iso14), "unit": "%"} if iso14 != "<2" else "<2%"
    outcomes = [("isolated_yield_13", {"number": iso13, "unit": "%"}), ("NMR_yield_13", {"number": nmr13, "unit": "%"}),
                ("NMR_yield_14", nmr14), ("isolated_yield_14", None),
                ("minor_product_isomer_count", 1), ("minor_product_C_C_configuration", None)]
    notes = ["The parenthesized Scheme 8 yields are NMR yields."]
    if mx.startswith("Li"):
        notes.append("LiX monohydrate was used.")
    if label == "13a":
        ps = hydro_participants(rid, "3", "3-butyl-3,4-pentadien-2-one", mx,
                               [(label, name), ("14a", "alpha,beta-unsaturated iodo isomer 14a")], evidence,
                               {"number": 1, "unit": "mmol"}, {"number": 1.2, "unit": "mmol"}, "HOAc-CF3CO2H (1:1)")
        ps[0]["amounts"].append(field("mass", {"number": 138, "unit": "mg"}, evidence))
        ps[1]["amounts"].append(field("mass", {"number": 180, "unit": "mg"}, evidence))
        ps[2]["amounts"].extend([field("HOAc_volume", {"number": 1, "unit": "mL"}, evidence), field("CF3CO2H_volume", {"number": 1, "unit": "mL"}, evidence)])
        outcomes.append(("isolated_mass_13a", {"number": 237, "unit": "mg"}))
        records.append(record(rid, "substrate_scope_entry", evidence, ps,
                              [("initial_temperature", "room temperature"), ("temperature", {"number": 25, "unit": "°C"}),
                               ("time", {"number": 24, "unit": "h"}), ("endpoint", "complete conversion"),
                               ("workup", "diluted with ether; neutralized with aqueous K2CO3 at 0 °C; aqueous layer extracted with ether; combined ether layers dried over MgSO4; solvent evaporated"),
                               ("purification", "silica gel chromatography, petroleum ether/ether 100:1")],
                              outcomes, notes, ["Atmosphere and reaction concentration are not reported; minor-product C=C configuration was not determined."]))
    else:
        add_scope_row(rid, "3", "3-butyl-3,4-pentadien-2-one", mx, "CF3CO2H-HOAc", 25, None,
                      [(label, name), (f"14{label[-1]}", f"alpha,beta-unsaturated {mx} isomer")], outcomes, evidence,
                      notes=[*notes, "Prepared similarly to 13a."],
                      unresolved=["Reaction time, row-specific charges, atmosphere, concentration, detailed workup, purification, and minor-product C=C configuration are not reported/determined."])


records.append(record(
    "proposed_hydrohalogenation_mechanism", "mechanism", [ev(3)],
    participants=[
        participant("mechanism_allenyl_ketone", "reactant", "1,2-allenyl ketone", None, [ev(3)]),
        participant("mechanism_halide", "reagent", "X-", "halide ion", [ev(3)]),
        participant("mechanism_product", "product", "beta,gamma-unsaturated beta-haloketone", None, [ev(3)]),
    ],
    notes=["The prose proposes nucleophilic conjugate addition of X- at the beta-position; mild acidic conditions are said to suppress isomerization to the alpha,beta-unsaturated ketone."],
    unresolved=["No mechanism drawing, intermediate structure, rate data, or direct mechanistic experiment is supplied on pages 1-4."],
))


coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1,
            "state": "attempted",
            "regions": [
                {"region": "upper-right Scheme 1", "finding": "Generic retrosynthetic relationship; not an individual experiment.", "evidence_ids": [ev(1)]},
                {"region": "right-column Scheme 2", "finding": "Six starting-material preparations/partial preparations (1-6); detailed procedures for 3 and 5 continue on page 3.", "evidence_ids": [ev(1)]},
                {"region": "left-column Equation (1) and adjacent prose", "finding": "Generic hydrohalogenation attributed to prior reference 7, classified as literature_example.", "evidence_ids": [ev(1)]},
                {"region": "results prose below Scheme 2", "finding": "Table 1 condition interpretation and no additional independent reaction arrow.", "evidence_ids": [ev(1)]},
            ],
            "record_ids": [f"{DOC}:scheme1_general_retrosynthesis", f"{DOC}:eq1_prior_hydrohalogenation", *[f"{DOC}:scheme2_prepare_{i}" for i in range(1, 7)]],
            "unresolved": ["Scheme 2 omits most charges/conditions/yields for compounds 1, 2, 4, and 6; drawing-derived structures remain unverified."],
        },
        {
            "page": 2,
            "state": "attempted",
            "regions": [
                {"region": "left upper Table 1", "finding": "Ten optimization rows for hydroiodination of 1, including two product yields and 7/8 ratios.", "evidence_ids": [ev(2)]},
                {"region": "left middle Scheme 3", "finding": "Three substrate-scope rows for 5 with NaI/LiBr/LiCl and Z/E outcomes.", "evidence_ids": [ev(2)]},
                {"region": "right upper Scheme 4", "finding": "Three substrate-scope rows for 6 with isolated Z/E yields.", "evidence_ids": [ev(2)]},
                {"region": "right middle Scheme 5", "finding": "NOESY configuration assignments for 9c and 9d; linked as analytical evidence, not a new reaction.", "evidence_ids": [ev(2)]},
                {"region": "right lower Scheme 6", "finding": "Three substrate-scope rows for 4 with NaI/LiBr/LiCl; alpha,beta isomers reported absent.", "evidence_ids": [ev(2)]},
            ],
            "record_ids": [*[f"{DOC}:table1_entry_{i}" for i in range(1, 11)], *[f"{DOC}:scheme3_9{x}" for x in "abc"], *[f"{DOC}:scheme4_9{x}" for x in "def"], *[f"{DOC}:scheme6_10{x}" for x in "abc"]],
            "unresolved": ["Scheme 6 does not state the yield measurement basis; row-specific charges and workups for Schemes 3, 4, and 6 are incomplete."],
        },
        {
            "page": 3,
            "state": "attempted",
            "regions": [
                {"region": "left upper Table 2", "finding": "Seven optimization rows for 2 with 11a/12a NMR yields and ratios.", "evidence_ids": [ev(3)]},
                {"region": "left middle Scheme 7", "finding": "Two halide-scope rows for 2 with major/minor NMR and isolated yields.", "evidence_ids": [ev(3)]},
                {"region": "right upper Scheme 8", "finding": "Three halide-scope rows for 3 with isolated/NMR yields and minor products.", "evidence_ids": [ev(3)]},
                {"region": "left lower mechanism prose", "finding": "Textual proposed conjugate-addition mechanism; no depicted intermediate or direct mechanistic experiment.", "evidence_ids": [ev(3)]},
                {"region": "right lower Experimental Section", "finding": "Detailed preparations of 3 and 5 and the general Table 1 procedure; characterization of 6.", "evidence_ids": [ev(3)]},
            ],
            "record_ids": [*[f"{DOC}:table2_entry_{i}" for i in range(1, 8)], f"{DOC}:scheme7_11b", f"{DOC}:scheme7_11c", *[f"{DOC}:scheme8_13{x}" for x in "abc"], f"{DOC}:scheme2_prepare_3", f"{DOC}:scheme2_prepare_5", f"{DOC}:scheme2_prepare_6", f"{DOC}:proposed_hydrohalogenation_mechanism", *[f"{DOC}:table1_entry_{i}" for i in range(1, 11)]],
            "unresolved": ["Scheme 7 and Scheme 8 do not print reaction times; minor-product C=C configurations are explicitly undetermined; many row-specific charges are absent."],
        },
        {
            "page": 4,
            "state": "attempted",
            "regions": [
                {"region": "top-left continuation of Table 1 procedure", "finding": "Crude-product NMR analysis using CH2Br2 internal standard; linked to all Table 1 rows.", "evidence_ids": [ev(4)]},
                {"region": "left-column 9a typical procedure and 9b-9f characterization", "finding": "Full 9a preparation merged with Scheme 3; related products stated to be prepared similarly.", "evidence_ids": [ev(4)]},
                {"region": "right-column 13a typical procedure and 13b-13c/11a-11c characterization", "finding": "Full 13a preparation merged with Scheme 8; related products characterized without independent reaction runs.", "evidence_ids": [ev(4)]},
                {"region": "bottom-right Supporting Information notice", "finding": "Article announces spectra online, but no SI file is supplied or associated in this pilot.", "evidence_ids": [ev(4)]},
            ],
            "record_ids": [*[f"{DOC}:table1_entry_{i}" for i in range(1, 11)], *[f"{DOC}:scheme3_9{x}" for x in "abc"], *[f"{DOC}:scheme4_9{x}" for x in "def"], *[f"{DOC}:scheme6_10{x}" for x in "abc"], *[f"{DOC}:table2_entry_{i}" for i in range(1, 8)], f"{DOC}:scheme7_11b", f"{DOC}:scheme7_11c", *[f"{DOC}:scheme8_13{x}" for x in "abc"]],
            "unresolved": ["SI association remains unestablished; announced spectra and any SI-only experimental detail are unavailable."],
        },
    ],
}


def main():
    raw = OUT / "raw_model/records_pages_0001_0004.json"
    cov = OUT / "coverage/pages_0001_0004.json"
    raw.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
    cov.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"records": len(records), "raw": str(raw), "coverage": str(cov)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
