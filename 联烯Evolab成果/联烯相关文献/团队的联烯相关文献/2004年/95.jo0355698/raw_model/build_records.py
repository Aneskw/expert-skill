import json
from pathlib import Path

DOC = "doc_dec2ba220ab9ef2a"
P1T, P1I = f"{DOC}:page1:text", f"{DOC}:page1:image"
P2T, P2I = f"{DOC}:page2:text", f"{DOC}:page2:image"
P3T, P3I = f"{DOC}:page3:text", f"{DOC}:page3:image"


def fact(value, ev):
    return {"value": value, "evidence_ids": list(ev),
            "verification": "missing" if value is None else "unreviewed"}


def fld(name, value, ev, targets=None):
    out = {"name": name, "fact": fact(value, ev)}
    if targets:
        out["target_entity_ids"] = list(targets)
    return out


def part(entity_id, role, ev, label=None, name=None, smiles=None, amounts=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, ev),
        "name": fact(name, ev),
        "smiles": fact(smiles, ev),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": amounts or [],
    }


def rec(rid, kind, ev, participants, steps, outcomes=None, notes=None, unresolved=None):
    return {
        "record_id": f"{DOC}:{rid}",
        "document_id": DOC,
        "source_reaction_id": rid,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": list(ev),
        "participants": participants,
        "steps": steps,
        "outcomes": outcomes or [],
        "notes": [fact(x, ev) for x in (notes or [])],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved or [
                "Supporting information was not provided or explicitly associated; procedural details remain incomplete."
            ],
        },
    }


def q(number, unit, raw_text=None):
    out = {"number": number, "unit": unit}
    if raw_text:
        out["raw_text"] = raw_text
    return out


def step(step_id, participant_ids, conditions):
    return {"step_id": step_id, "participant_ids": participant_ids,
            "conditions": conditions}


def common_solvents(ev, ratio="2:1"):
    return [
        part("thf", "solvent", ev, name="tetrahydrofuran", smiles="C1CCOC1"),
        part("dmf", "solvent", ev, name="N,N-dimethylformamide", smiles="CN(C)C=O"),
    ]


substrates = {
    "1a": ("2-methyl-4-phenyl-2,3-butadienoic acid", "O=C(O)C(C)=C=Cc1ccccc1"),
    "1b": ("2-propyl-4-phenyl-2,3-butadienoic acid", "O=C(O)C(CCC)=C=Cc1ccccc1"),
    "1c": ("2-benzyl-4-phenyl-2,3-butadienoic acid", "O=C(O)C(Cc1ccccc1)=C=Cc2ccccc2"),
    "1d": ("2-butyl-4-(4-methoxyphenyl)-2,3-butadienoic acid", "O=C(O)C(CCCC)=C=Cc1ccc(OC)cc1"),
    "1e": ("2-butyl-4-(4-fluorophenyl)-2,3-butadienoic acid", "O=C(O)C(CCCC)=C=Cc1ccc(F)cc1"),
    "1f": ("2-butyl-4-(4-isopropylphenyl)-2,3-butadienoic acid", "O=C(O)C(CCCC)=C=Cc1ccc(C(C)C)cc1"),
    "1g": ("2-butyl-4-(4-methylphenyl)-2,3-butadienoic acid", "O=C(O)C(CCCC)=C=Cc1ccc(C)cc1"),
    "1h": ("2-methyl-4-(1-naphthyl)-2,3-butadienoic acid", "O=C(O)C(C)=C=Cc1cccc2ccccc12"),
    "1i": ("2-propyl-4-(1-naphthyl)-2,3-butadienoic acid", "O=C(O)C(CCC)=C=Cc1cccc2ccccc12"),
}

iodoproducts = {
    "2a": ("3-methyl-4-iodo-5-phenyl-5-hydroxyfuran-2(5H)-one", "O=C1OC(O)(c2ccccc2)C(I)=C1C"),
    "2b": ("3-propyl-4-iodo-5-phenyl-5-hydroxyfuran-2(5H)-one", "O=C1OC(O)(c2ccccc2)C(I)=C1CCC"),
    "2c": ("3-benzyl-4-iodo-5-phenyl-5-hydroxyfuran-2(5H)-one", "O=C1OC(O)(c2ccccc2)C(I)=C1Cc3ccccc3"),
    "2d": ("3-butyl-4-iodo-5-(4-methoxyphenyl)-5-hydroxyfuran-2(5H)-one", "O=C1OC(O)(c2ccc(OC)cc2)C(I)=C1CCCC"),
    "2e": ("3-butyl-4-iodo-5-(4-fluorophenyl)-5-hydroxyfuran-2(5H)-one", "O=C1OC(O)(c2ccc(F)cc2)C(I)=C1CCCC"),
    "2f": ("3-butyl-4-iodo-5-(4-isopropylphenyl)-5-hydroxyfuran-2(5H)-one", "O=C1OC(O)(c2ccc(C(C)C)cc2)C(I)=C1CCCC"),
    "2g": ("3-butyl-4-iodo-5-(4-methylphenyl)-5-hydroxyfuran-2(5H)-one", "O=C1OC(O)(c2ccc(C)cc2)C(I)=C1CCCC"),
    "2h": ("3-methyl-4-iodo-5-(1-naphthyl)-5-hydroxyfuran-2(5H)-one", "O=C1OC(O)(c2cccc3ccccc23)C(I)=C1C"),
    "2i": ("3-propyl-4-iodo-5-(1-naphthyl)-5-hydroxyfuran-2(5H)-one", "O=C1OC(O)(c2cccc3ccccc23)C(I)=C1CCC"),
}


records = []

# Page 1: conceptual scheme and the cinchonidine-salt observation.
records.append(rec(
    "scheme1_general", "general_scheme", [P1T, P1I],
    [part("generic_allenoic_acid", "reactant", [P1I], label="4-aryl-2,3-allenoic acid (R1/R2 generic)"),
     part("generic_halobutenolide", "product", [P1I], label="4-halobutenolide intermediate (R1/R2/X generic)"),
     part("generic_hydroxy_product", "product", [P1I], label="4-halo-5-hydroxyfuran-2(5H)-one (R1/R2/X generic)")],
    [step("cyclization", ["generic_allenoic_acid", "generic_halobutenolide"], []),
     step("gamma_hydroxylation", ["generic_halobutenolide", "generic_hydroxy_product"], [])],
    notes=["Scheme 1 is a conceptual/general transformation and is not an individual reported experiment."],
    unresolved=["R1, R2 and X are generic groups; no unique structures or experimental conditions are specified in Scheme 1."]
))

records.append(rec(
    "eq1_cinchonidine_salt", "reported_experiment", [P1T, P1I],
    [part("eq1_1aa", "reactant", [P1I], label="1aa", name="1:1 salt of (L)-(-)-cinchonidine with 2-methyl-4-phenyl-2,3-butadienoic acid"),
     part("eq1_i2", "reagent", [P1I], name="iodine", smiles="II", amounts=[fld("equivalents", q(1.1, "equiv"), [P1I])]),
     *common_solvents([P1I], "3:1"),
     part("eq1_2a", "product", [P1I], label="2a", name=iodoproducts["2a"][0], smiles=iodoproducts["2a"][1])],
    [step("eq1", ["eq1_1aa", "eq1_i2", "thf", "dmf", "eq1_2a"],
          [fld("solvent", "THF/DMF (3:1)", [P1I]), fld("reaction_time", "overnight", [P1I])])],
    [fld("yield", q(84, "%"), [P1I], ["eq1_2a"]),
     fld("yield_measurement_basis", None, [], ["eq1_2a"])],
    notes=["The text identifies the product as racemic 2a."],
    unresolved=["Reaction temperature, atmosphere, workup, purification, numerical duration of 'overnight', and yield basis are not reported here; the full cinchonidine salt structure is not drawn."]
))

# Page 1-to-2 base screen: each explicitly named base is a separate failed optimization condition.
bases = [
    ("naoh", "sodium hydroxide", "[Na+].[OH-]"),
    ("k2co3", "potassium carbonate", "[K+].[K+].[O-]C([O-])=O"),
    ("na2co3", "sodium carbonate", "[Na+].[Na+].[O-]C([O-])=O"),
    ("cs2co3", "cesium carbonate", "[Cs+].[Cs+].[O-]C([O-])=O"),
    ("li2co3", "lithium carbonate", "[Li+].[Li+].[O-]C([O-])=O"),
    ("naoac", "sodium acetate", "[Na+].CC(=O)[O-]"),
    ("et3n", "triethylamine", "CCN(CC)CC"),
    ("pyridine", "pyridine", "n1ccccc1"),
]
for slug, base_name, base_smiles in bases:
    ev = [P1T, P1I, P2T, P2I]
    records.append(rec(
        f"base_screen_{slug}", "optimization_entry", ev,
        [part("screen_1a", "reactant", ev, label="1a", name=substrates["1a"][0], smiles=substrates["1a"][1]),
         part(f"screen_{slug}", "unspecified_agent", ev, name=base_name, smiles=base_smiles),
         *common_solvents(ev),
         part("screen_mixture", "product", ev, name="complicated products (unspecified mixture)")],
        [step("base_screen", ["screen_1a", f"screen_{slug}", "thf", "dmf", "screen_mixture"],
              [fld("solvent", "THF/DMF (2:1)", ev), fld("reaction_temperature", "r.t.", ev)])],
        [fld("reaction_result", "complicated products", ev, ["screen_mixture"])],
        unresolved=["The grouped prose does not report base loading, halogenating reagent, atmosphere, duration, individual product identities, or quantitative outcome for this base."]
    ))

# CsOAc success mentioned in prose; LiOAc is represented by Table 1 entry 1.
ev12 = [P1T, P1I, P2T, P2I]
records.append(rec(
    "base_screen_csoac", "optimization_entry", ev12,
    [part("csoac_1a", "reactant", ev12, label="1a", name=substrates["1a"][0], smiles=substrates["1a"][1]),
     part("csoac", "unspecified_agent", ev12, name="cesium acetate", smiles="[Cs+].CC(=O)[O-]"),
     *common_solvents(ev12),
     part("csoac_2a", "product", ev12, label="2a", name=iodoproducts["2a"][0], smiles=iodoproducts["2a"][1])],
    [step("base_screen", ["csoac_1a", "csoac", "thf", "dmf", "csoac_2a"],
          [fld("solvent", "THF/DMF (2:1)", ev12), fld("reaction_temperature", "r.t.", ev12), fld("reaction_time", q(6, "d"), ev12)])],
    [fld("yield", q(87, "%"), ev12, ["csoac_2a"]), fld("yield_measurement_basis", None, [], ["csoac_2a"])],
    unresolved=["CsOAc loading, halogenating reagent/amount, atmosphere, workup, purification, and yield basis are not stated in the prose summary."]
))

# Table 1 temperature optimization.
t1_rows = [(1, 13, 121, 89), (2, 30, 20, 68), (3, 30, 47, 88),
           (4, 40, 36, 87), (5, 50, 19, 82), (6, 60, 50, 64)]
for entry, temp, hours, yld in t1_rows:
    ev = [P2T, P2I]
    record_ev = [P1T, P1I, P2T, P2I] if entry == 1 else ev
    ps = [
        part("t1_1a", "reactant", ev, label="1a", name=substrates["1a"][0], smiles=substrates["1a"][1]),
        part("t1_i2", "reagent", ev, name="iodine", smiles="II", amounts=[fld("equivalents", q(2, "equiv"), ev)]),
        part("t1_lioac_hydrate", "unspecified_agent", ev, name="lithium acetate dihydrate", smiles="[Li+].CC(=O)[O-].O.O", amounts=[fld("equivalents", q(1.2, "equiv"), ev)]),
        *common_solvents(ev),
        part("t1_o2", "reagent", ev, name="oxygen", smiles="O=O"),
        part("t1_2a", "product", ev, label="2a", name=iodoproducts["2a"][0], smiles=iodoproducts["2a"][1]),
    ]
    atmosphere = "air" if entry == 1 else "O2 (1 atm)"
    records.append(rec(
        f"table1_entry{entry}", "optimization_entry", record_ev, ps,
        [step("stage1", ["t1_1a", "t1_i2", "t1_lioac_hydrate", "thf"],
              [fld("solvent", "THF", ev), fld("reaction_temperature", "r.t.", ev), fld("reaction_time", q(3, "h"), ev)]),
         step("stage2", ["t1_1a", "t1_i2", "t1_lioac_hydrate", "thf", "dmf", "t1_o2", "t1_2a"],
              [fld("solvent", "THF/DMF (2:1)", ev), fld("atmosphere", atmosphere, ev), fld("reaction_temperature", q(temp, "°C"), ev), fld("reaction_time", q(hours, "h"), ev)])],
        [fld("yield", q(yld, "%"), ev, ["t1_2a"]), fld("yield_measurement_basis", None, [], ["t1_2a"])],
        notes=(["The cross-page prose summarizes the LiOAc·2H2O result as 89% after about six days. Table 1 entry 1 gives the more precise 13 °C, 121 h values and footnotes the run as conducted in air at room temperature instead of O2 (1 atm)."] if entry == 1 else []) +
              (["Decomposition of 2a was observed because of higher temperature and prolonged reaction time."] if entry == 6 else []),
        unresolved=["Workup, purification, and yield basis are absent from the main-text table; supporting information was not provided."]
    ))

# Table 2 iodine substrate scope.
t2_rows = [
    (1, "1a", "2a", 36, 87, False), (2, "1b", "2b", 34, 83, False),
    (3, "1c", "2c", 8, 72, False), (4, "1d", "2d", 90, 54, False),
    (5, "1e", "2e", 13, 73, False), (6, "1f", "2f", 12, 70, False),
    (7, "1g", "2g", 19, 73, False), (8, "1h", "2h", 34, 40, False),
    (9, "1h", "2h", 120, 78, True), (10, "1i", "2i", 50.5, 31, False),
    (11, "1i", "2i", 120, 71, True),
]
for entry, slabel, plabel, hours, yld, air in t2_rows:
    ev = [P2T, P2I]
    sname, ssmiles = substrates[slabel]
    pname, psmiles = iodoproducts[plabel]
    ps = [
        part("t2_substrate", "reactant", ev, label=slabel, name=sname, smiles=ssmiles,
             amounts=[fld("amount", q(0.5, "mmol"), ev)]),
        part("t2_i2", "reagent", ev, name="iodine", smiles="II", amounts=[fld("amount", q(1.0, "mmol"), ev), fld("equivalents", q(2, "equiv"), ev)]),
        part("t2_lioac_hydrate", "unspecified_agent", ev, name="lithium acetate dihydrate", smiles="[Li+].CC(=O)[O-].O.O", amounts=[fld("amount", q(0.6, "mmol"), ev), fld("equivalents", q(1.2, "equiv"), ev)]),
        *common_solvents(ev),
        part("t2_o2", "reagent", ev, name="oxygen", smiles="O=O"),
        part("t2_product", "product", ev, label=plabel, name=pname, smiles=psmiles),
    ]
    stage2_temp = "r.t." if air else q(40, "°C")
    atmosphere = "air" if air else "O2 (1 atm)"
    records.append(rec(
        f"table2_entry{entry}", "substrate_scope_entry", ev, ps,
        [step("stage1", ["t2_substrate", "t2_i2", "t2_lioac_hydrate", "thf"],
              [fld("solvent", "THF", ev), fld("reaction_temperature", "r.t.", ev), fld("reaction_time", q(3, "h"), ev)]),
         step("stage2", ["t2_substrate", "t2_i2", "t2_lioac_hydrate", "thf", "dmf", "t2_o2", "t2_product"],
              [fld("solvent", "THF/DMF (2:1)", ev), fld("reaction_volume", q(3, "mL"), ev), fld("atmosphere", atmosphere, ev), fld("reaction_temperature", stage2_temp, ev), fld("reaction_time", q(hours, "h"), ev)])],
        [fld("isolated_yield", q(yld, "%"), ev, ["t2_product"]), fld("yield_measurement_basis", "isolated yield", ev, ["t2_product"])],
        notes=(["Footnote c overrides the standard O2/40 °C conditions: the reaction was conducted at room temperature in air."] if air else []),
        unresolved=["Workup and purification are absent from the main-text table; supporting information was not provided."]
    ))

# Equation 2: unsuccessful hydroxylation, but isolated iodolactonization product 3j.
ev2 = [P2T, P2I]
records.append(rec(
    "eq2_1j_to_3j", "reported_experiment", ev2,
    [part("eq2_1j", "reactant", ev2, label="1j", name="2,3-allenoic acid bearing n-C7H15", smiles="O=C(O)C=C=CCCCCCCC"),
     part("eq2_i2", "reagent", ev2, name="iodine", smiles="II"),
     part("eq2_lioac_hydrate", "unspecified_agent", ev2, name="lithium acetate dihydrate", smiles="[Li+].CC(=O)[O-].O.O"),
     *common_solvents(ev2),
     part("eq2_o2", "reagent", ev2, name="oxygen", smiles="O=O"),
     part("eq2_3j", "product", ev2, label="3j", name="4-iodo-5-heptylfuran-2(5H)-one", smiles="O=C1OC(CCCCCCC)C(I)=C1")],
    [step("stage1", ["eq2_1j", "eq2_i2", "eq2_lioac_hydrate", "thf"], [fld("solvent", "THF", ev2), fld("reaction_temperature", "r.t.", ev2), fld("reaction_time", q(3, "h"), ev2)]),
     step("stage2", ["eq2_1j", "eq2_i2", "eq2_lioac_hydrate", "thf", "dmf", "eq2_o2", "eq2_3j"], [fld("solvent", "THF/DMF", ev2), fld("atmosphere", "O2 (1 atm)", ev2), fld("reaction_temperature", q(40, "°C"), ev2), fld("reaction_time", q(42, "h"), ev2)])],
    [fld("yield", q(74, "%"), ev2, ["eq2_3j"]), fld("hydroxylation_result", "unsuccessful; only iodolactonization product 3j formed", ev2, ["eq2_3j"]), fld("yield_measurement_basis", None, [], ["eq2_3j"])],
    unresolved=["I2 and LiOAc·2H2O quantities, exact THF/DMF ratio, workup, purification, and yield basis are not stated in equation 2; supporting information was not provided."]
))

# Table 3 two-stage CuX2 substrate scope.
t3_rows = [
    (1, "1a", "Cl", "4a", 8.5, 77), (2, "1a", "Br", "4b", 3.5, 54),
    (3, "1b", "Cl", "4c", 6, 47), (4, "1b", "Br", "4d", 5, 50),
    (5, "1c", "Cl", "4e", 4.5, 79), (6, "1c", "Br", "4f", 3.5, 49),
    (7, "1i", "Cl", "4g", 5, 81), (8, "1i", "Br", "4h", 5, 77),
]
for entry, slabel, halogen, plabel, hours, yld in t3_rows:
    ev = [P2T, P2I]
    sname, ssmiles = substrates[slabel]
    r1 = {"1a": ("c2ccccc2", "C"), "1b": ("c2ccccc2", "CCC"), "1c": ("c2ccccc2", "Cc3ccccc3"), "1i": ("c2cccc3ccccc23", "CCC")}[slabel]
    psmiles = f"O=C1OC(O)({r1[0]})C({halogen})=C1{r1[1]}"
    pname = f"{plabel}: 4-{('chloro' if halogen == 'Cl' else 'bromo')}-5-hydroxyfuran-2(5H)-one derivative from {slabel}"
    cux_name = "copper(II) chloride" if halogen == "Cl" else "copper(II) bromide"
    cux_smiles = "Cl[Cu]Cl" if halogen == "Cl" else "Br[Cu]Br"
    ps = [
        part("t3_substrate", "reactant", ev, label=slabel, name=sname, smiles=ssmiles),
        part("t3_cux2", "reagent", ev, name=cux_name, smiles=cux_smiles),
        part("t3_acetone", "solvent", ev, name="acetone", smiles="CC(C)=O"),
        part("t3_water", "solvent", ev, name="water", smiles="O"),
        part("t3_lioac_hydrate", "unspecified_agent", ev, name="lithium acetate dihydrate", smiles="[Li+].CC(=O)[O-].O.O", amounts=[fld("equivalents", q(0.5, "equiv"), ev)]),
        *common_solvents(ev),
        part("t3_o2", "reagent", ev, name="oxygen", smiles="O=O"),
        part("t3_product", "product", ev, label=plabel, name=pname, smiles=psmiles),
    ]
    records.append(rec(
        f"table3_entry{entry}", "substrate_scope_entry", ev, ps,
        [step("halolactonization", ["t3_substrate", "t3_cux2", "t3_acetone", "t3_water"], [fld("solvent", "acetone/H2O", ev), fld("reaction_temperature", q(65, "°C"), ev), fld("reaction_time", {"minimum": 2, "maximum": 4, "unit": "h", "raw_text": "2–4 h"}, ev)]),
         step("hydroxylation", ["t3_substrate", "t3_cux2", "t3_lioac_hydrate", "thf", "dmf", "t3_o2", "t3_product"], [fld("solvent", "THF/DMF", ev), fld("atmosphere", "O2 (1 atm)", ev), fld("reaction_temperature", q(40, "°C"), ev), fld("reaction_time", q(hours, "h"), ev)])],
        [fld("isolated_yield", q(yld, "%"), ev, ["t3_product"]), fld("yield_measurement_basis", "isolated yield", ev, ["t3_product"])],
        notes=["No yield improvement was observed with more than 0.5 equiv LiOAc·2H2O."],
        unresolved=["CuX2 amount, solvent volumes/ratio, intervening workup details, and purification are not in the main-text table; supporting information was not provided."]
    ))

# Table 4 additive study.
t4_rows = [
    (1, None, None, 1, 22, 73, 7, False, False),
    (2, "LiOAc·2H2O", 0.2, 1, 56, 19, 7, False, False),
    (3, "LiOAc·2H2O", 1.2, 1, 54, 0, 7, False, False),
    (4, "LiOAc·2H2O", 1.2, 1, 84, 0, 7, True, False),
    (5, "LiOAc·2H2O", 1.2, None, 51, 0, 15, True, False),
    (6, "LiOAc", 1.2, None, 37, 17, 15, True, True),
    (7, "LiOAc", 1.2, 1, 43, 0, 15, False, True),
]
for entry, base, base_eq, oxygen_atm, yld, recovered, hours, add_i2, anhydrous in t4_rows:
    ev = [P2T, P2I, P3T, P3I]
    ps = [
        part("t4_3a", "reactant", ev, label="3a", name="3-methyl-4-iodo-5-phenyl-2(5H)-furanone", smiles="O=C1OC(c2ccccc2)C(I)=C1C"),
        *common_solvents(ev),
        part("t4_2a", "product", ev, label="2a", name=iodoproducts["2a"][0], smiles=iodoproducts["2a"][1]),
    ]
    pids = ["t4_3a", "thf", "dmf", "t4_2a"]
    if base:
        base_smiles = "[Li+].CC(=O)[O-].O.O" if "2H2O" in base else "[Li+].CC(=O)[O-]"
        ps.append(part("t4_base", "unspecified_agent", ev, name="lithium acetate dihydrate" if "2H2O" in base else "lithium acetate", smiles=base_smiles, amounts=[fld("equivalents", q(base_eq, "equiv"), ev)]))
        pids.append("t4_base")
    if add_i2:
        ps.append(part("t4_i2", "reagent", ev, name="iodine", smiles="II", amounts=[fld("equivalents", q(1, "equiv"), ev)]))
        pids.append("t4_i2")
    if oxygen_atm:
        ps.append(part("t4_o2", "reagent", ev, name="oxygen", smiles="O=O"))
        pids.append("t4_o2")
    cond = [fld("solvent", "anhydrous THF/DMF (2:1)" if anhydrous else "THF/DMF (2:1)", ev), fld("reaction_temperature", q(40, "°C"), ev), fld("reaction_time", q(hours, "h"), ev)]
    if oxygen_atm:
        cond.append(fld("atmosphere", "O2 (1 atm)", ev))
    elif entry == 5:
        cond.append(fld("atmosphere", "N2", ev))
    records.append(rec(
        f"table4_entry{entry}", "optimization_entry", ev, ps,
        [step("hydroxylation", pids, cond)],
        [fld("yield", q(yld, "%"), ev, ["t4_2a"]), fld("recovered_3a", q(recovered, "%"), ev, ["t4_3a"]), fld("yield_measurement_basis", None, [], ["t4_2a"])],
        notes=(["No O2 was supplied according to the table."] if oxygen_atm is None else []) + (["Footnote c specifies anhydrous THF/DMF (2:1)."] if anhydrous else []),
        unresolved=["Workup, purification, yield/recovery measurement basis, and reagent concentrations are absent from the main text; supporting information was not provided."]
    ))

# Scheme 2 solvent/anhydrous controls.
scheme2_rows = [
    ("anhydrous_thf", "anhydrous THF", "N2", 6, 93),
    ("dmf_o2", "DMF", "O2 (1 atm)", 42, None),
]
for slug, solvent, atmosphere, yld, recovered in scheme2_rows:
    ev = [P2T, P2I, P3T, P3I]
    hydrate = slug == "dmf_o2"
    ps = [
        part("s2_3a", "reactant", ev, label="3a", name="3-methyl-4-iodo-5-phenyl-2(5H)-furanone", smiles="O=C1OC(c2ccccc2)C(I)=C1C"),
        part("s2_lioac", "unspecified_agent", ev, name="lithium acetate dihydrate" if hydrate else "lithium acetate", smiles="[Li+].CC(=O)[O-].O.O" if hydrate else "[Li+].CC(=O)[O-]", amounts=[fld("equivalents", q(1.2, "equiv"), ev)]),
        part("s2_i2", "reagent", ev, name="iodine", smiles="II", amounts=[fld("equivalents", q(1, "equiv"), ev)]),
        part("s2_solvent", "solvent", ev, name="tetrahydrofuran" if slug == "anhydrous_thf" else "N,N-dimethylformamide", smiles="C1CCOC1" if slug == "anhydrous_thf" else "CN(C)C=O"),
        part("s2_2a", "product", ev, label="2a", name=iodoproducts["2a"][0], smiles=iodoproducts["2a"][1]),
    ]
    outcomes = [fld("yield", q(yld, "%"), ev, ["s2_2a"]), fld("yield_measurement_basis", None, [], ["s2_2a"])]
    if recovered is not None:
        outcomes.append(fld("recovered_3a", q(recovered, "%"), ev, ["s2_3a"]))
    records.append(rec(
        f"scheme2_{slug}", "optimization_entry", ev, ps,
        [step("hydroxylation", [p["entity_id"] for p in ps], [fld("solvent", solvent, ev), fld("atmosphere", atmosphere, ev), fld("reaction_temperature", q(40, "°C"), ev), fld("reaction_time", q(15, "h"), ev)])],
        outcomes,
        unresolved=["Workup, purification, yield/recovery measurement basis, and reagent concentrations are absent from Scheme 2; supporting information was not provided."]
    ))

# Scheme 3 is retained as a proposed mechanism, not as an experimental result.
ev3 = [P2T, P2I, P3T, P3I]
records.append(rec(
    "scheme3_mechanism", "mechanism", ev3,
    [part("m_1a", "reactant", ev3, label="1a", name=substrates["1a"][0], smiles=substrates["1a"][1]),
     part("m_3a", "unspecified_agent", ev3, label="3a", name="3-methyl-4-iodo-5-phenyl-2(5H)-furanone", smiles="O=C1OC(c2ccccc2)C(I)=C1C"),
     part("m_5", "unspecified_agent", ev3, label="5", name="proposed butenolide anion"),
     part("m_6", "unspecified_agent", ev3, label="6", name="proposed peroxy anion"),
     part("m_7", "unspecified_agent", ev3, label="7", name="proposed hydroperoxide"),
     part("m_8", "unspecified_agent", ev3, label="8", name="proposed diiodide intermediate"),
     part("m_9", "unspecified_agent", ev3, label="9", name="proposed diiodide intermediate"),
     part("m_2a", "product", ev3, label="2a", name=iodoproducts["2a"][0], smiles=iodoproducts["2a"][1]),
     part("m_i2", "reagent", ev3, name="iodine", smiles="II"),
     part("m_o2", "reagent", ev3, name="oxygen", smiles="O=O"),
     part("m_base", "unspecified_agent", ev3, name="base (unspecified)"),
     part("m_water", "reagent", ev3, name="water", smiles="O")],
    [step("halolactonization", ["m_1a", "m_i2", "m_base", "m_3a"], []),
     step("path_a_oxygenation", ["m_3a", "m_base", "m_5", "m_o2", "m_6", "m_7", "m_2a"], []),
     step("path_b_iodination_hydrolysis", ["m_5", "m_i2", "m_8", "m_9", "m_water", "m_2a"], [])],
    notes=["Scheme 3 is explicitly presented as a plausible mechanism; intermediates 5–9 are not reported as isolated experiments."],
    unresolved=["The proposed intermediate structures and proton/iodide transfers are mechanistic hypotheses, not experimentally verified records; exact base identity and quantities are unspecified."]
))

out = Path(__file__).with_name("extracted_pages_0001_0003.json")
out.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")

def ids_with(*prefixes):
    return [r["record_id"] for r in records
            if any(r["source_reaction_id"].startswith(prefix) for prefix in prefixes)]

base_ids = ids_with("base_screen_")
coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1,
            "state": "attempted",
            "regions": [
                {"region": "title and abstract", "finding": "Current-paper overview of sequential halolactonization–hydroxylation; no row-specific experiment in this region.", "evidence_ids": [P1T, P1I]},
                {"region": "Figure 1", "finding": "X-ray molecular structure of 2a; characterization evidence, not a separate reaction experiment.", "evidence_ids": [P1T, P1I]},
                {"region": "Scheme 1", "finding": "Generic cyclization then gamma-hydroxylation pathway, classified as a general scheme with R1/R2/X unresolved.", "evidence_ids": [P1T, P1I]},
                {"region": "equation (1)", "finding": "Reported formation of racemic 2a from cinchonidine salt 1aa with I2 in THF/DMF (3:1), overnight, 84%.", "evidence_ids": [P1T, P1I]},
                {"region": "lower-right base-screen prose continuing to page 2", "finding": "Eight named bases gave complicated products; each condition was retained as a separate failed optimization entry. The CsOAc success is separate; LiOAc is represented by Table 1 entry 1.", "evidence_ids": [P1T, P1I, P2T, P2I]},
                {"region": "left-column prior-art survey and references", "finding": "Cited literature strategies and biological context; no sufficiently specified current-paper experiment extracted from these citations.", "evidence_ids": [P1T, P1I]},
            ],
            "record_ids": ids_with("scheme1_", "eq1_") + base_ids + ids_with("table1_entry1"),
            "unresolved": [
                "The full cinchonidine salt structure, equation (1) temperature/atmosphere/yield basis, and detailed base-screen loadings/times are not supplied on the page.",
                "Supporting information is mentioned later but was not provided or explicitly associated."
            ],
        },
        {
            "page": 2,
            "state": "attempted",
            "regions": [
                {"region": "Table 1", "finding": "Six independent temperature/time optimization rows, including the air footnote for entry 1 and decomposition footnote for entry 6.", "evidence_ids": [P2T, P2I]},
                {"region": "Table 2", "finding": "Eleven independent iodolactonization–hydroxylation scope rows; entries 9 and 11 use room-temperature air conditions, and all yields are isolated.", "evidence_ids": [P2T, P2I]},
                {"region": "left-column prose above equation (2)", "finding": "Continuation of grouped base screening plus narrative interpretation of Table 2; cross-page base records cite both page images.", "evidence_ids": [P1T, P1I, P2T, P2I]},
                {"region": "equation (2)", "finding": "Failed hydroxylation of n-C7H15-substituted allenoic acid 1j; only iodolactonization product 3j was reported, 74% after 42 h.", "evidence_ids": [P2T, P2I]},
                {"region": "Table 3", "finding": "Eight independent two-stage CuCl2/CuBr2 scope rows with isolated yields; 0.5 equiv LiOAc·2H2O footnote structured on each row.", "evidence_ids": [P2T, P2I]},
                {"region": "lower-right hydroxylation/additive discussion", "finding": "Narrative context for the seven Table 4 controls on page 3 and for the solvent controls in Scheme 2; no duplicate experiments created from prose.", "evidence_ids": [P2T, P2I, P3T, P3I]},
                {"region": "Scheme 3 discussion beginning at page bottom", "finding": "Proposed mechanism only, linked to the Scheme 3 mechanism record rather than a reported experiment.", "evidence_ids": [P2T, P2I, P3T, P3I]},
                {"region": "reference 5 footnote", "finding": "Prior publications cited for CuX2 halolactonization; not treated as experiments newly reported in this paper.", "evidence_ids": [P2T, P2I]},
            ],
            "record_ids": base_ids + ids_with("table1_", "table2_", "eq2_", "table3_", "table4_", "scheme2_", "scheme3_"),
            "unresolved": [
                "Table 1 yield basis is unstated; Table 3 omits CuX2 amount, solvent ratio/volumes, workup, and purification.",
                "Equation (2) omits I2/LiOAc·2H2O amounts, exact THF/DMF ratio, workup, purification, and yield basis.",
                "Table 4 and Scheme 2 details continue on page 3 and are not claimed from page 2 alone."
            ],
        },
        {
            "page": 3,
            "state": "attempted",
            "regions": [
                {"region": "Table 4", "finding": "Seven independent additive/atmosphere/anhydrous optimization rows, with 2a yield and recovered 3a percentage kept as separate target-linked outcomes.", "evidence_ids": [P3T, P3I]},
                {"region": "Scheme 2", "finding": "Two independent solvent/anhydrous controls: anhydrous THF/N2 gives 2a 6% plus 93% recovered 3a; DMF/O2 gives 2a 42%.", "evidence_ids": [P3T, P3I]},
                {"region": "Scheme 3", "finding": "Plausible path-a oxygenation and path-b iodine/hydrolysis mechanism; classified as mechanism, not experimental scope.", "evidence_ids": [P3T, P3I]},
                {"region": "conclusion and Supporting Information notice", "finding": "Conclusion summarizes the chemistry. The paper states that SI exists online, but no SI file was supplied, so no association was made.", "evidence_ids": [P3T, P3I]},
                {"region": "references 6 and 7", "finding": "Prior mechanistic/spontaneous-oxidation citations; no current-paper experiment extracted.", "evidence_ids": [P3T, P3I]},
            ],
            "record_ids": ids_with("table4_", "scheme2_", "scheme3_"),
            "unresolved": [
                "Table 4 and Scheme 2 omit workup, purification, and yield/recovery measurement bases.",
                "Scheme 3 intermediates and transfers are proposed rather than isolated or independently verified.",
                "The cited SI was not attached or explicitly associated; records remain partial."
            ],
        },
    ],
}
coverage_path = Path(__file__).parents[1] / "coverage" / "pages_0001_0003.json"
coverage_path.parent.mkdir(parents=True, exist_ok=True)
coverage_path.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"output": str(out), "coverage": str(coverage_path), "records": len(records)}, ensure_ascii=False))
