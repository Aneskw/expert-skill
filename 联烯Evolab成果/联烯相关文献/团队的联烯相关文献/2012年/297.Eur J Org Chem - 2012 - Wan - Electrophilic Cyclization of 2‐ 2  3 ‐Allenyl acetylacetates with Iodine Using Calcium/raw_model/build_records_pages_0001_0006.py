#!/usr/bin/env python3
"""Build evidence-linked machine records for Wan et al., PDF pages 1--6."""
import json
from pathlib import Path

DOC = "doc_ddf8c15e6f7a1eca"
OUT = Path(__file__).with_name("records_pages_0001_0006.json")


def ev(page, kind="text"):
    return f"{DOC}:page{page}:{kind}"


def fact(value, evidence):
    return {
        "value": value,
        "evidence_ids": list(evidence) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def q(number, unit, **extra):
    return {"number": number, "unit": unit, **extra}


def field(name, value, evidence, targets=None):
    item = {"name": name, "fact": fact(value, evidence)}
    if targets:
        item["target_entity_ids"] = targets
    return item


def participant(entity_id, role, label, name, evidence, smiles=None, amounts=None):
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


def amount(name, number, unit, evidence):
    return field(name, q(number, unit), evidence)


def record(rid, source_id, kind, evidence, participants, steps, outcomes,
           notes=None, unresolved=None):
    return {
        "record_id": f"{DOC}:{rid}",
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


SIMPLE_SMILES = {
    "I2": "II",
    "CaH2": "[CaH2]",
    "tBuOK": "CC(C)(C)[O-].[K+]",
    "K2CO3": "[K+].[K+].[O-]C([O-])=O",
    "K3PO4": "[K+].[K+].[K+].[O-]P([O-])([O-])=O",
    "NaOH": "[Na+].[OH-]",
    "Et3N": "CCN(CC)CC",
    "NaH": "[Na+].[H-]",
    "THF": "C1CCOC1",
    "CH3CN": "CC#N",
    "CH3NO2": "C[N+](=O)[O-]",
    "Et2O": "CCOCC",
    "toluene": "Cc1ccccc1",
    "CH2Cl2": "ClCCl",
    "internal_standard": "Cc1cc(C)cc(C)c1",
    "phenylboronic_acid": "OB(O)c1ccccc1",
    "1_hexyne": "CCCCC#C",
    "propargyl_alcohol": "C#CCO",
    "CuI": "[Cu]I",
    "Et2NH": "CCNCC",
    "K3PO4_3H2O": "O.O.O.[K+].[K+].[K+].[O-]P([O-])([O-])=O",
}

SUBSTRATE_SMILES = {
    "1a": "C=C=CCC(C(C)=O)C(=O)OCC",
    "1b": "C=C=CCC(C(C)=O)C(=O)OC",
    "1c": "C=C=CCC(C(=O)CC)C(=O)OC",
    "1d": "C=C=CCC(C(=O)C(C)C)C(=O)OC",
    "1e": "C=C=CCC(C(=O)Cc1ccccc1)C(=O)OC",
    "1f": "C=C=CCC(C(=O)c1ccccc1)C(=O)OCC",
}

PRODUCT_NAMES = {
    "2a": "3-(Ethoxycarbonyl)-5-(1-iodovinyl)-2-methyl-4,5-dihydrofuran",
    "2b": "5-(1-Iodovinyl)-3-(methoxycarbonyl)-2-methyl-4,5-dihydrofuran",
    "2c": "2-Ethyl-5-(1-iodovinyl)-3-(methoxycarbonyl)-4,5-dihydrofuran",
    "2d": "5-(1-Iodovinyl)-2-isopropyl-3-(methoxycarbonyl)-4,5-dihydrofuran",
    "2e": "2-Benzyl-5-(1-iodovinyl)-3-(methoxycarbonyl)-4,5-dihydrofuran",
    "2f": "3-(Ethoxycarbonyl)-5-(1-iodovinyl)-2-phenyl-4,5-dihydrofuran",
    "2g": "3-(Ethoxycarbonyl)-5-ethyl-5-(1-iodovinyl)-2-methyl-4,5-dihydrofuran",
    "2h": "5-Benzyl-5-(1-iodovinyl)-2-isopropyl-3-(methoxycarbonyl)-4,5-dihydrofuran",
    "2i": "5-(1-Iodo-2-methyl-1-propenyl)-2-isopropyl-3-(methoxycarbonyl)-4,5-dihydrofuran",
    "2j": "2-Isopropyl-3-(methoxycarbonyl)-5-(2,2-pentamethylene-1-iodovinyl)-4,5-dihydrofuran",
    "2k": "5-(1-Iodo-1-undecenyl)-2-isopropyl-3-(methoxycarbonyl)-4,5-dihydrofuran",
    "2l": "5-(2-Cyclohexyl-1-iodovinyl)-2-isopropyl-3-(methoxycarbonyl)-4,5-dihydrofuran",
}

PRODUCT_SMILES = {
    "2a": "CCOC(=O)C1=C(C)OC(C1)C(=C)I",
    "2b": "COC(=O)C1=C(C)OC(C1)C(=C)I",
    "2c": "COC(=O)C1=C(CC)OC(C1)C(=C)I",
    "2d": "COC(=O)C1=C(C(C)C)OC(C1)C(=C)I",
    "2e": "COC(=O)C1=C(CC2=CC=CC=C2)OC(C1)C(=C)I",
    "2f": "CCOC(=O)C1=C(c2ccccc2)OC(C1)C(=C)I",
}

SUBSTITUTIONS = {
    "1a": "R1/R2/R3/R4 = CH3/Et/H/H",
    "1b": "R1/R2/R3/R4 = CH3/CH3/H/H",
    "1c": "R1/R2/R3/R4 = Et/CH3/H/H",
    "1d": "R1/R2/R3/R4 = iPr/CH3/H/H",
    "1e": "R1/R2/R3/R4 = Bn/CH3/H/H",
    "1f": "R1/R2/R3/R4 = Ph/Et/H/H",
    "1g": "R1/R2/R3/R4 = CH3/Et/Et/H",
    "1h": "R1/R2/R3/R4 = iPr/CH3/Bn/H",
    "1i": "R1/R2/R3/R4 = iPr/CH3/H/CH3",
    "1j": "R1/R2/R3/R4 = iPr/CH3/H/(CH2)5",
    "1k": "terminal allene substituent R = n-C9H19",
    "1l": "terminal allene substituent R = cyclohexyl",
}


def small(label, role, evidence, mmol=None, mg=None, equiv=None, entity=None, name=None):
    eid = entity or label.replace("·", "_").replace("-", "_")
    amts = []
    if mmol is not None:
        amts.append(amount("amount", mmol, "mmol", evidence))
    if mg is not None:
        amts.append(amount("mass", mg, "mg", evidence))
    if equiv is not None:
        amts.append(amount("equivalents", equiv, "equiv", evidence))
    return participant(eid, role, label, name or label, evidence, SIMPLE_SMILES.get(label), amts)


def substrate(label, evidence, mmol=None, mg=None, grams=None, ratio=None):
    amts = []
    if mmol is not None:
        amts.append(amount("amount", mmol, "mmol", evidence))
    if mg is not None:
        amts.append(amount("mass", mg, "mg", evidence))
    if grams is not None:
        amts.append(amount("mass", grams, "g", evidence))
    if ratio is not None:
        amts.append(field("input_Z_E_ratio", ratio, evidence))
    return participant(label, "reactant", label, SUBSTITUTIONS.get(label, label), evidence,
                       SUBSTRATE_SMILES.get(label), amts)


def product(label, evidence, mg=None, grams=None, name=None, smiles=None):
    amts = []
    if mg is not None:
        amts.append(amount("isolated_mass", mg, "mg", evidence))
    if grams is not None:
        amts.append(amount("isolated_mass", grams, "g", evidence))
    return participant(label, "product", label, name or PRODUCT_NAMES.get(label, label), evidence,
                       PRODUCT_SMILES.get(label) if smiles is None else smiles, amts)


def reaction_step(step_id, ids, evidence, solvent=None, volume=None, temperature=None,
                  time=None, atmosphere=None, purification=None, workup=None):
    c = []
    if solvent is not None:
        c.append(field("solvent", solvent, evidence))
    if volume is not None:
        c.append(field("solvent_volume", q(volume, "mL"), evidence))
    if temperature is not None:
        c.append(field("temperature", temperature if isinstance(temperature, str) else q(temperature, "°C"), evidence))
    if time is not None:
        c.append(field("time", q(time[0], time[1]), evidence))
    if atmosphere is not None:
        c.append(field("atmosphere", atmosphere, evidence))
    if purification is not None:
        c.append(field("purification", purification, evidence))
    if workup is not None:
        c.append(field("workup", workup, evidence))
    return {"step_id": step_id, "participant_ids": ids, "conditions": c}


records = []

# Table 1: twelve independent base/solvent optimization rows. Entry 7 is also Table 2 entry 1.
table1 = [
    (1, "THF", "tBuOK", 1.2, 18), (2, "THF", "K2CO3", 1.2, 28),
    (3, "THF", "K3PO4", 1.2, 54), (4, "THF", "NaOH", 1.2, 57),
    (5, "THF", "Et3N", 1.2, 70), (6, "THF", "NaH", 1.2, 75),
    (7, "THF", "CaH2", 0.6, 80), (8, "CH3CN", "CaH2", 0.6, 67),
    (9, "CH3NO2", "CaH2", 0.6, 56), (10, "Et2O", "CaH2", 0.6, 28),
    (11, "toluene", "CaH2", 0.6, 22), (12, "CH2Cl2", "CaH2", 0.6, 37),
]
for n, solvent_name, base, base_eq, yld in table1:
    evidence = [ev(1, "image"), ev(1)]
    if n == 7:
        evidence += [ev(2, "image"), ev(2)]
    rid = "table1_entry7_table2_entry1" if n == 7 else f"table1_entry{n}"
    ps = [
        substrate("1a", evidence, mmol=0.2),
        small("I2", "reagent", evidence, mmol=1.2, equiv=6, entity="iodine"),
        small(base, "reagent", evidence, equiv=base_eq, entity="base"),
        participant("solvent", "solvent", solvent_name, solvent_name, evidence,
                    SIMPLE_SMILES.get(solvent_name), [amount("volume", 2, "mL", evidence)]),
        product("2a", evidence),
        small("internal_standard", "reagent", evidence, entity="internal_standard",
              name="1,3,5-trimethylbenzene"),
    ]
    records.append(record(
        rid, f"Table 1 entry {n}" + (" / Table 2 entry 1" if n == 7 else ""),
        "optimization_entry", evidence, ps,
        [reaction_step("reaction", [p["entity_id"] for p in ps[:4]], evidence,
                       solvent=solvent_name, volume=2, temperature="r.t.", time=(0.5, "h"))],
        [field("NMR_yield", q(yld, "%"), evidence, ["2a"]),
         field("yield_measurement_basis", "1H NMR using 1,3,5-trimethylbenzene as internal standard", evidence, ["2a"])],
        unresolved=["Atmosphere, workup, and purification are not stated for this optimization row."]
    ))

# Table 2 entries 2--6. Entry 1 is already merged into Table 1 entry 7.
table2 = [(2, 5, 79, None), (3, 4, 76, None), (4, 3, 62, None),
          (5, 2, 34, 17), (6, 1, 7, 42)]
for n, iodine_eq, yld, recovery in table2:
    evidence = [ev(2, "image"), ev(2)]
    # Entry 3 is also Table 3 entry 1 and the detailed 2a batch on page 4.
    is_standard = n == 3
    if is_standard:
        evidence += [ev(4, "image"), ev(4)]
    rid = "standard_2a_table2_entry3_table3_entry1" if is_standard else f"table2_entry{n}"
    ps = [
        substrate("1a", evidence, mmol=0.2, mg=36.2 if is_standard else None),
        small("I2", "reagent", evidence, mmol=0.8 if is_standard else None,
              mg=205.0 if is_standard else None, equiv=iodine_eq, entity="iodine"),
        small("CaH2", "reagent", evidence, mmol=0.12, mg=5.2 if is_standard else None,
              equiv=0.6, entity="base"),
        participant("solvent", "solvent", "THF", "tetrahydrofuran", evidence,
                    SIMPLE_SMILES["THF"], [amount("volume", 2, "mL", evidence)]),
        product("2a", evidence, mg=45.2 if is_standard else None),
        small("internal_standard", "reagent", evidence, entity="internal_standard",
              name="1,3,5-trimethylbenzene"),
    ]
    steps = []
    if is_standard:
        steps.append(reaction_step("base_prestir", ["base", "solvent"], evidence,
                                   solvent="THF", volume=1, temperature="r.t.", time=(5, "min")))
    steps.append(reaction_step("reaction", ["1a", "iodine", "base", "solvent"], evidence,
                               solvent="THF", volume=2, temperature="r.t.", time=(0.5, "h")))
    if is_standard:
        steps.append(reaction_step(
            "workup_and_purification", ["2a"], evidence,
            workup="Quenched with saturated aqueous Na2S2O3 (10 mL), extracted with Et2O (3 x 15 mL), dried over anhydrous Na2SO4, filtered, and evaporated.",
            purification="Silica-gel chromatography, petroleum ether/dichloromethane 1:1."
        ))
    outcomes = [
        field("NMR_yield", q(yld, "%"), evidence, ["2a"]),
        field("yield_measurement_basis", "1H NMR using 1,3,5-trimethylbenzene as internal standard", evidence, ["2a"]),
    ]
    if is_standard:
        outcomes += [field("isolated_yield", q(74, "%"), evidence, ["2a"]),
                     field("isolated_yield_measurement_basis", "isolated after chromatography", evidence, ["2a"])]
    if recovery is not None:
        outcomes.append(field("recovered_starting_material_yield", q(recovery, "%"), evidence, ["1a"]))
    records.append(record(
        rid, ("Table 2 entry 3 / Table 3 entry 1 / typical 2a procedure" if is_standard else f"Table 2 entry {n}"),
        "optimization_entry", evidence, ps, steps, outcomes,
        unresolved=[] if is_standard else ["Atmosphere, workup, purification, and isolated yield are not stated for this optimization row."]
    ))

# Table 3 entry 2, the distinct one-gram scale experiment.
evidence = [ev(2, "image"), ev(2), ev(4, "image"), ev(4)]
ps = [
    substrate("1a", evidence, mmol=5.5, grams=1.0014),
    small("I2", "reagent", evidence, mmol=22.0, equiv=4, entity="iodine"),
    small("CaH2", "reagent", evidence, mmol=3.3, mg=139.1, equiv=0.6, entity="base"),
    participant("solvent", "solvent", "THF", "tetrahydrofuran", evidence, SIMPLE_SMILES["THF"],
                [amount("volume", 30, "mL", evidence)]),
    product("2a", evidence, grams=1.3207),
]
ps[1]["amounts"].append(amount("mass", 5.5840, "g", evidence))
records.append(record(
    "table3_entry2_one_gram_2a", "Table 3 entry 2 / one-gram-scale 2a procedure",
    "substrate_scope_entry", evidence, ps,
    [reaction_step("base_prestir", ["base", "solvent"], evidence, solvent="THF", volume=30,
                   temperature="r.t.", time=(10, "min")),
     reaction_step("reaction", ["1a", "iodine", "base", "solvent"], evidence,
                   solvent="THF", volume=30, temperature="r.t.", time=(0.5, "h")),
     reaction_step("workup_and_purification", ["2a"], evidence,
                   workup="Quenched with saturated aqueous Na2S2O3 (40 mL), extracted with Et2O (3 x 40 mL), dried over anhydrous Na2SO4, filtered, and evaporated.",
                   purification="Silica-gel chromatography, petroleum ether/dichloromethane 1:1.")],
    [field("isolated_yield", q(78, "%"), evidence, ["2a"]),
     field("yield_measurement_basis", "isolated after chromatography", evidence, ["2a"])],
    unresolved=["Atmosphere is not stated."]
))

# Table 3 entries 3--11, detailed across pages 4--5.
scope = [
    (3, "1b", "2b", 66, 4, 34.6, 39.7, 5.0, 203.6, "petroleum ether/dichloromethane 2:1", 30),
    (4, "1c", "2c", 72, 4, 36.7, 44.7, 5.3, 204.0, "petroleum ether/dichloromethane 2:1", 30),
    (5, "1d", "2d", 80, 4, 38.9, 51.3, 5.2, 206.0, "petroleum ether/dichloromethane 3:2", 30),
    (6, "1e", "2e", 61, 4, 49.9, 46.1, 5.4, 204.0, "petroleum ether/diethyl ether 10:1", 50),
    (7, "1f", "2f", 83, 4, 47.7, 59.7, 5.4, 202.4, "petroleum ether/ethyl acetate 3:2", 30),
    (8, "1g", "2g", 82, 5, 41.5, 54.5, 5.2, 203.6, "petroleum ether/diethyl ether 20:1", 30),
    (9, "1h", "2h", 70, 5, 57.4, 57.9, 5.4, 204.0, "petroleum ether/dichloromethane 3:1", 30),
    (10, "1i", "2i", 83, 5, 43.9, 56.9, 5.2, 203.5, "petroleum ether/ethyl acetate 30:1", 30),
    (11, "1j", "2j", 52, 5, 52.6, 40.6, 5.2, 206.0, "petroleum ether/dichloromethane 2:1", 30),
]
for n, sub, prod, yld, page, submg, prodmg, camg, i2mg, eluent, minutes in scope:
    evidence = [ev(2, "image"), ev(2), ev(page, "image"), ev(page)]
    if prod == "2g":
        evidence += [ev(4, "image"), ev(4)]
    ps = [
        substrate(sub, evidence, mmol=0.2, mg=submg),
        small("I2", "reagent", evidence, mmol=0.8, mg=i2mg, equiv=4, entity="iodine"),
        small("CaH2", "reagent", evidence, mmol=0.12, mg=camg, equiv=0.6, entity="base"),
        participant("solvent", "solvent", "THF", "tetrahydrofuran", evidence, SIMPLE_SMILES["THF"],
                    [amount("volume", 2, "mL", evidence)]),
        product(prod, evidence, mg=prodmg),
    ]
    records.append(record(
        f"table3_entry{n}_{prod}", f"Table 3 entry {n} / {prod} procedure",
        "substrate_scope_entry", evidence, ps,
        [reaction_step("reaction_and_purification", [sub, "iodine", "base", "solvent"], evidence,
                       solvent="THF", volume=2, temperature="r.t.", time=(minutes, "min"),
                       purification=f"Silica-gel chromatography, {eluent}.")],
        [field("isolated_yield", q(yld, "%"), evidence, [prod]),
         field("yield_measurement_basis", "isolated after chromatography", evidence, [prod])],
        notes=[SUBSTITUTIONS[sub]],
        unresolved=["Atmosphere and workup are not restated for this abbreviated product procedure."]
    ))

# Scheme 1: 2k and 2l are two further scope experiments, plus a separate kinetic resolution.
for sub, prod, yld, ratio, submg, prodmg, camg, i2mg in [
    ("1k", "2k", 86, "87:13", 63.3, 75.6, 5.3, 205.0),
    ("1l", "2l", 86, "85:15", 56.0, 70.3, 5.2, 203.1),
]:
    evidence = [ev(2, "image"), ev(2), ev(5, "image"), ev(5)]
    ps = [substrate(sub, evidence, mmol=0.2, mg=submg),
          small("I2", "reagent", evidence, mmol=0.8, mg=i2mg, equiv=4, entity="iodine"),
          small("CaH2", "reagent", evidence, mmol=0.12, mg=camg, equiv=0.6, entity="base"),
          participant("solvent", "solvent", "THF", "tetrahydrofuran", evidence, SIMPLE_SMILES["THF"],
                      [amount("volume", 2, "mL", evidence)]),
          product(prod, evidence, mg=prodmg)]
    records.append(record(
        f"scheme1_{prod}", f"Scheme 1 / {prod} procedure", "substrate_scope_entry", evidence, ps,
        [reaction_step("reaction_and_purification", [sub, "iodine", "base", "solvent"], evidence,
                       solvent="THF", volume=2, temperature="r.t.", time=(0.5, "h"),
                       purification="Silica-gel chromatography, petroleum ether/diethyl ether 20:1.")],
        [field("isolated_yield", q(yld, "%"), evidence, [prod]),
         field("yield_measurement_basis", "isolated after chromatography", evidence, [prod]),
         field("Z_E_ratio", ratio, evidence, [prod])],
        notes=[SUBSTITUTIONS[sub]],
        unresolved=["Atmosphere and workup are not restated; product structure and alkene stereochemistry remain machine-unverified."]
    ))

evidence = [ev(2, "image"), ev(2), ev(5, "image"), ev(5)]
ps = [
    substrate("2l_input", evidence, mmol=0.15, mg=58.4, ratio="85:15"),
    small("propargyl_alcohol", "reactant", evidence, mmol=0.053, mg=3.0, equiv=0.35,
          entity="propargyl_alcohol", name="prop-2-yn-1-ol"),
    participant("pd_catalyst", "catalyst", "Pd(PPh3)2Cl2", "bis(triphenylphosphine)palladium(II) dichloride",
                evidence, None, [amount("amount", 5.25, "umol", evidence), amount("mass", 3.7, "mg", evidence),
                                 amount("catalyst_loading", 3.5, "mol%", evidence)]),
    small("CuI", "catalyst", evidence, mmol=None, mg=1.0, entity="cui"),
    small("Et2NH", "reagent", evidence, mmol=0.053, mg=4.0, entity="diethylamine"),
    participant("solvent", "solvent", "CH3CN", "acetonitrile", evidence, SIMPLE_SMILES["CH3CN"],
                [amount("volume", 1.5, "mL", evidence)]),
    product("Z_2l", evidence, mg=45.6, name="Z-2l", smiles=None),
]
ps[3]["amounts"].extend([amount("amount", 5.25, "umol", evidence), amount("catalyst_loading", 3.5, "mol%", evidence)])
ps[4]["amounts"].append(amount("equivalents", 0.35, "equiv", evidence))
records.append(record(
    "scheme1_kinetic_resolution_Z_2l", "Scheme 1 / kinetic resolution of 2l",
    "reported_experiment", evidence, ps,
    [reaction_step("kinetic_resolution", [p["entity_id"] for p in ps[:-1]], evidence,
                   solvent="CH3CN", volume=1.5, temperature=3, time=(1.5, "h"), atmosphere="argon"),
     reaction_step("purification", ["Z_2l"], evidence,
                   purification="Concentrated and purified by silica-gel chromatography, petroleum ether/diethyl ether 15:1.")],
    [field("isolated_yield", q(78, "%"), evidence, ["Z_2l"]),
     field("yield_measurement_basis", "isolated after chromatography", evidence, ["Z_2l"]),
     field("product_stereochemical_outcome", "Z-2l as the only isomer", evidence, ["Z_2l"])],
    unresolved=["The consumed E-isomer/coupling product is not isolated or quantified; Z-2l structure remains machine-unverified."]
))

# Scheme 2 is a proposed mechanistic rationale, not a reported batch experiment.
evidence = [ev(3, "image"), ev(3)]
records.append(record(
    "scheme2_proposed_iodocyclization_mechanism", "Scheme 2", "mechanism", evidence,
    [participant("generic_allene", "reactant", "generic R-substituted allenyl acetylacetate", "generic substrate in Scheme 2", evidence),
     participant("int1", "unspecified_agent", "int1", "favored proposed iodonium intermediate", evidence),
     participant("int2", "unspecified_agent", "int2", "less-favored proposed iodonium intermediate", evidence),
     participant("generic_Z_product", "product", "Z", "proposed Z-4,5-dihydrofuran product", evidence),
     participant("generic_E_product", "product", "E", "proposed E-4,5-dihydrofuran product", evidence)],
    [], [],
    notes=["Proposed regioselective I2 interaction, deprotonation, and anti attack of the enolic oxygen; int1 is favored over int2 by steric reasoning."],
    unresolved=["Generic R group prevents assignment of complete structures; proposed intermediates are not isolated experiments."]
))

# Scheme 3 and the matching detailed procedures on pages 5--6.
couplings = [
    {
        "rid": "scheme3_suzuki_product3", "source": "Scheme 3 / product 3 procedure", "page": 6,
        "partner": ("phenylboronic_acid", "phenylboronic acid", 0.225, 27.1, 1.5),
        "cat": ("Pd(PPh3)4", 7.5, 8.5, 5.0), "base": ("K3PO4_3H2O", 0.3, 80.9, 2.0),
        "sub_mmol": 0.15, "sub_mg": 45.3, "solvent": "toluene", "volume": 1.5,
        "temp": 110, "time": (14, "h"), "prod": "3", "prod_name": "3-(Ethoxycarbonyl)-2-methyl-5-(1-phenylvinyl)-4,5-dihydrofuran",
        "prod_smiles": "CCOC(=O)C1=C(C)OC(C1)C(=C)c1ccccc1", "prod_mg": 31.1, "yield": 82,
        "eluent": "petroleum ether/ethyl acetate 20:1", "atmosphere": "argon",
    },
    {
        "rid": "scheme3_suzuki_product4", "source": "Scheme 3 / product 4 procedure", "page": 6,
        "partner": ("hexenylboronic_acid", "(1E)-hexenylboronic acid", 0.225, 29.2, 1.5),
        "cat": ("Pd(PPh3)4", 7.5, 9.0, 5.0), "base": ("K3PO4_3H2O", 0.3, 79.1, 2.0),
        "sub_mmol": 0.15, "sub_mg": 46.2, "solvent": "toluene", "volume": 1.5,
        "temp": 110, "time": (13.5, "h"), "prod": "4", "prod_name": "3-(Ethoxycarbonyl)-2-methyl-5-[octa-1,3(E)-dien-2-yl]-4,5-dihydrofuran",
        "prod_smiles": None, "prod_mg": 32.1, "yield": 81,
        "eluent": "petroleum ether/diethyl ether 25:1", "atmosphere": None,
    },
    {
        "rid": "scheme3_sonogashira_product5", "source": "Scheme 3 / product 5 procedure", "page": 6,
        "partner": ("1_hexyne", "1-hexyne", 0.4, 34.7, 2.0),
        "cat": ("Pd(PPh3)2Cl2", 6.0, 4.1, 3.0), "base": ("Et3N", 0.24, 24.8, 1.2),
        "sub_mmol": 0.2, "sub_mg": 60.5, "solvent": "CH3CN", "volume": 2.0,
        "temp": "r.t.", "time": (8, "h"), "prod": "5", "prod_name": "3-(Ethoxycarbonyl)-2-methyl-5-(oct-1-en-3-yn-2-yl)-4,5-dihydrofuran",
        "prod_smiles": "CCOC(=O)C1=C(C)OC(C1)C(=C)C#CCCCC", "prod_mg": 43.7, "yield": 84,
        "eluent": "petroleum ether/diethyl ether 40:1", "atmosphere": "argon",
    },
]
for c in couplings:
    evidence = [ev(3, "image"), ev(3), ev(c["page"], "image"), ev(c["page"])]
    if c["prod"] == "3":
        evidence += [ev(5, "image"), ev(5)]
    partner_id, partner_name, partner_mmol, partner_mg, partner_eq = c["partner"]
    cat_label, cat_umol, cat_mg, cat_molpct = c["cat"]
    base_label, base_mmol, base_mg, base_eq = c["base"]
    ps = [
        participant("2a", "reactant", "2a", PRODUCT_NAMES["2a"], evidence, PRODUCT_SMILES["2a"],
                    [amount("amount", c["sub_mmol"], "mmol", evidence), amount("mass", c["sub_mg"], "mg", evidence)]),
        participant(partner_id, "reactant", partner_name, partner_name, evidence, SIMPLE_SMILES.get(partner_id),
                    [amount("amount", partner_mmol, "mmol", evidence), amount("mass", partner_mg, "mg", evidence),
                     amount("equivalents", partner_eq, "equiv", evidence)]),
        participant("pd_catalyst", "catalyst", cat_label, cat_label, evidence, None,
                    [amount("amount", cat_umol, "umol", evidence), amount("mass", cat_mg, "mg", evidence),
                     amount("catalyst_loading", cat_molpct, "mol%", evidence)]),
        participant("base_or_coreagent", "reagent", base_label, base_label, evidence, SIMPLE_SMILES.get(base_label),
                    [amount("amount", base_mmol, "mmol", evidence), amount("mass", base_mg, "mg", evidence),
                     amount("equivalents", base_eq, "equiv", evidence)]),
        participant("solvent", "solvent", c["solvent"], c["solvent"], evidence, SIMPLE_SMILES.get(c["solvent"]),
                    [amount("volume", c["volume"], "mL", evidence)]),
        product(c["prod"], evidence, mg=c["prod_mg"], name=c["prod_name"], smiles=c["prod_smiles"]),
    ]
    # Sonogashira additionally contains CuI.
    if c["prod"] == "5":
        cui = small("CuI", "catalyst", evidence, mg=1.2, entity="cui")
        cui["amounts"].extend([amount("amount", 6.0, "umol", evidence), amount("catalyst_loading", 3.0, "mol%", evidence)])
        ps.insert(3, cui)
    records.append(record(
        c["rid"], c["source"], "reported_experiment", evidence, ps,
        [reaction_step("coupling", [p["entity_id"] for p in ps[:-1]], evidence,
                       solvent=c["solvent"], volume=c["volume"], temperature=c["temp"],
                       time=c["time"], atmosphere=c["atmosphere"]),
         reaction_step("purification", [c["prod"]], evidence,
                       purification=f"Concentrated and purified by silica-gel chromatography, {c['eluent']}.")],
        [field("isolated_yield", q(c["yield"], "%"), evidence, [c["prod"]]),
         field("yield_measurement_basis", "isolated after chromatography", evidence, [c["prod"]])],
        unresolved=(["Atmosphere is not restated for the product 4 abbreviated procedure."] if c["prod"] == "4" else [])
    ))


assert len(records) == 34, len(records)
OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
print(f"wrote {len(records)} records to {OUT}")
