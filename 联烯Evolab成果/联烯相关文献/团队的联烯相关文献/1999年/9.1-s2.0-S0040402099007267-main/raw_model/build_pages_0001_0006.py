#!/usr/bin/env python3
"""Build source-derived machine records for original PDF pages 1-6."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "runs/current"
RAW = OUT / "raw_model/records_pages_0001_0006.json"
COVERAGE = OUT / "coverage/pages_0001_0006.json"
TASKS = OUT / "tasks.json"
DOC = "doc_13430d7f78131b09"


def fact(value, evidence):
    return {
        "value": value,
        "evidence_ids": list(evidence) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def evidence(pages):
    values = []
    for page in pages:
        values.extend([f"{DOC}:page{page}:image", f"{DOC}:page{page}:text"])
    return values


def participant(spec, ev):
    amounts = [
        {"name": name, "fact": fact(value, ev)}
        for name, value in spec.get("amounts", [])
    ]
    return {
        "entity_id": spec["id"],
        "role": spec["role"],
        "label": fact(spec.get("label"), ev),
        "name": fact(spec.get("name"), ev),
        "smiles": fact(None, []),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": amounts,
    }


def make_record(
    rid,
    kind,
    pages,
    participants,
    conditions=(),
    outcomes=(),
    notes=(),
    unresolved=(),
    steps=None,
):
    ev = evidence(pages)
    parts = [participant(p, ev) for p in participants]
    if steps is None:
        step_rows = [{
            "step_id": "step1",
            "participant_ids": [p["entity_id"] for p in parts],
            "conditions": [
                {"name": name, "fact": fact(value, ev)} for name, value in conditions
            ],
        }]
    else:
        step_rows = []
        for step_id, participant_ids, step_conditions in steps:
            step_rows.append({
                "step_id": step_id,
                "participant_ids": participant_ids,
                "conditions": [
                    {"name": name, "fact": fact(value, ev)}
                    for name, value in step_conditions
                ],
            })
    return {
        "record_id": f"{DOC}:{rid}",
        "document_id": DOC,
        "source_reaction_id": rid,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": ev,
        "participants": parts,
        "steps": step_rows,
        "outcomes": [
            {"name": name, "fact": fact(value, ev)} for name, value in outcomes
        ],
        "notes": [fact(note, ev) for note in notes],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": [
                "No supporting-information file is supplied or explicitly associated.",
                "Participant structures are not machine-certified; SMILES remain null.",
                *unresolved,
            ],
        },
    }


def chemical(label, name, role, entity_id, amounts=()):
    return {
        "id": entity_id,
        "role": role,
        "label": label,
        "name": name,
        "amounts": list(amounts),
    }


records = []

# Page 1: explicitly attributed prior Pd/Ag chemistry.
records.append(make_record(
    "page1_eq1_prior_pd_ag_cyclization",
    "literature_example",
    [1],
    [
        chemical(None, "generic 1,2-allenic carboxylic acid", "reactant", "allene_acid"),
        chemical("R'X", "generic organic halide", "reactant", "organic_halide"),
        chemical(None, "Pd(0)", "catalyst", "pd0"),
        chemical(None, "Ag+", "catalyst", "silver_cocatalyst"),
        chemical(None, "acetonitrile", "solvent", "ch3cn"),
        chemical(None, "generic beta-substituted butenolide", "product", "butenolide"),
    ],
    outcomes=[("reported_result", "generic butenolide formation; no local yield")],
    notes=["Equation 1 is attributed by the authors to their prior reference 2 methodology."],
    unresolved=["Generic R/R' groups, reagent identity, charge, time, temperature and yield are not specified on page 1."],
))

# Page 2: retrosynthetic scheme, prior comparison, and Scheme 2 lactonizations.
records.append(make_record(
    "page2_scheme1_generic_coupling",
    "general_scheme",
    [2],
    [
        chemical(None, "generic beta-halobutenolide", "reactant", "halobutenolide"),
        chemical(None, "generic coupling partner", "reactant", "coupling_partner"),
        chemical(None, "generic beta-substituted butenolide", "product", "substituted_butenolide"),
    ],
    conditions=[("transformation", "coupling")],
    notes=["Scheme 1 is a retrosynthetic/general product-space relationship, not an individual experiment."],
    unresolved=["R, R', R'', X and operating conditions are generic or unstated."],
))
records.append(make_record(
    "page2_prior_gill_idvis_2a_42pct",
    "literature_example",
    [2],
    [
        chemical("1a", "2,3-octadienoic acid", "reactant", "substrate_1a"),
        chemical("2a", "beta-iodobutenolide 2a", "product", "product_2a"),
    ],
    outcomes=[("yield", {"number": 42, "unit": "%"})],
    notes=["The 42% result is explicitly attributed to the procedure reported by Gill and Idvis (reference 5)."],
    unresolved=["The cited procedure's local reagent charges, temperature, time, workup and yield basis are absent."],
))

records.append(make_record(
    "scheme2_iodolactonization_1a_to_2a",
    "reported_experiment",
    [2, 6],
    [
        chemical("1a", "2,3-octadienoic acid", "reactant", "substrate_1a", [
            ("mass", {"number": 154, "unit": "mg"}),
            ("amount", {"number": 1.0, "unit": "mmol"}),
        ]),
        chemical(None, "iodine", "reagent", "iodine", [
            ("mass", {"number": 508, "unit": "mg"}),
            ("amount", {"number": 2.2, "unit": "mmol"}),
        ]),
        chemical(None, "potassium carbonate", "reagent", "k2co3", [
            ("mass", {"number": 76, "unit": "mg"}),
            ("amount", {"number": 0.55, "unit": "mmol"}),
        ]),
        chemical(None, "dry THF", "solvent", "thf", [("volume", {"number": 5, "unit": "mL"})]),
        chemical("2a", "4-iodo-5-(n-butyl)-2(5H)-furanone", "product", "product_2a", [
            ("isolated_mass", {"number": 241, "unit": "mg"}),
        ]),
    ],
    outcomes=[
        ("yield", {"number": 91, "unit": "%"}),
        ("yield_measurement_basis", "isolated after flash chromatography"),
    ],
    notes=[
        "Stepwise iodine addition then potassium carbonate addition.",
        "Quenched with aqueous sodium thiosulfate, extracted with diethyl ether (3 x 15 mL), dried over anhydrous MgSO4, solvent removed, and purified by silica-gel flash chromatography with petroleum ether/ethyl acetate 10:1.",
    ],
    unresolved=[
        "Atmosphere and reaction concentration are not stated on pages 2 or 6; characterization continues beyond page 6.",
        "Scheme 3 on page 6 appears to print 1a beneath the 91% iodolactone structure, whereas Scheme 2 and the experimental heading identify the product as 2a.",
    ],
    steps=[
        ("iodine_stage", ["substrate_1a", "iodine", "thf"], [
            ("temperature", {"number": 0, "unit": "°C"}),
            ("time", {"number": 1, "unit": "h"}),
        ]),
        ("base_stage", ["substrate_1a", "iodine", "k2co3", "thf", "product_2a"], [
            ("temperature", {"number": 0, "unit": "°C"}),
            ("time", {"number": 10, "unit": "h"}),
        ]),
    ],
))

for rid, substrate_label, substrate_name, product_label, product_name, yld, pages in [
    ("scheme2_iodolactonization_1b_to_2b", "1b", "2,3-undecadienoic acid", "2b", "gamma-(n-heptyl)-beta-iodobutenolide", 90, [2]),
    ("scheme2_bromolactonization_1a_to_2c", "1a", "2,3-octadienoic acid", "2c", "4-bromo-5-(n-butyl)-2(5H)-furanone", 84, [2, 3]),
    ("scheme2_bromolactonization_1b_to_2d", "1b", "2,3-undecadienoic acid", "2d", "4-bromo-5-(n-heptyl)-2(5H)-furanone", 81, [3]),
]:
    iodo = "iodolactonization" in rid
    parts = [chemical(substrate_label, substrate_name, "reactant", "substrate")]
    if iodo:
        parts += [
            chemical(None, "iodine", "reagent", "iodine"),
            chemical(None, "potassium carbonate", "reagent", "k2co3"),
            chemical(None, "THF", "solvent", "solvent"),
        ]
        conds = [
            ("stage_1", "I2 in THF, 0 °C, 1 h"),
            ("stage_2", "K2CO3 added, 10 h; the stage-2 temperature is not restated for 2b on page 2"),
        ]
    else:
        parts += [
            chemical(None, "NBS", "reagent", "nbs"),
            chemical(None, "potassium carbonate", "reagent", "k2co3", [("equivalents", {"number": 1, "unit": "equiv"})]),
            chemical(None, "water", "solvent", "water"),
        ]
        conds = [("temperature", "rt"), ("time", {"number": 6, "unit": "h"})]
    parts.append(chemical(product_label, product_name, "product", "product"))
    records.append(make_record(
        rid,
        "reported_experiment",
        pages,
        parts,
        conditions=conds,
        outcomes=[("yield", {"number": yld, "unit": "%"}), ("yield_measurement_basis", None)],
        unresolved=["Row-specific charges, atmosphere, concentration, workup, purification and yield basis are not given within pages 1-6."],
    ))

# Page 3 prose-only Sonogashira screen results.
sonogashira_core = [
    chemical("2a", "gamma-(n-butyl)-beta-iodobutenolide", "reactant", "substrate_2a"),
    chemical(None, "phenylacetylene", "reactant", "phenylacetylene"),
    chemical(None, "PdCl2(PPh3)2", "catalyst", "pd_catalyst"),
    chemical(None, "CuI", "catalyst", "cui"),
    chemical("3a", "phenylacetylenyl butenolide 3a", "product", "product_3a"),
]
records.append(make_record(
    "page3_preliminary_et3n_thf_or_ch3cn_42pct",
    "optimization_entry",
    [3],
    sonogashira_core + [
        chemical(None, "triethylamine", "reagent", "et3n"),
        chemical(None, "THF or acetonitrile", "solvent", "solvent_ambiguous"),
    ],
    outcomes=[("yield", "~42%"), ("yield_measurement_basis", None)],
    notes=["The prose groups THF or CH3CN as solvent with Et3N base and reports a poor approximately 42% yield."],
    unresolved=["It is unclear whether ~42% applies to both solvent trials or one of them; time, temperature, charges and basis are unstated."],
))
records.append(make_record(
    "page3_preliminary_et3n_neat_67pct",
    "optimization_entry",
    [3],
    sonogashira_core + [chemical(None, "triethylamine (base and solvent)", "solvent", "et3n")],
    outcomes=[("yield", {"number": 67, "unit": "%"}), ("yield_measurement_basis", None)],
    unresolved=["Time, temperature, charges and yield basis are not stated."],
))
records.append(make_record(
    "page3_preliminary_dmf_66pct",
    "optimization_entry",
    [3],
    sonogashira_core + [chemical(None, "DMF", "solvent", "dmf")],
    outcomes=[("yield", {"number": 66, "unit": "%"}), ("yield_measurement_basis", None)],
    unresolved=["The base identity, time, temperature, charges and yield basis for the DMF trial are not explicitly stated."],
))

# Table 1, one record per row.
table1_rows = [
    (1, "2a", "Ph", "phenylacetylene", "3a", 3, 99),
    (2, "2a", "n-butyl", "1-hexyne", "3b", 2, "<5%"),
    (3, "2a", "n-butyl", "1-hexyne", "3b", 4.3, 93),
    (4, "2a", "HOCH2", "propargyl alcohol", "3c", 2, 95),
    (5, "2a", "TMS", "trimethylsilylacetylene", "3d", 3, 65),
    (6, "2b", "Ph", "phenylacetylene", "3e", 3, 95),
    (7, "2b", "n-butyl", "1-hexyne", "3f", 2.25, 86),
    (8, "2b", "HOCH2", "propargyl alcohol", "3g", 4.3, 79),
    (9, "2b", "TMS", "trimethylsilylacetylene", "3h", 3, 70),
    (10, "2c", "Ph", "phenylacetylene", "3a", 3, 78),
]
for entry, substrate, rprime, alkyne, product, hours, yld in table1_rows:
    pages = [3, 4]
    parts = [
        chemical(substrate, f"beta-halobutenolide {substrate}", "reactant", "halobutenolide"),
        chemical(rprime, alkyne, "reactant", "terminal_alkyne"),
        chemical(None, "PdCl2(PPh3)2", "catalyst", "pd_catalyst"),
        chemical(None, "CuI", "catalyst", "cui"),
        chemical(product, f"coupling product {product}", "product", "product"),
    ]
    conds = [("temperature", "rt"), ("time", {"number": hours, "unit": "h"})]
    notes = []
    unresolved = ["Atmosphere, concentration, workup and purification are not reported in Table 1 on pages 3-4."]
    if entry == 2:
        parts += [
            chemical(None, "triethylamine", "reagent", "base"),
            chemical(None, "THF", "solvent", "solvent"),
        ]
        notes.append("Table 1 footnote b overrides the standard base/solvent with Et3N and THF.")
        basis = "1H NMR using CH2Br2 as internal standard"
    else:
        parts.append(chemical(None, "potassium carbonate", "reagent", "base"))
        conds.append(("molar_ratio_2_alkyne_K2CO3_CuI_PdCl2PPh3_2", "1:1.02:1:0.01:0.01"))
        if entry == 1:
            parts.append(chemical(None, "acetonitrile", "solvent", "solvent"))
            basis = "isolated"
        else:
            basis = None
            unresolved.append("The row-specific solvent and yield basis are not explicitly stated in Table 1 within pages 1-6.")
    kind = "optimization_entry" if entry <= 3 else "substrate_scope_entry"
    records.append(make_record(
        f"table1_entry_{entry:02d}",
        kind,
        pages,
        parts,
        conditions=conds,
        outcomes=[
            ("yield", {"number": yld, "unit": "%"} if isinstance(yld, (int, float)) else yld),
            ("yield_measurement_basis", basis),
        ],
        notes=notes,
        unresolved=unresolved,
    ))

# Page 4 prior failed comparison.
records.append(make_record(
    "page4_eq2_prior_pd_ag_alkynyl_halide_failure",
    "literature_example",
    [4],
    [
        chemical("1a", "2,3-octadienoic acid", "reactant", "substrate_1a"),
        chemical("X = Br or I", "1-phenylethynyl halide", "reactant", "alkynyl_halide"),
        chemical(None, "Pd(0)", "catalyst", "pd0"),
        chemical(None, "Ag+", "catalyst", "ag"),
        chemical(None, "acetonitrile", "solvent", "ch3cn"),
        chemical("3a", "expected phenyacetylenyl butenolide 3a", "product", "expected_product"),
    ],
    outcomes=[("qualitative_result", "corresponding butenolide was not obtained in decent yield")],
    notes=["Equation 2 explicitly invokes the reaction conditions described in prior reference 2."],
    unresolved=["Separate Br/I outcomes, numerical yields, charges, time and temperature are not reported."],
))

# Alkylzinc addition-order comparison and successful equation 3.
records.append(make_record(
    "page4_alkylzinc_wrong_addition_order_no_coupling",
    "optimization_entry",
    [4],
    [
        chemical(None, "beta-iodobutenolide (identity not explicit in the failure sentence)", "reactant", "iodobutenolide"),
        chemical(None, "n-butylzinc bromide", "reactant", "nbuznbr"),
        chemical(None, "Pd catalyst (identity not repeated in the failure sentence)", "catalyst", "pd_catalyst"),
        chemical(None, "THF", "solvent", "thf"),
    ],
    conditions=[("addition_order", "solution of beta-iodobutenolide and Pd catalyst in THF added to n-butylzinc bromide")],
    outcomes=[("qualitative_result", "no cross-coupling product formed"), ("yield", None)],
    unresolved=["Substrate label, catalyst identity, charge, time, temperature and detection limit are unstated in the failure sentence."],
))
records.append(make_record(
    "eq3_2b_nbutylzinc_to_5a",
    "reported_experiment",
    [4, 5],
    [
        chemical(None, "n-BuLi in hexanes", "reagent", "nbuli"),
        chemical(None, "ZnBr2 in THF", "reagent", "znbr2"),
        chemical(None, "n-butylzinc bromide (prepared in situ)", "reactant", "nbuznbr"),
        chemical("2b", "gamma-(n-heptyl)-beta-iodobutenolide", "reactant", "substrate_2b"),
        chemical(None, "Pd(PPh3)4", "catalyst", "pd_catalyst"),
        chemical(None, "THF-hexanes", "solvent", "solvent"),
        chemical("5a", "4-(n-butyl)-5-(n-heptyl)-2(5H)-furanone", "product", "product_5a"),
    ],
    conditions=[("addition_order", "n-butylzinc bromide solution added to the solution of Pd catalyst and 2b")],
    outcomes=[("yield", {"number": 87, "unit": "%"}), ("yield_measurement_basis", None)],
    notes=["n-Butylzinc bromide was prepared in situ from commercial n-BuLi in hexanes and ZnBr2 in THF."],
    unresolved=["Charges, time, temperature, workup, purification and yield basis are not provided on pages 4-5."],
))

# Page 5 Table 2.
table2_rows = [
    (1, "2b", "phenyl", None, 2, "h", "4a", 93),
    (2, "2b", "p-methylphenyl", None, 8, "h", "4b", 83),
    (3, "2a", "naphthyl", None, 40, "min", "4c", 70),
    (4, "2b", "1(E)-hexenyl", "DMF", 50, "min", "4d", 77),
    (5, "2a", "vinyl", None, 16, "h", "4e", "<5%"),
    (6, "2a", "vinyl", "DMF", 10, "min", "4e", 92),
    (7, "2b", "vinyl", "DMF", 10, "h", "4f", 82),
    (8, "2c", "vinyl", "DMF", 10, "h", "4e", 78),
]
for entry, substrate, org_group, additive, number, unit, product, yld in table2_rows:
    reagent_name = {
        "phenyl": "phenylzinc bromide",
        "p-methylphenyl": "p-methylphenylzinc bromide",
        "naphthyl": "naphthylzinc bromide",
        "1(E)-hexenyl": "(E)-1-hexenylzinc bromide",
        "vinyl": "vinylzinc bromide",
    }[org_group]
    parts = [
        chemical(substrate, f"beta-halobutenolide {substrate} as printed in Table 2", "reactant", "halobutenolide"),
        chemical(org_group, reagent_name, "reactant", "organozinc"),
        chemical(None, "Pd(PPh3)4", "catalyst", "pd_catalyst"),
        chemical(None, "THF", "solvent", "thf"),
        chemical(product, f"coupling product {product}", "product", "product"),
    ]
    if additive:
        parts.append(chemical(None, additive, "solvent", "dmf_additive"))
    ratio = "3.3:1:0.05" if org_group == "vinyl" else "2.9:1:0.05"
    kind = "optimization_entry" if entry in (5, 6) else "substrate_scope_entry"
    unresolved = [
        "Yield basis, atmosphere, charge, concentration, workup and purification are not stated in Table 2.",
    ]
    if entry == 1:
        unresolved.append("Table 2 visibly prints substrate 2b for product 4a; the product structure/name is not independently resolved within pages 1-6.")
    if entry == 5:
        unresolved.append("The meaning of superscript b on the <5% result is not defined on page 5.")
    records.append(make_record(
        f"table2_entry_{entry:02d}",
        kind,
        [4, 5],
        parts,
        conditions=[
            ("temperature", "rt"),
            ("time", {"number": number, "unit": unit}),
            ("molar_ratio_organozinc_2_PdPPh3_4", ratio),
        ],
        outcomes=[
            ("yield", {"number": yld, "unit": "%"} if isinstance(yld, (int, float)) else yld),
            ("yield_measurement_basis", None),
        ],
        notes=["Aromatic zinc reagents were described as prepared by ZnBr2 transmetalation of aromatic lithiums; vinylzinc bromide from vinylmagnesium bromide and ZnBr2; (E)-1-hexenylzinc bromide from the iodide, n-BuLi and ZnBr2."],
        unresolved=unresolved,
    ))

# Page 5 prose / page 6 Scheme 3 methyl coupling.
records.append(make_record(
    "scheme3_2a_methylzinc_to_5b",
    "reported_experiment",
    [5, 6],
    [
        chemical("2a", "gamma-(n-butyl)-beta-iodobutenolide", "reactant", "substrate_2a"),
        chemical(None, "methylzinc bromide", "reactant", "meznbr"),
        chemical(None, "Pd(PPh3)4", "catalyst", "pd_catalyst"),
        chemical(None, "xylenes-THF-HMPA", "solvent", "solvent"),
        chemical("5b in prose; 3a printed below Scheme 3 structure", "gamma-(n-butyl)-beta-methylbutenolide", "product", "product_5b"),
    ],
    outcomes=[("yield", {"number": 92, "unit": "%"}), ("yield_measurement_basis", None)],
    notes=["Page 5 states that HMPA is crucial because the reaction was heterogeneous and sluggish before its addition."],
    unresolved=[
        "The page-5 prose calls the product 5b, whereas Scheme 3 on page 6 visibly prints 3a below the methylbutenolide structure.",
        "Charges, time, temperature, atmosphere, workup, purification and yield basis are not supplied on pages 5-6.",
    ],
))

# Page 6 formal-synthesis stages not already represented.
records.append(make_record(
    "scheme3_propargyl_bromide_to_allene_79pct",
    "reported_experiment",
    [6],
    [
        chemical(None, "n-butylmagnesium bromide", "reactant", "nbu_mgbr"),
        chemical(None, "propargyl bromide", "reactant", "propargyl_bromide"),
        chemical(None, "ether", "solvent", "ether"),
        chemical(None, "n-butyl-substituted 1,2-allene shown in Scheme 3", "product", "allene_product"),
    ],
    conditions=[("temperature", {"number": -40, "unit": "°C"})],
    outcomes=[("yield", {"number": 79, "unit": "%"}), ("yield_measurement_basis", None)],
    unresolved=["Time, charges, atmosphere, workup, purification, exact product name and yield basis are not stated."],
))
records.append(make_record(
    "scheme3_allene_carboxylation_to_1a_47pct",
    "literature_example",
    [6],
    [
        chemical(None, "n-butyl-substituted 1,2-allene shown in Scheme 3", "reactant", "allene"),
        chemical(None, "n-BuLi", "reagent", "nbuli"),
        chemical(None, "carbon dioxide", "reagent", "co2"),
        chemical("1a", "2,3-octadienoic acid", "product", "acid_1a"),
    ],
    outcomes=[("yield", {"number": 47, "unit": "%"}), ("yield_measurement_basis", None)],
    notes=["The starting-material paragraph says the allenic acids were prepared according to published procedure 11 via allenic lithiums generated from the corresponding allenes and n-BuLi."],
    unresolved=["Charges, solvent, temperature, time, atmosphere, workup, purification and yield basis are absent."],
))
records.append(make_record(
    "scheme3_known_conversion_5b_to_cis_whisky_lactone",
    "literature_example",
    [5, 6],
    [
        chemical("5b", "gamma-(n-butyl)-beta-methylbutenolide", "reactant", "product_5b"),
        chemical(None, "cis-whisky lactone", "product", "whisky_lactone"),
    ],
    outcomes=[("yield", None)],
    notes=["The conversion is assigned to known procedures in references 10c-d; no local experimental arrow conditions or yield are supplied."],
    unresolved=["Reagents, conditions, steps, workup, purification, stereochemical verification and yield are not reported locally."],
))


coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1,
            "state": "attempted",
            "regions": [
                {
                    "region": "lower-page Introduction and Equation (1)",
                    "finding": "Visually inspected prior Pd(0)/Ag+-cocatalyzed generic cyclization; classified as cited literature, not a current-paper experiment.",
                    "evidence_ids": [f"{DOC}:page1:image", f"{DOC}:page1:text"],
                },
                {
                    "region": "title, abstract, and introductory prose",
                    "finding": "Bibliographic/summary content and qualitative limitations; no additional row-level experiment was fabricated.",
                    "evidence_ids": [f"{DOC}:page1:image", f"{DOC}:page1:text"],
                },
            ],
            "record_ids": [f"{DOC}:page1_eq1_prior_pd_ag_cyclization"],
            "unresolved": ["Equation (1) is generic and omits specific substrates, full conditions and yield."],
        },
        {
            "page": 2,
            "state": "attempted",
            "regions": [
                {
                    "region": "Scheme 1, upper-middle page",
                    "finding": "Generic retrosynthetic coupling relationship; retained as a general scheme.",
                    "evidence_ids": [f"{DOC}:page2:image", f"{DOC}:page2:text"],
                },
                {
                    "region": "Results prose above Scheme 2",
                    "finding": "Cited Gill/Idvis 42% comparison plus current stepwise 2a/2b iodolactonization results.",
                    "evidence_ids": [f"{DOC}:page2:image", f"{DOC}:page2:text"],
                },
                {
                    "region": "Scheme 2, lower page",
                    "finding": "Two iodolactonization rows and the visible 1a-to-2c bromolactonization row; rows separated into experiments.",
                    "evidence_ids": [f"{DOC}:page2:image", f"{DOC}:page2:text"],
                },
            ],
            "record_ids": [
                f"{DOC}:page2_scheme1_generic_coupling",
                f"{DOC}:page2_prior_gill_idvis_2a_42pct",
                f"{DOC}:scheme2_iodolactonization_1a_to_2a",
                f"{DOC}:scheme2_iodolactonization_1b_to_2b",
                f"{DOC}:scheme2_bromolactonization_1a_to_2c",
            ],
            "unresolved": ["Scheme 2 does not supply row-specific charges, workups or yield bases except where page 6 later expands 2a."],
        },
        {
            "page": 3,
            "state": "attempted",
            "regions": [
                {
                    "region": "top paragraph continuing Scheme 2",
                    "finding": "Bromolactonizations to 2c (84%) and 2d (81%) at room temperature for 6 h.",
                    "evidence_ids": [f"{DOC}:page3:image", f"{DOC}:page3:text"],
                },
                {
                    "region": "Sonogashira screening prose above Table 1",
                    "finding": "Three prose-only screening outcomes (~42%, 67%, 66%) plus the 99% condition corresponding to Table 1 entry 1.",
                    "evidence_ids": [f"{DOC}:page3:image", f"{DOC}:page3:text"],
                },
                {
                    "region": "Table 1 and footnotes",
                    "finding": "All ten rows and footnote overrides visually read; each row retained separately, including the <5% NMR result.",
                    "evidence_ids": [f"{DOC}:page3:image", f"{DOC}:page3:text"],
                },
            ],
            "record_ids": [
                f"{DOC}:scheme2_bromolactonization_1a_to_2c",
                f"{DOC}:scheme2_bromolactonization_1b_to_2d",
                f"{DOC}:page3_preliminary_et3n_thf_or_ch3cn_42pct",
                f"{DOC}:page3_preliminary_et3n_neat_67pct",
                f"{DOC}:page3_preliminary_dmf_66pct",
                *[f"{DOC}:table1_entry_{i:02d}" for i in range(1, 11)],
            ],
            "unresolved": [
                "The ~42% prose result does not resolve whether it applies to both THF and CH3CN trials.",
                "Most Table 1 row-specific solvents and yield bases are not explicit within pages 1-6.",
            ],
        },
        {
            "page": 4,
            "state": "attempted",
            "regions": [
                {
                    "region": "Table 1 continuation prose and Equation (2)",
                    "finding": "Scope commentary and a prior-reference Pd/Ag failure with 1-alkynyl halides; Equation (2) classified as literature example.",
                    "evidence_ids": [f"{DOC}:page4:image", f"{DOC}:page4:text"],
                },
                {
                    "region": "aryl/alkenylzinc discussion",
                    "finding": "Reagent-generation context, DMF effect, and links to Table 2 rows; no duplicate records created.",
                    "evidence_ids": [f"{DOC}:page4:image", f"{DOC}:page4:text"],
                },
                {
                    "region": "bottom alkylzinc addition-order comparison",
                    "finding": "Wrong addition order gave no coupling; reverse order gave 5a in 87%, continued as Equation (3) on page 5.",
                    "evidence_ids": [f"{DOC}:page4:image", f"{DOC}:page4:text"],
                },
            ],
            "record_ids": [
                *[f"{DOC}:table1_entry_{i:02d}" for i in range(1, 11)],
                f"{DOC}:page4_eq2_prior_pd_ag_alkynyl_halide_failure",
                f"{DOC}:page4_alkylzinc_wrong_addition_order_no_coupling",
                f"{DOC}:eq3_2b_nbutylzinc_to_5a",
                *[f"{DOC}:table2_entry_{i:02d}" for i in range(1, 9)],
            ],
            "unresolved": ["The no-coupling sentence does not repeat the exact beta-iodobutenolide label or Pd catalyst identity."],
        },
        {
            "page": 5,
            "state": "attempted",
            "regions": [
                {
                    "region": "Equation (3) and adjacent prose",
                    "finding": "2b/n-BuZnBr coupling to 5a (87%) and 2a/MeZnBr coupling to 5b (92%).",
                    "evidence_ids": [f"{DOC}:page5:image", f"{DOC}:page5:text"],
                },
                {
                    "region": "Table 2 and footnote",
                    "finding": "All eight aryl/alkenylzinc rows visually read and split row-wise, including the <5% no-DMF result and DMF-enabled comparisons.",
                    "evidence_ids": [f"{DOC}:page5:image", f"{DOC}:page5:text"],
                },
                {
                    "region": "conclusion prose",
                    "finding": "Summary only; no new experiment record.",
                    "evidence_ids": [f"{DOC}:page5:image", f"{DOC}:page5:text"],
                },
            ],
            "record_ids": [
                f"{DOC}:eq3_2b_nbutylzinc_to_5a",
                f"{DOC}:scheme3_2a_methylzinc_to_5b",
                *[f"{DOC}:table2_entry_{i:02d}" for i in range(1, 9)],
                f"{DOC}:scheme3_known_conversion_5b_to_cis_whisky_lactone",
            ],
            "unresolved": [
                "Table 2 visibly prints 2b in entry 1 although the product label is 4a; the structure relationship is not resolved within pages 1-6.",
                "Table 2 does not define superscript b on entry 5 or state most yield bases.",
            ],
        },
        {
            "page": 6,
            "state": "attempted",
            "regions": [
                {
                    "region": "Scheme 3, upper page",
                    "finding": "Formal-synthesis sequence: 79% allene preparation, cited 47% carboxylation, the already-recorded 91% 2a lactonization, the already-recorded 92% methyl coupling, and a cited conversion to cis-whisky lactone.",
                    "evidence_ids": [f"{DOC}:page6:image", f"{DOC}:page6:text"],
                },
                {
                    "region": "Starting Materials paragraph",
                    "finding": "Cited/incomplete preparation routes for allenic acids, methylzinc halide, methylmagnesium iodide, trimethylsilylacetylene, and (E)-1-iodo-1-hexene; retained as contextual missing-detail notes rather than fabricated complete runs.",
                    "evidence_ids": [f"{DOC}:page6:image", f"{DOC}:page6:text"],
                },
                {
                    "region": "Iodolactonization procedure, lower page",
                    "finding": "Detailed 2a charges, two temperature/time stages, workup, chromatography and isolated mass merged into the Scheme 2 2a record.",
                    "evidence_ids": [f"{DOC}:page6:image", f"{DOC}:page6:text"],
                },
            ],
            "record_ids": [
                f"{DOC}:scheme3_propargyl_bromide_to_allene_79pct",
                f"{DOC}:scheme3_allene_carboxylation_to_1a_47pct",
                f"{DOC}:scheme2_iodolactonization_1a_to_2a",
                f"{DOC}:scheme3_2a_methylzinc_to_5b",
                f"{DOC}:scheme3_known_conversion_5b_to_cis_whisky_lactone",
            ],
            "unresolved": [
                "Scheme 3 appears to label the 91% iodolactone 1a, while Scheme 2 and the experimental heading identify it as 2a.",
                "Page-5 prose names the methyl-coupling product 5b, while Scheme 3 visibly labels it 3a.",
                "The detailed 2a characterization continues after page 6 and is outside the claimed visual coverage.",
                "Cited starting-material preparations lack local complete experimental details; no SI association is inferred.",
            ],
        },
    ],
}


RAW.parent.mkdir(parents=True, exist_ok=True)
COVERAGE.parent.mkdir(parents=True, exist_ok=True)
RAW.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
COVERAGE.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

tasks = json.loads(TASKS.read_text())
target_ids = {f"{DOC}:page{page}:text" for page in range(1, 7)}
for task in tasks:
    if task["task_id"] in target_ids:
        task["state"] = "attempted"
        task["reason"] = "Original page image visually inspected; records and unresolved findings are linked in pages_0001_0006 coverage ledger."
TASKS.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"records": len(records), "coverage_pages": [p["page"] for p in coverage["pages"]]}, ensure_ascii=False))
