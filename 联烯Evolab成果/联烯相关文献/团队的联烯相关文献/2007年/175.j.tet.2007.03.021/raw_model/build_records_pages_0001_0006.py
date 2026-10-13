#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "runs/current/raw_model"
DOC = "doc_36c1e591f611f19c"


def ev(page, kind="text"):
    return f"{DOC}:page{page}:{kind}"


def fact(value, evidence=()):
    return {
        "value": value,
        "evidence_ids": list(evidence),
        "verification": "missing" if value is None else "unreviewed",
    }


def qty(number, unit, raw_text=None, qualifier=None):
    value = {"number": number, "unit": unit}
    if raw_text is not None:
        value["raw_text"] = raw_text
    if qualifier is not None:
        value["qualifier"] = qualifier
    return value


def fld(name, value, evidence, targets=None):
    item = {"name": name, "fact": fact(value, evidence)}
    if targets:
        item["target_entity_ids"] = list(targets)
    return item


def amounts(evidence, *, mass=None, amount=None, volume=None, equivalents=None,
            mol_percent=None, isolated_mass=None):
    result = []
    for name, value in (
        ("mass", mass), ("amount", amount), ("volume", volume),
        ("equivalents", equivalents), ("loading", mol_percent),
        ("isolated_mass", isolated_mass),
    ):
        if value is not None:
            result.append(fld(name, value, evidence))
    return result


def participant(entity_id, role, label, name, evidence, smiles=None, amount_fields=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence) if label is not None else fact(None),
        "name": fact(name, evidence) if name is not None else fact(None),
        "smiles": fact(smiles, evidence) if smiles is not None else fact(None),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": amount_fields or [],
    }


def record(suffix, kind, evidence, participants, steps, outcomes, notes, unresolved):
    return {
        "record_id": f"{DOC}:{suffix}",
        "document_id": DOC,
        "source_reaction_id": suffix,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": list(dict.fromkeys(evidence)),
        "participants": participants,
        "steps": steps,
        "outcomes": outcomes,
        "notes": [fact(x, evidence) for x in notes],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved,
        },
    }


SMILES = {
    "allene1": "COC(=O)C=C=C",
    "2a": "OB(O)c1ccccc1",
    "2b": "OB(O)c1ccc(C)cc1",
    "2c": "OB(O)c1cc(C)cc(C)c1",
    "2d": "COc1ccc(B(O)O)cc1",
    "2e": "COc1cccc(B(O)O)c1",
    "3a": "O=Cc1ccccc1",
    "3f": "Cc1ccc(C=O)cc1",
    "3g": "O=Cc1ccc(Cl)cc1",
    "3h": "O=Cc1ccc(Br)cc1",
    "3i": "O=Cc1ccccc1Cl",
    "3j": "COc1ccc(C=O)cc1",
    "4a": "O=C1C=C(c2ccccc2)CC(c2ccccc2)O1",
    "4b": "O=C1C=C(c2ccc(C)cc2)CC(c2ccccc2)O1",
    "4c": "O=C1C=C(c2cc(C)cc(C)c2)CC(c2ccccc2)O1",
    "4d": "O=C1C=C(c2ccc(OC)cc2)CC(c2ccccc2)O1",
    "4e": "O=C1C=C(c2cccc(OC)c2)CC(c2ccccc2)O1",
    "4f": "O=C1C=C(c2ccccc2)CC(c2ccc(C)cc2)O1",
    "4g": "O=C1C=C(c2ccccc2)CC(c2ccc(Cl)cc2)O1",
    "4h": "O=C1C=C(c2ccccc2)CC(c2ccc(Br)cc2)O1",
    "4i": "O=C1C=C(c2ccccc2)CC(c2ccccc2Cl)O1",
    "4j": "O=C1C=C(c2ccccc2)CC(c2ccc(OC)cc2)O1",
    "4k": "O=C1C=C(c2ccc(OC)cc2)CC(c2ccc(OC)cc2)O1",
    "5a": "COC(=O)C=C(c1ccccc1)CC(O)c1ccccc1",
    "5d": "COC(=O)C=C(c1ccc(OC)cc1)CC(O)c1ccccc1",
    "PPh3": "P(c1ccccc1)(c1ccccc1)c1ccccc1",
    "water": "O",
    "THF": "C1CCOC1",
    "dioxane": "O1CCOCC1",
    "KF": "[K+].[F-]",
    "LiF": "[Li+].[F-]",
    "NaF": "[Na+].[F-]",
    "CsF": "[Cs+].[F-]",
    "Cs2CO3": "[Cs+].[Cs+].[O-]C([O-])=O",
}

PRODUCT_NAMES = {
    "4a": "4,6-diphenyl-5,6-dihydropyran-2-one",
    "4b": "6-phenyl-4-(4-tolyl)-5,6-dihydropyran-2-one",
    "4c": "4-(3,5-dimethylphenyl)-6-phenyl-5,6-dihydropyran-2-one",
    "4d": "4-(4-methoxyphenyl)-6-phenyl-5,6-dihydropyran-2-one",
    "4e": "4-(3-methoxyphenyl)-6-phenyl-5,6-dihydropyran-2-one",
    "4f": "4-phenyl-6-(4-tolyl)-5,6-dihydropyran-2-one",
    "4g": "6-(4-chlorophenyl)-4-phenyl-5,6-dihydropyran-2-one",
    "4h": "6-(4-bromophenyl)-4-phenyl-5,6-dihydropyran-2-one",
    "4i": "6-(2-chlorophenyl)-4-phenyl-5,6-dihydropyran-2-one",
    "4j": "6-(4-methoxyphenyl)-4-phenyl-5,6-dihydropyran-2-one",
    "4k": "4,6-bis(4-methoxyphenyl)-5,6-dihydropyran-2-one",
}


def simple_reactants(evidence, boronic_label="2a", boronic_name="phenylboronic acid",
                     aldehyde_label="3a", aldehyde_name="benzaldehyde"):
    return [
        participant("allene1", "reactant", "1", "methyl 2,3-butadienoate", evidence, SMILES["allene1"]),
        participant("boronic", "reactant", boronic_label, boronic_name, evidence, SMILES[boronic_label]),
        participant("aldehyde", "reactant", aldehyde_label, aldehyde_name, evidence, SMILES[aldehyde_label]),
    ]


records = []


OPT_ROWS = {
    1: dict(catalyst="RhCl(PPh3)3", pph3=None, ratio="1:2:2", base="Cs2CO3", base_eq=0.5, water_eq=2, y=8),
    2: dict(catalyst="RhCl(PPh3)3", pph3=2.5, ratio="1:2:2", base="Cs2CO3", base_eq=0.5, water_eq=4, y=33),
    3: dict(catalyst="[RhCl(COD)]2", pph3=10, ratio="1:2:2", base="Cs2CO3", base_eq=2, water_eq=4, y="Trace"),
    4: dict(catalyst="[RhCl(COD)]2", pph3=10, ratio="1:2:2", base="KF", base_eq=2, water_eq=4, y=31),
    5: dict(catalyst="[RhCl(COD)]2", pph3=10, ratio="1:2:2", base="KF", base_eq=2, water_eq=None, y=2),
    6: dict(catalyst="RhCl(PPh3)3", pph3=None, ratio="2:1:4", base="KF", base_eq=2, water_eq=4, y=18),
    7: dict(catalyst="[RhCl(COD)]2", pph3=10, ratio="2:1:4", base="KF", base_eq=2, water_eq=4, y=59),
    8: dict(catalyst="[RhCl(COD)]2", pph3=10, ratio="2:1:4", base="LiF", base_eq=2, water_eq=4, y="Trace"),
    9: dict(catalyst="[RhCl(COD)]2", pph3=10, ratio="2:1:4", base="NaF", base_eq=2, water_eq=4, y="Trace"),
    10: dict(catalyst="[RhCl(COD)]2", pph3=10, ratio="2:1:4", base="CsF", base_eq=2, water_eq=4, y=15),
    11: dict(catalyst="[RhCl(COD)]2", pph3=20, ratio="2:1:4", base="KF", base_eq=2, water_eq=4, y=26),
    12: dict(catalyst="[RhCl(COD)]2", pph3=10, ratio="2:1:4", base="KF", base_eq=2, water_eq=4,
             y=qty(5, "%", "<5%", "lt"), solvent="dioxane", temperature=80),
}


for entry, row in OPT_ROWS.items():
    evidence = [ev(2, "image"), ev(2)]
    if entry in (1, 2, 5, 6, 7, 11, 12):
        evidence += [ev(1, "image"), ev(1)]
    parts = simple_reactants(evidence)
    parts.append(participant("product4a", "product", "4a", PRODUCT_NAMES["4a"], evidence, SMILES["4a"]))
    if entry in (1, 2, 5):
        parts.append(participant("product5a", "product", "5a", "methyl 5-hydroxy-3,5-diphenylpent-2(E)-enoate", evidence, SMILES["5a"]))
    cat_amounts = amounts(evidence, mol_percent=qty(5, "mol%"))
    parts.append(participant("catalyst", "catalyst", row["catalyst"], row["catalyst"], evidence, None, cat_amounts))
    if row["pph3"] is not None:
        parts.append(participant("pph3", "reagent", "PPh3", "triphenylphosphine", evidence, SMILES["PPh3"],
                                 amounts(evidence, mol_percent=qty(row["pph3"], "mol%"))))
    parts.append(participant("base", "reagent", row["base"], row["base"], evidence, SMILES[row["base"]],
                             amounts(evidence, equivalents=qty(row["base_eq"], "equiv"))))
    if row["water_eq"] is not None:
        parts.append(participant("water", "reagent", "H2O", "water", evidence, SMILES["water"],
                                 amounts(evidence, equivalents=qty(row["water_eq"], "equiv"))))
    solvent = row.get("solvent", "THF")
    parts.append(participant("solvent", "solvent", solvent, "1,4-dioxane" if solvent == "dioxane" else "tetrahydrofuran",
                             evidence, SMILES[solvent]))
    conditions = [
        fld("stoichiometric_proportion_1_2a_3a", row["ratio"], evidence),
        fld("solvent", solvent, evidence),
        fld("temperature", qty(row.get("temperature", 60), "°C"), evidence),
        fld("time", "overnight", evidence),
        fld("atmosphere", "N2", evidence),
    ]
    outcomes = [fld("isolated_yield_4a", qty(row["y"], "%") if isinstance(row["y"], int) else row["y"],
                    evidence, ["product4a"]),
                fld("yield_measurement_basis", "isolated", evidence, ["product4a"])]
    notes = []
    unresolved = [
        "Workup and purification are not reported for this optimization row unless merged with the detailed 4a preparation.",
        "All candidate structures are unverified.",
    ]
    if entry == 1:
        outcomes += [
            fld("contaminant_5a_percentage", qty(17, "%"), evidence, ["product5a"]),
            fld("4a_to_5a_ratio", "1:2.1", evidence, ["product4a", "product5a"]),
        ]
        notes.append("The 4a/5a mixture could not be separated by silica-gel chromatography.")
    if entry == 2:
        outcomes.append(fld("5a_formation", "not observed", evidence, ["product5a"]))
    if entry == 5:
        outcomes.append(fld("contaminant_5a_percentage", qty(20, "%"), evidence, ["product5a"]))
        notes.append("Footnote e overrides the table header: the reaction was conducted without water.")
    if entry == 7:
        e3 = [ev(3, "image"), ev(3)]
        evidence += e3
        exact = {
            "allene1": amounts(e3, mass=qty(51, "mg"), amount=qty(0.52, "mmol")),
            "boronic": amounts(e3, mass=qty(31, "mg"), amount=qty(0.25, "mmol")),
            "aldehyde": amounts(e3, mass=qty(104, "mg"), amount=qty(1.02, "mmol"), volume=qty(100, "uL")),
            "catalyst": amounts(e3, mass=qty(3, "mg"), amount=qty(0.006, "mmol"), mol_percent=qty(2.5, "mol%")),
            "pph3": amounts(e3, mass=qty(7, "mg"), amount=qty(0.027, "mmol"), mol_percent=qty(10, "mol%")),
            "base": amounts(e3, mass=qty(29, "mg"), amount=qty(0.50, "mmol"), equivalents=qty(2, "equiv")),
            "water": amounts(e3, mass=qty(18, "mg"), amount=qty(1.00, "mmol"), volume=qty(18, "uL"), equivalents=qty(4, "equiv")),
            "solvent": amounts(e3, volume=qty(3, "mL")),
            "product4a": amounts(e3, isolated_mass=qty(36, "mg")),
        }
        for p in parts:
            if p["entity_id"] in exact:
                p["amounts"] = exact[p["entity_id"]]
        conditions += [
            fld("general_procedure_atmosphere", "argon", e3),
            fld("monitoring", "TLC until complete consumption of starting material", e3),
            fld("workup", "solvent evaporated", e3),
            fld("purification", "flash chromatography on silica gel (petroleum ether/diethyl ether)", e3),
        ]
        unresolved = [
            "Table 1 states N2/overnight, whereas the general experimental procedure states argon/TLC until complete consumption.",
            "Candidate product connectivity is unverified.",
        ]
    records.append(record(f"table1_entry{entry}", "optimization_entry", evidence, parts,
                          [{"step_id": "reaction", "participant_ids": [p["entity_id"] for p in parts if p["role"] != "product"],
                            "conditions": conditions}], outcomes, notes, unresolved))


SCOPE = [
    dict(entry=1, prod="4b", bor="2b", bor_name="4-tolylboronic acid", ald="3a", ald_name="benzaldehyde", page=4,
         bm=33, bmm=0.24, am=73, amm=0.74, av=100, alm=104, almm=1.02, base="KF", basem=30, basemm=0.52,
         pm=6, pmm=0.023, wm=18, wmm=1.00, wv=18, prodm=32, y=50, allene_eq=3),
    dict(entry=2, prod="4c", bor="2c", bor_name="3,5-dimethylphenylboronic acid", ald="3a", ald_name="benzaldehyde", page=4,
         bm=37, bmm=0.25, am=73, amm=0.74, av=100, alm=104, almm=1.02, base="KF", basem=30, basemm=0.52,
         pm=7, pmm=0.027, wm=18, wmm=1.00, wv=18, prodm=34, y=50, allene_eq=3),
    dict(entry=3, prod="4d", bor="2d", bor_name="4-methoxyphenylboronic acid", ald="3a", ald_name="benzaldehyde", page=4,
         bm=38, bmm=0.25, am=75, amm=0.74, av=100, alm=104, almm=1.02, base="CsF", basem=75, basemm=0.49,
         pm=6, pmm=0.023, wm=18, wmm=1.00, wv=18, prodm=36, y=51, allene_eq=2),
    dict(entry=4, prod="4e", bor="2e", bor_name="3-methoxyphenylboronic acid", ald="3a", ald_name="benzaldehyde", page=4,
         bm=37, bmm=0.24, am=52, amm=0.53, av=100, alm=104, almm=1.02, base="KF", basem=31, basemm=0.50,
         pm=7, pmm=0.027, wm=18, wmm=1.00, wv=18, prodm=31, y=45, allene_eq=2),
    dict(entry=5, prod="4f", bor="2a", bor_name="phenylboronic acid", ald="3f", ald_name="4-methylbenzaldehyde", page=4,
         bm=30, bmm=0.25, am=53, amm=0.54, av=118, alm=120, almm=1.00, base="KF", basem=28, basemm=0.48,
         pm=6, pmm=0.023, wm=18, wmm=1.00, wv=18, prodm=36, y=55, allene_eq=2),
    dict(entry=6, prod="4g", bor="2a", bor_name="phenylboronic acid", ald="3g", ald_name="4-chlorobenzaldehyde", page=4,
         bm=30, bmm=0.25, am=75, amm=0.77, av=None, alm=144, almm=1.02, base="KF", basem=30, basemm=0.52,
         pm=6, pmm=0.023, wm=18, wmm=1.00, wv=18, prodm=34, y=49, allene_eq=3),
    dict(entry=7, prod="4h", bor="2a", bor_name="phenylboronic acid", ald="3h", ald_name="4-bromobenzaldehyde", page=4,
         bm=30, bmm=0.25, am=50, amm=0.51, av=None, alm=184, almm=0.99, base="KF", basem=29, basemm=0.50,
         pm=7, pmm=0.027, wm=18, wmm=1.00, wv=18, prodm=40, y=50, allene_eq=2),
    dict(entry=8, prod="4i", bor="2a", bor_name="phenylboronic acid", ald="3i", ald_name="2-chlorobenzaldehyde", page=5,
         bm=30, bmm=0.25, am=78, amm=0.80, av=112, alm=140, almm=1.00, base="KF", basem=30, basemm=0.52,
         pm=6, pmm=0.023, wm=18, wmm=1.00, wv=18, prodm=36, y=51, allene_eq=3),
    dict(entry=9, prod="4j", bor="2a", bor_name="phenylboronic acid", ald="3j", ald_name="4-methoxybenzaldehyde", page=5,
         bm=31, bmm=0.25, am=98, amm=1.00, av=121, alm=136, almm=1.00, base="KF", basem=28, basemm=0.48,
         pm=6, pmm=0.023, wm=18, wmm=1.00, wv=18, prodm=38, y=54, allene_eq=4),
    dict(entry=10, prod="4k", bor="2d", bor_name="4-methoxyphenylboronic acid", ald="3j", ald_name="4-methoxybenzaldehyde", page=5,
         bm=38, bmm=0.25, am=53, amm=0.54, av=120, alm=136, almm=1.00, base="KF", basem=29, basemm=0.50,
         pm=7, pmm=0.027, wm=18, wmm=1.00, wv=18, prodm=32, y=42, allene_eq=2),
]


for row in SCOPE:
    p = row["page"]
    evidence = [ev(2, "image"), ev(2), ev(3, "image"), ev(3), ev(p, "image"), ev(p)]
    ps = simple_reactants(evidence, row["bor"], row["bor_name"], row["ald"], row["ald_name"])
    ps[0]["amounts"] = amounts(evidence, mass=qty(row["am"], "mg"), amount=qty(row["amm"], "mmol"),
                                  equivalents=qty(row["allene_eq"], "equiv"))
    ps[1]["amounts"] = amounts(evidence, mass=qty(row["bm"], "mg"), amount=qty(row["bmm"], "mmol"),
                                  equivalents=qty(1, "equiv"))
    ps[2]["amounts"] = amounts(evidence, mass=qty(row["alm"], "mg"), amount=qty(row["almm"], "mmol"),
                                  volume=qty(row["av"], "uL") if row["av"] is not None else None,
                                  equivalents=qty(4, "equiv"))
    ps += [
        participant("base", "reagent", row["base"], row["base"], evidence, SMILES[row["base"]],
                    amounts(evidence, mass=qty(row["basem"], "mg"), amount=qty(row["basemm"], "mmol"), equivalents=qty(2, "equiv"))),
        participant("catalyst", "catalyst", "[RhCl(COD)]2", "[RhCl(COD)]2", evidence, None,
                    amounts(evidence, mass=qty(3, "mg"), amount=qty(0.006, "mmol"), mol_percent=qty(2.5, "mol%"))),
        participant("pph3", "reagent", "PPh3", "triphenylphosphine", evidence, SMILES["PPh3"],
                    amounts(evidence, mass=qty(row["pm"], "mg"), amount=qty(row["pmm"], "mmol"), mol_percent=qty(10, "mol%"))),
        participant("water", "reagent", "H2O", "water", evidence, SMILES["water"],
                    amounts(evidence, mass=qty(row["wm"], "mg"), amount=qty(row["wmm"], "mmol"),
                            volume=qty(row["wv"], "uL"), equivalents=qty(4, "equiv"))),
        participant("thf", "solvent", "THF", "anhydrous tetrahydrofuran", evidence, SMILES["THF"],
                    amounts(evidence, volume=qty(3, "mL"))),
        participant("product", "product", row["prod"], PRODUCT_NAMES[row["prod"]], evidence, SMILES[row["prod"]],
                    amounts(evidence, isolated_mass=qty(row["prodm"], "mg"))),
    ]
    conditions = [
        fld("table_atmosphere", "N2", evidence),
        fld("general_procedure_atmosphere", "argon", evidence),
        fld("temperature", qty(60, "°C"), evidence),
        fld("time", "overnight", evidence),
        fld("monitoring", "TLC until complete consumption of starting material", evidence),
        fld("workup", "solvent evaporated", evidence),
        fld("purification", "flash chromatography on silica gel (petroleum ether/diethyl ether)", evidence),
    ]
    outcomes = [
        fld(f"isolated_yield_{row['prod']}", qty(row["y"], "%"), evidence, ["product"]),
        fld("yield_measurement_basis", "isolated", evidence, ["product"]),
    ]
    unresolved = [
        "Table 2 states N2/overnight, whereas the general experimental procedure states argon/TLC until complete consumption.",
        "The candidate product structure and stereochemistry are unverified.",
    ]
    records.append(record(f"table2_entry{row['entry']}_{row['prod']}", "substrate_scope_entry", evidence, ps,
                          [{"step_id": "reaction_and_isolation", "participant_ids": [x["entity_id"] for x in ps if x["role"] != "product"],
                            "conditions": conditions}], outcomes, [], unresolved))


e56 = [ev(5, "image"), ev(5), ev(6, "image"), ev(6)]
parts = [
    participant("allene1", "reactant", "1", "methyl 2,3-butadienoate", e56, SMILES["allene1"],
                amounts(e56, mass=qty(125, "mg"), amount=qty(1.28, "mmol"))),
    participant("boronic2d", "reactant", "2d", "4-methoxyphenylboronic acid", e56, SMILES["2d"],
                amounts(e56, mass=qty(381, "mg"), amount=qty(2.51, "mmol"), equivalents=qty(2, "equiv"))),
    participant("aldehyde3a", "reactant", "3a", "benzaldehyde", e56, SMILES["3a"],
                amounts(e56, mass=qty(265, "mg"), amount=qty(2.50, "mmol"), volume=qty(250, "uL"), equivalents=qty(2, "equiv"))),
    participant("catalyst", "catalyst", "RhCl(PPh3)3", "chlorotris(triphenylphosphine)rhodium(I)", e56, None,
                amounts(e56, mass=qty(60, "mg"), amount=qty(0.06, "mmol"), mol_percent=qty(5, "mol%"))),
    participant("base", "reagent", "Cs2CO3", "cesium carbonate", e56, SMILES["Cs2CO3"],
                amounts(e56, mass=qty(200, "mg"), amount=qty(0.61, "mmol"), equivalents=qty(0.5, "equiv"))),
    participant("water", "reagent", "H2O", "water", e56, SMILES["water"],
                amounts(e56, mass=qty(45, "mg"), amount=qty(2.50, "mmol"), volume=qty(45, "uL"), equivalents=qty(2, "equiv"))),
    participant("thf", "solvent", "THF", "anhydrous tetrahydrofuran", e56, SMILES["THF"], amounts(e56, volume=qty(15, "mL"))),
    participant("product4d", "product", "4d", PRODUCT_NAMES["4d"], e56, SMILES["4d"], amounts(e56, isolated_mass=qty(45, "mg"))),
    participant("product5d", "product", "5d", "methyl 5-hydroxy-3-(4-methoxyphenyl)-5-phenylpent-2(E)-enoate", e56,
                SMILES["5d"], amounts(e56, isolated_mass=qty(72, "mg"))),
]
records.append(record("section4_2_4d_5d", "reported_experiment", e56, parts,
                      [{"step_id": "reaction", "participant_ids": [x["entity_id"] for x in parts if x["role"] != "product"],
                        "conditions": [fld("temperature", qty(60, "°C"), e56), fld("time", "overnight", e56)]}],
                      [fld("reported_yield_4d", qty(13, "%"), e56, ["product4d"]),
                       fld("reported_yield_5d", qty(19, "%"), e56, ["product5d"])],
                      ["4d was reported as a white solid and 5d as a colorless oil.",
                       "The (E)-assignment for 5d is supported by the reported NOE analysis in note 20."],
                      ["Atmosphere, workup, purification, and yield measurement basis are not reported for this experiment.",
                       "The candidate structure and E stereochemistry of 5d are unverified."]))


e23 = [ev(2, "image"), ev(2), ev(3, "image"), ev(3)]
mechanism_parts = [
    participant("rh_oh", "catalyst", "I", "rhodium hydroxide active species Rh(OH)Ln", e23),
    participant("aryl_rh", "unspecified_agent", "II", "arylrhodium intermediate", e23),
    participant("allene1", "reactant", "1", "methyl 2,3-butadienoate", e23, SMILES["allene1"]),
    participant("allyl_rh", "unspecified_agent", "III", "pi-allyl rhodium intermediate", e23),
    participant("aldehyde", "reactant", "RCHO", "aldehyde", e23),
    participant("alkoxide_rh", "unspecified_agent", "IV", "rhodium alkoxide intermediate", e23),
    participant("product4", "product", "4", "alpha,beta-unsaturated delta-lactone", e23),
]
records.append(record("scheme1_proposed_catalytic_cycle", "mechanism", e23, mechanism_parts, [], [],
                      ["Proposed sequence: transmetalation, allenoate carborhodiation, aldehyde insertion, hydrolysis/lactonization, and catalyst regeneration.",
                       "The authors state that water may assist formation of the active species and cyclization."],
                      ["This is a proposed mechanism, not a separately executed experiment.",
                       "Generic Ar/R/Ln structures and organorhodium intermediates remain unverified."]))


assert len(records) == 24, len(records)
OUT.mkdir(parents=True, exist_ok=True)
(OUT / "records_pages_0001_0006.json").write_text(json.dumps(records, ensure_ascii=False, indent=2))

opt_ids = [f"{DOC}:table1_entry{i}" for i in range(1, 13)]
scope_ids = [f"{DOC}:table2_entry{x['entry']}_{x['prod']}" for x in SCOPE]
mech_id = f"{DOC}:scheme1_proposed_catalytic_cycle"
section_id = f"{DOC}:section4_2_4d_5d"
coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {"page": 1, "state": "attempted", "regions": [
            {"region": "title, abstract, introduction, and lower-right Results and discussion prose",
             "finding": "No row-level arrow or table is printed; prose describes the present reaction and corroborates selected Table 1 outcomes, including 4a/5a formation, catalyst/base effects, and the optimized 59% result.",
             "evidence_ids": [ev(1, "image"), ev(1)]}],
         "record_ids": [opt_ids[i-1] for i in (1, 2, 5, 6, 7, 11, 12)],
         "unresolved": ["Abstract-level claims were not duplicated as experiments; detailed rows appear on later pages."]},
        {"page": 2, "state": "attempted", "regions": [
            {"region": "upper half, Table 1 and footnotes",
             "finding": "All 12 optimization rows were extracted independently; water, solvent/temperature, contamination, absence-of-water, and isolated-yield footnotes were applied only to the specified rows.",
             "evidence_ids": [ev(2, "image"), ev(2)]},
            {"region": "lower half, Table 2 and footnotes",
             "finding": "All 10 substrate-scope rows were extracted independently and linked to their later compound-specific preparations; allene-equivalent and CsF overrides were retained.",
             "evidence_ids": [ev(2, "image"), ev(2)]},
            {"region": "middle-right mechanism discussion",
             "finding": "Opening text of the proposed catalytic cycle was classified as mechanism, not as an executed reaction.",
             "evidence_ids": [ev(2, "image"), ev(2)]}],
         "record_ids": opt_ids + scope_ids + [mech_id],
         "unresolved": ["Table 2 states N2/overnight while the page-3 general procedure states argon/TLC until complete consumption.",
                        "Aliphatic-aldehyde yields are described only as very low, without row-level data."]},
        {"page": 3, "state": "attempted", "regions": [
            {"region": "upper-left Figure 1", "finding": "ORTEP drawing supports the structure assignment of 4c and was linked to Table 2 entry 2; it is not a reaction.",
             "evidence_ids": [ev(3, "image"), ev(3)]},
            {"region": "upper-right Scheme 1 and adjacent prose", "finding": "Proposed Rh catalytic cycle classified as a mechanism record.",
             "evidence_ids": [ev(3, "image"), ev(3)]},
            {"region": "lower-left Table 3", "finding": "Non-aromatic 1H NMR data for 4a–4k; characterization only, so no new reaction records were created.",
             "evidence_ids": [ev(3, "image"), ev(3)]},
            {"region": "lower-right general procedure and 4a preparation", "finding": "General workup/purification and exact 4a quantities were merged into Table 1 entry 7, the same optimized experiment.",
             "evidence_ids": [ev(3, "image"), ev(3)]}],
         "record_ids": [opt_ids[6]] + scope_ids + [mech_id],
         "unresolved": ["Table 1 gives N2/overnight whereas the general procedure gives argon/TLC completion.",
                        "The printed general procedure uses the unusual text '2.5 mmol %'; Table 2 and exact quantities support a 2.5 mol% catalyst-loading interpretation."]},
        {"page": 4, "state": "attempted", "regions": [
            {"region": "two-column experimental sections 4.1.2–4.1.8 and start of 4.1.9",
             "finding": "Exact preparations of 4b–4h were merged into Table 2 entries 1–7; the cross-page 4i heading begins here and its full preparation continues on page 5.",
             "evidence_ids": [ev(4, "image"), ev(4)]}],
         "record_ids": scope_ids[:8],
         "unresolved": ["Compound characterization was retained as supporting context but not exhaustively decomposed into reaction-condition fields."]},
        {"page": 5, "state": "attempted", "regions": [
            {"region": "left column and upper-right, experimental sections 4.1.9–4.1.11",
             "finding": "Exact preparations of 4i–4k were merged into Table 2 entries 8–10.",
             "evidence_ids": [ev(5, "image"), ev(5)]},
            {"region": "lower-left section 4.2 continuing to upper-right",
             "finding": "A distinct RhCl(PPh3)3/Cs2CO3 experiment giving both 4d and 5d was extracted with exact quantities, product masses, and reported yields.",
             "evidence_ids": [ev(5, "image"), ev(5)]},
            {"region": "Supplementary data statement and references",
             "finding": "Online supplementary data are mentioned but no SI file is supplied or explicitly associated; references were not treated as present-paper experiments.",
             "evidence_ids": [ev(5, "image"), ev(5)]}],
         "record_ids": scope_ids[7:] + [section_id],
         "unresolved": ["The section-4.2 experiment does not state atmosphere, workup, purification, or yield basis.",
                        "SI association remains unestablished."]},
        {"page": 6, "state": "attempted", "regions": [
            {"region": "center-right graphical equation and note 20",
             "finding": "Graphical restatement of the section-4.2 4d/5d experiment supplies 60 °C/overnight and reagent-equivalent context; it was merged rather than duplicated. Note 20 reports the NOE basis for the (E)-5d assignment.",
             "evidence_ids": [ev(6, "image"), ev(6)]},
            {"region": "remaining reference list and crystallographic note",
             "finding": "Citations and crystal data are contextual/characterization material, not new present-paper reaction experiments.",
             "evidence_ids": [ev(6, "image"), ev(6)]}],
         "record_ids": [section_id],
         "unresolved": ["No associated SI or CCDC file was supplied.",
                        "The 5d stereochemical candidate remains unverified despite the reported NOE assignment."]},
    ],
}
cov_dir = ROOT / "runs/current/coverage"
cov_dir.mkdir(parents=True, exist_ok=True)
(cov_dir / "pages_0001_0006.json").write_text(json.dumps(coverage, ensure_ascii=False, indent=2))

tasks_path = ROOT / "runs/current/tasks.json"
tasks = json.loads(tasks_path.read_text())
for task in tasks:
    if task.get("document_id") == DOC and task.get("evidence_id") in {ev(i) for i in range(1, 7)}:
        task["state"] = "attempted"
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2))
print(json.dumps({"records": len(records), "coverage_pages": len(coverage["pages"])}, ensure_ascii=False))
