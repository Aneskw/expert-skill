#!/usr/bin/env python3
"""Build evidence-linked machine records for source PDF pages 1-4."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "runs/current/raw_model/extracted_records_pages_0001_0004.json"
COVERAGE = ROOT / "runs/current/coverage/pages_0001_0004.json"
DOC = "doc_b02fb24bcce9d4ad"


def ev(page):
    return [f"{DOC}:page{page}:image", f"{DOC}:page{page}:text"]


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


def participant(entity_id, role, label, name, evidence, smiles=None, amounts=None):
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


def record(rid, kind, evidence, participants, conditions, outcomes, unresolved, notes=None):
    return {
        "record_id": f"{DOC}:{rid}",
        "document_id": DOC,
        "source_reaction_id": rid,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": evidence,
        "participants": participants,
        "steps": [{
            "step_id": "step1",
            "participant_ids": [p["entity_id"] for p in participants],
            "conditions": conditions,
        }],
        "outcomes": outcomes,
        "notes": [fact(n, evidence) for n in (notes or [])],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved,
        },
    }


SMILES = {
    "1a": "C=C=CC(O)c1ccccc1",
    "1b": "C=C=CC(O)c1ccc(OC)cc1",
    "1c": "C=C=CC(O)c1ccccc1Cl",
    "1e": "C=C=C(CCCC)C(O)c1ccccc1",
    "1f": "C=C=CC(O)(c1ccccc1)c1ccccc1",
    "1g": "C=C=CC(O)CCCC",
    "3a": "C=C(Br)/C=C/c1ccccc1",
    "3b": "C=C(Cl)/C=C/c1ccccc1",
    "3c": "C=C(Br)/C=C/c1ccc(OC)cc1",
    "3d": "C=C(Cl)/C=C/c1ccc(OC)cc1",
    "3e": "C=C(Br)/C=C/c1ccccc1Cl",
    "3f": "C=C(Cl)/C=C/c1ccccc1Cl",
    "LiBr": "[Li+].[Br-]",
    "LiCl": "[Li+].[Cl-]",
    "HQ": "Oc1ccc(O)cc1",
    "AcOH": "CC(=O)O",
    "MeCN": "CC#N",
    "BQ": "O=C1C=CC(=O)C=C1",
    "NQ": "O=C1C=CC2=CC=CC=C2C1=O",
    "benzene": "c1ccccc1",
    "PdOAc": "CC(=O)[O-].CC(=O)[O-].[Pd+2]",
    "PdCl2MeCN": "CC#N.CC#N.Cl[Pd]Cl",
    "PdCl2PPh3": "Cl[Pd](Cl)(P(c1ccccc1)(c1ccccc1)c1ccccc1)P(c1ccccc1)(c1ccccc1)c1ccccc1",
    "DDQ": "N#CC1=C(Cl)C(=O)C(Cl)=C(C#N)C1=O",
}


records = []


def p1a(e):
    return participant("reactant_1a", "reactant", "1a", "1-phenyl-2,3-butadien-1-ol", e, SMILES["1a"])


def lix(e, halide="Br", hydrate=False, equiv=None):
    label = f"Li{halide}" + ("·H2O" if hydrate else "")
    amounts = [field("equivalents", {"number": equiv, "unit": "equiv"}, e)] if equiv is not None else []
    return participant("lithium_halide", "reagent", label, f"lithium {('bromide' if halide == 'Br' else 'chloride')}" + (" monohydrate" if hydrate else ""), e, SMILES[f"Li{halide}"], amounts)


def solvent_acoh(e):
    return participant("solvent_acoh", "solvent", "AcOH", "acetic acid", e, SMILES["AcOH"])


def hq(e, loading=20):
    amounts = [field("loading", {"number": loading, "unit": "mol%"}, e)] if loading is not None else []
    return participant("hydroquinone", "reagent", "HQ", "hydroquinone", e, SMILES["HQ"], amounts)


# Page-1 exploratory one-pot catalyst variants. The product structure is left unresolved
# because Figure 1 and Eq. (1) need independent source review for bromine substitution.
e = ev(1)
for suffix, catalyst_label, catalyst_name, catalyst_smiles, catalyst_present in [
    ("exploratory_pdoac2", "Pd(OAc)2", "palladium(II) acetate", SMILES["PdOAc"], True),
    ("exploratory_pdcl2_mecn", "PdCl2(CH3CN)2", "bis(acetonitrile)palladium(II) dichloride", SMILES["PdCl2MeCN"], True),
    ("exploratory_pdcl2_pph3", "PdCl2(PPh3)2", "bis(triphenylphosphine)palladium(II) dichloride", SMILES["PdCl2PPh3"], True),
    ("exploratory_no_pd", None, None, None, False),
]:
    parts = [
        p1a(e), lix(e, "Br", False, 5),
        participant("benzoquinone", "reactant", "benzoquinone", "1,4-benzoquinone", e, SMILES["BQ"], [field("equivalents", {"number": 2.5, "unit": "equiv"}, e)]),
        solvent_acoh(e),
    ]
    if catalyst_present:
        parts.append(participant("pd_catalyst", "catalyst", catalyst_label, catalyst_name, e, catalyst_smiles, [field("catalyst_loading", {"number": 5, "unit": "mol%"}, e)]))
    parts.append(participant("product_2a", "product", "2a", "Diels–Alder adduct 2a", e))
    records.append(record(
        suffix, "optimization_entry", e, parts,
        [field("solvent", "HOAc", e), field("temperature", None, []), field("time", None, [])],
        [field("product_formation", "formed", e, ["product_2a"]), field("yield", None, [], ["product_2a"])],
        ["Reaction time and temperature are not reported in this paragraph.", "Yield and yield measurement basis are not reported.", "Product 2a candidate structure requires independent visual review.", "Workup, purification, and atmosphere are not reported; no SI was supplied."],
        ["For catalyst substitutions and the no-Pd case, 'the same product 2a' is explicitly reported; the surrounding reaction mixture is treated as the compared condition set."],
    ))


# Scheme 1: three independent condition rows. The 76% row is also Table 1 entry 1.
e12 = ev(1) + ev(2)
parts = [p1a(e12), lix(e12, "Br", True, 3), solvent_acoh(e12), participant("solvent_mecn", "solvent", "CH3CN", "acetonitrile", e12, SMILES["MeCN"]), participant("product_3a", "product", "3a", "1-phenyl-3-bromo-1(E),3-butadiene", e12, SMILES["3a"])]
records.append(record(
    "scheme1_acoh_mecn_complicated", "optimization_entry", e12, parts,
    [field("solvent", "AcOH/CH3CN", e12), field("solvent_ratio", "1:19", e12), field("temperature", "reflux", e12), field("time", {"number": 10, "unit": "h"}, e12)],
    [field("reaction_result", "complicated", e12, ["product_3a"]), field("yield", None, [], ["product_3a"])],
    ["The source reports a complicated reaction and no product-specific yield.", "Reflux temperature, workup, purification, atmosphere, and yield basis are not reported."],
))

parts = [p1a(e12), lix(e12, "Br", True, 3), solvent_acoh(e12), participant("product_3a", "product", "3a", "1-phenyl-3-bromo-1(E),3-butadiene", e12, SMILES["3a"])]
records.append(record(
    "scheme1_acoh_70pct", "optimization_entry", e12, parts,
    [field("solvent", "AcOH", e12), field("temperature", {"number": 50, "unit": "°C"}, e12), field("time", {"number": 1, "unit": "h"}, e12)],
    [field("yield", {"number": 70, "unit": "%"}, e12, ["product_3a"]), field("yield_measurement_basis", None, [], ["product_3a"])],
    ["Yield measurement basis, workup, purification, atmosphere, and substrate scale are not reported."],
))

e123 = ev(1) + ev(2) + ev(3)
parts = [p1a(e123), lix(e123, "Br", True, 3), hq(e123, 20), solvent_acoh(e123), participant("product_3a", "product", "3a", "1-phenyl-3-bromo-1(E),3-butadiene", e123, SMILES["3a"])]
records.append(record(
    "table1_entry1_scheme1_standard", "substrate_scope_entry", e123, parts,
    [field("solvent", "AcOH", e123), field("temperature", {"number": 50, "unit": "°C"}, e123), field("time", {"number": 40, "unit": "min"}, e123)],
    [field("yield", {"number": 76, "unit": "%"}, e123, ["product_3a"]), field("yield_measurement_basis", None, [], ["product_3a"])],
    ["Yield measurement basis, workup, purification, atmosphere, and substrate scale are not reported."],
    ["This record merges the same 1a/LiBr·H2O/HQ/AcOH/50 °C/40 min/76% experiment shown in Scheme 1 and Table 1 entry 1."],
))


# Table 1 entries 2-8. Shared headers supply AcOH, 20 mol% HQ, and 50 °C.
table_rows = [
    (2, "1a", "Ph", "Br", False, 2, "h", 60, "3b", "1-phenyl-3-chloro-1,3-butadiene", SMILES["1a"], SMILES["3b"]),
    (3, "1b", "p-CH3OC6H4", "Br", False, 2, "h", 33, "3c", "1-(4-methoxyphenyl)-3-bromo-1,3-butadiene", SMILES["1b"], SMILES["3c"]),
    (4, "1b", "p-CH3OC6H4", "Cl", False, 2, "h", 53, "3d", "1-(4-methoxyphenyl)-3-chloro-1,3-butadiene", SMILES["1b"], SMILES["3d"]),
    (5, "1c", "o-ClC6H4", "Br", True, 1.5, "h", 82, "3e", "1-(2-chlorophenyl)-3-bromo-1,3-butadiene", SMILES["1c"], SMILES["3e"]),
    (6, "1c", "o-ClC6H4", "Cl", False, 1.5, "h", 60, "3f", "1-(2-chlorophenyl)-3-chloro-1,3-butadiene", SMILES["1c"], SMILES["3f"]),
    (7, "1d", "Naphthyl", "Br", True, 0.5, "h", 81, "3g", "naphthyl-substituted 3-bromo-1,3-butadiene 3g", None, None),
    (8, "1d", "Naphthyl", "Cl", True, 0.5, "h", 88, "3h", "naphthyl-substituted 3-chloro-1,3-butadiene 3h", None, None),
]
e = ev(3)
for entry, sublabel, ar, halide, hydrate, tnum, tunit, yld, prodlabel, prodname, subsmiles, prodsmiles in table_rows:
    substrate = participant("substrate", "reactant", sublabel, f"1-{ar}-2,3-butadien-1-ol" if ar != "Naphthyl" else "naphthyl-substituted 2,3-butadien-1-ol", e, subsmiles)
    product = participant("product", "product", prodlabel, prodname, e, prodsmiles)
    parts = [substrate, lix(e, halide, hydrate), hq(e, 20), solvent_acoh(e), product]
    unresolved = ["LiX equivalents, yield measurement basis, workup, purification, atmosphere, and substrate scale are not reported in Table 1."]
    if entry in (7, 8):
        unresolved.append("The naphthyl positional isomer is not specified in the table; substrate and product SMILES remain null.")
    records.append(record(
        f"table1_entry{entry}", "substrate_scope_entry", e, parts,
        [field("solvent", "AcOH", e), field("temperature", {"number": 50, "unit": "°C"}, e), field("time", {"number": tnum, "unit": tunit}, e)],
        [field("yield", {"number": yld, "unit": "%"}, e, ["product"]), field("yield_measurement_basis", None, [], ["product"])],
        unresolved,
    ))


# Equation (1): optimized benzoquinone one-pot process.
e = ev(2)
parts = [
    p1a(e), lix(e, "Br", False, 3),
    participant("benzoquinone", "reactant", "benzoquinone", "1,4-benzoquinone", e, SMILES["BQ"], [field("equivalents", {"number": 2.2, "unit": "equiv"}, e)]),
    solvent_acoh(e), participant("product_2a", "product", "2a", "Diels–Alder adduct 2a", e),
]
records.append(record(
    "equation1_benzoquinone_optimized", "optimization_entry", e, parts,
    [field("solvent", "HOAc", e), field("temperature", "r.t.", e), field("operation", "dark", e), field("time", {"number": 48, "unit": "h"}, e)],
    [field("yield", {"number": 51, "unit": "%"}, e, ["product_2a"]), field("yield_measurement_basis", None, [], ["product_2a"])],
    ["Exact room temperature, yield measurement basis, workup, purification, atmosphere, and substrate scale are not reported.", "Product 2a candidate structure requires independent visual review."],
))


# Scheme 2: two halide scope rows producing E/Z mixtures.
e23 = ev(2) + ev(3)
for halide, tnum, yld, ratio, ratio_label, prodlabel in [
    ("Br", 3.0, 87, "1.4:1", "Z/E", "3i"),
    ("Cl", 3.5, 73, "5.2:1", "E/Z", "3j"),
]:
    parts = [
        participant("substrate_1e", "reactant", "1e", "2-(n-butyl)-1-phenyl-2,3-butadien-1-ol", e23, SMILES["1e"]),
        lix(e23, halide, True, 3), hq(e23, None), solvent_acoh(e23),
        participant("product_mixture", "product", prodlabel, f"E/Z mixture of 3-{('bromo' if halide == 'Br' else 'chloro')}-1-phenyl-2-(n-butyl)-1,3-butadienes", e23),
    ]
    records.append(record(
        f"scheme2_{halide.lower()}", "substrate_scope_entry", e23, parts,
        [field("solvent", "HOAc", e23), field("temperature", {"number": 50, "unit": "°C"}, e23), field("time", {"number": tnum, "unit": "h"}, e23)],
        [field("yield", {"number": yld, "unit": "%"}, e23, ["product_mixture"]), field(f"{ratio_label}_ratio", ratio, e23, ["product_mixture"]), field("yield_measurement_basis", None, [], ["product_mixture"])],
        ["Hydroquinone amount, yield measurement basis, workup, purification, atmosphere, and substrate scale are not reported on the Scheme 2 arrow.", "The product is an E/Z mixture; a single stereochemical SMILES is not assigned."],
    ))


# Scheme 3: tertiary allenol scope.
e23 = ev(2) + ev(3)
for halide, yld, prodlabel in [("Br", 90, "3k"), ("Cl", 85, "3l")]:
    parts = [
        participant("substrate_1f", "reactant", "1f", "1,1-diphenyl-2,3-butadien-1-ol", e23, SMILES["1f"]),
        lix(e23, halide, True, 3), hq(e23, 20), solvent_acoh(e23),
        participant("product", "product", prodlabel, f"diphenyl-substituted 3-{('bromo' if halide == 'Br' else 'chloro')}-1,3-butadiene {prodlabel}", e23),
    ]
    records.append(record(
        f"scheme3_{halide.lower()}", "substrate_scope_entry", e23, parts,
        [field("solvent", "AcOH", e23), field("temperature", {"number": 50, "unit": "°C"}, e23), field("time", {"number": 40, "unit": "min"}, e23)],
        [field("yield", {"number": yld, "unit": "%"}, e23, ["product"]), field("yield_measurement_basis", None, [], ["product"])],
        ["Yield measurement basis, workup, purification, atmosphere, and substrate scale are not reported.", "Product candidate structure is not encoded pending independent review of alkene geometry."],
    ))


# Scheme 4: two explicitly unsuccessful substrate tests. Conditions are not printed.
e23 = ev(2) + ev(3)
for label, name, smiles, expected_name in [
    ("1g", "1-(n-butyl)-2,3-butadien-1-ol", SMILES["1g"], "expected n-butyl-substituted 3-bromo-1,3-butadiene"),
    ("1h", "1-(perfluorooctyl)-2,3-butadien-1-ol", None, "expected perfluorooctyl-substituted 3-bromo-1,3-butadiene"),
]:
    parts = [
        participant("substrate", "reactant", label, name, e23, smiles),
        lix(e23, "Br", False),
        participant("expected_product", "product", "expected product (not formed)", expected_name, e23),
    ]
    unresolved = ["Scheme 4 does not print temperature, time, solvent, reagent amount, or analytical detection limit.", "Workup, atmosphere, and substrate scale are not reported.", "The expected product SMILES is not assigned pending independent structural review."]
    if label == "1h":
        unresolved.append("The perfluorooctyl substrate SMILES is left null to avoid guessing chain connectivity from the compact label.")
    records.append(record(
        f"scheme4_{label}_not_formed", "substrate_scope_entry", e23, parts,
        [field("temperature", None, []), field("time", None, []), field("solvent", None, [])],
        [field("product_formation", "not formed", e23, ["expected_product"]), field("yield", None, [], ["expected_product"])],
        unresolved,
    ))


# Scheme 5: two naphthoquinone one-pot condition rows.
e = ev(3)
for suffix, temp, dark, time_h, yld in [
    ("40c", {"number": 40, "unit": "°C"}, None, 42, 53),
    ("dark_rt", "r.t.", "dark", 48, 72),
]:
    parts = [
        p1a(e), lix(e, "Br", False, 3),
        participant("naphthoquinone", "reactant", "naphthoquinone", "1,4-naphthoquinone", e, SMILES["NQ"]),
        solvent_acoh(e), participant("product_2b", "product", "2b", "Diels–Alder adduct 2b", e),
    ]
    conditions = [field("solvent", "AcOH", e), field("temperature", temp, e), field("time", {"number": time_h, "unit": "h"}, e)]
    if dark:
        conditions.append(field("operation", dark, e))
    records.append(record(
        f"scheme5_{suffix}", "optimization_entry", e, parts, conditions,
        [field("yield", {"number": yld, "unit": "%"}, e, ["product_2b"]), field("yield_measurement_basis", None, [], ["product_2b"])],
        ["Naphthoquinone amount, exact room temperature where applicable, yield measurement basis, workup, purification, atmosphere, and substrate scale are not reported.", "Product 2b candidate structure requires independent visual review."],
    ))


# Equation (2): oxidation of 2a to 2a'.
e = ev(3)
parts = [
    participant("reactant_2a", "reactant", "2a", "Diels–Alder adduct 2a", e),
    participant("ddq", "reagent", "DDQ", "2,3-dichloro-5,6-dicyano-1,4-benzoquinone", e, SMILES["DDQ"], [field("equivalents", {"number": 2, "unit": "equiv"}, e)]),
    participant("solvent_benzene", "solvent", "benzene", "benzene", e, SMILES["benzene"]),
    participant("product_2a_prime", "product", "2a′", "oxidized naphthoquinone derivative 2a′", e),
]
records.append(record(
    "equation2_ddq_oxidation", "reported_experiment", e, parts,
    [field("solvent", "benzene", e), field("temperature", "reflux", e), field("time", None, [])],
    [field("yield", {"number": 87, "unit": "%"}, e, ["product_2a_prime"]), field("yield_measurement_basis", None, [], ["product_2a_prime"])],
    ["Reaction time, benzene volume, reflux temperature, yield measurement basis, workup, purification, atmosphere, and substrate scale are not reported.", "Structures 2a and 2a′ require independent visual review and retain null SMILES."],
))


assert len(records) == 24, len(records)
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")


def ids(*suffixes):
    return [f"{DOC}:{x}" for x in suffixes]


coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1,
            "state": "attempted",
            "regions": [
                {"region": "title, abstract, and bibliographic header", "finding": "Article-level summary of LiX addition–elimination and quinone applications; no individual experiment created from the abstract.", "evidence_ids": [f"{DOC}:page1:image"]},
                {"region": "left-column introduction and prior-work discussion", "finding": "Prior literature and authors' earlier work are contextual citations, not experiments newly reported in this paper.", "evidence_ids": [f"{DOC}:page1:image"]},
                {"region": "left-column lower paragraph beginning with mixture of 1a", "finding": "Exploratory 1a/LiBr/benzoquinone/Pd(OAc)2 reaction producing 2a; yield, time, and temperature absent.", "evidence_ids": [f"{DOC}:page1:image"]},
                {"region": "right-column catalyst comparison paragraph", "finding": "Two alternative 5 mol% Pd catalysts and a no-Pd comparison each report the same product 2a; retained as separate optimization entries.", "evidence_ids": [f"{DOC}:page1:image"]},
                {"region": "right-column diene-isolation paragraphs", "finding": "AcOH/CH3CN complicated result, 70% AcOH result, and 76% hydroquinone-enhanced result correspond to Scheme 1 rows on page 2; the 76% result also matches Table 1 entry 1 on page 3.", "evidence_ids": [f"{DOC}:page1:image"]},
            ],
            "record_ids": ids("exploratory_pdoac2", "exploratory_pdcl2_mecn", "exploratory_pdcl2_pph3", "exploratory_no_pd", "scheme1_acoh_mecn_complicated", "scheme1_acoh_70pct", "table1_entry1_scheme1_standard"),
            "unresolved": ["The exploratory catalyst variants lack reported time, temperature, and yields.", "The exact structure/halogen count of product 2a should be independently checked against the figure and original experimental data.", "No supporting information was supplied or explicitly associated."],
        },
        {
            "page": 2,
            "state": "attempted",
            "regions": [
                {"region": "Figure 1, structures 1a/2a/3a and ORTEP", "finding": "Structure-identification context only; no new experiment. It supports labels but does not independently establish the exploratory reaction conditions.", "evidence_ids": [f"{DOC}:page2:image"]},
                {"region": "Scheme 1 three condition rows", "finding": "Three independent optimization results: complicated AcOH/CH3CN reflux, 70% in AcOH, and 76% with 20 mol% HQ. The last is merged with Table 1 entry 1.", "evidence_ids": [f"{DOC}:page2:image"]},
                {"region": "Scheme 2 and Scheme 3 prose", "finding": "Cross-page descriptions of E/Z mixtures from 1e and tertiary-alcohol 1f scope; detailed rows occur on page 3 and share records with that page.", "evidence_ids": [f"{DOC}:page2:image"]},
                {"region": "right-column no-reaction and mechanism paragraphs", "finding": "1g and 1h are explicitly said not to yield expected products; the proposed SN2′-type pathway is mechanistic interpretation, not a separate experiment.", "evidence_ids": [f"{DOC}:page2:image"]},
                {"region": "Equation (1)", "finding": "One-pot 1a/LiBr/benzoquinone experiment in HOAc at room temperature in the dark for 48 h, affording 2a in 51% yield.", "evidence_ids": [f"{DOC}:page2:image"]},
            ],
            "record_ids": ids("scheme1_acoh_mecn_complicated", "scheme1_acoh_70pct", "table1_entry1_scheme1_standard", "equation1_benzoquinone_optimized", "scheme2_br", "scheme2_cl", "scheme3_br", "scheme3_cl", "scheme4_1g_not_formed", "scheme4_1h_not_formed"),
            "unresolved": ["Figure 1 product 2a needs independent structural encoding review.", "Scheme 2 hydroquinone loading is not printed with the arrow.", "Scheme 4 experimental conditions are not printed."],
        },
        {
            "page": 3,
            "state": "attempted",
            "regions": [
                {"region": "Table 1 header and entries 1-8", "finding": "Eight substrate-scope rows were read individually; entry 1 is the same standard 76% experiment as Scheme 1 and is not duplicated.", "evidence_ids": [f"{DOC}:page3:image"]},
                {"region": "Scheme 2", "finding": "Two independent 1e reactions: bromide gives 3i in 87% with Z/E 1.4:1; chloride gives 3j in 73% with E/Z 5.2:1.", "evidence_ids": [f"{DOC}:page3:image"]},
                {"region": "Scheme 3", "finding": "Two independent tertiary-allenol 1f scope rows: bromide 3k 90% and chloride 3l 85%, each at 50 °C for 40 min.", "evidence_ids": [f"{DOC}:page3:image"]},
                {"region": "Equation (2)", "finding": "DDQ oxidation of 2a in refluxing benzene gives 2a′ in 87%; time and yield basis are absent.", "evidence_ids": [f"{DOC}:page3:image"]},
                {"region": "Scheme 4", "finding": "Two failed substrate tests (1g and 1h with LiBr); expected bromo-dienes are explicitly marked not formed.", "evidence_ids": [f"{DOC}:page3:image"]},
                {"region": "Scheme 5", "finding": "Two naphthoquinone one-pot condition rows: 40 °C/42 h/53% and dark room temperature/48 h/72%.", "evidence_ids": [f"{DOC}:page3:image"]},
                {"region": "conclusion paragraph", "finding": "Summary of the reported chemistry; no additional experiment beyond the schemes and table.", "evidence_ids": [f"{DOC}:page3:image"]},
            ],
            "record_ids": ids("table1_entry1_scheme1_standard", "table1_entry2", "table1_entry3", "table1_entry4", "table1_entry5", "table1_entry6", "table1_entry7", "table1_entry8", "scheme2_br", "scheme2_cl", "scheme3_br", "scheme3_cl", "equation2_ddq_oxidation", "scheme4_1g_not_formed", "scheme4_1h_not_formed", "scheme5_40c", "scheme5_dark_rt"),
            "unresolved": ["Table 1 does not state LiX equivalents or yield measurement basis.", "The naphthyl positional isomer in entries 7-8 is unspecified in the table.", "Product structures 2a, 2a′, and 2b remain unencoded pending independent structural review."],
        },
        {
            "page": 4,
            "state": "attempted",
            "regions": [
                {"region": "acknowledgements", "finding": "Funding and award acknowledgements; no reaction experiment.", "evidence_ids": [f"{DOC}:page4:image"]},
                {"region": "references 1-13", "finding": "Bibliographic references and descriptions of prior literature only; no experiment newly reported in this paper.", "evidence_ids": [f"{DOC}:page4:image"]},
            ],
            "record_ids": [],
            "unresolved": ["No experimental procedures or supporting information are present on this page."],
        },
    ],
}

COVERAGE.parent.mkdir(parents=True, exist_ok=True)
COVERAGE.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"records": len(records), "raw": str(OUT), "coverage": str(COVERAGE)}, ensure_ascii=False))
