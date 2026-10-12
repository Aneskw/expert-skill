#!/usr/bin/env python3
"""Build source-linked machine extraction records for PDF pages 1--3."""
import json
from pathlib import Path

DOC = "doc_d31917b333a62653"
P1 = [f"{DOC}:page1:text", f"{DOC}:page1:image"]
P2 = [f"{DOC}:page2:text", f"{DOC}:page2:image"]
P3 = [f"{DOC}:page3:text", f"{DOC}:page3:image"]


def fact(value, evidence):
    return {
        "value": value,
        "evidence_ids": list(evidence) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def field(name, value, evidence, targets=None):
    result = {"name": name, "fact": fact(value, evidence)}
    if targets:
        result["target_entity_ids"] = targets
    return result


def part(entity_id, role, label, evidence, name=None, smiles=None, amounts=None):
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


def qty(name, number, unit, evidence, raw_text=None):
    value = {"number": number, "unit": unit}
    if raw_text:
        value["raw_text"] = raw_text
    return field(name, value, evidence)


def rec(suffix, source_id, kind, evidence):
    return {
        "record_id": f"{DOC}:{suffix}",
        "document_id": DOC,
        "source_reaction_id": source_id,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": list(evidence),
        "participants": [],
        "steps": [],
        "outcomes": [],
        "notes": [],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": [
                "Supporting Information is mentioned in the article but was not provided or explicitly associated.",
                "Machine-extracted structures and chemical roles require independent source review.",
            ],
        },
    }


SMI_1A = "C=C=C(CCCC)P(=O)(OCC)OCC"
SMI_2A = "OB(O)c1ccccc1"
SMI_HOAC = "CC(=O)O"
SMI_PPH3 = "P(c1ccccc1)(c1ccccc1)c1ccccc1"


def shared_1a_2a(evidence):
    return [
        part("r_1a", "reactant", "1a", evidence,
             "diethyl (hepta-1,2-dien-3-yl)phosphonate", SMI_1A,
             [qty("amount", 0.25, "mmol", evidence)]),
        part("r_2a", "reactant", "2a", evidence, "phenylboronic acid", SMI_2A,
             [qty("amount", 0.50, "mmol", evidence)]),
    ]


def catalyst_part(label, loading, evidence):
    return part("cat", "catalyst", label, evidence, amounts=[qty("loading", loading, "mol%", evidence)])


def hoac_part(loading, evidence):
    return part("hoac", "reagent", "HOAc", evidence, "acetic acid", SMI_HOAC,
                [qty("loading", loading, "mol%", evidence)])


def solvent_part(label, evidence, volume=3):
    names = {"THF": "tetrahydrofuran", "CH3NO2": "nitromethane", "CH3OH": "methanol",
             "CH3CN": "acetonitrile", "CH2Cl2": "dichloromethane", "DMF": "N,N-dimethylformamide",
             "ether": "ether", "dioxane": "dioxane", "toluene": "toluene"}
    smiles = {"THF": "C1CCOC1", "CH3NO2": "C[N+](=O)[O-]", "CH3OH": "CO",
              "CH3CN": "CC#N", "CH2Cl2": "ClCCl", "DMF": "CN(C)C=O", "toluene": "Cc1ccccc1"}
    amounts = [qty("volume", volume, "mL", evidence)] if volume is not None else []
    return part("solvent", "solvent", label, evidence, names.get(label), smiles.get(label), amounts)


def product(entity_id, label, evidence, name=None):
    return part(entity_id, "product", label, evidence, name=name)


def common_step(participant_ids, evidence, time_h, temperature, solvent, atmosphere=True):
    conditions = [field("temperature", temperature, evidence), qty("time", time_h, "h", evidence),
                  field("solvent", solvent, evidence)]
    if atmosphere:
        conditions.append(field("atmosphere", "nitrogen", evidence))
    return {"step_id": "reaction", "participant_ids": participant_ids, "conditions": conditions}


records = []

# Page 1: generic reaction-class scheme, deliberately not an individual experiment.
r = rec("general_scheme_1_2_to_E3", "page1_generic_scheme", "general_scheme", P1)
r["participants"] = [
    part("generic_1", "reactant", "1 (R1/R2-substituted 1,2-allenylphosphonate)", P1),
    part("generic_2", "reactant", "2 (R3-boronic acid)", P1),
    catalyst_part("Pd(PPh3)4", 10, P1),
    hoac_part(100, P1),
    solvent_part("THF", P1, None),
    product("generic_E3", "E-3 (generic 1(E)-alkenylphosphonate)", P1),
]
r["steps"] = [{"step_id": "generic_transformation", "participant_ids": [p["entity_id"] for p in r["participants"]],
               "conditions": [field("temperature", "r.t.", P1), field("solvent", "THF", P1)]}]
r["notes"] = [fact("Generic graphical scope statement; not counted as a reported individual experiment.", P1)]
r["review"]["unresolved"].append("R1, R2, and R3 are generic substituents, so structures are intentionally left null.")
records.append(r)


def make_opt(suffix, source_id, catalyst, cat_loading, solvent, time_h, temperature, hoac_loading,
             yield_value=None, ratio=None, recovered=None, extra_pph3=False, evidence=P2):
    r = rec(suffix, source_id, "optimization_entry", evidence)
    r["participants"] = shared_1a_2a(evidence) + [catalyst_part(catalyst, cat_loading, evidence),
                                                  hoac_part(hoac_loading, evidence),
                                                  solvent_part(solvent, evidence)]
    if extra_pph3:
        r["participants"].append(part("pph3", "reagent", "PPh3", evidence, "triphenylphosphine", SMI_PPH3,
                                      [qty("loading", 20, "mol%", evidence)]))
    product_ids = []
    if yield_value is not None:
        if ratio in ("85:0:15", "98:0:2"):
            r["participants"] += [product("p_E3aa", "E-3aa", evidence), product("p_Z3aa", "Z-3aa", evidence),
                                  product("p_4aa", "4aa", evidence)]
            product_ids = ["p_E3aa", "p_4aa"]
        elif yield_value == "trace" and ratio is None:
            r["participants"].append(product("p_mix", "3aa + 4aa (reported product column)", evidence))
            product_ids = ["p_mix"]
        else:
            r["participants"].append(product("p_E3aa", "E-3aa", evidence,
                                             "diethyl (2-phenylhept-2(E)-en-3-yl)phosphonate"))
            product_ids = ["p_E3aa"]
    r["steps"] = [common_step([p["entity_id"] for p in r["participants"] if p["role"] != "product"],
                              evidence, time_h, temperature, solvent)]
    if yield_value is None:
        r["outcomes"].append(field("reaction_result", "NR (no reaction)", evidence))
    else:
        value = yield_value if isinstance(yield_value, str) else {"number": yield_value, "unit": "%"}
        r["outcomes"].append(field("isolated_yield", value, evidence, product_ids))
        r["outcomes"].append(field("yield_measurement_basis", "isolated yield of 3aa + 4aa", evidence, product_ids))
    if ratio == "85:0:15":
        r["outcomes"].append(field("E_3aa_Z_3aa_4aa_ratio", ratio, evidence,
                                   ["p_E3aa", "p_Z3aa", "p_4aa"]))
    elif ratio == "98:0:2":
        r["outcomes"].append(field("E_3aa_Z_3aa_4aa_ratio", ratio, evidence,
                                   ["p_E3aa", "p_Z3aa", "p_4aa"]))
    elif ratio == ">=97% E-3aa":
        r["outcomes"].append(field("selectivity_for_E_3aa",
                                   {"number": 97, "unit": "%", "qualifier": "ge", "raw_text": ">=97% of E-3aa"},
                                   evidence, ["p_E3aa"]))
        r["notes"].append(fact("Z-3aa and 4aa were not observed in the crude 300 MHz 1H NMR; >=97% E-3aa was assumed from instrument accuracy.", evidence))
    if recovered is not None:
        r["outcomes"].append(field("recovered_1a_percentage", {"number": recovered, "unit": "%"}, evidence,
                                   ["r_1a"]))
    return r


# Table 1, entries 1--8. Entry 9 is merged into the detailed standard record below.
table1 = [
    (1, "CH3NO2", 41, "trace", None, None),
    (2, "dioxane", 72, None, None, 53),
    (3, "ether", 72, None, None, 71),
    (4, "CH3CN", 72, None, None, 38),
    (5, "toluene", 72, None, None, 48),
    (6, "CH3OH", 41, 75, "85:0:15", None),
    (7, "DMF", 72, 12, ">=97% E-3aa", None),
    (8, "CH2Cl2", 24, 23, ">=97% E-3aa", None),
]
for e, solv, t, y, ratio, recovered in table1:
    records.append(make_opt(f"table1_entry{e}", f"Table 1 entry {e}", "Pd(PPh3)4", 10, solv, t, "r.t.", 100,
                            y, ratio, recovered))

# Table 2: catalyst screen. Footnote c adds 20 mol% PPh3 to entries 3--6.
table2 = [
    (1, "Pd(OAc)2", 45, "trace", None, None, False),
    (2, "PdCl2", 72, None, None, 53, False),
    (3, "PdCl2", 72, None, None, 36, True),
    (4, "Pd(PhCN)2Cl2", 72, None, None, 21, True),
    (5, "Pd(dba)2", 45, 70, ">=97% E-3aa", None, True),
    (6, "Pd(OAc)2", 45, 57, ">=97% E-3aa", None, True),
]
for e, cat, t, y, ratio, recovered, pph3 in table2:
    records.append(make_opt(f"table2_entry{e}", f"Table 2 entry {e}", cat, 10, "THF", t, "r.t.", 100,
                            y, ratio, recovered, pph3))

# Table 3, excluding entry 4, which is the same standard experiment detailed on page 3.
table3 = [
    (1, 1, "r.t.", 91, None, None, 69),
    (2, 3, "r.t.", 91, 71, "98:0:2", None),
    (3, 5, "r.t.", 91, 75, "98:0:2", None),
    (5, 5, {"number": 50, "unit": "°C"}, 33, 66, ">=97% E-3aa", None),
    (6, 5, "reflux", 33, 66, ">=97% E-3aa", None),
    (7, 10, {"number": 50, "unit": "°C"}, 9, 65, ">=97% E-3aa", None),
    (8, 10, "reflux", 9, 63, ">=97% E-3aa", None),
]
for e, loading, temp, t, y, ratio, recovered in table3:
    records.append(make_opt(f"table3_entry{e}", f"Table 3 entry {e}", "Pd(PPh3)4", loading, "THF", t, temp, 100,
                            y, ratio, recovered))

# Table 4, excluding entry 3, which duplicates the standard experiment.
table4 = [(1, 20, 48, 56), (2, 50, 35, 66), (4, 200, 23, 75)]
for e, hoac, t, y in table4:
    records.append(make_opt(f"table4_entry{e}", f"Table 4 entry {e}", "Pd(PPh3)4", 10, "THF", t, "r.t.", hoac,
                            y, ">=97% E-3aa"))

# The standard experiment appears as Table 1 entry 9, Table 3 entry 4, Table 4 entry 3, and Typical Procedure II.
ev_standard = P1 + P2 + P3
r = rec("standard_1a_2a_E3aa", "Table 1 entry 9 = Table 3 entry 4 = Table 4 entry 3 = Typical Procedure II",
        "reported_experiment", ev_standard)
r["participants"] = [
    part("r_1a", "reactant", "1a", ev_standard, "diethyl (hepta-1,2-dien-3-yl)phosphonate", SMI_1A,
         [qty("mass", 58, "mg", P3), qty("amount", 0.25, "mmol", ev_standard)]),
    part("r_2a", "reactant", "2a", ev_standard, "phenylboronic acid", SMI_2A,
         [qty("mass", 61, "mg", P3), qty("amount", 0.50, "mmol", ev_standard)]),
    part("cat", "catalyst", "Pd(PPh3)4", ev_standard, amounts=[qty("mass", 29, "mg", P3),
                                                               qty("amount", 0.025, "mmol", P3),
                                                               qty("loading", 10, "mol%", P2)]),
    part("hoac", "reagent", "HOAc / AcOH", ev_standard, "acetic acid", SMI_HOAC,
         [qty("volume", 14, "uL", P3), qty("reported_amount", 0.25, "mol", P3),
          qty("loading", 100, "mol%", P2)]),
    solvent_part("THF", ev_standard),
    product("p_E3aa", "E-3aa", ev_standard, "diethyl (2-phenylhept-2(E)-en-3-yl)phosphonate"),
]
r["participants"][-1]["amounts"] = [qty("mass", 63, "mg", P3)]
r["steps"] = [{
    "step_id": "reaction_and_isolation",
    "participant_ids": [p["entity_id"] for p in r["participants"]],
    "conditions": [field("atmosphere", "nitrogen", ev_standard), field("temperature", "r.t.", ev_standard),
                   qty("time", 24, "h", P2), field("solvent", "THF", ev_standard),
                   qty("solvent_volume", 3, "mL", ev_standard),
                   field("operation", "stirred and monitored by TLC (ether); solvent evaporated", P3),
                   field("purification", "flash chromatography on silica gel; petroleum ether/ether = 1:1", P3)],
}]
r["outcomes"] = [
    field("isolated_yield", {"number": 81, "unit": "%"}, ev_standard, ["p_E3aa"]),
    field("yield_measurement_basis", "isolated yield", ev_standard, ["p_E3aa"]),
    field("selectivity_for_E_3aa", {"number": 97, "unit": "%", "qualifier": "ge", "raw_text": ">=97% of E-3aa"},
          P2, ["p_E3aa"]),
    field("alkene_configuration_assignment", "E", P1, ["p_E3aa"]),
    field("configuration_measurement_basis", "1H-1H NOESY", P1, ["p_E3aa"]),
]
r["notes"] = [
    fact("The printed procedure reports AcOH as 14 uL, 0.25 mol; this is internally inconsistent with the table's 100 mol% and is retained without correction.", ev_standard),
    fact("Z-3aa and 4aa were not observed in crude 300 MHz 1H NMR; >=97% E-3aa was assumed from instrument accuracy.", P2),
]
r["review"]["unresolved"].append("Printed AcOH amount '0.25 mol' conflicts with 14 uL and 100 mol%; no silent correction to mmol was made.")
records.append(r)

# Page 3, Typical Procedure I: preparation of allene 1a.
r = rec("procedure_I_synthesis_1a", "Typical Procedure I: synthesis of 1a", "reported_experiment", P3)
r["participants"] = [
    part("heptynol", "reactant", "hept-2-yn-1-ol", P3, "hept-2-yn-1-ol", "CCCCC#CCO",
         [qty("mass", 1.152, "g", P3), qty("amount", 10, "mmol", P3)]),
    part("et3n", "reagent", "Et3N", P3, "triethylamine", "CCN(CC)CC",
         [qty("volume", 1.5, "mL", P3), qty("amount", 11, "mmol", P3)]),
    part("p_reagent", "reagent", "P(OEt)2Cl", P3, amounts=[qty("mass", 2.093, "g", P3),
                                                            qty("amount", 13, "mmol", P3)]),
    part("thf", "solvent", "THF", P3, "tetrahydrofuran", "C1CCOC1",
         [qty("initial_volume", 25, "mL", P3), qty("addition_solution_volume", 5, "mL", P3)]),
    product("p_1a", "1a", P3, "diethyl (hepta-1,2-dien-3-yl)phosphonate"),
]
r["participants"][-1]["smiles"] = fact(SMI_1A, P3)
r["participants"][-1]["amounts"] = [qty("mass", 1.582, "g", P3)]
r["steps"] = [
    {"step_id": "addition", "participant_ids": ["heptynol", "et3n", "p_reagent", "thf"],
     "conditions": [field("operation", "P(OEt)2Cl solution in THF added dropwise", P3),
                    field("temperature", {"number": -78, "unit": "°C"}, P3)]},
    {"step_id": "reflux_and_isolation", "participant_ids": ["heptynol", "et3n", "p_reagent", "thf", "p_1a"],
     "conditions": [field("temperature", "reflux", P3),
                    field("operation", "heated until complete conversion by TLC; filtered; solvent evaporated", P3),
                    field("purification", "flash chromatography on silica gel; petroleum ether/ether = 1:1", P3)]},
]
r["outcomes"] = [field("isolated_yield", {"number": 68, "unit": "%"}, P3, ["p_1a"]),
                 field("yield_measurement_basis", "isolated yield", P3, ["p_1a"])]
r["notes"] = [fact("Product reported as a liquid.", P3)]
r["review"]["unresolved"].append("Reaction duration and atmosphere are not reported in the supplied main text.")
records.append(r)

# Table 5 substrate scope.
scope_rows = [
    (1, "1a", "H / n-Bu", SMI_1A, "2b", "p-MeC6H4", "Cc1ccc(B(O)O)cc1", 52, 90, "E-3ab"),
    (2, "1b", "H / H", "C=C=CP(=O)(OCC)OCC", "2b", "p-MeC6H4", "Cc1ccc(B(O)O)cc1", 47, 87, "E-3bb"),
    (3, "1c", "H / Me", "C=C=C(C)P(=O)(OCC)OCC", "2b", "p-MeC6H4", "Cc1ccc(B(O)O)cc1", 77, 85, "E-3cb"),
    (4, "1d", "H / n-C7H15", "C=C=C(CCCCCCC)P(=O)(OCC)OCC", "2b", "p-MeC6H4", "Cc1ccc(B(O)O)cc1", 76, 91, "E-3db"),
    (5, "1e", "H / Ph", "C=C=C(c1ccccc1)P(=O)(OCC)OCC", "2b", "p-MeC6H4", "Cc1ccc(B(O)O)cc1", 135, 47, "E-3eb"),
    (6, "1f", "n-Bu / H", "CCCCC=C=CP(=O)(OCC)OCC", "2b", "p-MeC6H4", "Cc1ccc(B(O)O)cc1", 34, 52, "E-3fb"),
    (7, "1a", "H / n-Bu", SMI_1A, "2c", "m-MeOC6H4", "COc1cccc(B(O)O)c1", 70, 91, "E-3ac"),
    (8, "1a", "H / n-Bu", SMI_1A, "2d", "p-MeOC6H4", "COc1ccc(B(O)O)cc1", 65, 88, "E-3ad"),
    (9, "1a", "H / n-Bu", SMI_1A, "2e", "p-MeCOC6H4", "CC(=O)c1ccc(B(O)O)cc1", 65, 85, "E-3ae"),
    (10, "1a", "H / n-Bu", SMI_1A, "2f", "m-NO2C6H4", "[O-][N+](=O)c1cccc(B(O)O)c1", 32, 81, "E-3af"),
    (11, "1a", "H / n-Bu", SMI_1A, "2g", "1-(E)-heptenyl", "CCCCC/C=C/B(O)O", 96, 89, "E,E-3ag"),
    (12, "1a", "H / n-Bu", SMI_1A, "2h", "depicted PhOCH2-substituted alkenyl group", None, 78, 71, "E,E-3ah"),
]
for e, allene_label, r1r2, allene_smiles, boron_label, r3, boron_smiles, t, y, prod_label in scope_rows:
    r = rec(f"table5_entry{e}", f"Table 5 entry {e}", "substrate_scope_entry", P3)
    r["participants"] = [
        part("allene", "reactant", f"{allene_label} (R1/R2 = {r1r2})", P3, smiles=allene_smiles),
        part("boronic_acid", "reactant", f"{boron_label} (R3 = {r3})", P3, smiles=boron_smiles),
        catalyst_part("Pd(PPh3)4", 10, P3),
        hoac_part(100, P3),
        solvent_part("THF", P3, None),
        product("product", prod_label, P3),
    ]
    if e == 6:
        r["participants"].append(product("unknown_byproduct", "unidentified product", P3))
    r["steps"] = [{"step_id": "conditions_A", "participant_ids": [p["entity_id"] for p in r["participants"]],
                   "conditions": [field("temperature", "r.t.", P3), qty("time", t, "h", P3),
                                  field("solvent", "THF", P3)]}]
    r["outcomes"] = [field("isolated_yield", {"number": y, "unit": "%"}, P3, ["product"]),
                     field("yield_measurement_basis", "isolated yield", P3, ["product"]),
                     field("Z_3_formation", "not observed", P3, ["product"]),
                     field("selectivity_measurement_basis", "300 MHz 1H NMR analysis of crude reaction products", P3,
                           ["product"])]
    if e == 6:
        r["outcomes"].append(field("unidentified_product_formation", "observed", P3, ["unknown_byproduct"]))
        r["review"]["unresolved"].append("Table 5 footnote reports another unidentified product without identity or amount.")
    r["review"]["unresolved"].append("Table 5 does not report substrate amounts, solvent volume, atmosphere, or workup for this row.")
    if e == 12:
        r["review"]["unresolved"].append("The exact connectivity/stereochemical encoding of the drawn 2h substituent was not converted to SMILES.")
    records.append(r)

# Page 3 proposed mechanism; kept separate from experimental records.
r = rec("proposed_mechanism", "page3_proposed_mechanism", "mechanism", P3)
r["participants"] = [
    part("pd0", "catalyst", "Pd(0)", P3), part("hoac", "reagent", "HOAc", P3, "acetic acid", SMI_HOAC),
    part("allene_1", "reactant", "1 (1,2-allenylphosphonate)", P3),
    part("boronic_2", "reactant", "2 (organoboronic acid)", P3), product("E3", "E-3", P3),
]
r["steps"] = [
    {"step_id": "oxidative_addition", "participant_ids": ["pd0", "hoac"],
     "conditions": [field("operation", "proposed oxidative addition of HOAc to Pd(0)", P3)]},
    {"step_id": "hydrometalation", "participant_ids": ["allene_1", "pd0"],
     "conditions": [field("operation", "proposed regioselective hydrometalation of the terminal C=C bond to form an sp2-C-Pd species", P3)]},
    {"step_id": "coupling", "participant_ids": ["boronic_2", "E3"],
     "conditions": [field("operation", "proposed Suzuki-type coupling affording E-3", P3)]},
]
r["notes"] = [fact("Authors describe this as a proposed mechanism based on a previous ESI-MS study (reference 12), not as a separately reported experiment in this paper.", P3)]
r["review"]["unresolved"].append("Intermediates are not fully specified in the supplied main text and no mechanistic experiment is reported here.")
records.append(r)

out = Path(__file__).with_name("pages_0001_0003_records.json")
out.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"output": str(out), "records": len(records)}, ensure_ascii=False))
