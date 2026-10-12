#!/usr/bin/env python3
"""Build evidence-linked machine records for source PDF pages 1-6."""
import json
from pathlib import Path

DOC = "doc_d84cc3c252b14204"
BASE = Path(__file__).resolve().parents[1]


def ev(*pages):
    out = []
    for page in pages:
        out.extend([f"{DOC}:page{page}:text", f"{DOC}:page{page}:image"])
    return out


def fact(value, evidence):
    return {
        "value": value,
        "evidence_ids": list(evidence),
        "verification": "missing" if value is None else "unreviewed",
    }


def field(name, value, evidence, targets=None):
    result = {"name": name, "fact": fact(value, evidence)}
    if targets:
        result["target_entity_ids"] = list(targets)
    return result


def participant(entity_id, role, label, name, evidence, amounts=None, smiles=None):
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


def record(rid, kind, evidence, participants, steps=None, outcomes=None, notes=None, unresolved=None):
    return {
        "record_id": f"{DOC}:{rid}",
        "document_id": DOC,
        "source_reaction_id": rid,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": list(dict.fromkeys(evidence)),
        "participants": participants,
        "steps": steps or [],
        "outcomes": outcomes or [],
        "notes": [fact(x, evidence) for x in (notes or [])],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved or [
                "No explicitly associated Supporting Information was supplied.",
                "Depicted structures and candidate structures remain unverified.",
            ],
        },
    }


def q(number, unit, qualifier=None, raw_text=None):
    value = {"number": number, "unit": unit}
    if qualifier:
        value["qualifier"] = qualifier
    if raw_text:
        value["raw_text"] = raw_text
    return value


SMILES = {
    "AcOH": "CC(=O)O",
    "HCO2H": "O=CO",
    "EtCO2H": "CCC(=O)O",
    "THF": "C1CCOC1",
    "Et2O": "CCOCC",
    "Ac2O": "CC(=O)OC(C)=O",
    "Et3N": "CCN(CC)CC",
    "DMAP": "CN(C)c1ccncc1",
    "NaH": "[Na+].[H-]",
    "MeI": "CI",
    "DCE": "ClCCCl",
    "NaCl": "[Na+].[Cl-]",
    "Na2SO4": "[Na+].[Na+].[O-]S(=O)(=O)[O-]",
    "3a": "COc1ccc(B(O)O)cc1",
    "3b": "OB(O)c1ccccc1",
    "3c": "Cc1ccc(B(O)O)cc1",
    "3d": "O=[N+]([O-])c1cccc(B(O)O)c1",
    "3e": "OB(O)c1ccc(-c2ccccc2)cc1",
}


def common_participants(evidence, substrate_label, substrate_name, reagent_label, reagent_name,
                        products, acid="AcOH", acid_loading=20, reagent_equiv=2.0):
    ps = [
        participant("substrate", "reactant", substrate_label, substrate_name, evidence),
        participant("boronic_acid", "reactant", reagent_label, reagent_name, evidence,
                    [field("equivalents", q(reagent_equiv, "equiv"), evidence)] if reagent_equiv else [],
                    SMILES.get(reagent_label)),
        participant("catalyst", "catalyst", "[Pd(PPh3)4]", "tetrakis(triphenylphosphine)palladium(0)", evidence,
                    [field("loading", q(10, "mol%"), evidence)]),
        participant("acid", "reagent", acid, {"AcOH": "acetic acid", "HCO2H": "formic acid", "EtCO2H": "propionic acid"}.get(acid, acid), evidence,
                    [field("loading", q(acid_loading, "mol%"), evidence)] if acid_loading is not None else [], SMILES.get(acid)),
        participant("solvent", "solvent", "THF", "tetrahydrofuran", evidence, smiles=SMILES["THF"]),
    ]
    for entity_id, label, name in products:
        ps.append(participant(entity_id, "product", label, name, evidence))
    return ps


records = []

# Page 1: conceptual and literature/generic synthesis arrows.
e = ev(1)
for suffix, addition in [("12", "1,2-addition"), ("23", "2,3-addition")]:
    records.append(record(
        f"scheme1_{suffix}_generic_addition", "general_scheme", e,
        [participant("allene", "reactant", "generic allene", None, e),
         participant("hz", "reactant", "HZ", None, e),
         participant("products", "product", f"six possible {addition} regio-/stereoisomers", None, e)],
        [{"step_id": "addition", "participant_ids": ["allene", "hz", "products"],
          "conditions": [field("operation", addition, e)]}],
        notes=["Conceptual regioselectivity scheme, not a reported individual experiment."],
    ))

records.append(record(
    "scheme2_dibal_reduction", "literature_example", e,
    [participant("allenoate", "reactant", "generic 2,3-allenoate", None, e),
     participant("dibal", "reagent", "DIBAL-H", "diisobutylaluminium hydride", e),
     participant("dienol", "product", "generic 2,3-dien-1-ol", None, e)],
    [{"step_id": "reduction", "participant_ids": ["allenoate", "dibal", "dienol"],
      "conditions": [field("temperature", q(-78, "°C"), e)]}],
    notes=["Scheme 2 cites literature preparation; no yield or scale is reported on this page."],
))
records.append(record(
    "scheme2_bromination", "literature_example", e,
    [participant("dienol", "reactant", "generic 2,3-dien-1-ol", None, e),
     participant("pbr3", "reagent", "PBr3", "phosphorus tribromide", e),
     participant("pyridine", "reagent", "pyridine", "pyridine", e, smiles="n1ccccc1"),
     participant("ether", "solvent", "Et2O", "diethyl ether", e, smiles=SMILES["Et2O"]),
     participant("bromide", "product", "generic 2,3-dienyl bromide", None, e)],
    [{"step_id": "bromination", "participant_ids": ["dienol", "pbr3", "pyridine", "ether", "bromide"], "conditions": []}],
    notes=["Scheme 2 cites literature preparation; no time, temperature, yield, or scale is reported on this page."],
))
records.append(record(
    "scheme2_malonate_alkylation", "literature_example", e,
    [participant("bromide", "reactant", "generic 2,3-dienyl bromide", None, e),
     participant("pronucleophile", "reactant", "CH(E1)(E2)", "generic malonate/cyano pronucleophile", e),
     participant("nah", "reagent", "NaH", "sodium hydride", e, smiles=SMILES["NaH"]),
     participant("thf", "solvent", "THF", "tetrahydrofuran", e, smiles=SMILES["THF"]),
     participant("products", "product", "1a-1e", "2-(2,3-dienyl)malonate derivatives", e)],
    [{"step_id": "alkylation", "participant_ids": ["bromide", "pronucleophile", "nah", "thf", "products"], "conditions": []}],
    notes=["Scheme 2 summarizes literature procedures for compounds 1a-1e; no row-specific yields are shown."],
))

# Page 2, Scheme 4: literature preparation of 2a-2f.
e = ev(2)
records.append(record(
    "scheme4_wittig_allenoate_synthesis", "literature_example", e,
    [participant("ylide", "reactant", "Ph3P=C(R5)COOEt", "phosphorus ylide", e),
     participant("acyl_chloride", "reactant", "R6CH2COCl", "acyl chloride", e),
     participant("et3n", "reagent", "Et3N", "triethylamine", e, smiles=SMILES["Et3N"]),
     participant("dcm", "solvent", "CH2Cl2", "dichloromethane", e, smiles="ClCCl"),
     participant("products", "product", "2a-2f", "ethyl 2,3-allenoates", e)],
    [{"step_id": "wittig_type_allenoate_formation", "participant_ids": ["ylide", "acyl_chloride", "et3n", "dcm", "products"], "conditions": []}],
    notes=["Scheme 4 explicitly attributes compounds 2a-2f to literature procedures; no yield or time is reported here."],
))

# Page 2, Scheme 5 catalyst screen.
for catalyst, time_h, yield_value, ratios in [
    ("Pd(OAc)2", 45, "trace", None),
    ("[Pd(PPh3)4]", 43, q(66, "%"), ("67:33", "85:15")),
]:
    rid = "scheme5_catalyst_pdoac2" if catalyst == "Pd(OAc)2" else "scheme5_catalyst_pdp4"
    ps = [
        participant("s1a", "reactant", "1a", "dimethyl 2-(2-benzyl-2,3-butadienyl)malonate", e),
        participant("r3a", "reactant", "3a", "4-methoxyphenylboronic acid", e, smiles=SMILES["3a"]),
        participant("cat", "catalyst", catalyst, catalyst, e, [field("loading", q(10, "mol%"), e)]),
        participant("thf", "solvent", "THF", "tetrahydrofuran", e, smiles=SMILES["THF"]),
        participant("p4aa", "product", "4aa", "regioisomer 4aa", e),
        participant("p5aa", "product", "5aa", "methyl 2-(2-benzyl-3-(4-methoxyphenyl)but-2-enyl)malonate", e),
    ]
    outs = [field("combined_yield", yield_value, e, ["p4aa", "p5aa"]), field("yield_measurement_basis", None, e)]
    if ratios:
        outs += [field("4aa_to_5aa_ratio", ratios[0], e, ["p4aa", "p5aa"]), field("t5aa_to_c5aa_ratio", ratios[1], e, ["p5aa"])]
    records.append(record(rid, "optimization_entry", e, ps,
                          [{"step_id": "reaction", "participant_ids": [p["entity_id"] for p in ps],
                            "conditions": [field("time", q(time_h, "h"), e), field("temperature", "reflux", e)]}],
                          outs, notes=["Catalyst-screen experiment shown in Scheme 5; no acid is shown."],
                          unresolved=["Yield measurement basis is not stated.", "No explicitly associated Supporting Information was supplied.", "Structures remain unverified."]))

# Page 2, Table 1 optimization rows.
table1 = [
    (1, "AcOH", 40, 5, "reflux", 75, "95:5", "87:13", None),
    (2, "AcOH", 40, 16, "r.t.", 74, ">97:3", "91:9", None),
    (3, "AcOH", 20, 22, "r.t.", 81, ">97:3", "91:9", None),
    (4, "AcOH", 10, 22, "r.t.", 82, ">96:4", "90:10", None),
    (5, "AcOH", 20, 5, "reflux", 79, ">96:4", "87:13", None),
    (6, "HCO2H", 20, 32, "reflux", 65, "83:17", "88:12", None),
    (7, "EtCO2H", 20, 4, "reflux", 71, ">96:4", "88:12", None),
    (8, "AcOH", 10, 8.5, "reflux", 70, "95:5", "87:13", None),
    (9, "AcOH", 10, 4, q(85, "°C"), 67, "95:5", "85:15", "sealed tube"),
]
for entry, acid, loading, hours, temp, yld, rr, sr, special in table1:
    ps = common_participants(e, "1a", "dimethyl 2-(2-benzyl-2,3-butadienyl)malonate", "3a", "4-methoxyphenylboronic acid",
                             [("p5aa", "5aa", "major internal-alkene regioisomer"), ("p4aa", "4aa", "minor terminal-alkene regioisomer")],
                             acid=acid, acid_loading=loading)
    ps[4]["amounts"] = [field("volume", q(3, "mL"), e)]
    cond = [field("time", q(hours, "h"), e), field("temperature", temp, e)]
    if special:
        cond.append(field("operation", special, e))
    records.append(record(
        f"table1_entry{entry:02d}", "optimization_entry", e, ps,
        [{"step_id": "hydroarylation", "participant_ids": [p["entity_id"] for p in ps], "conditions": cond}],
        [field("combined_yield", q(yld, "%"), e, ["p5aa", "p4aa"]),
         field("5aa_to_4aa_ratio", rr, e, ["p5aa", "p4aa"]),
         field("t5aa_to_c5aa_ratio", sr, e, ["p5aa"]),
         field("yield_measurement_basis", None, e)],
        notes=["Table 1 footnote reports organoboronic acid at 2.0 equivalents and 10 mol% Pd(PPh3)4; the printed footnote calls it 2a although the scheme identifies reagent 3a."],
        unresolved=["The 2a/3a footnote-label inconsistency is preserved.", "Yield measurement basis is not explicitly stated.", "No explicitly associated Supporting Information was supplied.", "Structures remain unverified."],
    ))

# Page 3, Table 2 scope. Later experimental prose is merged as evidence and extra combined-yield outcomes.
table2 = [
    (1, "1a", "3a", 22, 79, ">97:3", "91:9", "5aa", "4aa", 5, 81, q(77, "mg")),
    (2, "1a", "3b", 40, 73, "97:3", "90:10", "5ab", "4ab", 5, 75, q(131, "mg")),
    (3, "1b", "3a", 14, 62, ">99:1", ">99:1", "5ba", "4ba", 5, 63, q(46, "mg")),
    (4, "1b", "3a", 7, 66, ">98:2", ">98:2", "5ba", "4ba", None, None, None),
    (5, "1b", "3b", 16, 49, ">97:3", ">98:2", "5bb", "4bb", 5, 51, q(32, "mg")),
    (6, "1c", "3a", 72, 30, "100:0", "92:8", "5ca", None, 5, 30, q(23, "mg")),
    (7, "1d", "3a", 22, 73, "100:0", "100:0", "5da", None, 6, 73, q(46, "mg")),
    (8, "1f", "3a", 72, 84, "100:0", "90:10", "5fa", None, 6, 84, q(83, "mg")),
    (9, "1g", "3a", 40, 91, ">99:1", "95:5", "5ga", "4ga", 6, 92, q(87, "mg")),
]
substrate_names = {
    "1a": "dimethyl 2-(2-benzyl-2,3-butadienyl)malonate",
    "1b": "dimethyl 2-(2,3-butadienyl)malonate",
    "1c": "2-(2-benzyl-2,3-butadienyl)malononitrile",
    "1d": "ethyl 2-cyanohexa-4,5-dienoate",
    "1f": "2-methyl-2-(2-benzyl-2,3-butadienyl)malonate",
    "1g": "dimethyl 2-methyl-2-(2-benzyl-2,3-butadienyl)malonate",
}
boronic_names = {"3a": "4-methoxyphenylboronic acid", "3b": "phenylboronic acid"}
product5_names = {
    "5aa": "methyl 2-(2-benzyl-3-(4-methoxyphenyl)but-2-enyl)malonate",
    "5ab": "methyl 2-(2-benzyl-3-phenylbut-2-enyl)malonate",
    "5ba": "methyl 2-(3-(4-methoxyphenyl)but-2-enyl)malonate",
    "5bb": "methyl 2-(3-phenylbut-2-enyl)malonate",
    "5ca": "2-(2-benzyl-3-(4-methoxyphenyl)but-2-enyl)malononitrile",
    "5da": "ethyl 2-cyano-5-(4-methoxyphenyl)hex-4-enoate",
    "5fa": "methyl 2-(1-methyl-2-benzyl-3-(4-methoxyphenyl)but-2-enyl)malonate",
    "5ga": "methyl 2-methyl-2-(2-benzyl-3-(4-methoxyphenyl)but-2-enyl)malonate",
}
for entry, sub, bor, hours, yld5, rr, sr, major, minor, detail_page, combined, mass in table2:
    evidence = ev(3, detail_page) if detail_page else ev(3)
    products = [("major", major, product5_names.get(major, f"product {major}"))]
    if minor:
        products.append(("minor", minor, f"regioisomer {minor}"))
    ps = common_participants(evidence, sub, substrate_names[sub], bor, boronic_names[bor], products, acid="AcOH", acid_loading=20)
    cond = [field("time", q(hours, "h"), evidence), field("temperature", "reflux" if entry == 4 else "r.t.", evidence)]
    if detail_page == 5 and entry in (1, 2, 3, 5, 6):
        # Detailed prose gives masses/scales; only common, unambiguous values are structured here.
        scale = {1: (q(68, "mg"), q(0.25, "mmol"), q(76, "mg"), q(0.50, "mmol")),
                 2: (q(136, "mg"), q(0.50, "mmol"), q(122, "mg"), q(1.00, "mmol")),
                 3: (q(46, "mg"), q(0.25, "mmol"), q(76, "mg"), q(0.50, "mmol")),
                 5: (q(46, "mg"), q(0.25, "mmol"), q(61, "mg"), q(0.50, "mmol")),
                 6: (q(50, "mg"), q(0.24, "mmol"), q(73, "mg"), q(0.48, "mmol"))}[entry]
        ps[0]["amounts"] = [field("mass", scale[0], evidence), field("amount", scale[1], evidence)]
        ps[1]["amounts"] = [field("mass", scale[2], evidence), field("amount", scale[3], evidence), field("equivalents", q(2.0, "equiv"), evidence)]
    if detail_page == 6:
        scale = {7: (q(38, "mg"), q(0.23, "mmol"), q(70, "mg"), q(0.46, "mmol")),
                 8: (q(72, "mg"), q(0.25, "mmol"), q(76, "mg"), q(0.50, "mmol")),
                 9: (q(72, "mg"), q(0.25, "mmol"), q(76, "mg"), q(0.50, "mmol"))}[entry]
        ps[0]["amounts"] = [field("mass", scale[0], evidence), field("amount", scale[1], evidence)]
        ps[1]["amounts"] = [field("mass", scale[2], evidence), field("amount", scale[3], evidence), field("equivalents", q(2.0, "equiv"), evidence)]
    outs = [field("yield_of_product_5", q(yld5, "%"), ev(3), ["major"]),
            field("5_to_4_ratio", rr, evidence, [x[0] for x in products]),
            field("t5_to_c5_ratio", sr, evidence, ["major"]),
            field("yield_measurement_basis", None, evidence)]
    if combined is not None:
        targets = [x[0] for x in products]
        outs += [field("combined_isolated_yield", q(combined, "%"), ev(detail_page), targets),
                 field("isolated_product_mass", mass, ev(detail_page), targets)]
    notes = ["Table 2 reports yield of product 5; where detailed experimental prose is present, its combined isolated yield is retained separately."]
    if entry == 8:
        notes.append("The page-6 prose prints t-5ca/c-5ca for the 5fa experiment; this apparent label typo was not silently substituted into the structured selectivity field, which follows Table 2's 5fa row.")
    records.append(record(
        f"table2_entry{entry:02d}", "substrate_scope_entry", evidence, ps,
        [{"step_id": "hydroarylation", "participant_ids": [p["entity_id"] for p in ps], "conditions": cond}], outs, notes=notes,
        unresolved=["Yield measurement basis for the table value is not explicitly stated.", "No explicitly associated Supporting Information was supplied.", "Structures remain unverified."],
    ))

# Page 3, Tables 3 and 4. Table 4 entry 1 is the same experiment as Table 3 entry 2.
table3 = [
    (1, "2a", "3a", 17, 66, "96:4", "96:4", "7aa", "6aa", 20, 6),
    (2, "2a", "3a", 12, 66, ">98:2", ">98:2", "7aa", "6aa", 100, 6),
    (3, "2b", "3a", 30, 62, ">99:1", ">98:2", "7ba", "6ba", 100, 6),
    (4, "2b", "3b", 14, 70, ">99:1", ">99:1", "7bb", "6bb", 100, 6),
    (5, "2b", "3c", 10, 75, ">99:1", ">99:1", "7bc", "6bc", 100, 6),
    (6, "2c", "3a", 22, 73, ">99:1", ">99:1", "7ca", "6ca", 100, 6),
    (7, "2d", "3a", 10, 86, ">98:2", "97:3", "7da", "6da", 100, 6),
    (8, "2d", "3b", 34, 31, ">98:2", ">99:1", "7db", "6db", 100, 6),
    (9, "2e", "3a", 32, 18, ">98:2", ">98:2", "7ea", "6ea", 100, None),
    (10, "2f", "3a", 36, 46, ">98:2", ">98:2", "7fa", "6fa", 100, None),
]
substrate2_names = {
    "2a": "ethyl 2-benzylbuta-2,3-dienoate", "2b": "ethyl buta-2,3-dienoate",
    "2c": "ethyl 2-methylbuta-2,3-dienoate", "2d": "ethyl 2-propylbuta-2,3-dienoate",
    "2e": "ethyl 2-benzylpenta-2,3-dienoate", "2f": "ethyl deca-2,3-dienoate",
}
boronic_names.update({"3c": "4-methylphenylboronic acid", "3d": "3-nitrophenylboronic acid", "3e": "biphenyl-4-boronic acid"})
product7_names = {
    "7aa": "ethyl 2-benzyl-3-(4-methoxyphenyl)but-2-enoate",
    "7ba": "ethyl 3-(4-methoxyphenyl)but-2-enoate", "7bb": "ethyl 3-phenylbut-2-enoate",
    "7bc": "ethyl 3-(4-methylphenyl)but-2-enoate", "7ca": "ethyl 2-methyl-3-(4-methoxyphenyl)but-2-enoate",
    "7da": "ethyl 2-propyl-3-(4-methoxyphenyl)but-2-enoate", "7db": "ethyl 2-propyl-3-phenylbut-2-enoate",
    "7ea": "ethyl 2-benzyl-3-(4-methoxyphenyl)pent-2-enoate", "7fa": "ethyl 3-(4-methoxyphenyl)dec-2-enoate",
}
for entry, sub, bor, hours, yld, rr, sr, major, minor, acid_loading, detail_page in table3:
    evidence = ev(2, 3, detail_page) if entry in (1, 2) else (ev(3, detail_page) if detail_page else ev(3))
    ps = common_participants(evidence, sub, substrate2_names[sub], bor, boronic_names[bor],
                             [("major", major, product7_names.get(major, f"product {major}")), ("minor", minor, f"regioisomer {minor}")],
                             acid="AcOH", acid_loading=acid_loading)
    outs = [field("yield_of_product_7", q(yld, "%"), ev(3), ["major"]),
            field("7_to_6_ratio", rr, evidence, ["major", "minor"]),
            field("E_to_Z_ratio_of_7", sr, evidence, ["major"]), field("yield_measurement_basis", None, evidence)]
    if entry == 1:
        outs.append(field("combined_yield_reported_in_prose", q(69, "%"), ev(2), ["major", "minor"]))
    if entry == 2:
        # Same experiment is shown in Table 4 entry 1 and the typical Conditions B procedure.
        evidence = ev(2, 3, 5, 6)
        for obj in ps:
            for key in ("label", "name", "smiles"):
                obj[key]["evidence_ids"] = evidence
        ps[0]["amounts"] = [field("mass", q(51, "mg"), ev(5)), field("amount", q(0.25, "mmol"), ev(5))]
        ps[1]["amounts"] = [field("mass", q(76, "mg"), ev(5)), field("amount", q(0.50, "mmol"), ev(5)), field("equivalents", q(2.0, "equiv"), evidence)]
        ps[2]["amounts"] = [field("mass", q(29, "mg"), ev(5)), field("amount", q(0.025, "mmol"), ev(5)), field("loading", q(10, "mol%"), evidence)]
        ps[3]["amounts"] = [field("volume", q(15, "uL"), ev(5)), field("loading", q(100, "mol%"), evidence)]
        ps[4]["amounts"] = [field("volume", q(3, "mL"), ev(5))]
        outs.append(field("combined_isolated_yield", q(66, "%"), ev(3, 5, 6), ["major", "minor"]))
        outs.append(field("isolated_product_mass", q(51, "mg"), ev(5), ["major", "minor"]))
    if detail_page == 6 and entry in range(3, 9):
        scales = {
            3: (q(56, "mg"), q(0.50, "mmol"), q(152, "mg"), q(1.0, "mmol"), q(68, "mg"), 62),
            4: (q(28, "mg"), q(0.25, "mmol"), q(61, "mg"), q(0.50, "mmol"), q(33, "mg"), 70),
            5: (q(28, "mg"), q(0.25, "mmol"), q(68, "mg"), q(0.50, "mmol"), q(38, "mg"), 75),
            6: (q(63, "mg"), q(0.50, "mmol"), q(152, "mg"), q(1.0, "mmol"), q(85, "mg"), 73),
            7: (q(39, "mg"), q(0.25, "mmol"), q(76, "mg"), q(0.50, "mmol"), q(56, "mg"), 86),
            8: (q(39, "mg"), q(0.25, "mmol"), q(61, "mg"), q(0.50, "mmol"), q(18, "mg"), 32),
        }
        a, b, c, d, product_mass, combined_yield = scales[entry]
        ps[0]["amounts"] = [field("mass", a, ev(6)), field("amount", b, ev(6))]
        ps[1]["amounts"] = [field("mass", c, ev(6)), field("amount", d, ev(6)), field("equivalents", q(2.0, "equiv"), evidence)]
        outs += [field("combined_isolated_yield", q(combined_yield, "%"), ev(6), ["major", "minor"]),
                 field("isolated_product_mass", product_mass, ev(6), ["major", "minor"])]
    records.append(record(
        f"table3_entry{entry:02d}", "substrate_scope_entry", evidence, ps,
        [{"step_id": "hydroarylation", "participant_ids": [p["entity_id"] for p in ps],
          "conditions": [field("time", q(hours, "h"), evidence), field("temperature", "r.t.", evidence),
                         field("atmosphere", "nitrogen", ev(5))] if entry == 2 else [field("time", q(hours, "h"), evidence), field("temperature", "r.t.", evidence)]}],
        outs, notes=["Table 3 reports yield of product 7; detailed prose and Table 4 combined yields are retained separately when available."],
        unresolved=["Yield measurement basis for the Table 3 value is not explicitly stated.", "No explicitly associated Supporting Information was supplied.", "Structures remain unverified."],
    ))

table4 = [
    (2, "3b", 24, 60, "96:4", "96:4", "7ab", "6ab"),
    (3, "3c", 9, 61, "97:3", "98:2", "7ac", "6ac"),
    (4, "3d", 21, 63, "96:4", "92:8", "7ad", "6ad"),
    (5, "3e", 36, 63, "95:5", "94:6", "7ae", "6ae"),
]
for entry, bor, hours, yld, rr, sr, major, minor in table4:
    evidence = ev(3)
    ps = common_participants(evidence, "2a", substrate2_names["2a"], bor, boronic_names[bor],
                             [("major", major, f"ethyl 2-benzyl aryl but-2-enoate {major}"), ("minor", minor, f"regioisomer {minor}")],
                             acid="AcOH", acid_loading=100)
    records.append(record(
        f"table4_entry{entry:02d}", "substrate_scope_entry", evidence, ps,
        [{"step_id": "hydroarylation", "participant_ids": [p["entity_id"] for p in ps],
          "conditions": [field("time", q(hours, "h"), evidence), field("temperature", "r.t.", evidence)]}],
        [field("combined_yield", q(yld, "%"), evidence, ["major", "minor"]),
         field("7_to_6_ratio", rr, evidence, ["major", "minor"]),
         field("E_to_Z_ratio_of_7", sr, evidence, ["major"]), field("yield_measurement_basis", None, evidence)],
        notes=["Table 4 entry; Table 4 entry 1 is not duplicated because it is merged into Table 3 entry 2."],
        unresolved=["Yield measurement basis is not explicitly stated.", "No explicitly associated Supporting Information was supplied.", "Structures remain unverified."],
    ))

# Page 3 equations 1 and 2.
e = ev(3)
records.append(record(
    "eq1_hydroalkenylation_7af", "substrate_scope_entry", e,
    common_participants(e, "2a", substrate2_names["2a"], "3f", "1-alkenylboronic acid 3f",
                        [("major", "7af", "ethyl 2-benzyl-3-methylundeca-2,4-dienoate"), ("minor", "6af", "regioisomer 6af")],
                        acid="AcOH", acid_loading=100),
    [{"step_id": "hydroalkenylation", "participant_ids": ["substrate", "boronic_acid", "catalyst", "acid", "solvent", "major", "minor"],
      "conditions": [field("time", q(10, "h"), e), field("temperature", "r.t.", e)]}],
    [field("combined_yield", q(52, "%"), e, ["major", "minor"]), field("7af_to_6af_ratio", ">99:1", e, ["major", "minor"]),
     field("2E4E_to_2Z4E_ratio", ">99:1", e, ["major"]), field("yield_measurement_basis", None, e)],
))
records.append(record(
    "eq2_hydroarylation_product9", "substrate_scope_entry", e,
    common_participants(e, "8", "ethyl 3,4-pentadienoate", "3a", "4-methoxyphenylboronic acid",
                        [("major", "9", "ethyl 4-(4-methoxyphenyl)pent-3-enoate"), ("minor", "10", "regioisomer 10")],
                        acid="AcOH", acid_loading=20),
    [{"step_id": "hydroarylation", "participant_ids": ["substrate", "boronic_acid", "catalyst", "acid", "solvent", "major", "minor"],
      "conditions": [field("time", q(13, "h"), e), field("temperature", "r.t.", e)]}],
    [field("combined_yield", q(43, "%"), e, ["major", "minor"]), field("9_to_10_ratio", "95:5", e, ["major", "minor"]),
     field("E9_to_Z9_ratio", "95:5", e, ["major"]), field("yield_measurement_basis", None, e)],
))

# Page 4 equations and control/mechanism.
e = ev(4)
records.append(record(
    "eq3_hydroarylation_1_2_decadiene", "substrate_scope_entry", e,
    common_participants(e, "11", "1,2-decadiene", "3a", "4-methoxyphenylboronic acid",
                        [("p12", "12", "2-(4-methoxyphenyl)dec-1-ene"), ("p13", "13", "2-(4-methoxyphenyl)dec-2-ene")],
                        acid="AcOH", acid_loading=20),
    [{"step_id": "hydroarylation", "participant_ids": ["substrate", "boronic_acid", "catalyst", "acid", "solvent", "p12", "p13"],
      "conditions": [field("time", q(36, "h"), e), field("temperature", "r.t.", e)]}],
    [field("combined_yield", q(71, "%"), e, ["p12", "p13"]), field("12_to_13_ratio", "11:89", e, ["p12", "p13"]),
     field("E13_to_Z13_ratio", ">96:4", e, ["p13"]), field("yield_measurement_basis", None, e)],
))
records.append(record(
    "eq4_hydroarylation_1e", "substrate_scope_entry", e,
    common_participants(e, "1e", "terminal n-hexyl-substituted 2,3-dienylmalonate 1e", "3a", "4-methoxyphenylboronic acid",
                        [("p5ea", "5ea", "methyl 2-(3-(4-methoxyphenyl)dec-2-enyl)malonate"),
                         ("p4ea", "4ea", "methyl 2-(3-(4-methoxyphenyl)dec-3-enyl)malonate")],
                        acid="AcOH", acid_loading=20),
    [{"step_id": "hydroarylation", "participant_ids": ["substrate", "boronic_acid", "catalyst", "acid", "solvent", "p5ea", "p4ea"],
      "conditions": [field("time", q(48, "h"), e), field("temperature", "r.t.", e)]}],
    [field("combined_yield", q(90, "%"), e, ["p5ea", "p4ea"]), field("5ea_to_4ea_ratio", "64:36", e, ["p5ea", "p4ea"]),
     field("stereochemical_assignment", "only E isomers reported", e, ["p5ea", "p4ea"]), field("yield_measurement_basis", None, e)],
))
records.append(record(
    "scheme6_no_interconversion_4aa", "reported_experiment", e,
    [participant("r4aa", "reactant", "4aa", "terminal-alkene regioisomer 4aa", e),
     participant("p5aa", "product", "5aa", "internal-alkene regioisomer 5aa", e)],
    [{"step_id": "control_under_conditions_A", "participant_ids": ["r4aa", "p5aa"],
      "conditions": [field("time", q(24, "h"), e), field("operation", "Conditions A", e)]}],
    [field("5aa_formation", "not detected", e, ["p5aa"]), field("4aa_recovery", q(93, "%"), e, ["r4aa"]),
     field("recovery_measurement_basis", None, e)],
    notes=["Control experiment showed no observed interconversion from 4aa to 5aa."],
))
records.append(record(
    "scheme7_proposed_mechanism", "mechanism", e,
    [participant("hx", "reactant", "HX", None, e), participant("pd0", "catalyst", "Pd0", "palladium(0)", e),
     participant("allene", "reactant", "generic allene", None, e), participant("boronic", "reactant", "ArB(OH)2", "arylboronic acid", e),
     participant("p14", "unspecified_agent", "14", "palladium hydride intermediate", e),
     participant("p15", "unspecified_agent", "15", "alkenylpalladium intermediate", e),
     participant("p16", "unspecified_agent", "16", "transmetalation intermediate", e),
     participant("p5", "product", "5", "tri- or tetrasubstituted alkene", e)],
    [{"step_id": "oxidative_addition", "participant_ids": ["hx", "pd0", "p14"], "conditions": []},
     {"step_id": "hydropalladation", "participant_ids": ["p14", "allene", "p15"], "conditions": []},
     {"step_id": "suzuki_coupling", "participant_ids": ["p15", "boronic", "p16", "p5"], "conditions": []}],
    notes=["Authors' proposed mechanistic rationale, not an isolated experiment."],
))

# Page 4 preparations of 1c and 1d.
for rid, product_label, product_name, reactants, product_mass, product_amount, yld in [
    ("prep_1c", "1c", substrate_names["1c"],
     [("bromide", "reactant", "3-bromomethyl-4-phenyl-1,2-butadiene acetate", q(2.65, "g"), q(12, "mmol"), None),
      ("malononitrile", "reactant", "malononitrile", q(1.1, "g"), q(16.8, "mmol"), "N#CCC#N"),
      ("nah", "reagent", "NaH (60% dispersion in mineral oil)", q(0.528, "g"), q(13.2, "mmol"), SMILES["NaH"])], q(1.50, "g"), None, 60),
    ("prep_1d", "1d", substrate_names["1d"],
     [("bromide", "reactant", "4-bromo-1,2-butadiene", q(1.06, "g"), q(8, "mmol"), None),
      ("cyanoacetate", "reactant", "ethyl cyanoacetate", q(1.27, "g"), q(11.2, "mmol"), "CCOC(=O)CC#N"),
      ("nah", "reagent", "NaH (60% dispersion in mineral oil)", q(0.352, "g"), q(8.8, "mmol"), SMILES["NaH"])], q(0.35, "g"), None, 26),
]:
    ps = []
    for entity_id, role, name, mass, amount, smiles in reactants:
        ps.append(participant(entity_id, role, name, name, e, [field("mass", mass, e), field("amount", amount, e)], smiles))
    ps.append(participant("product", "product", product_label, product_name, e))
    records.append(record(
        rid, "reported_experiment", e, ps,
        [{"step_id": "reported_literature_procedure", "participant_ids": [p["entity_id"] for p in ps], "conditions": []}],
        [field("isolated_product_mass", product_mass, e, ["product"]), field("isolated_yield", q(yld, "%"), e, ["product"])],
        notes=["Prepared by the cited reported procedure; the present article gives amounts and outcome but omits time, temperature, solvent, workup, and purification here."],
        unresolved=["Time, temperature, solvent, workup, and purification are not reported in this article paragraph.", "No explicitly associated Supporting Information was supplied.", "Product structure remains unverified."],
    ))

# Page 5: detailed precursor, 1f, and 1g preparations.
e = ev(2, 5)
ps = [
    participant("alcohol", "reactant", "3-benzylpenta-3,4-dien-2-ol", "3-benzylpenta-3,4-dien-2-ol", e,
                [field("mass", q(3.48, "g"), e), field("amount", q(18.4, "mmol"), e)]),
    participant("et3n", "reagent", "Et3N", "triethylamine", e, [field("volume", q(3.8, "mL"), e)], SMILES["Et3N"]),
    participant("ac2o", "reagent", "Ac2O", "acetic anhydride", e, [field("mass", q(2.86, "g"), e), field("amount", q(28, "mmol"), e)], SMILES["Ac2O"]),
    participant("dmap", "catalyst", "DMAP", "4-dimethylaminopyridine", e, [field("mass", q(242.5, "mg"), e), field("amount", q(2.0, "mmol"), e)], SMILES["DMAP"]),
    participant("ether", "solvent", "Et2O", "diethyl ether", e, [field("volume", q(70, "mL"), e)], SMILES["Et2O"]),
    participant("product", "product", "3-benzylpenta-3,4-dien-2-yl acetate", "3-benzylpenta-3,4-dien-2-yl acetate", e),
]
records.append(record(
    "prep_3_benzylpenta_3_4_dien_2_yl_acetate", "reported_experiment", e, ps,
    [{"step_id": "acetylation", "participant_ids": [p["entity_id"] for p in ps],
      "conditions": [field("time", q(1, "h"), e), field("temperature", "r.t.", e), field("operation", "monitored by TLC", e),
                     field("workup", "evaporation to dryness", e),
                     field("purification", "flash chromatography on silica gel; petroleum ether/diethyl ether 20:1", e)]}],
    [field("isolated_product_mass", q(3.62, "g"), e, ["product"]), field("isolated_yield", q(91, "%"), e, ["product"])],
))

ps = [
    participant("malonate", "reactant", "dimethyl malonate", "dimethyl malonate", e, [field("volume", q(4.68, "mL"), e), field("amount", q(39.0, "mmol"), e)], "COC(=O)CC(=O)OC"),
    participant("acetate", "reactant", "3-benzylpenta-3,4-dien-2-yl acetate", "3-benzylpenta-3,4-dien-2-yl acetate", e, [field("mass", q(2.63, "g"), e), field("amount", q(13, "mmol"), e)]),
    participant("cat", "catalyst", "[Pd(PPh3)4]", "tetrakis(triphenylphosphine)palladium(0)", e, [field("mass", q(0.754, "g"), e), field("amount", q(0.65, "mmol"), e), field("loading", q(5, "mol%"), e)]),
    participant("nah", "reagent", "NaH (60% dispersion in mineral oil)", "sodium hydride", e, [field("mass", q(0.572, "g"), e), field("amount", q(14.3, "mmol"), e)], SMILES["NaH"]),
    participant("dce", "solvent", "dry 1,2-dichloroethane", "1,2-dichloroethane", e, [field("volume", q(104, "mL"), e)], SMILES["DCE"]),
    participant("nacl", "reagent", "saturated aqueous NaCl", "sodium chloride solution", e, [field("volume", q(10, "mL"), e)], SMILES["NaCl"]),
    participant("ether", "solvent", "Et2O", "diethyl ether", e, [field("volume", q(200, "mL"), e)], SMILES["Et2O"]),
    participant("product", "product", "1f", substrate_names["1f"], e),
]
records.append(record(
    "prep_1f", "reported_experiment", e, ps,
    [{"step_id": "pd_0_catalyzed_allenylation", "participant_ids": [p["entity_id"] for p in ps],
      "conditions": [field("time", q(18, "h"), e), field("temperature", "r.t.", e), field("atmosphere", "nitrogen", e),
                     field("operation", "monitored by TLC", e),
                     field("workup", "quenched with saturated aqueous NaCl, extracted with diethyl ether, and dried over anhydrous sodium sulfate", e),
                     field("purification", "flash chromatography on silica gel; petroleum ether/ethyl acetate 20:1", e)]}],
    [field("isolated_product_mass", q(3.07, "g"), e, ["product"]), field("isolated_yield", q(82, "%"), e, ["product"])],
))

ps = [
    participant("s1a", "reactant", "1a", substrate_names["1a"], e, [field("mass", q(272, "mg"), e), field("amount", q(1.0, "mmol"), e)]),
    participant("nah", "reagent", "NaH (60% dispersion in mineral oil)", "sodium hydride", e, [field("mass", q(48, "mg"), e), field("amount", q(1.2, "mmol"), e)], SMILES["NaH"]),
    participant("mei", "reagent", "MeI", "iodomethane", e, [field("mass", q(213, "mg"), e), field("amount", q(1.5, "mmol"), e)], SMILES["MeI"]),
    participant("thf", "solvent", "THF", "tetrahydrofuran", e, [field("volume", q(3, "mL"), e)], SMILES["THF"]),
    participant("nacl", "reagent", "saturated aqueous NaCl", "sodium chloride solution", e, [field("volume", q(2, "mL"), e)], SMILES["NaCl"]),
    participant("ether", "solvent", "Et2O", "diethyl ether", e, [field("volume", q(20, "mL"), e)], SMILES["Et2O"]),
    participant("product", "product", "1g", substrate_names["1g"], e),
]
records.append(record(
    "prep_1g", "reported_experiment", e, ps,
    [{"step_id": "methylation", "participant_ids": [p["entity_id"] for p in ps],
      "conditions": [field("time", q(5, "h"), e), field("temperature", "r.t.", e), field("atmosphere", "nitrogen", e),
                     field("operation", "monitored by TLC", e),
                     field("workup", "quenched with saturated aqueous NaCl, extracted with diethyl ether, and dried over anhydrous sodium sulfate", e),
                     field("purification", "flash chromatography on silica gel; petroleum ether/ethyl acetate 10:1", e)]}],
    [field("isolated_product_mass", q(171, "mg"), e, ["product"]), field("isolated_yield", q(61, "%"), e, ["product"])],
))

# Enrich the Table 2 entry 1 record with the detailed Conditions A procedure on page 5.
for rec in records:
    if rec["source_reaction_id"] == "table2_entry01":
        rec["evidence_ids"] = ev(3, 5)
        rec["participants"][0]["amounts"] = [field("mass", q(68, "mg"), ev(5)), field("amount", q(0.25, "mmol"), ev(5))]
        rec["participants"][1]["amounts"] = [field("mass", q(76, "mg"), ev(5)), field("amount", q(0.50, "mmol"), ev(5)), field("equivalents", q(2.0, "equiv"), ev(3, 5))]
        rec["participants"][2]["amounts"] = [field("mass", q(29, "mg"), ev(5)), field("amount", q(0.025, "mmol"), ev(5)), field("loading", q(10, "mol%"), ev(3, 5))]
        rec["participants"][3]["amounts"] = [field("volume", q(2.9, "uL"), ev(5)), field("loading", q(20, "mol%"), ev(3, 5))]
        rec["participants"][4]["amounts"] = [field("volume", q(3, "mL"), ev(5))]
        rec["steps"][0]["conditions"] += [field("atmosphere", "nitrogen", ev(5)), field("operation", "monitored by TLC", ev(5)),
                                                field("workup", "evaporation to dryness", ev(5)),
                                                field("purification", "flash chromatography on silica gel; petroleum ether/ethyl acetate 20:1", ev(5))]

# Coverage ledger: every region cites its own rendered page evidence.
page_records = {p: [] for p in range(1, 7)}
for rec in records:
    for p in range(1, 7):
        if f"{DOC}:page{p}:image" in rec["evidence_ids"]:
            page_records[p].append(rec["record_id"])

coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {"page": 1, "state": "attempted", "regions": [
            {"region": "title, abstract, introduction, and Results and Discussion prose", "finding": "Article context and claims; no independent quantified experiment in this text region.", "evidence_ids": [f"{DOC}:page1:image", f"{DOC}:page1:text"]},
            {"region": "Scheme 1, lower left", "finding": "Two generic 1,2- and 2,3-addition arrows classified as conceptual general schemes, not reported experiments.", "evidence_ids": [f"{DOC}:page1:image"]},
            {"region": "Scheme 2, lower right", "finding": "Three-arrow literature/generic sequence (DIBAL reduction, PBr3 bromination, NaH alkylation) leading to 1a-1e; row-specific experimental details are absent.", "evidence_ids": [f"{DOC}:page1:image", f"{DOC}:page1:text"]},
        ], "record_ids": page_records[1], "unresolved": ["Scheme 2 gives generic R/E labels and no yields, scales, or times; structures remain unverified."]},
        {"page": 2, "state": "attempted", "regions": [
            {"region": "Schemes 3 and 4, upper and middle left", "finding": "Scheme 3 contains preparations of the acetate precursor, 1f, and 1g; the matching detailed page-5 procedures were merged. Scheme 4 is a literature-attributed generic allenoate synthesis.", "evidence_ids": [f"{DOC}:page2:image", f"{DOC}:page2:text"]},
            {"region": "Scheme 5 and catalyst table, upper right", "finding": "Two independent catalyst-screen experiments: Pd(OAc)2 gives trace product; Pd(PPh3)4 gives 66% combined yield.", "evidence_ids": [f"{DOC}:page2:image", f"{DOC}:page2:text"]},
            {"region": "Table 1, middle right", "finding": "Nine independent acid/temperature optimization rows extracted, including reflux and sealed-tube footnote overrides.", "evidence_ids": [f"{DOC}:page2:image", f"{DOC}:page2:text"]},
            {"region": "discussion text, lower half", "finding": "Conditions A/B and prose outcomes were linked to matching Table 2/Table 3 experiments; the 20 mol% AcOH prose combined yield for 2a+3a was retained separately from Table 3's product-7 yield.", "evidence_ids": [f"{DOC}:page2:image", f"{DOC}:page2:text"]},
        ], "record_ids": page_records[2], "unresolved": ["Table 1 footnote prints reagent 2a although the reaction scheme identifies organoboronic acid 3a.", "Yield measurement bases are not always explicit."]},
        {"page": 3, "state": "attempted", "regions": [
            {"region": "Table 2, upper half", "finding": "Nine substrate-scope rows extracted independently; detailed page-5/6 experiments were merged where they describe the same reaction.", "evidence_ids": [f"{DOC}:page3:image", f"{DOC}:page3:text"]},
            {"region": "Tables 3 and 4, center", "finding": "Ten Table 3 rows and five Table 4 rows inventoried; Table 4 entry 1 duplicates Table 3 entry 2 and was merged, leaving four additional Table 4 records.", "evidence_ids": [f"{DOC}:page3:image", f"{DOC}:page3:text"]},
            {"region": "Figure 1, lower left", "finding": "ORTEP/X-ray assignment for (E)-7ac; structural evidence only, not a separate synthetic experiment.", "evidence_ids": [f"{DOC}:page3:image", f"{DOC}:page3:text"]},
            {"region": "Equations 1 and 2, lower right", "finding": "Two independent scope experiments: hydroalkenylation to 7af/6af and hydroarylation of 8 to 9/10.", "evidence_ids": [f"{DOC}:page3:image", f"{DOC}:page3:text"]},
        ], "record_ids": page_records[3], "unresolved": ["Generic R-group structures and all depicted stereochemical structures remain unverified.", "The table headings do not fully specify yield measurement basis."]},
        {"page": 4, "state": "attempted", "regions": [
            {"region": "Equations 3 and 4, upper and middle left", "finding": "Two independent scope experiments for 1,2-decadiene and n-hexyl-substituted allene 1e, with yields and regio-/stereoselectivity.", "evidence_ids": [f"{DOC}:page4:image", f"{DOC}:page4:text"]},
            {"region": "Scheme 6, lower left", "finding": "Control experiment under Conditions A: no 5aa formed and 93% of 4aa recovered after 24 h.", "evidence_ids": [f"{DOC}:page4:image", f"{DOC}:page4:text"]},
            {"region": "Scheme 7 and mechanism discussion, upper right", "finding": "Proposed hydropalladation/Suzuki mechanism classified as mechanism, not as a reported experiment.", "evidence_ids": [f"{DOC}:page4:image", f"{DOC}:page4:text"]},
            {"region": "Experimental Section, lower right", "finding": "Preparations of 1c and 1d extracted with stated reagent amounts, product masses, and yields; omitted procedural details remain missing.", "evidence_ids": [f"{DOC}:page4:image", f"{DOC}:page4:text"]},
        ], "record_ids": page_records[4], "unresolved": ["The 1c/1d paragraphs defer to cited procedures and omit time, temperature, solvent, workup, and purification."]},
        {"page": 5, "state": "attempted", "regions": [
            {"region": "left column, acetate precursor and preparations of 1f/1g", "finding": "Three detailed reported experiments extracted, including participants, quantities, atmosphere, time, workup, purification, and isolated yields.", "evidence_ids": [f"{DOC}:page5:image", f"{DOC}:page5:text"]},
            {"region": "left column, typical Conditions A and B", "finding": "Typical A was merged into Table 2 entry 1; typical B was merged into Table 3 entry 2/Table 4 entry 1. The page image supports AcOH volumes of 2.9 uL and 15 uL.", "evidence_ids": [f"{DOC}:page5:image", f"{DOC}:page5:text"]},
            {"region": "right column and lower left, product descriptions 5aa/4aa, 5ab/4ab, 5ba/4ba, 5bb/4bb, 5ca", "finding": "These are characterization continuations of already-recorded scope experiments; yields/masses were linked to those records rather than duplicated.", "evidence_ids": [f"{DOC}:page5:image", f"{DOC}:page5:text"]},
        ], "record_ids": page_records[5], "unresolved": ["Spectroscopic characterization was not decomposed into reaction-condition fields.", "The paper has no explicitly associated SI in this workspace."]},
        {"page": 6, "state": "attempted", "regions": [
            {"region": "left column, continuation of 5ca and products 5da, 5fa, 5ga", "finding": "Scope narratives merged into Table 2 entries 6-9; explicit scales, isolated masses, combined yields, and selectivities were retained where stated.", "evidence_ids": [f"{DOC}:page6:image", f"{DOC}:page6:text"]},
            {"region": "right column, products 7ba, 7bb, 7bc, 7ca, 7da, 7db", "finding": "Scope narratives merged into Table 3 entries 3-8, preserving detailed scales and combined isolated outcomes separately from Table 3's product-7 yields.", "evidence_ids": [f"{DOC}:page6:image", f"{DOC}:page6:text"]},
            {"region": "left lower column, 7aa/6aa characterization", "finding": "Same Conditions B experiment as Table 3 entry 2 and Table 4 entry 1; merged rather than duplicated.", "evidence_ids": [f"{DOC}:page6:image", f"{DOC}:page6:text"]},
        ], "record_ids": page_records[6], "unresolved": ["The 5fa paragraph prints t-5ca/c-5ca, an apparent source label typo; Table 2's 5fa selectivity was retained and the conflict logged.", "Spectroscopic characterization was not treated as a separate reaction experiment."]},
    ],
}

(BASE / "raw_model").mkdir(parents=True, exist_ok=True)
(BASE / "coverage").mkdir(parents=True, exist_ok=True)
(BASE / "raw_model" / "extracted_records_pages_0001_0006.json").write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
(BASE / "coverage" / "pages_0001_0006.json").write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

# Mark only this session's six page tasks attempted and attach the actual rendered-image evidence.
tasks_path = BASE / "tasks.json"
tasks = json.loads(tasks_path.read_text())
for task in tasks:
    if task.get("document_id") != DOC:
        continue
    page = int(task["evidence_id"].split(":page", 1)[1].split(":", 1)[0])
    if 1 <= page <= 6:
        task["state"] = "attempted"
        task["visual_evidence_id"] = f"{DOC}:page{page}:image"
        task["reason"] = "Original rendered page image inspected; regions and linked records are documented in coverage/pages_0001_0006.json."
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"records": len(records), "coverage_pages": [p["page"] for p in coverage["pages"]]}, ensure_ascii=False))
