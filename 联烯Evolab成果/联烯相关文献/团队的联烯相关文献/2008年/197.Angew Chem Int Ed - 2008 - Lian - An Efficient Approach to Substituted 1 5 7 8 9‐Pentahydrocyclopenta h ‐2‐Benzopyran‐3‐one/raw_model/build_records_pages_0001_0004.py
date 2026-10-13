#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "runs/current/raw_model/records_pages_0001_0004.json"
COVERAGE = ROOT / "runs/current/coverage/pages_0001_0004.json"
TASKS = ROOT / "runs/current/tasks.json"
DOC = "doc_ee32c9a5a4c3f084"


def ev(*pages):
    out = []
    for p in pages:
        out.extend([f"{DOC}:page{p}:text", f"{DOC}:page{p}:image"])
    return out


def fact(value, evidence=()):
    return {
        "value": value,
        "evidence_ids": list(evidence) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def field(name, value, evidence, targets=None):
    result = {"name": name, "fact": fact(value, evidence)}
    if targets:
        result["target_entity_ids"] = list(targets)
    return result


def participant(entity_id, role, label, evidence, *, name=None, smiles=None, amounts=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence) if name else fact(None),
        "smiles": fact(smiles, evidence) if smiles else fact(None),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": amounts or [],
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


def q(number, unit, **extra):
    value = {"number": number, "unit": unit}
    value.update(extra)
    return value


records = []

# Scheme 1: cited precedent and the conceptual, unobserved target of the present study.
e = ev(1)
records.append(record(
    "scheme1_prior_aryl_alkenyl_halide_allenoic_acid",
    "literature_example", e,
    [
        participant("scheme1_rx", "reactant", "RX (aryl or alkenyl halide)", e),
        participant("scheme1_allenoic_acid", "reactant", "generic 2,3-allenoic acid 2", e),
        participant("scheme1_prior_product", "product", "generic substituted butenolide", e),
        participant("scheme1_pd0", "catalyst", "Pd(0)", e),
    ],
    [{"step_id": "literature_cyclization", "participant_ids": ["scheme1_rx", "scheme1_allenoic_acid", "scheme1_prior_product", "scheme1_pd0"], "conditions": []}],
    [],
    ["Scheme 1 upper arrow summarizes cited palladium(0)-catalyzed prior work, references 7a-c."],
    ["Generic R groups, exact palladium source, quantities, procedure, and yield are not supplied in this paper."],
))
records.append(record(
    "scheme1_expected_product_ii_concept",
    "general_scheme", e,
    [
        participant("scheme1_carbonate1", "reactant", "generic 2,7-alkadiynylic carbonate 1", e),
        participant("scheme1_acid2", "reactant", "generic 2,3-allenoic acid 2", e),
        participant("scheme1_intermediate_i", "unspecified_agent", "proposed 1,3,4-trienyl palladium intermediate I", e),
        participant("scheme1_expected_ii", "product", "expected II-type butenolide (not observed in the preliminary 1a/2a experiment)", e),
        participant("scheme1_pd", "catalyst", "Pd(0)", e),
    ],
    [{"step_id": "conceptual_path", "participant_ids": ["scheme1_carbonate1", "scheme1_acid2", "scheme1_intermediate_i", "scheme1_expected_ii", "scheme1_pd"], "conditions": []}],
    [],
    ["The lower Scheme 1 path is the authors' initial expectation; the 1a/2a experiment instead gave tricyclic 3a."],
    ["This is a conceptual generic route, not a reported successful preparation of II."],
))


solvents = {
    "MeCN": ("acetonitrile", "CC#N"),
    "DMSO": ("dimethyl sulfoxide", "CS(C)=O"),
    "DCE": ("1,2-dichloroethane", "ClCCCl"),
    "MeNO2": ("nitromethane", "C[N+](=O)[O-]"),
    "THF": ("tetrahydrofuran", "C1CCOC1"),
    "DMF": ("N,N-dimethylformamide", "CN(C)C=O"),
    "NMP": ("N-methyl-2-pyrrolidone", "CN1CCCC1=O"),
    "toluene": ("toluene", "Cc1ccccc1"),
}

table1 = [
    (1, "MeCN", "Pd(PPh3)4", None, 100, 76),
    (2, "DMSO", "Pd(PPh3)4", None, 100, 75),
    (3, "DCE", "Pd(PPh3)4", None, 92, None),
    (4, "MeNO2", "Pd(PPh3)4", None, 100, 87),
    (5, "THF", "Pd(PPh3)4", None, 25, None),
    (6, "DMF", "Pd(PPh3)4", None, 42, None),
    (7, "NMP", "Pd(PPh3)4", None, 23, None),
    (8, "toluene", "Pd(PPh3)4", None, 11, None),
    (9, "MeNO2", "Pd(OAc)2", ("tfp", "tri(furan-2-yl)phosphine", 10), 100, 71),
    (10, "MeNO2", "Pd(OAc)2", ("PPh3", "triphenylphosphine", 10), 83, 66),
    (11, "MeNO2", "Pd(OAc)2", ("dppe", "1,2-bis(diphenylphosphino)ethane", 5), "trace", None),
    (12, "MeNO2", "Pd(OAc)2", ("binap", "2,2'-bis(diphenylphosphino)-1,1'-binaphthyl", 5), "trace", None),
]

table1_ids = []
for entry, solvent, catalyst, ligand, nmr_yield, isolated_yield in table1:
    pages = (1, 2, 3, 4) if entry == 4 else (1, 2)
    e = ev(*pages)
    suffix = "optimized_3a_table1_entry4_table2_entry1" if entry == 4 else f"table1_entry{entry}"
    table1_ids.append(f"{DOC}:{suffix}")
    ps = [
        participant("carbonate_1a", "reactant", "2,7-alkadiynylic carbonate 1a", e,
                    amounts=[field("amount", q(0.3, "mmol"), e)]),
        participant("allenoic_acid_2a", "reactant", "2,3-allenoic acid 2a", e,
                    amounts=[field("amount", q(0.33, "mmol"), e)]),
        participant("product_3a", "product", "tricyclic product 3a", e,
                    amounts=([field("product_mass", q(109, "mg"), ev(3))] if entry == 4 else [])),
        participant("catalyst", "catalyst", catalyst, e,
                    amounts=[field("catalyst_loading", q(5, "mol%"), e)]),
        participant("solvent", "solvent", solvent, e, name=solvents[solvent][0], smiles=solvents[solvent][1],
                    amounts=[field("volume", q(3, "mL"), e)]),
        participant("nmr_internal_standard", "unspecified_agent", "CH2Br2", e,
                    name="dibromomethane", smiles="BrCBr"),
    ]
    if ligand:
        code, lname, loading = ligand
        lsmi = "P(c1ccccc1)(c1ccccc1)c1ccccc1" if code == "PPh3" else None
        ps.append(participant("ligand", "reagent", code, e, name=lname, smiles=lsmi,
                              amounts=[field("ligand_loading", q(loading, "mol%"), e)]))
    conditions = [
        field("atmosphere", "argon", e),
        field("temperature", q(60, "°C"), e),
        field("time", q(1, "h"), e),
    ]
    if entry == 4:
        conditions += [
            field("operation", "sequential addition to a dried and degassed Schlenk tube", ev(3)),
            field("operation", "reaction completion monitored by TLC", ev(3)),
            field("workup", "solvent removed by evaporation", ev(3)),
            field("purification", "silica-gel column chromatography; CH2Cl2 eluent", ev(3)),
        ]
    outcomes = [
        field("nmr_yield_3a", "trace" if nmr_yield == "trace" else q(nmr_yield, "%"), e, ["product_3a"]),
        field("nmr_yield_measurement_basis", "1H NMR spectroscopy with CH2Br2 as internal standard", e, ["product_3a"]),
    ]
    if isolated_yield is not None:
        outcomes += [
            field("isolated_yield_3a", q(isolated_yield, "%"), e, ["product_3a"]),
            field("isolated_yield_measurement_basis", "isolated product", e, ["product_3a"]),
        ]
    notes = [f"Table 1 entry {entry}; catalyst/solvent screen for formation of 3a."]
    unresolved = ["Complex reactant and product structures remain unverified."]
    if entry != 4:
        unresolved.append("Workup and purification are not reported for this optimization row.")
    if isolated_yield is None:
        unresolved.append("No isolated yield is printed for this row.")
    if entry == 4:
        notes += [
            "The same optimized condition appears as Table 1 entry 4, Table 2 entry 1, and the detailed 3a preparation; it is represented once.",
            "Product 3a was characterized by X-ray diffraction (CCDC 675814); crystallographic evidence does not verify the machine structure representation.",
        ]
        unresolved.append("No supporting-information file or CIF is supplied or explicitly associated.")
    records.append(record(suffix, "optimization_entry", e, ps,
                          [{"step_id": "cyclization", "participant_ids": [p["entity_id"] for p in ps if p["entity_id"] != "nmr_internal_standard"], "conditions": conditions}],
                          outcomes, notes, unresolved))


# Table 2 entries 2-11. Entry 1 is the merged optimized 3a record above.
scope_yields = {2: 74, 3: 75, 4: 73, 5: 86, 6: 80, 7: 74, 8: 70, 9: 61, 10: 75, 11: 54}
scope_context = {
    2: "tertiary N-tethered diyne; allyl-substituted allenoic acid; terminal alkyne",
    3: "tertiary N-tethered diyne; aryl-substituted allenoic acid; terminal alkyne",
    4: "tertiary N-tethered diyne; aryl-substituted allenoic acid; terminal alkyne",
    5: "secondary N-tethered diyne; terminal alkyne",
    6: "secondary N-tethered diyne; terminal alkyne",
    7: "tertiary N-tethered diyne; terminal alkyne",
    8: "tertiary N-tethered diyne; terminal alkyne",
    9: "tertiary N-tethered diyne; nonterminal alkyne",
    10: "tertiary oxygen-tethered diyne; nonterminal alkyne",
    11: "primary carbon-tethered diyne; terminal alkyne",
}
scope_ids = [f"{DOC}:optimized_3a_table1_entry4_table2_entry1"]
for entry in range(2, 12):
    e = ev(1, 2)
    product = f"3{chr(96 + entry)}"
    suffix = f"table2_entry{entry}_{product}"
    scope_ids.append(f"{DOC}:{suffix}")
    ps = [
        participant("carbonate_1", "reactant", f"2,7-alkadiynylic carbonate 1 (Table 2 entry {entry})", e,
                    amounts=[field("amount", q(0.3, "mmol"), e)]),
        participant("allenoic_acid_2", "reactant", f"2,3-allenoic acid 2 (Table 2 entry {entry})", e,
                    amounts=[field("amount", q(0.33, "mmol"), e)]),
        participant("scope_product", "product", f"tricyclic product {product}", e),
        participant("pdpph3", "catalyst", "Pd(PPh3)4", e,
                    amounts=[field("catalyst_loading", q(5, "mol%"), e)]),
        participant("men02", "solvent", "MeNO2", e, name="nitromethane", smiles="C[N+](=O)[O-]",
                    amounts=[field("volume", q(3, "mL"), e)]),
    ]
    conditions = [field("atmosphere", "argon", e), field("operation", "reaction conducted in a Schlenk tube", e),
                  field("temperature", q(60, "°C"), e), field("time", q(1, "h"), e)]
    outcomes = [field(f"isolated_yield_{product}", q(scope_yields[entry], "%"), e, ["scope_product"]),
                field("isolated_yield_measurement_basis", "isolated product", e, ["scope_product"])]
    records.append(record(suffix, "substrate_scope_entry", e, ps,
                          [{"step_id": "cyclization", "participant_ids": [p["entity_id"] for p in ps], "conditions": conditions}],
                          outcomes,
                          [f"Table 2 entry {entry}: {scope_context[entry]}."],
                          ["Compound-specific reactant labels, workup, purification, and verified connectivity are not supplied in the main-text row."]))


# Scheme 2: four substrate-synthesis transformations and the asymmetric cyclization.
e = ev(2, 3)
records.append(record(
    "scheme2_prepare_alcohol_5", "reported_experiment", e,
    [
        participant("propargyl_mgbr", "reactant", "propargylmagnesium bromide", e),
        participant("propionaldehyde", "reactant", "propionaldehyde", e, smiles="CCC=O"),
        participant("etmgbr", "reagent", "EtMgBr", e, name="ethylmagnesium bromide"),
        participant("tmscl", "reagent", "TMSCl", e, name="trimethylsilyl chloride", smiles="C[Si](C)(C)Cl"),
        participant("hcl", "reagent", "2 N HCl", e, name="hydrochloric acid", amounts=[field("concentration", "2 N (reported normality)", e)]),
        participant("thf", "solvent", "THF", e, name="tetrahydrofuran", smiles="C1CCOC1"),
        participant("alcohol5", "product", "propargylic alcohol 5", e),
    ],
    [{"step_id": "multistage_preparation", "participant_ids": ["propargyl_mgbr", "propionaldehyde", "etmgbr", "tmscl", "hcl", "thf", "alcohol5"],
      "conditions": [field("operation", "sequential treatment with propionaldehyde, EtMgBr, TMSCl in THF, then 2 N HCl", e)]}],
    [field("reported_yield_5", q(58, "%"), e, ["alcohol5"]), field("yield_measurement_basis", None, e, ["alcohol5"])],
    ["Scheme 2 starting-material synthesis; experimental details are deferred by the paper to Supporting Information."],
    ["Amounts, temperatures, durations, atmosphere, workup, purification, and yield basis are missing; SI is not supplied or associated.", "Product 5 connectivity is machine-unverified."],
))
records.append(record(
    "scheme2_kinetic_resolution_5_6", "reported_experiment", e,
    [
        participant("racemic5", "reactant", "propargylic alcohol 5", e),
        participant("novozym435", "catalyst", "Novozym 435", e),
        participant("vinyl_acetate", "reagent", "vinyl acetate", e, smiles="CC(=O)OC=C"),
        participant("r6", "product", "(R)-6 acetate", e),
        participant("s5", "product", "(S)-5 alcohol", e),
    ],
    [{"step_id": "enzymatic_resolution", "participant_ids": ["racemic5", "novozym435", "vinyl_acetate", "r6", "s5"], "conditions": []}],
    [field("reported_yield_r6", q(35, "%"), e, ["r6"]), field("reported_yield_s5", q(39, "%"), e, ["s5"]), field("yield_measurement_basis", None, e, ["r6", "s5"])],
    ["Scheme 2 enzymatic kinetic resolution gives two isolated labeled fractions."],
    ["Amounts, time, temperature, atmosphere, operations, yield basis, and absolute-configuration verification are missing; SI is not supplied or associated."],
))
records.append(record(
    "scheme2_mitsunobu_r7", "reported_experiment", e,
    [
        participant("s5", "reactant", "(S)-5 alcohol", e),
        participant("propargyl_tosylamide", "reactant", "prop-2-yn-1-yl tosylamide (drawn HCC-CH2-NHTs)", e),
        participant("dead", "reagent", "DEAD", e, name="diethyl azodicarboxylate", smiles="CCOC(=O)N=NC(=O)OCC"),
        participant("pph3", "reagent", "PPh3", e, name="triphenylphosphine", smiles="P(c1ccccc1)(c1ccccc1)c1ccccc1"),
        participant("thf", "solvent", "THF", e, name="tetrahydrofuran", smiles="C1CCOC1"),
        participant("r7", "product", "(R)-7", e),
    ],
    [{"step_id": "mitsunobu_substitution", "participant_ids": ["s5", "propargyl_tosylamide", "dead", "pph3", "thf", "r7"], "conditions": []}],
    [field("reported_yield_r7", q(84, "%"), e, ["r7"]), field("product_ee", q(99, "%", qualifier="gt", raw_text=">99% ee"), e, ["r7"]), field("yield_measurement_basis", None, e, ["r7"])],
    ["Scheme 2 labels the product (R)-7 and reports greater than 99% ee."],
    ["Amounts, time, temperature, atmosphere, workup, purification, yield basis, and stereochemical structure remain missing or unverified."],
))
records.append(record(
    "scheme2_r7_to_r1h", "reported_experiment", e,
    [
        participant("r7", "reactant", "(R)-7", e),
        participant("nbuli", "reagent", "nBuLi", e, name="n-butyllithium"),
        participant("acetone", "reagent", "acetone", e, smiles="CC(=O)C"),
        participant("clcoome", "reagent", "ClCOOMe", e, name="methyl chloroformate", smiles="COC(=O)Cl"),
        participant("tbaf", "reagent", "TBAF", e, name="tetra-n-butylammonium fluoride"),
        participant("thf", "solvent", "THF", e, name="tetrahydrofuran", smiles="C1CCOC1"),
        participant("r1h", "product", "R-(+)-1h", e),
    ],
    [
        {"step_id": "alkyne_functionalization", "participant_ids": ["r7", "nbuli", "acetone", "clcoome"], "conditions": [field("operation", "sequential nBuLi, acetone, then ClCOOMe treatment", e)]},
        {"step_id": "desilylation", "participant_ids": ["r7", "tbaf", "thf", "r1h"], "conditions": [field("operation", "TBAF treatment in THF", e)]},
    ],
    [field("reported_yield_r1h", q(68, "%"), e, ["r1h"]), field("product_ee", q(99, "%", qualifier="gt", raw_text=">99% ee"), e, ["r1h"]), field("yield_measurement_basis", None, e, ["r1h"])],
    ["Scheme 2 gives the sequence as a single arrow with four numbered reagent operations."],
    ["Amounts, temperatures, durations, atmosphere, workup, purification, yield basis, and stereochemical structure remain missing or unverified."],
))
records.append(record(
    "scheme2_cyclization_r1h_to_r3l", "substrate_scope_entry", e,
    [
        participant("r1h", "reactant", "R-(+)-1h", e, amounts=[field("amount", q(0.3, "mmol"), e)]),
        participant("acid2a", "reactant", "2,3-allenoic acid 2a", e, amounts=[field("amount", q(0.33, "mmol"), e)]),
        participant("pdpph3", "catalyst", "Pd(PPh3)4", e, amounts=[field("catalyst_loading", q(5, "mol%"), e)]),
        participant("meno2", "solvent", "MeNO2", e, name="nitromethane", smiles="C[N+](=O)[O-]", amounts=[field("volume", q(3, "mL"), e)]),
        participant("r3l", "product", "R-(-)-3l", e),
    ],
    [{"step_id": "asymmetric_substrate_cyclization", "participant_ids": ["r1h", "acid2a", "pdpph3", "meno2", "r3l"],
      "conditions": [field("atmosphere", "argon", e), field("operation", "standard conditions in a Schlenk tube", e), field("temperature", q(60, "°C"), e), field("time", q(1, "h"), e)]}],
    [field("reported_yield_r3l", q(73, "%"), e, ["r3l"]), field("product_ee", q(99, "%", qualifier="gt", raw_text=">99% ee"), e, ["r3l"]), field("yield_measurement_basis", None, e, ["r3l"])],
    ["The prose says the cyclization used the standard reaction conditions; the Table 2 standard quantities and atmosphere are therefore linked."],
    ["Workup, purification, yield basis, and stereochemical structure are not reported in the supplied main text; SI is not supplied or associated."],
))


# Scheme 3: two independently reported 4-monosubstituted-allenoic-acid reactions.
scheme3_ids = []
for acid, product, substituent, yld in [("2f", "4a", "1-naphthyl", 69), ("2g", "4b", "4-bromophenyl", 59)]:
    pages = (2, 3, 4) if product == "4b" else (2, 3)
    e = ev(*pages)
    suffix = f"scheme3_{acid}_to_{product}"
    scheme3_ids.append(f"{DOC}:{suffix}")
    ps = [
        participant("carbonate1a", "reactant", "2,7-alkadiynylic carbonate 1a", e),
        participant("acid", "reactant", f"4-monosubstituted 2,3-allenoic acid {acid} ({substituent})", e),
        participant("catalyst", "catalyst", "Pd(PPh3)4", e, amounts=[field("catalyst_loading", q(5, "mol%"), e)]),
        participant("solvent", "solvent", "MeNO2", e, name="nitromethane", smiles="C[N+](=O)[O-]"),
        participant("product", "product", f"aromatized tricyclic product {product}", e),
    ]
    notes = ["Scheme 3 reports aromatization for a 4-monosubstituted 2,3-allenoic acid."]
    if product == "4b":
        notes.append("Product 4b was characterized by X-ray diffraction (CCDC 675815); crystallographic evidence does not verify the machine structure representation.")
    records.append(record(suffix, "substrate_scope_entry", e, ps,
                          [{"step_id": "cyclization_aromatization", "participant_ids": [p["entity_id"] for p in ps],
                            "conditions": [field("temperature", q(60, "°C"), e), field("time", q(1, "h"), e)]}],
                          [field(f"reported_yield_{product}", q(yld, "%"), e, ["product"]), field("yield_measurement_basis", None, e, ["product"])],
                          notes,
                          ["Absolute quantities, atmosphere, workup, purification, yield basis, and complex structures are not reported or verified in the supplied main text.", "No supporting-information file or CIF is supplied or explicitly associated."]))


# Scheme 4 proposed mechanism.
e = ev(2, 3)
records.append(record(
    "scheme4_proposed_mechanism", "mechanism", e,
    [
        participant("intermediate_i", "unspecified_agent", "1,3,4-trienyl palladium species I", e),
        participant("allenoic_acid2", "reactant", "generic 2,3-allenoic acid 2", e),
        participant("intermediate_iii", "unspecified_agent", "palladabicyclic intermediate III", e),
        participant("intermediate_iv", "unspecified_agent", "seven-membered palladacycle IV", e),
        participant("product3", "product", "tricyclic product 3", e),
        participant("product4", "product", "aromatized product 4 when R3 = H", e),
        participant("pd0", "catalyst", "Pd(0)", e),
    ],
    [
        {"step_id": "trans_oxypalladation", "participant_ids": ["intermediate_i", "allenoic_acid2", "intermediate_iii"], "conditions": [field("operation", "proposed trans-oxypalladation with MeOH loss", e)]},
        {"step_id": "carbopalladation", "participant_ids": ["intermediate_iii", "intermediate_iv"], "conditions": [field("operation", "proposed regioselective intramolecular carbopalladation", e)]},
        {"step_id": "reductive_elimination", "participant_ids": ["intermediate_iv", "product3", "pd0"], "conditions": [field("operation", "proposed reductive elimination", e)]},
        {"step_id": "aromatization", "participant_ids": ["product3", "product4"], "conditions": [field("operation", "proposed further aromatization when R3 = H", e)]},
    ],
    [],
    ["Scheme 4 is explicitly presented as a possible mechanism and is not a set of independently executed experiments."],
    ["Generic substituents, organopalladium connectivities, and the mechanistic sequence remain unverified."],
))


# Exact page coverage and task state.
page1_ids = table1_ids + scope_ids + [
    f"{DOC}:scheme1_prior_aryl_alkenyl_halide_allenoic_acid",
    f"{DOC}:scheme1_expected_product_ii_concept",
]
page2_ids = table1_ids + scope_ids + [
    f"{DOC}:scheme2_prepare_alcohol_5",
    f"{DOC}:scheme2_kinetic_resolution_5_6",
    f"{DOC}:scheme2_mitsunobu_r7",
    f"{DOC}:scheme2_r7_to_r1h",
    f"{DOC}:scheme2_cyclization_r1h_to_r3l",
] + scheme3_ids + [f"{DOC}:scheme4_proposed_mechanism"]
page3_ids = [
    f"{DOC}:optimized_3a_table1_entry4_table2_entry1",
    f"{DOC}:scheme2_prepare_alcohol_5",
    f"{DOC}:scheme2_kinetic_resolution_5_6",
    f"{DOC}:scheme2_mitsunobu_r7",
    f"{DOC}:scheme2_r7_to_r1h",
    f"{DOC}:scheme2_cyclization_r1h_to_r3l",
] + scheme3_ids + [f"{DOC}:scheme4_proposed_mechanism"]
page4_ids = [f"{DOC}:optimized_3a_table1_entry4_table2_entry1", f"{DOC}:scheme3_2g_to_4b"]

coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1,
            "state": "attempted",
            "regions": [
                {"region": "right-column Scheme 1 and Figure 1", "finding": "Scheme 1 upper arrow is cited prior work; lower path is the authors' unobserved conceptual target. Figure 1 is ORTEP characterization of 3a, not another reaction.", "evidence_ids": ev(1)},
                {"region": "left-column preliminary-result and catalyst/solvent-screen prose", "finding": "Narrative evidence for Table 1 entries 1-12; the 1a/2a preliminary condition is Table 1 entry 1 and is not duplicated.", "evidence_ids": ev(1)},
                {"region": "lower-right Table 2 scope introduction", "finding": "Narrative classifies Table 2 substrate types and cross-references entries; row-level structures and yields are on page 2.", "evidence_ids": ev(1)},
            ],
            "record_ids": list(dict.fromkeys(page1_ids)),
            "unresolved": ["Supporting Information is stated to be available online but was not supplied or explicitly associated.", "Generic Scheme 1 structures and complex 3a connectivity remain machine-unverified."],
        },
        {
            "page": 2,
            "state": "attempted",
            "regions": [
                {"region": "upper-left Table 1 and footnotes", "finding": "All 12 independent optimization rows extracted; NMR and parenthesized isolated yields remain separate, and trace is qualitative.", "evidence_ids": ev(2)},
                {"region": "upper-right Table 2 and footnotes", "finding": "All 11 scope rows inventoried. Entry 1 is merged with identical Table 1 entry 4 and the page-3 detailed 3a preparation; entries 2-11 remain independent.", "evidence_ids": ev(2)},
                {"region": "lower-left scope/chiral/aromatization prose", "finding": "Substrate-class narrative, the R-(+)-1h to R-(-)-3l result, and the two Scheme 3 aromatization cases were extracted or linked to page 3.", "evidence_ids": ev(2)},
                {"region": "lower-center Figure 2 and mechanism prose", "finding": "Figure 2 is ORTEP characterization of 4b; mechanism prose is represented once as proposed Scheme 4, not as executed steps.", "evidence_ids": ev(2)},
            ],
            "record_ids": list(dict.fromkeys(page2_ids)),
            "unresolved": ["Table 2 compound-specific reactant labels and complex connectivities are not fully given in text and remain unverified.", "Scheme 3 yield basis and operational details are unstated.", "No SI or CIF was supplied or associated."],
        },
        {
            "page": 3,
            "state": "attempted",
            "regions": [
                {"region": "upper-left Scheme 2", "finding": "Four substrate-synthesis transformations and the chiral cyclization were split by executed arrow; omitted SI procedures remain missing.", "evidence_ids": ev(3)},
                {"region": "middle-left Scheme 3", "finding": "Two independent 4-monosubstituted-allenoic-acid reactions extracted: 2f to 4a (69%) and 2g to 4b (59%).", "evidence_ids": ev(3)},
                {"region": "lower-left Scheme 4", "finding": "Possible palladium mechanism classified as mechanism, not as reported stepwise experiments.", "evidence_ids": ev(3)},
                {"region": "upper-right Experimental Section", "finding": "Exact 3a preparation merged into the optimized Table 1 entry 4/Table 2 entry 1 record, including quantities, operations, product mass, and 87% isolated yield.", "evidence_ids": ev(3)},
            ],
            "record_ids": list(dict.fromkeys(page3_ids)),
            "unresolved": ["Scheme 2 explicitly defers experimental details to unavailable Supporting Information.", "Most Scheme 2/3 structures and stereochemical assignments remain machine-unverified."],
        },
        {
            "page": 4,
            "state": "attempted",
            "regions": [
                {"region": "both columns reference list", "finding": "References 3-13 are citations, not present-paper reaction experiments.", "evidence_ids": ev(4)},
                {"region": "right-column notes 8 and 10", "finding": "Crystal data and CCDC identifiers for 3a and 4b were linked as characterization evidence; no new reaction record was created.", "evidence_ids": ev(4)},
            ],
            "record_ids": page4_ids,
            "unresolved": ["CCDC 675814 and 675815 files were not supplied; crystallographic notes do not verify machine structures.", "Cited publications were not supplied as associated sources and were not mined for procedures."],
        },
    ],
}

OUT.parent.mkdir(parents=True, exist_ok=True)
COVERAGE.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
COVERAGE.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

tasks = json.loads(TASKS.read_text())
for task in tasks:
    if task["document_id"] == DOC and task["task_id"] in {f"{DOC}:page{i}:text" for i in range(1, 5)}:
        task["state"] = "attempted"
TASKS.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"records": len(records), "coverage_pages": [p["page"] for p in coverage["pages"]]}, ensure_ascii=False))
