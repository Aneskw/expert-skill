#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "runs/current/raw_model/records_pages_0001_0003.json"
COVERAGE = ROOT / "runs/current/coverage/pages_0001_0003.json"
TASKS = ROOT / "runs/current/tasks.json"
DOC = "doc_4b99347c27b9c1ae"


def fact(value, evidence=()):
    return {
        "value": value,
        "evidence_ids": list(evidence) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def field(name, value, evidence=(), targets=None):
    item = {"name": name, "fact": fact(value, evidence)}
    if targets:
        item["target_entity_ids"] = list(targets)
    return item


def participant(entity_id, role, label, evidence, name=None, smiles=None, amounts=()):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence) if name is not None else fact(None),
        "smiles": fact(smiles, evidence) if smiles is not None else fact(None),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": list(amounts),
    }


def experimental_step(step_id, participant_ids, evidence, temperature=None, time=None,
                      atmosphere=None, workup=None, purification=None):
    return {
        "step_id": step_id,
        "participant_ids": list(participant_ids),
        "conditions": [
            field("temperature", temperature, evidence),
            field("time", time, evidence),
            field("atmosphere", atmosphere, evidence),
            field("workup", workup, evidence),
            field("purification", purification, evidence),
        ],
    }


def record(rid, kind, evidence, participants=(), steps=(), outcomes=(), notes=(), unresolved=()):
    return {
        "record_id": f"{DOC}:{rid}",
        "document_id": DOC,
        "source_reaction_id": rid,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": list(dict.fromkeys(evidence)),
        "participants": list(participants),
        "steps": list(steps),
        "outcomes": list(outcomes),
        "notes": [fact(value, evidence) for value in notes],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": list(unresolved),
        },
    }


P1 = [f"{DOC}:page1:image", f"{DOC}:page1:text"]
P2 = [f"{DOC}:page2:image", f"{DOC}:page2:text"]
P3 = [f"{DOC}:page3:image", f"{DOC}:page3:text"]


def p_1a(ev, amount=None):
    amounts = [] if amount is None else [field("amount", amount, ev)]
    return participant("allene_1a", "reactant", "1a", ev,
                       "cyclic allene 1a (cyclonona-1,2-diene structure as drawn)",
                       "C1=C=CCCCCCC1", amounts)


def p_2a(ev, amount=None):
    amounts = [] if amount is None else [field("amount", amount, ev)]
    return participant("alkyne_2a", "reactant", "2a", ev, "propargyl alcohol", "C#CCO", amounts)


def p_3a(ev):
    return participant("product_3a", "product", "3a", ev,
                       "2-(3-hydroxypropenyl) cyclic 1,3-diene 3a")


def catalyst(entity_id, label, ev, loading=None):
    amounts = [] if loading is None else [field("catalyst_loading", loading, ev)]
    return participant(entity_id, "catalyst", label, ev, label, amounts=amounts)


SOLVENT_SMILES = {
    "toluene": "Cc1ccccc1",
    "DMF": "CN(C)C=O",
    "i-PrOH": "CC(O)C",
    "DMA": "CC(=O)N(C)C",
}


def solvent(label, ev, volume=None):
    amounts = [] if volume is None else [field("volume", volume, ev)]
    return participant("solvent", "solvent", label, ev, label,
                       SOLVENT_SMILES.get(label), amounts)


records = []

# Scheme 1: two cited generic transformations and this paper's generic reaction class.
records.append(record(
    "scheme1a_prior_alkyne_alkene_coupling", "literature_example", P1,
    participants=[
        participant("generic_alkyne", "reactant", "R1-substituted terminal alkyne", P1),
        participant("generic_alkene", "reactant", "R2-substituted alkene", P1),
        participant("ru_catalyst", "catalyst", "[Ru]", P1),
        participant("generic_14_diene", "product", "generic 1,4-diene", P1),
    ],
    steps=[experimental_step("prior_coupling", ["generic_alkyne", "generic_alkene", "ru_catalyst"], P1)],
    notes=["Scheme 1(a) is marked 'early work' and is discussed as Trost et al. prior work."],
    unresolved=["Generic R-group structures, catalyst identity, quantities, conditions, procedure and yield are not reported in this paper."]
))
records.append(record(
    "scheme1b_prior_allene_enone_coupling", "literature_example", P1,
    participants=[
        participant("generic_allene", "reactant", "R3-substituted allene", P1),
        participant("generic_enone", "reactant", "R4-substituted alpha,beta-unsaturated enone", P1),
        participant("ru_catalyst", "catalyst", "[Ru]", P1),
        participant("generic_methylene_alkenyl_ketone", "product", "generic 3-methylene-4-alkenyl ketone", P1),
    ],
    steps=[experimental_step("prior_coupling", ["generic_allene", "generic_enone", "ru_catalyst"], P1)],
    notes=["Scheme 1(b) is marked 'early work' and is discussed as Trost et al. prior work."],
    unresolved=["Generic R-group structures, catalyst identity, quantities, conditions, procedure and yield are not reported in this paper."]
))
records.append(record(
    "scheme1c_present_reaction_general_scheme", "general_scheme", P1,
    participants=[
        participant("generic_cyclic_allene", "reactant", "R3-substituted cyclic allene", P1),
        participant("generic_terminal_alkyne", "reactant", "R1-substituted terminal alkyne", P1),
        participant("ru_catalyst", "catalyst", "[Ru]", P1),
        participant("generic_cross_conjugated_triene", "product", "generic 2-vinylic cyclic 1,3-diene", P1),
    ],
    steps=[experimental_step("general_coupling", ["generic_cyclic_allene", "generic_terminal_alkyne", "ru_catalyst"], P1)],
    notes=["Scheme 1(c) summarizes the present reaction class; row-level experiments are recorded separately."],
    unresolved=["The generic R groups and full conditions are intentionally not expanded from the later examples."]
))

# Table 1 optimization entries.
table1 = [
    (1, "RuHCl(CO)(PPh3)3", "toluene", {"number": 100, "unit": "°C"}, None, "Complicated", False),
    (2, "RuHCl(CO)(PPh3)3", "DMF", {"number": 100, "unit": "°C"}, 4, None, False),
    (3, "Cp*RuCl(COD)", "toluene", {"number": 100, "unit": "°C"}, 18, None, False),
    (4, "Cp*RuCl(COD)", "DMF", {"number": 100, "unit": "°C"}, 7, None, False),
    (5, "Cp*RuCl(COD)", "i-PrOH", "reflux", 14, None, False),
    (6, "Cp*RuCl(COD)", "DMA", {"number": 100, "unit": "°C"}, 38, None, False),
    (7, "Cp*RuCl(PPh3)2", "DMA", {"number": 100, "unit": "°C"}, 27, None, False),
    (8, "Cp*RuCl(PPh3)2", "toluene", {"number": 100, "unit": "°C"}, 84, None, False),
    (9, "[CpRu(MeCN)3]PF6", "DMF", {"number": 80, "unit": "°C"}, 16, None, True),
]
for entry, cat_label, solv, temp, yld, qualitative, impure in table1:
    cat_id = "catalyst_" + str(entry)
    participants = [
        p_1a(P1, {"number": 0.25, "unit": "mmol"}),
        p_2a(P1, {"number": 0.3, "unit": "mmol"}),
        catalyst(cat_id, cat_label, P1, {"number": 5, "unit": "mol%"}),
        solvent(solv, P1, {"number": 2, "unit": "mL"}),
        p_3a(P1),
    ]
    outcomes = []
    if yld is None:
        outcomes.append(field("isolated_yield_3a", None, targets=["product_3a"]))
        outcomes.append(field("reaction_result", qualitative, P1, ["product_3a"]))
    else:
        outcomes.append(field("isolated_yield_3a", {"number": yld, "unit": "%"}, P1, ["product_3a"]))
    outcomes.append(field("yield_measurement_basis", "isolated", P1, ["product_3a"]))
    notes = [f"Table 1 entry {entry}."]
    if impure:
        notes.append("Footnote b states that the product is not pure.")
    records.append(record(
        f"table1_entry{entry}", "optimization_entry", P1, participants,
        [experimental_step("coupling", ["allene_1a", "alkyne_2a", cat_id, "solvent"], P1,
                           temperature=temp, time={"number": 24, "unit": "h"})],
        outcomes, notes,
        ["Atmosphere, workup and purification are not reported in the supplied main paper."
         + (" Product purity is explicitly qualified." if impure else "")]
    ))

# Table 2 scope.
scope = [
    (1, "2b", "Me-substituted propargylic alcohol", "C#CC(O)C", "3b", 67),
    (2, "2c", "phenyl-substituted propargylic alcohol", "C#CC(O)c1ccccc1", "3c", 66),
    (3, "2d", "4-methylphenyl-substituted propargylic alcohol", "C#CC(O)c1ccc(C)cc1", "3d", 60),
    (4, "2e", "4-methoxyphenyl-substituted propargylic alcohol", "C#CC(O)c1ccc(OC)cc1", "3e", 53),
    (5, "2f", "4-chlorophenyl-substituted propargylic alcohol", "C#CC(O)c1ccc(Cl)cc1", "3f", 76),
    (6, "2g", "3-bromophenyl-substituted propargylic alcohol", "C#CC(O)c1cccc(Br)c1", "3g", 72),
    (7, "2h", "benzodioxolyl-substituted propargylic alcohol", "C#CC(O)c1ccc2c(c1)OCO2", "3h", 61),
]
for entry, alkyne_label, alkyne_name, smi, product_label, yld in scope:
    alkyne_id = "alkyne_" + alkyne_label
    product_id = "product_" + product_label
    ev = P2
    participants = [
        p_1a(ev, {"number": 0.25, "unit": "mmol"}),
        participant(alkyne_id, "reactant", alkyne_label, ev, alkyne_name, smi,
                    [field("equivalents", {"number": 1.2, "unit": "equiv"}, ev)]),
        catalyst("catalyst", "Cp*RuCl(PPh3)2", ev, {"number": 5, "unit": "mol%"}),
        solvent("toluene", ev),
        participant(product_id, "product", product_label, ev, f"coupling product {product_label}"),
    ]
    records.append(record(
        f"table2_entry{entry}_{product_label}", "substrate_scope_entry", ev, participants,
        [experimental_step("coupling", ["allene_1a", alkyne_id, "catalyst", "solvent"], ev,
                           temperature={"number": 100, "unit": "°C"}, time={"number": 24, "unit": "h"})],
        [field(f"isolated_yield_{product_label}", {"number": yld, "unit": "%"}, ev, [product_id]),
         field("yield_measurement_basis", "isolated", ev, [product_id])],
        [f"Table 2 entry {entry}."],
        ["Atmosphere, solvent volume, workup and purification are not reported; product connectivity and stereochemistry remain unverified."]
    ))

# Equation 1: enantioenriched substrate.
eq1_participants = [
    p_1a(P2),
    participant("r_2b", "reactant", "(R)-2b", P2, "enantioenriched (R)-2b", "C#C[C@H](O)C"),
    catalyst("catalyst", "Cp*RuCl(PPh3)2", P2, {"number": 5, "unit": "mol%"}),
    solvent("toluene", P2),
    participant("r_3b", "product", "(R)-3b", P2, "enantioenriched coupling product (R)-3b"),
]
records.append(record(
    "equation1_r2b_to_r3b", "reported_experiment", P2, eq1_participants,
    [experimental_step("enantioenriched_coupling", ["allene_1a", "r_2b", "catalyst", "solvent"], P2,
                       temperature={"number": 100, "unit": "°C"})],
    [field("starting_material_ee", {"number": 98, "unit": "%"}, P2, ["r_2b"]),
     field("reported_yield_r3b", {"number": 60, "unit": "%"}, P2, ["r_3b"]),
     field("product_ee", {"number": 97, "unit": "%"}, P2, ["r_3b"]),
     field("yield_measurement_basis", None, targets=["r_3b"])],
    ["The text states that the product was obtained without obvious loss of chirality."],
    ["Time, absolute scale, atmosphere, workup, purification and yield measurement basis are not reported; stereochemical SMILES is a machine candidate."]
))

# Equation 2: deuterium-labeling experiment.
eq2_participants = [
    p_1a(P2),
    participant("d_2a", "reactant", "2a'", P2, "terminal- and O-deuterated propargyl alcohol 2a'", "[2H]C#CCO[2H]"),
    catalyst("catalyst", "Cp*RuCl(PPh3)2", P2, {"number": 5, "unit": "mol%"}),
    solvent("toluene", P2),
    participant("d_3a", "product", "3a'", P2, "3-deuterated 3-(nona-1,3-dien-2-yl)prop-2-enol 3a'"),
]
records.append(record(
    "equation2_deuterium_labeling", "reported_experiment", P2, eq2_participants,
    [experimental_step("deuterium_probe", ["allene_1a", "d_2a", "catalyst", "solvent"], P2,
                       temperature={"number": 100, "unit": "°C"}, time={"number": 24, "unit": "h"})],
    [field("starting_material_terminal_deuterium_incorporation", {"number": 96, "unit": "%"}, P2, ["d_2a"]),
     field("reported_yield_d3a", {"number": 60, "unit": "%"}, P2, ["d_3a"]),
     field("product_deuterium_incorporation", {"number": 94, "unit": "%"}, P2, ["d_3a"]),
     field("yield_measurement_basis", None, targets=["d_3a"])],
    ["The deuterium-labeling result is used to exclude a vinylidene-ruthenium pathway."],
    ["Absolute scale, atmosphere, workup, purification and yield measurement basis are not reported; isotope-specific product structure remains unverified."]
))

# Scheme 2: proposed mechanism.
mechanism_participants = [
    p_1a(P2),
    participant("d_2a", "reactant", "2a'", P2, "deuterated propargyl alcohol 2a'", "[2H]C#CCO[2H]"),
    catalyst("ru_species", "Cp*RuCl(PPh3)2 / derived [Ru] species", P2),
    participant("complex_i", "unspecified_agent", "I", P2, "coordination complex I"),
    participant("complex_ii", "unspecified_agent", "II", P2, "metallabicyclic intermediate II"),
    participant("complex_iii", "unspecified_agent", "III", P2, "beta-H-elimination intermediate III"),
    participant("d_3a", "product", "3a'", P2, "deuterated triene product 3a'"),
]
records.append(record(
    "scheme2_proposed_mechanism", "mechanism", P2, mechanism_participants,
    [
        {"step_id": "coordination", "participant_ids": ["allene_1a", "d_2a", "ru_species", "complex_i"],
         "conditions": [field("operation", "coordination of allene and alkyne", P2)]},
        {"step_id": "cyclometallation", "participant_ids": ["complex_i", "complex_ii"],
         "conditions": [field("operation", "cycloaddition/cyclometallation", P2)]},
        {"step_id": "beta_h_elimination", "participant_ids": ["complex_ii", "complex_iii"],
         "conditions": [field("operation", "beta-H elimination", P2)]},
        {"step_id": "reductive_elimination", "participant_ids": ["complex_iii", "d_3a", "ru_species"],
         "conditions": [field("operation", "reductive elimination and catalyst regeneration", P2)]},
    ],
    notes=["Scheme 2 is explicitly captioned as a proposed mechanism; hydroxyl coordination is proposed to determine regioselectivity."],
    unresolved=["Intermediates I-III and organoruthenium connectivity are proposed and unverified; no stepwise quantities or yields are reported."]
))

# Scheme 3, equations 3-5.
scheme3_rows = [
    ("scheme3_eq3_2i_to_3i", "2i", "propargylic tosyl amide", "C#CCNS(=O)(=O)c1ccc(C)cc1", "3i", 87,
     "Cp*RuCl(PPh3)2", "toluene", {"number": 100, "unit": "°C"}, {"number": 5, "unit": "mol%"}, P2),
    ("scheme3_eq4_2j_to_3j", "2j", "dimethyl 2-propargylmalonate", "C#CCC(C(=O)OC)C(=O)OC", "3j", 49,
     "Cp*RuCl(PPh3)2", "toluene", {"number": 100, "unit": "°C"}, {"number": 5, "unit": "mol%"}, P2),
    ("scheme3_eq5_2k_to_3k_cpruclcod", "2k", "phenylacetylene", "C#Cc1ccccc1", "3k", 50,
     "Cp*RuCl(COD)", "DMA", {"number": 100, "unit": "°C"}, {"number": 5, "unit": "mol%"}, P2),
]
for rid, alabel, aname, smi, plabel, yld, catlabel, solv, temp, loading, ev in scheme3_rows:
    aid, pid = "alkyne_" + alabel, "product_" + plabel
    parts = [p_1a(ev), participant(aid, "reactant", alabel, ev, aname, smi),
             catalyst("catalyst", catlabel, ev, loading), solvent(solv, ev),
             participant(pid, "product", plabel, ev, f"coupling product {plabel}")]
    basis = "isolated" if plabel == "3k" else None
    records.append(record(
        rid, "reported_experiment", ev, parts,
        [experimental_step("coupling", ["allene_1a", aid, "catalyst", "solvent"], ev, temperature=temp)],
        [field(f"reported_yield_{plabel}", {"number": yld, "unit": "%"}, ev, [pid]),
         field("yield_measurement_basis", basis, ev if basis else (), [pid])],
        [f"Scheme 3 reaction giving {plabel}."],
        ["Absolute scale, time, atmosphere, workup and purification are not reported."
         + (" Yield basis is not stated." if basis is None else "")]
    ))

# Alternative catalyst for phenylacetylene, described only in prose.
alt_ev = P2
alt_parts = [p_1a(alt_ev), participant("alkyne_2k", "reactant", "2k", alt_ev, "phenylacetylene", "C#Cc1ccccc1"),
             catalyst("catalyst", "Cp*RuCl(PPh3)2", alt_ev),
             participant("product_3k", "product", "3k", alt_ev, "coupling product 3k")]
records.append(record(
    "scheme3_eq5_2k_to_3k_cpruclpph3_alternative", "reported_experiment", alt_ev, alt_parts,
    [experimental_step("alternative_catalyst_coupling", ["allene_1a", "alkyne_2k", "catalyst"], alt_ev)],
    [field("reported_yield_3k", {"number": 52, "unit": "%"}, alt_ev, ["product_3k"]),
     field("yield_measurement_basis", None, targets=["product_3k"]),
     field("product_purity", "slightly lower purity", alt_ev, ["product_3k"])],
    ["The prose reports a similar 52% yield under Cp*RuCl(PPh3)2 catalysis, with slightly lower purity."],
    ["Catalyst loading, solvent, temperature, time, scale, atmosphere, workup, purification and yield basis are not explicitly restated for this alternative condition."]
))

# Scheme 4 on page 3, with contextual prose on page 2.
scheme4_ev = P2 + P3
scheme4_rows = [
    ("scheme4_eq6_1b_2d_to_3l", "2d", "4-methylphenyl-substituted propargylic alcohol", "C#CC(O)c1ccc(C)cc1", "3l", 60),
    ("scheme4_eq7_1b_2i_to_3m", "2i", "propargylic tosyl amide", "C#CCNS(=O)(=O)c1ccc(C)cc1", "3m", 50),
]
for rid, alabel, aname, smi, plabel, yld in scheme4_rows:
    aid, pid = "alkyne_" + alabel, "product_" + plabel
    parts = [
        participant("allene_1b", "reactant", "1b", scheme4_ev, "cyclic 1,2,6-nonatriene 1b as drawn",
                    amounts=[field("equivalents", {"number": 2, "unit": "equiv"}, P3)]),
        participant(aid, "reactant", alabel, scheme4_ev, aname, smi),
        catalyst("catalyst", "Cp*RuCl(PPh3)2", scheme4_ev, {"number": 5, "unit": "mol%"}),
        solvent("toluene", scheme4_ev),
        participant(pid, "product", plabel, scheme4_ev, f"1b-derived coupling product {plabel}"),
    ]
    records.append(record(
        rid, "reported_experiment", scheme4_ev, parts,
        [experimental_step("coupling", ["allene_1b", aid, "catalyst", "solvent"], scheme4_ev,
                           temperature={"number": 100, "unit": "°C"}, time={"number": 2, "unit": "h"})],
        [field(f"reported_yield_{plabel}", {"number": yld, "unit": "%"}, P3, [pid]),
         field("yield_measurement_basis", None, targets=[pid])],
        ["The page-2 prose states that the remote C-C double bond in 1b did not participate."],
        ["Absolute scale, atmosphere, workup, purification and yield measurement basis are not reported; structures remain unverified."]
    ))

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")

page1_ids = [r["record_id"] for r in records if any(e.startswith(f"{DOC}:page1:") for e in r["evidence_ids"])]
page2_ids = [r["record_id"] for r in records if any(e.startswith(f"{DOC}:page2:") for e in r["evidence_ids"])]
page3_ids = [r["record_id"] for r in records if any(e.startswith(f"{DOC}:page3:") for e in r["evidence_ids"])]

coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1,
            "state": "attempted",
            "regions": [
                {"region": "lower-left Scheme 1",
                 "finding": "Separated two generic cited prior-work arrows (a,b) from the present-paper generic reaction class (c); none was treated as a row-level executed experiment.",
                 "evidence_ids": [f"{DOC}:page1:image", f"{DOC}:page1:text"]},
                {"region": "upper-right Table 1 reaction header, nine rows, and footnotes",
                 "finding": "Extracted nine independent optimization entries with common scale/solvent volume/5 mol% catalyst/24 h conditions, row-specific catalyst, solvent, temperature and isolated-yield result; retained 'Complicated', reflux, and the impure-product footnote literally.",
                 "evidence_ids": [f"{DOC}:page1:image", f"{DOC}:page1:text"]},
                {"region": "title, abstract, introduction and results prose",
                 "finding": "Used narrative statements as context for Scheme 1 and Table 1; abstract-level claims and prose repetitions were not duplicated as experiments. The online ESI availability statement was not treated as supplied SI.",
                 "evidence_ids": [f"{DOC}:page1:image", f"{DOC}:page1:text"]},
            ],
            "record_ids": page1_ids,
            "unresolved": [
                "No SI file was supplied or explicitly associated.",
                "Table 1 omits atmosphere, workup and purification; entry 1 reports only a complicated outcome and entry 9 says the product is not pure.",
                "Generic Scheme 1 R-group structures and prior-work procedures remain unspecified.",
            ],
        },
        {
            "page": 2,
            "state": "attempted",
            "regions": [
                {"region": "upper-left Table 2 and reaction header",
                 "finding": "Extracted seven independent propargylic-alcohol scope rows with common 1a scale, 1.2-equivalent alkyne, 5 mol% catalyst, toluene/100 °C/24 h conditions, and isolated yields.",
                 "evidence_ids": [f"{DOC}:page2:image", f"{DOC}:page2:text"]},
                {"region": "left-column equations (1) and (2)",
                 "finding": "Extracted a distinct enantioenriched (R)-2b coupling and a distinct deuterium-labeling experiment, preserving substrate/product ee or D incorporation and reported yields.",
                 "evidence_ids": [f"{DOC}:page2:image", f"{DOC}:page2:text"]},
                {"region": "upper-right Scheme 2",
                 "finding": "Classified the I-to-III organoruthenium pathway as a proposed mechanism, not executed stepwise experiments.",
                 "evidence_ids": [f"{DOC}:page2:image", f"{DOC}:page2:text"]},
                {"region": "lower-right Scheme 3 and adjacent prose",
                 "finding": "Extracted three drawn terminal-alkyne coupling experiments plus the separately reported Cp*RuCl(PPh3)2 alternative for 3k; kept the two catalyst conditions independent.",
                 "evidence_ids": [f"{DOC}:page2:image", f"{DOC}:page2:text"]},
                {"region": "right-column Scheme 4 lead-in prose",
                 "finding": "Linked the statement that the remote double bond of 1b did not participate to the two Scheme 4 experiments drawn on page 3.",
                 "evidence_ids": [f"{DOC}:page2:image", f"{DOC}:page2:text", f"{DOC}:page3:image"]},
            ],
            "record_ids": page2_ids,
            "unresolved": [
                "Most scope/scheme experiments omit atmosphere, workup and purification; several omit scale, time or yield basis.",
                "The alternative Cp*RuCl(PPh3)2 preparation of 3k does not explicitly restate catalyst loading or the other conditions.",
                "Complex product structures, stereochemistry and the proposed organoruthenium intermediates remain unverified.",
            ],
        },
        {
            "page": 3,
            "state": "attempted",
            "regions": [
                {"region": "upper-left Scheme 4",
                 "finding": "Extracted two independent 1b coupling experiments (2d to 3l and 2i to 3m), including 2 equivalents 1b, 5 mol% catalyst, toluene/100 °C/2 h and product-specific yields.",
                 "evidence_ids": [f"{DOC}:page3:image", f"{DOC}:page3:text", f"{DOC}:page2:text"]},
                {"region": "remaining acknowledgments and references",
                 "finding": "No additional present-paper experiment, table, arrow or procedure; citations were not mined as associated source documents.",
                 "evidence_ids": [f"{DOC}:page3:image", f"{DOC}:page3:text"]},
            ],
            "record_ids": page3_ids,
            "unresolved": [
                "Scheme 4 omits absolute scale, atmosphere, workup, purification and yield measurement basis.",
                "No cited publication or SI file was supplied as an associated source.",
                "1b-derived product connectivity and stereochemistry remain unverified.",
            ],
        },
    ],
}
COVERAGE.parent.mkdir(parents=True, exist_ok=True)
COVERAGE.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

tasks = json.loads(TASKS.read_text())
for task in tasks:
    if task.get("document_id") == DOC and task.get("evidence_id") in {
        f"{DOC}:page1:text", f"{DOC}:page2:text", f"{DOC}:page3:text"
    }:
        task["state"] = "attempted"
TASKS.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"records": len(records), "coverage_pages": [p["page"] for p in coverage["pages"]]}, ensure_ascii=False))
