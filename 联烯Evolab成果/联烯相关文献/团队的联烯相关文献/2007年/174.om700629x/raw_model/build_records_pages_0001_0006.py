#!/usr/bin/env python3
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / "runs" / "current"
DOC = "doc_d88f44f799f3b8b2"


def ev(page, kind):
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
        item["target_entity_ids"] = list(targets)
    return item


def participant(entity_id, role, label, evidence, name=None, smiles=None, amounts=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence) if name is not None else fact(None, []),
        "smiles": fact(smiles, evidence) if smiles is not None else fact(None, []),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": amounts or [],
    }


def record(rid, kind, evidence, participants, steps, outcomes, notes, unresolved):
    return {
        "record_id": f"{DOC}:{rid}",
        "document_id": DOC,
        "source_reaction_id": rid,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": list(dict.fromkeys(evidence)),
        "participants": participants,
        "steps": steps,
        "outcomes": outcomes,
        "notes": [fact(value, note_ev) for value, note_ev in notes],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": list(unresolved),
        },
    }


def simple_step(step_id, participants, conditions=None):
    return {
        "step_id": step_id,
        "participant_ids": [p["entity_id"] for p in participants],
        "conditions": conditions or [],
    }


records = []

# Page 2, equation 1: conceptual alternatives, not an executed experiment.
e2 = [ev(2, "image"), ev(2, "text")]
p = [
    participant("eq1_allene", "reactant", "H2C=C=CH2", e2, "allene", "C=C=C"),
    participant("eq1_mr", "reactant", "LnM-R", e2, "generic metal-R complex"),
    participant("eq1_allyl_a", "product", "A", e2, "generic transition-metal allyl complex"),
    participant("eq1_vinyl_b", "product", "B", e2, "generic transition-metal vinyl complex"),
]
records.append(record(
    "equation1_generic_allene_insertion", "general_scheme", e2, p,
    [simple_step("conceptual_allene_insertion", p)],
    [field("possible_products", "allyl complex A or vinyl complex B", e2,
           ["eq1_allyl_a", "eq1_vinyl_b"])],
    [("Equation 1 illustrates two possible insertion connectivities and does not report an executed experiment.", e2)],
    ["Ln, M, and R are generic; no experiment-specific quantities, conditions, or yield are supplied."],
))


def add_literature(rid, evidence, metal_label, allene_label, allene_name, allene_smiles,
                   product_label, outcome, note, extra_unresolved=None):
    ps = [
        participant(f"{rid}_metal", "reactant", metal_label, evidence),
        participant(f"{rid}_allene", "reactant", allene_label, evidence, allene_name, allene_smiles),
        participant(f"{rid}_product", "product", product_label, evidence),
    ]
    records.append(record(
        rid, "literature_example", evidence, ps,
        [simple_step("reported_prior_reaction", ps)],
        [field("reported_prior_outcome", outcome, evidence, [f"{rid}_product"])],
        [(note, evidence)],
        ["This is cited prior work, not a present-paper experiment; quantities, conditions, workup, purification, and yield are not supplied on the inspected pages."]
        + (extra_unresolved or []),
    ))


# Explicit rare prior-work examples in page-2 prose.
add_literature(
    "literature_fe_hydride_allene_vinyl", e2,
    "[FeH(H2)(dmpe)2]+", "CH2=C=CH2", "allene", "C=C=C",
    "[Fe(C(CH3)=CH2)(dmpe)2]+", "vinyl complex reported",
    "Attributed to Hills et al., reference 17.",
)
add_literature(
    "literature_zr_pyridyl_allene_mixture", e2,
    "[Cp2Zr(eta2-pyridyl)(THF)]+", "CH2=C=CH2", "allene", "C=C=C",
    "mixture of vinyl and allyl complexes", "vinyl/allyl mixture reported",
    "Attributed to Guram and Jordan, reference 18.",
    ["Individual product structures and their ratio are not given in the inspected-page prose."],
)
add_literature(
    "literature_erker_zr_hf_allene_vinyl", e2,
    "Cp2M(CH2CHCHCH2B(C6F5)3), M = Zr or Hf", "CH2=C=CH2", "allene", "C=C=C",
    "Cp2M(C(=CH2)CH2CH2CHCHCH2B(C6F5)3", "vinyl complexes reported",
    "Attributed to Karl and Erker, reference 19; the source summarizes Zr and Hf congeners together.",
    ["The compact printed formula is retained as a label; connectivity and punctuation require source-paper review."],
)


# Three Ru/CO reactions explicitly described on page 2 as already reported work.
for suffix, allene_label, allene_name, smiles, product_label in [
    ("allene", "CH2=C=CH2", "allene", "C=C=C", "RuCl(eta3-C3H5)(CO)(PPh3)2"),
    ("phenylallene", "CH2=C=CHPh", "phenylallene", "C=C=Cc1ccccc1", "RuCl(eta3-CH2CHCHPh)(CO)(PPh3)2"),
    ("dimethylallene", "CH2=C=CMe2", "1,1-dimethylallene", "C=C=C(C)C", "RuCl(eta3-CH2CHCMe2)(CO)(PPh3)2"),
]:
    add_literature(
        f"literature_ru_co_{suffix}_allyl", e2,
        "RuHCl(CO)(PPh3)3", allene_label, allene_name, smiles,
        product_label, "eta3-allyl complex reported",
        "The page states that this RuHCl(CO)(PPh3)3 reaction had been shown previously (reference 9).",
    )


# Equation 2: present-paper methyl allenoate insertion.
eq2_ev = [ev(1, "image"), ev(1, "text"), ev(2, "image"), ev(2, "text"), ev(3, "image"), ev(3, "text")]
p = [
    participant("eq2_ru_hydride_1", "reactant", "1", eq2_ev, "RuHCl(CO)(PPh3)3"),
    participant("eq2_methyl_allenoate", "reactant", "CH2=C=CHCO2Me", eq2_ev,
                "methyl buta-2,3-dienoate", "C=C=CC(=O)OC"),
    participant("eq2_product_2", "product", "2", eq2_ev,
                "Ru(eta3-CH2CHCHCO2Me)Cl(CO)(PPh3)2"),
]
records.append(record(
    "equation2_ru_methyl_allenoate_allyl_2", "reported_experiment", eq2_ev, p,
    [simple_step("allene_insertion", p)],
    [
        field("reported_product_formation", "allyl complex 2 formed", [ev(1, "text"), ev(3, "text")], ["eq2_product_2"]),
        field("structure_confirmation", "X-ray diffraction", [ev(2, "image"), ev(3, "text")], ["eq2_product_2"]),
    ],
    [
        ("Page 3 reports allylic 1H NMR signals at 5.80 and 2.95-3.19 ppm; 13C signals at 103.5, 67.8, and 60.7 ppm; and 31P doublets at 39.5 and 28.9 ppm.", [ev(3, "text")]),
        ("Tables 1 and 2 contain crystallographic data for 2 and are structural characterization, not separate reactions.", [ev(3, "image")]),
    ],
    ["Pages 1-6 do not provide reaction quantities, solvent, time, temperature, atmosphere, workup, purification, or yield for equation 2.",
     "The organoruthenium product structure is retained as a formula/name; no standard SMILES was assigned."],
))


# Equation 3 contains two present-paper substrate cases.
def add_eq3_case(suffix, r_value, allene_label, allene_name, smiles, product_label, confirmed_by_xray=False):
    evidence = [ev(1, "image"), ev(1, "text"), ev(3, "image"), ev(3, "text"), ev(4, "image"), ev(4, "text")]
    if suffix == "benzyl":
        evidence = [ev(1, "image"), ev(1, "text"), ev(4, "image"), ev(4, "text")]
    ps = [
        participant(f"eq3_{suffix}_os_hydride_3", "reactant", "3", evidence, "OsHCl(CO)(PPh3)3"),
        participant(f"eq3_{suffix}_allene", "reactant", allene_label, evidence, allene_name, smiles),
        participant(f"eq3_{suffix}_product", "product", "4" if suffix == "phenyl" else "5", evidence, product_label),
    ]
    outcomes = [field("reported_product_formation", f"eta3-allyl complex formed (R = {r_value})", evidence,
                      [f"eq3_{suffix}_product"])]
    if confirmed_by_xray:
        outcomes.append(field("structure_confirmation", "X-ray diffraction", [ev(2, "image"), ev(3, "text")],
                              [f"eq3_{suffix}_product"]))
    records.append(record(
        f"equation3_os_{suffix}_allene_allyl", "reported_experiment", evidence, ps,
        [simple_step("allene_insertion", ps)], outcomes,
        [("Equation 3 is a shared arrow for two separately listed R groups; this record represents one substrate case.", [ev(4, "image")])],
        ["Pages 1-6 do not provide complete quantities, time, temperature, atmosphere, workup, purification, or yield for this equation-3 case.",
         "The organo-osmium product structure is retained as a formula/name; no standard SMILES was assigned."],
    ))


add_eq3_case("phenyl", "Ph", "CH2=C=CHPh", "phenylallene", "C=C=Cc1ccccc1",
             "Os(eta3-CH2CHCHPh)Cl(CO)(PPh3)2", True)
add_eq3_case("benzyl", "CH2Ph", "CH2=C=CHCH2Ph", "buta-2,3-dienylbenzene", "C=C=CCc1ccccc1",
             "Os(eta3-CH2CHCHCH2Ph)Cl(CO)(PPh3)2", False)


# Equation 4 is explicitly identified as earlier work (reference 20), split by R value.
eq4_ev = [ev(1, "image"), ev(1, "text"), ev(3, "image"), ev(3, "text"), ev(4, "image"), ev(4, "text")]
for label, r_value, allene_label, name, smiles, product_no in [
    ("tert_butyl", "CMe3", "CH2=C=CHCMe3", "4,4-dimethyl-1,2-pentadiene", "C=C=CC(C)(C)C", "7"),
    ("phenyl", "Ph", "CH2=C=CHPh", "phenylallene", "C=C=Cc1ccccc1", "8"),
    ("ethoxycarbonyl", "CO2Et", "CH2=C=CHCO2Et", "ethyl buta-2,3-dienoate", "C=C=CC(=O)OCC", "9"),
]:
    rid = f"literature_equation4_os_{label}_vinyl"
    ps = [
        participant(f"{rid}_os_hydride", "reactant", "6", eq4_ev, "OsHCl(PPh3)3"),
        participant(f"{rid}_allene", "reactant", allene_label, eq4_ev, name, smiles),
        participant(f"{rid}_product", "product", product_no, eq4_ev,
                    f"OsCl(C(CH3)=CHR)(CH2=C=CHR)(PPh3)2, R = {r_value}"),
    ]
    records.append(record(
        rid, "literature_example", eq4_ev, ps,
        [simple_step("reported_prior_insertion", ps)],
        [field("reported_prior_outcome", f"vinyl complex {product_no} formed", eq4_ev, [f"{rid}_product"])],
        [("The authors state that equation 4 had been shown previously in reference 20.", [ev(4, "text")])],
        ["This is cited prior work, not a present-paper experiment; pages 1-6 omit quantities, conditions, workup, purification, and yield.",
         "The organo-osmium product structure is retained as a formula/name; no standard SMILES was assigned."],
    ))


# Equation 5: present-paper Ru/PPh3 vinyl complex 11.
eq5_ev = [ev(1, "image"), ev(1, "text"), ev(4, "image"), ev(4, "text"), ev(5, "image"), ev(5, "text")]
p = [
    participant("eq5_ru_hydride_10", "reactant", "10", eq5_ev, "RuHCl(PPh3)3"),
    participant("eq5_allene", "reactant", "CH2=C=CHCMe3", eq5_ev,
                "4,4-dimethyl-1,2-pentadiene", "C=C=CC(C)(C)C"),
    participant("eq5_product_11", "product", "11", eq5_ev,
                "Ru(C(CH3)=CHCMe3)(eta2-1,2-CH2=C=CHCMe3)Cl(PPh3)2"),
]
records.append(record(
    "equation5_ru_tertbutyl_allene_vinyl_11", "reported_experiment", eq5_ev, p,
    [simple_step("vinyl_complex_formation", p)],
    [field("reported_product_formation", "vinyl complex 11 isolated", [ev(4, "text")], ["eq5_product_11"])],
    [
        ("Page 4 assigns a beta-agostic interaction from an unusually upfield methyl signal; page 5 continues the comparison with complex 7.", [ev(4, "text"), ev(5, "text")]),
        ("Reported NMR features include 31P at 22.0 ppm, =CH2 at 0.30 ppm, =CH at 4.53 and 5.85 ppm, and an agostic methyl signal at 0.13 ppm.", [ev(4, "text")]),
    ],
    ["Pages 1-6 do not provide reaction quantities, solvent, time, temperature, atmosphere, workup, purification, or yield for equation 5.",
     "The equation does not state the allene stoichiometry; it was not inferred from the product formula.",
     "The organoruthenium product structure is retained as a formula/name; no standard SMILES was assigned."],
))


# Two distinct unsuccessful present-paper RuHCl(PPh3)3 reactions described on page 4.
def add_failed_ru(label, allene_label, name, smiles):
    evidence = [ev(4, "image"), ev(4, "text")]
    rid = f"ru_hydride_{label}_unseparated_mixture"
    ps = [
        participant(f"{rid}_ru", "reactant", "10", evidence, "RuHCl(PPh3)3"),
        participant(f"{rid}_allene", "reactant", allene_label, evidence, name, smiles),
        participant(f"{rid}_mixture", "product", "unseparated mixture", evidence,
                    "mixture of species not fully characterized"),
    ]
    records.append(record(
        rid, "reported_experiment", evidence, ps,
        [simple_step("attempted_allene_reaction", ps)],
        [field("reaction_outcome", "mixture of species; products could not be separated and fully characterized",
               evidence, [f"{rid}_mixture"])],
        [("This is an explicitly reported unsuccessful/indeterminate present-paper reaction, retained rather than omitted.", evidence)],
        ["No individual product identity, yield, reaction quantities, solvent, time, temperature, atmosphere, workup, or purification is reported on pages 1-6."],
    ))


add_failed_ru("phenylallene", "CH2=C=CHPh", "phenylallene", "C=C=Cc1ccccc1")
add_failed_ru("ethyl_allenoate", "CH2=C=CHCO2Et", "ethyl buta-2,3-dienoate", "C=C=CC(=O)OCC")


# Scheme 1 and Figures 3-4: two computational model systems, not wet experiments.
mech_ev = [ev(5, "image"), ev(5, "text"), ev(6, "image"), ev(6, "text")]

p = [
    participant("pc1_precursor", "reactant", "PC1", mech_ev, "OsHCl(eta2-allene)(PH3)3"),
    participant("pc1_vinyl_product", "product", "PR1-vinyl", mech_ev),
    participant("pc1_allyl_product", "product", "PR1-allyl", mech_ev),
]
records.append(record(
    "scheme1_pc1_phosphine_computational_pathways", "mechanism", mech_ev, p,
    [
        {"step_id": "pc1_vinyl_pathway", "participant_ids": ["pc1_precursor", "pc1_vinyl_product"], "conditions": []},
        {"step_id": "pc1_allyl_pathway", "participant_ids": ["pc1_precursor", "pc1_allyl_product"], "conditions": []},
    ],
    [field("calculated_preferred_pathway", "vinyl pathway kinetically favored", [ev(5, "text"), ev(6, "image")], ["pc1_vinyl_product"])],
    [
        ("Figure 3 relative free energies (electronic energies in parentheses), kcal/mol: PC1-allyl 0.0 (0.0), PC1-vinyl 2.2 (0.9), TS1-vinyl 15.5 (15.7), TS1-allyl 18.0 (17.8), PR1-vinyl -1.1 (-4.0), and PR1-allyl 2.6 (-0.5).", [ev(6, "image")]),
        ("PH3 is the model phosphine ligand in the calculation; Scheme 1 is a mechanistic model, not an executed synthesis.", [ev(5, "image"), ev(6, "text")]),
    ],
    ["Transition-state and organometallic intermediate structures were not converted to SMILES.",
     "The energy unit kcal/mol is preserved in notes because it is outside the reaction-quantity schema's supported units."],
))

p = [
    participant("pc2_precursor", "reactant", "PC2", mech_ev, "OsHCl(eta2-allene)(CO)(PH3)2"),
    participant("pc2_vinyl_product", "product", "PR2-vinyl", mech_ev),
    participant("pc2_allyl_product", "product", "PR2-allyl", mech_ev),
]
records.append(record(
    "scheme1_pc2_carbonyl_computational_pathways", "mechanism", mech_ev, p,
    [
        {"step_id": "pc2_vinyl_pathway", "participant_ids": ["pc2_precursor", "pc2_vinyl_product"], "conditions": []},
        {"step_id": "pc2_allyl_pathway", "participant_ids": ["pc2_precursor", "pc2_allyl_product"], "conditions": []},
    ],
    [field("calculated_preferred_pathway", "eta3-allyl pathway kinetically and thermodynamically favored",
           [ev(5, "text"), ev(6, "image")], ["pc2_allyl_product"])],
    [
        ("Figure 4 reports PH3-model and ONIOM/PPh3 relative free/electronic energies. Key barriers are TS2-vinyl 8.1 (9.0) and 8.0 (8.3) kcal/mol, and TS2-allyl 7.5 (8.8) and 6.1 (7.5) kcal/mol.", [ev(6, "image")]),
        ("Figure 4 product energies include PR2-vinyl -17.4 (-19.5) and -22.2 (-22.4) kcal/mol, and PR2-allyl -19.8 (-24.0) and -18.7 (-22.2) kcal/mol.", [ev(6, "image")]),
        ("Scheme 1 and Figure 4 are computational models, not executed syntheses.", [ev(5, "image"), ev(6, "image")]),
    ],
    ["Transition-state and organometallic intermediate structures were not converted to SMILES.",
     "The energy unit kcal/mol is preserved in notes because it is outside the reaction-quantity schema's supported units."],
))


records_path = RUN / "raw_model" / "records_pages_0001_0006.json"
records_path.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")


def rid(suffix):
    return f"{DOC}:{suffix}"


page1_ids = [
    rid("equation2_ru_methyl_allenoate_allyl_2"),
    rid("equation3_os_phenyl_allene_allyl"),
    rid("equation3_os_benzyl_allene_allyl"),
    rid("literature_equation4_os_tert_butyl_vinyl"),
    rid("literature_equation4_os_phenyl_vinyl"),
    rid("literature_equation4_os_ethoxycarbonyl_vinyl"),
    rid("equation5_ru_tertbutyl_allene_vinyl_11"),
]
page2_ids = [
    rid("equation1_generic_allene_insertion"),
    rid("literature_fe_hydride_allene_vinyl"),
    rid("literature_zr_pyridyl_allene_mixture"),
    rid("literature_erker_zr_hf_allene_vinyl"),
    rid("literature_ru_co_allene_allyl"),
    rid("literature_ru_co_phenylallene_allyl"),
    rid("literature_ru_co_dimethylallene_allyl"),
    rid("equation2_ru_methyl_allenoate_allyl_2"),
    rid("equation3_os_phenyl_allene_allyl"),
]
page3_ids = [
    rid("equation2_ru_methyl_allenoate_allyl_2"),
    rid("equation3_os_phenyl_allene_allyl"),
    rid("literature_equation4_os_tert_butyl_vinyl"),
    rid("literature_equation4_os_phenyl_vinyl"),
    rid("literature_equation4_os_ethoxycarbonyl_vinyl"),
]
page4_ids = [
    rid("equation3_os_phenyl_allene_allyl"),
    rid("equation3_os_benzyl_allene_allyl"),
    rid("literature_equation4_os_tert_butyl_vinyl"),
    rid("literature_equation4_os_phenyl_vinyl"),
    rid("literature_equation4_os_ethoxycarbonyl_vinyl"),
    rid("equation5_ru_tertbutyl_allene_vinyl_11"),
    rid("ru_hydride_phenylallene_unseparated_mixture"),
    rid("ru_hydride_ethyl_allenoate_unseparated_mixture"),
]
page5_ids = [
    rid("equation5_ru_tertbutyl_allene_vinyl_11"),
    rid("scheme1_pc1_phosphine_computational_pathways"),
    rid("scheme1_pc2_carbonyl_computational_pathways"),
]
page6_ids = [
    rid("scheme1_pc1_phosphine_computational_pathways"),
    rid("scheme1_pc2_carbonyl_computational_pathways"),
]

coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1,
            "state": "attempted",
            "regions": [
                {
                    "region": "title, abstract, and introduction across the original page",
                    "finding": "The abstract summarizes the paper's Ru/Os allyl and vinyl outcomes. These statements were merged as cross-page evidence into the later equation records; no duplicate abstract-only experiment was created. The introduction gives broad cited context but no row-level present-paper experiment or reaction arrow on this page.",
                    "evidence_ids": [ev(1, "image"), ev(1, "text")],
                }
            ],
            "record_ids": page1_ids,
            "unresolved": [
                "Abstract-level statements do not supply quantities, conditions, yields, or complete structures beyond the formulas shown in text.",
                "Broad metal/R lists in the introduction were not expanded into unsupported individual literature experiments.",
            ],
        },
        {
            "page": 2,
            "state": "attempted",
            "regions": [
                {
                    "region": "upper-left equation 1 and adjacent prose",
                    "finding": "Equation 1 is a generic allene-insertion scheme with allyl and vinyl alternatives, not an executed experiment. Three explicit rare prior-work reactions in the prose and three previously reported Ru/CO allene cases were classified as literature examples.",
                    "evidence_ids": [ev(2, "image"), ev(2, "text")],
                },
                {
                    "region": "right-column Figures 1 and 2",
                    "finding": "X-ray structures of present-paper products 2 and 4 were linked to equation 2 and the phenyl case of equation 3; the figures were not counted as separate reactions.",
                    "evidence_ids": [ev(2, "image"), ev(2, "text")],
                },
                {
                    "region": "lower-right present-work context",
                    "finding": "The page introduces the hydride systems and identifies some Ru/CO reactions as previously reported; detailed present-paper equations continue on later pages.",
                    "evidence_ids": [ev(2, "image"), ev(2, "text")],
                },
            ],
            "record_ids": page2_ids,
            "unresolved": [
                "Prior-work prose omits quantities, conditions, yields, and, for the Zr mixture, individual product structures and ratio.",
                "The compact Erker product formula requires review against the cited source before assigning connectivity.",
            ],
        },
        {
            "page": 3,
            "state": "attempted",
            "regions": [
                {
                    "region": "lower-left equation 2 and Results and Discussion text",
                    "finding": "One present-paper insertion of RuHCl(CO)(PPh3)3 with methyl buta-2,3-dienoate was extracted, giving allyl complex 2; NMR and X-ray confirmation were associated with the same record.",
                    "evidence_ids": [ev(3, "image"), ev(3, "text")],
                },
                {
                    "region": "upper Table 1 and right-column Table 2",
                    "finding": "These are crystallographic/refinement and bond-geometry tables for products 2 and 4, not reaction-condition tables; no additional experiment records were created.",
                    "evidence_ids": [ev(3, "image"), ev(3, "text")],
                },
                {
                    "region": "top and lower-right cross-page prose",
                    "finding": "The top completes the citation to prior Os/PPh3 vinyl-complex work; the lower-right introduces the present OsHCl(CO)(PPh3)3 phenylallene case that is drawn as equation 3 on page 4.",
                    "evidence_ids": [ev(3, "image"), ev(3, "text")],
                },
            ],
            "record_ids": page3_ids,
            "unresolved": [
                "Equation 2 on pages 1-6 omits quantities, solvent, time, temperature, atmosphere, workup, purification, and yield.",
                "Crystallographic data establish structure but do not provide a separate synthesis condition.",
            ],
        },
        {
            "page": 4,
            "state": "attempted",
            "regions": [
                {
                    "region": "upper-left equation 3 and adjacent product discussion",
                    "finding": "The shared equation-3 arrow was split into two present-paper substrate cases (R = Ph and CH2Ph), producing allyl complexes 4 and 5. Table 3 is bond geometry for 4 and was not treated as another reaction.",
                    "evidence_ids": [ev(4, "image"), ev(4, "text")],
                },
                {
                    "region": "middle-right equation 4",
                    "finding": "The three R cases (CMe3, Ph, CO2Et) were classified as separate literature examples because the authors explicitly say they were shown previously in reference 20.",
                    "evidence_ids": [ev(4, "image"), ev(4, "text")],
                },
                {
                    "region": "lower-right equation 5 and surrounding prose",
                    "finding": "One present-paper RuHCl(PPh3)3/4,4-dimethyl-1,2-pentadiene reaction giving vinyl complex 11 was extracted. Two additional present-paper reactions with phenylallene and ethyl allenoate were retained separately as unsuccessful/indeterminate mixtures.",
                    "evidence_ids": [ev(4, "image"), ev(4, "text")],
                },
            ],
            "record_ids": page4_ids,
            "unresolved": [
                "Pages 1-6 omit full reaction quantities, conditions, yields, workups, and purifications for equations 3 and 5.",
                "The two mixture-producing reactions do not identify or quantify individual products.",
                "Complex organometallic connectivity was not converted to SMILES.",
            ],
        },
        {
            "page": 5,
            "state": "attempted",
            "regions": [
                {
                    "region": "top Scheme 1",
                    "finding": "Scheme 1 is a DFT model network, split into PC1 (tris-phosphine model) and PC2 (carbonyl/phosphine model) mechanism records. Its branch arrows are mechanistic alternatives, not wet experiments.",
                    "evidence_ids": [ev(5, "image"), ev(5, "text")],
                },
                {
                    "region": "left-column opening and equation-5 continuation",
                    "finding": "The first sentence completes the NMR comparison for product 11 and was merged into the equation-5 record; the remaining text discusses theoretical pathways.",
                    "evidence_ids": [ev(5, "image"), ev(5, "text")],
                },
                {
                    "region": "lower two-column theoretical discussion",
                    "finding": "The prose identifies the PC1 vinyl route as kinetically favored and the PC2 allyl route as kinetically and thermodynamically favored; ONIOM is used to assess PPh3 steric effects.",
                    "evidence_ids": [ev(5, "image"), ev(5, "text")],
                },
            ],
            "record_ids": page5_ids,
            "unresolved": [
                "Calculated transition-state/intermediate structures were not assigned SMILES.",
                "Scheme 1 contains no experimental quantities, workup, purification, or yield because it is computational.",
            ],
        },
        {
            "page": 6,
            "state": "attempted",
            "regions": [
                {
                    "region": "upper Figure 3",
                    "finding": "Calculated PC1 vinyl/allyl energy profiles were associated with the PC1 mechanism record; values are relative free energies with electronic energies in parentheses, not reaction yields.",
                    "evidence_ids": [ev(6, "image"), ev(6, "text")],
                },
                {
                    "region": "middle/lower Figure 4",
                    "finding": "Calculated PC2 vinyl/allyl profiles, including PH3-model and ONIOM/PPh3 energy sets, were associated with the PC2 mechanism record; no experimental reaction record was created.",
                    "evidence_ids": [ev(6, "image"), ev(6, "text")],
                },
                {
                    "region": "bottom continuation text",
                    "finding": "The text relates the lower PC2 barriers to weaker back-bonding in the presence of CO and continues onto page 7; page 7 is not claimed as covered.",
                    "evidence_ids": [ev(6, "image"), ev(6, "text")],
                },
            ],
            "record_ids": page6_ids,
            "unresolved": [
                "The mechanistic explanation continues beyond the requested page range.",
                "Energy values are retained as source text because kcal/mol is not a supported structured reaction-quantity unit in the current schema.",
            ],
        },
    ],
}

coverage_path = RUN / "coverage" / "pages_0001_0006.json"
coverage_path.parent.mkdir(parents=True, exist_ok=True)
coverage_path.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

tasks_path = RUN / "tasks.json"
tasks = json.loads(tasks_path.read_text())
target_tasks = {ev(i, "text") for i in range(1, 7)}
for task in tasks:
    if task["task_id"] in target_tasks:
        task["state"] = "attempted"
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"records": len(records), "coverage_pages": len(coverage["pages"])}, ensure_ascii=False))
