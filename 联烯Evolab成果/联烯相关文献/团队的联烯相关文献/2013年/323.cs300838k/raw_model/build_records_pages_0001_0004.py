#!/usr/bin/env python3
"""Build evidence-linked machine records for cs300838k, PDF pages 1--4."""

import json
from pathlib import Path


DOC = "doc_ad76625cbed619e7"
ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / "runs/current/raw_model/records_pages_0001_0004.json"
COVERAGE = ROOT / "runs/current/coverage/pages_0001_0004.json"
TASKS = ROOT / "runs/current/tasks.json"


def ev(*pages):
    ids = []
    for page in pages:
        ids.extend([f"{DOC}:page{page}:text", f"{DOC}:page{page}:image"])
    return ids


def fact(value, evidence=None):
    return {
        "value": value,
        "evidence_ids": list(evidence or []) if value is not None else [],
        "verification": "missing" if value is None else "unreviewed",
    }


def field(name, value, evidence=None, targets=None):
    item = {"name": name, "fact": fact(value, evidence)}
    if targets:
        item["target_entity_ids"] = targets
    return item


def q(number, unit, **extra):
    value = {"number": number, "unit": unit}
    value.update(extra)
    return value


def participant(entity_id, role, label, evidence, name=None, smiles=None, amounts=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence) if name is not None else fact(None),
        "smiles": fact(smiles, evidence) if smiles is not None else fact(None),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": amounts or [],
    }


def step(step_id, participant_ids, conditions):
    return {"step_id": step_id, "participant_ids": participant_ids, "conditions": conditions}


def record(rid, kind, pages, participants=None, steps=None, outcomes=None, notes=None, unresolved=None):
    evidence = ev(*pages)
    return {
        "record_id": f"{DOC}:{rid}",
        "document_id": DOC,
        "source_reaction_id": rid,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": evidence,
        "participants": participants or [],
        "steps": steps or [],
        "outcomes": outcomes or [],
        "notes": [fact(text, evidence) for text in (notes or [])],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved or [],
        },
    }


ALDEHYDES = {
    "2a": ("4-chlorobenzaldehyde", "O=Cc1ccc(Cl)cc1"),
    "2b": ("benzaldehyde", "O=Cc1ccccc1"),
    "2c": ("4-bromobenzaldehyde", "O=Cc1ccc(Br)cc1"),
    "2d": ("4-fluorobenzaldehyde", "O=Cc1ccc(F)cc1"),
    "2e": ("3-bromobenzaldehyde", "O=Cc1cccc(Br)c1"),
    "2f": ("3-nitrobenzaldehyde", "O=Cc1cccc([N+](=O)[O-])c1"),
    "2g": ("2-bromobenzaldehyde", "O=Cc1ccccc1Br"),
    "2h": ("2-chlorobenzaldehyde", "O=Cc1ccccc1Cl"),
    "2i": ("paraformaldehyde", None),
    "2j": ("butanal", "CCCC=O"),
    "2k": ("2-methylpropanal", "CC(C)C=O"),
    "2l": ("cyclohexanecarbaldehyde", "O=CC1CCCCC1"),
    "2m": ("4-isopropylbenzaldehyde", "O=Cc1ccc(C(C)C)cc1"),
    "2n": ("4-methoxybenzaldehyde", "O=Cc1ccc(OC)cc1"),
    "2o": ("methyl 4-formylbenzoate", "COC(=O)c1ccc(C=O)cc1"),
    "2p": ("3-methylbenzaldehyde", "O=Cc1cccc(C)c1"),
}

ALLENES_N = {
    "1a": ("N-(3,4-pentadienyl)-4-toluenesulfonamide", "C=C=CCCNS(=O)(=O)c1ccc(C)cc1"),
    "1b": ("N-(3-allyl-3,4-pentadienyl)-4-toluenesulfonamide", "C=C=C(CC=C)CCNS(=O)(=O)c1ccc(C)cc1"),
}

ALLENES_O = {
    "4a": ("3,4-pentadien-1-ol", "C=C=CCCO"),
    "4b": ("3-n-butyl-3,4-pentadien-1-ol", "C=C=C(CCCC)CCO"),
    "4c": ("3-allyl-3,4-pentadien-1-ol", "C=C=C(CC=C)CCO"),
    "4d": ("3-phenyl-3,4-pentadien-1-ol", "C=C=C(c1ccccc1)CCO"),
}

SOLVENTS = {
    "DCM": ("dichloromethane", "ClCCl"),
    "DCE": ("1,2-dichloroethane", "ClCCCl"),
    "toluene": ("toluene", "Cc1ccccc1"),
    "THF": ("tetrahydrofuran", "C1CCOC1"),
}


def allene_n(label, evidence, amounts=None):
    name, smiles = ALLENES_N[label]
    return participant(f"allene_{label}", "reactant", label, evidence, name, smiles, amounts)


def allene_o(label, evidence, amounts=None):
    name, smiles = ALLENES_O[label]
    return participant(f"allene_{label}", "reactant", label, evidence, name, smiles, amounts)


def aldehyde(label, evidence, amounts=None):
    name, smiles = ALDEHYDES[label]
    return participant(f"aldehyde_{label}", "reactant", label, evidence, name, smiles, amounts)


def catalyst(label, evidence, loading):
    names = {
        "FeCl3": ("iron(III) chloride", "Cl[Fe](Cl)Cl"),
        "Fe(acac)3": ("iron(III) acetylacetonate", None),
        "FeSO4·7H2O": ("iron(II) sulfate heptahydrate", None),
    }
    name, smiles = names[label]
    return participant("catalyst_iron", "catalyst", label, evidence, name, smiles,
                       [field("catalyst_loading", q(loading, "mol%"), evidence)])


def tmscl(evidence, equivalents):
    return participant("reagent_tmscl", "reagent", "TMSCl", evidence, "trimethylsilyl chloride",
                       "C[Si](C)(C)Cl", [field("equivalents", q(equivalents, "equiv"), evidence)])


def solvent(label, evidence):
    name, smiles = SOLVENTS[label]
    return participant(f"solvent_{label.lower()}", "solvent", label, evidence, name, smiles)


def product(label, evidence, product_class):
    return participant(f"product_{label}", "product", label, evidence, f"{product_class} {label}")


def common_missing_conditions():
    return [field("atmosphere", None), field("workup", None), field("purification", None)]


records = []

# The graphical abstract summarizes the whole paper; it is not a single experiment.
e1 = ev(1)
records.append(record(
    "graphical_abstract_overview", "general_scheme", [1],
    participants=[
        participant("generic_beta_allene", "reactant", "generic β-sulfonamidoallene or β-allenol", e1),
        participant("generic_aldehyde", "reactant", "R2CHO", e1),
        participant("generic_fecl3", "catalyst", "FeCl3", e1),
        participant("generic_tmscl", "reagent", "TMSCl", e1),
        participant("generic_cyclic_product", "product", "generic 3-chloromethyl heterocycle", e1),
    ],
    notes=["The graphical abstract reports an aggregate 25 examples and 40–95% yield range; these are summary statistics, not one experiment-specific yield."],
    unresolved=["Generic X/R1/R2 groups prevent unique structures and experiment-specific quantities."],
))

# Scheme 1 is explicitly a set of possible pathways.
records.append(record(
    "scheme1_possible_reaction_pathways", "mechanism", [1],
    participants=[
        participant("generic_allene_1", "reactant", "generic allene 1 (X = NTs or O)", e1),
        participant("generic_aldehyde_2", "reactant", "generic aldehyde 2", e1),
        participant("intermediate_int1", "unspecified_agent", "Int-1", e1),
        participant("intermediate_int2", "unspecified_agent", "Int-2", e1),
        participant("generic_product_A", "product", "A-type product", e1),
        participant("generic_product_B", "product", "B-type product", e1),
    ],
    notes=["Scheme 1 is captioned 'Possible Reaction Pathways'; acid-promoted condensation/cyclization and alternative nucleophilic capture products are proposed rather than individually observed here."],
    unresolved=["Intermediates Int-1 and Int-2 are proposed, and generic substituents prevent unique structures or experiment-specific outcomes."],
))


# Table 1: every catalyst/solvent/loading row is an independent optimization experiment.
table1 = [
    (1, "FeCl3", 5, 1.5, "DCM", 10, 24, None, None, None, 1.2),
    (2, "FeCl3", 10, 1.5, "DCM", 9, 54, None, None, None, 1.2),
    (3, "FeCl3", 25, 1.5, "DCM", 8.5, 70, None, None, None, 1.2),
    (4, "FeCl3", 30, 1.5, "DCM", 9, 64, None, None, None, 1.2),
    (5, "FeCl3", 25, 1.5, "DCM", 16, 68, None, None, None, 1.5),
    (6, "FeCl3", 25, 1.0, "DCM", 8, 78, 71, None, None, 1.2),
    (7, "FeCl3", 25, 1.0, "DCE", 10, 59, None, None, None, 1.2),
    (8, "FeCl3", 25, 1.0, "toluene", 10, 15, None, None, None, 1.2),
    (9, "FeCl3", 25, 1.0, "THF", 15.5, "table dash (–)", None, 93, None, 1.2),
    (10, None, None, 1.0, "DCM", 16.5, "table dash (–)", None, 94, None, 1.2),
    (11, "FeCl3", 25, None, "DCM", 16.5, 6, None, 45, None, 1.2),
    (12, "FeCl3", 25, None, "DCM", 23, "table dash (–)", None, None, 11, 1.2),
    (13, "Fe(acac)3", 25, 1.0, "DCM", 10, 33, None, None, None, 1.2),
    (14, "FeSO4·7H2O", 25, 1.0, "DCM", 12, "table dash (–)", None, 84, None, 1.2),
]
for entry, cat, loading, tms_eq, solv, hours, nmr_yield, isolated, recovery, conversion, ald_eq in table1:
    evidence = ev(1, 2)
    parts = [
        allene_n("1a", evidence, [field("reaction_concentration", q(0.1, "M"), ev(2))]),
        aldehyde("2a", evidence, [field("equivalents", q(ald_eq, "equiv"), ev(2))]),
    ]
    if cat is not None:
        parts.append(catalyst(cat, evidence, loading))
    if tms_eq is not None:
        parts.append(tmscl(evidence, tms_eq))
    if entry == 12:
        parts.append(participant("reagent_licl", "reagent", "LiCl", evidence, "lithium chloride",
                                 "[Li+].[Cl-]", [field("equivalents", q(1.0, "equiv"), ev(2))]))
    parts += [solvent(solv, evidence), product("3a", evidence, "3-chloromethyl-1,2,5,6-tetrahydro-1H-pyridine")]
    pid = "product_3a"
    conditions = [field("temperature", q(30, "°C"), ev(2)),
                  field("reaction_time", q(hours, "h"), ev(2)), *common_missing_conditions()]
    if entry == 10:
        conditions.append(field("catalyst_presence", "no Fe catalyst added", ev(1, 2)))
    if entry == 11:
        conditions.append(field("TMSCl_presence", "not added", ev(1, 2)))
    if entry == 12:
        conditions.append(field("TMSCl_presence", "LiCl used instead of TMSCl", ev(2)))
    outcomes = [
        field("1H_NMR_yield_3a", q(nmr_yield, "%") if isinstance(nmr_yield, (int, float)) else nmr_yield,
              ev(2), [pid]),
        field("yield_measurement_basis", "1H NMR analysis with 1,3,5-trimethylbenzene as internal standard", ev(2), [pid]),
    ]
    if isolated is not None:
        outcomes += [field("isolated_yield_3a", q(isolated, "%"), ev(2), [pid]),
                     field("isolated_yield_measurement_basis", "isolated yield", ev(2), [pid])]
    if recovery is not None:
        outcomes.append(field("recovered_starting_material_yield", q(recovery, "%"), ev(2), ["allene_1a"]))
    if conversion is not None:
        outcomes.append(field("conversion", q(conversion, "%"), ev(2), ["allene_1a"]))
    if entry == 10:
        outcomes.append(field("narrative_product_observation", "no product was obtained", ev(1), [pid]))
    if entry == 11:
        outcomes.append(field("narrative_product_observation", "only a trace amount of product was afforded", ev(1), [pid]))
    if entry == 12:
        outcomes.append(field("narrative_reaction_observation", "the reaction did not happen when LiCl was used instead of TMSCl", ev(1), [pid]))
    notes = ["Table 1 dashes are preserved as source markers and are not interpreted as zero or not detected."]
    records.append(record(
        f"table1_entry{entry}", "optimization_entry", [1, 2], parts,
        [step("fe_catalyzed_prins_cyclization", [p["entity_id"] for p in parts if p["role"] != "product"], conditions)],
        outcomes, notes,
        ["Reaction scale, atmosphere, workup, and purification are not reported in the supplied main text.",
         "The product structure and regioselectivity remain machine-unverified.",
         "Supporting Information is mentioned by the paper but no SI file was supplied or explicitly associated."],
    ))


# Table 2: twelve β-sulfonamidoallene scope rows.
table2 = [
    (1, "1a", "2b", 8, 70, "3b"),
    (2, "1a", "2c", 8, 68, "3c"),
    (3, "1a", "2d", 9, 52, "3d"),
    (4, "1a", "2e", 8, 66, "3e"),
    (5, "1a", "2f", 8, 66, "3f"),
    (6, "1a", "2g", 8, 64, "3g"),
    (7, "1a", "2h", 8, 65, "3h"),
    (8, "1a", "2i", 8, 40, "3i"),
    (9, "1a", "2j", 19, 71, "3j"),
    (10, "1a", "2k", 10, 64, "3k"),
    (11, "1a", "2l", 10, 61, "3l"),
    (12, "1b", "2a", 9.5, 60, "3m"),
]
for entry, sub, ald, hours, yld, prod_label in table2:
    pages = [2]
    if entry == 1:
        pages = [1, 2]
    if entry == 5:
        pages = [2, 3]
    if entry in (7, 10):
        pages = [2, 4]
    evidence = ev(*pages)
    ald_eq = 2.0 if entry in (9, 10) else 1.2
    cat_loading = 30 if entry in (9, 10) else 25
    tms_eq = 1.5 if entry in (9, 10) else 1.0
    parts = [
        allene_n(sub, evidence, [field("reaction_concentration", q(0.1, "M"), ev(2))]),
        aldehyde(ald, evidence, [field("equivalents", q(ald_eq, "equiv"), ev(2))]),
        catalyst("FeCl3", evidence, cat_loading), tmscl(evidence, tms_eq), solvent("DCM", evidence),
        product(prod_label, evidence, "3-chloromethyl-1,2,5,6-tetrahydro-1H-pyridine"),
    ]
    pid = f"product_{prod_label}"
    notes = ["Table 2 reports an isolated product yield for this row."]
    if entry == 8:
        notes.append("Table 2 footnote c specifies paraformaldehyde for aldehyde 2i.")
    if entry in (9, 10):
        notes.append("Table 2 footnote d overrides the standard catalyst, aldehyde, and TMSCl loadings for this row.")
    if entry == 5:
        notes.append("The acknowledgments state that Xiaobing Zhang reproduced the result in Table 2 entry 5; no separate run details are reported, so no duplicate experiment record is created.")
    if entry == 7:
        notes.append("Figure 1 and reference note 44 provide X-ray/crystal support for product 3h; this is characterization evidence, not another reaction.")
    if entry == 10:
        notes.append("Figure 1 and reference note 45 provide X-ray/crystal support for product 3k; this is characterization evidence, not another reaction.")
    records.append(record(
        f"table2_entry{entry}", "substrate_scope_entry", pages, parts,
        [step("fecl3_catalyzed_prins_cyclization", [p["entity_id"] for p in parts[:-1]], [
            field("temperature", q(30, "°C"), ev(2)), field("reaction_time", q(hours, "h"), ev(2)),
            *common_missing_conditions(),
        ])],
        [field("isolated_yield", q(yld, "%"), ev(2), [pid]),
         field("yield_measurement_basis", "isolated yield", ev(2), [pid])],
        notes,
        ["Absolute scale, atmosphere, workup, purification, and isolated product mass are not reported in the supplied main text.",
         "The complex product structure remains machine-unverified.",
         "Supporting Information is mentioned by the paper but no SI file was supplied or explicitly associated."],
    ))


# Equation 1 is a distinct gram-scale run, not the same physical experiment as Table 1 entry 6.
e2 = ev(2)
parts = [
    allene_n("1a", e2, [field("mass", q(1.1862, "g"), e2)]),
    aldehyde("2a", e2, [field("equivalents", q(1.2, "equiv"), e2)]),
    catalyst("FeCl3", e2, 25), tmscl(e2, 1.0), solvent("DCM", e2),
    product("3a", e2, "3-chloromethyl-1,2,5,6-tetrahydro-1H-pyridine"),
]
records.append(record(
    "eq1_gram_scale_3a", "reported_experiment", [2], parts,
    [step("gram_scale_prins_cyclization", [p["entity_id"] for p in parts[:-1]], [
        field("temperature", q(30, "°C"), e2), field("reaction_time", q(8, "h"), e2),
        *common_missing_conditions(),
    ])],
    [field("reported_yield_3a", q(65, "%"), e2, ["product_3a"]),
     field("yield_measurement_basis", None, targets=["product_3a"])],
    ["Equation 1 is a distinct 1.1862 g-scale run; it is not merged with the 0.1 M optimization row that reports a different yield."],
    ["Atmosphere, solvent volume, workup, purification, isolated product mass, and yield measurement basis are not reported.",
     "The product structure remains machine-unverified; no SI file was supplied or explicitly associated."],
))


# Table 3: twelve β-allenol scope rows.
table3 = [
    (1, "4a", "2b", 10, 66, "5a"),
    (2, "4a", "2m", 10, 75, "5b"),
    (3, "4a", "2n", 10, 50, "5c"),
    (4, "4a", "2a", 10, 78, "5d"),
    (5, "4a", "2c", 10, 85, "5e"),
    (6, "4a", "2d", 9.3, 75, "5f"),
    (7, "4a", "2o", 24, 83, "5g"),
    (8, "4a", "2p", 10, 74, "5h"),
    (9, "4a", "2h", 10, 72, "5i"),
    (10, "4b", "2a", 2, 95, "5j"),
    (11, "4c", "2a", 2, 94, "5k"),
    (12, "4d", "2a", 3, 76, "5l"),
]
for entry, sub, ald, hours, yld, prod_label in table3:
    pages = [2, 3]
    allene_eq = 2.0 if entry == 12 else 1.5
    cat_loading = 10 if entry in (10, 11, 12) else 5
    tms_eq = 1.0
    evidence = ev(*pages)
    parts = [
        allene_o(sub, evidence, [field("equivalents", q(allene_eq, "equiv"), ev(3))]),
        aldehyde(ald, evidence, [field("reaction_concentration", q(0.1, "M"), ev(3))]),
        catalyst("FeCl3", evidence, cat_loading), tmscl(evidence, tms_eq), solvent("DCM", evidence),
        product(prod_label, evidence, "3-chloromethyl-5,6-dihydro-2H-pyran"),
    ]
    pid = f"product_{prod_label}"
    notes = ["Table 3 reports an isolated product yield for this row."]
    if entry in (10, 11):
        notes.append("Table 3 footnote d overrides the standard conditions; its FeCl3 and TMSCl quantities are represented in the participant amounts.")
    if entry == 12:
        notes.append("Table 3 footnote e specifies FeCl3 at 10 mol% and 4d at 2.0 equiv.")
    if entry in (3, 10):
        notes.append(f"The acknowledgments state that Xiaobing Zhang reproduced the result in Table 3 entry {entry}; no separate run details are reported, so no duplicate experiment record is created.")
    records.append(record(
        f"table3_entry{entry}", "substrate_scope_entry", pages, parts,
        [step("fecl3_catalyzed_prins_cyclization", [p["entity_id"] for p in parts[:-1]], [
            field("temperature", q(40, "°C"), ev(3)), field("reaction_time", q(hours, "h"), ev(3)),
            *common_missing_conditions(),
        ])],
        [field("isolated_yield", q(yld, "%"), ev(3), [pid]),
         field("yield_measurement_basis", "isolated yield", ev(3), [pid])],
        notes,
        ["Absolute scale, atmosphere, workup, purification, and isolated product mass are not reported in the supplied main text.",
         "The complex product structure remains machine-unverified.",
         "Supporting Information is mentioned by the paper but no SI file was supplied or explicitly associated."],
    ))


# Footnote c is printed under Table 3, but no row carries a legible superscript c in the supplied page image.
records.append(record(
    "table3_footnote_c_unassigned", "unresolved", [3],
    participants=[catalyst("FeCl3", ev(3), 10), tmscl(ev(3), 1.5)],
    notes=["Table 3 footnote c states 'FeCl3 (10 mol %) and TMSCl (1.5 equiv) were used in this reaction,' but no table row has a legible c marker in the supplied original image. The override is retained without guessing its target row."],
    unresolved=["The Table 3 row governed by footnote c cannot be assigned from the supplied page image or extracted text."],
))


assert len(records) == 42, len(records)

t1_ids = [f"{DOC}:table1_entry{i}" for i in range(1, 15)]
t2_ids = [f"{DOC}:table2_entry{i}" for i in range(1, 13)]
t3_ids = [f"{DOC}:table3_entry{i}" for i in range(1, 13)]

coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1, "state": "attempted",
            "regions": [
                {"region": "page 1 title, abstract, and graphical abstract reaction arrow", "finding": "Article identity and the aggregate FeCl3/TMSCl reaction summary were inspected. The 25-example/40–95% statement is a general overview, not a unique experimental outcome.", "evidence_ids": ev(1)},
                {"region": "page 1 lower-left Scheme 1", "finding": "Possible reaction pathways through Int-1/Int-2 to A- and B-type products; classified as a mechanism rather than observed preparative experiments.", "evidence_ids": ev(1)},
                {"region": "page 1 lower-right optimization prose", "finding": "Narrative discusses Table 1 entries 1–14 and the start of Table 2; values were linked to the row records on page 2 instead of duplicated.", "evidence_ids": ev(1)},
            ],
            "record_ids": [f"{DOC}:graphical_abstract_overview", f"{DOC}:scheme1_possible_reaction_pathways", *t1_ids, f"{DOC}:table2_entry1"],
            "unresolved": ["The graphical abstract and Scheme 1 use generic R/X groups and do not define unique structures.", "The paper mentions Supporting Information, but no SI file is supplied or explicitly associated."],
        },
        {
            "page": 2, "state": "attempted",
            "regions": [
                {"region": "page 2 upper-left Table 1 drawing, rows 1–14, and footnotes a–j", "finding": "Fourteen distinct optimization rows retained with catalyst/loadings, TMSCl or LiCl, solvent, 30 °C, time, NMR yield or source dash, isolated yield where printed, recovery, and conversion.", "evidence_ids": ev(2)},
                {"region": "page 2 lower-left Table 2 drawing, rows 1–12, and footnotes a–d", "finding": "Twelve distinct β-sulfonamidoallene scope experiments retained with row-specific aldehyde, time, isolated yield, and footnote overrides.", "evidence_ids": ev(2)},
                {"region": "page 2 upper-right Figure 1", "finding": "ORTEP drawings characterize 3h and 3k; they support existing Table 2 entries 7 and 10 and are not additional reactions.", "evidence_ids": ev(2)},
                {"region": "page 2 center-right Equation 1", "finding": "A distinct 1.1862 g-scale 1a/2a reaction gives 3a in 65% after 8 h and was retained separately from optimization rows.", "evidence_ids": ev(2)},
                {"region": "page 2 lower-right Table 3 lead-in prose", "finding": "The β-allenol scope is introduced and continues as Table 3 on page 3; prose was linked as cross-page evidence without creating duplicate rows.", "evidence_ids": ev(2)},
            ],
            "record_ids": [*t1_ids, *t2_ids, f"{DOC}:eq1_gram_scale_3a", *t3_ids],
            "unresolved": ["Table rows omit atmosphere, workup, purification, and isolated product masses.", "Complex product structures remain machine-unverified.", "No SI file was supplied or associated."],
        },
        {
            "page": 3, "state": "attempted",
            "regions": [
                {"region": "page 3 upper-left Table 3 drawing, rows 1–12, and footnotes a–e", "finding": "Twelve distinct β-allenol scope experiments retained with aldehyde concentration, allenol equivalents, catalyst/TMSCl loadings, 40 °C, time, and isolated yield. Footnotes d/e were assigned to marked rows; footnote c has no legible row marker and is preserved as unresolved.", "evidence_ids": ev(3)},
                {"region": "page 3 lower-left conclusion and Associated Content", "finding": "Conclusion summarizes the reaction; the SI statement advertises procedures and spectra but does not establish an associated SI file in this workspace.", "evidence_ids": ev(3)},
                {"region": "page 3 top-right acknowledgments continuation", "finding": "Table 2 entry 5 and Table 3 entries 3 and 10 were reproduced by Xiaobing Zhang. This is attached as context to existing records, not counted as separate fully specified experiments.", "evidence_ids": ev(3)},
                {"region": "page 3 right-column references", "finding": "Bibliographic references are prior literature and were not expanded into current-paper reaction records.", "evidence_ids": ev(3)},
            ],
            "record_ids": [*t3_ids, f"{DOC}:table3_footnote_c_unassigned", f"{DOC}:table2_entry5"],
            "unresolved": ["The target row for Table 3 footnote c cannot be assigned from the original image or extracted text.", "SI-only procedures and spectra remain unavailable and unassociated."],
        },
        {
            "page": 4, "state": "attempted",
            "regions": [
                {"region": "page 4 full page references 39–47", "finding": "The page contains bibliography and crystal-data notes only; cited external papers were not converted into experiments of this paper.", "evidence_ids": ev(4)},
                {"region": "page 4 crystal-data notes 44–45", "finding": "CCDC/crystal metadata for 3h and 3k supports product characterization for Table 2 entries 7 and 10; it is not a preparative reaction outcome.", "evidence_ids": ev(4)},
            ],
            "record_ids": [f"{DOC}:table2_entry7", f"{DOC}:table2_entry10"],
            "unresolved": ["External CCDC deposits and cited papers are outside the supplied experiment evidence and were not imported."],
        },
    ],
}

RAW.parent.mkdir(parents=True, exist_ok=True)
COVERAGE.parent.mkdir(parents=True, exist_ok=True)
RAW.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
COVERAGE.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

tasks = json.loads(TASKS.read_text())
for item in tasks:
    if item.get("document_id") == DOC and item.get("task_id", "").endswith(":text"):
        page = int(item["task_id"].split(":page", 1)[1].split(":", 1)[0])
        if 1 <= page <= 4:
            item["state"] = "attempted"
            item["reason"] = "Original page image and extracted text inspected; coverage ledger records tables, arrows, footnotes, classifications, and unresolved details."
TASKS.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"records": len(records), "raw": str(RAW), "coverage": str(COVERAGE)}, ensure_ascii=False))
