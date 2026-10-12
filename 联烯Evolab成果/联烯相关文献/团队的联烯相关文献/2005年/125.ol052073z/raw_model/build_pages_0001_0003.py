#!/usr/bin/env python3
"""Build source-linked machine records for PDF pages 1-3 of ol052073z."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
DOC = "doc_b735dd35845a612f"
EV = {
    n: [f"{DOC}:page{n}:text", f"{DOC}:page{n}:image"] for n in (1, 2, 3)
}


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


def participant(entity_id, role, label, name, evidence, smiles=None, amounts=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence),
        "smiles": fact(smiles, evidence if smiles else []),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": amounts or [],
    }


def record(suffix, page, kind, participants, conditions, outcomes, notes, unresolved):
    # Copy the page list so a later cross-page evidence merge cannot mutate EV globally.
    evidence = list(EV[page])
    return {
        "record_id": f"{DOC}:{suffix}",
        "document_id": DOC,
        "source_reaction_id": suffix,
        "record_kind": kind,
        "status": "needs_review",
        "completeness": "partial",
        "evidence_ids": evidence,
        "participants": participants,
        "steps": [{
            "step_id": "step1",
            "participant_ids": [p["entity_id"] for p in participants],
            "conditions": conditions,
        }],
        "outcomes": outcomes,
        "notes": [fact(note, evidence) for note in notes],
        "review": {
            "method": "model",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved,
        },
    }


SMILES = {
    "1a": "c1ccc2[nH]ccc2c1",
    "1c": "Cc1cc2ccccc2[nH]1",
    "1d": "Cc1cc2ccccc2n1C",
    "1e": "COc1ccc2[nH]ccc2c1",
    "1f": "Brc1ccc2[nH]ccc2c1",
    "1g": "c1ccc(COc2ccc3[nH]ccc3c2)cc1",
    "1h": "Cn1ccc2ccccc21",
    "1i": "Cc1ccc2[nH]ccc2c1",
    "2a": "C=C=CC(=O)CCCCCCC",
    "2b": "C=C=CC(=O)CCCCCCCC",
    "2c": "C=C=CC(=O)CCCCCC",
    "2d": "C=C=CC(=O)CCCC",
    "2e": "C=C=CC(=O)Cc1ccccc1",
    "CH3CN": "CC#N",
    "CDCl3": "[2H]C(Cl)(Cl)Cl",
}

INDOLE_NAMES = {
    "1a": "indole",
    "1b": "7-methyl-1H-indole",
    "1c": "2-methyl-1H-indole",
    "1d": "1,2-dimethyl-1H-indole",
    "1e": "5-methoxy-1H-indole",
    "1f": "5-bromo-1H-indole",
    "1g": "5-benzyloxy-1H-indole",
    "1h": "1-methyl-1H-indole",
    "1i": "5-methyl-1H-indole",
}

ALLENE_NAMES = {
    "2a": "undeca-1,2-dien-4-one",
    "2b": "1,2-allenic ketone 2b (R3=n-C8H17)",
    "2c": "1,2-allenic ketone 2c (R3=n-C6H13)",
    "2d": "1,2-allenic ketone 2d (R3=n-C4H9)",
    "2e": "1,2-allenic ketone 2e (R3=Bn)",
}


def amount(value, evidence):
    return field("amount", value, evidence)


def catalyst(label, evidence, catalyst_amount=None):
    amounts = [] if catalyst_amount is None else [field("catalyst_loading", catalyst_amount, evidence)]
    return participant(f"catalyst_{label.replace('(', '_').replace(')', '').replace('/', '_')}",
                       "catalyst", label, label, evidence, amounts=amounts)


def solvent(label, evidence, volume=None):
    amounts = [] if volume is None else [field("solvent_volume", volume, evidence)]
    return participant(f"solvent_{label}", "solvent", label, label, evidence,
                       smiles=SMILES.get(label), amounts=amounts)


records = []

# Page 1: two arrows in the graphical abstract are generic, not individual examples.
p1 = EV[1]
generic1 = participant("generic_indole_1", "reactant", "1", "generic substituted indole 1", p1)
generic2 = participant("generic_allenic_ketone_2", "reactant", "2", "generic 1,2-allenic ketone 2", p1)
generic3 = participant("generic_enone_3", "product", "3", "generic beta-indolyl alpha,beta-unsaturated (E)-enone 3", p1)
records.append(record(
    "graphical_abstract_mono_generic", 1, "general_scheme",
    [generic1, generic2, generic3, catalyst("Sc(OTf)3", p1, {"number": 5, "unit": "mol%"}), solvent("CDCl3", p1)],
    [field("solvent", "CDCl3", p1), field("temperature", "r.t.", p1), field("time", None, [])],
    [field("yield", None, [], ["generic_enone_3"]), field("E_Z_ratio", None, [], ["generic_enone_3"])],
    ["Graphical-abstract first arrow; R1-R3 are generic substituents."],
    ["Generic R groups prevent structure-specific SMILES.", "Reaction time, yield, and exact quantities are not reported for this arrow."]
))
generic3b = participant("generic_enone_3", "reactant", "3", "generic beta-indolyl alpha,beta-unsaturated (E)-enone 3", p1)
generic1b = participant("generic_second_indole", "reactant", "1", "generic second substituted indole", p1)
generic4 = participant("generic_bisindolyl_ketone_4", "product", "4", "generic beta,beta-bisindolyl ketone 4", p1)
records.append(record(
    "graphical_abstract_second_indolylation_generic", 1, "general_scheme",
    [generic3b, generic1b, generic4, catalyst("Sc(OTf)3", p1, {"number": 5, "unit": "mol%"}), solvent("CDCl3", p1)],
    [field("solvent", "CDCl3", p1), field("temperature", "r.t.", p1), field("time", None, [])],
    [field("yield", None, [], ["generic_bisindolyl_ketone_4"])],
    ["Graphical-abstract second arrow; R1-R4 are generic substituents.",
     "The abstract separately states that beta,beta-bisindolyl ketones were prepared using 2.5 equivalents of indoles, but does not unambiguously assign that amount to this depicted stepwise arrow."],
    ["Generic R groups prevent structure-specific SMILES.", "Reaction time, yield, and exact reactant quantities for this arrow are not reported.", "The 2.5 equiv abstract statement is not assigned to a specific participant in this generic arrow."]
))

# Page 2, Table 1: five optimization rows.
p2 = EV[2]
table1 = [
    (1, "Mg(OTf)2", 12, "NR", None, None),
    (2, "Yb(OTf)3", 12, "NR", None, None),
    (3, "Sn(OTf)2", 12, {"number": 27, "unit": "%"}, ">99/1", None),
    (4, "Cu(OTf)2", 1.5, {"number": 68, "unit": "%"}, "91/9", {"number": 65, "unit": "%"}),
    (5, "Sc(OTf)3", 1.5, {"number": 73, "unit": "%"}, ">99/1", {"number": 75, "unit": "%"}),
]
for entry, cat, hours, table_yield, ez, prose_yield in table1:
    indole_amounts = [amount({"number": 0.2, "unit": "mmol"}, p2)]
    allene_amounts = [amount({"number": 0.3, "unit": "mmol"}, p2)]
    row_unresolved = ["Yield measurement basis, workup, purification, atmosphere, and detailed procedure are not given in the main-text table.",
                      "Product 3aa candidate SMILES is left null pending independent structure verification."]
    row_notes = ["Table 1 optimization row; the E/Z ratio was determined by 1H NMR where reported."]
    if entry == 5:
        indole_amounts.append(field("equivalents", {"number": 1, "unit": "equiv"}, p2))
        allene_amounts.append(field("equivalents", {"number": 3, "unit": "equiv"}, p2))
        row_notes.append("Footnote c gives a 1a:2a ratio of 1:3, whereas footnote a gives 0.2 mmol:0.3 mmol; both statements are preserved.")
        row_unresolved.append("Entry-specific 1:3 ratio conflicts with the 1:1.5 ratio implied by the general footnote amounts.")
    if prose_yield:
        row_notes.append(f"The adjacent prose reports {prose_yield['number']:.0f}% yield, conflicting with the table value {table_yield['number']:.0f}%.")
        row_unresolved.append("Prose and table yield values conflict; neither value was discarded.")
    ps = [
        participant("indole_1a", "reactant", "1a", "indole", p2, SMILES["1a"], indole_amounts),
        participant("allenic_ketone_2a", "reactant", "2a", "undeca-1,2-dien-4-one", p2, SMILES["2a"], allene_amounts),
        catalyst(cat, p2, {"number": 5, "unit": "mol%"}),
        solvent("CH3CN", p2, {"number": 2, "unit": "mL"}),
        participant("product_3aa", "product", "3aa", "beta-indolyl alpha,beta-unsaturated enone 3aa", p2),
    ]
    outs = [field("table_yield", table_yield, p2, ["product_3aa"]),
            field("E_Z_ratio", ez, p2 if ez else [], ["product_3aa"]),
            field("yield_measurement_basis", None, [], ["product_3aa"])]
    if prose_yield:
        outs.append(field("prose_yield", prose_yield, p2, ["product_3aa"]))
    records.append(record(
        f"table1_entry{entry}", 2, "optimization_entry", ps,
        [field("operation", "stirring", p2), field("solvent", "CH3CN", p2),
         field("temperature", "r.t.", p2), field("time", {"number": hours, "unit": "h"}, p2)],
        outs, row_notes, row_unresolved
    ))

# Page 2, Table 2: seven monoindolylation substrate-scope rows.
table2 = [
    (1, "1b", "2a", "3ba", 1, 81, ">99/1", "R1=7-Me, R2=H, R3=n-C7H15"),
    (2, "1c", "2a", "3ca", 1, 76, ">99/1", "R1=2-Me, R2=H, R3=n-C7H15"),
    (3, "1c", "2b", "3cb", 2, 82, ">99/1", "R1=2-Me, R2=H, R3=n-C8H17"),
    (4, "1c", "2c", "3cc", 2, 77, ">99/1", "R1=2-Me, R2=H, R3=n-C6H13"),
    (5, "1c", "2d", "3cd", 2, 74, ">99/1", "R1=2-Me, R2=H, R3=n-C4H9"),
    (6, "1c", "2e", "3ce", 2, 80, ">99/1", "R1=2-Me, R2=H, R3=Bn"),
    (7, "1d", "2a", "3da", 1.5, 73, ">99/1", "R1=2-Me, R2=Me, R3=n-C7H15"),
]
for entry, ind, allene, product, hours, yld, ez, descriptor in table2:
    ps = [
        participant(f"indole_{ind}", "reactant", ind, INDOLE_NAMES[ind], p2, SMILES.get(ind),
                    [amount({"number": 0.5, "unit": "mmol"}, p2)]),
        participant(f"allenic_ketone_{allene}", "reactant", allene, ALLENE_NAMES[allene], p2, SMILES[allene],
                    [amount({"number": 0.75, "unit": "mmol"}, p2)]),
        catalyst("Sc(OTf)3", p2, {"number": 5, "unit": "mol%"}),
        solvent("CH3CN", p2, {"number": 2, "unit": "mL"}),
        participant(f"product_{product}", "product", product,
                    f"beta-indolyl alpha,beta-unsaturated (E)-enone {product} ({descriptor})", p2),
    ]
    records.append(record(
        f"table2_entry{entry}_{product}", 2, "substrate_scope_entry", ps,
        [field("operation", "stirring", p2), field("solvent", "CH3CN", p2),
         field("temperature", "r.t.", p2), field("time", {"number": hours, "unit": "h"}, p2)],
        [field("yield", {"number": yld, "unit": "%"}, p2, [f"product_{product}"]),
         field("E_Z_ratio", ez, p2, [f"product_{product}"]),
         field("yield_measurement_basis", None, [], [f"product_{product}"])],
        ["Table 2 substrate-scope row; the E/Z ratio was determined by 1H NMR."],
        ["Yield measurement basis, workup, purification, and atmosphere are not reported in the main text.",
         f"Product {product} candidate SMILES is left null pending independent structure verification."]
    ))

# Page 2, Scheme 1: three mechanistic isotope-labeling experiments.
scheme1_rows = [
    ("scheme1_DOAc_3aa", "1a", "indole", None, "CH3CN", "DOAc", "3aa",
     "nondeuterated product 3aa", None),
    ("scheme1_1a_prime_3aa_A", "1a'", "3-deuterated N-deuterated indole 1a'", 92, "CDCl3", None, "3aa-A",
     "monodeuterated product 3aa-A", 90),
    ("scheme1_1a_double_prime_3aa_B", "1a''", "3-deuterated 1-methylindole 1a''", 85, "CDCl3", None, "3aa-B",
     "monodeuterated product 3aa-B", 85),
]
for suffix, label, name, react_d, solv, additive, product, result_text, product_d in scheme1_rows:
    react_amounts = [] if react_d is None else [field("reactant_deuterium_content", {"number": react_d, "unit": "%"}, p2)]
    ps = [
        participant("labeled_indole", "reactant", label, name, p2, SMILES.get(label), react_amounts),
        participant("allenic_ketone_2a", "reactant", "2a", "undeca-1,2-dien-4-one", p2, SMILES["2a"]),
        catalyst("Sc(OTf)3", p2, {"number": 5, "unit": "mol%"}),
        solvent(solv, p2),
    ]
    if additive:
        ps.append(participant("additive_DOAc", "reagent", "DOAc", "deuterated acetic acid (DOAc)", p2))
    ps.append(participant(f"product_{product}", "product", product, result_text, p2))
    outs = [field("isotope_labeling_result", result_text, p2, [f"product_{product}"]),
            field("yield", None, [], [f"product_{product}"])]
    if product_d is not None:
        outs.append(field("product_deuterium_content", {"number": product_d, "unit": "%"}, p2,
                          [f"product_{product}"]))
    isotope_record = record(
        suffix, 2, "mechanism", ps,
        [field("solvent", solv, p2), field("temperature", "r.t.", p2), field("time", None, [])],
        outs,
        ["Scheme 1 isotope-labeling experiment used to probe whether double-bond migration occurs."],
        ["Reaction time, reactant quantities, product yield, workup, purification, and atmosphere are not reported.",
         "Isotopically labeled structures and product stereochemistry are retained by label with null SMILES pending verification."]
    )
    if product in {"3aa-A", "3aa-B"}:
        isotope_record["evidence_ids"] += EV[3]
        isotope_record["notes"].append(fact(
            "The sentence continuing on page 3 states that the labeled products were formed separately in CDCl3 and discusses direct hydroindolylation rather than double-bond migration.",
            EV[3],
        ))
    records.append(isotope_record)

# Page 3, Table 3: seven double-indolylation scope rows.
p3 = EV[3]
table3 = [
    (1, "1a", "2a", "4aa", 2, 60, "R1=H, R2=H, R3=n-C7H15"),
    (2, "1e", "2a", "4ea", 1.5, 53, "R1=5-MeO, R2=H, R3=n-C7H15"),
    (3, "1f", "2a", "4fa", 2, 56, "R1=5-Br, R2=H, R3=n-C7H15"),
    (4, "1g", "2a", "4ga", 2, 51, "R1=5-BnO, R2=H, R3=n-C7H15"),
    (5, "1h", "2a", "4ha", 2, 61, "R1=H, R2=Me, R3=n-C7H15"),
    (6, "1a", "2c", "4ac", 2, 63, "R1=H, R2=H, R3=n-C6H13"),
    (7, "1a", "2e", "4ae", 12, 78, "R1=H, R2=H, R3=Bn"),
]
for entry, ind, allene, product, hours, yld, descriptor in table3:
    ps = [
        participant(f"indole_{ind}", "reactant", ind, INDOLE_NAMES[ind], p3, SMILES.get(ind),
                    [amount({"number": 1.25, "unit": "mmol"}, p3)]),
        participant(f"allenic_ketone_{allene}", "reactant", allene, ALLENE_NAMES[allene], p3, SMILES[allene],
                    [amount({"number": 0.5, "unit": "mmol"}, p3)]),
        catalyst("Sc(OTf)3", p3, {"number": 5, "unit": "mol%"}),
        solvent("CH3CN", p3, {"number": 2, "unit": "mL"}),
        participant(f"product_{product}", "product", product,
                    f"beta,beta-bisindolyl ketone {product} ({descriptor})", p3),
    ]
    records.append(record(
        f"table3_entry{entry}_{product}", 3, "substrate_scope_entry", ps,
        [field("operation", "stirring", p3), field("solvent", "CH3CN", p3),
         field("temperature", "r.t.", p3), field("time", {"number": hours, "unit": "h"}, p3)],
        [field("yield", {"number": yld, "unit": "%"}, p3, [f"product_{product}"]),
         field("yield_measurement_basis", None, [], [f"product_{product}"])],
        ["Table 3 double-indolylation substrate-scope row."],
        ["Yield measurement basis, workup, purification, and atmosphere are not reported in the main text.",
         f"Product {product} candidate SMILES is left null pending independent structure verification."]
    ))

# Page 3, Scheme 2: two distinct stepwise second-indolylation arrows.
scheme2_rows = [
    ("1h", "4ka", 64, "1-methyl-1H-indole", SMILES["1h"]),
    ("1i", "4la", 78, "5-methyl-1H-indole", SMILES["1i"]),
]
for ind, product, yld, ind_name, ind_smiles in scheme2_rows:
    ps = [
        participant("enone_3aa", "reactant", "(E)-3aa", "(E)-3aa", p3),
        participant(f"indole_{ind}", "reactant", ind, ind_name, p3, ind_smiles),
        catalyst("Sc(OTf)3", p3, {"number": 5, "unit": "mol%"}),
        solvent("CH3CN", p3),
        participant(f"product_{product}", "product", product, f"mixed beta,beta-bisindolyl ketone {product}", p3),
    ]
    records.append(record(
        f"scheme2_{ind}_{product}", 3, "reported_experiment", ps,
        [field("solvent", "CH3CN", p3), field("temperature", "r.t.", p3),
         field("time", {"number": 3, "unit": "h"}, p3)],
        [field("isolated_yield", {"number": yld, "unit": "%"}, p3, [f"product_{product}"]),
         field("yield_measurement_basis", "isolated", p3, [f"product_{product}"])],
        ["Scheme 2 stepwise second addition; the prose states that the mixed product was isolated."],
        ["Reactant amounts, solvent volume, workup, purification, and atmosphere are not reported.",
         f"Structures of (E)-3aa and product {product} retain labels with null SMILES pending independent verification."]
    ))

assert len(records) == 26
raw_path = ROOT / "raw_model" / "records_pages_0001_0003.json"
raw_path.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")

ids_by_page = {
    page: [r["record_id"] for r in records if f"{DOC}:page{page}:image" in r["evidence_ids"]]
    for page in (1, 2, 3)
}
coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1,
            "state": "attempted",
            "regions": [
                {"region": "graphical abstract, first arrow", "finding": "generic monoindolylation scheme; classified as general_scheme, not an individual reported experiment", "evidence_ids": [f"{DOC}:page1:image", f"{DOC}:page1:text"]},
                {"region": "graphical abstract, second arrow", "finding": "generic stepwise second indolylation to a beta,beta-bisindolyl ketone; classified as general_scheme", "evidence_ids": [f"{DOC}:page1:image", f"{DOC}:page1:text"]},
                {"region": "introduction and references 1-5", "finding": "background and cited prior work; no additional current-paper experiment was promoted", "evidence_ids": [f"{DOC}:page1:image", f"{DOC}:page1:text"]},
            ],
            "record_ids": ids_by_page[1],
            "unresolved": ["R-group structures in the graphical abstract are generic.", "No exact time or yield is given for either graphical-abstract arrow."],
        },
        {
            "page": 2,
            "state": "attempted",
            "regions": [
                {"region": "Table 1 and footnotes", "finding": "five optimization entries, including two NR results; table/prose yield conflicts preserved for Cu and Sc rows", "evidence_ids": [f"{DOC}:page2:image", f"{DOC}:page2:text"]},
                {"region": "Table 2 and footnotes", "finding": "seven monoindolylation substrate-scope entries extracted row by row", "evidence_ids": [f"{DOC}:page2:image", f"{DOC}:page2:text"]},
                {"region": "Scheme 1 and adjoining prose", "finding": "three isotope-labeling experiments extracted as mechanism records", "evidence_ids": [f"{DOC}:page2:image", f"{DOC}:page2:text"]},
                {"region": "references 6-8", "finding": "cited review/prior-work material only; no current-paper experiment promoted", "evidence_ids": [f"{DOC}:page2:image", f"{DOC}:page2:text"]},
            ],
            "record_ids": ids_by_page[2],
            "unresolved": ["Table 1 Cu and Sc yields conflict with adjacent prose.", "Table 1 entry 5 footnote ratio conflicts with the general mmol amounts.", "No SI was explicitly provided; detailed procedures and product structure verification remain unavailable."],
        },
        {
            "page": 3,
            "state": "attempted",
            "regions": [
                {"region": "continuation of Scheme 1 discussion", "finding": "mechanistic interpretation only; linked conceptually to page-2 isotope records and not duplicated", "evidence_ids": [f"{DOC}:page3:image", f"{DOC}:page3:text"]},
                {"region": "Table 3 and footnote", "finding": "seven double-indolylation substrate-scope entries extracted row by row", "evidence_ids": [f"{DOC}:page3:image", f"{DOC}:page3:text"]},
                {"region": "Scheme 2 and adjoining prose", "finding": "two distinct stepwise second-indolylation arrows extracted with isolated yields", "evidence_ids": [f"{DOC}:page3:image", f"{DOC}:page3:text"]},
                {"region": "Supporting Information Available statement", "finding": "the article states SI exists, but no SI file is explicitly supplied or associated in this workspace", "evidence_ids": [f"{DOC}:page3:image", f"{DOC}:page3:text"]},
                {"region": "references 9-10", "finding": "cited prior work only; no current-paper experiment promoted", "evidence_ids": [f"{DOC}:page3:image", f"{DOC}:page3:text"]},
            ],
            "record_ids": ids_by_page[3],
            "unresolved": ["Detailed workup/purification and most yield measurement bases require the unprovided SI.", "Complex product structures remain label-based with null SMILES."],
        },
    ],
}
coverage_dir = ROOT / "coverage"
coverage_dir.mkdir(parents=True, exist_ok=True)
(coverage_dir / "pages_0001_0003.json").write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

# Mark only the three in-scope page tasks attempted.
tasks_path = ROOT / "tasks.json"
tasks = json.loads(tasks_path.read_text())
for task in tasks:
    if task.get("document_id") == DOC and task.get("task_id") in {f"{DOC}:page{n}:text" for n in (1, 2, 3)}:
        task["state"] = "attempted"
        task["visual_evidence_id"] = task["task_id"].replace(":text", ":image")
        task["reason"] = "Original page image and text inspected; findings mapped in coverage/pages_0001_0003.json."
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"records": len(records), "records_by_page": {str(k): len(v) for k, v in ids_by_page.items()}, "raw": str(raw_path), "coverage": str(coverage_dir / "pages_0001_0003.json")}, ensure_ascii=False))
