#!/usr/bin/env python3
"""Build the machine-extracted records for PDF pages 1--4.

This is deliberately separate from the merge tool so the raw extraction is
preserved verbatim before the merge tool quarantines it as needs_review.
"""
from pathlib import Path
import json

DOC = "doc_418c20e0ff369844"
OUT = Path(__file__).with_name("records_pages_0001_0004.json")


def ev(page):
    return [f"{DOC}:page{page}:image", f"{DOC}:page{page}:text"]


P1, P2, P3, P4 = (ev(i) for i in range(1, 5))


def fact(value, evidence):
    return {
        "value": value,
        "evidence_ids": list(evidence) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def fld(name, value, evidence, targets=None):
    result = {"name": name, "fact": fact(value, evidence)}
    if targets:
        result["target_entity_ids"] = list(targets)
    return result


def part(entity_id, role, label, name, evidence, smiles=None, amounts=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence),
        "smiles": fact(smiles, evidence),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": amounts or [],
    }


def rec(suffix, kind, evidence, participants=None, steps=None, outcomes=None,
        notes=None, unresolved=None):
    return {
        "record_id": f"{DOC}:{suffix}",
        "document_id": DOC,
        "source_reaction_id": suffix,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": list(dict.fromkeys(evidence)),
        "participants": participants or [],
        "steps": steps or [],
        "outcomes": outcomes or [],
        "notes": [fact(x, e) for x, e in (notes or [])],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved or [],
        },
    }


def missing_conditions(evidence):
    return [fld("temperature", None, evidence), fld("time", None, evidence)]


records = []

# Page 1: classify every visible scheme route; none is a batch experiment from
# the present paper. Generic R groups are intentionally not expanded to SMILES.
records.append(rec(
    "scheme1_generic_cross_coupling", "general_scheme", P1,
    [part("generic_r_x", "reactant", "R'X", "organic halide or triflate", P1),
     part("generic_r_m", "reactant", "RM", "organometallic reagent", P1),
     part("generic_coupled", "product", "R'R", "cross-coupled product", P1),
     part("generic_ni_pd", "catalyst", "Ni or Pd", "nickel or palladium catalyst", P1)],
    [{"step_id": "scheme_arrow", "participant_ids": ["generic_r_x", "generic_r_m", "generic_ni_pd", "generic_coupled"],
      "conditions": missing_conditions(P1)}],
    [fld("reported_yield", None, P1, ["generic_coupled"])],
    [("Scheme 1 is a generic cross-coupling illustration, not a reported experiment in this paper.", P1)],
    ["R groups and metal identity are generic; time, temperature, and yield are not reported."]))


def page1_literature(suffix, labels, conditions, note):
    ps = [part(eid, role, label, name, P1, None, amounts)
          for eid, role, label, name, amounts in labels]
    records.append(rec(
        suffix, "literature_example", P1, ps,
        [{"step_id": "scheme_arrow", "participant_ids": [p["entity_id"] for p in ps],
          "conditions": conditions + missing_conditions(P1)}],
        [fld("reported_yield", None, P1, [p["entity_id"] for p in ps if p["role"] == "product"])],
        [(note, P1)],
        ["Scheme-only prior-work example; substrate identity, time, temperature, and yield are incomplete."]))


page1_literature(
    "scheme2_ref6_gold_cyclization",
    [("ref6_allenoate", "reactant", "generic 2,3-allenoate", "generic 2,3-allenoate", []),
     ("ref6_gold", "reagent", "[Au(PPh3)OTf]", "triphenylphosphinegold(I) triflate", [fld("stoichiometry", "stoichiometric", P1)]),
     ("ref6_product", "product", "2(5H)-furanonyl Au species", "generic furanonyl gold species", [])],
    [], "Reference 6 literature route shown in Scheme 2.")
page1_literature(
    "scheme2_context_hydrolysis",
    [("hydrolysis_allenoate", "reactant", "generic ethyl 2,3-allenoate", "generic ethyl 2,3-allenoate", []),
     ("hydrolysis_naoh", "reagent", "NaOH", "sodium hydroxide", []),
     ("hydrolysis_acid", "product", "generic 2,3-allenoic acid", "generic 2,3-allenoic acid", [])],
    [], "Contextual hydrolysis arrow in Scheme 2; not reported as a batch experiment here.")
page1_literature(
    "scheme2_ref10_acid_palladium_allylation",
    [("ref10_acid", "reactant", "generic 2,3-allenoic acid", "generic 2,3-allenoic acid", []),
     ("ref10_allyl_bromide", "reactant", "allyl bromide", "allyl bromide", []),
     ("ref10_nahco3", "reagent", "NaHCO3", "sodium bicarbonate", []),
     ("ref10_pdcl2", "catalyst", "PdCl2", "palladium(II) chloride", [fld("catalyst_loading", {"number": 5, "unit": "mol%"}, P1)]),
     ("ref10_product", "product", "allylic butenolide", "generic allylic butenolide", [])],
    [], "Reference 10 literature route shown in Scheme 2.")
page1_literature(
    "scheme2_ref5_gold_palladium_coupling",
    [("ref5_gold_species", "reactant", "furanonyl Au(PPh3) species", "generic furanonyl gold species", []),
     ("ref5_aryl_iodide", "reactant", "ArI", "generic aryl iodide", []),
     ("ref5_pd", "catalyst", "Pd", "palladium catalyst", [fld("catalyst_loading", {"number": 1, "unit": "mol%"}, P1)]),
     ("ref5_product", "product", "aryl-substituted butenolide", "generic aryl-substituted butenolide", [])],
    [], "Reference 5 literature route shown in Scheme 2.")
page1_literature(
    "scheme2_ref4_dual_gold_palladium",
    [("ref4_allylic_allenoate", "reactant", "generic allylic 2,3-allenoate", "generic allylic 2,3-allenoate", []),
     ("ref4_gold", "catalyst", "[Au(PPh3)OTf]", "triphenylphosphinegold(I) triflate", [fld("catalyst_loading", {"number": 5, "unit": "mol%"}, P1)]),
     ("ref4_pd", "catalyst", "[Pd2(dba)3]", "tris(dibenzylideneacetone)dipalladium", [fld("catalyst_loading", {"number": 5, "unit": "mol%"}, P1)]),
     ("ref4_product", "product", "allylic butenolide", "generic allylic butenolide", [])],
    [], "Reference 4 literature route shown in Scheme 2.")

records.append(rec(
    "scheme2_this_work_generic_route", "general_scheme", P1,
    [part("thiswork_allenoate", "reactant", "generic 2,3-allenoate", "generic 2,3-allenoate", P1),
     part("thiswork_allyl_bromide", "reactant", "allylic bromide", "generic allylic bromide", P1),
     part("thiswork_fecl3", "catalyst", "FeCl3", "iron(III) chloride", P1),
     part("thiswork_pdcl2", "catalyst", "PdCl2", "palladium(II) chloride", P1),
     part("thiswork_product", "product", "generic allylic butenolide", "generic allylic butenolide", P1)],
    [{"step_id": "generic_cocatalytic_route", "participant_ids": ["thiswork_allenoate", "thiswork_allyl_bromide", "thiswork_fecl3", "thiswork_pdcl2", "thiswork_product"],
      "conditions": missing_conditions(P1)}],
    [fld("reported_yield", None, P1, ["thiswork_product"])],
    [("Top route of Scheme 2 is the generic concept for this work, not an individual batch.", P1)],
    ["Generic substituents and missing operational details prevent an experiment-level record."]))


# Shared fully specified entities used on pages 2--3.
SMILES = {
    "1a": "CCOC(=O)C(CC)=C=Cc1ccccc1",
    "2a": "C=CCBr",
    "3a": "O=C1OC(c2ccccc2)C(CC)=C1CC=C",
    "4a": "O=C1OC(c2ccccc2)C(CC)=C1",
}


def amount(name, number, unit, evidence):
    return fld(name, {"number": number, "unit": unit}, evidence)


def core_1a_2a(evidence, products=("3a", "4a"), one_mmol=False):
    a1 = [amount("mass", 217.3, "mg", evidence), amount("amount", 1, "mmol", evidence)] if one_mmol else []
    ps = [part("1a", "reactant", "1a", "ethyl 4-phenyl-2-ethyl-2,3-butadienoate", evidence, SMILES["1a"], a1),
          part("2a", "reactant", "2a", "allyl bromide", evidence, SMILES["2a"], [amount("equivalents", 5, "equiv", evidence)])]
    if "3a" in products:
        ps.append(part("3a", "product", "3a", "4-allyl-3-ethyl-5-phenyl-2(5H)-furanone", evidence, SMILES["3a"]))
    if "4a" in products:
        ps.append(part("4a", "product", "4a", "3-ethyl-5-phenyl-2(5H)-furanone", evidence, SMILES["4a"]))
    return ps


def solvent(entity, label, name, smiles, evidence, volume=None):
    amounts = [amount("volume", volume, "mL", evidence)] if volume is not None else []
    return part(entity, "solvent", label, name, evidence, smiles, amounts)


def catalyst(entity, label, name, loading, evidence, mass=None, mmol=None):
    amounts = [amount("catalyst_loading", loading, "mol%", evidence)]
    if mass is not None:
        amounts.append(amount("mass", mass, "mg", evidence))
    if mmol is not None:
        amounts.append(amount("amount", mmol, "mmol", evidence))
    return part(entity, "catalyst", label, name, evidence, None, amounts)


def yields(evidence, y3=None, y4=None, recovery=None, basis=None):
    result = []
    if y3 is not None:
        result.append(fld("reported_yield_3a", {"number": y3, "unit": "%"}, evidence, ["3a"]))
        result.append(fld("yield_measurement_basis_3a", basis, evidence, ["3a"]))
    if y4 is not None:
        result.append(fld("reported_yield_4a", {"number": y4, "unit": "%"}, evidence, ["4a"]))
        result.append(fld("yield_measurement_basis_4a", basis, evidence, ["4a"]))
    if recovery is not None:
        result.append(fld("recovered_starting_material_yield", {"number": recovery, "unit": "%"}, evidence, ["1a"]))
    return result


# Page 2 equations 1 and 2.
for suffix, catalysts, temp, time, y3, y4, recovery in [
    ("equation1_gold_screen", [("aupph3cl", "Au(PPh3)Cl", "chlorotriphenylphosphinegold(I)"),
                               ("agotf", "Ag(OTf)", "silver triflate"),
                               ("pdoac2", "Pd(OAc)2", "palladium(II) acetate")], "RT", 45, 18, 9, 50),
    ("equation2_gold_screen", [("aucl", "AuCl", "gold(I) chloride"),
                               ("pdcl2", "PdCl2", "palladium(II) chloride")], {"number": 40, "unit": "°C"}, 23, 25, 2, 38),
]:
    ps = core_1a_2a(P2)
    for eid, label, name in catalysts:
        ps.append(catalyst(eid, label, name, 5, P2))
    ps.append(solvent("ch2cl2", "CH2Cl2", "dichloromethane", "ClCCl", P2))
    basis_unresolved = "Percentages are drawn next to products, but the measurement basis is not stated in the equation."
    records.append(rec(
        suffix, "optimization_entry", P2, ps,
        [{"step_id": "reaction", "participant_ids": [p["entity_id"] for p in ps],
          "conditions": [fld("solvent", "CH2Cl2", P2), fld("temperature", temp, P2), fld("time", {"number": time, "unit": "h"}, P2)]}],
        yields(P2, y3, y4, recovery, None),
        [("Best condition from the preceding gold-complex screening discussion.", P2)],
        [basis_unresolved, "Exact reactant amount, atmosphere, workup, and purification are not reported here."]))


# Table 1, eight independent optimization rows.
table1 = [
    (1, 5, 1, 35, 0, 0, 71, "Pd(PPh3)2Cl2", "dichlorobis(triphenylphosphine)palladium(II)"),
    (2, 5, 1, 18, 58, 4, None, "PdCl2", "palladium(II) chloride"),
    (3, 5, 1, 10, 57, 5, None, "Pd(PhCN)2Cl2", "dichlorobis(benzonitrile)palladium(II)"),
    (4, 5, 0.4, 33, 50, 7, None, "PdCl2", "palladium(II) chloride"),
    (5, 5, 2, 12, 41, 4, None, "PdCl2", "palladium(II) chloride"),
    (6, 1, 1, 45, 41, 9, None, "PdCl2", "palladium(II) chloride"),
    (7, 3, 1, 20, 53, 5, None, "PdCl2", "palladium(II) chloride"),
    (8, 10, 1, 11, 56, 4, None, "PdCl2", "palladium(II) chloride"),
]
for entry, fe, conc, time, y3, y4, recovery, pd_label, pd_name in table1:
    ps = core_1a_2a(P2, one_mmol=True)
    ps += [catalyst("fecl3", "FeCl3", "iron(III) chloride", fe, P2),
           catalyst("pd_catalyst", pd_label, pd_name, 5, P2),
           solvent("ch2cl2", "CH2Cl2", "dichloromethane", "ClCCl", P2)]
    unresolved = ["Atmosphere, workup, and purification are not reported for this optimization row."]
    records.append(rec(
        f"table1_entry{entry}", "optimization_entry", P2, ps,
        [{"step_id": "reaction", "participant_ids": [p["entity_id"] for p in ps],
          "conditions": [fld("solvent", "CH2Cl2", P2), fld("concentration", {"number": conc, "unit": "M"}, P2),
                         fld("temperature", {"number": 40, "unit": "°C"}, P2), fld("time", {"number": time, "unit": "h"}, P2)]}],
        yields(P2, y3, y4, recovery, "NMR"),
        [], unresolved))


# Table 2, eleven independent solvent rows.
table2 = [
    (1, "ClCH2CH2Cl", "1,2-dichloroethane", "ClCCCl", 20, 50, 4, 0),
    (2, "CCl3CH3", "1,1,1-trichloroethane", "CC(Cl)(Cl)Cl", 20, 45, 3, 0),
    (3, "CHCl2CH3", "1,1-dichloroethane", "CC(Cl)Cl", 20, 55, 4, 0),
    (4, "CH2Cl2", "dichloromethane", "ClCCl", 18, 58, 4, 0),
    (5, "CHCl2CH2Cl", "1,1,2-trichloroethane", "ClC(Cl)CCl", 20, 54, 4, 0),
    (6, "THF", "tetrahydrofuran", "C1CCOC1", 20, 29, 10, 29),
    (7, "toluene", "toluene", "Cc1ccccc1", 20, 41, 4, 0),
    (8, "CH3CN", "acetonitrile", "CC#N", 20, 18, 6, 32),
    (9, "n-hexane", "n-hexane", "CCCCCC", 20, 7, 1, 55),
    (10, "benzene", "benzene", "c1ccccc1", 20, 42, 2, 8),
    (11, "1,4-dioxane", "1,4-dioxane", "O1CCOCC1", 20, 38, 4, 12),
]
for entry, sol_label, sol_name, sol_smiles, time, y3, y4, recovery in table2:
    ps = core_1a_2a(P2, one_mmol=True)
    ps += [catalyst("fecl3", "FeCl3", "iron(III) chloride", 5, P2),
           catalyst("pdcl2", "PdCl2", "palladium(II) chloride", 5, P2),
           solvent("solvent", sol_label, sol_name, sol_smiles, P2)]
    records.append(rec(
        f"table2_entry{entry}", "optimization_entry", P2, ps,
        [{"step_id": "reaction", "participant_ids": [p["entity_id"] for p in ps],
          "conditions": [fld("solvent", sol_label, P2), fld("concentration", {"number": 1, "unit": "M"}, P2),
                         fld("temperature", {"number": 40, "unit": "°C"}, P2), fld("time", {"number": time, "unit": "h"}, P2)]}],
        yields(P2, y3, y4, recovery, "NMR"),
        [], ["Atmosphere, workup, and purification are not reported for this optimization row."]))


# Equation 3 starts on page 2 and its prose result continues on page 3.
eq3ev = P2 + P3
ps = core_1a_2a(eq3ev, products=("3a",))
ps += [catalyst("cucl2", "CuCl2", "copper(II) chloride", 5, eq3ev),
       catalyst("pdcl2", "PdCl2", "palladium(II) chloride", 5, eq3ev),
       solvent("ch2cl2", "CH2Cl2", "dichloromethane", "ClCCl", eq3ev)]
records.append(rec(
    "equation3_cucl2_control", "optimization_entry", eq3ev, ps,
    [{"step_id": "reaction", "participant_ids": [p["entity_id"] for p in ps],
      "conditions": [fld("solvent", "CH2Cl2", eq3ev), fld("temperature", {"number": 40, "unit": "°C"}, eq3ev),
                     fld("time", {"number": 35, "unit": "h"}, eq3ev)]}],
    [fld("nmr_yield_3a", {"number": 16, "unit": "%"}, eq3ev, ["3a"]),
     fld("yield_measurement_basis_3a", "NMR", eq3ev, ["3a"]),
     fld("recovered_starting_material_yield", {"number": 42, "unit": "%"}, eq3ev, ["1a"])],
    [], ["Exact reactant amount, atmosphere, workup, purification, and any 4a outcome are not reported."]))


# Qualitative repeat with high-purity FeCl3, reported only in prose on page 3.
ps = core_1a_2a(P3, products=("3a", "4a"), one_mmol=True)
ps += [catalyst("fecl3_high_purity", "FeCl3 (99.99% purity)", "iron(III) chloride", 5, P3),
       catalyst("pdcl2", "PdCl2", "palladium(II) chloride", 5, P3),
       solvent("ch2cl2", "CH2Cl2", "dichloromethane", "ClCCl", P3, 1)]
records.append(rec(
    "prose_high_purity_fecl3_repeat", "reported_experiment", P3, ps,
    [{"step_id": "reaction", "participant_ids": [p["entity_id"] for p in ps],
      "conditions": [fld("solvent", "CH2Cl2", P3), fld("temperature", {"number": 40, "unit": "°C"}, P3), fld("time", None, P3)]}],
    [fld("reported_result", "very similar results", P3)],
    [("The paper reports that Aldrich FeCl3 of 99.99% purity provided very similar results.", P3)],
    ["Exact duration and product yields for this repeat are not stated; 'very similar' is not converted to numbers."]))


# Page 3 Table 3. Fully specified acyclic structures receive candidate SMILES;
# the cyclic entry 10 remains label-only because the spanning -(CH2)5- row is
# not safely represented without independent structure verification.
scope = [
    (1, "1a", "Ph", "H", "Et", "H", 29, 51, "3a", SMILES["1a"], SMILES["3a"]),
    (2, "1b", "Ph", "H", "nPr", "H", 15.5, 73, "3b", "CCOC(=O)C(CCC)=C=Cc1ccccc1", "O=C1OC(c2ccccc2)C(CCC)=C1CC=C"),
    (3, "1c", "p-BrC6H4", "H", "Et", "H", 30, 59, "3c", "CCOC(=O)C(CC)=C=Cc1ccc(Br)cc1", "O=C1OC(c2ccc(Br)cc2)C(CC)=C1CC=C"),
    (4, "1d", "p-BrC6H4", "H", "nPr", "H", 60, 53, "3d", "CCOC(=O)C(CCC)=C=Cc1ccc(Br)cc1", "O=C1OC(c2ccc(Br)cc2)C(CCC)=C1CC=C"),
    (5, "1e", "p-ClC6H4", "H", "nPr", "H", 27, 64, "3e", "CCOC(=O)C(CCC)=C=Cc1ccc(Cl)cc1", "O=C1OC(c2ccc(Cl)cc2)C(CCC)=C1CC=C"),
    (6, "1f", "p-FC6H4", "H", "nPr", "H", 68, 60, "3f", "CCOC(=O)C(CCC)=C=Cc1ccc(F)cc1", "O=C1OC(c2ccc(F)cc2)C(CCC)=C1CC=C"),
    (7, "1g", "p-MeC6H4", "H", "nPr", "H", 71, 45, "3g", "CCOC(=O)C(CCC)=C=Cc1ccc(C)cc1", "O=C1OC(c2ccc(C)cc2)C(CCC)=C1CC=C"),
    (8, "1h", "Ph", "H", "Bn", "H", 27, 65, "3h", "CCOC(=O)C(Cc1ccccc1)=C=Cc1ccccc1", "O=C1OC(c2ccccc2)C(Cc2ccccc2)=C1CC=C"),
    (9, "1i", "Et", "H", "Ph", "H", 48, 40, "3i", "CCOC(=O)C(c1ccccc1)=C=CCC", "O=C1OC(CC)C(c2ccccc2)=C1CC=C"),
    (10, "1j", "-(CH2)5-", None, "Ph", "H", 33, 50, "3j", None, None),
    (11, "1b", "Ph", "H", "nPr", "Me", 67, 53, "3k", "CCOC(=O)C(CCC)=C=Cc1ccccc1", "O=C1OC(c2ccccc2)C(CCC)=C1CC(=C)C"),
    (12, "1d", "p-BrC6H4", "H", "nPr", "Me", 72, 65, "3l", "CCOC(=O)C(CCC)=C=Cc1ccc(Br)cc1", "O=C1OC(c2ccc(Br)cc2)C(CCC)=C1CC(=C)C"),
]
for entry, substrate, r1, r2, r3, r4, time, yld, product, s_smiles, p_smiles in scope:
    evidence = P3 + P4 if entry == 1 else P3
    substrate_name = f"Table 3 allenoate {substrate} (R1={r1}, R2={r2}, R3={r3})"
    if entry == 10:
        substrate_name = "Table 3 cyclic methyl allenoate 1j (-(CH2)5- spanning R1/R2; R3=Ph)"
    ps = [part(substrate, "reactant", substrate, substrate_name, evidence, s_smiles),
          part("allylic_bromide", "reactant", "2a" if r4 == "H" else "2-methylallyl bromide", "allyl bromide" if r4 == "H" else "2-methylallyl bromide", evidence,
               "C=CCBr" if r4 == "H" else "C=C(C)CBr", [amount("equivalents", 5, "equiv", evidence)]),
          part(product, "product", product, f"Table 3 butenolide {product}", evidence, p_smiles),
          catalyst("fecl3", "FeCl3", "iron(III) chloride", 5, evidence),
          catalyst("pdcl2", "PdCl2", "palladium(II) chloride", 5, evidence)]
    if entry in (9, 10):
        ps.append(solvent("dce", "DCE", "1,2-dichloroethane", "ClCCCl", evidence, 1))
        temp = 60
        sol_label = "DCE"
    else:
        ps.append(solvent("ch2cl2", "CH2Cl2", "dichloromethane", "ClCCl", evidence, 1 if entry == 1 else None))
        temp = 40
        sol_label = "CH2Cl2"
    if entry == 1:
        ps[0]["amounts"] += [amount("mass", 217.3, "mg", P3), amount("amount", 1, "mmol", P3)]
        ps[1]["amounts"] += [amount("mass", 604.2, "mg", P3), amount("amount", 5, "mmol", P3)]
        for p in ps:
            if p["entity_id"] == "fecl3":
                p["amounts"] += [amount("mass", 8.1, "mg", P3), amount("amount", 0.05, "mmol", P3)]
            if p["entity_id"] == "pdcl2":
                p["amounts"] += [amount("mass", 8.8, "mg", P3), amount("amount", 0.05, "mmol", P3)]
        ps[2]["amounts"] += [amount("mass", 0.117, "g", P3)]
    conditions = [fld("solvent", sol_label, evidence), fld("concentration", {"number": 1, "unit": "M"}, evidence),
                  fld("temperature", {"number": temp, "unit": "°C"}, evidence), fld("time", {"number": time, "unit": "h"}, evidence)]
    if entry == 1:
        conditions += [fld("atmosphere", "nitrogen", P3),
                       fld("operation", "Reagents were added sequentially to a dried Schlenk tube at room temperature; reaction completion was monitored by TLC.", P3),
                       fld("workup", "Diluted with Et2O (20 mL), filtered, concentrated, and sampled with mesitylene (35 uL) for crude 1H NMR analysis.", P3),
                       fld("purification", "Silica-gel column chromatography, petroleum ether/ethyl acetate 20:1.", P3)]
    basis = "isolated" if entry == 1 else None
    unresolved = [] if entry == 1 else ["Yield measurement basis, atmosphere, workup, and purification are not stated for this table row."]
    if entry == 10:
        unresolved.append("Entry 10's spanning -(CH2)5- substrate/product structures were not converted to SMILES.")
    notes = []
    if entry in (9, 10):
        notes.append(("Footnote a: reaction at 60 °C in 1 mL DCE; FeCl3 purity >97%.", P3))
    if entry == 10:
        notes.append(("Footnote b: methyl ester was used.", P3))
    if entry == 1:
        notes.append(("Page 4 continues NMR, IR, MS, and HRMS characterization of product 3a.", P4))
    records.append(rec(
        f"table3_entry{entry}", "substrate_scope_entry", evidence, ps,
        [{"step_id": "reaction", "participant_ids": [p["entity_id"] for p in ps], "conditions": conditions}],
        [fld(f"reported_yield_{product}", {"number": yld, "unit": "%"}, evidence, [product]),
         fld(f"yield_measurement_basis_{product}", basis, P3, [product])],
        notes, unresolved))


# Page 3 control equations 4--6.
ps = core_1a_2a(P3, products=("3a",))
ps += [catalyst("pdcl2", "PdCl2", "palladium(II) chloride", 5, P3),
       solvent("ch2cl2", "CH2Cl2", "dichloromethane", "ClCCl", P3)]
records.append(rec(
    "equation4_pdcl2_only_control", "reported_experiment", P3, ps,
    [{"step_id": "reaction", "participant_ids": [p["entity_id"] for p in ps],
      "conditions": [fld("solvent", "CH2Cl2", P3), fld("temperature", {"number": 40, "unit": "°C"}, P3), fld("time", {"number": 17.5, "unit": "h"}, P3)]}],
    [fld("reported_yield_3a", "no reaction", P3, ["3a"]),
     fld("recovered_starting_material_yield", {"number": 70, "unit": "%"}, P3, ["1a"])],
    [], ["Exact reactant amount, atmosphere, workup, purification, and recovery measurement basis are not stated."]))

ps = core_1a_2a(P3, products=("4a",))
ps += [catalyst("fecl3", "FeCl3", "iron(III) chloride", 5, P3),
       solvent("ch2cl2", "CH2Cl2", "dichloromethane", "ClCCl", P3)]
records.append(rec(
    "equation5_fecl3_only_control", "reported_experiment", P3, ps,
    [{"step_id": "reaction", "participant_ids": [p["entity_id"] for p in ps],
      "conditions": [fld("solvent", "CH2Cl2", P3), fld("temperature", {"number": 40, "unit": "°C"}, P3), fld("time", {"number": 34, "unit": "h"}, P3)]}],
    [fld("nmr_yield_4a", {"number": 5, "unit": "%"}, P3, ["4a"]),
     fld("yield_measurement_basis_4a", "NMR", P3, ["4a"]),
     fld("recovered_starting_material_yield", {"number": 64, "unit": "%"}, P3, ["1a"])],
    [], ["Exact reactant amount, atmosphere, workup, and purification are not stated."]))

ps = [part("1a", "reactant", "1a", "ethyl 4-phenyl-2-ethyl-2,3-butadienoate", P3, SMILES["1a"]),
      part("4a", "product", "4a", "3-ethyl-5-phenyl-2(5H)-furanone", P3, SMILES["4a"]),
      part("5a", "product", "5a", "chloro-substituted 2(5H)-furanone 5a", P3, None),
      part("fecl3", "reagent", "FeCl3", "iron(III) chloride", P3, None, [amount("equivalents", 1.2, "equiv", P3)]),
      solvent("ch2cl2", "CH2Cl2", "dichloromethane", "ClCCl", P3)]
records.append(rec(
    "equation6_stoichiometric_fecl3_control", "reported_experiment", P3, ps,
    [{"step_id": "reaction", "participant_ids": [p["entity_id"] for p in ps],
      "conditions": [fld("solvent", "CH2Cl2", P3), fld("temperature", {"number": 40, "unit": "°C"}, P3), fld("time", {"number": 22, "unit": "h"}, P3)]}],
    [fld("nmr_yield_4a", {"number": 16, "unit": "%"}, P3, ["4a"]),
     fld("yield_measurement_basis_4a", "NMR", P3, ["4a"]),
     fld("nmr_yield_5a", {"number": 19, "unit": "%"}, P3, ["5a"]),
     fld("yield_measurement_basis_5a", "NMR", P3, ["5a"])],
    [], ["Product 5a structure is retained by label because its exact connectivity was not independently verified; exact scale, atmosphere, workup, and purification are absent."]))


# Proposed cycle shown below Equation 6. It is explicitly not a batch record.
records.append(rec(
    "proposed_cocatalytic_mechanism", "mechanism", P3,
    [part("mechanism_1a", "reactant", "1a", "ethyl 4-phenyl-2-ethyl-2,3-butadienoate", P3, SMILES["1a"]),
     part("mechanism_fecl3", "catalyst", "FeCl3", "iron(III) chloride", P3),
     part("mechanism_pdii", "catalyst", "PdII", "palladium(II) species", P3),
     part("mechanism_allyl_bromide", "reactant", "allyl bromide", "allyl bromide", P3, SMILES["2a"]),
     part("mechanism_3a", "product", "3a", "4-allyl-3-ethyl-5-phenyl-2(5H)-furanone", P3, SMILES["3a"]),
     part("intermediate_a", "unspecified_agent", "A", "proposed furanonyl iron intermediate", P3),
     part("intermediate_b", "unspecified_agent", "B", "proposed furanonyl palladium intermediate", P3),
     part("intermediate_c", "unspecified_agent", "C", "proposed carbopalladation intermediate", P3)],
    [{"step_id": "proposed_cycle", "participant_ids": ["mechanism_1a", "mechanism_fecl3", "mechanism_pdii", "mechanism_allyl_bromide", "mechanism_3a", "intermediate_a", "intermediate_b", "intermediate_c"],
      "conditions": missing_conditions(P3)}],
    [fld("reported_yield", None, P3, ["mechanism_3a"])],
    [("The authors propose iron cyclization, transmetalation to Pd, carbopalladation with allyl bromide, and dehalopalladation.", P3)],
    ["Mechanistic intermediates A--C are proposed, not isolated experimental products; no time, temperature, or yield belongs to the cycle."]))


OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"output": str(OUT), "records": len(records)}, ensure_ascii=False))
