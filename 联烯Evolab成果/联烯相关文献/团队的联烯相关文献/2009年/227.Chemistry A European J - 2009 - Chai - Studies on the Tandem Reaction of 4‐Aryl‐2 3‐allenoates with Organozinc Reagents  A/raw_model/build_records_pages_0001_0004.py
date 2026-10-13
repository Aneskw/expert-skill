#!/usr/bin/env python3
"""Build evidence-linked records for Chai et al., Chem. Eur. J. 2009, PDF pages 1-4."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
DOC = "doc_15c7f302e701c25b"
RAW = ROOT / "raw_model" / "records_pages_0001_0004.json"
COVERAGE = ROOT / "coverage" / "pages_0001_0004.json"


def ev(page, kind="image"):
    return f"{DOC}:page{page}:{kind}"


def fact(value, evidence):
    return {
        "value": value,
        "evidence_ids": list(evidence) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def field(name, value, evidence, targets=None):
    item = {"name": name, "fact": fact(value, evidence)}
    if targets:
        item["target_entity_ids"] = targets
    return item


def participant(entity_id, role, label, evidence, name=None, smiles=None, amounts=()):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence) if name is not None else fact(None, ()),
        "smiles": fact(smiles, evidence) if smiles is not None else fact(None, ()),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": [field(n, v, evidence) for n, v in amounts],
    }


def record(rid, kind, evidence, participants, conditions=(), outcomes=(), notes=(), unresolved=()):
    step = {
        "step_id": "reaction",
        "participant_ids": [p["entity_id"] for p in participants],
        "conditions": [field(n, v, evidence) for n, v in conditions],
    }
    return {
        "record_id": f"{DOC}:{rid}",
        "document_id": DOC,
        "source_reaction_id": rid,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": list(dict.fromkeys(evidence)),
        "participants": participants,
        "steps": [step],
        "outcomes": list(outcomes),
        "notes": [fact(x, evidence) for x in notes],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": list(unresolved),
        },
    }


ALLENOATE = {
    "1a": ("ethyl 2-methyl-4-phenyl-2,3-butadienoate", "CCOC(=O)C(C)=C=Cc1ccccc1"),
    "1b": ("ethyl 2-methyl-4,4-diphenyl-2,3-butadienoate", "CCOC(=O)C(C)=C=C(c1ccccc1)c1ccccc1"),
    "1c": ("ethyl 2-n-propyl-4,4-diphenyl-2,3-butadienoate", "CCOC(=O)C(CCC)=C=C(c1ccccc1)c1ccccc1"),
    "1d": ("ethyl 4-(4-chlorophenyl)-2-methyl-2,3-butadienoate", "CCOC(=O)C(C)=C=Cc1ccc(Cl)cc1"),
    "1e": ("ethyl 4,4-diphenyl-2,3-butadienoate", "CCOC(=O)C=C=C(c1ccccc1)c1ccccc1"),
    "1f": ("methyl 2,4,4-triphenyl-2,3-butadienoate", "COC(=O)C(c1ccccc1)=C=C(c1ccccc1)c1ccccc1"),
}


def allenoate(label, evidence, amounts=()):
    name, smiles = ALLENOATE[label]
    return participant("substrate", "reactant", label, evidence, name, smiles, amounts)


SOLVENTS = {
    "toluene": "Cc1ccccc1",
    "Et2O": "CCOCC",
    "THF": "C1CCOC1",
    "n-hexane": "CCCCCC",
    "benzene": "c1ccccc1",
    "DMSO": "CS(C)=O",
    "1,4-dioxane": "O1CCOCC1",
    "CH2Cl2": "ClCCl",
    "mesitylene": "Cc1cc(C)cc(C)c1",
    "n-heptane": "CCCCCCC",
}


def solvent(label, evidence, amounts=(), entity_id="solvent"):
    return participant(entity_id, "solvent", label, evidence, label, SOLVENTS.get(label), amounts)


records = []

# Page 1, Scheme 1: explicitly separate the cited previous-work branch from this paper's generic branch.
e1 = [ev(1), ev(1, "text")]
records.append(record(
    "scheme1_prior_double_michael_cyclization", "literature_example", e1,
    [
        participant("allenoate", "reactant", "generic 4-aryl-2,3-allenoate 1", e1),
        participant("dialkylzinc", "reagent", "R4_2Zn (R4 = alkyl)", e1),
        participant("cyclohexenone", "product", "5-benzylidenecyclohex-2-enone family", e1),
    ],
    notes=["Top branch of Scheme 1 is attributed to reference 5."],
    unresolved=["Generic R groups, quantities, temperature, duration, yield, and exact structures are not stated on the covered page."],
))
records.append(record(
    "scheme1_current_generic_naphthol_route", "general_scheme", e1,
    [
        participant("allenoate", "reactant", "generic 4-aryl-2,3-allenoate 1", e1),
        participant("organozinc", "reagent", "R4ZnX or R4_2Zn (R4 = alkyl, aryl, or heteroaryl)", e1),
        participant("naphthol", "product", "polysubstituted naphthol 3", e1),
    ],
    notes=["Bottom branch of Scheme 1 summarizes the transformation reported in this paper."],
    unresolved=["Generic R groups and batch-specific conditions/outcomes are resolved only in Table 2."],
))

# Page 2, Table 1 optimization rows.
table1 = [
    (1, 3, "toluene", "RT", 16, 35),
    (2, 2, "toluene", "RT", 17, 18),
    (3, 1, "toluene", "RT", 17, 12),
    (4, 3, "Et2O", "RT", 19, 0),
    (5, 3, "THF", "RT", 19, 0),
    (6, 3, "n-hexane", "RT", 19, 17),
    (7, 3, "benzene", "RT", 19, 34),
    (8, 3, "DMSO", "RT", 19, 0),
    (9, 3, "1,4-dioxane", "RT", 19, 0),
    (10, 3, "toluene", {"number": 70, "unit": "°C"}, 1, 50),
    (11, 3, "xylenes", {"number": 140, "unit": "°C"}, 0.5, 65),
]
for idx, n_equiv, solv, temp, hours, yld in table1:
    evidence = [ev(2), ev(2, "text")]
    if idx == 1:
        evidence = e1 + evidence + [ev(3), ev(3, "text")]
    parts = [
        allenoate("1a", evidence),
        participant("organozinc", "reagent", "diphenylzinc (2a)", evidence, "diphenylzinc", None,
                    [("equivalents", {"number": n_equiv, "unit": "equiv"})]),
        solvent(solv, evidence),
        participant("product", "product", "3aa", evidence, "2-methyl-3,4-diphenyl-1-naphthol"),
    ]
    records.append(record(
        f"table1_entry{idx}", "optimization_entry", evidence, parts,
        conditions=[("temperature", temp), ("time", {"number": hours, "unit": "h"})],
        outcomes=[
            field("NMR_yield_3aa", {"number": yld, "unit": "%"}, evidence, ["product"]),
            field("yield_measurement_basis", "NMR spectroscopy using dibromomethane as internal standard", evidence, ["product"]),
        ],
        unresolved=["Reaction scale, solvent volume, atmosphere, workup, and purification are not stated in Table 1."],
    ))

# Page 2, Table 2 scope rows and method footnotes.
table2 = [
    (1, "1a", "Ph (2a)", 3, None, 0.5, "A", 56, "3aa", None),
    (2, "1b", "Ph (2a)", 3, None, 1, "A", 90, "3ba", None),
    (3, "1c", "Ph (2a)", 3, None, 1, "A", 91, "3ca", None),
    (4, "1e", "Ph (2a)", 3, None, 0.25, "A", 81, "3ea", None),
    (5, "1f", "Ph (2a)", 3, None, 1, "A", 86, "3fa", None),
    (6, "1a", "p-BrC6H4 (2b)", 6, "I", 0.5, "B", 82, "3ab", None),
    (7, "1b", "p-BrC6H4 (2b)", 6, "I", 6.5, "B", 88, "3bb", None),
    (8, "1d", "p-BrC6H4 (2b)", 6, "I", 1.5, "B", 70, "3db", None),
    (9, "1a", "2-thienyl (2c)", 6, "Br", 1, "B", 69, "3ac", None),
    (10, "1b", "2-thienyl (2c)", 6, "Br", 8, "B", 89, "3bc", None),
    (11, "1b", "Et (2d)", 3, None, 2, "B", 93, "3bd", None),
    (12, "1c", "Et (2d)", 3, None, 1, "B", 92, "3cd", None),
    (13, "1b", "nBu (2e)", 6, None, 10.5, "B", 68, "3be", None),
    (14, "1b", "p-FC6H4 (2f)", 6, "Br", 12, "B", 40, "3bf", 40),
    (15, "1b", "p-FC6H4 (2f)", 6, "Br", 10.5, "C", 70, "3bf", None),
]


def organozinc_part(label, n_equiv, evidence):
    role_name = {
        "Ph (2a)": "diphenylzinc (2a)",
        "p-BrC6H4 (2b)": "4-bromophenylzinc iodide (2b)",
        "2-thienyl (2c)": "2-thienylzinc bromide (2c)",
        "Et (2d)": "diethylzinc (2d)",
        "nBu (2e)": "di-n-butylzinc (2e)",
        "p-FC6H4 (2f)": "4-fluorophenylzinc bromide (2f)",
    }[label]
    amounts = [("equivalents", {"number": n_equiv, "unit": "equiv"})]
    if label in ("p-BrC6H4 (2b)", "2-thienyl (2c)", "p-FC6H4 (2f)"):
        amounts.append(("stock_concentration", {"number": 0.5, "unit": "M"}))
    elif label == "Et (2d)":
        amounts.append(("stock_concentration", {"number": 0.88, "unit": "M"}))
    elif label == "nBu (2e)":
        amounts.append(("stock_concentration", {"number": 1, "unit": "M"}))
    return participant("organozinc", "reagent", role_name, evidence, role_name, None, amounts)


for idx, sub, org, n_equiv, halide, hours, method, yld, prod, recovery in table2:
    evidence = [ev(2), ev(2, "text")]
    if idx == 1:
        evidence += [ev(3), ev(3, "text")]
    parts = [
        allenoate(sub, evidence, [("amount", {"number": 0.2, "unit": "mmol"})]),
        organozinc_part(org, n_equiv, evidence),
        solvent("xylenes", evidence, [("volume", {"number": 2, "unit": "mL"})], "substrate_solvent"),
        participant("product", "product", prod, evidence,
                    "3-(4-bromophenyl)-7-chloro-2-methyl-1-naphthol" if prod == "3db" else None,
                    "Cc1c(-c2ccc(Br)cc2)cc2ccc(Cl)cc2c1O" if prod == "3db" else None),
    ]
    conditions = [("time", {"number": hours, "unit": "h"})]
    notes = [f"Table 2 Method {method}; isolated yield."]
    unresolved = ["Atmosphere, workup, and purification are not stated in Table 2; the paper directs readers to Supporting Information for details, but no SI was supplied."]
    if halide:
        notes.append(f"Organozinc halide X = {halide}.")
    if method == "A":
        parts.append(solvent("xylenes", evidence, [("volume", {"number": 3, "unit": "mL"})], "organozinc_solvent"))
        conditions += [
            ("temperature", {"number": 140, "unit": "°C"}),
            ("operation", "substrate solution quickly added dropwise to diphenylzinc solution"),
        ]
    elif method == "B":
        parts.append(solvent("xylenes", evidence, [("volume", {"number": 3, "unit": "mL"})], "distillation_solvent"))
        carrier = "THF" if org in ("p-BrC6H4 (2b)", "2-thienyl (2c)", "p-FC6H4 (2f)") else ("n-hexane" if org == "Et (2d)" else "n-heptane")
        parts.append(solvent(carrier, evidence, entity_id="stock_carrier"))
        conditions += [
            ("temperature", {"number": 140, "unit": "°C"}),
            ("operation", "organozinc stock added to anhydrous xylenes and original low-boiling solvent distilled off; substrate solution then quickly added dropwise"),
        ]
    else:
        parts.append(solvent("mesitylene", evidence, [("volume", {"number": 3, "unit": "mL"})], "distillation_solvent"))
        parts.append(solvent("THF", evidence, entity_id="stock_carrier"))
        conditions += [
            ("temperature", {"number": 160, "unit": "°C"}),
            ("operation", "organozinc THF stock added to anhydrous mesitylene and THF distilled off; substrate solution then quickly added dropwise"),
        ]
    outcomes = [field("isolated_yield", {"number": yld, "unit": "%"}, evidence, ["product"])]
    if recovery is not None:
        outcomes.append(field("recovered_starting_material_yield", {"number": recovery, "unit": "%"}, evidence, ["substrate"]))
    records.append(record(f"table2_entry{idx}", "substrate_scope_entry", evidence, parts, conditions, outcomes, notes, unresolved))

# Page 3, Scheme 2 proposed rationale.
e3 = [ev(3), ev(3, "text")]
records.append(record(
    "scheme2_proposed_tandem_mechanism", "mechanism", e3,
    [
        participant("allenoate", "reactant", "generic 4-aryl-2,3-allenoate 1", e3),
        participant("organozinc", "reagent", "R4ZnX or R4_2Zn", e3),
        participant("A", "unspecified_agent", "proposed conjugate-addition intermediate A", e3),
        participant("B", "unspecified_agent", "proposed electrocyclization intermediate B", e3),
        participant("C", "unspecified_agent", "proposed zinc naphthoxide C", e3),
        participant("product", "product", "naphthol 3", e3),
    ],
    conditions=[("operation", "proposed Michael addition, then either 6pi electrocyclization or intramolecular Friedel-Crafts cyclization, ethanol elimination, and hydrolysis")],
    unresolved=["Intermediates A-C are proposed and not reported as isolated products; generic R groups and exact structures remain unverified."],
))

# Page 3, Scheme 3 top: a distinct Method B experiment not present in Table 2.
parts = [
    allenoate("1a", e3, [("amount", {"number": 0.2, "unit": "mmol"})]),
    participant("organozinc", "reagent", "diethylzinc (2d)", e3, "diethylzinc", None,
                [("equivalents", {"number": 3, "unit": "equiv"}), ("stock_concentration", {"number": 0.88, "unit": "M"})]),
    solvent("n-hexane", e3, entity_id="stock_carrier"),
    solvent("xylenes", e3, [("volume", {"number": 3, "unit": "mL"})], "distillation_solvent"),
    solvent("xylenes", e3, [("volume", {"number": 2, "unit": "mL"})], "substrate_solvent"),
    participant("naphthol", "product", "3ad", e3, "3-ethyl-2-methyl-1-naphthol"),
    participant("cyclohexenone", "product", "5-benzylidenecyclohex-2-enone side product", e3),
]
records.append(record(
    "scheme3_diethylzinc_1a", "reported_experiment", e3, parts,
    conditions=[
        ("temperature", {"number": 140, "unit": "°C"}),
        ("time", {"number": 1, "unit": "h"}),
        ("operation", "Method B: remove n-hexane from the diethylzinc stock in xylenes, then quickly add the substrate solution dropwise"),
    ],
    outcomes=[
        field("isolated_yield_3ad", {"number": 20, "unit": "%"}, e3, ["naphthol"]),
        field("NMR_yield_cyclohexenone", {"number": 6, "unit": "%"}, e3, ["cyclohexenone"]),
    ],
    unresolved=["Atmosphere, workup, purification, and the NMR internal standard for the 6% side-product result are not stated here."],
))

# Page 3, scale-up preparation of 3db; this differs from Table 2 entry 8 in scale and time.
e34 = [ev(3), ev(3, "text"), ev(4), ev(4, "text")]
parts = [
    allenoate("1d", e34, [("mass", {"number": 0.9485, "unit": "g"}), ("amount", {"number": 4.0, "unit": "mmol"})]),
    participant("organozinc", "reagent", "4-bromophenylzinc iodide (2b)", e34, "4-bromophenylzinc iodide", None,
                [("volume", {"number": 24, "unit": "mL"}), ("stock_concentration", {"number": 0.5, "unit": "M"}), ("amount", {"number": 12, "unit": "mmol"}), ("equivalents", {"number": 3, "unit": "equiv"})]),
    solvent("THF", e34, entity_id="stock_carrier"),
    solvent("xylenes", e34, [("volume", {"number": 30, "unit": "mL"})], "distillation_solvent"),
    solvent("xylenes", e34, [("volume", {"number": 20, "unit": "mL"})], "substrate_solvent"),
    participant("product", "product", "3db", e34, "3-(4-bromophenyl)-7-chloro-2-methyl-1-naphthol", "Cc1c(-c2ccc(Br)cc2)cc2ccc(Cl)cc2c1O"),
]
records.append(record(
    "scaleup_3db_4mmol", "reported_experiment", e34, parts,
    conditions=[
        ("atmosphere", "nitrogen"),
        ("temperature", {"number": 140, "unit": "°C"}),
        ("stock_solvent_distillation_time", {"number": 0.5, "unit": "h"}),
        ("time", {"number": 0.5, "unit": "h"}),
        ("operation", "distill THF under a stream of nitrogen; quickly add 1d solution dropwise by syringe at 140 °C; monitor by TLC"),
        ("workup", "quench saturated aqueous NH4Cl (5 mL) dropwise at 0 °C; warm to room temperature; extract with diethyl ether (3 x 60 mL); wash with 5% aqueous HCl, saturated aqueous NaHCO3, and brine; dry over anhydrous Na2SO4; filter and evaporate"),
        ("purification", "silica-gel column chromatography, 30-60 °C petroleum ether/ethyl acetate 50:1"),
    ],
    outcomes=[
        field("product_mass", {"number": 0.9710, "unit": "g"}, e34, ["product"]),
        field("isolated_yield", {"number": 70, "unit": "%"}, e34, ["product"]),
        field("melting_point", {"minimum": 157.5, "maximum": 159.0, "unit": "°C", "raw_text": "157.5-159.0 °C"}, e34, ["product"]),
    ],
    notes=["The analytical characterization continues onto page 4."],
    unresolved=["The source calls this an easily extended 4.0 mmol scale reaction; it is distinct from Table 2 entry 8 (0.2 mmol, 1.5 h)."],
))

# Page 3, Scheme 4: four successive, condition-distinct synthetic operations.
scheme4 = [
    ("scheme4_step_a_tosylation", "3db", "6db", 77,
     [("TsCl", "reagent", "p-toluenesulfonyl chloride", "Cc1ccc(S(=O)(=O)Cl)cc1", [("equivalents", {"number": 3, "unit": "equiv"})]),
      ("Et3N", "reagent", "triethylamine", "CCN(CC)CC", [("equivalents", {"number": 3, "unit": "equiv"})]),
      ("CH2Cl2", "solvent", "dichloromethane", "ClCCl", [])],
     [("initial_temperature", {"number": 0, "unit": "°C"}), ("warm_to", "r.t."), ("time", {"number": 24, "unit": "h"})]),
    ("scheme4_step_b_first_suzuki", "6db", "7db", 87,
     [("boronic_acid", "reagent", "4-methoxyphenylboronic acid", "COc1ccc(B(O)O)cc1", [("equivalents", {"number": 2, "unit": "equiv"})]),
      ("PdPPh3", "catalyst", "tetrakis(triphenylphosphine)palladium(0)", None, [("catalyst_loading", {"number": 5, "unit": "mol%"})]),
      ("K3PO4", "reagent", "potassium phosphate", None, [("equivalents", {"number": 2, "unit": "equiv"})]),
      ("toluene", "solvent", "toluene", "Cc1ccccc1", [])],
     [("temperature", "reflux"), ("time", {"number": 3, "unit": "h"})]),
    ("scheme4_step_c_second_suzuki", "7db", "8db", 94,
     [("boronic_acid", "reagent", "3-methoxyphenylboronic acid", "COc1cccc(B(O)O)c1", [("equivalents", {"number": 1.5, "unit": "equiv"})]),
      ("PdOAc2", "catalyst", "palladium acetate", "CC(=O)O[Pd]OC(C)=O", [("catalyst_loading", {"number": 5, "unit": "mol%"})]),
      ("SPhos", "catalyst", "SPhos", None, [("catalyst_loading", {"number": 10, "unit": "mol%"})]),
      ("K3PO4", "reagent", "potassium phosphate", None, [("equivalents", {"number": 2, "unit": "equiv"})]),
      ("toluene", "solvent", "toluene", "Cc1ccccc1", [])],
     [("temperature", {"number": 110, "unit": "°C"}), ("time", {"number": 1.5, "unit": "h"})]),
    ("scheme4_step_d_third_suzuki", "8db", "9db", "quantitative",
     [("boronic_acid", "reagent", "phenylboronic acid", "OB(O)c1ccccc1", [("equivalents", {"number": 6, "unit": "equiv"})]),
      ("PdOAc2", "catalyst", "palladium acetate", "CC(=O)O[Pd]OC(C)=O", [("catalyst_loading", {"number": 5, "unit": "mol%"})]),
      ("XPhos", "catalyst", "XPhos", None, [("catalyst_loading", {"number": 12.5, "unit": "mol%"})]),
      ("K3PO4", "reagent", "potassium phosphate", None, [("equivalents", {"number": 7.5, "unit": "equiv"})]),
      ("xylenes", "solvent", "xylenes", None, [])],
     [("temperature", "reflux"), ("time", {"number": 25, "unit": "h"})]),
]
product_names = {
    "3db": "3-(4-bromophenyl)-7-chloro-2-methyl-1-naphthol",
    "6db": "tosylated 3db (6db)",
    "7db": "first Suzuki-Miyaura product 7db",
    "8db": "second Suzuki-Miyaura product 8db",
    "9db": "3-[4'-(4-methoxyphenyl)phenyl]-7-(3-methoxyphenyl)-2-methyl-1-phenylnaphthalene",
}
for rid, src, dst, yld, agents, conds in scheme4:
    parts = [participant("substrate", "reactant", src, e3, product_names[src])]
    for entity_id, role, label, smiles, amounts in agents:
        parts.append(participant(entity_id, role, label, e3, label, smiles, amounts))
    parts.append(participant("product", "product", dst, e3, product_names[dst]))
    yield_value = yld if isinstance(yld, str) else {"number": yld, "unit": "%"}
    records.append(record(
        rid, "reported_experiment", e3, parts, conds,
        [field("reported_yield", yield_value, e3, ["product"])],
        notes=["Scheme 4 cites literature procedures for the coupling conditions while presenting the sequence as the synthetic application of 3db."],
        unresolved=["Reaction scale, atmosphere, workup, purification, and explicit yield basis are not stated in Scheme 4; exact product structures remain unverified."],
    ))

assert len(records) == 35, len(records)

coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1,
            "state": "attempted",
            "regions": [
                {
                    "region": "title, introduction, Scheme 1, Figure 1, and opening optimization discussion",
                    "finding": "Scheme 1 was split into a cited prior double-Michael/cyclization branch and this paper's generic naphthol branch. Figure 1 is an ORTEP identity assignment for 3aa, not a separate experiment. Opening prose links the diphenylzinc/toluene result to Table 1 entry 1.",
                    "evidence_ids": [ev(1), ev(1, "text")],
                }
            ],
            "record_ids": [
                f"{DOC}:scheme1_prior_double_michael_cyclization",
                f"{DOC}:scheme1_current_generic_naphthol_route",
                f"{DOC}:table1_entry1",
            ],
            "unresolved": ["Scheme 1 uses generic R groups; Figure 1/crystal assignment does not independently verify machine-generated connectivity."],
        },
        {
            "page": 2,
            "state": "attempted",
            "regions": [
                {
                    "region": "upper-left Table 1 and adjacent optimization prose",
                    "finding": "Eleven independent diphenylzinc-loading/solvent/temperature/time optimization rows extracted with NMR yields and dibromomethane internal-standard basis.",
                    "evidence_ids": [ev(2), ev(2, "text")],
                },
                {
                    "region": "lower half Table 2, method footnotes, and scope discussion",
                    "finding": "Fifteen independent substrate/organozinc scope rows extracted. Methods A-C, stock concentrations/carrier solvents, temperature programs, isolated yields, and entry-14 recovery were applied row-wise.",
                    "evidence_ids": [ev(2), ev(2, "text")],
                },
            ],
            "record_ids": [f"{DOC}:table1_entry{i}" for i in range(1, 12)] + [f"{DOC}:table2_entry{i}" for i in range(1, 16)],
            "unresolved": ["Table 1 omits scale and operational details. Table 2 directs readers to unavailable SI for details; no SI association was inferred."],
        },
        {
            "page": 3,
            "state": "attempted",
            "regions": [
                {
                    "region": "upper-left Scheme 2 and mechanism prose",
                    "finding": "Proposed conjugate-addition/electrocyclization or Friedel-Crafts pathway retained as a mechanism, not an observed batch.",
                    "evidence_ids": [ev(3), ev(3, "text")],
                },
                {
                    "region": "middle-left Scheme 3 and adjacent prose",
                    "finding": "The diethylzinc/1a Method-B experiment was extracted as a distinct batch with 20% isolated 3ad and 6% NMR cyclohexenone. The bottom two arrows duplicate Table 2 entry 1 and Table 1 entry 1 and only enrich their evidence.",
                    "evidence_ids": [ev(3), ev(3, "text")],
                },
                {
                    "region": "upper-right Scheme 4 and lower-right Experimental Section",
                    "finding": "The 4.0 mmol 3db scale-up was kept separate from Table 2 entry 8 because scale/time differ. Four successive Scheme-4 transformations were split by chemical operation and condition set.",
                    "evidence_ids": [ev(3), ev(3, "text")],
                },
            ],
            "record_ids": [
                f"{DOC}:scheme2_proposed_tandem_mechanism",
                f"{DOC}:scheme3_diethylzinc_1a",
                f"{DOC}:table1_entry1",
                f"{DOC}:table2_entry1",
                f"{DOC}:scaleup_3db_4mmol",
                f"{DOC}:scheme4_step_a_tosylation",
                f"{DOC}:scheme4_step_b_first_suzuki",
                f"{DOC}:scheme4_step_c_second_suzuki",
                f"{DOC}:scheme4_step_d_third_suzuki",
            ],
            "unresolved": ["Scheme 4 omits scale and operational details for the four downstream transformations; cited procedures were not consulted."],
        },
        {
            "page": 4,
            "state": "attempted",
            "regions": [
                {
                    "region": "top analytical continuation, acknowledgements, crystallographic note, and references",
                    "finding": "The opening HRMS line continues the page-3 characterization of scale-up product 3db. The remainder contains acknowledgements, 3aa crystal data, references, and publication metadata; no new experiment arrow, table row, or procedure was found.",
                    "evidence_ids": [ev(4), ev(4, "text")],
                }
            ],
            "record_ids": [f"{DOC}:scaleup_3db_4mmol"],
            "unresolved": ["Analytical and crystallographic data support identity but do not establish independent reaction records or verify candidate structures."],
        },
    ],
}

RAW.parent.mkdir(parents=True, exist_ok=True)
COVERAGE.parent.mkdir(parents=True, exist_ok=True)
RAW.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
COVERAGE.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

tasks_path = ROOT / "tasks.json"
tasks = json.loads(tasks_path.read_text())
for task in tasks:
    if task["document_id"] == DOC and task["task_id"] in {ev(p, "text") for p in range(1, 5)}:
        task["state"] = "attempted"
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"records": len(records), "raw": str(RAW), "coverage": str(COVERAGE)}, ensure_ascii=False))
