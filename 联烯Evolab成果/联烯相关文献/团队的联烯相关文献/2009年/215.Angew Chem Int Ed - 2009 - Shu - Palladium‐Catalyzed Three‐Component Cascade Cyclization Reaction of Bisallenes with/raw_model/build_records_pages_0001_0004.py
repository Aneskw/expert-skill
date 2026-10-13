#!/usr/bin/env python3
"""Build source-faithful machine records for doc_9cc9a3d021ec1861, PDF pages 1-4."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "runs/current"
DOC = "doc_9cc9a3d021ec1861"


def ev(page):
    return [f"{DOC}:page{page}:text", f"{DOC}:page{page}:image"]


def fact(value, evidence):
    return {"value": value, "evidence_ids": list(evidence),
            "verification": "missing" if value is None else "unreviewed"}


def field(name, value, evidence, targets=None):
    item = {"name": name, "fact": fact(value, evidence)}
    if targets:
        item["target_entity_ids"] = targets
    return item


def participant(entity_id, role, label, evidence, name=None, smiles=None, amounts=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence) if name else fact(None, []),
        "smiles": fact(smiles, evidence) if smiles else fact(None, []),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": amounts or [],
    }


def q(name, number, unit, evidence, **extra):
    value = {"number": number, "unit": unit}
    value.update(extra)
    return field(name, value, evidence)


def missing_conditions(evidence, *, time=True, volume=False):
    items = []
    if time:
        items.append(field("time", None, []))
    if volume:
        items.append(field("solvent_volume", None, []))
    items += [field("atmosphere", None, []), field("workup", None, []),
              field("purification", None, [])]
    return items


def record(rid, kind, evidence, participants, conditions, outcomes, notes=None, unresolved=None):
    return {
        "record_id": f"{DOC}:{rid}",
        "document_id": DOC,
        "source_reaction_id": rid,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": list(dict.fromkeys(evidence)),
        "participants": participants,
        "steps": [{"step_id": "reaction", "participant_ids": [p["entity_id"] for p in participants],
                   "conditions": conditions}],
        "outcomes": outcomes,
        "notes": [fact(x, evidence) for x in (notes or [])],
        "review": {"method": "none", "reviewer": None, "checked_fields": [],
                   "unresolved": unresolved or []},
    }


SMILES = {
    "1a": "COC(=O)OC(C)(C)C#Cc1ccccc1",
    "2a": "OB(O)c1ccccc1",
    "3a": "C=C=CCN(CC=C=C)S(=O)(=O)c1ccc(C)cc1",
    "na2co3": "[Na+].[Na+].[O-]C([O-])=O",
    "dce": "ClCCCl",
    "dmso": "CS(C)=O",
    "cb": "Clc1ccccc1",
    "dioxane": "O1CCOCC1",
    "toluene": "Cc1ccccc1",
    "nitromethane": "C[N+](=O)[O-]",
}


def core_participants(evidence, catalyst, ligand, solvent, *, base=True, product="cis-5a"):
    cat_label, cat_name = catalyst
    lig_label, lig_name = ligand
    solv_label, solv_name, solv_smiles = solvent
    ps = [
        participant("bisallene_3a", "reactant", "3a", evidence, "1,5-bisallene 3a", SMILES["3a"],
                    [q("amount", 0.20, "mmol", evidence)]),
        participant("carbonate_1a", "reactant", "1a", evidence, "propargylic carbonate 1a", SMILES["1a"],
                    [q("amount", 0.24, "mmol", evidence), q("equivalents", 1.2, "equiv", evidence)]),
        participant("boronic_2a", "reactant", "2a", evidence, "phenylboronic acid", SMILES["2a"],
                    [q("amount", 0.40, "mmol", evidence), q("equivalents", 2.0, "equiv", evidence)]),
        participant("palladium", "catalyst", cat_label, evidence, cat_name, None,
                    [q("catalyst_loading", 5, "mol%", evidence)]),
        participant("ligand", "reagent", lig_label, evidence, lig_name, None,
                    [q("ligand_loading", 10, "mol%", evidence)]),
    ]
    if base:
        ps.append(participant("base", "reagent", "Na2CO3", evidence, "sodium carbonate", SMILES["na2co3"],
                              [q("equivalents", 2.0, "equiv", evidence)]))
    ps += [participant("solvent", "solvent", solv_label, evidence, solv_name, solv_smiles),
           participant("product", "product", product, evidence, product)]
    return ps


records = []

# Table 1. Entry 4 is built later because it is the same experiment as Table 2 entry 1 and the typical procedure.
t1 = [
    (1, ("Pd(OAc)2", "palladium(II) acetate"), ("TFP", "tri(2-furyl)phosphine"), True,
     ("DCE", "1,2-dichloroethane", SMILES["dce"]), 80, {"number": 58, "unit": "%"}),
    (2, ("Pd(OAc)2", "palladium(II) acetate"), ("TFP", "tri(2-furyl)phosphine"), False,
     ("DCE", "1,2-dichloroethane", SMILES["dce"]), 80, "trace"),
    (3, ("Pd(OAc)2", "palladium(II) acetate"), ("TFP", "tri(2-furyl)phosphine"), True,
     ("DCE", "1,2-dichloroethane", SMILES["dce"]), 90, {"number": 64, "unit": "%"}),
    (5, ("[Pd(dba)2]", "bis(dibenzylideneacetone)palladium(0)"), ("dppe", "1,2-bis(diphenylphosphanyl)ethane"), True,
     ("DCE", "1,2-dichloroethane", SMILES["dce"]), 90, "n.r. (no reaction)"),
    (6, ("[Pd(dba)2]", "bis(dibenzylideneacetone)palladium(0)"), ("TFP", "tri(2-furyl)phosphine"), True,
     ("DMSO", "dimethyl sulfoxide", SMILES["dmso"]), 90, "trace"),
    (7, ("[Pd(dba)2]", "bis(dibenzylideneacetone)palladium(0)"), ("TFP", "tri(2-furyl)phosphine"), True,
     ("CB", "chlorobenzene", SMILES["cb"]), 90, {"number": 49, "unit": "%"}),
    (8, ("[Pd(dba)2]", "bis(dibenzylideneacetone)palladium(0)"), ("TFP", "tri(2-furyl)phosphine"), True,
     ("dioxane", "1,4-dioxane", SMILES["dioxane"]), 90, {"number": 19, "unit": "%"}),
    (9, ("[Pd(dba)2]", "bis(dibenzylideneacetone)palladium(0)"), ("TFP", "tri(2-furyl)phosphine"), True,
     ("toluene", "toluene", SMILES["toluene"]), 90, {"number": 24, "unit": "%"}),
    (10, ("[Pd(dba)2]", "bis(dibenzylideneacetone)palladium(0)"), ("TFP", "tri(2-furyl)phosphine"), True,
     ("CH3NO2", "nitromethane", SMILES["nitromethane"]), 90, "trace"),
]
for num, cat, lig, base, solvent, temp, result in t1:
    evidence = ev(2) + ev(1)
    ps = core_participants(evidence, cat, lig, solvent, base=base)
    outs = [field("isolated_yield_cis_5a", result, ev(2), ["product"]),
            field("yield_measurement_basis", "yield of isolated 5a", ev(2), ["product"])]
    notes = []
    unresolved = ["Reaction time, atmosphere, workup, and purification are not stated for this optimization row.",
                  "Candidate structures and product stereochemistry remain unverified."]
    if num in (2, 6, 10):
        outs.append(field("reported_conversion_of_3a", "starting material 3a completely consumed", ev(2), ["bisallene_3a"]))
    if num == 2:
        notes.append("The narrative says product could not be obtained in the absence of K2CO3, while Table 1 shows no base and trace product; the table-wide base is Na2CO3.")
        unresolved.append("Narrative K2CO3 versus Table 1 Na2CO3 identity conflict is unresolved.")
    records.append(record(f"table1_entry{num}", "optimization_entry", evidence, ps,
                          [q("temperature", temp, "°C", ev(2)), field("solvent", solvent[0], ev(2))]
                          + missing_conditions(ev(2)), outs, notes, unresolved))

# Cross-table optimized reaction: Table 1 entry 4 = Table 2 entry 1 = typical cis-5a preparation.
e1234 = ev(1) + ev(2) + ev(3) + ev(4)
ps = core_participants(e1234,
                       ("[Pd(dba)2]", "bis(dibenzylideneacetone)palladium(0)"),
                       ("TFP", "tri(2-furyl)phosphine"),
                       ("DCE", "1,2-dichloroethane", SMILES["dce"]))
byid = {p["entity_id"]: p for p in ps}
byid["base"]["amounts"] += [q("mass", 42, "mg", ev(3)), q("amount", 0.40, "mmol", ev(3))]
byid["palladium"]["amounts"] += [q("mass", 6, "mg", ev(3)), q("amount", 0.01, "mmol", ev(3))]
byid["ligand"]["amounts"] += [q("mass", 5, "mg", ev(3)), q("amount", 0.02, "mmol", ev(3))]
byid["bisallene_3a"]["amounts"].append(q("mass", 56, "mg", ev(3)))
byid["boronic_2a"]["amounts"].append(q("mass", 49, "mg", ev(3)))
byid["carbonate_1a"]["amounts"].append(q("mass", 52, "mg", ev(3)))
byid["solvent"]["amounts"].append(q("volume", 2, "mL", ev(3)))
byid["product"]["amounts"] += [q("mass", 71, "mg", ev(3))]
records.append(record(
    "table1_entry4_table2_entry1_cis5a", "optimization_entry", e1234, ps,
    [q("temperature", 90, "°C", ev(1)+ev(2)+ev(3)), q("time", 3, "h", ev(2)),
     field("solvent", "DCE", ev(1)+ev(2)+ev(3)), field("atmosphere", None, []),
     field("operation", "stirred until complete as monitored by TLC", ev(3)),
     field("workup", "solvent evaporated under reduced pressure", ev(3)),
     field("purification", "flash chromatography on silica gel; petroleum ether/ethyl acetate 10:1", ev(3))],
    [field("isolated_yield_cis_5a", {"number": 70, "unit": "%"}, ev(1)+ev(2)+ev(3), ["product"]),
     field("product_mass", {"number": 71, "unit": "mg"}, ev(3), ["product"]),
     field("yield_measurement_basis", "isolated product", ev(2)+ev(3), ["product"]),
     field("diastereoselectivity", "only the cis diastereoisomer was detected", ev(1), ["product"]),
     field("unobserved_alternative_products", "4A, 4B, 5a' and 5a'' were not detected by 1H NMR of the crude mixture", ev(1))],
    ["Table 1 entry 4, Table 2 entry 1, and the typical cis-5a procedure describe the same conditions and 70% result and are merged.",
     "The structure and relative configuration of cis-5a were supported by X-ray diffraction; page 4 reports formula C32H33NO2S and CCDC 703891."],
    ["Atmosphere is not stated.", "Candidate structures and stereochemistry remain unverified."]))

# Table 2 entries 2-9; entry 1 is represented by the cross-table record above.
boronic = {
    2: ("2 (R=4-ClC6H4)", "4-chlorophenylboronic acid", "OB(O)c1ccc(Cl)cc1", 5, 63, "5b"),
    3: ("2 (R=4-MeC6H4)", "4-methylphenylboronic acid", "Cc1ccc(B(O)O)cc1", 3, 70, "5c"),
    4: ("2 (R=4-MeCOC6H4)", "4-acetylphenylboronic acid", "CC(=O)c1ccc(B(O)O)cc1", 5, 64, "5d"),
    5: ("2 (R=3-MeOC6H4)", "3-methoxyphenylboronic acid", "COc1cccc(B(O)O)c1", 6, 66, "5e"),
    6: ("2 (R=4-C6H5C6H4)", "[1,1'-biphenyl]-4-ylboronic acid", "OB(O)c1ccc(-c2ccccc2)cc1", 3, 65, "5f"),
    7: ("2 (R=2-MeOC6H4)", "2-methoxyphenylboronic acid", "COc1ccccc1B(O)O", 4, 65, "5o"),
    8: ("2 (R=benzo[d][1,3]dioxol-5-yl)", "benzo[d][1,3]dioxol-5-ylboronic acid", "OB(O)c1ccc2OCOc2c1", 3, 65, "5g"),
    9: ("2 (R=3,5-Me2C6H3)", "3,5-dimethylphenylboronic acid", "Cc1cc(B(O)O)cc(C)c1", 3, 77, "5h"),
}
for num, (blabel, bname, bsmiles, hours, yld, prod) in boronic.items():
    evidence = ev(2)
    ps = core_participants(evidence,
                           ("[Pd(dba)2]", "bis(dibenzylideneacetone)palladium(0)"),
                           ("TFP", "tri(2-furyl)phosphine"),
                           ("DCE", "1,2-dichloroethane", SMILES["dce"]), product=prod)
    ps = [p for p in ps if p["entity_id"] != "boronic_2a"]
    ps.insert(2, participant("boronic_2", "reactant", blabel, evidence, bname, bsmiles,
                             [q("amount", 0.40, "mmol", evidence), q("equivalents", 2.0, "equiv", evidence)]))
    records.append(record(f"table2_entry{num}_{prod}", "substrate_scope_entry", evidence, ps,
                          [q("temperature", 90, "°C", evidence), q("time", hours, "h", evidence),
                           field("solvent", "DCE", evidence)] + missing_conditions(evidence, time=False, volume=True),
                          [field(f"isolated_yield_{prod}", {"number": yld, "unit": "%"}, evidence, ["product"]),
                           field("yield_measurement_basis", "isolated product", evidence, ["product"])],
                          unresolved=["Solvent volume, atmosphere, workup, and purification are not stated.",
                                      "Candidate structures and product stereochemistry remain unverified."]))

# Prose-only failed terminal-carbonate case.
e2 = ev(2)
ps = core_participants(e2,
                       ("[Pd(dba)2]", "bis(dibenzylideneacetone)palladium(0)"),
                       ("TFP", "tri(2-furyl)phosphine"),
                       ("DCE", "1,2-dichloroethane", SMILES["dce"]), product="expected bicyclo[4.3.0]nonene")
ps = [p for p in ps if p["entity_id"] != "carbonate_1a"]
ps.insert(1, participant("terminal_carbonate", "reactant", "methyl 2-methylbut-3-yn-2-yl carbonate", e2,
                         "methyl 2-methylbut-3-yn-2-yl carbonate", "C#CC(C)(C)OC(=O)OC"))
records.append(record("terminal_propargylic_carbonate_no_reaction", "reported_experiment", e2, ps,
                      [q("temperature", 90, "°C", e2), field("time", None, []), field("solvent", "DCE", e2)]
                      + missing_conditions(e2, time=False, volume=True),
                      [field("reported_yield_expected_product", "does not work", e2, ["product"])],
                      ["The authors suggest that Na2CO3 may be problematic for the acidic terminal alkynic proton."],
                      ["The sentence does not explicitly restate the other substrates, exact scale, duration, yield basis, workup, or purification; standard-condition context is retained but requires review."]))

# Table 3 entries.
t3 = [
    (1, "Me", "nBu", "NTs", 3, 73, "5i"),
    (2, "Me", "nBu", "C(E1)2; E1=CO2Bn", 4, 67, "5j"),
    (3, "Me", "nBu", "C(E2)2; E2=SO2Ph", 4, 61, "5k"),
    (4, "Me", "4-BrC6H4", "NTs", 5, 68, "5l"),
    (5, "-(CH2)4-", "Ph", "NTs", 3, 67, "5m"),
]
for num, r1, r2, x, hours, yld, prod in t3:
    evidence = ev(2)
    ps = [
        participant("carbonate_1", "reactant", f"1 (R1={r1}, R2={r2})", evidence,
                    f"propargylic carbonate 1, R1={r1}, R2={r2}", None,
                    [q("amount", 0.24, "mmol", evidence)]),
        participant("boronic_2a", "reactant", "2a", evidence, "phenylboronic acid", SMILES["2a"],
                    [q("amount", 0.40, "mmol", evidence)]),
        participant("bisallene_3", "reactant", f"3 (X={x})", evidence, f"bisallene 3, X={x}", None,
                    [q("amount", 0.20, "mmol", evidence)]),
        participant("palladium", "catalyst", "[Pd(dba)2]", evidence, "bis(dibenzylideneacetone)palladium(0)", None,
                    [q("catalyst_loading", 5, "mol%", evidence)]),
        participant("ligand", "reagent", "TFP", evidence, "tri(2-furyl)phosphine", None,
                    [q("ligand_loading", 10, "mol%", evidence)]),
        participant("base", "reagent", "Na2CO3", evidence, "sodium carbonate", SMILES["na2co3"],
                    [q("equivalents", 2.0, "equiv", evidence)]),
        participant("solvent", "solvent", "DCE", evidence, "1,2-dichloroethane", SMILES["dce"]),
        participant("product", "product", prod, evidence, f"cis-fused bicyclo[4.3.0]nonene {prod}"),
    ]
    records.append(record(f"table3_entry{num}_{prod}", "substrate_scope_entry", evidence, ps,
                          [q("temperature", 90, "°C", evidence), q("time", hours, "h", evidence),
                           field("solvent", "DCE", evidence)] + missing_conditions(evidence, time=False, volume=True),
                          [field(f"isolated_yield_{prod}", {"number": yld, "unit": "%"}, evidence, ["product"]),
                           field("yield_measurement_basis", "isolated product", evidence, ["product"])],
                          unresolved=["Complete structures for the substituted carbonate/bisallene/product, solvent volume, atmosphere, workup, and purification are not stated or not independently verified."]))

# Scheme 2: independent secondary-propargylic-carbonate experiment.
e3 = ev(3)
ps = [
    participant("carbonate_1e", "reactant", "1e", e3, "secondary propargylic carbonate 1e", None,
                [q("equivalents", 1.2, "equiv", e3)]),
    participant("boronic_2b", "reactant", "2b", e3, "4-chlorophenylboronic acid", "OB(O)c1ccc(Cl)cc1",
                [q("equivalents", 2.0, "equiv", e3)]),
    participant("bisallene_3a", "reactant", "3a", e3, "1,5-bisallene 3a", SMILES["3a"]),
    participant("palladium", "catalyst", "[Pd(dba)2]", e3, "bis(dibenzylideneacetone)palladium(0)", None,
                [q("catalyst_loading", 5, "mol%", e3)]),
    participant("ligand", "reagent", "TFP", e3, "tri(2-furyl)phosphine", None,
                [q("ligand_loading", 10, "mol%", e3)]),
    participant("base", "reagent", "Na2CO3", e3, "sodium carbonate", SMILES["na2co3"],
                [q("equivalents", 2.0, "equiv", e3)]),
    participant("solvent", "solvent", "DCE", e3, "1,2-dichloroethane", SMILES["dce"]),
    participant("product", "product", "cis-(E)-5n", e3, "cis-(E)-5n"),
]
records.append(record("scheme2_cis_e_5n", "reported_experiment", e3, ps,
                      [q("temperature", 90, "°C", e3), q("time", 6, "h", e3), field("solvent", "DCE", e3)]
                      + missing_conditions(e3, time=False, volume=True),
                      [field("reported_yield_cis_e_5n", {"number": 41, "unit": "%"}, e3, ["product"]),
                       field("diastereoselectivity", "single diastereoisomer; only cis-(E)-5n was formed", e3, ["product"]),
                       field("stereochemical_assignment_basis", "1H NMR of the crude mixture and NOE study", ev(2)+e3, ["product"])],
                      unresolved=["Reaction scale, solvent volume, yield basis, atmosphere, workup, and purification are not stated.",
                                  "The complex substrate/product connectivity and stereochemistry remain unverified."]))

# Schemes 1 and 3 are proposed pathways, not completed experiments.
records.append(record("scheme1_possible_pathways", "mechanism", ev(1), [],
                      [field("operation", "possible pathways through M1, syn-M2, M3-A or M3-B to 4A/4B", ev(1))], [],
                      ["Scheme 1 is a proposed pathway map and is not a reported experiment."],
                      ["Generic R groups and organopalladium intermediate structures remain unresolved."]))
records.append(record("scheme3_plausible_mechanism", "mechanism", ev(3), [],
                      [field("operation", "proposed oxidative addition, three carbopalladations, allylic isomerization, and Suzuki-type coupling via M1/syn-M2/cis-M3-B/M4/M5", ev(3))], [],
                      [{"direct_coupling_product_statement": {"number": 5, "unit": "%", "qualifier": "lt", "raw_text": "less than 5%"}}],
                      ["The pathway is explicitly described as plausible; intermediate structures are not experimentally established."]))

# Coverage ledger.
ids = [r["record_id"] for r in records]
def rid(s): return f"{DOC}:{s}"
table1_ids = [rid(f"table1_entry{i}") for i in [1,2,3]] + [rid("table1_entry4_table2_entry1_cis5a")] + [rid(f"table1_entry{i}") for i in [5,6,7,8,9,10]]
table2_ids = [rid("table1_entry4_table2_entry1_cis5a")] + [rid(f"table2_entry{i}_{boronic[i][5]}") for i in range(2,10)]
table3_ids = [rid(f"table3_entry{i}_{t3[i-1][6]}") for i in range(1,6)]
coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {"page": 1, "state": "attempted", "regions": [
            {"region": "upper and left title/introduction plus Scheme 1", "finding": "Scheme 1 is a proposed pathway map with generic R groups; it is classified as mechanism, not a completed experiment.", "evidence_ids": ev(1)},
            {"region": "right-column initial-results prose", "finding": "Narrative support for Table 1 entries 1-10 and the optimized cis-5a experiment; alternative products 4A/4B/5a'/5a'' were not detected under the standard conditions.", "evidence_ids": ev(1)},
        ], "record_ids": table1_ids + [rid("scheme1_possible_pathways")],
         "unresolved": ["The prose says absence of K2CO3 whereas Table 1 uses Na2CO3 as the base; this source conflict is retained.", "Scheme structures and complex product stereochemistry remain unverified."]},
        {"page": 2, "state": "attempted", "regions": [
            {"region": "upper-left Table 1 and footnotes", "finding": "Ten independent optimization rows extracted; entry 4 is merged with Table 2 entry 1 and the typical cis-5a procedure.", "evidence_ids": ev(2)},
            {"region": "upper-right Table 2 and footnotes", "finding": "Nine boronic-acid scope rows extracted, including row-specific times and isolated yields.", "evidence_ids": ev(2)},
            {"region": "lower-right prose and Table 3", "finding": "Five carbonate/bisallene scope rows and one prose-only terminal-carbonate failure extracted.", "evidence_ids": ev(2)},
            {"region": "lower-left Figure 1", "finding": "ORTEP of cis-5a supports the standard experiment and is not an additional reaction.", "evidence_ids": ev(2)},
        ], "record_ids": table1_ids + table2_ids + table3_ids + [rid("terminal_propargylic_carbonate_no_reaction")],
         "unresolved": ["Most table rows omit atmosphere, workup, purification, and solvent volume.", "The prose-only terminal-carbonate failure does not restate all substrates, scale, duration, or yield basis."]},
        {"page": 3, "state": "attempted", "regions": [
            {"region": "upper-left Scheme 2", "finding": "Independent 1e/2b/3a experiment extracted: cis-(E)-5n, 41%, 90 °C, 6 h, single diastereomer.", "evidence_ids": ev(3)},
            {"region": "left Scheme 3 and mechanism prose", "finding": "Proposed multistep palladium pathway classified as mechanism; the less-than-5% direct-coupling statement is retained as contextual source data.", "evidence_ids": ev(3)},
            {"region": "right Experimental Section", "finding": "Typical cis-5a procedure merged with Table 1 entry 4/Table 2 entry 1, adding exact quantities, TLC endpoint, workup, purification, product mass, and 70% yield.", "evidence_ids": ev(3)},
        ], "record_ids": [rid("scheme2_cis_e_5n"), rid("scheme3_plausible_mechanism"), rid("table1_entry4_table2_entry1_cis5a")],
         "unresolved": ["The typical procedure does not state atmosphere.", "Mechanistic intermediates are proposed and not independently established."]},
        {"page": 4, "state": "attempted", "regions": [
            {"region": "both columns", "finding": "References and crystallographic data only; CCDC 703891/formula data support cis-5a identity but do not constitute another reaction.", "evidence_ids": ev(4)},
        ], "record_ids": [rid("table1_entry4_table2_entry1_cis5a")],
         "unresolved": ["No additional present-paper experiment is shown on this page."]},
    ]
}

assert len(records) == 27, len(records)
assert len(ids) == len(set(ids))
assert all(rid_ in ids for page in coverage["pages"] for rid_ in page["record_ids"])

(OUT / "raw_model/records_pages_0001_0004.json").write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
(OUT / "coverage/pages_0001_0004.json").parent.mkdir(parents=True, exist_ok=True)
(OUT / "coverage/pages_0001_0004.json").write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

tasks_path = OUT / "tasks.json"
tasks = json.loads(tasks_path.read_text())
for task in tasks:
    if task.get("document_id") == DOC and task.get("evidence_id") in {f"{DOC}:page{i}:text" for i in range(1, 5)}:
        task["state"] = "attempted"
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"records": len(records), "coverage_pages": len(coverage["pages"])}, ensure_ascii=False))
