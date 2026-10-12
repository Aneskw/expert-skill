#!/usr/bin/env python3
"""Build evidence-linked machine records for source PDF pages 1-6."""

import json
from pathlib import Path


DOC = "doc_5fa965aae5d3692a"
OUT = Path(__file__).with_name("pages_0001_0006_records.json")
COVERAGE = Path(__file__).parents[1] / "coverage" / "pages_0001_0006.json"


def evid(page):
    return [f"{DOC}:page{page}:text", f"{DOC}:page{page}:image"]


def fact(value, ev=None):
    return {
        "value": value,
        "evidence_ids": list(ev or []),
        "verification": "missing" if value is None else "unreviewed",
    }


def field(name, value, ev=None, targets=None):
    item = {"name": name, "fact": fact(value, ev)}
    if targets:
        item["target_entity_ids"] = list(targets)
    return item


def qty(number, unit, **extra):
    value = {"number": number, "unit": unit}
    value.update(extra)
    return value


def rng(minimum, maximum, unit, raw_text):
    return {"minimum": minimum, "maximum": maximum, "unit": unit, "raw_text": raw_text}


def part(entity_id, role, name, label, ev, smiles=None, amounts=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, ev) if label is not None else fact(None),
        "name": fact(name, ev) if name is not None else fact(None),
        "smiles": fact(smiles, ev) if smiles is not None else fact(None),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": amounts or [],
    }


def amount(name, value, ev):
    return field(name, value, ev)


def record(rid, source_id, kind, ev, participants, steps, outcomes, unresolved, notes=None):
    return {
        "record_id": f"{DOC}:{rid}",
        "document_id": DOC,
        "source_reaction_id": source_id,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": list(dict.fromkeys(ev)),
        "participants": participants,
        "steps": steps,
        "outcomes": outcomes,
        "notes": notes or [],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved,
        },
    }


def step(step_id, participant_ids, conditions):
    return {"step_id": step_id, "participant_ids": participant_ids, "conditions": conditions}


COMMON_UNRESOLVED = [
    "Supporting-information association is unestablished; no SI details were inferred.",
    "Candidate structures are machine-transcribed from names/drawings and remain unverified.",
]


records = []


# Page 1 Scheme 1, with the matching detailed paragraph on page 5.
ev15 = evid(1) + evid(5)
p1 = part("s1_sub_1", "reactant", "1-phenyl-3-methyl-1-butyne", "1", ev15,
          "CC(C)C#Cc1ccccc1", [amount("mass", qty(124, "mg"), evid(5)), amount("amount", qty(0.86, "mmol"), evid(5))])
nbu = part("s1_nbu", "reagent", "n-butyllithium", "n-BuLi", ev15, None,
           [amount("volume", qty(0.54, "mL"), evid(5)), amount("concentration", qty(1.6, "M"), evid(5)), amount("amount", qty(1.0, "mmol"), evid(5))])
bnbr = part("s1_bnbr", "reactant", "benzyl bromide", "PhCH2Br", ev15, "BrCc1ccccc1",
            [amount("volume", qty(0.13, "mL"), evid(5)), amount("amount", qty(1.1, "mmol"), evid(5))])
prod2 = part("s1_prod_2", "product", "1,2-diphenyl-4-methyl-2,3-pentadiene", "2", ev15)
prod3 = part("s1_prod_3", "product", "1,4-diphenyl-3,3-dimethylbut-1-yne", "3", ev15,
             "CC(C)(Cc1ccccc1)C#Cc1ccccc1")
records.append(record(
    "scheme1_1_to_2_3", "Scheme 1 / 3.2.1.1", "reported_experiment", ev15,
    [p1, nbu, bnbr, prod2, prod3],
    [step("lithiation", ["s1_sub_1", "s1_nbu"], [field("temperature", rng(-78, 20, "°C", "-78 °C to r.t."), evid(1)), field("time", qty(1, "h"), evid(1))]),
     step("benzylation", ["s1_bnbr"], [field("temperature", "r.t.", evid(1)), field("time", None)])],
    [field("combined_yield", {"number": 99, "unit": "%", "qualifier": "gt", "raw_text": ">99%"}, ev15, ["s1_prod_2", "s1_prod_3"]),
     field("product_ratio", "2:3 = 70:30", ev15, ["s1_prod_2", "s1_prod_3"]),
     field("yield_measurement_basis", "300 MHz 1H NMR with CH2Br2 as internal standard", ev15, ["s1_prod_2", "s1_prod_3"])],
    COMMON_UNRESOLVED + ["Duration after benzyl bromide addition is not reported for this experiment."],
))


# Shared molecules and simple helpers for Table 1 / Scheme 2.
smiles = {
    "4a": "c1ccccc1C#CC1CC1",
    "5a": "c1ccccc1C#CC1(CC1)Cc1ccccc1",
    "5b": "C=CCC1(CC1)C#Cc1ccccc1",
    "4a_prime": "c1ccccc1C#CC1(CC1)C2(CC2)C#Cc1ccccc1",
    "5c": "CCCCC1(CC1)C#Cc1ccccc1",
    "5e": "CC1(CC1)C#Cc1ccccc1",
    "6": "c1ccccc1C#CC1CCC1",
    "8": "c1ccccc1C#CC1(CCC1)Cc1ccccc1",
    "9": "c1ccccc1C#CC1CCCCC1",
    "11": "c1ccccc1C#CC1(CCCCC1)Cc1ccccc1",
    "13a": "c1ccccc1C#CC1(c2ccccc2)CC1",
    "13b": "c1ccccc1C#CC1(c2cccc3ccccc23)CC1",
    "13c": "Cc1ccccc1C1(CC1)C#Cc1ccccc1",
    "13d": "COC(=O)c1ccc(C2(CC2)C#Cc2ccccc2)cc1",
    "13e": "N#Cc1ccc(C2(CC2)C#Cc2ccccc2)cc1",
    "13f": "COc1ccc(C2(CC2)C#Cc2ccccc2)cc1",
    "13g": "COC(=O)/C=C/C1(CC1)C#Cc1ccccc1",
    "13h": "Brc1ccc(C2(CC2)C#Cc2ccccc2)cc1",
    "13i": "Clc1ccc(C2(CC2)C#Cc2ccccc2)cc1",
    "13j": "N#Cc1ccc(C2(CC2)C#Cc2ccc(-c3ccccc3)cc2)cc1",
    "13k": "COC(=O)c1ccc(C2(CC2)C#Cc2ccc(-c3ccccc3)cc2)cc1",
    "14": "C1CC(=C=C(c2ccccc2)c2ccccc2)C1",
    "15": "C1CCC(=C=C(c2ccccc2)c2ccccc2)CC1",
}


def table1_record(entry, product_label, electrophile_name, electrophile_label, electrophile_smiles,
                  yield_value, detail_page, product_name, product_smiles=None, extra_product=None,
                  nbu_equiv=None, electrophile_equiv=None, reaction_temp="r.t."):
    ev = evid(2) + evid(detail_page)
    prefix = f"t1e{entry}"
    substrate = part(prefix + "_4a", "reactant", "1-cyclopropyl-2-phenylacetylene", "4a", ev, smiles["4a"])
    nbu_amounts = [amount("equivalents", qty(nbu_equiv, "equiv"), evid(2))] if nbu_equiv else []
    nbul = part(prefix + "_nbu", "reagent", "n-butyllithium", "n-BuLi", ev, None, nbu_amounts)
    e_amounts = [amount("equivalents", qty(electrophile_equiv, "equiv"), evid(2))] if electrophile_equiv else []
    electrophile = part(prefix + "_e", "reactant", electrophile_name, electrophile_label, ev, electrophile_smiles, e_amounts)
    product = part(prefix + "_prod", "product", product_name, product_label, ev, product_smiles)
    participants = [substrate, nbul, electrophile, product]
    targets = [prefix + "_prod"]
    outcomes = [field("yield", qty(yield_value, "%"), ev, targets)]
    if extra_product:
        ep = part(prefix + "_byproduct", "product", extra_product[1], extra_product[0], ev, extra_product[3])
        participants.append(ep)
        outcomes.append(field("byproduct_yield", qty(extra_product[2], "%"), ev, [prefix + "_byproduct"]))
    records.append(record(
        f"table1_entry{entry}_{product_label}", f"Table 1 entry {entry} / {product_label}", "substrate_scope_entry", ev,
        participants,
        [step("lithiation", [prefix + "_4a", prefix + "_nbu"], [field("temperature", "r.t.", evid(2)), field("time", qty(1, "h"), evid(2))]),
         step("electrophile_addition", [prefix + "_e"], [field("temperature", reaction_temp, evid(2)), field("time", None)])],
        outcomes + [field("yield_measurement_basis", "isolated after silica-gel chromatography", evid(detail_page), targets)],
        COMMON_UNRESOLVED + ["Reaction-completion time after electrophile addition is not numerically reported."],
    ))


table1_record(1, "5a", "benzyl bromide", "PhCH2Br", "BrCc1ccccc1", 78, 4,
              "1-(phenylethynyl)-1-benzylcyclopropane", smiles["5a"])
table1_record(2, "5b", "allyl bromide", "CH2=CHCH2Br", "C=CCBr", 77, 5,
              "1-(phenylethynyl)-1-allylcyclopropane", smiles["5b"],
              ("4a'", "1,1'-diphenylethynylbicyclopropyl", 2, smiles["4a_prime"]), 2, 4)
table1_record(3, "5c", "n-butyl bromide", "n-C4H9Br", "CCCCBr", 43, 5,
              "1-(phenylethynyl)-1-n-butylcyclopropane", smiles["5c"])
table1_record(4, "5d", "N-benzylidene-p-toluenesulfonamide", "PhCH=NTs",
              "Cc1ccc(S(=O)(=O)N=Cc2ccccc2)cc1", 50, 5,
              "N-[phenyl-(1-(phenylethynyl)cyclopropyl)methyl]-p-toluenesulfonamide", None,
              reaction_temp=qty(0, "°C"))
table1_record(5, "5e", "methyl iodide", "CH3I", "CI", 76, 5,
              "1-(phenylethynyl)-1-methylcyclopropane", smiles["5e"])


def scheme2_record(rid, substrate_label, substrate_name, substrate_smiles, product_rows, combined_yield, ratio, detail_page=6):
    ev = evid(2) + evid(detail_page)
    prefix = rid
    parts = [
        part(prefix + "_sub", "reactant", substrate_name, substrate_label, ev, substrate_smiles),
        part(prefix + "_nbu", "reagent", "n-butyllithium", "n-BuLi", ev, None, [amount("equivalents", qty(3, "equiv"), evid(2))]),
        part(prefix + "_bnbr", "reactant", "benzyl bromide", "PhCH2Br", ev, "BrCc1ccccc1", [amount("equivalents", qty(3, "equiv"), evid(2))]),
    ]
    targets = []
    outcomes = []
    for label, name, structure, individual_yield in product_rows:
        eid = prefix + "_prod_" + label
        parts.append(part(eid, "product", name, label, ev, structure))
        targets.append(eid)
        if individual_yield is not None:
            outcomes.append(field("isolated_yield", qty(individual_yield, "%"), evid(detail_page), [eid]))
    outcomes.extend([
        field("combined_yield", qty(combined_yield, "%"), ev, targets),
        field("product_ratio", ratio, ev, targets),
    ])
    records.append(record(
        rid, f"Scheme 2 / sections 3.2.1.6-3.2.1.7 ({substrate_label})", "reported_experiment", ev,
        parts,
        [step("lithiation", [prefix + "_sub", prefix + "_nbu"], [field("temperature", "r.t.", evid(2)), field("time", qty(1, "h"), evid(2))]),
         step("benzylation", [prefix + "_bnbr"], [field("temperature", "r.t.", evid(2)), field("time", qty(2, "h"), evid(2))])],
        outcomes,
        COMMON_UNRESOLVED + ["Combined-yield measurement basis is not explicitly stated in Scheme 2."],
    ))


scheme2_record("scheme2_cyclobutyl_7_8", "6", "1-cyclobutyl-2-phenylacetylene", smiles["6"],
               [("7", "2,3-diphenylpropenylidenecyclobutane", None, 24),
                ("8", "1-(phenylethynyl)-1-benzylcyclobutane", smiles["8"], 44)], 68, "7:8 = 35:65")
scheme2_record("scheme2_cyclohexyl_10_11", "9", "1-cyclohexyl-2-phenylacetylene", smiles["9"],
               [("10", "2,3-diphenylpropenylidenecyclohexane", None, None),
                ("11", "1-(phenylethynyl)-1-benzylcyclohexane", smiles["11"], None)], 76, "10:11 = 74:26")


# Table 2 scope. Detailed records for 12a and 12b are linked to page 6.
t2_rows = [
    (1, "12a", "iodobenzene", "Ph", "Ic1ccccc1", "allene 12a (R = Ph)", 47, 6, "CC(C)=C=C(c1ccccc1)c1ccccc1"),
    (2, "12b", "1-iodonaphthalene", "1-naphthyl", "Ic1cccc2ccccc12", "allene 12b (R = 1-naphthyl)", 25, 6, None),
    (3, "12c", "4-iodoanisole", "p-MeOC6H4", "COc1ccc(I)cc1", "allene 12c (R = p-MeOC6H4)", 71, 2, None),
    (4, "12d", "methyl 4-iodobenzoate", "p-MeO2CC6H4", "COC(=O)c1ccc(I)cc1", "allene 12d (R = p-MeO2CC6H4)", 91, 2, None),
    (5, "12e", "2-iodotoluene", "o-MeC6H4", "Cc1ccccc1I", "allene 12e (R = o-MeC6H4)", 40, 2, None),
    (6, "12f", "methyl (E)-3-iodopropenoate", "(E)-CH=CHCO2Me", "COC(=O)/C=C/I", "allene 12f (R = (E)-CH=CHCO2Me)", 37, 2, None),
]
for entry, label, ename, elabel, esmiles, pname, yld, detail_page, psmiles in t2_rows:
    ev = evid(2) + ([] if detail_page == 2 else evid(detail_page))
    prefix = f"t2e{entry}"
    parts = [
        part(prefix + "_sub", "reactant", "1-phenyl-3-methyl-1-butyne", "1", ev, "CC(C)C#Cc1ccccc1"),
        part(prefix + "_nbu", "reagent", "n-butyllithium", "n-BuLi", ev),
        part(prefix + "_znbr2", "reagent", "zinc bromide", "ZnBr2", ev, "[Br-].[Br-].[Zn+2]"),
        part(prefix + "_pd", "catalyst", "tetrakis(triphenylphosphine)palladium(0)", "Pd(PPh3)4", ev, None,
             [amount("catalyst_loading", qty(5, "mol%"), evid(2))]),
        part(prefix + "_electrophile", "reactant", ename, elabel, ev, esmiles),
        part(prefix + "_prod", "product", pname, label, ev, psmiles),
    ]
    records.append(record(
        f"table2_entry{entry}_{label}", f"Table 2 entry {entry} / section 3.2.2.{entry if entry <= 2 else entry}", "substrate_scope_entry", ev,
        parts,
        [step("lithiation", [prefix + "_sub", prefix + "_nbu"], [field("temperature", rng(-78, 20, "°C", "-78 °C to r.t."), evid(2)), field("time", qty(1, "h"), evid(2))]),
         step("transmetallation", [prefix + "_znbr2"], [field("temperature", "r.t.", evid(2)), field("time", None)]),
         step("cross_coupling", [prefix + "_pd", prefix + "_electrophile"], [field("temperature", None), field("time", None)])],
        [field("yield", qty(yld, "%"), ev, [prefix + "_prod"]), field("yield_measurement_basis", "isolated product" if detail_page == 6 else None, evid(detail_page) if detail_page == 6 else [], [prefix + "_prod"])],
        COMMON_UNRESOLVED + (["Transmetallation and cross-coupling durations are not numerically reported."] if detail_page == 2 else ["Cross-coupling completion time is reported only as TLC completion."]),
    ))


# Table 3 scope. R values are represented as the corresponding RI electrophiles named in the scheme header.
t3_rows = [
    (1, "4a", "13a", "iodobenzene", "Ph", "Ic1ccccc1", 72),
    (2, "4a", "13b", "1-iodonaphthalene", "1-naphthyl", "Ic1cccc2ccccc12", 27),
    (3, "4a", "13c", "2-iodotoluene", "o-MeC6H4", "Cc1ccccc1I", 25),
    (4, "4a", "13d", "methyl 4-iodobenzoate", "p-MeO2CC6H4", "COC(=O)c1ccc(I)cc1", 98),
    (5, "4a", "13e", "4-iodobenzonitrile", "p-NCC6H4", "N#Cc1ccc(I)cc1", 88),
    (6, "4a", "13f", "4-iodoanisole", "p-MeOC6H4", "COc1ccc(I)cc1", 33),
    (7, "4a", "13g", "methyl (E)-3-iodopropenoate", "(E)-CH=CHCO2Me", "COC(=O)/C=C/I", 34),
    (8, "4a", "13h", "1-bromo-4-iodobenzene", "p-BrC6H4", "Brc1ccc(I)cc1", 64),
    (9, "4a", "13i", "1-chloro-4-iodobenzene", "p-ClC6H4", "Clc1ccc(I)cc1", 55),
    (10, "4b", "13j", "4-iodobenzonitrile", "p-NCC6H4", "N#Cc1ccc(I)cc1", 70),
    (11, "4b", "13k", "methyl 4-iodobenzoate", "p-MeO2CC6H4", "COC(=O)c1ccc(I)cc1", 51),
]
for entry, sublabel, plabel, ename, elabel, esmiles, yld in t3_rows:
    detail = entry == 1
    ev = evid(3) + (evid(6) if detail else [])
    prefix = f"t3e{entry}"
    subname = "1-cyclopropyl-2-phenylacetylene" if sublabel == "4a" else "1-cyclopropyl-2-(p-phenylphenyl)acetylene"
    subsmiles = smiles["4a"] if sublabel == "4a" else "c1ccc(-c2ccc(C#CC3CC3)cc2)cc1"
    parts = [
        part(prefix + "_sub", "reactant", subname, sublabel, ev, subsmiles),
        part(prefix + "_nbu", "reagent", "n-butyllithium", "n-BuLi", ev, None, [amount("equivalents", qty(1.2, "equiv"), evid(3))]),
        part(prefix + "_znbr2", "reagent", "zinc bromide", "ZnBr2", ev, "[Br-].[Br-].[Zn+2]", [amount("equivalents", qty(2, "equiv"), evid(3))]),
        part(prefix + "_pd", "catalyst", "tetrakis(triphenylphosphine)palladium(0)", "Pd(PPh3)4", ev, None, [amount("catalyst_loading", qty(5, "mol%"), evid(3))]),
        part(prefix + "_electrophile", "reactant", ename, elabel, ev, esmiles),
        part(prefix + "_prod", "product", f"cyclopropyl alkyne {plabel} (R = {elabel})", plabel, ev, smiles.get(plabel)),
    ]
    records.append(record(
        f"table3_entry{entry}_{plabel}", f"Table 3 entry {entry} / {plabel}", "substrate_scope_entry", ev,
        parts,
        [step("lithiation", [prefix + "_sub", prefix + "_nbu"], [field("temperature", "r.t." if not detail else rng(-78, 20, "°C", "-78 °C to r.t."), ev), field("time", qty(1, "h"), ev)]),
         step("transmetallation", [prefix + "_znbr2"], [field("temperature", "r.t.", ev), field("time", qty(25, "min"), evid(3))]),
         step("cross_coupling", [prefix + "_pd", prefix + "_electrophile"], [field("temperature", "r.t." if detail else None, evid(6) if detail else []), field("time", None)])],
        [field("yield", qty(yld, "%"), ev, [prefix + "_prod"]), field("yield_measurement_basis", "isolated after silica-gel chromatography" if detail else None, evid(6) if detail else [], [prefix + "_prod"])],
        COMMON_UNRESOLVED + ["Cross-coupling completion time is not numerically reported."],
    ))


# Scheme 3: one experiment, two product-specific yields.
ev3 = evid(3)
parts = [
    part("s3_4a", "reactant", "1-cyclopropyl-2-phenylacetylene", "4a", ev3, smiles["4a"]),
    part("s3_nbu", "reagent", "n-butyllithium", "n-BuLi", ev3, None, [amount("equivalents", qty(1.2, "equiv"), ev3)]),
    part("s3_zn", "reagent", "zinc bromide", "ZnBr2", ev3, "[Br-].[Br-].[Zn+2]", [amount("equivalents", qty(2, "equiv"), ev3)]),
    part("s3_pd", "catalyst", "tetrakis(triphenylphosphine)palladium(0)", "Pd(PPh3)4", ev3, None, [amount("catalyst_loading", qty(5, "mol%"), ev3)]),
    part("s3_diiodo", "reactant", "1,4-diiodobenzene", "p-C6H4I2", ev3, "Ic1ccc(I)cc1"),
    part("s3_13l", "product", "mono-cross-coupling product 13l", "13l", ev3, "Ic1ccc(C2(CC2)C#Cc2ccccc2)cc1"),
    part("s3_13lp", "product", "double-cross-coupling product 13l'", "13l'", ev3),
]
records.append(record(
    "scheme3_13l_13lprime", "Scheme 3", "reported_experiment", ev3, parts,
    [step("lithiation", ["s3_4a", "s3_nbu"], [field("temperature", "r.t.", ev3), field("time", qty(1, "h"), ev3)]),
     step("transmetallation", ["s3_zn"], [field("temperature", "r.t.", ev3), field("time", qty(25, "min"), ev3)]),
     step("cross_coupling", ["s3_pd", "s3_diiodo"], [field("temperature", None), field("time", None)])],
    [field("yield", qty(57, "%"), ev3, ["s3_13l"]), field("yield", qty(18, "%"), ev3, ["s3_13lp"]), field("yield_measurement_basis", None, [], ["s3_13l", "s3_13lp"])],
    COMMON_UNRESOLVED + ["Cross-coupling temperature, duration, and yield basis are not reported in Scheme 3."],
))


def scheme4_record(rid, sublabel, subname, subsmiles, plabel, pname, psmiles, yld):
    ev = evid(3)
    prefix = rid
    parts = [
        part(prefix + "_sub", "reactant", subname, sublabel, ev, subsmiles),
        part(prefix + "_nbu", "reagent", "n-butyllithium", "n-BuLi", ev, None, [amount("equivalents", qty(3, "equiv"), ev)]),
        part(prefix + "_zn", "reagent", "zinc bromide", "ZnBr2", ev, "[Br-].[Br-].[Zn+2]"),
        part(prefix + "_pd", "catalyst", "tetrakis(triphenylphosphine)palladium(0)", "Pd(PPh3)4", ev, None, [amount("catalyst_loading", qty(5, "mol%"), ev)]),
        part(prefix + "_phi", "reactant", "iodobenzene", "PhI", ev, "Ic1ccccc1", [amount("equivalents", qty(3, "equiv"), ev)]),
        part(prefix + "_prod", "product", pname, plabel, ev, psmiles),
    ]
    records.append(record(
        rid, f"Scheme 4 / {plabel}", "reported_experiment", ev, parts,
        [step("lithiation", [prefix + "_sub", prefix + "_nbu"], [field("temperature", "r.t.", ev), field("time", qty(1, "h"), ev)]),
         step("transmetallation", [prefix + "_zn"], [field("temperature", "r.t.", ev), field("time", None)]),
         step("cross_coupling", [prefix + "_pd", prefix + "_phi"], [field("temperature", None), field("time", None)])],
        [field("yield", qty(yld, "%"), ev, [prefix + "_prod"]), field("yield_measurement_basis", None, [], [prefix + "_prod"])],
        COMMON_UNRESOLVED + ["Transmetallation/cross-coupling times and yield basis are not reported in Scheme 4."],
    ))


scheme4_record("scheme4_cyclobutyl_14", "6", "1-cyclobutyl-2-phenylacetylene", smiles["6"], "14", "2,2-diphenyl vinylidenecyclobutane", smiles["14"], 55)
scheme4_record("scheme4_cyclohexyl_15", "9", "1-cyclohexyl-2-phenylacetylene", smiles["9"], "15", "2,2-diphenyl vinylidenecyclohexane", smiles["15"], 44)


# Proposed strained intermediate/product class 16 is explanatory, not an experiment.
records.append(record(
    "mechanism_vinylidenecyclopropane_16", "Scheme 4 structure 16", "mechanism", evid(3),
    [part("m16", "unspecified_agent", "generic vinylidenecyclopropane (Ar1/Ar2 variable)", "16", evid(3))],
    [], [],
    ["Structure 16 is a generic Ar-substituted explanatory structure, not a reported isolated experiment.", "R-group structure is generic; SMILES is intentionally missing."],
    [fact("The authors attribute the observed selectivity to unfavorable strain in vinylidenecyclopropanes.", evid(3))],
))


# Page 4 starting-material preparations. These are distinct reported experiments.
def prep_record(rid, source_id, participants, steps, outcomes, unresolved):
    records.append(record(rid, source_id, "reported_experiment", evid(4), participants, steps, outcomes, COMMON_UNRESOLVED + unresolved))


prep_record(
    "prep_1", "3.1.1", [
        part("p1_li", "reagent", "lithium metal", "Li", evid(4), "[Li]", [amount("mass", qty(0.47, "g"), evid(4)), amount("amount", qty(60, "mmol"), evid(4))]),
        part("p1_nh3", "solvent", "anhydrous liquid ammonia", "NH3", evid(4), "N", [amount("volume", qty(100, "mL"), evid(4))]),
        part("p1_pa", "reactant", "phenylacetylene", None, evid(4), "C#Cc1ccccc1", [amount("volume", qty(5.5, "mL"), evid(4)), amount("amount", qty(50, "mmol"), evid(4))]),
        part("p1_diox", "solvent", "1,4-dioxane", None, evid(4), "O1CCOCC1", [amount("volume", qty(20, "mL"), evid(4))]),
        part("p1_iprbr", "reactant", "2-bromopropane", "i-PrBr", evid(4), "CC(C)Br", [amount("volume", qty(9.4, "mL"), evid(4)), amount("amount", qty(100, "mmol"), evid(4))]),
        part("p1_prod", "product", "1-phenyl-3-methyl-1-butyne", "1", evid(4), "CC(C)C#Cc1ccccc1", [amount("mass", qty(1.418, "g"), evid(4))]),
    ],
    [step("lithium_ammonia", ["p1_li", "p1_nh3"], [field("temperature", qty(-40, "°C"), evid(4)), field("time", qty(1, "h"), evid(4)), field("operation", "evaporate NH3", evid(4))]),
     step("acetylide_formation", ["p1_pa", "p1_diox"], [field("temperature", "reflux", evid(4)), field("time", qty(20, "min"), evid(4))]),
     step("alkylation", ["p1_iprbr"], [field("temperature", qty(150, "°C"), evid(4)), field("time", qty(16, "h"), evid(4)), field("operation", "closed autoclave", evid(4))]),
     step("workup", [], [field("workup", "cool; pour into cold water; extract with ether; dry over anhydrous MgSO4", evid(4)), field("purification", "rotary evaporation and distillation", evid(4))])],
    [field("yield", qty(20, "%"), evid(4), ["p1_prod"]), field("boiling_point", "67 °C/5 mmHg", evid(4), ["p1_prod"])],
    ["Yield basis is not explicitly labelled beyond recovered product mass and percentage."],
)


prep_record(
    "prep_4a", "3.1.2", [
        part("p4a_phi", "reactant", "iodobenzene", "PhI", evid(4), "Ic1ccccc1", [amount("volume", qty(8.8, "mL"), evid(4)), amount("amount", qty(78.5, "mmol"), evid(4))]),
        part("p4a_cpa", "reactant", "cyclopropylacetylene", None, evid(4), "C#CC1CC1", [amount("volume", qty(8, "mL"), evid(4)), amount("amount", qty(94, "mmol"), evid(4))]),
        part("p4a_pd", "catalyst", "tetrakis(triphenylphosphine)palladium(0)", "Pd(PPh3)4", evid(4), None, [amount("mass", qty(500, "mg"), evid(4)), amount("catalyst_loading", qty(0.5, "mol%"), evid(4))]),
        part("p4a_cui", "catalyst", "copper(I) iodide", "CuI", evid(4), "[Cu]I", [amount("mass", qty(270, "mg"), evid(4)), amount("catalyst_loading", qty(1, "mol%"), evid(4))]),
        part("p4a_dipa", "solvent", "diisopropylamine", "(i-Pr)2NH", evid(4), "CC(C)NC(C)C", [amount("volume", qty(350, "mL"), evid(4))]),
        part("p4a_prod", "product", "1-cyclopropyl-2-phenylacetylene", "4a", evid(4), smiles["4a"], [amount("mass", qty(11.544, "g"), evid(4))]),
    ],
    [step("sonogashira_coupling", ["p4a_phi", "p4a_cpa", "p4a_pd", "p4a_cui", "p4a_dipa"], [field("atmosphere", "N2", evid(4)), field("temperature", "r.t.", evid(4)), field("time", None)]),
     step("isolation", [], [field("operation", "filter brown precipitate and rotary evaporate", evid(4)), field("purification", "flash chromatography on silica gel with petroleum ether", evid(4))])],
    [field("yield", {"number": 99, "unit": "%", "qualifier": "approx", "raw_text": "~99%"}, evid(4), ["p4a_prod"])],
    ["Reaction duration is reported only as TLC completion."],
)


prep_record(
    "prep_4b", "3.1.3", [
        part("p4b_brbp", "reactant", "4-bromobiphenyl", "p-phenylphenyl bromide", evid(4), "Brc1ccc(-c2ccccc2)cc1", [amount("mass", qty(1.165, "g"), evid(4)), amount("amount", qty(5, "mmol"), evid(4))]),
        part("p4b_cpa", "reactant", "cyclopropylacetylene", None, evid(4), "C#CC1CC1", [amount("volume", qty(0.85, "mL"), evid(4)), amount("amount", qty(10, "mmol"), evid(4))]),
        part("p4b_pd", "catalyst", "tetrakis(triphenylphosphine)palladium(0)", "Pd(PPh3)4", evid(4), None, [amount("mass", qty(58, "mg"), evid(4)), amount("catalyst_loading", qty(1, "mol%"), evid(4))]),
        part("p4b_prod", "product", "1-cyclopropyl-2-(p-phenylphenyl)acetylene", "4b", evid(4), "c1ccc(-c2ccc(C#CC3CC3)cc2)cc1", [amount("mass", qty(700, "mg"), evid(4))]),
    ],
    [step("coupling", ["p4b_brbp", "p4b_cpa", "p4b_pd"], [field("operation", "procedure stated to follow synthesis of 4a", evid(4)), field("temperature", None), field("time", None)]),
     step("isolation", [], [field("purification", "petroleum ether", evid(4))])],
    [field("yield", qty(64, "%"), evid(4), ["p4b_prod"]), field("melting_point", rng(67, 68, "°C", "67-68 °C"), evid(4), ["p4b_prod"])],
    ["Repeated solvent, atmosphere, workup, and duration are not restated for 4b and were not copied as exact compound-specific facts."],
)


prep_record(
    "prep_cyclobutylacetylene", "3.1.4", [
        part("pcb_chloro", "reactant", "6-chloro-1-hexyne", None, evid(4), "C#CCCCCCl", [amount("mass", qty(1.855, "g"), evid(4)), amount("amount", qty(0.016, "mol"), evid(4))]),
        part("pcb_nbu", "reagent", "n-butyllithium", "n-BuLi", evid(4), None, [amount("volume", qty(21, "mL"), evid(4)), amount("amount", qty(0.034, "mol"), evid(4)), amount("concentration", qty(1.6, "M"), evid(4))]),
        part("pcb_thf", "solvent", "tetrahydrofuran", "THF", evid(4), "C1CCOC1"),
        part("pcb_prod", "product", "cyclobutylacetylene", None, evid(4), "C#CC1CCC1"),
    ],
    [step("cyclization", ["pcb_chloro", "pcb_nbu", "pcb_thf"], [field("temperature", qty(-78, "°C"), evid(4)), field("time", qty(20, "min"), evid(4)), field("operation", "warm naturally to r.t. and stir overnight", evid(4))]),
     step("workup", [], [field("workup", "quench with saturated aqueous NH4Cl; extract with ether; dry over anhydrous MgSO4", evid(4)), field("operation", "remove ether by distillation; use THF solution directly in next step", evid(4))])],
    [field("yield", None, [], ["pcb_prod"])],
    ["Product amount and yield are not reported because the THF solution was used directly."],
)


prep_record(
    "prep_6", "3.1.5", [
        part("p6_cba", "reactant", "cyclobutylacetylene in THF from section 3.1.4", None, evid(4), "C#CC1CCC1"),
        part("p6_phi", "reactant", "iodobenzene", "PhI", evid(4), "Ic1ccccc1", [amount("volume", qty(0.9, "mL"), evid(4)), amount("amount", qty(0.008, "mol"), evid(4))]),
        part("p6_cui", "catalyst", "copper(I) iodide", "CuI", evid(4), "[Cu]I", [amount("mass", qty(15, "mg"), evid(4)), amount("catalyst_loading", qty(1, "mol%"), evid(4))]),
        part("p6_pd", "catalyst", "tetrakis(triphenylphosphine)palladium(0)", "Pd(PPh3)4", evid(4), None, [amount("mass", qty(46, "mg"), evid(4)), amount("catalyst_loading", qty(0.5, "mol%"), evid(4))]),
        part("p6_dipa", "solvent", "diisopropylamine", "(i-Pr)2NH", evid(4), "CC(C)NC(C)C", [amount("volume", qty(3, "mL"), evid(4))]),
        part("p6_prod", "product", "1-cyclobutyl-2-phenylacetylene", "6", evid(4), smiles["6"], [amount("mass", qty(0.373, "g"), evid(4))]),
    ],
    [step("coupling", ["p6_cba", "p6_phi", "p6_cui", "p6_pd", "p6_dipa"], [field("atmosphere", "N2", evid(4)), field("temperature", "r.t.", evid(4)), field("time", None)]),
     step("isolation", [], [field("operation", "filter brown precipitate and rotary evaporate", evid(4)), field("purification", "flash chromatography on silica gel with petroleum ether", evid(4))])],
    [field("yield", qty(30, "%"), evid(4), ["p6_prod"])],
    ["Cyclobutylacetylene amount and reaction duration are not reported in section 3.1.5."],
)


prep_record(
    "prep_9", "3.1.6", [
        part("p9_zn", "reagent", "zinc dust", "Zn", evid(4), "[Zn]", [amount("mass", qty(2.24, "g"), evid(4)), amount("amount", qty(0.040, "mol"), evid(4))]),
        part("p9_dbe", "reagent", "1,2-dibromoethane", None, evid(4), "BrCCBr"),
        part("p9_tmscl", "reagent", "trimethylsilyl chloride", "TMSCl", evid(4), "C[Si](C)(C)Cl"),
        part("p9_thf", "solvent", "tetrahydrofuran", "THF", evid(4), "C1CCOC1", [amount("volume", qty(20, "mL"), evid(4))]),
        part("p9_cyi", "reactant", "cyclohexyl iodide", None, evid(4), "IC1CCCCC1", [amount("mass", qty(4.20, "g"), evid(4)), amount("amount", qty(20, "mmol"), evid(4))]),
        part("p9_cucn", "catalyst", "CuCN·2LiCl", "CuCN·2LiCl", evid(4), None, [amount("mass", qty(175, "mg"), evid(4)), amount("catalyst_loading", qty(5, "mol%"), evid(4))]),
        part("p9_pei", "reactant", "phenylethynyl iodide", None, evid(4), "IC#Cc1ccccc1", [amount("volume", qty(2.0, "mL"), evid(4)), amount("amount", qty(15, "mmol"), evid(4))]),
        part("p9_prod", "product", "1-cyclohexyl-2-phenylacetylene", "9", evid(4), smiles["9"], [amount("mass", qty(0.268, "g"), evid(4))]),
    ],
    [step("zinc_activation", ["p9_zn", "p9_dbe", "p9_tmscl", "p9_thf"], [field("temperature", "r.t.", evid(4)), field("time", qty(20, "min"), evid(4)), field("operation", "one drop each of 1,2-dibromoethane and TMSCl", evid(4))]),
     step("organozinc_formation", ["p9_cyi"], [field("temperature", rng(40, 50, "°C", "40-50 °C"), evid(4)), field("time", "overnight", evid(4))]),
     step("coupling", ["p9_cucn", "p9_pei"], [field("atmosphere", "N2 during zinc filtration", evid(4)), field("temperature", "r.t.", evid(4)), field("time", None)]),
     step("workup", [], [field("workup", "add saturated aqueous FeSO4; extract with ether; dry over anhydrous MgSO4", evid(4)), field("purification", "rotary evaporation and flash chromatography on silica gel with petroleum ether", evid(4))])],
    [field("yield", qty(9, "%"), evid(4), ["p9_prod"])],
    ["Amounts of 1,2-dibromoethane and TMSCl are qualitative ('one drop each'); coupling duration is reported only as TLC completion."],
)


# Enrich page 4-6 matching records with explicitly printed experiment quantities.
by_id = {r["record_id"]: r for r in records}


def add_amount(record_suffix, entity_id, page, name, value):
    rec = by_id[f"{DOC}:{record_suffix}"]
    target = next(p for p in rec["participants"] if p["entity_id"] == entity_id)
    target["amounts"].append(amount(name, value, evid(page)))


# 5a, 5b, 5c, 5d and 5e detailed quantities.
for suffix, prefix, page, vals in [
    ("table1_entry1_5a", "t1e1", 4, [("_4a", "mass", qty(56, "mg")), ("_4a", "amount", qty(0.39, "mmol")), ("_nbu", "volume", qty(0.30, "mL")), ("_nbu", "concentration", qty(1.6, "M")), ("_nbu", "amount", qty(0.47, "mmol")), ("_e", "volume", qty(0.056, "mL")), ("_e", "amount", qty(0.47, "mmol"))]),
    ("table1_entry2_5b", "t1e2", 5, [("_4a", "mass", qty(56, "mg")), ("_4a", "amount", qty(0.39, "mmol")), ("_nbu", "volume", qty(0.49, "mL")), ("_nbu", "amount", qty(0.79, "mmol")), ("_nbu", "concentration", qty(1.6, "M")), ("_e", "volume", qty(0.14, "mL")), ("_e", "amount", qty(1.58, "mmol"))]),
    ("table1_entry3_5c", "t1e3", 5, [("_4a", "mass", qty(55, "mg")), ("_4a", "amount", qty(0.39, "mmol")), ("_nbu", "volume", qty(0.29, "mL")), ("_nbu", "amount", qty(0.46, "mmol")), ("_nbu", "concentration", qty(1.6, "M")), ("_e", "volume", qty(0.059, "mL")), ("_e", "amount", qty(0.55, "mmol"))]),
    ("table1_entry4_5d", "t1e4", 5, [("_4a", "mass", qty(58, "mg")), ("_4a", "amount", qty(0.41, "mmol")), ("_nbu", "volume", qty(0.31, "mL")), ("_nbu", "amount", qty(0.49, "mmol")), ("_nbu", "concentration", qty(1.6, "M")), ("_e", "mass", qty(127, "mg")), ("_e", "amount", qty(0.49, "mmol"))]),
    ("table1_entry5_5e", "t1e5", 5, [("_4a", "mass", qty(59, "mg")), ("_4a", "amount", qty(0.42, "mmol")), ("_nbu", "volume", qty(0.31, "mL")), ("_nbu", "amount", qty(0.50, "mmol")), ("_nbu", "concentration", qty(1.6, "M")), ("_e", "volume", qty(0.052, "mL")), ("_e", "amount", qty(0.83, "mmol"))]),
]:
    for ending, name, value in vals:
        add_amount(suffix, prefix + ending, page, name, value)


# Product recovered masses for Table 1 entries.
for suffix, eid, page, mass in [
    ("table1_entry1_5a", "t1e1_prod", 4, 71), ("table1_entry2_5b", "t1e2_prod", 5, 55),
    ("table1_entry2_5b", "t1e2_byproduct", 5, 2), ("table1_entry3_5c", "t1e3_prod", 5, 33),
    ("table1_entry4_5d", "t1e4_prod", 5, 82), ("table1_entry5_5e", "t1e5_prod", 5, 50),
]:
    add_amount(suffix, eid, page, "mass", qty(mass, "mg"))


# Detailed Scheme 2 quantities.
for suffix, prefix, vals in [
    ("scheme2_cyclobutyl_7_8", "scheme2_cyclobutyl_7_8", [("_sub", "mass", qty(32, "mg")), ("_sub", "amount", qty(0.20, "mmol")), ("_nbu", "volume", qty(0.38, "mL")), ("_nbu", "amount", qty(0.60, "mmol")), ("_nbu", "concentration", qty(1.6, "M")), ("_bnbr", "volume", qty(72, "uL")), ("_bnbr", "amount", qty(0.60, "mmol")), ("_prod_7", "mass", qty(12, "mg")), ("_prod_8", "mass", qty(22, "mg"))]),
    ("scheme2_cyclohexyl_10_11", "scheme2_cyclohexyl_10_11", [("_sub", "mass", qty(37, "mg")), ("_sub", "amount", qty(0.20, "mmol")), ("_nbu", "volume", qty(0.38, "mL")), ("_nbu", "amount", qty(0.60, "mmol")), ("_nbu", "concentration", qty(1.6, "M")), ("_bnbr", "volume", qty(72, "uL")), ("_bnbr", "amount", qty(0.60, "mmol"))]),
]:
    for ending, name, value in vals:
        add_amount(suffix, prefix + ending, 6, name, value)


# Detailed 12a/12b and 13a quantities from page 6.
for suffix, prefix, vals in [
    ("table2_entry1_12a", "t2e1", [("_sub", "mass", qty(58, "mg")), ("_sub", "amount", qty(0.40, "mmol")), ("_nbu", "volume", qty(0.30, "mL")), ("_nbu", "amount", qty(0.48, "mmol")), ("_nbu", "concentration", qty(1.6, "M")), ("_znbr2", "mass", qty(180, "mg")), ("_znbr2", "amount", qty(0.80, "mmol")), ("_pd", "mass", qty(16, "mg")), ("_electrophile", "volume", qty(30, "uL")), ("_electrophile", "amount", qty(0.27, "mmol")), ("_prod", "mass", qty(28, "mg"))]),
    ("table2_entry2_12b", "t2e2", [("_sub", "mass", qty(57, "mg")), ("_sub", "amount", qty(0.40, "mmol")), ("_nbu", "volume", qty(0.30, "mL")), ("_nbu", "amount", qty(0.48, "mmol")), ("_nbu", "concentration", qty(1.6, "M")), ("_znbr2", "mass", qty(180, "mg")), ("_znbr2", "amount", qty(0.80, "mmol")), ("_pd", "mass", qty(16, "mg")), ("_electrophile", "volume", qty(40, "uL")), ("_electrophile", "amount", qty(0.27, "mmol")), ("_prod", "mass", qty(18, "mg"))]),
    ("table3_entry1_13a", "t3e1", [("_sub", "mass", qty(56, "mg")), ("_sub", "amount", qty(0.39, "mmol")), ("_nbu", "volume", qty(0.30, "mL")), ("_nbu", "amount", qty(0.47, "mmol")), ("_nbu", "concentration", qty(1.6, "M")), ("_znbr2", "mass", qty(178, "mg")), ("_znbr2", "amount", qty(0.79, "mmol")), ("_pd", "mass", qty(15, "mg")), ("_electrophile", "volume", qty(29, "uL")), ("_electrophile", "amount", qty(0.26, "mmol")), ("_prod", "mass", qty(41, "mg"))]),
]:
    for ending, name, value in vals:
        add_amount(suffix, prefix + ending, 6, name, value)


# THF and explicit workup for 5a/13a detailed procedures.
for suffix, prefix, thf_volume in [("table1_entry1_5a", "t1e1", 3), ("table3_entry1_13a", "t3e1", 3)]:
    rec = by_id[f"{DOC}:{suffix}"]
    solvent_id = prefix + "_thf"
    rec["participants"].append(part(solvent_id, "solvent", "tetrahydrofuran", "THF", evid(4 if "5a" in suffix else 6), "C1CCOC1", [amount("volume", qty(thf_volume, "mL"), evid(4 if "5a" in suffix else 6))]))
    rec["steps"][0]["participant_ids"].append(solvent_id)
    rec["steps"].append(step("workup_isolation", [], [field("workup", "quench with saturated aqueous NH4Cl; extract with ether; dry over anhydrous MgSO4", evid(4 if "5a" in suffix else 6)), field("purification", "rotary evaporation and flash chromatography on silica gel with petroleum ether", evid(4 if "5a" in suffix else 6))]))


# Exact THF amount for 13a transmetallation solution.
by_id[f"{DOC}:table3_entry1_13a"]["participants"].append(part("t3e1_thf_zn", "solvent", "tetrahydrofuran for ZnBr2 solution", "THF", evid(6), "C1CCOC1", [amount("volume", qty(4, "mL"), evid(6))]))
by_id[f"{DOC}:table3_entry1_13a"]["steps"][1]["participant_ids"].append("t3e1_thf_zn")


# Coverage ledger: page entries are intentionally exactly 1-6.
def ids(*suffixes):
    return [f"{DOC}:{s}" for s in suffixes]


coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1,
            "state": "attempted",
            "regions": [
                {"region": "title, abstract, introduction and results prose", "finding": "Context and cited prior work; no additional independent experiment created from the prose.", "evidence_ids": evid(1)},
                {"region": "Scheme 1 and caption at page bottom", "finding": "Reported lithiation/benzylation of 1 giving products 2 and 3 with combined NMR yield and product ratio; merged with detailed section 3.2.1.1 on page 5.", "evidence_ids": evid(1)},
            ],
            "record_ids": ids("scheme1_1_to_2_3"),
            "unresolved": ["Scheme 1 does not report the duration after benzyl bromide addition."]
        },
        {
            "page": 2,
            "state": "attempted",
            "regions": [
                {"region": "Table 1 including reaction header, five rows and footnotes", "finding": "Five distinct electrophile scope experiments; footnote overrides for entry 2 and entry 4 were structured.", "evidence_ids": evid(2)},
                {"region": "Scheme 2 upper-middle", "finding": "Two specific ring-size control experiments, each producing an allene/alkyne pair with combined yield and ratio.", "evidence_ids": evid(2)},
                {"region": "Table 2 at page bottom", "finding": "Six distinct Negishi-type cross-coupling scope rows forming allenes 12a-12f.", "evidence_ids": evid(2)},
                {"region": "results prose between schemes and tables", "finding": "Interpretive comparison of current experiments; no separate experiment beyond the linked table/scheme rows.", "evidence_ids": evid(2)},
            ],
            "record_ids": ids("table1_entry1_5a", "table1_entry2_5b", "table1_entry3_5c", "table1_entry4_5d", "table1_entry5_5e", "scheme2_cyclobutyl_7_8", "scheme2_cyclohexyl_10_11", "table2_entry1_12a", "table2_entry2_12b", "table2_entry3_12c", "table2_entry4_12d", "table2_entry5_12e", "table2_entry6_12f"),
            "unresolved": ["Several table-only rows omit reaction-completion time and yield basis; these remain missing rather than inferred."]
        },
        {
            "page": 3,
            "state": "attempted",
            "regions": [
                {"region": "Table 3 including reaction header and entries 1-11", "finding": "Eleven distinct cyclopropyl-alkyne cross-coupling scope experiments; shared conditions applied row-wise.", "evidence_ids": evid(3)},
                {"region": "Scheme 3 center", "finding": "One experiment with 1,4-diiodobenzene and two product-specific yields (13l and 13l').", "evidence_ids": evid(3)},
                {"region": "Scheme 4 lower half, reactions to 14 and 15", "finding": "Two ring-size control experiments yielding allenes 14 and 15.", "evidence_ids": evid(3)},
                {"region": "generic structure 16 and explanatory conclusion", "finding": "Mechanistic/general strained vinylidenecyclopropane structure; classified as mechanism, not as an isolated experiment.", "evidence_ids": evid(3)},
            ],
            "record_ids": ids(*[f"table3_entry{i}_{label}" for i, label in enumerate(["13a", "13b", "13c", "13d", "13e", "13f", "13g", "13h", "13i", "13j", "13k"], 1)], "scheme3_13l_13lprime", "scheme4_cyclobutyl_14", "scheme4_cyclohexyl_15", "mechanism_vinylidenecyclopropane_16"),
            "unresolved": ["Table-only cross-coupling completion times and most yield bases are not reported on this page."]
        },
        {
            "page": 4,
            "state": "attempted",
            "regions": [
                {"region": "section 3.1.1", "finding": "Detailed preparation of starting material 1.", "evidence_ids": evid(4)},
                {"region": "sections 3.1.2 and 3.1.3", "finding": "Preparations of alkynes 4a and 4b; 4b is explicitly stated to follow the 4a procedure.", "evidence_ids": evid(4)},
                {"region": "sections 3.1.4 and 3.1.5", "finding": "Cyclobutylacetylene preparation followed by a distinct coupling preparation of 6; successive stages kept separate.", "evidence_ids": evid(4)},
                {"region": "section 3.1.6", "finding": "Detailed preparation of 1-cyclohexyl-2-phenylacetylene 9.", "evidence_ids": evid(4)},
                {"region": "section 3.2.1", "finding": "Detailed experiment for 5a; merged with Table 1 entry 1 rather than duplicated.", "evidence_ids": evid(4)},
            ],
            "record_ids": ids("prep_1", "prep_4a", "prep_4b", "prep_cyclobutylacetylene", "prep_6", "prep_9", "table1_entry1_5a"),
            "unresolved": ["TLC-completion statements provide no numeric duration for several couplings; cyclobutylacetylene yield is unreported."]
        },
        {
            "page": 5,
            "state": "attempted",
            "regions": [
                {"region": "section 3.2.1.1", "finding": "Detailed Scheme 1 experiment producing 2 and 3; merged with page 1 record.", "evidence_ids": evid(5)},
                {"region": "section 3.2.1.2", "finding": "Detailed Table 1 entry 2 producing 5b and byproduct 4a'; both product yields retained in one experiment.", "evidence_ids": evid(5)},
                {"region": "sections 3.2.1.3 and 3.2.1.4", "finding": "Detailed Table 1 entries for 5c and 5d; merged with their page 2 rows.", "evidence_ids": evid(5)},
                {"region": "section 3.2.1.5 beginning", "finding": "Detailed Table 1 entry for 5e begins here and continues onto page 6; one record spans both pages.", "evidence_ids": evid(5)},
            ],
            "record_ids": ids("scheme1_1_to_2_3", "table1_entry2_5b", "table1_entry3_5c", "table1_entry4_5d", "table1_entry5_5e"),
            "unresolved": ["These derivative paragraphs inherit the typical procedure but do not restate every solvent, temperature stage, workup, or completion time."]
        },
        {
            "page": 6,
            "state": "attempted",
            "regions": [
                {"region": "top-left continuation of section 3.2.1.5", "finding": "Characterization continuation for 5e; part of the page 5 experiment, not a new record.", "evidence_ids": evid(6)},
                {"region": "sections 3.2.1.6 and 3.2.1.7", "finding": "Detailed Scheme 2 cyclobutyl and cyclohexyl control experiments; merged with page 2 records.", "evidence_ids": evid(6)},
                {"region": "section 3.2.2", "finding": "Detailed preparation of 13a; merged with Table 3 entry 1.", "evidence_ids": evid(6)},
                {"region": "sections 3.2.2.1 and 3.2.2.2", "finding": "Detailed preparations of 12a and 12b; merged with Table 2 entries 1 and 2.", "evidence_ids": evid(6)},
            ],
            "record_ids": ids("table1_entry5_5e", "scheme2_cyclobutyl_7_8", "scheme2_cyclohexyl_10_11", "table3_entry1_13a", "table2_entry1_12a", "table2_entry2_12b"),
            "unresolved": ["Reaction completion after palladium/electrophile addition is monitored by TLC but no numeric duration is given."]
        },
    ]
}


OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
COVERAGE.parent.mkdir(parents=True, exist_ok=True)
COVERAGE.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")
tasks_path = Path(__file__).parents[1] / "tasks.json"
tasks = json.loads(tasks_path.read_text())
for task in tasks:
    if task.get("document_id") == DOC and task.get("evidence_id") in {f"{DOC}:page{p}:text" for p in range(1, 7)}:
        task["state"] = "attempted"
        task["reason"] = "Original page image inspected; regions and linked records are documented in coverage/pages_0001_0006.json."
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"records": len(records), "records_file": str(OUT), "coverage_file": str(COVERAGE), "tasks_updated": 6}, ensure_ascii=False))
