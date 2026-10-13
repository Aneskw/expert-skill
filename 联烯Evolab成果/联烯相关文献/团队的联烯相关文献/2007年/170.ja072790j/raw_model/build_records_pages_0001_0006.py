#!/usr/bin/env python3
import json
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
DOC = "doc_568ce4bf656e1cc8"


def ev(page, kind="text"):
    return f"{DOC}:page{page}:{kind}"


def fact(value, evidence=()):
    return {
        "value": value,
        "evidence_ids": list(evidence),
        "verification": "missing" if value is None else "unreviewed",
    }


def field(name, value, evidence=(), targets=None):
    item = {"name": name, "fact": fact(value, evidence)}
    if targets:
        item["target_entity_ids"] = list(targets)
    return item


def participant(entity_id, role, label, evidence, *, name=None, smiles=None, amounts=()):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence if name else ()),
        "smiles": fact(smiles, evidence if smiles else ()),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": list(amounts),
    }


def record(rid, kind, evidence, participants=(), steps=(), outcomes=(), notes=(), unresolved=()):
    return {
        "record_id": f"{DOC}:{rid}",
        "document_id": DOC,
        "source_reaction_id": rid,
        "record_kind": kind,
        "status": "needs_review",
        "completeness": "partial",
        "evidence_ids": list(dict.fromkeys(evidence)),
        "participants": list(participants),
        "steps": list(steps),
        "outcomes": list(outcomes),
        "notes": [fact(n, evidence) for n in notes],
        "review": {
            "method": "model",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": list(unresolved),
        },
    }


def missing_conditions(*names):
    return [field(name, None) for name in names]


def q(number, unit, **extra):
    return {"number": number, "unit": unit, **extra}


SMILES = {
    "1a": "CC(=C=Cc1ccccc1)C(=O)O",
    "3a": "C=C=CCCCC",
    "3b": "C=C=CCCCCCC",
    "3c": "C=C=CCCCCCCC",
    "3d": "C=C=CCCCCCCCC",
    "3e": "C=C=CC1CCCCC1",
    "3f": "C=C=Cc1ccccc1",
    "3g": "C=C=CCc1ccccc1",
    "3j": "C=C=CCCOC(C)=O",
    "3k": "C=C=CCCN1C(=O)c2ccccc2C1=O",
    "Pd(OAc)2": "CC(=O)[O-].CC(=O)[O-].[Pd+2]",
    "LiBr.H2O": "[Li+].[Br-].O",
    "BQ": "O=C1C=CC(=O)C=C1",
    "HOAc": "CC(=O)O",
    "CH3CN": "CC#N",
    "CH2Cl2": "ClCCl",
    "TFA": "O=C(O)C(F)(F)F",
    "LiCl": "[Li+].[Cl-]",
    "Et2NH": "CCNCC",
    "K2CO3": "[K+].[K+].[O-]C([O-])=O",
    "PhSO2Na": "[Na+].[O-]S(=O)c1ccccc1",
    "NaBH4": "[Na+].[BH4-]",
    "DMF": "CN(C)C=O",
    "DMSO": "CS(C)=O",
    "CH3MgBr": "C[Mg]Br",
    "CuBr.SMe2": "[Cu]Br.CSC",
    "Br2": "BrBr",
}


records = []

# Page 2, Scheme 1: six generic arrows summarizing cited prior work.
lit = [
    ("scheme1a_palladium_allenyl_ketone_homodimerization", "functionalized allene, FG1=R4C(O)", "PdCl2(CH3CN)2", "3-(3'-oxo-1'-alkenyl)-substituted furan pattern"),
    ("scheme1a_gold_allenyl_ketone_homodimerization", "functionalized allene, FG1=R4C(O)", "AuCl3", "2-(3'-oxo-1'-alkenyl)-substituted furan pattern"),
    ("scheme1a_allenoic_acid_homodimerization", "2,3-allenoic acid, FG1=COOH", "PdCl2, oxidants", "bicyclic bibutenolide pattern"),
    ("scheme1b_allenoic_acid_allenyl_ketone", "allenoic acid + allenyl ketone", "PdCl2(CH3CN)2", "heterodimerized two-ring product pattern"),
    ("scheme1b_allenamide_allenyl_ketone", "allenamide + allenyl ketone", "PdCl2(CH3CN)2, benzoquinone", "heterodimerized N-containing product pattern"),
    ("scheme1b_allenoic_acid_allenol_or_carboxylate", "allenoic acid + allenol/allenyl carboxylate", "PdCl2", "cross-coupled cyclization/dienyl product patterns"),
]
for rid, substrate, catalyst, product in lit:
    ee = [ev(2), ev(2, "image")]
    records.append(record(
        rid, "literature_example", ee,
        [participant("prior_substrate", "reactant", substrate, ee),
         participant("prior_catalyst", "catalyst", catalyst, ee),
         participant("prior_product", "product", product, ee)],
        [{"step_id": "scheme_arrow", "participant_ids": ["prior_substrate", "prior_catalyst", "prior_product"], "conditions": []}],
        notes=["Generic Scheme 1 arrow summarizing cited prior literature; not a present-paper experiment."],
        unresolved=["Generic R-group connectivity and all experimental quantities are unspecified in the source scheme."],
    ))

ee2 = [ev(2), ev(2, "image")]
records.append(record(
    "scheme2_proposed_pathway", "mechanism", ee2,
    [participant("allenoic_acid_1", "reactant", "2,3-allenoic acid 1", ee2),
     participant("simple_allene_3", "reactant", "simple allene 3", ee2),
     participant("intermediate_2", "unspecified_agent", "furanonyl metal intermediate 2", ee2),
     participant("intermediate_4", "unspecified_agent", "pi-allylic intermediate 4", ee2),
     participant("pathway_products", "product", "beta-H-elimination or nucleophilic-substitution products", ee2)],
    [
        {"step_id": "cyclic_oxypalladation", "participant_ids": ["allenoic_acid_1", "intermediate_2"], "conditions": []},
        {"step_id": "allene_carbopalladation", "participant_ids": ["simple_allene_3", "intermediate_2", "intermediate_4"], "conditions": []},
        {"step_id": "product_forming_paths", "participant_ids": ["intermediate_4", "pathway_products"], "conditions": []},
    ],
    notes=["Scheme 2 is explicitly proposed as a pathway, not reported as an individual experiment."],
    unresolved=["Metal identity and generic R groups vary; intermediate structures are not independently verified."],
))


def base_scope_participants(substrate, allene, product, evidence, *, substrate_name=None, allene_name=None, pd_mol=2, scale=0.25, allene_scale=0.50):
    return [
        participant("substrate", "reactant", substrate, evidence, name=substrate_name, smiles=SMILES.get(substrate), amounts=[field("amount", q(scale, "mmol"), evidence)]),
        participant("allene", "reactant", allene, evidence, name=allene_name, smiles=SMILES.get(allene), amounts=[field("amount", q(allene_scale, "mmol"), evidence)]),
        participant("lithium_bromide", "reagent", "LiBr.H2O", evidence, name="lithium bromide monohydrate", smiles=SMILES["LiBr.H2O"], amounts=[field("amount", q(0.50, "mmol"), evidence)]),
        participant("benzoquinone", "reagent", "BQ", evidence, name="1,4-benzoquinone", smiles=SMILES["BQ"], amounts=[field("amount", q(0.375, "mmol"), evidence)]),
        participant("palladium_acetate", "catalyst", "Pd(OAc)2", evidence, name="palladium acetate", smiles=SMILES["Pd(OAc)2"], amounts=[field("catalyst_loading", q(pd_mol, "mol%"), evidence)]),
        participant("hoac", "solvent", "HOAc", evidence, name="acetic acid", smiles=SMILES["HOAc"], amounts=[field("volume", q(2, "mL"), evidence)]),
        participant("product", "product", product, evidence),
    ]


# Page 3, Table 1 optimization.
table1 = [
    (1, 1.1, "HOAc", 25, 35, 53),
    (2, 1.1, "HOAc", 13, 35, 44),
    (3, 1.1, "CH3CN", 13, 35, 16),
    (4, 1.1, "CH2Cl2", 10, 35, "trace"),
    (5, 1.1, "HOAc/TFA (10:1)", 31, 35, 19),
    (6, 1.5, "HOAc", 11.5, 35, 67),
    (7, 1.5, "HOAc", 36.5, "r.t.", 43),
    (8, 1.5, "HOAc", 5.5, 60, 70),
    (9, 1.5, "HOAc", 6, 60, 70),
]
for entry, bqeq, solvent, time, temp, yld in table1:
    ee = [ev(3), ev(3, "image")]
    allene_mmol = 0.375 if entry == 2 else 0.50
    pd_mol = 2 if entry == 9 else 5
    solvent_smiles = SMILES.get(solvent)
    pp = [
        participant("substrate_1a", "reactant", "1a", ee, name="2,3-allenoic acid 1a", smiles=SMILES["1a"], amounts=[field("amount", q(0.25, "mmol"), ee)]),
        participant("allene_3a", "reactant", "3a", ee, name="hepta-1,2-diene", smiles=SMILES["3a"], amounts=[field("amount", q(allene_mmol, "mmol"), ee)]),
        participant("lithium_bromide", "reagent", "LiBr.H2O", ee, name="lithium bromide monohydrate", smiles=SMILES["LiBr.H2O"], amounts=[field("equivalents", q(2.0, "equiv"), ee)]),
        participant("benzoquinone", "reagent", "BQ", ee, name="1,4-benzoquinone", smiles=SMILES["BQ"], amounts=[field("equivalents", q(bqeq, "equiv"), ee)]),
        participant("palladium_acetate", "catalyst", "Pd(OAc)2", ee, name="palladium acetate", smiles=SMILES["Pd(OAc)2"], amounts=[field("catalyst_loading", q(pd_mol, "mol%"), ee)]),
        participant("solvent", "solvent", solvent, ee, smiles=solvent_smiles, amounts=[field("volume", q(2, "mL"), ee)]),
        participant("product_z5aa", "product", "Z-5aa", ee),
    ]
    if entry in (3, 4):
        pp.append(participant("added_hoac", "reagent", "HOAc", ee, name="acetic acid", smiles=SMILES["HOAc"], amounts=[field("equivalents", q(2.0, "equiv"), ee)]))
    conditions = [field("time", q(time, "h"), ee), field("temperature", temp if isinstance(temp, str) else q(temp, "°C"), ee), field("operation", "Schlenk tube with screw cap", ee)] + missing_conditions("atmosphere", "workup", "purification")
    outcomes = [field("isolated_yield", yld if isinstance(yld, str) else q(yld, "%"), ee, ["product_z5aa"]), field("yield_measurement_basis", "isolated", ee, ["product_z5aa"])]
    notes = []
    unresolved = ["Workup, purification, and atmosphere are not reported for the optimization row.", "Complex substrate/product stereochemical structures remain unverified."]
    if entry == 6:
        notes.append("Page-2 prose points to 'Table 1, entry 3' for the 1.5-equiv-BQ/67% result, while the printed table places that result in entry 6.")
        unresolved.append("The prose/table entry-number cross-reference conflict is retained without correction.")
    if entry == 9:
        outcomes += [
            field("Z_to_E_ratio", {"minimum": 50, "maximum": 50, "unit": "%", "raw_text": ">50:1"}, ee, ["product_z5aa"]),
            field("cycloisomerization_product_7a", "little amount", ee),
            field("branched_product_6aa", "no significant amount detected", ee),
            field("homodimeric_product_8a", "no significant amount detected", ee),
        ]
        notes.append("The ratio is retained as source text in addition to the machine quantity object; it is a ratio, not a percentage yield.")
    records.append(record(f"table1_entry{entry}", "optimization_entry", ee, pp,
                          [{"step_id": "cyclization", "participant_ids": [p["entity_id"] for p in pp], "conditions": conditions}], outcomes, notes, unresolved))


# Pages 3, 5 and 6, Table 2 plus compound-specific paragraphs.
table2 = [
    (1, "1a", "Ph/Me/H", "Z-5aa", 6, 70, 2),
    (2, "1b", "Ph/n-Pr/H", "Z-5ba", 7, 59, 4),
    (3, "1c", "Ph/i-Bu/H", "Z-5ca", 7, 44, 2),
    (4, "1d", "p-BrC6H4/n-Pr/H", "Z-5da", 6, 51, 2),
    (5, "1e", "p-ClC6H4/n-Bu/H", "Z-5ea", 9, 54, 2),
    (6, "1f", "alpha-naphthyl/Me/H", "Z-5fa", 7, 56, 2),
    (7, "1g", "Ph/Me/Et", "Z-5ga", 8, 60, 2),
    (8, "1h", "Ph/cyclopropylmethyl/H", "Z-5ha", 10, 45, 2),
]
details_t2 = {
    1: (5, [("substrate", 44, 0.25), ("allene", 48, 0.50), ("lithium_bromide", 53, 0.50), ("benzoquinone", 41, 0.375), ("palladium_acetate", 1, 0.0045)], 63, 71),
    2: (5, [("substrate", 51, 0.25), ("allene", 48, 0.50), ("lithium_bromide", 53, 0.50), ("benzoquinone", 41, 0.375), ("palladium_acetate", 2, 0.009)], 56, 59),
    3: (6, [("substrate", 51, 0.236), ("allene", 48, 0.50), ("lithium_bromide", 53, 0.50), ("benzoquinone", 41, 0.375), ("palladium_acetate", 1, 0.0045)], 41, 44),
    4: (6, [("substrate", 70, 0.25), ("allene", 48, 0.50), ("lithium_bromide", 53, 0.50), ("benzoquinone", 41, 0.375), ("palladium_acetate", 1, 0.0045)], 58, 51),
    5: (6, [("substrate", 63, 0.25), ("allene", 48, 0.50), ("lithium_bromide", 53, 0.50), ("benzoquinone", 41, 0.375), ("palladium_acetate", 1, 0.0045)], 58, 54),
    6: (6, [("substrate", 56, 0.25), ("allene", 48, 0.50), ("lithium_bromide", 53, 0.50), ("benzoquinone", 41, 0.375), ("palladium_acetate", 1, 0.0045)], 56, 56),
    7: (6, [("substrate", 47, 0.233), ("allene", 48, 0.50), ("lithium_bromide", 53, 0.50), ("benzoquinone", 41, 0.375), ("palladium_acetate", 1, 0.0045)], 53, 60),
    8: (6, [("substrate", 54, 0.252), ("allene", 48, 0.50), ("lithium_bromide", 53, 0.50), ("benzoquinone", 41, 0.375), ("palladium_acetate", 1, 0.0045)], 44, 45),
}
for entry, substrate, sname, product, time, yld, pdmol in table2:
    detail_page, exact, product_mass, detail_yield = details_t2[entry]
    pages = [3, detail_page]
    if entry == 3:
        pages.append(5)  # heading starts at the bottom of page 5
    ee = [x for p in pages for x in (ev(p), ev(p, "image"))]
    pp = base_scope_participants(substrate, "3a", product, ee, substrate_name=f"2,3-allenoic acid {substrate} ({sname})", allene_name="hepta-1,2-diene", pd_mol=pdmol)
    byid = {p["entity_id"]: p for p in pp}
    detail_ev = [ev(detail_page), ev(detail_page, "image")]
    for entity_id, mass, mmol in exact:
        byid[entity_id]["amounts"].extend([field("mass", q(mass, "mg"), detail_ev), field("amount", q(mmol, "mmol"), detail_ev)])
    byid["product"]["amounts"].append(field("isolated_mass", q(product_mass, "mg"), detail_ev))
    conditions = [field("time", q(time, "h"), ee), field("temperature", q(60, "°C"), ee), field("operation", "Schlenk tube with screw cap", [ev(3), ev(3, "image")]), field("atmosphere", None)]
    if entry == 1:
        conditions += [field("monitoring", "TLC to complete consumption", detail_ev), field("workup", "solvent evaporated", detail_ev), field("purification", "flash chromatography on silica gel", detail_ev)]
    else:
        conditions += missing_conditions("workup", "purification")
    outcomes = [field("table2_reported_yield", q(yld, "%"), [ev(3), ev(3, "image")], ["product"])]
    if entry == 1:
        outcomes += [field("experimental_isolated_yield", q(detail_yield, "%"), detail_ev, ["product"]), field("yield_measurement_basis", "isolated after flash chromatography", detail_ev, ["product"])]
    else:
        outcomes.append(field("compound_specific_reported_yield", q(detail_yield, "%"), detail_ev, ["product"]))
    notes = []
    unresolved = ["Complex substrate/product connectivity and stereochemistry remain unverified.", "No supporting-information source was supplied or associated."]
    if entry == 1:
        notes.append("The same optimized experiment is 70% in Table 2 but 71% in the detailed typical procedure; both source values are retained.")
        unresolved.append("Table/detail yield conflict (70% versus 71%) requires expert source review.")
    if entry == 6:
        notes.append("Figure 1 provides an ORTEP structure for Z-5fa and is associated with this row, not treated as a separate reaction.")
    records.append(record(f"table2_entry{entry}_{product.lower().replace('-', '')}", "substrate_scope_entry", ee, pp,
                          [{"step_id": "cyclization", "participant_ids": [p["entity_id"] for p in pp], "conditions": conditions}], outcomes, notes, unresolved))

# Page 3, equation 1.
ee3 = [ev(3), ev(3, "image")]
records.append(record(
    "equation1_licl_halide_exchange", "reported_experiment", ee3,
    [participant("z5aa_start", "reactant", "Z-5aa", ee3),
     participant("licl", "reagent", "LiCl", ee3, name="lithium chloride", smiles=SMILES["LiCl"], amounts=[field("equivalents", q(1.0, "equiv"), ee3)]),
     participant("water_thf", "solvent", "H2O/THF", ee3),
     participant("z5aa_product", "product", "Z-5aa", ee3),
     participant("z5aa_chloride", "product", "Z-5AA (chloride analogue)", ee3)],
    [{"step_id": "halide_exchange", "participant_ids": ["z5aa_start", "licl", "water_thf", "z5aa_product", "z5aa_chloride"], "conditions": [field("temperature", q(40, "°C"), ee3)] + missing_conditions("time", "atmosphere", "workup", "purification")}],
    [field("combined_reported_yield", q(100, "%"), ee3, ["z5aa_product", "z5aa_chloride"]), field("product_ratio", "Z-5aa:Z-5AA = 1:1", ee3, ["z5aa_product", "z5aa_chloride"])],
    unresolved=["The page-3 equation does not report duration, exact solvent volumes, workup, purification, atmosphere, or yield basis.", "Product structures remain unverified."],
))


# Page 4, Table 3; its footnote explicitly refers to Table 2 footnote a on page 3.
table3 = [
    (1, "1a", "3b", "Z-5ab", 10.5, 62, 2),
    (2, "1a", "3c", "Z-5ac", 6.5, 59, 2),
    (3, "1a", "3d", "Z-5ad", 8, 60, 4),
    (4, "1a", "3e", "Z-5ae", 7, 70, 2),
    (5, "1a", "3f", "Z-5af", 6.5, 88, 2),
    (6, "1a", "3g", "Z-5ag", 5.5, 61, 2),
    (7, "1d", "3b", "Z-5db", 6, 57, 2),
    (8, "1i", "3c", "Z-5ic", 18.5, 50, 2),
    (9, "1j", "3d", "Z-5jd", 10, 56, 2),
]
details_t3 = {
    1: (6, [("substrate", 44, 0.25), ("allene", 62, 0.50), ("lithium_bromide", 53, 0.50), ("benzoquinone", 41, 0.375), ("palladium_acetate", 1, 0.0045)], 59, 62),
    2: (6, [("substrate", 44, 0.25), ("allene", 69, 0.50), ("lithium_bromide", 53, 0.50), ("benzoquinone", 41, 0.375), ("palladium_acetate", 1, 0.0045)], 58, 59),
    3: (6, [("substrate", 44, 0.25), ("allene", 76, 0.50), ("lithium_bromide", 53, 0.50), ("benzoquinone", 41, 0.375), ("palladium_acetate", 2, 0.009)], 61, 60),
}
for entry, substrate, allene, product, time, yld, pdmol in table3:
    pages = [3, 4] + ([6] if entry in details_t3 else [])
    ee = [x for p in pages for x in (ev(p), ev(p, "image"))]
    pp = base_scope_participants(substrate, allene, product, ee, substrate_name=f"2,3-allenoic acid {substrate}", allene_name=f"simple allene {allene}", pd_mol=pdmol)
    outcomes = [field("table3_reported_yield", q(yld, "%"), [ev(4), ev(4, "image")], ["product"])]
    if entry in details_t3:
        detail_page, exact, product_mass, detail_yield = details_t3[entry]
        detail_ev = [ev(detail_page), ev(detail_page, "image")]
        byid = {p["entity_id"]: p for p in pp}
        for entity_id, mass, mmol in exact:
            byid[entity_id]["amounts"].extend([field("mass", q(mass, "mg"), detail_ev), field("amount", q(mmol, "mmol"), detail_ev)])
        byid["product"]["amounts"].append(field("isolated_mass", q(product_mass, "mg"), detail_ev))
        outcomes.append(field("compound_specific_reported_yield", q(detail_yield, "%"), detail_ev, ["product"]))
    conditions = [field("time", q(time, "h"), [ev(4), ev(4, "image")]), field("temperature", q(60, "°C"), [ev(4), ev(4, "image")]), field("operation", "Schlenk tube with screw cap", [ev(3), ev(3, "image")])] + missing_conditions("atmosphere", "workup", "purification")
    records.append(record(f"table3_entry{entry}_{product.lower().replace('-', '')}", "substrate_scope_entry", ee, pp,
                          [{"step_id": "cyclization", "participant_ids": [p["entity_id"] for p in pp], "conditions": conditions}], outcomes,
                          unresolved=["Yield measurement basis, atmosphere, workup, and purification are not stated for this row.", "Complex structures and stereochemistry remain unverified.", "No SI source was supplied or associated."]))


# Page 4, Table 4 functionalized allene scope.
table4 = [
    (1, "1a", "3h", "dimethyl-malonate-functionalized allene", "Z-5ah", 58),
    (2, "1a", "3i", "diethyl-malonate-functionalized allene", "Z-5ai", 60),
    (3, "1a", "3j", "acetoxy-functionalized allene", "Z-5aj", 67),
    (4, "1f", "3j", "acetoxy-functionalized allene", "Z-5fj", 64),
    (5, "1a", "3k", "phthalimide-functionalized allene", "Z-5ak", 74),
]
for entry, substrate, allene, allene_name, product, yld in table4:
    ee = [ev(4), ev(4, "image")]
    pp = base_scope_participants(substrate, allene, product, ee, substrate_name=f"2,3-allenoic acid {substrate}", allene_name=allene_name)
    conditions = missing_conditions("time", "temperature", "atmosphere", "workup", "purification") + [field("operation", "Schlenk tube with screw cap", ee)]
    records.append(record(f"table4_entry{entry}_{product.lower().replace('-', '')}", "substrate_scope_entry", ee, pp,
                          [{"step_id": "cyclization", "participant_ids": [p["entity_id"] for p in pp], "conditions": conditions}],
                          [field("table4_reported_yield", q(yld, "%"), ee, ["product"])],
                          unresolved=["Reaction time, temperature, atmosphere, workup, purification, and yield basis are not given in Table 4.", "Functionalized-allene and product structures remain unverified.", "No SI source was supplied or associated."]))


# Page 4, Table 5 enantioenriched scope.
table5 = [
    (1, "3a", "n-C4H9", "R-(-)-Z-5aa", 63, 98),
    (2, "3b", "n-C6H13", "R-(-)-Z-5ab", 67, 98),
    (3, "3j", "CH2CH2OAc", "R-(-)-Z-5aj", 70, 98),
    (4, "3f", "Ph", "R-(-)-Z-5af", 80, 97),
]
for entry, allene, rgroup, product, yld, ee_value in table5:
    evidence = [ev(4), ev(4, "image")]
    pp = base_scope_participants("R-(-)-1a", allene, product, evidence, substrate_name="R-(-)-2,3-allenoic acid 1a (98% ee)", allene_name=f"simple allene {allene}, R={rgroup}")
    conditions = [field("time", q(6, "h"), evidence), field("temperature", q(60, "°C"), evidence), field("operation", "Schlenk tube with screw cap", evidence)] + missing_conditions("atmosphere", "workup", "purification")
    records.append(record(f"table5_entry{entry}_{product.lower().replace('-', '').replace('(', '').replace(')', '')}", "substrate_scope_entry", evidence, pp,
                          [{"step_id": "enantioenriched_cyclization", "participant_ids": [p["entity_id"] for p in pp], "conditions": conditions}],
                          [field("table5_reported_yield", q(yld, "%"), evidence, ["product"]), field("product_ee", q(ee_value, "%"), evidence, ["product"])],
                          unresolved=["Yield basis, atmosphere, workup, and purification are not stated in Table 5.", "Absolute/axial stereochemical structures remain unverified.", "No SI source was supplied or associated."]))


# Page 4, Scheme 3 proposed stereochemical rationale.
ee4 = [ev(4), ev(4, "image")]
records.append(record(
    "scheme3_stereochemical_rationale", "mechanism", ee4,
    [participant("furanonyl_pd_2", "unspecified_agent", "furanonyl palladium intermediate 2", ee4),
     participant("allene_3", "reactant", "monosubstituted allene 3", ee4),
     participant("anti9", "unspecified_agent", "anti-9 pi-allylpalladium intermediate", ee4),
     participant("syn9", "unspecified_agent", "syn-9 pi-allylpalladium intermediate", ee4),
     participant("bromide", "reagent", "Br-", ee4),
     participant("z5", "product", "Z-5", ee4),
     participant("benzoquinone", "reagent", "benzoquinone", ee4, smiles=SMILES["BQ"]),
     participant("hydroquinone", "product", "hydroquinone", ee4, smiles="Oc1ccc(O)cc1")],
    [
        {"step_id": "face_selective_coordination", "participant_ids": ["furanonyl_pd_2", "allene_3", "anti9", "syn9"], "conditions": []},
        {"step_id": "bromide_attack", "participant_ids": ["anti9", "bromide", "z5"], "conditions": []},
        {"step_id": "palladium_reoxidation", "participant_ids": ["benzoquinone", "hydroquinone"], "conditions": []},
    ],
    notes=["Scheme 3 is a rationale for stereoselectivity, not an independently reported experiment."],
    unresolved=["Generic intermediates and R groups are not independently structure-verified."],
))


def application_record(rid, start, product_specs, reagent_specs, solvent, conditions, outcomes, evidence_pages, unresolved_extra=()):
    evidence = [x for p in evidence_pages for x in (ev(p), ev(p, "image"))]
    pp = [participant("start", "reactant", start, evidence)]
    for eid, label, role in reagent_specs:
        amounts = [field("catalyst_loading", q(5, "mol%"), [ev(4), ev(4, "image")])] if label == "CuBr.SMe2" else []
        pp.append(participant(eid, role, label, evidence, smiles=SMILES.get(label), amounts=amounts))
    pp.append(participant("solvent", "solvent", solvent, evidence, smiles=SMILES.get(solvent)))
    for eid, label in product_specs:
        pp.append(participant(eid, "product", label, evidence))
    conds = [field(name, value, evidence) for name, value in conditions] + missing_conditions("time", "atmosphere", "workup", "purification")
    outs = [field(name, value, evidence, targets) for name, value, targets in outcomes]
    return record(rid, "reported_experiment", evidence, pp,
                  [{"step_id": "synthetic_application", "participant_ids": [p["entity_id"] for p in pp], "conditions": conds}], outs,
                  unresolved=["Scheme 4 does not state time, atmosphere, workup, purification, or yield basis.", "Product connectivity/stereochemistry remain unverified.", *unresolved_extra])


records += [
    application_record("scheme4_diethylamine_substitution", "Z-5aa", [("z10", "Z-10")], [("et2nh", "Et2NH", "reagent"), ("k2co3", "K2CO3", "reagent")], "DMF", [("temperature", "r.t.")], [("reported_yield", q(66, "%"), ["z10"])], [4, 5]),
    application_record("scheme4_benzenesulfinate_substitution", "Z-5aa", [("z11", "Z-11")], [("phso2na", "PhSO2Na", "reagent")], "DMF", [("temperature", q(-22, "°C"))], [("reported_yield", q(93, "%"), ["z11"])], [4, 5]),
    application_record("scheme4_borohydride_reduction", "Z-5aa", [("e12", "E-12")], [("nabh4", "NaBH4", "reagent")], "DMSO", [("temperature", None)], [("reported_yield", q(71, "%"), ["e12"]), ("regioselectivity_ratio", "15:1", ["e12"]), ("Z_to_E_ratio", "1:22", ["e12"])], [4, 5]),
    application_record("scheme4_grignard_substitution_13a", "Z-5aa", [("p13a", "13a")], [("ch3mgbr", "CH3MgBr", "reagent"), ("cubr", "CuBr.SMe2", "catalyst")], "CH2Cl2", [("temperature", q(-78, "°C"))], [("reported_yield", q(90, "%"), ["p13a"]), ("regioselectivity_ratio", "18:1", ["p13a"]), ("diastereomeric_ratio", "25:1", ["p13a"])], [4, 5]),
    application_record("scheme4_grignard_substitution_13b", "Z-5fa", [("p13b", "13b")], [("ch3mgbr", "CH3MgBr", "reagent"), ("cubr", "CuBr.SMe2", "catalyst")], "CH2Cl2", [("temperature", q(-78, "°C"))], [("reported_yield", q(80, "%"), ["p13b"]), ("regioselectivity_ratio", ">25:1", ["p13b"]), ("diastereomeric_ratio", ">50:1", ["p13b"])], [4, 5]),
    application_record("scheme4_bromination_14ba_14bb", "13b", [("p14ba", "14ba"), ("p14bb", "14bb")], [("br2", "Br2", "reagent")], "CH2Cl2", [("temperature", None)], [("reported_yield_14ba", q(14, "%"), ["p14ba"]), ("reported_yield_14bb", q(77, "%"), ["p14bb"])], [5], ["Figure 2 supports the relative stereochemical assignment of 14bb but is not itself a reaction."]),
]


out = BASE / "raw_model" / "records_pages_0001_0006.json"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(records, ensure_ascii=False, indent=2))

ids = lambda prefix: [r["record_id"] for r in records if r["source_reaction_id"].startswith(prefix)]
table3_ids = ids("table3_")
coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1,
            "state": "attempted",
            "regions": [
                {"region": "title, abstract, and introduction across the original page", "finding": "No row-level present-paper experiment, table, or reaction arrow; abstract gives high-level reaction and application claims only.", "evidence_ids": [ev(1, "image"), ev(1)]},
            ],
            "record_ids": [],
            "unresolved": ["Abstract-level claims were not converted into duplicate experiments; structures and details are supplied later."],
        },
        {
            "page": 2,
            "state": "attempted",
            "regions": [
                {"region": "upper-left Scheme 1", "finding": "Six generic arrows summarize cited prior-work homo- and heterodimerization patterns; classified as literature examples.", "evidence_ids": [ev(2, "image"), ev(2)]},
                {"region": "upper-right Scheme 2", "finding": "Proposed multi-step pathway via intermediates 2 and 4; classified as mechanism.", "evidence_ids": [ev(2, "image"), ev(2)]},
                {"region": "Results and Discussion prose, lower-right", "finding": "Narrative context for Table 1; no additional independent condition beyond the later table rows.", "evidence_ids": [ev(2, "image"), ev(2)]},
            ],
            "record_ids": ids("scheme1") + ids("scheme2"),
            "unresolved": ["Generic R-group structures and complete procedures for cited work are not present on this page.", "The prose cross-reference to the 1.5-equiv-BQ result points to entry 3 whereas Table 1 places 67% in entry 6."],
        },
        {
            "page": 3,
            "state": "attempted",
            "regions": [
                {"region": "upper-left Table 1 and footnotes", "finding": "Nine independent optimization entries extracted, including solvent/additive footnote overrides and trace result.", "evidence_ids": [ev(3, "image"), ev(3)]},
                {"region": "upper-right Table 2 and footnotes", "finding": "Eight independent substrate-scope entries extracted; later compound paragraphs are merged into the same records.", "evidence_ids": [ev(3, "image"), ev(3)]},
                {"region": "lower-left equation 1", "finding": "LiCl halide-exchange experiment extracted with quantitative combined yield and 1:1 product ratio.", "evidence_ids": [ev(3, "image"), ev(3)]},
                {"region": "center-right Figure 1", "finding": "ORTEP of Z-5fa linked to Table 2 entry 6; not treated as an additional reaction.", "evidence_ids": [ev(3, "image"), ev(3)]},
            ],
            "record_ids": ids("table1_") + ids("table2_") + ids("equation1_") + table3_ids,
            "unresolved": ["Table 2 does not state yield basis.", "Equation 1 omits duration, solvent volumes, workup, purification, atmosphere, and yield basis.", "Complex structures remain unverified."],
        },
        {
            "page": 4,
            "state": "attempted",
            "regions": [
                {"region": "upper-left Table 3", "finding": "Nine independent simple-allene scope entries extracted; entry 3 catalyst-loading footnote applied only to its row.", "evidence_ids": [ev(4, "image"), ev(4)]},
                {"region": "middle-left Table 4", "finding": "Five independent functionalized-allene scope entries extracted from structures and row labels.", "evidence_ids": [ev(4, "image"), ev(4)]},
                {"region": "upper-right Table 5", "finding": "Four independent enantioenriched-substrate scope entries extracted with yield and product ee.", "evidence_ids": [ev(4, "image"), ev(4)]},
                {"region": "middle-right Scheme 3", "finding": "Proposed stereochemical rationale and catalyst reoxidation classified as mechanism.", "evidence_ids": [ev(4, "image"), ev(4)]},
                {"region": "lower-right synthetic-utility prose", "finding": "Narrative facts for Z-10, Z-11, E-12 and Cu-catalyzed substitution merged into Scheme 4 application records.", "evidence_ids": [ev(4, "image"), ev(4)]},
            ],
            "record_ids": table3_ids + ids("table4_") + ids("table5_") + ids("scheme3_") + ids("scheme4_diethyl") + ids("scheme4_benzen") + ids("scheme4_borohydride") + ids("scheme4_grignard"),
            "unresolved": ["Table 4 omits time, temperature, yield basis, atmosphere, workup, and purification.", "Table 5 omits yield basis, atmosphere, workup, and purification.", "Generic mechanism structures remain unverified."],
        },
        {
            "page": 5,
            "state": "attempted",
            "regions": [
                {"region": "top Scheme 4", "finding": "Six distinct present-paper synthetic-application experiments extracted: three substitutions/reduction, two substrate-specific Grignard cases, and one bromination producing two products.", "evidence_ids": [ev(5, "image"), ev(5)]},
                {"region": "left-column typical procedure for Z-5aa", "finding": "Detailed quantities, TLC monitoring, solvent evaporation, flash chromatography, mass, and 71% yield merged into Table 2 entry 1.", "evidence_ids": [ev(5, "image"), ev(5)]},
                {"region": "right-column Z-5ba paragraph and Z-5ca heading", "finding": "Z-5ba details merged into Table 2 entry 2; cross-page Z-5ca heading linked to its page-6 paragraph.", "evidence_ids": [ev(5, "image"), ev(5)]},
                {"region": "lower-right Figure 2", "finding": "ORTEP of 14bb linked to the bromination record; not treated as an extra reaction.", "evidence_ids": [ev(5, "image"), ev(5)]},
            ],
            "record_ids": ids("scheme4_") + ids("table2_entry1_") + ids("table2_entry2_") + ids("table2_entry3_"),
            "unresolved": ["Scheme 4 omits times, atmospheres, workups, purifications, and yield bases.", "Table 2 and the typical Z-5aa procedure report 70% and 71%, respectively; both are retained."],
        },
        {
            "page": 6,
            "state": "attempted",
            "regions": [
                {"region": "left and right columns, experimental paragraphs 3–10", "finding": "Compound-specific preparations Z-5ca through Z-5ha and Z-5ab/Z-5ac merged into their Table 2 or Table 3 rows.", "evidence_ids": [ev(6, "image"), ev(6)]},
                {"region": "bottom-right experimental paragraph 11", "finding": "Z-5ad preparation begins here; page-6 quantities, time, temperature, mass and yield merged with Table 3 entry 3, while characterization continues beyond this page.", "evidence_ids": [ev(6, "image"), ev(6)]},
            ],
            "record_ids": ids("table2_entry3_") + ids("table2_entry4_") + ids("table2_entry5_") + ids("table2_entry6_") + ids("table2_entry7_") + ids("table2_entry8_") + ids("table3_entry1_") + ids("table3_entry2_") + ids("table3_entry3_"),
            "unresolved": ["Most abbreviated paragraphs do not restate atmosphere, workup, purification, or yield basis.", "The Z-5ad paragraph and characterization continue onto page 7; page 7 is not claimed as covered in this session."],
        },
    ],
}
coverage_path = BASE / "coverage" / "pages_0001_0006.json"
coverage_path.parent.mkdir(parents=True, exist_ok=True)
coverage_path.write_text(json.dumps(coverage, ensure_ascii=False, indent=2))

tasks_path = BASE / "tasks.json"
tasks = json.loads(tasks_path.read_text())
for task in tasks:
    if task["document_id"] == DOC and any(task["evidence_id"] == ev(page) for page in range(1, 7)):
        task["state"] = "attempted"
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2))

print(json.dumps({"records": len(records), "coverage_pages": len(coverage["pages"]), "output": str(out)}, ensure_ascii=False))
