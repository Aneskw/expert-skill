#!/usr/bin/env python3
"""Build evidence-linked raw records for doc_9eeb484825ce883e, PDF pages 1-6."""
from __future__ import annotations

import json
from pathlib import Path

DOC = "doc_9eeb484825ce883e"
BASE = Path(__file__).resolve().parents[1]
OUT = BASE / "raw_model" / "extracted_records_pages_0001_0006.json"
COVERAGE = BASE / "coverage" / "pages_0001_0006.json"


def ev(page: int) -> list[str]:
    return [f"{DOC}:page{page}:text", f"{DOC}:page{page}:image"]


def fact(value, evidence=None):
    return {
        "value": value,
        "evidence_ids": list(evidence or []),
        "verification": "missing" if value is None else "unreviewed",
    }


def field(name, value, evidence=None, targets=None):
    result = {"name": name, "fact": fact(value, evidence)}
    if targets:
        result["target_entity_ids"] = list(targets)
    return result


def participant(entity_id, role, label, evidence, name=None, smiles=None, amounts=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence) if label is not None else fact(None),
        "name": fact(name, evidence) if name is not None else fact(None),
        "smiles": fact(smiles, evidence) if smiles is not None else fact(None),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": list(amounts or []),
    }


def record(rid, kind, evidence, participants=None, steps=None, outcomes=None, notes=None, unresolved=None):
    return {
        "record_id": f"{DOC}:{rid}",
        "document_id": DOC,
        "source_reaction_id": rid,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": list(dict.fromkeys(evidence)),
        "participants": list(participants or []),
        "steps": list(steps or []),
        "outcomes": list(outcomes or []),
        "notes": [fact(x, evidence) for x in (notes or [])],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": list(unresolved or []),
        },
    }


def amount(name, number, unit, evidence):
    return field(name, {"number": number, "unit": unit}, evidence)


def standard_agents(evidence, solvent="acetonitrile", solvent_smiles="CC#N", solvent_volume=3):
    return [
        participant("cat", "catalyst", "[PdCl2(CH3CN)2]", evidence,
                    name="bis(acetonitrile)palladium(II) dichloride",
                    amounts=[amount("catalyst_loading", 5, "mol%", evidence)]),
        participant("solvent", "solvent", solvent, evidence, name=solvent,
                    smiles=solvent_smiles,
                    amounts=[amount("volume", solvent_volume, "mL", evidence)]),
    ]


records = []

# Page 2, Scheme 1: conceptual taxonomy, not a reported experiment.
records.append(record(
    "scheme1_reaction_patterns", "general_scheme", ev(2),
    notes=["Scheme 1 presents generic uniallene, self-dimeric coupling, and heterodimeric coupling-cyclization patterns using R/FG placeholders."],
    unresolved=["Generic R-group drawings are not fully specified molecules and no experiment-specific conditions or outcomes are reported."],
))

# Page 2, Table 1: each optimization/control row is independent.
solvents = {
    "THF": "C1CCOC1", "CH2Cl2": "ClCCl", "acetone": "CC(C)=O",
    "toluene": "Cc1ccccc1", "DMA": "CC(=O)N(C)C", "CH3CN": "CC#N",
}
table1 = [
    (1, "THF", 11, 14, 0, None),
    (2, "CH2Cl2", 11, 23, 14, None),
    (3, "acetone", 11, 40, 0, None),
    (4, "toluene", 16.5, 13, 18, None),
    (5, "DMA", 17.5, 76, 0, None),
    (6, "CH3CN", 4, 90, 0, None),
    (7, "CH3CN", 11.5, 57, 12, "three_equiv_2a"),
    (8, "CH3CN", 4, 90, 0, "argon"),
    (9, "CH3CN", 11, 0, None, "base_salt"),
]
for entry, solvent, hours, y3a, y4a, special in table1:
    evidence = ev(2) + (ev(3) if entry in (8, 9) else [])
    p1a = participant("1a", "reactant", "1a", evidence,
                      name="3-(n-propyl)-4-phenyl-2,3-butadienoic acid",
                      smiles="O=C(O)C(CCC)=C=C(c1ccccc1)",
                      amounts=[amount("amount", 0.25, "mmol", evidence)])
    a2 = [amount("equivalents", 3, "equiv", evidence)] if special == "three_equiv_2a" else [amount("amount", 1.25, "mmol", evidence)]
    p2a = participant("2a", "reactant", "2a", evidence,
                      name="penta-3,4-dien-2-one", smiles="C=C=CC(=O)C", amounts=a2)
    p3a = participant("3a", "product", "3a", evidence,
                      name="4-(3-(5-methylfuranyl))-5-phenyl-3-propyl-2(5H)-furanone",
                      smiles="O=C1OC(c2ccccc2)C(c2cc(C)oc2)=C1CCC")
    p4a = participant("4a", "product", "4a", evidence,
                      name="cycloisomerization furanone 4a")
    agents = standard_agents(evidence, solvent, solvents[solvent], 3)
    if special == "base_salt":
        agents += [
            participant("k2co3", "reagent", "K2CO3", evidence, name="potassium carbonate",
                        smiles="[K+].[K+].[O-]C([O-])=O",
                        amounts=[amount("equivalents", 1, "equiv", evidence)]),
            participant("bu4nbr", "reagent", "Bu4NBr", evidence, name="tetrabutylammonium bromide",
                        smiles="CCCC[N+](CCCC)(CCCC)CCCC.[Br-]",
                        amounts=[amount("equivalents", 1, "equiv", evidence)]),
        ]
    conditions = [field("time", {"number": hours, "unit": "h"}, evidence), field("temperature", None)]
    if special == "argon":
        conditions.append(field("atmosphere", "argon", evidence))
    else:
        conditions.append(field("atmosphere", None))
    outcomes = [
        field("yield_3a", {"number": y3a, "unit": "%"}, evidence, ["3a"]),
        field("yield_4a", None if y4a is None else {"number": y4a, "unit": "%"}, evidence if y4a is not None else [], ["4a"]),
        field("yield_measurement_basis", None),
    ]
    unresolved = ["Reaction temperature and yield measurement basis are not stated in Table 1.", "Supporting-information association is unestablished."]
    if y4a is None:
        unresolved.append("The 4a-yield cell is a dash; it is preserved as missing rather than converted to zero.")
    records.append(record(
        f"table1_entry_{entry:02d}", "optimization_entry", evidence,
        participants=[p1a, p2a, p3a, p4a] + agents,
        steps=[{"step_id": "reaction", "participant_ids": [p["entity_id"] for p in [p1a, p2a] + agents], "conditions": conditions}],
        outcomes=outcomes,
        unresolved=unresolved,
    ))

# Page 2, Equations 1 and 2: explicitly failed polysubstituted allenyl-ketone cases.
for eq_no, ketone, target, ketone_name in [
    (1, "2d", "3w", "polysubstituted 1,2-allenyl methyl ketone 2d"),
    (2, "2e", "3x", "n-heptyl-substituted 1,2-allenyl methyl ketone 2e"),
]:
    evidence = ev(2)
    ps = [
        participant("1a", "reactant", "1a", evidence, name="3-(n-propyl)-4-phenyl-2,3-butadienoic acid", smiles="O=C(O)C(CCC)=C=C(c1ccccc1)"),
        participant(ketone, "reactant", ketone, evidence, name=ketone_name),
        participant(target, "product", target, evidence, name=f"depicted but not obtained product {target}"),
    ] + standard_agents(evidence)
    records.append(record(
        f"equation_{eq_no}_failed_{ketone}", "substrate_scope_entry", evidence,
        participants=ps,
        steps=[{"step_id": "reaction", "participant_ids": [p["entity_id"] for p in ps if p["role"] != "product"], "conditions": [field("temperature", "r.t.", evidence), field("time", {"number": 11, "unit": "h"}, evidence)]}],
        outcomes=[field("product_yield", "not obtained", evidence, [target]), field("yield_measurement_basis", None)],
        notes=["The arrow is crossed out and the prose states that polysubstituted 1,2-allenyl ketones did not yield the corresponding products."],
        unresolved=["Reactant and target structures are retained by labels because the substituted allene drawings were not converted to verified structures.", "Supporting-information association is unestablished."],
    ))

# Connectivity candidates for the Table 2 series. Stereochemical verification is deliberately false.
acid_info = {
    "1a": ("2,3-allenoic acid 1a (R1=Ph, R2=n-C3H7, R3=H)", "O=C(O)C(CCC)=C=C(c1ccccc1)"),
    "1b": ("2,3-allenoic acid 1b (R1=Ph, R2=CH3, R3=H)", "O=C(O)C(C)=C=C(c1ccccc1)"),
    "1c": ("2,3-allenoic acid 1c (R1=Ph, R2=PhCH2, R3=H)", "O=C(O)C(Cc1ccccc1)=C=C(c1ccccc1)"),
    "1d": ("2,3-allenoic acid 1d (R1=Ph, R2=allyl, R3=H)", "O=C(O)C(CC=C)=C=C(c1ccccc1)"),
    "1e": ("2,3-allenoic acid 1e (R1=alpha-naphthyl, R2=CH3, R3=H)", "O=C(O)C(C)=C=C(c1cccc2ccccc12)"),
    "1f": ("2,3-allenoic acid 1f (R1=alpha-naphthyl, R2=n-C3H7, R3=H)", "O=C(O)C(CCC)=C=C(c1cccc2ccccc12)"),
    "1g": ("2,3-allenoic acid 1g (R1=CH3, R2=PhCH2, R3=H)", "O=C(O)C(Cc1ccccc1)=C=CC"),
    "1h": ("2,3-allenoic acid 1h (R1=Ph, R2=CH3, R3=Et)", "O=C(O)C(C)=C=C(CC)(c1ccccc1)"),
    "1i": ("2,3-allenoic acid 1i (R1=n-C7H15, R2=H, R3=H)", "O=C(O)C=C=C(CCCCCCC)"),
    "1j": ("2,3-allenoic acid 1j (R1=4-Br-Ph, R2=n-C3H7, R3=H)", "O=C(O)C(CCC)=C=C(c1ccc(Br)cc1)"),
}
ketone_info = {
    "2a": ("1,2-allenyl ketone 2a (R4=CH3)", "C=C=CC(=O)C"),
    "2b": ("1,2-allenyl ketone 2b (R4=n-C4H9)", "C=C=CC(=O)CCCC"),
    "2c": ("1,2-allenyl ketone 2c (R4=PhCH2)", "C=C=CC(=O)Cc1ccccc1"),
}
scope = [
    (1,"1a","2a","3a",90),(2,"1b","2a","3b",73),(3,"1c","2a","3c",92),
    (4,"1d","2a","3d",86),(5,"1e","2a","3e",84),(6,"1f","2a","3f",86),
    (7,"1g","2a","3g",90),(8,"1h","2a","3h",85),(9,"1i","2a","3i",69),
    (10,"1j","2a","3j",70),(11,"1a","2b","3k",84),(12,"1b","2b","3l",63),
    (13,"1d","2b","3m",66),(14,"1e","2b","3n",79),(15,"1h","2b","3o",86),
    (16,"1i","2b","3p",69),(17,"1a","2c","3q",74),(18,"1b","2c","3r",86),
    (19,"1d","2c","3s",82),(20,"1e","2c","3t",90),(21,"1h","2c","3u",84),
    (22,"1i","2c","3v",71),
]
product_names = {
    "3a":"4-(3-(5-methylfuranyl))-5-phenyl-3-propyl-2(5H)-furanone",
    "3b":"3-methyl-4-(3-(5-methylfuranyl))-5-phenyl-2(5H)-furanone",
    "3c":"3-benzyl-4-(3-(5-methylfuranyl))-5-phenyl-2(5H)-furanone",
    "3d":"3-allyl-4-(3-(5-methylfuranyl))-5-phenyl-2(5H)-furanone",
    "3e":"3-methyl-4-(3-(5-methylfuranyl))-5-(1-naphthyl)-2(5H)-furanone",
    "3f":"4-(3-(5-methylfuranyl))-5-(1-naphthyl)-3-propyl-2(5H)-furanone",
    "3g":"3-benzyl-5-methyl-4-(3-(5-methylfuranyl))-2(5H)-furanone",
}
product_smiles = {
    "3a":"O=C1OC(c2ccccc2)C(c2cc(C)oc2)=C1CCC",
    "3b":"O=C1OC(c2ccccc2)C(c2cc(C)oc2)=C1C",
    "3c":"O=C1OC(c2ccccc2)C(c2cc(C)oc2)=C1Cc1ccccc1",
    "3d":"O=C1OC(c2ccccc2)C(c2cc(C)oc2)=C1CC=C",
    "3e":"O=C1OC(c2cccc3ccccc23)C(c2cc(C)oc2)=C1C",
    "3f":"O=C1OC(c2cccc3ccccc23)C(c2cc(C)oc2)=C1CCC",
    "3g":"O=C1OC(C)C(c2cc(C)oc2)=C1Cc1ccccc1",
}
detailed = {
    "3a": {"acid": (50,0.248), "ketone": (103,1.26), "cat": (3,0.012), "solvent":3, "time":4, "mass":63, "state":"white solid", "purification":"flash chromatography on silica gel (petroleum ether/Et2O 3:1)"},
    "3b": {"acid": (44,0.253), "ketone": (108,1.317), "cat": (3,0.012), "solvent":3, "time":4, "mass":47, "state":"white solid", "purification":"flash chromatography on silica gel (CH2Cl2, then ethyl acetate/petroleum ether 1:2)"},
    "3c": {"acid": (125,0.5), "ketone": (205,2.5), "cat": (6,0.023), "solvent":5, "time":3.5, "mass":151, "state":"white solid", "purification":"flash chromatography on silica gel (CH2Cl2, then petroleum ether/ethyl acetate 15:1)"},
    "3d": {"acid": (50,0.25), "ketone": (108,1.32), "cat": (3,0.012), "solvent":3, "time":6, "mass":60, "state":"oil", "purification":"flash chromatography on silica gel (petroleum ether/ethyl acetate 5:1)"},
    "3e": {"acid": (56,0.25), "ketone": (103,1.256), "cat": (3,0.012), "solvent":3, "time":4, "mass":64, "state":"white solid", "purification":"flash chromatography on silica gel (petroleum ether/ethyl acetate 4:1, then CH2Cl2)"},
    "3f": {"acid": (126,0.5), "ketone": (205,2.5), "cat": (6,0.023), "solvent":5, "time":4, "mass":143, "state":"oil", "purification":"flash chromatography on silica gel (petroleum ether/Et2O 5:1)"},
    "3g": {"acid": (94,0.5), "ketone": (207,2.5), "cat": (6,0.023), "solvent":5, "time":4, "mass":120, "state":"oil", "purification":"flash chromatography on silica gel (petroleum ether/ethyl acetate 10:1, then CH2Cl2)"},
}

for entry, acid, ketone, product, yield_value in scope:
    evidence = ev(3) + (ev(6) if product in detailed else [])
    acid_name, acid_smiles = acid_info[acid]
    ketone_name, ketone_smiles = ketone_info[ketone]
    d = detailed.get(product)
    if d:
        acid_amounts = [amount("mass", d["acid"][0], "mg", ev(6)), amount("amount", d["acid"][1], "mmol", ev(6))]
        ketone_amounts = [amount("mass", d["ketone"][0], "mg", ev(6)), amount("amount", d["ketone"][1], "mmol", ev(6))]
        catalyst_amounts = [amount("mass", d["cat"][0], "mg", ev(6)), amount("amount", d["cat"][1], "mmol", ev(6))]
        solvent_amounts = [amount("volume", d["solvent"], "mL", ev(6))]
        time_value = d["time"]
    else:
        acid_amounts = [amount("amount", 0.25, "mmol", ev(3))]
        ketone_amounts = [amount("amount", 1.25, "mmol", ev(3))]
        catalyst_amounts = [amount("catalyst_loading", 5, "mol%", ev(3))]
        solvent_amounts = [amount("volume", 3, "mL", ev(3))]
        time_value = 4
    ps = [
        participant(acid, "reactant", acid, evidence, name=acid_name, smiles=acid_smiles, amounts=acid_amounts),
        participant(ketone, "reactant", ketone, evidence, name=ketone_name, smiles=ketone_smiles, amounts=ketone_amounts),
        participant(product, "product", product, evidence, name=product_names.get(product, f"Table 2 product {product}"), smiles=product_smiles.get(product)),
        participant("cat", "catalyst", "[PdCl2(CH3CN)2]", evidence, name="bis(acetonitrile)palladium(II) dichloride", amounts=catalyst_amounts),
        participant("solvent", "solvent", "CH3CN", evidence, name="acetonitrile", smiles="CC#N", amounts=solvent_amounts),
    ]
    outcomes = [field("product_yield", {"number": yield_value, "unit": "%"}, ev(3), [product])]
    if d:
        outcomes += [
            field("product_mass", {"number": d["mass"], "unit": "mg"}, ev(6), [product]),
            field("physical_form", d["state"], ev(6), [product]),
            field("yield_measurement_basis", "isolated after flash chromatography", ev(6), [product]),
        ]
        extra_conditions = [field("purification", d["purification"], ev(6))]
    else:
        outcomes.append(field("yield_measurement_basis", None))
        extra_conditions = []
    unresolved = ["Supporting-information association is unestablished."]
    if not d:
        unresolved += ["The Table 2 yield measurement basis, workup, and product mass are not reported on the inspected pages.", "Product SMILES was left null where only the table drawing/label was used and no confident connectivity candidate was created."]
    if product == "3g":
        unresolved.append("The detailed 3g sentence continues onto PDF page 7, outside the claimed inspection range; its yield is taken only from Table 2 on page 3.")
    records.append(record(
        f"table2_entry_{entry:02d}_{product}", "substrate_scope_entry", evidence,
        participants=ps,
        steps=[{"step_id":"reaction", "participant_ids":[acid,ketone,"cat","solvent"], "conditions":[field("temperature","r.t.",evidence), field("time", {"number":time_value,"unit":"h"}, evidence)] + extra_conditions}],
        outcomes=outcomes,
        unresolved=unresolved,
    ))

# Page 3 Equation 3, with page 4 X-ray confirmation: independent chiral 1j experiment.
evidence = ev(3) + ev(4)
ps = [
    participant("S_1j", "reactant", "(S)-(+)-1j", evidence, name="optically active 2,3-allenoic acid 1j", smiles=acid_info["1j"][1], amounts=[amount("starting_material_ee", 99, "%", ev(3))]),
    participant("2a", "reactant", "2a", evidence, name=ketone_info["2a"][0], smiles=ketone_info["2a"][1]),
    participant("S_3j", "product", "(S)-(+)-3j", evidence, name="(S)-4-(3-(5-methylfuranyl))-5-(4-bromophenyl)-3-propyl-2(5H)-furanone"),
] + standard_agents(evidence)
records.append(record(
    "equation3_chiral_1j_to_3j", "reported_experiment", evidence,
    participants=ps,
    steps=[{"step_id":"reaction", "participant_ids":["S_1j","2a","cat","solvent"], "conditions":[field("temperature","r.t.",ev(3)),field("time",{"number":4,"unit":"h"},ev(3))]}],
    outcomes=[field("product_yield",{"number":76,"unit":"%"},ev(3),["S_3j"]),field("product_ee",{"number":99,"unit":"%"},ev(3),["S_3j"]),field("absolute_configuration","S",ev(4),["S_3j"]),field("yield_measurement_basis",None)],
    notes=["Figure 2 reports X-ray assignment of the product as S configuration."],
    unresolved=["Reactant axial stereochemistry and product stereochemistry are not encoded in the candidate SMILES.", "Reactant amounts, workup, purification, and yield basis are not given in Equation 3.", "Supporting-information association is unestablished."],
))

# Pages 3-4, Scheme 2: byproduct distribution is a reported product study, separate from Table 2.
evidence = ev(3) + ev(4)
ps = [
    participant("1a", "reactant", "1a", evidence, name=acid_info["1a"][0], smiles=acid_info["1a"][1]),
    participant("2a", "reactant", "2a", evidence, name=ketone_info["2a"][0], smiles=ketone_info["2a"][1]),
    participant("3a", "product", "3a", evidence, name=product_names["3a"], smiles=product_smiles["3a"]),
    participant("5a", "product", "5a", evidence, name="homodimerization furan product 5a"),
    participant("6a", "product", "6a", evidence, name="4,5-dimethyleneocta-2,7-dione", smiles="CC(=O)CC(=C)C(=C)CC(=O)C"),
    participant("7a", "product", "7a", evidence, name="4-methyl-5-methylene-3-octene-2,7-dione", smiles="CC(=O)C=C(C)C(=C)CC(=O)C"),
    participant("8a", "product", "8a", evidence, name="4,5-dimethylocta-3,5-diene-2,7-dione", smiles="CC(=O)C=C(C)C(C)=CC(=O)C"),
    participant("cat", "catalyst", "[PdCl2(CH3CN)2]", evidence, name="bis(acetonitrile)palladium(II) dichloride", amounts=[amount("catalyst_loading",5,"mol%",ev(4))]),
]
records.append(record(
    "scheme2_byproduct_distribution", "reported_experiment", evidence,
    participants=ps,
    steps=[{"step_id":"reaction", "participant_ids":["1a","2a","cat"], "conditions":[field("temperature",None),field("time",None),field("solvent",None)]}],
    outcomes=[
        field("yield_5a",{"number":13,"unit":"%"},ev(4),["5a"]),
        field("yield_6a",{"number":6,"unit":"%"},ev(4),["6a"]),
        field("yield_7a",{"number":21,"unit":"%"},ev(4),["7a"]),
        field("yield_8a",{"number":13,"unit":"%"},ev(4),["8a"]),
        field("yield_measurement_basis","calculated based on penta-3,4-dien-2-one",ev(4),["5a","6a","7a","8a"]),
    ],
    unresolved=["Scheme 2 does not state solvent, temperature, time, reactant amounts, 3a yield, workup, or purification.", "It is not explicitly established that Scheme 2 is the identical physical run as a Table 1 or Table 2 entry, so it remains separate.", "Supporting-information association is unestablished."],
))

# Page 4, Scheme 3: mechanistic proposal, not a reaction experiment.
evidence = ev(4)
ps = [
    participant("mech_1a", "reactant", "1a", evidence, name=acid_info["1a"][0], smiles=acid_info["1a"][1]),
    participant("mech_2a", "reactant", "2a", evidence, name=ketone_info["2a"][0], smiles=ketone_info["2a"][1], amounts=[amount("mechanistic_equivalents",2,"equiv",evidence)]),
    participant("mech_hcl", "reagent", "HCl", evidence, name="hydrogen chloride", smiles="Cl", amounts=[amount("mechanistic_equivalents",2,"equiv",evidence)]),
    participant("mech_3a", "product", "3a", evidence, name=product_names["3a"], smiles=product_smiles["3a"]),
]
records.append(record(
    "scheme3_proposed_catalytic_cycle", "mechanism", evidence,
    participants=ps,
    steps=[{"step_id":"proposed_cycle", "participant_ids":["mech_1a","mech_2a","mech_hcl","mech_3a"], "conditions":[field("operation","proposed double oxypalladation, reductive elimination, cyclometallation, and protonolysis",evidence)]}],
    notes=["Scheme 3 is explicitly titled a proposed catalytic cycle and includes intermediates 9a, 10a, and 10a prime."],
    unresolved=["Mechanistic intermediates and stoichiometry are proposals, not independently reported experimental operations or yields."],
))

# Pages 5-6, Table 3: each chiral scope row is independent.
chiral_rows = [
    (1,"S_1a","(S)-(+)-1a",98,"2a","S_3a","(S)-(+)-3a",87,95),
    (2,"R_1a","(R)-(-)-1a",97,"2b","R_3k","(R)-(-)-3k",75,">99"),
    (3,"R_1a","(R)-(-)-1a",97,"2c","R_3q","(R)-(-)-3q",86,">99"),
    (4,"R_1b","(R)-(-)-1b",99,"2a","R_3b","(R)-(-)-3b",76,97),
    (5,"R_1b","(R)-(-)-1b",99,"2b","R_3l","(R)-(-)-3l",81,99),
    (6,"R_1b","(R)-(-)-1b",99,"2c","R_3r","(R)-(-)-3r",72,96),
    (7,"S_1d","(S)-(-)-1d",98,"2a","S_3d","(S)-(+)-3d",73,97),
    (8,"S_1d","(S)-(-)-1d",98,"2b","S_3m","(S)-(+)-3m",67,99),
    (9,"S_1d","(S)-(-)-1d",98,"2c","S_3s","(S)-(+)-3s",67,98),
    (10,"S_1e","(S)-(+)-1e",98,"2a","S_3e","(S)-(-)-3e",74,97),
    (11,"S_1e","(S)-(+)-1e",98,"2b","S_3n","(S)-(-)-3n",76,99),
    (12,"S_1e","(S)-(+)-1e",98,"2c","S_3t","(S)-(-)-3t",87,">99"),
]
base_product = {"S_3a":"3a","R_3k":"3k","R_3q":"3q","R_3b":"3b","R_3l":"3l","R_3r":"3r","S_3d":"3d","S_3m":"3m","S_3s":"3s","S_3e":"3e","S_3n":"3n","S_3t":"3t"}
base_acid = {"S_1a":"1a","R_1a":"1a","R_1b":"1b","S_1d":"1d","S_1e":"1e"}
for entry, acid_id, acid_label, acid_ee, ketone, product_id, product_label, yld, prod_ee in chiral_rows:
    page = 5 if entry <= 10 else 6
    evidence = ev(page)
    akey = base_acid[acid_id]
    pkey = base_product[product_id]
    ee_value = {"number":99,"unit":"%","qualifier":"gt","raw_text":">99%"} if prod_ee == ">99" else {"number":prod_ee,"unit":"%"}
    ps = [
        participant(acid_id,"reactant",acid_label,evidence,name=acid_info[akey][0],smiles=acid_info[akey][1],amounts=[amount("starting_material_ee",acid_ee,"%",evidence)]),
        participant(ketone,"reactant",ketone,evidence,name=ketone_info[ketone][0],smiles=ketone_info[ketone][1]),
        participant(product_id,"product",product_label,evidence,name=product_names.get(pkey,f"chiral Table 3 product {product_label}"),smiles=product_smiles.get(pkey)),
    ] + standard_agents(evidence)
    records.append(record(
        f"table3_entry_{entry:02d}_{pkey}", "substrate_scope_entry", evidence,
        participants=ps,
        steps=[{"step_id":"reaction", "participant_ids":[acid_id,ketone,"cat","solvent"], "conditions":[field("temperature","r.t.",evidence),field("time",{"number":4,"unit":"h"},evidence)]}],
        outcomes=[field("product_yield",{"number":yld,"unit":"%"},evidence,[product_id]),field("product_ee",ee_value,evidence,[product_id]),field("yield_measurement_basis",None)],
        unresolved=["Table 3 does not report reactant amounts, workup, purification, or yield measurement basis on the inspected pages.", "Axial/product stereochemistry is preserved in labels but is not encoded in candidate SMILES.", "Supporting-information association is unestablished."],
    ))

# Page 6 starting-material preparations explicitly refer to prior methods.
evidence = ev(6)
ps = [
    participant("acid_chlorides","reactant","acid chlorides",evidence,name="acid chlorides"),
    participant("ylide","reagent","ethyl 2-(triphenylphosphoranylidene)propionate",evidence,name="ethyl 2-(triphenylphosphoranylidene)propionate"),
    participant("allenoic_esters","product","2,3-allenoic esters",evidence,name="2,3-allenoic esters"),
    participant("naoh","reagent","NaOH",evidence,name="sodium hydroxide",smiles="[Na+].[OH-]",amounts=[amount("equivalents",1.5,"equiv",evidence)]),
    participant("allenoic_acids","product","1a-j",evidence,name="2,3-allenoic acids 1a-j"),
]
records.append(record(
    "literature_starting_material_allenoic_acids", "literature_example", evidence,
    participants=ps,
    steps=[
        {"step_id":"ylide_reaction", "participant_ids":["acid_chlorides","ylide","allenoic_esters"], "conditions":[field("time",None),field("temperature",None),field("solvent",None)]},
        {"step_id":"hydrolysis", "participant_ids":["allenoic_esters","naoh","allenoic_acids"], "conditions":[field("time",None),field("temperature",None),field("solvent",None)]},
    ],
    notes=["The authors state that the starting materials were prepared according to a known method cited as reference 27."],
    unresolved=["This is a literature-referenced preparation, not a complete procedure reported in the inspected article pages; solvents, temperatures, times, workup, purification, and yields are missing.", "Generic acid chlorides/esters and the 1a-j set are not single fully specified structures."],
))
records.append(record(
    "literature_chiral_resolution_allenoic_acids", "literature_example", ev(1)+ev(6),
    participants=[
        participant("racemic_acids","reactant","racemic 2,3-allenoic acids",ev(1)+ev(6),name="racemic 2,3-allenoic acids"),
        participant("chiral_amine","reagent","optically active amine",ev(1)+ev(6),name="cinchonidine or alpha-methylbenzylamine"),
        participant("optically_active_acids","product","optically active 2,3-allenoic acids",ev(1)+ev(6),name="optically active 2,3-allenoic acids"),
    ],
    steps=[{"step_id":"chiral_resolution","participant_ids":["racemic_acids","chiral_amine","optically_active_acids"],"conditions":[field("time",None),field("temperature",None),field("solvent",None)]}],
    notes=["The page 6 experimental section refers the chiral resolution to an earlier publication; page 1 names the resolving amines as alternatives."],
    unresolved=["The source does not assign which resolving amine was used for each acid or provide procedure, quantities, yields, or resolution conditions on pages 1-6."],
))

# Coverage ledger: exactly the six pages visually inspected in this session.
ids = {r["source_reaction_id"]: r["record_id"] for r in records}
table1_ids = [ids[f"table1_entry_{i:02d}"] for i in range(1,10)]
eq12_ids = [ids["equation_1_failed_2d"], ids["equation_2_failed_2e"]]
table2_ids = [ids[f"table2_entry_{i:02d}_{p}"] for i,_,_,p,_ in scope]
table3_ids = [ids[f"table3_entry_{i:02d}_{base_product[pid]}"] for i,_,_,_,_,pid,_,_,_ in chiral_rows]
coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page":1,"state":"attempted",
            "regions":[
                {"region":"title, abstract, and introduction columns","finding":"Article overview and prior-work context; no discrete current-paper experiment or quantitative reaction row is reported here.","evidence_ids":[f"{DOC}:page1:image",f"{DOC}:page1:text"]},
                {"region":"abstract statement on chiral resolution","finding":"Prior-method preparation of optically active allenoic acids; classified as literature example, not a new experiment in this paper.","evidence_ids":[f"{DOC}:page1:image",f"{DOC}:page1:text"]},
            ],
            "record_ids":[ids["literature_chiral_resolution_allenoic_acids"]],
            "unresolved":["No SI was provided or associated; the introduction cites earlier work without reproducing its experimental details."],
        },
        {
            "page":2,"state":"attempted",
            "regions":[
                {"region":"Scheme 1, upper-left","finding":"Generic reaction-pattern taxonomy with R/FG placeholders; recorded as a general scheme, not an experiment.","evidence_ids":[f"{DOC}:page2:image",f"{DOC}:page2:text"]},
                {"region":"Table 1 and footnotes, left-middle","finding":"Nine independent optimization/control rows for 1a + 2a, including solvent/time/yields and footnote overrides.","evidence_ids":[f"{DOC}:page2:image",f"{DOC}:page2:text"]},
                {"region":"Equations 1 and 2, lower-right","finding":"Two crossed-arrow failed substrate cases (2d and 2e) under CH3CN, room temperature, 11 h.","evidence_ids":[f"{DOC}:page2:image",f"{DOC}:page2:text"]},
            ],
            "record_ids":[ids["scheme1_reaction_patterns"]]+table1_ids+eq12_ids,
            "unresolved":["Table 1 does not state reaction temperature or yield basis; structures 2d/2e/3w/3x remain label-only candidates."],
        },
        {
            "page":3,"state":"attempted",
            "regions":[
                {"region":"Figure 1, upper-left","finding":"X-ray structure of 3a; characterization evidence, not a separate reaction experiment.","evidence_ids":[f"{DOC}:page3:image",f"{DOC}:page3:text"]},
                {"region":"Table 2, center-left","finding":"Twenty-two independent substrate-scope rows with shared CH3CN/room-temperature/4 h conditions and row-specific yields.","evidence_ids":[f"{DOC}:page3:image",f"{DOC}:page3:text"]},
                {"region":"Equation 3, lower-left","finding":"Independent chiral 1j + 2a experiment affording (S)-3j in 76% yield and 99% ee.","evidence_ids":[f"{DOC}:page3:image",f"{DOC}:page3:text"]},
                {"region":"control/mechanistic prose, right column","finding":"Argon and base/salt controls cross-reference Table 1 entries 8 and 9; byproduct prose leads into Scheme 2 and is not duplicated.","evidence_ids":[f"{DOC}:page3:image",f"{DOC}:page3:text"]},
            ],
            "record_ids":table2_ids+[ids["equation3_chiral_1j_to_3j"],ids["table1_entry_08"],ids["table1_entry_09"],ids["scheme2_byproduct_distribution"]],
            "unresolved":["Most Table 2 rows provide no row-specific workup, purification, product mass, or yield basis on pages 1-6."],
        },
        {
            "page":4,"state":"attempted",
            "regions":[
                {"region":"Figure 2, upper-left","finding":"X-ray assignment of compound 3j as S; merged as evidence for Equation 3 rather than a new experiment.","evidence_ids":[f"{DOC}:page4:image",f"{DOC}:page4:text"]},
                {"region":"Scheme 2 and Figure 3, left column","finding":"Reported 1a/2a byproduct distribution (5a-8a) plus X-ray characterization of 8a; retained as a separate partial reported experiment.","evidence_ids":[f"{DOC}:page4:image",f"{DOC}:page4:text"]},
                {"region":"Scheme 3, right column","finding":"Explicitly proposed catalytic cycle; classified as mechanism, not a reported experiment.","evidence_ids":[f"{DOC}:page4:image",f"{DOC}:page4:text"]},
            ],
            "record_ids":[ids["equation3_chiral_1j_to_3j"],ids["scheme2_byproduct_distribution"],ids["scheme3_proposed_catalytic_cycle"]],
            "unresolved":["Scheme 2 omits time, temperature, solvent, scale, and 3a yield; identity with any optimization/scope run is not explicit."],
        },
        {
            "page":5,"state":"attempted",
            "regions":[
                {"region":"Table 3 entries 1-10","finding":"Ten independent chiral substrate-scope rows with starting-material ee, product yield, and product ee under shared conditions.","evidence_ids":[f"{DOC}:page5:image",f"{DOC}:page5:text"]},
            ],
            "record_ids":table3_ids[:10],
            "unresolved":["Table 3 does not give row-specific quantities, workup, purification, or yield basis on this page; stereochemistry remains label-level in candidate SMILES."],
        },
        {
            "page":6,"state":"attempted",
            "regions":[
                {"region":"Table 3 continued, entries 11-12","finding":"Two independent chiral substrate-scope rows completing Table 3.","evidence_ids":[f"{DOC}:page6:image",f"{DOC}:page6:text"]},
                {"region":"Experimental Section starting-material synthesis","finding":"Two prior-method preparations (allenoic-acid synthesis and chiral resolution), classified as literature examples because procedures are cited rather than fully reported.","evidence_ids":[f"{DOC}:page6:image",f"{DOC}:page6:text"]},
                {"region":"general procedure for compound 3","finding":"Shared catalyst, scale, solvent, room-temperature/4 h reaction, evaporation, and silica purification context; used only where supported and not counted as a separate experiment.","evidence_ids":[f"{DOC}:page6:image",f"{DOC}:page6:text"]},
                {"region":"individual procedures 3a-3g","finding":"Detailed amounts/times/purifications for 3a-3g were merged into matching Table 2 records rather than duplicated; 3g continues beyond page 6.","evidence_ids":[f"{DOC}:page6:image",f"{DOC}:page6:text"]},
            ],
            "record_ids":table3_ids[10:]+table2_ids[:7]+[ids["literature_starting_material_allenoic_acids"],ids["literature_chiral_resolution_allenoic_acids"]],
            "unresolved":["The detailed 3g sentence continues on page 7, outside the claimed page range; page 6 alone does not show its percentage yield.","Starting-material literature methods omit most operational details."],
        },
    ],
}

OUT.parent.mkdir(parents=True, exist_ok=True)
COVERAGE.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
COVERAGE.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"records": len(records), "raw": str(OUT), "coverage": str(COVERAGE)}, ensure_ascii=False))
