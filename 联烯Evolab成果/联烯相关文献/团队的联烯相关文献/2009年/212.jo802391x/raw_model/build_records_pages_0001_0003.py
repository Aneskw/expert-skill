#!/usr/bin/env python3
"""Build source-faithful machine records for jo802391x, PDF pages 1--3."""
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).with_name("records_pages_0001_0003.json")
COVERAGE = ROOT / "coverage" / "pages_0001_0003.json"
TASKS = ROOT / "tasks.json"
DOC = "doc_c62993ac39784a43"
P1T, P1I = f"{DOC}:page1:text", f"{DOC}:page1:image"
P2T, P2I = f"{DOC}:page2:text", f"{DOC}:page2:image"
P3T, P3I = f"{DOC}:page3:text", f"{DOC}:page3:image"


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


def amount(name, number, unit, evidence, raw_text=None):
    value = {"number": number, "unit": unit}
    if raw_text:
        value["raw_text"] = raw_text
    return field(name, value, evidence)


def participant(entity_id, role, label, name, smiles, evidence, amounts=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence) if name else fact(None, ()),
        "smiles": fact(smiles, evidence) if smiles else fact(None, ()),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": amounts or [],
    }


def record(suffix, kind, evidence, participants, conditions, outcomes, notes=None, unresolved=None):
    return {
        "record_id": f"{DOC}:{suffix}",
        "document_id": DOC,
        "source_reaction_id": suffix,
        "record_kind": kind,
        "status": "needs_review",
        "completeness": "partial",
        "evidence_ids": list(dict.fromkeys(evidence)),
        "participants": participants,
        "steps": [{
            "step_id": "reaction",
            "participant_ids": [p["entity_id"] for p in participants],
            "conditions": conditions,
        }],
        "outcomes": outcomes,
        "notes": [fact(x, evidence) for x in (notes or [])],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved or [],
        },
    }


substrates = {
    "1a": ("dec-1-yne", "C#CCCCCCCCC"),
    "1b": ("dodec-1-yne", "C#CCCCCCCCCCC"),
    "1c": ("4-ethynylbiphenyl", "C#Cc1ccc(-c2ccccc2)cc1"),
    "1d": ("1d; MsO(CH2)7C≡CH", "C#CCCCCCCCOS(=O)(=O)C"),
    "1e": ("benzyl propargyl ether", "C#CCOCc1ccccc1"),
    "1f": ("1f; p-O2NC6H4CH2OCH2C≡CH", "C#CCOCc1ccc([N+](=O)[O-])cc1"),
    "1g": ("1-(4-ethylphenyl)pent-4-yn-1-ol", "C#CCC(O)c1ccc(CC)cc1"),
    "1h": ("1-(4-chlorophenyl)pent-4-yn-1-ol", "C#CCC(O)c1ccc(Cl)cc1"),
    "1i": ("1-(2-chlorophenyl)pent-4-yn-1-ol", "C#CCC(O)c1ccccc1Cl"),
    "1j": ("1-(4-bromophenyl)pent-4-yn-1-ol", "C#CCC(O)c1ccc(Br)cc1"),
    "1k": ("1k; HOCH2C(Me)2NTsCH2C≡CH", "C#CCN(S(=O)(=O)c1ccc(C)cc1)C(C)(C)CO"),
}
products = {
    "2a": ("undeca-1,2-diene", "C=C=CCCCCCCCC"),
    "2b": ("trideca-1,2-diene", "C=C=CCCCCCCCCCC"),
    "2c": ("2c; biphenyl-substituted terminal allene", "C=C=Cc1ccc(-c2ccccc2)cc1"),
    "2d": ("2d; mesylate-functionalized terminal allene", "C=C=CCCCCCCCOS(=O)(=O)C"),
    "2e": ("benzyl 2,3-butadienyl ether", "C=C=CCOCc1ccccc1"),
    "2f": ("2f; p-nitrobenzyl 2,3-butadienyl ether", "C=C=CCOCc1ccc([N+](=O)[O-])cc1"),
    "2g": ("1-(4-ethylphenyl)penta-3,4-dien-1-ol", "C=C=CCC(O)c1ccc(CC)cc1"),
    "2h": ("1-(4-chlorophenyl)penta-3,4-dien-1-ol", "C=C=CCC(O)c1ccc(Cl)cc1"),
    "2i": ("1-(2-chlorophenyl)penta-3,4-dien-1-ol", "C=C=CCC(O)c1ccccc1Cl"),
    "2j": ("1-(4-bromophenyl)penta-3,4-dien-1-ol", "C=C=CCC(O)c1ccc(Br)cc1"),
    "2k": ("2k; hydroxytosylamide-functionalized terminal allene", "C=C=CCN(S(=O)(=O)c1ccc(C)cc1)C(C)(C)CO"),
}


def p_sub(label, evidence, quantities=None):
    name, smiles = substrates[label]
    return participant("substrate", "reactant", label, name, smiles, evidence, quantities)


def p_prod(label, evidence):
    name, smiles = products[label]
    return participant("product", "product", label, name, smiles, evidence)


def p_para(evidence, quantities=None):
    return participant("paraformaldehyde", "reagent", "(CH2O)n", "paraformaldehyde", None, evidence, quantities)


def p_cui(evidence, quantities=None):
    return participant("copper_salt", "catalyst", "CuI", "copper(I) iodide", "[Cu]I", evidence, quantities)


def p_cubr(evidence, quantities=None):
    return participant("copper_salt", "catalyst", "CuBr", "copper(I) bromide", "[Cu]Br", evidence, quantities)


def p_amine(label, name, smiles, evidence, quantities=None):
    return participant("amine", "reagent", label, name, smiles, evidence, quantities)


def p_dioxane(evidence, quantities=None):
    return participant("dioxane", "solvent", "dioxane", "1,4-dioxane", "O1CCOCC1", evidence, quantities)


records = []

# The page-1 graphical abstract is a generic transformation, not a completed run.
ev1 = [P1I, P1T]
records.append(record(
    "graphical_abstract_general_transformation", "general_scheme", ev1,
    [
        participant("generic_alkyne", "reactant", "HC≡C–R1", "generic terminal 1-alkyne", None, ev1),
        p_para(ev1, [amount("equivalents", 2.5, "equiv", ev1)]),
        p_amine("Cy2NH", "dicyclohexylamine", "C1CCCCC1NC1CCCCC1", ev1,
                [amount("equivalents", 1.8, "equiv", ev1)]),
        p_cui(ev1, [amount("equivalents", 0.5, "equiv", ev1)]),
        p_dioxane(ev1),
        participant("generic_allene", "product", "CH2=C=CH–R1", "generic terminal allene", None, ev1),
    ],
    [field("temperature", "reflux", ev1)], [],
    notes=["Generic R1 transformation shown in the graphical abstract; no batch-specific yield is stated."],
    unresolved=["R1 is generic, so complete substrate and product structures are unavailable.",
                "Time, scale, atmosphere, workup, purification, and yield are not stated in the generic diagram."],
))

# Table 1: eight independent optimization experiments.
table1 = [
    (1, "i-Pr2NH", "diisopropylamine", "CC(C)NC(C)C", 1.8, "CuBr", 0.5, 33),
    (2, "Cy2NH", "dicyclohexylamine", "C1CCCCC1NC1CCCCC1", 1.8, "CuBr", 0.5, 43),
    (3, "Cy2NH", "dicyclohexylamine", "C1CCCCC1NC1CCCCC1", 1.8, "CuCl", 0.5, 26),
    (4, "Cy2NH", "dicyclohexylamine", "C1CCCCC1NC1CCCCC1", 1.8, "CuI", 0.5, 59),
    (5, "Cy2NH", "dicyclohexylamine", "C1CCCCC1NC1CCCCC1", 1.8, "CuI", 0.2, 36),
    (6, "Cy2NH", "dicyclohexylamine", "C1CCCCC1NC1CCCCC1", 1.8, "CuI", 0.8, 54),
    (7, "Cy2NH", "dicyclohexylamine", "C1CCCCC1NC1CCCCC1", 1.5, "CuI", 0.5, 21),
    (8, "Cy2NH", "dicyclohexylamine", "C1CCCCC1NC1CCCCC1", 2.0, "CuI", 0.5, 45),
]
cu_smiles = {"CuBr": "[Cu]Br", "CuCl": "[Cu]Cl", "CuI": "[Cu]I"}
for entry, alabel, aname, asmiles, aeq, culabel, cueq, yld in table1:
    parts = [
        p_sub("1a", ev1),
        p_para(ev1, [amount("equivalents", 2.5, "equiv", ev1)]),
        p_amine(alabel, aname, asmiles, ev1, [amount("equivalents", aeq, "equiv", ev1)]),
        participant("copper_salt", "catalyst", culabel, culabel, cu_smiles[culabel], ev1,
                    [amount("equivalents", cueq, "equiv", ev1)]),
        p_dioxane(ev1), p_prod("2a", ev1),
    ]
    records.append(record(
        f"table1_entry{entry}", "optimization_entry", ev1, parts,
        [field("temperature", "reflux", ev1), field("time", None, ()),
         field("atmosphere", None, ()), field("workup", None, ()), field("purification", None, ())],
        [field("reported_yield_2a", {"number": yld, "unit": "%"}, ev1, ["product"]),
         field("yield_measurement_basis", None, ())],
        unresolved=["Table 1 does not state duration, scale, atmosphere, workup, purification, or yield basis.",
                    "Candidate structures remain unverified."],
    ))

# Qualitative amine trials in page-1 prose. The source does not assign full conditions.
failed_amines = [
    ("2_imidazolidone", "2-imidazolidone", "O=C1NCCN1", "no reaction observed"),
    ("2_imidazolidinethione", "2-imidazolidinethione", "S=C1NCCN1", "no reaction observed"),
    ("1_phenylpiperazine", "1-phenylpiperazine", "c1ccc(N2CCNCC2)cc1", "did not work"),
    ("diallylamine", "diallylamine", "C=CCNCC=C", "failed to promote the reaction"),
    ("dibenzylamine", "dibenzylamine", "N(Cc1ccccc1)Cc1ccccc1", "failed to promote the reaction"),
    ("rr_1_2_diaminocyclohexane", "(1R,2R)-1,2-diaminocyclohexane", "N[C@@H]1CCCC[C@H]1N", "failed or afforded a trace amount; individual assignment not stated"),
    ("r_phenylalanine", "(R)-phenylalanine", "N[C@@H](Cc1ccccc1)C(=O)O", "failed or afforded a trace amount; individual assignment not stated"),
    ("benzyl_alpha_naphthylethylamine", "benzyl α-naphthylethylamine", None, "failed or afforded a trace amount; individual assignment not stated"),
    ("benzyl_isopropylamine", "benzyl isopropylamine", "CC(C)NCc1ccccc1", "failed or afforded a trace amount; individual assignment not stated"),
    ("ethyl_isopropylamine", "ethyl isopropylamine", "CCNC(C)C", "failed or afforded a trace amount; individual assignment not stated"),
    ("2_methyl_1_4_diazacyclohexane", "2-methyl-1,4-diazacyclohexane", "CC1CNCCN1", "failed or afforded a trace amount; individual assignment not stated"),
    ("n_n_diisopropyl_ethylenediamine", "N,N-diisopropylethylenediamine", "CC(C)N(CCN)C(C)C", "failed or afforded a trace amount; individual assignment not stated"),
]
for slug, name, smiles, result in failed_amines:
    parts = [p_sub("1a", ev1), p_amine(name, name, smiles, ev1), p_prod("2a", ev1)]
    records.append(record(
        f"prose_amine_screen_{slug}", "optimization_entry", ev1, parts,
        [field("temperature", None, ()), field("time", None, ()), field("solvent", None, ()),
         field("atmosphere", None, ()), field("workup", None, ()), field("purification", None, ())],
        [field("product_formation_result", result, ev1, ["product"])],
        notes=["Qualitative amine-screen result reported in prose outside Table 1."],
        unresolved=["The prose does not provide this trial's amine loading, copper salt/loading, paraformaldehyde loading, duration, or yield basis.",
                    "For the final seven amines, the source gives only the group-level wording 'failed or afforded a trace amount' and does not map each amine to one of the two outcomes.",
                    "Candidate structures remain unverified."],
    ))

# Table 2 rows. Each row contains two distinct experiments (conditions A and B).
table2 = [
    (1, "1a", "2a", 2.7, 42, 2.7, 66),
    (2, "1b", "2b", 2.5, 36, 2.5, 60),
    (3, "1c", "2c", 1.9, 59, 2.2, 70),
    (4, "1d", "2d", 2.3, 30, 2.3, 53),
    (5, "1e", "2e", 1.5, 53, 1.5, 81),
    (6, "1f", "2f", 2.9, 59, 2.9, 98),
    (7, "1g", "2g", 2.0, 40, 3.0, 74),
    (8, "1h", "2h", 3.0, 32, 3.0, 72),
    (9, "1i", "2i", 1.9, 33, 1.9, 52),
    (10, "1j", "2j", 2.3, 35, 2.3, 65),
    (11, "1k", "2k", 2.2, 27, 2.2, 42),
]
ev2 = [P2I, P2T]
general_workup = (
    "Cool to room temperature; add water (5 mL) and ether (10 mL); separate and extract the aqueous phase "
    "with ether (3 × 5 mL); wash the organic layer with brine; dry over anhydrous Na2SO4; evaporate."
)
general_purification = "Silica-gel column chromatography; petroleum ether or petroleum ether/Et2O eluent."
for entry, slabel, plabel, ta, ya, tb, yb in table2:
    # Conditions A. Entry 1 has a matching detailed preparation on page 2.
    aev = ev2
    smass = [amount("equivalents", 1.0, "equiv", aev)]
    para_amounts = [amount("equivalents", 2.5, "equiv", aev)]
    amine_amounts = [amount("equivalents", 1.8, "equiv", aev)]
    cu_amounts = [amount("equivalents", 0.5, "equiv", aev)]
    diox_amounts = []
    product_mass = None
    purification = None
    if entry == 1:
        smass += [amount("mass", 27.9, "mg", aev), amount("amount", 0.20, "mmol", aev)]
        para_amounts += [amount("mass", 15.3, "mg", aev), amount("amount", 0.51, "mmol", aev)]
        amine_amounts += [amount("mass", 37.0, "mg", aev), amount("amount", 0.37, "mmol", aev)]
        cu_amounts += [amount("mass", 14.4, "mg", aev), amount("amount", 0.10, "mmol", aev)]
        diox_amounts = [amount("volume", 1.0, "mL", aev)]
        product_mass = field("product_mass", {"number": 12.9, "unit": "mg"}, aev, ["product"])
        purification = "Silica-gel column chromatography with petroleum ether eluent."
    parts_a = [
        p_sub(slabel, aev, smass), p_para(aev, para_amounts),
        p_amine("i-Pr2NH", "diisopropylamine", "CC(C)NC(C)C", aev, amine_amounts),
        p_cubr(aev, cu_amounts), p_dioxane(aev, diox_amounts), p_prod(plabel, aev),
    ]
    outcomes_a = [field(f"isolated_yield_{plabel}", {"number": ya, "unit": "%"}, aev, ["product"]),
                  field("yield_measurement_basis", "isolated yield", aev)]
    if product_mass:
        outcomes_a.insert(1, product_mass)
    records.append(record(
        f"table2_entry{entry}_conditions_a", "substrate_scope_entry", aev, parts_a,
        [field("temperature", "reflux", aev), field("time", {"number": ta, "unit": "h"}, aev),
         field("atmosphere", None, ()), field("workup", None, ()),
         field("purification", purification, aev if purification else ())],
        outcomes_a,
        notes=["Table 2 Conditions A use CuBr/i-Pr2NH; the isolated-yield footnote applies to this row."],
        unresolved=["Atmosphere and workup are not stated for Conditions A; purification is stated only for entry 1.",
                    "Candidate structures remain unverified."],
    ))

    # Conditions B. The general procedure explicitly supplies scale and operations for 2a--k.
    bev = [P2I, P2T] + ([P3I, P3T] if entry == 1 else [])
    smass_b = [amount("equivalents", 1.0, "equiv", bev), amount("amount", 0.20, "mmol", bev)]
    para_b = [amount("equivalents", 2.5, "equiv", bev), amount("amount", 0.50, "mmol", bev)]
    amine_b = [amount("equivalents", 1.8, "equiv", bev), amount("amount", 0.36, "mmol", bev)]
    cu_b = [amount("equivalents", 0.5, "equiv", bev), amount("amount", 0.10, "mmol", bev)]
    if entry == 1:
        smass_b += [amount("mass", 27.8, "mg", bev)]
        para_b += [amount("mass", 15.0, "mg", bev)]
        amine_b += [amount("mass", 65.5, "mg", bev)]
        cu_b += [amount("mass", 19.1, "mg", bev)]
    parts_b = [
        p_sub(slabel, bev, smass_b), p_para(bev, para_b),
        p_amine("Cy2NH", "dicyclohexylamine", "C1CCCCC1NC1CCCCC1", bev, amine_b),
        p_cui(bev, cu_b), p_dioxane(bev, [amount("volume", 1.0, "mL", bev)]), p_prod(plabel, bev),
    ]
    outcomes_b = [field(f"isolated_yield_{plabel}", {"number": yb, "unit": "%"}, bev, ["product"]),
                  field("yield_measurement_basis", "isolated yield", bev)]
    if entry == 1:
        outcomes_b.insert(1, field("product_mass", {"number": 20.2, "unit": "mg"}, bev, ["product"]))
    records.append(record(
        f"table2_entry{entry}_conditions_b", "substrate_scope_entry", bev, parts_b,
        [field("temperature", "reflux", bev), field("time", {"number": tb, "unit": "h"}, bev),
         field("atmosphere", "argon", bev), field("operation", "Monitor reaction completion by TLC; cool to room temperature.", bev),
         field("workup", general_workup, bev), field("purification", general_purification, bev)],
        outcomes_b,
        notes=["Table 2 Conditions B are linked to the stated general procedure for allenes 2a–k."],
        unresolved=["Exact operation-specific solvent volumes beyond the stated general procedure are unavailable.",
                    "Candidate structures remain unverified."],
    ))

# Scheme 1: three independent preparative-scale experiments.
def scheme_parts(slabel, plabel, s_mmol, para_mmol, cui_mmol, amine_mmol, evidence,
                 s_mass=None, para_mass=None, cui_mass=None, amine_mass=None, dioxane_ml=None):
    sa = [amount("amount", s_mmol, "mmol", evidence)]
    pa = [amount("amount", para_mmol, "mmol", evidence)]
    ca = [amount("amount", cui_mmol, "mmol", evidence)]
    aa = [amount("amount", amine_mmol, "mmol", evidence)]
    if s_mass: sa.append(amount("mass", s_mass[0], s_mass[1], evidence))
    if para_mass: pa.append(amount("mass", para_mass[0], para_mass[1], evidence))
    if cui_mass: ca.append(amount("mass", cui_mass[0], cui_mass[1], evidence))
    if amine_mass: aa.append(amount("mass", amine_mass[0], amine_mass[1], evidence))
    return [p_sub(slabel, evidence, sa), p_para(evidence, pa), p_cui(evidence, ca),
            p_amine("Cy2NH", "dicyclohexylamine", "C1CCCCC1NC1CCCCC1", evidence, aa),
            p_dioxane(evidence, [amount("volume", dioxane_ml, "mL", evidence)] if dioxane_ml else []),
            p_prod(plabel, evidence)]

for suffix, slabel, plabel, vals in [
    ("scheme1_large_scale_1e_to_2e", "1e", "2e", (6.0, 14.9, 3.0, 10.8, 3.2, 81)),
    ("scheme1_large_scale_1i_to_2i", "1i", "2i", (5.9, 15.1, 3.0, 10.9, 2.3, 54)),
]:
    sm, pm, cm, am, time_h, yld = vals
    parts = scheme_parts(slabel, plabel, sm, pm, cm, am, ev2)
    records.append(record(
        suffix, "reported_experiment", ev2, parts,
        [field("temperature", "reflux", ev2), field("time", {"number": time_h, "unit": "h"}, ev2),
         field("atmosphere", None, ()), field("workup", None, ()), field("purification", None, ())],
        [field(f"reported_yield_{plabel}", {"number": yld, "unit": "%"}, ev2, ["product"]),
         field("yield_measurement_basis", None, ())],
        notes=["Preparative-scale reaction depicted in Scheme 1."],
        unresolved=["Scheme 1 does not state dioxane volume, atmosphere, workup, purification, product mass, or yield basis.",
                    "Candidate structures remain unverified."],
    ))

# Scheme 1's 1g batch is described in detail on page 3; both durations are retained.
ev23 = [P2I, P2T, P3I, P3T]
parts_g = scheme_parts(
    "1g", "2g", 6.1, 15.1, 3.0, 10.8, ev23,
    s_mass=(1.062, "g"), para_mass=(0.453, "g"), cui_mass=(0.571, "g"),
    amine_mass=(1.955, "g"), dioxane_ml=9.0,
)
records.append(record(
    "scheme1_large_scale_1g_to_2g", "reported_experiment", ev23, parts_g,
    [field("temperature", "gently refluxed", ev23),
     field("scheme_1_time", {"number": 2.8, "unit": "h"}, ev2),
     field("detailed_procedure_time", {"number": 2.5, "unit": "h"}, [P3I, P3T]),
     field("atmosphere", None, ()),
     field("operation", "Monitor by TLC; cool to room temperature; filter; concentrate filtrate under vacuum.", [P3I, P3T]),
     field("workup", "Dilute residue with water (5 mL) and ether (10 mL); acidify with 1 N HCl to pH 1–2; separate and extract aqueous phase with ether (3 × 10 mL); wash combined organic phase with water to pH 6–7, then brine; dry over anhydrous Na2SO4; evaporate.", [P3I, P3T]),
     field("purification", "Silica-gel column chromatography with petroleum ether/Et2O eluent.", [P3I, P3T])],
    [field("isolated_yield_2g", {"number": 72, "unit": "%"}, ev23, ["product"]),
     field("product_mass", {"number": 0.824, "unit": "g"}, [P3I, P3T], ["product"]),
     field("yield_measurement_basis", "isolated after column chromatography", [P3I, P3T])],
    notes=["Scheme 1 and the detailed preparation use the same quantities and 72% yield, so they are treated as the same batch."],
    unresolved=["Scheme 1 states 2.8 h, whereas the detailed page-3 procedure states 2.5 h; both are preserved without reconciliation.",
                "Atmosphere is not stated for this large-scale batch.", "Candidate structures remain unverified."],
))


OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")

ids = {r["source_reaction_id"]: r["record_id"] for r in records}
page1_ids = [ids["graphical_abstract_general_transformation"]]
page1_ids += [ids[f"table1_entry{i}"] for i in range(1, 9)]
page1_ids += [ids[f"prose_amine_screen_{x[0]}"] for x in failed_amines]
page2_ids = [ids[f"table2_entry{i}_conditions_{c}"] for i in range(1, 12) for c in ("a", "b")]
page2_ids += [ids["scheme1_large_scale_1e_to_2e"], ids["scheme1_large_scale_1g_to_2g"], ids["scheme1_large_scale_1i_to_2i"]]
page3_ids = [ids["table2_entry1_conditions_b"], ids["scheme1_large_scale_1g_to_2g"]]
coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1, "state": "attempted",
            "regions": [
                {"region": "upper-left graphical abstract", "finding": "Generic present-paper terminal-alkyne-to-terminal-allene transformation recorded as a general scheme, not a batch experiment.", "evidence_ids": [P1I, P1T]},
                {"region": "upper-right Table 1 and reaction arrow", "finding": "Eight independent optimization rows extracted with row-specific amine/copper loadings and yields.", "evidence_ids": [P1I, P1T]},
                {"region": "right-column optimization prose below Table 1", "finding": "Twelve named qualitative amine trials extracted; exact conditions and the failed-versus-trace mapping for the final group are unresolved.", "evidence_ids": [P1I, P1T]},
                {"region": "introduction and citations", "finding": "Prior literature summaries and abstract-level claims were not expanded into present-paper experiments.", "evidence_ids": [P1I, P1T]},
            ],
            "record_ids": page1_ids,
            "unresolved": ["Table 1 omits duration, scale, atmosphere, workup, purification, and yield basis.", "Qualitative prose trials do not provide a complete condition set.", "All candidate structures remain unverified."],
        },
        {
            "page": 2, "state": "attempted",
            "regions": [
                {"region": "upper-left Table 2 with Conditions A/B arrows and footnote", "finding": "Eleven rows split into 22 independent experiments; the isolated-yield footnote was retained and shared conditions applied only within their branch.", "evidence_ids": [P2I, P2T]},
                {"region": "upper-right Scheme 1", "finding": "Three distinct preparative-scale reactions extracted; the 1g case is linked to its detailed page-3 batch.", "evidence_ids": [P2I, P2T]},
                {"region": "right-column General Procedure for the Synthesis of Allenes (2a–k)", "finding": "Exact standard-B quantities, argon/reflux/TLC operations, workup, and chromatography merged into all Table 2 Conditions B records.", "evidence_ids": [P2I, P2T]},
                {"region": "lower-right 2a Conditions A/B preparation paragraphs", "finding": "Conditions A exact quantities/product mass merged into Table 2 entry 1 A; Conditions B continues onto page 3 and is merged into entry 1 B.", "evidence_ids": [P2I, P2T]},
                {"region": "starting-alkyne preparation paragraph", "finding": "Cited or abbreviated starting-material routes were treated as provenance/context, not as independent present-paper batch records.", "evidence_ids": [P2I, P2T]},
            ],
            "record_ids": page2_ids,
            "unresolved": ["Scheme 1 omits yield basis for 2e and 2i and omits several operational details.", "Most Conditions A rows omit scale, atmosphere, workup, and purification.", "All candidate structures remain unverified."],
        },
        {
            "page": 3, "state": "attempted",
            "regions": [
                {"region": "upper-left continuation of 2a Conditions B", "finding": "The remaining Cy2NH/CuI quantities and 20.2 mg, 66% outcome were merged into Table 2 entry 1 Conditions B.", "evidence_ids": [P3I, P3T]},
                {"region": "left-column detailed synthesis of 2g", "finding": "Detailed operations, masses, volumes, 0.824 g and 72% were merged into the Scheme 1 large-scale 1g batch; its 2.5 h duration conflicts with Scheme 1's 2.8 h.", "evidence_ids": [P3I, P3T]},
                {"region": "right-column Supporting Information Available notice", "finding": "The paper advertises SI, but no SI file was supplied or explicitly associated; no SI facts were inferred.", "evidence_ids": [P3I, P3T]},
            ],
            "record_ids": page3_ids,
            "unresolved": ["The 1g large-scale duration conflict (2.8 h in Scheme 1 versus 2.5 h in the detailed procedure) remains unresolved.", "SI association remains unestablished.", "All candidate structures remain unverified."],
        },
    ],
}
COVERAGE.parent.mkdir(parents=True, exist_ok=True)
COVERAGE.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

tasks = json.loads(TASKS.read_text())
for task in tasks:
    if task.get("document_id") == DOC and task.get("evidence_id") in {P1T, P2T, P3T}:
        task["state"] = "attempted"
TASKS.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"records": len(records), "output": str(OUT), "coverage": str(COVERAGE)}, ensure_ascii=False))
